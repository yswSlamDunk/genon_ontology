# 스케줄 빌드 트리거 (Trigger schedule build)

- 원문: https://www.palantir.com/docs/foundry/action-types/trigger-schedule-build/
- 사이드바 위치: Define Ontologies > Action types > Trigger schedule build

이 페이지는 액션이 적용될 때 데이터 파이프라인의 스케줄 빌드를 시작하도록 하는 스케줄 규칙(schedule rule)을 설명합니다. 스케줄 규칙의 설정 방법, 권한이 어떻게 위임되는지, 그리고 트리거된 빌드의 진행 상황을 객체 속성에 기록해 추적하는 방법을 다룹니다. 최종 사용자가 데이터 파이프라인 도구를 열지 않고도 액션 버튼 하나로 데이터셋 재계산을 요청할 수 있게 해 줍니다.

[스케줄(schedule)은](https://www.palantir.com/docs/foundry/data-integration/schedules/) Foundry가 [빌드(build)의](https://www.palantir.com/docs/foundry/data-integration/builds/) 일부로 다시 계산하는 리소스 집합을 정의합니다. 액션 타입에 **스케줄 규칙(schedule rule)을** 설정하면 액션이 적용될 때마다 그 스케줄의 빌드를 트리거할 수 있습니다. 이를 통해 사용자가 [Data Lineage](https://www.palantir.com/docs/foundry/data-lineage/overview/)나 [Builds 애플리케이션](https://www.palantir.com/docs/foundry/data-integration/application-reference/#builds)으로 이동하지 않고도, 온톨로지의 최종 사용자 업무 흐름에서 데이터셋을 다시 계산할 수 있습니다.

액션 타입에 스케줄 규칙이 있으면, 액션의 온톨로지 편집(edit)은 빌드가 시작된 *후에* 적용됩니다. 편집은 빌드가 끝나기를 기다리지 않습니다. 대신 액션은 빌드를 트리거하고, 스케줄 실행 RID(schedule run RID)를 기록한 다음, 온톨로지 편집을 포함한 나머지 규칙을 즉시 적용합니다.

**설명**: Foundry에서 데이터셋은 원천 데이터에서 변환(transform) 코드를 거쳐 만들어지며, 빌드는 이 변환을 실제로 실행해 데이터셋을 새로 계산하는 작업입니다. 스케줄은 "어떤 데이터셋들을 어떤 조건에서 빌드할지"를 묶어 둔 설정입니다. 실행 순서를 정리하면 (1) 액션 적용, (2) 스케줄 빌드 시작 요청, (3) 실행 RID 기록, (4) 빌드 완료를 기다리지 않고 나머지 규칙과 온톨로지 편집 적용입니다. 따라서 액션이 성공했다고 해서 빌드가 끝났거나 성공했다는 뜻은 아닙니다.

<a id="configure-a-schedule-rule"></a>
## 스케줄 규칙 설정하기 (Configure a schedule rule)

액션 타입에 스케줄 규칙을 추가하고 스케줄을 선택합니다. 스케줄은 [프로젝트 범위 모드(project-scoped mode)여야](https://www.palantir.com/docs/foundry/data-integration/schedules/#project-scope) 합니다.

![Ontology Manager의 액션 타입 설정 페이지. 스케줄 규칙을 추가하는 중입니다.](https://www.palantir.com/docs/resources/foundry/action-types/advanced-schedule-action-type-rule.png)

선택한 스케줄이 [파라미터화(parameterized)되어](https://www.palantir.com/docs/foundry/building-pipelines/parameterization/) 있다면 각 스케줄 파라미터에 값을 제공해야 합니다. 액션이 적용되면 확정된 파라미터 값이 스케줄로 전달되고, 다시 빌드 안의 파라미터화된 변환(transform)으로 전달됩니다.

스케줄 규칙은 [병렬화된 파라미터화 스케줄(parallelized parameterized schedules)과](https://www.palantir.com/docs/foundry/building-pipelines/parameterization/#parallelized-mode-advanced) 함께 쓸 때 특히 유용합니다. 병렬화된 스케줄에 온톨로지의 액션을 사용하는 방법에 대해서는 [파라미터화 문서](https://www.palantir.com/docs/foundry/building-pipelines/parameterization/#use-action-types-for-parallelized-schedules)를 참고하세요.

**설명**: 파라미터화된 스케줄은 함수에 인자를 넘기듯 빌드에 값을 넘길 수 있는 스케줄입니다. 예를 들어 `region` 파라미터를 받는 스케줄이라면, 액션 파라미터로 받은 "EMEA"를 스케줄 파라미터에 연결해 해당 지역의 데이터만 다시 계산하게 할 수 있습니다.

> **중간 요약**: 액션 타입에 스케줄 규칙을 추가하고 프로젝트 범위 모드의 스케줄을 선택합니다. 파라미터화된 스케줄이면 액션 적용 시 파라미터 값을 넘겨 빌드 안의 변환까지 전달합니다.

<a id="permissions"></a>
## 권한 (Permissions)

액션을 통해 스케줄을 트리거하는 데 필요한 권한은 액션의 [제출 조건(submission criteria)이](08_submission-criteria.md) 관리합니다. 사용자가 액션 제출 조건을 충족하면, 스케줄에 대한 직접 권한이 없어도 스케줄을 실행할 수 있습니다.

**주의**: Foundry는 스케줄이 처음 참조될 때와 스케줄 규칙이 편집될 때마다 사용자가 그 스케줄을 실행할 권한이 있는지 확인합니다. 액션 타입에서 스케줄을 참조하면, 스케줄 실행에 대한 통제권이 스케줄에서 액션 타입으로 위임됩니다. 그 후에는 액션 타입의 액션을 관리할 수 있는 사람이 누가 스케줄을 트리거할 수 있는지를 통제하게 됩니다.

**설명**: 권한 검사는 두 시점에 일어납니다. 설정 시점에는 액션 타입을 만드는 사람이 스케줄 실행 권한을 가지고 있는지 확인하고, 실행 시점에는 최종 사용자가 액션의 제출 조건을 만족하는지만 확인합니다. 즉, 스케줄 실행 권한이 있는 사람이 "이 액션의 제출 조건을 통과한 사람은 스케줄을 돌려도 된다"고 위임하는 구조입니다.

<a id="track-build-progress"></a>
## 빌드 진행 상황 추적하기 (Track build progress)

스케줄 규칙이 트리거되면 그 결과로 생긴 스케줄 실행은 **스케줄 실행 RID(schedule run RID)로** 식별됩니다. 이 RID는 액션 타입의 온톨로지 편집 규칙에서 참조할 수 있는 값으로 제공되므로, 편집 대상 객체의 문자열(string) 속성에 이 값을 기록할 수 있습니다. 액션이 트리거한 빌드의 기록을 객체에 남기고 싶을 때 유용합니다.

스케줄 실행 RID를 기록하려면 같은 액션 타입에 **Modify object** 또는 **Create object** 규칙을 설정하고, 대상 객체의 문자열 속성을 스케줄 규칙이 제공하는 스케줄 실행 RID 값에 매핑합니다.

![Ontology Manager의 액션 타입 설정 페이지. 스케줄 규칙이 추가되어 있고, Create object 규칙을 통해 스케줄 실행 RID를 문자열 속성에 기록합니다.](https://www.palantir.com/docs/resources/foundry/action-types/build-schedule-run-rid-property.png)

저장된 RID를 실시간 빌드 상태 표시기로 렌더링하려면 그 속성에 [리소스 RID 서식(resource RID formatting)을](../02_object-and-link-types/03_properties/03_value-formatting.md#supported-value-formatting) 적용합니다. 서식이 활성화되면 Foundry는 RID 값을 아이콘과 텍스트가 있는 링크로 표시하며, 이 텍스트는 빌드의 현재 상태인 `Running`, `Ignored`, `Failed`, `Succeeded` 중 하나를 반영합니다.

**설명**: 예를 들어 `RecomputeRequest` 객체 타입에 `build_run` 문자열 속성을 두고, 액션의 Create object 규칙으로 새 요청 객체를 만들면서 이 속성에 스케줄 실행 RID를 넣는 구성입니다. 이후 Object View나 Workshop에서 이 속성을 보면, 값 자체는 RID 문자열이지만 화면에는 "Running"에서 "Succeeded"로 바뀌는 상태 링크로 표시됩니다.

> **중간 요약**: 스케줄 실행 RID는 편집 규칙에서 참조할 수 있으므로 Modify object 또는 Create object 규칙으로 객체의 문자열 속성에 저장할 수 있고, 리소스 RID 서식을 적용하면 빌드 상태가 실시간으로 표시됩니다.

## 정리

- 스케줄 규칙은 액션이 적용될 때 프로젝트 범위 모드 스케줄의 빌드를 트리거합니다.
- 온톨로지 편집은 빌드 시작 직후 적용되며 빌드 완료를 기다리지 않습니다.
- 파라미터화된 스케줄이면 각 파라미터 값을 제공해야 하고, 병렬화된 파라미터화 스케줄과 함께 쓰면 특히 유용합니다.
- 실행 권한은 액션 제출 조건으로 관리되며, 스케줄 실행 통제권이 액션 타입으로 위임됩니다.
- 스케줄 실행 RID를 객체의 문자열 속성에 저장하고 리소스 RID 서식을 적용하면 빌드 상태를 추적할 수 있습니다.
