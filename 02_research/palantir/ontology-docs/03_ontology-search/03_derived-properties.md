# 파생 속성 (Derived properties)

- 원문: https://www.palantir.com/docs/foundry/ontology/derived-properties/
- 사이드바 위치: Ontology search > Derived properties

이 페이지는 값을 저장하지 않고 조회 시점에 계산하는 파생 속성(derived property)을 소개합니다. 파생 속성을 온톨로지에 정의하는 방식과 런타임에 정의하는 방식의 차이, 사용할 수 있는 애플리케이션, 보안이 적용되는 방식, 성능 특성, 수집 개수 제한, 현재의 제약 사항을 다룹니다. 데이터 파이프라인에서 미리 계산해 저장하는 값과 무엇이 다른지 이해하는 데 도움이 됩니다.

파생 속성은 다른 속성(property)이나 [링크된 객체](../02_define-ontologies/02_object-and-link-types/06_link-types/01_link-types-overview.md)로부터 조회 시점에 값이 계산되는 [속성](../02_define-ontologies/02_object-and-link-types/03_properties/01_properties-overview.md)입니다. 파생 속성은 값을 저장하는 대신 값을 계산하는 방법을 기술합니다. 링크를 따라가 링크된 객체의 속성을 선택하거나, 여러 링크된 객체에 걸쳐 집계하거나, 값을 산술적으로 조합하는 방식입니다.

파생 속성은 저장되지 않고 계산되므로 기반 데이터가 바뀌어도 항상 올바른 값을 유지합니다. 예를 들어 링크된 `Employee` 객체 수를 세는 파생 속성은 신규 입사와 퇴사를 자동으로 반영하며, 다시 실행할 파이프라인도, 관리할 갱신 로직도 필요 없습니다.

파생 속성은 다음 세 가지 방식 중 하나로 값을 계산할 수 있습니다.

* **링크된 객체에 걸쳐 집계(Aggregate across linked objects):** `Department` 객체 타입이 링크된 `Employee` 객체들의 평균 급여를 노출할 수 있습니다.
* **링크된 객체에서 선택(Select from a linked object):** `Employee` 객체 타입이 링크된 단일 `Employee` 객체에서 선택한 관리자 이름을 노출할 수 있습니다.
* **표현식 계산(Calculate an expression):** `Employee` 객체 타입이 `salary`와 `bonus`를 더해 계산한 총 보상을 노출할 수 있습니다.

파생 속성은 **읽기 전용**입니다. 액션이나 함수로 편집(edit)할 수 없으며, 객체 스토리지에 저장되지 않습니다.

**설명**: 관계형 데이터베이스로 표현하면 파생 속성은 저장된 열이 아니라 조회할 때 계산되는 열, 즉 뷰(view)나 `SELECT` 문 안의 계산식에 해당합니다. 예를 들어 `Department` 테이블과 `Employee` 테이블이 `department_id` 외래 키로 연결되어 있을 때, 부서별 평균 급여 파생 속성은 다음 SQL의 `avg_salary` 열과 같은 결과를 냅니다.

```sql
SELECT d.*, (SELECT AVG(e.salary) FROM employee e WHERE e.department_id = d.id) AS avg_salary
FROM department d;
```

직원 데이터가 바뀌면 다음 조회부터 바로 새 평균이 나오므로, 평균값을 별도 열에 저장해 두고 갱신하는 작업이 필요 없습니다. 대신 조회할 때마다 계산 비용이 든다는 점이 아래 "성능과 규모" 섹션의 주제입니다.

> **중간 요약**: 파생 속성은 다른 속성이나 링크된 객체로부터 조회 시점에 계산되는 읽기 전용 속성이며, 집계, 링크된 객체에서 선택, 표현식 계산의 세 가지 방식이 있습니다.

<a id="ontology-defined-and-runtime-defined-derived-properties"></a>
## 온톨로지 정의 파생 속성과 런타임 정의 파생 속성 (Ontology-defined and runtime-defined derived properties)

파생 속성은 온톨로지에서 정의할 수도 있고 런타임에 정의할 수도 있습니다. 어떤 형태를 쓰느냐에 따라 설정 위치, 볼 수 있는 사람, 사용할 수 있는 기능이 달라집니다.

![두 가지 형태의 파생 속성 비교. 온톨로지 정의 파생 속성은 Ontology Manager에서 설정하며 Workshop, Ontology SDK, Insight 같은 다른 애플리케이션에서 사용할 수 있고, 런타임 정의 파생 속성은 이를 선언한 워크플로 안에서만 쓰입니다.](https://www.palantir.com/docs/resources/foundry/ontology/derived-properties-ontology-vs-runtime-defined.png)

|   | 온톨로지 정의(Ontology-defined) | 런타임 정의(Runtime-defined) |
|---|---|---|
| 설정 위치 | Ontology Manager | Workshop 모듈, Insight 워크북, 또는 Ontology SDK 요청 |
| 저장 위치 | 온톨로지 정의 | 객체 집합(object set) 정의 |
| 공개 범위 | 해당 객체 타입을 사용하는 모든 곳 | 이를 선언한 요청이나 모듈, 그리고 이를 포함하는 저장된 객체 집합에 접근 권한이 있는 사용자 |
| 최대 링크 순회 횟수 | 3 | Workshop, Insight: 1, Ontology SDK: 고정 제한 없음 |
| 표현식 | 지원하지 않음 | 지원함 |
| 개발 상태 | 베타 | 정식 출시(Generally available) |

**참고**: 베타(Beta). 온톨로지 정의 파생 속성은 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며 사용 중인 환경(enrollment)에서는 사용하지 못할 수도 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다. 런타임 정의 파생 속성은 정식 출시되었습니다.

계산이 조직이 객체 타입을 모델링하는 방식의 일부이고 모든 사용처에서 이를 봐야 한다면 **온톨로지 정의** 파생 속성을 사용합니다. 계산이 하나의 애플리케이션이나 분석에만 속하거나, 산술 및 날짜 표현식이 필요하다면 **런타임 정의** 파생 속성을 사용합니다.

사용할 수 있는 집계와 표현식의 전체 목록은 [파생 속성 레퍼런스](04_derived-properties-reference.md)를 참고하세요.

**설명**: 두 형태의 차이는 정의가 어디에 저장되느냐입니다. 온톨로지 정의 파생 속성은 객체 타입의 스키마 자체에 들어가므로, 객체 타입을 쓰는 모든 애플리케이션에서 일반 속성처럼 보입니다. 런타임 정의 파생 속성은 특정 Workshop 모듈이나 SDK 요청 안에서 "이 객체 집합을 조회할 때 이런 계산 열을 붙여 달라"고 그때그때 지정하는 것이므로, 그 요청이나 모듈 밖에서는 보이지 않습니다.

> **중간 요약**: 온톨로지 정의 파생 속성은 Ontology Manager에서 설정해 모든 사용처에 공개되고(베타, 링크 순회 최대 3, 표현식 불가), 런타임 정의 파생 속성은 Workshop, Insight, Ontology SDK 요청 안에서만 쓰입니다(정식 출시, 표현식 가능).

<a id="expressions-and-link-based-derived-properties"></a>
## 표현식과 링크 기반 파생 속성 (Expressions and link-based derived properties)

링크 기반 파생 속성은 링크된 객체에서 값을 선택하거나 집계합니다. 온톨로지 정의 파생 속성과 런타임 정의 파생 속성 모두 링크 기반 계산을 지원합니다.

표현식은 원본(native) 속성이나, 링크 기반 및 집계 파생 속성을 사용해 산술 또는 날짜 계산을 수행합니다. 표현식은 런타임 정의 파생 속성에서만 사용할 수 있습니다. 계산된 속성은 같은 `withProperties` 연산 안에서 선언된 다른 계산된 속성을 참조할 수 없습니다. 대신 의존하는 속성을 다음 연산에서 선언합니다.

**설명**: 예를 들어 `totalComp = salary + bonus`를 만들고, 다시 `totalCompK = totalComp / 1000`을 만들고 싶다고 합시다. 두 정의를 한 번의 `withProperties` 호출 안에 함께 넣으면 `totalCompK`가 같은 호출 안의 `totalComp`를 참조하게 되므로 허용되지 않습니다. `withProperties`로 `totalComp`를 먼저 만든 뒤, 이어지는 두 번째 `withProperties`에서 `totalCompK`를 정의해야 합니다.

> **중간 요약**: 링크 기반 계산은 두 형태 모두 지원하지만 산술과 날짜 표현식은 런타임 정의에서만 가능하며, 같은 `withProperties` 안에서 계산 속성끼리 서로 참조할 수 없습니다.

<a id="availability"></a>
## 사용 가능한 곳 (Availability)

| 애플리케이션 | 지원 내용 |
|---|---|
| [Ontology Manager](../02_define-ontologies/02_object-and-link-types/03_properties/11_derived-properties.md) | 객체 타입에 온톨로지 정의 파생 속성을 설정합니다. |
| [Workshop](https://www.palantir.com/docs/foundry/workshop/derived-properties/) | 온톨로지 정의 파생 속성을 사용하거나, 일부 위젯에 쓸 런타임 정의 파생 속성을 모듈 수준에서 정의합니다. |
| [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/overview/) | 온톨로지 정의 파생 속성을 사용하거나, `withProperties` 연산으로 런타임 정의 파생 속성을 정의해 결과, 필터, 정렬, 집계에 사용합니다. |
| [Insight](https://www.palantir.com/docs/foundry/insight/table-insight/) | 온톨로지 정의 파생 속성을 사용하거나, 테이블 분석에 런타임 정의 파생 속성을 추가합니다. |

TypeScript Ontology SDK(OSDK 2.x)에서 `@osdk/client` 패키지의 최소 지원 버전은 `2.2.0-beta.x`입니다. 링크된 객체에서 속성을 선택하는 기능과 산술 또는 날짜 표현식을 사용하는 기능은 `2.4.0` 이상이 필요합니다. 자세한 내용은 [Developer Console](https://www.palantir.com/docs/foundry/developer-console/overview/)의 API 문서를 참고하세요.

> **중간 요약**: 파생 속성은 Ontology Manager(정의), Workshop, Ontology SDK, Insight(사용 및 런타임 정의)에서 쓸 수 있으며, TypeScript OSDK는 기능에 따라 `2.2.0-beta.x` 또는 `2.4.0` 이상이 필요합니다.

<a id="derived-properties-security"></a>
## 파생 속성 보안 (Derived properties security)

파생 속성은 계산에 사용된 모든 객체의 보안을 상속합니다. 접근 검사는 값을 합치기 전에 계산에 관여하는 각 객체마다 적용되며, 여러 단계 순회(multi-hop traversal)의 중간 객체도 포함됩니다.

그 결과 두 사용자가 **같은 객체의 같은 파생 속성에 대해 서로 다른 값을 볼 수 있습니다**. 각 사용자에게 계산된 값은 그 사용자가 볼 권한이 있는 원본 객체와 중간 객체만 반영합니다.

![Game World 객체 타입에 링크된 Quest 객체 수를 세고 가장 높은 보상을 반환하는 파생 속성. 한 지역에만 접근 권한이 있는 플레이어는 퀘스트 총 2개와 최고 보상 150을 보고, 모든 지역에 접근 권한이 있는 관리자는 퀘스트 34개와 최고 보상 1,200을 봅니다.](https://www.palantir.com/docs/resources/foundry/ontology/derived-properties-security-inheritance.png)

값을 리스트나 집합으로 모으는 집계는 모은 각 값의 보안 마킹(security marking)을 유지하므로, 리스트 안의 개별 값이 각자 자기 마킹을 가집니다. 자세한 내용은 [속성 보안 마킹](https://www.palantir.com/docs/foundry/security/property-security-markings/)을 참고하세요.

**설명**: 위 그림의 예를 숫자로 따라가 보겠습니다. Game World 객체 하나에 Quest 객체 34개가 링크되어 있고, 그중 2개만 플레이어가 접근할 수 있는 지역에 속한다고 합시다. 파생 속성 "퀘스트 수"를 계산할 때 플레이어의 요청에서는 접근 가능한 Quest 2개만 집계 대상이 되므로 2가 나오고, 관리자의 요청에서는 34개 모두 대상이 되므로 34가 나옵니다. 즉 파생 속성 값은 고정된 하나의 값이 아니라 "요청한 사용자가 볼 수 있는 데이터로 계산한 값"입니다.

> **중간 요약**: 파생 속성은 계산에 쓰인 모든 객체(중간 객체 포함)의 보안을 상속하므로, 같은 객체라도 사용자 권한에 따라 다른 값이 보일 수 있습니다.

<a id="performance-and-scale"></a>
## 성능과 규모 (Performance and scale)

파생 속성 값은 저장되거나 인덱싱되지 않고 조회 시점에 평가됩니다. 다만 플랫폼은 필터를 기반 객체 인덱스로 내려보내(push down) 파생 값을 계산하기 전에 처리해야 할 데이터를 줄이는 방식으로 많은 쿼리를 최적화할 수 있습니다.

성능은 필터를 적용한 뒤 남은 객체 수, 링크된 객체의 수와 중간 결과 크기, 집계 유형, 링크 순회 횟수에 따라 달라집니다. 파생 값으로 필터링하거나 정렬하려면 일반적으로 남아 있는 후보 객체 모두에 대해 그 값을 계산해야 합니다. 쿼리에 따라 일부 조인과 집계도 내려보낼 수 있습니다.

실행 임계값, 대체(fallback) 동작, 쿼리 설계 지침은 [온톨로지 쿼리 제한 사항](../02_define-ontologies/01_ontologies/05_usage/04_oss-limitations.md)을 참고하세요. 파생 속성 쿼리의 컴퓨팅 비용은 [쿼리 컴퓨팅 사용량](../02_define-ontologies/01_ontologies/05_usage/03_query-compute-usage.md)을 참고하세요. 파생 속성과 파이프라인에서 미리 계산한 값 중 무엇을 고를지에 대한 지침은 [온톨로지 구조 지침](../02_define-ontologies/07_ontology-structural-guidance.md)을 참고하세요.

**설명**: 필터 푸시다운(push down)은 계산 전에 걸러낼 수 있는 조건을 먼저 적용하는 최적화입니다. 예를 들어 부서 1만 개 중 `region = "APAC"`인 부서 200개에 대해서만 평균 급여를 보고 싶다면, 인덱스에서 200개를 먼저 골라낸 뒤 그 200개에 대해서만 평균을 계산하므로 1만 개 전부를 계산할 때보다 훨씬 적은 일을 합니다. 반대로 "평균 급여가 5000 이상인 부서"처럼 파생 값 자체로 필터링하면, 남은 후보 부서 모두의 평균을 먼저 계산해야 조건을 판단할 수 있습니다.

> **중간 요약**: 파생 속성은 조회 시점에 계산되므로 남은 객체 수, 링크된 객체 규모, 집계 종류, 링크 순회 횟수가 성능을 좌우합니다. 일반 속성 필터는 인덱스로 내려보내 계산량을 줄일 수 있지만, 파생 값으로 필터링하거나 정렬하면 후보 전체를 계산해야 합니다.

<a id="collection-limits"></a>
## 수집 개수 제한 (Collection limits)

**Collect list**와 **Collect set** 집계는 반환할 값의 개수 제한을 받을 수 있습니다. 이 제한은 사용자에게 반환되는 것을 제어할 뿐, 플랫폼이 평가하는 범위를 제한하지는 않습니다.

수집된 속성에 대한 필터, 정렬, 집계는 잘린 리스트가 아니라 **전체** 값 집합을 대상으로 실행됩니다. 따라서 객체가 반환받은 리스트에는 나타나지 않는 값으로 필터에 일치할 수 있습니다.

**주의**: 수집된 속성에 대한 필터는 수집 제한 안의 값만이 아니라 기반 값 전체를 검사합니다. 따라서 필터를 만족시킨 값이 반환된 리스트에 없어도 일치가 발생할 수 있습니다. 반환된 리스트는 제한만큼 잘리지만 필터는 그렇지 않습니다. 리듀서(reducer)도 똑같이 동작합니다. 리듀서는 수집 제한을 `1`로 설정한 것과 같지만, 반환하는 하나의 축약된 값만이 아니라 구성 값 전체를 대상으로 필터링합니다.

![Recipe 객체에서 Healthy를 검색한 결과. 레시피 태그를 모으는 Collect list 파생 속성의 표시 제한은 3입니다. Turkey Burger 레시피는 태그 중 하나가 Healthy이므로 일치하지만, 반환되는 것은 앞의 세 태그(Dinner, Weeknight, Grill)뿐입니다.](https://www.palantir.com/docs/resources/foundry/ontology/derived-properties-collection-limit-filtering.png)

**설명**: 위 그림을 데이터로 풀면 다음과 같습니다. Turkey Burger 레시피의 태그가 `Dinner`, `Weeknight`, `Grill`, `Healthy` 네 개이고 Collect list의 제한이 3이면, 화면에 보이는 값은 `[Dinner, Weeknight, Grill]`입니다. 그런데 "태그에 Healthy 포함" 필터는 네 개 전체를 검사하므로 이 레시피가 검색 결과에 나옵니다. 결과 화면만 보면 Healthy가 없는데 왜 일치했는지 헷갈릴 수 있으므로 이 동작을 알고 있어야 합니다.

> **중간 요약**: Collect list와 Collect set의 개수 제한은 반환되는 값에만 적용되고, 필터, 정렬, 집계는 전체 값을 대상으로 동작합니다. 그래서 반환된 리스트에 없는 값 때문에 필터에 일치할 수 있습니다.

<a id="limitations"></a>
## 제한 사항 (Limitations)

파생 속성은 활발히 개발 중이며, 온톨로지 정의 파생 속성은 베타 단계입니다. 아래 제한 사항은 현재 동작을 반영합니다.

<a id="all-derived-properties"></a>
### 모든 파생 속성 (All derived properties)

* **Object Storage v1:** 파생 속성이 포함된 쿼리에는 [OSv1](../06_ontology-architecture/01_overview-and-getting-started/03_osv1-osv2-migration.md)로 인덱싱된 객체 타입을 포함할 수 없습니다.
* **기본 키(Primary keys):** 기본 키(primary key) 속성은 파생 속성일 수 없습니다.
* **필수 속성(Required properties):** 파생 속성은 필수로 지정할 수 없습니다.
* **값 타입(Value types):** 파생 속성에는 값 타입(value type)을 직접 적용할 수 없습니다. 다만 파생 속성은 원본 속성의 값 타입을 상속합니다.
* **표시 형식(Display formatting):** 파생 속성에는 조건부 서식 규칙이나 값 서식을 설정할 수 없습니다.
* **인라인 액션(Inline actions):** 파생 속성에는 인라인 액션을 설정할 수 없습니다.
* **Automate:** [Automate](https://www.palantir.com/docs/foundry/automate/overview/) 조건은 [예약 모니터링(scheduled monitoring)](https://www.palantir.com/docs/foundry/automate/evaluation-frequency/#scheduled-monitoring)을 사용할 때만 파생 속성으로 필터링할 수 있습니다. [실시간 모니터링(live monitoring)](https://www.palantir.com/docs/foundry/automate/evaluation-frequency/#live-monitoring)은 파생 속성을 지원하지 않습니다.

<a id="ontology-defined-derived-properties"></a>
### 온톨로지 정의 파생 속성 (Ontology-defined derived properties)

* **링크 순회(Link traversals):** 파생 속성 하나당 최대 세 번의 링크 순회만 가능합니다.
* **산술 및 날짜 표현식(Arithmetic and date expressions):** 지원하지 않습니다. 온톨로지 정의 파생 속성은 링크 순회와 집계만 지원합니다. 산술이나 날짜 계산이 필요하면 대신 런타임 정의 파생 속성을 사용하세요.

<a id="runtime-defined-derived-properties"></a>
### 런타임 정의 파생 속성 (Runtime-defined derived properties)

* **연쇄 표현식(Chained expressions):** 산술 또는 날짜 표현식은 같은 `withProperties` 연산 안에서 선언된 다른 표현식을 참조할 수 없습니다. 대신 의존하는 표현식을 이어지는 별도의 `withProperties` 연산에서 선언하세요.

> **중간 요약**: 파생 속성은 OSv1 객체 타입과 함께 쿼리할 수 없고, 기본 키, 필수 속성, 직접적인 값 타입, 표시 서식, 인라인 액션, Automate 실시간 모니터링에 쓸 수 없습니다. 온톨로지 정의는 링크 순회 3회와 표현식 미지원, 런타임 정의는 같은 연산 내 표현식 연쇄 불가라는 제한이 있습니다.

## 정리

- 파생 속성은 다른 속성이나 링크된 객체로부터 조회 시점에 계산되는 읽기 전용 속성으로, 집계, 링크된 객체에서 선택, 표현식 계산의 세 가지 방식이 있습니다.
- 온톨로지 정의(Ontology Manager, 모든 사용처 공개, 베타)와 런타임 정의(Workshop, Insight, OSDK 요청 안에서만, 표현식 지원) 두 형태가 있습니다.
- 계산에 쓰인 모든 객체의 보안을 상속하므로 사용자마다 다른 값이 보일 수 있습니다.
- 저장이나 인덱싱이 아닌 조회 시점 계산이므로, 필터 후 남은 객체 수와 링크 규모가 성능을 좌우합니다.
- Collect list와 Collect set의 개수 제한은 반환 값에만 적용되고 필터는 전체 값에 적용되며, 기본 키, 필수 속성, OSv1 등에는 쓸 수 없는 제한이 있습니다.
