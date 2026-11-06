# 오류 타입 (Error types)

- 원문: https://www.palantir.com/docs/foundry/functions/typescript-error-types/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v1 > Error types

이 페이지는 TypeScript v1 함수(function)에서 출력 타입과 함께 오류 타입을 선언하는 방법을 다룹니다. 오류를 예외로 던지는 대신 "성공 값 또는 이름이 붙은 오류 값"을 반환 타입으로 표현하면, 이 함수를 질의(query)로 호출하는 다른 코드가 어떤 오류가 생길 수 있는지 타입으로 알고 오류 종류별로 처리할 수 있습니다.

**팁**: 다음 문서는 TypeScript v1 함수에만 해당합니다. 온톨로지 SDK 지원, 설정 가능한 리소스 요청 등 [더 강력한 기능](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 쓰려면 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)하는 것을 권장합니다.

TypeScript 함수에는 [출력 타입](../04_types-reference.md)뿐 아니라 오류 타입도 선언할 수 있습니다. 이는 특히 질의(query) 맥락에서 오류를 전파하고 처리할 때 유용합니다.

**설명**: 오류를 다루는 방식은 크게 두 가지입니다. 하나는 `throw`로 예외를 던지는 방식으로, 함수 시그니처만 보고는 어떤 오류가 날지 알 수 없습니다. 다른 하나는 반환값 자체를 "성공이면 결과, 실패면 오류 정보"를 담는 타입으로 만드는 방식으로, Rust의 `Result<T, E>`나 함수형 언어의 `Either` 타입이 대표적입니다. 이 페이지의 `FunctionsResult`는 두 번째 방식입니다.

<a id="define-an-error-type"></a>
## 오류 타입 정의하기 (Define an error type)

`@foundry/functions-api`에서 내보내는 `FunctionsError` 타입으로 오류 타입을 정의할 수 있습니다. 이 타입은 타입 파라미터 두 개를 받습니다. 하나는 문자열 이름이고, 다른 하나는 선택 사항인 타입으로 기본값은 빈 객체입니다. 함수의 [유효한 출력 타입](../04_types-reference.md)이라면 무엇이든(객체와 객체 집합(object set) 포함) 오류 타입으로 사용할 수 있습니다.

여러 `FunctionsError` 타입을 유니언(union)으로 묶어 함수에서 발생할 수 있는 오류 집합을 정의할 수 있습니다. 예를 들어 직원의 팀원 목록을 가져오는 함수에 다음과 같은 오류 타입을 정의할 수 있습니다.

```typescript
import { FunctionsError } from "@foundry/functions-api";
import { Employee } from "@foundry/ontology-api";

type GetTeammatesError =
    | FunctionsError<"EmployeeNotFoundForId", string>
    | FunctionsError<"MultipleEmployeesFoundForId", { employees: Employee[], employeeId: string }>
```

**설명**: 이 타입은 "오류는 두 종류 중 하나"라는 뜻입니다. 첫 번째 오류는 이름이 `"EmployeeNotFoundForId"`이고 함께 전달되는 값이 문자열(찾지 못한 ID)입니다. 두 번째 오류는 이름이 `"MultipleEmployeesFoundForId"`이고 함께 전달되는 값이 찾은 직원 배열과 ID를 담은 객체입니다. 오류 이름이 문자열 리터럴 타입이므로, 호출하는 쪽에서 이름으로 분기할 때 컴파일러가 오타를 잡아 줍니다.

<a id="declare-an-error-type-on-a-function"></a>
## 함수에 오류 타입 선언하기 (Declare an error type on a function)

TypeScript 함수에 오류 타입을 선언하려면 `@foundry/functions-api`에서 내보내는 `FunctionsResult` 타입을 사용합니다. 이 타입은 타입 파라미터 두 개, 즉 출력 타입과 오류 타입을 받습니다.

앞 절의 `GetTeammatesError` 예제를 사용하면, 함수에 다음과 같이 오류 타입을 선언할 수 있습니다.

```typescript
@Function()
public getTeammates(employeeId: string): FunctionsResult<Employee[], GetTeammatesError> {
    ...
}
```

(원문 예제에는 위 코드 앞에 `Function`, `FunctionsError`, `FunctionsResult`, `Employee` 임포트와 앞 절의 `GetTeammatesError` 정의가 함께 들어 있습니다.)

기본적으로 `FunctionsResult` 타입에는 TypeScript 함수 실행 인프라가 반환할 수 있는 몇 가지 오류가 포함됩니다.

* **`FunctionsTypeScriptExecutorService:CpuTimeoutError`:** 함수가 CPU 시간 제한을 넘으면 반환됩니다.
* **`FunctionsTypeScriptExecutorService:WallTimeoutError`:** 함수가 벽시계 시간(wall time) 제한을 넘으면 반환됩니다.
* **`FunctionsTypeScriptExecutorService:OutOfMemoryError`:** 함수가 메모리 제한을 넘으면 반환됩니다.
* **`FunctionsTypeScriptExecutorService:RuntimeError`:** 함수에서 그 밖의 런타임 오류가 발생하면 반환됩니다.

**설명**: CPU 시간은 프로세스가 실제로 CPU에서 연산한 시간이고, 벽시계 시간은 시작부터 끝까지 실제로 흐른 시간입니다. 함수가 다른 서비스의 응답을 기다리는 동안에는 CPU 시간은 거의 늘지 않지만 벽시계 시간은 계속 늘어납니다. 그래서 두 제한이 따로 있습니다.

> **중간 요약**: `FunctionsError<이름, 값 타입>`을 유니언으로 묶어 가능한 오류를 정의하고, 반환 타입을 `FunctionsResult<출력 타입, 오류 타입>`으로 선언합니다. 여기에는 CPU 시간 초과, 벽시계 시간 초과, 메모리 초과, 런타임 오류 같은 실행 인프라 오류가 기본으로 포함됩니다.

<a id="return-outputs-and-errors-in-your-function"></a>
## 함수에서 출력과 오류 반환하기 (Return outputs and errors in your function)

출력과 오류를 반환하려면 `@foundry/functions-api`에서 내보내는 `FunctionsResult.ok`와 `FunctionsResult.err` 메서드를 사용합니다.

* **`FunctionsResult.ok`:** 출력 값 하나를 인자로 받습니다.
* **`FunctionsResult.err`:** 오류 이름과 값을 인자로 받습니다.

앞 절의 `getTeammates` 예제를 사용하면, 출력과 오류를 다음과 같이 반환할 수 있습니다.

```typescript
import { Function, FunctionsError, FunctionsResult } from "@foundry/functions-api";
import { Employee } from "@foundry/ontology-api";

type GetTeammatesError =
    | FunctionsError<"EmployeeNotFoundForId", string>
    | FunctionsError<"MultipleEmployeesFoundForId", { employees: Employee[], employeeId: string }>

@Function()
public getTeammates(employeeId: string): FunctionsResult<Employee[], GetTeammatesError> {
    const employees = await Objects.search().employee([employeeId]).allAsync();
    if (employees.length === 0) {
        return FunctionsResult.err("EmployeeNotFoundForId", employeeId);
    }

    if (employees.length > 1) {
        return FunctionsResult.err("MultipleEmployeesFoundForId", { employees, employeeId });
    }

    const employee = employees[0];
    const teammates = await employee.teammates.allAsync();
    return FunctionsResult.ok(teammates);
}
```

**설명**: 직원 ID를 입력받아 해당 직원을 검색합니다. 결과가 0명이면 `EmployeeNotFoundForId` 오류를, 2명 이상이면 `MultipleEmployeesFoundForId` 오류를 반환하고, 정확히 1명이면 그 직원의 `teammates` 링크를 따라간 직원 목록을 `ok`로 감싸 반환합니다. 예를 들어 ID `"E-404"`로 검색한 결과가 없으면 반환값은 `err("EmployeeNotFoundForId", "E-404")`입니다. 오류도 `throw`가 아니라 `return`으로 돌려준다는 점이 핵심입니다.

<a id="handle-errors-from-queries"></a>
## 질의에서 오류 처리하기 (Handle errors from queries)

오류 타입이 있는 함수를 [다른 리포지토리에서 질의로 호출하면](../09_language-agnostic-features/02_query-functions.md#call-a-query-function), `ok` 또는 `err` 결과가 될 수 있는 `Result` 타입 응답이 반환됩니다.

`@foundry/functions-api`에서 내보내는 `isOk` 또는 `isErr` 타입 가드(type guard)를 사용해 두 가지 결과를 구별할 수 있습니다. 예를 들어 앞 절의 `getTeammates` 예제를 [질의로도 게시했다고](../09_language-agnostic-features/02_query-functions.md#query-decorator) 가정하고, 이를 호출해 응답을 다음과 같이 처리할 수 있습니다.

```typescript
import { Function, isOk } from "@foundry/function-api";
import { getTeammates } from "@foundry/ontology-api/queries";

@Function()
public async myFunction(employeeId: string): Promise<string> {
    const result = await getTeammates({ employeeId });

    if (isOk(result)) {
        const teammates = result.value;
        // 여기서 "teammates"로 원하는 작업을 합니다
        ...
    }

    // "name" 필드로 오류 이름별로 분기하고, "value" 필드로 오류 값을 얻을 수 있습니다
    switch (result.error.name) {
        case "EmployeeNotFoundForId": ...
        case "MultipleEmployeesFoundForId": ...
        case "FunctionsTypescriptExecutorService:OutOfMemoryError": ...
        ...
    }
}
```

**설명**: 타입 가드는 조건문 안에서 변수의 타입을 좁혀 주는 TypeScript 기능입니다. `if (isOk(result))` 블록 안에서는 컴파일러가 `result`를 성공 결과로 취급하므로 `result.value`(팀원 배열)에 접근할 수 있고, 그 밖에서는 오류 결과로 취급하므로 `result.error.name`과 `result.error.value`에 접근할 수 있습니다. `switch` 문은 정의된 오류 이름과 실행 인프라 오류 이름별로 다른 처리를 하는 자리입니다.

> **중간 요약**: 함수 안에서는 `FunctionsResult.ok(값)`과 `FunctionsResult.err(이름, 값)`으로 결과를 반환하고, 이 함수를 질의로 호출한 쪽에서는 `isOk`나 `isErr`로 결과를 구분한 뒤 `error.name`으로 오류 종류별 처리를 합니다.

## 정리

- TypeScript v1 함수는 출력 타입과 함께 오류 타입을 선언할 수 있으며, 질의 맥락에서 오류를 전파하고 처리할 때 유용합니다.
- 오류 타입은 `FunctionsError<이름, 값 타입>`의 유니언으로 정의하고, 함수 반환 타입은 `FunctionsResult<출력, 오류>`로 선언합니다.
- `FunctionsResult`에는 CPU 시간 초과, 벽시계 시간 초과, 메모리 초과, 런타임 오류가 기본으로 포함됩니다.
- 함수는 `FunctionsResult.ok`와 `FunctionsResult.err`로 결과를 반환하고, 호출하는 쪽은 `isOk`, `isErr` 타입 가드로 결과를 구분합니다.
