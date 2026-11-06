'use strict'
// Actions (kinetic layer): kinetic-action + three sample microservices, as child processes.
//
//   kinetic-action  plans an action over graph instances, checks policy, waits for a person's
//                   approval and runs the steps against registered systems (direct mode: it
//                   calls each system's base_url itself and adds that system's auth).
//   erp · wms · crm the sample business systems. Each owns one schema of the sample DB, so an
//                   action's effect shows up in the fabric (virtual nodes, 데이터소스 tab) as is.
//
// kinetic-action only accepts RS256 JWTs it can verify against a JWKS. There is no identity
// provider in this package, so the app holds one signing key (secrets.json) and serves its
// public half at /kinetic-idp/jwks.json on the local origin. Tokens are minted at start-up
// for Studio (approve · register systems) and for the agent (plan · execute).
const crypto = require('crypto')
const path = require('path')
const procs = require('./procs')

const AUDIENCE = 'kinetic-action'
const ISSUER = 'ontology-studio-lite'
const TOKEN_DAYS = 30

// Who may run the sample actions (policy `roles`). Studio shows this list to the build
// agent so it does not invent role names (KINETIC_ROLE_CATALOG).
const ROLE_CATALOG = [
  { role: 'scm_operator', description: '공급망 운영 담당 — 출하 우선순위·발주 보류·고객 안내를 요청할 수 있다', claims: [] },
]

/** Fills the per-install secrets this module needs into `sec` (and says whether it added any). */
function ensureSecrets(sec) {
  let added = false
  const put = (k, make) => { if (!sec[k]) { sec[k] = make(); added = true } }
  const rnd = () => crypto.randomBytes(18).toString('base64url')
  put('svcPassword', rnd)
  put('erpApiKey', rnd)
  put('wmsBasic', () => `kinetic:${rnd()}`)
  put('crmToken', rnd)
  put('kineticInternal', rnd)
  put('kineticKey', () => crypto.generateKeyPairSync('rsa', { modulusLength: 2048 }).privateKey.export({ type: 'pkcs8', format: 'pem' }))
  return added
}

function kid(sec) { return crypto.createHash('sha256').update(sec.kineticKey).digest('base64url').slice(0, 16) }

function jwks(sec) {
  const jwk = crypto.createPublicKey(sec.kineticKey).export({ format: 'jwk' })
  return { keys: [{ ...jwk, kid: kid(sec), alg: 'RS256', use: 'sig' }] }
}

function token(sec, sub, roles, claims = {}) {
  const now = Math.floor(Date.now() / 1000)
  const b64 = (o) => Buffer.from(JSON.stringify(o)).toString('base64url')
  const data = `${b64({ alg: 'RS256', typ: 'JWT', kid: kid(sec) })}.${b64({ sub, roles, ...claims, aud: AUDIENCE, iss: ISSUER, iat: now, exp: now + TOKEN_DAYS * 86400 })}`
  return `${data}.${crypto.sign('RSA-SHA256', Buffer.from(data), sec.kineticKey).toString('base64url')}`
}

const SERVICES = ['erp', 'wms', 'crm']

function pyEnv(rt, extra) {
  const site = path.join(rt.root, 'kinetic', 'site')
  return { ...baseEnv(), PATH: process.env.PATH || process.env.Path || '', PYTHONPATH: extra ? `${site}${path.delimiter}${extra}` : site,
    PYTHONDONTWRITEBYTECODE: '1', PYTHONUNBUFFERED: '1', PYTHON_DOTENV_DISABLED: '1' }
}
const { python, baseEnv } = require('./services')
const secretsEnv = (sec) => ({ ERP_API_KEY: sec.erpApiKey, WMS_BASIC: sec.wmsBasic, CRM_TOKEN: sec.crmToken })

/** Starts the three sample services and kinetic-action; resolves when all answer. */
async function start(rt, dirs, ports, sec, { superuser, graph }) {
  const svcDir = path.join(rt.resources, 'sample', 'services')
  for (const name of SERVICES) {
    procs.start(name, python(rt), ['-m', 'uvicorn', `${name}:app`, '--host', '127.0.0.1', '--port', String(ports[name]), '--log-level', 'warning', '--timeout-graceful-shutdown', '1'], {
      cwd: svcDir,
      env: { ...pyEnv(rt, svcDir), ...secretsEnv(sec), SAMPLE_DSN: `postgresql://sample_svc:${encodeURIComponent(sec.svcPassword)}@127.0.0.1:${ports.pg}/sample` },
    })
  }
  const app = path.join(rt.root, 'kinetic', 'app')
  procs.start('kinetic', python(rt), ['-m', 'uvicorn', 'app.main:_default_app', '--factory', '--host', '127.0.0.1', '--port', String(ports.kinetic), '--timeout-graceful-shutdown', '1'], {
    cwd: dirs.userData,
    env: {
      ...pyEnv(rt, app), ...secretsEnv(sec),
      KINETIC_DB_URL: `sqlite:///${path.join(dirs.userData, 'kinetic.db')}`,
      KINETIC_NEO4J_URI: `bolt://127.0.0.1:${ports.bolt}`, KINETIC_NEO4J_USER: superuser, KINETIC_NEO4J_PASSWORD: sec.pgPassword, KINETIC_NEO4J_DATABASE: graph,
      KINETIC_JWKS_URL: `http://127.0.0.1:${ports.web}/kinetic-idp/jwks.json`, KINETIC_AUDIENCE: AUDIENCE, KINETIC_ISSUER: ISSUER,
      KINETIC_INTERNAL_SECRET: sec.kineticInternal,
      KINETIC_PUBLIC_BASE: `http://127.0.0.1:${ports.kinetic}`, KINETIC_PORT: String(ports.kinetic), KINETIC_SVC_DIRECT: '1',
    },
  })
  await Promise.all([
    ...SERVICES.map((n) => procs.waitFor(`예제 ${n.toUpperCase()} 서비스`, () => procs.probeHttp(`http://127.0.0.1:${ports[n]}/health`), { name: n, timeoutMs: 60000 })),
    procs.waitFor('kinetic-action', () => procs.probeHttp(`http://127.0.0.1:${ports.kinetic}/api/kinetic/health`), { name: 'kinetic', timeoutMs: 60000 }),
  ])
}

/** What Studio needs to reach kinetic-action (studio.env may point at another one instead). */
function studioEnv(ports, sec) {
  return {
    KINETIC_URL: `http://127.0.0.1:${ports.kinetic}`,
    KINETIC_MCP_URL: `http://127.0.0.1:${ports.kinetic}/mcp/`,
    // The desktop's one person is also the operator: the dashboard's and the code apps' action
    // buttons plan with this token, so it carries the role the sample policies ask for.
    KINETIC_STUDIO_TOKEN: token(sec, 'lite-user', ['kinetic_admin', 'kinetic_approver', ...ROLE_CATALOG.map((r) => r.role)]),
    KINETIC_AGENT_TOKEN: token(sec, 'lite-agent', ['scm_operator']),
    KINETIC_ROLE_CATALOG: JSON.stringify(ROLE_CATALOG),
  }
}

// The sample systems as a company would register them: who owns it, how to reach it, how it
// authenticates (the secret itself stays in kinetic-action's environment, only its name here).
const SYSTEMS = {
  erp: { display_name: '구매 ERP', description: '발주 보류·해제, 협력사 납기 독촉', owner_team: '구매팀', icon: 'erp',
    tags: ['erp', 'purchasing', 'sample'], auth: { kind: 'api_key', header: 'X-API-Key', secret_env: 'ERP_API_KEY' } },
  wms: { display_name: '물류 WMS', description: '입고 선적 조회·우선순위 변경', owner_team: '물류팀', icon: 'wms',
    tags: ['wms', 'logistics', 'sample'], auth: { kind: 'basic', secret_env: 'WMS_BASIC' } },
  crm: { display_name: '고객 CRM', description: '고객 안내 발송·철회', owner_team: '고객지원팀', icon: 'crm',
    tags: ['crm', 'customer', 'sample'], auth: { kind: 'bearer', secret_env: 'CRM_TOKEN' } },
}
const systemName = (n) => `sample-${n}`

/** Registers the sample systems that are not registered yet (an edited registration is kept). */
async function registerSystems(ports, sec, log) {
  const base = `http://127.0.0.1:${ports.kinetic}/api/kinetic`
  const headers = { authorization: `Bearer ${token(sec, 'lite-setup', ['kinetic_admin'])}`, 'content-type': 'application/json' }
  const r = await fetch(`${base}/systems`, { headers })
  if (!r.ok) throw new Error(`kinetic-action systems: ${r.status} ${await r.text()}`)
  const have = new Set((await r.json()).map((s) => s.name))
  const added = []
  for (const n of SERVICES) {
    if (have.has(systemName(n))) continue
    const url = `http://127.0.0.1:${ports[n]}`
    const body = { name: systemName(n), base_url: url, openapi_url: `${url}/openapi.json`, health_path: '/health', protocol: 'rest',
      timeout_ms: 5000, retries: 2, environments: [{ name: 'local', base_url: url }], active_environment: 'local', ...SYSTEMS[n] }
    const res = await fetch(`${base}/systems`, { method: 'POST', headers, body: JSON.stringify(body) })
    if (!res.ok) throw new Error(`register ${systemName(n)}: ${res.status} ${await res.text()}`)
    added.push(systemName(n))
  }
  if (added.length) log(`시스템 등록: ${added.join(', ')}`)
  return added
}

/**
 * The sample systems' base_url carries their port. Ports are sticky, but when one had to move
 * the registration is pointed at the new address (other settings are left as they are).
 */
async function repointSystems(ports, sec, log) {
  const base = `http://127.0.0.1:${ports.kinetic}/api/kinetic`
  const headers = { authorization: `Bearer ${token(sec, 'lite-setup', ['kinetic_admin'])}`, 'content-type': 'application/json' }
  const list = await (await fetch(`${base}/systems`, { headers })).json()
  for (const n of SERVICES) {
    const s = list.find((x) => x.name === systemName(n))
    const url = `http://127.0.0.1:${ports[n]}`
    if (!s || s.base_url === url) continue
    const body = { ...s, base_url: url, openapi_url: `${url}/openapi.json`, environments: [{ name: 'local', base_url: url }], active_environment: 'local' }
    const res = await fetch(`${base}/systems`, { method: 'POST', headers, body: JSON.stringify(body) })
    log(`시스템 주소 갱신 ${s.name}: ${s.base_url} → ${url} (${res.status})`)
  }
}

module.exports = { ensureSecrets, jwks, token, start, studioEnv, registerSystems, repointSystems, SERVICES, ROLE_CATALOG, systemName }
