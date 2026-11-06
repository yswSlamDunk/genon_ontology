# 지도용 온톨로지 객체 (Ontology objects for the map)

- 원문: https://www.palantir.com/docs/foundry/map/integrate-objects/
- 사이드바 위치: Applications > Map > Integrate data for the map > Ontology objects for the map

이 페이지는 Map 애플리케이션에 객체를 표시하려면 온톨로지에서 객체 타입을 어떻게 설정해야 하는지 설명합니다. 점, 선, 다각형 같은 기본 지오메트리부터 원, 단계구분도(choropleth), H3 육각형, 지리 보정 이미지, 미디어 타일 이미지, 이동 궤적(track), 이벤트 객체까지, 지도에 그릴 수 있는 형태별로 필요한 속성과 설정 위치를 정리합니다.

Map 애플리케이션은 지리공간(geospatial) 데이터가 붙어 있는 온톨로지 객체를 지원합니다.

<a id="ontology-native-representation"></a>
## 온톨로지 기본 표현 (Ontology-native representation)

점, 선, 다각형 지오메트리는 `geopoint` 또는 `geoshape` 속성(property) 타입을 사용해 온톨로지에서 지정할 수 있습니다. 자세한 내용은 [지리공간 문서의 온톨로지 섹션](https://www.palantir.com/docs/foundry/geospatial/ontology/)을 참고하세요.

**설명**: `geopoint`는 위도와 경도 한 쌍(예: `37.5665, 126.9780`)으로 점 하나를 나타내는 타입입니다. `geoshape`는 선이나 다각형처럼 여러 좌표로 이루어진 도형을 담는 타입이며, 보통 GeoJSON(좌표 목록을 JSON으로 표현하는 표준 형식) 값을 저장합니다.

<a id="circles"></a>
## 원 (Circles)

객체 타입의 **Capabilities** 탭에 있는 **Geospatial** 섹션에서 **Radius** 속성을 선택하면 그 객체 타입에 원 지오메트리를 지정할 수 있습니다. 반지름 속성은 미터 단위로 측정되는 아무 숫자 속성이면 됩니다.

![Ontology Manager의 반지름 속성 설정](https://www.palantir.com/docs/resources/foundry/map/oma-capabilities-radius-earthquake.png)

**주의**: 원 지오메트리는 지도에 그려지기만 하고 검색용으로 인덱싱(indexing)되지는 않습니다. 원 지오메트리를 기준으로 객체를 지리공간 검색할 수 있어야 한다면 [다각형](#ontology-native-representation)으로 원을 근사해야 합니다.

**설명**: 예를 들어 지진(Earthquake) 객체에 진앙 `geopoint`와 `radius_m = 5000` 속성이 있으면, 지도에는 진앙을 중심으로 반지름 5km 원이 그려집니다. 하지만 "이 지역 안에 있는 객체 찾기" 같은 공간 검색은 인덱싱된 지오메트리만 대상으로 하므로 원 자체로는 검색되지 않습니다. 원을 검색 대상으로 만들려면 원 둘레를 점 여러 개(예: 64개)로 잘라 만든 다각형을 `geoshape` 속성에 저장해야 합니다.

> **중간 요약**: 점, 선, 다각형은 `geopoint`와 `geoshape` 속성으로, 원은 Capabilities 탭의 Radius 속성(미터)으로 지정합니다. 원은 화면 표시용일 뿐 검색 인덱스에는 들어가지 않습니다.

<a id="choropleths"></a>
## 단계구분도 (Choropleths)

[단계구분도 시각화](../06_visualize-ontology-data/04_visualize-choropleths.md)를 그리려면 객체를 지역 단위로 묶을 수 있도록 온톨로지를 설정해야 합니다. 방법은 **경계 식별자(boundary identifiers)와** **링크된 객체(linked objects)** 두 가지입니다.

**설명**: 단계구분도(choropleth)는 지역(나라, 주, 군 등)마다 집계 값을 계산해 그 값에 따라 지역을 다른 색으로 칠하는 지도입니다. 예를 들어 주별 주문 건수가 많을수록 진하게 칠합니다. 이를 위해서는 "각 객체가 어느 지역에 속하는가"를 알 수 있어야 하므로, SQL의 `GROUP BY region`에 해당하는 묶음 기준이 필요합니다.

<a id="boundary-identifiers"></a>
### 경계 식별자 (Boundary identifiers)

지도는 ISO 3166 국가 코드, 미국 주 약어 등 몇 가지 일반적인 지역 식별자 타입이 설정된 객체에 대해 단계구분도를 그리는 기능을 지원합니다. 이 경계 타입들의 다각형 지오메트리는 지도 애플리케이션에 내장되어 있으므로, 데이터에 이미 이런 식별자 중 하나가 붙어 있다면 데이터 통합이 쉬워집니다. 이 식별자는 지도에 표시하려는 객체 타입의 속성에 특정 [값 타입(Value Type)](../../../02_define-ontologies/02_object-and-link-types/08_value-types/01_value-types-overview.md)을 붙여서 설정합니다.

경계 식별자를 설정하려면 먼저 Marketplace에서 "Choropleth Value Types" 제품을 검색해 설치합니다. 이 제품에는 지도 애플리케이션이 단계구분도로 그릴 줄 아는 온톨로지 값 타입이 들어 있습니다.

![Marketplace의 Choropleth Value Types 제품 이미지](https://www.palantir.com/docs/resources/foundry/map/marketplace-choropleth-value-types.png)

현재 지원되는 지역 타입과 식별 방식은 다음과 같습니다.

* Admin 0 (전 세계 행정 구역 0단계 경계)
  * ISO 3166 alpha-2 국가 코드
  * ISO 3166 alpha-3 국가 코드
* 미국 주(US States)
  * FIPS 코드
  * USPS 약어
* 미국 카운티(US Counties)
  * FIPS 코드
  * ANSI 코드

객체 타입에 이미 이런 식별자 중 하나를 담은 속성이 있다면, Ontology Manager에서 그 속성의 **Value Type** 드롭다운 메뉴에서 해당 값 타입을 선택합니다.

![Ontology Manager의 Value Type 드롭다운 메뉴 이미지](https://www.palantir.com/docs/resources/foundry/map/oma-choropleth-value-type.png)

위 지역 타입 중 하나로 단계구분도를 표시하고 싶은데 데이터에 지원 식별자 대신 위도/경도 점만 있다면, Marketplace의 "Choropleth Boundary Datasets" 제품을 사용해 지역 식별자를 붙입니다. 이 제품에는 지역의 실제 지오메트리와 기타 메타데이터를 담은 데이터셋이 들어 있습니다. Pipeline Builder의 [Geometry intersection join](https://www.palantir.com/docs/foundry/pipeline-builder/transforms-geospatial/#geometry-intersection-joins)을 사용해 각 점이 속한 지역을 찾아 해당 지역 식별자를 붙인 다음, Ontology Manager에서 대응하는 값 타입을 설정합니다.

**설명**: ISO 3166 alpha-2는 `KR`, `US` 같은 두 글자 국가 코드, alpha-3는 `KOR`, `USA` 같은 세 글자 코드입니다. 지오메트리 교차 조인(geometry intersection join)은 일반 조인의 `ON a.key = b.key` 조건 대신 "점 a가 다각형 b 안에 있는가"를 조인 조건으로 쓰는 조인입니다. 예를 들어 매장 점 `(40.7, -74.0)`은 뉴욕주 다각형과 교차하므로 그 행에 `state = NY`가 붙습니다.

<a id="linked-objects"></a>
### 링크된 객체 (Linked objects)

위에 포함되지 않은 지역 타입으로 단계구분도를 표시하고 싶거나, 지역 지오메트리와 지역의 속성을 더 세밀하게 제어하고 싶다면, 원하는 지역 지오메트리를 가진 객체 타입을 직접 만들 수 있습니다. 그런 다음 집계하려는 객체 타입에서 그 지역 객체 타입으로 다대일(many-one) 링크를 만듭니다.

예를 들어 영업 지역별로 들어온 주문의 총액을 보여 주는 단계구분도를 표시하고 싶다고 합시다. 이를 위한 간단한 온톨로지 구성은 다음과 같습니다.

* 각 영업 지역의 지오메트리를 담은 geoshape 속성을 가진 "Sales region" 객체 타입
* 다음 속성을 가진 "Order" 객체 타입
  * 각 주문이 들어온 지역의 기본 키(primary key)를 담은 "Sales region"
  * 주문의 총액을 담은 "Value"
* "Order"에서 "Sales region"으로 가는 다대일 링크

단계구분도를 표시하려면 다음과 같이 합니다.

1. [검색 대화 상자](../04_interact-with-maps/03_add-to-map.md#add-ontology-objects)를 사용해 "Order" 객체를 지도에 추가합니다.
2. "Order" 레이어에 [**Choropleth** 디스플레이를 추가](../06_visualize-ontology-data/01_visualize-objects.md#displays)합니다.
3. [**Regions** 섹션](../06_visualize-ontology-data/04_visualize-choropleths.md#grouping-objects-into-regions)에서 **Linked object** 옵션을 고르고, "Order" 객체에서 그에 연결된 "Sales region"으로 가는 링크 타입을 선택합니다.
4. [집계 기반 스타일](../06_visualize-ontology-data/04_visualize-choropleths.md#styling-by-aggregation)에서 "Value" 속성을 사용해 각 지역의 색을 제어합니다.

**설명**: 이 구성은 SQL로 쓰면 `SELECT r.geometry, SUM(o.value) FROM orders o JOIN sales_region r ON o.sales_region = r.id GROUP BY r.id`와 같은 계산입니다. "Order"의 "Sales region" 속성이 외래 키 역할을 하고, 다대일 링크가 이 조인을 정의하며, 지도는 지역별 합계로 각 다각형의 색을 정합니다.

> **중간 요약**: 단계구분도를 그리려면 객체를 지역으로 묶을 기준이 필요합니다. 국가, 미국 주, 미국 카운티는 Marketplace의 값 타입을 속성에 붙이는 것으로 충분하고(좌표만 있으면 교차 조인으로 식별자를 먼저 붙임), 그 밖의 지역은 지역 객체 타입을 만들어 다대일 링크로 연결합니다.

<a id="h3-hexagons"></a>
## H3 육각형 (H3 hexagons)

객체는 [H3 지리공간 인덱싱 시스템 ↗](https://h3geo.org/docs/)의 H3 셀 ID를 담은 문자열 속성을 가질 수 있습니다. 이 속성은 지도에서 해당 육각형으로 그려집니다.

문자열 속성이 H3 셀 ID를 담고 있다고 지정하려면, 객체 타입의 **Capabilities** 탭에 있는 Geospatial 섹션의 **H3 cell** 아래에서 그 속성을 선택합니다.

![Ontology Manager의 H3 속성 설정](https://www.palantir.com/docs/resources/foundry/map/oma-capabilities-h3-tree.png)

**주의**: H3 육각형은 Map에 그려지기만 하고 검색용으로 인덱싱되지는 않습니다. H3 육각형을 기준으로 객체를 지리공간 검색할 수 있어야 한다면, H3 셀 ID를 GeoJSON 다각형으로 변환해 위에서 설명한 `geoshape` 속성에 넣어야 합니다.

**설명**: H3는 지구 표면을 육각형 격자로 나누고 각 칸에 `8a2a1072b59ffff` 같은 문자열 ID를 붙이는 체계입니다. ID 하나가 육각형 칸 하나를 뜻하므로, 객체에 이 문자열만 저장해 두면 지도가 ID에서 육각형 모양을 계산해 그릴 수 있습니다.

<a id="georectified-images"></a>
## 지리 보정 이미지 (Georectified images)

객체에는 위성 사진, 항공 이미지, 실물 지도 스캔본 같은 지리 보정(georectified) 이미지를 붙일 수 있습니다. 지리 보정 이미지에는 두 속성이 필요합니다.

* 그릴 이미지의 URL을 담은 이미지 URL `String` 속성. 지원되는 이미지 파일 확장자는 `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.bmp`, `.ico`, `.svg`입니다. 이미지 URL 속성의 ID는 이미지 경계 속성을 설정하는 데 쓰입니다.
* 이미지의 지리 보정된 경계를 나타내는 사각형의 GeoJSON 다각형을 담은 이미지 경계 `geoshape` 속성. 다각형은 왼쪽 아래 꼭짓점에서 시작해 시계 방향 순서로 꼭짓점을 지정해야 합니다.
  * 이미지 경계 속성에는 이미지 URL 속성의 ID를 가리키는 타입 클래스(type class)가 다음 형식으로 있어야 합니다.
    * Kind: `geo`
    * Value: `bounds.<image URL property ID>` (여기서 `<image URL property ID>`는 이미지 URL 속성의 ID입니다.)
  * 예를 들어 이미지 URL 속성 ID가 `image_url`이면 타입 클래스는 Kind: `geo`, Value: `bounds.image_url`이 됩니다.

![Ontology Manager의 지리 보정 이미지 속성 설정](https://www.palantir.com/docs/resources/foundry/map/oma-geo-bounds-typeclass.png)

지리 보정 이미지를 가진 객체는 다른 모든 `geoshape` 속성과 마찬가지로 지리공간 검색용으로 인덱싱됩니다.

**설명**: 지리 보정(georectification)은 이미지의 네 모서리가 실제 지구상의 어느 좌표에 해당하는지 정해, 지도 위 올바른 위치에 이미지를 펼쳐 놓을 수 있게 하는 작업입니다. 타입 클래스 `bounds.image_url`은 "이 경계 다각형은 `image_url` 속성의 이미지에 대한 것"이라는 연결 정보를 남기는 메타데이터 표시입니다.

<a id="tiled-imagery-from-media-sets-beta"></a>
## 미디어 세트의 타일 이미지 \[베타] (Tiled imagery from media sets \[Beta])

**참고**: 베타(Beta). Maps에서 미디어 참조를 사용하는 기능은 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며, 여러분의 환경(enrollment)에서는 사용할 수 없을 수도 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다.

지리 참조된 래스터 이미지는 GeoTIFF 이미지(`.tiff`, `.tif`)를 [미디어 세트(media set)](https://www.palantir.com/docs/foundry/data-integration/media-sets/)에 업로드하여 타일 형태로 표시할 수도 있습니다. 그런 다음 [미디어 참조 속성](https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-overview/#media-references)을 가진 객체 타입을 지도에 추가할 수 있으며, 사용자가 Map을 이동하거나 확대/축소할 때 이미지 중 보이는 부분만 불러옵니다.

**설명**: 타일(tile) 방식은 큰 이미지를 작은 정사각형 조각 여러 개로 나누어, 화면에 보이는 조각만 요청하는 방식입니다. 수 GB짜리 위성 이미지 전체를 한 번에 내려받지 않아도 되므로 큰 래스터(픽셀 격자) 이미지에 적합합니다.

> **중간 요약**: H3 셀 ID 문자열은 육각형으로 그려지지만 검색 인덱스에는 들어가지 않습니다. 지리 보정 이미지는 이미지 URL 속성과 `bounds.<ID>` 타입 클래스가 붙은 경계 `geoshape` 속성으로 설정하며 검색 인덱싱됩니다. GeoTIFF는 미디어 세트를 통해 타일로 표시할 수 있습니다(베타).

<a id="track-objects"></a>
## 궤적 객체 (Track objects)

객체는 시간에 따른 위도와 경도를 나타내는 숫자형 [시계열 속성](https://www.palantir.com/docs/foundry/time-series/time-series-overview/)을 가질 수 있습니다. 이를 통해 사용자는 객체가 시간에 따라 이동한 경로와, 임의 시점의 위치를 볼 수 있습니다.

객체 타입의 궤적을 설정하려면 객체 타입의 **Capabilities** 탭에 있는 **Geospatial** 섹션에서 **Track Latitude**와 **Track Longitude** 속성을 선택합니다. 두 속성 모두 시간에 따른 객체의 위치를 나타내는 숫자형 시계열 속성이어야 합니다. 시계열 설정에 대한 자세한 내용은 [시계열 설정](https://www.palantir.com/docs/foundry/time-series/time-series-setup/)을, 지도에서 궤적을 시각화하는 옵션은 [궤적 디스플레이](../06_visualize-ontology-data/07_visualize-tracks.md)를 참고하세요.

![Ontology Manager의 궤적 위도 및 경도 설정](https://www.palantir.com/docs/resources/foundry/map/oma-capabilities-track-lat-lon.png)

**설명**: 시계열 속성은 값 하나가 아니라 `(시각, 값)` 쌍의 목록을 담는 속성입니다. 예를 들어 선박 객체의 위도 시계열이 `[(10:00, 35.10), (10:05, 35.12), (10:10, 35.15)]`이고 경도 시계열도 같은 시각들에 값을 가지면, 두 값을 시각별로 짝지어 이동 경로 선을 그리고 특정 시각의 위치를 표시할 수 있습니다.

<a id="event-objects"></a>
## 이벤트 객체 (Event objects)

이벤트 객체는 특정 시점이나 기간에 발생하는 온톨로지 객체입니다. 객체 타입의 **Capabilities** 탭에 있는 **Event** 섹션에서 **Event start time**과 **Event end time** 타임스탬프 속성을 지정하면 객체 타입을 이벤트로 설정할 수 있습니다.

![Ontology Manager의 이벤트 설정](https://www.palantir.com/docs/resources/foundry/map/oma-capabilities-event.png)

<a id="event-objects-on-the-map"></a>
### 지도 위의 이벤트 객체 (Event objects on the map)

이벤트 객체를 Map에 추가하면, 현재 진행 중일 때(즉 선택한 타임스탬프가 이벤트 기간 안에 있을 때)만 표시되도록 설정할 수 있습니다.

<a id="event-objects-linked-to-objects-on-the-map"></a>
### 지도 위 객체에 링크된 이벤트 객체 (Event objects linked to objects on the map)

지도 위의 객체에 이벤트 객체가 링크되어 있으면, 그 이벤트 객체를 시간 분석을 위해 **Series** 패널에 추가할 수 있고, 객체 레이블에 현재 이벤트 수 표시기를 붙일 수 있습니다. 예를 들어 `road` 객체를 지도에 선으로 표현하고, `road` 객체에 `traffic accident` 이벤트가 링크되어 있다고 합시다. 사용자는 표시기를 사용해 임의 시점에 각 도로의 교통 사고 이벤트 수를 볼 수 있습니다.

이것이 가능하려면 이벤트 객체 타입의 **Capabilities** 탭에 있는 **Event** 섹션에서 이벤트의 심각도를 나타내는 **Event intent**를 설정해야 합니다.

**설명**: "현재 진행 중" 판단은 `event_start <= 선택 시각 <= event_end` 비교입니다. 예를 들어 사고 이벤트가 14:00\~14:30이면, 지도 시간 슬라이더를 14:10에 두었을 때만 표시되고 15:00으로 옮기면 사라집니다. 도로별 이벤트 수 표시기는 선택 시각에 진행 중인 링크된 이벤트를 도로마다 세는 것으로 이해할 수 있습니다.

> **중간 요약**: 위도와 경도 시계열 속성 두 개를 지정하면 이동 궤적을 그릴 수 있습니다. 시작/종료 타임스탬프로 이벤트 객체를 정의하면 선택 시각에 진행 중인 것만 표시하거나, 링크된 객체의 이벤트 수를 표시할 수 있으며, 후자에는 Event intent 설정이 필요합니다.

## 정리

- 점, 선, 다각형은 `geopoint`와 `geoshape` 속성으로 표현하며 검색 인덱싱됩니다.
- 원(Radius 속성)과 H3 육각형(H3 cell 속성)은 지도에 그려지기만 하고 검색되지 않으므로, 검색이 필요하면 다각형으로 바꿔 `geoshape`에 저장해야 합니다.
- 단계구분도는 Marketplace 값 타입을 붙인 경계 식별자 속성이나, 지역 객체 타입으로 가는 다대일 링크로 지역 묶음을 정의합니다.
- 지리 보정 이미지는 이미지 URL 속성과 `bounds.<ID>` 타입 클래스가 붙은 경계 속성으로, 대형 래스터는 미디어 세트 타일(베타)로 표시합니다.
- 위도/경도 시계열 속성은 이동 궤적을, 시작/종료 타임스탬프는 이벤트 객체를 만들며, 링크된 이벤트 수 표시에는 Event intent가 필요합니다.
