# 인라인 지표 (Inline metrics)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-inline-metrics/
- 사이드바 위치: Applications > Dynamic Scheduling > Inline metrics

이 페이지는 Scheduling Gantt Chart 위에 시간 구간별 숫자나 텍스트(예: 하루당 작업 수, 정비사별 가동률)를 바로 표시하는 인라인 지표(inline metrics)를 설명합니다. 지표 값은 함수(function)가 계산해서 "시간 구간과 값"의 목록으로 돌려주며, 차트 상단(헤더)이나 각 행 옆에 표시됩니다. 함수가 따라야 할 반환 형식, 예제 함수, 위젯 구성 방법을 다룹니다.

인라인 지표는 애플리케이션 빌더가 핵심 데이터를 차트 안에 바로 표시할 수 있는 간편한 방법을 제공합니다.

* 헤더 지표(Header metrics)는 위젯의 타임라인(x축)에 맞춰 정렬되며, 전체 일정에 대한 상위 수준 집계를 제공합니다.
* 행 지표(Row metrics)는 각 행에 맞춰 정렬되며, 개별 Resource 객체의 일정과 배정에 대한 정보를 제공합니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/inline-metrics-example.png" alt="헤더 지표와 행 지표가 구성된 Scheduling Gantt 차트." width="800" >

이 페이지의 코드 예제는 [TypeScript v1](../../02_define-ontologies/04_functions/12_typescript-v1/01_typescript-v1-getting-started.md) 함수와 [TypeScript v2](../../02_define-ontologies/04_functions/10_typescript-v2/01_typescript-v2-getting-started.md) 함수 두 가지로 제공됩니다. 사용 중인 함수 버전에 맞는 탭을 선택하세요. TypeScript v1은 각 함수를 내보낸(export) 클래스의 메서드로 정의하고 `@foundry/functions-api`의 `@Function()` 데코레이터를 붙이며, `Objects.search()`로 온톨로지를 조회합니다. TypeScript v2는 `export default`로 함수를 정의하고 `@osdk/functions`에서 타입을 가져오며, [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/) 클라이언트나 파라미터로 전달된 `ObjectSet`으로 온톨로지를 조회합니다. 전체 비교는 [TypeScript v1과 TypeScript v2 비교](../../02_define-ontologies/04_functions/02_language-feature-support.md#typescript-v1-vs-typescript-v2)를 참고하세요.

**설명**: 이 번역에서는 각 섹션에서 TypeScript v2 예제를 대표로 남기고, v1 예제는 차이점만 글로 적었습니다.

> **중간 요약**: 인라인 지표에는 x축 위에 전체 집계를 보여 주는 헤더 지표와 각 행 옆에 자원별 정보를 보여 주는 행 지표가 있으며, 예제는 TypeScript v1과 v2로 제공됩니다.

<a id="functions-signature"></a>
## 함수 시그니처 (Functions signature)

인라인 지표에는 다음 형태와 일치하는 [사용자 지정 타입](../../02_define-ontologies/04_functions/04_types-reference.md)의 목록을 반환하는 함수가 필요합니다.

```typescript tab="TypeScript v2"
import { Double, Range, TimestampISOString } from "@osdk/functions";

interface InlineMetricsBucket {
    range: Range<TimestampISOString>;
    value: Double;
}
```

(원문에는 같은 구조를 `IRange<Timestamp>`와 `Double`로 정의한 TypeScript v1 버전도 있습니다.)

**설명**: 지표 함수의 반환값은 "버킷(bucket)"의 배열입니다. 버킷 하나는 시간 구간 `range`와 그 구간에 표시할 값 `value`로 이루어집니다. 예를 들어 "11월 1일부터 11월 2일까지, 값 4"인 버킷과 "11월 2일부터 11월 3일까지, 값 7"인 버킷을 반환하면 차트의 해당 날짜 칸 위에 4와 7이 표시됩니다.

인라인 지표는 다른 반환 타입도 지원합니다.

```typescript tab="TypeScript v2"
import { DateISOString, Integer, Range, TimestampISOString } from "@osdk/functions";

// 참고: 인터페이스 이름은 중요하지 않고, 키 이름만 중요합니다
interface InlineMetricsBucketInteger {
    range: Range<TimestampISOString>;
    value: Integer;
}

interface InlineMetricsBucketString {
    range: Range<DateISOString>;
    value: string;
}
```

(원문에는 `IRange<Timestamp>`, `IRange<LocalDate>`를 쓰는 TypeScript v1 버전도 있습니다.)

**설명**: 위젯은 인터페이스 이름이 아니라 객체의 키 이름(`range`, `value`)으로 반환값을 해석합니다. 그래서 인터페이스 이름은 아무렇게나 지어도 되지만 키 이름은 정확히 맞춰야 합니다.

`range` 키는 `Timestamp`, `LocalDate`, 또는 `Integer`(숫자 값은 에포크 밀리초를 나타냄)에 대한 범위 타입을 지원합니다. TypeScript v1은 `@foundry/functions-api`의 `IRange` 타입을 사용하고, TypeScript v2는 그에 대응하는 `@osdk/functions`의 `Range` 타입을 내부 타입 `TimestampISOString`, `DateISOString`, 또는 `Integer`와 함께 사용합니다. 두 타입은 양 끝점의 이름이 다릅니다. `IRange<T>`는 `min`과 `max`를 가지고, `Range<T>`는 `startValue`와 `endValue`를 가집니다.

`value` 키는 `string`, `Integer`, 또는 `Double` 값을 지원합니다.

**설명**: 에포크 밀리초(epoch milliseconds)는 1970년 1월 1일 0시(UTC)부터 지난 시간을 밀리초로 센 정수입니다. ISO 문자열(`TimestampISOString`)은 `"2026-11-03T09:00:00Z"`처럼 시각을 문자열로 표현한 형식입니다.

> **중간 요약**: 지표 함수는 `range`(Timestamp, LocalDate, Integer 범위)와 `value`(string, Integer, Double)를 키로 가진 버킷 배열을 반환해야 합니다. 범위 끝점 이름은 v1이 `min`/`max`, v2가 `startValue`/`endValue`입니다.

<a id="sample-header-metric-function"></a>
## 헤더 지표 함수 예제 (Sample header metric function)

```typescript tab="TypeScript v2"
import { Client } from "@osdk/client";
import { Double, Range, TimestampISOString } from "@osdk/functions";
import { SchedulingMaintenanceTask } from "@ontology/sdk";

interface InlineMetricBucketDouble {
    range: Range<TimestampISOString>;
    value: Double;
}

// 주어진 범위 안의 작업 수를 일(day) 단위 step으로 나눈 버킷별로 셉니다
export default async function getInlineMetricsWithObjectCounts(
    client: Client,
    startTime: TimestampISOString,
    endTime: TimestampISOString,
    step: Double
): Promise<Array<InlineMetricBucketDouble>> {
    const tasks = await Array.fromAsync(
        client(SchedulingMaintenanceTask)
            .where({ startTime: { $gte: startTime, $lte: endTime } })
            .asyncIter()
    );
    const buckets: InlineMetricBucketDouble[] = [];

    let current = new Date(startTime);
    const end = new Date(endTime);
    while (current < end) {
        const currentEnd = new Date(current);
        currentEnd.setUTCDate(currentEnd.getUTCDate() + step);
        const tasksInRange = tasks.filter(t =>
            t.startTime != null &&
            new Date(t.startTime) >= current &&
            new Date(t.startTime) <= currentEnd
        );
        buckets.push({
            range: {
                startValue: current.toISOString(),
                endValue: currentEnd.toISOString(),
            },
            value: tasksInRange.length,
        });
        current = currentEnd;
    }
    return buckets;
}
```

(원문에는 `Objects.search().schedulingMaintenanceTask()`로 조회하고 `min`/`max`로 범위를 만드는 TypeScript v1 버전도 있습니다.)

**설명**: 입력은 차트에 보이는 시간 범위(`startTime`, `endTime`)와 버킷 크기(`step`, 일 단위)입니다. 먼저 시작 시각이 이 범위 안에 있는 정비 작업(`SchedulingMaintenanceTask`)을 모두 가져옵니다. 그다음 `current`를 `step`일씩 앞으로 옮기면서, 각 구간에 시작 시각이 들어가는 작업 수를 세어 버킷으로 추가합니다. 예를 들어 `step`이 1이고 범위가 3일이면 버킷 3개(각 날짜의 작업 수)가 반환됩니다.

헤더 지표는 x축 옆에 헤더로 표시되므로, 이 함수들이 반드시 특정 객체를 입력으로 받을 필요는 없습니다.

> **중간 요약**: 헤더 지표 함수는 시간 범위와 버킷 크기를 받아 구간별 집계(예: 구간별 작업 수)를 반환하며, 특정 객체를 입력으로 받지 않아도 됩니다.

<a id="sample-row-metric-function"></a>
## 행 지표 함수 예제 (Sample row metric function)

```typescript tab="TypeScript v2"
import { ObjectSet } from "@osdk/client";
import { Double, Range, TimestampISOString } from "@osdk/functions";
import { SchedulingTechnician } from "@ontology/sdk";

interface InlineMetricBucketString {
    range: Range<TimestampISOString>;
    value: string;
}

// 행의 이름과 해당 구간이 속한 버킷 번호를 함께 반환합니다
export default async function getInlineMetricsStringWithObject(
    techs: ObjectSet<SchedulingTechnician>,
    startTime: TimestampISOString,
    endTime: TimestampISOString,
    step: Double
): Promise<Array<InlineMetricBucketString>> {
    const firstPage = await techs.fetchPage({ $pageSize: 1 });
    const techName = firstPage.data[0].fullName;
    const buckets: Array<InlineMetricBucketString> = [];

    let current = new Date(startTime);
    const end = new Date(endTime);
    let count = 0;
    while (current < end) {
        const currentEnd = new Date(current);
        currentEnd.setUTCDate(currentEnd.getUTCDate() + step);
        buckets.push({
            range: {
                startValue: current.toISOString(),
                endValue: currentEnd.toISOString(),
            },
            value: `${techName}-${count}`,
        });
        current = currentEnd;
        count++;
    }
    return buckets;
}
```

(원문에는 `ObjectSet<SchedulingTechnician_1>`을 받고 `techs.all()[0].fullName`으로 이름을 읽는 TypeScript v1 버전도 있습니다.)

**설명**: 헤더 지표 함수와 달리 첫 번째 파라미터로 기술자(`SchedulingTechnician`) 객체 집합(object set)을 받습니다. 위젯이 이 자리에 해당 행의 객체를 넣어 줍니다. 함수는 그 객체의 `fullName`을 읽고, 구간마다 `"이름-번호"` 형식의 문자열 값을 만듭니다. 예를 들어 행이 "Kim"이면 `Kim-0`, `Kim-1`, `Kim-2`가 각 구간에 표시됩니다. 실제 활용에서는 이 자리에 해당 기술자의 구간별 배정 시간 합계 같은 값을 계산해 넣게 됩니다.

행 지표는 해당 행의 객체를 런타임 입력으로 받습니다. 구성에서 함수를 지정할 때 객체 파라미터를 런타임 입력(runtime input)으로 지정하면, 위젯이 해당 행을 자동으로 함수에 전달합니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/inline-metrics-runtime-input.png" alt="지표 구성의 런타임 입력." width="300" >

> **중간 요약**: 행 지표 함수는 행의 객체를 파라미터로 받아 그 자원에 대한 구간별 값을 반환하며, 구성에서 해당 파라미터를 런타임 입력으로 지정하면 위젯이 행 객체를 자동으로 넘겨 줍니다.

<a id="widget-configuration"></a>
## 위젯 구성 (Widget configuration)

Scheduling Gantt Chart 위젯 구성에는 헤더 수준과 행 수준 지표 옵션을 포함하는 **Metrics** 섹션이 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/inline-metrics-config-section.png" alt="Scheduling Gantt Chart 구성 패널의 Metrics 섹션." width="300" >

지표 구성 설정에서는 표시 제목을 입력하고, 아이콘을 선택하고, 그리고/또는 조건부 색상을 설정할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/inline-metrics-config.png" alt="개별 지표 구성 화면." width="300" >

## 정리

- 인라인 지표는 간트 차트 안에 핵심 수치를 표시하며, x축 기준의 헤더 지표와 행 기준의 행 지표가 있습니다.
- 지표 함수는 `range`와 `value` 키를 가진 버킷 배열을 반환해야 하며, `range`는 Timestamp, LocalDate, Integer 범위를, `value`는 string, Integer, Double을 지원합니다.
- TypeScript v1은 `IRange`(`min`/`max`), v2는 `Range`(`startValue`/`endValue`)를 사용합니다.
- 헤더 지표 함수는 객체 입력 없이 시간 범위만으로 집계할 수 있고, 행 지표 함수는 런타임 입력으로 행 객체를 받습니다.
- 위젯의 **Metrics** 섹션에서 지표별 제목, 아이콘, 조건부 색상을 설정합니다.
