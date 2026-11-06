# Map Layer Editor (Map Layer Editor)

- 원문: https://www.palantir.com/docs/foundry/map/layer-editor/
- 사이드바 위치: Applications > Map > Integrate data for the map > Map Layer Editor

이 페이지는 지도에 겹쳐 그릴 레이어(layer)를 만들고 편집하는 Map Layer Editor 애플리케이션을 소개합니다. 레이어의 데이터 출처에 따라 벡터, 래스터, 객체, Mapbox JSON 네 종류가 있으며, 각각 어떤 데이터를 넣을 수 있고 어떤 표시 옵션이 있는지 설명합니다. 이렇게 만든 레이어는 Map 애플리케이션과 Workshop Map 위젯에서 재사용됩니다.

Map Layer Editor 애플리케이션으로 지도 레이어를 생성, 편집, 미리 보기할 수 있습니다. 지도 레이어는 지리공간 데이터를 담고 있으며, 그 데이터를 어떻게 시각화할지 정의합니다. 지도 레이어는 [Map 애플리케이션](../04_interact-with-maps/03_add-to-map.md#add-map-overlays)과 [Workshop Map 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-map/#layers)에서 사용할 수 있습니다.

Map Layer Editor는 벡터 또는 래스터 데이터를 담은 지도 레이어를 클릭만으로 설정할 수 있는 UI를 제공합니다. 더 세밀하게 제어하거나 더 고급 지도 기능을 쓰고 싶다면, 대신 [Mapbox GL JS Style Specification 문서 ↗](https://docs.mapbox.com/mapbox-gl-js/style-spec/)를 직접 작성할 수도 있습니다.

**설명**: 벡터 데이터는 점, 선, 다각형을 좌표로 저장한 데이터(예: 도로 선, 행정구역 경계)이고, 래스터 데이터는 픽셀 격자로 된 이미지 데이터(예: 위성 사진, 기상 레이더 영상)입니다. Mapbox GL JS는 웹 지도 렌더링 라이브러리이며, Style Specification은 데이터 출처와 그리는 방식을 JSON으로 기술하는 규격입니다.

<a id="create-a-new-map-layer"></a>
## 새 지도 레이어 만들기 (Create a new map layer)

Foundry에서 지도 레이어를 만들 폴더로 이동한 다음, **New** 메뉴에서 **Map Layer**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/new-map-layer-button.png" alt="새 지도 레이어 버튼" width="219" />

그런 다음 데이터 소스를 추가하거나 Mapbox JSON 문서를 작성하는 쪽을 선택해 레이어 설정을 시작합니다.

![레이어 유형 선택](https://www.palantir.com/docs/resources/foundry/map/map-layer-editor-select-type.png)

**팁**: Mapbox JSON 문서는 벡터 레이어나 래스터 레이어가 지원하지 않는 기능이 필요할 때만 사용하기를 권장합니다.

오른쪽의 **Layer Preview** 패널에서 지도 레이어를 실시간으로 미리 볼 수 있습니다.

지도 레이어를 만들거나 수정한 뒤에는 항상 **Save**를 클릭해야 Map 애플리케이션에서 그 레이어를 사용할 수 있습니다.

> **중간 요약**: 폴더의 **New** 메뉴에서 **Map Layer**를 만들고 데이터 소스나 Mapbox JSON을 선택해 설정하며, 저장해야 Map에서 쓸 수 있습니다.

<a id="vector-layers"></a>
## 벡터 레이어 (Vector layers)

벡터 레이어는 GeoJSON 또는 벡터 타일(vector tile) 소스의 도형(geometry) 데이터를 표시합니다. 데이터 소스를 지정하는 방법은 네 가지입니다.

* **GeoJSON File:** [수동으로 업로드한](https://www.palantir.com/docs/foundry/compass/manually-upload-data/) GeoJSON 파일을 선택합니다.
* **Dataset GeoJSON File:** 데이터셋을 선택한 다음, 그 데이터셋에 들어 있는 GeoJSON 파일을 고릅니다.
* **GeoJSON URL:** GeoJSON 파일의 URL을 입력합니다.
* **MVT URL:** 벡터 타일셋(vector tileset)의 URL을 입력합니다.

소스를 추가한 뒤에는 하나 이상의 디스플레이(display)를 추가해 데이터가 지도에 어떻게 시각화될지 설정할 수 있습니다.

![벡터 레이어](https://www.palantir.com/docs/resources/foundry/map/map-layer-editor-vector.png)

**설명**: MVT(Mapbox Vector Tile)는 지도를 확대 수준별로 작은 사각형 타일로 잘라 필요한 부분만 내려받게 하는 벡터 데이터 형식입니다. 전 세계 도로처럼 큰 데이터를 GeoJSON 파일 하나로 통째로 내려받으면 느리기 때문에 타일 방식이 쓰입니다.

<a id="raster-layers"></a>
## 래스터 레이어 (Raster layers)

래스터 레이어는 래스터 타일셋의 비트맵 데이터를 표시합니다. 타일셋의 URL을 지정해 래스터 데이터 소스를 설정합니다.

![래스터 레이어](https://www.palantir.com/docs/resources/foundry/map/map-layer-editor-raster.png)

래스터 레이어에서 사용할 수 있는 표시 옵션은 다음과 같습니다.

* **Opacity:** 레이어를 얼마나 불투명하게 또는 투명하게 표시할지 정합니다.
* **Sampling:** 지도를 확대해 래스터 이미지를 키워야 할 때 사용할 보간(interpolation) 방법입니다.
  * **Linear:** 가장 가까운 원본 픽셀들의 평균으로 값을 보간합니다. 과도하게 확대하면 흐릿하게 보일 수 있습니다.
  * **Nearest:** 가장 가까운 원본 픽셀 하나를 골라 보간합니다. 과도하게 확대하면 선명하지만 픽셀이 도드라져 보입니다.
* **Zoom levels:** 레이어를 표시할 최대 및 최소 확대 수준입니다.

**설명**: 10x10 픽셀 이미지를 100x100으로 키운다고 하면, 새 픽셀 각각의 색을 원본 픽셀로부터 정해야 합니다. Nearest는 가장 가까운 원본 픽셀 색을 그대로 복사하므로 계단 모양 경계가 생기고, Linear는 주변 원본 픽셀 색을 거리에 따라 섞으므로 경계가 부드럽지만 흐려집니다.

> **중간 요약**: 벡터 레이어는 GeoJSON 파일, 데이터셋 안의 GeoJSON, GeoJSON URL, MVT URL을 소스로 쓰고 디스플레이로 모양을 정합니다. 래스터 레이어는 타일셋 URL을 소스로 하며 투명도, 샘플링 방식, 확대 수준을 설정합니다.

<a id="object-layers"></a>
## 객체 레이어 (Object layers)

객체 레이어는 온톨로지의 데이터를 직접 표시합니다. OSS 또는 OQL(지원 중단)에 동기화되어 있고 geopoint 또는 geoshape 속성(property) 타입을 가진 객체 타입만 객체 레이어로 표시할 수 있습니다.

![객체 레이어](https://www.palantir.com/docs/resources/foundry/map/map-layer-editor-objects.png)

**참고**: 객체 레이어에는 OSS 또는 OQL(지원 중단)이 필요하지만, 모든 인스턴스에서 사용할 수 있는 것은 아닙니다. 자세한 내용은 Palantir 담당자에게 문의하세요.

**설명**: OSS와 OQL은 객체 데이터를 검색하고 조회하기 위해 객체를 동기화(인덱싱)해 두는 Foundry의 백엔드 서비스 이름입니다. 원문은 그 이상 자세히 설명하지 않으므로, 여기서는 "객체 타입이 해당 서비스에 동기화되어 있어야 지도에 레이어로 그릴 수 있다"는 조건으로 이해하면 됩니다.

객체 레이어에서 렌더링할 데이터를 지정하는 방법은 두 가지입니다.

* **Object type:** 객체 타입을 선택하고 필요하면 필터를 정의합니다. 조건에 맞는 모든 객체가 지도 레이어에 표시됩니다.
* **Saved object set:** [Object Explorer에서 저장한 탐색(exploration)](../../01_object-explorer/04_analyze-and-compare/06_save-explorations.md)을 선택합니다. 레이어 앱은 저장된 탐색에 들어 있는 모든 객체를 표시합니다.

객체 레이어의 디스플레이 설정 옵션은 벡터 레이어와 같습니다.

<a id="mapbox-json-layers"></a>
## Mapbox JSON 레이어 (Mapbox JSON layers)

Mapbox JSON 레이어는 Map Layer Editor에서 JSON 문서를 직접 편집할 수 있습니다. 편집기는 JSON을 검증하고 오류를 강조 표시합니다.

JSON 내용은 [Mapbox GL JS Style Specification ↗](https://docs.mapbox.com/mapbox-gl-js/style-spec/)을 따라야 하지만, `sources`와 `layers` 속성만 지원됩니다(그리고 둘 다 필수입니다).

![JSON 레이어](https://www.palantir.com/docs/resources/foundry/map/map-layer-editor-json.png)

**설명**: `sources`는 데이터를 어디서 가져올지(예: 어떤 GeoJSON URL), `layers`는 그 데이터를 어떻게 그릴지(예: 선 색과 두께, 채우기 색)를 정의하는 부분입니다. Mapbox 스타일 규격에는 이 밖에도 배경 지도, 글꼴 등 여러 최상위 속성이 있지만 Map Layer Editor에서는 이 둘만 사용할 수 있습니다.

> **중간 요약**: 객체 레이어는 OSS/OQL에 동기화되고 geopoint 또는 geoshape 속성을 가진 객체 타입을 필터나 저장된 탐색으로 골라 표시합니다. Mapbox JSON 레이어는 `sources`와 `layers`만 포함한 스타일 JSON을 직접 작성합니다.

## 정리

- Map Layer Editor는 지리공간 데이터와 그 시각화 방식을 담은 지도 레이어를 만들고 미리 보는 도구이며, 결과는 Map 애플리케이션과 Workshop Map 위젯에서 씁니다.
- 레이어 종류는 벡터(GeoJSON, MVT), 래스터(타일셋 URL), 객체(온톨로지 객체 타입 또는 저장된 객체 집합), Mapbox JSON 네 가지입니다.
- Mapbox JSON은 다른 레이어로 안 되는 기능이 필요할 때만 쓰기를 권장하며, `sources`와 `layers`만 지원합니다.
- 만들거나 수정한 레이어는 반드시 **Save**해야 Map에서 사용할 수 있습니다.
