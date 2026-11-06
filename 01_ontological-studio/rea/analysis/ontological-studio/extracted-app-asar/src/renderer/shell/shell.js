'use strict'
// Shell page: the tab strip (in the title bar) and the home launcher.
// Tabs live in the main process (src/main/tabs.js); this page draws them and asks
// for changes through window.liteShell (preload). The home reads the same /api the
// Studio tabs use — this page is served from the same origin.
const S = window.liteShell

const ICONS = {
  home: '<path d="M4 10.5L12 4l8 6.5"/><path d="M6.5 9v10.5h11V9"/><path d="M10 19.5v-5h4v5"/>',
  build: '<circle cx="6" cy="6" r="2.4"/><circle cx="18" cy="6" r="2.4"/><circle cx="12" cy="18" r="2.4"/><path d="M8.4 6h7.2M7.1 8.1l3.8 7.8M16.9 8.1l-3.8 7.8"/>',
  act: '<path d="M20 14.5a2 2 0 0 1-2 2H9l-5 4V5.5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2z"/><path d="M8.5 8.5h7M8.5 12h4.5"/>',
  board: '<rect x="3.5" y="3.5" width="7" height="9" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="5" rx="1.5"/><rect x="13.5" y="11.5" width="7" height="9" rx="1.5"/><rect x="3.5" y="15.5" width="7" height="5" rx="1.5"/>',
  quality: '<path d="M12 3l7 3v5.2c0 4.4-2.9 8.1-7 9.8-4.1-1.7-7-5.4-7-9.8V6z"/><path d="M9 12l2.2 2.2L15.5 10"/>',
  datasources: '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/><path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>',
  systems: '<path d="M9 2.5v5M15 2.5v5"/><path d="M6.5 7.5h11v3.5a5.5 5.5 0 0 1-11 0z"/><path d="M12 16.5v5"/>',
  browser: '<rect x="3" y="4" width="18" height="16" rx="2.2"/><path d="M7 9.5l3 2.5-3 2.5M12.5 15h4.5"/>',
  node: '<circle cx="12" cy="12" r="6.5"/><circle cx="12" cy="12" r="2"/>',
  gear: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3H9a1.6 1.6 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V9a1.6 1.6 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z"/>',
  clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  close: '<path d="M6 6l12 12M18 6L6 18"/>',
  window: '<rect x="3.5" y="5" width="17" height="14" rx="2"/><path d="M3.5 9h17"/><path d="M14 13.5h3.5M15.75 11.75v3.5"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/>',
  moon: '<path d="M20 14.2A8 8 0 0 1 9.8 4a8 8 0 1 0 10.2 10.2z"/>',
  search: '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
  arrow: '<path d="M7 17L17 7M9 7h8v8"/>',
  folder: '<path d="M3.5 7.5a2 2 0 0 1 2-2h4l2 2.5h7a2 2 0 0 1 2 2v7.5a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>',
  logs: '<path d="M6 3.5h8.5L19 8v12.5H6z"/><path d="M14 3.5V8h5M9 12h7M9 15.5h7M9 19h4"/>',
  dot: '<circle cx="12" cy="12" r="2.5"/>',
}
const icon = (n, cls = 'ic') => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${ICONS[n] || ICONS.dot}</svg>`
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c])
const $ = (id) => document.getElementById(id)

const C = { teal: '#18b6a0', blue: '#4c8bf5', amber: '#e0a33e', violet: '#8d8ff5', pink: '#e06c9f', green: '#3fbf86', slate: '#93a1b3' }
const VIEW_LABEL = { build: '온톨로지 구축', act: '질의·액션', board: '대시보드', quality: '품질 검수', datasources: '데이터소스', systems: '시스템 등록', browser: 'Ontological Portal' }
const LABEL_VIEW = Object.fromEntries(Object.entries(VIEW_LABEL).map(([k, v]) => [v, k]))

const CARDS = [
  { title: '온톨로지 구축', desc: '문서와 데이터소스에서 클래스·관계를 만듭니다.', icon: 'build', c: 'teal', target: { kind: 'studio', view: 'build' }, llm: true },
  { title: '질의·액션', desc: '온톨로지에 묻고, 지시하면 액션을 계획·실행합니다.', icon: 'act', c: 'blue', target: { kind: 'studio', view: 'act' }, llm: true },
  { title: '데이터소스', desc: '원천 DB 를 연결하고 가상 노드로 노출합니다.', icon: 'datasources', c: 'amber', target: { kind: 'studio', view: 'datasources' } },
  { title: 'Ontological Portal', desc: 'Cypher 콘솔 · 스키마 지도 · 시점 조회.', icon: 'browser', c: 'green', target: { kind: 'portal' } },
  { title: '온톨로지 앱', desc: '대시보드나 코드 앱을 말로 만듭니다.', icon: 'board', c: 'violet', target: { kind: 'studio', view: 'board' } },
  { title: '품질 검수', desc: '구축이 남긴, 사람이 판단할 것.', icon: 'quality', c: 'pink', target: { kind: 'studio', view: 'quality' } },
  { title: '시스템 등록', desc: '키네틱 액션이 부를 서비스.', icon: 'systems', c: 'slate', target: { kind: 'studio', view: 'systems' }, kinetic: true },
  { title: '설정', desc: 'studio.env — 에이전트 · LLM 키.', icon: 'gear', c: 'slate', action: 'settings' },
]
const FILTERS = [
  { key: 'all', label: '전체', side: '최근 항목', icon: 'clock' },
  { key: 'schema', label: '온톨로지', icon: 'node' },
  { key: 'session', label: '대화', icon: 'act' },
  { key: 'board', label: '앱', icon: 'board' },
  { key: 'datasource', label: '데이터소스', icon: 'datasources' },
]

let tabState = { active: 'home', tabs: [] }
let info = {}
let items = []
let filter = 'all'
let query = ''

// ── opening things ──
function openTarget(target) {
  if (S) S.openTab(target)
  else location.href = target.kind === 'portal' ? '/' : `/?${new URLSearchParams(target)}`
}

// ── tab strip ──
function tabIcon(t) {
  if (t.kind === 'portal') return 'browser'
  if (t.kind === 'app') return 'board'
  return LABEL_VIEW[t.title] || t.view || 'build'
}
function renderTabs() {
  const home = `<div class="tab home${tabState.active === 'home' ? ' active' : ''}" data-id="home" role="tab" title="홈 (⌘1)">${icon('home')}<span class="tab-title">홈</span></div>`
  const rest = tabState.tabs.map((t, i) => `
    <div class="tab${tabState.active === t.id ? ' active' : ''}" data-id="${t.id}" role="tab" title="${esc(t.title)}${i < 8 ? ` (⌘${i + 2})` : ''}">
      ${t.loading ? '<span class="spin"></span>' : icon(tabIcon(t))}
      <span class="tab-title">${esc(t.title)}</span>
      <button class="tab-x" data-close="${t.id}" title="닫기 (⌘W)">${icon('close')}</button>
    </div>`).join('')
  $('tabs').innerHTML = home + rest
  document.body.classList.toggle('at-home', tabState.active === 'home')
  document.title = tabState.active === 'home' ? 'Ontological Studio' : (tabState.tabs.find((t) => t.id === tabState.active)?.title || 'Ontology Studio Lite')
}
$('tabs').addEventListener('mousedown', (e) => {
  if (e.button !== 0 || e.target.closest('[data-close]')) return
  const tab = e.target.closest('.tab')
  if (tab && S) S.tabs.activate(tab.dataset.id)
})
$('tabs').addEventListener('click', (e) => {
  const x = e.target.closest('[data-close]')
  if (x && S) S.tabs.close(x.dataset.close)
})
$('tabs').addEventListener('auxclick', (e) => { // middle click closes, as in a browser
  const tab = e.target.closest('.tab')
  if (e.button === 1 && tab && tab.dataset.id !== 'home' && S) S.tabs.close(tab.dataset.id)
})
$('tabs').addEventListener('contextmenu', (e) => {
  const tab = e.target.closest('.tab')
  if (tab && tab.dataset.id !== 'home' && S) { e.preventDefault(); S.tabs.menu(tab.dataset.id) }
})
$('new-tab').innerHTML = icon('plus')
$('new-tab').addEventListener('click', () => S && S.tabs.activate('home'))
$('btn-window').innerHTML = icon('window')
$('btn-window').addEventListener('click', () => S && S.newWindow())

// ── theme (shared with Studio through localStorage 'os-theme') ──
function theme() { return document.documentElement.dataset.theme === 'light' ? 'light' : 'dark' }
function paintThemeButton() { $('btn-theme').innerHTML = icon(theme() === 'dark' ? 'sun' : 'moon') }
$('btn-theme').addEventListener('click', () => {
  const next = theme() === 'dark' ? 'light' : 'dark'
  document.documentElement.dataset.theme = next
  try { localStorage.setItem('os-theme', next) } catch {}
  paintThemeButton()
})
window.addEventListener('storage', (e) => {
  if (e.key === 'os-theme' && (e.newValue === 'light' || e.newValue === 'dark')) { document.documentElement.dataset.theme = e.newValue; paintThemeButton() }
})
paintThemeButton()

// ── home ──
function renderCards() {
  $('cards').innerHTML = CARDS.map((c, i) => {
    const badges = []
    if (c.llm && info.llmConfigured === false) badges.push('<span class="badge warn">에이전트 설정 필요</span>')
    if (c.kinetic && info.kineticConfigured === false) badges.push('<span class="badge">별도 서비스</span>')
    return `<button class="card" data-card="${i}" style="--c:${C[c.c]}">
      <span class="card-icon">${icon(c.icon)}</span>
      <span class="card-title">${esc(c.title)} ${badges.join('')}</span>
      <span class="card-desc">${esc(c.desc)}</span>
      <span class="card-go">${icon('arrow')}</span>
    </button>`
  }).join('')
}
$('cards').addEventListener('click', (e) => {
  const el = e.target.closest('[data-card]')
  if (!el) return
  const c = CARDS[Number(el.dataset.card)]
  if (c.action) S && S.open(c.action)
  else openTarget(c.target)
})

function renderSide() {
  const count = (k) => (k === 'all' ? items.length : items.filter((x) => x.type === k).length)
  $('side-nav').innerHTML = FILTERS.map((f) => `<button class="side-item${filter === f.key ? ' active' : ''}" data-filter="${f.key}">${icon(f.icon)}<span>${f.side || f.label}</span><span class="n">${count(f.key)}</span></button>`).join('')
  $('seg').innerHTML = FILTERS.map((f) => `<button class="${filter === f.key ? 'active' : ''}" data-filter="${f.key}">${f.label}</button>`).join('')
  $('side-quick').innerHTML = [
    ['portal', 'browser', 'Ontological Portal'],
    ['logs', 'logs', '로그 폴더'],
    ['data', 'folder', '데이터 폴더'],
  ].map(([k, ic, label]) => `<button class="side-item" data-quick="${k}">${icon(ic)}<span>${label}</span><span class="go">${icon('arrow')}</span></button>`).join('')
}
for (const id of ['side-nav', 'seg']) {
  $(id).addEventListener('click', (e) => {
    const b = e.target.closest('[data-filter]')
    if (b) { filter = b.dataset.filter; renderSide(); renderRows() }
  })
}
$('side-quick').addEventListener('click', (e) => {
  const b = e.target.closest('[data-quick]')
  if (!b || !S) return
  if (b.dataset.quick === 'portal') S.openTab({ kind: 'portal' })
  else S.open(b.dataset.quick)
})
$('search-icon').outerHTML = icon('search')
$('q').addEventListener('input', (e) => { query = e.target.value.trim().toLowerCase(); renderRows() })

function when(v) {
  if (v == null || v === '') return null
  const n = typeof v === 'number' ? (v < 1e12 ? v * 1000 : v) : Date.parse(v)
  return Number.isFinite(n) ? n : null
}
function fmtDate(ms) {
  if (!ms) return '—'
  const d = new Date(ms), now = new Date()
  const hm = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  if (d.toDateString() === now.toDateString()) return `오늘 ${hm}`
  if (d.getFullYear() === now.getFullYear()) return `${d.getMonth() + 1}월 ${d.getDate()}일`
  return `${d.getFullYear()}. ${d.getMonth() + 1}. ${d.getDate()}.`
}

function renderRows() {
  const list = items
    .filter((x) => filter === 'all' || x.type === filter)
    .filter((x) => !query || `${x.name} ${x.info}`.toLowerCase().includes(query))
  $('rows').innerHTML = list.map((x, i) => `
    <tr data-row="${items.indexOf(x)}" style="--c:${C[x.c]}">
      <td><span class="name">${icon(x.icon)}${esc(x.name)}</span></td>
      <td class="kind">${esc(x.kind)}</td>
      <td class="info">${esc(x.info)}</td>
      <td class="date">${fmtDate(x.date)}</td>
    </tr>`).join('')
  $('empty').hidden = list.length > 0
  $('empty').textContent = items.length ? '조건에 맞는 항목이 없습니다.' : '아직 만든 것이 없습니다. 위에서 시작하세요.'
  $('count').textContent = `${FILTERS.find((f) => f.key === filter).label} · ${list.length}개`
}
$('rows').addEventListener('click', (e) => {
  const tr = e.target.closest('[data-row]')
  if (tr) openTarget(items[Number(tr.dataset.row)].target)
})

function renderStatus(neo) {
  const ok = neo && neo.status === 'connected'
  const a = info.agent || {}
  const cli = a.backend === 'cliagents'
  const sub = a.note || (cli ? '이 PC 의 CLI 가 Studio 스킬로 구축·질의합니다' : 'OpenAI 호환 LLM 으로 구축·질의합니다')
  $('status').innerHTML = `
    <div class="status-row"><span class="dot ${ok ? 'ok' : 'bad'}"></span><div><b>Ontological</b> ${ok ? '연결됨' : '연결 안 됨'}<small>그래프 ${esc(info.graph || 'ontology')} · PostgreSQL 16 · 127.0.0.1</small></div></div>
    <div class="status-row"><span class="dot ${a.ready && !a.note ? 'ok' : 'warn'}"></span><div><b>에이전트</b> ${esc(a.ready ? a.label || '' : '사용할 수 없음')}<small>${esc(sub)}</small></div>${a.ready ? '' : '<button data-settings>설정</button>'}</div>`
}
$('status').addEventListener('click', (e) => { if (e.target.closest('[data-settings]') && S) S.open('settings') })

async function getJSON(u) {
  try { const r = await fetch(u, { cache: 'no-store' }); return r.ok ? await r.json() : null } catch { return null }
}
async function load() {
  const [sessions, schemas, boards, fabric, neo, inf, codeapps] = await Promise.all([
    getJSON('/api/sessions'), getJSON('/api/schemas'), getJSON('/api/board/dashboards'),
    getJSON('/fabric-bridge/fabric/overview'), getJSON('/api/neo4j/status'), S ? S.info().catch(() => ({})) : {},
    getJSON('/codeapps/api/apps'),
  ])
  info = inf || {}
  const next = []
  for (const s of (sessions && sessions.sessions) || []) {
    // Studio's first conversation is the 'default' session; list it once something happened in it.
    if (!s || !s.id || (s.id === 'default' && !s.schema_name && (!s.title || s.title === '새 대화'))) continue
    // older sessions carry no mode; one that targets a schema is a build conversation
    const build = s.mode === 'build' || (!s.mode && !!s.schema_name)
    next.push({ type: 'session', name: s.title || '새 대화', kind: build ? '구축 대화' : '질의·액션 대화', info: s.schema_name || '', date: when(s.updated_at || s.created_at), icon: build ? 'build' : 'act', c: build ? 'teal' : 'blue', target: { kind: 'studio', view: build ? 'build' : 'act', session: s.id } })
  }
  for (const s of (schemas && schemas.schemas) || []) {
    const n = s.class_count ?? s.classes_count ?? (Array.isArray(s.classes) ? s.classes.length : null)
    next.push({ type: 'schema', name: s.name || s.id, kind: '온톨로지', info: n != null ? `클래스 ${n}` : (s.description || ''), date: when(s.updated_at || s.created_at), icon: 'node', c: 'teal', target: { kind: 'studio', view: 'build' } })
  }
  for (const b of (boards && (boards.dashboards || boards.items)) || []) {
    next.push({ type: 'board', name: b.title || b.name || b.id, kind: '대시보드', info: b.schema_name || b.schema || '', date: when(b.updated_at || b.created_at), icon: 'board', c: 'violet', target: { kind: 'studio', view: 'board' } })
  }
  // code apps (src/main/codeapps.js) open as their own tab
  for (const a of (codeapps && codeapps.apps) || []) {
    next.push({ type: 'board', name: a.name, kind: '코드 앱', info: a.running ? '에이전트 작업 중' : `수정 ${a.turns}회`, date: when(a.updated_at), icon: 'board', c: 'violet', target: { kind: 'app', app: a.id, title: a.name } })
  }
  const nodes = (fabric && fabric.virtual_nodes) || []
  for (const d of (fabric && fabric.datasources) || []) {
    const n = nodes.filter((x) => String(x.source).startsWith(`${d.name}.`)).length
    next.push({ type: 'datasource', name: d.name, kind: '데이터소스', info: `${d.engine} · 테이블 ${d.table_count} · 노드 ${n}`, date: null, icon: 'datasources', c: 'amber', target: { kind: 'studio', view: 'datasources', ds: d.name } })
  }
  next.sort((a, b) => (b.date || 0) - (a.date || 0))
  items = next
  renderCards(); renderSide(); renderRows(); renderStatus(neo)
}

// ── wiring ──
renderCards(); renderSide(); renderRows()
if (S) {
  S.tabs.onChange((state) => {
    const wasHome = tabState.active === 'home'
    tabState = state
    renderTabs()
    if (state.active === 'home' && !wasHome) load()
  })
  S.tabs.get().then((state) => { if (state) { tabState = state; renderTabs() } })
  document.body.classList.add(`os-${S.platform}`)
S.isFullScreen().then((on) => document.body.classList.toggle('full', !!on))
  S.onFullScreen((on) => document.body.classList.toggle('full', on))
}
renderTabs()
load()
window.addEventListener('focus', () => { if (tabState.active === 'home') load() })
