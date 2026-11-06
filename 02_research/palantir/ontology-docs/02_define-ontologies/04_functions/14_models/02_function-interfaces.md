# 함수 인터페이스 (Function interfaces)

- 원문: https://www.palantir.com/docs/foundry/functions/function-interfaces/
- 사이드바 위치: Define Ontologies > Functions > Models > Function interfaces

이 페이지는 함수(function)가 지켜야 할 입력, 출력, 오류의 형태를 미리 정해 두는 "함수 인터페이스"를 설명합니다. Foundry 애플리케이션(예: AIP Logic)은 이 계약을 기준으로 사용자가 직접 작성한 함수를 찾아내고 실행합니다. Palantir가 제공하는 `ChatCompletion` 인터페이스, 타입을 확장해서 구현하는 방법, 구현할 때 자주 만나는 컴파일 오류를 다룹니다.

**함수 인터페이스(Function interfaces)는** 함수 작성자가 자신의 커스텀 로직을 Foundry의 기본 기능과 통합할 수 있게 해 주며, 함수를 사용하는 애플리케이션과 함수 사이의 계약(contract)을 정의하는 강력한 방법을 제공합니다.

함수 인터페이스는 애플리케이션이나 사용자가 함수와 어떻게 상호작용해야 하는지를 정의합니다. 여기에는 함수의 입력, 출력, 오류가 포함됩니다. 다시 말해 함수 인터페이스는 함수의 시그니처(signature)를 기술하지만, 함수 인터페이스 자체는 함수가 아닙니다. 함수 인터페이스는 함수가 구현(implement)하도록 설계되어 있습니다.

일부 Foundry 애플리케이션은 어떤 인터페이스를 구현한 함수를 실행할 때, 알려진 입력, 출력, 오류를 바탕으로 특화된 동작을 제공하기 위해 함수 인터페이스를 사용합니다. 사용자는 특정 함수 인터페이스에 대한 자신만의 구현을 제공할 수 있고, 그래도 Foundry는 이 특화된 동작을 계속 제공할 수 있습니다. 특정 함수 인터페이스에 의존하는 Foundry 내 애플리케이션은 그 인터페이스를 구현한 모든 함수를 찾아낼(discover) 수 있습니다.

예를 들어 AIP Logic은 사용자가 자신의 LLM을 Logic 함수에 가져올 수 있도록 함수 인터페이스에 의존합니다. 구체적으로, AIP Logic의 [Use LLM](https://www.palantir.com/docs/foundry/logic/blocks/#use-llm) 블록에서는 Palantir가 제공하는 LLM이나 *등록된(registered)* LLM을 선택할 수 있습니다. 등록된 모델은 Foundry가 제공하는 함수 인터페이스(예: chat completion 함수 인터페이스)를 구현한, 사용자가 작성한 함수입니다. 이렇게 하면 AIP Logic은 chat completion의 구현으로 명시적으로 정의되어 있고, 일반적인 LLM의 시그니처를 가지며, AIP Logic이 적절히 처리할 수 있는 오류를 반환하는 함수를 찾아낼 수 있습니다. 앞으로는 사용자가 제공한 chat completion 구현을 Pipeline Builder나 Model Catalog 같은 플랫폼의 다른 부분에서도 사용할 수 있게 될 예정입니다.

[registered models 기능으로 LLM을 등록하는 방법을 알아보세요.](https://www.palantir.com/docs/foundry/aip/bring-your-own-model/) 함수 인터페이스를 사용하는 레거시 방법은 [함수 인터페이스로 LLM 등록하기 \[Legacy\]](https://www.palantir.com/docs/foundry/aip/chat-completion-function-interface-quickstart/)를 참고하세요.

**설명**: 프로그래밍 언어의 인터페이스(예: Java의 `interface`, TypeScript의 `interface`)를 떠올리면 됩니다. 인터페이스에는 메서드 이름과 매개변수 타입, 반환 타입만 있고 본문은 없습니다. 클래스가 그 인터페이스를 구현하면, 인터페이스 타입만 아는 호출 코드도 그 클래스를 사용할 수 있습니다. 함수 인터페이스도 같은 원리입니다. AIP Logic은 "메시지 목록과 파라미터를 받아 응답을 반환한다"는 시그니처만 알고 있고, 사용자가 그 시그니처를 구현한 함수(예: 사내 LLM을 호출하는 함수)를 만들면 AIP Logic이 그 함수를 LLM 목록에 띄워 호출할 수 있습니다. 참고로 이 페이지의 "인터페이스"는 온톨로지의 객체 타입 인터페이스(Interfaces 섹션)와는 다른 개념입니다.

> **중간 요약**: 함수 인터페이스는 함수의 입력, 출력, 오류 시그니처를 정의하는 계약이며, 이를 구현한 함수는 AIP Logic 같은 애플리케이션이 자동으로 찾아 특화된 방식으로 실행할 수 있습니다.

<a id="palantir-provided-function-interfaces"></a>
## Palantir가 제공하는 함수 인터페이스 (Palantir-provided function interfaces)

다음은 현재 Palantir가 제공하는 함수 인터페이스 목록입니다.

* [`ChatCompletion`](#chatcompletion)

<a id="chatcompletion"></a>
### `ChatCompletion`

**설명(Description):**

* 여러 턴(multi-turn), 여러 사용자(multi-user)의 텍스트 대화 기록을 바탕으로 문맥에 맞는 텍스트 응답을 생성하는 함수입니다.
* 대화형 사용 사례에 적합합니다.

**Foundry 통합(Foundry integrations):**

* AIP Logic의 *Use LLM* 보드(board).
* Pipeline Builder 지원 예정.

**문서(Documentation):**

* [**함수 인터페이스로 LLM 등록하기 \[Legacy\]**](https://www.palantir.com/docs/foundry/aip/chat-completion-function-interface-quickstart/)

> **중간 요약**: 현재 Palantir가 제공하는 함수 인터페이스는 대화 기록을 받아 응답을 생성하는 `ChatCompletion` 하나이며, AIP Logic의 Use LLM 보드와 통합됩니다.

<a id="type-customization"></a>
## 타입 커스터마이징 (Type customization)

더 많은 유연성을 위해, 함수 인터페이스를 구현할 때 제공된 타입만 사용해야 하는 것은 아닙니다. 경우에 따라 자신만의 [커스텀 타입](../04_types-reference.md#structcustom-type)을 만들고 싶을 수 있습니다. 함수가 함수 인터페이스에 정의된 함수와 [호환(compatible) ↗](https://www.typescriptlang.org/docs/handbook/type-compatibility.html#comparing-two-functions)되기만 하면, 컴파일러가 그 함수를 받아들이고 정상적으로 게시(publish)됩니다. 함수 인터페이스가 모든 필드가 선택적(optional)인 입력 타입을 정의한 경우, 타입을 커스터마이징할 때 공통 선택적 필드를 최소 하나는 공유해야 합니다.

```typescript
...
interface CustomParams extends GenericCompletionParams {
   modelSpecificParam?: string
}
...

// 유효한 구현
@ChatCompletion()
public async myRegisteredModel(
    messages: FunctionsGenericChatCompletionRequestMessages,
    params: CustomParams
): Promise<FunctionsGenericChatCompletionResponse> {
  ...
}
```

**설명**: `CustomParams`는 인터페이스가 정한 `GenericCompletionParams`를 상속(`extends`)하고 모델 전용 필드 `modelSpecificParam`을 하나 더 붙인 타입입니다. `@ChatCompletion()` 데코레이터는 이 메서드가 `ChatCompletion` 인터페이스의 구현이라고 표시합니다. 입력은 대화 메시지 목록(`messages`)과 파라미터(`params`)이고, 출력은 chat completion 응답 객체를 담은 `Promise`입니다. 기존 필드를 모두 유지한 채 필드를 추가했기 때문에 TypeScript의 구조적 타입 호환 규칙상 원래 시그니처와 호환되며, 따라서 유효한 구현으로 인정됩니다.

> **중간 요약**: 인터페이스가 정한 타입을 확장한 커스텀 타입을 써도, 함수 시그니처가 인터페이스의 함수와 TypeScript 규칙상 호환되면 구현으로 인정됩니다.

<a id="troubleshooting"></a>
## 문제 해결 (Troubleshooting)

함수 인터페이스는 유연하게 설계되어 다양한 구현을 허용합니다. 그래도 함수 인터페이스를 구현하다 보면 오류를 만날 수 있습니다. 다음은 TypeScript 함수에서 구현을 커스터마이징할 때 이런 오류를 피하는 데 도움이 되는 팁입니다.

<a id="error-function-input-name-does-not-match-the-required-input-name-of-the-function-interface-at-the-specific-input-position"></a>
### 오류: `Function input name does not match the required input name of the function interface at the specific input position`

각 파라미터의 입력 이름은 각 입력 위치에서 함수 인터페이스에 정의된 입력 이름과 일치해야 합니다. 린팅(linting) 메시지가 안내하듯, 각 위치의 입력 이름이 함수 인터페이스에 선언된 입력 이름과 정확히 같은지 확인하세요.

![자주 발생하는 오류: 입력 이름이 일치하지 않음.](https://www.palantir.com/docs/resources/foundry/functions/byom-tutorial-common-errors-input-params-not-match.png)

**설명**: 일반적인 TypeScript에서는 매개변수 이름이 달라도 타입만 맞으면 호환되지만, 함수 인터페이스 구현에서는 이름까지 위치별로 맞아야 한다는 점이 다릅니다. 예를 들어 인터페이스의 첫 번째 입력이 `messages`라면 구현 함수의 첫 번째 매개변수도 `messages`여야 하고, `msgs`처럼 바꾸면 이 오류가 납니다.

<a id="error-function-is-missing-input-parameter-of-the-function-interface"></a>
### 오류: `Function is missing input parameter of the function interface`

이 오류는 구현 함수가 함수 인터페이스에 정의된 필수 입력을 모두 포함하지 않았을 때 발생합니다. 오류를 해결하려면 함수 인터페이스에 선언된 각 입력이 구현 함수에 포함되어 있는지 확인하세요.

![자주 발생하는 오류: 필수 입력이 포함되지 않음.](https://www.palantir.com/docs/resources/foundry/functions/byom-tutorial-common-errors-missing-input-params.png)

<a id="error-type-type1-is-not-assignable-to-type-type2"></a>
### 오류: `Type {type1} is not assignable to type {type2}`

컴파일러가 구현 함수를 인터페이스에 정의된 함수와 호환되지 않는다고 거부할 수 있습니다. 그런 경우 각 타입의 구조를 함수 인터페이스에 정의된 타입과 비교해서, 구현 함수가 함수 인터페이스에 정의된 함수와 [호환 ↗](https://www.typescriptlang.org/docs/handbook/type-compatibility.html#comparing-two-functions)되는지 확인하세요.

![자주 발생하는 오류: 함수가 Chat completion 데코레이터와 호환되지 않음.](https://www.palantir.com/docs/resources/foundry/functions/byom-tutorial-common-errors-function-not-compatible-with-interface.png)

> **중간 요약**: 구현 함수는 입력 이름을 위치별로 정확히 맞추고, 필수 입력을 모두 포함하며, 타입 구조가 인터페이스와 호환되어야 합니다.

## 정리

- 함수 인터페이스는 함수의 입력, 출력, 오류를 정하는 계약이며 그 자체는 함수가 아닙니다.
- 인터페이스를 구현한 함수는 AIP Logic 같은 애플리케이션이 찾아내 특화된 방식으로 실행합니다.
- 현재 Palantir가 제공하는 인터페이스는 `ChatCompletion`이며, 사용자 LLM을 AIP Logic의 Use LLM 블록에 연결하는 데 쓰입니다.
- 커스텀 타입을 써도 시그니처가 호환되면 구현으로 인정되며, 입력 이름, 필수 입력, 타입 호환성이 주요 오류 원인입니다.
