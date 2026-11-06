# 소스 별칭 (Source aliases)

- 원문: https://www.palantir.com/docs/foundry/functions/source-aliases/
- 사이드바 위치: Define Ontologies > Functions > Aliases > Source aliases

이 페이지는 함수(function)가 외부 시스템에 접속할 때 쓰는 Data Connection 소스(source)를 별칭(alias)으로 참조하는 방법을 다룹니다. 소스를 가져오고 별칭을 붙이는 절차, 코드에서 별칭으로 소스를 꺼내 HTTP 요청을 보내는 예, 그리고 Marketplace 설치 시 설치하는 쪽이 자기 환경의 소스로 바꿔 끼우는 방법을 설명합니다.

소스 별칭은 [Data Connection 소스](https://www.palantir.com/docs/foundry/data-connection/set-up-source/)에 대한 이름 붙은, 이식 가능한(portable) 참조입니다. 특정 소스 식별자 대신 별칭 키로 소스를 참조하면, 함수 로직을 특정 소스 하나에 묶이지 않게 분리할 수 있습니다. 이렇게 하면 함수를 여러 환경으로 옮겨 쓸 수 있습니다.

**설명**: Data Connection 소스는 Foundry 바깥의 시스템(예: 외부 REST API 서버, 데이터베이스)에 접속하기 위한 주소와 자격 증명(credential)을 등록해 둔 Foundry 리소스입니다. 개발 환경에서는 테스트 서버를, 운영 환경에서는 실제 서버를 가리키는 서로 다른 소스가 있을 수 있습니다. 코드가 `demoSource` 같은 별칭만 쓰면, 어떤 실제 소스에 연결할지는 코드 밖에서 정할 수 있습니다.

<a id="import-a-source"></a>
## 소스 가져오기 (Import a source)

Code Workspaces의 VS Code에서 개발하고 있다면 [VS Code에서 소스 가져오기](../06_navigating-vscode.md#import-a-source) 절차를 따르세요.

소스를 가져오려면 다음과 같이 합니다.

1. TypeScript v2 또는 Python 코드 저장소를 열고 **Resource imports** 패널로 이동합니다.

2. **Ontology SDK** 탭을 선택합니다.

3. **Add > Sources**를 선택합니다.

   ![Resource imports 패널의 Add 드롭다운에 Sources 옵션이 표시된 화면.](https://www.palantir.com/docs/resources/foundry/functions/source-aliases-import.png)

4. 가져올 소스를 검색해 선택한 다음 **Confirm selection**을 선택합니다.

<a id="add-a-source-alias"></a>
## 소스 별칭 추가하기 (Add a source alias)

소스를 가져온 뒤 별칭을 추가할 수 있습니다.

1. **Resource imports** 패널의 **Sources** 아래에서 소스를 찾습니다.
2. 소스 이름 아래의 **Add alias**를 선택합니다.

   ![가져온 소스와 별칭 추가 옵션이 표시된 Resource imports 패널.](https://www.palantir.com/docs/resources/foundry/functions/source-aliases-add.png)

**주의**: 별칭 키는 저장소 안에서 유일해야 합니다.

<a id="edit-a-source-alias"></a>
## 소스 별칭 편집하기 (Edit a source alias)

기존 소스 별칭을 편집하려면 **Resource imports** 패널의 **Sources** 섹션으로 이동합니다. 별칭 옆의 연필 아이콘을 선택하면 그 자리에서 편집할 수 있습니다.

![소스 별칭과 편집 옵션이 표시된 Resource imports 패널.](https://www.palantir.com/docs/resources/foundry/functions/source-aliases-edit.png)

> **중간 요약**: 소스는 Resource imports 패널의 Ontology SDK 탭에서 Add > Sources로 가져오고, Sources 목록에서 Add alias로 별칭을 붙입니다. 별칭 키는 저장소 안에서 유일해야 하며 연필 아이콘으로 고칩니다.

<a id="use-a-source-alias-in-code"></a>
## 코드에서 소스 별칭 사용하기 (Use a source alias in code)

함수에서 소스 별칭을 사용하려면, 소스를 선언하고 가져오는 모든 곳에서 별칭 키로 참조합니다. 별칭 키를 `sources` 구성과 `getSource`(TypeScript v2) 또는 `get_source`(Python)에 전달합니다.

```typescript
import { getSource, getHttpsConnection, getFetch } from "@palantir/functions-sources";

export const config = {
    sources: ["demoSource"]
}

async function myExternalFunction(): Promise<string> {
    const source = await getSource("demoSource");
    const { url } = getHttpsConnection(source);
    const fetch = await getFetch(source);

    const response = await fetch(url);

    return response.text();
}
```

(원문에는 같은 동작을 하는 Python 버전도 있습니다. `@function(sources=["demoSource"])`로 소스를 선언하고, `get_source("demoSource")`로 소스를 얻은 뒤 `source.get_https_connection()`의 `url`과 `get_client()`로 GET 요청을 보내 `response.text`를 반환합니다.)

**설명**: 이 함수는 입력 없이, 별칭 `demoSource`가 가리키는 외부 서버에 HTTP 요청을 보내 응답 본문 문자열을 반환합니다.
- `config.sources: ["demoSource"]`: 이 함수가 `demoSource` 소스를 사용한다고 함수 정의 수준에서 미리 선언합니다. 원문 설명대로 별칭 키는 이 선언과 아래 `getSource` 호출 양쪽에 모두 넣어야 합니다.
- `getSource("demoSource")`: 별칭을 실제 소스로 해석해 가져옵니다.
- `getHttpsConnection(source)`: 소스에 등록된 HTTPS 연결 정보에서 `url`을 꺼냅니다.
- `getFetch(source)`: 이 소스로 요청을 보낼 수 있도록 준비된 `fetch` 함수를 얻습니다.
- `fetch(url)`와 `response.text()`: 요청을 보내고 응답 본문을 문자열로 읽습니다.

별칭이 해석되는 소스의 리소스 식별자(RID)가 필요하면, TypeScript v2에서는 `Aliases.source` 유틸리티를, Python에서는 `source` 유틸리티를 사용합니다. 해석된 RID는 `.rid` 속성에서 읽습니다.

```typescript
import { Aliases } from "@osdk/functions";

const sourceRid = Aliases.source("demoSource").rid;
```

(원문에는 Python 버전도 있습니다. `functions.aliases`에서 `source`를 import하고 `source("demoSource").rid`로 RID를 얻습니다.)

자격 증명 접근과 미리 구성된 클라이언트 사용을 포함해, 함수에서 소스를 사용하는 방법은 [함수에서 API 호출하기](../09_language-agnostic-features/04_api-calls.md)를 참고하세요.

> **중간 요약**: 코드에서는 `sources` 구성과 `getSource`(Python은 `get_source`)에 별칭 키를 넘겨 소스를 사용합니다. RID가 필요하면 `Aliases.source("키").rid`(Python은 `source("키").rid`)로 얻습니다.

<a id="use-source-aliases-with-marketplace"></a>
## Marketplace에서 소스 별칭 사용하기 (Use source aliases with Marketplace)

소스 별칭을 사용하는 함수를 [Marketplace 제품](../07_function-management/03_marketplace-functions.md)에 추가하면, 별칭이 붙은 각 소스가 **Data connection sources** 아래에 구성 가능한 입력으로 나타납니다. 설치하는 사람은 설치 중에 각 입력 소스를 자기 환경에서 사용할 수 있는 소스로 매핑할 수 있으며, 함수 소스 코드를 수정할 필요가 없습니다.

![Data Connection 소스가 구성 가능한 입력으로 표시된 Marketplace 제품.](https://www.palantir.com/docs/resources/foundry/functions/source-aliases-marketplace-product.png)

<a id="set-a-description"></a>
### 설명 설정하기 (Set a description)

설치하는 사람이 어떤 소스를 제공해야 하는지 이해하도록, 소스 입력에 설명(description)을 추가할 수 있습니다. **Inputs** 아래에서 소스를 선택해 **Details** 패널을 연 다음 **General** 탭에 설명을 입력합니다.

![설명 입력란이 표시된 소스 입력의 Details 패널.](https://www.palantir.com/docs/resources/foundry/functions/source-aliases-description.png)

<a id="installation-experience"></a>
### 설치 경험 (Installation experience)

설치 중에 설치하는 사람은 소스 설명을 보고 자기 환경에 맞는 소스를 선택할 수 있습니다. Marketplace는 선택된 소스를 정의된 별칭에 자동으로 다시 매핑하므로, 함수 코드는 그대로 유지됩니다.

![설명과 함께, 소스를 바꾸거나 네임스페이스로 범위를 지정하는 옵션이 표시된 소스 별칭의 설치 화면.](https://www.palantir.com/docs/resources/foundry/functions/source-aliases-install.png)

> **중간 요약**: Marketplace 제품에서 별칭이 붙은 소스는 Data connection sources 입력이 되고, 설치자는 자기 환경의 소스를 골라 연결합니다. 별칭이 자동으로 다시 매핑되므로 함수 코드는 바뀌지 않습니다.

## 정리

- 소스 별칭은 Data Connection 소스를 키 이름으로 참조해 함수를 특정 소스와 분리합니다.
- Resource imports 패널의 Ontology SDK 탭에서 소스를 가져오고 Add alias로 별칭을 붙입니다.
- 코드에서는 `sources` 선언과 `getSource`/`get_source`에 별칭 키를 넘기고, RID가 필요하면 `.rid`로 읽습니다.
- Marketplace 설치 시 설치자가 자기 환경의 소스를 고르면 별칭이 자동으로 다시 매핑됩니다.
