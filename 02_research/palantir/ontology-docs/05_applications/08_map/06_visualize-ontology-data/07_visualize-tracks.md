# 트랙: 움직이는 객체 (Tracks (moving objects))

- 원문: https://www.palantir.com/docs/foundry/map/visualize-tracks/
- 사이드바 위치: Applications > Map > Visualize Ontology data > Tracks (moving objects)

이 페이지는 선박, 항공기, 위성처럼 시간에 따라 위치가 바뀌는 객체를 지도에 그리는 트랙(track) 디스플레이를 설명합니다. 트랙 선(track line), 트랙 브레드크럼(track breadcrumb), 그리고 기록 사이의 위치를 어떻게 계산할지 정하는 보간 옵션을 다룹니다.

지도에는 시간에 따라 움직이는 객체를 그리는 디스플레이가 있습니다. 이 디스플레이들은 객체가 지나간 경로와, 객체가 지도 위를 움직이며 드러나는 패턴을 시각화하도록 설계되었습니다.

모든 트랙 디스플레이는 [시간 기반 불투명도 스타일](01_visualize-objects.md#opacity-styling)을 사용할 수 있습니다. 아래의 트랙 디스플레이 외에도, 트랙 지오메트리 소스를 [아이콘과 원](02_visualize-points.md)의 위치를 정하는 방법으로 사용할 수도 있습니다. [온톨로지에서 트랙을 설정하는 방법을 알아보세요.](../07_integrate-data-for-the-map/01_integrate-objects.md#track-objects)

아래의 가상 예시는 트랙 지오메트리 소스를 사용해, 밴쿠버 시 근처를 움직이는 선박 객체의 트랙 선, 브레드크럼, 현재 위치의 아이콘을 표시합니다.
![밴쿠버 시 근처를 움직이는 선박 객체의 트랙 선, 브레드크럼, 현재 위치 아이콘을 보여 주는 트랙 디스플레이 예시.](https://www.palantir.com/docs/resources/foundry/map/styling-tracks.png)

트랙당 시계열 지점 수는 Control Panel에서 [조직 단위](../09_configuration/02_control-panel.md#data-loading)로, 또는 [설정 메뉴에서 지도별](../09_configuration/01_settings.md#time-series-buckets)로 설정할 수도 있습니다.

**설명**: 트랙 데이터는 객체 하나에 대한 `(시각, 위치)` 기록의 목록입니다. 예를 들어 선박 V1의 기록이 다음과 같다고 합시다.

| time | position |
|---|---|
| 10:00 | (49.28, -123.12) |
| 10:10 | (49.29, -123.15) |
| 10:20 | (49.30, -123.18) |
| 11:30 | (49.35, -123.30) |

트랙 선은 이 점들을 순서대로 잇고, 브레드크럼은 네 점만 찍습니다. 아래 보간 옵션은 기록 사이의 시각(예: 10:05)이 선택되었을 때 V1을 어디에 그릴지 정합니다.

<a id="moving-geometry-interpolation"></a>
#### 움직이는 지오메트리 보간 (Moving geometry interpolation)

트랙을 지오메트리 소스로 사용할 때는, 지도가 트랙과 [선택된 시간](../05_time/01_time-overview.md#adjust-the-selected-time-time-range-and-filtered-time-window)으로부터 점 위치를 해석하는 방식을 설정하는 추가 옵션을 사용할 수 있습니다.

* **Interpolation mode**(보간 모드)
  * **Linear**: 트랙의 알려진 지점 사이를 매끄럽게 보간합니다.
  * **Last known**: 선택된 시간 이전에 마지막으로 기록된 위치에 객체를 표시합니다.
* **Max time gap**: 연속된 두 트랙 지점의 시간 차이가 설정한 값보다 크면, 그 기간에는 트랙에 데이터가 없는 것으로 간주합니다.

**설명**: 위 V1 예시에서 선택된 시간이 10:05이면 **Linear**는 10:00과 10:10 위치의 중간 지점에, **Last known**은 10:00 위치에 V1을 그립니다. **Max time gap**을 30분으로 두면 10:20과 11:30 사이는 70분 간격이므로 그 구간은 데이터가 없는 것으로 처리됩니다.

<a id="track-lines"></a>
## 트랙 선 (Track lines)

트랙 선은 인접한 기록 위치들을 선으로 이어 객체가 지나간 경로를 시각화합니다. 두 지점의 시간 차이가 설정한 **Max time gap**보다 크면 그 두 지점 사이에는 선을 그리지 않습니다. 그 밖에는 트랙 선의 스타일 옵션이 [선](03_visualize-polygons-lines.md)과 같습니다.

<a id="track-breadcrumbs"></a>
## 트랙 브레드크럼 (Track breadcrumbs)

트랙 브레드크럼은 객체의 정확한 기록 위치만 시각화하는 방법입니다. 각 객체의 트랙은 서로 다른 시각의 객체 위치를 보여 주는 작은 원(브레드크럼)의 연속으로 그려집니다. 그 밖에는 브레드크럼의 스타일 옵션이 [원](02_visualize-points.md#circle-configuration)과 같습니다.

트랙 브레드크럼은 타임라인에도 표시되어 객체 위치가 기록된 정확한 시각을 볼 수 있습니다. 이 예시는 위성의 지상 궤적(ground trace)을 시각화하며, 각 지점에서의 위성 위도에 따라 선과 브레드크럼에 색을 칠합니다. 타임라인의 브레드크럼에도 같은 색 스타일 설정이 반영됩니다.

지도 뷰포트에 보이지 않는 브레드크럼은 흐리게 표시되어, 시간에 따른 객체 경로와 객체가 지도에 보이게 될 시간 범위를 파악하는 데 도움을 줍니다. 현재 [시간 범위](../05_time/01_time-overview.md#adjust-the-selected-time-time-range-and-filtered-time-window)에 브레드크럼이 없으면 지도와 타임라인 어디에도 나타나지 않습니다.

![객체 위치가 기록된 정확한 시각을 볼 수 있는 트랙 브레드크럼 예시.](https://www.palantir.com/docs/resources/foundry/map/styling-track-breadcrumbs.png)

트랙 브레드크럼을 추가하고 나면, 타임라인 범례(legend)의 해당 지오메트리 항목에서 추가 설정 액션을 사용할 수 있습니다.

<a id="styling"></a>
### 스타일 지정 (Styling)

새 트랙 브레드크럼 지오메트리 레이어를 타임라인에 나타내려면 **Layers** 패널에서 브레드크럼 지오메트리를 추가합니다.

![Flights 객체가 타임라인에 표시되는 방식을 편집하는 타임라인 지오메트리.](https://www.palantir.com/docs/resources/foundry/map/track-breadcrumb_add-geometry.png)

트랙 브레드크럼 지오메트리를 추가하면 스타일 메뉴에 **Track breadcrumbs** 섹션이 나타납니다. 여기서 선택한 경로를 지도에 그릴 때 사용할 속성(property)을 바꿀 수 있습니다.

**Track breadcrumb** 지오메트리의 **Color** 메뉴를 선택해 타임라인에서 도형 색이 어떻게 나타날지 설정합니다.

**Color by** 드롭다운 메뉴에서 선택한 옵션을 바꾸면 속성과 측정값(measure)으로 트랙 브레드크럼의 색 스타일을 설정할 수도 있습니다. 예를 들어 아래 이미지는 `Latitude` 속성에 따라 무지개 색 스펙트럼으로 칠하도록 설정되어 있습니다.

!['Latitude' 속성에 따라 트랙 브레드크럼에 색을 칠한 예시.](https://www.palantir.com/docs/resources/foundry/map/timeline_track-breadcrumbs.png)

## 정리

- 트랙 디스플레이는 시간에 따라 움직이는 객체의 경로를 그리며, 모두 시간 기반 불투명도 스타일을 지원합니다.
- 보간 모드(**Linear**, **Last known**)와 **Max time gap**으로 기록 사이 시각의 위치와 데이터 공백 구간을 정합니다.
- 트랙 선은 기록 위치를 선으로 잇고(선 스타일 옵션), 트랙 브레드크럼은 기록 위치만 작은 원으로 찍습니다(원 스타일 옵션).
- 브레드크럼은 타임라인에도 표시되며, 속성이나 측정값으로 색을 칠할 수 있습니다.
