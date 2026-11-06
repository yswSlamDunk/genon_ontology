# 액션 타입 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/action-types/getting-started/
- 사이드바 위치: Define Ontologies > Action types > Getting started

이 페이지는 티켓의 우선순위를 바꾸는 간단한 액션 타입을 처음부터 끝까지 만들어 보는 튜토리얼입니다. 액션 타입 생성 마법사, 파라미터 제약, 제출 조건(submission criteria) 설정, Object View에 액션 버튼 배치, 실제 실행까지의 흐름을 한 번에 보여 줍니다. 마지막에는 사용자 편집과 데이터소스 갱신이 충돌할 때의 해결 전략도 소개합니다.

이 가이드에서는 티켓의 우선순위를 바꾸는 간단한 액션 타입을 만듭니다.

우선순위가 `P0`, `P1`, `P2` 중 하나이고 티켓 상태가 `Open`인지 확인하도록 제출 조건(submission criteria)을 구성합니다.

<a id="prerequisites"></a>
## 사전 준비 (Prerequisites)

이 가이드에서는 네 개의 속성(property)을 가진 `Demo Ticket` 객체 타입을 사용합니다.

* `Ticket ID`
* `Title`
* `Priority`
* `Status`

데모 객체도 두 개 준비되어 있습니다.

|Ticket ID|Title          |Status|Priority|
|---------|---------------|------|--------|
|PDS-123  |Demo Ticket One|Open  |P2      |
|PDS-124  |Demo Ticket Two|Closed|P1      |

원한다면 온톨로지(Ontology)에 이것들을 다시 만들어도 되지만 꼭 필요한 것은 아닙니다.

사용자가 액션 타입 구성에 정의된 액션을 실행하려면 [추가 구성이 필요합니다](../02_object-and-link-types/07_allow-editing.md#set-up-the-prerequisites). Object Storage v2를 사용한다면 토글로 편집을 활성화해야 합니다. Object Storage v1(Phonograph)을 사용한다면 라이트백(writeback) 데이터셋을 만들어야 합니다. [Object Storage v1](../../06_ontology-architecture/05_object-databases/01_object-storage-v1.md)은 개발 단계상 [사용 중단 예정(planned deprecation)](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으니 [Object Storage v2로 마이그레이션하세요](../../06_ontology-architecture/01_overview-and-getting-started/03_osv1-osv2-migration.md).

**설명**: 액션 타입은 "어떤 객체를, 어떤 입력을 받아, 어떻게 바꿀지"를 정의한 템플릿이고, 액션은 사용자가 그 템플릿에 실제 값을 넣어 한 번 실행한 것입니다. 함수 정의와 함수 호출의 관계로 보면 됩니다. 이 튜토리얼에서 만드는 액션 타입은 SQL로 쓰면 `UPDATE demo_ticket SET priority = ? WHERE ticket_id = ? AND status = 'Open'`에 해당하는 일을 화면에서 할 수 있게 해 줍니다.

> **중간 요약**: `Ticket ID`, `Title`, `Priority`, `Status` 속성을 가진 `Demo Ticket` 객체 타입을 예로 사용하며, 액션을 실행하려면 OSv2에서는 편집 토글, OSv1에서는 라이트백 데이터셋이 필요합니다.

<a id="create-a-new-action-type"></a>
## 새 액션 타입 만들기 (Create a new action type)

먼저 티켓 우선순위를 바꾸는 새 액션 타입을 만듭니다. Ontology Manager의 왼쪽 사이드바에서 **Action types**를 선택한 뒤, 화면 오른쪽 위에서 **New action type**(새 액션 타입)을 선택합니다.

![새 액션 타입 만들기](https://www.palantir.com/docs/resources/foundry/action-types/actions_wizard.png)

생성 마법사(creation wizard)에서는 액션 타입의 가장 중요한 기능을 구성할 수 있습니다. **Action type** 단계에서 **Object** 탭을 열고 `Demo Ticket` 객체 타입을 선택한 다음, **Object actions** 아래에서 **Modify object(s)**(객체 수정)를 선택합니다. **Mapping** 단계에서 **Add property**를 선택해 `Priority` 속성을 추가합니다. **Metadata** 단계에서 액션 타입의 **Action type name**(액션 타입 이름)을 입력합니다. 마지막 단계로 넘어가 **Create**를 선택합니다.

이제 액션 타입의 전체 상세 화면을 볼 수 있습니다. **Overview** 탭에서 **Description**(설명)을 추가하거나 **Rules** 탭에서 수정할 속성을 더 추가하는 등 추가 조정을 할 수 있습니다.

<a id="edit-parameters"></a>
## 파라미터 편집 (Edit parameters)

**Parameters** 탭을 선택하면 파라미터 개요를 볼 수 있습니다. `Ticket`과 `Priority` 파라미터는 **Rule**(규칙)을 기반으로 이미 만들어져 있습니다.

![액션 폼](https://www.palantir.com/docs/resources/foundry/action-types/actions_form.png)

`Priority` 파라미터를 선택해 가질 수 있는 값을 제한합니다. 제약 조건을 **User input**(사용자 입력)에서 **Multiple choice**(다중 선택)로 바꿉니다. 그러면 이 파라미터에 선택할 수 있는 값을 정할 수 있습니다. 옵션으로 `P0`, `P1`, `P2`를 추가합니다. 지금 액션을 객체에 적용하면 티켓의 우선순위를 `P0`, `P1`, `P2` 중 하나로 바꿀 수 있습니다. 다음으로 열린(open) 티켓의 우선순위만 바꿀 수 있도록 제한하는 제출 조건을 추가합니다.

![Priority 파라미터](https://www.palantir.com/docs/resources/foundry/action-types/actions_constraints.png)

**설명**: 파라미터는 액션 실행 시 사용자가 입력하는 값으로, 함수의 매개변수에 해당합니다. 여기서 `Ticket`은 어떤 티켓 객체를 바꿀지 가리키는 객체 참조 파라미터이고, `Priority`는 새 우선순위 값입니다. 규칙(rule)이 "`Ticket` 객체의 `Priority` 속성을 `Priority` 파라미터 값으로 바꾼다"고 정의하므로 두 파라미터가 자동으로 생겼습니다. Multiple choice 제약은 열거형(enum) 타입처럼 허용 값을 고정합니다.

> **중간 요약**: 생성 마법사에서 `Demo Ticket` 객체 타입, Modify object(s), `Priority` 속성, 이름을 지정해 액션 타입을 만들고, `Priority` 파라미터를 `P0`, `P1`, `P2` 다중 선택으로 제한합니다.

<a id="add-submission-criteria"></a>
## 제출 조건 추가 (Add submission criteria)

사이드바의 **Security & Submission Criteria** 탭에서 제출 조건 섹션을 엽니다. **Execution** 섹션에서 **Condition**(조건)을 선택해 새 조건을 만듭니다. **Parameter** 조건 템플릿을 사용해 `Ticket` 객체 파라미터의 `Status` 속성에 조건을 겁니다. `is` 연산자를 사용하면 티켓 상태와 특정 값 `Open` 사이에 정확한 문자열 비교를 할 수 있습니다.

![제출 조건](https://www.palantir.com/docs/resources/foundry/action-types/actions_submission_criteria.png)

사용자가 액션이 실패한 이유를 알 수 있도록 실패 메시지를 추가합니다. 이제 액션 정의가 완성되었으며, Object Explorer의 Object View 옆에 표시되도록 구성할 수 있습니다.

**설명**: 제출 조건은 액션을 실행하기 전에 검사하는 사전 조건(precondition)입니다. 파라미터 제약이 "입력 값이 올바른가"를 본다면, 제출 조건은 "지금 이 액션을 실행해도 되는 상황인가"를 봅니다. 여기서는 선택한 티켓의 `Status`가 `Open`이 아니면(예: PDS-124처럼 `Closed`이면) 제출이 거부되고 실패 메시지가 표시됩니다.

<a id="add-the-action-to-an-object-view"></a>
## Object View에 액션 추가 (Add the action to an Object View)

**Demo Ticket One**으로 가서 Object View를 편집합니다. 맨 위에 새 위젯을 추가하고 **Actions** 위젯을 선택합니다. 사이드바에서 **Add Item**을 선택합니다. Ontology Manager에서 액션 RID를 복사해 Action RID 필드에 붙여 넣습니다. 레이블 이름을 "Change Ticket Priority"로 지정합니다.

![Object View에 액션 추가](https://www.palantir.com/docs/resources/foundry/action-types/getting_started_add_RID.png)

기본적으로 액션 폼은 `Ticket` 파라미터를 포함한 모든 파라미터를 액션 폼의 필드로 보여 줍니다. 또한 액션은 `Ticket` 파라미터에 현재 객체를 채워 넣어야 한다는 사실을 알지 못합니다. 따라서 티켓 필드를 숨기고(사용자가 다른 티켓의 상태를 바꾸지 못하도록) 그 값을 현재 객체로 설정하도록 액션 폼을 구성합니다.
**Default value**(기본값) 아래에서 **Add Item**을 선택합니다. `Ticket` 파라미터의 파라미터 ID를 입력합니다. 이 튜토리얼에서는 `ticket`으로 설정했습니다. 값 유형을 **Environment variable**(환경 변수)로 바꾸고 **Current object**(현재 객체)를 선택합니다. 마지막으로 표시 옵션을 **Hidden**(숨김)으로 바꿉니다.

![액션 폼 구성](https://www.palantir.com/docs/resources/foundry/action-types/getting_started_configure_action_form.png)

이제 미리 보기 페이지에서 액션 버튼을 볼 수 있습니다.

![미리 보기 페이지의 액션 버튼](https://www.palantir.com/docs/resources/foundry/action-types/getting_started_preview_page.png)

이제 Object View를 저장하고 게시(publish)할 수 있습니다.

> **중간 요약**: `Status`가 `Open`인지 검사하는 제출 조건과 실패 메시지를 추가한 뒤, Object View에 Actions 위젯으로 액션을 붙이고 `ticket` 파라미터를 현재 객체로 자동 채우고 숨깁니다.

<a id="apply-the-action"></a>
## 액션 적용 (Apply the action)

액션을 적용하기 전에 Ontology Manager에서 [테스트 실행(test run)](05_test-run.md)으로 제출 조건, 규칙, 결과 편집(edit)을 검증할 수 있습니다.

열린 티켓으로 가서 앞에서 구성한 **Change Ticket Priority** 버튼을 선택합니다. 화면 위에 액션 폼이 나타납니다. **Priority** 필드를 클릭하면 파라미터에 구성한 단일 선택 조건이 표시됩니다.

![액션으로 티켓 우선순위 변경](https://www.palantir.com/docs/resources/foundry/action-types/getting_started_apply_action.png)

우선순위를 고르고 **Submit**(제출)을 선택합니다. 폼이 사라지고 Object View가 새 우선순위로 갱신됩니다. 제출 조건에 따라 닫힌 티켓에서는 이 액션을 실행할 수 없어야 합니다. 닫힌 상태인 Demo Ticket Two를 열면 다음과 같은 화면을 볼 수 있습니다.

![제출 조건이 닫힌 티켓에서 액션 실행을 막는 모습](https://www.palantir.com/docs/resources/foundry/action-types/getting_started_testing_validation.png)

<a id="resolve-conflicting-user-edits-actions-and-datasource-updates"></a>
## 사용자 편집(액션)과 데이터소스 갱신의 충돌 해결 (Resolve conflicting user edits (actions) and datasource updates)

Foundry 온톨로지의 객체 인스턴스는 입력 데이터소스와 사용자 편집 또는 액션 양쪽에서 생성되고 수정될 수 있습니다. 하나의 객체 인스턴스(즉, 특정 기본 키(primary key) 값을 가진 행 또는 객체)가 입력 데이터소스와 사용자 편집 양쪽에서 데이터를 받으면, 받은 값들은 충돌 해결 전략에 따라 투명하게 해결되어야 합니다.

충돌을 해결하는 전략은 두 가지입니다.

* 전략 1: 사용자 편집 적용(기본값)
* 전략 2: 가장 최근 값 적용(사용 중인 환경에서는 제공되지 않을 수 있음)

[사용자 편집과 데이터소스 갱신의 충돌을 해결하는 방법을 더 알아보세요.](../../06_ontology-architecture/04_object-edits-and-materializations/02_how-edits-applied.md#resolve-conflicting-user-edits-and-datasource-updates)

**설명**: 예를 들어 PDS-123의 우선순위를 사용자가 액션으로 `P0`으로 바꾼 뒤, 원본 데이터셋이 다시 빌드되면서 PDS-123의 우선순위가 `P1`으로 들어왔다고 합시다. 전략 1(기본값)에서는 사용자 편집이 우선하므로 `P0`이 유지됩니다. 전략 2에서는 두 값 중 더 나중에 들어온 값, 이 예에서는 데이터셋의 `P1`이 적용됩니다.

> **중간 요약**: 액션 버튼으로 우선순위를 바꾸면 Object View가 바로 갱신되고, 닫힌 티켓에서는 제출 조건 때문에 실행이 막힙니다. 같은 객체에 사용자 편집과 데이터소스 갱신이 겹치면 기본적으로 사용자 편집이 우선합니다.

<a id="next-steps"></a>
## 다음 단계 (Next steps)

* [링크, 함수, 웹훅, 시나리오 액션 등 만들 수 있는 다른 액션 타입을 살펴보세요.](03_explore-action-types.md)
* [액션 권한에 대해 더 알아보세요.](19_permissions.md)
* [함수 기반 액션(function-backed action)을 만드세요.](11_function-backed-actions/02_function-actions-getting-started.md)
* [플랫폼의 다른 곳에서 액션을 사용하세요.](04_use-actions.md)
* [사용자 편집(액션)과 데이터소스 갱신의 충돌을 해결하세요.](../../06_ontology-architecture/04_object-edits-and-materializations/02_how-edits-applied.md#resolve-conflicting-user-edits-and-datasource-updates)

## 정리

- 생성 마법사에서 객체 타입, 변경 종류(Modify object(s)), 수정할 속성, 이름을 지정해 액션 타입을 만듭니다.
- 파라미터는 규칙에서 자동 생성되며, Multiple choice 같은 제약으로 입력 값을 제한합니다.
- 제출 조건은 실행 전 상황(예: 티켓 상태가 `Open`)을 검사하고, 실패 시 실패 메시지를 보여 줍니다.
- Object View의 Actions 위젯에 액션 RID를 넣고, 객체 파라미터를 현재 객체로 채우고 숨기면 버튼 하나로 액션을 실행할 수 있습니다.
- 사용자 편집과 데이터소스 갱신이 충돌하면 기본적으로 사용자 편집이 적용됩니다.
