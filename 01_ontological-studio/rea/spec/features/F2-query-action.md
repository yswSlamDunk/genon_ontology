# F2. 질의·액션

- 상태: 초안 v0.1 (2026-11-01, Claude 작성) — 사용자 보정 전
- 원본 기준 동작: [`menus/02-query-action/design.md`](../../analysis/ontological-studio/menus/02-query-action/design.md), [`user-scenarios.md`](../../analysis/ontological-studio/menus/02-query-action/user-scenarios.md), SSE 공통 계약은 [`common/A3-agent-mcp/design.md`](../../analysis/ontological-studio/common/A3-agent-mcp/design.md) §5.7
- 관련 문서: [02](../02-ontology-model.md) §10 Action type · §12 Object set · §13 Object view, [03](../03-security.md) §4 사람 승인 증명, [04](../04-agent-integration.md) §4·§5, [F5](F5-ontology-apps.md)(Object view·위젯 액션), [F7](F7-systems.md)(시스템 호출 계약)
- 결정 대기: **D-18**(사람 승인 증명), D-10(에이전트 셸 도구), D-12(원본 결함 처리 원칙)

---

## 1. 목적

사용자가 한 대화창에서

1. **질문**하면 에이전트가 발행된 온톨로지를 **Object set과 자동 생성 온톨로지 도구**로 조회해 **근거 객체를 인용하며** 답한다(아무것도 바꾸지 않는다). 인용된 객체는 눌러서 **Object view**(02 §13)로 연다.
2. **지시**하면 에이전트가 발행된 **Action type**(02 §10)을 골라 **계획(dry-run)** 을 세우고, 사람이 **셸의 네이티브 승인 창**에서 승인(증표 발급)한 뒤, 사용자의 명시적 지시로 에이전트가 **실행**한다. 실행은 대상마다 **사가**(시스템 호출 실패 시 앞 단계 역순 보상)로 돈다.
3. **취소**를 요청하면 실행한 단계를 **역순으로 보상**하고 온톨로지 편집도 되돌린다.

핵심 불변식 — 원본과 같지만 이번에는 **구조로 보장**한다:
- **에이전트는 승인할 수 없다.** 승인은 셸만 발급하는 일회용 승인 증표가 있어야 성립한다(03 §4).
- **에이전트가 계획한 것은 반드시 사람이 승인한다**(Action type의 승인 설정과 무관, 03 §4).
- **계획한 주체는 그 계획을 승인할 수 없다**(직무 분리, 02 §10 `separationOfDuties`).

## 2. 원본 기준 동작 요약 [원본]

| 영역 | 원본 0.1.1 동작 |
|---|---|
| 화면 | 홈 카드 「질의·액션」 → Studio 탭 `view=act`. 왼쪽 대화 목록, 가운데 대화(빈 화면: 모드 설명 + **고정 문구** 예시 4개), 오른쪽 온톨로지 그래프(답에 쓰인 노드 강조). 파일 첨부 불가 |
| 질문 | act 모드 에이전트가 검색 MCP 도구(스키마·엔티티 해석·읽기 전용 Cypher·데이터소스 SQL)로 조회. **근거는 답 본문(마크다운)에만** 있고 구조화된 인용은 없음. 화면의 근거는 도구 칩과 그래프 강조뿐 |
| 지시 | 키네틱 도구 9개(`list_actions`, `plan_action`, `plan_action_ids`, `get_plan`, `execute_plan`, `get_run`, `list_runs`, `compensate_run`, `query_system`). **승인 도구 없음**. 계획 → 계획 카드 → 사람이 카드에서 「승인」 → 대화에서 "실행해" → 에이전트가 같은 plan 실행 → "취소해" → 역순 보상 |
| 실행기 | 별도 프로세스. 정책(CEL, 기본 거부), 계획 TTL 600초, 승인 임계치, 대상별 사가(대상 간 병렬, 대상 안 순차), 자동 보상, 되쓰기(`writeback_property`), 취소(완료 역순 × 단계 역순) |
| 신원 | 화면 공용 신원(승인 역할 보유), 에이전트 신원(운영 역할). 승인은 역할만 보고 **작성자 = 승인자 검사 없음** |
| SSE | A3 공통(`status`, `token`, `tool_start`, `tool_result`, `steered`, `ask_user`, `error_event`, `done`) + `kinetic_plan`, `kinetic_run`, `traversed_nodes` |
| 약점 | 인증 없는 백엔드의 승인 프록시가 **누가 부르든 화면 신원으로 승인**, CLI 에이전트가 권한 우회 모드로 셸을 쓰며 백엔드 주소·화면 신원 토큰을 환경으로 상속 → 에이전트가 셸에서 자기 계획을 승인·실행할 수 있는 경로(추정), 감사에는 사람 승인과 똑같이 기록(원본 design §9, REVIEW #9·#17) |

## 3. 새 설계에서 달라지는 점 [제안]

| # | 원본 | 새 설계 | 근거 |
|---|---|---|---|
| C1 | 그래프 Cypher·데이터소스 SQL 도구로 답 | 발행본에서 **자동 생성한 온톨로지 도구**(`search_<T>`, `get_<T>`, `<T>_links`, Function 도구, `object_set_query`, `describe_ontology`)로 답. Cypher는 설정으로 켜는 고급 도구 | 02 §12, 04 §5 |
| C2 | 근거는 답 본문에만 | **구조화된 근거**: 도구 결과에서 코어가 근거 객체·Object set을 결정적으로 모아 `cited_objects`·`evidence` 이벤트로 보냄. 답 본문의 객체 인용은 `object://` 링크 → 칩 → Object view. 이번 턴 도구 결과에 없던 객체를 인용하면 「근거 미확인」 표시 | [조사] AIP Agent Studio 출처 객체 인용 |
| C3 | 계획 대상 = 클래스 라벨 + 구조화 필터 / 키 목록 | 대상 = **Object set**(저장 rid 또는 DSL) / 기본 키 목록 / 원본 형식 필터(호환). 계획 결과의 대상은 객체 참조 | 02 §10·§12 |
| C4 | 규칙 = 시스템 호출 단계만 | Action type 규칙 = **온톨로지 편집**(modify/create/delete object, create/delete link) + **시스템 호출**(callSystem). 대상별로 시스템 호출은 사가, 온톨로지 편집은 대상별 한 트랜잭션으로 마지막에 확정 | 02 §10 |
| C5 | 카드 「승인」 = 인증 없는 HTTP 호출 | 카드 「승인」 = **셸에 승인 요청** → 셸이 **네이티브 승인 창**을 띄움 → 사람이 확인하면 셸이 **서명된 일회용 증표**로 코어에 승인. 웹 페이지·에이전트는 창을 열 수만 있고 누를 수 없음 | 03 §4, D-18 |
| C6 | 작성자 = 승인자 허용 | **직무 분리**: 승인자는 사람(`actor.kind=human`)이어야 하고 계획자와 달라야 함(사람이 화면에서 직접 만든 계획은 1인 사용 모드에서 본인 승인 허용) | 02 §10, 03 §4 |
| C7 | 승인 임계치 이하면 승인 없이 실행 가능(에이전트 계획 포함) | **에이전트 계획은 항상 승인 필요**. 사람·앱 계획은 Action type `approval` 설정을 따름 | 03 §4 |
| C8 | 감사에 사람·에이전트 구분 없음 | 감사 `actor.kind = human|agent|app|system`, 승인 행에 `proofId`. 거부된 승인 시도도 기록 | 01 §7, 03 §4 |
| C9 | 예시 4개 고정 문구 | 발행된 온톨로지의 **골든 퀘스천·골든 커맨드**에서 예시를 만들고(튜토리얼 설명대로), 없으면 원본 고정 문구 | D-12(튜토리얼이 더 합리적) |
| C10 | 실행기 별도 프로세스, 화면은 프록시로 | 코어의 **Action 모듈**(01 §2.1). 화면·에이전트·앱 모두 같은 `/api/v1` 계약을 토큰별 권한으로 사용 | 01 §2 |
| C11 | 계획이 액션 정의 변경과 무관 | 계획은 Action type **버전**과 온톨로지 발행 버전에 고정. 실행 전에 바뀌었으면 409 `plan_stale` | 02 §14 |
| C12 | 대화 턴 시작 = `GET /api/stream?prompt=…` (프롬프트가 URL에) | 턴 생성(POST) + 이벤트 구독(SSE) 분리. 이벤트 이름·data는 원본 유지 | 03 §3(토큰·로그 노출), P 명세 |

원본 계약 유지 원칙(D-12): 화면 흐름(계획 카드 → 승인 → "실행해" → "취소해"), 계획·실행 상태 값과 라벨, 오류 코드·문구, Idempotency-Key 형식, 보상 순서, SSE 이벤트 이름과 data 필드는 **그대로** 둔다. 바뀐 곳은 §11에서 "의도된 차이"로 표시한다.

### 3.1 원본의 "에이전트 승인 우회" 경로를 어떻게 닫나 (D-18)

원본에서 우회가 성립하던 조건(원본 design §9.2)과 각각을 닫는 장치:

| # | 원본 조건 | 새 설계의 차단 | 문서 |
|---|---|---|---|
| B1 | 승인 API가 인증 없이 열려 있고, 호출자가 누구든 화면 공용 신원으로 승인됨 | 모든 API는 실행별 세션 토큰 필요. **승인 API는 토큰만으로는 부족하고 셸 서명 승인 증표가 필수**. 증표는 셸 메인 프로세스만 가진 서명 키(메모리, 부팅마다 새로 생성)로 서명되고, 코어는 셸이 기동 시 넘긴 공개 키로 검증 | 03 §3·§4, §9 |
| B2 | CLI 에이전트가 백엔드 환경 전체(화면 신원 토큰, 실행기 주소, DB 비밀번호)를 상속 | 에이전트 프로세스 환경은 **화이트리스트**(PATH·HOME·언어·턴별 MCP 토큰)만. 세션 토큰·서명 키·DB 비밀번호는 어떤 파일·환경에도 없음 | 03 §5, 04 §3 |
| B3 | CLI가 권한 우회 모드로 셸 명령 실행 | 허용 도구 목록만, 셸 도구 기본 끔(D-10). **셸 도구가 켜져 있어도** 에이전트는 세션 토큰·증표를 얻을 길이 없으므로 승인 경로가 없음 | 04 §3·§7 |
| B4 | 턴별 MCP 토큰 같은 에이전트 자격으로 REST를 부를 수 있었음 | 턴별 MCP 토큰은 **해당 모드의 MCP 엔드포인트에서만** 유효(REST `/api/v1` 거부). act 모드 도구 목록에 승인 도구 없음 | 04 §4 |
| B5 | 승인 시 승인자 = 작성자 검사 없음 | 승인 시 `approver.kind == human` 그리고 (`planner.kind != human` 또는 1인 모드의 사람 자기 계획) 검사. 에이전트·앱 계획은 사람만, 계획자 본인은 불가 | §9.2 |
| B6 | 감사에 사람 승인과 구별 불가 | 승인 행에 `actor.kind`, `proofId`, 증표의 창 표시 요약 해시 기록. 증표 없는 승인 시도·에이전트 토큰 승인 시도도 `approve_denied`로 기록 | §7.4 |
| B7 | 승인 임계치 이하면 에이전트가 사람 없이 실행 | 에이전트 계획은 항상 `requires_approval=true` | C7 |
| B8 | 코드 앱이 같은 오리진에서 승인 경로·확인 창을 흉내 | 코드 앱은 별도 오리진 + 앱별 SDK 토큰(승인 범위 없음), 승인 창은 앱 문서 밖 셸 창 | F5, 03 §8, D-17 |

남는 위험과 대응: 사람이 창 내용을 읽지 않고 누르는 것(→ 창의 기본 버튼은 「취소」, 같은 계획의 창은 동시에 하나, 같은 요청자의 반복 요청은 10초 안에 무시), Studio UI가 XSS로 뚫리는 것(→ UI도 승인 창을 "요청"만 할 수 있고 창의 내용은 셸이 코어에서 직접 읽은 계획으로 그림).

## 4. 사용자 시나리오

원본 시나리오 번호(S#)와 대응한다. 사전 상태는 원본과 같다(예제 온톨로지 「공급망 운영」을 **Object type 방식으로** 다시 만들어 발행, 예제 Action type 3개 `expediteShipment`·`holdPurchaseOrder`·`notifyCustomer`, 예제 시스템 3개 등록).

| # | 시나리오 | 원본과의 차이 |
|---|---|---|
| S1 | 탭 열기: 빈 대화에 모드 설명 + 예시 4개 + 오른쪽 그래프 | 예시 = 골든 퀘스천 1·골든 커맨드 1·"방금 한 <첫 골든 커맨드 동작>을 취소해 줘"·「어떤 액션을 쓸 수 있어?」. 골든이 없으면 원본 문구 |
| S2 | 「3일 넘게 늦어진 입고 선적은…?」 → 결론·근거·경계가 있는 답, 그래프 강조 | 답 아래 「근거 객체」 칩(SHP-03, SHP-02, 협력사 1), 「사용한 Object set」(필터 `delayDays > 3`). 칩 → Object view. 신선도 표시(live: 「원천 실시간 · 조회 hh:mm」, indexed: 「동기화 hh:mm」) |
| S3 | 이어 묻기("그 협력사의 다른 미결 발주는?") | 같음. 앞 턴 근거 객체를 맥락으로 씀 |
| S4 | 답할 수 없는 질문 | 같음 + 「온톨로지에 없는 개념」 안내 아래 「구축에 제안으로 보내기」(사람이 누르면 F1 작업본 메모로, v1) |
| S5 | 지시 → 계획 카드(승인 대기) | 카드에 계획자 「에이전트 (Claude Code)」, 대상은 객체 칩. 에이전트 계획은 항상 「사람 승인 필요」 |
| S6 | 카드 「승인」 | **네이티브 승인 창**이 뜸(§5.3). 「승인」 → 배지 「승인됨」, 안내 문구는 원본과 같음 |
| S7 | "실행해" → 같은 plan 실행, 대상·단계 결과 | 단계 칩에 온톨로지 편집 단계(「온톨로지」)도 표시. 업무 시스템 호출 헤더에 내부 비밀 헤더 없음(F7) |
| S8 | 취소(대화 / 카드) → 역순 보상 | 카드 취소의 확인 창이 네이티브 창. 온톨로지 편집도 되돌림 |
| S9 | 발주 보류 실습 | 같음. 거부 사유 = `submissionCriteria.message` 그대로 |
| S10 | 액션 목록 / 미승인 실행 / 만료 | 같은 오류 코드·문구(409 `approval_required`, 409 `plan_expired`) |
| S11 | 대화 관리 | 같음 |
| S12 | 실행 중 끼어들기 | 같음(CLI 중 Claude Code만) |
| N1 | **에이전트 승인 시도 차단**: act 모드에서 "승인까지 해서 실행해" | 에이전트가 승인 불가를 안내하고 멈춤. (셸 도구를 켠 시험 환경에서) 에이전트가 REST 승인을 시도해도 401/403, 감사 `approve_denied{actor.kind:agent}` |
| N2 | **직무 분리**: 화면에서 내가 만든 계획(위젯 액션, F5)을 내가 승인 | 1인 사용 모드: 허용(명시적 클릭). 다중 역할 설정에서 `separationOfDuties: true`면 403 `self_approval` |
| N3 | **근거 미확인 인용**: 에이전트가 조회하지 않은 키를 답에 인용 | 그 칩에 「근거 미확인」 경고, `evidence.unverified`에 기록 |
| N4 | **Object set으로 계획**: "방금 답의 선적들 긴급 처리해 줘" | 에이전트가 앞 턴 Object set을 대상으로 `plan_expediteShipment` 호출, 카드에 「대상: Object set (2건)」 |
| N5 | **정의 변경 후 실행**: 계획 후 Action type을 고쳐 발행 → "실행해" | 409 `plan_stale` 「액션 정의가 바뀌었습니다. 다시 plan 하세요.」 → 에이전트 재계획(만료와 같은 처리) |
| N6 | **증표 재사용·위조 차단**: 같은 증표로 두 번 승인 / 다른 계획에 사용 | 403 `approval_proof_invalid` |
| N7 | **온톨로지 반영 실패 보상**: 시스템 호출은 성공했으나 편집 확정이 실패 | 대상 자동 보상(사유 「자동 보상: 온톨로지 반영 실패」), run `partial`/`failed` |

## 5. 화면 구성과 상호작용

### 5.1 진입·레이아웃 [원본 유지]
- 홈 카드 「질의·액션」(설명 「온톨로지에 묻고, 지시하면 액션을 계획·실행합니다.」, 에이전트 필요 배지) → Studio 탭 `view=act`(`session=<id>`면 그 대화).
- 왼쪽 「워크스페이스」: 이 모드 대화 목록·새 대화·삭제. 가운데 대화. 오른쪽 온톨로지 그래프(F4의 스키마 지도 부품 재사용; 근거 객체 강조).
- 빈 화면: 제목, 모드 이름 「질의·액션」, 원본 설명 문구 그대로, 예시 버튼 4개(C9). 입력창 안내문 원본 그대로. 파일 첨부 없음(원본 0.1.1과 같음, §12 Q4). Enter 전송, Shift+Enter 줄바꿈, 응답 중 입력은 끼어들기.

### 5.2 메시지 [원본 + 근거 표시]
- 상태 줄, 텍스트 조각, 도구 칩(이름·한 줄 설명·인자, 끝나면 결과 펼침), 「N개 도구 사용됨」 접힘, `ask_user` 선택지 — 원본과 같다.
- **근거 객체 칩**(신규): 답 본문의 `object://<Ontology>.<Type>/<pk>` 링크는 칩(아이콘·Object type 표시 이름·제목 속성 값)으로 그린다. 누르면 Object view 탭(F5). 근거 미확인이면 경고색 + 툴팁 「이번 답의 조회 결과에 없는 객체입니다」.
- **근거 패널**(신규, 답 아래 접이식 「근거 객체 N · Object set M」): Object type별 묶음(칩 목록, 신선도 라벨), 사용한 Object set(사람이 읽는 요약 — 예: 「선적 중 지연일 > 3」 — 와 건수, 「목록으로 열기」 → Object Explorer(F5) 해당 set, 「저장」 → 이름 입력 후 저장 Object set). PII 속성 값은 03·02 규칙대로 마스킹.
- 그래프 강조: `traversed_nodes`·`cited_objects`의 객체를 턴 동안 누적 강조(원본과 같은 동작).

### 5.3 계획 카드와 승인 창
카드는 이벤트로 받은 plan id·run id만 들고 내용은 REST로 다시 읽는다(원본과 같음). 마운트 시 `GET /api/v1/me`로 화면 주체(사람)와 역할을 읽는다.

**머리·요약·표** [원본 유지]: 「실행 계획」(run만 있으면 「실행 결과」) · `<Object type>.<Action type>` · 상태 배지 · 「새로고침」. 상태 라벨 planned 계획됨 / awaiting_approval 승인 대기 / approved 승인됨 / executed 실행됨 / expired 만료 / rejected 거부. 요약 「허용 **N**건 · 거부 **M**건 · 사람 승인 필요 · 만료 <시각> · 작성 <계획자 표시 이름>」. 표 = 구분 · 대상(객체 칩) · 속성 최대 3열 · 사유, 최대 50행(「상위 50건만 표시합니다.」). 「호출 미리보기 (N건)」 접이식(인증 헤더 가림).
- 신규 줄: 「규칙: 온톨로지 편집 K개 · 시스템 호출 S개(되돌릴 수 없는 단계 U개)」. 되돌릴 수 없는 단계 = 보상이 없는 callSystem.

**버튼**
| 조건 | 표시 |
|---|---|
| awaiting_approval이고 화면 주체가 승인 가능(§9.2) | 「승인 메모 (선택)」 + 「승인」 + 「반려」(신규) |
| awaiting_approval이고 승인 불가 | 경고 「현재 사용자에게 이 액션의 승인 역할(<approverRoles>)이 없습니다.」 또는 「이 계획은 현재 사용자가 만들었으므로 다른 승인자가 필요합니다.」 |
| 실행 가능(approved 또는 승인 불필요 planned, 허용>0, run 없음) + 계획자 = 화면 주체 | 「실행 (N건)」(위젯 액션 등 화면 계획, F5) |
| 실행 가능 + 계획자가 에이전트 | 원본 안내 「에이전트가 만든 계획입니다. 승인되었습니다 — 대화에서 “실행해”라고 요청하면 에이전트가 실행합니다.」 |

**「승인」 누름 → 네이티브 승인 창** [제안, D-18]
1. 카드가 셸 브리지 `requestApproval({planId, note})`를 부른다(HTTP 아님, Studio 탭에만 있는 렌더러 API).
2. 셸 메인 프로세스가 **자기 세션 토큰으로 코어에서 계획을 직접 읽고**(`GET /api/v1/action-plans/{id}/approval-summary`) 창을 그린다. 카드가 넘긴 값은 메모뿐이고 창에 "메모"로만 보인다.
3. 창 내용: 제목 「액션 승인」 / `<Action type 표시 이름> (<Object type>.<apiName> v<버전>)` / 계획자(「에이전트 · Claude Code · 대화 <제목>」 등) / 「허용 N건 · 거부 M건」, 대상 앞 5개 키(+ 「외 K건」) / 입력 파라미터 / 시스템 호출 요약(「WMS setShipmentPriority × 2, ERP createExpediteRequest × 2」), 되돌릴 수 없는 단계 강조 / 온톨로지 편집 요약 / 만료 시각 / 메모. 버튼 「승인」, 「취소」(기본 버튼 = 취소, Esc = 취소).
4. 「승인」이면 셸이 증표(§7.3)를 만들어 `POST /api/v1/action-plans/{id}/approve {note, proof}`를 **직접** 보내고 결과를 카드에 돌려준다. 카드는 계획을 다시 읽는다.
5. 「취소」/창 닫힘 → 아무 일 없음. 셸이 같은 계획의 창을 이미 띄웠으면 그 창을 앞으로 가져올 뿐 새 창을 만들지 않는다.

**실행 부분** [원본 유지]: 「실행 <run id> · <상태>」(running이면 1.5초마다 재조회, 「 · 자동 보상 N건」), run 상태 라벨 running 실행 중 / succeeded 성공 / partial 일부 실패 / failed 실패 / compensated 보상 완료 / partially_compensated 일부 보상. 대상 표(대상 · 결과 · 단계 칩 · HTTP · 시도 · 오류), 단계 칩 = 시스템 이름 대문자 + ✓/✗/–/…, 보상 ↺/⚠, **온톨로지 편집 단계는 「온톨로지」 칩**. 범례·취소 정보·「보상 이력 (호출 순서)」 표는 원본과 같다.
- 「취소(보상)」: 조건은 원본과 같음(run succeeded/partial, 성공 대상 있음, 화면 주체가 계획자이거나 승인자). 확인은 **네이티브 창**(문구 원본 그대로 「이 실행을 취소할까요? 성공한 대상의 단계를 역순으로 되돌립니다.」, 안내 「성공한 대상을 역순으로 되돌립니다. 승인은 필요 없습니다.」) — 셸이 `kind:"compensate"` 증표로 보낸다(§7.3).

### 5.4 대화 관리·끼어들기 [원본 유지]
첫 메시지로 제목(앞 30자 + `...`), 화면 메시지 배열 저장·복원(카드는 재조회), 대화 삭제 = 세션·메시지·에이전트 기억 삭제, 홈 최근 항목 「질의·액션 대화」. 끼어들기는 Claude Code만(`delivered`, `steered`).

## 6. API

공통: 모든 요청은 세션 토큰(UI는 셸이 주입한 쿠키) 필요(03 §3). 오류 형식 `{"error":{"code","message"}}` + 응답 헤더 `X-Request-Id` — 원본과 같다. JSON 필드 표기는 camelCase로 쓰되(§12 Q1), SSE data와 비교 대상 응답은 §6.4 대응표로 원본 필드에 맞춘다.

### 6.1 대화 (act 사용분 — 공통 계약은 P 명세)
| 메서드 | 경로 | 요청 | 응답 | 원본 대응 |
|---|---|---|---|---|
| POST | `/api/v1/sessions/{id}/turns` | `{prompt, mode:"act"}` | `{turnId}` / 409 실행 중 | `GET /api/stream?prompt=` 의 시작 부분 |
| GET | `/api/v1/sessions/{id}/turns/{turnId}/events` | (SSE, `Last-Event-ID` 재개) | §6.3 | `/api/stream` |
| POST | `/api/v1/sessions/{id}/steer?mode=act` | `{text}` | `{delivered, reason}` | `/api/agent/steer` |
| GET/POST/PATCH/DELETE | `/api/v1/sessions…` | 원본과 같은 필드 | | `/api/sessions…` |
| GET/PUT | `/api/v1/sessions/{id}/messages?mode=act` | 화면 메시지 배열 | | 같음 |

### 6.2 액션 (Action 모듈)
| 메서드 | 경로 | 요청 | 응답 / 오류 | 원본 대응 |
|---|---|---|---|---|
| GET | `/api/v1/me` | — | `{actor:{kind:"human", id, displayName}, roles[], singleUserMode}` | `/api/act/health`의 identity |
| GET | `/api/v1/actions?objectType=` | — | `[ActionSummary]` 호출 주체에게 보이는 것(§7.1) | `/api/act/actions` |
| POST | `/api/v1/actions/{actionType}/plan` | `{target, params}` (§7.2) | 201 Plan / 404 `not_found` / 403 `forbidden` / 422 `invalid_params`·`invalid_filter`·`too_many_targets`·`not_executable` | `/api/act/plans`, `/plans/by-ids` |
| GET | `/api/v1/action-plans/{planId}` | — | Plan (만료 갱신 포함) / 404 | `/api/act/plans/{id}` |
| GET | `/api/v1/action-plans/{planId}/approval-summary` | — | 창 표시용 요약 + `summaryHash`. **셸 주체만**(다른 주체 403) | 없음 |
| POST | `/api/v1/action-plans/{planId}/approve` | `{note?, proof}` | Plan / 403 `approval_proof_required`·`approval_proof_invalid`·`agent_cannot_approve`·`self_approval`·`forbidden` / 409 `plan_expired`·`conflict` | `/approve` |
| POST | `/api/v1/action-plans/{planId}/reject` | `{note?}` | Plan. 사람만(에이전트 403). 증표 불필요(안전 방향) | 실행기 전용 `/reject` |
| POST | `/api/v1/action-plans/{planId}/execute` | — | 202 Run / 403 `not_plan_owner`·`forbidden`(반려) / 409 `approval_required`·`plan_expired`·`nothing_to_execute`·`plan_stale` | `/execute` |
| POST | `/api/v1/actions/{actionType}/apply` | `{planId}` | 위와 같음 (Object API 별칭, 01 §4) | — |
| GET | `/api/v1/action-runs/{runId}` | — | Run | `/api/act/runs/{id}` |
| GET | `/api/v1/action-runs?limit=10&mine=true` | — | `{items:[Run 요약 + cancellable]}` | `list_runs` |
| POST | `/api/v1/action-runs/{runId}/compensate` | `{reason?, proof?}` | Run / 403 `not_plan_owner` / 409 | `/compensate` |
| POST | `/api/v1/action-runs/{runId}/retry` | — | Run. 계획자만, 실패·자동 보상 대상만 | 실행기 전용 `/retry` |
| GET | `/api/v1/audit?planId=&runId=` | — | 감사 행 목록. 사람만 | 실행기 전용 `/audit` |

- 셸 브리지(렌더러 API, HTTP 아님): `requestApproval({planId, note}) → {approved, plan}`, `requestCompensation({runId, reason}) → {confirmed, run}`. Studio 탭에만 노출(앱 탭·미리보기·외부 브라우저 없음).
- 앱 오리진 SDK 경로(F5): 계획 요청과 승인 **요청**만. 승인·실행 API 자체는 앱 토큰으로 403.

### 6.3 SSE 이벤트 (act) [원본 유지 + 추가]
형식 `event: <이름>\ndata: <JSON>\n\n`. A3 §5.7 공통 이벤트(`status`(시작 문구 「질의·액션 모드 실행 시작...」), `token{text,node}`, `tool_start{tool_call_id,name,node,args,description}`, `tool_result{tool_call_id,name,content(3000자),node}`, `steered{text}`, `ask_user`, `error_event{message}`, `done{message:"완료!",files,text,build_report:null}`)는 **이름·필드 그대로**. act 부수 이벤트:

| 이벤트 | data | 생성 조건 | 원본 대비 |
|---|---|---|---|
| `kinetic_plan` | `{plan_id, status, requires_approval, tool}` | 도구 `plan_<ActionType>`·`get_plan` 결과가 오류 아닌 JSON이고 `id`·`allowed`를 가짐 | 같음(도구 이름 집합만 다름) |
| `kinetic_run` | `{run_id, plan_id, status, tool}` | `execute_plan`·`get_run`·`compensate_run` 결과가 `id`·`targets`를 가짐 | 같음 |
| `traversed_nodes` | `{tool, node_ids[]}` | 조회 도구 결과의 객체 → 그래프 노드 id(`<Ontology>.<Type>:<pk>`) | 같은 이름, id 형식만 객체 참조 |
| `cited_objects` | `{tool, objects:[{object_type, primary_key, title, storage, as_of}]}` | 조회 도구 결과에서 객체 추출(규칙 §7.5) | **신규** |
| `object_set` | `{tool, object_set:{rid?, dsl, summary}, count, truncated}` | `search_*`·`object_set_query`·Function(출력 ObjectSet) 결과 | **신규** |
| `evidence` | `{objects:[…중복 제거], object_sets:[…], unverified:[{object_type, primary_key}]}` | `done` 바로 앞 1회 | **신규** |
| `approval_status` | `{plan_id, status}` | 같은 세션의 계획이 셸 승인 창에서 승인·반려되면 | **신규**(카드 재조회 신호) |

- 도구 결과의 MCP 봉투(`{"result":"<json>"}`)를 벗긴 뒤 판단하는 규칙은 원본과 같다.

### 6.4 원본 필드 대응 (비교 테스트용)
| 원본 | 새 |
|---|---|
| `class`, `action` | `actionType.objectType`, `actionType.apiName` |
| `actor_sub` | `planner.id` (+ `planner.kind`) |
| `where` / `ids` | `target.where` / `target.ids` (`target.objectSet` 신규) |
| `allowed[{key, props}]`, `denied[{key, props, reason}]` | 같은 이름, `key` = 기본 키 문자열(복합 키는 `a|b`), `objectRef` 추가 |
| `preview[]`, `expires_at`, `requires_approval`, `status`, `run_id` | `preview`, `expiresAt`, `requiresApproval`, `status`(값 동일), `runId` |
| `approved_by`, `approved_at`, `approval_note` | `approval.by`, `approval.at`, `approval.note` (+ `approval.proofId`) |
| run `targets[].steps[]`, `compensations[]`, `cancel` | 같은 구조, 단계에 `kind: callSystem|ontologyEdit` 추가 |

## 7. 데이터 (02의 개념으로)

### 7.1 액션 카탈로그
발행 버전의 Action type(02 §10)을 Action 모듈이 적재한다(발행 시 갱신, 원본의 30초 폴링 없음). `ActionSummary`:
```yaml
{ rid, apiName, objectType, displayName, description, aiDescription, version,
  parameters: JSON Schema,          # Action type parameters에서 생성
  targetMode: single|set, maxTargets,
  approval: { required, approverRoles, separationOfDuties },
  rules: [{ kind: modifyObject|createObject|deleteObject|createLink|deleteLink|callSystem, name, system?, operation?, compensable }],
  effect, goldenCommand?: "…" }
```
- 보이는가 = `submissionCriteria`의 `roles` 규칙만으로 판정(원본 정책 노출 규칙과 같음). 에이전트 주체의 역할은 모드 설정(F8)에서 정한다.

### 7.2 계획 (ActionPlan) — `workbench.runtime`
```yaml
ActionPlan:
  id: pln_<16hex>                       # 원본 형식 유지
  actionType: { rid, apiName, objectType, version }
  ontologyVersion: int
  planner: { kind: human|agent|app, id, displayName, sessionId? }
  target: { ids:[…] } | { where:[{prop, op, value}] } | { objectSet: rid | DSL }
  params: {}
  status: planned|awaiting_approval|approved|rejected|executed|expired
  requiresApproval: bool
  allowed: [{ key, objectRef, props }]
  denied:  [{ key, objectRef, props, reason }]
  preview: [{ targetKey, rule, kind, method?, url?, headers?, body?, edits?, compensable }]
  planHash: sha256                      # 아래 정규화 내용의 해시
  createdAt, expiresAt                  # TTL 600초 (설정 가능)
  approval: { by:{kind,id}, at, note, proofId } | null
  rejection: { by, at, note } | null
  runId
```
- 대상 해석: `ids`는 기본 키 일치, `where`는 원본 필터 문법(op `= != > >= < <= in contains starts_with is_null not_null`, 값은 항상 파라미터)을 Object set filter로 변환, `objectSet`은 그대로. 결과 `maxTargets + 1`개까지 읽어 초과면 422 `too_many_targets`(원본 문구).
- 대상마다 `submissionCriteria` 평가 → allowed/denied. 거부 사유 문구는 원본 정책 문구 규칙 유지(`message`가 있으면 그것, 없으면 「조건 불충족: <식>」, 규칙 없음 「정책 규칙이 없습니다 (기본 거부)」 등).
- `requiresApproval` = `planner.kind == agent` **또는** `approval.required`(bool 또는 `when` 식 평가).
- `planHash` 입력: actionType rid·version, ontologyVersion, planner, allowed의 키·props, params, preview(멱등 키 제외), expiresAt. 승인 증표는 이 해시에 묶인다.

### 7.3 승인 증표 (ApprovalProof) [제안, 03 §4 구체화]
```yaml
ApprovalProof:
  proofId: uuid
  kind: approve | approve_execute | compensate
  planId | runId
  planHash                       # compensate면 runId의 계획 해시
  summaryHash                    # 창에 보여 준 요약의 해시(무엇을 보고 눌렀는지)
  approver: { kind: human, id }  # 셸이 아는 로그인 OS 사용자
  issuedAt, expiresAt            # 60초
  signature: Ed25519(shellKey)   # 셸 메모리의 키. 공개 키는 셸이 코어 기동 시 전달
```
- 코어 검증: 서명, 만료, `proofId` 미사용(사용 목록에 기록), `planHash`·`summaryHash` 일치, kind와 엔드포인트 일치. 하나라도 실패 → 403 `approval_proof_invalid`, 감사 `approve_denied`.
- `approve_execute`는 코드 앱처럼 계획자가 실행할 수 없는 경우에만 쓴다(F5): 승인과 실행을 같은 증표로.

### 7.4 실행 (ActionRun)과 사가
```yaml
ActionRun:
  id: run_<16hex>, planId, status: running|succeeded|partial|failed|compensated|partially_compensated
  executor: { kind, id }, startedAt, finishedAt
  targets: [{ key, objectRef, status: pending|running|succeeded|failed|compensated|dead|skipped,
              attempts, finishedSeq, before: {}, compensatedBy: auto|cancel|null,
              steps: [{ name, kind: callSystem|ontologyEdit, system?, operation?, status, httpStatus,
                        httpAttempts, response, error,
                        edits?: [{ objectRef, property|link, before, after }],
                        compensation: null | { status: succeeded|failed|none|conflict, httpStatus, at, error? } }] }]
  compensations: [{ seq, at, targetKey, step, system?, operation?, status, httpStatus, trigger: auto|cancel }]
  cancel: null | { by:{kind,id}, reason, at }
```
실행 규칙(원본 순서 유지 + 확장):
1. 실행 주체 검사: 계획자 본인(사람·에이전트) — 아니면 403 `not_plan_owner` 「plan 작성자만 실행할 수 있습니다.」. 앱 계획은 `approve_execute` 증표로만(F5).
2. plan당 run 하나(이미 있으면 그대로 반환). 만료·반려·미승인·허용 0건 오류는 원본 코드·문구 그대로. **Action type 버전이나 발행 버전이 계획 이후 바뀌었으면 409 `plan_stale`**.
3. 허용 대상을 다시 조회(없어졌으면 skipped 「대상이 더 이상 존재하지 않습니다」), `submissionCriteria` 재평가(실패 skipped 「재평가 거부: <사유>」), `before` = 현재 속성.
4. 대상마다 사가(대상끼리 병렬, 동시 상한 8): 규칙을 **선언 순서대로** 처리한다.
   - `callSystem` → F7 호출 계약(헤더 `Idempotency-Key: <plan>:<대상키>:<단계>:a<시도>`, `X-Kinetic-Run: <run>`, 시스템 인증, 시스템별 재시도). 인자 식 뿌리 `$this/$target, $params, $actor, $run, $plan, $before, $steps, $cancel`와 매핑 키 `path.|query.|header.|body.`는 원본 그대로.
   - 온톨로지 편집 규칙 → 그 시점 값으로 **변경 묶음에 쌓기만** 한다(아직 쓰지 않음). 뒤 규칙은 `$steps.<name>`으로 앞 규칙 결과를 볼 수 있다.
   - 어느 `callSystem`이 실패하면 남은 규칙 skipped, 앞서 성공한 `callSystem`을 **역순 자동 보상**(사유 「자동 보상: '<단계>' 단계 실패」), 쌓인 편집은 버림 → `compensated` 또는 `dead`.
   - 모든 규칙 성공 → 쌓인 편집 + `writeback`을 **한 DB 트랜잭션**으로 확정(편집 레이어 행에 run id 기록, 02 §7.4). 확정 실패 → 성공한 `callSystem` 전부 역순 자동 보상(사유 「자동 보상: 온톨로지 반영 실패」).
   - 시도 수 상한(기본 3) 초과 → `dead`.
5. run 상태 규칙·감사는 원본과 같다. 실행 후 `sideEffects`(알림·웹훅)는 실패해도 run 결과를 바꾸지 않고 기록만(02 §10).

취소(보상): 원본 규칙(성공 대상만 `finishedSeq` 내림차순 하나씩, 대상 안 성공 단계 역순, 멱등 키 끝 `:c`, `$cancel.reason`, 사유 없으면 「사용자 취소」) + 온톨로지 편집 되돌리기:
- modify → 편집 레이어에서 그 run의 행을 지우고 `before`로 복원, create → 만든 객체·링크 삭제, delete → 스냅숏으로 복원.
- **충돌**: 되돌릴 속성의 현재 값이 run의 `after`와 다르면(그 사이 다른 편집) 덮어쓰지 않고 그 단계 보상 `conflict` → 대상 `dead`(「사람 처리 필요」).

### 7.5 근거 객체 추출 (결정적)
- 자동 생성 도구 결과는 객체를 `{"$objectType", "$primaryKey", "$title", "$storage", "$asOf", …속성}` 형태로 돌려준다(04 §5). 결과가 배열이면 항목, 객체면 자신 + `objects/data/items/results` 배열의 항목에서 `$objectType`·`$primaryKey`가 있는 것을 순서 유지·중복 제거로 모은다.
- 답 본문의 `object://<Ontology>.<Type>/<pk>` 링크 중 이번 턴에 모은 집합에 없는 것 → `unverified`.
- 신선도: `live`는 조회 시각, `indexed`는 그 Object type의 마지막 동기화 시각, `native`는 표시 없음.

### 7.6 감사 (`workbench.audit`, 추가만)
`{id, ts, event, actor:{kind,id}, requestId, planId, runId, proofId?, detail}`. event: `plan, approve, approve_denied, reject, expire, execute, retry, compensate, query`(+F7 레지스트리 이벤트). `approve_denied.detail.reason` ∈ `no_proof|invalid_proof|agent_token|self_approval|role`.

## 8. 에이전트 연동 (모드·도구)

모드는 `act`(04 §4). 대화 줄기 `<세션>:act` 하나를 유지(앞 턴 plan id를 이어받기 — 원본과 같음).

| 묶음 | 도구 | 비고 |
|---|---|---|
| 조회 | `describe_ontology()`, `search_<T>(filter, text?, limit)`, `get_<T>(pk)`, `<T>_links(pk, link)`, `search_<I>(…)`, Function 도구 `<f>(inputs)`, `object_set_query(dsl)`, `sandbox_read` | 04 §5 자동 생성. 결과 상한(원본 30행·60000자 등) 유지, 넘으면 `truncated` |
| 조회(고급) | `cypher_readonly(query)` | F8에서 켤 때만 |
| 액션 | `list_actions(objectType?)`, `plan_<ActionType>(target, params)`, `get_plan(plan_id)`, `execute_plan(plan_id)`, `get_run(run_id)`, `list_runs(limit=10)`, `compensate_run(run_id, reason?)`, `query_system(system, operation_id, path_params?, query?)` | 원본 9개 중 `plan_action`·`plan_action_ids`를 Action type별 `plan_<…>`로 대체(대상 인자: `ids`/`where`/`object_set`). 나머지 이름·인자 유지 |
| 없음 | 승인·반려·발행·삭제 확정 도구 | 어느 모드에도 없음(04 §4) |

- `execute_plan`은 코어 규칙(§7.4-1·2)으로 막히므로 지시문만 믿지 않는다: 에이전트 계획은 항상 승인 필요, 승인은 사람 증표로만.
- `compensate_run`: 에이전트는 **자기 계획의 run만** 취소(원본 규칙: 작성자 또는 승인자 → 에이전트는 작성자일 때만).
- `query_system`: GET operation만(F7 §조회, 422 `not_readonly`).
- 에이전트 주체 id = `agent:<backend>:<sessionId>`(다른 대화의 계획은 실행 불가).
- 지시문(스킬)은 원본 구조를 계승한다: 머리말(질문/지시/취소 라우팅) + 1부 답변 + 2부 액션. 바뀌는 규칙:
  - 1부: "조회 없이 답하지 않기"는 같고, **근거 객체를 `object://` 링크로 인용**, 사용한 조건을 Object set 요약으로 밝히기, 신선도(실시간/동기화 시각) 밝히기. "원시 행을 받아 직접 집계하지 않기" → 집계는 Function·`object_set_query` 집계로.
  - 2부: 원본 8단계·취소 5단계와 절대 규칙(대상 지어내기 금지, 승인 우회 금지·계획 쪼개기 금지, 명시적 확인 없이 실행 금지) 유지. 승인 안내 문구 「Studio 의 plan 카드에서 승인이 필요합니다」 유지 + "승인 창은 사람만 누를 수 있다".
- 외부 MCP `ontology_query`(04 §8)도 answer 모드로 같은 근거 형식(`sources` = `evidence.objects`)을 쓴다.

## 9. 보안·권한

### 9.1 주체
| 주체 | 인증 | 할 수 있는 것 |
|---|---|---|
| 사람(Studio 탭) | 세션 쿠키 | 질의, 계획(화면), 반려, 실행(자기 계획), 취소, 감사 조회. 승인은 **셸 창을 통해서만** |
| 셸 메인 프로세스 | 세션 토큰 + 서명 키 | 승인 요약 조회, 증표를 붙인 승인·취소 |
| 에이전트(act) | 턴별 MCP 토큰(MCP 엔드포인트 전용) | §8 도구만 |
| 코드 앱 | 앱별 SDK 토큰 | 선언한 Action type의 계획 요청, 승인 창 요청(F5) |

### 9.2 직무 분리 판정 (승인 시)
| 계획자 | 승인자 | 결과 |
|---|---|---|
| agent | human(다른 주체) | 허용(역할 충족 시) |
| app | human | 허용(`approve_execute`) |
| human A | human B | 허용 |
| human A | human A | 1인 사용 모드 + `separationOfDuties` 미설정/false면 허용(명시적 창 클릭), 아니면 403 `self_approval` 「계획한 주체는 같은 계획을 승인할 수 없습니다.」 |
| 누구든 | agent / app / 증표 없음 | 403 (`agent_cannot_approve` / `forbidden` / `approval_proof_required`) |
- 역할: 승인자는 `approverRoles` 중 하나를 가져야 한다(없으면 403 `forbidden` 「역할 '<role>' 이 필요합니다.」 — 원본 문구 형식). 1인 사용 모드의 기본값은 로컬 사용자가 모든 역할을 가짐(F8).

### 9.3 그 밖
- PII 속성은 도구 결과·근거 패널·계획 표에서 마스킹(02 §6 `pii`, 03). 승인 창에는 키와 제목만.
- 미리보기·감사·로그의 인증 헤더 가림, 업무 시스템에는 시스템 인증만 전송(F7, 03 S8).
- 계획·승인 요청 남용 방지: 같은 주체의 승인 창 요청은 대기 중 1개, 10초 안 반복 무시.

## 10. 오류·예외 (원본 문구 유지 여부)

| 상황 | 코드 | 문구 | 원본 |
|---|---|---|---|
| 액션 미발행 / 보이지 않음 | 404 `not_found` / 403 `forbidden` | 「액션 '<T>.<A>' 이 발행되지 않았습니다.」/「액션 '<T>.<A>' 을 쓸 권한이 없습니다.」 | 유지 |
| 파라미터·필터 | 422 `invalid_params`·`invalid_filter` | 원본 문구(「파라미터 '<n>' 이 필요합니다.」 등) | 유지 |
| 대상 초과 | 422 `too_many_targets` | 「대상이 max_targets(<n>) 를 넘습니다. 조건을 좁히세요.」 | 유지 |
| 비REST 시스템 | 422 `not_executable` | F7 문구 | 유지 |
| 미승인 실행 | 409 `approval_required` | 「허용 대상 N건 — 사람 승인이 필요합니다 (Studio 에서 승인).」 | 유지 |
| 만료 | 409 `plan_expired` | 「plan 이 만료됐습니다. 다시 plan 하세요.」 | 유지 |
| 상태 충돌 | 409 `conflict` | 「상태가 '<s>' 인 plan 은 승인/반려할 수 없습니다.」 | 유지 |
| 허용 0건 | 409 `nothing_to_execute` | 원본 문구 | 유지 |
| 작성자 아님 | 403 `not_plan_owner` | 「plan 작성자만 실행할 수 있습니다.」/「plan 작성자 또는 승인자만 취소할 수 있습니다.」 | 유지 |
| 반려된 계획 실행 | 403 `forbidden` | 「반려된 plan 입니다.」 | 유지 |
| 정의 변경 | 409 `plan_stale` | 「액션 정의가 바뀌었습니다. 다시 plan 하세요.」 | **신규** |
| 증표 없음 | 403 `approval_proof_required` | 「사람 승인 증명이 필요합니다 — 승인은 Studio 승인 창에서만 할 수 있습니다.」 | **신규** |
| 증표 무효 | 403 `approval_proof_invalid` | 「승인 증명이 유효하지 않습니다 (만료·재사용·계획 불일치).」 | **신규** |
| 에이전트·앱 승인 시도 | 403 `agent_cannot_approve` | 「에이전트는 승인할 수 없습니다.」 | **신규**(원본은 역할 403) |
| 자기 승인 | 403 `self_approval` | §9.2 | **신규** |
| 토큰 없음·무효 | 401 `unauthenticated` | 「인증이 필요합니다.」 | 원본은 무인증 |
| 단계 실패 / 보상 실패 / 반영 실패 | run `partial`/`failed`, 대상 `dead` | 원본 라벨 | 유지(+반영 실패) |
| 보상 충돌 | 단계 보상 `conflict`, 대상 `dead` | 「되돌릴 값이 그 사이 바뀌었습니다 — 사람 처리 필요」 | **신규** |
| 에이전트 도구 연결 실패 | 도구 결과 `{"error","hint"}` | 원본 형식 | 유지 |
| Action 모듈 준비 전 | 503 `unavailable` | 「액션 모듈이 아직 준비되지 않았습니다.」 | 원본은 실행기 미기동 문구 |

## 11. 원본과 비교할 테스트

### 11.1 같아야 함
1. 빈 화면 설명 문구·입력 안내문, 파일 첨부 불가(예시 버튼은 골든이 없는 온톨로지에서 원본 4개와 같음).
2. 질문 턴 SSE 이름 순서 패턴: `status`("질의·액션 모드 실행 시작...") → (`tool_start` → [`traversed_nodes`] → `tool_result`)+ → `token`+ → `done`. 질문 턴에 `kinetic_plan`·`kinetic_run` 없음, 감사에 plan 행 없음.
3. 튜토리얼 질문의 결론 값: SHP-03(9일)·SHP-02(7일), Shenzhen Goldline PCB, SHP-06 경계 제외; 이어 묻기 PO-001($82,000)·PO-002($41,000) (00 §7 성공 기준 1).
4. 지시 턴: `list_actions` → 조회 → 계획 도구, `kinetic_plan{status:"awaiting_approval", requires_approval:true}`, 턴 안 `execute_plan` 없음.
5. 계획 값: 허용 SHP-02·SHP-03, 거부 0, 미리보기 4건(callSystem 기준), 만료 = 생성 + 600초.
6. 승인 후 안내 문구, 재승인 409 `conflict`, "실행해" 턴은 `get_plan` → `execute_plan`(같은 plan id), 재계획 없음.
7. run 필드 구조(§6.4 대응), 단계별 Idempotency-Key 형식, 대상 안 호출 순서(wms → erp), 원천 차이(priority NORMAL→URGENT, 독촉 2건).
8. 취소: `compensations` seq = 대상 완료 역순 × 단계 역순(예제 4행), 보상 키 `:c`, `$before` 복원, run `compensated`, 재취소 같은 결과.
9. 오류 코드: 미승인 실행 409 `approval_required`, 만료 409 `plan_expired`, 다른 주체 실행 403 `not_plan_owner`, 허용 0건 409.
10. 감사 순서: plan → approve → execute → compensate.
11. 세션: `mode=act`, 제목 30자 규칙, 메시지 저장·복원 후 카드 재조회, 홈 최근 항목 문구. 끼어들기 `delivered`/`steered`.
12. `kinetic_plan`/`kinetic_run` 생성 조건(같은 입력 결과 JSON → 같은 이벤트).

### 11.2 의도된 차이 (D-12)
| # | 차이 | 확인 방법 |
|---|---|---|
| D1 | 승인은 네이티브 창 + 증표. 증표 없는 승인 → 403 `approval_proof_required` | 세션 토큰만으로 approve 호출 |
| D2 | 에이전트 MCP 토큰으로 REST 승인 → 401, 에이전트 프로세스 환경에 세션 토큰·DB 비밀번호 없음 | 03 §11-3·4 |
| D3 | 감사 승인 행 `actor.kind=human`, `proofId` 존재; 계획자 `agent` | 감사 조회 |
| D4 | 에이전트 계획은 승인 설정과 무관하게 `requires_approval=true` | `approval.required:false` Action type으로 계획 |
| D5 | 자기 승인 정책(§9.2) | 다중 역할 모드에서 N2 |
| D6 | 근거 이벤트 `cited_objects`/`object_set`/`evidence` 추가, 근거 미확인 판정 | N3 |
| D7 | 질문 도구 이름 = 자동 생성 도구(원본 `ontology_*` 아님), `plan_action*` → `plan_<ActionType>` | 도구 이름 집합 |
| D8 | 예시 버튼이 골든에서 생성 | 골든이 있는 온톨로지 |
| D9 | `plan_stale`, 보상 `conflict`, 온톨로지 반영 실패 자동 보상 | N5, N7 |
| D10 | 턴 시작이 POST + SSE 구독 | API |
| D11 | 업무 시스템 호출에 내부 비밀 헤더 없음 | F7 테스트 |

## 12. 열린 질문
- Q1. API JSON 필드 표기(camelCase vs 원본 snake_case) — 01 §4에 공통 규칙이 없다. 이 문서는 REST는 camelCase, SSE data는 원본 snake_case로 썼다. 01에서 정해 주면 맞춘다.
- Q2. 승인 창의 형태: OS 기본 메시지 상자(메모 입력 불가, 표현 제한) vs 셸 전용 신뢰 창(셸이 그리는 별도 창, 웹 콘텐츠 없음). 이 문서는 "메모는 카드에서 입력 → 창에는 표시만"으로 둘 다 가능하게 썼다. [확인 필요: 구현 검토]
- Q3. 승인 후 실행을 대화로만(원본) 둘지, 승인 창에 「승인 후 바로 실행」을 둘지. 이 문서는 원본 흐름 유지(앱 계획만 `approve_execute`).
- Q4. act 모드 파일 첨부(튜토리얼 13장에는 있음, 0.1.1은 꺼짐) — 켤지.
- Q5. 화면에서 에이전트 run을 취소할 수 있는 범위: 원본은 화면 신원이 승인자라 에이전트 run도 취소 가능. 이 문서는 "그 계획의 승인자인 사람"이면 가능으로 둠.
- Q6. 에이전트 주체의 역할(원본 `scm_operator`)을 어디서 정하나 — F8의 모드별 역할 설정으로 가정.
- Q7. 「구축에 제안으로 보내기」(S4)의 F1 쪽 수신 형식.
- Q8. [확인 필요] CLI 경로에서 "실행해" 후속 턴이 앞 plan id를 기억하는 방식(원본 design §13) — 새 구현은 `list_runs`/세션 메모리로 복구 가능해야 함.
