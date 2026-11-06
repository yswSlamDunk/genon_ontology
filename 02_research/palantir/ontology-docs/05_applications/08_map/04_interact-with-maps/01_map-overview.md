# Map 화면 개요 (Map interface overview)

- 원문: https://www.palantir.com/docs/foundry/map/map-overview/
- 사이드바 위치: Applications > Map > Interact with maps > Map interface overview

이 페이지는 Map 애플리케이션 화면의 구성 요소를 정리한 참고 페이지입니다. 화면 왼쪽과 오른쪽의 패널, 그리고 위쪽 도구 모음에 어떤 기능이 있는지 나열합니다. 이후 "Interact with maps" 섹션의 각 페이지가 이 구성 요소를 하나씩 자세히 다룹니다.

이 페이지는 아래에 보이는 Map 애플리케이션 화면의 요소를 설명합니다.

![Map 애플리케이션](https://www.palantir.com/docs/resources/foundry/map/map-interface-overview.png)

<a id="panels"></a>
## 패널 (Panels)

화면 왼쪽에는 다음 패널이 있습니다.

* **Layers:** 객체 레이어와 오버레이 레이어를 추가, 관리하고 스타일을 지정하며 베이스 레이어를 설정합니다.
* **Find:** 객체와 위치를 찾고, 특정 지리 좌표로 이동합니다.
* **Histogram:** 속성 값과 시계열 값을 기준으로 객체를 분석하고 필터링합니다.
* **Info:** 맵 전체의 요약을 표시합니다.

화면 오른쪽에는 다음 패널이 있습니다.

* **Selection:** 선택한 항목의 세부 정보를 분석하고 그 항목에 대해 액션을 수행합니다.
* **Time Selection:** 맵과 시계열 뷰에 적용할 시간 범위와 현재 타임스탬프를 설정합니다.

화면 오른쪽 아래에서는 **Series** 패널로 시계열 데이터와 이벤트 데이터의 시간 분석을 할 수 있습니다.

<a id="toolbars"></a>
## 도구 모음 (Toolbars)

화면 위쪽에는 다음 기능이 있는 도구 모음이 있습니다.

* **Select:** 맵의 모든 항목을 선택하거나, 선택을 반전하거나, 그린 도형과 교차하는 항목을 선택합니다.
* **Search Around:** 객체 관계를 탐색합니다.
* **Draw:** 다각형, 원, 사각형, 선, 점 등의 도형을 맵에 그리고 다룹니다.
* **Capture:** 현재 맵 상태의 스크린숏을 캡처합니다.
* **Measure:** 맵에서 물리적 거리를 측정합니다.
* **Annotate:** 맵에 텍스트 주석이나 다각형 주석을 추가합니다.
* **Delete:** 맵에서 항목을 제거합니다.

**설명**: 선택 반전(invert selection)은 지금 선택된 항목은 선택 해제하고, 선택되지 않은 항목을 모두 선택하는 동작입니다. 예를 들어 공항 10개 중 3개가 선택된 상태에서 반전하면 나머지 7개가 선택됩니다.

## 정리

- 왼쪽 패널: Layers(레이어 관리), Find(검색과 이동), Histogram(분포 분석과 필터), Info(맵 요약).
- 오른쪽 패널: Selection(선택 항목 상세와 액션), Time Selection(시간 범위와 현재 시각).
- 오른쪽 아래 **Series** 패널은 시계열과 이벤트의 시간 분석을 담당합니다.
- 위쪽 도구 모음: Select, Search Around, Draw, Capture, Measure, Annotate, Delete.
