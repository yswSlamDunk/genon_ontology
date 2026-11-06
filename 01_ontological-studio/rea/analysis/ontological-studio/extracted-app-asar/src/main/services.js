'use strict'
// Ontological (Bolt gateway + portal/management API) and Ontology Studio
// (backend + MCP) as child processes.
const fs = require('fs')
const path = require('path')
const procs = require('./procs')
const { SUPERUSER, GRAPH_DB, GRAPH } = require('./postgres')

function startBolt(rt, ports) {
  procs.start('bolt', path.join(rt.bin, process.platform === 'win32' ? 'ontological-bolt.exe' : 'ontological-bolt'), [], {
    env: {
      ...process.env,
      OG_BOLT_PGHOST: '127.0.0.1', OG_BOLT_PGPORT: String(ports.pg), OG_BOLT_PGDATABASE: GRAPH_DB,
      OG_BOLT_GRAPH: GRAPH, OG_BOLT_LISTEN: `127.0.0.1:${ports.bolt}`, OG_BOLT_ADVERTISED: `127.0.0.1:${ports.bolt}`,
      OG_BOLT_MAX_SESSIONS: '32',
    },
  })
  return procs.waitFor('Bolt 게이트웨이', () => procs.probeTcp(ports.bolt), { name: 'bolt', timeoutMs: 30000 })
}

/** Ontological portal: graph console + management API. Runs on Electron's own Node. */
function startPortal(rt, ports, sec) {
  procs.start('portal', process.execPath, [path.join(rt.portal, 'server', 'index.js')], {
    cwd: rt.portal,
    env: {
      ...process.env, ELECTRON_RUN_AS_NODE: '1',
      PORT: String(ports.portal), OG_STUDIO_HOST: '127.0.0.1',
      PGHOST: '127.0.0.1', PGPORT: String(ports.pg), PGDATABASE: GRAPH_DB, PGUSER: SUPERUSER, PGPASSWORD: sec.pgPassword,
    },
  })
  return procs.waitFor('Ontological 포털', () => procs.probeHttp(`http://127.0.0.1:${ports.portal}/api/health`), { name: 'portal', timeoutMs: 30000 })
}

function readUserEnv(file) {
  const out = {}
  if (!fs.existsSync(file)) return out
  for (const line of fs.readFileSync(file, 'utf8').split('\n')) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/)
    if (m && m[2] !== '') out[m[1]] = m[2].replace(/^["']|["']$/g, '')
  }
  return out
}

// ── who runs the agent ──
// Same rule as the ONTOLOGIC Studio desktop (desktop/src/main/studio.js): the default is
// `cliagents` — a coding CLI on this PC (Claude Code, or Codex) runs build and question
// turns with Studio's skills, reaching Studio's tools over the agent-bridge MCP. It brings
// its own model and login, so no API key. `deepagents` (in-process, OpenAI-compatible
// endpoint) is the fallback.
const CLIS = { 'claude-code': 'claude', codex: 'codex' }
const AGENT_LABEL = { 'claude-code': 'Claude Code', codex: 'Codex' }

/**
 * An app started from Finder gets PATH=/usr/bin:/bin:/usr/sbin:/sbin, not the login
 * shell's. Without the usual install places `claude`/`codex` would be "not installed"
 * when the app is opened from its icon, and found when it is started from a terminal.
 */
function augmentedPath() {
  const home = require('os').homedir()
  const extra = process.platform === 'win32'
    // npm global (claude.cmd · codex.cmd), Claude Code's native installer, scoop
    ? [path.join(process.env.APPDATA || '', 'npm'), path.join(home, '.local', 'bin'), path.join(home, 'scoop', 'shims')]
    : ['/opt/homebrew/bin', '/usr/local/bin', path.join(home, '.local', 'bin'), path.join(home, '.bun', 'bin'),
        path.join(home, '.deno', 'bin'), path.join(home, '.volta', 'bin'), path.join(home, '.npm-global', 'bin'), path.join(home, '.claude', 'local')]
  const dirs = (process.env.PATH || '').split(path.delimiter).filter(Boolean)
  for (const d of extra) if (!dirs.includes(d)) dirs.push(d)
  return dirs.join(path.delimiter)
}

/** PATH lookup with the rule Python's shutil.which uses — the backend looks the CLI up the same way. */
function which(name, searchPath = augmentedPath()) {
  const exts = process.platform === 'win32' ? (process.env.PATHEXT || '.EXE;.CMD;.BAT').split(';').filter(Boolean) : ['']
  for (const dir of searchPath.split(path.delimiter).filter(Boolean)) {
    for (const ext of exts) {
      const p = path.join(dir, name + ext.toLowerCase())
      try { fs.accessSync(p, fs.constants.X_OK); if (fs.statSync(p).isFile()) return p } catch {}
    }
  }
  return null
}

function detectAgentClis(searchPath = augmentedPath()) {
  return Object.fromEntries(Object.entries(CLIS).map(([id, bin]) => [id, which(bin, searchPath)]))
}

/**
 * What studio.env asks for, lowered to what this PC can actually run. A `cliagents`
 * backend whose CLI is missing makes the Studio backend refuse to start (warm_up_agent
 * raises AgentNotInstalledError), so that case falls back to the built-in agent and says why.
 */
function resolveAgent(user, searchPath = augmentedPath()) {
  const requested = (user.AGENT_BACKEND || 'cliagents').toLowerCase()
  const agentId = user.EXTERNAL_AGENT_ID === 'codex' ? 'codex' : 'claude-code'
  const llm = !!(user.OPENAI_API_KEY || user.OPENAI_BASE_URL)
  const builtin = (note) => ({ backend: 'deepagents', agentId, label: '내장 에이전트', ready: llm, note })
  if (requested !== 'cliagents') {
    return builtin(llm ? null : 'AGENT_BACKEND=deepagents 인데 LLM 접속 정보(OPENAI_API_KEY 또는 OPENAI_BASE_URL)가 비어 있습니다.')
  }
  const cli = CLIS[agentId]
  if (which(cli, searchPath)) return { backend: 'cliagents', agentId, label: AGENT_LABEL[agentId], ready: true, note: null }
  return builtin(llm
    ? `\`${cli}\` 를 찾지 못해 내장 에이전트로 실행합니다. ${AGENT_LABEL[agentId]} 를 설치하면 다음 시작부터 씁니다.`
    : `\`${cli}\` 를 찾지 못했고 LLM 키도 없습니다. ${AGENT_LABEL[agentId]} 를 설치하거나 studio.env 에 OPENAI_API_KEY 를 넣으세요.`)
}

/**
 * process.env without its PATH (Windows spells it `Path`, and a child given both `Path` and `PATH`
 * may pick either), plus UTF-8 for Python's own I/O — on Windows it would print through the
 * console code page (cp1252) and fail on Korean text.
 */
function baseEnv() {
  const env = { ...process.env }
  for (const k of Object.keys(env)) if (/^path$/i.test(k)) delete env[k]
  return { ...env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' }
}

function studioEnv(rt, dirs, ports, sec, agent, kineticEnv) {
  const user = readUserEnv(dirs.userEnv)
  const bridge = `http://127.0.0.1:${ports.web}/fabric-bridge`
  return {
    ...baseEnv(),
    ...user,
    // Windows: Studio's local sandbox runs `bash -lc`; the package carries a bash (busybox-w32) in runtime/bin
    PATH: process.platform === 'win32' ? `${rt.bin}${path.delimiter}${augmentedPath()}` : augmentedPath(),
    // ── set by the app; the user file cannot override these ──
    // Same neo4j driver, same Bolt protocol, different endpoint: the role is a PostgreSQL role.
    NEO4J_URI: `bolt://127.0.0.1:${ports.bolt}`, NEO4J_USER: SUPERUSER, NEO4J_PASSWORD: sec.pgPassword, NEO4J_DATABASE: GRAPH,
    ONTOLOGICAL_ADMIN_DEV_URL: `http://127.0.0.1:${ports.portal}`,
    // No separate production DB in the lite package: point "prod" nowhere rather than at
    // whatever happens to listen on the default 7482 on this machine.
    ONTOLOGICAL_ADMIN_PROD_URL: user.ONTOLOGICAL_ADMIN_PROD_URL || 'http://127.0.0.1:9',
    // kinetic-action: the one this package runs (kinetic.js: address + minted tokens), unless
    // studio.env points at another. Without either, a placeholder rather than the default
    // :9000, which would reach whatever else runs on this machine. Same for the reranker.
    ...(user.KINETIC_URL ? {} : kineticEnv || { KINETIC_URL: 'http://127.0.0.1:9', KINETIC_MCP_URL: 'http://127.0.0.1:9/mcp/kinetic/' }),
    ER_RERANK_URL: user.ER_RERANK_URL || 'http://127.0.0.1:9',
    // data-fabric / text2sql endpoints are served by the shell's fabric bridge, which reads
    // the Ontological fabric catalog over Bolt (no MindsDB, no separate service).
    DATAFABRIC_BASE_URL: bridge, TEXT2SQL_BASE_URL: bridge,
    AGENT_BACKEND: agent.backend, EXTERNAL_AGENT_ID: agent.agentId,
    SANDBOX_BACKEND: 'local', LOCAL_SANDBOX_ROOT: dirs.sandbox, SANDBOX_WORKDIR: '/workspace',
    BACKEND_HOST: '127.0.0.1', BACKEND_PORT: String(ports.backend),
    ANSWER_TOOLS_VIA_MCP: user.ANSWER_TOOLS_VIA_MCP || 'true',
    // The real-data tools of Studio's MCP (ontology_graph_cypher, ontology_get_datasource_schema …)
    // are registered only with this on. The dashboard profiles every class with them and the
    // question agent follows relationships with them, so this app turns it on. The MCP listens on
    // 127.0.0.1 only; an outside AI client connected to it can read source rows — studio.env can turn it off.
    MCP_ALLOW_DATASOURCE_EXPANSION: user.MCP_ALLOW_DATASOURCE_EXPANSION || 'true',
    ANSWER_MCP_TRANSPORT: 'http', ANSWER_MCP_URL: `http://127.0.0.1:${ports.mcp}/mcp`,
    BOARD_MCP_TRANSPORT: 'http', BOARD_MCP_URL: `http://127.0.0.1:${ports.mcp}/mcp`,
    MAIN_LOG_PATH: path.join(dirs.logDir, 'backend', 'app_flow.jsonl'),
    DETAIL_LOG_DIR: path.join(dirs.logDir, 'backend', 'details'),
    SESSION_DB_PATH: path.join(dirs.userData, 'sessions.db'),
    PYTHONPATH: rt.studioApp, PYTHONUNBUFFERED: '1', PYTHONDONTWRITEBYTECODE: '1',
    // settings.py calls load_dotenv(), which walks up from the bundle and would pick up any
    // stray .env above the install location. Configuration comes from studio.env only.
    PYTHON_DOTENV_DISABLED: '1',
  }
}

/** The bundled CPython: python-build-standalone keeps it at the top on Windows, under bin/ elsewhere. */
function python(rt) {
  return process.platform === 'win32' ? path.join(rt.studioPython, 'python.exe') : path.join(rt.studioPython, 'bin', 'python3')
}

/** Starts Studio backend + MCP; resolves to the agent they run with (see resolveAgent). */
async function startStudio(rt, dirs, ports, sec, kineticEnv) {
  const agent = resolveAgent(readUserEnv(dirs.userEnv))
  const env = studioEnv(rt, dirs, ports, sec, agent, kineticEnv)
  fs.mkdirSync(dirs.sandbox, { recursive: true })
  procs.start('mcp', python(rt), ['-m', 'backend.src.modules.ontology_mcp'], {
    cwd: dirs.userData, env: { ...env, MCP_TRANSPORT: 'http', MCP_HOST: '127.0.0.1', MCP_PORT: String(ports.mcp) },
  })
  procs.start('backend', python(rt), ['-m', 'uvicorn', 'backend.src.host.app:app', '--host', '127.0.0.1', '--port', String(ports.backend), '--timeout-graceful-shutdown', '3'], {
    cwd: dirs.userData, env,
  })
  await Promise.all([
    procs.waitFor('Studio 백엔드', () => procs.probeHttp(`http://127.0.0.1:${ports.backend}/openapi.json`), { name: 'backend', timeoutMs: 120000 }),
    procs.waitFor('Studio MCP', () => procs.probeTcp(ports.mcp), { name: 'mcp', timeoutMs: 120000 }),
  ])
  return agent
}

/**
 * Runs a one-off Python script with Studio's code and settings (same interpreter, env and
 * session DB as the backend) — used to seed the sample ontology through Studio's own
 * functions. Resolves to its stdout; rejects with its output on a non-zero exit.
 */
function runStudioScript(rt, dirs, ports, sec, kineticEnv, script, log, input) {
  const env = studioEnv(rt, dirs, ports, sec, resolveAgent(readUserEnv(dirs.userEnv)), kineticEnv)
  return new Promise((resolve, reject) => {
    const child = require('child_process').execFile(python(rt), [script], { cwd: dirs.userData, env, maxBuffer: 16 << 20, timeout: 300000 }, (err, stdout, stderr) => {
      if (stderr) for (const l of String(stderr).trim().split('\n').slice(-20)) log(`  ${path.basename(script)}: ${l}`)
      if (err) reject(new Error(String(stderr || err.message).trim().split('\n').slice(-3).join(' | ')))
      else resolve(stdout)
    })
    if (input !== undefined) child.stdin.end(input)
  })
}

/** Same environment as runStudioScript, but the child is handed back to stream its output (code apps). */
function spawnStudioScript(rt, dirs, ports, sec, kineticEnv, script, opts = {}) {
  const env = studioEnv(rt, dirs, ports, sec, resolveAgent(readUserEnv(dirs.userEnv)), kineticEnv)
  return require('child_process').spawn(python(rt), [script], { cwd: dirs.userData, env, windowsHide: true, ...opts })
}

/** Writes KEY=value lines into studio.env, replacing an existing (or commented-out) line. */
function updateUserEnv(file, values) {
  let lines = fs.existsSync(file) ? fs.readFileSync(file, 'utf8').split('\n') : []
  for (const [k, v] of Object.entries(values)) {
    const re = new RegExp(`^\\s*#?\\s*${k}\\s*=`)
    const i = lines.findIndex((l) => re.test(l))
    if (i >= 0) lines[i] = `${k}=${v}`
    else lines.splice(lines.length && lines[lines.length - 1] === '' ? lines.length - 1 : lines.length, 0, `${k}=${v}`)
  }
  fs.writeFileSync(file, lines.join('\n'), { mode: 0o600 })
}

// The sample's virtual types live in their own graph, away from the graph Studio builds
// ontologies in — a document about suppliers would otherwise collide with the read-only
// virtual Supplier type (writes and publish fail). Data sources are global.
const SAMPLE_GRAPH = 'sample'
const SAMPLE_SOURCES = new Set(['erp', 'wms', 'crm'])

/** Drop the sample's virtual relationships and nodes (sources erp/wms/crm) from one graph. */
async function dropSampleTypes(session, graph) {
  const rows = async (q) => (await session.run(q)).records.map((r) => r.toObject())
  let nodes
  try {
    nodes = (await rows(`SHOW VIRTUAL NODES IN ${graph}`)).filter((n) => SAMPLE_SOURCES.has(String(n.source).split('.')[0])).map((n) => n.node)
  } catch (e) {
    if (/not exist|unknown|no graph/i.test(String(e.message))) return
    throw e
  }
  for (const r of await rows(`SHOW VIRTUAL RELATIONSHIPS IN ${graph}`)) {
    // SHOW VIRTUAL RELATIONSHIPS gives the ends as "Type.property"
    const ends = [r.from, r.to].map((e) => String(e).split('.')[0])
    if (ends.some((t) => nodes.includes(t))) await session.run(`DROP VIRTUAL RELATIONSHIP ${r.relationship} IN ${graph}`)
  }
  for (const n of nodes) await session.run(`DROP VIRTUAL NODE ${n} IN ${graph}`)
}

/** First run: wire the sample DB into the fabric, statement by statement, over Bolt. */
async function seedFabric(rt, dirs, ports, sec, driver, log) {
  const marker = path.join(dirs.dataDir, '.ontology-lite-fabric')
  const ownGraph = path.join(dirs.dataDir, '.ontology-lite-fabric-sample-graph')
  if (fs.existsSync(marker) && fs.existsSync(ownGraph)) return false
  const text = fs.readFileSync(path.join(rt.resources, 'sample', 'fabric.cypher'), 'utf8')
  const stmts = text.split('\n').filter((l) => !l.trim().startsWith('//')).join('\n')
    .split(/;\s*\n/).map((s) => s.trim().replace(/;$/, '')).filter(Boolean)
  const session = driver.session({ database: GRAPH })
  try {
    if (fs.existsSync(marker)) {
      // seeded by an earlier version, into the Studio graph: move the types out
      log(`예제 가상 노드를 ${GRAPH} 그래프에서 ${SAMPLE_GRAPH} 그래프로 옮깁니다`)
      await dropSampleTypes(session, GRAPH)
    }
    for (const q of stmts) {
      try {
        const r = await session.run(q, { pw: sec.fabricPassword, port: require('neo4j-driver').int(ports.pg) })
        log(`fabric: ${r.records[0] ? JSON.stringify(r.records[0].toObject()) : q.slice(0, 60)}`)
      } catch (e) {
        if (!/already exists/i.test(String(e.message))) throw e
        log(`fabric: skip (exists) ${q.slice(0, 60)}`)
      }
    }
  } finally { await session.close() }
  fs.writeFileSync(marker, new Date().toISOString())
  fs.writeFileSync(ownGraph, SAMPLE_GRAPH)
  return true
}

/**
 * Data sources remember the PostgreSQL port they were created with (the FDW loops
 * back to this same instance). The port is sticky (ports.json), so this only runs
 * when the preferred port was taken by something else. Re-registering is done with
 * fabric statements over Bolt: drop the sample's virtual types, drop the data
 * sources, and seed again.
 */
async function repointFabric(ports, sec, driver, log, dirs) {
  const f = path.join(dirs.dataDir, '.ontology-lite-fabric-port')
  const prev = fs.existsSync(f) ? Number(fs.readFileSync(f, 'utf8')) : ports.pg
  // The new port is recorded only once the work is done — a run that fails half-way
  // must try again next time, not leave the data sources on the old port.
  if (prev === ports.pg || !fs.existsSync(path.join(dirs.dataDir, '.ontology-lite-fabric'))) {
    fs.writeFileSync(f, String(ports.pg))
    return
  }
  await resetSampleFabric(driver, log, dirs, `PostgreSQL 포트가 ${prev} → ${ports.pg} 로 바뀌어 예제 데이터소스를 다시 등록합니다`)
  fs.writeFileSync(f, String(ports.pg))
}

/**
 * Drops the sample's virtual types and data sources so that seedFabric registers them again.
 * Used when the sample DB moved (port) or its tables changed: a foreign table keeps the
 * columns it was imported with, and REFRESH DATASOURCE only picks up new tables.
 */
async function resetSampleFabric(driver, log, dirs, why) {
  if (!fs.existsSync(path.join(dirs.dataDir, '.ontology-lite-fabric'))) return
  log(why)
  const session = driver.session({ database: GRAPH })
  try {
    for (const g of [SAMPLE_GRAPH, GRAPH]) await dropSampleTypes(session, g)
    for (const ds of SAMPLE_SOURCES) await session.run(`DROP DATASOURCE ${ds}`).catch(() => {})
  } finally { await session.close() }
  fs.rmSync(path.join(dirs.dataDir, '.ontology-lite-fabric'), { force: true })
  fs.rmSync(path.join(dirs.dataDir, '.ontology-lite-fabric-sample-graph'), { force: true })
}

module.exports = { python, baseEnv, augmentedPath, startBolt, startPortal, startStudio, runStudioScript, spawnStudioScript, seedFabric, repointFabric, resetSampleFabric, readUserEnv, updateUserEnv, detectAgentClis, resolveAgent, AGENT_LABEL, SAMPLE_GRAPH }
