# Workshop 모듈에 Vulcan 임베드하기 (Embed Vulcan in a Workshop module)

- 원문: https://www.palantir.com/docs/foundry/vulcan/widget/
- 사이드바 위치: Applications > Vulcan > Embed Vulcan in a Workshop module

이 페이지는 3D CAD 모델 뷰어인 Vulcan을 Workshop 모듈 안에 위젯으로 넣는 방법과 위젯의 설정 항목 전체를 설명합니다. 어떤 온톨로지 객체가 CAD 객체가 될 수 있는지, 함수 출력으로 부품 위치와 색을 바꾸는 반환 스키마는 어떤 형식인지, 그리고 카메라, 도구, 액션, 출력 변수를 Workshop 변수와 어떻게 연결하는지 다룹니다.

**Vulcan** 위젯을 사용하면 Workshop 모듈에 Vulcan을 임베드할 수 있습니다. 이 위젯은 독립 실행형 애플리케이션과 같은 3D 뷰포트와 도구를 제공합니다. 위젯의 입력, 출력, 인터페이스는 Workshop 변수에도 연결할 수 있으므로 Vulcan이 모듈 안의 다른 위젯과 상호작용할 수 있습니다.

Workshop 모듈에 Vulcan을 임베드하는 과정은 위젯 추가, CAD 객체 선택, 위젯 설정의 세 단계입니다.

<a id="add-a-vulcan-widget-in-workshop"></a>
## Workshop에 Vulcan 위젯 추가하기 (Add a Vulcan widget in Workshop)

Vulcan을 표시하려는 Workshop 섹션에서 **+** 아이콘이나 **+ Add widget**을 선택해 위젯 메뉴를 연 다음, **Vulcan** 위젯을 검색해 선택합니다.

<a id="choose-a-cad-object"></a>
## CAD 객체 선택하기 (Choose a CAD object)

Vulcan이 화면을 그리려면 CAD 객체가 최소 하나 필요합니다. CAD 객체는 `cad_media_reference` 타입 클래스가 붙은 속성(property)을 가진 온톨로지 객체입니다. 전체 스키마는 [CAD 객체](03_schema-reference.md#cad-object)를 참고하세요.

**Input > Models** 아래에서 모델을 추가하고, **Model objects**를 CAD 객체가 들어 있는 Workshop 객체 집합(object set)으로 설정합니다. Vulcan은 집합의 첫 번째 객체를 불러옵니다. 여러 모델을 그리려면 객체 집합마다 별도의 모델 항목을 추가합니다.

**설명**: CAD(Computer-Aided Design)는 기계 부품이나 조립품을 3차원으로 설계한 데이터입니다. 여기서 CAD 객체란 그 3D 파일을 가리키는 미디어 참조를 속성 값으로 가진 온톨로지 객체입니다. 타입 클래스 `cad_media_reference`는 "이 속성 값은 CAD 파일 참조"라는 표시이므로, Vulcan은 이 표시를 보고 어느 속성을 읽어 모델을 불러올지 압니다.

> **중간 요약**: Vulcan 위젯을 추가하고, `cad_media_reference` 타입 클래스 속성을 가진 CAD 객체가 든 객체 집합을 Input > Models에 지정합니다. 집합에서 첫 객체만 불러오므로 모델이 여러 개면 항목을 여러 개 만듭니다.

<a id="configure-the-widget"></a>
## 위젯 설정하기 (Configure the widget)

Vulcan 위젯 설정은 다음 섹션들로 구성됩니다.

<a id="input"></a>
### 입력 (Input)

**Input** 섹션은 위젯이 사용하는 온톨로지 데이터와 시나리오를 제어합니다.

* **Models:** CAD 모델 입력의 반복 가능한 목록입니다.
  * **Model objects:** 모델이 들어 있는 객체 집합입니다.
  * **Options:** 이 모델에만 적용되는 설정입니다. **Transforms**와 **Part coloring**은 아래 반환 스키마에서 설명하는 함수 출력을 받습니다.
    * **Annotation objects:** 모델과 연결된 주석(annotation)의 객체 집합입니다. 각 객체는 [주석 스키마](03_schema-reference.md#annotation)를 따라야 합니다.
    * **Transforms:** 부품 인스턴스나 조립품에 대한 변환(transform) 덮어쓰기입니다. [Transforms 반환 스키마](#transforms-return-schema)를 참고하세요.
    * **Selected part ID** 및 **Selected part instance ID:** 현재 선택 상태를 위한 양방향 문자열 변수입니다. 부품 ID는 이 모델에 있는 그 부품의 모든 인스턴스를 선택하고, 부품 인스턴스 ID는 특정 인스턴스 하나를 선택합니다.
    * **Part coloring:** 색상과 불투명도 덮어쓰기입니다. [Part coloring 반환 스키마](#part-coloring-return-schema)를 참고하세요.
    * **Fallback color:** 이 모델에서 색이 지정되지 않은 부품에 쓸 CSS 색상 값입니다. 이 값은 해당 모델에 대해 전역 **Fallback color**보다 우선합니다.
* **Measurement objects** 및 **Section plane objects:** 표시할 측정값과 적용할 단면(section plane)이 들어 있는 객체 집합입니다. 객체는 각각 [측정](03_schema-reference.md#measurement) 또는 [단면](03_schema-reference.md#section-plane) 스키마를 따라야 합니다.
* **Scenario:** 온톨로지 객체를 불러올 때 사용할 Workshop 기본(primary) 시나리오입니다.

**설명**: 부품(part)과 부품 인스턴스(part instance)의 차이는 클래스와 인스턴스의 차이와 같습니다. 예를 들어 "M6 볼트"라는 부품 하나가 조립품 안에 8곳에 쓰이면 부품 ID는 1개, 부품 인스턴스 ID는 8개입니다. 부품 ID로 선택하면 볼트 8개가 모두 선택되고, 인스턴스 ID로 선택하면 그중 하나만 선택됩니다.

<a id="transforms-return-schema"></a>
#### Transforms 반환 스키마 (Transforms return schema)

**Transforms**는 다음 필드를 가진 구조체(struct)의 목록을 받습니다.

| 필드 | 필수 | 타입 | 설명 |
| ----------- | -------- | ---------------- | ----------------------------------------------------------------------------------------- |
| `id` | 예 | String | 변환할 부품 인스턴스 또는 조립품 ID입니다. |
| `transform` | 예 | Array of numbers | 열 우선(column-major) 순서의 4×4 변환 행렬을 나타내는 정확히 16개의 유한한 숫자입니다. |

행렬 값은 `[m11, m21, m31, m41, m12, m22, m32, m42, m13, m23, m33, m43, m14, m24, m34, m44]` 순서를 따라야 합니다. Vulcan은 ID가 없거나 행렬이 유효하지 않은 항목을 무시합니다.

**설명**: 4×4 변환 행렬은 3D 그래픽스에서 회전, 크기 조정, 이동을 한 행렬로 표현하는 표준 방식입니다. "열 우선"은 행렬을 1차원 배열로 펼칠 때 첫 번째 열(m11, m21, m31, m41)부터 차례로 적는다는 뜻입니다. 예를 들어 회전 없이 x축으로 10만큼 옮기는 행렬은 `[1,0,0,0, 0,1,0,0, 0,0,1,0, 10,0,0,1]`이며, 이동량은 마지막 열(m14, m24, m34)에 들어갑니다.

<a id="part-coloring-return-schema"></a>
#### Part coloring 반환 스키마 (Part coloring return schema)

**Part coloring**은 다음 필드를 가진 구조체의 목록을 받습니다.

| 필드 | 필수 | 타입 | 설명 |
| ----------------- | -------- | ---------------- | ----------------------------------------------------------------------- |
| `partInstanceIds` | 예 | Array of strings | 스타일을 적용할 하나 이상의 부품 인스턴스 또는 조립품 ID입니다. |
| `color` | 아니요 | String | `#0055ff`나 `rgb(0, 85, 255)` 같은 CSS 색상 값입니다. |
| `opacity` | 아니요 | Number | 기본 불투명도이며, `0`(투명)부터 `1`(불투명)까지입니다. |
| `selectedOpacity` | 아니요 | Number | 선택되거나 강조되었을 때의 불투명도이며, 같은 `0`\~`1` 척도를 씁니다. |

모델에 영향을 주려면 각 구조체가 `color`, `opacity`, `selectedOpacity` 중 하나 이상을 정의해야 합니다. Scene Coloring 도구도 색을 지정하는 경우, 색상은 장면 색칠(scene coloring) 값이 우선하고 설정된 불투명도 값은 그대로 적용됩니다.

**설명**: 예를 들어 함수가 `[{partInstanceIds: ["bolt-3", "bolt-4"], color: "#ff0000"}, {partInstanceIds: ["cover-1"], opacity: 0.2}]`를 반환하면, 볼트 두 개는 빨간색이 되고 덮개는 거의 투명해져 안쪽 부품이 보이게 됩니다. 결함이 보고된 부품만 빨갛게 칠하는 식으로 온톨로지 데이터와 3D 화면을 연결할 수 있습니다.

> **중간 요약**: Input에서는 모델별 객체 집합, 주석, 변환, 선택 상태, 색상, 대체 색상, 그리고 측정과 단면 객체, 시나리오를 지정합니다. Transforms는 ID와 열 우선 4×4 행렬 16개 숫자를, Part coloring은 인스턴스 ID 목록과 색상/불투명도를 담은 구조체 목록을 받습니다.

<a id="interaction"></a>
### 상호작용 (Interaction)

카메라 대상(target), 위치, 확대/축소 바인딩은 양방향으로 동작합니다. **Interaction** 섹션은 다음 카메라 및 장면 상호작용 상태를 Workshop 변수에 연결합니다.

* **Camera target X / Y / Z:** 카메라가 바라보는 점입니다. 세 좌표를 모두 설정합니다.
* **Camera position X / Y / Z:** 카메라의 위치입니다. 세 좌표를 모두 설정합니다.
* **Camera zoom:** 카메라 확대/축소 수준입니다.
* **Click X / Y / Z:** 사용자가 가장 최근에 선택한 모델 부품 위의 점의 3D 좌표를 담는 출력 숫자 변수입니다. 선택한 점을 재구성하려면 세 변수를 모두 바인딩합니다.

**설명**: 양방향 바인딩이란 Workshop 변수 값을 바꾸면 카메라가 움직이고, 사용자가 마우스로 카메라를 움직이면 변수 값도 바뀐다는 뜻입니다. 따라서 다른 위젯의 버튼으로 "정면 보기" 좌표를 변수에 넣어 카메라를 이동시키는 식의 구성이 가능합니다.

<a id="styling"></a>
### 스타일 (Styling)

색상 필드는 CSS 색상 값을 받습니다. **Styling** 섹션은 다음 설정으로 기본 장면 모양을 제어합니다.

* **Fallback color:** 색이 지정되지 않은 부품의 색입니다. 모델별 대체 색상이 있으면 그 모델에는 그것이 우선합니다.
* **Background color:** 3D 뷰포트의 배경색입니다.

<a id="interface"></a>
### 인터페이스 (Interface)

모든 옵션은 기본으로 켜져 있습니다. **Interface** 섹션은 어떤 인터페이스 요소를 사용할 수 있는지 제어합니다.

* **Show sidebar**, **Show toolbar**, **Show gizmo:** 장면 트리 사이드바, 상단 도구 모음, 방향 기즈모(gizmo)의 표시 여부를 제어합니다.
* **Enable context menu:** 사용자가 부품에서 컨텍스트 메뉴를 열 수 있게 합니다.
* **Expand sidebar by default:** 위젯이 처음 로드될 때 사이드바를 엽니다.

<a id="scene"></a>
### 장면 (Scene)

기본적으로 Vulcan은 Complete 모드, Orthographic 카메라, Orbit 컨트롤을 사용합니다. 모드 전환과 부품 정보는 켜져 있고, 자동 회전은 꺼져 있습니다. **Scene** 섹션은 다음 설정으로 Vulcan이 모델을 표시하고 탐색하는 방식을 제어합니다.

* **Default mode:** 초기 장면 모드입니다.
  * **Complete:** 조립된 모델과 전체 장면 트리를 표시합니다.
  * **Grid:** 고유 부품들의 정렬 가능한 격자를 표시합니다.
  * **Component:** 선택한 구성 요소에 집중합니다.
* **Enable switching modes:** 장면 모드를 바꾸는 컨트롤을 표시합니다.
* **Camera mode:** **Orthographic**(직교) 또는 **Perspective**(원근) 카메라를 사용합니다.
* **Controls mode:** **Orbit** 또는 **Trackball** 카메라 컨트롤을 사용합니다.
* **Enable scene auto-rotate:** 장면을 자동으로 회전시킵니다.
* **Complete mode config > Enable part info on select:** Complete 모드에서 사용자가 부품을 선택하면 부품 정보를 표시합니다.

**설명**: 직교(orthographic) 카메라는 멀리 있는 물체도 같은 크기로 그려 치수를 비교하기 좋고, 원근(perspective) 카메라는 멀수록 작게 그려 사람 눈에 보이는 모습에 가깝습니다. 설계 도면 검토에는 보통 직교 투영이 쓰입니다.

> **중간 요약**: Interaction은 카메라 상태와 클릭 좌표를 Workshop 변수에 연결하고, Styling은 대체 색상과 배경색을, Interface는 사이드바, 도구 모음, 기즈모, 컨텍스트 메뉴 표시를, Scene은 초기 모드(Complete, Grid, Component), 카메라 종류, 컨트롤 방식, 자동 회전을 정합니다.

<a id="tools"></a>
### 도구 (Tools)

**Tools** 섹션에서는 모듈에 필요 없는 기능을 숨길 수 있습니다. 모든 설정은 기본으로 켜져 있습니다. 설정을 끄면 임베드된 위젯에서 해당 도구의 컨트롤이 제거됩니다. 각 도구는 [Tools](02_tool-overview.md) 페이지에서 자세히 설명합니다.

| 설정 | 기능 |
| ------------------------------ | ---------------------------------------------- |
| **Enable annotation tool** | 모델 부품에 주석을 만듭니다. |
| **Enable mesh styling tool** | 개별 메시의 모양을 제어합니다. |
| **Enable measurement tool** | 모델 위 점들 사이의 거리를 측정합니다. |
| **Enable section view tool** | 단면을 사용해 모델의 단면도를 봅니다. |
| **Enable transform tool** | 부품과 조립품의 위치를 바꿉니다. |
| **Enable scene coloring tool** | 속성이나 함수 기반으로 부품을 색칠합니다. |

<a id="actions"></a>
### 액션 (Actions)

**Actions** 섹션은 사용자가 만든 콘텐츠를 어떤 온톨로지 액션으로 저장할지 지정합니다. **Annotation action**, **Measurement action**, **Section plane action**으로 각 콘텐츠 종류의 액션을 선택합니다.

액션을 설정하지 않으면, Vulcan은 필요한 파라미터 타입 클래스를 가진 액션을 찾아내어 사용자가 일치하는 것 중에서 고르게 합니다. 액션을 설정하면 저장이 그 액션으로 제한되며, 추가 액션 파라미터에 대한 기본값이나 사용자 입력 필드를 제공할 수 있습니다. Vulcan은 [액션 타입](03_schema-reference.md#action-types)에 나열된 도구별 값을 제공합니다.

**설명**: 예를 들어 사용자가 측정 도구로 두 점 사이 거리를 재고 저장을 누르면, Vulcan은 측정 결과(점 좌표, 거리 등)를 액션 파라미터로 넘겨 측정 객체를 생성하는 액션을 실행합니다. 액션을 미리 지정하지 않았다면 "측정 값을 받을 수 있는 파라미터 타입 클래스"를 가진 액션 목록이 사용자에게 제시됩니다.

<a id="output"></a>
### 출력 (Output)

출력을 하나 이상 설정하면, 사용자는 Measurement 도구에서 어떤 측정값을 Workshop으로 보낼지 고를 수 있습니다. **Output** 섹션은 다음 설정을 통해 선택한 측정값을 Workshop 변수로 보냅니다.

* **Measurement scene distance:** 모델의 장면 단위로 표현한 전체 측정 거리(숫자)입니다.
* **Measurement unit distance:** 같은 거리를 사용자가 선택한 표시 단위로 형식화한 문자열입니다(예: `12.30 mm`). 모델에 인식된 단위가 없으면 출력에 `units`를 사용합니다.

> **중간 요약**: Tools에서 필요 없는 도구를 끄고, Actions에서 주석, 측정, 단면을 저장할 온톨로지 액션을 지정(미지정 시 타입 클래스로 자동 탐색)하며, Output으로 선택한 측정 거리를 숫자와 형식화된 문자열로 Workshop 변수에 보냅니다.

## 정리

- Vulcan 위젯은 독립 실행형 Vulcan과 같은 3D 뷰포트와 도구를 Workshop 안에서 제공하며, 위젯 추가, CAD 객체 선택, 설정의 세 단계로 임베드합니다.
- CAD 객체는 `cad_media_reference` 타입 클래스 속성을 가진 객체이며, 객체 집합의 첫 객체가 모델로 로드됩니다.
- 함수 출력으로 부품 위치(열 우선 4×4 행렬)와 색상/불투명도를 바꿀 수 있습니다.
- 카메라, 선택, 클릭 좌표, 측정값을 Workshop 변수와 연결해 다른 위젯과 상호작용하며, 사용자가 만든 주석, 측정, 단면은 온톨로지 액션으로 저장합니다.
