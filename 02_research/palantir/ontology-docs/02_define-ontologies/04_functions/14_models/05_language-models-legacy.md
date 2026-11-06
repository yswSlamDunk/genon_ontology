# 함수 안의 레거시 언어 모델 (Legacy language models in functions)

- 원문: https://www.palantir.com/docs/foundry/functions/language-models-legacy/
- 사이드바 위치: Define Ontologies > Functions > Models > Legacy language models in functions

이 페이지는 TypeScript v1 함수(function)에서 언어 모델을 사용하던 예전(레거시) 방식을 설명합니다. 모델을 가져오는 절차와 `@foundry/models-api/language-models` 패키지를 통해 모델을 호출하는 예제를 다룹니다. 새로 시작하는 경우에는 업데이트된 방식을 써야 하지만, 기존 저장소의 코드를 읽거나 업그레이드할 때 이 문서의 형태를 알아 두면 도움이 됩니다.

**주의**: 레거시(Legacy). 이 페이지는 함수 안의 **레거시** 언어 모델을 다룹니다. TypeScript v2와 Python은 [프록시 엔드포인트와 모델 별칭(model alias)을 사용하는 워크플로](03_language-models-python-tsv2.md)를 참고하세요. 업데이트된 [TypeScript v1 언어 모델](04_language-models.md)은 비전(vision)과 스트리밍(streaming) 같은 기능을 지원합니다. 업데이트된 TypeScript v1 모델을 사용하려면 [업그레이드 안내](04_language-models.md#upgrade-from-legacy-language-models-within-functions)를 따르세요.

Palantir는 함수 안에서 사용할 수 있는 언어 모델 집합을 제공합니다. [Palantir 제공 LLM에 대해 더 읽어 보세요](https://www.palantir.com/docs/foundry/aip/supported-llms/).

<a id="prerequisites"></a>
## 사전 요구 사항 (Prerequisites)

Palantir 제공 언어 모델을 사용하려면 다음을 확인하세요.

* [사용 중인 환경(enrollment)에서 AIP가 활성화되어 있어야 합니다](https://www.palantir.com/docs/foundry/aip/enable-aip-features/).
* [AIP 빌더 기능(AIP builder capabilities)](https://www.palantir.com/docs/foundry/aip/aip-features/#aip-applications-and-builder-capabilities)을 사용할 권한이 있어야 합니다.

<a id="import-a-language-model"></a>
## 언어 모델 가져오기 (Import a language model)

언어 모델을 사용하려면 먼저 함수를 작성하는 코드 저장소로 해당 모델을 가져와야 합니다. 다음 단계를 따르세요.

1. **Model Imports** 사이드 패널로 이동해 열면, 이미 가져온 모든 모델을 볼 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/language-model-import-sidebar.png" alt="모델 가져오기 사이드바." width="400" />

2. 새 언어 모델을 가져오려면 **Resource Imports** 패널 오른쪽 위에서 **Add**를 선택하고 **Models**를 선택합니다. 그러면 사용할 수 있는 Palantir 제공 모델을 볼 수 있는 새 창이 열립니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/language-model-import-dialog.png" alt="Palantir 제공 LLM 몇 개가 표시된 모델 가져오기 대화 상자." width="600" />

3. 이전에 Modeling Objectives 앱이나 직접 모델 배포(direct model deployment)로 만든 사용자 정의 모델을 볼 수 있는 탭도 표시됩니다. 이런 모델을 사용하는 방법은 [모델 기반 함수(functions on models)](01_functions-on-models.md) 문서에 더 자세히 나와 있습니다.

4. 가져올 모델을 선택한 다음 **Confirm selection**을 선택해 저장소로 가져옵니다. Task runner가 `localDev` 작업을 실행해 이 모델들과 상호작용하기 위한 코드 바인딩(code bindings)을 생성합니다.

5. 언어 모델을 가져온 뒤에는 다음 import 문을 추가해 저장소에서 사용할 수 있습니다. GPT\_4o는 저장소로 가져온 언어 모델의 이름으로 바꾸세요.

```typescript
import { GPT_4o } from "@foundry/models-api/language-models"
```

> **중간 요약**: 레거시 방식도 Resource Imports 패널에서 모델을 가져오는 절차는 같지만, 코드에서는 `@foundry/models-api/language-models` 경로에서 `GPT_4o` 같은 이름으로 모델을 import합니다.

<a id="writing-a-function-that-uses-a-language-model"></a>
## 언어 모델을 사용하는 함수 작성하기 (Writing a function that uses a language model)

이제 가져온 언어 모델을 사용하는 함수를 작성할 수 있습니다. 이 예시에서는 위에서 설명한 대로 GPT\_4o를 가져왔다고 가정합니다.

먼저 파일에 다음 import 문을 추가합니다.

```typescript
import { GPT_4o } from "@foundry/models-api/language-models"
```

각 언어 모델에는 입력과 출력이 강하게 타입 지정된(strongly typed) 메서드가 생성되어 있습니다. 예를 들어 GPT\_4o 모델은 `createChatCompletion` 메서드를 제공합니다. 이 메서드로 메시지 집합과 함께 temperature나 최대 토큰 수처럼 모델 동작을 바꾸는 추가 파라미터를 전달할 수 있습니다.

다음 예시에서는 제공된 GPT\_4o 모델로 사용자가 입력한 텍스트에 대해 간단한 감정 분석(sentiment analysis)을 실행합니다. 함수는 텍스트를 "Good", "Bad", "Uncertain" 중 하나로 분류합니다.

```typescript
@Function()
public async sentimentAnalysis(userPrompt: string): Promise<string> {
    const systemPrompt = "Provide an estimation of the sentiment the text the user has provided. \
    You may respond with either Good, Bad, or Uncertain. Only choose Good or Bad if you are overwhelmingly \
    sure that the text is either good or bad. If the text is neutral, or you are unable to determine, choose Uncertain."

    const systemMessage = { role: "SYSTEM", contents: [{ text: systemPrompt }] };
    const userMessage = { role: "USER", contents: [{ text: userPrompt }] };
    const gptResponse = await GPT_4o.createChatCompletion({messages: [systemMessage, userMessage], params: { temperature: 0.7 } });
    return gptResponse.choices[0].message.content ?? "Uncertain";
}
```

**설명**: 이 함수는 문자열 `userPrompt`를 입력받아 "Good", "Bad", "Uncertain" 중 하나의 문자열을 반환합니다.
- `systemMessage`: 모델에게 분류 규칙을 알려 주는 `SYSTEM` 역할 메시지입니다. 레거시 방식에서는 내용이 `contents: [{ text: ... }]`처럼 배열 형태입니다.
- `userMessage`: 실제 분석할 텍스트를 담은 `USER` 역할 메시지입니다.
- `params: { temperature: 0.7 }`: 출력의 무작위성 정도를 정합니다. 값이 클수록 답이 다양해집니다.
- `gptResponse.choices[0].message.content ?? "Uncertain"`: 첫 번째 응답 후보의 텍스트를 반환하고, 값이 없으면(`null` 또는 `undefined`) `"Uncertain"`을 반환합니다. `??`는 TypeScript의 null 병합 연산자입니다.

이렇게 만든 함수는 플랫폼 전반에서 사용할 수 있습니다.

<a id="embeddings"></a>
## 임베딩 (Embeddings)

생성형 언어 모델과 함께, Palantir는 임베딩(embedding)을 생성하는 데 쓸 수 있는 모델도 제공합니다. 간단한 예는 다음과 같습니다.

```typescript
@Function()
public async generateEmbeddingsForText(inputs: string[]): Promise<Double[][]> {
    const response = await TextEmbeddingAda_002.createEmbeddings({ inputs });
    return response.embeddings;
}
```

**설명**: 문자열 배열을 입력받아 각 문자열을 숫자 벡터로 바꾼 결과의 배열(`Double[][]`)을 반환합니다. 업데이트된 방식과 달리 응답의 성공 여부(`type === "ok"`)를 확인하지 않고 `response.embeddings`를 바로 읽습니다.

이 기능은 주로 [시맨틱 검색(semantic search)](../../../03_ontology-search/01_semantic-search/05_using-palantir-provided-models-to-create-a-semantic-search-workflow.md) 워크플로에 사용됩니다.

> **중간 요약**: 레거시 방식에서는 `GPT_4o.createChatCompletion`의 응답을 `choices[0].message.content`로 읽고, 임베딩은 `TextEmbeddingAda_002.createEmbeddings`로 생성합니다.

<a id="performance-considerations"></a>
## 성능 고려 사항 (Performance considerations)

일부 모델에는 일정 기간 동안 전달할 수 있는 토큰 수를 제한하는 속도 제한(rate limit)이 적용될 수 있습니다. 이 제한은 함수에 적용되는 일반적인 제한과 함께 적용됩니다.

***

참고: AIP 기능의 제공 여부는 바뀔 수 있으며 고객마다 다를 수 있습니다.

## 정리

- 이 페이지는 TypeScript v1 함수의 레거시 언어 모델 사용법이며, 새 작업에는 업데이트된 방식이 권장됩니다.
- 모델 가져오기 절차는 Resource Imports 패널의 Add, Models, Confirm selection 순서로 동일합니다.
- 코드에서는 `@foundry/models-api/language-models`에서 모델을 import하고 `createChatCompletion`으로 호출합니다.
- 임베딩 모델은 시맨틱 검색에 쓰이며, 일부 모델에는 토큰 속도 제한이 있습니다.
