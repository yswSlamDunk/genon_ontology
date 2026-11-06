'use strict'
// Natural language → Cypher for the Ontological portal's query box.
//
// The portal tab asks over IPC (preload: liteShell.nl2cypher). The schema of the graph it has
// selected comes from the portal's own management API (/api/schema → og_schema), the question
// goes to the CLI agent this app runs (cliagents: Claude Code or Codex, one turn, no tools —
// resources/agent_turn.py, the same call Studio's dashboards make), and the query that comes back
// is tried on the graph over Bolt before the portal runs it. A query that fails gets one repair
// turn with the engine's message. Write clauses are never tried: they come back for a person to run.
const FUNCTIONS = 'count, sum, avg, min, max, collect, id, elementId, labels, type, length, size, toUpper, toLower, trim, ' +
  'substring, replace, split, coalesce, abs, ceil, floor, round, sqrt, rand, toString, toInteger, toFloat, timestamp, ' +
  'datetime, exists, keys'
const WRITE = /\b(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|REFRESH|ALTER|GRANT|REVOKE|LOAD|FOREACH)\b/i
const INTERNAL_TYPE = /^_/ // Studio's registry (_OntologyModel …) and the _Entity root
const INTERNAL_PROP = new Set(['_source_id', '_parent_source_id', 'created_at', 'updated_at', 'embedding'])

function system(graph) {
  return [
    'You turn a question about a graph into ONE Cypher query for Ontological DB (a PostgreSQL-based graph database).',
    'Answer with the query in a single ```cypher code block, then one short line in Korean saying what it returns. Nothing else.',
    '',
    `Graph: ${graph}. Use only the node labels, relationship types, directions and property names in the schema below.`,
    'Ontological speaks a subset of Cypher. Stay inside it:',
    '- Clauses: MATCH, OPTIONAL MATCH, WHERE, WITH, RETURN, ORDER BY, SKIP, LIMIT, UNWIND, DISTINCT, aggregates.',
    `- Functions: ${FUNCTIONS}. Nothing else — no head(), last(), nodes(), list or pattern comprehensions, CASE, APOC or db.* procedures.`,
    '- Give EVERY node in a pattern its label: (po:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier). A relationship in this',
    '  schema may be a join on keys between two tables; it only works when both ends are labelled.',
    '- Follow each relationship from its `from` type to its `to` type as the schema says.',
    '- Put labels in the pattern (MATCH (n:Supplier)), never as a predicate in WHERE (no `WHERE n:Label`, no `NOT n:Label`).',
    '- String matching: =, <>, STARTS WITH, ENDS WITH, CONTAINS. Text values are case-sensitive; codes look like the examples in the schema.',
    '- Read only: never CREATE, MERGE, SET, DELETE or REMOVE unless the question explicitly asks to change data.',
    '- Return named columns (RETURN s.name AS supplier, …), not whole nodes, unless the question asks to see the nodes or a graph.',
    '- Add LIMIT 100 when the result could be large.',
  ].join('\n')
}

function compactSchema(s) {
  const types = (s.entity_types || []).filter((t) => !INTERNAL_TYPE.test(t.name)).map((t) => ({
    label: t.name,
    ...(t.extends && t.extends.filter((x) => !INTERNAL_TYPE.test(x)).length ? { extends: t.extends.filter((x) => !INTERNAL_TYPE.test(x)) } : {}),
    properties: (t.properties || []).filter((p) => !INTERNAL_PROP.has(p.name)).map((p) => `${p.name}:${p.type}`),
  }))
  const rels = (s.relationship_types || s.relation_types || []).filter((r) => !INTERNAL_TYPE.test(r.name || r.type || '')).map((r) => {
    const roles = Array.isArray(r.roles) ? r.roles : []
    const end = (k) => (roles.find((x) => x && (x.role === k || x.name === k)) || {}).type
    const from = end('from') || end('source') || r.from
    const to = end('to') || end('target') || r.to
    return { type: r.name || r.type, ...(from ? { from } : {}), ...(to ? { to } : {}) }
  })
  return { node_types: types, relationship_types: rels }
}

function extractCypher(text) {
  const block = String(text).match(/```(?:cypher|sql)?\s*\n([\s\S]*?)```/i)
  const q = (block ? block[1] : String(text)).trim().replace(/;\s*$/, '')
  const note = block ? String(text).slice(String(text).indexOf(block[0]) + block[0].length).trim().split('\n')[0].trim() : ''
  return { cypher: q, note }
}

/**
 * @param req   { question, graph }
 * @param ctx   { ports, driver(), agent(), runAgent(system, user) → text }
 */
async function translate(req, ctx) {
  const question = String(req && req.question || '').trim()
  const graph = String(req && req.graph || '').trim()
  if (!question) throw new Error('질문이 비어 있습니다.')
  if (!/^[a-z_][a-z0-9_]*$/i.test(graph)) throw new Error('그래프를 고르세요.')
  const agent = ctx.agent()
  if (!agent || agent.backend !== 'cliagents') {
    throw new Error('자연어 → Cypher 는 CLI 에이전트(Claude Code · Codex)로 동작합니다. 메뉴 「런타임 › 에이전트」에서 고르세요.')
  }
  const t0 = Date.now()
  const r = await fetch(`http://127.0.0.1:${ctx.ports.portal}/api/schema?graph=${encodeURIComponent(graph)}`)
  if (!r.ok) throw new Error(`그래프 ${graph} 의 스키마를 읽지 못했습니다 (${r.status})`)
  const schema = compactSchema((await r.json()).schema || {})
  if (!schema.node_types.length) throw new Error(`그래프 ${graph} 에 노드 타입이 없습니다.`)
  await addEnds(ctx.driver(), graph, schema)
  const sys = system(graph)
  const user = `Schema (JSON):\n${JSON.stringify(schema)}\n\nQuestion: ${question}`

  let { cypher, note } = extractCypher(await ctx.runAgent(sys, user))
  if (!cypher) throw new Error('에이전트가 Cypher 를 내지 못했습니다.')
  const write = WRITE.test(cypher.replace(/'[^']*'|"[^"]*"/g, ''))
  let repaired = false
  let checked = false
  if (!write) {
    let err = await tryRead(ctx.driver(), graph, cypher)
    if (err) {
      ;({ cypher, note } = extractCypher(await ctx.runAgent(sys,
        `${user}\n\nThis query failed on Ontological:\n${cypher}\nError: ${err}\nFix it. Same answer format.`)))
      repaired = true
      err = await tryRead(ctx.driver(), graph, cypher)
      if (err) return { cypher, note, agent: agent.label, ms: Date.now() - t0, repaired, checked: false, error: err }
    }
    checked = true
  }
  return { cypher, note, agent: agent.label, ms: Date.now() - t0, repaired, checked, write }
}

/**
 * The schema API leaves the ends of a virtual relationship empty (it is a join, not stored
 * edges): the fabric says them (SHOW VIRTUAL …, a fabric statement over Bolt). A stored
 * relationship without declared ends is looked up on one edge. Virtual node types say where
 * they read from, so the agent knows a type is another system's table.
 */
async function addEnds(driver, graph, schema) {
  const s = driver.session({ database: graph })
  try {
    const rows = async (q) => { try { return (await s.run(q)).records.map((x) => x.toObject()) } catch { return [] } }
    const vrels = new Map((await rows(`SHOW VIRTUAL RELATIONSHIPS IN ${graph}`)).map((v) => [v.relationship, v]))
    for (const v of await rows(`SHOW VIRTUAL NODES IN ${graph}`)) {
      const t = schema.node_types.find((x) => x.label === v.node)
      if (t) t.source = String(v.source)
    }
    for (const r of schema.relationship_types) {
      const v = vrels.get(r.type)
      if (v) {
        const [fromType] = String(v.from).split('.'), [toType] = String(v.to).split('.')
        Object.assign(r, { from: fromType, to: toType, join: `${v.from} = ${v.to}` })
      } else if (!r.from || !r.to) {
        const e = (await rows(`MATCH (a)-[r:\`${r.type.replace(/`/g, '')}\`]->(b) RETURN labels(a) AS a, labels(b) AS b LIMIT 1`))[0]
        const pick = (ls) => (ls || []).find((l) => !INTERNAL_TYPE.test(l))
        if (e) Object.assign(r, { from: pick(e.a), to: pick(e.b) })
      }
    }
  } finally { await s.close().catch(() => {}) }
}

/** Runs a read query once over Bolt (rows discarded). Returns the engine's message, or null. */
async function tryRead(driver, graph, cypher) {
  const s = driver.session({ database: graph, defaultAccessMode: 'READ' })
  try {
    const run = s.run(cypher).then(() => null)
    // a query still running after 20 s did compile; the portal will show its result
    return await Promise.race([run, new Promise((resolve) => setTimeout(() => resolve(null), 20000))])
  } catch (e) {
    return String(e.message || e).replace(/^.*?(ERROR:\s*)/s, '').slice(0, 400)
  } finally {
    s.close().catch(() => {})
  }
}

module.exports = { translate, compactSchema, extractCypher }
