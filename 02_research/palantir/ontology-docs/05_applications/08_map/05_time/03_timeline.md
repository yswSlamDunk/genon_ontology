# 타임라인 (Timeline)

- 원문: https://www.palantir.com/docs/foundry/map/timeline/
- 사이드바 위치: Applications > Map > Time > Timeline

이 페이지는 Map 애플리케이션 화면 아래쪽에 있는 타임라인(timeline) 패널의 사용법을 설명합니다. 타임라인은 시간 정보를 가진 객체(이벤트, 이동 경로, 시계열)를 시간 축 위에 보여 주고, 지도 전체에 적용되는 "선택된 시간"과 "시간 범위"를 조절하는 도구입니다. 시간에 따라 바뀌는 데이터를 지도에서 다루려면 먼저 이 조작법을 알아야 합니다.

타임라인을 사용하면 시간 기반 데이터를 보고, 시간 창(time window)과 [선택된 시간(selected time)](01_time-overview.md#adjust-the-selected-time-time-range-and-filtered-time-window)을 설정할 수 있습니다. [선택된 시간과 시간 범위](01_time-overview.md#selected-time-and-time-range)를 정하고, 객체의 시간 기반 속성(property)을 자세히 살펴보고, 주어진 시간 범위 안의 특정 객체만 남도록 필터링할 수 있습니다.

![타임라인에 이벤트, 트랙 브레드크럼, 시계열이 표시된 Map 애플리케이션의 .gif 화면.](https://www.palantir.com/docs/resources/foundry/map/timeline-overview.gif)

타임라인으로 볼 수 있는 것은 [이벤트](#events)([이벤트 객체](04_events.md#event-objects)와 [타임라인 지오메트리](04_events.md#timeline-geometries)), [트랙 브레드크럼](#track-breadcrumbs), [시계열](#time-series-beta)입니다.

타임라인을 열지 않은 상태에서도, 타임라인의 시간 범위와 [선택된 시간](01_time-overview.md#selected-time-and-time-range)은 지도에 보이는 모든 시간 기반 데이터에 영향을 줄 수 있습니다.

**설명**: "선택된 시간"은 시간 축 위의 한 시점(커서 위치)이고, "시간 범위"는 타임라인 화면에 보이는 시작 시각부터 끝 시각까지의 구간입니다. 예를 들어 시간 범위가 2024-01-01\~2024-01-31이고 선택된 시간이 2024-01-15 12:00이면, 지도는 그 시점에 "활성"인 이벤트나 그 시점의 객체 위치를 기준으로 그려집니다.

<a id="basic-controls"></a>
## 기본 조작 (Basic controls)

<a id="open-and-enable-the-timeline"></a>
### 타임라인 열기와 활성화

지도 캔버스 왼쪽 아래의 **Timeline**을 선택하면 타임라인을 표시하거나 숨길 수 있습니다.

![타임라인 열기 버튼.](https://www.palantir.com/docs/resources/foundry/map/timeline_timeline-button.png)

[Map 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-map/)을 사용해 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)에 지도를 임베드할 때는 타임라인이 기본으로 열려 있도록 설정할 수 있습니다.

![Workshop Map 위젯 설정 패널의 타임라인 활성화 버튼.](https://www.palantir.com/docs/resources/foundry/map/timeline_workshop-enable.png)

<a id="adjust-the-selected-time"></a>
### 선택된 시간 조정하기

타임라인 위의 커서 위치가 지도의 [선택된 시간](01_time-overview.md#selected-time-and-time-range)을 나타냅니다. 선택된 시간은 다음 방법으로 조정할 수 있습니다.

* 타임라인을 더블 클릭하거나 오른쪽 클릭합니다.
* 커서를 새 위치로 드래그합니다.
* 타임라인 헤더 가운데의 날짜 또는 타임스탬프를 선택해 날짜와 시간 선택기를 엽니다.

![타임라인 위의 커서 위치.](https://www.palantir.com/docs/resources/foundry/map/timeline_cursor-pos.gif)

커서의 날짜를 더 정확히 지정하려면 커서 입력 폼을 클릭해 특정 날짜와 시간을 입력할 수 있습니다.

![타임라인 헤더 가운데의 입력란으로 커서 위치를 바꾸는 모습.](https://www.palantir.com/docs/resources/foundry/map/timeline_cursor-edit-map.png)

**View latest**를 선택하면 선택된 시간이 현재 시각으로 설정됩니다. **Latest Data** 보기 상태에서는 선택된 시간이 현재 시각에 맞춰 자동으로 갱신됩니다. **Latest Data** 모드를 [스트리밍 데이터](https://www.palantir.com/docs/foundry/building-pipelines/pipeline-types/#streaming)와 함께 사용하면 실시간으로 갱신되는 데이터를 지도에 시각화할 수 있습니다.

**참고**: 날짜와 시간 선택기를 사용할 때는 객체 레이어의 현재 시간 범위 안에 있는 시간만 선택할 수 있습니다.

[모든 지도에 대해 시계열의 **View latest** 모드 기본 시간 선택과 폴링 간격을 Control Panel에서 설정](../09_configuration/02_control-panel.md)할 수 있습니다. 또한 [지도별 폴링 간격, 시간대, 시간 형식은 설정(settings) 패널에서 설정](../09_configuration/01_settings.md#polling-interval)할 수 있습니다.

**설명**: 폴링(polling)은 클라이언트가 일정한 간격마다 서버에 "새 데이터가 있는지" 다시 요청하는 방식입니다. 폴링 간격이 10초라면 **View latest** 모드의 지도는 10초마다 최신 데이터를 다시 가져와 화면을 갱신합니다.

<a id="adjust-the-time-range"></a>
### 시간 범위 조정하기

[시간 범위](01_time-overview.md#selected-time-and-time-range)는 타임라인 헤더 오른쪽 위에서, 그리고 타임라인 보기의 시작 시각과 끝 시각에서 확인할 수 있습니다. 아래 안내에 따라 마우스나 트랙패드로 시간 범위를 조정할 수 있습니다.

스크롤 조작:

* 마우스 스크롤 휠로 타임라인을 확대하거나 축소합니다. 스크롤하기 전에 `Cmd`(macOS) 또는 `Ctrl`(Windows)을 누르고 있으면 시간 범위를 좌우로 이동(pan)합니다.
* 트랙패드에서는 위아래로 쓸어 넘기거나 핀치 인/아웃으로 타임라인을 확대하거나 축소합니다.

타임라인 헤더 오른쪽 위 리본의 **Time range**를 선택하면 타임라인의 날짜와 시간 범위를 직접 입력할 수 있습니다.

![타임라인 헤더 오른쪽의 입력란으로 시간 창을 바꾸는 모습.](https://www.palantir.com/docs/resources/foundry/map/timeline_time-window.png)

타임라인에 있는 데이터에 맞춰 시간 창을 자동으로 정하려면 양방향 화살표 모양의 **Zoom to fit** 버튼을 선택합니다.

![타임라인 오른쪽 헤더의 Zoom to fit 버튼.](https://www.palantir.com/docs/resources/foundry/map/timeline_zoom-to-fit.png)

<a id="filter-the-time-window"></a>
### 시간 창 필터링하기

다음 방법으로 지도의 이벤트를 필터링할 수 있습니다.

* `Shift`를 누른 채 타임라인의 한 지점을 선택하고 커서를 드래그해 시간 필터 창을 만듭니다.
* 타임라인 컨트롤 바의 **Time filter** 버튼을 사용합니다.

![타임라인의 시간 창 필터.](https://www.palantir.com/docs/resources/foundry/map/timeline_map-filter-close.png)

**Time filter**는 지도 캔버스 위쪽에서도 사용할 수 있습니다. 필터에 맞는 지도 위 객체는 완전히 불투명하게 표시되고, 시간 필터에 맞지 않는 객체는 흐리게 표시됩니다.

![Map 애플리케이션 위쪽에 표시된 시간 필터.](https://www.palantir.com/docs/resources/foundry/map/timeline_map-filter.png)

**설명**: 시간 필터는 SQL의 `WHERE event_time BETWEEN :start AND :end` 조건과 같은 역할을 합니다. 차이점은 조건에 맞지 않는 객체를 결과에서 없애지 않고 흐리게 남겨 둔다는 점입니다.

<a id="timeline-playback"></a>
### 타임라인 재생 (Timeline playback)

재생 버튼(⏵)을 사용하면 시간 커서를 자동으로 움직일 수 있습니다. 재생 속도는 속도 프리셋(1x, 2x, 5x, 10x, 100x 등)으로 조정할 수 있습니다.

![속도 프리셋과 재생/일시정지 버튼이 보이는 타임라인 재생 컨트롤.](https://www.palantir.com/docs/resources/foundry/map/timeline_playback_controls.png)

커서는 타임라인의 시간 창 안에서, 또는 시간 필터가 있으면 그 필터 범위 안에서 자동으로 반복 이동합니다.

![재생 컨트롤을 사용할 때 시간 커서가 시간 필터 범위 안에 머무는 모습.](https://www.palantir.com/docs/resources/foundry/map/timeline_playback_with_filter.png)

<a id="expand-the-timeline"></a>
### 타임라인 펼치기

타임라인이 접혀 있으면 타임라인에 추가한 데이터는 보이지 않습니다. 하지만 시간 범위, 필터링된 시간 창, [선택된 시간](01_time-overview.md#selected-time-and-time-range)은 여전히 바꿀 수 있습니다.

객체 타입마다 별도의 타임라인 행으로 표시하려면 타임라인 컨트롤 바에서 **Expand**(![위쪽을 가리키는 이중 꺾쇠 아이콘 버튼.](https://www.palantir.com/docs/resources/foundry/map/double-chevron.png))를 선택합니다.

> **중간 요약**: 타임라인 커서가 선택된 시간이고, 스크롤과 **Time range** 입력으로 시간 범위를 바꿉니다. `Shift` 드래그나 **Time filter**로 시간 창을 걸러 조건 밖의 객체를 흐리게 만들 수 있고, 재생 버튼으로 커서를 자동으로 움직일 수 있습니다.

<a id="add-data-to-the-timeline"></a>
## 타임라인에 데이터 추가하기 (Add data to the timeline)

타임라인에 추가된 모든 데이터는 객체 타입별로 묶여 표시됩니다.

<a id="events"></a>
### 이벤트 (Events)

<a id="event-objects"></a>
#### 이벤트 객체 (Event objects)

[이벤트 객체](04_events.md#event-objects)는 타임라인에 이벤트 레이어를 자동으로 추가합니다.

![이벤트 객체 'Earthquakes'의 시간 속성이 타임라인에 보이는 예시. 별도의 타임라인 지오메트리는 없습니다.](https://www.palantir.com/docs/resources/foundry/map/events-object.png)

<a id="timeline-geometries"></a>
#### 타임라인 지오메트리 (Timeline geometries)

새 타임라인 이벤트 지오메트리 레이어를 타임라인에 나타내려면 **Layers** 패널에서 [타임라인 지오메트리](../06_visualize-ontology-data/06_visualize-timeline.md)를 추가합니다. [타임라인 지오메트리에 사용자 지정 스타일을 적용하는 방법을 알아보세요.](../06_visualize-ontology-data/06_visualize-timeline.md#styling)

![Flights 객체가 타임라인에 표시되는 방식을 편집하는 타임라인 지오메트리.](https://www.palantir.com/docs/resources/foundry/map/timeline_add-geometry.png)

<a id="track-breadcrumbs"></a>
### 트랙 브레드크럼 (Track breadcrumbs)

브레드크럼 지오메트리를 가진 트랙은 [시간 범위](#adjust-the-time-range)와 지도 뷰포트(viewport)에 따라 타임라인에도 그려집니다.

선택된 시간을 다른 시점으로 옮기면 트랙 위 객체의 이동 경로를 애니메이션으로 볼 수 있습니다.

새 트랙 브레드크럼 레이어를 타임라인에 그리려면 **Layers** 패널에서 [트랙 브레드크럼 지오메트리](../06_visualize-ontology-data/07_visualize-tracks.md#track-breadcrumbs)를 추가합니다.

![객체 위치가 기록된 정확한 시각을 볼 수 있는 트랙 브레드크럼 예시.](https://www.palantir.com/docs/resources/foundry/map/timeline_track-breadcrumbs.png)

타임라인에 트랙 브레드크럼 레이어를 추가한 뒤에는 타임라인 범례(legend)의 해당 레이어 항목에서 **Layers** 패널의 [추가 스타일 설정](../06_visualize-ontology-data/07_visualize-tracks.md#styling) 같은 타임라인 지오메트리 액션을 더 사용할 수 있습니다.

**설명**: 트랙(track)은 시간에 따라 위치가 바뀌는 객체(예: 비행기, 선박)의 위치 기록이고, 브레드크럼(breadcrumb)은 그 기록의 각 지점을 점으로 찍어 지나온 경로를 보여 주는 표시 방식입니다. 예를 들어 선박 한 척의 위치가 10:00, 10:05, 10:10에 기록되었다면 지도에는 점 3개가, 타임라인에는 그 세 시각이 표시됩니다.

<a id="time-series"></a><a id="time-series-beta"></a>
### 시계열 \[Beta] (Time series)

지도의 타임라인에 시계열을 추가하고 설정하는 방법은 [시계열 문서](05_time-series.md#interact-with-time-series-in-the-timeline-beta)를 참고하세요.

> **중간 요약**: 타임라인에 올라가는 데이터는 객체 타입별로 묶이며, 이벤트 객체는 자동으로, 타임라인 지오메트리와 트랙 브레드크럼은 **Layers** 패널에서 추가해야 나타납니다.

<a id="faqs"></a>
## 자주 묻는 질문 (FAQs)

<a id="will-time-based-data-be-visible-on-the-map-or-timeline-for-large-object-sets"></a>
### 큰 객체 집합에서도 시간 기반 데이터가 지도나 타임라인에 보이나요?

큰(1,000개 초과) 객체 집합(object set)을 추가하면 지도는 [타일 기반 로딩(tile-based loading)](../06_visualize-ontology-data/08_objects-loading-methods.md)으로 객체를 자동으로 불러옵니다.

타일 기반 로딩에서는 [타임라인 이벤트](#events), 시간 기반 스타일, [필터링된 시간 창](#filter-the-time-window)을 사용할 수 없습니다. 해결하려면 **Object-based** 로딩으로 바꾸세요. 성능을 위해 객체 수를 줄여야 할 수도 있습니다.

<a id="why-am-i-unable-to-see-time-series-styling-on-my-map"></a>
### 지도에서 시계열 스타일이 보이지 않는 이유는 무엇인가요?

시계열 속성에서 나온 스타일이 보이지 않는다면, Map이 시간 속성에서 색을 도출하지 못하고 있다는 뜻입니다. [선택된 시간](01_time-overview.md#selected-time-and-time-range)이 데이터가 있는 시점을 포함하는지 확인하세요.

<a id="why-am-i-unable-to-see-time-based-opacity-on-my-objects-on-my-map"></a>
### 지도에서 객체의 시간 기반 불투명도가 보이지 않는 이유는 무엇인가요?

보이지 않는 특정 객체를 선택하고, 그 객체의 타임스탬프 또는 날짜 속성이 [선택된 시간](01_time-overview.md#selected-time-and-time-range)과 맞는지 확인하세요.
시간 기반 객체 불투명도는 [이벤트 객체](04_events.md#use-event-objects-for-styling)에서만 설정할 수 있습니다.

<a id="why-am-i-unable-to-see-any-track-breadcrumbs-on-my-map"></a>
### 지도에서 트랙 브레드크럼이 하나도 보이지 않는 이유는 무엇인가요?

브레드크럼 지오메트리를 가진 트랙은 [시간 범위](#adjust-the-time-range)에 따라 타임라인에 그려집니다.

<a id="why-am-i-unable-to-see-any-time-based-data-in-my-timeline"></a>
### 타임라인에 시간 기반 데이터가 하나도 보이지 않는 이유는 무엇인가요?

타임라인에 아무것도 보이지 않으면 **Zoom to fit** 버튼을 사용해 지도의 시간 이벤트가 타임라인의 **Time range** 안에 들어오도록 하세요.

데이터가 보이면 타임라인은 객체의 시간 속성을 선으로 표시합니다.

![이벤트 선이 표시된 타임라인.](https://www.palantir.com/docs/resources/foundry/map/timeline_event-lines.png)

또한 객체 속성에 들어 있는 시간 구간은 막대로 표시합니다.

![막대 이벤트가 표시된 타임라인.](https://www.palantir.com/docs/resources/foundry/map/timeline_bar-events.png)

> **중간 요약**: 데이터가 안 보일 때는 객체가 1,000개를 넘어 타일 기반 로딩이 켜졌는지, 선택된 시간과 시간 범위가 데이터 시점을 포함하는지부터 확인합니다.

## 정리

- 타임라인은 지도 전체에 적용되는 선택된 시간(커서)과 시간 범위를 조절하고, 시간 기반 데이터를 시간 축 위에 보여 주는 패널입니다.
- 커서 이동, 스크롤 확대와 축소, **Time range** 입력, **Zoom to fit**, `Shift` 드래그 시간 필터, 재생 기능을 제공합니다.
- 이벤트 객체는 자동으로, 타임라인 지오메트리와 트랙 브레드크럼은 **Layers** 패널에서 추가해 타임라인에 표시합니다.
- 객체가 1,000개를 넘으면 타일 기반 로딩으로 바뀌어 시간 관련 기능이 꺼지므로 **Object-based** 로딩으로 전환해야 합니다.
