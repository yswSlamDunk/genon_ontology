# 성능 최적화 (Optimize performance)

- 원문: https://www.palantir.com/docs/foundry/functions/optimize-performance/
- 사이드바 위치: Define Ontologies > Functions > Function consumption > Optimize performance

이 페이지는 함수(function)를 더 빠르고 적은 컴퓨팅 자원으로 실행하기 위한 모범 사례를 정리합니다. 함수의 비용이 어떻게 구성되는지, 어떤 입력 타입이 효율적인지, 객체를 반복문 안에서 하나씩 불러오는 것이 왜 느린지, 집계를 백엔드에 맡기는 방법, 병렬 실행이 속도와 비용에 각각 어떤 영향을 주는지 등을 예제 코드와 함께 다룹니다. 핵심 원칙은 "필요한 계산을 가능한 한 온톨로지 백엔드에서 한 번에 처리하게 하라"입니다.

이 페이지는 함수의 성능과 리소스 사용을 최적화하기 위한 모범 사례를 설명합니다. 이 지침을 따르면 컴퓨팅 사용량을 최소화하고 함수가 효율적으로 실행되도록 할 수 있습니다. 컴퓨팅 비용과 함수가 계량되는 방식에 대해서는 [온톨로지 질의의 컴퓨팅 사용량](../../01_ontologies/05_usage/03_query-compute-usage.md)을 참고하세요.

<a id="understand-function-compute-costs"></a>
## 함수 컴퓨팅 비용 이해하기 (Understand function compute costs)

함수의 비용은 여러 구성 요소로 이루어집니다.

* **오버헤드(Overhead):** 함수를 실행할 때마다 무엇을 하든 4 컴퓨트초(compute-second)의 고정 오버헤드가 발생합니다.
* **컴퓨팅 시간(Compute time):** 함수를 실행하는 데 필요한 vCPU 시간입니다.
* **외부 호출(External calls):** 플랫폼의 다른 부분에 대한 호출(온톨로지 질의, 모델 추론, LLM 호출)은 각각 별도의 비용이 발생합니다.

플랫폼에서 컴퓨트초가 어떻게 계산되고 측정되는지에 대한 자세한 내용은 [사용량 유형(Usage types)](https://www.palantir.com/docs/foundry/resource-management/usage-types/)을 참고하세요.

**설명**: 컴퓨트초(compute-second)는 Foundry가 컴퓨팅 사용량을 재는 단위입니다. 고정 오버헤드가 호출마다 4 컴퓨트초씩 붙기 때문에, 같은 작업이라도 함수를 1,000번 나눠 호출하면 오버헤드만 4,000 컴퓨트초가 됩니다. 또한 함수 안에서 온톨로지에 질의를 보낼 때마다 외부 호출 비용이 따로 쌓이므로, 질의 횟수를 줄이는 것이 이 페이지 전체를 관통하는 최적화 방향입니다.

> **중간 요약**: 함수 비용은 실행당 4 컴퓨트초의 고정 오버헤드, vCPU 실행 시간, 온톨로지 질의나 모델 호출 같은 외부 호출 비용의 합입니다.

<a id="use-the-performance-tab"></a>
## Performance 탭 사용하기 (Use the Performance tab)

Performance 탭은 함수의 성능 문제를 분석하고 찾아내는 도구를 제공합니다.

![functions-performance-tab](https://www.palantir.com/docs/resources/foundry/functions/functions-performance-tab.png)

워터폴(waterfall) 그래프는 각 작업을 X축의 시간 위에 펼쳐진 가로 막대로 나타냅니다. 각 작업에는 시간이 어디에 쓰였는지 보여 주는 표시가 있습니다.

* **Execute function**은 함수 코드를 실행하는 데 쓴 CPU 시간을 나타냅니다.
* **Load objects from arguments**와 **Load objects from links**는 그 밑에 있는 온톨로지 백엔드 데이터베이스 서비스(OSS)를 호출하는 데 쓴 시간을 나타냅니다.

함수 성능을 개선하려면 다음을 따르세요.

* 함수 컨텍스트 안에서 처리하는 것보다 더 빠르게 집계하고 링크를 탐색할 수 있도록 Objects API를 사용하세요([가능하면 Objects API 사용을 우선하기](#prefer-using-the-objects-api-where-possible)에서 설명).
* 순차적인 로드를 피하도록 온톨로지 백엔드 서비스 호출을 병렬로 수행하세요. `async`/`await` 호출이 여러 개라면 `Promise.all`을 사용해 모든 호출을 병렬로 기다리세요.
  * 예를 들어 흔한 패턴은 목록에 `.map()`을 써서 Promise들을 만든 다음, 그 결과 목록에 `Promise.all`을 적용하는 것입니다.
  * **중요:** `Promise.all()`을 사용하면 실행 속도는 빨라지지만 리소스 사용량이나 비용은 줄지 않습니다. 수행하는 작업 수는 같고, 단지 병렬로 실행될 뿐입니다. 대량(bulk) 작업은 더 빠르면서 비용 효율도 더 좋습니다.
* 실행 시간을 늘릴 수 있는 불필요한 중첩 반복문을 피하세요.

**설명**: `Promise`는 JavaScript에서 "나중에 완료될 비동기 작업의 결과"를 나타내는 객체이고, `await`는 그 결과가 나올 때까지 기다리는 문법입니다. 반복문 안에서 `await`를 하나씩 쓰면 질의 10개가 앞의 것이 끝나야 다음 것이 시작되므로 총 시간이 10개의 합이 됩니다. `Promise.all([p1, ..., p10])`은 10개를 동시에 보내고 모두 끝날 때까지 기다리므로 총 시간이 가장 느린 하나 정도로 줄어듭니다. 그러나 보낸 질의 수는 여전히 10개이므로 비용은 같습니다.

> **중간 요약**: Performance 탭의 워터폴 그래프로 코드 실행 시간과 온톨로지 로드 시간을 구분해 볼 수 있습니다. Objects API 활용, `Promise.all`을 통한 병렬 호출, 불필요한 중첩 반복문 제거로 성능을 개선하되, 병렬화는 속도만 높이고 비용은 줄이지 않는다는 점에 유의합니다.

<a id="choose-efficient-input-types"></a>
## 효율적인 입력 타입 고르기 (Choose efficient input types)

함수를 설계할 때 어떤 입력 파라미터 타입을 고르느냐가 성능에 큰 영향을 줍니다. 요구 사항을 충족하는 가장 효율적인 입력 타입을 사용하세요.

**모범 사례(Best practice):** 최대한의 효율과 확장성을 위해 가능하면 객체 집합(object set)을 사용하세요.
**허용(Acceptable):** 메모리에서 객체를 다뤄야 할 때는 객체 배열을 사용하세요.
**안티패턴(Anti-pattern):** 단일 객체 파라미터는 객체 타입에 인스턴스가 하나뿐이거나, 특정 비즈니스 로직이 정말로 객체별 처리를 요구할 때만 사용해야 합니다.

| 입력 타입 | 효율 | 사용 사례 |
|------------|------------|----------|
| 객체 집합(Object set) | 최상 | 질의 가능한 객체 집합. 집계만 필요하다면 미리 로드하는 비용이 없음 |
| 객체 배열(Object array) | 양호 | 특정 객체들을 순회해야 할 때 |
| 단일 객체(Single object) | 가장 비효율적 | 비즈니스 로직상 한 번에 하나의 객체를 처리해야 할 때 |

<a id="best-practice-object-sets"></a>
### 모범 사례: 객체 집합 (Best practice: Object sets)

파라미터로 전달된 객체는 객체 데이터를 로드하기 위한 온톨로지 질의를 일으킵니다. 객체 하나만 입력으로 받아도 그 객체를 메모리에 로드하는 호출이 발생합니다.

**객체 집합은** 실제로 데이터가 필요할 때까지 로딩을 미루므로 더 바람직합니다. 집계(예: 개수나 합계)만 필요하다면, 온톨로지 백엔드가 개별 객체를 로드하지 않고 집계를 계산합니다.

```python tab="Python"
from functions.api import function, Float
from ontology_sdk.ontology.objects import ExampleDataAircraft
from ontology_sdk.ontology.object_sets import ExampleDataAircraftObjectSet

# 덜 효율적: 단일 객체는 미리 로딩을 일으킴

@function()
def get_aircraft_name(aircraft: ExampleDataAircraft) -> str:
    return aircraft.display_name

# 보통: 객체 배열도 미리 로딩을 일으킴

@function()
def get_aircrafts_names(aircraft_array: list[ExampleDataAircraft]) -> list[str]:
    return [aircraft.display_name for aircraft in aircraft_array]

# 가장 효율적: 객체 집합은 필요할 때까지 로딩을 미룸

# 여기서는 집계된 값만 함수 메모리에 로드됨
@function()
def count_aircrafts(aircraft_set: ExampleDataAircraftObjectSet) -> Float:
    return aircraft_set.count().compute()
```

(원문에는 같은 세 가지 경우를 보여 주는 TypeScript v2 버전과 TypeScript v1 버전 예제 코드도 있습니다.)

**설명**: 세 함수는 입력 타입만 다릅니다. 앞의 두 함수는 호출되는 순간 항공기 객체의 모든 속성(property) 데이터가 함수 메모리로 옮겨집니다. 세 번째 함수의 `aircraft_set`은 "어떤 객체들인지에 대한 정의"일 뿐 데이터가 아직 로드되지 않은 상태이고, `count().compute()`를 호출하면 백엔드가 개수를 세어 숫자 하나만 돌려줍니다. SQL로 보면 `SELECT * FROM aircraft`로 모든 행을 가져와 애플리케이션에서 세는 것과 `SELECT COUNT(*) FROM aircraft`로 숫자만 받는 것의 차이입니다.

> **중간 요약**: 입력 타입은 객체 집합, 객체 배열, 단일 객체 순으로 효율적입니다. 객체 집합은 데이터 로딩을 실제로 필요할 때까지 미루고 집계를 백엔드에서 처리하게 해 줍니다.

<a id="load-objects-efficiently"></a>
## 객체를 효율적으로 로드하기 (Load objects efficiently)

함수 성능 문제의 흔한 원인은 객체를 비효율적으로 로드하는 것입니다. 반복문에서 객체를 하나씩 로드하면 반복할 때마다 온톨로지와 한 번씩 왕복(round-trip)하게 됩니다.

<a id="anti-pattern-loading-objects-one-by-one"></a>
### 안티패턴: 객체를 하나씩 로드하기 (Anti-pattern: Loading objects one by one)

반복문 안에서 객체를 로드하는 것은 성능에 큰 영향을 주는 안티패턴입니다. 반복할 때마다 온톨로지에 별도의 질의를 보냅니다.

```python tab="Python"
from functions.api import function
from ontology_sdk import FoundryClient
from ontology_sdk.ontology.objects import ExampleDataAircraft

# 안티패턴: 반복문에서 객체를 하나씩 로드

@function()
def for_loop_worst(pks_list: list[str]) -> int:
    client = FoundryClient()
    seats_count = 0

    for current_pk in pks_list:
        aircrafts = client.ontology.objects.ExampleDataAircraft.where(
            ExampleDataAircraft.object_type.tail_number == current_pk
        ).page()
        aircraft = aircrafts.data[0]
        seats_count += aircraft.number_of_seats or 0

    return seats_count

# 더 나음: 한 번의 호출로 모든 객체를 로드한 다음 순회

@function()
def for_loop_better(pks_list: list[str]) -> int:
    client = FoundryClient()
    seats_count = 0

    aircrafts = client.ontology.objects.ExampleDataAircraft.where(
        ExampleDataAircraft.object_type.tail_number.in_(pks_list)
    )

    for aircraft in aircrafts:
        seats_count += aircraft.number_of_seats or 0

    return seats_count

# 가장 좋음: 백엔드가 집계를 수행하게 함

@function()
def for_loop_best(pks_list: list[str]) -> int:
    client = FoundryClient()

    result = client.ontology.objects.ExampleDataAircraft.where(
        ExampleDataAircraft.object_type.tail_number.in_(pks_list)
    ).sum(ExampleDataAircraft.object_type.number_of_seats).compute()

    return int(result or 0)
```

(원문에는 같은 세 단계를 보여 주는 TypeScript v2 버전과 TypeScript v1 버전 예제 코드도 있습니다.)

**설명**: 세 함수 모두 항공기 등록번호(`tail_number`) 목록을 입력받아 좌석 수 합계를 반환합니다. `for_loop_worst`는 등록번호 100개가 들어오면 질의를 100번 보냅니다(`WHERE tail_number = 'A'`를 100번 실행). `for_loop_better`는 `in_(pks_list)`로 `WHERE tail_number IN (...)` 질의 한 번에 모든 객체를 가져온 뒤 함수 안에서 더합니다. `for_loop_best`는 `.sum(...)`으로 `SELECT SUM(number_of_seats) ... WHERE tail_number IN (...)`에 해당하는 계산을 백엔드에서 끝내고 숫자 하나만 받으므로, 질의 수와 함수로 전송되는 데이터 양이 모두 가장 적습니다.

<a id="best-practice-backend-aggregations"></a>
### 모범 사례: 백엔드 집계 (Best practice: Backend aggregations)

개수, 합계, 평균 같은 집계를 계산해야 할 때는 객체를 로드해 함수 안에서 계산하는 대신 온톨로지 백엔드의 집계 기능을 사용하세요.

> **중간 요약**: 반복문 안에서 객체를 하나씩 질의하면 반복 횟수만큼 왕복이 생깁니다. 한 번의 질의로 모두 불러오는 것이 낫고, 집계가 목적이라면 백엔드 집계를 쓰는 것이 가장 좋습니다.

<a id="prefer-using-the-objects-api-where-possible"></a>
## 가능하면 Objects API 사용을 우선하기 (Prefer using the Objects API where possible)

[Workshop의 함수 기반 열(function-backed columns)](https://www.palantir.com/docs/foundry/workshop/widgets-object-table/#function-backed-columns)은 관련 객체의 개수를 세는 것처럼 각 객체의 링크를 집계해 값을 계산하는 경우가 많습니다. 함수 기반 열은 코드를 작성하지 않고 Workshop에서 직접 구성하는 [파생 속성(derived properties)](https://www.palantir.com/docs/foundry/workshop/derived-properties/)과는 다릅니다.

아래 코드는 동작은 하지만, 함수가 링크된 객체를 모두 가져온 다음 집계(이 경우 개수 계산)를 수행해야 합니다.

```typescript tab="TypeScript v2"
import { ObjectSpecifier, Osdk } from "@osdk/client";
import { Employee } from "@ontology/sdk";
import { Integer } from "@osdk/functions";

export default async function getEmployeeProjectCount(
    employees: Osdk.Instance<Employee>[]
): Promise<Record<ObjectSpecifier<Employee>, Integer>> {
    const allEmployeeProjectCounts = await Promise.all(
        employees.map(async employee => {
            let count = 0;
            for await (const project of employee.$link.workHistory.asyncIter()) {
                count++;
            }
            return count;
        })
    );

    const result: Record<ObjectSpecifier<Employee>, Integer> = {};
    employees.forEach((employee, i) => {
        result[employee.$objectSpecifier] = allEmployeeProjectCounts[i];
    });

    return result;
}
```

(원문에는 같은 동작의 TypeScript v1 버전 예제 코드도 있습니다.)

위 코드는 비동기 API와 비동기 함수를 활용하지만([링크 탐색 최적화](#optimizing-link-traversals) 참고), Objects API가 제공하는 집계 메서드를 사용하는 편이 유리한 경우가 많습니다.

```typescript tab="TypeScript v2"
import { ObjectSpecifier, Osdk } from "@osdk/client";
import { Employee } from "@ontology/sdk";
import { Integer } from "@osdk/functions";

export default async function getEmployeeProjectCount(
    employees: Osdk.Instance<Employee>[]
): Promise<Record<ObjectSpecifier<Employee>, Integer>> {
    const result: Record<ObjectSpecifier<Employee>, Integer> = {};

    // 프로젝트 객체 자체를 로드하는 대신, 백엔드 집계로 각 직원의 링크된 프로젝트 수를 셈
    const counts = await Promise.all(
        employees.map(async employee => ({
            employee,
            count: await employee.$link.workHistory.aggregate({ $select: { $count: "unordered" } }),
        }))
    );

    counts.forEach(({ employee, count }) => {
        result[employee.$objectSpecifier] = count.$count;
    });

    return result;
}
```

(원문에는 TypeScript v1 버전 예제 코드도 있습니다. 이 버전은 `Objects.search().project()`로 전달된 직원 ID에 해당하는 프로젝트를 필터링한 다음 `groupBy(project => project.employeeId.byFixedWidths(1))`와 `count()`로 직원 ID별 프로젝트 수를 한 번의 집계로 구하고, 각 버킷의 `key.min`을 직원 ID로 사용합니다.)

이런 방식으로, 링크된 모든 프로젝트를 먼저 가져오지 않고도 집계를 수행할 수 있습니다.

**설명**: 두 함수는 모두 직원 배열을 입력받아 "직원별 프로젝트 수"를 담은 맵(`Record`)을 반환하며, Workshop 표의 한 열을 채우는 데 쓰입니다. 첫 번째 코드는 `asyncIter()`로 프로젝트 객체를 하나하나 받아 와 `count++`로 세므로, 프로젝트가 많을수록 전송되는 데이터가 늘어납니다. 두 번째 코드는 `aggregate({ $select: { $count: "unordered" } })`로 백엔드에 개수만 요청하므로 프로젝트 객체는 함수로 전혀 넘어오지 않습니다. `$objectSpecifier`는 객체를 가리키는 식별자로, 결과 맵의 키로 쓰입니다.

**주의**: 집계의 일반적인 제한은 여전히 적용됩니다. 특히 문자열 ID에 대한 `.topValues()`는 상위 1000개 값만 반환합니다. 집계는 현재 최대 10K개 버킷으로 제한되므로, 원하는 결과를 얻으려면 집계를 여러 번 수행해야 할 수도 있습니다. 자세한 내용은 [집계 계산하기(TSv1)](../13_functions-on-objects/07_api-object-sets.md#computing-aggregations)를 참고하세요.

**설명**: 버킷(bucket)은 group by 결과의 그룹 하나를 말합니다. 예를 들어 직원 ID별로 묶으면 직원 한 명이 버킷 하나가 되므로, 직원 수가 10,000명을 넘으면 한 번의 집계로는 모든 결과를 받을 수 없고 직원 목록을 나눠 여러 번 집계해야 합니다.

> **중간 요약**: 링크된 객체의 개수 같은 값은 객체를 모두 가져와 세기보다 Objects API의 집계 메서드로 백엔드에서 계산하는 것이 유리합니다. 단, `.topValues()`의 1000개 제한과 집계당 10K 버킷 제한이 있습니다.

<a id="optimizing-link-traversals"></a>
## 링크 탐색 최적화 (Optimizing link traversals)

함수 성능 문제의 가장 흔한 원인은 링크를 비효율적으로 탐색하는 것입니다. 대개 많은 객체를 순회하는 반복문을 작성하고, 반복할 때마다 관련 객체를 로드하는 API를 호출할 때 이런 일이 생깁니다.

```typescript tab="TypeScript v2"
for (const employee of employees) {
    const pastProjects = await employee.$link.workHistory.fetchPage();
}
```

(원문에는 같은 패턴의 TypeScript v1 버전(`employee.workHistory.all()`)도 있습니다.)

이 예제에서는 반복할 때마다 직원 한 명의 과거 프로젝트를 로드하므로 매번 데이터베이스와 왕복이 발생합니다. 이런 지연을 피하려면 많은 링크를 한꺼번에 탐색할 때 비동기 링크 탐색 API를 사용하면 됩니다. 아래는 링크를 비동기로 로드하도록 작성한 함수의 예입니다.

```typescript tab="TypeScript v2"
import { Osdk } from "@osdk/client";
import { Employee, Project } from "@ontology/sdk";

async function getProjects(employee: Osdk.Instance<Employee>): Promise<Osdk.Instance<Project>[]> {
    const projects: Osdk.Instance<Project>[] = [];
    for await (const project of employee.$link.workHistory.asyncIter()) {
        projects.push(project);
    }
    return projects;
}

export default async function findEmployeeWithMostProjects(
    employees: Osdk.Instance<Employee>[]
): Promise<Osdk.Instance<Employee>> {
    // 직원마다 프로젝트를 로드하는 요청을 보내 모든 링크를 병렬로 로드
    const allEmployeeProjects = await Promise.all(employees.map(employee => getProjects(employee)));

    // 결과를 순회하며 프로젝트가 가장 많은 직원을 찾음
    let result = employees[0];
    let maxProjectsLength = allEmployeeProjects[0].length;
    for (let i = 1; i < employees.length; i++) {
        if (allEmployeeProjects[i].length > maxProjectsLength) {
            result = employees[i];
            maxProjectsLength = allEmployeeProjects[i].length;
        }
    }

    return result;
}
```

(원문에는 `allAsync()`와 `Promise.all`을 사용하는 TypeScript v1 버전 예제 코드도 있습니다.)

TypeScript v1 예제는 ES6 [async 함수 ↗](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)를 사용하므로, `.getAsync()`와 `.allAsync()` 메서드가 반환하는 `Promise` 값을 편리하게 처리할 수 있습니다. TypeScript v2 예제는 `Promise.all()`을 `$link` 및 `asyncIter()`와 함께 사용해 각 직원의 링크된 프로젝트를 병렬로 로드합니다.

**설명**: 이 함수는 직원 배열을 입력받아 프로젝트가 가장 많은 직원을 반환합니다. 핵심 줄은 `Promise.all(employees.map(employee => getProjects(employee)))`입니다. `map`이 직원마다 "프로젝트를 불러오는 작업"을 하나씩 시작시키고, `Promise.all`이 그 작업들이 동시에 진행되도록 한 뒤 모두 끝나기를 기다립니다. 직원이 50명이면 앞의 반복문 방식은 왕복 50번을 차례로 기다리지만, 이 방식은 50번을 동시에 진행합니다.

> **중간 요약**: 반복문 안에서 링크를 하나씩 탐색하면 반복마다 왕복이 생기므로, 비동기 링크 탐색 API와 `Promise.all`로 여러 링크를 병렬로 로드해야 합니다.

<a id="understand-async-operations-and-resource-usage"></a>
## 비동기 작업과 리소스 사용 이해하기 (Understand async operations and resource usage)

비동기 작업은 함수 실행 속도를 높일 수 있지만 리소스 사용량을 줄이지는 않을 수 있습니다. 비용 최적화를 위해서는 이 차이를 이해하는 것이 중요합니다.

```typescript tab="TypeScript v2"
// forLoopAsync.ts - 실행은 더 빠르지만 여전히 온톨로지 호출이 여러 번 발생
import { Client, ObjectSet, Osdk } from "@osdk/client";
import { ExampleDataAircraft } from "@ontology/sdk";
import { Integer } from "@osdk/functions";

async function getMaintenanceEventCount(
    client: Client,
    aircraft: Osdk.Instance<ExampleDataAircraft>
): Promise<Integer> {
    const aircraftSet = client(ExampleDataAircraft).where({
        tailNumber: { $eq: aircraft.tailNumber }
    });
    const maintenanceEvents = aircraftSet.pivotTo("exampleDataAircraftMaintenanceEvent");
    const result = await maintenanceEvents.aggregate({
        $select: { $count: "unordered" }
    });
    return result.$count ?? 0;
}

export default async function forLoopAsync(
    client: Client,
    aircraftSet: ObjectSet<ExampleDataAircraft>
): Promise<Integer> {
    const allObjects: Osdk.Instance<ExampleDataAircraft>[] = [];
    for await (const obj of aircraftSet.asyncIter()) {
        allObjects.push(obj);
    }

    const futures = allObjects.map(obj => getMaintenanceEventCount(client, obj));
    const results = await Promise.all(futures);

    return results.reduce((sum, count) => sum + count, 0);
}

// bulkProcessing.ts - 가장 좋음: 온톨로지 작업 한 번
import { ObjectSet } from "@osdk/client";
import { ExampleDataAircraft } from "@ontology/sdk";
import { Integer } from "@osdk/functions";

export default async function bulkProcessing(
    aircraftSet: ObjectSet<ExampleDataAircraft>
): Promise<Integer> {
    const allMaintenanceEvents = aircraftSet.pivotTo("exampleDataAircraftMaintenanceEvent");
    const result = await allMaintenanceEvents.aggregate({
        $select: { $count: "unordered" }
    });
    return result.$count ?? 0;
}
```

(원문에는 search around를 사용한 대량 처리만 보여 주는 Python 버전과, 두 방식을 모두 보여 주는 TypeScript v1 버전 예제 코드도 있습니다.)

**설명**: 두 함수 모두 항공기 객체 집합을 입력받아 그 항공기들의 정비 이벤트 총 개수를 반환합니다. `forLoopAsync`는 항공기를 모두 로드한 뒤 항공기마다 정비 이벤트 개수를 세는 질의를 병렬로 보냅니다. 항공기가 200대면 질의도 200번입니다. `bulkProcessing`은 `pivotTo`로 "이 항공기들에 링크된 모든 정비 이벤트"라는 객체 집합을 만든 뒤 한 번만 개수를 셉니다. `pivotTo`(Python과 TypeScript v1에서는 search around)는 SQL의 조인에 해당하는 링크 이동을 백엔드에서 수행하는 연산입니다.

**팁**: 비동기 작업은 비용이 아니라 속도를 개선합니다(Async operations improve speed, not cost). `Promise.all()` 같은 비동기 작업을 사용하면 작업을 병렬로 실행해 실행 속도를 높일 수 있습니다. 하지만 비동기 작업은 **리소스 사용량이나 비용을 줄이지 않고**, 단지 더 빠르게 만들 뿐이라는 점을 이해하는 것이 중요합니다.

예를 들어 개별 질의를 반복하는 루프를 병렬화하면 순차 실행보다 빠르지만, 수행하는 질의 수는 여전히 같습니다. **계산을 백엔드로 넘기는 대량(bulk) 작업은** 두 방식 모두보다 더 빠르면서 리소스 효율도 더 좋습니다.

> **중간 요약**: 질의를 병렬로 보내면 빨라지지만 질의 수와 비용은 그대로입니다. `pivotTo`나 search around처럼 계산을 백엔드에 넘기는 대량 작업이 속도와 비용 모두에서 가장 좋습니다.

<a id="write-efficient-ontology-edits"></a>
## 효율적인 온톨로지 편집 작성하기 (Write efficient ontology edits)

객체를 편집(edit)하는 함수를 작성할 때도 같은 대량 로딩 원칙을 적용하세요. 객체를 하나씩 로드하지 말고 미리 모두 로드하세요.

<a id="editing-large-set-of-objects"></a>
### 대량의 객체 편집하기 (Editing large set of objects)

많은 수의 객체를 편집할 때는 페이지 나누기(pagination)를 사용해(명시적으로, 또는 `iterate`나 `asyncIter`를 통해 암묵적으로) 모든 것을 한 번에 메모리에 로드하지 않고 다룰 수 있는 크기의 묶음으로 처리하세요.

```python tab="Python"
from functions.api import function, OntologyEdit
from ontology_sdk.ontology.objects import ExampleDataAircraft
from ontology_sdk.ontology.object_sets import ExampleDataAircraftObjectSet
from ontology_sdk import FoundryClient

# 단일 객체 편집

@function(edits=[ExampleDataAircraft])
def edit_aircraft_name(aircraft: ExampleDataAircraft) -> list[OntologyEdit]:
    ontology_edits = FoundryClient().ontology.edits()
    editable = ontology_edits.objects.ExampleDataAircraft.edit(aircraft)
    editable.display_name = "new display name"
    return ontology_edits.get_edits()

# 순회를 사용하는 객체 집합 대량 편집

@function(edits=[ExampleDataAircraft])
def edit_all_aircrafts(aircraft_set: ExampleDataAircraftObjectSet) -> list[OntologyEdit]:
    ontology_edits = FoundryClient().ontology.edits()

    for aircraft in aircraft_set.iterate():
        editable = ontology_edits.objects.ExampleDataAircraft.edit(aircraft)
        editable.display_name = "new display name"

    return ontology_edits.get_edits()

# 대안: 페이지 나누기

# 객체를 묶음 단위로 처리함. 위의 iterate() 메서드가 내부에서 이 작업을 대신 처리함.
@function(edits=[ExampleDataAircraft])
def edit_all_with_pagination(aircraft_set: ExampleDataAircraftObjectSet) -> list[OntologyEdit]:
    edits = FoundryClient().ontology.edits()

    next_token = None
    while True:
        page = aircraft_set.page(1000, next_token)
        for aircraft in page.data:
            editable = edits.objects.ExampleDataAircraft.edit(aircraft)
            editable.status = "reviewed"

        next_token = page.next_page_token
        if not next_token:
            break

    return edits.get_edits()
```

(원문에는 단일 객체 편집과 `asyncIter()`를 사용한 객체 집합 편집을 보여 주는 TypeScript v2 버전, 그리고 단일 객체, 배열, 객체 집합 편집을 보여 주는 TypeScript v1 버전 예제 코드도 있습니다.)

**설명**: 세 번째 함수 `edit_all_with_pagination`이 페이지 나누기의 동작을 그대로 보여 줍니다. `aircraft_set.page(1000, next_token)`은 객체를 최대 1,000개씩 가져오고, 응답에 담긴 `next_page_token`을 다음 호출에 넘겨 이어지는 1,000개를 받습니다. 토큰이 비어 있으면 마지막 페이지이므로 반복을 끝냅니다. 두 번째 함수의 `iterate()`는 이 토큰 처리를 내부에서 자동으로 해 주므로 코드가 더 짧습니다. 어느 쪽이든 수십만 개의 객체를 한 번에 메모리에 올리지 않아도 됩니다.

> **중간 요약**: 편집 함수에서도 객체를 미리 대량으로 로드하고, 객체가 많을 때는 `iterate`, `asyncIter`, 또는 명시적 페이지 나누기로 묶음 단위로 처리해 메모리 사용을 제한합니다.

<a id="optimize-derived-column-generation"></a>
## 파생 열 생성 최적화 (Optimize derived column generation)

Workshop은 객체 함수(functions on objects, FOO)를 사용해 함수 기반 열을 계산하는 것을 지원합니다. Workshop 애플리케이션은 보통 객체 테이블의 내용 중 수십 개 행을 넣어 이 함수들을 호출합니다. 그러면 함수는 각 객체를 파생 열에 표시할 값에 대응시킨 맵을 반환합니다.

**설명**: 예를 들어 Workshop 표에 `Flight` 객체 30개가 보이고 "지연 위험도"라는 열이 함수 기반 열로 설정되어 있다면, Workshop은 이 30개 객체를 함수에 넘기고, 함수는 `{F100: 0.2, F101: 0.7, ...}` 같은 객체별 값의 맵을 돌려줍니다. 사용자가 스크롤할 때마다 다음 행들에 대해 다시 호출되므로, 이 함수는 짧은 시간 안에 반복적으로 실행됩니다.

<a id="base-implementation-without-optimization"></a>
### 최적화하지 않은 기본 구현 (Base implementation without optimization)

아래는 기준이 되는, 최적화하지 않은 구현입니다.

```typescript tab="TypeScript v2"
import { ObjectSet, ObjectSpecifier, Osdk } from "@osdk/client";
import { ObjectTypeA } from "@ontology/sdk";
import { Double } from "@osdk/functions";

// 주어진 객체에 필요한 값을 계산하는 함수의 예
function computeForThisObject(obj: Osdk.Instance<ObjectTypeA, never, "exampleProperty">, scalar: Double): Double | undefined {
    if (scalar === 0) {
        // 0으로 나누기 오류
        return undefined;
    }
    // exampleProperty가 정의되어 있으면 나누고, 아니면 undefined를 반환
    return obj.exampleProperty ? obj.exampleProperty / scalar : undefined;
}

/**
 * 이 함수는 ObjectSet을 입력받아 파생 열을 출력으로 생성함.
 * 파생 열은 각 객체 인스턴스를 그 열을 채울 숫자 값에 대응시킴.
 * 이 구현은 객체 속성을 상수 값으로 계산하는 단순한 for 반복문임.
 * 아래에서 개선할 기준 사례임.
 */
export default async function getDerivedColumnNoOptimization(
    objects: ObjectSet<ObjectTypeA>,
    scalar: Double
): Promise<Record<ObjectSpecifier<ObjectTypeA>, Double>> {
    // 반환할 결과 맵 정의
    const resultMap: Record<ObjectSpecifier<ObjectTypeA>, Double> = {};

    /* 메모리에 로드할 수 있는 객체 수에는 제한이 있음.
     * 현재 객체 집합 로드 제한은 enforced limit 문서를 참고.
     */
    for await (const obj of objects.asyncIter({ $select: ["exampleProperty"] })) {
        // 로드한 각 객체에 대해 계산을 수행하고, 결과가 정의되어 있으면 결과 맵에 저장
        const result = computeForThisObject(obj, scalar);
        if (result !== undefined) {
            resultMap[obj.$objectSpecifier] = result;
        }
    }

    return resultMap;
}
```

(원문에는 같은 구현의 TypeScript v1 버전 예제 코드도 있습니다.)

**설명**: 이 함수는 객체 집합과 숫자 `scalar`를 입력받아, 각 객체의 `exampleProperty`를 `scalar`로 나눈 값을 객체별로 담은 맵을 반환합니다. `asyncIter({ $select: ["exampleProperty"] })`는 필요한 속성 하나만 골라 객체를 차례로 받아 오므로, SQL의 `SELECT example_property FROM ...`처럼 불필요한 열을 가져오지 않습니다. 각 객체의 계산은 앞의 계산이 끝난 뒤에 순서대로 진행됩니다.

<a id="parallel-execution-optimization"></a>
### 병렬 실행 최적화 (Parallel execution optimization)

계산이 복잡하다면 비동기 실행을 사용해 컴퓨팅 시간을 줄일 수 있습니다. 이렇게 하면 각 객체에 대한 계산이 병렬로 실행됩니다.

```typescript tab="TypeScript v2"
import { ObjectSet, ObjectSpecifier, Osdk } from "@osdk/client";
import { ObjectTypeA } from "@ontology/sdk";
import { Double } from "@osdk/functions";

// 주어진 객체에 필요한 값을 계산하는 함수의 예
async function computeForThisObject(obj: Osdk.Instance<ObjectTypeA, never, "exampleProperty">, scalar: Double): Promise<Double | undefined> {
    if (scalar === 0) {
        // 0으로 나누기 오류
        return undefined;
    }
    // exampleProperty가 정의되어 있으면 나누고, 아니면 undefined를 반환
    return obj.exampleProperty ? obj.exampleProperty / scalar : undefined;
}

/**
 * 이 함수는 ObjectSet을 입력받아 파생 열을 출력으로 생성함.
 */
export default async function getDerivedColumnParallel(
    objects: ObjectSet<ObjectTypeA>,
    scalar: Double
): Promise<Record<ObjectSpecifier<ObjectTypeA>, Double>> {
    // 결과 맵 정의
    const resultMap: Record<ObjectSpecifier<ObjectTypeA>, Double> = {};

    /* 메모리에 로드할 수 있는 객체 수에는 제한이 있음.
     * 현재 객체 집합 로드 제한은 enforced limit 문서를 참고.
     * Workshop은 사용자가 스크롤할 때 지연 로딩(lazy-load)할 수 있으므로 문제가 되지 않음.
     */
    const allObjs: Osdk.Instance<ObjectTypeA, never, "exampleProperty">[] = [];
    for await (const obj of objects.asyncIter({ $select: ["exampleProperty"] })) {
        allObjs.push(obj);
    }

    // 배열의 각 객체에 대해 병렬 계산을 시작
    const promises = allObjs.map(currObject => computeForThisObject(currObject, scalar));

    // Promise.all로 도우미 함수의 비동기 실행을 병렬화
    const allResolvedPromises = await Promise.all(promises);

    // 결과로 resultMap 채우기
    allObjs.forEach((obj, i) => {
        const result = allResolvedPromises[i];
        if (result !== undefined) {
            resultMap[obj.$objectSpecifier] = result;
        }
    });

    return resultMap;
}
```

(원문에는 같은 구현의 TypeScript v1 버전 예제 코드도 있습니다.)

**설명**: 기본 구현과 달라진 점은 두 가지입니다. `computeForThisObject`가 `async` 함수가 되었고, 객체를 먼저 모두 배열에 모은 뒤 `allObjs.map(...)`으로 모든 계산을 한꺼번에 시작하고 `Promise.all`로 기다립니다. 객체별 계산 안에서 온톨로지 질의 같은 기다림이 있는 작업을 한다면, 그 기다림이 겹쳐 진행되어 전체 시간이 줄어듭니다.

<a id="advanced-ontology-filtering-within-computation"></a>
### 고급: 계산 안에서 온톨로지 필터링하기 (Advanced: Ontology filtering within computation)

객체마다 온톨로지에 질의해야 하는 더 복잡한 경우는 아래 예제를 참고하세요.
**참고:** Workshop의 [Chart XY 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-chart/)을 채우는 `TwoDimensionalAggregation`에도 같은 방법을 적용할 수 있습니다. 객체 인스턴스 목록 대신 계산할 범주 문자열(버킷) 목록을 전달하면 됩니다. 아래는 그 예입니다.

```typescript tab="TypeScript v2"
import { Client, ObjectSet, ObjectSpecifier, Osdk } from "@osdk/client";
import { ObjectTypeA, ObjectTypeB } from "@ontology/sdk";
import { Double } from "@osdk/functions";

// 객체들의 값을 합산
async function sumValue(objs: ObjectSet<ObjectTypeB>): Promise<Double> {
    const aggregation = await objs.aggregate({
        $select: { "propertyToAggregateB:sum": "unordered" },
    });
    return aggregation.propertyToAggregateB.sum ?? 0;
}

// 값이 null이 아닌 객체들의 값을 합산
async function sumValueIfPresent(objs: ObjectSet<ObjectTypeB>): Promise<Double> {
    const aggregation = await objs
        .where({ metric: { $isNull: false } })
        .aggregate({ $select: { "propertyToAggregateA:sum": "unordered" } });
    return aggregation.propertyToAggregateA.sum ?? 0;
}

async function computeMetricB(objs: ObjectSet<ObjectTypeB>): Promise<Double> {
    // 계산식의 각 부분에 대한 호출을 준비하고 병렬로 실행
    const [sum, sumIfPresent] = await Promise.all([sumValue(objs), sumValueIfPresent(objs)]);

    // 계산 수행
    return sum / sumIfPresent;
}

/**
 * 주어진 객체에 필요한 값을 계산하는 함수의 예.
 * 주어진 객체에 대해 온톨로지에 질의함(다른 객체 필터링, 다른 객체 집합으로 pivot 등).
 */
async function computeForThisObjectFilterOntology(client: Client, obj: Osdk.Instance<ObjectTypeA, never, "exampleProperty">): Promise<Double> {
    // 몇몇 속성으로 필터링해 객체 집합 생성
    const currObjectSet = client(ObjectTypeB).where({ property: { $eq: obj.exampleProperty } });
    // 참고: 두 객체 타입 사이에 링크가 이미 있다면 다음과 같이 할 수도 있음
    // const currObjectSet = obj.$link.objectTypeB;

    // 이 객체 집합에 대한 집계 계산
    return await computeMetricB(currObjectSet);
}

/**
 * ObjectSet을 입력받아 파생 열을 생성하며,
 * 각 객체에 대해 computeForThisObjectFilterOntology를 병렬로 호출함.
 */
export default async function getDerivedColumnFilterOntology(
    client: Client,
    objects: ObjectSet<ObjectTypeA>
): Promise<Record<ObjectSpecifier<ObjectTypeA>, Double>> {
    const resultMap: Record<ObjectSpecifier<ObjectTypeA>, Double> = {};

    const allObjs: Osdk.Instance<ObjectTypeA, never, "exampleProperty">[] = [];
    for await (const obj of objects.asyncIter({ $select: ["exampleProperty"] })) {
        allObjs.push(obj);
    }

    const results = await Promise.all(
        allObjs.map(obj => computeForThisObjectFilterOntology(client, obj))
    );
    allObjs.forEach((obj, i) => {
        resultMap[obj.$objectSpecifier] = results[i];
    });

    return resultMap;
}
```

(원문에는 `Objects.search()`와 `searchAroundObjectTypeB()`를 사용하는 TypeScript v1 버전 예제 코드도 있습니다.)

**설명**: 이 함수는 `ObjectTypeA` 객체마다, 그 객체의 `exampleProperty` 값과 일치하는 `ObjectTypeB` 객체들을 찾아 두 가지 합계의 비율을 계산합니다. 병렬화가 두 단계로 일어납니다. 바깥쪽 `Promise.all`은 A 객체들에 대한 계산을 동시에 진행하고, `computeMetricB` 안쪽의 `Promise.all`은 한 객체에 대해 필요한 두 집계 질의(`sumValue`와 `sumValueIfPresent`)를 동시에 보냅니다. 합계 자체는 `aggregate`로 백엔드에서 계산되므로 B 객체들은 함수로 로드되지 않습니다.

<a id="converting-to-twodimensionalaggregation"></a>
### TwoDimensionalAggregation으로 변환하기 (Converting to TwoDimensionalAggregation)

Workshop의 [Chart XY 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-chart/)에 사용하려면, 계산한 결과로 `TwoDimensionalAggregation`을 만들 수 있습니다.

```typescript tab="TypeScript v2"
import { ObjectSet, Osdk } from "@osdk/client";
import { ObjectTypeA } from "@ontology/sdk";
import { Double, TwoDimensionalAggregation } from "@osdk/functions";

export default async function getDerivedColumnParallelAsTwoDimensional(
    objects: ObjectSet<ObjectTypeA>,
    scalar: Double
): Promise<TwoDimensionalAggregation<string, Double>> {
    const allObjs: Osdk.Instance<ObjectTypeA, never, "exampleProperty">[] = [];
    for await (const obj of objects.asyncIter({ $select: ["exampleProperty"] })) {
        allObjs.push(obj);
    }

    // 위 병렬 실행 예제의 computeForThisObject를 재사용
    const allResolvedPromises = await Promise.all(allObjs.map(currObject => computeForThisObject(currObject, scalar)));

    // 계산한 값으로, 기본 키 속성을 키로 하는 TwoDimensionalAggregation 생성
    return allObjs
        .map((obj, i) => ({ key: String(obj.$primaryKey), value: allResolvedPromises[i] }))
        .filter((bucket): bucket is { key: string; value: Double } => bucket.value !== undefined);
}
```

(원문에는 `FunctionsMap`의 항목을 `buckets` 배열로 바꾸는 TypeScript v1 버전 예제 코드도 있습니다.)

**설명**: `TwoDimensionalAggregation`은 차트용 데이터 형식으로, `{ key, value }` 쌍의 목록입니다. 여기서는 각 객체의 기본 키(primary key)를 문자열로 바꿔 X축 범주(`key`)로 쓰고, 계산 결과를 Y축 값(`value`)으로 씁니다. 마지막 `.filter(...)`는 계산 결과가 `undefined`인 항목을 빼서 차트에 빈 값이 들어가지 않도록 합니다.

> **중간 요약**: Workshop 함수 기반 열은 객체 수십 개에 대해 반복 호출되므로, 필요한 속성만 선택해 로드하고 객체별 계산을 `Promise.all`로 병렬화하며, 객체마다 필요한 집계는 백엔드 집계로 처리합니다. 같은 결과를 `TwoDimensionalAggregation`으로 바꿔 Chart XY 위젯에 쓸 수도 있습니다.

## 정리

- 함수 비용은 실행당 4 컴퓨트초의 고정 오버헤드, vCPU 시간, 온톨로지 질의와 모델 호출 등 외부 호출 비용으로 구성됩니다.
- Performance 탭의 워터폴 그래프로 코드 실행 시간과 온톨로지 로드 시간을 구분해 병목을 찾습니다.
- 입력 타입은 객체 집합이 가장 효율적이고, 반복문 안에서 객체나 링크를 하나씩 로드하는 것은 대표적인 안티패턴입니다.
- 개수, 합계 같은 집계는 객체를 가져와 계산하지 말고 백엔드 집계(Objects API)에 맡깁니다. 집계에는 1000개 상위 값, 10K 버킷 제한이 있습니다.
- `Promise.all`을 통한 병렬화는 속도만 높이고 비용은 줄이지 않으며, 계산을 백엔드로 넘기는 대량 작업이 속도와 비용 모두에서 가장 좋습니다.
- 대량 편집은 페이지 나누기나 `iterate`/`asyncIter`로 묶음 처리하고, Workshop 파생 열 함수는 필요한 속성만 로드하고 병렬화합니다.
