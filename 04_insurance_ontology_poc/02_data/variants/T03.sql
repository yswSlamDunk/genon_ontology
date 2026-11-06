-- T03: 대기 기간 경계 — 입원 01-31, 퇴원 02-03 (명세 11.2절). 사건과 확인된 증빙을 함께 바꾼다 (11.1절).
UPDATE review.insurance_event SET admission_date = '2026-01-31', discharge_date = '2026-02-03' WHERE event_id = 'EV-001';
UPDATE review.document_verification
   SET verified_facts = verified_facts || '{"admission_date": "2026-01-31", "discharge_date": "2026-02-03"}'
 WHERE doc_id = 'DC-001';
