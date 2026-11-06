# 온톨로지 쿼리 컴퓨트 (Ontology query compute)

- 원문: https://www.palantir.com/docs/foundry/ontologies/query-compute-usage/
- 사이드바 위치: Define Ontologies > Ontologies > Usage > Ontology query compute

이 페이지는 사용자나 에이전트가 온톨로지를 조회하고 수정할 때(쿼리) 쓰이는 계산 자원, 즉 쿼리 컴퓨트가 어떻게 측정되고 어느 리소스에 청구되는지 설명합니다. 2026년 1월 1일부터 적용되는 쿼리 유형별 최소 비용 모델과, 그 이전의 레거시 모델을 함께 다룹니다.

Foundry 온톨로지는 파일 기반 데이터를 조직 중심의 객체로 매핑하고, 데이터 탐색, 데이터 분석, 운영 데이터 편집, 시나리오 분석 등을 위한 고속 쿼리를 제공하는 데이터 백엔드입니다. 온톨로지는 각자 목적이 다른 여러 방식(multi-modal)의 저장 백엔드에 데이터를 저장하며, 이들을 하나의 요청으로 유연하게 쿼리할 수 있습니다. Foundry 온톨로지를 쿼리하려면 아래에서 다루는 몇 가지 기초 개념을 알아야 합니다.

Palantir와 엔터프라이즈 계약을 맺고 있다면, 컴퓨트 사용량을 계산하기 전에 Palantir 담당자에게 문의하십시오.

<a id="core-concepts-object-types-and-object-sets"></a>
## 핵심 개념: 객체 타입과 객체 집합 (Core concepts: Object types and object sets)

첫 번째로 중요한 개념은 **객체 타입**과 그에 대응하는 **객체 집합(object set)의** 차이입니다. **객체 타입**은 엔터티 자체의 의미적(semantic) 표현입니다(예: 객체의 이름과 속성).

객체 타입에는 대응하는 **객체 집합**이 있으며, 객체 집합은 객체 자체를 담고 있습니다. **객체 집합**의 크기는 입력 데이터셋의 행 수, 그리고 온톨로지 액션으로 생성되거나 삭제된 객체 수에 따라 정해집니다.

**설명**: 객체 타입은 클래스 정의(또는 테이블 스키마), 객체 집합은 실제 인스턴스들(테이블의 행들)입니다. 예를 들어 데이터셋에서 온 Employee 행이 1,000개이고 액션으로 5명을 추가하고 2명을 삭제했다면 Employee 객체 집합의 크기는 1,003입니다. 쿼리 비용은 주로 이 객체 집합의 크기에 영향을 받습니다.

<a id="core-concept-query-types"></a>
## 핵심 개념: 쿼리 유형 (Core concept: Query types)

두 번째로 중요한 개념은 **쿼리 유형(query types)입니다**. 쿼리 유형에는 필터, 집계(aggregation), Search Around, 라이트백(writeback) 작업이 포함됩니다. 각 쿼리 유형은 실행에 컴퓨트가 필요합니다. 쿼리 유형별 현재 컴퓨트 초 오버헤드는 [온톨로지 쿼리 컴퓨트(2026)](#ontology-query-compute-2026)를 참고하십시오.

Foundry 온톨로지를 사용할 때 **쿼리 유형**은 다음 [Foundry 애플리케이션](../../../01_ontology-building/05_applications.md)에 의해 **객체 집합**을 대상으로 실행됩니다.

* Object Explorer
* Workshop
* Quiver
* Slate
* Vertex
* Foundry Rules
* Foundry Machinery
* Object APIs (OPIs)

이 중 어느 출처에서든 온톨로지를 쿼리하면 쿼리 실행에 컴퓨트 초가 사용됩니다.

**설명**: Search Around는 한 객체 집합에서 링크를 따라 연결된 다른 객체 집합으로 이동하는 쿼리입니다. SQL로 보면 `SELECT a.* FROM aircraft a JOIN flights f ON f.aircraft_id = a.aircraft_id WHERE f.origin = 'JFK'`처럼 "JFK에서 출발한 비행에 쓰인 항공기들"을 구하는 조인 쿼리에 해당합니다.

> **중간 요약**: 쿼리는 객체 타입이 아니라 실제 객체들을 담은 객체 집합에 대해 실행되며, 필터, 집계, Search Around, 라이트백 같은 쿼리 유형마다 컴퓨트가 듭니다. Workshop, Quiver, Object APIs 등 어느 애플리케이션에서 쿼리하든 컴퓨트 초가 사용됩니다.

<a id="investigating-foundry-compute-usage-from-ontology-queries"></a>
## 온톨로지 쿼리의 Foundry 컴퓨트 사용량 조사 (Investigating Foundry compute usage from Ontology queries)

Foundry에서 컴퓨트 초는 리소스와 상호작용하는 사용자가 아니라 플랫폼의 리소스에 귀속됩니다.

온톨로지 쿼리의 경우 컴퓨트가 귀속되는 방식은 여러 가지입니다. 일반 원칙은 쿼리가 시작된 리소스에 컴퓨트가 연결된다는 것입니다. 그러나 컴퓨트를 발생시킨 저장된 리소스가 없는 경우(예: API를 통한 쿼리)에는 쿼리 대상 객체 타입에 컴퓨트가 연결됩니다. 하나의 요청에서 여러 객체를 쿼리하면 컴퓨트는 객체들 사이에 균등하게 나뉘어 귀속됩니다.

다음 리소스 유형은 온톨로지 쿼리 컴퓨트가 기반 객체가 아니라 해당 리소스에 귀속됩니다.

* Workshop 애플리케이션
* Carbon 페이지
* Quiver 분석과 대시보드
* Vertex 애플리케이션
* Slate 애플리케이션
* Foundry Machinery 애플리케이션
* Foundry Rules 리소스
* Foundry Automate
* AIP Logic
* SQL Console 워크시트
* OSDK 애플리케이션

다음 상호작용 방식은 컴퓨트를 연결할 정해진 리소스가 없으므로, 온톨로지 쿼리 컴퓨트가 쿼리 대상 객체 타입에 직접 연결됩니다.

* Object Explorer
* Object APIs(OSDK 포함)

**설명**: 예를 들어 "정비 현황" Workshop 애플리케이션이 Aircraft 객체를 쿼리하면 그 비용은 Workshop 애플리케이션 리소스에 기록됩니다. 반면 외부 스크립트가 API로 Aircraft와 Flight를 한 요청에서 쿼리하면 비용은 Aircraft 객체 타입과 Flight 객체 타입에 반씩 기록됩니다. 비용을 줄이려면 어디에 귀속되는지 먼저 알아야 하므로 이 규칙이 중요합니다.

> **중간 요약**: 쿼리 컴퓨트는 사용자가 아니라 쿼리를 일으킨 리소스(Workshop 앱, Quiver 대시보드 등)에 귀속되고, 그런 리소스가 없는 Object Explorer나 API 쿼리는 대상 객체 타입에 균등 분할로 귀속됩니다.

<a id="ontology-query-compute-2026"></a>
## 온톨로지 쿼리 컴퓨트 (2026) (Ontology Query Compute (2026))

**참고**: 2026년 1월 1일부터 적용(Effective January 1, 2026). 다음 컴퓨트 모델은 2026년 1월 1일부터 적용되며, 아래 [레거시](#measuring-foundry-compute-with-ontology-object-queries-legacy) 섹션에서 설명하는 레거시 모델을 대체합니다.

온톨로지 쿼리 컴퓨트는 사용자와 에이전트의 온톨로지 사용에 의해 결정됩니다. 컴퓨트 사용량을 결정하는 주요 요인을 살펴봅니다.

<a id="factor-1-number-of-users-and-agents"></a>
### 요인 1: 사용자와 에이전트 수 (Factor 1: Number of users and agents)

컴퓨트 초는 누적으로 측정됩니다. 온톨로지에 대해 실행되는 쿼리와 변환이 많을수록 전체 컴퓨트 사용량이 커집니다. 쿼리 양은 사용자 상호작용(애플리케이션 새로고침, 대화형 쿼리 등)과 에이전트 기반 변환(agentic transformation)에 비례해 선형으로 증가합니다.

<a id="factor-2-query-type"></a>
### 요인 2: 쿼리 유형 (Factor 2: Query type)

사용자는 다음 쿼리 유형으로 온톨로지에 접근할 수 있으며, 각 유형에는 쿼리당 최소 컴퓨트 초 오버헤드가 정해져 있습니다. 실제 컴퓨트 사용량은 쿼리 복잡도와 객체 집합의 크기, 또는 쿼리 대상 객체 수에 따라 더 높을 수 있습니다.

* **기본 쿼리(Base query):** 객체 집합을 그대로 반환하거나 특정 속성에 대한 기본 필터링을 적용해 반환합니다.
* **Search Around 쿼리:** 입력 객체 집합을 받아, 입력 집합의 특정 속성을 기준으로 다른 객체 집합에 2차 필터를 실행합니다.
* **집계 쿼리(Aggregation query):** 입력 객체 집합을 받아, 집합의 모든 객체에 대해 속성 하나에 집계 함수(예: `sum`, `avg`)를 실행합니다.
* **[온톨로지 SQL 쿼리(Ontology SQL query)](https://www.palantir.com/docs/foundry/sql-warehousing/ontology-sql):** 객체 저장소에 대해 표준 Spark SQL 문법을 사용해 객체 타입, 링크, 인터페이스에 직접 SQL 쿼리를 실행합니다.
* **고급 쿼리(Advanced query):** 다른 쿼리 유형에 해당하지 않는 모든 것입니다. 예를 들어 객체 집합 전체에 걸쳐 임베딩에 대한 의미 검색(semantic search)을 적용하는 경우입니다.
* **파생 속성 쿼리(Derived Property query):** [파생 속성(derived properties)](../../../03_ontology-search/03_derived-properties.md)은 객체의 다른 속성이나 링크 값을 기반으로 쿼리 시점에 계산되는 속성이며, 링크된 객체의 속성을 집계하거나 선택하는 것도 포함합니다. 파생 속성은 같은 요청 안에서 필터링, 정렬, 집계 같은 추가 작업에 사용할 수 있습니다.
* **액션(Actions):** 지정된 객체 집합의 객체 속성 값을 대체하는 라이트백 작업입니다. 액션의 최소 오버헤드는 `18` 컴퓨트 초이며, 편집된 객체 수에 비례해 늘어나 첫 번째 이후 편집된 객체마다 `1` 컴퓨트 초가 추가됩니다.
* **온톨로지 컴퓨트(Phonograph) [레거시]:** 아직 Object Storage v1(OSv1) 백엔드를 쓰는 객체에 대한 쿼리입니다. Resource Management Application에는 "Ontology Compute (phonograph)"로 표시됩니다. 이 쿼리에는 [기존 OSv1 컴퓨트 모델](#measuring-compute-with-object-storage-v1-legacy)이 그대로 유지됩니다.

**다음 표는 쿼리 유형별 최소 컴퓨트 초 오버헤드를 요약합니다.**

| 쿼리 유형 | 최소 컴퓨트 초 오버헤드 |
|-----------------------------|----------------------------------|
| 기본 쿼리(Base query) | 2 |
| Search Around 쿼리 | 5 |
| 집계 쿼리(Aggregation query) | 5 |
| 온톨로지 SQL 쿼리 | 5 |
| 고급 쿼리(Advanced query) | 10 |
| 파생 속성 쿼리 | 10 |
| 액션(Actions) | 18 |
| 온톨로지 컴퓨트(Phonograph) [레거시] | 16 |

**참고**: Object Storage v1(OSv1) 쿼리에 대한 기존 컴퓨트 모델은 유지됩니다. 아직 OSv1 백엔드를 쓰는 객체에 대한 모든 쿼리에는 쿼리당 최소 `16` 컴퓨트 초의 오버헤드가 붙습니다.

**설명**: 표의 숫자는 하한값입니다. 예를 들어 Workshop 화면 하나가 열릴 때 기본 쿼리 3번과 집계 쿼리 2번을 실행한다면 최소 2 x 3 + 5 x 2 = 16 컴퓨트 초가 듭니다. 이 화면을 사용자 100명이 하루 10번씩 새로고침하면 최소 16 x 1,000 = 16,000 컴퓨트 초입니다(요인 1의 선형 증가). 액션으로 객체 50개를 한 번에 편집하면 18 + 49 x 1 = 67 컴퓨트 초입니다.

> **중간 요약**: 2026년 모델에서는 쿼리 유형마다 최소 비용이 있고(기본 2, Search Around와 집계와 SQL 5, 고급과 파생 속성 10, 액션 18, OSv1 16), 실제 비용은 복잡도와 객체 수에 따라 더 커질 수 있습니다. 전체 사용량은 사용자와 에이전트의 쿼리 횟수에 선형으로 비례합니다.

***

<a id="measuring-foundry-compute-with-ontology-object-queries-legacy"></a>
## 온톨로지 객체 쿼리의 Foundry 컴퓨트 측정 [레거시] (Measuring Foundry compute with Ontology object queries [Legacy])

**주의**: 레거시(Legacy). 다음 섹션은 2026년 1월 1일 이전에 적용되던 레거시 컴퓨트 모델을 설명하며, 참고용으로 남겨 둔 것입니다. 현재 컴퓨트 모델은 위의 [온톨로지 쿼리 컴퓨트(2026)](#ontology-query-compute-2026)를 참고하십시오.

레거시 모델에서 온톨로지 쿼리는 다음과 같이 컴퓨트 초를 사용합니다.

* 쿼리 오버헤드를 위한 고정된 최소 컴퓨트 초
* 쿼리를 처리하는 데 쓰인 컴퓨트 양으로 측정되는, 규모에 따라 늘어나는 추가 컴퓨트 초

<a id="measuring-compute-with-object-storage-v1-legacy"></a>
### Object Storage v1의 컴퓨트 측정 [레거시] (Measuring compute with Object Storage v1 [Legacy])

Object Storage v1(Phonograph)은 내구성 있고 수평 확장 가능한 클러스터 안에, 분산된 인덱스 집합으로 데이터를 저장합니다. 이 인덱스에서 데이터는 온톨로지 쿼리 엔진이 순회(traverse)하는 큰 자료구조 안에 놓입니다. 쿼리가 실행되면 엔진은 인덱스를 순회함으로써 검색 중 데이터의 넓은 영역을 처리하지 않고 건너뛸 수 있습니다. 이 과정을 "가지치기(pruning)"라고 합니다.

이 엔진을 사용하면 최대 1000배 적은 레코드를 평가하는 것만으로 수십억 개의 레코드를 검색할 수 있습니다. 레코드를 한 번 물리적으로 평가하는 것을 "히트(hit)"라고 합니다. Object Storage v1은 각 쿼리의 히트 수를 최소화하도록 설계되었습니다.

**설명**: 가지치기는 자료구조 수업의 이진 탐색 트리 탐색과 같은 원리입니다. 정렬된 인덱스에서 `age > 60`인 객체를 찾을 때, 60 이하 값만 담긴 하위 트리는 통째로 건너뛰므로 모든 레코드를 하나씩 비교(전체 스캔)하지 않아도 됩니다. 실제로 값을 비교한 레코드 수가 히트 수이고, 레거시 모델에서는 히트가 많을수록 추가 컴퓨트가 늘어납니다.

<a id="measuring-compute-with-object-storage-v2-legacy"></a>
### Object Storage v2의 컴퓨트 측정 [레거시] (Measuring compute with Object Storage v2 [Legacy])

Object Storage v2(OSv2)는 Palantir가 고속 인덱싱, Search Around, 라이트백에 최적화한 개선된 인덱싱 형식으로 객체를 저장하며, 복잡한 작업을 수행하기 위해 여러 컴퓨트 백엔드로 작업을 매끄럽게 넘길 수 있습니다. 여기에는 쿼리의 일부로 완전히 병렬화된 Spark 컴퓨트를 조합하는 것도 포함됩니다.

Object Storage v2도 효율적인 인덱싱 구조를 사용하므로, 기본 쿼리에는 Object Storage v1의 **히트** 원리가 똑같이 적용됩니다. 다만 쿼리의 일부로 띄워지는 온디맨드(on-demand) Spark 컨테이너에서도 컴퓨트 초가 사용될 수 있습니다.

Object Storage v2 백엔드의 객체에 대한 쿼리는 다음 방식으로 컴퓨트를 사용합니다.

* Object Storage v1 백엔드의 객체에 대해서는 쿼리당 최소 `16` 컴퓨트 초의 오버헤드가 있습니다.
* Object Storage v2 백엔드의 객체에 대해서는 쿼리당 최소 `4` 컴퓨트 초의 오버헤드가 있습니다. Object Storage v2의 최적화된 구조는 Object Storage v1보다 오버헤드가 적게 필요하므로 최소 컴퓨트 초 오버헤드가 낮습니다.
* 쿼리의 가지치기 과정에서 계산 작업이 이루어지면 추가 컴퓨트 초가 필요합니다. 추가 컴퓨트 초는 인덱스의 객체 수와 쿼리 유형에 따라 늘어납니다.
* Object Storage v2(OSv2)에서도 인덱스 가지치기에 추가 컴퓨트 초가 필요합니다. 또한 OSv2는 100,000개가 넘는 객체에 대해 Search Around를 실행하거나, 단일 요청에서 10,000개가 넘는 객체에 라이트백 작업을 실행할 때 온디맨드 Spark 클러스터 검색을 지원합니다. 이 Spark 클러스터는 플랫폼의 다른 모든 Spark 기반 애플리케이션과 같은 방식으로 사용량을 발생시킵니다. 설명은 [병렬화 컴퓨트 문서(parallelized compute documentation)](https://www.palantir.com/docs/foundry/resource-management/usage-types/)를 참고하십시오.
* 온톨로지로 라이트백하는 액션에는 최소 오버헤드가 있습니다. 액션 하나의 컴퓨트 초 오버헤드는 `18`입니다. 액션은 라이트백 요청에서 편집된 객체 수에 비례해 늘어나며, 첫 번째 이후 편집된 객체마다 `1` 컴퓨트 초가 추가됩니다.
* Functions on Objects로 실행되는 함수(function)에는 최소 오버헤드가 있습니다. 구체적으로 함수 실행 한 번에 `4` 컴퓨트 초의 고정 오버헤드가 붙습니다.

**다음 표는 레거시 모델에서 쿼리 유형별 최소 컴퓨트 초 사용량을 요약합니다.**

| 쿼리 유형 | 최소 컴퓨트 초 |
|---------------------|----------------------------------|
| 온톨로지 V1 쿼리(Ontology V1 query) | 16 |
| 온톨로지 V2 쿼리(Ontology V2 query) | 4 |
| 객체에 대한 액션(Action on Objects) | 18 |
| 객체에 대한 함수(Function on Objects) | 4 |

> **중간 요약**: 레거시 모델은 "고정 최소 오버헤드 + 히트 수에 따른 추가 비용" 구조였습니다. OSv1은 쿼리당 16, OSv2는 4, 액션은 18(+객체당 1), 함수는 4 컴퓨트 초가 최소이며, OSv2에서 대규모 Search Around나 라이트백은 Spark 클러스터 비용이 추가됩니다.

<a id="understanding-drivers-of-foundry-compute-usage-with-ontology-queries-legacy"></a>
## 온톨로지 쿼리의 Foundry 컴퓨트 사용량을 좌우하는 요인 [레거시] (Understanding drivers of Foundry compute usage with Ontology queries [Legacy])

* 아주 단순한 원칙으로, 쿼리당 고정 컴퓨트 사용량은 쿼리 수에 비례해 선형으로 늘어납니다. 쿼리를 덜 실행하면 전체적으로 컴퓨트를 덜 씁니다.
* 범용 다중 객체 검색처럼 객체 집합 서비스(object set service)에 대한 더 복잡한 쿼리는 각 객체 타입에 여러 하위 쿼리를 발생시킵니다. 검색 대상을 개별 객체 타입으로 한정하면 사용하는 쿼리 수를 줄일 수 있습니다.
* 쿼리의 **히트** 수는 쿼리 대상 객체 집합의 크기에 비례하므로, 작은 객체 집합에 대한 쿼리는 큰 객체 집합에 대한 쿼리보다 컴퓨트를 덜 씁니다.
* 다른 작업을 수행하기 전에 먼저 필터링하면, 고도로 인덱싱된 백엔드 구조의 이점을 활용할 수 있습니다. 이렇게 하면 쿼리의 **히트** 수가 줄어 전체 컴퓨트 사용량이 줄어듭니다. 필터링된 객체 집합은 전체 객체 집합보다 처리에 드는 컴퓨트가 적으므로, 집계와 Search Around에서 특히 중요합니다.

**설명**: 마지막 항목은 SQL에서 `WHERE`를 먼저 적용해 조인할 행을 줄이는 것과 같은 원리입니다. 예를 들어 "2024년에 JFK에서 출발한 비행"으로 먼저 거른 뒤 항공기로 Search Around를 하면, 전체 비행에서 Search Around를 한 뒤 거르는 것보다 처리 대상이 훨씬 적습니다.

> **중간 요약**: 쿼리 횟수를 줄이고, 검색 대상을 특정 객체 타입으로 좁히고, 집계나 Search Around 전에 먼저 필터링하는 것이 쿼리 컴퓨트를 줄이는 기본 방법입니다.

<a id="related-resources"></a>
## 관련 자료 (Related resources)

컴퓨트 사용량을 최소화하는 효율적인 함수 작성과 Automate 구성의 모범 사례는 다음을 참고하십시오.

* [함수 성능 최적화(Optimize function performance)](../../04_functions/08_function-consumption/03_optimize-performance.md)
* [Automate 성능 모범 사례(Automate performance best practices)](https://www.palantir.com/docs/foundry/automate/performance-best-practices/)

## 정리

- 쿼리 컴퓨트는 객체 집합에 대해 실행되는 필터, 집계, Search Around, 라이트백 등에 드는 비용이며, 사용자가 아니라 쿼리를 일으킨 리소스(없으면 대상 객체 타입)에 귀속됩니다.
- 2026년 1월 1일부터는 쿼리 유형별 최소 오버헤드(기본 2, Search Around, 집계, SQL 5, 고급과 파생 속성 10, 액션 18, OSv1 16)를 기준으로 합니다.
- 레거시 모델은 고정 오버헤드와 히트 수 기반 추가 비용으로 구성되었고, OSv2의 대규모 작업에는 Spark 비용이 더해졌습니다.
- 쿼리 횟수 감소, 객체 타입 한정, 선 필터링이 사용량을 줄이는 핵심입니다.
