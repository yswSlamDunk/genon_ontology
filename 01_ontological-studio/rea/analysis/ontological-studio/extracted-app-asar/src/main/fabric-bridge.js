'use strict'
// data-fabric / text2sql compatible catalog endpoints for Ontology Studio,
// answered from Ontological's built-in data fabric over Bolt — and the
// datasource tab's own endpoints (/fabric/*).
//
// Studio's datasource features were written against two HTTP services
// (data-fabric :8004 over MindsDB, neo4j-text2sql :8020). In this package the
// fabric lives inside Ontological, so the shell answers the *catalog reads*
// those services used to answer, using fabric statements only:
//   SHOW DATASOURCES / SHOW TABLES FROM <ds> / SHOW COLUMNS FROM <ds>.<t> / MATCH (n:<VirtualNode>) …
// No SQL is sent to Ontological's internals (ontological-layering rule).
// Free-form SQL execution (text2sql direct-sql, MindsDB statements) is not
// offered: in Ontological, querying a source goes through virtual nodes.
//
// The datasource tab changes the fabric the same way: each write endpoint takes
// a structured body, builds exactly one fabric statement from it (identifiers
// checked, values passed as Bolt parameters), and returns that statement so the
// screen can show what ran. `{"dry": true}` returns the statement without running it.
const { URL } = require('url')
const neo4j = require('neo4j-driver')

function plain(v) {
  if (neo4j.isInt(v)) return v.inSafeRange() ? v.toNumber() : v.toString()
  if (v && typeof v === 'object') {
    if (v.properties && v.labels) return plain(v.properties)
    if (Array.isArray(v)) return v.map(plain)
    if (typeof v.toString === 'function' && v.constructor && /Date|Time|Duration|Point/.test(v.constructor.name)) return v.toString()
    const o = {}; for (const [k, x] of Object.entries(v)) o[k] = plain(x); return o
  }
  return v
}

function typeOf(v) {
  if (v === null || v === undefined) return 'unknown'
  if (typeof v === 'number') return Number.isInteger(v) ? 'integer' : 'numeric'
  if (typeof v === 'boolean') return 'boolean'
  if (/^\d{4}-\d{2}-\d{2}$/.test(String(v))) return 'date'
  return 'text'
}

const bad = (msg, status = 400) => Object.assign(new Error(msg), { status })
const ident = (x, what = 'identifier') => {
  if (typeof x !== 'string' || !/^[A-Za-z_][A-Za-z0-9_]*$/.test(x)) throw bad(`${what} 은(는) 영문·숫자·밑줄만 쓸 수 있고 숫자로 시작할 수 없습니다: ${JSON.stringify(x)}`)
  return x
}
// Datasource names become schema names; the engine takes lower case only.
const dsName = (x) => {
  if (typeof x !== 'string' || !/^[a-z_][a-z0-9_]*$/.test(x)) throw bad(`데이터소스 이름은 영문 소문자·숫자·밑줄만 쓸 수 있고 숫자로 시작할 수 없습니다: ${JSON.stringify(x)}`)
  return x
}
// Ontological's messages arrive wrapped by the driver/Bolt; keep the sentence that matters.
const engineMessage = (e) => String(e && e.message || e).replace(/^.*?(ERROR:\s*)/s, '').replace(/^fabric statement:\s*/, '').trim()

// `graph` is the graph Studio builds ontologies in; virtual types may live in any graph
// (the sample's are in their own, `sampleGraph`), so reads look across graphs and writes
// name theirs with `IN <graph>`.
function createBridge(getDriver, graph, { sampleGraph = graph, engines = null } = {}) {
  async function run(cypher, params = {}, mode = 'READ', g = graph) {
    const s = getDriver().session({ database: g, defaultAccessMode: neo4j.session[mode] })
    try { return (await s.run(cypher, params)).records.map((r) => plain(r.toObject())) } finally { await s.close() }
  }
  const q = (cypher, params, g) => run(cypher, params, 'READ', g)
  async function graphs() {
    return (await q('SHOW GRAPHS')).map((r) => r.graph)
  }
  async function virtualNodes() {
    const out = []
    for (const g of await graphs()) for (const n of await q(`SHOW VIRTUAL NODES IN ${ident(g)}`)) out.push({ ...n, graph: g })
    return out
  }
  async function virtualRelationships() {
    const out = []
    for (const g of await graphs()) for (const r of await q(`SHOW VIRTUAL RELATIONSHIPS IN ${ident(g)}`)) out.push({ ...r, graph: g })
    return out
  }

  async function datasources() {
    return (await q('SHOW DATASOURCES')).map((d) => ({ name: d.name, engine: d.engine, display_name: d.name, database: d.name, host: d.host, table_count: d.tables }))
  }
  async function tables(ds) {
    return (await q(`SHOW TABLES FROM ${ident(ds, '데이터소스 이름')}`)).map((t) => ({
      name: String(t.table).replace(`${ds}.`, ''), schema: ds, column_count: t.columns, virtual_node: t.virtual_node, description: t.virtual_node ? `가상 노드 :${t.virtual_node}` : '',
    }))
  }
  async function sample(ds, table, limit) {
    const t = (await tables(ds)).find((x) => x.name === table)
    if (!t) throw bad(`table ${ds}.${table} not found`, 404)
    if (!t.virtual_node) return { columns: [], rows: [], note: `${ds}.${table} 에 가상 노드가 없습니다. CREATE VIRTUAL NODE … FROM ${ds}.${table} KEY … 로 노출하면 읽을 수 있습니다.` }
    // A table can back more than one node type; the first one is enough to read it — in its own graph.
    const node = (await virtualNodes()).find((n) => n.source === `${ds}.${table}`)
    const label = node ? node.node : String(t.virtual_node).split(',')[0].trim()
    const g = node ? node.graph : graph
    const rows = (await q(`MATCH (n:${ident(label)}) RETURN n LIMIT ${Math.max(1, Math.min(200, limit | 0 || 10))}`, {}, g)).map((r) => {
      const o = { ...r.n }; delete o._id; delete o._type; return o
    })
    const columns = rows.length ? Object.keys(rows[0]) : []
    return { columns, rows: rows.map((r) => columns.map((c) => r[c])), virtual_node: label, graph: g }
  }
  // SHOW COLUMNS is this package's addition to Ontological (patches/ontological). An engine
  // without it still answers for mapped tables, with types guessed from a sample row.
  async function columns(ds, table) {
    try {
      return (await q(`SHOW COLUMNS FROM ${ident(ds, '데이터소스 이름')}.${ident(table, '테이블 이름')}`)).map((c) => ({
        name: c.column, type: c.type, nullable: !!c.nullable, primary_key: !!c.key, description: '',
      }))
    } catch (e) {
      if (!/SHOW COLUMNS|not a fabric statement|expected/i.test(engineMessage(e))) throw e
      const s = await sample(ds, table, 1)
      if (!s.rows.length) return []
      return s.columns.map((c, i) => ({ name: c, type: typeOf(s.rows[0][i]), nullable: true, primary_key: false, description: '' }))
    }
  }
  async function overview() {
    const [ds, gs, nodes, rels] = await Promise.all([datasources(), graphs(), virtualNodes(), virtualRelationships()])
    return { graph, sample_graph: sampleGraph, graphs: gs, datasources: ds, virtual_nodes: nodes, virtual_relationships: rels }
  }
  const graphOf = (b) => ident(b.graph || sampleGraph, '그래프 이름')

  // ── writes: one structured body → one fabric statement ──
  // Engines this package has connectors for (scripts/build-fdw.sh) and the parameters each takes.
  const ENGINES = {
    postgres: { port: 5432, schema: 'public', required: ['host', 'database', 'user'], keys: ['host', 'port', 'database', 'schema', 'user', 'password'] },
    mysql: { port: 3306, required: ['host', 'database', 'user'], keys: ['host', 'port', 'database', 'user', 'password'] },
    oracle: { port: 1521, required: ['host', 'service', 'schema', 'user'], keys: ['host', 'port', 'service', 'schema', 'user', 'password'] },
    sqlserver: { port: 1433, schema: 'dbo', required: ['host', 'database', 'user'], keys: ['host', 'port', 'database', 'schema', 'user', 'password'] },
  }
  const ENGINE_ALIAS = { postgres: 'postgres', postgresql: 'postgres', mysql: 'mysql', mariadb: 'mysql', oracle: 'oracle', sqlserver: 'sqlserver', mssql: 'sqlserver' }
  const statements = {
    createDatasource(b) {
      const name = dsName(b.name)
      const engine = ENGINE_ALIAS[String(b.engine || 'postgres').toLowerCase()]
      if (!engine) throw bad(`지원하는 엔진: ${Object.keys(ENGINES).join(', ')}`)
      // engines whose connector this installation carries (index.js reads the extension files)
      if (engines && !engines.includes(engine)) throw bad(`이 설치에는 ${engine} 커넥터가 없습니다. 지금 쓸 수 있는 엔진: ${engines.join(', ')}`)
      const spec = ENGINES[engine]
      for (const k of spec.required) if (!b[k] || typeof b[k] !== 'string') throw bad(`${k} 를 입력하세요.`)
      const port = Number(b.port || spec.port)
      if (!Number.isInteger(port) || port < 1 || port > 65535) throw bad('포트는 1~65535 사이 정수여야 합니다.')
      // values go as Bolt parameters; only the keys this engine takes, in its order
      const vals = { host: b.host, port, database: b.database, service: b.service, schema: b.schema || spec.schema, user: b.user, password: String(b.password || '') }
      const keys = spec.keys.filter((k) => vals[k] !== undefined && vals[k] !== '')
      const params = Object.fromEntries(keys.map((k) => [k, k === 'port' ? neo4j.int(port) : vals[k]]))
      const head = `CREATE DATASOURCE ${name} WITH ENGINE = '${engine}', PARAMETERS = `
      return {
        text: head + `{${keys.map((k) => `${k}: $${k}`).join(', ')}}`,
        params,
        shown: head + `{${keys.map((k) => `${k}: ${k === 'password' ? "'••••'" : k === 'port' ? port : `'${vals[k]}'`}`).join(', ')}}`,
      }
    },
    dropDatasource: (b) => ({ text: `DROP DATASOURCE ${ident(b.name, '데이터소스 이름')}` }),
    refreshDatasource: (b) => ({ text: `REFRESH DATASOURCE ${ident(b.name, '데이터소스 이름')}` }),
    createVirtualNode(b) {
      const label = ident(b.label, '노드 타입 이름')
      const [ds, table] = String(b.source || '').split('.')
      const key = ident(b.key, 'KEY 컬럼')
      let text = `CREATE VIRTUAL NODE ${label} IN ${graphOf(b)} FROM ${ident(ds, '데이터소스 이름')}.${ident(table, '테이블 이름')} KEY ${key}`
      const props = Array.isArray(b.properties) ? b.properties : []
      if (props.length) {
        const list = props.map((p) => {
          const col = ident(typeof p === 'string' ? p : p.column, '컬럼 이름')
          const as = typeof p === 'object' && p.as && p.as !== col ? ident(p.as, '속성 이름') : ''
          return as ? `${col} AS ${as}` : col
        })
        if (!props.some((p) => (typeof p === 'string' ? p : p.column) === key)) list.unshift(key)
        text += ` PROPERTIES (${list.join(', ')})`
      }
      return { text }
    },
    dropVirtualNode: (b) => ({ text: `DROP VIRTUAL NODE ${ident(b.label, '노드 타입 이름')} IN ${graphOf(b)}` }),
    createVirtualRelationship(b) {
      const f = b.from || {}, t = b.to || {}
      return { text: `CREATE VIRTUAL RELATIONSHIP ${ident(b.name, '관계 이름')} IN ${graphOf(b)} FROM ${ident(f.node, '출발 노드')}(${ident(f.property, '출발 속성')}) TO ${ident(t.node, '도착 노드')}(${ident(t.property, '도착 속성')})` }
    },
    dropVirtualRelationship: (b) => ({ text: `DROP VIRTUAL RELATIONSHIP ${ident(b.name, '관계 이름')} IN ${graphOf(b)}` }),
  }
  async function write(kind, body) {
    const st = statements[kind](body || {})
    const shown = st.shown || st.text
    if (body && body.dry) return { statement: shown }
    try {
      const rows = await run(st.text, st.params || {}, 'WRITE')
      return { statement: shown, result: rows[0] ? rows[0].result ?? rows[0] : null }
    } catch (e) {
      throw Object.assign(bad(engineMessage(e), 422), { statement: shown })
    }
  }

  const GET = [
    [/^\/api\/datasources\/?$/, async () => ({ datasources: await datasources() })],
    [/^\/api\/datasources\/([^/]+)\/?$/, async (m) => (await datasources()).find((d) => d.name === m[1]) || Promise.reject(bad('not found', 404))],
    [/^\/api\/datasources\/([^/]+)\/health$/, async (m) => { await tables(m[1]); return { status: 'ok', datasource: m[1] } }],
    [/^\/api\/datasources\/([^/]+)\/schemas$/, async (m) => ({ schemas: [{ name: m[1], description: '', table_count: (await tables(m[1])).length }] })],
    [/^\/api\/datasources\/([^/]+)\/tables$/, async (m) => ({ tables: await tables(m[1]) })],
    [/^\/api\/datasources\/([^/]+)\/tables\/([^/]+)\/schema$/, async (m) => ({ columns: await columns(m[1], m[2]) })],
    [/^\/api\/datasources\/([^/]+)\/tables\/([^/]+)\/sample$/, async (m, u) => sample(m[1], m[2], Number(u.searchParams.get('limit') || 10))],
    [/^\/text2sql\/meta\/tables\/([^/]+)\/columns$/, async (m, u) => ({ columns: await columns(u.searchParams.get('datasource') || '', m[1]) })],
    [/^\/health$/, async () => ({ status: 'ok', engine: 'ontological-fabric' })],
    // datasource tab
    [/^\/fabric\/overview$/, async () => overview()],
    [/^\/fabric\/engines$/, async () => ({ engines: engines || Object.keys(ENGINES) })],
    [/^\/fabric\/datasources\/([^/]+)\/tables$/, async (m) => ({ tables: await tables(m[1]) })],
    [/^\/fabric\/datasources\/([^/]+)\/tables\/([^/]+)\/columns$/, async (m) => ({ columns: await columns(m[1], m[2]) })],
    [/^\/fabric\/datasources\/([^/]+)\/tables\/([^/]+)\/preview$/, async (m, u) => sample(m[1], m[2], Number(u.searchParams.get('limit') || 20))],
  ]
  const WRITE = [
    ['POST', /^\/fabric\/datasources$/, (m, b) => write('createDatasource', b)],
    ['DELETE', /^\/fabric\/datasources\/([^/]+)$/, (m, b) => write('dropDatasource', { ...b, name: m[1] })],
    ['POST', /^\/fabric\/datasources\/([^/]+)\/refresh$/, (m, b) => write('refreshDatasource', { ...b, name: m[1] })],
    ['POST', /^\/fabric\/virtual-nodes$/, (m, b) => write('createVirtualNode', b)],
    ['DELETE', /^\/fabric\/virtual-nodes\/([^/]+)$/, (m, b) => write('dropVirtualNode', { ...b, label: m[1] })],
    ['POST', /^\/fabric\/virtual-relationships$/, (m, b) => write('createVirtualRelationship', b)],
    ['DELETE', /^\/fabric\/virtual-relationships\/([^/]+)$/, (m, b) => write('dropVirtualRelationship', { ...b, name: m[1] })],
  ]

  function readBody(req) {
    return new Promise((resolve, reject) => {
      let s = ''
      req.on('data', (c) => { s += c; if (s.length > 1e5) reject(bad('body too large', 413)) })
      req.on('end', () => { try { resolve(s ? JSON.parse(s) : {}) } catch { reject(bad('JSON body expected')) } })
      req.on('error', reject)
    })
  }

  return async function handle(req, res, subpath) {
    const u = new URL(subpath, 'http://bridge')
    const send = (code, body) => { res.writeHead(code, { 'content-type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(body)) }
    const fail = (e) => send(e.status || 502, { error: String(e.message || e), ...(e.statement ? { statement: e.statement } : {}) })
    if (req.method === 'GET') {
      for (const [re, fn] of GET) {
        const m = u.pathname.match(re)
        if (!m) continue
        try { return send(200, await fn(m.map(decodeURIComponent), u)) } catch (e) { return fail(e) }
      }
      return send(404, { error: `no route ${u.pathname}` })
    }
    for (const [method, re, fn] of WRITE) {
      const m = u.pathname.match(re)
      if (!m || method !== req.method) continue
      try {
        const body = await readBody(req)
        if (u.searchParams.get('graph') && !body.graph) body.graph = u.searchParams.get('graph')
        return send(200, await fn(m.map(decodeURIComponent), body))
      } catch (e) { return fail(e) }
    }
    send(501, { status: 'error', type: 'error', error: '이 패키지에서는 원천 DB에 임의 SQL을 보내지 않습니다. Ontological 데이터 패브릭의 가상 노드(Cypher)로 조회하세요.' })
  }
}

module.exports = { createBridge, plain }
