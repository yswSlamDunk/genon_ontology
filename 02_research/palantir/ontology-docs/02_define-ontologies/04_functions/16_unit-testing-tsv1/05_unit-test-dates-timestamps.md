# 날짜, 타임스탬프, UUID 모킹하기 (Mock dates, timestamps, and UUIDs)

- 원문: https://www.palantir.com/docs/foundry/functions/unit-test-dates-timestamps/
- 사이드바 위치: Define Ontologies > Functions > Unit testing (TSv1) > Mock dates, timestamps, and UUIDs

이 페이지는 TypeScript v1 함수(function)의 단위 테스트에서 실행할 때마다 결과가 달라지는 값(무작위 UUID, 현재 시각, 오늘 날짜)을 고정하는 방법을 설명합니다. 이런 값은 그대로 두면 기대값을 미리 적을 수 없으므로, Jest의 `jest.spyOn()`으로 가짜 구현을 주입해 항상 같은 값을 돌려주게 만듭니다.

`jest.spyOn()`을 활용해 모의 구현(mock)을 주입하면, 비결정적(non-deterministic) 함수의 출력을 지정한 상태로 테스트를 실행할 수 있습니다.

**설명**: 비결정적 함수는 같은 입력으로 호출해도 매번 다른 결과를 내는 함수입니다. `Uuid.random()`은 호출할 때마다 새 ID를, `Timestamp.now()`는 호출 시점의 시각을 반환합니다. 테스트에서 "생성된 객체의 ID가 X여야 한다"고 검증하려면 X를 미리 알아야 하므로, `jest.spyOn(객체, "메서드이름").mockImplementation(...)`으로 해당 메서드를 가로채 정해진 값을 반환하도록 바꿉니다. Jest는 JavaScript와 TypeScript에서 널리 쓰는 테스트 프레임워크입니다.

<a id="uuid-functions"></a>
### UUID 함수 (UUID functions)

**참고**: `@foundry/functions-utils`의 `Uuid` 유틸리티는 TypeScript v1에서 사용할 수 있으며 아래 예제에서 사용됩니다. TypeScript v2에서는 [`uuid` npm 패키지 ↗](https://www.npmjs.com/package/uuid) 같은 표준 UUID 라이브러리를 사용하고 테스트에서 그것을 직접 모킹하세요.

모의 구현을 주입해 `Uuid`의 출력을 지정할 수 있습니다. 다음은 예제입니다.

```typescript
import { MyFunctions } from ".."

import { Objects, ExampleDataFlight } from "@foundry/ontology-api";
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";
import { Uuid } from "@foundry/functions-utils";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("creates new flight", () => {
        const makeUuid = () => "my-uuid";
        jest.spyOn(Uuid, "random").mockImplementation(() => makeUuid());

        verifyOntologyEditFunction(() => myFunctions.createNewFlight())
            .createsObject({
                objectType: ExampleDataFlight,
                properties: {
                    flightId: makeUuid()
                }
            })
    })
});
```

이 테스트로 다음 함수를 테스트할 수 있습니다.

```typescript
import { Function, OntologyEditFunction, Edits } from "@foundry/functions-api";
import { Objects, ExampleDataFlight } from "@foundry/ontology-api";
import { Uuid } from "@foundry/functions-utils";

export class MyFunctions {
    @Edits(ExampleDataFlight)
    @OntologyEditFunction()
    public createNewFlight(): void {
        Objects.create().exampleDataFlight(Uuid.random());
    }
}
```

**설명**: 테스트 대상 `createNewFlight`는 입력 없이 `Uuid.random()`으로 만든 ID를 기본 키(primary key)로 하는 Flight 객체를 새로 만듭니다. 테스트에서는 `jest.spyOn(Uuid, "random")` 줄로 `Uuid.random()`이 항상 `"my-uuid"`를 반환하도록 바꾼 뒤, `verifyOntologyEditFunction(...).createsObject(...)`로 "`flightId`가 `"my-uuid"`인 `ExampleDataFlight` 객체가 생성되었는지" 확인합니다.

<a id="advanced-uuid-functions"></a>
#### 고급 UUID 함수 (Advanced UUID functions)

`Uuid`의 출력을 완전히 제어하고 싶은 경우가 있습니다. 이를 위해서는 테스트 대상 함수의 코드를 조정해야 합니다. 예를 들어 위의 `createNewFlight` 함수는 `MyFunctions` 클래스로 감싸져 있으므로, 기본값을 가진 공급자(supplier)를 받는 생성자를 클래스에 추가할 수 있습니다. 공급자를 사용하도록 수정한 함수는 다음과 같습니다.

```typescript
import { Function, OntologyEditFunction, Edits } from "@foundry/functions-api";
import { Objects, ExampleDataFlight } from "@foundry/ontology-api";
import { Uuid } from "@foundry/functions-utils";

export class MyFunctions {
    constructor (private UuidSupplier: () => string = Uuid.random){} // 클래스에 새로 추가한 이 생성자는 공급자를 받습니다

    @Edits(ExampleDataFlight)
    @OntologyEditFunction()
    public createNewFlightWithConstructor(): void {
        Objects.create().exampleDataFlight(this.UuidSupplier());
    }
}
```

이렇게 수정한 함수는 출력을 완전히 제어하면서 테스트할 수 있습니다(이 경우 생성되는 `Uuid`를 `my-other-uuid`로 정합니다).

(원문에는 이 함수를 테스트하는 코드가 더 있습니다. `new MyFunctions(() => "my-other-uuid")`로 인스턴스를 만든 뒤 `createNewFlightWithConstructor()`를 실행하고, `flightId`가 `"my-other-uuid"`인 `ExampleDataFlight` 객체가 생성되는지 `verifyOntologyEditFunction(...).createsObject(...)`로 확인합니다.)

**설명**: 이 방식은 의존성 주입(dependency injection)입니다. UUID를 만드는 함수를 클래스 안에서 직접 호출하지 않고 생성자 매개변수 `UuidSupplier`로 받아 둡니다. 실제 운영에서는 인수 없이 `new MyFunctions()`로 생성되므로 기본값인 `Uuid.random`이 쓰이고, 테스트에서는 `new MyFunctions(() => "my-other-uuid")`처럼 원하는 함수를 넘겨 출력을 정합니다. `jest.spyOn`으로 전역 메서드를 바꾸지 않아도 되므로 테스트끼리 서로 영향을 주지 않습니다.

> **중간 요약**: `jest.spyOn(Uuid, "random")`으로 UUID 출력을 고정하거나, 클래스 생성자로 UUID 공급자 함수를 주입받게 만들어 테스트에서 원하는 값을 넘깁니다.

<a id="timestampnow-functions"></a>
### Timestamp.now() 함수 (Timestamp.now() functions)

모의 구현을 주입해 `Timestamp.now()`의 출력을 지정할 수 있습니다. 다음은 예제입니다.

```typescript
import { MyFunctions } from ".."

import { Objects , ExampleDataFlight } from "@foundry/ontology-api";
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";
import { Timestamp } from "@foundry/functions-api";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("test timestamp now", () => {
        const makeTimestamp = () => Timestamp.fromISOString("2018-06-13T12:11:13+05:00");
        jest.spyOn(Timestamp, "now").mockImplementation(() => makeTimestamp());

        const flight = Objects.create().exampleDataFlight("flightAnotherTest");
        verifyOntologyEditFunction(() => myFunctions.startTakeoff(flight))
            .modifiesObject({
                object: flight,
                properties: {
                    takeoff: makeTimestamp()
                }
            })
    })
});
```

이 테스트로 다음 함수를 테스트할 수 있습니다.

(원문에는 테스트 대상 함수 코드가 있습니다. `startTakeoff(flight: ExampleDataFlight)`는 `@Edits(ExampleDataFlight)`와 `@OntologyEditFunction()` 데코레이터가 붙은 메서드로, `flight.takeoff = Timestamp.now();` 한 줄로 이륙 시각 속성을 현재 시각으로 설정합니다.)

**설명**: 테스트는 `Timestamp.now()`가 항상 `2018-06-13T12:11:13+05:00`을 반환하도록 바꾼 다음, 테스트용 Flight 객체를 만들어 `startTakeoff`에 넘깁니다. `modifiesObject(...)`는 이 함수가 해당 객체의 `takeoff` 속성(property)을 고정된 시각으로 수정했는지 확인합니다. 앞의 UUID 예제가 객체 "생성"을 검증했다면 이 예제는 기존 객체의 "수정"을 검증합니다.

<a id="localdatenow-functions"></a>
### LocalDate.now() 함수 (LocalDate.now() functions)

모의 구현을 주입해 `LocalDate.now()`의 출력을 지정할 수 있습니다. 다음은 예제입니다.

```typescript
const makeLocalDate = () => LocalDate.fromISOString("2018-06-13");
jest.spyOn(LocalDate, "now").mockImplementation(() => makeLocalDate());

const flight = Objects.create().exampleDataFlight("flightTest");
verifyOntologyEditFunction(() => myFunctions.dateTakeoff(flight))
    .modifiesObject({
        object: flight,
        properties: {
            date: makeLocalDate()
        }
    })
```

(위 코드는 원문 테스트의 핵심 부분만 옮긴 것입니다. 원문에는 `Timestamp` 예제와 같은 import 문과 `describe`, `test` 블록이 함께 있으며, `LocalDate`는 `@foundry/functions-api`에서 import합니다.)

이 테스트로 다음 함수를 테스트할 수 있습니다.

(원문에는 테스트 대상 함수 코드가 있습니다. `dateTakeoff(flight: ExampleDataFlight)`는 `flight.date = LocalDate.now();`로 날짜 속성을 오늘 날짜로 설정하는 온톨로지 편집 함수입니다.)

**설명**: `Timestamp`는 시각까지 포함한 값이고 `LocalDate`는 시간대 없이 날짜만 담는 값입니다. 고정하는 방법은 같으며, `LocalDate.now()`가 항상 2018년 6월 13일을 반환하도록 만든 뒤 `date` 속성이 그 값으로 수정되었는지 확인합니다.

> **중간 요약**: `Timestamp.now()`와 `LocalDate.now()`도 `jest.spyOn`으로 고정한 뒤, `modifiesObject`로 객체 속성이 그 값으로 수정되었는지 검증합니다.

## 정리

- 비결정적 함수(UUID 생성, 현재 시각, 오늘 날짜)는 `jest.spyOn(...).mockImplementation(...)`으로 고정된 값을 반환하게 만들어 테스트합니다.
- TypeScript v1의 `Uuid` 유틸리티 대신 TypeScript v2에서는 `uuid` 같은 표준 라이브러리를 모킹합니다.
- UUID 출력을 완전히 제어하려면 생성자에서 UUID 공급자 함수를 주입받도록 클래스를 바꿀 수 있습니다.
- 객체 생성은 `createsObject`, 기존 객체 수정은 `modifiesObject`로 검증합니다.
