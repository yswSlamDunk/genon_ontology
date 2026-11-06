# 사용자 정의 집계 만들기 (Create a custom aggregation)

- 원문: https://www.palantir.com/docs/foundry/functions/python-functions-create-custom-aggregation/
- 사이드바 위치: Define Ontologies > Functions > Python > Create a custom aggregation

이 페이지는 Python 함수(function)로 온톨로지 데이터를 집계하고, 그 결과를 가공해 새로운 집계 결과를 만들어 반환하는 방법을 예제로 보여 줍니다. 이렇게 반환한 집계는 Workshop의 차트 위젯에서 바로 그릴 수 있습니다. 예제는 부서별, 월별 지출을 집계한 뒤 다음 6개월의 지출을 단순 추정하는 함수입니다.

함수를 사용하면 온톨로지의 데이터를 바탕으로 사용자 정의 집계를 계산할 수 있고, 그 결과를 Workshop의 차트 위젯에 표시할 수 있습니다. 이 가이드는 온톨로지에서 집계된 데이터를 불러오고, 그 결과를 가공해 미래 결과의 추정치(projection)를 만든 뒤, 수정된 결과를 반환하는 사용자 정의 집계 로직을 작성하는 과정을 안내합니다.

이 절을 진행하면서 다음 참고 자료가 유용할 수 있습니다.

* [Python 집계 타입](../04_types-reference.md#aggregation-types) 참조

**주의**: `TwoDimensionalAggregation`과 `ThreeDimensionalAggregation`의 `.from_osdk()`는 Python OSDK v2를 사용할 때만 지원됩니다.

**설명**: 집계(aggregation)는 SQL의 `GROUP BY`와 `SUM`, `COUNT` 같은 집계 함수로 여러 행을 묶어 요약 값을 만드는 작업입니다. `TwoDimensionalAggregation`은 "키 하나에 값 하나"(예: 부서별 지출 합계) 형태의 결과이고, `ThreeDimensionalAggregation`은 "키 두 개의 조합에 값 하나"(예: 부서별, 월별 지출 합계) 형태의 결과입니다. 차트로 보면 2차원 집계는 막대 하나가 키 하나인 막대 차트, 3차원 집계는 부서마다 선이 하나씩 있는 월별 선 차트로 그릴 수 있는 형태입니다.

<a id="loading-an-aggregation"></a>
## 집계 불러오기 (Loading an aggregation)

이 예제에서는 지출(expense)로 이루어진 온톨로지가 있고, 각 `expense` 객체가 부서 이름, 지출 날짜(`date`), 지출 금액(`amount`) 속성(property)을 가진다고 가정합니다. 다음 6개월 동안 부서별 월 지출을 추정하려면, 먼저 월 지출에 대한 집계 데이터를 불러오는 것부터 시작합니다.

```python
client = FoundryClient()
result: AggregateObjectsResponse = (
    client.ontology.objects.Expense
    .group_by(Expense.object_type.department_name.exact())
    .group_by(Expense.object_type.date.exact())
    .sum(Expense.object_type.amount)
    .compute()
)
```

**설명**: 이 코드는 SQL로 `SELECT department_name, date, SUM(amount) FROM expense GROUP BY department_name, date`에 해당합니다. `group_by`를 두 번 호출해 부서와 날짜 두 기준으로 묶고, `.sum(...)`으로 금액을 더한 뒤, `.compute()`로 실제 계산을 실행합니다. `.exact()`는 값을 구간으로 나누지 않고 정확히 같은 값끼리 묶으라는 뜻입니다. 예제는 `date`가 이미 월 단위 값(예: 매월 1일)이라고 가정하고 있습니다.

<a id="manipulating-aggregation-results"></a>
## 집계 결과 가공하기 (Manipulating aggregation results)

다음으로 각 부서의 다음 6개월 지출을 외삽(extrapolate)합니다. 이 예제에서는 마지막 달의 값을 다음 6개월의 추정치로 그대로 사용하는 단순한 방식을 씁니다.

```python
current_buckets = ThreeDimensionalAggregation.from_osdk(result, "departmentName", "date")
modified_buckets: list[NestedBucket[str, Range[Date], Double]] = []
date_format = "%Y-%m-%d"
for bucket in current_buckets.buckets:
    # 가장 최근 달에 해당하는 버킷을 찾습니다
    last_bucket: SingleBucket[Date, Double] = bucket.buckets[-1]

    next_six_months: list[SingleBucket[Range[Date], Double]] = []
    # `date` 필드는 YYYY-MM-DD 형식의 문자열로 변환되어 있습니다.
    # 문자열에서 `Date` 타입으로 변환합니다. 각 달의 SingleBucket 객체를
    # 만들 때는 다시 문자열로 변환합니다
    current_month: Date = datetime.strptime(last_bucket.key, date_format).date()

    # 여섯 번 반복합니다
    for _ in range(6):
        # 현재 달에서 다음 달을 계산합니다
        next_month = current_month + relativedelta(months=1)
        # 다음 달을 날짜 범위로, 가장 최근 달의 금액을 값으로 하는
        # 새 버킷을 추가합니다
        next_six_months.append(SingleBucket(Range(min=current_month, max=next_month), last_bucket.value))
        current_month = next_month

    # 수정된 결과를 NestedBucket으로 추가합니다
    modified_buckets.append(NestedBucket(bucket.key, next_six_months))
```

**설명**: 버킷(bucket)은 집계 결과에서 "키 하나와 그 값"을 담은 한 칸입니다. `from_osdk`로 변환한 결과는 부서마다 `NestedBucket` 하나가 있고, 그 안에 월별 `SingleBucket`이 시간순으로 들어 있는 2단 구조입니다. 예를 들어 입력이 다음과 같다고 합시다.

| 부서 | 월 | 지출 합계 |
|---|---|---|
| Sales | 2024-01-01 | 100 |
| Sales | 2024-02-01 | 120 |
| HR | 2024-02-01 | 50 |

반복문은 부서마다 마지막 버킷(`bucket.buckets[-1]`, Sales는 2024-02-01의 120)을 꺼내고, 그 날짜부터 한 달씩 6번 늘려 가며 `[2024-02-01, 2024-03-01)` 같은 날짜 범위(`Range`)를 키로, 120을 값으로 하는 버킷 6개를 만듭니다. HR도 같은 방식으로 50짜리 버킷 6개가 만들어집니다. 원래 집계는 키가 날짜 하나였지만 새 결과는 키가 날짜 범위라는 점이 다릅니다.

<a id="returning-the-aggregation"></a>
## 집계 반환하기 (Returning the aggregation)

다음 6개월의 추정치를 만들었으므로, 이 추정값을 `ThreeDimensionalAggregation`으로 반환할 수 있습니다.

```python
return ThreeDimensionalAggregation(modified_buckets)
```

이 함수의 전체 예제 코드는 다음과 같습니다.

(원문에는 위의 세 조각을 하나로 합친 `estimated_department_expenses()` 함수의 전체 코드가 있습니다. 반환 타입은 `ThreeDimensionalAggregation[str, Range[Date], Double]`이고, `@function` 데코레이터와 함께 `dateutil.relativedelta`, `datetime`, `functions.api`의 `Date`, `Double`, `NestedBucket`, `SingleBucket`, `Range`, `ThreeDimensionalAggregation`, `function`, 그리고 `ontology_sdk`의 `FoundryClient`, `Expense`를 임포트합니다.)

**설명**: 함수 시그니처의 반환 타입 `ThreeDimensionalAggregation[str, Range[Date], Double]`은 각각 "첫 번째 키는 문자열(부서 이름), 두 번째 키는 날짜 범위(월), 값은 실수(지출 금액)"라는 뜻입니다. Workshop은 이 타입 정보를 보고 결과를 차트의 축과 계열로 배치합니다.

결과 집계는 Workshop 차트에서 다음 6개월의 월 지출 추정치를 보여 주는 데 사용할 수 있습니다.

## 정리

- Python 함수로 온톨로지 데이터를 집계하고 가공한 뒤 집계 타입으로 반환하면 Workshop 차트에 표시할 수 있습니다.
- 집계는 `group_by`, `sum`, `compute` 체인으로 불러오며, SQL의 `GROUP BY`와 `SUM`에 해당합니다.
- `ThreeDimensionalAggregation.from_osdk()`(Python OSDK v2 전용)로 결과를 `NestedBucket`과 `SingleBucket` 구조로 바꿔 가공합니다.
- 예제는 부서별 마지막 달의 지출을 다음 6개월 날짜 범위에 복사해 추정치를 만들고, 이를 `ThreeDimensionalAggregation`으로 반환합니다.
