# 선택 (Selection)

- 원문: https://www.palantir.com/docs/foundry/map/selection/
- 사이드바 위치: Applications > Map > Interact with maps > Selection

이 페이지는 맵에서 객체와 주석을 선택하는 여러 방법과, 선택한 항목을 다루는 **Selection** 패널을 설명합니다. 클릭과 단축키로 고르는 방법, **Select** 메뉴의 고급 선택 기능, 히스토그램을 이용한 선택, 객체 잠금, 선택 항목의 속성과 시계열과 이벤트와 Object View 보기, 그리고 맵에서 항목을 제거하는 방법까지 다룹니다.

Map 애플리케이션에는 객체와 주석을 선택하는 다양한 방법이 있습니다.

<a id="select-items-on-the-map"></a>
## 맵에서 항목 선택하기 (Select items on the map)

* **항목 선택:** 객체나 주석을 클릭하면 선택됩니다. 커서 아래에 항목이 여러 개 있으면 모두 선택됩니다.
* **기존 선택에 항목 추가:** Ctrl(Windows) 또는 Cmd(macOS)를 누른 채 클릭하면 커서 아래의 항목이 선택에 추가됩니다.
* **사각형 영역의 모든 항목 선택:** Shift를 누른 채 클릭하고 커서를 드래그하면 사각형 영역 안의 모든 항목이 선택됩니다.
* **선택 해제:** 맵의 빈 곳을 클릭합니다.

**Select** 도구 모음 메뉴에는 추가 선택 옵션이 있습니다.

* **Select All:** 맵의 모든 항목을 선택합니다.
  * Ctrl+A(Windows) 또는 Cmd+A(macOS) 단축키로도 사용할 수 있습니다.
* **Select All of "Type":** 현재 선택한 객체의 객체 타입과 일치하는 모든 항목을 선택합니다.
  * 한 가지 객체 타입만 포함된 선택이 이미 있을 때만 사용할 수 있습니다.
* **Invert Selection:** 현재 선택되지 않은 모든 항목으로 선택을 바꿉니다.
  * Ctrl+I(Windows) 또는 Cmd+I(macOS) 단축키로도 사용할 수 있습니다.
* **Select intersecting objects:** 현재 선택된 모든 항목과 교차하는 모든 객체를 선택합니다.
  * 기존 선택이 있을 때만 사용할 수 있습니다.
* **Select intersecting a shape...:** 도형을 그리고 그 도형과 교차하는 모든 객체를 선택할 수 있습니다.
  * 기존 선택이 없을 때만 사용할 수 있습니다.

이 기능들은 마우스 오른쪽 클릭 메뉴에서도 사용할 수 있습니다.

| **Select** 메뉴                                            | 기존 선택이 있을 때의 **Select** 메뉴                                                   | 도형의 오른쪽 클릭 메뉴                                                      |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| ![도구 모음의 Select 메뉴](https://www.palantir.com/docs/resources/foundry/map/selection-toolbar-menu.png) | ![항목이 선택되었을 때 도구 모음의 Select 메뉴](https://www.palantir.com/docs/resources/foundry/map/selection-toolbar-menu-active.png) | ![도형의 오른쪽 클릭 메뉴](https://www.palantir.com/docs/resources/foundry/map/selection-right-click-menu-intersecting.png) |

**Layer Actions** 메뉴의 **Select objects in layer** 항목을 사용하면 특정 레이어의 모든 객체를 선택할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/selection-layer-actions-menu.png" alt="레이어 액션 메뉴가 열린 Layers 패널" width="459" />

**설명**: **Select intersecting objects**는 선택한 항목을 검색 영역으로 쓰는 기능입니다. 예를 들어 "홍수 위험 구역" 다각형 주석을 선택한 뒤 이 기능을 쓰면, 그 다각형과 겹치는 공항, 도로, 건물 객체가 한꺼번에 선택됩니다. **Select intersecting a shape...** 는 선택이 없을 때 새 도형을 그려 같은 일을 하는 방법입니다.

> **중간 요약**: 클릭, Ctrl/Cmd 클릭, Shift 드래그로 직접 고르고, **Select** 메뉴나 오른쪽 클릭 메뉴로 전체 선택, 같은 타입 선택, 반전, 교차 객체 선택을 할 수 있습니다. 레이어 단위 전체 선택도 가능합니다.

<a id="select-items-using-the-histogram"></a>
## 히스토그램으로 항목 선택하기 (Select items using the histogram)

**Histogram** 패널에서 행을 클릭하면 일치하는 모든 객체가 선택됩니다. 두 번째 행을 선택할 때 Shift를 누르고 있으면 행 범위가 선택됩니다. Ctrl(Windows) 또는 Cmd(macOS)를 누르고 있으면 그 행이 기존 선택에 추가됩니다. 자세한 내용은 [히스토그램과 필터링 문서](09_histogram.md)에서 확인할 수 있습니다.

![히스토그램 행이 선택된 Map 애플리케이션](https://www.palantir.com/docs/resources/foundry/map/selection-histogram-row.png)

<a id="locking-objects-on-the-map"></a>
## 맵에서 객체 잠그기 (Locking objects on the map)

**Layers** 패널의 "Objects" 섹션 아래에 있는 **…** 옵션을 선택해 레이어의 객체를 잠급니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/selection-locking.png" alt="레이어의 객체 잠그기" width="459" />

이렇게 하면 레이어의 객체가 잠겨 맵에서 선택할 수 없게 됩니다. 왼쪽의 **Layers**, **Find**, **Histogram** 패널에서는 여전히 객체를 선택할 수 있지만, 맵 위에서 커서, 선택 단축키, 교차 도형으로는 그 객체와 상호작용할 수 없습니다. **…** 메뉴 버튼에서 레이어의 스타일은 계속 편집할 수 있습니다.

레이어의 객체 잠금을 풀려면 **Layers** 패널에서 레이어 옆의 자물쇠 아이콘을 선택하거나 **…** 드롭다운 메뉴를 사용합니다.

**설명**: 잠금은 배경 정보로만 쓰는 레이어가 클릭을 가로채지 않게 할 때 유용합니다. 예를 들어 국가 경계 다각형 레이어가 화면 전체를 덮고 있으면 그 위의 공항 점을 클릭할 때마다 국가 다각형도 함께 선택되는데, 국가 레이어를 잠그면 공항만 선택됩니다.

> **중간 요약**: **Histogram** 패널의 행을 클릭해 그 값에 해당하는 객체를 선택할 수 있고, 레이어를 잠그면 맵 위에서 그 레이어 객체가 선택되지 않습니다.

<a id="selection-panel"></a>
## Selection 패널 (Selection Panel)

여러 객체가 선택되어 있으면 **Selection** 패널에 그 객체 목록이 표시됩니다. 이 목록에서 객체 하나를 클릭하면 선택을 그 객체로 좁힐 수 있습니다. 객체 하나가 선택된 상태에서는 오른쪽 **Selection** 패널에 그 객체의 세부 정보가 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/selection-panel-single-object.png" alt="객체 하나를 보여 주는 Selection 패널" width="327" />

객체에 액션이 있다면 ![망치 아이콘](https://www.palantir.com/docs/resources/foundry/map/selection-hammer-icon.png) 아이콘을 클릭해 사용할 수 있습니다. 맵 중심을 객체에 맞추기, 맵에서 객체 삭제하기, 다른 애플리케이션에서 객체 열기 같은 추가 동작은 **...** 메뉴에서 사용할 수 있습니다.

이 패널에는 탭이 네 개 있습니다.

* **Properties** 탭은 객체의 속성을 보여 줍니다.
  * 속성을 마우스 오른쪽 버튼으로 클릭하고 **Pin property**를 선택해 고정할 수 있습니다. 고정한 속성은 맨 위에 표시되며, 나머지 속성은 숨길 수 있습니다.
  * 사용할 수 있는 [함수(function)](../07_integrate-data-for-the-map/03_integrate-functions.md)가 있다면 오른쪽 아래의 ![더하기 아이콘](https://www.palantir.com/docs/resources/foundry/map/selection-plus-icon.png) 를 선택해 추가할 수 있습니다. 함수를 선택하면 그 함수가 반환한 값이 속성 목록에 추가됩니다.
* **Series** 탭은 객체에 연결된 시계열을 보여 줍니다.
* **Events** 탭은 현재 선택된 시간 창 안에서 객체에 연결된 이벤트를 보여 줍니다.
* **Object view** 탭은 [Ontology Manager의 **Object Views** 탭](../../03_object-views/01_overview.md)에서 설정한 Object View를 보여 줍니다.

객체의 기본 탭은 Ontology Manager의 **Capabilities** 탭에서 바꿀 수 있습니다.

![Ontology Manager에서 "Default Object Selection Panel"이라는 라벨과 "객체 선택 뷰에 표시할 기본 패널을 설정합니다"라는 설명이 붙은 섹션. 드롭다운 옵션은 "Property list", "Series list", "Events list", "Object view panel"](https://www.palantir.com/docs/resources/foundry/map/oma-capabilities-default-selection-tab.png)

| 함수 추가하기                                                                                                                              | 함수 값 표시하기                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| <img src="https://www.palantir.com/docs/resources/foundry/map/selection-panel-single-object-with-derived-properies-menu.png" alt="함수 메뉴가 열린 Selection 패널" width="333" /> | <img src="https://www.palantir.com/docs/resources/foundry/map/selection-panel-single-object-with-derived-propery.png" alt="함수 값이 포함된 Selection 패널" width="327" /> |

**설명**: **Properties** 탭에 함수를 추가하는 것은 저장된 열이 아니라 계산된 값을 보여 주는 기능입니다. 예를 들어 Airport 객체를 받아 "오늘 지연된 항공편 수"를 계산해 반환하는 함수를 추가하면, 그 숫자가 속성 목록에 한 줄로 나타납니다. 데이터베이스로 치면 저장된 열이 아니라 조회할 때마다 계산하는 파생 열(derived column)에 해당합니다.

> **중간 요약**: **Selection** 패널은 선택된 객체의 목록이나 상세를 보여 주며, 망치 아이콘으로 액션을 실행합니다. **Properties**, **Series**, **Events**, **Object view** 네 탭이 있고, 기본 탭은 Ontology Manager의 **Capabilities** 탭에서 정합니다.

<a id="remove-items-from-the-map"></a>
## 맵에서 항목 제거하기 (Remove items from the map)

선택한 객체와 주석을 맵에서 제거하려면 다음 중 하나를 합니다.

* 도구 모음에서 **Delete**를 클릭합니다.
* 오른쪽 클릭 메뉴에서 **Delete selection** 항목을 선택합니다.
* 키보드의 Delete 키를 누릅니다.

삭제된 항목 수를 확인하는 토스트(toast) 알림이 나타나며, **Undo** 옵션으로 이 동작을 되돌릴 수 있습니다.

한 레이어 안의 모든 객체를 제거하려면 **Layer actions** 메뉴의 **Delete layer** 항목을 사용합니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/selection-delete-layer.png" alt="레이어 액션 메뉴가 열린 Map 애플리케이션" width="459" />

**설명**: 여기서 "삭제"는 맵 화면에서 항목을 빼는 것일 뿐, 온톨로지에 저장된 객체 자체를 지우는 것이 아닙니다. 객체 데이터를 바꾸거나 지우려면 액션을 사용해야 합니다.

## 정리

- 클릭, Ctrl/Cmd 클릭, Shift 드래그, 빈 곳 클릭으로 기본 선택을 조작합니다.
- **Select** 메뉴와 오른쪽 클릭 메뉴는 전체 선택, 같은 타입 선택, 반전, 교차 객체 선택, 도형 교차 선택을 제공하며, 레이어 단위 선택도 가능합니다.
- **Histogram** 패널의 행으로도 선택할 수 있고, 레이어를 잠그면 맵 위에서 선택되지 않습니다.
- **Selection** 패널은 액션 실행과 **Properties**, **Series**, **Events**, **Object view** 탭을 제공하며, 함수 값을 속성 목록에 추가할 수 있습니다.
- **Delete**, **Delete selection**, Delete 키, **Delete layer**로 맵에서 항목을 제거하며, **Undo**로 되돌릴 수 있습니다.
