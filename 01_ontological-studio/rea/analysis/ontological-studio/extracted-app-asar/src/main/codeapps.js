'use strict'
// Code apps — an ontology app written as code by the CLI coding agent (cliagents: Claude Code
// or Codex), the way ainaru-portal's QuickApp has OpenHands write one. The app is a folder of
// static files (no build): Vue and ECharts come from resources/codeapp/runtime, data comes from
// the ontology through og.js → POST /codeapps/api/query, a read-only Cypher endpoint over Bolt.
//
//   <userData>/codeapps/<id>/            the app (index.html · app.js · style.css …)
//   <userData>/codeapps/<id>/.app.json   name, prompt, turns, agent session id
//
//   /codeapps/api/apps            GET list · POST create {name, text, resources}
//   /codeapps/api/apps/<id>       GET (meta + files) · DELETE
//   /codeapps/api/apps/<id>/turns POST {text, resources} — starts the agent
//   /codeapps/api/apps/<id>/events?from=n   SSE: the running (or last) turn's events
//   /codeapps/api/apps/<id>/file?path=      source of one file
//   /codeapps/api/query           POST {cypher, params} → {columns, rows}
//   /codeapps/api/schema          GET classes · properties · relationships
//   /codeapps/api/act/*           the ontology's actions, through Studio's action proxy (/api/act/*):
//                                 actions · plans · plans/by-ids · plan · approve · execute · run · compensate.
//                                 og.js act() renders the plan → approval → result → 취소 dialog.
//   /apps/_runtime/*              og.js · og.css · vue.js · echarts.min.js
//   /apps/<id>/*                  the app itself (preview iframe and app tabs)
const fs = require('fs')
const path = require('path')
const crypto = require('crypto')
const neo4j = require('neo4j-driver')

const META = '.app.json'
const HIDDEN = new Set([META, 'CLAUDE.md', 'AGENTS.md'])
const SYSTEM_PROPS = new Set(['_id', '_type', '_source_id', '_parent_source_id', 'created_at', 'updated_at', 'embedding'])
const MAX_ROWS = 5000
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png' }

// ── read-only Cypher ─────────────────────────────────────────────────
// Writing clauses are refused before the query reaches the engine; string literals and comments
// are blanked first so a value such as 'SET' does not count.
const WRITE = /\b(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|FOREACH|LOAD\s+CSV)\b|\bCALL\s+(dbms|og_|apoc\.(create|merge|refactor|periodic))/i
function isWrite(cypher) {
  const bare = String(cypher)
    .replace(/\/\/[^\n]*/g, ' ').replace(/\/\*[\s\S]*?\*\//g, ' ')
    .replace(/'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`[^`]*`/g, "''")
  return WRITE.test(bare)
}

/** Bolt values → plain JSON: integers as numbers, nodes as their properties (+ _labels, _id). */
function plain(v) {
  if (v === null || v === undefined) return null
  if (neo4j.isInt(v)) return v.inSafeRange() ? v.toNumber() : v.toString()
  if (Array.isArray(v)) return v.map(plain)
  if (v instanceof neo4j.types.Node) {
    const out = {}
    for (const [k, x] of Object.entries(v.properties)) if (!SYSTEM_PROPS.has(k)) out[k] = plain(x)
    out._labels = v.labels.filter((l) => !l.startsWith('_'))
    out._id = v.elementId
    return out
  }
  if (v instanceof neo4j.types.Relationship) return { ...plain(v.properties), _type: v.type, _id: v.elementId }
  if (v instanceof neo4j.types.Path) return v.segments.map((s) => ({ start: plain(s.start), rel: plain(s.relationship), end: plain(s.end) }))
  if (typeof v === 'object' && typeof v.toString === 'function' && v.constructor && v.constructor.name !== 'Object') {
    // temporal and spatial values
    return v.toString()
  }
  if (typeof v === 'object') { const o = {}; for (const [k, x] of Object.entries(v)) o[k] = plain(x); return o }
  return v
}

function createCodeApps({ dir, driver, graph, runtimeDir, templateDir, rulesFile, spawnTurn, webPort, backendPort, log }) {
  fs.mkdirSync(dir, { recursive: true })
  const running = new Map() // id → { events: [], done, listeners: Set, child }

  const appDir = (id) => path.join(dir, id)
  const validId = (id) => /^[a-z0-9-]{4,64}$/.test(id) && fs.existsSync(path.join(appDir(id), META))
  const readMeta = (id) => JSON.parse(fs.readFileSync(path.join(appDir(id), META), 'utf8'))
  const writeMeta = (id, m) => fs.writeFileSync(path.join(appDir(id), META), JSON.stringify(m, null, 2))

  function files(id) {
    const root = appDir(id)
    const out = []
    const walk = (d) => {
      for (const e of fs.readdirSync(d, { withFileTypes: true })) {
        if (e.name.startsWith('.') || HIDDEN.has(e.name)) continue
        const p = path.join(d, e.name)
        if (e.isDirectory()) walk(p)
        else out.push({ path: path.relative(root, p).split(path.sep).join('/'), size: fs.statSync(p).size })
      }
    }
    walk(root)
    return out.sort((a, b) => a.path.localeCompare(b.path))
  }

  async function read(cypher, params = {}) {
    const s = driver().session({ database: graph, defaultAccessMode: neo4j.session.READ })
    try {
      const r = await s.run(cypher, params)
      return { columns: r.records.length ? r.records[0].keys : [], rows: r.records.slice(0, MAX_ROWS).map((rec) => plain(rec.toObject())) }
    } finally { await s.close().catch(() => {}) }
  }

  /** Classes (properties, count, one example), relationships with their ends — for the agent's prompt and og.schema(). */
  async function schema() {
    const labels = (await read('CALL db.labels() YIELD label RETURN label')).rows.map((r) => r.label).filter((l) => !l.startsWith('_'))
    const classes = []
    for (const label of labels) {
      const q = '`' + label.replace(/`/g, '') + '`'
      const [one, n] = await Promise.all([
        read(`MATCH (n:${q}) WITH n LIMIT 1 RETURN n`).catch(() => ({ rows: [] })),
        read(`MATCH (n:${q}) RETURN count(n) AS c`).catch(() => ({ rows: [{ c: null }] })),
      ])
      const example = one.rows[0] ? one.rows[0].n : null
      const properties = example ? Object.keys(example).filter((k) => !k.startsWith('_')) : []
      classes.push({ name: label, count: n.rows[0] ? n.rows[0].c : null, properties, example })
    }
    const rels = (await read('MATCH (a)-[r]->(b) RETURN DISTINCT labels(a) AS a, type(r) AS t, labels(b) AS b LIMIT 200').catch(() => ({ rows: [] }))).rows
      .map((r) => ({ from: (r.a || []).find((l) => !l.startsWith('_')), type: r.t, to: (r.b || []).find((l) => !l.startsWith('_')) }))
      .filter((r) => r.from && r.to)
    const desc = {}
    for (const r of (await read('MATCH (r:_OntologyRelationship) RETURN r.name AS name, r.from_class AS f, r.to_class AS t, r.description AS d').catch(() => ({ rows: [] }))).rows) {
      desc[`${r.f}|${r.name}|${r.t}`] = r.d
    }
    for (const r of rels) r.description = desc[`${r.from}|${r.type}|${r.to}`] || ''
    return { graph, classes, relationships: rels }
  }

  function schemaBlock(s, mentioned) {
    const lines = []
    for (const c of s.classes) {
      const ex = c.example ? Object.fromEntries(Object.entries(c.example).filter(([k]) => !k.startsWith('_')).slice(0, 8)) : null
      lines.push(`- ${c.name}${mentioned.has(c.name) ? ' ★' : ''} (${c.count ?? '?'}건) 속성: ${c.properties.join(', ')}`
        + (ex ? `\n    예: ${JSON.stringify(ex)}` : ''))
    }
    lines.push('', '관계:')
    for (const r of s.relationships) lines.push(`- (:${r.from})-[:${r.type}]->(:${r.to})${r.description ? ` — ${r.description}` : ''}`)
    return lines.join('\n')
  }

  function resourceBlock(resources) {
    if (!resources || !resources.length) return ''
    const lines = ['', '## 사람이 고른 자원 (★) — 재검토하지 말고 실제로 쓰세요']
    for (const r of resources) {
      const m = /^(class|prop|widget):(.*)$/.exec(r.ref || '')
      if (!m) continue
      if (m[1] === 'class') lines.push(`- 클래스 ${m[2].split('/').pop()}`)
      else if (m[1] === 'prop') lines.push(`- 속성 ${m[2].split('/').pop()}`)
    }
    return lines.length > 1 ? lines.join('\n') + '\n' : ''
  }

  const mentionedClasses = (resources) => new Set((resources || []).map((r) => {
    const m = /^(class|prop):[^/]*\/([^.]+)/.exec(r.ref || '')
    return m ? m[2] : null
  }).filter(Boolean))

  // ── actions (kinetic) ────────────────────────────────────────────────
  // An app never reaches a business system itself. It asks Studio's action proxy — the same path as
  // the chat's plan card: plan (dry-run, policy per target) → a person's approval → execute →
  // compensate. Only the routes below pass; approve · execute · compensate also need a browser's
  // fetch (Sec-Fetch-Mode), so the coding agent's curl can look at actions and plans but not run them.
  const ACT = [
    ['GET', /^\/act\/health$/, () => '/api/act/health', false],
    ['GET', /^\/act\/actions$/, (u) => `/api/act/actions${u.searchParams.get('class') ? `?class_name=${encodeURIComponent(u.searchParams.get('class'))}` : ''}`, false],
    ['POST', /^\/act\/plans$/, () => '/api/act/plans', false],
    ['POST', /^\/act\/plans\/by-ids$/, () => '/api/act/plans/by-ids', false],
    ['GET', /^\/act\/plans\/([\w-]+)$/, (u, m) => `/api/act/plans/${m[1]}`, false],
    ['POST', /^\/act\/plans\/([\w-]+)\/approve$/, (u, m) => `/api/act/plans/${m[1]}/approve`, true],
    ['POST', /^\/act\/plans\/([\w-]+)\/execute$/, (u, m) => `/api/act/plans/${m[1]}/execute`, true],
    ['GET', /^\/act\/runs\/([\w-]+)$/, (u, m) => `/api/act/runs/${m[1]}`, false],
    ['POST', /^\/act\/runs\/([\w-]+)\/compensate$/, (u, m) => `/api/act/runs/${m[1]}/compensate`, true],
  ]

  /** Adds each action's golden command (the build brief's sentence it realizes) from Studio's definitions. */
  async function withGolden(list) {
    const golden = {}
    for (const cls of [...new Set(list.map((a) => a.class))]) {
      try {
        const r = await fetch(`http://127.0.0.1:${backendPort}/api/schema/classes/${encodeURIComponent(cls)}/actions`)
        for (const d of ((r.ok && (await r.json()).actions) || [])) if (d.golden_command) golden[`${d.class}.${d.name}`] = d.golden_command
      } catch { /* 정의를 못 읽어도 액션은 쓴다 */ }
    }
    return list.map((a) => ({ ...a, golden_command: golden[`${a.class}.${a.action}`] || '' }))
  }

  async function act(req, res, url) {
    if (url.pathname === '/act/actions' && req.method === 'GET') {
      const cls = url.searchParams.get('class') || ''
      return json(res, 200, (await actionList()).filter((a) => !cls || a.class === cls))
    }
    for (const [method, re, to, person] of ACT) {
      const m = re.exec(url.pathname)
      if (!m || req.method !== method) continue
      if (person && !req.headers['sec-fetch-mode']) return json(res, 403, { error: '승인·실행·취소는 앱 화면에서 사람이 눌러야 합니다.' })
      if (!backendPort) return json(res, 503, { error: '액션 실행기에 연결되지 않았습니다.' })
      const init = { method, headers: { 'content-type': 'application/json' } }
      if (method === 'POST') init.body = JSON.stringify(await body(req))
      try {
        const r = await fetch(`http://127.0.0.1:${backendPort}${to(url, m)}`, init)
        res.writeHead(r.status, { 'content-type': r.headers.get('content-type') || 'application/json; charset=utf-8' })
        return res.end(await r.text())
      } catch (e) {
        return json(res, 502, { error: `액션 실행기에 닿지 못했습니다: ${e.message}` })
      }
    }
    return json(res, 404, { error: '없는 액션 경로입니다.' })
  }

  /** Published actions, for the agent's prompt (empty when the action layer is off). */
  async function actionList() {
    if (!backendPort) return []
    try {
      const r = await fetch(`http://127.0.0.1:${backendPort}/api/act/actions`)
      return r.ok ? await withGolden(await r.json()) : []
    } catch { return [] }
  }

  function actionBlock(list) {
    if (!list.length) return ''
    const lines = ['', '## 이 온톨로지의 액션 — 앱에 버튼으로 연결할 수 있다 (CLAUDE.md 「액션」)']
    for (const a of list) {
      const ps = Object.entries((a.parameters && a.parameters.properties) || {})
        .map(([k, v]) => `${k}${((a.parameters.required || []).includes(k)) ? '*' : ''}(${v.description || v.type || ''})`)
      lines.push(`- ${a.class}.${a.action} — ${a.description}\n    대상 키: ${a.key_property} · 입력: ${ps.join(', ') || '없음'}`
        + (a.golden_command ? `\n    골든 커맨드: “${a.golden_command}”` : ''))
    }
    return lines.join('\n') + '\n'
  }

  async function create({ name, text, resources }) {
    const id = `app-${crypto.randomBytes(4).toString('hex')}`
    const root = appDir(id)
    fs.mkdirSync(root, { recursive: true })
    for (const f of fs.readdirSync(templateDir)) fs.copyFileSync(path.join(templateDir, f), path.join(root, f))
    const rules = fs.readFileSync(rulesFile, 'utf8').replace(/\{\{QUERY_URL\}\}/g, `http://127.0.0.1:${webPort}/codeapps/api/query`)
      .replace(/\{\{ACTIONS_URL\}\}/g, `http://127.0.0.1:${webPort}/codeapps/api/act/actions`)
    fs.writeFileSync(path.join(root, 'CLAUDE.md'), rules)   // Claude Code reads it from the working folder
    fs.writeFileSync(path.join(root, 'AGENTS.md'), rules)   // Codex too
    const now = new Date().toISOString()
    const title = (name || '').trim() || (text || '').replace(/@/g, '').trim().slice(0, 28) || '새 앱'
    writeMeta(id, { id, name: title, prompt: text, resources: resources || [], created_at: now, updated_at: now,
                    session_id: crypto.randomUUID(), turns: [] })
    return { id, name: title }
  }

  function startTurn(id, { text, resources }) {
    if (running.get(id) && !running.get(id).done) throw Object.assign(new Error('에이전트가 아직 일하는 중입니다.'), { status: 409 })
    const meta = readMeta(id)
    const first = meta.turns.length === 0
    return Promise.all([schema().catch((e) => ({ classes: [], relationships: [], error: e.message })), actionList()]).then(([s, actions]) => {
      const prompt = first
        ? [`# 만들 앱: ${meta.name}`, '', '## 사람의 요청', text, resourceBlock(resources),
           '## 발행된 온톨로지 (그래프 ' + graph + ')', schemaBlock(s, mentionedClasses(resources)), actionBlock(actions), '',
           '규칙은 이 폴더의 CLAUDE.md(AGENTS.md)에 있습니다. 질의를 curl 로 시험한 뒤 index.html · app.js · style.css 를 완성하세요. 진행 설명과 보고는 한국어로 씁니다.'].join('\n')
        : [text, resourceBlock(resources), '', '(같은 앱을 고칩니다. 바뀐 질의는 curl 로 다시 시험하세요. 말과 보고는 한국어로.)'].join('\n')
      const turn = { text, resources: resources || [], started_at: new Date().toISOString(), events: [], done: false, listeners: new Set() }
      running.set(id, turn)
      const push = (ev) => {
        turn.events.push(ev)
        for (const fn of turn.listeners) fn(ev)
      }
      push({ kind: 'user', text, resources: resources || [] })
      const child = spawnTurn()
      turn.child = child
      let buf = ''
      child.stdout.setEncoding('utf8')
      child.stdout.on('data', (chunk) => {
        buf += chunk
        let i
        while ((i = buf.indexOf('\n')) >= 0) {
          const line = buf.slice(0, i); buf = buf.slice(i + 1)
          if (!line.trim()) continue
          try {
            const ev = JSON.parse(line)
            if (ev.kind === 'token' && !ev.text) continue
            push(ev)
          } catch { /* not ours */ }
        }
      })
      let stderr = ''
      child.stderr.on('data', (d) => { stderr = (stderr + d).slice(-2000) })
      child.on('close', (code) => {
        const final = [...turn.events].reverse().find((e) => e.kind === 'final')
        if (code !== 0 && !turn.events.some((e) => e.kind === 'error')) push({ kind: 'error', message: `에이전트 실행이 끝나지 못했습니다 (exit ${code}) ${stderr.slice(-300)}` })
        const m = readMeta(id)
        m.turns.push({ text, resources: resources || [], started_at: turn.started_at, finished_at: new Date().toISOString(),
                       ok: code === 0, report: final ? final.text : '', events: turn.events.filter((e) => e.kind !== 'token' || e.text).slice(-400) })
        m.updated_at = new Date().toISOString()
        writeMeta(id, m)
        turn.done = true
        push({ kind: 'done', ok: code === 0 })
        log(`code app ${id}: turn ${m.turns.length} ${code === 0 ? 'ok' : 'failed'} (${Math.round((Date.now() - Date.parse(turn.started_at)) / 1000)} s)`)
      })
      child.stdin.end(JSON.stringify({ prompt, cwd: appDir(id), session_id: meta.session_id, resume: !first }))
      return { started: true }
    })
  }

  // ── HTTP ─────────────────────────────────────────────────────────────
  const json = (res, code, body) => { res.writeHead(code, { 'content-type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(body)) }
  const body = (req) => new Promise((resolve) => {
    let s = ''
    req.on('data', (d) => { s += d; if (s.length > 1 << 20) req.destroy() })
    req.on('end', () => { try { resolve(s ? JSON.parse(s) : {}) } catch { resolve({}) } })
  })

  function events(req, res, id, from) {
    res.writeHead(200, { 'content-type': 'text/event-stream; charset=utf-8', 'cache-control': 'no-cache', connection: 'keep-alive' })
    const send = (ev) => res.write(`data: ${JSON.stringify(ev)}\n\n`)
    const turn = running.get(id)
    if (!turn) {
      // nothing in memory (the app was restarted): replay the last stored turn
      const last = readMeta(id).turns.slice(-1)[0]
      if (last) { send({ kind: 'user', text: last.text, resources: last.resources }); for (const e of last.events) send(e) }
      send({ kind: 'done', ok: last ? last.ok : true, replay: true })
      return res.end()
    }
    for (const e of turn.events.slice(from)) send(e)
    if (turn.done) return res.end()
    const fn = (ev) => { send(ev); if (ev.kind === 'done') res.end() }
    turn.listeners.add(fn)
    const ping = setInterval(() => res.write(': ping\n\n'), 15000)
    req.on('close', () => { turn.listeners.delete(fn); clearInterval(ping) })
  }

  async function handle(req, res, u) {
    const url = new URL(u, 'http://x')
    const parts = url.pathname.split('/').filter(Boolean) // ['apps', id, 'turns'] …
    try {
      if (url.pathname === '/query' && req.method === 'POST') {
        const { cypher, params } = await body(req)
        if (!cypher || typeof cypher !== 'string') return json(res, 400, { error: 'cypher 가 없습니다.' })
        if (isWrite(cypher)) return json(res, 403, { error: '읽기 전용입니다 — CREATE·MERGE·SET·DELETE 같은 쓰기 절은 쓸 수 없습니다.' })
        try { return json(res, 200, await read(cypher, params || {})) } catch (e) { return json(res, 400, { error: String(e.message || e).replace(/^.*?ERROR:\s*/s, '').slice(0, 600) }) }
      }
      if (url.pathname === '/schema') return json(res, 200, await schema())
      if (url.pathname.startsWith('/act/')) return act(req, res, url)
      if (parts[0] !== 'apps') return json(res, 404, { error: 'not found' })
      if (parts.length === 1) {
        if (req.method === 'POST') {
          const b = await body(req)
          return json(res, 200, await create({ name: b.name, text: b.text, resources: b.resources }))
        }
        const list = fs.readdirSync(dir).filter(validId).map((id) => {
          const m = readMeta(id)
          const t = running.get(id)
          return { id, name: m.name, updated_at: m.updated_at, turns: m.turns.length, running: !!(t && !t.done), ok: m.turns.length ? m.turns[m.turns.length - 1].ok : null }
        }).sort((a, b) => String(b.updated_at).localeCompare(String(a.updated_at)))
        return json(res, 200, { apps: list })
      }
      const id = parts[1]
      if (!validId(id)) return json(res, 404, { error: '그 앱이 없습니다.' })
      if (parts.length === 2) {
        if (req.method === 'DELETE') {
          const t = running.get(id); if (t && t.child && !t.done) t.child.kill()
          running.delete(id)
          fs.rmSync(appDir(id), { recursive: true, force: true })
          return json(res, 200, { deleted: true })
        }
        const m = readMeta(id)
        const t = running.get(id)
        return json(res, 200, { ...m, turns: m.turns.map((x) => ({ text: x.text, resources: x.resources, ok: x.ok, report: x.report, started_at: x.started_at, finished_at: x.finished_at })),
                                running: !!(t && !t.done), files: files(id), url: `/apps/${id}/` })
      }
      if (parts[2] === 'turns' && req.method === 'POST') {
        const b = await body(req)
        if (!b.text || !String(b.text).trim()) return json(res, 400, { error: '무엇을 만들지 적어 주세요.' })
        return json(res, 200, await startTurn(id, { text: String(b.text), resources: b.resources || [] }))
      }
      if (parts[2] === 'events') return events(req, res, id, Number(url.searchParams.get('from') || 0))
      if (parts[2] === 'file') {
        const rel = url.searchParams.get('path') || ''
        const file = path.join(appDir(id), path.normalize(rel).replace(/^(\.\.[/\\])+/, ''))
        if (!file.startsWith(appDir(id) + path.sep) || HIDDEN.has(path.basename(file)) || !fs.existsSync(file)) return json(res, 404, { error: '그 파일이 없습니다.' })
        return json(res, 200, { path: rel, text: fs.readFileSync(file, 'utf8').slice(0, 400000) })
      }
      return json(res, 404, { error: 'not found' })
    } catch (e) {
      return json(res, e.status || 500, { error: e.message })
    }
  }

  /** /apps/_runtime/* and /apps/<id>/* — static, never cached (the agent rewrites files). */
  function serve(req, res, u) {
    const p = decodeURIComponent(new URL(u, 'http://x').pathname)
    const m = /^\/([^/]+)(\/.*)?$/.exec(p)
    if (!m) { res.writeHead(404); return res.end() }
    let root
    if (m[1] === '_runtime') root = runtimeDir
    else if (validId(m[1])) root = appDir(m[1])
    else { res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' }); return res.end('그 앱이 없습니다.') }
    if (!m[2]) { res.writeHead(302, { location: `/apps/${m[1]}/` }); return res.end() }
    let rel = m[2] === '/' ? '/index.html' : m[2]
    const file = path.join(root, path.normalize(rel).replace(/^(\.\.[/\\])+/, ''))
    if (!file.startsWith(root + path.sep) || HIDDEN.has(path.basename(file)) || path.basename(file).startsWith('.') || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' }); return res.end('없는 파일입니다.')
    }
    res.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream', 'cache-control': m[1] === '_runtime' ? 'max-age=3600' : 'no-store' })
    fs.createReadStream(file).pipe(res)
  }

  function stopAll() { for (const t of running.values()) if (t.child && !t.done) t.child.kill() }

  return { handle, serve, stopAll, schema, isWrite }
}

module.exports = { createCodeApps, isWrite }
