# 멀티모달 모델과 임베딩 모델 선택하기 (Choose multimodal and embedding models)

- 원문: https://www.palantir.com/docs/foundry/ontology/aip-multimodal-and-embedding-models/
- 사이드바 위치: Ontology search > Semantic search > Choose multimodal and embedding models

이 페이지는 문서를 대상으로 시맨틱 검색(semantic search)을 구축할 때 어떤 모델을 골라야 하는지 안내합니다. 도표나 차트처럼 이미지가 섞인 문서를 다루는 비전(vision) 모델과, 텍스트를 벡터로 바꾸는 임베딩 모델 각각에 대해 쓰는 방법과 고르는 기준을 정리합니다.

이 페이지는 다이어그램, 차트, 표를 포함한 문서를 비롯해 문서에 대한 [시맨틱 검색](01_overview-semantic-search.md)용 모델을 고르는 지침을 제공합니다. 사용할 수 있는 모델은 시간이 지나며 바뀌고, 엔롤먼트(enrollment)마다 다릅니다. 지원되는 모델 목록은 [지원되는 대규모 언어 모델(LLM)과 임베딩 모델](https://www.palantir.com/docs/foundry/aip/supported-llms/)을 확인하세요.

**설명**: 엔롤먼트(enrollment)는 고객 조직마다 할당된 Foundry 환경 하나를 뜻합니다. 계약 조건이나 지역에 따라 엔롤먼트마다 쓸 수 있는 모델 목록이 다를 수 있다는 의미입니다.

<a id="multimodal-models"></a>
## 멀티모달 모델 (Multimodal models)

텍스트 전용 LLM은 이미지를 읽을 수 없습니다. 다이어그램, 차트 또는 다른 이미지에 대한 질문에 답하려면 비전 기능을 가진 모델을 사용하세요. 이런 모델을 찾으려면 [Model Catalog 홈페이지](https://www.palantir.com/docs/foundry/model-catalog/overview/#model-catalog-homepage)에서 **Type**으로 필터링하고 **Vision model**을 선택하세요.

비전 모델은 다음과 같은 방식으로 사용할 수 있습니다.

* **PDF 문서에서 텍스트 추출:** [AIP Document Intelligence](https://www.palantir.com/docs/foundry/document-intelligence/overview/)를 사용해, 배포하기 전에 광학 문자 인식(OCR)과 비전 언어 모델(VLM) 추출 전략을 비교합니다.
* **파이프라인에서 이미지 처리:** Pipeline Builder에서 미디어 참조(media reference) 열을 [**Use LLM** 노드](https://www.palantir.com/docs/foundry/pipeline-builder/pipeline-builder-llm/#vision)에 전달하고 **Vision** 라벨이 붙은 모델을 선택합니다.

추출한 텍스트를 시맨틱 검색에 사용한 다음, 일치하는 페이지 이미지와 질문을 비전 모델에 보낼 수도 있습니다. 이를 지원하려면 각 청크(chunk) 객체에 페이지 번호와 해당 페이지 이미지에 대한 [미디어 참조](https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-overview/#media-references)를 저장하세요. Python 변환(transform)으로 [PDF 페이지를 이미지로 변환](https://www.palantir.com/docs/foundry/transforms-python/media-set-transforms-api/#convert_document_to_images)할 수 있습니다.

**설명**: 마지막 문단의 흐름을 순서대로 쓰면 다음과 같습니다. (1) 사용자의 질문을 임베딩해 텍스트 청크 중 가장 가까운 것을 찾습니다. (2) 찾은 청크 객체에 저장된 페이지 번호와 페이지 이미지 참조를 읽습니다. (3) 그 페이지 이미지와 원래 질문을 함께 비전 모델에 보내 답을 받습니다. 검색은 값싼 텍스트로 하고, 표나 도표를 정확히 읽어야 하는 답변 단계에서만 이미지를 쓰는 구성입니다. 이를 위해 Chunk 객체 타입에 `page_number`, `page_image` 같은 속성을 미리 두어야 합니다.

> **중간 요약**: 이미지가 포함된 문서를 다루려면 비전 모델이 필요하며, Model Catalog에서 **Vision model**로 찾을 수 있습니다. 비전 모델은 PDF 텍스트 추출(Document Intelligence)이나 파이프라인 이미지 처리(**Use LLM** 노드)에 쓰고, 청크 객체에 페이지 번호와 페이지 이미지 참조를 저장해 두면 검색 후 해당 페이지 이미지를 비전 모델에 보낼 수 있습니다.

<a id="embedding-models"></a>
## 임베딩 모델 (Embedding models)

Palantir가 제공하는 임베딩 모델 사용을 권장합니다. 이 모델을 찾으려면 [Model Catalog 홈페이지](https://www.palantir.com/docs/foundry/model-catalog/overview/#model-catalog-homepage)에서 **Type**으로 필터링하고 **Embedding model**을 선택하거나, [지원되는 텍스트 임베딩 모델](https://www.palantir.com/docs/foundry/aip/supported-llms/#available-text-embedding-models)을 확인하세요. Palantir 제공 모델을 사용할 수 없다면 [자체 모델을 등록](https://www.palantir.com/docs/foundry/aip/bring-your-own-model/)하고 [**Text to embeddings**](https://www.palantir.com/docs/foundry/pipeline-builder/pipeline-builder-aip/#text-to-embeddings)에서 선택할 수 있습니다.

임베딩 모델을 고를 때는 다음 지침을 따르세요.

* **청크와 질의에 같은 모델 사용:** 청크에 사용한 것과 같은 모델로 질의를 임베딩합니다. 모델을 바꾸면 모든 청크를 다시 임베딩하세요.
* **청크를 모델의 입력 한도 안에 유지:** 모델의 토큰 한도는 해당 모델의 [Model Catalog 엔터티 페이지](https://www.palantir.com/docs/foundry/model-catalog/overview/#model-entity-page)에서 확인할 수 있습니다. [**Chunk string**](02_document-processing.md#chunking) 보드는 청크 크기를 문자 수로 설정합니다. 영어 텍스트에서 [토큰](https://www.palantir.com/docs/foundry/aip/aip-compute-usage/#tokens-in-aip) 하나는 평균 약 4자입니다. 다른 언어는 토큰당 문자 수가 더 적은 경우가 많으므로 여유를 더 두세요.
* **짧은 질의가 긴 본문과 일치하도록 돕기:** 짧은 질문과 그 질문에 답하는 본문은 서로 다른 종류의 텍스트이므로 임베딩이 가깝지 않을 수 있습니다. 이 차이를 줄이려면 [가상 문서 임베딩(HyDE, hypothetical document embeddings)](04_ontology-augmented-generation.md#hyde-hypothetical-document-embeddings)을 시도해 보세요.
* **자신의 데이터로 테스트:** 모든 문서를 임베딩하기 전에, 사용자가 검색하는 각 언어별로 문서와 질문 샘플을 가지고 후보 모델을 비교하세요. [AIP Evals](https://www.palantir.com/docs/foundry/aip-evals/overview/)를 사용해 시맨틱 검색 함수를 테스트할 수 있습니다.

텍스트 대신 이미지를 임베딩하려면 Pipeline Builder에서 비전 기능을 지원하는 임베딩 모델과 함께 [**Image to embeddings**](https://www.palantir.com/docs/foundry/pb-functions-expression/imageToEmbeddingsV1/) 표현식을 사용하세요.

**설명**: 첫 번째 지침이 중요한 이유는, 모델마다 벡터 공간이 다르기 때문입니다. 모델 A가 만든 벡터와 모델 B가 만든 벡터는 차원 수가 같더라도 각 좌표의 의미가 달라 거리를 비교하는 것 자체가 의미가 없습니다. 두 번째 지침의 계산 예: 토큰 한도가 512인 모델에 영어 기준으로는 약 512 x 4 = 2,048자까지 넣을 수 있지만, 한국어는 토큰당 문자 수가 더 적은 경우가 많으므로 청크 크기를 그보다 훨씬 작게 잡아야 잘리지 않습니다. 토큰(token)은 모델이 텍스트를 처리하는 최소 단위로, 단어보다 작은 조각인 경우가 많습니다.

> **중간 요약**: Palantir 제공 임베딩 모델을 우선 사용하고, 불가능하면 자체 모델을 등록합니다. 청크와 질의는 반드시 같은 모델로 임베딩하고, 청크 크기는 토큰 한도 안에 들도록(영어 약 4자/토큰, 다른 언어는 더 여유 있게) 잡으며, 짧은 질의에는 HyDE를 고려하고 실제 데이터로 AIP Evals 등을 써서 비교합니다.

## 정리

- 사용할 수 있는 모델은 시간과 엔롤먼트에 따라 다르므로 지원 모델 목록과 Model Catalog에서 확인합니다.
- 다이어그램, 차트 같은 이미지에는 비전 모델이 필요하며, Document Intelligence나 Pipeline Builder의 **Use LLM** 노드에서 사용합니다.
- 청크 객체에 페이지 번호와 페이지 이미지 참조를 저장하면, 텍스트로 검색한 뒤 해당 페이지 이미지를 비전 모델에 넘길 수 있습니다.
- 임베딩 모델은 청크와 질의에 같은 모델을 쓰고, 토큰 한도에 맞춰 청크 크기를 정하며, HyDE와 자체 데이터 기반 평가로 품질을 높입니다.
- 이미지 자체를 임베딩하려면 **Image to embeddings** 표현식을 사용합니다.
