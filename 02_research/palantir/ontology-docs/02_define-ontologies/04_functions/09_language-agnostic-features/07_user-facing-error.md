# 사용자 대상 오류 (User-facing errors)

- 원문: https://www.palantir.com/docs/foundry/functions/user-facing-error/
- 사이드바 위치: Define Ontologies > Functions > Language-agnostic features > User-facing errors

이 페이지는 함수(function)가 실패할 때 최종 사용자에게 보여 줄 구체적인 오류 메시지를 지정하는 `UserFacingError`를 설명합니다. Workshop이나 액션에서 함수를 실행한 사용자가 무엇이 잘못되었는지 알고 스스로 고칠 수 있게 하려면 이 기능이 필요합니다.

## 사용자 대상 오류 던지기

Workshop이나 액션처럼 플랫폼의 다른 부분에서 함수를 실행할 때, 자세한 메시지가 담긴 오류를 던지고 싶을 수 있습니다. 그렇게 하려면 `UserFacingError`를 던집니다. 예를 들면 다음과 같습니다.

```typescript tab="TypeScript v2"
import { Osdk } from "@osdk/client";
import { Employee } from "@ontology/sdk";
import { UserFacingError } from "@osdk/functions";

export default async function searchExactlyFiveEmployees(employees: Array<Osdk.Instance<Employee>>): Promise<string> {
    if (employees.length != 5) {
        throw new UserFacingError(`Pass in exactly 5 employees. Received ${employees.length}.`);
    }

    // employees 검색
}
```

(원문에는 `@foundry/functions-api`의 `UserFacingError`를 사용하는 TypeScript v1 버전과, `raise UserFacingError(...)`를 사용하는 Python 버전도 있습니다.)

**설명**: 이 함수는 Employee 객체 배열을 입력받아, 개수가 정확히 5개가 아니면 `UserFacingError`를 던집니다. 예를 들어 3명을 넘기면 "Pass in exactly 5 employees. Received 3."이라는 메시지가 사용자에게 그대로 표시됩니다. 일반 `Error`를 던지면 사용자는 보통 원인을 알 수 없는 일반적인 실패 메시지만 보게 되지만, `UserFacingError`의 메시지는 사용자에게 보여 주려는 의도로 작성된 것으로 취급됩니다.

이 함수를 [Workshop 애플리케이션](https://www.palantir.com/docs/foundry/workshop/functions-use/)에서 [함수 기반 액션(Function-backed Action)](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)으로 실행하면서 직원 수를 잘못 넘기면, 사용자는 다음 오류를 보게 됩니다.

![사용자 대상 오류](https://www.palantir.com/docs/resources/foundry/functions/user-facing-error.png)

[함수 기반 내보내기(function-backed export)](https://www.palantir.com/docs/foundry/workshop/widgets-button-group/#function-backed-export)에서 사용하는 함수가 `UserFacingError`를 던지면, 내보내기 실패 토스트(toast) 알림에 오류 메시지가 표시됩니다.

자세한 사용자 대상 오류 메시지는 사용자가 문제를 파악하고 해결하는 데 도움이 됩니다.

## 정리

- 함수에서 `UserFacingError`를 던지면 지정한 메시지가 Workshop, 액션 등의 화면에서 사용자에게 그대로 표시됩니다.
- TypeScript v1, TypeScript v2, Python 모두 `UserFacingError`를 제공합니다.
- 함수 기반 내보내기에서는 실패 토스트 알림에 메시지가 표시됩니다.
- 입력 검증 실패처럼 사용자가 직접 고칠 수 있는 문제는 구체적인 메시지로 알려 주는 것이 좋습니다.
