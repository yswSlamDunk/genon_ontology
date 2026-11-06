# 기존 그래프 탐색하기 (Explore existing graphs)

- 원문: https://www.palantir.com/docs/foundry/vertex/graphs-explore/
- 사이드바 위치: Applications > Vertex > Graphs > Explore existing graphs

이 페이지는 이미 만들어져 공유된 Vertex 그래프를 열었을 때 할 수 있는 탐색 작업을 설명합니다. 객체를 선택해 속성을 보는 법, 객체에 연결된 이벤트를 배지로 확인하는 법, 시간 축을 움직이며 상태 변화를 보는 법, 히스토그램으로 필터링하는 법, 그리고 Search Around로 관계를 넓혀 가는 법을 다룹니다.

<a id="object-exploration"></a>
## 객체 탐색 (Object exploration)

그래프에서 관심 있는 객체를 선택하면 사이드바의 **Selection** 탭에서 그 객체의 속성(property)을 볼 수 있습니다.

객체의 노드 레이블에 핵심 정보나 지표가 표시될 수도 있습니다. 아래 예는 항공편의 출발 시각과 도착 시각을 보여 줍니다.

![객체 탐색](https://www.palantir.com/docs/resources/foundry/vertex/explore-existing-1.jpg)

> **중간 요약**: 그래프의 노드(객체)를 선택하면 **Selection** 탭에 속성이 나오고, 노드 레이블에도 핵심 값을 표시할 수 있습니다.

<a id="associated-events"></a>
## 연관 이벤트 (Associated events)

객체에 연관된 이벤트가 있으면, 그 이벤트가 영향을 받는 객체 위에 *배지(badge)로* 표시되도록 구성할 수 있습니다. 관련 이벤트가 있는 객체 노드를 클릭하면 **object selection** 사이드바의 **Events** 탭에서 세부 정보를 볼 수 있습니다.

![이벤트](https://www.palantir.com/docs/resources/foundry/vertex/explore-existing-2.jpg)

**설명**: 여기서 이벤트는 시작 시각과 종료 시각을 가진 객체(예: Flight Delay 객체)로, 링크를 통해 다른 객체(예: 지연된 Flight 객체)와 연결되어 있습니다. 예를 들어 Flight Delay 객체가 `start = 09:00`, `end = 10:30`, `flight_id = F100`을 가지면, F100 노드에 배지가 붙고 클릭하면 이 지연 정보가 **Events** 탭에 나옵니다.

<a id="understand-current-state-and-changes-over-time"></a>
### 현재 상태와 시간에 따른 변화 이해하기 (Understand current state and changes over time)

객체는 객체 타입, 속성 값, 시계열(time series), 이벤트에 따라 스타일을 지정할 수 있습니다. 아래 예에는 다음 스타일이 적용되어 있습니다.

* Airport 객체는 진한 파란색으로 칠해집니다.
* Flight 객체는 연한 파란색으로 칠해지며, `Cancelled Status`가 `True`이면 빨간색으로 표시됩니다.
* Flight Delay 이벤트는 빨간색으로 칠해집니다.
* Flight Delay 이벤트는 **Flight object** 노드 위에 빨간 배지로 표시됩니다.

시간 선택 패널을 사용하면 커서를 끌면서("스크러빙(scrub)") 속성이 어떻게 바뀌는지를 동적 스타일로 볼 수 있습니다. 아래 스크린샷은 이벤트 배지가 이벤트가 진행 중일 때(즉, 이벤트의 시작 시각과 종료 시각 사이)에만 나타난다는 것을 보여 줍니다.

![시간에 따른 변화](https://www.palantir.com/docs/resources/foundry/vertex/explore-existing-3.jpg)

**설명**: 스크러빙은 시간 슬라이더를 움직여 "그래프의 기준 시각"을 바꾸는 동작입니다. 앞의 예에서 기준 시각을 08:30에 두면 F100에 배지가 없고, 09:30으로 옮기면 `09:00 <= 09:30 <= 10:30`이므로 배지가 나타나며, 11:00으로 옮기면 다시 사라집니다.

<a id="filter-and-explore-object-properties"></a>
### 객체 속성 필터링과 탐색 (Filter and explore object properties)

읽기 전용 모드에서는 사이드바의 **Histogram** 탭을 사용해 객체 타입과 속성별로 그래프 뷰를 필터링할 수 있습니다.

![객체 속성](https://www.palantir.com/docs/resources/foundry/vertex/explore-existing-4.jpg)

관심 있는 객체를 선택한 다음 **Filter to**(이것만 보기)나 **Filter out**(이것 제외하기)을 선택하면 히스토그램에서 선택한 내용이 그래프에 적용됩니다. 그래프 캔버스 위쪽에 적용된 필터가 표시됩니다. 특정 파라미터 옆의 **x** 기호를 클릭해 개별 객체 필터를 제거하거나, **Clear filters**를 선택해 모든 필터를 제거할 수 있습니다.

![필터](https://www.palantir.com/docs/resources/foundry/vertex/explore-existing-5.jpg)

**설명**: 히스토그램은 값별 개수를 막대로 보여 주는 차트입니다. 예를 들어 `Cancelled Status` 속성의 히스토그램에 `False: 42`, `True: 3`이 보일 때 `True` 막대를 선택하고 **Filter to**를 누르면, SQL로 `WHERE cancelled_status = true`를 건 것처럼 취소된 항공편 3개만 그래프에 남습니다.

> **중간 요약**: 객체는 타입, 속성 값, 시계열, 이벤트로 스타일을 바꿀 수 있고, 시간 패널을 움직이면 그 시각의 상태가 반영됩니다. 이벤트는 배지로 표시되며 **Histogram** 탭으로 그래프를 필터링할 수 있습니다.

<a id="exploring-object-relationships"></a>
## 객체 관계 탐색하기 (Exploring object relationships)

더 탐색적인 워크플로에서는 그래프 뷰와 상호 작용하면서 더 넓은 관계와 다양한 지표를 이해하고 싶을 수 있습니다. 이렇게 편집 가능한 객체 그래프 뷰에서는 Search Around, 스타일 지정, 레이아웃 변경 등 전체 Vertex 애플리케이션에서 사용할 수 있는 많은 동작을 할 수 있습니다.

**주의**: Workshop 모듈 안에서 그래프에 가한 변경은 그래프를 생성하는 데 사용된 기반 템플릿을 갱신하지 않습니다. Workshop 안의 뷰를 영구적으로 바꾸려면 기반 템플릿을 갱신해야 합니다.

그래프 캔버스 위쪽에서 아래와 같은 추가 탐색 도구 모음을 볼 수 있습니다.

![객체 관계](https://www.palantir.com/docs/resources/foundry/vertex/explore-existing-6.jpg)

<a id="explore-relationships"></a>
### 관계 탐색 (Explore relationships)

객체를 선택하고 마우스 오른쪽 버튼을 클릭해 **Actions** 메뉴를 엽니다. 이 메뉴에서 Search Around를 실행해 관련 객체와 이벤트를 찾고 그래프 뷰에 노드를 추가할 수 있습니다.

![Search Around](https://www.palantir.com/docs/resources/foundry/vertex/explore-existing-7.jpg)

**설명**: Search Around는 선택한 객체에서 링크 타입을 따라 한 단계 떨어진 객체를 찾는 기능입니다. SQL로 보면 선택한 행을 기준으로 외래 키 조인을 한 번 수행하는 것과 같은 결과입니다. 예를 들어 Airport 객체 JFK에서 "출발 항공편" 링크로 Search Around를 하면 `flights.origin = 'JFK'`인 Flight 객체들이 새 노드로 추가되고 JFK와 간선으로 연결됩니다.

<a id="object-and-edge-node-styling"></a>
### 객체 노드와 간선 스타일 지정 (Object and edge node styling)

관심 있는 객체 노드나 간선(edge)을 선택한 다음 사이드바의 **Layers** 탭에서 스타일을 갱신하고 변경할 수 있습니다.

**주의**: Workshop 모듈 안에서 변경한 스타일은 유지되지 않습니다. 대신 기반 템플릿 안에 여러 개의 *저장된 스타일(saved styles)을* 구성해 둘 수 있습니다.

![스타일 지정](https://www.palantir.com/docs/resources/foundry/vertex/explore-existing-8.jpg)

> **중간 요약**: 편집 가능한 뷰에서는 오른쪽 클릭 **Actions** 메뉴의 Search Around로 관련 객체를 추가하고 **Layers** 탭에서 스타일을 바꿀 수 있습니다. 단, Workshop 안에서 바꾼 내용은 템플릿에 저장되지 않으므로 영구 변경은 템플릿에서 해야 합니다.

## 정리

- 노드를 선택하면 **Selection** 탭에서 속성을, **Events** 탭에서 연관 이벤트를 볼 수 있습니다.
- 객체 스타일은 타입, 속성 값, 시계열, 이벤트에 따라 달라지고, 시간 패널을 움직이면 그 시각의 상태가 그래프에 반영됩니다.
- 읽기 전용 모드에서도 **Histogram** 탭으로 **Filter to**/**Filter out** 필터링이 가능합니다.
- 편집 가능한 뷰에서는 Search Around와 **Layers** 탭 스타일 변경이 가능하지만, Workshop 안의 변경은 기반 템플릿에 저장되지 않습니다.
