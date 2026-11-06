-- 계정과 권한. 비밀번호는 reset.sh가 psql 변수(:reader_pw, :service_pw)로 넘긴다 — 파일에 적지 않는다.
--   ins_reader  : Studio 데이터소스 연결용. 네 스키마를 읽기만 한다 (예제의 fabric_ro와 같은 역할)
--   ins_service : 업무 시스템 서버(03_systems)용 (예제의 sample_svc와 같은 역할)

SELECT format('CREATE ROLE ins_reader LOGIN PASSWORD %L', :'reader_pw')
 WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ins_reader') \gexec
SELECT format('ALTER ROLE ins_reader PASSWORD %L', :'reader_pw') \gexec

SELECT format('CREATE ROLE ins_service LOGIN PASSWORD %L', :'service_pw')
 WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ins_service') \gexec
SELECT format('ALTER ROLE ins_service PASSWORD %L', :'service_pw') \gexec

SELECT format('GRANT CONNECT ON DATABASE %I TO ins_reader, ins_service', current_database()) \gexec

GRANT USAGE ON SCHEMA contract, intake, review, payment TO ins_reader, ins_service;
GRANT SELECT ON ALL TABLES IN SCHEMA contract, intake, review, payment TO ins_reader;

-- 서비스는 계약 시스템을 읽기만 한다 (명세 12.2절)
GRANT SELECT ON ALL TABLES IN SCHEMA contract TO ins_service;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA intake, review, payment TO ins_service;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA intake, review, payment TO ins_service;
-- 모의 지급 결과 대기열은 꺼내 쓰면 지운다 (테스트 전용)
GRANT DELETE ON payment.mock_outcome TO ins_service;
