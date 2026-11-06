# 타임라인에서 이벤트 보기와 필터링 (View and filter events on a timeline)

- 원문: https://www.palantir.com/docs/foundry/vertex/timeline/
- 사이드바 위치: Applications > Vertex > Events and time series > View and filter events on a timeline

이 페이지는 Vertex 화면 아래쪽의 타임라인(timeline)으로 객체의 시간 속성을 확인하고, 특정 시간 범위로 그래프를 필터링하고, 커서를 옮기고, 타임라인 모양과 색을 꾸미고, 재생 기능으로 시간을 자동으로 흘려 보는 방법을 설명합니다.

타임라인은 객체의 시간 속성(property)을 살펴보고, 주어진 시간 범위 안의 특정 이벤트로 필터링하는 데 사용할 수 있습니다.

![펼친 타임라인 개요](https://www.palantir.com/docs/resources/foundry/vertex/timeline_overview-expanded.png)

<a id="view-time-events"></a>
## 시간 이벤트 보기 (View time events)

화면 왼쪽 아래의 **Timeline** 버튼으로 타임라인을 보이거나 숨길 수 있습니다.

![타임라인 버튼](https://www.palantir.com/docs/resources/foundry/vertex/timeline_timeline-button.png)

타임라인에 아무것도 보이지 않으면 **Zoom to fit** 버튼을 사용해 그래프에 있는 시간 이벤트를 타임라인의 **Time range**에 맞춰 표시할 수 있습니다.

![화면에 맞추기](https://www.palantir.com/docs/resources/foundry/vertex/timeline_zoom-to-fit.png)

타임라인이 보이는 상태에서는 객체의 시간 속성은 선으로, 객체 속성에 있는 시간 범위는 막대로 표시됩니다.

![이벤트 선](https://www.palantir.com/docs/resources/foundry/vertex/timeline_event-lines.png)
![막대 이벤트](https://www.palantir.com/docs/resources/foundry/vertex/timeline_bar-events.png)

**설명**: 시간 속성이 하나뿐인 객체(예: `departure_time=09:00`인 Flight)는 타임라인의 한 시점에 세로선으로 그려집니다. 시작과 끝 두 시간 속성을 가진 객체(예: `start=09:00`, `end=10:30`인 Flight Delay)는 09:00부터 10:30까지 이어지는 막대로 그려집니다.

> **중간 요약**: **Timeline** 버튼으로 타임라인을 열고, 아무것도 보이지 않으면 **Zoom to fit**을 누릅니다. 단일 시각은 선, 시간 범위는 막대로 표시됩니다.

<a id="filter-time-events"></a>
## 시간 이벤트 필터링 (Filter time events)

그래프의 이벤트는 타임라인에서 Shift 키를 누른 채 마우스 왼쪽 버튼으로 드래그해 시간 필터 창을 만들거나, 타임라인 컨트롤 막대의 **Time filter** 버튼을 사용해 필터링할 수 있습니다.

**Time filter는** 애플리케이션 위쪽에서도 사용할 수 있습니다. 그래프에서 필터와 일치하는 노드는 완전히 불투명하게 보이고, 시간 필터와 일치하지 않는 노드는 흐리게 표시됩니다.

![시간 필터](https://www.palantir.com/docs/resources/foundry/vertex/timeline_graph-time-filter.png)

> **중간 요약**: Shift 드래그나 **Time filter** 버튼으로 시간 필터 창을 만들면, 그 구간에 해당하는 노드만 선명하게 보이고 나머지는 흐려집니다.

<a id="change-cursor-position"></a>
## 커서 위치 바꾸기 (Change cursor position)

타임라인의 커서 위치는 타임라인을 마우스 왼쪽 버튼으로 더블클릭하거나, 커서를 새 위치로 드래그하거나, 컨트롤 막대 가운데의 입력란을 사용해 바꿀 수 있습니다.

![커서 위치](https://www.palantir.com/docs/resources/foundry/vertex/timeline_cursor-pos.png)

커서에 더 구체적인 날짜를 지정하려면 커서 양식을 클릭해 특정 날짜와 시각을 입력할 수 있습니다.

![커서 편집](https://www.palantir.com/docs/resources/foundry/vertex/timeline_cursor-edit.png)

**설명**: 커서는 "지금 보고 있는 시점" 하나를 가리킵니다. 시간 필터가 구간(시작과 끝)을 정한다면, 커서는 그 안의 한 시각을 정합니다. 시계열 값처럼 시점마다 달라지는 표시는 이 커서 위치를 기준으로 결정됩니다.

<a id="expand-the-timeline"></a>
## 타임라인 펼치기 (Expand the timeline)

객체 타입마다 별도의 타임라인 행으로 표시하려면 타임라인 컨트롤 막대의 "expand" 버튼(![위쪽을 가리키는 이중 꺾쇠 아이콘](https://www.palantir.com/docs/resources/foundry/vertex/double-chevron.png))을 클릭합니다.

![객체 타입별 표시](https://www.palantir.com/docs/resources/foundry/vertex/timeline_by-object-type.png)

<a id="style-the-timeline"></a>
## 타임라인 스타일 지정 (Style the timeline)

타임라인에서 객체가 표시되는 방식을 바꾸려면 화면 왼쪽 **Layers** 패널에서 객체 노드 옆의 브러시 아이콘을 선택합니다. 그런 다음 **Timeline shape** 섹션을 펼칩니다.

![F1 Race 객체 노드의 Timeline shape 스타일 구성 섹션. 모양은 Bar로 설정되어 있고 시작 속성과 종료 속성을 고르는 옵션이 있습니다](https://www.palantir.com/docs/resources/foundry/vertex/timeline_shape-menu.png)

선택한 모양을 타임라인에 그릴 때 사용할 속성을 바꿀 수 있습니다. 시간 속성 두 개를 사용하는 모양은 **Start property**와 **End property** 드롭다운 메뉴를, 속성 하나를 사용하는 모양은 **Time property를** 선택합니다.

![F1 Race 객체 노드의 스타일 구성 섹션. 모양은 Diamond로 설정되어 있고 시간 속성 하나를 고르는 옵션이 있습니다.](https://www.palantir.com/docs/resources/foundry/vertex/timeline_diamond-select-time-property.png)

타임라인 스타일 구성에서 고른 모양은 타임라인에 나타나는 해당 객체 타입의 모든 인스턴스에 적용됩니다.

**Timeline Color** 메뉴를 선택해 타임라인에서 모양의 색을 어떻게 나타낼지 구성합니다.

![현재 고정 색으로 설정된 타임라인 색 구성 창.](https://www.palantir.com/docs/resources/foundry/vertex/timeline_color-menu.png)

**Color by** 드롭다운 메뉴에서 선택 항목을 바꾸면 속성과 측정값(measure)을 사용해 타임라인의 [색 스타일](../03_graphs/03_graphs-display-options.md#color-by)을 구성할 수도 있습니다. 예를 들어 아래 이미지는 `Year` 속성을 기준으로 무지개 색 스펙트럼을 사용해 색을 칠하도록 구성되어 있습니다.

![무지개 색 스펙트럼으로 속성에 따라 색을 칠하도록 설정된 타임라인 색 구성 창. 지도와 타임라인에 나타나는 객체들이 선형 보간에 따라 무지개 색으로 표시됩니다.](https://www.palantir.com/docs/resources/foundry/vertex/timeline_color-by-property.png)

**설명**: 선형 보간(linear interpolation)으로 색을 칠한다는 것은 속성 값의 최솟값과 최댓값을 색 스펙트럼의 양 끝에 대응시키고, 그 사이 값은 비율에 따라 중간 색을 고른다는 뜻입니다. 예를 들어 `Year`가 2000\~2020 범위라면 2000은 스펙트럼의 한쪽 끝 색, 2020은 반대쪽 끝 색, 2010은 정확히 가운데 색이 됩니다.

> **중간 요약**: **Layers** 패널의 브러시 아이콘에서 타임라인 모양(막대, 다이아몬드 등)과 그 모양에 쓸 시간 속성을 정하고, **Timeline Color**와 **Color by**로 고정 색이나 속성 기반 색을 지정합니다.

<a id="timeline-playback"></a>
## 타임라인 재생 (Timeline playback)

재생 버튼(⏵)을 사용하면 시간 커서를 자동으로 움직일 수 있으며, 재생 속도는 속도 프리셋(1x, 2x, 5x, 10x, 100x 등)으로 조절할 수 있습니다.

![속도 프리셋과 재생/일시정지 버튼을 보여 주는 타임라인 재생 컨트롤](https://www.palantir.com/docs/resources/foundry/vertex/timeline_playback_controls.png)

커서는 타임라인의 시간 창 안에서, 또는 시간 필터가 있으면 그 필터 범위 안에서 자동으로 반복 이동합니다.

![재생 컨트롤을 사용할 때 시간 커서가 필터 범위 안에 머무는 것을 보여 주는 타임라인 필터](https://www.palantir.com/docs/resources/foundry/vertex/timeline_playback_with_filter.png)

## 정리

- 타임라인은 객체의 시간 속성을 선(단일 시각)과 막대(시간 범위)로 보여 주며, **Timeline** 버튼과 **Zoom to fit**으로 표시합니다.
- Shift 드래그나 **Time filter**로 시간 필터를 만들면 일치하지 않는 노드가 흐려집니다.
- 커서는 더블클릭, 드래그, 입력란으로 옮기며, 타임라인을 펼치면 객체 타입별 행으로 나뉩니다.
- **Layers** 패널에서 타임라인 모양, 사용할 시간 속성, 색을 꾸밀 수 있고, 재생 버튼으로 커서를 자동 반복 이동시킬 수 있습니다.
