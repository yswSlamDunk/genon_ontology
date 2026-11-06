-- T08: 동일 사건 다른 청구 — 같은 EV-001·CV-001에 APPROVED 청구와 3일 예약 (명세 11.2·11.3절)
INSERT INTO intake.claim_receipt (receipt_no, request_key, policy_number, coverage_code, submitter_no, patient_no, accident_no,
                                  provider_code, admission_date, discharge_date, received_at)
VALUES ('RC-0901', 'REQ-T08-0901', 'TEST-POLICY-001', 'INPATIENT-DAILY-A', 'IP-0001', 'IP-0002', 'ACC-0001', 'H-001', '2026-03-10', '2026-03-13',
        '2026-02-20 10:00:00+09');
INSERT INTO review.claim (claim_id, receipt_no, policy_id, coverage_id, event_id, submitted_by_claimant_no, submitted_at, status,
                          assigned_reviewer_id)
VALUES ('CL-901', 'RC-0901', 'PO-001', 'CV-001', 'EV-001', 'IP-0001', '2026-02-20 10:00:00+09', 'APPROVED', 'reviewer-01');
INSERT INTO review.assessment (assessment_id, claim_id, rule_set_id, evaluated_at, input_snapshot, input_hash, rule_results,
                               recommendation, eligible_days, candidate_amount_krw, reason_codes)
VALUES ('AS-901', 'CL-901', 'RV-001', '2026-02-20 11:00:00+09', '{"fixture": "T08"}', 'fixture-T08', '[]', 'PAYABLE_CANDIDATE',
        3, 3 * 100000, '{}');
UPDATE review.claim SET current_assessment_id = 'AS-901' WHERE claim_id = 'CL-901';
INSERT INTO review.payment_order (payment_order_id, claim_id, assessment_id, beneficiary_cust_no, insured_cust_no, policy_id,
                                  coverage_id, benefit_period_key, reserved_days, amount_krw, status, payment_key, decided_by, decided_at)
VALUES ('PY-901', 'CL-901', 'AS-901', 'C-10002', 'C-10002', 'PO-001', 'CV-001', '2026-01-01/2027-01-01', 3, 3 * 100000,
        'RESERVED', 'PK-PY-901', 'reviewer-01', '2026-02-20 12:00:00+09');
