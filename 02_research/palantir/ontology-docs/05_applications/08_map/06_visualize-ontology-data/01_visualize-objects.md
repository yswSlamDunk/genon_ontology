# 온톨로지 데이터 시각화 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/map/visualize-objects/
- 사이드바 위치: Applications > Map > Visualize Ontology data > Overview

이 페이지는 Map에서 온톨로지 객체 레이어의 모양을 정하는 스타일 체계 전체를 설명합니다. 레이어 안에 여러 "디스플레이(display)"를 두는 구조, 객체의 값에 따라 색과 크기를 바꾸는 값 기반 스타일, 시간에 따른 불투명도, 레이블, 줌 레벨별 표시, 범례 설정을 다룹니다. 이어지는 점, 선, 폴리곤, 트랙 페이지는 모두 이 페이지의 개념을 바탕으로 합니다.

지도의 핵심 기능은 온톨로지의 지리공간 데이터를 시각화하고 분석할 수 있게 하는 것입니다. [지도에 객체를 추가](../04_interact-with-maps/03_add-to-map.md)하고 나면, 객체의 여러 속성(property)을 표현하도록 스타일을 설정할 수 있습니다. 큰 틀에서 보면, 객체 레이어는 지도 위에서 객체를 나타내는 여러 디스플레이(예: 아이콘, 선, 폴리곤)를 포함합니다. 각 디스플레이는 색, 크기, 불투명도처럼 객체의 서로 다른 속성을 나타내도록 스타일을 지정할 수 있습니다.

**설명**: 구조를 정리하면 "레이어 1개 = 객체 집합(object set) 1개", "레이어 안의 디스플레이 여러 개 = 같은 객체들을 그리는 여러 방법"입니다. 예를 들어 `Airport` 레이어 하나에 아이콘 디스플레이(공항 위치)와 원 디스플레이(연간 승객 수에 비례한 크기)를 함께 둘 수 있습니다.

<a id="edit-layer-styling"></a>
## 레이어 스타일 편집하기 (Edit layer styling)

레이어의 스타일을 편집하려면 Layers 패널에서 레이어 항목을 선택합니다. 레이어 세부 정보 패널이 열리며, 여러 섹션이 탭으로 나뉘어 있습니다.

* **Style**: 개별 디스플레이의 모양을 설정하거나, 여러 디스플레이에 적용할 수 있는 기본 설정을 정의합니다.
* **Legend**: 이 레이어의 스타일 정보가 Legend(범례) 패널에 어떻게 표시될지 제어합니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/styling-edit-button.png" alt="스타일 편집 버튼." width="450" />

<img src="https://www.palantir.com/docs/resources/foundry/map/layer-details-panel.png" alt="Style 탭과 Legend 탭이 보이는 레이어 세부 정보 패널." width="450" />

<a id="layer-style"></a>
## 레이어 스타일 (Layer style)

**Style** 섹션에서는 레이어의 모든 [디스플레이](#displays)에 적용되는 **Shared Defaults**(공유 기본값)를 설정할 수 있습니다. 기본 색과 불투명도를 특정 [디스플레이](#displays)에 연결해 일관된 스타일을 공유할 수 있습니다. 색과 불투명도를 설정하는 방법은 [값 기반 스타일](#value-based-styling)과 [불투명도 스타일](#opacity-styling) 섹션을 참고하세요.

<a id="displays"></a>
## 디스플레이 (Displays)

객체 레이어는 많은 **디스플레이**를 포함할 수 있으며, 각 디스플레이는 레이어의 객체를 지도나 타임라인에 나타내는 서로 다른 방법입니다. 여러 디스플레이를 조합하면 여러 속성을 한 번에 나타내는 복잡한 시각화를 만들고, 확대할수록 더 자세한 보기를 제공할 수 있습니다. 사용할 수 있는 디스플레이 타입은 다음과 같습니다.

* [**아이콘과 원(Icons and circles)**:](02_visualize-points.md) 지오포인트 속성에 따라 배치됩니다.
* [**선과 폴리곤(Lines and polygons)**:](03_visualize-polygons-lines.md) 지오셰이프 속성 또는 여러 지오포인트 속성을 기반으로 합니다.
* [**트랙 선, 브레드크럼, 히트맵(Track lines, breadcrumbs, and heatmaps)**:](07_visualize-tracks.md) 시간에 따라 움직이는 객체를 시각화하는 데 도움이 됩니다.

**Style** 섹션 아래의 **Add display** 옵션으로 새 디스플레이를 추가할 수 있습니다.

![Add display 옵션.](https://www.palantir.com/docs/resources/foundry/map/styling-add-display.png)

디스플레이 추가 메뉴는 두 섹션으로 되어 있습니다.

* **Display presets**: 레이어의 객체 타입에 있는 속성 하나를 고르면, 그 속성을 사용하도록 설정된 디스플레이가 지도에 추가됩니다.
* **Available displays**: Map이 그릴 수 있는 모든 디스플레이 타입 중에서 고릅니다. 레이어의 객체 타입에 대해 완전히 설정할 수 있는 디스플레이만 활성화됩니다.

각 디스플레이에는 사용자 지정할 수 있는 속성(attribute)이 많으며, 자세한 내용은 각 디스플레이 페이지에서 다룹니다. 디스플레이의 속성 대부분은 다음 섹션에서 설명하는 값 기반 스타일 방식을 따릅니다.

> **중간 요약**: 레이어 세부 정보 패널의 **Style** 탭에서 공유 기본값과 여러 디스플레이(아이콘과 원, 선과 폴리곤, 트랙 계열)를 설정하고, **Add display**로 디스플레이를 추가합니다.

<a id="value-based-styling"></a>
## 값 기반 스타일 (Value-based styling)

**값 기반 스타일**을 사용하면, 객체에 연결된 값에 따라 그 객체를 그리는 디스플레이의 모양을 제어할 수 있습니다. 예를 들어 아이콘의 색으로 기상 관측소의 기온을 나타내거나, 원의 크기로 회사의 직원 수를 나타내도록 설정할 수 있습니다. 값 기반 스타일을 사용하는 가장 흔한 속성(attribute) 타입은 색과 숫자형 속성(예: 선 굵기, 아이콘 크기, 원 반지름 등)입니다.

핵심 아이디어는, 그려지는 각 객체에 대해 **값 소스(value source)를** 지정해 각 객체에서 스타일에 쓸 값을 정하고, 그다음 그 값을 스타일 속성(예: 색, 크기, 불투명도)으로 변환하는 방법을 지정하는 것입니다. 스타일을 지정할 수 있는 각 속성에서 보통 사용할 수 있는 값 소스는 다음과 같습니다.

* **Fixed**: 레이어의 모든 객체에 똑같이 적용될 스타일 값 하나를 직접 고릅니다.
* **Property**: 객체의 속성에 따라 각 객체의 스타일을 정합니다.
* **Function**: [함수(function)](../07_integrate-data-for-the-map/03_integrate-functions.md)가 계산한 값에 따라 각 객체의 스타일을 정합니다.
* **Measure**: [시계열 측정값(time series measure)](../07_integrate-data-for-the-map/01_integrate-objects.md#track-objects)에 따라 각 객체의 스타일을 정합니다.

사용할 값을 고른 뒤, 그 값을 스타일 값(색, 선 굵기, 원 반지름 등)으로 변환하는 설정은 스타일을 지정하는 속성의 타입에 따라 달라집니다.

**설명**: 값 기반 스타일은 "객체 하나를 입력받아 스타일 값을 출력하는 함수"를 두 단계로 나눠 정의하는 것입니다. 1단계(값 소스)는 `객체 -> 값`이고, 2단계(매핑)는 `값 -> 색 또는 숫자`입니다. 예를 들어 `WeatherStation` 객체 S1의 `temperature` 속성이 25이면 1단계 결과는 25이고, 2단계에서 "0은 파랑, 30은 빨강"인 그라디언트를 쓰면 25는 빨강에 가까운 색이 됩니다.

<a id="color-styling"></a>
## 색 스타일 (Color styling)

다음 섹션에서는 속성 타입별로 사용할 수 있는 색 스타일 옵션을 설명합니다.

<a id="fixed"></a>
### 고정 (Fixed)

고정 색 스타일을 사용할 때는 색 선택기(color picker)로 레이어의 모든 객체에 똑같이 적용될 색 하나를 고릅니다.

<a id="value-based"></a>
### 값 기반 (Value-based)

숫자 값을 가진 함수, 속성, 시계열로 색을 칠할 때는 그라디언트 편집기를 사용해 값을 출력 색에 매핑합니다. 그라디언트에 쓰이는 색은 그라디언트 막대 위의 지점을 선택해 편집할 수 있습니다. 색 그라디언트의 수치 범위(최솟값과 최댓값)는 자동으로 추론되지만, 이 기능을 꺼서 범위를 직접 지정할 수도 있습니다.

![그라디언트 스타일 패널.](https://www.palantir.com/docs/resources/foundry/map/styling-gradient-editor.png)

문자열 값을 가진 함수, 속성, 시계열로 색을 칠할 때는 **Color mapping** 드롭다운 메뉴에서 값을 색에 매핑하는 방법을 고릅니다.

* **Manual**: 값마다 사용할 색을 직접 지정합니다.
* **Automatic**: 특정 값을 설정할 필요 없이, 서로 다른 값을 구분하도록 색 구성표(color scheme)의 색을 자동으로 배정합니다.
* **None**: 각 값을 16진수(hex) 색으로 직접 적용하려고 시도합니다.

**설명**: **None**은 속성 값 자체가 `#FF0000` 같은 색 코드일 때 쓰는 옵션입니다. 예를 들어 `status_color` 속성에 `"#00AA00"`이 들어 있으면 그 객체는 그대로 초록색으로 그려집니다.

<a id="numeric-styling"></a>
## 숫자 스타일 (Numeric styling)

다음 섹션에서는 속성 타입별로 사용할 수 있는 숫자 스타일 옵션을 설명합니다.

<a id="fixed"></a>
### 고정 (Fixed)

고정 숫자 스타일을 사용할 때는 슬라이더를 쓰거나 입력란에 정확한 숫자를 입력해 숫자 값을 지정합니다.

![고정 숫자 스타일.](https://www.palantir.com/docs/resources/foundry/map/styling-numeric-fixed.png)

<a id="value-based"></a>
### 값 기반 (Value-based)

숫자형 속성(attribute, 예: 선 굵기나 아이콘 크기)에 스타일을 지정할 때는 숫자 값을 가진 속성(property)만 값 소스로 사용할 수 있습니다. **Numeric mapping** 옵션을 선택해, 선택한 값 소스에서 스타일 속성으로의 매핑을 설정합니다.

* **Scaled**: 객체의 값을 스타일에 사용할 숫자로 변환하는 선형 척도(linear scale)를 정의합니다. <br><br>
  ![척도를 적용한 숫자 스타일.](https://www.palantir.com/docs/resources/foundry/map/styling-numeric-mapping.png) <br><br>

  * 위쪽 행은 스타일 속성의 최솟값과 최댓값을 정하고, 아래쪽 행은 그 최솟값과 최댓값에 대응할 값의 범위를 정합니다.
  * 이 예시에서 선 굵기는 "Departing Flights" 속성 값이 `20`인 객체에서 `1`픽셀, 속성 값이 `500`일 때 `10`픽셀이 됩니다.
* **None**: 속성 값을 아무런 척도 변환 없이 그대로 스타일 속성으로 사용합니다.

**설명**: 선형 척도는 일차 함수입니다. 위 예시에서 입력 범위 [20, 500]을 출력 범위 [1, 10]으로 옮기므로 `width = 1 + (value - 20) × (10 - 1) / (500 - 20)`입니다. 속성 값이 260이면 굵기는 1 + 240 × 9 / 480 = 5.5픽셀입니다.

> **중간 요약**: 값 기반 스타일은 값 소스(Fixed, Property, Function, Measure)로 값을 정한 뒤 색은 그라디언트나 값별 매핑으로, 숫자는 선형 척도(**Scaled**)나 그대로 사용(**None**)으로 변환합니다.

<a id="opacity-styling"></a>
## 불투명도 스타일 (Opacity styling)

**Opacity** 섹션에서는 레이어 객체의 투명도를 제어합니다.

**Value from** 드롭다운과 **By time** 불투명도 옵션은 [트랙](../07_integrate-data-for-the-map/01_integrate-objects.md#track-objects)이나 [이벤트 데이터](../07_integrate-data-for-the-map/01_integrate-objects.md#event-objects)를 가진 객체에 스타일을 지정할 때만 나타납니다. 그 밖의 경우 불투명도 섹션에는 고정 불투명도 옵션만 표시됩니다.

**Value from** 드롭다운 메뉴에는 불투명도를 지정하는 여러 방법이 있습니다.

* **Fixed**: 레이어의 모든 객체에 똑같이 적용될 불투명도 하나를 고릅니다.
* **By time**: [트랙](../07_integrate-data-for-the-map/01_integrate-objects.md#track-objects)이나 [이벤트](../07_integrate-data-for-the-map/01_integrate-objects.md#event-objects)인 객체를 그릴 때, 전역 [시간 선택](../05_time/01_time-overview.md#selected-time-and-time-range)에 따라 불투명도를 제어합니다. <br><br>
  ![시간 기반 불투명도 옵션](https://www.palantir.com/docs/resources/foundry/map/styling-opacity-time.png) <br><br>

  * **Active opacity**: 객체나 지점이 활성으로 간주될 때의 불투명도를 정합니다.
  * **Inactive opacity**: 객체나 지점이 활성으로 간주되지 않을 때의 불투명도를 정합니다.
  * **Active time buffer**: 이벤트나 트랙 지점의 타임스탬프가 현재 시간 커서에 시간상 얼마나 가까워야 활성으로 간주될지 정합니다.
  * **Fade duration**: 객체가 비활성이 된 뒤 활성 불투명도에서 비활성 불투명도로 서서히 바뀌는 데 걸리는 기간을 정합니다.
  * **Hide until occurred**: 켜면, 시간 커서가 이벤트의 시작 시각 또는 트랙 지점의 타임스탬프를 지나기 전까지 객체를 완전히 숨깁니다.

**설명**: 예를 들어 **Active time buffer**가 5분, **Fade duration**이 30분이라고 합시다. 타임스탬프가 10:00인 트랙 지점은 커서가 9:55\~10:05에 있을 때 활성(**Active opacity**)으로 그려지고, 10:05 이후 30분에 걸쳐 점점 흐려져 10:35부터는 **Inactive opacity**로 그려집니다. **Hide until occurred**를 켜면 커서가 10:00에 이르기 전에는 이 지점이 보이지 않습니다.

<a id="labels"></a>
### 레이블 (Labels)

지도에 중요한 정보를 텍스트로 보여 주는 사용자 지정 레이블을 정의할 수 있습니다. 다음 속성(attribute)으로 각 디스플레이에서 레이블이 나타나는 방식을 제어합니다.

* **Visibility**: 지도에서 레이블이 언제 보일지 설정합니다.
  * **Always visible**: 상위 디스플레이가 나타내는 모든 객체에 레이블을 보여 줍니다.
  * **Only on hover**: 사용자가 하나 이상의 객체 위에 마우스를 올렸을 때 커서 팝업으로 레이블을 보여 줍니다.
  * **Hidden**: 레이블 정보를 보여 주지 않습니다.
* **Style**: 항상 보이는 레이블의 경우 다음 옵션으로 레이블 내용의 모양을 제어합니다.
  * **Card**: 높은 대비와 가독성을 위해 단색 배경 위에 레이블을 보여 줍니다.
  * **Minimal**: 더 깔끔하고 덜 거슬리도록 레이블 내용을 텍스트로만 보여 줍니다.
* **Enable Header**: 레이블의 첫 번째 행 항목을 굵은 글씨와 더 불투명한 배경으로 표시해 핵심 정보가 바로 눈에 띄게 합니다.
* **Show Missing Data**: 값이 null이거나 비어 있는 행 항목도 레이블에 포함합니다.

![레이블 예시.](https://www.palantir.com/docs/resources/foundry/map/styling-labels.png)

**주의**: [타일 기반 로딩 방식](08_objects-loading-methods.md)을 사용하는 레이어에서는 레이블과 추가 툴팁 내용이 지원되지 않습니다. 레이블이나 사용자 지정 툴팁 내용이 필요하면 "Object" 로딩 방식을 사용하고 있는지 확인하세요.

<a id="label-content-for-object-layers"></a>
#### 객체 레이어의 레이블 내용 (Label content for object layers)

객체 기반 레이어에서 레이블에는 다음 항목을 넣을 수 있습니다.

* 속성([시계열 속성](../07_integrate-data-for-the-map/01_integrate-objects.md#track-objects) 포함)
* [함수](../07_integrate-data-for-the-map/03_integrate-functions.md)
* [시리즈](https://www.palantir.com/docs/foundry/time-series/time-series-overview/)
* 링크된 객체 개수

![공항 객체의 레이블 내용 예시.](https://www.palantir.com/docs/resources/foundry/map/styling-labels-content.png)

추가한 뒤에는 개별 레이블 행에서 다음 작업도 할 수 있습니다.

* 드래그해서 순서 바꾸기
* 표시 이름 편집하기
* 행 제목 보이기/숨기기

아래 그림처럼, 선택 패널에서 속성이나 시리즈 위에 마우스를 올리면 나타나는 **…** 메뉴로도 속성이나 시리즈를 추가할 수 있습니다.

![고정 속성 추가하기.](https://www.palantir.com/docs/resources/foundry/map/styling-add-to-label.png)

> **중간 요약**: 트랙과 이벤트 객체는 시간 커서와의 거리에 따라 활성과 비활성 불투명도를 바꿀 수 있습니다. 레이블은 표시 시점, 모양, 내용(속성, 함수, 시리즈, 링크된 객체 개수)을 설정하며, 타일 기반 로딩에서는 지원되지 않습니다.

<a id="display-visibility-by-zoom-level"></a>
## 줌 레벨별 디스플레이 표시 (Display visibility by zoom level)

**Zoom levels** 섹션에서는 레이어 객체가 보이는 범위를 제어합니다. 꺾쇠(caret) 기호가 현재 줌 레벨을 나타냅니다.

뷰포트가 활성 범위 안의 줌 레벨에 있으면 해당 디스플레이가 지도에 그려집니다. 범위를 벗어나면 해당 디스플레이는 숨겨집니다.

줌 레벨 설정은 [보이도록](../04_interact-with-maps/04_layer-management.md#toggle-layer-visibility) 켜져 있는 레이어에만 적용됩니다.

![줌 레벨.](https://www.palantir.com/docs/resources/foundry/map/zoom-levels.png)

**설명**: 웹 지도의 줌 레벨은 보통 0(전 세계가 한 화면)에서 시작해 숫자가 커질수록 확대됩니다. 예를 들어 레이블 디스플레이의 활성 범위를 12 이상으로 두면, 전국 단위로 볼 때는 아이콘만 보이고 도시 단위로 확대했을 때만 레이블이 나타납니다.

<a id="legend"></a>
## 범례 (Legend)

**Layers** 세부 정보 패널에서 **Legend** 탭을 사용해 레이어가 어떻게 표시될지 미리 보고 제어합니다. 레이어의 디스플레이에서 나온 스타일 정보는 기본적으로 이 탭에 포함됩니다. 제목 스위치는 이 레이어와 관련 디스플레이가 **Legend** 패널에 나타날지를 결정합니다. 행 단위 체크박스를 켜고 끄면 개별 항목을 숨기거나 보여 줄 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/styling-legend-config.png" alt="옵션이 있는 범례 설정." width="450" />

## 정리

- 객체 레이어는 여러 디스플레이(아이콘과 원, 선과 폴리곤, 트랙 계열)로 구성되고, 레이어 세부 정보 패널의 **Style**과 **Legend** 탭에서 설정합니다.
- 값 기반 스타일은 값 소스(Fixed, Property, Function, Measure)와 변환 방식(색 그라디언트나 값별 매핑, 숫자 선형 척도)을 조합합니다.
- 트랙과 이벤트 객체는 시간 선택에 따라 불투명도를 바꿀 수 있습니다(활성 버퍼, 페이드 기간, 발생 전 숨김).
- 레이블, 줌 레벨별 표시 범위, 범례 표시를 디스플레이와 레이어 단위로 설정할 수 있으며, 레이블은 Object 로딩 방식에서만 지원됩니다.
