# 파생 속성 레퍼런스 (Derived properties reference)

- 원문: https://www.palantir.com/docs/foundry/ontology/derived-properties-reference/
- 사이드바 위치: Ontology search > Derived properties reference

이 페이지는 파생 속성(derived property)에서 쓸 수 있는 집계(aggregation)와 식(expression)을 표로 정리한 레퍼런스입니다. 파생 속성은 데이터소스에 저장된 열이 아니라, 질의할 때 링크로 연결된 객체들의 값을 모아 계산하는 속성입니다. 어떤 집계가 어떤 입력 타입을 받아 어떤 결과 타입을 내는지, 일반 속성과 무엇이 다른지, 성능 비용이 어느 정도인지를 확인할 때 참고합니다.

이 페이지는 [파생 속성](03_derived-properties.md)에서 사용할 수 있는 집계와 식을 정리하고, 각각을 어디서 쓸 수 있는지와 성능상 어떻게 비교되는지를 설명합니다.

<a id="aggregations"></a>
## 집계 (Aggregations)

집계는 여러 [링크된 객체](../02_define-ontologies/02_object-and-link-types/06_link-types/01_link-types-overview.md)의 값을 하나의 값으로 합칩니다. 링크 순회(link traversal)로 둘 이상의 객체에 도달할 수 있는 경우에는 항상 집계가 필요합니다. 온톨로지에 정의된(ontology-defined) 파생 속성과 런타임에 정의된(runtime-defined) 파생 속성 모두 집계를 지원합니다.

링크된 선택(linked selection)과 집계 안에 다른 파생 속성 정의를 넣을 수는 없지만, 그 속성 선택자(property selector)는 이미 범위 안에 있는 속성을 참조할 수 있습니다. 식은 아래에서 설명하듯 네이티브 속성이나 링크된 선택 및 집계의 결과를 사용할 수 있습니다.

다음 표는 각 집계를 Ontology Manager에서의 이름과 Ontology SDK에서의 메서드 이름으로 나열하고, 입력으로 받는 속성 타입과 결과로 만드는 값의 속성 타입을 보여 줍니다.

| Ontology Manager에서의 이름 | Ontology SDK 메서드 이름 | 소스 속성 타입 | 결과 속성 타입 |
|---|---|---|---|
| Count | `$count` | 해당 없음 | Long |
| Average | `avg` | 숫자형 | Double |
| Sum | `sum` | 숫자형 | 숫자형, 확장됨(아래 참고) |
| Minimum | `min` | 숫자형, 문자열, Boolean, 날짜, 타임스탬프 | 소스와 동일 |
| Maximum | `max` | 숫자형, 문자열, Boolean, 날짜, 타임스탬프 | 소스와 동일 |
| Approximate cardinality | `approximateDistinct` | 숫자형, 문자열, Boolean, 날짜, 타임스탬프 | Long |
| Exact cardinality | `exactDistinct` | 숫자형, 문자열, Boolean, 날짜, 타임스탬프 | Long |
| Collect list | `collectList` | `vector`를 제외한 모든 타입 | 소스 타입의 배열 |
| Collect set | `collectSet` | `vector`를 제외한 모든 타입 | 소스 타입의 배열 |
| 제공되지 않음 | `approximatePercentile` | 숫자형 | 소스와 동일 |

이 표에서 **숫자형**은 `byte`, `short`, `integer`, `long`, `float`, `double`, `decimal`을 포함합니다.

유효한 소스 속성 타입은 각각 스칼라일 수도 있고 그 타입의 배열일 수도 있습니다. 집계는 결과를 계산하기 전에 배열 입력을 평탄화(flatten)합니다. 예를 들어 `array<integer>` 속성에 대한 백분위수(percentile)는 `integer`를 반환합니다.

**설명**: SQL로 생각하면 집계는 `GROUP BY`와 함께 쓰는 `COUNT`, `AVG`, `SUM`, `MIN`, `MAX`, `COUNT(DISTINCT ...)`에 해당합니다. 예를 들어 Customer 객체마다 링크된 Order 객체가 여러 개 있을 때, "고객별 주문 수"는 Customer에서 Order로 링크를 순회한 뒤 Count로 집계한 파생 속성입니다. Collect list와 Collect set은 PostgreSQL의 `array_agg(...)`와 `array_agg(DISTINCT ...)`처럼 값들을 배열로 모읍니다. "카디널리티(cardinality)"는 서로 다른 값의 개수를 뜻하고, Approximate cardinality는 HyperLogLog 같은 근사 알고리즘으로 빠르게 추정한 값, Exact cardinality는 정확히 센 값입니다.

<a id="result-type-widening"></a>
### 결과 타입 확장 (Result type widening)

**Sum** 집계는 오버플로를 피하기 위해 숫자형 결과 타입을 확장(widen)합니다.

| 소스 타입 | 결과 타입 |
|---|---|
| `short`, `integer` | `long` |
| `long` | `long` |
| `float` | `double` |
| `double` | `double` |
| `decimal` | `decimal`(필요한 경우 정밀도(precision)는 늘리고 스케일(scale)은 줄임) |

**설명**: 32비트 `integer`의 최댓값은 약 21억입니다. 값이 10억인 `integer` 세 개를 더하면 30억이 되어 `integer` 범위를 넘으므로, 합계를 64비트 `long`으로 반환해 이런 오버플로를 막습니다. `decimal`의 정밀도는 전체 자릿수, 스케일은 소수점 아래 자릿수를 뜻합니다.

<a id="collection-behavior"></a>
### 수집 동작 (Collection behavior)

**Collect list**와 **Collect set** 집계는 다음 동작을 공유합니다.

* [속성 리듀서(property reducer)](../02_define-ontologies/02_object-and-link-types/03_properties/10_property-reducers.md)가 정의되어 있지 않으면 수집된 값의 순서는 보장되지 않습니다. 속성 리듀서가 정의되어 있으면, 리듀서가 적용되는지와 관계없이 Foundry는 리듀서를 사용해 반환 값을 정렬합니다.
* 해당 속성에 값이 없는 객체는 건너뛰므로, 결과 배열에는 null이 들어가지 않습니다.
* **Collect set**은 중복 값을 제거합니다. **Collect list**는 중복을 유지합니다.
* **Collect set**에서는 한도(limit)를 적용하기 전에 중복을 제거합니다. 한도는 고려하는 값의 **전체** 개수가 아니라 반환되는 **서로 다른** 값의 개수를 제어합니다.
* 한도의 기본값은 `10`이며 최대 `100`까지 올릴 수 있습니다.
* 한도는 플랫폼이 평가하는 값이 아니라 사용자에게 반환되는 값을 정합니다. 수집된 속성으로 필터링하기 전에 [수집 한도(collection limits)](03_derived-properties.md#collection-limits)에 대해 더 알아보세요.

속성 리듀서는 표시와 인터페이스 구현을 위해 수집된 배열에서 대표 값 하나를 고를 수 있습니다. 리듀서는 질의에 사용되는 전체 배열을 바꾸지 않습니다.

**설명**: 예를 들어 어떤 Customer에 링크된 Order 5개의 `status` 값이 `["paid", "paid", "shipped", null, "paid"]`라고 합시다. Collect list 결과는 null을 뺀 `["paid", "paid", "shipped", "paid"]`이고, Collect set 결과는 `["paid", "shipped"]`입니다. 한도가 1이면 Collect set은 서로 다른 값 중 1개만 반환하지만, 필터 조건 평가에는 플랫폼이 전체 값을 사용합니다.

<a id="type-limitations-for-aggregations"></a>
### 집계의 타입 제한 (Type limitations for aggregations)

벡터(vector) 속성은 파생 속성으로 집계하거나 선택할 수 없습니다. 파생 속성은 벡터 값을 만들어 낼 수 없습니다.

> **중간 요약**: 집계는 링크된 여러 객체의 값을 하나로 합치며, 둘 이상의 객체에 도달하는 링크 순회에는 반드시 필요합니다. Sum은 오버플로 방지를 위해 결과 타입을 넓히고, Collect list/set은 null을 제외하고 기본 10개(최대 100개)까지 값을 반환합니다. 벡터 속성은 집계할 수 없습니다.

<a id="expressions"></a>
## 식 (Expressions)

식은 값을 산술적으로 결합하거나 날짜의 일부를 추출합니다. 식은 [런타임에 정의된](03_derived-properties.md#ontology-defined-and-runtime-defined-derived-properties) 파생 속성에서만 사용할 수 있습니다.

**참고**: 현재 식에서는 정적 리터럴(static literal)을 지원하지 않습니다. 식 기반 파생 속성은 선언 순서상 앞에서 정의된 파생 속성, 구체적으로는 안쪽 객체 집합 식에서 정의된 파생 속성만 참조할 수 있습니다. 예를 들어 여러 `withProperties` 연산을 연결할 때, 어떤 파생 속성은 이후의 식 기반 연산에서 참조할 수 있지만, 같은 연산 안이나 선언 순서상 더 앞선 연산에서는 참조할 수 없습니다. 링크된 속성 기반 및 집계 기반 파생 속성은 다른 파생 속성을 전혀 참조할 수 없습니다.

**설명**: 정적 리터럴이 지원되지 않는다는 것은 `price * 1.1`처럼 상수 `1.1`을 식에 직접 넣을 수 없다는 뜻입니다. 식은 속성 값끼리만 결합합니다. 선언 순서 규칙은 SQL에서 같은 `SELECT` 절 안에서 정의한 별칭을 곧바로 다른 열 계산에 쓸 수 없고, 서브쿼리로 한 번 감싼 뒤 바깥 쿼리에서 써야 하는 것과 같은 구조입니다. 첫 번째 `withProperties`에서 `orderCount`를 정의하고, 두 번째 `withProperties`에서 `orderCount`를 사용하는 식을 정의하는 순서여야 합니다.

<a id="numeric-expressions"></a>
### 숫자 식 (Numeric expressions)

| Ontology SDK | 설명 |
|---|---|
| `add` | 두 값을 더합니다. |
| `subtract` | 첫 번째 값에서 두 번째 값을 뺍니다. |
| `multiply` | 두 값을 곱합니다. |
| `divide` | 첫 번째 값을 두 번째 값으로 나눕니다. |
| `max` | 두 값 중 큰 값을 반환합니다. |
| `min` | 두 값 중 작은 값을 반환합니다. |
| `abs` | 절댓값을 반환합니다. |
| `negate` | 값의 부호를 뒤집습니다. |

<a id="date-and-timestamp-expressions"></a>
### 날짜 및 타임스탬프 식 (Date and timestamp expressions)

| Ontology SDK | 설명 |
|---|---|
| `min` | 두 값 중 더 이른 값을 반환합니다. |
| `max` | 두 값 중 더 늦은 값을 반환합니다. |
| `extractPart` | 날짜의 구성 요소를 추출합니다. `DAYS`, `MONTHS`, `QUARTERS`, `YEARS`를 받습니다. |

식을 사용하려면 `@osdk/client` 패키지 `2.4.0` 이상 버전이 필요합니다.

> **중간 요약**: 식은 런타임 정의 파생 속성에서만 쓸 수 있고, 사칙연산, 최대/최소, 절댓값, 부호 반전, 날짜 구성 요소 추출을 지원합니다. 상수 리터럴은 쓸 수 없으며, 앞선 연산에서 정의한 파생 속성만 참조할 수 있습니다.

<a id="choose-to-select-or-aggregate"></a>
## 선택할지 집계할지 정하기 (Choose to select or aggregate)

속성을 직접 선택할 수 있는지는 각 링크 순회가 몇 개의 객체에 도달할 수 있는지에 달려 있습니다. 둘 이상의 객체에 도달할 수 있으면 집계가 필요합니다.

| 링크 체인 | 사용 가능한 연산 |
|---|---|
| 모든 순회가 최대 한 개의 객체에 도달 | 속성을 직접 선택하거나 집계 |
| 어느 순회든 둘 이상의 객체에 도달할 수 있음 | 집계가 필요 |
| 체인에 다대다(many-to-many) 링크가 포함됨 | 집계가 필요하며, 선택은 절대 허용되지 않음 |
| 외래 키가 배열인 일대다(one-to-many) 링크 | 집계가 필요하며, 양방향 모두에서 여러 객체에 도달할 수 있는 것으로 취급 |

**설명**: Order에서 Customer로 가는 링크는 주문 하나당 고객이 하나이므로(다대일) `customer.name`을 그대로 선택할 수 있습니다. 반대로 Customer에서 Order로 가면 고객 하나에 주문이 여러 개일 수 있으므로, 그중 어떤 값을 쓸지 정하는 집계(Count, Sum, Collect list 등)를 지정해야 합니다. SQL에서 일대다 조인 결과를 고객당 한 행으로 만들려면 `GROUP BY`와 집계 함수가 필요한 것과 같은 이유입니다.

<a id="compare-derived-properties-to-native-properties"></a>
## 파생 속성과 네이티브 속성 비교 (Compare derived properties to native properties)

정의된 파생 속성은 같은 요청 안에서 네이티브 속성과 거의 비슷하게 동작하지만, 몇 가지 차이가 있습니다.

| 연산 | 지원 여부 | 참고 |
|---|---|---|
| 결과에 반환 | 예 | 속성 타입과 관계없이 파생 속성은 명시적으로 선택해야 합니다. |
| 필터 | 예 | 정확히 일치, 범위, 접두사, 구문(phrase), 전문(full-text), 지리, 상대 날짜 필터를 포함합니다. |
| 정렬 | 예 | Workshop에서 파생 속성을 사용하는 객체 집합을 정렬하면 집합이 200행으로 제한됩니다. |
| 집계 | 예 | |
| 그룹화(Group by) | 예 | |
| 다른 파생 속성에서 참조 | 제한적 | 링크된 속성 기반 및 집계 기반 파생 속성은 다른 파생 속성을 참조할 수 없습니다. 식 기반의 지원 여부는 위에서 설명한 선언 순서에 따라 달라집니다. |
| 액션이나 함수로 편집 | 아니요 | 파생 속성은 읽기 전용입니다. |
| 기본 키로 사용 | 아니요 | |
| 링크 타입 외래 키로 사용 | 아니요 | |

**설명**: 파생 속성은 데이터베이스의 뷰(view)나 계산 열에 가깝게 동작합니다. 저장된 값이 아니라 질의할 때마다 계산되는 값이므로 직접 수정할 수 없고, 값이 고정되어 있어야 하는 기본 키나 외래 키로도 쓸 수 없습니다.

<a id="scale-and-performance-by-aggregation"></a>
## 집계별 규모와 성능 (Scale and performance by aggregation)

파생 속성 값은 질의 시점에 평가되며 인덱싱되지 않습니다. 성능은 주로 데이터 규모, 즉 평가되는 객체 수와 각 객체가 도달하는 링크된 객체 수에 따라 달라집니다. 상대적 비용은 요청의 지연 시간(latency)과 컴퓨팅 사용량을 반영합니다.

* 파생 속성을 **로드(loading)하는** 것, 즉 결과에 그 값을 반환하는 것은 모든 집계에서 비교적 저렴합니다. 비용은 대략 집계 요청 한 번과 비슷합니다.
* 파생 속성으로 **검색(searching)하는** 것, 즉 그 값으로 필터링하거나 정렬하는 것은 대부분의 집계에서 더 비쌉니다. **Collect list**와 **Collect set**은 예외입니다. 플랫폼은 이 집계들에 대한 검색을 소스 속성에 이미 있는 인덱스로 내려보낼(push down) 수 있는 경우가 많습니다.

| 집계 | 로드 비용 | 검색 비용 | 참고 |
|---|---|---|---|
| Count | 낮음 | 높음 | |
| Sum, Average, Minimum, Maximum | 낮음 | 높음 | |
| Approximate cardinality | 낮음 | 높음 | 정확한 개수가 꼭 필요하지 않다면 **Exact cardinality**보다 이것을 선호하세요. |
| Exact cardinality | 보통 | 높음 | |
| Approximate percentile | 낮음 | 높음 | 런타임 정의에서만 사용 가능합니다. |
| Collect list, Collect set | 낮음 | 낮음 | 비용은 표시 한도가 아니라 링크된 객체 수에 비례합니다. |

추가 지침:

* **근사 카디널리티를 선호하세요:** 정확한 카디널리티는 성능이 상당히 떨어집니다. 정확한 개수가 꼭 필요하고 추가 지연 시간을 감수할 수 있을 때만 사용하세요.
* **순회 횟수와 링크 카디널리티를 고려하세요:** 순회할 때마다 중간 결과 크기가 커질 수 있습니다. 전체 성능은 데이터 규모와 링크된 객체 수 모두에 달려 있습니다.
* **집계하기 전에 필터링하세요:** 링크된 객체 집합에 필터를 적용하면 집계가 처리해야 하는 객체 수가 줄어듭니다.
* **규모가 크면 미리 계산한 값을 고려하세요:** 파생 속성 때문에 받아들일 수 없는 지연이 생긴다면, 비정규화(denormalization)가 적절한 절충인 경우에 대해 [온톨로지 구조 지침](../02_define-ontologies/07_ontology-structural-guidance.md#performance-considerations)을 검토하세요.

플랫폼 전체의 실행 임계값과 대체(fallback) 동작은 [온톨로지 질의 제한 사항](../02_define-ontologies/01_ontologies/05_usage/04_oss-limitations.md)을, 컴퓨팅 비용은 [질의 컴퓨팅 사용량](../02_define-ontologies/01_ontologies/05_usage/03_query-compute-usage.md)을 검토하세요.

**설명**: 인덱스가 없는 값으로 필터링하거나 정렬하려면, 후보 객체마다 파생 속성 값을 모두 계산한 뒤에야 비교할 수 있습니다. 데이터베이스에서 인덱스 없는 계산식으로 `WHERE`나 `ORDER BY`를 하면 전체 스캔이 일어나는 것과 같은 원리입니다. 그래서 단순히 값을 보여 주는 로드보다 검색 비용이 큽니다. 비정규화는 이런 계산 결과를 미리 데이터셋의 열로 만들어 두어 인덱싱되게 하는 방법입니다.

> **중간 요약**: 파생 속성은 질의 시점에 계산되고 인덱싱되지 않으므로, 값을 보여 주는 로드는 저렴하지만 필터나 정렬 같은 검색은 비쌉니다(Collect list/set 제외). 근사 카디널리티 사용, 집계 전 필터링, 규모가 크면 사전 계산된 값 사용이 권장됩니다.

## 정리

- 파생 속성은 링크된 객체의 값을 집계하거나 식으로 결합해 질의 시점에 계산하는 읽기 전용 속성입니다.
- 둘 이상의 객체에 도달할 수 있는 링크 순회(다대다 포함)에는 Count, Sum, Collect list 등 집계가 반드시 필요합니다.
- 식은 런타임 정의 파생 속성에서만 쓸 수 있고, 상수 리터럴 없이 앞서 정의된 파생 속성과 속성 값만 결합합니다.
- 필터, 정렬, 집계, 그룹화는 가능하지만 편집, 기본 키, 외래 키로는 쓸 수 없습니다.
- 인덱싱되지 않으므로 검색 비용이 크며, 규모가 크면 비정규화로 미리 계산한 값을 고려합니다.
