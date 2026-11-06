# 지도 Control Panel 설정 (Control Panel)

- 원문: https://www.palantir.com/docs/foundry/map/control-panel/
- 사이드바 위치: Applications > Map > Configuration > Control Panel

이 페이지는 관리자가 Control Panel에서 조직 전체에 적용되는 Map 설정을 바꾸는 방법을 다룹니다. 새 지도의 기본 화면, 데이터 불러오기 한도, 외부 지도 서비스 API 키, 배경 지도와 워터마크 같은 항목이 있습니다. 개별 사용자나 지도 단위의 설정([Settings](01_settings.md))은 여기서 정한 기본값과 한도 안에서 동작합니다.

[Control Panel](https://www.palantir.com/docs/foundry/administration/control-panel/)을 사용해 조직 전체에 적용되는 여러 Map 설정을 구성할 수 있습니다. Map 설정을 수정하려면 `Map Admin` 역할이 필요합니다.

![Control Panel의 Map 섹션.](https://www.palantir.com/docs/resources/foundry/map/control-panel-map-defaults.png)

일부 조직 수준 설정은 사용자가 [설정 메뉴](01_settings.md)에서 사용자 단위나 지도 단위로 재정의(override)할 수 있습니다.

<a id="map-defaults"></a>
## 지도 기본값 (Map Defaults)

* **Default viewport:** 사용자가 새 지도를 만들 때 보게 될 초기 화면을 중심점(위도와 경도)과 확대 수준으로 정의합니다.
* **Default time selection:** 사용자가 시간 범위를 선택할 때 보여 줄 날짜 옵션의 범위를 정의합니다.
* **Default unit system:** 모든 사용자 또는 특정 사용자 그룹에 대해 단위 체계(미터법, 야드파운드법, 해리법)를 설정합니다. 사용자는 [지도 설정](01_settings.md)에서 이 기본값을 재정의할 수 있습니다.

<a id="data-loading"></a>
## 데이터 불러오기 (Data loading)

* **Time series polling interval:** ["View Latest" 모드](../05_time/01_time-overview.md#selected-time-and-time-range)일 때 지도가 업데이트된 시계열(time series) 데이터를 얼마나 자주 확인할지 정의합니다.
  * **Default polling interval:** 새 지도의 기본 폴링 간격(초 단위)을 설정합니다. 사용자는 지도 안에서 이 설정을 재정의할 수 있습니다.
  * **Minimum allowed polling interval:** 재정의할 수 있는 폴링 간격의 최솟값(초 단위)을 설정합니다. 사용자는 개별 지도에서 이 값보다 짧은 폴링 간격을 설정할 수 없습니다.
* **Time series points:** 각 트랙마다 불러올 점의 개수를 정의합니다.
  * **Default time series point count:** 불러올 점의 기본 개수입니다.
  * **Maximum number of points:** 사용자가 개별 지도에서 기본 개수를 재정의할 때 지정할 수 있는 최대 점 개수입니다.
* **Object search limits:** 사용자가 검색 대화 상자에서 지도에 추가할 수 있는 객체의 최대 개수를 제어합니다.
* **Search around limits:** 사용자가 Search Around 한 번의 결과로 지도에 추가할 수 있는 객체의 최대 개수를 제어합니다.
* **Automatic object search:** 객체 검색 결과를 입력하는 동안 자동으로 불러올지, 수동으로 실행해야 할지를 제어합니다.

**설명**: 기본값과 최솟값, 최댓값을 함께 두는 이유는 서버 부하를 관리하기 위해서입니다. 예를 들어 기본 폴링 간격 30초, 최솟값 10초로 두면 사용자는 지도마다 간격을 20초로 줄일 수는 있지만 1초로 줄여 서버에 초당 요청을 보내게 할 수는 없습니다. 검색과 Search Around 한도도 지도 한 장에 수십만 개 객체가 올라가 브라우저가 멈추는 상황을 막는 역할을 합니다.

> **중간 요약**: 지도 기본값은 새 지도의 초기 화면, 시간 범위 옵션, 단위 체계를 정하고, 데이터 불러오기 설정은 폴링 간격과 점 개수의 기본값 및 한계, 객체 검색과 Search Around의 최대 객체 수, 자동 검색 여부를 정합니다.

<a id="api-keys"></a>
## API 키 (API Keys)

<a id="enable-find-locations-on-map"></a><a id="mapbox-enable-find-locations-on-map"></a>
### Mapbox: 지도에서 Find Locations 활성화 (Enable Find Locations on map)

[Find Locations](../04_interact-with-maps/05_navigation.md#find-locations) 기능은 Mapbox의 독점 지오코딩(geocoding) 서비스를 사용합니다. 조직에서 이 기능을 활성화하려면 Mapbox Geocoding API 접근 권한이 포함된 조직 전용 Mapbox API 키를 설정해야 합니다.

**설명**: 지오코딩은 "서울특별시청" 같은 주소나 장소 이름을 위도와 경도 좌표로 바꾸는 작업입니다. 이 변환을 외부 서비스가 수행하므로 그 서비스의 API 키가 필요합니다.

<a id="bing-maps-enable-bing-maps-base-layers"></a><a id="enable-bing-maps-base-layers"></a>
### Bing Maps: Bing Maps 배경 레이어 활성화 (Enable Bing Maps base layers)

기본 Mapbox 배경 레이어 대신 Bing Maps 배경 레이어를 사용하려면 Bing Maps API 키를 입력합니다.

<a id="base-maps"></a>
## 배경 지도 (Base maps)

<a id="enable-mapbox-base-maps"></a>
### Mapbox 배경 지도 활성화 (Enable Mapbox base maps)

Mapbox 스타일이 비활성화되면, Foundry 플랫폼의 지도 애플리케이션과 위젯은 기본적으로 첫 번째 사용자 정의(custom) 배경 지도를 사용합니다.

<a id="custom-base-map"></a>
### 사용자 정의 배경 지도 (Custom base map)

래스터 타일(Raster tiles) 또는 Mapbox JSON을 사용해 사용자 정의 배경 지도를 추가합니다.

![사용자 정의 배경 지도 설정 패널.](https://www.palantir.com/docs/resources/foundry/map/control-panel-custom-base-map.png)

<a id="watermark-configurations"></a>
### 워터마크 설정 (Watermark configurations)

워터마크는 기본값으로 또는 그룹별로 설정할 수 있습니다. 워터마크는 배경 지도 위에 겹쳐 표시됩니다.

!["demo"라는 워터마크가 표시된 지도 예시.](https://www.palantir.com/docs/resources/foundry/map/control-panel-watermark.png)

> **중간 요약**: API 키 설정으로 Mapbox 지오코딩 기반 Find Locations와 Bing Maps 배경 레이어를 켤 수 있고, 배경 지도 설정으로 Mapbox 사용 여부, 사용자 정의 배경 지도, 기본 또는 그룹별 워터마크를 정합니다.

## 정리

- Control Panel의 Map 설정은 조직 전체에 적용되며 `Map Admin` 역할이 있어야 바꿀 수 있습니다.
- 지도 기본값: 초기 화면, 시간 선택 범위, 단위 체계(사용자가 재정의 가능).
- 데이터 불러오기: 폴링 간격과 시계열 점 개수의 기본값과 한계, 객체 검색과 Search Around 최대 개수, 자동 검색 여부.
- API 키: Mapbox Geocoding(Find Locations), Bing Maps 배경 레이어.
- 배경 지도: Mapbox 사용 여부, 래스터 타일 또는 Mapbox JSON 기반 사용자 정의 배경 지도, 워터마크.
