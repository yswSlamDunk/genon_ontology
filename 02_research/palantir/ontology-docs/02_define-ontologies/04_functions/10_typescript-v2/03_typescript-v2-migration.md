# TypeScript v1에서 TypeScript v2로 마이그레이션 (Migrate from TypeScript v1 to TypeScript v2)

- 원문: https://www.palantir.com/docs/foundry/functions/typescript-v2-migration/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v2 > Migrate from TypeScript v1 to TypeScript v2

이 페이지는 TypeScript v1으로 작성한 기존 함수(function)를 TypeScript v2로 옮길 때 달라지는 문법과 구조를 항목별로 정리한 마이그레이션 안내서입니다. 함수 선언 방식, 타입을 가져오는 패키지, 온톨로지 조회(필터, 링크 탐색, 그룹화, 집계), 객체 식별, 온톨로지 편집(edit), ID 생성, 객체 로딩 방식이 각각 어떻게 바뀌는지 v1과 v2 코드를 나란히 비교합니다. 특히 v1에는 있었지만 v2에는 대응 기능이 없는 항목도 따로 정리되어 있어, 실제 마이그레이션 전에 점검 목록으로 쓸 수 있습니다.

이 가이드는 기존 TypeScript 함수를 v1에서 v2로 마이그레이션하면서 마주칠 수 있는 문법과 구조의 차이를 설명합니다. v2에서 개선된 점과 각 버전이 지원하는 기능은 [기능 지원 문서](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)를 참고하세요.

<a id="declare-a-function"></a>
## 함수 선언하기 (Declare a function)

TypeScript v1에서 함수를 플랫폼에 게시하려면 `@foundry/functions-api` 패키지의 `@Function()` 데코레이터를 함수에 붙여야 합니다. 또한 함수는 저장소(repository)의 루트 `index.ts` 파일에서 export하는 클래스의 메서드여야 합니다.

```typescript tab="TypeScript v1"
// src/index.ts

import { Function } from "@foundry/functions-api";

export class MyFunctions {

    @Function()
    public reverseStringArray(arr: string[]): string[] {
        return arr.reverse();
    }
}
```

TypeScript v2에서 함수를 플랫폼에 게시하려면 `src/functions` 디렉터리 안의 파일에 함수를 작성하고 `export default`로 내보내야 합니다. 파일 하나는 함수 하나만 export할 수 있습니다.

```typescript tab="TypeScript v2"
// src/functions/reverseStringArray.ts

export default function reverseStringArray(
    arr: string[]
): string[] {
    return arr.reverse();
}
```

**설명**: 두 코드는 문자열 배열을 받아 순서를 뒤집어 돌려주는 같은 함수입니다. 차이는 "플랫폼이 어떤 코드를 함수로 인식하는가"에 있습니다. v1은 클래스 메서드에 `@Function()` 데코레이터(클래스나 메서드에 메타데이터를 붙이는 TypeScript 문법)를 달아 표시하고, v2는 `src/functions` 아래 파일 하나에 `export default` 함수 하나를 두는 파일 단위 규칙으로 인식합니다. 따라서 v2에서는 파일 이름과 함수가 일대일로 대응합니다.

저장소를 정리된 상태로 유지하려면 관련 함수끼리 `src/functions` 디렉터리 안의 하위 디렉터리로 묶는 것을 권장합니다. 예를 들어 다음 폴더 구조는 함수를 `payroll`과 `staffing` 하위 디렉터리로 나누어 책임 구분을 더 분명하게 합니다.

![TypeScript v2 함수의 폴더 구조 예시.](https://www.palantir.com/docs/resources/foundry/functions/typescript-v2-folder-structure.png)

자세한 내용은 [TypeScript v2 함수 시작하기](01_typescript-v2-getting-started.md) 문서를 참고하세요.

> **중간 요약**: v1은 루트 `index.ts`에서 export한 클래스의 메서드에 `@Function()`을 붙여 함수를 선언하고, v2는 `src/functions` 아래 파일마다 `export default` 함수 하나를 둡니다.

<a id="use-the-osdkfunctions-package"></a>
## `@osdk/functions` 패키지 사용하기 (Use the `@osdk/functions` package)

TypeScript v1에서는 `Integer`, `Double` 같은 원시 타입을 시그니처에 쓰려면 `@foundry/functions-api` 패키지에서 가져와야 합니다. 반면 TypeScript v2에서는 그 대신 `@osdk/functions` 패키지를 사용해야 합니다.

다음 예제는 `@foundry/functions-api` 패키지에서 `Integer` 타입을 가져와, 두 정수의 최대공약수를 계산하는 TypeScript v1 함수의 시그니처에 사용합니다. TypeScript v2에서는 핵심 TypeScript 로직은 동일하지만 `@osdk/functions` 패키지의 `Integer` 타입을 사용해야 합니다.

```typescript tab="TypeScript v2"
import { Integer } from "@osdk/functions";

export default function gcd(a: Integer, b: Integer): Integer {
    if (b === 0) {
        return a;
    }
    return gcd(b, a % b);
}
```

(원문에는 같은 `gcd` 함수를 `@foundry/functions-api`의 `Integer`와 `@Function()` 데코레이터로 작성한 TypeScript v1 버전도 있습니다.)

**설명**: 유클리드 호제법으로 최대공약수를 구하는 재귀 함수입니다. 바뀐 것은 첫 줄의 import 경로뿐입니다. TypeScript 언어 자체에는 정수 전용 타입이 없고 `number`만 있으므로, Foundry는 `Integer`, `Double` 같은 별도 타입을 제공해 플랫폼에 "이 파라미터는 정수"라는 정보를 전달합니다. v2에서는 이 타입들이 `@osdk/functions` 패키지에 있습니다.

TypeScript v1과 TypeScript v2 함수 모두에서 타입을 가져와 시그니처에 쓰는 방법의 예시는 [타입 레퍼런스](../04_types-reference.md)를 참고하세요.

> **중간 요약**: 시그니처에 쓰는 Foundry 원시 타입은 v1에서는 `@foundry/functions-api`, v2에서는 `@osdk/functions`에서 가져옵니다.

<a id="dates-and-timestamps"></a>
## 날짜와 타임스탬프 (Dates and timestamps)

TypeScript v1은 시간 데이터를 다룰 때 `@foundry/functions-api` 패키지의 `LocalDate`와 `Timestamp` 타입을 사용합니다. TypeScript v2는 이를 `@osdk/functions` 패키지의 `DateISOString`과 `TimestampISOString` 타입으로 대체하며, 이 타입들은 날짜와 타임스탬프를 [ISO 8601 ↗](https://www.iso.org/iso-8601-date-and-time-format.html) 문자열로 표현합니다.

TypeScript v2 함수는 [dayjs ↗](https://www.npmjs.com/package/dayjs), [date-fns ↗](https://www.npmjs.com/package/date-fns), [luxon ↗](https://www.npmjs.com/package/luxon)처럼 NPM 생태계에 있는 어떤 날짜 및 타임스탬프 라이브러리든 사용할 수 있습니다.

**설명**: ISO 8601 문자열은 `"2024-03-15"`(날짜)나 `"2024-03-15T09:30:00Z"`(타임스탬프, 끝의 `Z`는 UTC)처럼 국제 표준 형식으로 적은 문자열입니다. v2에서는 날짜 값이 전용 객체가 아니라 이런 문자열로 들어오므로, 날짜 계산이 필요하면 위 라이브러리로 문자열을 파싱한 뒤 계산하고 다시 문자열로 돌려주면 됩니다.

> **중간 요약**: v2는 날짜와 타임스탬프를 ISO 8601 문자열 타입(`DateISOString`, `TimestampISOString`)으로 다루며, 계산에는 일반 NPM 날짜 라이브러리를 쓸 수 있습니다.

<a id="generate-the-ontology-sdk"></a>
## Ontology SDK 생성하기 (Generate the Ontology SDK)

TypeScript v2 함수는 [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/)를 통해 온톨로지를 조회하고 편집하는 기능을 일급(first-class)으로 지원합니다. TypeScript v1과 마찬가지로 TypeScript v2 저장소에서도 [**Resource imports** 사이드바](../12_typescript-v1/08_resource-imports-sidebar.md)를 통해 온톨로지 엔터티를 가져올 수 있습니다. 객체 타입과 링크 타입을 추가하면 Ontology SDK의 초기 버전을 만들라는 안내가 나타납니다.

![TypeScript 코드 저장소에서 첫 번째 Ontology SDK를 만들라는 안내.](https://www.palantir.com/docs/resources/foundry/functions/osdk-create-initial-version.png)

**Create**를 선택한 다음 Ontology SDK의 이름을 정합니다. 이 이름은 첫 번째 버전이 생성된 후에는 바꿀 수 없습니다. **Create new version**을 선택해 Ontology SDK를 생성합니다.

![첫 번째 Ontology SDK를 생성하기 전에 이름을 정합니다.](https://www.palantir.com/docs/resources/foundry/functions/osdk-name.png)

Ontology SDK가 생성되면 워크스페이스에 설치하는 옵션이 보입니다. **Install**을 선택하면 Ontology SDK가 `package.json` 파일에 의존성으로 추가되어 TypeScript 코드에서 사용할 수 있게 됩니다.

![TypeScript 코드 저장소에서 Ontology SDK를 설치하라는 안내.](https://www.palantir.com/docs/resources/foundry/functions/osdk-install.png)

TypeScript에서 온톨로지를 다루는 포괄적인 예제는 사이드바의 **Documentation** 탭에서 볼 수 있습니다.

**설명**: Ontology SDK(OSDK)는 사용자의 온톨로지에 정의된 객체 타입, 속성, 링크 타입으로부터 자동 생성되는 TypeScript 패키지입니다. 예를 들어 온톨로지에 `Aircraft` 객체 타입이 있으면 SDK에 `Aircraft`라는 이름의 타입 정의가 생기고, 코드에서 `import { Aircraft } from "@ontology/sdk"`처럼 가져와 쓸 수 있습니다. 온톨로지 구조가 바뀌면 SDK의 새 버전을 생성해야 코드에서 그 변경을 볼 수 있습니다.

> **중간 요약**: v2에서는 Resource imports로 객체 타입과 링크 타입을 추가한 뒤 Ontology SDK를 생성하고(이름은 이후 변경 불가) `Install`로 `package.json`에 의존성을 추가해 사용합니다.

<a id="query-the-ontology"></a>
## 온톨로지 조회하기 (Query the Ontology)

TypeScript v1에서는 온톨로지를 검색하려면 `@foundry/ontology-api` 패키지에서 `Objects`를 가져와야 합니다.

```typescript tab="TypeScript v1"
import { Function, Integer } from "@foundry/functions-api";
import { Objects } from "@foundry/ontology-api";

export class MyFunctions {

    @Function()
    public async countAircraft(): Promise<Integer> {
        const count = await Objects.search().aircraft().count() ?? 0;

        return count;
    }
}
```

TypeScript v2에서는 함수 시그니처의 첫 번째 인수로 Ontology SDK 클라이언트를 지정해 접근해야 합니다.

```typescript tab="TypeScript v2"
import { Aircraft } from "@ontology/sdk";
import { Client } from "@osdk/client";
import { Integer } from "@osdk/functions";

export default async function countAircraft(client: Client): Promise<Integer> {
    const aircraft = await client(Aircraft).aggregate({
        $select: {
            $count: "unordered"
        }
    });

    return aircraft.$count;
}
```

**설명**: 두 함수 모두 Aircraft 객체의 개수를 셉니다. SQL로 쓰면 `SELECT COUNT(*) FROM aircraft`에 해당합니다. v1은 전역 객체 `Objects`에서 `search().aircraft()`로 객체 집합(object set)을 얻고 `.count()`를 호출합니다. v2는 플랫폼이 넘겨주는 `client`를 첫 번째 파라미터로 받고, `client(Aircraft)`로 객체 집합을 얻은 뒤 `.aggregate()`에 "개수를 세라"는 요청 객체(`$select: { $count: ... }`)를 전달합니다. 결과의 `$count` 필드에 개수가 들어 있습니다.

이 섹션의 나머지 부분은 TypeScript v1의 조회 어휘를 TypeScript v2의 대응 표현에 매핑합니다. TypeScript v2의 전체 조회 어휘는 [TypeScript OSDK 레퍼런스](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/)를 확인하세요.

필터링, 정렬, 집계에 사용하는 모든 속성(property)은 두 버전 모두에서 Ontology Manager에 `Searchable`로 표시되어 있어야 합니다. `Searchable`은 속성이 인덱싱되는 방식을 제어하므로, 이 요구 사항은 어느 한쪽 SDK가 아니라 온톨로지에 속합니다. 달라지는 것은 문제를 발견하는 시점입니다. TypeScript v1에서는 코드 생성기가 표시되지 않은 속성에 대해 필터, 정렬, 집계 메서드를 생성하지 않으므로 그런 메서드를 쓰면 컴파일에 실패합니다. 반면 Ontology SDK는 `.where()`, `$orderBy`, `.aggregate()`에서 객체 타입의 어떤 속성이든 받아들입니다.

**주의**: 마이그레이션 전에 Searchable 여부를 확인하세요(Confirm Searchable before you migrate). 마이그레이션하기 전에 필터링, 정렬, 집계에 쓰는 모든 속성이 Ontology Manager에서 `Searchable`로 표시되어 있는지 확인하세요. TypeScript v2에서는 표시되지 않은 속성도 컴파일되므로 문제는 함수가 실행될 때에야 드러납니다. `$containsAnyTerm` 같은 전문(full-text) 검색 조건은 오류 대신 빈 페이지를 반환하므로, 필터가 아무것도 일치시키지 못하면서도 성공했다고 보고할 수 있습니다.

**설명**: 인덱스(index)는 데이터베이스에서 특정 열로 빠르게 검색하기 위해 미리 만들어 두는 보조 자료구조입니다. 인덱스가 없는 열로는 효율적인 검색이나 정렬을 할 수 없으므로, Foundry는 `Searchable`로 표시된 속성만 필터, 정렬, 집계에 쓸 수 있게 합니다. v1은 이 제약을 컴파일 시점에 잡아 주었지만 v2는 잡아 주지 않으므로, v2로 옮긴 함수가 오류 없이 빈 결과를 내면 먼저 이 설정을 의심해야 합니다.

> **중간 요약**: v2에서는 첫 번째 파라미터로 받은 `client`로 온톨로지를 조회합니다. 필터, 정렬, 집계 대상 속성은 두 버전 모두 `Searchable`이어야 하지만, v2는 이를 컴파일 시점에 검사하지 않으므로 미리 확인해야 합니다.

<a id="filter-operator-mapping"></a>
### 필터 연산자 매핑 (Filter operator mapping)

TypeScript v1에서 `.filter()` 메서드는 필터링하는 속성의 타입에 따라 선택되는 필터 정의를 받습니다. TypeScript v2는 이 메서드 계열을 절(clause) 객체를 받는 단일 `.where()` 호출로 대체합니다. 다음 표는 각 TypeScript v1 필터 메서드를 TypeScript v2의 where 절 키와 적용 가능한 속성 타입에 매핑합니다.

TypeScript v2의 제한은 TypeScript v1의 대응 기능보다 엄격합니다. 지리공간(geospatial) 속성은 `$within`, `$intersects`, `$isNull`만 받고, 배열 속성은 `$contains`와 `$isNull`만 받습니다. 각 필터의 형태는 TypeScript OSDK 레퍼런스의 [Filtering](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#filtering)을 확인하세요. 다만 그 문서는 `$within`, `$intersects`, `$interval`을 다루지 않습니다.

| TypeScript v1 | TypeScript v2 where 절 키 | 적용 대상 |
|---|---|---|
| `.exactMatch(value)` | `$eq`, 또는 값 그대로 | Boolean, Datetime, Number, String |
| `.exactMatch(...values)` | `$in: [...]` | Boolean, Datetime, Number, String |
| `Filters.not(exactMatch)` | `$ne` | Boolean, Datetime, Number, String |
| `.hasProperty()` | `$isNull: false` | Array, Boolean, Datetime, Geopoint, GeoShape, Number, String |
| `Filters.not(hasProperty())` | `$isNull: true` | Array, Boolean, Datetime, Geopoint, GeoShape, Number, String |
| `.range().lt(x)` | `$lt` | Datetime, Number |
| `.range().lte(x)` | `$lte` | Datetime, Number |
| `.range().gt(x)` | `$gt` | Datetime, Number |
| `.range().gte(x)` | `$gte` | Datetime, Number |
| `.isTrue()` / `.isFalse()` | `$eq: true` / `$eq: false` | Boolean |
| `.matchAnyToken(...)` | `$containsAnyTerm` | String |
| `.matchAllTokens(...)` | `$containsAllTerms` | String |
| `.phrase(...)` | `$containsAllTermsInOrder` | String |
| `.phrasePrefix()`, `.prefixOnLastToken()` | `$interval`, 검색 문자열은 `$match`에 담고 `$prefixOnLastTerm: true` 지정 | String |
| `.contains(...)` | `$contains`, 내부 필터를 정확히 하나만 받음 | Array |
| `.withinDistanceOf()`, `.withinPolygon()`, `.withinBoundingBox()` | `$within` | Geopoint, GeoShape |
| `.intersectsPolygon()`, `.intersectsBoundingBox()` | `$intersects` | GeoShape |
| `.doesNotIntersectPolygon()`, `.doesNotIntersectBoundingBox()` | `$intersects`를 감싼 `$not` | GeoShape |
| `.isPresent()` | 대응하는 where 절 키 없음 | Links |

세 가지 동작 차이가 변환된 필터의 형태를 바꿉니다. TSv2 절 형태 규칙 자체는 [Filtering](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#filtering)을 확인하세요.

* **범위가 양쪽으로 정해진 필터는 절 두 개가 됩니다.** TypeScript v1의 `.range().gte(a).lte(b)` 체인은 호출 하나이지만, TypeScript v2는 속성 하나에 연산자 키를 하나만 받으므로 같은 필터가 `$and: [{ p: { $gte: a } }, { p: { $lte: b } }]`가 됩니다.
* **여러 값을 받는 `.contains()`는 `$or`가 됩니다.** TypeScript v1의 `.contains()`는 여러 값을 받아 그중 하나라도 일치하면 매치하지만, TypeScript v2의 `$contains`는 내부 필터를 정확히 하나만 받습니다.
* **Datetime 비교는 ISO 8601 문자열을 받습니다.** 예: `{ $gt: "2010-10-01T00:00:00Z" }`.

**설명**: `.where()`에 넘기는 절 객체는 SQL의 `WHERE` 조건을 JSON 형태로 쓴 것입니다. 예를 들어 `client(Aircraft).where({ capacity: { $gte: 100 } })`는 `WHERE capacity >= 100`에 해당하고, 100 이상 200 이하라면 위 규칙대로 `$and`로 두 절을 묶어 `WHERE capacity >= 100 AND capacity <= 200`을 표현합니다. 같은 원리로 배열 속성 `tags`에 "a" 또는 "b"가 들어 있는 객체를 찾으려면 `$contains` 절 두 개를 `$or`로 묶어야 합니다.

> **중간 요약**: v1의 타입별 `.filter()` 메서드는 v2의 단일 `.where()` 절 객체로 바뀝니다. 양쪽 범위 조건은 `$and`, 여러 값의 `contains`는 `$or`로 풀어 써야 하고, 날짜 비교는 ISO 8601 문자열을 쓰며, 링크 존재 여부(`.isPresent()`) 필터에는 대응 키가 없습니다.

<a id="link-traversal-mapping"></a>
### 링크 탐색 매핑 (Link traversal mapping)

TypeScript v1은 각 객체 인터페이스에 링크 타입마다 필드를 하나씩 생성하고, 객체 집합에는 링크 타입마다 `searchAround` 메서드를 하나씩 생성합니다. TypeScript v2는 링크별 접근자를 `$link` 아래에 넣고, `searchAround` 계열 전체를 단일 `pivotTo()` 메서드로 대체합니다.

| TypeScript v1 | TypeScript v2 |
|---|---|
| `SingleLink` 필드, `.get()` 또는 `.getAsync()`로 읽음 | `$link.{linkApiName}.fetchOne()`, 또는 예외를 던지는 대신 `{ value }` / `{ error }` 래퍼를 받으려면 `fetchOneWithErrors()`. 링크된 객체가 없을 때의 동작이 바뀐다는 점에 유의하세요. `.get()`은 `undefined`를 반환하지만, `fetchOne()`은 예외를 던지고 `fetchOneWithErrors()`는 `{ error }`를 보고하며 이는 다른 실패와 구별되지 않습니다 |
| `MultiLink` 필드, `.all()` 또는 `.allAsync()`로 읽음 | `$link.{linkApiName}`. 이미 `ObjectSet`이므로 `asyncIter()`로 순회 |
| 객체 집합의 `searchAround<LinkApiName>()` | `pivotTo("<linkApiName>")` |

링크 API 이름을 `searchAround` 메서드 이름에서 유추하지 마세요. 메서드 이름은 링크 API 이름을 확실하게 보존하지 않습니다. 대신 링크 API 이름을 직접 찾아보세요. 생성된 TypeScript v2 SDK에서 객체 타입의 `$link` 컨테이너 키가 정확히 링크 API 이름이며, `pivotTo()`는 그 값을 그대로 받습니다. 예를 들어 API 이름이 `toOtherObjectType`인 링크는 `pivotTo("toOtherObjectType")`로 탐색합니다.

TypeScript v1은 단일 객체 인스턴스에서 도달한 링크로 할 수 있는 일도 제한합니다. `MultiLink`는 객체 집합으로 변환할 수 없으므로 먼저 객체로부터 객체 집합을 다시 만들어야 합니다. TypeScript v2에서는 다중(many) 카디널리티의 `$link` 항목이 이미 `ObjectSet`이고 `pivotTo()`도 객체 집합을 반환하므로 바로 체이닝할 수 있습니다. TSv2 API 자체는 TypeScript OSDK 레퍼런스의 [Links](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#links)를 확인하세요.

**설명**: 링크 탐색은 SQL의 조인으로 관련 행을 찾아가는 것에 해당합니다. 예를 들어 Flight와 Aircraft가 링크되어 있을 때, 특정 항공편 객체 `flight`에서 `flight.$link.aircraft.fetchOne()`은 그 항공편에 배정된 항공기 하나를 가져옵니다(일대일 방향이므로 `SingleLink`). 반대로 "JFK에서 출발하는 모든 항공편의 항공기들"처럼 객체 집합 전체에서 링크된 객체 집합으로 건너가려면 `client(Flight).where({ origin: "JFK" }).pivotTo("aircraft")`처럼 씁니다. 이는 `SELECT a.* FROM flights f JOIN aircraft a ON f.aircraft_id = a.aircraft_id WHERE f.origin = 'JFK'`에 해당합니다.

> **중간 요약**: v2에서는 단일 링크를 `$link.<이름>.fetchOne()`으로 읽고(없으면 예외), 다중 링크는 이미 객체 집합이며, 객체 집합 간 탐색은 `pivotTo("<링크 API 이름>")` 하나로 합니다. 링크 API 이름은 `$link`의 키에서 확인해야 합니다.

<a id="group-by-strategy-mapping"></a>
### 그룹화 전략 매핑 (Group-by strategy mapping)

TypeScript v1은 속성 타입에 따라 선택되는 버킷 분할(bucketing) 메서드로 `.groupBy()`를 호출해 집계를 버킷으로 나눕니다. TypeScript v2는 같은 정보를 단일 `.aggregate()` 호출의 `$groupBy` 객체 안에 값으로 지정합니다. 다음 표는 각 TypeScript v1 버킷 분할 메서드를 TypeScript v2 `$groupBy` 값에 매핑합니다.

`$ranges`는 원소가 두 개인 튜플의 배열을 받고, `$duration`은 `[값, 단위]` 튜플을 받습니다. 범위는 TypeScript v1과 마찬가지로 시작값을 포함하고 끝값은 포함하지 않습니다. `"seconds"`, `"minutes"`, `"hours"`, `"days"`만 임의의 값을 받으며, 그보다 큰 단위는 `1`만 받습니다. 그룹화 전략 자체는 [Types of grouping](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#types-of-group-bys)을 확인하세요.

| TypeScript v1 | TypeScript v2 `$groupBy` 값 |
|---|---|
| `.exactValues()` | `"exact"` |
| `.exactValues({ maxBuckets: n })` | `{ $exactWithLimit: n }` |
| `.topValues()` | `"exact"` |
| `.byFixedWidth(50)` | `{ $fixedWidth: 50 }` |
| `.byRanges({ min: 0, max: 50 }, { min: 50, max: 100 })` | `{ $ranges: [[0, 50], [50, 100]] }` |
| `.byYear()` | `{ $duration: [1, "years"] }` |
| `.byQuarter()` | `{ $duration: [1, "quarters"] }` |
| `.byMonth()` | `{ $duration: [1, "months"] }` |
| `.byWeek()` | `{ $duration: [1, "weeks"] }` |
| `.byDays(n)` | `{ $duration: [n, "days"] }` |
| `.byHours(n)`, `.byMinutes(n)`, `.bySeconds(n)` | `{ $duration: [n, "hours"] }`, `{ $duration: [n, "minutes"] }`, `{ $duration: [n, "seconds"] }` |
| `.segmentBy(...)` | 같은 `$groupBy` 객체 안의 두 번째 키 |

정확한 값(exact-value) 기준 그룹화 요청에는 항상 최대 버킷 수가 붙으며, 기본값은 버전마다 다릅니다. TypeScript v1의 `.topValues()`는 기본값이 1,000이고, TypeScript v2의 `"exact"`는 10,000입니다. 결과는 속성의 고유값(distinct value) 개수가 그 수 안에 들어올 때만 정확합니다. 그 수를 넘으면 일부 객체가 반환된 그룹에서 빠지고 집계는 근사값이 됩니다. 플랫폼은 모든 응답에서 결과가 정확한지 근사인지를 알려 주지만, TypeScript OSDK는 그 필드를 노출하지 않으므로 TypeScript v2 함수 안에서는 근사 결과가 정확한 결과와 똑같이 보입니다. 카디널리티가 높은 속성이라면 `{ $exactWithLimit: n }`으로 버킷 수를 늘리거나, 먼저 `.where()`로 객체 집합을 좁히세요. Boolean 속성은 고유값이 최대 두 개뿐이므로 `"exact"`가 항상 정확합니다.

**설명**: 그룹화는 SQL의 `GROUP BY`에 해당합니다. 예를 들어 `$groupBy: { manufacturer: "exact" }`는 `GROUP BY manufacturer`처럼 제조사 값마다 버킷을 하나씩 만들고, `$groupBy: { capacity: { $fixedWidth: 50 } }`는 좌석 수를 0\~49, 50\~99, ... 처럼 폭 50인 구간으로 나눕니다. 카디널리티(cardinality)는 속성이 가지는 서로 다른 값의 개수입니다. 고유값이 15,000개인 속성을 `"exact"`로 그룹화하면 버킷 상한 10,000을 넘으므로, 경고 없이 일부 데이터가 빠진 결과를 받게 됩니다.

> **중간 요약**: v1의 `.groupBy()` 버킷 분할 메서드는 v2에서 `.aggregate()`의 `$groupBy` 값(`"exact"`, `$fixedWidth`, `$ranges`, `$duration` 등)으로 바뀝니다. exact 그룹화의 기본 버킷 상한은 v2에서 10,000이며, 이를 넘으면 결과가 근사가 되지만 v2 함수 안에서는 알 수 없습니다.

<a id="aggregation-metric-mapping"></a>
### 집계 지표 매핑 (Aggregation metric mapping)

TypeScript v1은 객체 집합을 그룹화한 뒤 `.count()`나 `.average()` 같은 집계 메서드를 호출해 지표를 계산합니다. TypeScript v2는 단일 `.aggregate()` 호출의 `$select` 객체로 지표를 선택합니다. 다음 표는 각 TypeScript v1 집계 메서드를 TypeScript v2 `$select` 키에 매핑합니다.

개수(count)가 아닌 모든 키는 `"<propertyApiName>:<metric>"` 형태의 문자열이고, 모든 값은 정렬 지시어인 `"unordered"`, `"asc"`, `"desc"` 중 하나입니다. 숫자 속성은 모든 접미사를 받습니다. 날짜(datetime)와 타임스탬프 속성은 `min`, `max`, `approximateDistinct`, `exactDistinct`만 받고, 그 밖의 타입은 고유값 개수를 세는 두 접미사만 받습니다. 집계 개념은 TypeScript OSDK 레퍼런스의 [Aggregations](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#aggregations)를 확인하세요.

| TypeScript v1 | TypeScript v2 `$select` 키 |
|---|---|
| `.count()` | `$count: "unordered"` |
| `.average(e => e.p)` | `"p:avg": "unordered"` |
| `.max(e => e.p)` | `"p:max": "unordered"` |
| `.min(e => e.p)` | `"p:min": "unordered"` |
| `.sum(e => e.p)` | `"p:sum": "unordered"` |
| `.cardinality(e => e.p)` | `"p:approximateDistinct": "unordered"` |
| TypeScript v1에 대응 기능 없음 | `"p:exactDistinct": "unordered"` |

변환된 호출의 형태에 영향을 주는 차이가 하나 있습니다. `.aggregate()`는 정확히 두 개의 키, 즉 필수인 `$select`와 선택인 `$groupBy`만 가진 요청 객체 하나를 받습니다. `where` 키가 없으므로 `.aggregate()`를 호출하기 전에 `.where()`를 체이닝해 객체 집합을 필터링하세요.

결과의 형태도 바뀌므로, 변환된 함수는 자신의 출력을 다르게 읽어야 합니다. `$select` 지시어, 정렬 제한, 그룹화된 결과를 읽는 방법은 [Aggregations](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#aggregations)를 확인하세요.

**설명**: 지표는 SQL의 집계 함수(`COUNT`, `AVG`, `MAX`, `MIN`, `SUM`, `COUNT(DISTINCT ...)`)에 해당합니다. 예를 들어 `client(Aircraft).where({ status: "active" }).aggregate({ $select: { "capacity:avg": "unordered" }, $groupBy: { manufacturer: "exact" } })`는 `SELECT manufacturer, AVG(capacity) FROM aircraft WHERE status = 'active' GROUP BY manufacturer`와 같은 질의입니다. `approximateDistinct`는 빠르지만 근사인 고유값 개수, `exactDistinct`는 정확한 고유값 개수입니다.

> **중간 요약**: v2에서는 집계 지표를 `$select`의 `"속성:지표"` 키로 지정하고, 필터는 `.aggregate()` 앞에 `.where()`로 체이닝합니다. 날짜와 타임스탬프 속성에는 `min`, `max`, 고유값 개수만 쓸 수 있습니다.

<a id="capabilities-with-no-typescript-v2-equivalent"></a>
### TypeScript v2에 대응 기능이 없는 기능 (Capabilities with no TypeScript v2 equivalent)

일부 TypeScript v1 조회 기능은 TypeScript v2에 대응하는 기능이 없으므로, 검색이나 집계를 변환하기 전에 미리 대비하세요.

<a id="filtering"></a>
#### 필터링 (Filtering)

* **링크 존재 여부 필터에는 where 절 키가 없습니다.** TypeScript v1에서 `.isPresent()`는 객체 집합을 주어진 타입의 링크된 객체가 하나 이상 있는 객체로, 부정하면 하나도 없는 객체로 필터링합니다. TypeScript v2에는 이를 수행하는 `$` 키가 없습니다. 가장 가까운 방법은 파생 속성(derived property)입니다. 링크된 객체 수를 세는 파생 속성을 정의한 다음 그 개수가 0보다 큰 것으로 필터링합니다. 이 방법은 지원되는 대응 기능이 아니라 우회 방법이므로, 의존하기 전에 실제 데이터로 테스트하세요.
* **`Fuzziness` 편집 거리는 TypeScript v2에 대응 형태가 없습니다.** TypeScript v2의 단어(term) 연산자 `$containsAnyTerm`과 `$containsAllTerms`는 단순한 `fuzzySearch` 불리언만 받고 편집 거리 제어를 제공하지 않으므로, `Fuzziness.LEVENSHTEIN_ONE`과 `Fuzziness.LEVENSHTEIN_TWO`에는 직접 대응하는 TypeScript v2 형태가 없습니다. `$containsAllTermsInOrder`는 퍼지(fuzzy) 옵션을 아예 받지 않습니다. `$interval` 키는 편집 거리를 담는 `$fuzzy`와 `$fuzziness` 하위 키를 제공하므로, 의존하기 전에 실제 데이터로 이 구성을 테스트하세요.

**설명**: 편집 거리(Levenshtein distance)는 한 문자열을 다른 문자열로 바꾸는 데 필요한 문자 삽입, 삭제, 교체의 최소 횟수입니다. 예를 들어 "boeing"과 "boing"의 편집 거리는 1입니다. `LEVENSHTEIN_ONE`은 편집 거리 1 이내의 오타까지 일치로 인정하는 퍼지 검색 설정입니다.

<a id="grouping"></a>
#### 그룹화 (Grouping)

* **한쪽이 열린 범위 버킷이 없어졌습니다.** TypeScript v1에서는 `min`이나 `max`를 생략해 음의 무한대부터 `max`까지, 또는 `min`부터 무한대까지의 버킷을 만들 수 있습니다. TypeScript v2의 `$ranges` 튜플은 양쪽 끝값을 모두 요구합니다.
* **TypeScript v2에서는 `Long` 속성을 그룹화할 수 없습니다.** TypeScript v1은 `Long`을 그룹화 가능한 숫자 타입에 포함하지만, TypeScript v2 타입은 `Long` 속성에 대한 `$groupBy` 값을 제공하지 않습니다.
* **TypeScript v2에서는 배열 속성 기준 그룹화가 지원되지 않습니다.** TypeScript v1은 배열 속성에 그 원소 타입과 같은 버킷 분할 메서드를 제공합니다. TypeScript v2 타입은 `$groupBy`에 배열 속성을 받아들이므로 이 실수가 컴파일은 되지만, 결과는 보장되지 않습니다. 대신 스칼라 속성으로 그룹화하세요.
* **TypeScript v2에는 `segmentBy`가 없습니다.** TypeScript v1은 `.groupBy()` 다음에 `.segmentBy()`를 호출해 두 속성으로 버킷을 나눈 3차원 집계를 계산합니다. TypeScript v2의 대응 방법은 같은 `$groupBy` 객체의 두 번째 키이지만, 반환 형태가 같지 않습니다. TypeScript v1은 중첩된 버킷을 만들고, TypeScript v2는 행들의 평평한(flat) 배열을 반환하며 각 행은 모든 그룹화 키의 값을 담은 `$group` 객체를 가집니다. 따라서 3차원 집계를 반환해야 하는 함수는 중첩 구조를 직접 다시 만들어야 합니다. 각 버전이 기대하는 형태는 [집계 타입(Aggregation types)](../04_types-reference.md#aggregation-types)을 참고하세요.

**설명**: 예를 들어 제조사와 연도 두 속성으로 그룹화하면, v1은 `{ Boeing: { 2020: 12, 2021: 15 }, Airbus: { ... } }`처럼 바깥 버킷 안에 안쪽 버킷이 들어 있는 중첩 구조를 만듭니다. v2는 `[{ $group: { manufacturer: "Boeing", year: 2020 }, $count: 12 }, { $group: { manufacturer: "Boeing", year: 2021 }, $count: 15 }, ...]`처럼 SQL `GROUP BY manufacturer, year`의 결과 행 목록과 같은 평평한 배열을 돌려줍니다(예시 값은 설명을 위한 것입니다).

<a id="aggregation-metrics"></a>
#### 집계 지표 (Aggregation metrics)

* **날짜나 타임스탬프의 평균은 TypeScript v1에서만 가능합니다.** TypeScript v1의 `.average()`는 타임스탬프와 날짜 속성을 받습니다. TypeScript v2는 날짜나 타임스탬프 속성에 `min`, `max`, `approximateDistinct`, `exactDistinct`만 제공하므로 `avg`도 `sum`도 쓸 수 없습니다.
* **TypeScript v2에는 지표 별칭(aliasing)이 없습니다.** 결과 키는 항상 속성과 지표로부터 만들어지므로, `$count`나 `"property:metric"` 문자열이 아닌 `$select` 키는 타입 오류가 됩니다.

<a id="ordering-and-loading"></a>
#### 정렬과 로딩 (Ordering and loading)

* **TypeScript v2에는 `.take()`나 `.limit()`이 없습니다.** 정렬은 더 이상 체이닝되는 절이 아닙니다. `fetchPage()`나 `asyncIter()`의 옵션 객체 안에 `$orderBy`로 들어가며, 결과 개수는 같은 옵션 객체의 `$pageSize`로 제한합니다.
* **TypeScript v2에는 `.all()`이 없습니다.** TypeScript v1의 `.all()`과 `.allAsync()`는 객체 집합 전체를 한 번에 메모리에 구체화합니다. TypeScript v2는 [객체를 메모리에 로드하기](#load-objects-into-memory)에서 설명하듯 `asyncIter()`로 순회하거나 `fetchPage()`로 한 페이지를 읽습니다.
* **최근접 이웃(nearest-neighbor) 한도가 넓어졌습니다.** TypeScript v1은 `k` 값을 `0 < K <= 100`으로 제한하지만, TypeScript v2의 `nearestNeighbors()` 메서드는 1에서 500 사이의 `numNeighbors`를 받습니다. 따라서 범위 상한에서 검색하던 TypeScript v1 코드는 마이그레이션 후 다섯 배 많은 이웃을 요청할 수 있습니다.
* **관련도(relevance) 정렬은 최근접 이웃 검색에서만 동작합니다.** TypeScript v2에서 `$orderBy: "relevance"`는 `nearestNeighbors()` 검색에 적용되며, 이때 `numNeighbors`가 결과 수를 제한하고 반환된 각 객체에 `$score`가 붙습니다. 단어 일치(token-match) `where` 절에는 효과가 없으므로, `.matchAnyToken()`으로 필터링하고 관련도로 정렬한 뒤 처음 N개를 가져오는 TypeScript v1 패턴에는 TypeScript v2 대응 방법이 없습니다.

**설명**: 최근접 이웃 검색은 벡터 임베딩(텍스트 등을 수치 벡터로 바꾼 것) 속성에서 질의 벡터와 가장 가까운 벡터를 가진 객체 k개를 찾는 검색입니다. "의미가 비슷한 문서 찾기" 같은 시맨틱 검색에 쓰이며, `$score`는 질의와의 유사도 점수입니다. 페이지 단위 조회(`fetchPage()`)는 SQL의 `ORDER BY ... LIMIT n`을 페이지마다 이어서 가져오는 방식에 해당합니다.

> **중간 요약**: v2로 옮길 수 없는 기능으로 링크 존재 여부 필터, 편집 거리 지정 퍼지 검색, 열린 범위 버킷, `Long`과 배열 속성 그룹화, `segmentBy`의 중첩 결과, 날짜 평균, 지표 별칭, `.take()`/`.limit()`/`.all()`, 단어 일치 검색의 관련도 정렬이 있습니다. 정렬과 개수 제한은 `fetchPage()`/`asyncIter()` 옵션으로 옮겨 갑니다.

<a id="identify-objects"></a>
## 객체 식별하기 (Identify objects)

TypeScript v1은 객체의 식별 정보를 `rid`, `primaryKey`, `typeId` 필드로 노출합니다. TypeScript v2는 객체 자신의 속성과 구분하기 위해 모든 내장 식별자 필드 앞에 `$`를 붙이고, 객체 타입과 기본 키(primary key)를 함께 인코딩한 단일 문자열인 `$objectSpecifier`를 추가합니다. `$rid`는 읽기 요청에서 `$includeRid: true`로 명시적으로 요청할 때만 존재하므로, TypeScript v2에서 식별 로직의 기준으로는 `$rid`가 아니라 `$objectSpecifier`를 사용하세요.

<a id="identifier-reference"></a>
### 식별자 레퍼런스 (Identifier reference)

다음 표는 각 TypeScript v1 식별자와 타입을 TypeScript v2 대응 항목에 매핑합니다.

| TypeScript v1 | TypeScript v2 | 비고 |
|---------------|---------------|-------|
| `obj.rid` | `obj.$rid` | 읽기 요청에 `$includeRid: true`를 넘길 때만 존재합니다. |
| `obj.primaryKey` | `obj.$primaryKey` | 항상 존재합니다. |
| `obj.typeId` | `obj.$apiName` 또는 `obj.$objectType` | 항상 존재합니다. 둘 다 객체 타입 API 이름을 담지만, `$apiName`만 리터럴 타입입니다. |
| 없음 | `obj.$objectSpecifier` | 항상 존재합니다. `"<apiName>:<primaryKey>"` 형태의 문자열입니다. |
| `Employee` | `Osdk.Instance<Employee>` | 로드된 객체 인스턴스의 타입입니다. |
| `OntologyObject` | 대응 항목 없음 | `@osdk/api`의 `OsdkBase`가 가장 가까운 타입입니다. |
| `IsOntologyObject` | 대응 항목 없음 | 직접적인 대체 없이 제거되었습니다. |
| 객체를 키로 쓰는 `FunctionsMap<T, V>` | `Record<ObjectSpecifier<T>, V>` | 스칼라 키를 쓰는 `FunctionsMap`은 일반 `Record<K, V>`가 됩니다. [객체 매핑(Object mappings)](../13_functions-on-objects/03_object-identifiers.md#object-mappings)을 참고하세요. |

마이그레이션하면 두 객체의 동등성 비교가 더 간단해집니다. TypeScript v1에서는 기본 키가 단일 객체 타입 안에서만 유일하므로 `typeId`와 `primaryKey`를 둘 다 비교해야 합니다. TypeScript v2는 두 값을 `$objectSpecifier`에 함께 인코딩하므로, 같은 검사를 문자열 비교 한 번으로 할 수 있으며 두 객체의 객체 타입이 달라도 올바르게 동작합니다.

```typescript tab="TypeScript v2"
function isEqual(o1: { $objectSpecifier: string }, o2: { $objectSpecifier: string }): boolean {
    return o1.$objectSpecifier === o2.$objectSpecifier;
}
```

**설명**: 기본 키는 데이터베이스 테이블 안에서만 유일합니다. 예를 들어 Employee 테이블에도 키 `"42"`인 행이 있고 Aircraft 테이블에도 키 `"42"`인 행이 있을 수 있으므로, 기본 키만 비교하면 서로 다른 두 객체를 같다고 잘못 판단합니다. `$objectSpecifier`는 `"Employee:42"`, `"Aircraft:42"`처럼 타입 이름과 키를 이어 붙인 문자열이므로, 이 문자열 하나만 비교하면 (테이블, 기본 키) 쌍 전체를 비교한 것과 같은 효과를 냅니다. 같은 이유로 객체를 키로 하는 맵을 만들 때도 이 문자열을 키로 씁니다.

두 버전에서 객체를 키로 쓰는 맵의 실제 예제는 타입 레퍼런스의 [Map](../04_types-reference.md#map)을 확인하세요. 두 예제의 TypeScript v1 형태와, 객체 동등성에 주의가 필요한 개념적 배경은 [객체 식별자(Object identifiers)](../13_functions-on-objects/03_object-identifiers.md)를 확인하세요.

> **중간 요약**: v2의 내장 식별자 필드는 `$`로 시작하며(`$primaryKey`, `$apiName` 등), `$rid`는 요청할 때만 채워집니다. 객체 동등성 비교와 객체 키 맵에는 타입과 기본 키를 합친 `$objectSpecifier`를 씁니다.

<a id="edit-the-ontology"></a>
## 온톨로지 편집하기 (Edit the Ontology)

TypeScript v1에서 온톨로지 편집 함수를 작성하려면 `@foundry/functions-api` 패키지의 `@OntologyEditFunction()` 데코레이터를 붙이고 반환 타입을 `void`로 지정해야 합니다. 또한 [`@Edits decorator`](../12_typescript-v1/03_api-ontology-edits.md#the-edits-decorator)를 적용해 편집하는 모든 객체 타입을 미리 선언해야 하며, 이를 통해 함수 기반 액션(function-backed action)이 호출되기 전에 해당 객체 타입에 대한 권한을 검사할 수 있습니다.

```typescript tab="TypeScript v1"
import { Edits, OntologyEditFunction } from "@foundry/functions-api";
import { Aircraft, Employee } from "@foundry/ontology-api";

export class MyOntologyEditFunctions {

    @Edits(Aircraft, Employee)
    @OntologyEditFunction()
    public myFunction(aircraft: Aircraft, employee: Employee): void {
        aircraft.businessCapacity = 3;
        employee.department = "HR";
    }
}
```

TypeScript v2에서는 `@osdk/functions` 패키지에서 `createEditBatch` 함수를 가져와, 실행되는 동안 사용할 편집 저장소를 만들어야 합니다. 또한 `Edits` 타입을 사용해 함수가 편집할 수 있는 엔터티를 선언해야 합니다. 이는 컴파일 시점에 타입 안전성을 강제합니다. `Edits` 타입에 포함되지 않은 타입의 객체나 링크를 편집하려고 하면 TypeScript 컴파일러가 오류를 반환합니다.

```typescript tab="TypeScript v2"
import { createEditBatch, Edits } from "@osdk/functions";
import { Aircraft, Employee } from "@ontology/sdk";
import { Client, Osdk } from "@osdk/client";

type OntologyEdit = Edits.Object<Aircraft> | Edits.Object<Employee>;

export default function myFunction(
    client: Client, 
    aircraft: Osdk.Instance<Aircraft>, 
    employee: Osdk.Instance<Employee>
): OntologyEdit[] {

    const batch = createEditBatch<OntologyEdit>(client);

    batch.update(aircraft, { businessCapacity: 3 });
    batch.update(employee, { department: "HR" });

    return batch.getEdits();
}
```

**설명**: 두 함수 모두 항공기 객체 하나와 직원 객체 하나를 입력으로 받아, 항공기의 `businessCapacity`를 3으로, 직원의 `department`를 "HR"로 바꾸는 편집(edit)을 만듭니다. v1은 객체 필드에 값을 직접 대입하는 방식이고, 플랫폼이 그 대입을 몰래 기록합니다. v2는 `createEditBatch`로 만든 `batch`에 `update(대상 객체, { 바꿀 속성: 새 값 })`을 명시적으로 쌓고, 마지막에 `batch.getEdits()`로 편집 목록을 반환합니다. `type OntologyEdit = Edits.Object<Aircraft> | Edits.Object<Employee>`는 "이 함수는 Aircraft와 Employee만 편집한다"는 선언이며, 여기에 없는 타입을 `batch`로 편집하려 하면 컴파일 오류가 납니다. v1의 `@Edits(Aircraft, Employee)`가 하던 역할을 타입 시스템이 맡는 것입니다.

TypeScript v2에서는 `Edits.Interface<MyInterface>`를 사용해 [온톨로지 인터페이스](../../05_interfaces/01_interface-overview.md) 속성을 통해 객체를 생성, 수정, 삭제할 수 있습니다. 자세한 내용은 [온톨로지 편집(Ontology edits)](04_typescript-v2-ontology-edits.md)을 참고하세요.

TypeScript v1에서는 함수가 실행되는 동안 편집이 온톨로지에 적용*되지 않습니다*. [편집과 객체 검색 문서](../09_language-agnostic-features/01_edits-overview.md#edits-and-object-search)에서 설명하듯, 객체와 링크에 대한 변경은 함수 실행이 끝난 뒤에만, 그리고 함수 기반 액션 안에서 호출된 경우에만 전파됩니다.

TypeScript v2는 이 동작을 더 명시적으로 만듭니다. 편집을 암묵적으로 누적하는 대신, 함수가 편집 배치(edit batch)로 편집을 추적하고 완료 시 반환해야 합니다.

TypeScript v2에서 지원되는 전체 작업 목록은 TypeScript v2 문서의 [온톨로지 편집(Ontology edits)](04_typescript-v2-ontology-edits.md) 섹션을 참고하세요.

TypeScript v2는 쓰기 후 읽기(read-after-write)를 보장하는 대안 실행 모델인 [스테이징된 쓰기(staged writes)](05_typescript-v2-staged-writes.md)도 지원합니다. 스테이징된 쓰기 함수는 `createEditBatch` 대신 `WriteableClient`를 사용하며, 편집을 명시적으로 반환할 필요가 없습니다.

> **중간 요약**: v1은 데코레이터(`@OntologyEditFunction`, `@Edits`)와 필드 대입으로 편집하고, v2는 `Edits` 타입으로 편집 대상을 선언한 뒤 `createEditBatch`로 편집을 쌓아 `getEdits()`로 반환합니다. 두 버전 모두 편집은 함수 실행이 끝난 뒤 액션을 통해서만 적용됩니다. 쓰기 후 읽기가 필요하면 v2의 staged writes를 쓸 수 있습니다.

<a id="generate-unique-ids-for-objects"></a>
## 객체용 고유 ID 생성하기 (Generate unique IDs for objects)

TypeScript v1에서 새로 만든 객체의 고유 ID를 생성하려면 `@foundry/functions-utils` 패키지의 `Uuid` 유틸리티를 사용합니다. TypeScript v2는 완전한 Node.js 환경에서 실행되므로 대신 `node:crypto` 코어 모듈을 사용할 수 있습니다.

```typescript tab="TypeScript v2"
import { FlightScenario } from "@ontology/sdk";
import { Client } from "@osdk/client";
import { createEditBatch, Edits } from "@osdk/functions";
import { randomUUID } from "node:crypto";

type OntologyEdit = Edits.Object<FlightScenario>;

export default function createFlightScenario(client: Client): OntologyEdit[] {

    const batch = createEditBatch<OntologyEdit>(client);

    batch.create(FlightScenario, { 
        id: randomUUID(),
        scenarioName: "New scenario",
    });

    return batch.getEdits();
}
```

(원문에는 `Uuid.random()`과 `Objects.create().flightScenarios(...)`로 같은 객체를 만드는 TypeScript v1 예제 코드도 있습니다.)

**설명**: 이 함수는 입력 없이 새 FlightScenario 객체 하나를 생성하는 편집을 반환합니다. `batch.create(객체 타입, { 속성 값들 })`에서 기본 키 속성 `id`에 `randomUUID()`가 만든 UUID(예: `"3f2b8c1e-..."` 형태의 128비트 무작위 식별자)를 넣어, 다른 객체와 기본 키가 겹치지 않게 합니다.

**주의**: 모듈 최상위(함수 본문 밖)에서 `randomUUID`나 다른 무작위 값 생성기를 호출하지 마세요. TypeScript v2 함수는 웜 호출(warm invocation)을 사용하는데, 모든 모듈 수준 코드는 초기화 중에 한 번만 평가되고 이후 호출에서 재사용됩니다. 따라서 모듈 수준의 `randomUUID` 호출은 한 번만 평가되어 모든 웜 호출에서 같은 값을 만들어 냅니다. 고유성을 보장하려면 항상 함수 본문 안에서 무작위 값을 생성하세요.

**설명**: 예를 들어 파일 맨 위에 `const ID = randomUUID();`를 두고 함수 안에서 `ID`를 쓰면, 첫 번째 호출과 두 번째 호출이 같은 ID로 객체를 만들려고 해 기본 키 충돌이 납니다. 프로세스가 한 번 띄워진 뒤 여러 요청을 처리하는 서버 환경에서는 모듈 코드가 프로세스 시작 시 한 번만 실행되기 때문입니다.

> **중간 요약**: v2에서는 Node.js 표준 `node:crypto`의 `randomUUID()`로 새 객체의 ID를 만듭니다. 웜 호출 때문에 반드시 함수 본문 안에서 호출해야 합니다.

<a id="load-objects-into-memory"></a>
## 객체를 메모리에 로드하기 (Load objects into memory)

TypeScript v1 함수는 특정 타입의 모든 객체를 메모리에 로드해 처리하는 `.all()`과 `.allAsync()` API를 제공합니다. 그러나 이 방식은 온톨로지의 객체 수가 늘어날수록 메모리 사용량이 높아지고 성능이 느려질 수 있습니다.

```typescript tab="TypeScript v1"
import { Edits, OntologyEditFunction } from "@foundry/functions-api";
import { Aircraft, Objects } from "@foundry/ontology-api";

export class MyFunctions {

    @Edits(Aircraft)
    @OntologyEditFunction()
    public editAircraft(): void {

        const aircraft = Objects.search().aircraft().all();

        aircraft.forEach(a => {
            a.arrived = true;
        });
    }
}
```

TypeScript v2 함수는 Ontology SDK를 통한 스트리밍 객체 처리를 지원하므로 전체 객체 집합을 한꺼번에 메모리에 둘 필요가 없습니다. 가능하면 이 방식을 권장합니다.

```typescript tab="TypeScript v2"
import { Aircraft } from "@ontology/sdk";
import { Client } from "@osdk/client";
import { createEditBatch, Edits } from "@osdk/functions";

type OntologyEdit = Edits.Object<Aircraft>;

export default async function editAircraft(client: Client): Promise<OntologyEdit[]> {

    const batch = createEditBatch<OntologyEdit>(client);
    
    for await (const a of client(Aircraft).asyncIter()) {
        batch.update(a, { arrived: true });
    }

    return batch.getEdits();
}
```

**설명**: 두 함수 모두 모든 Aircraft 객체의 `arrived` 속성을 `true`로 바꾸는 편집을 만듭니다. v1의 `.all()`은 객체 전체를 배열로 한꺼번에 받아 오므로 객체가 백만 개면 백만 개가 동시에 메모리에 올라갑니다. v2의 `asyncIter()`는 비동기 이터레이터로, 내부적으로 객체를 페이지 단위로 가져오면서 `for await` 루프에 하나씩 넘겨 줍니다. 처리가 끝난 페이지는 메모리에서 내려갈 수 있으므로 메모리 사용량이 객체 수에 비례해 커지지 않습니다(단, 이 예제에서는 편집 목록 자체는 객체 수만큼 쌓입니다).

데이터 규모가 문제가 되지 않는다면, 특정 타입의 모든 객체를 로드하는 다른 방법도 있습니다. (원문에는 `Array.fromAsync(client(Aircraft).asyncIter())`로 모든 객체를 배열로 모은 뒤 `forEach`로 편집하는 TypeScript v2 예제 코드가 더 있습니다.)

> **중간 요약**: v1의 `.all()`은 객체 전체를 한 번에 메모리에 올리지만, v2는 `asyncIter()`로 객체를 스트리밍 처리하는 방식을 권장합니다. 규모가 작다면 `Array.fromAsync()`로 한 번에 모을 수도 있습니다.

## 정리

- v2 함수는 `src/functions` 아래 파일마다 `export default` 함수 하나로 선언하며, 타입은 `@osdk/functions`, 온톨로지 접근은 생성된 Ontology SDK와 첫 번째 파라미터 `client`로 합니다.
- 날짜와 타임스탬프는 ISO 8601 문자열 타입으로 바뀌고, 일반 NPM 라이브러리를 쓸 수 있습니다.
- 조회 어휘는 `.where()` 절 객체, `$link`와 `pivotTo()`, `.aggregate()`의 `$groupBy`와 `$select`로 바뀌며, 링크 존재 필터, `segmentBy` 중첩 결과, 날짜 평균 등 일부 v1 기능은 대응 기능이 없습니다.
- `Searchable` 누락과 exact 그룹화 버킷 초과는 v2에서 컴파일 오류나 경고 없이 잘못된 결과로 나타나므로 마이그레이션 전에 점검해야 합니다.
- 객체 식별에는 `$objectSpecifier`, 편집에는 `Edits` 타입과 `createEditBatch`, ID 생성에는 함수 본문 안의 `randomUUID()`, 대량 처리에는 `asyncIter()`를 사용합니다.
