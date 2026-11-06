# 도형 (Shapes)

- 원문: https://www.palantir.com/docs/foundry/map/shapes/
- 사이드바 위치: Applications > Map > Interact with maps > Shapes

이 페이지는 Map 애플리케이션에서 도형(shape)을 만들고 수정하고 활용하는 방법을 다룹니다. 도형은 지도 위의 지리 영역을 지정하는 다각형, 선, 점으로, 그 영역 안의 객체를 검색하거나 선택하고, 지리 정보를 입력으로 받는 액션을 실행하는 데 쓰입니다.

도형을 사용하면 지도에서 객체를 검색할 지리 영역을 선택하거나, 이미 지도에 있는 객체를 선택하거나, 액션을 실행하거나, 주석(annotation)을 만들 수 있습니다.

<a id="create-a-shape"></a>
## 도형 만들기 (Create a shape)

도형에 대해 사용할 수 있는 모든 작업은 먼저 활성화된 도형(active shape)이 있어야 합니다. 다음 방법 중 하나로 도형을 만듭니다.

* [그리기 도구](#draw-a-shape)를 사용해 직접 도형을 만듭니다.
* 현재 선택된 객체와 주석을 사용해 [선택 영역과 같은 지리 영역](#from-selection)을 덮는 도형을 만듭니다.

<a id="draw-a-shape"></a>
### 도형 그리기 (Draw a shape)

툴바에서 **Drawing method** 옵션 중 하나를 고르거나 키보드에서 `D`를 눌러 지도에 직접 도형을 그립니다.

![그리기 도구 열기](https://www.palantir.com/docs/resources/foundry/map/shapes-draw-button.png)

현재 그리기 모드를 클릭하면 열리는 드롭다운에서 사용 가능한 여러 모드 중 하나를 선택합니다.

![그리기 모드 선택](https://www.palantir.com/docs/resources/foundry/map/shapes-draw-modes.png)

<a id="from-selection"></a>
### 선택 영역에서 만들기 (From selection)

지도에서 현재 선택한 항목으로부터 도형을 만들 수도 있습니다. 선택된 객체 아무거나 마우스 오른쪽 버튼으로 클릭하고 **Create shape from selection** 메뉴 항목을 사용합니다.

![선택 영역에서 도형 만들기](https://www.palantir.com/docs/resources/foundry/map/shapes-from-selection.png)

<a id="modify-a-shape"></a>
## 도형 수정하기 (Modify a shape)

도형 툴바의 **Modify** 버튼을 사용해 지도의 활성 도형을 편집할 수 있습니다.

![Modify 버튼](https://www.palantir.com/docs/resources/foundry/map/shapes-modify-button.png)

다음과 같은 수정 도구를 사용할 수 있습니다.

![Modify 툴바](https://www.palantir.com/docs/resources/foundry/map/shapes-modify-modes.png)

* **Edit points(점 편집):** 개별 꼭짓점을 끌어서 다각형, 선, 점을 수정할 수 있습니다.
* **Buffer(버퍼):** 특정 거리를 입력해 도형의 둘레를 그만큼 키우거나 줄일 수 있습니다.
* **Translate(이동):** 도형 전체를 끌어서 옮길 수 있습니다.
* **Replace(교체):** 현재 그린 도형을 버리고, 새 도형을 그릴 수 있도록 그리기 도구를 엽니다.

수정을 마쳤으면 **Done** 버튼으로 도형 툴바로 돌아갑니다.

**설명**: 버퍼는 지리 정보 시스템(GIS)의 표준 연산으로, 도형의 경계에서 지정한 거리 안에 있는 모든 점을 포함하도록 영역을 넓히거나(양수 거리) 좁히는(음수 거리) 계산입니다. 예를 들어 도로를 나타내는 선에 500 m 버퍼를 주면 도로 양쪽 500 m 폭의 띠 모양 다각형이 됩니다.

<a id="perform-operations-with-an-active-shape"></a>
## 활성 도형으로 작업하기 (Perform operations with an active shape)

활성 도형이 있으면 **Shapes** 툴바로 여러 작업을 할 수 있습니다.

![Shapes 툴바](https://www.palantir.com/docs/resources/foundry/map/shapes-toolbar.png)

* **Select intersecting(교차 항목 선택):** 보이는 레이어에 있으면서 현재 도형과 교차하는 지도 위의 모든 객체를 선택합니다.
* **Search within(내부 검색):** **Add objects** 패널을 열고, 지리 데이터가 현재 도형과 교차하는 객체만 결과에 남도록 필터링합니다. [`geohash` 또는 `geoshape` 속성](../07_integrate-data-for-the-map/01_integrate-objects.md)을 가진 객체만 검색할 수 있습니다.
* **Actions(액션):** 도형을 입력으로 받는 사용 가능한 모든 온톨로지 액션을 보여 줍니다. 지리 액션 구성에 대해서는 [액션](10_actions.md)을 참고하세요. 액션 버튼은 온톨로지에 지리 액션이 구성되어 있을 때만 나타납니다.
* **Delete(삭제):** 선택한 도형을 지도 인터페이스에서 제거합니다.

**설명**: `geohash` 속성은 위도와 경도로 정해지는 점 위치를, `geoshape` 속성은 다각형이나 선 같은 모양을 저장하는 속성 타입입니다. "교차(intersect)"는 두 도형이 한 점이라도 공유한다는 공간 조건으로, 예를 들어 서울 강남구를 덮는 다각형을 그린 뒤 **Search within**을 하면 위치(점)가 그 다각형 안에 있는 매장 객체나, 경로(선)가 그 다각형을 지나가는 배송 경로 객체가 결과에 나옵니다.

## 정리

- 도형은 지도 위의 지리 영역을 지정하는 데 쓰이며, 모든 도형 작업에는 활성 도형이 필요합니다.
- 도형은 그리기 도구(`D` 키)로 직접 그리거나, 선택한 객체와 주석에서 **Create shape from selection**으로 만듭니다.
- **Modify**에서 점 편집, 버퍼, 이동, 교체로 도형을 수정합니다.
- 활성 도형으로 교차 객체 선택, `geohash`나 `geoshape` 속성 기반 내부 검색, 지리 액션 실행, 도형 삭제를 할 수 있습니다.
