# 04. 에이전트(LLM) 통합

## 1. 원본 요약 [원본]
근거: 분석 `common/A3-agent-mcp/design.md`.
- 에이전트 선택: 외부 CLI(Claude Code / Codex, 설치돼 있으면) 또는 내장 에이전트(OpenAI 호환 키). 셸이 결정해 백엔드에 강제.
- 모드 6개: build(구축), brief_draft(브리프 초안), answer(질의), answer_nods(실데이터 제외 질의), act(질의·액션), dashboard(대시보드 편집). 모드마다 지시문(스킬)과 MCP 도구 묶음.
- CLI는 대화별 작업 폴더에서 권한 확인 없이 실행, MCP 설정을 인라인 주입, 스트리밍 입출력(Claude는 실행 중 끼어들기 지원).
- 외부용 검색 MCP 서버(`ontology_query` 등), 인증 없음.
- 일부 기능(품질 추출, 대시보드 등)은 선택한 에이전트와 무관하게 OpenAI 호환 API를 직접 호출.

## 2. 유지할 것 [제안]
- 두 가지 에이전트 백엔드(CLI / 내장)와 자동 선택 규칙, 실행 중 전환.
- 모드별 지시문 + 모드별 도구 묶음(원칙: **모드가 권한의 단위**).
- 대화 thread = `<세션>:<모드>`, SSE 이벤트 계약(원본 A3 §5.7), 실행 중 끼어들기.
- 골든 퀘스천/커맨드를 지시문 재료로 쓰는 구축 방식.

## 3. 바꿀 것 [제안]
| 원본 | 새 설계 | 이유 |
|---|---|---|
| CLI를 권한 우회로 실행 | **허용 도구 목록**(MCP 도구 + 작업 폴더 안 파일 읽기/쓰기)만. 셸 명령 도구는 기본 끔, 모드별로 켤 수 있음(구축 모드에서 파서 실행이 필요할 때) [결정 대기 D-10] | S2 |
| 백엔드 환경 전체 상속 | 화이트리스트 환경 + 턴별 MCP 토큰 | S3 |
| 도구가 Cypher/SQL/스키마 내부 함수 위주(구축 모드 40여 개) | **온톨로지 도구 자동 생성**: 발행된 Object type·Link·Action·Function에서 도구를 만든다 (§5) + 작업본 편집 도구 | 모델과 도구 일치, 도구 수 축소, 권한 표현 쉬움 |
| 에이전트가 발행·적용까지 가능(「발행해 줘」, 대시보드 dry_run=false) | 에이전트는 **작업본 편집과 제안 생성**까지. 발행·적용·승인은 사람 | S4, S11 |
| LLM 호출이 기능마다 따로 | 코어 Agent 모듈의 **단일 LLM 클라이언트**(설정한 공급자). 품질 추출·대시보드 추천도 같은 설정을 씀 | 원본 M6 결함 |
| 외부 MCP 기본 켬·무인증 | 기본 끔, 개인 접근 토큰 | S10 |

## 4. 모드와 권한 [제안]
| 모드 | 용도 | 읽기 | 쓰기 |
|---|---|---|---|
| `build` | 온톨로지 구축(F1) | 카탈로그, 백킹 미리보기, 작업본, 발행본, 문서 | **작업본** 편집, 제안 생성, 문서 추출 실행(품질 게이트로) |
| `brief` | 구축 의도·골든 초안 | 카탈로그, 작업본 | 브리프 초안(제안) |
| `answer` | 질의(F2) | 발행본 Object set·Function, 근거 객체 | 없음 |
| `act` | 질의·액션(F2) | answer와 같음 + 액션 카탈로그 | **액션 계획(dry-run)만**. 실행은 승인된 계획에 한해, 사용자가 실행을 지시한 경우 |
| `dashboard` | 대시보드 편집(F5) | Object set, 위젯 추천 | **패치 제안**(사람이 「적용」) |
| `extract` (신규, 내부) | 문서 추출(F6) | 문서 | 추출 후보(품질 게이트로) |
- 어느 모드에도 **승인·발행·삭제 확정 도구는 없다.**

## 5. 온톨로지에서 도구 자동 생성 (OSDK식) [조사 → 제안]
[조사] Palantir는 Action type에 "Tool description"을 두고 AI 에이전트가 액션을 도구로 호출하며(AIP Agent Studio), 2026년 Ontology MCP를 GA했다. 새 설계:
| 정의 | 생성되는 도구 (발행본 기준) |
|---|---|
| Object type `T` | `search_T(filter, text?, limit)`, `get_T(pk)`, `T_links(pk, link)` |
| Interface `I` | `search_I(...)` |
| Function `f` (query/compute) | `f(inputs)` |
| Action type `a` | `plan_a(target, params)` → 계획 id (act 모드만), `get_plan(id)` |
| 공통 | `object_set_query(dsl)`, `describe_ontology()`(이름·설명·aiDescription 지도), `cypher_readonly(query)`(고급, 설정으로 켬) |
- 도구 설명 = `aiDescription`(없으면 description) + 속성 목록(PII 속성은 이름만, 값 마스킹 규칙 적용).
- 도구 결과 크기 상한(원본: 30행·200행·60000자 등)을 유지하고 넘으면 `truncated`와 저장 위치를 알려 준다.

## 6. 작업본 편집 도구 (build 모드)
`draft_get`, `draft_upsert_object_type`, `draft_upsert_property`, `draft_upsert_link_type`, `draft_upsert_backing`, `draft_upsert_action_type`, `draft_upsert_function`, `draft_validate`, `proposal_create(summary)`, `catalog_list/describe`, `backing_preview(objectType)`, `strategy_recommend`(원본 결정 표 유지), `reverse_bind_preview`(원본 점수 규칙), `document_extract(fileId, targetTypes)`(품질 게이트), `action_dry_run(actionType, where, params)`(원본과 같은 요약 형식).
- 원본의 골든 커맨드 → 액션 생성 규칙(시스템 탐색, 보상 고르기, 정책·임계값 기본값, dry-run 검증 루프)은 지시문으로 계승한다(F1 명세).

## 7. CLI 실행 계약 [제안]
- 작업 폴더: 대화별(원본과 같음). 지시문 파일 위치도 원본과 같음(Claude `.claude/skills/…`, Codex `.agents/skills/…`).
- Claude Code: `--permission-mode` 기본값 `default` + `--allowedTools`(MCP 도구, Read/Write/Edit 작업 폴더 한정, Bash는 D-10), `--strict-mcp-config`, `--setting-sources project`(사용자 전역 훅·설정 차단), 스트리밍 입출력 유지.
- Codex: `exec --sandbox workspace-write`(작업 폴더 밖 쓰기 금지), 승인 정책 `never` + MCP 도구 허용 설정, 프로젝트 설정만.
- MCP 접속: 턴별 토큰을 헤더로 넣은 인라인 설정.
- [확인 필요] 원본 실행 기록에서 CLI가 사용자 전역 설정을 상속하는지 확인 후 차단 방법 확정.

## 8. 외부 MCP
- 기본 끔. 켜면 F8에서 토큰 발급, 범위: `read`(온톨로지 지도·Object set), `data`(live 원천 값 포함), `plan`(액션 계획 요청).
- 도구: §5 자동 생성 도구 중 범위에 맞는 것 + `ontology_query(question)`(answer 모드 에이전트 1회 실행 — 원본과 같은 응답 형식 `{answer, sources, meta}`).
