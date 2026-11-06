# 시계열 규칙 [Sunset] (Time series rules [Sunset])

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/timeseries-concepts/
- 사이드바 위치: Applications > Foundry Rules > Time series > Time series rules [Sunset]

이 페이지는 Foundry Rules에서 시계열(time series) 데이터를 대상으로 규칙을 작성하는 기능과, 이를 위한 두 가지 로직 보드(Add Timeseries, Timeseries Search)를 설명합니다. 이 기능은 단계적 종료(sunset) 단계에 있으므로, 새 요구에는 다른 기능이 권장된다는 점도 함께 알아 두어야 합니다.

**주의**: 단계적 종료(Sunset). Foundry Rules의 시계열 기능은 개발 수명 주기상 [sunset](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으며 향후 지원 중단(deprecated)될 예정입니다. 전체 지원은 계속 제공됩니다. 새로운 시계열 규칙 요구 사항에는 워크플로를 [시계열 알림 자동화(time series alerting automations)](https://www.palantir.com/docs/foundry/time-series/alerting-overview/)로 마이그레이션할 것을 권장합니다.

Foundry Rules에서는 데이터셋과 객체를 다루는 것 외에도 시계열 데이터를 사용하는 규칙을 관리할 수 있습니다. Foundry Rules로 사용자는 데이터 안에서 관심 있는 기간을 식별하는 규칙을 작성할 수 있습니다. 이 시간 구간(interval)은 Foundry 규칙에 의해 행으로 출력되며, 알림이나 다른 용도로 하위 단계에서 사용할 수 있습니다. Foundry Rules는 현재 기존 시계열의 변환(예: 집계, 수식, 도함수(derivative) 사용)과 여러 기준에 따른 구간 식별을 지원합니다.

Foundry Rules는 Foundry의 [시계열](https://www.palantir.com/docs/foundry/time-series/time-series-overview/) 위에서 동작하며, [시계열 속성(time series property)](https://www.palantir.com/docs/foundry/time-series/time-series-concepts-glossary/#time-series-property-tsp)과 측정값(measure)을 지원합니다.

Foundry Rules에서 시계열을 사용하려면 [배포 지침](02_deploy-timeseries-foundry-rules.md)을 따르세요.

**설명**: 시계열은 (타임스탬프, 값) 쌍이 시간 순서로 이어진 데이터입니다. 예를 들어 펌프 P-1의 온도 센서가 1초마다 값을 기록하면 `(10:00:00, 71.2), (10:00:01, 71.5), ...` 같은 시계열이 됩니다. 일반 규칙이 "조건에 맞는 행"을 찾는다면, 시계열 규칙은 "조건이 성립한 시간 구간"을 찾습니다. 예: "P-1의 온도가 90도를 넘은 구간은 10:05:12부터 10:07:40까지"라는 결과가 행 하나로 출력됩니다.

<a id="time-series-boards"></a>
## 시계열 보드 (Time series boards)

규칙에는 표준 Foundry Rules [로직](../02_core-concepts/04_rule-logic.md) 전부와 함께 두 종류의 시계열 보드인 **Add Timeseries**와 **Timeseries Search**를 넣을 수 있습니다.

<a id="add-timeseries-board"></a>
### Add Timeseries 보드 (Add Timeseries board)

Add Timeseries 보드는 시계열 하나를 입력으로 받아 변형된 시계열을 만들며, 이 시계열은 이후 보드에서 사용할 수 있습니다. 변환된 시계열은 이름(1)과 연산(2), 그리고 그 연산에 필요한 구성으로 정의됩니다. 예를 들어 아래 보드는 1000일에 걸친 이동 집계(rolling aggregate)로 만든 새 시계열 `$baseline`을 추가합니다. 결과 시계열은 'Preview Timeseries' 버튼(3)으로 미리 볼 수 있습니다.

![add timeseries](https://www.palantir.com/docs/resources/foundry/foundry-rules/add_timeseries.png)

**설명**: 이동 집계는 각 시점마다 그 시점 이전의 일정 기간(창, window) 값을 모아 평균이나 합계를 계산하는 연산입니다. 1000일 이동 평균이라면 오늘의 `$baseline` 값은 지난 1000일 원래 값의 평균이 됩니다. 이렇게 만든 기준선은 다음 보드에서 "현재 값이 기준선보다 20% 높은 구간" 같은 조건에 쓸 수 있습니다.

<a id="timeseries-search-board"></a>
### Timeseries Search 보드 (Timeseries Search board)

Timeseries Search 보드는 지정한 조건에 따라 입력 집합의 모든 객체에 대해 구간을 생성합니다. 조건에서는 원래 루트 객체에 연결된 시계열과, 앞선 **Add Timeseries** 보드에서 만든 모든 시계열을 참조할 수 있습니다. 객체에 존재하는 측정값은 `@` 접두어로, 규칙 안에서 추가한 시계열은 `$` 접두어로 표시됩니다. 조건에 맞는 구간은 'Preview Intervals' 버튼으로 미리 볼 수도 있습니다.

입력의 각 루트 객체마다, 일치하는 구간들이 출력 데이터셋에 구간 데이터(시작 시각, 종료 시각, 지속 시간)를 담은 열들로 나타납니다.

![timeseries search](https://www.palantir.com/docs/resources/foundry/foundry-rules/timeseries_search.png)

**설명**: 예를 들어 루트 객체가 펌프 3대이고 조건이 `@temperature > $baseline * 1.2`라면, 출력 데이터셋은 다음과 같은 행을 가질 수 있습니다.

| pump_id | start_time | end_time | duration |
|---|---|---|---|
| P-1 | 2024-03-01 10:05 | 2024-03-01 10:40 | 35분 |
| P-1 | 2024-03-02 08:00 | 2024-03-02 08:15 | 15분 |
| P-3 | 2024-03-01 22:10 | 2024-03-01 23:00 | 50분 |

P-2는 조건이 성립한 구간이 없어 행이 없습니다. 열 이름은 설명을 위한 예시입니다.

> **중간 요약**: Add Timeseries 보드는 기존 시계열로 새 시계열(`$` 접두어)을 만들고, Timeseries Search 보드는 측정값(`@`)과 새 시계열을 조건에 써서 객체별로 조건이 성립한 시간 구간을 행으로 출력합니다.

## 정리

- Foundry Rules의 시계열 기능은 sunset 단계이며, 새 요구에는 시계열 알림 자동화가 권장됩니다.
- 시계열 규칙은 데이터 안에서 관심 있는 시간 구간을 찾아 행으로 출력합니다.
- 시계열 속성과 측정값을 지원하며, 사용하려면 별도의 배포 절차가 필요합니다.
- Add Timeseries 보드는 집계, 수식, 도함수 등으로 새 시계열을 만들고, Timeseries Search 보드는 조건에 맞는 구간(시작, 종료, 지속 시간)을 객체별로 출력합니다.
