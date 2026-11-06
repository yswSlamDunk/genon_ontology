"""심사 시스템 (ins-review, :18103) — 규칙 버전, 확정 사건, 증빙 확인, 청구, 평가, 심사 업무, 지급 지시, 실행 이력.
인증: Bearer (env INS_REVIEW_TOKEN). 지급 결과 콜백(A10)만 Bearer 대신 서명(X-Payment-Signature).

쓰기: 명세 8절 A01 2단계, A02 2단계, A03–A11. 서버_설계서.md 7절.
다른 시스템 값(계약 역할·보장, 접수 서류 연결, 동일인 토큰)은 그 시스템 API로 읽는다.
식별자: 청구 CL-…, 사건 EV-…, 평가 AS-…, 업무 TK-…, 지급 지시 PY-…, 규칙 RV-…, 이력 AL-…, 전송 대기 OB-….
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from fastapi import Depends, Header, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field

import evaluation
from common import (LIMIT, DependencyError, IdemKey, Reject, bearer_auth, call, canonical_hash, db, db_write,
                    get_or_none, idem_begin, idem_finish, make_app, next_id, one, plain, rows, signature_ok, where)

app = make_app(
    title="심사 시스템",
    description="보험금 심사 업무 시스템. 청구 처리 상태, 확정된 입원 사건, 증빙 확인 결과, 평가 기록, 심사 업무, "
                "지급 지시(한도 예약), 실행 이력, 심사 규칙 버전을 다룬다. 쓰기: 청구 등록, 증빙 연결 반영·확인, 평가, "
                "보완 요청, 업무 해결, 지급 승인·부지급 결정, 지급 요청·결과 반영·대사. 데이터는 insurance DB의 review 스키마다.",
    schema="review",
)
auth = bearer_auth("INS_REVIEW_TOKEN")
AUTH = [Depends(auth)]
S = "review"
SEOUL = ZoneInfo("Asia/Seoul")
CLOSED = {"APPROVED", "REJECTED", "PAID"}
LOGIC_HASH = hashlib.sha256(Path(evaluation.__file__).read_bytes()).hexdigest()

CLAIM = ("SELECT claim_id, receipt_no, policy_id, coverage_id, event_id, submitted_by_claimant_no, submitted_at, status, "
         "current_assessment_id, assigned_reviewer_id, created_at, updated_at, revision FROM review.claim")
ASSESSMENT = ("SELECT assessment_id, claim_id, rule_set_id, evaluated_at, input_snapshot, input_hash, rule_results, "
              "recommendation, eligible_days, candidate_amount_krw, reason_codes, created_at FROM review.assessment")
TASK = ("SELECT task_id, claim_id, task_type, reason_code, related_ref, status, assignee_id, reason_note, resolution, "
        "resolved_by, resolved_at, created_at, updated_at, revision FROM review.review_task")
EVENT = ("SELECT event_id, intake_accident_no, subject_claimant_no, event_type, provider_code, admission_date, "
         "discharge_date, fact_status, created_at, updated_at, revision FROM review.insurance_event")
VERIFICATION = ("SELECT doc_id, supports_event_id, verification_status, verified_facts, verified_by, verified_at, "
                "verification_note, created_at, updated_at, revision FROM review.document_verification")
RULE = ("SELECT rule_set_id, rule_code, version, published_at, clause_reference, definition_ref, definition_hash, "
        "logic_hash, required_document_types, created_at FROM review.rule_set_version")
ORDER = ("SELECT payment_order_id, claim_id, assessment_id, beneficiary_cust_no, insured_cust_no, policy_id, coverage_id, "
         "benefit_period_key, reserved_days, amount_krw, status, payment_key, external_transaction_id, decided_by, "
         "decided_at, created_at, updated_at, revision FROM review.payment_order")
LOG = ("SELECT log_id, action_type, actor_id, target_refs, executed_at, idempotency_key, before_hash, after_hash, outcome, "
       "reason, created_at FROM review.action_log")


# ═══ 조회 ═══════════════════════════════════════════════════════════════════

@app.get("/claims/{claim_id}", operation_id="getClaim", summary="청구 조회", dependencies=AUTH,
         description="청구 ID(예: CL-001)로 청구 1건을 돌려준다. 미해결 심사 업무 수와 지급 지시 요약을 함께 담는다.")
def get_claim(claim_id: str):
    with db() as conn:
        return _claim_view(conn, claim_id)


def _claim_view(conn, claim_id: str) -> dict:
    claim = one(conn, CLAIM + " WHERE claim_id = %s", (claim_id,), f"청구 {claim_id}")
    claim["open_task_count"] = conn.execute(
        "SELECT count(*) AS n FROM review.review_task WHERE claim_id = %s AND status = 'OPEN'", (claim_id,)).fetchone()["n"]
    claim["payment_order"] = conn.execute(
        "SELECT payment_order_id, status, amount_krw, reserved_days, payment_key FROM review.payment_order WHERE claim_id = %s",
        (claim_id,)).fetchone()
    return claim


@app.get("/claims", operation_id="listClaims", summary="청구 목록", dependencies=AUTH,
         description="처리 상태나 접수 번호(접수 시스템의 RC-…)로 청구를 찾는다.")
def list_claims(status: str | None = Query(None, description="RECEIVED, UNDER_REVIEW, NEED_INFO, READY_FOR_DECISION, "
                                                              "APPROVED, REJECTED, PAID"),
                receipt_no: str | None = Query(None, description="접수 번호"), limit: int = LIMIT):
    w, p = where({"status": status, "receipt_no": receipt_no})
    with db() as conn:
        return rows(conn, CLAIM + w + " ORDER BY claim_id LIMIT %s", (*p, limit))


@app.get("/claims/{claim_id}/assessments", operation_id="listAssessments", summary="청구의 평가 이력", dependencies=AUTH,
         description="청구의 평가 기록을 최신순으로 돌려준다. 평가는 수정되지 않고 새로 쌓인다.")
def list_assessments(claim_id: str, limit: int = LIMIT):
    with db() as conn:
        one(conn, "SELECT 1 FROM review.claim WHERE claim_id = %s", (claim_id,), f"청구 {claim_id}")
        return rows(conn, ASSESSMENT + " WHERE claim_id = %s ORDER BY evaluated_at DESC, assessment_id DESC LIMIT %s",
                    (claim_id, limit))


@app.get("/assessments/{assessment_id}", operation_id="getAssessment", summary="평가 조회 (사용한 증빙 포함)",
         dependencies=AUTH, description="평가 ID로 평가 1건과 평가가 사용한 증빙(당시 문서 해시)을 돌려준다.")
def get_assessment(assessment_id: str):
    with db() as conn:
        a = one(conn, ASSESSMENT + " WHERE assessment_id = %s", (assessment_id,), f"평가 {assessment_id}")
        a["evidence"] = rows(conn, "SELECT doc_id, content_hash FROM review.assessment_evidence WHERE assessment_id = %s "
                                   "ORDER BY doc_id", (assessment_id,))
        return a


@app.get("/claims/{claim_id}/tasks", operation_id="listReviewTasks", summary="청구의 심사 업무", dependencies=AUTH,
         description="청구의 심사 업무를 돌려준다. status=OPEN 이면 미해결 업무만.")
def list_review_tasks(claim_id: str, status: str | None = Query(None, description="OPEN 또는 RESOLVED"),
                      limit: int = LIMIT):
    w, p = where({"claim_id": claim_id, "status": status})
    with db() as conn:
        one(conn, "SELECT 1 FROM review.claim WHERE claim_id = %s", (claim_id,), f"청구 {claim_id}")
        return rows(conn, TASK + w + " ORDER BY created_at, task_id LIMIT %s", (*p, limit))


@app.get("/tasks/{task_id}", operation_id="getReviewTask", summary="심사 업무 조회", dependencies=AUTH,
         description="업무 ID(예: TK-001)로 심사 업무 1건을 돌려준다.")
def get_review_task(task_id: str):
    with db() as conn:
        return one(conn, TASK + " WHERE task_id = %s", (task_id,), f"업무 {task_id}")


@app.get("/events/{event_id}", operation_id="getInsuranceEvent", summary="입원 사건 조회", dependencies=AUTH,
         description="사건 ID(예: EV-001)로 확정된 입원 사건을 돌려준다. fact_status 가 VERIFIED 인 값만 확정 사실이다.")
def get_insurance_event(event_id: str):
    with db() as conn:
        return one(conn, EVENT + " WHERE event_id = %s", (event_id,), f"사건 {event_id}")


@app.get("/documents/{doc_id}/verification", operation_id="getDocumentVerification", summary="증빙 확인 결과",
         dependencies=AUTH, description="서류 ID(예: DC-001)의 확인 상태, 확인값, 확인자, 지지하는 사건을 돌려준다.")
def get_document_verification(doc_id: str):
    with db() as conn:
        return one(conn, VERIFICATION + " WHERE doc_id = %s", (doc_id,), f"서류 {doc_id} 의 확인 결과")


@app.get("/rules/{rule_set_id}", operation_id="getRuleSetVersion", summary="심사 규칙 버전 조회", dependencies=AUTH,
         description="규칙 버전 ID(예: RV-001)로 규칙 정의 위치, 해시, 필수 서류 유형을 돌려준다.")
def get_rule_set_version(rule_set_id: str):
    with db() as conn:
        return one(conn, RULE + " WHERE rule_set_id = %s", (rule_set_id,), f"규칙 버전 {rule_set_id}")


@app.get("/rules", operation_id="listRuleSetVersions", summary="심사 규칙 버전 목록", dependencies=AUTH,
         description="계약 보장이 가리키는 (규칙 코드, 버전)으로 규칙 버전을 찾는다.")
def list_rule_set_versions(rule_code: str | None = Query(None, description="규칙 코드 (예: INPATIENT-DAILY)"),
                           version: str | None = Query(None, description="버전 (예: 1.0)"), limit: int = LIMIT):
    w, p = where({"rule_code": rule_code, "version": version})
    with db() as conn:
        return rows(conn, RULE + w + " ORDER BY rule_code, version LIMIT %s", (*p, limit))


@app.get("/payment-orders/{payment_order_id}", operation_id="getPaymentOrder", summary="지급 지시 조회",
         dependencies=AUTH, description="지급 지시 ID로 1건을 돌려준다. 상태, 금액, 예약 일수, 지급 키를 담는다.")
def get_payment_order(payment_order_id: str):
    with db() as conn:
        return one(conn, ORDER + " WHERE payment_order_id = %s", (payment_order_id,), f"지급 지시 {payment_order_id}")


@app.get("/payment-orders", operation_id="listPaymentOrders", summary="지급 지시 목록", dependencies=AUTH,
         description="청구, 상태, 계약, 보장으로 지급 지시를 찾는다. 같은 계약·보장의 기존 예약·지급(한도 내역)을 볼 때 쓴다.")
def list_payment_orders(claim_id: str | None = Query(None), status: str | None = Query(None, description="RESERVED, "
                        "REQUESTED, PAID, FAILED, UNKNOWN"), policy_id: str | None = Query(None),
                        coverage_id: str | None = Query(None), limit: int = LIMIT):
    w, p = where({"claim_id": claim_id, "status": status, "policy_id": policy_id, "coverage_id": coverage_id})
    with db() as conn:
        return rows(conn, ORDER + w + " ORDER BY decided_at, payment_order_id LIMIT %s", (*p, limit))


@app.get("/action-logs", operation_id="listActionLogs", summary="실행 이력", dependencies=AUTH,
         description="업무 실행 이력을 최신순으로 돌려준다. target_id 를 주면 그 대상(예: CL-001)이 들어간 이력만. 거절도 남는다.")
def list_action_logs(target_id: str | None = Query(None, description="대상 ID"),
                     action_type: str | None = Query(None, description="예: ApproveClaim"), limit: int = LIMIT):
    conds, params = [], []
    if target_id is not None:
        conds.append("target_refs @> %s::jsonb")
        params.append(json.dumps([{"id": target_id}]))
    if action_type is not None:
        conds.append("action_type = %s")
        params.append(action_type)
    w = (" WHERE " + " AND ".join(conds)) if conds else ""
    with db() as conn:
        return rows(conn, LOG + w + " ORDER BY executed_at DESC, log_id DESC LIMIT %s", (*params, limit))


# ═══ 쓰기 공통 ══════════════════════════════════════════════════════════════

def _ref(type_: str, id_: str | None) -> dict:
    return {"type": type_, "id": id_}


def log_action(conn, action_type: str, actor_id: str, targets: list[dict], key: str, outcome: str = "SUCCESS",
               reason: str | None = None, before: Any = None, after: Any = None) -> str:
    log_id = next_id(conn, "review.action_log_seq", "AL-", 5)
    conn.execute("INSERT INTO review.action_log (log_id, action_type, actor_id, target_refs, executed_at, idempotency_key, "
                 "before_hash, after_hash, outcome, reason) VALUES (%s, %s, %s, %s, now(), %s, %s, %s, %s, %s)",
                 (log_id, action_type, actor_id, Jsonb([t for t in targets if t["id"]]), key,
                  canonical_hash(before) if before is not None else None,
                  canonical_hash(after) if after is not None else None, outcome, reason))
    return log_id


def run_action(action_type: str, actor_id: str, key: str, payload: dict, targets: list[dict],
               fn: Callable[[Any], dict], replay: Callable[[Any, Any], dict] | None = None) -> dict:
    """멱등성 확인 → 업무 변경(fn) → 결과 저장을 한 트랜잭션으로. 거절이면 전체를 되돌리고 거절 이력만 남긴다."""
    try:
        with db_write() as conn:
            prev = idem_begin(conn, S, action_type, actor_id, key, payload)
            if prev is not None:
                return replay(conn, prev) if replay else prev
            return idem_finish(conn, S, action_type, actor_id, key, fn(conn))
    except DependencyError as exc:
        reject = Reject("DEPENDENCY_UNAVAILABLE", f"{exc.system} 시스템을 조회하지 못했습니다: {exc.detail}", 503)
    except Reject as exc:
        reject = exc
    with db_write() as conn:
        log_action(conn, action_type, actor_id, targets, key, "REJECTED", f"{reject.code}: {reject.message}")
    raise reject


def _claim(conn, claim_id: str) -> dict:
    return one(conn, CLAIM + " WHERE claim_id = %s FOR UPDATE", (claim_id,), f"청구 {claim_id}")


def _not_closed(claim: dict) -> None:
    if claim["status"] in CLOSED:
        raise Reject("CLAIM_CLOSED", f"청구 {claim['claim_id']} 는 {claim['status']} 상태입니다")


def _revision(row: dict, expected: int | None, what: str) -> None:
    if expected is not None and row["revision"] != expected:
        raise Reject("REVISION_CONFLICT", f"{what} revision 이 {row['revision']} 입니다 (요청 {expected})")


def _set_claim(conn, claim_id: str, **fields) -> None:
    sets = ", ".join(f"{k} = %s" for k in fields)
    conn.execute(f"UPDATE review.claim SET {sets}, revision = revision + 1, updated_at = now() WHERE claim_id = %s",
                 (*fields.values(), claim_id))


def _open_tasks(conn, claim_id: str) -> int:
    return conn.execute("SELECT count(*) AS n FROM review.review_task WHERE claim_id = %s AND status = 'OPEN'",
                        (claim_id,)).fetchone()["n"]


def _ensure_task(conn, claim: dict, task_type: str, reason_code: str, related_ref: str, note: str) -> str | None:
    """미해결 업무를 만든다. 같은 (청구, 유형, 사유, 관련 ID)의 미해결 업무가 있으면 만들지 않는다 (명세 5.4절)."""
    task_id = next_id(conn, "review.task_seq", "TK-", 3)
    row = conn.execute("INSERT INTO review.review_task (task_id, claim_id, task_type, reason_code, related_ref, status, "
                       "assignee_id, reason_note) VALUES (%s, %s, %s, %s, %s, 'OPEN', %s, %s) "
                       "ON CONFLICT (claim_id, task_type, reason_code, related_ref) WHERE status = 'OPEN' DO NOTHING "
                       "RETURNING task_id",
                       (task_id, claim["claim_id"], task_type, reason_code, related_ref, claim["assigned_reviewer_id"],
                        note)).fetchone()
    return row["task_id"] if row else None


def _on_date(roles: list[dict], role_type: str, day: dt.date | None) -> list[dict]:
    return [r for r in roles if r["role_type"] == role_type
            and (day is None or dt.date.fromisoformat(r["valid_from"]) <= day < dt.date.fromisoformat(r["valid_to"]))]


def _custs_of_claimant(claimant_no: str) -> tuple[str | None, list[str]]:
    """접수 청구인 → (identity_token, 계약 시스템 고객번호 목록). 동일인 판정은 토큰으로 한다."""
    claimant = get_or_none("intake", f"/claimants/{claimant_no}")
    if not claimant:
        return None, []
    _, custs = call("contract", "GET", "/customers", params={"identity_token": claimant["identity_token"]})
    return claimant["identity_token"], sorted(c["cust_no"] for c in custs)


# ═══ 평가 입력 스냅샷 (서버_설계서.md 7.4절) ═════════════════════════════════

def build_snapshot(conn, claim: dict) -> tuple[dict | None, list[str]]:
    """평가에 쓰는 모든 입력을 모은다. → (스냅샷, 보류 사유 목록). 다른 시스템 연결 실패는 DependencyError."""
    errors: list[str] = []
    policy = get_or_none("contract", f"/policies/{claim['policy_id']}")
    if policy is None:
        return None, [f"계약 {claim['policy_id']} 를 찾지 못했습니다"]
    coverage = next((c for c in policy["coverages"] if c["coverage_id"] == claim["coverage_id"]), None)
    if coverage is None:
        return None, [f"보장 {claim['coverage_id']} 가 계약 {claim['policy_id']} 에 없습니다"]
    rule = conn.execute(RULE + " WHERE rule_code = %s AND version = %s", (coverage["rule_code"], coverage["rule_version"])).fetchone()
    if rule is None:
        return None, [f"규칙 {coverage['rule_code']}/{coverage['rule_version']} 를 찾지 못했습니다"]
    if rule["logic_hash"] and rule["logic_hash"] != LOGIC_HASH:
        errors.append(f"평가 로직 해시가 규칙 {rule['rule_set_id']} 와 다릅니다")
    receipt = get_or_none("intake", f"/receipts/{claim['receipt_no']}")
    if receipt is None:
        return None, [f"접수 {claim['receipt_no']} 를 찾지 못했습니다"]
    event = one(conn, EVENT + " WHERE event_id = %s", (claim["event_id"],), f"사건 {claim['event_id']}")
    token, custs = _custs_of_claimant(event["subject_claimant_no"])

    active = sorted((d for d in receipt["documents"] if d["detached_at"] is None), key=lambda d: d["doc_id"])
    ver = {v["doc_id"]: v for v in rows(conn, VERIFICATION + " WHERE doc_id = ANY(%s)", ([d["doc_id"] for d in active],))}
    documents = [{"doc_id": d["doc_id"], "document_type": d["document_type"], "content_hash": d["content_hash"],
                  "attachment_id": d["attachment_id"],
                  "verification_status": ver.get(d["doc_id"], {}).get("verification_status", "PENDING"),
                  "verified_facts": ver.get(d["doc_id"], {}).get("verified_facts"),
                  "supports_event_id": ver.get(d["doc_id"], {}).get("supports_event_id"),
                  "revision": ver.get(d["doc_id"], {}).get("revision")} for d in active]

    duplicates = rows(conn, "SELECT c.claim_id, c.status, po.payment_order_id, po.status AS payment_order_status "
                            "FROM review.claim c LEFT JOIN review.payment_order po USING (claim_id) "
                            "WHERE c.event_id = %s AND c.coverage_id = %s AND c.claim_id <> %s ORDER BY c.claim_id",
                      (claim["event_id"], claim["coverage_id"], claim["claim_id"]))

    adm = event["admission_date"]
    insured = _on_date(policy["roles"], "INSURED", adm) or _on_date(policy["roles"], "INSURED", None)
    insured_cust = insured[0]["cust_no"] if insured else None
    orders = rows(conn, "SELECT payment_order_id, claim_id, status, reserved_days FROM review.payment_order "
                        "WHERE policy_id = %s AND coverage_id = %s AND insured_cust_no = %s AND benefit_period_key = %s "
                        "AND claim_id <> %s ORDER BY payment_order_id",
                  (claim["policy_id"], claim["coverage_id"], insured_cust, coverage["benefit_period_key"],
                   claim["claim_id"])) if insured_cust else []

    snapshot = plain({
        "claim": {k: claim[k] for k in ("claim_id", "receipt_no", "policy_id", "coverage_id", "event_id",
                                        "submitted_by_claimant_no", "revision")},
        "policy": {k: policy[k] for k in ("policy_id", "policy_number", "contract_from", "contract_to", "revision")},
        "coverage": {k: coverage[k] for k in ("coverage_id", "policy_id", "coverage_code", "version", "valid_from",
                                              "valid_to", "daily_amount_krw", "max_days", "waiting_days", "rule_code",
                                              "rule_version", "benefit_period_key", "revision")},
        "rule_set": {k: rule[k] for k in ("rule_set_id", "rule_code", "version", "clause_reference", "definition_hash",
                                          "logic_hash", "required_document_types")},
        "roles": sorted(({k: r[k] for k in ("role_id", "cust_no", "role_type", "valid_from", "valid_to", "revision")}
                         for r in policy["roles"]), key=lambda r: r["role_id"]),
        "event": {k: event[k] for k in ("event_id", "subject_claimant_no", "provider_code", "admission_date",
                                        "discharge_date", "fact_status", "revision")},
        "subject": {"claimant_no": event["subject_claimant_no"], "identity_token": token, "cust_nos": custs},
        "documents": documents,
        "duplicates": duplicates,
        "limit": {"insured_cust_no": insured_cust, "orders": orders},
    })
    return snapshot, errors


# ═══ 쓰기 API ═══════════════════════════════════════════════════════════════

class Actor(BaseModel):
    actor_id: str = Field(..., description="실행자 ID (예: reviewer-01). 권한 검사에 쓴다")


class RegisterClaimIn(Actor):
    receipt_no: str = Field(..., description="접수 시스템의 접수 번호 (createReceipt 응답의 receipt_no)")
    assigned_reviewer_id: str = Field("reviewer-01", description="담당 심사자")
    coverage_id: str | None = Field(None, description="보장 ID를 직접 지정할 때 (선택). 접수 계약의 보장이어야 한다")


class EvidenceAttachedIn(Actor):
    doc_id: str = Field(..., description="접수에 연결한 서류 ID")
    replaced_doc_id: str | None = Field(None, description="교체로 해제한 서류 ID (선택)")
    expected_revision: int | None = Field(None, description="청구 revision (선택)")


class VerifiedFacts(BaseModel):
    insured: str = Field(..., description="입원한 사람 (접수 시스템 청구인 번호, 예: IP-0002)")
    provider_code: str = Field(..., description="의료기관 코드")
    admission_date: dt.date = Field(..., description="입원일")
    discharge_date: dt.date = Field(..., description="퇴원일")


class VerifyIn(Actor):
    verification_status: str = Field(..., description="VERIFIED 또는 REJECTED")
    verified_facts: VerifiedFacts | None = Field(None, description="확인값. VERIFIED 면 필수")
    supports_event_id: str | None = Field(None, description="이 서류가 뒷받침하는 사건 ID (없으면 기존 값 또는 관련 청구의 사건)")
    note: str = Field(..., description="확인 근거")
    expected_revision: int | None = Field(None, description="확인 기록 revision (선택)")


class EvaluateIn(Actor):
    expected_revision: int | None = Field(None, description="청구 revision (선택)")


class EvidenceRequestIn(Actor):
    missing_items: list[str] = Field(..., min_length=1, description="누락 항목 (예: HOSPITALIZATION_CERTIFICATE)")
    message: str = Field(..., description="요청 문구 (PoC에서는 저장만 하고 보내지 않는다)")


class ResolveIn(Actor):
    resolution: str = Field(..., description="해결 근거")
    corrected_event_id: str | None = Field(None, description="청구를 다시 연결할 확인된 사건 ID (선택)")
    fact_refs: list[str] = Field(default_factory=list, description="수정된 사실 참조 (선택)")


class DecisionIn(Actor):
    assessment_id: str = Field(..., description="결정 근거 평가 ID (청구의 현재 평가)")
    reason: str = Field(..., description="결정 사유")
    expected_revision: int | None = Field(None, description="청구 revision (선택)")


class PaymentResultIn(BaseModel):
    payment_key: str = Field(..., description="지급 키")
    external_transaction_id: str | None = Field(None, description="지급 시스템 거래 ID")
    result: str = Field(..., description="PAID, FAILED, UNKNOWN")


# ── A01 2단계: 청구 등록 ──────────────────────────────────────────────────────

@app.post("/claims", operation_id="registerClaim", summary="청구 등록 (A01 2단계)", dependencies=AUTH,
          description="접수 시스템의 접수 원본으로 심사 청구(CL-…)를 RECEIVED 로 만든다. 계약 번호·보장 코드로 계약 시스템의 계약·보장을 "
                      "찾고, 보장이 그 계약의 것인지, 제출자가 계약자 또는 피보험자인지 확인한다. 같은 사고번호의 사건이 없으면 미확인 사건을 만든다.")
def register_claim(body: RegisterClaimIn, idem: str = IdemKey):
    def run(conn):
        if conn.execute("SELECT 1 FROM review.claim WHERE receipt_no = %s", (body.receipt_no,)).fetchone():
            raise Reject("ALREADY_REGISTERED", f"접수 {body.receipt_no} 로 이미 청구가 있습니다")
        receipt = get_or_none("intake", f"/receipts/{body.receipt_no}")
        if receipt is None:
            raise Reject("REFERENCE_NOT_FOUND", f"접수 {body.receipt_no} 가 없습니다", 404)
        if receipt["cancelled_at"]:
            raise Reject("RECEIPT_CANCELLED", f"접수 {body.receipt_no} 는 취소됐습니다")
        _, policies = call("contract", "GET", "/policies", params={"policy_number": receipt["policy_number"]})
        if len(policies) != 1:
            raise Reject("REFERENCE_NOT_FOUND", f"계약 번호 {receipt['policy_number']} 의 계약을 찾지 못했습니다")
        policy = get_or_none("contract", f"/policies/{policies[0]['policy_id']}")
        received_day = dt.datetime.fromisoformat(receipt["received_at"]).astimezone(SEOUL).date()
        if body.coverage_id:
            coverage = get_or_none("contract", f"/coverages/{body.coverage_id}")
            if coverage is None:
                raise Reject("REFERENCE_NOT_FOUND", f"보장 {body.coverage_id} 가 없습니다")
        else:
            cands = [c for c in policy["coverages"] if c["coverage_code"] == receipt["coverage_code"]]
            day = dt.date.fromisoformat(receipt["admission_date"]) if receipt["admission_date"] else received_day
            dated = [c for c in cands if dt.date.fromisoformat(c["valid_from"]) <= day < dt.date.fromisoformat(c["valid_to"])]
            coverage = (dated or cands or [None])[0]
            if coverage is None:
                raise Reject("REFERENCE_NOT_FOUND", f"계약 {policy['policy_id']} 에 보장 코드 {receipt['coverage_code']} 가 없습니다")
        if coverage["policy_id"] != policy["policy_id"]:
            raise Reject("REFERENCE_MISMATCH", f"보장 {coverage['coverage_id']} 는 계약 {coverage['policy_id']} 의 것입니다 "
                                               f"(청구 계약 {policy['policy_id']})")
        _, submitter_custs = _custs_of_claimant(receipt["submitter_no"])
        allowed = [r for r in _on_date(policy["roles"], "POLICYHOLDER", received_day) + _on_date(policy["roles"], "INSURED", received_day)
                   if r["cust_no"] in submitter_custs]
        if not allowed:
            raise Reject("SUBMITTER_NOT_ALLOWED", f"제출자 {receipt['submitter_no']} 는 접수일에 계약 {policy['policy_id']} 의 "
                                                  "계약자·피보험자가 아닙니다")
        event = conn.execute("SELECT event_id FROM review.insurance_event WHERE intake_accident_no = %s AND subject_claimant_no = %s "
                             "ORDER BY event_id LIMIT 1", (receipt["accident_no"], receipt["patient_no"])).fetchone()
        if event:
            event_id = event["event_id"]
        else:
            event_id = next_id(conn, "review.event_seq", "EV-", 3)
            conn.execute("INSERT INTO review.insurance_event (event_id, intake_accident_no, subject_claimant_no, fact_status) "
                         "VALUES (%s, %s, %s, 'UNVERIFIED')", (event_id, receipt["accident_no"], receipt["patient_no"]))
        claim_id = next_id(conn, "review.claim_seq", "CL-", 3)
        conn.execute("INSERT INTO review.claim (claim_id, receipt_no, policy_id, coverage_id, event_id, submitted_by_claimant_no, "
                     "submitted_at, status, assigned_reviewer_id) VALUES (%s, %s, %s, %s, %s, %s, %s, 'RECEIVED', %s)",
                     (claim_id, body.receipt_no, policy["policy_id"], coverage["coverage_id"], event_id,
                      receipt["submitter_no"], receipt["received_at"], body.assigned_reviewer_id))
        claim = _claim_view(conn, claim_id)
        log_action(conn, "SubmitClaim", body.actor_id, [_ref("Claim", claim_id), _ref("InsuranceEvent", event_id)], idem,
                   reason=f"접수 {body.receipt_no} → 청구 {claim_id}", after=claim)
        return {**claim, "event_created": event is None}
    return run_action("SubmitClaim", body.actor_id, idem, body.model_dump(), [_ref("Receipt", body.receipt_no)], run)


# ── A02 2단계: 증빙 연결 반영 ─────────────────────────────────────────────────

@app.post("/claims/{claim_id}/evidence-attached", operation_id="recordEvidenceAttached", summary="증빙 연결 반영 (A02 2단계)",
          dependencies=AUTH,
          description="접수 시스템에서 서류를 연결·교체한 뒤 심사 청구에 반영한다. 서류 확인 기록이 없으면 PENDING 으로 만들고, "
                      "평가가 있거나 보완 대기(NEED_INFO)면 청구를 UNDER_REVIEW 로 바꾼다. 종결된 청구는 거절.")
def record_evidence_attached(claim_id: str, body: EvidenceAttachedIn, idem: str = IdemKey):
    def run(conn):
        claim = _claim(conn, claim_id)
        _not_closed(claim)
        _revision(claim, body.expected_revision, f"청구 {claim_id}")
        receipt = get_or_none("intake", f"/receipts/{claim['receipt_no']}")
        if not receipt or not any(d["doc_id"] == body.doc_id and d["detached_at"] is None for d in receipt["documents"]):
            raise Reject("NOT_ATTACHED", f"서류 {body.doc_id} 가 접수 {claim['receipt_no']} 에 연결돼 있지 않습니다")
        conn.execute("INSERT INTO review.document_verification (doc_id, verification_status) VALUES (%s, 'PENDING') "
                     "ON CONFLICT (doc_id) DO NOTHING", (body.doc_id,))
        status = "UNDER_REVIEW" if claim["current_assessment_id"] or claim["status"] == "NEED_INFO" else claim["status"]
        _set_claim(conn, claim_id, status=status)
        after = _claim_view(conn, claim_id)
        log_action(conn, "AttachEvidence", body.actor_id, [_ref("Claim", claim_id), _ref("EvidenceDocument", body.doc_id),
                                                           _ref("EvidenceDocument", body.replaced_doc_id)],
                   idem, reason=f"서류 {body.doc_id} 연결" + (f" ({body.replaced_doc_id} 교체)" if body.replaced_doc_id else ""),
                   before=claim, after=after)
        return after
    return run_action("AttachEvidence", body.actor_id, idem, {"claim_id": claim_id, **body.model_dump()},
                      [_ref("Claim", claim_id)], run)


# ── A03 증빙 확인 ────────────────────────────────────────────────────────────

@app.post("/documents/{doc_id}/verify", operation_id="verifyEvidence", summary="증빙 확인 (A03)", dependencies=AUTH,
          description="서류의 확인값(사람·의료기관·입원일·퇴원일)을 저장한다. 사건이 미확인이면 확인값으로 사실을 채워 VERIFIED, "
                      "이미 확인된 사실과 다르면 CONFLICT 로 둔다. 관련 청구의 평가는 재평가 대상(UNDER_REVIEW)이 된다. "
                      "승인된 청구의 근거로 쓰인 서류는 덮어쓸 수 없다.")
def verify_evidence(doc_id: str, body: VerifyIn, idem: str = IdemKey):
    if body.verification_status not in ("VERIFIED", "REJECTED"):
        raise Reject("INVALID_INPUT", "verification_status 는 VERIFIED 또는 REJECTED", 422)
    if body.verification_status == "VERIFIED" and body.verified_facts is None:
        raise Reject("INVALID_INPUT", "VERIFIED 에는 verified_facts 가 필요합니다", 422)

    def run(conn):
        if get_or_none("intake", f"/documents/{doc_id}") is None:
            raise Reject("REFERENCE_NOT_FOUND", f"서류 {doc_id} 가 없습니다", 404)
        locked = conn.execute("SELECT ae.assessment_id FROM review.assessment_evidence ae JOIN review.payment_order po "
                              "USING (assessment_id) WHERE ae.doc_id = %s LIMIT 1", (doc_id,)).fetchone()
        if locked:
            raise Reject("EVIDENCE_LOCKED", f"서류 {doc_id} 는 승인된 평가 {locked['assessment_id']} 의 근거입니다. "
                                            "정정 문서를 새로 만들어야 합니다")
        links = get_or_none("intake", f"/documents/{doc_id}/receipts") or []
        receipts = sorted({link["receipt_no"] for link in links if link["detached_at"] is None})
        related = rows(conn, "SELECT claim_id, status, event_id, current_assessment_id FROM review.claim WHERE receipt_no = ANY(%s) "
                             "OR claim_id IN (SELECT a.claim_id FROM review.assessment a JOIN review.assessment_evidence ae "
                             "USING (assessment_id) WHERE ae.doc_id = %s) ORDER BY claim_id FOR UPDATE", (receipts, doc_id))
        closed = [c["claim_id"] for c in related if c["status"] in ("APPROVED", "PAID")]
        if closed:
            raise Reject("CLAIM_CLOSED", f"관련 청구 {', '.join(closed)} 가 이미 승인됐습니다")
        before = conn.execute(VERIFICATION + " WHERE doc_id = %s FOR UPDATE", (doc_id,)).fetchone()
        if before:
            _revision(before, body.expected_revision, f"서류 {doc_id} 확인 기록")
        event_id = body.supports_event_id or (before and before["supports_event_id"]) or \
            (related[0]["event_id"] if len({c["event_id"] for c in related}) == 1 else None)
        facts = plain(body.verified_facts.model_dump()) if body.verified_facts else None
        conn.execute("INSERT INTO review.document_verification (doc_id, supports_event_id, verification_status, verified_facts, "
                     "verified_by, verified_at, verification_note) VALUES (%s, %s, %s, %s, %s, now(), %s) "
                     "ON CONFLICT (doc_id) DO UPDATE SET supports_event_id = EXCLUDED.supports_event_id, "
                     "verification_status = EXCLUDED.verification_status, verified_facts = EXCLUDED.verified_facts, "
                     "verified_by = EXCLUDED.verified_by, verified_at = EXCLUDED.verified_at, "
                     "verification_note = EXCLUDED.verification_note, revision = review.document_verification.revision + 1, "
                     "updated_at = now()",
                     (doc_id, event_id, body.verification_status, Jsonb(facts) if facts else None, body.actor_id, body.note))
        event_change = None
        if event_id and facts:
            ev = one(conn, EVENT + " WHERE event_id = %s FOR UPDATE", (event_id,), f"사건 {event_id}")
            same = (ev["subject_claimant_no"] == facts["insured"] and ev["provider_code"] == facts["provider_code"]
                    and plain(ev["admission_date"]) == facts["admission_date"]
                    and plain(ev["discharge_date"]) == facts["discharge_date"])
            if ev["fact_status"] == "UNVERIFIED" and ev["subject_claimant_no"] == facts["insured"]:
                conn.execute("UPDATE review.insurance_event SET provider_code = %s, admission_date = %s, discharge_date = %s, "
                             "fact_status = 'VERIFIED', revision = revision + 1, updated_at = now() WHERE event_id = %s",
                             (facts["provider_code"], facts["admission_date"], facts["discharge_date"], event_id))
                event_change = "VERIFIED"
            elif not same and ev["fact_status"] != "CONFLICT":
                conn.execute("UPDATE review.insurance_event SET fact_status = 'CONFLICT', revision = revision + 1, "
                             "updated_at = now() WHERE event_id = %s", (event_id,))
                event_change = "CONFLICT"
        reopened = []
        for c in related:
            if c["status"] not in CLOSED and c["current_assessment_id"]:
                _set_claim(conn, c["claim_id"], status="UNDER_REVIEW")
                reopened.append(c["claim_id"])
        after = one(conn, VERIFICATION + " WHERE doc_id = %s", (doc_id,), doc_id)
        log_action(conn, "VerifyEvidence", body.actor_id,
                   [_ref("EvidenceDocument", doc_id), _ref("InsuranceEvent", event_id)] + [_ref("Claim", c) for c in reopened],
                   idem, reason=body.note + (f" / 사건 {event_id} → {event_change}" if event_change else ""),
                   before=before, after=after)
        return {**after, "event_id": event_id, "event_change": event_change, "claims_to_reevaluate": reopened}
    return run_action("VerifyEvidence", body.actor_id, idem, {"doc_id": doc_id, **body.model_dump()},
                      [_ref("EvidenceDocument", doc_id)], run)


# ── A04 평가 ─────────────────────────────────────────────────────────────────

@app.post("/claims/{claim_id}/evaluate", operation_id="evaluateClaim", summary="청구 평가 (A04)", dependencies=AUTH,
          description="계약·접수·심사 데이터로 규칙 R01–R07을 계산해 새 평가(AS-…)를 만든다. 지급 후보 금액, 사유, 필요한 심사 업무를 "
                      "남기고 청구 상태를 바꾼다(READY_FOR_DECISION / NEED_INFO / UNDER_REVIEW). 규칙이나 다른 시스템을 조회하지 못하면 "
                      "평가를 보류(result=HELD)하고 데이터 보정 업무를 만든다. 종결된 청구는 거절.")
def evaluate_claim(claim_id: str, body: EvaluateIn, idem: str = IdemKey):
    def run(conn):
        claim = _claim(conn, claim_id)
        _not_closed(claim)
        _revision(claim, body.expected_revision, f"청구 {claim_id}")
        try:
            snapshot, errors = build_snapshot(conn, claim)
        except DependencyError as exc:
            snapshot, errors = None, [f"{exc.system} 시스템 조회 실패: {exc.detail}"]
        if errors:
            task = _ensure_task(conn, claim, "DATA_REPAIR", "DEPENDENCY_UNAVAILABLE", "EVALUATION", "; ".join(errors))
            _set_claim(conn, claim_id, status="UNDER_REVIEW")
            log_action(conn, "EvaluateClaim", body.actor_id, [_ref("Claim", claim_id), _ref("ReviewTask", task)], idem,
                       reason="평가 보류: " + "; ".join(errors), before=claim)
            return {"result": "HELD", "reason_code": "DEPENDENCY_UNAVAILABLE", "errors": errors, "task_created": task,
                    **_claim_view(conn, claim_id)}
        res = evaluation.evaluate(snapshot)
        assessment_id = next_id(conn, "review.assessment_seq", "AS-", 3)
        conn.execute("INSERT INTO review.assessment (assessment_id, claim_id, rule_set_id, evaluated_at, input_snapshot, input_hash, "
                     "rule_results, recommendation, eligible_days, candidate_amount_krw, reason_codes) "
                     "VALUES (%s, %s, %s, now(), %s, %s, %s, %s, %s, %s, %s)",
                     (assessment_id, claim_id, snapshot["rule_set"]["rule_set_id"],
                      Jsonb({"snapshot": snapshot, "engine_logic_hash": LOGIC_HASH, "figures": res["figures"]}),
                      evaluation.input_hash(snapshot), Jsonb(res["rule_results"]), res["recommendation"],
                      res["eligible_days"], res["candidate_amount_krw"], res["reason_codes"]))
        for d in snapshot["documents"]:
            conn.execute("INSERT INTO review.assessment_evidence (assessment_id, doc_id, content_hash) VALUES (%s, %s, %s)",
                         (assessment_id, d["doc_id"], d["content_hash"]))
        created = [t for t in (_ensure_task(conn, claim, t["task_type"], t["reason_code"], t["related_ref"], t["reason_note"])
                               for t in res["tasks"]) if t]
        open_n = _open_tasks(conn, claim_id)
        rec = res["recommendation"]
        status = ("READY_FOR_DECISION" if rec in ("PAYABLE_CANDIDATE", "NOT_PAYABLE_CANDIDATE") and open_n == 0
                  else "NEED_INFO" if rec == "NEED_INFO" else "UNDER_REVIEW")
        _set_claim(conn, claim_id, current_assessment_id=assessment_id, status=status)
        after = _claim_view(conn, claim_id)
        log_action(conn, "EvaluateClaim", body.actor_id,
                   [_ref("Claim", claim_id), _ref("Assessment", assessment_id)] + [_ref("ReviewTask", t) for t in created], idem,
                   reason=f"{rec} {res['candidate_amount_krw']}원 {','.join(res['reason_codes'])}".strip(),
                   before=claim, after=after)
        return {"result": "EVALUATED", "assessment_id": assessment_id, "recommendation": rec,
                "eligible_days": res["eligible_days"], "candidate_amount_krw": res["candidate_amount_krw"],
                "reason_codes": res["reason_codes"], "figures": res["figures"], "tasks_created": created, **after}
    return run_action("EvaluateClaim", body.actor_id, idem, {"claim_id": claim_id, **body.model_dump()},
                      [_ref("Claim", claim_id)], run)


# ── A05 보완 요청 ────────────────────────────────────────────────────────────

@app.post("/claims/{claim_id}/evidence-requests", operation_id="requestEvidence", summary="증빙 보완 요청 (A05)",
          dependencies=AUTH,
          description="누락 항목마다 증빙 보완 업무(EVIDENCE_REQUEST)를 만들고 청구를 NEED_INFO 로 바꾼다. 요청 문구는 저장만 하고 "
                      "고객에게 보내지 않는다. 같은 항목의 미해결 업무가 있으면 새로 만들지 않는다.")
def request_evidence(claim_id: str, body: EvidenceRequestIn, idem: str = IdemKey):
    def run(conn):
        claim = _claim(conn, claim_id)
        _not_closed(claim)
        created = [t for t in (_ensure_task(conn, claim, "EVIDENCE_REQUEST", "MISSING_DOCUMENT", item, body.message)
                               for item in body.missing_items) if t]
        _set_claim(conn, claim_id, status="NEED_INFO")
        after = _claim_view(conn, claim_id)
        log_action(conn, "RequestEvidence", body.actor_id, [_ref("Claim", claim_id)] + [_ref("ReviewTask", t) for t in created],
                   idem, reason=f"보완 요청: {', '.join(body.missing_items)}", before=claim, after=after)
        return {**after, "tasks_created": created}
    return run_action("RequestEvidence", body.actor_id, idem, {"claim_id": claim_id, **body.model_dump()},
                      [_ref("Claim", claim_id)], run)


# ── A06 업무 해결 ────────────────────────────────────────────────────────────

@app.post("/tasks/{task_id}/resolve", operation_id="resolveReviewTask", summary="심사 업무 해결 (A06)", dependencies=AUTH,
          description="미해결 심사 업무를 해결 근거와 함께 RESOLVED 로 닫는다. corrected_event_id 를 주면 청구를 그 확인된 사건으로 "
                      "다시 연결한다. 청구는 UNDER_REVIEW 가 되고, 재평가(evaluateClaim)는 따로 해야 한다.")
def resolve_review_task(task_id: str, body: ResolveIn, idem: str = IdemKey):
    def run(conn):
        task = one(conn, TASK + " WHERE task_id = %s FOR UPDATE", (task_id,), f"업무 {task_id}")
        claim = _claim(conn, task["claim_id"])
        if task["status"] != "OPEN":
            raise Reject("INVALID_STATE", f"업무 {task_id} 는 이미 {task['status']} 입니다")
        _not_closed(claim)
        if body.actor_id not in (task["assignee_id"], claim["assigned_reviewer_id"]):
            raise Reject("NOT_ASSIGNED_REVIEWER", f"{body.actor_id} 는 업무 {task_id} 의 담당자가 아닙니다")
        if not body.resolution.strip():
            raise Reject("INVALID_INPUT", "해결 근거가 필요합니다", 422)
        fields: dict[str, Any] = {"status": "UNDER_REVIEW"}
        if body.corrected_event_id:
            ev = one(conn, EVENT + " WHERE event_id = %s", (body.corrected_event_id,), f"사건 {body.corrected_event_id}")
            if ev["fact_status"] != "VERIFIED":
                raise Reject("EVENT_NOT_VERIFIED", f"사건 {body.corrected_event_id} 는 {ev['fact_status']} 입니다")
            fields["event_id"] = body.corrected_event_id
        conn.execute("UPDATE review.review_task SET status = 'RESOLVED', resolution = %s, resolved_by = %s, resolved_at = now(), "
                     "revision = revision + 1, updated_at = now() WHERE task_id = %s",
                     (body.resolution + (f" [사실 참조: {', '.join(body.fact_refs)}]" if body.fact_refs else ""),
                      body.actor_id, task_id))
        _set_claim(conn, claim["claim_id"], **fields)
        after = _claim_view(conn, claim["claim_id"])
        log_action(conn, "ResolveReviewTask", body.actor_id,
                   [_ref("ReviewTask", task_id), _ref("Claim", claim["claim_id"]), _ref("InsuranceEvent", body.corrected_event_id)],
                   idem, reason=body.resolution, before=task, after=after)
        return {**after, "task": one(conn, TASK + " WHERE task_id = %s", (task_id,), task_id)}
    return run_action("ResolveReviewTask", body.actor_id, idem, {"task_id": task_id, **body.model_dump()},
                      [_ref("ReviewTask", task_id)], run)


# ── A07 승인 / A08 부지급 (명세 8.2절, 서버_설계서.md 7.5절) ─────────────────────

def _decision_checks(conn, claim: dict, body: DecisionIn, want: str) -> dict:
    if claim["status"] != "READY_FOR_DECISION":
        raise Reject("INVALID_STATE", f"청구 {claim['claim_id']} 는 {claim['status']} 상태입니다 (READY_FOR_DECISION 필요)")
    if body.actor_id != claim["assigned_reviewer_id"]:
        raise Reject("NOT_ASSIGNED_REVIEWER", f"{body.actor_id} 는 청구 {claim['claim_id']} 의 담당 심사자가 아닙니다")
    _revision(claim, body.expected_revision, f"청구 {claim['claim_id']}")
    if body.assessment_id != claim["current_assessment_id"]:
        raise Reject("STALE_ASSESSMENT", f"평가 {body.assessment_id} 는 현재 평가({claim['current_assessment_id']})가 아닙니다")
    a = one(conn, ASSESSMENT + " WHERE assessment_id = %s", (body.assessment_id,), f"평가 {body.assessment_id}")
    if a["recommendation"] != want:
        raise Reject("NOT_PAYABLE" if want == "PAYABLE_CANDIDATE" else "NOT_REJECTABLE",
                     f"평가 {a['assessment_id']} 는 {a['recommendation']} 입니다 ({want} 필요)")
    if _open_tasks(conn, claim["claim_id"]):
        raise Reject("OPEN_TASKS", f"청구 {claim['claim_id']} 에 미해결 업무가 있습니다")
    return a


def _fresh_snapshot(conn, claim: dict, a: dict) -> dict:
    """잠금을 잡은 뒤 입력을 다시 모아, 평가 당시와 같은지 확인한다 (명세 8.2절 6–7)."""
    snapshot, errors = build_snapshot(conn, claim)
    if errors:
        raise Reject("DEPENDENCY_UNAVAILABLE", "; ".join(errors), 503)
    if evaluation.input_hash(snapshot) != a["input_hash"]:
        raise Reject("STALE_ASSESSMENT", f"평가 {a['assessment_id']} 이후 관련 입력이 바뀌었습니다. 다시 평가하세요")
    return snapshot


@app.post("/claims/{claim_id}/approve", operation_id="approveClaim", summary="지급 승인 (A07)", dependencies=AUTH,
          description="담당 심사자가 지급 후보 평가를 승인한다. 최신 평가·미해결 업무 0건·수익자를 확인하고, 같은 한도·같은 사건의 동시 승인을 "
                      "막은 채 한도와 중복을 다시 검사한 뒤, 지급 지시(RESERVED, 한도 예약)와 청구 APPROVED 를 한 번에 기록한다. "
                      "평가 이후 입력이 바뀌었으면 STALE_ASSESSMENT 로 거절.")
def approve_claim(claim_id: str, body: DecisionIn, idem: str = IdemKey):
    def run(conn):
        claim = _claim(conn, claim_id)
        a = _decision_checks(conn, claim, body, "PAYABLE_CANDIDATE")
        old = a["input_snapshot"]["snapshot"]
        keys = sorted([f"limit:{claim['policy_id']}:{claim['coverage_id']}:{old['limit']['insured_cust_no']}:"
                       f"{old['coverage']['benefit_period_key']}", f"event:{claim['event_id']}:{claim['coverage_id']}"])
        for k in keys:   # 같은 한도 키·같은 사건을 건드리는 승인을 한 번에 하나만 (항상 같은 순서로 잡는다)
            conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (k,))
        snapshot = _fresh_snapshot(conn, claim, a)
        res = evaluation.evaluate(snapshot)
        if res["recommendation"] != "PAYABLE_CANDIDATE" or res["eligible_days"] != a["eligible_days"]:
            raise Reject("STALE_ASSESSMENT", "다시 계산한 결과가 평가와 다릅니다")
        insured = snapshot["limit"]["insured_cust_no"]
        adm = dt.date.fromisoformat(snapshot["event"]["admission_date"])
        beneficiaries = [r["cust_no"] for r in _on_date(snapshot["roles"], "BENEFICIARY", adm)]
        if insured not in beneficiaries:   # 이번 상품의 수익자는 피보험자로 고정 (명세 2.1절)
            raise Reject("BENEFICIARY_MISMATCH", f"수익자 {beneficiaries} 가 피보험자 {insured} 와 다릅니다")
        if res["figures"]["remaining_days"] < a["eligible_days"]:
            raise Reject("LIMIT_EXHAUSTED", "잔여 한도가 인정 일수보다 적습니다")
        po_id = next_id(conn, "review.payment_order_seq", "PY-", 3)
        conn.execute("INSERT INTO review.payment_order (payment_order_id, claim_id, assessment_id, beneficiary_cust_no, "
                     "insured_cust_no, policy_id, coverage_id, benefit_period_key, reserved_days, amount_krw, status, payment_key, "
                     "decided_by, decided_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'RESERVED', %s, %s, now())",
                     (po_id, claim_id, a["assessment_id"], insured, insured, claim["policy_id"], claim["coverage_id"],
                      snapshot["coverage"]["benefit_period_key"], a["eligible_days"], a["candidate_amount_krw"],
                      f"PK-{po_id}", body.actor_id))
        _set_claim(conn, claim_id, status="APPROVED")
        after = _claim_view(conn, claim_id)
        log_action(conn, "ApproveClaim", body.actor_id,
                   [_ref("Claim", claim_id), _ref("Assessment", a["assessment_id"]), _ref("PaymentOrder", po_id)], idem,
                   reason=body.reason, before=claim, after=after)
        return {**after, "payment_order": one(conn, ORDER + " WHERE payment_order_id = %s", (po_id,), po_id)}
    return run_action("ApproveClaim", body.actor_id, idem, {"claim_id": claim_id, **body.model_dump()},
                      [_ref("Claim", claim_id), _ref("Assessment", body.assessment_id)], run)


@app.post("/claims/{claim_id}/reject", operation_id="rejectClaim", summary="부지급 결정 (A08)", dependencies=AUTH,
          description="담당 심사자가 부지급 후보 평가로 부지급을 결정한다. 최신 평가·미해결 업무 0건을 확인하고 청구를 REJECTED 로 바꾼다. "
                      "결정 사유는 실행 이력에 남는다.")
def reject_claim(claim_id: str, body: DecisionIn, idem: str = IdemKey):
    def run(conn):
        claim = _claim(conn, claim_id)
        a = _decision_checks(conn, claim, body, "NOT_PAYABLE_CANDIDATE")
        _fresh_snapshot(conn, claim, a)
        _set_claim(conn, claim_id, status="REJECTED")
        after = _claim_view(conn, claim_id)
        log_action(conn, "RejectClaim", body.actor_id, [_ref("Claim", claim_id), _ref("Assessment", a["assessment_id"])], idem,
                   reason=body.reason, before=claim, after=after)
        return after
    return run_action("RejectClaim", body.actor_id, idem, {"claim_id": claim_id, **body.model_dump()},
                      [_ref("Claim", claim_id), _ref("Assessment", body.assessment_id)], run)


# ── 지급 결과 반영 (A10 공통 처리, 서버_설계서.md 7.6절) ─────────────────────────

def apply_result(conn, payment_key: str, tx_id: str | None, result: str, actor: str, key: str, reason: str) -> dict:
    po = one(conn, ORDER + " WHERE payment_key = %s FOR UPDATE", (payment_key,), f"지급 키 {payment_key}")
    cur = po["status"]
    if result not in ("PAID", "FAILED", "UNKNOWN"):
        raise Reject("INVALID_INPUT", "result 는 PAID, FAILED, UNKNOWN", 422)
    if cur == result and (result != "PAID" or po["external_transaction_id"] == tx_id):
        return {"result": "DUPLICATE", "payment_order": po, "status": _claim_status(conn, po["claim_id"])}
    if cur in ("PAID", "FAILED") or (cur == "UNKNOWN" and result == "UNKNOWN"):
        raise Reject("RESULT_CONFLICT", f"지급 지시 {po['payment_order_id']} 는 {cur} 입니다. {result} 결과는 덮어쓰지 않습니다 (조사 필요)")
    if cur not in ("REQUESTED", "UNKNOWN"):
        raise Reject("INVALID_STATE", f"지급 지시 {po['payment_order_id']} 는 {cur} 입니다")
    conn.execute("UPDATE review.payment_order SET status = %s, external_transaction_id = coalesce(%s, external_transaction_id), "
                 "revision = revision + 1, updated_at = now() WHERE payment_order_id = %s", (result, tx_id, po["payment_order_id"]))
    if result == "PAID":
        _set_claim(conn, po["claim_id"], status="PAID")
    after = one(conn, ORDER + " WHERE payment_order_id = %s", (po["payment_order_id"],), "")
    log_action(conn, "RecordPaymentResult", actor, [_ref("PaymentOrder", po["payment_order_id"]), _ref("Claim", po["claim_id"])],
               key, reason=f"{cur} → {result}" + (f" ({tx_id})" if tx_id else "") + (f" / {reason}" if reason else ""),
               before=po, after=after)
    return {"result": result, "payment_order": after, "status": _claim_status(conn, po["claim_id"])}


def _claim_status(conn, claim_id: str) -> str:
    return conn.execute("SELECT status FROM review.claim WHERE claim_id = %s", (claim_id,)).fetchone()["status"]


def _order_view(conn, payment_order_id: str) -> dict:
    po = one(conn, ORDER + " WHERE payment_order_id = %s", (payment_order_id,), f"지급 지시 {payment_order_id}")
    po["outbox"] = rows(conn, "SELECT outbox_id, attempt, status, sent_at FROM review.payment_outbox WHERE payment_order_id = %s "
                              "ORDER BY attempt", (payment_order_id,))
    return {**po, "claim_status": _claim_status(conn, po["claim_id"])}


def deliver(outbox_id: str) -> None:
    """전송 대기 기록 하나를 지급 시스템에 보낸다 (명세 8.3절 전달기). 결과를 모르면 UNKNOWN 으로 둔다."""
    with db_write() as conn:
        ob = conn.execute("SELECT * FROM review.payment_outbox WHERE outbox_id = %s FOR UPDATE", (outbox_id,)).fetchone()
        if not ob or ob["status"] != "PENDING":
            return
        po = one(conn, ORDER + " WHERE payment_order_id = %s", (ob["payment_order_id"],), "")
        key = f"{ob['payment_key']}:a{ob['attempt']}"
        try:
            status, data = call("payment", "POST", "/payment-requests",
                                json_body={"payment_key": po["payment_key"], "amount_krw": po["amount_krw"],
                                           "beneficiary_token": f"VACCT-{po['beneficiary_cust_no']}",
                                           "payment_order_id": po["payment_order_id"]},
                                headers={"Idempotency-Key": key}, timeout=3)
        except DependencyError as exc:
            conn.execute("UPDATE review.payment_outbox SET status = 'UNKNOWN', sent_at = now(), response = %s WHERE outbox_id = %s",
                         (Jsonb({"error": exc.detail}), outbox_id))
            if po["status"] == "REQUESTED":
                apply_result(conn, po["payment_key"], None, "UNKNOWN", "payment-dispatcher", key, f"전송 결과 불명: {exc.detail}")
            return
        conn.execute("UPDATE review.payment_outbox SET status = 'SENT', sent_at = now(), response = %s WHERE outbox_id = %s",
                     (Jsonb(plain(data)), outbox_id))
        if status < 300 and isinstance(data, dict) and data.get("status") in ("PAID", "FAILED"):
            try:
                apply_result(conn, po["payment_key"], data.get("external_transaction_id"), data["status"],
                             "payment-dispatcher", key, f"지급 요청 {data.get('request_no')} 응답")
            except Reject as exc:
                log_action(conn, "RecordPaymentResult", "payment-dispatcher", [_ref("PaymentOrder", po["payment_order_id"])],
                           key, "REJECTED", f"{exc.code}: {exc.message}")
        elif status >= 400:
            log_action(conn, "RequestPayment", "payment-dispatcher", [_ref("PaymentOrder", po["payment_order_id"])], key,
                       "REJECTED", f"지급 시스템 거절 HTTP {status}: {data}")


# ── A09 지급 요청 ────────────────────────────────────────────────────────────

@app.post("/payment-orders/{payment_order_id}/request", operation_id="requestPayment", summary="지급 요청 (A09)",
          dependencies=AUTH,
          description="예약(RESERVED)된 지급 지시, 또는 미지급이 확인된(FAILED) 지급 지시의 지급을 요청한다. 지급 지시를 REQUESTED 로 "
                      "바꾸고 전송 대기 기록을 남긴 뒤 지급 시스템에 같은 지급 키로 보낸다. 응답에 따라 PAID / FAILED, 결과를 모르면 UNKNOWN. "
                      "재시도에도 새 지급 지시를 만들지 않는다.")
def request_payment(payment_order_id: str, body: Actor, idem: str = IdemKey):
    def run(conn):
        po = one(conn, ORDER + " WHERE payment_order_id = %s FOR UPDATE", (payment_order_id,), f"지급 지시 {payment_order_id}")
        if po["status"] not in ("RESERVED", "FAILED"):
            raise Reject("INVALID_STATE", f"지급 지시 {payment_order_id} 는 {po['status']} 입니다 (RESERVED 또는 FAILED 필요)")
        attempt = conn.execute("SELECT count(*) + 1 AS n FROM review.payment_outbox WHERE payment_order_id = %s",
                               (payment_order_id,)).fetchone()["n"]
        outbox_id = next_id(conn, "review.outbox_seq", "OB-", 5)
        conn.execute("INSERT INTO review.payment_outbox (outbox_id, payment_order_id, payment_key, attempt, status) "
                     "VALUES (%s, %s, %s, %s, 'PENDING')", (outbox_id, payment_order_id, po["payment_key"], attempt))
        conn.execute("UPDATE review.payment_order SET status = 'REQUESTED', revision = revision + 1, updated_at = now() "
                     "WHERE payment_order_id = %s", (payment_order_id,))
        log_action(conn, "RequestPayment", body.actor_id, [_ref("PaymentOrder", payment_order_id), _ref("Claim", po["claim_id"])],
                   idem, reason=f"{po['status']} → REQUESTED (시도 {attempt}, 지급 키 {po['payment_key']})", before=po)
        return {"payment_order_id": payment_order_id, "outbox_id": outbox_id}

    first = run_action("RequestPayment", body.actor_id, idem, {"payment_order_id": payment_order_id, **body.model_dump()},
                       [_ref("PaymentOrder", payment_order_id)], run)
    deliver(first["outbox_id"])   # 트랜잭션 뒤에 보낸다. 이미 보냈으면 아무것도 하지 않는다
    with db() as conn:
        view = _order_view(conn, payment_order_id)
    return {**view, "status": view["claim_status"]}


# ── A10 지급 결과 반영 (지급 연계 전용) ─────────────────────────────────────────

@app.post("/payment-results", operation_id="recordPaymentResult", summary="지급 결과 반영 (A10, 지급 연계 전용)",
          description="지급 연계 서비스가 지급 결과를 알린다. X-Payment-Signature(본문 HMAC-SHA256) 서명이 맞아야 한다. "
                      "REQUESTED·UNKNOWN 에서 PAID(청구도 PAID) / FAILED / UNKNOWN 으로 바꾼다. 같은 결과의 재수신은 기존 결과를 돌려주고, "
                      "상충하는 결과는 덮어쓰지 않고 거절 이력을 남긴다. 사람이 실행하는 액션이 아니다.")
async def record_payment_result(request: Request, body: PaymentResultIn,
                                signature: str | None = Header(None, alias="X-Payment-Signature"),
                                idem: str | None = Header(None, alias="Idempotency-Key")):
    raw = await request.body()
    if not signature_ok(raw, signature):
        raise HTTPException(401, "X-Payment-Signature 가 맞지 않습니다")
    key = idem or f"{body.payment_key}:{body.external_transaction_id}:{body.result}"

    def work():
        return run_action("RecordPaymentResult", "payment-connector", key, body.model_dump(),
                          [_ref("PaymentKey", body.payment_key)],
                          lambda conn: apply_result(conn, body.payment_key, body.external_transaction_id, body.result,
                                                    "payment-connector", key, "지급 연계 콜백"))
    return await run_in_threadpool(work)


# ── A11 지급 대사 ────────────────────────────────────────────────────────────

@app.post("/payment-orders/{payment_order_id}/reconcile", operation_id="reconcilePayment", summary="지급 결과 대사 (A11)",
          dependencies=AUTH,
          description="결과를 모르는(UNKNOWN) 또는 요청 중(REQUESTED)인 지급 지시를 지급 시스템에서 지급 키로 조회해 결과를 확정한다. "
                      "지급 시스템이 PAID / FAILED 면 반영, 아직 처리 중이면 그대로 둔다. 지급 시스템에 기록이 없으면 미지급 확인으로 FAILED.")
def reconcile_payment(payment_order_id: str, body: Actor, idem: str = IdemKey):
    def run(conn):
        po = one(conn, ORDER + " WHERE payment_order_id = %s FOR UPDATE", (payment_order_id,), f"지급 지시 {payment_order_id}")
        if po["status"] not in ("UNKNOWN", "REQUESTED"):
            raise Reject("INVALID_STATE", f"지급 지시 {payment_order_id} 는 {po['status']} 입니다 (UNKNOWN 또는 REQUESTED 필요)")
        _, found = call("payment", "GET", "/payment-requests", params={"payment_key": po["payment_key"]})
        if not found:
            out = apply_result(conn, po["payment_key"], None, "FAILED", body.actor_id, idem,
                               "대사: 지급 시스템에 요청 기록 없음 (NOT_RECEIVED)")
            return {**out, "external": None}
        ext = found[0]
        if ext["status"] in ("PAID", "FAILED"):
            out = apply_result(conn, po["payment_key"], ext["external_transaction_id"], ext["status"], body.actor_id, idem,
                               f"대사: 지급 요청 {ext['request_no']}")
            return {**out, "external": ext}
        log_action(conn, "ReconcilePayment", body.actor_id, [_ref("PaymentOrder", payment_order_id)], idem,
                   reason=f"대사: 지급 시스템 {ext['status']}, 상태 유지")
        return {"result": "STILL_PENDING", "payment_order": po, "external": ext, "status": _claim_status(conn, po["claim_id"])}
    return run_action("ReconcilePayment", body.actor_id, idem, {"payment_order_id": payment_order_id, **body.model_dump()},
                      [_ref("PaymentOrder", payment_order_id)], run)
