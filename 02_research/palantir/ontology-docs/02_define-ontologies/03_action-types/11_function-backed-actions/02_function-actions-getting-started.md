# 함수 기반 액션 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/action-types/function-actions-getting-started/
- 사이드바 위치: Define Ontologies > Action types > Function-backed actions > Getting started

이 페이지는 함수(function)가 실제 편집(edit) 로직을 담당하는 액션 타입, 즉 함수 기반 액션(function-backed action)을 처음부터 만드는 과정을 따라가는 튜토리얼입니다. 액션 타입의 기본 규칙만으로는 표현하기 어려운 계산이나 조건부 수정이 필요할 때 코드로 작성한 함수를 액션에 연결합니다. 함수 버전을 올리는 방법과 자동 업그레이드(auto upgrade)를 켤 때의 보안, 호환성 주의점도 함께 다룹니다.

이 튜토리얼은 [온톨로지 편집 함수(Ontology Edit function)](../../04_functions/09_language-agnostic-features/01_edits-overview.md)를 기반으로 하는 액션 타입을 만드는 방법을 설명합니다.

<a id="prerequisites"></a>
## 사전 준비 (Prerequisites)

이 튜토리얼에서는 [액션 시작하기 튜토리얼](../02_getting-started.md)과 같은 `Demo Ticket` 객체 타입과 샘플 객체를 사용합니다.

먼저 액션이 수행할 편집을 실행하는 온톨로지 편집 함수를 작성합니다. 이를 위해 다음이 필요합니다.

* functions on objects TypeScript 템플릿으로 리포지토리를 설정하기
* 관련 객체 타입을 리포지토리로 가져오기(import)
* 액션이 읽을 수 있도록 온톨로지 편집 함수를 게시(publish)하기

이 단계들에 대한 정보는 함수 문서에서 찾을 수 있습니다.

* **[시작하기](../../04_functions/03_getting-started.md):** 이 튜토리얼을 따라 기본 함수 리포지토리를 만들고 함수를 게시합니다.
* **[객체에 대한 함수(Functions on objects)](../../04_functions/13_functions-on-objects/01_functions-on-objects.md):** 이 튜토리얼을 따라 객체 데이터를 사용하는 함수를 만듭니다.
* **[온톨로지 편집(Ontology edits)](../../04_functions/12_typescript-v1/03_api-ontology-edits.md):** 이 레퍼런스를 참고해 온톨로지 편집 함수를 만듭니다.

온톨로지 편집 함수를 작성하고 게시했다면, 아래 단계에 따라 함수를 액션에 연결하여 이 함수로 객체를 편집할 수 있게 합니다. 이 튜토리얼에서는 리포지토리에서 다음과 같은 온톨로지 편집 함수를 작성하고 게시해 두었습니다.

![온톨로지 편집 함수](https://www.palantir.com/docs/resources/foundry/action-types/function_backed_actions_ontology_edit_function.png)

편의를 위해 코드를 여기에도 실어 둡니다.

```typescript
@OntologyEditFunction()
public addPriorityToTitle(ticket: DemoTicket): void {
    let newTitle: string = "[" + ticket.ticketPriority + "]" + ticket.ticketTitle;
    ticket.ticketTitle = newTitle;
}
```

**설명**: 이 함수는 `DemoTicket` 객체 하나를 입력으로 받고 반환값은 없습니다(`void`). 대신 입력 객체의 `ticketTitle` 속성(property)을 직접 바꿉니다. 예를 들어 우선순위가 `High`이고 제목이 `Login fails`인 티켓이 들어오면 제목이 `[High]Login fails`로 바뀝니다. 핵심은 마지막 줄의 대입문 `ticket.ticketTitle = newTitle`입니다. 일반 프로그램에서는 메모리의 객체 필드만 바뀌지만, 온톨로지 편집 함수에서는 이 대입이 "이 객체의 이 속성을 이 값으로 바꾼다"는 편집 기록으로 수집되고, 액션이 실행될 때 실제 온톨로지에 반영됩니다. 함수 위의 `@OntologyEditFunction()`은 TypeScript 데코레이터로, 이 함수가 편집을 만들어 내는 함수임을 플랫폼에 알립니다.

**주의**: 액션 타입에서 사용할 함수에는 `@Function()` 대신 `@OntologyEditFunction()` 어노테이션을 붙여야 합니다. 자세한 내용은 [객체에 대한 함수](../../04_functions/12_typescript-v1/03_api-ontology-edits.md#declaring-an-edit-function) 문서를 참고하세요.

> **중간 요약**: 함수 기반 액션을 만들려면 먼저 `@OntologyEditFunction()`이 붙은 온톨로지 편집 함수를 작성해 게시해야 합니다. 예제 함수는 티켓 제목 앞에 우선순위를 붙이는 편집을 수행합니다.

<a id="creating-a-function-backed-action"></a>
## 함수 기반 액션 만들기 (Creating a function-backed action)

**Rules** 섹션에서 **Function** 타입의 규칙을 하나만 추가합니다. [사전 준비](#prerequisites) 단계에서 게시한 함수를 검색해 최신 버전을 선택합니다. 아래처럼 입력(input)이 액션 파라미터와 맞아떨어지도록 구성합니다. 함수 규칙은 [다른 온톨로지 규칙](../06_rules.md#ontology-rules)과 함께 사용할 수 없습니다.

![입력 구성](https://www.palantir.com/docs/resources/foundry/action-types/function_backed_actions_configure_inputs.png)

함수를 선택하면 함수의 모든 입력이 자동으로 파라미터로 만들어져 **Parameters** 탭에 추가됩니다. 이 스크린샷의 예에서는 **Object reference**(객체 참조) 타입의 `Demo Ticket` 파라미터가 만들어졌습니다. 필요하면 이 파라미터를 더 세부적으로 설정할 수 있습니다.

![Demo Ticket](https://www.palantir.com/docs/resources/foundry/action-types/function_backed_actions_demo_ticket.png)

![Demo Ticket 상세](https://www.palantir.com/docs/resources/foundry/action-types/function_backed_actions_demo_ticket_details.png)

액션을 저장한 뒤, [다른 애플리케이션과의 통합 안내](../04_use-actions.md)에 설명된 대로 플랫폼 곳곳에서 액션을 구성합니다.

**설명**: 함수의 시그니처 `addPriorityToTitle(ticket: DemoTicket)`에서 매개변수 `ticket`이 액션의 `Demo Ticket` 파라미터로 자동 변환됩니다. 사용자가 액션 폼에서 티켓 하나를 고르면 그 객체가 함수의 `ticket` 인자로 전달되는 구조입니다. "함수 규칙은 다른 규칙과 함께 쓸 수 없다"는 말은, 한 액션 안에서 "객체 수정" 같은 기본 규칙과 함수 규칙을 섞을 수 없고 모든 편집을 함수가 책임진다는 뜻입니다.

> **중간 요약**: Rules 섹션에 Function 규칙 하나를 추가하고 게시한 함수를 고르면, 함수의 입력이 액션 파라미터로 자동 생성됩니다. 함수 규칙은 다른 온톨로지 규칙과 함께 쓸 수 없습니다.

<a id="changing-function-version"></a>
## 함수 버전 변경 (Changing function version)

기본적으로 함수 로직이 바뀌어도 액션이 자동으로 따라 업데이트되지는 않습니다. 대신 액션의 **Rules** 섹션으로 돌아가 액션이 참조하는 함수의 버전을 올려야 합니다. 예를 들어 함수의 0.1.2 버전을 게시했다면 여기에서 버전을 업데이트해야 합니다.

![함수 버전을 업데이트하는 방법](https://www.palantir.com/docs/resources/foundry/action-types/function_backed_actions_update_function_logic.png)

**설명**: 액션은 기본적으로 함수의 특정 버전 하나(예: 0.1.1)에 고정되어 있습니다. 소프트웨어 패키지 의존성을 `==0.1.1`처럼 정확한 버전으로 고정해 두는 것과 같은 방식입니다. 이렇게 하면 누군가 함수를 고쳐 새 버전을 게시해도 이미 사용 중인 액션의 동작은 바뀌지 않으므로, 예상치 못한 변화를 막을 수 있습니다.

<a id="auto-upgrades"></a>
### 자동 업그레이드 (Auto upgrades)

선택적으로, 액션이 참조하는 함수에 대해 자동 업그레이드를 켤 수 있습니다. 이 옵션을 켜면 액션은 [버전 범위(version range)](../../04_functions/08_function-consumption/04_version-range-dependencies-for-functions.md)로 함수에 의존하며, 런타임에 [버전을 결정(resolve)](../../04_functions/08_function-consumption/04_version-range-dependencies-for-functions.md#version-range-resolution)합니다.

액션에 자동 업그레이드를 켜려면 액션의 **Rules** 섹션으로 이동해 **Function** 파라미터를 선택합니다. **Function** 드롭다운에서 실행하려는 함수의 최소 버전을 선택하고 **Auto upgrade** 옵션을 켭니다. 이는 선택한 최소 버전의 하위 호환되는 모든 버전(예: 마이너 또는 패치 업그레이드)을 포함하는 버전 범위 의존성에 해당합니다.

![함수 기반 액션에서 자동 업그레이드를 켜는 방법](https://www.palantir.com/docs/resources/foundry/action-types/function_backed_actions_auto_upgrade.png)

**참고**: `0.y.z` 형식의 함수 버전에서는 자동 업그레이드를 사용할 수 없습니다. 이 버전들은 함수 API와 동작이 자주 바뀔 수 있는 초기 개발용으로 예약되어 있어 안정적이라고 볼 수 없습니다. [릴리스 버전 선택](../../04_functions/07_function-management/01_functions-versioning.md#choosing-a-release-version) 문서를 참고하세요.

**설명**: 버전 번호는 시맨틱 버저닝(semantic versioning) 규칙인 `주(major).부(minor).패치(patch)`를 따릅니다. 하위 호환이 깨지는 변경이면 주 버전을, 기능 추가면 부 버전을, 버그 수정이면 패치 버전을 올립니다. 예를 들어 최소 버전을 1.2.0으로 고르고 자동 업그레이드를 켜면 1.2.1, 1.3.0 등은 자동으로 쓰이지만 2.0.0은 쓰이지 않습니다. 주 버전이 0인 `0.y.z`는 아직 개발 중이라는 의미이므로 자동 업그레이드 대상에서 빠집니다.

<a id="security"></a>
#### 보안 (Security)

함수 기반 액션에 자동 업그레이드가 켜져 있으면, [액션에 대한 편집 권한](../../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#permissions-for-editing-link-types)이 없는 사용자도 백킹 함수를 변경함으로써 액션의 동작을 바꿀 수 있습니다. 함수에 대한 편집 권한이 액션에 대한 권한과 연결되어 있지 않기 때문입니다.

<a id="breaking-changes"></a>
#### 호환성을 깨는 변경 (Breaking changes)

잘못된 함수 릴리스에 [호환성을 깨는 변경](../../04_functions/08_function-consumption/04_version-range-dependencies-for-functions.md#risks)이 들어 있으면 자동 업그레이드 때문에 액션 실행이 실패할 수 있습니다.

<a id="provenance"></a>
#### 출처 범위 (Provenance)

액션의 provenance(출처 범위)는 선택한 최소 함수 버전의 provenance에 따라 설정됩니다. 함수의 새 릴리스가 이 provenance 밖의 편집(예: 추가된 다른 객체 타입에 대한 편집)을 반환하면 액션 실행이 실패합니다. 현재 provenance는 액션이 런타임에 편집할 수 있는 객체 타입들로만 구성됩니다.

**설명**: 예를 들어 최소 버전 1.2.0의 함수가 `Demo Ticket` 객체만 편집한다면, 이 액션의 provenance는 `{Demo Ticket}`으로 정해집니다. 나중에 1.3.0 버전이 `Demo Ticket`과 함께 `Comment` 객체도 편집하도록 바뀌면, 이 편집은 정해진 범위 밖이므로 액션 실행이 실패합니다. 이 경우 액션의 최소 버전을 새로 골라 provenance를 갱신해야 합니다.

> **중간 요약**: 기본적으로 액션은 함수의 특정 버전에 고정되며 새 버전을 쓰려면 직접 올려야 합니다. 자동 업그레이드를 켜면 하위 호환 버전이 런타임에 자동 적용되지만, 권한 우회, 잘못된 릴리스로 인한 실패, provenance 범위를 벗어난 편집으로 인한 실패에 주의해야 합니다.

## 정리

- 함수 기반 액션은 `@OntologyEditFunction()`으로 작성해 게시한 온톨로지 편집 함수를 액션의 Rules 섹션에 Function 규칙으로 연결해 만듭니다.
- 함수의 입력은 액션 파라미터로 자동 생성되고, 함수 규칙은 다른 온톨로지 규칙과 함께 쓸 수 없습니다.
- 액션은 기본적으로 특정 함수 버전에 고정되므로, 함수를 고친 뒤에는 Rules 섹션에서 버전을 올려야 합니다.
- 자동 업그레이드를 켜면 최소 버전 이상의 하위 호환 버전이 런타임에 적용되며, `0.y.z` 버전에는 쓸 수 없습니다.
- 자동 업그레이드에는 함수 편집자를 통한 동작 변경, 호환성 깨짐, provenance 위반에 따른 실행 실패 위험이 따릅니다.
