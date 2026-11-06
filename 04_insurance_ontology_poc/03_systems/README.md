# 03_systems — 업무 시스템 서버

명세 1절의 네 시스템을 HTTP 서버로 만든 것입니다. Studio에 **시스템으로 등록**해서 씁니다. 기준 문서는 [서버_설계서.md](서버_설계서.md)입니다. 무엇을 바꾸든 설계서를 먼저 고칩니다.

- **1단계, 조회:** 조회 API (설계서 5절)
- **2단계, 쓰기:** 명세 8절 Action A01–A11을 실행하는 API, 평가 엔진, 모의 지급 (설계서 7절)

## 실행

```bash
cd 04_insurance_ontology_poc/03_systems
./run.sh start        # 네 서버 시작 (처음이면 uv로 의존성 설치, .env.local 생성)
./run.sh status       # 실행 상태와 /health
./check.sh            # 조회 API 확인 (B0 값, 25개 항목)
.venv/bin/python scenario_test.py                 # 쓰기 API 시나리오 (명세 11절 + A01·A02)
.venv/bin/python scenario_test.py --repeat 100 T18 T19   # 동시 승인 반복
./run.sh restart      # 코드를 바꾼 뒤
./run.sh stop
```

- 전제: PostgreSQL이 켜져 있고 `insurance` DB가 있어야 합니다(`02_data/reset.sh`).
- `scenario_test.py`는 테스트마다 DB를 B0로 되돌립니다. 끝나면 B0 상태로 남깁니다.
- 서버는 자동으로 켜지지 않습니다. Studio에서 쓰는 동안 켜 둡니다.
- 로그: `logs/<시스템>.log`

## Studio 등록

1. `./studio-env.sh` 실행 → Studio 앱을 완전히 종료(⌘Q)하고 다시 엽니다. 인증 비밀 값을 Studio 실행기에 넘기는 단계입니다(설계서 2.3절). 재부팅한 뒤에도 다시 합니다.
2. 「시스템 등록」에서 아래 값으로 네 개를 등록합니다. 네 개 모두 OpenAPI 주소는 `<주소>/openapi.json`, 상태 확인 경로는 `/health`입니다.

| 이름 | 주소 | 인증 | 헤더 | 환경변수 이름 | API 수 |
|---|---|---|---|---|---|
| `ins-contract` | `http://127.0.0.1:18101` | API 키 | `X-API-Key` | `INS_CONTRACT_API_KEY` | 6 |
| `ins-intake` | `http://127.0.0.1:18102` | Basic | | `INS_INTAKE_BASIC` | 11 |
| `ins-review` | `http://127.0.0.1:18103` | Bearer | `Authorization` | `INS_REVIEW_TOKEN` | 24 |
| `ins-payment` | `http://127.0.0.1:18104` | API 키 | `X-Payment-Key` | `INS_PAYMENT_API_KEY` | 3 |

인증란에는 **환경변수 이름**을 적습니다. 비밀 값 자체는 `.env.local`(권한 600)에만 있고, 이 파일은 공유하지 않습니다.

## 파일

| 파일 | 내용 |
|---|---|
| `서버_설계서.md` | 기준 문서: Studio 조건, 설계 원칙, 등록 값, 조회 API, 쓰기 API·평가·승인·지급 규칙 |
| `services/common.py` | DB 연결(조회는 읽기 전용), 인증 3종, `/health`, 멱등성, 거절 응답, 다른 시스템 호출 |
| `services/evaluation.py` | 평가 엔진 R01–R07. 이 파일의 SHA-256이 규칙 `RV-001`의 `logic_hash` |
| `services/{contract,intake,review,payment}.py` | 시스템별 서버 |
| `run.sh`, `check.sh`/`check.py`, `scenario_test.py`, `studio-env.sh` | 실행, 조회 확인, 쓰기 시나리오 테스트, Studio 실행기 환경 |
| `pyproject.toml`, `uv.lock` | 의존성 (Python 3.12, FastAPI, uvicorn, psycopg, httpx) |

## 확인 기록

2026-11-03 1단계:
- `./check.sh` 25개 항목 모두 통과했습니다.
- 조회 연결에서 UPDATE를 하면 `ReadOnlySqlTransaction`으로 거부됩니다.
- Studio 실행기의 OpenAPI 해석 코드로 읽으면 API 25개가 나옵니다.

2026-11-03 2단계:
- `scenario_test.py --repeat 100` 결과는 [05_tests/서버_2단계_테스트_결과.md](../05_tests/서버_2단계_테스트_결과.md)에 있습니다.
- 첫 실행에서 T05가 실패했습니다. 입원일이 역할 기간 밖이라 R01이 UNKNOWN이 된 것이 원인이었고, 설계서 7.4절을 고친 뒤 통과했습니다.
- Studio 등록과 연결 테스트는 이 시점에는 하지 않았습니다(아래 「Studio 등록」에 기록).

2026-11-03 Studio 기능 대조 뒤 보완([notes/Studio_기능_대조.md](../notes/Studio_기능_대조.md)):
- 되돌리기 API(`cancelReceipt`, `revertAttachment`)가 심사 시스템을 조회합니다. 성공한 A01·A02를 Studio에서 취소해도 데이터가 어긋나지 않습니다(설계서 7.2·7.3절).
- 심사 시스템이 꺼져 있으면 되돌리지 않고 503을 돌려주는 것을 직접 확인했습니다.
- 쓰지 않던 `payment.idempotency_record`를 지웠습니다.
- `scenario_test.py --repeat 100` 결과 109/109 통과입니다(취소 경로 2개 추가).

2026-11-03 Studio 등록:
- 실행기 환경에 `INS_*` 4개가 들어온 것을 확인했습니다(`studio-env.sh` 뒤 Studio 재시작).
- 4개 시스템을 위 표의 값으로 등록했습니다. 프로토콜은 REST, 환경은 `local`입니다. 화면과 같은 Studio 백엔드 API(`/api/act/systems`)를 썼습니다.
- 연결 테스트는 4개 모두 스펙·상태 확인·인증 통과(`missing_env` 없음)였고, API 수는 6 / 11 / 24 / 3입니다.
- Studio 실행기를 거친 GET 조회(`listPolicies`, `getReceipt`, `getClaim`, `listPaymentRequests`)가 모두 200입니다. 서버가 인증 없이는 401을 돌려주므로, 인증 값 전달까지 확인한 것입니다.
