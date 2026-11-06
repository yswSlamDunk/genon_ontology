# 온톨로지 아키텍처 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-backend/overview/
- 사이드바 위치: Ontology architecture > Overview and getting started > Overview

이 페이지는 Foundry 온톨로지(Ontology)를 뒤에서 떠받치는 백엔드 서비스들의 구성을 개괄합니다. 온톨로지를 정의하는 메타데이터 서비스, 객체 데이터를 저장하고 조회하는 객체 데이터베이스, 읽기를 담당하는 Object Set Service, 쓰기를 조율하는 Funnel 등이 각각 어떤 역할을 하는지 설명합니다. 또 레거시 백엔드인 Object Storage v1(Phonograph)에서 차세대 백엔드인 Object Storage v2로 넘어간 배경과 달라진 점을 정리합니다.

Foundry 온톨로지는 조직을 위한 운영 계층(operational layer)입니다. 온톨로지는 Foundry에 통합된 디지털 자산(데이터셋과 모델) 위에 자리 잡고, 이 자산들을 현실 세계의 대응물과 연결합니다. 그 대응물은 공장, 장비, 제품 같은 물리적 자산부터 고객 주문이나 금융 거래 같은 개념까지 다양합니다. 온톨로지는 조직의 디지털 트윈(digital twin) 역할을 하며, 모든 유형의 사용 사례를 가능하게 하는 데 필요한 의미적 요소(semantic elements: 객체, 속성(property), 링크)와 동적 요소(kinetic elements: 액션, 함수(function), 동적 보안)를 모두 담고 있습니다. Foundry 온톨로지와 그것이 더 나은 의사 결정을 어떻게 가능하게 하는지는 [온톨로지 문서](../../01_ontology-building/01_overview.md)에서 더 알아볼 수 있습니다.

Foundry 온톨로지는 온톨로지 안의 객체를 인덱싱하고, 저장하고, 조회하고, 조작하기 위해 함께 동작하는 여러 서비스가 뒷받침합니다. 이 페이지는 온톨로지 백엔드 아키텍처를 높은 수준에서 개괄합니다.

**설명**: "의미적 요소"는 데이터가 무엇을 뜻하는지 기술하는 부분(어떤 객체 타입이 있고, 어떤 속성을 가지며, 서로 어떻게 연결되는지)이고, "동적 요소"는 그 데이터를 바꾸거나 계산하거나 접근을 통제하는 동작 부분입니다. 데이터베이스로 치면 스키마와 데이터가 의미적 요소, 트랜잭션과 저장 프로시저와 접근 제어가 동적 요소에 대응합니다.

<a id="functional-components-and-architecture"></a>
## 기능 구성 요소와 아키텍처 (Functional components and architecture)

Foundry 플랫폼은 여러 서비스가 함께 온톨로지 백엔드를 구성하는 마이크로서비스 아키텍처를 사용합니다. 온톨로지 백엔드는 세 가지 주요 기능을 담당합니다.

* 온톨로지에 데이터를 공급하고 온톨로지 안의 스키마 정의를 관리하는 **데이터소스 관리**.
* 특정 필터링과 권한 적용을 지원하면서 온톨로지에서 **객체를 조회, 검색, 집계**하는 기능.
* 데이터소스의 인덱싱, 그리고 Foundry에서 내려진 결정이나 수행된 액션에 따른 온톨로지 객체 편집(edit)을 포함하는 **온톨로지 쓰기의 조율(orchestration)**.

이 기능들은 온톨로지 백엔드를 이루는 서비스들이 함께 처리하며, 그 서비스들은 아래와 같습니다.

* [Ontology Metadata Service (OMS)](#ontology-metadata-service-oms)
* [객체 데이터베이스(Object databases)](#object-databases)
* [Object Set Service (OSS)](#object-set-service-oss)
* [액션(Actions)](#actions)
* [Object Data Funnel](#object-data-funnel)
* [Functions on Objects](#functions-on-objects)

**설명**: 마이크로서비스 아키텍처는 하나의 큰 프로그램 대신 역할별로 나뉜 여러 개의 작은 서버 프로그램이 네트워크(주로 HTTP API)로 서로 호출하며 전체 시스템을 이루는 설계 방식입니다. 여기서는 "스키마를 관리하는 서비스", "읽기를 처리하는 서비스", "쓰기를 처리하는 서비스"가 각각 따로 존재한다는 뜻입니다.

<a id="oms"></a><a id="ontology-metadata-service-oms"></a>
### Ontology Metadata Service (OMS)

Ontology Metadata Service(OMS)는 어떤 온톨로지 엔터티들이 존재하는지를 정의하는 총괄 서비스입니다. 이 정의에는 객체 타입의 메타데이터, 객체 타입 사이의 관계를 기술하는 링크 타입, 구조화되고 통제된 방식으로 객체 데이터를 수정할 수 있는 액션 타입 등이 포함됩니다.

Foundry 온톨로지의 핵심 개념은 [온톨로지 메타데이터 문서](../../01_ontology-building/04_core-concepts.md)에서 더 알아볼 수 있습니다.

**설명**: OMS가 저장하는 것은 객체 데이터 자체가 아니라 "데이터에 대한 데이터", 즉 메타데이터입니다. 관계형 데이터베이스에서 테이블의 행이 아니라 `CREATE TABLE` 문으로 정의된 테이블 이름, 열 이름, 열 타입, 외래 키 정의를 보관하는 시스템 카탈로그에 해당합니다.

<a id="object-databases"></a>
### 객체 데이터베이스 (Object databases)

객체 데이터베이스는 온톨로지에서 인덱싱된 객체 데이터를 저장하는 서비스로, 사용자 애플리케이션에 빠른 데이터 조회와 쿼리 계산을 제공하도록 설계되었습니다. 객체 데이터베이스는 인덱싱된 데이터를 저장하는 것 외에도 인덱싱, 조회, 사용자 편집의 조율도 담당합니다.

**Object Storage v1 (Phonograph)은** Foundry의 레거시 온톨로지 백엔드 구성 요소입니다. **Object Storage v2는** 온톨로지를 뒷받침하는 차세대 표준 데이터 저장소입니다. 이 서비스들에 대한 자세한 내용은 [아래](#evolution-of-the-ontology-backend)에서 찾을 수 있습니다.

**설명**: 인덱싱(indexing)은 원본 데이터(예: 데이터셋 파일)를 읽어서 검색과 조회가 빠르도록 별도의 자료구조로 변환해 저장하는 과정입니다. 데이터베이스에서 B-트리 인덱스를 만들면 전체 테이블을 훑지 않고도 특정 값을 빠르게 찾을 수 있는 것과 같은 원리입니다. 온톨로지에서는 데이터셋의 행을 객체로 바꾸어 객체 데이터베이스에 넣는 작업 전체를 인덱싱이라고 부릅니다.

<a id="object-set-service-oss"></a><a id="oss"></a>
### Object Set Service (OSS)

Object Set Service(OSS)는 온톨로지로부터의 읽기 요청을 처리하는 서비스입니다. OSS는 다른 Foundry 서비스와 애플리케이션이 온톨로지에서 객체 데이터를 조회할 수 있게 하여, 객체의 검색, 필터링, 집계, 로딩을 가능하게 합니다.

<a id="object-sets"></a>
#### 객체 집합 (Object sets)

객체 집합(object set)은 나중에 참조하고 객체를 지원하는 Foundry 애플리케이션 전반에서 사용할 수 있도록 저장된, 현실 세계 엔터티의 목록입니다. 객체 집합은 협업자와 쉽게 공유할 수 있도록 리소스로 저장됩니다.

객체 집합은 정의 방식(정적 또는 동적)과 객체 백엔드에서의 현재 상태(임시 또는 영구)로 구분할 수 있습니다.

* **정적 객체 집합(Static object sets):** 정적 객체 집합은 기본 키(primary key)의 목록으로 저장되며, 입력 데이터가 어떻게 바뀌든 그대로 유지됩니다.

* **동적 객체 집합(Dynamic object sets):** 동적 객체 집합은 객체 집합을 만들 때 적용한 필터의 표현으로 저장됩니다. 새 데이터가 필터 조건에 맞으면 객체 집합이 갱신됩니다.

* **임시 객체 집합(Temporary object sets):** 임시 객체 집합은 주로 플랫폼 안에서 한 애플리케이션이나 서비스에서 다른 애플리케이션이나 서비스로 객체 집합을 넘겨줄 때 사용하며, 만든 사용자만 접근할 수 있습니다. 임시 객체 집합 RID의 예는 `ri.object-set.main.temporary-object-set.37d7e171-2d11-4fcd-b031-9a0863f6f744` 과 같은 형태이며, 24시간 안에 만료됩니다.

* **영구 객체 집합(Permanent object sets):** 영구 객체 집합은 나중에 참조하고 플랫폼 전반에서 사용할 수 있도록 객체 백엔드에 저장됩니다.

**설명**: 정적 객체 집합과 동적 객체 집합의 차이는 SQL로 보면 분명합니다. 정적 객체 집합은 `WHERE employee_id IN ('E1', 'E7', 'E9')` 처럼 저장 시점의 기본 키 목록을 그대로 기억하므로, 나중에 새 직원이 추가되어도 결과는 E1, E7, E9 세 개뿐입니다. 동적 객체 집합은 `WHERE department = 'Sales'` 같은 조건식 자체를 저장하므로, 나중에 Sales 부서에 직원이 추가되면 다시 조회할 때 그 직원도 결과에 포함됩니다. 동적 객체 집합은 데이터베이스의 뷰(view)와 같은 성질을 가집니다. RID(Resource Identifier)는 Foundry가 리소스마다 붙이는 고유 식별 문자열입니다.

> **중간 요약**: 온톨로지 백엔드는 정의(OMS), 저장(객체 데이터베이스), 읽기(OSS), 편집(Actions), 쓰기 조율(Funnel), 로직 실행(Functions)을 각각 맡는 서비스로 나뉩니다. 객체 집합은 기본 키 목록으로 고정된 정적 집합과 필터로 정의되는 동적 집합이 있고, 저장 수명에 따라 임시와 영구로 나뉩니다.

<a id="actions"></a>
### 액션 (Actions)

Actions 서비스는 사용자 편집을 객체 데이터베이스에 적용하는 역할을 합니다. 액션은 객체의 속성 값을 수정하는 구조화된 방법을 제공하고, 사용자 편집에 대해 복잡한 권한과 조건을 걸 수 있게 합니다. 또한 액션을 사용해 사용자 결정을 분석하기 위한 액션 이력 로그를 만들 수도 있습니다.

<a id="object-data-funnel"></a>
### Object Data Funnel

Object Data Funnel("Funnel")은 Object Storage v2 아키텍처에서 온톨로지로의 데이터 쓰기를 조율하는 마이크로서비스입니다. Funnel은 Foundry 데이터소스(데이터셋, 제한된 뷰(restricted view), 스트리밍 데이터소스 등)와 사용자 편집(액션으로부터 온 것)에서 데이터를 읽어 객체 데이터베이스에 인덱싱합니다. 또한 Funnel은 기반 데이터소스가 갱신될 때 인덱싱된 데이터도 최신 상태로 유지되도록 보장합니다.

**설명**: 즉 객체 데이터베이스로 들어오는 쓰기 경로는 두 가지입니다. 하나는 파이프라인이 만든 데이터셋 같은 데이터소스가 갱신되는 경로이고, 다른 하나는 사용자가 액션으로 객체를 직접 고치는 경로입니다. Funnel은 이 두 입력을 함께 받아 최종 객체 상태를 만들어 저장하는 관문 역할을 합니다.

<a id="functions-on-objects"></a>
### Functions on Objects

함수(function)는 코드 작성자가 의사 결정 과정을 지원하도록 설계된 대시보드나 애플리케이션 같은 운영 환경에서 빠르게 실행될 수 있는 로직을 작성할 수 있게 합니다.

자세한 내용은 [Functions](../../02_define-ontologies/04_functions/01_overview.md) 문서를 참고하십시오.

> **중간 요약**: 액션은 통제된 방식의 사용자 편집을 담당하고, Funnel은 데이터소스와 사용자 편집을 받아 객체 데이터베이스에 인덱싱하며 최신 상태를 유지합니다. 함수는 애플리케이션에서 빠르게 실행되는 로직을 제공합니다.

<a id="evolution-of-the-ontology-backend"></a>
## 온톨로지 백엔드의 발전 (Evolution of the Ontology backend)

이 섹션은 Object Storage v1(Phonograph)의 레거시 아키텍처와 개선된 Object Storage v2 아키텍처를 설명합니다.

<a id="object-storage-v1-phonograph-architecture-planned-deprecation"></a>
### Object Storage v1 (Phonograph) 아키텍처 \[지원 중단 예정]

**주의**: 지원 중단 예정(Planned deprecation). Object Storage v1(Phonograph)은 개발 수명 주기상 [지원 중단 예정](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으며 2026년 6월 30일 이후에는 사용할 수 없습니다. [객체 타입과 링크 타입을 Object Storage v2로 마이그레이션](03_osv1-osv2-migration.md)하십시오. 자세한 내용은 [Upgrade Assistant](https://www.palantir.com/docs/foundry/upgrade-assistant/overview/)의 `Migrate object types and many-to-many link types from Object Storage v1 to v2` 개입(intervention) 항목을 참고하십시오. 워크플로의 OSv1에서 OSv2로의 마이그레이션에 대해 질문이 있으면 Palantir Support에 문의하십시오.

Object Storage v1(Phonograph)은 Foundry의 최초 객체 데이터베이스로, 온톨로지 안의 객체 데이터 전반에 Foundry의 보안 모델을 유지하면서 매우 다양한 데이터 모델의 정보를 인덱싱하고 관리하도록 설계되었습니다. Object Storage v1(Phonograph)은 데이터를 인덱싱하고 저장하는 것 외에도 사용자가 만든 편집의 적용을 추적하고, 검색과 집계를 포함한 복잡한 사용자 쿼리를 처리하며, 데이터 라이트백(writeback)을 조율합니다.

아래는 Object Storage v1(Phonograph)의 아키텍처를 설명하는 다이어그램입니다.

![Object Storage v1 아키텍처](https://www.palantir.com/docs/resources/foundry/object-backend/osv1-arch.png)

<a id="object-storage-v2-architecture"></a>
### Object Storage v2 아키텍처

Foundry가 더 많은 기능을 갖추고 Palantir 고객의 복잡한 운영 요구와 커지는 규모에 맞춰 발전하면서, 차세대 온톨로지 기반 사용 사례와 워크플로를 가능하게 하기 위해 Object Storage v2가 기본 원리부터 새로 설계되었습니다.

구체적으로, 새 아키텍처는 Object Storage v1(Phonograph)에 한데 묶여 있던 관심사의 차원들을 분리하고 시스템 설계 안에서 책임을 분리(decouple)합니다. 데이터 인덱싱을 맡는 하위 시스템과 데이터 조회를 맡는 하위 시스템을 분리함으로써, Object Storage v2는 향후 요구에 맞춰 더 쉽게 수평 확장할 수 있습니다.

**설명**: 수평 확장(horizontal scaling)은 한 대의 서버 성능을 올리는 대신 서버 대수를 늘려 처리량을 키우는 방식입니다. 인덱싱(쓰기)과 조회(읽기)가 한 시스템에 묶여 있으면 무거운 인덱싱 작업이 조회 응답 속도에 영향을 주고, 둘 중 하나만 늘리기도 어렵습니다. 둘을 분리하면 읽기가 많을 때는 조회 쪽만, 데이터가 많을 때는 인덱싱 쪽만 따로 늘릴 수 있습니다.

Object Storage v2는 [Object Data Funnel](#object-data-funnel)을 통해 [액션](../../02_define-ontologies/03_action-types/01_overview.md) 같은 추가 서비스도 통합합니다.

Object Storage v2로 가능해진 새로운 기능은 다음과 같습니다.

* 모든 객체 타입에 대해 증분 객체 인덱싱(incremental object indexing, 기본으로 활성화)을 통해 온톨로지 데이터 인덱싱 성능이 크게 향상되었습니다.
* 단일 객체 타입에 대해 수백억 개 규모의 객체까지 인덱싱 처리량이 늘었습니다.
* 다중 데이터소스 객체 타입을 통해 열(column)과 속성 수준 권한을 포함한 더 세분화된 객체 권한을 지원합니다.
* 사용자 편집 처리량이 늘어, 단일 액션에서 최대 10,000개 객체를 편집할 수 있습니다. 더 높은 한도가 필요하면 Palantir Support에 연락해 해당 환경(enrollment)에 대한 변경 요청을 만드십시오.
* 사용자 편집의 지연 시간이 줄고, 사용자 편집이 더 빨리 반영되어 보입니다.
* 객체 타입에 호환성을 깨는(breaking) 스키마 변경이 있은 뒤에도 기존 사용자 편집을 마이그레이션할 수 있습니다.
* 스트리밍 데이터소스를 지원하여 온톨로지로의 저지연 데이터 인덱싱이 가능합니다.
* 객체 타입당 최대 2000개의 속성을 지원합니다.
* Spark 기반 쿼리 실행 계층을 통해 더 큰 규모의 Search Around와 더 정확한 집계를 지원합니다.
  * 기본적으로 Search Around 한도는 100,000개 객체입니다. 사용 사례에 100,000개 객체를 넘는 대규모 Search Around가 필요하면 Palantir Support에 연락해 활성화 방법을 안내받으십시오.

**설명**: 증분 인덱싱은 데이터소스가 갱신될 때 전체 데이터를 처음부터 다시 인덱싱하지 않고, 새로 추가되거나 바뀐 행만 반영하는 방식입니다. 예를 들어 1억 행 데이터셋에 하루 1만 행이 추가된다면, 전체 인덱싱은 매일 1억 행을 다시 처리하지만 증분 인덱싱은 1만 행만 처리합니다. Search Around는 어떤 객체 집합에서 링크를 따라가 연결된 객체 집합을 얻는 연산으로, SQL의 조인과 같은 역할을 합니다.

아래는 Object Storage v2가 온톨로지를 어떻게 뒷받침하는지 설명하는 아키텍처 다이어그램입니다.

![Object Storage v2 아키텍처](https://www.palantir.com/docs/resources/foundry/object-backend/osv2-arch.png)

> **중간 요약**: Object Storage v1(Phonograph)은 인덱싱, 저장, 편집, 쿼리를 한 시스템에서 처리하던 레거시 백엔드로 2026년 6월 30일 이후 사용할 수 없습니다. Object Storage v2는 인덱싱과 조회를 분리해 수평 확장을 쉽게 했고, 증분 인덱싱, 대규모 인덱싱, 속성 수준 권한, 액션당 10,000개 객체 편집, 스트리밍 데이터소스, 대규모 Search Around 등을 지원합니다.

## 정리

- 온톨로지 백엔드는 OMS(정의), 객체 데이터베이스(저장), OSS(읽기), Actions(편집), Funnel(쓰기 조율), Functions(로직)로 구성된 마이크로서비스 묶음입니다.
- 객체 집합은 정적(기본 키 목록)과 동적(필터), 임시(24시간, 생성자만 접근)와 영구로 구분됩니다.
- Funnel은 데이터소스와 사용자 편집을 받아 객체 데이터베이스에 인덱싱하고 최신 상태를 유지합니다.
- 레거시 OSv1(Phonograph)은 지원 중단 예정이며, OSv2는 인덱싱과 조회를 분리해 성능, 규모, 권한 세분화를 크게 개선했습니다.
