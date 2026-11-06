# 집계 시 고려 사항 (Aggregation considerations)

- 원문: https://www.palantir.com/docs/foundry/object-backend/aggregation-considerations/
- 사이드바 위치: Ontology architecture > Overview and getting started > Aggregation considerations

이 페이지는 객체 데이터를 그룹별로 세거나 합칠 때(집계) 결과가 완전히 정확하지 않을 수 있는 이유와, Foundry의 각 애플리케이션에서 그런 부정확한 집계가 어떻게 나타나는지를 설명합니다. Object Explorer, Workshop, Quiver, OSDK, Functions가 각각 정확도와 속도 중 무엇을 우선하는지 알면, 화면에 보이는 상위 N개 결과를 그대로 믿어도 되는지 판단할 수 있습니다.

Foundry에서는 다루는 데이터의 복잡도와 양에 따라, 카디널리티(cardinality)가 높은 집계의 특성 때문에 애플리케이션이 완전히 정확하지 않은 결과를 표시할 수 있습니다(이를 "부정확한 집계(inexact aggregations)"라고도 합니다).

**설명**: 카디널리티는 여기서 그룹으로 묶을 열이 가진 서로 다른 값의 개수입니다. 예를 들어 `gender` 열은 값이 몇 개뿐이라 카디널리티가 낮고, `zip_code`나 `customer_id` 열은 서로 다른 값이 수만, 수백만 개라 카디널리티가 높습니다. SQL로 `SELECT zip_code, COUNT(*) FROM t GROUP BY zip_code ORDER BY 2 DESC LIMIT 100`을 정확하게 계산하려면 모든 그룹의 개수를 다 세야 합니다. 데이터가 여러 서버(샤드)에 나뉘어 있으면 보통 각 서버가 자기 상위 그룹만 보내고 그것을 합치는 근사 방식을 쓰는데, 이때 어떤 서버에서도 상위권이 아니었지만 합치면 상위권인 그룹이 빠질 수 있습니다. 이것이 부정확한 집계가 생기는 일반적인 원리입니다.

`object-set-service` API에는 집계 정확도와 관련된 다음 필드가 있으며, 사용할 수 있는 곳에서는 이를 이용해 정확도를 높일 수 있습니다.

* API 호출자는 요청에 `AggregationExecutionMode`를 추가하고 값을 `PREFER_ACCURACY`로 설정할 수 있습니다. 이렇게 설정하면 API 응답은 느려지지만 더 정확한 결과를 제공합니다. 다만 완전한 정확성이 보장되지는 않습니다.
* 집계 응답에는 결과가 정확한지를 나타내는 `AggregateResultAccuracy` 필드가 들어 있습니다.

Foundry의 각 제품은 집계가 부정확할 수 있음을 나타내는 방식이 조금씩 다릅니다. 다음 섹션에서 Foundry에서 부정확한 집계가 어떻게 나타날 수 있는지에 대한 예시와, 정확도를 얻기 위해 사용자가 고려해야 할 사항을 확인하십시오.

추가 안내가 필요하면 Palantir Support에 문의하십시오.

> **중간 요약**: 카디널리티가 높은 집계는 근사 결과가 나올 수 있습니다. OSS API에서는 `AggregationExecutionMode`를 `PREFER_ACCURACY`로 지정해 정확도를 높이고, 응답의 `AggregateResultAccuracy`로 정확 여부를 확인할 수 있습니다.

<a id="object-explorer-and-workshop"></a>
## Object Explorer와 Workshop (Object Explorer and Workshop)

다음 두 히스토그램 스크린샷을 살펴보십시오. 둘 다 객체 2천만 개가 있는 데이터셋의 데이터를 보여 줍니다. 첫 번째 스크린샷은 데이터셋을 Object Explorer로 불러온 것이고, 두 번째는 Workshop 안의 Workshop Filter List 위젯입니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-backend/inexact-histogram1.png" alt="Object Explorer 히스토그램." width="500">

<img src="https://www.palantir.com/docs/resources/foundry/object-backend/inexact-histogram2.png" alt="Workshop Filter List 위젯 히스토그램." width="500">

이 히스토그램들은 두 번의 집계 요청으로 만들어졌습니다. 첫 번째 요청은 개수 기준 상위 100개 버킷을 가져오려고 하며, 근사 응답을 받습니다. 두 번째 요청은 같은 100개 버킷의 개수를 다시 가져오되, 개수가 정확하도록 이 100개 버킷만 남기는 필터를 추가로 적용합니다.

표시된 개수 자체는 정확하지만, 첫 번째 집계 응답이 정확하지 않았기 때문에 표시된 버킷이 실제로 개수 기준 상위 100개 버킷은 아니라는 점에서 두 번째 히스토그램은 여전히 부정확합니다.

Object Explorer와 Workshop이 OSS로 보내는 요청은 `AggregationExecutionMode`를 지정하지 않으며, 이 경우 OSS는 기본값인 `PREFER_SPEED`를 사용합니다.

**설명**: 버킷(bucket)은 그룹 바이(group by)로 묶인 그룹 하나입니다. 두 단계 요청을 SQL로 풀어 보면, 1단계는 근사 방식으로 상위 100개 값 목록을 얻고, 2단계는 `WHERE bucket IN (1단계의 100개 값) GROUP BY bucket`으로 그 100개만 정확히 다시 세는 것입니다. 그래서 막대 높이(개수)는 정확하지만, 1단계에서 놓친 값이 있으면 실제로는 상위 100위 안에 드는 버킷이 화면에 아예 나타나지 않을 수 있습니다.

<a id="quiver-pivot-table-and-workshop-pivot-table"></a>
## Quiver 피벗 테이블과 Workshop 피벗 테이블 (Quiver pivot table and Workshop pivot table)

Quiver와 Workshop 피벗 테이블에서 열을 개수 기준 내림차순으로 정렬하면, 상위 버킷이 올바른 순서로 표시되지 않습니다. 이 경우 부정확한 집계는 다음 오류 메시지 중 하나로 나타날 수 있습니다.

* "Too many values for `column`, not all are displayed"(`column`의 값이 너무 많아 모두 표시되지 않습니다)
* "Showing approximate results due to computational limitations"(계산상의 제약으로 근사 결과를 표시합니다)
* "Only loading first 1,000 values per property. Filter your data for more accurate results."(속성당 처음 1,000개 값만 불러옵니다. 더 정확한 결과를 원하면 데이터를 필터링하십시오.)

아래 예시에서 `Example Bucket` 열은 원하는 대로 내림차순으로 정렬되어 있지 않습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-backend/inexact-workshop-pivot.png" alt="Workshop 피벗 테이블." width="250">

<img src="https://www.palantir.com/docs/resources/foundry/object-backend/inexact-quiver-pivot.png" alt="오류 메시지가 있는 Quiver 피벗 테이블." width="600">

<img src="https://www.palantir.com/docs/resources/foundry/object-backend/inexact-quiver-pivot-2.png" alt="오류 메시지가 있는 Quiver 피벗 테이블 2." width="400">

Quiver와 Workshop은 피벗 테이블을 뒷받침하는 집계 요청에 정렬 순서를 지정하지 않기 때문에, 이것들은 개수 기준 실제 상위 버킷이 아닙니다. 정렬은 반환된 버킷들을 가지고 프런트엔드에서 수행됩니다.

**설명**: 백엔드가 정렬 없이 일부 버킷만 돌려주고, 브라우저(프런트엔드)가 받은 버킷만 가지고 정렬하는 구조입니다. 예를 들어 실제 개수가 A=900, B=800, C=700인데 백엔드가 B와 C만 돌려주었다면 화면에는 B, C 순서로 보이고 가장 큰 A는 나타나지 않습니다.

> **중간 요약**: Object Explorer와 Workshop은 속도 우선(`PREFER_SPEED`)으로 요청하므로 표시된 개수는 정확해도 상위 N개 버킷 자체가 실제와 다를 수 있습니다. Quiver와 Workshop 피벗 테이블은 정렬을 프런트엔드에서 하므로 개수 기준 정렬 결과가 실제 상위 순서가 아닐 수 있으며, 경고 메시지로 이를 알립니다.

<a id="ontology-sdk-osdk"></a><a id="osdk"></a>
## Ontology SDK (OSDK)

OSDK는 `PREFER_ACCURACY`로 설정되어 있고 집계 복잡도가 제한되어 있으므로, 모든 쿼리 응답은 `ACCURATE`(정확)입니다.

![OSDK 애플리케이션 문서.](https://www.palantir.com/docs/resources/foundry/object-backend/inexact-osdk.png)

<a id="functions"></a>
## 함수 (Functions)

함수(function)는 항상 `PREFER_ACCURACY`를 사용하므로, 각 버킷의 값은 정확합니다. 현재 함수 호출 중에 `groupBy`와 `orderBy`를 동시에 사용할 방법은 없습니다. 다음 코드 조각은 백엔드에서 `groupBy`를 수행하고 메모리에서 정렬하는 현재 방식의 예를 보여 줍니다.

```
    @Function()
    public async aggregateOnMoreBucketsThanAuthorized(): Promise<TwoDimensionalAggregation<string, Double>> {
        // 집계하고 개수를 셉니다
        const aggregation = await Objects.search()._af20mInstancesObv2()
                 .groupBy(o => o.exampleBucket.topValues())
                 .count()

        aggregation.buckets.sort((b1, b2) => b2.value - b1.value);
        return aggregation;
    }
```

**설명**: 이 TypeScript 함수는 입력 없이 호출되며, `_af20mInstancesObv2` 객체 타입 전체를 검색해 `exampleBucket` 속성의 상위 값들(`topValues()`)로 그룹을 나누고 그룹별 개수를 셉니다(`count()`). 여기까지가 백엔드에서 실행되는 집계입니다. 그다음 줄 `aggregation.buckets.sort(...)`는 백엔드가 돌려준 버킷 배열을 함수 실행 메모리 안에서 `value`(개수) 내림차순으로 정렬합니다. 반환값은 문자열 키와 숫자 값을 가진 버킷 목록(`TwoDimensionalAggregation`)입니다. 정렬이 백엔드 집계 이후에 일어나므로, 버킷 값은 정확하지만 어떤 버킷들이 반환되는지는 `topValues()`가 고른 범위에 달려 있습니다.

결과 예시는 다음과 같습니다.

```
{
  "buckets": [
    {
      "key": {
        "string": "10105",
        "type": "string"
      },
      "value": {
        "double": 461,
        "type": "double"
      }
    },
    {
      "key": {
        "string": "10163",
        "type": "string"
      },
      "value": {
        "double": 454,
        "type": "double"
      }
    },
    ...
```

(원문 결과 예시에는 같은 형식의 버킷이 하나 더 나열되어 있습니다.)

> **중간 요약**: OSDK와 함수는 항상 정확도 우선(`PREFER_ACCURACY`)이라 버킷 값이 정확합니다. 다만 함수에서는 `groupBy`와 `orderBy`를 함께 쓸 수 없어, 집계 결과를 메모리에서 직접 정렬해야 합니다.

## 정리

- 카디널리티가 높은 데이터를 집계하면 속도를 위해 근사 결과가 나올 수 있으며, 특히 "상위 N개 버킷"이 실제와 다를 수 있습니다.
- OSS API의 `AggregationExecutionMode`(`PREFER_SPEED` 또는 `PREFER_ACCURACY`)로 속도와 정확도 중 무엇을 우선할지 정하고, `AggregateResultAccuracy`로 결과의 정확 여부를 확인합니다.
- Object Explorer와 Workshop은 기본 속도 우선, Quiver와 Workshop 피벗 테이블은 프런트엔드 정렬이라 순서가 부정확할 수 있습니다.
- OSDK와 함수는 정확도 우선이며, 함수에서는 집계 후 메모리에서 정렬합니다.
