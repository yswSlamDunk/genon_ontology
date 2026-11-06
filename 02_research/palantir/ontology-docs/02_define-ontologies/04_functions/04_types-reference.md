# 타입 레퍼런스 (Types reference)

- 원문: https://www.palantir.com/docs/foundry/functions/types-reference/
- 사이드바 위치: Define Ontologies > Functions > Types reference

함수(function)를 함수 레지스트리(function registry)에 등록해 다른 애플리케이션에서 호출하려면, 입력 파라미터와 반환값의 타입을 Foundry가 이해하는 타입으로 명시해야 합니다. 이 페이지는 함수 레지스트리가 지원하는 모든 타입과, 각 타입이 TypeScript v1, TypeScript v2, Python에서 어떤 언어 타입에 대응하는지 정리한 레퍼런스입니다. 스칼라, 컬렉션, 집계, 온톨로지, 미디어, 사용자/그룹, 지오메트리 타입을 차례로 다룹니다.

**코드 예제 안내**: 원문은 거의 모든 타입마다 TypeScript v1, TypeScript v2, Python 세 가지 버전의 예제를 나란히 제공합니다. 이 번역에서는 지침에 따라 섹션마다 대표 예제 하나만 남기고, 언어별 차이가 중요한 경우에만 본문에서 그 차이를 설명합니다.

함수 레지스트리에 게시(publish)되려면 TypeScript 함수는 모든 입력 파라미터에 명시적인 타입 주석(type annotation)을 달고, 명시적인 반환 타입을 지정해야 합니다. 아래는 현재 지원되는 함수 레지스트리 타입과 그에 대응하는 언어 타입의 전체 목록입니다.

**참고**: Pipeline Builder에서 Python 함수를 사용자 정의 함수(UDF, user-defined function)로 쓰고 있나요? 아래의 스칼라 타입(`str`, `int` 등)은 UDF가 반환하는 값입니다. 함수가 행마다 한 번씩 실행되고 그 반환값이 새 열이 되기 때문입니다. DataFrame을 반환하지 않습니다. 자세한 내용은 [Pipeline Builder에서 Python 함수가 데이터를 처리하는 방식](11_python/07_python-functions-builder.md#how-python-functions-process-data)을 참고하세요.

**설명**: 함수 레지스트리는 Foundry 안의 함수 목록과 각 함수의 시그니처(이름, 파라미터 타입, 반환 타입)를 저장해 두는 곳입니다. Workshop이나 액션이 함수를 호출하려면 "이 함수는 정수 두 개를 받아 정수 하나를 돌려준다" 같은 정보를 미리 알아야 하므로, 언어 고유 타입이 아니라 아래 표의 "함수 레지스트리 타입"으로 시그니처를 기록합니다. 같은 레지스트리 타입이 언어마다 다른 이름으로 표현되기 때문에 아래 대응표가 필요합니다. UDF 참고 사항은 SQL의 스칼라 함수와 같은 구조입니다. `SELECT upper(name) FROM t`에서 `upper`가 행마다 값 하나를 돌려주듯, Pipeline Builder의 Python UDF도 행마다 값 하나를 돌려주고 그 값들이 새 열이 됩니다.

| 함수 레지스트리 타입 | TypeScript v1 타입 | TypeScript v2 타입 | Python 타입 | |
|---|---|---|---|---|
| Attachment | `Attachment` | `Attachment` | `Attachment` | [예제](#attachment) |
| Boolean | `boolean` | `boolean` | `bool` | [예제](#boolean) |
| Binary | 지원 안 됨 | 지원 안 됨 | `bytes` | [예제](#binary) |
| Byte | 지원 안 됨 | 지원 안 됨 | `int*` | [예제](#byte) |
| Classification marking | `ClassificationMarking` | `ClassificationMarking` | `ClassificationMarking` | [예제](#classification-marking) |
| Date | `LocalDate` | `DateISOString` | `datetime.date` | [예제](#date) |
| Decimal | 지원 안 됨 | 지원 안 됨 | `decimal.Decimal` | [예제](#decimal) |
| Double | `Double` | `Double` | `float*` | [예제](#double) |
| Float | `Float` | `Float` | `float` | [예제](#float) |
| GeoPoint | `GeoPoint` | `Point` | `GeoPoint` | [예제](#geopoint) |
| GeoShape | `GeoShape` | `Geometry` | `GeoShape` | [예제](#geoshape) |
| Group | `Group` | `GroupId` | `GroupId` | [예제](#group) |
| Integer | `Integer` | `Integer` | `int` | [예제](#integer) |
| Interface | 지원 안 됨 | `Osdk.Instance<MyInterface>` | 지원 안 됨 | [예제](#interface) |
| Interface object set | 지원 안 됨 | `ObjectSet<MyInterface>` | 지원 안 됨 | [예제](#interface-object-set) |
| List | `T[]` 또는 `Array<T>` | `T[]` 또는 `Array<T>` | `list[T]` | [예제](#list) |
| Long | `Long` | `Long` | `int*` | [예제](#long) |
| Mandatory marking | `MandatoryMarking` | `MandatoryMarking` | `MandatoryMarking` | [예제](#mandatory-marking) |
| Map | `FunctionsMap<K, V>` | `Record<K, V>` | `dict[K, V]` | [예제](#map) |
| Media reference | `MediaItem` | `Media` | `Media` | [예제](#media) |
| Notification | `Notification` | `Notification` | `Notification` | [예제](#notification) |
| Object | `MyObjectType` | `Osdk.Instance<MyObjectType>` | `MyObjectType` | [예제](#object) |
| Object set | `ObjectSet<MyObjectType>` | `ObjectSet<MyObjectType>` | `MyObjectTypeObjectSet` | [예제](#object-set) |
| Ontology edit | `void` | `Edits` | `OntologyEdit` | [예제](#ontology-edit) |
| Optional | `T \| undefined` | `T \| undefined` | `typing.Optional` 또는 `T \| None` | [예제](#optional) |
| Principal | `Principal` | `Principal` | `Principal` | [예제](#principal) |
| Range | `IRange<T>` | `Range<T>` | `Range[T]` | [예제](#range) |
| Set | `Set<T>` | 지원 안 됨 | `set[T]` | [예제](#set) |
| Short | 지원 안 됨 | 지원 안 됨 | `int*` | [예제](#short) |
| String | `string` | `string` | `str` | [예제](#string) |
| Struct/custom type | `interface` | `interface` | `dataclasses.dataclass` | [예제](#structcustom-type) |
| Timestamp | `Timestamp` | `TimestampISOString` | `datetime.datetime` | [예제](#timestamp) |
| Two-dimensional aggregation | `TwoDimensionalAggregation<K, V>` | `TwoDimensionalAggregation<K, V>` | `TwoDimensionalAggregation[K, V]` | [예제](#two-dimensional-aggregation) |
| Three-dimensional aggregation | `ThreeDimensionalAggregation<K, S, V>` | `ThreeDimensionalAggregation<K, S, V>` | `ThreeDimensionalAggregation[K, S, V]` | [예제](#three-dimensional-aggregation) |
| User | `User` | `UserId` | `UserId` | [예제](#user) |

**팁**: `Integer`와 `Long`은 모두 Python 타입 `int`에 대응하지만, 함수 시그니처에 `int`로 직접 표시한 필드는 `Integer` 타입으로 등록됩니다. 따라서 숫자 데이터 타입을 등록할 때는 API의 `Integer` 또는 `Long` 타입을 사용할 것을 권장합니다. `Float`와 `Double`에도 비슷한 지침이 적용됩니다. 함수 시그니처에 Python 타입 `float`를 직접 쓰면 기본적으로 `Float`로 등록됩니다.

**설명**: 표에서 `int*`, `float*`처럼 별표가 붙은 항목이 이 팁에 해당합니다. Python의 `int`는 크기 제한이 없는 정수 하나뿐이지만, 레지스트리에는 Short(16비트), Integer(32비트), Long, Byte처럼 범위가 다른 정수 타입이 여럿 있습니다. 시그니처에 그냥 `int`라고 쓰면 그중 `Integer`로 등록되므로, 32비트 범위를 넘는 값을 다루려면 `from functions.api import Long`으로 가져와 `Long`이라고 명시해야 합니다. `float`도 마찬가지로 기본값은 32비트 `Float`이므로, 64비트 정밀도가 필요하면 `Double`을 명시합니다.

> **중간 요약**: 함수 레지스트리에 등록하려면 모든 파라미터와 반환값의 타입을 명시해야 하며, 표는 레지스트리 타입과 각 언어 타입의 대응을 보여 줍니다. Python에서 `int`와 `float`를 그대로 쓰면 `Integer`와 `Float`로 등록되므로, 다른 숫자 타입이 필요하면 API 타입을 명시합니다.

<a id="scalar-types"></a>
## 스칼라 타입 (Scalar types)

스칼라 타입은 단일 값을 나타내며, 주로 텍스트, 숫자, 시간 데이터를 담는 데 쓰입니다.

JavaScript와 TypeScript에는 정수와 부동소수점 값을 모두 나타내는 데 흔히 쓰이는 `number` 타입 하나만 있습니다. 더 나은 타입 검증과 구조를 제공하기 위해, TypeScript v1 함수에서는 `@foundry/functions-api` 패키지가, TypeScript v2 함수에서는 `@osdk/functions` 패키지가 내보내는(export) 숫자 별칭(alias)만 지원합니다. 마찬가지로 Python 함수에서 숫자 타입을 다룰 때는 `functions.api` 모듈이 내보내는 타입 별칭을 사용할 것을 권장합니다.

**설명**: 타입 별칭은 기존 타입에 새 이름을 붙인 것입니다. 예를 들어 `type Integer = number`라고 정의하면 실행 시점에는 둘 다 같은 `number`이지만, 시그니처에 `Integer`라고 쓰면 레지스트리는 "32비트 정수"로, `Double`이라고 쓰면 "64비트 부동소수점"으로 등록할 수 있습니다. 즉 별칭은 실행 동작을 바꾸지 않고 "이 값이 어떤 종류의 숫자인지"라는 정보를 레지스트리에 전달하는 역할을 합니다.

<a id="boolean"></a>
### Boolean

```typescript
// TypeScript v2
import { Integer } from "@osdk/functions";

function isEven(num: Integer): boolean {
    return num % 2 === 0;
}

export default isEven;
```

(원문에는 TypeScript v1과 Python 버전의 예제도 있습니다.)

**설명**: 정수 하나를 받아 짝수인지 여부를 `boolean`(Python에서는 `bool`)으로 반환합니다. TypeScript v2에서는 함수를 일반 함수로 작성하고 `export default`로 내보내는 반면, TypeScript v1에서는 클래스 안의 메서드에 `@Function()` 데코레이터를 붙이고, Python에서는 함수에 `@function` 데코레이터를 붙여 등록합니다. 이 세 가지 등록 방식의 차이는 이 페이지의 모든 예제에 공통입니다.

<a id="string"></a>
### String

```python
# Python
from functions.api import function

@function
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

(원문에는 TypeScript v1과 v2 버전의 예제도 있습니다.)

**설명**: 문자열 `name`을 받아 `"Hello, {name}!"` 형태의 문자열을 반환합니다. 입력이 `"Kim"`이면 출력은 `"Hello, Kim!"`입니다.

<a id="short"></a>
### Short

-32,768부터 32,767까지의 정수 값을 나타냅니다.

Python 함수에서 `Short` 타입은 내장 `int` 타입의 별칭입니다.

```python
# Python
from functions.api import function, Short

@function
def increment(num: Short) -> Short:
    return num + 1
```

**설명**: Short는 16비트 부호 있는 정수(-2<sup>15</sup>부터 2<sup>15</sup> - 1)입니다. 표에서 보듯 TypeScript에서는 지원되지 않고 Python에서만 쓸 수 있습니다.

<a id="integer"></a>
### Integer

(-2<sup>31</sup>)부터 (2<sup>31</sup> - 1)까지의 정수 값을 나타냅니다.

* TypeScript v1과 v2 함수 모두에서 `Integer` 타입은 내장 `number` 타입의 별칭입니다.
* Python 함수에서 `Integer` 타입은 내장 `int` 타입의 별칭입니다.

```typescript
// TypeScript v1
import { Function, Integer } from "@foundry/functions-api";

export class MyFunctions {
    @Function()
    public sum(a: Integer, b: Integer): Integer {
        return a + b;
    }
}
```

(원문에는 TypeScript v2와 Python 버전의 예제도 있습니다.)

**설명**: TypeScript v1 방식의 등록 구조를 보여 주는 예제입니다. `MyFunctions` 클래스를 내보내고, 그 안의 `sum` 메서드에 `@Function()` 데코레이터를 붙여 함수로 등록합니다. 두 정수를 받아 합을 반환합니다.

<a id="long"></a>
### Long

-(2<sup>53</sup> - 1)부터 (2<sup>53</sup> - 1)까지의 정수 값을 나타냅니다. 이 범위는 함수를 브라우저 환경에서 호출할 때 정밀도 손실을 막기 위해 JavaScript의 `Number.MIN_SAFE_INTEGER`와 `Number.MAX_SAFE_INTEGER`와 같게 정해져 있습니다.

* TypeScript v1 함수에서 `Long` 타입은 내장 `number` 타입의 별칭입니다. TypeScript v2 함수에서 `Long` 타입은 내장 `string` 타입의 별칭입니다.
* Python 함수에서 `Long` 타입은 내장 `int` 타입의 별칭입니다.

```typescript
// TypeScript v2
import { Long } from "@osdk/functions";

function subtract(a: Long, b: Long): string {
    return (BigInt(a) - BigInt(b)).toString();
}

export default subtract;
```

(원문에는 TypeScript v1과 Python 버전의 예제도 있습니다.)

**설명**: JavaScript의 `number`는 64비트 부동소수점(IEEE 754 double)이라 정수를 정확히 표현할 수 있는 범위가 2<sup>53</sup> - 1까지입니다. 그보다 큰 정수는 가까운 값으로 반올림되어 값이 틀어집니다. 그래서 Long의 범위를 2<sup>53</sup> - 1로 제한한 것입니다. TypeScript v2에서는 `Long`이 `string`의 별칭이므로 값이 `"9007199254740991"` 같은 문자열로 들어옵니다. 예제는 두 문자열을 `BigInt`(임의 정밀도 정수)로 바꿔 뺄셈한 뒤 다시 문자열로 반환해, 계산 중 정밀도 손실을 피합니다.

<a id="float"></a>
### Float

32비트 부동소수점 수를 나타냅니다.

* TypeScript v1과 v2 함수 모두에서 `Float` 타입은 내장 `number` 타입의 별칭입니다.
* Python 함수에서 `Float` 타입은 내장 `float` 타입의 별칭입니다.

(원문에는 두 `Float` 값을 곱해 반환하는 `multiply` 예제가 세 언어로 있습니다.)

<a id="double"></a>
### Double

64비트 부동소수점 수를 나타냅니다.

* TypeScript v1과 v2 함수 모두에서 `Double` 타입은 내장 `number` 타입의 별칭입니다.
* Python 함수에서 `Double` 타입은 내장 `float` 타입의 별칭입니다.

```python
# Python
from functions.api import function, Double

@function
def divide(a: Double, b: Double) -> Double:
    return a / b
```

(원문에는 TypeScript v1과 v2 버전의 예제도 있습니다.)

**설명**: 두 `Double` 값을 받아 나눈 결과를 반환합니다. Float(32비트)는 유효 숫자가 약 7자리, Double(64비트)은 약 15\~16자리입니다. 예를 들어 금액이나 좌표처럼 정밀도가 중요한 값은 Double을 씁니다.

<a id="decimal"></a>
### Decimal

```python
# Python
from decimal import Decimal
from functions.api import function

@function
def return_pi() -> Decimal:
    return Decimal('3.1415926535')
```

**설명**: Decimal은 Python에서만 지원됩니다. 부동소수점은 0.1 같은 십진 소수를 이진수로 정확히 표현하지 못해 `0.1 + 0.2`가 `0.30000000000000004`가 되는 오차가 생기지만, `decimal.Decimal`은 십진수를 그대로 저장하므로 이런 오차가 없습니다. 예제는 문자열 `'3.1415926535'`로 Decimal을 만들어 반환합니다(float로 만들면 그 시점에 이미 오차가 들어가므로 문자열로 만드는 것이 일반적입니다).

<a id="date"></a>
### Date

달력의 날짜를 나타냅니다.

```typescript
// TypeScript v2
import { DateISOString } from "@osdk/functions";

function returnDate(): DateISOString {
    return "1999-10-17";
}

export default returnDate;
```

(원문에는 TypeScript v1과 Python 버전의 예제도 있습니다.)

**설명**: 날짜 표현 방식이 언어 버전마다 다릅니다. TypeScript v2의 `DateISOString`은 `"1999-10-17"` 같은 ISO 8601 형식 문자열이고, TypeScript v1은 `LocalDate.fromISOString("1999-10-17")`로 만든 `LocalDate` 객체, Python은 `date.fromisoformat('1999-10-17')`로 만든 `datetime.date` 객체를 씁니다. Date에는 시각과 시간대가 없습니다.

<a id="timestamp"></a>
### Timestamp

시간상의 한 시점(instant)을 나타냅니다.

```python
# Python
from datetime import datetime
from functions.api import function, Timestamp

@function
def get_current_timestamp() -> Timestamp:
    return datetime.now()
```

(원문에는 TypeScript v1과 v2 버전의 예제도 있습니다. TypeScript v1은 `Timestamp.now()`를, TypeScript v2는 `new Date().toISOString()`으로 만든 ISO 문자열(`TimestampISOString`)을 반환합니다.)

**설명**: 현재 시각을 반환합니다. Date가 "1999년 10월 17일"이라는 날짜라면, Timestamp는 "1999-10-17T09:30:00Z"처럼 특정 순간을 가리킵니다.

<a id="binary"></a>
### Binary

Python 함수에서 `Binary` 타입은 내장 `bytes` 타입의 별칭입니다.

```python
# Python
from functions.api import function

@function
def encode_utf8(param: str) -> bytes:
    return param.encode('utf-8')
```

**설명**: 문자열을 UTF-8로 인코딩한 바이트열을 반환합니다. 예를 들어 `"A가"`는 `b'A\xea\xb0\x80'`(4바이트)가 됩니다. Python에서만 지원됩니다.

<a id="byte"></a>
### Byte

Python 함수에서 `Byte` 타입은 내장 `int` 타입의 별칭입니다.

(원문에는 문자열을 UTF-8로 인코딩한 뒤 첫 번째 바이트를 `Byte`로 반환하고, 빈 문자열이면 예외를 발생시키는 Python 예제가 있습니다.)

**설명**: Byte는 8비트 정수 하나입니다. Python에서 `bytes` 객체의 원소 하나를 꺼내면(`b'A'[0]`) `65` 같은 `int`가 나오기 때문에 `int`의 별칭으로 정의됩니다.

<a id="mandatory-marking"></a>
### 필수 마킹 (Mandatory marking)

마킹(marking)은 데이터에 접근하려면 사용자가 특정 마킹을 가지고 있어야 하도록 요구해 접근을 제한하는 필수 통제(mandatory control)입니다.

```typescript
// TypeScript v1
import { OntologyEditFunction, MandatoryMarking } from "@foundry/functions-api";
import { Employee, Objects } from "@foundry/ontology-api";

export class MyFunctions {
    @Edits(Employee)
    @OntologyEditFunction()
    public async editMandatoryMarkings(markings: MandatoryMarking[]): Promise<void> {
        const employeeOne = Objects.search().employee().filter(e => e.id.exactMatch(1)).all()[0];
        employeeOne.markingsProperty = markings;
    }
}
```

(원문에는 TypeScript v2와 Python 버전의 예제도 있습니다. Python 예제에는 `editable_employee.markings_property = [Marking(m) for m in markings]`처럼 `Marking`으로 감싸서 대입하며, `list[MandatoryMarking]`을 그대로 대입해도 동작하지만 LSP 경고가 난다는 주석이 있습니다.)

**설명**: 마킹 목록을 받아 `id`가 1인 `Employee` 객체를 찾고, 그 객체의 마킹 속성(`markingsProperty`)을 받은 마킹으로 바꾸는 편집 함수입니다. `@Edits(Employee)`는 이 함수가 `Employee` 객체를 편집한다고 선언하고, `@OntologyEditFunction()`은 이 함수를 온톨로지 편집 함수로 등록합니다. "필수 통제"란 일반 권한(역할 기반)과 별개로 반드시 충족해야 하는 조건이라는 뜻입니다. 예를 들어 어떤 데이터에 "PII" 마킹이 붙어 있으면, 프로젝트 편집 권한이 있어도 PII 마킹을 부여받지 않은 사용자는 그 데이터를 볼 수 없습니다.

<a id="classification-marking"></a>
### 분류 마킹 (Classification marking)

분류 기반 접근 통제(CBAC, Classification-based access controls)는 민감한 정부 정보를 보호하는 데 쓰이는 필수 통제입니다. 정보에 접근하려면 사용자가 특정 분류 마킹을 가지고 있어야 하도록 요구해 접근을 제한합니다.

(원문에는 위 필수 마킹 예제와 같은 구조로, `ClassificationMarking[]`을 받아 `Employee` 객체의 마킹 속성을 바꾸는 예제가 세 언어로 있습니다.)

**설명**: 분류 마킹은 "기밀", "비밀" 같은 정부 보안 등급 체계에 쓰이는 마킹입니다. 함수에서 다루는 방법은 필수 마킹과 같고, 타입 이름만 `ClassificationMarking`으로 다릅니다.

> **중간 요약**: 스칼라 타입은 단일 값(불리언, 문자열, 정수, 실수, 날짜, 시각, 바이트, 마킹)을 나타냅니다. 숫자는 `number`나 `int` 대신 Integer, Long, Float, Double 같은 별칭으로 종류를 명시하며, Long은 정밀도 손실을 막기 위해 2<sup>53</sup> - 1로 제한되고 TypeScript v2에서는 문자열로 전달됩니다. Short, Byte, Binary, Decimal은 Python에서만 지원됩니다.

<a id="collection-types"></a>
## 컬렉션 타입 (Collection types)

컬렉션 타입은 다른 타입으로 매개변수화(parameterized)됩니다. 예를 들어 Array\[String]은 문자열의 리스트이고, Map\[String, Integer]는 문자열 키와 정수 값을 가진 딕셔너리입니다. 매개변수 타입은 반드시 지정해야 하며, 그 타입도 지원되는 타입이어야 합니다. Map의 키로는 스칼라 타입이나 온톨로지 객체 타입만 쓸 수 있습니다.

**설명**: 매개변수화는 Java나 TypeScript의 제네릭(generic)과 같은 개념입니다. `List`만으로는 등록할 수 없고 `List<Integer>`처럼 원소 타입까지 정해야 레지스트리가 시그니처를 기록할 수 있습니다. `any[]`나 원소 타입이 섞인 리스트는 허용되지 않는다는 뜻입니다.

<a id="list"></a>
### List

```typescript
// TypeScript v2
import { Integer } from "@osdk/functions";

function filterForEvenIntegers(nums: Integer[]): Integer[] {
    return nums.filter(num => num % 2 === 0);
}

export default filterForEvenIntegers;
```

(원문에는 TypeScript v1과 Python 버전의 예제도 있습니다.)

**설명**: 정수 배열을 받아 짝수만 남긴 배열을 반환합니다. 입력이 `[1, 2, 3, 4]`이면 출력은 `[2, 4]`입니다.

<a id="map"></a>
### Map

Map은 주로 스칼라 타입을 키로 삼아, 다른 어떤 함수 레지스트리 타입이든 될 수 있는 연관 값에 접근하는 데 쓰입니다.

```python
# Python
from functions.api import function

@function
def get_map() -> dict[str, str]:
    my_map = {}

    my_map["Name"] = "Phil"
    my_map["Favorite Color"] = "Blue"

    return my_map
```

(원문에는 TypeScript v1과 v2 버전의 예제도 있습니다. TypeScript v1은 `new FunctionsMap<string, string>()`을 만들어 `set`으로 값을 넣고, TypeScript v2는 일반 객체 `Record<string, string>`에 대입합니다.)

**설명**: 키 `"Name"`, `"Favorite Color"`에 각각 `"Phil"`, `"Blue"`를 담은 딕셔너리를 반환합니다. 같은 Map이 언어마다 다른 타입(`FunctionsMap`, `Record`, `dict`)으로 표현된다는 점이 핵심입니다.

추가로, Map은 온톨로지 객체를 키로 쓰는 것도 지원합니다.

```typescript
// TypeScript v2
import { ObjectSpecifier, Osdk } from "@osdk/client";
import { Integer } from "@osdk/functions";
import { Airplane } from "@ontology/sdk";

function getObjectMap(aircraft: Osdk.Instance<Airplane>[]): Record<ObjectSpecifier<Airplane>, Integer | undefined> {
    const myMap: Record<ObjectSpecifier<Airplane>, Integer | undefined> = {};

    aircraft.forEach(obj => {
        myMap[obj.$objectSpecifier] = obj.capacity;
    });

    return myMap;
}

export default getObjectMap;
```

(원문에는 TypeScript v1과 Python 버전의 예제도 있습니다. 두 버전은 `Airplane` 객체 자체를 키로 씁니다.)

**설명**: `Airplane` 객체 배열을 받아 "비행기 객체에서 그 비행기의 좌석 수(`capacity`)로" 가는 Map을 만듭니다. TypeScript v2에서는 JavaScript 객체의 키가 문자열이어야 하므로 객체 자체 대신 객체를 식별하는 문자열인 `$objectSpecifier`를 키로 씁니다. 값 타입이 `Integer | undefined`인 이유는 `capacity` 속성이 비어 있는 비행기가 있을 수 있기 때문입니다.

<a id="set"></a>
### Set

(원문에는 정수 `Set`을 받아 원소 개수를 반환하는 `getSizeOfSet` 예제가 TypeScript v1과 Python으로 있습니다. 표에서 보듯 TypeScript v2는 Set을 지원하지 않습니다.)

**설명**: Set은 중복 없는 원소의 모음입니다. 예를 들어 `{1, 2, 2, 3}`을 Set으로 만들면 `{1, 2, 3}`이 되고 크기는 3입니다.

<a id="optional"></a>
### Optional

* TypeScript 함수에서 선택적 파라미터는 `varName?: T` 또는 `varName: T | undefined`로 선언합니다. 예를 들어 `value`라는 선택적 정수 파라미터를 가진 함수는 `value?: Integer` 또는 `value: Integer | undefined`로 선언할 수 있습니다. TypeScript 함수는 `T | undefined` 타입을 지정해 선택적 반환 타입도 선언할 수 있습니다. 예를 들어 `Integer`를 반환하거나 아무 값도 반환하지 않을 수 있는 함수의 반환 타입은 `Integer | undefined`입니다.
* Python 함수에서 선택적 파라미터와 반환값은 `typing.Optional[T]` 또는 `T | None`으로 선언할 수 있습니다. `T | None` 문법은 Python 3.10 이상이 필요합니다.
* TypeScript와 Python 함수 모두에서 매개변수 타입 `T`는 반드시 지정해야 하며, 지원되는 다른 타입이어야 합니다.

```typescript
// TypeScript v2
function greet(name?: string): string | undefined {
    if (name === undefined) {
        return undefined;
    }
    return `Hello, ${name}!`;
}

export default greet;
```

(원문에는 TypeScript v1과 Python 버전의 예제도 있습니다.)

**설명**: `name`이 주어지지 않으면 `undefined`를, 주어지면 인사말을 반환합니다. 선택적 타입은 데이터베이스의 NULL 허용 열과 같은 개념으로, "값이 없을 수 있음"을 타입에 명시하는 것입니다.

함수는 함수 시그니처의 기본값도 지원합니다.

```python
# Python
from functions.api import function, Double
from ontology_sdk.ontology.objects import Customer

@function
def compute_risk_factor(customer: Customer, weight: Double = 0.75) -> Double:
    # ...
```

(원문에는 TypeScript v1과 v2 버전의 예제도 있습니다.)

**설명**: `weight` 파라미터에 기본값 0.75를 지정했습니다. 호출하는 쪽이 `weight`를 넘기지 않으면 0.75가 쓰입니다. 함수 본문은 원문에서도 `...`로 생략되어 있습니다.

<a id="structcustom-type"></a>
### 구조체/사용자 정의 타입 (Struct/custom type)

사용자 정의 타입(custom type)은 다른 지원 타입(다른 사용자 정의 타입 포함)으로 구성되며, 함수 시그니처에 쓸 수 있습니다.

**참고**: 함수 시그니처에 쓰는 사용자 정의 타입은 온톨로지 구조체(struct) 속성용으로 생성되는 클래스와 다릅니다. Python 함수에서 온톨로지 구조체 속성을 편집하려면 [구조체 속성 편집하기](11_python/05_python-ontology-edits.md#edit-struct-properties)에서 설명하는 생성된 구조체 속성 클래스를 사용하세요.

* TypeScript 함수에서 사용자 정의 타입은 `interface` 키워드를 사용한 사용자 정의 TypeScript 인터페이스입니다.
  * 선택적 필드는 `?` 선택 토큰 또는 `undefined`와의 유니언으로 지원됩니다.

* Python 함수에서 사용자 정의 타입은 사용자 정의 Python 클래스입니다.
  * 유효한 사용자 정의 타입이 되려면 클래스가 다음을 지켜야 합니다.
    * 클래스의 모든 필드에 타입 주석이 있어야 합니다.
    * 필드 타입은 지원되는 타입이어야 합니다. 기본 API 타입이나 (위 표에 정의된) Python 기본 타입을 쓸 수 있습니다.
    * `__init__` 메서드는 필드와 이름과 타입 주석이 같은 이름 있는(named) 인자만 받아야 합니다.
  * [`dataclasses.dataclass` ↗](https://docs.python.org/3/library/dataclasses.html) 데코레이터를 사용하면 이 요구 사항에 맞는 `__init__` 메서드를 자동으로 생성할 수 있습니다.

```python
# Python
from dataclasses import dataclass
from functions.api import function, Integer
from ontology_sdk.ontology.objects import Passenger

@dataclass
class PassengerInfo:
    name: str | None
    age: Integer | None

@function
def get_passenger_info(passenger) -> PassengerInfo:
    return PassengerInfo(
        name=passenger.name,
        age=passenger.age
    )
```

(원문에는 TypeScript v1과 v2 버전의 예제도 있습니다. TypeScript에서는 `interface PassengerInfo { name?: string; age?: Integer; }`로 같은 타입을 정의합니다.)

**설명**: `Passenger` 객체를 받아 이름과 나이만 담은 `PassengerInfo` 구조체를 반환합니다. `@dataclass`는 `PassengerInfo(name=..., age=...)`처럼 필드 이름으로 값을 받는 `__init__`을 자동으로 만들어 주므로, 위의 세 요구 사항을 자연스럽게 만족합니다. 반환 결과는 `{name: "Kim", age: 31}` 같은 이름 붙은 필드 묶음이며, 함수가 여러 값을 한 번에 돌려줘야 할 때 씁니다.

> **중간 요약**: 컬렉션 타입(List, Map, Set, Optional)은 원소 타입을 반드시 지정해야 하며, Map 키로는 스칼라 타입이나 객체 타입만 쓸 수 있습니다. 사용자 정의 타입은 TypeScript `interface`나 Python 데이터클래스로 정의하고, 온톨로지 구조체 속성 클래스와는 별개입니다.

<a id="aggregation-types"></a>
## 집계 타입 (Aggregation types)

집계 타입은 함수에서 반환해 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)의 차트(Chart) 같은 플랫폼의 다른 부분에서 쓸 수 있습니다.

지원되는 집계 타입은 두 가지입니다.

* [2차원 집계](#two-dimensional-aggregation)는 버킷 키 하나에서 숫자 값으로 매핑합니다. 예를 들어 특정 직함을 가진 직원 수 같은 집계를 나타낼 수 있습니다.
* [3차원 집계](#three-dimensional-aggregation)는 버킷 키 두 개에서 숫자 값으로 매핑합니다. 예를 들어 직원의 직함과 근무 사무소별 직원 수 같은 집계를 나타낼 수 있습니다.

집계의 키로는 여러 타입을 쓸 수 있습니다.

* [Boolean](#boolean) 버킷은 `true` 또는 `false`인 값을 나타냅니다.
* [String](#string) 버킷은 범주형 값을 나타내는 데 쓸 수 있습니다.
* [Range](#range) 버킷은 버킷 키가 값의 범위인 집계를 나타냅니다. 차트의 히스토그램이나 날짜 축을 나타내는 데 쓸 수 있습니다.
  * [Integer](#integer)와 [Double](#double)을 포함한 숫자 범위는 숫자 값에 대한 버킷 집계를 나타냅니다.
  * [Date](#date)와 [Timestamp](#timestamp)를 포함한 날짜 및 시간 범위는 날짜 범위에 대한 버킷 집계를 나타냅니다.

**설명**: SQL의 `GROUP BY`와 대응합니다. 2차원 집계는 `SELECT job_title, COUNT(*) FROM employee GROUP BY job_title`의 결과처럼 (키, 값) 쌍의 목록입니다. 3차원 집계는 `GROUP BY job_title, office`처럼 키가 두 개인 결과로, 차트에서는 막대를 office별로 나눠 쌓거나 색으로 구분하는 데 쓰입니다. Range 버킷은 `GROUP BY` 키가 "20\~29세", "30\~39세" 같은 구간인 경우입니다.

<a id="range"></a>
### Range

필드 이름은 버전마다 다릅니다. TSv1의 `IRange<T>`와 Python의 `Range[T]`는 `min`과 `max`를 쓰고, TSv2의 `Range<T>`는 `startValue`와 `endValue`를 쓰며 열린 범위를 위해 둘 중 하나를 생략할 수 있습니다.

```typescript
// TypeScript v2
import { Integer, Range } from "@osdk/functions";

function getRange(min: Integer, max: Integer): Range<Integer> {
    return {
        startValue: min,
        endValue: max,
    };
}

export default getRange;
```

(원문에는 TypeScript v1(`{ min, max }`)과 Python(`Range(min=min, max=max)`) 버전의 예제도 있습니다.)

**설명**: 두 정수를 받아 그 사이의 범위를 반환합니다. 열린 범위란 예를 들어 `endValue`만 지정해 "100 이하 전부"를 나타내는 경우입니다.

<a id="two-dimensional-aggregation"></a>
### 2차원 집계 (Two-dimensional aggregation)

```typescript
// TypeScript v2
import { Double, TwoDimensionalAggregation } from "@osdk/functions";

function myTwoDimensionalAggregationFunction(): TwoDimensionalAggregation<string, Double> {
    return [
        { key: "bucket1", value: 5.0 },
        { key: "bucket2", value: 6.0 },
    ];
}

export default myTwoDimensionalAggregationFunction;
```

(원문에는 TypeScript v1과 Python 버전의 예제도 있습니다. TypeScript v1은 배열을 `{ buckets: [...] }`로 감싸고, Python은 `TwoDimensionalAggregation(buckets=[SingleBucket(key=..., value=...), ...])`로 만듭니다.)

**설명**: 키 `"bucket1"`에 5.0, `"bucket2"`에 6.0이 대응하는 집계를 반환합니다. Workshop 막대 차트에 연결하면 막대 두 개(높이 5와 6)로 그려집니다.

<a id="three-dimensional-aggregation"></a>
### 3차원 집계 (Three-dimensional aggregation)

버킷 구조는 버전마다 다릅니다. TSv1은 바깥 버킷을 `buckets` 키 아래에 두고 안쪽 단계를 `value`라는 키로 둡니다. TSv2는 바깥 단계를 감싸지 않은 배열로 반환하고 안쪽 단계를 `groups` 아래에 두므로, `ThreeDimensionalAggregation<T, U, V>`는 `{ key: T; groups: { key: U; value: V }[] }[]`가 됩니다. Python은 TSv1처럼 바깥 버킷을 감싸며, `NestedBucket`과 `SingleBucket` 클래스로 버킷을 만듭니다.

```typescript
// TypeScript v2
import { Double, ThreeDimensionalAggregation } from "@osdk/functions";

function myThreeDimensionalAggregation(): ThreeDimensionalAggregation<string, string, Double> {
    return [
        {
            key: "group-by-1",
            groups: [
                { key: "partition-by-1", value: 5.0 },
                { key: "partition-by-2", value: 6.0 },
            ],
        },
        {
            key: "group-by-2",
            groups: [
                { key: "partition-by-1", value: 7.0 },
                { key: "partition-by-2", value: 8.0 },
            ],
        },
    ];
}

export default myThreeDimensionalAggregation;
```

(원문에는 TypeScript v1과 Python 버전의 예제도 있습니다.)

**설명**: 결과를 표로 펼치면 다음과 같습니다.

| 첫 번째 키 | 두 번째 키 | 값 |
|---|---|---|
| group-by-1 | partition-by-1 | 5.0 |
| group-by-1 | partition-by-2 | 6.0 |
| group-by-2 | partition-by-1 | 7.0 |
| group-by-2 | partition-by-2 | 8.0 |

즉 `GROUP BY key1, key2`의 결과를 첫 번째 키 기준으로 중첩한 구조입니다. 같은 데이터를 TypeScript v1은 `{ buckets: [{ key, value: [...] }] }`로, TypeScript v2는 `[{ key, groups: [...] }]`로 표현하므로 버전을 옮길 때 필드 이름에 주의해야 합니다.

> **중간 요약**: 집계 타입은 Workshop 차트 등에서 쓰는 함수 반환 타입으로, 2차원은 키 하나, 3차원은 키 두 개에서 숫자 값으로 매핑합니다(SQL `GROUP BY` 결과에 해당). 키로는 Boolean, String, Range를 쓰며, Range와 3차원 집계는 버전마다 필드 이름과 중첩 구조가 다릅니다.

<a id="ontology-types"></a>
## 온톨로지 타입 (Ontology types)

함수 시그니처에서 객체 타입을 쓰려면 먼저 저장소로 가져와야(import) 합니다. [온톨로지 가져오기에 대해 자세히 알아보세요.](13_functions-on-objects/05_ontology-imports.md)

<a id="object"></a>
### 객체 (Object)

온톨로지의 객체 타입은 함수 시그니처에서 입력과 출력 모두로 쓸 수 있습니다. 객체 타입의 인스턴스 하나를 받거나 반환하려면, Ontology SDK에서 객체 타입을 가져와 그 타입으로 함수에 주석을 답니다.

```python
# Python
from functions.api import function, Integer
from ontology_sdk.ontology.objects import Airplane

@function
def get_capacity(airplane: Airplane) -> Integer:
    return airplane.capacity
```

(원문에는 TypeScript v1과 v2 버전의 예제도 있습니다. TypeScript v2에서는 파라미터 타입을 `Osdk.Instance<Airplane>`으로 씁니다.)

**설명**: `Airplane` 객체 하나를 받아 `capacity` 속성 값을 반환합니다. 객체 타입이 클래스, 객체가 그 인스턴스라는 대응이 코드에 그대로 드러납니다. 가져오기를 하면 `Airplane` 클래스가 생성되고, 함수는 그 인스턴스를 받아 속성을 필드처럼 읽습니다.

TypeScript v2에서는 객체 타입에 대한 참조를 [구조체](#structcustom-type) 파라미터 필드로 쓸 수 있습니다. 객체 타입 인스턴스를 담은 구조체나 구조체 리스트를 받으려면, Ontology SDK의 객체 타입 필드를 가진 사용자 정의 타입 입력을 만듭니다. 이를 [온톨로지 편집](#ontology-edit)과 함께 쓰면 다른 객체 타입들로부터 파생된 객체 타입 인스턴스 여러 개를 생성하는 워크플로를 지원할 수 있습니다.

(원문에는 `airplane`, `passenger`, `seat` 필드를 가진 `TicketInfo` 인터페이스의 배열을 받아, 항목마다 `Ticket` 객체를 생성하는 편집을 반환하는 TypeScript v2 예제가 있습니다.)

**설명**: 예를 들어 입력이 `[{airplane: KE001 비행기, passenger: 김철수, seat: "12A"}, {airplane: KE001 비행기, passenger: 이영희, seat: "12B"}]`이면, 함수는 비행기의 편명과 승객 이름, 좌석을 조합해 `Ticket` 객체 두 개를 생성하는 편집을 반환합니다.

<a id="object-set"></a>
### 객체 집합 (Object set)

객체 모음을 함수에 넣고 꺼내는 방법은 두 가지입니다. 구체적인 객체 컬렉션(배열 등)을 쓰거나, 객체 집합(object set)을 쓰는 것입니다.

객체 배열을 함수에 넘기면 구체적인 객체 목록에 대해 로직을 실행할 수 있지만, 대신 객체를 함수 실행 환경으로 미리 모두 로드해야 합니다. 반면 객체 집합을 쓰면 필터링, 서치 어라운드(search-around), 집계 연산을 수행하고 최종 결과는 요청할 때만 로드할 수 있습니다.

**팁**: 객체 집합은 대개 성능이 더 좋고 10,000개가 넘는 객체를 함수에 넘길 수 있으므로, 배열 대신 객체 집합을 쓸 것을 권장합니다.

아래 예제는 객체를 메모리에 로드하지 않고 객체 집합을 필터링해, 필터링된 객체 집합을 애플리케이션의 다른 부분으로 반환하는 방법을 보여 줍니다.

```typescript
// TypeScript v2
import { ObjectSet } from "@osdk/client";
import { Airplane } from "@ontology/sdk";

function filterAircraft(aircraft: ObjectSet<Airplane>): ObjectSet<Airplane> {
    return aircraft
        .where({
            capacity: {
                $gt: 200,
            }
        });
}

export default filterAircraft;
```

(원문에는 TypeScript v1(`aircraft.filter(a => a.capacity.range().gt(200))`)과 Python(`aircraft.where(Airplane.object_type.capacity > 200)`) 버전의 예제도 있습니다.)

**설명**: 객체 배열과 객체 집합의 차이는 "데이터를 이미 가져온 결과"와 "아직 실행하지 않은 쿼리"의 차이입니다. 배열은 `SELECT * FROM airplane`을 실행해 모든 행을 메모리로 가져온 상태이고, 객체 집합은 `SELECT * FROM airplane WHERE capacity > 200`이라는 쿼리 정의만 들고 있는 상태입니다. 위 함수는 객체를 하나도 로드하지 않고 쿼리에 조건을 덧붙여 반환할 뿐이므로, 비행기가 100만 대여도 빠르게 동작합니다. 실제 데이터는 이 객체 집합을 받은 쪽(예: Workshop 테이블)이 화면에 보여 줄 때 가져옵니다. 서치 어라운드는 링크를 따라 연결된 객체 집합으로 이동하는 연산(SQL 조인에 해당)입니다.

<a id="interface"></a>
### 인터페이스 (Interface)

온톨로지의 인터페이스 타입은 TypeScript v2 함수 시그니처에서 입력과 출력 모두로 쓸 수 있습니다. TypeScript v1이나 Python에서는 지원되지 않습니다.

```typescript
// TypeScript v2
import { Osdk } from "@osdk/client";
import { Integer } from "@osdk/functions";
import { Person } from "@ontology/sdk";

function getAge(person: Osdk.Instance<Person>): Integer {
    return person.age;
}

export default getAge;
```

**설명**: `Person`은 객체 타입이 아니라 인터페이스입니다. 따라서 `Person` 인터페이스를 구현한 어떤 객체 타입(예: `Employee`, `Customer`)의 객체든 이 함수에 넘길 수 있고, 함수는 인터페이스에 정의된 `age` 속성만 사용합니다.

<a id="interface-object-set"></a>
### 인터페이스 객체 집합 (Interface object set)

인터페이스 객체 집합은 TypeScript v2 함수 시그니처에서 입력과 출력 모두로 쓸 수 있습니다.

(원문에는 `ObjectSet<Person>`을 받아 `age`가 200보다 큰 객체로 필터링해 반환하는 TypeScript v2 예제가 있습니다. 구조는 위 객체 집합 예제와 같습니다.)

<a id="ontology-edit"></a>
### 온톨로지 편집 (Ontology edit)

온톨로지에서 데이터를 읽는 함수 외에도, 객체를 생성하고 객체의 속성과 객체 사이의 링크를 편집하는 함수를 작성할 수 있습니다. 편집 함수의 동작 방식에 대한 자세한 내용은 [개요 페이지](09_language-agnostic-features/01_edits-overview.md)를 참고하세요.

편집 함수로 등록되려면, TypeScript v1 함수는 시그니처에 `void` 반환 타입이 있어야 합니다. 반면 TypeScript v2와 Python 함수는 온톨로지 편집 목록을 명시적으로 반환해야 합니다.

```typescript
// TypeScript v2
import { Client } from "@osdk/client";
import { createEditBatch, Edits } from "@osdk/functions";
import { Employee, LaptopRequest } from "@ontology/sdk";

type EmployeeEdit =
    | Edits.Object<Employee>
    | Edits.Object<LaptopRequest>
    | Edits.Link<Employee, "lead">;

function assignEmployee(
    client: Client,
    newEmployee: Osdk.Instance<Employee>,
    leadEmployee: Osdk.Instance<Employee>
): EmployeeEdit[] {

    const batch = createEditBatch<EmployeeEdit>(client);

    batch.create(LaptopRequest, {
        id: Date.now().toString(),
        employeeName: newEmployee.name,
    });
    batch.link(newEmployee, "lead", leadEmployee);

    return batch.getEdits();
}

export default assignEmployee;
```

(원문에는 TypeScript v1과 Python 버전의 예제도 있습니다. TypeScript v1은 `@Edits(Employee, LaptopRequest)`와 `@OntologyEditFunction()` 데코레이터를 붙이고 반환 타입이 `void`이며, 객체를 직접 수정하는 방식으로 작성합니다.)

**설명**: 신규 직원과 리드 직원을 받아 두 가지 편집을 만듭니다. (1) 현재 시각을 ID로 하는 `LaptopRequest` 객체를 생성하고 직원 이름을 기록합니다. (2) 신규 직원과 리드 직원 사이에 `lead` 링크를 만듭니다. `EmployeeEdit` 타입은 이 함수가 만들 수 있는 편집의 종류(어떤 객체 타입과 링크 타입을 건드리는지)를 미리 선언한 것입니다. 핵심은 함수가 데이터베이스를 직접 바꾸지 않는다는 점입니다. `batch`에 편집을 모아 `getEdits()`로 목록을 반환할 뿐이고, 이 목록을 실제로 온톨로지에 적용하는 것은 이 함수를 호출한 액션입니다. TypeScript v1은 반환값 대신 객체를 직접 수정하는 코드를 쓰고 플랫폼이 그 변경을 수집하는 방식이라 반환 타입이 `void`입니다.

<a id="attachment"></a>
### 첨부 파일 (Attachment)

(원문에는 `Attachment`를 받아 내용을 문자열로 읽어 반환하는 예제가 세 언어로 있습니다. TypeScript v1은 `attachment.readAsync()`, TypeScript v2는 `attachment.fetchContents()`, Python은 `attachment.read()`를 사용합니다.)

**설명**: 첨부 파일은 사용자가 액션 폼 등으로 업로드한 파일입니다. 함수는 파일을 참조하는 `Attachment` 값을 받고, 필요할 때 위 메서드로 실제 내용을 읽습니다.

<a id="notification"></a>
### 알림 (Notification)

알림 타입을 함수에서 반환해, 플랫폼에서 보낼 알림을 유연하게 구성할 수 있습니다. 예를 들어 `User`와 객체 타입 같은 파라미터를 받아 메시지가 구성된 Notification을 반환하는 함수를 작성할 수 있습니다.

* `Notification`은 `ShortNotification`과 `EmailNotificationContent` 두 필드로 구성됩니다.
* `ShortNotification`은 알림의 요약 버전으로, Foundry 플랫폼 안에 표시됩니다. 짧은 `heading`(제목), `content`(내용), `Link` 모음을 포함합니다.
* `EmailNotificationContent`는 이메일로 외부에 보낼 수 있는 풍부한 버전의 알림입니다. `subject`(제목), 헤드리스 HTML로 된 `body`(본문), `Link` 모음을 포함합니다.
* `Link`에는 사용자에게 보이는 `label`과 `linkTarget`이 있습니다. `LinkTarget`은 URL, `OntologyObject`, 또는 Foundry 안의 어떤 리소스든 그 `rid`일 수 있습니다.

알림 API 사용 예는 [가이드](09_language-agnostic-features/03_configure-notifications.md)를 참고하세요.

```typescript
// TypeScript v2
import {
    Notification
} from "@osdk/functions";

export default function buildNotification(): Notification {
    return {
        platformNotification: {
            heading: "Issue reminder",
            content: "Investigate this issue.",
            links: []
        },
        emailNotification: {
            subject: "New issue",
            body: "hello",
            links: []
        }
    };
}
```

(원문에는 TypeScript v1(빌더 패턴: `Notification.builder().shortNotification(...).emailNotificationContent(...).build()`)과 Python 버전의 예제도 있습니다.)

**설명**: 플랫폼 내 알림(제목 "Issue reminder")과 이메일 알림(제목 "New issue")을 함께 정의해 반환합니다. TypeScript v2와 Python에서는 필드 이름이 `platformNotification`/`emailNotification`(Python은 `platform_notification`/`email_notification`)으로, 위 목록의 `ShortNotification`/`EmailNotificationContent`(TypeScript v1 이름)에 각각 대응합니다. "헤드리스 HTML"은 `<html>`, `<head>` 같은 문서 껍데기 없이 `<p>`, `<b>` 같은 본문 태그만으로 된 HTML 조각을 뜻합니다.

> **중간 요약**: 온톨로지 타입을 쓰려면 먼저 가져오기를 해야 합니다. 객체는 객체 타입 인스턴스 하나, 객체 집합은 아직 로드하지 않은 쿼리이며 대량 데이터에는 객체 집합이 권장됩니다. 인터페이스와 인터페이스 객체 집합은 TypeScript v2에서만 지원됩니다. 편집 함수는 TypeScript v1에서는 `void`를, v2와 Python에서는 편집 목록을 반환하며, Attachment와 Notification 타입도 지원됩니다.

<a id="media-types"></a>
## 미디어 타입 (Media types)

<a id="media"></a>
### 미디어 (Media)

함수는 미디어 항목을 받고 반환할 수 있습니다. TypeScript v1에서는 `MediaItem` 타입을 쓰고, TypeScript v2와 Python에서는 입력과 출력 타입 모두 `Media`를 씁니다. 호출하는 쪽은 객체의 미디어 속성 같은 기존 `MediaReference`를 함수에 넘길 수 있습니다. 다운스트림 소비자는 반환된 값을 이용해 내용을 가져오거나, 메타데이터를 가져오거나, 다른 객체에 첨부할 수 있습니다. 자세한 내용은 [미디어](13_functions-on-objects/09_media.md) 가이드를 참고하세요.

```python
# Python
from foundry_sdk.v2.core.models import MediaReference
from functions.api import function, Media

@function
def echo_media(media: Media) -> Media:
    # 내부의 MediaReference를 가져옵니다
    media_reference: MediaReference = media.get_media_reference()
    # 간단한 메타데이터(path, size_bytes, media_type)를 가져옵니다
    metadata = media.get_media_metadata()
    # 유형별 메타데이터(페이지 수, 크기, 재생 시간 등)를 가져옵니다
    full_metadata = media.get_media_full_metadata()
    # 바이너리 내용을 BytesIO 스트림으로 가져옵니다
    contents = media.get_media_content()
    return media
```

(원문에는 TypeScript v1과 v2 버전의 예제도 있습니다. TypeScript v1 예제는 `MediaItem.isDocument(media)`, `MediaItem.isAudio(media)`로 하위 타입을 판별해 문서면 텍스트 추출(`extractTextAsync`), 오디오면 음성 전사(`transcribeAsync`)를 호출하는 방법도 보여 줍니다.)

**설명**: 미디어(PDF, 이미지, 오디오 등)를 받아 그대로 반환하면서, 그 과정에서 쓸 수 있는 메서드를 보여 줍니다. `MediaReference`는 실제 파일 바이트가 아니라 파일을 가리키는 참조값입니다. 그래서 함수가 미디어를 받을 때 파일 전체가 전달되는 것이 아니라 참조가 전달되고, 내용이 필요할 때만 `get_media_content()`로 바이트를 가져옵니다.

<a id="users-groups-and-principals"></a>
## 사용자, 그룹, 주체 (Users, groups, and principals)

주체(Principal)는 Foundry 사용자 계정 또는 그룹을 나타냅니다. 이 타입들을 함수에 넘기면 그룹 이름이나 사용자의 이름, 성, 이메일 주소처럼 사용자나 그룹에 연관된 정보에 접근할 수 있습니다. 모든 Principal 타입은 `@foundry/functions-api` 패키지에서 내보냅니다.

* `User`는 항상 사용자 이름(username)을 가지며, `firstName`, `lastName`, `email`을 가질 수 있습니다. `Principal`에 연관된 모든 필드도 포함합니다.
* `Group`은 이름을 가집니다. `Principal`에 연관된 모든 필드도 포함합니다.
* `Principal`은 `User` 또는 `Group`일 수 있습니다. `type` 필드를 보고 주어진 `Principal`이 `User`인지 `Group`인지 판단할 수 있습니다. `User`와 `Group` 고유 필드 외에, `Principal`은 `id`, `realm`, 그리고 `attributes` 딕셔너리를 가집니다.

**설명**: 객체 지향으로 보면 `Principal`이 상위 타입이고 `User`와 `Group`이 하위 타입입니다. `type` 필드는 어떤 하위 타입인지 구분하는 판별자(discriminator)입니다. 또 표에서 보듯 TypeScript v1은 `User`/`Group` 객체 자체를 받지만, TypeScript v2와 Python은 `UserId`/`GroupId`(식별자)만 받고 상세 정보는 필요할 때 Admin API로 조회한다는 차이가 있습니다.

<a id="user"></a>
### 사용자 (User)

```typescript
// TypeScript v1
import { Function, User } from "@foundry/functions-api";

export class MyFunctions {
    @Function()
    public getUserEmail(user: User): string {
        return user.email;
    }
}
```

(원문에는 TypeScript v2와 Python 버전의 예제도 있습니다. 두 버전은 `UserId`를 받아 `Users.get(client, userId)` 또는 `client.admin.User.get(user_id)`로 사용자 정보를 조회한 뒤 이메일을 반환합니다.)

**설명**: TypeScript v1에서는 `User` 객체가 바로 들어오므로 `user.email`을 읽기만 하면 됩니다. v2와 Python에서는 ID만 들어오므로 한 번 더 조회하는 단계가 필요합니다.

<a id="group"></a>
### 그룹 (Group)

(원문에는 그룹을 받아 이름을 반환하는 예제가 세 언어로 있습니다. 구조는 위 사용자 예제와 같으며, TypeScript v1은 `group.name`을 바로 읽고, TypeScript v2와 Python은 `GroupId`로 `Groups.get` 또는 `client.admin.Group.get`을 호출합니다.)

<a id="principal"></a>
### 주체 (Principal)

```typescript
// TypeScript v1
import { Function, Principal } from "@foundry/functions-api";

export class MyFunctions {
    @Function()
    public getPrincipalType(principal: Principal): string {

        switch (principal.type) {
            case "user":
                return "User";
            case "group":
                return "Group";
            default:
                return "Unknown";
        }
    }
}
```

(원문에는 TypeScript v2와 Python 버전의 예제도 있습니다. 두 버전은 `UserId`와 `GroupId`를 받아 `{type: "user", id: userId}`(Python은 `Principal.user(user_id)`)와 같은 형태로 Principal 두 개의 목록을 만들어 반환합니다.)

**설명**: `type` 필드 값에 따라 `"User"` 또는 `"Group"`을 반환합니다. 판별자 필드로 하위 타입을 분기하는 전형적인 패턴입니다.

> **중간 요약**: 미디어는 TypeScript v1에서 `MediaItem`, v2와 Python에서 `Media`로 다루며 파일 자체가 아니라 참조가 전달됩니다. Principal은 User 또는 Group이고 `type` 필드로 구분하며, TypeScript v1은 객체 자체를, v2와 Python은 ID를 받아 필요 시 조회합니다.

<a id="geometry-types"></a>
## 지오메트리 타입 (Geometry types)

지오메트리 타입은 함수에서 공간 데이터와 지리적 도형을 나타냅니다. 두 가지 지오메트리 타입이 지원됩니다.

* **GeoPoint는** 위도와 경도 좌표를 가진 지리적 점 하나를 나타냅니다.
* **GeoShape는** Point, Polygon, LineString 등을 포함한 유효한 GeoJSON 지오메트리 무엇이든 나타냅니다.

이 타입들은 [GeoJSON 명세 ↗](https://geojson.org/)를 따르며 공간 연산, 지도 표시, 지리 분석에 쓸 수 있습니다. 위치 인자는 GeoJSON 명세에 따라 경도, 위도 순서를 따릅니다.

<a id="geopoint"></a>
### GeoPoint

다음 예제는 GeoPoint를 생성해 반환하는 방법을 보여 줍니다.

```typescript
// TypeScript v2
import { Point } from "@osdk/functions";

function createPoint(): Point {
    return {
        type: "Point",
        coordinates: [-22.4194, 37.7749]
    };
}

export default createPoint;
```

(원문에는 TypeScript v1(`GeoPoint.fromCoordinates({ latitude, longitude })`)과 Python(`GeoPoint(type="Point", coordinates=[...])`) 버전의 예제도 있습니다.)

**설명**: `coordinates` 배열이 `[경도, 위도]` 순서라는 점에 주의하세요. 일상에서는 "위도, 경도" 순서로 말하는 경우가 많지만 GeoJSON은 x(경도), y(위도) 순서입니다. TypeScript v1처럼 `latitude`, `longitude`를 이름으로 지정하는 방식에서는 순서 혼동이 없습니다.

<a id="geoshape"></a>
### GeoShape

다음 예제는 Polygon을 생성해 반환하는 방법을 보여 줍니다.

```python
# Python
from functions.api import function, Polygon

@function
def create_polygon() -> Polygon:
    return Polygon(
        type="Polygon",
        coordinates=[[
            [-22.4, 37.8],
            [-22.5, 37.8],
            [-22.5, 37.7],
            [-22.4, 37.7],
            [-22.4, 37.8]
        ]])
```

(원문에는 TypeScript v1과 v2 버전의 예제도 있습니다.)

**설명**: 꼭짓점 네 개로 된 사각형 다각형을 만듭니다. 점이 다섯 개인 이유는 GeoJSON에서 다각형의 고리(linear ring)는 첫 점과 마지막 점이 같아야, 즉 닫혀 있어야 하기 때문입니다. `coordinates`가 이중 배열인 것은 바깥 경계 고리 외에 구멍(안쪽 고리)을 추가로 넣을 수 있는 구조이기 때문입니다.

[온톨로지 편집 함수](09_language-agnostic-features/01_edits-overview.md)는 GeoJSON 문자열로 `geoshape` 속성을 설정할 수 있지만, 변환 단계는 언어마다 다릅니다.

* **TypeScript v1:** `GeoShape.fromGeoJson()`은 파싱된 GeoJSON 지오메트리나 지오메트리 컬렉션을 받으므로, 문자열을 넘기기 전에 파싱해야 합니다.
* **TypeScript v2:** `Geometry`는 일반 GeoJSON 객체이므로 변환 함수가 필요 없습니다. 파싱한 값을 바로 대입합니다.
* **Python:** `Polygon`이나 `LineString` 같은 각 구체적인 지오메트리 클래스는 JSON 문자열 자체를 받는 `from_geo_json()` 메서드를 제공합니다. `GeoShape` 타입은 이 메서드를 제공하지 않으므로, 기대하는 지오메트리에 맞는 클래스를 사용하세요.

다음 예제는 JSON 문자열로 `Region` 객체의 `geoshape` 속성을 설정합니다.

```typescript
// TypeScript v1
import { OntologyEditFunction, Edits, GeoShape } from "@foundry/functions-api";
import { Region } from "@foundry/ontology-api";

export class MyFunctions {
    @Edits(Region)
    @OntologyEditFunction()
    public updateBoundary(region: Region, boundary: string): void {
        region.boundary = GeoShape.fromGeoJson(JSON.parse(boundary));
    }
}
```

(원문에는 TypeScript v2(`batch.update(region, { boundary: JSON.parse(boundary) as Geometry })`)와 Python(`Polygon.from_geo_json(boundary)`) 버전의 예제도 있습니다.)

**설명**: `Region` 객체와 GeoJSON 문자열(예: `'{"type":"Polygon","coordinates":[[[...]]]}'`)을 받아, 문자열을 `JSON.parse`로 객체로 바꾼 뒤 `GeoShape.fromGeoJson()`으로 변환해 `boundary` 속성에 대입합니다. 위 목록에서 설명한 언어별 차이(TypeScript v1은 파싱 후 변환, v2는 파싱만, Python은 문자열을 바로 받는 클래스 메서드)가 이 예제에서 드러납니다.

> **중간 요약**: GeoPoint는 점 하나, GeoShape는 모든 GeoJSON 지오메트리를 나타내며 좌표는 경도, 위도 순서입니다. GeoJSON 문자열로 `geoshape` 속성을 설정할 때 TypeScript v1은 파싱 후 `GeoShape.fromGeoJson()`, v2는 파싱한 값을 그대로, Python은 `Polygon.from_geo_json()` 같은 구체 클래스 메서드를 씁니다.

## 정리

- 함수 레지스트리에 게시하려면 모든 파라미터와 반환값의 타입을 명시해야 하며, 같은 레지스트리 타입이 TypeScript v1, TypeScript v2, Python에서 서로 다른 언어 타입으로 표현됩니다.
- 숫자는 Integer, Long, Float, Double 같은 별칭으로 종류를 명시하며, Python의 `int`와 `float`는 기본적으로 Integer와 Float로 등록됩니다. Long은 2<sup>53</sup> - 1로 제한되고 TypeScript v2에서는 문자열입니다.
- 컬렉션은 원소 타입을 지정해야 하고, 사용자 정의 타입은 TypeScript `interface`나 Python 데이터클래스로 정의하며, 집계 타입은 Workshop 차트 등에 쓰이는 `GROUP BY` 결과 형태입니다.
- 온톨로지 타입은 가져오기가 필요하며, 대량 데이터에는 배열 대신 객체 집합이 권장되고, 편집 함수는 TypeScript v1은 `void`, v2와 Python은 편집 목록을 반환합니다.
- 버전별 지원 차이(인터페이스는 TypeScript v2만, Short/Byte/Binary/Decimal은 Python만, Set은 TypeScript v2 미지원)와 필드 이름 차이(Range, 3차원 집계, Notification, User/Group)에 주의해야 합니다.
