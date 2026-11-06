# 함수 지표 (Function metrics)

- 원문: https://www.palantir.com/docs/foundry/functions/function-metrics/
- 사이드바 위치: Define Ontologies > Functions > Function consumption > Function metrics

이 페이지는 배포된 함수(function)가 실제로 얼마나 호출되고, 얼마나 성공하거나 실패하며, 얼마나 오래 걸리는지를 보여 주는 함수 지표를 설명합니다. 함수를 만들어 공개한 뒤에는 운영 중 상태를 지켜봐야 문제를 빨리 찾을 수 있으므로, 어떤 지표가 있고 실패가 어떤 범주로 나뉘는지 알아 두면 디버깅에 도움이 됩니다.

함수 지표는 함수 타입의 최근 30일간 사용량을 거의 실시간으로 보여 줍니다. 이 지표는 [Ontology Manager](../../../05_applications/04_ontology-manager/01_overview.md)의 [함수 타입 개요](../../../05_applications/04_ontology-manager/01_overview.md#function-type-view) 페이지에서 볼 수 있고, [Workflow Lineage](https://www.palantir.com/docs/foundry/workflow-lineage/overview/)에서 특정 실행에 대한 함수 노드를 선택해서도 볼 수 있습니다. 제공되는 지표는 다음과 같습니다.

* **성공/실패 지표:** 성공 횟수와 실패 횟수로 함수의 현재 상태를 모니터링합니다. 이를 통해 문제를 빠르게 파악하고 선제적으로 문제를 해결할 수 있어, 실패가 발생하는 즉시 대응할 수 있습니다.
* **P95 소요 시간 지표:** 함수 타입별 실행 소요 시간의 95번째 백분위수(P95)를 추적합니다. 이 지표는 실행 시간의 상위 구간을 드러내므로, 성능 병목을 찾아내고 워크플로가 일관되고 효율적으로 동작하도록 최적화하는 데 도움이 됩니다.

**설명**: P95 소요 시간은 실행 시간을 짧은 순서로 늘어놓았을 때 95%에 해당하는 위치의 값입니다. 예를 들어 실행 100번 중 95번이 0.8초 이내에 끝났다면 P95는 약 0.8초입니다. 평균은 대부분 빠른 실행에 가려져 가끔 발생하는 느린 실행이 잘 보이지 않지만, P95는 "느린 쪽 끝"이 얼마나 느린지를 보여 주므로 성능 문제를 찾는 데 더 유용합니다.

또한 [실행 기록(run history)](https://www.palantir.com/docs/foundry/aip-observability/run-history/)에도 접근할 수 있으며, 여기서는 특정 함수의 최근 7일간 실행 전체를 볼 수 있습니다. [온톨로지와 AIP 관측 가능성(observability)](https://www.palantir.com/docs/foundry/aip-observability/overview/)에 대해 더 알아보세요.

![개요 섹션의 함수 지표 스크린샷.](https://www.palantir.com/docs/resources/foundry/functions/function-metrics.png)

모든 지표는 Foundry Telemetry Service(FTS)의 최신 데이터를 사용해 거의 실시간으로 갱신됩니다. 따라서 함수를 모니터링하고, 디버깅하고, 상태를 유지하는 데 필요한 가장 최신 정보를 얻을 수 있습니다.

[Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)의 [Observability Chart 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-observability-chart/)을 사용하면 함수 지표를 운영 애플리케이션 안에 직접 넣어, 워크플로의 나머지 부분과 함께 리소스 상태를 모니터링할 수도 있습니다.

> **중간 요약**: 함수 지표는 최근 30일간의 성공/실패 횟수와 P95 실행 시간을 거의 실시간으로 보여 주며, Ontology Manager, Workflow Lineage, Workshop 위젯에서 볼 수 있습니다. 개별 실행 내역은 실행 기록에서 최근 7일분을 확인합니다.

<a id="function-failure-types"></a>
## 함수 실패 유형 (Function failure types)

함수 지표에는 여러 범주의 실패가 표시될 수 있습니다. 범주는 다음과 같습니다.

* **Runtime failure(런타임 실패):** 함수를 실행하는 도중 예기치 않은 오류가 발생했습니다. 대개 함수 코드의 버그나 처리되지 않은 상황 때문입니다.
* **Resource limit exceeded(리소스 한도 초과):** 함수가 허용 한도를 넘는 객체 타입에 영향을 주었습니다(기본값은 보통 10,000).
* **User facing error(사용자 대상 오류):** 사용자에게 보여 주려는 목적으로 의도된 오류가 발생했습니다. 보통 무엇이 잘못되었는지, 어떻게 고칠 수 있는지 안내합니다.
* **Invalid inputs error(잘못된 입력 오류):** 함수에 제공된 입력 중 하나 이상이 유효하지 않거나 요구 조건을 충족하지 않았습니다.
* **Invalid output error(잘못된 출력 오류):** 함수가 유효하지 않거나 기대하는 형식 또는 규칙을 따르지 않는 출력을 만들었습니다.
* **Data loading not allowed error(데이터 로딩 불허 오류):** 함수 실행이 객체, 객체 집합(object set), 사용자, 그룹 같은 데이터를 로드하려 했지만 그렇게 하도록 허용되지 않았습니다.
* **Undeclared object types edited error(선언되지 않은 객체 타입 편집 오류):** 함수 실행이 함수 명세(spec)에 선언되지 않은 객체 타입의 객체를 수정, 생성, 삭제하려 했습니다.
* **Structured error(구조화된 오류):** 함수 실행 중 함수 명세에 정의된 구조화된 오류가 발생했습니다.
* **Deployment error(배포 오류):** 함수의 배포에 문제가 있어 함수 실행이 실패했습니다.
* **Consistent snapshot error(일관된 스냅숏 오류):** 일관된 스냅숏 오류로 함수 실행이 실패했습니다.

**설명**: 이 범주는 크게 두 갈래로 볼 수 있습니다. Runtime failure처럼 코드 자체의 결함에서 오는 실패가 있고, Invalid inputs error나 Undeclared object types edited error처럼 함수가 미리 선언한 계약(입력 타입, 편집할 수 있는 객체 타입 목록 등)을 어긴 경우가 있습니다. 함수 명세(spec)는 함수의 이름, 입력과 출력 타입, 편집 대상 객체 타입처럼 함수 바깥에 공개되는 정의를 말하며, 프로그래밍 언어의 함수 시그니처에 해당하는 정보에 몇 가지가 더해진 것입니다. 실패 유형을 보면 코드를 고쳐야 하는지, 호출하는 쪽의 입력이나 설정을 고쳐야 하는지 구분하는 데 도움이 됩니다.

> **중간 요약**: 함수 실패는 런타임 오류, 리소스 한도 초과, 입력 및 출력 오류, 데이터 로딩이나 객체 편집 권한 관련 오류, 배포 오류 등 10가지 범주로 나뉘어 표시됩니다.

<a id="set-up-monitoring-alerts"></a>
## 모니터링 알림 설정 (Set up monitoring alerts)

성능이 떨어지거나 실패가 발생했을 때 알림을 받도록 모니터링 규칙을 구성할 수도 있습니다. 함수 모니터링은 P95 함수 소요 시간과, 일정 시간 구간 안의 함수 실패 횟수에 대한 알림을 지원합니다. 구성 방법은 [함수 모니터링](../07_function-management/04_monitoring.md)을 참고하세요.

<a id="permissions"></a>
## 권한 (Permissions)

함수 지표를 보려면 해당 함수에 대해 `viewer` 권한이 있어야 합니다.

## 정리

- 함수 지표는 함수 타입의 최근 30일 사용량을 거의 실시간(FTS 데이터 기반)으로 보여 줍니다.
- 주요 지표는 성공/실패 횟수와 P95 실행 소요 시간이며, 실행 기록에서는 최근 7일간의 개별 실행을 볼 수 있습니다.
- Ontology Manager의 함수 타입 개요, Workflow Lineage, Workshop의 Observability Chart 위젯에서 지표를 확인할 수 있습니다.
- 실패는 런타임 실패, 리소스 한도 초과, 입력과 출력 오류 등 10가지 유형으로 분류됩니다.
- P95 소요 시간과 실패 횟수에 대한 알림을 설정할 수 있고, 지표를 보려면 함수의 `viewer` 권한이 필요합니다.
