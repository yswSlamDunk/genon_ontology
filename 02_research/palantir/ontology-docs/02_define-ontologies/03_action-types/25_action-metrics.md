# 액션 지표 (Action metrics)

- 원문: https://www.palantir.com/docs/foundry/action-types/action-metrics/
- 사이드바 위치: Define Ontologies > Action types > Action metrics

이 페이지는 액션 타입이 최근 30일 동안 얼마나 쓰였고 얼마나 성공하거나 실패했는지, 얼마나 오래 걸렸는지를 보여 주는 액션 지표(action metrics)를 설명합니다. 지표를 어디서 볼 수 있는지, 실패가 어떤 유형으로 분류되는지, 보려면 어떤 권한이 필요한지를 다룹니다.

액션 지표는 최근 30일 동안 액션 타입의 사용 현황을 거의 실시간으로 보여 줍니다. 이 지표는 [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)의 액션 타입 개요 페이지에서, 또는 [Workflow Lineage](https://www.palantir.com/docs/foundry/workflow-lineage/overview/)에서 특정 실행의 액션 노드를 선택해서 볼 수 있습니다. 다음 지표를 사용할 수 있습니다.

* **성공/실패 지표(Success/failure metrics):** 성공 및 실패 횟수로 액션의 현재 상태를 모니터링합니다. 이를 통해 문제를 빠르게 식별하고 선제적으로 문제를 해결할 수 있어, 실패가 발생하는 즉시 대응할 수 있습니다.
* **P95 소요 시간 지표(P95 duration metric):** 각 액션 타입의 95번째 백분위수(P95) 실행 시간을 추적합니다. 이 지표는 실행 시간의 상위 범위를 보여 주므로, 성능 병목을 찾아내고 워크플로가 일관되고 효율적으로 동작하도록 최적화하는 데 도움이 됩니다.

최근 7일 동안 특정 액션의 실행 내역 전체를 보여 주는 [실행 기록(run history)](https://www.palantir.com/docs/foundry/aip-observability/run-history/)에도 접근할 수 있습니다. [온톨로지와 AIP의 관측 가능성(observability) 기능](https://www.palantir.com/docs/foundry/aip-observability/overview/)에 대해 더 알아보세요.

![개요 섹션의 액션 지표 화면.](https://www.palantir.com/docs/resources/foundry/action-types/action-metrics-failures.png)

모든 지표는 Foundry Telemetry Service(FTS)의 최신 데이터를 사용해 거의 실시간으로 업데이트됩니다. 따라서 액션을 모니터링하고, 디버깅하고, 건강한 상태로 유지하는 데 필요한 최신 정보를 얻을 수 있습니다.

또한 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)의 [Observability Chart 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-observability-chart/)을 사용해 운영 애플리케이션 안에 액션 지표를 직접 넣어, 워크플로의 나머지 부분과 함께 리소스 상태를 모니터링할 수 있습니다.

**설명**: 지표(metrics)는 집계된 숫자(성공 1,200건, 실패 3건, P95 850ms 등)이고, 실행 기록이나 로그는 개별 실행 한 건 한 건의 기록입니다. 지표로 이상 징후를 발견하고, 실행 기록에서 실패한 구체적인 실행을 찾아 원인을 확인하는 식으로 함께 씁니다. P95의 의미는 [액션 모니터링](22_monitoring.md) 페이지의 설명을 참고하세요.

> **중간 요약**: 액션 지표는 최근 30일의 성공/실패 횟수와 P95 실행 시간을 거의 실시간으로 보여 주며, Ontology Manager, Workflow Lineage, Workshop 위젯에서 볼 수 있습니다. 개별 실행 내역은 최근 7일치 실행 기록에서 확인합니다.

<a id="action-failure-types"></a>
## 액션 실패 유형 (Action failure types)

액션 지표를 표시하는 데 [액션 로그](26_action-log.md)가 필요하지는 않습니다. 액션 로그와 달리 액션 지표는 실패를 추적합니다.

액션 지표에는 표시될 수 있는 여러 실패 범주가 있습니다. 범주는 다음과 같습니다.

* **잘못된 파라미터 실패(Invalid parameter failure):** 액션의 맥락에서 유효하지 않은 파라미터를 하나 이상 포함해 액션이 제출되었습니다.
* **규모 한도 실패(Scale limit failure):** 액션이 허용된 객체 타입 한도(기본적으로 보통 10,000개)를 넘는 대상에 영향을 주었습니다.
* **인증 실패(Authentication failure):** 사용자가 액션의 보안 제출 조건(submission criteria)을 통과하지 못했습니다.
* **부수 효과 실패(Side effect failure):** 웹훅이나 잘못 설정된 부수 효과 때문에 액션이 실패했습니다.
* **함수 실패(Function failure):** 기반 함수가 실패해서 액션이 실패했습니다. 이 실패 유형은 함수 기반 액션에서만 발생할 수 있습니다.
* **사용자 대상 함수 실패(User-facing function failure):** 액션을 뒷받침하는 함수가 사용자에게 표시할 목적의 오류를 던졌습니다. 이 실패 유형은 함수 기반 액션에서만 발생할 수 있습니다.
* **충돌 실패(Conflict failure):** 동시 수정 같은 충돌 때문에 액션이 실패했습니다.
* **미분류 실패(Unclassified failure):** 위 범주 어디에도 속하지 않는 액션 실패입니다.

**설명**: 규모 한도 실패에 대해 원문은 "객체 타입(object types)의 한도"라고 표현했지만, 문맥상 한 번의 액션이 편집할 수 있는 객체 수의 한도를 뜻하는 것으로 읽힙니다. 충돌 실패는 [일관성과 격리](21_consistency-guarantees.md) 페이지에서 설명한 쓰기-쓰기 충돌을 말합니다. 사용자 대상 함수 실패는 함수 작성자가 "재고가 부족합니다"처럼 사용자에게 보여 줄 메시지를 담아 일부러 던진 오류이므로, 코드 버그로 인한 일반 함수 실패와 구분됩니다.

> **중간 요약**: 액션 지표는 액션 로그 없이도 실패를 추적하며, 실패를 파라미터, 규모 한도, 인증, 부수 효과, 함수, 사용자 대상 함수, 충돌, 미분류의 8개 범주로 나눕니다.

<a id="permissions"></a>
## 권한 (Permissions)

액션 지표를 보려면 그 액션에 대해 `viewer` 권한이 있어야 합니다.

## 정리

- 액션 지표는 최근 30일간 액션 타입의 성공/실패 횟수와 P95 실행 시간을 FTS 데이터로 거의 실시간 표시합니다.
- Ontology Manager의 액션 타입 개요, Workflow Lineage의 액션 노드, Workshop의 Observability Chart 위젯에서 볼 수 있고, 최근 7일 실행 기록도 제공됩니다.
- 실패는 8개 범주로 분류되며, 액션 로그 설정과 무관하게 추적됩니다.
- 지표를 보려면 액션에 대한 `viewer` 권한이 필요합니다.
