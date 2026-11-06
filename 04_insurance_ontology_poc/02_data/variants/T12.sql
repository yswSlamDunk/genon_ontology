-- T12: 기간 경계 초과 — 입원 12-30, 퇴원 2027-01-02 (명세 11.2절). 사건과 확인된 증빙을 함께 바꾼다 (11.1절).
UPDATE review.insurance_event SET admission_date = '2026-12-30', discharge_date = '2027-01-02' WHERE event_id = 'EV-001';
UPDATE review.document_verification
   SET verified_facts = verified_facts || '{"admission_date": "2026-12-30", "discharge_date": "2027-01-02"}'
 WHERE doc_id = 'DC-001';
