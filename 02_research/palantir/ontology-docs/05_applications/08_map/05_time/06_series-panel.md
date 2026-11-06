# 시리즈 패널 \[Planned deprecation] (Series panel [Planned deprecation])

- 원문: https://www.palantir.com/docs/foundry/map/series-panel/
- 사이드바 위치: Applications > Map > Time > Series panel [Planned deprecation]

이 페이지는 Map의 **Series** 패널을 설명합니다. 이 패널은 시계열과 링크된 이벤트를 타임라인의 시간 선택과 맞춰 보여 주는 기능이지만, 폐지가 예정되어 있어 앞으로는 타임라인 기능으로 대체됩니다. 기존 워크플로를 이해하거나 옮길 때 참고하는 페이지입니다.

**주의**: 폐지 예정(Planned deprecation). Map의 시리즈 패널은 [폐지 예정](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며 2026년 1월 31일 이후에는 사용할 수 없습니다. Map에서 시간 기반 데이터를 보고 객체의 시간 기반 속성을 자세히 살펴보려면 [타임라인](03_timeline.md#time-series-beta)을 사용하세요. <br><br>
Map의 타임라인 기능에 대해 질문이 있거나 워크플로 이전에 추가 도움이 필요하면 Palantir Support에 문의하세요.

지도의 **Series** 패널을 사용하면 타임라인의 선택된 시간과 시간 창에 동기화된 [시계열](05_time-series.md)과 [링크된 이벤트](04_events.md#linked-events)를 자세히 살펴볼 수 있습니다.

![시리즈 패널.](https://www.palantir.com/docs/resources/foundry/map/time-series-view.png)

<a id="time-series"></a>
## 시계열 (Time series)

[시계열](https://www.palantir.com/docs/foundry/time-series/time-series-overview/)은 시간에 따라 변하는 측정값입니다.

다음 방법으로 시리즈 패널에 시계열을 추가할 수 있습니다.

* 객체를 오른쪽 클릭하고 **Add series to series view**를 선택한 다음 **Add series to series panel** 메뉴에서 시리즈를 고릅니다.
* 객체를 선택하고 [**Selection** 패널을 연](../04_interact-with-maps/06_selection.md#selection-panel) 뒤 **Series** 탭으로 이동합니다. 시리즈 행 위에 마우스를 올리면 나타나는 **…** 아이콘을 선택해 선택한 시계열 관련 추가 액션 메뉴를 엽니다. 그런 다음 **Add to series view**를 선택합니다.

<table>
  <tr>
    <th>오른쪽 클릭으로 시계열 추가하기</th>
    <th><b>Selection</b> 패널로 시계열 추가하기</th>
  </tr>
  <tr>
    <td><img src="https://www.palantir.com/docs/resources/foundry/map/series-panel_right-click.png" alt="오른쪽 클릭 메뉴에서 시리즈 패널에 시리즈를 추가하는 모습."></img></td>
    <td><img src="https://www.palantir.com/docs/resources/foundry/map/series-panel_selection-panel.png" alt="선택 패널에서 시리즈 패널에 시리즈를 추가하는 모습."></img></td>
  </tr>
</table>

**Series** 패널에 시계열을 추가하면 지도 아래쪽에 시간에 따른 시리즈 시각화가 나타납니다. **Series** 패널에서 보고 싶은 시점을 선택해 시간을 이동할 수 있습니다. 또한 그려진 시간 범위를 따라 스크롤할 수 있습니다.

## 정리

- **Series** 패널은 타임라인의 선택된 시간과 시간 창에 맞춰 시계열과 링크된 이벤트를 보여 주는 패널입니다.
- 2026년 1월 31일 이후 사용할 수 없으며, 대신 타임라인의 시계열 기능을 사용해야 합니다.
- 오른쪽 클릭 메뉴의 **Add series to series view** 또는 **Selection** 패널의 **Series** 탭에서 시계열을 추가합니다.
