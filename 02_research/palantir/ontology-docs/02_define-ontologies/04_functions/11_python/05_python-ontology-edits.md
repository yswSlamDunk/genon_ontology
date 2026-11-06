# Python 온톨로지 편집 (Ontology edits)

- 원문: https://www.palantir.com/docs/foundry/functions/python-ontology-edits/
- 사이드바 위치: Define Ontologies > Functions > Python > Ontology edits

이 페이지는 Python 함수(function)에서 온톨로지 객체를 생성, 수정, 삭제하고 링크를 바꾸는 편집(edit) API를 설명합니다. 편집 함수는 편집 목록을 만들어 반환할 뿐이고, 실제 데이터 변경은 이 함수를 액션 타입에 연결해 실행할 때 일어납니다. 편집 함수 선언 규칙, 편집 컨테이너, 속성과 구조체(struct) 속성 수정, 링크 수정, 객체 생성과 삭제를 차례로 다룹니다.

온톨로지에서 데이터를 읽는 함수뿐 아니라, 객체를 생성하고 객체의 속성(property)과 객체 사이의 링크를 편집하는 함수도 작성할 수 있습니다. 이 페이지는 함수에서 사용할 수 있는 객체 편집 API를 설명합니다. 편집 함수가 동작하는 방식에 대한 자세한 내용은 [개요 페이지](../09_language-agnostic-features/01_edits-overview.md)를 참고하세요.

Python은 [스테이징 쓰기(staged writes)](06_python-staged-writes.md)도 지원합니다. 스테이징 쓰기는 쓰기 후 읽기(read-after-write) 보장을 제공하고 다른 스테이징 쓰기 함수를 중첩 호출할 수 있게 해 줍니다. 함수가 방금 편집한 데이터를 질의해야 한다면 스테이징 쓰기를 사용하세요.

함수에서 만든 편집이 실제로 적용되려면, 온톨로지 편집 함수를 *[함수 기반 액션(function-backed Action)](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)으로 구성해야 합니다*. 액션을 이렇게 구성하면 추가 메타데이터를 제공하고, 권한을 설정하고, 여러 운영 인터페이스에서 액션에 접근할 수 있습니다. [문서](../09_language-agnostic-features/01_edits-overview.md#when-edits-are-applied)에서 설명하듯이, 편집 함수를 액션 밖에서 실행하면 객체 데이터가 실제로 수정되지 않습니다.

**주의**: 객체를 편집한 직후에 객체를 검색하면 예상과 다른 결과가 나올 수 있습니다. 자세한 내용은 [주의 사항(Caveats) 절](../09_language-agnostic-features/01_edits-overview.md#edits-and-object-search)을 참고하세요.

**설명**: 편집 함수의 출력은 "Employee 23번의 `last_name`을 Kim으로 바꾼다", "Ticket 7번을 새로 만든다" 같은 변경 명령의 목록입니다. 함수만 단독으로 실행하면 이 목록이 만들어지고 끝나며, 데이터는 그대로입니다. 액션이 함수를 실행하고 반환된 목록을 받아 온톨로지에 적용할 때 비로소 데이터가 바뀝니다. 이렇게 나누어 두면 누가 어떤 권한으로 언제 변경했는지를 액션 단위로 관리할 수 있습니다.

<a id="define-an-edit-function"></a>
## 편집 함수 정의하기 (Define an edit function)

온톨로지를 편집하는 함수는 다음 조건을 지켜야 합니다.

* 편집할 객체 타입을 지정하기 위해 `functions.api`에서 임포트한 `@function(edits=[MyObjectType])` 데코레이터를 붙여야 합니다.
* 편집하는 다대다(many-to-many) 링크 타입은 역시 `functions.api`에서 임포트한 `OntologyLinkType(SourceObjectType, "linkApiName")`으로 선언해야 합니다. 자세한 내용은 [편집하는 링크 타입 선언하기](#declare-edited-link-types)를 참고하세요.
* `functions.api`에서 임포트한 `list[OntologyEdit]`를 반환 타입 힌트로 명시해야 합니다.

<a id="construct-an-ontology-edits-container"></a>
## 온톨로지 편집 컨테이너 만들기 (Construct an Ontology edits container)

Python 함수에서 온톨로지 편집을 수행하려면, 먼저 [OSDK 클라이언트](03_python-functions-on-objects.md)에서 온톨로지 편집 컨테이너를 만듭니다. 예를 들면 다음과 같습니다.

```python
ontology_edits = FoundryClient().ontology.edits()
```

이 컨테이너는 함수에서 만든 모든 편집을 추적하는 데 쓰입니다.

**설명**: 편집 컨테이너는 함수 안에서 일어난 변경을 차례로 기록해 두는 객체입니다. 함수 끝에서 `ontology_edits.get_edits()`를 호출하면 지금까지 기록된 편집 목록이 나오고, 이것을 `list[OntologyEdit]`로 반환합니다.

> **중간 요약**: 편집 함수는 `@function(edits=[...])`로 편집 대상 객체 타입(그리고 다대다 링크 타입)을 선언하고 `list[OntologyEdit]`를 반환해야 하며, 함수 기반 액션으로 실행될 때만 편집이 실제로 적용됩니다. 편집은 `FoundryClient().ontology.edits()`로 만든 컨테이너에 기록됩니다.

<a id="update-properties"></a>
## 속성 수정하기 (Update properties)

Python 함수에서 온톨로지 객체는 기본적으로 읽기 전용입니다. 속성을 수정하려고 하면 예외가 발생합니다.

객체를 편집하려면 먼저 온톨로지 편집 컨테이너를 사용해 그 객체의 편집 가능한 뷰(editable view)를 얻어야 합니다. 기존 객체 인스턴스에서 얻을 수도 있고,

```python
editable_object = ontology_edits.objects.MyObjectType.edit(my_object)
```

객체의 기본 키(primary key)로 얻을 수도 있습니다.

```python
editable_object = ontology_edits.objects.MyObjectType.edit(object_primary_key)
```

편집 가능한 객체를 얻은 뒤에는 객체의 속성 값을 다시 대입해서 속성 값을 편집할 수 있습니다. 예를 들면 다음과 같습니다.

```python
editable_employee.last_name = new_name
```

같은 함수 실행 안에서 이후에 `editable_employee`의 `last_name` 속성 값에 접근하면 방금 설정한 새 값이 나옵니다. 하지만 원래의 편집 불가능한 객체에는 변경 사항이 반영되지 *않습니다*.

편집 가능한 객체의 배열 속성은 변경 가능한 `list` 값이지만, 편집은 속성에 대입할 때만 기록되므로 리스트를 제자리에서(in place) 수정한 내용은 아무 경고 없이 버려집니다. 배열을 수정하려면 복사본을 만들어 수정한 뒤 속성을 갱신하세요.

```python
# 새 배열로 복사합니다
array_copy = list(editable_object.my_array_property)
# 이제 복사한 배열을 수정할 수 있습니다
array_copy.append(new_item)
# 그런 다음 속성 값을 덮어씁니다
editable_object.my_array_property = array_copy
```

기존 객체의 기본 키 속성 값은 수정할 수 없습니다.

**설명**: 편집 기록은 `editable_object.속성 = 값` 형태의 대입 문장이 실행될 때 남습니다. `editable_object.my_array_property.append(x)`는 리스트 객체 내부만 바꿀 뿐 속성에 대한 대입이 일어나지 않으므로 편집 컨테이너가 이를 알지 못합니다. 그래서 `list(...)`로 복사하고, 복사본을 고치고, 다시 대입하는 세 단계를 거쳐야 합니다. 기본 키를 바꿀 수 없는 이유는 기본 키가 객체의 정체성 자체이기 때문입니다. 기본 키를 바꾸고 싶다면 새 객체를 만들고 기존 객체를 삭제해야 합니다.

<a id="edit-struct-properties"></a>
## 구조체 속성 편집하기 (Edit struct properties)

**참고**: 베타(Beta). 구조체(struct) 속성은 Python 함수에서 베타 기능입니다. `@function` 데코레이터의 `beta` 인자로 구조체 속성을 활성화할 수 있으며, 생성된 구조체 속성 클래스는 객체별 온톨로지 SDK 모듈에서 임포트합니다.

객체를 생성할 때는 먼저 `create()`를 호출한 다음, 반환된 편집 가능한 객체에 구조체 속성을 대입합니다. 구조체 속성은 `create()`에 키워드 인자로 직접 넘길 수 없습니다.

```python
from functions.api import function, OntologyEdit
from ontology_sdk import FoundryClient
from ontology_sdk.ontology.objects import MyObjectType
from ontology_sdk.ontology.objects.my_object_type import MyStructPropertyClass

@function(beta=True, edits=[MyObjectType])
def create_object(primary_key: str) -> list[OntologyEdit]:
    ontology_edits = FoundryClient().ontology.edits()

    new_object = ontology_edits.objects.MyObjectType.create(primary_key)
    new_object.my_struct_property = MyStructPropertyClass(
        first_field="Example value",
        second_field=True,
    )

    return ontology_edits.get_edits()
```

**설명**: 기본 키를 입력받아 객체를 만들고, 구조체 속성에 두 필드를 가진 값을 대입한 뒤 편집 목록을 반환합니다. 이 코드에 편집 함수의 세 가지 요건(`edits=[...]` 선언, 편집 컨테이너 사용, `list[OntologyEdit]` 반환)이 모두 들어 있습니다. `beta=True`는 구조체 속성 같은 베타 기능을 켜는 인자입니다.

생성된 구조체 속성 클래스는 Python 필드 이름을 대응하는 온톨로지 API 이름으로 변환해 줍니다. 사용자가 정의한 클래스나 `dataclass`로 대신할 수 없습니다.

기존 구조체 속성 안의 필드 하나를 수정하려면, 필드를 바꾼 뒤 구조체 속성 전체를 편집 가능한 객체에 다시 대입합니다.

```python
editable_object = ontology_edits.objects.MyObjectType.edit(my_object)

struct_property = editable_object.my_struct_property
struct_property.first_field = "Updated value"
editable_object.my_struct_property = struct_property
```

`editable_object.my_struct_property.first_field = "Updated value"`처럼 필드를 직접 바꾸면 온톨로지 편집이 등록되지 않습니다.

**설명**: 배열 속성과 같은 원리입니다. 편집은 객체의 속성에 대입할 때만 기록되므로, 구조체 내부 필드를 바꾼 뒤 구조체 전체를 다시 속성에 대입해야 합니다.

> **중간 요약**: 객체는 기본적으로 읽기 전용이므로 `edit()`로 편집 가능한 뷰를 얻은 뒤 속성에 값을 대입해 편집합니다. 편집은 대입할 때만 기록되므로 배열과 구조체는 복사하거나 꺼내서 수정한 뒤 속성 전체를 다시 대입해야 하며, 기본 키는 바꿀 수 없습니다.

<a id="update-links"></a>
## 링크 수정하기 (Update links)

단일 링크(single-link)와 다중 링크(multi-link) 속성에는 링크를 수정하는 여러 메서드가 있습니다.

```python
# 직원의 상사를 설정합니다
editable_employee.supervisor.set(new_supervisor)

# 직원의 상사를 지웁니다
editable_employee.supervisor.clear()

# 해당 직원에게 새 부하 직원을 추가합니다
editable_employee.reports.add(new_report)

# 해당 직원과 연결된 기존 부하 직원을 제거합니다
editable_employee.reports.remove(new_report)
```

속성 수정과 마찬가지로, 링크를 수정한 뒤 `editable_employee`의 링크에 접근하면 수정한 내용이 반영되어 있습니다.

**설명**: 단일 링크는 상대 객체가 최대 하나인 링크(직원 한 명의 상사는 한 명)이므로 `set`과 `clear`를 쓰고, 다중 링크는 상대 객체가 여러 개일 수 있는 링크(상사 한 명의 부하 직원은 여러 명)이므로 `add`와 `remove`를 씁니다.

<a id="declare-edited-link-types"></a>
### 편집하는 링크 타입 선언하기 (Declare edited link types)

다대다 링크를 편집하는 함수는 `@function` 데코레이터의 `edits` 파라미터에 `OntologyLinkType`으로 그 링크 타입을 선언해야 합니다. 그래야 액션이 완전한 [출처(provenance)](../../03_action-types/11_function-backed-actions/02_function-actions-getting-started.md#provenance) 정보를 받습니다. `OntologyLinkType`은 출발하는 객체 타입과 그 객체 타입에 정의된 링크 타입 API 이름을 받습니다. 이 API 이름은 링크 타입의 온톨로지 API 이름이며, 편집 가능한 객체에서 링크에 접근할 때 쓰는 속성 이름과 다를 수 있습니다.

링크를 추가하고 제거하는 전체 예제는 [링크 타입 편집](../09_language-agnostic-features/01_edits-overview.md#link-type-edits)의 Python 탭을 참고하세요.

일대일(one-to-one)과 일대다(one-to-many) 링크는 두 객체 타입 중 한쪽의 외래 키 속성으로 뒷받침되므로, 이런 링크를 설정하거나 지우면 링크 편집이 아니라 객체 편집이 만들어집니다. 이런 링크 타입에서는 링크 타입을 선언하는 대신 외래 키를 가진 객체 타입을 선언합니다.

**설명**: 예를 들어 Employee의 `supervisor` 링크가 Employee 테이블의 `supervisor_id` 외래 키 열로 구현되어 있다면, `supervisor.set(...)`은 실제로 Employee 객체의 `supervisor_id` 속성을 바꾸는 객체 편집입니다. 따라서 `edits=[Employee]`만 선언하면 됩니다. 반면 Employee와 Ticket의 다대다 링크는 별도의 조인 테이블로 구현되므로 `OntologyLinkType(Employee, "assignedTickets")`처럼 링크 타입 자체를 선언해야 합니다. 이때 `"assignedTickets"`는 온톨로지의 API 이름이고, Python 코드의 속성 이름은 `assigned_tickets`처럼 다른 표기일 수 있다는 점에 주의하세요.

> **중간 요약**: 단일 링크는 `set`과 `clear`, 다중 링크는 `add`와 `remove`로 수정합니다. 다대다 링크를 편집하면 `OntologyLinkType`으로 링크 타입을 선언해야 하고, 일대일과 일대다 링크는 외래 키를 가진 객체 타입만 선언하면 됩니다.

<a id="create-objects"></a>
## 객체 생성하기 (Create objects)

온톨로지 편집 컨테이너의 `MyObjectType.create()` 메서드로 새 객체를 생성할 수 있습니다. 새 객체를 만들 때는 기본 키 값을 반드시 지정해야 합니다.

이 예제에서는 주어진 ID로 새 Ticket 객체를 만들고, `due_date` 속성을 설정하고, `assigned_tickets` 링크를 수정해 주어진 Employee에게 할당합니다.

```python
from datetime import datetime, timedelta

from functions.api import function, Integer, Array, OntologyEdit, OntologyLinkType
from ontology_sdk import FoundryClient
from ontology_sdk.ontology.objects import Employee, Ticket

@function(edits=[Employee, Ticket, OntologyLinkType(Employee, "assignedTickets")])
def create_new_ticket_and_assign_to_employee(
    employee: Employee,
    ticket_id: Integer
) -> list[OntologyEdit]:
    ontology_edits = FoundryClient().ontology.edits()

    new_ticket = ontology_edits.objects.Ticket.create(ticket_id)
    new_ticket.due_date = datetime.now() + timedelta(days=7)

    editable_employee = ontology_edits.objects.Employee.edit(employee)
    editable_employee.assigned_tickets.add(new_ticket)

    return ontology_edits.get_edits()
```

**설명**: 입력은 Employee 객체와 티켓 ID이고, 출력은 편집 3개(티켓 생성, 티켓의 `due_date` 설정, 직원과 티켓의 링크 추가)를 담은 목록입니다. 데코레이터의 `edits`에는 편집하는 객체 타입 두 개와 다대다 링크 타입 하나가 모두 선언되어 있습니다. 마감일은 실행 시각에서 7일 뒤로 설정됩니다.

기본 키 외에 구조체가 아닌 속성 값도 create 메서드에 직접 넘길 수 있습니다. 예를 들면 다음과 같습니다.

```python
new_due_date = datetime.now() + timedelta(days=7)
new_ticket = ontology_edits.objects.Ticket.create(ticket_id, due_date=new_due_date)
```

<a id="delete-objects"></a>
## 객체 삭제하기 (Delete objects)

온톨로지 편집 컨테이너의 `MyObjectType.delete()` 메서드를 호출해 객체를 삭제할 수 있습니다.

이 예제에서는 주어진 직원에게 할당된 모든 티켓을 삭제합니다.

```python
for ticket in employee.tickets:
    ontology_edits.objects.Ticket.delete(ticket)
```

인스턴스 대신 기본 키로 객체를 삭제할 수도 있습니다.

```python
ontology_edits.objects.Ticket.delete(ticket_id)
```

> **중간 요약**: `create(기본 키, 속성=값)`으로 객체를 만들고(구조체 속성은 생성 후 대입), `delete(인스턴스 또는 기본 키)`로 객체를 삭제합니다.

## 정리

- Python 편집 함수는 `@function(edits=[...])`로 편집 대상을 선언하고 `list[OntologyEdit]`를 반환하며, 함수 기반 액션으로 실행될 때만 실제로 데이터가 바뀝니다.
- `FoundryClient().ontology.edits()` 컨테이너로 `edit()`, `create()`, `delete()`를 호출해 객체를 편집하고, 마지막에 `get_edits()`로 편집 목록을 반환합니다.
- 편집은 속성에 대입할 때만 기록되므로 배열과 구조체 속성은 복사본을 수정한 뒤 다시 대입해야 하고, 기본 키는 수정할 수 없습니다.
- 링크는 단일 링크의 `set`과 `clear`, 다중 링크의 `add`와 `remove`로 수정하며, 다대다 링크는 `OntologyLinkType`으로 선언해야 합니다.
- 방금 편집한 데이터를 같은 함수에서 질의해야 한다면 스테이징 쓰기를 사용합니다.
