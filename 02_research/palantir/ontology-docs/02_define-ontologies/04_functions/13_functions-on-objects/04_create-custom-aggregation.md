# 사용자 정의 집계 만들기 (Create a custom aggregation (TSv1))

- 원문: https://www.palantir.com/docs/foundry/functions/create-custom-aggregation/
- 사이드바 위치: Define Ontologies > Functions > Functions on objects > Create a custom aggregation (TSv1)

이 페이지는 TypeScript v1 함수(function)로 온톨로지 데이터를 집계(aggregation)한 뒤, 그 결과를 가공해서 Workshop 차트에 보여 줄 사용자 정의 집계를 만드는 방법을 단계별로 설명합니다. 부서별 월간 지출을 집계하고 이를 바탕으로 앞으로 6개월의 지출을 추정하는 예제를 따라가며 집계 불러오기, 결과 가공, 반환의 세 단계를 다룹니다.

<a id="create-a-custom-aggregation"></a><a id="loading-an-aggregation"></a>
## 사용자 정의 집계 만들기 (Create a custom aggregation)

함수를 사용하면 온톨로지의 데이터를 바탕으로 사용자 정의 집계를 계산할 수 있고, 그 결과를 Workshop의 차트 위젯에 표시할 수 있습니다. 이 가이드는 온톨로지에서 집계된 데이터를 불러오고, 그 결과를 가공해 미래 결과의 추정치(projection)를 만들고, 수정된 결과를 반환하는 사용자 정의 집계 로직을 작성하는 과정을 안내합니다.

이 페이지는 TypeScript v1을 다룹니다. Python은 [Python 함수로 사용자 정의 집계 만들기](../11_python/04_python-functions-create-custom-aggregation.md)를, TypeScript v2는 OSDK 레퍼런스의 [Aggregations](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#aggregations)를 참고하십시오.

이 섹션을 진행하는 동안 다음 자료가 유용할 수 있습니다.

* [객체 집합(Object Set) 집계](07_api-object-sets.md#computing-aggregations) 레퍼런스
* [집계 타입](../04_types-reference.md#aggregation-types) 레퍼런스
* 이 가이드의 Python 버전인 [Python 함수로 사용자 정의 집계 만들기](../11_python/04_python-functions-create-custom-aggregation.md)
* TypeScript v2 집계 문법을 다루는 TypeScript OSDK 레퍼런스의 [Aggregations](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#aggregations)

**설명**: 집계는 SQL의 `GROUP BY`와 `SUM`, `COUNT` 같은 집계 함수로 여러 행을 묶어 요약 값을 구하는 작업입니다. 보통 Workshop 차트는 온톨로지에서 이런 집계를 직접 계산해 그리지만, "지난달 값을 바탕으로 다음 6개월을 추정"처럼 표준 집계만으로 표현할 수 없는 계산이 필요할 때는 함수가 집계 결과를 받아 가공한 뒤 차트에 넘겨줍니다.

<a id="loading-an-aggregation"></a><a id="manipulating-aggregation-results"></a>
## 집계 불러오기 (Loading an aggregation)

TypeScript v1은 `Objects.search()`에 `.groupBy()`, `.segmentBy()`, 그리고 지표(metric) 메서드를 체인으로 이어 집계를 만듭니다. TypeScript v1 집계 지표는 검색 가능(searchable)으로 표시된 속성(property)만 받습니다. 문자열 속성에는 두 가지 버킷 전략이 있으며, 각각 최대 버킷 수의 한도가 있고 그 한도를 넘으면 근사값이 됩니다. `.topValues()`는 상위 1,000개 값으로 버킷을 나누고 빠르게 응답하며, `.exactValues()`는 최대 10,000개의 버킷을 고려하고 그만큼 느립니다.

TypeScript v2의 집계 문법은 TypeScript OSDK 레퍼런스의 [Aggregations](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/#aggregations)를 참고하십시오. 마이그레이션 가이드에는 TypeScript v1의 모든 [버킷 메서드](../10_typescript-v2/03_typescript-v2-migration.md#group-by-strategy-mapping)와 [집계 지표](../10_typescript-v2/03_typescript-v2-migration.md#aggregation-metric-mapping)에 대응하는 TypeScript v2의 대응 항목이 정리되어 있고, [TypeScript v2에 대응 항목이 없는 기능](../10_typescript-v2/03_typescript-v2-migration.md#capabilities-with-no-typescript-v2-equivalent)도 나열되어 있습니다.

이 예제에서는 지출(expense)로 이루어진 온톨로지가 있고, 각 `expense` 객체에 부서 이름, 지출 `date`(날짜), 지출 `amount`(금액) 속성이 있다고 가정합니다. 앞으로 6개월 동안 부서별 월간 지출을 추정하고 싶다면, 먼저 월간 지출에 대한 집계 데이터를 불러오는 것부터 시작할 수 있습니다.

```typescript tab="TypeScript v1"
const result = await Objects.search()
    .expenses()
    .groupBy(expense => expense.departmentName.topValues())
    .segmentBy(expense => expense.date.byMonth())
    .sum(expense => expense.amount);
```

**설명**: 이 체인은 SQL로 쓰면 대략 `SELECT departmentName, month(date), SUM(amount) FROM expenses GROUP BY departmentName, month(date)`에 해당합니다. `.groupBy()`가 첫 번째 차원(부서), `.segmentBy()`가 두 번째 차원(월)이고 `.sum()`이 각 칸의 값을 계산합니다. 차이점은 결과가 평평한 행 목록이 아니라 "부서별 버킷 안에 월별 버킷이 들어 있는" 중첩 구조로 돌아온다는 점입니다. 예를 들어 Sales 부서의 버킷 안에 1월: 5000, 2월: 6200, 3월: 5800 같은 월별 버킷이 들어 있는 형태입니다.

> **중간 요약**: TypeScript v1에서는 `Objects.search()`에 `.groupBy()`, `.segmentBy()`, 지표 메서드를 이어 집계를 만들며, 지표는 검색 가능한 속성만 받습니다. 문자열 버킷은 빠른 `.topValues()`(1,000개)와 느리지만 넓은 `.exactValues()`(10,000개) 중에서 고릅니다.

<a id="manipulating-aggregation-results"></a><a id="returning-the-aggregation"></a>
## 집계 결과 가공하기 (Manipulating aggregation results)

`.groupBy()` 다음에 `.segmentBy()`를 호출하면 `ThreeDimensionalAggregation`이 만들어지므로, `result.buckets`는 이미 부서마다 버킷 하나씩으로 중첩되어 있습니다. 각 안쪽 버킷의 키는 해당 월의 양 끝점을 모두 담은 `IRange<Timestamp>`이며, `min`은 포함(inclusive), `max`는 제외(exclusive)입니다. 각 `Timestamp` 값은 `.plusMonths()` 같은 메서드로 달력 연산을 지원합니다.

다음으로 각 부서의 향후 6개월 지출을 외삽(extrapolate)할 수 있습니다. 이 예제에서는 마지막 달의 값을 다음 6개월의 추정치로 그대로 쓰는 단순한 방법을 사용합니다.

```typescript tab="TypeScript v1"
const modifiedBuckets = result.buckets.map(bucket => {
    // 가장 최근 달에 해당하는 버킷을 찾음
    const lastBucket = bucket.value[bucket.value.length - 1];

    let nextSixMonths: IBaseBucket<IRange<Timestamp>, Double>[] = [];
    let currentMonth = lastBucket.key.max!;
    // 여섯 번 반복
    for (let i = 0; i < 6; i++) {
        // 이 범위의 끝(다음 달)을 구함
        const nextMonth = currentMonth.plusMonths(1);
        // 다음 달을 날짜 범위로, 가장 최근 달의 값을 값으로 하는
        // 새 버킷을 추가
        nextSixMonths.push({
            key: {
                min: currentMonth,
                max: nextMonth,
            },
            value: lastBucket.value,
        });
        currentMonth = nextMonth;
    }

    // 수정된 결과를 반환
    return { key: bucket.key, value: nextSixMonths };
});
```

**설명**: 바깥 `map`은 부서 버킷을 하나씩 처리합니다. `bucket.value`는 그 부서의 월별 버킷 배열이고, 마지막 원소가 가장 최근 달입니다. 그 달의 범위 끝(`max`, 예: 3월 버킷이면 4월 1일 0시)을 시작점으로 잡고, 반복문에서 한 달씩 `plusMonths(1)`로 늘려 가며 [4월 1일, 5월 1일), [5월 1일, 6월 1일) 같은 범위 6개를 만듭니다. 각 새 버킷의 값은 모두 최근 달의 지출(`lastBucket.value`)입니다. `max!`의 `!`는 TypeScript에게 "이 값은 undefined가 아니다"라고 알려 주는 non-null 단언 연산자입니다. 결과적으로 부서 키는 그대로 두고 월별 버킷만 미래 6개월로 바뀐 새 배열이 만들어집니다.

TypeScript v2에서는 `.aggregate()`가 중첩된 버킷 대신 평평한 행 배열을 반환하므로, 3차원 집계를 반환해야 하는 함수는 중첩 구조를 직접 다시 만들어야 합니다. 마이그레이션 가이드의 [Grouping](../10_typescript-v2/03_typescript-v2-migration.md#grouping)을 검토하십시오.

> **중간 요약**: `groupBy`와 `segmentBy`를 함께 쓴 결과는 부서별 버킷 안에 월별 버킷이 있는 `ThreeDimensionalAggregation`이고, 월 버킷의 키는 `min` 포함, `max` 제외인 시간 범위입니다. 예제는 각 부서의 마지막 달 값을 이후 6개월 버킷에 복사해 추정치를 만듭니다.

<a id="returning-the-aggregation"></a>
## 집계 반환하기 (Returning the aggregation)

향후 6개월에 대한 추정치를 만들었으니 이제 추정 값을 반환할 수 있습니다.

```typescript tab="TypeScript v1"
return { buckets: modifiedBuckets };
```

TypeScript v1은 버킷들을 `buckets` 키 아래의 객체로 감싸고, 중첩된 단계는 `value` 키로 둡니다. 반환 타입은 TypeScript v1, TypeScript v2, Python 모두에서 `ThreeDimensionalAggregation`으로 같으며, 각 버전은 함수 안에서 이 값을 서로 다르게 만듭니다. 그래서 이 함수를 사용하는 Workshop 차트는 마이그레이션 후에도 계속 동작합니다. 각 버전이 기대하는 형태는 [집계 타입](../04_types-reference.md#aggregation-types)을, Python의 `NestedBucket`과 `SingleBucket` 클래스는 [Python 함수로 사용자 정의 집계 만들기](../11_python/04_python-functions-create-custom-aggregation.md)를 참고하십시오.

이 함수의 전체 예제 코드는 다음과 같습니다.

(원문에는 위의 세 조각을 `@Function()` 데코레이터가 붙은 `public async estimatedDepartmentExpenses(): Promise<ThreeDimensionalAggregation<string, IRange<Timestamp>, Double>>` 메서드 하나로 합친 전체 예제 코드가 있습니다. 본문은 집계 불러오기, 버킷 가공, `return { buckets: modifiedBuckets }`를 차례로 이어 붙인 것과 같습니다.)

**설명**: 반환 타입 `ThreeDimensionalAggregation<string, IRange<Timestamp>, Double>`의 세 타입 인자는 차례로 첫 번째 차원 키(부서 이름, `string`), 두 번째 차원 키(월 범위, `IRange<Timestamp>`), 값(지출 합계, `Double`)을 뜻합니다. 반환되는 데이터는 `{ buckets: [ { key: "Sales", value: [ { key: {min, max}, value: 5800 }, ... ] }, ... ] }` 형태입니다. Workshop 차트는 이 구조를 받아 부서별 시리즈, 월별 x축으로 그릴 수 있습니다.

결과 집계는 Workshop 차트에서 향후 6개월의 월간 지출 추정치를 보여 주는 데 사용할 수 있습니다.

> **중간 요약**: 가공한 버킷을 `{ buckets: ... }`로 감싸 반환하며, 반환 타입 `ThreeDimensionalAggregation`은 언어 버전과 관계없이 같아서 Workshop 차트가 마이그레이션 후에도 그대로 동작합니다.

## 정리

- 함수로 온톨로지 데이터를 집계하고 가공해 Workshop 차트에 표시할 사용자 정의 집계를 만들 수 있습니다.
- TypeScript v1은 `Objects.search()`에 `.groupBy()`, `.segmentBy()`, 지표 메서드를 이어 집계하며, 검색 가능한 속성만 지표에 쓸 수 있습니다.
- `groupBy`와 `segmentBy`를 함께 쓰면 중첩 버킷 구조의 `ThreeDimensionalAggregation`이 나오고, 이를 `map`과 날짜 연산으로 가공합니다.
- 결과는 `{ buckets: ... }` 형태로 반환하며, TypeScript v2는 평평한 행을 직접 중첩 구조로 다시 만들어야 합니다.
