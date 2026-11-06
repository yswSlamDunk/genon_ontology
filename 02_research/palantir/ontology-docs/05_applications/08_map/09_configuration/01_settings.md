# 지도 설정 (Settings)

- 원문: https://www.palantir.com/docs/foundry/map/settings/
- 사이드바 위치: Applications > Map > Configuration > Settings

이 페이지는 Map 애플리케이션 화면의 설정 메뉴에서 바꿀 수 있는 항목을 설명합니다. 설정은 내 계정에 저장되어 모든 지도에 적용되는 사용자 설정과, 특정 지도에 저장되어 그 지도를 보는 모든 사용자에게 적용되는 지도 설정 두 범주로 나뉩니다. 거리 단위, 시간대, 테마처럼 지도를 읽는 방식에 영향을 주는 값들이 여기에 있습니다.

Map 화면 오른쪽 위의 설정 톱니바퀴 아이콘(![톱니바퀴 아이콘](https://www.palantir.com/docs/resources/foundry/map/settings-icon.png))을 선택해 설정 메뉴를 엽니다.

![지도 설정 메뉴](https://www.palantir.com/docs/resources/foundry/map/settings.png)

일부 설정은 [Control Panel](02_control-panel.md)에서 조직 전체에 설정된 내용에 따라 제한됩니다.

<a id="user-settings"></a>
## 사용자 설정 (User settings)

사용자 계정에 연결되어, 내가 여는 모든 지도에 적용되는 설정입니다.

<a id="units"></a>
### 단위 (Units)

거리를 표시할 단위를 지정할 수 있습니다. 사용자별 설정이며, Map 애플리케이션을 사용할 때마다 적용됩니다. 단위 옵션은 다음과 같습니다.

* Metric(미터법)
* Imperial(야드파운드법)
* Nautical(해리법)

<a id="enable-geojson-panel"></a>
### GeoJSON 패널 활성화 (Enable GeoJSON panel)

화면 오른쪽 아래에 GeoJSON 패널을 추가로 켤 수 있습니다. 이 패널에서 GeoJSON 데이터를 입력하고 편집할 수 있으며, GeoJSON 도형을 바탕으로 주석(annotation)을 만들 수 있습니다. 사용자별 설정이며, Map 애플리케이션을 사용할 때마다 적용됩니다.

![GeoJSON 패널](https://www.palantir.com/docs/resources/foundry/map/geojson-panel.png)

**설명**: GeoJSON은 점, 선, 다각형 같은 지리 도형을 JSON으로 표현하는 표준 형식입니다. 예를 들어 `{"type":"Point","coordinates":[126.9779,37.5663]}`를 패널에 붙여 넣으면 그 위치에 점 주석을 만들 수 있습니다(좌표는 경도, 위도 순서).

> **중간 요약**: 사용자 설정은 계정에 저장되어 모든 지도에 적용되며, 거리 단위와 GeoJSON 패널 표시 여부가 있습니다.

<a id="map-settings"></a>
## 지도 설정 (Map settings)

지도마다 저장되는 설정입니다. 이 설정은 저장된 특정 지도를 사용하는 모든 사용자에게 적용됩니다.

<a id="polling-interval"></a>
### 폴링 간격 (Polling interval)

["View Latest" 모드](../05_time/01_time-overview.md#selected-time-and-time-range)일 때 새 시계열(time series) 값과 시계열 속성(property) 값을 얼마나 자주 불러올지 지정할 수 있습니다.

**설명**: 폴링(polling)은 서버에 "새 데이터가 있는가"를 일정 간격으로 반복해서 묻는 방식입니다. 간격을 10초로 두면 10초마다 최신 값을 다시 요청하므로, 실시간에 가깝지만 요청 수가 늘어납니다.

<a id="time-series-buckets"></a>
### 시계열 버킷 (Time series buckets)

각 트랙(track)마다 불러올 점의 개수를 지정할 수 있습니다.

**설명**: 트랙은 선박이나 항공기처럼 움직이는 객체의 시간별 위치 기록을 선으로 이은 것입니다. 원본 위치 기록이 10만 개여도 버킷 수를 1,000으로 두면 그 구간을 1,000개 점으로 나누어 불러오므로 화면 그리기가 가벼워집니다.

<a id="time-zone"></a>
### 시간대 (Time zone)

지도를 표시할 시간대를 지정할 수 있습니다. 시간대 옵션은 다음과 같습니다.

* Local(보는 사람 컴퓨터의 시간대를 사용합니다)
* UTC

<a id="time-format"></a>
### 시간 형식 (Time format)

지도를 표시할 시간 형식입니다.

* 12-hour(12시간제)
* 24-hour(24시간제)
* Local(로컬 형식)

시간대를 UTC로 설정하면 사용할 수 있는 시간 형식은 24-hour뿐입니다.

<a id="theme"></a>
### 테마 (Theme)

Map 앱을 **Light**(밝은) 모드와 **Dark**(어두운) 모드 사이에서 전환합니다. 이 설정은 배경 지도를 밝게 또는 어둡게 바꾸지 않으며, Map 애플리케이션의 UI만 바꿉니다.

![다크 모드가 켜진 지도.](https://www.palantir.com/docs/resources/foundry/map/settings-dark-mode.png)

<a id="enable-experimental-labels"></a>
### 실험적 라벨 활성화 (Enable experimental labels)

지도에서 [객체 라벨](../06_visualize-ontology-data/01_visualize-objects.md#labels)을 표시하고 배치하는 실험적 방법을 켤 수 있습니다. 이 방법은 라벨끼리 겹치거나 라벨이 객체를 가리는 경우를 최소화하려고 시도하는 배치 알고리즘을 적용합니다. 그러나 어떤 상황에서는(예: 라벨 수가 매우 많을 때) 결과 라벨 배치가 바람직하지 않거나, 라벨이 바람직하지 않거나 주의를 흩뜨리는 방식으로 위치를 바꿀 수 있습니다. 이 설정은 지도별 설정이며, 저장된 특정 지도를 사용하는 모든 사용자에게 적용됩니다.

> **중간 요약**: 지도 설정은 지도 자체에 저장되어 그 지도를 보는 모든 사용자에게 적용되며, 폴링 간격, 트랙당 점 개수, 시간대와 시간 형식, UI 테마, 실험적 라벨 배치가 있습니다.

## 정리

- 설정 메뉴는 Map 화면 오른쪽 위 톱니바퀴 아이콘으로 열며, 일부 값은 Control Panel의 조직 설정에 제한됩니다.
- 사용자 설정(모든 지도에 적용): 거리 단위(미터법, 야드파운드법, 해리법), GeoJSON 패널.
- 지도 설정(해당 지도의 모든 사용자에게 적용): 폴링 간격, 시계열 버킷, 시간대, 시간 형식(UTC면 24시간제만), 테마, 실험적 라벨.
- 테마는 앱 UI만 바꾸고 배경 지도는 바꾸지 않습니다.
