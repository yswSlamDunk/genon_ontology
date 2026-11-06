"""네 서버를 인증 붙여 불러 B0 값을 확인한다 (서버_설계서.md 6.4절). 비밀 값은 출력하지 않는다."""

from __future__ import annotations

import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENV = dict(line.split("=", 1) for line in (HERE / ".env.local").read_text().split() if "=" in line)

AUTH = {
    "contract": (18101, {"X-API-Key": ENV["INS_CONTRACT_API_KEY"]}),
    "intake": (18102, {"Authorization": "Basic " + base64.b64encode(ENV["INS_INTAKE_BASIC"].encode()).decode()}),
    "review": (18103, {"Authorization": "Bearer " + ENV["INS_REVIEW_TOKEN"]}),
    "payment": (18104, {"X-Payment-Key": ENV["INS_PAYMENT_API_KEY"]}),
}
EXPECTED_OPS = {"contract": 6, "intake": 11, "review": 24, "payment": 3}

failed = 0


def call(system: str, path: str, auth: bool = True) -> tuple[int, object]:
    port, headers = AUTH[system]
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", headers=headers if auth else {})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


def check(label: str, ok: bool, detail: str = "") -> None:
    global failed
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  — {detail}" if detail and not ok else ""))


for s in AUTH:
    code, _ = call(s, "/health", auth=False)
    check(f"{s}: /health 200 (인증 없이)", code == 200, str(code))
    code, _ = call(s, "/openapi.json", auth=False)
    _, spec = call(s, "/openapi.json")
    ops = [op.get("operationId") for item in spec["paths"].values() for op in item.values()]
    check(f"{s}: operationId {EXPECTED_OPS[s]}개, 모두 있음, /mock 제외", len(ops) == EXPECTED_OPS[s] and all(ops)
          and not any(p.startswith("/mock") for p in spec["paths"]), str(ops))

code, _ = call("review", "/claims/CL-001", auth=False)
check("review: 인증 없이 조회 → 401", code == 401, str(code))
code, _ = call("intake", "/receipts/RC-0001", auth=False)
check("intake: 인증 없이 조회 → 401", code == 401, str(code))

code, c = call("review", "/claims/CL-001")
check("review getClaim CL-001 → RECEIVED, 미해결 업무 0, 지급 지시 없음",
      code == 200 and c["status"] == "RECEIVED" and c["open_task_count"] == 0 and c["payment_order"] is None, str(c))
code, e = call("review", "/events/EV-001")
check("review getInsuranceEvent EV-001 → VERIFIED 2026-03-10~2026-03-13",
      code == 200 and e["fact_status"] == "VERIFIED" and e["admission_date"] == "2026-03-10"
      and e["discharge_date"] == "2026-03-13", str(e))
code, r = call("review", "/rules?rule_code=INPATIENT-DAILY&version=1.0")
check("review listRuleSetVersions (INPATIENT-DAILY, 1.0) → RV-001",
      code == 200 and [x["rule_set_id"] for x in r] == ["RV-001"], str(r))
code, v = call("review", "/documents/DC-001/verification")
check("review getDocumentVerification DC-001 → VERIFIED, EV-001",
      code == 200 and v["verification_status"] == "VERIFIED" and v["supports_event_id"] == "EV-001", str(v))
code, _ = call("review", "/claims/CL-999")
check("review getClaim CL-999 → 404", code == 404, str(code))

code, p = call("contract", "/policies/PO-001")
check("contract getPolicy PO-001 → 역할 3개, 보장 1개",
      code == 200 and len(p["roles"]) == 3 and len(p["coverages"]) == 1, str(p))
code, cv = call("contract", "/coverages?policy_number=TEST-POLICY-001&coverage_code=INPATIENT-DAILY-A")
check("contract listCoverages (TEST-POLICY-001, INPATIENT-DAILY-A) → CV-001, 일당 100000",
      code == 200 and len(cv) == 1 and cv[0]["coverage_id"] == "CV-001" and cv[0]["daily_amount_krw"] == 100000, str(cv))
code, cu = call("contract", "/customers?identity_token=TKN-B")
check("contract listCustomers TKN-B → C-10002", code == 200 and [x["cust_no"] for x in cu] == ["C-10002"], str(cu))

code, rc = call("intake", "/receipts/RC-0001")
check("intake getReceipt RC-0001 → 서류 DC-001 연결",
      code == 200 and [d["doc_id"] for d in rc["documents"] if d["detached_at"] is None] == ["DC-001"], str(rc))
code, cl = call("intake", "/claimants?identity_token=TKN-B")
check("intake listClaimants TKN-B → IP-0002", code == 200 and [x["claimant_no"] for x in cl] == ["IP-0002"], str(cl))

code, pr = call("payment", "/payment-requests")
check("payment listPaymentRequests → 0건 (B0)", code == 200 and pr == [], str(pr))

for s in AUTH:
    _, h = call(s, "/health", auth=False)
    check(f"{s}: 조회 API는 읽기 전용 연결", isinstance(h, dict) and h.get("read_only_queries") is True, str(h))

print(f"\n{'모두 통과' if not failed else f'실패 {failed}개'}")
sys.exit(1 if failed else 0)
