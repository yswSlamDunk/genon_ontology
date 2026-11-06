-- SECOND: 두 번째 청구 B의 재료 (T18·T19). 별개 사건 EV-902의 3일 입원, 확인된 입퇴원확인서 DC-902.
-- T19는 이 파일 대신 같은 사건으로 등록한다 (scenario_test.py 참고)
INSERT INTO intake.claim_receipt (receipt_no, request_key, policy_number, coverage_code, submitter_no, patient_no, accident_no,
                                  provider_code, admission_date, discharge_date, received_at)
VALUES ('RC-0902', 'REQ-SECOND-0902', 'TEST-POLICY-001', 'INPATIENT-DAILY-A', 'IP-0001', 'IP-0002', 'ACC-0902', 'H-002',
        '2026-04-10', '2026-04-13', '2026-04-14 10:00:00+09');
INSERT INTO intake.document (doc_id, document_type, storage_ref, content_hash, uploaded_at)
VALUES ('DC-902', 'HOSPITALIZATION_CERTIFICATE', 'fixture://DC-902', 'fixture-hash-dc902', '2026-04-14 10:00:00+09');
INSERT INTO intake.receipt_document (attachment_id, receipt_no, doc_id, attached_at)
VALUES ('AT-0902', 'RC-0902', 'DC-902', '2026-04-14 10:00:00+09');
INSERT INTO review.insurance_event (event_id, intake_accident_no, subject_claimant_no, provider_code, admission_date, discharge_date, fact_status)
VALUES ('EV-902', 'ACC-0902', 'IP-0002', 'H-002', '2026-04-10', '2026-04-13', 'VERIFIED');
INSERT INTO review.document_verification (doc_id, supports_event_id, verification_status, verified_facts, verified_by, verified_at)
VALUES ('DC-902', 'EV-902', 'VERIFIED',
        '{"insured": "IP-0002", "provider_code": "H-002", "admission_date": "2026-04-10", "discharge_date": "2026-04-13"}',
        'reviewer-01', '2026-04-14 11:00:00+09');
INSERT INTO review.claim (claim_id, receipt_no, policy_id, coverage_id, event_id, submitted_by_claimant_no, submitted_at, status,
                          assigned_reviewer_id)
VALUES ('CL-902', 'RC-0902', 'PO-001', 'CV-001', 'EV-902', 'IP-0001', '2026-04-14 10:00:00+09', 'RECEIVED', 'reviewer-01');
