# 속성 리듀서 (Property reducers)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/property-reducers/
- 사이드바 위치: Define Ontologies > Object and link types > Properties > Property reducers

이 페이지는 배열 속성(array property)의 여러 값 가운데 하나만 골라 화면에 보여 주거나 인터페이스 구현에 쓰게 하는 속성 리듀서(property reducer) 기능을 설명합니다. 리듀서는 저장된 데이터를 바꾸지 않고 "읽을 때 어떤 원소 하나를 대표로 내놓을지"만 정하는 설정입니다. 어떤 타입의 배열에 쓸 수 있는지, 구조체(struct) 배열에서 여러 리듀서로 동점을 처리하는 방법, 인터페이스와 구조체 주 필드(main field)와 함께 쓰는 방법, 제약 사항을 다룹니다.

**참고**: 베타(Beta). 속성 리듀서는 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며 사용자의 환경(enrollment)에서는 사용할 수 없을 수도 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다.

**속성 리듀서(property reducer)를** 사용하면 표시와 인터페이스 구현을 위해 [배열 속성](01_properties-overview.md#supported-property-types)을 배열 안의 값 하나로 변환할 수 있습니다. 리듀스(reduction)는 내부의 속성 타입이나 저장된 속성 데이터를 바꾸지 *않습니다*. 대신 속성 값을 읽을 때 배열에서 리듀스된 값에 접근할 수 있게 해 줍니다.

예를 들어 여러 점검 날짜가 들어 있는 배열에 리듀서를 적용하면, 표나 애플리케이션에서 속성을 볼 때는 가장 최근 날짜만 표시하면서도 질의와 기타 작업에는 전체 배열에 여전히 접근할 수 있습니다. [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)처럼 리듀서를 지원하는 애플리케이션에서는 마우스를 올리거나 펼친 보기에서 전체 배열을 볼 수도 있습니다.

리듀서는 숫자, 시간, 문자열, 불리언 기본 타입을 담은 배열 속성에서 동작합니다. [구조체](../04_structs/01_structs-overview.md) 배열은 지원되는 기본 타입을 사용하는 구조체 필드 중 어느 것을 기준으로든 리듀스할 수 있습니다. 속성 리듀서가 지원하는 기본 타입은 [아래 표](#supported-and-unsupported-base-types)를 참고하세요.

**설명**: "리듀스(reduce)"는 함수형 프로그래밍에서 여러 값을 하나로 줄이는 연산을 가리키는 말입니다. 예를 들어 `inspectionDates = [2024-01-15, 2024-06-30, 2024-03-02]`라는 배열 속성이 있을 때 "가장 최근" 리듀서를 걸면 화면에는 `2024-06-30`만 보입니다. 이는 SQL에서 `SELECT MAX(d) FROM UNNEST(inspectionDates) AS d`로 계산한 값을 보여 주는 것과 결과가 같지만, 저장된 배열 자체는 세 원소 그대로 남습니다.

<a id="when-to-use-property-reducers"></a>
## 속성 리듀서를 사용해야 할 때 (When to use property reducers)

다음과 같은 경우에 속성 리듀서를 사용합니다.

* 점검 날짜, 상태 업데이트, 측정값처럼 이력 데이터나 시간 데이터가 배열에 저장되어 있을 때.
* 속성의 전체 이력은 보존하면서, 표나 애플리케이션에서는 배열 값 중 가장 늦은/가장 이른 값, 가장 높은/가장 낮은 값, 첫 번째/마지막 값을 표시하고 싶을 때.
* 배열 속성으로 [인터페이스 속성](../../05_interfaces/03_implement-interface.md)을 제대로 구현하려면 배열이 아닌 타입이 필요할 때.

<a id="supported-and-unsupported-base-types"></a>
## 지원되는 기본 타입과 지원되지 않는 기본 타입 (Supported and unsupported base types)

리듀서는 배열 속성의 내부 기본 타입에 따라 동작합니다. 다음 표는 어떤 배열 하위 타입이 리듀서를 지원하고 어떤 하위 타입이 지원하지 않는지 분류합니다.

<a id="supported-base-types"></a>
### 지원되는 기본 타입 (Supported base types)

속성 리듀서는 다음 하위 타입을 담은 배열에서 사용할 수 있습니다.

| 분류 | 기본 타입 | 리듀서 옵션 |
|----------|-----------|----------------|
| **숫자(Numeric)** | `Byte`, `Short`, `Integer`, `Long`, `Float`, `Double`, `Decimal` | 가장 높은 값(Highest), 가장 낮은 값(lowest) |
| **시간(Temporal)** | `Date`, `Timestamp`| 가장 최근(Most recent, latest), 가장 오래된(Least recent, earliest) |
| **문자열(String)** | `String` | 첫 번째(First), 마지막(last) (사전순) |
| **불리언(Boolean)** | `Boolean` | true 우선(True first), false 우선(false first) |
| **구조체(Struct)** | [아래에 설명된](#support-for-struct-arrays) 지원되는 구조체 필드 중 하나를 기준으로 | 구조체 필드의 기본 타입에 따라 다름 |

<a id="unsupported-base-types"></a>
### 지원되지 않는 기본 타입 (Unsupported base types)

속성 리듀서는 다음 하위 타입을 담은 배열에서는 사용할 수 *없습니다*.

* `Attachment`
* `Cipher Text`
* `Geohash`
* `Geoshape`
* `Geotemporal Series Reference`
* `Marking`
* `Media Reference`
* `Time Dependent`
* `Vector`

<a id="support-for-struct-arrays"></a>
### 구조체 배열 지원 (Support for struct arrays)

구조체 배열에서 리듀서는 구조체 자체가 아니라 구조체 안의 특정 **필드**를 기준으로 동작합니다. 위에 나열된 [지원되는 기본 타입](#supported-base-types) 중 하나를 사용하는 구조체 필드로만 리듀스할 수 있습니다. 또한 동점(tie-breaking) 상황을 처리하기 위해 서로 다른 구조체 필드를 사용하는 리듀서를 여러 개 구성할 수 있습니다.

**설명**: 문자열의 "사전순(lexicographic)" 첫 번째와 마지막은 문자 코드 순으로 정렬했을 때의 맨 앞과 맨 뒤입니다. 예를 들어 `["banana", "apple", "cherry"]`에서 첫 번째는 `apple`, 마지막은 `cherry`입니다. 배열에 원래 들어 있던 순서(인덱스 0번, 마지막 인덱스)가 아니라는 점에 주의하세요.

> **중간 요약**: 리듀서는 숫자, 시간, 문자열, 불리언 배열과, 이런 타입의 필드를 가진 구조체 배열에 쓸 수 있습니다. 미디어, 지리 공간, 벡터 등 복합 타입 배열에는 쓸 수 없습니다.

<a id="configure-a-property-reducer"></a>
## 속성 리듀서 구성하기 (Configure a property reducer)

1. **Ontology Manager**로 이동합니다.
2. 왼쪽 패널의 **Resources** 아래에서 **Object types**를 선택해 객체 타입을 검색하고 선택합니다.
3. 객체 타입의 **Properties** 탭에서 구성할 배열 속성을 선택합니다.
4. 오른쪽에 열리는 속성 편집기 패널에서 **Interaction** 탭을 선택합니다.
5. **Reduce array** 영역까지 스크롤합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/property-reducers-interactions-tab.png" alt="Interactions 탭이 있는 속성 사이드바" width="800">

6. **Add array reducer**를 선택합니다.
7. 속성의 기본 타입에 맞는 원하는 [리듀서 옵션](#supported-base-types)을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/property-reducers-add-reducer-section.png" alt="리듀서 추가 영역" width="600" />

8. 변경 사항을 **Save**(저장)합니다.

<a id="configure-a-property-reducer-for-struct-arrays"></a>
## 구조체 배열에 속성 리듀서 구성하기 (Configure a property reducer for struct arrays)

구조체 배열은 리듀서를 가장 유연하게 쓸 수 있는 경우입니다. [지원되는 기본 타입](#supported-base-types)을 사용하는 구조체의 어떤 필드든 기준으로 리듀스할 수 있고, 동점 상황을 위해 리듀서를 여러 개 구성할 수 있습니다.

<a id="example-customer-review-history"></a>
### 예시: 고객 리뷰 이력 (Example: Customer review history)

`customerReviews`라는 구조체 배열 속성을 가진 `Product` 객체 타입이 있고, 이 구조체에 다음 필드가 있다고 합시다.

* `rating` (`Integer`): 1\~5점 별점입니다.
* `reviewDate` (`Date`): 고객이 리뷰를 올린 날짜입니다.
* `reviewerName` (`String`): 리뷰 작성자 이름입니다.
* `verifiedPurchase` (`Boolean`): 구매가 인증되었는지 여부입니다.

`Product` 객체 하나의 `customerReviews` 속성 예시 데이터는 다음과 같습니다.

| `rating` | `reviewDate` | `reviewerName` | `verifiedPurchase` |
|--------|-----------|--------------|-----------------|
| 5 | 2024-11-20 | Alice Chen | true |
| 3 | 2024-11-15 | Bob Smith | false |
| 4 | 2024-11-22 | Carol Lee | true |

<a id="configure-a-single-reducer"></a>
### 단일 리듀서 구성하기 (Configure a single reducer)

시작하기 전에 [속성 리듀서 구성 안내](#configure-a-property-reducer)와 [지원되는 기본 타입](#supported-base-types) 표를 확인하세요. 구조체 필드 하나에 리듀서 하나를 구성할 수 있으며, Foundry는 이를 사용해 구조체 배열을 구조체 하나로 리듀스합니다. 이때 리듀서가 구성된 필드를 기준으로 값을 정렬해 표시할 것을 고릅니다.

* **단일 리듀서:** 가장 최근 `reviewDate`를 표시합니다.
* **결과:** `2024-11-22`에 작성된 Carol Lee의 4점 리뷰가 담긴 구조체가 표시됩니다.

사용자는 여전히 전체 리뷰 이력을 질의하고 접근할 수 있습니다.

<a id="configure-multiple-reducers"></a>
### 여러 리듀서 구성하기 (Configure multiple reducers)

동점 상황을 처리하기 위해 리듀서를 여러 개 구성할 수 있습니다.

* **기본 리듀서(Primary reducer):** 구조체를 정렬해 `reviewDate`가 가장 최근인 구조체를 표시합니다.
* **대체 리듀서(Fallback reducer):** `rating`이 가장 높은 것을 표시합니다.
* **사용 사례:** 같은 날 리뷰 두 개가 올라왔다면 별점이 더 높은 리뷰를 표시합니다.

대체 리듀서는 기본 리듀서의 결과가 여러 항목일 때*만* 적용됩니다. 기본 리듀서가 항상 먼저 평가되고, 기본 기준에서 동점인 항목만 대체 리듀서로 다시 리듀스됩니다. 추가로 구성한 리듀서가 있으면 같은 방식이 반복됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/property-reducers-struct-configuration.png" alt="구조체 배열 리듀서 구성" width="600" />

**설명**: 여러 리듀서는 SQL의 `ORDER BY reviewDate DESC, rating DESC LIMIT 1`과 같은 순서로 동작합니다. 예를 들어 위 데이터에 `{rating: 2, reviewDate: 2024-11-22, reviewerName: "Dan Park"}`이라는 행이 하나 더 있다면, 첫 번째 리듀서(가장 최근 날짜)만으로는 Carol Lee(4점)와 Dan Park(2점)이 동점입니다. 그러면 두 번째 리듀서(가장 높은 별점)가 둘 중 Carol Lee의 리뷰를 고릅니다.

> **중간 요약**: 리듀서는 속성 편집기의 **Interaction** 탭에 있는 **Reduce array** 영역에서 추가합니다. 구조체 배열에서는 필드 하나를 기준으로 구조체 하나를 고르며, 여러 리듀서를 두면 앞의 기준에서 동점인 항목만 다음 기준으로 다시 고릅니다.

<a id="how-reducers-appear-in-applications"></a>
## 애플리케이션에서 리듀서가 표시되는 방식 (How reducers appear in applications)

리듀서를 지원하는 애플리케이션은 표나 목록 같은 간결한 보기에는 리듀스된 값을 표시하고, 펼친 보기나 마우스 올리기(hover) 기능을 통해 전체 배열에 접근할 수 있게 합니다. 이 방식 덕분에 사용자는 길게 나열된 배열 표현을 보지 않고도 데이터를 빠르게 훑어볼 수 있고, 필요할 때는 전체 배열을 살펴볼 수 있습니다.

예를 들어 애플리케이션은 표의 셀에 `2024-11-22`(가장 최근 날짜)만 표시하다가, 사용자가 그 셀에 마우스를 올리거나 셀을 펼치면 날짜 배열 전체를 보여 줄 수 있습니다.

<a id="use-property-reducers-with-interfaces"></a>
## 인터페이스와 함께 속성 리듀서 사용하기 (Use property reducers with interfaces)

속성 리듀서를 사용하면 배열 속성이 배열이 아닌 인터페이스 속성을 구현할 수 있습니다. 이렇게 하면 배열 데이터를 가진 객체 타입을 단일 값을 기대하는 [인터페이스 속성](../../05_interfaces/03_implement-interface.md)에 매핑할 수 있습니다.

<a id="example-render-the-most-recent-equipment-maintenance-date-through-an-interface-implementation"></a>
### 예시: 인터페이스 구현을 통해 가장 최근 장비 정비 날짜 표시하기 (Example: Render the most recent equipment maintenance date through an interface implementation)

**인터페이스:** `Asset`

* 속성: `lastMaintenanceDate` (`Date`)

**객체 타입:** `Equipment`

* 속성: `maintenanceHistory` (`Date` 배열)
  * 값: `[2024-01-15, 2024-03-22, 2024-11-01]`
* **리듀서:** 가장 최근 `maintenanceHistory` 날짜.
* **구현:** `Date` 배열 속성이 구성된 리듀서를 통해 단일 `Date`를 구현합니다. 사용자가 인터페이스를 통해 이 속성을 보면 `2024-11-01`이 보입니다.

리듀서 덕분에 `maintenanceHistory` 배열 속성을 단일 `Date` 값으로 표현할 수 있으므로, `Equipment` 객체 타입은 `Asset` 인터페이스를 구현할 수 있습니다. 사용자가 `Asset` 인터페이스를 통해 `Equipment` 객체를 보면 가장 최근 정비 날짜만 보입니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/property-reducers-interface-implementation.png" alt="리듀서를 통한 인터페이스 구현" width="700" />

**주의**: 객체 타입에서 리듀스된 배열 값을 사용해 [인터페이스 액션](../../03_action-types/09_actions-on-interfaces.md)의 파라미터인 인터페이스 속성을 충족시키면, 그 타입의 객체에 대해 액션을 호출할 때 오류가 반환됩니다. 다만 리듀스된 배열 값을 통해 인터페이스를 구현하지 않은 객체에는 여전히 그 인터페이스 액션을 사용할 수 있습니다.

**설명**: 인터페이스는 프로그래밍 언어의 인터페이스처럼 "이 속성들을 이 타입으로 제공해야 한다"는 계약입니다. `Asset` 인터페이스는 `lastMaintenanceDate`를 `Date` 하나로 요구하는데, `Equipment`에는 `Date[]`만 있으므로 원래는 타입이 맞지 않습니다. 리듀서가 `Date[]`를 `Date`로 바꿔 주는 어댑터 역할을 해서 구현이 가능해집니다.

> **중간 요약**: 리듀서를 쓰면 배열 속성이 단일 값을 요구하는 인터페이스 속성을 구현할 수 있습니다. 다만 그렇게 구현된 속성을 편집하는 인터페이스 액션은 오류를 냅니다.

<a id="combine-property-reducers-with-struct-main-fields"></a>
## 구조체 주 필드와 속성 리듀서 결합하기 (Combine property reducers with struct main fields)

속성 리듀서를 [구조체 주 필드(struct main field)](../04_structs/06_struct-main-fields.md)와 결합하면, 속성 표시가 가능해지고 구현할 수 있는 인터페이스의 개수와 형태가 늘어납니다.

구조체 배열인 `Locations` 속성을 가진 아래 `Event` 객체 타입을 생각해 봅시다.

**객체 타입:** `Event`

* 속성: `locations` (`Struct` 배열)
  * 구조체 필드: `streetName` (`String`), `dateCollected` (`Date`), `numberOfGuests` (`Integer`).
* **구성된 주 필드:** `streetName`
* **구성된 리듀서:** `dateCollected` 기준 가장 최근.

`streetName` 필드를 주 필드로, 가장 최근 `dateCollected`를 속성 리듀서로 구성하면 여러 인터페이스 구현 선택지가 생깁니다.

| 구성 | 구현 가능한 타입 |
|---------------|---------------|
| 둘 다 구성하지 않음 | `Struct Array`만 |
| 주 필드만 | `Struct Array`, `String Array` |
| 리듀서만 | `Struct Array`, `Struct` |
| **둘 다 구성** | `Struct Array`, `String Array`, `Struct`, `String` |

예를 들어 구조체 주 필드와 속성 리듀서를 모두 구성하면, `locations` 속성으로 인터페이스의 *단일* 문자열 속성을 충족시킬 수 있습니다. 아래 그림의 가상 `Event` 인터페이스에 있는 `Event street name`이 그런 예입니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/property-reducers-combination-single-string.png" alt="리듀서와 주 필드를 통한 단일 문자열 구현" width="700">

구조체 주 필드와 속성 리듀서를 모두 구성하면 변환은 다음과 같이 이루어집니다.

* 구성된 속성 리듀서를 적용해 날짜 기준으로 가장 최근 위치를 가져옵니다.
* 구성된 주 필드를 추출해 그 값을 문자열로 반환합니다.

즉, 속성 하나가 `Struct Array`, `String Array`, `Struct`, `String` 중 어느 타입을 요구하는 인터페이스든 구현할 수 있습니다.

**설명**: 두 변환은 서로 다른 방향으로 차원을 줄입니다. 리듀서는 배열을 원소 하나로 줄이고(`Struct[]`에서 `Struct`로), 주 필드는 구조체를 필드 하나로 줄입니다(`Struct`에서 `String`으로). 예를 들어 `locations = [{streetName: "Main St", dateCollected: 2024-05-01}, {streetName: "Oak Ave", dateCollected: 2024-07-10}]`이면 리듀서가 두 번째 원소를 고르고, 주 필드가 `"Oak Ave"`를 꺼냅니다. 주 필드만 있으면 각 원소에서 필드를 꺼내 `["Main St", "Oak Ave"]`(`String Array`)가 됩니다.

> **중간 요약**: 리듀서(배열을 원소 하나로)와 구조체 주 필드(구조체를 필드 하나로)를 함께 구성하면, 구조체 배열 속성 하나로 `Struct Array`, `String Array`, `Struct`, `String` 타입의 인터페이스 속성을 모두 구현할 수 있습니다.

<a id="limitations-and-considerations"></a>
## 제약 사항과 고려 사항 (Limitations and considerations)

* **리듀스된 값으로 직접 질의할 수 없음:** 리듀스된 값을 기준으로 필터링하거나 질의할 수 없습니다. 질의는 리듀스된 표현이 아니라 전체 배열을 대상으로 동작합니다.
* **리듀서나 구조체 주 필드로 구현한 경우 인터페이스 액션이 지원되지 않음:** 속성 리듀서나 [구조체 주 필드](../04_structs/06_struct-main-fields.md)를 통해 구현된 속성을 편집하는 [인터페이스 액션](../../03_action-types/09_actions-on-interfaces.md)은 그 타입의 객체에 대해 호출하면 오류를 반환합니다. 리듀스된 값과 구조체 주 필드 값은 내부의 객체 속성으로 거꾸로 변환할 수 없기 때문입니다. 예를 들어 배열에서 원소 하나를 고르는 리듀서에는 전체 배열을 재구성할 역연산이 없고, 필드 일부를 추출하는 구조체 주 필드는 나머지 필드를 채울 방법이 없습니다. 이런 속성을 대상으로 하지 않는 인터페이스 액션이나, 리듀서나 구조체 주 필드 없이 인터페이스를 구현한 객체를 대상으로 하는 인터페이스 액션은 정상적으로 동작합니다.

**설명**: 첫 번째 제약은, 예를 들어 "가장 최근 정비 날짜가 2024-10-01 이후인 장비"를 리듀스된 값으로 직접 필터링할 수 없다는 뜻입니다. 필터는 배열 전체에 대해 동작하므로 "배열 원소 중 하나라도 2024-10-01 이후인 장비"처럼 다른 의미가 될 수 있습니다. 두 번째 제약은 함수의 역함수 문제입니다. `max([1, 5, 3]) = 5`에서 결과 `5`만 보고 원래 배열 `[1, 5, 3]`을 복원할 수 없으므로, 인터페이스를 통해 "최근 정비 날짜를 2024-12-01로 바꿔라"라는 편집이 들어와도 배열의 어디를 어떻게 바꿔야 할지 정할 수 없습니다.

> **중간 요약**: 리듀스된 값으로는 필터링이나 질의를 할 수 없고, 리듀서나 구조체 주 필드로 구현된 인터페이스 속성은 역변환이 불가능하므로 인터페이스 액션으로 편집할 수 없습니다.

<a id="faqs"></a>
## 자주 묻는 질문 (FAQs)

<a id="can-i-change-or-remove-a-reducer-after-configuration"></a>
### 구성한 뒤에 리듀서를 바꾸거나 제거할 수 있나요? (Can I change or remove a reducer after configuration?)

예, Ontology Manager에서 언제든지 리듀서를 수정하거나 제거할 수 있습니다. 변경 사항은 재인덱싱(reindex)이 필요 없으며 즉시 적용됩니다.

<a id="what-happens-if-multiple-items-tie-for-the-reducer-criteria"></a>
### 여러 항목이 리듀서 기준에서 동점이면 어떻게 되나요? (What happens if multiple items tie for the reducer criteria?)

구조체 배열에서는 동점을 처리하기 위해 대체 리듀서를 구성할 수 있습니다. 대체 리듀서는 기본 리듀서에서 동점인 항목에 대해서만 평가됩니다. 원시 타입(primitive) 배열이나 대체 리듀서가 없는 구조체의 경우, 동점 값 중 하나가 결정적이지만 순서가 정해지지 않은 방식으로 반환됩니다.

<a id="can-i-use-reducers-with-edit-only-properties"></a>
### 편집 전용 속성에도 리듀서를 쓸 수 있나요? (Can I use reducers with edit-only properties?)

예, [편집 전용 속성(edit-only property)](06_edit-only-properties.md)에도 리듀서를 구성할 수 있습니다. 리듀서 구성은 속성에 백킹 열(backing column)이 있는지와 무관합니다.

<a id="do-reducers-function-across-all-applications"></a>
### 리듀서는 모든 애플리케이션에서 동작하나요? (Do reducers function across all applications?)

애플리케이션들이 리듀스된 속성 지원을 점진적으로 배포하고 있습니다. 어떤 속성에 리듀서를 구성했는데 아직 리듀서를 지원하지 않는 애플리케이션을 쓰더라도 기존 기능이 깨지지는 않으며, 그 속성은 계속 배열로 표시될 뿐입니다. 리듀서를 지원하는 애플리케이션에서만 리듀스된 값을 표시할 수 있습니다.

**설명**: "결정적이지만 순서가 정해지지 않은(deterministic but unordered)" 방식이란, 같은 데이터로 여러 번 읽으면 항상 같은 원소가 나오지만 그 원소가 "배열에서 먼저 나온 것"처럼 사용자가 예측할 수 있는 규칙으로 선택된다는 보장은 없다는 뜻입니다.

## 정리

- 속성 리듀서는 배열 속성의 저장 데이터는 그대로 두고, 읽을 때 원소 하나(가장 최근, 가장 큰 값 등)를 대표로 보여 주는 베타 기능입니다.
- 숫자, 시간, 문자열, 불리언 배열과 이런 필드를 가진 구조체 배열에 쓸 수 있으며, 구조체 배열에서는 여러 리듀서로 동점을 순차적으로 처리합니다.
- 리듀서를 쓰면 배열 속성이 단일 값 인터페이스 속성을 구현할 수 있고, 구조체 주 필드와 함께 쓰면 `Struct Array`, `String Array`, `Struct`, `String` 모두를 구현할 수 있습니다.
- 리듀스된 값으로는 질의할 수 없고, 리듀서나 주 필드로 구현된 속성은 인터페이스 액션으로 편집할 수 없습니다.
- 리듀서 변경은 재인덱싱 없이 즉시 적용되며, 지원하지 않는 애플리케이션에서는 그대로 배열로 표시됩니다.
