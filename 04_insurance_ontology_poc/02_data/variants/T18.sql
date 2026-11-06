-- T18: 동시 승인·한도 — 기존 지급 2일 (+ 시나리오가 별개 사건의 3일 청구 B를 만든다) (명세 11.2·11.3절)
INSERT INTO intake.claim_receipt (receipt_no, request_key, policy_number, coverage_code, submitter_no, patient_no, accident_no,
                                  provider_code, admission_date, discharge_date, received_at)
VALUES ('RC-0901', 'REQ-T18-0901', 'TEST-POLICY-001', 'INPATIENT-DAILY-A', 'IP-0001', 'IP-0002', 'ACC-0901', 'H-001', '2026-02-10', '2026-02-12',
        '2026-02-20 10:00:00+09');
INSERT INTO review.insurance_event (event_id, intake_accident_no, subject_claimant_no, provider_code, admission_date, discharge_date, fact_status)
VALUES ('EV-901', 'ACC-0901', 'IP-0002', 'H-001', '2026-02-10', '2026-02-12', 'VERIFIED');
INSERT INTO review.claim (claim_id, receipt_no, policy_id, coverage_id, event_id, submitted_by_claimant_no, submitted_at, status,
                          assigned_reviewer_id)
VALUES ('CL-901', 'RC-0901', 'PO-001', 'CV-001', 'EV-901', 'IP-0001', '2026-02-20 10:00:00+09', 'PAID', 'reviewer-01');
INSERT INTO review.assessment (assessment_id, claim_id, rule_set_id, evaluated_at, input_snapshot, input_hash, rule_results,
                               recommendation, eligible_days, candidate_amount_krw, reason_codes)
VALUES ('AS-901', 'CL-901', 'RV-001', '2026-02-20 11:00:00+09', '{"fixture": "T18"}', 'fixture-T18', '[]', 'PAYABLE_CANDIDATE',
        2, 2 * 100000, '{}');
UPDATE review.claim SET current_assessment_id = 'AS-901' WHERE claim_id = 'CL-901';
INSERT INTO review.payment_order (payment_order_id, claim_id, assessment_id, beneficiary_cust_no, insured_cust_no, policy_id,
                                  coverage_id, benefit_period_key, reserved_days, amount_krw, status, payment_key, decided_by, decided_at)
VALUES ('PY-901', 'CL-901', 'AS-901', 'C-10002', 'C-10002', 'PO-001', 'CV-001', '2026-01-01/2027-01-01', 2, 2 * 100000,
        'PAID', 'PK-PY-901', 'reviewer-01', '2026-02-20 12:00:00+09');
