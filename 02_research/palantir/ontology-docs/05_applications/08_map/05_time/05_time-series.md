# 시계열 (Time series)

- 원문: https://www.palantir.com/docs/foundry/map/time-series/
- 사이드바 위치: Applications > Map > Time > Time series

이 페이지는 지리공간 객체에 연결된 시계열(time series) 데이터를 Map에서 살펴보고, 스타일에 활용하고, 타임라인에 추가하는 방법을 설명합니다. 센서 측정값처럼 시간에 따라 계속 바뀌는 값을 객체의 위치와 함께 보고 싶을 때 쓰는 기능입니다.

[시계열](https://www.palantir.com/docs/foundry/time-series/time-series-overview/)은 시간에 따라 변하는 측정값입니다. 온톨로지에서는 시계열 값을 [시계열 속성(time series property)](https://www.palantir.com/docs/foundry/time-series/time-series-setup/)으로 설정할 수 있습니다. Map에는 지리공간 객체와 연결된 시계열 데이터를 보고 분석하는 데 도움이 되는 기능이 있습니다.

![타임라인과 선택 패널에 표시된 시계열 데이터.](https://www.palantir.com/docs/resources/foundry/map/time-series.png)

**설명**: 시계열은 `(시각, 값)` 쌍의 목록입니다. 예를 들어 `WeatherStation` 객체 S1의 `temperature` 시계열이 `(09:00, 12.1)`, `(10:00, 13.4)`, `(11:00, 15.0)`이라면, 객체 S1의 일반 속성(이름, 위치)은 값이 하나이지만 `temperature` 속성은 시각마다 다른 값을 가집니다. 그래서 "선택된 시간"이 정해져야 화면에 보여 줄 값 하나가 결정됩니다.

<a id="explore-related-time-series"></a>
## 관련 시계열 탐색하기 (Explore related time series)

지도에서 시계열 데이터가 연결된 객체를 선택합니다. 선택 패널의 **Series** 탭에서 관련된 시계열을 모두 볼 수 있습니다. 각 시리즈 옆에 표시되는 값은 현재 [선택된 시간](01_time-overview.md#selected-time-and-time-range)에서의 시리즈 값입니다.

![선택 패널의 Series 탭.](https://www.palantir.com/docs/resources/foundry/map/time-series-tab.png)

객체를 오른쪽 클릭하고 **Add series to series view**를 선택해 [시계열](https://www.palantir.com/docs/foundry/time-series/time-series-overview/)을 시리즈 패널에 직접 추가할 수도 있습니다. 또한 객체를 선택해 [**Selection** 패널](../04_interact-with-maps/06_selection.md#selection-panel)을 연 다음 **Series** 탭으로 이동할 수 있습니다. **Series** 탭에서 시리즈 행 위에 마우스를 올리면 나타나는 줄임표(ellipsis) 아이콘을 선택해 해당 시계열 관련 추가 액션 메뉴를 열고, 거기서 **Add to series view**를 선택할 수 있습니다.

<table>
  <tr>
    <th>오른쪽 클릭으로 시계열 추가하기</th>
    <th><b>Selection</b> 패널로 시계열 추가하기</th>
  </tr>
  <tr>
    <td><img src="https://www.palantir.com/docs/resources/foundry/map/timeline_right-click.png" alt="오른쪽 클릭 메뉴에서 타임라인에 시리즈를 추가하는 모습."></img></td>
    <td><img src="https://www.palantir.com/docs/resources/foundry/map/timeline_selection-panel.png" alt="선택 패널에서 타임라인에 시리즈를 추가하는 모습."></img></td>
  </tr>
</table>

타임라인에 시계열을 추가하면 지도 아래쪽에 시간에 따른 시리즈 시각화가 나타납니다. [타임라인](03_timeline.md)을 사용해 시리즈를 살펴보고, 타임라인 범례(legend)의 해당 항목에서 시계열 액션을 더 사용할 수 있습니다.

> **중간 요약**: 객체를 선택하면 **Series** 탭에 연결된 시계열과 선택된 시간 기준의 값이 보이며, 오른쪽 클릭 메뉴나 **Series** 탭의 줄임표 메뉴로 시계열을 시리즈 보기나 타임라인에 추가할 수 있습니다.

<a id="use-time-series-for-styling"></a>
## 시계열로 스타일 지정하기 (Use time series for styling)

지도의 객체에 시계열 데이터가 연결되어 있으면, 연결된 시계열로 객체에 색을 입힐 수 있습니다. 이렇게 하면 지도가 현재 [시간 선택](01_time-overview.md#selected-time-and-time-range)에 반응하고, 데이터가 시간에 따라 어떻게 변하는지 이해하는 데 도움이 됩니다. 시계열을 [값 기반 스타일](../06_visualize-ontology-data/01_visualize-objects.md#value-based-styling)에 사용하는 방법을 더 읽어 보세요.

**설명**: 위 `temperature` 예시에서 "15도 이상은 빨강, 그 미만은 파랑"이라는 규칙을 걸면, 선택된 시간을 09:00에서 11:00으로 옮길 때 S1의 색이 파랑에서 빨강으로 바뀝니다.

<a id="interact-with-time-series-in-the-timeline"></a><a id="interact-with-time-series-in-the-timeline-beta"></a>
## 타임라인에서 시계열 다루기 \[Beta] (Interact with time series in the timeline)

**참고**: 베타(Beta). Map 타임라인에서 시계열을 다루는 기능은 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며 사용자의 환경(enrollment)에서는 사용할 수 없을 수도 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다. 이 기능에 대한 접근을 요청하려면 Palantir Support에 문의하세요.

지도의 타임라인에 시계열을 추가하는 방법은 두 가지입니다.

* **오른쪽 클릭 메뉴**: 지도에서 객체를 오른쪽 클릭하고 **Add series to the timeline**을 선택한 다음 메뉴에서 시리즈를 고릅니다.
* **Selection 패널**: 지도에서 객체를 선택하고 [**Selection** 패널을 연](../04_interact-with-maps/06_selection.md#selection-panel) 뒤 **Series** 탭으로 이동합니다. 다음으로 시리즈 행 위에 마우스를 올리면 나타나는 **…을** 선택해 선택한 시계열 관련 추가 액션 메뉴를 열고 **Add to timeline**을 선택합니다.

타임라인에 시계열을 추가한 뒤에는 타임라인 범례를 사용해 그려지는 스타일을 설정하고, 필요하면 표시 여부를 켜고 끌 수 있습니다.

## 정리

- 시계열은 시간에 따라 변하는 측정값이며, 온톨로지에서 시계열 속성으로 설정합니다.
- 객체를 선택하면 **Series** 탭에서 연결된 시계열과 선택된 시간 기준의 값을 볼 수 있습니다.
- 시계열로 객체 색을 칠하면 선택된 시간을 옮길 때마다 지도 스타일이 바뀝니다.
- 베타 기능으로, 오른쪽 클릭 메뉴나 **Selection** 패널에서 시계열을 타임라인에 추가하고 범례에서 스타일과 표시 여부를 조정할 수 있습니다.
