# 레이어 관리 (Layer management)

- 원문: https://www.palantir.com/docs/foundry/map/layer-management/
- 사이드바 위치: Applications > Map > Interact with maps > Layer management

이 페이지는 **Layers** 패널에서 레이어를 다루는 방법을 설명합니다. 레이어를 보이거나 숨기기, 이름 바꾸기, 순서 바꾸기, 객체를 다른 레이어로 옮기기를 다룹니다. 레이어 순서는 어떤 데이터가 위에 그려지는지를 정하므로 시각화 결과에 직접 영향을 줍니다.

맵의 모든 데이터는 여러 [레이어 유형](../03_core-concepts.md)으로 묶이며, 이 레이어는 **Layers** 패널에서 관리할 수 있습니다.

<a id="toggle-layer-visibility"></a>
## 레이어 표시 전환 (Toggle layer visibility)

표시 토글을 사용해 레이어의 내용을 보이거나 숨깁니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/layer-management-hide-layer.png" alt="레이어 숨기기 버튼" />

<a id="rename-layers"></a>
## 레이어 이름 바꾸기 (Rename layers)

현재 이름을 클릭해 레이어 이름을 편집합니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/layer-management-edit-layer-name.png" alt="레이어 이름 편집" />

<a id="reorder-layers"></a>
## 레이어 순서 바꾸기 (Reorder layers)

레이어 아이콘을 드래그해 레이어 순서를 바꿉니다. 레이어 목록에서 위쪽에 있는 레이어가 아래쪽에 있는 레이어 위에 그려지므로, 레이어 순서를 바꾸면 맵이 그려지는 모습이 달라질 수 있습니다.

![날씨 레이어가 snotel 레이어 위에 있을 때의 레이어 순서와 렌더링](https://www.palantir.com/docs/resources/foundry/map/layer-management-ordering-weather-first.png)

![snotel 레이어가 날씨 레이어 위에 있을 때의 레이어 순서와 렌더링](https://www.palantir.com/docs/resources/foundry/map/layer-management-ordering-snotel-first.png)

**설명**: 같은 위치에 두 레이어의 도형이 겹치면, 목록에서 위에 있는 레이어의 도형이 나중에 그려져 화면에 보이고 아래 레이어의 도형은 가려집니다. 예를 들어 넓은 날씨 영역 다각형 레이어를 위에 두면 그 아래 관측소(snotel) 점들이 덮여 잘 보이지 않을 수 있으므로, 점 레이어를 위로 올리는 식으로 조정합니다.

<a id="move-objects-to-new-or-existing-layers"></a>
## 객체를 새 레이어나 기존 레이어로 옮기기 (Move objects to new or existing layers)

내용이 모두 같은 객체 타입이라면 객체를 여러 레이어에 나누어 담을 수 있습니다. 선택한 집합을 새 레이어로 옮기면, 아래 이미지처럼 각 집합의 객체에 서로 다른 스타일을 적용할 수 있습니다.

![선택한 기상 관측소 객체 집합으로 새 레이어 만들기](https://www.palantir.com/docs/resources/foundry/map/layer-management-move-to-new-layer.png)

![기상 관측소 객체를 기존 레이어로 옮기기](https://www.palantir.com/docs/resources/foundry/map/layer-management-move-to-layer.png)

**설명**: 스타일은 레이어 단위로 지정됩니다. 그래서 같은 Weather Station 객체 타입이라도 "점검 필요" 관측소만 골라 별도 레이어로 옮기면, 그 레이어만 빨간색으로 칠하고 나머지는 회색으로 두는 식의 구분이 가능합니다. 한 레이어에는 한 객체 타입만 담을 수 있습니다.

## 정리

- 맵의 데이터는 레이어로 묶이며 **Layers** 패널에서 관리합니다.
- 표시 토글로 레이어를 보이거나 숨기고, 이름을 클릭해 바꿀 수 있습니다.
- 목록에서 위에 있는 레이어가 위에 그려지므로, 아이콘을 드래그해 순서를 조정합니다.
- 같은 객체 타입의 객체를 여러 레이어로 나누면 집합마다 다른 스타일을 적용할 수 있습니다.
