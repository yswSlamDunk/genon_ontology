# 온톨로지 편집 (Ontology edits)

- 원문: https://www.palantir.com/docs/foundry/functions/typescript-v2-ontology-edits/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v2 > Ontology edits

이 페이지는 TypeScript v2 함수(function)에서 온톨로지 데이터를 바꾸는 편집(edit) API를 설명합니다. 편집할 엔터티를 `Edits` 타입으로 선언하는 방법, 편집 배치(edit batch)를 만드는 방법, 그리고 배치로 속성(property) 수정, 링크 추가와 제거, 객체 생성과 삭제, 구조체(struct) 속성 편집을 하는 방법을 다룹니다. 함수가 만든 편집은 액션(action)을 통해서만 실제로 반영된다는 점이 이 페이지 전체의 전제입니다.

함수는 온톨로지에서 데이터를 읽는 것 외에도 객체를 생성하고 객체의 속성과 객체 사이의 링크를 편집할 수 있습니다. 이 페이지는 함수에서 사용할 수 있는 객체 편집 API를 문서화합니다. 편집 함수의 동작 방식에 대한 자세한 내용은 [개요 페이지](../09_language-agnostic-features/01_edits-overview.md)를 참고하세요.

함수에서 만든 편집이 실제로 적용되려면, 온톨로지 편집 함수를 *[함수 기반 액션(function-backed Action)](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)으로 구성해야 합니다*. 액션을 이렇게 구성하면 추가 메타데이터를 제공하고, 권한(permission)을 구성하고, 여러 운영 인터페이스에서 그 액션을 사용할 수 있습니다. [문서](../09_language-agnostic-features/01_edits-overview.md#when-edits-are-applied)에서 언급했듯이, 액션 밖에서 편집 함수를 실행하면 실제로 객체 데이터가 수정되지 않습니다.

표준 온톨로지 편집은 편집 배치를 사용합니다. TypeScript v2는 함수 안에서 쓰기 후 읽기(read-after-write)를 보장하는 [스테이징된 쓰기(staged writes)](05_typescript-v2-staged-writes.md)도 지원합니다. 이 방식에서는 편집이 같은 실행 안의 이후 질의에 즉시 보이고, 중첩된 스테이징된 쓰기 함수 호출이 그 편집을 공유합니다. 함수가 방금 쓴 데이터를 읽어야 할 때 스테이징된 쓰기를 사용하세요. 스테이징된 쓰기는 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며 사용 중인 환경(enrollment)에서는 제공되지 않을 수 있습니다.

**주의**: 예상치 못한 검색 결과는 스테이징된 쓰기가 아니라 편집 배치에 영향을 줍니다(Unexpected search results affect edit batches, not staged writes). 편집 배치를 사용할 때 객체를 편집한 직후 그 객체를 검색하면 예상치 못한 결과가 반환될 수 있습니다. 이 주의 사항은 스테이징된 쓰기에는 해당하지 않습니다. 자세한 내용은 [주의 사항 섹션](../09_language-agnostic-features/01_edits-overview.md#edits-and-object-search)을 참고하세요.

**설명**: 편집 배치 방식에서 함수는 "무엇을 바꿀지"의 목록만 만들어 반환하고, 실제 데이터베이스 반영은 함수가 끝난 뒤 액션이 수행합니다. 그래서 함수 실행 도중에 방금 바꾼 Ticket을 검색하면 아직 반영 전인 옛 값이 나옵니다. 데이터베이스 트랜잭션에서 커밋 전의 변경이 다른 질의에 보이지 않는 상황을 생각하면 됩니다. 스테이징된 쓰기는 같은 실행 안에서는 자신의 변경을 바로 읽을 수 있게 해 주는 별도 모델입니다.

> **중간 요약**: 편집 함수의 결과는 함수 기반 액션으로 실행될 때만 실제로 반영됩니다. 기본 방식인 편집 배치에서는 함수 실행 중에 자신이 만든 편집이 검색에 보이지 않으며, 이것이 필요하면 베타 기능인 스테이징된 쓰기를 씁니다.

<a id="define-an-edit-function"></a>
## 편집 함수 정의하기 (Define an edit function)

온톨로지를 편집하는 함수는 `@osdk/functions` 패키지가 export하는 `Edits` 타입을 사용해 편집할 엔터티를 명시적으로 선언해야 합니다. 다음 예제는 `Employee`와 `Ticket` 객체 타입, 그리고 `Employee`와 `Ticket` 사이의 링크 타입에 대한 편집을 나타내는 새 타입을 선언합니다. 여러 엔터티에 대한 편집은 `|` 연산자로 이어야 합니다.

```typescript tab="TypeScript v2"
import { Employee, Person, Ticket } from "@ontology/sdk";
import { Edits } from "@osdk/functions";

type OntologyEdit = Edits.Object<Employee> | Edits.Interface<Person> | Edits.Object<Ticket> | Edits.Link<Employee, "assignedTickets">;
```

그런 다음 함수가 새 타입의 편집 배열을 반환한다고 선언해야 합니다.

```typescript tab="TypeScript v2"
export default function createNewTicketAndAssignToEmployee(): OntologyEdit[] {
    // ...
}
```

**설명**: `|`는 TypeScript의 유니언(union) 타입 연산자로, "이 타입들 중 하나"를 뜻합니다. 따라서 `OntologyEdit`는 "Employee 객체 편집, Person 인터페이스 편집, Ticket 객체 편집, Employee의 `assignedTickets` 링크 편집 중 하나"인 값의 타입입니다. 함수의 반환 타입 `OntologyEdit[]`는 이런 편집들의 배열이며, 이 목록에 없는 객체 타입을 편집하는 코드는 컴파일되지 않습니다.

> **중간 요약**: 편집 함수는 `Edits.Object`, `Edits.Interface`, `Edits.Link`를 `|`로 묶어 편집 대상 타입을 선언하고, 그 타입의 배열을 반환합니다.

<a id="construct-an-ontology-edits-batch"></a>
## 온톨로지 편집 배치 만들기 (Construct an Ontology edits batch)

TypeScript v2 함수에서 온톨로지 편집을 수행하려면, 먼저 `@osdk/functions`가 export하는 `createEditBatch` 함수로 온톨로지 편집 배치를 만들고, 앞에서 선언한 타입을 타입 인수로 넘깁니다.

```typescript tab="TypeScript v2"
import { Employee, Ticket } from "@ontology/sdk";
import { Client } from "@osdk/client";
import { createEditBatch, Edits } from "@osdk/functions";

type OntologyEdit = Edits.Object<Employee> | Edits.Object<Ticket> | Edits.Link<Employee, "assignedTickets">;

export default function createNewTicketAndAssignToEmployee(client: Client): OntologyEdit[] {

    const batch = createEditBatch<OntologyEdit>(client);
    // ...
}
```

이 배치는 함수에서 만든 모든 편집을 추적하는 데 사용됩니다.

**설명**: `createEditBatch<OntologyEdit>(client)`의 꺾쇠 괄호 부분이 제네릭 타입 인수입니다. 이렇게 만든 `batch`는 `OntologyEdit`에 포함된 타입만 편집할 수 있도록 타입이 고정됩니다. 이후 `batch.update(...)`, `batch.create(...)` 같은 호출은 편집을 배치 안의 목록에 추가할 뿐이고, 함수 마지막에 `return batch.getEdits()`로 그 목록을 반환합니다.

<a id="update-properties"></a>
## 속성 수정하기 (Update properties)

<a id="object-properties"></a>
### 객체 속성 (Object properties)

생성한 배치의 `update` 메서드를 사용해 객체 속성을 하나 이상 수정합니다.

```typescript tab="TypeScript v2"
batch.update(employee, { lastName: newName });
```

`employee` 객체 인스턴스를 메모리에 로드하지 않았다면, 객체의 API 이름과 기본 키(primary key)로 참조해서 수정할 수도 있습니다.

```typescript tab="TypeScript v2"
batch.update({ $apiName: "Employee", $primaryKey: 23 }, { lastName: newName });
```

같은 함수 실행에서 이후에 `employee`의 `lastName` 속성 값에 접근해도, 편집 배치에 `update`를 호출해 만든 변경이 반영되어 있지 *않습니다*.

**설명**: 두 번째 형태는 SQL의 `UPDATE employee SET last_name = :newName WHERE id = 23`에 해당합니다. 객체를 먼저 조회하지 않고 타입 이름과 기본 키만으로 대상 행을 지정할 수 있다는 뜻입니다. 또 `update`는 메모리의 `employee` 변수를 바꾸지 않으므로, 호출 뒤에 `employee.lastName`을 읽으면 여전히 옛 이름이 나옵니다.

때로는 한 객체 타입의 인스턴스가 가진 모든 속성 값을 다른 인스턴스로 복사하는 것이 유용합니다. 다음 예제는 `employee2`의 속성 값을 `employee1`에 할당합니다.

```typescript tab="TypeScript v2"
batch.update(employee1, employee2);
```

기존 객체의 기본 키 속성 값은 수정할 수 없습니다.

<a id="interface-properties"></a>
### 인터페이스 속성 (Interface properties)

`update` 메서드를 사용해 온톨로지 인터페이스를 통해 객체의 인터페이스 속성을 수정할 수 있습니다. 아래 예제에서 `person`의 타입은 온톨로지 인터페이스이지만, 실제 인스턴스는 `Person` 인터페이스를 구현하는 객체입니다.

`update` 메서드는 객체 타입이든 인터페이스든 인수 두 개를 받습니다. 인터페이스의 경우 수정할 인터페이스와 수정할 인터페이스 속성을 받습니다.

```typescript tab="TypeScript v2"
batch.update(person, { firstName: newFirstName });
```

실제 객체의 기본 키 속성으로 구현된 인터페이스 속성은 수정할 수 없습니다.

**설명**: 인터페이스는 여러 객체 타입이 공통으로 가지는 속성의 집합으로, 프로그래밍의 인터페이스와 같은 개념입니다. 예를 들어 Employee와 Contractor가 모두 `Person` 인터페이스를 구현하면, `person`이 실제로 Employee이든 Contractor이든 `firstName`을 같은 코드로 수정할 수 있습니다. 플랫폼은 인터페이스 속성 `firstName`이 실제 객체 타입의 어느 속성에 대응하는지 찾아 그 속성을 수정합니다.

> **중간 요약**: `batch.update(대상, { 속성: 값 })`으로 객체나 인터페이스의 속성을 수정합니다. 대상은 로드한 인스턴스나 `{ $apiName, $primaryKey }`로 지정하며, 기본 키(와 기본 키로 구현된 인터페이스 속성)는 수정할 수 없고, 수정 결과는 같은 실행 안의 변수에 반영되지 않습니다.

<a id="update-links"></a>
## 링크 수정하기 (Update links)

다대다(many-to-many) 링크의 경우, 생성한 배치의 `link`와 `unlink` 메서드로 객체 사이의 링크를 추가하거나 제거합니다.

```typescript tab="TypeScript v2"
// 직원을 사무실에 배정합니다.
batch.link(employee, "office", office);

// 직원에게서 사무실 배정을 해제합니다.
batch.unlink(employee, "office", office);
```

이 방식으로 편집하는 모든 링크 타입은 `Edits.Link`로 선언하세요. 첫 번째 타입 인수는 탐색을 시작하는 객체 타입이고, 두 번째는 그 객체 타입에 정의된 링크 타입 API 이름입니다. 링크를 추가하고 제거하는 전체 예제는 [링크 타입 편집(Link type edits)](../09_language-agnostic-features/01_edits-overview.md#link-type-edits)의 TypeScript v2 탭을 참고하세요.

링크 타입이 대상을 여러 개 가질 수 있다면, `link`와 `unlink`에 배열을 넘겨 한 번에 여러 링크를 편집할 수 있습니다. 배열의 각 원소는 별도의 링크 편집을 만듭니다.

일대일(one-to-one)과 일대다(one-to-many) 링크의 경우, 생성한 배치의 `update` 메서드로 원본 객체의 외래 키(foreign key) 속성을 수정합니다. 아래 예제에서 일대다 링크는 `Ticket` 객체 타입의 `assignedEmployeeId` 외래 키 속성으로 뒷받침되므로, 링크 편집은 곧 객체 편집입니다. 이 경우에는 `Edits.Object<Ticket>`만 선언해야 합니다.

```typescript tab="TypeScript v2"
// 티켓을 직원에게 배정합니다.
batch.update({ $apiName: "Ticket", $primaryKey: 13 }, { assignedEmployeeId: 52 });

// 티켓 배정을 해제합니다.
batch.update({ $apiName: "Ticket", $primaryKey: 13 }, { assignedEmployeeId: undefined });
```

**설명**: 링크가 저장되는 방식이 관계형 데이터베이스와 같기 때문에 편집 방법이 둘로 나뉩니다. 일대다 관계(직원 한 명이 티켓 여러 개를 가짐)는 Ticket 테이블에 `assignedEmployeeId` 외래 키 열을 두는 것으로 표현되므로, 링크를 바꾸는 것은 그 열 값을 `UPDATE`하는 것과 같습니다. 다대다 관계(직원 여러 명이 사무실 여러 곳에 배정됨)는 외래 키 열 하나로 표현할 수 없어 (employee_id, office_id) 쌍을 행으로 담는 별도의 조인 테이블을 쓰므로, `link`와 `unlink`가 그 조인 테이블에 행을 `INSERT`하거나 `DELETE`하는 역할을 합니다.

속성 수정과 마찬가지로, 객체 타입의 구체적인 인스턴스를 미리 로드하지 않았다면 링크의 어느 쪽이든 API 이름과 기본 키로 참조할 수 있습니다.

```typescript tab="TypeScript v2"
// 티켓을 직원에게 배정합니다.
batch.link({ $apiName: "Employee", $primaryKey: 23 }, "assignedTickets", { $apiName: "Ticket", $primaryKey: 12 });

// 직원에게서 티켓 배정을 해제합니다.
batch.unlink({ $apiName: "Employee", $primaryKey: 23 }, "assignedTickets", { $apiName: "Ticket", $primaryKey: 12 });
```

> **중간 요약**: 다대다 링크는 `link`/`unlink`로 편집하고 `Edits.Link`로 선언합니다. 일대일과 일대다 링크는 외래 키 속성을 `update`로 바꾸는 객체 편집이므로 `Edits.Object`만 선언하면 됩니다.

<a id="create-objects"></a>
## 객체 생성하기 (Create objects)

<a id="objects"></a>
### 객체 (Objects)

편집 배치의 `create` 메서드로 새 객체를 만들 수 있습니다. 새 객체를 만들 때는 기본 키 값을 반드시 지정해야 하며, 다른 속성은 선택적으로 초기화할 수 있습니다.

이 예제에서는 주어진 ID로 새 `Ticket` 객체를 만들고, `dueDate` 속성을 설정하고, `assignedTickets` 링크를 수정해 주어진 `Employee`에게 배정합니다. `dueDate`의 새 값 계산을 간단하게 하기 위해 `luxon` 라이브러리를 사용합니다.

```typescript tab="TypeScript v2"
import { Employee, Ticket } from "@ontology/sdk";
import { Client, Osdk } from "@osdk/client";
import { createEditBatch, Edits, Integer } from "@osdk/functions";
import { DateTime } from "luxon";

type OntologyEdit = Edits.Object<Employee> | Edits.Object<Ticket> | Edits.Link<Employee, "assignedTickets">;

export default function createNewTicketAndAssignToEmployee(
    client: Client,
    employee: Osdk.Instance<Employee>,
    ticketId: Integer,
): OntologyEdit[] {
    const batch = createEditBatch<OntologyEdit>(client);

    batch.create(Ticket, {
        ticketId,
        dueDate: DateTime.now().plus({ days: 7 }).toFormat('yyyy-MM-dd'),
    });

    // 새 티켓은 아직 온톨로지에 구체적인 인스턴스로 존재하지 않지만,
    // API 이름과 기본 키로 참조해서 링크할 수 있습니다.
    batch.link(employee, "assignedTickets", { $apiName: "Ticket", $primaryKey: ticketId });

    return batch.getEdits();
}
```

**설명**: 입력은 직원 객체 하나와 새 티켓 ID(정수)입니다. `batch.create(Ticket, {...})`는 기본 키 `ticketId`와 마감일 `dueDate`(오늘부터 7일 뒤를 `yyyy-MM-dd` 문자열로 만든 값)를 가진 Ticket 객체를 생성하는 편집을 추가합니다. 이 시점에는 티켓이 아직 실제로 존재하지 않으므로 인스턴스 변수가 없지만, `{ $apiName: "Ticket", $primaryKey: ticketId }`로 참조하면 같은 배치 안에서 링크를 걸 수 있습니다. 반환되는 편집 목록은 "Ticket 생성"과 "Employee와 Ticket 링크" 두 건입니다.

<a id="interfaces"></a>
### 인터페이스 (Interfaces)

`create` 메서드를 호출하면서 인터페이스, 실제 객체 타입, 인터페이스 속성 집합을 지정해 인터페이스를 통해 새 객체 인스턴스를 만들 수 있습니다. 제공하는 인터페이스 속성 중 하나는 실제 객체 타입의 기본 키 속성으로 구현된 것이어야 합니다.

```typescript tab="TypeScript v2"
editBatch.create(Person, {
    $objectType: "Employee",
    firstName: "John",
    lastName: "Doe",
});
```

**설명**: 인터페이스는 추상적인 타입이므로 그 자체의 인스턴스는 만들 수 없습니다. 그래서 `$objectType: "Employee"`로 실제로 어떤 객체 타입의 객체를 만들지 지정하고, 나머지 값은 인터페이스 속성 이름으로 넘깁니다. 이 예제에서는 기본 키로 구현된 인터페이스 속성이 그 값 중에 들어 있어야 합니다.

> **중간 요약**: `batch.create(객체 타입, { 기본 키, 기타 속성 })`으로 객체를 만들며, 아직 존재하지 않는 새 객체도 `{ $apiName, $primaryKey }`로 참조해 링크할 수 있습니다. 인터페이스로 만들 때는 `$objectType`으로 실제 객체 타입을 지정합니다.

<a id="delete-objects"></a>
## 객체 삭제하기 (Delete objects)

<a id="objects"></a>
### 객체 (Objects)

편집 배치의 `delete` 메서드를 호출해 객체를 삭제할 수 있습니다.

이 예제에서는 주어진 직원에게 배정된 모든 티켓을 삭제합니다.

```typescript tab="TypeScript v2"
for await (const ticket of employee.$link.assignedTickets.asyncIter()) {
    batch.delete(ticket);
}
```

**설명**: `employee.$link.assignedTickets`는 이 직원과 링크된 Ticket 객체 집합이고, `asyncIter()`로 하나씩 순회하면서 각 티켓에 대한 삭제 편집을 배치에 추가합니다. SQL로는 `DELETE FROM ticket WHERE assigned_employee_id = :employeeId`에 해당합니다.

인스턴스 대신 기본 키로 객체를 삭제할 수도 있습니다.

```typescript tab="TypeScript v2"
batch.delete({ $apiName: "Ticket", $primaryKey: 12 });
```

<a id="interfaces"></a>
### 인터페이스 (Interfaces)

`delete` 메서드를 호출해 인터페이스를 통해 객체를 삭제할 수 있습니다.

```typescript tab="TypeScript v2"
batch.delete(person);
```

> **중간 요약**: `batch.delete(대상)`으로 객체를 삭제하며, 대상은 로드한 인스턴스, `{ $apiName, $primaryKey }`, 또는 인터페이스 타입의 값일 수 있습니다.

<a id="edits-on-struct-properties"></a>
## 구조체 속성 편집 (Edits on struct properties)

객체 타입과 인터페이스 타입 모두의 온톨로지 구조체(struct) 속성은 TypeScript v2 함수로 편집할 수 있습니다. TypeScript v2에서 [구조체 타입](../04_types-reference.md#structcustom-type)은 TypeScript 인터페이스로 정의합니다. 함수의 구조체 타입이 구조체 속성과 같은 필드를 가지고, 필드 이름이 온톨로지 구조체 속성 필드의 API 이름과 일치하면, 그 구조체 타입으로 온톨로지 구조체 속성을 편집할 수 있습니다.

```typescript tab="TypeScript v2"
interface Address {
    street: string,
    city: string,
    state: string,
    country: string,
    zipcode: string,
}

export default function updateEmployeeAddress(
    client: Client,
    employee: Osdk.Instance<Employee>,
    newAddress: Address
): OntologyEdit[] {
    const batch = createEditBatch<OntologyEdit>(client);
    batch.update(employee, { address: newAddress });
    return batch.getEdits();
}
```

**설명**: 구조체 속성은 여러 하위 필드를 묶은 하나의 속성입니다. 여기서 Employee의 `address` 속성은 street, city, state, country, zipcode 다섯 필드를 가진 구조체입니다. 함수 쪽에서 같은 필드 이름을 가진 TypeScript `interface Address`를 정의해 파라미터 타입으로 쓰면, 입력받은 `newAddress` 값을 그대로 `address` 속성의 새 값으로 넣을 수 있습니다. 필드 이름이 온톨로지 쪽 API 이름과 하나라도 다르면 이 대응이 성립하지 않습니다.

> **중간 요약**: 구조체 속성은 필드 이름이 온톨로지 구조체 필드의 API 이름과 같은 TypeScript 인터페이스 값을 `update`에 넘겨 편집합니다.

## 정리

- 편집 함수의 결과는 함수 기반 액션으로 실행될 때만 실제 데이터에 반영됩니다.
- 편집 대상은 `Edits.Object`, `Edits.Interface`, `Edits.Link`의 유니언 타입으로 선언하고, `createEditBatch`로 만든 배치에 편집을 쌓아 `getEdits()`로 반환합니다.
- `update`는 속성 수정과 일대일, 일대다 링크(외래 키) 수정에, `link`/`unlink`는 다대다 링크에, `create`와 `delete`는 객체 생성과 삭제에 씁니다.
- 대상 객체는 로드한 인스턴스 대신 `{ $apiName, $primaryKey }`로 지정할 수 있으며, 기본 키는 수정할 수 없습니다.
- 편집 배치에서는 같은 실행 안에서 자신의 편집이 보이지 않으며, 그것이 필요하면 스테이징된 쓰기를 씁니다.
