"""평가 엔진 — 명세 7절 (R01–R07, 결과 집계, 금액 계산). 서버_설계서.md 7.4절.

이 파일은 입력 스냅샷만 보고 계산한다 (DB·네트워크 없음). 그래서 같은 스냅샷이면 언제 계산해도 결과가 같다 (T26).
이 파일의 SHA-256이 평가 로직 해시(logic_hash)다. 바꾸면 02_data/reset.sh 가 새 해시를 RV-001에 넣는다.

스냅샷 구조 (review.py build_snapshot 이 만든다. 날짜는 ISO 문자열):
  claim       {claim_id, policy_id, coverage_id, event_id, ...}
  coverage    {coverage_id, policy_id, valid_from, valid_to, daily_amount_krw, max_days, waiting_days, benefit_period_key, ...}
  rule_set    {rule_set_id, required_document_types, definition_hash, logic_hash, ...}
  roles       [{role_id, cust_no, role_type, valid_from, valid_to}]
  event       {event_id, subject_claimant_no, provider_code, admission_date, discharge_date, fact_status}
  subject     {claimant_no, identity_token, cust_nos: [...]}           사건 주체의 계약 시스템 고객 (동일인 매핑)
  documents   [{doc_id, document_type, content_hash, verification_status, verified_facts}]   현재 연결된 서류
  duplicates  [{claim_id, status, payment_order_status}]               같은 사건·같은 보장의 다른 청구
  limit       {insured_cust_no, orders: [{payment_order_id, claim_id, status, reserved_days}]}   같은 한도 키의 다른 청구
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from typing import Any

RULE_IDS = ["R01_IDENTITY_MATCH", "R02_COVERAGE_PERIOD", "R03_WAITING_PERIOD", "R04_EVIDENCE_COMPLETE",
            "R05_POSITIVE_STAY", "R06_DUPLICATE_CLEAR", "R07_LIMIT_AVAILABLE"]

# 명세 7.3절 1번: 수동 검토로 보내는 사유
MANUAL_CODES = {"INVALID_DATES", "FACT_CONFLICT", "PERIOD_CROSSING", "DUPLICATE_REVIEW", "DEPENDENCY_UNAVAILABLE"}
# 명세 5.4절: 사유 → 심사 업무 유형 (확인된 조건 미충족은 업무 없음)
TASK_TYPE = {
    "MISSING_DOCUMENT": "EVIDENCE_REQUEST",
    "FACT_CONFLICT": "FACT_REVIEW",
    "UNCONFIRMED_FACT": "FACT_REVIEW",
    "INVALID_DATES": "DATA_REPAIR",
    "DEPENDENCY_UNAVAILABLE": "DATA_REPAIR",
    "PERIOD_CROSSING": "PERIOD_REVIEW",
    "DUPLICATE_REVIEW": "DUPLICATE_REVIEW",
}
NOTE = {
    "MISSING_DOCUMENT": "필수 증빙({ref})이 없거나 확인되지 않았습니다",
    "FACT_CONFLICT": "증빙 확인값과 사건 사실이 다릅니다 ({ref})",
    "UNCONFIRMED_FACT": "핵심 사실이 확인되지 않았습니다 ({ref})",
    "INVALID_DATES": "입퇴원일이 역전됐습니다 ({ref})",
    "DEPENDENCY_UNAVAILABLE": "필수 조회를 하지 못했습니다 ({ref})",
    "PERIOD_CROSSING": "입원이 보장 종료 경계를 넘습니다 ({ref})",
    "DUPLICATE_REVIEW": "같은 사건·보장에 유효한 다른 청구가 있습니다 ({ref})",
}
VALID_ORDER = {"RESERVED", "REQUESTED", "UNKNOWN", "FAILED", "PAID"}   # 예약·지급으로 집계하는 지급 지시 (명세 9.2절)
FACT_FIELDS = ("insured", "provider_code", "admission_date", "discharge_date")


def _d(value: Any) -> dt.date | None:
    return dt.date.fromisoformat(value) if value else None


def _result(rule_id: str, result: str, issues: list[dict] | None = None, observed: dict | None = None,
            evidence: list[str] | None = None) -> dict:
    issues = issues or []
    return {"rule_id": rule_id, "result": result, "reason_code": issues[0]["code"] if issues else None,
            "observed_values": observed or {}, "evidence_refs": evidence or [], "issues": issues}


def _issue(code: str, ref: str, cause: str | None = None) -> dict:
    return {"code": code, "related_ref": ref, "cause": cause}


def evaluate(s: dict) -> dict:
    """스냅샷 → {rule_results, recommendation, eligible_days, candidate_amount_krw, reason_codes, tasks, figures}."""
    cov, ev = s["coverage"], s["event"]
    adm, dis = _d(ev.get("admission_date")), _d(ev.get("discharge_date"))
    facts_ok = ev["fact_status"] == "VERIFIED" and adm is not None and dis is not None
    vf, vt = _d(cov["valid_from"]), _d(cov["valid_to"])

    def fact_unknown(rule_id: str) -> dict:
        if ev["fact_status"] == "CONFLICT":
            return _result(rule_id, "UNKNOWN", [_issue("FACT_CONFLICT", ev["event_id"], "EVENT_CONFLICT")],
                           {"fact_status": ev["fact_status"]}, [ev["event_id"]])
        return _result(rule_id, "UNKNOWN", [_issue("UNCONFIRMED_FACT", ev["event_id"], "EVENT_UNVERIFIED")],
                       {"fact_status": ev["fact_status"]}, [ev["event_id"]])

    results: list[dict] = []

    # R01 IDENTITY_MATCH — 사건의 사람과 입원일 기준 계약 피보험자
    if not facts_ok:
        results.append(fact_unknown("R01_IDENTITY_MATCH"))
    else:
        insured = [r for r in s["roles"] if r["role_type"] == "INSURED" and _d(r["valid_from"]) <= adm < _d(r["valid_to"])]
        as_of = ev["admission_date"]
        if not insured and not (vf <= adm < vt):
            # 입원일이 보장 기간 밖이면 그 날짜의 역할이 없는 것이 당연하다. 보장 밖은 R02가 FAIL 로 판정하므로,
            # 동일인 여부는 계약의 피보험자 역할 전체로 본다 (T05: 미확인이 아니라 부지급 후보)
            insured = [r for r in s["roles"] if r["role_type"] == "INSURED"]
            as_of = "POLICY_INSURED_ROLES"
        subject = s["subject"]["cust_nos"]
        obs = {"event_subject": ev["subject_claimant_no"], "subject_cust_nos": subject,
               "insured_cust_nos": [r["cust_no"] for r in insured], "as_of": as_of}
        refs = [ev["event_id"], *(r["role_id"] for r in insured)]
        if not subject:
            results.append(_result("R01_IDENTITY_MATCH", "UNKNOWN",
                                   [_issue("UNCONFIRMED_FACT", "IDENTITY", "IDENTITY_UNMAPPED")], obs, refs))
        elif not insured:
            results.append(_result("R01_IDENTITY_MATCH", "UNKNOWN",
                                   [_issue("UNCONFIRMED_FACT", "INSURED_ROLE", "NO_INSURED_ROLE")], obs, refs))
        elif any(r["cust_no"] in subject for r in insured):
            results.append(_result("R01_IDENTITY_MATCH", "PASS", None, obs, refs))
        else:
            results.append(_result("R01_IDENTITY_MATCH", "FAIL", [_issue("IDENTITY_MISMATCH", ev["event_id"])], obs, refs))

    # R02 COVERAGE_PERIOD — 입원일이 [시작, 종료) 안, 퇴원일 ≤ 종료
    if not facts_ok:
        results.append(fact_unknown("R02_COVERAGE_PERIOD"))
    else:
        obs = {"admission_date": ev["admission_date"], "discharge_date": ev["discharge_date"],
               "coverage_from": cov["valid_from"], "coverage_to": cov["valid_to"]}
        if not (vf <= adm < vt):
            results.append(_result("R02_COVERAGE_PERIOD", "FAIL", [_issue("OUTSIDE_COVERAGE", cov["coverage_id"])], obs,
                                   [cov["coverage_id"]]))
        elif dis > vt:
            results.append(_result("R02_COVERAGE_PERIOD", "UNKNOWN", [_issue("PERIOD_CROSSING", cov["coverage_id"])], obs,
                                   [cov["coverage_id"]]))
        else:
            results.append(_result("R02_COVERAGE_PERIOD", "PASS", None, obs, [cov["coverage_id"]]))

    # R03 WAITING_PERIOD — 입원일 ≥ 보장 시작 + 대기 일수
    waiting_end = vf + dt.timedelta(days=cov["waiting_days"])
    if not facts_ok:
        results.append(fact_unknown("R03_WAITING_PERIOD"))
    else:
        obs = {"admission_date": ev["admission_date"], "waiting_end_date": waiting_end.isoformat()}
        if adm >= waiting_end:
            results.append(_result("R03_WAITING_PERIOD", "PASS", None, obs, [cov["coverage_id"]]))
        else:
            results.append(_result("R03_WAITING_PERIOD", "FAIL", [_issue("WAITING_NOT_MET", cov["coverage_id"])], obs,
                                   [cov["coverage_id"]]))

    # R04 EVIDENCE_COMPLETE — 필수 서류 유형마다 확인 완료 서류, 확인값 = 사건 사실
    issues, refs, obs = [], [], {"required_document_types": s["rule_set"]["required_document_types"], "documents": []}
    for doc_type in s["rule_set"]["required_document_types"]:
        docs = [d for d in s["documents"] if d["document_type"] == doc_type]
        verified = [d for d in docs if d["verification_status"] == "VERIFIED"]
        obs["documents"] += [{"doc_id": d["doc_id"], "verification_status": d["verification_status"]} for d in docs]
        refs += [d["doc_id"] for d in docs]
        if not verified:
            issues.append(_issue("MISSING_DOCUMENT", doc_type))
            continue
        if ev["fact_status"] == "CONFLICT":
            issues.append(_issue("FACT_CONFLICT", ev["event_id"], "EVENT_CONFLICT"))
            continue
        if ev["fact_status"] != "VERIFIED":
            continue   # 사건 사실이 아직 없으면 비교할 것이 없다. 사건 쪽 규칙이 UNCONFIRMED_FACT 로 잡는다
        event_facts = {"insured": ev["subject_claimant_no"], "provider_code": ev["provider_code"],
                       "admission_date": ev["admission_date"], "discharge_date": ev["discharge_date"]}
        for d in verified:
            facts = d.get("verified_facts") or {}
            diff = [f for f in FACT_FIELDS if facts.get(f) != event_facts[f]]
            if diff:
                issues.append(_issue("FACT_CONFLICT", d["doc_id"]))
                obs.setdefault("conflicts", []).append({"doc_id": d["doc_id"], "fields": diff})
    issues.sort(key=lambda i: 0 if i["code"] == "FACT_CONFLICT" else 1)
    results.append(_result("R04_EVIDENCE_COMPLETE", "UNKNOWN" if issues else "PASS", issues, obs, refs))

    # R05 POSITIVE_STAY — 퇴원일 > 입원일
    if not facts_ok:
        results.append(fact_unknown("R05_POSITIVE_STAY"))
    else:
        obs = {"admission_date": ev["admission_date"], "discharge_date": ev["discharge_date"]}
        if dis > adm:
            results.append(_result("R05_POSITIVE_STAY", "PASS", None, obs, [ev["event_id"]]))
        elif dis == adm:
            results.append(_result("R05_POSITIVE_STAY", "FAIL", [_issue("ZERO_STAY", ev["event_id"])], obs, [ev["event_id"]]))
        else:
            results.append(_result("R05_POSITIVE_STAY", "UNKNOWN", [_issue("INVALID_DATES", ev["event_id"])], obs,
                                   [ev["event_id"]]))

    # R06 DUPLICATE_CLEAR — 같은 사건·같은 보장의 다른 청구에 유효한 승인·지급이 없음
    dups = [d for d in s["duplicates"]
            if d["status"] in ("APPROVED", "PAID") or (d.get("payment_order_status") in VALID_ORDER)]
    obs = {"other_claims": s["duplicates"]}
    if dups:
        results.append(_result("R06_DUPLICATE_CLEAR", "UNKNOWN", [_issue("DUPLICATE_REVIEW", d["claim_id"]) for d in dups],
                               obs, [d["claim_id"] for d in dups]))
    else:
        results.append(_result("R06_DUPLICATE_CLEAR", "PASS", None, obs, []))

    # R07 LIMIT_AVAILABLE — 잔여 일수 = max(0, 최대 - 지급 - 다른 청구 예약) > 0
    orders = s["limit"]["orders"]
    paid_days = sum(o["reserved_days"] for o in orders if o["status"] == "PAID")
    reserved_other = sum(o["reserved_days"] for o in orders if o["status"] in VALID_ORDER - {"PAID"})
    remaining = max(0, cov["max_days"] - paid_days - reserved_other)
    obs = {"insured_cust_no": s["limit"]["insured_cust_no"], "max_days": cov["max_days"], "paid_days": paid_days,
           "reserved_days_other": reserved_other, "remaining_days": remaining,
           "limit_key": [cov["policy_id"], cov["coverage_id"], s["limit"]["insured_cust_no"], cov["benefit_period_key"]]}
    order_refs = [o["payment_order_id"] for o in orders]
    if s["limit"]["insured_cust_no"] is None:
        results.append(_result("R07_LIMIT_AVAILABLE", "UNKNOWN",
                               [_issue("UNCONFIRMED_FACT", "INSURED_ROLE", "NO_INSURED_ROLE")], obs, order_refs))
    elif remaining > 0:
        results.append(_result("R07_LIMIT_AVAILABLE", "PASS", None, obs, order_refs))
    else:
        results.append(_result("R07_LIMIT_AVAILABLE", "FAIL", [_issue("LIMIT_EXHAUSTED", cov["coverage_id"])], obs, order_refs))

    # 집계 — 명세 7.3절
    all_issues = [i for r in results for i in r["issues"]]
    codes = {i["code"] for i in all_issues}
    unconfirmed = [i for i in all_issues if i["code"] == "UNCONFIRMED_FACT"]
    evidence_can_resolve = "MISSING_DOCUMENT" in codes and all(i["cause"] == "EVENT_UNVERIFIED" for i in unconfirmed)
    if codes & MANUAL_CODES or (unconfirmed and not evidence_can_resolve):
        recommendation = "MANUAL_REVIEW"
    elif "MISSING_DOCUMENT" in codes:
        recommendation = "NEED_INFO"
    elif any(r["result"] == "FAIL" for r in results):
        recommendation = "NOT_PAYABLE_CANDIDATE"
    else:
        recommendation = "PAYABLE_CANDIDATE"

    hospital_days = (dis - adm).days if facts_ok else None
    if recommendation == "PAYABLE_CANDIDATE":
        eligible = min(hospital_days, remaining)
        amount = eligible * cov["daily_amount_krw"]
    elif recommendation == "NOT_PAYABLE_CANDIDATE":
        eligible, amount = 0, 0
    else:
        eligible, amount = None, None   # UNKNOWN 이 있으면 null (0원과 구분)

    tasks, seen = [], set()
    for i in all_issues:
        if i["code"] not in TASK_TYPE:
            continue
        if recommendation == "NEED_INFO" and i["code"] == "UNCONFIRMED_FACT":
            continue   # 서류 보완으로 해소될 미확인은 업무를 따로 만들지 않는다
        key = (TASK_TYPE[i["code"]], i["code"], i["related_ref"])
        if key not in seen:
            seen.add(key)
            tasks.append({"task_type": key[0], "reason_code": key[1], "related_ref": key[2],
                          "reason_note": NOTE[i["code"]].format(ref=i["related_ref"])})

    return {
        "rule_results": [{k: v for k, v in r.items() if k != "issues"} | {"issues": r["issues"]} for r in results],
        "recommendation": recommendation, "eligible_days": eligible, "candidate_amount_krw": amount,
        "reason_codes": sorted(codes), "tasks": tasks,
        "figures": {"hospital_days": hospital_days, "waiting_end_date": waiting_end.isoformat(), "paid_days": paid_days,
                    "reserved_days_other": reserved_other, "remaining_days": remaining},
    }


def _strip(value: Any) -> Any:
    """해시에서 빼는 값: revision, 시각, 청구 상태·현재 평가 (명세 7.4절)."""
    drop = {"revision", "created_at", "updated_at", "status_of_claim", "current_assessment_id", "verified_at"}
    if isinstance(value, dict):
        return {k: _strip(v) for k, v in value.items() if k not in drop}
    if isinstance(value, list):
        return [_strip(v) for v in value]
    return value


def input_hash(snapshot: dict) -> str:
    text = json.dumps(_strip(snapshot), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode()).hexdigest()
