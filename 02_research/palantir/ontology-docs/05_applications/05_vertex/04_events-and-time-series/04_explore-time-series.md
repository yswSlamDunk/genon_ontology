# 관련 시계열 탐색하기 (Explore related time series)

- 원문: https://www.palantir.com/docs/foundry/vertex/explore-time-series/
- 사이드바 위치: Applications > Vertex > Events and time series > Explore related time series

이 페이지는 Vertex 그래프에서 객체에 연결된 시계열을 보고, 시리즈 뷰나 다른 애플리케이션에서 열고, 그래프 위 라벨과 판독값(readout)으로 표시하는 방법을 설명합니다.

Vertex 그래프에서는 [시계열(time series)](https://www.palantir.com/docs/foundry/time-series/time-series-overview/)과 상호작용하여 시스템 전반의 변화를 시각화하고, 분석을 심화해 과거 결정의 영향, 현재 상태, 미래 가능성을 보여 줄 수 있습니다.

**참고**: 모든 고객 설치 환경에 시계열이 포함되어 있지는 않습니다. 이 기능에 대해 더 알고 싶다면 Palantir 담당자에게 문의하세요.

**관련 시계열 보기(View related time series):** 객체를 선택하면 선택 사이드바의 **Series** 탭에서 관련 시계열을 볼 수 있습니다. 객체에 표시된 개별 시계열 옆의 **...을** 선택하면 메뉴에 여러 옵션이 나타납니다.

![시계열](https://www.palantir.com/docs/resources/foundry/vertex/changes-over-time-3.jpg)

**시리즈 뷰에서 열기(Open in series view):** 시계열을 시리즈 뷰에 추가하면 그래프 아래쪽에 타임라인 시각화가 표시됩니다. 시리즈 뷰에서 보고 싶은 시점을 클릭하거나 시리즈 패널 아래쪽의 타임라인을 스크롤해 시간을 이동할 수 있습니다.

![시리즈 뷰](https://www.palantir.com/docs/resources/foundry/vertex/changes-over-time-4.jpg)

**Quiver / Object Explorer에서 열기(Open in Quiver / Object Explorer):** **Open in Quiver** 또는 **Open in Object Explorer** 옵션을 선택하면 새 창이 열려 시계열을 더 자세히 볼 수 있습니다.

**확장 라벨/판독값에 추가(Add to extended label/readout):** 선택한 객체의 라벨에 시계열 값을 표시합니다. **Add to readout**을 선택하면 객체 라벨에 붙이지 않고 시계열 값을 그래프에 추가할 수 있으므로, 시스템이나 프로세스 안에서 가장 관련 있는 위치에 이 값들을 배치할 수 있습니다.

![시리즈 판독값](https://www.palantir.com/docs/resources/foundry/vertex/changes-over-time-5.jpg)

**설명**: 그래프에 표시되는 시계열 값은 "현재 보고 있는 시점"의 값입니다. 예를 들어 펌프 P1의 압력 시계열이 `(09:00, 3.1), (09:01, 3.2)`라면, 타임라인에서 09:01을 선택했을 때 P1의 라벨이나 판독값에는 3.2가 표시됩니다. 시점을 바꾸면 표시 값도 그 시점의 값으로 바뀝니다.

## 정리

- 객체를 선택하면 선택 사이드바의 **Series** 탭에서 관련 시계열을 볼 수 있습니다.
- 시계열을 시리즈 뷰에 추가하면 그래프 아래 타임라인에서 시점을 옮겨 가며 볼 수 있습니다.
- Quiver나 Object Explorer에서 열어 더 자세히 분석할 수 있습니다.
- 시계열 값을 객체 라벨이나 독립된 판독값으로 그래프 위에 표시할 수 있습니다.
