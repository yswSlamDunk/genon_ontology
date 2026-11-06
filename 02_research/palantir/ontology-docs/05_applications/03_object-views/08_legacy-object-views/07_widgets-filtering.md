# 필터링 위젯 (Filtering)

- 원문: https://www.palantir.com/docs/foundry/object-views/widgets-filtering/
- 사이드바 위치: Applications > Object Views > Legacy Object Views > Filtering

이 페이지는 레거시(Legacy) Object View에서 사용자가 화면에 보이는 링크된 객체를 원하는 부분집합으로 좁혀 볼 수 있게 해 주는 필터 위젯(widget)들을 다룹니다. 다중 선택, 드롭다운, 버튼, 날짜 범위 필터 같은 개별 필터와, 필터가 적용되는 범위를 묶어 주는 컨테이너, 현재 걸린 필터를 요약해 보여 주는 위젯의 설정 방법을 설명합니다. 필터가 위젯과 탭 사이에서 어떻게 전달되는지(교차 필터링)를 이해하는 것이 이 페이지의 핵심입니다.

많은 Object View에서는 사용자가 차트, 표, 집계 지표, KPI 같은 시각적 구성 요소를 필터링할 수 있어야 합니다. **필터 위젯(Filter Widgets)은** 사용자가 여러 종류의 필터를 적용해 해당 Object View에 있는 링크된 객체(Linked Object) 중 특정 부분집합으로 좁혀 들어갈(drill-down) 수 있게 해 줍니다.

이 범주에는 다음과 같은 필터 위젯이 있습니다.

* 미리 정한 속성(property)으로 필터링합니다. 문자열, 숫자 값, 날짜를 [Multiselect Filter](#multiselect-filter), [Dropdown Filter](#dropdown-filter), [Button Filter](#button-filter), [Date Range Filter](#date-range-filter)로 필터링할 수 있습니다.
  * 더 유연한 필터링 기능이 필요하면 [Linked Object Filter Sidebar](#linked-object-filter-sidebar)를 사용합니다.
* 특정 필터를 현재 뷰의 일부에만 적용하려면 [Filter Sandbox Container](#filter-sandbox-container)를 사용합니다.
* 미리 정한 필터를 Object View 안의 일부 위젯에만 적용하려면 [Filter Container](#filter-container)를 사용합니다.
* Object View에 현재 적용된 모든 필터를 요약해 보려면 [Active Filters](#active-filters)를 사용합니다.

필터링만을 위한 이 핵심 필터링 위젯들 외에도, 시각화용이지만 어느 정도 필터링도 가능한 위젯(예: Charts)이 있습니다. [Conditional Container](08_widgets-layout.md#conditional-container)를 사용하면 사용자가 조작하는 필터에 따라 콘텐츠를 표시하거나 숨길 수 있습니다.

**설명**: 여기서 "필터"는 SQL의 `WHERE` 절에 해당합니다. 예를 들어 Airport JFK의 Object View에 도착 항공편 표가 있을 때, 사용자가 필터 위젯에서 항공사 "Delta"를 고르면 표는 `WHERE airline = 'Delta'` 조건을 만족하는 항공편만 보여 줍니다. 필터 위젯은 이런 조건을 사용자가 클릭으로 만들게 해 주는 UI입니다.

**자주 겪는 문제와 참고 사항:**

* Object View의 한 탭 안에 있는 여러 위젯에 걸쳐, 또는 여러 탭에 걸쳐 필터가 적용되게 하려면 **오른쪽 편집 패널의 "Settings" 아래에 있는 "cross-filtering"(교차 필터링) 체크박스를 반드시 체크해야 합니다**. 이 체크박스를 체크하지 않은 탭에는 필터가 적용되지 않습니다. <br><img src="https://www.palantir.com/docs/resources/foundry/object-views/cross-section-filtering.png" alt="교차 섹션 필터링 활성화" height="500"/>

* 필터를 **여러 탭에 걸쳐** 적용하려면, 필터를 공유하려는 모든 탭의 Settings에 있는 "filterSet value"가 똑같은 텍스트 값인지 확인하세요. 이 값은 대소문자를 구분합니다.
  * 이 경우 같은 filterSet 값을 쓰는 필터들은 같은 활성 필터의 영향을 받습니다. 예를 들어 Tab A와 Tab B가 같은 filterSet 값을 공유하면 Tab A에서 적용한 필터는 모두 Tab B에도 적용되며, 그 반대도 마찬가지입니다. <br><img src="https://www.palantir.com/docs/resources/foundry/object-views/filter-across-tabs.png" alt="탭 간 필터" height="500"/>

* 모든 필터 설정에서는 지금 편집 중인 객체 자체가 아니라, 그 객체에 링크된 객체를 선택합니다.
  * 예: "Airport"의 Object View를 설정하고 있고 여기에 "Flights"가 연결되어 있다면, 항공편에 대한 여러 시각화(타임라인, 차트, 모든 항공편 목록 표)가 있을 것이고, 필터는 "Flights"의 여러 속성(예: 항공사별 필터, 날짜별 필터, 출발 도시별 필터)에 걸고 싶을 것입니다.
  * 따라서 필터를 설정하기 전에 현재 객체가 다른 객체와 링크되어 있어야 합니다. 링크 설정은 Ontology Manager에서 합니다.

* 대부분의 필터 위젯은 사용자가 지금 보고 있는 객체의 현재 뷰에 필터를 로컬로 적용할 수 있는 선택적 기능만 추가합니다.
  * 대부분의 필터 위젯은 사용자에게 보이는 뷰를 기본으로 좁혀 두도록 필터를 미리 활성화해 둘 수 없습니다(Filter Container는 예외로, 미리 설정한 필터를 둘 수 있습니다).
  * 사용자는 현재 객체의 현재 뷰에서 필터를 활성화할 수 있지만, 다른 객체로 이동하거나 페이지를 새로 고치면 그 필터는 더 이상 적용되지 않습니다.

**설명**: filterSet value는 필터 상태를 공유하는 그룹의 이름표입니다. 동작 순서로 보면 다음과 같습니다. (1) Tab A와 Tab B의 filterSet value를 둘 다 `flights-main`으로 설정합니다. (2) Tab A에서 사용자가 항공사 필터로 "Delta"를 고릅니다. (3) 이 필터는 `flights-main` 그룹에 기록되므로, Tab B로 이동해도 Tab B의 위젯들이 "Delta" 항공편만 보여 줍니다. Tab C의 값이 `flights-other`라면 Tab C에는 적용되지 않습니다. 대소문자를 구분하므로 `Flights-main`은 다른 그룹으로 취급됩니다.

> **중간 요약**: 필터 위젯은 링크된 객체를 조건으로 걸러 보는 UI이며, 필터는 항상 현재 객체가 아니라 링크된 객체의 속성에 겁니다. 필터가 여러 위젯과 탭에 전달되려면 cross-filtering 체크박스와 같은 filterSet value가 필요하고, 대부분의 필터는 새로 고치면 사라집니다.

<a id="multiselect-filter"></a>
## 다중 선택 필터 (Multiselect Filter)

다중 선택 필터는 사용자가 여러 값으로 Object View를 필터링할 수 있게 하며, 값들 사이에는 "OR" 조건이 적용됩니다. 선택한 값 중 하나 이상을 만족하는 항목을 모두 남깁니다.

설정을 마치면 다음과 같이 보입니다.

![multiselect-filter](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hp-multi-select-filter-1.gif)

<a id="configuration"></a>
### 설정 (Configuration)

참고: 항상 필수인 설정에는 옆에 (\*) 표시가 붙어 있습니다.

* \[필수] **Linked Object to Filter(필터를 적용할 링크된 객체):** 이 필터를 적용할 링크된 객체를 선택합니다. 위젯 설정 화면은 지금 설정 중인 객체에 링크된 객체(Ontology Manager에서 정의한 것)만 선택지로 보여 줍니다.
  * 예: *Airport* Object View에 *Flights* 객체를 보여 주는 뷰가 있고, *Airport*와의 링크가 "*Arriving Flights*"와 "*Departing Flights*" 두 종류라고 합시다. 링크된 객체 "*Arriving Flights*"로 Multiselect Filter를 설정하면, 이 필터는 같은 객체 "*Arriving Flights*"를 사용하는 다른 모든 위젯에 적용됩니다.
* \[필수] **Property to Filter(필터링할 속성):** 필터링 기준으로 삼을 속성을 선택합니다. (1) 먼저 필터에 쓸 객체 타입을 선택하고, (2) 그 객체에서 필터링 기준이 될 속성을 선택합니다.
  * 선택하면 이 값 목록이 Object View에서 다중 선택 드롭다운이 있는 필터 상자로 사용자에게 제공됩니다. 이 필터의 영향을 받고 이 필터와 같은 객체를 공유하는 다른 모든 위젯은 선택한 속성 값(하나 또는 여러 개)을 가진 객체 인스턴스만 남도록 필터링됩니다.
  * 예: 20개 출발지에서 도착하는 항공편이 있는 공항 객체를 보고 있고, 이 출발지들에서 도착하는 모든 항공편을 보여 주는 표 위젯이 하나 더 있다고 합시다. 사용자는 `Arriving flights` 객체에 대한 다중 선택 필터를 고르고, 이어서 `Flights` 객체의 `Origin City` 속성을 고릅니다. 드롭다운 필터는 20개 출발지를 모두 사용자에게 보여 줍니다. 사용자가 그중 일부 출발지를 고르면 표 위젯은 그 출발지에서 도착한 항공편만 보여 줍니다.
* \[선택] **Label For Filter(필터 라벨):** Object View에서 필터 상자 옆에 사용자에게 표시됩니다.
* \[선택] **Maximum Number Of Filter Options(필터 선택지 최대 개수):** 필터링할 속성의 서로 다른 값을 몇 개까지 표시할지 정합니다. 기본값은 100입니다.

**자주 겪는 문제와 참고 사항:**

* 설정을 마친 뒤 필터가 Object View에 영향을 주게 하려면 오른쪽 설정 편집기의 settings에서 "allow cross-filtering" 체크박스를 체크해야 합니다(위 설명 참고).

**설명**: 다중 선택 필터에서 사용자가 `Origin City`로 Boston과 Chicago를 고르면 조건은 `WHERE origin_city IN ('Boston', 'Chicago')`, 즉 `origin_city = 'Boston' OR origin_city = 'Chicago'`와 같습니다.

<a id="dropdown-filter"></a>
## 드롭다운 필터 (Dropdown Filter)

이 필터는 속성 하나에 대해 단일 선택 드롭다운을 가진 필터를 하나 이상 둘 수 있게 하며, 사용자는 값 드롭다운으로 Object View의 다른 위젯을 필터링할 수 있습니다.

설정을 마치면 다음과 같이 보입니다.

![Dropdown Filter](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hp-dropdown-filter.gif)

<a id="configuration"></a>
### 설정 (Configuration)

설정하려는 드롭다운 필터 옵션마다 먼저 "Add Item"을 클릭해야 합니다. "Add Item"을 다시 클릭하는 것만으로 한 위젯 아래에 여러 드롭다운 필터를 추가할 수 있습니다(모두 나란히 표시됩니다).

항목을 추가하면 설정 메뉴에서 "Filter Type(필터 유형)"으로 두 가지 옵션을 제공합니다.

**옵션 1: Dynamic List(동적 목록)**

더 간단한 옵션으로, 대부분의 필터 위젯처럼 드롭다운에 쓸 객체와 속성을 쉽게 고를 수 있습니다.

* \[필수] **Linked Object to Filter(필터를 적용할 링크된 객체):** 이 필터를 적용할 링크된 객체를 선택합니다. 위젯 설정 화면은 지금 설정 중인 객체에 링크된 객체(Ontology Manager에서 정의한 것)만 선택지로 보여 줍니다.
* \[필수] **Property to Filter(필터링할 속성):** 필터링 기준으로 삼을 속성을 선택합니다. (I) 먼저 필터에 쓸 객체 타입을 선택하고, (II) 그 객체에서 필터링 기준이 될 속성을 선택합니다.
  * 선택하면 이 필터의 영향을 받고 이 필터와 같은 객체 타입에 관련된 다른 모든 위젯은, 모든 링크된 객체 중 해당 속성 값이 드롭다운에서 선택한 값과 같은 객체만 남도록 필터링됩니다.
* \[선택] **Label For Filter(필터 라벨):** Object View에서 필터 상자 옆에 사용자에게 표시됩니다.
* **Enable 'All' filter option toggle('All' 필터 옵션 사용 토글):** 필터가 필수여야 한다면, 즉 사용자가 반드시 값 하나를 고르게 하려면 이 토글을 끈 상태로 둡니다. 모든 값을 선택한 상태(어떤 값으로도 필터링하지 않음)가 가능해야 한다면 토글을 켭니다. 여러 값을 선택하려면 대신 Multiselect Filter 위젯을 선택하세요.

**옵션 2: Value List(값 목록)**

더 복잡한 옵션으로, 필터링할 값의 정확한 목록, 즉 전체 드롭다운 목록의 부분 목록을 직접 정의하려는 경우에 씁니다. 사용자에게 보여 줄 Dropdown Filter에 넣을 값을 하나하나 직접 입력해야 합니다. 설정 방법은 다음과 같습니다.

* \[필수] **Linked Object to Filter(필터를 적용할 링크된 객체):** 이 필터를 적용할 링크된 객체를 선택합니다.
* \[필수] **Property to Filter(필터링할 속성):** 필터링 기준으로 삼을 속성을 선택합니다. (I) 먼저 필터에 쓸 객체 타입을 선택하고, (II) 그 객체에서 필터링 기준이 될 속성을 선택합니다.
  * 선택하면 이 필터의 영향을 받고 이 필터와 같은 객체 타입에 관련된 다른 모든 위젯은, 모든 링크된 객체 중 해당 속성 값이 드롭다운에서 선택한 값과 같은 객체만 남도록 필터링됩니다.
* \[필수] **Filter property value(s)(필터 속성 값):** 사용자에게 보여 줄 이 드롭다운 필터에 넣을 값을 하나하나 직접 입력하고 "Create"를 클릭해 추가해야 합니다.
  * 입력한 값은 대소문자를 구분하며 입력한 순서대로 표시됩니다. 한번 입력한 값은 순서를 바꿀 수 없으며, 값을 삭제('X' 클릭)한 뒤 다시 입력하는 방법으로만 재배열할 수 있습니다.
  * 표시되는 값의 개수는 100개로 제한됩니다.
  * 'All' 옵션은 기본으로 제공됩니다. 원하면 이 옵션을 제거했다가 다시 추가할 수 있습니다("All", 대소문자 구분).
* \[선택] **Label For Filter(필터 라벨):** Object View에서 필터 상자 옆에 사용자에게 표시됩니다.

**자주 겪는 문제와 참고 사항:**

* 다음 경우에는 Dropdown filter 대신 Multiselect filter 사용을 고려하세요. (a) 둘 이상의 옵션을 선택하는 기능이 필요한 경우, (b) 드롭다운이 여러 개 필요하지 않은 경우(이 문제는 filter container로도 해결할 수 있습니다).
* Dropdown 위젯과 "Active Widget"의 상호 작용은 제한적입니다. "Enable 'All' filter option"이 켜져 있어도, 사용자가 Multiselect filter에서 "All"을 명시적으로 선택하지 않는 한 "Clear filter"를 할 수 없습니다.
* 설정을 마친 뒤 필터가 Object View에 영향을 주게 하려면 오른쪽 설정 편집기의 settings에서 "allow cross-filtering" 체크박스를 체크해야 합니다(위 설명 참고).
* 하나의 드롭다운 필터 위젯 아래에서 UI가 보여 줄 수 있는 드롭다운 필터 상자 수에는 한계가 있습니다(서로 다른 드롭다운 약 7\~8개). 드물게 한 Object View에 그보다 많은 드롭다운 필터가 필요하다면 Dropdown filter를 하나 더 추가하거나 Filter Container를 사용하세요.

**설명**: Dynamic List와 Value List의 차이는 선택지 목록을 어디서 가져오느냐입니다. Dynamic List는 실제 데이터에 있는 값을 자동으로 모아(SQL의 `SELECT DISTINCT airline FROM flights`와 같은 결과) 드롭다운에 보여 줍니다. Value List는 편집자가 입력한 값(예: "Delta", "United" 두 개)만 보여 주므로, 데이터에 "American"이 있어도 드롭다운에는 나타나지 않습니다.

> **중간 요약**: Multiselect Filter는 여러 값을 OR로 고르는 필터이고, Dropdown Filter는 값 하나만 고르는 필터입니다. Dropdown Filter는 데이터에서 값을 자동으로 모으는 Dynamic List와 편집자가 값을 직접 입력하는 Value List 방식이 있으며, 둘 다 cross-filtering 체크가 있어야 Object View에 영향을 줍니다.

<a id="button-filter"></a>
## 버튼 필터 (Button Filter)

이 위젯은 한 번 클릭하면 미리 정한 값 집합, 즉 텍스트(문자열) 값, 숫자 값 범위, 날짜 범위 중 하나로 필터링하는 버튼을 만듭니다. 버튼을 한 번 더 클릭하면 필터가 해제됩니다.

이 필터는 고정된 필터입니다. Object View 편집자(Object View Editor)가 한번 설정하면 최종 사용자가 바꿀 수 있는 설정은 없습니다.

버튼은 선택하거나 선택 해제할 때 색이 바뀝니다. 상태를 시각적으로 분명하게 보여 주려면 [Active Filters](#active-filters)를 추가할 수 있습니다.

설정을 마치면 다음과 같이 보입니다.
![Button Filter](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hp-buttons-filter.gif)

<a id="configuration"></a>
### 설정 (Configuration)

먼저 버튼 필터 유형을 선택합니다.

* Value List(값 목록): 텍스트 속성(문자열)을 필터링합니다.
* Range(범위): 숫자 속성(정수나 double 등)을 필터링합니다.
* Date Range(날짜 범위): 날짜 속성 목록으로 좁혀 필터링합니다.

세 가지 버튼 필터 유형 모두 다음 항목을 설정합니다.

* \[필수] **Object to Filter(필터를 적용할 객체):** 이 필터를 적용할 링크된 객체를 선택합니다.

* \[필수] **Property to Filter(필터링할 속성):** 필터링 기준으로 삼을 속성을 선택합니다. (I) 먼저 필터에 쓸 객체 타입을 선택하고, (II) 그 객체에서 필터링 기준이 될 속성을 선택합니다.
  * 선택하면 이 필터의 영향을 받고 이 필터와 같은 객체 타입에 관련된 다른 모든 위젯은, 모든 링크된 객체 중 속성 값이 필터 조건을 만족하는 객체만 남도록 필터링됩니다.

* \[필수] 여기부터는 버튼 유형마다 설정이 다릅니다.
  * **Value List:** 필터링할 값의 정확한 목록을 직접 입력하며, 값들 사이에는 "OR" 조건이 적용됩니다. 값은 대소문자를 구분하고 순서를 간단히 바꿀 수 없습니다. 순서를 바꾸려면 값 목록 전체를 삭제하고 다시 입력해야 합니다. "All" 옵션과 다른 특정 값 X를 함께 적용하면 필터는 값 X에만 적용됩니다.
  * **Range:** 숫자 값의 하한과 상한을 모두 제공합니다. 둘 중 하나 이상에 값을 입력합니다.
    * Lowerbound(하한) = 이상(크거나 같음)
    * Upperbound(상한) = 이하(작거나 같음)
    * 둘 다 채우면 범위 필터가 됩니다.
    * "보다 큼" 조건만 원하면 Upperbound의 0을 반드시 지우고, "보다 작음" 조건만 원하면 반대로 Lowerbound의 0을 지우세요.
  * **Date Range:** 두 가지 옵션을 고르는 토글을 제공합니다. 정확한 날짜("from 1\1\2019 to 31\12\2019") 또는 현재 시각 기준의 상대 날짜("Last Month"나 "Between two years ago and one year ago")입니다. 설정 자체는 표준 달력 날짜 선택기로 합니다.

* \[선택] **Button Label(버튼 라벨):** 버튼에 표시할 텍스트입니다. 선택 사항이지만 라벨이 있는 버튼을 만드는 것이 모범 사례입니다.

* \[선택] **Button color(버튼 색상):** 기본 색상은 회색입니다. 다른 색을 쓰려면 Blueprint 표준 색상(https://blueprintjs.com/docs/#core/colors 참고)이나 Palantir 내부 Blueprint 라이브러리를 사용합니다. 기본 색상 이름("Blue", "Red", "Yellow" 등)도 작동합니다.
  * 선택되지 않은 버튼은 흐린 색으로 표시됩니다. 클릭해야만 선택한 색으로 바뀝니다.
  * Date Range Button에는 버튼 색상을 고르는 옵션이 없습니다.

**자주 겪는 문제와 참고 사항:**

* 사용자에게 더 많은 유연성을 주려면 다음 사용을 고려하세요.
  * "Date Range Button Filter" 대신 "Date Range Filter"
  * "Value List Button Filter" 대신 "Multiselect Filter"나 "Dropdown Filter"
* 버튼 필터가 무엇을 하는지 알려 주는 방법은 두 가지입니다. (I) 버튼 라벨을 잘 붙입니다. (II) "Active Filter" 위젯을 추가합니다. 이 위젯은 버튼 필터를 클릭해 실제로 걸린 값을 포함해 모든 필터를 보여 줍니다.
* Button Filter는 기본적으로 꺼져 있으므로, 필터를 적용하려면 클릭해야 합니다.
* 설정을 마친 뒤 필터가 Object View에 영향을 주게 하려면 오른쪽 설정 편집기의 settings에서 "allow cross-filtering" 체크박스를 체크해야 합니다(위 설명 참고).

**설명**: Range 설정은 SQL 조건으로 옮기면 다음과 같습니다. Lowerbound만 100으로 채우면 `price >= 100`, Upperbound만 500으로 채우면 `price <= 500`, 둘 다 채우면 `price BETWEEN 100 AND 500`입니다. 입력란에 기본값 0이 들어 있을 수 있으므로, 하한만 쓰려는데 Upperbound에 0이 남아 있으면 `price >= 100 AND price <= 0`이 되어 결과가 비게 됩니다. 원문이 0을 지우라고 하는 이유가 이것입니다.

<a id="date-range-filter"></a>
## 날짜 범위 필터 (Date Range Filter)

Date Range Filter는 특정 날짜 속성을 기준으로 Object View를 날짜 범위로 좁혀 필터링할 수 있게 합니다.
설정을 마친 뒤 사용자가 날짜 범위를 고르고 **Submit을** 선택하면 Object View의 모든 위젯이 영향을 받습니다. 뷰에는 선택한 날짜 속성의 날짜가 범위 안에 있는 객체 인스턴스만 표시됩니다.

필터링하려는 객체의 object ID를 넣어야 하며, 이 객체는 보통 지금 설정 중인 객체에 링크된 객체입니다.

설정을 마치면 다음과 같이 보입니다.
![Date Range Filter](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hp-daterange-filter.gif)

<a id="configuration"></a>
### 설정 (Configuration)

* \[필수] **Object to Filter(필터를 적용할 객체):** 이 필터를 적용할 링크된 객체를 선택합니다.
* \[필수] **Property to Filter(필터링할 속성):** 필터링 기준으로 삼을 속성을 선택합니다. (I) 먼저 필터에 쓸 객체 타입을 선택하고, (II) 그 객체에서 필터링 기준이 될 속성을 선택합니다.
  * 선택하면 이 필터의 영향을 받고 이 필터와 같은 객체 타입에 관련된 다른 모든 위젯은, 모든 링크된 객체 중 선택한 날짜 속성이 이 날짜 범위 안에 있는 객체만 남도록 필터링됩니다.
* \[선택] **Label For Filter(필터 라벨):** Object View에서 필터 상자 옆에 사용자에게 표시됩니다.

**자주 겪는 문제와 참고 사항:**

* 설정을 마친 뒤 필터가 Object View에 영향을 주게 하려면 오른쪽 설정 편집기의 settings에서 "allow cross-filtering" 체크박스를 체크해야 합니다(위 설명 참고).

> **중간 요약**: Button Filter는 편집자가 미리 정한 값 목록, 숫자 범위, 날짜 범위로 한 번에 필터링하는 고정 버튼이며, 사용자는 켜고 끄는 것만 할 수 있습니다. Date Range Filter는 사용자가 직접 날짜 범위를 골라 Submit하는 필터입니다.

<a id="linked-object-filter-sidebar"></a>
## 링크된 객체 필터 사이드바 (Linked Object Filter Sidebar)

이 위젯은 유연한 필터링 경험을 제공합니다. 사용자는 해당 링크된 객체의 모든 속성 중에서 원하는 값 집합으로 현재 Object View를 필터링할 수 있습니다.

이 위젯은 선택의 폭이 넓은 대신 사용자에게는 더 복잡합니다. 다른 필터 위젯(예: Dropdown Filter, Button Filter)은 속성을 미리 설정해 두지만, 이 위젯은 사용자가 링크된 객체의 속성을 이해하고 알고 있어야 합니다.

설정을 마치면 다음과 같이 보입니다.

![Linked Object Filter Sidebar.gif](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hp-filter-sidebar.gif)

<a id="configuration"></a>
### 설정 (Configuration)

이 위젯의 설정은 Object View가 필터링 기준으로 삼을 링크된 객체를 선택하는 것뿐입니다. 나머지 설정, 즉 필터링할 구체적인 속성과 값을 고르는 일은 전적으로 사용자에게 맡겨지며 사용자 자신의 뷰에만 로컬로 적용됩니다. 사용자가 페이지를 새로 고치거나 다른 객체로 이동하면 이 필터들을 다시 설정해야 합니다.

**자주 겪는 문제와 참고 사항:**

* 한 속성에 대해 선택한 값들 사이에는 "OR" 조건이 적용됩니다. 서로 다른 속성의 값들 사이에는 "AND" 조건이 적용됩니다.
  * 예: "Airport" 객체에서 Object View 편집자가 링크된 객체 "Arriving Flights"에 대한 Linked Object Filter Sidebar를 추가했습니다. 사용자는 속성 "Month"로 필터링하면서 1월부터 6월까지만 고르고, 동시에 "Carrier Name"으로 필터링하면서 Delta Airlines와 United Airlines를 고를 수 있습니다. 그러면 뷰는 해당 공항에 도착한 항공편 중 1월부터 6월 사이(1월 또는 2월 ... 또는 6월)이면서 United 또는 Delta인 항공편만 보여 줍니다.

**설명**: 위 예를 SQL로 옮기면 `WHERE month IN ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun') AND carrier_name IN ('Delta Airlines', 'United Airlines')`입니다. 같은 속성 안에서는 `IN`(OR), 서로 다른 속성 사이에서는 `AND`로 결합됩니다.

<a id="filter-sandbox-container"></a>
## 필터 샌드박스 컨테이너 (Filter Sandbox Container)

Filter Sandbox Container를 사용하면 위젯들을 하나의 컨테이너로 묶어 그 안의 모든 필터를 샌드박스(sandbox)로 격리할 수 있습니다. 즉 컨테이너 안의 필터는 같은 컨테이너 안의 다른 위젯에만 영향을 주고, 그 위젯들에게서만 영향을 받습니다.

<a id="configuration"></a>
### 설정 (Configuration)

Filter Sandbox Container 위젯을 추가한 뒤 "Add Item"을 클릭해 기존 위젯을 컨테이너에 넣습니다.
위젯 선택기에서 추가할 위젯을 고릅니다.

나머지 설정 옵션은 필터 집합 식별자(filter set identifier)입니다. 기본적으로 새 필터 샌드박스마다 새로운 고유 값이 생성됩니다. 다음 대상과 필터를 공유하려면 이 값을 바꿀 수 있습니다.

* 다른 Filter Sandbox Container: 두 컨테이너의 filter set identifier를 같은 값으로 설정합니다.
* 다른 탭의 모든 위젯: 대상 탭에서 교차 섹션 필터링(cross-section filtering)을 켜고 그 탭의 filter set identifier를 같은 값으로 설정합니다.

**자주 겪는 문제와 참고 사항:**

* 이 컨테이너에서는 교차 필터링(컨테이너 안의 다른 위젯에 필터가 영향을 주고, 또 그 위젯들에게서 영향을 받는 것)이 항상 켜져 있습니다.
* 컨테이너 안의 위젯끼리 교차 필터링이 필요하다면 샌드박스 용도로는 Filter Container 위젯보다 이 컨테이너를 사용하세요. 미리 정한 필터의 영향만 받는 위젯이 필요하다면 필터 구독(subscription)을 끈 Filter Container를 사용하세요.
* 샌드박스 안의 교차 필터링과 미리 정한 필터가 모두 필요하다면 Filter Sandbox Container를 사용하고, 그 안에 필터 게시(publishing)와 구독을 모두 켠 Filter Container를 추가하세요.

**설명**: 샌드박스로 격리한다는 것은 필터 상태의 유효 범위(scope)를 제한한다는 뜻입니다. 프로그래밍 언어에서 함수 안에 선언한 지역 변수가 함수 밖에 보이지 않는 것과 같은 원리로, 컨테이너 안에서 고른 필터는 컨테이너 밖 위젯에 전달되지 않고, 컨테이너 밖에서 고른 필터도 안으로 들어오지 않습니다. filter set identifier를 같게 맞추는 것은 두 범위를 명시적으로 하나로 합치는 설정입니다.

> **중간 요약**: Linked Object Filter Sidebar는 사용자가 링크된 객체의 어떤 속성으로든 자유롭게 필터링하게 해 주며, 같은 속성 안은 OR, 서로 다른 속성 사이는 AND로 결합합니다. Filter Sandbox Container는 안에 든 위젯끼리만 필터를 주고받도록 범위를 격리하며, filter set identifier로 다른 컨테이너나 탭과 범위를 공유할 수 있습니다.

<a id="filter-container"></a>
## 필터 컨테이너 (Filter Container)

이 위젯은 *미리 정한 필터 집합*이 그 안의 위젯에만 적용되는, 위젯들의 묶음을 만듭니다.

이 필터 집합은 다음 속성 유형을 어떤 조합으로든 정의할 수 있습니다. (1) 텍스트(문자열) 값 목록, (2) 숫자 범위, (3) 날짜 범위.

이 위젯은 미리 정한 필터만 지원하도록 만들어졌으므로 필터 샌드박스 용도로 사용하지 마세요.

참고: 필터링 샌드박스 컨테이너가 필요하다면(즉 필터가 컨테이너 안에서만 적용되고 외부 필터의 영향을 받지 않게 하려면) 대신 [Filter Sandbox Container](#filter-sandbox-container)를 사용하세요.

<a id="configuration"></a>
### 설정 (Configuration)

Filter Container 설정은 두 부분으로 이루어집니다.

**1부: 컨테이너 안의 모든 위젯에 미리 설정한 필터 적용하기**

미리 정한 이 필터들은 기본적으로 *컨테이너 안의 위젯에만* 적용됩니다. 컨테이너의 미리 정한 필터는 다음 세 가지 필터 유형을 어떤 조합으로든 사용할 수 있습니다.

* Value List(값 목록): 텍스트 속성(즉 문자열)을 필터링합니다.
* Range(범위): 숫자 속성(즉 integer, double)을 필터링합니다.
* Date Range(날짜 범위): 날짜 속성 목록으로 좁혀 필터링합니다.

각 기본 필터마다 다음을 설정해야 합니다.

* \[필수] **Linked Object to Filter(필터를 적용할 링크된 객체):** 이 필터를 적용할 링크된 객체를 선택합니다. 위젯 설정 화면은 현재 객체에 링크된 객체(Ontology Manager에서 정의한 것)만 선택지로 보여 줍니다.
* \[필수] **Property to Filter(필터링할 속성):** 필터링 기준으로 삼을 속성을 선택합니다. (I) 먼저 필터에 쓸 객체 타입을 선택하고, (II) 그 객체에서 필터링 기준이 될 속성을 선택합니다.
  * 선택하면 이 컨테이너 안에서 같은 객체 타입에 관련된 다른 모든 위젯은, 모든 링크된 객체 중 속성 값이 필터 조건을 만족하는 객체만 남도록 필터링됩니다.
* \[필수] 여기부터는 필터 유형(Text Value List, Numeric Range, Date Range)마다 설정이 다릅니다.
  * **Value List:** 필터링할 값의 정확한 목록을 직접 입력하며, 값들 사이에는 "OR" 조건이 적용됩니다. 값은 대소문자를 구분하고 순서를 간단히 바꿀 수 없습니다. 순서를 바꾸려면 값 목록 전체를 삭제하고 다시 입력해야 합니다. "All" 옵션과 다른 특정 값 X를 함께 적용하면 필터는 값 X에만 적용됩니다.
  * **Range:** 숫자 값 범위의 하한과 상한을 모두 설정할 수 있습니다. 둘 중 하나 이상에 값을 입력합니다.
    * Lowerbound(하한) = 이상(크거나 같음)
    * Upperbound(상한) = 이하(작거나 같음)
    * 둘 다 채우면 범위 필터가 됩니다.
    * "보다 큼" 조건만 원하면 Upperbound의 0을 반드시 지우고, "보다 작음" 조건만 원하면 반대로 Lowerbound의 0을 지우세요.
  * **Date Range:** 두 가지 옵션을 고르는 토글을 제공합니다. 정확한 날짜("from 1\1\2019 to 31\12\2019") 또는 현재 시각 기준의 상대 날짜("Last Month"나 "Between two years ago and one year ago")입니다. 설정 자체는 표준 달력 날짜 선택기로 합니다.
* \[선택] **Filter Label(필터 라벨):** 문서화용 내부 라벨이며 사용자에게는 어디에도 표시되지 않습니다. 선택 사항입니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/widgets_hp-filter-container.png" alt="Filter Container 설정하기" height="700"/>

**교차 필터링 설정(Cross-filtering settings):**

* ***Subscribe to filters for nested sections?(중첩 섹션에서 필터를 구독할까요?)*** Filter Container가 컨테이너 밖에서 적용된 필터, 즉 컨테이너가 들어 있는 탭의 필터와 현재 탭과 교차 필터링을 공유하는 다른 탭의 필터에 영향을 받게 하려면 켭니다. 켜면 컨테이너 안의 다른 필터 위젯(예: 막대가 선택된 Chart 위젯이나 multiselect filter)의 필터도 받아들이게 됩니다.
* ***Publish filters from nested sections?(중첩 섹션의 필터를 게시할까요?)*** Filter Container 안의 필터가 컨테이너 밖, 즉 컨테이너가 들어 있는 탭과 현재 탭과 교차 필터링을 공유하는 다른 탭에도 적용되게 하려면 켭니다. 이 설정은 미리 정한 필터에는 적용되지 않으며, 컨테이너 안에 추가로 둔 필터 위젯에만 적용됩니다.

이 토글은 어떻게 사용할까요?

* 두 토글 모두 끔: 미리 정한 필터는 컨테이너 안에서만 적용되며, 컨테이너 안팎의 다른 필터를 게시하지도 받아들이지도 않습니다.
* Subscribe 토글만 켬: 컨테이너가 외부 필터의 영향을 받지만, 컨테이너 안에서의 필터링은 미리 정한 필터를 제외하면 작동하지 않습니다.
* Publish 토글만 켬: 컨테이너 안의 필터 위젯은 컨테이너 밖에만 적용되고 컨테이너 안에는 적용되지 않습니다. 컨테이너 안에는 미리 정한 필터만 적용됩니다.
* 두 토글 모두 켬: 이 컨테이너의 미리 정한 필터를 제외한 탭의 모든 필터가 모든 곳에 적용됩니다.

**설명**: 구독(subscribe)과 게시(publish)는 필터 정보가 흐르는 두 방향을 따로 켜고 끄는 스위치입니다. Subscribe는 "밖의 필터 조건을 안으로 받아들일지", Publish는 "안의 필터 위젯에서 고른 조건을 밖으로 내보낼지"를 정합니다. 예를 들어 탭에 항공사 Dropdown Filter가 있고 Filter Container 안에 "Month = Jan" 미리 정한 필터와 표 위젯이 있다고 합시다. Subscribe를 끄면 사용자가 탭의 드롭다운에서 "Delta"를 골라도 컨테이너 안 표는 계속 1월 항공편 전체를 보여 줍니다. Subscribe를 켜면 표는 1월이면서 Delta인 항공편만 보여 줍니다. 어느 경우든 "Month = Jan" 조건은 컨테이너 밖으로 나가지 않습니다.

**자주 겪는 문제와 참고 사항:**

* 미리 정한 필터는 컨테이너 안에서만 적용되며 컨테이너 밖의 어떤 위젯에도 적용되지 않습니다. 이는 미리 정한 필터에만 해당하며, 컨테이너 안에 설정할 수 있는 다른 필터 위젯에는 해당하지 않습니다. 샌드박스 컨테이너 기능을 찾고 있나요? [Filter Sandbox Container](#filter-sandbox-container)를 사용해 보세요.
* "Filter Container"의 미리 정한 필터는 UI에서 사용자에게 보이지 않으며, 다음 단계를 따르지 않으면 사용자가 제거할 수 없습니다.
  * Filter Container 안에 "Active Filter" 위젯을 추가해 필터를 표시합니다.
  * "Enable removing default filters" 토글이 켜져 있는지 확인합니다(기본값은 켜짐). 이 토글이 꺼져 있으면 "Active Filter"의 제거 옵션을 써도 사용자가 이 필터를 제거할 수 없습니다.
* Filter Container 안에서 필터를 적용하면 [Dropdown Filter](#dropdown-filter) 같은 필터 위젯에서 조건에 맞지 않는 선택지도 사라집니다. 이 동작을 원하지 않으면 대신 [Filter Sandbox Container](#filter-sandbox-container)를 사용하세요.

**2부: 위젯을 담는 컨테이너로서의 Filter Container**

이 컨테이너 안의 뷰는 다른 컨테이너와 똑같이 설정합니다. 추가하는 모든 위젯은 Filter Container의 미리 정한 필터를 구독하며, 그 위젯에 영향을 주도록 정의된 다른 필터도 함께 받습니다.

"Add Section"을 클릭하면 메인 Object View나 중첩 탭을 가진 다른 위젯(예: 모든 Container 위젯)에서 "Add Section"을 클릭할 때와 같은 설정 화면이 나타납니다.

**섹션 레이아웃(Section layout):**

Filter Container 안의 위젯을 세로로 쌓을지(하나 아래 다른 하나, 기본값) 가로로 놓을지(왼쪽에서 오른쪽으로 나란히) 정합니다.

> **중간 요약**: Filter Container는 안에 든 위젯에만 미리 정한 필터(값 목록, 숫자 범위, 날짜 범위)를 적용하는 컨테이너입니다. Subscribe 토글은 밖의 필터를 받을지, Publish 토글은 안의 필터 위젯 조건을 밖으로 내보낼지를 정하며, 미리 정한 필터 자체는 어떤 경우에도 컨테이너 밖에 적용되지 않습니다.

<a id="active-filters"></a>
## 활성 필터 (Active Filters)

이 위젯은 Object View에 현재 적용된 모든 필터의 요약을 보여 주며, 사용자가 개별 필터를 제거하거나 모든 필터를 지울 수 있게 합니다. 이 필터에는 필요한 설정이 없습니다.

Active Filter는 사용자가 Object View에 지금 어떤 필터가 걸려 있는지 이해하는 데 유용한 시각적 표시입니다. Object View에 필터링 위젯이 여러 개(차트를 이용한 필터링 포함) 있고, 특히 Filter Container나 Button Filter를 쓴다면 활성 필터를 볼 수 있게 하는 것이 사용자 경험에 중요합니다.

설정을 마치면 아래의 대화형 위젯처럼 왼쪽에 필터 아이콘이 있는 형태로 보입니다. 이 예에서는 여러 필터 위젯의 영향을 받고 있습니다.

![filter-summary](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-filter-summary-1.gif)

<a id="configuration"></a>
## 설정 (Configuration)

Active Filter 위젯에는 설정이 없습니다. 새 섹션으로 추가하기만 하면 됩니다.

**자주 겪는 문제와 참고 사항:**

* 이 위젯은 교차 섹션 필터링과 교차 탭 필터링을 공유하는 모든 섹션에서 적용된 필터를 모두 표시합니다.
* 일부 필터 위젯은 이 위젯과 상호 작용하지 않을 수 있습니다. 현재 이 위젯은 Dropdown filter로 적용한 필터를 제거하지 못하므로, 사용자는 여전히 드롭다운의 값을 직접 바꿔야 합니다. Dropdown이 기본적으로 값 하나로 제한할 때는 이 동작이 이해가 되지만, "All" 옵션이 켜져 있을 때도 마찬가지로 적용됩니다.

> **중간 요약**: Active Filters는 설정 없이 추가만 하면 현재 걸린 모든 필터를 요약해 보여 주고 개별 제거나 전체 해제를 제공하는 위젯입니다. 다만 Dropdown Filter로 건 필터는 이 위젯에서 제거할 수 없습니다.

## 정리

* 필터 위젯은 링크된 객체의 속성에 조건을 걸어 Object View의 다른 위젯이 보여 주는 데이터를 좁히는 도구입니다.
* 필터가 위젯과 탭 사이에 전달되려면 cross-filtering 체크박스를 켜고, 탭 간 공유에는 같은 filterSet value를 써야 합니다.
* Multiselect, Dropdown, Button, Date Range Filter는 미리 정한 속성으로 필터링하고, Linked Object Filter Sidebar는 사용자가 속성을 자유롭게 고르게 합니다(같은 속성은 OR, 다른 속성은 AND).
* Filter Sandbox Container는 필터 범위를 컨테이너 안으로 격리하고, Filter Container는 안의 위젯에만 미리 정한 필터를 적용하며 Subscribe/Publish 토글로 필터 흐름을 조절합니다.
* Active Filters는 현재 걸린 필터를 요약해 보여 주며, 대부분의 필터는 새로 고침이나 객체 이동 시 사라집니다.
