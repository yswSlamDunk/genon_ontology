# M1 온톨로지 구축 — 설계 문서 (클린룸)

- 상태: 초안 v0.1 (2026-11-01, 정적 분석 기반. 4단계 실행 기록 후 「모르는 점」 갱신)
- 대상: Ontological Studio 0.1.1 「온톨로지 구축」(Studio 뷰 `build`)과 같은 동작을 하는 새 구현
- 이 문서에는 원본 코드·파일 경로·내부 함수 이름을 넣지 않는다. HTTP 경로, 필드 이름, 화면 문구, MCP 도구 이름, 그래프 라벨처럼 밖에서 관찰되는 계약만 적는다(ADR-0002, 0011).
- 함께 받는 문서: A2 저장소(그래프·Bolt), **A3 에이전트·MCP**(CLI 실행, 브리지 MCP, SSE 기본 이벤트, 스킬 파일 배치), M3 데이터소스(패브릭 브리지), **M7 시스템 등록**(시스템 레지스트리·실행기), M6 품질 검수(신뢰도 게이트·검수 큐), M2 질의·액션(계획 카드·승인·실행).

---

## 1. 목적

사용자가 고른 **재료**(업로드 문서, 등록 데이터소스, 등록 업무 시스템)와 **기준**(구축 의도, 골든 퀘스천 = 답해야 할 질문, 골든 커맨드 = 할 수 있어야 할 지시)으로, 에이전트가 온톨로지를 만든다:

- **스키마**: 스키마 그룹(=하나의 온톨로지) 안의 클래스·속성·관계 유형.
- **인스턴스**: 문서·표·시스템 조회 결과를 그래프 노드·관계로 적재(materialized 클래스), 또는 데이터소스 테이블에 바인딩해 조회 시점에 읽기(virtual 클래스 + behavior).
- **액션**: 골든 커맨드마다 등록 시스템 API를 부르는 다단계 액션(단계·보상·정책)을 정의하고 dry-run으로 검증.
- **검증**: 골든 퀘스천을 실제로 실행해 답이 나오는지 보고, 사람이 맞다/틀리다를 판정하면 피드백으로 다시 개선.
- **발행**: 정의를 그래프에 내보내 질의·액션·앱이 쓰게 한다(사람의 결정 — 현재는 대화로 지시).

사람이 판단할 것(근거 약한 추출, 보류)은 검수 탭(M6)으로 넘긴다. 액션 **실행·승인**은 M2.

## 2. 사용자 시나리오 (요약)
상세는 `user-scenarios.md`.
- S1 화면 구성 / S2–S4 브리프 3단계(소스·대상·의도, 에이전트 초안, 권장 전략) / S5 구축 스트리밍·끼어들기·중단 / S6 보고서·골든 퀘스천 판정·피드백 재구축 / S7 그래프·정보 탭 편집 / S8 「발행해 줘」 / S9 골든 커맨드 → 액션 / S10 테이블 구조로 바로 생성 / S11 바인딩·behavior / S12 액션 편집기·dry-run / S13 역바인딩 / S14 인과 가설 / S15 검수 탭 / S16 배포 탭 / S17 대화 관리·초기화.

## 3. 핵심 개념과 저장 위치

| 개념 | 정의 | 원천(진실) | 그래프 표현 |
|---|---|---|---|
| 스키마 그룹 | 온톨로지 하나. 이름 유일, 구축 의도·골든 퀘스천·골든 커맨드를 가짐 | 앱 로컬 DB(세션 DB, SQLite) | 발행 시 `_OntologyModel` |
| 클래스 | 이름(영문 PascalCase 권장, 한글 허용), 설명, 속성 목록, 종류 `materialized`/`virtual` | 로컬 DB | 인스턴스 라벨 `:_Entity:<클래스>`; 발행 시 `_OntologyClass` + 키 제약 |
| 관계 유형 | 이름(UPPER_SNAKE), 출발·도착 클래스, 설명, 속성(예: 조인 키) | 로컬 DB | 인스턴스 관계 타입; 발행 시 `_OntologyRelationship` |
| 바인딩 | virtual 클래스 ↔ 데이터소스 테이블/뷰, 컬럼→속성 매핑, 키 컬럼, 기본 조건 | 로컬 DB | 발행 시 `_OntologyBinding` |
| behavior | virtual 클래스의 파라미터 SQL 조회(골든 퀘스천 대응) | 로컬 DB | 발행 시 `_OntologyBehavior{behavior_type:'sql'}` |
| 액션 | 클래스 인스턴스에 대해 등록 시스템 operation을 순서대로 부르는 정의 | 로컬 DB | 발행 시 `_OntologyBehavior{behavior_type:'action'}` |
| 인스턴스 | 노드 `:_Entity:<클래스>{_source_id, name, content?, …, created_at, updated_at, embedding?}` | **그래프** `ontology` | 그대로 |
| 출처 기록 | 요소(클래스/속성/관계)를 어떤 전략이 어떤 근거로 만들었는지 | 로컬 DB | 없음 |
| 인과 가설 | 통계로 발견한 영향 후보와 사람 판정 | 로컬 DB | 승격 시 관계 |

원칙: **정의는 로컬 DB가 원천이고 그래프는 발행물만 읽는다.** 인스턴스만 그래프가 원천이다. 클래스 이름은 그래프 라벨이라 **스키마 그룹을 넘어 전역**이다(같은 이름이면 인스턴스가 섞임 — 튜토리얼 FAQ와 같은 동작).

## 4. 화면 구성과 상호작용

### 4.1 레이아웃
Studio 탭의 대화형 화면(구축·질의·액션 공통):
- 왼쪽 레일: 온톨로지 구축 / 질의·액션 / 대시보드 / 품질 검수 / 데이터소스 / 시스템 등록 / Ontological Portal. 스트리밍 중에는 대화형 뷰 전환 버튼 비활성.
- 사이드바(접기 가능, 접힘 상태는 브라우저 저장소): 제목 「온톨로지 구축」, 「+」(새 대화), 설명 「문서를 분석하고 스키마, 엔티티, 관계를 생성하는 작업 모드입니다.」, 구축 대화 목록(질의·액션·질문응답이 아닌 세션, 최근순; 행 = 스키마 이름 배지·제목(기본 「새 대화」)·시각(오늘이면 시:분, 아니면 월 일)·× 삭제). 그 아래 파일 패널(업로드/출력 목록, 눌러 보기·내려받기·삭제), 맨 아래 「초기화」.
- 가운데: 대화가 비어 있으면 **브리프 패널**, 아니면 **대화창**.
- 오른쪽 패널(폭 조절·더블클릭 초기화): 제목 「온톨로지 그래프」, 탭 「그래프」「정보」「배포」「검수」(툴팁 「빌드가 남긴 것 중 사람이 판단할 것」, 배지 = 확인 필요 + 보류 건수).
- URL 쿼리 `view=build`(뷰), `session=<id>`(해당 대화 열기, 목록 로드 뒤 적용).

### 4.2 브리프 패널 (3단계 탭)
단계 버튼: `1 소스`, `2 대상`, `3 의도`. 각 버튼 아래 요약, 다른 단계에 있고 완료면 ✓. 스트리밍 중 비활성. 하단 「← 이전」「다음 →」, 3단계에서 「이 브리프로 구축 시작」. 입력이 모두 비면 1단계로 돌아간다.

**1 소스** — 질문 「무엇을 근거로 온톨로지를 만들까요?」, 보조 문구 「문서와 데이터소스를 함께 쓸 수도 있습니다. 문서는 내용을 파싱해 인스턴스로 적재하고, 데이터소스는 복제하지 않고 조회 시점에 데이터를 가져옵니다.」
- 문서: 업로드 영역(클릭·드래그 앤 드롭, 여러 파일). 비었으면 「+ 파일 업로드 (드래그 앤 드롭 가능)」, 있으면 칩(이름·크기) + 「+ 추가」. 올리면 바로 업로드(§5.2)하고 초안 요청 예약.
- 데이터소스(패브릭이 살아 있고 1개 이상일 때): 칩(표시 이름·엔진). 고르면 스키마 칩 줄(로드 중 「스키마를 불러오는 중...」, 테이블 수 표시)이 펼쳐지고 스키마를 여러 개 고를 수 있다. 패브릭 불통이면 「데이터 패브릭에 연결되지 않아 데이터소스를 선택할 수 없습니다. 문서만으로 진행합니다.」
- 시스템 (서비스): 등록 시스템 칩(이름, `API <operation 수>`, 툴팁 설명 또는 base_url), 보조 문구 「골든 커맨드를 실행할 액션이 이 시스템들의 API 를 부릅니다. 인스턴스는 문서·데이터소스에서 옵니다.」 목록이 비면 영역 숨김.
- **테이블 구조로 바로 생성**(데이터소스 스키마를 1개 이상 고르면): 제목 + 배지 「LLM 불필요」, 설명(테이블→클래스, 컬럼→속성, 외래키→관계, 같은 카탈로그는 같은 결과, 가상 클래스로 즉시 조회), 대상 선택(`<ds>::<schema>`), 「미리보기」(dry-run, 문구 「이 계획으로 생성하면 아래 클래스와 관계가 만들어집니다.」 + 클래스/테이블/속성/키 표, 관계/출발/도착 표, 머리 `클래스 N · 관계 M · 속성 K`), 「이대로 생성」(대상 스키마 이름 = 새 스키마 이름 또는 대상 스키마) → 「생성 완료 — 클래스 N개, 관계 M개. 가상 클래스로 바인딩되어 바로 조회할 수 있습니다.」 오류는 빨간 문구.
- 요약: `문서 N개 · <ds 이름들> · 시스템 N개`. 아무것도 없으면 경고 「문서·데이터소스·시스템 중 1개 이상 선택하세요.」

**2 대상** — 질문 「어느 스키마에 담을까요?」, 보조 「기존 스키마를 고르면 그 스키마의 클래스만 사용해 추가 인제스천합니다. 이름을 비워 두면 구축 의도에 맞춰 새로 만듭니다.」 선택 상자: 「새 스키마 생성」 + 기존 스키마들(`<이름> (추가 인제스천)`). 새 스키마면 이름 입력(placeholder 「새 스키마 이름 (선택, 예: 제조 운영 스키마)」). 기존 스키마를 고르면 그 스키마의 의도·골든 퀘스천·골든 커맨드로 브리프를 채운다(값이 있는 것만). 요약: `<이름> (추가)` / `새 스키마 「<이름>」` / `새 스키마 생성`.

**3 의도** — 질문 「무엇에 답할 수 있어야 하나요?」
- 요약 상자: 소스·대상 한 줄씩.
- 초안 상태 줄: 생성 중 「에이전트가 소스를 살펴보고 초안을 만드는 중입니다. 그동안 직접 입력해도 됩니다.」 / 실패 「초안을 만들지 못했습니다 — 직접 입력해서 그대로 진행할 수 있습니다.」 + 오류 / 완료 「아래는 에이전트 초안입니다. 그대로 쓰지 말고 고쳐 주세요.」 + 메모. 「초안 다시 생성」(생성 중엔 「생성 중…」).
- 구축 의도(여러 줄, placeholder 「예: 내부 감사 담당자가 문서의 핵심 개체와 관계를 빠르게 추적할 수 있도록 온톨로지를 만들고 싶습니다.」), 초안이면 배지 「에이전트 초안」.
- 권장 전략 상자(추천이 있으면): 전략 이름·이유, 쓸 수 없는 전략과 사유, 「권장은 강제가 아닙니다. 이대로 시작해도 다른 전략으로 바꿀 수 있습니다.」 전략 이름: `doc_reverse_bind`=「문서 엔티티 → 데이터소스 역바인딩」, `causal_discovery`=「데이터에서 인과 발견」, `catalog_schema`=「테이블 구조 그대로 매핑」, `document_only`=「문서 기반 (인스턴스 적재)」, `none`=「입력 부족」. (전략 선택은 표시뿐이며 에이전트에 전달되지 않는다.)
- Golden Question 목록: 줄마다 입력(placeholder `예: Golden Question <n>`)·「삭제」, 초안이면 아래에 「근거: <evidence>」. 머리 「파일에서 불러오기」(텍스트 파일, 빈 줄 제외 한 줄 = 한 질문; 목록이 빈 한 줄뿐이면 대체, 아니면 뒤에 추가), 「질문 추가」. 마지막 한 줄을 지우면 빈 줄로 남긴다.
- Golden Command 목록: 같은 형태(placeholder `예: Golden Command <n>`), 「커맨드 추가」, 보조 「예: “3일 넘게 늦어진 입고 선적을 긴급 처리해 줘 (사유 포함)”, “방금 한 처리를 취소해 줘”. 에이전트가 등록 시스템의 API 를 탐색해 단계·보상을 갖춘 액션을 만들고 dry-run 으로 검증합니다.」
- 요약: `질문 N개[ · 커맨드 M개]` 또는 `질문 없음`.
- 시작 조건: 의도(공백 제외) 있음 + 질문 ≥1 + (문서 또는 데이터소스 또는 시스템) ≥1. 아니면 「구축 의도와 Golden Question을 최소 1개 입력하면 구축을 시작할 수 있습니다.」

**초안 자동 요청 규칙**
- build 화면에서 소스(문서·데이터소스·스키마 선택)가 바뀌면 900ms 디바운스 후 요청. 「초안 다시 생성」은 강제.
- 근거(문서·데이터소스)가 없으면 요청하지 않음(강제면 「초안을 만들 근거가 없습니다 — 문서를 올리거나 데이터소스를 선택하세요.」).
- 강제가 아니고 의도·질문이 둘 다 사용자 입력이면 요청 생략. 진행 중 요청은 새 요청이 오면 취소.
- 에이전트 턴 진행 중 강제 요청: 「에이전트가 응답하는 중입니다. 끝난 뒤 다시 눌러 주세요.」
- 응답 적용: 의도 칸이 비었거나 직전 초안 그대로면 채우고 draft 표시; 질문 목록이 비었거나 직전 초안 그대로면 대체하고 draft 표시·근거 저장. 사용자가 쓴 칸은 두고 메모 「직접 입력한 항목은 그대로 두었습니다 — 구축 의도 · Golden Question.」 의도·질문 둘 다 비면 오류(응답 note 또는 「초안이 비어 있습니다 — 에이전트가 소스에서 근거를 찾지 못했습니다.」). HTTP 404 → 「초안 생성 경로를 찾지 못했습니다 (404). 백엔드가 아직 준비 중일 수 있습니다 — 잠시 뒤 다시 시도하세요.」, 그 밖 → `초안 생성 실패 (HTTP <코드>). <본문 200자>`.
- 사용자가 초안 칸을 고치면 그 칸의 draft 표시를 지운다.

### 4.3 구축 시작과 대화창
- 「이 브리프로 구축 시작」(또는 3단계에서 입력란 전송) → 대화가 없으면 먼저 세션 생성(제목 「새 대화」, mode build, schema_name = 대상 또는 새 이름) → 대상/새 이름이 **기존 스키마**면 브리프 저장(PUT brief) → 사용자 말풍선(입력이 비었으면 「구축 의도와 Golden Question을 기준으로 온톨로지 구축 시작」, 말풍선에 브리프 사본 보관) → 스트림 열기(`mode=build`, `build_context` 포함, §5.1). 프롬프트가 비면 기본 문장 「업로드된 문서를 바탕으로 Golden Question에 답할 수 있는 온톨로지를 구축해줘.」
- 후속 메시지(대화가 있을 때)는 `build_context` 없이 보낸다(서버가 저장본 복원).
- 입력란: Enter 전송, 파일 첨부 버튼·붙여넣기·드롭(업로드 후 대화가 있으면 말풍선 「파일 업로드: a, b」). placeholder: 브리프 미완이면 「파일 또는 데이터소스를 1개 이상 선택하고, 의도 1개, Golden Question 최소 1개를 입력하세요...」, 아니면 「추가 지시사항이 있으면 입력하세요. 비워두면 설정한 의도와 Golden Question 기준으로 바로 구축합니다.」; 스트리밍 중 「작업 중에도 지시를 보낼 수 있습니다 — 방향을 바꾸거나 범위를 좁혀보세요」.
- 스트리밍 중: 전송 버튼 대신 ➤(「작업 중인 에이전트에게 전달」, steer API, 전달되면 사용자 말풍선을 진행 중 답 앞에 끼우고 「작업 중 지시」 표시) + 「중단」(스트림 닫기, 답 끝에 「\n[중단됨] "계속해"를 입력하면 이어서 진행합니다.」, 메시지 저장).
- 어시스턴트 말풍선: 상태 문구, 토큰 텍스트(마크다운), 도구 칩 목록(이름, 분류 배지 `ONTOLOGICAL`/`DATA`/`TOOL`, 데이터소스 칩이면 `<ds>.<table> · N건`, 실행 중 「실행 중...」 → ✓, 설명 한 줄, 「입력 보기」(execute면 명령 원문), 「결과 보기」; 접힘 요약 `<n>개 도구 사용됨` / `<마지막 도구> 실행 중...`), 출력 파일 버튼, 계획·실행 카드(kinetic 이벤트 — M2 컴포넌트), 질문 카드(ask_user: 질문·선택지 버튼 → 선택하면 「<질문>: <선택>」을 steer로), 보고서(§4.4).
- 분류 배지 규칙: 데이터소스 계열 도구(`datasource_*`, `class_*binding*`, `behavior_*`, `entity_fetch`, `ontology_get_datasource_schema`, `ontology_query_datasource_sql`, …) → DATA, 스키마·그래프 계열(`neo4j_cypher*`, `schema_create_*`, `schema_get`, `entity_*`, `relationship_create`, `ontology_graph_*`, `ontology_list_*`, `ontology_resolve_entity`, `ontology_get_schema`) → ONTOLOGICAL, 그 밖 TOOL.
- 이벤트 반응: `neo4j_update` → 스키마·그래프 다시 읽기, `schema_created` → 그래프 필터를 그 스키마로, 세션 schema_name 갱신, `todos` → 진행 상황 패널, `skill_loaded`/`ref_file` → 컨텍스트 패널(스킬·참조 파일), `done` → 텍스트 확정·보고서·파일·메시지 저장·첫 메시지면 세션 제목(앞 30자+`...`)·전체 갱신, `error_event` → 「\n오류: <message>」.
- 메시지는 턴 종료·중단·대화 전환 시 서버에 통째로 저장(화면 상태 그대로, mode별).

### 4.4 구축 보고서
- **Golden Question 검수** 카드: 제목, 「이 구축 결과가 각 Golden Question에 답할 수 있는지 확인해 주세요.」, `<n>개 질문`; 질문마다 상태 배지(answerable=「답변 가능」, partially_answerable=「부분적으로 답변 가능」, not_yet_answerable=「아직 답변 어려움」), 신뢰도(high/medium/low = 「신뢰도 높음/보통/낮음」), 답(없으면 「에이전트가 답변 초안을 제공하지 못했습니다.」), 「맞다」「틀리다」 토글(다시 누르면 해제, 틀리다가 아니면 피드백 지움), 틀리다면 피드백 입력(placeholder 「무엇이 부족하거나 잘못되었는지 적어 주세요. 이 내용이 다음 개선 루프에 전달됩니다.」), 「피드백 반영 요청」(활성 조건: 판정된 질문 중 틀리다 ≥1이고 틀리다 전부 피드백 있음, 스트리밍 아님).
- 피드백 반영: 사용자 말풍선 「Golden Question 검토 피드백 반영 요청」, 프롬프트 「방금 검토 피드백을 반영해서 Golden Question에 더 잘 답할 수 있도록 온톨로지를 개선해줘.」, build_context에 `review_feedback=[{question, answer, status, verdict(correct|incorrect), feedback}]`(판정된 질문만).
- **Golden Command** 표(커맨드가 있을 때): 열 커맨드(아래 note) / 액션(`Class.action` 코드, 없으면 —) / 단계(`a → b`) / 검증(「✓ dry-run」 또는 「미검증」).
- 검수 현황 줄(확인 필요나 보류가 있을 때): 「🙋 확인이 필요한 내용 **N**건 · 🗂️ 보류 **M**건 — 사람이 판단해야 지식 지도에 들어갑니다.」 + 「검수 탭에서 보기」(검수 탭 열고 그 스키마 선택).

### 4.5 오른쪽 「그래프」 탭
- 보기 전환 「스키마」(클래스=노드, 관계 유형=엣지, 가상 클래스는 다른 모양·툴팁 「가상 클래스 (데이터소스)」「조회 시점에 데이터를 인출하며 노드를 저장하지 않습니다」, 속성 노드 `[속성] 이름`) / 「엔티티」(인스턴스 그래프, 최대 200).
- 배치: Force (CoSE)·Circle·Concentric·Tree·Grid. 스키마 필터(「전체 스키마」+ 그룹들), 클래스 필터(「전체 클래스」), 검색(「이름/속성으로 검색...」 → 하이라이트 `N개 노드 하이라이트` / 「결과 없음」), 자연어 질문(「자연어로 질문 (예: 리스크 관련 프로세스는?)」 → 그래프 NL 질의 API), 노드 확장(이웃, `N개 노드 추가됨`), 엔티티 생성·속성 수정·삭제(선택 다중 삭제 「선택된 N개 노드를 삭제하시겠습니까?」), 클래스 삭제 확인, 「새로고침」, 스키마 삭제 메뉴(「엔티티만 삭제 — 스키마 정의는 보존」 / 「스키마 전체 삭제 — 정의 + 엔티티 모두」 / 「취소」).
- 질의 대화에서 지나간 노드(traversed_nodes)를 강조.

### 4.6 오른쪽 「정보」 탭
위에서부터:
1. 진행 상황(todos, 있을 때).
2. **온톨로지 스키마** 패널(접기 가능): 스키마 선택(+「(미분류)」), 스키마 동작(「엔티티 삭제」 확인 「이 스키마의 모든 엔티티를 삭제하시겠습니까? (스키마 정의는 보존됩니다)」, 「스키마 복원 (Neo4j)」, 대시보드 자동 구성 「이 온톨로지로 대시보드를 자동 구성합니다」 → 대시보드 뷰로 이동). 비었으면 「스키마가 아직 없습니다. 대화로 설계를 시작하세요.」 클래스 행: C 아이콘·이름·「가상」 배지(툴팁 「데이터소스: <ds> / <schema.table>」, 바인딩 없으면 「데이터소스에 연결된 가상 클래스입니다.」) 또는 인스턴스 수, 버튼 ⛁「데이터 연결」·✎「편집」·삭제; 펼치면 속성(이름·타입·`← 원천 컬럼`·PII·`*`), 가상이면 「바인딩에서 편집」. 편집 폼: 클래스 이름·설명 (선택)·속성(이름·타입 string/integer/float/boolean/date/list, 「+ 속성」)·「저장」「취소」. 「+ 클래스 추가」(새 클래스 이름), 관계 행(이름, 출발→도착)·편집·삭제, 「+ 관계 추가」(관계명, 출발·도착 선택). 하단 「엔티티 수」 목록(라벨별 인스턴스 수, `_Entity` 제외).
3. **클래스 데이터 연결** 패널(⛁로 연 클래스): 머리 클래스 이름 + `ds / schema.table` 또는 「데이터소스에 연결되지 않은 클래스입니다.」, 「닫기」. 탭 「바인딩」 / 「동작(Behavior)」(바인딩 있을 때만) / 「액션」(항상).
   - 바인딩: 데이터소스·스키마·테이블 선택, 샘플 행, 「컬럼 → 속성 매핑」(포함·컬럼·속성명·타입·키·PII; 안내 「매핑하지 않은 컬럼은 조회할 수 없습니다. 개인정보 컬럼은 PII로 표시하면 결과에서 제외됩니다.」), 「기본 조회조건」(조건 추가·값·삭제; 「모든 동작에 항상 적용됩니다. 너무 좁으면 조회 결과가 0건이 됩니다.」), 「라벨 속성」, 「스키마 변경 감지」(사라진 컬럼/새 컬럼/타입 변경), 「저장」(→「저장했습니다.」 또는 「저장했습니다. (데이터 패브릭에 연결할 수 없어 컬럼 검증은 건너뛰었습니다)」), 「연결 해제」(→「연결을 해제했습니다.」, 클래스는 materialized로 돌아가고 behavior 삭제), 「스키마 검증」.
   - 동작: behavior 칩 + 「+ 새 동작」, 이름(예 「고객별 주문 조회」), 설명, 대응 Golden Question, 파라미터(이름·타입·필수·기본값, 「파라미터 추가」), SQL 템플릿(안내: `{{파라미터}}` 형태, LIMIT 금지, 기본 조건 있으면 WHERE에 `{{__base_filter__}}` 필수), 테스트 인자, 「테스트 실행」(→ `N건을 조회했습니다.` + 실행 SQL), 「저장」(→「저장했습니다. (실제 실행으로 검증됨)」 또는 「…(기본값이 없어 실행 검증은 건너뛰었습니다)」), 「삭제」.
   - 액션: §4.7.
4. **문서 엔티티 → 데이터소스 역바인딩** 패널(스키마 선택 + 브리프에 데이터소스 스키마 선택이 있을 때): 대상 선택, 「미리보기」(「미리보기입니다. 아직 저장되지 않았습니다.」), 표(엔티티·판정 자동/검토필요/충돌/매칭없음·테이블·점수·근거 「일치 … / 미일치: …」, 검토필요·충돌은 후보 선택 「선택하세요」), 「데이터소스가 없는 엔티티 N개는 미바인딩으로 온톨로지에 남습니다 — …」, 「문서가 덮지 못한 테이블 N개: …」, 충돌 안내, 「확정 바인딩」 → 「바인딩 N개 완료.」「확인이 필요해 건너뛴 항목 K개.」「미바인딩 U개는 그대로 남습니다.」 / 「바인딩에 실패했습니다.」
5. **인과 가설 검토** 패널(같은 조건): 「발견 실행」, 안내(통계 한계·승인한 것만 관계·거부한 가설은 재실행해도 되살아나지 않음), 분석 요약(분석 행·검정 횟수·보정·표본 잘림 경고·기존 판정 보존 수), 표(원인·결과·방법·시차·강도·p(보정)·판정 승인/거부/방향반전, 유의하지 않음 표시), 「관계로 승격 (n)」 → 「관계 N개 승격.」「미검토 K건은 그대로입니다.」
6. 컨텍스트(스킬·참조 파일).

### 4.7 액션 편집기 (정보 탭 → 클래스 ⛁ → 「액션」)
- 실행기 상태 경고: 불통 「kinetic-action 에 닿지 못했습니다 (<url>). 정의는 저장되지만 시스템·operation 목록과 dry-run 은 쓸 수 없습니다. <error>」, 신원 토큰 없음 「KINETIC_STUDIO_TOKEN 이 설정되지 않았습니다 — 실행기 호출이 인증에서 거부됩니다.」
- 기존 액션 칩(`이름 v<version>`) + 「+ 새 액션」. 칩을 누르면 폼에 로드(이름 잠금).
- 폼: 이름(placeholder `setMaintenanceMode`), 「설명 (에이전트에게 보입니다)」, 「단계 (n) — 위에서 아래로 실행」 + 「단계 추가」(새 단계 이름 `main` 또는 `step<n>`), 인자 규칙 안내. 단계마다: slug(「영문 소문자로 시작, 소문자·숫자·밑줄」), 제목, 위로/아래로/삭제, 시스템 선택(「(레지스트리에 없음)」 표시 포함), Operation 선택(`n개`, 「(목록에 없음)」), 「인자 매핑」(키·값·JSON 토글·필수 표시, 「인자 추가」), 「보상(compensation) — 뒤 단계 실패·취소 시 이 단계를 되돌리는 호출」 토글(보상 시스템·보상 Operation·보상 인자 매핑, 안내 `$before.속성`·`$steps.이단계.response.…`·`$cancel.reason`), 보상 끄면 「보상이 없으면 이 단계는 되돌리지 않습니다 (계획 카드에 표시).」
- 「파라미터 (JSON Schema)」 텍스트, 「정책 (규칙은 OR · 규칙이 없으면 아무도 실행 못함)」(역할 쉼표 목록·CEL 조건·설명, 「규칙 추가」, 비면 「규칙이 없습니다 — 기본 거부입니다.」), 효과(write/read), 승인 임계치(「허용 대상 수가 승인 임계치를 넘으면 사람 승인이 필요합니다. 0 = 항상 승인.」), 대상 상한, 「키 속성 (비우면 클래스 키)」, 「성공 시 기록할 속성」(「(없음)」+ 클래스 속성).
- **Operation 선택 시 인자 자동 채움**: operation의 path/query/header 파라미터 → `path.<n>`/`query.<n>`/`header.<n>`; 요청 본문 스키마의 속성 → `body.<p>`(배열 속성이고 항목에 속성이 있으면 `body.<p>.0.<q>`). 이미 있는 키는 필수 표시만 갱신. 기본값 제안: 전진 단계 — `path.*`→`$this.$key`, 이름 `reason`→`$params.reason`, `requestedBy`→`$actor.sub`, `equipmentCode|equipmentId`→`$this.$key`; 보상 — 같은 시스템의 다른 operation이고 path 이름이 `id`/`…Id`면 `$steps.<이 단계>.response.<이름>`, 그 밖 `path.*`→`$this.$key`, `reason`→`$cancel.reason`, `requestedBy`→`$actor.sub`, `status`→`$before.status`. 보상을 켤 때 보상 시스템 기본 = 단계 시스템.
- 저장 버튼 활성: 이름 있음, 단계 ≥1, 모든 단계 slug 규칙·시스템·operation 있음, 켠 보상은 operation 있음, slug 중복 없음.
- 저장 → PUT(§5.4) → 「저장했습니다 (v<n>). 발행하면 실행기에 반영됩니다.」 + 경고 목록. 안내 「저장한 정의는 스키마를 **발행**해야 실행기에 반영됩니다.」 삭제 확인 「액션 '<이름>' 를 지울까요? 다음 발행에서 그래프에서도 사라집니다.」 → 「삭제했습니다.」 JSON 오류: 「단계 '<s>' 인자 '<k>' 의 JSON 값이 올바르지 않습니다.」, 「파라미터 JSON 오류: <msg>」.
- **Dry-run (발행된 정의 기준)**: 조건 줄(속성 「속성 (예: plant)」·연산자 `= != > >= < <= in contains starts_with is_null not_null`·값; `in`은 쉼표 목록; 숫자처럼 보이면 숫자, `true/false`는 불리언; is_null/not_null은 값 없음), 「파라미터 (JSON)」, 「계획 만들기 (dry-run)」 → 실행기에 계획 생성(화면 신원) → 계획 카드(M2 컴포넌트). not_found면 「실행기가 이 액션을 모릅니다 — 스키마를 발행했는지 확인하세요. (<msg>)」.

### 4.8 「배포」 탭
개발·운영 두 쪽 카드(스키마 버전·타입 수·변경 이력·운영 릴리스 이력·오류), 패키지 목록(이름·hash·생성 시각·스키마 버전·인스턴스·조각·관계·타입 수), 「패키지 만들기」(이름 선택, 기본 `R<n>`), 「계획 보기」(스키마 변경·새/바뀌는/같은 인스턴스·쓸 조각·이미 적용됨), 「운영에 적용」(결과 「적용 완료 — 릴리스 #…」, 단계·결과 로그), 「새로고침」. 세부 문구는 원본 동작 기록으로 보완(모르는 점).

### 4.9 「검수」 탭
M6 검수 화면의 축약판: 온톨로지 선택(기본: 지정 스키마 → 그래프 필터 스키마 → 대상 스키마 → 가장 최근 스키마), 머리 「지도에 N개 · 확인 필요 A · 보류 B」, 탭 「🙋 확인하기」/「🗂️ 보류함」(확인 필요 0이고 보류 있으면 보류함으로), 비었으면 「구축을 시작하면 이곳에 사람이 판단할 내용이 모입니다.」 구축 턴이 끝날 때마다 다시 읽는다. 카드 동작은 M6 설계를 따른다.

### 4.10 초기화
「초기화」 → 체크 「샌드박스 파일시스템」, 「Ontological 데이터」 → 「선택 항목 초기화」(둘 다 꺼지면 비활성) → 확인 「다음 항목이 초기화됩니다:\n- …\n\n정말 초기화하시겠습니까?」 → 샌드박스 비우기 / 그래프 전체 삭제 → 현재 세션 대화 기억 초기화(reset) → 파일·메시지 비움, 스키마 재조회. **원본은 그래프 `ontology` 전체(발행물·예제 포함)를 지운다** — 새 구현에서 범위를 좁힐지 결정(§13).

### 4.11 대화 관리
- 「+」: 세션 생성(제목 「새 대화」, 현재 모드) → 메시지·브리프·파일 비움.
- 대화 선택: 현재 대화 메시지 저장 → 새 대화의 build/answer/act 메시지 로드(build 말풍선에 브리프 사본이 있으면 브리프 복원) → 세션 모드로 화면 전환, 그래프 필터 = 세션 스키마.
- 삭제 ×: 세션과 대화 기억·작업 파일 삭제(A3), 현재 대화면 `default`로.

## 5. API 명세 (백엔드, 로컬 오리진 `/api`, 인증 없음)
모든 응답 JSON. 오류는 대개 200 + `{error}`(아래 예외 표기).

### 5.1 대화·세션
| 메서드 경로 | 요청 | 응답 |
|---|---|---|
| GET `/api/stream` | `prompt`, `session_id`, `mode=build`, `build_context`(JSON 문자열) | SSE (A3 §5.7 + §6.2 이 문서) |
| POST `/api/agent/steer`, GET `/api/agent/running`, POST `/api/session/reset` | A3 | A3 |
| GET `/api/sessions` | | `{sessions:[{id, title, mode, schema_name, created_at, updated_at}]}` 최근순 |
| POST `/api/sessions?title&mode&schema_name` | | 세션 객체(id 12자 hex) |
| PATCH `/api/sessions/{id}?title&schema_name` | 빈 값은 무시 | `{status:'ok'}` |
| DELETE `/api/sessions/{id}` | | `{status:'ok'}` |
| GET `/api/sessions/{id}/messages?mode=build|answer|act` | | `{messages:[…]}` (없으면 `[]`) |
| PUT 같은 경로 | 메시지 배열(화면 형식 그대로) | `{status:'ok'}` |

`build_context` 형식: `{intent, golden_questions[], review_feedback[{question, answer, status, verdict, feedback}], datasources[{name, schemas[]}], documents[파일 이름], target_schema | new_schema_name, golden_commands[], systems[]}`. 서버는 공백 정리, 빈 항목 제거, 문서 이름에서 `/` 제거.

### 5.2 파일
| 메서드 경로 | 요청 | 응답 |
|---|---|---|
| POST `/api/upload` | multipart `files`(여러 개), `session_id` | `{uploaded:[{name, path:"/workspace/uploads/<name>", local_path, size}]}` 또는 항목별 `{name, error}` |
| GET `/api/files?session_id` | | `{uploads:[{name, size}], output:[{name, size}]}` (size 예 `12.3 KB`) |
| DELETE `/api/files/{name}?session_id` | | `{status:'ok'|'not_found', filename}` |
| GET `/api/uploads/{name}?session_id[&download=true]` | | 파일. md/markdown/txt/csv/json/sql/yaml/yml은 `text/plain; charset=utf-8` inline. 없으면 `{error:"파일을 찾을 수 없습니다: …"}` |
| GET `/api/download/{name}?session_id` | | 출력 파일(첨부) |
| POST `/api/sandbox/clear?session_id` | | `{status:'ok', message:'샌드박스 파일이 모두 삭제되었습니다.'}` |
- 작업 폴더는 A3 §5.2(세션별 `uploads/`, `output/`). 원본은 업로드를 세션 폴더와 샌드박스 공통 `uploads/`에 **두 벌** 쓴다(에이전트 경로 호환). 이름은 유니코드 NFC 정규화. **새 구현은 파일 이름의 경로 구분자·`..`를 거부할 것**(원본은 검사 없음).

### 5.3 스키마·그래프
| 메서드 경로 | 요청 | 응답 / 동작 |
|---|---|---|
| GET `/api/neo4j/status` | | `{status:'connected'|'disconnected', error?}` (화면은 30초마다) |
| GET `/api/schema` | | 모든 그룹 통합: `{classes:[{name, description, properties, binding_kind, binding?{datasource, schema, table, key_columns, base_conditions, label_property}, behaviors?[{name, description, parameters, output_columns, result_kind, verified_at, golden_question}]}], relationships:[{name, from_class, to_class, description, properties}], schemas:[{name, description, class_names}]}` — 이름순, 같은 클래스가 여러 그룹에 있으면 바인딩 있는 쪽 우선. SQL 템플릿은 넣지 않음 |
| PUT `/api/schema/classes` | `{name, original_name?, description, properties[], schema_name, binding_kind?}` | 이름이 바뀌면 모든 그룹의 클래스·관계·바인딩 이름과 그래프 라벨을 바꾼다. `{status:'ok', class, merge_warning?|warning?}` |
| DELETE `/api/schema/classes/{name}` | | 정의·관련 관계 유형·인스턴스 삭제 |
| PUT `/api/schema/relationships` | `{name, from_class, to_class, description, properties[], schema_name}` | `{status:'ok', relationship_type}` |
| DELETE `/api/schema/relationships/{name}?from_class&to_class` | | |
| GET `/api/schemas` | | `{schemas:[{id, name, description, intent, golden_questions, golden_commands, created_at, updated_at, classes:[{class_name, description, properties, binding_kind, entity_count}], relationships, total_entity_count}]}` 최근 갱신순 |
| GET `/api/schemas/{id}` | | 같은 형태 하나(엔티티 수 없음) / `{error:"스키마를 찾을 수 없습니다."}` |
| PUT `/api/schemas/{id}/brief` | `{intent, golden_questions[], golden_commands?[]}` | 커맨드를 생략하면 보존. `{status:'ok'}` |
| POST `/api/build-brief/draft` | `{datasources[{name, schemas}], documents[], target_schema, intent, golden_questions[]}` | `{intent, questions[{question, evidence}], note, error}`. 저장하지 않음. 소스가 없으면 note 「데이터소스나 문서를 먼저 고르면 초안을 만들 수 있습니다.」 형식 블록이 없으면 error 「에이전트가 초안 형식(ontology_brief_draft)을 반환하지 않았습니다.」 모든 실패는 200 + error. 요청 처리 중에도 다른 API가 막히지 않게 별도 작업자에서 실행 |
| DELETE `/api/schemas/{id}` | | 정의만 삭제(인스턴스 보존, **발행물도 남음**) |
| DELETE `/api/schemas/{id}/entities` | | 그룹의 클래스 라벨 인스턴스 삭제 `{status, deleted}` |
| POST `/api/schemas/{id}/rebuild` | | `{status, classes, relationships}` (원본은 실제 작업 없음) |
| GET `/api/graph?class_name&schema_name&limit=100` | | `{nodes:[{id(elementId), labels, properties, label}], edges:[…]}`; `limit=0`이면 라벨 집계용 |
| GET `/api/graph/search?q&class_name&limit=50` | | 이름/속성 포함 검색 |
| POST `/api/graph/nl-query` | `{question, schema_hint?}` | `{cypher, nodes, edges}` / `{error:"LLM 호출 실패: …"|"생성된 쿼리가 읽기 전용이 아닙니다."|"Cypher 실행 실패: …"}` — 원본은 OpenAI 호환 API를 직접 부름 |
| GET `/api/graph/neighbors?node_id&depth=1` | | 이웃 |
| POST `/api/graph/entities` `{class_name, properties, match_keys=['name']}`, PATCH `/api/graph/entities/{elementId}` `{properties}`, DELETE 같은 경로, POST `/api/graph/relationships` `{from_id, to_id, rel_type, properties}` | | |
| POST `/api/neo4j/clear-all` | | 그래프 전체 삭제 `{status:'ok', message:'Neo4j 데이터가 모두 삭제되었습니다.'}` |

### 5.4 액션 정의 (M1이 원천)
| 메서드 경로 | 요청 | 응답 |
|---|---|---|
| GET `/api/schema/classes/{c}/actions` | | `{actions:[액션 공개형], count}` |
| PUT `/api/schema/classes/{c}/actions/{a}` | `{system?, operation_id?, description, parameters, arg_mapping, effect, key_property, confirm_threshold, max_targets, policy, compensate, writeback_property, schema_name, steps?, golden_command?}` | 200 `{status:'ok', action, warnings[], next:'그래프에 발행해야 kinetic-action 이 이 정의를 씁니다.'}` / 422 `{error, action_name}` |
| DELETE `/api/schema/classes/{c}/actions/{a}?schema_name` | | `{status:'ok', deleted:'C.a'}` / 404 `{error:"액션 'C.a' 이(가) 없습니다."}` |
액션 공개형: `{class, name, description, parameters, key_property, system, operation_id, arg_mapping, effect, confirm_threshold, max_targets, policy, compensate, writeback_property, steps, golden_command, verified_at, verify_summary, version}`. 정의 계약은 §7.4.

### 5.5 데이터소스 바인딩·전략
| 메서드 경로 | 요청 | 응답 |
|---|---|---|
| GET `/api/datasources[?refresh=true]`, `/{ds}/schemas`, `/{ds}/tables?schema`, `/{ds}/tables/{t}/columns?schema`, `/{ds}/tables/{t}/sample?limit` | | M3 브리지 프록시(카탈로그 캐시 TTL, `refresh`로 갱신, `degraded` 표시) |
| GET/PUT/DELETE `/api/schema/classes/{c}/binding` | PUT `{datasource, table, source_schema, schema_name, column_map[{property, column, type, pii?, key?}], key_columns[], base_conditions[], label_property, extra_tables[], default_limit=100, notes}` | 바인딩하면 클래스 종류 virtual, 속성은 column_map에서 생성. 해제하면 materialized로, behavior 삭제 |
| GET `/api/schema/classes/{c}/binding/validate` | | 컬럼 변화(사라진/새/타입 변경) |
| GET/PUT/DELETE `/api/schema/classes/{c}/behaviors[/{b}]` | PUT `{sql_template, description, parameters[{name, type, required, default?}], output_columns, result_kind='rows', max_rows=200, golden_question, schema_name}` | 저장 전 기본값으로 실제 실행 검증(`smoke_test: passed|skipped`), 실패면 저장 안 함 `{error, detail?}` |
| POST `…/behaviors/{b}/invoke` `{arguments, limit}`, POST `…/behaviors/preview` (정의+arguments), POST `/api/schema/classes/{c}/fetch` `{filters, limit=50}` | | 행 `{columns, rows, row_count, sql?, elapsed_ms}` |
| POST `/api/schema/generate-from-catalog` | `{datasource, source_schema, schema_name, tables[], bind=true, include_relationships=true, dry_run}` | `{datasource, schema, classes[{class_name, description, table, source_schema, datasource, column_map, key_columns, label_property, column_count}], relationships[{name, from_class, to_class, description, from_column, to_column}], counts{classes, relationships, properties}}`; 카탈로그 없음 `{error, catalog_empty:true}` |
| GET `/api/build-strategy/recommend?has_documents&datasource&schema&intent&max_lag=2` | | `{inputs{…}, recommended, reason, available[], unavailable[{strategy, reason}]}` (§7.6) |
| POST `/api/schema/{id}/reverse-bind/preview` `{datasource, source_schema, limit=5}`, `/apply` `{datasource, source_schema, bindings[], include_auto=true, document_refs{}}` | | 후보 순위·판정 / `{counts{bound, unbound,…}}` |
| POST `/api/schema/{id}/causal/discover` `{datasource, source_schema, intent, target?, max_lag=2, fdr_q=0.05, dry_run}`, GET `…/causal/hypotheses?decision`, POST `…/causal/decide` `{decisions[]}`, POST `…/causal/apply` | | 전제 미충족은 `ok:false` + 빈 엣지(오류 아님) |
| POST `/api/schema/{id}/publish[?dry_run=true]`, DELETE 같은 경로 | | §7.5 결과 (화면 미사용, 에이전트·스크립트 용) |

### 5.6 배포
| 메서드 경로 | 요청 | 응답 |
|---|---|---|
| GET `/api/release/overview` | | `{graph, dev{url, graph, schema_version, types, changes(30), releases, ok, error?}, prod{…}, packages[{name, hash, created_at, schema_version, instances, slices, edges, types}]}` |
| POST `/api/release/export` | `{name?, keys?{Type: prop}}` | `{name, counts, skipped, hash, schema_version}`; 이름 규칙 `^[A-Za-z0-9._-]{1,64}$`(400), 중복 409 |
| POST `/api/release/plan` / `/apply` | `{name, actor?}` | 운영 관리 API의 계획/적용 결과(적용 제한 1800초) |
| GET `/api/release/package/{name}` | | 패키지 JSON 파일 |
| GET `/api/release/timeline?type&key_prop&key&target=prod&frm&to&system_at` | | 관리 API 중계 |
- 관리 API 계약(스냅샷·변경 이력·릴리스 내보내기/계획/적용)은 M4. 개발 = 앱의 포털 주소, 운영 = 설정값(기본 없음 → 운영 쪽은 항상 `ok:false`). 관리 API 불통은 502 `{error:"Ontological admin API unreachable: …"}`. 타입 키 자동 선택: 선언된 키 속성, 없으면 `clause_key, version_id, doc_id, code, grade, key, name` 중 처음 있는 것. 패키지 파일은 서버 쪽 패키지 폴더에 `<name>.json`(형식 `og-release/1`)으로 보관 — **새 구현은 사용자 데이터 폴더 아래에 둘 것**(원본 기본은 앱 설치 폴더 안).

## 6. 에이전트 계약 (구축)

### 6.1 모드·도구
- 구축 턴은 모드 `build`(A3 §5.1), 초안은 모드 `brief_draft`(읽기 전용 도구 6개). 도구 목록과 MCP 엔드포인트는 A3 §6.1을 그대로 따른다. 구축 도구 45개 중 M1이 의미를 정하는 것은 §7에 요약.
- 구축 모드에는 **실행·승인·검수 결정·인과 승격 도구가 없다**(의도된 권한 경계). dry-run(plan 생성)과 발행은 있다.
- 파일·셸 작업은 CLI 에이전트 자체 도구(내장 에이전트는 `execute`·`sandbox_*`).

### 6.2 구축 프롬프트 조립 (값에 라벨만 붙인다)
첫 턴(대화 기억이 없을 때; CLI 경로는 기억을 쓰지 않으므로 매 턴) 사용자 메시지는 값이 있는 라벨 블록만 빈 줄로 이어 붙인다. 순서:
```
[사용자 작업 요청]\n<prompt>
[구축 의도]\n<intent>
[연결 데이터소스]\n1. <ds>[ (스키마: a, b)]
[업로드 문서]\n- /workspace/uploads/<이름>
[대상 스키마]\n<이름>        ← 또는 [새 스키마 이름]\n<이름>
[골든 퀘스천]\n1. <q>
[연결 시스템]\n1. <system>
[인스턴스 원천]\n등록 시스템의 조회 API (system_query)      ← 시스템만 있고 문서·데이터소스가 없을 때
[실행 역할] — 액션 정책 roles 에는 이 이름만 쓴다\n- <role>: <설명>[ (클레임: …)]   ← 골든 커맨드가 있고 역할 목록이 설정돼 있을 때
[골든 커맨드]\n1. <c>
[검토 피드백]\n1. 질문: …\n   이전 판정: …\n   이전 상태: …\n   기존 답변: …\n   사용자 피드백: …
```
- 지시문은 프롬프트에 섞지 않는다(지시문의 원천은 스킬 파일 하나).
- build_context는 세션별로 저장한다. 요청에 의도·질문·커맨드 중 하나라도 있으면 저장(세션이 없으면 제목=프롬프트 앞 80자로 생성), 없으면 저장본을 복원한다.
- 내장 에이전트 등 대화 기억이 있으면 **이어가기 프롬프트**: `[사용자 후속 요청]`, `[최초 구축 의도]`, `[골든 퀘스천]`, `[연결 시스템]`, `[골든 커맨드]`, `[검토 피드백]`(한 줄 형식 `n. 질문 → 판정: …, 피드백: …`), `[이전 에이전트 세션 요약]`, `[기존 산출물 파일]`, `[현재 그래프 상태]`(그래프 통계 JSON), `[검색 힌트]`(출력 폴더 `_search_hints.json` 앞 1000자).
- 역할 목록은 설정값(JSON 배열 `[{role, description, claims[]}]`). 원본 예제 값: `scm_operator` — 「공급망 운영 담당 — 출하 우선순위·발주 보류·고객 안내를 요청할 수 있다」.

### 6.3 SSE (A3 §5.7에 더해 M1이 정하는 것)
- 시작 `status`: 첫 턴 `온톨로지 구축 에이전트를 시작합니다... (<n>개 Golden Question)`, 이어가기 `이전 대화를 이어서 진행합니다...`.
- `tool_start.description` 문구(한국어 한 줄): execute(명령 내용에 따라 「PDF 문서를 파싱하여 텍스트를 추출합니다」/「Excel 파일을 읽어 데이터를 추출합니다」/「파싱 결과를 JSON 파일로 저장합니다」/「파일 시스템을 탐색합니다」/「파일 내용을 읽습니다」/「코드를 실행합니다: <첫 줄 60자>」), 「<path> 디렉토리의 파일 목록을 조회합니다」, 「파일을 읽습니다: <이름>」, 「파일을 작성합니다: <이름>」, 「현재 온톨로지 스키마를 조회합니다」, 「클래스 '<name>' 를 생성합니다」, 「관계 유형 '<name>' (<from> → <to>)를 정의합니다」, 「'<class>' 엔티티를 생성합니다」, 「'<class>' 엔티티를 검색합니다」, 「관계 '<type>' 를 생성합니다」, 「파싱 결과를 Neo4j에 일괄 적재합니다[: <파일>]」, 「그래프 전체 통계를 조회합니다 (노드 수, 관계 수)」, 「Cypher 쿼리를 실행합니다: <60자>」, 그 밖 「<tool> 도구를 실행합니다」.
- 부수 이벤트 규칙(도구 결과의 MCP 봉투 `{"result":"<json>"}`를 먼저 벗긴다):
  - `neo4j_update{tool}`: `schema_create_class`, `schema_create_relationship_type`, `schema_group_create`, `entity_create`, `entity_search`, `relationship_create`, `neo4j_cypher`, 그리고 바인딩/해제 후.
  - `schema_created{schema_name}`: `schema_group_create` 결과의 `name`.
  - `datasource_update{tool, class_name?, behavior?, row_count?, elapsed_ms?, binding_kind?, datasource?, table?, error?(300자)}`: 데이터소스 계열 도구.
  - `ref_file{name, path}`: 파일 목록/읽기 결과에 나온 `/workspace/uploads/…`.
  - `/workspace/output/<이름>`이 결과에 나오면 출력 파일 목록에 추가(`done.files`).
  - `kinetic_plan{plan_id, status, requires_approval, tool}` / `kinetic_run{…}`: plan/run을 돌려준 도구(act 모드에서 주로).
- 성공 종료 직전 `todos{items:[{id:'schema_design', content:'Phase 1: 스키마 설계'}, {id:'data_ingest', content:'Phase 2: 소스 파싱 + 적재'}, {id:'validation', content:'Phase 3: 검증'}, {id:'quality_review', content:'Phase 4: 검수 — 사람이 판단할 항목 정리'}] (모두 completed)}`, 그다음 `done{message:'완료!', files, text, build_report}`.

### 6.4 구축 보고서 추출 규칙 (`done.build_report`)
1. 최종 텍스트에서 펜스 언어 `ontology_build_report`인 JSON 블록을 찾는다. 없으면 펜스 `json`(또는 언어 없음) 블록 가운데 `golden_questions` 또는 `golden_commands` 키를 가진 마지막 것(한 겹 감싼 형태 허용)을 보고서로 받는다. 화면 텍스트에서는 블록을 뺀다. 블록이 깨졌으면 보고서 없음.
2. `golden_questions[i]` 정규화: `question`(없으면 i번째 원래 질문), `answer`, `status`(기본 `answerable`), `confidence`(기본 `medium`). 항목이 하나도 없고 원래 질문이 있으면 모두 `not_yet_answerable`/`low`/빈 답.
3. `intent`(없으면 브리프 의도), `summary`, `next_action`.
4. `golden_commands`: 에이전트 항목(`command` 앞 번호 `1. `/`2) ` 제거, `class`, `action`, `steps`(이름 문자열), `verified`, `note`) → 액션이 비었으면 저장소에서 찾기: 액션의 `golden_command` 문장(번호 제거) 일치, 아니면 커맨드가 취소형(정규식 `취소|되돌|원복|원래대로|롤백|undo|cancel`, 대소문자 무시)이면 모든 단계에 보상이 있는 액션 하나를 `steps:['보상(역순)']`, `note:'보상 흐름 — compensate_run'`으로. 브리프 커맨드 중 보고서에 없는 것은 같은 방식으로 찾고, 못 찾으면 `{command, class:'', action:'', steps:[], verified:false, note:'액션이 만들어지지 않았습니다.'}`. 마지막으로 저장된 액션이 있으면 **`verified` = 저장소의 검증 시각 존재 여부**(에이전트 말 무시), steps가 비면 저장된 단계 이름들(단일 단계면 `['main']`).
5. 브리프 골든 커맨드를 스키마 그룹(새 이름 또는 대상)에 저장 — 그 그룹의 커맨드가 비어 있을 때만.
6. `quality` = 검수 현황 `{schema_id, to_review, held, held_by_reason, in_graph, pending_by_kind, schema_name}`(M6). 스키마는 세션의 schema_name, 없으면 이번 턴 도구 호출 인자 중 마지막 `schema_name`(그리고 세션에 기록).

### 6.5 지시문(스킬) — 의도와 구조 (요약, 원문 복사 금지)
**구축 스킬** (한국어 응답, 쓰기 가능). 구조:
1. 용도와 비범위(질의 응답은 다른 스킬).
2. 전제: 스키마·적재·검증 핵심 도구가 없으면 시작하지 말고 연결 방법을 알린 뒤 멈춤 — 지어내지 않기.
3. 권한 경계: 그래프는 도구로만, 전역 삭제 금지(패브릭 카탈로그까지 지워짐), 개인정보 컬럼 제외 또는 PII 표시.
4. 입력 점검: 표(작업 요청·구축 의도·골든 퀘스천·대상 소스 필수; 전략·대상 스키마·검토 피드백·골든 커맨드·연결 시스템 선택). 라벨이 아니라 정보 유무로 판정. 다 있으면 3~5줄 요약 후 바로 진행(확인 요구 금지), 빠지면 빠진 것만 구체적으로 묻고 턴 종료, 되묻기 최대 2회 후 가정 명시. 전략 선택지가 여럿이면 근거와 함께 사용자에게. 금지: 받은 것 다시 묻기, 지어내기, **골든 퀘스천·커맨드 문장 다듬기**.
5. 작업 경로: 환경 블록의 업로드/출력 경로, 없으면 현재 폴더 `uploads/`·`output/`을 알리고 사용.
6. 4단계 흐름:
   - **Phase 1 스키마 설계**: 전략 추천 도구 먼저 → 질문마다 필요한 클래스·관계 도출 → 데이터소스가 있으면 실제 카탈로그를 보고 클래스 종류(materialized/virtual) 판정 → 인제스천 패턴 선택 → 스키마 그룹 생성 후 클래스·관계 생성 → 질문별 해소 경로를 출력 폴더 `_schema_design.json`에 기록(`classes[{name, binding_kind, binding{…}}]`, `relationships`, `question_paths[{question, resolution: graph|behavior|hybrid, path, behavior, required_classes}]`).
   - **Phase 2 적재**: 신뢰도 게이트를 지나는 도구로만. 문장 속 사실 → `extract_triples`; 표 → `table_ingest`(원천 점검 규칙 필수, 엑셀은 CSV로 변환); 문서 구조(조·항) → 파서 작성·실행 → `batch_ingest`(파일 경로 권장). 데이터소스 → 객체 판정 → 필요시 뷰(미리 실행해 행 확인) → 바인딩 → 관계 선언(가상 클래스 사이도, 조인 키를 설명·속성에) → 질문마다 behavior. virtual 클래스에는 인스턴스 적재 금지.
   - **Phase 2.5 골든 커맨드 → 액션**(커맨드가 있을 때): §7.4.
   - **Phase 3 검증**: 질문마다 실제 실행(그래프는 읽기 전용 Cypher, behavior는 실제 행 `row_count>0`, hybrid는 둘을 이어서), PASS/FAIL, FAIL이면 스키마/데이터/behavior 갭으로 분류해 Phase 1·2로(최대 3회), 출력 폴더에 검색 힌트 `_search_hints.json`(`classes, searchable_properties, sample_queries, keyword_fields, virtual_classes, question_routing`). 커맨드가 있으면 발행 후 dry-run.
   - **Phase 4 검수**: 검수 점검 도구 1회 → 사람이 판단할 건수·원인을 쉬운 말 3~5줄로, 스키마·매핑으로 풀리는 보류면 고칠 방법 제안. 승인·기각·재처리는 하지 않음(사람이 검수 탭에서), 검수 대기 사실을 검증 근거로 쓰지 않음, 보류를 피하려 규칙 완화 금지.
7. 스키마 그룹 규칙: 시작 시 반드시 그룹 생성(이름은 의도 반영), 생성·적재 도구에 그룹 지정, 다른 그룹에 같은 클래스가 있으면 병합 여부 질문, `[대상 스키마]`면 그 그룹의 기존 클래스만 사용(새 클래스 금지), `[새 스키마 이름]`이면 묻지 않고 그 이름.
8. 핵심 규칙: 골든 퀘스천이 전부를 결정, 모든 업로드 파일을 먼저 탐색, 검증은 실제 실행, 물리 해석은 빌드 단계에서 끝내기(뷰), **클래스는 사물·behavior는 질문**(보고서 제목 같은 이름은 클래스가 아님), **관계 0개는 미완성**(반복 키 = 빠진 관계), 파서 출력 `{nodes, relationships}`, 클래스 PascalCase·관계 UPPER_SNAKE_CASE, content 2000자, 단계마다 한국어 설명, 참조 문서를 못 읽었으면 알리고 멈춤, 사용자 피드백 반영.
9. 완료 기준: 스키마와 그래프만으로 질문에 답할 수 있음, 각 질문 실제 실행 검증, 클래스 2개 이상이면 관계 존재, 마지막에 `ontology_build_report` 블록(질문 원문 유지), 커맨드마다 액션·dry-run 검증.

참조 문서 8개(필요한 단계에서 읽으라고 지시): 전략 표, 데이터소스 바인딩·behavior 규칙, 인제스천 패턴 A–D(D-1 카탈로그 일괄 생성 포함), 파서 규칙(2-pass 전체 텍스트→구조 분할, 모든 노드 `name`·`content` 필수, 목차 건너뛰기, 표는 행 노드, 의미 있는 노드 id `{타입}_{번호}`, 관계 속성에 출처 페이지, 원문에 없는 개념 금지, 실행 후 content 커버리지 80% 미만이면 파서 수정), 소스 유형별 라이브러리(PDF·Excel·Shapefile·Markdown/DOCX·PPTX), 골든 커맨드 규칙(§7.4), 검증·리포트 형식(§6.4 입력 형식), 검수 단계.

**브리프 초안 스킬** (한국어, 읽기 전용, 한 턴): 초안은 사용자가 고칠 재료 — 근거 없는 질문 금지, 확신 없으면 적게, 되묻지 않음. 입력 라벨 `[연결 데이터소스]`, `[업로드 문서]`, `[대상 스키마]`, `[기존 구축 의도]`, `[기존 골든 퀘스천]`(있으면 그 문장은 고치지 않고 빈 쪽만 채움). 흐름: 소스를 실제로 봄(데이터소스는 스키마 테이블 목록 → 눈에 띄는 테이블 3~6개 컬럼·샘플; 시간·수치·분류·외래키 컬럼에서 질문 유형 도출, 연결을 건너는 질문 최소 1개; 문서는 앞부분만) → 의도 한 문단(누가·무엇을 위해·어떤 판단) → 질문 3~5개(각각 근거, 근거 못 대면 버림; 구체적·답이 하나·서로 다름). 출력: 요약 3~5줄 + 펜스 언어 `ontology_brief_draft` JSON 하나 `{intent, questions[{question, evidence}], note}`. 소스가 없으면 빈 초안 + note.

초안 응답 해석: 블록이 없거나 깨지면 빈 초안(본문을 추측해 채우지 않음). questions 항목이 문자열이면 evidence 빈 값. 일회용 대화(세션 `brief-draft-<12hex>`)로 실행하고 끝나면 CLI 세션 기억을 지운다.

## 7. 데이터 모델과 규칙

### 7.1 스키마 그룹 레코드
`{id(12자 hex), name(유일), description, intent, golden_questions[문자열], golden_commands[문자열], created_at, updated_at}`. 생성은 같은 이름이 있으면 기존 것을 돌려준다. 이름으로 찾을 때 원본은 정확 일치가 없으면 **부분 일치(최근 것)**로 대체한다 — 새 구현은 정확 일치만 권장(§13).

### 7.2 클래스·관계
- 클래스 `{class_name, description, properties[{name, type, description?, key?, required?, pii?, source_column?}], binding_kind}`. 속성 타입: string, integer, float, boolean, date, list.
- 관계 `{name, from_class, to_class, description, properties[]}` — 키 (그룹, 이름, 출발, 도착).
- 출처 `{element_kind: class|property|relationship, element_key: Class | Class.prop | Rel:from:to, strategy: doc_reverse_bind|causal_discovery|catalog_schema|manual, evidence_kind: document|foreign_key|statistical|human, evidence_ref}` — 처음 기록이 우선.

### 7.3 인스턴스 적재 (`batch_ingest`)
- 입력: JSON 문자열 또는 파일 경로(`/workspace/…`는 작업 폴더로 해석). 형식 `{nodes:[{id, class, properties{}, parent_id?}], relationships:[{from_id, to_id, type, properties?}]}`.
- 품질 선별(M6): 식별자 결측·끝점 없는 관계·선언된 관계의 정의역/공역 위반은 쓰지 않고 보류함(DLQ)으로.
- 노드: `:_Entity:<class>`를 `_source_id = id`로 MERGE, 처음이면 `created_at`, 항상 `updated_at`, 속성 SET(문자열 2000자 초과는 잘라 `...`), `parent_id`는 `_parent_source_id` + `(부모)-[:CONTAINS]->(자식)`.
- 관계: 양끝을 `_source_id`로 찾아 MERGE(타입 없으면 `RELATED_TO`).
- 임베딩: 임베딩 없는 `_Entity` 최대 500개를 `name title content(1500자)`로 임베딩(설정된 경우), 벡터 인덱스 `entity_embedding_vector` 생성.
- 그룹 지정 시 사용된 클래스를 그룹에 등록 — **원본은 이때 기존 클래스의 설명·속성을 빈 값으로 덮어쓰는 것으로 보인다**(§13·모르는 점). 새 구현은 기존 정의를 보존.
- 응답 `{status:'ok', nodes_created, relationships_created, nodes_embedded, quarantined?{count, by_reason, samples, note}, errors?(최대 20)}`.

### 7.4 액션 정의 계약
**필드**: `action_name`(`^[A-Za-z][A-Za-z0-9_]*$`), `description`, `parameters`(JSON Schema object; 비면 `{"type":"object","properties":{}}`; 속성 이름 `^[A-Za-z_가-힣][A-Za-z0-9_가-힣]*$`; required ⊆ properties), `key_property`(같은 이름 규칙; 비면 클래스 속성 중 `key:true` → 바인딩 첫 키 컬럼의 속성명 → 빈 값=실행기가 노드 id 사용), `system`·`operation_id`(필수; steps가 있으면 첫 단계 값으로 덮음), `arg_mapping`(첫 단계와 같음), `steps[]`, `effect`(`read`|`write`, 기본 write), `confirm_threshold`(정수 ≥0, 기본 0 = 항상 승인), `max_targets`(정수 ≥1, 기본 50), `policy[{roles?[], when?(CEL), description?}]`(다른 키 금지; 비면 아무도 실행 불가), `compensate`(액션 이름, 메타데이터), `writeback_property`, `golden_command`(원문), `version`(갱신마다 +1), `verified_at`, `verify_summary`.
**단계**: `{name(^[a-z][a-z0-9_]*$, 액션 내 유일), title?, system, operation_id, arg_mapping, compensation?{system(비면 단계 시스템), operation_id, arg_mapping}}`.
**arg_mapping**: 키 `^(path|query|header|body)\.[A-Za-z0-9_.-]+$`(body는 점 경로, 숫자 세그먼트 = 배열 인덱스). 값은 문자열(`$` 없으면 리터럴) 또는 `{"$literal": 값}`. 표현식 뿌리: `$this.<속성>`, `$this.$key`, `$params.<이름>`, `$actor.<클레임>`, `$run.id`, `$plan.id`, `$before.<속성>`, `$steps.<단계>.response[.<경로>]`(다단계에서만; 전진 매핑은 **앞 단계만**, 보상은 자기 단계까지), `$cancel.reason`(보상 매핑만). 그 밖 `$…`는 오류 「…표현식 '<expr>' 의 뿌리를 알 수 없습니다. …」.
**검증 오류 문구**(422 `error`): 「액션 이름 '<n>' 은(는) 쓸 수 없습니다. 영문으로 시작하고 영문·숫자·밑줄만 씁니다.」, 「system(서비스 레지스트리 이름)이 비어 있습니다.」, 「operation_id 가 비어 있습니다.」, 「steps[i].name '<n>' 은(는) 쓸 수 없습니다. …」, 「단계 이름 '<n>' 이(가) 중복됩니다.」, 「policy 는 규칙의 배열이어야 합니다.」, 「policy[i] 에 알 수 없는 키가 있습니다: … (roles · when · description 만 씁니다)」, 「…: $cancel.reason 은 보상(compensation) 매핑에서만 씁니다.」, 「…: '<s>' 단계를 참조할 수 없습니다 (앞 단계만 — 보상은 자기 단계까지).」, 「confirm_threshold 는 0 이상이어야 합니다.」 등(형식: 사람이 고칠 수 있게 위치를 포함).
**저장 후 경고**(저장은 됨): 단계·보상마다 레지스트리 확인 — 「<라벨>서비스 레지스트리에 시스템 '<s>' 이(가) 없습니다.」, 「<라벨>시스템 '<s>' 에 operation '<op>' 이(가) 없습니다.」, 실행기 불통 「<라벨>operation 을 확인하지 못했습니다 (<msg>).」(라벨 `단계 <n>: ` / `단계 <n> 보상: `); 단계 2개 이상에서 보상 없는 단계 「보상이 없는 단계가 있습니다 — 뒤 단계가 실패하거나 취소해도 되돌리지 않습니다: a, b」; 정책 없음 「policy 규칙이 없어 아무도 이 액션을 실행할 수 없습니다(기본 거부).」
**스키마 해석**: 그룹 지정 시 그 그룹에 클래스가 있어야 함(「스키마 'X' 에 클래스 'C' 이(가) 없습니다.」), 미지정이면 클래스를 가진 첫 그룹, 없으면 「클래스 'C'을(를) 어떤 스키마에서도 찾을 수 없습니다. 먼저 클래스를 만들거나 schema_name을 지정하세요.」 액션은 바인딩과 무관하게 어떤 클래스에도 붙는다.
**정의를 고치면 검증 기록을 지운다.**

**에이전트의 골든 커맨드 처리 규칙(구축 스킬 참조 문서의 요지)**:
- 대상은 그래프 인스턴스(materialized)여야 한다. virtual 클래스를 가리키면 알리고 적재 방법 제안. 필터 속성은 숫자형으로 적재(표 적재는 문자열이 되므로 숫자 필요 시 파서 경로).
- 시스템만 재료일 때: GET 목록 operation으로 조회(`system_query`, 큰 결과는 `save_path`로 저장 후 변환) → 응답 필드를 속성으로, 레코드 `id` 보존, 업무 코드를 키로, 다른 코드 참조는 관계로 → materialized 적재 → 건수 확인.
- 시스템 목록 → operation 탐색. 시스템이 없거나 실행기 불통이면 액션을 지어내지 말고 「시스템 등록」 안내 후 건너뜀. 커맨드를 업무 흐름으로 풀어 여러 시스템 단계로.
- 보상 고르기: 같은 시스템의 cancel/revert/restore/undo/delete 계열, 상태 덮어쓰기면 같은 operation + `$before.<속성>`, 만든 리소스는 `$steps.<단계>.response.id`, 되돌릴 수 없는 단계는 보상 없이 설명에 명시. 취소형 커맨드는 새 액션이 아니라 앞 액션의 보상.
- 새 레코드를 만드는 커맨드는 기준정보 인스턴스(고객·품목·금형)를 대상으로, 나머지는 파라미터로.
- 정책: 역할은 `[실행 역할]` 목록의 이름만, 담당 범위 속성이 있으면 `when`으로 제한, 설명에 한 문장. confirm_threshold 일상 1~3 / 되돌리기 어려우면 0, max_targets 20~50, writeback_property 보통 `status`, `golden_command` 원문.
- 검증: 발행 → 커맨드마다 dry-run(조건을 구조화 필터로), 허용 0건이면 원인 점검 후 최대 3회. 액션을 고치면 검증이 지워지므로 **맨 마지막에 다시 발행·dry-run**, 보고 전 검증 시각 빈 액션이 없는지 확인. 취소형 커맨드는 모든 단계의 보상 존재로 검증(일부 없으면 「부분 취소만 가능」). 실행·승인 안 함.

**dry-run 도구 계약** (`action_dry_run(class_name, action_name, where='[]', params='{}', schema_name='')`): 정의 존재 확인 → 실행기에 계획 요청(**에이전트 신원** 토큰, 없으면 화면 신원) → 요약 `{plan_id, status, requires_approval, allowed(수), denied(수), allowed_keys(앞 10), denied_reasons(중복 제거 5), preview_calls, where, params}`; 허용 ≥1이면 `verified:true`로 검증 기록 저장. 응답 `{status:'ok', verified, summary, note}`(note: 「dry-run 만 했습니다 — 실행·승인은 하지 않습니다.」 / 「허용 대상이 0건입니다 — 조건(where)·정책·인스턴스를 확인하세요. 검증 기록을 남기지 않았습니다.」). 실행기 오류 `{error, code, hint, verified:false}`(not_found면 hint 「실행기가 이 액션을 모릅니다 — 스키마를 발행(publish)했는지 확인하세요.」).
**시스템 도구**: `system_list` → `{systems[{name, description, base_url, operations_count, route, health_path}], count}`(오류 시 hint 「kinetic-action 이 떠 있는지, 시스템이 「시스템 등록」에서 등록됐는지 확인하세요.」), `system_operations(system)` → `{system, operations[{operation_id, method, path, summary, parameters[{name, in, required, schema}], request_body_schema, source}], count}`, `system_query(system, operation_id, path_params, query, save_path)` → `{system, operation_id, ok, http_status, latency_ms, truncated_by_system, saved_to?, total_rows, shown_rows, truncated, envelope_key?, envelope?, fields, rows | data | data_text, note?}`(표시 상한 200행·60000자, save_path는 `/workspace/output/` 아래만, GET 아니면 code `not_readonly`).

### 7.5 발행
- 발행 단위 = 스키마 그룹. 멱등: 그 그룹의 이전 레지스트리 하위 노드를 지우고 다시 쓴다(다른 그룹·다른 서비스 노드는 건드리지 않음). 인스턴스는 건드리지 않는다.
- 그래프 `ontology`에 쓰는 형태(관찰 계약 — 포털 Cypher로 비교):
  - `(:_OntologyModel {schema_id, name, description, intent, golden_questions(JSON 문자열), golden_commands(JSON), format_version:1, published_at})`
  - `-[:HAS_CLASS]->(:_OntologyClass {class_name, description, binding_kind, properties(JSON)})`
  - `_OntologyClass -[:HAS_ACTION]->(:_OntologyBehavior {behavior_type:'action', behavior_name, class_name, schema_id, description, parameters(JSON, 빈 값은 빈 object 스키마), key_property, system, operation_id, arg_mapping(JSON, 빈 값 '{}'), effect, confirm_threshold, max_targets, policy(JSON), compensate, writeback_property, version, steps(JSON, 다단계일 때만; 단일이면 속성 없음)})` — **바인딩 유무와 무관하게** 쓴다.
  - `_OntologyClass -[:HAS_BINDING]->(:_OntologyBinding {class_name, datasource, source_schema, table_name, extra_tables, key_columns, column_map, base_conditions, label_property, default_limit})` — 자격 증명은 싣지 않음.
  - `_OntologyBinding -[:HAS_BEHAVIOR]->(:_OntologyBehavior {behavior_type:'sql', behavior_name, class_name, description, parameters, sql_template, output_columns, result_kind, max_rows, golden_question})`.
  - `_OntologyModel -[:HAS_RELATIONSHIP]->(:_OntologyRelationship {name, from_class, to_class, …})`.
  - 클래스별 키 제약 `ont_pub_<…>`(가상 클래스도 라벨 등재용; 앵커 노드는 남기지 않음), 더는 필요 없는 `ont_pub_*` 제약은 삭제.
  - 라벨·관계 이름 규칙 `^[A-Za-z_가-힣][A-Za-z0-9_가-힣]*$` 위반이면 발행 전체 중단(부분 적용 안 함).
- 발행 후 실행기에 카탈로그 다시 읽기를 요청(실패해도 발행 성공). 결과 `{status:'ok', dry_run:false, schema_id, schema_name, format_version, classes[{class_name, binding_kind, property_count, has_binding, behavior_count, action_count, constraint, key_property, source}], relationships[], counts{classes, virtual_classes, relationships, behaviors, actions}, constraints_created, constraints_dropped, kinetic_refresh}`. dry_run이면 그래프를 건드리지 않고 계획만.
- 발행 거두기: 레지스트리와 제약 삭제 + 실행기 새로고침.
- 에이전트 도구 `schema_publish(schema_name)` → `{status:'ok', schema, result}` / `{error:"스키마 그룹 'X' 이(가) 없습니다."}` / `{error:"발행 실패: …"}`.

### 7.6 전략 추천 결정 표 (결정적)
입력: 문서 유무, 데이터소스 유무, 의도 유무, 시계열 준비(데이터소스+스키마가 있을 때만 계산: 통계 서비스 불통이면 사유 「통계 서비스에 연결할 수 없습니다」, 카탈로그 없음/오류 사유, 날짜형 컬럼 없음 「시간축 컬럼이 없습니다. 테이블 N개를 검사했습니다. …」, 수치 컬럼 <2 「수치 변수가 N개입니다. 최소 2개가 필요합니다.」).
| 조건(위에서부터) | 추천 | 이유 문구 |
|---|---|---|
| 문서+데이터소스 | doc_reverse_bind | 「문서와 데이터소스가 함께 있습니다. 문서가 정의한 엔티티에 데이터소스를 역으로 찾아 바인딩합니다.」 |
| 데이터소스+의도+시계열 | causal_discovery | 「문서가 없고 인텐트가 있습니다. 데이터에서 인과 구조를 발견해 가설 관계로 만듭니다.」 |
| 데이터소스 | catalog_schema | 의도 없으면 「카탈로그 구조만으로 결정적으로 생성합니다. LLM 호출이 없습니다.」, 있으면 「인텐트가 있으나 인과 발견의 시계열 전제를 충족하지 않습니다. 카탈로그 구조로 생성합니다.」 |
| 문서 | document_only | 「바인딩할 데이터소스가 없습니다. 기존 문서 기반 경로로 인스턴스를 적재합니다.」 |
| 없음 | none | 「문서도 데이터소스도 없습니다. 최소한 하나가 필요합니다.」 |
available = 조건을 만족하는 모든 전략. unavailable 사유: 역바인딩 「문서가 없습니다 / 데이터소스가 없습니다」, 인과 「데이터소스가 없습니다」|「인텐트가 없습니다」|시계열 사유(없으면 「시계열 전제를 충족하지 않습니다」), 카탈로그 「데이터소스가 없습니다」. 최소 행 수 = max_lag×2+10.

### 7.7 카탈로그 일괄 생성 규칙 (LLM 없음)
- 카탈로그(데이터소스·스키마의 테이블·컬럼·PK·FK) 읽기, 테이블 없으면 「카탈로그에 '<ds>' / '<schema>' 테이블이 없습니다. 데이터 패브릭에서 메타데이터 추출을 먼저 실행하세요.」
- 클래스 이름 = 테이블 이름을 영숫자 아닌 문자로 나눠 각 조각 첫 글자 대문자(전부 대문자 조각은 Title 처리) 이어 붙임(`mfg_daily_equipment`→`MfgDailyEquipment`). 설명 = 테이블 설명 또는 `<사람 읽기 이름> (<schema>.<table>)`.
- 모든 컬럼이 속성(속성명=컬럼명), 타입 매핑: bool→boolean, int/serial→integer, numeric/decimal/float/double/real/money→float, timestamp/datetime/date/time→date, 그 밖 string. PK가 아닌 `_id/_no/_code/_key` 접미 컬럼은 `reference:true`.
- 키 = PK, 라벨 속성 = 이름이 name/title/label/code/description(또는 `_<그것>`으로 끝남) 순, 없으면 PK 첫 컬럼, 없으면 첫 컬럼.
- 관계 = FK마다 이름 `REFERENCES_<대상 테이블 대문자 조각_연결>`, 설명 `from_table.from_col → to_table.to_col`, 같은 (이름, 출발, 도착)은 하나.
- bind=true면 각 클래스를 그 테이블에 바인딩(virtual). 출처 `catalog_schema/foreign_key`.

### 7.8 역바인딩 점수
문서로 만든 클래스마다 카탈로그 테이블 후보 점수 = 열 일치 0.6 + 타입 일치 0.2 + 이름 토큰 겹침 0.2(설명도 일치 대상으로 봄). 판정 auto / needs_review / conflict(두 엔티티가 같은 테이블) / no_match. auto만 자동 적용, 나머지는 사람이 고른 것만. 테이블 없는 엔티티는 지우지 않고 미바인딩으로 남김. (임계값은 실행 기록·원본 문서 대조로 확정 — 모르는 점.)

## 8. 상태·저장
| 무엇 | 어디 | 수명 |
|---|---|---|
| 세션 `{id, title, mode, schema_name, …}`, 세션별 build_context, 화면 메시지(mode별) | 사용자 데이터 폴더 세션 DB | 영구, 세션 삭제 시 함께 |
| 스키마 그룹·클래스·관계·바인딩·behavior·액션·출처·인과 가설 | 같은 DB | 영구 (그룹 삭제 시 연쇄 삭제) |
| 인스턴스·발행 레지스트리·제약 | 그래프 `ontology` | 영구 |
| 업로드·파서·출력 파일 | `sandbox/sessions/<세션>/{uploads,output}` (+ 공통 `sandbox/uploads`) | 세션 초기화·삭제·샌드박스 비우기까지 |
| 릴리스 패키지 | 패키지 폴더(새 구현: 사용자 데이터 폴더) | 영구 |
| 화면만: 브리프 입력(새 대화 전), 초안 상태, 사이드바 접힘(브라우저 저장소) | 탭 메모리 | 탭 새로고침 시 사라짐(브리프는 첫 사용자 말풍선에 사본) |
- 첫 실행 예제 온톨로지(§10의 시드)는 「공급망 운영 (예제)」 정의·인스턴스·액션을 만들고 발행·dry-run까지 한다(A2 단계 표식). 새 구현의 시드는 사람이 화면/도구로 만든 것과 같은 모양이 되도록 **같은 저장·적재·발행·dry-run 경로**를 거쳐야 한다.

## 9. 다른 기능과의 의존
| 대상 | 관계 |
|---|---|
| A2 | 그래프 `ontology`(Bolt), 예제 가상 노드 그래프 `sample` |
| A3 | 대화 스트림·CLI 실행·브리지 MCP(build/brief_draft)·스킬 배치·끼어들기·세션 초기화 |
| M3 | 데이터소스 카탈로그(브리지 호환 엔드포인트), 패브릭 연결 여부 |
| M7 | 시스템 목록·operation·조회, 액션 저장 시 operation 존재 확인, 역할 목록·신원 토큰 |
| M6 | 신뢰도 게이트(문장 추출·표 적재·적재 선별), 검수 현황·검수 탭 카드 |
| M2 | 발행된 정의 소비, 계획 카드(승인·실행·취소) 컴포넌트 공유, act 화면에도 같은 오른쪽 패널 |
| M4 | 관리 API(배포), 발행물 Cypher 관찰 |
| M5 | 「이 온톨로지로 대시보드를 자동 구성」 이동, 골든 퀘스천·커맨드가 앱 예시로 |

## 10. 예제 온톨로지 「공급망 운영 (예제)」 (비교 기준 데이터)
- 그룹: 이름 `공급망 운영 (예제)`, 설명 「예제 업무 DB(ERP·WMS·CRM)의 협력사·발주·입고 선적·고객 주문·클레임. 예제 마이크로서비스로 액션을 실행한다.」, 의도 「공급망 운영 담당자가 늦어진 입고·품질 문제를 묻고, 긴급 처리·발주 보류·고객 안내를 시스템에 요청한다」.
- 클래스(설명, 키 *): Supplier「협력사 (ERP)」 supplier_id*·name·country·tier(integer) / Item「품목 (ERP)」 item_id*·name·safety_stock(integer) / PurchaseOrder「구매 발주 (ERP)」 po_id*·supplier_id·order_date(date)·amount_usd(float)·status / Shipment「입고 선적 (WMS)」 shipment_no*·ref_po_no·vendor_code·ship_status·delay_days(integer)·eta(date)·priority / Customer「고객 (CRM)」 cust_no*·name·country / SalesOrder「판매 주문 (CRM)」 so_no*·cust_no·sku_code·qty(integer)·status / Claim「고객 클레임 (CRM)」 ticket_no*·so_no·severity·opened_date(date)·subject.
- 관계(출발 속성 → 도착 키): ORDERED_FROM PurchaseOrder→Supplier(supplier_id), SHIPS Shipment→PurchaseOrder(ref_po_no), SHIPPED_BY Shipment→Supplier(vendor_code), PLACED_BY SalesOrder→Customer(cust_no), FOR_ITEM SalesOrder→Item(sku_code), ABOUT Claim→SalesOrder(so_no). 대상 키가 없는 값은 잇지 않음.
- 인스턴스: `sample` 그래프의 같은 이름 가상 노드 전체를 읽어 노드 id `sample:<Class>:<key>`, `name` 없으면 subject 또는 키 값.
- 골든 퀘스천 3, 골든 커맨드 4(튜토리얼 11 표와 같음).
- 액션 3(모두 effect write, confirm_threshold 0, max_targets 20, 역할 `scm_operator`):
  - `Shipment.expediteShipment` key shipment_no, 파라미터 reason(필수), 단계 wms(sample-wms `setShipmentPriority`: path.shipment_no=$this.shipment_no, body.priority=URGENT, body.reason=$params.reason, body.requestedBy=$actor.sub; 보상 같은 op로 priority=$before.priority, reason=$cancel.reason, requestedBy=$actor.sub) → erp(sample-erp `createExpediteRequest`: body.poId=$this.ref_po_no, reason, requestedBy; 보상 `withdrawExpediteRequest` path.request_id=$steps.erp.response.id, reason=$cancel.reason), 정책 when `target.ship_status != 'DELIVERED'`(「입고가 끝난 선적은 제외」), writeback priority, dry-run 조건 delay_days > 3, params reason 「생산 차질 우려」.
  - `PurchaseOrder.holdPurchaseOrder` key po_id, reason 필수, 단계 erp(`holdPurchaseOrder` path.po_id, reason, requestedBy; 보상 `releasePurchaseOrder` path.po_id, reason=$cancel.reason), when `target.status == 'OPEN'`(「미결 발주만」), writeback status, dry-run supplier_id = S-CN-01 그리고 status = OPEN.
  - `Customer.notifyCustomer` key cust_no, subject·message 필수, 단계 crm(sample-crm `createNotice` body.custNo, subject, message, requestedBy; 보상 `withdrawNotice` path.notice_id=$steps.crm.response.id, reason=$cancel.reason), 정책 역할만, writeback 없음, dry-run cust_no = C-200.
  - 설명 문장은 튜토리얼 15 표 수준으로 작성(원본 문장 그대로일 필요는 없음 — 비교는 구조).
- 순서: 그룹 → 브리프(+커맨드) → 클래스 → 관계 → 인스턴스 적재 → 액션 → 발행 → dry-run 3회(모두 verified 아니면 실패 처리, 다음 시작에 재시도).

## 11. 오류·예외
| 상황 | 동작 |
|---|---|
| 브리프 미완 | 시작 버튼 비활성 + 안내 문구(§4.2) |
| 초안 실패 | 200 + error, 화면 「초안을 만들지 못했습니다…」, 브리프 작성은 계속 가능 |
| 에이전트 실행 오류·시간 초과·CLI 종료 | `error_event` → 「\n오류: <message>」 (A3 §14) |
| 사용자 중단 | 스트림 종료, 「[중단됨] …」, 서버 프로세스 정리(A3) |
| 그래프 연결 끊김 | 상태 배지 「Ontological 연결 안됨」, 스키마 API는 빈 목록 + error |
| 데이터 패브릭 불통 | 데이터소스 영역 숨김 + 안내, 바인딩 저장 시 컬럼 검증 건너뜀 문구 |
| 실행기 불통 | 액션 정의는 저장(경고), 편집기 경고, dry-run 불가, 에이전트는 시스템 단계 건너뜀 |
| 발행 전 dry-run | not_found → 발행 안내 문구 |
| 액션 정의 위반 | 422 + 위치 포함 한국어 오류, 저장 안 함 |
| 발행 이름 규칙 위반 | 발행 중단, `{error}` |
| behavior 실행 실패 | 저장 안 함, `{error, detail}` |
| 카탈로그 비어 있음 | `{error, catalog_empty:true}` |
| 관리 API 불통(배포) | 502 + error, 카드에 오류 |
| 같은 이름 클래스 | 정의 병합 경고 「클래스 'X'이(가) 이미 스키마 'Y'에 존재합니다. 병합되었습니다.」, 에이전트는 병합/분리 질문 |
| 존재하지 않는 스키마 이름 | 「스키마 'X'을(를) 찾을 수 없습니다.」(warning) |

## 12. 원본과 비교할 테스트 항목 (구조·계약, ADR-0010)
1. 구축 탭 첫 로딩 API 호출 집합과 각 응답 키.
2. 브리프 단계 요약 문자열·시작 조건·안내 문구(입력 조합 표 5가지).
3. 초안 자동 요청: 디바운스·생략 조건·응답 적용 규칙(사용자 칸 보존, draft 배지) — 응답은 목(mock)으로 고정해 비교.
4. `POST /api/build-brief/draft` 응답 형식과 실패 형식, 초안 프롬프트 라벨 블록(목 에이전트로 캡처).
5. 권장 전략 결정 표 전 조합(목 카탈로그·통계 상태)에서 `recommended/available/unavailable` 동일.
6. 구축 턴의 `/api/stream` 쿼리, 에이전트가 받은 라벨 블록(브리프 조합별: 문서만 / 데이터소스만 / 시스템만+커맨드 / 대상 스키마 / 피드백), 저장된 build_context.
7. SSE 이벤트 순서 패턴 `status → (token|tool_start|tool_result|부수 이벤트)* → todos → done`과 각 data 키, tool_start 설명 문구, 부수 이벤트 발생 규칙(도구별).
8. 보고서 추출: 정상 블록 / json 대체 블록 / 블록 없음 / 질문 누락 / 커맨드 누락·취소형·저장소 검증 덮어쓰기 — 같은 입력 텍스트·저장소 상태에서 `build_report` JSON 동일.
9. 세션 API(생성·제목·schema_name·메시지 저장/복원)와 대화 전환 시 브리프 복원.
10. 파일 API 응답 형식, 저장 위치 구조.
11. 스키마 API: `/api/schema`, `/api/schemas` 형태, 클래스 이름 변경이 그룹·관계·바인딩·그래프 라벨에 반영.
12. `batch_ingest` 결과 형식과 그래프 결과(라벨 `_Entity`, `_source_id`, CONTAINS, 2000자 자르기).
13. 액션 정의 검증: 경계 사례 표(이름·단계 slug·중복·표현식 뿌리 각 종류·`$cancel`·`$steps` 앞/뒤·정책 키·정수 범위) → 같은 수락/거절과 오류 위치. 저장 후 경고 문구·version 증가·검증 기록 초기화.
14. 액션 편집기 인자 자동 채움 결과(예제 시스템 operation 대상).
15. 발행 후 그래프의 레지스트리 노드·관계·속성 집합과 제약 이름(포털 Cypher로 비교), 재발행 멱등, 거두기.
16. dry-run 도구 응답 요약 키와 검증 기록 조건(허용≥1), 에이전트 신원 사용.
17. 카탈로그 일괄 생성 계획(목 카탈로그) — 클래스·관계 이름·키·라벨·타입 동일.
18. 예제 온톨로지 시드 결과: 그룹 1, 클래스 7(속성·키), 관계 6, 인스턴스·관계 수, 액션 3(정의 전체), 발행물, dry-run 3건 verified.
19. 초기화·스키마 삭제가 지우는 범위(그래프·DB·파일).
20. 배포 overview 응답 형태(운영 미설정 시 `prod.ok=false`).

## 13. 구현 시 결정할 것 (원본 동작 vs 개선)
1. **초기화 「Ontological 데이터」 범위** — 원본은 그래프 전체 삭제(예제·발행물·패브릭 관련 노드 포함 가능). 권장: 스키마 그룹 단위 삭제로 축소, 또는 원본과 같게 두고 경고 강화.
2. **스키마 삭제 시 발행물 처리** — 원본은 거두지 않아 질의 측에 남는다. 권장: 삭제 시 발행 거두기.
3. **이름 부분 일치 조회** — 원본은 정확 일치 실패 시 부분 일치로 다른 그룹을 고를 수 있다. 권장: 정확 일치만.
4. **적재 시 클래스 정의 덮어쓰기** — 원본은 적재 도구가 기존 클래스 설명·속성을 비울 수 있다(추정). 권장: 보존.
5. **발행 버튼** — 원본 화면에 없음(대화로만). 권장: 정보 탭에 「발행」(dry-run 계획 → 확인 → 발행) 추가 여부 결정. 비교 테스트는 원본 동작(버튼 없음) 기준.
6. **데이터소스 SQL 경로** — 원본 데스크톱 패키지에서 behavior·미리보기·뷰는 거절될 가능성이 높다. 새 구현은 (a) 원본처럼 두고 가상 노드 Cypher 경로만 지원, (b) 원천 읽기 전용 SQL 실행기를 붙여 패턴 D를 살림 중 선택.
7. **문서 OCR·인덱싱** — 원본은 미연결. 넣을지 결정.
8. **업로드 이름 검증·작업 폴더 격리** — 경로 이동 차단, 공통 uploads 이중 저장 여부.
9. **편집기 dry-run 계획 카드의 승인·실행 버튼** — 원본은 구축 화면에서도 실행까지 가능(M2 컴포넌트 공유). 구축 화면에서는 「계획 보기 전용」으로 제한할지 결정.
10. **그래프 탭 자연어 질의** — 원본은 OpenAI 키 직접 사용. CLI 에이전트 경로(A3 단발 질의)로 바꿀지.
11. **릴리스 패키지 위치** — 사용자 데이터 폴더로.
12. **전략 선택 전달** — 원본 화면의 권장 전략은 에이전트에 전달되지 않는다(스킬은 `[전략]` 라벨을 기대). 전달할지 결정.
13. 보안(A3 §11 연장): 구축 에이전트는 권한 우회 모드로 셸·파일을 쓰며 백엔드 환경(그래프 슈퍼유저 비밀번호, 실행기 토큰)을 물려받는다 → 액션 정의·실행 경계를 프로세스 수준에서 보장하지 못함.

## 14. 모르는 점 (4단계 실행 기록에서 확인)
1. 카탈로그 일괄 생성(「테이블 구조로 바로 생성」)이 이 패키지에서 동작하는가 — 카탈로그를 그래프의 테이블·컬럼 노드에서 읽는데, 그런 노드가 `ontology` 그래프에 있는지 불명. 오류 문구가 기대 결과일 수 있다.
2. 바인딩 behavior 테스트·저장, 쿼리 미리보기, 뷰 생성이 패브릭 브리지 501로 실패하는가(「실행 실패 (HTTP 501)」). 에이전트가 데이터소스 소스로 구축할 때 실제로 어떤 경로를 택하는가(가상 노드 Cypher, 셸로 그래프 직접 접속 등).
3. 역바인딩 판정 임계값(auto/needs_review 경계)과 미리보기 응답 형식.
4. 인과 발견이 통계 서비스 없이 어떤 응답을 내는가(권장 전략 사유 문구 포함).
5. 적재 도구가 그룹 지정 시 기존 클래스 설명·속성을 실제로 지우는가(예제 시드 후 `/api/schemas`의 Supplier 속성 수로 확인 — 튜토리얼 화면에는 속성이 보였으므로 다른 경로가 복원할 가능성).
6. 첫 턴 이후(CLI) 후속 메시지에 매번 전체 라벨 블록이 다시 가는가(A3 모르는 점과 동일).
7. 배포 탭의 실제 화면·오류 문구(운영 미설정), 패키지 내보내기 성공 여부와 파일 위치(앱 번들 내부 쓰기 가능 여부).
8. 업로드 파일이 두 위치에 생기는지, 세션 간 공통 uploads 때문에 다른 대화의 파일이 에이전트에 보이는지.
9. 튜토리얼 12의 「같은 대상 맞추기」(엔티티 식별)가 실제로 어느 도구에서 일어나는가 — 문장 추출 파이프라인의 해소 단계(재순위 서비스 없음 상태)로 추정.
10. 「발행해 줘」 턴에서 에이전트가 부르는 도구와 소요 시간, 발행 후 레지스트리 노드 실측.
11. 액션 편집기 dry-run 카드에서 「실행」 버튼이 활성인가(작성자 = 화면 신원이라 활성 추정) — 실제 실행은 하지 않고 표시만 확인.
12. 보고서의 `quality.schema_id`가 「검수 탭에서 보기」로 정확한 스키마를 여는지.
13. 화면 문구 중 미확인: 배포 탭 전체, 그래프 탭 엔티티 편집 폼, 정보 탭 관계 편집 폼 세부.
