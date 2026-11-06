# 주석 (Annotations)

- 원문: https://www.palantir.com/docs/foundry/map/annotations/
- 사이드바 위치: Applications > Map > Interact with maps > Annotations

이 페이지는 맵에 텍스트나 도형으로 표시를 남기는 주석(annotation) 기능을 설명합니다. 주석은 온톨로지 객체가 아니라 맵 사용자가 직접 그린 표시로, 특정 영역을 강조하거나 메모를 남기는 데 씁니다. 주석을 만드는 방법, 편집하는 방법, 스타일 옵션 전체를 다룹니다.

**주석(annotation)** 을 사용하면 맵의 특정 영역을 강조하고 그 영역에 대한 맥락 정보를 추가할 수 있습니다.

![주석 예시](https://www.palantir.com/docs/resources/foundry/map/annotations-example.png)

<a id="create-an-annotation"></a>
## 주석 만들기 (Create an annotation)

도구 모음에서 **Annotate**를 선택하고 다음 방법 중 하나를 골라 주석을 만듭니다.

* **Text:** 특정 위치에 텍스트를 추가합니다.
* **Line:** 모든 점을 지정해 선을 추가합니다.
* **Polygon:** 모든 점을 지정해 다각형을 추가합니다.
* **Rectangle:** 두 모서리를 지정해 사각형 주석을 추가합니다.
* **Circle:** 중심과 반지름을 지정해 원형 주석을 추가합니다.

![주석 메뉴](https://www.palantir.com/docs/resources/foundry/map/annotations-create-menu.png)

만들려는 주석 종류를 선택하면 [그리기 도구](08_shapes.md#draw-a-shape)가 열리고, 그 그리기 모드로 새 주석을 만드는 방법을 안내합니다. 맵은 주석을 종류별로 레이어에 묶습니다.

<a id="edit-annotations"></a>
## 주석 편집하기 (Edit annotations)

주석을 선택한 다음 **Selection** 패널에서 제목을 편집하고 메모(notes)를 추가합니다. 텍스트 주석의 경우 제목과 메모가 맵 위와, 마우스를 올렸을 때 나타나는 툴팁 양쪽에 표시됩니다. 다각형 주석과 선 주석의 경우 제목과 메모는 툴팁에만 표시됩니다.

**Edit** 버튼을 사용해 주석의 위치를 조정합니다.

![주석 제목 편집](https://www.palantir.com/docs/resources/foundry/map/annotations-modify.png)

> **중간 요약**: **Annotate**에서 Text, Line, Polygon, Rectangle, Circle 중 하나를 골라 주석을 그리고, **Selection** 패널에서 제목과 메모를 편집하며 **Edit** 버튼으로 위치를 조정합니다.

<a id="annotation-styling"></a>
## 주석 스타일 (Annotation styling)

**Layers** 패널에서 주석의 스타일을 편집해 모양을 바꿀 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/annotations-edit-styling.png" alt="주석 스타일 편집" width="450" />

주석 스타일 옵션은 다음과 같습니다.

* **Text**(텍스트)
  * **Text color:** 주석 텍스트의 색을 설정합니다.
  * **Text size:** 주석 텍스트의 크기를 픽셀 단위로 설정합니다.
  * **Text value:** 맵에 표시되는 텍스트 값에 제목뿐 아니라 주석의 메모도 포함할지 설정합니다.
  * **Text outline color:** 텍스트 뒤에 표시되는 외곽선의 색을 설정합니다.
  * **Show location dot:** 켜면 주석이 추가된 정확한 위치를 가리키는 원형 마커를 표시합니다.
  * **Show tooltips:** 켜면 사용자가 주석 위에 마우스를 올렸을 때 주석의 제목과 메모가 담긴 툴팁이 나타납니다.
* **Shapes**(도형)
  * **Color:** 다각형과 선의 색을 설정합니다.
  * **Opacity:** 다각형과 선의 불투명도를 설정합니다.
  * **Stroke width:** 선의 두께와, **Fill polygons**가 꺼져 있을 때 다각형 외곽선의 두께를 설정합니다.
  * **Stroke style:** 선을 그릴 때 쓰는 점선 패턴을 설정합니다.
  * **Measurements:** 맵에 나타나는 측정값을 제어합니다.
    * **Polygon measurements**(다각형 측정값)
      * **Perimeter:** 다각형 둘레의 측정값을 어떻게 표시할지 설정합니다. 표시하지 않음, 둘레의 각 선분마다 길이 표시, 전체 둘레의 총길이 표시 중에서 고릅니다.
      * **Area:** 다각형의 전체 면적 표시를 켭니다.
    * **Line measurements**(선 측정값)
      * **Length:** 선의 측정값을 어떻게 표시할지 설정합니다. 표시하지 않음, 각 선분마다 길이 표시, 선 전체의 총길이 표시 중에서 고릅니다.
  * **Fill polygons:** 켜면 다각형이 최소한의 외곽선과 함께 지정한 색으로 내부가 채워져 그려집니다. 끄면 다각형의 외곽선만 그려집니다.
  * **Show tooltips:** 켜면 사용자가 주석 위에 마우스를 올렸을 때 주석의 제목과 메모가 담긴 툴팁이 나타납니다.

**설명**: 다각형은 꼭짓점을 차례로 이은 닫힌 도형이고, 둘레의 "선분(segment)"은 인접한 두 꼭짓점을 잇는 각 변입니다. 예를 들어 사각형 주석에서 **Perimeter**를 선분별 표시로 두면 네 변의 길이가 각각 표시되고, 총길이 표시로 두면 네 변을 더한 값 하나가 표시됩니다.

> **중간 요약**: 주석 스타일은 **Layers** 패널에서 바꾸며, 텍스트 주석은 색, 크기, 표시 내용, 외곽선, 위치 점, 툴팁을, 도형 주석은 색, 불투명도, 선 두께와 패턴, 둘레/면적/길이 측정값, 채우기, 툴팁을 설정합니다.

## 정리

- 주석은 맵 영역을 강조하고 맥락 정보를 남기는 텍스트나 도형 표시입니다.
- **Annotate** 도구에서 Text, Line, Polygon, Rectangle, Circle 주석을 만들 수 있고, 종류별로 레이어에 묶입니다.
- **Selection** 패널에서 제목과 메모를 편집하며, 텍스트 주석은 맵과 툴팁에, 도형 주석은 툴팁에만 표시됩니다.
- **Layers** 패널에서 텍스트와 도형의 스타일, 측정값 표시(둘레, 면적, 길이), 채우기 여부를 설정합니다.
