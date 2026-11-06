# 스트리밍 함수 (Streaming functions)

- 원문: https://www.palantir.com/docs/foundry/functions/streaming-functions/
- 사이드바 위치: Define Ontologies > Functions > Language-agnostic features > Streaming functions

이 페이지는 함수(function)의 실행 결과를 한 번에 돌려주지 않고 여러 조각(chunk)으로 나누어 차례로 흘려보내는 스트리밍 함수를 설명합니다. Python과 TypeScript v2에서 스트리밍 응답을 작성하는 문법, 언어 모델의 답변을 실시간으로 전달하는 예제, Ontology SDK에서 스트리밍 함수를 호출하는 방법을 다룹니다.

Python과 TypeScript v2 함수는 실행 결과를 조각 단위로 스트리밍할 수 있습니다. 이는 데이터가 시간에 걸쳐 차례로 준비될 때 유용하며, 결과를 사용하는 애플리케이션이 결과가 완성되기 전에 처리를 시작할 수 있게 해 줍니다.

<a id="write-a-function-with-a-streamed-response"></a>
## 스트리밍 응답을 반환하는 함수 작성하기 (Write a function with a streamed response)

응답을 스트리밍하려면 Python 함수는 반환 타입을 `Iterable[T]`로 지정하고, 값이 준비될 때마다 `yield` 키워드로 값을 내보내야 합니다. TypeScript에서는 `function` 키워드 뒤에 `*` 문자를 붙여 비동기 제너레이터(async generator) 함수를 선언하고, 반환 타입을 `AsyncIterable<T>`로 지정하고, 값이 준비될 때마다 `yield` 키워드로 값을 내보내야 합니다.

다음 예제는 함수가 정수 사이마다 1초씩 간격을 두고 정수 스트림을 반환하는 방법을 보여 줍니다.

```python tab="Python"
from functions.api import function
from typing import Iterable
import time

@function
def my_lazy_number_generator(n: int) -> Iterable[int]:
    for i in range(n):
        time.sleep(1)
        yield i
```

(원문에는 `async function*`과 `AsyncIterable<Integer>`로 같은 동작을 구현한 TypeScript v2 버전도 있습니다.)

**설명**: `yield`를 쓰는 함수는 제너레이터(generator)가 됩니다. `return`은 값을 하나 돌려주고 함수를 끝내지만, `yield`는 값을 하나 내보낸 뒤 그 자리에서 멈췄다가 다음 값을 요청받으면 이어서 실행합니다. 이 예제에서 `n = 3`이면 호출한 쪽은 1초 뒤 `0`, 다시 1초 뒤 `1`, 다시 1초 뒤 `2`를 받습니다. 일반 함수라면 3초를 기다린 뒤 `[0, 1, 2]`를 한꺼번에 받았을 것입니다.

스트리밍 응답을 반환하는 함수는 전체 출력을 생성하는 데 시간이 걸릴 수 있는 언어 모델을 다룰 때 유용합니다. 모델이 응답 조각을 생성할 때마다 그 조각을 `yield`하면, 응답이 완전히 끝날 때까지 막혀 있지 않는 실시간 경험을 제공할 수 있습니다. 함수에서 언어 모델을 호출하는 방법에 대한 자세한 내용은 [TypeScript v2와 Python 함수의 언어 모델](../14_models/03_language-models-python-tsv2.md)을 참조하십시오.

다음 예제는 `openai` SDK를 사용해 언어 모델을 호출하고, 요청에서 `stream` 플래그를 활성화해 응답을 스트리밍으로 돌려줍니다.

```typescript tab="TypeScript v2"
import { PlatformClient } from "@osdk/client";
import OpenAI from "openai";
import { Aliases } from "@osdk/functions";
import { getFoundryToken, getOpenAiBaseUrl, createFetch } from "@osdk/language-models";

export default async function* createChatCompletion(client: PlatformClient, prompt: string): AsyncIterable<string> {
    const oaiClient = new OpenAI({
        apiKey: await getFoundryToken(client),
        baseURL: getOpenAiBaseUrl(client),
        fetch: createFetch(client),
    });

    const stream = await oaiClient.chat.completions.create({
        model: Aliases.model("gpt55").rid,
        messages: [
            { role: 'user', content: prompt },
        ],
        stream: true
    });

    for await (const event of stream) {
        const content = event.choices[0]?.delta?.content;
        if (content) {
            yield content;
        }
    }
}
```

(원문에는 `get_foundry_token`, `get_openai_base_url`, `get_http_client`로 OpenAI 클라이언트를 구성하는 Python 버전도 있습니다.)

**설명**: 이 함수는 사용자의 `prompt`를 입력받아 언어 모델 답변을 문자열 조각으로 흘려보냅니다. OpenAI SDK 클라이언트를 만들 때 Foundry 토큰, Foundry가 제공하는 OpenAI 호환 주소, Foundry용 fetch를 넣어 주므로, 요청은 OpenAI 서버가 아니라 Foundry를 거쳐 모델로 전달됩니다. `stream: true`로 요청하면 모델이 단어 몇 개 분량씩 이벤트를 보내고, `for await` 루프가 각 이벤트의 `delta.content`(새로 생성된 텍스트 조각)를 꺼내 바로 `yield`합니다. 모델 이름은 `Aliases.model("gpt55")`처럼 별칭으로 지정합니다.

> **중간 요약**: Python은 `Iterable[T]`와 `yield`, TypeScript v2는 `async function*`, `AsyncIterable<T>`, `yield`로 스트리밍 함수를 작성합니다. 언어 모델 응답을 조각마다 바로 전달하는 데 특히 유용합니다.

<a id="call-streaming-functions-through-the-ontology-sdk"></a>
## Ontology SDK로 스트리밍 함수 호출하기 (Call streaming functions through the Ontology SDK)

스트리밍 함수를 태그하고 게시하면, React 애플리케이션, Workshop의 사용자 지정 위젯, 또는 다른 함수에서 [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/overview/)를 통해 실행할 수 있습니다.

**참고**: 베타(Beta). Ontology SDK를 통해 스트리밍 응답을 반환하는 함수를 실행하는 기능은 개발 단계 중 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다.

```typescript tab="TypeScript"
import { __EXPERIMENTAL__NOT_SUPPORTED_YET__executeStreamingFunction } from "@osdk/api/unstable";

const stream = client(__EXPERIMENTAL__NOT_SUPPORTED_YET__executeStreamingFunction).executeStreamingFunction(
    createChatCompletion,
    {
        prompt: "Where is Mount Everest?",
    }
);

for await (const text of stream) {
    // ...
}
```

(원문에는 `AllowBetaFeatures()` 블록 안에서 `client.ontology.queries.create_chat_completion_streaming(...)`을 호출하고 `for` 루프로 조각을 받는 Python 버전도 있습니다.)

**설명**: 호출하는 쪽은 실험 기능인 `executeStreamingFunction`에 함수(`createChatCompletion`)와 입력(`prompt`)을 넘겨 스트림을 받습니다. 그다음 `for await` 루프로 조각이 도착할 때마다 `text`를 처리합니다. 예를 들어 화면에 조각을 계속 이어 붙이면 사용자는 답변이 타이핑되듯 나타나는 것을 보게 됩니다. 함수 이름의 `__EXPERIMENTAL__NOT_SUPPORTED_YET__`는 아직 정식 지원되지 않는 베타 API라는 표시입니다.

> **중간 요약**: 게시한 스트리밍 함수는 React 앱, Workshop 사용자 지정 위젯, 다른 함수에서 Ontology SDK로 호출할 수 있으며, 이 기능은 현재 베타입니다.

## 정리

- Python과 TypeScript v2 함수는 결과를 조각 단위로 스트리밍할 수 있어, 소비하는 쪽이 결과 완성 전에 처리를 시작할 수 있습니다.
- Python은 `Iterable[T]` 반환 타입과 `yield`, TypeScript v2는 `async function*`, `AsyncIterable<T>`, `yield`를 사용합니다.
- 언어 모델 호출 시 `stream` 옵션을 켜고 생성되는 조각을 바로 `yield`하면 실시간 응답을 제공할 수 있습니다.
- 스트리밍 함수는 Ontology SDK로 호출할 수 있으며, 이 호출 기능은 베타 단계입니다.
