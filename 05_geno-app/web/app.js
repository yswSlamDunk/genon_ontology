// GenTology 화면 — 서버(/api)와 실제로 연결. 처음엔 데이터가 하나도 없음(빈 상태에서 시작).
// 모양은 제논 어드민 디자인 시스템(문구 합니다체 · 되돌릴 수 없는 일은 확인 모달), 누르면 어디로 가고 무엇이 뜨는지는 Fabric 흐름을 따름(편집기 리본 · 탐색기 · 전체 페이지 편집 + 아래 저장/취소).

const $ = (s) => document.querySelector(s);
const imgUrl = (id, page = 1) => (window.MOCK_IMG && window.MOCK_IMG[page > 1 ? `${id}-p${page}` : id]) || '/api/docs/' + encodeURIComponent(id) + '/image' + (page > 1 ? `?page=${page}` : '');
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmtT = (t) => { if (!t) return '-'; const d = new Date(t * 1000), p = (n) => String(n).padStart(2, '0'); return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`; };
const fmtD = (t) => fmtT(t).slice(0, 10);

async function api(path, opt = {}) {
  const o = { ...opt };
  let uid = ''; try { uid = localStorage.getItem('geno_uid') || ''; } catch { /* 저장소 없음 */ }
  o.headers = { 'X-GenO-User': uid };
  if (o.body && !(o.body instanceof FormData)) { o.headers['Content-Type'] = 'application/json'; o.body = JSON.stringify(o.body); }
  const r = await fetch('/api' + path, o);
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.detail || `요청에 실패했습니다. (${r.status})`);
  return j;
}
const get = (p) => api(p);
const post = (p, body = {}) => api(p, { method: 'POST', body });
const del = (p) => api(p, { method: 'DELETE' });

// ── 공통 UI ──
let toastT, modalClose = null, modalBusy = false;
function toast(t, err = false) {
  const el = $('#toast'); el.className = 'toast on' + (err ? ' err' : '');
  el.innerHTML = ic(err ? 'warn' : 'check', 24) + esc(t); clearTimeout(toastT); toastT = setTimeout(() => (el.className = 'toast'), err ? 5000 : 3000);
}
// 확인 모달 — 위험한 일은 [닫기] [삭제 등], 되돌릴 수 있는 일은 [취소] [확인]
function confirmBox({ title, body = '', ok = '확인', danger = false, cancel = null, input = null }) {
  cancel = cancel || (danger ? '닫기' : '취소');
  return new Promise((res) => {
    $('#modal').className = 'modal' + (input ? ' md' : '');
    $('#modal').innerHTML = `<div class="mh"><h2>${esc(title)}</h2></div><div class="mb">${body}${input ? `<div class="fld" style="margin-top:12px"><label>${esc(input)}<i></i></label><textarea class="inp" id="mIn" rows="3"></textarea></div>` : ''}</div>
      <div class="mf"><button class="btn out" id="mNo">${cancel}</button><button class="btn ${danger ? 'danger' : 'pri'}" id="mOk" ${input ? 'disabled' : ''}>${ok}</button></div>`;
    $('#modalBg').classList.add('on');
    const done = (v) => { modalClose = null; $('#modalBg').classList.remove('on'); res(v); };
    modalClose = () => done(false);
    $('#mNo').onclick = () => done(false);
    $('#mOk').onclick = () => done(input ? $('#mIn').value.trim() : true);
    if (input) $('#mIn').oninput = () => ($('#mOk').disabled = !$('#mIn').value.trim());
  });
}
// 받침 있으면 '을', 없으면 '를'
const josa = (w) => { const c = w.charCodeAt(w.length - 1) - 0xac00; return c < 0 || c > 11171 ? '을(를)' : c % 28 ? '을' : '를'; };
// 필수 칸(라벨에 빨간 점)이 비면 칸 아래에 바로 알림
function checkRequired(root) {
  let first = null;
  root.querySelectorAll('.fld').forEach((f) => {
    f.classList.remove('invalid'); f.querySelector('.err-msg')?.remove();
    const req = f.querySelector('label i'), inp = f.querySelector('.inp');
    if (req && inp && !inp.value.trim()) {
      const lab = f.querySelector('label').textContent.trim();
      f.classList.add('invalid'); f.insertAdjacentHTML('beforeend', `<span class="err-msg">${esc(lab)}${josa(lab)} 입력해 주세요.</span>`);
      first = first || inp;
    }
  });
  if (first) first.focus();
  return !first;
}
function formModal(title, html, okLabel, onOk, size = 'md') {
  formModal.rebindExtra = null;
  $('#modal').className = 'modal ' + size;
  $('#modal').innerHTML = `<div class="mh"><h2>${esc(title)}</h2></div><div class="mb" style="color:var(--ink)">${html}</div>
    <div class="mf"><button class="btn out" id="mNo">취소</button><button class="btn pri" id="mOk">${okLabel}</button></div>`;
  $('#modalBg').classList.add('on');
  let dirty = false;
  $('#modal').addEventListener('input', () => (dirty = true));
  const close = async () => {
    if (modalBusy) return;
    if (dirty) { modalClose = null; const html0 = $('#modal').innerHTML, vals = [...$('#modal').querySelectorAll('input,textarea,select')].map((x) => x.value); if (!(await confirmBox({ title: '저장하지 않고 나가시겠습니까?', body: '입력한 내용은 저장되지 않습니다.', ok: '나가기', danger: true }))) { $('#modal').className = 'modal ' + size; $('#modal').innerHTML = html0; [...$('#modal').querySelectorAll('input,textarea,select')].forEach((x, i) => (x.value = vals[i])); $('#modalBg').classList.add('on'); formModal.rebindExtra?.(); return formModal.rebind(); } }
    modalClose = null; $('#modalBg').classList.remove('on');
  };
  formModal.rebind = () => { $('#mNo').onclick = close; modalClose = close; $('#mOk').onclick = submit; };
  const submit = async () => {
    if (!checkRequired($('#modal'))) return;
    await run($('#mOk'), '', async () => { modalBusy = true; try { await onOk(); modalClose = null; $('#modalBg').classList.remove('on'); } finally { modalBusy = false; } });
  };
  formModal.rebind();
}
function panel(html, size = 'lg') { $('#spanel').className = `spanel ${size} on`; $('#spanel').innerHTML = html; $('#dim').classList.add('on'); }
async function closePanel(force = false) {
  if (!force && typeof NODE !== 'undefined' && NODE.dirty && !(await leaveNode())) return;
  $('#spanel').classList.remove('on'); $('#dim').classList.remove('on');
}
const empty = (title, desc = '', btn = '', sm = false, icon = 'cube') => `<div class="empty ${sm ? 'sm' : ''} ${icon === 'warn' ? 'err' : ''}"><span class="ei">${ic(icon, sm ? 24 : 48)}</span><div class="et"><b>${title}</b>${desc ? `<p>${desc}</p>` : ''}</div>${btn}</div>`;
const resetBtn = (code) => `<button class="btn ter sm" onclick="${code};render()">${ic('refresh', 16)}초기화</button>`;
// 처리 중: 버튼 글자는 그대로 두고 앞에 도는 표시만 붙임(폭 유지)
async function run(btn, label, fn) {
  const old = btn.innerHTML, w = btn.offsetWidth; btn.disabled = true; btn.style.minWidth = w + 'px';
  btn.innerHTML = '<span class="spin"></span>' + old.replace(/<svg[\s\S]*?<\/svg>/, '');
  try { return await fn(); } catch (e) { toast(e.message, true); } finally { btn.disabled = false; btn.innerHTML = old; btn.style.minWidth = ''; }
}

// ── 메뉴 ──
// 메뉴는 역할에 따라 — 현업(쓰는 사람)은 데이터 에이전트 · 내 질문 기록 · 그래프 탐색만
const NAV_ALL = [
  ['구축', [['source', '데이터 원본', 'db'], ['design', '온톨로지 설계', 'graph'], ['read', '문서 읽기', 'doc']]],
  ['검증', [['golden', '골든 질문', 'star'], ['trace', '질문 기록', 'trace'], ['explore', '그래프 탐색', 'search']]],
  ['관리', [['history', '변경 이력', 'history'], ['users', '사용자·권한', 'user']]],
];
const NAV_USER = [['', [['ask', '데이터 에이전트', 'chat'], ['trace', '내 질문 기록', 'trace'], ['explore', '그래프 탐색', 'search']]]];
const navFor = () => (isUser() ? NAV_USER : NAV_ALL.map(([g, items]) => [g, items.filter(([id]) => id !== 'users' || can('admin'))]));
const TITLE = { ...Object.fromEntries(NAV_ALL.flatMap((g) => g[1].map((i) => [i[0], i[1]]))), connect: '데이터 원본 연결', rules: '규칙', metrics: '메트릭', workspace: '작업 영역', whatif: '가정 바꿔 보기' };
const cur = () => (location.hash.slice(1) || 'workspace').split('?')[0];
let ST = {};

function renderNav() {
  // 규칙 · 메트릭은 온톨로지 설계 안(탐색기 개요)에서 들어감 — 메뉴에선 온톨로지 설계를 켬(Fabric 온톨로지 규칙처럼)
  const c = { connect: 'source', rules: 'design', metrics: 'design', whatif: 'design' }[cur()] || cur();
  document.querySelector('.lnb .ws')?.classList.toggle('cur', c === 'workspace');
  const cnt = { read: ST.review, history: ST.pending };
  $('#nav').innerHTML = navFor().map(([g, items]) => (g ? `<div class="grp">${g}</div>` : '') + items.map(([id, t, icon]) =>
    `<a href="#${id}" class="${c === id ? 'cur' : ''}">${ic(icon, 20)}<span>${t}</span>${cnt[id] ? `<span class="cnt">${cnt[id]}</span>` : ''}</a>`).join('')).join('');
}

// ── 그래프 배치(자동) ──
function layout(names, edges, W = 1000, H = 460) {
  const n = names.length, P = {};
  if (!n) return P;
  names.forEach((k, i) => { const a = (i / n) * Math.PI * 2; P[k] = { x: W / 2 + Math.cos(a) * W * 0.35, y: H / 2 + Math.sin(a) * H * 0.35 }; });
  for (let it = 0; it < 400; it++) {
    const F = Object.fromEntries(names.map((k) => [k, { x: 0, y: 0 }]));
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
      const a = P[names[i]], b = P[names[j]], dx = a.x - b.x, dy = (a.y - b.y) * 1.6, d2 = Math.max(dx * dx + dy * dy, 100), f = 60000 / d2, d = Math.sqrt(d2);
      F[names[i]].x += (dx / d) * f; F[names[i]].y += (dy / d) * f; F[names[j]].x -= (dx / d) * f; F[names[j]].y -= (dy / d) * f;
    }
    for (const [a, b] of edges) {
      if (!P[a] || !P[b]) continue;
      const dx = P[b].x - P[a].x, dy = P[b].y - P[a].y, d = Math.max(Math.hypot(dx, dy), 1), f = (d - 210) * 0.05;
      F[a].x += (dx / d) * f; F[a].y += (dy / d) * f; F[b].x -= (dx / d) * f; F[b].y -= (dy / d) * f;
    }
    for (const k of names) { P[k].x += Math.max(-20, Math.min(20, F[k].x + (W / 2 - P[k].x) * 0.01)); P[k].y += Math.max(-20, Math.min(20, F[k].y + (H / 2 - P[k].y) * 0.01)); }
  }
  const xs = names.map((k) => P[k].x), ys = names.map((k) => P[k].y), mnx = Math.min(...xs), mxx = Math.max(...xs), mny = Math.min(...ys), mxy = Math.max(...ys);
  for (const k of names) { P[k].x = 90 + ((P[k].x - mnx) / Math.max(mxx - mnx, 1)) * (W - 180); P[k].y = 40 + ((P[k].y - mny) / Math.max(mxy - mny, 1)) * (H - 80); }
  // 상자끼리 겹치면 밀어냄(상자 150×48 + 여백)
  for (let it = 0; it < 300; it++) {
    let moved = false;
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
      const a = P[names[i]], b = P[names[j]], dx = b.x - a.x, dy = b.y - a.y, ox = 172 - Math.abs(dx), oy = 66 - Math.abs(dy);
      if (ox > 0 && oy > 0) {
        moved = true;
        if (ox / 172 < oy / 66) { const m = (ox / 2 + 1) * (dx < 0 ? -1 : 1); a.x -= m; b.x += m; } else { const m = (oy / 2 + 1) * (dy < 0 ? -1 : 1); a.y -= m; b.y += m; }
      }
    }
    for (const k of names) { P[k].x = Math.max(80, Math.min(W - 80, P[k].x)); P[k].y = Math.max(30, Math.min(H - 30, P[k].y)); }
    if (!moved) break;
  }
  return P;
}
function svgGraph(nodes, edges, { W = 1000, H = 460, sel = null, hot = null, attr = 'data-node' } = {}) {
  // nodes: [{id, label, sub}], edges: [{a, b, cls, lab}]
  const P = layout(nodes.map((x) => x.id), edges.map((e) => [e.a, e.b]), W, H);
  const hotN = hot ? new Set(hot) : null;
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
  for (const e of edges) {
    if (!P[e.a] || !P[e.b]) continue;
    s += `<line class="e ${e.cls || ''}" x1="${P[e.a].x}" y1="${P[e.a].y}" x2="${P[e.b].x}" y2="${P[e.b].y}"/>`;
    if (e.lab) s += `<text class="elab ${e.cls || ''}" x="${(P[e.a].x + P[e.b].x) / 2}" y="${(P[e.a].y + P[e.b].y) / 2 - 8}" text-anchor="middle">${esc(e.lab)}</text>`;
  }
  for (const x of nodes) {
    const p = P[x.id], w = 150, h = 48;
    const cls = [sel === x.id ? 'sel' : '', hotN && hotN.has(x.id) ? 'hot' : '', hotN && !hotN.has(x.id) ? 'dimn' : ''].join(' ');
    s += `<g class="node ${cls}" ${attr}="${esc(x.id)}"><rect x="${p.x - w / 2}" y="${p.y - h / 2}" width="${w}" height="${h}" rx="8"/>` +
      `<text x="${p.x}" y="${p.y - 3}" text-anchor="middle">${esc(String(x.label).slice(0, 12))}</text><text class="s" x="${p.x}" y="${p.y + 14}" text-anchor="middle">${esc(String(x.sub).slice(0, 20))}</text></g>`;
  }
  return s + '</svg>';
}

// ── 페이지 ──
const P = {};

P.home = async () => {
  const s = ST, asks = await get('/asks');
  const steps = [
    [1, '데이터 원본', s.sources ? `원본 ${s.sources}개 · 테이블 ${s.tables}개` : '연결 전', s.sources ? 'source' : 'connect', s.tables > 0],
    [2, '온톨로지 설계', s.objects ? `엔터티 형식 ${s.objects}개 · 관계 ${s.relations}개 · 엔터티 형식을 눌러 업무 이름을 채워 주세요` : '설계 전', 'design', s.objects > 0],
    [3, '문서 읽기', s.docs ? `문서 ${s.docs}건 · 읽음 ${s.read}건` : '선택 · 문서가 있을 때', 'read', !s.docs || (s.read > 0 && !s.review)],
    [4, '규칙·메트릭', s.rules || s.metrics ? `규칙 ${s.rules}개 · 메트릭 ${s.metrics}개` : '규칙·메트릭 없음', 'rules', s.rules > 0 || s.metrics > 0],
    [5, '골든 질문', s.golden ? `${s.golden_pass}개 / ${s.golden}개 통과` : '질문 없음', 'golden', s.golden > 0 && s.golden_pass === s.golden],
    [6, '변경 이력', s.version ? `현재 버전 v${s.version}${s.pending ? ` · 승인 대기 ${s.pending}건` : ''}` : '기록 없음', 'history', s.version > 0 && !s.pending],
  ];
  const next = steps.find((x) => !x[4]);
  const step = ([no, t, sub, href, done]) => `<button class="stp ${done ? 'done' : ''} ${next && next[0] === no ? 'next' : ''}" onclick="location.hash='${href}'"><span class="n">${done ? ic('check', 14) : no}</span><b>${t}${next && next[0] === no ? ' <span class="b info">다음</span>' : ''}</b><span class="s">${sub}</span></button>`;
  const m = (icon, k, v, unit, sub2 = '') => `<div class="metric"><span class="mi">${ic(icon, 24)}</span><div><div class="k">${k}</div><div class="v">${v === null ? '-' : v}${v === null ? '' : `<small>${unit}</small>`}${sub2 ? `<span class="sub2">${sub2}</span>` : ''}</div></div></div>`;
  return `
  <div class="ph"><div class="t"><h1>개요</h1><p>데이터를 연결해 온톨로지를 만들고, 골든 질문으로 맞는지 확인합니다.</p></div>
    ${next ? `<button class="btn pri" ${next[0] === 6 ? lock('review') : lock()} onclick="location.hash='${next[3]}'">다음: ${next[1]}</button>` : ''}</div>
  ${s.setup ? `<div class="alert info" style="margin-bottom:16px">${ic('info')}<div>첫 관리자를 생성하면 역할별로 화면과 권한이 나뉩니다. 지금은 모든 기능을 쓸 수 있습니다.</div><button class="btn ter act" onclick="firstAdmin()">첫 관리자 생성</button></div>` : ''}
  <div class="card"><h3>구축 의도 <span class="sp"></span>${s.intent ? `<button class="ibtn" aria-label="구축 의도 수정" ${lock()} onclick="editIntent()">${ic('pencil', 16)}</button>` : ''}</h3>
    ${s.intent ? `<p style="margin:0;font-size:16px;line-height:24px">${esc(s.intent)}</p>` : empty('아직 구축 의도가 없습니다.', '이 데이터로 무엇을 하려는지 적어 주세요. 테이블을 연결하면 AI가 초안을 제안합니다.', `<button class="btn out sm" ${lock()} onclick="editIntent()">구축 의도 작성</button>`, true, 'pencil')}</div>
  <div class="sec"><div class="sec-t">진행 단계</div><div class="steps">
    ${steps.map(step).join('')}
  </div></div>
  <div class="sec g4">
    ${m('star', '골든 질문 통과', s.golden_run ? s.golden_pass : null, '개', s.golden ? `전체 ${s.golden}개` : '')}
    ${m('graph', '엔터티 형식', s.objects, '개', s.objects ? `관계 ${s.relations}개` : '')}
    ${m('doc', '검수 대기', s.read ? s.review : null, '칸')}
    ${m('chat', '질문', s.asks, '건')}
  </div>
  <div class="sec"><div class="sec-t">최근 질문 <span class="sp"></span>${asks.length ? `<button class="btn out sm" onclick="location.hash='trace'">질문 기록으로 이동</button>` : ''}</div>
    <div class="card flat">${asks.length ? `<table class="t"><thead><tr><th>질문</th><th>예제 쿼리</th><th>답</th><th>질문 일시</th></tr></thead><tbody>
      ${asks.slice(0, 5).map((a) => `<tr class="click" onclick="openAsk(${a.id})"><td>${esc(a.q)}</td><td><span class="b">${esc(a.tpl || '-')}</span></td><td>${statusDot(a.status, a.answer)}</td><td class="r">${fmtT(a.at)}</td></tr>`).join('')}
      </tbody></table>` : empty('아직 질문이 없습니다.', '데이터 에이전트 화면에서 데이터에 대해 물어볼 수 있습니다.', `<button class="btn out sm" onclick="location.hash='ask'">데이터 에이전트</button>`, true, 'chat')}</div></div>`;
};
const statusDot = (st, ans) => st === 'ok' ? `<span class="dotb ok">${esc(ans)}</span>` : st === 'broken' ? `<span class="dotb bad">데이터 미연결로 답변 불가</span>` : `<span class="dotb warn">${esc(ans || '답변 불가')}</span>`;
async function editIntent() {
  formModal('구축 의도 수정', `<div class="fld"><label>구축 의도<i></i></label><textarea class="inp" id="fIntent" rows="4" placeholder="예) 청구 서류 값을 계약 테이블과 이어 지급액 계산">${esc(ST.intent || '')}</textarea>
    <span class="help">${ST.tables ? '<span class="link" id="intentAi">AI 초안 생성</span>' : '테이블을 연결하면 AI 초안을 받을 수 있습니다.'}</span></div>`, '저장', async () => {
    const t = $('#fIntent').value.trim(); if (!t) throw new Error('구축 의도를 입력해 주세요.');
    await post('/onto/intent', { text: t }); toast('구축 의도가 저장되었습니다.'); await refresh();
  });
  const a = $('#intentAi'); if (a) a.onclick = async () => { a.textContent = '생성 중'; try { $('#fIntent').value = (await post('/onto/intent/draft')).text; } catch (e) { toast(e.message, true); } a.textContent = 'AI 초안 생성'; };
}

// 작업 영역 — Fabric 작업 영역처럼: 이 공간에 있는 항목(데이터 · 온톨로지 · 질문 에이전트 · 골든 질문)을 종류별 아이콘 목록으로. 누르면 그 항목 화면으로
let WSF = '';
const WSK = { data: ['데이터', 'db'], onto: ['온톨로지', 'graph'], agent: ['데이터 에이전트', 'chat'], eval: ['평가', 'star'] };
P.workspace = async () => {
  const [srcs, ch, ag] = await Promise.all([get('/sources'), get('/changes'), get('/agent').catch(() => ({ instr: '', templates: [] }))]);
  const last = (layers) => Math.max(0, ...ch.items.filter((c) => layers.includes(c.layer) && c.status === 'applied').map((c) => c.at)) || null;
  const items = [
    ...srcs.map((s) => ({ k: 'data', icon: s.kind === 'db' ? 'db' : s.kind === 'doc' ? 'pdf' : 'csv', name: s.name, type: s.kind === 'db' ? `DB 연결 · ${s.kind_label}` : s.kind === 'doc' ? '업로드 · 문서' : '업로드 · 테이블',
      sub: s.kind === 'doc' ? `문서 ${s.docs}건` : `테이블 ${s.tables.length}개 · ${s.tables.reduce((n, t) => n + t.nrows, 0).toLocaleString()}행`, at: s.synced_at, go: `SSEL={k:'src',id:'${s.id}'};location.hash='source'` })),
    ...(ST.objects ? [{ k: 'onto', icon: 'graph', name: '온톨로지', type: '온톨로지', sub: `엔터티 형식 ${ST.objects}개 · 관계 ${ST.relations}개 · 규칙 ${ST.rules}개 · 메트릭 ${ST.metrics}개`, at: last(['개체 · 관계', '규칙', '지표', '읽을 칸']), go: "location.hash='design'" }] : []),
    ...(ST.objects ? [{ k: 'agent', icon: 'chat', name: '데이터 에이전트', type: '데이터 에이전트', sub: `예제 쿼리 ${ag.templates.length}개 · 지침 ${ag.instr ? '있음' : '없음'} · 질문 ${ST.asks}건`, at: last(['에이전트']), go: "location.hash='ask'" }] : []),
    ...(ST.golden ? [{ k: 'eval', icon: 'star', name: '골든 질문', type: '평가', sub: `${ST.golden}개 중 ${ST.golden_pass || 0}개 통과`, at: last(['골든 질문']), go: "location.hash='golden'" }] : []),
  ];
  const list = items.filter((x) => !WSF || x.k === WSF);
  const newMenu = `<div class="morew"><button class="btn pri" ${lock()} aria-haspopup="menu" onclick="getMenu(event)">${ic('plus')}새 항목${ic('chevd', 16)}</button><div class="menu" id="getMenu" role="menu">
    <button role="menuitem" onclick="closeMenu();filePanel()">${ic('upload')}<span>파일 업로드<small class="muted"> · CSV는 테이블, 그림·PDF는 문서</small></span></button>
    <button role="menuitem" onclick="closeMenu();Object.assign(CN,{step:1,kind:'',tested:null,conf:null,name:'',pick:null,pw:''});location.hash='connect'">${ic('db')}<span>DB 연결</span></button>
    <div class="sepl"></div><button role="menuitem" ${ST.tables ? '' : 'disabled'} onclick="closeMenu();location.hash='design';setTimeout(draftDialog,500)">${ic('graph')}<span>온톨로지<small class="muted"> · 테이블로 AI 초안</small></span></button>
    <button role="menuitem" ${ST.objects ? '' : 'disabled'} onclick="closeMenu();location.hash='golden';setTimeout(goldModal,500)">${ic('star')}<span>골든 질문</span></button></div></div>`;
  return `<div class="ph"><div class="t"><h1>GenTology 작업 영역</h1><p>이 공간에 있는 데이터 · 온톨로지 · 데이터 에이전트 · 골든 질문입니다. 누르면 그 항목이 열립니다.</p></div>${can('build') ? newMenu : ''}</div>
  ${items.length ? `<div class="lc"><div class="seg" role="group" aria-label="종류">${[['', '전체'], ...Object.entries(WSK).map(([k, v]) => [k, v[0]])].map(([k, t]) => `<button class="${WSF === k ? 'on' : ''}" onclick="WSF='${k}';render()">${t}${k ? ` <span class="muted">${items.filter((x) => x.k === k).length}</span>` : ''}</button>`).join('')}</div><span class="cnt">총 ${list.length}개</span></div>
  <div class="card flat"><table class="t"><thead><tr><th>이름</th><th>유형</th><th>내용</th><th>최근 변경</th></tr></thead><tbody>
    ${list.map((x) => `<tr class="click" onclick="${x.go}"><td><span class="wsn"><span class="wsi ${x.k}">${ic(x.icon, 16)}</span>${esc(x.name)}</span></td><td class="r">${esc(x.type)}</td><td class="r">${esc(x.sub)}</td><td class="r">${fmtT(x.at)}</td></tr>`).join('')}</tbody></table></div>`
  : `<div class="card">${empty('작업 영역이 비어 있습니다.', '데이터를 가져오면 여기에 항목이 생기고, 테이블로 온톨로지를 만들 수 있습니다.', can('build') ? `<button class="btn pri" onclick="filePanel()">파일 업로드</button>` : '', false, 'db')}</div>`}
  <div class="guide" style="margin-top:24px"><b>항목 순서</b>데이터(테이블 · 문서) → 온톨로지(엔터티 형식 · 관계 · 규칙 · 메트릭) → 질문 에이전트(데이터 에이전트) → 골든 질문(맞는지 확인)</div>`;
};

// 데이터 원본 — Fabric 레이크하우스 탐색기처럼: 왼쪽 트리(원본 폴더 › 테이블 · 문서), 누르면 오른쪽에 테이블 미리 보기 · 문서 그림 · 원본 정보
let SRC = [], SDOCS = [], SSEL = { k: '', id: '' }, SOPEN = {};
const KL = { csv: 'CSV 파일', db: 'DB', doc: '문서' };
P.source = async () => {
  [SRC, SDOCS] = await Promise.all([get('/sources'), get('/docs').then((d) => d.docs).catch(() => [])]);
  ONTO = ONTO || (await get('/onto').catch(() => null));
  if (!SRC.length) {
    return `<div class="ph"><div class="t"><h1>데이터 원본</h1><p>회사 DB를 연결하거나 파일·문서를 업로드합니다. 가져온 테이블은 온톨로지의 엔터티 형식이 됩니다.</p></div>${can('build') ? getDataBtn() : ''}</div>
    <div class="card">${empty('아직 데이터 원본이 없습니다.', can('build') ? 'CSV·문서를 업로드하거나 DB를 연결해 주세요.' : '구축 담당이 데이터 원본을 연결하면 여기에 표시됩니다.', '', false, 'db')}</div>`;
  }
  if (SSEL.k === 'src' && !SRC.some((s) => s.id === +SSEL.id)) SSEL = { k: '', id: '' };
  return `<div class="ph"><div class="t"><h1>데이터 원본</h1><p>왼쪽에서 테이블이나 문서를 누르면 내용을 바로 봅니다. 가져온 테이블은 온톨로지 설계에서 엔터티 형식이 됩니다.</p></div>${getDataBtn()}</div>
  <div class="edb"><aside class="exp" aria-label="그래프 탐색기"><div class="xh">탐색기 <span class="xn">원본 ${SRC.length}</span></div>${srcTree()}</aside>
  <section class="cv" id="srcView">${await srcView()}</section></div>`;
};
function srcTree() {
  // Fabric 레이크하우스처럼 두 갈래: 테이블(Tables) — CSV · DB에서 온 테이블 / 파일(Files) — 업로드한 그림 · PDF
  const item = (k, id, icon, label, extra = '') => `<button class="xi ${SSEL.k === k && String(SSEL.id) === String(id) ? 'on' : ''}" style="padding-left:44px" onclick="srcPick('${k}','${esc(id)}')">${ic(icon, 16)}<span class="xl ${k === 'tbl' ? 'mono' : ''}">${esc(label)}</span>${extra}</button>`;
  const folder = (s, kids) => { const open = SOPEN[s.id] !== false; return `<div class="xi xr ${SSEL.k === 'src' && SSEL.id == s.id ? 'on' : ''}" style="padding-left:12px"><button class="xm" aria-expanded="${open}" onclick="SOPEN[${s.id}]=${!open};srcRedraw()"><span class="tw ${open ? 'o' : ''}">${ic('chev', 12)}</span>${ic(s.kind === 'db' ? 'db' : 'side', 16)}<span class="xl">${esc(s.name)}</span></button><button class="ibtn sm" aria-label="${esc(s.name)} 정보" data-tip="원본 정보" onclick="srcPick('src',${s.id})">${ic('info', 16)}</button></div>${open ? kids : ''}`; };
  const up = (s) => s.tables.filter((t) => t.name !== 'doc_extract');
  const ts = SRC.filter((s) => up(s).length), fs = SRC.filter((s) => SDOCS.some((d) => d.source_id === s.id));
  const dx = SRC.flatMap((s) => s.tables).find((t) => t.name === 'doc_extract');
  const nt = ts.reduce((n, s) => n + up(s).length, 0) + (dx ? 1 : 0);
  const dxOpen = SOPEN.dx !== false;
  const dxFolder = dx ? `<div class="xi xr" style="padding-left:12px"><button class="xm" aria-expanded="${dxOpen}" onclick="SOPEN.dx=${!dxOpen};srcRedraw()"><span class="tw ${dxOpen ? 'o' : ''}">${ic('chev', 12)}</span>${ic('robot', 16)}<span class="xl">문서에서 읽은 값</span></button></div>${dxOpen ? item('tbl', 'doc_extract', 'table', 'doc_extract', `<span class="xn">${dx.nrows.toLocaleString()}</span>`) : ''}` : '';
  return `<div class="xg">${ic('table', 12)} 테이블 <span class="xn">${nt}</span></div>${ts.length || dx ? ts.map((s) => folder(s, up(s).map((t) => item('tbl', t.name, 'table', t.name, `<span class="xn">${t.nrows.toLocaleString()}</span>`)).join(''))).join('') + dxFolder : '<p class="xe">테이블이 없습니다. CSV를 올리거나 DB를 연결해 주세요.</p>'}
    <div class="xg">${ic('doc', 12)} 파일 <span class="xn">${SDOCS.length}</span></div>${fs.length ? fs.map((s) => folder(s, SDOCS.filter((d) => d.source_id === s.id).map((d) => item('doc', d.id, d.file?.toLowerCase().endsWith('.pdf') ? 'pdf' : 'doc', d.id, d.read_at ? '' : '<span class="xn">읽기 전</span>')).join(''))).join('') : '<p class="xe">파일이 없습니다. 그림·PDF를 올리면 여기에 보입니다.</p>'}`;
}
function srcPick(k, id) { SSEL = { k, id }; srcRedraw(); }
// doc_extract 표 — 줄을 고르면 표 아래에 그 문서(그림 · 읽은 값 · 본문)를 보여 줌(위: 표, 아래: 고른 문서)
async function dxPick(did) { SSEL.dx = SSEL.dx === did ? '' : did; await srcRedraw(); if (SSEL.dx) dxDetail(did); }
async function dxDetail(did, page = 1) {
  const el = $('#dxDetail'); if (!el) return;
  const [vals, txt] = await Promise.all([get('/docs/' + encodeURIComponent(did) + '/values'), get('/docs/' + encodeURIComponent(did) + '/text')]);
  if (!DOCS || !DOCS.docs.some((x) => x.id === did)) DOCS = await get('/docs');
  const d = DOCS.docs.find((x) => x.id === did) || {}, np = Math.min(d.pages || 1, 10), ptxt = [...new Set(txt.filter((t) => t.page === page).map((t) => t.text))];
  el.innerHTML = `<div class="dxd"><div class="cvt" style="margin:16px 0 8px"><b class="mono">${esc(did)}</b><span class="b">${esc(d.doc_type || '-')}</span>${np > 1 ? `<span class="row" style="gap:4px"><button class="ibtn sm" aria-label="이전 쪽" ${page > 1 ? '' : 'disabled'} onclick="dxDetail('${esc(did)}',${page - 1})">${ic('chev', 16).replace('<svg', '<svg style="transform:rotate(180deg)"')}</button><span class="muted">${page} / ${np}쪽</span><button class="ibtn sm" aria-label="다음 쪽" ${page < np ? '' : 'disabled'} onclick="dxDetail('${esc(did)}',${page + 1})">${ic('chev', 16)}</button></span>` : ''}<span class="sp"></span><button class="btn out sm" onclick="openDoc('${esc(did)}',${page})">${ic('side', 16)}패널로 크게 보기</button></div>
    <div class="gdoc"><div class="docfig"><img class="docimg big" style="max-height:48vh" src="${imgUrl(did, page)}" alt="${esc(did)} ${page}쪽" onclick="viewImg('${esc(did)}',${page})"><div class="zbs"><button class="zb" onclick="viewImg('${esc(did)}',${page})">${ic('search', 16)}화면 가득</button></div></div>
    <div><div class="sec-t sm">읽은 값</div><table class="t"><thead><tr><th>칸</th><th>값</th><th>확신도</th></tr></thead><tbody>${vals.map((v) => `<tr><td>${esc((DOCS.fields.find((f) => f.name === v.field) || {}).label || v.field)}</td><td class="mono">${esc(v.value || '-')}</td><td class="r">${v.by === '사람' ? '<span class="b ok">사람</span>' : v.conf == null ? '-' : v.conf.toFixed(2)}</td></tr>`).join('') || `<tr><td colspan="3" class="r">${d.read_at ? '읽을 칸이 없어 값은 없습니다.' : '아직 읽지 않았습니다.'}</td></tr>`}</tbody></table>
    ${ptxt.length ? `<details class="sqlbox" open style="margin-top:12px"><summary>${page}쪽 본문(AI가 읽은 글자)</summary><div class="doctext" style="max-height:30vh;overflow:auto">${esc(ptxt.join('\n…\n'))}</div></details>` : ''}</div></div></div>`;
}
async function srcRedraw() { if (cur() !== 'source') return; $('.exp').innerHTML = `<div class="xh">탐색기 <span class="xn">원본 ${SRC.length}</span></div>${srcTree()}`; $('#srcView').innerHTML = await srcView(); }
const objOfTbl = (t) => ONTO?.objects.filter((o) => o.base === t) || [];
async function srcView() {
  const { k, id } = SSEL;
  if (k === 'tbl') {
    const t = await get('/tables/' + encodeURIComponent(id) + '?n=50').catch(() => null);
    const s = SRC.find((x) => x.tables.some((y) => y.name === id)), meta = s?.tables.find((y) => y.name === id);
    if (!t || !meta) return empty('테이블을 찾을 수 없습니다.', '', '', true, 'table');
    const objs = objOfTbl(id), nf = Math.max(0, meta.cols.length - 4);
    const dxNote = id === 'doc_extract' ? `<div class="alert ${nf ? 'info' : 'warn'}" style="margin-bottom:12px">${ic(nf ? 'info' : 'warn')}<div><b>문서 읽기가 만든 테이블입니다.</b> 문서 한 건이 한 줄이고, 문서 읽기에서 정한 <b>읽을 칸</b>이 열이 됩니다. ${nf ? `지금 읽을 칸 ${nf}개.` : '아직 읽을 칸이 없어 문서 이름 · 종류만 있습니다. 본문 글자는 본문 검색용으로 따로 저장되어 있습니다.'}</div><button class="btn ter act" onclick="location.hash='read'">${nf ? '문서 읽기로' : '읽을 칸 정하기'}</button></div>` : '';
    return dxNote + `<div class="cvt"><b class="mono" style="font-size:16px">${esc(id)}</b><span class="b">${meta.nrows.toLocaleString()}행 · ${meta.cols.length}열</span>${objs.length ? objs.map((o) => `<button class="b info" style="border:0;cursor:pointer" onclick="dzOpen('${esc(o.name)}')">엔터티 형식 · ${esc(o.label)}</button>`).join('') : '<span class="b warn" data-tip="온톨로지 설계에서 이 테이블로 엔터티 형식을 만들 수 있습니다.">엔터티 형식 아님</span>'}<span class="sp"></span><span class="muted">${esc(s.name)}</span></div>
      <div style="overflow:auto;max-height:${id === 'doc_extract' && SSEL.dx ? '36vh' : 'calc(100vh - 340px)'}"><table class="t"><thead><tr>${t.cols.map((c, i) => `<th>${esc(c)}<div class="muted" style="font-weight:400">${esc(meta.types?.[i] || '')}</div></th>`).join('')}</tr></thead><tbody>${t.rows.map((r) => `<tr ${id === 'doc_extract' && r.doc_id ? `class="click ${SSEL.dx === r.doc_id ? 'sel' : ''}" onclick="dxPick('${esc(r.doc_id)}')"` : ''}>${t.cols.map((c) => `<td class="r">${esc(r[c])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
      ${id === 'doc_extract' ? `<p class="muted" style="margin:8px 0 0">줄을 누르면 아래에 그 문서의 그림 · 읽은 값 · 본문이 보입니다. 표는 그대로 남습니다.</p><div id="dxDetail">${SSEL.dx ? '<p class="muted">문서를 불러오는 중입니다.</p>' : ''}</div>` : ''}${meta.nrows > t.rows.length ? `<p class="muted" style="margin:8px 0 0">앞 ${t.rows.length}행만 보여 줍니다.</p>` : ''}`;
  }
  if (k === 'doc') {
    const d = SDOCS.find((x) => x.id === id); if (!d) return empty('문서를 찾을 수 없습니다.', '', '', true, 'doc');
    return `<div class="cvt"><b class="mono" style="font-size:16px">${esc(d.id)}</b><span class="b">${d.pages || 1}쪽</span>${d.read_at ? `<span class="b ok">읽음${d.doc_type ? ` · ${esc(d.doc_type)}` : ''}</span>` : '<span class="b">읽기 전</span>'}${d.rot ? `<span class="b info">자동으로 ${d.rot}° 돌림</span>` : ''}${d.lying ? '<span class="b warn">누운 문서</span>' : ''}<span class="sp"></span><button class="btn out sm" onclick="location.hash='read';setTimeout(()=>openDoc('${esc(d.id)}'),400)">문서 읽기에서 열기</button></div>
      ${isUser() ? '' : `<button class="zoomb wide" aria-label="크게 보기" onclick="viewImg('${esc(d.id)}')"><img class="docimg big" src="${imgUrl(d.id)}" alt="${esc(d.id)} 첫 쪽"><span class="zb">${ic('search', 16)}크게 보기</span></button>`}`;
  }
  if (k === 'src') {
    const s = SRC.find((x) => x.id === +id);
    return `<div class="cvt"><b style="font-size:16px">${esc(s.name)}</b><span class="b">${s.kind === 'db' ? esc(s.kind_label) : KL[s.kind]}</span><span class="sp"></span>
      <button class="btn out sm" ${lock()} onclick="srcRename(${s.id})">${ic('pencil', 16)}이름 변경</button>${s.kind === 'db' ? `<button class="btn out sm" ${lock()} onclick="run(this,'',async()=>{await post('/sources/${s.id}/sync');toast('최신 데이터가 반영되었습니다.');refresh()})">${ic('refresh', 16)}지금 가져오기</button>` : ''}<button class="btn dan sm" ${lock()} onclick="removeSource(${s.id})">삭제</button></div>
      <dl class="dl"><dt>유형</dt><dd>${s.kind === 'db' ? esc(s.kind_label) : KL[s.kind]}</dd>${s.where ? `<dt>위치</dt><dd class="mono">${esc(s.where)}</dd>` : ''}<dt>최근 가져오기</dt><dd>${fmtT(s.synced_at)}</dd><dt>가져온 것</dt><dd>${s.kind === 'doc' ? `문서 ${s.docs}건` : `테이블 ${s.tables.length}개`}</dd></dl>`;
  }
  // 아무것도 고르지 않았을 때: 테이블 전체 목록(Fabric 레이크하우스 Tables 목록처럼)
  const all = SRC.flatMap((s) => s.tables.map((t) => ({ ...t, src: s.name })));
  return `<div class="cvt"><b style="font-size:16px">테이블 ${all.length}개 · 문서 ${SDOCS.length}건</b><span class="sp"></span><span class="muted">왼쪽에서 테이블이나 문서를 누르면 내용이 보입니다.</span></div>
    ${all.length ? `<table class="t"><thead><tr><th>테이블</th><th>원본</th><th class="num">행</th><th class="num">열</th><th>엔터티 형식</th></tr></thead><tbody>${all.map((t) => { const o = objOfTbl(t.name); return `<tr class="click" onclick="srcPick('tbl','${esc(t.name)}')"><td class="mono">${esc(t.name)}</td><td class="r">${esc(t.src)}</td><td class="num">${t.nrows.toLocaleString()}</td><td class="num">${t.cols.length}</td><td>${o.length ? o.map((x) => `<span class="b info">${esc(x.label)}</span>`).join(' ') : '<span class="b warn">엔터티 형식 아님</span>'}</td></tr>`; }).join('')}</tbody></table>` : empty('가져온 테이블이 없습니다.', '', '', true, 'table')}`;
}
function srcRename(id) {
  const s = SRC.find((x) => x.id === id);
  formModal('이름 변경', `<div class="fld"><label>이름<i></i></label><input class="inp" id="sN" value="${esc(s.name)}"></div>`, '저장', async () => {
    await post(`/sources/${id}/name`, { name: $('#sN').value.trim() }); toast('이름이 변경되었습니다.'); refresh();
  });
}
async function removeSource(id) {
  const s = SRC.find((x) => x.id === id);
  if (!(await confirmBox({ title: '데이터 원본을 삭제하시겠습니까?', body: `${esc(s.name)}에서 가져온 테이블·문서와 읽은 값이 함께 삭제됩니다. 삭제 후에는 되돌릴 수 없습니다.`, ok: '삭제', danger: true }))) return;
  await del('/sources/' + id); SSEL = { k: '', id: '' }; toast('데이터 원본이 삭제되었습니다.'); refresh();
}

// 데이터 가져오기 — Fabric 흐름: [데이터 가져오기 ▾] → 파일 업로드(사이드 패널) / DB 연결(원본 선택 → 연결 설정 → 테이블 선택 → 검토 → 만들기)
const CN = { step: 1, kind: '', tested: null, conf: null, name: '', pick: null, pw: '' };
const DBK = [['postgresql', 'PostgreSQL', '5432'], ['mysql', 'MySQL · MariaDB', '3306'], ['sqlite', 'SQLite 파일', '']];
function getMenu(e) {
  e.stopPropagation(); const m = $('#getMenu'); const on = !m.classList.contains('on'); closeMenu(); m.classList.toggle('on', on);
}
const getDataBtn = (cls = 'btn pri') => `<div class="morew"><button class="${cls}" ${lock()} aria-haspopup="menu" onclick="getMenu(event)">${ic('plus')}데이터 가져오기${ic('chevd', 16)}</button><div class="menu" id="getMenu" role="menu">
  <button role="menuitem" onclick="closeMenu();filePanel()">${ic('upload')}<span>파일 업로드<small class="muted"> · CSV는 테이블, 그림·PDF는 파일</small></span></button>
  <button role="menuitem" onclick="closeMenu();Object.assign(CN,{step:1,kind:'',tested:null,conf:null,name:'',pick:null,pw:''});location.hash='connect'">${ic('db')}<span>DB 연결<small class="muted"> · PostgreSQL · MySQL · SQLite</small></span></button></div></div>`;
// 파일 업로드 — 사이드 패널(Fabric 파일 업로드 창처럼), [업로드] 후 목록에 바로 반영
let UPF = [];
function filePanel() {
  UPF = [];
  panel(`<div class="hd"><h2>파일 업로드</h2></div><div class="bd stack">
    <div class="fld"><label>원본 이름</label><input class="inp" id="uName" placeholder="예) 청구 서류 1차"><span class="help">탐색기에 보일 폴더 이름입니다. 비우면 "업로드한 테이블 · 날짜"처럼 붙습니다. 나중에 바꿀 수 있습니다.</span></div>
    <div class="fld"><label>파일<i></i></label><label class="drop" id="drop">${ic('upload', 24)}<div style="margin-top:8px">파일을 끌어 놓거나 눌러서 선택해 주세요.</div><div class="muted">CSV는 테이블에, 그림·PDF는 파일에 들어갑니다(파일은 문서 읽기에서 읽음).</div><input type="file" id="uFiles" multiple accept=".csv,.jpg,.jpeg,.png,.webp,.pdf" hidden></label>${window.MOCK_DEMO ? `<div class="row" style="margin-top:8px"><button type="button" class="btn ter sm" onclick="mockFiles('csv')">${ic('csv', 16)}예시 CSV 넣기</button><button type="button" class="btn ter sm" onclick="mockFiles('doc')">${ic('pdf', 16)}예시 문서 넣기</button><span class="muted">목업 전용 · 예시 파일을 고른 것처럼 채웁니다</span></div>` : ''}<div id="uList"></div></div></div>
  <div class="ft"><button class="btn out" onclick="closePanel()">취소</button><button class="btn pri" id="uGo" disabled data-tip="파일을 선택해 주세요." onclick="fileUpload(this)">업로드</button></div>`, 'md');
  const show = () => {
    const keep = Object.fromEntries([...document.querySelectorAll('#uList .tn')].map((x) => [x.dataset.f, x.value]));
    $('#uList').innerHTML = UPF.map((f, i) => `<div class="row fitem">${ic(f.name.toLowerCase().endsWith('.csv') ? 'csv' : 'doc', 16)}<span class="sp mono">${esc(f.name)}${f.name.toLowerCase().endsWith('.csv') ? `<input class="inp xs tn" data-f="${esc(f.name)}" aria-label="${esc(f.name)} 테이블 이름" title="테이블 이름" value="${esc(keep[f.name] ?? f.name.replace(/\.csv$/i, '').toLowerCase().replace(/[^a-z0-9가-힣_]+/g, '_'))}" style="margin-top:4px;font-family:inherit">` : ''}</span><span class="muted">${f.size < 1024 ? `${f.size}B` : f.size < 1048576 ? `${(f.size / 1024).toFixed(1)}KB` : `${(f.size / 1048576).toFixed(1)}MB`}</span><button class="ibtn sm" aria-label="${esc(f.name)} 빼기" onclick="UPF.splice(${i},1);this.closest('.bd').dispatchEvent(new Event('files'))">${ic('x', 16)}</button></div>`).join('');
    $('#uGo').disabled = !UPF.length; if (UPF.length) delete $('#uGo').dataset.tip; else $('#uGo').dataset.tip = '파일을 선택해 주세요.';
    NODE.dirty = UPF.length > 0;
  };
  const drop = $('#drop'), fi = $('#uFiles');
  $('#spanel .bd').addEventListener('files', show);
  fi.onchange = () => { UPF = UPF.concat([...fi.files]); show(); };
  drop.ondragover = (e) => { e.preventDefault(); drop.classList.add('on'); };
  drop.ondragleave = () => drop.classList.remove('on');
  drop.ondrop = (e) => { e.preventDefault(); drop.classList.remove('on'); UPF = UPF.concat([...e.dataTransfer.files]); show(); };
}
// 목업 전용 — 예시 데이터의 파일 이름으로 가짜 파일을 넣음(내용은 목업 서버가 예시 데이터로 채움)
function mockFiles(kind) {
  const fx = window.FIXTURES?.fx || {}, src = (fx['/sources'] || []).find((s) => (kind === 'csv' ? s.kind === 'csv' : s.kind === 'doc'));
  const names = kind === 'csv' ? (src?.tables || []).map((t) => `${t.name}.csv`) : (fx['/docs']?.docs || []).filter((d) => d.source_id === src?.id).map((d) => d.file);
  UPF = UPF.concat(names.map((n) => new File(['예시'], n, { type: kind === 'csv' ? 'text/csv' : 'application/pdf' })));
  if (!$('#uName').value) $('#uName').value = src?.name || '';
  $('#spanel .bd').dispatchEvent(new Event('files'));
}
async function fileUpload(btn) {
  await run(btn, '업로드 중', async () => {
    const fd = new FormData(); fd.append('name', $('#uName').value.trim());
    fd.append('tables', JSON.stringify(Object.fromEntries([...document.querySelectorAll('#uList .tn')].map((x) => [x.dataset.f, x.value.trim()])))); UPF.forEach((f) => fd.append('files', f));
    const r = await api('/sources/files', { method: 'POST', body: fd });
    NODE.dirty = false; closePanel(true); toast(`업로드되었습니다. (테이블 ${r.tables?.length || 0}개 · 문서 ${r.docs?.length || 0}건)`);
    if (cur() !== 'source') location.hash = 'source'; else refresh();
  });
}
P.connect = async () => {
  const st = CN.kind ? CN.step : 1, k = DBK.find((x) => x[0] === CN.kind);
  const steps = ['원본 선택', '연결 설정', '테이블 선택', '검토'];
  const wiz = `<div class="wiz">${steps.map((t, i) => `${i ? '<span class="line"></span>' : ''}<span class="${st === i + 1 ? 'on' : st > i + 1 ? 'done' : ''}"><i>${st > i + 1 ? ic('check', 12) : i + 1}</i>${t}</span>`).join('')}</div>`;
  let body = '', foot = '';
  const back = `<button class="btn out" onclick="CN.step=${st - 1};render()">이전</button>`;
  if (st === 1) {
    const tile = (icon, t, d, act) => `<button class="startc" onclick="${act}"><span class="si">${ic(icon, 24)}</span><b>${t}</b><span>${d}</span></button>`;
    body = `<div class="card"><h3>어디에서 가져올까요?</h3><div class="tiles">
      ${DBK.map(([v, t]) => tile('db', t, v === 'sqlite' ? '이 컴퓨터의 DB 파일을 읽기 전용으로 엽니다.' : '회사 DB에 읽기 전용으로 접속합니다.', `CN.kind='${v}';CN.step=2;CN.tested=null;render()`)).join('')}
      ${tile('upload', '파일 업로드', 'CSV는 테이블에, 그림·PDF는 파일에 들어갑니다.', 'filePanel()')}</div></div>`;
    foot = `<button class="btn out" onclick="location.hash='source'">취소</button>`;
  } else if (st === 2) {
    const c = CN.conf || {};
    body = `<div class="card stack"><h3>${ic('db', 16)}${k[1]} 연결 설정</h3>
      <div class="fld"><label>연결 이름<i></i></label><input class="inp cf" id="cName" placeholder="예) 계약 DB" value="${esc(CN.name || '')}"></div>
      <div class="fgrid">${CN.kind === 'sqlite' ? `<div class="fld full"><label>파일 경로<i></i></label><input class="inp cf" id="cPath" placeholder="예) /Users/me/data/shop.db" value="${esc(c.path || '')}"></div>` :
      `<div class="fld"><label>호스트<i></i></label><input class="inp cf" id="cHost" placeholder="예) db.example.com" value="${esc(c.host || '')}"></div>
       <div class="fld"><label>포트<i></i></label><input class="inp cf" id="cPort" placeholder="${k[2]}" value="${esc(c.port || '')}"></div>
       <div class="fld"><label>DB 이름<i></i></label><input class="inp cf" id="cDb" value="${esc(c.dbname || '')}"></div>
       <div class="fld"><label>계정<i></i></label><input class="inp cf" id="cUser" placeholder="예) readonly_user" value="${esc(c.user || '')}"><span class="help">읽기 전용 계정을 권장합니다.</span></div>
       <div class="fld full"><label>비밀번호</label><input class="inp cf" id="cPw" type="password" autocomplete="new-password"><span class="help">비밀번호는 이 컴퓨터의 비밀 파일에만 보관하며 화면에 다시 표시하지 않습니다.</span></div>`}</div>
      ${window.MOCK_DEMO ? `<div><button type="button" class="btn ter sm" onclick="['cName','계약·청구 DB','cHost','db.example.local','cPort','5432','cDb','claims','cUser','readonly_user','cPath','/data/claims.db'].forEach((v,i,a)=>{if(i%2===0&&$('#'+v))$('#'+v).value=a[i+1]})">예시 접속 정보 넣기</button> <span class="muted">목업 전용</span></div>` : ''}
      <div class="row"><button class="btn out sm" id="cTest">${ic('link', 16)}연결 테스트</button><span id="cRes" class="muted">${CN.tested ? `<span class="dotb ok">연결 · 테이블 ${CN.tested.tables.length}개 찾음</span>` : '테스트 전'}</span></div></div>`;
    foot = `${back}<button class="btn pri" id="cNext" ${CN.tested ? '' : 'disabled data-tip="연결 테스트를 완료한 후 진행할 수 있습니다."'}>다음</button>`;
  } else if (st === 3) {
    const t = CN.tested.tables;
    body = `<div class="lc"><span class="cnt">테이블 ${t.length}개 · <b id="cPickN">${CN.pick?.length || 0}</b>개 선택</span><span class="sp"></span><label class="chk"><input type="checkbox" id="cAll">전체 선택</label></div>
      <div class="card flat" style="max-height:480px;overflow:auto"><table class="t"><thead><tr><th style="width:56px"></th><th>테이블</th><th class="num">행</th></tr></thead><tbody>
      ${t.map((x) => `<tr><td><label class="chk"><input type="checkbox" class="cT" aria-label="${esc(x.name)} 선택" value="${esc(x.name)}" ${CN.pick?.includes(x.name) ? 'checked' : ''}></label></td><td class="mono">${esc(x.name)}</td><td class="num">${x.rows == null ? '-' : x.rows.toLocaleString()}</td></tr>`).join('')}</tbody></table></div>
      <p class="muted" style="margin-top:8px">테이블마다 최대 50,000행을 이 컴퓨터로 복사해 옵니다.</p>`;
    foot = `${back}<button class="btn pri" id="cNext3" ${CN.pick?.length ? '' : 'disabled data-tip="가져올 테이블을 선택해 주세요."'}>다음</button>`;
  } else {
    const rows = Object.fromEntries(CN.tested.tables.map((x) => [x.name, x.rows]));
    body = `<div class="card"><h3>검토</h3><dl class="dl"><dt>연결 이름</dt><dd>${esc(CN.name)}</dd><dt>유형</dt><dd>${k[1]}</dd><dt>위치</dt><dd class="mono">${esc(CN.conf.path || `${CN.conf.host}:${CN.conf.port || k[2]}/${CN.conf.dbname}`)}</dd></dl></div>
      <div class="sec-t sm" style="margin-top:24px">가져올 테이블 ${CN.pick.length}개 <small>빼고 싶은 테이블은 지울 수 있습니다.</small></div>
      <div class="card flat"><table class="t"><thead><tr><th>테이블</th><th class="num">행</th><th></th></tr></thead><tbody>${CN.pick.map((n, i) => `<tr><td class="mono">${esc(n)}</td><td class="num">${rows[n] == null ? '-' : rows[n].toLocaleString()}</td><td class="num"><button class="ibtn sm" aria-label="${esc(n)} 빼기" ${CN.pick.length > 1 ? '' : 'disabled data-tip="테이블이 하나 이상 있어야 합니다."'} onclick="CN.pick.splice(${i},1);render()">${ic('x', 16)}</button></td></tr>`).join('')}</tbody></table></div>`;
    foot = `${back}<button class="btn pri" id="cMake" ${lock()}>만들기</button>`;
  }
  CRUMB = [['데이터 원본', '#source'], ['DB 연결']];
  return `<div class="ph"><div class="t"><h1>DB 연결</h1><p>회사 DB를 읽기 전용으로 연결하고, 가져올 테이블을 고릅니다.</p></div></div>
  ${wiz}<div style="max-width:960px">${body}</div>${pageFoot(foot)}`;
};
function readConf() {
  const v = (id) => ($(id) ? $(id).value.trim() : '');
  CN.name = v('#cName');
  CN.conf = CN.kind === 'sqlite' ? { kind: 'sqlite', path: v('#cPath') } : { kind: CN.kind, host: v('#cHost'), port: v('#cPort'), dbname: v('#cDb'), user: v('#cUser') };
  if ($('#cPw')) CN.pw = $('#cPw').value;
}
function bindConnect() {
  document.querySelectorAll('.cf').forEach((el) => (el.oninput = () => { NODE.dirty = true; if (CN.tested) { CN.tested = null; $('#cRes').textContent = '테스트 전'; const n = $('#cNext'); n.disabled = true; n.dataset.tip = '연결 테스트를 완료한 후 진행할 수 있습니다.'; } }));
  if ($('#cTest')) $('#cTest').onclick = (e) => run(e.currentTarget, '확인 중', async () => { readConf(); if (!CN.name) { toast('연결 이름을 입력해 주세요.', true); return; } CN.tested = await post('/sources/db/test', { conf: CN.conf, password: CN.pw }); CN.pick = null; render(); });
  if ($('#cNext')) $('#cNext').onclick = () => { readConf(); CN.step = 3; render(); };
  const syncPick = () => { CN.pick = [...document.querySelectorAll('.cT:checked')].map((c) => c.value); $('#cPickN').textContent = CN.pick.length; const n = $('#cNext3'); n.disabled = !CN.pick.length; if (CN.pick.length) delete n.dataset.tip; else n.dataset.tip = '가져올 테이블을 선택해 주세요.'; };
  document.querySelectorAll('.cT').forEach((c) => (c.onchange = syncPick));
  if ($('#cAll')) $('#cAll').onchange = (e) => { document.querySelectorAll('.cT').forEach((c) => (c.checked = e.target.checked)); syncPick(); };
  if ($('#cNext3')) $('#cNext3').onclick = () => { CN.step = 4; render(); };
  if ($('#cMake')) $('#cMake').onclick = (e) => run(e.currentTarget, '가져오는 중', async () => {
    await post('/sources/db', { name: CN.name, conf: CN.conf, password: CN.pw, tables: CN.pick });
    toast(`DB가 연결되었습니다. (테이블 ${CN.pick.length}개)`); NODE.dirty = false;
    Object.assign(CN, { step: 1, kind: '', tested: null, conf: null, name: '', pick: null, pw: '' }); location.hash = 'source';
  });
}

// 온톨로지 설계
let ONTO = null;
const lab = (t) => (ONTO?.objects.find((o) => o.name === t) || {}).label || t;
function goldPaths(gold) {
  const run = gold.filter((g) => g.run_at);
  if (!gold.length) return empty('아직 골든 질문이 없습니다.', '', `<button class="btn out sm" onclick="location.hash='golden'">골든 질문으로 이동</button>`, true, 'star');
  if (!run.length) return empty('골든 질문을 아직 실행하지 않았습니다.', '', `<button class="btn out sm" onclick="location.hash='golden'">골든 질문으로 이동</button>`, true, 'star');
  return `<table class="t"><thead><tr><th>골든 질문</th><th>결과</th><th></th></tr></thead><tbody>${run.map((g) => `<tr><td>${esc(g.q)}</td><td>${okTag(g.ok)}</td><td class="num">${g.ask_id ? `<button class="btn xs out" onclick="openAsk(${g.ask_id})">탄 경로</button>` : ''}</td></tr>`).join('')}</tbody></table>`;
}

// 문서 읽기
let DOCS = null, RV = [], rvWhy = '', readTab = 'fields';
P.read = async () => {
  [DOCS, RV] = await Promise.all([get('/docs'), get('/review')]);
  const tabs = [['fields', '읽을 칸', DOCS.fields.length], ['docs', '문서', DOCS.docs.length], ['review', '읽은 값 검수', RV.length], ['search', '본문 검색', DOCS.chunks]];
  let body = '';
  if (readTab === 'fields') {
    setTimeout(fieldSug);
    body = `<div class="alert info" style="margin-bottom:16px">${ic('info')}<div>읽을 칸이 없어도 <b>문서 종류와 본문</b>은 읽습니다(본문 검색 · 데이터 에이전트 답에 씀). 값을 테이블 열로 받아 다른 테이블과 이으려면 칸을 정해 주세요. 한 번 읽은 뒤에는 AI가 본문을 보고 칸을 추천합니다.</div></div>
    <div class="card" id="fSug" style="margin-bottom:16px"><h3>${ic('robot', 16)}AI 추천 칸 <small>본문을 보고 고른 후보 · 누르면 추가됩니다</small></h3><p class="muted" style="margin:0">추천을 불러오는 중입니다.</p></div>
    <div class="lc"><span class="cnt">총 ${DOCS.fields.length}칸</span><span class="sp"></span><button class="btn out sm" ${lock()} onclick="fieldModal()">${ic('plus', 16)}읽을 칸 직접 추가</button></div>
    <div class="card flat">${DOCS.fields.length ? `<table class="t"><thead><tr><th>표시 이름 · 열 이름</th><th>설명(AI에게 전달)</th><th></th></tr></thead><tbody>
      ${DOCS.fields.map((f) => `<tr><td>${esc(f.label)}<div class="muted mono">${esc(f.name)}</div></td><td class="r">${esc(f.desc)}</td><td class="num"><button class="btn xs out" ${lock()} onclick="delField('${esc(f.name)}')">삭제</button></td></tr>`).join('')}</tbody></table>`
      : empty('아직 읽을 칸이 없습니다.', '위 추천 칸을 누르거나 직접 추가해 주세요. 칸마다 뜻 · 형식을 적어야 AI가 정확히 읽습니다.', '', true, 'doc')}</div>`;
  } else if (readTab === 'docs') {
    const unread = DOCS.docs.filter((d) => !d.read_at).length;
    body = `<div class="lc"><span class="cnt">총 ${DOCS.docs.length}건 · 읽지 않음 ${unread}건</span><span class="sp"></span>
      <button class="btn pri sm" ${DOCS.docs.length ? lock() : 'disabled data-tip="문서를 업로드한 후 실행할 수 있습니다."'} onclick="readDocs(this)">${ic('play', 16)}읽기 실행</button></div>
    ${DOCS.docs.length && !DOCS.fields.length ? `<div class="alert info" style="margin-bottom:16px">${ic('info')}<div>읽을 칸이 없으면 <b>본문만</b> 읽어 본문 검색에 씁니다. 값으로 다른 테이블과 이으려면 읽을 칸을 추가해 주세요.</div></div>` : ''}
    ${DOCS.docs.length ? `<div class="dgrid">${DOCS.docs.map((d) => `<button class="dthumb" onclick="openDoc('${esc(d.id)}')"><span class="tz" role="button" tabindex="0" aria-label="${esc(d.id)} 크게 보기" data-tip="크게 보기" onclick="event.stopPropagation();viewImg('${esc(d.id)}')">${ic('search', 16)}</span><img loading="lazy" src="${imgUrl(d.id)}" alt=""><span class="id">${esc(d.id)}</span>
      <span class="row" style="gap:4px;margin-top:4px">${d.pages > 1 ? `<span class="b">${d.pages}쪽</span>` : ''}${d.err ? '<span class="b bad">실패</span>' : d.read_at ? `<span class="b ok">${d.filled}칸</span>${d.chunks ? `<span class="b">본문 ${d.chunks}</span>` : ''}` : '<span class="b">읽기 전</span>'}${d.rot ? `<span class="b info" data-tip="누워 있어서 ${d.rot}° 돌려 다시 읽었습니다.">자동 회전</span>` : ''}${d.lying ? '<span class="b warn">방향 오류</span>' : ''}${d.review ? `<span class="b bad">검수 ${d.review}</span>` : ''}</span></button>`).join('')}</div>`
    : `<div class="card">${empty('아직 문서가 없습니다.', '데이터 원본에서 문서(그림·PDF)를 업로드해 주세요.', `<button class="btn pri" ${lock()} onclick="filePanel()">파일 업로드</button>`, false, 'doc')}</div>`}`;
  } else if (readTab === 'search') {
    setTimeout(searchEx);
    const objs = (await get('/onto')).objects.filter((o) => o.name !== 'doc_extract');
    body = `<div class="alert info" style="margin-bottom:16px">${ic('info')}<div>먼저 고른 대상에 이어진 문서만 남기고, 그 안에서 뜻이 가까운 본문을 고릅니다.${DOCS.search_mode !== '검색 전' ? ` 지금 방식: <b>${esc(DOCS.search_mode)}</b>` : ''}</div></div>
    ${DOCS.chunks ? `<div id="sEx" style="margin:-4px 0 12px"></div><div class="lc"><div class="search">${ic('search')}<input class="inp" id="sQ" placeholder="검색어 입력" onkeydown="if(event.key==='Enter')docSearch()"></div>
      <select class="inp" id="sObj" onchange="const v=$('#sVal');v.disabled=!this.value;v.value='';v.placeholder=this.value?(this.selectedOptions[0].dataset.key+' 입력'):'먼저 대상을 선택'"><option value="">좁히기 | 전체 문서</option>${objs.map((o) => `<option value="${esc(o.name)}" data-key="${esc(o.key)}">좁히기 | ${esc(o.label)}</option>`).join('')}</select>
      <div class="search">${ic('filter')}<input class="inp" id="sVal" disabled placeholder="먼저 대상을 선택" onkeydown="if(event.key==='Enter')docSearch()"></div><span class="muted">Enter로 검색</span></div><div id="sOut"></div>`
      : `<div class="card">${empty('아직 본문이 없습니다.', '문서 탭에서 읽기를 실행하면 본문이 쪽마다 저장됩니다.', `<button class="btn out sm" onclick="readTab='docs';render()">문서 탭으로 이동</button>`, false, 'doc')}</div>`}`;
  } else {
    const reasons = [...new Set(RV.flatMap((r) => r.why.map((w) => w.replace(/\(.*\)/, '').replace(/^.*\.(.*)에 없는 값$/, '이어 둔 테이블에 없는 값').trim())))];
    const list = RV.filter((r) => !rvWhy || r.why.some((w) => w.includes(rvWhy.replace('이어 둔 테이블에 없는 값', '없는 값'))));
    body = `<div class="alert info" style="margin-bottom:16px">${ic('info')}<div>확신도가 낮거나, 누운 문서이거나, <b>이어 둔 테이블에 없는 값</b>을 보여 줍니다. 확신도는 틀린 값에도 높게 나올 수 있습니다.</div></div>
    <div class="lc"><select class="inp" onchange="rvWhy=this.value;render()"><option value="">걸린 이유 | 전체</option>${reasons.map((x) => `<option ${rvWhy === x ? 'selected' : ''}>${esc(x)}</option>`).join('')}</select>${rvWhy ? resetBtn("rvWhy=''") : ''}<span class="cnt">총 ${list.length}칸</span><span class="sp"></span></div>
    <div class="card flat">${list.length ? `<table class="t"><thead><tr><th>문서</th><th>칸</th><th>읽은 값</th><th>확신도</th><th>걸린 이유</th><th>추천 값</th></tr></thead><tbody>
      ${list.map((r) => `<tr class="click" onclick="openReview('${esc(r.doc_id)}','${esc(r.field)}')"><td class="mono">${esc(r.doc_id)}</td><td>${esc(r.label)}</td><td class="mono">${esc(r.value)}</td><td class="r">${r.conf == null ? '-' : r.conf.toFixed(2)}</td><td>${r.why.map((w) => `<span class="b warn">${esc(w)}</span>`).join(' ')}</td><td class="mono">${esc(r.fix || '-')}</td></tr>`).join('')}</tbody></table>`
      : empty('검수할 칸이 없습니다.', '', '', true, 'check')}</div>`;
  }
  return `<div class="ph"><div class="t"><h1>문서 읽기</h1><p>문서(그림·PDF)에서 정한 칸을 AI가 읽어 <b>읽은 값</b> 엔터티 형식으로 추가합니다. 틀릴 만한 칸은 사람이 검수합니다.</p></div></div>
  <div class="tabs">${tabs.map(([k, t, n]) => `<button class="${readTab === k ? 'on' : ''}" onclick="readTab='${k}';render()">${t}<span>${n}</span></button>`).join('')}</div>${body}`;
};
// AI 추천 칸 — 이미 읽은 본문을 보고 서버가 후보를 냄(같은 문서면 저장해 둔 추천을 씀). 칩을 누르면 바로 추가
let FSUG = [];
async function fieldSug(refresh = false) {
  const el = $('#fSug'); if (!el) return;
  if (refresh) el.querySelector('p, .chips')?.replaceWith(Object.assign(document.createElement('p'), { className: 'muted', textContent: '추천을 다시 만드는 중입니다(AI · 몇 초).' }));
  let r; try { r = await get('/fields/suggest' + (refresh ? '?refresh=1' : '')); } catch (e) { r = { items: [], why: e.message }; }
  FSUG = r.items; if (!$('#fSug')) return;
  $('#fSug').innerHTML = `<h3>${ic('robot', 16)}AI 추천 칸 <small>본문을 보고 고른 후보 · 누르면 추가됩니다</small><span class="sp"></span>${FSUG.length ? `<button class="btn out sm" ${lock()} onclick="fieldAdd(FSUG)">모두 추가</button>` : ''}<button class="btn ter sm" ${lock()} onclick="fieldSug(true)">${ic('refresh', 16)}다시 추천</button></h3>
    ${FSUG.length ? `<div class="chips" style="justify-content:flex-start;margin-top:0">${FSUG.map((x, i) => `<button type="button" ${lock()} data-tip="${esc(x.desc)}${x.example ? ` · 예: ${esc(x.example)}` : ''}${x.types?.length ? ` · ${esc(x.types.join(', '))}` : ''}${x.link ? ` · 이어질 테이블: ${esc(x.link)}` : ''}" onclick="fieldAdd([FSUG[${i}]])">${ic('plus', 12)} ${esc(x.label)}${x.link ? ' <span class="b info">이어짐</span>' : ''}</button>`).join('')}</div>
      <p class="muted" style="margin:8px 0 0">"이어짐" = 다른 테이블에 같은 뜻의 열이 있어, 읽은 값으로 그 테이블과 이을 수 있는 칸입니다. 칸에 마우스를 올리면 뜻 · 형식 · 예시가 보입니다.</p>`
      : `<p class="muted" style="margin:0">${esc(r.why || '추천할 칸이 더 없습니다.')}</p>`}`;
}
async function fieldAdd(items) {
  if (!items?.length) return;
  const r = await post('/fields/bulk', { items });
  toast(`읽을 칸 ${r.added}개가 추가되었습니다. 문서 탭에서 읽기를 실행하면 값이 채워집니다.`); refresh();
}
function fieldModal() {
  formModal('읽을 칸 추가', `<div class="fld"><label>표시 이름(화면에 보이는 이름)<i></i></label><input class="inp" id="fL" placeholder="예) 환자 성명"></div>
    <div class="fld" style="margin-top:16px"><label>열 이름(영문 · 테이블 열)<i></i></label><input class="inp" id="fN" placeholder="예) patient_name"><span class="help">문서에서 읽은 값 테이블(doc_extract)의 열 이름이 됩니다. 다른 테이블과 이으려면 그 테이블의 열 이름과 똑같이 적어 주세요(예: disease_code).</span></div>
    <div class="fld" style="margin-top:16px"><label>설명(AI에게 전달)<i></i></label><textarea class="inp" id="fD" rows="3" placeholder="예) 진단서에 적힌 환자 이름. 한글 실명"></textarea><span class="help">뜻과 형식을 적을수록 정확히 읽습니다(예: 실제 진단일, 발급일 아님, YYYY-MM-DD).</span></div>`, '추가', async () => {
    await post('/fields', { name: $('#fN').value.trim(), label: $('#fL').value.trim(), desc: $('#fD').value.trim() }); toast('읽을 칸이 추가되었습니다.'); refresh();
  });
}
async function delField(n) {
  if (!(await confirmBox({ title: '읽을 칸을 삭제하시겠습니까?', body: '이미 읽은 값은 다음 읽기 때까지 남습니다.', ok: '삭제', danger: true }))) return;
  await del('/fields/' + encodeURIComponent(n)); toast('읽을 칸이 삭제되었습니다.'); refresh();
}
async function readDocs(btn) {
  const human = DOCS.docs.length;
  if (!(await confirmBox({ title: `문서 ${human}건 읽기를 실행하시겠습니까?`, body: '사람이 고친 값은 그대로 유지됩니다. 문서 수에 따라 1분 이상 걸릴 수 있습니다.' }))) return;
  await run(btn, '읽는 중', async () => { const r = await post('/read'); toast(`문서 ${r.docs}건 읽기가 완료되었습니다. (${r.secs}초${r.failed ? ` · 실패 ${r.failed}건` : ''})`); await refresh(); });
}
// ── 문서 크게 보기 — 화면 가득(DS 풀팝업 모양), 확대 · 축소 · 맞춤 · 돌려 보기 · 끌어서 옮기기 · 쪽 넘기기. Esc로 닫음 ──
const VW = { id: '', page: 1, np: 1, z: 1, r: 0, x: 0, y: 0 };
function viewImg(id, page = 1) {
  const d = (DOCS?.docs || SDOCS || []).find((x) => x.id === id) || {};
  Object.assign(VW, { id, page, np: Math.min(d.pages || 1, 10), z: 1, r: 0, x: 0, y: 0 });
  let v = $('#viewer');
  if (!v) { v = document.createElement('div'); v.id = 'viewer'; v.className = 'viewer'; v.setAttribute('role', 'dialog'); v.setAttribute('aria-label', '문서 크게 보기'); document.body.appendChild(v); }
  v.innerHTML = `<div class="vbox"><div class="vh"><b class="mono">${esc(id)}</b>${VW.np > 1 ? `<span class="row" style="gap:4px"><button class="ibtn sm" aria-label="이전 쪽" onclick="vwPage(-1)">${ic('chev', 16).replace('<svg', '<svg style="transform:rotate(180deg)"')}</button><span class="muted" id="vwPg"></span><button class="ibtn sm" aria-label="다음 쪽" onclick="vwPage(1)">${ic('chev', 16)}</button></span>` : ''}<span class="sp"></span>
    <button class="btn out sm" onclick="vwZoom(1/1.25)" aria-label="축소">−</button><span class="muted" id="vwZ" style="min-width:48px;text-align:center"></span><button class="btn out sm" onclick="vwZoom(1.25)" aria-label="확대">+</button>
    <button class="btn out sm" onclick="Object.assign(VW,{z:1,x:0,y:0});vwApply()">맞춤</button><button class="btn out sm" onclick="VW.r=(VW.r+90)%360;vwApply()">${ic('refresh', 16)}돌려 보기</button><button class="ibtn" aria-label="닫기" onclick="vwClose()">${ic('x', 20)}</button></div>
    <div class="vbd" id="vwBd"><img id="vwImg" alt="${esc(id)}" draggable="false"></div><div class="vft muted">휠로 확대 · 끌어서 옮기기 · 두 번 눌러 2배 · Esc로 닫기</div></div>`;
  v.classList.add('on');
  const bd = $('#vwBd'), im = $('#vwImg');
  bd.onwheel = (e) => { e.preventDefault(); vwZoom(e.deltaY < 0 ? 1.15 : 1 / 1.15); };
  im.ondblclick = () => { VW.z = VW.z > 1.5 ? 1 : 2; if (VW.z === 1) { VW.x = 0; VW.y = 0; } vwApply(); };
  let drag = null;
  bd.onpointerdown = (e) => { drag = { x: e.clientX - VW.x, y: e.clientY - VW.y }; bd.setPointerCapture(e.pointerId); bd.classList.add('grab'); };
  bd.onpointermove = (e) => { if (!drag) return; VW.x = e.clientX - drag.x; VW.y = e.clientY - drag.y; vwApply(); };
  bd.onpointerup = () => { drag = null; bd.classList.remove('grab'); };
  vwLoad();
}
function vwLoad() { $('#vwImg').src = imgUrl(VW.id, VW.page); if ($('#vwPg')) $('#vwPg').textContent = `${VW.page} / ${VW.np}쪽`; vwApply(); }
function vwPage(d) { const p = VW.page + d; if (p < 1 || p > VW.np) return; Object.assign(VW, { page: p, x: 0, y: 0 }); vwLoad(); }
function vwZoom(f) { VW.z = Math.min(8, Math.max(0.25, VW.z * f)); vwApply(); }
function vwApply() { const im = $('#vwImg'); if (!im) return; im.style.transform = `translate(${VW.x}px, ${VW.y}px) scale(${VW.z}) rotate(${VW.r}deg)`; $('#vwZ').textContent = `${Math.round(VW.z * 100)}%`; }
function vwClose() { $('#viewer')?.classList.remove('on'); }
document.addEventListener('keydown', (e) => { if (!$('#viewer')?.classList.contains('on')) return; if (e.key === 'Escape') { e.stopImmediatePropagation(); vwClose(); } if (e.key === 'ArrowRight') vwPage(1); if (e.key === 'ArrowLeft') vwPage(-1); }, true);

// 문서 그림 칸 — [크게 보기]는 패널을 넓혀 그림만 키움(값은 계속 보임), [화면 가득]은 풀팝업
let DOCW = false;
const docFig = (id, page, again) => `<div class="docfig"><img class="docimg big" src="${imgUrl(id, page)}" alt="${esc(id)} ${page}쪽" onclick="${again}">
  <div class="zbs"><button class="zb" onclick="DOCW=!DOCW;${again}">${ic(DOCW ? 'x' : 'search', 16)}${DOCW ? '작게 보기' : '크게 보기'}</button><button class="zb" onclick="viewImg('${esc(id)}',${page})" aria-label="화면 가득 보기" data-tip="화면 가득 · 확대 · 돌려 보기">${ic('side', 16)}</button></div></div>`;
async function openDoc(id, page = 1) {
  const [vals, txt] = await Promise.all([get('/docs/' + encodeURIComponent(id) + '/values'), get('/docs/' + encodeURIComponent(id) + '/text')]);
  if (!DOCS || !DOCS.docs.some((x) => x.id === id)) DOCS = await get('/docs');
  const d = DOCS.docs.find((x) => x.id === id), np = Math.min(d.pages || 1, 10);
  const ptxt = txt.filter((t) => t.page === page).map((t) => t.text);
  panel(`<div class="hd"><h2>${esc(id)}</h2><button class="ibtn" aria-label="닫기" onclick="closePanel()">${ic('x', 20)}</button></div><div class="bd">
    ${np > 1 ? `<div class="pager"><button class="ibtn" aria-label="이전 쪽" ${page > 1 ? '' : 'disabled'} onclick="openDoc('${esc(id)}',${page - 1})">${ic('chev', 20).replace('<svg', '<svg style="transform:rotate(180deg)"')}</button><span class="muted">${page} / ${np}쪽</span><button class="ibtn" aria-label="다음 쪽" ${page < np ? '' : 'disabled'} onclick="openDoc('${esc(id)}',${page + 1})">${ic('chev', 20)}</button></div>` : ''}
    <div class="gdoc ${DOCW ? 'w' : ''}"><div>${docFig(id, page, `openDoc('${esc(id)}',${page})`).replace(`onclick="openDoc('${esc(id)}',${page})">`, `onclick="DOCW=!DOCW;openDoc('${esc(id)}',${page})">`)}</div>
    <div><dl class="dl"><dt>종류</dt><dd>${esc(d.doc_type || '-')}</dd><dt>읽은 일시</dt><dd>${fmtT(d.read_at)}</dd>${d.err ? `<dt>오류</dt><dd style="color:var(--bad)">${esc(d.err)}</dd>` : ''}</dl>
    <div class="sec-t sm" style="margin-top:16px">읽은 값 <small>doc_extract 테이블의 이 문서 줄</small></div><table class="t"><thead><tr><th>칸</th><th>값</th><th>확신도</th></tr></thead><tbody>${vals.map((v) => `<tr><td>${esc((DOCS.fields.find((f) => f.name === v.field) || {}).label || v.field)}</td><td class="mono">${esc(v.value || '-')}</td><td class="r">${v.by === '사람' ? '<span class="b ok">사람</span>' : v.conf == null ? '-' : v.conf.toFixed(2)}</td></tr>`).join('') || `<tr><td colspan="3" class="r">${d.read_at ? '읽을 칸이 없어 값은 없습니다. 본문만 읽었습니다.' : '아직 읽지 않았습니다.'}</td></tr>`}</tbody></table>
    ${ptxt.length ? `<details class="sqlbox" open style="margin-top:16px"><summary>${page}쪽 본문(AI가 읽은 글자)</summary><div class="doctext">${esc([...new Set(ptxt)].join('\n…\n'))}</div></details>` : ''}</div></div></div>`, DOCW ? 'xxl' : 'xl');
}
function openReview(doc, field, page = 1) {
  const r = RV.find((x) => x.doc_id === doc && x.field === field);
  const d = (DOCS?.docs || []).find((x) => x.id === doc) || {}, np = Math.min(d.pages || 1, 10);
  panel(`<div class="hd"><h2>읽은 값 검수 · ${esc(doc)}</h2></div><div class="bd"><div class="gdoc ${DOCW ? 'w' : ''}">
    <div>${np > 1 ? `<div class="pager"><button class="ibtn" aria-label="이전 쪽" ${page > 1 ? '' : 'disabled'} onclick="openReview('${esc(doc)}','${esc(field)}',${page - 1})">${ic('chev', 20).replace('<svg', '<svg style="transform:rotate(180deg)"')}</button><span class="muted">${page} / ${np}쪽</span><button class="ibtn" aria-label="다음 쪽" ${page < np ? '' : 'disabled'} onclick="openReview('${esc(doc)}','${esc(field)}',${page + 1})">${ic('chev', 20)}</button></div>` : ''}
    ${docFig(doc, page, `openReview('${esc(doc)}','${esc(field)}',${page})`).replace(`onclick="openReview('${esc(doc)}','${esc(field)}',${page})">`, `onclick="DOCW=!DOCW;openReview('${esc(doc)}','${esc(field)}',${page})">`)}</div>
    <div><dl class="dl"><dt>칸</dt><dd>${esc(r.label)}</dd><dt>읽은 값</dt><dd class="mono">${esc(r.value)}</dd><dt>확신도</dt><dd>${r.conf == null ? '-' : r.conf.toFixed(2)}</dd><dt>걸린 이유</dt><dd>${r.why.map((w) => `<span class="b warn">${esc(w)}</span>`).join(' ')}</dd></dl>
    <div class="fld" style="margin-top:24px"><label>값<i></i></label><input class="inp mono" id="rvV" value="${esc(r.fix || r.value)}"><span class="help">${r.fix ? `추천 값: 이어 둔 테이블에서 가장 비슷한 값 "${esc(r.fix)}"` : '문서를 보고 맞는 값을 입력해 주세요.'}</span></div></div></div></div>
    <div class="ft"><button class="btn out" id="rvOk" ${lock()}>읽은 값 확인</button><button class="btn pri" id="rvSave" ${lock()}>저장</button></div>`, DOCW ? 'xxl' : 'xl');
  const save = async (v, msg) => { await post('/review/fix', { doc_id: doc, field, value: v }); closePanel(); toast(msg); refresh(); };
  $('#rvOk').onclick = () => save(r.value, '읽은 값이 확인되었습니다.');
  $('#rvSave').onclick = () => save($('#rvV').value.trim(), '읽은 값이 수정되었습니다.');
}

// 규칙
let RULES = [];
// 규칙 — Fabric 흐름: 목록 페이지(검색 · 엔터티 형식 필터) → 규칙을 누르면 상세 페이지, 새 규칙은 전체 페이지
//  새 규칙은 중지 상태로 저장되고 [저장 후 시작]이나 상세의 [시작]으로 켬(Fabric Activator처럼)
let RQ = { q: '', obj: '' }, RNEW = null;
P.rules = async () => {
  [RULES, ONTO] = await Promise.all([get('/rules'), get('/onto')]);
  const q = hq();
  if (q.get('id')) return ruleDetail(+q.get('id'));
  if (q.get('new')) return ruleNewPage(q.get('new'));
  const list = RULES.filter((r) => (!RQ.q || r.name.includes(RQ.q) || r.text.includes(RQ.q)) && (!RQ.obj || r.cond.start === RQ.obj));
  const objs = [...new Set(RULES.map((r) => r.cond.start).filter(Boolean))];
  const starts = [...new Set(RULES.filter((r) => r.on_ && r.check.ok).map((r) => r.cond.start))];
  const newBtn = (t) => `<button class="btn pri" ${ST.objects ? lock() : 'disabled data-tip="온톨로지 설계에서 엔터티 형식을 만든 후 규칙을 만들 수 있습니다."'} onclick="location.hash='rules?new=판단'">${ic('plus')}${t}</button>`;
  return `<div class="ph"><div class="t"><h1>규칙</h1><p><b>한 건씩 보고 해당/아님을 판정합니다</b>(예: 가입 후 90일 안 청구면 확인 필요). 문장으로 쓰면 AI가 조건으로 바꾸고, 판정은 프로그램이 조건대로 합니다. 여러 건을 세거나 합치는 것은 메트릭입니다.</p></div>${RULES.length ? newBtn('새 규칙') : ''}</div>
  ${RULES.length ? `<div class="lc"><div class="search">${ic('search')}<input class="inp" placeholder="규칙 이름으로 검색" value="${esc(RQ.q)}" onkeydown="if(event.key==='Enter'){RQ.q=this.value;render()}"></div>
    <select class="inp" onchange="RQ.obj=this.value;render()"><option value="">시작 엔터티 형식 | 전체</option>${objs.map((o) => `<option value="${esc(o)}" ${RQ.obj === o ? 'selected' : ''}>시작 엔터티 형식 | ${esc(lab(o))}</option>`).join('')}</select>
    ${RQ.q || RQ.obj ? resetBtn("RQ={q:'',obj:''}") : ''}<span class="cnt">총 ${list.length}개</span></div>
  <div class="card flat">${list.length ? `<table class="t"><thead><tr><th>규칙</th><th>종류</th><th>시작 엔터티 형식</th><th>상태</th><th>점검</th></tr></thead><tbody>
    ${list.map((r) => `<tr class="click" onclick="location.hash='rules?id=${r.id}'"><td>${esc(r.name)}<div class="muted">${esc(r.text).slice(0, 80)}</div></td><td class="r nw">${esc(r.kind)}${r.kind === '분류' ? ` <span class="muted">${r.ord}번째</span>` : ''}</td><td class="r">${esc(lab(r.cond.start))}</td>
      <td>${r.on_ ? '<span class="dotb ok">실행 중</span>' : '<span class="dotb">중지</span>'}</td><td>${r.check.ok ? '<span class="tag ok">실행 가능</span>' : `<span class="tag bad" data-tip="${esc(r.check.why.join(' · '))}">고칠 것 ${r.check.why.length}개</span>`}</td></tr>`).join('')}</tbody></table>`
    : empty('조건에 맞는 규칙이 없습니다.', '검색어 또는 필터를 조정해 주세요.', resetBtn("RQ={q:'',obj:''}"), true, 'search')}</div>`
  : `<div class="card">${empty('아직 규칙이 없습니다.', '업무 기준을 문장으로 적으면 AI가 조건으로 바꿉니다.', newBtn('규칙 만들기') + (can('build') ? await exChips('rule', 'exRuleNew') : ''), false, 'rule')}</div>`}
  <p class="muted" style="margin:16px 0 0">건수·합계·날짜 차이가 필요한 규칙은 먼저 <button class="link" onclick="location.hash='design'">온톨로지 설계</button>에서 엔터티 형식에 계산 속성을 만들어 주세요.</p>
  ${starts.length ? `<div class="card" style="margin-top:24px"><h3>전체 판정 <small>모든 건에 실행 중인 규칙을 돌려 결과를 판정 결과 엔터티 형식으로 저장합니다.</small></h3>
    <div class="row" style="align-items:flex-end"><div class="fld" style="width:240px"><label>시작 엔터티 형식</label><select class="inp" id="raStart">${starts.map((x) => `<option value="${esc(x)}">${esc(lab(x))}</option>`).join('')}</select></div><button class="btn out" ${lock()} onclick="runAll(this)">${ic('play', 16)}전체 판정 실행</button></div><div id="raOut"></div></div>` : ''}`;
};
const plab = (o, c) => (ONTO?.objects.find((x) => x.name === o)?.props || []).find((p) => p.col === c)?.label || c;
function condText(c) {
  if (ONTO) return `<span class="k">시작</span> ${esc(lab(c.start))}\n` + (c.when || []).map((w, i) => `<span class="k">${i ? '그리고' : '조건  '}</span> ${esc(lab(w.obj))} ${esc(plab(w.obj, w.col))} ${esc(w.op)} ${w.ref ? esc(lab(w.ref.obj) + ' ' + plab(w.ref.obj, w.ref.col)) : esc(JSON.stringify(w.value))}`).join('\n') + `\n<span class="k">결과</span> ${esc(c.then)}`;
  return `<span class="k">시작</span> ${esc(c.start)}\n` + (c.when || []).map((w, i) => `<span class="k">${i ? 'AND ' : 'IF  '}</span> ${esc(w.obj)}.${esc(w.col)} ${esc(w.op)} ${w.ref ? esc(w.ref.obj + '.' + w.ref.col) : esc(JSON.stringify(w.value))}`).join('\n') + `\n<span class="k">THEN</span> ${esc(c.then)}`;
}
// 규칙이 쓰는 개념(엔터티 형식 · 속성) — Fabric 규칙의 연결된 개념처럼 보여 줌
function ruleConcepts(c) {
  const objs = new Set([c.start]), props = new Set();
  (c.when || []).forEach((w) => { objs.add(w.obj); props.add(`${w.obj}|${w.col}`); if (w.ref) { objs.add(w.ref.obj); props.add(`${w.ref.obj}|${w.ref.col}`); } });
  return `<div class="row">${[...objs].filter(Boolean).map((o) => `<span class="tag" ${objOf2(o) ? `style="cursor:pointer" onclick="dzOpen('${esc(o)}')"` : ''}>${ic('cube', 12)}&nbsp;${esc(lab(o))}</span>`).join('')}${[...props].map((x) => { const [o, col] = x.split('|'); return `<span class="tag">${esc(lab(o))} · ${esc(plab(o, col))}</span>`; }).join('')}</div>`;
}
const objOf2 = (n) => ONTO?.objects.some((o) => o.name === n);
function ruleDetail(id) {
  const r = RULES.find((x) => x.id === id);
  if (!r) { history.replaceState(null, '', '#rules'); toast('규칙을 찾을 수 없습니다. 삭제되었을 수 있습니다.', true); return P.rules(); }
  CRUMB = [['규칙', '#rules'], [r.name]];
  return `<div class="ph"><div class="t"><h1>${esc(r.name)} ${r.on_ ? '<span class="b ok">실행 중</span>' : '<span class="b">중지</span>'}</h1><p>${esc(r.kind)} 규칙${r.kind === '분류' ? ` · 위에서 ${r.ord}번째` : ''} · 시작 엔터티 형식 ${esc(lab(r.cond.start))}</p></div>
    <button class="btn out" ${r.check.ok ? '' : 'disabled data-tip="고칠 것을 먼저 고쳐 주세요."'} onclick="ruleTest(${r.id},this)">${ic('play', 16)}테스트 실행</button>
    ${r.on_ ? `<button class="btn out" ${lock()} onclick="ruleToggle(${r.id},0)">중지</button>` : `<button class="btn pri" ${!can('build') ? lock() : r.check.ok ? '' : 'disabled data-tip="실행할 수 없는 규칙은 시작할 수 없습니다."'} onclick="ruleToggle(${r.id},1)">시작</button>`}
    <div class="morew"><button class="ibtn" aria-label="더보기" aria-haspopup="menu" ${lock()} onclick="phMore(event)">${ic('dots', 20)}</button><div class="menu" id="moreMenu" role="menu"><button role="menuitem" class="dan" onclick="closeMenu();ruleDel(${r.id})">${ic('x')}<span>규칙 삭제</span></button></div></div></div>
  <div class="g2">
    <div class="card"><h3>규칙 문장</h3><p style="margin:0;font-size:16px;line-height:24px">${esc(r.text)}</p></div>
    <div class="card"><h3>연결된 개념 <small>이 규칙이 쓰는 엔터티 형식·속성</small></h3>${ruleConcepts(r.cond)}</div>
    <div class="card"><h3>조건 <small>프로그램이 이대로 실행합니다.</small></h3><div class="cond">${condText(r.cond)}</div>
      <div class="row" style="margin-top:12px">${r.check.ok ? '<span class="tag ok">실행 가능</span>' : r.check.why.map((w) => `<span class="tag bad">${esc(w)}</span>`).join('')}</div></div>
    <div class="card"><h3>테스트 결과</h3><p id="rt${r.id}" class="muted" style="margin:0">[테스트 실행]을 누르면 지금 데이터에서 몇 건이 걸리는지 보여 줍니다.</p></div>
  </div>`;
}
function ruleNewPage(kind) {
  CRUMB = [['규칙', '#rules'], ['새 규칙']];
  if (!RNEW || RNEW.from !== location.hash) RNEW = { from: location.hash, kind: kind === '분류' ? '분류' : '판단', text: '', made: null };
  const N = RNEW, m = N.made;
  exChips('rule', 'exRule').then((h) => { if ($('#rEx')) $('#rEx').innerHTML = h; });
  setTimeout(() => { const t = $('#rTxt'); if (t) t.oninput = () => { N.text = t.value; NODE.dirty = !!t.value.trim(); if (N.made) { N.made = null; $('#rOut').innerHTML = ''; ruleBtns(); } }; ruleBtns(); });
  return `<div class="ph"><div class="t"><h1>새 규칙</h1><p>업무 기준을 문장으로 적고 미리 보기로 조건을 확인합니다. 저장한 규칙은 중지 상태로 남고, 시작해야 질문·전체 판정에 쓰입니다.</p></div></div>
  <div class="card stack" style="max-width:960px">
    <div class="fld"><label>종류<i></i></label><div class="seg" id="rkSeg">${[['판단', '조건에 걸리면 결과를 붙임'], ['분류', '위에서부터 처음 걸린 곳으로 보냄']].map(([k, d]) => `<button class="${k === N.kind ? 'on' : ''}" data-tip="${d}" onclick="RNEW.kind='${k}';RNEW.made=null;render()">${k}</button>`).join('')}</div></div>
    <div id="rEx"></div>
    <div class="fld"><label>규칙 문장<i></i></label><textarea class="inp" id="rTxt" rows="4" placeholder="예) 가입 후 90일 안에 청구했고 고지사항에 병력이 있으면 확인 필요">${esc(N.text)}</textarea></div>
    <div><button class="btn out sm" onclick="ruleCompile(this)">${ic('robot', 16)}미리 보기</button></div>
    <div id="rOut">${m ? `<div class="stack"><div class="fld"><label>규칙 이름<i></i></label><input class="inp" id="rName" value="${esc(m.name)}" oninput="RNEW.made.name=this.value"></div>
      <div class="fld"><label>조건</label><div class="cond">${condText(m)}</div><div class="row">${m.check.ok ? '<span class="tag ok">실행 가능</span>' : m.check.why.map((w) => `<span class="tag bad">${esc(w)}</span>`).join('')}</div></div>
      <div class="fld"><label>연결된 개념</label>${ruleConcepts(m)}</div></div>` : ''}</div>
  </div>
  ${pageFoot(`<button class="btn out" onclick="location.hash='rules'">취소</button><button class="btn out" id="rSave" ${lock()} onclick="ruleSave(this,0)">저장</button><button class="btn pri" id="rStart" ${lock()} onclick="ruleSave(this,1)">저장 후 시작</button>`)}`;
}
function ruleBtns() {
  const m = RNEW?.made, s = $('#rSave'), g = $('#rStart'); if (!s || !can('build')) return;
  s.disabled = !m; g.disabled = !m || !m.check.ok;
  s.dataset.tip = m ? '' : '미리 보기를 확인한 후 저장할 수 있습니다.'; g.dataset.tip = !m ? '미리 보기를 확인한 후 저장할 수 있습니다.' : m.check.ok ? '' : '실행할 수 없는 규칙은 저장만 할 수 있습니다.';
  [s, g].forEach((b) => { if (!b.dataset.tip) delete b.dataset.tip; });
}
async function ruleCompile(btn) {
  const t = $('#rTxt').value.trim(); if (!t) { toast('규칙 문장을 입력해 주세요.', true); return; }
  await run(btn, '', async () => { RNEW.text = t; RNEW.made = { ...(await post('/rules/compile', { text: t, kind: RNEW.kind })), kind: RNEW.kind, text: t }; NODE.dirty = true; $('#page').innerHTML = await ruleNewPage(RNEW.kind); });
}
async function ruleSave(btn, on) {
  await run(btn, '', async () => { const r = await post('/rules', { ...RNEW.made, name: ($('#rName')?.value || RNEW.made.name).trim(), on }); NODE.dirty = false; RNEW = null; toast(on ? '규칙이 저장되고 시작되었습니다.' : '규칙이 저장되었습니다. 시작해야 질문·전체 판정에 쓰입니다.'); location.hash = 'rules?id=' + r.id; });
}
async function ruleTest(id, btn) { await run(btn, '실행 중', async () => { const r = await post(`/rules/${id}/test`); $('#rt' + id).className = ''; $('#rt' + id).innerHTML = `<b>${r.total.toLocaleString()}건 중 ${r.hits.length}건</b>이 걸렸습니다.${r.hits.length ? `<div class="muted" style="margin-top:4px">${esc(r.hits.slice(0, 12).join(', '))}${r.hits.length > 12 ? ' …' : ''}</div>` : ''}${r.calc?.length ? `<div class="sec-t sm" style="margin-top:12px">걸린 건의 계산 과정 <small>앞 ${r.calc.length}건</small></div>${r.calc.map((c) => `<div class="muted" style="margin-top:6px">${esc(c.key)}</div>${calcView(c.items, { compact: true })}`).join('')}` : ''}`; }); }
async function ruleToggle(id, on) { await post(`/rules/${id}/toggle`, { on: !!on }); toast(on ? '규칙이 시작되었습니다.' : '규칙이 중지되었습니다.'); refresh(); }
async function ruleDel(id) {
  if (!(await confirmBox({ title: '규칙을 삭제하시겠습니까?', body: '버전 기록에서 복원할 수 있습니다.', ok: '삭제', danger: true }))) return;
  await del('/rules/' + id); toast('규칙이 삭제되었습니다.'); location.hash = 'rules';
}

// 골든 질문
let GOLD = [], gOk = '';
const okTag = (ok) => ok === '맞음' ? '<span class="b ok">통과</span>' : ok === '일부' ? '<span class="b warn">일부</span>' : ok ? '<span class="b bad">실패</span>' : '<span class="b">실행 전</span>';
async function goldRun(btn) { await run(btn, '실행 중', async () => { const r = await post('/golden/run'); toast(`골든 질문 ${r.total}개 중 ${r.pass}개가 통과되었습니다.`); await refresh(); }); }
async function goldVote(id, v) { await post(`/golden/${id}/vote`, { vote: v }); toast('판정이 저장되었습니다.'); refresh(); }
async function goldDel(id) { if (!(await confirmBox({ title: '골든 질문을 삭제하시겠습니까?', body: '삭제 후에는 되돌릴 수 없습니다.', ok: '삭제', danger: true }))) return; await del('/golden/' + id); toast('골든 질문이 삭제되었습니다.'); if (location.hash === '#golden') refresh(); else location.hash = 'golden'; }

// 질문 기록
let ASKS = [], aQ = '', aSt = '';
P.trace = async () => {
  ASKS = await get('/asks');
  const list = ASKS.filter((a) => (!aQ || a.q.includes(aQ)) && (!aSt || a.status === aSt));
  return `<div class="ph"><div class="t"><h1>${isUser() ? '내 질문 기록' : '질문 기록'}</h1><p>답과 근거, 그리고 어떤 길로 찾았는지(탄 경로)를 남깁니다. 질문은 데이터 에이전트에서 합니다.</p></div>
    </div>
  <div class="lc"><div class="search">${ic('search')}<input class="inp" placeholder="질문 입력" value="${esc(aQ)}" onkeydown="if(event.key==='Enter'){aQ=this.value;render()}"></div>
    <select class="inp" onchange="aSt=this.value;render()"><option value="">결과 | 전체</option>${[['ok', '답변'], ['broken', '미연결'], ['no', '답변 불가']].map(([k, v]) => `<option value="${k}" ${aSt === k ? 'selected' : ''}>결과 | ${v}</option>`).join('')}</select>${aQ || aSt ? resetBtn("aQ='';aSt=''") : ''}<span class="cnt">총 ${list.length}건</span><span class="sp"></span><button class="btn pri" onclick="${isUser() ? "location.hash='ask'" : 'fabOpen(true)'}">${ic('chat')}데이터 에이전트</button></div>
  <div class="card flat">${list.length ? `<table class="t"><thead><tr><th>질문</th>${isUser() ? '' : '<th data-tip="같은 모양의 질문을 묶은 이름입니다. 같은 틀이면 같은 길로 찾습니다.">예제 쿼리</th>'}<th>답</th>${isUser() ? '' : '<th>질문한 사람</th>'}<th>질문 일시</th></tr></thead><tbody>
    ${list.map((a) => `<tr class="click" onclick="openAsk(${a.id})"><td>${esc(a.q)}</td>${isUser() ? '' : `<td><span class="b">${a.mode === 'set' ? '여러 건 · ' : ''}${esc(a.tpl || '-')}</span></td>`}<td>${statusDot(a.status, a.answer)}</td>${isUser() ? '' : `<td class="r">${esc(a.who || '-')}</td>`}<td class="r">${fmtT(a.at)}</td></tr>`).join('')}</tbody></table>`
    : ASKS.length ? empty('조건에 맞는 질문이 없습니다.', '검색어 또는 필터를 조정해 주세요.', resetBtn("aQ='';aSt=''"), true, 'search') : empty('아직 질문이 없습니다.', '데이터 에이전트 화면에서 궁금한 것을 물어보세요.', `<button class="btn pri" onclick="location.hash='ask'">데이터 에이전트</button>`, false, 'chat')}</div>`;
};
async function openAsk(id) {
  const [a, o] = await Promise.all([get('/asks/' + id), get('/onto')]);
  ONTO = o;
  const cls = a.status === 'ok' ? '' : a.status === 'broken' ? 'bad' : 'warn';
  const nodes = o.objects.map((x) => ({ id: x.name, label: x.label, sub: x.name }));
  const used = new Set(a.hot.rels);
  const edges = o.relations.map((r) => ({ a: r.a_tbl, b: r.b_tbl, cls: used.has(r.id) ? 'hot' : 'dime' })).concat((a.missing || []).map(([x, y]) => ({ a: x, b: y, cls: 'miss', lab: '미연결' })));
  const biz = isUser();
  const how = `<div><div class="sec-t sm">탄 경로 <small>단계를 선택하면 보낸 쿼리가 보입니다.</small></div><div class="trace">${a.steps.map((s, i) => `<div class="tr ${s.broken ? 'broken' : i === a.steps.length - 1 && a.status === 'ok' ? 'res' : ''}" onclick="this.classList.toggle('open')"><span class="no">${i + 1}</span><div><b>${esc(s.title)}</b><div class="qres">${esc(s.detail || '')}</div>${s.sql && !biz ? `<div class="q"><div class="qcode">${esc(s.sql)}</div></div>` : ''}</div><span class="ms">${s.ms ?? ''}ms</span></div>`).join('')}</div></div>
    <div><div class="sec-t sm">지나간 엔터티 형식</div><div class="gwrap">${svgGraph(nodes, edges, { hot: a.hot.nodes, attr: 'data-x', H: Math.max(380, Math.min(760, 80 + nodes.length * 40)) })}</div><div class="legend"><span><i class="hot"></i>이번 답에 쓴 길</span><span><i class="miss"></i>미연결</span></div></div>`;
  panel(`<div class="hd"><h2>${biz ? '답과 근거' : '질문 기록'}</h2><button class="ibtn" aria-label="닫기" onclick="closePanel()">${ic('x', 20)}</button></div><div class="bd stack">
    <div class="ans ${cls}"><div class="row"><span class="muted">${esc(a.q)}</span><span class="sp"></span>${a.tpl && !biz ? `<span class="b" data-tip="같은 모양의 질문을 묶은 이름입니다. 같은 틀이면 같은 길로 찾습니다.">예제 쿼리 · ${esc(a.tpl)}</span>` : ''}${a.same_tpl > 1 && !biz ? `<span class="b info">같은 틀 질문 ${a.same_tpl}건</span>` : ''}</div>
      <div class="v">${esc(a.answer)}</div><div>${esc(a.detail || '')}</div>${a.evidence?.length ? `<div style="margin-top:8px;font-weight:700">근거</div><ol>${a.evidence.map((e) => `<li>${esc(e)}</li>`).join('')}</ol>` : ''}</div>
    ${a.table ? `<div><div class="sec-t sm">계산 결과 <span class="sp"></span>${can('build') && !isUser() ? `<button class="btn out sm" onclick="closePanel();saveAsMetric(${id})">${ic('chart', 16)}메트릭으로 저장</button>` : ''}</div>${resView(a.table)}</div>` : ''}
    ${(a.chunks || []).length ? `<div><div class="sec-t sm">문서 본문 근거 <small>관계로 이어진 문서 안에서 고른 조각</small></div>${a.chunks.map((c) => `<button class="snip" ${biz ? 'disabled style="cursor:default"' : `onclick="openDoc('${esc(c.doc_id)}',${c.page})"`}><div class="row"><b class="mono">${esc(c.doc_id)}</b><span class="b">${c.page}쪽</span><span class="sp"></span><span class="muted mono" title="비슷한 정도(1에 가까울수록 비슷)">${Number(c.score).toFixed(2)}</span></div><p>${esc(c.text).replace(/\n/g, '<br>')}</p></button>`).join('')}</div>` : ''}
    ${(a.missing || []).length ? `<div class="alert bad">${ic('linkbreak')}<div>${biz ? '필요한 데이터가 서로 이어져 있지 않아 답할 수 없습니다. 구축 담당에게 알려 주세요.' : `미연결: ${a.missing.map(([x, y]) => esc(lab(x) + ' → ' + lab(y))).join(', ')} — 온톨로지 설계에서 관계를 추가해 주세요.`}</div></div>` : ''}
    ${(a.rules || []).length && !biz ? `<div><div class="sec-t sm">규칙 실행</div>${a.rules.map((r) => `<div class="row" style="padding:4px 0"><span class="tag ${r.hit ? 'warn' : r.hit === null ? 'bad' : ''}">${r.hit ? '해당' : r.hit === null ? '실행 불가' : '미해당'}</span><b>${esc(r.name)}</b>${r.hit ? `<span>→ ${esc(r.then || '')}</span>` : ''}</div>`).join('')}</div>` : ''}
    ${biz ? `<details class="sqlbox"><summary>어떻게 찾았는지 보기</summary><div class="stack" style="margin-top:12px">${how}</div></details>` : how}</div>`, 'xl');
}

// 그래프 탐색
let EXP = { obj: '', val: '', q: '', list: null, data: null, sel: null };
P.explore = async () => {
  ONTO = await get('/onto');
  if (!ONTO.objects.length) return `<div class="ph"><div class="t"><h1>그래프 탐색</h1><p>엔터티 형식에 들어간 실제 값을 그래프로 봅니다.</p></div></div><div class="card">${empty('아직 탐색할 데이터가 없습니다.', isUser() ? '구축 담당이 온톨로지를 만들면 탐색할 수 있습니다.' : '온톨로지 설계에서 엔터티 형식을 생성해 주세요.', isUser() ? '' : `<button class="btn pri" onclick="location.hash='design'">온톨로지 설계로 이동</button>`, false, 'search')}</div>`;
  if (!EXP.obj || !ONTO.objects.some((o) => o.name === EXP.obj)) EXP.obj = ONTO.objects[0].name;
  const d = EXP.data, list = EXP.list;
  return `<div class="ph"><div class="t"><h1>그래프 탐색</h1><p>대상을 고르고 이름·번호로 찾은 뒤, 한 줄을 고르면 이어진 값을 그래프로 보여 줍니다.</p></div></div>
  <div class="lc"><select class="inp" id="eObj" onchange="EXP.obj=this.value;EXP.q='';EXP.list=null;EXP.data=null;render()">${ONTO.objects.map((o) => `<option value="${esc(o.name)}" ${EXP.obj === o.name ? 'selected' : ''}>찾을 대상 | ${esc(o.label)}</option>`).join('')}</select>
    <div class="search">${ic('search')}<input class="inp" id="eVal" placeholder="검색어 입력" value="${esc(EXP.q || '')}" onkeydown="if(event.key==='Enter')findInst()"></div>${EXP.q ? resetBtn("EXP.q='';EXP.list=null;EXP.data=null") : ''}${list ? `<span class="cnt">총 ${list.total.toLocaleString()}행</span>` : ''}</div>
  ${list ? `<div class="card flat" style="margin-bottom:16px">${list.rows.length ? `<div style="max-height:260px;overflow:auto"><table class="t"><thead><tr>${list.cols.slice(0, 6).map((c) => `<th>${esc(list.labels?.[c] || c)}</th>`).join('')}</tr></thead><tbody>${list.rows.map((x) => `<tr class="click ${String(x[list.key]) === EXP.val ? 'sel' : ''}" onclick="EXP.val='${esc(x[list.key])}';doExplore()">${list.cols.slice(0, 6).map((c) => `<td class="r">${esc(x[c])}</td>`).join('')}</tr>`).join('')}</tbody></table></div><p class="muted" style="padding:8px 16px;margin:0">${list.total > list.rows.length ? `앞 ${list.rows.length}행만 보여 줍니다. · ` : ''}줄을 선택하면 이어진 값을 그래프로 보여 줍니다.</p>` : empty('조건에 맞는 값이 없습니다.', '검색어를 조정해 주세요.', '', true, 'search')}</div>` : ''}
  <div class="card">${!d ? empty('검색어를 입력해 주세요.', '찾은 줄을 선택하면 이어진 값을 그래프로 보여 줍니다.', '', true, 'search')
    : !d.nodes.length ? empty('조건에 맞는 값이 없습니다.', '검색어를 조정해 주세요.', '', true, 'search')
    : `<div class="gwrap">${svgGraph(d.nodes.map((n) => ({ id: n.id, label: n.label, sub: n.value })), d.edges.map(([a, b]) => ({ a, b })), { attr: 'data-inst', sel: EXP.sel, H: Math.max(360, Math.min(620, 140 + d.nodes.length * 18)) })}</div><p class="muted" style="margin-top:8px">값 ${d.nodes.length}개 · 엔터티 형식마다 최대 6개까지 보여 줍니다. 값을 선택하면 상세가 열립니다.</p>`}</div>`;
};
async function findInst() {
  EXP.obj = $('#eObj').value; EXP.q = $('#eVal').value.trim(); EXP.data = null;
  try { EXP.list = await get(`/objects/${encodeURIComponent(EXP.obj)}/rows?q=${encodeURIComponent(EXP.q)}&n=50`); if (EXP.list.rows.length === 1) { EXP.val = String(EXP.list.rows[0][EXP.list.key]); return doExplore(); } } catch (e) { toast(e.message, true); }
  render();
}
async function doExplore(fromPanel = false) {
  if (!EXP.val) return;
  EXP.sel = null;
  if (fromPanel) EXP.list = null;
  try { EXP.data = await get(`/explore?obj=${encodeURIComponent(EXP.obj)}&value=${encodeURIComponent(EXP.val)}`); } catch (e) { toast(e.message, true); }
  render();
}
function openInst(id) {
  const n = EXP.data?.nodes.find((x) => x.id === id); if (!n) return;
  panel(`<div class="hd"><h2>${esc(n.label)} · ${esc(n.value)}</h2></div><div class="bd">
    <dl class="dl">${Object.entries(n.row).map(([k, v]) => `<dt>${esc((ONTO?.objects.find((o) => o.name === n.tbl)?.props || []).find((p) => p.col === k)?.label || k)}</dt><dd>${esc(v || '-')}</dd>`).join('')}</dl></div>
    <div class="ft"><button class="btn out" onclick="closePanel()">닫기</button><button class="btn pri" onclick="closePanel();EXP.obj='${esc(n.tbl)}';EXP.val='${esc(n.key)}';EXP.list=null;doExplore()">이 값으로 재탐색</button></div>`, 'md');
}

// 변경 이력
P.history = async () => {
  const h = await get('/changes');
  const groups = {};
  h.items.forEach((c) => (groups[fmtD(c.at)] ||= []).push(c));
  const today = Object.entries(h.today).filter(([, v]) => v.length);
  const item = (c) => {
    const st = c.status === 'pending' ? '<span class="b warn">승인 대기</span>' : c.status === 'rejected' ? '<span class="b">반려</span>' : c.id === h.current ? '<span class="b ok">현재 버전</span>' : '';
    const lines = c.diff?.lines || Object.entries(c.diff || {}).filter(([k]) => !['snap'].includes(k)).map(([k, v]) => `${k}: ${typeof v === 'string' ? v : JSON.stringify(v)}`);
    return `<div class="tli"><div class="h"><b>v${c.id}</b>${st}<span class="b">${esc(c.layer)}</span><span class="muted">${fmtT(c.at).slice(11)} · ${esc(c.by)}</span></div><p>${esc(c.title)}</p>
      ${lines.length ? `<div class="diff">${lines.slice(0, 4).map((l) => `<div class="a">${esc(String(l).slice(0, 200))}</div>`).join('')}</div>` : ''}
      ${c.status === 'pending' ? `<div class="row"><button class="btn sm pri" ${lock('review')} onclick="approve(${c.id})">승인</button><button class="btn sm out" ${lock('review')} onclick="reject(${c.id})">반려</button></div>`
      : c.status === 'applied' && c.id !== h.current ? `<div class="row"><button class="btn xs out" ${lock()} onclick="rollback(${c.id})">${ic('undo', 12)}이 버전으로 복원</button></div>` : ''}</div>`;
  };
  return `<div class="ph"><div class="t"><h1>변경 이력</h1><p>바꿀 때마다 버전이 남습니다. Copilot이 제안한 변경과 복원은 승인 후 적용됩니다.</p></div></div>
  <div class="card" style="margin-bottom:24px"><h3>오늘 바뀐 것 <small>종류마다 건수 · 마우스를 올리면 내용이 보입니다.</small></h3>${today.length ? `<div class="row" style="gap:12px">${today.map(([k, v]) => `<span class="tag" title="${esc(v.join('\n'))}">${esc(k)} ${v.length}건</span>`).join('')}</div>` : '<p class="muted" style="margin:0">오늘 바뀐 것이 없습니다.</p>'}</div>
  ${h.items.length ? Object.entries(groups).map(([d, cs]) => `<div class="tlg"><div class="d"><b>${d.slice(5)}</b><span>${d.slice(0, 4)}</span></div><div class="vl"></div><div>${cs.map(item).join('')}</div></div>`).join('')
    : `<div class="card">${empty('아직 변경 이력이 없습니다.', '', '', false, 'history')}</div>`}
  <div class="guide" style="margin-top:24px"><b>변경 적용 기준</b>화면에서 바꾼 것은 바로 적용되고 이름이 남습니다. Copilot 제안과 복원은 검토자가 승인해야 적용되며, 자기 신청은 승인할 수 없습니다.</div>`;
};
async function approve(id) { if (!(await confirmBox({ title: '변경을 승인하시겠습니까?', body: '승인하면 바로 적용됩니다.', ok: '승인' }))) return; await post(`/changes/${id}/approve`); toast('변경이 승인되었습니다.'); refresh(); }
async function reject(id) { const why = await confirmBox({ title: '변경을 반려하시겠습니까?', input: '반려 사유', ok: '반려', danger: true, cancel: '닫기' }); if (!why) return; await post(`/changes/${id}/reject`, { reason: why }); toast('변경이 반려되었습니다.'); refresh(); }
async function rollback(id) { if (!(await confirmBox({ title: '복원을 신청하시겠습니까?', body: `v${id} 상태로 엔터티 형식·관계·읽을 칸·규칙·메트릭을 되돌립니다. 검토자가 승인하면 적용됩니다.` }))) return; await post(`/changes/${id}/rollback`); toast('복원이 신청되었습니다.'); refresh(); }

// ── 사용자 · 역할 ── 로그인 대신 화면 위에서 사용자를 고름(시험용)
let ME = { user: null, setup: true, perms: [], roles: {} };
const can = (p) => ME.setup || ME.perms.includes(p);
const LOCK = { build: '구축 담당·관리자만 할 수 있습니다.', review: '검토자·관리자만 할 수 있습니다.', admin: '관리자만 할 수 있습니다.' };
const lock = (p = 'build') => (can(p) ? '' : `disabled data-tip="${LOCK[p]}"`);
const isUser = () => ME.user?.role === '현업';
function setUid(id) { try { id ? localStorage.setItem('geno_uid', id) : localStorage.removeItem('geno_uid'); } catch { /* 저장소 없음 */ } }
function renderWho() {
  const u = ME.user;
  $('#who').innerHTML = ME.setup ? `<button class="btn out sm" onclick="firstAdmin()">${ic('user', 16)}첫 관리자 생성</button>`
    : `<button class="btn out sm" aria-haspopup="menu" onclick="whoMenu(event)">${ic('user', 16)}${esc(u?.name || '사용자 선택')}${u ? `<span class="muted">· ${esc(u.role)}</span>` : ''}${ic('chevd', 16)}</button>`;
}
async function whoMenu(e) {
  e.stopPropagation();
  const { users } = await get('/users');
  const m = $('#whoMenu');
  m.setAttribute('role', 'menu');
  m.innerHTML = `<div class="mt">사용자 전환 <small>로그인 대신(시험용)</small></div>${users.map((u) => `<button role="menuitem" class="${ME.user?.id === u.id ? 'on' : ''}" onclick="switchUser(${u.id})"><span>${esc(u.name)}</span><span class="muted">${esc(u.role)}</span>${ME.user?.id === u.id ? `<span class="ok">${ic('check', 16)}</span>` : ''}</button>`).join('')}
    ${can('admin') ? `<div class="sepl"></div><button role="menuitem" onclick="location.hash='users';closeMenu()">${ic('gear', 16)}<span>사용자·권한 관리</span></button>` : ''}`;
  m.classList.add('on');
}
function phMore(e) { e.stopPropagation(); $('#moreMenu').classList.toggle('on'); }
function closeMenu() { ['#whoMenu', '#moreMenu', '#getMenu'].forEach((m) => $(m)?.classList.remove('on')); }
function switchUser(id) { setUid(id); CHAT = []; closeMenu(); location.hash = ''; refresh().then(() => toast(`${ME.user?.name}(${ME.user?.role}) 사용자로 전환되었습니다.`)); }
function firstAdmin() {
  formModal('첫 관리자 생성', `<p class="muted" style="margin:0 0 16px">관리자를 만들면 역할(관리자·구축 담당·검토자·현업)별로 화면과 권한이 나뉩니다. 로그인 대신 화면 위에서 사용자를 바꿔 씁니다.</p>
    <div class="fld"><label>이름<i></i></label><input class="inp" id="uN" placeholder="예) 김제논"></div>`, '생성', async () => {
    const r = await post('/users/first', { name: $('#uN').value.trim() }); setUid(r.id); toast('관리자가 생성되었습니다.'); await refresh();
  });
}

// 사용자·권한 페이지(관리자)
P.users = async () => {
  const { users, roles } = await get('/users');
  return `<div class="ph"><div class="t"><h1>사용자·권한</h1><p>만드는 사람(구축 담당)과 쓰는 사람(현업)을 나눕니다. 화면 위 사용자 전환으로 역할별 화면을 확인할 수 있습니다.</p></div></div>
  <div class="lc"><span class="cnt">총 ${users.length}명</span><span class="sp"></span><button class="btn pri" ${lock('admin')} onclick="userModal()">${ic('plus')}사용자 추가</button></div>
  <div class="card flat">${users.length ? `<table class="t"><thead><tr><th>이름</th><th>역할</th><th>추가 일시</th><th></th></tr></thead><tbody>
    ${users.map((u) => `<tr><td>${esc(u.name)}${ME.user?.id === u.id ? ' <span class="muted">(나)</span>' : ''}</td><td><select class="inp xs" ${lock('admin')} onchange="setRole(${u.id},this.value)">${Object.keys(roles).map((r) => `<option ${u.role === r ? 'selected' : ''}>${r}</option>`).join('')}</select></td>
      <td class="r">${fmtT(u.at)}</td><td class="num"><button class="btn xs dan" ${lock('admin')} onclick="userDel(${u.id})">삭제</button></td></tr>`).join('')}</tbody></table>`
    : empty('아직 사용자가 없습니다.', '첫 관리자를 만들어 주세요.', `<button class="btn pri" onclick="firstAdmin()">첫 관리자 생성</button>`, false, 'user')}</div>
  <div class="sec"><div class="sec-t">역할별 권한</div><div class="card flat"><table class="t"><thead><tr><th style="width:160px">역할</th><th>할 수 있는 일</th></tr></thead><tbody>
    ${Object.entries(roles).map(([r, d]) => `<tr><td>${r}</td><td class="r">${esc(d)}</td></tr>`).join('')}</tbody></table></div>
    <div class="guide" style="margin-top:16px"><b>변경 적용 기준</b>화면에서 바꾼 것은 바로 적용되고 이름이 남습니다. Copilot 제안과 복원은 검토자가 승인해야 적용되며, 자기 신청은 승인할 수 없습니다.</div></div>`;
};
function userModal() {
  formModal('사용자 추가', `<div class="fld"><label>이름<i></i></label><input class="inp" id="uN" placeholder="예) 박현업"></div>
    <div class="fld" style="margin-top:16px"><label>역할<i></i></label><select class="inp" id="uR">${Object.entries(ME.roles).map(([r, d]) => `<option value="${r}">${r} — ${esc(d)}</option>`).join('')}</select></div>`, '추가', async () => {
    await post('/users', { name: $('#uN').value.trim(), role: $('#uR').value }); toast('사용자가 추가되었습니다.'); refresh();
  });
}
async function setRole(id, role) {
  const u = (await get('/users')).users.find((x) => x.id === id);
  if (!(await confirmBox({ title: '역할을 변경하시겠습니까?', body: `${esc(u.name)}의 역할을 ${esc(role)}(으)로 바꿉니다.${ME.user?.id === id ? ' 바꾸면 내 화면과 권한도 바로 바뀝니다.' : ''}` }))) return render();
  try { await post(`/users/${id}/role`, { role }); toast('역할이 변경되었습니다.'); } catch (e) { toast(e.message, true); } refresh();
}
async function userDel(id) {
  if (!(await confirmBox({ title: '사용자를 삭제하시겠습니까?', body: '이 사용자가 남긴 변경 이력과 질문 기록은 그대로 남습니다.', ok: '삭제', danger: true }))) return;
  try { await del('/users/' + id); toast('사용자가 삭제되었습니다.'); } catch (e) { toast(e.message, true); } refresh();
}

// ── 계산 결과 그리기(여러 건 질문 · 메트릭 · 전체 판정 공통) ──
function resView(t, { max = 20, sql = '' } = {}) {
  if (!t || !t.rows) return '';
  const rows = t.rows.slice(0, max);
  let body;
  if (t.cols.length === 1 && t.cols[0] === 'val') {
    const v = rows[0]?.val;
    body = `<div class="bignum">${v == null ? '-' : Number(v).toLocaleString()}</div>`;
  } else if (t.cols[0] === 'grp') {
    const mx = Math.max(...rows.map((r) => Number(r.val) || 0), 1);
    body = `<div class="bars">${rows.map((r) => `<div class="br"><span class="bl" title="${esc(r.grp)}">${esc(r.grp ?? '(빈 값)')}</span><span class="bt"><i style="width:${Math.max(2, ((Number(r.val) || 0) / mx) * 100)}%"></i></span><span class="bv">${Number(r.val).toLocaleString()}</span></div>`).join('')}</div>`;
  } else {
    body = `<div style="overflow:auto"><table class="t"><thead><tr>${t.cols.map((c) => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${rows.map((r) => `<tr>${t.cols.map((c) => `<td class="r">${esc(r[c] ?? '')}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  }
  return body + (t.rows.length > max ? `<p class="muted">앞 ${max}행만 보여 줍니다.</p>` : '') + (t.total != null ? `<p class="muted" style="margin-top:8px">조건에 맞는 대상 ${Number(t.total).toLocaleString()}건 · 계산은 프로그램(SQL)이 했습니다.</p>` : '')
    + (sql ? `<details class="sqlbox"><summary>보낸 쿼리</summary><div class="qcode">${esc(sql)}</div></details>` : '');
}

// ── 엔터티 형식 정의 층 ──
const OPS = ['=', '!=', '<', '<=', '>', '>=', '포함', '안 포함'];
const CARD = { '1:1': '1:1 · 한 건 ↔ 한 건', '1:N': '1:N · 한 건 → 여러 건', 'N:1': 'N:1 · 여러 건 → 한 건', 'N:M': 'N:M · 여러 건 ↔ 여러 건' };
const fltText = (f) => (f || []).map((x) => `${x.col} ${x.op} ${x.value}`).join(' AND ');
// 온톨로지 설계 — Fabric 온톨로지 편집기 흐름을 따름(모양은 제논 DS)
//  첫 화면: 위 리본(엔터티 형식 추가 · 관계 추가 · 엔터티 형식 세부 정보 보기 …) + 왼쪽 탐색기(개요 · 엔터티 형식 · 관계) + 가운데 그래프(전체 온톨로지 / 동네)
//  엔터티 형식을 열면 같은 자리에 엔터티 형식 페이지(구성 · 인스턴스). 속성 편집 · 관계 · 새 엔터티 형식은 각자 전체 페이지 + 아래 저장/취소
const hq = () => new URLSearchParams(location.hash.split('?')[1] || '');
const dzHref = (k, v, more = '') => `design?${k}=${encodeURIComponent(v)}${more}`;
const dzOpen = (name, tab = '') => { location.hash = dzHref('obj', name, tab ? `&tab=${tab}` : ''); };
let DZ = { sel: '', view: 'all', q: '', gold: [] };
let CRUMB = null;
P.design = async () => {
  [ONTO, DZ.gold] = await Promise.all([get('/onto'), get('/golden')]);
  const q = hq(), on = q.get('obj');
  if (on && !ONTO.objects.some((o) => o.name === on)) { toast('엔터티 형식을 찾을 수 없습니다. 삭제되었을 수 있습니다.', true); history.replaceState(null, '', '#design'); return dzHome(); }
  if (on) return q.get('edit') === 'props' ? dzProps(on) : dzObj(on, q.get('tab') || 'conf');
  if (q.get('rel')) return dzRel(q.get('rel'), q.get('a'));
  if (q.get('new')) return dzNew();
  return dzHome();
};
const objOf = (n) => ONTO.objects.find((o) => o.name === n);
const pageFoot = (btns) => `<div class="pfoot">${btns}</div>`;

// ── 편집기 첫 화면 ──
function dzHome() {
  const o = ONTO, has = o.objects.length > 0;
  if (DZ.sel && !objOf(DZ.sel)) DZ.sel = '';
  const ribbon = `<div class="ribbon" role="toolbar" aria-label="온톨로지 편집">
    <button class="rb" ${lock()} onclick="dzAddObj()">${ic('plus', 16)}엔터티 형식 추가</button>
    <button class="rb" ${!can('build') ? lock() : has ? '' : 'disabled data-tip="엔터티 형식을 먼저 추가해 주세요."'} onclick="relDialog(DZ.sel)">${ic('link', 16)}관계 추가</button>
    <button class="rb" ${DZ.sel ? '' : 'disabled data-tip="그래프나 탐색기에서 엔터티 형식을 선택해 주세요."'} onclick="dzOpen(DZ.sel)">${ic('cube', 16)}엔터티 형식 세부 정보 보기</button>
    <i class="rsep"></i>
    <button class="rb" ${!can('build') ? lock() : o.objects.length > 1 ? '' : 'disabled data-tip="엔터티 형식이 2개 이상 있어야 합니다."'} onclick="erOpen()">${ic('merge', 16)}같은 대상 묶기</button>
    <button class="rb" ${!can('build') ? lock() : ST.tables ? '' : 'disabled data-tip="데이터 원본을 먼저 연결해 주세요."'} onclick="draftDialog()">${ic('robot', 16)}AI 초안 ${has ? '재생성' : '생성'}</button>
    <button class="rb" onclick="focusCop()">${ic('chat', 16)}Copilot</button>
    <span class="sp"></span><button class="btn out sm" onclick="verPanel()">${ic('history', 16)}버전 기록</button></div>`;
  return `<div class="ph"><div class="t"><h1>온톨로지 설계</h1><p>테이블을 엔터티 형식으로, 열을 관계로 잇습니다. 엔터티 형식을 선택하면 할 일이 보이고, 두 번 누르면 엔터티 형식이 열립니다.</p></div></div>
  ${ribbon}${has ? dzNext() : ''}
  <div class="edb">${dzExplorer()}<section class="cv">${has ? dzCanvas() : dzStart()}</section></div>
  ${has ? `<div class="sec"><div class="sec-t">골든 질문이 지나는 길</div><div class="card flat">${goldPaths(DZ.gold)}</div></div>` : ''}`;
}
// 다음 할 일 한 줄(개요 화면 대신) — 빠진 것이 있을 때만
function dzNext() {
  const o = ONTO, loose = o.loose_tables.length, nk = o.objects.filter((x) => !x.key_ok).length;
  const todo = !o.relations.length ? ['관계가 없습니다. 엔터티 형식끼리 이어야 여러 엔터티 형식을 지나는 질문에 답할 수 있습니다.', '관계 추가', 'relDialog()']
    : nk ? [`키 값이 겹치는 엔터티 형식이 ${nk}개 있습니다(${esc(o.objects.filter((x) => !x.key_ok).map((x) => x.label).slice(0, 3).join(', '))}). 다른 줄이 한 인스턴스로 합쳐질 수 있어 키를 고쳐야 합니다.`, '고치기', `dzOpen('${esc(o.objects.find((x) => !x.key_ok).name)}')`]
    : ST.review ? [`문서 읽기 검수 대기 ${ST.review}칸이 있습니다.`, '검수하기', "location.hash='read'"]
    : !ST.golden ? ['골든 질문이 없습니다. 꼭 답해야 하는 질문과 정답을 넣어 두면 바꿀 때마다 맞는지 확인할 수 있습니다.', '골든 질문 만들기', "location.hash='golden'"]
    : ST.golden_pass < ST.golden ? [`골든 질문 ${ST.golden}개 중 ${ST.golden_pass}개 통과입니다.`, '골든 질문 보기', "location.hash='golden'"] : null;
  const extra = loose ? ` · 엔터티 형식으로 쓰지 않은 테이블 ${loose}개` : '';
  return todo ? `<div class="alert info" style="margin-bottom:16px">${ic('info')}<div><b>다음 할 일</b> ${todo[0]}<span class="muted">${extra}</span></div><button class="btn ter act" ${todo[2].startsWith('relDialog') ? lock() : ''} onclick="${todo[2]}">${todo[1]}</button></div>` : '';
}
function dzStart() {
  const t = ST.tables > 0, b = can('build');
  const card = (icon, title, desc, act, ok, why) => `<button class="startc" ${ok ? '' : `disabled data-tip="${why}"`} onclick="${act}"><span class="si">${ic(icon, 24)}</span><b>${title}</b><span>${desc}</span></button>`;
  const chk = [[ST.tables > 0, '데이터 가져오기', 'source'], [ST.objects > 0, '엔터티 형식 · 관계 만들기', 'design'], [ST.golden > 0, '골든 질문으로 확인하기', 'golden']];
  return `<div class="start"><h2>시작하기</h2><ol class="chk3">${chk.map(([ok, t, h], i) => `<li class="${ok ? 'ok' : ''}"><span class="n">${ok ? ic('check', 12) : i + 1}</span><a href="#${h}">${t}</a></li>`).join('')}</ol><div class="startg">
    ${card('robot', 'AI 초안으로 시작', '가져온 테이블로 AI가 엔터티 형식·관계 초안을 만듭니다.', 'draftDialog()', t && b, t ? LOCK.build : '데이터 원본을 먼저 연결해 주세요.')}
    ${card('cube', '엔터티 형식 직접 추가', '테이블을 골라 엔터티 형식을 하나씩 만듭니다.', 'dzAddObj()', t && b, t ? LOCK.build : '데이터 원본을 먼저 연결해 주세요.')}
    ${card('db', '데이터 원본 연결', t ? `가져온 테이블 ${ST.tables}개 · 테이블을 더 가져옵니다.` : '먼저 회사 DB나 파일에서 테이블을 가져옵니다.', "location.hash='connect'", b, LOCK.build)}
  </div></div>`;
}
function dzExplorer() {
  const o = ONTO;
  return `<aside class="exp" aria-label="탐색기"><div class="xh">탐색기</div>
    <div class="xg">개요</div>
    <a class="xi" href="#rules">${ic('rule', 16)}<span class="xl">규칙</span><span class="xn">${ST.rules || 0}</span></a>
    <a class="xi" href="#metrics">${ic('chart', 16)}<span class="xl">메트릭</span><span class="xn">${ST.metrics || 0}</span></a>
    <a class="xi" href="#whatif">${ic('refresh', 16)}<span class="xl">가정 바꿔 보기</span><span class="xn">${ST.scenarios || 0}</span></a>
    <div class="xg">엔터티 형식 <span class="xn">${o.objects.length}</span></div>
    ${o.objects.length ? `<div class="xs">${ic('search', 16)}<input class="inp xs" aria-label="엔터티 형식 이름으로 필터" placeholder="이름으로 필터" value="${esc(DZ.q)}" oninput="DZ.q=this.value;$('#dzObjs').innerHTML=dzObjList()"></div>` : ''}
    <div id="dzObjs">${dzObjList()}</div>
    <div class="xg">관계 유형 <span class="xn">${o.relations.length}</span></div>
    ${o.relations.length ? o.relations.map((r) => `<a class="xi" href="#design?rel=${r.id}">${ic('link', 16)}<span class="xl">${esc(lab(r.a_tbl))} → ${esc(lab(r.b_tbl))}</span></a>`).join('') : '<p class="xe">관계가 없습니다.</p>'}
    ${o.pending_rel.length ? `<a class="xi" href="#history">${ic('history', 16)}<span class="xl">승인 대기 관계</span><span class="b warn">${o.pending_rel.length}</span></a>` : ''}
    ${o.loose_tables.length ? `<div class="xg">엔터티 형식이 아닌 테이블 <span class="xn">${o.loose_tables.length}</span></div>${o.loose_tables.map((t) => `<div class="xi xr"><span class="ic">${ic('table', 16)}</span><span class="xl mono">${esc(t)}</span><button class="btn xs out" ${lock()} onclick="dzAddObj('${esc(t)}')">엔터티 형식으로</button></div>`).join('')}` : ''}
  </aside>`;
}
function dzObjList() {
  const q = DZ.q.trim(), list = ONTO.objects.filter((x) => !q || x.label.includes(q) || x.name.includes(q));
  if (!ONTO.objects.length) return '<p class="xe">엔터티 형식이 없습니다.</p>';
  if (!list.length) return '<p class="xe">조건에 맞는 엔터티 형식이 없습니다.</p>';
  return list.map((x) => `<div class="xi xr ${DZ.sel === x.name ? 'on' : ''}"><button class="xm" onclick="dzSel('${esc(x.name)}')" ondblclick="dzOpen('${esc(x.name)}')">${ic('cube', 16)}<span class="xl">${esc(x.label)}</span>${x.key_ok ? '' : `<span class="xw" data-tip="키 점검 필요 — 키 값이 겹칩니다. 열어서 고칠 방법을 확인하세요.">${ic('warn', 16)}</span>`}</button><button class="ibtn sm" aria-label="${esc(x.label)} 열기" data-tip="열기" onclick="dzOpen('${esc(x.name)}')">${ic('side', 16)}</button></div>`).join('');
}
function dzCanvas() {
  const o = ONTO, s = DZ.sel, nb = DZ.view === 'nb' && s;
  const near = new Set([s]); if (nb) o.relations.concat(o.pending_rel.map((p) => p.rel)).forEach((r) => { if (r.a_tbl === s) near.add(r.b_tbl); if (r.b_tbl === s) near.add(r.a_tbl); });
  const objs = nb ? o.objects.filter((x) => near.has(x.name)) : o.objects;
  const ids = new Set(objs.map((x) => x.name));
  const rels = o.relations.filter((r) => ids.has(r.a_tbl) && ids.has(r.b_tbl));
  const pend = o.pending_rel.filter((p) => ids.has(p.rel.a_tbl) && ids.has(p.rel.b_tbl));
  const edges = rels.map((r) => ({ a: r.a_tbl, b: r.b_tbl })).concat(pend.map((p) => ({ a: p.rel.a_tbl, b: p.rel.b_tbl, cls: 'pend', lab: '승인 대기' })));
  const so = s && objOf(s);
  return `<div class="cvt">${so ? `<div class="selbar"><span class="muted">선택</span><b>${esc(so.label)}</b><button class="btn xs pri" onclick="dzOpen('${esc(s)}')">열기</button><button class="btn xs out" ${lock()} onclick="relDialog('${esc(s)}')">관계 추가</button><button class="btn xs out" onclick="dzOpen('${esc(s)}','rows')">인스턴스</button>${so.derived && !s.startsWith('same_') ? `<button class="btn xs dan" ${lock()} onclick="objDel('${esc(s)}')">삭제</button>` : ''}<button class="ibtn sm" aria-label="선택 해제" onclick="dzSel('')">${ic('x', 16)}</button></div>` : '<span class="muted">엔터티 형식을 선택하면 할 일이 보입니다.</span>'}
    <span class="sp"></span><div class="seg" role="group" aria-label="보기"><button class="${nb ? '' : 'on'}" onclick="DZ.view='all';dzDraw()">전체 온톨로지</button><button class="${nb ? 'on' : ''}" ${s ? '' : 'disabled data-tip="엔터티 형식을 선택하면 동네(이어진 것만)를 볼 수 있습니다."'} onclick="DZ.view='nb';dzDraw()">동네</button></div></div>
  <div class="gwrap">${svgGraph(objs.map((x) => ({ id: x.name, label: x.label, sub: x.name })), edges, { H: Math.max(420, Math.min(720, 80 + objs.length * 40)), sel: s || null })}</div>
  <div class="cvs"><span>표시: 엔터티 형식 ${o.objects.length}개 중 ${objs.length}개 · 관계 ${o.relations.length}개 중 ${rels.length}개</span><span class="sp"></span><div class="legend"><span><i></i>연결</span><span><i class="pend"></i>승인 대기</span></div></div>`;
}
function dzSel(name) { DZ.sel = DZ.sel === name ? '' : name; if (!DZ.sel) DZ.view = 'all'; dzDraw(); }
function dzDraw() { if (cur() === 'design' && !location.hash.includes('?')) $('#page').innerHTML = dzHome(); }
document.addEventListener('click', (e) => {
  const g = e.target.closest('[data-node]'); if (g && cur() === 'design') { if (location.hash.includes('?')) dzOpen(g.dataset.node); else dzSel(g.dataset.node); }
  const x = e.target.closest('[data-inst]'); if (x) openInst(x.dataset.inst);
});
document.addEventListener('dblclick', (e) => { const g = e.target.closest('[data-node]'); if (g && cur() === 'design' && !location.hash.includes('?')) dzOpen(g.dataset.node); });
async function draftOnto(btn) { await run(btn, 'AI가 설계하는 중', async () => { const r = await post('/onto/draft'); toast(`초안이 생성되었습니다. (엔터티 형식 ${r.objects}개 · 관계 ${r.relations}개)`); await refresh(); }); }
async function redraft() {
  if (!(await confirmBox({ title: '초안을 재생성하시겠습니까?', body: 'AI가 만든 엔터티 형식·관계가 새 초안으로 바뀝니다. 직접 만든 엔터티 형식은 남고, 현재 버전은 버전 기록에서 복원할 수 있습니다.' }))) return;
  toast('AI가 설계하는 중입니다.'); try { const r = await post('/onto/draft'); toast(`초안이 생성되었습니다. (엔터티 형식 ${r.objects}개 · 관계 ${r.relations}개)`); } catch (e) { toast(e.message, true); } refresh();
}

// 버전 기록 — 편집기 오른쪽 위 버튼 → 사이드 패널(Fabric 버전 기록처럼)
async function verPanel() {
  const h = await get('/changes');
  const items = h.items.slice(0, 30);
  const byDay = {}; items.forEach((c) => (byDay[fmtD(c.at)] ||= []).push(c));
  panel(`<div class="hd"><h2>버전 기록</h2><button class="ibtn" aria-label="닫기" onclick="closePanel()">${ic('x', 20)}</button></div>
  <div class="bd">${items.length ? Object.entries(byDay).map(([d, cs]) => `<div class="vday">${d}</div><div class="vlist">${cs.map((c) => `<div class="vi"><div class="row"><b>v${c.id}</b>${c.id === h.current ? '<span class="b ok">현재 버전</span>' : c.status === 'pending' ? '<span class="b warn">승인 대기</span>' : c.status === 'rejected' ? '<span class="b">반려</span>' : ''}<span class="sp"></span><span class="muted">${fmtT(c.at)}</span></div>
    <p>${esc(c.title)}</p><div class="row"><span class="muted">${esc(c.layer)} · ${esc(c.by)}</span><span class="sp"></span>${c.status === 'applied' && c.id !== h.current ? `<button class="btn xs out" ${lock()} onclick="closePanel(true);rollback(${c.id})">${ic('undo', 12)}이 버전으로 복원</button>` : ''}</div></div>`).join('')}</div>`).join('')
    : empty('아직 버전이 없습니다.', '엔터티 형식이나 관계를 바꾸면 버전이 남습니다.', '', true, 'history')}</div>
  <div class="ft"><button class="btn out" onclick="closePanel(true);location.hash='history'">변경 이력 전체 보기</button></div>`, 'md');
}

// ── 엔터티 형식 추가: 이름 묻는 창 → 데이터 연결 페이지(원본 테이블 · 키 · 조건) → 만들기 → 엔터티 형식 페이지 ──
let NEWO = { label: '', base: '', key: '', filter: [] };
function dzAddObj(base = '') {
  formModal('엔터티 형식 추가', `<div class="fld"><label>엔터티 형식 이름<i></i></label><input class="inp" id="oN" placeholder="예) 진단서" value="${esc(base ? '' : '')}"><span class="help">다음 화면에서 이 엔터티 형식에 연결할 원본 테이블을 고릅니다.</span></div><div id="oEx"></div>`, '다음', async () => {
    const l = $('#oN').value.trim(); if (!l) throw new Error('엔터티 형식 이름을 입력해 주세요.');
    NEWO = { label: l, base, key: '', filter: [] }; location.hash = 'design?new=1';
  });
  objEx('#oEx');
}
async function dzNew() {
  if (!NEWO.label) { history.replaceState(null, '', '#design'); return dzHome(); }
  const tbls = (await get('/sources')).flatMap((s) => s.tables);
  const de = objOf('doc_extract'); if (de && !tbls.some((t) => t.name === 'doc_extract')) tbls.push({ name: 'doc_extract', cols: de.cols, nrows: de.nrows });
  if (!NEWO.base || !tbls.some((t) => t.name === NEWO.base)) NEWO.base = tbls[0]?.name || '';
  const t = tbls.find((x) => x.name === NEWO.base);
  if (t && !t.cols.includes(NEWO.key)) NEWO.key = t.cols[0];
  let prev = null; try { prev = t ? await get('/tables/' + encodeURIComponent(t.name) + '?n=6') : null; } catch { prev = null; }
  CRUMB = [['온톨로지 설계', '#design'], [`새 엔터티 형식 · ${NEWO.label}`]];
  const colOpt = (sel) => (t?.cols || []).map((c) => `<option ${sel === c ? 'selected' : ''}>${esc(c)}</option>`).join('');
  return `<div class="ph"><div class="t"><h1>데이터 연결 · ${esc(NEWO.label)}</h1><p>엔터티 형식으로 쓸 원본 테이블을 고릅니다. 조건을 넣으면 테이블의 일부 줄만 엔터티 형식이 됩니다(예: 문서 테이블 중 진단서만).</p></div></div>
  <div class="bind"><aside class="card flat bl"><div class="xh">원본 테이블 <span class="xn">${tbls.length}</span></div>
    ${tbls.length ? tbls.map((x) => `<button class="xi ${x.name === NEWO.base ? 'on' : ''}" onclick="NEWO.base='${esc(x.name)}';NEWO.key='';NEWO.filter=[];render()">${ic('table', 16)}<span class="xl mono">${esc(x.name)}</span><span class="xn">${(x.nrows ?? 0).toLocaleString()}행</span></button>`).join('') : '<p class="xe">가져온 테이블이 없습니다.</p>'}</aside>
  <div class="stack">
    <div class="card"><h3>${ic('table', 16)}<span class="mono">${esc(NEWO.base || '-')}</span><small>데이터 미리 보기 · 앞 6행</small></h3>
      ${prev?.rows?.length ? `<div style="overflow:auto"><table class="t"><thead><tr>${prev.cols.map((c) => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${prev.rows.map((r) => `<tr>${prev.cols.map((c) => `<td class="r">${esc(r[c])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>` : '<p class="muted" style="margin:0">미리 볼 수 있는 행이 없습니다.</p>'}</div>
    <div class="card"><h3>키 · 조건</h3><div class="fgrid">
      <div class="fld"><label>키(한 줄을 가리키는 열)<i></i></label><select class="inp" id="nK" onchange="NEWO.key=this.value">${colOpt(NEWO.key)}</select><span class="help">만든 뒤 엔터티 형식 페이지에서 키 값이 겹치는지 점검합니다.</span></div>
      <div class="fld full"><label>조건</label><div id="nC">${NEWO.filter.map((f) => dzCond(t, f)).join('')}</div><div><button type="button" class="btn ter sm" onclick="$('#nC').insertAdjacentHTML('beforeend', dzCond(objOrTbl('${esc(NEWO.base)}')))">${ic('plus', 16)}조건 추가</button></div><span class="help">조건을 비우면 테이블 전체가 엔터티 형식이 됩니다. 예) doc_type = 진단서</span></div></div></div>
  </div></div>
  ${pageFoot(`<button class="btn out" onclick="NEWO.label='';location.hash='design'">취소</button><button class="btn pri" ${lock()} ${t ? '' : 'disabled'} onclick="dzCreate(this)">만들기</button>`)}`;
}
let TBLS = [];
const objOrTbl = (n) => ({ cols: [...document.querySelectorAll('#nK option')].map((x) => x.value) });
const dzCond = (t, f = {}) => `<div class="row crow" style="flex-wrap:nowrap;margin-bottom:8px"><select class="inp cc" style="flex:1" aria-label="열">${(t?.cols || []).map((c) => `<option ${f.col === c ? 'selected' : ''}>${esc(c)}</option>`).join('')}</select><select class="inp co" style="width:110px" aria-label="연산자">${OPS.map((x) => `<option ${f.op === x ? 'selected' : ''}>${x}</option>`).join('')}</select><input class="inp cv" style="flex:1" placeholder="값" aria-label="값" value="${esc(f.value || '')}"><button class="ibtn" aria-label="조건 삭제" onclick="this.parentElement.remove()">${ic('x', 16)}</button></div>`;
async function dzCreate(btn) {
  const filter = [...document.querySelectorAll('#nC .crow')].map((r) => ({ col: r.querySelector('.cc').value, op: r.querySelector('.co').value, value: r.querySelector('.cv').value.trim() })).filter((f) => f.value);
  await run(btn, '', async () => {
    const r = await post('/onto/object', { label: NEWO.label, base: NEWO.base, key: $('#nK').value, filter });
    toast(`엔터티 형식이 추가되었습니다. (${r.nrows.toLocaleString()}행)`); NEWO.label = ''; ST = await get('/state'); dzOpen(r.name);
  });
}

// ── 엔터티 형식 페이지: 구성(속성 · 관계 · 메타데이터 · 세부 정보 · 계산 속성) / 인스턴스 ──
let NODE = { name: '', calc: null, dirty: false };
async function leaveNode() {
  if (!NODE.dirty) return true;
  const ok = await confirmBox({ title: '저장하지 않고 나가시겠습니까?', body: '입력한 내용은 저장되지 않습니다.', ok: '나가기', danger: true });
  if (ok) NODE.dirty = false;
  return ok;
}
const openNode = (name, tab = '') => dzOpen(name, tab === 'calc' ? '' : tab);
function dzObj(name, tab) {
  const o = objOf(name);
  NODE.name = name;
  const rels = ONTO.relations.filter((r) => r.a_tbl === name || r.b_tbl === name);
  const base = o.props.filter((p) => !p.calc), calcs = o.props.filter((p) => p.calc);
  CRUMB = [['온톨로지 설계', '#design'], [o.label]];
  const del = o.derived && !name.startsWith('same_');
  const head = `<div class="ph"><div class="t"><h1>${esc(o.label)}</h1><p>${o.desc ? esc(o.desc) : '설명이 없습니다. 메타데이터에 설명을 적으면 질문·규칙 AI가 이 엔터티 형식을 더 잘 알아봅니다.'}</p></div>
    <button class="btn out" onclick="DZ.sel='${esc(name)}';location.hash='design'">${ic('graph', 16)}그래프에서 보기</button>
    ${del ? `<div class="morew"><button class="ibtn" aria-label="더보기" aria-haspopup="menu" ${lock()} onclick="phMore(event)">${ic('dots', 20)}</button><div class="menu" id="moreMenu" role="menu"><button role="menuitem" class="dan" onclick="closeMenu();objDel('${esc(name)}')">${ic('x')}<span>엔터티 형식 삭제</span></button></div></div>` : ''}</div>
  <div class="tabs">${[['conf', '구성', ''], ['rows', '인스턴스', o.nrows]].map(([k, t, n]) => `<button class="${tab === k ? 'on' : ''}" onclick="dzOpen('${esc(name)}','${k === 'conf' ? '' : k}')">${t}${n !== '' ? `<span>${Number(n).toLocaleString()}</span>` : ''}</button>`).join('')}</div>`;
  if (tab === 'rows') {
    setTimeout(instList);
    return head + `<div class="lc"><div class="search">${ic('search')}<input class="inp" id="iQ" placeholder="검색어 입력" onkeydown="if(event.key==='Enter')instList()"></div><span class="cnt" id="iCnt"></span></div><div class="card flat" id="iOut"></div>`;
  }
  const tagOf = (p) => [p.col === o.key && '<span class="b info">키</span>', p.col === o.title && '<span class="b">보일 이름</span>', p.sensitive && '<span class="b warn">민감</span>', p.hidden && '<span class="b">숨김</span>'].filter(Boolean).join(' ');
  const nbIds = new Set([name]); rels.forEach((r) => { nbIds.add(r.a_tbl); nbIds.add(r.b_tbl); });
  const nbObjs = ONTO.objects.filter((x) => nbIds.has(x.name));
  setTimeout(() => keyCheck(name, o.key, '#dzKey'));
  return head + `<div class="g2">
    <div class="card"><h3>속성 <span class="b">${base.length}</span>${base.some((p) => !p.named) ? `<span class="b warn" data-tip="업무 이름을 붙이지 않은 칸은 칸 이름을 옮긴 임시 한글 이름으로 보입니다.">업무 이름 비어 있음 ${base.filter((p) => !p.named).length}</span><button class="btn xs out" ${lock()} onclick="fillNames('${esc(name)}')">이름 채우기</button>` : ''}<span class="sp"></span><button class="btn out sm" ${lock()} onclick="location.hash='${dzHref('obj', name, '&edit=props')}'">${ic('pencil', 16)}속성 편집</button></h3>
      <table class="t"><thead><tr><th>업무 이름</th><th>열</th><th>타입</th><th></th></tr></thead><tbody>${base.slice(0, 8).map((p) => `<tr><td>${esc(p.label)}${p.named ? '' : ' <span class="muted" data-tip="업무 이름이 없어 칸 이름으로 만든 임시 이름입니다.">(임시)</span>'}${p.syn ? `<div class="muted">동의어: ${esc(p.syn)}</div>` : ''}</td><td class="mono r">${esc(p.col)}</td><td class="r">${esc(p.type)}</td><td>${tagOf(p)}</td></tr>`).join('')}</tbody></table>
      ${base.length > 8 ? `<p class="muted" style="margin:8px 0 0">외 ${base.length - 8}개 · <span class="link" onclick="location.hash='${dzHref('obj', name, '&edit=props')}'">속성 편집에서 모두 보기</span></p>` : ''}</div>
    <div class="card"><h3>관계 <span class="b">${rels.length}</span><span class="sp"></span><button class="btn out sm" ${lock()} onclick="relDialog('${esc(name)}')">${ic('plus', 16)}관계 추가</button></h3>
      ${rels.length ? `<div class="gwrap mini">${svgGraph(nbObjs.map((x) => ({ id: x.name, label: x.label, sub: x.name })), rels.map((r) => ({ a: r.a_tbl, b: r.b_tbl })), { W: 640, H: 240, sel: name })}</div>
      <table class="t"><tbody>${rels.map((r) => `<tr class="click" onclick="location.hash='design?rel=${r.id}'"><td>${esc(lab(r.a_tbl))} → ${esc(lab(r.b_tbl))}${r.name ? `<div class="muted">${esc(r.name)}</div>` : ''}</td><td class="r nw">${(CARD[r.card] || r.card || '').split(' · ')[0]}</td><td class="num">${ic('chev', 12)}</td></tr>`).join('')}</tbody></table>`
      : empty('관계가 없습니다.', '다른 엔터티 형식과 이을 열을 골라 관계를 추가해 주세요.', '', true, 'link')}</div>
    <div class="card"><h3>메타데이터<span class="sp"></span><button class="btn out sm" ${lock()} onclick="metaPanel()">${ic('pencil', 16)}편집</button></h3>
      <dl class="dl"><dt>설명</dt><dd>${o.desc ? esc(o.desc) : '<span class="muted">없음</span>'}</dd><dt>키</dt><dd><span class="mono">${esc(o.key)}</span><div id="dzKey" class="muted">키를 점검하는 중입니다.</div></dd><dt>보일 이름</dt><dd>${o.title ? `<span class="mono">${esc(o.title)}</span>` : '<span class="muted">키 그대로</span>'}</dd></dl></div>
    <div class="card"><h3>세부 정보</h3>
      <dl class="dl"><dt>원본 테이블</dt><dd class="mono">${esc(o.base)}</dd><dt>조건</dt><dd>${o.filter.length ? `<span class="mono">${esc(fltText(o.filter))}</span>` : '<span class="muted">없음 · 테이블 전체</span>'}</dd><dt>행</dt><dd>${o.nrows.toLocaleString()}행 · <span class="link" onclick="dzOpen('${esc(name)}','rows')">인스턴스 보기</span></dd>${name.startsWith('same_') ? '<dt>만든 방식</dt><dd>같은 대상 묶기</dd>' : ''}</dl></div>
  </div>
  <div class="card" style="margin-top:16px"><h3>계산 속성 <span class="b">${calcs.length}</span><small>건수·합계·날짜 차이처럼 규칙과 질문에 쓸 값 · 계산은 프로그램(SQL)이 합니다.</small><span class="sp"></span><button class="btn out sm" ${lock()} onclick="calcPanel()">${ic('plus', 16)}계산 속성 추가</button></h3>
    ${calcs.length ? `<table class="t"><thead><tr><th>계산 속성</th><th>계산</th><th></th></tr></thead><tbody>${calcs.map((p) => `<tr><td>${esc(p.label)}<div class="muted mono">${esc(p.col)}</div></td><td class="r">${esc(p.text || '')}${p.desc ? `<div class="muted">${esc(p.desc)}</div>` : ''}</td>
      <td class="num"><button class="btn xs dan" ${lock()} onclick="calcDel('${esc(name)}','${esc(p.col)}')">삭제</button></td></tr>`).join('')}</tbody></table>` : empty('아직 계산 속성이 없습니다.', '예) 이 고객의 지난 1년 청구 건수 · 계약일부터 사고일까지 일수', '', true, 'chart')}</div>`;
}
function keyCheck(name, col, sel) {
  return get(`/onto/object/${encodeURIComponent(name)}/key?col=${encodeURIComponent(col)}`).then((k) => {
    const el = $(sel); if (!el) return;
    if (k.ok) { el.className = 'help ok'; el.innerHTML = `${k.rows.toLocaleString()}행 모두 값이 다릅니다.`; return; }
    const o = objOf(name), L = (c) => (o?.props.find((p) => p.col === c) || {}).label || c;
    el.className = 'keyfix';
    // 무엇이 문제고 어떻게 고치는지 — 값이 모두 다른 열로 바꾸거나, 두 열을 합친 키를 만듦
    el.innerHTML = `<div class="err-msg">${k.dups.length ? `같은 값이 있습니다: ${k.dups.slice(0, 3).map((d) => `${esc(d.v)}(${d.c}행)`).join(', ')}` : ''}${k.empty ? ` 빈 값 ${k.empty}행` : ''}</div>
      <p class="muted" style="margin:6px 0">키는 한 줄(인스턴스 하나)을 가리키는 열입니다. 지금은 다른 줄이 한 인스턴스로 합쳐져 값이 섞일 수 있습니다.${k.pair?.length ? ` 이 테이블은 한 줄이 "${esc(L(k.pair[0][0]))} 하나의 ${esc(L(k.pair[0][1]))} 하나"처럼 두 열이 함께 있어야 구분됩니다.` : ''}</p>
      ${sel === '#dzKey' && can('build') ? `<div class="row">${(k.single || []).map((c) => `<button class="btn xs out" onclick="keySet('${esc(name)}','${esc(c)}')">키를 ${esc(L(c))}(으)로 바꾸기</button>`).join('')}${(k.pair || []).slice(0, 2).map(([a, b]) => `<button class="btn xs ${b === (k.pair[0] || [])[1] && a === k.pair[0][0] ? 'pri' : 'out'}" onclick="keyPair('${esc(name)}','${esc(a)}','${esc(b)}')">${esc(L(a))} + ${esc(L(b))} 합친 키 만들기</button>`).join('')}${!k.single?.length && !k.pair?.length ? '<span class="muted">값이 모두 다른 열이나 두 열 짝이 없습니다. 원본 데이터를 확인해 주세요.</span>' : ''}</div>` : ''}`;
  }).catch(() => { const el = $(sel); if (el) el.textContent = ''; });
}
async function keySet(name, col) {
  const o = objOf(name);
  await post(`/onto/object/${encodeURIComponent(name)}/def`, { label: o.label, key: col, title: o.title || '', desc: o.desc || '', props: propsOf(o) });
  toast('키가 바뀌었습니다.'); refresh();
}
async function keyPair(name, a, b) {
  if (!(await confirmBox({ title: '두 열을 합친 키를 만드시겠습니까?', body: `${esc(a)}와 ${esc(b)}를 '-'로 이어 붙인 계산 속성을 만들어 키로 씁니다(Fabric 복합 키처럼). 원본 데이터는 그대로입니다.` }))) return;
  try { await post(`/onto/object/${encodeURIComponent(name)}/compound_key`, { cols: [a, b] }); toast('합친 키를 만들어 키로 바꿨습니다.'); } catch (e) { toast(e.message, true); }
  refresh();
}
// 메타데이터 편집 — 사이드 패널(엔터티 형식 이름 · 설명 · 키 · 보일 이름)
function metaPanel() {
  const o = objOf(NODE.name), opt = (sel, none) => (none ? `<option value="">${none}</option>` : '') + o.cols.map((c) => `<option value="${esc(c)}" ${sel === c ? 'selected' : ''}>${esc(c)}</option>`).join('');
  NODE.dirty = false;
  panel(`<div class="hd"><h2>메타데이터 편집</h2></div><div class="bd stack">
    <div class="fld"><label>엔터티 형식 이름<i></i></label><input class="inp" id="oLabel" value="${esc(o.label)}"></div>
    <div class="fld"><label>설명</label><textarea class="inp" id="oDesc" rows="3" placeholder="예) 고객이 낸 보험금 청구 한 건">${esc(o.desc || '')}</textarea><span class="help">질문·규칙 AI가 이 엔터티 형식이 무엇인지 알아보는 데 씁니다.</span></div>
    <div class="fld"><label>키(한 줄을 가리키는 열)<i></i></label><select class="inp" id="oKey">${opt(o.key)}</select><span class="help" id="oKeyChk">키를 점검하는 중입니다.</span></div>
    <div class="fld"><label>보일 이름(표시 속성)</label><select class="inp" id="oTitle">${opt(o.title, '키 그대로')}</select><span class="help">그래프와 답에 ID 대신 보일 이름입니다.</span></div></div>
  <div class="ft"><button class="btn out" onclick="closePanel()">취소</button><button class="btn pri" onclick="saveMeta(this)">저장</button></div>`, 'md');
  $('#spanel .bd').addEventListener('input', () => (NODE.dirty = true));
  const chk = () => keyCheck(o.name, $('#oKey').value, '#oKeyChk'); $('#oKey').onchange = () => { NODE.dirty = true; chk(); }; chk();
}
const propsOf = (o, fill = false) => o.props.filter((p) => !p.calc).map((p) => ({ col: p.col, label: p.named || fill ? p.label : '', type: p.type, desc: p.desc, syn: p.syn, hidden: !!p.hidden, sensitive: !!p.sensitive }));
// 이름 채우기 — 업무 이름이 빈 칸에 임시 한글 이름(설명 · 동의어 · 사전으로 만든 것)을 업무 이름으로 저장. 속성 바인딩 관리에서 고칠 수 있음
async function fillNames(name) {
  const o = objOf(name), n = o.props.filter((p) => !p.calc && !p.named).length;
  if (!(await confirmBox({ title: `업무 이름 ${n}개를 채우시겠습니까?`, body: '칸 이름을 옮긴 임시 이름(예: visit_type → 진료 유형)을 업무 이름으로 저장합니다. 저장한 뒤 속성 바인딩 관리에서 고칠 수 있습니다.' }))) return;
  await post(`/onto/object/${encodeURIComponent(name)}/def`, { label: o.label, key: o.key, title: o.title || '', desc: o.desc || '', props: propsOf(o, true) });
  toast(`업무 이름 ${n}개를 채웠습니다.`); refresh();
}
async function saveMeta(btn) {
  if (!checkRequired($('#spanel'))) return;
  const o = objOf(NODE.name);
  await run(btn, '', async () => { await post(`/onto/object/${encodeURIComponent(o.name)}/def`, { label: $('#oLabel').value.trim(), key: $('#oKey').value, title: $('#oTitle').value, desc: $('#oDesc').value.trim(), props: propsOf(o) }); NODE.dirty = false; closePanel(true); toast('메타데이터가 저장되었습니다.'); refresh(); });
}
// 계산 속성 추가 — 사이드 패널(문장 → 미리 보기 → 추가)
function calcPanel() {
  const o = objOf(NODE.name); NODE.calc = null; NODE.dirty = false;
  panel(`<div class="hd"><h2>계산 속성 추가</h2></div><div class="bd stack">
    <div class="alert info">${ic('info')}<div>문장으로 쓰면 AI가 계산식으로 바꾸고, <b>계산은 프로그램(SQL)</b>이 합니다. 미리 보기로 값을 확인한 뒤 추가합니다.</div></div>
    ${calcEx(o).length ? exBox('이 엔터티 형식의 관계 · 속성으로 만든 예시 · 누르면 입력칸이 채워집니다', calcEx(o).map((t) => `<button type="button" onclick="$('#cTxt').value=this.dataset.t;$('#cTxt').dispatchEvent(new Event('input'))" data-t="${esc(t)}">${esc(t)}</button>`).join('')) : ''}
    <div class="fld"><label>무엇을 계산할지<i></i></label><textarea class="inp" id="cTxt" rows="3" placeholder="예) 이 고객의 지난 1년 청구 건수 / 계약일부터 사고일까지 일수"></textarea></div>
    <div><button class="btn out sm" id="cGo">${ic('robot', 16)}미리 보기</button></div><div id="cOut"></div></div>
  <div class="ft"><button class="btn out" onclick="closePanel()">취소</button><button class="btn pri" id="cAdd" disabled data-tip="미리 보기로 값을 확인한 뒤 추가할 수 있습니다." onclick="calcAdd(this)">추가</button></div>`, 'lg');
  $('#cTxt').oninput = () => (NODE.dirty = true);
  $('#cGo').onclick = (e) => run(e.currentTarget, '', async () => {
    const t = $('#cTxt').value.trim(); if (!t) { toast('계산 내용을 입력해 주세요.', true); return; }
    const c = await post('/onto/calc/compile', { obj: o.name, text: t }); NODE.calc = c;
    $('#cOut').innerHTML = `<div class="card" style="padding:16px"><div class="row"><b>${esc(c.label)}</b><span class="muted mono">${esc(c.col)}</span><span class="sp"></span><span class="b">${{ expr: '같은 줄 계산', agg: '이어진 줄 집계', lookup: '이어진 값 가져오기' }[c.calc.kind] || ''}</span></div>
      <p style="margin:8px 0">${esc(c.plain || '')}</p><table class="t"><thead><tr><th>${esc(o.title || o.key)}</th><th>${esc(c.label)}</th></tr></thead><tbody>${c.preview.map((r) => `<tr><td class="mono">${esc(r.key)}</td><td class="mono">${esc(r.value ?? '')}</td></tr>`).join('')}</tbody></table></div>`;
    $('#cAdd').disabled = false; delete $('#cAdd').dataset.tip;
  });
}
async function instList() {
  if (!$('#iOut')) return;
  const r = await get(`/objects/${encodeURIComponent(NODE.name)}/rows?q=${encodeURIComponent($('#iQ')?.value || '')}&n=30`);
  const show = r.cols.slice(0, 8);
  $('#iCnt').textContent = `총 ${r.total.toLocaleString()}행`;
  $('#iOut').innerHTML = r.rows.length ? `<table class="t"><thead><tr>${show.map((c) => `<th>${esc(r.labels?.[c] || c)}</th>`).join('')}</tr></thead><tbody>${r.rows.map((x) => `<tr class="click" onclick="instPanel('${esc(NODE.name)}','${esc(x[r.key])}')">${show.map((c) => `<td class="r">${esc(x[c])}</td>`).join('')}</tr>`).join('')}</tbody></table><p class="muted" style="padding:8px 0">줄을 누르면 값 · 계산 과정을 보고, 가정 바꿔 보기를 할 수 있습니다.</p>`
    : empty('조건에 맞는 값이 없습니다.', '검색어를 조정해 주세요.', '', true, 'search');
}
// 속성 편집 — 전체 페이지(Fabric 속성 바인딩처럼), 아래 저장/취소. 저장 안 하고 나가면 확인
function dzProps(name) {
  const o = objOf(name), base = o.props.filter((p) => !p.calc);
  NODE.name = name; NODE.dirty = false;
  CRUMB = [['온톨로지 설계', '#design'], [o.label, '#' + dzHref('obj', name)], ['속성 편집']];
  setTimeout(() => { const t = $('table.edit'); if (!t) return; if (!can('build')) t.querySelectorAll('input,select').forEach((x) => (x.disabled = true)); else t.addEventListener('input', () => (NODE.dirty = true)); });
  return `<div class="ph"><div class="t"><h1>속성 편집 · ${esc(o.label)}</h1><p>업무 이름·설명·동의어는 질문·규칙 AI가 열 이름 대신 봅니다. 숨김 = 질문·규칙에 쓰지 않음 · 민감 = 현업에게 ●●●로 가림</p></div></div>
  <div class="card flat"><div style="overflow:auto"><table class="t edit"><thead><tr><th>원본 열</th><th>업무 이름</th><th style="width:96px">타입</th><th>설명</th><th>동의어</th><th class="c" data-tip="질문·규칙에 쓰지 않음">숨김</th><th class="c" data-tip="현업에게 값을 가림">민감</th></tr></thead><tbody>
  ${base.map((p) => `<tr data-col="${esc(p.col)}"><td class="mono">${esc(p.col)}${p.col === o.key ? ' <span class="b info">키</span>' : ''}</td><td><input class="inp xs p-lab" aria-label="${esc(p.col)} 업무 이름" value="${p.named ? esc(p.label) : ''}" placeholder="${esc(p.label)} (임시 이름)"></td>
    <td><select class="inp xs p-typ" aria-label="${esc(p.col)} 타입">${['글자', '숫자', '날짜'].map((t) => `<option ${p.type === t ? 'selected' : ''}>${t}</option>`).join('')}</select></td>
    <td><input class="inp xs p-desc" aria-label="${esc(p.col)} 설명" value="${esc(p.desc)}" placeholder="뜻·형식"></td><td><input class="inp xs p-syn" aria-label="${esc(p.col)} 동의어" value="${esc(p.syn)}" placeholder="예) 보장, 담보"></td>
    <td class="c"><input type="checkbox" aria-label="${esc(p.col)} 숨김" class="p-hid" ${p.hidden ? 'checked' : ''}></td><td class="c"><input type="checkbox" aria-label="${esc(p.col)} 민감" class="p-sen" ${p.sensitive ? 'checked' : ''}></td></tr>`).join('')}</tbody></table></div></div>
  ${pageFoot(`<button class="btn out" onclick="location.hash='${dzHref('obj', name)}'">취소</button><button class="btn pri" ${lock()} onclick="saveDef(this)">저장</button>`)}`;
}
async function saveDef(btn) {
  const o = objOf(NODE.name);
  const props = [...document.querySelectorAll('table.edit tbody tr')].map((tr) => ({ col: tr.dataset.col, label: tr.querySelector('.p-lab').value.trim(), type: tr.querySelector('.p-typ').value, desc: tr.querySelector('.p-desc').value.trim(), syn: tr.querySelector('.p-syn').value.trim(), hidden: tr.querySelector('.p-hid').checked, sensitive: tr.querySelector('.p-sen').checked }));
  await run(btn, '', async () => { await post(`/onto/object/${encodeURIComponent(o.name)}/def`, { label: o.label, key: o.key, title: o.title || '', desc: o.desc || '', props }); NODE.dirty = false; toast('속성이 저장되었습니다.'); dzOpen(o.name); });
}
async function calcAdd(btn) { const c = NODE.calc; await run(btn, '', async () => { await post('/onto/calc', { obj: NODE.name, col: c.col, label: c.label, calc: { ...c.calc, plain: c.plain } }); NODE.dirty = false; closePanel(true); toast('계산 속성이 추가되었습니다.'); refresh(); }); }
async function calcDel(obj, col) {
  if (!(await confirmBox({ title: '계산 속성을 삭제하시겠습니까?', body: '이 속성을 쓰는 규칙·메트릭은 실행할 수 없게 됩니다. 버전 기록에서 복원할 수 있습니다.', ok: '삭제', danger: true }))) return;
  await del(`/onto/calc/${encodeURIComponent(obj)}/${encodeURIComponent(col)}`); toast('계산 속성이 삭제되었습니다.'); refresh();
}
async function objDel(name) {
  if (!(await confirmBox({ title: '엔터티 형식을 삭제하시겠습니까?', body: '이 엔터티 형식의 관계와 속성 정의가 함께 삭제됩니다. 원본 테이블은 남습니다. 버전 기록에서 복원할 수 있습니다.', ok: '삭제', danger: true }))) return;
  await del('/onto/object/' + encodeURIComponent(name)); DZ.sel = ''; toast('엔터티 형식이 삭제되었습니다.');
  if (location.hash === '#design') refresh(); else location.hash = 'design';
}
async function refreshQuiet() { ST = await get('/state'); renderNav(); }

// ── 관계 페이지: 원본 엔터티 형식 · 관계 · 대상 엔터티 형식 세 칸(Fabric 관계 세부 정보처럼) ──
let NREL = null;
// 관계 추가: 이름 · 원본 · 대상을 묻는 창 → 열을 고르는 관계 페이지(Fabric 흐름)
function relDialog(a = '') {
  const objs = ONTO.objects, a0 = objOf(a) ? a : objs[0]?.name, b0 = (objs.find((x) => x.name !== a0) || objs[0])?.name;
  const opt = (sel) => objs.map((o) => `<option value="${esc(o.name)}" ${sel === o.name ? 'selected' : ''}>${esc(o.label)}</option>`).join('');
  formModal('관계 추가', `<div class="stack"><div class="fld"><label>관계 이름</label><input class="inp" id="rdN" placeholder="예) 청구한 계약"></div>
    <div class="fld"><label>원본 엔터티 형식<i></i></label><select class="inp" id="rdA">${opt(a0)}</select></div>
    <div class="fld"><label>대상 엔터티 형식<i></i></label><select class="inp" id="rdB">${opt(b0)}</select><span class="help">다음 화면에서 두 엔터티 형식을 이을 열을 고릅니다.</span></div><div id="rdEx"></div></div>`, '다음', async () => {
    NREL = { from: '#design?rel=new', a: $('#rdA').value, ac: '', b: $('#rdB').value, bc: '', name: $('#rdN').value.trim() };
    location.hash = 'design?rel=new';
  });
  relEx('#rdEx');
}
function dzRel(id, a) {
  CRUMB = [['온톨로지 설계', '#design'], [id === 'new' ? '관계 추가' : '관계']];
  if (id !== 'new') {
    const r = ONTO.relations.find((x) => String(x.id) === id);
    if (!r) { history.replaceState(null, '', '#design'); toast('관계를 찾을 수 없습니다. 삭제되었을 수 있습니다.', true); return dzHome(); }
    CRUMB[1] = [`${lab(r.a_tbl)} → ${lab(r.b_tbl)}`];
    const side = (t, c, h) => `<div class="card r3"><div class="r3h">${h}</div><b class="r3o" onclick="dzOpen('${esc(t)}')">${ic('cube', 16)}${esc(lab(t))}</b><dl class="dl"><dt>열</dt><dd class="mono">${esc(c)}</dd></dl></div>`;
    return `<div class="ph"><div class="t"><h1>${esc(lab(r.a_tbl))} → ${esc(lab(r.b_tbl))}</h1><p>${r.name ? esc(r.name) + ' · ' : ''}${esc(r.by)}${r.at ? ` · ${fmtT(r.at)}` : ''}</p></div><button class="btn dan" ${lock()} onclick="delRel(${r.id})">${ic('x', 16)}삭제</button></div>
    <div class="rel3">${side(r.a_tbl, r.a_col, '원본 엔터티 형식')}<span class="r3a">${ic('chev', 20)}</span>
      <div class="card r3"><div class="r3h">관계</div><b>${esc(r.name || '이름 없음')}</b><dl class="dl"><dt>몇 대 몇</dt><dd>${CARD[r.card] || r.card || '-'}</dd><dt>값 겹침</dt><dd>${r.ov.a ? `<span class="tag ${r.ov.hit === r.ov.a ? 'ok' : r.ov.hit ? 'warn' : 'bad'}">${r.ov.hit}개 / ${r.ov.a}개</span><div class="muted">원본 열 값 중 대상 열에도 있는 개수</div>` : '<span class="tag">값 없음</span>'}</dd></dl></div>
      <span class="r3a">${ic('chev', 20)}</span>${side(r.b_tbl, r.b_col, '대상 엔터티 형식')}</div>
    ${pageFoot(`<button class="btn out" onclick="history.length > 1 ? history.back() : (location.hash='design')">닫기</button>`)}`;
  }
  const objs = ONTO.objects;
  if (!NREL || NREL.from !== location.hash) { const a0 = objOf(a) ? a : objs[0]?.name; NREL = { from: location.hash, a: a0, ac: '', b: (objs.find((x) => x.name !== a0) || objs[0])?.name, bc: '', name: '' }; }
  const N = NREL, oa = objOf(N.a), ob = objOf(N.b);
  // 처음엔 두 엔터티 형식에 같은 이름으로 있는 열을 골라 둠(대상 키 우선)
  const same = (oa?.cols || []).filter((c) => ob?.cols.includes(c));
  if (!oa?.cols.includes(N.ac)) N.ac = (ob && same.includes(ob.key) ? ob.key : same[0]) || oa?.key || oa?.cols[0] || '';
  if (!ob?.cols.includes(N.bc)) N.bc = ob?.cols.find((c) => c === N.ac) || ob?.key || ob?.cols[0] || '';
  const oOpt = (sel) => objs.map((o) => `<option value="${esc(o.name)}" ${sel === o.name ? 'selected' : ''}>${esc(o.label)}</option>`).join('');
  const cOpt = (o, sel) => (o?.cols || []).map((c) => `<option ${sel === c ? 'selected' : ''}>${esc(c)}</option>`).join('');
  setTimeout(relOv);
  return `<div class="ph"><div class="t"><h1>관계 추가</h1><p>두 엔터티 형식에서 같은 값을 가진 열을 고르면 관계가 됩니다. 값 겹침으로 실제로 이어지는지 바로 확인합니다.</p></div><button class="btn out" onclick="relSwap()">${ic('refresh', 16)}방향 바꾸기</button></div>
  <div class="rel3">
    <div class="card r3"><div class="r3h">원본 엔터티 형식</div><div class="fld"><label>엔터티 형식<i></i></label><select class="inp" onchange="NREL.a=this.value;NREL.ac='';render()">${oOpt(N.a)}</select></div><div class="fld"><label>열<i></i></label><select class="inp" id="rAc" onchange="NREL.ac=this.value;relOv()">${cOpt(oa, N.ac)}</select></div></div>
    <span class="r3a">${ic('chev', 20)}</span>
    <div class="card r3"><div class="r3h">관계</div><div class="fld"><label>관계 이름</label><input class="inp" id="rN" value="${esc(N.name)}" placeholder="예) 청구한 계약" oninput="NREL.name=this.value"></div><div id="rOv" class="ovbox muted">값 겹침을 확인하는 중입니다.</div></div>
    <span class="r3a">${ic('chev', 20)}</span>
    <div class="card r3"><div class="r3h">대상 엔터티 형식</div><div class="fld"><label>엔터티 형식<i></i></label><select class="inp" onchange="NREL.b=this.value;NREL.bc='';render()">${oOpt(N.b)}</select></div><div class="fld"><label>열<i></i></label><select class="inp" id="rBc" onchange="NREL.bc=this.value;relOv()">${cOpt(ob, N.bc)}</select></div></div>
  </div>
  ${pageFoot(`<button class="btn out" onclick="NREL=null;history.length > 1 ? history.back() : (location.hash='design')">취소</button><button class="btn pri" ${lock()} onclick="relSave(this)">저장</button>`)}`;
}
function relSwap() { const N = NREL; [N.a, N.b, N.ac, N.bc] = [N.b, N.a, N.bc, N.ac]; render(); }
async function relOv() {
  const N = NREL, el = $('#rOv'); if (!el || !N) return;
  try {
    const r = await post('/onto/overlap', { a_tbl: N.a, a_col: N.ac, b_tbl: N.b, b_col: N.bc });
    const cls = r.hit === r.a && r.a ? 'ok' : r.hit ? 'warn' : 'bad';
    el.className = 'ovbox'; el.innerHTML = `<div class="row"><span class="muted">값 겹침</span><span class="tag ${cls}">${r.hit}개 / ${r.a}개</span></div><p class="muted" style="margin:4px 0 0">${r.hit ? `원본 열 값 ${r.a}개 중 ${r.hit}개가 대상 열에 있습니다.` : '겹치는 값이 없습니다. 열을 다시 골라 주세요.'}</p>`;
  } catch { el.textContent = ''; }
}
async function relSave(btn) {
  const N = NREL;
  await run(btn, '', async () => { await post('/onto/relation', { a_tbl: N.a, a_col: N.ac, b_tbl: N.b, b_col: N.bc, name: N.name.trim() }); toast('관계가 추가되었습니다.'); const a = N.a; NREL = null; dzOpen(a); });
}
async function delRel(id) {
  if (!(await confirmBox({ title: '관계를 삭제하시겠습니까?', body: '이 관계를 쓰는 규칙·질문은 미연결로 멈춥니다. 버전 기록에서 복원할 수 있습니다.', ok: '삭제', danger: true }))) return;
  await del('/onto/relation/' + id); toast('관계가 삭제되었습니다.'); location.hash = 'design';
}

// 같은 대상 묶기(엔터티 형식 해소)
let ER = { a: '', b: '', how: 'loose', res: null, pairs: [] };
function erOpen() {
  const objs = ONTO.objects.filter((o) => !o.name.startsWith('same_'));
  ER.a = ER.a || objs[0]?.name; ER.b = ER.b || (objs[1] || objs[0])?.name; ER.res = null;
  const opt = (sel) => objs.map((o) => `<option value="${esc(o.name)}" ${sel === o.name ? 'selected' : ''}>${esc(o.label)}</option>`).join('');
  const cols = (t) => (ONTO.objects.find((o) => o.name === t)?.cols || []).map((c) => `<option>${esc(c)}</option>`).join('');
  const pairRow = () => `<div class="row prow" style="flex-wrap:nowrap;margin-top:8px"><select class="inp pa" style="flex:1">${cols(ER.a)}</select><span>=</span><select class="inp pb" style="flex:1">${cols(ER.b)}</select><button class="ibtn" aria-label="열 짝 삭제" onclick="this.parentElement.remove()">${ic('x', 16)}</button></div>`;
  $('#modal').className = 'modal xl';
  $('#modal').innerHTML = (`<div class="mh"><h2>같은 대상 묶기</h2></div><div class="mb stack" style="color:var(--ink)">
    <div class="alert info">${ic('info')}<div>두 엔터티 형식에서 같은 대상(같은 사람·회사 등)을 여러 열로 견줘 찾습니다. 확정한 쌍은 <b>같은 대상 목록</b> 엔터티 형식으로 저장되어 두 엔터티 형식을 잇습니다.</div></div>
    <div class="fgrid"><div class="fld"><label>기준 엔터티 형식<i></i></label><select class="inp" id="eA">${opt(ER.a)}</select></div><div class="fld"><label>비교할 엔터티 형식<i></i></label><select class="inp" id="eB">${opt(ER.b)}</select></div></div>
    <div class="fld"><label>견줄 열<i></i></label><div id="eP">${pairRow()}</div><div><button type="button" class="btn ter sm" id="ePAdd" style="margin-top:8px">${ic('plus', 16)}견줄 열 추가</button></div><span class="help">여러 열을 넣으면 모두 맞아야 같은 대상입니다. 예) 이름 = 성명, 생년월일 = 생일</span></div>
    <div class="fld"><label>기준<i></i></label><div class="seg" id="eHow">${[['exact', '정확히 같음'], ['loose', '테이블기 차이 무시'], ['similar', '비슷함(85% 이상)']].map(([k, t]) => `<button class="${ER.how === k ? 'on' : ''}" data-k="${k}">${t}</button>`).join('')}</div><span class="help">테이블기 차이 무시 = 공백·대소문자·하이픈·괄호를 빼고 견줍니다.</span></div>
    <div><button class="btn out" id="eRun">${ic('search', 16)}같은 대상 찾기</button></div><div id="eOut"></div></div>
    <div class="mf"><button class="btn out" id="mNo">취소</button><button class="btn pri" id="eSave" disabled data-tip="같은 대상을 찾은 후 저장할 수 있습니다.">저장</button></div>`);
  $('#modalBg').classList.add('on');
  const erClose = () => { if (!modalBusy) { modalClose = null; $('#modalBg').classList.remove('on'); } };
  modalClose = erClose; $('#mNo').onclick = erClose;
  $('#eA').onchange = () => { ER.a = $('#eA').value; erOpen(); }; $('#eB').onchange = () => { ER.b = $('#eB').value; erOpen(); };
  $('#ePAdd').onclick = () => $('#eP').insertAdjacentHTML('beforeend', pairRow());
  document.querySelectorAll('#eHow button').forEach((b) => (b.onclick = () => { ER.how = b.dataset.k; document.querySelectorAll('#eHow button').forEach((x) => x.classList.toggle('on', x === b)); }));
  $('#eRun').onclick = (e) => run(e.currentTarget, '', async () => {
    ER.pairs = [...document.querySelectorAll('#eP .prow')].map((r) => [r.querySelector('.pa').value, r.querySelector('.pb').value]);
    ER.res = await post('/onto/er/run', { a: ER.a, b: ER.b, pairs: ER.pairs, how: ER.how });
    const r = ER.res;
    $('#eOut').innerHTML = `<div class="sec-t sm">찾은 쌍 ${r.total.toLocaleString()}개 <small>${esc(lab(ER.a))} ${r.a_rows.toLocaleString()}행 · ${esc(lab(ER.b))} ${r.b_rows.toLocaleString()}행 견줌 · 확인할 짝부터</small></div>
      ${r.multi ? `<div class="alert warn" style="margin-bottom:12px">${ic('warn')}<div>${esc(lab(ER.a))}의 한 줄이 여러 대상과 이어진 쌍이 ${r.multi}개 있습니다(예: 동명이인). 견줄 열을 더 넣어 좁히거나, 맞는 쌍만 선택해 주세요.</div></div>` : ''}
      ${r.pairs.length ? `<div style="overflow:auto;max-height:420px"><table class="t"><thead><tr><th style="width:48px"><input type="checkbox" aria-label="전체 선택" id="eAll" ${r.multi ? '' : 'checked'}></th><th>${esc(lab(ER.a))}</th><th>${esc(lab(ER.b))}</th><th>점수</th></tr></thead><tbody>${r.pairs.map((p, i) => `<tr><td><input type="checkbox" aria-label="이 쌍 선택" class="eC" data-i="${i}" ${p.multi ? '' : 'checked'}></td><td><span class="mono">${esc(p.a_key)}</span><div class="muted">${esc(p.a.join(' · '))}</div></td><td><span class="mono">${esc(p.b_key)}</span><div class="muted">${esc(p.b.join(' · '))}</div></td><td>${p.score < 1 || p.multi ? `<span class="dotb warn">${p.score.toFixed(2)}${p.multi ? ' · 여러 쌍' : ''}</span>` : `<span class="muted mono">${p.score.toFixed(2)}</span>`}</td></tr>`).join('')}</tbody></table></div>`
      : empty('같은 대상이 없습니다.', '견줄 열이나 기준을 바꿔 주세요.', '', true, 'search')}`;
    const upd = () => { const n = document.querySelectorAll('.eC:checked').length; $('#eSave').disabled = !n || !can('build'); $('#eSave').textContent = n ? `선택한 ${n}쌍 저장` : '저장'; if (!can('build')) $('#eSave').dataset.tip = LOCK.build; else if (!n) $('#eSave').dataset.tip = '저장할 쌍을 선택해 주세요.'; else delete $('#eSave').dataset.tip; };
    if ($('#eAll')) $('#eAll').onchange = (ev) => { document.querySelectorAll('.eC').forEach((c) => (c.checked = ev.target.checked)); upd(); };
    document.querySelectorAll('.eC').forEach((c) => (c.onchange = upd)); upd();
  });
  $('#eSave').onclick = (e) => run(e.currentTarget, '', async () => {
    const matches = [...document.querySelectorAll('.eC:checked')].map((c) => ER.res.pairs[+c.dataset.i]);
    const r = await post('/onto/er/apply', { a: ER.a, b: ER.b, matches, pairs: ER.pairs, how: ER.how });
    erClose(); toast(`같은 대상 ${r.pairs}쌍이 저장되었습니다. 엔터티 형식 목록에서 확인할 수 있습니다.`); refresh();
  });
}

// ── 메트릭 ── 자주 보는 여러 건 계산을 이름 붙여 저장
let METS = [];
P.metrics = async () => {
  METS = await get('/metrics');
  return `<div class="ph"><div class="t"><h1>메트릭</h1><p><b>여러 건을 모아 숫자 하나나 테이블을 냅니다</b>(건수·합계·평균·순위). 이름 붙여 두면 같은 메트릭을 물을 때 늘 같은 계산식을 씁니다. 한 건씩 해당/아님을 판정하는 것은 규칙입니다.</p></div></div>
  <div class="lc"><span class="cnt">총 ${METS.length}개</span><span class="sp"></span><button class="btn pri" ${ST.objects ? lock() : 'disabled data-tip="온톨로지 설계에서 엔터티 형식을 생성한 후 메트릭을 생성할 수 있습니다."'} onclick="metricModal()">${ic('plus')}메트릭 생성</button></div>
  <div class="card flat">${METS.length ? `<table class="t"><thead><tr><th>메트릭</th><th>요청 문장</th><th>계산 방법</th><th>만든 사람</th><th></th></tr></thead><tbody>
    ${METS.map((m) => `<tr><td><b>${esc(m.name)}</b></td><td class="r">${esc(m.text)}</td><td class="r">${esc(m.plain)}</td><td class="r">${esc(m.by)}</td>
      <td class="num"><div class="row" style="flex-wrap:nowrap;justify-content:flex-end"><button class="btn xs out" onclick="metricRun(${m.id},this)">${ic('play', 12)}실행</button><button class="btn xs dan" ${lock()} onclick="metricDel(${m.id})">삭제</button></div></td></tr>`).join('')}</tbody></table>`
    : empty('아직 메트릭이 없습니다.', '메트릭을 생성하거나, 질문 기록의 계산 결과에서 [메트릭으로 저장]을 눌러 주세요.', ST.objects && can('build') ? `<button class="btn pri" onclick="metricModal()">메트릭 생성</button>${await exChips('metric', 'exMetricNew')}` : '', false, 'chart')}</div>
  <div class="guide" style="margin-top:24px"><b>메트릭과 규칙의 차이</b>규칙은 한 건씩 조건을 보고 판단합니다. 메트릭은 여러 건을 모아 세거나 합칩니다. 건마다 필요한 건수·날짜 차이는 엔터티 형식의 계산 속성으로 만듭니다.</div>`;
};
function metricModal(pre = null) {
  let made = pre?.spec ? pre : null;
  $('#modal').className = 'modal lg';
  $('#modal').innerHTML = `<div class="mh"><h2>메트릭 생성</h2></div><div class="mb stack" style="color:var(--ink)">
    <div class="fld"><label>무엇을 셀지<i></i></label><textarea class="inp" id="mTxt" rows="3" placeholder="예) 질병군별 청구 건수 / 이번 달 지급 보류 청구의 청구 금액 합계">${esc(pre?.text || '')}</textarea></div>
    <div id="mEx"></div><div><button class="btn out sm" id="mGo">${ic('robot', 16)}미리 보기</button></div><div id="mOut"></div></div>
    <div class="mf"><button class="btn out" id="mNo">취소</button><button class="btn pri" id="mSave" ${made ? '' : 'disabled data-tip="미리 보기를 확인한 후 생성할 수 있습니다."'}>생성</button></div>`;
  $('#modalBg').classList.add('on');
  const close = () => { if (!modalBusy) { modalClose = null; $('#modalBg').classList.remove('on'); } };
  modalClose = close; $('#mNo').onclick = close;
  const show = () => { $('#mOut').innerHTML = `<div class="fld"><label>메트릭 이름<i></i></label><input class="inp" id="mName" value="${esc(made.name)}"></div><p class="muted" style="margin:8px 0">${esc(made.plain || '')}</p>${made.preview ? resView(made.preview, { max: 8, sql: made.preview.sql }) : ''}`; $('#mSave').disabled = false; delete $('#mSave').dataset.tip; };
  if (made) show();
  if (!pre) exChips('metric', 'exMetric').then((h) => { if ($('#mEx')) $('#mEx').innerHTML = h; });
  $('#mTxt').oninput = () => { made = null; $('#mSave').disabled = true; };
  $('#mGo').onclick = (e) => { if (!checkRequired($('#modal'))) return; run(e.currentTarget, '', async () => { made = await post('/metrics/compile', { text: $('#mTxt').value.trim() }); show(); }); };
  $('#mSave').onclick = (e) => { if (!checkRequired($('#modal'))) return; run(e.currentTarget, '', async () => { await post('/metrics', { name: $('#mName').value.trim(), text: made.text || $('#mTxt').value.trim(), spec: made.spec }); close(); toast('메트릭이 생성되었습니다.'); refresh(); }); };
}
async function metricRun(id, btn) {
  await run(btn, '', async () => {
    const r = await post(`/metrics/${id}/run`), m = METS.find((x) => x.id === id);
    panel(`<div class="hd"><h2>${esc(m.name)}</h2><button class="ibtn" aria-label="닫기" onclick="closePanel()">${ic('x', 20)}</button></div><div class="bd stack"><p class="muted" style="margin:0">${esc(m.plain)}</p>${resView(r, { sql: r.sql })}</div>`, 'xl');
  });
}
async function metricDel(id) {
  if (!(await confirmBox({ title: '메트릭을 삭제하시겠습니까?', body: '변경 이력에서 복원할 수 있습니다.', ok: '삭제', danger: true }))) return;
  await del('/metrics/' + id); toast('메트릭이 삭제되었습니다.'); refresh();
}
async function saveAsMetric(aid) {
  const a = await get('/asks/' + aid);
  metricModal({ name: a.tpl || a.q.slice(0, 20), text: a.q, spec: a.spec, plain: '', preview: a.table ? { ...a.table, sql: '' } : null });
}

// ── 전체 판정 ── 건마다 규칙을 모두 돌려 결과를 엔터티 형식으로 저장
async function runAll(btn) {
  const start = $('#raStart').value;
  if (!(await confirmBox({ title: '전체 판정을 실행하시겠습니까?', body: `${esc(lab(start))}의 모든 건(최대 2,000건)에 사용 중인 규칙을 돌립니다. 결과는 <b>판정 결과</b> 엔터티 형식으로 저장되어 질문·메트릭에 쓸 수 있습니다.`, ok: '실행' }))) return;
  await run(btn, '', async () => {
    const r = await post('/rules/run_all', { start });
    const routes = Object.entries(r.route);
    const cols = r.cols.filter((c) => c !== 'route' || r.rows.some((x) => x.route));
    $('#raOut').innerHTML = `<div class="alert ok" style="margin-top:16px">${ic('check')}<div><b>${esc(lab(start))} 판정 결과</b> 엔터티 형식으로 저장되었습니다.${r.total >= 2000 ? ' 앞 2,000건만 판정했습니다.' : ''}</div><button class="btn ter act" onclick="location.hash='metrics'">메트릭으로 만들기</button></div>
      <div class="row" style="margin:16px 0 8px;gap:8px">${r.rules.map((x) => `<span class="b ${x.hits ? 'warn' : ''}">${esc(x.name)} ${x.hits}건</span>`).join('')}</div>
      ${routes.length > 1 || routes[0]?.[0] !== '(분류 없음)' ? `<div class="sec-t sm">분류 결과</div>${resView({ cols: ['grp', 'val'], rows: routes.map(([k, v]) => ({ grp: k, val: v })).sort((a, b) => b.val - a.val) })}` : ''}
      <div class="sec-t sm" style="margin-top:16px">건별 결과 <small>${r.total.toLocaleString()}건 중 앞 50건</small></div>
      <div style="overflow:auto"><table class="t"><thead><tr>${cols.map((c) => `<th>${esc(c === 'key' ? lab(start) : r.labels[c] || c)}</th>`).join('')}</tr></thead><tbody>${r.rows.slice(0, 50).map((x) => `<tr>${cols.map((c) => `<td class="${c === 'key' ? 'mono nw' : 'r'}">${x[c] === '해당' ? '<span class="b warn">해당</span>' : esc(x[c] || (c === 'hits' ? '-' : ''))}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
`;
    refreshQuiet();
  });
}

// ── 본문 검색 ── 그래프로 거르고 벡터로 고름
async function docSearch(btn = $('#sQ')) {
  const q = $('#sQ').value.trim(); if (!q) { toast('검색어를 입력해 주세요.', true); return; }
  const obj = $('#sObj').value, val = $('#sVal').value.trim();
  if (obj && !val) { toast('좁힐 값을 입력해 주세요.', true); return; }
  await run(btn, '', async () => {
    const r = await get(`/search?q=${encodeURIComponent(q)}&obj=${encodeURIComponent(obj)}&value=${encodeURIComponent(val)}`);
    const words = q.split(/\s+/).filter((w) => w.length > 1);
    const hl = (t) => words.reduce((s, w) => s.split(esc(w)).join(`<mark>${esc(w)}</mark>`), esc(t));
    $('#sOut').innerHTML = `<p class="muted" style="margin:16px 0 8px">${r.via ? `<b>${esc(r.via.obj)} ${esc(r.via.value)}</b>에 관계로 이어진 문서 ${r.via.docs.length}건 안에서 찾았습니다.` : '전체 문서에서 찾았습니다.'} · ${esc(r.mode)}</p>
      ${r.hits.length ? r.hits.map((h) => `<button class="snip" onclick="openDoc('${esc(h.doc_id)}')"><div class="row"><b class="mono">${esc(h.doc_id)}</b><span class="b">${h.page}쪽</span><span class="sp"></span><span class="muted mono" title="비슷한 정도(1에 가까울수록 비슷)">${h.score.toFixed(2)}</span></div><p>${hl(h.text).replace(/\n/g, '<br>')}</p></button>`).join('')
      : `<div class="card">${empty('찾은 본문이 없습니다.', r.via && !r.via.docs.length ? '이 값에 이어진 문서가 없습니다. 문서 읽기 결과(읽은 값)가 이 엔터티 형식과 관계로 이어져 있는지 확인해 주세요.' : '검색어를 바꿔 주세요.', '', true, 'search')}</div>`}`;
  });
}

// ── 데이터 에이전트(현업 첫 화면) ──
// 데이터 에이전트 — Fabric 데이터 에이전트 흐름: 가운데 대화 + 답마다 [실행 단계] 펼치기, 위 리본(구축 담당: 에이전트 지침 · 예제 쿼리 / 공통: 새 대화)
//  대화는 이 화면에만 남고 새로 고침하면 비워짐(Fabric처럼). 지난 질문은 질문 기록에 남음
let CHAT = [];
P.ask = async () => {
  setTimeout(() => agentEx('#agEx'));
  const gold = await get('/golden');
  const ex = [...new Set(gold.map((g) => g.q))].slice(0, 4);
  const ready = ST.objects > 0, b = !isUser();
  return `<div class="ph"><div class="t"><h1>데이터 에이전트</h1><p>연결된 데이터로 답하고, 답마다 근거와 실행 단계를 함께 보여 줍니다.</p></div></div>
  <div class="ribbon" role="toolbar" aria-label="질문 에이전트">${b ? `<button class="rb" onclick="instrPanel()">${ic('pencil', 16)}에이전트 지침</button><button class="rb" onclick="exPanel()">${ic('star', 16)}예제 쿼리</button><i class="rsep"></i>` : ''}
    <button class="rb" id="newChat" ${CHAT.length ? '' : 'disabled data-tip="대화가 없습니다."'} onclick="CHAT=[];chatDraw()">${ic('refresh', 16)}새 대화</button><span class="sp"></span>
    <button class="btn out sm" onclick="location.hash='trace'">${ic('trace', 16)}${b ? '질문 기록' : '내 질문 기록'}</button></div>
  <div class="chatw"><div class="chatm" id="chatM">${CHAT.length ? CHAT.map(chatMsg).join('') : chatHello(ex, ready)}</div>
    <div class="askbox"><textarea class="inp" id="aIn" rows="1" ${ready ? '' : 'disabled'} aria-label="질문 입력" placeholder="예) 질병군별 청구 건수는? / CL-004 지급액은?" onkeydown="if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();askGo()}"></textarea><button class="btn pri lg" id="aGo" ${ready ? '' : 'disabled'} onclick="askGo()">${ic('send', 20)}보내기</button></div>
    <p class="muted" style="margin:8px 0 0;text-align:center">●●●는 권한에 따라 가린 값입니다. AI가 쓴 문장은 틀릴 수 있으니 근거와 실행 단계를 확인해 주세요.</p></div>`;
};
function chatHello(ex, ready) {
  return `<div class="hello"><span class="hi">${ic('robot', 24)}</span><h2>무엇이 궁금하신가요?</h2><p>건수·합계·순위(예: 질병군별 청구 건수)나 한 건의 값(예: CL-004 지급액)을 물을 수 있습니다.</p>
    ${ready ? '' : `<div class="alert info" style="text-align:left">${ic('info')}<div>아직 질문할 데이터가 준비되지 않았습니다. ${isUser() ? '구축 담당이 데이터를 연결하면 질문할 수 있습니다.' : '온톨로지 설계에서 엔터티 형식을 먼저 만들어 주세요.'}</div></div>`}
    ${ready ? `<div id="agEx"></div>${ex.length ? `<div class="chips" style="margin-top:8px">${ex.map((q) => `<button onclick="askGo(this.textContent)">${ic('star', 12)} ${esc(q)}</button>`).join('')}</div>` : ''}` : ''}</div>`;
}
const chatMsg = (m, i) => `<div class="cq"><span>${esc(m.q)}</span></div>` + (m.r ? chatAns(m.r, i) : m.err ? `<div class="ca"><div class="alert bad">${ic('warn')}<div>답하지 못했습니다. ${esc(m.err)}</div></div></div>` : `<div class="ca"><div class="ans"><span class="typing"><i></i><i></i><i></i></span> <span class="muted">길을 찾고 값을 모으는 중입니다.</span></div></div>`);
function chatAns(r, i) {
  const cls = r.status === 'ok' ? '' : r.status === 'broken' ? 'bad' : 'warn', biz = isUser(), ms = (r.steps || []).reduce((s, x) => s + (x.ms || 0), 0);
  return `<div class="ca"><span class="av">${ic('robot', 14)}</span><div class="cab"><div class="ans ${cls}"><div class="v">${esc(r.answer)}${r.estimated ? ' <span class="b warn" data-tip="확인 전 값이 들어간 계산이 있습니다. 실행 단계에서 확인해 주세요.">예상</span>' : ''}</div><div>${esc(r.detail || '')}</div>
    ${r.table ? `<div style="margin-top:12px">${resView(r.table, { max: 10 })}</div>` : ''}
    ${r.evidence?.length ? `<div style="margin-top:8px;font-weight:700">근거</div><ol>${r.evidence.map((e) => `<li>${esc(e)}</li>`).join('')}</ol>` : ''}
    ${r.missing?.length ? `<p style="margin-top:8px">${biz ? '필요한 데이터가 서로 이어져 있지 않아 답할 수 없습니다. 구축 담당에게 알려 주세요.' : `미연결: ${r.missing.map(([a, b]) => esc(lab(a) + ' → ' + lab(b))).join(', ')} — 온톨로지 설계에서 관계를 추가해 주세요.`}</p>` : ''}</div>
    <details class="xsteps"><summary>실행 단계 ${(r.steps || []).length}개 <span class="muted">· ${(ms / 1000).toFixed(1)}초${r.tpl && !biz ? ` · 예제 쿼리 "${esc(r.tpl)}"` : ''}</span></summary><ol>${(r.steps || []).map((s) => `<li class="${s.broken ? 'broken' : ''}"><b>${esc(s.title)}</b> <span class="muted">${s.ms ?? ''}ms</span><div class="muted">${esc(s.detail || '')}</div>${s.sql && !biz ? `<div class="qcode">${esc(s.sql)}</div>` : ''}${s.calc ? s.calc.map((c) => `<div class="muted" style="margin-top:6px">${esc(c.obj_label)} ${esc(c.key)}</div>${calcView(c.items, { compact: true })}`).join('') : ''}</li>`).join('')}</ol></details>
    <div class="row cact"><button class="btn xs out" onclick="openAsk(${r.id})">${biz ? '근거 보기' : '근거·탄 경로 보기'}</button>${!biz ? `<button class="btn xs out" ${lock()} onclick="goldFromAsk(${i})">골든 질문으로 저장</button>${r.table ? `<button class="btn xs out" ${lock()} onclick="saveAsMetric(${r.id})">메트릭으로 저장</button>` : ''}` : ''}</div></div></div>`;
}
function chatDraw() {
  // 같은 대화를 페이지(#chatM)와 오른쪽 아래 말풍선 창(#fabM) 둘 다에 그림
  const fm = $('#fabM'); if (fm) { fm.innerHTML = CHAT.length ? CHAT.map(chatMsg).join('') : fabHello(); fm.scrollTop = 1e6; }
  const el = $('#chatM'); if (!el) return;
  el.innerHTML = CHAT.length ? CHAT.map(chatMsg).join('') : '';
  if (!CHAT.length) return render();
  el.scrollTop = 1e6;
  const n = $('#newChat'); if (n) { n.disabled = false; delete n.dataset.tip; }
}
async function askGo(q) {
  const onPage = cur() === 'ask', inp = onPage ? $('#aIn') : $('#fabIn');
  q = (q ?? inp?.value ?? '').trim(); if (!q) { inp?.focus(); return; }
  if (!onPage) fabOpen(true);
  if (inp) inp.value = '';
  const m = { q }; CHAT.push(m); chatDraw();
  ['#aGo', '#fabGo'].forEach((x) => $(x) && ($(x).disabled = true));
  try { m.r = await post('/ask', { q }); } catch (e) { m.err = e.message; }
  ['#aGo', '#fabGo'].forEach((x) => $(x) && ($(x).disabled = false));
  chatDraw(); refreshQuiet();
}
// 데이터 에이전트 말풍선 — 오른쪽 아래 버튼(메신저처럼) → 작은 대화 창. 페이지와 같은 대화를 씀
let FAB = false;
const fabHello = () => (setTimeout(() => agentEx('#fabEx')), `<div class="hello sm"><span class="hi">${ic('robot', 20)}</span><b>무엇이 궁금하신가요?</b><p class="muted">건수·합계·순위나 한 건의 값을 물어보세요. 답마다 근거와 실행 단계가 붙습니다.</p><div id="fabEx" style="width:100%"></div></div>`);
function fabOpen(on = !FAB) {
  FAB = on; const b = $('#fabBox');
  b.classList.toggle('on', FAB); $('#fabBtn').innerHTML = ic(FAB ? 'x' : 'chat', 24); $('#fabBtn').setAttribute('aria-label', FAB ? '데이터 에이전트 닫기' : '데이터 에이전트 열기');
  if (!FAB) return;
  const bld = !isUser();
  b.innerHTML = `<div class="fh"><span class="av">${ic('robot', 14)}</span><b>데이터 에이전트</b><span class="sp"></span>${bld ? `<button class="ibtn sm" data-tip="에이전트 지침" aria-label="에이전트 지침" onclick="instrPanel()">${ic('pencil', 16)}</button><button class="ibtn sm" data-tip="예제 쿼리" aria-label="예제 쿼리" onclick="exPanel()">${ic('star', 16)}</button>` : ''}<button class="ibtn sm" data-tip="새 대화" aria-label="새 대화" onclick="CHAT=[];chatDraw()">${ic('refresh', 16)}</button><button class="ibtn sm" data-tip="크게 보기" aria-label="크게 보기" onclick="fabOpen(false);location.hash='ask'">${ic('side', 16)}</button></div>
    <div class="fm" id="fabM"></div>
    <div class="fi"><textarea class="inp" id="fabIn" rows="1" ${ST.objects ? '' : 'disabled'} aria-label="질문 입력" placeholder="${ST.objects ? '예) 질병군별 청구 건수는?' : '먼저 온톨로지를 만들어 주세요.'}" onkeydown="if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();askGo()}"></textarea><button class="snd" id="fabGo" aria-label="보내기" ${ST.objects ? '' : 'disabled'} onclick="askGo()">${ic('send', 16)}</button></div>`;
  chatDraw(); setTimeout(() => $('#fabIn')?.focus(), 50);
}
function goldFromAsk(i) {
  const m = CHAT[i];
  formModal('골든 질문으로 저장', `<div class="fld"><label>질문<i></i></label><textarea class="inp" id="gQ" rows="2">${esc(m.q)}</textarea></div>
    <div class="fld" style="margin-top:16px"><label>정답<i></i></label><input class="inp" id="gW" value="${esc(m.r?.status === 'ok' ? m.r.answer : '')}"><span class="help">GenTology 답을 넣어 두었습니다. 맞는 정답인지 확인해 주세요.</span></div>`, '저장', async () => {
    await post('/golden', { q: $('#gQ').value, want: $('#gW').value }); toast('골든 질문이 저장되었습니다.'); refreshQuiet();
  });
}
// 에이전트 지침 — 오른쪽 패널(Fabric 데이터 에이전트 지침처럼). 질문 계획과 답 쓰기에 늘 함께 들어감
async function instrPanel() {
  const a = await get('/agent'); NODE.dirty = false;
  panel(`<div class="hd"><h2>에이전트 지침</h2></div><div class="bd stack">
    <div class="alert info">${ic('info')}<div>모든 질문에 늘 적용할 기준입니다. AI가 질문 계획을 세울 때와 답을 쓸 때 함께 들어갑니다. 계산은 그대로 프로그램(SQL)이 합니다.</div></div>
    <div class="fld"><label>지침</label><textarea class="inp" id="iTx" rows="12" maxlength="5000" ${lock()} placeholder="예)\n- 보험금 지급 질문은 지급이력이 아니라 해당 청구 건에서 찾는다.\n- 금액은 원 단위로, 날짜는 YYYY-MM-DD로 쓴다.\n- '이번 달'은 접수일 기준이다.">${esc(a.instr)}</textarea><span class="help" id="iCnt">${a.instr.length.toLocaleString()} / 5,000자</span></div>
    ${can('build') ? exBox('예시 지침 · 누르면 지침 끝에 붙습니다', instrEx().map((t) => `<button type="button" data-t="${esc(t)}" onclick="const x=$('#iTx');x.value=(x.value.trim()?x.value.trim()+'\\n':'')+'- '+this.dataset.t;x.dispatchEvent(new Event('input'))">${esc(t)}</button>`).join('')) : ''}
    ${ST.intent ? `<div class="guide"><b>참고 · 구축 의도</b>${esc(ST.intent)}</div>` : ''}</div>
  <div class="ft"><button class="btn out" onclick="closePanel()">취소</button><button class="btn pri" ${lock()} onclick="run(this,'',async()=>{await post('/agent/instr',{text:$('#iTx').value});NODE.dirty=false;closePanel(true);toast('에이전트 지침이 저장되었습니다. 다음 질문부터 적용됩니다.');refreshQuiet()})">저장</button></div>`, 'md');
  $('#iTx').oninput = () => { NODE.dirty = true; $('#iCnt').textContent = `${$('#iTx').value.length.toLocaleString()} / 5,000자`; };
}
// 예제 쿼리 — 오른쪽 패널. 질문하면 예제 쿼리(어떤 길로 찾는지)이 저장되고, 같은 틀 질문은 같은 길로 찾음
async function exPanel() {
  const a = await get('/agent');
  panel(`<div class="hd"><h2>예제 쿼리</h2><button class="ibtn" aria-label="닫기" onclick="closePanel()">${ic('x', 20)}</button></div><div class="bd stack">
    <div class="alert info">${ic('info')}<div>질문하면 <b>예제 쿼리</b>(무엇을 묻는지 + 어떤 길로 찾는지)이 저장됩니다. 값만 다른 같은 모양의 질문은 이 길을 그대로 씁니다. 틀린 틀은 지우면 다음 질문 때 다시 만듭니다.</div></div>
    <div class="fld"><label>예제 쿼리 추가</label><div class="row" style="flex-wrap:nowrap"><input class="inp" id="exQ" placeholder="예) 피보험자별 청구 건수 상위 3명은?" onkeydown="if(event.key==='Enter'&&!event.isComposing)$('#exGo').click()"><button class="btn out" id="exGo" ${lock()} onclick="const q=$('#exQ').value.trim();if(!q){toast('질문을 입력해 주세요.',true);return}closePanel(true);askGo(q)">질문해서 틀 만들기</button></div><span class="help">데이터 에이전트 화면에서 답과 실행 단계를 보고 맞는지 확인합니다.</span></div>
    <div class="sec-t sm">예제 쿼리 ${a.templates.length}개</div>
    ${a.templates.length ? a.templates.map((t) => `<div class="exi"><div class="row"><b>${esc(t.name)}</b><span class="b">${t.mode === 'set' ? '여러 건' : '한 건'}</span><span class="sp"></span><span class="muted">질문 ${t.uses}건</span></div>
      <div class="muted mono" style="margin:4px 0">${esc(t.how)}</div>${t.example ? `<div class="row"><span class="muted">예: ${esc(t.example)}</span><span class="sp"></span><button class="btn xs out" onclick="closePanel(true);askGo(${esc(JSON.stringify(t.example))})">다시 묻기</button><button class="btn xs dan" ${lock()} onclick="tplDel(${esc(JSON.stringify(t.name))})">삭제</button></div>` : `<div class="row"><span class="sp"></span><button class="btn xs dan" ${lock()} onclick="tplDel(${esc(JSON.stringify(t.name))})">삭제</button></div>`}</div>`).join('')
    : empty('아직 예제 쿼리가 없습니다.', '질문하면 틀이 저장됩니다.', '', true, 'star')}</div>`, 'lg');
}
async function tplDel(name) {
  if (!(await confirmBox({ title: '예제 쿼리를 삭제하시겠습니까?', body: `"${esc(name)}" 틀을 지웁니다. 같은 모양의 다음 질문 때 AI가 길을 새로 정합니다.`, ok: '삭제', danger: true }))) return;
  await del('/agent/templates/' + encodeURIComponent(name)); toast('예제 쿼리가 삭제되었습니다.'); exPanel();
}

// 골든 질문 — 목록 → 상세(정답 · GenTology 답 · 판정 · 실행 단계). 만들기는 창
P.golden = async () => {
  GOLD = await get('/golden');
  const id = +hq().get('id');
  if (id) return goldDetail(id);
  const ran = GOLD.filter((g) => g.run_at), pass = ran.filter((g) => g.ok === '맞음').length;
  const list = GOLD.filter((g) => !gOk || (gOk === '실행 전' ? !g.ok : g.ok === gOk));
  return `<div class="ph"><div class="t"><h1>골든 질문</h1><p>온톨로지가 꼭 답해야 하는 질문과 정답입니다. 바꿀 때마다 실행해서 맞는지 확인합니다.</p></div>
    <button class="btn out" ${GOLD.length ? lock() : 'disabled data-tip="골든 질문을 만든 후 실행할 수 있습니다."'} onclick="goldRun(this)">${ic('play')}전체 실행</button><button class="btn pri" ${lock()} onclick="goldModal()">${ic('plus')}골든 질문 만들기</button></div>
  <div class="g4" style="margin-bottom:24px"><div class="metric"><span class="mi">${ic('star', 24)}</span><div><div class="k">통과</div><div class="v">${ran.length ? pass : '-'}${ran.length ? `<small>개</small><span class="sub2">전체 ${GOLD.length}개</span>` : ''}</div></div></div></div>
  <div class="lc"><select class="inp" onchange="gOk=this.value;render()"><option value="">결과 | 전체</option>${['맞음', '일부', '틀림', '실행 전'].map((x) => `<option value="${x}" ${gOk === x ? 'selected' : ''}>결과 | ${x === '맞음' ? '통과' : x === '틀림' ? '실패' : x}</option>`).join('')}</select>${gOk ? resetBtn("gOk=''") : ''}<span class="cnt">총 ${list.length}개${ran.length ? ` · 최근 실행 ${fmtT(Math.max(...ran.map((g) => g.run_at)))}` : ''}</span></div>
  <div class="card flat">${list.length ? `<table class="t"><thead><tr><th>질문</th><th>정답</th><th>GenTology 답</th><th>결과</th><th>사람 판정</th></tr></thead><tbody>
    ${list.map((g) => `<tr class="click" onclick="location.hash='golden?id=${g.id}'"><td>${esc(g.q)}</td><td class="r">${esc(g.want)}</td><td class="r">${esc(g.got || '-')}</td><td>${okTag(g.ok)}</td>
      <td>${g.vote ? `<span class="b ${g.vote === '맞음' ? 'ok' : 'bad'}">${g.vote}</span>` : g.ok ? '<span class="muted">판정 전</span>' : '-'}</td></tr>`).join('')}</tbody></table>`
    : GOLD.length ? empty('조건에 맞는 골든 질문이 없습니다.', '필터를 조정해 주세요.', resetBtn("gOk=''"), true, 'search') : empty('아직 골든 질문이 없습니다.', '데이터 에이전트에서 받은 답을 골든 질문으로 저장하거나 직접 만들어 주세요.', `<button class="btn pri" ${lock()} onclick="goldModal()">골든 질문 만들기</button>${can('build') ? await exChips('gold', 'exGoldNew') : ''}`, false, 'star')}</div>`;
};
async function goldDetail(id) {
  const g = GOLD.find((x) => x.id === id);
  if (!g) { history.replaceState(null, '', '#golden'); toast('골든 질문을 찾을 수 없습니다. 삭제되었을 수 있습니다.', true); return P.golden(); }
  CRUMB = [['골든 질문', '#golden'], [g.q]];
  const a = g.ask_id ? await get('/asks/' + g.ask_id).catch(() => null) : null;
  return `<div class="ph"><div class="t"><h1>${esc(g.q)}</h1><p>${g.run_at ? `최근 실행 ${fmtT(g.run_at)}` : '아직 실행하지 않았습니다.'}</p></div>
    <button class="btn out" onclick="askGo(${esc(JSON.stringify(g.q))})">${ic('chat', 16)}데이터 에이전트에서 묻기</button><button class="btn out" ${lock()} onclick="goldRun(this)">${ic('play', 16)}전체 실행</button>
    <div class="morew"><button class="ibtn" aria-label="더보기" aria-haspopup="menu" ${lock()} onclick="phMore(event)">${ic('dots', 20)}</button><div class="menu" id="moreMenu" role="menu"><button role="menuitem" class="dan" onclick="closeMenu();goldDel(${g.id})">${ic('x')}<span>골든 질문 삭제</span></button></div></div></div>
  <div class="g2">
    <div class="card"><h3>정답</h3><p class="bigt">${esc(g.want)}</p></div>
    <div class="card"><h3>GenTology 답 ${okTag(g.ok)}</h3><p class="bigt">${esc(g.got || '-')}</p>${a?.detail ? `<p class="muted" style="margin:8px 0 0">${esc(a.detail)}</p>` : ''}</div>
    <div class="card"><h3>사람 판정 <small>AI 채점을 사람이 확인합니다.</small></h3>${g.ok ? `<div class="row">${['맞음', '틀림'].map((v) => `<button class="btn ${g.vote === v ? (v === '맞음' ? 'pri' : 'danger') : 'out'} sm" onclick="goldVote(${g.id},'${v}')">${v}</button>`).join('')}${g.vote ? `<span class="muted">판정: ${g.vote}</span>` : '<span class="muted">아직 판정하지 않았습니다.</span>'}</div>` : '<p class="muted" style="margin:0">실행한 후 판정할 수 있습니다.</p>'}</div>
    <div class="card"><h3>실행 단계 ${a ? `<span class="sp"></span><button class="btn out sm" onclick="openAsk(${g.ask_id})">탄 경로 보기</button>` : ''}</h3>${a ? `<ol class="stl">${a.steps.map((s) => `<li class="${s.broken ? 'broken' : ''}"><b>${esc(s.title)}</b> <span class="muted">${s.ms ?? ''}ms</span><div class="muted">${esc(s.detail || '')}</div></li>`).join('')}</ol>` : '<p class="muted" style="margin:0">실행하면 어떤 길로 찾았는지 보입니다.</p>'}</div>
  </div>`;
}
async function goldModal() {
  const ex = await exChips('gold', 'exGold');
  formModal('골든 질문 만들기', `${ex}<div class="fld" ${ex ? 'style="margin-top:16px"' : ''}><label>질문<i></i></label><textarea class="inp" id="gQ" rows="2" placeholder="예) 청구 CL-004는 얼마를 지급해야 하나?"></textarea></div>
    <div class="fld" style="margin-top:16px"><label>정답<i></i></label><input class="inp" id="gW" placeholder="예) 600만 원"><span class="help">예시의 정답은 원본 테이블에서 바로 읽은 값입니다. 맞는지 확인해 주세요.</span></div>`, '만들기', async () => {
    await post('/golden', { q: $('#gQ').value, want: $('#gW').value }); toast('골든 질문이 만들어졌습니다.'); refresh();
  });
}

function ansCard(r, big = false) {
  const cls = r.status === 'ok' ? '' : r.status === 'broken' ? 'bad' : 'warn';
  return `<div class="ans ${cls} ${big ? '' : 'sm'}" ${big ? 'style="margin-bottom:24px"' : ''}><div class="v">${esc(r.answer)}</div><div>${esc(r.detail || '')}</div>
    ${r.table ? `<div style="margin-top:12px">${resView(r.table, { max: big ? 20 : 5 })}</div>` : ''}
    ${r.evidence?.length ? `<div style="margin-top:8px;font-weight:700">근거</div><ol>${r.evidence.map((e) => `<li>${esc(e)}</li>`).join('')}</ol>` : ''}${r.missing?.length ? `<p style="margin-top:8px">${isUser() ? '필요한 데이터가 서로 이어져 있지 않아 답할 수 없습니다. 구축 담당에게 알려 주세요.' : `미연결: ${r.missing.map(([a, b]) => esc(lab(a) + ' → ' + lab(b))).join(', ')}`}</p>` : ''}
    <p style="margin-top:8px"><button class="link" onclick="openAsk(${r.id ?? r.ask_id})">${isUser() ? '근거 보기' : '근거·탄 경로 보기'}</button></p></div>`;
}

// ── 계산 과정 펼쳐 보기 — 계산 속성마다 식 · 들어간 값(원본 테이블 · 줄 · 상태) · 중간 결과 · 결과. 확인 전 값이 들어가면 "예상" ──
const ST_CLS = { '확정': '', '계산 속성': 'info', '빈 값': 'warn', '사람 확인 전': 'warn' };
function calcView(items, { compact = false } = {}) {
  return items.map((it) => `<details class="calcx" ${compact ? '' : 'open'}><summary><b>${esc(it.label)}</b> = <span class="mono">${esc(it.result ?? '빈 값')}</span>${it.estimated ? ` <span class="b warn" data-tip="${esc((it.why || []).join(' · '))}">예상</span>` : ' <span class="b ok">확정</span>'}<span class="muted"> · ${esc(it.kind)}</span></summary>
    ${it.text ? `<p class="muted" style="margin:6px 0">정의: ${esc(it.text)}</p>` : ''}${it.formula ? `<div class="qcode">${esc(it.formula)}</div>` : ''}
    ${it.inputs?.length ? `<table class="t" style="margin-top:8px"><thead><tr><th>들어간 값</th><th>값</th><th>출처(원본 테이블 · 줄)</th><th>상태</th></tr></thead><tbody>${it.inputs.slice(0, compact ? 6 : 20).map((i) => `<tr><td>${esc(i.obj_label)} · ${esc(i.label)}</td><td class="mono">${esc(i.value ?? '')}</td><td class="r mono">${esc(i.src)}</td><td><span class="b ${ST_CLS[i.state] || ''}">${esc(i.state)}</span></td></tr>`).join('')}</tbody></table>${it.inputs.length > (compact ? 6 : 20) ? `<p class="muted">외 ${it.inputs.length - (compact ? 6 : 20)}줄</p>` : ''}` : ''}
    ${it.steps?.length ? `<ol class="stl">${it.steps.map((s) => `<li>${esc(s)}</li>`).join('')}</ol>` : ''}${it.error ? `<p class="err-msg">${esc(it.error)}</p>` : ''}</details>`).join('');
}

// 인스턴스 한 건 — 오른쪽 패널(값 · 계산 과정), [가정 바꿔 보기] · [그래프 탐색에서 보기]
async function instPanel(name, key) {
  const o = objOf(name) || (ONTO = await get('/onto'), objOf(name));
  const [r, ex] = await Promise.all([get(`/objects/${encodeURIComponent(name)}/rows?q=${encodeURIComponent(key)}&n=50`), get(`/objects/${encodeURIComponent(name)}/explain?key=${encodeURIComponent(key)}`).catch(() => [])]);
  const row = r.rows.find((x) => String(x[r.key]) === String(key)) || r.rows[0] || {};
  const base = o.props.filter((p) => !p.calc && !p.hidden);
  panel(`<div class="hd"><h2>${esc(o.label)} ${esc(key)}</h2><button class="ibtn" aria-label="닫기" onclick="closePanel()">${ic('x', 20)}</button></div><div class="bd stack">
    <dl class="dl">${base.map((p) => `<dt>${esc(p.label)}</dt><dd class="${p.type === '글자' ? '' : 'mono'}">${esc(row[p.col] ?? '')}</dd>`).join('')}</dl>
    ${ex.length ? `<div><div class="sec-t sm">계산 속성 ${ex.length}개 <small>식 · 들어간 값 · 출처를 펼쳐 봅니다. 확인 전 값이 들어가면 "예상"입니다.</small></div>${calcView(ex)}</div>` : ''}</div>
  <div class="ft">${row.doc_id ? `<button class="btn out" onclick="closePanel(true);openDoc('${esc(row.doc_id)}')">${ic('doc', 16)}문서 보기</button>` : ''}<button class="btn out" onclick="closePanel(true);EXP.obj='${esc(name)}';EXP.val='${esc(key)}';location.hash='explore';doExplore(true)">그래프 탐색에서 보기</button>${isUser() ? '' : `<button class="btn pri" onclick="whatifPanel('${esc(name)}','${esc(key)}')">${ic('refresh', 16)}가정 바꿔 보기</button>`}</div>`, 'xl');
}

// ── 가정 바꿔 보기(What-if) — 값을 임시로 바꾸면 계산 속성 · 규칙 판정 · 골든 질문 답이 어떻게 바뀌는지 "지금 / 바꾸면". 원본은 그대로 ──
let WI = { obj: '', key: '', res: null, changes: [] };
async function whatifPanel(name, key, pre = null) {
  const o = objOf(name) || (ONTO = await get('/onto'), objOf(name));
  const r = await get(`/objects/${encodeURIComponent(name)}/rows?q=${encodeURIComponent(key)}&n=50`);
  const row = r.rows.find((x) => String(x[r.key]) === String(key)) || {};
  const base = o.props.filter((p) => !p.calc && !p.hidden && p.col !== o.key);
  WI = { obj: name, key, res: null, changes: [], row, base };
  const crow = (c = {}) => `<div class="row wrow" style="flex-wrap:nowrap;margin-bottom:8px"><select class="inp wc" style="flex:1" aria-label="바꿀 속성" onchange="this.parentElement.querySelector('.wnow').value=WI.row[this.value]??''">${base.map((p) => `<option value="${esc(p.col)}" ${c.col === p.col ? 'selected' : ''}>${esc(p.label)}</option>`).join('')}</select><input class="inp wnow" style="flex:1" aria-label="지금 값" readonly value="${esc(row[c.col || base[0]?.col] ?? '')}"><span>→</span><input class="inp wv" style="flex:1" aria-label="바꿀 값" placeholder="바꿀 값" value="${esc(c.value ?? '')}"><button class="ibtn" aria-label="빼기" onclick="this.parentElement.remove()">${ic('x', 16)}</button></div>`;
  panel(`<div class="hd"><h2>가정 바꿔 보기 · ${esc(o.label)} ${esc(key)}</h2></div><div class="bd stack">
    <div class="alert info">${ic('info')}<div>값을 임시로 바꿔 계산 속성 · 규칙 판정 · 골든 질문 답이 어떻게 달라지는지 봅니다. <b>원본 데이터는 바뀌지 않습니다.</b></div></div>
    <div id="wpEx"></div><div class="fld"><label>바꿀 값<i></i></label><div id="wRows">${(pre || [{}]).map(crow).join('')}</div><div><button type="button" class="btn ter sm" id="wAdd">${ic('plus', 16)}바꿀 값 추가</button></div></div>
    <label class="chk"><input type="checkbox" id="wGold" ${ST.golden && ST.golden <= 5 ? 'checked' : ''} ${ST.golden ? '' : 'disabled'}>골든 질문도 다시 풀기 <span class="muted">(AI 사용 · ${ST.golden || 0}개 · 질문마다 몇 초)</span></label>
    <div><button class="btn out" id="wRun">${ic('play', 16)}결과 보기</button></div><div id="wOut"></div></div>
  <div class="ft"><button class="btn out" onclick="closePanel(true)">닫기</button><button class="btn pri" id="wSave" disabled data-tip="결과를 본 뒤 저장할 수 있습니다." ${lock()} onclick="whatifSave(this)">이름 붙여 저장</button></div>`, 'xl');
  $('#wAdd').onclick = () => $('#wRows').insertAdjacentHTML('beforeend', crow());
  if (!pre) whatifEx('#wpEx', name);
  $('#wRun').onclick = (e) => run(e.currentTarget, '계산 중', async () => {
    const changes = [...document.querySelectorAll('#wRows .wrow')].map((x) => ({ obj: name, key, col: x.querySelector('.wc').value, value: x.querySelector('.wv').value })).filter((c) => c.value !== '');
    if (!changes.length) { toast('바꿀 값을 입력해 주세요.', true); return; }
    WI.changes = changes; WI.res = await post('/whatif/run', { changes, golden: $('#wGold').checked });
    $('#wOut').innerHTML = whatifView(WI.res);
    if (can('build')) { $('#wSave').disabled = false; delete $('#wSave').dataset.tip; }
  });
}
function whatifView(r, all = false) {
  const ch = r.calcs.filter((c) => all || c.changed), rc = r.rules.filter((x) => all || x.changed || x.error);
  const nch = r.calcs.filter((c) => c.changed).length, nrc = r.rules.filter((x) => x.changed).length;
  const gch = (r.golden || []).filter((g) => g.ok_before !== g.ok_after || g.before !== g.after).length;
  const dv = (a, b) => `<td class="mono">${esc(a ?? '빈 값')}</td><td class="mono ${String(a) !== String(b) ? 'chg' : ''}">${esc(b ?? '빈 값')}</td>`;
  return `<div class="g3w"><div class="metric sm"><div><div class="k">바뀐 계산 속성</div><div class="v">${nch}<small>개</small></div></div></div><div class="metric sm"><div><div class="k">바뀐 규칙 판정</div><div class="v">${nrc}<small>개</small></div></div></div><div class="metric sm"><div><div class="k">바뀐 골든 질문</div><div class="v">${r.with_golden ? gch : '-'}${r.with_golden ? '<small>개</small>' : ''}</div></div></div></div>
    <div class="sec-t sm">바꾼 값</div><table class="t"><thead><tr><th>대상</th><th>속성</th><th>지금</th><th>바꾸면</th></tr></thead><tbody>${r.changes.map((c) => `<tr><td>${esc(c.obj_label)} ${esc(c.key)}</td><td>${esc(c.label)}</td>${dv(c.before, c.value)}</tr>`).join('')}</tbody></table>
    <div class="sec-t sm" style="margin-top:16px">계산 속성 <small>${all ? '모두' : '바뀐 것만'}</small><span class="sp"></span>${r.calcs.length ? `<button class="link" onclick="this.closest('#wOut, .bd').querySelector('.wiv').outerHTML=whatifView(${all ? 'WI.res' : 'WI.res'}, ${!all}).replace(/^/, '<div class=&quot;wiv&quot;>')+'</div>'">${all ? '바뀐 것만 보기' : '바뀌지 않은 것도 보기'}</button>` : ''}</div>
    ${ch.length ? `<table class="t"><thead><tr><th>대상</th><th>계산 속성</th><th>지금</th><th>바꾸면</th></tr></thead><tbody>${ch.map((c) => `<tr><td>${esc(c.obj_label)} ${esc(c.key)}</td><td>${esc(c.label)}</td>${dv(c.before, c.after)}</tr>`).join('')}</tbody></table>` : `<p class="muted">${r.calcs.length ? '바뀐 계산 속성이 없습니다.' : '이 값을 쓰는 계산 속성이 없습니다.'}</p>`}
    <div class="sec-t sm" style="margin-top:16px">규칙 판정 <small>실행 중인 규칙 · 걸린 건수</small></div>
    ${r.rules.length ? `<table class="t"><thead><tr><th>규칙</th><th>지금</th><th>바꾸면</th><th>달라진 건</th></tr></thead><tbody>${(all ? r.rules : rc.length ? rc : r.rules).map((x) => x.error ? `<tr><td>${esc(x.name)}</td><td colspan="3" class="err-msg">${esc(x.error)}</td></tr>` : `<tr><td>${esc(x.name)}</td><td class="num">${x.before}건</td><td class="num ${x.changed ? 'chg' : ''}">${x.after}건</td><td class="r">${x.added.length ? `새로 걸림: ${esc(x.added.join(', '))}` : ''}${x.removed.length ? ` 빠짐: ${esc(x.removed.join(', '))}` : ''}${!x.changed ? '<span class="muted">같음</span>' : ''}</td></tr>`).join('')}</tbody></table>` : '<p class="muted">실행 중인 규칙이 없습니다.</p>'}
    ${r.with_golden ? `<div class="sec-t sm" style="margin-top:16px">골든 질문</div><table class="t"><thead><tr><th>질문</th><th>지금 답</th><th>바꾸면 답</th></tr></thead><tbody>${r.golden.map((g) => `<tr><td>${esc(g.q)}<div class="muted">정답: ${esc(g.want)}</div></td><td class="r">${okTag(g.ok_before)} ${esc(g.before)}</td><td class="r ${g.before !== g.after ? 'chg' : ''}">${okTag(g.ok_after)} ${esc(g.after)}</td></tr>`).join('')}</tbody></table>` : ''}`;
}
function whatifSave(btn) {
  formModal('가정 저장', `<div class="fld"><label>가정 이름<i></i></label><input class="inp" id="wName" placeholder="예) CL-004 청구일을 가입 직후로"></div>`, '저장', async () => {
    await post('/whatif', { name: $('#wName').value.trim(), changes: WI.changes, result: WI.res }); toast('가정이 저장되었습니다. 온톨로지 설계 › 가정에서 다시 볼 수 있습니다.'); refreshQuiet();
  });
}
// 저장한 가정 목록 — 온톨로지 설계 탐색기 개요에서 들어감
let WIS = [];
P.whatif = async () => {
  WIS = await get('/whatif'); setTimeout(() => whatifEx('#wiEx'));
  return `<div class="ph"><div class="t"><h1>가정 바꿔 보기</h1><p>값을 임시로 바꿨을 때 계산 속성 · 규칙 판정 · 골든 질문 답이 어떻게 달라지는지 저장해 둔 것입니다. 원본 데이터는 바뀌지 않습니다.</p></div><button class="btn pri" ${ST.objects ? '' : 'disabled'} onclick="whatifNew()">${ic('plus')}새 가정</button></div>
  <div id="wiEx" style="margin-bottom:16px"></div>
  <div class="card flat">${WIS.length ? `<table class="t"><thead><tr><th>이름</th><th>바꾼 값</th><th>달라진 것</th><th>만든 사람</th><th>일시</th></tr></thead><tbody>${WIS.map((s) => { const r = s.result || {}; return `<tr class="click" onclick="whatifOpen(${s.id})"><td>${esc(s.name)}</td><td class="r">${esc((r.changes || []).map((c) => `${c.obj_label} ${c.key} ${c.label}: ${c.before ?? ''} → ${c.value}`).join(' · '))}</td><td class="r">계산 ${(r.calcs || []).filter((c) => c.changed).length} · 규칙 ${(r.rules || []).filter((x) => x.changed).length}${r.with_golden ? ` · 골든 ${(r.golden || []).filter((g) => g.before !== g.after).length}` : ''}</td><td class="r">${esc(s.by)}</td><td class="r">${fmtT(s.at)}</td></tr>`; }).join('')}</tbody></table>`
    : empty('아직 저장한 가정이 없습니다.', '엔터티 형식의 인스턴스를 열고 [가정 바꿔 보기]를 누르거나, [새 가정]으로 시작합니다.', `<button class="btn out sm" ${ST.objects ? '' : 'disabled'} onclick="whatifNew()">새 가정</button>`, false, 'refresh')}</div>`;
};
function whatifNew() {
  const objs = (ONTO?.objects || []).filter((o) => !o.name.startsWith('same_') && !o.name.startsWith('result_'));
  formModal('새 가정', `<div class="stack"><div class="fld"><label>엔터티 형식<i></i></label><select class="inp" id="wnO">${objs.map((o) => `<option value="${esc(o.name)}">${esc(o.label)}</option>`).join('')}</select></div>
    <div class="fld"><label>대상(키 값)<i></i></label><input class="inp" id="wnK" placeholder="예) CL-004"><span class="help">엔터티 형식 페이지 · 인스턴스 탭에서 키 값을 볼 수 있습니다.</span></div></div>`, '다음', async () => {
    const o = $('#wnO').value, k = $('#wnK').value.trim(); if (!k) throw new Error('대상 키 값을 입력해 주세요.');
    const r = await get(`/objects/${encodeURIComponent(o)}/rows?q=${encodeURIComponent(k)}&n=50`);
    if (!r.rows.some((x) => String(x[r.key]) === k)) throw new Error(`${k}을(를) 찾을 수 없습니다.`);
    setTimeout(() => whatifPanel(o, k), 50);
  });
  if (!objs.length) get('/onto').then((o) => { ONTO = o; });
}
function whatifOpen(id) {
  const s = WIS.find((x) => x.id === id); WI = { ...WI, res: s.result, changes: s.changes };
  const c0 = s.changes[0] || {};
  panel(`<div class="hd"><h2>${esc(s.name)}</h2><button class="ibtn" aria-label="닫기" onclick="closePanel()">${ic('x', 20)}</button></div><div class="bd stack"><p class="muted" style="margin:0">${esc(s.by)} · ${fmtT(s.at)}에 계산한 결과입니다.</p><div class="wiv">${whatifView(s.result)}</div></div>
    <div class="ft"><button class="btn dan" ${lock()} onclick="whatifDel(${s.id})">삭제</button><span class="sp"></span><button class="btn pri" onclick="whatifPanel('${esc(c0.obj)}','${esc(c0.key)}', ${esc(JSON.stringify(s.changes.map((c) => ({ col: c.col, value: c.value }))))})">지금 데이터로 다시 계산</button></div>`, 'xl');
}
async function whatifDel(id) {
  if (!(await confirmBox({ title: '가정을 삭제하시겠습니까?', body: '저장한 결과가 지워집니다. 원본 데이터와는 상관없습니다.', ok: '삭제', danger: true }))) return;
  await del('/whatif/' + id); closePanel(true); toast('가정이 삭제되었습니다.'); refresh();
}


// ── 누르면 바로 해 보는 예시(서버가 지금 데이터로 만듦: /api/examples) — 기존 예시 칩과 같은 모양 ──
let EXM = { v: null, d: null };
// 화면이 다 그려진 뒤에 칩을 넣음(그리기보다 먼저 불려도 자리가 생길 때까지 잠깐 기다림)
async function waitEl(sel) { for (let i = 0; i < 30; i++) { const el = $(sel); if (el) return el; await new Promise((r) => setTimeout(r, 100)); } return null; }
async function exm() { if (EXM.v !== ST.version || !EXM.d) { try { EXM = { v: ST.version, d: await get('/examples') }; } catch { EXM = { v: ST.version, d: {} }; } } return EXM.d; }
const exBox = (title, chips) => (chips ? `<div class="exchips"><span class="muted">${ic('star', 12)} ${title}</span><div class="chips" style="justify-content:flex-start;margin-top:6px">${chips}</div></div>` : '');
// 데이터 에이전트: 질문 유형별 하나씩 — 누르면 바로 물음
async function agentEx(sel) {
  const d = await exm(), el = await waitEl(sel); if (!el || !d.agent?.length) return;
  el.innerHTML = exBox('내 데이터로 만든 예시 질문 · 누르면 바로 묻습니다', d.agent.map((x) => `<button type="button" onclick="askGo(${esc(JSON.stringify(x.q))})"><span class="b">${esc(x.kind)}</span>${esc(x.q)}</button>`).join(''));
}
// 본문 검색: 검색어 + 좁힐 대상 — 누르면 채우고 바로 검색
async function searchEx() {
  const d = await exm(), el = await waitEl('#sEx'); if (!el || !d.search?.length) return;
  el.innerHTML = exBox('본문에 실제로 있는 말로 만든 예시 · 누르면 바로 검색합니다', d.search.map((x, i) => `<button type="button" onclick="searchExGo(${i})">${esc(x.q)}${x.obj ? ` <span class="muted">· ${esc(x.obj_label)} ${esc(x.value)}로 좁혀</span>` : ''}</button>`).join(''));
}
function searchExGo(i) {
  const x = EXM.d.search[i]; $('#sQ').value = x.q; const so = $('#sObj'); so.value = x.obj || ''; so.onchange?.call(so); $('#sVal').value = x.value || ''; docSearch();
}
// 가정 바꿔 보기: 결과가 실제로 달라지는 값 바꾸기 — 누르면 그 값이 채워진 가정 패널이 열림
async function whatifEx(sel, only = '') {
  const d = await exm(), el = await waitEl(sel), list = (d.whatif || []).filter((x) => !only || x.obj === only); if (!el || !list.length) return;
  el.innerHTML = exBox('결과가 실제로 달라지는 예시 · 누르면 바꿀 값이 채워집니다', list.map((x) => `<button type="button" data-tip="${esc(x.effect)}" onclick="whatifPanel('${esc(x.obj)}','${esc(x.key)}',[{col:'${esc(x.col)}',value:'${esc(x.value)}'}])">${esc(x.obj_label)} ${esc(x.key)} ${esc(x.label)}: ${esc(x.before ?? '')} → ${esc(x.value)}</button>`).join(''));
}
// 엔터티 형식 추가: 값 종류가 몇 개뿐인 열로 떼어 내기 — 누르면 이름 · 원본 테이블 · 조건이 채워진 데이터 바인딩 화면
async function objEx(sel) {
  const d = await exm(), el = await waitEl(sel); if (!el || !d.objects?.length) return;
  el.innerHTML = exBox('내 데이터로 만든 예시 · 누르면 원본 테이블과 조건이 채워집니다', d.objects.map((x, i) => `<button type="button" data-tip="${esc(x.base)} 중 ${esc(x.filter[0].col)} = ${esc(x.filter[0].value)}인 ${x.rows}줄" onclick="objExGo(${i})">${esc(x.label)} <span class="muted">· ${esc(x.base)}</span></button>`).join(''));
}
function objExGo(i) { const x = EXM.d.objects[i]; NEWO = { label: x.label, base: x.base, key: x.key, filter: x.filter }; modalClose ? modalClose() : $('#modalBg').classList.remove('on'); location.hash = 'design?new=1'; if (cur() === 'design') render(); }
// 관계 추가: 값이 겹치는데 아직 관계가 없는 열 짝 — 누르면 열까지 채워진 관계 화면
async function relEx(sel) {
  const d = await exm(), el = await waitEl(sel); if (!el || !d.relations?.length) return;
  el.innerHTML = exBox('값이 겹치는데 아직 이어지지 않은 짝 · 누르면 열까지 채워집니다', d.relations.map((x, i) => `<button type="button" data-tip="값 ${x.hit}개 / ${x.of}개 겹침" onclick="relExGo(${i})">${esc(x.a_label)} ${esc(x.a_col_label || x.a_col)} → ${esc(x.b_label)} ${esc(x.b_col_label || x.b_col)}</button>`).join(''));
}
function relExGo(i) { const x = EXM.d.relations[i]; NREL = { from: '#design?rel=new', a: x.a, ac: x.a_col, b: x.b, bc: x.b_col, name: '' }; modalClose ? modalClose() : $('#modalBg').classList.remove('on'); location.hash = 'design?rel=new'; if (cur() === 'design') render(); }
// 계산 속성 추가: 이 엔터티 형식의 관계 · 숫자 · 날짜 속성으로 만든 문장 — 누르면 입력칸에
function calcEx(o) {
  const L = (p) => p.label || p.col, out = [];
  ONTO.relations.filter((r) => r.a_tbl === o.name || r.b_tbl === o.name).slice(0, 3).forEach((r) => {
    const other = objOf(r.a_tbl === o.name ? r.b_tbl : r.a_tbl); if (!other) return;
    out.push(`이 ${o.label}에 이어진 ${other.label} 건수`);
    const num = other.props.find((p) => p.type === '숫자' && !p.calc && p.col !== other.key); if (num) out.push(`이 ${o.label}에 이어진 ${other.label}의 ${L(num)} 합계`);
  });
  const ds = o.props.filter((p) => p.type === '날짜' && !p.calc); if (ds.length >= 2) out.push(`${L(ds[0])}부터 ${L(ds[1])}까지 일수`);
  return [...new Set(out)].slice(0, 4);
}
// 에이전트 지침: 데이터에 맞춘 지침 한 줄 — 누르면 지침 끝에 붙음
function instrEx() {
  const objs = ONTO?.objects || [], out = [];
  const d = objs.flatMap((o) => o.props).find((p) => p.type === '날짜'); if (d) out.push('날짜는 YYYY-MM-DD로 답한다.');
  const m = objs.flatMap((o) => o.props).find((p) => /금액|amount|amt|비용|합계/.test(p.label + p.col)); if (m) out.push(`${m.label || m.col} 같은 금액은 원 단위 숫자와 함께 '600만 원'처럼 읽기 쉽게도 쓴다.`);
  if (ST.rules) out.push('규칙에 걸린 건이면 규칙 이름과 결과를 먼저 말한다.');
  out.push('값이 없으면 추측하지 말고 "확인할 수 없음"이라고 답한다.');
  return out;
}

// AI 초안 창 — 구축 의도(무엇에 답하고 싶은지) + 엔터티 형식으로 쓸 테이블 고르기(Fabric · 팔란티어처럼 원본 테이블을 사람이 정함)
async function draftDialog() {
  const tbls = (await get('/sources')).flatMap((s) => s.tables.map((t) => ({ ...t, src: s.name })));
  const used = new Set((ONTO?.objects || []).map((o) => o.base));
  const pick = (t) => (used.size ? used.has(t.name) : true);
  formModal(ONTO?.objects.length ? 'AI 초안 재생성' : 'AI 초안 생성', `<div class="stack">
    <div class="fld"><label>이 데이터로 무엇에 답하고 싶나요?</label><textarea class="inp" id="dIntent" rows="2" placeholder="예) 청구 서류 값을 계약과 이어 지급액과 지급 보류 사유를 답한다">${esc(ST.intent || '')}</textarea><span class="help">AI 초안과 데이터 에이전트 답에 함께 들어갑니다(구축 의도).</span></div>
    <div class="fld"><label>엔터티 형식으로 쓸 테이블<i></i></label><div class="row" style="justify-content:space-between"><span class="muted" id="dCnt"></span><label class="chk"><input type="checkbox" id="dAll">전체 선택</label></div>
      <div class="card flat" style="max-height:320px;overflow:auto;border:1px solid var(--line)"><table class="t"><thead><tr><th style="width:48px"></th><th>테이블</th><th>원본</th><th class="num">행</th><th>지금</th></tr></thead><tbody>
      ${tbls.map((t) => `<tr><td><label class="chk"><input type="checkbox" class="dT" aria-label="${esc(t.name)} 선택" value="${esc(t.name)}" ${pick(t) ? 'checked' : ''}></label></td><td class="mono">${esc(t.name)}</td><td class="r">${esc(t.src)}</td><td class="num">${t.nrows.toLocaleString()}</td><td>${used.has(t.name) ? '<span class="b info">엔터티 형식</span>' : '<span class="b">엔터티 형식 아님</span>'}</td></tr>`).join('')}</tbody></table></div>
      <span class="help">고르지 않은 테이블은 엔터티 형식에서 빠집니다. 직접 만든 엔터티 형식(조건 엔터티 형식 · 같은 대상 묶기 · 판정 결과)는 그대로 남고, 지금 버전은 버전 기록에 남습니다.</span></div></div>`, 'AI 초안 생성', async () => {
    const tables = [...document.querySelectorAll('.dT:checked')].map((c) => c.value);
    if (!tables.length) throw new Error('엔터티 형식으로 쓸 테이블을 하나 이상 골라 주세요.');
    const it = $('#dIntent').value.trim();
    if (it && it !== (ST.intent || '')) await post('/onto/intent', { text: it });
    toast('AI가 설계하는 중입니다. 테이블이 많으면 1~2분 걸립니다.');
    const r = await post('/onto/draft', { tables });
    toast(`초안이 생성되었습니다. (엔터티 형식 ${r.objects}개 · 관계 ${r.relations}개)`); await refresh();
  }, 'lg');
  const cnt = () => { const n = document.querySelectorAll('.dT:checked').length; $('#dCnt').textContent = `테이블 ${tbls.length}개 중 ${n}개 선택`; };
  const bind = () => { $('#dAll').onchange = (e) => { document.querySelectorAll('.dT').forEach((c) => (c.checked = e.target.checked)); cnt(); }; document.querySelectorAll('.dT').forEach((c) => (c.onchange = cnt)); cnt(); };
  formModal.rebindExtra = bind; bind();
}

// 예시 칩 — 내 엔터티 형식 · 속성 · 실제 값으로 만든 규칙 · 메트릭 · 골든 질문 예시(LLM 없이). 누르면 입력칸만 채우고 저장은 사람이
let EXS = { v: null, d: null };
async function exSeeds() {
  if (EXS.v === ST.version && EXS.d) return EXS.d;
  const o = ONTO?.objects?.length ? ONTO : (ONTO = await get('/onto'));
  const objs = o.objects.filter((x) => !x.name.startsWith('same_') && !x.name.startsWith('result_'));
  const deg = (n) => o.relations.filter((r) => r.a_tbl === n || r.b_tbl === n).length;
  // 예시를 만들 엔터티 형식: 관계가 많고 숫자 · 날짜 속성이 있는 업무 엔터티 형식(코드표보다 거래 · 건 단위 테이블) 위에서 2개
  const score = (x) => deg(x.name) + 3 * x.props.some((p) => p.type === '숫자' && p.col !== x.key) + 2 * x.props.some((p) => p.type === '날짜') + Math.min(x.nrows, 50) / 50;
  const top = [...objs].sort((a, b) => score(b) - score(a)).slice(0, 2);
  const out = { rule: [], metric: [], gold: [] };
  const L = (p) => p.label || p.col, J = (w) => (/[가-힣]$/.test(w) && (w.charCodeAt(w.length - 1) - 0xac00) % 28 ? '이' : '가');
  for (const main of top) {
    const r = await get(`/objects/${encodeURIComponent(main.name)}/rows?n=200`).catch(() => ({ rows: [], total: 0 }));
    const rows = r.rows || [], P_ = main.props.filter((p) => !p.hidden && p.col !== main.key);
    const vals = (p) => rows.map((x) => x[p.col]).filter((v) => v !== null && v !== '' && v !== '●●●');
    const num = P_.find((p) => p.type === '숫자' && vals(p).length);
    const cat = P_.find((p) => p.type === '글자' && p.col !== main.title && !/_id$|코드|번호/.test(p.col + L(p)) && (() => { const s = new Set(vals(p)); return s.size > 1 && s.size <= Math.max(2, rows.length * 0.6) && s.size <= 12; })());
    const ml = main.label;
    if (num) {
      const ns = vals(num).map(Number).filter((n) => !isNaN(n)).sort((a, b) => a - b), med = ns[Math.floor(ns.length / 2)];
      out.rule.push(`${ml}의 ${L(num)}${J(L(num))} ${Number(med).toLocaleString()} 이상이면 확인 필요`);
      out.metric.push(`${ml} ${L(num)} 상위 5개`);
    }
    if (cat) {
      const top2 = Object.entries(vals(cat).reduce((m, x) => ((m[x] = (m[x] || 0) + 1), m), {})).sort((a, b) => b[1] - a[1]);
      out.rule.push(`${ml}의 ${L(cat)}${J(L(cat))} '${top2[0][0]}'이면 우선 검토`);
      out.metric.push(`${L(cat)}별 ${ml} 건수`);
      if (num) out.metric.push(`${L(cat)}별 ${L(num)} 합계`);
      if (r.total && r.total <= rows.length && (top2.length < 2 || top2[0][1] > top2[1][1])) out.gold.push([`${L(cat)}별 ${ml} 건수가 가장 많은 것은?`, `${top2[0][0]} (${top2[0][1]}건)`]);
    }
    const row = rows[0], show = P_.find((p) => row && row[p.col] !== '' && row[p.col] != null && row[p.col] !== '●●●' && !p.sensitive && (p.type === '숫자' || p.type === '날짜')) || P_.find((p) => row && row[p.col] && !p.sensitive);
    if (row && show) out.gold.push([`${ml} ${row[main.key]}의 ${L(show)}${J(L(show)) === '이' ? '은' : '는'}?`, String(row[show.col])]);
  }
  const main = top[0], nb = main && o.relations.find((x) => x.a_tbl === main.name || x.b_tbl === main.name);
  if (nb) {
    const other = o.objects.find((x) => x.name === (nb.a_tbl === main.name ? nb.b_tbl : nb.a_tbl));
    const oc = other?.props.find((p) => p.type === '글자' && !p.hidden && p.col !== other.key);
    if (other && oc) out.rule.push(`${main.label}에 이어진 ${other.label}의 ${L(oc)}${J(L(oc))} 비어 있으면 확인 필요`);
  }
  if (main?.nrows) out.gold.push([`${main.label}${J(main.label)} 모두 몇 건인가?`, `${main.nrows.toLocaleString()}건`]);
  ['rule', 'metric', 'gold'].forEach((k) => (out[k] = out[k].slice(0, 4)));
  return (EXS = { v: ST.version, d: out }).d;
}
// 칩 그리기: kind = rule · metric · gold, fill = 누르면 할 일(함수 이름)
async function exChips(kind, fill) {
  if (!ST.objects) return '';
  const d = await exSeeds().catch(() => null), list = d?.[kind] || [];
  if (!list.length) return '';
  return `<div class="exchips"><span class="muted">${ic('star', 12)} 내 데이터로 만든 예시 · 누르면 입력칸이 채워집니다</span><div class="chips" style="justify-content:flex-start;margin-top:6px">${list.map((x, i) => `<button type="button" onclick="${fill}(${i})">${esc(Array.isArray(x) ? x[0] : x)}</button>`).join('')}</div></div>`;
}
const exRule = (i) => { const t = $('#rTxt'); t.value = EXS.d.rule[i]; t.dispatchEvent(new Event('input')); t.focus(); };
const exMetric = (i) => { const t = $('#mTxt'); t.value = EXS.d.metric[i]; t.dispatchEvent(new Event('input')); t.focus(); };
const exGold = (i) => { $('#gQ').value = EXS.d.gold[i][0]; $('#gW').value = EXS.d.gold[i][1]; };
// 목록이 비었을 때: 예시를 누르면 만들기 화면이 그 문장으로 열림
const exRuleNew = (i) => { RNEW = { from: '#rules?new=' + encodeURIComponent('판단'), kind: '판단', text: EXS.d.rule[i], made: null }; location.hash = 'rules?new=' + encodeURIComponent('판단'); };
const exMetricNew = (i) => { metricModal({ text: EXS.d.metric[i] }); };
const exGoldNew = async (i) => { await goldModal(); exGold(i); };

// ── Copilot ──
const SUG = {
  home: ['지금 무엇부터 하면 되나요?'], source: ['가져온 테이블을 설명해 줘'], design: ['빠진 관계가 있는지 봐 줘'],
  read: ['읽을 칸 추천해 줘'], rules: ['규칙 예시를 들어 줘'], metrics: ['자주 볼 메트릭을 추천해 줘'], golden: ['골든 질문 예시를 들어 줘'], trace: [], explore: [], ask: ['예제 쿼리를 추천해 줘'], history: ['오늘 무엇이 바뀌었어?'], users: [],
};
function focusCop() { if ($('#cop').classList.contains('off')) toggleCop(); $('#cinput').focus(); }
function botSay(html) { const m = document.createElement('div'); m.className = 'm a'; m.innerHTML = `<span class="av">${ic('robot', 14)}</span><div class="bx">${html}</div>`; $('#msgs').appendChild(m); $('#msgs').scrollTop = 1e6; return m; }
function userSay(t) { const m = document.createElement('div'); m.className = 'm u'; m.textContent = t; $('#msgs').appendChild(m); $('#msgs').scrollTop = 1e6; }
const PROPS = [];
async function chatSend(text) {
  text = (text ?? $('#cinput').value).trim(); if (!text) return;
  $('#cinput').value = ''; focusCop(); userSay(text);
  const w = botSay('<span class="typing"><i></i><i></i><i></i></span>');
  try {
    const r = await post('/chat', { text, page: TITLE[cur()] });
    if (r.kind === 'answer') {
      // 데이터 질문은 데이터 에이전트 화면이 맡음 — 답을 데이터 에이전트 대화에 넣고 그쪽으로 안내
      CHAT.push({ q: text, r });
      w.querySelector('.bx').innerHTML = `<p>데이터 질문은 데이터 에이전트에서 답합니다.</p><p><b>${esc(r.answer)}</b></p><button class="btn xs out" onclick="fabOpen(true)">데이터 에이전트에서 근거·실행 단계 보기</button>`;
    } else if (r.kind === 'proposal') {
      const i = PROPS.push(r) - 1;
      w.querySelector('.bx').innerHTML = `<p>${esc(r.why || '아래와 같이 바꾸는 것을 제안합니다.')}</p><div class="prop"><div class="ph2">${ic('diff', 14)}${esc(r.title)}<span class="sp"></span><span class="b warn">승인 필요</span></div>
        <div class="pb mono">${r.lines.map(esc).join('<br>')}</div><div class="pf" id="pf${i}"><button class="btn xs pri" ${lock()} onclick="propose(${i})">변경 신청</button></div></div>`;
    } else w.querySelector('.bx').innerHTML = `<p>${esc(r.text)}</p>`;
  } catch (e) { w.querySelector('.bx').innerHTML = `<p>처리하지 못했습니다. ${esc(e.message)}</p>`; }
  $('#msgs').scrollTop = 1e6;
}
async function propose(i) {
  const p = PROPS[i];
  if (!(await confirmBox({ title: '변경을 신청하시겠습니까?', body: '검토자가 승인하면 적용됩니다.' }))) return;
  await post('/chat/propose', { title: p.title, layer: p.layer, op: p.op, lines: p.lines });
  $('#pf' + i).innerHTML = '<span class="b warn">승인 대기</span><span class="link" onclick="location.hash=\'history\'">변경 이력으로 이동</span>';
  toast('변경이 신청되었습니다.'); refresh();
}
function toggleCop() { $('#cop').classList.toggle('off'); $('#fab').classList.toggle('withcop', !$('#cop').classList.contains('off') && !$('#cop').classList.contains('hide')); $('#copToggle').innerHTML = `${ic('chat', 14)}${$('#cop').classList.contains('off') ? 'Copilot 열기' : 'Copilot 닫기'}`; }

// ── 그리기 ──
async function refresh() {
  [ST, ME] = await Promise.all([get('/state'), get('/me')]);
  if (!ME.setup && !ME.user) { setUid(''); const { users } = await get('/users'); const a = users.find((u) => u.role === '관리자') || users[0]; if (a) { setUid(a.id); ME = await get('/me'); } }
  renderWho(); render();
}
let renderSeq = 0;
async function render() {
  let c = P[cur()] && cur() !== 'home' ? cur() : 'workspace';
  const seq = ++renderSeq;
  if (isUser() && !['ask', 'trace', 'explore'].includes(c)) c = 'ask';
  if (c === 'users' && !can('admin')) c = 'design';
  $('#fab').classList.toggle('hide', c === 'ask' || !ME.user && !ME.setup); $('#fab').classList.toggle('withcop', !isUser() && c !== 'ask' && !$('#cop').classList.contains('off'));
  $('#cop').classList.toggle('hide', isUser() || c === 'ask'); $('#copToggle').style.display = isUser() || c === 'ask' ? 'none' : '';
  renderNav();
  $('#crumb').innerHTML = c === 'home' ? '<b>개요</b>' : c === 'ask' ? '<b>데이터 에이전트</b>' : c === 'connect' ? `데이터 원본 ${ic('chev', 12)} <b>연결</b>` : `<b>${TITLE[c]}</b>`;
  $('#ver').innerHTML = ST.version ? `<span class="b">현재 버전 v${ST.version}</span>${ST.pending ? ` <span class="b warn">승인 대기 ${ST.pending}건</span>` : ''}` : '';
  $('#llm').innerHTML = ST.llm?.available ? `LLM 연결 · ${esc(ST.llm.model)}` : 'LLM 미연결 · AI 기능 미사용';
  $('#ctx').textContent = TITLE[c];
  $('#sug').innerHTML = (SUG[c] || []).map((s) => `<button onclick="chatSend(this.textContent)">${s}</button>`).join('');
  try {
    const html = await P[c]();
    if (seq !== renderSeq) return;
    $('#page').innerHTML = html;
    if (c === 'rules' || c === 'metrics' || c === 'whatif') CRUMB = [['온톨로지 설계', '#design'], ...(CRUMB ? CRUMB.map((x, i) => (i === 0 ? [x[0], '#' + c] : x)) : [[TITLE[c]]])];
    if (CRUMB) { $('#crumb').innerHTML = CRUMB.map(([t, h], i) => (i < CRUMB.length - 1 ? `<a href="${h}">${esc(t)}</a> ${ic('chev', 12)}` : `<b>${esc(t)}</b>`)).join(' '); CRUMB = null; }
    if (c === 'ask') $('#aIn')?.focus();
    if (c === 'connect') bindConnect();
  } catch (e) { $('#page').innerHTML = `<div class="card">${empty(`${TITLE[c]} 화면을 불러오는 데 실패했습니다.`, `${esc(e.message)} 다시 시도해 주세요.`, `<button class="btn out" onclick="refresh()">다시 시도</button>`, false, 'warn')}</div>`; }
}
function init() {
  $('#copAv').innerHTML = ic('robot', 14); $('#copClose').innerHTML = ic('x', 16); $('#csend').innerHTML = ic('send', 16);
  $('#copToggle').innerHTML = `${ic('chat', 14)}Copilot 닫기`;
  $('#copToggle').onclick = toggleCop; $('#fabBtn').innerHTML = ic('chat', 24); $('#fabBtn').onclick = () => fabOpen(); $('#copClose').onclick = toggleCop;
  $('#dim').onclick = () => closePanel(); $('#csend').onclick = () => chatSend();
  document.addEventListener('click', (e) => { if (!e.target.closest('#whoMenu, #moreMenu, #getMenu')) closeMenu(); });
  window.addEventListener('unhandledrejection', (e) => toast(e.reason?.message || '요청을 처리하지 못했습니다. 다시 시도해 주세요.', true));
  $('#cinput').addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); chatSend(); } });
  document.addEventListener('keydown', (e) => { if (e.key !== 'Escape' || modalBusy) return; closeMenu(); if ($('#modalBg').classList.contains('on')) { modalClose ? modalClose() : $('#modalBg').classList.remove('on'); } else closePanel(); });
  botSay('<p>온톨로지를 만들며 궁금한 것을 묻거나 바꿀 것을 말해 주세요(예: 빠진 관계 찾아 줘). 바꾸는 것은 변경 신청 후 승인되어야 적용됩니다. 데이터 질문은 데이터 에이전트에서 답합니다.</p>');
  // 저장 안 한 입력이 있으면 다른 화면으로 가기 전에 확인(속성 편집 페이지 · 편집 패널)
  let lastHash = location.hash, guarding = false;
  window.addEventListener('hashchange', async () => {
    if (guarding) return;
    if (NODE.dirty) { guarding = true; const ok = await leaveNode(); guarding = false; if (!ok) { history.replaceState(null, '', lastHash || '#'); return; } }
    lastHash = location.hash; closePanel(true); render();
  });
  refresh();
  liveReload();
}
// 개발 중 자동 새로 고침 — 화면 파일이 바뀌면 열린 페이지가 스스로 다시 불러옴
function liveReload() {
  let stamp = null;
  setInterval(async () => {
    try { const s = (await get('/dev/stamp')).stamp; if (stamp && s !== stamp) location.reload(); stamp = s; } catch { /* 서버 재시작 중 */ }
  }, 1500);
}
init();
