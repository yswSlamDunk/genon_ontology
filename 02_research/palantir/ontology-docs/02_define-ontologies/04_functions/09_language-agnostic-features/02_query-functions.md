# 쿼리 함수를 API gateway로 게시하고 호출하기 (Publish and call query functions through API gateway)

- 원문: https://www.palantir.com/docs/foundry/functions/query-functions/
- 사이드바 위치: Define Ontologies > Functions > Language-agnostic features > Publish and call query functions through API gateway

이 페이지는 함수(function) 가운데 읽기 전용인 쿼리(query)를 정의하고, API 이름을 붙여 Foundry API gateway를 통해 외부에 공개하는 방법을 다룹니다. 쿼리를 정의하는 데코레이터 문법, API 이름 규칙, 버전 관리 방식, Ontology Manager에서 쿼리를 찾는 방법, 다른 저장소에서 쿼리를 호출하는 방법을 차례로 설명합니다. 외부 시스템이 HTTP로 온톨로지 데이터를 계산해 가져가야 할 때 필요한 기능입니다.

<a id="queries"></a><a id="query-decorator"></a>
## 쿼리 (Queries)

쿼리(query)는 함수 중에서 읽기 전용인 부분집합으로, 선택적으로 [API gateway](https://www.palantir.com/docs/foundry/api/general/overview/introduction/)를 통해 공개할 수 있습니다. 쿼리는 온톨로지를 수정하거나 외부 시스템을 변경하는 것과 같은 부수 효과(side effect)를 가질 수 없습니다. API gateway를 통해 이런 편집 기능이 추가로 필요하다면 [액션(Action)](https://www.palantir.com/docs/foundry/api/ontology-resources/actions/apply-action/)을 사용해야 합니다.

**설명**: API gateway는 Foundry 기능을 HTTP API(REST 엔드포인트)로 노출하는 관문입니다. 쿼리는 SQL의 `SELECT`처럼 데이터를 읽고 계산해서 값을 돌려주기만 합니다. 데이터를 바꾸는 일(`INSERT`, `UPDATE`에 해당)은 액션의 몫으로 분리되어 있습니다.

<a id="example-api-named-query"></a><a id="query-decorator"></a>
## 쿼리 데코레이터 (Query decorator)

쿼리 함수를 정의하려면 다음 문법을 사용합니다.

```typescript tab="TypeScript v1"
import { Query } from "@foundry/functions-api";

@Query({ apiName: "myTypeScriptV1Function" })
```

```typescript tab="TypeScript v2"
// 함수가 들어 있는 파일에서 apiName 파라미터를 가진 config 객체를 export합니다
export const config = {
    apiName: "myTypeScriptV2Function"
};
```

```python tab="Python"
from functions.api import function

@function(api_name="myPythonFunction")
```

**설명**: 언어별로 API 이름을 붙이는 방식이 다릅니다. TypeScript v1은 `@Query` 데코레이터에 `apiName`을 넘기고, TypeScript v2는 파일에서 `config` 객체를 export하며, Python은 `@function` 데코레이터에 `api_name`을 넘깁니다. 데코레이터는 함수나 클래스 메서드 위에 붙여 추가 정보(메타데이터)를 부여하는 문법입니다.

Python과 TypeScript v1 함수의 경우, 데코레이터는 `string` 타입의 API 이름 파라미터를 받으며, API 이름을 정의하려면 이 파라미터가 필요합니다. TypeScript v1을 사용할 때 `apiName` 파라미터를 정의하지 않으면, 쿼리는 기존 [`@Function` 데코레이터](../12_typescript-v1/02_decorators.md)와 비슷하게 동작합니다. 이에 대응하는 Python 문법은 `api_name`입니다.

<a id="api-name-validations"></a><a id="example-api-named-query"></a>
### 예제: API 이름이 붙은 쿼리 (Example: API-named query)

아래 예제는 쿼리를 [API gateway](https://www.palantir.com/docs/foundry/api/general/overview/introduction/)를 통해 공개하는 방법을 보여 줍니다.

```typescript tab="TypeScript v2"
import { Client } from "@osdk/client";
import { Double } from "@osdk/functions";
import { Aircraft } from "@ontology/sdk";

export const config = {
    apiName: "getReschedulableAircraftCount"
};

async function countAircraftTakingOffAfter(client: Client, minimumTimeInMinutes: Double): Promise<Double> {
    const { $count } = await client(Aircraft).where({
        timeUntilNextFlight: {
            $gt: minimumTimeInMinutes
        }
    }).aggregate({ $select: { $count: "unordered" } })

    return $count;
}

export default countAircraftTakingOffAfter;
```

(원문에는 같은 쿼리를 `@Query` 데코레이터로 작성한 TypeScript v1 버전과 `@function(api_name=...)`으로 작성한 Python 버전도 있습니다.)

**설명**: 이 함수는 분(minute) 단위 숫자 `minimumTimeInMinutes`를 입력받아, 다음 비행까지 남은 시간(`timeUntilNextFlight`)이 그 값보다 큰 Aircraft 객체의 개수를 돌려줍니다. `where(...)`가 필터, `aggregate({ $select: { $count: ... } })`가 개수 집계이며, SQL로는 `SELECT COUNT(*) FROM aircraft WHERE time_until_next_flight > ?`에 해당합니다. `config`의 `apiName`이 `getReschedulableAircraftCount`이므로 API gateway에서는 이 이름으로 호출됩니다. 반면 코드 안의 함수 이름은 `countAircraftTakingOffAfter`입니다.

> **중간 요약**: 쿼리는 부수 효과가 없는 읽기 전용 함수이며, API 이름을 붙이면 API gateway로 공개됩니다. 언어마다 API 이름을 지정하는 문법(`@Query`, `config` 객체, `api_name`)이 다릅니다.

<a id="api-name-validations"></a><a id="version-and-update-api-named-queries"></a>
## API 이름 검증 (API name validations)

쿼리의 `apiName`은 다음 요구 사항을 만족하는 문자열이어야 합니다.

* `lowerCamelCase` 형식이어야 합니다.
* 100자 미만이어야 합니다.
* 숫자로 시작하면 안 됩니다.
* 저장소에 가져온(import) 모든 온톨로지 사이에서 고유해야 합니다.
  * `apiName`이 고유하지 않으면 [태깅 과정](../03_getting-started.md#publish-your-functions)이 실패하며, 이름을 바꿔야 합니다.

또한 API 이름이 붙은 쿼리를 포함하는 저장소는 적어도 하나의 온톨로지에서 엔터티를 가져와야 합니다.

**설명**: `lowerCamelCase`는 첫 단어는 소문자로, 이어지는 단어의 첫 글자만 대문자로 붙여 쓰는 표기입니다(예: `getAircraftCount`). 태깅(tagging)은 저장소의 특정 커밋에 버전 태그(예: `1.2.0`)를 달아 함수를 게시하는 과정입니다.

<a id="search-and-view-queries"></a><a id="version-and-update-api-named-queries"></a>
## API 이름이 붙은 쿼리의 버전 관리와 업데이트 (Version and update API-named queries)

API 이름이 붙은 쿼리는 항상 게시된 쿼리의 **가장 최근에 태그된 버전**을 사용하며, 다른 Foundry 함수와 같은 시맨틱 버저닝(semantic versioning) 방식을 따르지 않습니다.

API 이름과 쿼리의 연결을 끊어 API gateway에서 더 이상 동작하지 않게 하려면, 쿼리 데코레이터에서 API 이름을 제거하고 저장소에서 새 태그를 릴리스해야 합니다.

**주의**: 데코레이터의 API 이름을 바꾸고 새 태그를 게시하면 소비자(consumer)가 깨집니다. 쿼리는 가장 최근에 게시된 버전만 지원됩니다.

소비자가 호환성을 깨는 변경 없이 편한 시점에 업그레이드할 수 있도록, 같은 API 이름의 여러 버전을 지원할 수 있습니다. 그렇게 하려면 저장소에서 쿼리 코드를 복사하고 다른 API 이름을 붙여야 합니다. 예를 들면 `getReschedulableAircraftCountV2`와 같습니다.

**설명**: 시맨틱 버저닝은 `주.부.수` 형태(예: `2.1.0`)로 버전을 매기고, 호출하는 쪽이 특정 버전에 고정해 쓰는 방식입니다. 일반 함수는 이렇게 버전을 고정할 수 있지만, API 이름이 붙은 쿼리는 항상 최신 태그 버전으로 실행됩니다. 따라서 입력이나 출력 형식을 바꾸면 기존 호출자가 바로 영향을 받습니다. 이를 피하려면 `...V2`처럼 새 이름의 쿼리를 따로 만들어 두 버전을 함께 운영합니다.

> **중간 요약**: API 이름은 `lowerCamelCase`, 100자 미만, 숫자로 시작하지 않음, 고유함이라는 규칙을 지켜야 합니다. API 이름이 붙은 쿼리는 항상 최신 태그 버전으로 동작하므로, 호환성을 깨는 변경은 새 API 이름의 복사본으로 제공해야 합니다.

<a id="call-a-query-function"></a><a id="search-and-view-queries"></a>
## 쿼리 검색과 조회 (Search and view queries)

다른 함수와 마찬가지로 [Ontology Manager](../../../05_applications/04_ontology-manager/01_overview.md)에서 쿼리를 검색하고 관리할 수 있습니다. 쿼리 이름이나 API 이름으로 검색할 수 있습니다. [위](#example-api-named-query) 예제에서 API 이름은 `getReschedulableAircraftCount`, 쿼리 이름은 `countAircraftTakingOffAfter`입니다.

![Ontology Manager에서 쿼리 검색하기](https://www.palantir.com/docs/resources/foundry/functions/query-in-oma.png)

**주의**: TypeScript v1 함수를 사용할 때는, 쿼리를 활성화하기 위해 저장소의 `functions.json` 파일에서 `enableQueries` 속성을 true로 설정해야 할 수 있습니다. <br><br>

```typescript tab="TypeScript v1"
{
  "enableQueries": true
}
```

<a id="call-a-query-function"></a>
## 쿼리 함수 호출하기 (Call a query function)

TypeScript 또는 Python 쿼리 함수를 게시한 다음, 그 함수를 사용할(consume) 코드 저장소로 이동해 [**Resource imports** 사이드바](../12_typescript-v1/08_resource-imports-sidebar.md)를 사용해 함수를 가져옵니다.

그러면 사용하는 쪽 저장소에서 함수를 호출할 수 있습니다. 예를 들면 다음과 같습니다.

```typescript tab="TypeScript v2"
import { Client } from "@osdk/client";
import { Double } from "@osdk/functions";
import { getReschedulableAircraftCount } from "@ontology/sdk";

async function callQueryFunction(client: Client): Promise<Double> {
    return client(getReschedulableAircraftCount).executeFunction({ timeUntilNextFlight: 10 });
}

export default callQueryFunction;
```

(원문에는 `Queries.getReschedulableAircraftCount(10)`으로 호출하는 TypeScript v1 버전과 `FoundryClient().ontology.queries.get_reschedulable_aircraft_count(...)`로 호출하는 Python 버전도 있습니다.)

**설명**: 가져온 쿼리는 생성된 SDK(`@ontology/sdk`) 안에 `getReschedulableAircraftCount`라는 이름으로 들어옵니다. `client(쿼리).executeFunction({...})`에 입력 파라미터를 객체로 넘기면 쿼리가 실행되고 결과(여기서는 개수)가 돌아옵니다. 코드 안의 함수 이름이 아니라 API 이름으로 호출한다는 점이 핵심입니다.

TypeScript v1 함수의 경우, Foundry는 게시된 함수에서 어떤 쿼리 함수와 언어 모델 메서드를 호출하는지 알아야 합니다. Foundry는 호출되는 쿼리를 감지하기 위해 자동으로 정적 분석을 제공합니다. 그러나 이 정적 분석이 가끔 특정 호출을 놓칠 수 있으며, 이 경우 `@Uses` 데코레이터를 추가하라는 런타임 오류가 발생합니다. 이 데코레이터는 자동으로 감지된 쿼리 사용 목록을 보완하는 역할을 합니다. 언어 모델 메서드도 같은 `queries` 배열에 나열합니다.

다음 예제는 `@Uses` 데코레이터의 사용법을 보여 줍니다.

```typescript tab="TypeScript v1"
import { Uses } from "@foundry/functions-api";
import { Queries } from "@foundry/ontology-api";

export class MyFunctions {
    @Uses({ queries: [Queries.getReschedulableAircraftCount] })
    @Function()
    public callQueryFunction(): Promise<Double> {
        return Queries.getReschedulableAircraftCount(10);
    }
}
```

**설명**: 정적 분석은 코드를 실행하지 않고 소스 코드만 읽어서 어떤 쿼리를 부르는지 찾아내는 방식입니다. 호출 대상을 변수에 담아 간접적으로 부르는 경우처럼 소스만 보고 알기 어려운 호출은 놓칠 수 있습니다. 그럴 때 `@Uses({ queries: [...] })`에 사용하는 쿼리를 직접 적어 두면 Foundry가 의존 관계를 정확히 알 수 있습니다.

> **중간 요약**: 게시한 쿼리는 Ontology Manager에서 쿼리 이름이나 API 이름으로 찾을 수 있고, 다른 저장소에서 Resource imports로 가져와 호출할 수 있습니다. TypeScript v1에서 정적 분석이 쿼리 호출을 놓치면 `@Uses` 데코레이터로 직접 선언합니다.

## 정리

- 쿼리는 부수 효과가 없는 읽기 전용 함수이며, API 이름을 붙이면 API gateway를 통해 HTTP로 호출할 수 있습니다. 데이터를 바꾸려면 액션을 사용합니다.
- API 이름은 `lowerCamelCase`, 100자 미만, 숫자로 시작하지 않음, 가져온 온톨로지 전체에서 고유함이라는 규칙을 따라야 합니다.
- API 이름이 붙은 쿼리는 항상 최신 태그 버전으로 동작하므로, 호환성을 깨는 변경은 `...V2` 같은 새 API 이름으로 제공합니다.
- 다른 저장소에서는 Resource imports 사이드바로 쿼리를 가져와 호출하며, TypeScript v1에서는 필요 시 `@Uses` 데코레이터로 사용하는 쿼리를 명시합니다.
