# 온톨로지 편집 검증하기 (Verify Ontology edits)

- 원문: https://www.palantir.com/docs/foundry/functions/unit-test-ontology-edits/
- 사이드바 위치: Define Ontologies > Functions > Unit testing (TSv1) > Verify Ontology edits

이 페이지는 온톨로지를 수정하는 함수(온톨로지 편집 함수)가 기대한 편집(edit)을 정확히 만들어 내는지 단위 테스트로 확인하는 방법을 다룹니다. `verifyOntologyEditFunction()` API로 객체 생성, 속성 수정, 객체 삭제, 링크 추가와 제거를 검증하고, 그 밖의 편집이 없는지까지 확인하는 방법을 예제로 설명합니다.

`verifyOntologyEditFunction()` API를 사용하면 함수가 수행한 편집을 검증할 수 있습니다. 이 API는 `"@foundry/functions-testing-lib"`에서 import해야 합니다. 이를 통해 아래에 나열한 워크플로에 대한 단위 테스트를 만들 수 있습니다.

**설명**: 온톨로지 편집 함수(`@OntologyEditFunction()`이 붙은 함수)는 값을 반환하는 대신 객체를 만들거나 속성을 바꾸는 등의 편집을 일으킵니다. 반환값이 없으므로 `expect(반환값).toEqual(...)`로는 검사할 수 없습니다. `verifyOntologyEditFunction(() => 함수 호출)`은 함수를 실행하면서 발생한 편집 목록을 모아 두고, 그 뒤에 이어 붙인 `.createsObject(...)` 같은 메서드로 "이런 편집이 있었는가"를 하나씩 확인합니다.

<a id="singular-and-plural-verification-methods"></a>
#### 단수형과 복수형 검증 메서드 (Singular and plural verification methods)

각 종류의 편집은 단수형 메서드나 복수형 메서드로 검증할 수 있습니다. 단수형 메서드는 편집 하나를 검증하며 값 하나를 받고, 복수형 메서드는 같은 종류의 편집 여러 개를 검증하며 그 값들의 배열을 받습니다. 두 형태는 서로 바꿔 쓸 수 없으며, 잘못된 형태를 쓰면 타입 오류가 됩니다.

| 검증할 편집 | 편집 하나 검증 | 편집 여러 개 검증 |
| --------------------- | -------------------------------------------- | ------------------------------------------------- |
| 객체 생성 | `.createsObject({ objectType, properties })` | `.createsObjects([{ objectType, properties }])`   |
| 객체 속성 편집 | `.modifiesObject({ object, properties })`    | `.modifiesObjects([{ object, properties }])`      |
| 객체 삭제 | `.deletesObject(object)`                     | `.deletesObjects([object])`                       |
| 링크 생성 | `.addsLink({ link, linkedObject })`          | `.addsLinks([{ link, linkedObject }])`            |
| 링크 제거 | `.removesLink({ link, unlinkedObject })`     | `.removesLinks([{ link, unlinkedObject }])`       |

링크 관련 메서드 4개는 지금까지 수집된 편집을 인자로 받는 콜백(callback)도 받을 수 있습니다. 이는 링크할 객체가 테스트 대상 함수 안에서 생성된 경우에 유용합니다. 이 경우 `.addsLink`와 `.removesLink`의 콜백은 링크 하나를 반환하고, `.addsLinks`와 `.removesLinks`의 콜백은 배열을 반환합니다. 예는 [새로 생성된 객체에 대한 편집 검증하기](#verify-edits-on-a-newly-created-object)를 참고하세요.

`.hasNoMoreEdits()`에는 복수형이 없으며, 결과를 반환하지 않으므로 검증 체인의 맨 마지막에 와야 합니다.

**설명**: 메서드 체인(method chain)이란 `a().b().c()`처럼 앞 메서드가 반환한 객체에 다음 메서드를 이어 호출하는 방식입니다. `.createsObject(...)` 등은 다음 검증을 이어 붙일 수 있는 객체를 반환하지만, `.hasNoMoreEdits()`는 아무것도 반환하지 않으므로 그 뒤에는 더 붙일 수 없습니다.

> **중간 요약**: 편집 종류마다 단수형(값 하나)과 복수형(배열) 검증 메서드가 있으며 서로 바꿔 쓸 수 없습니다. 링크 메서드는 함수 안에서 새로 만든 객체를 가리키도록 콜백을 받을 수 있고, `.hasNoMoreEdits()`는 체인의 마지막에 둡니다.

<a id="verify-object-creation"></a>
#### 객체 생성 검증하기 (Verify object creation)

`.createsObject` 메서드를 사용해 객체 생성을 검증할 수 있습니다. 한 번의 호출로 여러 객체의 생성을 검증하려면 대신 [`.createsObjects`](#verify-multiple-objects-were-created)를 사용하세요. 예는 다음과 같습니다.

```typescript
import { MyFunctions } from ".."

import { Objects , ExampleDataAirport } from "@foundry/ontology-api";
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("create airport", () => { 
        verifyOntologyEditFunction(() => myFunctions.createAirport("airportCode", "airportDisplayName"))
            .createsObject(
                {
                    objectType: ExampleDataAirport,
                    properties: {
                        airport: "airportCode",
                        displayAirportName: "airportDisplayName",
                    },
                });
    });
});
```

이 테스트는 다음 함수를 테스트하는 데 사용할 수 있습니다.

```typescript
import { Function, OntologyEditFunction, Edits } from "@foundry/functions-api";
import { Objects, ExampleDataAirport } from "@foundry/ontology-api";

export class MyFunctions {

    @Edits(ExampleDataAirport)
    @OntologyEditFunction()
    public createAirport(airport: string, displayName: string): void {
        const newAirport = Objects.create().exampleDataAirport(airport);
        newAirport.displayAirportName = displayName;
    }
}
```

**설명**: 테스트 대상 함수 `createAirport`는 공항 코드와 표시 이름을 받아 `ExampleDataAirport` 객체를 하나 만들고 `displayAirportName` 속성을 채웁니다. `@Edits(ExampleDataAirport)`는 이 함수가 그 객체 타입을 편집한다고 선언합니다. 테스트는 `createAirport("airportCode", "airportDisplayName")`를 실행했을 때 `ExampleDataAirport` 타입 객체가 생성되었고, 그 객체의 `airport` 속성이 `"airportCode"`, `displayAirportName` 속성이 `"airportDisplayName"`인지 확인합니다.

<a id="verify-edits-on-a-newly-created-object"></a>
#### 새로 생성된 객체에 대한 편집 검증하기 (Verify edits on a newly created object)

새로 생성된 객체가 관련된 편집도 검증할 수 있습니다. 예를 들어 새 `ExampleDataFlight` 객체를 만들고, `new-flight-delay-0`으로의 링크가 생성되었는지 검증하고 싶을 수 있습니다. 예는 다음과 같습니다.

```typescript
import { MyFunctions } from ".."

import { Objects , ExampleDataFlight, ExampleFlightDelayEvent } from "@foundry/ontology-api";
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("single key with single created object", () => {
            const flight = Objects.create().exampleDataFlight("flightTest");
            verifyOntologyEditFunction(() => myFunctions.createAndLinkDelays(flight, 1))
                .createsObject({
                    objectType: ExampleFlightDelayEvent,
                    properties: {
                        eventId: "new-flight-delay-0",
                    },
                })
                .addsLink(edits => ({
                    link: flight.flightDelayEvent,
                    linkedObject: edits.createdObjects.byObjectType(ExampleFlightDelayEvent)[0],
                }))
        });
});
```

이 테스트는 다음 함수를 테스트하는 데 사용할 수 있습니다.

```typescript
import { Function, Integer, OntologyEditFunction, Edits } from "@foundry/functions-api";
import { Objects, ExampleDataFlight, ExampleFlightDelayEvent } from "@foundry/ontology-api";

export class MyFunctions {

    @Edits(ExampleDataFlight, ExampleFlightDelayEvent )
    @OntologyEditFunction()
    public createAndLinkDelays(flight: ExampleDataFlight, numDelay: Integer): void {
        for (let n = 0; n < numDelay; n++) {
            const delay = Objects.create().exampleFlightDelayEvent(`new-flight-delay-${n}`);
            flight.flightDelayEvent.add(delay);
        }
    }
}
```

**설명**: `createAndLinkDelays(flight, numDelay)`는 `numDelay`개의 지연 이벤트 객체(`new-flight-delay-0`, `new-flight-delay-1`, ...)를 만들고 각각을 `flight`에 링크합니다. 테스트에서는 `numDelay`를 1로 주었으므로 `new-flight-delay-0` 하나만 생깁니다. 문제는 이 지연 이벤트 객체가 함수 안에서 만들어지므로 테스트 코드가 그 객체를 미리 변수로 갖고 있지 않다는 점입니다. 그래서 `.addsLink`에 콜백 `edits => ({ ... })`를 넘기고, `edits.createdObjects.byObjectType(ExampleFlightDelayEvent)[0]`로 "이번 실행에서 생성된 `ExampleFlightDelayEvent` 객체 중 첫 번째"를 꺼내 링크 대상으로 지정합니다.

<a id="verify-object-property-edits"></a>
#### 객체 속성 편집 검증하기 (Verify object property edits)

`.modifiesObject`를 사용해 속성 편집을 검증할 수 있습니다. 한 번의 호출로 여러 객체의 속성 편집을 검증하려면 `.modifiesObjects`에 배열을 전달합니다. 예는 다음과 같습니다.

```typescript
import { MyFunctions } from ".."

import { Objects , ExampleDataFlight, ExampleFlightDelayEvent } from "@foundry/ontology-api";
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("modifies aircraft of the flight", () => {
        const flight = Objects.create().exampleDataFlight("NY -> LA");
        const oldAircraft = Objects.create().exampleDataAircraft("N11111");
        flight.aircraft.set(oldAircraft);
        const newAircraft = Objects.create().exampleDataAircraft("A00000");
        verifyOntologyEditFunction(() => myFunctions.assignAircraftToFlight(flight, newAircraft))
            .modifiesObject(
                { 
                    object: flight, 
                    properties: { 
                        tailNumber: "A00000" 
                    } 
                })
        });
});
```

이 테스트는 다음 함수를 테스트하는 데 사용할 수 있습니다.

```typescript
import { Function, OntologyEditFunction, Edits } from "@foundry/functions-api";
import { Objects, ExampleDataFlight, ExampleFlightDelayEvent } from "@foundry/ontology-api";

export class MyFunctions {

    @Edits(ExampleDataFlight)
    @OntologyEditFunction()
    public assignAircraftToFlight(flight: ExampleDataFlight, aircraft: ExampleDataAircraft): void {
        flight.aircraft.clear();
        aircraft.flight.set(flight);
        flight.tailNumber = aircraft.tailNumber;
    }
}
```

**설명**: 테스트는 먼저 항공편 `flight`에 기존 항공기(`N11111`)를 링크해 둔 상태를 만들고, 새 항공기(`A00000`)를 배정하는 함수를 실행합니다. 함수는 기존 항공기 링크를 지우고 새 항공기와 링크한 뒤 `flight.tailNumber`를 새 항공기의 값으로 바꿉니다. 테스트는 그중 "`flight` 객체의 `tailNumber` 속성이 `"A00000"`으로 수정되었는가"를 확인합니다.

> **중간 요약**: `.createsObject`는 생성된 객체의 타입과 속성 값을, `.modifiesObject`는 기존 객체의 바뀐 속성 값을 검증합니다. 함수 안에서 새로 만든 객체와의 링크는 콜백의 `edits.createdObjects.byObjectType(...)`로 대상을 찾아 검증합니다.

<a id="verify-no-other-edits-to-an-object"></a>
#### 객체에 다른 편집이 없는지 검증하기 (Verify no other edits to an object)

선택 사항인 `.hasNoMoreEdits()`를 사용해 다른 편집이 없는지 확인할 수 있습니다. 즉, 지정한 편집만 허용되며 다른 편집이 감지되면 검증이 실패합니다. 예는 다음과 같습니다.

```typescript
import { MyFunctions } from ".."

import { Objects , ExampleDataFlight, ExampleFlightDelayEvent } from "@foundry/ontology-api";
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("single key with linked object", () => {
            const flight = Objects.create().exampleDataFlight("flightAnotherTest");
            const delay = Objects.create().exampleFlightDelayEvent("new-flight-delay")
            verifyOntologyEditFunction(() => myFunctions.linkDelays(flight, delay))
                .addsLink({link: flight.flightDelayEvent, linkedObject: delay })
                .hasNoMoreEdits();
        });
});
```

`.hasNoMoreEdits()`를 사용할 때 특정 종류의 편집은 무시하도록 할 수 있습니다. 다음 항목의 일부 또는 전부를 담은 객체를 전달하면 됩니다.

* `ignoreExtraCreatedObjects: true`
* `ignoreExtraModifiedObjects: true`
* `ignoreExtraDeletedObjects: true`
* `ignoreExtraLinkedObjects: true`
* `ignoreExtraUnlinkedObjects: true`

**설명**: 예를 들어 `.hasNoMoreEdits({ ignoreExtraModifiedObjects: true })`라고 쓰면, 앞에서 명시한 편집 외에 추가로 속성이 수정된 객체가 있어도 실패로 보지 않고, 그 밖의 추가 생성, 삭제, 링크 추가, 링크 제거가 있으면 실패로 판정합니다. 각 옵션 이름이 무시할 편집 종류(생성, 수정, 삭제, 링크, 링크 해제)에 하나씩 대응합니다.

<a id="verify-link-creation-to-an-object"></a>
#### 객체에 대한 링크 생성 검증하기 (Verify link creation to an object)

`.addsLink`를 사용해 객체에 대한 링크 생성을 검증할 수 있습니다. 예는 다음과 같습니다.

```typescript
import { MyFunctions } from ".."

import { Objects , ExampleDataFlight, ExampleFlightDelayEvent } from "@foundry/ontology-api";
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("single key with linked object", () => {
            const flight = Objects.create().exampleDataFlight("flightAnotherTest");
            const delay = Objects.create().exampleFlightDelayEvent("new-flight-delay")
            verifyOntologyEditFunction(() => myFunctions.linkDelays(flight, delay))
                .addsLink({link: flight.flightDelayEvent, linkedObject: delay })
                .hasNoMoreEdits();
        });
});
```

이 테스트는 같은 링크를 반대 방향에서 테스트하는 것과 동일합니다. 즉, 위 코드의 `.addsLink` 줄을 `.addsLink({link: delay.flight, linkedObject: flight })`로 바꾼 테스트와 같습니다. (원문에는 이 반대 방향 버전의 전체 테스트 코드가 따로 있습니다.)

이 테스트는 다음 함수를 테스트하는 데 사용할 수 있습니다.

```typescript
import { Function, OntologyEditFunction, Edits } from "@foundry/functions-api";
import { Objects, ExampleDataFlight, ExampleFlightDelayEvent } from "@foundry/ontology-api";

export class MyFunctions {

    @Edits(ExampleDataFlight, ExampleFlightDelayEvent )
    @OntologyEditFunction()
    public linkDelays(flight: ExampleDataFlight, delay: ExampleFlightDelayEvent): void {
        flight.flightDelayEvent.add(delay);
    }
}
```

**설명**: `linkDelays`는 항공편과 지연 이벤트를 받아 둘을 링크합니다. 링크는 양방향 관계이므로 "항공편 쪽에서 본 `flightDelayEvent` 링크에 `delay`가 추가됨"과 "지연 이벤트 쪽에서 본 `flight` 링크에 `flight`가 추가됨"은 같은 편집입니다. 데이터베이스로 보면 두 테이블을 잇는 외래 키 값 하나가 생긴 것이며, 어느 테이블 쪽에서 조인하든 같은 관계가 보이는 것과 같습니다. 테스트 끝의 `.hasNoMoreEdits()`는 이 링크 추가 외에 다른 편집이 없음을 확인합니다.

<a id="verify-link-removal-from-an-object"></a>
#### 객체에서 링크 제거 검증하기 (Verify link removal from an object)

`.removesLink`를 사용해 객체에서 링크가 제거되었는지 검증할 수 있습니다. 예는 다음과 같습니다.

```typescript
import { MyFunctions } from ".."

import { Objects , ExampleDataFlight, ExampleFlightDelayEvent } from "@foundry/ontology-api";
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("test link removal", () => {
            const flight = Objects.create().exampleDataFlight("flightAnotherTest");
            const delay = Objects.create().exampleFlightDelayEvent("new-flight-delay")
            flight.flightDelayEvent.add(delay);
            verifyOntologyEditFunction(() => myFunctions.removeAllDelays(flight))
                .removesLink({link: flight.flightDelayEvent, unlinkedObject: delay })
                .hasNoMoreEdits();
        });
});
```

이 테스트는 `flight.flightDelayEvent.clear()`로 항공편의 모든 지연 이벤트 링크를 지우는 `removeAllDelays(flight)` 함수를 테스트하는 데 사용할 수 있습니다. (원문에는 이 함수의 전체 코드가 있습니다. 구조는 위 `linkDelays`와 같고 본문만 `clear()` 호출입니다.)

**설명**: 테스트는 먼저 `flight`와 `delay`를 링크해 둔 초기 상태를 만들고, 함수를 실행한 뒤 그 링크가 제거되었는지(`unlinkedObject: delay`) 확인합니다.

<a id="verify-deleting-an-object"></a>
#### 객체 삭제 검증하기 (Verify deleting an object)

`.deletesObject`를 사용해 객체 삭제를 검증할 수 있습니다. 예는 다음과 같습니다.

```typescript
import { MyFunctions } from ".."

import { Objects , ExampleDataFlight } from "@foundry/ontology-api";
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("test object deletion", () => {
            const flight = Objects.create().exampleDataFlight("flightAnotherTest");
            verifyOntologyEditFunction(() => myFunctions.deleteFlight(flight))
                .deletesObject(flight)
                .hasNoMoreEdits();
        });
});
```

이 테스트는 `@Edits(ExampleDataFlight)`와 `@OntologyEditFunction()`이 붙어 있고 본문에서 `flight.delete()`를 호출하는 `deleteFlight(flight)` 함수를 테스트하는 데 사용할 수 있습니다. (원문에는 이 함수의 전체 코드가 있습니다.)

> **중간 요약**: `.hasNoMoreEdits()`는 명시한 편집 외의 편집이 없음을 확인하며, `ignoreExtra...` 옵션으로 특정 종류는 무시할 수 있습니다. 링크 추가, 링크 제거, 객체 삭제는 각각 `.addsLink`, `.removesLink`, `.deletesObject`로 검증하고, 링크는 어느 방향에서 검증해도 같습니다.

<a id="verify-multiple-objects-were-created"></a>
#### 여러 객체가 생성되었는지 검증하기 (Verify multiple objects were created)

`.createsObjects` 메서드에 객체 명세의 배열을 전달해 여러 객체가 생성되었는지 검증할 수 있습니다. 예는 다음과 같습니다.

```typescript
import { MyFunctions } from ".."

import { Objects , ExampleDataFlight, ExampleFlightDelayEvent } from "@foundry/ontology-api";
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("single key with many created objects", () => {
            const flight = Objects.create().exampleDataFlight("flightTest");
            verifyOntologyEditFunction(() => myFunctions.createAndLinkDelays(flight, 3))
                .createsObjects(
                    [0, 1, 2].map(i => ({
                        objectType: ExampleFlightDelayEvent,
                        properties: {
                            eventId: "new-flight-delay-" + i,
                        },
                    })),
                )
                .addsLinks(edits =>
                    edits.createdObjects.byObjectType(ExampleFlightDelayEvent).map(event => ({
                        link: flight.flightDelayEvent,
                        linkedObject: event,
                    })),
                )
                .hasNoMoreEdits();
        });
});
```

이 테스트는 앞의 [새로 생성된 객체에 대한 편집 검증하기](#verify-edits-on-a-newly-created-object)에 나온 것과 같은 `createAndLinkDelays` 함수를 테스트하는 데 사용할 수 있습니다. (원문에는 그 함수 코드가 다시 실려 있습니다.)

**설명**: 이번에는 `numDelay`를 3으로 주었으므로 함수는 `new-flight-delay-0`, `new-flight-delay-1`, `new-flight-delay-2` 세 객체를 만들고 모두 `flight`에 링크합니다. 테스트는 `[0, 1, 2].map(...)`으로 기대하는 객체 명세 3개의 배열을 만들어 `.createsObjects`에 넘기고, `.addsLinks`의 콜백에서는 생성된 지연 이벤트 객체 전부를 `map`으로 링크 명세 배열로 바꿔 반환합니다. 마지막 `.hasNoMoreEdits()`로 그 밖의 편집이 없음을 확인합니다.

<a id="asynchronous-ontology-edits"></a>
### 비동기 온톨로지 편집 (Asynchronous ontology edits)

비동기 온톨로지 편집은 다음과 같이 검증할 수 있습니다.

```typescript
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";

test("test async edit function", async () => {
        const obj = Objects.create().objectWithAllPropertyTypes(1);
        (await verifyOntologyEditFunction(() => myFunctions.setDateAndTimestampToNow(obj))).modifiesObject({
            object: obj,
            properties: {
                timestampProperty: makeTimestamp(),
            },
        });
    });
```

**설명**: 테스트 대상 함수가 `async` 함수(Promise를 반환하는 함수)이면 편집이 비동기로 끝납니다. 이때는 테스트 함수도 `async`로 선언하고, `verifyOntologyEditFunction(...)`의 결과를 `await`로 기다린 다음에 `.modifiesObject(...)`를 호출해야 합니다. 괄호로 `(await ...)`를 감싼 것이 그 순서를 지키기 위한 부분입니다.

<a id="multiple-verifications"></a>
### 여러 검증 이어 붙이기 (Multiple verifications)

위 예제에서 본 것처럼 검증을 체인으로 이어 붙일 수 있습니다. 다음 패턴이 이를 보여 줍니다.

```typescript
import { verifyOntologyEditFunction } from "@foundry/functions-testing-lib";
import { Objects, ExampleDataObject } from "@foundry/ontology-api";

test("multiple action edit", () => { 
    verifyOntologyEditFunction(() => myFunctions.multistageEdits("objectId", "objectName"))
        .createsObject({...})
        .modifiesObjects([{...}])
        .addsLinks([{...}])
        .removesLinks([{...}])
        .deletesObject(...)
        .hasNoMoreEdits(); 
});
```

**설명**: 하나의 함수가 여러 종류의 편집을 일으키면, 각 편집에 맞는 검증 메서드를 단수형이든 복수형이든 필요한 만큼 이어 붙이고 마지막에 `.hasNoMoreEdits()`를 둡니다. 코드의 `{...}`는 앞 예제들에서 본 명세 객체가 들어갈 자리를 줄여 쓴 것입니다.

> **중간 요약**: 여러 객체 생성은 `.createsObjects`와 `.addsLinks` 콜백으로 한 번에 검증합니다. 비동기 편집 함수는 `await verifyOntologyEditFunction(...)` 후에 검증하고, 여러 검증은 체인으로 이어 붙입니다.

## 정리

- `verifyOntologyEditFunction(() => 함수 호출)`은 온톨로지 편집 함수가 일으킨 편집을 모아 검증할 수 있게 합니다.
- 객체 생성, 속성 수정, 삭제, 링크 추가, 링크 제거마다 단수형과 복수형 검증 메서드가 있으며 서로 바꿔 쓸 수 없습니다.
- 함수 안에서 새로 만든 객체는 링크 메서드의 콜백에서 `edits.createdObjects.byObjectType(...)`로 찾아 검증합니다.
- `.hasNoMoreEdits()`는 체인 마지막에 두어 다른 편집이 없음을 확인하고, `ignoreExtra...` 옵션으로 일부 종류는 무시할 수 있습니다.
- 비동기 편집 함수는 `await`로 결과를 기다린 뒤 검증합니다.
