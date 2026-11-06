# 타임라인 이벤트 (Timeline events)

- 원문: https://www.palantir.com/docs/foundry/map/visualize-timeline/
- 사이드바 위치: Applications > Map > Visualize Ontology data > Timeline events

이 페이지는 레이어의 객체가 가진 시간 속성을 지도 아래쪽 타임라인에 도형으로 그리는 타임라인 지오메트리(timeline geometry)의 추가와 스타일 설정 방법을 설명합니다. Ontology Manager에서 이벤트로 설정하지 않은 객체라도 타임스탬프 속성만 있으면 이 방법으로 타임라인에 표시할 수 있습니다.

레이어에 있는 모든 객체의 시간 기반 속성을 타임라인에서 시각화하려면 [타임라인](../05_time/03_timeline.md)에 나타날 타임라인 지오메트리를 설정하면 됩니다.

!['\[Example\] Airports' 객체의 시간 속성이 타임라인에 보이는 타임라인 지오메트리 예시.](https://www.palantir.com/docs/resources/foundry/map/styling-timeline-event.png)

타임라인 지오메트리는 [이벤트 객체](../05_time/04_events.md#event-objects)와 다릅니다. 객체 레이어마다 타임라인 지오메트리를 여러 개 설정할 수 있고, 속성 기반 색 칠하기 같은 추가 스타일 옵션을 적용할 수 있기 때문입니다.

타임라인 지오메트리를 추가하고 나면, 타임라인 범례(legend)의 해당 지오메트리 항목에서 추가 설정 액션을 사용할 수 있습니다.

**설명**: 예를 들어 `Flight` 객체에 `scheduled_departure`, `actual_departure`, `actual_arrival` 세 타임스탬프 속성이 있다면, "예정 출발"을 다이아몬드로, "실제 출발부터 도착까지"를 막대로 그리는 타임라인 지오메트리 두 개를 같은 레이어에 둘 수 있습니다. 이벤트 객체는 Ontology Manager에서 지정한 시작과 끝 한 쌍만 보여 주므로 이런 구성이 불가능합니다.

<a id="styling"></a>
## 스타일 지정 (Styling)

새 타임라인 이벤트 지오메트리 레이어를 타임라인에 나타내려면 **Layers** 패널에서 **Timeline** 지오메트리를 추가합니다.

![Flights 객체가 타임라인에 표시되는 방식을 편집하는 타임라인 지오메트리.](https://www.palantir.com/docs/resources/foundry/map/timeline_add-geometry.png)

타임라인 지오메트리를 추가하면 스타일 메뉴에 **Timeline** 섹션이 나타나며, 여기서 선택한 도형을 타임라인에 그릴 때 사용할 속성을 바꿀 수 있습니다. 시간 속성 두 개를 쓰는 도형이면 **Start property**와 **End property** 드롭다운 메뉴를, 속성 하나를 쓰는 도형이면 **Time property**를 선택합니다.

![Flights 객체의 Timeline 스타일 설정 섹션. 도형이 Bar로 설정되어 있고, 시작 속성과 끝 속성을 선택하는 옵션이 있습니다.](https://www.palantir.com/docs/resources/foundry/map/timeline_bar-select-time-properties.png)

타임라인 지오메트리는 모든 속성이 설정되기 전에는 타임라인에 나타나지 않습니다.

![Flights 객체의 Timeline 스타일 설정 섹션. 도형이 Diamond로 설정되어 있고, 시간 속성을 선택하는 옵션이 있습니다.](https://www.palantir.com/docs/resources/foundry/map/timeline_diamond-select-time-property.png)

**Timeline** 스타일 설정 섹션에서 고른 **Shape**는 타임라인에서 해당 객체 타입의 모든 인스턴스에 그려집니다. 예를 들어 아래 이미지는 타임라인에서 `Flights` 객체 타입을 다이아몬드 도형으로 나타냅니다.

![지도 타임라인에서 다이아몬드로 표시된 Flights 객체 타입.](https://www.palantir.com/docs/resources/foundry/map/timeline_diamond-on-timeline.png)

**Geometry** 섹션의 **Color** 메뉴를 선택해 지도의 타임라인에서 도형 색이 어떻게 그려질지 설정합니다.

![현재 고정 색으로 설정된 타임라인 색 설정 창.](https://www.palantir.com/docs/resources/foundry/map/timeline_color-menu.png)

**Color by** 드롭다운 메뉴에서 선택한 옵션을 바꾸면 속성과 측정값(measure)으로 타임라인 색 스타일을 설정할 수도 있습니다. 예를 들어 아래 이미지는 `Arrival Latitude` 속성에 따라 무지개 색 스펙트럼으로 칠하도록 설정한 타임라인 지오메트리를 보여 줍니다.

![무지개 색 스펙트럼으로 속성에 따라 칠하도록 설정된 타임라인 색 설정 창. 지도와 타임라인에 나타나는 객체가 선형 보간에 따른 무지개 색으로 표시됩니다.](https://www.palantir.com/docs/resources/foundry/map/timeline_color-by-property.png)

## 정리

- 타임라인 지오메트리는 레이어 객체의 시간 속성을 타임라인에 도형으로 그리는 디스플레이이며, **Layers** 패널에서 **Timeline** 지오메트리로 추가합니다.
- 이벤트 객체와 달리 레이어당 여러 개를 둘 수 있고 속성 기반 색 같은 스타일 옵션이 더 있습니다.
- 막대처럼 두 시간 속성을 쓰는 도형은 **Start property**와 **End property**를, 다이아몬드처럼 한 시간 속성을 쓰는 도형은 **Time property**를 지정해야 표시됩니다.
- 색은 고정 색, 속성, 측정값 중에서 골라 설정합니다.
