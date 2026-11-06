# 다른 액션 타입 살펴보기 (Explore other action types)

- 원문: https://www.palantir.com/docs/foundry/action-types/explore-action-types/
- 사이드바 위치: Define Ontologies > Action types > Explore other action types

이 페이지는 속성 하나를 수정하는 기본 액션 타입을 넘어, 규칙(rule)을 조합해 만들 수 있는 다양한 액션 타입을 한눈에 소개합니다. 객체 생성과 삭제, 링크 관리, 함수(function) 실행, 웹훅 호출, 알림, 빌드 트리거, 시나리오 병합, 인터페이스와 구조체(struct) 처리까지, 각 기능을 언제 쓰는지와 어디서 구성하는지를 설명하고 상세 문서로 연결합니다.

[시작하기](02_getting-started.md) 튜토리얼은 한 가지 종류의 액션 타입, 즉 객체 하나의 속성(property)을 수정하는 규칙을 만듭니다. 액션 타입은 속성 편집보다 훨씬 많은 것을 표현할 수 있습니다. 같은 구성 화면에서 객체를 생성하고 삭제하고, 객체 간 링크를 관리하고, 함수에서 사용자 정의 로직을 실행하고, 외부 시스템을 호출하고, 사용자에게 알리고, 빌드를 트리거하고, 시나리오 편집(edit)을 병합할 수도 있습니다.

이 페이지는 각 기능을 소개하고, 언제 사용하는지 설명하며, 참조 문서로 연결합니다. 예시는 [시작하기](02_getting-started.md) 튜토리얼의 `Demo Ticket` 객체 타입을 이어서 사용하므로 같은 온톨로지(Ontology)에서 따라 해 볼 수 있습니다.

<a id="prerequisites"></a>
## 사전 준비 (Prerequisites)

* [시작하기](02_getting-started.md) 튜토리얼을 완료하세요. 이 페이지의 나머지 부분에서 이미 안다고 가정하는 생성 마법사, 파라미터, 제출 조건(submission criteria)을 다룹니다.
* 변경하려는 객체 타입이 [편집할 수 있도록 구성](../02_object-and-link-types/07_allow-editing.md#set-up-the-prerequisites)되어 있는지 확인하세요.

<a id="where-to-configure-rules"></a>
## 규칙을 구성하는 곳 (Where to configure rules)

아래 기능들은 규칙을 통해 구성하며, 규칙은 두 곳에서 추가할 수 있습니다.

생성 마법사는 새 액션 타입의 첫 번째 규칙을 구성합니다. **Action type** 단계에서 **Object** 탭을 열고 객체 타입을 선택한 다음, **Object actions** 아래에서 액션이 하는 변경을 선택합니다. **Mapping** 단계에서 포함할 속성을 선택합니다. [시작하기](02_getting-started.md) 튜토리얼이 이 흐름을 단계별로 안내합니다.

![액션 타입 생성 마법사의 첫 단계. 객체 타입과 액션이 하는 변경을 선택합니다.](https://www.palantir.com/docs/resources/foundry/action-types/actions_wizard.png)

이미 있는 액션 타입이라면 [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)에서 열고 **Rules** 탭을 선택한 뒤 **Add new rule**(새 규칙 추가)을 선택해 필요한 규칙을 고릅니다. 이 페이지에서 설명하는 모든 규칙을 여기서 추가할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/side_effects_notification_tutorial_edit_action_rules.png" alt="액션 타입 Rules 탭의 Add new rule 드롭다운 메뉴" width="500" />

하나의 액션 타입은 여러 규칙을 조합할 수 있습니다. 단, [함수 규칙](#run-custom-logic-with-a-function)은 예외로, 다른 온톨로지 규칙과 함께 쓸 수 없습니다.

**설명**: 규칙은 "액션이 실행되면 무엇을 할지"를 선언적으로 적은 한 줄 단위의 명령입니다. 예를 들어 "Demo Ticket 객체를 수정한다", "알림을 보낸다"가 각각 하나의 규칙이며, 한 액션 타입에 여러 규칙을 넣으면 액션 한 번 실행에 이들이 모두 수행됩니다.

<a id="choose-a-rule"></a>
## 규칙 선택하기 (Choose a rule)

| 목표 | 추가할 규칙 | 더 알아보기 |
|--- |--- |--- |
| 새 객체 만들기 | **Create object** | [객체 생성과 삭제](#create-and-delete-objects) |
| 사용자가 객체를 제공하지 않을 때만 객체 만들기 | **Create or modify object** | [객체 생성과 삭제](#create-and-delete-objects) |
| 기존 객체 삭제하기 | **Delete object** | [객체 생성과 삭제](#create-and-delete-objects) |
| 두 객체를 연결하거나 그 관계 제거하기 | **Create link** 또는 **Delete link** | [객체 간 링크 관리](#manage-links-between-objects) |
| 규칙으로 기술할 수 없는 로직 표현하기 | **Run function** | [함수로 사용자 정의 로직 실행](#run-custom-logic-with-a-function) |
| Foundry 외부 시스템에 요청 보내기 | **Webhook** | [웹훅으로 외부 시스템 호출](#call-an-external-system-with-a-webhook) |
| 편집이 적용되기 전에 외부 시스템 호출하기 | **Writeback Webhook** | [웹훅으로 외부 시스템 호출](#call-an-external-system-with-a-webhook) |
| 무언가 바뀌었음을 사용자에게 알리기 | **Notification** | [액션 적용 시 사용자에게 알림](#notify-users-when-an-action-is-applied) |
| 액션 적용 시 데이터셋 다시 계산하기 | **Schedule** | [빌드 트리거](#trigger-a-build) |
| 시나리오에 스테이징된 편집 커밋하기 | **Apply scenario** | [시나리오 편집 병합](#merge-scenario-edits) |
| 인터페이스를 구현하는 모든 타입의 객체 변경하기 | 인터페이스 규칙 | [인터페이스에 대한 작업](#act-on-interfaces) |

[규칙(rules)](06_rules.md) 참조 문서에서 모든 규칙을 자세히 설명합니다.

> **중간 요약**: 규칙은 생성 마법사(첫 규칙)나 기존 액션 타입의 Rules 탭(Add new rule)에서 추가하며, 한 액션 타입에 여러 규칙을 조합할 수 있지만 Run function 규칙만은 다른 온톨로지 규칙과 함께 쓸 수 없습니다.

<a id="create-and-delete-objects"></a>
## 객체 생성과 삭제 (Create and delete objects)

시작하기 튜토리얼은 사용자가 선택한 객체를 수정합니다. 대신 새 티켓을 만들려면 **Create object** 규칙을 추가하고 `Demo Ticket` 객체 타입을 선택합니다. 객체 타입의 기본 키(primary key), 이 예에서는 `Ticket ID`는 반드시 채워야 하는 필수 속성입니다. 새 객체에 필요한 다른 속성(`Title`, `Status`, `Priority` 등)은 **Add property**를 선택해 추가합니다.

추가하는 각 속성은 같은 이름의 파라미터를 자동으로 만들고 속성을 그 파라미터에 매핑합니다. 대신 속성을 객체 참조 파라미터의 속성, 사용자가 바꿀 수 없는 정적 값, 현재 사용자, 제출 시각에 매핑할 수도 있습니다. 모든 매핑 옵션은 [값과 파라미터](06_rules.md#values-and-parameters)를 참고하세요.

관련된 두 규칙이 나머지 경우를 다룹니다.

* **Create or modify object(객체 생성 또는 수정):** 객체 참조 파라미터로 제공된 객체를 수정합니다. 객체가 제공되지 않으면 자동 생성된 고유 ID 또는 사용자가 제출한 기본 키로 새 객체를 만듭니다.
* **Delete object(객체 삭제):** 객체 참조 파라미터로 제공된 객체를 삭제합니다. 이 규칙은 같은 액션이 만드는 객체를 참조할 수 없습니다.

**주의**: 액션 타입에 규칙이 여러 개 있으면 Foundry는 이를 객체마다 하나의 편집으로 컴파일하므로, 규칙의 순서가 결과에 영향을 주며 일부 조합은 지원되지 않습니다. 한 액션 타입에서 생성, 수정, 삭제 규칙을 조합하기 전에 [유효하지 않은 조합](06_rules.md#invalid-combinations)을 확인하세요.

**설명**: Create or modify object는 SQL의 upsert(`INSERT ... ON CONFLICT DO UPDATE`)와 비슷한 동작입니다. 기존 객체가 주어지면 갱신하고, 없으면 새로 삽입합니다. 여러 규칙이 "객체마다 하나의 편집으로 컴파일"된다는 것은, 예를 들어 같은 티켓에 대해 규칙 1이 `Priority=P1`, 규칙 2가 `Priority=P0`으로 설정하면 두 번의 갱신이 각각 일어나는 것이 아니라 최종 결과 하나로 합쳐진다는 뜻입니다. 그래서 순서가 결과를 바꿉니다.

<a id="manage-links-between-objects"></a>
## 객체 간 링크 관리 (Manage links between objects)

액션은 객체의 속성뿐 아니라 객체 간 관계도 관리할 수 있습니다. 어떤 규칙이 필요한지는 [링크 타입](../02_object-and-link-types/06_link-types/01_link-types-overview.md)의 카디널리티에 따라 다릅니다.

다대다(many-to-many) 링크 타입에서는, 객체 참조 파라미터로 제공된 두 객체를 연결하려면 **Create link** 규칙을, 둘 사이의 관계를 제거하려면 **Delete link** 규칙을 추가합니다.

일대일 또는 일대다 링크 타입에서는 관계가 객체의 외래 키(foreign key) 속성에 저장됩니다. 링크 규칙 대신 **Modify object** 규칙을 사용해 그 속성을 설정하거나 비웁니다.

하나의 액션에서 객체와 그 객체의 다대다 링크를 함께 만들 수도 있습니다. 다대다 링크 타입을 가진 객체 타입으로 **Create object** 규칙을 구성한 다음, **Add property** 아래의 **Add link**를 선택해 링크 타입을 고르고 링크를 구성합니다.

**설명**: 관계형 데이터베이스로 보면 이해가 쉽습니다. 일대다 관계(티켓 여러 개가 담당자 한 명에게 배정)는 티켓 테이블의 `assignee_id` 열 하나로 표현되므로, 링크를 바꾸는 것은 그 열 값을 `UPDATE`하는 것입니다. 다대다 관계(티켓과 태그)는 별도 조인 테이블의 행으로 표현되므로, 링크를 만들거나 지우는 것은 그 조인 테이블에 행을 `INSERT`하거나 `DELETE`하는 것이고, 이를 위해 전용 규칙이 있습니다.

> **중간 요약**: Create object, Create or modify object, Delete object로 객체를 만들고 지우며, 여러 규칙은 객체당 하나의 편집으로 합쳐지므로 순서와 조합에 주의해야 합니다. 링크는 다대다면 Create link와 Delete link로, 일대일과 일대다면 외래 키 속성을 Modify object로 바꿔 관리합니다.

<a id="run-custom-logic-with-a-function"></a>
## 함수로 사용자 정의 로직 실행 (Run custom logic with a function)

규칙은 편집을 선언적 매핑으로 기술하는데, 이것만으로 항상 충분하지는 않습니다. 사용자가 선택한 객체에 링크된 모든 객체를 수정하려 할 때, 여러 객체를 읽는 비즈니스 로직으로 속성 값을 계산하려 할 때, 여러 타입의 객체를 만들고 서로 링크하려 할 때는 [온톨로지 편집 함수(Ontology edit function)](../04_functions/09_language-agnostic-features/01_edits-overview.md)로 액션을 뒷받침하는 것을 고려하세요.

**Run function** 규칙 하나를 추가한 다음, 게시된 함수와 사용할 버전을 선택합니다. 함수의 모든 입력은 액션 타입의 파라미터로 만들어지며, 다른 파라미터처럼 제약할 수 있습니다. **Run function** 규칙은 다른 [온톨로지 규칙](06_rules.md#ontology-rules)과 함께 쓸 수 없습니다. 함수 코드만으로 그 규칙들이 할 수 있는 모든 것을 표현할 수 있기 때문입니다.

액션이 참조하는 [함수 버전을 바꾸는 방법](11_function-backed-actions/02_function-actions-getting-started.md#changing-function-version)을 포함한 전체 과정은 [함수 기반 액션 튜토리얼](11_function-backed-actions/02_function-actions-getting-started.md)을 따르세요. 기본적으로 액션은 선택한 버전에 머뭅니다. 대신 실행 시점에 버전 범위를 해석하려면 [자동 업그레이드(auto upgrades)](11_function-backed-actions/02_function-actions-getting-started.md#auto-upgrades)를 활성화하되, 그 전에 거기서 설명하는 권한과 호환성 깨짐 측면의 장단점을 검토하세요.

<a id="call-an-external-system-with-a-webhook"></a>
## 웹훅으로 외부 시스템 호출 (Call an external system with a webhook)

Foundry 외부 시스템이 프로세스 일부의 원천 데이터(source of truth)일 때, 웹훅 규칙은 액션을 적용하는 과정에서 그 시스템에 요청을 보냅니다. 액션 파라미터를 웹훅의 입력으로 넘길 수 있습니다.

요청을 보내는 규칙은 두 가지가 따로 있으며, 어떤 규칙을 추가하느냐에 따라 실행 시점이 정해집니다.

* **Webhook:** 객체 편집이 적용된 뒤에 요청을 보냅니다. **Side Effects** 그룹에서 이 규칙을 추가합니다. 액션 타입 하나에 여러 개 넣을 수 있으며, 실패해도 최종 사용자에게 표시되지 않습니다. 최종 사용자는 이미 성공 메시지를 봤을 수 있습니다.
* **Writeback Webhook:** 다른 규칙이 평가되기 전에 요청을 보냅니다. **External Request** 그룹에서 이 규칙을 추가합니다. 요청이 실패하면 아무 편집도 적용되지 않고 최종 사용자에게 실패가 표시됩니다. 액션 타입 하나에 하나만 넣을 수 있으며, 그 [출력 파라미터](12_side-effects/04_webhooks.md#output-parameters)를 이후 규칙에서 사용할 수 있습니다.

웹훅은 규칙에서 선택하기 전에 [Data Connection](https://www.palantir.com/docs/foundry/data-connection/webhooks-setup/)에 이미 존재해야 합니다. 구성 단계는 [웹훅 설정](12_side-effects/05_set-up-webhook.md)을 따르고, 입력 파라미터, 출력 파라미터, 인증 옵션은 [웹훅](12_side-effects/04_webhooks.md)을 참고하세요.

**설명**: 두 웹훅의 차이는 트랜잭션 순서입니다. 예를 들어 외부 결제 시스템에 주문을 등록해야 하는 경우, Writeback Webhook은 먼저 외부 시스템을 호출하고 성공해야만 Foundry 객체를 바꾸므로 두 시스템의 상태가 어긋나지 않습니다. 외부 시스템이 돌려준 주문 번호를 출력 파라미터로 받아 객체 속성에 기록할 수도 있습니다. 일반 Webhook은 Foundry 편집이 끝난 뒤 "알림성" 호출을 보내는 용도이며, 실패해도 Foundry 쪽 편집은 되돌려지지 않습니다.

> **중간 요약**: 규칙으로 표현하기 어려운 로직은 Run function 규칙으로 함수에 맡기며, 이 규칙은 단독으로만 씁니다. 외부 시스템 호출은 편집 후 실행되고 실패가 무시되는 Webhook과, 편집 전에 실행되어 실패하면 전체를 막는 Writeback Webhook 중에서 고릅니다.

<a id="notify-users-when-an-action-is-applied"></a>
## 액션 적용 시 사용자에게 알림 (Notify users when an action is applied)

**Notification** 규칙은 액션이 적용되었음을 사용자에게 알립니다. 수신자는 고정된 사용자 집합일 수도 있고 객체 파라미터의 속성에서 도출될 수도 있으며, 내용은 액션의 파라미터를 참조하는 템플릿일 수 있습니다. 각 수신자는 자신의 알림 설정에 따라 플랫폼 내 푸시 알림, 이메일 또는 둘 다를 받습니다.

알림은 액션의 모든 편집이 적용된 뒤에 전송되지만, 그 내용은 편집이 적용되기 전의 온톨로지 상태를 바탕으로 생성됩니다. 실제 예시는 [알림 설정](12_side-effects/03_set-up-notification.md)을 따르고, 모든 수신자와 내용 옵션은 [알림](12_side-effects/02_notifications.md)을 참고하세요.

**설명**: "내용은 편집 전 상태로 생성된다"는 점은 템플릿을 쓸 때 중요합니다. 예를 들어 우선순위를 `P2`에서 `P0`으로 바꾸는 액션의 알림 템플릿에서 티켓 객체의 `Priority` 속성을 읽으면 이전 값 `P2`가 들어갑니다. 새 값을 보여 주려면 객체 속성이 아니라 `Priority` 파라미터 값을 참조해야 합니다.

<a id="trigger-a-build"></a>
## 빌드 트리거 (Trigger a build)

**Schedule** 규칙은 액션이 적용될 때 [스케줄(schedule)](https://www.palantir.com/docs/foundry/data-integration/schedules/)의 빌드를 트리거합니다. **Advanced** 그룹에서 이 규칙을 추가합니다. 이를 통해 온톨로지의 최종 사용자 워크플로가 액션의 일부로 데이터셋을 다시 계산할 수 있습니다. 스케줄은 [프로젝트 범위 모드(project-scoped mode)](https://www.palantir.com/docs/foundry/data-integration/schedules/#project-scope)여야 합니다.

스케줄 규칙이 있는 액션 타입은 빌드가 끝나기를 기다리지 않고 빌드가 시작된 뒤에 온톨로지 편집을 적용합니다. 파라미터화된 스케줄에 값을 넘기는 방법과 그 결과로 생긴 스케줄 실행 RID를 객체에 기록하는 방법은 [스케줄 빌드 트리거](13_trigger-schedule-build.md)를 참고하세요.

<a id="merge-scenario-edits"></a>
## 시나리오 편집 병합 (Merge scenario edits)

[시나리오](../../04_ontology-scenarios/01_overview-ontology-scenario.md) 안에서 한 편집은 그 시나리오의 샌드박스 안에만 존재하며 메인 온톨로지에 영향을 주지 않습니다. 병합(merge) 액션은 스테이징된 모든 편집을 하나의 트랜잭션으로 커밋합니다. 병합 액션에는 시나리오의 RID를 담은 **Scenario** 파라미터가 필요하며, 이 값은 보통 Workshop 변수나 Ontology SDK 애플리케이션에서 전달됩니다.

병합 액션을 만드는 경로는 두 가지입니다.

* 새 액션 타입을 만들면서 생성 마법사에서 **Scenario** 탭을 선택한 뒤, 관련 **Object types**와 **Link types**를 추가해 병합 범위를 정의합니다.
* 이미 있는 액션 타입의 **Rules** 탭에서 **Apply scenario** 규칙을 추가합니다.

두 경우 모두 액션 타입의 **Security & Submission Criteria** 탭에서 어떤 사용자가 병합을 실행할 수 있는지 정의합니다. 전체 구성은 [시나리오 병합](../../04_ontology-scenarios/04_merge-scenario.md#configure-the-merge-action)을 참고하세요.

**참고**: 베타(Beta). 온톨로지 시나리오는 개발 단계상 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으며 사용 중인 환경에서 제공되지 않을 수 있습니다. 시나리오 사용 권한을 요청하려면 Palantir Support에 문의하세요.

**설명**: 시나리오는 메인 데이터를 건드리지 않고 "만약 이렇게 바꾸면"을 시험해 보는 격리된 작업 공간입니다. 데이터베이스 트랜잭션에서 `BEGIN` 후 여러 변경을 하고 마지막에 `COMMIT`하는 것처럼, 병합 액션은 시나리오에 쌓인 변경 전체를 한 번에 반영하거나 하나도 반영하지 않습니다.

> **중간 요약**: Notification은 편집 후에 보내지지만 내용은 편집 전 상태로 만들어지고, Schedule은 빌드 시작 후 바로 편집을 적용하며, 시나리오 병합 액션은 시나리오의 편집 전체를 한 트랜잭션으로 커밋합니다.

<a id="act-on-interfaces"></a>
## 인터페이스에 대한 작업 (Act on interfaces)

인터페이스에는 온톨로지 편집마다 전용 규칙이 있습니다.

* **Create object of interface**(인터페이스의 객체 생성)
* **Modify object of interface**(인터페이스의 객체 수정)
* **Delete object of interface**(인터페이스의 객체 삭제)
* **Create link on object of interface**(인터페이스 객체에 링크 생성)
* **Delete link on object of interface**(인터페이스 객체의 링크 삭제)

각 규칙은 특정 객체 타입 하나가 아니라 인터페이스를 구현하는 모든 객체 타입을 대상으로 합니다. 수정과 삭제 규칙은 객체 참조 파라미터 대신 인터페이스 참조 파라미터를 받습니다. [인터페이스에 대한 액션](09_actions-on-interfaces.md)을 참고하세요.

<a id="map-a-struct-property-in-a-rule"></a>
## 규칙에서 구조체 속성 매핑하기 (Map a struct property in a rule)

[구조체 속성(struct property)](../02_object-and-link-types/04_structs/01_structs-overview.md)은 중첩 필드가 속성의 필드를 그대로 반영하는 구조체 파라미터에서 값을 가져옵니다. 규칙 안에서 속성을 매핑하고, 모든 필드가 매핑되었는지 확인하세요. [구조체에 대한 액션](10_actions-on-structs.md)을 참고하세요.

> **중간 요약**: 인터페이스 전용 규칙은 인터페이스를 구현한 어떤 객체 타입이든 대상으로 하며 인터페이스 참조 파라미터를 쓰고, 구조체 속성은 같은 필드 구조의 구조체 파라미터에 모든 필드를 매핑해야 합니다.

<a id="next-steps"></a>
## 다음 단계 (Next steps)

* [테스트 실행으로 액션 타입을 검증하세요.](05_test-run.md)
* [전체 규칙 참조 문서를 살펴보세요.](06_rules.md)
* [파라미터로 사용자가 제출할 수 있는 내용을 정하세요.](07_parameters/01_parameter-overview.md)
* [제출 조건으로 액션을 적용할 수 있는 시점을 제한하세요.](08_submission-criteria.md)
* [플랫폼의 다른 곳에서 액션을 사용하세요.](04_use-actions.md)

## 정리

- 액션 타입은 규칙을 조합해 만들며, 규칙은 생성 마법사나 Rules 탭의 Add new rule에서 추가합니다.
- 객체 생성, 생성 또는 수정, 삭제 규칙과 링크 생성, 삭제 규칙(다대다)으로 데이터를 바꾸고, 여러 규칙은 객체당 하나의 편집으로 컴파일됩니다.
- Run function 규칙은 복잡한 로직을 함수로 처리하며 다른 온톨로지 규칙과 함께 쓸 수 없습니다.
- 부수 효과(side effect)와 외부 연동으로 Webhook, Writeback Webhook, Notification, Schedule 규칙이 있고, 각각 실행 시점과 실패 처리가 다릅니다.
- 시나리오 병합, 인터페이스 전용 규칙, 구조체 속성 매핑도 같은 규칙 체계로 구성합니다.
