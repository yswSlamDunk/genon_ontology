# 인핸스 COS — Ontology Layer 기능 조사 (초안)

> 목적: base PPT의 [Appendix] 인핸스 COS 아키텍처(slide 13) 중 **Ontology Layer**를 대상으로
> ① 어떤 기능을 제공하는지, ② 그 기능이 온톨로지 구축 프로세스(METHONTOLOGY 7단계, slide 3)에 해당하는지,
> ③ 구축된 온톨로지가 다른 레이어(Data·Agent·Action)와 어떤 기능으로 연결·사용되는지 정리
>
> 자료: base PPT slide 10·12·13 (인핸스 COS 소개 자료 도식), 인핸스 홈페이지(/ontology, /agent-builder, /app-builder, /pipeline-builder, 2026.10 확인)
> 표기: **[확인]** 공개 자료에 있음 / **[추정]** 본 리서치 해석 / **[미확인]** 공개 자료에 없음

---

## 0. PPT 구성안 (2~3장)

| # | 슬라이드 제목 (안) | 핵심 메시지 |
|---|---|---|
| 1 | Ontology Layer 제공 기능 | 온톨로지 매니저 = 4개 기능(오브젝트·관계·지식사전·테스트) |
| 2 | 기능 × 구축 프로세스 매핑 | ③개념화·④형식화·⑦유지관리(평가)에 집중, ①②는 도구 없음(FDE 수행), ⑤통합은 Data Layer가 담당 |
| 3 | 구축 후 레이어 간 연결 | 온톨로지는 Agent Layer(워크플로·대시보드)의 **조회·맥락 소스**로 쓰이고, Action Layer와는 에이전트를 거쳐 간접 연결 |

---

## 1. Ontology Layer 제공 기능

COS 아키텍처 도식상 Ontology Layer = **온톨로지 매니저 (의미·관계 설계)** 단일 모듈, 하위 4개 기능 [확인]

| 기능 (COS 도식) | 내용 | 홈페이지 표현 대응 |
|---|---|---|
| **오브젝트 목록** (조회, LLM 의미 생성) | 데이터를 업무 단위(거래처·주문·납기 등) 오브젝트로 정리, LLM이 의미(설명) 초안 생성 | Entity Modeling |
| **관계 링크 관리** (관계 지정) | 오브젝트 간 관계 지정 → 탐색·질의·추론 기준 | Relationship Mapping |
| **지식 사전** (GT·가이드라인·룰 관리) | 현장 규칙·암묵지·정답셋(GT)·가이드라인 등록 — 비정형 데이터의 적재 대상 | Rule and Constraint Layer / Semantic Knowledge Graph |
| **테스트케이스, 데이터 검증** | 실제 시나리오 기준으로 온톨로지 동작·데이터 검증 | (홈페이지 미기재) |

- 특징 [추정]: 팔란티어와 달리 **Action(실행 동작)을 온톨로지에 정의하지 않음** — 실행은 Agent·Action Layer에 위치
- 형식 언어(OWL·RDF 등)·내부 저장 방식, 버전·변경 승인 기능 [미확인]

---

## 2. 기능 × 온톨로지 구축 프로세스 매핑

| 구축 단계 | 해당 여부 | COS 기능 | 비고 |
|---|---|---|---|
| ① 계획 수립 | ✕ | — | FDE가 현장 인터뷰로 문제·KPI 합의 (도구 없음) |
| ② 요구사항 명세 | ✕ | — | 자동화 범위·사람 판단 지점 정리 (도구 없음). CQ·명세서 같은 산출물 기능 [미확인] |
| ③ 개념화 | **◎ Ontology Layer** | 오브젝트 목록(+LLM 의미 생성), 관계 링크 관리 | 레이어의 핵심 역할 |
| ④ 형식화 | **○ Ontology Layer** | 지식 사전(룰·가이드라인 명시), 관계 링크 | 표준 언어 기반 형식화는 [미확인] |
| ⑤ 통합 | △ (레이어 밖) | Pipeline Builder (Data Layer) | ETL·정규화 → 오브젝트 적재, 비정형 → 지식사전 적재. 표준 온톨로지 재사용 [미확인] |
| ⑥ 구현 | △ (레이어 밖) | Workflow Builder·Dashboard·ACT-2 | 온톨로지 "활용" 단계 — 3장 참조 |
| ⑦ 유지관리 | **○ Ontology Layer** | 테스트케이스, 데이터 검증 | Decision Making 시뮬레이션 결과로 틀린 판단을 온톨로지·에이전트 함께 수정 |
| (지원) 지식 획득 | ○ | 지식 사전 | 현장 규칙·암묵지 수집 창구 |
| (지원) 평가 | ○ | 테스트케이스 | |
| (지원) 문서화 | ✕ | — | [미확인] |

**정리**
- Ontology Layer **해당**: ③ 개념화 · ④ 형식화 · ⑦ 유지관리(평가) + 지식 획득
- Ontology Layer **비해당**: ①② (사람/FDE 영역), ⑤ (Data Layer), ⑥ (Agent·Action Layer)
- 즉 COS는 7단계 중 **"모델 설계 + 검증"만 Ontology Layer에 두고**, 통합·구현은 앞뒤 레이어로 분리한 구조

---

## 3. 구축 후 다른 레이어와의 연결

```
[Data Layer]  Pipeline Builder ──(적재: upsert)──▶ 오브젝트 / 지식사전
                                                       │
[Ontology Layer] 온톨로지 매니저 ───────────────────────┤ (의미·관계 = 공통 맥락)
                                                       ▼
[Agent Layer]  Workflow Builder ◀──(조회/생성 노드, 지식사전 연결)
               Dashboard Generation ◀──(온톨로지 + 자연어 쿼리)
                                                       │
[Action Layer] ACT-2 · Decision Making ◀──(에이전트 경유 실행) ── 결과 피드백 → 온톨로지 수정
```

| 연결 대상 | 연결 기능 | 사용 방식 | 근거 |
|---|---|---|---|
| **Data Layer** → Ontology (입력) | Pipeline Builder 적재 | 정형 → ETL·정규화 → 온톨로지 오브젝트 / 비정형 → 텍스트·이미지·표 인식 → 지식사전. upsert·중복제거로 적재 | [확인] |
| **Agent Layer** — 워크플로 | 온톨로지 오브젝트 연결 · 지식사전 연결 · **Ontology Query Node / Create Ontology Node** | 에이전트가 오브젝트 조회(읽기)·생성(쓰기), 지식사전을 판단 근거로 참조. MCP/Tool·HITL 노드와 함께 오케스트레이션 | [확인] |
| **Agent Layer** — 뷰/대시보드 (App Builder) | 온톨로지·자연어 쿼리 기반 대시보드 생성 | 온톨로지에 연결된 데이터로 대시보드·입력폼·모니터링 뷰 생성 → 편집·배포 | [확인] |
| **Action Layer** — ACT-2 | (직접 연결 기능 미기재) | 워크플로 에이전트의 판단 결과를 ACT-2가 기존 시스템 화면 조작으로 실행 | [추정] |
| **Action Layer** — Decision Making | 실행 자동화·시뮬레이션 | 시뮬레이션 결과 확인 후 운영 전환, 오류 시 온톨로지 수정 (피드백 루프) | [확인: slide 12] |

**포인트**
- 온톨로지는 실행 로직을 갖지 않고 **에이전트·대시보드에 "업무 맥락(조회 대상 + 근거 규칙)"을 공급하는 역할**
- 쓰기(Write-back)는 소스 시스템이 아닌 **온톨로지 노드 생성(Create Ontology Node)** 수준만 확인 — 소스 시스템 반영은 ACT-2 화면 조작으로 대체 [추정]

---

## 4. 비교 메모 (PPT 반영 여부 검토)

| 항목 | 인핸스 COS | 팔란티어 | GenD (Ontology Studio 안) |
|---|---|---|---|
| 온톨로지 구성요소 | Object · Link · Knowledge · Test | Object · Property · Link · **Action** | Object(LinkML) · SHACL 검증 · **Action(MCP)** |
| 실행 정의 위치 | Agent/Action Layer (온톨로지 밖) | 온톨로지 내 Action Type | 온톨로지 내 Action → MCP 도구 |
| 소스 시스템 반영 | ACT-2 화면 조작 | Action Write-back | MCP 도구 |
| 검증 | 테스트케이스·데이터 검증 | Proposals 리뷰 | SHACL 상시 검증 |

---

## 5. 미확인 / 추가 조사 필요

- 온톨로지 내부 표현 형식(그래프 DB 종류, OWL 등 표준 지원 여부)
- 버전 관리·변경 승인·권한 관리 기능 여부
- 에이전트가 온톨로지를 조회하는 인터페이스 (API / MCP / 자체 쿼리 언어)
- ACT-2가 온톨로지를 직접 참조하는지 여부
- 테스트케이스의 형태 (CQ 질의형인지, 시나리오 실행형인지)

## 출처

- base PPT v2.7 slide 10·12·13 (인핸스 COS 소개 자료 — End-to-End 아키텍처 구조, 데이터부터 액션까지 연결 흐름 도식)
- [인핸스 Ontology](https://www.enhans.ai/ontology) · [Agent Builder](https://www.enhans.ai/agent-builder) · [App Builder](https://www.enhans.ai/app-builder) · [Pipeline Builder](https://www.enhans.ai/pipeline-builder) (2026.10.28 확인)
