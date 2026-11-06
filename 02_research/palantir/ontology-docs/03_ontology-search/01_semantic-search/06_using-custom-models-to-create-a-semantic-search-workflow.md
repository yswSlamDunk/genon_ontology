# 커스텀 모델로 시맨틱 검색 워크플로 만들기 (Use custom models to create a semantic search workflow)

- 원문: https://www.palantir.com/docs/foundry/ontology/using-custom-models-to-create-a-semantic-search-workflow/
- 사이드바 위치: Ontology search > Semantic search > Use custom models to create a semantic search workflow

이 페이지는 Palantir가 제공하지 않는 임베딩 모델(직접 가져온 오픈소스 모델 등)로 시맨틱 검색 워크플로를 만드는 튜토리얼입니다. 모델로 문서 임베딩을 일괄 생성하고, 벡터 속성(property)을 가진 객체 타입을 만들고, 사용자 질의를 실시간으로 임베딩할 라이브 배포(live deployment)를 띄운 뒤, 함수(function)로 KNN 검색을 수행해 Workshop에서 쓰는 다섯 단계로 구성됩니다. Palantir 제공 모델을 쓰는 방식보다 단계가 많기 때문에, 각 단계가 왜 필요한지 이해하는 데 초점을 두고 읽으면 좋습니다.

**주의**: 이 튜토리얼은 Palantir가 제공하지 않는 임베딩 모델을 사용하는 경우를 위한 것이며, 이 방식은 더 이상 권장되는 워크플로가 아닙니다. [Palantir 제공 모델](https://www.palantir.com/docs/foundry/aip/supported-llms/) 목록과 [Palantir 제공 모델 시맨틱 검색 튜토리얼](05_using-palantir-provided-models-to-create-a-semantic-search-workflow.md)을 참고하세요.

이 페이지는 프롬프트가 주어졌을 때 관련 문서를 찾아 주는 가상의 엔드투엔드 문서 검색 서비스를 만드는 과정을 설명합니다. 이 서비스는 [Foundry 모델링 목표(modeling objective)](https://www.palantir.com/docs/foundry/model-integration/objectives/)를 사용해 문서를 임베딩하고 그 특징을 벡터로 추출합니다. 이 문서와 임베딩은 벡터 속성을 가진 객체 타입에 저장됩니다.

이 예제에서는 먼저 Foundry에 모델을 설정하고 임베딩을 생성하는 파이프라인을 만듭니다. 그다음 새 객체 타입을 만들고, 자연어로 이를 조회하는 함수를 작성합니다.

시작점은 파싱된 문서와 `Document_Content`, `Link` 같은 메타데이터가 들어 있는 데이터셋입니다. 다음으로 `Document_Content`에서 임베딩을 생성해 시맨틱 검색으로 조회할 수 있게 합니다.

![임베딩을 생성할 데이터셋](https://www.palantir.com/docs/resources/foundry/ontology/dataset-to-generate-embeddings.png)

KNN 기능의 세부 사항은 Foundry 문서의 [객체에 대한 KNN 함수(TSv1)](../../02_define-ontologies/04_functions/13_functions-on-objects/07_api-object-sets.md#k-nearest-neighbors-knn) 섹션을 참고하세요.

**팁**: 값 치환(Value substitution). 이 워크플로 전체에서 각 자리에 일관되게 쓰기만 한다면 원하는 값으로 바꿔 넣을 수 있습니다. 예를 들어 `ObjectApiName`이 나오는 모든 곳은 항상 `Document`로 바꿉니다.

치환해야 하는 값은 다음과 같습니다.

* `ObjectApiName`: 고유한 객체 타입(ObjectType)의 식별자이며, 이 예에서는 `Document`입니다. *참고:* 이 식별자는 첫 글자가 소문자인 `objectApiName` 형태로 나타나기도 합니다.
* `ModelApiName`: 모델(Model)을 감싸는 함수의 식별자입니다. *참고:* 이 식별자는 첫 글자가 소문자인 `modelApiName` 형태로 나타나기도 합니다.
* `OutputDatasetRid`: [임베딩 트랜스폼](#1-create-embeddings-using-models-in-foundry)의 출력 데이터셋 식별자입니다.
* `InputDatasetRid`: [임베딩 트랜스폼](#1-create-embeddings-using-models-in-foundry)의 입력 데이터셋 식별자입니다.
* `ModelRid`: [임베딩 트랜스폼](#1-create-embeddings-using-models-in-foundry)과 [라이브 모델링 배포 생성](#3-create-a-live-modeling-deployment)에 사용하는 모델의 식별자입니다.

**설명**: RID(Resource Identifier)는 Foundry에서 데이터셋, 모델 같은 리소스 하나하나를 유일하게 가리키는 식별 문자열입니다. 코드에서 `"InputDatasetRid"` 자리에 실제 데이터셋의 RID 문자열을 넣는다고 이해하면 됩니다.

<a id="1-create-embeddings-using-models-in-foundry"></a><a id="create-embeddings-using-models-in-foundry"></a>
## 1. Foundry에서 모델로 임베딩 만들기 (Create embeddings using models in Foundry)

Foundry에서 모델로 임베딩을 만드는 방법은 몇 가지가 있습니다. 이 예에서는 [가져온 오픈소스 모델](https://www.palantir.com/docs/foundry/integrate-models/import-huggingface-models/)과 상호작용하는 트랜스폼을 만듭니다. 사용할 모델은 `all-MiniLM-L6-v2`로, 384차원(크기)의 벡터를 만드는 범용 텍스트 임베딩 모델입니다. 이 모델은 [Foundry 온톨로지 `vector` 타입](../../02_define-ontologies/02_object-and-link-types/03_properties/05_property-metadata.md#property-base-types-with-limited-support)과 호환되는 벡터를 출력하는 다른 기존 모델로 교체할 수 있습니다. 새 오픈소스 모델을 가져오려면 [Hugging Face 모델 문서](https://www.palantir.com/docs/foundry/integrate-models/import-huggingface-models/)를 참고하세요.

아래 코드는 모델이 `text` 문자열 열을 가진 표 형태 입력과, `embedding`(실수 리스트) 열을 가진 표 형태 출력을 제공하는 API를 노출한다고 가정합니다. 모델 API를 정의하는 방법은 [모델 어댑터 API 문서](https://www.palantir.com/docs/foundry/integrate-models/model-adapter-api/)를 참고하세요.

```python
import palantir_models as pm


class EmbeddingModelAdapter(pm.ModelAdapter):
    ...

    @classmethod
    def api(cls):
        inputs = {
            "inference_data": pm.Pandas(columns=[("text", str)])
        }
        outputs = {
            "output_data": pm.Pandas(columns=[("text", str), ("embedding", list[float])])
        }
        return inputs, outputs
```

**설명**: 모델 어댑터의 `api()` 메서드는 모델의 입출력 형식을 선언합니다. 입력은 `inference_data`라는 이름의 Pandas 데이터프레임으로, `text` 문자열 열 하나를 가집니다. 출력은 `output_data`라는 데이터프레임으로, 원래 `text`와 그에 대한 `embedding`(실수 리스트) 열을 가집니다. 함수의 시그니처(파라미터 타입과 반환 타입)를 정하는 것과 같은 역할입니다.

아래 트랜스폼은 데이터를 모델에 통과시켜 `embedding`을 얻은 다음, 벡터 임베딩에 필요한 타입에 맞추기 위해 `embedding` 값(double 배열)을 float로 변환합니다.

몇 가지 고려할 점이 있습니다.

* `schema` 변수의 각 `StructField`는 처리된 입력 데이터셋(`InputDatasetRid`)에 있는 열 하나와, 모델이 추가한 `embedding` 열에 대응합니다.
* 대규모 데이터를 다룰 때 Pandas 데이터프레임이 지나치게 크면 트랜스폼이 실패할 수 있습니다. 이런 경우 트랜스폼을 Spark에서 수행해야 합니다.
* GPU(Graphics Processing Unit)를 활용하면 트랜스폼이 임베딩을 만드는 속도를 높일 수 있습니다. 트랜스폼에 `@configure` 데코레이터를 추가하면 GPU를 사용할 수 있습니다. 사용 중인 환경에서 이를 활성화하고 싶다면 Palantir 담당자에게 문의하세요.

예제 트랜스폼은 다음과 같습니다.

```python
from transforms.api import configure, transform, Input, Output
from palantir_models.transforms import ModelInput
from pyspark.sql.functions import pandas_udf, PandasUDFType
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, FloatType, ArrayType
import numpy as np


@configure(profile=["DRIVER_GPU_ENABLED"]) # 환경에서 GPU가 활성화되지 않았다면 이 줄을 삭제합니다
@transform(
    dataset_out=Output("OutputDatasetRid"),
    dataset_in=Input("InputDatasetRid"),
    embedding_model=ModelInput("ModelRid")
)
def compute(ctx, dataset_out, dataset_in, embedding_model):
    # 모델의 입력 열 이름에 맞춥니다
    spark_df = dataset_in.dataframe().withColumnRenamed("Document_Content", "text")

    def embed_df(df):
        # 임베딩 생성
        output_df = embedding_model.transform(df).output_data
        # float 배열로 변환
        output_df["embedding"] = output_df["embedding"].apply(lambda x: np.array(x).astype(float).tolist())
        # 불필요한 열 삭제
        return output_df.drop('inference_device', axis=1)

    # 갱신된 스키마
    schema = StructType([
        StructField("UID", IntegerType(), True),
        StructField("Category", StringType(), True),
        StructField("text", StringType(), True),
        StructField("Link", StringType(), True),
        StructField("embedding", ArrayType(FloatType()), True)
    ])

    udf = pandas_udf(embed_df, returnType=schema, functionType=PandasUDFType.GROUPED_MAP)
    output_df = spark_df.groupBy('UID').apply(udf)

    # 출력 DataFrame 쓰기
    dataset_out.write_dataframe(output_df)
```

**설명**: 이 트랜스폼은 입력 데이터셋을 읽어 임베딩 열이 추가된 출력 데이터셋을 씁니다. 동작 순서는 다음과 같습니다. (1) `Document_Content` 열 이름을 모델이 기대하는 `text`로 바꿉니다. (2) `embed_df` 함수가 Pandas 데이터프레임 조각을 받아 `embedding_model.transform(df)`로 모델을 실행하고, 결과의 `embedding` 값을 float 리스트로 바꿉니다. (3) `pandas_udf`와 `groupBy('UID').apply(udf)`로 Spark 데이터를 `UID`별 조각으로 나눠 `embed_df`를 적용합니다. (4) `schema`는 이 함수가 돌려주는 표의 열 구성(`UID`, `Category`, `text`, `Link`, `embedding`)을 Spark에 알려 줍니다. 결과적으로 입력 테이블의 각 행에 384개 실수로 이루어진 `embedding` 열이 붙은 테이블이 만들어집니다.

다음으로, 사용자 질의로부터 임베딩을 만들어 기존 벡터와 비교 검색하려면 라이브 모델링 배포(Live Modeling Deployment)가 필요합니다. 이 부분에서 쓰는 모델은 현재 단계에서 처음 임베딩을 생성할 때 사용한 모델과 같아야 합니다.

> **중간 요약**: 모델 어댑터로 입출력 형식을 정의하고, Python 트랜스폼으로 문서 텍스트 전체를 일괄 임베딩해 `embedding` 열을 가진 데이터셋을 만듭니다. 질의 임베딩에도 같은 모델을 써야 합니다.

<a id="2-create-object-type"></a><a id="create-object-type"></a>
## 2. 객체 타입 만들기 (Create object type)

이제 [첫 번째 단계](#1-create-embeddings-using-models-in-foundry)에서 배치 모델링 배포로 생성한 float 벡터 임베딩 열을 가진 새 데이터셋이 있어야 합니다. 다음으로 객체 타입을 만듭니다.

객체 타입 이름을 `Document`로 정하고, `embedding` 속성의 속성 타입을 `Vector`로 설정합니다. 이를 위해 두 가지 값을 설정해야 합니다.

1. **Dimension(차원):** `embedding` 열에 들어 있는 배열의 길이입니다.
2. **Similarity Function(유사도 함수):** 서로 다른 객체의 `embedding` 값 두 개 사이의 거리를 계산하는 방법입니다.

![새 벡터 속성 타입](https://www.palantir.com/docs/resources/foundry/ontology/vector-property-in-oma.jpg)

이 객체 타입을 만들고 나면 `Documentation` 객체들을 시맨틱 검색하는 데 사용할 수 있는 속성(`embedding`)이 생깁니다.

`ObjectApiName` 값은 객체 타입을 저장한 뒤에 확인할 수 있으며, 생성한 객체 타입의 설정 페이지에서 찾을 수 있습니다. 자세한 내용은 문서의 [객체 타입 만들기](../../02_define-ontologies/02_object-and-link-types/02_object-types/02_create-object-type.md#add-metadata-for-a-new-object-type) 섹션을 참고하세요.

**설명**: 이 예제에서는 `all-MiniLM-L6-v2` 모델이 384차원 벡터를 만들므로 Dimension은 384입니다. 유사도 함수로 많이 쓰이는 코사인 유사도는 두 벡터 사이 각도의 코사인 값으로, 방향이 같을수록 1에 가깝습니다. 벡터 길이가 1로 정규화되어 있으면 코사인 유사도는 두 벡터의 내적(각 원소를 곱해 더한 값)과 같습니다. 이 사실은 4단계의 임계값 예제에서 다시 쓰입니다.

> **중간 요약**: 임베딩 데이터셋으로 `Document` 객체 타입을 만들고, `embedding` 속성을 `Vector` 타입으로 지정하면서 차원(배열 길이)과 유사도 함수를 설정합니다.

<a id="3-create-a-live-modeling-deployment"></a><a id="create-a-live-modeling-deployment"></a>
## 3. 라이브 모델링 배포 만들기 (Create a Live Modeling Deployment)

객체가 임베딩을 속성으로 가지게 되었으니, 이제 사용자 질의에 대한 임베딩을 짧은 지연 시간으로 생성해야 합니다. 이 임베딩은 비슷한 임베딩 값을 가진 객체를 찾는 데 쓰입니다. 이를 위해 Functions에서 빠르고 지연 시간이 짧게 접근할 수 있는 라이브 모델 배포를 만듭니다.

[Modeling Objectives에서 라이브 배포를 설정하는 방법](https://www.palantir.com/docs/foundry/manage-models/set-up-live/) 또는 [모델에서 직접 설정하는 방법](https://www.palantir.com/docs/foundry/manage-models/create-a-model-deployment/)의 안내를 참고하세요. 그다음 해당 모델에 대한 [함수를 게시(publish)해야 합니다](https://www.palantir.com/docs/foundry/model-integration/model-functions-guide/).

**설명**: 1단계의 트랜스폼은 데이터셋 전체를 한 번에 처리하는 배치 작업이므로, 사용자가 검색창에 문장을 입력할 때마다 실행하기에는 적합하지 않습니다. 라이브 배포는 모델을 항상 실행 중인 서버로 띄워 두고 요청 하나가 들어오면 바로 임베딩을 돌려주는 방식이므로, 실시간 질의 처리에 필요합니다.

> **중간 요약**: 질의 문장을 즉시 임베딩하기 위해 같은 모델을 라이브 배포로 띄우고, 함수에서 호출할 수 있도록 모델 함수를 게시합니다.

<a id="4-create-an-embedding-with-functions-on-models"></a><a id="create-an-embedding-with-functions-on-models"></a>
## 4. Functions on Models로 임베딩 만들기 (Create an embedding with Functions on Models)

**주의**: 함수에서 벡터 속성 사용 활성화하기(Enabling vector properties for functions). 진행하기 전에 Functions 코드 저장소의 `functions.json` 파일에 `"enableVectorProperties": true`, `"enableResourceGeneration": true`, `"useDeploymentApiNames": true` 항목이 *모두* 있는지 확인하세요. 이 항목이 없다면 `functions.json`에 추가하고 변경 사항을 커밋한 뒤 진행합니다. 추가 도움이 필요하면 Palantir 담당자에게 문의하세요.

`functions.json` 설정 파일은 TypeScript v1 저장소의 산출물입니다. TypeScript v2 저장소에 대해서는 이에 해당하는 벡터 속성, 리소스 생성, 배포 API 이름 설정이 문서화되어 있지 않으므로 이 항목들이 그대로 적용된다고 가정하지 마세요. TypeScript v2 저장소에서 KNN 검색이 실패하면 Palantir 담당자에게 문의하세요.

이 섹션의 코드 예제는 [TypeScript v1](../../02_define-ontologies/04_functions/12_typescript-v1/01_typescript-v1-getting-started.md)과 [TypeScript v2](../../02_define-ontologies/04_functions/10_typescript-v2/01_typescript-v2-getting-started.md) 함수 버전으로 모두 제공되며, 한쪽 버전에만 있는 구성 요소는 설명 문장에서 따로 밝힙니다. 사용하는 함수 버전에 맞는 탭을 선택하세요. TypeScript v1은 각 함수를 export된 클래스의 메서드로 정의하며, 그 메서드는 `@foundry/functions-api`의 `@Function()` 데코레이터를 사용하고 `Objects.search()`로 온톨로지를 조회합니다. TypeScript v2는 각 함수를 자기 파일에서 `export default`로 정의하고, `@osdk/functions`에서 타입을 가져오며, 첫 번째 파라미터로 받은 [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/) 클라이언트로 온톨로지를 조회합니다. 전체 비교는 [TypeScript v1과 TypeScript v2 비교](../../02_define-ontologies/04_functions/02_language-feature-support.md#typescript-v1-vs-typescript-v2)를 참고하세요.

Python 함수도 [모델 함수](../../02_define-ontologies/04_functions/14_models/01_functions-on-models.md)와 시맨틱 검색을 지원하지만, 이 튜토리얼에는 Python 예제가 포함되어 있지 않습니다.

마지막 단계는 이 객체 타입을 조회하는 함수를 만드는 것입니다. 이 함수는 사용자 입력을 받아 [앞에서 만든](#3-create-a-live-modeling-deployment) 라이브 모델링 배포로 벡터를 생성합니다. 그런 다음 객체 타입에 대해 [KNN 검색(TSv1)](../../02_define-ontologies/04_functions/13_functions-on-objects/07_api-object-sets.md#k-nearest-neighbors-knn)을 실행합니다. 이웃 개수 범위를 포함한 TSv2와의 차이점은 아래 예제와 함께 설명합니다.
이 사용 사례에 맞는 예제 함수와 파일 구조는 아래와 같습니다.

벡터 속성에 대한 편집(edit)은 액션(Actions)과 함수(Functions)로 적용할 수 있습니다.

함수에서 모델을 사용하는 방법에 대한 자세한 내용은 [Functions on models 문서](../../02_define-ontologies/04_functions/14_models/01_functions-on-models.md)를 참고하세요.

<a id="file-structure"></a>
### 파일 구조 (File structure)

아래 파일 구조는 TypeScript v1 저장소 기준입니다.

```text
|-- functions-typescript
|   |-- src
|   |   |-- tests
|   |   |   |-- index.ts
|   |   |-- index.ts
|   |   |-- semanticSearch.ts
|   |   |-- service.ts
|   |   |-- tsconfig.json
|   |   |-- types.ts
|   |-- functions.json
|   |-- jest.config.js
|   |-- package-lock.json
|   |-- package.json
|-- version.properties
```

TypeScript v2 저장소는 구성이 다릅니다. 모든 함수는 `typescript-functions/src/functions` 안에 있는 자기 파일의 default export여야 하고, 파일 이름은 함수 이름과 같아야 합니다. 따라서 아래의 두 검색 함수는 각각 `typescript-functions/src/functions/fetchSuggestedDocuments.ts`와 `typescript-functions/src/functions/fetchSuggestedDocumentsWithThreshold.ts`가 됩니다. 공용 모듈인 `types.ts`와 `service.ts`는 `functions` 디렉터리 옆, 즉 `typescript-functions/src`에 둡니다. 전체 요구 사항은 [TypeScript v2 함수 시작하기](../../02_define-ontologies/04_functions/10_typescript-v2/01_typescript-v2-getting-started.md)를 참고하세요.

**설명**: 역할을 나누면 다음과 같습니다. `types.ts`는 모델 요청과 응답의 데이터 형태(인터페이스)를 정의하고, `service.ts`는 라이브 배포된 모델을 호출하는 코드를 담으며, `semanticSearch.ts`는 실제 검색 함수를 담고, `index.ts`는 TypeScript v1에서 함수 클래스를 외부에 등록합니다.

<a id="functions-typescriptsrctypests"></a>
### functions-typescript/src/types.ts

이 인터페이스들은 순수 TypeScript이므로 TypeScript v2에서도 그대로 쓸 수 있습니다. 단, `Double` 가져오기(import)만 `@foundry/functions-api`에서 `@osdk/functions`로 바뀝니다.

```typescript tab="TypeScript v1"
import { Double } from "@foundry/functions-api";

export interface IEmbeddingModel {
    embed: (content: string) => Promise<IEmbeddingResponse>;
}

export interface IEmbeddingResponse {
    text: string
    embedding: Double[]
    inference_device?: string
}

export interface IEmbeddingRequest {
    text: string
}
```

**설명**: `IEmbeddingModel`은 문자열을 받아 임베딩 응답을 돌려주는 `embed` 메서드를 가진 객체의 형태를 정의합니다. `IEmbeddingRequest`와 `IEmbeddingResponse`는 1단계 모델 어댑터에서 선언한 입력 열(`text`)과 출력 열(`text`, `embedding`)에 대응합니다.

(원문에는 첫 줄이 `import { Double } from "@osdk/functions";`인 것만 다른 TypeScript v2 버전 코드도 있습니다.)

<a id="functions-typescriptsrcservicets"></a>
### functions-typescript/src/service.ts

TypeScript v1은 가져온 모델 함수를 직접 호출합니다. TypeScript v2는 [온톨로지에 바인딩된 모델 함수(ontology-bound model function)](../../02_define-ontologies/04_functions/14_models/01_functions-on-models.md#ontology-or-space-bound-functions)가 필요하며, 이 함수는 생성된 Ontology SDK에서 가져와 `client(ModelApiName).executeFunction()`으로 호출합니다. `inference_data`와 `output_data` 키는 [1단계](#1-create-embeddings-using-models-in-foundry)에서 선언한 모델 API와 일치합니다. TypeScript v2에서는 Ontology SDK 클라이언트가 전역으로 주어지지 않으므로, 아래 서비스는 생성자에서 클라이언트를 받으며 `IEmbeddingModel` 인터페이스는 그대로 유지됩니다.

```typescript tab="TypeScript v1"
// 어느 네임스페이스에서 가져올지는 저장소의 Resource imports 사이드바에서 모델을 확인하세요
import { ModelApiName } from "@{YOUR_NAMESPACE_HERE}/models";
import { IEmbeddingRequest, IEmbeddingResponse } from "./types";

// 모델을 호출하는 서비스
export class EmbeddingService {
    public async embed(content: string): Promise<IEmbeddingResponse> {
        const request: IEmbeddingRequest = {
                                "text": content,
                            };
        return await ModelApiName([request])
                                 .then((output: any) => output[0]) as IEmbeddingResponse;
    }
}
```

**설명**: `embed`는 문자열 하나를 받아 `{ text: content }` 요청 객체를 만들고, 이를 배열에 담아 모델 함수 `ModelApiName`에 보냅니다. 모델은 요청 배열과 같은 길이의 응답 배열을 돌려주므로 `output[0]`으로 첫 번째(유일한) 응답을 꺼내 반환합니다.

(원문에는 생성자로 `client`를 받아 `this.client(ModelApiName).executeFunction({ "inference_data": [request] })`를 호출하고 `modelOutput.output_data[0]`을 반환하는 TypeScript v2 버전 코드도 있습니다.)

<a id="functions-typescriptsrcsemanticsearchts"></a>
### functions-typescript/src/semanticSearch.ts

TypeScript v1은 두 검색 함수를 하나의 export된 클래스의 메서드로 묶고, 공용 `private static dotProduct` 헬퍼를 둡니다. TypeScript v2에는 클래스가 없습니다. 각 함수는 자기 파일의 default export이며, 헬퍼는 그것을 사용하는 파일의 모듈 수준 함수가 됩니다.

K-최근접 이웃 호출 방식도 다릅니다. TypeScript v1은 콜백을 넘기고 옵션 객체에서 k 값을 읽은 뒤 `.orderByRelevance()`와 `.take()`를 이어 붙입니다. TypeScript v2는 질의 벡터, 이웃 개수, 벡터 속성 키를 세 개의 위치 인자로 `nearestNeighbors`에 넘긴 다음 `fetchPage`로 결과를 실제로 가져옵니다. TypeScript v2에는 `.take()` 메서드가 없습니다. 두 버전은 허용 범위도 다릅니다. TypeScript v1은 k 값을 `0 < K <= 100` 범위로 제한하고, TypeScript v2의 `nearestNeighbors` 메서드는 1\~500개의 이웃을 허용합니다. `nearestNeighbors`와 함께 관련도 순 정렬을 조합하는 방법이 문서화되어 있지 않으므로 TypeScript v2 예제에서는 관련도 정렬을 생략합니다.

아래 TypeScript v2 탭은 `typescript-functions/src/functions/fetchSuggestedDocuments.ts`의 내용입니다.

```typescript tab="TypeScript v1"
import { Function, Integer, Double } from "@foundry/functions-api";
import { Objects, ObjectApiName } from "@foundry/ontology-api";

import { EmbeddingService } from "./service";
import { IEmbeddingResponse, IEmbeddingModel } from './types';

export class SuggestedDocs {
    embeddingService: IEmbeddingModel = new EmbeddingService;

    @Function()
    public async fetchSuggestedDocuments(userQuery: string, kValue: Integer, category: string): Promise<ObjectApiName[]> {
        const embedding: IEmbeddingResponse = await this.embeddingService.embed(userQuery);
        const vector: Double[] = embedding.embedding;

        return Objects.search()
                      .objectApiName()
                      .filter(obj => obj.category.exactMatch(category))
                      .nearestNeighbors(obj => obj.embedding.near(vector, {kValue: kValue}))
                      .orderByRelevance()
                      .take(kValue);
    }

    /**
     * 다음은 유사도 임계값을 적용하는 fetchSuggestedDocuments의 대안입니다.
     * 임계값이 없으면 유사도와 상관없이 항상 kValue개의 문서가 반환됩니다.
     * 거리 계산 방식은 embedding 속성에 정의된 거리 함수에 따라 달라집니다.
     * 여기서는 코사인 유사도라고 가정하며, 임베딩 모델이 정규화된 벡터를 만든다면
     * 단순한 벡터 내적으로 계산할 수 있습니다.
     */
    @Function()
    public async fetchSuggestedDocumentsWithThreshold(userQuery: string, kValue: Integer, category: string, thresholdSimilarity: Double): Promise<ObjectApiName[]> {
        const embedding: IEmbeddingResponse = await this.embeddingService.embed(userQuery);
        const vector: Double[] = embedding.embedding;

        return Objects.search()
                      .objectApiName()
                      .filter(obj => obj.category.exactMatch(category))
                      .nearestNeighbors(obj => obj.embedding.near(vector, {kValue: kValue}))
                      .orderByRelevance()
                      .take(kValue)
                      .filter(obj => SuggestedDocs.dotProduct(vector, obj.embedding! as number[]) >= thresholdSimilarity);
    }

    private static dotProduct<K extends number>(arr1: K[], arr2: K[]): number {
        if (arr1.length !== arr2.length) {
            throw EvalError("Two vectors must be of the same dimensions");
        }
        return arr1.map((_, i) => arr1[i] * arr2[i]).reduce((m, n) => m + n);
    }
}
```

**설명**: `fetchSuggestedDocuments`는 사용자 질의, 반환 개수, 문서 카테고리를 입력받습니다. 먼저 `embeddingService.embed(userQuery)`로 라이브 배포된 모델을 호출해 질의 벡터를 얻고, `.filter(obj => obj.category.exactMatch(category))`로 지정한 카테고리의 문서만 남긴 뒤, `.nearestNeighbors(...)`로 그중 질의 벡터와 가장 가까운 K개를 고릅니다. SQL로 치면 `WHERE category = ?` 조건을 건 다음 거리 순으로 `LIMIT K` 하는 구조입니다. `fetchSuggestedDocumentsWithThreshold`는 여기에 마지막 `.filter(...)`를 더해, 질의 벡터와 문서 벡터의 내적(`dotProduct`)이 `thresholdSimilarity` 이상인 문서만 남깁니다. 예를 들어 K=5여도 유사도가 0.7 이상인 문서가 2개뿐이면 2개만 반환됩니다.

(원문에는 같은 기능을 TypeScript v2로 작성한 예제 코드도 있습니다. `client(ObjectApiName).where({ category: { $eq: category } }).nearestNeighbors(vector, kValue, "embedding").fetchPage({ $pageSize: kValue, $orderBy: "relevance" })`로 조회해 `page.data`를 반환합니다.)

TypeScript v2에서는 임계값 버전이 두 번째 파일 `typescript-functions/src/functions/fetchSuggestedDocumentsWithThreshold.ts`가 됩니다. TypeScript v1은 `.take()` 뒤에 JavaScript `.filter()`를 이어 붙여 임계값을 적용합니다. TypeScript v2는 대신 `fetchPage`가 반환한 `data` 배열을 필터링합니다. 이 예제는 `$select`로 가져올 속성을 좁히지 않으므로 `embedding`을 포함한 모든 기본 속성을 임계값 필터에서 사용할 수 있습니다. 불러오는 데이터 양을 줄이려고 `$select`를 추가한다면 목록에 `embedding`을 반드시 포함하세요.

(원문에는 `page.data.filter(obj => dotProduct(vector, obj.embedding! as number[]) >= thresholdSimilarity)`로 결과를 거르고 `dotProduct`를 모듈 수준 함수로 둔 TypeScript v2 임계값 버전 예제 코드가 더 있습니다.)

<a id="functions-typescriptsrcindexts"></a>
### functions-typescript/src/index.ts

이 재수출(re-export)은 TypeScript v1이 함수 클래스를 등록하는 방식이므로 TypeScript v2에는 대응하는 것이 없으며, 아래에는 TypeScript v1 탭만 있습니다. TypeScript v2는 `typescript-functions/src/functions` 안의 각 파일의 default export에서 함수를 찾아내므로 index 파일이 관여하지 않습니다.

```typescript tab="TypeScript v1"
export { SuggestedDocs } from "./semanticSearch";
```

> **중간 요약**: 함수 저장소에서 `types.ts`(데이터 형태), `service.ts`(라이브 모델 호출), `semanticSearch.ts`(카테고리 필터 + KNN 검색, 선택적으로 내적 기반 유사도 임계값)를 작성합니다. TypeScript v1은 클래스와 `index.ts` 재수출로 함수를 등록하고, TypeScript v2는 함수마다 별도 파일의 default export를 사용하며 k 범위(1\~500)와 정렬 방식도 다릅니다.

<a id="5-publish-the-function-and-use-in-an-example"></a><a id="publish-the-function-and-use-in-an-example"></a>
## 5. 함수 게시 및 예제에서 사용하기 (Publish the function and use in an example)

이제 자연어로 객체를 조회하는 시맨틱 검색 함수가 준비되었습니다. 마지막 단계는 [함수를 게시](../../02_define-ontologies/04_functions/03_getting-started.md#publish-your-functions)하고 워크플로에서 사용하는 것입니다. 문서 검색 예제를 이어서, 텍스트 입력으로 이 함수를 호출해 가장 잘 맞는 문서 두 개를 사용자에게 보여 주는 Workshop 애플리케이션을 만듭니다.

예제의 문서 서비스에 시맨틱 검색을 만드는 과정은 다음과 같습니다.

1. 먼저 [Workshop 애플리케이션을 만듭니다](https://www.palantir.com/docs/foundry/workshop/getting-started/).
2. [텍스트 입력(text input)](https://www.palantir.com/docs/foundry/workshop/widgets-text-input/)과 [문자열 선택기(string selector)](https://www.palantir.com/docs/foundry/workshop/widgets-string-selector/)를 추가합니다. 문자열 선택기는 필터로 사용할 문서 카테고리를 고르는 데 쓰입니다. 텍스트 입력과 문자열 선택기 모두 게시한 KNN 문서 조회 함수의 입력이 됩니다.
3. 마지막으로 [객체 목록(object list) 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-object-list/)을 추가하고, 함수에서 생성된 입력 객체 집합(object set)과 선택한 입력값을 아래와 같이 설정합니다.

![객체 집합을 생성하는 KNN 함수](https://www.palantir.com/docs/resources/foundry/ontology/knn-function-workshop-panel.png)

이제 입력값을 사용해 객체 타입의 문서를 시맨틱 검색하고 가장 관련 있는 두 개를 반환합니다. 이것은 벡터 속성과 시맨틱 검색의 간단한 사용 사례 하나일 뿐입니다. 완성된 Workshop 애플리케이션 예시는 아래 스크린숏에서 볼 수 있습니다.

![시맨틱 검색 Workshop 예시](https://www.palantir.com/docs/resources/foundry/ontology/completed-knn-workshop.png)

> **중간 요약**: 함수를 게시한 뒤 Workshop에서 텍스트 입력과 문자열 선택기를 함수 입력으로, 객체 목록 위젯을 결과 표시로 연결하면 카테고리별 문서 시맨틱 검색 화면이 완성됩니다.

## 정리

- 이 튜토리얼은 Palantir 제공 모델이 아닌 커스텀 임베딩 모델을 쓰는 방식이며, 현재는 권장되지 않습니다.
- 1단계에서 모델 어댑터와 Python 트랜스폼으로 문서 텍스트를 일괄 임베딩하고, 2단계에서 `Vector` 타입 속성(차원과 유사도 함수 설정)을 가진 `Document` 객체 타입을 만듭니다.
- 3단계에서 같은 모델을 라이브 배포로 띄워 질의를 실시간 임베딩할 수 있게 하고, 모델 함수를 게시합니다.
- 4단계에서 질의 임베딩, 카테고리 필터, KNN 검색, 선택적인 유사도 임계값 필터를 수행하는 함수를 작성합니다. TypeScript v1과 v2는 파일 구조, 클라이언트 사용, k 범위, 정렬 방식이 다릅니다.
- 5단계에서 함수를 게시해 Workshop 위젯과 연결합니다.
