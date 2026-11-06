# Foundry platform SDK로 플랫폼 API 사용하기 (Use platform APIs with the Foundry platform SDK)

- 원문: https://www.palantir.com/docs/foundry/functions/platform-sdk/
- 사이드바 위치: Define Ontologies > Functions > Language-agnostic features > Use platform APIs with the Foundry platform SDK

이 페이지는 함수(function) 안에서 Foundry platform SDK를 사용해 온톨로지 밖의 Foundry 기능(관리, 스케줄과 빌드, 미디어 세트, 언어 모델 호출 등)을 호출하는 방법을 다룹니다. SDK를 설치하는 방법, 인증된 클라이언트를 준비하는 방법, 실제 호출 예제, 클라이언트가 가진 권한 범위(scope)를 설명합니다.

**설명**: SDK(Software Development Kit)는 어떤 플랫폼의 API를 프로그래밍 언어에서 함수 호출처럼 쓸 수 있게 감싼 라이브러리입니다. HTTP 요청을 직접 만들지 않고 `foundry_client.media_sets.MediaSet.read(...)`처럼 메서드를 호출하면, SDK가 내부에서 해당 REST API를 호출합니다. 온톨로지 객체를 다루는 Ontology SDK(OSDK)와 달리, platform SDK는 Foundry 플랫폼 전반의 API를 다룹니다.

Foundry API는 다양한 기능을 노출하며, 함수에서 [Foundry platform SDK](https://www.palantir.com/docs/foundry/api/v2/general/overview/sdks/#foundry-platform-software-development-kits) 라이브러리를 통해 이 기능을 활용할 수 있습니다. platform SDK를 사용해 관리(administrative)나 거버넌스 워크플로를 위한 함수를 만들고, 스케줄과 빌드와 상호작용하고, 미디어 세트(media set)에 접근하는 등의 일을 할 수 있습니다.

**주의**: TypeScript v1 함수에서는 일급(first-class) 인증이 지원되지 않습니다. 이런 워크플로에는 Python 함수와 TypeScript v2 함수를 사용할 것을 권장합니다.

<a id="install-the-sdk"></a>
## SDK 설치하기 (Install the SDK)

Foundry platform SDK를 설치하려면 코드 저장소의 **Libraries** 사이드 패널로 이동해 SDK 이름을 검색합니다. Python은 `foundry-platform-sdk`, TypeScript는 `@osdk/foundry`입니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/platform-sdk-lib-panel-py.png" alt="Python platform SDK를 검색하는 Libraries 검색 패널." width="400" />

<img src="https://www.palantir.com/docs/resources/foundry/functions/platform-sdk-lib-panel-ts.png" alt="TypeScript platform SDK를 검색하는 Libraries 검색 패널." width="400" />

<a id="python-version-compatibility"></a>
### Python 버전 호환성 (Python version compatibility)

Python `foundry-platform-sdk`는 Python 3.9 이상이 필요합니다. Python 3.14 지원은 `foundry-platform-sdk` 버전 1.93.0부터 시작됩니다. 이전 SDK 버전은 Python 3.14에서 `typing` 모듈 오류를 반환할 수 있습니다. 이 오류를 해결하려면 버전 1.93.0 이상으로 업그레이드하십시오. 또는 Python 3.11, 3.12, 3.13을 사용하십시오.

<a id="initialize-your-client"></a>
## 클라이언트 초기화하기 (Initialize your client)

함수가 Foundry API와 상호작용하려면 인증이 필요합니다. 이 과정에서는 인증된 "클라이언트"를 인스턴스화하고, 그 클라이언트를 통해 SDK로 Foundry API에 요청을 보냅니다. TypeScript v2 저장소에서는 이를 위해 `@osdk/client` 라이브러리가 필요하며, 이 라이브러리는 미리 설치되어 있어야 합니다. 초록색 핀 표시를 찾아 이를 확인할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/platform-sdk-lib-panel-client-ts.png" alt="TypeScript용 인증 라이브러리." width="400" />

**설명**: 클라이언트는 "누가, 어떤 권한으로" 요청하는지에 대한 인증 정보를 담고 있는 객체입니다. API를 호출할 때마다 이 객체를 넘기면 SDK가 요청에 인증 토큰을 붙여 보냅니다.

> **중간 요약**: platform SDK는 Libraries 패널에서 `foundry-platform-sdk`(Python) 또는 `@osdk/foundry`(TypeScript)로 설치합니다. API를 호출하려면 인증된 클라이언트가 필요하며, TypeScript v2에서는 `@osdk/client`가 이를 담당합니다.

<a id="use-platform-apis"></a>
## 플랫폼 API 사용하기 (Use platform APIs)

함수가 인증되면 Foundry API를 사용하기 시작할 수 있습니다. 아래 예제는 Python과 TypeScript에서 언어 모델을 호출하거나 미디어 세트를 조회하는 방법을 보여 줍니다.

```typescript tab="TypeScript v2"
import {
    Client, // 함수가 온톨로지와 상호작용한다면 Client를 사용합니다
    PlatformClient // 함수가 온톨로지와 상호작용하지 않는다면 PlatformClient를 사용합니다
} from "@osdk/client";
import { Functions } from "@osdk/foundry";

export default async function useLlm(
    client: PlatformClient, // 이 파라미터는 실행 시점에 Foundry가 채워 넣습니다
    prompt: string
): Promise<string> {

    const promptMessage = [
        {
            role: "USER",
            content: prompt
        }
    ];
    const result = await Functions.Queries.execute(
        client,
        "com.foundry.languagemodelservice.models.gpt41.CreateChatCompletion",
        {
            parameters: {
                messages: promptMessage
            }
        },
        {
            preview: true, // 불안정(unstable) 엔드포인트에만 필요합니다. API 참조를 확인하십시오
        }
    );
    return result.value["completion"] as string;
}
```

**설명**: 이 TypeScript 함수는 문자열 `prompt`를 입력받아 언어 모델의 답변 문자열을 반환합니다. `client`는 코드에서 만들지 않고 Foundry가 실행 시점에 첫 번째 인자로 넣어 줍니다. `Functions.Queries.execute`는 이름(`...CreateChatCompletion`)으로 지정한 Foundry 쿼리를 실행하는 platform API이며, 여기서는 그 쿼리가 언어 모델 채팅 완성 기능입니다. 결과 객체의 `value["completion"]`에 모델의 답변이 들어 있습니다.

```python tab="Python"
from foundry_sdk import FoundryClient

@function
def media_item_to_base64(media_item_rid: str, media_set_rid: str) -> str:
    foundry_client = FoundryClient()

    result = foundry_client.media_sets.MediaSet.read(
        media_set_rid=media_set_rid,
        media_item_rid=media_item_rid,
        preview=True  # 불안정(unstable) 엔드포인트에만 필요합니다. API 참조를 확인하십시오
    )

    # 바이너리 스트림을 base64로 인코딩된 문자열로 변환합니다
    base64_encoded = base64.b64encode(result).decode('utf-8')

    return base64_encoded
```

**설명**: 이 Python 함수는 미디어 세트의 RID와 그 안의 미디어 항목 RID를 입력받아, 해당 파일(예: 이미지)의 바이트를 base64 문자열로 바꿔 반환합니다. Python에서는 `FoundryClient()`를 코드 안에서 직접 만들어 인증된 클라이언트를 얻습니다. RID(Resource Identifier)는 Foundry가 각 리소스에 부여하는 고유 식별자 문자열입니다. base64는 바이너리 데이터를 텍스트로 표현하는 인코딩으로, 문자열만 주고받을 수 있는 반환 타입에 파일 내용을 담을 때 씁니다.

<a id="client-permissions"></a>
### 클라이언트 권한 (Client permissions)

TypeScript v2 클라이언트(실행 시점에 Foundry가 함수에 전달)와 코드에서 초기화한 Python 클라이언트는 다음 권한 범위(scope)를 가집니다.

* `api:admin-read`
* `api:functions-read`
* `api:ontologies-read`
* `api:orchestration-read`
* `api:usage:mediasets-read`
* `api:usage:ontologies-write`

각 platform API 엔드포인트를 호출하려면 특정 범위가 필요합니다. 이 범위에 대한 문서는 [API 참조](https://www.palantir.com/docs/foundry/api/v2)에서 찾을 수 있습니다.

**주의**: Foundry 함수는 `api:usage:datasets-read` 범위로 데이터셋을 직접 읽는 것을 지원하지 않습니다. 데이터셋 읽기는 권한 오류를 반환합니다. Code Workspaces 라이브 미리보기에서는 사용자 컨텍스트와 전체 범위로 실행되므로 코드가 성공할 수 있지만, 배포된 함수는 제한된 권한을 사용하므로 실패합니다.

**설명**: 범위(scope)는 인증 토큰이 할 수 있는 일의 목록입니다. 예를 들어 토큰에 `api:ontologies-read`가 있으면 온톨로지 읽기 API를 호출할 수 있지만, 목록에 `api:usage:datasets-read`가 없으므로 데이터셋 읽기 API는 거부됩니다. 미리보기에서는 개발자 본인의 넓은 권한으로 실행되기 때문에, 미리보기에서 성공했다고 게시 후에도 성공한다는 보장이 없습니다.

> **중간 요약**: platform SDK로 언어 모델 호출, 미디어 세트 읽기 같은 Foundry API를 함수에서 사용할 수 있습니다. 함수의 클라이언트는 정해진 범위만 가지며, 특히 데이터셋 직접 읽기는 지원되지 않습니다.

## 정리

- Foundry platform SDK를 쓰면 함수에서 관리, 거버넌스, 스케줄과 빌드, 미디어 세트, 언어 모델 같은 Foundry API를 호출할 수 있습니다.
- Python(`foundry-platform-sdk`)과 TypeScript v2(`@osdk/foundry`)를 권장하며, TypeScript v1은 일급 인증을 지원하지 않습니다.
- TypeScript v2는 Foundry가 실행 시점에 클라이언트를 넘겨 주고, Python은 `FoundryClient()`를 코드에서 만듭니다.
- 클라이언트의 권한 범위는 정해져 있으며, 데이터셋을 직접 읽는 것은 허용되지 않습니다.
