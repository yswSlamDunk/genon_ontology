-- 기본 데이터 세트 B0 — 명세 10.1절. 각 테스트 전에 reset.sh가 이 상태로 되돌린다.
-- 평가·심사 업무·지급 지시·지급 내역은 없다 ("기본 데이터에는 평가·심사 업무·지급 지시가 없다").
-- 문서·규칙 해시는 reset.sh가 실제 파일에서 계산해 :doc_dc001_hash, :rule_rv001_hash 로 넘긴다.
-- 평가 로직 해시(:logic_hash)는 03_systems/services/evaluation.py의 SHA-256이다 (서버_설계서.md 7.4절).
-- 같은 사람·계약·사고가 시스템마다 다른 식별자로 들어 있다 (명세 1절). 대응표는 02_data/README.md.

BEGIN;

-- 계약 시스템 ---------------------------------------------------------------
INSERT INTO contract.customer (cust_no, display_name, identity_token) VALUES
    ('C-10001', '가상 인물 A', 'TKN-A'),   -- 명세 PT-001: 계약자
    ('C-10002', '가상 인물 B', 'TKN-B');   -- 명세 PT-002: 피보험자·수익자

INSERT INTO contract.policy (policy_id, policy_number, contract_from, contract_to, administrative_status) VALUES
    ('PO-001', 'TEST-POLICY-001', '2026-01-01', '2027-01-01', 'ACTIVE');

INSERT INTO contract.policy_role (role_id, policy_id, cust_no, role_type, valid_from, valid_to) VALUES
    ('PR-001', 'PO-001', 'C-10001', 'POLICYHOLDER', '2026-01-01', '2027-01-01'),
    ('PR-002', 'PO-001', 'C-10002', 'INSURED',      '2026-01-01', '2027-01-01'),
    ('PR-003', 'PO-001', 'C-10002', 'BENEFICIARY',  '2026-01-01', '2027-01-01');

INSERT INTO contract.coverage (coverage_id, policy_id, coverage_code, version, valid_from, valid_to,
                               daily_amount_krw, max_days, waiting_days, rule_code, rule_version, benefit_period_key) VALUES
    ('CV-001', 'PO-001', 'INPATIENT-DAILY-A', '1.0', '2026-01-01', '2027-01-01',
     100000, 5, 30, 'INPATIENT-DAILY', '1.0', '2026-01-01/2027-01-01');

-- 접수 시스템 ---------------------------------------------------------------
INSERT INTO intake.claimant (claimant_no, display_name, identity_token) VALUES
    ('IP-0001', '가상 인물 A', 'TKN-A'),
    ('IP-0002', '가상 인물 B', 'TKN-B');

INSERT INTO intake.claim_receipt (receipt_no, request_key, policy_number, coverage_code, submitter_no, patient_no,
                                  accident_no, provider_code, admission_date, discharge_date, received_at) VALUES
    ('RC-0001', 'REQ-B0-0001', 'TEST-POLICY-001', 'INPATIENT-DAILY-A', 'IP-0001', 'IP-0002',
     'ACC-0001', 'H-001', '2026-03-10', '2026-03-13', '2026-03-14 10:00:00+09');

INSERT INTO intake.document (doc_id, document_type, storage_ref, content_hash, extracted_facts, uploaded_at) VALUES
    ('DC-001', 'HOSPITALIZATION_CERTIFICATE', '02_data/seed/documents/DC-001.txt', :'doc_dc001_hash',
     '{"insured": {"value": "TKN-B", "confidence": 0.98},
       "provider_code": {"value": "H-001", "confidence": 0.99},
       "admission_date": {"value": "2026-03-10", "confidence": 0.97},
       "discharge_date": {"value": "2026-03-13", "confidence": 0.97}}',
     '2026-03-14 10:00:00+09');

INSERT INTO intake.receipt_document (attachment_id, receipt_no, doc_id, attached_at) VALUES
    ('AT-0001', 'RC-0001', 'DC-001', '2026-03-14 10:00:00+09');

-- 심사 시스템 ---------------------------------------------------------------
INSERT INTO review.rule_set_version (rule_set_id, rule_code, version, published_at, clause_reference,
                                     definition_ref, definition_hash, logic_hash, required_document_types) VALUES
    ('RV-001', 'INPATIENT-DAILY', '1.0', '2026-01-01 00:00:00+09', 'TEST-TERMS-A-1.0',
     '02_data/seed/rules/INPATIENT-DAILY-1.0.yaml', :'rule_rv001_hash', NULLIF(:'logic_hash', ''),
     '{HOSPITALIZATION_CERTIFICATE}');

INSERT INTO review.insurance_event (event_id, intake_accident_no, subject_claimant_no, provider_code,
                                    admission_date, discharge_date, fact_status) VALUES
    ('EV-001', 'ACC-0001', 'IP-0002', 'H-001', '2026-03-10', '2026-03-13', 'VERIFIED');

INSERT INTO review.document_verification (doc_id, supports_event_id, verification_status, verified_facts,
                                          verified_by, verified_at) VALUES
    ('DC-001', 'EV-001', 'VERIFIED',
     '{"insured": "IP-0002", "provider_code": "H-001", "admission_date": "2026-03-10", "discharge_date": "2026-03-13"}',
     'reviewer-01', '2026-03-14 11:00:00+09');

INSERT INTO review.claim (claim_id, receipt_no, policy_id, coverage_id, event_id, submitted_by_claimant_no,
                          submitted_at, status, assigned_reviewer_id) VALUES
    ('CL-001', 'RC-0001', 'PO-001', 'CV-001', 'EV-001', 'IP-0001',
     '2026-03-14 10:00:00+09', 'RECEIVED', 'reviewer-01');

-- 지급 시스템: B0에는 지급 내역이 없다 ---------------------------------------

COMMIT;
