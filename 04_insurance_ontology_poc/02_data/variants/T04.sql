-- T04: 보장 종료 경계 — 입원 12-29, 퇴원 2027-01-01 (명세 11.2절). 사건과 확인된 증빙을 함께 바꾼다 (11.1절).
UPDATE review.insurance_event SET admission_date = '2026-12-29', discharge_date = '2027-01-01' WHERE event_id = 'EV-001';
UPDATE review.document_verification
   SET verified_facts = verified_facts || '{"admission_date": "2026-12-29", "discharge_date": "2027-01-01"}'
 WHERE doc_id = 'DC-001';
