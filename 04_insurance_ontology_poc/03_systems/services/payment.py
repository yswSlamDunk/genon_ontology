"""지급 시스템 (ins-payment, :18104) — 모의 지급 요청과 결과. 인증: X-Payment-Key (env INS_PAYMENT_API_KEY).

외부 지급 시스템을 흉내 낸다. 심사 시스템의 지급 지시를 지급 키(payment_key)로만 안다.
식별자: 지급 요청 번호 PAYREQ-…, 외부 거래 ID TX-….
쓰기: submitPaymentRequest (심사 시스템 A09가 부른다). 같은 지급 키면 새 요청을 만들지 않는다.
테스트 전용 제어(/mock/…)는 OpenAPI 문서에 넣지 않는다 (서버_설계서.md 7.7절).
"""

from __future__ import annotations

import json
import os
import time

from fastapi import Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from common import LIMIT, DependencyError, Reject, api_key_auth, call, db, db_write, make_app, next_id, one, rows, sign, where

app = make_app(
    title="지급 시스템 (모의)",
    description="모의 지급 시스템. 지급 요청과 결과(지급 완료·실패), 외부 거래 ID를 다룬다. 심사 시스템의 지급 지시와는 "
                "지급 키로 대사한다. 데이터는 insurance DB의 payment 스키마다.",
    schema="payment",
)
auth = api_key_auth("INS_PAYMENT_API_KEY", header="X-Payment-Key")
AUTH = [Depends(auth)]
MOCK_DELAY = float(os.environ.get("INS_MOCK_PAYMENT_DELAY", "5"))   # TIMEOUT 흉내: 심사 시스템 제한(3초)보다 길게

REQUEST = ("SELECT request_no, payment_key, amount_krw, beneficiary_token, status, external_transaction_id, attempt_count, "
           "requested_at, completed_at, created_at, updated_at FROM payment.payment_request")


@app.get("/payment-requests/{request_no}", operation_id="getPaymentRequest", summary="지급 요청 조회", dependencies=AUTH,
         description="지급 요청 번호로 1건을 돌려준다.")
def get_payment_request(request_no: str):
    with db() as conn:
        return one(conn, REQUEST + " WHERE request_no = %s", (request_no,), f"지급 요청 {request_no}")


@app.get("/payment-requests", operation_id="listPaymentRequests", summary="지급 요청 목록", dependencies=AUTH,
         description="지급 키(심사 시스템 지급 지시의 payment_key)나 상태로 찾는다. 지급 결과 대사에 쓴다.")
def list_payment_requests(payment_key: str | None = Query(None, description="지급 키"),
                          status: str | None = Query(None, description="REQUESTED, PAID, FAILED"), limit: int = LIMIT):
    w, p = where({"payment_key": payment_key, "status": status})
    with db() as conn:
        return rows(conn, REQUEST + w + " ORDER BY requested_at, request_no LIMIT %s", (*p, limit))


class PaymentIn(BaseModel):
    payment_key: str = Field(..., description="지급 키 (재시도에도 같은 키)")
    amount_krw: int = Field(..., gt=0, description="지급 금액 (원)")
    beneficiary_token: str = Field(..., description="수익자 가상 계좌 토큰")
    payment_order_id: str | None = Field(None, description="심사 시스템 지급 지시 ID (참고용)")


def _settle(conn, request_no: str, outcome: str) -> dict:
    if outcome == "PAID":
        tx = next_id(conn, "payment.transaction_seq", "TX-", 5)
        conn.execute("UPDATE payment.payment_request SET status = 'PAID', external_transaction_id = %s, completed_at = now(), "
                     "updated_at = now() WHERE request_no = %s", (tx, request_no))
    elif outcome == "FAILED":
        conn.execute("UPDATE payment.payment_request SET status = 'FAILED', completed_at = now(), updated_at = now() "
                     "WHERE request_no = %s", (request_no,))
    return one(conn, REQUEST + " WHERE request_no = %s", (request_no,), request_no)


@app.post("/payment-requests", operation_id="submitPaymentRequest", summary="지급 요청 (심사 시스템 전용)", dependencies=AUTH,
          description="지급 키로 지급을 요청한다. 같은 지급 키가 이미 PAID 거나 처리 중이면 새로 지급하지 않고 기존 결과를 돌려준다. "
                      "FAILED 면 같은 요청으로 다시 시도한다(attempt_count 증가). 응답 status: PAID / FAILED / REQUESTED.")
def submit_payment_request(body: PaymentIn):
    delay = False
    with db_write() as conn:
        prev = conn.execute(REQUEST + " WHERE payment_key = %s FOR UPDATE", (body.payment_key,)).fetchone()
        if prev and (prev["amount_krw"] != body.amount_krw or prev["beneficiary_token"] != body.beneficiary_token):
            raise Reject("PAYMENT_KEY_CONFLICT", f"지급 키 {body.payment_key} 는 다른 금액·수익자로 이미 요청됐습니다")
        if prev and prev["status"] in ("PAID", "REQUESTED"):
            return prev
        if prev:   # FAILED → 같은 요청으로 재시도
            request_no = prev["request_no"]
            conn.execute("UPDATE payment.payment_request SET status = 'REQUESTED', attempt_count = attempt_count + 1, "
                         "completed_at = NULL, updated_at = now() WHERE request_no = %s", (request_no,))
        else:
            request_no = next_id(conn, "payment.request_seq", "PAYREQ-", 5)
            conn.execute("INSERT INTO payment.payment_request (request_no, payment_key, amount_krw, beneficiary_token, status, "
                         "requested_at) VALUES (%s, %s, %s, %s, 'REQUESTED', now())",
                         (request_no, body.payment_key, body.amount_krw, body.beneficiary_token))
        mock = conn.execute("DELETE FROM payment.mock_outcome WHERE id = (SELECT min(id) FROM payment.mock_outcome) "
                            "RETURNING outcome").fetchone()
        outcome = mock["outcome"] if mock else "PAID"
        if outcome in ("PAID", "FAILED"):
            result = _settle(conn, request_no, outcome)
        elif outcome == "LOST_RESPONSE":   # 처리는 됐는데 응답이 사라짐
            _settle(conn, request_no, "PAID")
            delay = True
        else:                              # TIMEOUT: 받아 두고 응답하지 않음
            delay = True
    if delay:
        time.sleep(MOCK_DELAY)
        return JSONResponse({"detail": "mock timeout"}, status_code=504)
    return result


# ── 테스트 전용 제어 (OpenAPI 제외) ──────────────────────────────────────────

class OutcomesIn(BaseModel):
    outcomes: list[str]


class SettleIn(BaseModel):
    status: str


@app.post("/mock/outcomes", include_in_schema=False, dependencies=AUTH)
def mock_outcomes(body: OutcomesIn):
    with db_write() as conn:
        for o in body.outcomes:
            conn.execute("INSERT INTO payment.mock_outcome (outcome) VALUES (%s)", (o,))
        return {"queued": rows(conn, "SELECT id, outcome FROM payment.mock_outcome ORDER BY id")}


@app.post("/mock/payment-requests/{request_no}/settle", include_in_schema=False, dependencies=AUTH)
def mock_settle(request_no: str, body: SettleIn):
    with db_write() as conn:
        r = one(conn, REQUEST + " WHERE request_no = %s FOR UPDATE", (request_no,), f"지급 요청 {request_no}")
        if r["status"] != "REQUESTED":
            raise Reject("INVALID_STATE", f"지급 요청 {request_no} 는 {r['status']} 입니다")
        return _settle(conn, request_no, body.status)


@app.post("/mock/payment-requests/{request_no}/callback", include_in_schema=False, dependencies=AUTH)
def mock_callback(request_no: str):
    """현재 결과를 서명해 심사 시스템 A10으로 보낸다. 두 번 부르면 중복 콜백 (T24)."""
    with db() as conn:
        r = one(conn, REQUEST + " WHERE request_no = %s", (request_no,), f"지급 요청 {request_no}")
    payload = json.dumps({"payment_key": r["payment_key"], "external_transaction_id": r["external_transaction_id"],
                          "result": r["status"] if r["status"] != "REQUESTED" else "UNKNOWN"}).encode()
    try:
        status, data = call("review", "POST", "/payment-results", json_body=None,
                            headers={"X-Payment-Signature": sign(payload), "Content-Type": "application/json"},
                            raw=payload)
    except DependencyError as exc:
        return JSONResponse({"detail": exc.detail}, status_code=502)
    return JSONResponse({"review_status": status, "review_response": data}, status_code=200)
