# 객체 검색과 집계 스텁하기 (Stub object searches and aggregations)

- 원문: https://www.palantir.com/docs/foundry/functions/unit-test-object-searches/
- 사이드바 위치: Define Ontologies > Functions > Unit testing (TSv1) > Stub object searches and aggregations

이 페이지는 TypeScript v1 함수(function)의 단위 테스트에서 객체 집합(object set) 검색과 집계 호출의 결과를 미리 정해 두는 "스텁(stub)" 사용법을 설명합니다. 테스트 환경에서는 실제 온톨로지 데이터를 조회하지 않으므로, 함수가 검색이나 집계를 호출하면 무엇을 돌려받을지 테스트 코드가 직접 지정해야 합니다.

단위 테스트를 작성할 때, 코드가 수행하는 호출에 대한 응답을 정해 두기 위해 객체 집합 검색이나 객체 집계에 대한 미리 준비된 답(canned answer, "스텁"이라고도 함)을 만들고 싶을 수 있습니다. 스텁을 사용하려면 `"@foundry/functions-testing-lib"`에서 `{ whenObjectSet }`을 import해야 합니다.

**설명**: 단위 테스트는 함수 하나의 로직만 검증하는 테스트입니다. 함수가 데이터베이스나 외부 서비스를 호출하면 테스트 결과가 그 데이터에 따라 달라지므로, 호출 결과를 고정값으로 바꿔치기합니다. 이렇게 "이 호출이 오면 이 값을 돌려준다"고 정해 둔 가짜 응답을 스텁이라고 합니다. `whenObjectSet(호출).thenReturn(값)`이 바로 그 규칙을 등록하는 문법입니다.

<a id="testing-filters-on-object-sets"></a>
#### 객체 집합의 필터 테스트하기 (Testing filters on object sets)

```typescript
import { Objects } from "@foundry/ontology-api";

const objectSet = Objects.search().objectType();

expect(myFunctions.filterObjectSet(objectSet))
        .toEqual(objectSet.filter(s => s.prop.range().gte(0)))
```

**설명**: 이 예제는 스텁 없이 필터 로직을 확인합니다. `filterObjectSet` 함수에 객체 집합을 넣었을 때 반환값이 "`prop` 속성이 0 이상인 객체만 남긴 객체 집합"과 같은지 비교합니다. 실제 데이터를 가져오는 것이 아니라 필터 조건이 같은 객체 집합 정의인지 확인하는 것입니다.

<a id="testing-aggregations-on-an-object-property-using-stubs"></a>
#### 스텁으로 객체 속성 집계 테스트하기 (Testing aggregations on an object property using stubs)

스텁을 사용해 집계 호출에 대한 응답을 정의할 수 있습니다.

```typescript
import { whenObjectSet } from "@foundry/functions-testing-lib"

whenObjectSet(Objects.search().objectType().sum(s => s.property)).thenReturn(55);
```

이는 `Objects.search().objectType().sum(s => s.property))`가 실행될 때마다 결과가 55가 된다는 뜻입니다.

<a id="testing-objects-using-stubs"></a>
#### 스텁으로 객체 테스트하기 (Testing objects using stubs)

특정 객체 검색에 대한 응답도 스텁으로 정의할 수 있습니다.

```typescript
import { whenObjectSet } from "@foundry/functions-testing-lib";

whenObjectSet(Objects.search().objectType().orderBy().takeAsync(10)).thenReturn([employeeObj])
await expect(myFunctions.aggregateSum(objectSet)).resolves.toEqual(65);
```

이는 이 특정 객체 검색 집계가 실행될 때마다 속성 합계가 65로 결정된다는 뜻입니다.

**설명**: 첫 줄은 "정렬 후 상위 10개를 가져오는 검색"의 결과를 `employeeObj` 하나가 담긴 배열로 고정합니다. 둘째 줄은 `aggregateSum` 함수가 그 검색 결과를 바탕으로 합계를 계산했을 때 65가 나오는지 확인합니다. 즉 테스트용 객체 `employeeObj`의 속성 값으로 합계가 계산된다는 전제입니다.

<a id="testing-different-object-sets-using-stubs"></a>
#### 스텁으로 서로 다른 객체 집합 테스트하기 (Testing different object sets using stubs)

검색 생성자(search constructor)를 오버로딩해서 여러 개의 특정 객체 집합 검색을 모킹(mock)할 수 있습니다. 각 객체에 `rid` 속성을 지정해야 합니다.

```typescript
import { whenObjectSet } from "@foundry/functions-testing-lib";

const objA = Objects.create().objectType('a');
const objB = Objects.create().objectType('b');

objA.rid = 'ridA';
objB.rid = 'ridB';

whenObjectSet(Objects.search().ObjType([objA]).all()).thenReturn([objA]);
whenObjectSet(Objects.search().ObjType([objB, objB]).all()).thenReturn([objA, objB]);
```

**설명**: 객체 배열로 시작하는 검색은 어떤 객체로 시작했는지에 따라 다른 검색으로 취급됩니다. 테스트 라이브러리가 두 검색을 구분하려면 객체마다 고유 식별자가 필요하므로 `rid`를 직접 넣어 줍니다. 위 예제에서 `[objA]`로 시작한 검색은 `[objA]`를, `[objB, objB]`로 시작한 검색은 `[objA, objB]`를 돌려줍니다.

<a id="testing-link-traversals-using-stubs"></a>
#### 스텁으로 링크 탐색 테스트하기 (Testing link traversals using stubs)

`searchAround` 탐색도 다른 객체 집합 검색과 같은 방식으로 스텁할 수 있으며, 단일 객체에서 시작해 검색 생성자로 변환하는 경우도 마찬가지입니다. 탐색 메서드 이름은 [링크 타입 필드 이름](../13_functions-on-objects/06_api-objects-links.md#link-types)에서 생성되며, 검색 생성자에 넘기는 각 객체에 `rid` 속성을 지정해야 합니다.

```typescript
import { whenObjectSet } from "@foundry/functions-testing-lib";

const objA = Objects.create().objectType('a');
const objB = Objects.create().objectType('b');

objA.rid = 'ridA';

whenObjectSet(Objects.search().ObjType([objA]).searchAroundLinkField().all()).thenReturn([objB]);
```

**설명**: `searchAround`는 링크를 따라 연결된 객체를 찾는 탐색으로, SQL로 보면 외래 키 조인으로 연결된 행을 가져오는 것에 해당합니다. `searchAroundLinkField`의 `LinkField` 부분은 실제로는 링크 타입의 필드 이름으로 바뀝니다. 이 예제는 `objA`에서 링크를 따라갔을 때 `objB`가 나오도록 고정합니다.

스텁 객체에 링크 상태를 설정하는 예제는 [온톨로지 편집 검증하기](03_unit-test-ontology-edits.md#verify-link-creation-to-an-object)를 참고하세요.

## 정리

- 스텁은 객체 집합 검색이나 집계 호출의 결과를 테스트에서 고정값으로 정하는 방법이며, `whenObjectSet(...).thenReturn(...)` 형태로 씁니다.
- 합계 같은 집계 결과, 정렬과 개수 제한이 붙은 검색 결과를 모두 스텁할 수 있습니다.
- 객체 배열로 시작하는 서로 다른 검색이나 `searchAround` 링크 탐색을 스텁할 때는 각 객체에 `rid`를 지정해야 합니다.
