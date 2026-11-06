# 관련 이벤트 탐색하기 (Explore related events)

- 원문: https://www.palantir.com/docs/foundry/vertex/explore-related-events/
- 사이드바 위치: Applications > Vertex > Events and time series > Explore related events

이 페이지는 온톨로지에 구성한 이벤트 객체를 Vertex 그래프에서 확인하는 여러 방법을 설명합니다. 선택 패널, 노드에 붙는 배지, 이벤트 객체 자체를 그래프에 추가하는 방법, 시리즈 패널에서 시간 순으로 훑어보는 방법이 차례로 나옵니다.

**이벤트(event)는** 온톨로지 안에서 정의되고 구성됩니다. 모든 이벤트는 구별되는 시작 시각과 종료 시각을 가져야 하며, 이벤트에 표시될 색을 정하는 특정 임계값(threshold)을 구성할 수 있습니다. [이벤트 설정과 구성에 대해 더 읽어 보세요](02_configure-events.md).

이벤트 객체를 만들고 구성하고 나면, 시스템 그래프에서 이벤트 객체와 동적으로 상호작용할 수 있습니다.

<a id="view-events"></a>
### 이벤트 보기 (View events)

선택한 객체에 링크된 이벤트는 선택 패널(selection panel)에 표시되고, 이벤트가 지속되는 동안 객체 위에 배지로도 표시됩니다.

![explore-events-1](https://www.palantir.com/docs/resources/foundry/vertex/explore-events-1.jpg)

<a id="event-badges"></a>
### 이벤트 배지 (Event badges)

이벤트 배지는 레이어 스타일 옵션에서 구성합니다. 이벤트 배지를 표시할 객체 타입을 선택하고 **linked events** 옵션을 고르면 그래프의 노드나 엣지에 배지가 추가됩니다.

![explore-events-2](https://www.palantir.com/docs/resources/foundry/vertex/explore-events-2.jpg)

**설명**: 그래프 용어로 노드(node)는 점, 즉 여기서는 객체 하나이고, 엣지(edge)는 두 노드를 잇는 선, 즉 링크 하나입니다. "이벤트가 지속되는 동안 배지가 표시된다"는 것은 현재 보고 있는 시점이 이벤트의 시작 시각과 종료 시각 사이에 있을 때만 배지가 보인다는 뜻입니다.

<a id="event-objects"></a>
### 이벤트 객체 (Event objects)

이벤트의 전체 세부 정보를 보려면 해당 객체를 그래프에 추가하면 됩니다. 이벤트와 관련된 객체에서 마우스 오른쪽 버튼을 누르고 **Search Around** 옵션을 선택해 이벤트 객체(이 예에서는 Flight Delay 이벤트)를 찾습니다.

![explore-events-3](https://www.palantir.com/docs/resources/foundry/vertex/explore-events-3.jpg)

그래프에 추가한 뒤에는 이벤트 객체를 선택해 선택 패널에서 전체 세부 정보와 속성(property)을 볼 수 있습니다.

![explore-events-4](https://www.palantir.com/docs/resources/foundry/vertex/explore-events-4.jpg)

<a id="events-in-the-series-panel"></a>
### 시리즈 패널의 이벤트 (Events in the series panel)

객체에서 마우스 오른쪽 버튼을 누르고 **Open linked events**를 선택하면 시리즈 패널(series panel)이 열리고 이벤트가 추가됩니다. 여기서 시간 선택(time selection)을 사용해 시간을 앞뒤로 훑으며 여러 이벤트를 차례로 살펴볼 수 있습니다.

![explore-events-5](https://www.palantir.com/docs/resources/foundry/vertex/explore-events-5.jpg)

## 정리

- 이벤트는 시작과 종료 시각을 가진 온톨로지 객체이며, 임계값으로 표시 색을 정할 수 있습니다.
- 객체를 선택하면 링크된 이벤트가 선택 패널과 배지로 보이며, 배지는 레이어 스타일의 **linked events** 옵션으로 켭니다.
- **Search Around**로 이벤트 객체 자체를 그래프에 추가해 상세 속성을 볼 수 있습니다.
- **Open linked events**로 이벤트를 시리즈 패널에 올리고 시간 선택으로 훑어볼 수 있습니다.
