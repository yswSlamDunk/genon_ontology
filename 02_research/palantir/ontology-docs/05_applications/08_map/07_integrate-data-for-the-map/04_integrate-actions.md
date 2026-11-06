# 지도의 온톨로지 액션 (Ontology Actions for the map)

- 원문: https://www.palantir.com/docs/foundry/map/integrate-actions/
- 사이드바 위치: Applications > Map > Integrate data for the map > Ontology Actions for the map

이 페이지는 Map 애플리케이션에서 지도 위의 점, 도형, 선을 입력으로 받아 실행되는 액션 타입을 정의하는 방법을 다룹니다. 지도에서 한 지점을 우클릭해 "여기에 새 시설 객체 만들기"를 하거나, 다각형을 그려 구역 객체를 만드는 식의 작업이 여기에 해당합니다. Map이 어떤 액션을 메뉴에 보여 줄지는 액션 파라미터의 타입 클래스(type class)로 결정되므로, 그 규칙을 설명합니다.

원문 페이지 제목은 "온톨로지 액션(Ontology Actions)"입니다.

Map 애플리케이션에서 사용자가 지리공간(geospatial) 객체에 적용할 수 있는 [액션](../../../02_define-ontologies/03_action-types/01_overview.md)을 온톨로지에 설정할 수 있습니다. 예를 들어 지도에서 선택한 점, 그린 다각형이나 선을 바탕으로 객체를 생성하거나 편집(edit)하는 액션이 있을 수 있습니다.

**설명**: 타입 클래스는 파라미터에 붙이는 `Kind`와 `Value` 한 쌍의 메타데이터 태그입니다. 파라미터의 데이터 타입은 그냥 `String`이지만, `Kind: geo, Value: geopoint` 태그가 붙어 있으면 Map은 "이 문자열 칸에는 좌표를 넣으면 된다"는 것을 알고 사용자가 클릭한 위치를 자동으로 채워 줍니다.

<a id="point-actions"></a>
## 점 액션 (Point Actions)

사용자가 지도 또는 점 객체를 우클릭하면, 액션 메뉴에 지리공간 점에 적용되는 모든 온톨로지 액션이 표시됩니다. 점에 적용되는 액션을 정의하려면 액션에 다음 중 하나가 있어야 합니다.

* 타입 클래스가 Kind: `geo`, Value: `geopoint`인 `String` 파라미터(데이터는 `latitude,longitude` 형식의 문자열), 또는

![Ontology Manager의 Geopoint 액션 파라미터](https://www.palantir.com/docs/resources/foundry/map/integrate-actions-geopoint-param.png)

* `Double` 파라미터 두 개:
  * 위도(latitude)가 전달될 파라미터. 타입 클래스는 Kind: `geo`, Value: `latitude`
  * 경도(longitude)가 전달될 파라미터. 타입 클래스는 Kind: `geo`, Value: `longitude`

![Ontology Manager의 위도 액션 파라미터](https://www.palantir.com/docs/resources/foundry/map/integrate-actions-latitude-param.png)

![Ontology Manager의 경도 액션 파라미터](https://www.palantir.com/docs/resources/foundry/map/integrate-actions-longitude-param.png)

**설명**: 예를 들어 사용자가 서울시청 근처를 우클릭하면, 첫 번째 방식에서는 `String` 파라미터에 `"37.5663,126.9779"`가 들어가고, 두 번째 방식에서는 위도 파라미터에 `37.5663`, 경도 파라미터에 `126.9779`가 각각 들어갑니다.

> **중간 요약**: 점 액션은 `geo`/`geopoint` 타입 클래스의 문자열 파라미터 하나, 또는 `geo`/`latitude`와 `geo`/`longitude` 타입 클래스의 실수 파라미터 두 개로 정의합니다.

<a id="shape-actions"></a>
## 도형 액션 (Shape Actions)

사용자가 다각형(polygon) 객체를 선택하거나 지도에 도형을 그리면, **Actions** 메뉴에 지리공간 도형에 적용되는 모든 온톨로지 액션이 표시됩니다. 도형에 적용되는 액션을 정의하려면, 액션에 타입 클래스가 Kind: `geo`, Value: `geojson`인 `String` 파라미터가 있어야 하며, 이 파라미터의 데이터는 GeoJSON geometry 문자열입니다.

![Ontology Manager의 Geojson 액션 파라미터](https://www.palantir.com/docs/resources/foundry/map/integrate-actions-geojson-param.png)

**설명**: GeoJSON은 지리 정보를 JSON으로 표현하는 표준 형식입니다. 사각형 구역 하나는 예를 들어 `{"type":"Polygon","coordinates":[[[126.97,37.56],[126.98,37.56],[126.98,37.57],[126.97,37.57],[126.97,37.56]]]}`처럼 꼭짓점 좌표 목록(경도, 위도 순서이며 처음과 끝 점이 같음)으로 표현되고, 이 문자열이 파라미터로 전달됩니다.

> **중간 요약**: 도형 액션은 `geo`/`geojson` 타입 클래스의 문자열 파라미터로 정의하며, 그 값으로 GeoJSON geometry 문자열을 받습니다.

<a id="use-actions-to-edit-object-geoshape-properties"></a>
## 액션으로 객체의 `geoshape` 속성 편집하기 (Use actions to edit object `geoshape` properties)

사용자가 지도에서 객체의 `geoshape` 속성(property)을 편집할 수 있도록 액션을 설정할 수 있습니다. 사용자는 객체를 선택하고, **Actions** 메뉴에서 해당 액션을 고른 다음, 필요에 따라 도형을 수정할 수 있습니다(예: 점 추가 또는 이동, 버퍼링(buffering), 도형 평행 이동).

![도형 업데이트 액션 사용하기](https://www.palantir.com/docs/resources/foundry/map/integrate-actions-applying-shape-update.gif)

지도에서 사용자가 객체의 `geoshape` 속성을 편집할 수 있게 하는 액션을 설정하려면, 원하는 객체 타입에 대해 "Modify object"(객체 수정) 액션을 만들고, 다음 요구 사항을 모두 만족하는 파라미터를 둡니다.

* `String` 파라미터입니다.
* 업데이트하려는 객체의 `geoshape` 속성에 매핑되어 있습니다.
* 기본값(default value)이 비활성화되어 있습니다.
* 타입 클래스 Kind: `geo`, Value: `geojson`을 가집니다.
* 타입 클래스 Kind: `geo`, Value: `prefill`을 가집니다.

![Ontology Manager의 도형 업데이트 액션 파라미터](https://www.palantir.com/docs/resources/foundry/map/integrate-actions-oma-shape-param.png)

![Ontology Manager의 도형 업데이트 액션 파라미터 타입 클래스](https://www.palantir.com/docs/resources/foundry/map/integrate-actions-oma-shape-param-details.png)

**설명**: 버퍼링은 도형의 경계를 일정 거리만큼 바깥(또는 안쪽)으로 넓히는 지리공간 연산입니다. `prefill` 타입 클래스는 액션을 열 때 선택한 객체의 현재 도형을 파라미터에 미리 채워 넣어, 사용자가 처음부터 다시 그리지 않고 기존 도형을 고칠 수 있게 하는 역할을 합니다. 파라미터 하나에 `geojson`과 `prefill` 두 타입 클래스를 함께 붙인다는 점에 유의하세요.

> **중간 요약**: 기존 객체의 `geoshape` 속성을 지도에서 고치게 하려면 "Modify object" 액션에 `geoshape` 속성과 매핑된, 기본값이 꺼진 `String` 파라미터를 두고 `geo`/`geojson`과 `geo`/`prefill` 타입 클래스를 모두 붙입니다.

## 정리

- Map은 액션 파라미터의 타입 클래스(Kind `geo`)를 보고 지도 위 점이나 도형에 적용할 수 있는 액션을 메뉴에 보여 줍니다.
- 점 액션: `geopoint` 문자열 파라미터 하나, 또는 `latitude`, `longitude` 실수 파라미터 두 개.
- 도형 액션: GeoJSON geometry 문자열을 받는 `geojson` 문자열 파라미터.
- `geoshape` 편집 액션: "Modify object" 액션에서 `geoshape` 속성에 매핑되고 기본값이 꺼진 문자열 파라미터에 `geojson`과 `prefill` 타입 클래스를 함께 지정합니다.
