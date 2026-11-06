-- T15: 규칙 누락 — CV-001이 가리키는 규칙 (INPATIENT-DAILY, 1.0)을 찾을 수 없다
DELETE FROM review.rule_set_version WHERE rule_set_id = 'RV-001';
