import { createApp, ref, computed, onMounted } from '/apps/_runtime/vue.js'
import { query, actions, act } from '/apps/_runtime/og.js'

// ── 표시 도우미 ────────────────────────────────────────────────────────
const has = (v) => v !== undefined && v !== null && v !== ''
const NONE = '기록 없음'
const fmtNum = (n) => (has(n) && !isNaN(Number(n)) ? Number(n).toLocaleString('ko-KR') : NONE)
const fmtWon = (n) => (has(n) && !isNaN(Number(n)) ? `${Number(n).toLocaleString('ko-KR')}원` : NONE)
const fmtDays = (n) => (has(n) && !isNaN(Number(n)) ? `${Number(n).toLocaleString('ko-KR')}일` : NONE)
function fmtDate(s) {
  if (!has(s)) return NONE
  const m = String(s).match(/^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?/)
  if (!m) return String(s)
  return m[4] ? `${m[1]}.${m[2]}.${m[3]} ${m[4]}:${m[5]}` : `${m[1]}.${m[2]}.${m[3]}`
}
const day = (s) => (has(s) ? String(s).slice(0, 10) : null) // 'YYYY-MM-DD' 은 문자열 비교로 대소가 맞는다
function addDays(s, n) {
  const d = new Date(`${day(s)}T00:00:00Z`)
  d.setUTCDate(d.getUTCDate() + Number(n))
  return d.toISOString().slice(0, 10)
}
const diffDays = (a, b) => Math.round((new Date(`${day(b)}T00:00:00Z`) - new Date(`${day(a)}T00:00:00Z`)) / 86400000)
/** 이름이 아직 정해지지 않은 클래스(평가·업무·지급 지시)에서 후보 속성 중 처음 있는 값을 고른다. */
const pick = (o, keys) => { for (const k of keys) if (o && has(o[k])) return o[k]; return undefined }

const CLAIM_STATUS = {
  RECEIVED: '접수됨', EVIDENCE_REQUESTED: '보완 요청됨', PENDING_EVIDENCE: '보완 대기', UNDER_REVIEW: '심사 중',
  ASSESSED: '평가 완료', EVALUATED: '평가 완료', APPROVED: '지급 승인', REJECTED: '부지급', PAYMENT_REQUESTED: '지급 요청됨',
  PAID: '지급 완료', PAYMENT_UNKNOWN: '지급 결과 불명', CLOSED: '종결', CANCELLED: '취소',
}
const PAY_STATUS = {
  NONE: '지급 없음', CREATED: '지급 지시 생성', PENDING: '대기', READY: '요청 대기', REQUESTED: '지급 요청됨',
  PAID: '지급 완료', SUCCEEDED: '지급 완료', FAILED: '실패', UNKNOWN: '결과 불명', CANCELLED: '취소',
}
const ROLE = { POLICYHOLDER: '계약자', INSURED: '피보험자', BENEFICIARY: '수익자' }
const REC = { PAY: '지급', APPROVE: '지급', PAYABLE: '지급', REJECT: '부지급', DENY: '부지급', NOT_PAYABLE: '부지급', REVIEW: '추가 심사', MANUAL_REVIEW: '추가 심사', PEND: '보류' }
const label = (map, v) => (has(v) ? (map[v] ? `${map[v]}` : String(v)) : NONE)

// 지급 지시 상태 분류 — 한도 사용(paid_days + reserved_days_of_other_claims)
const isPaid = (s) => /^(PAID|SUCCEEDED|COMPLETED|SETTLED)$/i.test(s || '')
const isVoid = (s) => /^(CANCELLED|CANCELED|FAILED|REJECTED|VOID|REVERSED)$/i.test(s || '')
const canRequestPay = (s) => !/(REQUEST|PAID|SUCC|COMPLET|SETTL|UNKNOWN|FAIL|CANCEL|REJECT|VOID|REVERS)/i.test(s || '')
// 청구가 이미 결정(승인·부지급)이나 지급 단계로 넘어갔는가
const isDecided = (s) => /(APPROV|REJECT|DENI|PAID|PAYMENT|CLOS|CANCEL|WITHDRAW)/i.test(s || '')

const ORDER_CLAIM = ['claim_id']
const ORDER_COVERAGE = ['coverage_id']
const ORDER_INSURED = ['insured_claimant_no', 'insured_no', 'insured', 'patient_no', 'subject_claimant_no', 'claimant_no']
const ORDER_DAYS = ['payable_days', 'approved_days', 'granted_days', 'days', 'paid_days', 'reserved_days', 'stay_days']
const ORDER_AMOUNT = ['amount_krw', 'amount', 'payable_amount_krw', 'candidate_amount_krw']

// ── 질의 ───────────────────────────────────────────────────────────────
async function loadClaimIds() {
  const rows = await query('MATCH (c:InsuranceClaim) RETURN c.claim_id AS id, c.status AS status')
  return rows.map((r) => r).sort((a, b) => String(a.id).localeCompare(String(b.id)))
}

/** 청구인 번호 하나에서 사람 → 계약 고객 → 계약 역할까지 */
async function loadPersonSide(claimantNo) {
  if (!has(claimantNo)) return null
  const [base] = await query(
    'MATCH (s:Claimant) WHERE s.claimant_no = $n OPTIONAL MATCH (s:Claimant)-[:CLAIMANT_RECORD_OF]->(p:Person) RETURN s, p',
    { n: claimantNo })
  if (!base) return { claimant_no: claimantNo, claimant: null, person: null, customers: [] }
  const token = base.p ? base.p.identity_token : null
  let customers = []
  if (has(token)) {
    const rows = await query(
      'MATCH (cc:ContractCustomer)-[:CUSTOMER_RECORD_OF]->(p:Person) WHERE p.identity_token = $t ' +
      'OPTIONAL MATCH (cc:ContractCustomer)-[:HOLDS_ROLE]->(pr:PolicyRole) RETURN cc, collect(pr) AS roles', { t: token })
    customers = rows.map((r) => ({ ...r.cc, roles: (r.roles || []).filter(Boolean) }))
  }
  return { claimant_no: claimantNo, claimant: base.s, person: base.p, customers }
}

async function loadClaim(id) {
  const [row] = await query('MATCH (c:InsuranceClaim) WHERE c.claim_id = $id RETURN c', { id })
  if (!row) return null
  const c = row.c
  const [receiptRows, eventRows, covRows, polRows, subRows, assessRows, taskRows, orderRows, sameEventRows] = await Promise.all([
    query('MATCH (c:InsuranceClaim)-[:RECEIVED_VIA]->(r:ClaimReceipt) WHERE c.claim_id = $id RETURN r', { id }),
    query('MATCH (c:InsuranceClaim)-[:FOR_EVENT]->(e:InsuranceEvent) WHERE c.claim_id = $id RETURN e', { id }),
    query('MATCH (c:InsuranceClaim)-[:CLAIMS_COVERAGE]->(cv:Coverage) WHERE c.claim_id = $id ' +
      'OPTIONAL MATCH (cv:Coverage)-[:APPLIES_RULE]->(r:RuleSetVersion) RETURN cv, r', { id }),
    query('MATCH (c:InsuranceClaim)-[:CLAIM_UNDER_POLICY]->(p:Policy) WHERE c.claim_id = $id RETURN p', { id }),
    query('MATCH (c:InsuranceClaim)-[:CLAIM_SUBMITTED_BY]->(s:Claimant) WHERE c.claim_id = $id RETURN s.claimant_no AS no', { id }),
    query('MATCH (a:Assessment) RETURN a'),
    query('MATCH (t:ReviewTask) RETURN t'),
    query('MATCH (o:PaymentOrder) RETURN o'),
    query('MATCH (x:InsuranceClaim) WHERE x.event_id = $e RETURN x.claim_id AS id, x.status AS status', { e: c.event_id ?? '' }),
  ])
  const receipt = receiptRows[0] ? receiptRows[0].r : null
  const event = eventRows[0] ? eventRows[0].e : null
  const coverage = covRows[0] ? covRows[0].cv : null
  const rule = covRows[0] ? covRows[0].r : null
  const policy = polRows[0] ? polRows[0].p : null

  // 서류: 접수에 연결된 서류(현재·해제) + 확인 결과
  let docs = []
  if (receipt) {
    const rows = await query(
      'MATCH (d:Document)-[a:ATTACHED_TO]->(r:ClaimReceipt) WHERE r.receipt_no = $r ' +
      'OPTIONAL MATCH (v:DocumentVerification)-[:VERIFIES]->(d:Document) RETURN d, a, collect(v) AS vs', { r: receipt.receipt_no })
    docs = rows.map((x) => {
      const vs = (x.vs || []).filter(Boolean).sort((p, q) =>
        (Number(q.revision) || 0) - (Number(p.revision) || 0) || String(q.verified_at || '').localeCompare(String(p.verified_at || '')))
      const current = x.a ? (x.a.is_current !== false && !has(x.a.detached_at)) : true
      return { doc: x.d, link: x.a || {}, ver: vs[0] || null, olderVers: vs.slice(1), current }
    }).sort((p, q) => Number(q.current) - Number(p.current))
  }

  const submitterNo = subRows[0] ? subRows[0].no : (c.submitted_by_claimant_no ?? (receipt && receipt.submitter_no))
  const patientNo = event ? event.subject_claimant_no : (receipt && receipt.patient_no)
  const [submitter, patient] = await Promise.all([loadPersonSide(submitterNo), loadPersonSide(patientNo)])

  const byClaim = (o) => pick(o, ['claim_id']) === id
  const assessments = assessRows.map((r) => r.a).filter(byClaim)
    .sort((p, q) => String(pick(q, ['assessed_at', 'created_at']) || '').localeCompare(String(pick(p, ['assessed_at', 'created_at']) || '')))
  const tasks = taskRows.map((r) => r.t).filter(byClaim)
  const allOrders = orderRows.map((r) => r.o)

  return { claim: c, receipt, event, coverage, rule, policy, docs, submitter, patient, assessments, tasks, allOrders,
    sameEvent: sameEventRows.filter((r) => r.id !== id) }
}

// ── 앱 ─────────────────────────────────────────────────────────────────
createApp({
  setup() {
    const claimIds = ref([])
    const selected = ref('')
    const d = ref(null)
    const loading = ref(true)
    const error = ref('')
    const loadedAt = ref(null)
    const acts = ref({}) // 'Class.action' → 액션 정의

    async function loadActions() {
      const lists = await Promise.all(['InsuranceClaim', 'PaymentOrder', 'ReviewTask', 'Document'].map((c) => actions(c)))
      const m = {}
      for (const l of lists) for (const a of l || []) m[`${a.class}.${a.action}`] = a
      acts.value = m
    }

    async function load() {
      loading.value = true
      error.value = ''
      try {
        claimIds.value = await loadClaimIds()
        if (!selected.value) {
          const def = claimIds.value.find((x) => x.id === 'CL-001')
          selected.value = def ? def.id : (claimIds.value[0] ? claimIds.value[0].id : '')
        }
        d.value = selected.value ? await loadClaim(selected.value) : null
        loadedAt.value = new Date()
      } catch (e) {
        error.value = e.message || String(e)
      } finally {
        loading.value = false
      }
    }

    function choose(id) { selected.value = id; load() }

    // ── 1. 사람 ─────────────────────────────
    const policyId = computed(() => d.value && (d.value.claim.policy_id || (d.value.policy && d.value.policy.policy_id)))
    function rolesOf(side) {
      if (!side) return []
      const out = []
      for (const cc of side.customers) for (const r of cc.roles) if (!policyId.value || r.policy_id === policyId.value) out.push({ ...r, cust: cc })
      return out
    }
    const admission = computed(() => d.value && d.value.event && day(d.value.event.admission_date))
    const roleValidOn = (r, dt) => has(dt) && (!has(r.valid_from) || day(r.valid_from) <= dt) && (!has(r.valid_to) || dt < day(r.valid_to))
    const insuredCheck = computed(() => {
      if (!d.value) return null
      if (!d.value.event) return { state: 'none', text: '입원 사건 기록이 없어 판단할 수 없습니다' }
      const roles = rolesOf(d.value.patient).filter((r) => r.role_type === 'INSURED')
      if (!roles.length) return { state: 'bad', text: '입원한 사람에게 이 계약의 피보험자 역할 기록이 없습니다' }
      const ok = roles.find((r) => roleValidOn(r, admission.value))
      return ok
        ? { state: 'ok', text: `입원일 ${fmtDate(admission.value)}에 피보험자 (${ok.role_id}, ${fmtDate(ok.valid_from)}~${has(ok.valid_to) ? fmtDate(ok.valid_to) : '종료일 없음'})` }
        : { state: 'bad', text: `입원일 ${fmtDate(admission.value)}에 유효한 피보험자 역할이 아닙니다` }
    })
    const people = computed(() => d.value ? [
      { key: 'sub', title: '청구를 낸 사람', sub: '제출자', side: d.value.submitter },
      { key: 'pat', title: '입원한 사람', sub: '입원 사건 대상자', side: d.value.patient },
    ] : [])
    const samePerson = computed(() => {
      const a = d.value && d.value.submitter && d.value.submitter.person
      const b = d.value && d.value.patient && d.value.patient.person
      if (!a || !b) return null
      return a.identity_token === b.identity_token
    })

    // ── 2. 계약·보장 ─────────────────────────
    const periodCheck = computed(() => {
      const cv = d.value && d.value.coverage, e = d.value && d.value.event
      if (!cv || !e) return { state: 'none', text: '보장 또는 입원 사건 기록이 없어 판단할 수 없습니다' }
      const a = day(e.admission_date), dis = day(e.discharge_date), from = day(cv.valid_from), to = day(cv.valid_to)
      if (!has(a) || !has(from)) return { state: 'none', text: '입원일 또는 보장 시작일이 없습니다' }
      const inStart = from <= a && (!has(to) || a < to)
      const inEnd = !has(to) || !has(dis) || dis <= to
      if (inStart && inEnd) return { state: 'ok', text: `입원 ${fmtDate(a)}~${fmtDate(dis)} 이 보장 기간 ${fmtDate(from)}~${has(to) ? fmtDate(to) : ''} 안` }
      return { state: 'bad', text: !inStart ? `입원일 ${fmtDate(a)} 이 보장 기간 밖` : `퇴원일 ${fmtDate(dis)} 이 보장 종료일 ${fmtDate(to)} 이후` }
    })
    const waitingCheck = computed(() => {
      const cv = d.value && d.value.coverage, e = d.value && d.value.event
      if (!cv || !e) return { state: 'none', text: '보장 또는 입원 사건 기록이 없어 판단할 수 없습니다' }
      let end = day(cv.waiting_period_end), derived = false
      if (!has(end) && has(cv.waiting_days) && has(cv.valid_from)) { end = addDays(cv.valid_from, cv.waiting_days); derived = true }
      if (!has(end)) return { state: 'none', text: '대기 기간 기록이 없습니다' }
      const a = day(e.admission_date)
      const src = derived ? ' (보장 시작일+대기 일수로 계산)' : ''
      return a > end
        ? { state: 'ok', text: `대기 기간 종료 ${fmtDate(end)}${src} 이후 입원 — 대기 기간 경과` }
        : { state: 'bad', text: `입원일 ${fmtDate(a)} 이 대기 기간(종료 ${fmtDate(end)}${src}) 안` }
    })

    // ── 3. 서류 비교 ─────────────────────────
    function docRows(x) {
      const e = d.value.event || {}, v = x.ver, doc = x.doc
      const subjToken = d.value.patient && d.value.patient.person && d.value.patient.person.identity_token
      const fields = [
        { k: 'insured', name: '피보험자', ev: e.subject_claimant_no, ve: v && v.verified_insured, ex: doc.extracted_insured, conf: doc.extracted_insured_confidence },
        { k: 'provider', name: '의료기관', ev: e.provider_code, ve: v && v.verified_provider_code, ex: doc.extracted_provider_code, conf: doc.extracted_provider_code_confidence },
        { k: 'adm', name: '입원일', ev: e.admission_date, ve: v && v.verified_admission_date, ex: doc.extracted_admission_date, conf: doc.extracted_admission_date_confidence, date: true },
        { k: 'dis', name: '퇴원일', ev: e.discharge_date, ve: v && v.verified_discharge_date, ex: doc.extracted_discharge_date, conf: doc.extracted_discharge_date_confidence, date: true },
      ]
      return fields.map((f) => {
        const norm = (s) => (f.date ? day(s) : (has(s) ? String(s) : null))
        const verDiff = has(f.ev) && has(f.ve) && norm(f.ev) !== norm(f.ve)
        // 추출값의 피보험자는 동일인 토큰으로 나올 수 있다(예: TKN-B) — 대상자의 토큰과 같으면 일치로 본다
        const exSame = has(f.ex) && has(f.ev) && (norm(f.ex) === norm(f.ev) || (f.k === 'insured' && has(subjToken) && f.ex === subjToken))
        const exDiff = has(f.ex) && has(f.ev) && !exSame
        const show = (s) => (has(s) ? (f.date ? fmtDate(s) : String(s)) : NONE)
        return { ...f, evText: show(f.ev), veText: show(f.ve), exText: has(f.ex) ? show(f.ex) : '추출값 없음', verDiff, exDiff,
          exToken: f.k === 'insured' && has(f.ex) && f.ex === subjToken,
          confText: has(f.conf) ? `신뢰도 ${Math.round(Number(f.conf) * 100)}%` : '' }
      })
    }

    // ── 4. 한도 ─────────────────────────────
    const limit = computed(() => {
      if (!d.value) return null
      const cv = d.value.coverage, e = d.value.event, id = d.value.claim.claim_id
      const insuredNo = e ? e.subject_claimant_no : (d.value.receipt && d.value.receipt.patient_no)
      const covId = d.value.claim.coverage_id || (cv && cv.coverage_id)
      const orders = d.value.allOrders.filter((o) => {
        if (pick(o, ORDER_COVERAGE) !== covId) return false
        const ins = pick(o, ORDER_INSURED)
        return has(ins) ? ins === insuredNo : false
      })
      let paid = 0, reserved = 0, paidN = 0, resN = 0
      for (const o of orders) {
        const st = pick(o, ['status']), days = Number(pick(o, ORDER_DAYS)) || 0
        if (isVoid(st)) continue
        if (isPaid(st)) { paid += days; paidN++ } else if (pick(o, ORDER_CLAIM) !== id) { reserved += days; resN++ }
      }
      const max = cv && has(cv.max_days) ? Number(cv.max_days) : null
      const stay = e ? (has(e.stay_days) ? Number(e.stay_days) : (has(e.admission_date) && has(e.discharge_date) ? diffDays(e.admission_date, e.discharge_date) : null)) : null
      const used = paid + reserved
      const remain = max === null ? null : Math.max(0, max - used)
      return { orders, max, paid, reserved, paidN, resN, used, remain, stay, noOrders: orders.length === 0,
        over: remain !== null && stay !== null && stay > remain }
    })

    // ── 5. 평가·업무·지급 ────────────────────
    const currentAssessment = computed(() => {
      if (!d.value) return null
      const curId = d.value.claim.current_assessment_id
      const list = d.value.assessments
      if (has(curId)) return list.find((a) => pick(a, ['assessment_id', 'id']) === curId) || null
      return list[0] || null
    })
    const assessView = computed(() => {
      const a = currentAssessment.value
      if (!a) return null
      const reasons = pick(a, ['reason_codes', 'reason_code', 'reasons'])
      return {
        id: pick(a, ['assessment_id', 'id']),
        rec: pick(a, ['recommendation', 'decision', 'result']),
        days: pick(a, ['approved_days', 'allowed_days', 'payable_days', 'recognized_days', 'granted_days']),
        amount: pick(a, ['candidate_amount_krw', 'candidate_amount', 'amount_krw', 'payable_amount_krw']),
        reasons: Array.isArray(reasons) ? reasons.join(', ') : reasons,
        at: pick(a, ['assessed_at', 'created_at']),
        by: pick(a, ['assessed_by', 'actor_id', 'created_by']),
        ruleSet: pick(a, ['rule_set_id', 'rule_version']),
      }
    })
    const openTasks = computed(() => d.value ? d.value.tasks.filter((t) => !/(RESOLV|CLOSED|DONE|CANCEL)/i.test(t.status || '')) : [])
    const claimOrders = computed(() => d.value ? d.value.allOrders.filter((o) => pick(o, ORDER_CLAIM) === d.value.claim.claim_id) : [])

    // ── 액션 버튼 ───────────────────────────
    const busy = ref('')
    const claimButtons = computed(() => {
      if (!d.value) return { shown: [], hidden: [] }
      const st = d.value.claim.status
      const decided = isDecided(st)
      const hasAssess = !!currentAssessment.value || has(d.value.claim.current_assessment_id) || /(ASSESS|EVALUAT)/i.test(st || '')
      const defs = [
        { action: 'evaluateClaim', text: '평가', kind: '', ok: !decided, why: '이미 결정되었거나 지급 단계인 청구' },
        { action: 'requestEvidence', text: '보완 요청', kind: '', ok: !decided, why: '이미 결정되었거나 지급 단계인 청구',
          params: () => { const t = d.value.rule && d.value.rule.required_document_types; return has(t) ? { missing_item: String(t).split(',')[0].trim() } : {} } },
        { action: 'approveClaim', text: '지급 승인', kind: 'primary', ok: !decided && hasAssess, why: decided ? '이미 결정된 청구' : '현재 평가 없음 — 먼저 평가' },
        { action: 'rejectClaim', text: '부지급', kind: 'danger', ok: !decided && hasAssess, why: decided ? '이미 결정된 청구' : '현재 평가 없음 — 먼저 평가' },
      ].filter((b) => acts.value[`InsuranceClaim.${b.action}`])
      return { shown: defs.filter((b) => b.ok), hidden: defs.filter((b) => !b.ok) }
    })
    const hasAct = (k) => !!acts.value[k]

    async function run(cls, action, ids, params, title) {
      busy.value = `${cls}.${action}`
      try {
        const out = await act({ class: cls, action, ids, params: params || {}, title })
        if (out.executed) await load()
      } finally {
        busy.value = ''
      }
    }
    const runClaim = (b) => run('InsuranceClaim', b.action, [d.value.claim.claim_id], b.params ? b.params() : {}, `${b.text} — ${d.value.claim.claim_id}`)
    const runPay = (o) => run('PaymentOrder', 'requestPayment', [o.payment_order_id], {}, `지급 요청 — ${o.payment_order_id}`)
    const runResolve = (t) => run('ReviewTask', 'resolveReviewTask', [t.task_id], {}, `심사 업무 해결 — ${t.task_id}`)

    onMounted(async () => { await Promise.all([loadActions(), load()]) })

    return { claimIds, selected, d, loading, error, loadedAt, choose, load,
      people, rolesOf, insuredCheck, samePerson, periodCheck, waitingCheck, docRows, limit, admission, roleValidOn,
      assessView, openTasks, claimOrders, claimButtons, busy, hasAct, runClaim, runPay, runResolve, canRequestPay,
      fmtNum, fmtWon, fmtDays, fmtDate, label, has, pick, NONE, CLAIM_STATUS, PAY_STATUS, ROLE, REC, ORDER_DAYS, ORDER_AMOUNT }
  },

  template: `
<div class="page">
  <header class="top">
    <div class="top-row">
      <div class="title">
        <h1>청구 심사</h1>
        <span class="note" title="이 화면의 값은 온톨로지 그래프에 적재된 시점의 값입니다. 업무 시스템의 최신 값과 다를 수 있습니다.">그래프 값은 적재 시점 기준</span>
      </div>
      <div class="top-tools">
        <label class="pick">청구
          <select :value="selected" @change="choose($event.target.value)" :disabled="loading && !claimIds.length">
            <option v-if="!claimIds.length" value="">청구 없음</option>
            <option v-for="c in claimIds" :key="c.id" :value="c.id">{{ c.id }} · {{ label(CLAIM_STATUS, c.status) }}</option>
          </select>
        </label>
        <button class="ghost" @click="load" :disabled="loading">{{ loading ? '불러오는 중…' : '다시 읽기' }}</button>
      </div>
    </div>

    <div v-if="d" class="summary">
      <div class="kv"><span>청구</span><b>{{ d.claim.claim_id }}</b></div>
      <div class="kv"><span>심사 상태</span><b class="badge" :class="'st-' + (d.claim.status || 'none')">{{ label(CLAIM_STATUS, d.claim.status) }}</b><code v-if="d.claim.status">{{ d.claim.status }}</code></div>
      <div class="kv"><span>담당 심사자</span><b>{{ d.claim.assigned_reviewer_id || NONE }}</b></div>
      <div class="kv"><span>지급 상태</span><b>{{ label(PAY_STATUS, d.claim.payment_status) }}</b></div>
      <div class="kv"><span>제출 시각</span><b>{{ fmtDate(d.claim.submitted_at) }}</b></div>
      <div class="kv"><span>접수</span><b>{{ d.claim.receipt_no || NONE }}</b></div>
      <div class="actions">
        <button v-for="b in claimButtons.shown" :key="b.action" :class="b.kind" :disabled="!!busy" @click="runClaim(b)">{{ b.text }}</button>
        <span v-if="!claimButtons.shown.length && !claimButtons.hidden.length" class="dim small">액션 실행기가 꺼져 있어 버튼이 없습니다</span>
        <span v-else-if="claimButtons.hidden.length" class="dim small" :title="claimButtons.hidden.map(b => b.text + ': ' + b.why).join('\\n')">
          지금 할 수 없는 액션: {{ claimButtons.hidden.map(b => b.text).join(', ') }} ({{ claimButtons.hidden[0].why }})
        </span>
      </div>
    </div>
    <p v-if="d" class="dim small actor-hint">버튼을 누르면 확인 창에서 담당자 ID(actor_id)를 입력하고, 계획을 본 뒤 승인합니다.</p>
  </header>

  <div v-if="loading && !d" class="state">청구를 불러오는 중…</div>
  <div v-else-if="error" class="state err">불러오지 못했습니다: {{ error }} <button class="ghost" @click="load">다시 시도</button></div>
  <div v-else-if="!d" class="state">{{ claimIds.length ? '선택한 청구를 찾을 수 없습니다' : '온톨로지에 청구(InsuranceClaim)가 없습니다' }}</div>

  <main v-else class="grid" :class="{ fading: loading }">
    <div v-if="d.sameEvent.length" class="alert span2">같은 입원 사건 {{ d.claim.event_id }}에 연결된 다른 청구가 있습니다:
      <b v-for="x in d.sameEvent" :key="x.id" class="chip">{{ x.id }} · {{ label(CLAIM_STATUS, x.status) }}</b> — 중복 여부를 확인하세요.</div>

    <!-- 1. 사람 -->
    <section class="card span2">
      <h2><i>1</i> 사람 <small>청구인 → 사람 → 계약 고객 → 계약 역할</small></h2>
      <div class="check" :class="insuredCheck.state">
        <span class="dot"></span><b>입원한 사람의 피보험자 여부</b> {{ insuredCheck.text }}
      </div>
      <p v-if="samePerson !== null" class="dim small">{{ samePerson ? '제출자와 입원한 사람이 같은 사람입니다.' : '제출자와 입원한 사람이 다른 사람입니다 (동일인 토큰이 다름).' }}</p>
      <div class="people">
        <div v-for="p in people" :key="p.key" class="person">
          <div class="person-head"><b>{{ p.title }}</b><span class="dim">{{ p.sub }}</span></div>
          <template v-if="p.side && p.side.claimant">
            <div class="who">{{ (p.side.person && p.side.person.display_name) || p.side.claimant.display_name || '이름 없음' }}</div>
            <dl class="dl">
              <dt>청구인 번호</dt><dd><code>{{ p.side.claimant.claimant_no }}</code></dd>
              <dt>사람(동일인 토큰)</dt><dd>{{ p.side.person ? p.side.person.identity_token : '연결된 사람 없음' }}</dd>
              <dt>계약 고객</dt><dd>
                <span v-if="!p.side.customers.length">연결된 계약 고객 없음</span>
                <code v-for="cc in p.side.customers" :key="cc.cust_no" class="mr">{{ cc.cust_no }}</code></dd>
            </dl>
            <table class="tbl" v-if="rolesOf(p.side).length">
              <thead><tr><th>역할</th><th>역할 ID</th><th>계약</th><th>유효 기간</th><th>입원일 기준</th></tr></thead>
              <tbody><tr v-for="r in rolesOf(p.side)" :key="r.role_id">
                <td><b>{{ label(ROLE, r.role_type) }}</b> <span class="dim small">{{ r.role_type }}</span></td>
                <td><code>{{ r.role_id }}</code></td>
                <td>{{ r.policy_id }}</td>
                <td>{{ fmtDate(r.valid_from) }} ~ {{ has(r.valid_to) ? fmtDate(r.valid_to) : '종료일 없음' }}</td>
                <td><span v-if="!admission" class="dim">입원일 없음</span><span v-else-if="roleValidOn(r, admission)" class="ok-t">유효</span><span v-else class="bad-t">유효 아님</span></td>
              </tr></tbody>
            </table>
            <p v-else class="empty">이 계약에서 맡은 역할 기록 없음</p>
          </template>
          <p v-else class="empty">{{ p.side ? '청구인 ' + p.side.claimant_no + ' 기록이 그래프에 없습니다' : '청구인 기록 없음' }}</p>
        </div>
      </div>
    </section>

    <!-- 2. 계약·보장 -->
    <section class="card span2">
      <h2><i>2</i> 계약 · 보장 · 심사 규칙</h2>
      <div class="checks">
        <div class="check" :class="periodCheck.state"><span class="dot"></span><b>보장 기간</b> {{ periodCheck.text }}</div>
        <div class="check" :class="waitingCheck.state"><span class="dot"></span><b>대기 기간</b> {{ waitingCheck.text }}</div>
      </div>
      <div class="three">
        <div class="sub">
          <h3>계약</h3>
          <dl v-if="d.policy" class="dl">
            <dt>계약 ID</dt><dd><code>{{ d.policy.policy_id }}</code></dd>
            <dt>대외 계약 번호</dt><dd>{{ d.policy.policy_number || NONE }}</dd>
            <dt>계약 기간</dt><dd>{{ fmtDate(d.policy.contract_from) }} ~ {{ fmtDate(d.policy.contract_to) }}</dd>
            <dt>계약 상태</dt><dd>{{ d.policy.administrative_status === 'ACTIVE' ? '유지 (ACTIVE)' : (d.policy.administrative_status || NONE) }}</dd>
          </dl>
          <p v-else class="empty">계약 기록 없음</p>
        </div>
        <div class="sub">
          <h3>보장</h3>
          <dl v-if="d.coverage" class="dl">
            <dt>보장</dt><dd><code>{{ d.coverage.coverage_id }}</code> {{ d.coverage.coverage_code }}</dd>
            <dt>1일 지급액</dt><dd class="num">{{ fmtWon(d.coverage.daily_amount_krw) }}</dd>
            <dt>한도 일수</dt><dd class="num">{{ fmtDays(d.coverage.max_days) }} <span class="dim small">/ 보장 기간</span></dd>
            <dt>대기 일수</dt><dd class="num">{{ fmtDays(d.coverage.waiting_days) }} <span v-if="d.coverage.waiting_period_end" class="dim small">(~{{ fmtDate(d.coverage.waiting_period_end) }})</span></dd>
            <dt>보장 기간</dt><dd>{{ fmtDate(d.coverage.valid_from) }} ~ {{ fmtDate(d.coverage.valid_to) }}</dd>
          </dl>
          <p v-else class="empty">보장 기록 없음</p>
        </div>
        <div class="sub">
          <h3>심사 규칙 버전</h3>
          <dl v-if="d.rule" class="dl">
            <dt>규칙</dt><dd><code>{{ d.rule.rule_code }}</code> 버전 {{ d.rule.version }}</dd>
            <dt>약관</dt><dd>{{ d.rule.clause_reference || NONE }}</dd>
            <dt>필요 서류</dt><dd>{{ d.rule.required_document_types || NONE }}</dd>
            <dt>입원 일수</dt><dd class="small">{{ d.rule.stay_days_rule || NONE }}</dd>
            <dt>한도 사용</dt><dd class="small"><code>{{ d.rule.limit_usage_rule || NONE }}</code></dd>
            <dt>게시</dt><dd>{{ fmtDate(d.rule.published_at) }}</dd>
          </dl>
          <p v-else class="empty">{{ d.coverage ? '보장에 연결된 규칙 버전 기록 없음' : '규칙 기록 없음' }}</p>
        </div>
      </div>
    </section>

    <!-- 3. 서류 -->
    <section class="card span2">
      <h2><i>3</i> 서류 대조 <small>입원 사건 값 · 심사자 확인값 · 추출값(참고)</small></h2>
      <p v-if="!d.receipt" class="empty">접수 기록이 없어 서류를 찾을 수 없습니다</p>
      <p v-else-if="!d.docs.length" class="empty">접수 {{ d.receipt.receipt_no }}에 연결된 서류 기록 없음</p>
      <div v-for="x in d.docs" :key="x.doc.doc_id" class="doc" :class="{ detached: !x.current }">
        <div class="doc-head">
          <b>{{ x.doc.name || x.doc.doc_id }}</b>
          <span class="chip">{{ x.doc.document_type === 'HOSPITALIZATION_CERTIFICATE' ? '입퇴원확인서' : x.doc.document_type }}</span>
          <span v-if="x.current" class="chip ok">현재 연결</span><span v-else class="chip">해제됨 {{ fmtDate(x.link.detached_at) }}</span>
          <span class="dim small">업로드 {{ fmtDate(x.doc.uploaded_at) }}</span>
          <span class="grow"></span>
          <span v-if="x.ver" class="small">확인 <b :class="x.ver.verification_status === 'VERIFIED' ? 'ok-t' : 'bad-t'">{{ x.ver.verification_status === 'VERIFIED' ? '확인 완료' : x.ver.verification_status }}</b>
            · {{ x.ver.verified_by }} · {{ fmtDate(x.ver.verified_at) }}</span>
          <span v-else class="bad-t small">심사자 확인 기록 없음</span>
        </div>
        <table class="tbl cmp">
          <thead><tr><th>항목</th><th>입원 사건 값</th><th>확인값 (심사자)</th><th class="ex">추출값 (확인 전 후보)</th><th>대조</th></tr></thead>
          <tbody><tr v-for="r in docRows(x)" :key="r.k">
            <td>{{ r.name }}</td>
            <td>{{ r.evText }}</td>
            <td :class="{ diff: r.verDiff, missing: !x.ver }">{{ x.ver ? r.veText : '확인 전' }}</td>
            <td class="ex" :class="{ 'ex-diff': r.exDiff }">{{ r.exText }} <span v-if="r.exToken" class="small">(동일인 토큰)</span> <span class="small">{{ r.confText }}</span></td>
            <td><span v-if="!x.ver" class="dim">확인값 없음</span><span v-else-if="r.verDiff" class="bad-t">불일치</span><span v-else-if="r.evText === NONE" class="dim">사건 값 없음</span><span v-else class="ok-t">일치</span></td>
          </tr></tbody>
        </table>
        <p v-if="x.ver && x.ver.supports_event_id && d.event && x.ver.supports_event_id !== d.event.event_id" class="bad-t small">이 확인 결과가 뒷받침하는 사건({{ x.ver.supports_event_id }})이 청구의 사건({{ d.event.event_id }})과 다릅니다.</p>
      </div>
      <p v-if="d.receipt" class="dim small">접수 신고값(확인 전): 의료기관 {{ d.receipt.reported_provider_code || NONE }}, {{ fmtDate(d.receipt.reported_admission_date) }} ~ {{ fmtDate(d.receipt.reported_discharge_date) }} · 접수 {{ fmtDate(d.receipt.received_at) }}</p>
    </section>

    <!-- 4. 한도 -->
    <section class="card span2">
      <h2><i>4</i> 한도 <small>같은 보장 · 같은 피보험자의 지급 지시 기준</small></h2>
      <div class="tiles">
        <div class="tile"><span>한도 일수</span><b>{{ limit.max === null ? NONE : fmtDays(limit.max) }}</b><em>보장 기간당</em></div>
        <div class="tile"><span>지급 일수 합계</span><b :class="{ none: limit.noOrders || !limit.paidN }">{{ limit.paidN ? fmtDays(limit.paid) : NONE }}</b><em>{{ limit.paidN ? '지급 지시 ' + limit.paidN + '건' : '지급 완료 지시 없음' }}</em></div>
        <div class="tile"><span>예약 일수 합계</span><b :class="{ none: !limit.resN }">{{ limit.resN ? fmtDays(limit.reserved) : NONE }}</b><em>{{ limit.resN ? '다른 청구 ' + limit.resN + '건' : '다른 청구의 미지급 지시 없음' }}</em></div>
        <div class="tile accent"><span>남은 일수</span><b>{{ limit.remain === null ? NONE : fmtDays(limit.remain) }}</b>
          <em>{{ limit.remain === null ? '한도 일수 없음' : (limit.noOrders ? '지급 지시 기록이 없어 한도 전부' : '한도 − 지급 − 예약') }}</em></div>
        <div class="tile" :class="{ warn: limit.over }"><span>이번 청구 입원 일수</span><b>{{ limit.stay === null ? NONE : fmtDays(limit.stay) }}</b>
          <em v-if="limit.over">남은 일수보다 많음 — 일부만 인정될 수 있음</em><em v-else>퇴원일 − 입원일</em></div>
      </div>
      <div v-if="limit.max" class="bar" :title="'지급 ' + limit.paid + '일 · 예약 ' + limit.reserved + '일 · 이번 청구 ' + (limit.stay || 0) + '일 / 한도 ' + limit.max + '일'">
        <div class="seg paid" :style="{ width: Math.min(100, limit.paid / limit.max * 100) + '%' }"></div>
        <div class="seg res" :style="{ width: Math.min(100, limit.reserved / limit.max * 100) + '%' }"></div>
        <div class="seg cur" :class="{ over: limit.over }" :style="{ width: Math.min(100 - Math.min(100, limit.used / limit.max * 100), (limit.stay || 0) / limit.max * 100) + '%' }"></div>
      </div>
      <div v-if="limit.max" class="legend small"><span><i class="paid"></i>지급</span><span><i class="res"></i>예약(다른 청구)</span><span><i class="cur"></i>이번 청구</span></div>
    </section>

    <!-- 5. 평가·업무·지급 -->
    <section class="card">
      <h2><i>5</i> 현재 평가</h2>
      <dl v-if="assessView" class="dl">
        <dt>평가 ID</dt><dd><code>{{ assessView.id || NONE }}</code></dd>
        <dt>권고</dt><dd><b>{{ has(assessView.rec) ? label(REC, assessView.rec) : NONE }}</b> <span v-if="has(assessView.rec)" class="dim small">{{ assessView.rec }}</span></dd>
        <dt>인정 일수</dt><dd class="num">{{ fmtDays(assessView.days) }}</dd>
        <dt>후보 금액</dt><dd class="num">{{ fmtWon(assessView.amount) }}</dd>
        <dt>사유 코드</dt><dd>{{ has(assessView.reasons) ? assessView.reasons : NONE }}</dd>
        <dt>평가 시각</dt><dd>{{ fmtDate(assessView.at) }} <span v-if="assessView.by" class="dim small">{{ assessView.by }}</span></dd>
      </dl>
      <p v-else class="empty">평가 기록 없음 <span class="dim small">— 「평가」 버튼으로 평가할 수 있습니다</span></p>
    </section>

    <section class="card">
      <h2>미해결 심사 업무 <small>그래프 기준 {{ openTasks.length ? openTasks.length + '건' : '' }}</small></h2>
      <table v-if="openTasks.length" class="tbl">
        <thead><tr><th>업무</th><th>유형</th><th>상태</th><th>내용</th><th></th></tr></thead>
        <tbody><tr v-for="t in openTasks" :key="t.task_id">
          <td><code>{{ t.task_id || NONE }}</code></td>
          <td>{{ pick(t, ['task_type', 'type', 'missing_item']) || NONE }}</td>
          <td>{{ t.status || NONE }}</td>
          <td class="small">{{ pick(t, ['message', 'description', 'reason', 'note']) || '' }}</td>
          <td><button v-if="hasAct('ReviewTask.resolveReviewTask') && t.task_id" class="sm" :disabled="!!busy" @click="runResolve(t)">해결 처리</button></td>
        </tr></tbody>
      </table>
      <p v-else class="empty">미해결 업무 기록 없음</p>
      <p v-if="has(d.claim.open_task_count) && Number(d.claim.open_task_count) !== openTasks.length" class="dim small">청구 노드의 미해결 업무 수: {{ fmtNum(d.claim.open_task_count) }}건 (업무 기록과 적재 시점이 다를 수 있음)</p>
    </section>

    <section class="card span2">
      <h2>지급 지시 <small>이 청구</small></h2>
      <table v-if="claimOrders.length" class="tbl">
        <thead><tr><th>지급 지시</th><th>상태</th><th class="r">일수</th><th class="r">금액</th><th>생성</th><th></th></tr></thead>
        <tbody><tr v-for="o in claimOrders" :key="o.payment_order_id">
          <td><code>{{ o.payment_order_id || NONE }}</code></td>
          <td>{{ label(PAY_STATUS, o.status) }} <span class="dim small">{{ o.status }}</span></td>
          <td class="r">{{ fmtDays(pick(o, ORDER_DAYS)) }}</td>
          <td class="r">{{ fmtWon(pick(o, ORDER_AMOUNT)) }}</td>
          <td>{{ fmtDate(pick(o, ['created_at', 'approved_at'])) }}</td>
          <td class="r"><button v-if="hasAct('PaymentOrder.requestPayment') && o.payment_order_id && canRequestPay(o.status)" class="sm primary" :disabled="!!busy" @click="runPay(o)">지급 요청</button></td>
        </tr></tbody>
      </table>
      <p v-else class="empty">지급 지시 기록 없음 <span class="dim small">— 지급 승인 후 생깁니다. 청구의 지급 상태: {{ label(PAY_STATUS, d.claim.payment_status) }}</span></p>
    </section>
  </main>

  <footer v-if="loadedAt" class="foot dim small">화면을 읽은 시각 {{ loadedAt.toLocaleString('ko-KR') }} · 값은 그래프에 적재된 시점 기준이며 업무 시스템과 다를 수 있습니다.</footer>
</div>`,
}).mount('#app')
