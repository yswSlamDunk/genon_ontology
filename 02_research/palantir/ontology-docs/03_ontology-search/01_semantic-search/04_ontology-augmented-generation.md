# 온톨로지 증강 생성 (Ontology augmented generation)

- 원문: https://www.palantir.com/docs/foundry/ontology/ontology-augmented-generation/
- 사이드바 위치: Ontology search > Semantic search > Ontology augmented generation

이 페이지는 LLM에게 넘겨줄 관련 맥락(context)을 온톨로지에서 찾아오는 방법, 즉 검색 증강 생성(RAG, retrieval augmented generation)을 온톨로지 위에서 구현하는 방법을 다룹니다. 기본 시맨틱 검색 구성에서 시작해, 검색 품질이 부족할 때 쓰는 HyDE, 순위 기반 키워드 검색, 질의 증강, 하이브리드 검색(RRF) 기법을 TypeScript 함수 예제와 함께 설명합니다.

LLM은 비즈니스에 특화된 맥락에 적용될 때 엄청난 힘을 발휘합니다. 어떤 작업이 주어지면, 첫 단계는 거의 언제나 LLM에게 제공해야 할 관련 맥락을 찾는 것입니다. 관련 맥락을 찾는 일은 검색 증강 생성(retrieval augmented generation) 시스템을 설계할 때 가장 어려운 부분인 경우가 많습니다. 이 섹션은 맥락 검색(context retrieval)의 몇 가지 일반적인 접근 방식을 설명합니다. 유일한 "최선의 접근 방식"은 없다는 점에 유의하세요. 최선의 해법은 데이터의 구체적인 특성에 크게 좌우되기 때문입니다. 그러나 여기서 설명하는 주제들은 좋은 출발점이며, 상황에 맞게 수정하고 조합할 수 있습니다.

새로운 세대의 모델은 컨텍스트 길이가 늘어났기 때문에, 시맨틱 검색을 전혀 쓰지 않고 전체 맥락을 프롬프트에 넣을 수도 있습니다. 예를 들어 128,000토큰 컨텍스트 윈도는 300쪽이 넘는 텍스트에 해당합니다. 애플리케이션의 전체 맥락이 이 한도 안에 들어간다면, 검색 없이 시작하는 것을 권장합니다.

**설명**: RAG의 동작 순서는 다음과 같습니다. (1) 사용자의 질문을 받습니다. (2) 질문과 관련된 문서 조각(청크)을 데이터 저장소에서 검색합니다. (3) 검색한 청크를 질문과 함께 프롬프트에 넣어 LLM에 보냅니다. (4) LLM이 그 청크를 근거로 답합니다. LLM은 학습 데이터에 없는 회사 내부 문서를 모르므로, (2) 단계에서 올바른 청크를 찾아오지 못하면 (4)의 답도 틀립니다. 이 페이지 제목의 "온톨로지 증강"은 (2)의 검색 대상이 온톨로지 객체라는 뜻입니다. 컨텍스트 윈도(context window)는 LLM이 한 번에 입력으로 받을 수 있는 최대 토큰 수입니다.

<a id="basic-semantic-search"></a>
## 기본 시맨틱 검색 (Basic semantic search)

기본 시맨틱 검색을 만들려면 다음을 수행합니다.

1. [청킹](02_document-processing.md#chunking) 전략을 따릅니다.
2. [미디어 참조(media reference)](https://www.palantir.com/docs/foundry/data-integration/media-sets/) 속성을 가진 청크 객체를 만듭니다.
3. [시맨틱 검색 워크플로](05_using-palantir-provided-models-to-create-a-semantic-search-workflow.md)의 일부로 청크를 검색합니다.
4. Workshop에서 구성 옵션에 유의하며 [PDF Viewer 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-pdf-viewer/)을 사용합니다.

<a id="embeddings"></a>
## 임베딩 (Embeddings)

임베딩에 대한 자세한 내용은 [Palantir 제공 모델을 사용해 시맨틱 검색 워크플로를 만드는 방법에 대한 문서를 확인하세요.](05_using-palantir-provided-models-to-create-a-semantic-search-workflow.md#generate-embeddings-and-create-object-type)

<a id="retrieval"></a>
## 검색 (Retrieval)

검색에 대한 자세한 내용은 [Palantir 제공 모델을 사용해 시맨틱 검색 워크플로를 만드는 방법에 대한 문서를 확인하세요.](05_using-palantir-provided-models-to-create-a-semantic-search-workflow.md#create-a-function-to-semantically-search-across-objects-for-use-in-workshop-andor-aip-logic)

> **중간 요약**: 전체 맥락이 컨텍스트 윈도(예: 128,000토큰, 300쪽 이상) 안에 들어가면 검색 없이 시작하는 것이 좋습니다. 기본 시맨틱 검색은 청킹, 미디어 참조 속성을 가진 청크 객체 생성, 시맨틱 검색, Workshop의 PDF Viewer 위젯 표시 순서로 구성하며, 임베딩과 검색의 세부 내용은 별도 문서에 있습니다.

<a id="advanced-retrieval"></a>
## 고급 검색 (Advanced retrieval)

AIP 관련 도구가 문서 코퍼스(corpus)에 있어야 할 질문에 답하지 못한다면, 먼저 관련 맥락이 검색되어 프롬프트에 전달되었는지 조사해야 합니다. 가장 관련성 높은 맥락을 찾아내지 못하는 것은 대개 검색 단계이며, 이 때문에 다음 단계에서 LLM이 적절하게 응답하지 못하게 됩니다.

데이터와 질의의 내용에 따라 검색을 개선하는 방법은 많이 있으며, 그중 일부는 아래와 같습니다.

* **HyDE (Hypothetical Document Embeddings, 가상 문서 임베딩)**
* **순위 기반 키워드 검색(Ranked keyword-based search)**
* **질의 증강(Query augmentation)**
* **하이브리드 검색(Hybrid search)**

<a id="technique-consideration"></a>
### 기법 선택 시 고려 사항 (Technique consideration)

이는 결국 구체적인 사용 사례의 요구 사항과 얼마나 많은 시간을 투자할 의향이 있는지에 달려 있습니다. 사용 사례에 따라서는 처음의 단순한 구성으로도 충분히 잘 동작할 수 있습니다. 그렇지 않다면 HyDE와 시맨틱 청킹만 추가하고 나머지는 그대로 두면 될 수도 있습니다. 권장 사항은 기본 구현으로 시작한 다음, 필요해질 때 기능을 추가하는 것입니다.

**설명**: 디버깅 순서로 정리하면, LLM의 답이 틀렸을 때 바로 프롬프트를 고치기보다 (2) 검색 단계에서 반환된 청크 목록을 먼저 확인합니다. 정답이 담긴 청크가 목록에 없다면 문제는 검색이고, 있는데도 답이 틀렸다면 문제는 프롬프트나 모델입니다.

<a id="hyde-hypothetical-document-embeddings"></a><a id="가상-문서-임베딩-hypothetical-document-embeddings"></a>
### HyDE (가상 문서 임베딩, Hypothetical document embeddings)

검색 성능을 개선하는 한 가지 방법은 HyDE, 즉 가상 문서 임베딩입니다. 핵심 아이디어는 질의를 직접 임베딩하는 대신, 먼저 LLM에게 이 질문에 답하는 가상의 청크를 만들게 한 다음 그것을 임베딩하는 것입니다. 직관적으로 이는 질의와 그 답 사이의 비대칭을 상쇄하는 데 도움이 됩니다. 관련 학술 논문 ["Precise Zero-Shot Dense Retrieval without Relevance Labels" ↗](https://arxiv.org/abs/2212.10496)도 참고할 수 있습니다.

이 방법은 청크가 [원본 문서와 장(chapter)](02_document-processing.md#chunking)을 인코딩하도록 특정 형식으로 구성된 경우에 특히 유용할 수 있습니다.

예를 들어 "동물 충돌은 어떻게 처리합니까?(How do we deal with animal collisions?)"라는 질문에 대한 적절한 답으로 다음 청크를 생각해 봅시다.

```
Claim Management - Motor: Animal Collision:
Animal collision claims are generally covered in type A, B, D policies. However,
exclusions apply...
```

먼저 LLM에게 다음과 같이 가상의 청크를 생성하도록 프롬프트를 줍니다.

```
You are an insurance specialist assistant tasked to assist your colleagues with
finding relevant documents for their queries.

Given the following user query:
{query}

Produce a hypothetical paragraph answering it. Give your response in the following
format:
{Document Name}: {Chapter name}: {Section} > ...
{Content}

where {Document Name} is the name of the document that contains the passage,
{Chapter name} is the name of the chapter, {Section} is the name of the section
and {Content} is the content of the section.
```

**설명**: 프롬프트의 요지는 "당신은 보험 전문가 보조입니다. 다음 사용자 질의 `{query}`에 답하는 가상의 문단을 `{문서 이름}: {장 이름}: {절} > ...` 다음 줄에 `{내용}` 형식으로 만들어 주세요"입니다. 실제 청크와 같은 머리말 형식을 요구하는 것이 핵심입니다.

이 프롬프트는 다음과 같은 응답을 돌려줍니다.

```
Animal Claims Management: General Terms:
Animal collision is commonly insured in fully comprehensive packages...
```

LLM의 응답은 이미 (구조적으로) 실제 답에 "더 가깝기" 때문에, 그 임베딩도 실제 답을 담은 청크에 더 가까워집니다. 함수에서 시맨틱 검색은 다음과 같이 작성합니다.

```TypeScript
async searchChunksByEmbedding(query: string, k: Integer): Promise<Chunk[]> {
   // 가상 청크 생성을 위한 전체 프롬프트를 만듭니다
   const prompt = `...`

   // 가상 청크를 생성합니다
   const hypothetical = await GPT_4o.createChatCompletion({messages: [{"role": "user", "contents": [{"text": prompt}]}]})
   // 결과를 임베딩합니다
   const embedding = await TextEmbeddingAda_002.createEmbeddings({inputs: [hypothetical]})
   // 그 임베딩으로 최근접 이웃 검색을 합니다
   const docs = Objects.search()
                    .chunks()
                    .nearestNeighbors(chunk => chunk.vectorProperty.near(embedding, {kValue: k})
                    .orderByRelevance()
                    .takeAsync(k)
   return docs
```

**설명**: 입력은 질의 문자열 `query`와 반환할 청크 수 `k`이고, 출력은 `Chunk` 객체 배열입니다. 처리 순서는 (1) `GPT_4o.createChatCompletion`으로 가상 청크 텍스트 생성, (2) `TextEmbeddingAda_002.createEmbeddings`로 그 텍스트를 벡터로 변환, (3) `Objects.search().chunks().nearestNeighbors(...)`로 Chunk 객체의 벡터 속성 중 그 벡터와 가장 가까운 k개를 찾기입니다. 일반 시맨틱 검색과의 차이는 (2)에서 질의 대신 가상 청크를 임베딩한다는 점 하나뿐입니다. "질의와 답의 비대칭"이란, "동물 충돌은 어떻게 처리합니까?" 같은 짧은 의문문과 "Claim Management - Motor: ..."로 시작하는 긴 서술문은 문장 형태가 달라 벡터도 멀어지기 쉽다는 뜻입니다.

> **중간 요약**: 답을 못 할 때는 먼저 검색 단계에서 올바른 맥락이 왔는지 확인하고, 기본 구현에서 시작해 필요할 때 기법을 더합니다. HyDE는 LLM이 만든 가상의 답 청크를 임베딩해 검색함으로써 짧은 질의와 긴 답 본문 사이의 형태 차이를 줄입니다.

<a id="ranked-keyword-based-search"></a>
### 순위 기반 키워드 검색 (Ranked keyword-based search)

OpenAI Ada 같은 범용 임베딩 모델은 다양한 데이터로 이루어진 대규모 코퍼스로 학습되었습니다. 사용 사례가 도메인 특화 코퍼스(예: 제조)에 대한 검색을 요구한다면, 검색이 기대만큼 잘 동작하지 않을 수 있습니다. 범용 임베딩 모델이 특정 도메인에 대해 임베딩 공간의 작은 부분만 사용하기 때문입니다.

이런 경우 검색을 개선하는 한 가지 방법은 사용자 정의 모델을 파인튜닝하는 것이지만, 훨씬 간단한 기본 제공 해법은 순위 기반 키워드 검색을 사용하는 것이며, 필요하면 LLM 전처리를 함께 씁니다.

Object Storage v2가 동작하는 기반 인덱스(index)는 질의가 주어졌을 때 이미 "관련성(relevance)" 개념을 갖추고 있기 때문입니다. 이 관련성은 *다른 청크에 상대적*이므로, 청크의 도메인 특화 맥락을 자동으로 고려합니다.

객체 기반 함수(Functions on Objects)는 객체 질의 결과를 이 관련성으로 정렬하는 기능을 지원하므로, 다음과 같은 함수를 작성할 수 있습니다.

```TypeScript
async searchChunksByKeywords(query: string, k: Integer): Promise<Chunk[]> {
    const chunks = Objects.search()
                    .chunks()
                    .filter(chunk => chunk.text.matchAnyToken(query))
                    .orderByRelevance()
                    .takeAsync(k)
    return chunks
}

```

**설명**: `matchAnyToken(query)`는 질의의 단어(토큰) 중 하나라도 청크의 `text` 속성에 들어 있으면 일치로 보는 필터이고, `orderByRelevance()`는 검색 인덱스가 계산한 관련성 점수 순으로 정렬합니다. 이런 관련성 점수는 검색 엔진에서 흔히 쓰는 TF-IDF나 BM25 계열 방식처럼, 전체 문서에서 드물게 나오는 단어가 일치할수록 높아지는 경향이 있습니다. "다른 청크에 상대적"이라는 원문 표현이 이 성질을 가리킵니다. 예를 들어 제조 문서 전체에 "공정"이라는 단어가 흔하다면 그 단어 일치는 점수를 적게 올리고, 드문 부품 번호 일치는 점수를 많이 올립니다.

그러나 이 방법은 시맨틱 검색의 의미적 요소를 없애 버립니다. 예를 들어 사용자가 "**사슴(deer)** 충돌은 어떻게 처리합니까?"라고 묻고 그 질문을 그대로 함수에 넣으면, **동물(animal)** 충돌 일반을 다루는 청크는 찾지 못합니다. LLM은 아래에서 설명하는 [질의 증강](#query-augmentation)을 통해 의미적 요소를 다시 들여올 수 있습니다.

> **중간 요약**: 범용 임베딩 모델이 도메인 특화 문서에서 잘 동작하지 않을 때는, Object Storage v2 인덱스의 관련성 점수로 정렬하는 키워드 검색(`matchAnyToken` + `orderByRelevance`)이 간단한 대안입니다. 다만 단어가 정확히 일치해야 하므로 의미적 검색 능력이 사라지며, 이를 질의 증강으로 보완합니다.

<a id="query-augmentation"></a>
### 질의 증강 (Query augmentation)

질의 전처리는 반환되는 결과의 관련성을 최대화하는 중요한 단계입니다. 본질적으로, 검색 유형에 따라 사용자 질의를 핵심 구성 요소로 압축하려는 것입니다. [질의 보강(query enriching)](#query-enriching)과 [질의 추출(query extraction)](#query-extraction)을 고려할 수 있습니다.

<a id="query-enriching"></a>
#### 질의 보강 (Query enriching)

사용자 질의와 키워드 검색에 전달되는 값 사이에 LLM 단계를 넣으면, 질의를 압축해 더 관련성 있게 만들 수 있습니다. LLM에게 불용어(stopword)와 무관한 군더더기 표현("\~를 찾아 주세요")을 제거하고, 관련 단어나 동의어를 추가하도록 프롬프트를 줄 수 있습니다.

다음과 같은 프롬프트를 구성할 수 있습니다.

```
You are an insurance AI assistant tasked to help users find relevant documents.
To do so, you can use keyword-search in the company's internal database.

Given the following user query: {query}

Give a list of search terms that would find relevant results. Be sure to remove stop words,
and add synonyms and related terms to the most important terms.
Give your answer as a list of comma-separated values.
```

**설명**: 프롬프트의 요지는 "회사 내부 데이터베이스에서 키워드 검색을 할 수 있는 보험 AI 보조로서, 사용자 질의 `{query}`에 대해 관련 결과를 찾을 검색어 목록을 쉼표로 구분해 주되, 불용어는 빼고 중요한 단어에는 동의어와 관련어를 더하라"입니다.

예시 질문 "How do we deal with animal collisions?"에 대한 LLM의 응답은 다음과 같습니다.

```
deer, animal, collision, claims, wildlife, accidents, vehicle, damage, car, insurance, policy, coverage, comprehensive, reimbursement
```

이렇게 하면 사용자는 "사슴 충돌(deer collisions)"이라는 말이 한 번도 나오지 않는 문서뿐 아니라, "동물(animal)", "야생 동물(wildlife)", "사고(accidents)" 일반을 다루는 문서도 찾을 수 있습니다.

(원문에는 이 보강된 질의를 `matchAnyToken`에 넣어 관련성 순으로 k개를 가져오는 `searchChunksByAugmentedKeywords` 예제 코드가 더 있습니다. 앞의 `searchChunksByKeywords`에 `GPT_4o.createChatCompletion` 호출 한 줄을 앞에 붙이고, 원래 질의 대신 LLM이 만든 검색어 목록을 필터에 넘기는 구조입니다.)

<a id="query-extraction"></a>
#### 질의 추출 (Query extraction)

질의 증강은 관련성 순으로 정렬하는 키워드 검색에 잘 맞습니다. 그러나 시맨틱 검색에서는 사용자 질의의 핵심 요구를 추출해야 하며, 그렇게 하면서 불용어처럼 의미를 주지 않는 군더더기 단어를 제거하고, 필요하면 질의어를 [표제어 추출(lemmatize)하거나 어간 추출(stem) ↗](https://keremkargin.medium.com/nlp-tokenization-stemming-lemmatization-and-part-of-speech-tagging-9088ac068768)해야 합니다.

이를 위해 질의 추출을 수행해 질문을 사용자의 핵심 요구로 변환합니다.

예시 프롬프트는 다음과 같습니다.

```
You are preparing a user-given query in order to perform a semantic search.
Extract the key user actions from the given query, removing unnecessary stop words
in the process.

Given the following user query: {query}

Return concatenated actions delimited by full stops.
```

**설명**: 프롬프트의 요지는 "시맨틱 검색을 위해 질의를 준비하는 중이니, 사용자 질의 `{query}`에서 불필요한 불용어를 빼고 핵심 행동을 추출해 마침표로 구분해 이어 붙여 달라"입니다.

예시 질문 "How do we deal with animal collisions?"에 대해 LLM은 다음을 반환합니다.

```
Deal with animal collisions.
```

이 응답은 질의의 의미 내용을 최대화하고, 이후 시맨틱 검색을 실행했을 때 더 강하게 일치할 가능성을 높입니다. 위 예시는 불용어 제거만으로도 해결할 수 있습니다.

(원문에는 추출된 질의를 `TextEmbeddingAda_002.createEmbeddings`로 임베딩한 뒤 `nearestNeighbors`로 가장 가까운 청크를 찾는 `searchChunksByExtractedQuery` 예제 코드가 더 있습니다. HyDE 예제와 구조가 같고, 임베딩하는 대상이 가상 청크가 아니라 추출된 핵심 요구라는 점만 다릅니다.)

**설명**: 두 기법의 방향은 반대입니다. 키워드 검색용 질의 보강은 단어를 늘려(동의어, 관련어 추가) 일치할 기회를 넓히고, 시맨틱 검색용 질의 추출은 단어를 줄여(불용어 제거) 벡터가 핵심 의미에 집중하게 합니다. 불용어(stopword)는 "how", "do", "we", "the"처럼 거의 모든 문장에 나와 검색에 정보를 주지 않는 단어입니다. 어간 추출(stemming)은 "collisions"를 "collis"처럼 접미사를 잘라 내는 규칙 기반 처리이고, 표제어 추출(lemmatization)은 "collisions"를 사전형 "collision"으로 바꾸는 처리입니다.

> **중간 요약**: 질의 증강은 검색 전에 LLM으로 질의를 다듬는 단계입니다. 키워드 검색에는 불용어를 빼고 동의어와 관련어를 더하는 질의 보강을, 시맨틱 검색에는 핵심 요구만 남기는 질의 추출을 사용합니다.

<a id="hybrid-search-combining-semantic-and-keyword-search-with-reciprocal-rank-fusion-rrf"></a>
#### 하이브리드 검색: 상호 순위 융합(RRF)으로 시맨틱 검색과 키워드 검색 결합하기 (Hybrid search: Combining semantic and keyword search with reciprocal rank fusion (RRF))

상호 순위 융합(RRF, reciprocal rank fusion)은 여러 검색 유형의 결과를 하나의 목록으로 합치는 간단한 알고리즘입니다. 본질적으로, 어떤 목록에서 순위가 높을수록 문서에 더 높은 점수를 줍니다. 총점은 모든 목록에 걸친 점수의 합입니다.

`k`는 정규화 항(regularizer) 역할을 합니다. k가 클수록 문서가 목록의 *어디에* 나오는지는 덜 중요해지고, 목록에 *나오는지* 자체만 중요해집니다.

```
`RRFscore(d ∈ D) = Σ [1 / (k + r(d))]`

`# k is a constant that helps to balance between high and low ranking.`
`# r(d)is the rank/position of the document`
```

**설명**: 수식은 "문서 d의 RRF 점수는 각 결과 목록에서 1 / (k + d의 순위)를 구해 모두 더한 값"이라는 뜻입니다. 주석은 "k는 높은 순위와 낮은 순위 사이의 균형을 잡는 상수, r(d)는 문서의 순위(위치)"라는 의미입니다. 구체적인 계산 예로 k = 60, 순위를 0부터 센다고 합시다. 청크 A가 벡터 검색 0위, 키워드 검색 2위라면 점수는 1/60 + 1/62 = 약 0.0328입니다. 청크 B가 벡터 검색 1위에만 나온다면 1/61 = 약 0.0164입니다. 두 목록 모두에 나온 A가 위로 올라갑니다. k가 60처럼 크면 0위(1/60)와 5위(1/65)의 점수 차이가 작아서, "여러 목록에 나왔는가"가 순위보다 더 큰 영향을 줍니다. 이 방식은 두 검색의 원래 점수(벡터 거리와 키워드 관련성)가 서로 다른 척도라서 직접 더할 수 없을 때, 순위만으로 합칠 수 있다는 장점이 있습니다.

```TypeScript
public combineResultsWithRRF(vectorSearchResults: Chunk[], keywordSearchResults: Chunk[], k: Integer = 60): Chunk[] {

    // RRF 점수 함수를 정의합니다
    const RRF = (r: number, k: number) => 1 / (r + k);

    // 각 청크의 점수를 추적할 맵을 초기화합니다
    // 이후 각 Chunk에 문자열 기본 키 속성 "id"가 있다고 가정합니다
    const resultMap: Map<string, {chunk: Chunk, score: number}> = new Map();
    const combinedResults: Chunk[] = [];

    const searchResultsList = [vectorSearchResults, keywordSearchResults];

    searchResultsList.forEach((searchResults) => {
        searchResults.forEach((chunk, rank) => {
            // 목록의 각 Chunk에 대해 점수를 계산하고
            // 맵에 있는 그 Chunk의 총점에 더합니다
            const rrfScore = RRF(rank, k);
            const chunkData = resultMap.get(chunk.id) || {chunk: chunk, score: 0};

            chunkData.score += rrfScore;
            resultMap.set(chunk.id, chunkData);
        });
    });

    // 모든 Chunk를 목록으로 모읍니다
    resultMap.forEach((chunkData) => {
        combinedResults.push(chunkData.chunk);
    });

    // resultMap의 점수 기준으로 내림차순 정렬합니다
    combinedResults.sort((a, b) => resultMap.get(b.id).score - resultMap.get(a.id).score);

    return combinedResults;
}
```

**설명**: 입력은 벡터 검색 결과 배열과 키워드 검색 결과 배열(각각 관련성 순으로 정렬됨), 상수 `k`이고, 출력은 RRF 총점 내림차순으로 정렬된 합쳐진 배열입니다. 핵심은 `resultMap`으로, 청크의 기본 키 `id`를 키로 삼아 같은 청크가 두 목록에 모두 나오면 점수가 누적되도록 합니다. `forEach((chunk, rank) => ...)`의 두 번째 인자가 배열 인덱스이므로 순위가 0부터 매겨집니다. 이 방식은 해시 맵을 쓰므로 전체 결과 수를 n이라 할 때 점수 누적은 O(n), 정렬은 O(n log n)입니다.

전체 하이브리드 검색 구현은 다음과 같습니다.

(원문에는 `hybridSearch(query, k, n1, n2)` 예제 코드가 더 있습니다. `searchChunksByKeywords(query, n1)`과 `searchChunksByEmbedding(query, n2)`를 동시에 시작해 `Promise.all`로 두 결과를 기다린 뒤, `combineResultsWithRRF`로 합치고 상위 `k`개를 `slice(0, k)`로 잘라 반환합니다. 두 검색을 병렬로 실행하므로 전체 지연 시간은 둘 중 느린 쪽에 맞춰집니다.)

> **중간 요약**: 하이브리드 검색은 키워드 검색과 시맨틱 검색을 병렬로 실행한 뒤 RRF로 합칩니다. RRF는 각 목록에서 1 / (k + 순위)를 더하는 방식이라 점수 척도가 다른 검색 결과도 순위만으로 합칠 수 있고, 여러 목록에 나오는 청크가 위로 올라갑니다.

## 정리

- 온톨로지 증강 생성은 LLM에 넘길 맥락을 온톨로지 객체(청크)에서 검색해 오는 RAG 방식이며, 맥락이 컨텍스트 윈도에 다 들어가면 검색 없이 시작하는 것이 좋습니다.
- 기본 구성은 청킹, 미디어 참조를 가진 청크 객체, 시맨틱 검색, Workshop PDF Viewer로 이루어집니다.
- 답이 틀리면 먼저 검색 단계가 올바른 맥락을 가져왔는지 확인하고, 기본 구현에서 출발해 필요한 기법만 더합니다.
- HyDE는 가상 답 청크를 임베딩해 질의와 답의 형태 차이를 줄이고, 순위 기반 키워드 검색은 도메인 특화 문서에 강하지만 의미 검색 능력이 없습니다.
- 질의 보강(키워드 검색용)과 질의 추출(시맨틱 검색용)로 질의를 다듬고, 하이브리드 검색은 두 검색 결과를 RRF로 합칩니다.
