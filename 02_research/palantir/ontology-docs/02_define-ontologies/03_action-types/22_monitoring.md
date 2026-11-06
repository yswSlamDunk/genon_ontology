# 액션 모니터링 (Monitoring)

- 원문: https://www.palantir.com/docs/foundry/action-types/monitoring/
- 사이드바 위치: Define Ontologies > Action types > Monitoring

이 페이지는 액션의 성능과 안정성을 지켜보기 위해 Foundry가 제공하는 모니터링 기능을 설명합니다. 액션이 운영 환경에서 쓰이기 시작하면 "느려지지 않았는가", "실패가 늘지 않았는가"를 사람이 일일이 확인하기 어렵기 때문에, 조건을 정해 두고 넘으면 알림을 받는 방식이 필요합니다. 여기서는 사용할 수 있는 규칙 두 가지와 설정 절차를 다룹니다.

Foundry의 액션은 성능과 안정성을 추적하기 위해 모니터링할 수 있습니다. 이 페이지는 액션에 사용할 수 있는 모니터링 기능을 설명합니다.

<a id="available-monitoring-rules"></a>
## 사용 가능한 모니터링 규칙 (Available monitoring rules)

Foundry의 액션 모니터링은 두 가지 핵심 규칙 유형을 지원합니다.

1. **Action duration p95:** 실행 시간의 95번째 백분위수가 임계값을 넘으면 알림을 보냅니다.
2. **Number of action failures in window:** 일정 기간 안의 실패 횟수가 임계값을 넘으면 알림을 보냅니다.

자세한 설정 옵션과 파라미터는 [모니터링 규칙 참조 문서](https://www.palantir.com/docs/foundry/monitoring-views/rules-reference/#action-rules)를 확인하세요.

**설명**: 95번째 백분위수(p95)는 실행 시간을 짧은 순으로 정렬했을 때 95% 지점에 있는 값입니다. 예를 들어 액션을 100번 실행했다면 빠른 순으로 95번째 실행의 소요 시간이 p95입니다. 평균은 극단적으로 느린 몇 건에 묻히기 쉬운 반면, p95는 "대부분의 사용자가 겪는 최악에 가까운 대기 시간"을 보여 주므로 성능 감시에 자주 쓰입니다.

> **중간 요약**: 액션 모니터링 규칙은 실행 시간 p95와 기간 내 실패 횟수 두 가지이며, 각각 임계값을 넘으면 알림을 보냅니다.

<a id="set-up-action-monitoring"></a>
## 액션 모니터링 설정하기 (Set up action monitoring)

액션 모니터링을 설정하려면, 모니터링 뷰(monitoring view)와 규칙을 만드는 표준 절차를 따릅니다.

1. [모니터링 뷰 개요 문서](https://www.palantir.com/docs/foundry/monitoring-views/overview/#create-a-new-monitoring-view)에 설명된 대로 모니터링 뷰를 만듭니다.
2. [모니터링 규칙 추가](https://www.palantir.com/docs/foundry/monitoring-views/overview/#add-a-monitoring-rule) 섹션에 설명된 대로 액션 또는 액션 타입에 대한 모니터링 규칙을 추가합니다.
3. 적절한 임계값과 심각도(severity) 수준을 설정합니다.
4. [알림 구독 가이드](https://www.palantir.com/docs/foundry/monitoring-views/overview/#subscribe-to-alerts)에 따라 알림 통지를 설정합니다.

![모니터링 알림 설정 예시.](https://www.palantir.com/docs/resources/foundry/action-types/monitoring-alerts.png)

<a id="dynamic-scopes"></a>
### 동적 범위 (Dynamic scopes)

액션 모니터는 **Workflow Lineage**, **Workshop**, **OSDK application**을 동적 범위(dynamic scope)로 지원합니다. 이 범위 중 하나를 선택하면, 모니터는 해당 리소스가 사용하는 모든 액션을 자동으로 추적하고, 액션이 추가되거나 제거되면 별도의 조치 없이 이에 맞춰 조정됩니다.

![액션 타입 모니터의 동적 범위 옵션(Workshop module, Workflow Lineage, Developer Console application 등)을 보여 주는 Select scope 대화 상자.](https://www.palantir.com/docs/resources/foundry/action-types/app-as-dynamic-scope-monitoring.png)

**설명**: 정적 범위는 "액션 타입 X, Y, Z를 감시"처럼 대상을 직접 나열하는 방식입니다. 동적 범위는 "Workshop 모듈 M이 쓰는 모든 액션"처럼 대상을 규칙으로 정하므로, 나중에 모듈 M에 액션 W를 추가하면 모니터도 W를 자동으로 감시하기 시작합니다.

> **중간 요약**: 모니터링 뷰를 만들고 규칙, 임계값, 알림 구독을 차례로 설정합니다. Workshop이나 OSDK 앱 같은 동적 범위를 고르면 그 앱이 쓰는 액션이 자동으로 감시 대상에 포함됩니다.

<a id="related-documentation"></a>
## 관련 문서 (Related documentation)

* [모니터링 규칙 참조](https://www.palantir.com/docs/foundry/monitoring-views/rules-reference/#action-rules)
* [모니터링 뷰 개요](https://www.palantir.com/docs/foundry/monitoring-views/overview/)
* [액션 지표(Action metrics)](25_action-metrics.md)
* [액션 로그(Action log)](26_action-log.md)

## 정리

- 액션 모니터링은 실행 시간 p95와 기간 내 실패 횟수라는 두 규칙을 지원합니다.
- 설정은 모니터링 뷰 생성, 규칙 추가, 임계값과 심각도 설정, 알림 구독 순서로 진행합니다.
- Workflow Lineage, Workshop, OSDK application을 동적 범위로 지정하면 해당 리소스가 쓰는 액션이 자동으로 추적됩니다.
