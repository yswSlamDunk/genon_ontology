-- T29: 계약 연결 오류 — 다른 계약 PO-002와 그 보장 CV-002를 둔다. CL 등록 때 CV-002를 지정하면 거절돼야 한다
INSERT INTO contract.policy (policy_id, policy_number, contract_from, contract_to, administrative_status)
VALUES ('PO-002', 'TEST-POLICY-002', '2026-01-01', '2027-01-01', 'ACTIVE');
INSERT INTO contract.coverage (coverage_id, policy_id, coverage_code, version, valid_from, valid_to, daily_amount_krw, max_days,
                               waiting_days, rule_code, rule_version, benefit_period_key)
VALUES ('CV-002', 'PO-002', 'INPATIENT-DAILY-A', '1.0', '2026-01-01', '2027-01-01', 100000, 5, 30, 'INPATIENT-DAILY', '1.0',
        '2026-01-01/2027-01-01');
