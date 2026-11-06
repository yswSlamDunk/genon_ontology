-- 심사 시스템 (review) — 명세 1절 "심사 시스템에는 담당자의 판단이 있다", 12.1–12.2절 업무 서비스
-- 증빙 확인, 확정 사건, 평가, 심사 업무, 승인·예약, 실행 이력을 관리한다.
-- 청구의 처리 상태와 지급 지시(예약)를 같은 스키마에 둔다: 승인(명세 8.2절)이 둘을 한 트랜잭션으로 바꿔야 하기 때문.
-- 식별자: 청구 CL-…, 사건 EV-…는 이 시스템의 ID다. 접수 번호(RC-…)·사고번호(ACC-…)로 접수 원본을 가리킨다.
--         계약은 계약 시스템의 내부 ID(PO-…, CV-…)로, 사람은 접수 시스템의 청구인 번호(IP-…)로 가리킨다.
--         지급 지시의 수익자·피보험자는 계약 시스템 고객번호(C-…)로 가리킨다(수익자 역할이 계약에 있으므로).

CREATE SCHEMA review;
COMMENT ON SCHEMA review IS '심사 시스템: 규칙 버전, 확정 사건, 증빙 확인, 청구 처리, 평가, 심사 업무, 지급 지시, 실행 이력';

-- 생성 후 수정할 수 없는 기록(명세 5.1절: Assessment, 발행된 RuleSetVersion, ActionLog)
CREATE FUNCTION review.forbid_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION '% 는 생성 후 수정·삭제할 수 없습니다 (명세 5.1절)', TG_TABLE_NAME;
END $$;

CREATE TABLE review.rule_set_version (
    rule_set_id              text PRIMARY KEY,         -- RV-…
    rule_code                text NOT NULL,
    version                  text NOT NULL,
    published_at             timestamptz NOT NULL,
    clause_reference         text NOT NULL,            -- 가상 약관 식별자
    definition_ref           text NOT NULL,            -- 규칙 정의 파일 위치
    definition_hash          text NOT NULL,            -- 규칙 정의 파일 SHA-256
    logic_hash               text,                     -- 평가 로직 코드 해시. 평가 서비스를 만들 때 채운다
    required_document_types  text[] NOT NULL,
    created_at               timestamptz NOT NULL DEFAULT now(),
    UNIQUE (rule_code, version)
);
COMMENT ON TABLE review.rule_set_version IS '심사 규칙 버전 → 온톨로지 RuleSetVersion. 계약 보장은 (rule_code, version)으로 가리킨다';

CREATE TABLE review.insurance_event (
    event_id             text PRIMARY KEY,             -- EV-…
    intake_accident_no   text NOT NULL,                -- 접수 사고번호 (intake.claim_receipt.accident_no)
    subject_claimant_no  text NOT NULL,                -- 입원한 사람 (intake.claimant.claimant_no)
    event_type           text NOT NULL DEFAULT 'HOSPITALIZATION' CHECK (event_type IN ('HOSPITALIZATION')),
    provider_code        text,
    admission_date       date,
    discharge_date       date,
    fact_status          text NOT NULL CHECK (fact_status IN ('UNVERIFIED', 'VERIFIED', 'CONFLICT')),
    created_at           timestamptz NOT NULL DEFAULT now(),
    updated_at           timestamptz NOT NULL DEFAULT now(),
    revision             integer NOT NULL DEFAULT 1,
    CHECK (fact_status <> 'VERIFIED'
           OR (provider_code IS NOT NULL AND admission_date IS NOT NULL AND discharge_date IS NOT NULL))
);
COMMENT ON TABLE review.insurance_event IS '확인된 입원 사건 → 온톨로지 InsuranceEvent (event_subject). 날짜 역전은 막지 않는다: T14가 데이터 오류를 평가로 판정해야 하므로';

CREATE TABLE review.document_verification (
    doc_id               text PRIMARY KEY,             -- intake.document.doc_id
    supports_event_id    text REFERENCES review.insurance_event(event_id),
    verification_status  text NOT NULL CHECK (verification_status IN ('PENDING', 'VERIFIED', 'REJECTED')),
    verified_facts       jsonb,                        -- {insured, provider_code, admission_date, discharge_date}
    verified_by          text,
    verified_at          timestamptz,
    verification_note    text,
    created_at           timestamptz NOT NULL DEFAULT now(),
    updated_at           timestamptz NOT NULL DEFAULT now(),
    revision             integer NOT NULL DEFAULT 1
);
COMMENT ON TABLE review.document_verification IS '증빙의 확인 결과 → 온톨로지 EvidenceDocument의 확인 속성과 supports_event';

CREATE TABLE review.claim (
    claim_id                  text PRIMARY KEY,        -- CL-…
    receipt_no                text NOT NULL UNIQUE,    -- 접수 번호 (intake.claim_receipt)
    policy_id                 text NOT NULL,           -- contract.policy.policy_id
    coverage_id               text NOT NULL,           -- contract.coverage.coverage_id
    event_id                  text NOT NULL REFERENCES review.insurance_event(event_id),
    submitted_by_claimant_no  text NOT NULL,           -- intake.claimant.claimant_no
    submitted_at              timestamptz NOT NULL,
    status                    text NOT NULL CHECK (status IN ('RECEIVED', 'UNDER_REVIEW', 'NEED_INFO',
                                                              'READY_FOR_DECISION', 'APPROVED', 'REJECTED', 'PAID')),
    current_assessment_id     text,                    -- FK는 assessment 생성 뒤 아래에서 건다
    assigned_reviewer_id      text NOT NULL,
    created_at                timestamptz NOT NULL DEFAULT now(),
    updated_at                timestamptz NOT NULL DEFAULT now(),
    revision                  integer NOT NULL DEFAULT 1
);
COMMENT ON TABLE review.claim IS '청구 처리 → 온톨로지 Claim (claimed_under, targets_coverage, concerns_event, submitted_by)';

CREATE TABLE review.assessment (
    assessment_id         text PRIMARY KEY,            -- AS-…
    claim_id              text NOT NULL REFERENCES review.claim(claim_id),
    rule_set_id           text NOT NULL REFERENCES review.rule_set_version(rule_set_id),
    evaluated_at          timestamptz NOT NULL,
    input_snapshot        jsonb NOT NULL,              -- 명세 7.4절 스냅샷
    input_hash            text NOT NULL,
    rule_results          jsonb NOT NULL,              -- [{rule_id, result, reason_code, observed_values, evidence_refs}]
    recommendation        text NOT NULL CHECK (recommendation IN ('PAYABLE_CANDIDATE', 'NOT_PAYABLE_CANDIDATE',
                                                                  'NEED_INFO', 'MANUAL_REVIEW')),
    eligible_days         integer,                     -- UNKNOWN이면 NULL (0과 구분)
    candidate_amount_krw  integer,                     -- UNKNOWN이면 NULL (0원과 구분)
    reason_codes          text[] NOT NULL DEFAULT '{}',
    created_at            timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE review.assessment IS '평가 기록 → 온톨로지 Assessment (has_assessment, applied_rule). 수정 불가';
CREATE TRIGGER assessment_immutable BEFORE UPDATE OR DELETE ON review.assessment
    FOR EACH ROW EXECUTE FUNCTION review.forbid_change();

ALTER TABLE review.claim
    ADD CONSTRAINT claim_current_assessment_fk FOREIGN KEY (current_assessment_id) REFERENCES review.assessment(assessment_id);

CREATE TABLE review.assessment_evidence (
    assessment_id  text NOT NULL REFERENCES review.assessment(assessment_id),
    doc_id         text NOT NULL,                      -- intake.document.doc_id
    content_hash   text NOT NULL,                      -- 평가 당시 문서 해시
    PRIMARY KEY (assessment_id, doc_id)
);
COMMENT ON TABLE review.assessment_evidence IS '평가가 사용한 증빙 → 온톨로지 used_evidence';
CREATE TRIGGER assessment_evidence_immutable BEFORE UPDATE OR DELETE ON review.assessment_evidence
    FOR EACH ROW EXECUTE FUNCTION review.forbid_change();

CREATE TABLE review.review_task (
    task_id       text PRIMARY KEY,                    -- TK-…
    claim_id      text NOT NULL REFERENCES review.claim(claim_id),
    task_type     text NOT NULL CHECK (task_type IN ('EVIDENCE_REQUEST', 'FACT_REVIEW', 'DATA_REPAIR',
                                                     'PERIOD_REVIEW', 'DUPLICATE_REVIEW')),
    reason_code   text NOT NULL,
    related_ref   text NOT NULL DEFAULT '',            -- 관련 문서·사건 ID
    status        text NOT NULL CHECK (status IN ('OPEN', 'RESOLVED')),
    assignee_id   text NOT NULL,
    reason_note   text NOT NULL,                       -- 설명 문장 (명세의 reason)
    resolution    text,
    resolved_by   text,
    resolved_at   timestamptz,
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now(),
    revision      integer NOT NULL DEFAULT 1
);
COMMENT ON TABLE review.review_task IS '심사 업무 → 온톨로지 ReviewTask (has_task)';
-- 미해결 업무 중복 생성 방지 (명세 5.4절)
CREATE UNIQUE INDEX review_task_open_dedupe ON review.review_task (claim_id, task_type, reason_code, related_ref)
    WHERE status = 'OPEN';

CREATE TABLE review.payment_order (
    payment_order_id         text PRIMARY KEY,         -- PY-…
    claim_id                 text NOT NULL UNIQUE REFERENCES review.claim(claim_id),  -- MVP: 청구당 최대 1개
    assessment_id            text NOT NULL REFERENCES review.assessment(assessment_id),
    beneficiary_cust_no      text NOT NULL,            -- contract.customer.cust_no (payable_to)
    insured_cust_no          text NOT NULL,            -- contract.customer.cust_no (consumes_for)
    policy_id                text NOT NULL,            -- 한도 집계 키
    coverage_id              text NOT NULL,            -- 한도 집계 키 (consumes_coverage)
    benefit_period_key       text NOT NULL,            -- 한도 집계 키
    reserved_days            integer NOT NULL CHECK (reserved_days > 0),
    amount_krw               integer NOT NULL CHECK (amount_krw > 0),
    status                   text NOT NULL CHECK (status IN ('RESERVED', 'REQUESTED', 'PAID', 'FAILED', 'UNKNOWN')),
    payment_key              text NOT NULL UNIQUE,     -- 재시도에도 바뀌지 않는 지급 키
    external_transaction_id  text,
    decided_by               text NOT NULL,
    decided_at               timestamptz NOT NULL,
    created_at               timestamptz NOT NULL DEFAULT now(),
    updated_at               timestamptz NOT NULL DEFAULT now(),
    revision                 integer NOT NULL DEFAULT 1
);
COMMENT ON TABLE review.payment_order IS '지급 지시·한도 예약 → 온톨로지 PaymentOrder';

CREATE TABLE review.action_log (
    log_id           text PRIMARY KEY,                 -- AL-…
    action_type      text NOT NULL,
    actor_id         text NOT NULL,
    target_refs      jsonb NOT NULL,                   -- [{type, id}]
    executed_at      timestamptz NOT NULL,
    idempotency_key  text NOT NULL,
    before_hash      text,
    after_hash       text,
    outcome          text NOT NULL CHECK (outcome IN ('SUCCESS', 'REJECTED')),
    reason           text,
    created_at       timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE review.action_log IS '업무 실행 이력 → 온톨로지 ActionLog. 거절도 기록. 수정 불가';
CREATE TRIGGER action_log_immutable BEFORE UPDATE OR DELETE ON review.action_log
    FOR EACH ROW EXECUTE FUNCTION review.forbid_change();

-- 지급 요청 전송 대기 기록 (명세 8.3절: 승인 거래와 함께 저장하고 전달기가 지급 시스템에 보낸다). 업무 Object가 아니다
CREATE TABLE review.payment_outbox (
    outbox_id         text PRIMARY KEY,                -- OB-…
    payment_order_id  text NOT NULL REFERENCES review.payment_order(payment_order_id),
    payment_key       text NOT NULL,
    attempt           integer NOT NULL,
    status            text NOT NULL CHECK (status IN ('PENDING', 'SENT', 'UNKNOWN')),
    response          jsonb,
    created_at        timestamptz NOT NULL DEFAULT now(),
    sent_at           timestamptz,
    UNIQUE (payment_order_id, attempt)
);
COMMENT ON TABLE review.payment_outbox IS '지급 요청 전송 대기 기록 (연계용 저장소, 업무 Object 아님)';

-- 서버가 만드는 ID (B0가 쓴 번호 다음부터) — 03_systems/서버_설계서.md 7.8절
CREATE SEQUENCE review.claim_seq START 2;
CREATE SEQUENCE review.event_seq START 2;
CREATE SEQUENCE review.assessment_seq START 1;
CREATE SEQUENCE review.task_seq START 1;
CREATE SEQUENCE review.payment_order_seq START 1;
CREATE SEQUENCE review.action_log_seq START 1;
CREATE SEQUENCE review.outbox_seq START 1;

-- 쓰기 API의 멱등성 기록 (서버_설계서.md 7.1절)
CREATE TABLE review.idempotency_record (
    action_type   text NOT NULL,
    actor_id      text NOT NULL,
    idem_key      text NOT NULL,
    request_hash  text NOT NULL,
    response      jsonb,
    created_at    timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (action_type, actor_id, idem_key)
);
