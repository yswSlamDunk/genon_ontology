# 스테이징 쓰기 (Staged writes)

- 원문: https://www.palantir.com/docs/foundry/functions/typescript-v2-staged-writes/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v2 > Staged writes

이 페이지는 TypeScript v2 함수(function)에서 온톨로지 객체를 편집(edit)하는 또 다른 실행 방식인 스테이징 쓰기(staged writes)를 다룹니다. 일반 편집 함수는 편집 묶음을 반환값으로 돌려줘야 적용되고, 함수 안에서 방금 쓴 내용을 다시 읽을 수 없습니다. 스테이징 쓰기는 이 두 제약을 풀어서, 함수 안에서 쓴 내용을 바로 질의에 반영하고 다른 함수 호출까지 하나의 원자적 단위로 묶을 수 있게 해 줍니다.

**참고**: 베타(Beta). 스테이징 쓰기는 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며 사용자의 환경(enrollment)에서는 사용할 수 없을 수도 있습니다. 활발히 개발 중이므로 기능이 바뀔 수 있습니다. 사용하려면 Palantir 지원팀에 접근 권한을 요청하세요.

라이브 미리보기(live preview)와 게시된 함수 미리보기(published function preview)는 Code Repositories에서만 지원되며, 로컬 개발 환경이나 VS Code 워크스페이스 환경에서는 지원되지 않습니다.

이 페이지는 TypeScript v2 함수의 스테이징 쓰기를 설명합니다. Python의 경우 [Python 함수의 스테이징 쓰기](../11_python/06_python-staged-writes.md)를 참고하세요.

스테이징 쓰기는 온톨로지의 객체를 편집하는 함수를 위한 추가 실행 모델을 제공합니다. 일반 [온톨로지 편집 함수](04_typescript-v2-ontology-edits.md)로 만든 편집과 달리, 스테이징 쓰기 함수는 다음과 같은 특징이 있습니다.

* 함수 안에서 적용한 온톨로지 편집에 대해 쓰기 후 읽기 보장(read-after-write guarantee)을 제공합니다. 함수 안에서 적용한 모든 편집은 스테이징되며, 함수의 이후 부분에서 실행하는 온톨로지 질의와 집계에 반영됩니다.
* 온톨로지 편집을 수행하는 다른 스테이징 쓰기 함수를 중첩 호출할 수 있습니다.

이 페이지는 스테이징 쓰기 함수를 작성하는 방법과 고유한 특성을 설명합니다. 편집 함수가 동작하는 방식에 대한 자세한 내용은 [개요 페이지](../09_language-agnostic-features/01_edits-overview.md)를 참고하세요.

**설명**: "스테이징(staging)"은 변경 사항을 곧바로 최종 저장소에 반영하지 않고 임시 영역에 쌓아 두는 것을 말합니다. git에서 `git add`로 변경을 스테이징 영역에 올려 두었다가 `git commit`으로 한꺼번에 확정하는 흐름, 그리고 데이터베이스 트랜잭션에서 `BEGIN` 이후의 변경이 `COMMIT` 전까지 다른 세션에 보이지 않는 흐름과 같은 개념입니다. 쓰기 후 읽기 보장은 "같은 트랜잭션 안에서 INSERT한 행을 바로 SELECT하면 그 행이 보인다"는 성질을 뜻합니다.

<a id="key-differences-from-regular-ontology-edit-functions"></a>
## 일반 온톨로지 편집 함수와의 주요 차이점 (Key differences from regular Ontology edit functions)

스테이징 쓰기 함수는 여러 중요한 면에서 일반 편집 함수와 다릅니다.

<a id="read-after-write-guarantee"></a>
### 쓰기 후 읽기 보장 (Read-after-write guarantee)

스테이징 쓰기 함수 안에서 읽는 모든 온톨로지 데이터는 그 함수에서 이전에 수행한 모든 편집(그리고 같은 액션 실행 안에서 이 함수를 호출한 스테이징 쓰기 함수가 수행한 모든 편집)을 반영합니다. 이 편집들은 스테이징만 된 상태이므로, 다른 사용자가 실행하는 질의나 이 실행 컨텍스트 밖의 함수에서는 보이지 않습니다. 따라서 함수 안에서 검색 요청과 집계로 온톨로지를 질의하면, 스테이징된 모든 편집이 질의 결과에 반영됩니다.

<a id="no-requirement-to-return-edits-at-the-end-of-the-function"></a>
### 함수 끝에서 편집을 반환할 필요 없음 (No requirement to return edits at the end of the function)

일반 Python 및 TypeScript V2 온톨로지 편집 함수는 편집을 적용하려면 온톨로지 편집 묶음(batch)을 함수의 반환값으로 돌려줘야 합니다. 스테이징 쓰기 함수에서는 온톨로지 편집이 자동으로 스테이징되며, 액션이 완료될 때 함수 실행이 끝나는 시점에 온톨로지에 적용됩니다. 그래서 함수의 반환값을 호출자에게 다른 정보를 돌려주는 데 쓸 수 있습니다.

예를 들어, TypeScript V2 스테이징 쓰기 함수를 실행하는 액션을 적용하고, 그 함수가 몇 가지 편집을 한 뒤 AIP Logic 함수를 호출한다고 합시다. AIP Logic 함수가 실행하는 질의는 TypeScript V2 함수가 만든 온톨로지 변경을 반환합니다. AIP Logic 함수가 추가로 만든 편집도 Logic 함수의 반환값으로 돌려줄 필요 없이 같은 스테이징 편집에 합류합니다. 액션이 완료되면 스테이징된 모든 편집이 자동으로 적용됩니다.

<a id="atomic-execution"></a>
### 원자적 실행 (Atomic execution)

스테이징 쓰기 함수 안의 모든 작업(질의, 함수 호출, AIP Logic 실행 포함)은 편집을 함께 스테이징합니다. 스테이징된 편집은 함수가 성공적으로 끝난 뒤 커밋(즉, 온톨로지에 적용)됩니다. 함수가 오류를 던지면 온톨로지는 수정되지 않은 상태로 남고, 액션이 함수를 재시도하기 전에 스테이징된 모든 편집이 폐기됩니다.

**설명**: 원자성(atomicity)은 데이터베이스 트랜잭션의 ACID 성질 중 A에 해당합니다. 여러 편집이 "모두 적용되거나, 하나도 적용되지 않거나" 둘 중 하나만 일어난다는 뜻입니다. 예를 들어 티켓을 만들고 직원에게 연결하는 두 편집 중 두 번째에서 오류가 나면, 첫 번째로 만든 티켓도 남지 않습니다.

<a id="writeableclient"></a>
### `WriteableClient`

스테이징 쓰기 함수는 표준 `Client` 대신 `WriteableClient`를 사용합니다. `WriteableClient`는 편집 묶음을 구성할 필요 없이 객체를 생성, 수정, 삭제하는 메서드를 직접 제공합니다.

> **중간 요약**: 스테이징 쓰기 함수는 함수 안의 편집을 임시로 쌓아 두고, 같은 실행 안의 질의에는 바로 반영하며, 함수가 성공하면 한꺼번에 커밋하고 실패하면 모두 버립니다. 편집을 반환할 필요가 없으므로 반환값을 자유롭게 쓸 수 있고, `WriteableClient`로 편집을 직접 수행합니다.

<a id="define-a-staged-write-function"></a>
## 스테이징 쓰기 함수 정의하기 (Define a staged-write function)

스테이징 쓰기 함수는 `@osdk/functions` 패키지에서 내보내는 `Edits` 타입을 사용해 편집할 엔터티를 명시적으로 선언해야 합니다. 첫 번째 파라미터는 `WriteableClient<T>`여야 하며, 여기서 `T`는 함수가 수행할 모든 편집 타입의 유니언(union)입니다. 반환값은 더 이상 편집 배열로 제한되지 않으므로 어떤 값이든 반환할 수 있습니다. 다음 예제는 `Employee` 객체 타입을 편집하는 함수를 선언합니다.

```typescript tab="TypeScript v2"
import { Employee } from "@ontology/sdk";
import { Edits, Integer } from "@osdk/functions";
import { WriteableClient } from "@osdk/functions/experimental";

type OntologyEdit = Edits.Object<Employee>;

export default async function assignTicket(
    client: WriteableClient<OntologyEdit>,
    employeeId: string,
    ticketId: string
): Promise<Integer> {
    // ...
}
```

**설명**: `type OntologyEdit = Edits.Object<Employee>;` 줄이 "이 함수는 Employee 객체를 편집한다"는 선언입니다. 여러 종류를 편집한다면 `Edits.Object<Ticket> | Edits.Link<Employee, "assignedTickets">`처럼 TypeScript 유니언 타입(`|`)으로 나열합니다. 이 선언이 `WriteableClient`의 타입 파라미터로 들어가므로, 선언하지 않은 객체 타입을 편집하려 하면 컴파일 단계에서 타입 오류가 납니다. 반환 타입은 `Promise<Integer>`처럼 편집과 무관한 값이어도 됩니다.

<a id="create-objects"></a>
## 객체 생성하기 (Create objects)

`WriteableClient`의 `create` 메서드를 사용해 새 객체를 생성합니다. 객체 타입을 지정하고 기본 키(primary key) 값과 초기화하려는 다른 속성(property) 값을 함께 제공해야 합니다.

```typescript tab="TypeScript v2"
import { Employee } from "@ontology/sdk";
import { Edits } from "@osdk/functions";
import { WriteableClient } from "@osdk/functions/experimental";

type OntologyEdit = Edits.Object<Employee>;

async function createEmployee(
    client: WriteableClient<OntologyEdit>,
    employeeId: string,
    firstName: string,
    lastName: string
): Promise<Integer> {
    await client.create(Employee, {
        employeeId: employeeId,
        firstName: firstName,
        lastName: lastName
    });

    return employeeId;
}

export default createEmployee;
```

**설명**: 직원 ID, 이름, 성을 입력받아 `client.create(Employee, {...})`로 Employee 객체 하나를 만듭니다. SQL의 `INSERT INTO employee (employee_id, first_name, last_name) VALUES (...)`에 해당합니다. 일반 편집 함수와 달리 편집 묶음을 반환하지 않고, 대신 만든 직원의 ID를 반환합니다. `await`가 붙어 있는 것은 생성 요청이 비동기로 처리되기 때문입니다.

<a id="creating-with-generated-ids"></a>
### 생성된 ID로 생성하기 (Creating with generated IDs)

ID를 생성한 뒤 바로 사용해야 할 때는 다음과 같이 합니다.

(원문에는 `crypto` 모듈의 `randomUUID()`로 티켓 ID를 만든 뒤 `client.create(Ticket, { ticketId, title, status: "open" })`로 Ticket 객체를 생성하고 그 ID를 반환하는 예제 코드가 있습니다.)

**설명**: 기본 키를 함수 안에서 직접 만들어야 하는 경우입니다. UUID(전역 고유 식별자)를 생성해 변수에 담아 두면, 객체 생성에 쓰고 나서 같은 값을 링크 생성이나 반환값에 다시 쓸 수 있습니다.

<a id="update-objects"></a>
## 객체 수정하기 (Update objects)

<a id="object-properties"></a>
### 객체 속성 (Object properties)

`WriteableClient`의 `update` 메서드를 사용해 객체 속성을 수정합니다.

```typescript tab="TypeScript v2"
await client.update(employee, { lastName: newName });
```

객체의 API 이름과 기본 키를 참조해서 객체를 수정할 수도 있습니다.

```typescript tab="TypeScript v2"
await client.update({ $apiName: "Employee", $primaryKey: 23 }, { lastName: newName });
```

인터페이스 편집은 스테이징 쓰기 함수에서 지원되지 않습니다.

**설명**: 첫 번째 방식은 이미 불러온 객체 인스턴스(`employee`)를 넘기고, 두 번째 방식은 객체를 불러오지 않고 "Employee 타입의 기본 키 23번"이라는 참조만 넘깁니다. 두 번째 방식은 SQL의 `UPDATE employee SET last_name = ... WHERE employee_id = 23`과 같은 형태로, 객체를 먼저 조회하는 단계를 생략할 수 있습니다.

<a id="delete-objects"></a>
## 객체 삭제하기 (Delete objects)

`WriteableClient`의 `delete` 메서드를 호출해 객체를 삭제할 수 있습니다.

```typescript tab="TypeScript v2"
await client.delete(ticket);
```

인스턴스 대신 기본 키를 사용해 객체를 삭제할 수도 있습니다.

```typescript tab="TypeScript v2"
await client.delete({ $apiName: "Ticket", $primaryKey: 12 });
```

<a id="create-or-delete-links"></a>
## 링크 생성 또는 삭제하기 (Create or delete links)

`WriteableClient`의 `link`와 `unlink` 메서드를 사용해 객체 사이의 다대다(many to many) 링크를 추가하거나 제거합니다.

```typescript tab="TypeScript v2"
// 직원에게 티켓을 할당
await client.link(employee, "assignedTickets", ticket);

// 직원에게서 티켓 할당을 해제
await client.unlink(employee, "assignedTickets", ticket);
```

링크의 어느 쪽이든 API 이름과 기본 키로 참조할 수도 있습니다.

(원문에는 `client.link({ $apiName: "Employee", $primaryKey: 23 }, "assignedTickets", { $apiName: "Ticket", $primaryKey: 12 })`처럼 양쪽을 모두 기본 키로 참조하는 예제 코드가 있습니다.)

일대다(one to many) 링크를 편집하려면, 객체 생성 또는 수정 편집으로 외래 키 속성을 편집합니다.

**설명**: 관계형 데이터베이스에서 다대다 관계는 보통 별도의 조인 테이블(예: `employee_ticket(employee_id, ticket_id)`)에 행을 넣고 빼는 방식으로 표현합니다. `link`와 `unlink`는 그 행을 추가하고 삭제하는 작업에 해당합니다. 반면 일대다 관계는 "다" 쪽 테이블의 외래 키 열(예: Ticket의 `assigneeId`)로 표현되므로, 링크 전용 메서드가 아니라 그 열 값을 바꾸는 `create`나 `update`로 편집합니다.

> **중간 요약**: `WriteableClient`는 `create`, `update`, `delete`, `link`, `unlink` 메서드로 객체와 다대다 링크를 직접 편집합니다. 대상은 객체 인스턴스나 `{ $apiName, $primaryKey }` 참조로 지정하며, 일대다 링크는 외래 키 속성을 수정해 바꿉니다. 인터페이스 편집은 지원되지 않습니다.

<a id="read-after-write-within-a-staged-write-function"></a>
## 스테이징 쓰기 함수 안에서 쓰기 후 읽기 (Read-after-write within a staged-write function)

스테이징 쓰기 함수의 핵심 장점 중 하나는 같은 실행 안에서 방금 쓴 데이터를 읽을 수 있다는 점입니다. 즉각적인 일관성이 필요한 워크플로를 구현할 때 유용합니다.

```typescript tab="TypeScript v2"
import { Employee, Ticket } from "@ontology/sdk";
import { Edits, Integer } from "@osdk/functions";
import { WriteableClient } from "@osdk/functions/experimental";
import { randomUUID } from "crypto";

type OntologyEdit = Edits.Object<Ticket> | Edits.Link<Employee, "assignedTickets">;

async function assignTicketAndCheckWorkload(
    client: WriteableClient<OntologyEdit>,
    employeeId: Integer,
    title: string
): Promise<{ ticketId: string, totalAssignedTickets: number }> {
    const ticketId = randomUUID();

    // 티켓 생성
    await client.create(Ticket, {
        ticketId: ticketId,
        title: title,
        status: "open"
    });

    // 직원에게 티켓 할당
    await client.link(
        { $apiName: "Employee", $primaryKey: employeeId },
        "assignedTickets",
        { $apiName: "Ticket", $primaryKey: ticketId }
    );

    // 새로 할당한 티켓까지 포함해 직원의 전체 업무량을 질의합니다.
    // 쓰기 후 읽기 보장 덕분에 이 질의가 동작합니다.
    // where 절은 객체 타입 자신의 속성만 필터링하므로,
    // Ticket 속성으로 필터링하기 전에 pivotTo()로 assignedTickets 링크를 따라갑니다.
    const result = await client(Employee)
        .where({ employeeId: { $eq: employeeId } })
        .pivotTo("assignedTickets")
        .where({ status: { $eq: "open" } })
        .aggregate({ $select: { $count: "unordered" } });

    return {
        ticketId: ticketId,
        totalAssignedTickets: result.$count
    };
}

export default assignTicketAndCheckWorkload;
```

**설명**: 입력은 직원 ID와 티켓 제목이고, 출력은 새 티켓 ID와 그 직원이 가진 열린 티켓 수입니다. 동작 순서는 (1) 티켓 생성, (2) 직원과 티켓 링크, (3) 직원에서 `assignedTickets` 링크를 따라 티켓으로 이동(`pivotTo`)한 뒤 `status`가 `"open"`인 것만 세기(`aggregate`)입니다. 일반 편집 함수였다면 (1)과 (2)는 함수가 끝난 뒤에야 적용되므로 (3)의 개수에 새 티켓이 빠집니다. 스테이징 쓰기에서는 (3)의 결과에 방금 만든 티켓이 포함됩니다. 예를 들어 직원이 원래 열린 티켓 2개를 갖고 있었다면 `totalAssignedTickets`는 3이 됩니다.

<a id="calling-other-functions-from-a-staged-write-function"></a>
## 스테이징 쓰기 함수에서 다른 함수 호출하기 (Calling other functions from a staged-write function)

스테이징 쓰기 함수 안에서 다른 함수나 질의를 호출하면, 그 작업들도 같은 스테이징 편집에 참여합니다. 모든 읽기는 이 실행에서 이전에 스테이징된 편집을 반영하고, 호출된 함수가 만든 편집은 같은 스테이징 편집에 추가됩니다. 이는 다음에 적용됩니다.

* 다른 TypeScript 스테이징 쓰기 함수
* AIP Logic 함수
* 온톨로지 질의

최상위 함수가 성공적으로 끝나면, 중첩 호출 전체에 걸쳐 스테이징된 모든 편집이 함께 커밋됩니다. 어느 호출이든 오류를 던지면 전체 묶음이 롤백됩니다.

아래 예제에서 `assignTicket`은 같은 리포지토리에서 게시한 별도의 스테이징 쓰기 함수입니다. `bulkAssignTickets`는 OSDK가 생성한 `$Queries` 임포트를 통해 이 함수를 호출하며, 각 호출은 자신의 편집을 같은 스테이징 편집에 추가합니다.

```typescript tab="TypeScript v2"
import { Employee, Ticket, $Queries } from "@ontology/sdk";
import { Edits, Integer } from "@osdk/functions";
import { WriteableClient } from "@osdk/functions/experimental";

type OntologyEdit = Edits.Object<Ticket> | Edits.Link<Employee, "assignedTickets">;

async function bulkAssignTickets(
    client: WriteableClient<OntologyEdit>,
    employeeId: Integer,
    ticketIds: string[]
): Promise<Integer> {
    let assignedCount = 0;

    for (const ticketId of ticketIds) {
        // assignTicket을 호출할 때마다 그 편집이
        // 호출한 함수의 편집과 함께 스테이징됩니다.
        await client($Queries.assignTicket).executeFunction({
            employeeId: employeeId,
            ticketId: ticketId,
        });

        assignedCount++;
    }

    // 중첩 호출 전체에서 스테이징된 모든 편집은
    // 최상위 함수가 끝날 때 함께 커밋됩니다.
    return assignedCount;
}

export default bulkAssignTickets;
```

**설명**: 티켓 ID 목록을 받아 반복문에서 `client($Queries.assignTicket).executeFunction({...})`로 다른 함수를 한 번씩 호출합니다. 티켓이 5개라면 `assignTicket`이 5번 실행되고, 그 편집 5묶음이 모두 하나의 스테이징 영역에 쌓입니다. 네 번째 호출에서 오류가 나면 앞의 세 번 호출로 만든 편집까지 모두 롤백되어, "일부 티켓만 할당된" 중간 상태가 남지 않습니다.

> **중간 요약**: 스테이징 쓰기 함수 안에서 호출한 다른 스테이징 쓰기 함수, AIP Logic 함수, 온톨로지 질의는 모두 같은 스테이징 편집을 공유합니다. 최상위 함수가 성공하면 전부 함께 커밋되고, 어느 하나라도 실패하면 전부 롤백됩니다.

<a id="execution-lifecycle"></a>
## 실행 생명주기 (Execution lifecycle)

신뢰할 수 있는 함수를 만들려면 스테이징된 편집이 언제 커밋되는지 이해하는 것이 중요합니다.

1. **함수 실행(Function execution):** 모든 작업(생성, 수정, 삭제, 읽기, 중첩 함수 호출)이 온톨로지에 스테이징됩니다. 이 작업들은 함수 자신과 모든 중첩 함수에게는 보이지만, 커밋되기 전까지는 현재 실행 밖에서 보이지 않습니다.
2. **커밋(Commit):** 함수가 성공적으로 끝나면, 액션이 끝나기 전에 스테이징된 모든 편집이 커밋됩니다.
3. **오류 시 롤백(Rollback on error):** 함수가 오류를 던지면 온톨로지는 수정되지 않은 상태로 남고 스테이징된 모든 편집이 폐기됩니다. 그런 다음 액션이 함수를 재시도합니다.

```typescript tab="TypeScript v2"
import { Employee } from "@ontology/sdk";
import { Edits, Integer } from "@osdk/functions";
import { WriteableClient } from "@osdk/functions/experimental";

async function updateEmployeeWithValidation(
    client: WriteableClient<Edits.Object<Employee>>,
    employeeId: Integer,
    newSalary: number
): Promise<Integer> {
    // 입력 검증
    if (newSalary < 0) {
        // 스테이징된 편집은 폐기됩니다
        throw new Error("Salary cannot be negative");
    }

    // 직원 수정
    await client.update(
        { $apiName: "Employee", $primaryKey: employeeId },
        { salary: newSalary }
    );

    // 여기까지 도달하면 스테이징된 모든 편집이 원자적으로 커밋됩니다
}

export default updateEmployeeWithValidation;
```

**설명**: 새 급여가 음수이면 `throw`로 오류를 던져 아무 편집도 커밋되지 않게 하고, 그렇지 않으면 급여를 수정합니다. 함수가 정상적으로 반환되는 것이 곧 "커밋해도 된다"는 신호이고, 예외를 던지는 것이 곧 "롤백하라"는 신호입니다. 따라서 검증 실패를 처리할 때 이미 만든 편집을 수동으로 되돌리는 코드를 작성할 필요가 없습니다.

> **중간 요약**: 실행 중에는 편집이 스테이징되어 실행 내부에만 보이고, 함수가 성공하면 액션 종료 전에 커밋되며, 오류가 나면 폐기된 뒤 액션이 함수를 재시도합니다.

## 정리

- 스테이징 쓰기(베타)는 TypeScript v2 함수에서 온톨로지 편집을 임시로 쌓아 두었다가 함수 성공 시 한꺼번에 커밋하는 실행 모델입니다.
- 같은 실행 안에서는 쓰기 후 읽기가 보장되어, 방금 만든 객체와 링크가 질의와 집계 결과에 바로 반영됩니다.
- 편집을 반환할 필요가 없어 반환값을 자유롭게 쓸 수 있고, `Edits` 타입으로 편집 대상을 선언한 `WriteableClient`로 `create`, `update`, `delete`, `link`, `unlink`를 호출합니다.
- 다른 스테이징 쓰기 함수, AIP Logic 함수, 온톨로지 질의를 중첩 호출해도 모두 같은 스테이징 편집에 참여하며, 어느 하나라도 실패하면 전체가 롤백됩니다.
- 인터페이스 편집은 지원되지 않고, 일대다 링크는 외래 키 속성 수정으로 편집합니다.
