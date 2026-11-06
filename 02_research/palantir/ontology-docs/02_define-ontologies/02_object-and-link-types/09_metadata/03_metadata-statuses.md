# 상태 (Statuses)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/metadata-statuses/
- 사이드바 위치: Define Ontologies > Object and link types > Metadata > Statuses

이 페이지는 온톨로지 리소스(객체 타입, 속성, 링크 타입, 액션, 인터페이스)에 붙는 개발 상태(status) 값과, 상태에 따라 금지되는 작업, 상태를 바꾸는 방법, 객체 타입과 링크 타입 사이의 상태 일관성 규칙을 설명합니다. 상태는 "이 리소스를 운영 애플리케이션에서 믿고 써도 되는가"를 알려 주는 표식이므로, 여러 팀이 같은 온톨로지를 공유할 때 실수로 쓰이는 리소스를 지우거나 바꾸는 일을 막아 줍니다.

<a id="available-status-values"></a>
## 상태 개요

온톨로지의 모든 객체 타입, 속성(property), 링크 타입, 액션, 인터페이스에는 개발 단계를 나타내는 **상태(status)가** 있습니다. 온톨로지 리소스의 상태는 active, experimental, deprecated, example 중 하나이며, 객체 타입은 추가로 [promoted](#promoted-status-object-types-only)로 분류될 수도 있습니다. 상태 메타데이터는 온톨로지를 편집하는 사용자가 어떤 리소스를 사용자 애플리케이션이 실제로 의존하고 있는지 알 수 있게 도와줍니다. 이 상태들은 [**Object Explorer**](../../../05_applications/01_object-explorer/01_overview.md), [**Object Views**](../../../05_applications/03_object-views/01_overview.md), [**Workshop**](https://www.palantir.com/docs/foundry/workshop/overview/)에서 볼 수 있으며, 어떤 객체 타입이 사용자 애플리케이션에서 쓰이도록 의도된 것인지에 대한 정보를 더 제공합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/statuses-active.png" alt="Active 상태" width="400" />

상태는 다음 다섯 가지 값 중 하나를 가질 수 있습니다.

<a id="available-status-values"></a><a id="promoted-status-object-types-only"></a>
## 사용 가능한 상태 값 (Available Status Values)

* **Promoted(객체 타입 전용):** 객체 타입이 온톨로지 소유자의 검증을 거친 핵심적이고 신뢰할 수 있는 리소스임을 나타냅니다. `Promoted` 객체 타입은 API 이름에 대해 `active` 객체 타입과 비슷한 보호를 물려받습니다.
* **Active:** 리소스가 사용자 대상 애플리케이션에서 실제로 사용 중이며, Ontology Manager에서 큰 호환성 파괴 변경(breaking change)이 이루어지지 않을 것임을 나타냅니다.
* **Experimental:** 리소스가 아직 개발 중임을 나타냅니다. 실험 단계 항목은 사용자 대상 애플리케이션에서 쓸 수 없게 되는 변경이 일어날 수 있습니다.
* **Deprecated:** 리소스가 곧 삭제될 것임을 나타냅니다. 지원 중단된 항목에 사용자 대상 애플리케이션이 의존해서는 안 됩니다.
  * 지원 중단된 리소스에는 다음을 포함하는 메타데이터도 있습니다.
    * 지원 중단 이유에 대한 설명
    * 시스템에서 삭제될 것으로 예상되는 기한
    * 지원 중단되는 리소스를 대체할 리소스
* **Example:** 리소스가 예제로 설치되었음을 나타냅니다. 예제 리소스는 가상의(notional) 것으로, 교육이나 초기 단계의 탐색적 사용에만 적합합니다. 예제는 운영(production) 워크플로에서 사용하도록 의도된 것이 *아닙니다*.

**설명**: 호환성 파괴 변경(breaking change)은 기존 사용자의 코드나 화면이 더 이상 동작하지 않게 만드는 변경입니다. 예를 들어 Workshop 모듈이 `Employee` 객체 타입의 `hire_date` 속성을 API 이름으로 참조하고 있는데 그 속성을 지우거나 API 이름을 `start_date`로 바꾸면 그 모듈은 깨집니다. `active` 상태는 이런 변경을 막겠다는 약속이고, `experimental`은 아직 그런 약속이 없다는 뜻입니다.

<a id="operations-that-are-not-allowed"></a>
### `Promoted` 상태 (객체 타입 전용)

객체 타입은 온톨로지 안에서 더 높은 수준의 신뢰와 공식적 지위를 나타내는 특별한 `promoted` 상태를 지원합니다. 새로운 보라색 체크 표시 아이콘으로 표시되는 이 상태는, 사용자가 핵심적이고 재사용 가능한 객체 타입을 특정 사용 사례 전용이거나 실험적인 객체 타입과 구별하는 데 도움을 줍니다.

`promoted` 상태는 표준 `active` 상태보다 더 두드러지게 보입니다. 이 상태의 객체 타입은 높은 기준을 지키며 중앙 팀이 관리하는 "핵심(core)" 리소스로 간주됩니다. `Promoted` 객체 타입은 삭제 제한처럼 `active` 상태가 가진 운영상의 보호를 비슷하게 물려받습니다.

`promoted` 상태의 주요 특징은 다음과 같습니다.

* **범위(Scope):** `promoted` 상태는 객체 타입에만 적용됩니다. 속성, 링크 타입, 액션 타입, 인터페이스에는 사용할 수 없습니다.
* **가시성(Visibility):** 객체 타입의 상태를 `promoted`로 설정하면 가시성이 자동으로 `prominent`로 설정되어 플랫폼 전반에서 더 쉽게 발견됩니다. 사용자는 선택적으로 객체 타입의 모든 속성을 `active` 상태로 옮길 수 있습니다.
* **권한(Permissions):**
  * 온톨로지 수준에서 `Ontology Owner` 역할을 가진 사용자만 `promoted` 상태를 직접 적용할 수 있습니다.
  * 다른 사용자는 이 상태를 적용하려면 제안(proposal)을 제출해 온톨로지 수준의 `Ontology Owner`에게 검토와 승인을 받아야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/promoted-example.png" alt="Promoted 객체 타입 예시" width="400"/>

> **중간 요약**: 상태는 Promoted(객체 타입 전용), Active, Experimental, Deprecated, Example 다섯 가지입니다. Promoted는 중앙에서 관리되는 핵심 객체 타입을 뜻하며, `Ontology Owner`만 직접 적용할 수 있고 다른 사용자는 제안을 통해 승인을 받아야 합니다.

<a id="edit-a-status"></a><a id="operations-that-are-not-allowed"></a>
## 허용되지 않는 작업 (Operations that are not allowed)

애플리케이션이 온톨로지 리소스에 의존하므로, 리소스의 상태가 `active`이면 파괴적일 수 있는 몇 가지 작업이 허용되지 않습니다.

* 삭제할 수 없습니다. 리소스를 삭제하려면 먼저 상태가 `experimental` 또는 `deprecated`여야 합니다.
* active 리소스의 API 이름은 변경할 수 없습니다. API 이름 변경은 `experimental`로 표시된 리소스에서만 가능합니다.

> **중간 요약**: `active` 리소스는 삭제할 수 없고 API 이름도 바꿀 수 없습니다. 이런 작업을 하려면 먼저 상태를 바꿔야 합니다.

<a id="bulk-edit-statuses"></a><a id="edit-a-status"></a>
## 상태 편집 (Edit a status)

기본적으로 새로 만든 온톨로지 리소스에는 `experimental` 상태가 주어집니다. 상태를 바꾸려면 다음을 수행합니다.

1. 현재 상태 옆의 드롭다운을 선택합니다.
2. 새 상태를 선택합니다.

리소스를 `deprecated` 상태로 바꿀 때는 다음을 입력하라는 안내가 나옵니다.

* 지원 중단 이유에 대한 설명
* 시스템에서 삭제될 것으로 예상하는 기한
* 선택 사항으로, 지원 중단하는 리소스를 대체할 리소스

이 상태들은 Object Explorer, Object Views, Workshop에서 볼 수 있으며, 어떤 객체 타입이 사용자 애플리케이션에서 쓰이도록 의도된 것인지에 대한 정보를 더 제공합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-status-change-status.png" alt="상태 변경" width="400" />

Ontology Manager는 객체 타입과 그에 딸린 속성이나 링크 타입 사이의 상태 일관성을 보장합니다. 예를 들어 객체 타입이 `active`에서 `experimental`로 바뀌면, 그 객체 타입의 모든 속성도 `experimental`로 표시됩니다.

아래 표는 상태가 서로 다른 객체 타입 사이의 링크 타입이 가질 수 있는 상태를 나타냅니다. 일반적으로는 다음과 같습니다.

* 링크 타입의 객체 타입 중 하나라도 `experimental`로 바뀌면, 링크 타입은 자동으로 `experimental`로 바뀝니다.
* 링크 타입의 객체 타입 중 하나라도 `example`로 바뀌면, 링크 타입은 자동으로 `example`로 바뀝니다.
* 링크 타입의 객체 타입 중 하나라도 `deprecated`로 바뀌면, 링크 타입은 자동으로 `deprecated`로 바뀝니다.

| *객체 타입 A가…* (행) / 객체 타입 B가… (열) | EXPERIMENTAL | ACTIVE | DEPRECATED |
|---|---|---|---|
| *EXPERIMENTAL* | experimental만 가능 | experimental만 가능 | deprecated만 가능 |
| *ACTIVE* | experimental만 가능 | experimental, active, deprecated 중 하나 가능 | deprecated만 가능 |
| *DEPRECATED* | deprecated만 가능 | deprecated만 가능 | deprecated만 가능 |

(원문 표는 머리글이 두 줄로 나뉘어 있어, 여기서는 행이 객체 타입 A의 상태, 열이 객체 타입 B의 상태를 뜻하도록 하나의 머리글로 합쳤습니다.)

링크 타입의 외래 키(foreign key)에도 같은 요구 사항이 적용됩니다. 애플리케이션은 속성을 변경할 때 링크 타입의 상태를 다음과 같이 바꿉니다.

* 외래 키 속성이 `experimental`로 바뀌면, 그 링크 타입은 `experimental`로 바뀝니다.
* 외래 키 속성이 `example`로 바뀌면, 그 링크 타입은 `example`로 바뀝니다.
* 외래 키 속성이 `deprecated`로 바뀌면, 그 링크 타입은 `deprecated`로 바뀝니다.

애플리케이션은 유효하지 않은 상태를 막기 위해 상태를 바꿉니다. 외래 키 속성이 `experimental`이고 아직 개발 중이라면, 그 링크 타입은 `active`로 표시되어 운영 환경에서 의존되어서는 안 됩니다. 반대로 속성을 `active`로 표시할 때는, 그 속성을 외래 키로 참조하는 링크 타입을 애플리케이션이 `active`로 바꾸지 않습니다. 외래 키 속성은 운영 중이면서 링크 타입과 그 백킹 데이터소스(backing datasource)는 아직 개발 중인 상태가 유효하기 때문입니다.

**설명**: 규칙의 핵심은 "링크 타입은 그것이 의존하는 대상보다 더 안정적인 상태일 수 없다"는 것입니다. 예를 들어 `Employee`(active)와 `Department`(experimental)를 잇는 `works_in` 링크 타입은 `Employee.department_id` 외래 키와 `Department` 객체 타입에 의존합니다. `Department`가 아직 바뀔 수 있는데 `works_in`만 active로 약속하면 그 약속을 지킬 수 없으므로 링크 타입은 experimental로 내려갑니다. 반대 방향(`department_id` 속성만 active로 올리는 경우)은 링크 타입이 덜 안정적인 상태로 남는 것이라 문제가 없으므로 자동으로 바꾸지 않습니다.

> **중간 요약**: 새 리소스는 `experimental`로 시작하고, 드롭다운으로 상태를 바꾸며, `deprecated`로 바꿀 때는 이유, 기한, 대체 리소스를 입력합니다. 객체 타입이나 외래 키 속성이 덜 안정적인 상태로 바뀌면 관련 링크 타입도 자동으로 따라 바뀌지만, 더 안정적인 상태로 바뀔 때는 링크 타입이 자동으로 올라가지 않습니다.

<a id="bulk-edit-statuses"></a><a id="properties"></a>
## 상태 일괄 편집 (Bulk edit statuses)

<a id="object-types"></a><a id="properties"></a>
### 속성 (Properties)

객체 타입을 `experimental`에서 `active`로 바꿀 때, 그 객체 타입의 모든 속성에도 `active` 상태를 적용하는 옵션이 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-status-apply-active-annotated.png" alt="Active 상태 적용" width="400" />

객체 타입을 `example`로 바꾸면 그 객체 타입의 모든 속성도 자동으로 `example`이 됩니다.

객체 타입의 여러 속성에 걸친 상태는 객체 타입의 **Properties** 페이지에서도 일괄 편집할 수 있습니다. [속성 일괄 편집에 대해 더 읽어 보세요.](../03_properties/02_edit-properties.md#bulk-edit-multiple-properties)

<a id="object-types"></a><a id="troubleshooting"></a>
### 객체 타입 (Object types)

여러 객체 타입에 걸친 상태도 홈 페이지의 객체 타입 보기 페이지에서 일괄 편집할 수 있습니다. 편집할 객체 타입의 체크박스를 선택한 뒤 표 오른쪽 위의 **Edit status** 버튼을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-status-bulk-edit.png" alt="객체 타입 일괄 편집" width="400" />

> **중간 요약**: 객체 타입을 active로 올릴 때 속성까지 함께 올릴 수 있고, **Properties** 페이지와 홈 페이지의 **Edit status** 버튼으로 속성과 객체 타입의 상태를 한꺼번에 바꿀 수 있습니다.

<a id="conflicts-between-property-status-and-link-type-status"></a><a id="troubleshooting"></a>
## 문제 해결 (Troubleshooting)

<a id="conflicts-between-object-type-status-and-link-type-status"></a>
### 속성 상태와 링크 타입 상태의 충돌

`OntologyMetadata:ConflictBetweenLinkTypeStatusAndPropertyTypeStatus` 오류가 발생하면, 링크 타입의 상태와 속성의 상태가 충돌하는 것입니다. 예를 들어 외래 키가 `deprecated`라면, 그 외래 키를 참조하는 링크 타입도 `deprecated`여야 합니다.

### 객체 타입 상태와 링크 타입 상태의 충돌

`OntologyMetadata:ConflictBetweenLinkTypeStatusAndObjectTypeStatus` 오류가 발생하면, 링크 타입의 상태와 그에 연결된 객체 타입 중 하나의 상태가 충돌하는 것입니다. 위 표에 따라 유효하지 않은 객체 타입과 링크 타입 조합일 때 이런 일이 생길 수 있습니다. 예를 들어 `experimental` 객체 타입은 `active` 링크 타입을 가질 수 없습니다.

## 정리

- 모든 온톨로지 리소스는 Active, Experimental, Deprecated, Example 중 하나의 상태를 가지며, 객체 타입은 추가로 Promoted가 될 수 있습니다.
- `active` 리소스는 삭제와 API 이름 변경이 막혀 있어, 애플리케이션이 의존하는 리소스를 보호합니다.
- 새 리소스는 `experimental`로 시작하고, `deprecated`로 바꿀 때는 이유, 삭제 기한, 대체 리소스를 기록합니다.
- 링크 타입은 연결된 객체 타입과 외래 키 속성보다 더 안정적인 상태일 수 없으며, Ontology Manager가 이를 자동으로 맞춥니다. 어긋나면 `ConflictBetweenLinkTypeStatus...` 오류가 납니다.
- 상태는 속성 페이지와 홈 페이지에서 일괄 편집할 수 있습니다.
