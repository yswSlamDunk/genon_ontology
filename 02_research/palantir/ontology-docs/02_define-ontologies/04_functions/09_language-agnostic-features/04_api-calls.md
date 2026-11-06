# 함수에서 API 호출하기 (Make API calls from functions)

- 원문: https://www.palantir.com/docs/foundry/functions/api-calls/
- 사이드바 위치: Define Ontologies > Functions > Language-agnostic features > Make API calls from functions

이 페이지는 함수(function) 안에서 Foundry 바깥의 외부 시스템 API를 호출하는 방법을 다룹니다. Data Connection에서 소스(source)를 구성하는 사전 작업, 함수에서 소스를 선언하고 사용하는 코드, 소스의 속성과 자격 증명(credential)에 접근하는 방법, OAuth 2.0 인증을 쓰는 방법, 자주 발생하는 오류의 해결책을 설명합니다. 함수가 외부 날씨 서비스나 사내 REST API 같은 시스템과 데이터를 주고받아야 할 때 필요한 내용입니다.

TypeScript v1, TypeScript v2, Python 함수에서 외부 소스로 API를 호출할 수 있지만, 그렇게 하려면 추가 구성이 필요합니다. 이 구성과 외부 소스 사용법을 아래에서 자세히 설명합니다.

**팁**: 소스 별칭(Source aliases). TypeScript v2와 Python 함수에서는 [소스 별칭](../15_aliases/03_source-aliases.md)을 통해 소스를 참조할 것을 권장합니다. 소스 별칭은 특정 소스 대신 소스 식별자로 사용할 수 있는, 이식 가능한 이름 있는 참조입니다. 함수가 [Marketplace 제품](../07_function-management/03_marketplace-functions.md)으로 배포될 때 별칭을 환경마다 다른 소스로 다시 매핑할 수 있으므로 함수 코드의 이식성이 유지됩니다. TypeScript v1 함수는 생성된 소스 심볼을 사용하며 별칭을 지원하지 않습니다.

**설명**: 소스(source)는 Data Connection에 등록된 외부 시스템 연결 정보(주소, 인증서, 비밀 값 등)입니다. 별칭은 코드가 실제 소스 대신 `"mySourceAlias"` 같은 이름을 참조하게 하는 간접 참조입니다. 예를 들어 개발 환경에서는 별칭이 테스트 서버 소스를, 운영 환경에서는 운영 서버 소스를 가리키도록 매핑만 바꾸면 코드를 고치지 않고 같은 함수를 쓸 수 있습니다.

<a id="configure-access-to-external-apis"></a>
## 외부 API 접근 구성하기 (Configure access to external APIs)

기본적으로 함수는 외부 API를 호출할 수 없습니다. 함수에서 외부 시스템을 호출할 수 있게 하려면, Foundry가 외부 시스템과 연결할 수 있도록 [Data Connection](https://www.palantir.com/docs/foundry/data-connection/overview/)에서 [소스를 구성](https://www.palantir.com/docs/foundry/data-connection/set-up-source/)해야 합니다.

함수가 소스의 외부 시스템에 안전하게 연결하려면, 소스가 [내보내기(export)를 활성화](https://www.palantir.com/docs/foundry/data-connection/export-overview/#enable-exports-for-source)하고 [소스를 Code Repositories로 가져오기](https://www.palantir.com/docs/foundry/data-connection/external-transforms/#prerequisite-import-a-source-into-code)를 허용하도록 구성되어 있어야 합니다. 두 설정 모두 Data Connection에서 해당 소스로 이동해 **Connection settings** 섹션을 열면 구성할 수 있습니다.

TypeScript v1 함수의 경우, 코드에서 참조하는 식별자는 소스의 API 이름(**Connection settings** 아래 **Code import configuration** 탭에서 구성)입니다.

**주의**: 소스에 인증서 체인(certificate chain)을 완전히 구성했는지 확인하십시오. <br><br>
웹훅(webhook)과 함수의 실행 환경은 동일하지 않습니다. <br><br>
가끔 웹훅은 올바르게 동작하는데 함수에서의 API 호출은 `UNABLE_TO_GET_ISSUER_CERT` 오류를 만날 수 있습니다. <br><br>
인증서를 검증하려면 [소스 터미널의 `openssl` 명령](https://www.palantir.com/docs/foundry/data-connection/troubleshooting/#openssl)에 대한 문서를 참조하십시오.

**설명**: HTTPS 연결에서 서버는 자기 인증서를 보여 주고, 클라이언트는 그 인증서를 발급한 기관(issuer)의 인증서를 거슬러 올라가며 신뢰할 수 있는지 확인합니다. 이 연쇄가 인증서 체인입니다. 중간 기관의 인증서가 빠져 있으면 클라이언트가 발급자를 찾지 못해 `UNABLE_TO_GET_ISSUER_CERT` 오류가 납니다.

> **중간 요약**: 함수는 기본적으로 외부 API를 호출할 수 없으며, Data Connection에 소스를 만들고 내보내기와 코드 가져오기를 허용해야 합니다. 인증서 체인이 불완전하면 함수 호출만 실패할 수 있습니다.

<a id="use-an-external-source-in-a-function"></a>
## 함수에서 외부 소스 사용하기 (Use an external source in a function)

함수에서 API를 호출하려면 먼저 [resource imports 사이드바](../12_typescript-v1/08_resource-imports-sidebar.md)를 사용해 소스를 함수 저장소로 가져와야 합니다. TypeScript v2와 Python 함수에서는 그다음 [소스 별칭을 만들고](../15_aliases/03_source-aliases.md) 별칭 키를 소스 식별자로 사용할 것을 권장합니다. TypeScript v1 함수는 가져온 소스를 직접 참조합니다. 그런 다음 아래 예제처럼 함수가 소스를 사용한다고 선언해야 합니다.

예제는 아래와 같습니다.

```typescript tab="TypeScript v2"
import { getSource, getHttpsConnection, getFetch } from "@palantir/functions-sources";

export const config = {
    sources: ["mySourceAlias"]
}

async function MyExternalFunction(): Promise<string> {
    const source = await getSource("mySourceAlias");
    const { url } = getHttpsConnection(source);
    const fetch = await getFetch(source);

    const response = await fetch(url);

    return response.text();
}
```

(원문에는 `@ExternalSystems({ sources: [MySource] })` 데코레이터로 소스를 선언하는 TypeScript v1 버전과, `@function(sources=["mySourceAlias"])`로 선언하고 `get_source`로 소스를 얻는 Python 버전도 있습니다.)

**설명**: 동작 순서는 다음과 같습니다. (1) `config.sources`에 사용할 소스 별칭을 선언합니다. 선언하지 않은 소스는 함수 안에서 쓸 수 없습니다. (2) `getSource`로 소스 객체를 얻습니다. (3) `getHttpsConnection(source)`로 소스에 설정된 기본 URL을 얻습니다. (4) `getFetch(source)`로 소스 설정(인증서, 프록시)이 적용된 `fetch` 함수를 얻어 HTTP 요청을 보냅니다. (5) 응답 본문을 문자열로 반환합니다.

라이브 미리보기(live preview)에서 함수를 테스트할 수 있으며, 게시한 뒤에는 함수를 사용해 외부 호출을 할 수 있습니다.

**주의**: **서드파티 클라이언트는 fetch 함수나 HTTP 에이전트를 재정의(override)하지 않는 한 서버리스 실행이나 라이브 미리보기에서 아직 지원되지 않습니다.** 모든 환경에서 API 호출이 올바르게 동작하도록 하려면 관련 라이브러리 메서드를 사용해 올바른 구성으로 요청을 보내야 합니다. 외부 소스나 내부 Foundry URL로 직접 API를 호출하는 것은 모든 환경에서 동작한다고 보장되지 않습니다.

<a id="access-source-attributes-and-credentials"></a>
## 소스 속성과 자격 증명에 접근하기 (Access source attributes and credentials)

각 함수 타입에 대응하는 라이브러리가 제공하는 소스 속성에 접근할 수 있습니다.

아래 예제는 위 예제에 나온 소스의 기본 URL을 얻는 방법을 보여 줍니다.

```typescript tab="TypeScript v1"
const { url } = MySource.getHttpsConnection();
```

```typescript tab="TypeScript v2"
const { url } = getHttpsConnection(source);
```

```python tab="Python"
url = get_source("mySourceAlias").get_https_connection().url
```

소스에 저장된 추가 비밀 값(secret)이나 자격 증명에도 접근할 수 있습니다. 비밀 값에 접근하려면 다음 문법을 사용합니다.

```typescript tab="TypeScript v1"
const secret = MySource.getSecret("MySecret");
```

```typescript tab="TypeScript v2"
const secret = source.secrets["MySecret"];
```

```python tab="Python"
secret = get_source("mySourceAlias").get_secret("MySecret")
```

**설명**: 비밀 값은 API 키나 비밀번호처럼 코드에 직접 적으면 안 되는 값입니다. 소스에 이름(`"MySecret"`)으로 저장해 두고 실행 시점에 이름으로 꺼내 쓰므로, 저장소의 소스 코드에는 실제 값이 남지 않습니다.

<a id="use-the-pre-configured-clients"></a>
## 미리 구성된 클라이언트 사용하기 (Use the pre-configured clients)

REST API를 제공하는 소스의 경우, 소스 객체에서 클라이언트를 얻을 수 있습니다. 이 클라이언트에는 소스에 지정된 서버 인증서와 클라이언트 인증서가 미리 구성되어 있습니다. 또한 함수가 실행되는 환경에서 외부로 나가는 통신(egress)을 허용하는 추가 프록시 구성도 포함됩니다. 함수가 모든 환경에서 소스로 나가는 통신을 할 수 있도록 보장하려면, 가능한 한 항상 이 클라이언트를 사용해야 합니다.

```typescript tab="TypeScript v1"
const fetch = MySource.fetch;
```

```typescript tab="TypeScript v2"
const fetch = await getFetch(source);
```

```python tab="Python"
client = source.get_https_connection().get_client()
```

또는 외부 요청을 보내는 자체 클라이언트나 서드파티 라이브러리를 사용하고, 소스 객체로 [속성과 자격 증명을 가져올](#access-source-attributes-and-credentials) 수도 있습니다.

TypeScript v2 함수는 사용자 지정 HTTP 에이전트를 받는 서드파티 라이브러리와 함께 사용할 수 있도록, 미리 구성된 HTTP 에이전트를 추가 연동 지점으로 제공합니다.

다음 예제는 이 에이전트를 얻어 [axios ↗](https://github.com/axios/axios)와 함께 사용하는 방법을 보여 줍니다.

```typescript tab="TypeScript v2"
import { getHttpAgent, getHttpsConnection } from "@palantir/functions-sources";
import axios from 'axios';

const agent = await getHttpAgent(source);
const { url } = getHttpsConnection(source);

const response = await axios.get(url, {
    httpsAgent: agent,
});
```

**설명**: HTTP 에이전트는 Node.js에서 연결 방식(프록시, TLS 인증서 등)을 담당하는 객체입니다. axios는 자체적으로 요청을 보내므로 소스 설정을 모르지만, `httpsAgent`에 소스에서 얻은 에이전트를 넘기면 소스의 인증서와 프록시 설정이 적용된 상태로 요청이 나갑니다.

**참고**: 현재로서는 소스가 HTTPS 클라이언트를 제공하지 않는 한, 자격 증명이 아닌 소스 속성에는 접근할 수 없습니다. 예를 들어 [PostgreSQL 소스](https://www.palantir.com/docs/foundry/available-connectors/postgresql/)에서는 `hostname`이나 그 밖의 비밀이 아닌 속성에 접근할 수 없습니다.

> **중간 요약**: 함수는 사용할 소스를 선언한 뒤 소스의 URL, 비밀 값, 미리 구성된 클라이언트를 사용해 외부 API를 호출합니다. 모든 실행 환경에서 동작하게 하려면 소스가 제공하는 클라이언트(또는 TypeScript v2의 HTTP 에이전트)를 쓰는 것이 안전합니다.

<a id="use-oauth-20-with-outbound-applications"></a>
## 아웃바운드 애플리케이션으로 OAuth 2.0 사용하기 (Use OAuth 2.0 with outbound applications)

외부 API가 OAuth 2.0 인가(authorization)를 요구한다면, Control Panel에서 [아웃바운드 애플리케이션(outbound application)](https://www.palantir.com/docs/foundry/administration/configure-outbound-applications/)을 구성하고 이를 REST API 소스의 인증 방법으로 사용할 수 있습니다. 함수가 실행되면 소스는 호출한 사용자의 OAuth 액세스 토큰을 세션 자격 증명(session credentials)으로 노출합니다. 그러면 함수는 이 토큰을 사용해 사용자를 대신해서 외부 API를 호출할 수 있습니다.

이 패턴은 Python과 TypeScript v2 함수에서 지원됩니다. 코드 예제는 아래 [소스의 미리 구성된 클라이언트 사용하기](#use-the-sources-pre-configured-client)를 참조하십시오.

**설명**: OAuth 2.0은 사용자가 비밀번호를 넘기지 않고도 어떤 애플리케이션이 자기 대신 다른 서비스의 API를 호출하도록 허락하는 표준 프로토콜입니다. 허락이 끝나면 애플리케이션은 액세스 토큰(access token)을 받아 HTTP 요청의 `Authorization: Bearer <토큰>` 헤더에 넣어 보냅니다. 여기서는 Foundry가 그 애플리케이션 역할을 하며, 함수를 실행한 사용자 본인의 토큰으로 외부 API가 호출됩니다.

<a id="limitations"></a>
### 제한 사항 (Limitations)

* **TypeScript v1:** TypeScript v1 함수는 소스에서 OAuth 토큰을 직접 가져올 수 없습니다. TypeScript v1 함수에서 OAuth 2.0 API로 인증하려면, 아웃바운드 애플리케이션으로 구성된 REST API 소스의 [웹훅](../12_typescript-v1/10_webhooks.md)으로 호출을 감싸십시오. 토큰에 직접 접근하려면 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)하는 것을 고려하십시오.
* **배포 모드(Deployed mode):** 함수가 [배포 모드](06_functions-deployed.md)로 실행 중일 때는 OAuth 토큰 갱신을 사용할 수 없습니다. 실행 중에 호출한 사용자의 액세스 토큰이 만료되면, 함수는 토큰을 자동으로 갱신할 수 없습니다. OAuth 기반 아웃바운드 애플리케이션을 사용하려면 함수를 [서버리스 모드](06_functions-deployed.md#choose-between-deployed-and-serverless-execution-modes)로 실행하십시오.
* **Workshop에서 함수를 직접 사용하는 경우:** [함수 기반 변수](https://www.palantir.com/docs/foundry/workshop/functions-use/#function-backed-variables-in-workshop)나 위젯 내용을 채우는 함수처럼 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/) 모듈에서 직접 사용하는 함수는 OAuth 2.0 대화형 인가 프롬프트를 띄울 수 없습니다. 사용자가 아웃바운드 애플리케이션을 아직 인가하지 않았다면, 함수는 프롬프트를 표시하는 대신 실패합니다. Workshop에서 OAuth 기반 함수를 사용하려면 [함수 기반 액션](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)으로 감싸십시오. 또는 Workshop에서 함수가 직접 호출되기 전에, 사용자가 다른 대화형 인터페이스(예: 같은 아웃바운드 애플리케이션을 쓰는 함수 기반 액션)에서 인가 절차를 마치도록 하십시오.

<a id="use-the-sources-pre-configured-client"></a>
### 소스의 미리 구성된 클라이언트 사용하기 (Use the source's pre-configured client)

가장 간단한 방법은 소스가 제공하는 HTTP 클라이언트를 사용하는 것입니다. `Authorization` 헤더가 자동으로 주입됩니다.

```python tab="Python"
from functions.api import function
from functions.sources import get_source

@function(sources=["myOAuthSourceAlias"])
def call_external_api() -> str:
    source = get_source("myOAuthSourceAlias")
    url = source.get_https_connection().url
    client = source.get_https_connection().get_client()

    response = client.get(url + "/api/v1/resource", timeout=10)
    return response.text
```

(원문에는 `getFetch(source)`로 얻은 fetch를 사용하는 TypeScript v2 버전도 있습니다.)

**설명**: 앞의 일반 예제와 코드가 거의 같습니다. 차이는 소스가 OAuth 아웃바운드 애플리케이션으로 구성되어 있다는 점뿐이며, `get_client()`로 얻은 클라이언트가 호출한 사용자의 토큰을 `Authorization` 헤더에 자동으로 넣어 줍니다.

<a id="use-a-native-http-client-with-manual-token-injection"></a>
### 네이티브 HTTP 클라이언트에 토큰을 직접 주입하기 (Use a native HTTP client with manual token injection)

소스가 제공하는 클라이언트 대신 자체 HTTP 클라이언트를 사용해야 한다면, 세션 자격 증명에서 OAuth 토큰을 가져와 `Authorization` 헤더를 직접 설정합니다.

```typescript tab="TypeScript v2"
import { getSource, getHttpsConnection } from "@palantir/functions-sources";

export const config = {
    sources: ["myOAuthSourceAlias"]
};

export default async function callExternalApi(): Promise<string> {
    const source = await getSource("myOAuthSourceAlias");
    const credentials = await source.sessionCredentials?.get();

    if (!credentials || credentials.type !== "oauth") {
        throw new Error("Expected OAuth credentials");
    }

    const accessToken: string = credentials.accessToken;
    const { url } = getHttpsConnection(source);

    const response = await fetch(url + "/api/v1/resource", {
        headers: { Authorization: `Bearer ${accessToken}` },
    });

    return response.text();
}
```

(원문에는 `source.get_session_credentials().get()`으로 자격 증명을 얻고 `OauthCredentials`인지 확인한 뒤 `requests` 라이브러리로 호출하는 Python 버전도 있습니다.)

**설명**: `source.sessionCredentials?.get()`이 현재 사용자의 세션 자격 증명을 돌려줍니다. 그 타입이 `"oauth"`인지 확인한 다음 `accessToken`을 꺼내 `Bearer` 헤더로 직접 붙입니다. 소스 클라이언트를 쓰지 않으므로 헤더 주입을 코드가 책임집니다.

<a id="use-oauth-backed-functions-in-actions"></a>
### 액션에서 OAuth 기반 함수 사용하기 (Use OAuth-backed functions in actions)

흔한 패턴은 OAuth 기반 외부 API를 호출하고 그 결과를 [온톨로지 편집(edit)](01_edits-overview.md)에 넣는 것입니다. 그런 다음 그 함수를 [함수 기반 액션](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)으로 공개할 수 있습니다. 사용자가 Workshop이나 AIP Studio에서 액션을 실행하면, 그 사용자의 OAuth 토큰으로 API 호출이 이루어지고 결과로 생긴 객체 편집은 그 사용자가 한 것으로 기록됩니다.

예를 들어 아래 함수는 OAuth 토큰을 사용해 서드파티 신원(identity) 서비스에서 호출한 사용자의 프로필을 가져옵니다. 그런 다음 그 정보로 새 온톨로지 객체를 만듭니다.

```python tab="Python"
from functions.api import function, OntologyEdit
from functions.sources import get_source
from ontology_sdk import FoundryClient
from ontology_sdk.ontology.objects import UserProfile


@function(sources=["myOAuthSourceAlias"], edits=[UserProfile])
def link_user_profile() -> list[OntologyEdit]:
    source = get_source("myOAuthSourceAlias")
    url = source.get_https_connection().url
    client = source.get_https_connection().get_client()

    response = client.get(url + "/v1/me", timeout=10)
    response.raise_for_status()
    profile = response.json()

    ontology_edits = FoundryClient().ontology.edits()
    ontology_edits.objects.UserProfile.create(
        profile["id"],
        display_name=profile["display_name"],
    )
    return ontology_edits.get_edits()
```

(원문에는 `createEditBatch`로 편집을 모으는 TypeScript v2 버전도 있습니다.)

**설명**: 이 함수는 입력 없이 실행되어 (1) 외부 서비스의 `/v1/me`를 호출해 현재 사용자 프로필 JSON(예: `{"id": "abc", "display_name": "Kim"}`)을 받고, (2) 그 값으로 `UserProfile` 객체를 하나 만드는 편집을 기록한 뒤, (3) 편집 목록을 반환합니다. `edits=[UserProfile]`은 이 함수가 `UserProfile` 객체 타입을 편집한다고 선언하는 부분입니다. 함수 자체는 편집 목록을 반환할 뿐이고, 실제로 온톨로지에 반영되는 것은 이 함수를 액션으로 실행했을 때입니다.

> **중간 요약**: 아웃바운드 애플리케이션을 소스 인증 방법으로 쓰면 함수가 호출한 사용자의 OAuth 토큰으로 외부 API를 호출할 수 있습니다(Python, TypeScript v2). 배포 모드와 Workshop 직접 호출에는 제한이 있으므로 서버리스 모드나 함수 기반 액션을 사용합니다.

<a id="troubleshoot-common-errors"></a>
## 자주 발생하는 오류 해결하기 (Troubleshoot common errors)

`HTTP 401: Unauthorized`, `Credentials expired and no refresh handler provided`, `Resolved source credentials are not present on the Source` 같은 OAuth 인가 오류는 Data Connection 문제 해결 참조 문서의 [OAuth와 아웃바운드 애플리케이션](https://www.palantir.com/docs/foundry/data-connection/troubleshooting/#oauth-and-outbound-applications)을 참조하십시오.

<a id="http-407-proxy-authentication-required"></a>
### HTTP 407: 프록시 인증 필요 (HTTP 407: Proxy authentication required)

함수의 네트워크 요청은 소스의 [이그레스 정책(egress policy)](https://www.palantir.com/docs/foundry/administration/configure-egress/)이 허용하는 범위 안에 있어야 합니다. 대상 호스트 이름이 허용된 정책과 일치하지 않으면 요청이 `HTTP 407: Proxy Authentication Required`를 반환할 수 있습니다.

이그레스 정책이 올바르게 보인다면 요청 URL을 어떻게 만드는지 확인하십시오. `getHttpsConnection()`에서 얻는 URL에는 끝에 슬래시가 없으므로, 앞에 `/`를 빠뜨린 경로를 덧붙이면 호스트 이름에 붙어 버립니다.

```text
"https://example.com" + "api/v1"
→ "https://example.comapi/v1"
```

그 결과 생긴 호스트 이름(`example.comapi`)은 어떤 이그레스 정책에도 포함되지 않으므로 요청이 거부됩니다. 경로 앞에 `/`를 붙이십시오(예: `url + "/api/v1"`).

**설명**: 이그레스(egress)는 Foundry 내부에서 바깥 네트워크로 나가는 통신입니다. Foundry는 허용 목록에 있는 호스트로만 나가는 요청을 통과시키므로, 문자열을 잘못 이어 붙여 호스트 이름이 바뀌면 허용 목록에 없는 주소로 판단되어 차단됩니다.

> **중간 요약**: OAuth 관련 오류는 Data Connection 문제 해결 문서를 참조합니다. HTTP 407은 이그레스 정책에 맞지 않는 호스트로 요청할 때 생기며, URL에 경로를 붙일 때 앞의 `/`를 빠뜨린 것이 흔한 원인입니다.

## 정리

- 함수가 외부 API를 호출하려면 Data Connection에서 소스를 만들고, 내보내기와 코드 가져오기를 허용한 뒤, 함수에서 소스를 선언해야 합니다.
- TypeScript v2와 Python에서는 소스 별칭을 쓰는 것이 권장되며, TypeScript v1은 소스를 직접 참조합니다.
- 소스 객체에서 기본 URL, 비밀 값, 인증서와 프록시가 미리 구성된 클라이언트를 얻을 수 있고, 모든 환경에서 동작하려면 이 클라이언트를 쓰는 것이 안전합니다.
- 아웃바운드 애플리케이션을 쓰면 호출한 사용자의 OAuth 토큰으로 외부 API를 호출할 수 있으며, 함수 기반 액션과 결합해 결과를 온톨로지 편집으로 남길 수 있습니다.
- HTTP 407 오류는 이그레스 정책 범위 밖의 호스트로 요청할 때 발생하며, URL 경로 앞의 `/` 누락을 먼저 확인합니다.
