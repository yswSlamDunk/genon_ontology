-- SAME_EVENT: 같은 사건 EV-001·같은 보장의 두 번째 청구 B (T19). 둘 다 미승인. 같은 서류 DC-001을 함께 쓴다 (문서-청구 다대다)
INSERT INTO intake.claim_receipt (receipt_no, request_key, policy_number, coverage_code, submitter_no, patient_no, accident_no,
                                  provider_code, admission_date, discharge_date, received_at)
VALUES ('RC-0902', 'REQ-SAME-0902', 'TEST-POLICY-001', 'INPATIENT-DAILY-A', 'IP-0002', 'IP-0002', 'ACC-0001', 'H-001',
        '2026-03-10', '2026-03-13', '2026-03-15 10:00:00+09');
INSERT INTO intake.receipt_document (attachment_id, receipt_no, doc_id, attached_at)
VALUES ('AT-0902', 'RC-0902', 'DC-001', '2026-03-15 10:00:00+09');
INSERT INTO review.claim (claim_id, receipt_no, policy_id, coverage_id, event_id, submitted_by_claimant_no, submitted_at, status,
                          assigned_reviewer_id)
VALUES ('CL-902', 'RC-0902', 'PO-001', 'CV-001', 'EV-001', 'IP-0002', '2026-03-15 10:00:00+09', 'RECEIVED', 'reviewer-01');
