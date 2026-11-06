'use strict'
// Ontological Studio — Electron main.
// Boot order: PostgreSQL → (first run: bootstrap) → Bolt gateway → portal →
// (first run: fabric seed over Bolt) → Studio backend + MCP → local origin → UI.
const { app, BrowserWindow, Menu, shell, ipcMain } = require('electron')
const fs = require('fs')
const path = require('path')
const neo4j = require('neo4j-driver')
const procs = require('./procs')
const ports_ = require('./ports')
const pg = require('./postgres')
const services = require('./services')
const web = require('./web')
const { createBridge } = require('./fabric-bridge')
const tabs = require('./tabs')
const tray = require('./tray')
const kinetic = require('./kinetic')
const nl2cypher = require('./nl2cypher')
const { createCodeApps } = require('./codeapps')

const T0 = Date.now()
const timings = {}
const mark = (k) => { timings[k] = Date.now() - T0 }


// ── where things live ──
const ROOT = app.isPackaged ? process.resourcesPath : path.resolve(__dirname, '..', '..')
const rt = {
  root: path.join(ROOT, 'runtime'),
  pg: path.join(ROOT, 'runtime', 'pg'),
  bin: path.join(ROOT, 'runtime', 'bin'),
  portal: path.join(ROOT, 'runtime', 'portal'),
  studioPython: path.join(ROOT, 'runtime', 'studio', 'python'),
  studioApp: path.join(ROOT, 'runtime', 'studio', 'app'),
  frontend: path.join(ROOT, 'runtime', 'frontend'),
  resources: app.isPackaged ? path.join(process.resourcesPath, 'resources') : path.join(ROOT, 'resources'),
}
// The app was called "Ontology Studio Lite"; its data folder follows the name once. Not while
// that app still runs from it (its PostgreSQL holds the folder) — then this run uses it in place.
let migrated = ''
function migrateUserData() {
  const now = app.getPath('userData')
  const old = path.join(app.getPath('appData'), 'Ontology Studio Lite')
  // "has data" = a database. The new folder may already exist with only Electron's own files
  // (any earlier start under the new name creates it) — those give way to the old folder's.
  const hasData = (d) => fs.existsSync(path.join(d, 'pgdata'))
  if (hasData(now) || !hasData(old)) return
  const alive = (f) => { try { return process.kill(Number(fs.readFileSync(f, 'utf8').split('\n')[0]), 0) } catch { return false } }
  if (alive(path.join(old, 'pgdata', 'postmaster.pid')) || alive(path.join(old, 'run', 'postgres.pid'))) {
    app.setPath('userData', old); migrated = `이전 이름의 데이터 폴더를 그대로 씁니다(그 앱이 실행 중): ${old}`
    return
  }
  try {
    if (!fs.existsSync(now)) fs.renameSync(old, now)
    else {
      for (const name of fs.readdirSync(old)) {
        fs.rmSync(path.join(now, name), { recursive: true, force: true })
        fs.renameSync(path.join(old, name), path.join(now, name))
      }
      fs.rmdirSync(old)
    }
    migrated = `데이터 폴더를 새 이름으로 옮겼습니다: ${old} → ${now}`
  } catch (e) {
    app.setPath('userData', old); migrated = `데이터 폴더를 옮기지 못해 이전 위치를 씁니다: ${e.message}`
  }
}
const customUserData = process.env.ONTOLOGICAL_STUDIO_USER_DATA || process.env.ONTOLOGY_LITE_USER_DATA
if (customUserData) app.setPath('userData', customUserData)
else migrateUserData()
// One instance per data folder (the lock follows userData): a second data folder — a demo,
// a test run — can run next to the everyday one; it allocates its own free ports.
if (!app.requestSingleInstanceLock()) { app.quit(); process.exit(0) }
const userData = app.getPath('userData')
const dirs = {
  userData,
  dataDir: path.join(userData, 'pgdata'),
  logDir: path.join(userData, 'logs'),
  runDir: path.join(userData, 'run'),
  sandbox: path.join(userData, 'sandbox'),
  userEnv: path.join(userData, 'studio.env'),
}

let win = null
let ports = null
let driver = null
let server = null
let sec = null
let agent = null // who runs Studio's agent turns — services.resolveAgent
let kineticEnv = null // Studio's KINETIC_* for the bundled kinetic-action (null: studio.env names another)
let kineticUp = false
let codeapps = null // code apps (codeapps.js) — their agent runs are stopped at quit
let phase = 'starting'
let lastError = null

procs.init(dirs)
const logFile = path.join(dirs.logDir, 'desktop.log')
function log(msg) {
  const line = `${new Date().toISOString()} ${msg}\n`
  fs.appendFileSync(logFile, line)
  if (!app.isPackaged) process.stdout.write(line)
}

function progress(step, detail) {
  phase = step
  tray.update()
  log(`[${step}] ${detail || ''}`)
  if (win && !win.isDestroyed() && win.webContents.getURL().startsWith('file:')) {
    win.webContents.executeJavaScript(`window.setStep && setStep(${JSON.stringify(step)}, ${JSON.stringify(detail || '')})`).catch(() => {})
  }
}

function ensureUserEnv() {
  if (fs.existsSync(dirs.userEnv)) return
  fs.copyFileSync(path.join(rt.resources, 'studio.env.example'), dirs.userEnv)
  fs.chmodSync(dirs.userEnv, 0o600)
}

async function boot() {
  fs.mkdirSync(userData, { recursive: true })
  if (migrated) log(migrated)
  ensureUserEnv()
  await procs.reapOrphans(rt.root, log)
  const portsFile = path.join(userData, 'ports.json')
  const saved = fs.existsSync(portsFile) ? JSON.parse(fs.readFileSync(portsFile, 'utf8')) : {}
  ports = await ports_.allocate(saved)
  fs.writeFileSync(portsFile, JSON.stringify(ports, null, 2))
  log(`ports ${JSON.stringify(ports)}`)
  sec = pg.secrets(userData)
  if (kinetic.ensureSecrets(sec)) pg.saveSecrets(userData, sec)

  progress('postgres', 'PostgreSQL 시작')
  const fresh = await pg.initdb(rt, dirs.dataDir, sec.pgPassword, log)
  pg.start(rt, dirs.dataDir, ports.pg)
  await pg.waitReady(rt, ports.pg); mark('postgres')
  if (fresh || !fs.existsSync(path.join(dirs.dataDir, '.ontology-lite-bootstrap'))) {
    progress('bootstrap', '첫 실행 — Ontological 확장과 예제 DB 준비')
    await pg.bootstrap(rt, dirs.dataDir, ports.pg, sec, log); mark('bootstrap')
  }
  const servicesMigrated = await pg.migrateServices(rt, dirs.dataDir, ports.pg, sec, log)

  progress('ontological', 'Ontological Bolt 게이트웨이 · 포털 시작')
  await Promise.all([services.startBolt(rt, ports), services.startPortal(rt, ports, sec)]); mark('ontological')
  driver = neo4j.driver(`bolt://127.0.0.1:${ports.bolt}`, neo4j.auth.basic(pg.SUPERUSER, sec.pgPassword), { maxConnectionPoolSize: 4, disableLosslessIntegers: false })
  await services.repointFabric(ports, sec, driver, log, dirs)
  // the services added columns (wms.shipment.priority) the existing foreign tables do not have
  if (servicesMigrated) await services.resetSampleFabric(driver, log, dirs, '예제 업무 DB 가 바뀌어(마이크로서비스 테이블) 예제 데이터소스를 다시 등록합니다')
  if (await services.seedFabric(rt, dirs, ports, sec, driver, log)) mark('fabricSeed')

  progress('studio', 'Studio · 키네틱 액션 · 예제 시스템 시작')
  const bridge = createBridge(() => driver, pg.GRAPH, { sampleGraph: services.SAMPLE_GRAPH, engines: fabricEngines() })
  const externalKinetic = !!services.readUserEnv(dirs.userEnv).KINETIC_URL
  // code apps: the ontology app written as code by the CLI agent (src/main/codeapps.js)
  codeapps = createCodeApps({
    dir: path.join(userData, 'codeapps'), driver: () => driver, graph: pg.GRAPH, webPort: ports.web, backendPort: ports.backend, log,
    runtimeDir: path.join(rt.resources, 'codeapp', 'runtime'), templateDir: path.join(rt.resources, 'codeapp', 'template'),
    rulesFile: path.join(rt.resources, 'codeapp', 'AGENTS.md'),
    spawnTurn: () => services.spawnStudioScript(rt, dirs, ports, sec, kineticEnv, path.join(rt.resources, 'code_app_turn.py')),
  })
  server = await web.start({ port: ports.web, frontend: rt.frontend, ports, graph: pg.GRAPH, bridge, codeapps,
    kineticOn: () => externalKinetic || kineticUp, jwks: () => kinetic.jwks(sec),
    status: () => ({ phase, timings, ports, userData, error: lastError, pids: procs.running() }) })
  // kinetic-action and Studio start side by side: Studio only needs kinetic-action's address
  // and tokens to start, not kinetic-action itself.
  kineticEnv = externalKinetic ? null : kinetic.studioEnv(ports, sec)
  const kineticStart = externalKinetic ? Promise.resolve(false) : kinetic.start(rt, dirs, ports, sec, { superuser: pg.SUPERUSER, graph: pg.GRAPH })
    .then(async () => {
      await kinetic.repointSystems(ports, sec, log)
      await kinetic.registerSystems(ports, sec, log)
      kineticUp = true; mark('kinetic')
      return true
    })
    .catch((e) => { log(`kinetic-action 을 시작하지 못했습니다 — 액션 없이 계속합니다: ${e.message}`); return false })
  agent = await services.startStudio(rt, dirs, ports, sec, kineticEnv); mark('studio')
  logAgent()
  if (await kineticStart) await seedSampleOntology()

  phase = 'ready'
  progress('ready', '준비 완료')
  tabs.ready({ ports, graph: pg.GRAPH })
  await new Promise((resolve) => win.webContents.once('did-finish-load', resolve))
  mark('uiLoaded')
  fs.writeFileSync(path.join(dirs.logDir, 'boot-timings.json'), JSON.stringify({ at: new Date().toISOString(), fresh, timings }, null, 2))
  log(`timings ${JSON.stringify(timings)}`)
}

/**
 * First run: the sample ontology 「공급망 운영 (예제)」 with its actions and golden commands,
 * made by Studio's own code (resources/sample/seed_ontology.py) once kinetic-action and the
 * sample systems are up. A failure is logged and retried at the next start; the app still opens.
 */
async function seedSampleOntology() {
  const marker = path.join(dirs.dataDir, '.ontology-lite-sample-ontology')
  if (fs.existsSync(marker)) return
  progress('studio', '예제 온톨로지 · 액션 준비 (첫 실행)')
  try {
    const out = await services.runStudioScript(rt, dirs, ports, sec, kineticEnv, path.join(rt.resources, 'sample', 'seed_ontology.py'), log)
    log(`예제 온톨로지: ${out.trim().split('\n').pop()}`)
    fs.writeFileSync(marker, new Date().toISOString())
    mark('sampleOntology')
  } catch (e) {
    log(`예제 온톨로지를 만들지 못했습니다(다음 시작에 다시 시도): ${e.message}`)
  }
}

/** Data fabric engines this installation can connect to: those whose FDW extension is installed. */
function fabricEngines() {
  const dirs_ = [path.join(rt.pg, 'share', 'postgresql', 'extension'), path.join(rt.pg, 'share', 'extension')]
  const has = (ext) => dirs_.some((d) => fs.existsSync(path.join(d, `${ext}.control`)))
  return Object.entries({ postgres: 'postgres_fdw', mysql: 'mysql_fdw', oracle: 'oracle_fdw', sqlserver: 'tds_fdw' })
    .filter(([, ext]) => has(ext)).map(([e]) => e)
}

function createWindow() {
  win = new tabs.TabWindow().win
}

function logAgent() {
  log(`에이전트: ${agent.label} (AGENT_BACKEND=${agent.backend}${agent.backend === 'cliagents' ? `, ${agent.agentId}` : ''})${agent.note ? ' — ' + agent.note : ''}`)
}

/**
 * Menu choice: write it to studio.env and restart only Studio's two processes — the agent
 * backend is read once at start-up (the backend keeps one agent per mode). Open Studio tabs
 * are reloaded so they reconnect; PostgreSQL, Bolt and the portal keep running.
 */
let switching = false
async function switchAgent(choice) {
  if (switching || phase !== 'ready') return
  switching = true
  try {
    services.updateUserEnv(dirs.userEnv, choice === 'deepagents'
      ? { AGENT_BACKEND: 'deepagents' }
      : { AGENT_BACKEND: 'cliagents', EXTERNAL_AGENT_ID: choice })
    progress('studio', '에이전트를 바꾸어 Studio 를 다시 시작합니다')
    await Promise.all([procs.stop('backend', 8000), procs.stop('mcp', 8000)])
    agent = await services.startStudio(rt, dirs, ports, sec, kineticEnv)
    logAgent()
    phase = 'ready'
    progress('ready', '준비 완료')
    for (const w of tabs.windows()) {
      for (const t of w.tabs) if (t.target.kind === 'studio') t.view.webContents.reload()
      w.win.webContents.executeJavaScript('typeof load === "function" && load()').catch(() => {})
    }
  } catch (e) {
    lastError = String(e && e.message || e)
    log(`agent switch failed: ${lastError}`)
  } finally {
    switching = false
    buildMenu()
  }
}

function agentMenu() {
  const found = services.detectAgentClis()
  const want = services.readUserEnv(dirs.userEnv)
  const backend = (want.AGENT_BACKEND || 'cliagents').toLowerCase()
  const id = want.EXTERNAL_AGENT_ID === 'codex' ? 'codex' : 'claude-code'
  const item = (key, label, enabled) => ({
    label, type: 'radio', enabled: enabled && !switching,
    checked: key === 'deepagents' ? backend !== 'cliagents' : backend === 'cliagents' && id === key,
    click: () => switchAgent(key),
  })
  return [
    item('claude-code', `Claude Code${found['claude-code'] ? '' : ' (설치 안 됨)'}`, !!found['claude-code']),
    item('codex', `Codex${found.codex ? '' : ' (설치 안 됨)'}`, !!found.codex),
    item('deepagents', '내장 에이전트 (OpenAI 호환 키)', true),
  ]
}

// Shell actions (title bar buttons, home cards, tray menu). Fixed targets only.
function shellOpen(what) {
  if (what === 'settings') return shell.openPath(dirs.userEnv).then(() => true)
  if (what === 'logs') return shell.openPath(dirs.logDir).then(() => true)
  if (what === 'data') return shell.openPath(userData).then(() => true)
  if (what === 'portal' && ports) return shell.openExternal(`http://127.0.0.1:${ports.portal}/`).then(() => true)
  return Promise.resolve(false)
}

/** The window the user is in (or the first one), brought forward. */
function frontWindow() {
  const w = tabs.focused() || new tabs.TabWindow()
  if (w.win.isMinimized()) w.win.restore()
  w.win.show(); w.win.focus()
  return w
}

// Ontological portal: natural language → Cypher, through the CLI agent (src/main/nl2cypher.js)
ipcMain.handle('lite:nl2cypher', async (_e, req) => {
  if (phase !== 'ready') throw new Error('아직 시작하는 중입니다.')
  const t0 = Date.now()
  try {
    const out = await nl2cypher.translate(req, {
      ports, driver: () => driver, agent: () => agent,
      runAgent: (system, user) => services.runStudioScript(rt, dirs, ports, sec, kineticEnv, path.join(rt.resources, 'agent_turn.py'), log, JSON.stringify({ system, user })),
    })
    log(`nl2cypher ${req.graph}: ${Date.now() - t0} ms${out.repaired ? ' (고침 1회)' : ''}${out.error ? ' — 실패: ' + out.error.slice(0, 120) : ''}`)
    return out
  } catch (e) {
    log(`nl2cypher 실패: ${e.message}`)
    throw new Error(e.message)
  }
})

tabs.wireIpc({
  open: shellOpen,
  info() {
    const env = services.readUserEnv(dirs.userEnv)
    const a = agent || services.resolveAgent(env)
    return {
      graph: pg.GRAPH, ports, phase,
      agent: { backend: a.backend, agentId: a.agentId, label: a.label, ready: a.ready, note: a.note },
      llmConfigured: a.ready,
      kineticConfigured: kineticUp || !!env.KINETIC_URL,
      version: app.getVersion(),
    }
  },
})

function buildMenu() {
  const tpl = [
    { role: 'appMenu' },
    { role: 'editMenu' },
    { label: '탭', submenu: tabs.menuItems() },
    { label: '보기', submenu: [{ role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }, { type: 'separator' }, { role: 'togglefullscreen' }] },
    { label: '런타임', submenu: [
      { label: 'Ontological 포털 탭 열기', click: () => { const w = BrowserWindow.getFocusedWindow(); const tw = tabs.windows().find((x) => x.win === w) || tabs.windows()[0]; if (ports && tw) tw.open({ kind: 'portal' }) } },
      { label: 'Ontological 포털을 브라우저에서 열기', click: () => ports && shell.openExternal(`http://127.0.0.1:${ports.portal}/`) },
      { type: 'separator' },
      { label: '에이전트', submenu: agentMenu() },
      { type: 'separator' },
      { label: '설정 파일 열기 (studio.env)', click: () => shell.openPath(dirs.userEnv) },
      { label: '로그 폴더 열기', click: () => shell.openPath(dirs.logDir) },
      { label: '데이터 폴더 열기', click: () => shell.openPath(userData) },
    ] },
    { role: 'windowMenu' },
  ]
  Menu.setApplicationMenu(Menu.buildFromTemplate(tpl))
}

let stopping = null
async function shutdown() {
  if (stopping) return stopping
  stopping = (async () => {
    log('shutdown')
    tray.destroy()
    try { if (codeapps) codeapps.stopAll() } catch {}
    try { if (server) server.close() } catch {}
    try { if (driver) await driver.close() } catch {}
    // Reverse of boot order. PostgreSQL last, with SIGINT (fast shutdown, clean checkpoint).
    await Promise.all([procs.stop('backend', 8000), procs.stop('mcp', 8000), procs.stop('kinetic', 5000),
      ...kinetic.SERVICES.map((n) => procs.stop(n, 5000))])
    await Promise.all([procs.stop('portal', 5000), procs.stop('bolt', 5000)])
    await pg.stopFast(rt, dirs.dataDir) // Windows: pg_ctl (no SIGINT there); a no-op elsewhere
    await procs.stop('postgres', 20000)
    log('all stopped')
  })()
  return stopping
}

app.on('second-instance', () => {
  const w = tabs.windows()[0]
  if (w) { if (w.win.isMinimized()) w.win.restore(); w.win.focus() }
})
app.on('window-all-closed', () => app.quit())
app.on('before-quit', (e) => {
  if (stopping === 'done') return
  e.preventDefault()
  shutdown().finally(() => { stopping = 'done'; app.quit() })
})
for (const sig of ['SIGINT', 'SIGTERM']) process.on(sig, () => app.quit())

app.whenReady().then(() => {
  // the packaged app gets its icon from the bundle; `npm start` would show Electron's
  if (!app.isPackaged && process.platform === 'darwin') app.dock.setIcon(path.join(ROOT, 'build', 'icon.png'))
  buildMenu()
  createWindow()
  tray.create({
    resources: rt.resources,
    phase: () => phase,
    agent: () => agent,
    home: () => frontWindow().activate('home'),
    open: (target) => frontWindow().open(target),
    newWindow: () => new tabs.TabWindow(),
    shellOpen,
    quit: () => app.quit(),
  })
  win.webContents.once('did-finish-load', () => {
    boot().catch(async (err) => {
      lastError = String(err && err.stack || err)
      phase = 'error'
      tray.update()
      log(`BOOT FAILED: ${lastError}`)
      if (win && !win.isDestroyed()) {
        win.webContents.executeJavaScript(`window.setError && setError(${JSON.stringify(String(err.message || err))}, ${JSON.stringify(dirs.logDir)})`).catch(() => {})
      }
    })
  })
})
