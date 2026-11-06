# 객체 식별자 (Object identifiers)

- 원문: https://www.palantir.com/docs/foundry/functions/object-identifiers/
- 사이드바 위치: Define Ontologies > Functions > Functions on objects > Object identifiers

이 페이지는 TypeScript v1 함수에서 온톨로지 객체를 식별하는 여러 방법(RID, 기본 키, 객체 지정자)을 설명하고, 이것이 코드 작성에 어떤 영향을 주는지 다룹니다. 특히 같은 객체를 두 번 읽었을 때 `===` 비교가 `false`가 되는 이유와, 객체를 Map의 키로 쓸 때 주의할 점을 알려 줍니다.

이 페이지는 `typeId`와 `primaryKey`로 객체를 식별하는 TSv1을 다룹니다. TSv2의 필드와 각 필드의 대응 관계는 [객체 식별하기](../10_typescript-v2/03_typescript-v2-migration.md#identify-objects)를 참고하십시오.

Foundry에서 객체의 정체성(identity)은 몇 가지 다른 방식으로 표현되며, 이 표현들의 차이를 이해하는 것은 함수에서 올바른 코드를 작성하는 데 중요할 수 있습니다. 이 섹션에서는 객체를 식별하는 여러 방식과 그것이 코드에 미치는 영향을 설명합니다.

<a id="types-of-identifiers"></a>
## 식별자의 종류 (Types of identifiers)

<a id="object-rids"></a>
### 객체 RID (Object RIDs)

"RID"는 엔터티를 식별하는 데 쓰는 Palantir의 오픈 소스 명세인 [Resource Identifier ↗](https://github.com/palantir/resource-identifier)를 가리킵니다. 온톨로지 객체는 생성될 때 RID를 부여받으며, 생성은 백킹 데이터셋을 인덱싱하면서 일어나거나 액션의 일부로 일어납니다.

TypeScript v1 함수에서 모든 [온톨로지 객체](06_api-objects-links.md)에는 `string | undefined` 타입의 `rid` 필드가 있습니다. RID가 undefined일 수 있는 이유는 함수에서 [객체 생성](../12_typescript-v1/03_api-ontology-edits.md#creating-objects) API로 새 객체를 만들 수 있기 때문입니다. 새로 생성된 객체의 `rid` 값은 항상 `undefined`이고, 기존 객체에는 항상 `rid`가 정의되어 있습니다.

**설명**: Resource Identifier 명세에서 RID는 `ri.<service>.<instance>.<type>.<locator>`처럼 `ri` 접두어 뒤에 서비스, 인스턴스, 리소스 종류, 고유 값을 점으로 이어 붙인 형식의 문자열입니다. 함수 실행 중에 새로 만든 객체는 아직 플랫폼에 저장되지 않았으므로 RID가 발급되지 않았고, 그래서 `undefined`입니다. TypeScript의 `string | undefined`는 "문자열이거나 값이 없음"을 뜻하는 유니언 타입입니다.

<a id="primary-keys"></a>
### 기본 키 (Primary keys)

객체는 객체 타입과 기본 키(primary key)로도 유일하게 식별할 수 있습니다. 기본 키는 고유한 `propertyId`와 값의 쌍입니다. 예를 들어 Employee 객체 타입은 `employeeId`라는 `string` 속성으로 유일하게 식별될 수 있습니다.

모든 온톨로지 객체에는 새로 생성된 객체를 포함해 항상 `typeId`와 `primaryKey` 필드가 있습니다. 새 객체를 생성할 때 기본 키를 반드시 제공해야 하기 때문입니다.

<a id="object-specifiers"></a>
### 객체 지정자 (Object specifiers)

TypeScript v1에서 객체를 유일하게 식별하려면 `typeId`와 `primaryKey`가 모두 필요합니다. 객체 타입과 기본 키가 서로 다른 필드이기 때문입니다.

**설명**: 관계형 데이터베이스에서 기본 키는 테이블 하나 안에서만 유일합니다. `employee` 테이블과 `contractor` 테이블에 둘 다 `id = 'E100'`인 행이 있을 수 있듯이, Employee 객체와 Contractor 객체가 같은 기본 키 값을 가질 수 있습니다. 그래서 (테이블 이름, 기본 키 값)에 해당하는 (`typeId`, `primaryKey`) 쌍이 있어야 온톨로지 전체에서 객체 하나를 특정할 수 있습니다.

> **중간 요약**: 객체는 RID 또는 (객체 타입, 기본 키) 쌍으로 식별됩니다. 함수에서 새로 만든 객체는 RID가 `undefined`이지만 `typeId`와 `primaryKey`는 항상 있으므로, TSv1에서는 이 두 값을 함께 써서 객체를 식별합니다.

<a id="implications-for-code"></a>
## 코드에 미치는 영향 (Implications for code)

<a id="checking-for-equality"></a>
### 동일성 비교하기 (Checking for equality)

함수 안에서 각 온톨로지 객체는 [JavaScript 객체 ↗](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object)로 표현됩니다. 하나의 온톨로지 객체가 여러 개의 JavaScript 객체로 표현될 수 있습니다. 예를 들어 [객체 검색](07_api-object-sets.md)으로 같은 온톨로지 객체를 여러 번 불러오거나, 파라미터로 전달받은 객체를 객체 검색으로 한 번 더 불러올 때 이런 일이 생깁니다.

```typescript tab="TypeScript v1"
public myFunction(employee: Employee): void {
    const employee2 = Objects.search().employee()
        .filter(e => e.id.exactMatch(employee.id))
        .all()[0];
    console.log(employee == employee2); // false
    console.log(employee === employee2); // false
    console.log(employee.id === employee2.id); // true
}
```

위 예제에서 `employee`와 `employee2`는 개념상 같은 온톨로지 객체를 가리키지만, 두 변수가 서로 다른 JavaScript 객체를 참조하므로 `==`와 `===` 연산자로 비교하면 `false`가 반환됩니다. 단순히 `rid` 필드를 비교하는 것도 문제가 될 수 있는데, 새로 생성된 객체의 `rid`는 `undefined`이기 때문입니다.

**설명**: 입력으로 받은 `employee`와 같은 `id`를 가진 Employee를 검색해 `employee2`에 담은 뒤 세 가지 비교를 출력하는 코드입니다. JavaScript에서 객체끼리의 `==`, `===`는 내용이 아니라 참조(메모리상 같은 객체인지)를 비교합니다. Java에서 두 `String` 객체를 `==`로 비교하면 내용이 같아도 `false`가 나올 수 있고 `equals()`를 써야 하는 것과 같은 상황입니다. 반면 `employee.id === employee2.id`는 문자열 값끼리의 비교라서 `true`입니다.

따라서 두 온톨로지 객체가 같은지 비교하는 가장 좋은 방법은 `typeId`와 `primaryKey`를 비교하는 것입니다.

```typescript tab="TypeScript v1"
function isEqual(o1: OntologyObject, o2: OntologyObject) {
    return o1.typeId === o2.typeId
        && JSON.stringify(o1.primaryKey) == JSON.stringify(o2.primaryKey);
}
```

기본 키는 하나의 객체 타입 안에서만 유일하므로 두 값이 모두 필요합니다.

**설명**: `typeId`는 문자열이라 `===`로 바로 비교할 수 있습니다. `primaryKey`는 값이 객체 형태로 표현될 수 있으므로 `JSON.stringify`로 문자열로 바꾼 뒤 비교합니다. 이렇게 하면 서로 다른 JavaScript 객체라도 내용이 같으면 같은 문자열이 되어 비교가 성립합니다.

<a id="object-mappings"></a>
### 객체 매핑 (Object mappings)

객체에서 어떤 값으로의 매핑을 저장해 두면 유용한 경우가 많습니다. 예를 들어 객체 배열을 순회하면서 나중에 효율적으로 조회할 수 있도록 값을 저장하고 싶을 수 있습니다.

앞에서 설명한 동일성 비교 문제 때문에 온톨로지 객체 자체를 JavaScript Map의 키로 사용할 수는 없습니다. 대신 OntologyObject를 키로 지원하도록 특별히 설계된 [FunctionsMap](../04_types-reference.md#collection-types)을 사용할 수 있습니다.

**설명**: JavaScript의 `Map`은 객체 키를 참조로 구분합니다. 같은 Employee를 두 번 불러와 만든 두 JavaScript 객체로 `map.set(employee, 1)`, `map.get(employee2)`를 하면 `undefined`가 나옵니다. FunctionsMap은 온톨로지 객체를 키로 받을 때 이 문제를 처리하도록 만든 컬렉션 타입입니다.

> **중간 요약**: 같은 온톨로지 객체라도 여러 JavaScript 객체로 표현될 수 있으므로 `==`나 `===`로 비교하면 안 되고, `typeId`와 `primaryKey`를 함께 비교해야 합니다. 객체를 키로 하는 매핑에는 JavaScript Map 대신 FunctionsMap을 씁니다.

## 정리

- TSv1에서 객체는 RID 또는 `typeId`와 `primaryKey`의 쌍으로 식별됩니다.
- 함수에서 새로 만든 객체는 `rid`가 `undefined`이므로 RID 비교는 믿을 수 없습니다.
- 기본 키는 객체 타입 안에서만 유일하므로 `typeId`와 `primaryKey`를 함께 비교해야 합니다.
- 같은 객체를 여러 번 불러오면 서로 다른 JavaScript 객체가 되어 `===` 비교가 `false`가 됩니다.
- 객체를 키로 쓰는 매핑에는 JavaScript Map 대신 FunctionsMap을 사용합니다.
