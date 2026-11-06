# 로딩 방식 (Loading methods)

- 원문: https://www.palantir.com/docs/foundry/map/objects-loading-methods/
- 사이드바 위치: Applications > Map > Visualize Ontology data > Loading methods

이 페이지는 Map이 레이어의 객체를 브라우저로 불러오는 두 방식, 객체 기반 로딩(object-based loading)과 타일 기반 로딩(tile-based loading)의 차이와 설정 조건, 그리고 타일 기반 로딩에서 쓸 수 없는 기능을 설명합니다. 수십만 개 이상의 객체를 지도에 올려야 할 때 어떤 기능을 포기해야 하는지 판단하는 기준이 됩니다.

기본적으로 Map 애플리케이션은 레이어의 모든 객체를 불러와 지도에 그립니다. 이 방식에는 본질적으로 규모의 한계가 있습니다. 온톨로지에서 브라우저로 불러올 수 있는 만큼의 데이터만 그릴 수 있기 때문입니다. **Loading method** 설정은 지도의 보이는 범위를 표시하는 데 필요한 데이터만 불러오도록 애플리케이션을 제한해, 대규모 객체 집합(object set)을 표시할 수 있게 해 줍니다.

**설명**: 타일(tile)은 웹 지도에서 화면을 줌 레벨별로 일정한 크기의 사각형 조각으로 나눈 단위입니다. 타일 기반 로딩에서는 현재 화면에 걸친 타일들에 해당하는 데이터만, 그것도 단순화된 도형으로 서버에서 받아 옵니다. 예를 들어 객체 100만 개 중 화면에 보이는 영역에 있는 것만 받아 오므로 브라우저 메모리 한계를 피할 수 있습니다. 대신 개별 객체의 전체 속성이나 시계열을 가져오지 않기 때문에 아래에 나오는 여러 기능을 쓸 수 없습니다.

<a id="configure-loading-methods"></a>
## 로딩 방식 설정하기 (Configure loading methods)

스타일 패널의 **Loading method** 드롭다운 메뉴에서 디스플레이의 로딩 방식을 설정할 수 있습니다.

![스타일 메뉴의 로딩 방식 설정 옵션.](https://www.palantir.com/docs/resources/foundry/map/objects-loading-methods.png)

로딩 방식 옵션은 다음과 같습니다.

* **Auto**: 기본값입니다. 애플리케이션이 레이어의 내용을 보고 타일 기반 로딩과 객체 기반 로딩 중 최적의 방식을 추론합니다.
* **Tile**: 지도 뷰포트 범위 안의 단순화된 지오메트리 데이터를 불러옵니다. 큰 객체 집합과 성능을 우선하는 경우에 가장 적합합니다.
* **Object**: 개별 객체의 전체 세부 정보를 불러옵니다. 복잡한 스타일 설정에 가장 적합합니다.

다음 조건을 모두 만족할 때만 디스플레이의 로딩 방식을 선택할 수 있습니다.

* 레이어의 객체 타입에 [지오포인트 또는 지오셰이프 속성](https://www.palantir.com/docs/foundry/geospatial/ontology/)이 하나 이상 있어야 합니다.
* Ontology Manager에서 지오메트리 속성의 **Searchable** [렌더 힌트(render hint)](../../../02_define-ontologies/02_object-and-link-types/09_metadata/02_metadata-render-hints.md)가 켜져 있어야 합니다. **Searchable**이 켜져 있지 않으면 타일이 비어 있어 지도에 객체가 하나도 보이지 않습니다.
* 해당 디스플레이 타입이 타일 기반 렌더링을 지원해야 합니다. 현재는 아이콘, 원, 지오셰이프 기반 디스플레이만 지원됩니다.

**설명**: **Searchable** 렌더 힌트는 속성을 검색용 인덱스(index)에 넣도록 지정하는 설정입니다. 타일을 만들려면 "이 사각형 영역 안에 있는 객체"를 빠르게 찾는 공간 질의가 필요한데, 인덱싱(indexing)되지 않은 속성으로는 이런 질의를 할 수 없으므로 타일이 비게 됩니다.

<a id="add-objects-with-tile-based-loading-methods"></a>
## 타일 기반 로딩 방식으로 객체 추가하기 (Add objects with tile-based loading methods)

타일 기반 로딩 방식을 지원하는 객체 타입에서는 검색 대화 상자가 지도에 추가할 수 있는 객체 수를 제한하지 않습니다. 따라서 **Add all** 옵션이 항상 활성화됩니다.

<a id="tile-based-loading-method-compatibility"></a>
## 타일 기반 로딩 방식의 호환성 (Tile-based loading method compatibility)

타일 기반 디스플레이로 그려진 객체는 Map 애플리케이션의 여러 다른 기능과 함께 올바르게 동작하지 않습니다. 호환되지 않는 기능 중 다수는 타일 기반 레이어에서 그리는 데이터 규모를 감당할 수 없는 서비스에서 데이터를 불러와야 하는 기능입니다.

다음 섹션은 타일 기반 로딩 방식과 호환되지 않는 Map 기능을 나열합니다.

<a id="styling"></a>
### 스타일 (Styling)

[객체 레이어 디스플레이](01_visualize-objects.md#displays)의 지오메트리 소스로는 지오포인트와 지오셰이프 속성만 지원되며, 모든 [값 기반 스타일 옵션](01_visualize-objects.md#value-based-styling)에서는 속성 값만 지원됩니다.

따라서 다음 옵션은 지원되지 *않습니다*.

* 시계열 기반 스타일(측정값과 TSP)
* 함수(function)
* [시간 기반 불투명도](01_visualize-objects.md#opacity-styling)
* [레이블](01_visualize-objects.md#labels)
* [타임라인 지오메트리](06_visualize-timeline.md)
* [Search Around](../07_integrate-data-for-the-map/02_integrate-searcharounds.md)

**설명**: TSP는 시계열 속성(time series property)의 약자입니다. 이 목록의 기능들은 모두 객체마다 추가 계산이나 추가 조회(함수 실행, 시계열 조회, 링크 따라가기)가 필요하므로 객체 수가 매우 많은 타일 기반 레이어에서는 제공되지 않습니다.

<a id="filtering"></a>
### 필터링 (Filtering)

타일 기반 디스플레이에 표시된 객체는 [히스토그램](../04_interact-with-maps/09_histogram.md#filtering)이나 [타임라인](../05_time/03_timeline.md#filter-the-time-window)에서 적용한 필터를 따르지 않습니다.

<a id="shapes"></a>
### 도형 (Shapes)

[현재 선택 영역에서 도형을 만들 때](../04_interact-with-maps/08_shapes.md#from-selection) 타일 기반 디스플레이에 표시된 객체는 포함되지 않습니다.

## 정리

- 로딩 방식은 **Auto**(자동 선택), **Tile**(뷰포트 안의 단순화된 지오메트리만 로드, 대규모용), **Object**(개별 객체 전체 정보 로드, 복잡한 스타일용) 세 가지입니다.
- 로딩 방식을 고르려면 지오포인트나 지오셰이프 속성이 있고, 그 속성에 **Searchable** 렌더 힌트가 켜져 있고, 디스플레이가 아이콘, 원, 지오셰이프 기반이어야 합니다.
- 타일 기반 로딩에서는 추가할 객체 수 제한이 없지만, 시계열 및 함수 기반 스타일, 시간 기반 불투명도, 레이블, 타임라인 지오메트리, Search Around, 히스토그램과 타임라인 필터, 선택 영역 도형 만들기를 쓸 수 없습니다.
