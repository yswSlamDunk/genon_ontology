# 스텁 객체 만들기 (Create stub objects)

- 원문: https://www.palantir.com/docs/foundry/functions/unit-test-stub-objects/
- 사이드바 위치: Define Ontologies > Functions > Unit testing (TSv1) > Create stub objects

이 페이지는 단위 테스트에서 실제 온톨로지 데이터 대신 쓸 가짜 객체(mock object)를 `Objects.create()`로 만드는 방법을 보여 줍니다. 객체를 입력으로 받는 함수를 테스트하려면 테스트 안에서 그 객체를 직접 만들어 넘겨야 하는데, 이 페이지가 그 기본 방법을 다룹니다.

`Objects.create()`를 사용해 모의 객체(mock object)를 만들고 정의할 수 있으며, 이는 일반 함수 안에서 쓰는 것과 같은 방식으로 사용할 수 있습니다. 이렇게 만든 모의 객체를 단위 테스트를 작성할 때 사용할 수 있습니다. 예는 다음과 같습니다.

```typescript
import { MyFunctions } from ".."

import { Objects, ExampleDataAirport } from "@foundry/ontology-api";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();

    test("test created objects", () => {
        const JFK = Objects.create().exampleDataAirport("JFK Test");
        JFK.displayAirportName = "John F. Kennedy International";
        expect(myFunctions.getAirportName(JFK)).toEqual("John F. Kennedy International");
    });
});
```

참고로 위 예제는 Jest 문법인 [`expect(...).toEqual(...)` ↗](https://jestjs.io/docs/expect#toequalvalue)를 사용합니다.

**설명**: 스텁(stub) 또는 모의 객체는 테스트를 위해 만든 가짜 데이터입니다. 실제 온톨로지에 저장된 객체를 읽어 오지 않으므로 테스트 결과가 외부 데이터 상태에 따라 바뀌지 않습니다. 위 코드의 동작은 다음과 같습니다.
1. `Objects.create().exampleDataAirport("JFK Test")`: 기본 키(primary key)가 `"JFK Test"`인 `ExampleDataAirport` 객체를 테스트용으로 하나 만듭니다.
2. `JFK.displayAirportName = ...`: 그 객체의 `displayAirportName` 속성(property)에 값을 넣습니다.
3. `myFunctions.getAirportName(JFK)`: 테스트 대상 함수에 이 객체를 넘기고, 반환값이 방금 넣은 이름과 같은지 확인합니다.

## 정리

- 테스트용 객체는 `Objects.create().<객체 타입>(기본 키)`로 만들고, 속성은 일반 대입문으로 채웁니다.
- 이렇게 만든 스텁 객체를 테스트 대상 함수에 넘겨, 실제 데이터 없이 함수의 동작을 확인합니다.
