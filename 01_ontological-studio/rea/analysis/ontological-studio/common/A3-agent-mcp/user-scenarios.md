# A3 에이전트·MCP — 운영 시나리오

- 상태: 초안 (2026-10-31, 정적 분석 기반)
- 출처: 튜토리얼 `01-install.md`(「코딩 에이전트 연결하기」), `02-tour.md`, `23-faq.md`, 배포본 0.1.1 코드
- 기준 버전: 0.1.1 (ADR-0012)
- A3는 사용자 메뉴가 아니라 공통 기반이다. 시나리오는 "에이전트가 어떻게 골라지고, 어떻게 실행되고, 어떻게 정리되는가"를 확인하는 운영 시나리오다. 실제 대화 내용(구축·질의 결과)은 M1·M2·M5에서 다룬다.
- 에이전트를 실제로 실행하는 기록은 **분석용 데이터 폴더**에서만 한다 (ADR-0004: `ONTOLOGICAL_STUDIO_USER_DATA=<분석용 폴더>`).

## 공통 사전 상태
- 분석용 데이터 폴더로 첫 실행 직후 (예제 데이터·예제 온톨로지 존재)
- 이 PC에 `claude`(Claude Code)와 `codex`(Codex CLI)가 설치·로그인돼 있는지 여부를 기록해 둔다 (시나리오마다 조건이 다름)

---

## S1. 첫 실행 — Claude Code가 있을 때 에이전트 선택
- **목적:** 기본값(cliagents + Claude Code)으로 에이전트가 골라지는지 확인한다.
- **조건:** `claude`가 PATH(또는 Homebrew·`~/.local/bin` 등 보충 경로)에 있다. studio.env는 예제 그대로.
- **단계:**
  1. 앱을 Finder(아이콘)로 연다 — 터미널이 아닌 곳에서 열어 PATH 보충이 동작하는지도 함께 본다.
  2. 홈 화면 왼쪽 아래 상태와 트레이 메뉴를 본다.
  3. 메뉴 「런타임 › 에이전트」를 연다.
- **기대 결과:**
  - 홈 상태: `에이전트 Claude Code` · 부제 "이 PC 의 CLI 가 Studio 스킬로 구축·질의합니다", 초록 점
  - 트레이: `에이전트: Claude Code` (비활성 항목)
  - 메뉴: 「Claude Code」 라디오 선택됨, 설치 안 된 CLI는 `(설치 안 됨)` 표시·비활성, 「내장 에이전트 (OpenAI 호환 키)」 항상 활성
  - 로그(`logs/desktop.log`): `에이전트: Claude Code (AGENT_BACKEND=cliagents, claude-code)`
- **기록할 것:** 화면 캡처, `desktop.log`의 에이전트 줄, `ps`로 본 프로세스 목록(백엔드·MCP 서버 두 Python 프로세스), 백엔드와 MCP 서버 프로세스의 환경 변수 중 `AGENT_BACKEND`·`EXTERNAL_AGENT_ID`·`ANSWER_MCP_URL`·`MCP_ALLOW_DATASOURCE_EXPANSION`
- **주의:** 이 시나리오는 CLI를 **실행하지 않는다**(감지만). 실행은 S4부터.

## S2. CLI가 없을 때 내장 에이전트로 떨어짐
- **목적:** CLI가 없을 때의 대체 규칙과 안내 문구를 확인한다.
- **조건 A:** `claude`·`codex` 모두 없음, `OPENAI_API_KEY`·`OPENAI_BASE_URL` 모두 비어 있음.
- **조건 B:** CLI 없음, `OPENAI_API_KEY`만 있음.
- **단계:** 각 조건에서 앱을 시작하고 홈 상태와 카드 배지를 본다.
- **기대 결과:**
  - A: 상태 `에이전트 사용할 수 없음`, 부제 "`claude` 를 찾지 못했고 LLM 키도 없습니다. Claude Code 를 설치하거나 studio.env 에 OPENAI_API_KEY 를 넣으세요.", 「설정」 버튼 노출, 「온톨로지 구축」·「질의·액션」 카드에 `에이전트 설정 필요` 배지
  - B: 상태 `에이전트 내장 에이전트`, 부제 "`claude` 를 찾지 못해 내장 에이전트로 실행합니다. Claude Code 를 설치하면 다음 시작부터 씁니다.", 노란 점(안내 문구가 있으므로), 배지 없음
- **기록할 것:** 두 조건의 화면 캡처, 백엔드 기동 성공 여부(키 없이 내장 에이전트가 기동되는지 — 모르는 점), 백엔드 로그
- **주의:** CLI를 PATH에서 숨기려면 앱을 터미널에서 PATH를 줄여 띄워도 보충 경로(`/opt/homebrew/bin` 등)가 다시 붙는다. 설치 위치를 일시적으로 이름 바꾸는 식의 방법이 필요하다(4단계 계획 시 결정).

## S3. 실행 중 에이전트 바꾸기 (메뉴)
- **목적:** 메뉴 전환이 studio.env를 고치고 Studio 프로세스 둘만 재시작하는지 확인한다.
- **단계:**
  1. Studio 탭(예: 질의·액션)을 하나 열어 둔다.
  2. 메뉴 「런타임 › 에이전트 › Codex」(설치돼 있으면) 또는 「내장 에이전트」를 고른다.
  3. 진행 표시와 탭 동작을 본다. 다시 「Claude Code」로 되돌린다.
- **기대 결과:**
  - studio.env의 `AGENT_BACKEND`(와 `EXTERNAL_AGENT_ID`) 줄이 바뀜. 주석 처리된 같은 키 줄이 있으면 그 줄이 대체됨
  - Studio 백엔드·MCP 프로세스만 새 PID로 재시작, PostgreSQL·Bolt·포털·kinetic은 그대로
  - 열린 Studio 탭이 다시 로드되고, 홈은 상태를 다시 읽음
  - 전환 중에는 메뉴 항목이 비활성
- **기록할 것:** 전환 전후 studio.env diff, 프로세스 PID 전후, 소요 시간, 진행 중이던 대화의 이어짐 여부(CLI 세션은 백엔드 메모리에만 있어 끊길 것으로 추정)
- **주의:** 앱 상태가 `ready`가 아니거나 이미 전환 중이면 메뉴 선택이 무시된다.

## S4. CLI 에이전트 한 턴 (구축·질의의 공통 실행 경로)
- **목적:** CLI 에이전트가 어떤 인자·작업 폴더·MCP 연결로 실행되고, 진행이 어떻게 스트리밍되는지 구조를 기록한다(ADR-0010).
- **단계:**
  1. 「질의·액션」에서 짧은 질문을 한 번 보낸다(예: "클래스 목록 알려줘").
  2. 실행 중 `ps -o pid,args`로 CLI 프로세스의 명령줄을 기록한다.
  3. 같은 대화에서 후속 질문을 하나 더 보낸다.
- **기대 결과(정적 분석):**
  - Claude Code: `claude -p --input-format stream-json --output-format stream-json --verbose --mcp-config {...} --strict-mcp-config --permission-mode bypassPermissions --append-system-prompt <스킬 본문+[환경] 블록>` + 첫 턴 `--session-id <새 UUID>`, 후속 턴 `--resume <같은 UUID>`
  - MCP 연결 대상: `http://127.0.0.1:<백엔드 포트>/mcp/agent-bridge/act/` (모드별 경로)
  - 작업 폴더: `<데이터 폴더>/sandbox/sessions/<세션 id>/` 아래 `uploads/`, `output/`, `.claude/skills/<스킬>/SKILL.md`(+references)
  - 화면 스트림: `/api/stream` SSE에 `status` → `token`/`tool_start`/`tool_result` … → `done`
- **기록할 것:** CLI 명령줄 전체(시스템 프롬프트는 길이·첫 줄만), 작업 폴더 트리, SSE 원문, 도구 이름이 `mcp__ontology-studio__` 접두사 없이 표시되는지
- **주의:** bypassPermissions로 실행되므로 반드시 분석용 데이터 폴더에서. 에이전트가 데이터 폴더 밖 파일을 건드릴 수 있다는 전제로 짧은 질의만.

## S5. 실행 중 끼어들기(steering)
- **목적:** Claude Code 턴 실행 중 보낸 메시지가 같은 턴에 전달되는지 확인한다.
- **단계:** 「온톨로지 구축」 같은 긴 턴을 시작한 뒤, 끝나기 전에 입력창에 추가 지시를 보낸다.
- **기대 결과:** `POST /api/agent/steer` 응답 `{"delivered": true}`; 스트림에 `steered` 이벤트; 에이전트가 하던 일을 중단(interrupt)하고 새 지시를 처리. Codex·내장 에이전트에서는 `delivered: false` → 화면이 후속 턴으로 보냄.
- **기록할 것:** steer 요청·응답, SSE의 `steered` 이벤트, 이후 결과 이벤트 순서
- **주의:** 비용·시간이 큰 시나리오. 1회만.

## S6. 대화 초기화와 세션 삭제
- **목적:** 초기화 시 CLI 대화 이어짐이 끊기는지 확인한다.
- **단계:** S4 대화에서 초기화(`POST /api/session/reset`)를 일으킨 뒤 다시 질문한다. 다른 대화는 삭제(`DELETE /api/sessions/{id}`)한다.
- **기대 결과:** 다음 턴은 `--resume` 없이 새 `--session-id`로 시작한다.
- **기록할 것:** 초기화 전후 CLI 명령줄, 작업 폴더가 지워지는지

## S7. 외부 AI 클라이언트가 Studio MCP에 붙기
- **목적:** 앱이 띄우는 읽기 전용 MCP 서버(검색용)의 표면을 확인한다.
- **단계:**
  1. `ports.json`에서 `mcp` 포트를 확인한다.
  2. MCP 클라이언트(예: MCP Inspector)로 `http://127.0.0.1:<mcp 포트>/mcp`에 붙어 도구·리소스·프롬프트 목록을 본다.
  3. studio.env에 `MCP_ALLOW_DATASOURCE_EXPANSION=false`를 넣고 재시작 후 다시 본다.
- **기대 결과:**
  - 기본(앱이 켬): 도구 8개 — `ontology_query`, `ontology_list_entities`, `ontology_list_schemas`, `ontology_get_schema`, `ontology_resolve_entity`, `ontology_graph_cypher`, `ontology_get_datasource_schema`, `ontology_query_datasource_sql`; 리소스 `graph://schema`; 프롬프트 1개
  - false: 앞 4개 도구만
  - 앱의 로컬 웹 오리진(`http://127.0.0.1:<web 포트>/mcp`)으로도 같은 서버에 닿음
- **기록할 것:** tools/list·resources/list·prompts/list 원문, `ontology_graph_cypher`에 쓰기 문장을 넣었을 때 거절 메시지
- **주의:** `ontology_query`는 내부에서 CLI 에이전트를 띄운다(S4와 같은 권한). 기록 시 1회만.

## S8. 앱 종료 시 에이전트 정리
- **목적:** 실행 중이던 CLI 에이전트 프로세스가 남지 않는지 확인한다.
- **단계:** S4처럼 턴을 시작한 직후 앱을 종료(⌘Q)한다.
- **기대 결과:** 백엔드 종료 시 남은 CLI 프로세스 그룹이 SIGTERM → SIGKILL로 정리됨. 코드 앱 턴은 셸이 직접 kill.
- **기록할 것:** 종료 전후 `ps` 결과, 백엔드 로그의 "Closed agent processes still running at shutdown"

## S9. 한 번 묻고 답하는 보조 스크립트 (참고 — 상세는 M4·M5)
- **목적:** 셸이 Studio와 같은 환경으로 단발 스크립트를 실행하는 경로를 확인한다.
- **단계:** 포털의 자연어→Cypher(M4)와 코드 앱 한 턴(M5)을 한 번씩 실행한다.
- **기대 결과:**
  - 자연어→Cypher: 도구 없는 단발 CLI 호출(`claude -p … --output-format text --allowed-tools ""`), 빈 임시 폴더에서, 180초 제한. 내장 에이전트 선택 시 "CLI 에이전트로 동작합니다" 오류
  - 코드 앱: 앱 폴더에서 `--permission-mode acceptEdits`, 파일 도구와 `curl`·`node --check`만 허용, 20분 제한, JSON 줄 스트림
- **기록할 것:** 두 경우의 CLI 명령줄, 스크립트 stdout 형식

---

## 튜토리얼에 없어 확인이 필요한 것
- 내장 에이전트(deepagents)로 키 없이 백엔드가 정상 기동하는가
- Codex 사용 시 사용자 전역 `~/.codex/config.toml`의 다른 MCP 서버가 함께 붙는가
- Claude Code 사용 시 사용자 `~/.claude` 설정(훅·스킬·CLAUDE.md)이 구축·질의 턴에 영향을 주는가
