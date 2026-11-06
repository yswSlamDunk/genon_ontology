-- T07: 증빙 충돌 — 사건 퇴원일 03-13, 문서 확인값 03-14
UPDATE review.document_verification SET verified_facts = verified_facts || '{"discharge_date": "2026-03-14"}'
 WHERE doc_id = 'DC-001';
