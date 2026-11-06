# Python의 단계적 쓰기 (Staged writes)

- 원문: https://www.palantir.com/docs/foundry/functions/python-staged-writes/
- 사이드바 위치: Define Ontologies > Functions > Python > Staged writes

이 페이지는 온톨로지 객체를 편집하는 Python 함수(function)를 위한 또 하나의 실행 방식인 단계적 쓰기(staged writes)를 설명합니다. 일반 편집 함수는 편집 목록을 반환하고 함수가 끝난 뒤에야 반영되지만, 단계적 쓰기 함수는 함수 안에서 한 편집(edit)을 같은 함수 안의 이후 조회에서 바로 볼 수 있고, 다른 단계적 쓰기 함수를 중첩 호출할 수 있습니다. 데이터베이스 트랜잭션 개념을 알고 있으면 이해가 쉽습니다.

**참고**: 베타(Beta). 단계적 쓰기는 개발 단계상 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/)입니다. 활발한 개발 중에 기능이 바뀔 수 있습니다.

실시간 미리 보기(live preview)와 게시된 함수 미리 보기는 Code Repositories에서만 지원되며, 로컬 개발 환경이나 VS Code 작업 공간 환경에서는 지원되지 않습니다.

단계적 쓰기는 온톨로지의 객체를 편집하는 Python 함수에 추가적인 실행 모델을 제공합니다. 일반 [Python 온톨로지 편집 함수](05_python-ontology-edits.md)와 달리 단계적 쓰기 함수는 다음과 같은 특징이 있습니다.

* 함수 안에서 적용한 온톨로지 편집에 대해 쓰기 후 읽기 보장(read-after-write guarantee)을 제공합니다. 함수 안에서 적용한 모든 편집은 단계적으로 쌓이며(staged), 함수 안의 이후 온톨로지 쿼리와 집계에 반영됩니다.
* 온톨로지 편집을 수행하는 다른 단계적 쓰기 함수를 중첩 호출할 수 있습니다.

이 페이지는 Python으로 단계적 쓰기 함수를 작성하는 방법과 그 고유한 특성을 설명합니다. TypeScript v2에 대해서는 [TypeScript v2 함수의 단계적 쓰기](../10_typescript-v2/05_typescript-v2-staged-writes.md)를 참고하세요. 편집 함수의 동작 방식에 대한 자세한 내용은 [온톨로지 편집 개요](../09_language-agnostic-features/01_edits-overview.md)를 참고하세요.

**설명**: "staged"는 "아직 확정(commit)되지 않고 대기 중인 상태"라는 뜻입니다. 데이터베이스에서 `BEGIN` 이후 `INSERT`를 실행하면 같은 트랜잭션 안의 `SELECT`에는 그 행이 보이지만, `COMMIT` 전까지 다른 세션에는 보이지 않습니다. 단계적 쓰기 함수도 이와 같은 방식으로 동작합니다.

<a id="key-differences-from-regular-ontology-edit-functions"></a>
## 일반 온톨로지 편집 함수와의 주요 차이점 (Key differences from regular Ontology edit functions)

단계적 쓰기 함수는 몇 가지 중요한 점에서 일반 편집 함수와 다릅니다.

<a id="read-after-write-guarantee"></a>
### 쓰기 후 읽기 보장 (Read-after-write guarantee)

단계적 쓰기 함수 안에서 읽는 모든 온톨로지 데이터에는 그 함수 안에서 앞서 수행한 모든 편집과, 같은 액션 실행 안에서 이 함수를 호출한 단계적 쓰기 함수가 수행한 모든 편집이 반영됩니다. 이 편집들은 단계적으로 쌓여 있을 뿐이며, 실행 컨텍스트 밖의 다른 사용자나 함수에는 보이지 않습니다. 함수 안에서 검색 요청과 집계로 온톨로지를 조회할 수 있으며, 그 결과에는 앞서 쌓인 모든 편집이 반영됩니다.

<a id="no-requirement-to-return-edits"></a>
### 편집을 반환할 필요 없음 (No requirement to return edits)

일반 Python 온톨로지 편집 함수는 편집이 적용되도록 온톨로지 편집 묶음(batch)을 반환해야 합니다. 단계적 쓰기 함수는 편집을 자동으로 단계적으로 쌓아 두었다가 액션이 완료될 때 온톨로지에 적용합니다. 따라서 함수는 편집 대신 지원되는 어떤 함수 타입이든 반환할 수 있습니다.

<a id="atomic-execution"></a>
### 원자적 실행 (Atomic execution)

쿼리, 함수 호출, AIP Logic 실행을 포함해 단계적 쓰기 함수 안의 모든 작업은 편집을 함께 쌓습니다. 함수가 성공적으로 끝나면 편집이 온톨로지에 커밋됩니다. 함수가 오류를 발생시키면 온톨로지는 수정되지 않은 상태로 남고, 액션이 함수를 재시도하기 전에 쌓인 편집이 모두 폐기됩니다.

**설명**: 원자성(atomicity)은 "전부 반영되거나 전혀 반영되지 않거나" 둘 중 하나라는 성질입니다. 예를 들어 함수가 Ticket 3개를 만들고 네 번째에서 예외가 나면, 앞의 3개도 온톨로지에 남지 않습니다.

<a id="writeableclient"></a>
### `WriteableClient`

Python 단계적 쓰기 함수는 표준 `FoundryClient` 대신 생성된 `WriteableClient`를 사용합니다. `WriteableClient`로 단계적 쓰기 컨테이너를 만듭니다. 이 컨테이너는 일반 Python 편집 컨테이너와 같은 객체 및 링크 편집 API를 제공하지만, 그 편집을 함수에서 반환하지는 않습니다.

> **중간 요약**: 단계적 쓰기 함수는 함수 안에서 한 편집을 이후 조회에서 바로 볼 수 있고, 편집을 반환할 필요 없이 액션 완료 시 한꺼번에 커밋되며, 오류가 나면 전부 버려집니다. 클라이언트로는 `WriteableClient`를 씁니다.

<a id="define-a-staged-write-function"></a>
## 단계적 쓰기 함수 정의하기 (Define a staged-write function)

Python 단계적 쓰기 함수를 정의하려면 다음과 같이 합니다.

* `@function` 데코레이터에 `beta=True`를 설정합니다.
* 데코레이터의 `edits` 파라미터로 함수가 편집할 수 있는 모든 객체 타입과 링크 타입을 선언합니다. 중첩 함수 호출을 통해 편집하는 것도 포함합니다. 링크 편집을 선언하려면 `OntologyLinkType(SourceObjectType, "linkApiName")`을 사용합니다.
* 첫 번째 파라미터에 생성된 `WriteableClient` 타입을 주석(annotation)으로 지정합니다. 함수 런타임이 액션 실행의 트랜잭션 컨텍스트를 담은 클라이언트를 주입하므로, 함수 안에서 클라이언트를 직접 생성하지 마세요.
* 지원되는 어떤 함수 타입이든 반환합니다.

다음 함수는 `Employee` 객체 타입에 대한 편집을 선언하고 적용합니다.

```python
from functions.api import Integer, function
from ontology_sdk import WriteableClient
from ontology_sdk.ontology.objects import Employee

@function(beta=True, edits=[Employee])
def update_employee_last_name(
    client: WriteableClient,
    employee_id: Integer,
    new_last_name: str,
) -> Integer:
    staged_writes = client.ontology.staged_writes()
    editable_employee = staged_writes.objects.Employee.edit(employee_id)
    editable_employee.last_name = new_last_name
    return employee_id
```

**설명**: 입력은 직원 ID와 새 성(last name)입니다. `client.ontology.staged_writes()`로 단계적 쓰기 컨테이너를 얻고, `Employee.edit(employee_id)`로 편집 가능한 객체를 받아 `last_name` 속성에 새 값을 대입합니다. 반환값은 편집 목록이 아니라 단순한 정수(직원 ID)입니다. `client`는 호출하는 쪽이 넘기는 값이 아니라 런타임이 주입하는 값입니다.

단계적 쓰기 함수의 편집을 적용하려면 이 함수를 [함수 기반 액션(function-backed action)](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)으로 구성합니다.

<a id="create-objects"></a>
## 객체 만들기 (Create objects)

단계적 쓰기 컨테이너에서 객체 타입의 `create` 메서드를 사용합니다. 객체의 기본 키(primary key)는 반드시 제공해야 하며, 같은 호출에서 다른 속성도 초기화할 수 있습니다.

```python
from functions.api import function
from ontology_sdk import WriteableClient
from ontology_sdk.ontology.objects import Employee

@function(beta=True, edits=[Employee])
def create_employee(
    client: WriteableClient,
    employee_id: str,
    first_name: str,
    last_name: str,
) -> str:
    staged_writes = client.ontology.staged_writes()
    staged_writes.objects.Employee.create(
        employee_id=employee_id,
        first_name=first_name,
        last_name=last_name,
    )
    return employee_id
```

**설명**: `create`의 키워드 인자 중 `employee_id`가 기본 키이고, 나머지는 함께 채울 속성 값입니다. SQL로 보면 `INSERT INTO Employee (employee_id, first_name, last_name) VALUES (...)`에 해당하는 편집이 쌓입니다.

<a id="create-objects-with-generated-ids"></a>
### 생성된 ID로 객체 만들기 (Create objects with generated IDs)

같은 실행 안에서 기본 키를 생성하고, 객체를 만들고, 그 키를 반환하거나 이후에 사용할 수 있습니다.

```python
from uuid import uuid4

from functions.api import function
from ontology_sdk import WriteableClient
from ontology_sdk.ontology.objects import Ticket

@function(beta=True, edits=[Ticket])
def create_ticket(client: WriteableClient, title: str) -> str:
    ticket_id = str(uuid4())
    staged_writes = client.ontology.staged_writes()
    staged_writes.objects.Ticket.create(
        ticket_id=ticket_id,
        title=title,
        status="open",
    )
    return ticket_id
```

**설명**: `uuid4()`는 무작위 128비트 식별자(UUID)를 만듭니다. 충돌 가능성이 사실상 없으므로 기본 키로 쓰기에 적합하며, 만든 ID를 반환해 호출한 쪽이 새 Ticket을 찾을 수 있게 합니다.

<a id="update-objects"></a>
## 객체 수정하기 (Update objects)

단계적 쓰기 컨테이너에서 객체 타입의 `edit` 메서드를 사용합니다. 객체 또는 그 기본 키를 넘긴 다음, 편집 가능한 객체에 새 속성 값을 대입합니다.

```python
staged_writes = client.ontology.staged_writes()
editable_employee = staged_writes.objects.Employee.edit(employee)
editable_employee.last_name = new_name

editable_employee = staged_writes.objects.Employee.edit(23)
editable_employee.last_name = new_name
```

**설명**: 앞 두 줄은 이미 가지고 있는 `employee` 객체를, 뒤 두 줄은 기본 키 값 `23`을 넘겨 같은 편집을 하는 두 가지 방법입니다.

인터페이스 편집은 단계적 쓰기 함수에서 지원되지 않습니다.

<a id="delete-objects"></a>
## 객체 삭제하기 (Delete objects)

객체 또는 그 기본 키를 인자로 객체 타입의 `delete` 메서드를 호출합니다.

```python
staged_writes = client.ontology.staged_writes()
staged_writes.objects.Ticket.delete(ticket)
staged_writes.objects.Ticket.delete(12)
```

<a id="create-or-delete-links"></a>
## 링크 만들기 또는 삭제하기 (Create or delete links)

단계적 쓰기 컨테이너를 통해 객체를 편집한 다음, 링크 속성의 `add` 또는 `remove` 메서드로 다대다(many-to-many) 링크를 편집합니다.

```python
staged_writes = client.ontology.staged_writes()
editable_employee = staged_writes.objects.Employee.edit(employee)
editable_employee.assigned_tickets.add(ticket)
editable_employee.assigned_tickets.remove(ticket)
```

일대다(one-to-many) 링크를 편집하려면 객체 생성 또는 수정 편집으로 외래 키 속성을 편집합니다.

**설명**: 다대다 링크는 데이터베이스에서 별도의 조인 테이블(예: `employee_id`, `ticket_id` 두 열만 있는 테이블)에 행을 넣고 빼는 것에 해당하므로 `add`/`remove`로 다룹니다. 일대다 링크는 "다" 쪽 객체가 "일" 쪽 객체의 키를 외래 키 속성으로 가지고 있으므로, 그 속성 값을 바꾸는 것이 곧 링크를 바꾸는 것입니다.

> **중간 요약**: 단계적 쓰기 컨테이너의 `create`, `edit`, `delete`로 객체를 만들고 고치고 지우며, 다대다 링크는 링크 속성의 `add`/`remove`로, 일대다 링크는 외래 키 속성 수정으로 편집합니다. 인터페이스 편집은 지원되지 않습니다.

<a id="read-after-write-within-a-staged-write-function"></a>
## 단계적 쓰기 함수 안에서의 쓰기 후 읽기 (Read-after-write within a staged-write function)

`WriteableClient`를 통한 읽기에는 같은 실행에서 앞서 쓴 데이터가 반영됩니다. 클라이언트는 온톨로지를 읽기 전에 대기 중인 편집을 단계적 트랜잭션으로 보내므로, 쿼리나 집계에 그 편집이 포함됩니다.

다음 함수는 티켓을 하나 만든 뒤 열린(open) 티켓 수를 셉니다. 결과에는 새로 만든 티켓이 포함됩니다.

```python
from functions.api import Integer, function
from ontology_sdk import WriteableClient
from ontology_sdk.ontology.objects import Ticket

@function(beta=True, edits=[Ticket])
def create_ticket_and_count_open(
    client: WriteableClient,
    ticket_id: str,
    title: str,
) -> Integer:
    staged_writes = client.ontology.staged_writes()
    staged_writes.objects.Ticket.create(
        ticket_id=ticket_id,
        title=title,
        status="open",
    )
    return (
        client.ontology.objects.Ticket.where(
            Ticket.object_type.status == "open"
        )
        .count()
        .compute()
    )
```

**설명**: 실행 전에 열린 티켓이 5개였다면 이 함수는 6을 반환합니다. 일반 편집 함수에서는 함수가 끝나기 전까지 새 티켓이 온톨로지에 반영되지 않으므로 같은 조회가 5를 반환합니다. 이 차이가 쓰기 후 읽기 보장입니다.

<a id="call-other-functions-from-a-staged-write-function"></a>
## 단계적 쓰기 함수에서 다른 함수 호출하기 (Call other functions from a staged-write function)

`WriteableClient`를 통해 다른 함수나 쿼리를 호출하면, 그 작업들도 같은 단계적 편집에 참여합니다. 호출된 함수 안의 읽기에는 실행 중에 앞서 쌓인 편집이 반영되고, 호출된 함수가 수행한 편집은 같은 단계적 편집에 합류합니다. 이는 다음에 적용됩니다.

* 다른 Python 또는 TypeScript v2 단계적 쓰기 함수
* AIP Logic 함수
* 온톨로지 쿼리

최상위 함수가 성공적으로 끝나면 중첩 호출 전체에서 쌓인 모든 편집이 함께 커밋됩니다. 어느 호출에서든 오류가 발생하면 편집 전체가 폐기됩니다.

다음 예제에서 `assign_ticket`은 같은 저장소에서 게시된 별도의 단계적 쓰기 함수입니다. `bulk_assign_tickets`는 OSDK가 생성한 쿼리 API를 통해 이 함수를 호출하며, 각 호출은 같은 단계적 편집에 자신의 편집을 추가합니다.

```python
from functions.api import Integer, OntologyLinkType, function
from ontology_sdk import WriteableClient
from ontology_sdk.ontology.objects import Employee, Ticket

@function(
    beta=True,
    edits=[Ticket, OntologyLinkType(Employee, "assignedTickets")],
)
def bulk_assign_tickets(
    client: WriteableClient,
    employee_id: Integer,
    ticket_ids: list[str],
) -> Integer:
    for ticket_id in ticket_ids:
        client.ontology.queries.assign_ticket(
            employee_id=employee_id,
            ticket_id=ticket_id,
        )
    return len(ticket_ids)
```

**설명**: `edits`에는 이 함수가 직접 편집하지 않더라도 중첩 호출된 `assign_ticket`이 편집하는 대상(Ticket 객체 타입과 Employee의 `assignedTickets` 링크)까지 모두 선언해야 합니다. 티켓 ID 10개를 넘기면 `assign_ticket`이 10번 호출되고, 10번의 편집은 하나의 트랜잭션으로 묶여 모두 커밋되거나 모두 폐기됩니다.

> **중간 요약**: `WriteableClient`로 조회하면 앞서 쌓인 편집이 반영되고, 다른 단계적 쓰기 함수, AIP Logic 함수, 온톨로지 쿼리를 호출하면 그 편집도 같은 트랜잭션에 묶입니다.

<a id="execution-lifecycle"></a>
## 실행 생명주기 (Execution lifecycle)

단계적 쓰기 함수는 다음 실행 생명주기를 따릅니다.

1. **함수 실행(Function execution):** 생성, 수정, 삭제, 읽기, 중첩 함수 호출이 같은 단계적 트랜잭션에 참여합니다. 편집은 해당 함수와 중첩 함수에는 보이지만 커밋될 때까지 실행 밖에는 나타나지 않습니다.
2. **커밋(Commit):** 함수가 성공적으로 끝나면 액션이 완료되기 전에 쌓인 모든 편집이 커밋됩니다.
3. **오류 시 롤백(Rollback on error):** 함수가 오류를 발생시키면 온톨로지는 수정되지 않은 채로 남고 쌓인 편집은 모두 폐기됩니다. 그런 다음 액션이 함수를 재시도할 수 있습니다.

```python
from functions.api import Integer, function
from ontology_sdk import WriteableClient
from ontology_sdk.ontology.objects import Employee

@function(beta=True, edits=[Employee])
def update_employee_with_validation(
    client: WriteableClient,
    employee_id: Integer,
    new_salary: float,
) -> Integer:
    if new_salary < 0:
        raise ValueError("Salary cannot be negative")
    staged_writes = client.ontology.staged_writes()
    editable_employee = staged_writes.objects.Employee.edit(employee_id)
    editable_employee.salary = new_salary
    return employee_id
```

**설명**: `new_salary`가 음수이면 `ValueError`가 발생해 3단계(롤백)로 가고, 온톨로지에는 아무 변화가 없습니다. 0 이상이면 `salary` 편집이 쌓인 뒤 함수가 정상 종료되어 2단계(커밋)로 갑니다.

## 정리

- 단계적 쓰기(베타)는 온톨로지를 편집하는 Python 함수의 추가 실행 모델로, `@function(beta=True, edits=[...])`와 첫 파라미터 `WriteableClient`로 정의합니다.
- 함수 안의 편집은 같은 실행 안의 이후 조회와 집계에 즉시 반영됩니다(쓰기 후 읽기 보장).
- 편집을 반환할 필요가 없고, 함수가 성공하면 모든 편집이 한 번에 커밋되며 오류가 나면 전부 폐기됩니다.
- 다른 단계적 쓰기 함수, AIP Logic 함수, 온톨로지 쿼리를 중첩 호출하면 그 편집도 같은 트랜잭션에 포함됩니다.
- 인터페이스 편집은 지원되지 않으며, 편집을 적용하려면 함수 기반 액션으로 구성해야 합니다.
