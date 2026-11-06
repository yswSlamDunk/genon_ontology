# 온톨로지 편집 (Ontology edits)

- 원문: https://www.palantir.com/docs/foundry/functions/api-ontology-edits/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v1 > Ontology edits

이 페이지는 TypeScript v1 함수(function)에서 온톨로지의 객체를 수정하는 API를 설명합니다. 속성(property) 값 변경, 링크 설정과 해제, 객체 생성과 삭제 방법, 그리고 함수 실행 중 편집(edit)이 어떻게 모였다가 액션을 통해 적용되는지, `@Edits` 데코레이터로 출처 정보를 선언하는 이유를 다룹니다.

**팁**: 이 문서는 TypeScript v1 함수에 한정된 내용입니다. 이 페이지의 TypeScript v2 버전은 [온톨로지 편집](../10_typescript-v2/04_typescript-v2-ontology-edits.md)을 참고하세요. Ontology SDK 지원과 구성 가능한 리소스 요청을 포함한 [더 강력한 기능](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 위해 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)하는 것을 권장합니다.

온톨로지를 바탕으로 파생 값을 반환하는 함수뿐 아니라, 온톨로지에 있는 객체의 속성과 객체 사이의 링크를 편집하는 함수도 작성할 수 있습니다. 이 페이지는 함수에서 사용할 수 있는 객체 편집 API를 설명합니다. 편집 함수의 동작 방식에 대한 자세한 내용은 [개요 페이지](../09_language-agnostic-features/01_edits-overview.md)를 참고하세요.

실제 운영 환경에서 사용하려면 **온톨로지 편집 함수를 액션으로 구성해야 하며**, 이를 [함수 기반 액션(function-backed Action)](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)이라고 합니다. 이렇게 액션을 구성하면 추가 메타데이터를 제공하고, 권한을 구성하고, 여러 운영 인터페이스에서 그 액션에 접근할 수 있습니다. [문서](../09_language-agnostic-features/01_edits-overview.md#when-edits-are-applied)에 언급된 대로, 액션 밖에서 편집 함수를 실행하면 객체 데이터가 실제로 수정되지 않습니다.

**주의**: 객체를 편집한 뒤 그 객체를 검색하면 예상과 다른 결과가 반환될 수 있습니다. 자세한 내용은 [주의 사항 섹션](../09_language-agnostic-features/01_edits-overview.md#edits-and-object-search)을 참고하세요.

**설명**: 편집 함수는 "어떤 편집을 할지"를 계산하는 역할만 하고, 그 편집을 실제 데이터에 기록하는 것은 액션입니다. 예를 들어 Live Preview에서 편집 함수를 실행하면 어떤 편집이 만들어지는지는 볼 수 있지만, 온톨로지의 Employee 객체 값은 바뀌지 않습니다.

<a id="declaring-an-edit-function"></a>
## 편집 함수 선언하기 (Declaring an edit function)

온톨로지를 편집하는 함수는 다음 조건을 갖춰야 합니다.

* `@foundry/functions-api`에서 가져온 `@OntologyEditFunction()` 데코레이터가 붙어 있어야 합니다.
* 편집할 객체 타입을 지정하기 위해 `@foundry/functions-api`에서 가져온 `@Edits([object type])` 데코레이터가 붙어 있어야 합니다.
* 반환 타입이 명시적으로 `void`여야 합니다.

<a id="updating-properties"></a>
## 속성 업데이트하기 (Updating properties)

객체의 속성 값을 다시 대입하기만 하면 속성 값을 편집할 수 있습니다. 예를 들면 다음과 같습니다.

```typescript
employee.lastName = newName;
```

같은 함수 실행 안에서 나중에 `lastName` 속성 값에 접근하면 방금 설정한 새 값이 반환됩니다.

객체의 [배열 속성](../13_functions-on-objects/06_api-objects-links.md#array-properties)은 `ReadOnlyArray` 타입으로 생성됩니다. 배열을 수정하려면 복사본을 만들어 복사본을 수정한 다음 속성을 업데이트합니다.

```typescript
// 새 배열로 복사합니다
let arrayCopy = [...myObject.myArrayProperty];
// 이제 복사한 배열을 수정할 수 있습니다
arrayCopy.push(newItem);
// 그런 다음 속성 값을 덮어씁니다
myObject.myArrayProperty = arrayCopy;
```

**설명**: `ReadOnlyArray`에는 `push` 같은 변경 메서드가 없으므로 원본 배열을 직접 바꿀 수 없습니다. 스프레드 구문 `[...배열]`로 새 배열을 만들어 수정한 뒤, 속성에 새 배열 전체를 대입해야 편집으로 기록됩니다. 예를 들어 `["a", "b"]`에 `"c"`를 추가하면 속성 값이 `["a", "b", "c"]`로 바뀌는 편집 하나가 생깁니다.

기존 객체의 기본 키(primary key) 속성 값은 업데이트할 수 없습니다.

<a id="updating-links"></a>
## 링크 업데이트하기 (Updating links)

`SingleLink`와 `MultiLink` 인터페이스에는 링크를 업데이트하는 데 쓸 수 있는 여러 메서드가 있습니다.

```typescript
// Employee의 상사(supervisor)를 설정합니다
employee.supervisor.set(newSupervisor);

// Employee의 상사를 비웁니다
employee.supervisor.clear();

// 해당 직원에게 새 부하 직원(report)을 추가합니다
employee.reports.add(newReport);

// 해당 직원과 연결된 기존 부하 직원을 제거합니다
employee.reports.remove(oldReport);
```

속성 업데이트와 마찬가지로, 링크를 업데이트한 뒤 접근하면 수행한 업데이트가 반영되어 있습니다.

**설명**: `SingleLink`는 상대 객체가 최대 하나인 링크(직원 한 명의 상사는 한 명)이므로 `set`/`clear`를 쓰고, `MultiLink`는 상대 객체가 여럿일 수 있는 링크(한 상사의 부하 직원 여러 명)이므로 `add`/`remove`를 씁니다.

> **중간 요약**: 편집 함수는 `@OntologyEditFunction()`과 `@Edits`를 붙이고 `void`를 반환합니다. 속성은 값을 대입해서(배열은 복사 후 대입), 링크는 `set`/`clear`/`add`/`remove`로 수정하며, 기본 키는 바꿀 수 없습니다.

<a id="creating-objects"></a>
## 객체 만들기 (Creating objects)

`@foundry/ontology-api`에서 제공하는 `Objects.create()` 인터페이스로 새 객체를 만들 수 있습니다. 새 객체를 만들 때는 기본 키 값을 지정해야 합니다.

다음 예제에서는 주어진 ID로 새 Ticket 객체를 만들고, `dueDate` 속성을 설정하고, (`assignedTickets` 링크를 수정해) 주어진 Employee에게 할당합니다.

```typescript
import { OntologyEditFunction, Edits } from "@foundry/functions-api";
import { Employee, Objects, Tickets } from "@foundry/ontology-api";

export class TicketActionFunctions {
    @Edits(Employee, Tickets)
    @OntologyEditFunction()
    public createNewTicketAndAssignToEmployee(employee: Employee, ticketId: Integer): void {
        const newTicket = Objects.create().ticket(ticketId);

        newTicket.dueDate = LocalDate.now().plusDays(7);

        employee.assignedTickets.add(newTicket);
    }
}
```

**설명**: `Objects.create().ticket(ticketId)`의 인자가 새 객체의 기본 키입니다. 마감일은 오늘로부터 7일 뒤로 설정하고, 직원의 `assignedTickets` 링크에 새 티켓을 추가합니다. 결과적으로 "Ticket 생성"과 "링크 추가" 편집이 만들어집니다.

<a id="deleting-objects"></a>
## 객체 삭제하기 (Deleting objects)

`.delete()` 메서드를 호출해 객체를 삭제할 수 있습니다.

다음 예제에서는 주어진 직원에게 할당된 모든 티켓을 삭제합니다.

```typescript
const tickets = employee.tickets.all();
tickets.forEach(ticket => ticket.delete());
```

<a id="how-edits-are-captured"></a>
## 편집이 수집되는 방식 (How edits are captured)

온톨로지 편집 함수가 실행되면, 객체에 대한 모든 업데이트가 함수 인프라에 의해 수집되어 함수 실행이 끝날 때 반환됩니다. 여기에는 `Objects.create()` API를 통한 새 객체 생성, 모든 속성 업데이트, 객체 삭제가 포함됩니다.

편집은 액션에서 최소한의 편집 집합만 적용되도록 지능적으로 합쳐집니다. 예를 들어 새 객체를 만든 다음 그 속성을 업데이트하면, 속성 업데이트를 포함한 **Create Object** 편집 하나가 반환됩니다. 마찬가지로 기존 객체의 여러 속성을 업데이트하면 모든 속성 편집을 담은 **Update Object** 편집 하나가 반환됩니다. 객체를 삭제하면 삭제 전에 수행한 다른 속성 편집은 모두 지워집니다. 원자적 트랜잭션을 실행하는 액션 서비스에 전달될 편집 목록이 만들어지려면 함수 전체가 성공해야 합니다.

**설명**: 예를 들어 함수가 다음 순서로 동작했다고 합시다. (1) Ticket T1 생성, (2) T1의 `title` 설정, (3) Employee E1의 `lastName` 변경, (4) E1의 `department` 변경. 반환되는 편집은 4개가 아니라 "T1 생성(title 포함)", "E1 수정(lastName, department)" 2개입니다. 함수 중간에 예외가 나면 편집 목록 자체가 만들어지지 않으므로 아무것도 적용되지 않습니다.

수집된 온톨로지 편집은 함수 실행 결과로 목록 형태로 반환됩니다. 이것이 온톨로지 편집 함수의 반환 타입이 `void` 또는 `Promise<void>`여야 하는 이유입니다. 실행될 때 함수의 실제 반환 타입은 온톨로지 편집 목록이므로, 다른 값을 동시에 반환할 수 없습니다.

편집은 한 번의 함수 실행의 전체 생명주기 동안 하나의 편집 저장소(edit store)에 수집됩니다. 따라서 객체를 만들거나 업데이트하거나 삭제하는 도우미 함수를 호출할 수 있으며, 그 도우미 함수가 온톨로지 편집 함수로 게시되지 않았어도 됩니다. 예를 들면 다음과 같습니다.

```typescript
export class HelperEditFunctions {
    @Edits(ObjectA, ObjectB)
    @OntologyEditFunction()
    public createAndLink(): void {
        const objectA = this.createObjectA();
        const objectB = this.createObjectB();
        objectA.linkToB.set(objectB);
    }

    /**
     * 이 도우미 함수들은 @OntologyEditFunction()이 붙어 있지 않지만,
     * 다른 편집 함수에서 사용할 새 객체를 만들 수 있습니다.
     */
    private createObjectA(): ObjectA {
        const objectA = Objects.create().objectA(this.generateRandomId());
        objectA.prop1 = "example";
        objectA.prop2 = 42;
        return objectA;
    }

    private createObjectB(): ObjectB {
        const objectB = Objects.create().objectB(this.generateRandomId());
        objectB.prop1 = "another example";
        return objectB;
    }

    /* 필요에 따라 기본 키를 생성하세요. 예를 들면,
    import { Uuid } from "@foundry/functions-utils";
    private generateRandomId(){
       return Uuid.random();
    }
    */
}
```

**설명**: 게시되는 함수는 `createAndLink` 하나뿐이고, `createObjectA`와 `createObjectB`는 private 도우미 메서드입니다. 도우미 메서드 안에서 만든 객체도 같은 편집 저장소에 기록되므로, 최종적으로 "ObjectA 생성", "ObjectB 생성", "A와 B 링크" 편집이 함께 반환됩니다.

<a id="retrieving-edited-values"></a>
## 편집된 값 조회하기 (Retrieving edited values)

함수에서 편집을 수행하면, 그 값을 읽을 때 함수 인프라가 편집된 값을 반환합니다. 예를 들어 객체의 속성을 설정한 다음 조회하면 새 값이 반환됩니다.

```
airplane.departureTime = newDepartureTime;
console.log(airplane.departureTime); // newDepartureTime이 출력됩니다
```

객체를 삭제하면 검색 결과에서 제거되고 그 속성에 접근할 수 없게 됩니다.

> **중간 요약**: 함수 실행 중의 모든 생성, 수정, 삭제는 하나의 편집 저장소에 모였다가 최소 편집 목록으로 합쳐져 반환되므로 편집 함수는 다른 값을 반환할 수 없습니다. 같은 실행 안에서 편집한 객체를 다시 읽으면 새 값이 보입니다.

<a id="the-edits-decorator"></a>
## @Edits 데코레이터 (The @Edits decorator)

액션은 권한을 적용하기 위해 출처(provenance) 정보가 필요할 수 있습니다. 액션에 이 정보를 제공하려면 `@Edits` 데코레이터를 사용해 함수가 편집을 반환하는 객체 타입을 지정합니다.

`@Edits` 데코레이터를 사용할 때는 다음을 고려하세요.

* 속성을 편집할 때는 편집된 객체의 타입을 선언해야 합니다.
* 일대일 또는 일대다 링크를 편집할 때는 외래 키 속성을 가진 객체의 타입을 선언해야 합니다.
* 조인 테이블 링크를 편집할 때는 소스와 대상 객체 타입을 모두 선언해야 합니다.

**설명**: 링크 규칙은 링크가 데이터상 어디에 저장되는지를 따릅니다. 일대다 링크(예: Ticket 여러 개가 Employee 하나에 속함)는 Ticket 쪽의 `employee_id` 외래 키 열로 표현되므로, 링크를 바꾸는 것은 Ticket 객체를 수정하는 것이고 따라서 Ticket을 선언합니다. 다대다 링크는 별도의 조인 테이블에 행을 추가하거나 빼는 것이므로 양쪽 객체 타입을 모두 선언합니다.

**주의**: 함수는 코드를 정적 분석해 참조된 객체 타입을 자동으로 감지합니다. 하지만 정적 분석은 참조를 제대로 감지하지 *못할 수도* 있습니다. 참조된 객체 타입에 대한 출처 정보를 제공하기 위해 항상 `@Edits` 데코레이터를 사용할 것을 강력히 권장합니다.

다음 예제에서는 함수가 `Employee`와 `Aircraft` 객체 타입을 편집합니다.

```typescript
import { OntologyEditFunction } from "@foundry/functions-api";
import { Employee, Aircraft, Objects } from "@foundry/ontology-api";

export class MyOntologyEditFunction {
    @Edits(Aircraft, Employee)
    @OntologyEditFunction()
    public myFunction(): void {
        const x = Objects.search().aircraft().all()[0];
        x.businessCapacity = 3;
        const y = Objects.search().employee().all()[0];
        y.department = "HR";
    }
}
```

이전에 편집한 객체를 편집으로 바뀌지 않은 식별자(예: 기본 키)를 사용해 `Objects.search()` API로 조회(또는 머티리얼라이즈)하면, 편집된 값이 반환됩니다. 객체가 머티리얼라이즈될 때 함수 인프라가 대기 중인 편집을 그 객체에 적용하기 때문입니다. 이는 편집한 값으로 필터링하거나, 서치 어라운드(search around)하거나, 집계하는 경우와 다릅니다. 이런 경우에는 함수 실행이 끝날 때까지 편집이 반영되지 않습니다. 자세한 내용은 [편집과 객체 검색](../09_language-agnostic-features/01_edits-overview.md#edits-and-object-search)을 참고하세요.

```typescript
import { OntologyEditFunction } from "@foundry/functions-api";
import { Employee, Objects } from "@foundry/ontology-api";

export class CaveatEditFunctions {
    @Edits(Employee)
    @OntologyEditFunction()
    public async editAndSearch(): Promise<void> {
        const employeeOne = Objects.search().employee().filter(e => e.id.exactMatch(1)).all()[0];
        employeeOne.name = "Bob";

        // 이미 편집한 객체를 다시 조회합니다
        const employeeOneAgain = Objects.search().employee().filter(e => e.id.exactMatch(1)).all()[0];
        console.log(employeeOneAgain.name); // "Bob"이 출력됩니다
    }
}
```

**설명**: 두 번째 조회는 편집으로 바뀌지 않은 `id`(기본 키)로 필터링하므로, 원래 객체를 찾은 뒤 대기 중인 편집(`name = "Bob"`)을 덧씌워 반환합니다. 반대로 `filter(e => e.name.exactMatch("Bob"))`처럼 편집한 값 자체로 검색하면, 검색 인덱스에는 아직 옛 이름이 들어 있으므로 이 객체가 결과에 나오지 않습니다. 이 점이 Python의 단계적 쓰기(staged writes)가 제공하는 쓰기 후 읽기 보장과의 차이입니다.

> **중간 요약**: `@Edits`에는 속성을 편집한 객체 타입, 외래 키를 가진 쪽 객체 타입, 조인 테이블 링크의 양쪽 객체 타입을 선언하며, 정적 분석에 의존하지 말고 항상 명시하는 것이 좋습니다. 편집된 객체는 기본 키로 다시 조회하면 새 값이 보이지만, 편집한 값으로 필터, 서치 어라운드, 집계를 하면 반영되지 않습니다.

## 정리

- TypeScript v1 편집 함수는 `@OntologyEditFunction()`과 `@Edits`를 붙이고 `void`를 반환하며, 함수 기반 액션으로 구성해야 실제로 데이터가 바뀝니다.
- 속성은 대입으로(배열은 복사 후 대입), 링크는 `SingleLink`/`MultiLink` 메서드로, 객체는 `Objects.create()`와 `.delete()`로 편집합니다. 기본 키는 수정할 수 없습니다.
- 편집은 실행 전체에 걸쳐 하나의 저장소에 모였다가 최소 집합으로 합쳐져 반환되며, 도우미 메서드의 편집도 포함됩니다.
- `@Edits`로 출처 정보를 명시하는 것이 강력히 권장됩니다.
- 편집한 객체를 기본 키로 다시 읽으면 새 값이 보이지만, 편집한 값 기준의 검색과 집계는 함수가 끝날 때까지 반영되지 않습니다.
