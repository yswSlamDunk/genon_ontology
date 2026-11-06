# 시간 선택 (Time selection)

- 원문: https://www.palantir.com/docs/foundry/map/time-selection/
- 사이드바 위치: Applications > Map > Time > Time selection

이 페이지는 Map 애플리케이션의 **Time selection** 패널로 선택 시각과 시간 창(time window)을 조정하는 방법을 다룹니다. 이 패널은 지원 중단(deprecated)되었고 기능은 타임라인으로 옮겨졌으므로, 기존 지도를 다루거나 타임라인의 동작을 이해할 때 참고하는 용도입니다.

**주의**: 지원 중단된 기능(Deprecated functionality). Map의 **Time selection** 패널은 지원 중단되었으며, 이 문서는 향후 릴리스에서 제거됩니다. 이 패널의 기능은 이제 [타임라인](01_time-overview.md#selected-time-and-time-range)에 있습니다.

**Time selection** 패널을 사용하면 현재 선택 시각과 시간 창을 조정할 수 있습니다. 시간 창을 따라 스크롤하면 데이터가 시간에 따라 어떻게 변하는지 이해할 수 있습니다.

<a id="change-the-selected-time"></a>
## 선택 시각 바꾸기 (Change the selected time)

시간 선택기(time selector)를 사용해 관심 있는 시각의 데이터를 시각화하도록 지도를 조정합니다.

**참고**: 시간 선택기에서는 현재 시간 창 안에 있는 시각만 선택할 수 있습니다.

![시간 선택기](https://www.palantir.com/docs/resources/foundry/map/time-selection-selector.png)

슬라이더를 사용해 시간 창을 따라 스크롤할 수도 있습니다.

![시간 슬라이더](https://www.palantir.com/docs/resources/foundry/map/time-selection-slider.png)

<a id="view-the-latest-data"></a>
### 최신 데이터 보기 (View the latest data)

**View latest**를 클릭하면 선택 시각이 현재 시각으로 설정됩니다. **Latest Data** 보기에서는 선택 시각이 현재 시각에 맞춰 자동으로 갱신됩니다. 최신 데이터 모드를 [스트리밍 데이터](https://www.palantir.com/docs/foundry/building-pipelines/pipeline-types/#streaming)와 함께 사용하면 실시간으로 갱신되는 데이터를 지도에 시각화할 수 있습니다.

<a id="change-the-time-window"></a>
## 시간 창 바꾸기 (Change the time window)

시간 슬라이더 아래의 날짜 범위 선택기로 시간 창을 조정합니다.

![시간 창](https://www.palantir.com/docs/resources/foundry/map/time-selection-window.png)

**설명**: 시간 창과 선택 시각은 포함 관계입니다. 예를 들어 시간 창을 2024년 1월 1일부터 1월 31일까지로 두면, 선택 시각은 그 안의 한 시점(예: 1월 15일 12:00)만 고를 수 있고 슬라이더도 그 31일 사이를 움직입니다. 2월의 데이터를 보려면 먼저 시간 창을 넓히거나 옮겨야 합니다.

## 정리

- **Time selection** 패널은 지원 중단되었고, 같은 기능은 타임라인에서 제공합니다.
- 시간 선택기나 슬라이더로 선택 시각을 바꾸며, 선택 시각은 현재 시간 창 안에서만 고를 수 있습니다.
- **View latest**는 선택 시각을 현재 시각으로 맞추고 계속 따라가게 하며, 스트리밍 데이터와 함께 실시간 표시에 쓰입니다.
- 시간 창은 슬라이더 아래의 날짜 범위 선택기로 조정합니다.
