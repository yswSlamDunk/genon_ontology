# Palantir 제공 모델로 시맨틱 검색 워크플로 만들기 (Use Palantir-provided models to create a semantic search workflow)

- 원문: https://www.palantir.com/docs/foundry/ontology/using-palantir-provided-models-to-create-a-semantic-search-workflow/
- 사이드바 위치: Ontology search > Semantic search > Use Palantir-provided models to create a semantic search workflow

이 페이지는 Palantir가 제공하는 임베딩 모델을 사용해 시맨틱 검색(semantic search) 워크플로를 처음부터 끝까지 만드는 과정을 보여 줍니다. 먼저 텍스트를 벡터(임베딩)로 바꿔 객체 타입의 속성(property)으로 저장하고, 그다음 Workshop, AIP Chatbot, 함수(function) 중 하나로 그 벡터를 검색하는 화면이나 로직을 구성합니다. 키워드가 정확히 일치하지 않아도 의미가 비슷한 객체를 찾아 주는 검색을 직접 구현해 보는 실습 안내서입니다.

**참고**: Palantir가 제공하는 언어 모델을 사용하려면 먼저 [사용 중인 환경(enrollment)에서 AIP가 활성화되어 있어야 합니다](https://www.palantir.com/docs/foundry/aip/enable-aip-features/). 또한 [AIP 개발자 기능](https://www.palantir.com/docs/foundry/platform-overview/aip-capabilities/)을 사용할 권한이 있어야 합니다. 직접 만든 모델(custom model)을 사용하나요? 그렇다면 대신 [커스텀 모델로 시맨틱 검색 워크플로 만들기](06_using-custom-models-to-create-a-semantic-search-workflow.md)를 참고하세요.

이 페이지는 [Palantir가 제공하는 임베딩 모델](https://www.palantir.com/docs/foundry/aip/supported-llms/)을 사용해 가상의 엔드투엔드 시맨틱 검색 워크플로를 만드는 과정을 설명합니다.

**설명**: 임베딩(embedding)은 문장 같은 텍스트를 고정 길이의 실수 배열(벡터)로 바꾼 것입니다. 예를 들어 "엔진 과열 경고"와 "엔진 온도가 너무 높음"은 단어는 다르지만 의미가 비슷하므로, 임베딩 모델을 거치면 서로 가까운 벡터가 나옵니다. 시맨틱 검색은 사용자의 질의도 같은 모델로 벡터로 바꾼 뒤, 저장된 벡터 중 질의 벡터와 거리가 가장 가까운 것들을 찾는 방식으로 동작합니다. SQL의 `LIKE '%엔진%'`처럼 문자열 일치를 보는 검색과 달리, 의미의 유사도를 기준으로 결과를 고릅니다.

<a id="instructions"></a>
## 진행 순서 (Instructions)

먼저 임베딩을 생성하고 이를 [`vector` 타입](../../02_define-ontologies/02_object-and-link-types/03_properties/05_property-metadata.md#property-base-types-with-limited-support)을 가진 객체 타입에 저장해야 합니다. 그런 다음 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)에서 시맨틱 검색 워크플로를 설정하거나, [AIP Chatbot Workshop 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-aip-chatbot/) 솔루션을 만들거나, [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)과 [AIP Logic](https://www.palantir.com/docs/foundry/logic/overview/)에서 사용할 커스텀 시맨틱 검색 함수를 만들 수 있습니다.

사전 준비:

* [임베딩 생성 및 객체 타입 만들기](#generate-embeddings-and-create-object-type)

선택지:

* [KNN 객체 집합(object set)을 사용해 Workshop에서 간단한 시맨틱 검색 워크플로 만들기(노코드)](#create-a-simple-semantic-search-workflow-within-workshop-using-a-knn-object-set-no-code)
* [AIP Chatbot이 객체를 시맨틱 검색하도록 설정하기(노코드)](#use-aip-chatbot-no-code)
* [Workshop 또는 AIP Logic에서 사용할, 객체를 시맨틱 검색하는 함수 만들기](#create-a-function-to-semantically-search-across-objects-for-use-in-workshop-andor-aip-logic)

> **중간 요약**: 공통 준비 단계는 임베딩을 만들어 객체 타입의 벡터 속성으로 저장하는 것입니다. 그 뒤 Workshop의 KNN 객체 집합, AIP Chatbot, 커스텀 함수 중 하나를 골라 검색을 구성합니다.

<a id="generate-embeddings-and-create-object-type"></a>
## 임베딩 생성 및 객체 타입 만들기 (Generate embeddings and create object type)

[Pipeline Builder](https://www.palantir.com/docs/foundry/pipeline-builder/overview/)의 [**Text to Embeddings** 표현식](https://www.palantir.com/docs/foundry/pipeline-builder/pipeline-builder-aip/#text-to-embeddings)을 사용해 데이터셋의 텍스트를 벡터로 임베딩합니다. 이 표현식은 문자열을 입력받아 Palantir가 제공하는 모델 중 하나를 사용해 벡터로 변환합니다. 이 예에서는 `text-embedding-ada-002` 임베딩 모델을 사용합니다.

![Text to Embedding 표현식](https://www.palantir.com/docs/resources/foundry/ontology/text-to-embedding.png)

이렇게 만든 임베딩은 벡터 속성으로 온톨로지에 추가할 수 있습니다.

![Pipeline Builder 출력 객체 속성에서 벡터 속성 설정하기](https://www.palantir.com/docs/resources/foundry/ontology/embeddings-as-pipeline-builder-output-object-property.png)

Palantir 제공 모델로 임베딩을 생성하는 과정을 더 세밀하게 제어하고 싶다면 [Python 트랜스폼 안의 언어 모델](https://www.palantir.com/docs/foundry/transforms-python-spark/palantir-provided-models/#embeddings)을 참고하세요.

**설명**: 결과적으로 데이터셋에 열이 하나 추가된다고 보면 됩니다. 예를 들어 `incident_id`, `description` 열이 있던 테이블에 `embeddings` 열이 생기고, 각 행의 이 열에는 `description` 텍스트를 모델에 넣어 얻은 실수 배열(ada-002 모델은 1536개 원소)이 들어갑니다. 이 열을 객체 타입의 `vector` 타입 속성으로 매핑하면, 이후 온톨로지 차원에서 벡터 검색을 할 수 있습니다.

> **중간 요약**: Pipeline Builder의 Text to Embeddings 표현식으로 텍스트 열을 벡터 열로 바꾸고, 그 열을 객체 타입의 벡터 속성으로 등록합니다.

<a id="create-a-simple-semantic-search-workflow-within-workshop-using-a-knn-object-set-no-code"></a>
## KNN 객체 집합을 사용해 Workshop에서 간단한 시맨틱 검색 워크플로 만들기(노코드) (Create a simple semantic search workflow within Workshop using a KNN object set (no-code))

**참고**: KNN 객체 집합은 관련도(relevance) 순으로 정렬할 수 없습니다. 정렬된 결과가 필요하다면 TypeScript v1 또는 TypeScript v2로 [함수 방식](#create-a-function-to-semantically-search-across-objects-for-use-in-workshop-andor-aip-logic)을 사용하세요. 두 버전 모두 관련도 순 정렬을 지원합니다.

[Workshop](https://www.palantir.com/docs/foundry/workshop/overview/) 안에서 [KNN 객체 집합(TSv1)](../../02_define-ontologies/04_functions/13_functions-on-objects/07_api-object-sets.md#k-nearest-neighbors-knn)을 설정하는 것은 코드 없이 시맨틱 검색 워크플로를 만드는 쉬운 방법입니다.

**설명**: KNN(K-Nearest Neighbors, K-최근접 이웃)은 질의 벡터와 거리가 가장 가까운 K개의 데이터를 찾는 방법입니다. K=3이면 저장된 모든 벡터 가운데 질의 벡터와 가장 가까운 3개를 돌려줍니다.

1. 객체 집합 [변수](https://www.palantir.com/docs/foundry/workshop/concepts-variables/)를 만들고, 임베딩 속성을 가진 객체 타입을 선택합니다.
2. 필터의 `+ On a property` 옵션을 선택한 뒤, 메뉴의 속성 목록에서 임베딩 속성을 선택합니다.
3. 선택하면 K-최근접 이웃 설정 화면이 나타나야 합니다. 이 설정이 나타나지 않는다면 선택한 속성이 임베딩 속성인지 확인하세요.

![Workshop KNN 설정](https://www.palantir.com/docs/resources/foundry/ontology/knn-config-workshop.png)

이 패널에서 다음 항목을 설정할 수 있습니다.

* **K-value:** 시맨틱 검색에서 몇 개의 객체를 반환할지 정하는 1\~100 사이의 숫자입니다.
* **Query:** 시맨틱 검색을 수행할 때 질의로 사용할 문자열 변수입니다.

4. 다음으로 [텍스트 입력(text input)](https://www.palantir.com/docs/foundry/workshop/widgets-text-input/) 위젯을 만들고, 그 출력 변수를 위에서 본 KNN의 Query 옵션에 넣습니다.
5. 마지막으로 [객체 테이블(object table)](https://www.palantir.com/docs/foundry/workshop/widgets-object-table/) 위젯을 추가하고, 그 입력 변수를 새로 만든 [KNN 객체 집합](../../02_define-ontologies/04_functions/13_functions-on-objects/07_api-object-sets.md#k-nearest-neighbors-knn)으로 설정합니다.

![Workshop KNN 시맨틱 검색](https://www.palantir.com/docs/resources/foundry/ontology/knn-workshop-semantic.png)

더 맞춤화된 시맨틱 검색 로직이 필요하다면 [함수 섹션](#create-a-function-to-semantically-search-across-objects-for-use-in-workshop-andor-aip-logic)을 참고하세요.

**설명**: 이 구성에서 데이터 흐름은 다음 순서입니다. 사용자가 텍스트 입력 위젯에 문장을 입력하면, 그 값이 문자열 변수에 들어가고, KNN 객체 집합 변수가 이 문자열을 질의로 삼아 가장 가까운 K개 객체를 계산하며, 객체 테이블 위젯이 그 결과를 표로 보여 줍니다.

> **중간 요약**: Workshop에서는 객체 집합 변수에 임베딩 속성 기준 KNN 필터를 걸고, 텍스트 입력 위젯을 질의로, 객체 테이블 위젯을 결과 표시용으로 연결하면 코드 없이 시맨틱 검색이 됩니다. 단, 결과를 관련도 순으로 정렬할 수는 없습니다.

<a id="use-aip-chatbot-no-code"></a>
## AIP Chatbot 사용하기(노코드) (Use AIP Chatbot (no-code))

[AIP Chatbot Studio](https://www.palantir.com/docs/foundry/chatbot-studio/overview/)에서 만든 AIP Chatbot(이전 이름 AIP Agents)은 코드가 전혀 필요 없으므로 객체에 대한 시맨틱 검색을 시작하기에 좋습니다. [기능을 더 세밀하게 제어하면서 시맨틱 검색을 통합하는 방법](#create-a-function-to-semantically-search-across-objects-for-use-in-workshop-andor-aip-logic)도 알아보세요.

[시작하기(getting started)](https://www.palantir.com/docs/foundry/chatbot-studio/getting-started/) 가이드의 안내에 따라 AIP Chatbot을 만들고, [Ontology context](https://www.palantir.com/docs/foundry/chatbot-studio/retrieval-context/#ontology-context)를 추가하거나 **Ontology semantic search** [도구(tool)](https://www.palantir.com/docs/foundry/chatbot-studio/tools/#types-of-tools)를 추가합니다. 이 초기 설정만으로 AIP Chatbot에게 객체를 시맨틱 검색해 달라고 요청할 수 있습니다.

> **중간 요약**: AIP Chatbot에 Ontology context나 Ontology semantic search 도구를 붙이면 대화형으로 객체를 시맨틱 검색할 수 있습니다.

<a id="create-a-function-to-semantically-search-across-objects-for-use-in-workshop-andor-aip-logic"></a>
## Workshop 또는 AIP Logic에서 사용할, 객체를 시맨틱 검색하는 함수 만들기 (Create a function to semantically search across objects for use in Workshop and/or AIP Logic)

[함수 저장소(functions repository)](../../02_define-ontologies/04_functions/03_getting-started.md)를 만들고, 객체 타입을 조회하는 함수를 작성합니다. 목표는 사용자 입력을 받아 객체 타입에 대해 [KNN 검색](../../02_define-ontologies/04_functions/13_functions-on-objects/07_api-object-sets.md#k-nearest-neighbors-knn)을 실행하는 것입니다. TypeScript v1에서는 먼저 [앞에서 사용한](#generate-embeddings-and-create-object-type) 것과 같은 Palantir 제공 모델로 벡터를 생성합니다. Palantir 제공 모델을 TypeScript v1 함수로 가져오는 방법은 [TypeScript v1 함수의 언어 모델](../../02_define-ontologies/04_functions/14_models/04_language-models.md#embeddings)을 참고하세요. TypeScript v2와 Python은 아래 설명처럼 질의를 텍스트 그대로 받습니다.

**주의**: 함수에서 벡터 속성 사용 활성화하기(Enabling vector properties for functions). 진행하기 전에 Functions 코드 저장소의 `functions.json` 파일에 `"enableVectorProperties": true` 항목이 있는지 확인하세요. 이 항목이 없다면 `functions.json`에 추가하고 변경 사항을 커밋한 뒤 진행합니다. 추가 도움이 필요하면 Palantir 담당자에게 문의하세요.

`functions.json` 설정 파일은 TypeScript v1 저장소의 산출물입니다. TypeScript v2나 Python 저장소에 대해서는 이에 해당하는 벡터 속성 설정이 문서화되어 있지 않으므로, 이 항목이 그대로 적용된다고 가정하지 마세요. TypeScript v2나 Python 저장소에서 KNN 검색이 실패하면 Palantir 담당자에게 문의하세요.

<a id="example-semantic-search-function"></a>
### 시맨틱 검색 함수 예제 (Example semantic search function)

이 섹션의 코드 예제는 [TypeScript v1](../../02_define-ontologies/04_functions/12_typescript-v1/01_typescript-v1-getting-started.md), [TypeScript v2](../../02_define-ontologies/04_functions/10_typescript-v2/01_typescript-v2-getting-started.md), Python 함수 버전으로 제공되며, 사용하는 함수 버전에 맞는 탭을 선택하면 됩니다. TypeScript v1은 각 함수를 export된 클래스의 메서드로 정의하고, 그 메서드에 `@foundry/functions-api`의 `@Function()` 데코레이터를 붙이며, `Objects.search()`를 통해 온톨로지를 조회합니다. TypeScript v2는 `export default`로 함수를 정의하고, `@osdk/functions`에서 타입을 가져오며, 파라미터로 전달된 [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/) 클라이언트를 통해 온톨로지를 조회합니다. Python은 `@function` 데코레이터를 사용하고 함수 본문 안에서 Ontology SDK 클라이언트를 생성합니다. 전체 비교는 [TypeScript v1과 TypeScript v2 비교](../../02_define-ontologies/04_functions/02_language-feature-support.md#typescript-v1-vs-typescript-v2)를 참고하세요.

세 버전은 질의 임베딩을 어디서 만드는지, 그리고 함수를 어디에 정의해야 하는지가 다릅니다.

* **TypeScript v1**은 Palantir 제공 임베딩 모델로 질의를 직접 임베딩한 다음, 그 결과 벡터를 `nearestNeighbors`에 전달합니다. 함수는 export된 클래스의 메서드이며, 관례적으로 `functions-typescript/src/index.ts`에 정의합니다.
* **TypeScript v2**는 사용자의 텍스트를 `nearestNeighbors`에 그대로 전달합니다. `nearestNeighbors`는 질의 벡터와 질의 텍스트를 모두 받을 수 있습니다. 별도의 임베딩 호출이 필요 없으므로 두 단계였던 작업이 한 단계로 줄어듭니다. 함수는 `typescript-functions/src/functions` 디렉터리에 있는 파일의 default export여야 하고, 파일 이름은 함수 이름과 같아야 합니다. 전체 요구 사항은 [함수 작성하기](../../02_define-ontologies/04_functions/10_typescript-v2/01_typescript-v2-getting-started.md#write-a-function)를 참고하세요.
* **Python** 역시 [`nearest_neighbors`](https://www.palantir.com/docs/foundry/ontology-sdk/python-osdk-migration/#nearest-neighbor-object-set-filtering)를 통해 질의를 텍스트로 받습니다. 이 메서드는 베타 기능이므로 함수를 `@function(beta=True)`로 선언합니다.

TypeScript v1 예제가 `TextEmbeddingAda_002.createEmbeddings`로 하는 것처럼 임베딩을 별도 단계로 생성하는 방식은 TypeScript v2에 문서화된 대응 기능이 없습니다. 이 워크플로에서는 KNN 검색 중에 질의 텍스트가 임베딩되므로 그런 기능이 필요하지 않습니다. 다른 목적으로 TypeScript v2나 Python 함수에서 Palantir 제공 모델을 직접 호출하려면 [TypeScript v2 및 Python 함수의 언어 모델](../../02_define-ontologies/04_functions/14_models/03_language-models-python-tsv2.md)을 참고하세요.

이웃 개수 제한은 TypeScript 버전마다 다릅니다. TypeScript v1은 k 값을 `0 < K <= 100` 범위로 제한하고, TypeScript v2의 `numNeighbors` 인자는 `1`부터 `500`까지의 값을 받습니다.

TypeScript v1은 상위 k개 결과를 가져오기 전에 별도의 `.orderByRelevance()` 호출로 결과를 정렬합니다. TypeScript v2는 `fetchPage()`에 `$orderBy: "relevance"`를 전달해 관련도 순 정렬을 요청합니다. Python에는 문서화된 대응 기능이 없으며, 대신 검색에 전달한 이웃 개수가 결과 개수의 상한이 됩니다. Python의 [`nearest_neighbors`](https://www.palantir.com/docs/foundry/ontology-sdk/python-osdk-migration/#nearest-neighbor-object-set-filtering) 메서드가 반환하는 객체에는 `_score` 필드도 들어 있습니다.

아래의 TypeScript v2와 Python 예제는 TypeScript v1 예제와 같은 질의 텍스트와 이웃 개수를 받아 가장 가까운 객체들을 반환합니다. TypeScript v2 함수는 여기에 더해 첫 번째 파라미터로 Ontology SDK 클라이언트를 받습니다.

아래 각 코드 조각에서 `ObjectApiName`이 나오는 모든 곳을 여러분의 고유한 객체 타입으로 바꾸세요. 이 식별자는 첫 글자가 소문자인 `objectApiName` 형태로 나타나기도 합니다.

```typescript tab="TypeScript v1"
import { Function, Integer } from "@foundry/functions-api";
import { Objects, ObjectApiName } from "@foundry/ontology-api";
import { TextEmbeddingAda_002 } from "@foundry/models-api/language-models"

export class MyFunctions {
    @Function()
    public async findRelevantObjects(
        query: string,
        kValue: Integer,
    ): Promise<ObjectApiName[]> {
        if (query.length < 1) {
            return []
        }
        const embedding = await TextEmbeddingAda_002.createEmbeddings({inputs: [query]}).then(r => r.embeddings[0]);

        return Objects.search()
                    .objectApiName()
                    .nearestNeighbors(obj => obj.embeddings.near(embedding, {kValue: kValue}))
                    .orderByRelevance()
                    .take(kValue);
    }
}
```

**설명**: 이 함수는 질의 문자열 `query`와 반환 개수 `kValue`를 입력받아 가장 의미가 가까운 객체 배열을 반환합니다. 핵심은 두 줄입니다. `TextEmbeddingAda_002.createEmbeddings(...)` 줄이 질의 문자열을 데이터 쪽과 같은 ada-002 모델로 벡터화하고, `nearestNeighbors(obj => obj.embeddings.near(embedding, {kValue}))` 줄이 객체의 `embeddings` 속성과 그 벡터의 거리를 비교해 가까운 K개를 고릅니다. 이어서 `.orderByRelevance()`로 가까운 순서대로 정렬하고 `.take(kValue)`로 K개를 가져옵니다. 질의와 데이터를 반드시 같은 모델로 임베딩해야 거리 비교가 의미를 가집니다.

```typescript tab="TypeScript v2"
import { Client, Osdk } from "@osdk/client";
import { Integer } from "@osdk/functions";
import { ObjectApiName } from "@ontology/sdk";

export default async function findRelevantObjects(
    client: Client,
    query: string,
    kValue: Integer,
): Promise<Osdk.Instance<ObjectApiName>[]> {
    if (query.length < 1) {
        return [];
    }

    // nearestNeighbors가 질의 텍스트를 임베딩하므로 별도의 임베딩 호출이 필요 없습니다.
    const page = await client(ObjectApiName)
        .nearestNeighbors(query, kValue, "embeddings")
        .fetchPage({ $pageSize: kValue, $orderBy: "relevance" });

    return page.data;
}
```

**설명**: TypeScript v2 버전은 임베딩 단계가 사라집니다. `nearestNeighbors(query, kValue, "embeddings")`에 질의 텍스트, 이웃 개수, 검색할 벡터 속성 이름을 넘기면 내부에서 질의가 임베딩되고 검색이 수행됩니다. `fetchPage`의 `$orderBy: "relevance"`가 TypeScript v1의 `.orderByRelevance()` 역할을 합니다.

(원문에는 `client.ontology.objects.ObjectApiName.nearest_neighbors(query=..., num_neighbors=..., vector_property=...)`를 호출하는 같은 기능의 Python 예제 코드도 있습니다.)

이제 자연어로 객체를 조회하는 시맨틱 검색 함수가 준비되었습니다. 이 함수를 Foundry 어디에서나 사용할 수 있도록 [함수를 게시(publish)](../../02_define-ontologies/04_functions/03_getting-started.md#publish-your-functions)하는 것을 잊지 마세요.

<a id="use-semantic-search-functions-in-workshop"></a>
### Workshop에서 시맨틱 검색 함수 사용하기 (Use semantic search functions in Workshop)

1. 먼저 [Workshop 애플리케이션을 만듭니다](https://www.palantir.com/docs/foundry/workshop/getting-started/).
2. [텍스트 입력 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-text-input/)을 추가합니다. 이 위젯은 게시한 KNN 문서 조회 함수의 입력으로 쓰입니다.
3. [객체 목록(object list) 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-object-list/)을 추가하고, 입력으로 [함수에서 생성된 객체 집합](https://www.palantir.com/docs/foundry/workshop/functions-use/#function-backed-variables-in-workshop)을 지정한 뒤 아래와 같이 입력값을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology/semantic-search-workshop-function.png" alt="객체 집합을 생성하는 KNN 함수" width="450">

4. 이웃 개수(TypeScript에서는 `kValue`, Python에서는 `k_value`)를 원하는 결과 개수로 설정합니다. 이 값은 위에서 설명한 제한을 따릅니다. TypeScript v1은 추가로 [지정된 제한](../../02_define-ontologies/04_functions/13_functions-on-objects/07_api-object-sets.md#k-nearest-neighbors-knn)도 적용됩니다.

<a id="use-semantic-search-functions-in-aip-logic"></a>
### AIP Logic에서 시맨틱 검색 함수 사용하기 (Use semantic search functions in AIP Logic)

게시한 함수를 AIP Logic 안에서 [도구(tool)](https://www.palantir.com/docs/foundry/logic/getting-started/#use-a-logic-function)로 추가합니다. 그리고 다음과 비슷한 프롬프트로 언어 모델이 이 도구를 사용하도록 지시합니다.

```
Use the findRelevantObjects tool with a `kValue` of 5 to find the most related objects. Remember to add quotes around query when using the tool.
```

(번역: findRelevantObjects 도구를 `kValue` 5로 사용해 가장 관련 있는 객체를 찾으세요. 도구를 사용할 때 query 앞뒤에 따옴표를 붙이는 것을 잊지 마세요.)

> **중간 요약**: 함수 방식은 질의를 벡터로 바꾸고(TypeScript v1) 또는 텍스트 그대로(TypeScript v2, Python) KNN 검색을 실행해 관련도 순 결과를 돌려줍니다. 게시한 함수는 Workshop의 객체 목록 위젯 입력이나 AIP Logic의 도구로 쓸 수 있습니다.

## 정리

- 시맨틱 검색의 출발점은 Pipeline Builder의 Text to Embeddings로 텍스트를 벡터로 바꾸고, 이를 객체 타입의 `vector` 속성으로 저장하는 것입니다.
- 가장 간단한 방법은 Workshop에서 KNN 객체 집합(K는 1\~100)을 쓰는 것이지만, 관련도 순 정렬은 되지 않습니다.
- AIP Chatbot에 Ontology context나 Ontology semantic search 도구를 붙이면 코드 없이 대화형 검색이 가능합니다.
- 더 세밀한 제어가 필요하면 함수를 작성합니다. TypeScript v1은 질의를 직접 임베딩하고(k는 100 이하), TypeScript v2와 Python은 질의 텍스트를 그대로 넘깁니다(TypeScript v2의 k는 1\~500).
- 게시한 함수는 Workshop 위젯과 AIP Logic 도구에서 재사용할 수 있습니다.
