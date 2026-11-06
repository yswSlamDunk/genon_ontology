-- T11: 피보험자 불일치 — 사건·증빙의 사람을 PT-001(접수 IP-0001)로. 계약 역할은 그대로
UPDATE review.insurance_event SET subject_claimant_no = 'IP-0001' WHERE event_id = 'EV-001';
UPDATE review.document_verification SET verified_facts = verified_facts || '{"insured": "IP-0001"}' WHERE doc_id = 'DC-001';
UPDATE intake.claim_receipt SET patient_no = 'IP-0001' WHERE receipt_no = 'RC-0001';
