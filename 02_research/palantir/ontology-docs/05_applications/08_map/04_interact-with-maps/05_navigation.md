# 탐색 (Navigation)

- 원문: https://www.palantir.com/docs/foundry/map/navigation/
- 사이드바 위치: Applications > Map > Interact with maps > Navigation

이 페이지는 맵의 보는 위치와 각도를 조작하는 방법을 설명합니다. 이동, 확대와 축소, 회전과 기울이기 같은 기본 조작, 선택한 객체로 맵 중심 맞추기, 그리고 **Find** 패널로 맵 위 객체, 주소나 지명, 좌표를 찾아가는 방법을 다룹니다.

Map 애플리케이션에서는 보기와 분석을 편하게 하도록 맵을 이동(pan), 확대/축소(zoom), 회전(rotate), 기울이기(tilt)할 수 있습니다. 단축키로 맵 중심을 빠르게 맞추거나, **Find** 패널로 맵에서 객체, 위치, 좌표를 찾을 수도 있습니다.

<a id="basic-map-controls"></a>
## 기본 맵 조작 (Basic map controls)

* 이동하려면 맵 뷰포트를 클릭한 채 드래그하거나 키보드의 화살표 키를 사용합니다.
* 확대하거나 축소하려면 다음 중 하나를 사용합니다.
  * 왼쪽 아래의 **Zoom in**, **Zoom out** 버튼
  * 마우스 휠
  * 키보드의 **+** 키와 **-** 키
* 맵을 회전하거나 기울이려면 Ctrl(Windows) 또는 Cmd(macOS)를 누른 채 클릭하고 드래그합니다.

<a id="center-the-map-on-items"></a>
## 항목에 맵 중심 맞추기 (Center the map on items)

키보드에서 **0**을 누르면 선택한 객체가 보이도록 맵을 이동합니다. 선택한 객체가 없으면 **0**은 맵의 모든 객체가 보이도록 맵을 이동합니다.

> **중간 요약**: 드래그나 화살표 키로 이동하고, 버튼이나 휠이나 **+**/**-** 키로 확대/축소하며, Ctrl 또는 Cmd를 누른 채 드래그해 회전과 기울이기를 합니다. **0** 키는 선택 항목(없으면 전체 객체)에 맞춰 화면을 이동합니다.

<a id="use-the-find-panel"></a>
## Find 패널 사용하기 (Use the Find panel)

**Find** 패널에서는 맵에 추가된 객체뿐 아니라 위치와 좌표로도 이동할 수 있습니다.

<a id="find-objects-on-map"></a>
### 맵 위 객체 찾기 (Find objects on map)

**Objects on map** 탭을 선택하고 검색어를 입력해 제목이나 속성 값으로 객체를 찾습니다. 결과를 선택하면 맵이 그 객체로 이동합니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/navigation-object-results.png" alt="객체 결과" width="450" />

<a id="find-locations"></a>
### 위치 찾기 (Find locations)

**주의**: API 키 필요(API key required). 이 기능을 사용하려면 조직에서 [Control Panel에 Mapbox API 키](../09_configuration/02_control-panel.md#api-keys)를 설정해 두어야 합니다.

**Locations** 탭을 선택하고 검색어를 입력해 주소나 이름으로 위치를 찾습니다. 결과를 선택하면 맵이 그 위치로 이동하고 위치의 주소가 담긴 마커를 표시합니다. 결과 목록에서 주소 옆의 **eye**(눈) 아이콘을 클릭하면 마커를 숨길 수 있습니다.

![위치 결과](https://www.palantir.com/docs/resources/foundry/map/navigation-location-results.png)

**설명**: 주소나 지명을 위도와 경도 좌표로 바꾸는 작업을 지오코딩(geocoding)이라고 합니다. Map은 이 작업을 외부 서비스인 Mapbox에 맡기므로, Mapbox API를 호출할 수 있는 키가 등록되어 있어야 이 탭이 동작합니다.

<a id="navigate-to-coordinates"></a>
### 좌표로 이동하기 (Navigate to Coordinates)

**Objects on map** 탭이나 **Locations** 탭 중 어느 것을 선택한 상태에서든, 검색 입력란에 좌표를 입력하고 결과를 선택해 맵을 그 좌표로 이동할 수 있습니다. **Show coordinates** 버튼을 사용하면 지정한 좌표에 텍스트 주석이 추가됩니다.

![좌표로 이동](https://www.palantir.com/docs/resources/foundry/map/navigation-coordinates.png)

> **중간 요약**: **Find** 패널의 **Objects on map** 탭은 맵 위 객체를, **Locations** 탭은 주소나 지명(Mapbox API 키 필요)을 찾으며, 두 탭 모두 좌표를 입력해 이동할 수 있습니다.

## 정리

- 이동은 드래그나 화살표 키, 확대/축소는 버튼이나 휠이나 **+**/**-** 키, 회전과 기울이기는 Ctrl 또는 Cmd를 누른 채 드래그합니다.
- **0** 키로 선택한 객체, 또는 선택이 없으면 전체 객체에 맞춰 화면을 이동합니다.
- **Find** 패널의 **Objects on map** 탭은 제목이나 속성 값으로 맵 위 객체를 찾습니다.
- **Locations** 탭은 주소나 이름으로 위치를 찾으며, Control Panel에 Mapbox API 키가 필요합니다.
- 두 탭 모두 좌표 입력으로 이동할 수 있고, **Show coordinates**로 그 지점에 텍스트 주석을 남길 수 있습니다.
