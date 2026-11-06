'use strict'
// The single PostgreSQL instance. It holds two databases:
//   ogstudio — Ontological's storage (extension `ontological`, graph `ontology`)
//   sample   — the sample business data (schemas erp / wms / crm) that the
//              data fabric reaches through postgres_fdw on the same instance.
// This module only does what an installer does (initdb, CREATE DATABASE,
// CREATE EXTENSION, load sample). Everything after that goes through Bolt.
const fs = require('fs')
const path = require('path')
const crypto = require('crypto')
const { execFile } = require('child_process')
const procs = require('./procs')

const SUPERUSER = 'og'
const GRAPH_DB = 'ogstudio'
const GRAPH = 'ontology'
const SAMPLE_DB = 'sample'

function secrets(userData) {
  const f = path.join(userData, 'secrets.json')
  if (fs.existsSync(f)) return JSON.parse(fs.readFileSync(f, 'utf8'))
  const s = { pgPassword: crypto.randomBytes(18).toString('base64url'), fabricPassword: crypto.randomBytes(18).toString('base64url') }
  fs.writeFileSync(f, JSON.stringify(s, null, 2), { mode: 0o600 })
  return s
}

function saveSecrets(userData, sec) {
  fs.writeFileSync(path.join(userData, 'secrets.json'), JSON.stringify(sec, null, 2), { mode: 0o600 })
}

const EXE = process.platform === 'win32' ? '.exe' : ''
function bin(rt, name) { return path.join(rt.pg, 'bin', name + EXE) }

function run(cmd, args, env) {
  return new Promise((resolve, reject) => {
    execFile(cmd, args, { env: { ...process.env, ...env }, maxBuffer: 16 << 20 }, (err, stdout, stderr) => {
      if (err) reject(new Error(`${path.basename(cmd)} ${args.slice(-2).join(' ')}: ${stderr || err.message}`))
      else resolve(stdout)
    })
  })
}

function psql(rt, port, password, db, sqlOrFile, { file = false } = {}) {
  const args = ['-h', '127.0.0.1', '-p', String(port), '-U', SUPERUSER, '-d', db, '-v', 'ON_ERROR_STOP=1', '-q', '-X']
  args.push(file ? '-f' : '-c', sqlOrFile)
  return run(bin(rt, 'psql'), args, { PGPASSWORD: password, PGCONNECT_TIMEOUT: '5' })
}

async function initdb(rt, dataDir, password, log) {
  if (fs.existsSync(path.join(dataDir, 'PG_VERSION'))) return false
  fs.mkdirSync(dataDir, { recursive: true, mode: 0o700 })
  const pw = path.join(path.dirname(dataDir), '.pwfile')
  fs.writeFileSync(pw, password, { mode: 0o600 })
  try {
    log('initdb')
    await run(bin(rt, 'initdb'), ['-D', dataDir, '-U', SUPERUSER, '--auth=scram-sha-256', `--pwfile=${pw}`, '-E', 'UTF8', '--locale=C', '--no-instructions'])
  } finally { fs.rmSync(pw, { force: true }) }
  // Small-footprint settings for a desktop. Port/listen are passed per start.
  fs.appendFileSync(path.join(dataDir, 'postgresql.conf'), [
    '', '# ontology-studio-lite',
    'shared_buffers = 64MB', 'max_connections = 40', 'work_mem = 8MB', 'maintenance_work_mem = 64MB',
    'max_wal_size = 256MB', 'min_wal_size = 32MB', 'wal_level = minimal', 'max_wal_senders = 0',
    'autovacuum_naptime = 5min', 'log_min_messages = warning', 'logging_collector = off', ''
  ].join('\n'))
  return true
}

function start(rt, dataDir, port) {
  // A server killed hard leaves postmaster.pid behind; nothing listens on our port, so it is stale.
  const pidFile = path.join(dataDir, 'postmaster.pid')
  if (fs.existsSync(pidFile)) {
    const pid = Number(fs.readFileSync(pidFile, 'utf8').split('\n')[0])
    let live = false; try { process.kill(pid, 0); live = true } catch {}
    if (!live) fs.rmSync(pidFile, { force: true })
  }
  const env = {
    ...process.env, LC_ALL: 'C',
    // mysql_fdw's client (MariaDB Connector/C 3.4) verifies a remote server's TLS certificate by
    // default, unlike MySQL's own client (ssl-mode=PREFERRED: encrypted, not verified). Servers with
    // self-signed certificates — most of them — would refuse. Keep MySQL's behaviour.
    MARIADB_TLS_DISABLE_PEER_VERIFICATION: '1',
  }
  if (process.platform === 'win32') {
    // postgres.exe refuses to run with administrative rights (an elevated session, a CI runner);
    // pg_ctl starts it with a restricted token. It is then not our child process: stopFast() stops
    // it with pg_ctl, and waitReady() watches the port instead of the process.
    const logFile = path.join(path.dirname(dataDir), 'logs', 'postgres.log')
    execFile(bin(rt, 'pg_ctl'), ['start', '-W', '-D', dataDir, '-l', logFile, '-o', `-p ${port} -c listen_addresses=127.0.0.1`],
      { env, windowsHide: true }, () => {})
    return null
  }
  return procs.start('postgres', bin(rt, 'postgres'), [
    '-D', dataDir, '-p', String(port), '-c', 'listen_addresses=127.0.0.1', '-c', 'unix_socket_directories=',
  ], { env, stopSignal: 'SIGINT' })
}

async function waitReady(rt, port) {
  return procs.waitFor('PostgreSQL', async () => {
    try { await run(bin(rt, 'pg_isready'), ['-h', '127.0.0.1', '-p', String(port), '-q']); return true } catch { return false }
  }, { name: process.platform === 'win32' ? undefined : 'postgres', timeoutMs: 60000 })
}

/** First-run bootstrap. Idempotent: guarded by a marker file in the data dir. */
async function bootstrap(rt, dataDir, port, sec, log) {
  const marker = path.join(dataDir, '.ontology-lite-bootstrap')
  if (fs.existsSync(marker)) return false
  const pw = sec.pgPassword
  log('CREATE DATABASE ogstudio + EXTENSION ontological')
  await psql(rt, port, pw, 'postgres', `SELECT 1`)
  const dbs = await psql(rt, port, pw, 'postgres', `SELECT string_agg(datname, ',') FROM pg_database`)
  if (!dbs.includes(GRAPH_DB)) await psql(rt, port, pw, 'postgres', `CREATE DATABASE ${GRAPH_DB}`)
  await psql(rt, port, pw, GRAPH_DB, 'CREATE EXTENSION IF NOT EXISTS ontological CASCADE')
  await psql(rt, port, pw, GRAPH_DB, 'CREATE EXTENSION IF NOT EXISTS postgres_fdw')
  // Same as ontology-studio/scripts/ontological-entrypoint.sh: the graph and the
  // abstract `_Entity` root type Studio expects.
  await psql(rt, port, pw, GRAPH_DB, `SELECT og_create_graph('${GRAPH}')`)
  await psql(rt, port, pw, GRAPH_DB, `SELECT og_create_type('${GRAPH}', '_Entity', 'entity', '{}'::text[], true)
     WHERE NOT EXISTS (SELECT 1 FROM og_catalog.type t JOIN og_catalog.graph g USING (graph_id)
                        WHERE g.name = '${GRAPH}' AND t.name = '_Entity')`)
  log('sample DB (erp · wms · crm)')
  if (!dbs.includes(SAMPLE_DB)) {
    await psql(rt, port, pw, 'postgres', `CREATE DATABASE ${SAMPLE_DB}`)
    await psql(rt, port, pw, SAMPLE_DB, path.join(rt.resources, 'sample', 'sample.sql'), { file: true })
  }
  await psql(rt, port, pw, SAMPLE_DB, `ALTER ROLE fabric_ro PASSWORD '${sec.fabricPassword.replace(/'/g, "''")}'`)
  fs.writeFileSync(marker, new Date().toISOString())
  return true
}

/**
 * The sample microservices' tables and account (resources/sample/services.sql). Runs once per
 * data folder — on a new one right after bootstrap, on an older one at its next start.
 * Returns true when it ran, so the caller can refresh the fabric's view of those schemas.
 */
async function migrateServices(rt, dataDir, port, sec, log) {
  const marker = path.join(dataDir, '.ontology-lite-services')
  if (fs.existsSync(marker)) return false
  log('예제 마이크로서비스 테이블 · 계정 (services.sql)')
  await psql(rt, port, sec.pgPassword, SAMPLE_DB, path.join(rt.resources, 'sample', 'services.sql'), { file: true })
  await psql(rt, port, sec.pgPassword, SAMPLE_DB, `ALTER ROLE sample_svc PASSWORD '${sec.svcPassword.replace(/'/g, "''")}'`)
  fs.writeFileSync(marker, new Date().toISOString())
  return true
}

/**
 * Windows: a child process cannot be sent SIGINT (Node's kill() terminates it), and PostgreSQL
 * would then recover from WAL at the next start. pg_ctl asks for a fast shutdown instead.
 * Elsewhere procs.stop('postgres') sends SIGINT, which is the same fast shutdown.
 */
async function stopFast(rt, dataDir) {
  if (process.platform !== 'win32') return
  await run(bin(rt, 'pg_ctl'), ['stop', '-D', dataDir, '-m', 'fast', '-w', '-t', '20']).catch(() => {})
}

module.exports = { SUPERUSER, GRAPH_DB, GRAPH, SAMPLE_DB, secrets, saveSecrets, initdb, start, waitReady, bootstrap, migrateServices, stopFast }
