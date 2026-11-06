# API: 객체와 링크 (Objects and links (TSv1))

- 원문: https://www.palantir.com/docs/foundry/functions/api-objects-links/
- 사이드바 위치: Define Ontologies > Functions > Functions on objects > Objects and links (TSv1)

이 페이지는 TypeScript v1(TSv1) 함수(function) 안에서 온톨로지의 객체, 속성(property), 링크를 코드로 다루는 API를 설명합니다. 온톨로지에 정의한 객체 타입이 TypeScript 인터페이스로 자동 생성되므로, 함수 작성자는 점 표기법으로 속성을 읽고 메서드 호출로 링크를 따라갈 수 있습니다. 배열 속성과 링크 결과가 읽기 전용인 이유, 링크 탐색 비용, 속성 타입 메타데이터도 함께 다룹니다.

이 페이지는 TSv1을 다룹니다. TSv2와 Python은 Ontology SDK를 통해 객체를 읽습니다. [언어별 객체 API](01_functions-on-objects.md#object-apis-by-language)를 보거나, TSv2의 탐색 API는 TypeScript OSDK 레퍼런스의 [Links](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#links)를 참고하세요.

프로젝트에 가져온 모든 [객체 타입](../../02_object-and-link-types/02_object-types/01_object-types-overview.md)은 TypeScript v1 API로 변환되므로, Foundry에서 사용할 수 있는 객체에 쉽게 접근하고 조작할 수 있습니다.

**설명**: "API로 변환된다"는 것은 코드 생성(code generation)을 뜻합니다. 예를 들어 온톨로지에 `Employee` 객체 타입이 있고 속성으로 `firstName`, `lastName`이 있으면, 함수 저장소에서 `import { Employee } from "@foundry/ontology-api"`로 불러올 수 있는 TypeScript 타입이 자동으로 만들어집니다. 함수 작성자는 이 타입 덕분에 편집기의 자동 완성과 컴파일러의 타입 검사를 받을 수 있습니다.

<a id="properties"></a>
### 속성 (Properties)

각 객체 타입의 [속성](../../02_object-and-link-types/03_properties/01_properties-overview.md)은 객체 타입마다 생성되는 TypeScript 인터페이스의 필드로 변환됩니다. 생성되는 필드 이름은 온톨로지에 지정된 API Name을 사용합니다.

각 속성의 필드에는 간단한 점 표기법으로 접근할 수 있습니다.

```typescript tab="TypeScript v1"
const firstName = employee.firstName;
```

**설명**: `employee`는 `Employee` 타입의 객체 하나(테이블의 행 하나에 해당)이고, `.firstName`은 그 행의 `firstName` 열 값을 읽는 것입니다.

속성에는 구체적인 값이 설정되어 있지 않을 수 있으므로, 속성 값에 접근할 때 반환 타입이 `undefined`일 수 있습니다. TypeScript에서는 `undefined` 경우를 명시적으로 처리하지 않으면 컴파일러가 오류를 냅니다. 자세한 내용은 [이 가이드](../12_typescript-v1/06_undefined-values.md)를 참고하세요.

**설명**: 데이터베이스에서 열 값이 NULL일 수 있는 것과 같은 상황입니다. 생성된 타입은 `firstName: string | undefined`처럼 정의되므로, `employee.firstName.length`처럼 바로 쓰면 컴파일 오류가 나고 `if (employee.firstName !== undefined)` 같은 검사를 먼저 해야 합니다.

<a id="array-properties"></a>
#### 배열 속성 (Array properties)

TypeScript v1에서 객체 타입의 배열 속성은 `ReadonlyArray` 타입으로 변환됩니다. 이렇게 하는 이유는 배열 속성을 [편집(edit)](../12_typescript-v1/03_api-ontology-edits.md)하는 의미를 분명히 하기 위해서입니다. 배열 속성의 값을 수정하는 유일한 방법은 완전히 새로운 배열 값으로 업데이트하는 것입니다.

이 때문에 배열 속성의 값을 조작하기 전에 먼저 복사해야 합니다.

```typescript tab="TypeScript v1"
// 새 배열로 복사
let arrayCopy = [...myObject.myArrayProperty];
// 이제 복사한 배열을 수정할 수 있습니다
arrayCopy.push(newItem);
```

**설명**: `[...배열]`은 전개 구문(spread syntax)으로 원본 배열의 원소를 담은 새 배열을 만듭니다. `ReadonlyArray`에는 `push` 같은 변경 메서드가 없으므로, 복사본을 만든 뒤 수정하고, 필요하면 그 복사본 전체를 속성에 다시 대입하는 방식으로 편집합니다.

TypeScript v2는 배열 속성을 `ReadonlyArray`가 아니라 일반 `T[]`로 타입을 지정하므로, 컴파일러가 제자리(in place) 수정을 허용합니다. 그래도 편집은 배열 값 전체를 교체하는 방식이므로, 어느 버전에서든 새 배열을 만들어 속성에 대입하세요. Python도 같은 방식으로 동작합니다. [온톨로지 편집(Ontology edits)](../11_python/05_python-ontology-edits.md)을 참고하세요.

> **중간 요약**: 객체 타입의 속성은 생성된 TypeScript 인터페이스의 필드가 되며 점 표기법으로 읽습니다. 값이 없을 수 있으므로 `undefined` 처리가 필요하고, 배열 속성은 읽기 전용이라 복사해서 수정한 뒤 새 배열 전체로 교체해야 합니다.

<a id="link-types"></a>
### 링크 타입 (Link types)

객체 타입 사이의 [링크 타입](../../02_object-and-link-types/06_link-types/01_link-types-overview.md)도 각 객체 타입의 TypeScript 인터페이스에서 최상위 필드로 변환됩니다. 링크를 따라가려면 그 필드에 접근한 다음 객체를 불러오는 메서드 중 하나를 호출합니다. 링크 타입 필드 이름은 온톨로지에 지정된 API Name으로 생성됩니다.

Foundry 온톨로지는 1대1, 1대다, 다대다 링크 타입 정의를 지원합니다. 링크의 `1` 쪽에 접근할 때 생성되는 필드는 `SingleLink` 타입이며, `get()` 또는 `getAsync()` 메서드로 링크된 객체에 접근할 수 있습니다.

```typescript tab="TypeScript v1"
const manager = employee.manager.get();
```

1대1 또는 다대1 링크를 따라갈 때 링크된 객체가 없으면 반환 값이 `undefined`일 수 있습니다. 이런 링크의 `undefined` 값 처리는 [가이드](../12_typescript-v1/06_undefined-values.md)를 따르세요.

링크의 `many` 쪽에 접근할 때 생성되는 필드는 `MultiLink` 타입입니다. `all()` 또는 `allAsync()` 메서드로 링크된 객체의 배열에 접근할 수 있습니다. 링크된 객체가 없으면 이 메서드들은 빈 배열을 반환합니다.

```typescript tab="TypeScript v1"
const employees = employee.reports.all();
```

**설명**: Employee 테이블에 `manager_id` 외래 키 열이 있다고 생각해 봅시다. 직원 한 명 입장에서 관리자는 최대 한 명이므로 `employee.manager`는 `SingleLink`이고 `get()`이 객체 하나(또는 `undefined`)를 돌려줍니다. 반대로 관리자 입장에서 부하 직원은 여러 명이므로 `employee.reports`는 `MultiLink`이고 `all()`이 배열을 돌려줍니다. SQL로 쓰면 `SELECT * FROM employee WHERE manager_id = :현재직원ID`의 결과에 해당합니다. `getAsync()`, `allAsync()`는 같은 일을 비동기(Promise 반환)로 수행하는 버전입니다.

링크를 따라가는 작업은 백엔드에서 어떤 객체가 링크되어 있는지 불러와야 하므로 비용이 클 수 있습니다. 링크 탐색을 더 효율적으로 수행하는 방법은 [이 섹션](../08_function-consumption/03_optimize-performance.md#optimizing-link-traversals)을 참고하세요.

`.all()` 또는 `.allAsync()` 호출로 반환되는 링크된 객체 배열은 `ReadonlyArray`입니다. 이 배열을 수정하려면 먼저 복사하세요.

```typescript tab="TypeScript v1"
let copiedEmployees = [...employee.reports.all()];
```

링크된 객체 인스턴스를 메모리에 불러오지 않으려면 링크를 `ObjectSet`으로 따라갈 수 있습니다. 온톨로지에 링크가 만들어지면, 해당 타입의 객체 집합(object set)에 다른 링크된 객체 집합으로 "검색해 넘어가는(search around)" API가 생성됩니다.

```typescript tab="TypeScript v1"
import { ObjectSet, Employee, OtherObjectType } from "@foundry/ontology-api";

// 다음과 같은 객체 집합이 있다고 가정합니다:
// const employee_id = "123";
// const employeeObjectSet : ObjectSet<Employee> = Objects.search().employee().filter(exactMatch(employee_id));

const linkedObjs: ObjectSet<OtherObjectType> = employeeObjectSet.searchAroundToOtherObjectType();
```

**설명**: `MultiLink`의 `all()`은 링크된 객체를 실제로 모두 메모리로 가져오지만, `ObjectSet`은 "어떤 객체들인지"에 대한 질의 정의만 들고 있다가 필요할 때 서버에서 계산됩니다. SQL 관점에서 보면, `all()`은 조인 결과를 클라이언트로 모두 내려받는 것이고, `searchAroundTo...()`는 `SELECT ... FROM other JOIN employee ...` 질의문을 조립만 해 두는 것입니다. 링크된 객체가 수천 개일 때 차이가 커집니다.

객체 인스턴스 하나에서 출발해 검색해 넘어가면 `MultiLink<objectType>`을 얻습니다. 이 `MultiLink`는 `ObjectSet`으로 변환할 수 없습니다. 다른 객체 집합으로 넘어가려면 객체 인스턴스를 객체 집합으로 변환해야 합니다.

```typescript tab="TypeScript v1"
// 다음을 가정합니다:
// const employee: Employee

// MultiLink는 메모리에 불러와 추가로 처리할 수 있습니다.

const linkedObjs: MultiLink<objectType> = employee.reports

// 단일 객체 인스턴스를 객체 집합으로 변환합니다. 이 문장은 `employee().filter()` 문장보다 오래 걸립니다.
const employeeObjectSet : ObjectSet<Employee> = Objects.search().employee([employee])

// 그다음부터는 위의 "searchAroundToOtherObjectType"을 사용해 객체 집합만으로 처리할 수 있습니다.
```

**설명**: 핵심 줄은 `Objects.search().employee([employee])`입니다. 이미 메모리에 있는 객체 인스턴스 배열을 넘겨 그 객체들로 이루어진 `ObjectSet`을 만들고, 이후에는 search around API를 연결해 쓸 수 있습니다. 주석대로 처음부터 필터로 객체 집합을 만드는 것보다 느립니다.

TSv2 형태는 TypeScript OSDK 레퍼런스의 [Links](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#links)와, 메서드별 변환을 정리한 [링크 탐색 매핑(link traversal mapping)](../10_typescript-v2/03_typescript-v2-migration.md#link-traversal-mapping)을 참고하세요. 각 TSv1 식별자와 타입에 대응하는 TSv2 항목은 [식별자 레퍼런스(identifier reference)](../10_typescript-v2/03_typescript-v2-migration.md#identifier-reference)를 확인하세요.

> **중간 요약**: 링크 타입은 인터페이스의 필드가 되며, `1` 쪽은 `SingleLink`(`get()`), `many` 쪽은 `MultiLink`(`all()`)로 접근합니다. 링크 탐색은 비용이 크므로, 객체를 메모리에 올리지 않고 `ObjectSet`의 search around API로 탐색하는 방법이 있으며, 단일 객체에서 시작할 때는 먼저 객체 집합으로 변환해야 합니다.

<a id="ontology-metadata"></a>
### 온톨로지 메타데이터 (Ontology metadata)

Functions는 객체와 속성 목록을 제공하여 사용 가능한 온톨로지에 접근할 수 있게 합니다. 온톨로지 메타데이터 정보는 각 객체 타입의 상수 타입에 접근하여 얻을 수 있습니다. 자세한 내용은 아래 섹션을 참고하세요.

**주의**: 이 온톨로지 메타데이터 API는 TSv1 전용이며, TSv2나 Python에는 대응하는 기능이 없습니다.

<a id="object-property-metadata"></a>
#### 객체 속성 메타데이터 (Object property metadata)

객체 속성에는 타입 메타데이터도 포함되어 있어 각 속성의 타입에 프로그래밍 방식으로 접근할 수 있습니다. 이 기능은 특정 타입의 속성을 모두 찾아내거나, 주어진 속성 이름이 특정 타입인지 검증하는 등의 고급 워크플로에 사용할 수 있습니다.

예를 들어 employee 객체 **타입**이 있는 온톨로지에서는 그 객체 **타입의** 속성에 대한 타입 정보에 다음과 같이 접근할 수 있습니다.

```typescript tab="TypeScript v1"
import { Employee } from "@foundry/ontology-api";
...
const type = Employee.properties.firstName;
```

이 경우 `firstName`이 `Employee` 객체 타입의 문자열 속성이라면, 그 타입은 `StringPropertyBaseType`이 됩니다.

**설명**: 앞의 `employee.firstName`은 객체 인스턴스 하나의 값(예: "Alice")을 읽는 것이고, 여기의 `Employee.properties.firstName`은 객체 타입(클래스) 수준에서 "이 속성의 타입이 무엇인가"라는 스키마 정보를 읽는 것입니다. 데이터베이스로 치면 행의 값을 조회하는 것과 `information_schema.columns`에서 열의 데이터 타입을 조회하는 것의 차이입니다.

사용할 수 있는 속성 타입은 다음과 같습니다.

* `BooleanPropertyBaseType`
* `BytePropertyBaseType`
* `DatePropertyBaseType`
* `FloatPropertyBaseType`
* `TimestampPropertyBaseType`
* `ShortPropertyBaseType`
* `GeohashPropertyBaseType` (`geopoint` 속성에 사용합니다. 이전에는 `geohash` 속성이라고 불렀습니다.)
* `DecimalPropertyBaseType`
* `StringPropertyBaseType`
* `LongPropertyBaseType`
* `IntegerPropertyBaseType`
* `DoublePropertyBaseType`
* `ArrayPropertyBaseType`
* `VectorPropertyBaseType`

> **중간 요약**: TSv1에서는 `Employee.properties.firstName`처럼 객체 타입의 상수를 통해 각 속성의 타입 정보를 코드에서 조회할 수 있으며, 결과는 `StringPropertyBaseType` 같은 속성 기본 타입 중 하나입니다. 이 기능은 TSv1 전용입니다.

## 정리

- TSv1에서는 온톨로지의 객체 타입이 TypeScript 인터페이스로 자동 생성되고, 속성은 API Name을 이름으로 하는 필드가 됩니다.
- 속성 값은 `undefined`일 수 있으므로 명시적으로 처리해야 하며, 배열 속성과 `all()` 결과는 `ReadonlyArray`이므로 복사해서 다룹니다.
- 링크는 `SingleLink`(`get()`/`getAsync()`)와 `MultiLink`(`all()`/`allAsync()`)로 탐색하며, 비용을 줄이려면 `ObjectSet`의 search around API를 사용합니다.
- 속성 타입 메타데이터 API(`Employee.properties.xxx`)는 TSv1 전용입니다.
- TSv2와 Python은 Ontology SDK를 통해 객체를 다루므로 별도 문서를 참고합니다.
