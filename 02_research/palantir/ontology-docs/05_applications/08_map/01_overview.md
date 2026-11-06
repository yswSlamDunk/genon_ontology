# Map 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/map/overview/
- 사이드바 위치: Applications > Map > Overview

이 페이지는 Foundry의 **Map** 애플리케이션이 무엇을 할 수 있는지 소개합니다. Map은 온톨로지 객체와 각종 지리 데이터를 한 지도 위에 모아 공간적(어디에 있는가)이고 시간적(언제 있었는가)인 분석을 하는 도구입니다. 또 Map이 사용하는 좌표계와 지도 투영법을 함께 설명합니다.

**Map** 애플리케이션은 강력한 지리공간(geospatial) 분석, 시간 분석, 시각화 기능을 제공하며, Foundry 곳곳의 데이터를 하나의 일관된 지리공간 환경으로 통합할 수 있게 해 줍니다.

* 지리공간 객체 사이의 연결을 탐색하고 물리적 네트워크를 따라갑니다.
* 경계 상자(bounding box)와 다각형 교차(polygon intersection) 질의를 사용해 점(point) 데이터와 다각형(polygon) 데이터를 지리공간적으로 검색합니다.
* 대규모 벡터 데이터와 위성 이미지를 비롯한 다양한 출처의 맥락 지리공간 데이터, 그리고 시간에 따른 객체 이동 경로나 이벤트 같은 시간 데이터를 시각화합니다.
* 도형을 그리고 지리공간 액션을 수행하며 상호작용합니다.
* 맵 템플릿을 사용해 지리공간 애플리케이션을 만듭니다.

![Map 애플리케이션](https://www.palantir.com/docs/resources/foundry/map/map-overview.png)

**설명**: 경계 상자 질의는 "위도 37\~38도, 경도 126\~127도 사이에 있는 모든 점"처럼 직사각형 범위로 찾는 검색입니다. 다각형 교차 질의는 사용자가 그린 임의의 다각형과 겹치는 객체를 찾는 검색입니다. 벡터 데이터는 점, 선, 다각형처럼 좌표로 표현한 도형 데이터이고, 위성 이미지는 픽셀 격자로 된 래스터(raster) 데이터입니다.

<a id="geospatial-data-on-the-map"></a>
## Map의 지리공간 데이터 (Geospatial data on the Map)

Map 애플리케이션은 [Web Mercator 투영법 ↗](https://en.wikipedia.org/wiki/Web_Mercator_projection)(EPSG:3857)을 사용해 지도를 그리며, 위도와 경도 좌표는 WGS 84 도(degree) 단위(EPSG:4326)로 받는다고 가정합니다. Foundry에서 지리공간 데이터를 변환하는 방법은 [Foundry의 지리공간 데이터](https://www.palantir.com/docs/foundry/geospatial/overview/)를 참고하세요.

**설명**: 지구는 곡면이므로 평면 화면에 그리려면 투영법이 필요합니다. Web Mercator(EPSG:3857)는 Google 지도 등 대부분의 웹 지도가 쓰는 투영법입니다. WGS 84(EPSG:4326)는 GPS가 쓰는 좌표 체계로, 위도와 경도를 도 단위 숫자로 나타냅니다(예: 서울 시청은 위도 약 37.566, 경도 약 126.978). 즉 데이터는 위도와 경도로 저장하고, 화면에 그릴 때 Map이 Web Mercator로 변환합니다. EPSG 번호는 좌표계를 식별하는 표준 코드입니다.

## 정리

- Map은 Foundry 데이터를 하나의 지도 위에서 지리공간적, 시간적으로 분석하고 시각화하는 애플리케이션입니다.
- 객체 간 연결 탐색, 경계 상자와 다각형 검색, 벡터와 위성 이미지와 이동 경로 시각화, 도형 그리기와 지리공간 액션, 템플릿 기반 애플리케이션 구축을 지원합니다.
- 지도는 Web Mercator(EPSG:3857)로 그리고, 좌표 입력은 WGS 84 위도와 경도(EPSG:4326)를 기대합니다.
