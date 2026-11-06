# 02_data — 가상 업무 DB

명세 1절의 전제("계약·접수·심사·지급 시스템에 데이터가 흩어져 있고, **시스템마다 식별자가 다르다**")를 그대로 만든 PostgreSQL DB입니다. Studio에는 이 DB를 **데이터소스로 연결**해서 씁니다. Studio 안에서는 테이블을 만들거나 데이터를 넣을 수 없기 때문입니다.

업무 시스템 서버(`03_systems/`)가 이 DB를 읽고 씁니다. 서버가 쓰는 보조 테이블(멱등성 기록, 지급 전송 대기, 모의 지급 결과, ID 시퀀스)도 이 스키마에 있습니다(`03_systems/서버_설계서.md` 7.8절).

## 구성

DB 하나(`insurance`) 안에 시스템마다 스키마를 하나씩 둡니다. Studio 예제가 `sample` DB 안에 `erp`, `wms`, `crm`을 둔 것과 같은 방식입니다.

| 스키마 | 시스템 | 테이블 | 온톨로지 Object |
|---|---|---|---|
| `contract` | 계약 시스템 (읽기 전용 원천) | `customer`, `policy`, `policy_role`, `coverage` | Party, Policy, PolicyRole, CoverageVersion |
| `intake` | 접수 시스템 (접수 원본) | `claimant`, `claim_receipt`, `document`, `receipt_document` | Party, Claim·InsuranceEvent의 원천, EvidenceDocument |
| `review` | 심사 시스템 (업무 서비스) | `rule_set_version`, `insurance_event`, `document_verification`, `claim`, `assessment`, `assessment_evidence`, `review_task`, `payment_order`, `action_log` | RuleSetVersion, InsuranceEvent, Claim, Assessment, ReviewTask, PaymentOrder, ActionLog |
| `payment` | 지급 시스템 (모의) | `payment_request` | PaymentOrder의 지급 결과 |

설계 결정:
- **청구의 처리 상태와 지급 지시(예약)는 심사 시스템에** 둡니다. 승인(명세 8.2절)이 둘을 한 트랜잭션으로 바꿔야 하기 때문입니다. 접수 시스템에는 접수된 그대로의 원본만 남깁니다.
- **사건의 확정 사실과 증빙 확인값도 심사 시스템에** 둡니다. 명세 4.2절("확인 Action을 거친 값만 사건의 확정 속성으로"), 12.2절("증빙 확인 … 은 업무 서비스가 관리")을 따른 것입니다.
- 수정할 수 없는 기록(`assessment`, `assessment_evidence`, `action_log`)은 트리거로 수정·삭제를 막습니다 (명세 5.1절).
- 미해결 심사 업무는 같은 (청구, 업무 유형, 사유, 관련 ID)로 두 번 만들 수 없습니다 (명세 5.4절, 부분 유일 인덱스).
- 사건의 날짜 역전은 DB에서 막지 않습니다. T14가 이것을 **평가에서** 데이터 오류로 판정해야 하기 때문입니다.
- 멱등성 기록(`intake`·`review`의 `idempotency_record`, 지급 시스템은 지급 키로 거르므로 없음)과 지급 전송 대기 기록(`review.payment_outbox`, 명세 8.3절)을 둡니다.
- 청구–서류 연결(`intake.receipt_document`)은 단일 키 `attachment_id`를 씁니다. 교체·되돌리기 이력을 행으로 남기고, Studio 가상 노드의 단일 키 조건도 맞춥니다.

## 같은 대상, 다른 식별자 (B0)

온톨로지가 이어 붙여야 하는 대응표입니다. 왼쪽 열은 명세의 ID(온톨로지에서 쓸 ID)입니다.

| 명세 ID | 계약 시스템 | 접수 시스템 | 심사 시스템 | 잇는 방법 |
|---|---|---|---|---|
| PT-001 (계약자 A) | `C-10001` | `IP-0001` | 제출자 `IP-0001` | `identity_token` = `TKN-A` |
| PT-002 (피보험자·수익자 B) | `C-10002` | `IP-0002` | 사건 주체 `IP-0002` | `identity_token` = `TKN-B` |
| PO-001 (계약) | `PO-001` | `TEST-POLICY-001` (대외 계약 번호) | `PO-001` | `policy.policy_number` |
| CV-001 (보장) | `CV-001` | `INPATIENT-DAILY-A` (보장 코드) | `CV-001` | 계약 번호 + `coverage_code` |
| RV-001 (규칙) | `INPATIENT-DAILY` / `1.0` | — | `RV-001` | (`rule_code`, `version`) |
| CL-001 (청구) | — | `RC-0001` (접수 번호) | `CL-001` | `claim.receipt_no` |
| EV-001 (입원 사건) | — | `ACC-0001` (사고번호) | `EV-001` | `insurance_event.intake_accident_no` |
| DC-001 (입퇴원확인서) | — | `DC-001` (원문) | `DC-001` (확인값) | `doc_id` |

B0의 값은 명세 10.1절과 같습니다. 이 데이터로 계산하면 입원 3일, 대기 기간 종료 2026-01-31, 지급 후보 300,000원이 나옵니다(명세 10.3절).

문서와 규칙의 해시는 실제 파일에서 계산합니다: [seed/documents/DC-001.txt](seed/documents/DC-001.txt), [seed/rules/INPATIENT-DAILY-1.0.yaml](seed/rules/INPATIENT-DAILY-1.0.yaml). 평가 로직의 해시(`logic_hash`)는 평가 엔진 파일 `03_systems/services/evaluation.py`에서 계산합니다.

## 계정

| 계정 | 용도 | 권한 |
|---|---|---|
| `ins_reader` | Studio 데이터소스 연결 | 네 스키마 읽기만 |
| `ins_service` | 업무 시스템 서버 (`03_systems`) | 계약 읽기, 접수·심사·지급 읽기·쓰기, 시퀀스 사용 |

비밀번호는 `reset.sh`를 처음 실행할 때 만들어 `.env.local`(권한 600)에 저장합니다. 이 파일은 공유하지 않습니다.

## 실행

이 맥에는 Homebrew로 PostgreSQL 16을 설치했습니다(2026-11-02). 로그인할 때 자동으로 켜집니다(`brew services`).

- 데이터 폴더: `/opt/homebrew/var/postgresql@16`
- 접속: `localhost:5432`만 받습니다. TCP 접속은 비밀번호가 필요하고(scram-sha-256), 관리자 작업은 로컬 소켓(`/tmp`)으로 합니다.
- 켜기·끄기: `brew services start postgresql@16` / `brew services stop postgresql@16`

```bash
# 관리자(맥 사용자 계정)로 로컬 소켓 접속
export PSQL=/opt/homebrew/opt/postgresql@16/bin/psql PGHOST=/tmp PGPORT=5432 PGUSER="$USER"
./reset.sh          # insurance DB를 B0로 (없으면 만든다)
./reset.sh T09      # B0 + variants/T09.sql
./reset.sh T18 SECOND   # 변형 여러 개를 순서대로
```

`reset.sh`는 네 스키마를 지우고 다시 만든 뒤 B0를 넣습니다. **테스트마다 실행**해서 같은 출발점을 만듭니다 (명세 10.1, 11.1절).

### 테스트 변형 (`variants/`)

| 파일 | B0에서 바꾸는 것 |
|---|---|
| `T02`–`T05`, `T12`–`T14` | 사건과 확인된 증빙의 입퇴원일 (명세 11.2절 표의 날짜) |
| `T06` | DC-001 연결 해제 (증빙 누락) |
| `T07` | 증빙 확인값의 퇴원일만 03-14 (충돌) |
| `T08` | 같은 사건 EV-001에 APPROVED 청구 CL-901과 3일 예약 |
| `T09`, `T10`, `T18` | 별개 사건 EV-901 청구의 기존 PAID 3일 / 5일 / 2일 |
| `T11` | 사건·증빙의 사람을 IP-0001(계약자)로 |
| `T15` | 규칙 RV-001 삭제 (규칙 누락) |
| `T29` | 다른 계약 PO-002와 보장 CV-002 |
| `SECOND` | 별개 사건 EV-902의 두 번째 청구 CL-902 (T18) |
| `SAME_EVENT` | 같은 사건 EV-001의 두 번째 청구 CL-902 (T19) |
| `A01` | 계약 역할이 없는 청구인 IP-0003 (접수 권한 검사) |

다른 청구의 기존 지급을 넣는 변형은 접수·사건·청구·평가·지급 지시를 함께 만들어 참조 무결성을 지킵니다(명세 11.1절). 이런 고정 데이터는 `9xx` 번호를 씁니다.

## Studio에 연결

데이터소스 탭의 「＋」에서 PostgreSQL을 고르고, 스키마마다 하나씩 연결합니다. 데이터소스 이름은 시스템 이름과 같게 합니다. 네 개 모두 호스트 `127.0.0.1`, 포트 `5432`, 계정 `ins_reader`이고, 비밀번호는 `.env.local`의 `INS_READER_PASSWORD`입니다.

| 데이터소스 | 데이터베이스 | 스키마 | 계정 |
|---|---|---|---|
| `contract` | `insurance` | `contract` | `ins_reader` |
| `intake` | `insurance` | `intake` | `ins_reader` |
| `review` | `insurance` | `review` | `ins_reader` |
| `payment` | `insurance` | `payment` | `ins_reader` |
