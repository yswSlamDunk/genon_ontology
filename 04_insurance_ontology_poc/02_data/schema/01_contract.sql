-- 계약 시스템 (contract) — 명세 1절 "계약 시스템에는 계약과 보장이 있다", 12.1절 고객 마스터·계약·가입 담보
-- 읽기 전용 원천이다(명세 12.2절: 계약·보장 정보는 화면에서 임의 수정하지 않는다). 액션이 쓰지 않는다.
-- 식별자: 고객은 이 시스템의 고객번호(C-…)를 쓴다. 접수 시스템의 청구인 번호(IP-…)와 다르다.

CREATE SCHEMA contract;
COMMENT ON SCHEMA contract IS '계약 시스템: 고객 마스터, 계약, 계약상 역할, 가입 보장';

CREATE TABLE contract.customer (
    cust_no          text PRIMARY KEY,                 -- 계약 시스템 고객번호
    party_type       text NOT NULL DEFAULT 'PERSON' CHECK (party_type IN ('PERSON')),
    display_name     text NOT NULL,                    -- 가상 인물만
    identity_token   text NOT NULL UNIQUE,             -- 시스템 간 동일인 대조용 가상 토큰
    created_at       timestamptz NOT NULL DEFAULT now(),
    updated_at       timestamptz NOT NULL DEFAULT now(),
    revision         integer NOT NULL DEFAULT 1
);
COMMENT ON TABLE contract.customer IS '고객 마스터 → 온톨로지 Party';

CREATE TABLE contract.policy (
    policy_id              text PRIMARY KEY,           -- 내부 계약 ID (PO-…)
    policy_number          text NOT NULL UNIQUE,       -- 대외 계약 번호. 접수 시스템은 이 번호로 계약을 가리킨다
    contract_from          date NOT NULL,
    contract_to            date NOT NULL,              -- 종료일 제외
    administrative_status  text NOT NULL CHECK (administrative_status IN ('ACTIVE', 'EXPIRED')),
    created_at             timestamptz NOT NULL DEFAULT now(),
    updated_at             timestamptz NOT NULL DEFAULT now(),
    revision               integer NOT NULL DEFAULT 1,
    CHECK (contract_from < contract_to)
);
COMMENT ON TABLE contract.policy IS '보험 계약 → 온톨로지 Policy';

CREATE TABLE contract.policy_role (
    role_id      text PRIMARY KEY,                     -- PR-…
    policy_id    text NOT NULL REFERENCES contract.policy(policy_id),
    cust_no      text NOT NULL REFERENCES contract.customer(cust_no),
    role_type    text NOT NULL CHECK (role_type IN ('POLICYHOLDER', 'INSURED', 'BENEFICIARY')),
    valid_from   date NOT NULL,
    valid_to     date NOT NULL,                        -- 종료일 제외
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now(),
    revision     integer NOT NULL DEFAULT 1,
    CHECK (valid_from < valid_to)
);
COMMENT ON TABLE contract.policy_role IS '계약상 역할 → 온톨로지 PolicyRole (has_role, role_of)';

CREATE TABLE contract.coverage (
    coverage_id         text PRIMARY KEY,              -- CV-…
    policy_id           text NOT NULL REFERENCES contract.policy(policy_id),
    coverage_code       text NOT NULL,                 -- 접수 시스템은 계약 번호 + 이 코드로 보장을 가리킨다
    version             text NOT NULL,
    valid_from          date NOT NULL,
    valid_to            date NOT NULL,                 -- 종료일 제외
    daily_amount_krw    integer NOT NULL CHECK (daily_amount_krw > 0),
    max_days            integer NOT NULL CHECK (max_days >= 0),
    waiting_days        integer NOT NULL CHECK (waiting_days >= 0),
    rule_code           text NOT NULL,                 -- 심사 시스템의 규칙 버전을 (코드, 버전)으로 가리킨다
    rule_version        text NOT NULL,
    benefit_period_key  text NOT NULL,                 -- 한도 집계 키의 기간 부분
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),
    revision            integer NOT NULL DEFAULT 1,
    UNIQUE (policy_id, coverage_code, version),
    CHECK (valid_from < valid_to)
);
COMMENT ON TABLE contract.coverage IS '가입 보장 버전 → 온톨로지 CoverageVersion (has_coverage, evaluated_by_rule)';
