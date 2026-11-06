# F1. 온톨로지 구축 (Ontology Manager + 에이전트 구축)

- 상태: 초안 v0.1 (2026-11-01, Claude 작성) — 사용자 보정 전
- 원본 기준 동작: `../../analysis/ontological-studio/menus/01-ontology-build/design.md`(이하 **M1 설계**), `user-scenarios.md`(S1–S17)
- 근거 문서: [02 온톨로지 모델](../02-ontology-model.md)(개념·이름은 여기를 그대로 따른다), [03 보안](../03-security.md), [04 에이전트](../04-agent-integration.md), [90 결정 대기](../90-open-decisions.md)
- 관련 결정: **D-15**(구축 5가지), **D-19**(포털 스키마 디자이너·릴리스 API), D-05·D-06·D-07·D-08(모델), D-10(셸 도구), D-12(원본 결함 처리 원칙)
- 함께 읽는 기능 명세: F2(계획 카드·승인·실행), F3(데이터소스·카탈로그), F5(Object view 소비·대시보드), **F6(품질 게이트·검수)**, F7(시스템 레지스트리), P(셸·대화·파일)

---

## 1. 목적

온톨로지를 **설계하고, 데이터에 연결하고, 검증해서, 사람이 승인한 버전으로 발행**하는 메뉴다. 두 가지 작업 방식을 한 작업본(draft) 위에서 섞어 쓴다.

| 방식 | 누가 | 무엇을 | 근거 |
|---|---|---|---|
| **설계 화면** (Ontology Manager식) | 도메인 설계자가 직접 | Object type·Property·Shared property·Value type·Link type·Interface·Backing source·Action type·Function·Object view·Type group을 폼과 그래프로 편집 | [조사] Palantir Ontology Manager, 02 문서 |
| **에이전트 구축** (원본 계승) | 에이전트가 제안, 사람이 고침 | 브리프(재료·의도·골든 퀘스천/커맨드) → 전략 추천 → 설계·백킹 연결·문서 추출 → 골든 커맨드로 Action type 생성·dry-run → 검증 → **변경 제안** | [원본] M1 설계 §4–§7 |

두 방식의 결과는 모두 **작업본**에 쌓이고, **변경 제안(Proposal)** 으로 묶여 diff·검증·영향 분석·골든 회귀를 거친 뒤 **사람의 명시적 승인(증명)** 으로만 발행된다(02 §14, 03 §4). 에이전트는 작업본 편집과 제안 생성까지만 한다.

사람이 판단할 추출 결과(근거 약한 사실·보류)는 F6 품질 검수로, 액션의 **실행·승인**은 F2로 넘긴다.

---

## 2. 원본 기준 동작 요약 [원본]

근거: M1 설계 전체. 핵심만 적는다.

- **화면**: 대화형 화면(사이드바 = 구축 대화 목록·파일 패널·「초기화」 / 가운데 = 비었으면 브리프 패널, 아니면 대화창 / 오른쪽 = 「온톨로지 그래프」 패널, 탭 「그래프」「정보」「배포」「검수」). (M1 설계 §4.1)
- **브리프 3단계**: `1 소스`(문서 업로드·데이터소스+스키마·등록 시스템, 「테이블 구조로 바로 생성」), `2 대상`(새 스키마 / 기존 스키마 추가 인제스천), `3 의도`(구축 의도·Golden Question·Golden Command, 에이전트 초안, 권장 전략). 시작 조건 = 의도 + 질문 ≥1 + 소스 ≥1. (§4.2)
- **구축 턴**: SSE 스트리밍, 도구 칩(ONTOLOGICAL/DATA/TOOL), 끼어들기(steer)·중단, 4단계 진행(설계 → 적재 → 검증 → 검수), 끝에 `ontology_build_report` 블록에서 **구축 보고서**(Golden Question 검수 카드·Golden Command 표·검수 현황 줄) 추출, 「맞다/틀리다」 + 피드백으로 재구축. (§4.3–4.4, §6)
- **정보 탭**: 클래스·관계 편집, 클래스 ⛁ 「데이터 연결」(바인딩: 컬럼→속성 매핑·기본 조회조건·라벨 속성·스키마 변경 감지 / 동작(behavior): 파라미터 SQL 템플릿 / 액션 편집기), 역바인딩 패널, 인과 가설 패널. (§4.6–4.7)
- **액션 정의 계약**: 단계(steps)·인자 매핑(`path.|query.|header.|body.`)·표현식 뿌리(`$this` `$params` `$actor` `$run` `$plan` `$before` `$steps` `$cancel`)·보상·정책(roles/when, 비면 기본 거부)·confirm_threshold·max_targets·writeback·golden_command·version·검증 기록. 오류·경고 문구. Operation 선택 시 인자 자동 채움. (§7.4)
- **결정적 규칙**: 전략 추천 결정 표(§7.6), 카탈로그 일괄 생성 규칙(LLM 없음, §7.7), 역바인딩 점수(열 0.6 + 타입 0.2 + 이름 0.2, §7.8), 보고서 추출 규칙(§6.4), dry-run 요약 형식(§7.4).
- **발행**: 화면에 버튼 없음, 대화로 「발행해 줘」 → 에이전트가 발행 도구 호출. 스키마 그룹 단위 전체 덮어쓰기(멱등), 이름 규칙 위반 시 전체 중단. (§7.5, S8)
- **배포 탭**: 개발→운영 릴리스 패키지(만들기·계획·적용). (§4.8)
- **초기화**: 「Ontological 데이터」가 그래프 **전체** 삭제. (§4.10)
- **알려진 결함·약점**(M1 설계 §13, REVIEW #19·#20·#21): 데이터소스 SQL 경로가 패키지에서 막혀 있을 가능성, 구축 화면 계획 카드에서 실행까지 가능, 발행 버튼 없음, 초기화 범위 과대·스키마 삭제 시 발행물 잔존, 문서 OCR 미연결, 업로드 이름 경로 이동 미검사, 이름 부분 일치 조회, 적재 시 클래스 정의 덮어쓰기 추정, 클래스 이름이 그래프 전역 라벨, 권장 전략이 에이전트에 전달되지 않음, 에이전트가 권한 우회·전체 환경 상속.

---

## 3. 새 설계에서 달라지는 점 [제안]

### 3.1 큰 변화

| # | 원본 | 새 설계 | 근거 |
|---|---|---|---|
| 1 | 정의 = 클래스·관계·바인딩·behavior·액션, 저장 즉시 확정 | 02 메타모델 전체(Object type ~ Object view). 모든 편집은 **작업본**에 쌓이고 발행해야 반영 | 02 §2, §14 |
| 2 | 편집 UI = 오른쪽 「정보」 탭의 작은 폼 | **설계 화면**(Ontology Manager식): 홈·리소스 목록·상세 탭·속성 편집기(컬럼 매핑·Automap·객체 미리보기)·Link type 조인 설정·Action type 폼 편집기·검색(⌘K) | [조사] 3-1~3-6, D-19 |
| 3 | 바인딩 = 테이블 1개, 컬럼 그대로 | Backing source 여러 개(주/보강), 키·매핑·필터 **표현식**, 우선순위, 저장 방식 live/indexed/native | 02 §7 |
| 4 | behavior = 파라미터 SQL | **Function**(query = Object set, compute, llm). SQL 직접 실행은 고급 옵션(기본 끔) | 02 §11, D-07, **D-15①** |
| 5 | 액션 = 클래스에 붙은 시스템 호출 단계 | **Action type**: 대상·타입 있는 파라미터·폼·규칙(객체/링크 편집 + callSystem)·제출 조건·승인·부수효과. 원본 단계·표현식 계약은 그대로 포함 | 02 §10 |
| 6 | 발행 = 대화로만, 전체 덮어쓰기, 이력 없음 | 「제안 만들기」→ 제안 화면(diff·검증·영향 분석·골든 회귀) → 「발행」 버튼(네이티브 확인 창) → 버전 n. 이력·되돌리기 | **D-15③**, 02 §14 |
| 7 | 에이전트가 발행까지 | 에이전트는 **작업본 편집 + 제안 생성**까지. 「발행해 줘」에는 제안을 만들고 발행 위치를 안내 | 04 §3·§4, 03 §4 |
| 8 | 골든 커맨드 dry-run은 **발행 후에만** 가능 | **작업본 dry-run**(발행 전 정의로 계획만 만들고 실행 불가). 그래서 에이전트가 발행 없이 검증 루프를 끝낼 수 있다 | 신규 [제안] |
| 9 | 골든 퀘스천 = 지시문 재료 | + **회귀 테스트**: 제안마다 자동 실행, 결과를 발행 판단에 보여 줌 | 02 §15 |
| 10 | 배포 탭(개발→운영 릴리스 패키지) | 버전 이력 + **YAML 내보내기/가져오기**. 운영 환경 개념은 없음(단일 사용자) | **D-19** |
| 11 | 초기화 = 그래프 전체 삭제 | **온톨로지 단위**, 범위 선택 + 네이티브 확인 + 자동 백업 | **D-15④**, 03 S13 |
| 12 | 클래스 이름 = 그래프 전역 라벨(온톨로지끼리 섞임) | 이름공간 `<Ontology>.<Type>`, 불변 rid | 02 §3 |
| 13 | 권장 전략은 표시만 | 사용자가 고른 전략을 `[전략]` 라벨로 에이전트에 전달 | M1 설계 §13-12 해결 |
| 14 | 오른쪽 그래프 탭에서 인스턴스 직접 생성·수정·삭제 | 데이터 변경은 Action type으로만(감사). native Object type은 「기본 편집 액션」(생성·수정·삭제)을 자동 생성할 수 있음 | 02 §10, 원칙 2 |

### 3.2 결정 대기 항목의 권장안 적용

**D-15 구축 5가지** (권장안으로 작성):

| # | 질문 | 이 명세의 적용 |
|---|---|---|
| ① | 데이터소스 SQL 경로(behavior·미리보기·뷰) | behavior는 **Function(query)** 로 대체(Object set 질의, 코어가 저장 방식에 맞게 번역). 백킹에는 `kind: sql`(읽기 전용 단일 SELECT, 검증 필수)을 허용. SQL 직접 실행 Function은 D-07 고급 옵션(기본 끔). 백킹 미리보기는 Data 모듈의 읽기 전용 경로(`fabric_ro`)로 항상 동작해야 한다 |
| ② | 구축 화면의 계획 카드 | 작업본 dry-run 계획 카드는 **보기 전용**(「승인」「실행」 없음, 배지 「작업본 계획 — 실행할 수 없음」). 발행본 계획은 F2 카드를 쓰고, 승인은 **네이티브 창**(03 §4) |
| ③ | 발행 버튼 | 상단 바에 「제안 만들기」·「발행」 추가. 발행은 열린 제안이 있을 때만, 네이티브 확인 창 필수 |
| ④ | 초기화 범위 | 온톨로지 단위로 한정, 범위 체크(§5.17), 네이티브 확인 + 자동 백업. 그래프 전체 삭제 기능은 없음 |
| ⑤ | 문서 OCR | **v1 선택 기능**: 스캔 PDF·이미지에 OCR을 켜는 설정(F8, 기본 끔). 켜져 있으면 업로드 시 텍스트 층을 만들어 추출(F6)·에이전트가 같은 텍스트를 쓴다 |

**D-19 포털의 튜토리얼 밖 기능**: 포털 스키마 디자이너(계획→단계 실행)는 이 메뉴의 **설계 화면 + 제안 흐름**으로 흡수한다(제안 = 계획, 발행 = 단계 실행). 릴리스 패키지 API는 **온톨로지 내보내기/가져오기(YAML)** 로 대체한다(§5.16).

**그 밖의 결정 대기 반영**: D-05(live 다원천 = 같은 데이터소스만) → 백킹 탭 검증 규칙. D-06(편집 레이어 충돌 기본 edit-wins) → Object type 「편집」 설정 기본값, flag 선택 시 F6로. D-07 → Function 편집기의 「SQL」 종류는 고급 설정이 켜졌을 때만 보임. D-08(작업본 1개) → 온톨로지당 작업본 1개·열린 제안 최대 1개. D-10(셸 도구) → 문서 파서 실행이 필요한 구축 턴에서만 사용자 동의 후 켬(§8.5). D-12 → 원본 문구·형식은 유지, 결함은 고치고 §11에 「의도된 차이」로 표시.

### 3.3 원본 M1 기능 이행표 (S1–S17 → 새 위치)

| 원본 | 원본 내용 | 새 위치 | 변화 |
|---|---|---|---|
| **S1** 화면 구성 | 사이드바·브리프/대화·오른쪽 4탭 | §5.1 「구축 대화」 작업 공간 + 「설계」 작업 공간, 오른쪽 패널 탭 「그래프·변경·검수·제안」 | 「정보」 탭 → 설계 화면, 「배포」 탭 → 이력(§5.16) |
| **S2** 브리프 1 소스 | 문서·데이터소스·시스템 선택 | §5.14.1 그대로 | 문서 OCR 선택(D-15⑤) |
| **S3** 브리프 2 대상 | 새 스키마 / 추가 인제스천 | §5.14.1 「대상」: 새 온톨로지 / 기존 온톨로지(작업본) | 「기존 Object type만 사용」 토글(원본 규칙, 기본 켬) |
| **S4** 브리프 3 의도 | 초안·골든·권장 전략 | §5.14.1 그대로 + 전략 선택이 에이전트에 전달 | §3.1-13 |
| **S5** 구축 스트리밍 | 도구 칩·끼어들기·중단·4단계 | §5.14.2, §8.4 | 5단계(제안 만들기 추가), 이벤트 이름 일부 변경 |
| **S6** 보고서·피드백 | GQ 검수 카드·GC 표·검수 현황 | §5.14.3 그대로 + 「제안 보기」 줄 | GC 표 검증 열이 「✓ dry-run(작업본)」/「✓ dry-run(발행본)」 구분 |
| **S7** 그래프·정보 탭 편집 | 클래스·관계 편집, 엔티티 편집 | 설계 화면(§5.2–5.13), 오른쪽 「그래프」 탭은 보기 전용 + 액션 호출 | 엔티티 직접 편집 → 기본 편집 액션 |
| **S8** 「발행해 줘」 | 에이전트 발행 | 상단 「발행」 버튼 + 제안 화면(§5.15). 에이전트는 제안만 | **의도된 차이** |
| **S9** 골든 커맨드 → 액션 | 탐색·생성·발행·dry-run | §8.3 Phase 2.5, 작업본 dry-run | 발행 없이 검증 |
| **S10** 테이블 구조로 바로 생성 | 카탈로그 → 클래스·관계(가상) | 브리프 1단계 상자 + 설계 화면 「+ 새로 만들기 → 테이블에서 만들기」(§5.3.1), 규칙 §7.5 | Object type(live)+Link type(foreign-key)로, 작업본에 |
| **S11** 바인딩·behavior | 컬럼 매핑·기본 조건·SQL behavior | Object type 「백킹 데이터」 탭·속성 편집기(§5.4–5.5), Function(query)(§5.10) | **D-15①** |
| **S12** 액션 편집기·dry-run | 단계·인자 자동 채움·정책·dry-run | Action type 편집기(§5.9) | 폼 편집기·제출 조건·승인 추가, 작업본 dry-run |
| **S13** 역바인딩 | 문서 엔티티 → 테이블 후보 | Object type 「백킹 데이터」 탭의 「원천 찾기」 + 구축 대화 오른쪽 패널(§5.5.4), 규칙 §7.6 | 결과가 작업본 변경(주 원천 추가)으로 |
| **S14** 인과 가설 | 통계 발견 → 관계 승격 | **v2**: Link type 후보 제안(02 §18). v1에서는 패널 숨김, 전략 표의 판정만 유지 | 범위(00 §5) |
| **S15** 검수 탭 | M6 축약판 | 오른쪽 패널 「검수」 탭 = F6 컴포넌트 | F6 |
| **S16** 배포 탭 | 릴리스 패키지 | 「이력」 화면(버전·diff·되돌리기) + 내보내기/가져오기(§5.16) | **D-19** |
| **S17** 대화 관리·초기화 | 세션·파일·초기화 | 세션·파일은 그대로(P 명세), 초기화는 §5.17 | **D-15④** |

### 3.4 단계별 범위 (00 §5, D-01 연결)

| 단계 | F1에 포함 |
|---|---|
| **MVP** | 설계 화면: Object type·Property·Link type·Backing source(table/sql/manual, live/indexed/native)·Action type(파라미터·callSystem·modifyObject·제출 조건·승인)·Type group·검색. 작업본 → 「발행」(diff + 검증만, 네이티브 확인). 카탈로그 일괄 생성. 시드 예제 |
| **v1** | 에이전트 구축 전체(브리프·전략·초안·구축 턴·보고서·골든 커맨드 → 액션), 문서 추출 백킹(F6 게이트), 역바인딩, Interface·Shared property·Value type, Function(query·compute), Object view 설정, **제안 화면**(영향 분석·골든 회귀)·이력·되돌리기·YAML 내보내기/가져오기, OCR(선택) |
| **v2** | Function(llm), 인과 발견 → Link type 후보, 여러 작업본(D-08), 객체 데이터 포함 내보내기 |

---

## 4. 사용자 시나리오

원본 시나리오(S-번호)는 [원본] 흐름을 유지하면서 대상만 새 모델로 바꾼다. 새 시나리오는 N-번호.

### 4.1 원본 대응 시나리오
| 번호 | 시나리오 (새 설계 기준) | 원본과 같아야 할 것 | 달라지는 것 |
|---|---|---|---|
| S1 | 「온톨로지 구축」 카드 → 구축 대화 작업 공간. 예제 「공급망 운영 (예제)」이 오른쪽 그래프에 보임 | 사이드바 구성·문구, 브리프/대화 전환 규칙 | 오른쪽 탭 이름, 상단 「설계」 전환 |
| S2–S4 | 브리프 3단계로 재료·대상·의도 입력, 초안·권장 전략 확인 | 단계 요약 문자열, 시작 조건, 초안 자동 요청 규칙, 안내 문구 전부 | 「스키마」→「온톨로지」 문구, 전략 선택 라디오(에이전트 전달) |
| S5 | 「이 브리프로 구축 시작」 → 스트리밍, 끼어들기, 중단 | 말풍선·상태 문구·중단 문구·도구 칩 규칙 | 도구 이름, 진행 5단계 |
| S6 | 보고서에서 「맞다/틀리다」 + 피드백 → 재구축 | 카드 문구·활성 조건·`review_feedback` 형식 | 보고서 아래 「제안 #n 보기」 |
| S7 | 설계 화면에서 만들어진 Object type을 고친다 | — | 화면 전체가 새 설계 |
| S8 | 「발행해 줘」 → 에이전트가 **제안**을 만들고 「제안 #n을 만들었습니다 — 위의 「발행」에서 검토 후 발행하세요」 → 사람이 「발행」 → 네이티브 확인 → 버전 n | 발행 후 질의(F2)에서 골든 퀘스천 답이 원본과 같은 값 | 에이전트는 발행 못 함 |
| S9 | 시스템만 고르고 골든 커맨드 입력 → 에이전트가 Action type 생성 → **작업본 dry-run** 검증 → 보고서 GC 표 | 시스템 탐색·보상 고르기·정책 기본값 규칙, 보고서 GC 표 형식 | 발행 단계 없음 |
| S10 | 데이터소스 스키마 고르고 「테이블 구조로 바로 생성」 → 미리보기 → 「이대로 작업본에 추가」 | 미리보기 문구·머리 `… N · 관계 M · 속성 K`, 카탈로그 비었을 때 문구 | 결과 = live Object type + foreign-key Link type, 발행 전까지 질의 불가 |
| S11 | Object type 「백킹 데이터」에서 테이블 연결·Automap·필터·제목 속성, Function(query)로 질문 대응 | 「매핑하지 않은 컬럼은 조회할 수 없습니다…」, 「모든 동작에 항상 적용됩니다…」 안내 | behavior → Function |
| S12 | Action type 편집기에서 단계·인자 자동 채움·보상·제출 조건·승인 → 저장 → 작업본 dry-run | 인자 자동 채움 결과, 검증 오류·경고 문구, 저장 버튼 활성 조건 | 저장 문구(§10), 폼 편집기 |
| S13 | 문서로 만든 Object type에서 「원천 찾기」 → 후보 판정 → 확정 | 점수 규칙·판정 4종·결과 문구 | 결과가 작업본 변경 |
| S15 | 오른쪽 「검수」 탭 | F6 | — |
| S16 | 「이력」에서 버전·diff 확인, 내보내기 | — | D-19 |
| S17 | 대화 관리, 「초기화」(온톨로지 단위) | 세션 API·대화 전환 규칙 | 초기화 범위·확인 방식 |

### 4.2 새 시나리오
| 번호 | 시나리오 | 기대 결과 |
|---|---|---|
| N1 | **수동으로 Object type 만들기**: 「+ 새로 만들기 → Object type」 → 이름 `Shipment`/선적, 「백킹 데이터」에서 `wms.shipment` 선택 → 「모두 자동 매핑(Automap)」 → 기본 키 `shipmentNo`, 제목 `shipmentNo` → 「객체 미리보기」 | 매핑 현황 `7 / 7 컬럼 매핑됨`, 미리보기 20건, 키 결측·중복 0. 작업본 변경 1건 |
| N2 | **변환 키로 다원천 링크**: Link type `shipmentPurchaseOrder`(many-to-one), 조인 foreign-key, `fromExpr = replace(ref_po_no,'PO-','')` → 「링크 미리보기」 | 일치율·불일치 예시 표시, 카디널리티 위반 0 |
| N3 | **보강 원천**: `PurchaseOrder`에 `wms.shipment`를 enrichment로 추가, `match` 표현식, 계산 속성 「최근 선적 상태」 | 같은 데이터소스가 아니면 live 거부 안내 → indexed로 전환(D-05) |
| N4 | **Value type·Shared property·Interface**: Value type `CountryCode`(regex), Shared property `country`, Interface `Partner` → `Supplier`·`Customer`가 구현 | 구현 타입의 매핑 누락이 검증 오류로 표시 |
| N5 | **Action type 폼 편집기**: `expediteShipment` 파라미터 순서·라벨·도움말·기본값을 폼 미리보기로 확인, 제출 조건 「운송 중인 선적만」, 승인 `count($targets) > 3` | 오른쪽 실시간 폼 미리보기, 조건 실패 메시지 미리보기 |
| N6 | **제안 → 발행**: 「제안 만들기」 → diff·검증·영향 분석·골든 회귀 확인 → 「발행」 → 네이티브 확인 창 | 버전 n+1, Object API·에이전트 도구·액션 카탈로그 교체. 검증 오류가 있으면 발행 불가 |
| N7 | **되돌리기**: 이력에서 버전 n-1 「이 버전으로 되돌리기」 | 되돌리기 제안 생성 → 발행 → 버전 n+1(내용 = n-1) |
| N8 | **내보내기/가져오기**: 버전 n을 YAML로 내보내 다른 데이터 폴더에서 가져오기 | 새 온톨로지의 작업본으로 들어오고, 없는 데이터소스·시스템은 경고 |
| N9 | **영향 분석**: 대시보드가 쓰는 속성을 삭제한 뒤 제안 | 「깨지는 의존 1건: 대시보드 '…' 위젯 '…'」 경고, 발행 시 추가 확인 |
| N10 | **검색 ⌘K**: `입고` 입력 | 별칭 「입고 선적」을 가진 Object type `Shipment`가 첫 결과 |
| N11 | **Object view 설정**: `Shipment`의 헤더 속성·링크 섹션·액션 버튼 배치 → 미리보기 객체로 확인 | 발행 후 F2·F5에서 객체 클릭 시 이 화면 |
| N12 | **에이전트와 동시 편집**: 구축 턴이 Object type을 고치는 중에 사람이 같은 속성을 고침 | 늦게 저장한 쪽이 409 「다른 곳에서 먼저 바뀌었습니다…」, 변경 목록에 두 주체 구분 |
| N13 | **골든 퀘스천 관리**: 설계 화면 「골든」에서 기대 결과(Object set) 지정 → 「지금 실행(작업본)」 | 통과/실패/변화 표시, 다음 제안의 회귀 기준 |

---

## 5. 화면 구성과 상호작용

### 5.1 전체 레이아웃

F1 탭은 **두 작업 공간**을 가진다. 상단 바의 전환 「구축 대화 · 설계」(URL `view=build&space=chat|design`). 원본 `view=build`, `session=<id>` 쿼리는 그대로 받는다.

**상단 바 (두 공간 공통)**
- 온톨로지 선택(`displayName` + 발행 버전 배지 `v3` 또는 「미발행」).
- 작업본 상태: `작업본 변경 N건`(누르면 오른쪽 「변경」 탭), 검증 배지(오류 n 빨강 / 경고 n 주황 / ✓).
- 「제안 만들기」(변경 0건이면 비활성), 열린 제안이 있으면 `제안 #n` 칩(누르면 제안 화면).
- 「발행」(열린 제안이 있고 검증 오류 0일 때만 활성. **D-15③**). MVP에서는 제안 화면 대신 「발행 미리보기」(diff + 검증) 대화상자.
- 검색 상자(⌘K / Ctrl+K).
- 오른쪽 끝 「⋯」: 이력, 내보내기, 가져오기, 초기화, 온톨로지 삭제.

**구축 대화 공간** (원본 S1 레이아웃 유지)
- 왼쪽 레일: 원본과 같은 메뉴(F 번호 순). 스트리밍 중 대화형 뷰 전환 비활성.
- 사이드바: 제목 「온톨로지 구축」, 「+」(새 대화), 설명 「문서를 분석하고 스키마, 엔티티, 관계를 생성하는 작업 모드입니다.」[원본 문구 유지 — 문구 개정 여부는 §12], 대화 목록(온톨로지 이름 배지·제목·시각·×), 파일 패널, 「초기화」.
- 가운데: 비었으면 브리프 패널, 아니면 대화창(§5.14).
- 오른쪽 패널(폭 조절·더블클릭 초기화): 탭 「그래프」「변경」「검수」「제안」.
  - 「그래프」: 보기 전환 「작업본」/「발행본」 × 「스키마」/「객체」. 배치 5종(원본과 같음), 필터·검색·자연어 질문(단일 LLM 클라이언트 경유, 04 §3)·노드 확장. 스키마 보기에서 노드 더블클릭 → 설계 공간의 해당 Object type. 객체 보기는 **발행본만**, 편집 대신 노드 메뉴에 실행 가능한 액션(F2 계획 카드로 연결).
  - 「변경」: 작업본 변경 목록(§5.15.1과 같은 행), 주체 아이콘(사람/에이전트), 행별 「되돌리기」.
  - 「검수」: F6 「확인하기·보류함」 컴포넌트(툴팁 「빌드가 남긴 것 중 사람이 판단할 것」, 배지 = 확인 필요 + 보류). [원본 S15]
  - 「제안」: 열린 제안 요약(검증·영향·골든 결과 숫자)과 「제안 화면 열기」.

**설계 공간** (Ontology Manager식) [조사 3-1, 3-2]
- 왼쪽 내비게이션:
  - 「홈」, 「제안」, 「이력」, 「상태 점검」
  - 「리소스」: Object types · Properties · Shared properties · Value types · Link types · Interfaces · Action types · Functions · Object views · Type groups — 각 항목 옆 개수, 작업본에서 바뀐 개수는 점 표시
  - 「골든」: Golden questions · Golden commands
- 본문: 선택한 리소스의 목록 또는 상세. 상세는 상단 「저장」「되돌리기」와 변경 수(`3 edits`)를 가진다(여러 필드를 고친 뒤 한 번에 저장 [조사 3-5]).
- 모든 상세 화면 공통 머리: `displayName`, `apiName`(복사 버튼), rid(접힘), 상태(`experimental`/`active`/`deprecated`), 작업본 표시(「새로 만듦」「바뀜」「삭제 예정」), 「⋯」(복제, 삭제, 이력 보기, 의존 대상 보기).

### 5.2 홈 (Discover)
- 카드: 「최근 본 Object type」(객체 수 — 발행본 기준, 의존 앱 수), 「Type group」(그룹별 미니 그래프와 멤버 수), 「작업본 요약」(새로 만듦·바뀜·삭제 예정 수), 「상태 점검」 요약(문제 수), 「골든」 요약(통과 n / 실패 m — 마지막 실행 기준).
- 비었을 때(새 온톨로지): 「아직 정의가 없습니다.」 + 버튼 3개 「테이블에서 만들기」「직접 만들기」「구축 대화로 시작」.

### 5.3 Object type

#### 5.3.1 목록과 만들기
- 표 열: 아이콘·표시 이름, apiName, 저장 방식(live/indexed/native 배지), 주 원천(`erp.purchase_order` 또는 「문서」「수동」), 속성 수, 링크 수, 액션 수, 상태, 작업본 표시. 필터: Type group, 저장 방식, 상태.
- 「+ 새로 만들기」 메뉴:
  - **직접 만들기**: 표시 이름·복수형·apiName(표시 이름이 영문이면 자동 제안, 한글이면 비워 두고 입력 요구)·아이콘·색·Type group → 저장 방식 선택(설명 포함) → 생성 후 상세로.
  - **테이블에서 만들기**(원본 「테이블 구조로 바로 생성」의 설계 화면 버전): 데이터소스·스키마·테이블 다중 선택 → 미리보기 표 → 「이대로 작업본에 추가」. 규칙은 §7.5. 배지 「LLM 불필요」.
  - **문서에서 만들기**: 구축 대화 공간으로 이동해 문서 소스 브리프를 연다(문서 추출은 에이전트·F6 경로).

#### 5.3.2 상세 탭
`개요 · 속성 · 백킹 데이터 · 링크 · 액션 · 인터페이스 · Object view · 편집 · 의존 대상 · 이력` [조사 3-2]

- **개요**: 메타데이터(표시 이름, 복수형, 설명, `aiDescription`(「에이전트 도구 설명 — 비우면 설명을 씁니다」), 별칭(칩 입력), 아이콘·색, 상태, Type group), 기본 키·제목 속성 요약, 저장 방식과 동기화 상태(indexed: 마지막 동기화 시각·객체 수·「지금 동기화」 — 발행본만), 미니 링크 그래프, 검색 설정(전문 검색 속성, 벡터 검색 켜기·대상 속성).
- **속성**: §5.4 속성 편집기.
- **백킹 데이터**: §5.5.
- **링크**: 이 타입이 양끝 중 하나인 Link type 그래프와 목록. 그래프에서 다른 Object type으로 끌어 놓으면 「새 Link type」 폼이 열린다 [조사 3-2 ④].
- **액션**: 이 타입을 대상으로 하거나 파라미터로 쓰는 Action type 목록 + 「+ 새 Action type」(대상 미리 채움).
- **인터페이스**: 구현한 Interface와 속성 매핑 표(Interface 공유 속성 ↔ 이 타입 속성 선택). 누락은 빨강.
- **Object view**: §5.11.
- **편집**: `editable` 속성 체크 목록(indexed·native만 활성, live는 「live 저장 방식은 읽기 전용입니다. 쓰기는 액션의 시스템 호출로 원천에 합니다.」), 편집 레이어 충돌 정책(`edit-wins` 기본 / `source-wins` / `flag` — flag면 「원천이 바뀌면 품질 검수 보류함으로 보냅니다」) [D-06], native 전용 「기본 편집 액션 만들기」(생성·수정·삭제 Action type 3개를 작업본에 추가).
- **의존 대상**: 이 타입을 쓰는 Link type·Action type·Function·Interface·Object view·저장된 Object set·대시보드 위젯·코드 앱(선언)·골든 퀘스천 [조사 3-2 ⑤]. 영향 분석(§5.15.3)과 같은 데이터.
- **이력**: 이 정의의 버전별 변경(발행본)과 작업본 변경.

### 5.4 속성 편집기 (컬럼 매핑·Automap·미리보기) [조사 3-3]

화면 3분할:
1. **위 — 속성 목록 표**: 열 = 상태, 표시 이름, apiName, baseType(배열이면 `[]`), Value type, 필수(`*`), PII, 키(🔑)/제목(T) 표시, **매핑**(`← erp.purchase_order.amount_usd` 또는 `fx: map(status, …)`, 계산 속성이면 `ƒ 함수명`, 미매핑이면 「매핑 없음」). 머리에 매핑 현황 `9 / 11 컬럼 매핑됨`(주 원천 기준). 「+ 속성」, 「Shared property에서 추가」.
2. **오른쪽 — 선택 속성 패널** (탭 「일반 · 표시 · 고급」):
   - 일반: 표시 이름, apiName, 설명, baseType(02 §6 표), 「여러 값 허용(배열)」, Value type 선택(선택 시 baseType 고정), Shared property 연결(연결 시 이름·타입·제약 상속 표시, 「연결 해제」), 필수, 기본 키 토글, 제목 키 토글.
   - 표시: 포맷터(number·통화·단위·날짜 형식·퍼센트), PII(「PII로 표시하면 에이전트 도구 결과와 화면에서 값이 가려집니다」 — 원본 안내 「개인정보 컬럼은 PII로 표시하면 결과에서 제외됩니다.」를 대체).
   - 고급: 계산 속성(Function 선택·입력 바인딩), 식별 속성(F6 동일성 판정에 쓰임, §12 열린 질문), 설명용 `aiDescription`.
3. **아래 — 백킹 데이터 미리보기**: 원천 선택 탭(주 원천 + 보강 원천들), 원천 샘플 행(20행) 격자. 각 열 머리에 매핑된 속성 칩 또는 「+ 속성으로」. 열 머리 클릭 → 「이 컬럼을 속성 X로 매핑」/「표현식으로 매핑…」.
   - **Automap** 「모두 자동 매핑」: 미매핑 컬럼마다 (a) 이름 정규화(소문자·`_`/공백 제거) 일치하는 기존 속성에 매핑, (b) 없으면 새 속성 생성(apiName = 컬럼명 camelCase, 표시 이름 = 컬럼 설명 또는 컬럼명, baseType = §7.5 타입 매핑, PII 후보 = 컬럼명 패턴 `email|phone|mobile|ssn|resident|birth|address|이메일|전화|주민|주소`). 결과를 미리 보여 주고 「적용」 [제안].
   - **표현식으로 매핑**: 표현식 편집기(02 §7.5 문법, 자동 완성 = 원천 컬럼·함수, 실시간 검사 = 결과 타입·오류·live 번역 가능 여부 「이 함수는 live에서 원천 SQL로 바꿀 수 없습니다: regexExtract」, 샘플 행 5개에 대한 계산 결과 미리보기).
   - **「객체 미리보기」**: 작업본 정의로 객체 20개를 만들어 표로 보여 준다(키·제목·속성, 보강 원천 병합 결과 포함). 머리 통계 `원천 행 N · 객체 M · 키 결측 a · 키 중복 b · 보강 미일치 c · 식 오류 d`. 각 문제는 클릭하면 해당 행. [조사 3-3 Preview objects]
   - 안내(원본 유지): 「매핑하지 않은 컬럼은 조회할 수 없습니다.」

### 5.5 백킹 데이터 (Backing source)

#### 5.5.1 백킹 목록
- 저장 방식 선택(live/indexed/native, 02 §7.3 표의 설명을 툴팁으로). 바꾸면 「저장 방식을 바꾸면 발행 때 동기화 작업이 다시 돕니다.」
- 원천 카드 목록: 역할(주/보강), 종류(table/sql/system/document/manual), 원천 표시(`erp / erp.purchase_order`), 우선순위, 갱신(indexed: live·schedule cron·manual), 상태(컬럼 변경 감지 결과).
- 「+ 원천 추가」 → 종류 선택:
  - **table**: 데이터소스·스키마·테이블 선택(F3 카탈로그, 「스키마를 불러오는 중...」 원본 문구), 샘플 행.
  - **sql**: 데이터소스 + SELECT 편집기(읽기 전용 단일 SELECT, 저장 전 검증 = 구문 분석·문장 1개·SELECT/WITH만·`LIMIT` 금지(원본 규칙 계승)·실행 시간 제한 내 시험 실행 → 「저장했습니다. (실제 실행으로 검증됨)」, 기본값 없는 파라미터는 없음). D-15①.
  - **system**: 등록 시스템·GET operation·`recordsPath`(응답에서 레코드 배열 경로, 시험 호출로 후보 제시). indexed 전용.
  - **document**: 문서 컬렉션(F6 품질 게이트 통과분). native(주 원천) 또는 enrichment.
  - **manual**: native 전용, 액션·화면 입력.

#### 5.5.2 원천 상세
- **키**: 이 원천의 행 → 객체 기본 키. 기본 키 속성마다 표현식 1개(기본 = 같은 이름 컬럼). 타입 불일치는 오류.
- **match**(enrichment 전용): 객체를 찾는 표현식.
- **매핑**: 속성별 표현식 표(속성 편집기와 같은 데이터, 이 원천만 보기).
- **필터**: 원본 「기본 조회조건」의 후계. 조건 행 편집기(컬럼·연산자 `= != > >= < <= in contains starts_with is_null not_null`·값) 또는 표현식 직접 입력. 안내 원본 유지: 「모든 동작에 항상 적용됩니다. 너무 좁으면 조회 결과가 0건이 됩니다.」
- **우선순위**: 같은 속성을 여러 원천이 줄 때(02 §7.6). 값 충돌은 동기화 때 F6로.
- **컬럼 변경 감지**(원본 「스키마 변경 감지」): 사라진 컬럼 / 새 컬럼 / 타입 변경. 사라진 컬럼을 쓰는 매핑은 오류로 표시, 「새 컬럼을 속성으로 추가」 버튼.
- 저장 시 데이터소스에 닿지 못하면 저장은 하되 원본 문구 계승: 「저장했습니다. (데이터소스에 연결할 수 없어 컬럼 검증은 건너뛰었습니다)」 + 검증 경고로 남음(제안 시 다시 검사).

#### 5.5.3 검증 (화면 즉시 표시, 02 §17-3·4)
- live·indexed는 주 원천 정확히 1개. native는 table/sql 주 원천 불가.
- live: 주 원천 table/sql, 보강 원천은 없거나 **같은 데이터소스**만(D-05), 모든 표현식 번역 가능. 아니면 「live는 같은 데이터소스의 원천만 합칠 수 있습니다 — indexed로 바꾸세요.」
- 매핑 대상 속성 존재, 원천 컬럼 존재(카탈로그), 키 표현식 타입 = 키 속성 타입.

#### 5.5.4 원천 찾기 (역바인딩, 원본 S13)
- 위치: document 주 원천을 가진 Object type의 「백킹 데이터」 탭 상단 배너 「문서에서 만든 타입입니다 — 데이터소스에서 같은 대상을 찾을 수 있습니다」 → 「원천 찾기」, 그리고 구축 대화 오른쪽 「그래프」 탭 아래 패널(브리프에 데이터소스 스키마가 있을 때, 원본 위치 유지).
- 흐름(원본과 같음): 대상(데이터소스·스키마) → 「미리보기」(「미리보기입니다. 아직 저장되지 않았습니다.」) → 표(Object type·판정 자동/검토필요/충돌/매칭없음·테이블·점수·근거 「일치 … / 미일치: …」, 검토필요·충돌은 후보 선택 「선택하세요」) → 「확정」.
- 확정 결과는 **작업본 변경**: 고른 테이블을 주 원천(table)으로 추가하고 저장 방식을 indexed로, 기존 document 원천은 enrichment(match = 제목 속성 정규화 일치)로 바꾼다. 매칭되지 않는 문서 객체는 F6 동일성(sameAs) 검사 대상이 된다. 규칙 §7.6.
- 결과 문구 원본 계승: 「바인딩 N개 완료.」→「원천 연결 N개를 작업본에 추가했습니다.」, 「확인이 필요해 건너뛴 항목 K개.」, 「미바인딩 U개는 그대로 남습니다.」, 충돌 안내 「충돌 — 테이블 A 을 X 가 함께 지목했습니다. 어느 쪽인지 고르지 않으면 바인딩하지 않습니다.」

### 5.6 Shared property · Value type
- **Value type** 목록·상세: apiName(PascalCase), 표시 이름, baseType, 제약(정규식·열거·범위·길이 중 하나 이상), 설명, 「값 시험」 입력란(통과/실패와 이유). 사용처 목록. 제약을 좁히면 영향 분석에서 「기존 값 중 위반 예상 n건(발행본 표본 1000건 기준)」.
- **Shared property** 목록·상세: apiName(camelCase), 표시 이름, baseType·배열, Value type, 설명, 사용 Object type 목록(각 타입의 매핑 상태), 사용 Interface. 「Object type에 추가」.

### 5.7 Link type [조사 3-4]
- 목록: 이름(정방향 표시 이름 ↔ 역방향 표시 이름), 양끝 타입, 카디널리티, 조인 방식, 상태.
- 상세 폼:
  - 양끝: `from`(Object type, apiName, 표시 이름), `to`(같음). 예 `선적 → 발주 (purchaseOrder)` / `발주 → 선적들 (shipments)`.
  - 카디널리티: 1:1 / 1:N / N:1 / N:N 그림 선택.
  - 조인 방식 탭 4개:
    - **foreign-key**: `from` 쪽 표현식(자동 완성 = from 타입 속성·원천 컬럼) → `to` 쪽 속성(보통 기본 키). 변환 허용.
    - **join-source**: 조인 테이블/SQL 원천, `fromKey`·`toKey` 표현식. N:N에서만 권장.
    - **link-object**: 링크 자체가 될 Object type 선택(그 타입의 두 속성이 양끝 키를 가리키도록 설정).
    - **stored**: 액션·추출이 만드는 간선. indexed/native 양끝에서만.
  - aiDescription, 상태.
- 「링크 미리보기」: from 객체 표본 200개에 대해 `일치율 x% · 미일치 a · to 쪽 다중 일치 b · 카디널리티 위반 c` + 예시. 원본에서 「대상 키가 없는 값은 잇지 않음」 규칙 유지.
- 검증(02 §17-5): 양끝 존재, 조인 표현식 타입 일치, 카디널리티 vs 키 유일성(예: N:1인데 `to` 속성이 유일하지 않으면 오류).

### 5.8 Interface
- 상세: apiName·표시 이름·설명, 공유 속성 목록(Shared property 선택), 선택적 링크 정의, 구현 Object type 목록과 매핑 상태 표(행 = 구현 타입, 열 = 공유 속성, 칸 = 매핑된 속성 또는 빨간 「없음」).
- 「구현 타입 추가」는 그 타입의 「인터페이스」 탭 매핑 화면을 연다.

### 5.9 Action type 편집기

원본 액션 편집기(M1 설계 §4.7)의 모든 입력을 포함하고, Palantir식 구성으로 나눈다 [조사 3-5]. 좌측 하위 메뉴: `개요 · 파라미터 · 폼 · 규칙 · 제출 조건 · 승인 · 부수효과 · 검증(dry-run) · 이력`.

- **경고 띠**(원본 계승): 액션 실행 모듈(F2)에 닿지 못하면 「액션 실행 모듈에 닿지 못했습니다. 정의는 저장되지만 시스템·operation 목록과 dry-run 은 쓸 수 없습니다. <오류>」. (원본의 신원 토큰 미설정 경고는 03 §3 설계로 사라짐.)
- **개요**: 표시 이름, apiName(원본 이름 규칙 `^[A-Za-z][A-Za-z0-9_]*$`를 포함하는 02 §3 camelCase 규칙; 기존 원본 이름 가져오기는 허용), 「설명 (에이전트에게 보입니다)」→ `description`과 `aiDescription` 두 칸, 대상(Object type 또는 Interface, `single`/`set`, 「대상 상한」 = maxTargets 기본 50), effect(write/read), 대응 골든 커맨드(선택, 원문 표시), 취소용 액션(compensate), 버전 표시 `v<n>`, 검증 상태(「✓ dry-run(작업본) 2026-…」/「미검증」).
- **파라미터**: 표(apiName, 표시 이름, 타입 = baseType·Value type·**Object 참조**·Object set, 필수, 기본값(표현식 가능), 설명). 「JSON Schema로 보기/붙여넣기」 토글(원본 「파라미터 (JSON Schema)」 호환, 붙여넣으면 표로 변환하고 변환 못 한 항목은 경고).
- **폼**: 사용자 입력 폼 편집 — 파라미터 순서(끌어 놓기), 섹션, 라벨·도움말·자리 표시자, 표시 조건(`$params.x == …`), 입력 위젯(텍스트·여러 줄·선택·날짜·객체 선택기). 오른쪽에 **실시간 폼 미리보기**(대상 객체 표본 1개를 골라 기본값 평가) [조사 3-5 폼 편집기].
- **규칙**: 순서 있는 규칙 목록(위에서 아래로 실행, 끌어서 순서 변경). 「+ 규칙」: `객체 수정`·`객체 생성`·`객체 삭제`·`링크 생성`·`링크 삭제`·`시스템 호출`.
  - 객체 수정/생성: 대상 객체 표현식, `set` 속성 표(속성 선택 — **`editable` 속성만** 고를 수 있고 아니면 「이 속성은 편집 가능으로 지정되지 않았습니다 — Object type 「편집」 탭에서 켜세요」), 생성 시 링크 연결.
  - **시스템 호출**(원본 단계): slug(「영문 소문자로 시작, 소문자·숫자·밑줄」), 제목, 위로/아래로/삭제, 시스템 선택(「(레지스트리에 없음)」 표시 포함), Operation 선택(`n개`, 「(목록에 없음)」), 「인자 매핑」(키·값·JSON 토글·필수 표시, 「인자 추가」), 「보상(compensation) — 뒤 단계 실패·취소 시 이 단계를 되돌리는 호출」 토글(보상 시스템·Operation·인자 매핑, 안내 `$before.속성`·`$steps.이단계.response.…`·`$cancel.reason`), 보상 끄면 「보상이 없으면 이 단계는 되돌리지 않습니다 (계획 카드에 표시).」 — 모두 원본 문구.
  - **Operation 선택 시 인자 자동 채움**: 원본 규칙 그대로(M1 설계 §4.7). path/query/header → `path.<n>`/`query.<n>`/`header.<n>`, 본문 스키마 → `body.<p>`(배열 항목은 `body.<p>.0.<q>`), 기존 키는 필수 표시만 갱신. 기본값 제안: 전진 — `path.*`→`$this.$key`, `reason`→`$params.reason`, `requestedBy`→`$actor.sub`, `equipmentCode|equipmentId`→`$this.$key`; 보상 — 같은 시스템의 다른 operation이고 path 이름이 `id`/`…Id`면 `$steps.<이 단계>.response.<이름>`, 그 밖 `path.*`→`$this.$key`, `reason`→`$cancel.reason`, `requestedBy`→`$actor.sub`, `status`→`$before.status`. 보상 켤 때 보상 시스템 기본 = 단계 시스템. [제안 추가] `$params.<x>` 제안은 **같은 이름 파라미터가 있을 때만**, 없으면 「파라미터 'x' 추가」 링크.
- **제출 조건** [조사 3-5]: 조건 목록(규칙은 OR — 원본 정책과 같은 의미). 각 조건 = 역할 칩(설정의 실행 역할 목록에서 선택) + 조건식(`when`, 02 §7.5 + `$target`·`$params`·`$actor`) + 실패 메시지(「운송 중인 선적만 처리할 수 있습니다」). 비면 원본 문구 「규칙이 없습니다 — 기본 거부입니다.」 시험: 대상 표본·역할을 골라 「조건 시험」 → 통과/실패 메시지 미리보기.
- **승인**: 「사람 승인」 = 항상 / 조건부(`count($targets) > n` 또는 표현식) / 안 함, 승인 역할, 직무 분리(기본 켬, 03 §4). 원본 「승인 임계치」 입력은 조건부의 n으로 들어간다(안내 원본 계승: 「허용 대상 수가 승인 임계치를 넘으면 사람 승인이 필요합니다. 0 = 항상 승인.」).
- **부수효과**: 알림(앱 안)·웹훅(시스템 operation). 「실행 후 처리되며 실패해도 액션은 성공으로 기록됩니다」. writeback(원본 「성공 시 기록할 속성」: 「(없음)」 + editable 속성, 값 표현식 기본 `$steps.<마지막 단계>.response.<속성>` [확인 필요: 원본이 어떤 값을 쓰는지]).
- **저장 버튼 활성**(원본 조건 확장): 이름 있음, 규칙 ≥1, 모든 시스템 호출 규칙의 slug 규칙·시스템·operation 있음, 켠 보상은 operation 있음, slug 중복 없음, 객체 수정 규칙의 속성이 editable.
- 저장 → 작업본 변경. 문구: 「작업본에 저장했습니다 (v<n>). 발행하면 실행 모듈에 반영됩니다.」 + 경고 목록(원본 경고 문구 그대로, §10). 삭제 확인 「액션 '<이름>' 를 지울까요? 다음 발행에서 사라집니다.」 정의를 고치면 검증 기록을 지운다(원본 규칙).
- **검증(dry-run)** [D-15②]:
  - 「작업본으로 계획 만들기」와 「발행본으로 계획 만들기」 두 버튼(발행본에 이 액션이 없으면 후자 비활성, 툴팁 「발행본에 이 액션이 없습니다」).
  - 조건 줄(원본 그대로: 속성·연산자·값, `in`은 쉼표, 숫자/불리언 자동 해석, is_null/not_null 값 없음), 「파라미터 (JSON)」 또는 폼 미리보기 입력.
  - 결과 카드: F2 계획 카드 컴포넌트를 **보기 전용**으로(허용/거부 건수, 사람 승인 필요 여부, 대상 표, 호출 미리보기, 보상 없는 단계 표시). 작업본 계획은 배지 「작업본 계획 — 실행할 수 없음」, 발행본 계획은 「F2에서 열기」 링크(승인·실행은 F2, 네이티브 창).
  - 허용 ≥1이면 검증 기록(`verifiedAt`, `verifySummary`, `verifiedAgainst: draft|published`).

### 5.10 Function
- 목록: apiName, 종류(query·compute·llm(v2)·sql(고급)), 입력·출력 타입, 사용처 수.
- 상세 [조사 3-6을 편집 가능하게 바꿈]: 입력(이름·타입: 원시·Object·ObjectSet), 출력 타입, 본문:
  - **query**: Object set 편집기(기준 타입/Interface, 필터 행 편집기, 링크 따라가기 단계, 검색, 정렬·제한). 원본 behavior의 「대응 Golden Question」 필드 유지.
  - **compute**: 표현식 편집기.
  - **llm**(v2): 프롬프트·컨텍스트 객체·출력 스키마. 호출은 단일 LLM 클라이언트(04 §3).
  - **sql**(D-07 고급 설정이 켜졌을 때만 보임): 원본 behavior 화면 그대로(파라미터 `{{이름}}`, LIMIT 금지, 필터가 있으면 `{{__base_filter__}}` 필수) + 「테스트 실행」(→ `N건을 조회했습니다.` + 실행 SQL).
- 「테스트 실행」: 입력 값 → 결과 표/객체 목록, 소요 시간. 작업본 기준(발행 전 타입은 미리보기 데이터로).
- 검증: 입출력 타입, 계산 속성 ↔ Function 순환 금지.

### 5.11 Object view 설정 [조사 3-8]
- Object type의 「Object view」 탭: 레이아웃 편집 — 헤더(제목·부제 속성·주요 속성 최대 6개·아이콘), 섹션(속성 묶음), 링크 섹션(Link type별 목록·표시 속성·최대 행), 타임라인(액션 이력·시점 데이터), 액션 버튼(이 타입 대상 Action type 중 선택·순서).
- 오른쪽 미리보기: 객체 표본을 골라 실제 렌더링(작업본 정의 + 미리보기 데이터).
- 발행 후 F2 답변·F4·F5 위젯의 객체 클릭에서 공통으로 쓰인다(02 §13).

### 5.12 Type group · 검색
- **Type group**: 이름·색·멤버(Object type·Link type·Action type 끌어 놓기). 홈 카드에 미니 그래프. 표시용(권한·이름공간과 무관).
- **검색 ⌘K** [조사 3-1]: 대상 = 모든 정의의 displayName·apiName·rid·별칭·설명. 결과 행 = 종류 아이콘·이름·apiName·작업본 표시. 필터 칩(종류). 첫 줄 Enter로 상세 이동. 작업본 기준(삭제 예정은 흐리게).

### 5.13 골든 (Golden questions · commands)
- 원본에서는 브리프 3단계에만 있던 목록을 설계 공간에서도 관리한다(같은 데이터, 02 §15).
- Golden question 행: 질문 원문(**에이전트가 다듬지 않음** — 원본 규칙), 기대 결과(선택: Object set DSL 또는 「답에 포함될 말」 목록), 마지막 결과(작업본/발행본 각각 상태·시각), 「지금 실행」.
- Golden command 행: 원문, 연결 Action type, 기대 계획(선택: 허용 ≥1, 특정 키 포함 등), 마지막 dry-run 결과.
- 「모두 실행(작업본)」 → §7.8 회귀 실행과 같은 동작.

### 5.14 구축 대화 (에이전트 구축) [원본 계승]

#### 5.14.1 브리프 패널 (3단계 — 원본 M1 설계 §4.2 문구·규칙 그대로)
- 단계 버튼 `1 소스`, `2 대상`, `3 의도`, 요약, ✓, 「← 이전」「다음 →」「이 브리프로 구축 시작」 — 원본과 같다.
- **1 소스**: 원본과 같음(문서 업로드, 데이터소스·스키마 칩, 시스템 칩, 경고·안내 문구). 데이터소스 연결 불가 시 문구 「데이터 패브릭에 연결되지 않아 데이터소스를 선택할 수 없습니다. 문서만으로 진행합니다.」는 「데이터소스 서비스에 연결되지 않아…」로 바꾼다(용어 정리, §10). OCR 설정이 켜졌으면 업로드 칩에 「OCR」 배지(D-15⑤).
  - 「테이블 구조로 바로 생성」 상자: 원본 문구·미리보기 표 유지. 버튼 「이대로 생성」→「이대로 작업본에 추가」. 완료 문구 「생성 완료 — 클래스 N개, 관계 M개. 가상 클래스로 바인딩되어 바로 조회할 수 있습니다.」 → 「작업본에 추가했습니다 — Object type N개, Link type M개 (live). 발행하면 조회할 수 있습니다.」(**의도된 차이**: 발행 전 조회 불가). 미리보기 표 머리 `Object type N · Link type M · 속성 K`.
- **2 대상**: 질문 「어느 온톨로지에 담을까요?」, 선택 상자 「새 온톨로지 생성」 + 기존 온톨로지(`<이름> (작업본에 추가)`). 기존을 고르면 그 의도·골든 퀘스천·커맨드로 채움(원본 규칙). 토글 「기존 Object type만 사용」(기본 켬 — 원본 「그 스키마의 클래스만 사용해 추가 인제스천」 계승; 끄면 새 타입 생성 허용). 새 이름 placeholder 「새 온톨로지 이름 (선택, 예: 제조 운영 온톨로지)」.
- **3 의도**: 원본 그대로(초안 상태 줄 문구·「초안 다시 생성」·의도·Golden Question·Golden Command·「파일에서 불러오기」·시작 조건 문구). **권장 전략 상자**: 원본 표시 + 전략 선택 라디오(기본 = 추천). 선택값을 `build_context.strategy`로 보내고 프롬프트 `[전략]` 블록이 된다(§8.2). 쓸 수 없는 전략은 비활성 + 사유. 원본 문구 「권장은 강제가 아닙니다. 이대로 시작해도 다른 전략으로 바꿀 수 있습니다.」 유지.
- **초안 자동 요청 규칙**: 원본 그대로(900ms 디바운스, 생략 조건, 진행 중 요청 취소, 응답 적용 규칙, 사용자 칸 보존·draft 배지, 오류 문구). 초안은 `brief` 모드(읽기 전용) 일회용 대화.

#### 5.14.2 대화창
- 시작 흐름(원본 §4.3): 세션 생성(mode build, 대상 온톨로지 rid 또는 새 이름) → 기존 온톨로지면 브리프 저장 → 사용자 말풍선(빈 입력이면 「구축 의도와 Golden Question을 기준으로 온톨로지 구축 시작」) → 스트림. 빈 프롬프트 기본 문장 「업로드된 문서를 바탕으로 Golden Question에 답할 수 있는 온톨로지를 구축해줘.」 — 원본 그대로.
- 입력란·placeholder·첨부·끼어들기(➤ 「작업 중인 에이전트에게 전달」)·「중단」(「\n[중단됨] "계속해"를 입력하면 이어서 진행합니다.」)·질문 카드(ask_user) — 원본 그대로.
- 어시스턴트 말풍선: 상태 문구, 마크다운 텍스트, 도구 칩(이름·분류 배지·설명·「입력 보기」「결과 보기」·접힘 요약), 출력 파일 버튼, 계획 카드(작업본 dry-run → 보기 전용), 보고서.
- 분류 배지 규칙(새 도구 이름 기준): `ONTOLOGICAL` = `draft_*`·`proposal_*`·`describe_ontology`·`golden_*`; `DATA` = `catalog_*`·`backing_*`·`reverse_bind_*`·`table_ingest`·`document_extract`·`batch_ingest`; `TOOL` = 그 밖(시스템·dry-run·파일·셸).
- 이벤트 반응(§8.4): `draft_update` → 작업본·그래프·상단 변경 수 갱신, `ontology_created` → 세션 온톨로지 기록·필터, `proposal_created` → 상단 제안 칩, `todos` → 진행 상황, `done` → 보고서.
- 메시지 저장 규칙(턴 종료·중단·대화 전환 시 통째로) 원본 그대로.

#### 5.14.3 구축 보고서
- **Golden Question 검수** 카드: 원본 문구·배지(답변 가능 / 부분적으로 답변 가능 / 아직 답변 어려움, 신뢰도 높음/보통/낮음)·「맞다/틀리다」·피드백 입력·「피드백 반영 요청」 활성 조건 — 원본 그대로. 질문마다 「근거 보기」(작업본 질의 결과 객체 목록, §8.3 Phase 3).
- **Golden Command** 표: 열 커맨드 / 액션(`ObjectType.actionApiName`, 없으면 —) / 단계(`a → b`) / 검증(「✓ dry-run(작업본)」·「✓ dry-run(발행본)」·「미검증」). 검증 값은 **저장소 검증 기록**으로 결정(원본 규칙, 에이전트 말 무시).
- 검수 현황 줄: 원본 문구 「🙋 확인이 필요한 내용 **N**건 · 🗂️ 보류 **M**건 — 사람이 판단해야 지식 지도에 들어갑니다.」 + 「검수 탭에서 보기」.
- [신규] 제안 줄: 「📝 변경 제안 #n — 변경 N건 · 검증 오류 a · 경고 b」 + 「제안 화면 열기」. 오류가 있으면 「오류를 고쳐야 발행할 수 있습니다」.

### 5.15 제안 (Proposal) 화면

#### 5.15.1 구성
머리: `제안 #n` 제목(요약 한 줄, 수정 가능), 상태(`열림`·`오래됨(stale)`·`발행됨`·`거절됨`), 만든 주체(사람/에이전트 + 세션 링크), 기준 버전 `v3 → 새 버전`, 버튼 「새로 고침」(작업본 최신으로 다시 계산), 「거절」, 「발행」.

탭 4개:
1. **변경 (diff)**: 정의별 행(종류 아이콘·이름·`추가`/`변경`/`삭제`/`이름 변경`) → 펼치면 필드 단위 before/after(YAML 나란히 보기, 바뀐 줄 강조). 변경 출처(사람/에이전트/가져오기/품질 검수) 표시.
2. **검증**: 02 §17 규칙 결과. 오류(발행 차단)·경고(확인 후 발행) 목록, 각 행에 위치(`ObjectType Shipment › backing[0] › key`)와 「고치러 가기」.
3. **영향 분석**: 삭제·이름 변경·타입 변경·저장 방식 변경·제약 강화의 의존 대상. 행 = 의존 대상(대시보드 위젯, 코드 앱 선언, Function, Action type, Object view, 저장된 Object set, 골든 퀘스천, 에이전트 도구 이름), 영향(「깨짐」/「동작 바뀜」/「재동기화 필요」/「편집 값 n건 버려짐」), 조치 링크. 데이터 영향: 저장 방식 변경·키 변경 시 「indexed 재동기화: 예상 객체 n건」, editable 해제·속성 삭제 시 「편집 레이어 값 n건이 더는 보이지 않습니다」.
4. **골든 회귀**: 질문·커맨드별 「발행본 결과 → 작업본 결과」(통과→통과 / 통과→**실패** / 실패→통과 / 새로 추가). 실패 회귀가 있으면 머리에 빨간 줄.

#### 5.15.2 발행
- 「발행」 → 코어가 발행 요약(변경 수, 경고 수, 깨지는 의존 수, 골든 실패 회귀 수)을 만들고 **셸 네이티브 확인 창**을 연다(03 §4): 「온톨로지 '<이름>'을 v<n>으로 발행합니다. 변경 N건 · 경고 a · 깨지는 의존 b · 골든 실패 c」. 확인 → 승인 증표와 함께 발행 API.
- 검증 오류가 1건이라도 있으면 「발행」 비활성(툴팁 「검증 오류를 먼저 고치세요」).
- 진행 표시: 컴파일 → 그래프 반영 → 실행 모듈 카탈로그 갱신 → 동기화 작업 등록. 실패 시 「발행하지 못했습니다 — 이전 버전(v3)이 그대로 유지됩니다: <원인>」(원자성, 02 §16).
- 성공: 「v4로 발행했습니다.」 + 「동기화 진행 상황 보기」(indexed가 있을 때).
- **에이전트가 만든 제안도 사람만 발행**(03 §4 직무 분리). 사람이 만든 제안은 1인 사용 모드에서 본인이 발행 가능(명시적 클릭 + 증표).

#### 5.15.3 오래된 제안
제안을 만든 뒤 작업본이 바뀌면 상태 `오래됨` + 띠 「제안 이후 작업본이 바뀌었습니다 — 새로 고친 뒤 발행할 수 있습니다」. 발행은 최신 작업본 리비전과 일치할 때만.

### 5.16 이력·되돌리기·내보내기/가져오기 [D-19]
- **이력**: 버전 표(v·발행 시각·발행자·근거 제안·요약·변경 수), 행 선택 → 그 버전 정의 보기(읽기 전용 설계 화면), 「이 버전과 비교」(두 버전 diff).
- **되돌리기**: 「이 버전으로 되돌리기」 → 확인 「작업본의 미발행 변경 N건이 버려지고 v2 내용으로 바뀝니다. 계속할까요?」 → 작업본 = v2 스냅숏 → **되돌리기 제안** 자동 생성(영향 분석·골든 회귀 포함) → 발행은 보통 흐름. 결과 버전은 새 번호(v5 = v2 내용).
- **내보내기**: 대상(발행 버전 선택 또는 「작업본」) → YAML 묶음(zip) 내려받기. 형식 §7.9. 비밀값·자격 증명은 넣지 않음(데이터소스·시스템은 이름으로만).
- **가져오기**: 파일 선택 → 미리보기(온톨로지 이름, 정의 수, 참조하는 데이터소스·시스템 중 이 기기에 없는 것, 이름 충돌) → 대상 「새 온톨로지로」 / 「현재 작업본에 합치기」(충돌 행마다 「가져온 것 사용 / 현재 유지」) → 작업본 변경으로 들어감(출처 = 가져오기). 발행은 보통 흐름.

### 5.17 초기화·삭제 [D-15④]
- 사이드바 「초기화」 → 대화상자 「무엇을 초기화할까요?」 체크:
  - 「이 대화의 작업 파일」(원본 「샌드박스 파일시스템」 — 범위를 현재 대화로 한정)
  - 「이 온톨로지의 미발행 변경(작업본을 발행본으로 되돌림)」
  - 「이 온톨로지의 객체 데이터(native 객체·indexed 사본·편집 레이어·검수 대기열)」
- 「선택 항목 초기화」(아무것도 안 고르면 비활성) → 객체 데이터가 포함되면 **네이티브 확인 창** + 자동 백업(데이터 폴더 `backups/<온톨로지>-<시각>`), 아니면 웹 확인 「다음 항목이 초기화됩니다:\n- …\n\n정말 초기화하시겠습니까?」(원본 문구 형식).
- 정의와 발행 버전은 초기화하지 않는다. 그래프 전체 삭제 기능은 없다(**의도된 차이**).
- **온톨로지 삭제**(「⋯」): 네이티브 확인 + 백업 → 발행 거두기(Object API·도구·액션 카탈로그에서 제거) → 객체 데이터 삭제 → 정의·버전 삭제. 원본의 「스키마 삭제 시 발행물 잔존」 결함 수정.
- 예제 온톨로지는 「⋯ → 예제 다시 만들기」로 복구(시드 경로, §7.10).

### 5.18 상태 점검 (Health) [조사 3-1 Health issues/Cleanup]
작업본·발행본 각각에 대해 문제 목록:
- 깨진 원천(컬럼 사라짐·데이터소스 연결 불가·시스템 operation 없음),
- 사용하지 않는 정의(어디서도 참조 안 되는 Value type·Shared property·Function, 링크·액션 없는 Object type은 정보 수준),
- deprecated 참조, 미검증 Action type(검증 기록 없음), 골든 실패, 보상 없는 다단계 액션, 제출 조건 없는 액션(기본 거부),
- 동기화 실패(indexed), F6 열린 보류 중 정의 원인(없는 링크·속성).
각 행에 「고치러 가기」. 홈 카드와 상단 검증 배지는 이 목록의 요약.

---

## 6. API

- 모두 `/api/v1`, JSON, 세션 토큰 필수(03 §3). 에이전트는 같은 동작을 MCP 도구로만 호출(§8).
- 오류 형식: HTTP 상태 + `{error:{code, message, details?}}`(message는 한국어 문구, §10). 원본은 대부분 200 + `{error}` → **의도된 차이**(비교 테스트는 message 문구와 code로).
- 경로의 `{ont}` = 온톨로지 apiName 또는 rid. 정의 경로의 이름 = apiName(이름이 바뀌어도 rid로도 접근 가능: `…/by-rid/{rid}`).
- 작업본 편집은 **리비전 검사**: 요청 헤더 `If-Match: <revision>`. 맞지 않으면 409 `DRAFT_CONFLICT`.

### 6.1 온톨로지·브리프
| 메서드 경로 | 요청 | 응답 / 비고 | 원본 대응 |
|---|---|---|---|
| GET `/ontologies` | | `{items:[{rid, apiName, displayName, description, intent, publishedVersion, draft{revision, changeCount, updatedAt}, openProposal?{id, number, status}, counts{objectTypes, linkTypes, actionTypes, objects?}}]}` 최근 갱신순 | GET `/api/schemas` |
| POST `/ontologies` | `{apiName, displayName, description?, intent?}` | 온톨로지. 같은 apiName이면 409(원본은 기존 것을 돌려줌 → 의도된 차이, 에이전트 도구는 「이미 있음」을 결과로 받음) | 스키마 그룹 생성 |
| GET/PATCH `/ontologies/{ont}` | PATCH `{displayName?, description?, intent?}` | | GET `/api/schemas/{id}` |
| PUT `/ontologies/{ont}/brief` | `{intent, goldenQuestions[], goldenCommands?[]}` | 커맨드 생략 시 보존(원본 규칙). 작업본 변경으로 기록 | PUT brief |
| DELETE `/ontologies/{ont}` | `{approvalProof}` | §5.17 | DELETE schema (의도된 차이) |
| POST `/ontologies/{ont}/reset` | `{scopes:["files"|"draft"|"objects"], sessionId?, approvalProof?}` | `{backup?, reset{…}}`; objects 포함 시 증표 필수 | 초기화 |

### 6.2 작업본 (draft)
| 메서드 경로 | 요청 | 응답 |
|---|---|---|
| GET `/ontologies/{ont}/draft` | `?kinds=` | 작업본 정의 전체(02 형식) + `revision` |
| GET `/ontologies/{ont}/draft/changes` | | `{revision, items:[{id, rid, kind, apiName, op: add|modify|remove|rename, fields[], actor{kind, id}, sessionId?, source: ui|agent|import|quality|catalog|reverse-bind|seed, at}]}` |
| POST `/ontologies/{ont}/draft/changes/{id}/revert` · DELETE `/ontologies/{ont}/draft/changes` | | 한 변경 되돌리기 / 전체 버리기(= 발행본으로) |
| GET·PUT·DELETE `/ontologies/{ont}/draft/{kind}/{apiName}` | PUT 본문 = 02의 정의 YAML을 JSON으로 | `{definition, revision, validation{errors, warnings}}`. `kind` = `object-types`·`shared-properties`·`value-types`·`link-types`·`interfaces`·`action-types`·`functions`·`object-views`·`type-groups`·`golden-questions`·`golden-commands` |
| PUT·DELETE `/ontologies/{ont}/draft/object-types/{t}/properties/{p}` | | 속성 단위 편집(작은 변경용) |
| POST `/ontologies/{ont}/draft/validate` | `{scope?: rid[]}` | `{errors:[{code, path, message}], warnings:[…]}` |
| POST `/expressions/check` | `{expr, context:{objectType?, source?, params?}, target: live|indexed}` | `{type, errors[], translatable, sample?[]}` |

### 6.3 백킹·미리보기·생성
| 메서드 경로 | 요청 | 응답 | 원본 대응 |
|---|---|---|---|
| POST `/ontologies/{ont}/draft/object-types/{t}/automap` | `{backingId}` | `{suggestions:[{column, property, action: map|create, baseType, pii?}]}` (저장 안 함) | 신규 |
| POST `/ontologies/{ont}/draft/object-types/{t}/preview` | `{limit≤200, backingId?}` | `{objects[], stats{sourceRows, objects, keyNulls, keyDuplicates, enrichmentUnmatched, exprErrors}, issues[{kind, row, message}]}` | 바인딩 샘플·fetch |
| GET `/ontologies/{ont}/draft/object-types/{t}/backing/{id}/drift` | | `{removed[], added[], typeChanged[{column, from, to}]}` | binding/validate |
| POST `/ontologies/{ont}/draft/link-types/{l}/preview` | `{sample≤500}` | `{matchRate, unmatched, multiMatch, cardinalityViolations, examples[]}` | 신규 |
| POST `/ontologies/{ont}/draft/generate-from-catalog` | `{datasource, sourceSchema, tables[], includeLinks=true, storage='live', dryRun}` | `{objectTypes[{apiName, displayName, table, primaryKey, titleKey, properties[{apiName, column, baseType}]}], linkTypes[{apiName, from, to, cardinality, fromColumn, toColumn}], suggestions[], counts{objectTypes, linkTypes, properties}}` / 404 `CATALOG_EMPTY` | generate-from-catalog |
| POST `/ontologies/{ont}/draft/reverse-bind/preview` | `{datasource, sourceSchema, limit=5}` | `{items[{objectType, verdict: auto|needs_review|conflict|no_match, candidates[{table, score, matched[], unmatched[]}]}], uncoveredTables[], unboundTypes[]}` | reverse-bind/preview |
| POST `/ontologies/{ont}/draft/reverse-bind/apply` | `{datasource, sourceSchema, choices[{objectType, table}], includeAuto=true}` | `{counts{bound, skipped, unbound}, changes[]}` | reverse-bind/apply |
| GET `/build/strategy/recommend` | `?hasDocuments&datasource&schema&intent&maxLag=2` | `{inputs, recommended, reason, available[], unavailable[{strategy, reason}]}` — 원본과 같은 키·값 | build-strategy/recommend |
| POST `/build/brief-draft` | `{datasources[{name, schemas}], documents[], targetOntology?, intent, goldenQuestions[]}` | `{intent, questions[{question, evidence}], note, error}` — 원본과 같은 키, 실패도 200 + error(원본 계약 유지: 화면이 이 형식에 의존) | build-brief/draft |

### 6.4 Action type·Function·골든
| 메서드 경로 | 요청 | 응답 |
|---|---|---|
| POST `/ontologies/{ont}/draft/action-types/{a}/autofill` | `{ruleIndex, system, operation, compensation?:bool}` | `{args:[{key, value, required}]}` (§5.9 규칙) |
| POST `/ontologies/{ont}/draft/action-types/{a}/dry-run` | `{against: draft|published, where[{property, op, value}], params{}}` | `{planId, draft:bool, status, requiresApproval, allowed, denied, allowedKeys(10), deniedReasons(5), previewCalls, where, params, verified}` — 원본 요약 키 유지 |
| POST `/ontologies/{ont}/draft/functions/{f}/test` | `{inputs}` | `{columns?, rows?, objects?, rowCount, elapsedMs, sql?}` |
| POST `/ontologies/{ont}/golden/run` | `{against: draft|published, ids?[]}` | `{runId, results[{rid, kind, status: pass|fail|error|unknown, answer?, evidence[], plan?{allowed, denied}, previous?}]}` |

### 6.5 제안·버전·내보내기
| 메서드 경로 | 요청 | 응답 |
|---|---|---|
| POST `/ontologies/{ont}/proposals` | `{summary}` | 제안 `{id, number, status, baseVersion, draftRevision, createdBy{kind, id}, diff[], validation{}, impact[], golden{}}`. 열린 제안이 있으면 그것을 새로 고쳐 돌려줌(D-08: 1개) |
| GET `/ontologies/{ont}/proposals[?status]` · GET `/proposals/{id}` | | |
| POST `/proposals/{id}/refresh` · POST `/proposals/{id}/reject` | `{reason?}` | |
| POST `/proposals/{id}/publish` | `{approvalProof}` | `{version, publishedAt, compile{objectTypes, linkTypes, actionTypes, functions, syncJobs[]}, warnings[]}` / 403 `APPROVAL_PROOF_REQUIRED` / 409 `PROPOSAL_STALE` / 422 `VALIDATION_FAILED` / 500 `PUBLISH_FAILED`(이전 버전 유지) |
| GET `/ontologies/{ont}/versions` · GET `/versions/{n}` · GET `/versions/{a}/diff/{b}` | | |
| POST `/ontologies/{ont}/rollback` | `{toVersion}` | 되돌리기 제안 |
| GET `/ontologies/{ont}/export` | `?version=n|draft` | `application/zip` (YAML 묶음) |
| POST `/ontologies/import` | multipart `file`, `mode: new|merge`, `target?` | `{ontology, changes[], conflicts[], missingRefs{datasources[], systems[]}, warnings[]}` |
| GET `/ontologies/{ont}/search` | `?q&kinds&scope=draft|published` | `{items[{rid, kind, apiName, displayName, match}]}` |
| GET `/ontologies/{ont}/dependents` | `?rid` | `{items[{kind, id, name, via}]}` |
| GET `/ontologies/{ont}/health` | `?scope=draft|published` | `{items[{severity, code, rid?, message}]}` |

### 6.6 대화·파일 (P 명세·04와 공유)
원본 계약을 경로만 `/api/v1`로 옮겨 유지: 세션 목록·생성·수정·삭제·메시지 저장/복원(mode별), 스트림(`mode=build`, `build_context`), steer·running·reset, 업로드·파일 목록·삭제·보기·내려받기. `build_context` 형식은 §8.2.

### 6.7 원본 API → 새 API (요약)
| 원본 | 새 |
|---|---|
| GET `/api/schema`, `/api/schemas` | GET `/ontologies`, `/ontologies/{ont}/draft` |
| PUT `/api/schema/classes`, `/relationships` | PUT `/draft/object-types/{t}`, `/draft/link-types/{l}` |
| `/api/schema/classes/{c}/binding` | Object type `backing`(PUT 정의) + automap·preview·drift |
| `/api/schema/classes/{c}/behaviors` | `/draft/functions` (query, sql 고급) |
| `/api/schema/classes/{c}/actions/{a}` | `/draft/action-types/{a}` |
| POST `/api/schema/{id}/publish` | POST `/proposals/{id}/publish` (증표 필요) |
| `/api/release/*` | `/versions`, `/export`, `/import` |
| `/api/graph/*` (엔티티 CRUD) | 읽기는 Object API(01 §4), 쓰기는 Action type |
| POST `/api/graph/nl-query` | F4 그래프 콘솔 자연어 질의(단일 LLM 클라이언트) |
| POST `/api/neo4j/clear-all` | 없음 → POST `/ontologies/{ont}/reset` |

---

## 7. 데이터

개념은 02 문서를 그대로 쓴다. 이 절은 F1이 추가로 정하는 저장 단위와 결정적 규칙이다. 저장 위치는 `workbench.meta`(정의·작업본·제안·버전), `workbench.runtime`(세션·build_context·골든 실행 결과), `workbench.audit`(01 §3).

### 7.1 작업본·변경·제안·버전
```yaml
Draft:      { ontologyRid, revision: int, definitions: {rid: Definition}, updatedAt }
DraftChange:{ id, ontologyRid, rid, kind, op: add|modify|remove|rename, before, after,
              actor: { kind: human|agent|system, id }, sessionId?, source, at }
Proposal:   { id, number, ontologyRid, status: open|stale|published|rejected,
              baseVersion, draftRevision, summary, createdBy, diff, validation, impact,
              golden: { runId, results }, publishedVersion?, approvalProofId? }
Version:    { ontologyRid, number, snapshot: {definitions}, compiledArtifacts, publishedAt,
              publishedBy, approvalProofId, proposalId, kind: normal|rollback|seed }
```
- 작업본 1개·열린 제안 최대 1개(D-08). 제안은 작업본의 **리비전**을 가리키고 스냅숏을 따로 두지 않는다(stale 판정용 해시만).
- 버전 스냅숏은 불변. 되돌리기는 스냅숏 → 작업본 복사.
- 사람 변경과 에이전트 변경은 `actor.kind`로 구분(감사 01 §7).

### 7.2 출처 (provenance)
원본 출처 기록(`element_kind`, `strategy`, `evidence_kind`, `evidence_ref`, 처음 기록 우선)을 정의 단위로 유지: `{rid, path?, strategy: doc_reverse_bind|causal_discovery|catalog_schema|document_only|manual|agent|quality_review|import|seed, evidenceKind: document|foreign_key|statistical|human|catalog, evidenceRef, at}`. 설계 화면 상세 머리 「출처」 툴팁에 표시.

### 7.3 build_context (세션별)
원본 형식에 새 키를 더한다: `{intent, golden_questions[], golden_commands[], review_feedback[{question, answer, status, verdict, feedback}], datasources[{name, schemas[]}], documents[파일 이름], systems[], target_ontology | new_ontology_name, existing_types_only: bool, strategy}`. 원본 키 `target_schema`/`new_schema_name`은 받아서 새 키로 바꾼다(호환). 저장·복원 규칙(의도·질문·커맨드 중 하나라도 있으면 저장, 없으면 복원)은 원본 그대로.

### 7.4 이름 변환 규칙 (원본 이름 → 02 이름 규칙)
- Object type apiName: 원본 클래스 이름 규칙 그대로(영숫자 아닌 문자로 나눠 각 조각 첫 글자 대문자, 전부 대문자 조각은 Title 처리: `mfg_daily_equipment`→`MfgDailyEquipment`). 숫자로 시작하면 앞에 `T`.
- Property apiName: 컬럼 이름을 같은 방식으로 나눠 첫 조각 소문자 + 나머지 Title(`supplier_id`→`supplierId`, `ETA`→`eta`). 충돌 시 뒤에 `2`, `3`. 매핑 표현식은 원래 컬럼 이름.
- Link type: apiName = `<from 타입 camel><To 타입>`(`purchaseOrderSupplier`), from 방향 이름 = to 타입 camel(`supplier`), to 방향 이름 = from 타입 camel 복수(`purchaseOrders`; 규칙: `y`→`ies`, `s|x|ch|sh`→`es`, 그 밖 `s`). 한 쌍에 FK가 여럿이면 from 방향 이름 = 컬럼 기반(`vendorCode`→`vendor`) [제안]. 원본 관계 이름(`REFERENCES_<…>`, 예제의 `ORDERED_FROM` 등)은 **별칭**으로 남겨 비교·검색에 쓴다.
- 표시 이름: 테이블·컬럼 설명이 있으면 그것, 없으면 원본 규칙의 「사람 읽기 이름」.

### 7.5 카탈로그 일괄 생성 규칙 (LLM 없음, 원본 §7.7을 새 모델로)
- 입력·오류: 원본과 같음. 테이블이 없으면 404 `CATALOG_EMPTY` + 「카탈로그에 '<ds>' / '<schema>' 테이블이 없습니다. 데이터소스 화면에서 메타데이터 추출을 먼저 실행하세요.」(용어만 변경).
- 테이블 → Object type(`storage: live`, 주 원천 table, `filter` 없음), 설명 = 테이블 설명 또는 `<사람 읽기 이름> (<schema>.<table>)`.
- 컬럼 → Property(모두 매핑), 타입 매핑 [원본 → 새]:

| 원본 판정 | 원본 타입 | 새 baseType |
|---|---|---|
| bool | boolean | boolean |
| int, serial | integer | integer (bigint·bigserial은 `long` [제안]) |
| numeric, decimal, money | float | **decimal** |
| float, double, real | float | double |
| timestamp, datetime | date | **timestamp** |
| date | date | date |
| time | date | string [제안] |
| 그 밖 | string | string |

- 기본 키 = PK 컬럼들(복합 허용 — 원본은 키 목록을 받았으나 02 §5에서 복합 키를 정식 지원). PK가 없으면 Object type을 만들되 검증 오류 「기본 키가 없습니다」로 남겨 사람이 고르게 한다(원본은 키 없이 바인딩) [의도된 차이].
- 제목 속성 = 원본 라벨 속성 규칙(name/title/label/code/description 또는 `_<그것>`으로 끝나는 순, 없으면 PK 첫 컬럼, 없으면 첫 컬럼).
- FK → Link type(`foreign-key`, `fromExpr` = FK 컬럼, `toProperty` = 대상 PK 속성), 카디널리티 = FK 컬럼이 유일하면 one-to-one, 아니면 many-to-one. 같은 (from, to, 컬럼)은 하나. 복합 FK는 v1에서 만들지 않고 `suggestions`에 「복합 외래키는 수동으로 만드세요」.
- 원본의 `reference:true`(PK 아닌 `_id/_no/_code/_key` 접미 컬럼)는 FK 제약이 없으면 **링크 후보**로 `suggestions`에 넣는다(만들지 않음).
- 출처 `catalog_schema/foreign_key`(링크), `catalog_schema/catalog`(타입).
- 결과는 작업본 변경(source `catalog`). 같은 apiName이 이미 있으면 건너뛰고 `suggestions`에 「이미 있음」.

### 7.6 역바인딩 점수 (원본 §7.8 그대로)
document 주 원천 Object type마다 카탈로그 테이블 후보 점수 = 열 일치 0.6 + 타입 일치 0.2 + 이름 토큰 겹침 0.2(설명도 일치 대상). 비교 대상 = Object type의 속성 apiName·표시 이름·별칭 ↔ 컬럼 이름. 판정 `auto`/`needs_review`/`conflict`(두 타입이 같은 테이블)/`no_match`, `auto`만 기본 적용. 임계값 [확인 필요 — 원본 M1 설계 §14-3]. 매칭 없는 타입은 지우지 않는다.

### 7.7 전략 추천 결정 표 (원본 §7.6 그대로)
입력·조건 순서·추천·이유 문구·`available`/`unavailable` 사유·최소 행 수(max_lag×2+10)를 **바꾸지 않는다**. 전략 표시 이름도 원본 그대로(`doc_reverse_bind`=「문서 엔티티 → 데이터소스 역바인딩」, `causal_discovery`=「데이터에서 인과 발견」, `catalog_schema`=「테이블 구조 그대로 매핑」, `document_only`=「문서 기반 (인스턴스 적재)」, `none`=「입력 부족」). 인과 발견 기능이 없는 v1에서는 시계열 준비 판정이 「통계 서비스에 연결할 수 없습니다」를 돌려준다(원본 패키지에서 통계 서비스가 없을 때와 같은 결과 [확인 필요]).

### 7.8 골든 회귀 실행
- 질문: 기대 결과가 Object set이면 작업본/발행본 컴파일 결과로 실행해 **객체 키 집합 비교**(같음 = pass). 「답에 포함될 말」이면 `answer` 모드 에이전트 1회(대상 = 작업본 미리보기 또는 발행본) 후 포함 검사. 둘 다 없으면 에이전트 판정(answerable/partially/not_yet)을 `unknown`·`pass`·`fail`로 사상(answerable = pass, not_yet = fail, partially = unknown).
- 커맨드: 연결 Action type dry-run(작업본) → 허용 ≥1이고 `expectedPlan` 조건을 만족하면 pass. Action type이 없으면 fail 「액션이 만들어지지 않았습니다.」(원본 문구).
- 결과는 `lastResult`로 저장하고 제안의 「골든 회귀」 탭에서 발행본 마지막 결과와 비교.
- 에이전트 판정을 쓰는 실행은 비결정적이다 — 회귀 표시는 「참고」로, 결정적 검사(Object set·dry-run)만 빨간 줄 대상.

### 7.9 내보내기 YAML 형식 [D-19]
```
<ontology-apiName>-v<n>.zip
  ontology.yaml          # format: workbench-ontology/1, apiName, displayName, description, intent, version, exportedAt
  object-types/<Name>.yaml   # 02 §5 ObjectType (backing 포함, 데이터소스·시스템은 이름 참조)
  link-types/<name>.yaml · interfaces/ · shared-properties/ · value-types/
  action-types/<name>.yaml · functions/<name>.yaml · object-views/<Type>.yaml
  type-groups.yaml · golden.yaml
```
- rid는 보존(같은 기기 재가져오기 시 같은 정의로 인식), 다른 온톨로지로 가져오면 새 rid 발급 + 원본 rid를 `importedFrom`에.
- 자격 증명·비밀 참조·객체 데이터·편집 레이어·검증 기록은 넣지 않는다. 키는 사전순, 줄 끝 LF(Git 비교 쉬움).

### 7.10 예제 온톨로지 「공급망 운영 (예제)」 (시드, 비교 기준)
원본 M1 설계 §10을 새 모델로 옮긴다. **사람이 화면으로 만든 것과 같은 경로**(작업본 편집 API → 제안 → 발행 → dry-run)를 거친다. 발행 증표 대신 `actor.kind = system`, `Version.kind = seed`로 감사에 남긴다(03 §4의 예외로 명시 — §12 열린 질문).
- 온톨로지: apiName `SupplyChainSample`, 표시 이름 `공급망 운영 (예제)`, 설명·의도 원본과 같음. 골든 퀘스천 3, 골든 커맨드 4(원본과 같은 문장).
- Object type 7: Supplier·Item·PurchaseOrder·Shipment·Customer·SalesOrder·Claim, 원본 속성을 §7.4 규칙으로(`supplier_id`→`supplierId` …), 키·타입 원본과 같음(float → `amountUsd`는 decimal). **저장 방식 indexed**(원천 = 예제 erp/wms/crm 테이블) — 원본이 인스턴스를 그래프에 적재하고 writeback이 속성을 바꾸던 동작을 재현하기 위해. editable: Shipment.`priority`, PurchaseOrder.`status`.
- Interface `Partner`(공유 속성 `name`, `country`) — Supplier·Customer 구현(02 §7.2).
- Link type 6: 원본 관계를 foreign-key로(`purchaseOrderSupplier`(별칭 ORDERED_FROM), `shipmentPurchaseOrder`(SHIPS, fromExpr `ref_po_no`), `shipmentSupplier`(SHIPPED_BY, `vendor_code`), `salesOrderCustomer`(PLACED_BY), `salesOrderItem`(FOR_ITEM, `sku_code`), `claimSalesOrder`(ABOUT)), 모두 many-to-one. 대상 키가 없는 값은 잇지 않음.
- Action type 3: 원본 정의를 §8.3 사상 규칙으로 변환(`expediteShipment` 2단계 wms→erp + 보상, 제출 조건 `$target.shipStatus != 'DELIVERED'`「입고가 끝난 선적은 제외」, 역할 `scm_operator`, 승인 항상(원본 threshold 0), maxTargets 20, writeback `priority` / `holdPurchaseOrder` / `notifyCustomer`). dry-run 조건·파라미터 원본과 같음(`delayDays > 3` …), 3건 모두 verified여야 시드 성공(아니면 다음 시작에 재시도 — 원본 규칙).

---

## 8. 에이전트 연동

### 8.1 모드·도구 (04 §4·§6)
- 구축 턴 = `build`, 초안 = `brief`(읽기 전용, 원본 `brief_draft`), 문서 추출 내부 = `extract`(F6).
- `build` 모드 도구 (04 §6 + 이 명세가 추가 제안하는 것 ★ — 04 문서 반영 필요):

| 묶음 | 도구 | 원본 대응 |
|---|---|---|
| 작업본 읽기·편집 | `draft_get`, `draft_upsert_object_type`, `draft_upsert_property`, `draft_upsert_link_type`, `draft_upsert_backing`, `draft_upsert_action_type`, `draft_upsert_function`, ★`draft_upsert_interface`, ★`draft_upsert_value_type`, ★`draft_set_brief`, `draft_validate` | `schema_*`, `class_*binding*`, `behavior_*`, 액션 저장, 스키마 그룹 |
| 제안 | `proposal_create(summary)` | `schema_publish`(대체) |
| 데이터 | `catalog_list/describe`, `backing_preview(objectType)`, ★`generate_from_catalog(dryRun)`, `reverse_bind_preview`, ★`reverse_bind_apply`(auto만, 결과는 작업본) | 데이터소스 도구, generate-from-catalog |
| 전략 | `strategy_recommend` | 같음 |
| 문서·적재 | `document_extract(fileId, targetTypes)`(F6 `extract_triples` 후계), ★`table_ingest`(F6), ★`batch_ingest`(파서 출력, F6 §5.6 선별) | 같음 |
| 시스템 | ★`system_list`, ★`system_operations`, ★`system_query`(GET만, `save_path`는 작업 폴더 `output/` 아래만) | 같음 |
| 검증 | `action_dry_run(actionType, where, params)`(작업본 기본), ★`golden_run(against)`, ★`draft_query(objectSet)`(작업본 미리보기 질의) | `action_dry_run`, 읽기 Cypher |
| 품질 | ★`quality_checkup`, ★`quality_report` (F6) | 같음 |
| 파일 | 작업 폴더 안 읽기/쓰기(04 §7), 셸은 D-10 | CLI 자체 도구 |

- **없는 도구**(의도된 권한 경계): 발행, 제안 승인, 되돌리기, 초기화, 온톨로지 삭제, 액션 승인·실행, 품질 결정·재처리, 원천 쓰기 SQL.
- 도구 결과 크기 상한(30행·200행·60000자 등)과 `truncated` 표시는 04 §5 그대로.

### 8.2 구축 프롬프트 조립 (원본 §6.2 계승)
값이 있는 라벨 블록만 빈 줄로 잇는다. 순서와 이름(변경 표시 ▲, 신규 ★):
```
[사용자 작업 요청] · [구축 의도] · [연결 데이터소스] · [업로드 문서]
[대상 온톨로지]▲ 또는 [새 온톨로지 이름]▲   (+ 「기존 Object type만 사용」이면 한 줄 「새 Object type을 만들지 않는다」)
[전략]★ <전략 코드> — <표시 이름>
[작업본 요약]★ Object type n · Link type m · Action type k · 열린 제안 #p(있으면)
[골든 퀘스천] · [연결 시스템] · [인스턴스 원천]
[실행 역할] — 액션 제출 조건 roles 에는 이 이름만 쓴다▲
[골든 커맨드] · [검토 피드백]
```
- 업로드 문서 경로 표기는 작업 폴더 상대 경로(`uploads/<이름>`). 절대 경로를 프롬프트에 넣지 않는다(03 §9).
- 지시문은 프롬프트에 섞지 않는다(스킬 파일 하나가 원천). 이어가기 프롬프트 라벨도 원본 그대로, `[현재 그래프 상태]`는 `[작업본 요약]`으로 대체.
- 실행 역할 목록은 F8 설정(원본 예제 값 `scm_operator` 유지).

### 8.3 구축 스킬 — 단계와 규칙 (원본 §6.5를 작업본·제안으로 재정렬, 원문 복사 금지)
공통 규칙은 원본 그대로 계승: 전제 도구 없으면 멈춤, 입력 점검(빠진 것만 구체적으로, 되묻기 최대 2회, 받은 것 다시 묻지 않기, **골든 문장 다듬기 금지**), 골든 퀘스천이 전부를 결정, 모든 업로드 파일 먼저 탐색, 검증은 실제 실행, **타입은 사물·Function은 질문**, **링크 0개는 미완성**(반복 키 = 빠진 링크), 단계마다 한국어 설명. 이름 규칙은 02 §3(PascalCase / camelCase).

- **Phase 1 설계** — `strategy_recommend` → (사용자가 고른 `[전략]` 우선) → 질문별 필요한 Object type·Link type·Function 도출 → 데이터소스가 있으면 실제 카탈로그로 저장 방식 판정(원천 그대로 읽으면 live, 다원천·편집·검색이 필요하면 indexed, 원천 없으면 native) → 작업본에 정의. 설계 기록 `output/_schema_design.json`(원본 형식, `classes`→`objectTypes`, `resolution: graph|behavior|hybrid`→`objectSet|function|hybrid`).
- **Phase 2 연결·적재** — 데이터소스: `draft_upsert_backing` → `backing_preview`로 키 결측·중복·식 오류 0 확인 → Link type(foreign-key, 필요하면 변환 표현식) → 질문마다 Function(query). 문서: 문장 사실 → `document_extract`, 표 → `table_ingest`(원천 규칙 필수), 구조 문서 → 파서 작성·실행(D-10 동의 필요) → `batch_ingest`. 모두 F6 품질 게이트를 지난다. live·indexed 타입에 문서 사실을 넣으려면 document 원천을 enrichment로 먼저 연결.
- **Phase 2.5 골든 커맨드 → Action type** (원본 규칙 계승, 새 필드로 사상):
  - 시스템만 재료일 때: `system_query`로 GET 목록 조회 → 응답 필드를 속성으로 → **system 원천의 indexed Object type**(원본: materialized 적재) → `backing_preview`로 건수 확인.
  - `system_list` → `system_operations` 탐색. 시스템이 없거나 실행 모듈 불통이면 지어내지 말고 「시스템 등록」(F7) 안내 후 건너뜀. 커맨드를 업무 흐름으로 풀어 여러 `callSystem` 규칙으로.
  - 대상: Object type(저장 방식 무관). 단 `modifyObject`/writeback은 indexed·native의 editable 속성만 — live면 시스템 호출만으로 구성하고 writeback 없음(원본은 「virtual 대상이면 알리고 적재 제안」 → 새 모델은 live도 대상 가능, **의도된 차이**).
  - 보상 고르기: 원본 규칙 그대로(같은 시스템 cancel/revert/restore/undo/delete 계열, 상태 덮어쓰기면 같은 operation + `$before.<속성>`, 만든 리소스는 `$steps.<단계>.response.id`, 되돌릴 수 없으면 보상 없이 설명에 명시). **취소형 커맨드**(정규식 `취소|되돌|원복|원래대로|롤백|undo|cancel`)는 새 액션이 아니라 앞 액션의 보상으로 충족.
  - 새 레코드를 만드는 커맨드는 기준정보 Object type을 대상으로, 나머지는 파라미터로.
  - 사상 규칙: 원본 `policy[{roles, when, description}]` → `submissionCriteria[{roles}, {when, message: description}]`; `confirm_threshold` 0 → `approval.required: true`, n≥1 → `approval.required: {when: "count($targets) > n"}`(일상 1~3, 되돌리기 어려우면 0 — 원본 기본값 지침); `max_targets` → `target.maxTargets`(20~50); `writeback_property` → `writeback.property`(보통 `status`); `golden_command` → `goldenCommand`(원문); `key_property` → 기본 키(`$this.$key` 유지); `steps` → `rules.callSystem`; `parameters`(JSON Schema) → `parameters[]`.
  - 검증: 커맨드마다 `action_dry_run`(작업본, 조건을 구조화 필터로). 허용 0건이면 원인 점검 후 최대 3회. 정의를 고치면 검증이 지워지므로 **맨 마지막에 다시 dry-run**, 보고 전 검증 기록 빈 Action type이 없는지 확인. 취소형은 모든 단계의 보상 존재로 검증(일부 없으면 「부분 취소만 가능」). 실행·승인 안 함.
- **Phase 3 검증** — `golden_run(against=draft)` 또는 `draft_query`로 질문마다 실제 실행, PASS/FAIL, FAIL이면 스키마/데이터/Function 갭으로 분류해 Phase 1·2로(최대 3회). 검색 힌트 `output/_search_hints.json`(원본 형식).
- **Phase 4 검수** — `quality_checkup` 1회 → 사람이 판단할 건수·원인 3~5줄, 정의로 풀리는 보류면 고칠 방법 제안. 승인·기각·재처리·규칙 완화 금지(원본 그대로).
- **Phase 5 제안** ★ — `draft_validate` 오류 0 확인 → `proposal_create(summary)` → 보고서에 제안 번호. 사용자가 「발행해 줘」라고 하면 같은 흐름 후 「제안 #n을 만들었습니다 — 위의 「발행」에서 검토 후 발행하세요.」로 답한다(**발행 도구 없음**).
- 완료 기준: 원본 + 「검증 오류 0인 제안이 있음」.

**브리프 초안 스킬**: 원본 그대로(근거 없는 질문 금지, 소스를 실제로 봄, 의도 한 문단, 질문 3~5개+근거, `ontology_brief_draft` 블록 하나, 블록 없거나 깨지면 빈 초안). 입력 라벨 `[대상 스키마]`→`[대상 온톨로지]`.

### 8.4 SSE 이벤트 (A3 기본 계약 + F1)
- 기본(원본 유지): `status`, `token`, `tool_start{description}`, `tool_result`, `ask_user`, `skill_loaded`, `ref_file`, `todos`, `done`, `error_event`. 시작 문구 원본 그대로(`온톨로지 구축 에이전트를 시작합니다... (<n>개 Golden Question)` / `이전 대화를 이어서 진행합니다...`).
- `tool_start.description` 한국어 한 줄: 파일·셸 문구는 원본 그대로, 새 도구는 「Object type '<name>' 을 작업본에 저장합니다」, 「Link type '<name>' (<from> → <to>)를 정의합니다」, 「'<type>' 백킹 데이터를 미리 봅니다」, 「액션 '<name>' 을 작업본 기준으로 dry-run 합니다」, 「변경 제안을 만듭니다」, 그 밖 「<tool> 도구를 실행합니다」.
- F1 부수 이벤트(도구 결과 봉투를 벗긴 뒤):
  - `draft_update{tool, revision, changes[{rid, kind, op}]}` — 작업본을 바꾼 도구 뒤 (원본 `neo4j_update` 대체 ▲)
  - `ontology_created{ontology, rid}` (원본 `schema_created` 대체 ▲)
  - `backing_update{tool, objectType, rows?, elapsedMs?, error?(300자)}` (원본 `datasource_update` 대체 ▲)
  - `kinetic_plan{plan_id, status, requires_approval, tool, draft: true}` (원본 유지 + `draft`)
  - `proposal_created{id, number, status}` ★
  - `ref_file`·출력 파일 규칙은 원본 그대로(경로는 작업 폴더 상대).
- 종료 직전 `todos`: 원본 4단계 + `{id:'proposal', content:'Phase 5: 변경 제안'}`. 이어서 `done{message:'완료!', files, text, build_report}`.

### 8.5 보고서 추출 (원본 §6.4 계승)
- 블록 탐색(`ontology_build_report` 펜스 → `golden_questions`/`golden_commands` 키를 가진 마지막 json 블록), 질문 정규화, 커맨드 정규화(번호 제거, 저장소에서 찾기, 취소형 규칙, 「액션이 만들어지지 않았습니다.」), **`verified` = 저장소 검증 기록 존재**, steps 기본값 — 원본 규칙 그대로.
- 필드 이름: 커맨드 항목 `{command, objectType, action, steps, verified, verifiedAgainst, note}` (원본 `class`도 읽어서 `objectType`으로).
- 브리프 커맨드를 온톨로지에 저장(비어 있을 때만) — 원본 규칙.
- `quality` = F6 review-status(대상 = 세션 온톨로지, 없으면 이번 턴 도구 인자의 마지막 온톨로지).
- `proposal` ★ = 이 세션이 만든 열린 제안 `{id, number, status, errors, warnings}`(백엔드가 붙임, 에이전트 말 무시).

### 8.6 셸 도구 (D-10)
문서 파서 실행이 필요할 때 에이전트가 `ask_user`로 「문서 파서를 실행하려면 이 대화에서 셸 명령을 허용해야 합니다. 허용할까요?」를 묻고, 사용자가 허용하면 그 세션의 다음 턴부터 셸 도구를 켠다(작업 폴더 안, 화이트리스트 환경, 03 §5). 거절하면 `document_extract`(LLM 추출)로 대체.

---

## 9. 보안·권한

| 항목 | 규칙 | 근거 |
|---|---|---|
| 발행·되돌리기 발행·온톨로지 삭제·객체 데이터 초기화 | 셸 네이티브 확인 창 + 일회용 승인 증표. 증표 없으면 403 `APPROVAL_PROOF_REQUIRED` | 03 §4, D-15③④ |
| 에이전트 권한 | build 모드 도구는 작업본 편집·제안 생성·dry-run·읽기. 발행·승인·삭제·초기화·품질 결정 도구 없음. 턴별 MCP 토큰은 이 도구 집합에만 유효 | 04 §4, 03 §5 |
| 직무 분리 | 에이전트가 만든 제안은 사람만 발행. 감사: `createdBy.kind=agent`, `publishedBy.kind=human`, `proof` | 03 §4 |
| 작업본 dry-run | 계획은 `draft:true`로 표시, 승인·실행 API가 거부(F2) | D-15② |
| SQL 원천 | 단일 SELECT만(구문 분석), DDL/DML·여러 문장·주석 속 문장 거부, `fabric_ro` 역할, 시간 제한. SQL Function은 고급 설정(D-07) | 03 §6, D-15① |
| 표현식 | 02 §7.5 문법만 해석(임의 코드 실행 없음), 함수 화이트리스트 | 02 §7.5 |
| 파일 | 업로드 이름 정규화(경로 구분자·`..` 제거), 대화 작업 공간 아래만, 심볼릭 링크 무시. 도구의 파일 경로는 작업 폴더 상대만, 절대 경로 거부 | 03 §9 (원본 결함 수정) |
| 가져오기 | YAML 안전 로딩(태그·별칭 확장 제한), 파일 10MB·정의 5000개 상한, 모든 정의 검증 후 작업본에. SQL 원천은 SQL 검증 통과해야 함 | [제안] |
| 내보내기 | 비밀·자격 증명·객체 데이터 제외 | 03 §7 |
| PII | PII 속성은 에이전트 도구 결과·미리보기 도구에서 값 마스킹(이름만) | 04 §5 |
| 이름 조회 | 온톨로지·정의 이름은 **정확 일치만**(원본 부분 일치 결함 수정) | M1 설계 §13-3 |
| 적재 시 정의 보존 | 적재·추출 도구는 정의를 덮어쓰지 않는다(정의 변경은 `draft_*`만) | M1 설계 §13-4 |
| 감사 | 작업본 변경(actor·source), 제안 생성·거절, 발행(증표), 초기화·삭제(백업 위치)를 `audit`에 | 01 §7 |

---

## 10. 오류·예외

| 상황 | 동작 / 문구 | 원본 문구 유지 |
|---|---|---|
| 브리프 미완 | 시작 버튼 비활성 + 「구축 의도와 Golden Question을 최소 1개 입력하면 구축을 시작할 수 있습니다.」 | 유지 |
| 초안 실패 | 200 + error, 「초안을 만들지 못했습니다 — 직접 입력해서 그대로 진행할 수 있습니다.」 등 원본 문구 전부 | 유지 |
| 에이전트 오류·중단 | `error_event` → 「\n오류: <message>」, 「[중단됨] …」 | 유지 |
| 데이터소스 서비스 불통 | 데이터소스 영역 숨김 + 안내, 백킹 저장 시 컬럼 검증 건너뜀 문구 | 「데이터 패브릭」→「데이터소스 서비스」 용어만 변경 |
| 액션 실행 모듈 불통 | 정의 저장(경고), 편집기 경고 띠, dry-run 불가, 에이전트는 시스템 단계 건너뜀 | 서비스 이름만 변경 |
| Action type 검증 오류(422) | 원본 문구 그대로: 「액션 이름 '<n>' 은(는) 쓸 수 없습니다. …」, 「system(서비스 레지스트리 이름)이 비어 있습니다.」, 「operation_id 가 비어 있습니다.」, 「steps[i].name '<n>' 은(는) 쓸 수 없습니다. …」, 「단계 이름 '<n>' 이(가) 중복됩니다.」, 「…: $cancel.reason 은 보상(compensation) 매핑에서만 씁니다.」, 「…: '<s>' 단계를 참조할 수 없습니다 (앞 단계만 — 보상은 자기 단계까지).」, 「…표현식 '<expr>' 의 뿌리를 알 수 없습니다. …」, 「단계 '<s>' 인자 '<k>' 의 JSON 값이 올바르지 않습니다.」, 「파라미터 JSON 오류: <msg>」. 위치는 `rules[i]` 기준으로 표기 | 유지(위치 표기만 확장) |
| 원본 정책 키 오류 | 「policy[i] 에 알 수 없는 키가 있습니다: …」는 JSON 가져오기(원본 형식) 때만, 화면은 조건 편집기라 발생 안 함 | 가져오기 경로만 |
| Action type 저장 후 경고 | 원본 문구 그대로: 「<라벨>서비스 레지스트리에 시스템 '<s>' 이(가) 없습니다.」, 「<라벨>시스템 '<s>' 에 operation '<op>' 이(가) 없습니다.」, 「<라벨>operation 을 확인하지 못했습니다 (<msg>).」, 「보상이 없는 단계가 있습니다 — 뒤 단계가 실패하거나 취소해도 되돌리지 않습니다: a, b」, 「policy 규칙이 없어 아무도 이 액션을 실행할 수 없습니다(기본 거부).」→「제출 조건이 없어 아무도 이 액션을 실행할 수 없습니다(기본 거부).」 | 마지막만 용어 변경 |
| 새 Action type 검증 | 「이 속성은 편집 가능으로 지정되지 않았습니다: <Type>.<prop>」, 「live Object type에는 writeback을 둘 수 없습니다」, 「객체 참조 파라미터의 타입 '<T>' 이(가) 없습니다」 | 신규 |
| 발행 전 dry-run(발행본 대상) | 「실행 모듈이 이 액션을 모릅니다 — 발행했는지 확인하세요. (<msg>)」, 화면은 「작업본으로 계획 만들기」를 권함 | 유지(용어) |
| dry-run 허용 0건 | 「허용 대상이 0건입니다 — 조건(where)·제출 조건·객체를 확인하세요. 검증 기록을 남기지 않았습니다.」 / 성공 note 「dry-run 만 했습니다 — 실행·승인은 하지 않습니다.」 | 유지(용어) |
| 작업본 충돌 | 409 `DRAFT_CONFLICT` 「다른 곳에서 먼저 바뀌었습니다 — 새로 고친 뒤 다시 저장하세요.」(에이전트에겐 최신 정의를 함께 돌려줌) | 신규 |
| 같은 apiName | 422 「Object type 'X' 이(가) 이미 있습니다.」 (원본 「…병합되었습니다.」 병합 동작 없음) | 의도된 차이 |
| 없는 온톨로지 | 404 「온톨로지 'X'을(를) 찾을 수 없습니다.」 | 용어 변경 |
| 카탈로그 비어 있음 | 404 `CATALOG_EMPTY` + 문구(§7.5) | 용어 변경 |
| 검증 오류 있는 발행 | 422 `VALIDATION_FAILED`, 버튼 비활성 | 신규 |
| 발행 실패 | 「발행하지 못했습니다 — 이전 버전(vN)이 그대로 유지됩니다: <원인>」 | 원본 「발행 실패: …」 확장 |
| 오래된 제안 발행 | 409 `PROPOSAL_STALE` | 신규 |
| 증표 없음 | 403 `APPROVAL_PROOF_REQUIRED` | 신규 |
| 가져오기 실패 | 422 + 파일 안 위치(`object-types/Shipment.yaml: backing[0].key`) | 신규 |
| live 제약 위반 | 「live는 같은 데이터소스의 원천만 합칠 수 있습니다 — indexed로 바꾸세요.」, 「이 함수는 live에서 원천 SQL로 바꿀 수 없습니다: <fn>」 | 신규 |
| 그래프 연결 끊김 | 상단 상태 배지 「그래프 엔진 연결 안됨」, 발행·객체 보기 비활성, 작업본 편집은 가능(정의는 메타 DB) | 원본 「Ontological 연결 안됨」 용어 변경 |

---

## 11. 원본과 비교할 테스트

원본 M1 설계 §12의 20항목을 기준으로 한다. 에이전트 결과는 내용이 아니라 흐름·형식으로 비교(ADR-0010).

### 11.1 같아야 함
1. 브리프 단계 요약 문자열·시작 조건·안내 문구(입력 조합 5가지). (원본 #2)
2. 초안 자동 요청: 디바운스·생략 조건·응답 적용 규칙(목 응답 고정). `brief-draft` 응답·실패 형식, 초안 프롬프트 라벨 블록(목 에이전트 캡처). (#3, #4)
3. 권장 전략 결정 표 전 조합에서 `recommended/available/unavailable`와 이유 문구 동일. (#5)
4. 구축 턴 프롬프트 라벨 블록 — 원본 라벨(이름이 바뀐 것은 사상표로)과 순서, 저장된 build_context 복원 규칙. (#6)
5. SSE 패턴 `status → (token|tool_start|tool_result|부수 이벤트)* → todos → done`, 시작 문구, 파일·셸 `tool_start` 설명 문구. (#7)
6. 보고서 추출: 정상 블록 / json 대체 / 블록 없음 / 질문 누락 / 커맨드 누락·취소형·저장소 검증 덮어쓰기 — 같은 입력에서 같은 `golden_questions`·`golden_commands`(필드 이름 사상 후). (#8)
7. 세션 API·대화 전환 시 브리프 복원. 파일 API 응답 형식. (#9, #10)
8. Action type 검증 경계 사례 표(이름·slug·중복·표현식 뿌리 각 종류·`$cancel`·`$steps` 앞/뒤·정수 범위) → 같은 수락/거절과 같은 문구. 저장 후 경고 문구·version 증가·검증 기록 초기화. (#13)
9. 인자 자동 채움 결과(예제 시스템 operation 대상). (#14)
10. dry-run 요약 키(`allowed`, `denied`, `allowed_keys` 10, `denied_reasons` 5, `preview_calls`…)와 검증 기록 조건(허용 ≥1). (#16)
11. 카탈로그 일괄 생성: 목 카탈로그에서 Object type 이름·제목·키, Link 수가 원본 클래스·관계와 1:1 대응(이름은 §7.4 사상, 타입은 §7.5 표). (#17)
12. 역바인딩 점수·판정(같은 목 데이터에서 같은 점수와 판정). 결과 문구. (S13)
13. 예제 시드: 온톨로지 1, Object type 7(속성·키), Link type 6, 객체 수(원본 인스턴스 수와 같음), Action type 3(사상된 정의), dry-run 3건 verified. 발행 후 F2에서 원본 튜토리얼 골든 퀘스천 답이 같은 값(00 §7 성공 기준 1). (#18)

### 11.2 의도된 차이 (D-12)
| # | 원본 | 새 | 테스트 |
|---|---|---|---|
| 1 | 「발행해 줘」로 에이전트가 발행 | 에이전트는 제안만, 사람이 「발행」+네이티브 창 | build 도구 목록에 발행 도구 없음; 증표 없는 발행 403 |
| 2 | 화면에 발행 버튼 없음 | 상단 「발행」 | D-15③ |
| 3 | 저장 즉시 반영 | 작업본 → 발행 후 반영 | 발행 전 Object API에 없음 |
| 4 | 골든 커맨드 dry-run은 발행 후 | 작업본 dry-run, 계획은 실행 불가 | `draft:true` 계획 승인 시 거부 |
| 5 | 구축 화면 계획 카드에서 승인·실행 | 작업본 카드 보기 전용, 발행본은 F2 | D-15② |
| 6 | 초기화 = 그래프 전체 삭제 | 온톨로지 단위 + 백업 + 네이티브 창 | 다른 온톨로지·예제 객체 수 불변 |
| 7 | 스키마 삭제 시 발행물 잔존 | 삭제 시 발행 거두기 | 삭제 후 Object API 404 |
| 8 | 같은 이름 클래스 = 전역 라벨, 병합 경고 | 이름공간 분리, 같은 온톨로지 안 중복은 422 | 두 온톨로지에 `Supplier` → 객체 섞이지 않음 |
| 9 | 이름 부분 일치 조회 | 정확 일치 | 「공급망」으로 찾기 → 없음 |
| 10 | 적재 도구가 클래스 정의를 비울 수 있음 | 정의 불변 | `batch_ingest` 후 정의 diff 없음 |
| 11 | 업로드 이름 경로 이동 미검사 | 정규화 | `../../x` → 작업 공간 안 |
| 12 | 권장 전략 미전달 | `[전략]` 블록 | 프롬프트 캡처 |
| 13 | 카탈로그 생성 결과 = 가상 클래스 즉시 조회 | 작업본 live 타입, 발행 후 조회 | 완료 문구 |
| 14 | 원본 속성명 = 컬럼명, float/date 타입 | camelCase, decimal/double/timestamp | §7.4·§7.5 사상표 |
| 15 | 오류 = 200 + `{error}` | HTTP 상태 + `{error:{code,message}}` (단 `brief-draft`는 유지) | 코드·문구 비교 |
| 16 | 배포 탭(개발→운영 릴리스) | 버전·내보내기/가져오기 | D-19 |
| 17 | 그래프 탭 엔티티 직접 CRUD | 액션(기본 편집 액션)으로 | 감사에 actionRun id |
| 18 | 그래프 탭 자연어 질의가 OpenAI 키 직접 사용 | 단일 LLM 클라이언트 | 04 §3 |
| 19 | SSE `neo4j_update`·`schema_created`·`datasource_update` | `draft_update`·`ontology_created`·`backing_update` + `proposal_created` | 이벤트 이름 사상표 |
| 20 | 인과 가설 패널 | v2 (Link type 후보) | v1에서 숨김 |
| 21 | 키 없는 테이블도 바인딩 | 기본 키 없음 = 검증 오류 | §7.5 |

### 11.3 새 기능 테스트
작업본 리비전 충돌(409), 제안 stale 판정, 발행 원자성(컴파일 실패 주입 → 이전 버전 유지), 되돌리기 결과 = 이전 스냅숏과 정의 동일, 내보내기 → 가져오기 왕복 후 정의 동일(rid 보존 모드), Automap 결과 결정성, 객체 미리보기 통계(키 결측·중복 주입), Link 미리보기 일치율, live 제약 판정, 영향 분석(대시보드 위젯 의존 삭제 → 「깨짐」), 골든 회귀 pass→fail 표시.

---

## 12. 열린 질문

1. **작업본 dry-run의 대상 해석**: 발행 전 indexed 타입은 동기화된 데이터가 없다. 이 명세는 「미리보기 해석(원천 표본 최대 1000행)」으로 계획을 만든다고 가정 — 표본 상한과 표시 방법 확인 필요. 원천이 크면 허용 0건이 표본 탓일 수 있다.
2. **시드 예제의 발행 증표 예외**: 첫 실행 시드는 사람 증표 없이 `system`으로 발행한다(03 §4 예외). 03에 예외 조항을 둘지, 시드도 첫 실행 때 사람이 「예제 발행」을 누르게 할지.
3. **설명 문구 개정**: 사이드바 「문서를 분석하고 스키마, 엔티티, 관계를 생성하는 작업 모드입니다.」 등 원본 문구를 새 용어(Object type·링크)로 바꿀지 — 비교 테스트 문구 일치와 충돌.
4. **식별 속성·기본값 선언**: F6 동일성 판정·결측 보정은 원본에서 속성의 `identifier`·`default` 선언을 쓴다. → **해결: 02 §6 Property에 `identifier`·`default` 추가됨.**
5. **writeback 값**: 원본 「성공 시 기록할 속성」이 어떤 값을 기록하는지(응답의 같은 이름 필드로 추정) [확인 필요 — 실행 기록].
6. **역바인딩 임계값**(auto/needs_review 경계) [확인 필요 — 원본 M1 설계 §14-3].
7. **열린 제안 1개 제약**과 에이전트 동시 작업: 사람이 검토 중인 제안을 에이전트가 새로 고쳐 버리는 일을 막을지(검토 중 잠금).
8. **Object view 범위**: 00 §5는 Object view를 F5 v1로 둔다. 설정 화면은 F1(정의), 렌더링은 F5로 나눴다 — 맞는지.
9. **복합 외래키·복합 키 링크** → **해결: 02 §8 foreign-key에 `pairs` 목록 추가됨.**: 02 §8 foreign-key가 단일 표현식이다. 복합 키 Object type으로의 링크를 어떻게 표현할지(표현식 `concat` 강제 vs 키 목록).
10. **문서 OCR 엔진**(D-15⑤): 로컬 엔진 번들 vs LLM 비전 호출(단일 클라이언트). 기본 끔은 확정, 엔진은 미정.
