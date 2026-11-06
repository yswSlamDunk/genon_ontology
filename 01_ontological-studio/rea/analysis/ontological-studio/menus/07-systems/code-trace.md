# M7 시스템 등록 — 코드 추적 (원본 근거, 구현 세션에 넘기지 않음)

- 기준: 배포본 0.1.1. 경로 약어
  - `SH` = `extracted-app-asar/src/main/`
  - `KA` = `shared/app/runtime/kinetic/app/app/` (kinetic-action, Python)
  - `ST` = `shared/app/runtime/studio/app/backend/src/modules/` (Studio 백엔드)
  - `SV` = `shared/app/resources/sample/` (예제 서비스·SQL)
  - `FE` = `shared/app/runtime/frontend/assets/index-Bnym06ph.js` (압축 번들, 위치는 **바이트 오프셋** `@N`)
- 앱 실행·스크립트 실행 없음. `kinetic.db`는 `sqlite3 -readonly .schema`만 확인(내용 미조회).

## 0. 구성 요소와 호출 경로

```
화면(SystemRegistryPanel, FE) ──fetch /api/act/…──▶ 로컬 웹 오리진(SH web.js) ──프록시──▶ Studio 백엔드 ST kinetic/api.py
     │                                                   └ 실행기 미가동 시 GET /api/act/health·/api/act/systems 를 셸이 직접 응답
     ▼
Studio 백엔드 ST kinetic/client.py ──HTTP /api/kinetic/… + Bearer KINETIC_STUDIO_TOKEN──▶ kinetic-action KA main.py
                                                                                               ├ registry.py (등록·스펙 해석)
                                                                                               ├ store.py → SQLite <userData>/kinetic.db
                                                                                               └ dispatch.py/sysauth.py → 업무 시스템 직접 호출(KINETIC_SVC_DIRECT=1)
kinetic-action ──GET JWKS──▶ 로컬 웹 오리진 /kinetic-idp/jwks.json (SH web.js L62, kinetic.js jwks())
```

## 1. 셸의 키네틱 통합 (SH kinetic.js, index.js, web.js, services.js)

| 항목 | 위치 | 내용 |
|---|---|---|
| 비밀값 보강 | kinetic.js L29–40, index.js L129 | `secrets.json`에 없으면 생성: `svcPassword`, `erpApiKey`, `wmsBasic`(=`kinetic:<난수>`), `crmToken`, `kineticInternal`(18바이트 base64url), `kineticKey`(RSA 2048 PKCS8 PEM) |
| kid | kinetic.js L42 | `sha256(PEM)` base64url 앞 16자 |
| JWKS | kinetic.js L44–47, web.js L61–62 | `GET /kinetic-idp/jwks.json` → `{keys:[{…공개 JWK, kid, alg:'RS256', use:'sig'}]}` |
| 토큰 발급 | kinetic.js L49–54 | RS256 JWT, 헤더 `{alg,typ,kid}`, 페이로드 `{sub, roles, aud:'kinetic-action', iss:'ontology-studio-lite', iat, exp=iat+30일}` |
| 역할 카탈로그 | kinetic.js L24–26 | `[{role:'scm_operator', description:'공급망 운영 담당 — …', claims:[]}]` |
| 프로세스 기동 | kinetic.js L67–91 | 예제 서비스 3개: `python -m uvicorn <erp|wms|crm>:app --host 127.0.0.1 --port <포트>` (cwd=`SV/services`, env= 기본 env + `ERP_API_KEY/WMS_BASIC/CRM_TOKEN` + `SAMPLE_DSN=postgresql://sample_svc:…@127.0.0.1:<pg>/sample`). 실행기: `uvicorn app.main:_default_app --factory` (cwd=userData) |
| 실행기 env | kinetic.js L78–85 | `KINETIC_DB_URL=sqlite:///<userData>/kinetic.db`, `KINETIC_NEO4J_URI=bolt://127.0.0.1:<bolt>`, `KINETIC_NEO4J_USER/PASSWORD`(=슈퍼유저), `KINETIC_NEO4J_DATABASE=<graph>`, `KINETIC_JWKS_URL=http://127.0.0.1:<web>/kinetic-idp/jwks.json`, `KINETIC_AUDIENCE`, `KINETIC_ISSUER`, `KINETIC_INTERNAL_SECRET`, `KINETIC_PUBLIC_BASE`, `KINETIC_PORT`, `KINETIC_SVC_DIRECT=1`, 그리고 예제 비밀 3개. **`studio.env`(readUserEnv)는 넘기지 않음** — kinetic.js 전체에 readUserEnv 호출 없음, `PYTHON_DOTENV_DISABLED=1`(L61) |
| 준비 확인 | kinetic.js L87–90 | 예제 `GET /health`, 실행기 `GET /api/kinetic/health`, 각 60초 |
| Studio env | kinetic.js L94–104, services.js L132–135 | `KINETIC_URL`, `KINETIC_MCP_URL=<kinetic>/mcp/`, `KINETIC_STUDIO_TOKEN`(sub `lite-user`, roles `kinetic_admin, kinetic_approver, scm_operator`), `KINETIC_AGENT_TOKEN`(sub `lite-agent`, roles `scm_operator`), `KINETIC_ROLE_CATALOG`. 사용자가 `studio.env`에 `KINETIC_URL`을 두면 이 값들 대신 사용자 값(없으면 자리표시자 `http://127.0.0.1:9`) |
| 외부 실행기 | index.js L151, L164–165 | `studio.env`에 `KINETIC_URL`이 있으면 내장 실행기·예제 서비스를 띄우지 않음 |
| 부팅 순서 | index.js L165–175 | 실행기 시작 ‖ Studio 시작. 실행기 성공 → `repointSystems` → `registerSystems` → `kineticUp=true`, mark('kinetic'). 실패 → 로그 「kinetic-action 을 시작하지 못했습니다 — 액션 없이 계속합니다」 |
| 예제 등록 | kinetic.js L108–137 | 토큰 sub `lite-setup`, roles `kinetic_admin`. `GET /api/kinetic/systems` 후 없는 `sample-<n>`만 `POST`. 본문: `name, base_url, openapi_url=<url>/openapi.json, health_path:'/health', protocol:'rest', timeout_ms:5000, retries:2, environments:[{name:'local', base_url}], active_environment:'local'` + 표시정보(display_name, description, owner_team, icon, tags, auth) |
| 예제 표시정보 | kinetic.js L108–115 | erp: 구매 ERP / 발주 보류·해제, 협력사 납기 독촉 / 구매팀 / icon erp / tags erp,purchasing,sample / auth `{kind:'api_key', header:'X-API-Key', secret_env:'ERP_API_KEY'}`; wms: 물류 WMS / 입고 선적 조회·우선순위 변경 / 물류팀 / wms / `{kind:'basic', secret_env:'WMS_BASIC'}`; crm: 고객 CRM / 고객 안내 발송·철회 / 고객지원팀 / crm / `{kind:'bearer', secret_env:'CRM_TOKEN'}` |
| 주소 갱신 | kinetic.js L143–155 | 예제 시스템의 `base_url`이 현재 포트와 다르면 `{...기존, base_url, openapi_url, environments:[local], active_environment:'local'}`를 다시 `POST`(=교체). 로그 `시스템 주소 갱신 …` |
| 미가동 응답 | web.js L41–47, L63–66 | 실행기 미가동이면 `GET /api/act/health` → 200 `{url:'시작하지 않음', identity:null, reachable:false, error:'키네틱 액션 실행기(kinetic-action)가 아직 시작되지 않았거나 시작하지 못했습니다. 로그 폴더의 kinetic.log 를 확인하세요.'}`, `GET /api/act/systems` → 503 `{detail:<같은 문구>}`. 그 밖의 `/api/act/*`는 백엔드로 감 |
| info | index.js L313 | `kineticConfigured: kineticUp || !!env.KINETIC_URL` (홈 카드 `kinetic:true` 표시 조건) |
| 종료 | index.js L350–351 | backend·mcp(8s), kinetic(5s), 예제 3개(5s) 병렬 정지 |
| 예제 DB | SH postgres.js L131–139, SV services.sql | 첫 실행 1회: `wms.shipment.priority` 열, `wms.priority_change`, `erp.po_hold`, `erp.expedite_request`, `crm.notice` 생성, 역할 `sample_svc`(SELECT/INSERT/UPDATE on erp·wms·crm), `fabric_ro` SELECT |

## 2. 시나리오별 흐름

### S1 목록
- FE SystemRegistryPanel(컴포넌트 이름 `@123994`, 루트 `data-testid=system-registry` `@119769`, 머리말 문구 `@140363`). 마운트 시 `health()`(전역 1회 캐시, API 팩토리 `@117328`) 와 `Ee()`=`listSystems()` → 시스템마다 `Te(name)`=`systemHealth(name)`.
- `GET /api/act/systems` → ST kinetic/api.py L373–375 → client.py L205 `GET /api/kinetic/systems` → KA main.py L140–142 (아무 유효 토큰) → registry.py L647–648 `_public` 목록(이름순, store.py L157–159).
- 카드: 아이콘 맵 8종(mes·cmms·aps·erp·sap·scm·wms·generic) — `icon` 값이 없으면 이름에 키가 포함되는지로 추정, 없으면 generic. 프로토콜 라벨, 상태 점 `✓/!/?`, 상태 문구 `정상 · Nms` / `이상 · HTTP N` / `응답 없음 · …` / `확인 중` / `상태 미확인`.
- 신원 배지: `/api/act/health`의 `identity.sub` + (`roles`에 `kinetic_admin` 있으면 「관리자」, 없으면 「조회 전용」, 툴팁 「kinetic_admin 역할이 없어 등록·수정·삭제가 거부됩니다」).
- ST api.py L360–370 `act_health`: `{url: origin(), identity: token_identity(), reachable, error?}` — identity는 토큰을 **검증하지 않고** 페이로드만 읽음(client.py L112–133) `{configured, sub, roles}`. 실행기 `GET /api/kinetic/health` 3초.

### S2 상세
- FE `Oe(name)`: `getSystem(name)` → 응답에 `operations` 배열이 없으면 `listOperations`. `GET /api/act/systems/{name}` → api.py L400–402 → KA main.py L148–150 → registry.py L650–651 `{..._public, operations: merged}`.
- `_public` 필드(registry.py L241–258): `name, display_name, description, owner_team, contact, tags[], icon('generic'), protocol, spec_format, executable, adapter_required, base_url, environments[], active_environment, openapi_url, auth{…공개}, auth_kind, auth_header, auth_secret_env, timeout_ms, retries(기본 2), health_path(기본 '/health'), operations_count, route('/svc/<name>'), created_at, updated_at`.
- 인증 표시 문자열(FE `oe()`): none→`없음`; api_key→`API 키 · <헤더 또는 ?쿼리> ← $ENV`; bearer→`Bearer · <헤더> ← $ENV`; basic→`Basic ← $ENV`; oauth2→`OAuth2 client credentials · <client_id> ← $<env> · <token_url>`; login_token→`로그인 토큰 · <url> · <user필드> ← $<env>, <pw필드> ← $<env> · 응답 <path> → <헤더>: <스킴>`.
- operation 병합(registry.py L126–138): 스펙(OpenAPI 3 → `parse_openapi` L76–98, operationId 있는 get/post/put/patch/delete만, 공통+개별 파라미터, `application/json` 요청 본문 스키마, `$ref` 깊이 8까지 펼침, `servers[0].url`의 경로 접두 처리 L60–73) 또는 WSDL(specs.py L198–205) + 수동(같은 id면 수동 우선). 항목 `{operation_id, method, path, summary, parameters[{name,in,required,schema}], request_body_schema, source:'openapi'|'wsdl'|'manual'}`.
- 예제 서비스 operation(SV services/*.py): ERP 6(getPurchaseOrder GET `/purchase-orders/{po_id}`, holdPurchaseOrder POST `/purchase-orders/{po_id}/hold`, releasePurchaseOrder POST `…/release`, createExpediteRequest POST `/expedite-requests`, withdrawExpediteRequest POST `/expedite-requests/{request_id}/withdraw`, listExpediteRequests GET `/expedite-requests`), WMS 3(getShipment, setShipmentPriority POST `/shipments/{shipment_no}/priority`, listShipments GET `/shipments?min_delay`), CRM 4(getCustomer, createNotice POST `/notices`, withdrawNotice POST `/notices/{notice_id}/withdraw`, listNotices). `/health`는 스키마 제외(`include_in_schema=False`).

### S3 상태 확인
- FE `Te(name)` → `GET /api/act/systems/{name}/health` → api.py L426–428 → client.py L241 (타임아웃 6초) → KA main.py L179–181 → dispatch.py L85–97: 직접 모드에선 `base_url + health_path`로 **인증 헤더를 붙여** GET, 3초. `ok = status < 300`. 응답 `{ok, http_status, latency_ms, checked_at, error?}` (`error`: `HTTP N` / `<예외명>: …` / `auth_unavailable: …`).
- FE 실패 처리: 예외 시 `{ok:false, error, http_status: status(503 제외)}`.

### S4 스펙 다시 읽기
- FE `Ve()` → `POST /api/act/systems/{name}/refresh` → api.py L421–423 → KA main.py L172–177 (kinetic_admin, 감사 `refresh_system` + operations 수) → registry.py L619–625: `openapi_url` 없으면 422 「시스템 '…' 에 openapi_url 이 없습니다.」, 있으면 다시 입수·저장(수동 API 유지).
- 배너 「'<name>' 의 스펙을 다시 읽었습니다 — API N개 (직접 추가한 API 는 유지).」

### S5 API 추가·삭제
- FE `Je()`: 본문 `{operation_id, method, path, summary, parameters:[{name,in,required(path는 강제 true),schema:{type}}], request_body_schema|null}` → `POST /api/act/systems/{name}/operations` → api.py L448–457(빈 스키마 제거, method 대문자) → KA main.py L194–200 (admin, 감사 `add_operation`) → registry.py L627–634, 검증 L432–459 (operation_id `^[A-Za-z_][A-Za-z0-9_.-]{0,99}$`, method 5종, path `/` 시작, param.in path|query|header, 경로 변수는 path 파라미터로 선언돼야 함 → 422 「경로 변수 [...] 가 parameters(in: path) 에 없습니다.」).
- 삭제: `DELETE /api/act/systems/{name}/operations/{id}` → KA main.py L202–208 → registry.py L636–645: 스펙 출처면 409 「스펙에서 온 operation 은 지울 수 없습니다 (명세를 고치고 refresh).」, 없으면 404. FE는 409를 「스펙에서 온 API 는 지울 수 없습니다 — 스펙을 고치고 다시 읽으세요.」로 바꿔 보임.

### S6 GET 조회
- FE `A(op)` → `POST /api/act/systems/{name}/query` `{operation_id}` (path_params·query는 화면에서 안 보냄) → api.py L431–441 → client.py L245–264 → KA main.py L187–192 → plans.py L100–127: GET이 아니면 422 `not_readonly`, 실행 불가 프로토콜이면 422 `not_executable`, 쿼리 스칼라 검사, dispatch.py L121–146 GET 1회(시스템 timeout_ms), 결과 `{ok, http_status, data, latency_ms, truncated, error?}`, `KINETIC_QUERY_MAX_ITEMS`(기본 500) 초과 시 잘림, 감사 `query`. 권한: 유효 토큰이면 누구나(역할 검사 없음).
- FE 표시: 배열 20건 초과 시 앞 20건 + `… 외 N건`. 「조회」 버튼은 `method==GET && path에 '{' 없음`일 때만.

### S7·S8·S9 새 시스템 마법사
- FE 상태 초기값 `M()`: `name:'', icon:'generic', protocol:'rest', specMode:'file', spec_format:'', environments:[{name:'default', base_url:''}], active_environment:'default', auth_kind:'none', api_key_in:'header', username_field:'loginId', password_field:'password', token_path:'token', scheme:'Bearer', timeout_ms:5000, retries:2, health_path:'/health'`.
- 단계 검증 `_e(n)`: 1 이름 `^[a-z0-9][a-z0-9-]*$` 이고 `routes` 아님 / 2 `none` 또는 URL 비지 않음 또는 파일 내용 있음 / 3 이름+`http(s)://` 주소 환경 1개 이상, 활성 환경이 그중 하나 / 4 방식별 필수(api_key: env+헤더 또는 쿼리 이름, basic·bearer: env, oauth2: token_url+client_id+secret env, login_token: 별도 검사 `he`) / 5 항상 / 6 테스트 결과 존재. 「연결 테스트」·「등록」 활성 = 1–4 모두 참 (`ve`). → **테스트 없이 등록 가능**.
- 로그인 토큰 화면 검사(`he`): URL http(s), 두 env 이름 `^[A-Za-z_][A-Za-z0-9_]*$`, 필드·토큰 위치 `^[A-Za-z_][A-Za-z0-9_.-]*$`, 고정 본문 JSON 객체.
- 파일 업로드 `Pe()`: 확장자·내용으로 형식 판별(proto / graphql_sdl / wsdl / odata_metadata / swagger2 / openapi3 / asyncapi, YAML 키도 인식), 생성 모드면 프로토콜 자동 전환(wsdl→soap, proto→grpc, graphql_sdl→graphql, asyncapi→async, odata_metadata→odata).
- 요청 본문 `Re()`: `{name, display_name, description, owner_team, contact, tags[], icon, protocol, environments(유효한 것만), active_environment, base_url(활성 환경 주소), auth, timeout_ms, retries, health_path, spec_format?, openapi_url?(URL 모드), openapi_text?(파일 모드)}`.
- 인증 객체 `Le()`: none `{kind}`; api_key `{kind, header, secret_env}` 또는 `{kind, query_param, secret_env}`; basic `{kind, secret_env}`; bearer `{kind, header(기본 Authorization), secret_env}`; login_token `{kind, token_url, login_body?, username_field, username_env, password_field, password_env, token_path, header, scheme}`; oauth2 `{kind, token_url, client_id, client_secret_env, scopes[]}`.
- 테스트: `POST /api/act/systems/test` → api.py L389–397 (`_system_body` L212–256: 빈 값 제거, 환경 정리·활성 기본값·base_url 보충, openapi 문자열이면 JSON 시도 후 실패 시 openapi_text; `_auth_payload` L174–205: 방식별 허용 필드만, `validate_system_auth` = ST kinetic/definition.py L383–442: env 이름 형식, login_token 필수값·본문에 비밀번호 필드 금지 → 422) → client.py L219–223 (타임아웃 30초) → KA main.py L134–138 (admin) → registry.py L542–588:
  - `spec`: 입수 성공 → `{ok:true, format, operations:N, operation_ids:[…≤200], note?:'스펙 없음 — 수동 등록 API 만 쓰는 시스템'}`, 실패 → `{ok:false, format, operations:0, error}`
  - `health`: `base_url + health_path` 인증 없이 GET 3초, `ok = status < 300` → `{ok, http_status, url, latency_ms, error?}`; 주소가 http(s) 아님 → 「http(s) 주소가 아니라 health 를 부를 수 없습니다 (어댑터 필요).」
  - `auth`: `{ok, kind, required_env[], missing_env[], checked_in:'kinetic-action', injected_by:'kinetic-action'(직접 모드)}` — **실행기 프로세스의 os.environ**만 검사(L580–581)
  - `protocol, executable, adapter_required, ok = spec.ok && health.ok && auth.ok`
- FE 테스트 표시: 스펙 줄 `operation N개 · <형식>` (N=0이면 실패색), `해석 실패: …`, none 모드 「스펙 없음 — 저장 뒤 API 를 직접 추가합니다」; 헬스 줄 `정상 · HTTP s · Nms` 또는 오류; 환경변수 줄 `없음: A, B` 또는 「필요한 이름이 모두 있습니다 (값은 보지 않음)」; 앞 12개 operation; 「응답 원문」. 테스트 404/405면 「실행기가 연결 테스트(POST /systems/test)를 아직 지원하지 않습니다. 저장은 할 수 있습니다.」 (FE `ze()`).
- 등록: `POST /api/act/systems` → api.py L378–386 → client.py L215 → KA main.py L127–132 (admin, 감사 `register_system`) → registry.py L521–540: 이름 `^[a-z0-9][a-z0-9-]{0,62}$` & ≠`routes`; **같은 이름이 있으면 교체**(created_at·manual_ops 유지, 표시정보는 본문에 없는 항목만 이전 값 유지 L358–383); 스펙 입수 L476–506 (우선순위 openapi 객체 > openapi_text > openapi_url(10초 GET); swagger2는 OpenAPI 3로 변환 specs.py L133–193; wsdl·sdl·proto·asyncapi·$metadata는 원문만 `spec_text`; 스펙 없으면 `"{}"`); 프로토콜 = 본문 값 > 스펙 형식 기본 > rest; 환경 L386–429; 인증 L281–331 (비밀 값 키 `secret/value/password/client_secret/token/api_key`가 있으면 422 「…비밀 값은 등록하지 않습니다 — 환경변수 이름(*_env)을 주세요.」); `timeout_ms` 기본 **10000**(본문 없을 때, L534), `retries` 0–5, `health_path` 기본 `/health` & `/` 시작.
- FE 등록 후: 배너 「시스템 '<표시이름>' 을(를) 등록했습니다 — API N개.」(+ 실행 불가면 「 실행 어댑터가 필요해 액션 실행은 거부됩니다.」), 목록 다시 읽고 상세로.
- 프로토콜 목록(FE·KA 일치): rest, odata, soap, grpc, graphql, db_procedure, async. 실행 가능 = rest, odata (registry.py L36–37).
- 스펙 형식: openapi3, swagger2, wsdl, graphql_sdl, proto, asyncapi, odata_metadata (specs.py L17).

### S10 편집
- FE `Ae()`로 상세 → 폼 채움(specMode = openapi_url 있으면 url, 아니면 none; 파일 모드·이름·프로토콜 잠금). 저장 `Be()` 편집 분기: 본문에서 `name, protocol, openapi_text` 제외 → `PATCH /api/act/systems/{name}` → api.py L405–411 (`_patch_body` L282–302: None 아닌 값만) → KA main.py L156–162 (admin, 감사 `update_system` + 필드 목록) → registry.py L590–612. `openapi_url`이 바뀌었으면 FE가 이어서 `refresh` 호출.
- 편집 시 health_path 빈칸 → `""` 전송 → `_health_path("")` = `/health`.

### S11 삭제
- FE `He()` confirm → `DELETE /api/act/systems/{name}` → api.py L414–418 → KA main.py L164–170: 삭제 후 `used_by = actions_using(name)`(plans.py L134–135, 카탈로그의 발행 액션 중 단계·보상 시스템에 포함된 것 `Class.action`) → `{deleted:true, used_by:[…]}`, 감사 `delete_system`. **거절하지 않음.**
- 재시작 시 `registerSystems`가 없는 `sample-*`를 다시 등록(kinetic.js L126–134).

### S12 이름 중복
- FE 생성 모드는 중복 검사 없음 → `POST` → registry.py L521–540 upsert(store.py L150–155).

### S13 실행기 없음
- 내장 실행기 미가동: web.js L63–66. 외부 URL 실패: client.py L180–186 → 503 `unavailable` 「kinetic-action 에 닿지 못했습니다 (<url>): <예외>. KINETIC_URL 과 서비스 기동 여부를 확인하세요.」. 401 → 「kinetic-action 인증 실패 — KINETIC_STUDIO_TOKEN 을 확인하세요.」, 403 → 「… — 스튜디오 신원에 필요한 역할이 없습니다 (레지스트리 쓰기는 kinetic_admin, 승인은 kinetic_approver).」 (client.py L136–162).
- FE 권한 오류 문구 함수 `@119538`: 「권한이 없습니다 — 스튜디오 신원(KINETIC_STUDIO_TOKEN)에 kinetic_admin 역할이 필요합니다. (…)」.

### S14 주소 갱신
- kinetic.js L143–155 (위 표).

## 3. API 목록

### 3.1 화면 → Studio 백엔드 (`/api/act/…`, 인증 없음, 로컬 오리진)
| 메서드 | 경로 | 요청 | 응답 |
|---|---|---|---|
| GET | `/api/act/health` | — | `{url, identity:{configured,sub,roles}|null, reachable, error?}` |
| GET | `/api/act/systems` | — | `System[]` |
| POST | `/api/act/systems` | SystemBody | `System` |
| POST | `/api/act/systems/test` | SystemBody | TestResult |
| GET | `/api/act/systems/{name}` | — | `System + operations[]` |
| PATCH | `/api/act/systems/{name}` | SystemPatchBody | `System` |
| DELETE | `/api/act/systems/{name}` | — | `{deleted, used_by[]}` |
| POST | `/api/act/systems/{name}/refresh` | — | `System` |
| GET | `/api/act/systems/{name}/health` | — | `{ok,http_status,latency_ms,checked_at,error?}` |
| POST | `/api/act/systems/{name}/query` | `{operation_id, path_params?, query?}` | `{ok,http_status,data,latency_ms,truncated,error?}` |
| GET | `/api/act/systems/{name}/operations` | — | `Operation[]` |
| POST | `/api/act/systems/{name}/operations` | Operation 입력 | `Operation + source:'manual'` |
| DELETE | `/api/act/systems/{name}/operations/{id}` | — | `{deleted:true}` |
- 오류 형식: `{error:{code, message}}` + 상태(401/403/404/409/422/502/503). 셸 미가동 목록만 `{detail}`.
- FE 래퍼(오류 변환 `@117089`, 팩토리 `@117328`): 응답이 `!ok` 이거나 본문에 `error`가 있으면 예외(`message`, `code`, `status`).

### 3.2 Studio 백엔드 → 실행기 (`/api/kinetic/…`, Bearer JWT)
위 표와 1:1 (경로 접두만 `/api/kinetic`). 추가로 실행기에만: `GET /api/kinetic/health` → `{ok:true}`, `GET /api/kinetic/systems/routes`(헤더 `X-Kinetic-Internal` 필요, 게이트웨이 라우트용, registry.py L679–708), `/.well-known/oauth-protected-resource[/mcp]`. 역할: 등록·테스트·수정·삭제·refresh·operation 추가/삭제 = `kinetic_admin`; 목록·상세·health·operations·query = 유효 토큰.
- 토큰 검증 KA auth.py L53–77: RS256, JWKS(캐시 300초), aud·iss 검사, `sub`·`exp` 필수, 여유 `KINETIC_JWT_LEEWAY`(30초). 실패 401 + `WWW-Authenticate: Bearer resource_metadata="…"`.
- 응답 헤더 `X-Request-Id` (요청 값 또는 생성). 감사 기록에 request_id.

### 3.3 실행기 → 업무 시스템 (직접 모드)
- dispatch.py: URL = `base_url + path` (게이트웨이 모드면 `KINETIC_SVC_BASE/<name>` — 0.1.1 미사용). 헤더 `Idempotency-Key`, `X-Kinetic-Run`, `X-Kinetic-Internal`(내부 비밀, **업무 시스템에도 전송됨** L60–68) + 인증.
- sysauth.py: api_key 헤더/쿼리, basic `base64(env값)`, bearer(`Bearer ` 접두 없으면 붙임), oauth2 client_credentials(form POST, `access_token`, 만료 60초 전 갱신, 기본 300초), login_token(JSON POST, 점 경로로 토큰, JWT exp 또는 ttl, 401 시 1회 재로그인). env 비어 있으면 인증 없이 보냄.
- **시스템별 `retries`는 직접 모드 호출에서 쓰이지 않음** (dispatch.py 주석 L6, `retries` 참조 없음 — 게이트웨이 라우트 정보로만 노출). 타임아웃은 `timeout_ms` 사용.

### 3.4 다른 소비자
- M1 구축 에이전트 도구(ST ontology/tools.py): `system_list` L1921–1942(필드 name·description·base_url·operations_count·route·health_path), `system_operations` L1945–1971, `system_query` L2011–(GET만), `action_create`의 `_check_operation` L1698–1715(`missing_system`/`missing`/`unverified`).
- M1 구축 마법사 「소스」 단계 FE `@306290` `listSystems()`; 액션 편집기 FE `@260785`·`@255962` `listSystems/listOperations` + 실행기 불가 배너 「… 정의는 저장되지만 시스템·operation 목록과 dry-run 은 쓸 수 없습니다.」.
- 실행기 MCP `query_system` 도구(KA mcp_tools.py L147–157) — M2.
- 예제 온톨로지 액션(SV seed_ontology.py L82–126)이 `sample-wms/setShipmentPriority`, `sample-erp/createExpediteRequest·withdrawExpediteRequest·holdPurchaseOrder·releasePurchaseOrder`, `sample-crm/createNotice·withdrawNotice` 참조.

## 4. 데이터 구조·저장

- SQLite `<userData>/kinetic.db` (KA store.py L31–66, 실측 `.schema` 일치): 표 `kinetic_systems`(PK name; base_url, openapi(JSON 문자열, 비스펙이면 "{}"), auth_kind, auth_header, auth_secret_env, timeout_ms, created_at, description, openapi_url, health_path, manual_ops(JSON), updated_at, display_name, owner_team, contact, tags(JSON), icon, protocol, spec_format, spec_text, environments(JSON), active_environment, retries, auth_query_param, auth_token_url, auth_client_id, auth_client_secret_env, auth_scopes(JSON), auth_login(JSON)), 그 밖 `kinetic_plans`, `kinetic_runs`, `kinetic_audit`(M2).
- 시작 시 빠진 열만 `ALTER TABLE ADD COLUMN` (store.py L67–73, L131–).
- 시각 RFC3339 UTC 초 단위 `…Z` (store.py L106–107).
- 메모리 캐시: 시스템별 operation 병합 결과(registry `_ops`, 저장 시 무효화), JWKS, OAuth/로그인 토큰.
- 예제 서비스의 멱등 캐시는 프로세스 메모리(SV services/common.py L65–79) — 재시작 시 사라짐.

## 5. 설정값

| 이름 | 기본 | 설정 주체 |
|---|---|---|
| `KINETIC_DB_URL` | `sqlite:///./kinetic.db` | 셸: `<userData>/kinetic.db` |
| `KINETIC_JWKS_URL`, `KINETIC_ISSUER`, `KINETIC_AUDIENCE` | —, —, `kinetic-action` | 셸 |
| `KINETIC_INTERNAL_SECRET` | — | 셸(secrets.kineticInternal) |
| `KINETIC_SVC_DIRECT` | false | 셸 `1` |
| `KINETIC_SVC_BASE` | `http://localhost:9000/svc` | 미설정 |
| `KINETIC_PUBLIC_BASE`, `KINETIC_PORT` | 8030 | 셸(포트 27830 선호) |
| `KINETIC_CONCURRENCY`/`MAX_ATTEMPTS`/`PLAN_TTL`/`CATALOG_REFRESH`/`QUERY_MAX_ITEMS` | 8/3/600/30/500 | 기본값 |
| `KINETIC_JWT_LEEWAY` | 30 | 기본값 |
| Studio `KINETIC_URL`, `KINETIC_STUDIO_TOKEN`, `KINETIC_AGENT_TOKEN`, `KINETIC_ROLE_CATALOG`, `KINETIC_MCP_URL` | | 셸 또는 studio.env |
| 예제 `ERP_API_KEY`, `WMS_BASIC`, `CRM_TOKEN`, `SAMPLE_DSN` | | 셸(secrets.json) |
| 포트 erp/wms/crm | 27841/27842/27843 | A1 포트 규칙 |

## 6. 튜토리얼·문서와 코드 불일치 (관찰)
1. 튜토리얼 「서버가 응답만 하면(5xx가 아니면) 연결됨, 404·405면 『연결됨 · 경고』와 주황 ~」 → 0.1.1 FE에 해당 문구·상태 없음(번들의 「연결됨」은 그래프 상태 배지 1곳뿐 `@2300592`), KA는 `< 300`만 정상.
2. 튜토리얼 「상태 점검 경로를 비워 두면 활성 주소 자체를 점검」 → 빈 값은 Studio 백엔드에서 제거되거나 KA에서 `/health`로 대체(api.py L222 빈 값 제거, registry.py L334–338).
3. 튜토리얼 「등록 시스템의 비밀 값은 studio.env에 적으면 된다」 → 내장 실행기 env에 studio.env가 들어가지 않음(kinetic.js L58–86). 앱을 띄운 셸 환경 변수는 상속됨(services.js baseEnv L111–115). 추정: Finder로 실행하면 사용자 시스템 비밀은 항상 `missing_env`.
4. `studio.env.example` L21–26 「kinetic-action … 이 패키지에는 들어 있지 않다」 → 0.1.1은 내장 실행.
5. 화면 문구 「게이트웨이가 실행 시점에 값을 읽습니다」, 「게이트웨이가 토큰을 발급·캐시」 → 0.1.1은 게이트웨이 없이 실행기가 직접(KINETIC_SVC_DIRECT=1).
6. 마법사 정책 안내 「재시도는 5xx·연결 오류에만…」 → 직접 모드에서는 시스템별 재시도 미적용(3.3).
