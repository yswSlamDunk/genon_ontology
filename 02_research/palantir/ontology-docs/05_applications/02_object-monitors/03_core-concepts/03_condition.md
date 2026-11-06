# 조건 (Conditions)

- 원문: https://www.palantir.com/docs/foundry/object-monitors/condition/
- 사이드바 위치: Applications > Object Monitors [Sunset] > Core concepts > Conditions

이 페이지는 객체 모니터가 언제 반응할지를 정하는 조건(condition)의 세 가지 종류를 설명합니다. 특정 시점에 일어난 일을 잡아내는 이벤트(event) 조건, 참과 거짓 상태가 바뀌는 순간을 잡아내는 임계값(threshold) 조건, 그리고 직접 작성한 함수로 판단하는 함수 기반(function-backed) 조건입니다. 조건 종류에 따라 실시간 평가 지원 여부도 달라집니다.

**주의**: 단계적 종료(Sunset). Object Monitors는 [Automate](https://www.palantir.com/docs/foundry/automate/overview/)로 대체되었습니다. Automate는 이전 버전과 완전히 호환되는 제품으로, 플랫폼의 모든 비즈니스 자동화를 위한 단일 진입점을 제공합니다.

객체 모니터 조건은 새로운 감시 활동이 언제 감지되고 기록될지를 정의합니다. **임계값(Threshold)** 조건은 계속 이어지는 참 또는 거짓 상태를 만들고, **이벤트(event)** 조건은 개별(discrete) 이벤트를 만듭니다. 조건에는 여러 하위 조건이 포함될 수 있으며, 여러 [입력](02_input.md) 객체 집합을 참조할 수 있습니다. 객체 모니터는 다음 조건 유형을 지원합니다.

**설명**: 두 종류의 차이는 출력의 모양에 있습니다. 이벤트 조건은 "10:03에 객체 A 추가, 10:15에 객체 B 추가"처럼 시각이 찍힌 사건 목록을 만듭니다. 임계값 조건은 "합계 > 10,000"이 지금 참인지 거짓인지라는 상태를 만들고, 이 상태가 거짓에서 참으로(또는 그 반대로) 바뀌는 순간만 활동으로 기록합니다. 따라서 합계가 계속 10,000을 넘는 동안에는 새 활동이 기록되지 않습니다.

<a id="event"></a>
## 이벤트 (Event)

이벤트 조건은 가장 흔한 조건 유형입니다. 이벤트 조건에는 입력에 객체가 추가되거나 제거되는 조건과, 지표가 증가하거나 감소하는 조건이 있습니다. 각 이벤트는 특정 시각에 일어나는 개별 이벤트입니다. 따라서 활동 그래프에서 점으로 표시됩니다.

![Object Monitors 앱의 활동 기록 탭](https://www.palantir.com/docs/resources/foundry/object-monitors/activity-history-graph.png)

아래 예시에서 이벤트 조건은 입력 탐색 하나를 사용하며, 그 탐색에 새 객체가 들어오는 시점을 확인합니다. 객체는 새로 생성되었거나, 입력을 정의하는 필터에 맞도록 값이 바뀌어서 추가될 수 있습니다.

![Sales Opportunity 추가 이벤트 조건 예시](https://www.palantir.com/docs/resources/foundry/object-monitors/monitor_event_condition_example.png)

**설명**: 입력이 "금액이 5만 달러 이상인 Sales Opportunity"라면, 객체가 집합에 새로 들어오는 경우는 두 가지입니다. 금액 6만 달러인 영업 기회가 새로 생성된 경우, 그리고 기존에 4만 달러였던 영업 기회의 금액이 5.5만 달러로 수정되어 필터를 새로 만족하게 된 경우입니다. 두 경우 모두 "추가" 이벤트로 감지됩니다.

일부 이벤트 조건에는 임계값 하위 조건이 필요할 수 있습니다. 이런 경우 이벤트가 감지되려면 주 조건과 하위 조건이 모두 참이어야 합니다. 예를 들어 입력 객체 수가 증가하는 시점을 감지하되, 입력 집합에 이미 최소 `N`개의 객체가 있다는 주 조건이 충족될 때만 감지하도록 임계값 하위 조건을 사용할 수 있습니다.

> **중간 요약**: 이벤트 조건은 객체 추가와 제거, 지표 증가와 감소처럼 특정 시각에 일어나는 개별 사건을 감지하며, 필요하면 임계값 하위 조건을 함께 걸어 두 조건이 모두 참일 때만 감지합니다.

<a id="threshold"></a>
## 임계값 (Threshold)

임계값 조건은 입력에 대해 실행되어 시간에 따라 `true` 또는 `false` 상태를 만듭니다. 임계값을 어느 방향으로든 넘을 때 활동이 기록됩니다. 임계값을 쓰는 조건에는 중첩된 하위 조건을 몇 개든 포함할 수 있습니다.

아래는 Object Monitors 애플리케이션의 임계값 조건 예시입니다. 이 예에서 조건은 사용자 지정 코호트(cohort)의 Sales Opportunity들에 걸친 `amount` 합계가 `10,000`보다 커지는 시점을 확인합니다.

![Sales Opportunities 임계값 조건 예시](https://www.palantir.com/docs/resources/foundry/object-monitors/monitor_threshold_condition_example.png)

**참고**: 임계값 조건은 [실시간 평가](04_evaluation.md#realtime-evaluation)를 지원하지 않습니다.

> **중간 요약**: 임계값 조건은 입력에 대한 참과 거짓 상태를 계산하고, 상태가 바뀔 때마다 활동을 기록합니다. 중첩 하위 조건을 둘 수 있지만 실시간 평가는 지원하지 않습니다.

<a id="function-backed"></a>
## 함수 기반 (Function-backed)

함수 기반 조건은 이벤트나 임계값 규칙 옵션으로 지원되지 않는 것을 포함해 더 복잡한 조건을 정의할 수 있도록 설계되었습니다. 함수 기반 조건은 `true` 또는 `false`의 불리언(Boolean) 값을 반환하는 함수(function)를 정의하고 게시(publish)하는 방식으로 동작합니다. 모니터가 평가될 때 이 함수가 호출되며, 응답은 그 실행의 결과를 나타내야 합니다. 상태가 바뀌었다면 이벤트가 기록됩니다.

함수는 감시 대상 객체 타입의 `ObjectSet<>`을 받아, 조건이 충족되었는지를 나타내는 불리언 값을 반환해야 합니다. Object Monitors에서 사용할 [함수 작성 방법](../../../02_define-ontologies/04_functions/08_function-consumption/01_use-functions.md)을 더 알아봅니다.

아래 예시는 함수를 사용해, Sales Opportunity 객체 입력 집합에서 `realized_amount`의 합계가 `expected_amount`의 합계보다 작은 시점을 계산합니다.

![함수 기반 Sales Opportunity 조건 예시](https://www.palantir.com/docs/resources/foundry/object-monitors/monitor_function_backed_condition_example.png)

```
@Function()
/**
 * 영업 기회 집합의 실현 금액(amountRealized) 합계가
 * 전체 기회 금액(amount) 합계보다 작은지 계산합니다.
 */
public async calculateOpportunityUnderRealized(opportunities: ObjectSet<SalesOpportunity>): Promise<boolean> {
    let amount = await opportunities.sum(o => o.amount)
    let amountRealized = await opportunities.sum(o => o.amountRealized)
    if (amount !== null && amountRealized !== null && amountRealized < amount) {
        return true
    } else {
        return false
    }
}
```

**설명**: TypeScript로 작성된 함수입니다. 입력은 `SalesOpportunity` 객체 집합(`ObjectSet<SalesOpportunity>`)이고 출력은 `Promise<boolean>`, 즉 비동기로 계산되는 참 또는 거짓입니다. `opportunities.sum(o => o.amount)`는 집합 안 모든 객체의 `amount` 속성을 더하는 집계로, SQL의 `SELECT SUM(amount) FROM opportunities`에 해당합니다. 두 합계가 모두 값이 있고(`null`이 아니고) 실현 금액 합계가 전체 금액 합계보다 작으면 `true`를 반환합니다. 모니터는 평가할 때마다 이 함수를 호출하고, 반환값이 직전 평가와 달라졌을 때 이벤트를 기록합니다. `@Function()` 데코레이터는 이 메서드를 Foundry에 함수로 게시하겠다는 표시입니다.

**참고**: 함수 기반 조건은 [실시간 평가](04_evaluation.md#realtime-evaluation)를 지원하지 않습니다. 또한 함수 기반 조건은 임계값 조건에서만, 그리고 불리언 값 하나를 출력하는 방식으로만 사용할 수 있습니다.

> **중간 요약**: 함수 기반 조건은 객체 집합을 받아 불리언 하나를 반환하는 함수를 게시해 만들며, 반환값이 바뀔 때 이벤트가 기록됩니다. 임계값 방식으로만 쓸 수 있고 실시간 평가는 지원하지 않습니다.

## 정리

- 조건은 모니터가 언제 활동을 감지하고 기록할지 정하며, 여러 하위 조건과 여러 입력을 참조할 수 있습니다.
- 이벤트 조건은 객체 추가와 제거, 지표 증가와 감소 같은 개별 사건을 만들며 가장 흔히 쓰입니다.
- 임계값 조건은 참과 거짓 상태를 만들고 경계를 넘을 때 활동을 기록하며, 실시간 평가를 지원하지 않습니다.
- 함수 기반 조건은 `ObjectSet<>`을 받아 불리언을 반환하는 함수로 복잡한 조건을 표현하며, 임계값 방식으로만 동작하고 실시간 평가를 지원하지 않습니다.
