# Foundry Rules 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/overview/
- 사이드바 위치: Applications > Foundry Rules > Overview

이 페이지는 Foundry Rules가 무엇인지, 규칙(rule)과 조건(condition)이 어떻게 구성되는지, 어떤 업무에 쓰이는지를 소개합니다. Foundry Rules는 코드를 직접 쓰지 않고 화면에서 비즈니스 규칙을 만들어 데이터에 적용하는 도구로, 이후 Foundry Rules 하위 페이지들의 출발점입니다.

Foundry Rules(이전 이름 Taurus)는 사용자가 클릭 위주의 로우코드(low-code) 인터페이스로 Foundry에서 복잡한 비즈니스 로직을 능동적으로 관리할 수 있게 해 줍니다. Foundry Rules를 사용하면 규칙을 만들고, 그 규칙을 데이터셋, 객체, 시계열(time series)에 적용해 알림 생성이나 데이터 분류 같은 다양한 사용 사례에 활용할 수 있습니다.

Foundry Rules는 규칙을 만들고, 관리하고, 적용하기 위한 여러 구성 요소로 이루어져 있습니다.

* **규칙(rule)은** 함께 묶였을 때 데이터셋의 특정 행들을 지정할 수 있는 *조건(condition)들의* 집합입니다.
* 규칙을 이루는 **조건은** 데이터셋의 열에 적용되며, 단순한 필터부터 복잡한 집계(aggregation), 조인, 기타 연산자까지 다양합니다.

![규칙과 조건을 담은 필터 그룹 스크린숏](https://www.palantir.com/docs/resources/foundry/foundry-rules/filter_group.png)

이어지는 페이지들은 여러 [핵심 개념](02_core-concepts/01_core-concepts.md)을 설명하고, Foundry Rules를 [배포](03_deploy/01_deploy-foundry-rules.md)하고 [사용자 정의](04_settings-customization/01_customization.md)하는 방법을 안내합니다.

**설명**: 규칙은 SQL의 `WHERE` 절로 생각하면 정확합니다. 예를 들어 거래 테이블에서 "금액이 1,000만 원 이상이고 해외 송금인 거래"를 고르는 규칙은 `amount >= 10000000 AND is_foreign = true`라는 두 조건의 결합입니다. 조건에는 이런 단순 필터뿐 아니라 "같은 계좌의 최근 7일 거래 합계"처럼 `GROUP BY`가 필요한 집계나 다른 테이블과의 조인도 들어갈 수 있습니다. 차이는 이 조건을 SQL로 쓰지 않고 화면에서 클릭으로 조립한다는 점입니다.

> **중간 요약**: Foundry Rules(이전 이름 Taurus)는 로우코드 화면에서 규칙을 만들어 데이터셋, 객체, 시계열에 적용하는 도구입니다. 규칙은 데이터의 특정 행을 고르는 조건들의 집합이며, 조건은 단순 필터부터 집계와 조인까지 포함할 수 있습니다.

<a id="example-use-cases"></a>
## 사용 사례 예시 (Example use cases)

Foundry Rules는 다음과 같이 복잡한 규칙 집합이 필요한 사용 사례의 관리 과정을 단순하게 만들어 줍니다.

* **자금세탁방지(Anti-Money Laundering, AML):** 거래 건별 메트릭과 집계 메트릭을 모두 겨냥한 규칙으로 의심스러운 거래를 표시(flag)합니다.
* **장비 모니터링(Equipment monitoring):** 센서 데이터를 바탕으로 장비 성능 저하 가능성에 대한 알림을 발생시킵니다(예: 특정 측정값이 일정 값에 도달할 때).
* **코호트 분류(Cohorting):** 규칙에 따라 엔터티를 그룹, 즉 "코호트(cohort)"로 분류합니다. 예를 들어 마케팅 대상을 더 정확히 겨냥하기 위해 특정 특징을 가진 고객 그룹을 만듭니다.

## 정리

- Foundry Rules(이전 이름 Taurus)는 클릭 위주의 로우코드 인터페이스로 비즈니스 규칙을 만들고 관리하는 도구입니다.
- 규칙은 조건들의 집합으로 데이터셋의 특정 행을 지정하며, 조건은 열에 대한 필터, 집계, 조인 등입니다.
- 규칙은 데이터셋, 객체, 시계열에 적용할 수 있으며, 알림 생성과 데이터 분류에 주로 쓰입니다.
- 대표 사용 사례는 자금세탁방지, 장비 모니터링, 고객 코호트 분류입니다.
