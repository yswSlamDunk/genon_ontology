-- 지급 시스템 (payment) — 명세 1절 "지급 시스템에는 지급 내역이 있다", 12.1절 모의 지급 서비스
-- 외부 지급 시스템을 흉내 낸다. 심사 시스템의 지급 지시를 지급 키(payment_key)로만 안다.
-- 식별자: 지급 요청 번호(PAYREQ-…)와 외부 거래 ID(TX-…)는 이 시스템의 것이다.

CREATE SCHEMA payment;
COMMENT ON SCHEMA payment IS '지급 시스템(모의): 지급 요청과 결과';

CREATE TABLE payment.payment_request (
    request_no               text PRIMARY KEY,         -- 지급 요청 번호
    payment_key              text NOT NULL UNIQUE,     -- review.payment_order.payment_key (재시도에도 같은 키)
    amount_krw               integer NOT NULL CHECK (amount_krw > 0),
    beneficiary_token        text NOT NULL,            -- 가상 계좌 토큰
    status                   text NOT NULL CHECK (status IN ('REQUESTED', 'PAID', 'FAILED')),
    external_transaction_id  text UNIQUE,
    attempt_count            integer NOT NULL DEFAULT 1,
    requested_at             timestamptz NOT NULL,
    completed_at             timestamptz,
    created_at               timestamptz NOT NULL DEFAULT now(),
    updated_at               timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE payment.payment_request IS '모의 지급 내역 → 온톨로지 PaymentOrder의 지급 결과 (payment_key로 대사)';

-- 모의 지급 결과 대기열 (테스트 전용, 서버_설계서.md 7.7절). 비어 있으면 PAID
CREATE TABLE payment.mock_outcome (
    id          serial PRIMARY KEY,
    outcome     text NOT NULL CHECK (outcome IN ('PAID', 'FAILED', 'TIMEOUT', 'LOST_RESPONSE')),
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE SEQUENCE payment.request_seq START 1;
CREATE SEQUENCE payment.transaction_seq START 1;
