# 맵에 데이터 추가하기 (Add data to a map)

- 원문: https://www.palantir.com/docs/foundry/map/add-to-map/
- 사이드바 위치: Applications > Map > Interact with maps > Add data to a map

이 페이지는 맵에 데이터를 올리는 여러 방법을 설명합니다. 온톨로지 객체를 검색과 필터로 찾아 추가하는 방법, 그린 도형과 겹치는 객체만 찾는 지리공간 검색, 미리 만들어 둔 맵 오버레이 추가, 그리고 이미 맵에 있는 객체에서 링크를 따라 관련 객체를 추가하는 Search Around를 다룹니다.

맵에 데이터를 추가하는 것으로 지리공간 분석을 시작합니다. Foundry 플랫폼에서 맵에 추가할 수 있는 지리공간 데이터는 두 종류입니다. 온톨로지 객체와 맵 오버레이입니다.

**Layers** 패널에서 **+ Add to map**을 클릭하면 검색 대화 상자를 통해 이 두 종류의 데이터를 맵에 추가할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/add-to-map-button.png" alt="Add to map 버튼" width="328" />

<a id="add-ontology-objects"></a>
## 온톨로지 객체 추가하기 (Add Ontology objects)

검색 대화 상자의 **Objects** 탭에서 [지리공간 데이터를 가진 온톨로지 객체](../07_integrate-data-for-the-map/01_integrate-objects.md)를 맵에 추가할 수 있습니다.

![객체 검색 대화 상자](https://www.palantir.com/docs/resources/foundry/map/add-to-map-objects-dialog.png)

대화 상자에서는 위쪽의 기본 **Search...** 입력란에 아무 질문이나 입력해 객체를 검색하거나, 왼쪽의 필터 패널을 사용해 검색할 객체 범위를 좁힐 수 있습니다.

[Control Panel에서 객체 검색 한도를 설정](../09_configuration/02_control-panel.md#data-loading)할 수도 있습니다.

<a id="filter-objects"></a>
### 객체 필터링 (Filter objects)

객체 타입을 선택하면 결과를 그 타입의 객체만 포함하도록 필터링합니다. 객체 타입을 선택한 뒤에는 **Filters** 옵션으로 검색을 더 세밀하게 좁힐 수 있습니다.

![객체 타입으로 필터링된 결과](https://www.palantir.com/docs/resources/foundry/map/objects-add-type-selected.png)

가장 자주 쓰이는 속성 일부가 필터 영역에 자동으로 나타나므로, 관심 있는 속성의 값을 선택해 객체 결과를 좁힐 수 있습니다.

![객체 타입으로 필터링된 결과](https://www.palantir.com/docs/resources/foundry/map/objects-add-filters.png)

**+ Add filter**를 선택하고 원하는 속성을 추가하면 객체 타입의 어떤 속성으로든 필터링할 수 있습니다. **Back**을 선택하면 고른 속성이 필터 영역에 나타납니다.

![필터 추가](https://www.palantir.com/docs/resources/foundry/map/objects-add-filter-selector.png)

**설명**: 필터는 SQL의 `WHERE` 절에 해당합니다. 예를 들어 Airport 객체 타입을 고르고 `country` 속성 값으로 "United States"를 선택하면 `SELECT * FROM airport WHERE country = 'United States'`와 같은 범위의 객체만 결과에 남습니다.

<a id="select-and-add-results"></a>
### 결과 선택하고 추가하기 (Select and add results)

결과 표에서 객체를 선택합니다. `Cmd`(macOS) 또는 `Ctrl`(Windows) 키를 누른 채 클릭하면 객체 선택을 하나씩 켜고 끌 수 있고, 여기에 `Shift` 키를 사용하면 객체 범위를 한꺼번에 선택할 수 있습니다. **+ Add selected**로 선택한 객체를 맵에 추가하거나, **Add all**로 검색에 일치한 모든 객체를 추가합니다.

맵은 검색 대화 상자에서 추가할 수 있는 객체 수를 제한합니다. 기본값으로 1000개까지 추가할 수 있습니다. 이 한도에 도달하면 **Add all** 옵션이 비활성화되며, 옵션이 다시 활성화되도록 [결과를 필터링](#filter-objects)해 객체 수를 줄여야 합니다.

![비활성화된 Add all](https://www.palantir.com/docs/resources/foundry/map/objects-add-add-all-disabled.png)

> **중간 요약**: **Objects** 탭에서 검색어, 객체 타입, 속성 필터로 객체를 찾아 **+ Add selected** 또는 **Add all**로 추가합니다. 한 번에 추가할 수 있는 객체는 기본 1000개이며, 넘으면 필터로 줄여야 합니다.

<a id="search-for-objects-geospatially"></a>
## 지리공간적으로 객체 검색하기 (Search for objects geospatially)

특정 관심 지역 안에 있는 객체를 검색할 수 있습니다. **Add to map** 드롭다운에서 **Search for objects that intersect a shape...**(도형과 교차하는 객체 검색)를 선택합니다.

![도형과 교차하는 객체 검색](https://www.palantir.com/docs/resources/foundry/map/objects-add-search-shape.png)

그러면 검색하려는 지리 영역 둘레에 [도형](08_shapes.md)을 그리라는 안내가 나옵니다.

![도형과 교차하는 객체 검색](https://www.palantir.com/docs/resources/foundry/map/objects-add-draw-shape.png)

도형을 다 그리면 객체 검색 대화 상자가 열리고, 그린 도형과 교차하는 지리공간 데이터를 가진 객체만 표시됩니다.

![교차하는 객체로 필터링된 검색 대화 상자](https://www.palantir.com/docs/resources/foundry/map/objects-add-dialog-intersecting.png)

**설명**: "교차한다(intersect)"는 두 도형이 한 점이라도 공유한다는 뜻입니다. 점 객체는 도형 안에 있으면 교차하고, 선이나 다각형 객체는 도형과 일부만 겹쳐도 교차로 판정됩니다. 예를 들어 그린 사각형에 활주로 선의 한쪽 끝만 들어가도 그 활주로는 결과에 포함됩니다.

<a id="add-map-overlays"></a>
## 맵 오버레이 추가하기 (Add map overlays)

검색 대화 상자의 **Overlays** 탭에서는 [Map Layer Editor](../07_integrate-data-for-the-map/05_layer-editor.md)로 만든 레이어를 추가할 수 있습니다. 이 레이어에는 여러 맵에서 재사용할 수 있도록 미리 설정해 둔 지리공간 데이터셋의 뷰가 들어 있습니다.

![오버레이 대화 상자](https://www.palantir.com/docs/resources/foundry/map/add-to-map-overlays.png)

대화 상자에서는 여러 방법으로 레이어를 찾을 수 있습니다.

* 위쪽의 **Search...** 입력란에 텍스트를 입력해 이름으로 레이어를 찾습니다.
* 사이드바의 **Tags** 섹션을 사용해 레이어 결과를 특정 주제로 좁힙니다.
* **In path** 입력란에 폴더 경로를 입력해 특정 폴더나 프로젝트 안의 레이어를 찾습니다.
* **Created by**에서 사용자를 선택해 특정 사용자가 만든 레이어를 찾습니다.

레이어를 선택합니다. `Cmd`(macOS) 또는 `Ctrl`(Windows) 키를 누른 채 클릭하면 레이어 선택을 하나씩 켜고 끌 수 있고, Shift 키를 사용하면 레이어 범위를 선택할 수 있습니다. **Add layers**로 선택한 레이어를 맵에 추가합니다.

> **중간 요약**: 도형을 그려 그 영역과 교차하는 객체만 검색할 수 있고, **Overlays** 탭에서는 Map Layer Editor로 미리 만든 재사용 레이어를 이름, 태그, 경로, 작성자로 찾아 추가합니다.

<a id="search-around"></a>
## Search Around

이미 맵에 있는 객체에서 출발해 온톨로지 관계를 따라가며 **Search Around**로 관련 객체를 맵에 추가할 수 있습니다. 먼저 맵에서 객체 몇 개를 선택한 다음 **Search Around**를 선택합니다.

![Search Around 메뉴](https://www.palantir.com/docs/resources/foundry/map/objects-add-search-around-menu.png)

관련 객체 목록에서 선택하면 그 객체들이 맵에 추가됩니다. 관련 객체가 점으로 표시되는 경우, 맵은 관련 객체 사이에 시각적인 링크를 그립니다.

![Search Around 링크](https://www.palantir.com/docs/resources/foundry/map/objects-add-search-around-links.png)

**설명**: 관련 객체 목록에 나오는 항목은 선택한 객체 타입에 정의된 링크 타입들입니다. 예를 들어 Airport에 Runway, Flight 링크 타입이 정의되어 있다면 두 항목이 목록에 나타나고, Flight를 고르면 선택한 공항과 링크로 연결된 항공편 객체가 추가됩니다.

> **중간 요약**: Search Around는 맵에 있는 객체의 링크 타입을 따라 관련 객체를 추가하며, 점 객체끼리는 연결선이 그려집니다.

## 정리

- 맵에 추가할 수 있는 데이터는 온톨로지 객체와 맵 오버레이 두 종류이며, **Layers** 패널의 **+ Add to map**에서 시작합니다.
- **Objects** 탭에서는 검색어, 객체 타입, 속성 필터로 객체를 찾아 추가하며, 기본 한도는 1000개입니다.
- **Search for objects that intersect a shape...** 로 도형을 그려 그 영역과 교차하는 객체만 검색할 수 있습니다.
- **Overlays** 탭에서는 Map Layer Editor로 만든 재사용 레이어를 추가합니다.
- **Search Around**는 맵 위 객체에서 링크를 따라 관련 객체를 추가합니다.
