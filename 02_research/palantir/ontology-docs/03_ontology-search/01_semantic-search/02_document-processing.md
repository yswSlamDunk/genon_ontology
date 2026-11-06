# 문서 처리 (Document processing)

- 원문: https://www.palantir.com/docs/foundry/ontology/document-processing/
- 사이드바 위치: Ontology search > Semantic search > Document processing

이 페이지는 PDF 문서나 이미지에서 텍스트를 뽑아내고, 그 텍스트를 시맨틱 검색(semantic search)에 알맞은 작은 조각(청크, chunk)으로 나누는 방법을 다룹니다. 모든 단계를 코드 없이 Pipeline Builder의 보드(board)로 처리하는 예제가 들어 있으며, 두 행짜리 예시 데이터셋이 단계마다 어떻게 바뀌는지 표로 보여 줍니다. 비정형 문서를 온톨로지 객체로 만들어 검색하려면 먼저 이 전처리 과정을 거쳐야 합니다.

이 페이지에서는 PDF 문서나 이미지에서 데이터를 추출할 때 유용한 몇 가지 고려 사항을 설명합니다.

<a id="data-extraction"></a>
## 데이터 추출 (Data extraction)

이 섹션은 [Pipeline Builder](https://www.palantir.com/docs/foundry/pipeline-builder/overview/)를 사용해 시맨틱 검색용으로 PDF를 파싱하는 기본 가이드를 제공하고, 텍스트 콘텐츠만 있을 때 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/) 애플리케이션에서 정보를 보여 주는 방법에 대한 권장 사항도 포함합니다.

시맨틱 검색은 PDF에 사용하기에 강력한 도구입니다. 특히 콘텐츠를 따로따로 임베딩되는 더 작은 "청크"로 나누면, 그렇지 않았다면 찾기 어려웠을 중요한 정보를 사용자와 워크플로가 찾아낼 수 있게 도와줍니다. PDF 안에는 종종 눈에 띄지 않고 묻혀 있는 방대한 비정형 지식이 있다는 점을 생각하면 이는 특히 유용합니다.

사용 방법은 간단합니다. PDF를 Foundry에 업로드하고, 텍스트를 추출하고, 그 텍스트를 청크로 나누고, 그 청크를 검색한 다음, 검색 결과를 해당 PDF를 옆에 렌더링한 상태로 보여 주어 사용자가 원본(source of truth)과 교차 검증할 수 있게 합니다.

**설명**: 임베딩(embedding)은 텍스트를 고정 길이의 실수 벡터(예: 길이 768의 float 배열)로 바꾸는 것입니다. 의미가 비슷한 문장일수록 벡터 사이 거리가 가깝게 나오도록 학습된 모델을 쓰므로, 검색어도 벡터로 바꾼 뒤 가장 가까운 벡터를 찾으면 단어가 정확히 일치하지 않아도 의미가 비슷한 문단을 찾을 수 있습니다. 이것이 키워드 검색과 구분되는 시맨틱 검색의 핵심입니다.

PDF를 가져오고 텍스트를 추출하려면 아래 단계를 따르세요.

1. [PDF를 미디어 세트(media set)로 가져옵니다](https://www.palantir.com/docs/foundry/data-integration/media-sets/).
2. [미디어 세트를 Pipeline Builder에 추가합니다](https://www.palantir.com/docs/foundry/pipeline-builder/datasets-add/#add-data-from-foundry-to-pipeline-builder).
3. **Get Media References** 보드를 사용합니다.

![Get Media References 보드](https://www.palantir.com/docs/resources/foundry/ontology/get-media-references.png)

4. **Text Extraction** 보드를 사용합니다.

![Text Extraction 보드](https://www.palantir.com/docs/resources/foundry/ontology/text-extraction.png)

**설명**: 미디어 세트는 PDF, 이미지처럼 표 형식이 아닌 파일을 모아 두는 Foundry의 저장 단위입니다. **Get Media References** 보드는 미디어 세트 안의 각 파일을 가리키는 참조 값(파일 하나당 한 행)을 열로 만들고, **Text Extraction** 보드는 그 참조가 가리키는 PDF에서 텍스트를 꺼내 문자열 열로 만듭니다. 결과적으로 "파일 하나 = 한 행, 그 파일의 텍스트 = 한 열"인 데이터셋이 생깁니다.

> **중간 요약**: PDF는 미디어 세트로 가져온 뒤 Pipeline Builder의 **Get Media References**와 **Text Extraction** 보드로 텍스트를 추출합니다. 추출한 텍스트를 청크로 나눠 임베딩하면 시맨틱 검색으로 찾을 수 있고, 검색 결과 옆에 원본 PDF를 보여 주어 검증하게 합니다.

<a id="chunking"></a>
## 청킹 (Chunking)

이 섹션은 [시맨틱 검색](01_overview-semantic-search.md) 워크플로에 기본적인 청킹 전략을 적용하는 방법을 설명합니다. 여기서 청킹은 큰 텍스트 덩어리를 더 작은 텍스트 조각으로 나누는 것을 뜻합니다. 이렇게 하면 이점이 있는데, 임베딩 모델에는 텍스트 입력의 최대 길이가 있고, 무엇보다 작은 텍스트 조각일수록 검색할 때 의미적으로 더 뚜렷하게 구분되기 때문입니다. 청킹은 [PDF](#data-extraction) 같은 큰 문서를 파싱할 때 흔히 사용합니다.

주된 목표는 긴 텍스트를 더 작은 "청크"로 나누고, 각 청크마다 원래 객체로 [링크](../../02_define-ontologies/02_object-and-link-types/06_link-types/02_create-link-type.md)되는 온톨로지 객체를 두는 것입니다.

**설명**: 100쪽짜리 계약서 전체를 벡터 하나로 임베딩하면 그 벡터는 문서 전체의 평균적인 의미만 담게 되어, "해지 위약금" 같은 특정 조항을 찾는 검색어와 잘 맞지 않습니다. 문단 단위 청크로 나누면 각 벡터가 한 가지 주제를 담으므로 검색 정확도가 올라갑니다. 데이터 모델로 보면 Document 객체 타입(1)과 Chunk 객체 타입(다) 사이에 1대다 링크를 두는 구조입니다.

청킹은 [Pipeline Builder](https://www.palantir.com/docs/foundry/pipeline-builder/overview/)의 **Chunk string** 보드가 수행합니다. 변환(transform) 메뉴에서 보드를 추가한 뒤 다음 인수를 구성하세요.

* **Expression:** 청크로 나눌 텍스트 열입니다.
* **Chunk size:** 각 청크의 대략적인 문자 수입니다.
* **Chunk overlap:** 각 청크가 이전 청크와 공유하는 문자 수로, 청크 경계를 넘어 문맥을 보존하는 데 도움이 됩니다.
* **Separators:** 보드가 텍스트를 나눌 때 쓰는, 순서와 우선순위가 정해진 구분자 목록입니다. 보드는 가장 우선순위가 높은 구분자로 먼저 나누고, 청크가 여전히 청크 크기보다 클 때만 다음 구분자로 넘어갑니다.

전체 인수 레퍼런스는 [Chunk string](https://www.palantir.com/docs/foundry/pb-functions-expression/chunkStringV1/) 함수 문서를 참고하세요.

**설명**: 구분자 목록이 예를 들어 `["\n\n", "\n", " "]`(빈 줄, 줄바꿈, 공백)이라면, 먼저 문단 경계로 자르고, 그래도 너무 긴 문단만 줄 단위로, 그래도 긴 줄만 단어 단위로 자릅니다. 이렇게 하면 가능한 한 큰 의미 단위를 유지하면서 크기 제한을 지킬 수 있습니다. 겹침(overlap)은 문장이 두 청크 경계에 걸쳐 잘릴 때 앞 청크의 끝부분을 다음 청크 앞에 반복해 넣어 문맥이 끊기지 않게 하는 장치입니다.

> **중간 요약**: 청킹은 임베딩 모델의 입력 길이 제한을 지키고 검색 정확도를 높이기 위해 긴 텍스트를 작은 조각으로 나누는 작업입니다. Pipeline Builder의 **Chunk string** 보드에서 대상 열, 청크 크기, 겹침, 우선순위 있는 구분자 목록을 지정합니다.

<a id="chunking-example"></a>
## 청킹 예제 (Chunking example)

출발점으로, [Pipeline Builder](https://www.palantir.com/docs/foundry/pipeline-builder/overview/)에서 코드를 쓰지 않고 기본 청킹 전략을 구현하는 방법을 보여 드립니다. 더 고급 전략에는 파이프라인의 일부로 [코드 저장소(code repository)](https://www.palantir.com/docs/foundry/code-repositories/overview/)를 사용하는 것을 권장합니다.

설명을 위해 `object_id`와 `object_text` 두 열을 가진 간단한 두 행짜리 데이터셋을 사용합니다. 이해하기 쉽도록 아래 `object_text` 예시는 일부러 짧게 만들었습니다.

|object\_id|object\_text|
|---------|--------|
|abc|gold ring lost|
|xyz|fast cars zoom|

먼저 **Chunk String** 보드를 사용합니다. 이 보드는 `object_text`를 더 작은 조각으로 나눈 배열을 담은 열을 하나 추가합니다. 보드는 각 의미 개념이 일관되고 고유하게 유지되도록 겹침과 구분자 같은 다양한 청킹 방식을 지원합니다.

아래 **Chunk String** 보드 스크린숏은 사용 사례에 맞게 바꿔 쓸 수 있는 간단한 전략을 보여 줍니다. 아래 구성은 대략 256자 크기의 청크를 반환하려고 시도합니다. 실제로 보드는 각 청크가 청크 크기 이하가 될 때까지 가장 우선순위가 높은 구분자로 텍스트를 나눕니다. 가장 우선순위가 높은 구분자로 더 나눌 곳이 없는데도 일부 청크가 여전히 너무 크면, 다음 구분자로 넘어가서 모든 청크가 청크 크기 이하가 되거나 더 쓸 구분자가 없을 때까지 계속합니다. 마지막으로 보드는 찾아낸 각 청크에 대해, 다음 청크가 이전 청크의 마지막 20자를 덮는 겹침을 갖도록 보장합니다.

![Chunk string 보드](https://www.palantir.com/docs/resources/foundry/ontology/chunk-string-board.png)

|object\_id|object\_text|chunks|
|---------|--------|-------|
|abc|gold ring lost|\[gold,ring,lost]|
|xyz|fast cars zoom|\[fast,cars,zoom]|

다음으로 배열의 각 원소가 자기만의 행을 갖게 하려고 합니다. **Explode Array with Position** 보드를 사용해 데이터셋을 여섯 행짜리로 변환합니다. 각 행의 새 열(아래 참고)은 배열 안의 위치와 배열의 원소라는 두 개의 키-값 쌍을 가진 구조체(struct, 맵)입니다.

![청크 펼치기(explode).](https://www.palantir.com/docs/resources/foundry/ontology/explode-chunks.png)

|object\_id|object\_text|chunks|chunks\_with\_position|
|---------|--------|-------|----------------------------------|
|abc|gold ring lost|\[gold,ring,lost]|{position:0, element:gold}|
|abc|gold ring lost|\[gold,ring,lost]|{position:1, element:ring}|
|abc|gold ring lost|\[gold,ring,lost]|{position:2, element:lost}|
|xyz|fast cars zoom|\[fast,cars,zoom]|{position:0, element:fast}|
|xyz|fast cars zoom|\[fast,cars,zoom]|{position:1, element:cars}|
|xyz|fast cars zoom|\[fast,cars,zoom]|{position:2, element:zoom}|

**설명**: "explode"는 배열 열을 펼쳐 원소마다 한 행씩 만드는 연산입니다. 원래 행의 나머지 열 값은 복제됩니다. SQL로는 PostgreSQL의 `SELECT object_id, object_text, chunks, u.elem, u.pos FROM t, unnest(chunks) WITH ORDINALITY AS u(elem, pos)`와 같은 동작입니다(단, ORDINALITY는 1부터, 여기의 position은 0부터 셉니다). 2행이 각각 원소 3개를 가지므로 결과는 2 x 3 = 6행이 됩니다.

그다음 위치와 원소를 각각 별도의 열로 꺼냅니다.

![청크 위치 가져오기.](https://www.palantir.com/docs/resources/foundry/ontology/get-chunk-position.png)
![청크 가져오기.](https://www.palantir.com/docs/resources/foundry/ontology/get-chunk.png)

|object\_id|object\_text|chunks|chunks\_with\_position|position|chunk|
|---------|--------|-------|----------------------------------|--|--|
|abc|gold ring lost|\[gold,ring,lost]|{position:0, element:gold}|0|gold|
|abc|gold ring lost|\[gold,ring,lost]|{position:1, element:ring}|1|ring|
|abc|gold ring lost|\[gold,ring,lost]|{position:2, element:lost}|2|lost|
|xyz|fast cars zoom|\[fast,cars,zoom]|{position:0, element:fast}|0|fast|
|xyz|fast cars zoom|\[fast,cars,zoom]|{position:1, element:cars}|1|cars|
|xyz|fast cars zoom|\[fast,cars,zoom]|{position:2, element:zoom}|2|zoom|

각 청크의 고유 식별자를 만들기 위해, 배열 안에서의 청크 위치를 문자열로 변환한 다음 원래 객체 ID에 이어 붙입니다. 불필요한 열도 삭제합니다.

![청크 위치를 문자열로 변환.](https://www.palantir.com/docs/resources/foundry/ontology/cast-chunk-position-to-string.png)

![chunk\_id 만들기.](https://www.palantir.com/docs/resources/foundry/ontology/create-chunk-id.png)

![불필요한 object\_text, chunks, position, chunks\_with\_position 열 삭제.](https://www.palantir.com/docs/resources/foundry/ontology/drop-unnecessary-columns.png)

|object\_id|chunk|chunk\_id|
|---------|-----|--|
|abc|gold|abc\_0|
|abc|ring|abc\_1|
|abc|lost|abc\_2|
|xyz|fast|xyz\_0|
|xyz|cars|xyz\_1|
|xyz|zoom|xyz\_2|

이제 여섯 개의 서로 다른 청크를 나타내는 여섯 행이 생겼습니다. 각 행에는 `object_id`(링크용), 새 기본 키가 될 새 `chunk_id`, 그리고 [시맨틱 검색 워크플로](05_using-palantir-provided-models-to-create-a-semantic-search-workflow.md#generate-embeddings-and-create-object-type)에서 설명한 대로 임베딩할 `chunk`가 있습니다. 그 결과 다음과 같은 표가 됩니다.

|object\_id|chunk|chunk\_id|embedding|
|---------|-----|--|--|
|abc|gold|abc\_0|\[-0.7,...,0.4]|
|abc|ring|abc\_1|\[0.6,...,-0.2]|
|abc|lost|abc\_2|\[-0.8,...,0.9]|
|xyz|fast|xyz\_0|\[0.3,...,-0.5]|
|xyz|cars|xyz\_1|\[-0.1,...,0.8]|
|xyz|zoom|xyz\_2|\[0.2,...,-0.3]|

**설명**: 최종 표는 그대로 Chunk 객체 타입의 백킹 데이터소스(backing datasource)가 됩니다. `chunk_id`는 기본 키(primary key)로, `abc` 객체의 0번째 청크라는 뜻의 `abc_0`처럼 원래 ID와 위치를 합쳐 전체에서 유일하게 만듭니다. `object_id`는 원래 객체(Document 등)의 기본 키를 가리키는 외래 키 역할을 하므로, 이 열로 Chunk에서 원래 객체로 가는 링크 타입을 정의할 수 있습니다. `embedding` 열은 벡터 속성이 되어 시맨틱 검색에 쓰입니다.

> **중간 요약**: 예제는 **Chunk String**으로 텍스트를 배열로 나누고, **Explode Array with Position**으로 원소마다 행을 만든 뒤, 위치와 원소를 열로 꺼내 `object_id`와 위치를 이어 붙인 `chunk_id`를 기본 키로 만듭니다. 마지막으로 각 청크를 임베딩하면 원래 객체에 링크되는 청크 객체 타입의 데이터가 완성됩니다.

## 정리

- PDF는 미디어 세트로 가져와 Pipeline Builder의 **Get Media References**와 **Text Extraction** 보드로 텍스트를 추출합니다.
- 긴 텍스트는 임베딩 입력 길이 제한과 검색 정확도 때문에 **Chunk string** 보드로 청크로 나눕니다. 청크 크기, 겹침, 우선순위 구분자를 설정합니다.
- 배열로 나온 청크는 **Explode Array with Position**으로 행 단위로 펼치고, 원래 ID와 위치를 합쳐 청크의 기본 키를 만듭니다.
- 각 청크를 임베딩하고 원래 객체에 링크하면 시맨틱 검색용 청크 객체 타입이 완성되며, 고급 전략은 코드 저장소에서 구현하는 것을 권장합니다.
