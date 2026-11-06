# M5 온톨로지 앱 — 설계 문서 (클린룸)

- 상태: 초안 v0.1 (정적 분석 기반, 2026-11-01). "모르는 점"은 원본 동작 기록(4단계) 후 갱신.
- 대상: Ontological Studio 0.1.1의 「온톨로지 앱」(Studio 화면 이름 「대시보드」)과 같은 동작을 하는 새 구현.
- 이 문서만으로 구현할 수 있게 쓴다. 원본 코드·파일 경로·내부 함수 이름은 넣지 않는다. 외부에서 관찰되는 계약(HTTP 경로, 요청·응답 필드, SDK 함수, 화면 문구, 환경 변수 이름)은 비교 테스트를 위해 적는다.
- LLM이 결과를 만드는 부분은 **구조·계약**(입력 블록, 출력 형식, 허용 도구, 후처리 규칙)으로 적는다(ADR-0010).
- 관련 문서: A1 셸(탭·웹 오리진), A3 에이전트·MCP(CLI 실행, 검색 MCP 서버, 에이전트 브리지 MCP `dashboard` 모드, 스킬), M1 구축(발행 온톨로지·골든 퀘스천·액션 정의), M2 질의·액션(계획 카드·액션 실행 API), M7 시스템 등록(액션 실행기), M8 설정(studio.env).

---

## 1. 목적

발행된 온톨로지 위에서 **업무 화면(앱)** 을 말로 만든다. 두 종류가 있다.

| | 대시보드 | 코드 앱 |
|---|---|---|
| 정체 | 위젯 정의(JSON 명세) 하나. 렌더러가 그린다 | 정적 웹 파일 묶음(HTML·JS·CSS) 하나 |
| 만드는 주체 | **결정적 엔진**이 위젯 종류·축·지표를 정하고, 에이전트는 "명세 패치"만 제안, 사람이 적용 | CLI 코딩 에이전트가 앱 폴더에 코드를 직접 씀 |
| 데이터 | 서버가 위젯 정의에서 Cypher(그래프 적재 클래스) 또는 SQL(가상 클래스)을 조회 시점에 만들어 검색 MCP 서버로 실행 | 앱이 SDK로 **읽기 전용 Cypher**를 보냄 |
| 값 바꾸기 | 위젯의 「액션」 버튼 → 액션 실행기의 계획·승인·실행·취소 | SDK `act()` 확인 창 → 같은 경로 |
| 저장 | 대시보드 명세 JSON 파일 | 사용자 데이터 폴더 `codeapps/<id>/` |

핵심 원칙
1. **저장물에 질의문이 없다.** 대시보드 명세에는 클래스·속성 이름과 집계만 있고, 질의는 조회할 때 만든다. 자격 증명도 넣지 않는다.
2. **위젯 종류는 엔진이 정한다.** 같은 데이터 모양은 언제나 같은 위젯이 된다. 에이전트가 위젯을 "추가"하면 클래스 이름만 받아 엔진 추천으로 바꾼다. 사람이 종류를 명시하면 그 위젯은 "고정됨".
3. **에이전트 제안은 사람이 적용한다.** 자연어 편집 결과는 검증된 diff로 보이고, 「적용」을 눌러야 반영된다.
4. **앱은 업무 시스템을 직접 부르지 않는다.** 값을 바꾸는 일은 액션 실행기 경로로만, 승인·실행·취소는 사람이 누른다.
5. **코드 앱은 빌드가 없고 오프라인으로 뜬다.** 라이브러리(Vue 3, ECharts)와 SDK는 앱이 제공한다.

## 2. 사용자 시나리오 (요약 — 상세는 user-scenarios.md)
- S1 화면 열기: 갤러리(앱 만들기 입력, 모델 전체 자동 구성, 코드 앱 목록, 대시보드 목록).
- S2 말로 대시보드 만들기: `@클래스` 멘션 → 엔진이 즉시 위젯 배치(약 1초) → 남은 말은 에이전트 구성안(diff, 수십 초) → 「적용」.
- S3 이어서 고치기: 위젯 `@` 멘션으로 말로 고치기, 인스펙터 직접 설정, 자동 추천으로 되돌리기, 되돌리기, 배치 변경, 저장.
- S4 전역 필터·선택 연동: 필터가 걸리는 위젯 수 표시, 막대 클릭 → 관련 위젯 교차 필터.
- S5 모델 전체 자동 구성(「대시보드도 같이 생성」).
- S6 빈 화면에서 끌어다 놓기. S7 Superset 내보내기. S8 위젯 액션 버튼. S9 열기·삭제·홈 최근 항목.
- S10–S15 코드 앱: 만들기(1–3분), 같은 세션으로 말로 고치기, 파일 보기·손으로 고치기, 앱 탭으로 열기, 액션 버튼(SDK 확인 창), 삭제·실행 중 상태·재시작 후 재생.
- S16 읽기 전용·사람 승인 경계, S17 오류·대체 경로, S18 종합 과제, S19 에이전트별 차이.

## 3. 구성

```
[Studio 화면 view=board]
   ├─ 대시보드 API  /api/board/*        → 분석 백엔드 (대시보드 모듈)
   │      └─ 데이터: 검색 MCP 서버(A3)의 리소스 graph://schema, 도구 ontology_graph_cypher /
   │                 ontology_query_datasource_sql / ontology_get_datasource_schema
   │      └─ LLM: CLI 에이전트(스트리밍 편집 시 백엔드 자신의 에이전트 브리지 MCP dashboard 모드에 연결) 또는 OpenAI 호환 API
   ├─ 액션 API     /api/act/*, /api/schema/classes/{c}/actions  → 분석 백엔드의 액션 프록시(M2/M7)
   └─ 코드 앱 API  /codeapps/api/*      → 데스크톱 셸(같은 로컬 웹 오리진)
          ├─ 읽기 전용 Cypher: 셸의 그래프 연결(읽기 모드 세션, 그래프 `ontology`)
          ├─ 에이전트 한 턴: 보조 스크립트 → claude / codex 자식 프로세스(앱 폴더에서)
          └─ 정적 제공: /apps/_runtime/* (SDK·스타일·Vue·ECharts), /apps/<id>/* (앱 파일)
[앱 탭]  http://127.0.0.1:<web>/apps/<id>/  — 셸 브리지(렌더러 API) 없이 뜬다
```
- 모든 경로는 로컬 웹 오리진(127.0.0.1, 인증 없음, A1 §7) 하나에 있다.

---

## 4. 화면 구성과 상호작용

### 4.1 공통: 멘션 입력창
- contenteditable 입력. `@` 다음 글자로 후보(클래스·속성·위젯)를 최대 8개 띄운다. 후보 항목: 이름(속성은 속성명), 사람이 읽는 이름(다를 때), 보조 줄(모델 이름 또는 소속 클래스), 종류(클래스/속성/위젯). 맨 아래 「↑↓ 고르기 · Enter 넣기 · Esc 닫기」.
- 고른 자원은 **칩**(`@이름`)으로 들어가며, 백스페이스 한 번에 통째로 지워진다. 이미 넣은 자원은 후보에서 빠진다. 칩 툴팁 = 종류 · 사람 이름 · 보조 줄.
- 자원 트리/팔레트에서 끌어다 놓으면 놓은 위치(단어 경계로 맞춤)에 칩이 들어간다. 붙여넣기는 평문만(최대 3000자). 한글 조합 중 키 입력은 무시.
- 제출: ⌘/Ctrl+Enter(대시보드 AI 패널·코드 앱 대화창은 Enter, Shift+Enter 줄바꿈).
- 자원 참조 형식(요청 본문 `resources[]` 각 항목 `{ref, kind, name, note}`): `class:<모델명>/<클래스>`, `prop:<모델명>/<클래스>.<속성>`, `widget:<위젯 id>`. `note`는 속성을 클래스 아래에서 골랐을 때 `<클래스> 안`.
- **사람이 읽는 이름 규칙:** 클래스 설명에서 ` — `, ` – `, ` - ` 중 처음 나오는 구분자 앞부분, 끝의 괄호 덩어리 제거. 비거나 클래스 이름과 (대소문자·공백·_·- 무시) 같으면 클래스 이름.

### 4.2 갤러리 (화면 진입 시)
- 머리말 「온톨로지 앱」 / 「발행된 온톨로지로 만든 화면들입니다.」 / 버튼 「+ 빈 화면에서 시작」.
- **앱 만들기 영역** 「말로 만드는 온톨로지 앱」
  - 안내: 「왼쪽 자원을 문장 안으로 끌어다 놓거나 `@` 로 부르세요. **대시보드**는 멘션한 클래스가 바로 위젯이 되고 나머지 말은 에이전트가 구성안으로 냅니다. **코드 앱**은 에이전트가 앱의 코드를 직접 씁니다.」
  - 왼쪽 서랍(기본 열림) = 자원 트리: 검색 「자원 찾기 (클래스·속성)」(클래스 이름·사람 이름·설명, 속성 이름에 걸림; 속성만 걸리면 그 클래스를 펼친 채 표시), 모델별 묶음(제목·개수), 클래스 줄(사람 이름, 다르면 클래스 이름, 가상이면 「가상」 배지 — 툴팁 「데이터소스에 바인딩됨 — 질의하면 원천 데이터가 나옵니다」, 「+」 = 입력창에 넣기, 더블클릭 동일), ▸로 속성(`_` 접두 제외) 펼침. 하단 「클래스 N개 · 끌어다 놓거나 + 를 누르세요」. 빈 경우 「발행된 클래스가 없습니다.」/「걸리는 자원이 없습니다.」
  - 「앱 이름」(최대 60자, placeholder 「비우면 문장에서 짓습니다 — 예: 공급망 현황판」), 입력창(placeholder 「예: @PurchaseOrder 를 공급사별 금액으로 보고, 늦어지는 @Shipment 상태도 같이 보여 줘」).
  - 「골든 퀘스천」 칩: 발행 모델들의 골든 퀘스천(문자열 또는 `{question|text}`) 중복 제거 최대 6개, 누르면 입력창 커서 위치에 문장+공백 삽입.
  - 모드 전환 「대시보드」(기본)/「코드 앱」, 서랍 토글 「▤ 자원 닫기 / ▤ 온톨로지 자원」(+ 넣은 자원 수).
  - 안내 문구: 코드 모드 「에이전트가 Vue 앱 코드를 쓰고 미리보기로 띄웁니다 — 몇 분 걸립니다.」 / 멘션 클래스가 있으면 「위젯 N개를 바로 놓고, 나머지는 에이전트에게 묻습니다.」(멘션을 뺀 말이 없으면 뒷부분 생략) / 입력이 비면 「⌘/Ctrl + Enter 로도 만듭니다.」 / 그 외 「에이전트가 클래스를 골라 구성안을 냅니다.」
  - 버튼: 「앱 만들기 →」/「코드로 앱 만들기 →」, 진행 중 「만드는 중…」. 문장도 자원도 없으면 비활성.
- **자동 구성 영역** 「모델 전체로 자동 구성」 / 「클래스를 훑어 위젯을 정하고, 골든 퀘스천 순서로 배치합니다.」, 모델 선택(기본 첫 모델), 버튼 「대시보드도 같이 생성」(진행 중 「구성 중…」). 아래 진행 로그(⚙ 도구 · 인자 / ↳ 결과 / 오류 / 텍스트).
- **코드 앱 목록**(있을 때만) 「코드 앱 N」: 카드 = 이름, 「코드」 배지 + 상태(「에이전트 작업 중」/「마지막 작업 실패」/「수정 N회」) · 날짜(월/일 시:분), ×(확인 「«이름» 의 코드를 지웁니다. 되돌릴 수 없습니다.」 취소/삭제).
- **대시보드 목록** 「대시보드 N」: 카드 = 이름, 「위젯 N개 · 날짜」, ×(확인 「«이름» 을 지웁니다. 되돌릴 수 없습니다.」 → 「삭제했습니다.」). 로딩 「불러오는 중…」, 빈 상태 「아직 만든 앱이 없습니다. 위에서 말로 만들거나 모델 전체로 자동 구성하세요.」
- 화면 진입 순서: 대시보드 health → classes → 액션 목록(`GET /api/act/actions`, 실패해도 무시, 클래스별로 묶음) → 대시보드 목록. 코드 앱 목록은 별도 조회.
- 외부에서 "이 모델로 자동 구성" 요청을 받고 열린 경우(M1 구축 직후 연계) 갤러리로 돌아와 바로 자동 구성을 시작한다.

### 4.3 「앱 만들기」 동작
- **대시보드 모드**
  1. 이름 = 입력 이름 → 없으면 (멘션 칩을 지운 문장, 그것도 없으면 원문)에서 `@` 제거 후 24자 → 없으면 「새 앱」.
  2. 저장 키 = 이름의 공백을 `-`로. 기존 대시보드 id와 겹치면 `-2`, `-3`, … 붙임.
  3. 편집 화면으로 바꾸고, 멘션된 자원에서 클래스(속성 멘션이면 그 클래스, 중복 제거)마다 §4.4 "클래스 추가".
  4. 바로 저장(PUT).
  5. (멘션 칩을 뺀 말이 남았거나, 속성 멘션이 있거나, 위젯이 0개면) AI 편집 요청(§4.6). 말이 없으면 「고른 자원으로 앱 화면을 구성해 주세요.」를 요청으로 쓴다. 결과가 유효한 구성안이면 「구성안이 오른쪽에 있습니다 — 적용을 누르면 반영됩니다.」. 아니면 「위젯 N개로 만들었습니다.」
- **코드 모드**: 코드 앱 생성(`POST /codeapps/api/apps`) → 첫 턴 시작(`POST …/turns`, 같은 문장·자원) → 코드 앱 화면. 실패 시 갤러리 로그에 「코드 앱을 시작하지 못했습니다: <오류>」.

### 4.4 대시보드 편집 화면
- 머리: 「‹ 갤러리」, 이름 입력(기본 「새 대시보드」), 「되돌리기」, 「저장」, 「Superset 내보내기」. 상태 메시지는 4초간 표시.
- **왼쪽 팔레트** 「온톨로지 객체」 + 「새로고침」(클래스 다시 읽기)
  - 안내: 실데이터 확장이 꺼져 있으면 「데이터소스 확장이 꺼져 있습니다. 가상 클래스는 데이터를 읽을 수 없습니다 (`MCP_ALLOW_DATASOURCE_EXPANSION=false`).」, MCP가 안 되면 「MCP 에 연결하지 못했습니다. <오류>」, 서버 note가 있으면 그 문장.
  - 힌트: 「클래스를 캔버스로 끌어다 놓으면 위젯이 자동으로 정해집니다. 오른쪽 아래 AI 입력창에 놓으면 **@멘션**이 됩니다 — ▸ 를 열면 속성도 멘션할 수 있습니다.」
  - 클래스 줄: 사람 이름(+클래스 이름), 배지 「가상」 또는 「N속성」, 발행 레지스트리에 없으면 「고아」(툴팁 「발행 레지스트리에 없습니다」). 툴팁: 설명 / 부가 설명 / 「데이터소스: ds · schema.table」 / 확장 꺼짐 안내. 확장 꺼진 가상 클래스는 비활성(끌기 불가). 끌어다 놓거나 더블클릭 = 클래스 추가.
- **필터 막대** 「필터」 + 「+ 필터 추가」(§4.5).
- **캔버스**: 12칸 격자, 셀 높이 190px, 여백 8px, 끌어서 이동·크기 조절(배치는 위젯 `layout`에 반영). 캔버스 너비 ≥860px면 2열(w=6), 아니면 1열(w=12); 새 위젯 높이 2. 창 크기 변경 시 다시 배치.
  - 비었을 때: 「두 가지 방법이 있습니다.」 / **끌어다 놓기** — 왼쪽 목록에서 객체를 캔버스로 옮기면 위젯이 자동으로 정해집니다. / **대화** — 오른쪽 아래 대화창에 무엇을 보고 싶은지 쓰면 에이전트가 구성안을 냅니다. **@** 로 클래스·속성·위젯을 멘션할 수 있습니다.
  - 위젯 머리: 제목(위젯 제목이 클래스 이름과 다르면 그것, 아니면 사람 이름), 규칙 코드, 위젯 종류, `@` 버튼(이 위젯을 AI 입력창에 멘션), 「액션 N」(그 클래스에 쓸 수 있는 액션이 있을 때; 툴팁 「N개 액션 — 계획 · 승인 · 실행 · 취소」), 「필터 N」 배지(적용된 필터·선택 수, 툴팁 `라벨: 조인(<관계>)`/`same_class`/`same_name`/걸리지 않은 사유 줄들), 잘림 배지(`N건 중 M건`), 「집계 승격」 배지(툴팁 = 승격 내용 JSON).
  - 위젯 본문(차트): 오류면 오류 문장, 행 0이면 「데이터가 없습니다.」, kpi/kpi_group은 첫 행의 열마다 큰 숫자+열 이름, table·pivot_table(현재 표로 그림)은 HTML 표(행 클릭 = 선택), 나머지는 차트(§4.7).
- **클래스 추가**: 「<클래스> 분석 중…」 → 추천 API → 가드면 「<클래스>: <사유>」 → 아니면 주 위젯을 배치하고 조회, 화면을 그 위젯으로 스크롤, 기존 전역 필터의 적용 범위를 다시 계산, 「<클래스> → <종류> (<규칙>)」.
- **오른쪽 인스펙터**(위젯 선택 시; 없으면 빈 안내)
  - 머리: 사람 이름(+클래스 이름), 「고정됨」(툴팁 「수동으로 정했습니다」).
  - 이유 줄: 규칙 코드 + 이유 문장(사용자에게 그대로 보여 준다).
  - 「위젯 종류」(17종), 「시간 입도」(위젯에 입도가 있을 때: hour/day/month/quarter/year), 차원(축) 목록(속성 선택·삭제·추가 — 역할 unknown 제외, 아직 안 쓴 첫 속성), 지표 목록(속성 + 집계 count/sum/avg/min/max, 추가 시 첫 수치 속성 avg 또는 `*` count), 「자동 추천으로 되돌리기」, 「제거」.
  - 값을 바꾸면 되돌리기 스냅숏을 쌓고, 그 위젯을 `pinned=true`로 하고, 그 위젯만 다시 조회.
  - 되돌리기: 화면 메모리의 위젯 목록 스냅숏 스택(저장된 파일은 그대로). 「되돌렸습니다.」 / 자동 추천 복원 「자동 추천으로 되돌렸습니다.」(id·배치 유지, pinned 해제).
- **AI 패널** 「AI 로 고치기」(§4.6).
- **저장**: PUT 본문 = `{format_version:1, name:<이름>, description:"", model:{}, widgets:<현재>, global_filters:<현재>, params:{}}` → 「저장했습니다.」, 거부 시 「저장 거부: <첫 오류 path> — <reason>」. 키는 처음 정한 키를 유지(이름을 바꿔도 키는 그대로), 키가 없으면 이름의 공백을 `-`로, 이름도 없으면 `board`.
  - 원본 동작 주의: 화면 저장은 `model`을 빈 객체로, `description`을 빈 문자열로 덮는다(자동 구성이 넣은 값이 사라짐).
- **대시보드 열기**: GET → 위젯·전역 필터 복원, 위젯별 해소 판정 중 ok가 아닌 것이 있으면 「N개 위젯을 열지 못했습니다: <첫 사유>」, 모든 위젯 조회.
- **Superset 내보내기**: 저장 후 내보내기 → 대화상자 「Superset 내보내기」 / 「차트 N개가 생성됩니다.」 / 「제외된 위젯 N개」 목록 / 「닫기」.

### 4.5 전역 필터와 선택(교차 필터)
- 「+ 필터 추가」 후보: 대시보드에 올라온 클래스(프로파일이 있는 것)별로, 역할이 시간이거나 범주(고유값 2–50)인 속성. 표기 `속성 (기간|범주)`.
- 추가 시 필터 `{id:"gf<n>", kind:"time"|"category", label:<속성>, source_class, property, op:"between"|"eq", value:null, options:[]}`. 범주면 값 목록 API로 `options` 채움. 그리고 적용 범위 계산(§5.1 #9): 결과로 `hit/total 위젯` 표시, 일부가 빠지면 강조, 툴팁 「모든 위젯에 걸립니다.」/「걸리지 않는 위젯: a, b」.
- 필터가 없을 때 안내 「기간·지역 같은 필터를 추가하면 대시보드 전체에 걸립니다.」
- 기간 필터: 두 텍스트 칸(placeholder `2025-01`, `2025-12`) → 값 `[시작, 끝]`(둘 다 비면 null). 범주: 선택 상자 `(전체)` + 값들.
- 값이 바뀌거나 제거되면 모든 위젯 다시 조회. 값이 비어 있는 필터는 조회에 보내지 않는다.
- **선택**: 차트 요소(계열) 또는 표 행 클릭 → 선택 = 클릭한 행에서 그 클래스의 키 속성 값이 있으면 `{source_class, property:<키>, value, label}`, 없으면 첫 차원(행에 있는 것) 값, 행이 없으면 클릭한 이름. 「<값> 선택 — 관련 위젯에 필터를 겁니다」 후 모든 위젯 다시 조회. 필터 막대에 「선택 <라벨> <클래스.속성>」 + × 「선택을 해제했습니다.」
- 선택·필터 값·되돌리기 스택은 화면 상태다(필터 정의는 저장되지만 값도 함께 저장된다 — 저장 시점 값).

### 4.6 AI 편집 패널과 흐름
- 대상 표시: 선택 위젯 제목 또는 「대시보드 전체」. 비었을 때 안내 「'<위젯>' 위젯을 말로 고칩니다.」/「위젯을 클릭하면 그 위젯이 대상이 됩니다.」
- 입력 placeholder 「예) @지역 별로 쪼개줘 · 평균 말고 합계로」(진행 중 「기다리는 중…」), 「보내기」.
- 요청 시: 대화에 사용자 말 추가 → **현재 화면을 먼저 저장(PUT)** → 스트리밍 편집 요청. 본문 `question` = 사용자 말 + (자원이 있으면) `\n\n[사람이 고른 자원]\n- 클래스 X (모델 M) — 속성: a, b …(최대 20)` / `- 속성 C.p` / `- 위젯 <id>「이름」 (종류, 클래스)` + `\n\n[대시보드 id]\n<키>`. `widget_id` = 선택 위젯 또는 멘션한 첫 위젯.
- 이벤트 표시: `tool_start` → 「⚙ <도구 이름>」 + 인자 요약(우선 키 query, sql, class_name, dashboard_id, file_path, command 중 첫 값, 90자), `tool_result` → 「↳ <내용>」, `error` → 오류 문장, `token` → 텍스트. 진행 중 「생각 중…」.
- 결과 카드: 바꿀 것 없음(`no_patch` 또는 유효하지만 diff 없음) → 「바꿀 것 없음」 + 메모. 유효 → 「승인 대기」(적용 후 「적용됨」) + diff 목록(각 줄 `op field|widget_kind : before(취소선) → after(굵게)`, 값 60자) + 「취소」(결과 카드 지움)·「적용」. 무효 → 「거부됨」 + `path — reason` 목록. 메모(`note`)가 있으면 표시.
- 「적용」: 받은 `patch`를 그대로 `dry_run:false`로 보냄 → 서버 명세 다시 읽어 위젯 교체 → 모든 위젯 조회 → 「패치를 적용했습니다.」

### 4.7 차트 렌더링 규칙 (ECharts 수준의 표현)
- 공통: 10색 팔레트, 낮/밤 테마별 글자·축·격자·툴팁 색, 테마가 바뀌면 다시 그림. 숫자 축 표기: 1억 이상 `x.x억`, 1만 이상 `x.x만`, 정수는 천 단위 구분, 소수는 절댓값 <1이면 3자리 아니면 2자리. 값 없음 `—`.
- 지표 열 이름 = 지표 라벨 또는 속성(`*`면 `count`). 차원 열 = 위젯 차원 중 결과에 있는 것, 없으면 지표가 아닌 열.
- line/bar/bar_h: 첫 차원 = 범주축. 두 번째 차원이 있고 지표가 1개면 두 번째 차원 값별 계열, 아니면 지표별 계열. line은 부드럽게, 점은 범주 ≤40일 때만. bar_h는 축을 바꿈. 계열 >1이면 범례.
- pie: 도넛(38–68%), 라벨 `이름\n퍼센트`. scatter: 지표 2개(없으면 앞 열 2개), 남는 차원으로 계열. heatmap: 차원 2개 × 지표, 하단 가로 색 막대, 셀 ≤60이면 값 표시. treemap: 차원 순서대로 중첩 합계. sunburst: treemap과 같은 데이터를 원형으로. box_plot·word_cloud: 0.1.1은 각각 막대·가로 막대로 그린다(전용 렌더러 없음).
- 지도(geo_point/geo_path/geo_polygon): 내장 지도 두 개(한국 시도, 미국 주). 위젯 `options.map`이 있으면 그것, 아니면 점들의 평균 좌표가 들어가는 지도, 기본 한국. 점들의 범위(+18% 여백)로 확대. 점: 크기 = 지표 비례(8–26), 이름 = 키/첫 열. 경로: GeoJSON LineString(또는 Multi*·Polygon의 첫 고리) 선 + 흐름 효과. 구역: 다각형 반투명 채움.
- 결과가 `fallback:"table"`이면 표로 그림.
- 클릭: 계열 요소/빈 캔버스 클릭을 위젯 이벤트로 올림(§4.5 선택).

### 4.8 위젯 액션 창
- 「액션 N」 → 모달. 머리 「액션 — `<클래스>`」, 부제 「계획 → 승인 → 실행 → 취소(보상). 업무 시스템은 액션 실행기를 거쳐서만 호출됩니다.」, ×.
- 액션 고르기 버튼(액션이 하나면 미리 선택): 짧은 이름(설명의 ` — ` 앞이 28자 이하면 그것에서 끝의 「한다/하다」 제거, 아니면 액션 이름) + 액션 이름 + 설명 + (액션 정의에 골든 커맨드가 있으면) 「Golden Command “…”」.
- 「대상 — <클래스> 중에서」: 조건 줄(속성 선택 · 연산자 `= != > >= < <= contains` · 값 · 「−」), 「+ 조건」. 선택이 같은 클래스면 `선택 속성 = 값` 조건을 미리 넣고 「차트에서 고른 「p = v」 로 채웠습니다.」, 조건이 없으면 「조건이 없으면 모든 인스턴스가 후보이고, 정책이 대상마다 허용·거부를 정합니다.」
- 「입력」: 액션 매개변수(필수는 표시). 필수가 비었거나 조건 속성·연산자가 비면 「계획 세우기」 비활성. 값 변환: 숫자 모양은 숫자, `true/false`는 불, `contains`는 문자열.
- 「계획 세우기」(진행 중 「계획 세우는 중…」) → 계획 생성 API(`{class, action, where:[{prop,op,value}], params}`) → M2의 계획 카드 부품을 그대로 보여 줌(승인·실행·결과·취소는 그 카드가 처리) + 「다른 대상으로」(계획 버림)·「닫기」.
- 계획이 있는 동안 1.5초마다 계획·실행을 조회해, 실행 상태가 끝난 상태로 바뀌면 위젯을 모두 다시 조회하고 「액션 결과를 반영해 위젯을 다시 읽었습니다.」(보상이면 「취소(보상)를 반영해 위젯을 다시 읽었습니다.」). 닫을 때 계획을 세웠으면 다시 조회.

### 4.9 코드 앱 화면
- 머리: 「‹ 갤러리」, 앱 이름, 「코드 앱」, 상태(실행 중 「에이전트가 코드를 쓰는 중 · m:ss」(1초 갱신) / 마지막 턴 「완료 · 수정 N회」 또는 「실패 · 수정 N회」), 오류 문장, 「미리보기 새로고침」, 「앱 탭으로 열기 ↗」.
- 왼쪽 대화: 지난 턴은 요청 + 보고(이스케이프 후 `**굵게**`, `` `코드` ``만 꾸밈). 현재(또는 재생된 마지막) 턴은 이벤트를 순서대로:
  - 사용자 말, 에이전트 텍스트(연속 토큰은 줄바꿈으로 이어 붙임), 도구 줄, 오류, 사용량(「N초 · N단계」).
  - 도구 줄 아이콘·문구: Write 「＋ 파일 작성 · <파일명>」, Edit/MultiEdit 「✎ 파일 수정 · …」, Read 「◔ 읽기 · …」, Glob/Grep 「⌕ 찾기 · <패턴>」, Bash — 명령에 질의 주소와 `"cypher":"…"`가 있으면 「⟡ 질의 시험 · <Cypher>」, 스키마 주소면 「⟡ 온톨로지 구조 읽기」, 그 밖 「› 명령 · <명령 120자>」. 결과: 오류면 빨간 문장(160자), JSON `{error}`면 그 오류, `{rows}`면 「N행」.
  - 실행 중 「· · ·」.
- 아래 입력(멘션 가능, Enter 제출): placeholder 「고칠 점을 말하세요 — 예: @Shipment 지연이 3일 넘으면 빨간색으로」, 실행 중 비활성 「에이전트가 일하는 중입니다…」. 「보내기」 → 턴 시작 → 이벤트 구독.
- 오른쪽 탭: 「미리보기」(iframe `/apps/<id>/?v=<시각>`), 「파일 N」(목록: 경로 + `x.x KB`, 처음 열면 app.js 또는 첫 파일, 선택 파일 원문 표시), 주소 표시 `/apps/<id>/`.
- 미리보기 자동 새로 고침: 파일 쓰기/수정 도구 결과가 오면 0.6초 뒤(연속이면 마지막 기준), 턴이 끝나면 즉시 + 열린 파일 다시 읽기.
- 「앱 탭으로 열기」: 셸의 탭 열기 기능으로 `{kind:'app', app:<id>, title:<이름>}`, 셸 기능이 없으면 새 창 `/apps/<id>/`.

### 4.10 앱 탭 (셸)
- 탭 종류 `app`: id 형식 소문자·숫자·하이픈 4–64자, URL `http://127.0.0.1:<web>/apps/<id>/`, 제목 = 앱 이름(페이지 제목이 바뀌면 따라감). **셸 브리지(렌더러 API)를 주지 않는다.** 격리·샌드박스.
- 탭 안의 새 창 요청 중 `/apps/` 주소는 앱 탭으로, 그 밖 규칙은 A1과 같다.
- 홈 최근 항목: 코드 앱 → 종류 「코드 앱」, 정보 「에이전트 작업 중」/「수정 N회」, 누르면 앱 탭. 대시보드 → 종류 「대시보드」, 정보 칸(모델 이름; 원본은 목록 응답에 없어 비어 있음), 누르면 대시보드 화면의 갤러리.

### 4.11 SDK 확인 창(코드 앱 `act()`)
- 앱 문서에 덮개+카드로 그린다(모든 앱에서 같은 모양). 머리: 제목(옵션 `title` → 액션 설명의 ` — ` 앞 → 액션 이름), `<클래스>.<액션>`, ×.
- 계획 전: 설명, 골든 커맨드(「Golden Command “…”」), 범위(「대상 N건: …」/「조건: p op v · …」/「조건 없음 — 정책이 대상마다 허용·거부를 정합니다」), 입력(매개변수; 필수 `*`; 앱이 준 값 미리 채움), 「닫기」·「계획 세우기」(「계획 세우는 중…」). 액션을 못 찾으면 「액션 <클래스>.<액션> 이 없거나 쓸 권한이 없습니다.」
- 계획 후: 「실행 계획 · <상태> · 허용 N건 · 거부 N건[ · 사람 승인 필요]」, 표(구분 허용/거부 · 대상 키 · 사유; 없으면 「대상이 없습니다.」).
  - 승인 대기면 메모 입력(「승인 메모 (선택)」)+「승인」; 실행 가능(실행 기록 없음, 허용 ≥1, 상태 approved 또는 승인 불필요한 planned)이면 「실행 (N건)」; 실행이 성공/부분 성공이고 아직 취소 안 했으면 사유 입력(「취소 사유 (선택)」)+「취소 (되돌리기)」; 「닫기」.
  - 실행 결과: 「실행 결과 · <상태>[ · 취소함 (“사유”)]」, 표(대상 · 결과 · 단계별 이름+✓/✗/·, 보상 성공 ↺).
  - 실행·보상 중 1.2초마다 실행 조회, 끝나면 계획도 다시 조회.
- 상태 문구: planned 계획됨, awaiting_approval 승인 대기, approved 승인됨, executed 실행됨, expired 만료, rejected 거부, running 실행 중, succeeded 성공, partial 일부 성공, failed 실패, compensated 취소됨(되돌림), compensating 되돌리는 중, skipped 건너뜀.
- 덮개 클릭·닫기 → 창 제거, `act()`가 `{executed:<실행 기록 있음>, cancelled:<취소함>, plan, run}`로 끝남.

---

## 5. API 명세

### 5.1 대시보드 API (분석 백엔드, prefix `/api/board`, JSON, 인증 없음)
오류 형식: FastAPI 관례 `{"detail": <문자열 또는 객체>}`. MCP 오류 문구는 가공하지 않고 그대로 전달한다.

| # | 메서드 경로 | 요청 | 응답 / 오류 |
|---|---|---|---|
| 1 | GET `/health` | — | `{transport, target, mcp:"ok"\|"unreachable", datasource_expansion:bool, tools:[이름], error?, row_budget:{cypher:int\|null, sql:null}, cached_profiles:int}` |
| 2 | GET `/models` | — | `{models, counts, note}` / 503 |
| 3 | GET `/classes?schema_name=` | — | `{models, classes, counts, note}` (모델 필터 선택) / 503 |
| 4 | GET `/classes/{c}/profile?schema_name=&refresh=false` | — | 객체 프로파일(§6.2, 별칭 `class`, `schema` 사용) / 409 `{detail:{error, ambiguous:true, schema_names}}` / 404 / 503 |
| 5 | GET `/classes/{c}/related?schema_name=` | — | `{related:[DatasourceRef]}` / 404 |
| 6 | POST `/classes/{c}/recommend?schema_name=&refresh=false` | — | `{primary:WidgetSpec, secondary:[WidgetSpec], profile}` 또는 `{guard:"G2"\|"G5"\|"G8", reason, profile}` / 409 / 404 / 503 |
| 7 | POST `/widgets/query` | `{widget:WidgetSpec, params:{}, global_filters:[GlobalFilter], selection:Selection\|null}` | 항상 200 QueryOutcome(§6.5). 오류는 `error` 필드 |
| 8 | GET `/classes/{c}/values?property=&schema_name=&limit=50` | — | `{class_name, property, type, role, values:[], truncated:(개수≥limit), distinct_count}` / 404 「'<c>' 에 '<p>' 속성이 없습니다.」 / 503 |
| 9 | POST `/filters/applicability` | `{source_class, property, class_names:[]}` | `{source:"C.p", applies_to:{클래스:{how, property, via?}}, not_applicable:[클래스]}` |
| 10 | GET `/dashboards` | — | `{dashboards:[{id(저장 키), name, widgets(개수), updated_at}]}` (키 이름순) |
| 11 | GET `/dashboards/{id}` | — | `{dashboard:DashboardSpec, resolution:[{widget_id, class_name, status, reason?, schema_names?}]}` / 404 「대시보드 '<id>' 가 없습니다.」 |
| 12 | PUT `/dashboards/{id}` | DashboardSpec | `{dashboard}`(created_at·updated_at 채움) / 422 `{detail:{errors:[{path, reason}]}}` |
| 13 | DELETE `/dashboards/{id}` | — | `{deleted:true\|false}` |
| 14 | POST `/dashboards/{id}/patch` | `{patch:[PatchOp], dry_run:true}` | `{valid, diff, errors, applied}` (dry_run이거나 무효면 저장 안 함) |
| 15 | POST `/dashboards/{id}/ask` | `{question, widget_id:""}` | 편집 결과(§6.6) / 404 / 503 |
| 16 | POST `/dashboards/{id}/ask/stream` | 같음 | SSE(`text/event-stream`, `Cache-Control: no-cache`, `X-Accel-Buffering: no`), 각 줄 `data: {"kind":…, …}`: `token{text}`, `tool_start{tool_call_id?, name, args}`, `tool_result{tool_call_id?, content}`, `error{message}`, 마지막 `result{…§6.6}`. 대시보드 없음·LLM 불가는 `error` 이벤트로 |
| 17 | POST `/compose` | `{schema_name:"", dashboard_id:"", use_agent:true}` | SSE: 클래스마다 `tool_start{name:"widget_recommend", args:{class_name}}` + `tool_result{content:"C → kind (rule)"\|"C: 건너뜀 — 사유"\|"C: 실패 — …"}`, 에이전트 선택 중 이벤트(token/tool_*), 대체 시 `token{text}`, 마지막 `result`: 성공 `{created:true, dashboard_id(저장 키), dashboard, skipped:[{class_name, guard?, reason}], note}` / 위젯 없음 `{created:false, skipped, reason}` / 검증 실패 `{created:false, errors}`; 예외 `error{message(300자)}` |
| 18 | POST `/dashboards/{id}/export/superset` | — | `{charts:[{slice_name, viz_type, datasource_id:null, datasource_type:"table", source:{datasource, schema, table}, params:"<form_data JSON 문자열>"}], excluded:[{widget_id, class_name?, reason:"materialized_not_exportable"\|"no_superset_equivalent", detail?}]}` / 404 |
| 19 | POST `/cache/clear` | — | `{cleared:true}` (프로파일 캐시·확장 여부 캐시) |

### 5.2 코드 앱 API (데스크톱 셸, prefix `/codeapps/api`, JSON)
오류 형식 `{"error": "<한국어 문장>"}`.

| 메서드 경로 | 요청 | 응답 / 오류 |
|---|---|---|
| POST `/query` | `{cypher, params:{}}` (본문 최대 1MB) | 200 `{columns:[], rows:[{…}]}`(최대 5000행) / 400 「cypher 가 없습니다.」 / 403 「읽기 전용입니다 — CREATE·MERGE·SET·DELETE 같은 쓰기 절은 쓸 수 없습니다.」 / 400 `{error:<엔진 메시지, 앞의 접두 제거, 600자>}` |
| GET `/schema` | — | `{graph, classes:[{name, count, properties:[], example:{}\|null}], relationships:[{from, type, to, description}]}` |
| GET `/apps` | — | `{apps:[{id, name, updated_at, turns, running, ok:bool\|null}]}` (updated_at 내림차순) |
| POST `/apps` | `{name, text, resources}` | `{id:"app-<8hex>", name}` |
| GET `/apps/<id>` | — | `{id, name, prompt, resources, created_at, updated_at, session_id, turns:[{text, resources, ok, report, started_at, finished_at}], running, files:[{path, size}], url:"/apps/<id>/"}` / 404 「그 앱이 없습니다.」 |
| DELETE `/apps/<id>` | — | `{deleted:true}` (실행 중 턴 종료 후 폴더 삭제) |
| POST `/apps/<id>/turns` | `{text, resources}` | `{started:true}` / 400 「무엇을 만들지 적어 주세요.」 / 409 「에이전트가 아직 일하는 중입니다.」 |
| GET `/apps/<id>/events?from=<n>` | — | SSE(`data: <이벤트 JSON>`): 진행 중 턴의 n번째부터 + 이후 실시간, 15초마다 `: ping`, `done` 후 종료. 메모리에 턴이 없으면 마지막 저장 턴을 `user` + 저장 이벤트로 재생하고 `{kind:"done", ok, replay:true}` 후 종료(턴이 없으면 `ok:true`) |
| GET `/apps/<id>/file?path=` | — | `{path, text(최대 400000자)}` / 404 「그 파일이 없습니다.」(폴더 밖·숨김·없음) |
| `/act/*` | §5.3 | |
| 그 밖 | | 404 `{error:"not found"}`; 처리 중 예외 500 `{error}` |

이벤트(§6.8) — 턴 이벤트 종류: `user{text, resources}`, `token{text, agent?}`, `tool_start{tool_call_id, name, args}`, `tool_result{tool_call_id, name, content(600자), is_error}`, `error{message}`, `usage{duration_ms, turns, cost_usd}`, `final{text, exit_code}`, `done{ok, replay?}`.

정적 제공
- GET `/apps/_runtime/<파일>` — SDK·스타일·Vue·ECharts. `Cache-Control: max-age=3600`.
- GET `/apps/<id>` → 302 `/apps/<id>/`. GET `/apps/<id>/` → index.html. GET `/apps/<id>/<경로>` → 앱 폴더 파일(`Cache-Control: no-store`). 숨김(메타 파일, 규칙 파일 2개, 점으로 시작하는 파일)·폴더 밖·없는 파일·디렉터리 → 404 「없는 파일입니다.」, 없는 앱 → 404 「그 앱이 없습니다.」. MIME: html/js/css(UTF-8), json, svg, png, 그 외 octet-stream.

### 5.3 액션 경로
- 대시보드 화면(직접): `GET /api/act/actions` (응답 = 액션 배열, 항목 `{class, action, description, key_property, parameters:{properties:{이름:{type, description}}, required:[]}, …}`), `GET /api/schema/classes/{c}/actions`(정의 목록 — `actions[{name, golden_command, …}]`), `POST /api/act/plans {class, action, where, params}`, `GET /api/act/plans/{id}`, approve `{note}`, execute, `GET /api/act/runs/{id}`, compensate `{reason}` — 상세 계약은 M2 설계.
- 코드 앱(셸 프록시 `/codeapps/api/act/…` → 백엔드 `/api/act/…`):

| 앱 경로 | 백엔드 | 사람 확인 필요 |
|---|---|---|
| GET `/act/health` | `/api/act/health` | |
| GET `/act/actions?class=` | 셸이 백엔드 액션 목록 + 클래스별 정의의 `golden_command`를 붙여(`golden_command` 없으면 `""`) class로 거름 | |
| POST `/act/plans` | `/api/act/plans` | |
| POST `/act/plans/by-ids` | `/api/act/plans/by-ids` (`{class, action, ids, params}`) | |
| GET `/act/plans/<id>` | `/api/act/plans/<id>` | |
| POST `/act/plans/<id>/approve` | `/api/act/plans/<id>/approve` | 예 |
| POST `/act/plans/<id>/execute` | `/api/act/plans/<id>/execute` | 예 |
| GET `/act/runs/<id>` | `/api/act/runs/<id>` | |
| POST `/act/runs/<id>/compensate` | `/api/act/runs/<id>/compensate` | 예 |
- id 형식 `[\w-]+`. 원본의 "사람 확인" = 요청에 브라우저가 붙이는 `Sec-Fetch-Mode` 헤더가 있는지. 없으면 403 「승인·실행·취소는 앱 화면에서 사람이 눌러야 합니다.」. 백엔드 포트 없음 503 「액션 실행기에 연결되지 않았습니다.」, 연결 실패 502 「액션 실행기에 닿지 못했습니다: …」, 그 밖 404 「없는 액션 경로입니다.」. 백엔드 응답은 상태 코드·본문 그대로 전달.
- 액션 목록을 못 얻으면(백엔드 없음·오류) 빈 배열.

### 5.4 코드 앱 SDK (`/apps/_runtime/og.js`, ES 모듈) — 외부 계약
| 함수 | 동작 |
|---|---|
| `await query(cypher, params = {})` | `POST /codeapps/api/query`. 성공 → `rows` 배열. 실패 → `Error(서버 error 문장 또는 "HTTP <n>")` |
| `await schema()` | `GET /codeapps/api/schema` 결과. 실패 → `Error("HTTP <n>")` |
| `theme()` | 저장소 키 `os-theme`(Studio와 같은 오리진에서 공유)가 `light`/`dark`면 그것, 아니면 시스템 설정 |
| `onTheme(fn)` | 테마가 바뀌면 `fn(theme)`. 해제 함수 반환. 다른 탭의 저장소 변경·시스템 테마 변경을 감지하고 `<html data-theme>`을 맞춘다(모듈 로드 시 1회 적용) |
| `color(name)` | CSS 변수 `--og-<name>`의 계산값 |
| `await actions(className?)` | 액션 목록(클래스로 거름). 오류면 `[]` |
| `await act(opts)` | §4.11 창. `opts = {class, action, ids?:[키 값], where?:[{prop, op, value}], params?:{}, title?}`. `ids`가 있으면 by-ids 계획, 아니면 where 계획(없으면 `[]`). 반환 `{executed, cancelled, plan, run}` |

- 스타일 `/apps/_runtime/og.css`: 낮/밤 토큰 `--og-bg, --og-panel, --og-raised, --og-line, --og-line-2, --og-fg, --og-dim, --og-mute, --og-accent, --og-on-accent, --og-blue, --og-warn, --og-danger, --og-ok, --og-purple, --og-soft, --og-shadow`(기본=밤, `[data-theme=light]`=낮) + SDK 창 스타일.
- `/apps/_runtime/vue.js`(Vue 3, 템플릿 컴파일러 포함 ES 모듈 빌드), `/apps/_runtime/echarts.min.js`(전역 `echarts`).
- `query` 결과 값: 정수는 숫자(안전 범위 밖은 문자열), 노드는 속성 객체(시스템 속성 `_id,_type,_source_id,_parent_source_id,created_at,updated_at,embedding` 제외) + `_labels`(`_`로 시작하는 라벨 제외) + `_id`, 관계는 속성 + `_type`, `_id`, 경로는 `[{start, rel, end}]`, 시간·공간 값은 문자열, 열 이름 = `RETURN … AS` 이름.

---

## 6. 데이터 모델

### 6.1 대시보드 명세 (DashboardSpec, 파일 하나 = 대시보드 하나)
```
{
  format_version: 1,
  name: 문자열,               // 표시 이름
  description: 문자열,        // 자동 구성의 에이전트 메모
  model: {schema_id, schema_name} | {},
  widgets: [WidgetSpec],
  global_filters: [GlobalFilter],
  params: {키: 값},           // 위젯 필터의 param_key 값
  created_at, updated_at: ISO8601(UTC, 초)
}
WidgetSpec {
  id: 문자열(엔진은 "w_" + 16진 8자),
  schema_name: 문자열|null, class_name: 문자열,
  widget_kind: 17종 중 하나(기본 table),
  rule: 규칙 코드(기본 "O10"), reason: 이유 문장,
  pinned: bool,                          // 사람이 정함 → 자동 추천이 덮지 않음
  dimensions: [속성 이름], measures: [{property(또는 "*"), agg: count|sum|avg|min|max, label|null}],
  filters: [{property, op: eq|ne|gt|gte|lt|lte|contains|in, param_key}],   // 값이 아니라 키
  time_grain: hour|day|week|month|quarter|year|null, top_n: int|null,
  layout: {x, y, w(기본 6), h(기본 2)}, title: 문자열, options: {}        // options.map = "korea"|"usa"
}
GlobalFilter { id, kind: time|category, label, source_class, property, op: eq|gte|lte|between|in|contains, value, options: [] }
Selection { source_class, property, value, label }
```
- 위젯 종류(닫힌 목록): `kpi, kpi_group, table, bar, bar_h, pie, timeseries_line, box_plot, treemap, sunburst, word_cloud, heatmap, scatter, pivot_table, geo_point, geo_path, geo_polygon`.
- 필드 대입 시 타입 검증(잘못된 값 → 검증 오류로 사유 전달).

### 6.2 객체 프로파일 (조회용, 저장 안 함)
```
{ schema_name, class_name, description, binding_kind: materialized|virtual,
  instance_count, data_row_count, native_key: [], source: {datasource, schema, table}|null,
  datasource_refs: [{from_class, class, datasource, schema, table, via_relationship, join_on}],
  properties: [{ name, column, role: identifier|temporal|numeric|categorical|unknown,
                 type: boolean|integer|float|date|string|geojson|null,
                 type_source: column_map|value_inference|none, distinct_count, null_ratio,
                 min, max, avg_length, geo_shape: point|linestring|polygon|null,
                 coord_axis: lat|lng|null, stored_as_string, is_reference }],
  sampled_rows, cache_key, warnings: [] }
```

### 6.3 저장 검증 규칙 (저장·자동 구성·패치 공통)
- 어느 깊이든 키 이름이 `password, passwd, secret, token, host, port, user, username`(대소문자 무시)이면 거부: 「'<키>' 는 자격증명 계열 키라 저장할 수 없습니다.」
- 문자열 값에 단어 `SELECT|MATCH|MERGE|INSERT|UPDATE|DELETE` + 공백이 있으면 거부: 「질의문은 저장하지 않습니다. 조회 시점에 만듭니다.」(대소문자 무시 — 제목·이유 문장도 해당)
- 위젯 종류가 목록 밖: 「알 수 없는 위젯 종류입니다: …」, 위젯 id 중복: 「위젯 id 가 중복입니다: …」, 위젯 필터의 `param_key`가 `params`에 없음: 「'<키>' 가 params 에 없습니다.」
- 오류 경로 형식: `$.widgets[0].widget_kind`, `$.params.x.password` 식.
- 저장 키: 대시보드 id에서 영문·숫자·`_`·한글·`-` 외 문자를 `_`로, 80자. 비면 「대시보드 id 가 비어 있습니다.」 목록의 `id`는 이 키.

### 6.4 패치 (PatchOp)
- `{op:"set", widget_id, field, value}` — 위젯 필드 대입. `field`는 WidgetSpec 필드만(아니면 「없는 필드입니다: …」).
- `{op:"add"|"append", widget_id, field, value}` — 목록 필드에 값(또는 값 목록) 덧붙임(목록이 아니면 「'<f>' 는 목록이 아니라 값을 더할 수 없습니다.」).
- `{op:"add"|"append", value:WidgetSpec}` (field 없음) — 위젯 추가(형식 오류 「위젯 형식이 아닙니다: …」).
- `{op:"remove", widget_id}` — 위젯 삭제.
- 없는 위젯 「그 id 의 위젯이 없습니다.」. `op` 생략 = set.
- set/add로 바뀐 위젯은 `pinned=true`.
- 끝에 참조 무결성: 발행 온톨로지에 없는 클래스 「'<C>' 이 발행된 온톨로지에 없습니다.」, 속성 목록이 있는 클래스에서 차원·지표 속성이 없으면 「'<C>' 에 '<p>' 속성이 없습니다.」, 그리고 §6.3 검증.
- 결과 `{valid, diff:[{op:"set", widget_id, field, before, after} | {op:"add", widget_id, widget_kind} | {op:"remove", widget_id}], errors:[{path, reason}], draft}` (draft는 내부용, 응답에서 뺌). 오류가 하나라도 있으면 아무것도 바꾸지 않는다.

### 6.5 조회 결과 (QueryOutcome, 저장 안 함)
`{columns:[], rows:[{}], returned_count, total_count(별도 count 질의의 참값 또는 null), truncated, aggregation_promoted:{dropped_series?|from,to}|null, badge:"<total>건 중 <returned>건"|"", fallback:"table"|null, context:[{kind:"filter"|"selection", id, label, source:"C.p", applied, how?, property?, via?, reason?}], error|null}`

### 6.6 AI 편집 결과
`{valid, applied:false, diff, errors, patch:[최종 패치(후처리 포함)], note, question, no_patch?:true}` — 응답이 JSON이 아니면 `{valid:false, applied:false, diff:[], errors:[], patch:[], no_patch:true, note:<응답 앞 600자 또는 "에이전트가 답하지 않았습니다.">}`, patch가 목록이 아니면 errors `[{path:"$.patch", reason:"patch 가 목록이 아닙니다."}]`.

### 6.7 코드 앱 폴더
```
<사용자 데이터 폴더>/codeapps/<id>/      id = "app-" + 16진 8자
  index.html, app.js, style.css (+ 에이전트가 만든 모듈 등)
  CLAUDE.md, AGENTS.md        // 같은 내용의 에이전트 규칙(§8.5), 앱 제공 시 숨김
  .app.json                    // 메타
.app.json = { id, name, prompt(첫 요청), resources, created_at, updated_at,
              session_id(UUID, 에이전트 세션 이어받기용), 
              turns: [{ text, resources, started_at, finished_at, ok, report(final 텍스트), events(빈 토큰 제외, 마지막 400개) }] }
```
- 이름: 입력 이름 → 없으면 문장에서 `@` 제거 28자 → 「새 앱」.
- 템플릿: index.html(문서 언어 ko, viewport, 제목 「새 앱」, og.css → style.css → echarts 순 로드, `<div id="app">`, `app.js` 모듈), app.js(자리표시 화면 「에이전트가 앱을 만들고 있습니다…」), style.css(자리표시 가운데 정렬).
- 규칙 파일의 자리표시 두 개를 이 설치의 질의 주소(`http://127.0.0.1:<web>/codeapps/api/query`)와 액션 목록 주소(`…/codeapps/api/act/actions`)로 바꿔 저장.
- 목록에는 메타 파일이 있고 id 형식이 맞는 폴더만 나온다.

### 6.8 실행 상태 (메모리)
- 앱마다 진행 중 턴 하나: `{text, resources, started_at, events[], done, listeners, child}`. 같은 앱에 두 번째 턴 요청은 409. 다른 앱끼리는 동시에 실행 가능(원본은 전역 제한 없음).
- 턴이 끝나면 메타에 기록 후 `done` 이벤트. 앱 종료 시 실행 중인 턴 프로세스를 모두 종료(메타에 기록되지 않음 — 확인 대상).

---

## 7. 대시보드 엔진 규칙 (결과를 좌우하는 결정적 부분)

### 7.1 발행 온톨로지 지도
- 검색 MCP 서버의 리소스 `graph://schema`를 읽는다: `models[{schema_id, name, description, intent, golden_questions, golden_commands, format_version, published_at}]`, `classes[{schema_name, class_name, description, binding_kind, property_names, native_key, source?, orphaned?…}]`, `relationships[{schema_name, name, from_class, to_class, description, properties[]}]`, `counts`, `note?`. 컬럼·SQL은 없다.
- 실데이터 확장 여부 = MCP 도구 목록에 `ontology_get_datasource_schema`가 있는가(1회 캐시).

### 7.2 프로파일링
- 클래스 찾기: 같은 이름이 여러 모델에 있으면(모델을 안 정했을 때) 「'<C>' 이 여러 그룹에 있습니다: a, b」(409, 사용자가 고르게). 없으면 「'<C>' 은 발행된 온톨로지에 없습니다.」
- 캐시: (모델 `schema_id@published_at`, 클래스) 단위. 시간 만료 없음. 재발행 시 키가 바뀌어 무효. `refresh=true`로 다시. 메모리.
- 공통: 그래프 인스턴스 수 `MATCH (n:_Entity:<C>) RETURN count(n) AS c`(가상 클래스는 항상 0). 노드 1건을 받아 그 결과의 데이터소스 참조(`_datasource_refs`)를 연관 정보로 둔다.
- **가상 클래스**: 컬럼 선언(도구 `ontology_get_datasource_schema(class_name, schema_name)`)의 타입을 쓴다(그 5종 밖이면 string, 참조 컬럼은 `is_reference`). 표본 `SELECT <컬럼들> FROM <schema.table>`(limit 200)으로 통계, `SELECT COUNT(*) AS c FROM …`(limit 1)로 데이터 행 수. 값이 GeoJSON/WKT면 geojson으로 바꿈. 동명 모호 → 409.
- **적재 클래스**: `MATCH (n:_Entity:<C>) RETURN n LIMIT <표본 수, 기본 50>`으로 값을 보고 타입 추론. 속성 이름 = 지도 목록 ∪ 표본 키, 시스템 속성(적재 시각 등)과 `_` 접두 제외. 데이터 행 수 = 인스턴스 수. 수로 읽히는데 문자열로 저장된 속성은 `stored_as_string`.
- 타입 추론(모든 비어 있지 않은 값이 만족해야 함, 위에서부터): 모두 같은 형상의 GeoJSON/WKT → geojson / 모두 불 → boolean / 모두 숫자로 읽히는 문자열(하나라도 앞자리 0이면 제외; 소수점·지수 있으면 float) / 모두 정수 → integer / 모두 수 → float / 모두 날짜 객체 또는 `YYYY-MM-DD[ T]HH:MM[:SS]` 문자열 → date / 그 외 string.
- 통계: null 비율, 고유값 수, 수의 min/max, 문자열 평균 길이.
- 역할(첫 매치): geojson → unknown; date → temporal(키에 있어도); 키 컬럼·참조·이름 끝 `_id/_no/_code/_key` → identifier; 수 → numeric; 불·문자 → categorical; 그 외 unknown.
- 좌표: 수 속성 중 이름이 (`lat|latitude|위도` 단어)이고 값 범위가 −90~90 → 위도, (`lng|lon|long|longitude|경도`)이고 −180~180 → 경도.

### 7.3 가드 (위젯을 만들지 않음)
| 코드 | 조건 | 문구 |
|---|---|---|
| G8 | 가상 클래스 + 실데이터 확장 꺼짐 | 「데이터소스 확장이 꺼져 있어 이 클래스의 데이터를 읽을 수 없습니다 (MCP_ALLOW_DATASOURCE_EXPANSION=false).」 |
| G2 | 데이터 행 수 = 0 | 「이 클래스에는 아직 데이터가 없습니다.」 |
| G5 | 속성 > 30 | 「속성이 N개로 너무 많습니다.」 |

### 7.4 위젯 추천 규칙표
정의: k(속성) = 고유값 수(모르면 무한대). **범주 후보** = categorical 중 (평균 길이 >40인 긴 텍스트 제외) k≥2, 그리고 (표본 행 ≥5이면 k < 행×0.9), k 오름차순. **지표 묶음** = numeric 중 첫 지표 크기(|min|,|max| 중 큰 값)의 100배 안쪽만, 최대 3개. **기본 지표** = 첫 numeric의 avg, 없으면 `*` count. **관측 시간축** = 키에 포함된 temporal, 없으면 k≥5인 첫 temporal.

위에서부터 모두 검사해 맞는 것을 모은다. 첫째 = 주 위젯, 나머지 = 보조 위젯. 하나도 없으면 O10.
| 순서 | 규칙 | 조건 | 결과 |
|---|---|---|---|
| 1 | O5 | geojson linestring 속성 | geo_path, 차원 [그 속성], 기본 지표 |
| 2 | O6 | geojson polygon 속성 | geo_polygon, 차원 [그 속성], 기본 지표 |
| 3 | O4 | 위도·경도 속성 둘 다 | geo_point, 차원 [위도, 경도], 기본 지표 |
| 4 | O1 | 관측 시간축 + numeric ≥1 + 데이터 행 ≥3 | timeseries_line, 차원 [시간축(+첫 범주 후보, k≤8이면)], 지표 = 지표 묶음 avg, 입도 day |
| 5 | O2 | 범주 후보 ≥1 + numeric 정확히 1 + 첫 범주 k≤25 + 수치 k ≥ 4×범주 k | box_plot, 차원 [범주], 지표 avg |
| 6 | O3 | 범주 후보 ≥2이고 (k가 엄격히 증가하고 마지막이 유한 또는 자기참조 관계) + 앞 4개 k의 곱 ≤400 | treemap, 차원 = 앞 최대 4개, 기본 지표 |
| 7 | O7 | 긴 텍스트 중 평균 길이 최대인 것의 k ≥ 행×0.6 | word_cloud, 차원 [그 속성], `*` count |
| 8 | O8 | k≤15인 범주 후보 ≥2 + numeric ≥1 | heatmap, 차원 [앞 둘], 첫 numeric avg |
| 9 | O9 | 데이터 행 = 1 + numeric 1–6 + 범주 후보·temporal 없음 | numeric 1개면 kpi, 아니면 kpi_group, 지표 = 모든 numeric avg |
| 10 | R7/R6 | 범주 후보·numeric 있음 + 첫 범주 2≤k≤25 | 지표 묶음이 1개 + k≤7 + 첫 numeric이 비율성(이름에 ratio/rate/pct/percent/비율/비중/점유, 또는 min≥0이고 이름에 cnt/count/건수/수량) + min≥0 → pie(R7); 아니면 k>12 bar_h, 그 외 bar (R6). 지표 = 지표 묶음 avg |
| 11 | R11/R10 | numeric ≥2 + 데이터 행 ≥10 | scatter, 첫 범주 k≤8이면 그 범주로 색(R11) 아니면 R10, 지표 = 앞 두 numeric avg |
| 폴백 | O10 | — | table, 차원 = 속성 앞 8개, 지표 없음 |
- 위젯 id 새로 생성, 제목 = 클래스 이름, layout w6 h2.
- 이유 문장(사용자에게 보임, 원본 표현 예): O1 「'<t>' 이 키의 일부라 관측 축입니다.」 또는 「'<t>' 이 서로 다른 시점이 N개라 추이가 그려집니다.」 + 「 수치 N개의 추이를 봅니다.」 + 「 '<s>' 별로 나눕니다.」; R6 「'<c>'(N종) 별로 '<m>' 를 막대로 비교합니다.」(가로면 「라벨이 많아 가로 막대로 봅니다」); O10 「어느 규칙에도 맞지 않아 표로 봅니다. 억지로 차트를 그리지 않습니다.」 등. 구현은 규칙마다 이유 문장을 내면 된다(문구 일치는 비교 대상 아님, 형태만).

### 7.5 질의 생성
- 식별자(클래스·속성): `^[A-Za-z_가-힣][A-Za-z0-9_가-힣]*$`이 아니면 질의를 만들지 않고 「식별자로 쓸 수 없는 이름입니다: '…'」.
- **원시 위젯**(집계 안 함): table, scatter, geo_point, geo_path, geo_polygon, 그리고 차원·지표가 모두 없는 위젯. 열 = 키 + 차원 + 지표 속성(중복·없는 속성 제외, 최대 14; 아무것도 없으면 속성 앞 12개).
- **적재 클래스 → Cypher**: `MATCH (n:_Entity:<C>) [WHERE …]` 다음
  - 원시: `RETURN n.<p> AS <p>, …`
  - 집계: `WITH <차원식> AS <d>, …, <집계식> AS <라벨> RETURN <d>, …, <라벨> ORDER BY <첫 차원>` (차원 없으면 `RETURN <집계>`)
  - 첫 차원이 temporal이고 입도가 있으면 문자열 앞자리 자르기(year 4, month 7, day 10, hour 13자; week·quarter는 자르지 않음).
  - 집계식: count(`*`면 `count(*)`), sum/avg/min/max. 문자열로 저장된 수에 sum/avg/min/max면 실수 변환을 감쌈. 라벨 = `label` 또는 속성(`*`면 `count`).
  - 필터: `params`에 값이 있는 것만. 연산자 `= <> > >= < <=`, `in`, `contains`(양쪽 소문자 문자열 포함). 값은 **항상 매개변수**(`$키`, 키의 비단어 문자는 `_`).
- **가상 클래스 → SQL**(컬럼명 사용, ASCII가 아닌 식별자는 큰따옴표): `SELECT <차원식> AS <d>, <집계> AS <라벨> FROM <schema.table> [WHERE …] GROUP BY <차원식> ORDER BY <첫 차원식>`, 원시는 `SELECT <컬럼들> FROM …`. LIMIT은 쓰지 않는다(도구 인자). 시간 자르기 `SUBSTRING(CAST(x AS CHAR(32)), 1, k)`(PostgreSQL·MySQL 모두 되는 형태). 필터 값은 SQL 도구가 매개변수를 받지 않으므로 타입별로 그려 넣는다: 불 → TRUE/FALSE, 수 → 그대로, 그 외 → `'문자열'`, 단 문자열에 `' " \` ; \\`, `--`, `/*`, `*/`, 제어 문자가 있으면 **그 필터를 빼고** 실행(원본 동작; 개선 검토 §11). `contains` → `LIKE '…%'`(앞 와일드카드 없음 — 원본 동작).
- 실행: 가상 → 도구 `ontology_query_datasource_sql(sql, limit=500)`(총계 = 응답 `row_count`, 잘림 = `truncated_for_agent`); 적재 → 도구 `ontology_graph_cypher(query, params=<JSON 문자열>)`(잘림 = `truncated`) + 그룹 수 count 질의(`MATCH … WITH DISTINCT <차원식> RETURN count(*) AS c`, 차원 없으면 클래스 count)로 총계.
- **상한 대응**: 잘렸으면 최대 2회 축소 후 재실행 — (입도가 있고 시간 아닌 차원이 있으면) 마지막 계열 차원을 버림 → 아니면 입도를 한 칸 올림(day→month→year, hour→day; week/quarter 건너뜀). 기록 `aggregation_promoted`. 끝까지 잘린 시계열은 `fallback:"table"`.
- **값 정규화**: 집계 열은 count → 정수, 그 외 → 실수. 다른 열은 프로파일 타입으로(문자열 수 → 수, `true/t/y/yes/1` → 참 등). 재집계는 하지 않는다.
- 행 예산: health에서 `MATCH (n:_Entity) WITH n LIMIT 5000 RETURN id(n) AS i`의 반환 행 수를 1회 재서 `row_budget.cypher`로 알린다.

### 7.6 전역 필터·선택 연결 (한 홉)
- 연결 재료: 발행 관계의 속성 목록 중 이름이 `join`인 항목의 설명 `"a = b"` → (from_class.a = to_class.b), 양방향.
- 출처 `S.p`를 대상 클래스 T에 거는 방법(첫 매치): S=T이고 T에 p 있음 → `same_class`; S≠T이고 T에 같은 이름 p 있음 → `same_name`; S→T 홉 중 from 속성이 p이고 T에 to 속성이 있음 → `join`(via 관계 이름). 없으면 걸지 않고 사유 「'<T>' 에 연결할 속성이 없습니다.」
- 위젯 조회 시 값이 있는 전역 필터 + 선택을 추가 필터(`param_key` = `__ctx_<n>`, between은 `_a`/`_b`로 gte·lte 둘)로 덧붙이고, 결과 `context`에 걸림/안 걸림을 담는다.
- 적용 범위 API는 지도의 클래스별 속성 이름 목록으로 같은 판정을 한다.

### 7.7 열 때 해소 판정
위젯마다(모델 이름이 있으면 그 모델로 좁힘): 후보 없음 `missing_class`, 2개 이상 `ambiguous_class`(+schema_names), 가상인데 확장 꺼짐 `expansion_disabled`, 차원·지표 속성이 지도에 없음 `missing_property`(「속성이 없습니다: a, b」), 그 외 `ok`. 깨진 위젯이 있어도 연다.

---

## 8. 에이전트 부분 (구조·계약)

### 8.1 자연어 편집 (대시보드)
- 입력: 시스템 = 편집 스킬 본문, 사용자 = 라벨 블록
  `[사용자 요청]` (프런트가 붙인 `[사람이 고른 자원]`, `[대시보드 id]` 포함) / `[대시보드]` JSON(name, widgets[id, class_name, widget_kind, rule, dimensions, measures[{property, agg}], time_grain, pinned, title, selected?], params 키 목록, global_filters) / `[선택된 위젯]` id 또는 「(없음 — 대시보드 전체가 대상입니다)」 / `[사용 가능한 클래스와 속성]` JSON(대시보드 위젯 클래스는 속성별 name·role·type·distinct_count, 나머지 지도 클래스는 property_names; 6000자에서 자름) / `[응답 형식]`.
- 출력 계약: `{"patch":[PatchOp…], "note":"한 문장 설명"}` (예: 값 바꾸기 `{"op":"set","widget_id":"w1","field":"time_grain","value":"month"}`, 목록에 더하기 `{"op":"add","widget_id":"w1","field":"dimensions","value":"x"}`, 위젯 더하기 `{"op":"add","value":{"id":"w9","class_name":"C"}}`, 지우기 `{"op":"remove","widget_id":"w1"}`; measures는 `[{"property","agg"}]`). 응답에서 첫 번째로 **괄호 균형이 맞고 파싱되는** JSON 객체를 찾는다(코드 펜스·설명이 섞여도). 없으면 산문 답 = 거절로 취급.
- 서버 후처리(구조로 강제):
  1. 위젯 추가 패치는 `class_name`(+`schema_name`)만 취해 엔진 추천 주 위젯으로 바꾸고, 에이전트가 준 `layout`·`title`만 유지(가드·실패면 원안 그대로 검증에 맡김).
  2. 시계열 위젯의 차원·입도를 바꾸는 set이 있고 같은 패치에 종류 지정이 없을 때, 바뀐 첫 차원이 temporal이 아니면 `widget_kind=bar` 패치를 덧붙이고, 입도가 있으면 `time_grain=null`도 덧붙인다(diff에 보이므로 사람이 같이 승인).
  3. dry-run 검증 → 결과는 항상 `applied:false`.
- 실행 경로: 에이전트 백엔드가 내장(`deepagents`)이면 OpenAI 호환 채팅 API JSON 모드(모델 = `MAJOR_MODEL`의 `provider:` 뒤, 없으면 `gpt-4.1`; `OPENAI_BASE_URL` 지원; 키 없으면 「OPENAI_API_KEY 가 없어 자연어 편집을 쓸 수 없습니다. AGENT_BACKEND=cliagents 로 CLI 에이전트를 쓰거나, 인스펙터에서 직접 고칠 수 있습니다.」). 스트리밍에서는 먼저 `tool_start{name:"openai.chat", args:{model:"major"}}` 한 줄.
- CLI(기본): 프롬프트 = 시스템 + `\n\n---\n\n` + 사용자 한 덩어리.
  - Claude Code: 스트림 JSON 출력, MCP 설정으로 백엔드 자신의 에이전트 브리지 `dashboard` 모드(서버 이름 `ontology-studio`, `http://<백엔드>/mcp/agent-bridge/dashboard/`)만 연결, 다른 MCP 상속 차단, 허용 도구 = 그 서버의 `dashboard_get`, `widget_recommend`, `dashboard_patch` 셋뿐. 이벤트 변환: 어시스턴트 텍스트 → `token`, 도구 사용 → `tool_start`, 도구 결과 → `tool_result`(400자), 오류 결과 → `error`, 최종 결과 텍스트는 수집만.
  - Codex: `exec`(도구 없음), 출력 줄마다 `token`.
  - 실패(실행 파일 없음, exit≠0) → 「CLI 경로 실패 — API 키 경로로 넘어갑니다. (…)」 후 API 경로. 그것도 실패하면 `error` 이벤트.
  - CLI 출력은 별도 스레드에서 읽어 같은 서버의 브리지 MCP가 응답할 수 있게 한다(단일 프로세스 교착 방지 — 구현 시 필수).
  - 비스트리밍 경로(API #15)는 Claude Code를 도구 없이 텍스트 출력, 180초 제한으로 부른다.
- 브리지 도구 계약(A3 `dashboard` 모드): `dashboard_get(dashboard_id)` → `{dashboard, resolution}` 또는 `{error}`; `widget_recommend(class_name, schema_name="", hint="")` → 추천 API #6 결과(힌트 무시) 또는 `{error}`; `dashboard_patch(dashboard_id, patch(목록 또는 JSON 문자열), dry_run=true)` → `{valid, diff, errors, applied}` — `dry_run=false`면 즉시 저장.
- **스킬 의도(편집)**: 이미 있는 대시보드를 말로 고침. 도구 셋이 없으면 시작하지 말고 백엔드·MCP·발행 상태를 확인하라고 알림. 코드 실행·그래프 변경·SQL/Cypher 작성·접속 정보 취급 금지 — 할 수 있는 것은 명세 패치뿐. 위젯 종류를 고르지 말고 추천 도구를 부를 것(사용자가 명시하면 예외, 그 위젯은 고정). 추천의 rule·reason을 사용자에게 전할 것. 절차: 현재 상태 먼저 → 패치 → 항상 dry-run 먼저 → diff 보여 주고 승인 → 승인 후에만 적용 → 오류는 그대로 설명. 하지 말 것: dry-run 생략, 여러 요청 몰아넣기, 속성명 추측, 확인 전 "바꿨습니다".
- **스킬 의도(자동 구성)**: 발행 모델 하나로 처음 보는 사람용 대시보드. 에이전트가 정하는 것은 클래스 선택·순서·제목 셋뿐, 위젯 종류·축·지표·배치·필터는 엔진. 근거 순서: 골든 퀘스천 → 구축 의도 → (없으면) 데이터 있는 클래스, 관측·위치·마스터 순. 6–8개 이하, 관련 클래스를 붙여 놓기, 사람이 읽는 제목. 없는 클래스 지어내기·속성 추측·전부 담기·빈 대시보드 금지.

### 8.2 자동 구성 (대시보드)
1. 모델(이름 지정, 없으면 전체)의 모든 클래스를 프로파일·추천. 가드·실패는 `skipped`에 담고 계속.
2. 결정적 순서: 규칙 우선순위(O1=0; O4·O5·O6=1; O2·O8=2; O3=3; R6·R7·R10·R11=4; O7·O9=5; 기타=6; O10=9) → 데이터 행 많은 순 → 클래스 이름. 앞 8개, 제목 `<모델 이름> 대시보드`(이름 없으면 「온톨로지 대시보드」).
3. 에이전트 사용 시 선택 요청: 시스템 = 자동 구성 스킬 본문, 사용자 = `[모델]{name, intent, golden_questions}` / `[담을 수 있는 클래스]`[{class_name, display(설명의 ` — ` 앞 또는 클래스 이름), rows, properties(최대 12)}](5000자) / `[응답 형식]` `{"title":"…", "widgets":[{"class_name":"…","title":"…"}], "note":"…"}` + 「widgets 는 최대 8개. 목록에 있는 class_name 만 씁니다. 위젯 종류는 적지 마세요 — 엔진이 정합니다.」. 내장이면 API JSON 모드, 아니면 §8.1 CLI 스트리밍(이벤트를 그대로 흘림).
4. 응답이 쓸 만하면(목록에 있는 클래스만, 중복 제거, 최대 8) 그 순서·제목·대시보드 제목·메모를 씀. 에이전트 불가 → 「에이전트를 쓸 수 없어 결정적 순서로 채웁니다. (<사유>)」, 파싱 실패 → 「에이전트 응답에서 선택을 읽지 못해 결정적 순서로 채웁니다.」(둘 다 `token` 이벤트, 실패가 아님).
5. 배치: i번째 위젯 `x=(i mod 2)×6, y=⌊i/2⌋×2, w=6, h=2`.
6. 전역 필터 후보: 고른 위젯들의 temporal 속성과 범주(2≤k≤50) 속성 중, (이름, 역할)별 처음 것으로, §7.6 판정에서 2개 이상 위젯에 걸리는 것. 최대 3개. `{id:"gf_<n>", kind, label:<속성>, source_class, property, op: between|eq, value:null}`.
7. 명세 `{name:<제목>, description:<메모>, model:{schema_id, schema_name}, widgets, global_filters}` 저장(키 = 요청 `dashboard_id` 또는 제목). 위젯이 0개면 저장하지 않고 이유(「위젯을 하나도 만들지 못했습니다.」/「발행된 클래스가 없습니다.」).

### 8.3 코드 앱 한 턴
- 셸이 보조 실행기(Studio와 같은 환경 변수·인터프리터)를 띄우고 표준입력으로 `{"prompt", "cwd":<앱 폴더>, "session_id", "resume":<첫 턴이 아님>}`를 준다. 실행기는 표준출력에 JSON 줄(§5.2 이벤트 어휘; 첫 줄 `{"kind":"token","text":"","agent":<id>}`, 끝 `final{text, exit_code}`)을 쓴다. 종료 코드: 0 성공, 3 에이전트 못 찾음, 5 에이전트 실패.
- 에이전트 실행(cwd = 앱 폴더, 표준입력 없음, 20분 뒤 강제 종료):
  - Claude Code: 비대화 모드, 스트림 JSON, 허용 도구 = 파일 읽기·쓰기·편집·다중 편집·글롭·그렙 + 셸은 `curl …`과 `node --check …`로 시작하는 명령만, 편집 자동 승인 모드, 설정 출처 = 프로젝트만(사용자 훅·전역 설정 미상속), MCP 상속 차단. 첫 턴 `--session-id <앱의 UUID>`, 이후 `--resume <같은 UUID>`.
  - Codex: `exec`, git 검사 생략, `--full-auto`, 작업 폴더 = 앱 폴더. 세션을 잇지 않는다(파일이 곧 이전 상태). 출력 줄 = `token`.
  - 이벤트 변환은 §8.1과 같고, `tool_result`에 도구 이름을 붙이고 600자로 자르며, 결과 이벤트에서 `usage{duration_ms, turns(단계 수), cost_usd}`를 낸다.
- 셸 쪽: 빈 `token`은 버림. 종료 코드≠0이고 오류 이벤트가 없으면 「에이전트 실행이 끝나지 못했습니다 (exit N) <stderr 끝 300자>」 추가.

### 8.4 코드 앱 프롬프트 (구조)
- 첫 턴: 
  1. `# 만들 앱: <이름>` / `## 사람의 요청` / 원문
  2. 자원이 있으면 `## 사람이 고른 자원 (★) — 재검토하지 말고 실제로 쓰세요` + `- 클래스 X` / `- 속성 C.p` 줄(위젯 멘션은 무시)
  3. `## 발행된 온톨로지 (그래프 <그래프 이름>)` + 클래스 줄 `- <라벨>[ ★] (<건수>건) 속성: a, b` + `    예: {처음 8개 속성 JSON}` + `관계:` + `- (:A)-[:T]->(:B)[ — 설명]` 줄. 클래스 목록 = 그래프의 모든 비`_` 라벨(예시 1건, 건수), 관계 = 실제 간선 유형(최대 200)에 발행 관계 설명을 붙임. ★ = 멘션된 클래스(속성 멘션 포함).
  4. 액션이 있으면 `## 이 온톨로지의 액션 — 앱에 버튼으로 연결할 수 있다 (CLAUDE.md 「액션」)` + `- C.a — 설명` / `    대상 키: k · 입력: p*(설명), …|없음` / `    골든 커맨드: “…”`
  5. 마무리: 규칙은 폴더의 규칙 파일에 있음, 질의를 curl로 시험한 뒤 세 파일 완성, 진행 설명과 보고는 한국어.
- 이후 턴: 원문 + 자원 블록 + 「(같은 앱을 고칩니다. 바뀐 질의는 curl 로 다시 시험하세요. 말과 보고는 한국어로.)」
- 스키마를 못 읽으면 빈 목록으로 진행.

### 8.5 코드 앱 에이전트 규칙 (규칙 파일의 의도 요약)
앱 폴더에 같은 내용으로 두 이름(Claude Code용, Codex용) 저장. 요지:
- **품질 기준**: 현업이 바로 쓰겠다고 할 수준. 조잡한 시안은 실패.
- **작업 범위**: 이 폴더 = 앱 하나. 폴더 밖 읽기·쓰기 금지. 진입점 3파일, 커지면 하위 모듈 허용. 런타임 로드 줄 유지, 문서 제목 = 앱 이름.
- **빌드·외부 자원 금지**: 패키지 관리자·번들러·CDN·웹폰트 없이 오프라인 동작. 쓸 수 있는 것은 제공된 Vue 3(템플릿 컴파일 포함), 전역 ECharts, SDK 함수 7개, 기본 스타일과 색 토큰.
- **데이터**: SDK 질의로만, 읽기 전용. 목·하드코딩 데이터 금지, 없으면 없다고 표시. 질의는 쓰기 전에 질의 주소로 curl 시험 필수. 이 엔진의 Cypher 제약(노드 패턴마다 라벨, 일부 함수·부정 라벨 조건 없음, 쓸 수 있는 집계, `$매개변수`)과 오류 메시지를 읽고 고칠 것.
- **액션**: 프롬프트에 액션이 있으면 해당 클래스 행·카드에 버튼을 달고 SDK `act()`로만 연결. 승인·실행·취소는 창에서 사람이. 앱이 대신 누르거나 창을 흉내 내지 않음. `ids` = 대상 키, 모르는 필수 입력은 빼 둠, `actions()`로 버튼 표시 여부 결정. 업무 시스템·액션 경로를 앱이 직접 부르지 않고, 에이전트도 계획·승인·실행을 curl로 시험하지 않음(목록 조회만).
- **화면**: 한국어 업무 용어, 천 단위 구분, 읽기 쉬운 금액·날짜. 낮/밤 모두 읽히게 색은 토큰만, 캔버스 차트는 색 함수 + 테마 변경 시 다시 칠하기. 데스크톱 폭(1000–1600px), 로딩·빈 결과·오류 상태 각각.
- **말·보고**: 진행 말과 끝 보고 모두 한국어. 문법은 `node --check`. 끝에 무엇을 만들었고 어떤 클래스·관계를 읽는지 3–6줄, 못 한 것은 못 했다고, 질의 실패 상태로 완료라 하지 않음.

---

## 9. 상태·저장
| 대상 | 위치 | 비고 |
|---|---|---|
| 대시보드 명세 | 저장 폴더의 `<키>.json`(UTF-8, 들여쓰기 2) | 원본은 `BOARD_STORAGE_DIR`가 없으면 **분석 백엔드 패키지 안 `data/boards`** — 앱 업데이트 시 사라지고, 같은 설치를 쓰는 모든 데이터 폴더가 공유하며, 배포본에 개발용 대시보드 12개가 들어 있다. 새 구현은 **사용자 데이터 폴더 아래**(예: `boards/`)를 권장(§11) |
| 코드 앱 | 사용자 데이터 폴더 `codeapps/<id>/` | 파일 + `.app.json` |
| 프로파일 캐시, 확장 여부, 행 예산 | 백엔드 메모리 | `/cache/clear`로 비움(행 예산은 안 비워짐 — 원본) |
| 코드 앱 실행 중 턴 | 셸 메모리 | 재시작 시 사라짐 → 이벤트는 마지막 저장 턴으로 재생 |
| 에이전트 세션 | Claude Code 자체 세션 저장소(앱이 정한 UUID) | 앱 쪽은 UUID만 보관 |
| 화면 상태(되돌리기, 선택, 필터 값 편집 중, AI 대화) | 브라우저 메모리 | AI 대화 기록은 저장 안 함 |
| 테마 | 브라우저 저장소 `os-theme` | Studio·셸·코드 앱 공유(같은 오리진) |

## 10. 다른 기능과의 의존
- **A1 셸**: 로컬 웹 오리진(`/api/*` 프록시, `/codeapps/api/*`, `/apps/*` 라우팅), `app` 탭(셸 브리지 없음), 홈 카드·최근 항목, 종료 시 코드 앱 턴 종료.
- **A3 에이전트·MCP**: 에이전트 선택(`AGENT_BACKEND`, `EXTERNAL_AGENT_ID`), CLI 실행 파일 찾기, 검색 MCP 서버(리소스·도구 3개), 에이전트 브리지 `dashboard` 모드, 스킬 2개, 보조 스크립트 실행 환경.
- **M1 구축**: 발행 온톨로지(모델·클래스·관계 `join` 속성·골든 퀘스천·의도), 액션 정의와 골든 커맨드, 구축 후 자동 구성 연계.
- **M2 질의·액션 / M7 시스템 등록**: 액션 목록·계획·승인·실행·보상 API와 계획 카드 화면 부품, 액션 실행기 가동 여부.
- **M3 데이터소스**: 가상 클래스 데이터(SQL 도구가 패브릭을 통해 원천을 읽음).
- **M8 설정**: `MCP_ALLOW_DATASOURCE_EXPANSION`(끄면 가상 클래스 위젯 불가), `OPENAI_*`·`MAJOR_MODEL`(대체 경로), `BOARD_*`.

## 11. 오류·예외
| 상황 | 동작 |
|---|---|
| MCP 서버 불통 | health `mcp:"unreachable"` + 팔레트 안내; 목록·추천 API 503(문구 그대로); 위젯 조회 `error` |
| 동명 클래스(모델 미지정) | 409 + 후보 모델 목록; 위젯 조회 `error` |
| 가드 | 추천 응답 `guard` + 사유; 화면 「<클래스>: <사유>」 |
| 식별자 형식 위반 | 위젯 조회 `error` 「식별자로 쓸 수 없는 이름입니다: …」 |
| 도구가 오류 문구 반환 | 위젯 조회 `error` = 그 문구 |
| 저장 검증 실패 | 422 + 경로별 사유; 화면 「저장 거부: …」 |
| LLM 불가 | 편집: CLI → API 대체 → `error`; 자동 구성: 결정적 순서로 대체(실패 아님) |
| 에이전트가 산문으로 답(거절) | `no_patch` + 메모, 「바꿀 것 없음」 |
| 코드 앱: 같은 앱 동시 턴 | 409 「에이전트가 아직 일하는 중입니다.」 |
| 코드 앱: 에이전트 없음/실패/20분 초과 | `error` 이벤트, 턴 `ok:false`, 목록 「마지막 작업 실패」, 화면 「실패 · 수정 N회」 |
| 코드 앱: 쓰기 질의 | 403 → SDK `Error` |
| 코드 앱: 승인·실행·취소를 헤더 없이 | 403 |
| 액션 실행기 꺼짐 | 대시보드: 「액션」 버튼 없음; 코드 앱: `actions()` 빈 배열, act 경로 503/502 |

## 12. 원본과 비교할 테스트 항목 (구조·계약 기준)
1. 화면 진입 요청 순서와 각 응답 형태(S1). 갤러리 문구·빈 상태.
2. 결정적 엔진: 예제 온톨로지 각 클래스의 `recommend` 결과(주 위젯 종류·규칙·차원·지표·입도·보조 위젯 목록)가 원본과 **같아야 한다**(LLM 무관 — 정확 비교). 가드 코드도 같아야 함.
3. 같은 위젯 정의·필터·선택에 대한 `widgets/query` 결과(열·행·총계·잘림·배지·승격·context)가 같아야 한다(정확 비교, 원천 데이터 동일 전제).
4. 저장 검증: 금지 키, 질의 단어, 중복 id, 알 수 없는 종류, 없는 param_key 각각의 422 경로·사유.
5. 패치 검증: 4가지 op, 없는 위젯·필드, 목록 아닌 필드에 add, 없는 클래스·속성, pinned 설정, diff 형태.
6. AI 편집(LLM): SSE 이벤트 어휘·순서(token/tool_start/tool_result/error → result 하나), result 필드 형태, 항상 `applied:false`, 위젯 추가 패치가 엔진 추천으로 바뀌는지, 시계열 축 변경 시 bar 패치가 덧붙는지, 「적용」 후 파일 반영.
7. 자동 구성: SSE 순서(클래스별 tool_start/tool_result → 에이전트 이벤트 → result), 위젯 ≤8, 2열 배치, 전역 필터 ≤3, 에이전트 없을 때 결정적 순서 결과(정확 비교).
8. 전역 필터 적용 범위(`applies_to`/`not_applicable`)와 연결 방식(same_class/same_name/join via).
9. 열기 해소 판정 5종.
10. Superset 내보내기: 물리 위젯 전부 제외, 가상 위젯 viz_type 대응.
11. 위젯 액션: 선택값 → 조건 자동 채움, 계획 요청 본문, 실행 후 위젯 재조회.
12. 코드 앱 생성: 폴더 구조(파일 6개), 메타 형태, 규칙 파일 자리표시 치환, 템플릿 내용.
13. 코드 앱 턴: 에이전트 명령 줄(허용 도구·권한 모드·설정 출처·세션 인자), 프롬프트 블록 구조, 이벤트 어휘, 20분 제한, 409, 재생(`replay:true`).
14. `/codeapps/api/query`: 쓰기 절 거부(문자열·주석 안 단어는 허용), 행 5000 제한, 값 변환 규칙(노드·관계·경로·정수·시간).
15. `/codeapps/api/schema` 형태. `/apps/*` 정적 제공 규칙(302, 숨김 404, 캐시 헤더).
16. 액션 프록시: 9개 경로, 헤더 없는 승인·실행·취소 403, golden_command 결합.
17. SDK 7개 함수 계약과 확인 창 상태 전이(버튼 표시 조건).
18. 앱 탭에 셸 브리지가 없음. 홈 최근 항목 문구.
19. 앱 종료 시 실행 중 코드 앱 에이전트 프로세스 0개.

## 13. 구현 시 결정할 것 (원본 동작 vs 개선)
1. **대시보드 저장 위치**: 원본은 앱 패키지 안(업데이트 시 소실, 데이터 폴더 간 공유, 개발용 12개 동봉). → 사용자 데이터 폴더 권장. 원본 비교 시 동봉 12개를 어떻게 다룰지(빈 목록으로 시작 권장).
2. **사람 승인 경계 강화**(notes §3): 원본의 "브라우저 헤더 확인"은 curl로 헤더를 붙이면 통과하고, 백엔드 `/api/act/*`는 같은 오리진에서 확인 없이 열려 있으며, 앱 코드는 같은 오리진이라 Studio API 전체와 SDK 창 버튼을 직접 누를 수 있다. → 앱을 별도 오리진(또는 샌드박스 iframe)으로 제공, 승인은 Studio/셸이 띄우는 창에서만(앱 문서 밖), 일회용 토큰 등.
3. **미리보기 iframe 격리**: 원본은 같은 오리진·샌드박스 없음 → 생성 코드가 부모 Studio 창(셸 브리지 포함)에 접근 가능(추정). 샌드박스 속성 권장.
4. **에이전트 권한**: Claude Code의 curl 허용이 범위가 넓음(임의 URL·파일 쓰기 `-o`), 읽기 도구는 폴더 밖도 읽을 수 있음(추정), Codex `--full-auto`. 원본 재현 vs 제한(질의 전용 도구를 MCP로 제공 등).
5. **대시보드 에이전트의 자가 적용**: 브리지 도구 `dashboard_patch(dry_run=false)`가 열려 있어 사람 「적용」 전에 저장될 수 있음 → 브리지에서 dry_run 강제 권장.
6. 화면 저장이 `model`·`description`을 지우는 동작, 홈의 대시보드 항목이 특정 대시보드를 열지 않는 동작, 이름 변경 시 키 유지 — 원본 재현 여부.
7. SQL 필터 값의 "위험 문자면 필터를 조용히 뺌" → 오류로 알리는 편이 안전(빠진 필터는 숫자를 틀리게 만든다). 값 목록 API의 SQL 문자열 조립도 식별자 검사 추가.
8. box_plot·word_cloud 전용 렌더러(원본은 막대로 대체).
9. 스트리밍 CLI 편집에 제한 시간 없음(원본) → 제한 시간 추가.

## 14. 모르는 점 (4단계 실행 기록에서 확인)
1. 실제 화면 배치·문구(특히 편집 화면 머리, 상태 메시지 위치, 인스펙터 「제거」 문구, Superset 대화상자 제외 사유 표시).
2. 스트리밍 편집 중 Claude Code가 `dashboard_patch(dry_run=false)`를 스스로 불러 「적용」 전에 파일이 바뀌는지(스킬은 금지하지만 도구는 허용).
3. 검색 MCP 도구의 행 상한(`ontology_query_datasource_sql`이 에이전트용 30행으로 자르는지 → 가상 클래스 위젯이 늘 잘리는지)과 `row_budget` 실측값.
4. 코드 앱 질의 경로의 읽기 모드 세션을 그래프 엔진이 실제로 강제하는지(쓰기 검사에 없는 패브릭 문장 — 예: 새로 고침 문장 — 이 통과하는지). 분석용 폴더에서만, 사용자 결정 후.
5. 미리보기 iframe에서 부모 창의 셸 브리지 접근 가능 여부, 앱 코드가 `/api/*`(예: 액션 승인)를 직접 부를 때의 결과.
6. Claude Code `--setting-sources project` + `Bash(curl:*)`에서 실제 허용 범위(파이프·리다이렉트·`-o`), 폴더 밖 Read 가능 여부. Codex `--full-auto` 샌드박스에서 질의 curl(로컬 네트워크)이 되는지.
7. 내장 에이전트(`deepagents`)만 있을 때 코드 앱 동작(보조 실행기는 CLI만 다룸 → 실패로 보이는지).
8. 앱 종료 중 실행 중이던 턴이 메타에 기록되는지, 다음 실행에서 「마지막 작업 실패」로 보이는지.
9. 배포본에 동봉된 대시보드 12개가 다른 사용자 환경에서 열릴 때의 해소 판정(예제 온톨로지와 맞는지)과 삭제 시 앱 패키지 파일이 지워지는지(서명된 앱 수정).
10. 이름을 바꿔 저장했을 때 키·파일 동작, 같은 이름 대시보드를 두 번 만들 때 `-2` 규칙(갤러리 목록 기준이라 목록을 새로 읽기 전이면 겹칠 수 있음).
11. 홈 최근 항목의 대시보드 행에서 정보 칸·열리는 화면.
12. 「모델 전체 자동 구성」에서 Claude Code가 브리지 도구를 쓰는지(compose도 같은 스트리밍 함수 → 도구 3개가 붙음), 소요 시간.
13. 위젯 액션 창 계획 카드(M2 부품) 안의 승인·실행 버튼 문구와 흐름.
14. 코드 앱 SSE 재연결(탭을 떠났다 돌아올 때 `from` 값 — 화면은 항상 0부터 다시 받음) 시 중복 표시 여부.
