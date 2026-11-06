# 임계값 구성하기 (Configure thresholds)

- 원문: https://www.palantir.com/docs/foundry/vertex/configure-thresholds/
- 사이드바 위치: Applications > Vertex > Events and time series > Configure thresholds

이 페이지는 시계열 측정값에 임계값(threshold)을 설정해, 값이 기준을 넘었을 때 Vertex에서 표시되도록 하는 위치를 짧게 안내합니다.

Ontology Manager의 Vertex Capabilities에서 시계열 측정값(time series measure)에 임계값(Thresholds)을 구성할 수 있으며, 이 임계값은 값이 기준을 넘어섰을 때(breached) 이를 표시해 줍니다.

![임계값 구성하기](https://www.palantir.com/docs/resources/foundry/vertex/optional_ontology_config-threshold.jpg)

**설명**: 임계값은 측정값이 넘으면 안 되는 기준 값입니다. 예를 들어 펌프 압력 시계열에 상한 임계값 5.0을 두면, 시계열 값 `(09:00, 4.8), (09:01, 5.3)` 중 09:01 시점의 값은 임계값을 넘은 것으로 표시됩니다. 임계값을 어떤 형식으로 입력하는지 같은 세부 화면 구성은 원문 이미지 외에 별도 설명이 없습니다.

## 정리

- 임계값은 Ontology Manager의 Vertex Capabilities에서 시계열 측정값에 대해 구성합니다.
- 구성한 임계값을 넘으면 Vertex에서 이를 표시합니다.
