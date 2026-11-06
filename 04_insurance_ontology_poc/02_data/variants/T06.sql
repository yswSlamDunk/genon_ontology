-- T06: 증빙 누락 — DC-001 연결 제거 (행은 지우지 않고 해제 기록)
UPDATE intake.receipt_document SET detached_at = '2026-03-14 10:30:00+09', detach_reason = 'TEST_T06'
 WHERE attachment_id = 'AT-0001';
