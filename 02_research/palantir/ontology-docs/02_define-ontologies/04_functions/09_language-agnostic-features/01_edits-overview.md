# 온톨로지 편집 (Ontology edits)

- 원문: https://www.palantir.com/docs/foundry/functions/edits-overview/
- 사이드바 위치: Define Ontologies > Functions > Language-agnostic features > Ontology edits

이 페이지는 함수(function)가 객체를 생성, 수정, 삭제하거나 링크를 추가, 제거하는 "온톨로지 편집(edit)"을 어떻게 표현하는지를 언어(TypeScript v1, TypeScript v2, Python)와 상관없이 공통된 관점에서 설명합니다. 특히 편집 함수를 실행하는 것만으로는 실제 객체가 바뀌지 않는다는 점, 그리고 편집 결과가 같은 함수 안의 검색에는 반영되지 않는다는 점처럼 처음 접할 때 오해하기 쉬운 동작 방식을 다룹니다.

**온톨로지 편집(Ontology edit)은** 객체를 생성, 수정, 삭제하는 행위입니다. 함수는 [함수 기반 액션(function-backed action)](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)에서 사용할 수 있도록 [온톨로지 편집](../04_types-reference.md#ontology-edit)을 반환하는 것을 지원합니다.

* TypeScript v1 함수는 `@OntologyEditFunction` 데코레이터를 사용해 작성하며, 이 데코레이터가 특별한 의미를 부여해 코드를 단순하게 만들어 줍니다. TypeScript v1 함수는 또한 [`@Edits` 데코레이터](../12_typescript-v1/03_api-ontology-edits.md#the-edits-decorator)를 사용해 액션에 출처(provenance) 정보를 제공하며, 액션은 이 정보를 사용해 [권한을 강제](../../03_action-types/19_permissions.md)할 수 있습니다. [온톨로지 편집 검증](../16_unit-testing-tsv1/03_unit-test-ontology-edits.md)용 API를 사용해 TypeScript v1 온톨로지 편집 함수에 대한 단위 테스트를 작성할 수 있습니다.
* TypeScript v2 함수는 `@osdk/functions` 패키지에서 내보내는 [`createEditBatch`](../10_typescript-v2/04_typescript-v2-ontology-edits.md#construct-an-ontology-edits-batch) 함수를 사용해 작성합니다. 이 함수들은 `Edits` 타입을 사용해 액션에 출처 정보를 제공합니다.
* Python 함수는 온톨로지 SDK에서 내보내는 [`FoundryClient`](../11_python/05_python-ontology-edits.md#construct-an-ontology-edits-container)를 사용해 편집 컨테이너를 만들어 작성합니다. 이 함수들은 [`@function`](../11_python/05_python-ontology-edits.md#define-an-edit-function) 데코레이터의 `edits` 파라미터를 사용해 액션에 출처 정보를 제공합니다.

**설명**: 세 언어 모두 공통된 구조를 가집니다. 함수는 객체를 직접 고치는 대신 "어떤 객체를 어떻게 바꿀지"를 담은 편집 목록을 만들어 반환합니다. 그리고 함수가 어떤 객체 타입을 편집할 수 있는지 미리 선언합니다(TypeScript v1의 `@Edits`, TypeScript v2의 `Edits` 타입, Python의 `edits` 파라미터). 이 선언이 출처(provenance) 정보로, 액션이 실행될 때 사용자가 그 객체 타입을 편집할 권한이 있는지 확인하는 데 쓰입니다. 데코레이터는 TypeScript나 Python에서 함수나 클래스 정의 위에 `@이름` 형태로 붙여 추가 동작이나 메타데이터를 부여하는 문법입니다.

<a id="link-type-edits"></a>
### 링크 타입 편집 (Link type edits)

두 객체 사이에 링크를 추가하거나 제거하는 것도 객체를 생성하거나 속성(property) 값을 바꾸는 것과 마찬가지로 온톨로지 편집입니다. 완전한 [출처](../../03_action-types/11_function-backed-actions/02_function-actions-getting-started.md#provenance) 정보를 위해, 다대다(many-to-many) 링크는 링크 편집을 선언하고, 일대일(one-to-one)과 일대다(one-to-many) 링크는 외래 키를 가진 객체 타입에 대한 편집을 선언하세요.

**설명**: 관계형 데이터베이스에서 일대다 관계는 "다" 쪽 테이블의 외래 키 열로 표현됩니다. 예를 들어 `Ticket` 테이블에 `assignee_id` 열이 있다면, 티켓을 다른 직원에게 넘기는 것은 `Ticket` 행의 `assignee_id` 값을 바꾸는 일이므로 `Ticket` 객체 타입에 대한 편집이 됩니다. 반면 다대다 관계는 별도의 조인 테이블(예: `employee_id`, `ticket_id` 두 열로 이루어진 테이블)의 행을 추가하거나 지우는 일이므로, 어느 한쪽 객체 타입이 아니라 링크 자체에 대한 편집으로 선언합니다.

다음 예제에서 `assignedTickets`는 `Employee` 객체 타입에서 `Ticket` 객체 타입으로 가는 다대다 링크 타입입니다. 함수는 한 티켓에 대한 링크를 추가하고 다른 티켓에 대한 링크를 제거합니다.

```typescript tab="TypeScript v2"
import { Employee, Ticket } from "@ontology/sdk";
import { Client, Osdk } from "@osdk/client";
import { createEditBatch, Edits } from "@osdk/functions";

type OntologyEdit = Edits.Link<Employee, "assignedTickets">;

export default function reassignTicket(
    client: Client,
    employee: Osdk.Instance<Employee>,
    ticketToAssign: Osdk.Instance<Ticket>,
    ticketToUnassign: Osdk.Instance<Ticket>,
): OntologyEdit[] {
    const batch = createEditBatch<OntologyEdit>(client);

    batch.link(employee, "assignedTickets", ticketToAssign);
    batch.unlink(employee, "assignedTickets", ticketToUnassign);

    return batch.getEdits();
}
```

(원문에는 같은 동작을 하는 TypeScript v1 버전(`@Edits(Employee, Ticket)`과 `@OntologyEditFunction()` 데코레이터 사용)과 Python 버전(`@function(edits=[OntologyLinkType(Employee, "assignedTickets")])` 사용)도 있습니다.)

**설명**: 이 함수는 직원 객체 하나와 티켓 객체 두 개를 입력받습니다. `type OntologyEdit = Edits.Link<Employee, "assignedTickets">` 줄이 이 함수가 `Employee`의 `assignedTickets` 링크를 편집한다고 선언하는 부분입니다. `createEditBatch`로 편집 묶음(batch)을 만들고, `batch.link`로 링크 추가를, `batch.unlink`로 링크 제거를 기록합니다. 마지막 `batch.getEdits()`는 기록된 편집 목록을 반환할 뿐이며, 이 시점에 데이터가 실제로 바뀌지는 않습니다.

이 문서의 나머지 부분에서는 온톨로지 편집 함수가 내부적으로 어떻게 동작하는지 설명하여, 그 밑에 있는 인프라를 더 잘 이해할 수 있도록 합니다.

> **중간 요약**: 온톨로지 편집은 객체의 생성, 수정, 삭제와 링크의 추가, 제거를 뜻하며, 함수는 편집 목록을 반환해 함수 기반 액션에서 사용됩니다. 언어마다 문법은 다르지만 모두 편집할 대상을 미리 선언해 액션에 출처 정보를 제공합니다.

<a id="when-edits-are-applied"></a>
### 편집이 적용되는 시점 (When edits are applied)

온톨로지 편집 함수에 대해 흔히 하는 오해는, 함수를 실행하면 온톨로지의 객체가 갱신되는지에 관한 것입니다. **Authoring**의 functions 도우미에서 온톨로지 편집 함수를 실행해도 편집이 실제 객체에 적용되지는 않습니다. 함수를 사용해 객체를 갱신하는 유일한 방법은 [함수 기반 액션](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md) 문서에 설명된 대로, 액션이 그 함수를 사용하도록 구성하는 것입니다.

따라서 객체 자체가 갱신될 걱정 없이 functions 도우미에서 온톨로지 편집 함수를 자유롭게 실행해 다양한 입력에 대한 결과를 검증할 수 있습니다.

![결과 창](https://www.palantir.com/docs/resources/foundry/functions/results-pane-edits.png "객체에 대한 편집을 보여 주는 결과 창.")

**설명**: 즉 편집 함수의 반환값은 "변경 계획"이고, 그 계획을 실제 데이터에 반영하는 주체는 액션입니다. functions 도우미의 결과 창에는 어떤 객체의 어떤 속성이 어떤 값으로 바뀔지가 표시되지만, 저장은 일어나지 않습니다. 데이터베이스 트랜잭션에서 커밋하지 않은 변경 내용을 확인만 하는 상태와 같은 동작입니다.

> **중간 요약**: functions 도우미에서 편집 함수를 실행해도 실제 객체는 바뀌지 않으며, 객체를 실제로 갱신하는 유일한 방법은 함수 기반 액션을 통해 실행하는 것입니다.

<a id="caveats"></a>
### 주의 사항 (Caveats)

<a id="edits-and-object-search"></a>
#### 편집과 객체 검색 (Edits and object search)

객체와 링크에 대한 변경 사항은 함수 실행이 *끝난 뒤에* 객체 집합(object set) API에 전파됩니다. 따라서 편집된 값에 결과가 좌우되는 `Objects.search()` 질의, 예를 들어 편집한 속성이나 링크에 대한 필터, search around, 집계는 이전 객체, 속성, 링크를 사용하며, 생성과 삭제를 포함한 온톨로지 편집 내용을 반영하지 않을 수 있습니다. 함수에서 이런 경우를 직접 처리해야 합니다.

이는 이미 편집한 특정 객체를 가져오는 경우(예: 기본 키(primary key)로 가져오기)와는 다릅니다. 그 경우에는 객체가 머티리얼라이즈(materialize)될 때 함수 인프라가 대기 중인 편집을 적용하므로, 편집된 속성 값과 링크 값이 반환됩니다. 예시는 [@Edits 데코레이터](../12_typescript-v1/03_api-ontology-edits.md#the-edits-decorator)를 참고하세요.

다음 예제에서는 ID가 1인 Employee가 있다고 가정합니다.

```typescript tab="TypeScript v2"
import { Client } from "@osdk/client";
import { Employee } from "@ontology/sdk";
import { Edits, createEditBatch } from "@osdk/functions";

type OntologyEdit = Edits.Object<Employee>;

async function editAndSearch(client: Client): Promise<OntologyEdit[]> {
    const batch = createEditBatch<OntologyEdit>(client);

    const employeeOne = await client(Employee).fetchOne(1);
    batch.update(employeeOne, { name: "Bob" });

    const count = await client(Employee)
        .where({
            name: {
                $eq: "Bob"
            }
        })
        .aggregate({
            $select: {
                $count: "unordered"
            }
        })
        .then(response => response.$count);
    console.log(count);
    // 기대값: 1, 실제값: 0

    return batch.getEdits();
}

export default editAndSearch;
```

(원문에는 같은 상황을 보여 주는 TypeScript v1 버전과 Python 버전 예제 코드도 있습니다.)

**설명**: 함수는 ID 1인 직원을 가져와 이름을 "Bob"으로 바꾸는 편집을 기록한 다음, 이름이 "Bob"인 직원 수를 셉니다. 개발자는 1을 기대하지만 실제 결과는 0입니다. `batch.update`는 편집을 기록만 할 뿐이고, `where(...).aggregate(...)` 질의는 아직 편집이 반영되지 않은 기존 데이터(인덱스)에 대해 실행되기 때문입니다. 이처럼 편집 후 같은 함수 안에서 검색, 필터, 집계 결과를 사용하려면, 방금 바꾼 값을 코드에서 따로 반영해 계산해야 합니다.

<a id="apply-ontology-edits-in-automate"></a>
#### Automate에서 온톨로지 편집 적용하기 (Apply Ontology edits in Automate)

[Automate](https://www.palantir.com/docs/foundry/automate/overview/)는 이펙트(effect)로 사용된 함수가 반환한 편집을 적용하지 않습니다. 자동화를 통해 온톨로지 편집을 적용하려면 대신 함수 기반 액션을 구성하세요. 자세한 내용은 [함수 이펙트(Function effects)](https://www.palantir.com/docs/foundry/automate/effect-function/)를 참고하세요.

<a id="optional-arrays-in-function-backed-actions"></a>
#### 함수 기반 액션의 선택적 배열 (Optional arrays in function-backed actions)

code repositories에서 `@OntologyEditFunction`을 실행할 때는 생략된 선택적(optional) 배열이 `undefined`로 처리되지만, 액션을 통해 함수를 실행할 때는 빈 배열로 전달됩니다.

**설명**: 예를 들어 `tags?: string[]` 파라미터를 받는 함수에서 `if (tags === undefined)`로 생략 여부를 판단하면, 저장소에서 테스트할 때와 액션으로 실행할 때 동작이 달라집니다. 두 경우를 모두 처리하려면 `undefined`와 빈 배열(`[]`)을 같은 경우로 다루도록 작성하는 편이 안전합니다.

> **중간 요약**: 편집 내용은 함수가 끝난 뒤에 검색 API에 반영되므로 같은 함수 안의 검색, 필터, 집계에는 보이지 않습니다(기본 키로 직접 가져온 객체에는 반영됨). Automate의 함수 이펙트는 편집을 적용하지 않으며, 선택적 배열은 실행 경로에 따라 `undefined` 또는 빈 배열로 전달됩니다.

## 정리

- 온톨로지 편집은 객체의 생성, 수정, 삭제와 링크의 추가, 제거이며, 함수는 편집 목록을 반환해 함수 기반 액션에서 쓰입니다.
- TypeScript v1은 `@OntologyEditFunction`과 `@Edits`, TypeScript v2는 `createEditBatch`와 `Edits` 타입, Python은 `FoundryClient`의 편집 컨테이너와 `@function`의 `edits` 파라미터를 사용합니다.
- 다대다 링크는 링크 편집으로, 일대일과 일대다 링크는 외래 키를 가진 객체 타입 편집으로 선언해야 출처 정보가 완전해집니다.
- functions 도우미에서 실행해도 실제 객체는 바뀌지 않으며, 액션을 통해서만 편집이 적용됩니다.
- 편집은 함수 종료 후 검색 API에 반영되므로 같은 함수 안의 검색 결과에는 보이지 않고, Automate 함수 이펙트는 편집을 적용하지 않습니다.
