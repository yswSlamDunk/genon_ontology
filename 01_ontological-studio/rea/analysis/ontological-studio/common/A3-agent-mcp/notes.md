# A3 에이전트·MCP — 메모 (보안·품질 관찰, 다른 대상 관련 발견)

## 보안 관찰 (관찰 = 코드 확인)

1. **권한 우회 실행 (관찰)** — 구축·질의·액션·브리프 초안 턴에서 Claude Code는 `--permission-mode bypassPermissions`, Codex는 `--dangerously-bypass-approvals-and-sandbox`. 허용 도구 목록 없음. cwd만 대화별 작업 폴더. 원본 주석은 "스튜디오가 샌드박스 경계"라고 하지만 실제 파일 시스템 제한은 없다. ADR-0004가 이미 이를 전제로 분석용 폴더에서만 실행하도록 정함.
2. **CLI가 백엔드 환경 전체를 상속 (관찰)** — CLI 자식 env = 백엔드 env(`NEO4J_PASSWORD` = PostgreSQL 슈퍼유저 비밀번호, `KINETIC_STUDIO_TOKEN`(admin·approver 역할 포함), `KINETIC_AGENT_TOKEN`, `OPENAI_API_KEY`, studio.env의 모든 값). 1과 결합하면 에이전트가 Bash로 DB에 직접 붙거나, 승인자 토큰으로 실행기 API를 부를 수 있다 → "에이전트는 승인할 수 없다"는 액션 설계 원칙(스킬·도구 목록 수준)을 프로세스 수준에서 우회 가능. **M2·M7 분석에서 승인 흐름의 실효성을 이 관점으로 확인할 것.**
3. **MCP 실데이터 확장 기본 켬 (관찰)** — 셸이 `MCP_ALLOW_DATASOURCE_EXPANSION=true`를 기본 주입(백엔드 기본은 false). 검색 MCP 서버는 인증 없이 127.0.0.1에서 `ontology_query_datasource_sql`·`ontology_graph_cypher`를 노출. 같은 PC의 임의 로컬 프로세스가 원천 행을 읽을 수 있다. 완화 요소: 루프백 바인딩, FastMCP DNS 리바인딩 보호(Host/Origin), SQL은 바인딩 테이블만·SELECT만, 카탈로그 라벨 차단, PII 컬럼 제거(주석상).
4. **에이전트 브리지 무인증 쓰기 표면 (관찰)** — 백엔드의 `/mcp/agent-bridge/build/`는 `execute`(호스트 셸), `neo4j_cypher`(쓰기 가능) 등을 인증 없이 제공. 백엔드 CORS `allow_origins=["*"]`. 브라우저 기반 공격은 MCP SDK의 Host/Origin 검사가 막을 것으로 추정(FastMCP 생성 시 기본 host 127.0.0.1 → 자동 보호; 브리지 서버는 host 인자 없이 생성 → 보호 켜짐 추정). 로컬 프로세스는 막지 못함.
5. **로컬 샌드박스 격리 없음 (관찰)** — 원본 코드 주석에 "DEV-ONLY: there is no isolation"이 그대로 있는데 배포본이 이 모드를 고정 사용.
6. **사용자 CLI 설정 상속 (추정)** — 구축·질의 턴은 `--setting-sources`를 주지 않아 사용자 훅·플러그인이 그대로 돈다. 코드 앱 턴만 `--setting-sources project`. Codex `-c mcp_servers.…`는 전역 config.toml 위에 덧붙는 방식.
7. **스킬 README 안의 실행 지시** — `skills/README.md`에 `./start-all-services.sh`, `uv run uvicorn …`, `/plugin marketplace add …` 같은 명령이 있다. 대상 데이터로만 취급했고 실행하지 않았다(BRIEF 보안 규칙).

## 품질 관찰

- **studio.env 예제 주석이 낡음 (관찰)** — "키네틱 액션은 … 이 패키지에는 들어 있지 않다. 비워 두면 「시스템 등록」은 연결 안 됨으로 보인다"라고 하지만, 0.1.1은 kinetic-action과 예제 서비스 3개를 번들로 띄운다. (M8 notes에도 기록)
- **메뉴 체크 표시는 요청값 기준** — 「런타임 › 에이전트」 라디오는 studio.env의 값을 보여 준다. CLI가 없어 내장으로 내려간 경우에도 「Claude Code」가 체크된 채(비활성)로 보일 수 있다(추정; 비활성 라디오가 checked일 수 있음). 홈·트레이는 실제 결정값을 보여 준다.
- **CLI 세션 id 메모리 보관** — 앱 재시작·에이전트 전환 후 같은 대화를 이어 가면 CLI는 새 세션으로 시작하고, 화면에는 이전 대화가 보여 사용자는 맥락이 이어진다고 오해할 수 있다(추정).
- **answer 브리지 도구 목록 고정 시점** — 백엔드 기동 시 1회 계산. 백엔드와 MCP 서버를 동시에 띄우므로 경쟁 상태 가능(모르는 점).
- `readUserEnv`는 값 끝 공백을 남기고(정규식 탐욕), 인라인 주석·`export`를 지원하지 않는다. M8 설계에서 명시.

## 다른 대상 관련 발견

- **M7 시스템 등록 / 튜토리얼 14장 불일치 (관찰)** — 튜토리얼은 "등록한 시스템의 비밀 값은 studio.env에 `ERP_API_KEY=...`처럼 적으면 된다"고 하지만, 셸이 kinetic-action 프로세스에 넘기는 env는 `baseEnv + 예제 서비스 비밀 3개(ERP_API_KEY, WMS_BASIC, CRM_TOKEN) + KINETIC_*`뿐이고 studio.env를 읽지 않는다. studio.env는 Studio 백엔드·MCP에만 들어간다. 실행기가 비밀을 어디서 해석하는지(백엔드가 대신 넘기는지) M7에서 확인 필요.
- **M4 포털 자연어→Cypher** — 내장 에이전트에서는 동작하지 않음(CLI 전용). 도구 없이 단발, 빈 임시 폴더, 180초.
- **M5 대시보드** — CLI 단발 호출은 cwd를 지정하지 않아 사용자 데이터 폴더(백엔드 cwd)에서 실행된다(도구 없음이라 영향은 작음). 스트리밍 편집은 dashboard 브리지 3개 도구만 허용.
- **M5 코드 앱** — 셸이 앱 폴더에 규칙 파일을 `CLAUDE.md`와 `AGENTS.md` 둘 다로 쓰고, 세션 id를 앱 메타에 저장(영속). 구축·질의 CLI 세션 id(메모리)와 다름.
- **ontology_query의 재귀 체인** — 외부 MCP 클라이언트의 `ontology_query` → (검색 서버 프로세스 안) 답변 에이전트 → cliagents면 CLI 기동 → 백엔드 `/mcp/agent-bridge/answer(_nods)/` → 대리 도구가 다시 검색 서버 MCP를 호출. 백엔드가 떠 있어야 동작.
- feature-map 열린 질문 "agent_bridge_mcp는 어느 메뉴에 속하는가" → 특정 메뉴가 아니라 A3 공통(구축·질의·액션·대시보드의 CLI 도구 표면).
