"""2단계 쓰기 API 시나리오 테스트 — 명세 11절 T01–T29 중 서버로 확인할 수 있는 것 + Action별 경로.

매 테스트 전에 02_data/reset.sh 로 B0(+변형)를 복원한다 (명세 11.1절). 서버가 켜져 있어야 한다 (./run.sh start).
비밀 값은 출력하지 않는다.

    .venv/bin/python scenario_test.py              # 전체
    .venv/bin/python scenario_test.py T01 T18      # 일부
    .venv/bin/python scenario_test.py --repeat 100 T18 T19   # 동시 승인 반복 (명세 11.4절)
    .venv/bin/python scenario_test.py --report ../05_tests/서버_2단계_테스트_결과.md
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import os
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import httpx
import psycopg
from psycopg.rows import dict_row

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "services"))
import evaluation  # noqa: E402

ENV = dict(line.split("=", 1) for line in (HERE / ".env.local").read_text().split() if "=" in line)
RESET = HERE.parent / "02_data" / "reset.sh"
ADMIN_DSN = f"host=/tmp port=5432 dbname=insurance user={os.environ.get('USER')}"
PSQL_ENV = {**os.environ, "PSQL": "/opt/homebrew/opt/postgresql@16/bin/psql", "PGHOST": "/tmp", "PGPORT": "5432",
            "PGUSER": os.environ.get("USER", "")}

URL = {"contract": "http://127.0.0.1:18101", "intake": "http://127.0.0.1:18102", "review": "http://127.0.0.1:18103",
       "payment": "http://127.0.0.1:18104"}
AUTH = {
    "contract": {"X-API-Key": ENV["INS_CONTRACT_API_KEY"]},
    "intake": {"Authorization": "Basic " + base64.b64encode(ENV["INS_INTAKE_BASIC"].encode()).decode()},
    "review": {"Authorization": "Bearer " + ENV["INS_REVIEW_TOKEN"]},
    "payment": {"X-Payment-Key": ENV["INS_PAYMENT_API_KEY"]},
}

RESULTS: list[tuple[str, str, bool, str]] = []   # (test, check, ok, detail)
CURRENT = {"test": ""}


# ── 도구 ─────────────────────────────────────────────────────────────────────

def reset(*variants: str) -> None:
    out = subprocess.run([str(RESET), *variants], env=PSQL_ENV, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"reset 실패 {variants}: {out.stderr[-500:]}")


def key() -> str:
    return "k-" + uuid.uuid4().hex[:12]


def post(system: str, path: str, body: dict, idem: str | None = None, timeout: float = 20) -> tuple[int, dict]:
    r = httpx.post(URL[system] + path, json=body, headers={**AUTH[system], "Idempotency-Key": idem or key()}, timeout=timeout)
    return r.status_code, r.json()


def get(system: str, path: str, **params) -> dict | list:
    return httpx.get(URL[system] + path, params=params, headers=AUTH[system], timeout=10).json()


def sql(query: str, params: tuple = ()) -> list[dict]:
    with psycopg.connect(ADMIN_DSN, row_factory=dict_row) as conn:
        cur = conn.execute(query, params)
        return cur.fetchall() if cur.description else []


def code(resp: dict) -> str | None:
    d = resp.get("detail")
    return d.get("code") if isinstance(d, dict) else None


def check(name: str, ok: bool, detail: object = "") -> bool:
    RESULTS.append((CURRENT["test"], name, bool(ok), "" if ok else str(detail)[:300]))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + ("" if ok else f"  — {str(detail)[:300]}"))
    return bool(ok)


def evaluate(claim: str = "CL-001", actor: str = "reviewer-01") -> dict:
    status, body = post("review", f"/claims/{claim}/evaluate", {"actor_id": actor})
    assert status == 200, body
    return body


def approve(claim: str, assessment: str, actor: str = "reviewer-01", idem: str | None = None) -> tuple[int, dict]:
    return post("review", f"/claims/{claim}/approve", {"actor_id": actor, "assessment_id": assessment, "reason": "테스트 승인"},
                idem)


def rule(ev: dict, rule_id: str) -> str:
    a = get("review", f"/assessments/{ev['assessment_id']}")
    return next(r["result"] for r in a["rule_results"] if r["rule_id"].startswith(rule_id))


def orders(claim: str | None = None) -> list[dict]:
    return sql("SELECT * FROM review.payment_order" + (" WHERE claim_id = %s" if claim else ""), (claim,) if claim else ())


def open_tasks(claim: str = "CL-001") -> list[dict]:
    return sql("SELECT task_type, reason_code, related_ref FROM review.review_task WHERE claim_id = %s AND status = 'OPEN'", (claim,))


# ── 업무 규칙 테스트 (명세 11.2절) ───────────────────────────────────────────

def expect_eval(variant: str | None, rec: str, days, amount, extra=None) -> dict:
    reset(*([variant] if variant else []))
    ev = evaluate()
    check(f"평가 결과 {rec}", ev["recommendation"] == rec, ev)
    check(f"인정 일수 {days}, 금액 {amount}", ev["eligible_days"] == days and ev["candidate_amount_krw"] == amount, ev)
    if extra:
        extra(ev)
    return ev


def t01():
    reset()
    ev = evaluate()
    check("후보 3일·300,000원, READY_FOR_DECISION", (ev["eligible_days"], ev["candidate_amount_krw"], ev["status"])
          == (3, 300000, "READY_FOR_DECISION"), ev)
    check("R01–R07 모두 PASS", all(r["result"] == "PASS" for r in get("review", f"/assessments/{ev['assessment_id']}")["rule_results"]))
    check("대기 기간 종료 2026-01-31, 잔여 5일", ev["figures"]["waiting_end_date"] == "2026-01-31"
          and ev["figures"]["remaining_days"] == 5, ev["figures"])
    s, ap = approve("CL-001", ev["assessment_id"])
    check("승인 → APPROVED, PY RESERVED 3일 300,000원", s == 200 and ap["status"] == "APPROVED"
          and (ap["payment_order"]["status"], ap["payment_order"]["reserved_days"], ap["payment_order"]["amount_krw"])
          == ("RESERVED", 3, 300000), ap)
    s, pay = post("review", f"/payment-orders/{ap['payment_order']['payment_order_id']}/request", {"actor_id": "payer-01"})
    check("지급 요청 → 지급 지시 PAID, 청구 PAID", s == 200 and pay["status"] == "PAID" and pay["claim_status"] == "PAID", pay)
    check("평가 1개, 지급 지시 1개", len(sql("SELECT 1 FROM review.assessment")) == 1 and len(orders()) == 1)
    logs = {r["action_type"] for r in sql("SELECT action_type FROM review.action_log WHERE outcome = 'SUCCESS'")}
    check("실행 이력: 평가·승인·지급 요청·결과 반영", {"EvaluateClaim", "ApproveClaim", "RequestPayment", "RecordPaymentResult"} <= logs, logs)
    s, lock = post("review", "/documents/DC-001/verify", {"actor_id": "reviewer-01", "verification_status": "REJECTED",
                                                          "note": "덮어쓰기 시도"})
    check("승인 근거 증빙은 A03으로 덮어쓸 수 없음 (EVIDENCE_LOCKED)", s == 409 and code(lock) == "EVIDENCE_LOCKED", lock)


def t02():
    expect_eval("T02", "NOT_PAYABLE_CANDIDATE", 0, 0, lambda ev: (
        check("R03 FAIL", rule(ev, "R03") == "FAIL"),
        check("자동 부지급 결정 없음 (READY_FOR_DECISION)", ev["status"] == "READY_FOR_DECISION", ev["status"])))


def t03():
    expect_eval("T03", "PAYABLE_CANDIDATE", 3, 300000, lambda ev: check("R03 PASS", rule(ev, "R03") == "PASS"))


def t04():
    expect_eval("T04", "PAYABLE_CANDIDATE", 3, 300000, lambda ev: check("R02 PASS (퇴원일 = 보장 종료일)", rule(ev, "R02") == "PASS"))


def t05():
    expect_eval("T05", "NOT_PAYABLE_CANDIDATE", 0, 0, lambda ev: check("R02 FAIL", rule(ev, "R02") == "FAIL"))


def t06():
    expect_eval("T06", "NEED_INFO", None, None, lambda ev: check("보완 업무 1개", [t["task_type"] for t in open_tasks()]
                                                                  == ["EVIDENCE_REQUEST"], open_tasks()))
    evaluate()
    check("다시 평가해도 미해결 업무가 늘지 않음", len(open_tasks()) == 1, open_tasks())


def t07():
    expect_eval("T07", "MANUAL_REVIEW", None, None, lambda ev: check("사실 충돌 업무 (FACT_REVIEW, DC-001)", open_tasks()
                                                                      == [{"task_type": "FACT_REVIEW", "reason_code": "FACT_CONFLICT",
                                                                           "related_ref": "DC-001"}], open_tasks()))


def t08():
    ev = expect_eval("T08", "MANUAL_REVIEW", None, None, lambda ev: (
        check("R06 UNKNOWN", rule(ev, "R06") == "UNKNOWN"),
        check("중복 검토 업무 (CL-901)", {"task_type": "DUPLICATE_REVIEW", "reason_code": "DUPLICATE_REVIEW",
                                     "related_ref": "CL-901"} in open_tasks(), open_tasks())))
    s, ap = approve("CL-001", ev["assessment_id"])
    check("승인 불가", s == 409, ap)


def t09():
    expect_eval("T09", "PAYABLE_CANDIDATE", 2, 200000, lambda ev: check("잔여 2일 = 5 − 기지급 3", ev["figures"]["remaining_days"] == 2))


def t10():
    expect_eval("T10", "NOT_PAYABLE_CANDIDATE", 0, 0, lambda ev: check("R07 FAIL", rule(ev, "R07") == "FAIL"))


def t11():
    expect_eval("T11", "NOT_PAYABLE_CANDIDATE", 0, 0, lambda ev: (
        check("R01 FAIL (계약자를 피보험자로 취급하지 않음)", rule(ev, "R01") == "FAIL"),
        check("R04 PASS (증빙과 사건은 일치)", rule(ev, "R04") == "PASS")))


def t12():
    expect_eval("T12", "MANUAL_REVIEW", None, None, lambda ev: (
        check("PERIOD_CROSSING, 일부 일수 자동 산정 없음", "PERIOD_CROSSING" in ev["reason_codes"], ev["reason_codes"])))


def t13():
    expect_eval("T13", "NOT_PAYABLE_CANDIDATE", 0, 0, lambda ev: check("R05 FAIL", rule(ev, "R05") == "FAIL"))


def t14():
    expect_eval("T14", "MANUAL_REVIEW", None, None, lambda ev: (
        check("INVALID_DATES, DATA_REPAIR 업무", "INVALID_DATES" in ev["reason_codes"]
              and any(t["task_type"] == "DATA_REPAIR" for t in open_tasks()), (ev["reason_codes"], open_tasks()))))


def t15():
    reset("T15")
    ev = evaluate()
    check("평가 보류 (HELD), 평가 기록 없음", ev["result"] == "HELD" and not sql("SELECT 1 FROM review.assessment"), ev)
    check("데이터 보정 업무 (DEPENDENCY_UNAVAILABLE)", any(t["reason_code"] == "DEPENDENCY_UNAVAILABLE" for t in open_tasks()),
          open_tasks())


# ── Action·상태·연계 테스트 (명세 11.3절) ─────────────────────────────────────

def t16():
    reset()
    ev = evaluate()
    k = key()
    s1, a1 = approve("CL-001", ev["assessment_id"], idem=k)
    s2, a2 = approve("CL-001", ev["assessment_id"], idem=k)
    check("같은 키 2회 → 같은 지급 지시", s1 == s2 == 200 and a1["payment_order"]["payment_order_id"]
          == a2["payment_order"]["payment_order_id"], (a1, a2))
    check("유효 지급 지시 1개, 예약 3일", len(orders()) == 1 and orders()[0]["reserved_days"] == 3)


def t17():
    reset()
    ev = evaluate()
    approve("CL-001", ev["assessment_id"])
    s, a = approve("CL-001", ev["assessment_id"])
    check("다른 키의 두 번째 승인 → 상태 조건 거절", s == 409 and code(a) == "INVALID_STATE", a)
    check("추가 예약 없음", len(orders()) == 1)


def concurrent_approvals(variants: tuple[str, ...], repeat: int, label: str, same_event: bool) -> None:
    over, wins_ok, stale_ok = 0, 0, 0
    for _ in range(repeat):
        reset(*variants)
        a, b = evaluate("CL-001"), evaluate("CL-902")
        if not (a["recommendation"] == b["recommendation"] == "PAYABLE_CANDIDATE"):
            check(f"{label}: 두 청구 모두 지급 후보", False, (a, b))
            return
        out: dict[str, tuple[int, dict]] = {}
        barrier = threading.Barrier(2)

        def go(claim, ass):
            barrier.wait()
            out[claim] = approve(claim, ass)
        ts = [threading.Thread(target=go, args=(c, e["assessment_id"])) for c, e in (("CL-001", a), ("CL-902", b))]
        [t.start() for t in ts]
        [t.join() for t in ts]
        codes = sorted((s, code(r)) for s, r in out.values())
        wins_ok += codes[0][0] == 200 and codes[1] == (409, "STALE_ASSESSMENT")
        total = sql("SELECT coalesce(sum(reserved_days), 0) AS n FROM review.payment_order")[0]["n"]
        over += total > 5
        if same_event:
            loser = next(c for c, (s, _) in out.items() if s != 200)
            re = evaluate(loser)
            stale_ok += re["recommendation"] == "MANUAL_REVIEW" and "DUPLICATE_REVIEW" in re["reason_codes"]
    check(f"{label}: {repeat}회 모두 한 건만 승인, 다른 건 STALE_ASSESSMENT", wins_ok == repeat, f"{wins_ok}/{repeat}")
    check(f"{label}: 지급+예약 합계 ≤ 5일 (초과 0회)", over == 0, f"초과 {over}회")
    if same_event:
        check(f"{label}: 진 쪽 재평가 → 중복 검토 (MANUAL_REVIEW)", stale_ok == repeat, f"{stale_ok}/{repeat}")


def t18(repeat: int):
    concurrent_approvals(("T18", "SECOND"), repeat, "동시 승인·한도 (기지급 2일 + 3일 × 2)", False)


def t19(repeat: int):
    concurrent_approvals(("SAME_EVENT",), repeat, "동시 승인·같은 사건", True)


def t20():
    reset()
    ev = evaluate()
    sql("UPDATE intake.document SET content_hash = 'corrected-hash' WHERE doc_id = 'DC-001'")   # 증빙 정정
    s, a = approve("CL-001", ev["assessment_id"])
    check("평가 후 증빙 정정 → STALE_ASSESSMENT", s == 409 and code(a) == "STALE_ASSESSMENT", a)
    check("지급 지시 없음", not orders())


def t21():
    reset()
    ev = evaluate()
    s, a = approve("CL-001", ev["assessment_id"], actor="reviewer-02")
    check("담당자가 아닌 승인 → 거절", s == 409 and code(a) == "NOT_ASSIGNED_REVIEWER", a)
    check("거절 이력 남음", sql("SELECT 1 FROM review.action_log WHERE action_type = 'ApproveClaim' AND outcome = 'REJECTED' "
                            "AND actor_id = 'reviewer-02'"))
    check("청구·예약 변화 없음", not orders() and get("review", "/claims/CL-001")["status"] == "READY_FOR_DECISION")


def t22():
    reset("T06")
    first = evaluate()
    task = sql("SELECT task_id FROM review.review_task WHERE status = 'OPEN'")[0]["task_id"]
    s, att = post("intake", "/receipts/RC-0001/documents", {"doc_id": "DC-001", "actor_id": "intake-01"})
    check("A02-1 서류 다시 연결", s == 200 and att["attachment_id"], att)
    s, rec = post("review", "/claims/CL-001/evidence-attached", {"doc_id": "DC-001", "actor_id": "intake-01"})
    check("A02-2 반영 → UNDER_REVIEW", s == 200 and rec["status"] == "UNDER_REVIEW", rec)
    facts = {"insured": "IP-0002", "provider_code": "H-001", "admission_date": "2026-03-10", "discharge_date": "2026-03-13"}
    s, ver = post("review", "/documents/DC-001/verify", {"actor_id": "reviewer-01", "verification_status": "VERIFIED",
                                                         "verified_facts": facts, "note": "원본 대조"})
    check("A03 확인", s == 200 and ver["verification_status"] == "VERIFIED", ver)
    s, res = post("review", f"/tasks/{task}/resolve", {"actor_id": "reviewer-01", "resolution": "입퇴원확인서 재제출 확인"})
    check("A06 보완 업무 해결", s == 200 and res["task"]["status"] == "RESOLVED", res)
    second = evaluate()
    check("재평가 → 지급 후보 300,000원", second["recommendation"] == "PAYABLE_CANDIDATE" and second["candidate_amount_krw"] == 300000,
          second)
    check("이전 평가 보존 (평가 2개)", {r["assessment_id"] for r in sql("SELECT assessment_id FROM review.assessment")}
          == {first["assessment_id"], second["assessment_id"]})


def approved_order() -> dict:
    ev = evaluate()
    return approve("CL-001", ev["assessment_id"])[1]["payment_order"]


def t23():
    reset()
    po = approved_order()
    post("payment", "/mock/outcomes", {"outcomes": ["TIMEOUT"]})
    t0 = time.time()
    s, pay = post("review", f"/payment-orders/{po['payment_order_id']}/request", {"actor_id": "payer-01"})
    check("지급 요청 결과 불명 → UNKNOWN, 청구 APPROVED", s == 200 and pay["payment_order_id"] and pay["status"] == "APPROVED"
          and get("review", f"/payment-orders/{po['payment_order_id']}")["status"] == "UNKNOWN", pay)
    check("예약 3일 유지, 추가 지급 지시 없음", len(orders()) == 1 and orders()[0]["reserved_days"] == 3)
    check("심사 시스템은 3초 제한으로 기다림", time.time() - t0 < 5, round(time.time() - t0, 1))
    s, rc = post("review", f"/payment-orders/{po['payment_order_id']}/reconcile", {"actor_id": "payer-01"})
    check("A11 대사: 지급 시스템 처리 중 → 유지", s == 200 and rc["result"] == "STILL_PENDING", rc)
    req = get("payment", "/payment-requests", payment_key=po["payment_key"])[0]
    post("payment", f"/mock/payment-requests/{req['request_no']}/settle", {"status": "PAID"})
    s, rc = post("review", f"/payment-orders/{po['payment_order_id']}/reconcile", {"actor_id": "payer-01"})
    check("A11 대사: 지급 확인 → PAID, 청구 PAID", s == 200 and rc["result"] == "PAID" and rc["status"] == "PAID", rc)


def t24():
    reset()
    po = approved_order()
    post("review", f"/payment-orders/{po['payment_order_id']}/request", {"actor_id": "payer-01"})
    req = get("payment", "/payment-requests", payment_key=po["payment_key"])[0]
    r1 = httpx.post(f"{URL['payment']}/mock/payment-requests/{req['request_no']}/callback", headers=AUTH["payment"]).json()
    r2 = httpx.post(f"{URL['payment']}/mock/payment-requests/{req['request_no']}/callback", headers=AUTH["payment"]).json()
    check("같은 거래 ID 성공 콜백 2회 → 기존 결과 반환", r1["review_status"] == r2["review_status"] == 200
          and r2["review_response"]["result"] == "DUPLICATE", (r1, r2))
    check("PAID 1건, 지급 일수 3일", [(o["status"], o["reserved_days"]) for o in orders()] == [("PAID", 3)])
    bad = httpx.post(f"{URL['review']}/payment-results", json={"payment_key": po["payment_key"], "result": "FAILED"},
                     headers={"X-Payment-Signature": "forged"})
    check("서명이 틀린 콜백 → 401", bad.status_code == 401, bad.status_code)


def t25():
    reset()
    po = approved_order()
    post("payment", "/mock/outcomes", {"outcomes": ["FAILED"]})
    s, p1 = post("review", f"/payment-orders/{po['payment_order_id']}/request", {"actor_id": "payer-01"})
    check("첫 지급 요청 → FAILED (예약 유지)", get("review", f"/payment-orders/{po['payment_order_id']}")["status"] == "FAILED"
          and orders()[0]["reserved_days"] == 3, p1)
    s, p2 = post("review", f"/payment-orders/{po['payment_order_id']}/request", {"actor_id": "payer-01"})
    check("같은 지급 키로 재시도 → PAID", s == 200 and p2["status"] == "PAID", p2)
    reqs = get("payment", "/payment-requests")
    check("지급 지시 1개, 지급 요청 1건(시도 2회)", len(orders()) == 1 and len(reqs) == 1 and reqs[0]["attempt_count"] == 2, reqs)


def t26():
    reset()
    ev = evaluate()
    a = get("review", f"/assessments/{ev['assessment_id']}")
    snap = a["input_snapshot"]["snapshot"]
    sql("UPDATE intake.document SET content_hash = 'new-version' WHERE doc_id = 'DC-001'")   # 현재 문서를 새 버전으로
    again = evaluation.evaluate(snap)
    check("저장된 스냅샷으로 같은 해시·금액 재현", evaluation.input_hash(snap) == a["input_hash"]
          and again["candidate_amount_krw"] == a["candidate_amount_krw"] and again["recommendation"] == a["recommendation"])
    check("평가 기록의 로직 해시 = 규칙 RV-001 로직 해시", a["input_snapshot"]["engine_logic_hash"]
          == get("review", "/rules/RV-001")["logic_hash"])


def t27():
    reset()
    post("review", "/claims/CL-001/evidence-requests", {"actor_id": "reviewer-01", "missing_items": ["OTHER"],
                                                         "message": "추가 서류 요청"})
    ev = evaluate()
    check("미해결 업무가 있으면 지급 후보여도 READY_FOR_DECISION 아님", ev["recommendation"] == "PAYABLE_CANDIDATE"
          and ev["status"] == "UNDER_REVIEW", ev)
    s, a = approve("CL-001", ev["assessment_id"])
    check("승인 거절", s == 409, a)


def t28():
    reset()
    ev = evaluate()
    k = key()
    s1, a1 = approve("CL-001", ev["assessment_id"], idem=k)
    s2, a2 = approve("CL-001", "AS-999", idem=k)
    check("같은 요청 키·다른 입력 → 멱등성 충돌", s1 == 200 and s2 == 409 and code(a2) == "IDEMPOTENCY_CONFLICT", a2)
    check("원래 결과 유지", len(orders()) == 1 and get("review", "/claims/CL-001")["status"] == "APPROVED")


def t29():
    reset("T29")
    s, rc = post("intake", "/receipts", {"request_key": "REQ-T29", "policy_number": "TEST-POLICY-001",
                                         "coverage_code": "INPATIENT-DAILY-A", "submitter_no": "IP-0001", "patient_no": "IP-0002",
                                         "accident_no": "ACC-0029", "actor_id": "intake-01"})
    s, r = post("review", "/claims", {"receipt_no": rc["receipt_no"], "coverage_id": "CV-002", "actor_id": "intake-01"})
    check("다른 계약의 보장 연결 → 참조 일관성 거절", s == 409 and code(r) == "REFERENCE_MISMATCH", r)
    check("잘못된 청구 생성 없음", len(sql("SELECT 1 FROM review.claim")) == 1)


# ── Action 경로 (A01·A02 보상 포함) ──────────────────────────────────────────

def a01():
    reset("A01")
    body = {"request_key": "REQ-A01-1", "policy_number": "TEST-POLICY-001", "coverage_code": "INPATIENT-DAILY-A",
            "submitter_no": "IP-0001", "patient_no": "IP-0002", "accident_no": "ACC-0002", "provider_code": "H-003",
            "admission_date": "2026-05-01", "discharge_date": "2026-05-04", "actor_id": "intake-01"}
    s, rc = post("intake", "/receipts", body)
    s2, rc2 = post("intake", "/receipts", body)
    check("A01-1 접수 생성, 같은 요청 키는 같은 접수", s == s2 == 200 and rc["receipt_no"] == rc2["receipt_no"], (rc, rc2))
    s, conflict = post("intake", "/receipts", {**body, "accident_no": "ACC-XXXX"})
    check("같은 요청 키·다른 내용 → 거절", s == 409 and code(conflict) == "IDEMPOTENCY_CONFLICT", conflict)
    k = key()
    s, cl = post("review", "/claims", {"receipt_no": rc["receipt_no"], "actor_id": "intake-01"}, k)
    check("A01-2 청구 RECEIVED, 미확인 사건 생성", s == 200 and cl["status"] == "RECEIVED" and cl["event_created"], cl)
    s, again = post("review", "/claims", {"receipt_no": rc["receipt_no"], "actor_id": "intake-01"})
    check("같은 접수 재등록 → 거절", s == 409 and code(again) == "ALREADY_REGISTERED", again)
    claim = cl["claim_id"]
    ev = evaluate(claim)
    check("서류 없음·사건 미확인 → NEED_INFO, 보완 업무만", ev["recommendation"] == "NEED_INFO"
          and [t["task_type"] for t in open_tasks(claim)] == ["EVIDENCE_REQUEST"], (ev, open_tasks(claim)))
    s, doc = post("intake", "/documents", {"document_type": "HOSPITALIZATION_CERTIFICATE", "storage_ref": "test://DC-new",
                                           "content_hash": "hash-new", "actor_id": "intake-01"})
    post("intake", f"/receipts/{rc['receipt_no']}/documents", {"doc_id": doc["doc_id"], "actor_id": "intake-01"})
    s, rec = post("review", f"/claims/{claim}/evidence-attached", {"doc_id": doc["doc_id"], "actor_id": "intake-01"})
    check("서류 등록·연결·반영 → UNDER_REVIEW", s == 200 and rec["status"] == "UNDER_REVIEW", rec)
    facts = {"insured": "IP-0002", "provider_code": "H-003", "admission_date": "2026-05-01", "discharge_date": "2026-05-04"}
    s, ver = post("review", f"/documents/{doc['doc_id']}/verify", {"actor_id": "reviewer-01", "verification_status": "VERIFIED",
                                                                    "verified_facts": facts, "note": "원본 확인"})
    check("A03 확인 → 사건 사실 VERIFIED", s == 200 and ver["event_change"] == "VERIFIED", ver)
    task = sql("SELECT task_id FROM review.review_task WHERE claim_id = %s AND status = 'OPEN'", (claim,))[0]["task_id"]
    post("review", f"/tasks/{task}/resolve", {"actor_id": "reviewer-01", "resolution": "서류 접수 확인"})
    ev2 = evaluate(claim)
    check("재평가 → 지급 후보 3일·300,000원", (ev2["recommendation"], ev2["eligible_days"], ev2["candidate_amount_krw"])
          == ("PAYABLE_CANDIDATE", 3, 300000), ev2)
    # 성공한 A01을 Studio에서 취소하면 2단계는 보상이 없어 cancelReceipt만 불린다 → 청구가 있으니 거절
    s, inuse = post("intake", f"/receipts/{rc['receipt_no']}/cancel", {"reason": "사용자 취소", "actor_id": "studio"})
    still = get("intake", f"/receipts/{rc['receipt_no']}")
    check("청구가 있는 접수 취소 → RECEIPT_IN_USE, 접수 유지", s == 409 and code(inuse) == "RECEIPT_IN_USE"
          and still["cancelled_at"] is None, (inuse, still))
    # 접수 권한: 계약 역할이 없는 사람 → 거절, 보상(접수 취소) 뒤에는 등록 불가
    s, rc3 = post("intake", "/receipts", {**body, "request_key": "REQ-A01-3", "submitter_no": "IP-0003", "accident_no": "ACC-0003"})
    s, bad = post("review", "/claims", {"receipt_no": rc3["receipt_no"], "actor_id": "intake-01"})
    check("계약자·피보험자가 아닌 제출자 → SUBMITTER_NOT_ALLOWED", s == 409 and code(bad) == "SUBMITTER_NOT_ALLOWED", bad)
    s, cc = post("intake", f"/receipts/{rc3['receipt_no']}/cancel", {"reason": "A01 보상", "actor_id": "studio"})
    s, after = post("review", "/claims", {"receipt_no": rc3["receipt_no"], "actor_id": "intake-01"})
    check("보상 cancelReceipt 뒤 등록 → RECEIPT_CANCELLED", cc["cancelled_at"] and code(after) == "RECEIPT_CANCELLED", after)
    check("거절도 실행 이력에 남음", sql("SELECT 1 FROM review.action_log WHERE action_type = 'SubmitClaim' AND outcome = 'REJECTED'"))


def a02():
    reset()
    s, doc = post("intake", "/documents", {"document_type": "HOSPITALIZATION_CERTIFICATE", "storage_ref": "test://DC-repl",
                                           "content_hash": "hash-repl", "actor_id": "intake-01"})
    s, att = post("intake", "/receipts/RC-0001/documents", {"doc_id": doc["doc_id"], "replaces_doc_id": "DC-001",
                                                            "actor_id": "intake-01"})
    check("A02-1 교체 → 새 서류만 연결", s == 200 and [d["doc_id"] for d in att["documents"]] == [doc["doc_id"]], att)
    s, rv = post("intake", f"/attachments/{att['attachment_id']}/revert", {"actor_id": "studio", "reason": "A02 보상"})
    check("보상 revertAttachment → 원래 서류 DC-001 다시 연결", s == 200 and [d["doc_id"] for d in rv["documents"]] == ["DC-001"], rv)
    post("review", "/claims/CL-001/evaluate", {"actor_id": "reviewer-01"})
    s, doc2 = post("intake", "/documents", {"document_type": "OTHER", "storage_ref": "test://DC-late",
                                            "content_hash": "hash-late", "actor_id": "intake-01"})
    s, att2 = post("intake", "/receipts/RC-0001/documents", {"doc_id": doc2["doc_id"], "actor_id": "intake-01"})
    sql("UPDATE review.claim SET status = 'REJECTED' WHERE claim_id = 'CL-001'")
    # 성공한 A02를 청구 종결 뒤에 취소 → 근거 서류 연결을 되돌리지 않음
    s, nope = post("intake", f"/attachments/{att2['attachment_id']}/revert", {"actor_id": "studio", "reason": "사용자 취소"})
    docs = [d["doc_id"] for d in get("intake", "/receipts/RC-0001")["documents"]]
    check("종결된 청구의 연결 되돌리기 → CLAIM_CLOSED, 연결 유지", s == 409 and code(nope) == "CLAIM_CLOSED"
          and doc2["doc_id"] in docs, (nope, docs))
    s, closed = post("review", "/claims/CL-001/evidence-attached", {"doc_id": "DC-001", "actor_id": "intake-01"})
    check("종결된 청구에 증빙 반영 → CLAIM_CLOSED", s == 409 and code(closed) == "CLAIM_CLOSED", closed)


TESTS = {"T01": t01, "T02": t02, "T03": t03, "T04": t04, "T05": t05, "T06": t06, "T07": t07, "T08": t08, "T09": t09,
         "T10": t10, "T11": t11, "T12": t12, "T13": t13, "T14": t14, "T15": t15, "T16": t16, "T17": t17, "T18": t18,
         "T19": t19, "T20": t20, "T21": t21, "T22": t22, "T23": t23, "T24": t24, "T25": t25, "T26": t26, "T27": t27,
         "T28": t28, "T29": t29, "A01": a01, "A02": a02}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tests", nargs="*")
    ap.add_argument("--repeat", type=int, default=10, help="T18·T19 반복 횟수 (명세 11.4절은 100)")
    ap.add_argument("--report", help="결과를 Markdown 파일로 저장")
    args = ap.parse_args()
    names = args.tests or list(TESTS)
    started = dt.datetime.now().astimezone()
    for name in names:
        CURRENT["test"] = name
        print(f"[{name}]")
        try:
            TESTS[name](args.repeat) if name in ("T18", "T19") else TESTS[name]()
        except Exception as exc:   # noqa: BLE001 — 테스트 하나의 예외가 전체를 멈추지 않게
            check("예외 없이 실행", False, f"{type(exc).__name__}: {exc}")
    reset()
    failed = [r for r in RESULTS if not r[2]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} 통과" + (f", 실패 {len(failed)}" if failed else ""))
    if args.report:
        lines = [f"# 서버 2단계 시나리오 테스트 결과", "",
                 f"- 실행: {started:%Y-%m-%d %H:%M %Z}, `03_systems/scenario_test.py`" + (f" (T18·T19 각 {args.repeat}회)" if
                                                                                    {"T18", "T19"} & set(names) else ""),
                 f"- 결과: **{len(RESULTS) - len(failed)}/{len(RESULTS)} 통과**", "",
                 "| 테스트 | 확인 | 결과 | 실패 내용 |", "|---|---|---|---|"]
        lines += [f"| {t} | {c} | {'PASS' if ok else '**FAIL**'} | {d.replace('|', '/')} |" for t, c, ok, d in RESULTS]
        Path(args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"보고서: {args.report}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
