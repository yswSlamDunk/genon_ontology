# 함수 모니터링 (Function monitoring)

- 원문: https://www.palantir.com/docs/foundry/functions/monitoring/
- 사이드바 위치: Define Ontologies > Functions > Function management > Function monitoring

이 페이지는 운영 중인 함수(function)의 성능과 안정성을 지켜보고, 실행 시간이나 실패 횟수가 기준을 넘으면 알림을 받도록 설정하는 방법을 설명합니다. 함수는 Workshop 모듈이나 OSDK 애플리케이션 뒤에서 호출되므로, 함수가 느려지거나 실패하면 사용자 화면이 바로 영향을 받습니다. 그래서 문제가 생겼을 때 사람이 먼저 알아챌 수 있도록 모니터링 규칙을 거는 것이 중요합니다.

Foundry의 함수는 성능과 안정성을 추적하도록 모니터링할 수 있습니다. 이 페이지는 함수에 사용할 수 있는 모니터링 기능을 설명합니다.

Ontology Manager에서는 함수 타입별 성공 및 실패 횟수와 P95 실행 시간을 포함한 실시간 [함수 지표(function metrics)](../08_function-consumption/02_function-metrics.md)도 볼 수 있습니다.

<a id="available-monitoring-rules"></a>
## 사용 가능한 모니터링 규칙 (Available monitoring rules)

Foundry의 함수 모니터링은 다음 규칙 유형을 지원합니다.

1. **Function duration p95(함수 실행 시간 p95):** 실행 시간의 95번째 백분위수가 임계값을 넘으면 알림을 보냅니다.
2. **Number of function failures in window(구간 내 함수 실패 횟수):** 일정 기간 안의 전체 실패 횟수가 임계값을 넘으면 알림을 보냅니다. 이 규칙은 모든 실패 유형을 추적합니다.
3. **Number of user-facing function failures in window(구간 내 사용자 대상 함수 실패 횟수):** 일정 기간 안의 사용자 대상(user-facing) 실패 횟수가 임계값을 넘으면 알림을 보냅니다. 이 규칙은 함수 코드가 던진 사용자 대상 오류만 추적합니다.
4. **Number of non-user-facing function failures in window(구간 내 비사용자 대상 함수 실패 횟수):** 일정 기간 안의 비사용자 대상 실패 횟수가 임계값을 넘으면 알림을 보냅니다. 이 규칙은 사용자 대상 오류를 제외하므로 인프라와 시스템 수준의 실패를 모니터링하는 데 유용합니다.

각 규칙 유형의 자세한 설정 옵션과 파라미터는 [모니터링 규칙 참조 문서](https://www.palantir.com/docs/foundry/monitoring-views/rules-reference/#function-rules)를 확인하세요.

**설명**: p95(95번째 백분위수)는 실행 시간을 짧은 순서로 정렬했을 때 95% 지점에 있는 값입니다. 예를 들어 100번 호출의 실행 시간을 정렬해 95번째 값이 1.2초라면, 호출의 95%는 1.2초 이내에 끝났다는 뜻입니다. 평균은 아주 느린 몇 건에 끌려 올라가거나 묻히기 쉬워서, 대부분의 사용자가 겪는 응답 시간을 볼 때는 p95 같은 백분위수를 많이 씁니다. 사용자 대상 오류는 함수 코드가 의도적으로 던져 사용자에게 메시지로 보여 주는 오류(예: "입력 날짜가 과거입니다")이고, 비사용자 대상 오류는 메모리 부족, 시간 초과, 내부 서비스 장애처럼 코드 의도와 무관하게 발생하는 실패를 가리킵니다.

> **중간 요약**: 함수 모니터링 규칙은 p95 실행 시간, 전체 실패 횟수, 사용자 대상 실패 횟수, 비사용자 대상 실패 횟수의 네 가지이며, 각각 임계값을 넘으면 알림을 보냅니다.

<a id="set-up-function-monitoring"></a>
## 함수 모니터링 설정하기 (Set up function monitoring)

함수 모니터링을 설정하려면 모니터링 뷰(monitoring view)와 규칙을 만드는 표준 절차를 따릅니다.

1. [모니터링 뷰 개요 문서](https://www.palantir.com/docs/foundry/monitoring-views/overview/#create-a-new-monitoring-view)에 설명된 대로 모니터링 뷰를 만듭니다.
2. [모니터링 규칙 추가](https://www.palantir.com/docs/foundry/monitoring-views/overview/#add-a-monitoring-rule) 섹션에 설명된 대로 함수용 모니터링 규칙을 추가합니다.
3. 적절한 임계값과 심각도 수준(severity level)을 설정합니다.
4. [알림 구독 가이드](https://www.palantir.com/docs/foundry/monitoring-views/overview/#subscribe-to-alerts)에 따라 알림 통지를 설정합니다.

![모니터링 알림 설정 예시.](https://www.palantir.com/docs/resources/foundry/functions/monitoring-alerts.png)

<a id="dynamic-scopes"></a>
### 동적 범위 (Dynamic scopes)

함수 모니터는 **Workflow Lineage**, **Workshop**, **OSDK application**을 동적 범위(dynamic scope)로 지원합니다. 이 범위 중 하나를 선택하면, 모니터가 해당 리소스가 사용하는 모든 함수를 자동으로 추적하고, 함수가 추가되거나 제거되면 별도 조작 없이 추적 대상을 조정합니다.

![함수 모니터의 동적 범위 옵션을 보여 주는 범위 선택 대화 상자.](https://www.palantir.com/docs/resources/foundry/functions/functions-app-as-dynamic-scope-monitoring.png)

**설명**: 동적 범위를 쓰지 않으면 감시할 함수를 하나씩 직접 골라야 하고, 애플리케이션이 새 함수를 쓰기 시작해도 모니터에는 반영되지 않습니다. 예를 들어 Workshop 모듈 하나를 범위로 지정해 두면, 그 모듈이 나중에 함수 `getOpenOrders`를 새로 호출하도록 바뀌었을 때 이 함수도 자동으로 감시 대상에 들어갑니다.

> **중간 요약**: 모니터링 뷰를 만들고 함수 규칙, 임계값, 심각도, 알림 구독을 차례로 설정합니다. Workshop, OSDK 애플리케이션, Workflow Lineage를 동적 범위로 지정하면 그 리소스가 쓰는 함수가 자동으로 감시 대상이 됩니다.

<a id="related-documentation"></a>
## 관련 문서 (Related documentation)

* [모니터링 규칙 참조](https://www.palantir.com/docs/foundry/monitoring-views/rules-reference/#function-rules)
* [모니터링 뷰 개요](https://www.palantir.com/docs/foundry/monitoring-views/overview/)
* 알림을 위한 [외부 시스템 연동](https://www.palantir.com/docs/foundry/monitoring-views/external-systems/)

## 정리

- 함수 모니터링은 성능(p95 실행 시간)과 안정성(실패 횟수)을 기준으로 알림을 보내는 기능입니다.
- 실패 규칙은 전체, 사용자 대상(코드가 던진 오류), 비사용자 대상(인프라와 시스템 오류)으로 나누어 걸 수 있습니다.
- 설정은 모니터링 뷰 생성, 규칙 추가, 임계값과 심각도 설정, 알림 구독 순서로 진행합니다.
- 동적 범위를 쓰면 Workshop, OSDK 애플리케이션 등이 사용하는 함수 목록 변화를 모니터가 자동으로 따라갑니다.
