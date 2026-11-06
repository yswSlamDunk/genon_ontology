# 사용자와 그룹 모킹하기 (Mock users and groups)

- 원문: https://www.palantir.com/docs/foundry/functions/unit-test-users-groups/
- 사이드바 위치: Define Ontologies > Functions > Unit testing (TSv1) > Mock users and groups

이 페이지는 TypeScript v1 함수(function)의 단위 테스트에서 Foundry 사용자(user)와 그룹(group)을 가짜로 만드는 방법을 설명합니다. 함수가 사용자나 그룹 정보를 조회하는 경우, 테스트 환경에는 실제 사용자 디렉터리가 없으므로 `createUser`와 `createGroup`으로 필요한 필드만 채운 모의 객체를 만들어 씁니다.

<a id="user-mocks"></a>
### 사용자 모킹 (User mocks)

`createUser`를 사용해 사용자의 부분 모의 객체(partial mock)를 만들 수 있으며, `id`와 `username`을 제외한 모든 속성은 선택 사항입니다. `"@foundry/functions-testing-lib"`에서 `{ createUser }`를 import해야 합니다.

```typescript
import { MyFunctions } from ".."

import { verifyOntologyEditFunction, createGroup, createUser } from "@foundry/functions-testing-lib";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();
    test("test users and groups", async () => {
        const group = createGroup({
            id: "groupId",
        });
        const user = createUser({
            id: "userId",
            username: "username",
        });
        await expect(myFunctions.searchUsers("userId", "groupId")).resolves.toEqual([user, group]);
    });
});
```

이 테스트로 다음 함수를 테스트할 수 있습니다.

```typescript
import { Function, OntologyEditFunction, Users, Group, Principal } from "@foundry/functions-api";

export class MyFunctions {
    @Function()
    public async searchUsers(userId: string, groupId: string): Promise<Principal[]> {
        const existingPrincipals = await Promise.all([
            Users.getUserByIdAsync(userId),
            Users.getGroupByIdAsync(groupId),
        ]);
        return existingPrincipals.filter(r => !!r).map(r => r!);
    }
}
```

**설명**: 테스트 대상 `searchUsers`는 사용자 ID와 그룹 ID를 입력받아 `Users.getUserByIdAsync`와 `Users.getGroupByIdAsync`로 두 주체(principal)를 동시에 조회하고, 찾지 못해 비어 있는 결과를 걸러 낸 배열을 반환합니다. Principal은 권한을 받을 수 있는 대상(사용자 또는 그룹)을 통칭하는 말입니다. 테스트에서는 `createUser`와 `createGroup`으로 ID가 `"userId"`, `"groupId"`인 모의 사용자와 그룹을 만들고, 함수 결과가 `[user, group]`과 같은지 확인합니다. 모의 객체를 만들어 두면 테스트 라이브러리가 해당 ID 조회에 그 객체를 돌려주는 것으로 이해할 수 있습니다.

> **중간 요약**: `createUser`는 `id`와 `username`만 필수로 채우는 모의 사용자를 만들며, 사용자 조회 함수가 그 객체를 반환하는지 테스트할 수 있습니다.

<a id="group-mocks"></a>
### 그룹 모킹 (Group mocks)

`createGroup`을 사용해 그룹의 부분 모의 객체도 만들 수 있으며, `id`를 제외한 모든 속성은 선택 사항입니다. `"@foundry/functions-testing-lib"`에서 `{ createGroup }`을 import해야 합니다.

```typescript
import { MyFunctions } from ".."

import { verifyOntologyEditFunction, createGroup } from "@foundry/functions-testing-lib";

describe("example test suite", () => {
    const myFunctions = new MyFunctions();
    test("test groups", async () => {
        const group = createGroup({
            id: "groupId",
        });
        await expect(myFunctions.searchGroups("groupId")).resolves.toEqual([group]);
    });
});
```

이 테스트로 다음 함수를 테스트할 수 있습니다.

(원문에는 테스트 대상 함수 코드가 있습니다. `searchGroups(groupId: string)`은 앞의 `searchUsers`와 같은 구조로, `Users.getGroupByIdAsync(groupId)`만 호출해 찾은 그룹을 배열로 반환하는 `@Function()` 메서드입니다.)

**설명**: 그룹은 사용자 이름에 해당하는 필드가 없으므로 `id` 하나만 필수입니다. 테스트는 모의 그룹을 만든 뒤 `searchGroups("groupId")`의 결과가 `[group]`인지 확인합니다.

> **중간 요약**: `createGroup`은 `id`만 필수인 모의 그룹을 만들며, 그룹 조회 함수의 결과를 검증하는 데 씁니다.

## 정리

- 함수가 사용자나 그룹을 조회하는 경우 `@foundry/functions-testing-lib`의 `createUser`, `createGroup`으로 모의 객체를 만듭니다.
- `createUser`는 `id`와 `username`, `createGroup`은 `id`만 필수이고 나머지 속성은 선택입니다.
- 모의 객체를 만든 뒤 함수가 그 객체를 반환하는지 `expect(...).resolves.toEqual(...)`로 확인합니다.
