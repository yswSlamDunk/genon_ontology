# 시간 선택 사용하기 (Use time selection)

- 원문: https://www.palantir.com/docs/foundry/vertex/use-time-selection/
- 사이드바 위치: Applications > Vertex > Events and time series > Use time selection

이 페이지는 Vertex 작업 공간 위쪽의 시간 선택(time selection) 막대로 시간 구간을 정하고, 여러 구간을 나란히 비교하는 방법을 설명합니다.

작업 공간 위쪽의 **Time selection** 막대를 선택하면 시간 창(time window)을 정하고 스크롤하면서 시스템이 시간에 따라 어떻게 변하는지 이해할 수 있습니다. 관심 있는 특정 시간 범위가 있다면 날짜 선택기로 시간 창을 지정할 수도 있습니다.

![시간 선택](https://www.palantir.com/docs/resources/foundry/vertex/changes-over-time-1.jpg)

비교를 위해 시간 선택을 여러 개 만들 수 있습니다. **Time selection** 창 오른쪽의 **+ Compare** 버튼을 클릭하면 시간 선택이 추가됩니다. 선택한 시간 창들을 비교하면 그래프의 확장 라벨과 판독값에 표시되는 값이 갱신됩니다. 이렇게 갱신되는 값을 통해 시간에 따른 변화를 시각화하고 비교할 수 있습니다.

![시간 비교](https://www.palantir.com/docs/resources/foundry/vertex/changes-over-time-2.jpg)

시뮬레이션 사례 연구(simulation case study)가 있다면 드롭다운에서 선택해 모델링된 값을 비교할 수 있습니다.

**설명**: 시간 창은 시작 시각과 끝 시각으로 정한 구간입니다. 예를 들어 첫 번째 시간 선택을 "3월 1일 09:00\~10:00", 두 번째를 "3월 8일 09:00\~10:00"으로 두면, 같은 펌프의 압력 값이 두 구간에서 각각 어떻게 표시되는지 나란히 비교할 수 있습니다.

## 정리

- **Time selection** 막대로 시간 창을 정하고 스크롤하거나 날짜 선택기로 범위를 지정합니다.
- **+ Compare**로 시간 선택을 여러 개 만들면 라벨과 판독값이 구간별로 갱신되어 비교할 수 있습니다.
- 시뮬레이션 사례 연구를 선택하면 모델링된 값과도 비교할 수 있습니다.
