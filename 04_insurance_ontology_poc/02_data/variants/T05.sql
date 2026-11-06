-- T05: 보장 밖 입원 — 입원 2027-01-01, 퇴원 01-04 (명세 11.2절). 사건과 확인된 증빙을 함께 바꾼다 (11.1절).
UPDATE review.insurance_event SET admission_date = '2027-01-01', discharge_date = '2027-01-04' WHERE event_id = 'EV-001';
UPDATE review.document_verification
   SET verified_facts = verified_facts || '{"admission_date": "2027-01-01", "discharge_date": "2027-01-04"}'
 WHERE doc_id = 'DC-001';
