# 액션 (Actions)

- 원문: https://www.palantir.com/docs/foundry/map/actions/
- 사이드바 위치: Applications > Map > Interact with maps > Actions

이 페이지는 Map 애플리케이션에서 온톨로지 액션을 실행하는 방법을 다룹니다. 지도 위의 점, 다각형, 선을 액션의 입력으로 넘겨 객체를 만들거나, 이미 있는 객체의 지리 정보를 지도에서 직접 그려서 고칠 수 있습니다. 지도 위 위치나 도형에서 시작하는 경우와, 선택한 객체에서 시작하는 경우를 나눠 설명합니다.

Map 애플리케이션에서 [액션](../07_integrate-data-for-the-map/04_integrate-actions.md)을 사용하면 지도에 그린 점, 다각형, 선을 바탕으로 객체를 만들거나 편집할 수 있습니다.

<a id="actions-on-shapes-and-points"></a>
## 도형과 점에 대한 액션 (Actions on shapes and points)

지도를 마우스 오른쪽 버튼으로 클릭하면, 메뉴의 **Actions** 항목에 지리 점(geospatial point)에 적용되는 모든 액션이 아래처럼 표시됩니다.

![오른쪽 클릭 액션 메뉴](https://www.palantir.com/docs/resources/foundry/map/actions-right-click-menu.png)

[도형을 그린](08_shapes.md) 뒤에는 툴바의 **Actions** 버튼에 그린 다각형, 선, 점에 적용되는 모든 액션이 표시됩니다.

![도형 도구의 액션 메뉴](https://www.palantir.com/docs/resources/foundry/map/actions-shape-menu.png)

이 메뉴 중 하나에서 액션을 선택한 뒤, 추가로 입력해야 하는 파라미터가 있을 수 있습니다. 이 경우 Map은 추가 파라미터를 입력할 수 있는 대화 상자를 표시합니다.

![액션 폼이 있는 대화 상자](https://www.palantir.com/docs/resources/foundry/map/actions-dialog.png)

추가 파라미터가 없거나 대화 상자의 폼을 제출하고 나면, Map 애플리케이션이 액션을 실행하고 액션이 만든 지리 객체를 지도에 추가합니다.

**설명**: 예를 들어 "사고 지점 등록" 액션 타입에 위치(지리 점) 파라미터와 사고 유형(문자열) 파라미터가 있다고 합시다. 지도에서 사고가 난 지점을 오른쪽 클릭하고 이 액션을 고르면, 위치 파라미터는 클릭한 좌표로 자동으로 채워지고 대화 상자에서는 사고 유형만 입력하면 됩니다. 제출하면 새 Incident 객체가 만들어지고 그 지점에 바로 표시됩니다.

<a id="actions-on-ontology-objects"></a>
## 온톨로지 객체에 대한 액션 (Actions on Ontology objects)

**Selection** 패널의 **Actions** 버튼을 사용해 선택한 객체에 지리 액션을 실행합니다. 액션을 선택하면 액션에 지정된 구성에 따라 도형을 편집하거나 새로 만들라는 안내가 나옵니다.

![도형을 갱신하는 액션 적용](https://www.palantir.com/docs/resources/foundry/map/actions-update-shape.gif)

도형 그리기 또는 편집 도구에서 **Done**을 클릭하면, 추가로 입력해야 하는 파라미터가 있을 수 있습니다. 이 경우 Map은 추가 파라미터를 입력할 수 있는 대화 상자를 표시합니다.

![액션 폼이 있는 대화 상자](https://www.palantir.com/docs/resources/foundry/map/actions-dialog.png)

추가 파라미터가 없거나 대화 상자의 폼을 제출하고 나면, Map 애플리케이션이 액션을 실행하고 액션이 만들거나 수정한 객체가 반영되도록 지도를 갱신합니다.

**설명**: 이 경우는 이미 있는 객체가 출발점입니다. 예를 들어 배송 구역 객체 하나를 선택하고 "구역 경계 수정" 액션을 고르면, 그 객체의 현재 `geoshape` 다각형이 편집 가능한 상태로 나타나고, 꼭짓점을 옮긴 뒤 **Done**을 누르면 수정된 다각형이 액션 파라미터로 넘어가 객체의 속성이 갱신됩니다.

## 정리

- Map 애플리케이션에서는 지도에 그린 점, 다각형, 선을 입력으로 온톨로지 액션을 실행해 객체를 만들거나 편집할 수 있습니다.
- 지도를 오른쪽 클릭하면 점에 적용되는 액션이, 도형을 그린 뒤 툴바의 **Actions** 버튼에서는 그 도형에 적용되는 액션이 나옵니다.
- 선택한 객체에는 **Selection** 패널의 **Actions** 버튼으로 지리 액션을 실행하며, 구성에 따라 도형을 편집하거나 새로 그립니다.
- 추가 파라미터가 있으면 대화 상자에서 입력하고, 실행 결과로 만들어지거나 수정된 객체가 지도에 반영됩니다.
