# 파라미터 드롭다운 결과 필터링 (Filter results of a parameter dropdown)

- 원문: https://www.palantir.com/docs/foundry/action-types/parameters-filter/
- 사이드바 위치: Define Ontologies > Action types > Parameters > Filter results of a parameter dropdown

이 페이지는 액션 폼의 드롭다운 메뉴에 나타나는 선택지를 제한하는 방법을 설명합니다. 객체가 수천 개인 객체 타입을 그대로 드롭다운에 보여 주면 사용자가 잘못된 객체를 고르기 쉬우므로, 필터와 Search Around로 "이 상황에서 고를 수 있는 값"만 남기는 것이 실무에서 중요합니다.

객체 참조가 아닌 다중 선택(multiple choice) 파라미터나 단일 객체 참조 파라미터에 필터를 추가하면, 파라미터의 드롭다운 메뉴에서 선택할 수 있는 허용 값이 결정됩니다.

<a id="multiple-choice-parameter-dropdown-menus"></a>
## 다중 선택 파라미터 드롭다운 메뉴 (Multiple choice parameter dropdown menus)

다중 선택 파라미터의 드롭다운 메뉴를 구성할 때 액션 편집자는 허용 값을 어떤 객체 집합(object set)의 속성 값으로만 줄일 수 있습니다. 이를 활용하면 링크된 객체의 속성을 기준으로 값을 표시하거나 미리 채울 수 있습니다. 이렇게 하려면 파라미터가 다중 선택을 표시하도록 설정되어 있는지 확인하고, **Get options from an object set**(객체 집합에서 선택지 가져오기)을 선택한 다음, 원하는 객체 집합을 구성하고, 파라미터 드롭다운 메뉴의 모든 허용 값을 담고 있는 속성을 선택합니다. 결과 객체 집합에 링크된 객체가 하나만 있고 파라미터가 필수라면, 파라미터 드롭다운 메뉴는 해당 속성 값으로 자동으로 미리 채워집니다. 결과로 나오는 다중 선택 옵션은 사용자가 볼 권한이 있는 객체들의 집합에서 만들어집니다. 다시 말해 객체 집합에서 다중 선택 옵션을 만들 때, 사용자는 접근 권한이 없는 객체의 속성은 보지 못합니다.

![속성 드롭다운 메뉴 구성](https://www.palantir.com/docs/resources/foundry/action-types/property_dropdown_configuration.png)

**설명**: 여기서 "다중 선택 파라미터"는 문자열 같은 일반 값을 정해진 선택지 중에서 고르게 하는 파라미터를 말합니다. 예를 들어 `Aircraft`에 링크된 `Seat Configuration` 객체들의 `layout` 속성 값(`"2-4-2"`, `"3-3-3"`)만 선택지로 보여 주는 식입니다. SQL로 쓰면 `SELECT DISTINCT layout FROM seat_configuration WHERE aircraft_id = :selected_aircraft` 결과를 드롭다운 항목으로 쓰는 것에 해당합니다.

<a id="object-dropdown-menus"></a>
## 객체 드롭다운 메뉴 (Object dropdown menus)

파라미터 구성 화면에서 액션 편집자는 필터와 Search Around를 지정해, 모든 액션 인터페이스(액션이 표시되는 모든 화면)의 드롭다운 메뉴에 나타나는 객체를 제한할 수 있습니다. 필터를 구성하면 액션 폼은 필터와 일치하는 객체만 담은 드롭다운 메뉴를 렌더링합니다. 선택된 값은 액션이 실행되기 전에 검증도 됩니다.

예를 들어 아래 객체 드롭다운 메뉴는 **Name**이 `Name` 파라미터의 값과 같은 **Stock Series**만 보여 주도록 구성되어 있습니다.

![객체 드롭다운 메뉴의 시작 집합](https://www.palantir.com/docs/resources/foundry/action-types/objectDropdownStartingSet.png)

아래 이미지는 `Name` 파라미터에 가능한 값을 보여 줍니다.

![객체 드롭다운 메뉴의 결과 폼](https://www.palantir.com/docs/resources/foundry/action-types/objectDropdownResultingForm.png)

<a id="properties-displayed-in-dropdown-menu-options"></a>
### 드롭다운 메뉴 옵션에 표시되는 속성 (Properties displayed in dropdown menu options)

드롭다운 메뉴 옵션에는 각 객체의 제목과 함께 객체 타입의 [주요 속성(prominent properties)](../../02_object-and-link-types/03_properties/05_property-metadata.md#metadata-reference)이 표시됩니다. 검색어와 일치하는 속성이 일치하는 텍스트가 강조된 상태로 먼저 표시되고, 그 뒤에 나머지 주요 속성이 표시됩니다. 값이 없는 주요 속성은 `No value`로 표시됩니다.

어떤 속성이 표시될지는 액션 타입이 아니라 Ontology Manager에서 객체 타입에 구성한 가시성(visibility)에 따라 결정됩니다. 사용자는 볼 권한이 있는 객체만 볼 수 있으며, 사용자가 볼 수 없는 속성 값은 표시되지 않습니다.

<a id="data-privacy-implications"></a>
### 데이터 프라이버시 영향 (Data privacy implications)

객체 파라미터에 새 검증 방식을 사용하면, 액션 타입을 볼 수 있는 모든 사람이 데이터를 볼 수 있게 될 가능성이 있습니다. 파라미터 필터에 민감한 정적 값이 있으면, 사용자는 필터링되는 기반 객체를 볼 수 없더라도 그 값은 볼 수 있습니다. [데이터 프라이버시 영향에 대해 더 알아보세요.](04_dropdown-security.md)

**설명**: 필터 조건에 직접 적어 넣은 값(예: `customer_id = "VIP-0042"`)은 객체 데이터가 아니라 액션 타입 설정의 일부입니다. 그래서 그 고객 객체를 볼 권한이 없는 사람도 액션 타입 설정을 볼 수 있다면 `"VIP-0042"`라는 문자열 자체는 알게 됩니다.

> **중간 요약**: 객체 드롭다운은 필터와 Search Around로 후보 객체를 제한하고, 선택 값은 실행 전에 다시 검증됩니다. 옵션에는 제목과 주요 속성이 권한 범위 안에서 표시되며, 필터의 정적 값은 액션 타입을 볼 수 있는 사람에게 노출될 수 있습니다.

<a id="supported-operations"></a>
## 지원되는 연산 (Supported operations)

<a id="filtering-on-a-property"></a>
### 속성으로 필터링 (Filtering on a property)

객체 드롭다운 메뉴는 지정한 속성이 제공된 값 중 하나와 일치하는 객체만 보여 줍니다.

![속성으로 필터링하는 객체 드롭다운 메뉴](https://www.palantir.com/docs/resources/foundry/action-types/object_dropdown_filtering_on_property.png)

비교할 값은 사용자가 정적으로 정의하거나, 다른 파라미터에서 가져오거나, `Object Reference` 파라미터의 속성에서 가져올 수 있습니다. 비교할 값이 둘 이상이면 결과는 **OR** 연산이 됩니다.

**설명**: 값이 `["Open", "In Progress"]` 두 개라면 조건은 `status = 'Open' OR status = 'In Progress'`, 즉 SQL의 `status IN ('Open', 'In Progress')`와 같습니다.

<a id="changing-the-starting-object-set"></a>
### 시작 객체 집합 바꾸기 (Changing the starting object set)

쿼리의 **시작 집합(starting set)은** 기본적으로 해당 객체 타입의 모든 객체로 설정되지만, 다른 타입으로 바꿀 수 있습니다. 시작 집합을 `ObjectReference` 목록 파라미터로 설정할 수도 있습니다.

![시작 집합을 바꾸는 객체 드롭다운 메뉴](https://www.palantir.com/docs/resources/foundry/action-types/object_dropdown_changing_starting_set.png)

<a id="search-arounds"></a>
### Search Around

Search Around는 현재 집합의 모든 객체에서 링크를 따라가 새로운 집합을 만듭니다. 예를 들어 `Github Issue of Current Employee`는 현재 집합의 `Employees`를 가져와, 그 `Employees`에 링크된 `Github Issues`로 이루어진 결과 집합을 만듭니다.

![Search Around를 사용하는 객체 드롭다운 메뉴](https://www.palantir.com/docs/resources/foundry/action-types/object_dropdown_search_around.png)

**설명**: Search Around는 SQL의 조인으로 링크된 쪽 행을 얻는 것에 해당합니다. 시작 집합이 직원 `E1`, `E2`이고 `Employee`와 `Github Issue` 사이에 담당자 링크가 있다면, 결과는 `SELECT i.* FROM github_issue i JOIN employee e ON i.assignee_id = e.employee_id WHERE e.employee_id IN ('E1', 'E2')`와 같은 이슈 집합입니다. 시작 집합 설정, 속성 필터, Search Around를 이어 붙이면 "현재 사용자의 팀원이 맡은 미해결 이슈"처럼 단계적인 조건을 만들 수 있습니다.

> **중간 요약**: 객체 드롭다운에서는 속성 필터(여러 값이면 OR), 시작 집합 변경, 링크를 따라가는 Search Around를 조합해 후보를 좁힐 수 있습니다.

## 정리

- 다중 선택 파라미터는 객체 집합의 속성 값을 선택지로 쓸 수 있고, 사용자의 권한 범위 안의 객체만 반영됩니다.
- 객체 참조 파라미터는 필터와 Search Around로 드롭다운 후보를 제한하며, 선택 값은 실행 전에 검증됩니다.
- 드롭다운 옵션에 보이는 속성은 객체 타입의 주요 속성 설정과 사용자 권한으로 결정됩니다.
- 필터에 넣은 민감한 정적 값은 액션 타입을 볼 수 있는 사람에게 노출될 수 있으므로 주의해야 합니다.
