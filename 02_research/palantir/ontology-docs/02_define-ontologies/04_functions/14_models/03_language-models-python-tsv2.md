# TypeScript v2와 Python 함수에서 언어 모델 사용하기 (Language models in TypeScript v2 and Python functions)

- 원문: https://www.palantir.com/docs/foundry/functions/language-models-python-tsv2/
- 사이드바 위치: Define Ontologies > Functions > Models > Language models in TypeScript v2 and Python functions

이 페이지는 TypeScript v2 또는 Python으로 작성한 함수(function) 안에서 Palantir가 제공하는 언어 모델(LLM)을 호출하는 방법을 설명합니다. 모델을 코드 저장소에 가져오고(import) 별칭(alias)을 붙이는 절차와, 프록시 엔드포인트를 통해 모델을 호출하는 예제 코드를 다룹니다.

Palantir는 함수 안에서 사용할 수 있는 언어 모델 세트를 제공합니다. [Palantir가 제공하는 LLM에 대해 더 알아보세요](https://www.palantir.com/docs/foundry/aip/supported-llms/).

<a id="prerequisites"></a>
## 사전 요구 사항 (Prerequisites)

Palantir가 제공하는 언어 모델을 사용하려면 다음을 확인하세요.

* [사용 중인 enrollment에서 AIP가 활성화되어 있어야 합니다](https://www.palantir.com/docs/foundry/aip/enable-aip-features/).
* [AIP 빌더 기능(AIP builder capabilities)](https://www.palantir.com/docs/foundry/aip/aip-features/#aip-applications-and-builder-capabilities)을 사용할 권한이 있어야 합니다.

**설명**: enrollment는 한 조직이 사용하는 Foundry 환경 단위를 가리키는 Palantir 용어입니다. 즉 조직 차원에서 AIP 기능을 켜 두어야 하고, 사용자 개인에게도 해당 기능을 쓸 권한이 있어야 합니다.

<a id="import-a-language-model"></a>
## 언어 모델 가져오기 (Import a language model)

언어 모델을 사용하려면 먼저 아래 단계에 따라 해당 모델을 함수 코드 저장소(code repository)로 가져와야 합니다.

1. **Resource imports** 패널에서 **Platform SDK** 탭을 엽니다.

![TypeScript v2 저장소에서 Platform SDK 리소스에 접근하는 탭.](https://www.palantir.com/docs/resources/foundry/functions/platform-sdk-tab.png)

2. 새 언어 모델을 가져오려면 오른쪽 위에서 **Add > Models**를 선택합니다. Palantir가 제공하는 모델과 등록된(registered) 모델을 볼 수 있는 창이 열립니다.

![TypeScript v2 저장소의 모델 가져오기 대화 상자.](https://www.palantir.com/docs/resources/foundry/functions/models-v3-import-dialog.png)

3. 가져올 모델을 선택한 뒤 **Confirm selection**을 선택합니다. 선택한 각 모델의 별칭(alias)을 설정할 수 있는 구성 대화 상자가 열립니다. 별칭 옆의 펜 아이콘을 선택해 수정하거나, 기본값을 그대로 둘 수 있습니다.

**주의**: 모든 모델에는 별칭이 있어야 하며, 별칭은 저장소 안에서 고유해야 합니다.

![가져올 모델을 고른 뒤 모델 별칭을 구성하는 화면.](https://www.palantir.com/docs/resources/foundry/functions/configure-models-aliases.png)

4. 가져온 모델은 **Resource imports** 사이드 패널의 **Platform SDK** 탭에 나타납니다. 별칭 옆의 펜 아이콘을 선택하면 어떤 별칭이든 그 자리에서 수정할 수 있습니다.

![모델 별칭을 그 자리에서 수정하는 화면.](https://www.palantir.com/docs/resources/foundry/functions/inline-models-aliases-edit.png)

**Platform SDK** 탭에서 [커스텀 별칭(custom aliases)](../15_aliases/01_custom-aliases.md)도 정의할 수 있습니다. 커스텀 별칭은 구성 파라미터, 기능 플래그(feature flag), 환경별 설정을 저장하며, 설치자가 Marketplace 설치 과정에서 이를 바꿀 수 있습니다.

**설명**: 별칭은 코드에서 모델을 가리킬 때 쓰는 이름입니다. Foundry의 리소스는 RID(Resource Identifier)라는 긴 고유 식별자로 구분되는데, 코드에 RID 문자열을 직접 적는 대신 `"my-gpt"` 같은 별칭을 쓰면 코드가 읽기 쉬워지고, 다른 환경에 설치할 때 별칭이 가리키는 실제 모델만 바꿀 수 있습니다.

> **중간 요약**: Platform SDK 탭에서 **Add > Models**로 모델을 가져오고, 저장소 안에서 고유한 별칭을 붙입니다. 코드는 이 별칭으로 모델을 참조합니다.

<a id="write-a-function-that-uses-a-language-model"></a>
## 언어 모델을 사용하는 함수 작성하기 (Write a function that uses a language model)

TypeScript v2와 Python 함수의 언어 모델은 프록시 엔드포인트(proxy endpoint)를 사용해 모델과 상호작용합니다. 다음 예제는 [OpenAI chat completion 프록시 엔드포인트](https://www.palantir.com/docs/foundry/api/v2/llm-apis/models/openai-chat-completions-proxy/)를 사용합니다. 문서 사이드 패널에서 다른 제공자(provider)를 선택할 수 있습니다.

아래 예제의 `openai` 같은 서드파티 라이브러리는 미리 설치되어 있지 않습니다. 왼쪽 사이드 패널의 **Libraries** 섹션에서 설치하세요.

가져온 언어 모델을 함수에서 사용하려면 먼저 필요한 유틸리티를 import합니다.

```typescript tab="TypeScript v2"
import { PlatformClient } from "@osdk/client";
import OpenAI from "openai";
import { Aliases } from "@osdk/functions";
import { getFoundryToken, getOpenAiBaseUrl, createFetch } from "@osdk/language-models";
```

(원문에는 같은 import를 Python으로 작성한 버전도 있습니다. `openai`의 `OpenAI`, `functions.api`의 `function`, `functions.aliases`의 `model`, `foundry_sdk.v2.language_models`의 `get_openai_base_url`, `get_foundry_token`, `get_http_client`를 가져옵니다.)

**설명**: `getFoundryToken`은 Foundry 인증 토큰을, `getOpenAiBaseUrl`은 Foundry의 OpenAI 호환 프록시 주소를, `createFetch`는 Foundry 환경에 맞춘 HTTP 요청 함수를 돌려줍니다. `Aliases`는 앞에서 정한 모델 별칭을 조회할 때 씁니다.

구성해 둔 모델 별칭과 import한 유틸리티를 사용해 모델을 직접 호출합니다. 이 방식은 TypeScript v1 워크플로보다 단순하며, 리소스 식별자를 하드코딩할 필요를 줄여 줍니다.

```typescript tab="TypeScript v2"
export default async function callOpenAi(client: PlatformClient, prompt: string): Promise<string> {
    const oaiClient = new OpenAI({
        apiKey: await getFoundryToken(client),
        baseURL: getOpenAiBaseUrl(client),
        fetch: createFetch(client),
    });

    const completion = await oaiClient.chat.completions.create({
        model: Aliases.model("{MY_ALIAS}").rid,
        messages: [
            { role: 'user', content: prompt },
        ],
        max_completion_tokens: 200,
    });

    return completion.choices[0]?.message.content ?? "";
}
```

(원문에는 같은 동작을 하는 Python 버전 `get_chat_completion(prompt: str) -> str` 함수도 있습니다. `@function` 데코레이터를 붙이고 `OpenAI(api_key=get_foundry_token(preview=True), base_url=get_openai_base_url(preview=True), http_client=get_http_client(preview=True))`로 클라이언트를 만든 뒤 `model("{MY_ALIAS}").rid`로 모델을 지정합니다.)

**설명**: 이 함수는 입력으로 문자열 `prompt`를 받고, 모델의 답변 문자열을 반환합니다. 핵심은 두 부분입니다. 첫째, `new OpenAI({...})`에서 OpenAI 공식 라이브러리를 쓰되 API 키 자리에 Foundry 토큰을, 주소 자리에 Foundry 프록시 주소를 넣습니다. 그래서 요청은 OpenAI 서버로 직접 가지 않고 Foundry를 거쳐 전달됩니다. 둘째, `model: Aliases.model("{MY_ALIAS}").rid`에서 별칭으로 모델의 RID를 조회해 모델 이름으로 넘깁니다. `{MY_ALIAS}`는 앞 단계에서 정한 별칭으로 바꿔 써야 합니다. 응답에서 `choices[0].message.content`를 꺼내고, 값이 없으면 빈 문자열을 반환합니다.

> **중간 요약**: 프록시 엔드포인트와 OpenAI 라이브러리를 이용해, Foundry 토큰과 프록시 주소로 클라이언트를 만들고 별칭으로 조회한 모델 RID를 넘겨 호출합니다.

## 정리

- AIP가 활성화되어 있고 AIP 빌더 권한이 있어야 Palantir 제공 언어 모델을 쓸 수 있습니다.
- **Resource imports > Platform SDK** 탭에서 모델을 가져오고 저장소 안에서 고유한 별칭을 붙입니다.
- TypeScript v2와 Python 함수는 프록시 엔드포인트를 통해 모델을 호출하며, `openai` 같은 라이브러리는 직접 설치해야 합니다.
- 코드에서는 별칭으로 모델 RID를 조회하므로 리소스 식별자를 하드코딩하지 않아도 됩니다.
