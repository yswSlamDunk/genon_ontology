# undefined 값 처리하기 (Handle undefined values)

- 원문: https://www.palantir.com/docs/foundry/functions/undefined-values/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v1 > Handle undefined values

이 페이지는 TypeScript v1 함수(function)에서 객체의 속성(property)이나 링크에 접근했을 때 값이 없어 `undefined`가 나오는 경우를 처리하는 두 가지 방법을 비교합니다. 온톨로지 객체의 속성은 비어 있을 수 있으므로, TypeScript 컴파일러는 이런 값을 `string | undefined`처럼 다루며 그대로 쓰면 타입 오류를 냅니다.

**팁**: 다음 문서는 TypeScript v1 함수에만 해당합니다. 온톨로지 SDK 지원, 설정 가능한 리소스 요청 등 [더 강력한 기능](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 쓰려면 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)하는 것을 권장합니다.

아래는 속성이나 링크에 접근할 때 반환될 수 있는 `undefined` 값을 처리하는 데 유용한 두 가지 패턴입니다.

**설명**: 데이터베이스 테이블의 열에 `NULL`이 들어 있을 수 있는 것처럼, 객체의 속성 값도 비어 있을 수 있습니다. 예를 들어 Employee 데이터셋의 한 행에 `last_name` 칸이 비어 있으면, 그 객체의 `employee.lastName`은 `undefined`입니다. TypeScript의 엄격한 null 검사(strict null checks)는 이런 가능성이 있는 값을 `string`이 필요한 자리에 그대로 쓰지 못하게 막습니다.

<a id="explicit-checks"></a>
### 명시적 검사 (Explicit checks)

```typescript
@Function()
public getFullName(employee: Employee): string {
    if (!(employee.firstName && employee.lastName)) {
        throw new UserFacingError("Cannot derive full name because either first or last name is undefined.");
    }
    return employee.firstName + " " + employee.lastName;
}
```

`firstName`과 `lastName` 필드가 모두 정의되어 있는지 검사하면, TypeScript 컴파일러는 `return` 문이 있는 마지막 줄이 올바르게 컴파일될 수 있다는 것을 압니다. 이 방식의 장점은 타입 검사가 더 명시적이라는 점이고, `undefined` 값이 있을 때 무엇이 잘못되었는지 더 명확한 오류를 던질 수 있다는 점입니다.

**설명**: `if` 조건에서 두 값이 모두 참(truthy)인지 확인하고 아니면 오류를 던지므로, `if` 문 다음 줄에 도달했다면 두 값이 모두 존재한다는 것이 보장됩니다. TypeScript 컴파일러는 이 흐름을 분석해 그 뒤에서는 두 필드의 타입을 `string`으로 좁혀 줍니다(타입 좁히기, narrowing). `UserFacingError`는 사용자 화면에 그대로 보여 줄 수 있는 오류 메시지를 담는 오류 타입입니다. 참고로 이 검사는 빈 문자열 `""`도 거짓으로 취급하므로 빈 이름도 오류로 처리됩니다.

<a id="non-null-assertion-operator"></a>
### non-null 단언 연산자 (Non-null assertion operator)

TypeScript의 [non-null 단언 연산자 ↗](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-0.html#non-null-assertion-operator)(`!`)를 사용해 `undefined`인 경우를 무시할 수 있습니다.

```typescript
@Function()
public getFullName(employee: Employee): string {
    return employee.firstName! + " " + employee.lastName!;
}
```

이 방식은 TypeScript 컴파일러의 판단을 무시하고, 접근하는 필드가 정의되어 있다고 단언(assert)할 뿐입니다. 코드는 더 간결해지지만, 필드 중 하나가 실제로 `undefined`인 경우 알아보기 어려운 오류로 이어질 수 있습니다. 가능하면 명시적 검사를 하는 것을 권장합니다.

**설명**: `!`는 실행 시점에 아무 검사도 하지 않고 컴파일러에게 "이 값은 undefined가 아니다"라고 알려 주기만 합니다. 따라서 `lastName`이 실제로 비어 있으면 오류가 나는 대신 `"Kim undefined"` 같은 잘못된 문자열이 반환될 수 있고, 다른 맥락(예: `employee.manager!.name`)에서는 원인을 짐작하기 어려운 `TypeError`가 납니다.

## 정리

- 객체의 속성이나 링크에 접근하면 값이 비어 있어 `undefined`가 나올 수 있으며, TypeScript는 이를 그대로 쓰지 못하게 합니다.
- 명시적 검사는 `if`로 값의 존재를 확인하고 없으면 `UserFacingError`를 던지는 방식으로, 타입이 안전하게 좁혀지고 오류 메시지가 명확합니다.
- non-null 단언 연산자 `!`는 코드가 짧지만 실제로 값이 없으면 알아보기 어려운 오류로 이어집니다.
- 가능하면 명시적 검사가 권장됩니다.
