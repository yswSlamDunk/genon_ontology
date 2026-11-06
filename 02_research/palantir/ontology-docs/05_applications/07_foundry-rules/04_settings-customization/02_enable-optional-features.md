# 선택 기능 활성화 (Enable optional features)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/enable-optional-features/
- 사이드바 위치: Applications > Foundry Rules > Settings & customization > Enable optional features

이 페이지는 규칙 작성자가 쓸 수 있는 로직 보드(logic board)의 종류와 부가 기능을 켜고 끄는 방법을 설명합니다. 어떤 변환(윈도, 집계, 조인 등)을 사용자에게 열어 줄지 정하는 설정입니다.

선택 기능은 [Rules Workshop 애플리케이션](../02_core-concepts/03_workshop-application.md) 안에서 Rule Editor 위젯의 구성을 편집해 활성화하거나 비활성화할 수 있습니다. 아래 스크린샷을 참고하세요.

![선택 기능 구성](https://www.palantir.com/docs/resources/foundry/foundry-rules/enable_optional_features.png)

Foundry Rules에서 활성화하거나 비활성화할 수 있는 선택 로직 보드는 다음과 같습니다.

* **Window board:** [윈도 함수(Window functions) ↗](https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-window.html)를 지원합니다.
* **Aggregation board:** 그룹화한 열에 대해 집계를 계산합니다.
* **Join board:** 추가 데이터셋이나 객체를 조인합니다.
* **Expression board:** 열을 추가하거나 필터링하기 위해 임의의 표현식을 실행합니다.
* **Select columns board:** 다음 로직 보드로 넘길 열의 일부를 선택합니다.
* **Union board:** 추가 데이터셋이나 객체를 유니온(union)합니다.

**설명**: 각 보드는 SQL 연산과 직접 대응합니다. Aggregation은 `GROUP BY ... COUNT/SUM`, Join은 `JOIN`, Expression은 `SELECT ..., price * qty AS total` 같은 계산 열 또는 `WHERE` 조건, Select columns는 `SELECT` 열 목록, Union은 `UNION`입니다. 윈도 함수는 행을 줄이지 않고 그룹 안에서 계산하는 함수로, 예를 들어 `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ts)`는 고객별 거래에 1, 2, 3... 순번을 붙입니다.

또한 Contour에서 규칙을 가져오는 기능을 활성화하거나 비활성화하는 옵션이 있습니다.

* **Contour import:** [Contour 분석](https://www.palantir.com/docs/foundry/contour/core-concepts/)에 저장된 로직을 가져와 규칙으로 변환합니다.

마지막으로 Foundry Rules는 시계열 데이터 위에 직접 규칙을 작성하는 기능을 지원합니다.

* **Time series:** 규칙의 일부로 시계열을 직접 다룰 수 있는 [시계열 보드](../05_time-series/01_timeseries-concepts.md#add-timeseries-board)를 추가합니다.

## 정리

- 선택 기능은 Workshop의 Rule Editor 위젯 구성에서 켜고 끕니다.
- 선택 로직 보드에는 Window, Aggregation, Join, Expression, Select columns, Union 보드가 있습니다.
- Contour 분석의 로직을 규칙으로 가져오는 Contour import 기능을 켤 수 있습니다.
- 시계열 데이터에 직접 규칙을 쓰는 Time series 보드도 선택 기능으로 제공됩니다.
