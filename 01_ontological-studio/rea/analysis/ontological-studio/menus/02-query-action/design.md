# M2 질의·액션 — 설계 문서 (클린룸)

- 대상: Ontological Studio 0.1.1과 같은 동작을 하는 새 구현의 「질의·액션」 메뉴.
- 이 문서만으로 구현할 수 있게 쓴다. 원본 코드·파일 경로·내부 함수 이름은 넣지 않는다. 외부에서 관찰되는 계약(HTTP 경로·필드, SSE 이벤트, MCP 도구 이름, 화면 문구, 환경 변수 이름)은 비교 테스트를 위해 적는다.
- 에이전트(LLM) 부분은 결과 내용이 아니라 구조·계약으로 정의한다(ADR-0010).
- 함께 볼 문서: A3(에이전트 실행·MCP 브리지·SSE 공통 계약), M7(액션 실행기의 시스템 레지스트리·업무 시스템 호출 계약·신원 토큰), M1(액션 정의·발행), M5(대시보드·코드 앱의 액션 버튼).

---

## 1. 목적

사용자가 한 대화창에서
1. **질문**하면 에이전트가 발행된 온톨로지(그래프)와 연결된 데이터소스를 조회해 **근거와 함께** 답하고(아무것도 바꾸지 않음),
2. **지시**하면 에이전트가 정의된 액션을 골라 **계획(드라이런)** 을 세우고, 사람이 화면의 계획 카드에서 **승인**한 뒤, 사용자의 명시적 확인으로 에이전트가 **실행**하며,
3. **취소**를 요청하면 실행한 단계를 **역순으로 보상**해 되돌린다.

핵심 불변식: **에이전트는 승인할 수 없다.** 승인은 사람이 화면에서만 한다(§9에서 원본의 실제 보장 수준과 구현 권고를 다룬다).

## 2. 사용자 시나리오 (요약)
| # | 시나리오 | 결과 |
|---|---|---|
| S1 | 탭 열기 | 빈 대화: 모드 설명 + 예시 4개, 오른쪽 그래프 |
| S2 | 질문 | 도구 칩이 흐르고 결론·근거·경계가 있는 답, 그래프에 쓰인 노드 강조 |
| S3 | 이어 묻기 | 앞 대화 맥락 사용 |
| S4 | 답 없는 질문 | "온톨로지에 그 개념이 없다"와 이유 |
| S5 | 지시 → 계획 | 계획 카드(허용/거부, 사람 승인 필요, 만료, 미리보기), 에이전트는 멈춤 |
| S6 | 승인 | 카드에서 메모+승인 → 「승인됨」, "대화에서 실행해라고 요청하라" 안내 |
| S7 | 실행 | "실행해" → 같은 계획 실행, 대상·단계별 결과, 업무 시스템 데이터 변경 |
| S8 | 취소 | 대화 또는 카드 버튼 → 역순 보상, 보상 이력 표 |
| S9 | 발주 보류 실습 | 두 번째 액션으로 같은 흐름 |
| S10 | 액션 목록/미승인 실행/만료 | 오류 코드에 맞는 안내 |
| S11 | 대화 관리 | 대화 목록·복원·삭제, 홈 최근 항목 |
| S12 | 끼어들기 | CLI(Claude Code)일 때만 실행 중 추가 지시 |

## 3. 화면 구성과 상호작용

### 3.1 진입
- 홈 카드 「질의·액션」(설명 「온톨로지에 묻고, 지시하면 액션을 계획·실행합니다.」, 에이전트 필요 배지) → Studio 탭 `view=act`. URL에 `session=<id>`가 있으면 그 대화를 연다.
- Studio 상단 내비 항목 「💬 질의·액션」. 구축(build)과 함께 "대화형" 화면이며, 구축과 별개의 대화 상태(입력 초안·메시지 목록)를 가진다. 예전 모드 `answer`의 대화도 이 화면에서 연다.

### 3.2 레이아웃
- 왼쪽 레일: 「워크스페이스」(펼침 상태는 브라우저 로컬 저장) — 이 모드(`act`)의 대화 목록, 새 대화, 삭제.
- 가운데: 대화. 비어 있으면 제목 `ONTOLOGIC Studio`, 모드 이름 「질의·액션」, 설명
  「구축된 온톨로지에 질문하고, 지시하면 정의된 액션을 계획해 승인·확인을 거쳐 외부 시스템에 실행합니다. 실행한 것은 "취소해"로 되돌릴 수 있습니다.」
  와 예시 버튼 4개(누르면 바로 전송, **고정 문구**):
  1. 「3일 넘게 늦어진 입고 선적은 어떤 것이고, 어느 협력사 건이야?」
  2. 「3일 넘게 늦어진 입고 선적을 긴급 처리해 줘. 사유는 생산 차질 우려.」
  3. 「방금 한 긴급 처리를 취소해 줘.」
  4. 「어떤 액션을 쓸 수 있어?」
- 입력창 안내문 「질문하거나 지시하세요. 예: 3일 넘게 늦어진 입고 선적은? / 그 선적들 긴급 처리해 줘 (사유: 생산 차질 우려)」. 이 모드는 **파일 첨부를 받지 않는다**. Enter=전송, Shift+Enter=줄바꿈. 내용이 비었거나 응답 중이면 전송 불가(응답 중에는 끼어들기로 전송 — §3.6).
- 오른쪽: 온톨로지 스키마·인스턴스 그래프. 답변 중 조회 도구가 돌려준 노드를 **강조**한다(§5.3 `traversed_nodes`). 그래프 쓰기 알림(`neo4j_update`)이 오면 스키마·그래프를 다시 읽는다.

### 3.3 메시지 표시
- 사용자 메시지: 말풍선. 끼어들기로 보낸 것은 「작업 중 지시」 표시.
- 에이전트 메시지: 상태 줄(`status`), 텍스트 조각(마크다운), 도구 칩(이름·한 줄 설명·인자, 끝나면 결과 펼침), 실행 중이면 「<도구> 실행 중...」, 끝나면 「N개 도구 사용됨」으로 접힘. 질문 카드(`ask_user`)가 오면 선택지 버튼.
- **근거 표시 방식:** 답의 근거(어느 노드·관계·조건·테이블·행 수)는 에이전트가 **답 본문 안에** 쓴다(지시문 규칙, §7). 화면이 따로 보여 주는 근거는 도구 칩(실제 조회 인자·결과)과 그래프 강조뿐이다. 구조화된 인용 목록은 없다.
- 계획/실행 이벤트가 오면 메시지 안에 **계획 카드**를 넣는다(§3.4). 같은 plan id는 카드 하나, 그 plan의 run 이벤트는 같은 카드에 붙인다. plan을 모르는 run 이벤트는 run 단독 카드.

### 3.4 계획 카드 (실행 계획/실행 결과)
카드는 이벤트로 받은 plan id·run id만 들고, 내용은 REST로 다시 읽는다(도구 결과는 잘려서 오므로). 마운트 시 `GET /api/act/health`로 화면 신원(`sub`, `roles`)을 읽어 버튼 표시에 쓴다.

머리: 「실행 계획」(plan 없이 run만 있으면 「실행 결과」) · `<클래스>.<액션>` · 상태 배지 · 「새로고침」.
상태 라벨: planned 계획됨, awaiting_approval 승인 대기, approved 승인됨, executed 실행됨, expired 만료, rejected 거부.

계획 부분:
- 요약 「허용 **N**건 · 거부 **M**건」 [+ 「 · 사람 승인 필요」(requires_approval)] [+ 「 · 만료 <현지 시각>」] [+ 「 · 작성 <actor_sub>」].
- 표: 구분(허용/거부) · 대상 키 · 속성 열(앞 행들의 속성 중 `$key`, `_`로 시작, `created_at`, `updated_at`, `embedding`을 뺀 최대 3개) · 사유. 허용 먼저, 그다음 거부. 최대 50행, 넘으면 「상위 50건만 표시합니다.」.
- 「호출 미리보기 (<preview 수>건)」 접이식: 첫 미리보기 JSON.
- 버튼 영역:
  - 상태가 awaiting_approval → 「승인 메모 (선택)」 입력 + 「승인」.
  - 실행 가능 조건 = (approved 또는 (planned 이고 승인 불필요)) 그리고 허용>0. 이 조건이고 **plan 작성자 == 화면 신원** 이며 아직 run이 없으면 「실행 (N건)」 버튼(화면에서 직접 만든 계획용 — 대시보드·코드 앱 경로).
  - 실행 가능 조건인데 작성자가 화면이 아니면(=에이전트 계획) 안내 「에이전트가 만든 계획입니다. 승인되었습니다 — 대화에서 “실행해”라고 요청하면 에이전트가 실행합니다.」(approved가 아니면 「승인되었습니다 — 」 부분 없음).
  - awaiting_approval인데 화면 신원에 `kinetic_approver`가 없으면 경고 「현재 스튜디오 신원(<sub 또는 미설정>)에 kinetic_approver 역할이 없어 승인이 거부될 수 있습니다.」
- 오류 표시: 승인 403 → 「승인 권한이 없습니다 (kinetic_approver 역할 필요): <메시지>」, 그 밖 오류 메시지 그대로. 실행 시 `plan_expired`면 plan을 다시 읽는다.

실행 부분(run이 있으면):
- 「실행 <run id> · <상태 배지>」 [+ 「 · 상태 확인 중…」(running이면 1.5초마다 다시 읽음)] [+ 「 · 자동 보상 N건」]. run 상태 라벨: running 실행 중, succeeded 성공, partial 일부 실패, failed 실패, compensated 보상 완료, partially_compensated 일부 보상.
- 대상 표: 대상 키 · 결과(대상 상태 라벨: succeeded 성공, failed 실패, compensated 보상됨, dead 사람 처리 필요, skipped 건너뜀 등 + compensated면 「자동 보상」 또는 「취소」 꼬리표) · 단계(다단계 액션일 때만: 단계 칩 = 시스템 이름 대문자(`mock-` 접두 제거) + ✓/✗/–/…, 보상 성공 ↺, 보상 실패 ⚠, 칩 툴팁에 단계명·시스템·결과·HTTP·오류·보상 결과) · HTTP · 시도 · 오류. 범례 「✓ 성공 · ✗ 실패 · – 건너뜀 · ↺ 보상(되돌림) 완료 · ⚠ 보상 실패」.
- 취소 정보: 「취소 요청 — <주체> · 사유 “<사유>” · <시각>」.
- 「보상 이력 (호출 순서)」 표: # · 시각 · 대상 · 단계 · 시스템 · operation · 결과(+HTTP) · 계기(자동/취소). seq 순.
- 취소 버튼: run이 succeeded/partial이고 성공 대상이 있고, 화면이 작성자이거나 approver일 때 「취소 사유 (선택)」 + 「취소(보상)」 + 안내 「성공한 대상을 역순으로 되돌립니다. 승인은 필요 없습니다.」. 누르면 확인창 「이 실행을 취소할까요? 성공한 대상의 단계를 역순으로 되돌립니다.」. 원본에서는 화면 신원이 approver라 **에이전트 run도 화면에서 취소할 수 있다**.
- run 이벤트가 새로 오면(같은 카드) run을 다시 읽고, run이 끝났는데 plan이 executed가 아니면 plan도 다시 읽는다.

### 3.5 대화 관리
- 첫 전송 때 대화가 임시면 서버에 생성(`mode=act`, 제목 「새 대화」). 이 화면의 첫 사용자 메시지면 제목을 그 메시지 앞 30자(+`...`)로 바꾼다.
- 턴이 끝날 때 등 화면 메시지 배열 전체(도구 칩·카드 참조 포함)를 서버에 저장하고, 대화를 다시 열면 그대로 복원한다(카드는 다시 조회하므로 최신 상태).
- 대화 삭제 = 서버 세션·메시지·에이전트 대화 기억 삭제.
- 홈 「최근 항목」에 「질의·액션 대화」로 나오고 누르면 `view=act&session=<id>`.

### 3.6 끼어들기
- 응답 중 입력하면 `POST /api/agent/steer`. `delivered:true`면 사용자 메시지로 「작업 중 지시」 표시, SSE `steered`가 오면 상태 「사용자 지시를 반영해 방향을 바꿉니다...」. `false`면 턴이 끝난 뒤 보통 메시지로 보낸다. CLI(Claude Code)만 지원(A3).

## 4. 처리 흐름

### 4.1 한 턴
1. 화면이 SSE로 `GET /api/stream?prompt=<원문>&session_id=<id>&mode=act`를 연다.
2. 서버는 세션이 없으면 만들고(제목=프롬프트 앞 80자), 시작 이벤트 `status{message:"질의·액션 모드 실행 시작..."}`를 보낸다. 프롬프트는 **가공하지 않는다**(구축 모드와 달리).
3. act 모드 에이전트를 돌린다(A3: CLI면 대화별 작업 폴더에서 자식 프로세스 + 브리지 MCP `/mcp/agent-bridge/act/`, 내장이면 같은 도구 함수). 대화 줄기는 `<세션>:act` 하나로 **유지**한다(다음 턴 "실행해"가 앞 턴 plan id를 기억해야 하므로; 다른 모드처럼 이어짐마다 새 하위 줄기를 열지 않는다).
4. 도구 결과마다 부수 이벤트(§5.3)를 내고, 끝에 `done`.

### 4.2 질문 경로 (도구·지시문 계약)
- 도구(표준 MCP 경유, 기본): `ontology_graph_schema`, `ontology_list_schemas`, `ontology_get_schema`, `ontology_list_entities`, `ontology_resolve_entity`, `ontology_graph_cypher`(읽기 전용), `ontology_get_datasource_schema`, `ontology_query_datasource_sql`(SELECT, 바인딩 테이블만), `sandbox_read`. 각 도구는 A3의 검색 MCP 서버에 대리 호출한다(의미·인자·제약은 A3 §6.2).
- 내장 도구 표면(`ANSWER_TOOLS_VIA_MCP=false`): `schema_get`, `entity_search`, `neo4j_cypher_readonly`, `graph_stats`, `vector_search`, `sandbox_read`, `behavior_list`, `behavior_invoke`, `entity_fetch`, `datasource_sql_query`. 지시문도 그에 맞는 답변 지시문으로 바꾼다.
- 질문만으로는 계획·실행하지 않는다(질문에 액션을 **제안**할 수는 있음).

### 4.3 액션 경로 (도구 계약)
에이전트용 키네틱 도구 9개(이름·인자 고정, 결과는 JSON 문자열, 연결 실패는 `{"error": "...", "hint": "..."}`):

| 도구 | 인자 | 하는 일 |
|---|---|---|
| `query_system` | `system, operation_id, path_params="{}", query="{}"` | 등록 시스템 GET API로 현재 값 확인(계획·승인 없음, GET 아니면 `not_readonly`) |
| `list_actions` | `class_name=""` | 호출자에게 보이는 액션 목록 |
| `plan_action` | `class_name, action, where="[]", params="{}"` | 구조화 필터로 계획 |
| `plan_action_ids` | `class_name, action, ids="[]", params="{}"` | 키 목록으로 계획 |
| `get_plan` | `plan_id` | 계획 상태(승인 여부 확인) |
| `execute_plan` | `plan_id` | 실행 |
| `get_run` | `run_id` | 실행 결과 |
| `list_runs` | `limit=10` | 호출자가 만든 계획의 최근 run |
| `compensate_run` | `run_id, reason=""` | 취소(역순 보상) |

- `where`·`ids`·`params`·`path_params`·`query`는 JSON 문자열 또는 구조 둘 다 받는다. JSON이 깨졌으면 `{"error":"<이름> 가 올바른 JSON 이 아닙니다: …"}`.
- 이 도구들은 실행기의 MCP 엔드포인트(`KINETIC_MCP_URL`)를 **에이전트 신원 토큰**(`KINETIC_AGENT_TOKEN`)으로 부른다. 따라서 에이전트가 만든 계획의 작성자 = 에이전트.
- **승인 도구는 없다.**

### 4.4 계획 → 승인 → 실행 → 취소 (실행기 규칙)
실행기(kinetic-action)는 별도 프로세스다. 레지스트리·업무 시스템 호출은 M7. 여기서는 액션 부분.

**액션 카탈로그**
- 발행된 그래프에서 액션 정의를 읽어 메모리에 두고 30초마다 갱신(발행 직후 Studio가 갱신 요청도 보냄, M1). 같은 클래스·이름이 여러 개면 높은 version.
- 액션: `class, action, description, parameters(JSON Schema), key_property, effect, confirm_threshold(기본 0), max_targets(기본 100), policy[], writeback_property, version, steps[]`. 단계 `{name(소문자 시작 영숫자_), title, system, operation_id, arg_mapping, compensation?{system(생략 시 단계와 같음), operation_id, arg_mapping}}`. steps가 없으면 단일 단계 `main`(보상 없음). steps 형식 오류면 그 액션 무시.
- 목록 항목(`list_actions` 응답): `{class, action, description, parameters, effect, confirm_threshold, max_targets, key_property(비면 "$elementId"), system, operation_id(첫 단계), steps:[{name,title,system,operation_id,compensable}]}`.

**정책**
- 규칙 배열 OR, 규칙 없음 또는 해당 규칙 없음 = 거부(기본 거부). 규칙 `{roles?, when?, description?}`: `roles`가 비면 누구에게나, 있으면 호출자 역할과 교집합이 있어야 적용. `when`은 CEL 식, 변수 `actor`(토큰 클레임), `target`(대상 속성 + `$key`), `params`, `now`. 식 없음 = 허용. 평가 오류·비불리언 = 거부.
- 거부 사유 문구: 「정책 규칙이 없습니다 (기본 거부)」, 「호출자 역할에 적용되는 정책 규칙이 없습니다」, 「조건 불충족: <description 또는 식>」(여러 규칙이면 `; `로 이음), 「정책 평가 오류(<식>): …」, 「정책 식이 bool 이 아닙니다(<식>)」.
- 목록 노출(보이는가)은 roles만으로 판정.

**계획(드라이런)**
1. 액션이 없으면 404 `not_found` 「액션 '<C>.<A>' 이 발행되지 않았습니다.」, 보이지 않으면 403 `forbidden` 「액션 '<C>.<A>' 을 쓸 권한이 없습니다.」.
2. 파라미터 검사(required 누락 「파라미터 '<n>' 이 필요합니다.」, 타입, enum) → 422 `invalid_params`.
3. 필터 검사(§6.3) → 422 `invalid_filter`. ids 모드면 비어 있지 않은 배열.
4. 모든 단계·보상의 시스템이 등록·실행 가능하고 operation이 있어야 함(M7; 없으면 404, 실행 불가 422 `not_executable`).
5. 그래프에서 대상 조회(라벨 = 클래스, 필터는 파라미터화, ids는 키 속성 문자열 비교 또는 내부 id, 키 속성 순 정렬), `max_targets + 1`개까지. 초과면 422 `too_many_targets` 「대상이 max_targets(<n>) 를 넘습니다. 조건을 좁히세요.」.
6. 대상마다 정책 평가 → `allowed[{key, props}]`, `denied[{key, props, reason}]`. 대상 키 = 키 속성 값(없으면 내부 id).
7. 허용 대상 × 단계마다 호출 미리보기 `{target_key, step, method, url, headers(비밀 헤더 제외, Idempotency-Key 포함), body, compensable}`. 아직 없는 값(`$steps.*`, `$cancel.*`)은 `"<식>"`.
8. `requires_approval = 허용 수 > confirm_threshold`. 상태 = 승인 필요면 `awaiting_approval`, 아니면 `planned`. `expires_at = 지금 + KINETIC_PLAN_TTL(기본 600초)`(UTC, 초 단위 `Z`).
9. 저장, 감사 `plan`. 아무것도 바꾸지 않는다.

**계획 조회** — 살아 있는 상태(planned/awaiting_approval/approved)인데 만료 시각이 지났으면 `expired`로 바꾸고 감사 `expire`. 없으면 404.

**승인 / 반려**
- `kinetic_approver` 역할 필요(아니면 403 `forbidden` 「역할 'kinetic_approver' 이 필요합니다.」).
- 만료면 409 `plan_expired` 「plan 이 만료됐습니다. 다시 plan 하세요.」, 상태가 planned/awaiting_approval이 아니면 409 `conflict` 「상태가 '<s>' 인 plan 은 승인/반려할 수 없습니다.」.
- `status=approved|rejected`, `approved_by=<sub>`, `approved_at`, `approval_note`. 감사 `approve|reject`(detail에 note).
- 원본은 승인자가 작성자와 같아도 막지 않는다(§9).

**실행**
1. 호출자 sub == plan 작성자여야 함(403 `not_plan_owner` 「plan 작성자만 실행할 수 있습니다.」).
2. 그 plan의 run이 이미 있으면 그대로 돌려줌(plan당 run 하나, 동시 실행도 하나로 수렴).
3. 만료 409 `plan_expired`, 반려 403 `forbidden` 「반려된 plan 입니다.」, 승인 필요인데 미승인 409 `approval_required` 「허용 대상 N건 — 사람 승인이 필요합니다 (Studio 에서 승인).」, 허용 0건 409 `nothing_to_execute` 「허용된 대상이 0건입니다. 대상 지정(키 속성 값)이나 조건을 고쳐 다시 plan 하세요.」.
4. 허용 키로 그래프를 **다시** 조회: 없어졌으면 대상 `skipped`(「대상이 더 이상 존재하지 않습니다」), 정책 재평가 실패면 `skipped`(「재평가 거부: <사유>」), 통과면 `before` = 지금 속성.
5. run 생성(status running), plan → `executed`(+run_id).
6. 대상마다 **사가**(대상끼리 병렬, 대상 안 단계는 순서대로): 단계 호출(M7 호출 계약, 헤더 `Idempotency-Key: <plan>:<대상키>:<단계>:a<시도>`, `X-Kinetic-Run: <run>`). 실패하면 남은 단계 skipped, 앞서 성공한 단계를 **역순 자동 보상**(사유 「자동 보상: '<단계>' 단계 실패」, 계기 auto) → 대상 `compensated`(전부 성공) 또는 `dead`(보상 실패). 성공한 단계가 없으면 `failed`. 시도 수 ≥ `KINETIC_MAX_ATTEMPTS`(3)면 `dead`. 대상 끝날 때 `finished_seq` 부여.
7. 대상 성공 시 되쓰기: `writeback_property`가 있으면 첫 단계 응답의 `status` 값(없으면 `"done"`)을 그래프의 그 노드 속성에 기록. 실패해도 결과는 유지하고 `writeback_error` 기록.
8. run 상태: 성공만 `succeeded`, 성공+실패류 `partial`, 그 밖(실패만·전부 건너뜀) `failed`. 감사 `execute`(상태·보상 수·대상 상태별 개수).
- 재시도(REST 전용, 원본 화면 없음): 작성자만, 실패/자동 보상 대상만 새 시도 번호로, 정책 재평가 없음. 취소된 run은 409.

**취소(보상)**
- 작성자 또는 approver(403 `not_plan_owner` 「plan 작성자 또는 승인자만 취소할 수 있습니다.」). 승인 불필요(원상 복구 방향).
- 이미 취소된 run이면 그대로 돌려줌. 단계 기록 없는 옛 run은 409.
- 사유 없으면 「사용자 취소」. `cancel{actor_sub, reason, at(ms)}`.
- 성공 대상만 `finished_seq` **내림차순으로 하나씩**, 대상 안에서는 성공 단계 **역순**으로 보상 호출(Idempotency-Key 끝에 `:c`, 매핑에 `$cancel.reason`). 보상 정의 없는 단계는 `none`. 대상 → `compensated`/`dead`, 성공한 대상은 되쓰기 값을 `before`로 원복.
- run 상태 `compensated` 또는 (dead가 있으면) `partially_compensated`. 감사 `compensate`(사유·상태·대상·호출 수).

**조회 API**(`query_system`) — M7 §조회 계약 그대로.

### 4.5 인자 매핑(값 식)
키 `<위치>.<이름>`(위치 path·query·header·body; body는 점 경로, 숫자 조각은 배열 인덱스 0–999). 값:
`$this.<속성>`, `$this.$key`, `$params.<이름>`, `$actor.<클레임>`, `$before.<속성>`(실행 직전 값), `$steps.<단계>.response.<점 경로>`(같은 대상의 앞 단계 응답; 없으면 그 호출 실패), `$cancel.reason`, `$run.id`, `$plan.id`, `{"$literal": 값}`, 그 밖 문자열은 리터럴. 경로 변수가 비면 「경로 변수 '<v>' 값이 없습니다.」.

## 5. API 명세

### 5.1 대화 (A3 공통, act 사용분)
| 메서드 | 경로 | 요청 | 응답 |
|---|---|---|---|
| GET | `/api/stream` | `prompt`, `session_id`, `mode=act` | SSE (§5.3) |
| POST | `/api/agent/steer?session_id=&mode=act` | `{text}` | `{delivered, reason}` |
| GET | `/api/agent/running?session_id=&mode=act` | | `{running}` |
| POST | `/api/session/reset?session_id=` | | `{status:"ok"}` |
| GET | `/api/sessions` | | `{sessions:[{id,title,mode,schema_name,created_at,updated_at}]}` 최근순 |
| POST | `/api/sessions?title=&mode=act&schema_name=` | | 세션 메타(id = 12자 hex) |
| PATCH | `/api/sessions/{id}?title=&schema_name=` | | `{status:"ok"}` |
| DELETE | `/api/sessions/{id}` | | `{status:"ok"}` |
| GET | `/api/sessions/{id}/messages?mode=act` | | `{messages:[…]}` (없으면 빈 배열) |
| PUT | `/api/sessions/{id}/messages?mode=act` | 화면 메시지 배열 | `{status:"ok"}` |

### 5.2 액션 프록시 (Studio 백엔드, 화면용)
화면은 실행기에 직접 붙지 않는다. 백엔드가 **화면 공용 신원 토큰**(`KINETIC_STUDIO_TOKEN`)으로 실행기 `/api/kinetic/...`을 부르고 결과·오류(상태코드 + `{error:{code,message}}`)를 그대로 돌려준다. 실행기에 못 닿으면 503 `unavailable`(문구 M7).

| 메서드 | 경로 | 요청 | 실행기 경로 |
|---|---|---|---|
| GET | `/api/act/health` | | `GET /api/kinetic/health` → `{url, identity{configured,sub,roles}, reachable, error?}` (M7) |
| GET | `/api/act/actions?class_name=` | | `GET /api/kinetic/actions?class=` |
| POST | `/api/act/plans` | `{class, action, where[], params{}}` | `POST /api/kinetic/plans` |
| POST | `/api/act/plans/by-ids` | `{class, action, ids[], params{}}` | `POST /api/kinetic/plans/by-ids` |
| GET | `/api/act/plans/{id}` | | `GET /api/kinetic/plans/{id}` |
| POST | `/api/act/plans/{id}/approve` | `{note}` (선택) | `POST /api/kinetic/plans/{id}/approve` |
| POST | `/api/act/plans/{id}/execute` | | `POST /api/kinetic/plans/{id}/execute` |
| GET | `/api/act/runs/{id}` | | `GET /api/kinetic/runs/{id}` |
| POST | `/api/act/runs/{id}/compensate` | `{reason}` (선택) | `POST /api/kinetic/runs/{id}/compensate` |

실행기에만 있는 것(화면 없음): `POST /api/kinetic/plans/{id}/reject`, `GET /api/kinetic/runs?limit=`, `POST /api/kinetic/runs/{id}/retry`, `GET /api/kinetic/audit?plan_id=`(admin 또는 approver; 아니면 403 「감사 로그는 승인자·관리자만 볼 수 있습니다.」), `POST /api/kinetic/catalog/refresh` → `{actions:<개수>}`.

실행기 MCP(에이전트용): `<실행기>/mcp`(또는 `/mcp/`), Bearer JWT 필수(없거나 무효면 401, `WWW-Authenticate` M7과 같음), 무상태 streamable HTTP, JSON 응답. 도구 9개: `list_actions(class?)`, `plan_action(class, action, where?, params?)`, `plan_action_ids(class, action, ids, params?)`, `execute_plan(plan_id)`, `get_plan(plan_id)`, `list_runs(limit=10)` → `{items:[…]}`, `get_run(run_id)`, `compensate_run(run_id, reason?)`, `query_system(system, operation_id, path_params?, query?)`. 실행기 오류는 도구 오류 결과로(`{error:{code,message}}`).

### 5.3 SSE 이벤트 (act에서 쓰는 것)
A3 §5.7 공통 계약에 더해:
| 이벤트 | data | 조건 |
|---|---|---|
| `kinetic_plan` | `{plan_id, status, requires_approval, tool}` | 도구 `plan_action`·`plan_action_ids`·`get_plan`의 결과가 오류 아닌 JSON이고 `id`와 `allowed`를 가짐 |
| `kinetic_run` | `{run_id, plan_id, status, tool}` | 도구 `execute_plan`·`get_run`·`compensate_run`의 결과가 `id`와 `targets`를 가짐 |
| `traversed_nodes` | `{tool, node_ids[]}` | 조회 도구(`ontology_graph_cypher`, `ontology_list_entities`, `ontology_resolve_entity`, 내장 `entity_search`, `neo4j_cypher_readonly`, `vector_search`) 결과에서 노드 id 추출 |
| `datasource_update` | (A3/M1) | 데이터소스 도구 |
| `neo4j_update` | `{tool}` | 그래프 쓰기 도구(act에서는 사실상 없음) |

- 도구 결과가 MCP 봉투(`{"result":"<json>"}`)에 싸여 오면 벗긴 뒤 판단한다(CLI 경로).
- 노드 id 추출 규칙: 결과가 배열이면 그 항목들, 객체면 자기 자신 + `nodes/entities/results/rows/matches/candidates/items/records` 배열의 항목들. 각 항목에서 `node_id`, `_element_id`, 또는 `:`를 포함한 문자열 `id`; 한 단계 안쪽 객체의 `id`/`_element_id`도. 순서 유지 중복 제거. 화면은 턴 동안 누적해 강조.
- `done`: `{message:"완료!", files, text, build_report:null}`.

## 6. 데이터 모델

### 6.1 계획(Plan)
```
{ id: "pln_<16 hex>", class, action, actor_sub, params{},
  where: [필터] | [{prop:<key_property 또는 "$elementId">, op:"in", value:[ids]}],
  status: planned|awaiting_approval|approved|rejected|executed|expired,
  requires_approval: bool, expires_at, created_at,
  allowed: [{key, props}], denied: [{key, props, reason}],
  preview: [{target_key, step, method, url, headers, body, compensable}],
  approved_by, approved_at, approval_note, run_id }
```
### 6.2 실행(Run)
```
{ id: "run_<16 hex>", plan_id, status: running|succeeded|partial|failed|compensated|partially_compensated,
  started_at, finished_at,
  targets: [{ key, status: pending|running|succeeded|failed|compensated|dead|skipped,
              http_status, response, error, attempts, finished_seq, before{}, compensated_by: auto|cancel|null,
              writeback_error?,
              steps: [{name, title, system, status: pending|succeeded|failed|skipped, http_status, response, error,
                       compensation: null | {status: succeeded|failed|none, http_status, response, at, error?}}] }],
  compensations: [{seq, at, target_key, step, system, operation_id, status, http_status, trigger: auto|cancel}],
  cancel: null | {actor_sub, reason, at} }
```
### 6.3 필터
`{prop, op, value?}`. op ∈ `= != > >= < <= in contains starts_with is_null not_null`. prop·클래스 이름은 `^[A-Za-z_가-힣][A-Za-z0-9_가-힣]*$`(아니면 「속성 이름 '<p>' 은 허용되지 않습니다.」). `in`은 스칼라 배열, `contains`/`starts_with`는 문자열, 그 밖은 스칼라, `is_null`/`not_null`은 값 없음. 클래스는 카탈로그에 액션이 있는 클래스여야 함(「클래스 '<C>' 은 발행된 클래스가 아닙니다.」). 값은 항상 질의 파라미터로(문자열 결합 금지). 원문 Cypher는 받지 않는다.

### 6.4 감사(Audit)
`{id, ts, event, actor_sub, request_id, plan_id, run_id, detail(JSON)}`. event: `plan, approve, reject, expire, execute, retry, compensate, query` (+ M7 레지스트리 이벤트). 요청 id = 요청 헤더 `x-request-id` 또는 새 값, 응답 헤더 `X-Request-Id`.

### 6.5 대화 저장 (A2/A3)
세션 메타 표, 화면 메시지(세션×모드 JSON), 에이전트 대화 기억(내장: 체크포인트, CLI: 메모리의 CLI 세션 id).

## 7. 지시문(스킬) — 구조와 계약 (ADR-0010)
act 모드 지시문 = **머리말** + `---` + `# 1부 — 질문 답변` + 답변 지시문 + `---` + `# 2부 — 액션 실행` + 액션 지시문. 참조 파일은 두 지시문 것을 합쳐 같은 스킬 폴더에 둔다(A3 스킬 배치 규칙).

머리말(라우팅만, 한국어 응답 지시):
- 질문(무엇·몇·얼마·왜·어디·보여줘) → 1부, 아무것도 바꾸지 않음.
- 바꾸라는 요청 → 2부(계획 → 보여 주기 → 확인/승인 → 실행). 취소·되돌려·원복 → 2부 취소 절차.
- 섞인 요청 → 1부로 대상 조회해 보여 준 뒤 2부. 질문만 받았으면 액션 제안은 가능하나 계획·실행 금지.
- 1부의 "조회 전용"은 조회 도구에 대한 말이고, 외부 시스템을 바꾸는 유일한 길은 2부 도구이며 2부의 절대 규칙이 우선.

답변 지시문(요지): 도구가 없으면 답하지 않음 / 조회 전용, 카탈로그·발행 레지스트리 라벨 금지 / 흐름: (개념 질문이면 의미 검색) → 온톨로지 지도 1회 → 이름을 실제 키로 해석 → 그래프 탐색 → 필요한 클래스 하나의 데이터소스 스키마 → DB가 집계하는 SQL / 규칙: 조회 없이 답하지 않기, id 지어내지 않기, 원시 행 받아 직접 집계하지 않기(파생 계산은 식과 함께), LIMIT은 인자로, **근거 밝히기(그래프: 노드 이름/번호, 데이터: `datasource.table`과 행 수)**, 기본 조건 반영, 잘린 결과 명시, 조회 실패를 "없다"로 말하지 않기 / 완료 기준: 실제 조회 근거, 그래프·데이터 근거 함께, 답할 수 없으면 이유.

액션 지시문(요지):
- 절대 규칙: 원문 Cypher로 대상 지정 금지(구조화 필터만, 속성명은 조회로 확인) / 목록에 없는 액션 지어내지 않기 / 키 지어내지 않기 / **승인 우회 금지(임계치 회피용 계획 쪼개기 포함)** / **명시적 확인 없이 실행 금지("바꿔줘"는 확인이 아님)** / 조회 도구로 쓰기 금지 / 취소할 run 지어내지 않기.
- 8단계: ① 의도(무엇·어떻게·왜, 필수 파라미터 없으면 묻고 멈춤) ② 액션 고르기 ③ 대상 조건 → 필터(이름이면 키 해석 후 ids 계획; 스냅숏 값이 바뀌었을 수 있으면 조회 API로 현재 값 확인, 요청대로 못 하면 선택지 제시하고 멈춤) ④ 계획 ⑤ 표로 보여 주기(허용/거부 표, 허용 N·거부 M, plan id, 만료, 단계 순서, 되돌릴 수 없는 단계, 첫 호출 미리보기; 거부 사유는 그대로) ⑥ 분기(허용 0 → 멈춤·실행 제안 금지; 승인 필요 → "Studio 의 plan 카드에서 승인이 필요합니다" 안내 후 멈춤, 다음 말에서 계획 상태가 approved인지 확인; 승인 불필요 → "위 N건에 실행할까요?" 묻고 멈춤) ⑦ 실행(승인된 그 plan id 그대로, 재계획 금지; 만료면 재계획 후 ⑤부터) ⑧ 결과 표(대상·단계별, skipped·자동 보상·dead 의미 설명, 실패를 성공처럼 요약 금지).
- 취소 5단계: run 정하기(하나면 그것, 여럿이면 묻기) → 되돌릴 순서 설명 → 모호하면 확인 → `compensate_run` → `compensations`를 seq 순 표로. 여러 건 취소는 `list_runs`에서 cancellable을 최근 것부터 하나씩.
- 완료 기준: 실행된 것은 사용자가 본 계획의 허용 대상이고 확인(필요 시 승인)이 앞섰음, 결과를 대상·단계별로 정직하게 보고, 못 했으면 이유.

## 8. 상태·저장
| 무엇 | 어디 | 수명 |
|---|---|---|
| 대화 메타·화면 메시지 | 세션 DB(`<사용자 데이터>/sessions.db`) | 영구, 대화 삭제 시 삭제 |
| 에이전트 대화 기억 | 내장: 세션 DB 체크포인트(`<세션>:act` 줄기) / CLI: 백엔드 메모리 | 내장 영구, CLI는 재시작·전환 시 소실 |
| 계획·실행·감사 | 실행기 DB(`<사용자 데이터>/kinetic.db`) | 영구, 화면에서 지울 수 없음 |
| 액션 카탈로그 | 실행기 메모리(그래프에서 30초 주기) | — |
| 업무 데이터 변경 | 업무 시스템(예제는 원천 DB `sample`) | 보상으로만 되돌림 |
| 되쓰기 값 | 온톨로지 그래프 노드 속성 | 취소 시 원복 |
| 화면 신원 | 백엔드 환경 `KINETIC_STUDIO_TOKEN`(부팅마다 30일 토큰, M7) | — |

## 9. 승인 분리 — 원본의 보장 수준과 구현 권고 (보안)

### 9.1 원본이 구조로 보장하는 것 (관찰)
- 에이전트의 모든 도구 표면(브리지 act, 내장 act, 실행기 MCP)에 승인 도구가 없다.
- 에이전트 도구는 에이전트 신원(`lite-agent`, 역할 `scm_operator`)으로 실행기를 부르며, 실행기 승인은 `kinetic_approver` 역할을 요구한다.
- 실행은 계획 작성자만 가능, 승인 필요 계획은 승인 전 실행 불가.
- 화면 승인은 별도 신원(`lite-user`, 역할 `kinetic_admin`·`kinetic_approver`·`scm_operator`)으로 백엔드 프록시를 거친다.

### 9.2 원본에서 뚫리는 지점 (관찰된 조건 + 추정된 결과)
- 실행기는 승인자 ≠ 작성자 검사가 없다(역할만 본다). (관찰)
- Studio 백엔드는 인증이 없다(127.0.0.1, CORS 모든 오리진). 승인 프록시 `POST /api/act/plans/{id}/approve`를 부르는 누구든 화면 신원으로 승인된다. (관찰)
- CLI 에이전트는 권한 우회 모드로 셸을 쓰고, 백엔드 환경 전체(화면 신원 토큰 `KINETIC_STUDIO_TOKEN`, `KINETIC_URL`, 백엔드 포트)를 상속하며, MCP 설정 URL에도 백엔드 포트가 있다. 사용자 데이터 폴더의 비밀 파일에는 토큰 서명 개인키도 있다. (관찰)
- 그러므로 에이전트가 지시문을 어기면(프롬프트 주입 포함) 셸에서 승인 경로를 직접 불러 자기 계획을 승인하고 `execute_plan`으로 실행할 수 있다. 감사 기록상 승인자는 `lite-user`로 남아 사람 승인과 구별되지 않는다. (추정 — 실행 검증 안 함)
- 내장 에이전트의 act 모드에는 셸 도구가 없어 이 경로가 없다(단 build 모드 셸 도구는 같은 환경을 가진다). (관찰)

### 9.3 새 구현 권고 (원본과 다르게 할지 결정 필요)
1. 승인 경로에 **사람 상호작용 증거**를 요구: 화면 세션에만 발급하는 일회용 승인 토큰(CSRF 토큰과 유사, 백엔드 메모리 보관, 에이전트 프로세스 환경에 없음) 또는 셸 창의 네이티브 확인 대화상자.
2. 에이전트 자식 프로세스 환경을 화이트리스트로(화면 신원 토큰·DB 비밀번호·실행기 주소 제외). 서명 키를 에이전트가 읽을 수 없는 곳(OS 키체인)에.
3. 실행기에서 직무 분리 옵션: 승인자 sub ≠ 작성자 sub이면서 승인자가 에이전트 신원이 아닐 것.
4. 감사에 승인 출처(화면/기타)와 화면 세션 id를 남김.
5. 비교 테스트는 원본 계약(§11)으로 하되, 이 완화가 원본 화면 흐름을 바꾸지 않도록(사람이 카드에서 승인 → 에이전트가 실행) 설계.

## 10. 다른 기능과의 의존
- A3: 에이전트 선택·CLI 실행·브리지 MCP·SSE·스킬 배치·끼어들기.
- A2: 세션 DB, 그래프 접속.
- 검색 MCP 서버(A3): 질문 도구의 실제 구현. 실데이터 확장(`MCP_ALLOW_DATASOURCE_EXPANSION`, 앱 기본 켬)이 꺼지면 데이터소스 도구가 사라지고 답이 그래프 근거로만 제한.
- M1: 액션 정의·발행(카탈로그 원천), 골든 커맨드. 발행 시 실행기 카탈로그 갱신 요청.
- M7: 실행기 프로세스·레지스트리·업무 시스템 호출 계약·신원 토큰·JWKS.
- M3/M4: 실행 결과 확인(데이터소스 미리보기, 포털 Cypher).
- M5: 대시보드 액션 버튼·코드 앱 `act()`가 같은 프록시(§5.2)를 쓰며, 그 계획은 화면 신원이 작성자라 카드에서 바로 「실행」 가능.

## 11. 오류·예외
| 상황 | 동작 |
|---|---|
| 실행기 미기동 | `/api/act/health` → `reachable:false`(+셸 대체 문구, M7). 에이전트 도구 → `{"error":"키네틱 …","hint":"…"}`, 지시문상 추측 진행 없이 안내 후 멈춤 |
| 검색 MCP 서버 불통 | 질문 도구 → `{"error":"온톨로지 …","hint":"ontology_mcp 서버(기본 8100)가 …"}` |
| 액션 미발행/권한 없음 | 404 `not_found` / 403 `forbidden` |
| 파라미터·필터 오류 | 422 `invalid_params` / `invalid_filter` |
| 대상 초과 | 422 `too_many_targets` |
| 비REST 시스템 액션 | 422 `not_executable` |
| 승인 전 실행 | 409 `approval_required` |
| 만료 | 409 `plan_expired` (승인·실행 모두) |
| 상태 충돌 | 409 `conflict` |
| 허용 0건 실행 | 409 `nothing_to_execute` |
| 작성자 아님 | 403 `not_plan_owner` |
| 승인 역할 없음 | 403 `forbidden` 「역할 'kinetic_approver' 이 필요합니다.」 → 카드 「승인 권한이 없습니다 (…)」 |
| 토큰 무효·만료 | 401 `unauthenticated` → 백엔드 문구 「kinetic-action 인증 실패 — KINETIC_STUDIO_TOKEN 을 확인하세요.」 |
| 단계 실패 | 대상 자동 보상, run `partial`/`failed` |
| 보상 실패 | 대상 `dead`(「사람 처리 필요」), run `partially_compensated` |
| 되쓰기 실패 | 결과 유지, `writeback_error` |
| 에이전트 턴 오류 | `error_event` (A3) |

## 12. 원본과 비교할 테스트 항목 (구조·계약, ADR-0010)
1. 빈 화면 문구·예시 4개·입력 안내문이 같다. 파일 첨부 불가.
2. 질문 턴 SSE 이름 순서 패턴: `status`("질의·액션 모드 실행 시작...") → (`tool_start` → [`traversed_nodes`] → `tool_result`)+ … `token`+ … → `done`. 질문 턴에서 `kinetic_plan`·`kinetic_run` 없음, 실행기 감사에 plan 행 없음.
3. 질문 턴 도구 이름 집합이 §4.2 목록의 부분집합.
4. 지시 턴: `list_actions` → (조회) → `plan_action|plan_action_ids` 호출, `kinetic_plan{plan_id,status:"awaiting_approval",requires_approval:true,tool}`, 턴 안에서 `execute_plan` 호출 없음.
5. 계획 응답 필드 집합(§6.1)과 예제 값: 허용 SHP-02·SHP-03, 거부 0, 미리보기 4건, 만료 = 생성+600초, 작성자 `lite-agent`.
6. 카드: 승인 대기 시 메모+「승인」만, 실행 버튼 없음; 승인 후 안내문 문구; 화면 계획(작성자 lite-user)이면 「실행 (N건)」.
7. 승인 요청/응답(`approved_by:"lite-user"`, `approval_note`), 재승인 409 `conflict`.
8. "실행해" 턴: `get_plan` → `execute_plan`(같은 plan id), `kinetic_run`, 재계획 없음. run 필드 집합(§6.2), 단계별 Idempotency-Key 형식, 업무 시스템 호출 순서(대상 안 wms → erp).
9. 원천 DB 차이: priority NORMAL→URGENT, 독촉 2건; 그래프 되쓰기 속성 값.
10. 취소(대화·카드 각각): `compensations` seq 순서 = 대상 실행 완료 역순 × 단계 역순(예제 4행), 보상 Idempotency-Key `:c`, `$before` 복원, run `compensated`, 재취소 시 같은 결과.
11. 오류 코드·상태: 미승인 실행 409 `approval_required`, 만료 409 `plan_expired`, 다른 신원 실행 403 `not_plan_owner`, 에이전트 토큰 승인 403 `forbidden`.
12. 감사 행 순서: plan → approve → execute → compensate, actor_sub 값.
13. 세션: 생성 `mode=act`, 제목 30자 규칙, 메시지 저장·복원 후 카드 재조회, 홈 최근 항목 종류 문구.
14. 끼어들기: Claude Code에서 `delivered:true` + `steered`, Codex/내장 false.
15. `kinetic_plan`/`kinetic_run`/`traversed_nodes` 이벤트 생성 조건(§5.3)과 노드 id 추출 규칙(단위 시험으로 같은 입력에 같은 출력).

## 13. 모르는 점 (4단계 실행 기록에서 확인)
- 에이전트가 실제로 셸에서 승인 경로를 부를 수 있는지(§9.2) — **실험은 분석용 폴더에서만, 사용자 결정 후**. 최소한 CLI 프로세스 환경에 `KINETIC_STUDIO_TOKEN`이 실제로 있는지 확인.
- CLI 경로에서 "실행해" 후속 턴이 `--resume`으로 앞 plan id를 기억하는지, 재시작 뒤에는 `get_plan`/`list_runs`로 복구하는지.
- 계획 카드가 대화 안 어디에 놓이는지(도구 칩 사이/메시지 끝), 메시지 저장 시점(턴 끝마다인지).
- 대화의 "근거·경계" 문단이 실제로 지시문대로 나오는지(답 구조), 그래프 강조 노드 수와 답에 언급된 노드의 관계.
- `writeback_property`의 값: 예제 WMS 단계 응답에 `status` 필드가 있는지(없으면 `"done"`이 priority에 기록될 수 있음 — 튜토리얼은 "선적 우선순위가 온톨로지에 반영"이라 함).
- 예제 `expediteShipment`의 정책 대상 속성(`ship_status`)이 발행 그래프 노드에 실제로 있는지, 대상 조회가 물리 노드인지 가상 노드인지.
- 화면 카드의 run 단독 카드가 언제 생기는지(plan 이벤트 없이 `get_run`만 부른 경우 등).
- `act` 모드 대화를 삭제해도 내장 에이전트 체크포인트(`<세션>:act`)가 남는 원본 동작이 관찰 가능한 차이를 만드는지(같은 id 재사용은 드묾).
- 튜토리얼의 📎 문서 첨부(13장)는 0.1.1 act 모드에서 꺼져 있음 — 실제 화면 확인.
- 실행기 MCP의 DNS 리바인딩 보호가 꺼져 있고 Bearer 필수인 조합에서 브라우저발 요청이 어떻게 되는지(토큰 없으면 401이므로 영향 작을 것으로 추정).
- 원본 계획 TTL(600초)이 화면에서 「만료」로 바뀌는 시점(조회 시에만 갱신 — 카드를 새로고침해야 바뀜).
