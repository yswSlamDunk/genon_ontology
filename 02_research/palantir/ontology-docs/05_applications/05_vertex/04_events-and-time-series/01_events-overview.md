# 이벤트와 시계열 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/vertex/events-overview/
- 사이드바 위치: Applications > Vertex > Events and time series > Overview

이 페이지는 Vertex에서 시간에 따른 변화를 다루는 두 종류의 데이터, 즉 이벤트(event)와 시계열(time series)을 소개하고 관련 하위 페이지로 안내합니다. 둘 다 온톨로지에 설정해 두어야 Vertex에서 사용할 수 있으므로, 각각이 온톨로지의 어떤 요소로 표현되는지 먼저 알아 두는 것이 중요합니다.

Vertex에는 조직이 시간에 따라 어떻게 변하는지 이해하도록 돕는 기능들이 들어 있습니다. 이는 과거의 이벤트를 분석하고 미래의 이벤트를 예측하는 데 유용하며, 특히 Vertex의 [시나리오](../05_scenarios/01_scenarios-overview.md) 지원과 함께 사용할 때 효과적입니다.

알아 두어야 할 시간 데이터(temporal data)에는 크게 두 가지, **이벤트**와 **시계열이** 있습니다.

* 이벤트는 시간 정보를 포함하도록 온톨로지에 구성된 [객체 타입](../../../02_define-ontologies/02_object-and-link-types/02_object-types/01_object-types-overview.md)입니다. 최소한 이벤트의 시작과 끝을 나타내는 타임스탬프 두 개가 있어야 합니다.
* [시계열](https://www.palantir.com/docs/foundry/time-series/time-series-overview/)은 시간에 따라 측정된 값을 나타내며, 온톨로지에서 [시계열 속성(time series property)](https://www.palantir.com/docs/foundry/time-series/time-series-setup/)으로 구성할 수 있습니다.

**설명**: 두 데이터의 차이를 테이블로 보면 분명해집니다. 이벤트 객체 타입은 행 하나가 "언제부터 언제까지 일어난 일" 하나입니다. 예를 들어 Flight Delay 테이블의 한 행은 `delay_id=D1, flight_id=F100, start=2024-03-01 09:00, end=2024-03-01 10:30` 처럼 시작과 끝 시각을 갖습니다. 반면 시계열은 하나의 객체(예: 펌프 P1)에 딸린 `(시각, 값)` 쌍의 긴 목록입니다. 예를 들어 P1의 압력이 `(09:00, 3.1), (09:01, 3.2), (09:02, 3.0) ...` 처럼 계속 기록되며, 이 목록 전체가 P1 객체의 시계열 속성 하나에 연결됩니다.

먼저 [이벤트 구성 방법](02_configure-events.md)을 알아본 다음, Vertex에서 이벤트와 시계열을 어떻게 활용하는지 살펴보세요.

* [관련 이벤트 탐색하기](03_explore-related-events.md)
* [관련 시계열 탐색하기](04_explore-time-series.md)
* [시간 선택 사용하기](05_use-time-selection.md)
* [임계값 구성하기](06_configure-thresholds.md)

## 정리

- Vertex는 시간에 따른 변화를 분석하고 예측하는 기능을 제공하며, 시나리오와 함께 쓰면 특히 유용합니다.
- 이벤트는 시작과 끝 타임스탬프를 가진 객체 타입이고, 시계열은 시간에 따라 측정된 값으로 온톨로지에서 시계열 속성으로 구성합니다.
- 이벤트 구성부터 시작해 이벤트 탐색, 시계열 탐색, 시간 선택, 임계값 구성 순으로 학습할 수 있습니다.
