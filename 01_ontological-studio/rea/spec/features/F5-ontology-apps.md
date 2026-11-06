# F5. 온톨로지 앱 (대시보드 · Object view · 객체 탐색 · 코드 앱)

- 상태: 초안 v0.1 (2026-11-01, Claude 작성) — 사용자 보정 전
- 원본 기준 동작: [`menus/05-ontology-app/design.md`](../../analysis/ontological-studio/menus/05-ontology-app/design.md), [`user-scenarios.md`](../../analysis/ontological-studio/menus/05-ontology-app/user-scenarios.md)
- 관련 문서: [01](../01-architecture.md) §2(앱 오리진) · §3(저장소) · §4(Object API), [02](../02-ontology-model.md) §12 Object set · §13 Object view, [03](../03-security.md) §4 승인 증명 · §8 코드 앱 격리, [04](../04-agent-integration.md) §4 `dashboard` 모드, [F2](F2-query-action.md)(계획 카드·승인 창), F4(그래프 부품)
- 결정 대기: **D-17**(코드 앱 격리), D-18(승인 증명), D-12, D-01(단계: 대시보드·Object view v1, 코드 앱·SDK v2)

---

## 1. 목적

발행된 온톨로지 위에서 **업무 화면**을 만든다. 네 가지 표면이 있다.

| 표면 | 정체 | 만드는 주체 | 데이터 | 값 바꾸기 |
|---|---|---|---|---|
| **대시보드** | 위젯 명세(JSON) | **결정적 엔진**이 위젯을 정하고, 에이전트는 **패치 제안만**, 사람이 적용 | 위젯 → Object set 질의·집계(코어가 번역) | 위젯 「액션」 → F2 계획 카드 |
| **Object view** (신규, 02 §13) | Object type별 객체 360° 화면 설정 | 기본은 자동 생성, 사람이 편집 | Object API(객체·링크·타임라인) | 헤더의 액션 버튼 → F2 계획 카드 |
| **객체 탐색** (신규, Object Explorer식) | 전체 Object type 검색·필터·저장 | — | 검색 + Object set | 선택 객체 대량 액션 → F2 |
| **코드 앱** | 정적 웹 파일 묶음 | CLI 코딩 에이전트 | **SDK = Object API**(앱이 선언하고 사람이 승인한 범위) | SDK `act()` → 계획 요청 → **셸 승인 창** |

핵심 원칙(원본 계승 + 강화)
1. **저장물에 질의문·자격 증명이 없다.** 명세에는 Object type·속성 apiName과 집계만, 질의는 조회할 때 코어가 만든다(원본 원칙 1).
2. **위젯 종류는 엔진이 정한다**(원본 원칙 2). 추천 규칙표를 그대로 유지한다.
3. **에이전트 제안은 사람이 적용한다** — 이번에는 구조로: 에이전트 도구는 적용할 수 없다(원본 원칙 3, 03 S11).
4. **앱은 업무 시스템·Studio API를 직접 부르지 않는다.** 앱은 별도 오리진에서 앱별 토큰으로 Object API 읽기와 액션 **계획 요청**만 한다. 승인·실행은 앱 문서 밖 셸 창에서 사람이(원본 원칙 4, 03 §8).
5. **앱 정의는 데이터 폴더/DB에 둔다.** 앱 패키지 폴더에는 쓰지 않는다(01 §3).

## 2. 원본 기준 동작 요약 [원본]

| 영역 | 원본 0.1.1 동작 |
|---|---|
| 갤러리 | 「말로 만드는 온톨로지 앱」(자원 트리·`@` 멘션·골든 퀘스천 칩·대시보드/코드 앱 전환), 「모델 전체로 자동 구성」, 코드 앱 목록, 대시보드 목록 |
| 대시보드 | 멘션한 클래스 → 엔진이 즉시 위젯(프로파일 → 가드 G2·G5·G8 → 규칙표 O1–O10·R6·R7·R10·R11), 남은 말 → 에이전트 패치 구성안(diff) → 「적용」. 인스펙터(17종·입도·차원·지표, 「고정됨」, 자동 추천으로 되돌리기), 되돌리기, 12칸 격자, 전역 필터·선택 교차 필터(한 홉 연결 same_class/same_name/join), 잘림·집계 승격 배지, Superset 내보내기, 위젯 「액션」 창 |
| 질의 | 위젯 명세에서 조회 시점에 Cypher(적재 클래스) 또는 SQL(가상 클래스)을 만들어 검색 MCP 서버로 실행. SQL 필터 값에 위험 문자가 있으면 **필터를 조용히 뺌** |
| 저장 | 대시보드 JSON 파일을 **앱 패키지 안**에 저장(업데이트 시 소실, 데이터 폴더 간 공유, 개발용 12개 동봉). 화면 저장이 `model`·`description`을 비움 |
| 코드 앱 | CLI 에이전트가 데이터 폴더 `codeapps/<id>/`에 Vue 앱 작성(질의를 curl로 시험), 미리보기 iframe·앱 탭(`/apps/<id>/`). SDK `query(cypher)`(읽기 전용 Cypher)·`schema()`·`actions()`·`act()`·테마 함수 |
| 약점 | 코드 앱이 Studio와 **같은 오리진** → `/api/*` 전체·승인 경로 호출 가능, "사람 확인" = `Sec-Fetch-Mode` 헤더 존재뿐(curl로 우회), SDK 확인 창이 **앱 문서 안**(흉내·대리 클릭 가능), 미리보기 iframe 무샌드박스. 대시보드 에이전트 도구가 `dry_run=false`로 **사람 적용 전 저장** 가능. 에이전트 curl 허용 범위가 넓음(REVIEW #22·#23) |

## 3. 새 설계에서 달라지는 점 [제안]

| # | 원본 | 새 설계 | 근거 |
|---|---|---|---|
| C1 | 위젯 대상 = 클래스(모델명 + 클래스명) | 위젯 대상 = **Object type 전체 이름**(`<Ontology>.<Type>`) 또는 **저장 Object set**(rid). Interface도 대상 가능 | 02 §3·§9·§12 |
| C2 | 위젯 → Cypher/SQL 직접 생성 | 위젯 → **Object set 질의·집계 요청**, 코어가 저장 방식(live/indexed/native)에 맞게 번역. 필터 값은 항상 타입 있는 파라미터 → "위험 문자 필터 조용히 빼기" 결함 제거 | 01 §4, 02 §12 |
| C3 | 프로파일 = 값 추론 위주 | Property `baseType`·기본 키·Link 정의로 먼저 정하고 부족할 때만 값 추론. **추천 규칙표·가드·이유 문장은 그대로** | 02 §6 |
| C4 | 전역 필터 연결 = 관계 속성 `join` 설명 문자열 | 연결 = **Link type**(한 홉) / 같은 속성 apiName·Shared property | 02 §8·§6 |
| C5 | 저장 = 앱 패키지 안 JSON 파일 | 저장 = `workbench.runtime`(DB), JSON 내보내기/가져오기(원본 v1 파일 가져오기 포함). 앱 패키지에 쓰지 않음, 동봉 대시보드 없음 | 01 §3, 원본 design §13-1 |
| C6 | 에이전트 `dashboard_patch(dry_run=false)`로 자가 저장 가능 | 에이전트 도구는 **제안(proposal)만 저장**. 적용은 사람 세션만, 제안 id + 기준 버전 일치 필요 | 03 S11, 04 §3 |
| C7 | 없음 | **Object view**: Object type별 기본 상세 화면(자동 생성 + 편집). F2 근거 객체·탐색 결과·위젯 행·F4 노드에서 연다 | 02 §13, [조사] Core Object Views |
| C8 | 없음 | **객체 탐색**(Object Explorer식): 전체 검색, 범위 필터, 타입 그룹, 목록/그래프 전환, 미리보기, 저장한 탐색(= 저장 Object set), 대량 액션 | [조사] Object Explorer·Workshop |
| C9 | 코드 앱 = Studio와 같은 오리진, SDK = 읽기 전용 Cypher | 코드 앱 = **앱마다 별도 오리진**, **앱별 SDK 토큰**, **선언 범위**(Object type 읽기, Action type 계획 요청) ∩ 사람이 승인한 범위만. SDK는 Object API 기반 | **D-17**, 03 §8, 01 §4 |
| C10 | SDK 확인 창이 앱 문서 안, 헤더 확인 | 승인·실행·취소 확정은 **셸의 네이티브 창**에서만. 앱은 "요청"만 | D-18, 03 §4 |
| C11 | 코드 앱 에이전트가 curl로 질의 시험 | 셸 도구 없이 MCP 도구(`app_try_query` 등)로 시험. 파일 쓰기는 앱 폴더 안만 | 03 S2, 04 §3 |
| C12 | 화면 저장이 `model`·`description`을 비움, 홈 최근 항목이 갤러리를 엶, 클라이언트가 저장 키 중복을 계산 | 값 보존, 최근 항목은 그 대시보드를 엶, 저장 키는 서버가 정함 | D-12(원본 결함) |
| C13 | Superset 내보내기 | MVP·v1 범위 밖(Object API를 Superset이 읽지 못함). §12 Q5 | D-01 |

## 4. 사용자 시나리오

원본 S#과 대응. 사전 상태: 예제 온톨로지 「공급망 운영」(Object type 방식) 발행, 예제 Action type 3개, 예제 시스템 등록(F7).

| # | 시나리오 | 원본과의 차이 |
|---|---|---|
| S1 | 화면 열기: 갤러리 | 상단 탭 「앱」/「객체 탐색」/「Object view」 추가. 자원 트리 = Ontology › Type group › Object type › 속성(저장 방식 배지 `live`/`indexed`/`native`). 동봉 대시보드 없음(빈 목록 문구 원본 그대로) |
| S2 | 말로 대시보드 만들기(「공급망 현황판」) | 같음. 에이전트 구성안은 **제안**으로 저장(id), 「적용」은 사람. 적용 전 저장소 변화 없음을 시험으로 확인 |
| S3 | 이어서 고치기(위젯 `@`, 인스펙터, 되돌리기, 배치, 저장) | 같음. 이름을 바꿔 저장해도 키 유지(원본과 같음), `model`·`description` 보존 |
| S4 | 전역 필터·선택 연동 | 연결 방식 툴팁에 Link type 이름(`link(supplier)`) |
| S5 | 모델 전체 자동 구성 | Ontology 선택. 같음 |
| S6 | 빈 화면에서 끌어다 놓기 | 확장 꺼짐 안내(G8) 대신 「원천에 연결할 수 없음」(live 원천 불통일 때) |
| S7 | Superset 내보내기 | **없음**(C13) |
| S8 | 위젯 액션 버튼 | 계획 카드 「승인」 → 네이티브 승인 창(F2 §5.3), 「실행 (N건)」은 Studio 카드에서 |
| S9 | 열기·삭제·홈 최근 항목 | 최근 항목이 그 대시보드를 바로 엶 |
| S10 | 코드 앱 만들기(「지연 선적 보드」) | 앱이 `http://app-xxxxxxxx.localhost:<apps>/`에서 뜸. 에이전트 도구 줄에 `⟡ 질의 시험 · <Object set 요약>`. 첫 턴 끝에 「권한 확인」 카드(멘션한 Object type 읽기는 자동 부여, 그 밖은 요청) |
| S11 | 코드 앱 말로 고치기 | 같음 |
| S12 | 파일 보기·손으로 고치기 | 같음. 손으로 고친 예는 `where('delayDays', '>', 3)` |
| S13 | 앱 탭으로 열기·최근 항목 | 앱 탭 콘솔에서 셸 브리지 없음, Studio API(`127.0.0.1:<web>/api/…`)는 CSP·오리진 검사로 실패 |
| S14 | 코드 앱 액션 버튼 | 앱 안 창은 계획 **표시**와 「승인 요청」만, 승인은 셸 창 「승인 후 실행」 |
| S15 | 삭제·실행 중·재시작 후 재생 | 같음 + 삭제 시 SDK 토큰·권한 폐기 |
| S16 | 읽기 전용·사람 승인 경계 | `query(cypher)` → SDK 오류 「Cypher 질의는 앱에서 쓸 수 없습니다…」. 앱 토큰으로 승인 API → 403. curl(토큰 없음) → 401 |
| S17 | 오류·대체 경로 | §10 |
| S18 | 종합 과제 | 같은 구조 |
| S19 | 에이전트별 차이 | 같음(Codex는 세션 비유지) |
| N1 | **F2 근거에서 Object view 열기**: 답의 `SHP-03` 칩 → Object view 탭 | 헤더(선적번호·상태 배지·지연일), 속성, 링크(발주 1 · 협력사 1), 타임라인(액션 실행 이력), 「선적 긴급 처리」 버튼 |
| N2 | **Object view 편집**: Shipment 뷰에 「발주 금액」 Function 섹션과 링크 열 변경 → 저장 | 이후 모든 진입점에서 같은 뷰 |
| N3 | **객체 탐색**: 「Goldline」 검색 → Supplier 1, PurchaseOrder 3, Shipment 2 묶음 → Shipment 선택 → 패싯 「상태 = CUSTOMS_HOLD」 → 오른쪽 Object view 미리보기 | 결과 수·하이라이트 |
| N4 | **탐색 저장 → 위젯**: N3 결과를 「통관 보류 선적」으로 저장 → 「대시보드에 추가」 | 위젯 대상 = 저장 Object set, 엔진 추천으로 위젯 결정 |
| N5 | **대량 액션**: 탐색 결과 2건 선택 → 「액션」 → 「선적 긴급 처리」 → 계획 카드(대상 Object set 2건) → 승인 창 → 실행 | F2와 같은 카드 |
| N6 | **앱 권한 범위 밖 요청**: 코드 앱이 선언하지 않은 `Customer`를 `objects('Customer')`로 읽음 | 403 `scope_denied`, 앱 카드에 「권한 요청」 없음(선언 안 했으므로) |
| N7 | **앱 권한 추가**: 다음 턴에서 에이전트가 매니페스트에 `Customer` 읽기와 `notifyCustomer` 계획을 추가 | 앱 화면에 「권한 요청 2」 → 사람이 셸 창에서 승인 → 이후 허용 |
| N8 | **앱이 승인 흉내**: 앱 코드가 계획 후 `request-approval`을 반복 호출하고 자기 화면에 가짜 「승인됨」 표시 | 셸 창은 하나만 뜨고 사람이 눌러야 함. 계획 상태는 `awaiting_approval` 유지 |
| N9 | **원본 대시보드 가져오기**: 원본 v1 JSON(「공급망 현황판」)을 가져오기 | 클래스 → Object type 대응표로 위젯 이관, 대응 못 한 위젯은 「열지 못한 위젯」 |

## 5. 화면 구성과 상호작용

### 5.1 갤러리 [원본 유지 + 탭 추가]
- 머리말 「온톨로지 앱」/「발행된 온톨로지로 만든 화면들입니다.」/「+ 빈 화면에서 시작」. 그 아래 탭 「앱」(기본)·「객체 탐색」(§5.6)·「Object view」(§5.8 목록).
- 「앱」 탭은 원본 구성 그대로: 「말로 만드는 온톨로지 앱」(멘션 입력·자원 트리·앱 이름·골든 퀘스천 칩 최대 6·「대시보드」/「코드 앱」 전환·안내 문구·「앱 만들기 →」/「코드로 앱 만들기 →」), 「모델 전체로 자동 구성」(Ontology 선택 + 「대시보드도 같이 생성」), 「코드 앱 N」, 「대시보드 N」, 빈 상태 문구. 문구는 원본 그대로(「클래스」라는 말만 「객체 유형」으로 바꾸지 않고 유지할지 §12 Q1).
- 자원 참조 형식: `type:<Ontology>.<Type>`, `prop:<Ontology>.<Type>.<prop>`, `set:<rid>`, `widget:<id>`(원본 `class:`/`prop:` 형식 대체).
- 사람이 읽는 이름 = Object type `displayName`(원본의 "설명에서 구분자 앞부분" 규칙은 displayName이 없을 때만).
- 코드 앱 카드에 상태 + 「권한 요청 N」 배지(있을 때).

### 5.2 대시보드 편집 화면 [원본 유지]
원본 design §4.4 그대로: 머리(「‹ 갤러리」·이름·「되돌리기」·「저장」), 왼쪽 팔레트 「온톨로지 객체」(Object type + 저장 Object set, 저장 방식 배지, 「N속성」, deprecated 배지), 필터 막대, 12칸 격자 캔버스(셀 190px, 너비 ≥860px 2열), 위젯 머리(제목·규칙 코드·종류·`@`·「액션 N」·「필터 N」·잘림 `N건 중 M건`·「집계 승격」), 본문(kpi·표·차트), 인스펙터(17종·입도·차원·지표·「자동 추천으로 되돌리기」·「제거」·「고정됨」), 되돌리기 스택(화면 메모리), 클래스 추가 메시지 「<이름> 분석 중…」→「<이름> → <종류> (<규칙>)」, 열 때 「N개 위젯을 열지 못했습니다: <사유>」. 차트 렌더링 규칙(원본 §4.7: 팔레트·숫자 표기 억/만·축·계열·지도 등)은 그대로.
- 차이: 「Superset 내보내기」 버튼 없음. 위젯 행·차트 요소 클릭 = 선택(원본), **행의 객체 아이콘 또는 더블클릭 = Object view 열기**(신규). 저장은 `model`·`description`을 보존.

### 5.3 전역 필터·선택 [원본 유지]
「+ 필터 추가」 후보(시간·범주 2–50), `hit/total 위젯`, 툴팁(「모든 위젯에 걸립니다.」/「걸리지 않는 위젯: …」), 기간 입력 `2025-01`~`2025-12`, 범주 선택, 선택 = 클릭 행의 **기본 키** 우선, 「<값> 선택 — 관련 위젯에 필터를 겁니다」, 「선택을 해제했습니다.」 — 원본과 같다. 위젯 「필터 N」 툴팁의 연결 방식 표기만 `same_class`/`same_name`/`link(<Link type apiName>)`.

### 5.4 AI 편집 패널 [원본 유지 + 제안 저장]
- 대상 표시·입력·이벤트 표시(「⚙ <도구>」, 「↳ <결과>」, 「생각 중…」)·결과 카드(「바꿀 것 없음」/「승인 대기」 + diff/「거부됨」 + `path — reason`)는 원본과 같다. 요청 전 현재 화면을 먼저 저장하는 것도 같다.
- 결과 카드가 「승인 대기」면 그 구성안은 서버에 **제안**(`proposalId`, 기준 버전)으로 저장돼 있다. 「적용」 = `POST …/proposals/{proposalId}/apply`(사람 세션) → 「패치를 적용했습니다.」. 기준 버전이 바뀌었으면 409 → 「대시보드가 그 사이 바뀌었습니다. 다시 요청하세요.」. 「취소」 = 제안 폐기.
- 에이전트가 적용을 시도하면(도구에 `dry_run=false` 등) 도구 오류 「에이전트는 적용할 수 없습니다 — 사람이 「적용」을 눌러야 합니다.」(원본 S11 대응).

### 5.5 위젯 액션 창 [원본 유지 + F2 승인]
원본 §4.8 그대로(머리 「액션 — `<Object type>`」, 부제 문구, 액션 고르기 + 골든 커맨드, 「대상 — <이름> 중에서」 조건 줄, 선택값 자동 채움 문구, 입력, 「계획 세우기」, 1.5초 재조회, 「액션 결과를 반영해 위젯을 다시 읽었습니다.」). 차이:
- 계획 요청 본문 = F2 `POST /api/v1/actions/{actionType}/plan`, 대상 `{where}` 또는 위젯이 저장 Object set이면 `{objectSet: rid}` + 조건.
- 계획 카드(F2 §5.3)의 「승인」은 네이티브 승인 창. 계획자 = 사람(화면) → 1인 모드에서는 본인 승인 가능, 실행은 카드의 「실행 (N건)」.

### 5.6 객체 탐색 (Object Explorer식) [제안]
레이아웃 [조사: Object Explorer A–G, Workshop 필터→표→Object view]:
```
┌ 검색창 [ Goldline              ] 범위: [온톨로지 ▾][타입 그룹 ▾][객체 유형 ▾]  [목록|그래프] ┐
├ 왼쪽: 타입 그룹 › Object type (건수)      ├ 가운데: 결과                  ├ 오른쪽: 미리보기 ┤
│   ★ 즐겨찾기 / 저장한 탐색                │  (타입 미선택) 유형별 묶음 상위 5 │  Object view     │
│   패싯(타입 선택 시): 범주 값·건수,         │  (타입 선택) 표: 제목·헤더 속성   │  (§5.7 축약판)   │
│   기간 히스토그램, 수치 범위              │  체크박스 선택 · 정렬 · 페이지     │                  │
└──────────────────────────────────────────┴──────────────────────────────────┴──────────────────┘
 하단 동작 막대(선택 시): 「액션 ▾」 「내보내기 CSV」 「탐색 저장」 「대시보드에 추가」 「그래프 콘솔에서 보기」
```
- 검색: 각 Object type의 제목 속성 + `searchable.fullText` 속성 키워드 검색, `searchable.vector`가 켜진 타입은 의미 검색 결과를 합침(02 §5). 하이라이트는 일치한 속성 이름·조각. 범위 필터는 Ontology·Type group·Object type(Interface 선택 시 구현 타입 전체).
- 결과 표 열 = 그 타입 Object view 헤더 속성(§5.7) + 제목. 행 클릭 = 오른쪽 미리보기, 더블클릭 = Object view 탭.
- 패싯: 범주 속성(고유값 2–50, 값별 건수), temporal(월 히스토그램, 끌어서 기간), 수치(최소~최대). 패싯 변경 = Object set filter 갱신, URL에 반영.
- 「그래프」 전환: 선택 객체와 한 홉 링크를 F4 그래프 부품으로(최대 200 노드).
- 「탐색 저장」: 현재 Object set(검색어·범위·패싯·정렬)을 이름 붙여 **저장 Object set**(rid)으로. 왼쪽 「저장한 탐색」에 나오고, 대시보드 위젯·F2 계획 대상·코드 앱에서 쓸 수 있다.
- 「즐겨찾기」: 객체·저장 Object set 별표(사용자별).
- 「액션 ▾」: 선택한 타입을 대상으로 하는 Action type 중 보이는 것(`target.mode: set`이면 선택 전체, `single`이면 1건 선택 시만). 고르면 파라미터 입력 → 계획(대상 `{ids}`) → F2 계획 카드(모달).
- 「내보내기 CSV」: 선택 또는 전체(최대 10,000행). PII 속성은 기본 마스킹, 「PII 포함」을 고르면 확인 창 「개인정보 속성 N개를 포함해 내보냅니다.」 + 감사 기록.
- 빈 결과 「찾은 객체가 없습니다.」, 검색 불가 타입(검색 설정 없음)은 범위 목록에 흐리게 + 툴팁 「이 객체 유형은 검색 설정이 없습니다 (F1 Object type › 검색).」

### 5.7 Object view (실행 화면) [제안, 02 §13]
- 진입: F2 근거 칩, 객체 탐색 행, 대시보드 행 아이콘, F4 그래프 노드 「Object view 열기」, 다른 Object view의 링크 행, URL `view=object&type=<Ontology.Type>&pk=<pk>` (Studio 탭, 홈 최근 항목 종류 「객체」).
- 구성(설정 §7.6, 없으면 자동 기본):
  - **헤더**: 아이콘·색, 제목(titleKey 값), Object type 표시 이름, 부제 속성 최대 3, 상태 배지(범주 속성 + 색 표), 저장 방식·신선도(「원천 실시간」/「동기화 hh:mm」), 오른쪽 **액션 버튼**(이 타입을 대상으로 하는 보이는 Action type; 누르면 파라미터 창 → 계획(대상 `{ids:[pk]}`) → F2 계획 카드 모달), 「⋯」(그래프 콘솔에서 보기, 링크 복사, 시점 조회).
  - **속성 섹션**: 그룹별 2열 표(이름·값·formatter·Value type 표시), 편집 레이어 값이면 「편집됨」 표시(툴팁: 액션 실행 id·시각·원천 값), PII 마스킹.
  - **링크 섹션**: Link type별 카드(역할 이름·건수, 표 열·정렬·최대 20행 + 「모두 보기」 → 객체 탐색에 그 링크 set), 행 클릭 = 그 객체의 Object view.
  - **타임라인**: 편집 레이어 변경·이 객체를 대상으로 한 액션 run(상태·단계 칩, F2 run 카드로 연결)·temporal 속성 이벤트, 최신순 50.
  - **위젯 섹션**(선택): 대시보드 위젯 명세 재사용, 대상 Object set = `$this`의 링크 탐색(예: 이 협력사의 발주 금액 월별 추이).
  - **Function 섹션**(선택): `query`/`compute` Function을 `$this`로 호출해 값·표로.
- 시점 조회(`asOf`, 그래프 엔진 지원 시): 헤더 「⋯ › 시점 조회」로 날짜 지정 → 속성·링크를 그 시점으로, 상단에 「<날짜> 기준 (읽기 전용)」, 액션 버튼 숨김.
- 오류: 없는 객체 404 「객체 '<pk>' 을(를) 찾을 수 없습니다.」, 원천 불통(live) → 헤더 아래 경고 「원천에 연결할 수 없어 최신 값을 읽지 못했습니다.」(indexed는 마지막 동기화 값 표시).

### 5.8 Object view 편집기 [제안]
- 「Object view」 탭: Object type 목록(뷰 상태 「자동」/「사용자 설정」·수정 시각). 고르면 왼쪽 섹션 목록(끌어 순서 바꾸기, 추가·삭제), 가운데 실시간 미리보기(예시 객체 선택), 오른쪽 섹션 설정(속성 고르기, 링크 열·정렬, 배지 색 표, 위젯은 대시보드 인스펙터 재사용).
- 「저장」 = 그 Object type의 뷰 설정 새 버전(이력 보관, 「이전 버전으로」). 「자동으로 되돌리기」 = 설정 삭제.
- 검증: 없는 속성·링크·Action type·Function 참조는 저장 거부(「'<p>' 속성이 없습니다.」 형식), deprecated 참조는 경고. 온톨로지 발행으로 참조가 깨지면 그 섹션만 「표시할 수 없음: <사유>」로 그리고 나머지는 보여 준다(F1 제안의 영향 분석에 Object view 포함).

### 5.9 코드 앱 화면 [원본 유지 + 권한]
원본 §4.9 그대로(머리 상태 「에이전트가 코드를 쓰는 중 · m:ss」/「완료 · 수정 N회」, 왼쪽 대화·도구 줄 아이콘 규칙, 입력창, 오른쪽 「미리보기」/「파일 N」, 「미리보기 새로고침」, 「앱 탭으로 열기 ↗」, 파일 쓰기 후 0.6초 뒤 자동 새로고침). 차이:
- 도구 줄: 원본의 `⟡ 질의 시험 · <Cypher>`는 `⟡ 질의 시험 · <Object set 요약>` + 결과 「N건」, `⟡ 온톨로지 구조 읽기`는 `describe_ontology` 호출. `› 명령` 줄은 없음(셸 도구 없음), `✓ 문법 검사 · app.js`.
- **권한 카드**(신규): 매니페스트의 선언 범위(§7.8)와 승인 상태. 미승인 항목이 있으면 「권한 요청 N」 + 「검토」 → 셸 창(§9.3) → 승인/거절. 승인 전 미리보기의 해당 호출은 `scope_denied`로 실패하고 SDK가 앱 안에 「앱 권한이 아직 승인되지 않았습니다」 안내를 띄운다.
- 「파일 N」 목록에 `app.manifest.json`은 보이고(사람이 읽을 수 있게), 규칙 파일·`.app.json`은 숨김(원본과 같음).
- 미리보기 = `<iframe src="http://app-xxxxxxxx.localhost:<apps>/#…" sandbox="allow-scripts allow-same-origin allow-forms">`(§9.2).

### 5.10 SDK 액션 흐름 (앱 안 표시 + 셸 창) [제안]
1. 앱의 버튼 → `act(opts)` → SDK가 앱 문서에 덮개 카드를 그린다(원본 모양: 제목·`<Type>.<Action>`·설명·골든 커맨드·범위·입력, 「닫기」·「계획 세우기」). 원본 문구 유지.
2. 「계획 세우기」 → `POST /sdk/v1/actions/{actionType}/plan` → 계획 표시(원본 「실행 계획 · <상태> · 허용 N건 · 거부 N건 · 사람 승인 필요」 + 표). **이 카드는 표시 전용**이다.
3. 버튼 「승인 요청」(원본 「승인」 자리) → `POST /sdk/v1/action-plans/{id}/request-approval` → 셸이 **네이티브 승인 창**(F2 §5.3과 같은 내용 + 요청자 「코드 앱 <이름>」, 버튼 「승인 후 실행」/「취소」)을 띄운다. 카드에는 「Studio 승인 창에서 확인하세요…」.
4. 사람이 「승인 후 실행」 → 셸이 `approve_execute` 증표로 승인·실행(F2 §7.3). SDK는 `/sdk/v1/events`(또는 1.2초 폴링)로 상태를 받아 실행 결과 표(원본 모양: 대상·결과·단계 ✓/✗/··↺)를 그린다.
5. 「취소 (되돌리기)」 → `request-compensation` → 셸 확인 창(원본 문구) → 보상. 창을 닫으면 `act()`가 `{executed, cancelled, plan, run}`으로 끝난다(원본 반환 형태).
- 앱이 카드를 흉내 내도 승인은 셸 창에서만 일어나므로 효과가 없다. 같은 계획에 대한 창은 하나, 같은 앱의 승인 요청은 대기 중 1개·10초 안 반복 무시(F2 §9.3).

## 6. API

공통: Studio 쪽은 세션 토큰(03 §3). 오류 형식은 `{"error":{"code","message"}}`로 통일(원본 대시보드 API의 `{"detail":…}`, 코드 앱 API의 `{"error":"문장"}`과 다름 — 의도된 차이, 필드 `errors[{path, reason}]`는 유지).

### 6.1 대시보드 (`/api/v1/dashboards`, Apps 모듈)
| # | 메서드 경로 | 요청 | 응답 | 원본 대응 |
|---|---|---|---|---|
| 1 | GET `/api/v1/apps/health` | — | `{objectApi:"ok", agent:{available, backend}, rowBudget, cachedProfiles}` | `/api/board/health` |
| 2 | GET `/api/v1/apps/palette?ontology=` | — | `{ontologies, objectTypes:[{fullName, displayName, storage, propertyCount, status, sourceAvailable}], objectSets:[…], counts}` | `/models`, `/classes` |
| 3 | GET `/api/v1/apps/profiles/{objectType}?refresh=` | — | Profile(§7.2) / 404 | `/classes/{c}/profile` |
| 4 | POST `/api/v1/apps/recommend` | `{target:{objectType}|{objectSet}, refresh?}` | `{primary, secondary[], profile}` 또는 `{guard, reason, profile}` | `/classes/{c}/recommend` |
| 5 | POST `/api/v1/apps/widgets/query` | `{widget, params, globalFilters, selection}` | 항상 200 QueryOutcome(원본 §6.5 필드 그대로) | `/widgets/query` |
| 6 | GET `/api/v1/apps/values?objectType=&property=&limit=50` | — | `{property, type, role, values, truncated, distinctCount}` | `/classes/{c}/values` |
| 7 | POST `/api/v1/apps/filters/applicability` | `{source:{objectType, property}, objectTypes[]}` | `{source, appliesTo:{T:{how, property, via?}}, notApplicable[]}` | 같음 |
| 8 | GET `/api/v1/dashboards` | — | `{dashboards:[{id, name, widgets, ontology, updatedAt}]}` | `/dashboards` |
| 9 | POST `/api/v1/dashboards` | `{name, spec?}` | `{id, dashboard}` — **키는 서버가 정함**(이름 → 키 규칙 + `-2`…) | 클라이언트 키 계산 |
| 10 | GET/PUT/DELETE `/api/v1/dashboards/{id}` | DashboardSpec | 원본과 같음(PUT 422 `errors[{path, reason}]`, GET `resolution[]`) | 같음 |
| 11 | POST `/api/v1/dashboards/{id}/patch` | `{patch, dryRun:true}` | `{valid, diff, errors, applied}` — 사람 세션만 `dryRun:false` 허용 | 같음 |
| 12 | POST `/api/v1/dashboards/{id}/ask/stream` | `{question, widgetId}` | SSE `data: {"kind":…}`: `token`, `tool_start`, `tool_result`, `error`, 마지막 `result{…, proposalId?}` | 같음(+proposalId) |
| 13 | POST `/api/v1/dashboards/{id}/proposals/{pid}/apply` | — | `{dashboard, applied:true}` / 409 기준 버전 불일치 / 404 만료(1시간) | **신규**(원본은 패치 재전송) |
| 14 | DELETE `/api/v1/dashboards/{id}/proposals/{pid}` | — | `{deleted}` | 신규 |
| 15 | POST `/api/v1/dashboards/compose` | `{ontology, dashboardId?, useAgent:true}` | SSE(원본 #17과 같은 이벤트·result 형태). `dashboardId`가 이미 있으면 새 키로 만듦(덮어쓰지 않음) | `/compose` |
| 16 | GET `/api/v1/dashboards/{id}/export` | — | DashboardSpec v2 JSON 파일 | 신규 |
| 17 | POST `/api/v1/dashboards/import` | v1 또는 v2 JSON, `{ontology}` | `{id, dashboard, unmapped:[{widgetId, className, reason}]}` | 신규 |

### 6.2 객체 탐색 (Object 모듈, 01 §4 Object API 확장)
| 메서드 경로 | 요청 | 응답 |
|---|---|---|
| POST `/api/v1/search` | `{text, scope:{ontology?, typeGroups?, objectTypes?, interfaces?}, perType:5}` | `{groups:[{objectType, total, hits:[{objectRef, title, highlights:[{property, fragment}], score}]}]}` |
| POST `/api/v1/object-sets/query` | `{objectSet, select?, orderBy?, pageSize, pageToken?}` | `{data:[Object], nextPageToken, total?}` (01 §4) |
| POST `/api/v1/object-sets/aggregate` | `{objectSet, groupBy:[{property, grain?}], metrics:[{property|"*", agg}], limit}` | `{columns, rows, groupCount, truncated}` — **01 §4에 추가 제안** |
| GET/POST/PATCH/DELETE `/api/v1/object-sets[/{rid}]` | 저장 Object set `{name, description, objectSet}` | 저장 set (rid) |
| GET/PUT/DELETE `/api/v1/favorites` | `{objects:[objectRef], objectSets:[rid]}` | 사용자별 |
| POST `/api/v1/object-sets/export` | `{objectSet, select, includePii:false, limit:10000}` | CSV 스트림 |

### 6.3 Object view
| 메서드 경로 | 응답 |
|---|---|
| GET `/api/v1/object-views/{objectType}` | `{config|null, auto:ObjectViewConfig, version}` — 설정 없으면 자동 기본 |
| PUT `/api/v1/object-views/{objectType}` | 저장(새 버전) / 422 `errors[{path, reason}]` |
| DELETE `/api/v1/object-views/{objectType}` | 자동으로 되돌리기 |
| GET `/api/v1/object-views/{objectType}/versions` | 이력 |
| GET `/api/v1/objects/{objectType}/{pk}?asOf=` | 객체(01 §4) |
| GET `/api/v1/objects/{objectType}/{pk}/links/{linkType}?pageSize=20` | 링크 객체(01 §4) |
| GET `/api/v1/objects/{objectType}/{pk}/timeline?limit=50` | `{items:[{at, kind: edit|actionRun|event, …}]}` — **01 §4에 추가 제안** |

### 6.4 코드 앱 관리 (Studio 쪽, Apps 모듈)
| 메서드 경로 | 요청 | 응답 | 원본 대응 |
|---|---|---|---|
| GET `/api/v1/code-apps` | — | `{apps:[{id, name, updatedAt, turns, running, ok, pendingScopes}]}` | `/codeapps/api/apps` |
| POST `/api/v1/code-apps` | `{name, text, resources}` | `{id:"app-<8hex>", name}` | 같음 |
| GET/DELETE `/api/v1/code-apps/{id}` | — | 원본 필드 + `manifest`, `grants`, `origin` | 같음(삭제 시 토큰·권한 폐기) |
| POST `/api/v1/code-apps/{id}/turns` | `{text, resources}` | `{started:true}` / 400 「무엇을 만들지 적어 주세요.」 / 409 「에이전트가 아직 일하는 중입니다.」 | 같음 |
| GET `/api/v1/code-apps/{id}/events?from=` | SSE | 원본 이벤트 어휘(`user, token, tool_start, tool_result, error, usage, final, done{ok, replay?}`) | 같음 |
| GET `/api/v1/code-apps/{id}/file?path=` | — | `{path, text}` / 404 「그 파일이 없습니다.」 | 같음 |
| POST `/api/v1/code-apps/{id}/launch` | `{surface: preview|tab}` | `{url, expiresAt}` — URL 조각에 일회성 런치 값 | **신규** |
| POST `/api/v1/code-apps/{id}/grants` | `{scopes, proof}` | `{grants}` — 셸 증표(kind `app_grant`) 필수 | **신규** |
| DELETE `/api/v1/code-apps/{id}/grants` | `{scopes}` | 회수(증표 불필요) | 신규 |
- 원본의 `/codeapps/api/query`(Cypher)·`/schema`·`/act/*`는 없다. 앱 데이터 경로는 §6.5 앱 오리진만.

### 6.5 앱 오리진 게이트웨이 (`http://app-<8hex>.localhost:<apps>`)
셸이 제공(01 §2 앱 오리진). 모든 `/sdk/v1/*` 요청은 `Authorization: Bearer <SDK 토큰>` 필수, 토큰의 앱 id = Host의 앱 id. 게이트웨이는 코어에 앱 주체 `app:<id>`로 전달하고 코어가 범위를 강제한다.

| 경로 | 범위 | 코어 대응 |
|---|---|---|
| GET `/`, `/<파일>` | — | 앱 폴더 정적 파일(숨김 파일 404 「없는 파일입니다.」, `Cache-Control: no-store`) |
| GET `/_runtime/<파일>` | — | `og.js`, `og.css`, `vue.js`, `echarts.min.js` (`max-age=3600`) |
| GET `/sdk/v1/ontology` | 범위 안 정의만 | 온톨로지 지도(범위로 거름) |
| GET `/sdk/v1/objects/{type}` · `/{pk}` · `/{pk}/links/{link}` | `objects` | Object API(링크는 양끝 타입 모두 범위 안) |
| POST `/sdk/v1/object-sets/query` · `/aggregate` | `objects`(set의 모든 타입) | Object set |
| GET `/sdk/v1/actions?objectType=` | `actions` | 액션 카탈로그(범위 안만, 오류면 `[]`) |
| POST `/sdk/v1/actions/{actionType}/plan` | `actions` | F2 계획(계획자 `app:<id>`) |
| GET `/sdk/v1/action-plans/{id}`, `/sdk/v1/action-runs/{id}` | 이 앱이 만든 계획만 | F2 조회 |
| POST `/sdk/v1/action-plans/{id}/request-approval` | 이 앱의 계획 | 셸 승인 창 요청 → 202 `{requested:true}` |
| POST `/sdk/v1/action-runs/{id}/request-compensation` | 이 앱의 run | 셸 확인 창 요청 → 202 |
| GET `/sdk/v1/events` | — | SSE: `theme{mode}`, `approval_status{planId, status}`, `run_status{runId, status}`, `grants_changed` |
- 승인·실행·보상 API는 앱 오리진에 **없다**(코어도 앱 주체의 승인·실행을 403).
- 응답 헤더: `Content-Security-Policy`(§9.2), `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Cross-Origin-Resource-Policy: same-origin`. CORS 허용 없음(같은 오리진만).

### 6.6 SDK 계약 (`/_runtime/og.js`, ES 모듈) — 외부 계약
Object API(01 §4)를 감싼다. 객체 모양 `{$objectType, $primaryKey, $title, …속성}`(PII는 `"••••"`).

| 함수 | 동작 | 원본 대비 |
|---|---|---|
| `await ontology()` | 범위 안 Object type(apiName·displayName·primaryKey·titleKey·properties[apiName, displayName, baseType, pii]·links)·Action type 요약 | 신규 |
| `await schema()` | `ontology()` 별칭 | 이름 유지, 모양 변경 |
| `objects(type)` | 질의 빌더: `.where(prop, op, value)` / `.where(filterExpr)`(02 §7.5 식) · `.search(text)` · `.orderBy(prop, 'asc'|'desc')` · `.select([...])` · `.limit(n)` → `await .fetch()` = `{data, nextPageToken}`, `await .all({max: 5000})`, `await .count()`, `await .aggregate({groupBy, metrics})` = `{columns, rows}` | 신규(원본 `query(cypher)` 대체) |
| `objectSet(dsl | rid)` | 같은 빌더, 시작이 Object set(02 §12) | 신규 |
| `await object(type, pk)` | 객체 또는 `null` | 신규 |
| `await links(type, pk, link, {limit})` | 링크 객체 배열 | 신규 |
| `await actions(type?)` | 범위 안 액션 목록. 오류면 `[]` | 유지 |
| `await act(opts)` | §5.10. `opts = {actionType | (class, action), ids?, where?, objectSet?, params?, title?}` → `{executed, cancelled, plan, run}` | 반환 유지, 승인 경로 변경 |
| `await query(cypher)` | 항상 `Error("Cypher 질의는 앱에서 쓸 수 없습니다 — objects()/objectSet() 을 쓰세요.")` | **의도된 차이** |
| `theme()`, `onTheme(fn)`, `color(name)` | 원본과 같음. 테마 원천 = 런치 조각의 `theme` + `/sdk/v1/events`의 `theme`(Studio와 오리진이 달라 저장소 공유 불가) | 동작 유지, 원천 변경 |
- 오류: `SdkError{code, status, message}`. `scope_denied`(403) 「앱 권한 밖입니다: <scope>. 코드 앱 화면에서 권한을 승인하세요.」, `unauthenticated`(401) 「앱 실행 토큰이 만료됐습니다 — 앱을 다시 여세요.」.
- 스타일 `og.css` 토큰(`--og-bg` … `--og-shadow`, 낮/밤)과 Vue 3(템플릿 컴파일러 포함)·ECharts 제공은 원본과 같다.

## 7. 데이터 (02의 개념으로)

### 7.1 DashboardSpec v2 — `workbench.runtime.dashboard`
```yaml
Dashboard:  { id(키), name, ontology: rid, spec, version(int, 저장마다 +1), createdBy, createdAt, updatedAt }
spec:
  format_version: 2
  name, description
  model: { ontology: <apiName>, ontologyRid }            # 원본 {schema_id, schema_name} 후계
  widgets: [WidgetSpec]
  global_filters: [GlobalFilter]                          # source_class → source_object_type
  params: {}
WidgetSpec:   # 원본 필드 유지, 대상만 바뀜
  id, object_type: "<Ontology>.<Type>" | null, object_set: rid | null,   # 둘 중 하나 (원본 schema_name+class_name)
  widget_kind (17종), rule, reason, pinned, dimensions:[prop apiName], measures:[{property|"*", agg, label}],
  filters:[{property, op, param_key}], time_grain, top_n, layout:{x,y,w,h}, title, options
```
- 저장 검증 규칙(원본 §6.3)을 그대로 적용: 자격 증명 계열 키 거부, 질의 단어(`SELECT|MATCH|MERGE|INSERT|UPDATE|DELETE` + 공백) 거부, 알 수 없는 위젯 종류, 위젯 id 중복, 없는 `param_key` — 문구·경로 형식 원본 그대로. 참조 무결성: 없는 Object type 「'<T>' 이 발행된 온톨로지에 없습니다.」, 없는 속성 「'<T>' 에 '<p>' 속성이 없습니다.」.
- 패치(PatchOp: set / add·append / remove, `pinned` 규칙, diff 형태, 하나라도 오류면 무변경)는 원본 §6.4 그대로.
- 키 규칙: 이름 → 영문·숫자·`_`·한글·`-` 외 `_`, 80자, 중복이면 `-2`… — 서버가 원자적으로 정함.
- v1 가져오기: `class_name`(+`schema_name`) → 선택한 Ontology에서 같은 apiName의 Object type(02 §18 이행표: 클래스 → Object type), `dimensions`·`measures` 속성 이름은 원본 컬럼명 → 매핑된 속성 apiName(Backing source `mappings`를 거꾸로 찾음). 못 찾으면 `unmapped`.

### 7.2 프로파일 (조회용, 메모리 캐시)
원본 §6.2 모양 유지, 출처만 바뀜:
| 항목 | 원본 | 새 |
|---|---|---|
| 대상 | 클래스(가상/적재) | Object type(live/indexed/native) 또는 저장 Object set |
| 속성 목록 | 컬럼 선언 ∪ 표본 키 | Property 정의(`vector`·`attachment`·`struct`·배열 제외) |
| type | 값 추론 | `baseType`: string → string(값이 GeoJSON/WKT면 geojson, 수 문자열이면 `stored_as_string`), integer·long → integer, double·decimal → float, date·timestamp → date, boolean, geopoint → geopoint |
| 표본 | 가상 200행 / 적재 50건 | live 200 / indexed·native 50 (같은 수) |
| 데이터 행 수 | count 질의 | Object set count |
| identifier | 키·참조·이름 끝 `_id/_no/_code/_key` | 기본 키 속성, Link type foreign-key 속성, 이름 끝 `_id/_no/_code/_key` 또는 `Id/No/Code/Key`(camelCase) |
| 자기참조 관계(O3) | 관계 정의 | 같은 Object type 양끝의 Link type |
| 캐시 키 | 모델 `schema_id@published_at` + 클래스 | `<온톨로지 rid>@v<발행 버전>` + 대상, `refresh=true`로 갱신 |
- 역할 판정(첫 매치)·좌표 판정·통계는 원본 §7.2 그대로. 추가: `geopoint` → 위도·경도 쌍과 같은 취급(O4 조건 충족).

### 7.3 가드·추천 규칙 [원본 유지]
- 가드: **G2**(데이터 행 0 「이 클래스에는 아직 데이터가 없습니다.」), **G5**(속성 > 30 「속성이 N개로 너무 많습니다.」) 원본 그대로. **G8** = live Object type의 원천에 연결할 수 없음 「원천 데이터소스에 연결할 수 없어 이 객체의 데이터를 읽을 수 없습니다.」(원본 G8 "실데이터 확장 꺼짐"의 후계 — 대시보드는 코어 Object API를 쓰므로 외부 MCP 설정과 무관).
- 추천 규칙표(O5·O6·O4·O1·O2·O3·O7·O8·O9·R7/R6·R11/R10·O10), 범주 후보·지표 묶음·기본 지표·관측 시간축 정의, 순서 "위에서부터 모두 검사, 첫째 = 주 위젯", 위젯 id·제목·layout 기본값, 규칙별 이유 문장 — **원본 design §7.4를 문구까지 그대로** 쓴다(이 문서에 다시 적지 않는다: 같은 표를 두 곳에 두면 어긋나므로 구현은 원본 표를 단일 원천으로 옮긴 코드 상수로 둔다). 추가 1건: O4 조건에 "geopoint 속성 1개"를 OR로 더함.
- 자동 구성(원본 §8.2): 규칙 우선순위·데이터 행 순·이름순 정렬, 최대 8, 2열 배치, 전역 필터 후보 ≤3, 제목 `<Ontology 표시 이름> 대시보드`, 에이전트 불가 시 결정적 순서 — 원본 그대로.

### 7.4 위젯 질의 (Object set 번역)
- 원시 위젯(table·scatter·geo_* 또는 차원·지표 없음): `object-sets/query` + `select`(키 + 차원 + 지표 속성, 최대 14; 없으면 앞 12개).
- 집계 위젯: `object-sets/aggregate`(groupBy = 차원, 첫 차원 temporal + 입도면 `grain`, metrics = 지표). 정렬 = 첫 차원.
- 필터: 위젯 `filters`의 `param_key` 값 + 값이 있는 전역 필터 + 선택을 Object set filter로 합침. 값은 **항상 타입 있는 파라미터**(원본 SQL 경로의 "위험 문자면 필터를 빼고 실행" 없음). `contains`는 대소문자 무시 부분 일치로 통일(원본: 적재 = 양쪽 소문자 포함, 가상 = 앞 일치 `LIKE 'x%'` — 의도된 차이).
- 행 상한 500, 잘리면 원본 축소 규칙(계열 차원 버림 → 입도 올림, 최대 2회, `aggregation_promoted`, 끝까지 잘린 시계열은 `fallback:"table"`), 총계 = `groupCount`, 배지 `<total>건 중 <returned>건`, 값 정규화(count 정수, 그 밖 실수) — 원본 그대로.

### 7.5 전역 필터·선택 연결 (한 홉)
출처 `S.p`를 대상 T에 거는 방법(첫 매치): `same_class`(S=T) → `same_name`(T에 같은 apiName 속성 또는 같은 Shared property) → `join`(S–T 사이 Link type 하나: foreign-key면 그 키 속성끼리, 그 밖 조인 방식은 링크 탐색 필터 `traverse`; `via` = Link type apiName) → 없음(「'<T>' 에 연결할 속성이 없습니다.」). 결과 `context[]` 형태는 원본과 같다.

### 7.6 ObjectViewConfig — `workbench.runtime.object_view` [제안]
```yaml
ObjectViewConfig:
  objectType: rid, version, updatedBy, updatedAt
  header: { subtitle: [prop ≤3], badges: [{ property, colors: {값: 색} }], actions: [ActionType rid] | "auto" }
  sections:
    - { kind: properties, title, properties: [prop], columns: 2 }
    - { kind: links, link: apiName, title, columns: [prop], orderBy, limit: 20 }
    - { kind: timeline, include: [edits, actionRuns, temporal:<prop>], limit: 50 }
    - { kind: widget, widget: WidgetSpec }               # object_set = $this 기준 링크 탐색
    - { kind: function, function: rid, inputs: { <apiName>: $this }, display: value | table }
```
자동 기본(설정이 없을 때, 결정적):
1. 부제: 기본 키·제목이 아닌 속성 중 PII 아님, `formatter`·의미 우선순위 temporal 1개 → numeric 1개 → categorical 1개.
2. 배지: categorical 중 고유값 2–12인 첫 속성(이름에 `status|state|상태` 포함 우선). 색은 값 순서대로 팔레트.
3. 속성 섹션 1개: 모든 표시 가능 속성(`vector` 제외), Interface 공유 속성 먼저, 그다음 정의 순.
4. 링크 섹션: 이 타입이 끝인 모든 Link type(정방향 먼저), 열 = 상대 타입의 제목 + 부제 규칙 속성.
5. 타임라인 섹션(edits + actionRuns).
6. 헤더 액션 = 이 타입을 `target`으로 하는 보이는 Action type 전부.
- 저장 위치: 온톨로지 발행 버전과 **분리**(뷰 변경에 제안·발행을 요구하지 않음). 참조는 rid. §12 Q3.

### 7.7 저장 Object set·즐겨찾기
- 저장 Object set = 02 §12 `ObjectSet`(rid, name, description, owner). 위젯·계획 대상·코드 앱 범위 검사에서 rid로 참조. 삭제 시 참조하는 위젯은 열 때 `missing_object_set`.
- 즐겨찾기 `{owner, objects:[objectRef], objectSets:[rid]}`.

### 7.8 코드 앱 — 데이터 폴더 `codeapps/<id>/` + DB
```
codeapps/app-xxxxxxxx/
  index.html, app.js, style.css (+ 모듈)
  app.manifest.json          # 앱이 "선언"하는 범위 (에이전트·사람 편집 가능)
  CLAUDE.md, AGENTS.md       # 에이전트 규칙(§8.3), 앱 제공 시 숨김
  .app.json                  # 메타(원본과 같은 필드: name, prompt, resources, session_id, turns…)
```
```json
{ "manifestVersion": 1,
  "ontology": "SupplyChain",
  "scopes": {
    "objects": ["SupplyChain.Shipment", "SupplyChain.PurchaseOrder", "SupplyChain.Supplier"],
    "pii": [],
    "actions": ["SupplyChain.Shipment.expediteShipment"] } }
```
- **승인(grant)은 파일이 아니라 DB** `workbench.runtime.code_app_grant {appId, scope, grantedBy, grantedAt, proofId}` — 에이전트가 파일을 고쳐도 권한은 늘지 않는다.
- 유효 범위 = 선언 ∩ 승인. 선언이 줄면 그 승인은 자동 비활성(재선언 시 재승인 필요 없음, 이력 유지).
- 자동 승인: 첫 턴에 **사람이 멘션한 Object type**의 `objects` 읽기만(멘션 = 사람의 의도 표시). `pii`·`actions`와 그 밖 타입은 항상 사람 승인.
- 템플릿(index.html·app.js·style.css 자리표시 「에이전트가 앱을 만들고 있습니다…」)은 원본과 같다. 규칙 파일의 자리표시 치환은 없다(curl 주소를 주지 않음).

### 7.9 SDK 토큰 — 메모리(셸·코어)
`{token(32바이트 무작위), appId, grantsVersion, surface: preview|tab, issuedAt, expiresAt(8시간)}`. 발급: `launch` 호출 시. 전달: 앱 URL **조각**(`#wb_launch=<token>&theme=dark`) — 서버 로그·Referer에 남지 않고, SDK가 읽은 뒤 `history.replaceState`로 지우고 모듈 메모리에만 둔다. 폐기: 앱 삭제, 권한 변경(grantsVersion 불일치 → 401 → 앱 다시 열기), 탭 닫힘, 셸 종료.

## 8. 에이전트 연동 (모드·도구)

### 8.1 `dashboard` 모드 (04 §4)
| 도구 | 동작 | 원본 대비 |
|---|---|---|
| `dashboard_get(dashboard_id)` | `{dashboard, resolution}` | 같음 |
| `widget_recommend(target, hint?)` | 추천 API(§6.1 #4) 결과, hint 무시 | 인자 `class_name` → `target`(Object type 또는 set) |
| `dashboard_patch(dashboard_id, patch)` | 검증 후 **제안으로 저장**, `{valid, diff, errors, applied:false, proposalId}`. `dry_run` 인자를 받지 않음(주면 오류 「에이전트는 적용할 수 없습니다 — 사람이 「적용」을 눌러야 합니다.」) | 자가 적용 차단 |
- 입력 블록·출력 계약(`{"patch":[…], "note":"…"}`, 첫 번째 균형 잡힌 JSON 객체 찾기)·서버 후처리(위젯 추가 → 엔진 추천으로 치환, 시계열 축 변경 시 `bar`·`time_grain=null` 덧붙임, 항상 `applied:false`)·스킬 의도는 원본 §8.1 그대로. `[사용 가능한 클래스와 속성]` 블록은 Object type 표시 이름·apiName·속성 역할로 채운다.
- LLM 호출은 Agent 모듈 단일 클라이언트(01 §4). CLI 경로 실패 → API 경로 대체 문구는 원본과 같되 「OPENAI_API_KEY 가 없어…」 문구는 「설정된 LLM 공급자가 없어 자연어 편집을 쓸 수 없습니다. 인스펙터에서 직접 고칠 수 있습니다.」로.
- 스트리밍 편집에 제한 시간 180초(원본 스트리밍은 무제한 — 의도된 차이).

### 8.2 자동 구성
원본 §8.2와 같음. 에이전트가 정하는 것은 Object type 선택·순서·제목뿐. 결과 저장은 사람이 누른 「대시보드도 같이 생성」의 결과이므로 새 대시보드로 바로 저장한다(기존 대시보드를 덮지 않음).

### 8.3 `codeapp` 모드 (신규 — 04 §4에 추가 제안)
| 항목 | 내용 |
|---|---|
| 실행 | CLI(Claude Code / Codex), cwd = 앱 폴더, 20분 제한, 세션 이어받기 규칙 원본과 같음(Claude 이어받기, Codex 새 세션) |
| 파일 도구 | 읽기·쓰기·편집·글롭·그렙 — **앱 폴더 안만**(04 §7의 경로 한정) |
| MCP 도구 | `describe_ontology()`(선택 Ontology 전체 지도 — 범위 제안용), `app_try_query(builder_json)`(SDK `objects()/objectSet()`와 같은 JSON을 받아 **매니페스트 선언 범위 안에서만** 실행, 20행·`truncated`), `list_actions(object_type?)`, `app_check(path)`(JS 문법 검사), `app_manifest_get()` |
| 없음 | 셸 명령(curl 포함), 계획·승인·실행 도구, 앱 폴더 밖 접근 |
- 프롬프트 구조는 원본 §8.4를 따르되 `## 발행된 온톨로지` 블록 = Object type(표시 이름·apiName·건수·속성·예시 1건)·Link type, 액션 블록 = Action type(`<Type>.<action>`·대상 키·입력·골든 커맨드), 마무리 문구 = "질의는 `app_try_query`로 시험한 뒤 파일을 완성하고, 필요한 범위를 `app.manifest.json`에 선언하라".
- 규칙 파일 요지(원본 §8.5 계승 + 변경): 품질 기준·작업 범위·빌드·외부 자원 금지·화면 규칙·한국어 보고는 같음. 데이터 = SDK `objects()/objectSet()/object()/links()`로만(Cypher 금지), 읽을 Object type과 쓸 Action type은 **매니페스트에 선언**, 선언하지 않은 것은 동작하지 않음, 권한 승인은 사람이 함. 액션 = `act()`로만, 승인 흉내 금지(원본과 같음).

## 9. 보안·권한

### 9.1 주체와 권한
| 주체 | 할 수 있는 것 | 못 하는 것 |
|---|---|---|
| 사람(Studio) | 대시보드 CRUD·제안 적용, Object view 편집, 탐색·내보내기, 코드 앱 관리, 권한 승인(셸 창), 위젯·뷰 액션 계획·실행 | — |
| 에이전트 `dashboard` | 대시보드 읽기, 추천, **제안 저장** | 적용·저장·삭제 |
| 에이전트 `codeapp` | 앱 폴더 파일, 범위 안 시험 질의, 액션 목록 | 셸, 폴더 밖, 계획·승인, 권한 승인 |
| 코드 앱(SDK 토큰) | 유효 범위 안 Object API 읽기, 선언 Action type 계획, 승인·보상 **요청** | 승인·실행·보상 확정, Studio API, 범위 밖 읽기, 다른 앱의 계획 조회 |

### 9.2 코드 앱 격리 (D-17, 03 §8 구체화)
- **오리진**: 앱마다 `http://app-<8hex>.localhost:<apps>`. Studio(`127.0.0.1:<web>`)와도, 다른 앱과도 오리진이 다르다 → 쿠키·저장소·DOM 분리. 게이트웨이는 Host가 `^app-[0-9a-f]{8}\.localhost:<apps>$`이고 그 앱이 존재할 때만 응답(DNS 리바인딩 방지).
- **토큰**: §7.9. 토큰 없는 요청 401, 다른 앱 Host의 토큰 401.
- **CSP**(앱 응답 전부): `default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; frame-ancestors http://127.0.0.1:<web>; base-uri 'none'; form-action 'none'; object-src 'none'`. (`'unsafe-eval'`은 Vue 템플릿 컴파일러용이며 앱 오리진 안에만 영향.) 외부 스크립트·연결 금지(원본 규칙 "CDN 금지"를 구조로 강제).
- **미리보기 iframe**: `sandbox="allow-scripts allow-same-origin allow-forms"`, `allow-top-navigation`·`allow-popups`·`allow-modals` 없음, `referrerpolicy="no-referrer"`. 앱 오리진이 Studio와 다르므로 `allow-same-origin`은 앱 자기 오리진을 유지할 뿐 부모 접근을 주지 않는다(03 §8 문구 "same-origin 불허"를 이렇게 바꾸자고 제안 — §12, 최종 보고 참고). 「앱 탭으로 열기」는 부모(Studio)가 셸에 요청.
- **앱 탭**: 셸의 `app` 탭(셸 브리지 없음, 원본과 같음), 새 창 요청은 같은 앱 오리진만 앱 탭으로, 그 밖은 차단(외부 링크는 OS 기본 브라우저로 열지 묻기).
- **승인 창**: 앱 문서 밖 셸 창(§5.10, F2 §5.3). 앱은 요청만.

### 9.3 권한 승인 창 (셸)
- 제목 「코드 앱 권한 승인」 / 앱 이름·오리진 / 요청 범위 목록: 「읽기: 선적(SupplyChain.Shipment) · 발주 · 협력사」, 「개인정보 속성 읽기: …」(강조), 「액션 계획 요청: 선적 긴급 처리 — 실행하려면 매번 승인 창이 뜹니다」 / 매니페스트 해시 / 「승인」·「거절」(기본 = 거절).
- 승인 → 셸 증표(kind `app_grant`, 범위 목록 해시에 묶임, 03 §4 증표 형식) → `POST /api/v1/code-apps/{id}/grants`.

### 9.4 그 밖
- PII: 대시보드·Object view·탐색·앱 모두 02 `pii` 속성을 기본 마스킹(위젯 차원·지표로는 쓸 수 있으나 표 값은 `••••`, 집계 결과 그룹 키가 PII면 마스킹). 내보내기에서 PII 포함은 확인 + 감사.
- 감사(`workbench.audit`): 대시보드 제안 생성(actor agent)·적용(human)·삭제, Object view 저장, 저장 Object set 생성·삭제, CSV 내보내기(PII 여부), 코드 앱 생성·삭제·권한 승인/회수(proofId)·`scope_denied` 거부(빈도 집계), 앱의 계획 요청·승인 요청.

## 10. 오류·예외 (원본 문구 유지 여부)
| 상황 | 동작 | 원본 |
|---|---|---|
| 동명 대상 모호 | 없음(전체 이름 사용) — 원본 409 `ambiguous` 경로 삭제 | 삭제 |
| 가드 | 추천 응답 `guard` + 사유, 화면 「<이름>: <사유>」 | 유지(G8 문구 변경) |
| 식별자 위반 | 위젯 조회 `error` 「식별자로 쓸 수 없는 이름입니다: '…'」 | 유지 |
| 저장 검증 실패 | 422 + 경로별 사유, 「저장 거부: <path> — <reason>」 | 유지 |
| 제안 기준 버전 불일치 / 만료 | 409 「대시보드가 그 사이 바뀌었습니다. 다시 요청하세요.」 / 404 「구성안이 만료됐습니다. 다시 요청하세요.」 | 신규 |
| 에이전트 적용 시도 | 도구 오류(§8.1) | 신규 |
| LLM 불가 | 편집: CLI → API 대체 → `error`; 자동 구성: 결정적 순서(원본 문구) | 유지(문구 일부 변경) |
| 열 때 해소 | `missing_object_type`, `missing_object_set`, `source_unavailable`, `missing_property`(「속성이 없습니다: a, b」), `ok` | 원본 5종의 후계 |
| Object view 객체 없음 | 404 「객체 '<pk>' 을(를) 찾을 수 없습니다.」 | 신규 |
| 코드 앱 동시 턴 | 409 「에이전트가 아직 일하는 중입니다.」 | 유지 |
| 코드 앱 에이전트 없음·실패·20분 | `error` 이벤트, 「마지막 작업 실패」, 「실패 · 수정 N회」, 원본 문구 | 유지 |
| 앱 범위 밖 | 403 `scope_denied` → SDK Error | 신규(원본: 쓰기 Cypher 403) |
| 앱 토큰 없음·만료 | 401 → SDK Error 「앱 실행 토큰이 만료됐습니다 — 앱을 다시 여세요.」 | 신규 |
| 앱이 승인·실행 API 호출 | 경로 없음 404, 코어 직접 호출은 오리진·토큰 검사로 401/403 | 원본 403 「승인·실행·취소는 앱 화면에서 사람이 눌러야 합니다.」 대체 |
| 앱의 Cypher | SDK Error(§6.6) | 의도된 차이 |
| Action 모듈 미준비 | 위젯 「액션」 버튼 없음, `actions()` `[]` | 유지 |

## 11. 원본과 비교할 테스트

### 11.1 같아야 함
1. 갤러리 문구·빈 상태·멘션 입력 동작(후보 8개, 칩, 붙여넣기 3000자, ⌘/Ctrl+Enter).
2. **결정적 엔진**: 원본 프로파일 고정 입력(픽스처)에 대해 추천 결과(주 위젯 종류·규칙·차원·지표·입도·보조 위젯)와 가드 코드가 **정확히 같다**. 예제 온톨로지에서 원본 가상 클래스와 1:1인 live Object type은 실제 데이터로도 같다.
3. 같은 위젯·필터·선택의 QueryOutcome(열·행·총계·잘림·배지·승격·context) — 원천 동일 전제, `contains` 제외(D3).
4. 저장 검증 422 경로·사유, 패치 검증(4가지 op, 없는 위젯·필드, 목록 아닌 필드, pinned, diff 형태).
5. AI 편집 SSE 어휘·순서(token/tool_start/tool_result/error → result), 결과 필드, 항상 `applied:false`, 위젯 추가 → 엔진 추천 치환, 시계열 축 변경 시 bar 덧붙임.
6. 자동 구성: 이벤트 순서, 위젯 ≤8, 2열 배치, 전역 필터 ≤3, 에이전트 없을 때 결정적 결과(정확 비교).
7. 전역 필터 적용 범위(`same_class`/`same_name`), 선택 = 키 속성 우선.
8. 위젯 액션: 선택값 → 조건 자동 채움, 실행 후 위젯 재조회 문구.
9. 코드 앱: 생성 응답 id 형식, 턴 이벤트 어휘, 409, 20분 제한, 재생 `{kind:"done", replay:true}`, 파일 목록 숨김 규칙, 앱 탭에 셸 브리지 없음, 홈 최근 항목 문구.
10. SDK `actions()`·`act()` 반환 형태 `{executed, cancelled, plan, run}`, 확인 카드 상태 라벨(원본 §4.11 목록).

### 11.2 의도된 차이 (D-12, D-17, D-18)
| # | 차이 | 확인 |
|---|---|---|
| D1 | 대시보드 저장 = DB, 앱 패키지 무변경, 동봉 대시보드 없음, `model`·`description` 보존, 서버 키 결정 | 저장 후 앱 폴더 해시 불변 |
| D2 | 에이전트 `dashboard_patch` 후 저장본 불변, 사람 적용만 반영 | S2(원본 design §14-2 의심 동작의 반대) |
| D3 | 필터 값은 파라미터(위험 문자 필터도 적용), `contains` 통일 | 따옴표 포함 값 필터 |
| D4 | 코드 앱 오리진 분리: 앱에서 `fetch('http://127.0.0.1:<web>/api/v1/…')` 실패, 미리보기에서 `window.parent` 접근 불가 | 03 §11-5 |
| D5 | 승인은 셸 창, 앱 토큰으로 승인 API 403·없음, 헤더 위조 curl 401 | S16, N8 |
| D6 | `query(cypher)` 불가, SDK = Object API | S16 |
| D7 | 범위 밖 403 `scope_denied`, 권한 승인 흐름 | N6, N7 |
| D8 | Superset 내보내기 없음 | — |
| D9 | 홈 최근 항목이 그 대시보드를 엶 | S9 |
| D10 | Object view·객체 탐색·저장 Object set(신규 표면) | N1–N5 |
| D11 | 오류 형식 `{"error":{code, message}}` 통일 | API |
| D12 | 코드 앱 에이전트 셸 도구 없음(curl 대신 `app_try_query`) | 에이전트 명령 줄 |

## 12. 열린 질문
- Q1. 화면 용어: 원본 문구의 「클래스」를 「객체 유형」으로 바꿀지(비교성 vs 새 모델 일관성). 이 문서는 원본 문구 유지를 기본으로 함.
- Q2. 앱별 서브도메인 오리진(`app-<id>.localhost`) 채택 — 03 §8은 `127.0.0.1:<apps>` 단일 오리진으로 적혀 있다. 단일 오리진이면 앱끼리 저장소·토큰이 섞인다. [확인 필요: Electron/Chromium에서 `*.localhost` 해석·쿠키 동작 검증]
- Q3. Object view 설정의 저장 위치·버전: 온톨로지 발행과 분리(이 문서) vs 온톨로지 정의의 일부(02 §13은 "표현" 개념으로만 적음).
- Q4. 객체 탐색을 F5 안 탭으로 둘지, 홈 카드·전역 검색(⌘K, P 명세)로 올릴지.
- Q5. Superset 내보내기를 되살릴지(v2) — 살린다면 live Object type의 원천 테이블만 대상.
- Q6. 코드 앱 SDK에 Function 호출(`functions.execute`) 범위를 v2에 넣을지 — 이번 범위는 Object API + 계획 요청만(D-17 권장안).
- Q7. 앱이 Object view를 열어 달라고 셸에 요청하는 함수(`openObject`)를 둘지 — 데이터 접근은 없지만 앱 밖 UI 조작이라 범위 정의 필요.
- Q8. 첫 턴 자동 승인(멘션한 Object type 읽기)이 허용 가능한 완화인지, 모든 범위를 사람 승인으로 할지.
- Q9. 대시보드 공유(다른 데이터 폴더·사람에게)는 내보내기 JSON으로 충분한지.
