-- 접수 시스템 (intake) — 명세 1절 "접수 시스템에는 청구와 첨부 서류가 있다", 12.1절 청구 접수·문서 저장소
-- 접수된 그대로의 원본을 보관한다. 확인된 사실과 심사 상태는 심사 시스템(review)이 관리한다(명세 4.2, 12.2절).
-- 식별자: 사람은 청구인 번호(IP-…), 계약은 대외 계약 번호(policy_number), 사고는 접수 사고번호(ACC-…)로 가리킨다.
--         계약 시스템의 고객번호·내부 계약 ID, 심사 시스템의 사건 ID와 다르다.

CREATE SCHEMA intake;
COMMENT ON SCHEMA intake IS '접수 시스템: 청구인, 청구 접수 원본, 첨부 서류 원문';

CREATE TABLE intake.claimant (
    claimant_no     text PRIMARY KEY,                  -- 접수 시스템 청구인 번호
    display_name    text NOT NULL,
    identity_token  text NOT NULL UNIQUE,              -- 계약 시스템 고객과 같은 사람인지 대조하는 토큰
    created_at      timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE intake.claimant IS '접수 시스템의 사람 기록 → 온톨로지 Party (계약 시스템 고객과 identity_token으로 동일인 판정)';

CREATE TABLE intake.claim_receipt (
    receipt_no         text PRIMARY KEY,               -- 접수 번호 (RC-…)
    request_key        text NOT NULL UNIQUE,           -- 접수 요청 키 (중복 접수 방지)
    policy_number      text NOT NULL,                  -- 대외 계약 번호 (계약 시스템 policy.policy_number)
    coverage_code      text NOT NULL,                  -- 청구한 보장 코드
    submitter_no       text NOT NULL REFERENCES intake.claimant(claimant_no),
    patient_no         text NOT NULL REFERENCES intake.claimant(claimant_no),
    accident_no        text NOT NULL,                  -- 접수 사고번호 (ACC-…)
    provider_code      text,                           -- 신고된 의료기관
    admission_date     date,                           -- 신고된 입원일 (확인 전 값)
    discharge_date     date,                           -- 신고된 퇴원일 (확인 전 값)
    received_at        timestamptz NOT NULL,
    cancelled_at       timestamptz,                    -- 접수 취소 시각 (A01 보상). 행을 지우지 않는다
    cancel_reason      text,
    created_at         timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE intake.claim_receipt IS '청구 접수 원본 → 온톨로지 Claim·InsuranceEvent의 원천 기록';

CREATE TABLE intake.document (
    doc_id           text PRIMARY KEY,                 -- DC-…
    document_type    text NOT NULL CHECK (document_type IN ('HOSPITALIZATION_CERTIFICATE', 'OTHER')),
    storage_ref      text NOT NULL,                    -- 원문 위치 (02_data/seed/documents/…)
    content_hash     text NOT NULL,                    -- 원문 SHA-256
    extracted_facts  jsonb,                            -- 추출값 후보와 신뢰도. 확인값이 아니다
    uploaded_at      timestamptz NOT NULL,
    created_at       timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE intake.document IS '첨부 서류 원문 → 온톨로지 EvidenceDocument (확인값은 review.document_verification)';

CREATE TABLE intake.receipt_document (
    attachment_id           text PRIMARY KEY,          -- 연결 ID (AT-…). 가상 노드의 단일 키
    receipt_no              text NOT NULL REFERENCES intake.claim_receipt(receipt_no),
    doc_id                  text NOT NULL REFERENCES intake.document(doc_id),
    attached_at             timestamptz NOT NULL,
    detached_at             timestamptz,               -- 교체·해제 시각. 행을 지우지 않는다
    detach_reason           text,
    replaces_attachment_id  text REFERENCES intake.receipt_document(attachment_id),  -- 교체로 생긴 연결이면 바뀐 연결
    UNIQUE (receipt_no, doc_id, attached_at)
);
-- 같은 서류를 같은 접수에 두 번 걸어 둘 수 없다 (현재 연결 기준)
CREATE UNIQUE INDEX receipt_document_active ON intake.receipt_document (receipt_no, doc_id) WHERE detached_at IS NULL;
COMMENT ON TABLE intake.receipt_document IS '청구-서류 연결 (N:M) → 온톨로지 has_document';

-- 서버가 만드는 ID (B0가 쓴 번호 다음부터) — 03_systems/서버_설계서.md 7.8절
CREATE SEQUENCE intake.receipt_seq START 2;
CREATE SEQUENCE intake.attachment_seq START 2;
CREATE SEQUENCE intake.document_seq START 2;

-- 쓰기 API의 멱등성 기록 (서버_설계서.md 7.1절). 업무 변경과 같은 트랜잭션으로 남긴다
CREATE TABLE intake.idempotency_record (
    action_type   text NOT NULL,
    actor_id      text NOT NULL,
    idem_key      text NOT NULL,
    request_hash  text NOT NULL,
    response      jsonb,
    created_at    timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (action_type, actor_id, idem_key)
);
