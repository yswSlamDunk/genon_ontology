# 단위 테스트 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/functions/unit-test-getting-started/
- 사이드바 위치: Define Ontologies > Functions > Unit testing (TSv1) > Getting started

이 페이지는 TypeScript v1 함수(function) 저장소에서 Jest로 단위 테스트(unit test)를 작성하고 실행하는 기본 방법을 다룹니다. 테스트 파일 위치, 간단한 함수와 그 테스트 예제, 테스트 실행 버튼, 커밋 시 자동 실행되는 검사(Checks)를 설명합니다. 이후 페이지들에서 다루는 온톨로지 관련 테스트 기법의 출발점입니다.

Functions는 [Jest ↗](https://jestjs.io/) 단위 테스트를 지원합니다. 이 가이드의 단계를 따라 저장소에 단위 테스트 도구를 설정하세요.

기본적으로 함수 저장소에는 `functions-typescript/src/__tests__/index.ts` 테스트 파일에 단위 테스트 하나가 들어 있습니다. 테스트 파일은 `__tests__` 폴더 안 어디에나 만들 수 있습니다.

**설명**: 단위 테스트는 함수 하나처럼 작은 코드 단위에 정해진 입력을 넣고, 기대한 출력이 나오는지 자동으로 확인하는 코드입니다. Jest는 JavaScript와 TypeScript에서 널리 쓰이는 테스트 프레임워크로, `describe`로 테스트를 묶고 `test`로 개별 테스트를 정의하며 `expect(실제값).toEqual(기대값)`으로 결과를 비교합니다.

<a id="example"></a>
## 예제 (Example)

예를 들어 `functions-typescript/src/index.ts`에 있는 다음 `addOne` 함수를 테스트하고 싶다고 합시다.

```typescript
import { Function, Integer } from "@foundry/functions-api";

export class MyFunctions {

    @Function()
    public addOne(n: Integer): Integer {
         return n + 1;
    }
}
```

다음과 같은 `test add one` 테스트를 작성해 `addOne` 함수를 테스트할 수 있습니다.

```typescript
import { MyFunctions } from ".."

describe("example test suite", () => {
    const myFunctions = new MyFunctions();
    test("test add one", () => {
        expect(myFunctions.addOne(42)).toEqual(43);
    });
});
```

**설명**: 첫 번째 코드는 정수 `n`을 받아 `n + 1`을 반환하는 함수입니다. 두 번째 코드는 그 테스트입니다. `import { MyFunctions } from ".."`로 상위 폴더(`src`)의 `index.ts`에서 클래스를 가져오고, `new MyFunctions()`로 인스턴스를 만든 뒤 `addOne(42)`를 호출합니다. 결과가 43이면 테스트가 통과하고, 다른 값이면 실패로 표시됩니다.

사용할 수 있는 전체 테스트 API는 [Jest API ↗](https://jestjs.io/docs/en/api)를 참고하세요.

<a id="running-tests"></a>
## 테스트 실행하기 (Running tests)

오른쪽 위에 있는 `Test` 버튼을 클릭하면 모든 테스트를 실행할 수 있고, 각 테스트의 줄 번호 옆에 있는 삼각형 "Play" 버튼을 클릭하면 테스트를 하나씩 실행할 수 있습니다.

![테스트 실행 버튼](https://www.palantir.com/docs/resources/foundry/functions/button-run-tests.png)

**Commit**을 클릭하면 모든 테스트가 Checks에서도 실행됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/run-tests.png" alt="테스트 실행" width="500"/>

**설명**: Checks는 커밋할 때마다 저장소에서 자동으로 실행되는 검사 단계입니다. 테스트가 여기서 함께 실행되므로, 누군가 코드를 고쳐 기존 동작이 깨지면 커밋 직후 실패로 드러납니다.

<a id="next-steps"></a>
## 다음 단계 (Next steps)

다음으로, 온톨로지와 상호작용하는 함수를 테스트하는 데 사용할 수 있는 여러 방법을 알아보세요.

* [스텁 객체 만들기](02_unit-test-stub-objects.md)
* [온톨로지 편집 검증하기](03_unit-test-ontology-edits.md)
* [객체 검색과 집계 스텁 만들기](04_unit-test-object-searches.md)

## 정리

- TypeScript v1 함수 저장소는 Jest 단위 테스트를 기본 지원하며, 테스트 파일은 `__tests__` 폴더 안에 둡니다.
- `describe`, `test`, `expect(...).toEqual(...)`로 함수의 입력과 기대 출력을 검사합니다.
- `Test` 버튼으로 전체 테스트를, 줄 번호 옆 Play 버튼으로 개별 테스트를 실행하며, 커밋하면 Checks에서도 실행됩니다.
