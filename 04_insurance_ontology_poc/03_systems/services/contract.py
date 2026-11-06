"""계약 시스템 (ins-contract, :18101) — 고객, 계약, 계약상 역할, 보장. 인증: X-API-Key (env INS_CONTRACT_API_KEY).

명세 12.2절: 계약·보장 정보는 원천 계약 시스템이 관리하며 임의 수정하지 않는다 → 조회 API만 둔다.
식별자: 고객번호 C-…, 내부 계약 ID PO-…, 보장 ID CV-…. 대외 계약 번호(policy_number)로도 찾을 수 있다.
"""

from __future__ import annotations

from fastapi import Depends, Query

from common import LIMIT, api_key_auth, db, make_app, one, rows, where

app = make_app(
    title="계약 시스템",
    description="보험 계약의 원천 시스템. 고객 마스터, 계약, 계약상 역할(계약자·피보험자·수익자), 가입 보장 버전을 조회한다. "
                "읽기 전용이다. 데이터는 insurance DB의 contract 스키마다.",
    schema="contract",
)
auth = api_key_auth("INS_CONTRACT_API_KEY")
AUTH = [Depends(auth)]

CUSTOMER = "SELECT cust_no, party_type, display_name, identity_token, created_at, updated_at, revision FROM contract.customer"
POLICY = ("SELECT policy_id, policy_number, contract_from, contract_to, administrative_status, created_at, updated_at, "
          "revision FROM contract.policy")
ROLE = ("SELECT role_id, policy_id, cust_no, role_type, valid_from, valid_to, created_at, updated_at, revision "
        "FROM contract.policy_role")
COVERAGE = ("SELECT c.coverage_id, c.policy_id, p.policy_number, c.coverage_code, c.version, c.valid_from, c.valid_to, "
            "c.daily_amount_krw, c.max_days, c.waiting_days, c.rule_code, c.rule_version, c.benefit_period_key, "
            "c.created_at, c.updated_at, c.revision FROM contract.coverage c JOIN contract.policy p USING (policy_id)")


@app.get("/customers/{cust_no}", operation_id="getCustomer", summary="고객 조회", dependencies=AUTH,
         description="계약 시스템 고객번호(예: C-10001)로 고객 1명을 돌려준다.")
def get_customer(cust_no: str):
    with db() as conn:
        return one(conn, CUSTOMER + " WHERE cust_no = %s", (cust_no,), f"고객 {cust_no}")


@app.get("/customers", operation_id="listCustomers", summary="고객 목록", dependencies=AUTH,
         description="identity_token 을 주면 그 토큰의 고객만 돌려준다 (다른 시스템의 사람과 동일인 대조).")
def list_customers(identity_token: str | None = Query(None, description="동일인 대조 토큰 (예: TKN-A)"), limit: int = LIMIT):
    w, p = where({"identity_token": identity_token})
    with db() as conn:
        return rows(conn, CUSTOMER + w + " ORDER BY cust_no LIMIT %s", (*p, limit))


@app.get("/policies/{policy_id}", operation_id="getPolicy", summary="계약 조회 (역할·보장 포함)", dependencies=AUTH,
         description="내부 계약 ID(예: PO-001)로 계약 1건과 그 계약의 역할 목록, 보장 목록을 돌려준다.")
def get_policy(policy_id: str):
    with db() as conn:
        policy = one(conn, POLICY + " WHERE policy_id = %s", (policy_id,), f"계약 {policy_id}")
        policy["roles"] = rows(conn, ROLE + " WHERE policy_id = %s ORDER BY role_id", (policy_id,))
        policy["coverages"] = rows(conn, COVERAGE + " WHERE c.policy_id = %s ORDER BY c.coverage_id", (policy_id,))
        return policy


@app.get("/policies", operation_id="listPolicies", summary="계약 목록", dependencies=AUTH,
         description="policy_number(대외 계약 번호, 예: TEST-POLICY-001)를 주면 그 계약만 돌려준다.")
def list_policies(policy_number: str | None = Query(None, description="대외 계약 번호"), limit: int = LIMIT):
    w, p = where({"policy_number": policy_number})
    with db() as conn:
        return rows(conn, POLICY + w + " ORDER BY policy_id LIMIT %s", (*p, limit))


@app.get("/coverages/{coverage_id}", operation_id="getCoverage", summary="보장 조회", dependencies=AUTH,
         description="보장 ID(예: CV-001)로 보장 버전 1건을 돌려준다. 일당 금액, 최대 일수, 대기 기간, 적용 규칙을 담는다.")
def get_coverage(coverage_id: str):
    with db() as conn:
        return one(conn, COVERAGE + " WHERE c.coverage_id = %s", (coverage_id,), f"보장 {coverage_id}")


@app.get("/coverages", operation_id="listCoverages", summary="보장 목록", dependencies=AUTH,
         description="접수 시스템이 쓰는 (대외 계약 번호, 보장 코드)로 보장을 찾는다.")
def list_coverages(policy_number: str | None = Query(None, description="대외 계약 번호"),
                   coverage_code: str | None = Query(None, description="보장 코드 (예: INPATIENT-DAILY-A)"),
                   limit: int = LIMIT):
    w, p = where({"p.policy_number": policy_number, "c.coverage_code": coverage_code})
    with db() as conn:
        return rows(conn, COVERAGE + w + " ORDER BY c.coverage_id LIMIT %s", (*p, limit))
