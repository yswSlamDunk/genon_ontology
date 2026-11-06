# 시각화 위젯 (Visualization)

- 원문: https://www.palantir.com/docs/foundry/object-views/widgets-visualization/
- 사이드바 위치: Applications > Object Views > Legacy Object Views > Visualization

이 페이지는 레거시(Legacy) Object View에서 현재 객체와 관련된 데이터를 표, 타임라인 같은 형태로 보여 주는 시각화 위젯(widget)을 다룹니다. 구체적으로는 링크된 객체를 표로 보여 주는 Linked Object View, 이벤트를 시간순 목록으로 보여 주는 Timeline, 이벤트를 그룹별 그래프와 표로 함께 보여 주는 Grouped Events Timeline and Table 위젯의 설정 방법과 자주 겪는 문제를 설명합니다. Object View는 객체 하나를 열었을 때 보이는 상세 화면이므로, 이 위젯들은 "이 객체와 연결된 데이터를 어떻게 한 화면에 정리해 보여 줄 것인가"를 정하는 도구입니다.

**시각화 위젯(Visualization widgets)은** 현재 객체와 관련된 데이터를 차트, 피벗 테이블, 타임라인, 지도, 그 밖의 시각화(단순 텍스트와 지표 포함)로 표시합니다.
다른 Foundry 앱에서 만든 시각화도 임베드할 수 있습니다. Slate 애플리케이션, Contour 보드, Foundry 리포트, Fusion 스프레드시트, Quiver 시계열이나 차트를 임베드하는 방법은 [Apps and Files](09_widgets-apps-files.md) 범주를 참고하세요.

**설명**: 이 문서에서 "링크된 객체(Linked Object)"는 현재 보고 있는 객체와 링크 타입으로 연결된 다른 객체를 뜻합니다. 예를 들어 Airport 객체 JFK를 보고 있다면, 링크 타입 "Arriving Flights"로 연결된 Flight 객체들(F100, F102 등)이 링크된 객체입니다. 관계형 데이터베이스로 말하면 `flights.destination = 'JFK'` 조건으로 조인해서 얻는 행들에 해당합니다.

<a id="linked-object-view"></a>
## 링크된 객체 뷰 (Linked Object View)

이 위젯은 주로 특정 타입의 링크된 객체 전체를 관련 속성(property)과 함께 *표(table)* 형태로 보여 줄 때 사용합니다. 이 표에서는 링크된 객체 중 일부를 선택해 다른 Foundry 앱에서 열거나, 설정된 Object Action을 실행할 수도 있습니다.
표 뷰 외에 단순 목록(list) 뷰와 카드(card) 뷰도 제공합니다.

다음은 필터 사이드바(Filter Sidebar)가 없는 Linked Object View(표)와 필터 사이드바가 있는 Linked Object View의 예입니다.

![필터 사이드바가 없는 Linked Object View 표](https://www.palantir.com/docs/resources/foundry/object-views/widgets_linked-object-view-without-sidebar.png)

![필터 사이드바가 있는 Linked Object View 표](https://www.palantir.com/docs/resources/foundry/object-views/widgets_linked-object-view-with-sidebar.png)

<a id="configuration"></a>
### 설정 (Configuration)

<a id="settings-tab"></a>
#### Settings 탭

설정은 세 부분으로 이루어집니다.

* Data(데이터)
  * *Linked Object to display(표시할 링크된 객체)*: 표시하려는 링크된 객체를 선택합니다. 위젯 설정 화면은 [온톨로지 설정](../../../02_define-ontologies/02_object-and-link-types/06_link-types/02_create-link-type.md)에 정의된 대로 현재 객체에 링크된 객체들을 선택지로 보여 줍니다. 객체 타입은 직접 링크로 고를 수도 있고, 중간 객체 타입을 거치는 전이적(transitive) 링크로 고를 수도 있습니다.
  * *Properties to display(표시할 속성)*:
    * All Properties: Prominent 또는 Normal로 정의된 속성을 모두 표시하고, Hidden 속성은 표시하지 않습니다. `Properties to Exclude` 선택기(아래 참고)로 특정 속성들을 제외할 수 있습니다.
    * Prominent Properties: Ontology Manager에서 Prominent로 정의된 속성만 표시합니다. `properties to exclude` 선택기(아래 참고)로 특정 속성들을 제외할 수 있습니다.
    * Specific Properties: 해당 링크된 객체의 모든 속성이 담긴 다중 선택 드롭다운을 열어 그중에서 고르게 합니다.
    * No Properties: 속성을 하나도 표시하지 않습니다.
  * *Properties to Exclude(제외할 속성)*: 표시에서 제외할 속성을 선택합니다. **All Properties와** **Prominent Properties** 옵션에서만 사용할 수 있습니다.
* View Options(뷰 옵션): 최종 사용자에게 기본으로 보여 줄 뷰 유형을 선택합니다. 최종 사용자는 UI(위젯 헤더)에서 나머지 두 뷰로 바꿀 수 있습니다.
  * Table view(표 뷰): 가장 많이 쓰는 뷰로, 모든 값을 표로 보여 주며 빠른 필터 검색을 제공합니다.
  * Card view(카드 뷰): 각 링크된 객체를 속성(1b에서 선택한 것)과 함께 압축된 카드로 보여 줍니다. 이 옵션은 표 뷰의 기능을 모두 갖추지는 않았습니다. 예를 들어 선택이나 Object Action을 지원하지 않습니다.
    * 참고: Card 표시 옵션에는 "Card Width(카드 너비)"라는 보조 설정이 있어 카드의 시각적 밀도를 정합니다. Table이나 List 뷰 옵션에는 영향을 주지 않습니다.
  * List view(목록 뷰): 선택한 링크된 객체의 모든 인스턴스를 단순 목록으로 보여 줍니다. 선택 기능도 없고 링크된 속성도 표시하지 않습니다.
* Search and Filtering(검색과 필터링): 표 뷰에 검색과 필터링 기능을 추가합니다.
  * Results limit(결과 개수 제한): 표시할 결과의 최대 개수를 제한합니다. 표시할 결과가 많을수록 뷰를 불러오는 데 시간이 더 걸립니다. 이 값과 최소/최대 높이 설정(아래 Format 탭 참고)이 함께 이 위젯이 전체 뷰에서 차지하는 크기를 결정합니다.
  * Enable search and filtering(검색과 필터링 사용): 켜면 위젯에 검색과 필터링 기능이 생깁니다. 기본(basic) 검색과 고급(advanced) 검색 중 하나를 고릅니다.
    * Basic: 위젯 헤더에 자유 텍스트 검색용 단순 검색창을 둡니다.
    * Advanced: 상세한 필터링 옵션이 있는 전체 필터 사이드바를 두며, 최종 사용자에게 사이드바를 기본으로 펼칠지 접을지 정하는 토글도 포함합니다. 기본 자유 텍스트 검색과 달리, 이 검색은 속성 타입에 따라 더 복잡한 필터링을 할 수 있습니다(문자열은 자유 텍스트와 다중 선택, 타임스탬프는 날짜 범위, double/integer는 숫자). 이 검색창은 레거시 Object Explorer의 기능과 UI를 기반으로 합니다.

**설명**: Prominent, Normal, Hidden은 Ontology Manager에서 각 속성에 지정하는 표시 수준입니다. 예를 들어 Flight 객체 타입에 `flight_id`(Prominent), `origin`(Normal), `internal_row_hash`(Hidden) 세 속성이 있으면, All Properties를 고르면 `flight_id`와 `origin`이 표시되고, Prominent Properties를 고르면 `flight_id`만 표시됩니다. Results limit는 SQL의 `LIMIT` 절처럼 가져오는 행 수의 상한을 정하는 설정입니다.

**Format 탭:**

위젯 설정의 Format 탭에서는 기본 항목인 Title, Icon, Info, Layout 외에 섹션의 최소 높이와 최대 높이를 조절할 수 있습니다(선택 사항).

**자주 겪는 문제와 참고 사항:**

* 이 위젯은 토글이 켜져 있으면 다른 위젯의 필터에 *영향을 받지만*, 필터 사이드바가 열려 있더라도 교차 필터링(cross-filtering)을 공유하는 다른 위젯에 *필터를 게시(publish)하지는 않습니다*. 결과적으로 내부 필터는 이 객체 표 위젯 안에서만 작동합니다.
* 조건부 서식(Conditional Formatting)과 값 렌더러(Value Renderers): 표의 값은 조건부 서식과 값 렌더러로 표시 방식을 바꿀 수 있습니다.

**설명**: "필터를 게시한다"는 것은 한 위젯에서 사용자가 고른 필터 조건을 같은 화면의 다른 위젯에도 전달해 함께 걸러지게 한다는 뜻입니다. 이 위젯은 다른 위젯이 보낸 필터 조건은 받아서 자기 표에 적용하지만, 자기 사이드바에서 건 조건은 다른 위젯으로 보내지 않습니다. 필터를 주고받는 방식은 [Filtering](07_widgets-filtering.md) 페이지에서 자세히 다룹니다.

> **중간 요약**: Linked Object View는 현재 객체에 링크된 객체들을 표, 카드, 목록 중 하나로 보여 주는 위젯입니다. 표시할 속성, 기본 뷰, 결과 개수 제한, 기본/고급 검색을 설정할 수 있으며, 다른 위젯의 필터는 받지만 자기 필터는 내보내지 않습니다.

<a id="timeline"></a>
## 타임라인 (Timeline)

이벤트를 날짜와 시간 순으로 정렬해 위에서 아래로 표시하는 시간순 목록을 만듭니다. 이 타임라인은 타임스탬프를 하나 이상 가진 링크된 객체로 구성됩니다. 보통 이 객체는 이벤트, 즉 시작 타임스탬프와 종료 타임스탬프로 어떤 기간을 정의하는 객체입니다.
이 위젯은 현재 객체에 직접 링크되었거나 다른 링크된 객체를 거쳐 링크된 객체 타입을 하나 이상 포함할 수 있습니다. 또한 아래 예처럼 같은 이벤트를 서로 다른 날짜 속성으로 표시할 수도 있습니다.

그래프 형태의 타임라인이 필요하면 [Grouped Events Timeline and Table](#grouped-events-timeline-and-table) 위젯을 사용하세요.

![Timeline](https://www.palantir.com/docs/resources/foundry/object-views/widgets_timeline.png)

<a id="configuration"></a>
### 설정 (Configuration)

<a id="settings-tab"></a>
#### Settings 탭

* **링크된 객체(이벤트) 하나 이상 추가하기**: 먼저 "Add Event Type"을 클릭해 타임라인에 표시할 링크된 객체 타입을 하나 이상 추가합니다. 여러 종류의 링크된 객체를 추가할 수 있습니다.
  * 완전히 다른 이벤트인 서로 다른 객체 타입을 한 타임라인에 표시합니다. 예: Aircraft에 링크된 객체 중 Flights 이벤트와 Aircraft Maintenance 이벤트를 함께 표시.
  * 같은 링크된 객체 타입의 이벤트를 서로 다른 날짜 속성으로, 또는 서로 다른 종류의 링크로 표시합니다. 예:
    * Airport 객체에 링크된 Flight 이벤트를 서로 다른 날짜 속성 (1) "Planned Arrival Time", (2) "Actual Arrival Time", (3) "Expected Departure Time"으로 같은 타임라인에 표시합니다. 타임라인은 모든 항공편을 시간순 목록으로 보여 주며, 이 경우 각 항공편은 최대 3번 나타납니다.
    * Airport 객체에 링크된 Arriving Flights와 Departing Flights를 같은 타임라인에 함께 표시할 수 있습니다.
* **추가할 이벤트 객체의 타입 선택하기**: 추가하려는 이벤트 객체마다 해당 객체 타입의 세부 사항을 설정합니다.
  * 링크된 객체 타입을 선택합니다. 직접 링크된 객체(Linked Object) 또는 확장 링크(Extended Link) 중 하나입니다.
    * 직접 링크된 객체의 예: 현재 객체가 Airport이고 Arriving Flights와 Departing Flights의 타임라인을 표시하려는 경우.
    * 확장 객체(2단계)의 예: 현재 객체가 Airport이고, 그 Airport에 링크된 Arriving Flights에 다시 링크된 모든 Aircraft 객체를 타임라인으로 표시하려는 경우.
* **타임라인에서 이벤트 정렬에 쓸 날짜 속성 정하기**: 타임라인의 이벤트를 정렬할 기준이 되는 링크된 객체의 속성을 선택합니다. 이 속성은 타임스탬프나 날짜여야 하므로, 설정 화면은 그런 속성만 제안합니다.
* **링크된 객체에서 표시할 속성 선택하기**.
  * 표시할 속성을 선택합니다.
    * All Properties: 링크된 객체에 속성이 많으면 화면이 복잡해져 타임라인을 훑어보기 어려우므로 권장하지 않습니다.
    * Prominent Properties: Ontology Manager에서 Prominent로 정의된 속성만 표시합니다.
    * Specific Properties: 해당 링크된 객체의 모든 속성이 담긴 다중 선택 드롭다운을 열어 그중에서 고르게 합니다.
    * No Properties: 타임라인에 링크된 객체의 제목만 표시합니다.
  * 제외할 속성을 선택합니다. 앞의 두 옵션인 All Properties와 Prominent Properties에서만 사용할 수 있습니다.
* 타임라인의 각 이벤트에 **표시할 제목 선택하기**. 세 가지 옵션이 있습니다.
  * **Object Name(객체 이름)을** 제목으로 사용(예: 이벤트 이름): 가장 많이 쓰는 옵션이며 기본값입니다.
  * **Date Property name(날짜 속성 이름)을** 제목으로 사용: 한 링크된 객체의 이벤트를 둘 이상의 속성(예: "Planned Arrival Time", "Actual Arrival Time", "Expected Departure Time" 등)으로 표시할 때 유용합니다. 참고로 이 경우 서로 다른 속성에 기반한 각 링크는 Timeline 위젯 안에서 따로 설정해야 합니다(위 첫 번째 항목 참고).
  * **Custom Name(사용자 지정 이름)**: 해당 타입의 모든 링크된 객체에 자유 텍스트 설명을 붙이는 옵션입니다. 예를 들어 Arriving Flights와 Departing Flights를 같은 타임라인에 연결했다면, 모든 Arriving Flights에는 "Arrival", 모든 Departing Flights에는 "Departure"라는 제목을 붙이고 싶을 수 있습니다.

**설명**: "같은 이벤트를 서로 다른 날짜 속성으로 표시"한다는 것은 다음과 같은 동작입니다. Flight 객체 F100에 `planned_arrival = 09:00`, `actual_arrival = 09:20` 두 속성이 있다고 합시다. 정렬 기준을 `planned_arrival`로 하는 항목과 `actual_arrival`로 하는 항목을 각각 추가하면, 타임라인에는 F100이 09:00 위치에 한 번, 09:20 위치에 한 번, 모두 두 번 나타납니다. 이때 제목을 Date Property name으로 정하면 두 항목 중 어느 것이 계획 시각이고 어느 것이 실제 시각인지 구분할 수 있습니다.

<a id="format-tab"></a>
#### Format 탭

위젯 설정의 Format 탭에서는 기본 항목인 Title, Icon, Info, Layout 외에 섹션의 최소 높이와 최대 높이를 조절할 수 있습니다(선택 사항).

<a id="common-issues-and-notes"></a>
### 자주 겪는 문제와 참고 사항 (Common issues and notes)

* 이 위젯은 검색과 정렬(오래된 순, 최신 순)을 지원합니다. 그러나 필터링은 지원하지 않으므로 필터의 영향을 받지 않습니다. 필터링 기능이 필요하면 [Grouped Events Timeline and Table](#grouped-events-timeline-and-table) 위젯 사용을 고려하세요.
* 이벤트를 단순 시간순 목록이 아니라 그래픽 타임라인으로 표시하려면 [Grouped Events Timeline and Table](#grouped-events-timeline-and-table) 위젯 사용을 고려하세요.
* 간트 차트(Gantt chart) 형태의 타임라인이 필요하면 "Linked Objects Gantt Chart" 위젯이 있습니다. 이 위젯을 사용할 수 없다면 Palantir 담당자에게 문의하세요. 이 위젯은 프로젝트 일정처럼 시작일과 종료일이 분명한 소수의 이벤트를 표시할 때 적합합니다.
* 시계열(Timeseries) 시각화가 필요하면 Object View에 임베드할 수 있는 Quiver에 관해 Palantir 팀에 문의하세요. X축에 날짜/시간 속성을 두는 Charts 위젯을 사용하거나 Contour 또는 Quiver 차트를 임베드할 수도 있습니다.
* 날짜가 없는 이벤트는 이벤트 목록에 표시되지 않습니다. 누락된 이벤트가 있다는 메시지가 사용자에게 표시됩니다.
* 성능상의 이유로 기본적으로 링크된 객체 50개만 표시합니다. 사용자가 목록을 아래로 스크롤하면 추가 객체가 100개씩 나타납니다.

**설명**: 처음에 일부만 불러오고 스크롤할 때 나머지를 덧붙여 불러오는 방식을 페이지네이션(pagination) 또는 무한 스크롤이라고 합니다. 링크된 객체가 수천 개일 때 한 번에 모두 가져오면 응답이 느려지므로, 첫 화면에 필요한 만큼만 가져오는 것입니다.

> **중간 요약**: Timeline 위젯은 날짜 속성을 가진 링크된 객체를 시간순 목록으로 보여 줍니다. 여러 객체 타입이나 같은 객체의 여러 날짜 속성을 한 타임라인에 넣을 수 있고, 표시할 속성과 제목 방식을 고를 수 있습니다. 필터링과 그래프 표시는 지원하지 않으므로 그런 기능이 필요하면 Grouped Events Timeline and Table을 씁니다.

<a id="grouped-events-timeline-and-table"></a>
## 그룹화된 이벤트 타임라인과 표 (Grouped Events Timeline and Table)

이 위젯은 두 구성 요소로 이루어집니다. (1) 링크된 객체의 타임라인과, (2) 그 아래에 링크된 객체를 나열하는 표입니다. 링크된 객체는 속성 기준으로 그룹화할 수 있고, 텍스트, 날짜 범위, 외부 필터로 필터링할 수 있습니다.

그룹화된 이벤트는 서로 평행한 여러 줄에 나뉘어 그려지며, 각 줄에는 특정 속성이 특정 값을 가진 이벤트만 들어갑니다. 피벗 테이블과 비슷한 방식입니다. 아래 예에서는 도시마다 줄이 하나씩 있고, 각 줄에는 해당 도시에서 도착하는(빨간색) 항공편과 출발하는(파란색) 항공편이 모두 표시됩니다.

이 위젯은 현재 객체에 직접 링크되었거나 다른 링크된 객체를 거쳐 링크된 객체 타입을 하나 이상 포함할 수 있습니다. 또한 같은 이벤트를 서로 다른 날짜 속성으로 표시할 수도 있습니다(아래 예 참고).

![Grouped Events Timeline and Table](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-grouped-events-table.gif)

**설명**: "속성 값별로 줄을 나눈다"는 것은 SQL의 `GROUP BY`와 같은 원리입니다. 예를 들어 항공편 4건이 `city` 속성으로 Boston, Boston, Chicago, Denver 값을 가지면, 타임라인에는 Boston 줄(2건), Chicago 줄(1건), Denver 줄(1건) 세 줄이 그려집니다.

<a id="configuration"></a>
### 설정 (Configuration)

<a id="settings"></a>
#### Settings

* **링크된 객체(이벤트) 하나 이상 추가하기**: 먼저 "Add Item"을 클릭해 타임라인에 표시할 링크된 객체 타입을 하나 이상 추가합니다. 여러 종류의 링크된 객체를 추가할 수 있습니다.
  * 완전히 다른 이벤트인 서로 다른 객체 타입을 한 타임라인에 표시합니다. 예: Aircraft에 링크된 객체 중 Flights 이벤트와 Maintenance 이벤트를 함께 표시.
  * 같은 링크된 객체 타입의 이벤트를 서로 다른 날짜 속성으로, 또는 서로 다른 종류의 링크로 표시합니다. 예:
    * Airport 객체에 링크된 Flights 이벤트를 서로 다른 날짜 속성 (1) "Planned Arrival Time", (2) "Actual Arrival Time", (3) "Expected Departure Time"으로 같은 타임라인에 표시합니다. 이 경우 각 항공편은 최대 3번 나타납니다.
    * Airport 객체에 링크된 Arriving Flights와 Departing Flights를 같은 타임라인에 함께 표시할 수 있습니다.
* **추가할 이벤트 객체의 타입 선택하기**: 추가하려는 이벤트 객체마다 해당 객체 타입의 세부 사항을 설정합니다.
  * 링크된 객체를 선택합니다. 직접 링크된 객체 또는 확장 링크(Extended Link) 중 하나입니다.
    * 직접 링크된 객체의 예: 현재 객체가 Airport이고 Arriving Flights와 Departing Flights의 타임라인을 표시하려는 경우.
    * 확장 객체(2단계)의 예: 현재 객체가 Airport이고, 그 Airport에 링크된 Arriving Flights에 다시 링크된 모든 Aircraft 객체를 타임라인으로 표시하려는 경우.
* **시각적 서식 옵션 설정하기**
  * Max Number of Events(최대 이벤트 수): 이 옵션은 현재 작동하지 않습니다.
  * Color(색상): 이 항목 설정에 속한 모든 이벤트의 색상을 선택합니다. [Blueprint 표준 색상 ↗](https://blueprintjs.com/docs/#core/colors)이나 기본 색상 이름("Blue", "Red", "Yellow" 등)을 사용합니다.
  * Series Name(시리즈 이름): 이 타임라인에 속한 모든 이벤트의 설명으로, 그래픽 타임라인의 범례에 표시됩니다.
* **타임라인에서 이벤트 정렬에 쓸 날짜 속성 정하기**: 타임라인에 이벤트를 표시할 때 기준으로 삼을 링크된 객체의 속성을 선택합니다. 이 속성은 타임스탬프나 날짜여야 하므로, 설정 화면은 그런 속성만 제안합니다.
* **Group Events By(이벤트 그룹화 기준)**: 그래픽 타임라인에서 이벤트를 어떻게 그룹화할지 선택합니다. 각 그룹은 그래픽 타임라인에서 별도의 가로줄로 표시되며, 줄들은 위아래로 쌓입니다. 두 가지 옵션이 있습니다.
  * Constant(상수): 현재 항목을 자유 텍스트 값으로 정한 제목을 가진 하나의 타임라인으로 묶습니다. 이 경우 다른 타임라인을 별도 줄로 추가하려면 항목을 더 정의해야 합니다.
  * Property(속성): 이벤트를 여러 개의 타임라인으로 나누고, 해당 속성의 서로 다른 값에 따라 각 타임라인에 이벤트를 그룹화합니다.
    * 예: Airport 객체의 모든 Arriving Flights 타임라인을 표시할 때 "Airline Name" 속성을 선택하면, 항공사마다 별도의 타임라인이 생기고 각 타임라인에는 해당 항공사의 항공편만 표시됩니다. 아래쪽 목록에는 모든 항공사의 Flights 이벤트 전체가 시간순으로 나열됩니다.
* **Properties Displayed in List(목록에 표시할 속성)**: 위젯의 두 번째 부분인 목록에 표시할 속성을 선택합니다.
  * 표시할 속성을 선택합니다.
    * All Properties: 링크된 객체에 속성이 많으면 화면이 복잡해져 타임라인을 훑어보기 어려우므로 권장하지 않습니다.
    * Prominent Properties: Ontology Manager에서 Prominent로 정의된 속성만 표시합니다.
    * Specific Properties: 해당 링크된 객체의 모든 속성이 담긴 다중 선택 드롭다운을 엽니다. 표시할 특정 속성을 고릅니다.
    * No Properties: 타임라인에 링크된 객체의 제목만 표시합니다.
  * Property Filter(속성 필터): 속성 하나를 기준으로 특정 값만 포함하도록 필터를 추가하는 선택적 토글입니다. 이 값들은 대소문자를 구분하는 자유 텍스트 문자열로 직접 입력해야 합니다.
* 그래픽 타임라인에 대한 추가 설정(이 설정은 타임라인 구성 요소에만 적용되며 표 구성 요소에는 영향을 주지 않습니다)
  * **Groups Displayed by Default(기본으로 표시할 그룹)**: 타임라인에서 별도 줄로 표시할 타임라인의 개수나 정확한 목록을 정합니다. 어느 경우든 사용자는 나머지 그룹이 모두 들어 있는 다중 선택 도우미를 사용할 수 있습니다.
    * Max Number(최대 개수): 그래픽 타임라인에 표시할 서로 다른 그룹(즉 서로 다른 타임라인)의 최대 개수를 숫자(Value)로 정합니다.
    * Explicit List(명시적 목록): 표시하려는 그룹 값의 정확한 목록을 입력합니다(텍스트, 대소문자 구분).
  * **Sort Groups By(그룹 정렬 기준)**: 타임라인에는 가로줄이 여러 개 있을 수 있으며, 이 줄들을 다음 세 가지 방법 중 하나로 정렬할 수 있습니다.
    * Configuration Order(설정 순서): 여러 항목을 설정한 순서
    * Name(이름): 모든 그룹을 알파벳순으로, 맨 위 A부터 맨 아래 Z까지
    * Most Recent Event(가장 최근 이벤트): 가장 최근 이벤트를 가진 그룹이 맨 위
  * **Max Graph Height(그래프 최대 높이)**: 위젯 안의 그래픽 타임라인 최대 높이를 픽셀 단위로 정합니다. 위젯 전체의 높이를 정하려면 설정의 Format 탭에 있는 크기(Sizing) 옵션을 참고하세요.

<a id="format"></a>
#### Format

Format 탭에서는 기본 항목인 Title, Icon, Info, Layout 외에 섹션의 최소 높이와 최대 높이를 조절할 수 있습니다. 둘 다 선택 사항입니다.

<a id="common-issues-and-notes"></a>
### 자주 겪는 문제와 참고 사항 (Common Issues and Notes)

* 최종 사용자는 자유 텍스트 필터나 날짜 범위로 타임라인을 필터링할 수 있지만, 이 필터는 게시되지 않으므로 다른 위젯에는 영향을 *주지 않습니다*.
* 교차 섹션 필터링(cross-section filtering)이 켜져 있으면 이 위젯은 다른 필터링 위젯의 영향을 받습니다.

> **중간 요약**: Grouped Events Timeline and Table은 위쪽의 그래픽 타임라인과 아래쪽의 표로 이루어지며, 속성 값(또는 상수 제목)별로 이벤트를 여러 줄에 나눠 그립니다. 색상, 시리즈 이름, 그룹 표시 개수와 정렬, 그래프 높이를 설정할 수 있고, 다른 위젯의 필터는 받지만 자기 필터는 내보내지 않습니다.

## 정리

* 레거시 Object View의 시각화 위젯은 현재 객체에 링크된 객체들을 표, 목록, 카드, 타임라인 형태로 보여 줍니다.
* Linked Object View는 링크된 객체를 표 중심으로 보여 주며, 표시 속성 선택, 결과 개수 제한, 기본/고급 검색을 지원합니다.
* Timeline은 날짜 속성 기준의 시간순 목록이며, 필터링과 그래프 표시는 지원하지 않습니다.
* Grouped Events Timeline and Table은 속성 값별로 그룹화한 그래픽 타임라인과 표를 함께 제공하고, 외부 필터의 영향을 받을 수 있습니다.
* 세 위젯 모두 다른 위젯이 게시한 필터를 받을 수는 있지만(Timeline 제외), 자기 내부 필터를 다른 위젯에 게시하지는 않습니다.
