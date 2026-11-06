# 인터페이스에 대한 액션 (Actions on interfaces)

- 원문: https://www.palantir.com/docs/foundry/action-types/actions-on-interfaces/
- 사이드바 위치: Define Ontologies > Action types > Actions on interfaces

인터페이스는 여러 객체 타입이 공통으로 가지는 속성의 형태를 정의한 것입니다. 이 페이지는 특정 객체 타입 하나가 아니라 인터페이스를 대상으로 액션을 만들어, 그 인터페이스를 구현한 모든 객체 타입에 한꺼번에 적용하는 방법을 설명합니다. 생성, 수정, 삭제, 링크 생성/삭제 규칙별 주의점(특히 기본 키 문제)과 권한, 지원 범위, 제한 사항을 다룹니다.

선택한 인터페이스의 모든 객체에 적용되는 범용 액션을 만들 수 있습니다. 액션 안에서 인터페이스를 사용하는 주된 방법은 두 가지입니다.

* **인터페이스 액션 규칙(Interface action rules):** 구성된 인터페이스의 객체를 생성, 수정, 삭제, 링크합니다.
* **인터페이스 참조 파라미터(Interface reference parameters):** 구성된 인터페이스의 객체를 참조합니다. 이 파라미터는 "Modify"와 "Delete" 인터페이스 액션 규칙에 필수이지만, 다른 액션 규칙에서도 사용할 수 있습니다.

인터페이스는 [인터페이스 액션 타입 제약(interface action type constraints)](../05_interfaces/07_interface-action-type-constraints.md)도 정의할 수 있습니다. 이 제약은 구현하는 객체 타입이 구체적인 액션 타입으로 충족할 수 있는, 기대되는 액션 기능을 기술합니다.

액션 타입 제약은 인터페이스 수준의 액션 계약(contract)을 정의하고, 액션 규칙은 액션 타입이 제출될 때 수행되는 편집(edit)을 정의합니다.

인터페이스 액션 타입 제약은 현재 Ontology Manager의 모델링 및 매핑 기능이며, 최종 사용자 애플리케이션이나 Ontology SDK에서 호출할 수 있는 기능은 아닙니다.

**주의**: 인터페이스 액션의 제출 조건(submission criteria)은 인터페이스를 구현하는 모든 객체 타입에 똑같이 적용됩니다. 인터페이스 액션을 만들기 전에, 인터페이스를 구현하는 모든 객체 타입에 걸쳐 어떤 사용자가 객체를 생성, 수정, 삭제할 권한을 가지게 될지 신중히 검토하세요. [인터페이스 액션에 대한 통제를 설정하는 방법을 알아보세요](#limitations-of-interface-action-rules).

**설명**: 인터페이스는 Java나 TypeScript의 `interface`와 같은 개념입니다. 예를 들어 `Ticket` 인터페이스가 `title`, `description`, `priority` 속성을 정의하고, `Bug`와 `FeatureRequest` 객체 타입이 이 인터페이스를 구현한다고 합시다. 객체 타입별 액션은 `Bug`만 받는 메서드이고, 인터페이스 액션은 `Ticket` 타입 인자를 받아 `Bug`든 `FeatureRequest`든 처리하는 메서드입니다. "액션 타입 제약"은 이와 별개로 "이 인터페이스를 구현하는 객체 타입이라면 이런 액션을 하나 갖춰야 한다"는 요구 사항(추상 메서드 선언에 해당)을 적어 두는 것이고, "액션 규칙"은 실제로 실행되는 동작입니다.

> **중간 요약**: 인터페이스 액션 규칙으로 인터페이스 객체를 생성, 수정, 삭제, 링크하고, 인터페이스 참조 파라미터로 그 객체를 가리킵니다. 제출 조건이 모든 구현 객체 타입에 똑같이 적용되므로 권한 범위를 신중히 검토해야 합니다.

<a id="using-action-on-interface-rules"></a>
## 인터페이스 액션 규칙 사용하기 (Using action on interface rules)

인터페이스 액션 규칙은 편집이 인터페이스를 구현하는 모든 객체 타입에 적용될 수 있을 때 사용할 수 있습니다. 다시 말해, 인터페이스 액션 규칙은 *인터페이스의 공유 속성(shared property)만* 수정하거나 객체를 삭제하는 데 쓸 수 있습니다. 예를 들어 "Feature request"와 "Bug"가 "Ticket" 인터페이스의 객체 타입이라면, "Create a ticket" 액션 타입으로 버그와 기능 요청을 생성할 수는 있지만, 버그나 기능 요청에만 있는 속성은 만들 수 없습니다.

![인터페이스 액션 규칙 사용](https://www.palantir.com/docs/resources/foundry/action-types/action_on_interface_rules.png)

**설명**: 앞의 예에서 `Bug`에만 `stepsToReproduce` 속성이 있다고 합시다. `Ticket` 인터페이스 액션은 `Ticket`에 정의된 `title`, `description`, `priority`만 다룰 수 있으므로, 이 액션으로 버그를 만들면 `stepsToReproduce`는 채울 수 없습니다. 프로그래밍에서 인터페이스 타입 변수로는 인터페이스에 선언된 멤버만 접근할 수 있는 것과 같은 규칙입니다.

<a id="creating-a-new-interface-action-type"></a>
### 새 인터페이스 액션 타입 만들기 (Creating a new interface action type)

새 인터페이스 액션 타입을 설정하려면 Ontology Manager의 **New** 메뉴에서 **Action type**을 선택합니다.

1. **Interfaces** 아래에서 원하는 인터페이스와 규칙 유형을 고릅니다.

![새 인터페이스 만들기](https://www.palantir.com/docs/resources/foundry/action-types/action_on_interface_new_interface.png)

2. 액션에 포함할 공유 속성을 추가합니다(해당하는 경우).
3. 액션 타입을 설명하는 메타데이터를 추가합니다. 이 메타데이터는 인터페이스를 구현하는 모든 객체 타입에 적용된다는 점을 기억하세요.
4. **Submission criteria**(제출 조건) 아래에서 액션을 실행할 수 있는 사용자를 고릅니다(더 복잡한 조건은 나중에 적용할 수 있습니다). 이 권한은 사용자가 편집 권한을 가지고 있는 한, 인터페이스를 구현하는 모든 객체 타입에 적용된다는 점을 기억하세요.
5. **Create**를 선택해 액션 타입을 완성합니다.

<a id="create-actions-on-interfaces"></a>
### 인터페이스에 대한 "Create" 액션

액션 타입이 인터페이스에만 연결되어 있으므로, 어떤 객체 타입을 생성할지 나타내는 "Object type"(객체 타입) 파라미터가 자동으로 생성됩니다. 폼이나 테이블을 사용하면 사용자에게 목록에서 객체 타입을 고르라는 안내가 나옵니다.

![인터페이스에 대한 Create 액션](https://www.palantir.com/docs/resources/foundry/action-types/action_on_interface_create_action.png)

**객체는 기본 키(primary key) 없이 생성할 수 없습니다**. 따라서 규칙에서 기본 키가 지정되지 않은 객체 타입은 제출 시 실패합니다. 이런 실패를 피하려면, 인터페이스와 Create 규칙 모두에 인터페이스를 구현하는 객체 타입들에서 기본 키로 쓸 수 있는 인터페이스 속성을 포함하세요.

![기본 키가 없는 인터페이스 액션](https://www.palantir.com/docs/resources/foundry/action-types/action_on_interface_primary_key.png)

**설명**: 데이터베이스에서 `INSERT`를 할 때 기본 키 열 값이 없으면 행을 넣을 수 없는 것과 같습니다. 예를 들어 `Bug`의 기본 키가 `ticketId`이고 `FeatureRequest`의 기본 키가 `requestId`라면, `Ticket` 인터페이스에는 둘 다 없으므로 Create 액션이 기본 키 값을 채울 수 없습니다. 해결책은 `Ticket` 인터페이스에 `ticketId` 같은 공유 속성을 두고, 각 구현 객체 타입이 그 속성을 기본 키로 쓰도록 맞추는 것입니다.

<a id="modify-actions-on-interfaces"></a>
### 인터페이스에 대한 "Modify" 액션

인터페이스의 "Modify" 규칙은 구성된 인터페이스의 어떤 객체든 수정할 수 있습니다. 선택한 인터페이스로 제한된 "interface reference"(인터페이스 참조) 파라미터가 생성됩니다. "interface reference" 파라미터는 "object reference"(객체 참조) 파라미터와 비슷하지만, 인터페이스를 구현하는 모든 타입의 객체를 보여 준다는 점이 다릅니다. 폼이나 테이블을 사용하면 사용자는 목록에서 객체를 고를 수 있습니다.

기본 키 값은 어떤 액션 타입으로도 *수정할 수 없습니다*. 따라서 선택된 객체 타입의 기본 키 속성을 수정하려는 액션은 제출 시 실패합니다. 인터페이스를 구현하는 객체 타입 중 일부가 기본 키로 사용할 가능성이 있는 속성을 액션 규칙이 수정하지 않도록 항상 확인하세요.

아래 예에서 "Title" 속성이 "Bug" 객체 타입의 기본 키로 잘못 사용되고 있습니다. "Edit ticket" 액션은 버그의 기본 키를 바꾸려 하므로 제출 시 실패합니다.

![기본 키를 수정하는 인터페이스 액션](https://www.palantir.com/docs/resources/foundry/action-types/action_on_interface_primary_key_modify.png)

**설명**: 예를 들어 `Edit ticket` 액션이 `title`을 수정하도록 되어 있다고 합시다. `FeatureRequest`는 기본 키가 `requestId`이므로 `title`을 바꿔도 문제가 없지만, `Bug`는 `title`이 기본 키이므로 같은 액션이 `Bug`에 대해서는 실패합니다. 같은 인터페이스 액션이 객체 타입에 따라 성공하기도 하고 실패하기도 하는 것입니다. 기본 키는 객체의 정체성(identity)이므로 바뀌면 다른 객체가 되기 때문에 수정이 금지됩니다.

<a id="delete-actions-on-interfaces"></a>
### 인터페이스에 대한 "Delete" 액션

"Delete" 액션 규칙에는 객체 참조 파라미터 대신 "interface reference" 파라미터를 지정할 수 있습니다. 특정 인터페이스로 제한된 이 인터페이스 참조가 삭제할 객체를 나타냅니다. 폼이나 테이블을 사용하면 사용자는 목록에서 객체를 고를 수 있습니다.

<a id="create-link-actions-on-interfaces"></a>
### 인터페이스에 대한 "Create link" 액션

"Create interface link"(인터페이스 링크 생성) 규칙을 사용하면 인터페이스에 정의된 인터페이스 링크 제약(interface link constraint)을 이용해 링크를 생성할 수 있습니다. "Create interface link" 규칙을 구성하려면 다음과 같이 합니다.

1. 링크를 생성할 인터페이스를 선택합니다.
2. 인터페이스에 정의된 인터페이스 링크 제약을 선택합니다. 링크 제약이 두 인터페이스 사이에 있으면 출발(source)과 도착(destination) 파라미터가 모두 인터페이스 참조 파라미터로 자동 생성됩니다. 링크 제약이 인터페이스와 객체 타입 사이에 있으면 출발은 인터페이스 참조 파라미터, 도착은 객체 참조 파라미터가 됩니다.

액션이 자동 생성한 파라미터를 쓰고 싶지 않다면, 출발 객체와 도착 객체를 수동으로 구성할 수도 있습니다. 다음 중 하나일 수 있습니다.

* 기존 객체를 참조하는 인터페이스 참조 파라미터 또는 객체 참조 파라미터.
* 같은 액션 타입 안의 "Create object" 또는 "Create object(s) of interface" 규칙으로 생성된 객체.

**주의**: 객체 타입에 해당 링크 제약에 대한 구체적인 링크 구현이 여러 개 있으면 액션은 실패합니다. 또한 일대다(one-to-many) 링크를 생성하면 관계의 "다(many)" 쪽에 있는 외래 키가 수정됩니다. 액션 타입이 "Create object"나 "Modify object(s)" 규칙으로 같은 외래 키도 수정한다면 충돌이 없는지 확인하세요.

**설명**: 인터페이스 링크 제약은 "`Ticket`은 `Person`과 assignee 관계로 링크될 수 있다"처럼 인터페이스 수준에서 선언한 관계이고, 실제 링크 타입은 각 객체 타입이 구현합니다(예: `Bug`와 `Employee` 사이의 `bugAssignee` 링크 타입). 한 객체 타입이 같은 제약을 구현하는 링크 타입을 둘 이상 가지면 어느 것을 써야 할지 모호하므로 생성이 실패합니다. 외래 키 주의 사항은 데이터베이스 설계와 직접 연결됩니다. 일대다 링크는 보통 "다" 쪽 테이블의 외래 키 열(예: `bug.assignee_id`)로 표현되므로, 링크를 만드는 것은 그 열에 값을 쓰는 것입니다. 같은 액션의 다른 규칙이 `assignee_id`에 다른 값을 쓰면 두 쓰기가 충돌합니다.

<a id="delete-link-actions-on-interfaces"></a>
### 인터페이스에 대한 "Delete link" 액션

"Delete interface link"(인터페이스 링크 삭제) 규칙을 사용하면 인터페이스에 정의된 인터페이스 링크 제약을 이용해 링크를 삭제할 수 있습니다. "Delete interface link" 규칙을 구성하려면 다음과 같이 합니다.

1. 링크를 삭제할 인터페이스를 선택합니다.
2. 인터페이스에 정의된 인터페이스 링크 제약을 선택합니다. 링크 제약이 두 인터페이스 사이에 있으면 출발과 도착 파라미터가 모두 인터페이스 참조 파라미터로 자동 생성됩니다. 링크 제약이 인터페이스와 객체 타입 사이에 있으면 출발은 인터페이스 참조 파라미터, 도착은 객체 참조 파라미터가 됩니다.

자동 생성된 파라미터 대신 출발 객체와 도착 객체를 수동으로 구성할 수도 있습니다. 이 경우 기존 객체를 참조하는 파라미터(인터페이스 참조 파라미터 또는 객체 참조 파라미터)여야 합니다.

**주의**: 객체 타입에 해당 링크 제약에 대한 구체적인 링크 구현이 여러 개 있으면, 액션은 모든 구체적인 링크 구현을 삭제하려고 시도합니다.

**설명**: 생성과 삭제의 동작이 다르다는 점에 유의하세요. 링크 구현이 여러 개일 때 생성은 어느 쪽에 만들지 정할 수 없어 실패하지만, 삭제는 해당하는 모든 구현에서 링크를 지우려고 합니다. 또 삭제는 이미 존재하는 링크를 지우는 것이므로, 같은 액션 안에서 새로 생성된 객체는 출발/도착으로 쓸 수 없고 기존 객체를 가리키는 파라미터만 쓸 수 있습니다.

<a id="executing-actions-on-interfaces"></a>
### 인터페이스에 대한 액션 실행하기 (Executing actions on interfaces)

인터페이스 액션 규칙으로 만든 액션은 객체 타입별 액션 타입과 마찬가지로, 그 인터페이스를 구현하는 객체 타입의 객체에 적용할 수 있습니다. 특정 객체에 대해서는 그 객체에 적용할 수 있는 모든 객체 타입별 액션과 인터페이스 기반 액션이 액션 드롭다운에 나타납니다.

> **중간 요약**: 인터페이스 액션 규칙은 인터페이스의 공유 속성만 다룰 수 있습니다. Create는 객체 타입 파라미터가 자동 생성되며 기본 키로 쓸 인터페이스 속성이 필요하고, Modify는 기본 키 속성을 건드리면 실패합니다. 링크 생성/삭제는 인터페이스 링크 제약을 기반으로 하며, 링크 구현이 여러 개일 때 생성은 실패하고 삭제는 모두 지우려 합니다.

<a id="permissions"></a>
## 권한 (Permissions)

인터페이스 액션 규칙은 객체 액션 타입과 같은 권한을 따릅니다.

자세한 내용은 [액션 타입 권한](19_permissions.md) 문서를 참고하세요.

<a id="level-of-support"></a>
## 지원 수준 (Level of support)

인터페이스 액션 규칙과 참조 파라미터에 대한 지원이 확대되는 과정에 있으므로, Palantir 플랫폼 전반에서 사용 가능 여부가 다를 수 있습니다.

<a id="supported-applications-and-services"></a>
### 지원되는 애플리케이션과 서비스 (Supported applications and services)

* **Ontology Manager:** 인터페이스 액션 타입 생성, 그리고 제출 조건과 재정의(override)에서 인터페이스 파라미터 구성.
* **Object Explorer와 Object Views:** 인터페이스에 정의된 액션 렌더링.

<a id="limitations-of-interface-action-rules"></a>
### 인터페이스 액션 규칙의 제한 사항 (Limitations of interface action rules)

* 제출 조건이 인터페이스를 구현하는 모든 객체 타입에 똑같이 적용되므로, 하나의 인터페이스 액션 안에서 객체 타입별로 다른 권한을 구성할 수 없습니다. 접근을 제한하려면 [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)에서 해당 객체 타입의 **Interfaces** 탭을 선택하고 **Interface action control**(인터페이스 액션 통제) 섹션에서 인터페이스로부터 상속된 액션에 대한 통제를 설정해, 특정 객체 타입에 대해 인터페이스 액션을 비활성화하세요. 인터페이스 액션에 더 세분화된 권한 통제를 적용하는 기능은 현재 활발히 개발 중입니다.
* 액션 로그(action log)는 아직 지원되지 않습니다.
* 인터페이스에 대한 액션은 함수와 함께 사용할 수 없습니다.

**설명**: 예를 들어 `Ticket` 인터페이스 액션의 제출 조건이 "Support 그룹"이라면, Support 그룹 구성원은 (객체 편집 권한이 있는 한) `Bug`와 `FeatureRequest` 모두에 이 액션을 쓸 수 있습니다. `FeatureRequest`는 Product 그룹만 다루게 하고 싶다면, 액션 하나 안에서 객체 타입별로 조건을 나눌 수 없으므로 `FeatureRequest` 객체 타입의 Interfaces 탭에서 이 인터페이스 액션을 비활성화해야 합니다.

> **중간 요약**: 인터페이스 액션은 객체 액션 타입과 같은 권한 체계를 따르며, Ontology Manager, Object Explorer, Object Views에서 지원됩니다. 객체 타입별로 다른 제출 조건은 둘 수 없어 Interface action control로 비활성화해야 하고, 액션 로그와 함수는 지원되지 않습니다.

## 정리

- 인터페이스 액션은 인터페이스를 구현하는 모든 객체 타입에 적용되는 범용 액션이며, 인터페이스 액션 규칙과 인터페이스 참조 파라미터로 구성합니다.
- 규칙은 인터페이스의 공유 속성만 다룰 수 있고, 기본 키 문제(생성 시 기본 키 필요, 수정 시 기본 키 변경 불가)를 구현 객체 타입 전체에 대해 확인해야 합니다.
- 링크 생성/삭제는 인터페이스 링크 제약을 기반으로 하며, 링크 구현이 여러 개이거나 외래 키를 다른 규칙이 함께 수정하면 문제가 생길 수 있습니다.
- 제출 조건은 모든 구현 객체 타입에 똑같이 적용되므로 필요하면 객체 타입별로 Interface action control에서 비활성화하고, 액션 로그와 함수는 아직 지원되지 않습니다.
