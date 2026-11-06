-- T14: 날짜 오류 — 입원 03-13, 퇴원 03-10 (DB가 막지 않는다) (명세 11.2절). 사건과 확인된 증빙을 함께 바꾼다 (11.1절).
UPDATE review.insurance_event SET admission_date = '2026-03-13', discharge_date = '2026-03-10' WHERE event_id = 'EV-001';
UPDATE review.document_verification
   SET verified_facts = verified_facts || '{"admission_date": "2026-03-13", "discharge_date": "2026-03-10"}'
 WHERE doc_id = 'DC-001';
