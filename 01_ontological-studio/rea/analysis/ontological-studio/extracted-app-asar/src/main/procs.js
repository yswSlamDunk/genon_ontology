'use strict'
// Child-process housekeeping: spawn with logs, readiness probes, ordered stop,
// and reaping of orphans a crashed previous run left behind.
const { spawn, execFileSync } = require('child_process')
const fs = require('fs')
const net = require('net')
const http = require('http')
const path = require('path')

const children = new Map() // name -> { proc, stopSignal }
let runDir = null
let logDir = null

function init(dirs) {
  runDir = dirs.runDir
  logDir = dirs.logDir
  fs.mkdirSync(runDir, { recursive: true })
  fs.mkdirSync(logDir, { recursive: true })
}

function alive(pid) {
  try { process.kill(pid, 0); return true } catch { return false }
}

function commandOf(pid) {
  try {
    if (process.platform === 'win32') {
      return execFileSync('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command',
        `(Get-CimInstance Win32_Process -Filter "ProcessId=${Number(pid)}").CommandLine`], { encoding: 'utf8', windowsHide: true }).trim()
    }
    return execFileSync('ps', ['-p', String(pid), '-o', 'command='], { encoding: 'utf8' }).trim()
  } catch { return '' }
}

/** Kill processes recorded by a previous run whose command still points into our runtime. */
async function reapOrphans(runtimeRoot, log) {
  for (const f of fs.existsSync(runDir) ? fs.readdirSync(runDir) : []) {
    if (!f.endsWith('.pid')) continue
    const pid = Number(fs.readFileSync(path.join(runDir, f), 'utf8'))
    if (pid && alive(pid)) {
      const cmd = commandOf(pid)
      if (cmd.includes(runtimeRoot) || cmd.includes('ontology-lite')) {
        log(`orphan ${f} (pid ${pid}) — stopping`)
        try { process.kill(pid, f === 'postgres.pid' ? 'SIGINT' : 'SIGTERM') } catch {}
        for (let i = 0; i < 50 && alive(pid); i++) await sleep(200)
        if (alive(pid)) try { process.kill(pid, 'SIGKILL') } catch {}
      }
    }
    fs.rmSync(path.join(runDir, f), { force: true })
  }
}

function start(name, command, args, { env, cwd, stopSignal = 'SIGTERM', onExit } = {}) {
  const out = fs.openSync(path.join(logDir, `${name}.log`), 'a')
  fs.writeSync(out, `\n--- ${new Date().toISOString()} start ${command} ${args.join(' ')}\n`)
  const proc = spawn(command, args, { env, cwd, stdio: ['ignore', out, out], detached: false })
  fs.closeSync(out)
  fs.writeFileSync(path.join(runDir, `${name}.pid`), String(proc.pid))
  children.set(name, { proc, stopSignal })
  proc.on('exit', (code, sig) => {
    children.delete(name)
    fs.rmSync(path.join(runDir, `${name}.pid`), { force: true })
    if (onExit) onExit(code, sig)
  })
  return proc
}

async function stop(name, timeoutMs = 15000) {
  const c = children.get(name)
  if (!c) return
  const { proc, stopSignal } = c
  const done = new Promise((r) => proc.once('exit', r))
  try { proc.kill(stopSignal) } catch {}
  const t = await Promise.race([done.then(() => 'ok'), sleep(timeoutMs).then(() => 'timeout')])
  if (t === 'timeout') { try { proc.kill('SIGKILL') } catch {}; await done }
}

const running = () => [...children.entries()].map(([n, c]) => ({ name: n, pid: c.proc.pid }))
const isRunning = (name) => children.has(name)
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

function probeTcp(port, host = '127.0.0.1') {
  return new Promise((resolve) => {
    const s = net.connect({ port, host })
    s.once('connect', () => { s.destroy(); resolve(true) })
    s.once('error', () => resolve(false))
    s.setTimeout(1000, () => { s.destroy(); resolve(false) })
  })
}

function probeHttp(url) {
  return new Promise((resolve) => {
    const req = http.get(url, (res) => { res.resume(); resolve(res.statusCode < 500) })
    req.on('error', () => resolve(false))
    req.setTimeout(2000, () => { req.destroy(); resolve(false) })
  })
}

async function waitFor(what, probe, { timeoutMs = 120000, intervalMs = 150, name } = {}) {
  const t0 = Date.now()
  while (Date.now() - t0 < timeoutMs) {
    if (name && !isRunning(name)) throw new Error(`${what}: 프로세스가 종료됐습니다 (로그: logs/${name}.log)`)
    if (await probe()) return Date.now() - t0
    await sleep(intervalMs)
  }
  throw new Error(`${what}: ${timeoutMs / 1000}초 안에 준비되지 않았습니다`)
}

module.exports = { init, start, stop, running, isRunning, reapOrphans, probeTcp, probeHttp, waitFor, sleep }
