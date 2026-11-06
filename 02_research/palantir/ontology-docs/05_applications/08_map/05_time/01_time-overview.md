# 지도의 시간과 시간 데이터 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/map/time-overview/
- 사이드바 위치: Applications > Map > Time > Overview

이 페이지는 Map 애플리케이션이 시간에 따라 변하는 데이터를 어떻게 다루는지 소개합니다. 지도에서 쓸 수 있는 세 가지 시간 기반 데이터(시계열, 이벤트, 트랙)와, 지도 전체에 적용되는 선택 시각(selected time)과 시간 범위(time range)의 개념을 설명합니다. 이후 Time 섹션의 다른 페이지들을 읽기 위한 출발점입니다.

지도에는 시간에 따라 변하는 데이터를 시각화하고 다루기 위한 여러 기능이 있습니다. 시간 데이터는 다양한 형태를 띠며, 형태마다 서로 다른 방식으로 사용하고 시각화할 수 있습니다.

<a id="time-based-data-types-available-on-a-map"></a>
## 지도에서 쓸 수 있는 시간 기반 데이터 타입 (Time-based data types available on a map)

<a id="time-series"></a>
### 시계열 (Time series)

[시계열](05_time-series.md)은 시간에 따라 변하는 측정값입니다. 시계열 값은 온톨로지에서 [시계열 속성(time series property)](https://www.palantir.com/docs/foundry/time-series/time-series-setup/)으로 구성할 수 있습니다. 시계열을 사용해 지도 위 [객체에 스타일을 적용](../06_visualize-ontology-data/01_visualize-objects.md#value-based-styling)하고, [타임라인](05_time-series.md#explore-related-time-series)에서 볼 수 있습니다.

![타임라인과 선택 패널에 표시된 시계열 데이터.](https://www.palantir.com/docs/resources/foundry/map/time-series.png)

<a id="events"></a>
### 이벤트 (Events)

[이벤트 객체](04_events.md)는 객체를 특정 시각이나 시간 범위와 연결하는 메타데이터를 추가로 가진 객체입니다. 이벤트 객체는 지도 위 [객체의 불투명도를 제어](../06_visualize-ontology-data/01_visualize-objects.md#opacity-styling)하는 데 쓸 수 있고, [타임라인](../06_visualize-ontology-data/06_visualize-timeline.md)에 시각화할 수 있습니다.

![시간에 따라 이벤트에 스타일 적용하기.](https://www.palantir.com/docs/resources/foundry/map/events-style-by-time.gif)

<a id="tracks"></a>
### 트랙 (Tracks)

[트랙](../07_integrate-data-for-the-map/01_integrate-objects.md#track-objects)을 사용하면 위치가 시간에 따라 바뀌는 객체를 표현할 수 있습니다. [트랙 스타일 옵션](../06_visualize-ontology-data/07_visualize-tracks.md)으로 객체의 시간별 위치를 시각화하는 방식을 사용자 정의할 수 있습니다.

![트랙 표시 예시.](https://www.palantir.com/docs/resources/foundry/map/styling-tracks.png)

**설명**: 세 가지는 데이터 모양이 다릅니다. 시계열은 한 객체에 `(시각, 값)` 쌍이 계속 쌓이는 형태입니다(예: 기상 관측소 객체의 10분 간격 기온 측정값). 이벤트는 객체 자체가 하나의 시각이나 기간을 가지는 형태입니다(예: 시작 시각과 종료 시각 속성을 가진 지진 객체). 트랙은 `(시각, 위도, 경도)` 쌍이 쌓이는 형태로, 위치가 시계열인 객체입니다(예: 선박의 항적).

> **중간 요약**: 지도에서 쓸 수 있는 시간 데이터는 시간에 따라 변하는 측정값인 시계열, 특정 시각이나 기간에 묶인 이벤트 객체, 시간에 따라 위치가 바뀌는 트랙의 세 가지입니다.

<a id="selected-time-and-time-range"></a>
## 선택 시각과 시간 범위 (Selected time and time range)

지도에 표시되는 모든 시간 데이터는 현재 선택 시각과 시간 범위를 따릅니다. 이를 통해 데이터가 시간에 따라 어떻게 변하는지 보고, 과거의 특정 시각을 살펴볼 수 있습니다.

**View latest**를 선택하면 **Latest Data** 보기가 시작되며, 이 보기에서는 선택 시각이 현재 시각에 맞춰 자동으로 갱신됩니다. **Latest Data** 보기를 [스트리밍 데이터](https://www.palantir.com/docs/foundry/building-pipelines/pipeline-types/#streaming)와 함께 사용하면 실시간으로 갱신되는 데이터를 지도에 시각화할 수 있습니다.

지도의 선택 시각과 시간 범위는 [타임라인](03_timeline.md)에서 볼 수 있습니다. 선택 시각과 시간 범위는 타임라인이 열려 있지 않을 때도 지도에 데이터가 표시되는 방식에 영향을 줍니다.

예를 들어 선택 시각에 따라 시간 기반 스타일의 색상이 달라집니다.

![타임라인에서 선택 시각을 바꾸면 기상 관측소 아이콘 색상이 바뀌는 예시 지도.](https://www.palantir.com/docs/resources/foundry/map/time_time-selection-changes.gif)

**설명**: 선택 시각은 지도 전체에 걸린 "현재 보고 있는 시점" 하나입니다. 예를 들어 기상 관측소 아이콘 색을 기온 시계열로 칠하도록 했다면, 선택 시각을 오후 2시로 두면 각 관측소의 오후 2시 기온으로, 오후 6시로 옮기면 오후 6시 기온으로 색이 다시 계산됩니다. 데이터베이스의 시점 조회(point-in-time query)처럼 "그 시각 기준 값"을 보여 주는 것입니다.

<a id="adjust-the-selected-time-time-range-and-filtered-time-window"></a>
## 선택 시각, 시간 범위, 필터 시간 창 조정하기 (Adjust the selected time, time range, and filtered time window)

[타임라인](03_timeline.md)을 사용해 다음을 조정합니다.

* [선택 시각](03_timeline.md#adjust-the-selected-time)
* [시간 범위](03_timeline.md#adjust-the-time-range)
* [필터 시간 창](03_timeline.md#filter-the-time-window)

## 정리

- Map 애플리케이션은 시계열, 이벤트, 트랙의 세 가지 시간 기반 데이터를 다룹니다.
- 시계열은 객체 스타일과 타임라인 표시에, 이벤트는 불투명도 제어와 타임라인 표시에, 트랙은 시간별 위치 시각화에 쓰입니다.
- 지도의 모든 시간 데이터는 선택 시각과 시간 범위를 따르며, 타임라인이 닫혀 있어도 그 영향을 받습니다.
- **View latest**로 **Latest Data** 보기를 켜면 선택 시각이 현재 시각을 따라가며, 스트리밍 데이터와 함께 실시간 지도를 만들 수 있습니다.
- 선택 시각, 시간 범위, 필터 시간 창은 타임라인에서 조정합니다.
