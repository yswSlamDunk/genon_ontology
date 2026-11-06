# 이벤트 (Events)

- 원문: https://www.palantir.com/docs/foundry/map/events/
- 사이드바 위치: Applications > Map > Time > Events

이 페이지는 Map에서 "이벤트"를 다루는 두 가지 방식인 이벤트 객체(event object)와 타임라인 지오메트리(timeline geometry)를 비교하고 각각의 사용법을 설명합니다. 둘 다 시간 정보를 가진 객체를 타임라인과 지도에 보여 주지만, 설정 위치(Ontology Manager와 지도의 **Layers** 패널)와 스타일 기능이 다릅니다. 시간에 따라 의미가 달라지는 객체(지진, 운항, 정비 기간 등)를 지도에 표시하려면 이 차이를 알아야 합니다.

이벤트는 특정 시점 또는 기간에 관한 시간 정보를 포함하는 [객체 타입](../../../02_define-ontologies/02_object-and-link-types/02_object-types/01_object-types-overview.md) 또는 [타임라인 지오메트리](#timeline-geometries)입니다. 가장 흔한 경우는 이벤트 객체가 기간의 시작과 끝을 나타내는 타임스탬프 속성(property)을 갖는 형태입니다. 이벤트 객체는 지도 캔버스에서는 아이콘으로, 화면 아래쪽의 타임라인 패널에서는 타임라인 지오메트리로 그려지며, 두 가지 모두 스타일을 지정해 사용자가 객체의 이벤트를 시간과 관련지어 더 잘 이해하도록 도울 수 있습니다.

**설명**: 예를 들어 `Earthquake` 객체 타입의 데이터가 다음과 같다고 합시다.

| quake_id | location | start_time | end_time |
|---|---|---|---|
| Q1 | (35.1, 129.0) | 2024-03-01 10:00 | 2024-03-01 10:02 |
| Q2 | (37.5, 127.0) | 2024-03-05 08:30 | 2024-03-05 08:31 |

`start_time`과 `end_time`이 이벤트의 시작과 끝을 나타내는 타임스탬프 속성입니다. 이런 객체 타입이 이벤트 객체가 될 수 있습니다.

이벤트 객체와 타임라인 지오메트리의 차이는 아래 표를 참고하세요.

<table>
    <thead>
        <tr>
            <th>기능 동작 또는 설정</th>
            <th>이벤트 객체</th>
            <th>타임라인 지오메트리</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>렌더링 설정의 전제 조건</td>
            <td>Ontology Manager에서 설정하며, 이벤트 객체는 시작과 끝 타임스탬프 속성을 포함합니다.</td>
            <td>지도의 <b>Layers</b> 패널에서 설정하며, 타임라인 지오메트리는 지오메트리 모양에 따라 객체에 타임스탬프 속성이 최소 하나 있어야 합니다. 타임스탬프 속성이 하나 이상 있는 객체라면 어떤 객체든 지도의 타임라인에 그릴 수 있습니다.</td>
        </tr>
        <tr>
            <td>지도 캔버스에 미치는 효과</td>
            <td>불투명도(opacity) 기반 스타일에 사용됩니다.</td>
            <td>효과 없음. 지도의 타임라인에 레이어만 추가합니다.</td>
        </tr>
        <tr>
            <td>지도 타임라인에 미치는 효과</td>
            <td>Foundry가 이벤트 객체를 지도의 타임라인에 자동으로 표시합니다.</td>
            <td>지도의 <b>Layers</b> 패널에서 설정하면 Foundry가 타임스탬프 속성을 가진 객체를 타임라인 지오메트리로 표시합니다. 이벤트 객체의 기본 타임라인 스타일을 덮어씁니다.</td>
        </tr>
        <tr>
            <td>타임라인 스타일 옵션</td>
            <td>타임라인 스타일 옵션이 없습니다. 이벤트 객체는 객체의 색을 보여 주는 막대를 가집니다.</td>
            <td>모양, 사용자 지정 색 등 여러 타임라인 스타일 옵션을 사용할 수 있습니다.</td>
        </tr>
        <tr>
            <td>타임라인 레이어가 여러 개일 때의 표시 동작</td>
            <td>이벤트 객체는 Ontology Manager에서 설정한 이벤트 기간만 보여 줍니다.</td>
            <td>객체의 타임스탬프 속성을 바탕으로 지도의 <b>Layers</b> 패널에서 타임라인 지오메트리 레이어를 여러 개 설정할 수 있습니다.</td>
        </tr>
    </tbody>
</table>

[온톨로지에서 이벤트를 설정하는 방법을 알아보세요.](../07_integrate-data-for-the-map/01_integrate-objects.md#event-objects)

> **중간 요약**: 이벤트 객체는 Ontology Manager에서 시작과 끝 시각을 지정한 객체 타입으로, 지도 불투명도와 타임라인에 자동으로 반영됩니다. 타임라인 지오메트리는 지도의 **Layers** 패널에서 만드는 타임라인 표시 방식으로, 스타일 옵션이 많고 타임스탬프 속성만 있으면 어떤 객체에도 쓸 수 있습니다.

<a id="event-objects"></a>
## 이벤트 객체 (Event objects)

이벤트 객체는 특정 시점 또는 기간에 관한 시간 정보를 포함하는 [객체 타입](../../../02_define-ontologies/02_object-and-link-types/02_object-types/01_object-types-overview.md)입니다. 가장 흔한 경우는 이벤트 객체가 기간의 시작과 끝을 나타내는 타임스탬프 속성을 갖는 형태입니다. [온톨로지에서 이벤트를 설정하는 방법을 알아보세요.](../07_integrate-data-for-the-map/01_integrate-objects.md#event-objects)

[이벤트 객체를 지도에 레이어로 추가](../04_interact-with-maps/03_add-to-map.md)하고 나면 사용자 지정 스타일을 적용하고, 링크된 이벤트를 탐색하고, [타임라인](03_timeline.md)에서 이벤트 기간을 볼 수 있습니다.

![이벤트 객체 'Earthquakes'의 시간 속성이 타임라인에 보이는 타임라인 지오메트리 예시. 별도의 타임라인 지오메트리는 없습니다.](https://www.palantir.com/docs/resources/foundry/map/events-object.png)

이벤트 객체는 타임라인에 이벤트 레이어를 자동으로 채우며, 이벤트 객체의 시작과 끝 시각과 같은 시작과 끝 시각을 갖는 타임라인 지오메트리를 추가해 스타일을 지정할 수 있습니다. 왼쪽 패널의 **Style** 섹션에서 다음 표시 옵션을 추가로 사용할 수 있습니다.

* **Shape**: 기본적으로 시작 시각 속성과 끝 시각 속성을 사용해 막대를 그립니다. 객체 타입의 시작 시각과 끝 시각은 [Ontology Manager의 **Capabilities** 탭](../07_integrate-data-for-the-map/01_integrate-objects.md#event-objects)에서 설정합니다.
* **Color**: **Color**를 선택해 이벤트 객체의 아이콘 색을 **Fixed color**(고정 색), **Function**(함수), **Property**(속성), **Linked sensor**(링크된 센서) 중 하나로 칠합니다.

**Layers** 패널에서 타임라인 지오메트리를 추가하면, 그 지오메트리가 타임라인에서 이 이벤트 레이어의 모양을 덮어씁니다. 하지만 이벤트의 시작과 끝 시각은 지도의 불투명도 기반 스타일에 여전히 사용될 수 있습니다.

<a id="use-event-objects-for-styling"></a>
### 이벤트 객체로 스타일 지정하기

현재 [시간 선택](01_time-overview.md#selected-time-and-time-range)이 이벤트 기간과 겹칠 때만 이벤트 객체가 보이도록 지도에서 스타일을 지정할 수 있습니다. 이렇게 하면 지도가 시간에 따라 반응하며 현재 관련 있는 이벤트 객체만 보여 줍니다. [이벤트 객체로 스타일을 지정하는 방법을 알아보세요.](../06_visualize-ontology-data/01_visualize-objects.md#opacity-styling)

![시간에 따라 이벤트에 스타일을 적용하는 모습.](https://www.palantir.com/docs/resources/foundry/map/events-style-by-time.gif)

**설명**: "겹친다"는 조건은 `start_time <= 선택된 시간 <= end_time`입니다. 위 `Earthquake` 예시에서 선택된 시간이 2024-03-01 10:01이면 Q1만 보이고 Q2는 숨겨지거나 흐려집니다. 선택된 시간이 범위로 지정되어 있다면 두 구간이 한 시점이라도 공유하는지로 판단합니다.

<a id="linked-events"></a>
### 링크된 이벤트 (Linked events)

링크된 이벤트는 다른 객체에 링크된 이벤트 객체입니다. 지도에서 객체를 선택하고 **Events** 탭을 열면 링크된 이벤트를 볼 수 있습니다. 현재 선택된 시간이 이벤트의 시작 시각과 끝 시각 사이에 있으면 그 이벤트는 **Active events** 섹션에 나타납니다. 그렇지 않으면 비활성 이벤트로 간주되며 **Show inactive events** 옵션으로 표시할 수 있습니다.

![Events 탭이 표시된 모습.](https://www.palantir.com/docs/resources/foundry/map/events-selection-events-tab.png)

링크된 이벤트가 [지리공간 객체 타입](../07_integrate-data-for-the-map/01_integrate-objects.md)이면 **+를** 클릭해 지도에 추가할 수 있습니다.

![지도에 추가 버튼.](https://www.palantir.com/docs/resources/foundry/map/events-add-to-map.png)

각 이벤트에서 다음 액션을 할 수 있습니다.

* ![돋보기 아이콘.](https://www.palantir.com/docs/resources/foundry/map/events-magnifying-glass.png) 아이콘으로 선택된 시간 창을 이벤트의 시작과 끝 시각에 맞춥니다.
* ![Open in 버튼.](https://www.palantir.com/docs/resources/foundry/map/events-open-in.png) 아이콘으로 이벤트를 Object Explorer에서 엽니다.

**설명**: 예를 들어 `Aircraft` 객체 A1과 `Maintenance`(정비) 이벤트 객체 사이에 링크 타입이 있다면, 지도에서 A1을 선택했을 때 **Events** 탭에 A1의 정비 기록이 나열됩니다. 데이터베이스로 보면 `Maintenance.aircraft_id = 'A1'`인 행을 조인으로 가져온 결과입니다.

<a id="show-on-series-panel"></a><a id="show-on-series-panel-planned-deprecation"></a>
#### 시리즈 패널에 표시하기 \[Planned deprecation] (Show on series panel)

객체를 오른쪽 클릭하고 **Open linked events**를 선택하면 링크된 이벤트를 [시리즈 패널](06_series-panel.md)에 열고 추가할 수 있습니다. 중요한 기간을 배경으로 시계열 데이터를 분석하고, 지도가 관심 있는 시간을 반영하도록 시간 선택을 조정할 수 있습니다.

![시리즈 패널에 이벤트 추가하기.](https://www.palantir.com/docs/resources/foundry/map/events-add-to-series-panel.png)

<a id="show-counts-in-labels"></a>
#### 레이블에 개수 표시하기 (Show counts in labels)

레이어의 레이블을 켜면 각 객체의 레이블에 활성 이벤트 개수도 표시됩니다. 활성 이벤트 개수 위에 마우스를 올리면 활성 이벤트를 볼 수 있습니다.

![레이블에서 이벤트 보기.](https://www.palantir.com/docs/resources/foundry/map/events-view-from-label.png)

> **중간 요약**: 이벤트 객체는 타임라인에 자동으로 나타나고, 선택된 시간과 기간이 겹칠 때만 보이도록 지도 스타일에 쓸 수 있습니다. 다른 객체에 링크된 이벤트는 **Events** 탭에서 활성과 비활성으로 나뉘어 표시됩니다.

<a id="timeline-geometries"></a>
## 타임라인 지오메트리 (Timeline geometries)

이벤트 객체의 짝을 이루는 타임스탬프 속성으로 정의되는 타임라인 지오메트리는 지도의 타임라인에 이벤트 레이어로 그려지며, 객체 속성에 따라 스타일을 지정할 수 있습니다. 타임라인 지오메트리는 지도 레이어로 그려지는 이벤트 객체보다 더 많은 사용자 지정 스타일 옵션을 제공합니다.

[지도에 타임라인 지오메트리를 추가하고 설정하는 방법을 알아보세요.](../06_visualize-ontology-data/06_visualize-timeline.md)

## 정리

- 이벤트는 시점 또는 기간 정보(보통 시작과 끝 타임스탬프 속성)를 가진 객체 타입이나 타임라인 지오메트리입니다.
- 이벤트 객체는 Ontology Manager의 **Capabilities** 탭에서 시작과 끝 시각을 지정하며, 타임라인에 자동 표시되고 지도에서 시간 기반 불투명도 스타일에 쓰입니다.
- 타임라인 지오메트리는 지도의 **Layers** 패널에서 추가하며, 타임라인 스타일 옵션이 더 많고 이벤트 객체의 기본 타임라인 표시를 덮어씁니다.
- 링크된 이벤트는 선택한 객체의 **Events** 탭에서 활성과 비활성으로 확인하고, 지도에 추가하거나 Object Explorer로 열 수 있습니다.
