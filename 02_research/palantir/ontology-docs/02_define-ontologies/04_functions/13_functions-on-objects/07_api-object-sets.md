# API: 객체 집합 (Object sets (TSv1))

- 원문: https://www.palantir.com/docs/foundry/functions/api-object-sets/
- 사이드바 위치: Define Ontologies > Functions > Functions on objects > Object sets (TSv1)

이 페이지는 TypeScript v1 함수(function)에서 객체 집합(object set)을 다루는 API를 설명합니다. 객체 집합을 검색해 만들고, 필터링하고, 링크를 따라 다른 객체 타입으로 이동(Search Around)하고, 정렬하거나 집계하는 방법을 다룹니다. 객체를 메모리에 전부 불러오지 않고 서버 쪽에서 걸러 내고 집계하는 방식이라 대량 데이터를 다룰 때 핵심이 되는 API입니다.

이 페이지는 TypeScript v1(TSv1)을 다룹니다. TypeScript v2(TSv2)와 Python은 Ontology SDK를 통해 온톨로지(Ontology)를 질의합니다. [TypeScript](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/) 및 [Python](https://www.palantir.com/docs/foundry/ontology-sdk/python-osdk/) OSDK 레퍼런스를 참고하세요. [마이그레이션 가이드](../10_typescript-v2/03_typescript-v2-migration.md)는 각 TSv1 연산자를 TSv2 형태에 대응시켜 정리해 둡니다.

**객체 집합(object set)은** 단일 타입 객체들의 순서 없는 모음을 나타냅니다. 함수 API를 사용해 객체 집합을 필터링하고, 정의된 링크 타입을 기반으로 다른 객체 타입으로 Search Around를 수행하고, 집계 값을 계산하거나 실제 객체를 가져올 수 있습니다. 개별 객체를 함수 입력으로 전달하는 것 외에도, 객체 검색 API를 사용하면 언제든 객체 집합을 검색할 수 있습니다.

TypeScript v1에서 필터링, 정렬, 집계는 `Searchable` [렌더 힌트](../../02_object-and-link-types/09_metadata/02_metadata-render-hints.md)가 활성화된 속성(property)에서만 동작합니다. 이 속성들은 검색용으로 인덱싱되어 있기 때문입니다. 이 렌더 힌트는 Ontology Manager에서 활성화할 수 있습니다.

함수 입력으로서 객체 집합은 객체 배열보다 효율적입니다. 필요할 때까지 로딩을 미루기 때문입니다. 객체 집합을 효율적으로 사용하는 모범 사례는 [성능 최적화](../08_function-consumption/03_optimize-performance.md)를 참고하세요.

**설명**: 객체 집합은 SQL로 치면 "아직 실행하지 않은 SELECT 질의"에 해당합니다. `.filter()`를 붙이면 WHERE 조건이 추가될 뿐 데이터는 아직 오지 않고, `.all()`이나 `.take()`, `.count()` 같은 메서드를 호출할 때 비로소 서버에서 질의가 실행됩니다. 반면 객체 배열(`Flight[]`)은 이미 모든 객체를 메모리에 불러온 상태입니다. 그래서 객체 수가 많을수록 객체 집합으로 받는 편이 유리합니다. 인덱싱은 검색 속도를 높이기 위해 값을 미리 정리해 둔 자료구조를 만드는 작업으로, 인덱싱되지 않은 속성으로는 필터나 정렬을 할 수 없다는 뜻입니다.

<a id="object-search"></a>
## 객체 검색 (Object search)

`Objects.search()` 인터페이스를 사용하면 프로젝트에 가져온(import) 모든 객체 타입에 대해 검색을 시작할 수 있습니다. 이 예제에서 함수는 주어진 `airportCode`로 그 공항에서 출발한 모든 항공편을 찾습니다. 그런 다음 그 항공편들의 서로 다른 도착지를 모두 찾아 반환합니다.

TSv2에 대해서는 [Filtering](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#filtering)을 참고하세요.

```typescript tab="TypeScript v1"
import { Function } from "@foundry/functions-api";
import { Objects } from "@foundry/ontology-api";

export class FlightFunctions {
    @Function()
    public currentFlightDestinations(airportCode: string): Set<string> {
        const flightsFromAirport = Objects.search()
            .flights()
            .filter(flight => flight.departureAirportCode.exactMatch(airportCode))
            .all();

        const destinations = flightsFromAirport.map(flight => flight.arrivalAirportCode!);

        return new Set(destinations);
    }
}
```

**설명**: 입력은 공항 코드 문자열(예: `"JFK"`) 하나이고 출력은 도착 공항 코드의 집합(`Set<string>`)입니다. `Objects.search().flights()`가 Flight 객체 타입 전체를 대상으로 하는 객체 집합을 만들고, `.filter(...)`가 `departureAirportCode = airportCode` 조건을 붙이며, `.all()`이 조건에 맞는 객체를 실제로 불러와 배열로 돌려줍니다. 이후 `map`으로 도착 공항 코드만 뽑고 `Set`으로 중복을 제거합니다. SQL로는 `SELECT DISTINCT arrivalAirportCode FROM flights WHERE departureAirportCode = ?`와 같은 결과입니다.

객체 집합은 객체 목록, 객체 리소스 식별자 목록, 또는 객체 집합 리소스 식별자를 검색 대상 객체 타입의 인자로 전달하여 만들 수도 있습니다. 예: `Objects.search().flights([flight])`.

특정 타입의 객체 집합을 얻고 나면, 아래에 설명된 다양한 연산을 그 집합에 수행할 수 있습니다.

> **중간 요약**: `Objects.search().객체타입()`으로 객체 집합을 만들고, 그 위에 필터, Search Around, 정렬, 집계 같은 연산을 이어 붙입니다. TSv1에서 이 연산들은 `Searchable`로 인덱싱된 속성에서만 동작합니다.

<a id="filtering"></a>
## 필터링 (Filtering)

TypeScript v1에서 객체 집합의 `.filter()` 메서드를 사용하면 객체의 검색 가능한 속성을 기준으로 객체 집합을 필터링할 수 있습니다. filter 메서드는 필터 정의를 받으며, 이 정의는 필터링하려는 속성의 타입에 따라 달라집니다. TypeScript v2의 대응 형태는 마이그레이션 가이드의 [필터 연산자 매핑](../10_typescript-v2/03_typescript-v2-migration.md#filter-operator-mapping) 표를 참고하세요. TypeScript v1 필터 메서드는 다음과 같습니다.

* 모든 속성 타입은 `.exactMatch()` 필터를 지원합니다. 이 필터는 해당 속성 값이 정확히 일치하는 객체만 남깁니다. 문자열의 정확한 일치를 찾거나(위 예제처럼), 객체의 기본 키(primary key)로 필터링할 때 유용합니다(예: `.filter(object => object.primaryKey.exactMatch(PrimaryKey))`).
  * 속성이 `null` 또는 `undefined`인지 확인하려면 `hasProperty()` 메서드를 사용합니다.
  * 여러 값을 전달하려면 전개 연산자를 사용합니다: `.exactMatch(...listVariable)`. 빈 배열을 전달하면 필터가 무시됩니다.
* 문자열 속성은 여러 키워드 필터를 지원합니다. 각 메서드의 자세한 내용은 Code Assist의 문서를 참고하세요.
  * `.phrase()`는 검색어를 토큰(보통 개별 단어)으로 나눕니다. 모든 토큰을 순서대로, 그 사이에 다른 토큰 없이 포함하는 값만 남깁니다. 밑줄과 마침표는 속성 값을 별도 토큰으로 나누지 않습니다. 예를 들어 `banana`로 검색하면 `banana_pudding`이나 `banana.pudding`은 반환되지 않습니다.
  * `.phrasePrefix()`는 `phrase()`와 거의 같지만, 마지막 토큰은 그 토큰으로 시작하는 토큰과도 일치합니다. 예를 들어 `fresh banana`로 `.phrasePrefix()` 검색을 하면 속성 값 `fresh banana_pudding`과 일치하지만 `banana_pudding fresh`와는 일치하지 않습니다. `pudding`으로 `.phrasePrefix()` 검색을 하면 속성 값 `banana_pudding`과 일치하지 않습니다.
  * `.prefixOnLastToken()`은 검색어를 토큰으로 나눈 뒤, 주어진 토큰을 모두 포함하는 값만 남깁니다. 이때 마지막 토큰은 그 토큰으로 시작하는 토큰과도 일치합니다. 예를 들어 `big app`은 `big apples`와도, `apples from the big tree`와도 일치하지만 `apples from the biggest tree`와는 일치하지 않습니다.
  * `.matchAnyToken()`, `.fuzzyMatchAnyToken()`은 검색어를 토큰으로 나눈 뒤, 주어진 토큰 중 하나라도 포함하는 값만 남깁니다. `fuzzy` 버전은 근사한 값도 일치로 인정합니다.
  * `.matchAllTokens()`, `.fuzzyMatchAllTokens()`는 검색어를 토큰으로 나눈 뒤, 주어진 토큰을 모두 포함하는 값만 남깁니다. `fuzzy` 버전은 근사한 값도 일치로 인정합니다.
    * Fuzzy 필터는 `@foundry/functions-api`에서 가져온 선택적 `Fuzziness` 파라미터를 받을 수 있습니다.
    * 사용 가능한 `Fuzziness` 옵션의 설명은 [ElasticSearch 문서 ↗](https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#fuzziness)에서 볼 수 있습니다. 아래에도 추가 정보가 있습니다.
* 숫자, 날짜, 타임스탬프 속성은 `.range()` 필터를 지원합니다.
  * 범위 필터에는 `.lt()`, `.lte()`, `.gt()`, `gte()` 메서드가 있으며, 각각 미만, 이하, 초과, 이상 비교를 수행합니다.
* 불리언 속성은 `.isTrue()`와 `.isFalse()` 필터를 지원합니다.
* Geopoint 속성은 `.withinDistanceOf()`, `.withinPolygon()`, `.withinBoundingBox()` 필터를 지원합니다.
* GeoShape 속성은 `.withinBoundingBox()`, `.intersectsBoundingBox()`, `.doesNotIntersectBoundingBox()`, `.withinPolygon()`, `.intersectsPolygon()`, `doesNotIntersectPolygon()` 필터를 지원합니다.
* 링크 필터는 `.isPresent()` 메서드를 사용해 특정 타입의 연결된 객체가 하나라도 있는지(또는 없는지)로 객체를 필터링할 때 쓸 수 있습니다.
* 배열 속성은 `.contains()` 필터를 지원합니다. 이 필터는 배열 속성 값에 주어진 값 중 *하나라도* 포함된 객체만 남깁니다.

**설명**: 토큰(token)은 문자열을 공백 등의 기준으로 잘라 낸 검색 단위입니다. 예를 들어 `"fresh banana_pudding"`은 `fresh`와 `banana_pudding` 두 토큰이 됩니다(밑줄에서는 나뉘지 않음). 그래서 `banana`로 `phrase()` 검색을 해도 `banana_pudding` 토큰과는 일치하지 않습니다. 이런 동작은 SQL의 `LIKE '%banana%'`처럼 부분 문자열을 찾는 방식과 다르다는 점에 주의해야 합니다.

<a id="combining-filters"></a>
### 필터 조합하기 (Combining filters)

TypeScript v1에서는 `@foundry/functions-api`에서 내보내는 `Filters` API를 사용해 필터를 조합할 수 있습니다. 사용 가능한 메서드는 다음과 같습니다.

* `and()`는 주어진 필터를 모두 통과하는 객체만 남깁니다.
* `or()`는 주어진 필터 중 하나라도 통과하는 객체만 남깁니다.
* `not()`은 주어진 필터를 부정합니다.

TSv2에 대해서는 [`Not`](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#not-filter), [`And`](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#and-filter), [`Or`](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#or-filter) 필터를 참고하세요.

아래 예제에서는 `and()`를 사용해 항공편 객체 집합을 도착지 기준으로 필터링합니다.

```typescript tab="TypeScript v1"
import { Filters } from "@foundry/functions-api";

Objects.search()
    .flights()
    .filter(flight => Filters.or(
        Filters.and(flight.destination.exactMatch("SFO"), flight.passengerCount.gt(100)),
        Filters.and(flight.destination.exactMatch("LAX"), flight.passengerCount.gt(300)),
    ))
```

위 코드는 승객이 100명을 넘으면서 SFO에 도착한 항공편, 또는 승객이 300명을 넘으면서 LAX에 도착한 항공편만 남깁니다.

**설명**: SQL로 쓰면 `WHERE (destination = 'SFO' AND passengerCount > 100) OR (destination = 'LAX' AND passengerCount > 300)`입니다. 조건식을 JavaScript의 `&&`, `||`로 쓰지 않고 `Filters.and`, `Filters.or` 함수 호출로 쓰는 이유는, 이 조건이 TypeScript에서 바로 계산되는 불리언 값이 아니라 서버로 보낼 검색 조건 객체이기 때문입니다.

**주의**: 필터는 논리 연산자가 아니라 Filters 메서드로 조합하세요(Combine filters with Filters methods, not logical operators). TypeScript v1에서 객체 집합의 `.filter()` 메서드는 `&&`나 `||` 연산자를 사용하지 않습니다. 여러 필터를 적용하려면 위에 나열된 `Filters`의 메서드 중 하나를 사용해야 합니다(또는 `.filter()`를 여러 번 호출해 `and` 조건을 만들 수 있습니다).

<a id="filtering-on-string-properties-with-fuzzy-search"></a>
### 퍼지 검색으로 문자열 속성 필터링하기 (Filtering on string properties with fuzzy search)

선택적 `fuzziness` 파라미터를 지정하면 퍼지 일치(Fuzzy matching) 동작을 더 세밀하게 제어할 수 있습니다. fuzziness를 지정하지 않으면 검색하는 토큰의 길이에 따라 자동으로 편집 거리(edit distance)가 허용됩니다. 편집 거리를 지정하려면 `@foundry/functions-api`에서 `Fuzziness`를 가져와야 합니다.

`Fuzziness`는 TypeScript v2에 대응 개념이 없는 TypeScript v1 개념입니다. 자세한 내용은 마이그레이션 가이드의 [TypeScript v2에 대응 기능이 없는 기능](../10_typescript-v2/03_typescript-v2-migration.md#capabilities-with-no-typescript-v2-equivalent)을 참고하세요.

<a id="fuzzy-match-any-token"></a>
#### 토큰 중 하나와 퍼지 일치 (Fuzzy match any token)

```typescript tab="TypeScript v1"
Objects.search().employee().filter(employee => employee.firstName.fuzzyMatchAnyToken("Michael", { fuzziness: Fuzziness.LEVENSHTEIN_TWO })).all();
```

위 코드는 이름(first name)이 제공된 검색어에서 편집 2회 이내(레벤슈타인 거리 2)인 직원을 모두 반환합니다. 이 예제에서는 `Michael`, `Micheal`, `Mikhael`, `Michel`, `Mikhail`, `Mihail`이 포함됩니다(예를 들어 `Miguel`은 포함되지 않습니다). 검색어의 정확성에 더 확신이 있다면, 더 작은 편집 거리(다른 레벤슈타인 거리)로 검색해 결과를 조금 더 좁힐 수 있습니다.

**설명**: 레벤슈타인 거리(Levenshtein distance)는 한 문자열을 다른 문자열로 바꾸는 데 필요한 최소 편집 횟수입니다. 편집은 문자 하나의 삽입, 삭제, 치환을 말합니다. 예를 들어 `Michael`에서 `Michel`은 `a` 하나를 삭제하면 되므로 거리가 1입니다. 동적 계획법(DP)으로 계산하는 대표적인 알고리즘 문제이기도 합니다.

<a id="fuzzy-match-all-tokens"></a>
#### 모든 토큰과 퍼지 일치 (Fuzzy match all tokens)

```typescript tab="TypeScript v1"
Objects.search().employee().filter(employee => employee.fullName.fuzzyMatchAllTokens("Michael Smith", { fuzziness: Fuzziness.LEVENSHTEIN_ONE })).all();
```

여러 토큰으로 된 구절에도 퍼지 필터를 사용할 수 있습니다. 위 코드는 전체 이름(full name)에 `Michael`과 `Smith`가 **둘 다** 각 토큰당 최대 편집 1회 이내로 들어 있는 직원과 일치합니다. 예를 들어 `Mikhael Smitt`가 해당합니다(각각 레벤슈타인 거리 1). `fuzzyMatchAllTokens` 또는 `fuzzyMatchesAllTokens` 필터에서는 토큰의 순서를 고려하지 않습니다.

<a id="fuzzy-match-on-string-array-properties"></a>
#### 문자열 배열 속성에서 퍼지 일치 (Fuzzy match on string array properties)

배열 기반 속성에 대한 모든 필터는 그 기반 타입에서 사용할 수 있는 메서드를 쓸 수 있습니다. 예를 들어 문자열 배열 속성은 문자열 속성에서 쓸 수 있는 모든 메서드로 필터링할 수 있으며, 메서드 이름은 약간 다를 수 있습니다. 배열 속성에 대한 필터링에서는 배열 원소 중 하나만 일치해도 해당 객체가 반환됩니다.

> **중간 요약**: 필터는 속성 타입별로 다른 메서드(`exactMatch`, 토큰 기반 문자열 검색, `range`, 지리 필터, `contains` 등)를 제공합니다. 여러 조건은 `&&`, `||`가 아니라 `Filters.and/or/not`으로 조합하고, 문자열은 `Fuzziness`로 오타 허용 정도를 조절할 수 있습니다.

<a id="search-around"></a>
## Search Around

**주의**: TypeScript v1의 Search Around 제한(Search around limits in TypeScript v1). 다음 제한은 TypeScript v1 Objects API에 대해 문서화된 것입니다. `.all()` 또는 `.allAsync()`로 메모리에 불러오는 객체 집합에는 **Search Around를 최대 3회까지** 사용할 수 있습니다. 3회를 넘게 사용하면 오류가 발생합니다. Object Storage v2에서 객체 집합 A에서 객체 집합 B로 Search Around를 수행할 때, 결과 객체 집합 B는 객체 인스턴스가 1,000만 개를 넘을 수 없으며 넘으면 오류가 발생합니다. Object Storage v1에서는 이 제한이 100,000개입니다.

객체 집합의 객체 타입에 따라, [링크](../../02_object-and-link-types/06_link-types/01_link-types-overview.md)를 따라 이동할 수 있도록 *Search Around* 메서드가 생성됩니다. 아래 예제에서는 출발 공항 코드로 Flights 객체 집합을 필터링한 다음, 그 항공편의 승객으로 Search Around합니다. 그 결과 Passengers 객체 집합이 만들어지며, 이 집합에 다시 필터나 Search Around를 적용할 수 있습니다.

TypeScript v1은 링크 타입마다 링크 이름을 딴 Search Around 메서드를 하나씩 생성합니다. TSv2는 이를 하나의 `pivotTo()` 메서드로 대체합니다. [Links](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#links)를 참고하세요.

```typescript tab="TypeScript v1"
const passengersDepartingFromAirport = Objects.search()
    .flights()
    .filter(flight => flight.departureAirportCode.exactMatch(airportCode))
    .searchAroundPassengers();
```

**설명**: 입력은 Flight 객체 집합이고 출력은 Passenger 객체 집합입니다. `searchAroundPassengers()`는 Flight와 Passenger 사이의 링크 타입을 따라가 "필터된 항공편에 탑승한 모든 승객"을 돌려줍니다. SQL로는 `SELECT p.* FROM flights f JOIN passengers p ON ... WHERE f.departureAirportCode = ?`에 해당하는 조인 연산입니다. 결과가 다시 객체 집합이므로 `.filter()`를 이어 붙일 수 있습니다.

Search Around 메서드는 프로젝트에 가져온 링크 타입에 대해서만 생성됩니다. 링크 타입을 가져오는 방법은 [튜토리얼](02_foo-getting-started.md#import-ontology-types)을 참고하세요.

TypeScript v1에서는 성능상의 이유로, 한 번의 검색에서 수행할 수 있는 Search Around 연산 수가 현재 3회로 제한됩니다. Search Around 깊이가 3단계를 넘는 검색을 실행하려고 하면 런타임에 검색이 실패합니다.

> **중간 요약**: Search Around는 링크 타입을 따라 한 객체 집합에서 연결된 다른 타입의 객체 집합으로 이동하는 조인 연산입니다. TSv1에서는 링크마다 `searchAround링크이름()` 메서드가 생기고, 한 검색에서 최대 3단계까지 가능합니다.

<a id="k-nearest-neighbors-knn"></a>
## K-최근접 이웃 (K-nearest neighbors, KNN)

**주의**: KNN 제한(KNN limits). KNN은 [OSv2](../../../06_ontology-architecture/01_overview-and-getting-started/01_overview.md)에 인덱싱된 객체 타입에서만 지원됩니다. TypeScript v1에서 k 값은 0 < K <= 100 범위로 제한됩니다. 또한 검색 벡터는 인덱싱에 사용된 벡터와 크기가 같아야 하며 차원은 최대 2048입니다. 이 제한 중 하나라도 넘으면 오류가 발생합니다.

임베딩 속성을 가진 객체 타입은 KNN 검색에 사용할 수 있습니다. 이 검색은 제공된 임베딩 파라미터와 가장 가까운 임베딩 속성을 가진 객체를 k개 반환합니다. 다음 예제는 제공된 영화 대본과 가장 유사한 영화들을 반환합니다. 임베딩은 [Pipeline Builder](https://www.palantir.com/docs/foundry/pipeline-builder/pipeline-builder-aip/#text-to-embeddings) 같은 변환 도구에서 생성하거나, 함수 질의 시점에 [Palantir가 제공하는 임베딩 모델](../14_models/04_language-models.md#embeddings) 또는 [함수 안의 자체 모델](../14_models/01_functions-on-models.md)을 사용해 생성할 수 있습니다.

함수 저장소의 `functions.json` 설정 파일에서 `enableVectorProperties` 항목이 `true`로 설정되어 있는지 확인하세요.

두 버전 모두 `nearestNeighbors()`를 호출하지만 시그니처가 다릅니다. TypeScript v1은 벡터 속성과 검색 벡터를 지정하는 콜백을 전달하고, TSv2는 질의, 이웃 수, 속성을 위치 인자로 받으며 이웃을 100개가 아니라 최대 500개까지 허용합니다. [Nearest neighbors](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#nearest-neighbors)를 참고하세요.

```typescript tab="TypeScript v1"
import { Objects } from "@foundry/ontology-api";

const kValue: number = 2;
// 벡터는 FML Live에서 생성하거나 기존 객체에서 가져올 수 있습니다
const vector: Double[] = [0.7, 0.1, 0.3];
const movies: Movies[] = Objects.search()
        .movies()
        .nearestNeighbors(obj => obj.vectorProperty.near(vector, { kValue }))
        .orderByRelevance()
        .take(kValue);
```

위 예제는 처음 `kValue`개의 결과를 가져오기 전에 관련도 순으로 정렬도 합니다.

**설명**: 임베딩(embedding)은 텍스트나 이미지를 고정 길이의 실수 벡터로 바꾼 값입니다. 의미가 비슷한 데이터는 벡터 공간에서 거리가 가깝도록 만들어집니다. KNN 검색은 입력 벡터 `[0.7, 0.1, 0.3]`과 거리가 가장 가까운 `vectorProperty` 값을 가진 Movie 객체 k개(여기서는 2개)를 찾습니다. 키워드가 정확히 일치하지 않아도 의미상 비슷한 객체를 찾을 수 있어 "시맨틱 검색"에 쓰입니다.

전체 시맨틱 검색 워크플로 예시는 [시맨틱 검색 워크플로 가이드](../../../03_ontology-search/01_semantic-search/05_using-palantir-provided-models-to-create-a-semantic-search-workflow.md)를 참고하세요.

> **중간 요약**: 임베딩 속성이 있는 OSv2 객체 타입은 `nearestNeighbors()`로 입력 벡터와 가장 가까운 객체 k개를 찾을 수 있습니다. TSv1에서는 k가 최대 100, 벡터 차원은 최대 2048이며 `enableVectorProperties` 설정이 필요합니다.

<a id="set-operations"></a>
## 집합 연산 (Set operations)

TypeScript v1에서는 같은 객체 타입의 객체 집합들을 집합 연산으로 다양하게 결합할 수 있습니다.

* `.union()`은 주어진 객체 집합 중 하나에라도 있는 객체로 구성된 새 객체 집합을 만듭니다.
* `.intersect()`는 주어진 모든 객체 집합에 있는 객체로 구성된 새 객체 집합을 만듭니다.
* `.subtract()`는 주어진 객체 집합에 있는 객체를 제거합니다.

TSv2도 같은 세 메서드를 같은 이름으로 제공합니다. [Set operations](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#set-operations)를 참고하세요.

**설명**: 각각 수학의 합집합, 교집합, 차집합이며 SQL의 `UNION`, `INTERSECT`, `EXCEPT`에 해당합니다. 예를 들어 "SFO 도착 항공편 집합"에서 "지연된 항공편 집합"을 `.subtract()`하면 SFO에 정시 도착한 항공편 집합이 됩니다.

<a id="retrieving-all-objects"></a>
## 모든 객체 가져오기 (Retrieving all objects)

TypeScript v1에서 `.all()`과 `.allAsync()` 메서드는 객체 집합의 모든 객체를 가져오지만, 한 번에 너무 많은 객체를 불러오려 하면 함수 실행이 실패합니다. TypeScript v1에서 불러올 수 있는 최대 객체 수는 100,000개입니다. 다만 10,000개를 넘게 불러와도 함수 실행이 시간 초과될 수 있습니다. [함수의 시간 및 공간 제한에 대해 더 알아보세요.](../07_function-management/02_manage-functions.md#enforced-limits)

`.allAsync()` 메서드를 사용하면 객체 집합의 모든 객체로 resolve되는 Promise를 얻을 수 있습니다. 여러 객체 집합에서 데이터를 병렬로 불러올 때 유용합니다.

TSv2의 대응 방법은 [객체를 메모리에 불러오기](../10_typescript-v2/03_typescript-v2-migration.md#load-objects-into-memory)를 참고하세요.

**설명**: Promise는 JavaScript에서 "나중에 완료될 비동기 작업의 결과"를 나타내는 객체입니다. 예를 들어 `const [a, b] = await Promise.all([setA.allAsync(), setB.allAsync()])`처럼 쓰면 두 집합의 로딩 요청을 동시에 보내고 둘 다 끝날 때까지 기다리므로, 하나씩 순서대로 불러올 때보다 전체 대기 시간이 줄어듭니다.

<a id="ordering-and-limiting"></a>
## 정렬과 개수 제한 (Ordering and limiting)

모든 객체를 가져오는 대신, 객체 집합에 정렬 절을 적용한 다음 불러올 객체 수를 지정해 제한된 수만 불러올 수 있습니다. TypeScript v1에서는 다음 메서드를 사용할 수 있습니다.

* `.orderBy()`는 정렬 기준이 될 검색 가능한 속성을 지정하며, 정렬 방향도 지정할 수 있습니다. 정렬 가능한 타입(숫자, 날짜, 문자열)의 속성만 이 메서드에서 선택할 수 있습니다. 여러 속성으로 정렬하려면 `.orderBy()`를 여러 번 호출할 수 있습니다.
* `.orderByRelevance()`는 제공된 필터에 얼마나 잘 일치하는지 순서로 객체를 반환하도록 지정하며, 가장 관련성 높은 객체가 먼저 나옵니다. 특정 객체의 속성 값에 대한 검색어의 관련도는 속성 값 안에서 그 단어가 나타나는 빈도, 전체 객체에서 그 단어가 나타나는 빈도 등을 고려하는 복잡한 판정입니다. `.exactMatch()` 필터만 수행하거나 문자열이 아닌 속성으로 필터링할 때는 관련도가 덜 적합합니다. 한 검색에서는 `.orderBy()`와 `.orderByRelevance()` 중 하나만 사용할 수 있습니다.
* `.take()`와 `.takeAsync()`를 사용하면 집합에서 지정된 수의 객체를 가져올 수 있습니다. 이 메서드들은 정렬을 지정한 뒤에만 사용할 수 있습니다.

TSv2에 대해서는 [Load ordered results](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#load-ordered-results)를 참고하세요. [정렬과 로딩](../10_typescript-v2/03_typescript-v2-migration.md#ordering-and-loading)에는 TSv2 형태가 없는 TSv1 기능이 정리되어 있습니다.

예를 들어 다음 코드는 입사일이 가장 이른 직원 10명을 가져옵니다.

```typescript tab="TypeScript v1"
Objects.search()
    .employees()
    .orderBy(e => e.startDate.asc())
    .take(10)
```

**설명**: SQL의 `SELECT * FROM employees ORDER BY startDate ASC LIMIT 10`과 같습니다. 정렬 없이 `take()`를 쓸 수 없게 한 이유는, 순서가 정해지지 않은 집합에서 "처음 10개"는 실행할 때마다 달라질 수 있기 때문입니다.

또 다른 예로, 보험사의 사고 청구 텍스트를 담은 객체 타입 `claims`가 있다고 합시다. 빨간 차와 사슴이 관련된 특정 청구를 찾고 싶다고 가정합니다. `.orderByRelevance()` 줄이 없으면 `red`, `car`, `collision`, `with`, `deer` 중 아무 단어라도 포함한 결과가 상위 10개에 반환될 수 있습니다. `.orderByRelevance()` 줄이 있으면 처음 10개 결과는 검색어를 가장 많이 포함한 청구가 되므로, 가장 관련성 높은 청구가 먼저 나타납니다.

다음 예제는 청구를 필터링하고 관련도 순으로 정렬합니다.

```typescript tab="TypeScript v1"
const results = Objects.search()
    .claims()
    .filter(doc => doc.text.matchAnyToken("red car collision with deer"))
    .orderByRelevance()
    .take(10)
```

> **중간 요약**: `.all()`은 최대 100,000개까지 불러올 수 있지만 10,000개만 넘어도 시간 초과 위험이 있습니다. 필요한 만큼만 가져오려면 `.orderBy()` 또는 `.orderByRelevance()`로 정렬한 뒤 `.take(n)`을 사용합니다.

<a id="computing-aggregations"></a>
## 집계 계산하기 (Computing aggregations)

**주의**: TypeScript v1의 집계 제한(Aggregation limits in TypeScript v1). TypeScript v1 Objects API가 반환하는 집계는 **전체 버킷 10,000개**로 제한됩니다. 이 제한을 넘으면 오류가 발생합니다.

`.topValues()`로 버킷을 나눌 때 데이터의 서로 다른 값이 1,000개를 넘으면 결과는 근사값이 됩니다. 이 경우 상위 값 목록이 정확하지 않을 수 있습니다.

<a id="grouping-objects-by-properties"></a>
### 속성으로 객체 그룹화하기 (Grouping objects by properties)

많은 경우 객체 집합의 모든 객체를 불러올 필요가 없습니다. 대신 값을 버킷으로 나눈 집계만 불러와 추가 분석을 할 수 있습니다.

집계 계산을 시작하려면 객체 집합에서 `.groupBy()` 메서드를 호출합니다. 이 메서드로 객체 집합에 속한 객체 타입의 검색 가능한 속성 중 하나를 기준으로 버킷을 지정할 수 있습니다.

TSv2에 대해서는 [Types of group bys](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#types-of-group-bys)를 참고하세요.

예를 들어 이 코드는 직원을 입사일 기준으로 그룹화합니다.

```typescript tab="TypeScript v1"
Objects.search()
    .employees()
    .groupBy(e => e.startDate.byDays())
```

**설명**: 버킷(bucket)은 그룹화 결과로 생기는 각 그룹입니다. SQL의 `GROUP BY startDate`를 실행했을 때 생기는 그룹 하나하나가 버킷 하나에 해당합니다. 예를 들어 직원 5명의 입사일이 3/1, 3/1, 3/2, 3/5, 3/5라면 `byDays()`로 3개의 버킷(3/1, 3/2, 3/5)이 생깁니다.

버킷 기준 속성을 지정할 때는 속성 타입에 따라 버킷을 어떻게 나눌지에 대한 추가 정보를 제공해야 합니다. TSv2는 [group-by 전략 매핑](../10_typescript-v2/03_typescript-v2-migration.md#group-by-strategy-mapping)을 참고하세요. TypeScript v1 버킷 메서드는 다음과 같습니다.

* `boolean` 속성의 유일한 옵션은 `.topValues()`입니다. `true`와 `false`에 대해 버킷 두 개를 반환합니다.
* 문자열 속성에는 두 가지 옵션이 있습니다.
  * `.topValues()`: 빠른 응답 시간이 필요하고 카디널리티가 작은 속성에 적합합니다. 문자열 속성의 상위 1,000개 값으로 버킷을 나눕니다. 이 제한은 반환되는 집계가 과도하게 커지지 않도록 하기 위한 것입니다.
  * `.exactValues()`: 더 정확한 집계가 필요하고, 카디널리티가 높은 속성에 대해 최대 10,000개 버킷까지 고려할 수 있습니다. 고려할 버킷 수는 `.exactValues({"maxBuckets": numBuckets})`로 지정할 수 있으며, `numBuckets`는 0에서 10,000 사이의 정수여야 합니다. 더 많은 결과를 고려해야 하므로 이 메서드는 응답 시간이 더 길어질 수 있습니다.
* 숫자 속성(예: `Integer`, `Long`, `Float`, `Double`)의 두 가지 버킷 옵션은 다음과 같습니다.
  * `.byRanges()`로 사용할 범위를 정확히 지정할 수 있습니다. 예를 들어 `.byRanges({ min: 0, max: 50 }, { min: 50, max: 100 })`를 사용하면 여기서 지정한 \[0, 50]과 \[50, 100] 두 범위로 객체를 나눕니다. 범위의 `min`은 포함이고 `max`는 미포함입니다. `min`이나 `max`를 생략하면 각각 -∞부터 `max`까지, 또는 `min`부터 ∞까지의 값을 담는 버킷이 됩니다.
  * `.byFixedWidth()`는 각 버킷의 폭을 지정합니다. 예를 들어 `.byFixedWidth(50)`을 사용하면 폭이 50인 범위들로 객체를 나눕니다.
* `LocalDate` 속성에는 손쉬운 버킷 나누기를 위한 여러 편의 메서드가 제공됩니다.
  * `.byYear()`
  * `.byQuarter()`
  * `.byMonth()`
  * `.byWeek()`
  * `.byDays()`는 값을 일 단위로 나눕니다. 버킷 폭으로 사용할 일 수를 전달할 수 있습니다.
* `Timestamp` 속성에는 `LocalDate`와 같은 버킷 옵션이 적용되며, 다음이 추가됩니다.
  * `.byHours()`는 값을 시간 단위로 나눕니다. 버킷 폭으로 사용할 시간 수를 전달할 수 있습니다.
  * `.byMinutes()`는 값을 분 단위로 나눕니다. 버킷 폭으로 사용할 분 수를 전달할 수 있습니다.
  * `.bySeconds()`는 값을 초 단위로 나눕니다. 버킷 폭으로 사용할 초 수를 전달할 수 있습니다.
* `Array` 속성의 버킷 옵션은 배열 원소의 타입에 따라 결정됩니다. 구체적으로 `Array<PropertyType>`에는 `PropertyType`과 같은 버킷 메서드가 제공됩니다(예: `Array<boolean>`은 `boolean`과 같은 버킷 메서드를 가집니다).
  * 예를 들어 Alice와 Bob으로 구성된 `employeeSet`이라는 객체 집합이 있고, 두 사람의 `Array<string>` 속성 `pastCountries`가 각각 `["US", "UK"]`와 `["US"]`라면, `employeeSet.groupBy(e => e.pastCountries.exactValues()).count()`는 `{ "US": 2, "UK": 1 }`을 반환합니다.

**설명**: 카디널리티(cardinality)는 속성이 가질 수 있는 서로 다른 값의 개수입니다. 예를 들어 `gender` 속성은 카디널리티가 낮고, `email` 속성은 거의 모든 객체가 다른 값을 가지므로 카디널리티가 높습니다. `.topValues()`는 가장 많이 나오는 값 상위 1,000개만 근사적으로 계산하므로 빠르고, `.exactValues()`는 더 많은 버킷을 정확히 계산하는 대신 느립니다.

한 속성으로 그룹화한 뒤 선택적으로 `.segmentBy()` 메서드를 호출해 버킷을 한 번 더 나눌 수 있습니다. 이렇게 하면 검색 가능한 속성 두 개로 버킷을 나눈 3차원 집계를 계산할 수 있습니다. TypeScript v2는 같은 `$groupBy` 객체에 두 번째 키를 넣어 두 번째 속성으로 버킷을 나누며, 반환되는 결과 형태가 다릅니다. 마이그레이션 가이드의 [TypeScript v2에 대응 기능이 없는 기능](../10_typescript-v2/03_typescript-v2-migration.md#capabilities-with-no-typescript-v2-equivalent)을 참고하세요.

예를 들어 다음과 같이 직원을 입사일과 역할(role)로 그룹화할 수 있습니다.

```typescript tab="TypeScript v1"
Objects.search()
    .employees()
    .groupBy(e => e.startDate.byDays())
    .segmentBy(e => e.role.topValues())
```

<a id="choosing-an-aggregation-metric"></a>
### 집계 지표 선택하기 (Choosing an aggregation metric)

객체 집합을 그룹화한 뒤에는 다양한 집계 메서드를 호출해 각 버킷의 집계 지표를 계산할 수 있습니다. TypeScript v1에서 속성이 필요한 메서드는 searchable로 표시된 속성만 받습니다. TypeScript v2의 대응 형태는 마이그레이션 가이드의 [집계 지표 매핑](../10_typescript-v2/03_typescript-v2-migration.md#aggregation-metric-mapping) 표를 참고하세요. 사용 가능한 TypeScript v1 집계 메서드는 다음과 같습니다.

* `.count()`는 각 버킷의 객체 수를 그대로 반환합니다.
* `.average()`는 주어진 숫자, 타임스탬프, 날짜 속성의 평균을 반환합니다.
* `.max()`는 주어진 숫자, 타임스탬프, 날짜 속성의 최댓값을 반환합니다.
* `.min()`은 주어진 숫자, 타임스탬프, 날짜 속성의 최솟값을 반환합니다.
* `.sum()`은 주어진 숫자 속성 값의 합계를 반환합니다.
* `.cardinality()`는 주어진 속성의 서로 다른 값의 근사 개수를 반환합니다.

TypeScript v1에서 이 메서드 중 하나를 호출하면 `TwoDimensionalAggregation` 또는 `ThreeDimensionalAggregation`이 반환됩니다. 최종 집계 메서드를 호출하기 전에 `.segmentBy()`를 호출했다면 `ThreeDimensionalAggregation`이 반환됩니다.

[**유효한 버킷 타입**을 포함해 이 집계 타입들의 구조에 대해 더 알아보세요.](../04_types-reference.md#aggregation-types)

**설명**: `TwoDimensionalAggregation`은 "버킷 키 하나와 값 하나"의 목록입니다. 예: `[{key: "Engineer", value: 12}, {key: "Designer", value: 4}]`. `ThreeDimensionalAggregation`은 버킷 키가 두 단계로 중첩된 형태입니다. 예: `Engineer` 버킷 안에 `{key: "Seoul", value: 7}, {key: "London", value: 5}`가 들어 있는 구조입니다. SQL로 치면 `GROUP BY title`과 `GROUP BY title, office`의 차이입니다. 정확한 필드 구조는 링크된 타입 레퍼런스에 있습니다.

집계를 계산하려면 원격 서비스에서 데이터를 불러와야 하므로, 결과 집계는 `Promise`로 감싸져 있습니다. [async/await ↗](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function) 문법을 사용해 `Promise` 결과를 꺼낼 수 있습니다.

아래는 집계를 불러와 결과로 반환하는 TypeScript v1 전체 예제입니다.

```typescript tab="TypeScript v1"
import { Double, Function, ThreeDimensionalAggregation } from "@foundry/functions-api";
import { Objects } from "@foundry/ontology-api";

export class AggregationFunctions {
    @Function()
    public async employeesByRoleAndOffice(): Promise<ThreeDimensionalAggregation<string, string, Double>> {
        return Objects.search()
            .employee()
            .groupBy(e => e.title.topValues())
            .segmentBy(e => e.office.topValues())
            .count();
    }
}
```

**설명**: 입력은 없고, 출력은 직함(title)과 사무실(office)의 조합별 직원 수입니다. `groupBy`로 직함별 버킷을 만들고, `segmentBy`로 각 버킷을 다시 사무실별로 나눈 뒤, `.count()`로 각 칸의 객체 수를 셉니다. SQL로는 `SELECT title, office, COUNT(*) FROM employee GROUP BY title, office`입니다. 반환 타입의 세 타입 인자 `<string, string, Double>`은 각각 첫째 버킷 키, 둘째 버킷 키, 값의 타입입니다.

TypeScript v1에서는 그룹화된 집계가 이미 `ThreeDimensionalAggregation` 형태이므로, 위처럼 함수가 이를 바로 반환할 수 있습니다. TSv2에서는 `.aggregate()`가 평평한(flat) 행 배열을 반환하므로 함수가 집계 타입을 직접 조립해야 합니다. [집계 타입](../04_types-reference.md#aggregation-types)과 [그룹화](../10_typescript-v2/03_typescript-v2-migration.md#grouping)를 참고하세요.

아래는 `groupBy` 문 없이 집계하는 전체 예제입니다. TypeScript v1에서는 count가 undefined일 경우에 대비해 `?? 0`을 씁니다.

```typescript tab="TypeScript v1"
import { Double, Function } from "@foundry/functions-api";
import { Objects } from "@foundry/ontology-api";

export class AggregationFunctions {
    @Function()
    public async employeesStats(): Promise<Double> {
        // 전체 직원 수. count()가 undefined를 반환하면 0을 기본값으로 사용
        return Objects.search().employee().count() ?? 0;
    }
}
```

위 TypeScript v1 코드 예제에서 해당 줄을 바꾸면 `groupBy` 없이 다른 집계도 수행할 수 있습니다. 예:

* 전체 직원 수: `Objects.search().employee().count();` (위 예제와 같음)
* 직원 평균 근속 기간: `Objects.search().employee().average(e => e.tenure);`
* 직원 최대 근속 기간: `Objects.search().employee().max(e => e.tenure);`
* 직원 최소 근속 기간: `Objects.search().employee().min(e => e.tenure);`
* 전체 직원 급여 합계: `Objects.search().employee().sum(e => e.salary);`
* 사무실 수: `Objects.search().employee().cardinality(e => e.office);`

집계 결과를 메모리에서 가공하는 예시는 [사용자 정의 집계 만들기](04_create-custom-aggregation.md) 가이드를 참고하세요.

> **중간 요약**: `.groupBy()`(필요하면 `.segmentBy()`까지)로 버킷을 나누고 `.count()`, `.sum()` 같은 지표 메서드로 각 버킷 값을 계산합니다. 결과는 2차원 또는 3차원 집계 타입의 Promise이며, TSv1에서는 버킷이 최대 10,000개로 제한됩니다.

## 정리

- 객체 집합은 한 타입 객체들의 순서 없는 모음이며, 실제 데이터 로딩을 필요한 시점까지 미루므로 객체 배열보다 효율적입니다.
- TSv1에서는 `Objects.search()`로 시작해 `.filter()`, `searchAround...()`, `nearestNeighbors()`, `union/intersect/subtract`를 이어 붙여 원하는 집합을 만듭니다.
- 결과는 `.all()`(최대 100,000개), `.orderBy()`/`.orderByRelevance()` 후 `.take(n)`, 또는 `.groupBy()`와 집계 메서드로 받습니다.
- 필터, 정렬, 집계는 `Searchable`로 인덱싱된 속성에서만 동작하며 Search Around 3단계, 버킷 10,000개 같은 제한이 있습니다.
- TSv2와 Python은 OSDK를 사용하므로, 대응 방법은 마이그레이션 가이드와 OSDK 문서를 참고합니다.
