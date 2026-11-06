# TypeScript v1 함수에서 언어 모델 사용하기 (Language models in TypeScript v1 functions)

- 원문: https://www.palantir.com/docs/foundry/functions/language-models/
- 사이드바 위치: Define Ontologies > Functions > Models > Language models in TypeScript v1 functions

이 페이지는 TypeScript v1으로 작성하는 함수(function) 안에서 Palantir가 제공하는 대규모 언어 모델(LLM)을 불러와 사용하는 방법을 다룹니다. 모델을 코드 저장소로 가져오는(import) 절차, 가져온 모델의 메서드를 호출하는 함수 작성법, 임베딩 모델 사용법, 그리고 예전 방식(레거시) 언어 모델에서 새 방식으로 업그레이드하는 절차를 설명합니다. 함수 안에서 LLM을 호출할 수 있으면 감정 분석, 요약 같은 작업을 온톨로지 데이터와 결합해 플랫폼 전반에서 재사용할 수 있습니다.

**주의**: 이 페이지는 TypeScript v1 함수를 다룹니다. TypeScript v2나 Python은 [TypeScript v2 및 Python 함수에서 언어 모델 사용하기](03_language-models-python-tsv2.md)를 참고하세요. Ontology SDK와 구성 가능한 리소스 요청(configurable resource requests)을 사용하려면 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)하세요.

Palantir는 함수 안에서 사용할 수 있는 언어 모델 집합을 제공합니다. [Palantir 제공 LLM에 대해 더 읽어 보세요](https://www.palantir.com/docs/foundry/aip/supported-llms/).

**설명**: 여기서 "함수"는 Foundry의 Functions 기능으로 작성해 게시(publish)하는 서버 측 코드 단위입니다. 게시된 함수는 Workshop 같은 애플리케이션이나 액션에서 호출할 수 있습니다. 이 페이지의 핵심은 그 함수 코드 안에서 외부 API 키를 직접 다루지 않고, Foundry가 제공하는 모델 객체(예: `Gpt41`)의 메서드를 호출해 LLM을 쓴다는 점입니다.

<a id="prerequisites"></a>
## 사전 요구 사항 (Prerequisites)

Palantir 제공 언어 모델을 사용하려면 다음을 확인하세요.

* [사용 중인 환경(enrollment)에서 AIP가 활성화되어 있어야 합니다](https://www.palantir.com/docs/foundry/aip/enable-aip-features/).
* [AIP 빌더 기능(AIP builder capabilities)](https://www.palantir.com/docs/foundry/aip/aip-features/#aip-applications-and-builder-capabilities)을 사용할 권한이 있어야 합니다.

**설명**: enrollment는 한 고객 조직에 배정된 Foundry 환경 단위를 가리킵니다. AIP는 Palantir의 AI 기능 묶음 이름이며, 관리자가 환경 단위로 켜야 쓸 수 있습니다.

<a id="import-a-language-model"></a>
## 언어 모델 가져오기 (Import a language model)

언어 모델을 사용하려면 먼저 함수를 작성하는 코드 저장소(code repository)로 해당 모델을 가져와야 합니다. 다음 단계를 따르세요.

1. **Model Imports** 사이드 패널로 이동해 열면, 이미 가져온 모든 모델을 볼 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/v3-lms-functions-import-sidebar.png" alt="모델 가져오기 사이드바." width="400" />

2. 새 언어 모델을 가져오려면 **Resource Imports** 패널 오른쪽 위에서 **Add**를 선택한 다음 **Models**를 선택합니다. 그러면 사용할 수 있는 Palantir 제공 모델을 볼 수 있는 새 창이 열립니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/v3-lms-functions-import-dialog.png" alt="Palantir 제공 LLM 몇 개가 표시된 모델 가져오기 대화 상자." width="600" />

3. 이전에 Modeling Objectives 애플리케이션이나 직접 모델 배포(direct model deployment)로 만든 사용자 정의 모델을 볼 수 있는 탭도 표시됩니다. 이런 모델을 사용하는 방법은 [모델 기반 함수(functions on models)](01_functions-on-models.md) 문서에 더 자세히 나와 있습니다.

4. 가져올 모델을 고른 다음 **Confirm selection**을 선택해 저장소로 가져옵니다. Task runner가 `localDev` 작업을 실행해 이 모델들과 상호작용하기 위한 코드 바인딩(code bindings)을 생성합니다.

5. 언어 모델을 가져온 뒤 사이드바에서 모델을 선택하면 그 모델이 제공하는 기능을 자세히 볼 수 있습니다. 모델을 가져오고 함수를 작성하는 데 도움이 되는 코드 스니펫을 복사할 수도 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/v3-lms-functions-sidebar-detail.png" alt="사이드바의 모델 세부 정보." width="400" />

**설명**: 코드 바인딩이란 모델의 API를 TypeScript에서 바로 호출할 수 있도록 자동 생성된 클래스와 타입 정의입니다. 예를 들어 GPT-4.1을 가져오면 `Gpt41`이라는 이름으로 import할 수 있는 모듈이 생기고, 그 안의 메서드는 입력과 출력 타입이 정해져 있어 컴파일 시점에 잘못된 인자를 잡아낼 수 있습니다.

> **중간 요약**: 언어 모델은 코드 저장소의 Resource Imports 패널에서 Add, Models 순으로 골라 가져옵니다. 가져오면 `localDev` 작업이 타입이 지정된 코드 바인딩을 생성합니다.

<a id="write-a-function-that-uses-a-language-model"></a>
## 언어 모델을 사용하는 함수 작성하기 (Write a function that uses a language model)

이제 가져온 언어 모델을 사용하는 함수를 작성할 수 있습니다. 이 예시에서는 GPT-4.1을 가져왔다고 가정합니다.

먼저 파일에 다음 import 문을 추가합니다.

```typescript
import { Function, Uses } from "@foundry/functions-api";
import { Gpt41 } from "@foundry/languagemodelservice/models";
```

각 언어 모델에는 입력과 출력이 강하게 타입 지정된(strongly typed) 메서드가 생성되어 있습니다. 예를 들어 GPT-4.1 모델은 모델과 상호작용하는 여러 API로 `createChatCompletion`, `createChatVisionCompletion`, `createChatCompletionStreamed`를 제공합니다. 기능 목록은 가져온 모델의 이후 버전에서 늘어날 수 있습니다.

Foundry는 게시된 함수가 어떤 모델 메서드를 호출하는지 알아야 합니다. 대부분의 호출은 정적 분석(static analysis)으로 자동 감지됩니다. 정적 분석이 놓친 호출이 있으면 런타임 오류가 발생하며, 오류 메시지는 `@Uses` 데코레이터를 추가하라고 안내합니다. `@Uses` 데코레이터는 자동으로 감지된 사용 내역을 보완합니다. 아래 예시와 모델 세부 정보 패널의 코드 스니펫처럼, 모델 메서드는 데코레이터의 `queries` 키 아래에 선언합니다.

다음 예시에서는 제공된 GPT-4.1 모델로 사용자가 입력한 텍스트나 이미지에 대해 간단한 감정 분석(sentiment analysis)을 실행합니다. 함수는 텍스트를 "Good", "Bad", "Uncertain" 중 하나로 분류합니다.

```typescript
const SYSTEM_PROMPT =
    "Provide an estimation of the sentiment the text the user has provided. \
You may respond with either Good, Bad, or Uncertain. Only choose Good or Bad if you are overwhelmingly \
sure that the text is either good or bad. If the text is neutral, or you are unable to determine, choose Uncertain.";

export class MyFunctions {
    @Function()
    @Uses({ queries: [Gpt41.createChatCompletion] })
    public async llmFunction_createChatCompletion(userPrompt: string): Promise<string | undefined> {
        const response = await Gpt41.createChatCompletion({
            messages: [
                { role: "SYSTEM", content: SYSTEM_PROMPT },
                { role: "USER", content: userPrompt },
            ],
            params: {
                temperature: 0,
            },
        });
        return response.type === "ok" ? response.value.completion : "error";
    }
}
```

(원문에는 같은 클래스 안에 `createChatVisionCompletion`으로 텍스트와 Base64로 인코딩한 PNG 이미지를 함께 보내는 `llmFunction_createChatVisionCompletion` 메서드 예제가 더 있습니다. 메시지의 `content`를 `{ type: "text", ... }`와 `{ type: "genericMedia", genericMedia: { mimeType: "IMAGE_PNG", content: ... } }` 항목의 배열로 구성한다는 점만 다릅니다.)

**설명**: 이 함수는 문자열 `userPrompt`를 입력받아 분류 결과 문자열을 반환합니다. 핵심 줄은 다음과 같습니다.
- `@Function()`: 이 메서드를 Foundry 함수로 게시할 대상으로 표시합니다.
- `@Uses({ queries: [Gpt41.createChatCompletion] })`: 이 함수가 GPT-4.1의 `createChatCompletion`을 호출한다고 명시적으로 선언합니다.
- `messages` 배열: `SYSTEM` 역할 메시지로 모델의 지시사항(분류 규칙)을, `USER` 역할 메시지로 실제 분석할 텍스트를 보냅니다.
- `temperature: 0`: 출력의 무작위성을 최소화해 같은 입력에 대해 최대한 같은 답을 얻도록 합니다.
- `response.type === "ok"`: 응답은 성공(`ok`) 또는 실패를 나타내는 타입을 가진 값입니다. 성공이면 `response.value.completion`(모델이 생성한 텍스트)을, 아니면 `"error"`를 반환합니다.

이렇게 만든 함수는 플랫폼 전반에서 사용할 수 있습니다.

[`@Uses` 데코레이터](../09_language-agnostic-features/02_query-functions.md#call-a-query-function)는 가져온 모델에도 적용됩니다. 이런 호출은 `@Uses({ queries: [Gpt41.createChatCompletion] })`처럼 `queries` 아래에 선언합니다.

> **중간 요약**: 가져온 모델은 `Gpt41.createChatCompletion` 같은 타입 지정 메서드로 호출합니다. Foundry가 호출 내역을 알 수 있도록 정적 분석이 놓친 호출은 `@Uses({ queries: [...] })`로 선언합니다.

<a id="embeddings"></a>
## 임베딩 (Embeddings)

생성형 언어 모델과 함께, Palantir는 임베딩(embedding)을 생성하는 데 쓸 수 있는 모델도 제공합니다. 간단한 예는 다음과 같습니다.

```typescript
@Function()
@Uses({ queries: [Textembedding3large.createEmbeddings] })
public async llmFunction_embeddings(inputs: string[]): Promise<Double[][]> {
    const response = await Textembedding3large.createEmbeddings({ inputs });
    return response.type === "ok" ? response.value.embeddings : [[]];
}
```

**설명**: 이 함수는 문자열 배열을 입력받아 각 문자열에 대한 실수 벡터(`Double[]`)의 배열을 반환합니다. 예를 들어 입력이 `["late flight", "delayed departure"]`이면 출력은 길이가 같은 벡터 2개입니다. 임베딩은 텍스트의 의미를 고정 길이의 숫자 벡터로 표현한 것으로, 의미가 비슷한 문장일수록 두 벡터 사이의 거리(예: 코사인 유사도 기준)가 가깝게 나옵니다. 실패하면 `[[]]`(빈 벡터 하나를 담은 배열)를 반환합니다.

이 기능은 주로 [시맨틱 검색(semantic search)](../../../03_ontology-search/01_semantic-search/05_using-palantir-provided-models-to-create-a-semantic-search-workflow.md) 워크플로에 사용됩니다.

<a id="upgrade-from-legacy-language-models-within-functions"></a>
## 함수 안의 레거시 언어 모델에서 업그레이드하기 (Upgrade from legacy language models within functions)

함수 안의 업데이트된 언어 모델은 비전(vision)과 스트리밍(streaming) 지원 강화 같은 더 발전된 기능을 제공합니다. 최신 AIP 기능을 활용하려면 저장소를 업그레이드할 것을 강력히 권장합니다. [레거시 언어 모델](05_language-models-legacy.md)을 가져온 적 없는 새 저장소에서 시작한다면 아래 단계는 건너뛰어도 됩니다.

**주의**: 다음 절차를 진행하면 코드 문법이 바뀌므로 코드 저장소에서 컴파일 오류가 발생합니다. 업데이트된 각 모델의 사이드바에 있는 코드 스니펫을 참고해 코드를 수정하세요.

1. 기존에 가져온 [레거시 언어 모델](05_language-models-legacy.md)이 있으면 사이드바에 업그레이드를 알리는 경고 아이콘이 나타납니다. **Select imports**를 선택해 모델 가져오기 대화 상자를 엽니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/v3-lms-functions-migration-sidebar.png" alt="사이드바의 모델 가져오기 경고." width="400" />

2. 모델 가져오기 대화 상자에서 **Fix**를 선택해 지원 중단된(deprecated) 레거시 언어 모델을 제거합니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/v3-lms-functions-migration-dialog-warning.png" alt="경고가 표시된 모델 가져오기 대화 상자." width="400" />

3. 모델을 다시 선택해 업데이트된 언어 모델 버전으로 마이그레이션합니다. 이 버전에서 지원하는 추가 기능은 대화 상자 가운데의 세부 정보 패널에서 볼 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/v3-lms-functions-migration-dialog-selected.png" alt="제거된 모델이 표시된 모델 가져오기 대화 상자." width="400" />

4. 이제 사이드바에서 업데이트된 모델 가져오기 목록을 볼 수 있습니다. 모델을 선택하면 추가 기능을 활용하도록 코드를 수정하는 데 도움이 되는 코드 스니펫이 담긴 세부 정보 패널이 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/v3-lms-functions-sidebar-detail.png" alt="사이드바의 모델 세부 정보와 코드 스니펫." width="400" />

**설명**: 컴파일 오류가 생기는 이유는 레거시 모델과 새 모델의 import 경로와 메서드 입출력 형태가 다르기 때문입니다. 예를 들어 레거시 방식은 `@foundry/models-api/language-models`에서 `GPT_4o`를 가져오고 응답을 `gptResponse.choices[0].message.content`로 읽지만, 새 방식은 `@foundry/languagemodelservice/models`에서 가져오고 `response.value.completion`으로 읽습니다. 기존 코드를 이 새 형태에 맞게 고쳐야 컴파일이 다시 통과합니다.

> **중간 요약**: 업데이트된 모델은 비전과 스트리밍을 더 잘 지원하므로 업그레이드가 권장됩니다. 사이드바 경고에서 Select imports, Fix, 모델 재선택 순으로 진행하고, 바뀐 문법에 맞게 코드를 고칩니다.

<a id="performance-considerations"></a>
## 성능 고려 사항 (Performance considerations)

일부 모델에는 일정 기간 동안 전달할 수 있는 토큰 수를 제한하는 속도 제한(rate limit)이 적용될 수 있습니다. 이 제한은 함수에 적용되는 일반적인 제한과 함께 적용됩니다.

***

참고: AIP 기능의 제공 여부는 바뀔 수 있으며 고객마다 다를 수 있습니다.

## 정리

- 이 페이지는 TypeScript v1 함수 전용이며, TypeScript v2와 Python은 별도 문서를 따릅니다.
- 사용 전에 AIP 활성화와 AIP 빌더 권한이 필요합니다.
- Resource Imports 패널에서 모델을 가져오면 `Gpt41` 같은 타입 지정 코드 바인딩이 생성되고, `createChatCompletion` 등의 메서드로 호출합니다.
- 정적 분석이 놓친 모델 호출은 `@Uses({ queries: [...] })`로 선언합니다.
- 임베딩 모델은 시맨틱 검색에 주로 쓰이며, 레거시 모델은 사이드바 안내에 따라 업그레이드하되 코드 수정이 필요합니다.
