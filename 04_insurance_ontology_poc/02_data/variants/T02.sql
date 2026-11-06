-- T02: 대기 기간 미충족 — 입원 01-30, 퇴원 02-02 (명세 11.2절). 사건과 확인된 증빙을 함께 바꾼다 (11.1절).
UPDATE review.insurance_event SET admission_date = '2026-01-30', discharge_date = '2026-02-02' WHERE event_id = 'EV-001';
UPDATE review.document_verification
   SET verified_facts = verified_facts || '{"admission_date": "2026-01-30", "discharge_date": "2026-02-02"}'
 WHERE doc_id = 'DC-001';
