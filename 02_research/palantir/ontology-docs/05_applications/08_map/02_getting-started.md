# 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/map/getting-started/
- 사이드바 위치: Applications > Map > Getting started

이 페이지는 항공 노선 예제 데이터를 사용해 Map 애플리케이션을 처음 써 보는 튜토리얼입니다. 맵을 만들고, 화면 구성을 익히고, 공항 객체를 지도에 올리고, 링크로 연결된 활주로 객체를 찾고, 원을 그려 반경 검색을 하는 과정을 차례로 따라갑니다.

이 가이드는 **Foundry Training and Resources** 프로젝트의 리소스를 사용해 Map 애플리케이션을 쓰는 방법을 보여 줍니다. 이 예제에서는 항공 노선 데이터를 지리공간적으로 분석합니다.

<a id="create-a-new-map"></a>
## 새 맵 만들기 (Create a new map)

맵을 만들려면 왼쪽의 Foundry 탐색 바를 펼친 다음 Apps 섹션에서 **View all**을 클릭합니다. **Operational Applications** 섹션 아래에서 **Map** 애플리케이션을 찾을 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/navigation-bar-map.png" alt="Foundry 탐색 바의 Map 애플리케이션" width="430" />

<a id="map-application-interface-overview"></a>
## Map 애플리케이션 화면 개요 (Map application interface overview)

Map 애플리케이션이 로드되면 빈 지도가 표시됩니다.

![Map 애플리케이션](https://www.palantir.com/docs/resources/foundry/map/map-interface-overview.png)

화면 왼쪽에는 다음 패널이 있습니다.

* **Layers:** 객체 레이어와 오버레이 레이어를 추가, 관리하고 스타일을 지정하며 베이스 레이어를 설정합니다.
* **Find:** 객체와 위치를 찾고, 특정 지리 좌표로 이동합니다.
* **Histogram:** 속성 값과 시계열 값을 기준으로 객체를 분석하고 필터링합니다.
* **Info:** 맵 전체의 요약을 표시합니다.

화면 위쪽에는 다음 기능이 있는 도구 모음이 있습니다.

* **Select:** 맵의 모든 항목을 선택하거나, 선택을 반전하거나, 그린 도형과 교차하는 항목을 선택합니다.
* **Search Around:** 객체 관계를 탐색합니다.
* **Draw:** 다각형, 원, 사각형, 선, 점 등의 도형을 맵에 그리고 다룹니다.
* **Capture:** 현재 맵 상태의 스크린숏을 캡처합니다.
* **Measure:** 맵에서 물리적 거리를 측정합니다.
* **Annotate:** 맵에 텍스트 주석이나 다각형 주석을 추가합니다.
* **Delete:** 맵에서 항목을 제거합니다.

화면 오른쪽에는 다음 패널이 있습니다.

* **Selection:** 선택한 항목의 세부 정보를 분석하고 그 항목에 대해 액션을 수행합니다.
* **Time Selection:** 맵과 시계열 뷰에 적용할 시간 범위와 현재 타임스탬프를 설정합니다.

화면 오른쪽 아래에는 시계열 데이터와 이벤트 데이터의 시간 분석을 위한 **Series** 패널이 있습니다.

> **중간 요약**: 맵은 Apps 목록의 **Operational Applications**에서 만들며, 화면은 왼쪽 패널(Layers, Find, Histogram, Info), 위쪽 도구 모음, 오른쪽 패널(Selection, Time Selection), 오른쪽 아래 **Series** 패널로 구성됩니다.

<a id="add-an-object-to-the-map"></a>
## 맵에 객체 추가하기 (Add an object to the map)

이 예제에서는 디트로이트 메트로 공항(DTW)을 검색해 맵에 추가합니다.

먼저 **Layers** 패널에서 **Add to Map**을 클릭합니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/add-to-map-button.png" alt="Add to Map 버튼" width="328" />

그런 다음 `DTW`를 검색해 디트로이트 메트로 공항을 찾습니다. 오른쪽 목록에서 객체 타입 `[Example Data] Airport`를 선택해야 할 수도 있습니다. DTW 공항 객체를 선택하고 **Add selected**를 클릭합니다.

![디트로이트 메트로 공항 검색](https://www.palantir.com/docs/resources/foundry/map/tutorial-add-dialog-dtw-airport.png)

이제 맵이 DTW 공항으로 확대되어 보일 것입니다. 이 객체의 지리공간 데이터는 점(point)이므로, 객체는 좌표를 가리키는 맵 핀으로 표시됩니다. 아래와 같이 왼쪽 **Layers** 패널에는 `[Example Data] Airports` 레이어가 생겼고, 오른쪽 **Selection** 패널에는 선택한 객체의 세부 정보가 표시됩니다.

![디트로이트 메트로 공항이 표시된 맵](https://www.palantir.com/docs/resources/foundry/map/tutorial-dtw-on-map.png)

맵을 이리저리 이동해 보세요.

* 클릭한 채로 드래그하면 맵을 이동(pan)할 수 있습니다.
* 다음 방법 중 하나로 확대하거나 축소할 수 있습니다.
  * 마우스 휠 스크롤
  * 화면 왼쪽 아래 모서리의 확대/축소 버튼 클릭
  * 키보드의 **+** 키와 **-** 키 누르기

**설명**: 여기서 Airport 객체 타입은 위도와 경도를 담은 지리공간 속성을 가지고 있어 지도에 점으로 그려집니다. 객체를 맵에 추가하면 그 객체 타입 이름으로 레이어가 자동으로 생깁니다.

<a id="search-around-for-linked-objects"></a>
## Search Around로 링크된 객체 찾기 (Search Around for linked objects)

이 예제에서는 디트로이트 메트로 공항(DTW)에 대한 탐색적 분석을 수행합니다. 먼저 맵의 DTW 객체 아이콘을 마우스 오른쪽 버튼으로 클릭하고 **Search Around**를 선택한 다음 `[Example Data] Runway`를 골라 DTW의 활주로를 맵에 추가합니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/tutorial-searcharound-airport-runway.png" alt="디트로이트 메트로 공항의 Search Around 메뉴" width="684" />

그러면 활주로 객체도 맵에 추가된 것을 볼 수 있습니다. 활주로 객체는 맵에서 선으로 표시됩니다. 활주로 선 위에 마우스를 올리면 활주로 ID를 볼 수 있습니다. 활주로를 클릭해 선택하면 **Selection** 패널에서 더 자세한 내용을 볼 수도 있습니다.

![맵에 추가된 활주로](https://www.palantir.com/docs/resources/foundry/map/tutorial-added-runways.png)

**설명**: Search Around는 온톨로지의 링크 타입을 따라 연결된 객체를 가져오는 기능입니다. Airport와 Runway 사이에 링크 타입이 정의되어 있으므로, SQL로 치면 `SELECT * FROM runway WHERE airport_id = 'DTW'`에 해당하는 결과를 맵에 추가하는 셈입니다.

<a id="geospatial-search"></a>
## 지리공간 검색 (Geospatial search)

이 예제에서는 디트로이트 메트로 공항(DTW)에서 200킬로미터 안에 있는 다른 공항을 찾습니다.

먼저 **Draw**를 클릭해 도형 그리기 도구를 엽니다.

![도구 모음의 Draw 버튼](https://www.palantir.com/docs/resources/foundry/map/toolbar-draw-button.png)

그런 다음 **Circle**(원) 도구를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/tutorial-draw-tool-choose-circle.png" alt="원 도구" width="280" />

마지막으로 맵에서 DTW 공항을 클릭해 중심점을 정하고, "200"을 입력한 뒤 **km**를 선택합니다.

![반경 200km 검색](https://www.palantir.com/docs/resources/foundry/map/tutorial-200km-radius-search.png)

그러면 그 원과 교차하는 객체로 필터링된 Object Search 대화 상자가 열립니다. **Object Type** 목록에서 **\[Example Data] Airports** 를 선택하고 **Add all**을 클릭합니다. 그러면 공항 6개가 맵에 추가됩니다.

> **중간 요약**: **Add to Map**으로 객체를 검색해 맵에 올리고, **Search Around**로 링크된 객체를 따라가며, **Draw**의 원 도구로 반경 검색을 해 그 영역과 겹치는 객체를 추가할 수 있습니다.

## 정리

- Map은 Apps의 **Operational Applications**에서 열어 새 맵을 만듭니다.
- 화면은 왼쪽 패널(Layers, Find, Histogram, Info), 위쪽 도구 모음, 오른쪽 패널(Selection, Time Selection), **Series** 패널로 구성됩니다.
- **Add to Map**으로 객체를 검색해 추가하면 객체 타입별 레이어가 생기고, 점 데이터는 핀으로 표시됩니다.
- **Search Around**는 링크 타입을 따라 연결된 객체(예: 공항의 활주로)를 추가합니다.
- **Draw**로 원을 그리면 그 영역과 교차하는 객체만 검색해 추가할 수 있습니다.
