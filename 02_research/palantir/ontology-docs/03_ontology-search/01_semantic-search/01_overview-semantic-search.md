# 시맨틱 검색 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/ontology/overview-semantic-search/
- 사이드바 위치: Ontology search > Semantic search > Overview

이 페이지는 키워드가 아니라 의미를 기준으로 텍스트를 찾는 시맨틱 검색(semantic search)의 원리를 소개합니다. 텍스트를 임베딩(embedding)이라는 숫자 벡터로 바꾸고, 그 벡터를 온톨로지(Ontology) 객체와 연결해 검색 기반 업무 흐름에 활용하는 방식의 출발점이 되는 페이지입니다.

<a id="semantic-search"></a>
## 시맨틱 검색 (Semantic search)

시맨틱 검색은 키워드나 기타 전통적인 검색 방법에만 의존하지 않고, 텍스트의 본래 의미나 문맥을 기준으로 텍스트를 검색하는 방법입니다.

시맨틱 검색은 AI 모델을 사용해 텍스트를 벡터(숫자의 배열)로 변환하는 방식으로 이루어지며, 이 벡터를 "임베딩(embeddings)"이라고 부릅니다. 모델이 효과적이라면, 각각 크기가 N인 벡터들 가운데 N차원 공간에서 서로 가까이 있는 벡터들이 근본적인 의미, 즉 의미론적(semantic) 의미가 비슷한 벡터들입니다. 예를 들어 "face mask"의 임베딩 벡터는 "respirator"의 임베딩 벡터보다 "face covering"의 임베딩 벡터에 더 가깝습니다.

![임베딩 시각화.](https://www.palantir.com/docs/resources/foundry/ontology/aip-embeddings-visualization.png)

임베딩된 텍스트가 [온톨로지](../../01_ontology-building/01_overview.md)의 특정 객체와 연결되면, 검색 기반의 운영 워크플로가 훨씬 더 유용해집니다. 관련 엔터티를 찾거나 특정 검색어와 관련된 엔터티를 찾는 일은 N차원 공간에서 가장 가까운 벡터를 찾는 일이 됩니다.

**설명**: 키워드 검색은 문서에 "face mask"라는 글자가 있어야 찾습니다. 시맨틱 검색에서는 임베딩 모델이 "face mask"를 예를 들어 `[0.12, -0.40, 0.33, ...]`처럼 수백에서 수천 개의 실수로 이루어진 배열로 바꾸고, "face covering"도 비슷한 숫자 배열로 바꿉니다. 두 벡터 사이의 거리(주로 코사인 유사도나 유클리드 거리)를 계산하면 의미가 가까운 정도를 수치로 비교할 수 있습니다. 온톨로지에서는 예컨대 `Document` 객체 타입에 본문 텍스트 속성(property)과 그 임베딩 벡터 속성을 함께 두고, 검색어의 벡터와 가장 가까운 벡터를 가진 객체 k개를 찾는 식(k-최근접 이웃 검색, KNN)으로 활용합니다.

시맨틱 검색과 관련된 주제는 다음 문서 페이지를 참고하세요.

* [Palantir가 제공하는 모델로 시맨틱 검색 워크플로를 만드는 방법 알아보기](05_using-palantir-provided-models-to-create-a-semantic-search-workflow.md)
* [커스텀 모델로 시맨틱 검색 워크플로를 만드는 방법 알아보기](06_using-custom-models-to-create-a-semantic-search-workflow.md)
* [시맨틱 검색 워크플로에 청킹(chunking)을 적용하는 방법 알아보기](02_document-processing.md#chunking)
* [시맨틱 검색 워크플로에서 PDF를 사용하는 방법 알아보기](04_ontology-augmented-generation.md)
* 추가 학습 자료는 [YouTube 영상 "Building with Palantir AIP: Semantic Search" ↗](https://youtu.be/7rRLOTXe60Q)와 [블로그 글 "Building with Palantir AIP: Semantic Search" ↗](https://blog.palantir.com/building-with-palantir-aip-semantic-search-dc3adf40f6a6)를 참고하세요.

## 정리

- 시맨틱 검색은 키워드 일치가 아니라 의미와 문맥을 기준으로 텍스트를 찾습니다.
- AI 모델이 텍스트를 임베딩(숫자 벡터)으로 바꾸며, 의미가 비슷한 텍스트의 벡터는 N차원 공간에서 서로 가깝습니다.
- 임베딩을 온톨로지 객체와 연결하면, 관련 객체를 찾는 일이 가장 가까운 벡터를 찾는 일이 됩니다.
- 구체적인 워크플로 구성, 청킹, PDF 활용은 하위 문서에서 다룹니다.
