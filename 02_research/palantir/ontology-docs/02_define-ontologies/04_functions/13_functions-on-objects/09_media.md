# 미디어 (Media)

- 원문: https://www.palantir.com/docs/foundry/functions/media/
- 사이드바 위치: Define Ontologies > Functions > Functions on objects > Media

이 페이지는 함수(function)에서 이미지, PDF 문서, 오디오 같은 미디어를 읽고, 업로드하고, 변환하는 방법을 설명합니다. TypeScript v2와 Python은 `Media` 타입으로 업로드, 메타데이터 조회, 회전이나 OCR 같은 변환까지 할 수 있고, TypeScript v1은 `MediaItem` 타입으로 기존 미디어를 읽고 OCR이나 음성 인식을 수행합니다. 앞 페이지의 첨부 파일(attachment)과 달리 미디어는 Foundry의 미디어 세트(media set)에 저장되며, 객체에는 그 미디어를 가리키는 미디어 참조(media reference) 속성이 들어갑니다.

함수를 사용하면 [TypeScript v2](../10_typescript-v2/01_typescript-v2-getting-started.md), [Python](../11_python/01_python-getting-started.md), [TypeScript v1](../12_typescript-v1/01_typescript-v1-getting-started.md)에서 미디어에 접근하고 수정할 수 있습니다. TypeScript v2와 Python은 `Media` 타입을 사용해 미디어를 읽고, 업로드하고, 변환하며, [온톨로지 편집(Ontology edits)](../09_language-agnostic-features/01_edits-overview.md)과 OSDK를 통한 미디어 업로드를 지원합니다. TypeScript v1 함수는 외부 라이브러리 없이 여러 종류의 미디어를 다룰 수 있는 기본 제공 연산을 가진 `MediaItem` 타입을 제공합니다.

현재 기본 제공되지 않는 연산이 필요하다면 외부 라이브러리를 사용하거나 직접 코드를 작성해야 할 가능성이 큽니다. [함수 저장소에 의존성을 추가하는 방법에 대해 더 알아보세요.](../12_typescript-v1/09_add-dependencies.md)

**설명**: 미디어 참조(media reference)는 객체 속성에 저장되는 "미디어 파일의 위치를 가리키는 값"입니다. 데이터베이스에서 이미지 자체를 BLOB 열에 넣지 않고 파일 저장소 경로만 열에 저장하는 설계와 같은 구조입니다. 예를 들어 Aircraft 객체의 `myMediaProperty` 속성에는 정비 사진 파일을 가리키는 참조가 들어 있고, 함수는 그 참조로 실제 바이트나 메타데이터를 가져옵니다.

<a id="typescript-v2-and-python"></a>
## TypeScript v2와 Python (TypeScript v2 and Python)

온톨로지 편집 함수를 사용해 미디어를 업로드하고 온톨로지에 객체를 만듭니다. 업로드한 뒤에는 애플리케이션에서 사용하기 위해 객체에서 미디어 파일을 읽고 내려받을 수 있습니다. [Foundry의 미디어 세트에 대해 더 알아보세요.](https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-overview/)

TypeScript v2와 Python 함수에서는 온톨로지에 미디어를 업로드해 `Media` 인스턴스를 얻는 방식으로 온톨로지 편집을 구성할 수 있습니다. `Media` 타입은 `MediaReference`를 감싸고, 내용 가져오기, 메타데이터 가져오기, 객체에 미디어 첨부하기 같은 [상위 수준 연산](#media-ontology-sdk-operations)을 제공합니다. `Media`를 사용해 온톨로지 편집을 구성하거나, 기존 미디어를 파라미터로 함수에 전달할 수 있습니다.

<a id="use-as-a-function-input-or-output-type"></a>
### 함수 입력 또는 출력 타입으로 사용하기 (Use as a function input or output type)

함수는 `Media`를 입력으로 받거나, `uploadMedia`로 데이터를 업로드해 임시 미디어를 만들거나, 객체의 미디어 참조 속성에서 `Media`를 가져올 수 있습니다. 함수는 임시로 업로드된 것이든 객체의 미디어 참조 속성에서 온 것이든 `Media` 타입을 반환할 수도 있습니다. 함수 안에서는 `Media`의 바이트 내용을 가져오거나, 메타데이터를 가져오거나, 온톨로지 편집으로 온톨로지 객체에 첨부할 수 있습니다. TypeScript v2와 Python 모두 상위 수준 메타데이터 필드(`mediaType`, `sizeBytes`, `path`, Python에서는 snake\_case 표기)나 미디어 타입별 [전체 메타데이터](#get-media-metadata)를 가져올 수 있습니다.

[Live preview](../03_getting-started.md#test-in-live-preview)는 미디어 파라미터를 받는 함수를 지원합니다. 미디어 참조를 직접 입력하는 대신 미디어 세트를 검색해 항목을 바로 선택할 수 있습니다.

```typescript tab="TypeScript v2"
import type { Media } from "@osdk/client";

export default async function echoMedia(media: Media): Promise<Media> {
    return media;
}
```

(원문에는 `functions.api`에서 `Media`를 가져와 같은 동작을 하는 Python 버전 `echo_media`도 있습니다. Python의 `Media` 타입은 `foundry_sdk_runtime.media`에서 가져올 수도 있습니다.)

**설명**: 입력으로 받은 `Media`를 그대로 반환하는 가장 단순한 함수입니다. 파라미터와 반환 타입에 `Media`를 쓸 수 있다는 것을 보여 줍니다. 이 함수를 Live preview에서 실행하면 미디어 세트에서 항목을 고르는 입력 칸이 나타납니다.

<a id="upload-media"></a>
### 미디어 업로드하기 (Upload media)

함수 안에서 원시 바이트를 업로드하려면 Ontology SDK의 `uploadMedia`(TypeScript v2)와 `client.ontology.media.upload_media`(Python) 헬퍼를 사용합니다. 둘 다 `Media`를 반환하며, 이를 온톨로지 편집으로 온톨로지 객체의 미디어 속성에 넣거나 함수에서 반환할 수 있습니다.

```python tab="Python"
from ontology_sdk import FoundryClient
from foundry_sdk_runtime.media import Media
from functions.api import function

@function
def upload_media(body: str, media_set_filename: str) -> Media:
    client = FoundryClient()
    media: Media = client.ontology.media.upload_media(
        body=body.encode("utf8"),
        filename=media_set_filename,
    )
    return media
```

(원문에는 `Blob`을 만들어 `uploadMedia(client, { data: blob, fileName })`을 호출하는 TypeScript v2 버전과, `async_upload_media`를 await하는 Python 비동기 버전 예제도 있습니다.)

**설명**: 입력은 문자열 본문과 파일 이름이고, 출력은 업로드된 `Media`입니다. 문자열을 UTF-8 바이트로 인코딩해 `upload_media`에 넘기면 미디어 세트에 임시 항목이 생기고 그 핸들이 반환됩니다. 예를 들어 `body="Hello"`, `media_set_filename="note.txt"`로 호출하면 5바이트짜리 텍스트 미디어가 만들어집니다. 이 미디어는 아래 주의 사항처럼 아직 임시 상태입니다.

**주의**: 업로드된 미디어는 온톨로지 객체의 미디어 참조 속성에 설정하지 않으면 임시 상태로 남습니다. 온톨로지 편집이 적용되면 그때 미디어가 온톨로지 객체 속성에 영구 저장됩니다.

<a id="upload-media-in-ontology-edit-functions"></a>
### 온톨로지 편집 함수에서 미디어 업로드하기 (Upload media in Ontology edit functions)

함수 안에서 업로드했든 함수 입력으로 `Media`를 받았든, `Media` 파라미터로 기존 온톨로지 객체의 미디어 속성을 수정하거나 새 온톨로지 객체를 만들 수 있습니다.

```typescript tab="TypeScript v2"
// TypeScript OSDK 2.16 이상을 사용하는지 확인하세요

import type { Client, Media } from "@osdk/client";
import { Aircraft } from "@ontology-sdk/sdk";
import type { Edits } from "@osdk/functions";
import { createEditBatch, uploadMedia } from "@osdk/functions";

async function uploadTextToNewPlane(client: Client): Promise<Edits.Object<Aircraft>[]> {
    const batch = createEditBatch<Edits.Object<Aircraft>>(client);
    const blob = new Blob(["Hello, world"], { type: "text/plain" });
    const media: Media = await uploadMedia(
        client,
        { data: blob, fileName: "/planes/aircraft.txt" }
    );
    batch.create(Aircraft, { myMediaProperty: media, /* ... */ });
    return batch.getEdits();
}

export default uploadTextToNewPlane;
```

(원문에는 Python OSDK 2.198 이상에서 `client.ontology.edits()`와 `upload_media`를 사용해 같은 일을 하는 Python 버전 예제도 있습니다.)

**설명**: 입력은 OSDK 클라이언트이고, 출력은 Aircraft 객체 생성 편집 목록입니다. `createEditBatch`로 편집 묶음을 만들고, "Hello, world" 텍스트를 미디어로 업로드한 뒤, `batch.create(Aircraft, { myMediaProperty: media, ... })`로 그 미디어를 미디어 속성으로 가진 새 Aircraft 객체를 만드는 편집을 추가합니다. 반환된 편집이 적용되는 순간 임시 미디어가 객체 속성에 묶여 영구 저장됩니다.

**주의**: TypeScript OSDK 생성기 2.20 이전 버전에서는 `uploadMedia`가 `MediaReference`를 반환했습니다. 2.20 버전부터 `uploadMedia`는 `Media`를 반환합니다. `Media`는 내부의 `MediaReference`를 감싸고 `fetchContents`, `fetchMetadata`, `getMediaReference()` 같은 상위 수준 연산을 제공합니다. `Media`는 `createEditBatch` 연산에 바로 전달할 수 있습니다.

<a id="passing-a-media-reference-parameter-on-action-type"></a>
### 액션 타입에서 미디어 참조 파라미터 전달하기 (Passing a media reference parameter on action type)

미디어 참조 타입의 액션 파라미터는 함수에 파라미터로 전달될 수 있습니다.

아래 스크린샷은 액션이 미디어 파라미터를 자신을 뒷받침하는 함수에 전달하는 모습을 보여 줍니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/media-tutorial-media-action-parameter.png" alt = "액션" width="600"/>

> **중간 요약**: TSv2와 Python에서 `Media`는 함수의 입력과 출력 타입으로 쓸 수 있고, `uploadMedia`/`upload_media`로 새 미디어를 업로드할 수 있습니다. 업로드한 미디어는 온톨로지 편집으로 객체의 미디어 속성에 설정되어야 영구 저장되며, 액션의 미디어 참조 파라미터도 함수로 전달됩니다.

<a id="media-ontology-sdk-operations"></a>
### 미디어 Ontology SDK 연산 (Media Ontology SDK operations)

아래 메서드는 `upload_media`가 반환한 것과 객체 타입의 `Media` 속성으로 노출된 것을 포함해 모든 `Media` 인스턴스에서 동작합니다.

<a id="retrieve-media-bytes-data"></a>
#### 미디어 바이트 데이터 가져오기 (Retrieve media bytes data)

`Media`에 저장된 원시 데이터에 접근할 수 있습니다. 메서드 시그니처는 다음과 같습니다.

```typescript tab="TypeScript v2"
fetchContents(): Promise<Response>;

// "Response"는 JavaScript Fetch API의 표준 인터페이스입니다
// https://developer.mozilla.org/en-US/docs/Web/API/Response
const mediaContents: Response = await myAircraft.myMediaProperty.fetchContents();

if (mediaContents.ok) {
    const mediaMimeType = mediaContents.headers.get("Content-Type");

    // Blob은 변경 불가능한 원시 데이터를 담은 파일 형태의 객체를 나타내는 표준 JavaScript 타입입니다.
    // https://developer.mozilla.org/en-US/docs/Web/API/Blob
    // https://developer.mozilla.org/en-US/docs/Web/API/Response/blob
    const mediaBlob: Blob = await mediaContents.blob();
}
```

(원문에는 `get_media_content()`로 `BytesIO`를 받는 Python 버전도 있습니다.)

**설명**: `fetchContents()`는 HTTP 응답 형태로 미디어를 돌려줍니다. `ok`로 성공 여부를 확인하고, `Content-Type` 헤더에서 MIME 타입(예: `image/png`, `application/pdf`)을 읽고, `.blob()`으로 실제 바이트를 꺼냅니다.

<a id="get-media-metadata"></a>
#### 미디어 메타데이터 가져오기 (Get media metadata)

`Media`의 메타데이터를 가져올 수 있습니다.

```python tab="Python"
from foundry_sdk_runtime.media import MediaMetadata

# 사용 예:
media_metadata: MediaMetadata = my_aircraft.my_media_property.get_media_metadata()
path = media_metadata.path
size_bytes = media_metadata.size_bytes
media_type = media_metadata.media_type
```

(원문에는 `fetchMetadata()`로 `sizeBytes`, `mediaType`을 읽는 TypeScript v2 버전도 있습니다.)

**설명**: 파일 내용을 내려받지 않고 경로(`path`), 크기(`size_bytes`), MIME 타입(`media_type`) 같은 공통 정보만 가져옵니다. 예를 들어 크기가 너무 큰 파일은 처리하지 않도록 먼저 걸러 낼 때 쓸 수 있습니다.

두 언어 모두 미디어 타입별 전체 메타데이터도 가져올 수 있습니다. 이 메타데이터에는 문서의 페이지 수나 이미지의 크기와 밴드처럼 해당 타입에만 적용되는 필드가 포함됩니다. TypeScript v2는 `fetchFullMetadata`를, Python은 `get_media_full_metadata`를 제공합니다. 각각 `MediaFullMetadata`를 반환하며, 그 `itemMetadata`(Python에서는 `item_metadata`)는 미디어 타입에 대한 판별 유니온(discriminated union)입니다.

타입별 필드에 접근하려면 먼저 유니온의 타입을 좁혀야 합니다. TypeScript v2에서는 `itemMetadata.type` 문자열 판별자를 확인합니다. Python에서는 변형 클래스로 `isinstance`를 사용하거나 `item_metadata.type`을 확인합니다.

```typescript tab="TypeScript v2"
// fetchFullMetadata를 쓰려면 @osdk/client 2.56.0 이상을 사용하는지 확인하세요.
fetchFullMetadata?(): Promise<MediaFullMetadata>;

// 그 밖의 변형으로 "audio", "video", "spreadsheet", "model3d", "dicom",
// "email", "untyped"가 있습니다. 전체 타입 정의는 다음을 참고하세요:
// https://github.com/palantir/osdk-ts/blob/main/packages/api/src/object/Media.ts

const fullMetadata = await myAircraft.myMediaProperty.fetchFullMetadata?.();
const itemMetadata = fullMetadata?.itemMetadata;

if (itemMetadata?.type === "document") {
    const pageCount = itemMetadata.pages;
    const title = itemMetadata.title;
} else if (itemMetadata?.type === "imagery") {
    const dimensions = itemMetadata.dimensions;
    const bands = itemMetadata.bands;
}
```

(원문에는 `DocumentMediaItemMetadata`, `ImageryMediaItemMetadata` 클래스로 `isinstance` 검사를 하는 Python 버전도 있습니다.)

**설명**: 판별 유니온(discriminated union)은 "여러 타입 중 하나"인 값인데, 공통 필드 하나(여기서는 `type`)의 값으로 실제 타입을 구분할 수 있게 만든 타입입니다. 예를 들어 `type`이 `"document"`이면 `pages`, `title` 필드가 있고, `"imagery"`이면 `dimensions`, `bands` 필드가 있습니다. `if (itemMetadata?.type === "document")` 검사 안에서는 TypeScript 컴파일러가 타입을 문서 메타데이터로 좁혀 주므로 `pages`에 안전하게 접근할 수 있습니다. 밴드(band)는 이미지의 색 채널(예: RGB의 R, G, B)을 뜻합니다.

TypeScript v2에서 `fetchFullMetadata`는 `Media` 인터페이스의 선택적(optional) 멤버입니다. 그래야 `Media`의 외부 구현체가 계속 컴파일됩니다. Ontology SDK가 반환하는 모든 `Media`는 이 메서드를 구현하므로, 위처럼 `?.()`로 호출하는 것은 안전합니다.

TypeScript v2는 `unknown` 변형도 정의합니다. 설치된 SDK 버전이 아직 모델링하지 못한 미디어 타입을 플랫폼이 반환하면, `itemMetadata`는 이 변형을 사용하고 `itemMetadata.raw`에 원본 페이로드를 보존해 검사할 수 있게 합니다. 타입을 좁히려면 `@osdk/client`를 업그레이드하세요. `unknown` 변형은 `untyped` 변형과 다릅니다. `untyped`는 [모든 파일 형식을 받는 미디어 세트](https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-overview/#multimodal-media-sets)를 위한 플랫폼 타입입니다.

> **중간 요약**: 모든 `Media`는 바이트 내용(`fetchContents`/`get_media_content`), 공통 메타데이터(`fetchMetadata`/`get_media_metadata`), 타입별 전체 메타데이터(`fetchFullMetadata`/`get_media_full_metadata`)를 가져올 수 있습니다. 전체 메타데이터는 판별 유니온이므로 `type` 검사나 `isinstance`로 타입을 좁힌 뒤 페이지 수, 이미지 크기 같은 필드에 접근합니다.

<a id="transform-media"></a>
### 미디어 변환하기 (Transform media)

**주의**: 미디어 변환은 베타 개발 단계입니다. 활발한 개발 중에 기능이 바뀔 수 있습니다.

미디어 항목을 변환(예: 이미지 회전, 크기 조정, 재인코딩, PDF 페이지 자르기나 렌더링, OCR 실행)하고 그 결과를 기다릴 수 있습니다. 변환 작업이 제출되면 완료될 때까지 폴링(polling)되고, 변환된 내용이 반환됩니다.

TypeScript v2에서는 변환이 `@osdk/api/unstable`을 통해 실험적 헬퍼로 제공됩니다. Python에서는 생성된 `FoundryClient`에서 `client.ontology.media.transform_and_wait`를 호출합니다. 비동기 변형인 `async_transform_and_wait`는 같은 인자를 받으며 await할 수 있습니다.

**설명**: 폴링은 작업 완료 여부를 일정 간격으로 반복해서 물어보는 방식입니다. 변환은 서버에서 비동기로 실행되는 작업이므로, `transform_and_wait`는 (1) 작업을 제출하고, (2) `poll_interval_seconds`마다 상태를 확인하다가, (3) 완료되면 결과 바이트를 돌려주고, `poll_timeout_seconds`를 넘기면 시간 초과 오류를 냅니다.

```python tab="Python"
from foundry_sdk.v2.media_sets.models import (
    ImageTransformation,
    JpgFormat,
    RotateImageOperation,
)
from foundry_sdk_runtime.errors import (
    MediaTransformationFailedError,
    MediaTransformationTimeoutError,
)
from foundry_sdk_runtime.media import Media
from functions.api import function
from ontology_sdk import FoundryClient

@function(beta=True)
def image_transform(document: Media) -> Media:
    client = FoundryClient()
    transformation = ImageTransformation(
        encoding=JpgFormat(),
        operations=[RotateImageOperation(angle="DEGREE_180")],
    )
    try:
        transformed_bytes: bytes = client.ontology.media.transform_and_wait(
            media_reference=document.get_media_reference(),
            transformation=transformation,
            poll_interval_seconds=3.0,
            poll_timeout_seconds=30.0,
        )
    except MediaTransformationFailedError:
        # 변환 작업이 FAILED 상태를 보고함
        raise
    except MediaTransformationTimeoutError:
        # 작업이 완료되기 전에 poll_timeout_seconds가 지남
        raise
    # 함수가 Media를 반환하도록 변환된 바이트를 다시 업로드
    return client.ontology.media.upload_media(body=transformed_bytes, filename="rotated.jpg")
```

(원문에는 `@osdk/api` 2.55.0 이상에서 `transformAndWait`와 `MediaTransformation` 객체(`$image`, `$encoding`, `$operations: [{ $rotate: ... }]`)를 사용하는 TypeScript v2 버전도 있습니다. 2.55.0 이전에는 이 헬퍼가 `__EXPERIMENTAL__NOT_SUPPORTED_YET__transformAndWait`라는 이름으로 내보내졌고 `media` 대신 `mediaReference` 인자를 받았습니다. TypeScript v2의 `MediaTransformation`은 `$image`, `$video`, `$audio`, `$documentToText`, `$documentToImage`, `$documentToDocument`, `$audioToText` 등의 변형을 가진 판별 유니온이며, 변형마다 인코딩과 연산 필드가 따로 있습니다.)

**설명**: 입력은 이미지 `Media`이고 출력은 180도 회전된 JPG `Media`입니다. `ImageTransformation`이 "결과 인코딩은 JPG, 연산은 180도 회전"이라는 변환 명세이고, `transform_and_wait`가 이 명세를 서버에 보내 결과 바이트를 받습니다. 변환 결과는 `Media`가 아니라 원시 바이트이므로, 함수가 `Media`를 반환하려면 마지막 줄처럼 다시 업로드해야 합니다. 실패와 시간 초과는 서로 다른 예외로 구분됩니다.

<a id="example-run-page-by-page-ocr-on-a-pdf-with-bounding-box-output"></a>
#### 예: PDF 페이지별 OCR과 바운딩 박스 출력 (Example: Run page-by-page OCR on a PDF with bounding box output)

이 워크플로는 PDF(미디어 세트에 업로드되었거나 객체에 첨부된 것)를 받아 모든 페이지에 OCR을 실행하고 hOCR 출력을 요청합니다. hOCR은 감지된 모든 단어와 줄에 `bbox` 속성이 붙은 HTML이므로, 같은 응답에서 인식된 텍스트와 그 바운딩 박스 좌표를 모두 추출할 수 있습니다. 각 `transform_and_wait` 호출은 한 페이지의 바이트를 반환하므로, 문서 전체를 처리하려면 반복합니다.

```python tab="Python"
from foundry_sdk.v2.media_sets.models import (
    DocumentMediaItemMetadata,
    DocumentToTextTransformation,
    OcrHocrOutputFormat,
    OcrLanguageWrapper,
    OcrOnPageOperation,
    OcrParameters,
)
from foundry_sdk_runtime.media import Media
from functions.api import function
from ontology_sdk import FoundryClient

@function(beta=True)
def ocr_pdf_pages(document: Media) -> list[bytes]:
    """PDF의 모든 페이지에 OCR을 실행하고 페이지별 hOCR 바이트를 반환합니다.

    각 hOCR 문서에는 감지된 단어, 줄, 문단에 `bbox` 속성이 들어 있으므로
    아무 HTML 파서로나 파싱하면 텍스트와 바운딩 박스를 한 번에 얻을 수 있습니다.
    """
    client = FoundryClient()
    metadata = document.get_media_full_metadata().item_metadata
    if not isinstance(metadata, DocumentMediaItemMetadata) or metadata.pages is None:
        raise ValueError("Expected a PDF document with a known page count")

    media_reference = document.get_media_reference()
    page_results: list[bytes] = []

    for page_number in range(metadata.pages):
        transformation = DocumentToTextTransformation(
            operation=OcrOnPageOperation(
                page_number=page_number,
                parameters=OcrParameters(
                    output_format=OcrHocrOutputFormat(),
                    languages=[OcrLanguageWrapper(language="ENG")],
                ),
            ),
        )
        hocr_bytes: bytes = client.ontology.media.transform_and_wait(
            media_reference=media_reference,
            transformation=transformation,
            poll_timeout_seconds=120.0,
        )
        page_results.append(hocr_bytes)

    return page_results
```

(원문에는 페이지 수를 `pageCount` 파라미터로 받고 `$documentToText`, `$ocrOnPage`, `$hocr` 변환을 반복 실행하는 TypeScript v2 버전도 있습니다.)

**설명**: 입력은 PDF `Media`이고, 출력은 페이지마다 하나씩인 hOCR 바이트 목록입니다. 먼저 전체 메타데이터에서 페이지 수를 얻고(문서가 아니거나 페이지 수가 없으면 오류), 0번 페이지부터 마지막 페이지까지 "이 페이지를 영어로 OCR하고 hOCR 형식으로 달라"는 변환을 하나씩 실행합니다. OCR(광학 문자 인식)은 이미지 속 글자를 텍스트로 바꾸는 기술이고, 바운딩 박스(bounding box)는 글자가 있는 위치를 감싸는 직사각형의 좌표입니다. 10쪽짜리 PDF라면 변환이 10번 실행되고 길이 10인 목록이 반환됩니다.

내용이 빽빽한 페이지는 OCR 실행 시간이 기본 함수 시간 제한을 훨씬 넘길 수 있습니다. 함수 실행 시간 제한을 설정하는 방법은 [게시된 함수 관리](../07_function-management/02_manage-functions.md)를 참고하세요.

<a id="example-render-pdf-pages-as-images-and-slice-ranges"></a>
#### 예: PDF 페이지를 이미지로 렌더링하고 범위 잘라 내기 (Example: Render PDF pages as images and slice ranges)

각 페이지의 시각적 렌더링이 필요한 워크플로(후속 이미지 주석, 임베딩, 화면 표시 등)에서는 `$documentToImage`와 `$renderPage`를 사용해 특정 페이지의 PNG/JPG 이미지를 얻습니다. PDF의 일부 범위를 별도 PDF 문서로 추출하려면 `$documentToDocument`와 `$slicePdfRange`를 사용합니다. 아래 각 함수는 `Media`를 반환할 수 있도록 변환된 바이트를 다시 업로드합니다. 각 함수는 별도 모듈이며, 등록되는 함수는 모듈의 `export default`입니다.

한 페이지를 PNG 이미지로 렌더링하기:

```typescript tab="TypeScript v2"
import { transformAndWait, type MediaTransformation } from "@osdk/api/unstable";
import type { Client, Media } from "@osdk/client";
import { uploadMedia } from "@osdk/functions";

export default async function renderFirstPageAsPng(
    client: Client,
    media: Media,
): Promise<Media> {
    const transformation: MediaTransformation = {
        $documentToImage: {
            $encoding: "png",
            $operation: { $renderPage: { $pageNumber: 0, $width: 1200 } },
        },
    };
    const result = await client(transformAndWait).transformAndWait({
        media,
        transformation,
    });
    if (!result.ok) {
        throw new Error(`Render failed: ${result.status}`);
    }
    // 함수가 Media를 반환하도록 렌더링된 페이지를 다시 업로드
    return uploadMedia(client, { data: await result.blob(), fileName: "page.png" });
}
```

(원문에는 `DocumentToImageTransformation`, `RenderPageOperation`을 사용하는 Python 버전도 있습니다.)

**설명**: 입력은 PDF `Media`이고 출력은 첫 페이지(0번)를 폭 1200픽셀로 렌더링한 PNG `Media`입니다. `MediaTransformation` 객체의 바깥 키(`$documentToImage`)가 변환 종류(문서에서 이미지로)를, 안쪽 `$operation`이 구체적인 연산(페이지 렌더링)을 정합니다.

페이지 범위를 새 PDF 문서로 잘라 내기:

```python tab="Python"
from foundry_sdk.v2.media_sets.models import (
    DocumentToDocumentTransformation,
    PdfFormat,
    SlicePdfRangeOperation,
)
from foundry_sdk_runtime.media import Media
from functions.api import function
from ontology_sdk import FoundryClient

@function(beta=True)
def slice_first_ten_pages(document: Media) -> Media:
    """입력 PDF의 0\~9페이지를 담은 새 PDF를 Media로 반환합니다."""
    client = FoundryClient()
    transformation = DocumentToDocumentTransformation(
        encoding=PdfFormat(),
        operation=SlicePdfRangeOperation(
            start_page_inclusive=0,
            end_page_exclusive=10,
            strictly_enforce_end_page=False,  # 10페이지보다 짧은 문서도 허용
        ),
    )
    sliced_pdf: bytes = client.ontology.media.transform_and_wait(
        media_reference=document.get_media_reference(),
        transformation=transformation,
    )
    # 함수가 Media를 반환하도록 잘라 낸 PDF를 다시 업로드
    return client.ontology.media.upload_media(body=sliced_pdf, filename="slice.pdf")
```

(원문에는 `$documentToDocument`와 `$slicePdfRange`를 사용하는 TypeScript v2 버전도 있습니다.)

**설명**: 시작 페이지는 포함(inclusive), 끝 페이지는 미포함(exclusive)이므로 0부터 10까지 지정하면 0\~9번, 즉 앞의 10페이지가 잘려 나옵니다. Python의 `range(0, 10)`과 같은 규칙입니다. `strictly_enforce_end_page=False`이면 문서가 5페이지뿐이어도 오류 없이 있는 페이지까지만 반환합니다.

<a id="example-annotate-every-page-with-detected-bounding-boxes"></a>
#### 예: 모든 페이지에 감지된 바운딩 박스 표시하기 (Example: Annotate every page with detected bounding boxes)

시각적인 디버깅 출력(각 PDF 페이지를 렌더링하고 그 위에 OCR로 감지한 바운딩 박스를 그린 것)을 만들려면, 페이지마다 세 가지 변환을 연결합니다. 각 페이지에 대해 페이지를 이미지로 렌더링하고, 같은 페이지를 OCR해 단어와 줄의 바운딩 박스를 얻습니다. 그런 다음 렌더링된 이미지를 다시 업로드하고 이미지 주석(annotate) 연산으로 주석을 그립니다. 페이지 수는 전체 메타데이터에서 나오므로 TypeScript v2에서는 `fetchFullMetadata`, Python에서는 `get_media_full_metadata`로 읽습니다. 각 단계는 이전 단계의 바이트를 새로 업로드해 다음 단계에 넘깁니다. 함수는 주석이 그려진 각 페이지를 다시 업로드해 페이지마다 `Media` 하나씩을 반환합니다.

```python tab="Python"
from foundry_sdk.v2.media_sets.models import (
    AnnotateImageOperation,
    Annotation,
    BoundingBox,
    BoundingBoxGeometry,
    DocumentMediaItemMetadata,
    DocumentToImageTransformation,
    DocumentToTextTransformation,
    ImageTransformation,
    OcrHocrOutputFormat,
    OcrLanguageWrapper,
    OcrOnPageOperation,
    OcrParameters,
    PngFormat,
    RenderPageOperation,
)
from foundry_sdk_runtime.media import Media
from functions.api import function
from ontology_sdk import FoundryClient

@function(beta=True)
def annotate_pdf_with_ocr_boxes(document: Media) -> list[Media]:
    """PDF의 모든 페이지를 렌더링하고, 각 페이지를 OCR해 텍스트 바운딩 박스를 찾고,
    렌더링된 이미지 위에 그린 뒤, 페이지마다 주석이 그려진 Media 하나를 반환합니다."""
    client = FoundryClient()
    media_reference = document.get_media_reference()

    # 전체 메타데이터로 페이지 수를 알아냄
    metadata = document.get_media_full_metadata().item_metadata
    if not isinstance(metadata, DocumentMediaItemMetadata) or metadata.pages is None:
        raise ValueError("Expected a PDF document with a known page count")

    annotated_pages: list[Media] = []
    for page_number in range(metadata.pages):
        # 1. 페이지를 PNG로 렌더링
        rendered_png: bytes = client.ontology.media.transform_and_wait(
            media_reference=media_reference,
            transformation=DocumentToImageTransformation(
                encoding=PngFormat(),
                operation=RenderPageOperation(page_number=page_number, width=1200),
            ),
        )

        # 2. 같은 페이지를 hOCR 모드로 OCR해 단어 단위 바운딩 박스를 얻음
        hocr_bytes: bytes = client.ontology.media.transform_and_wait(
            media_reference=media_reference,
            transformation=DocumentToTextTransformation(
                operation=OcrOnPageOperation(
                    page_number=page_number,
                    parameters=OcrParameters(
                        output_format=OcrHocrOutputFormat(),
                        languages=[OcrLanguageWrapper(language="ENG")],
                    ),
                ),
            ),
            poll_timeout_seconds=120.0,
        )

        # 3. hOCR을 파싱해 이미지 픽셀 단위 바운딩 박스를 얻음
        # parse_hocr_bounding_boxes 헬퍼는 생략했습니다. 예제 아래 설명을 참고하세요.
        boxes: list[tuple[str, BoundingBox]] = parse_hocr_bounding_boxes(hocr_bytes)

        # 4. 렌더링된 PNG를 임시 미디어 항목으로 다시 업로드
        rendered_media = client.ontology.media.upload_media(
            body=rendered_png, filename=f"page-{page_number}.png"
        )

        # 5. 미디어 변환으로 렌더링된 페이지에 주석을 그림
        annotated_bytes: bytes = client.ontology.media.transform_and_wait(
            media_reference=rendered_media.get_media_reference(),
            transformation=ImageTransformation(
                encoding=PngFormat(),
                operations=[
                    AnnotateImageOperation(
                        annotations=[
                            Annotation(
                                geometry=BoundingBoxGeometry(bounding_box=box),
                                label=label,
                            )
                            for label, box in boxes
                        ],
                    ),
                ],
            ),
        )

        # 6. 함수가 Media를 반환하도록 주석이 그려진 페이지를 다시 업로드
        annotated_pages.append(
            client.ontology.media.upload_media(
                body=annotated_bytes, filename=f"page-{page_number}-annotated.png"
            )
        )

    return annotated_pages
```

(원문에는 렌더링과 OCR을 `Promise.all`로 동시에 실행하는 TypeScript v2 버전과, `asyncio.gather`로 페이지별 작업과 각 페이지 안의 렌더링/OCR을 병렬 처리하는 Python 비동기 버전 예제도 있습니다.)

**설명**: 입력은 PDF `Media`이고 출력은 페이지마다 하나씩인 주석 이미지 `Media` 목록입니다. 페이지마다 (1) 렌더링으로 PNG 이미지를, (2) OCR로 hOCR 텍스트를 얻고, (3) hOCR에서 `(라벨, 박스)` 쌍 목록을 뽑고, (4) PNG를 다시 업로드해 미디어 참조를 얻은 뒤, (5) 그 이미지에 박스를 그리는 변환을 실행하고, (6) 결과를 업로드합니다. 변환 연산은 미디어 참조를 입력으로 받기 때문에 중간 결과 바이트를 매번 다시 업로드해야 한다는 점이 핵심입니다. 렌더링과 OCR은 서로 독립적이어서 비동기 버전에서는 동시에 실행해 대기 시간을 줄입니다.

hOCR 파싱 헬퍼는 두 예제 모두에서 생략되어 있습니다. 어떤 HTML 파서로든 `class="ocrx_word"` 요소와 그 `title="bbox X1 Y1 X2 Y2 ..."` 속성을 추출할 수 있습니다. Python에서는 `lxml`이나 `BeautifulSoup` 같은 파서를 사용하고, 일치하는 항목마다 `BoundingBox(left=X1, top=Y1, width=X2-X1, height=Y2-Y1)`로 변환합니다. TypeScript v2에서는 일치하는 항목마다 `{ $left: X1, $top: Y1, $width: X2-X1, $height: Y2-Y1 }`로 변환합니다.

**설명**: hOCR의 `bbox X1 Y1 X2 Y2`는 왼쪽 위 꼭짓점 (X1, Y1)과 오른쪽 아래 꼭짓점 (X2, Y2)입니다. 예를 들어 `bbox 100 50 180 70`이면 `left=100, top=50, width=80, height=20`인 상자로 변환됩니다.

> **중간 요약**: TSv2(`transformAndWait`)와 Python(`transform_and_wait`)으로 이미지 회전, PDF 페이지 렌더링, 페이지 범위 자르기, OCR, 이미지 주석 같은 변환을 실행할 수 있습니다(베타). 변환 결과는 바이트이므로 `Media`로 반환하거나 다음 변환에 넘기려면 다시 업로드해야 하며, 페이지가 많은 OCR은 함수 시간 제한을 늘려야 할 수 있습니다.

<a id="typescript-v1"></a>
## TypeScript v1

TypeScript v1에서는 함수 안에서 미디어를 업로드하는 기능을 지원하지 않습니다. 아래 예제는 기존 미디어를 온톨로지 편집에 전달하는 방법과 객체 타입의 미디어 속성에 대한 연산을 다룹니다.

**주의**: Foundry는 TypeScript v1 함수를 실행할 때 엄격한 메모리 제한을 적용합니다. 메모리 제한을 넘지 않도록 20MB 미만의 미디어 파일만 다루어야 합니다.

<a id="setting-existing-media-on-an-object"></a>
### 기존 미디어를 객체에 설정하기 (Setting existing media on an object)

온톨로지 편집 함수를 사용해 기존 미디어 항목을 객체에 첨부합니다.

```typescript tab="TypeScript v1"
import { OntologyEditFunction, MediaItem } from "@foundry/functions-api";
import { Aircraft } from "@foundry/ontology-api";

export class MyFunctions {
    @OntologyEditFunction()
    public async setExistingMediaToObject(
        aircraft: Aircraft,
        mediaItem: MediaItem
    ): Promise<void> {
        // 전달받은 MediaItem을 사용하는 온톨로지 편집은 지원됩니다
        aircraft.myMediaProperty = mediaItem;
    }
}
```

**설명**: 입력은 Aircraft 객체와 기존 미디어 항목이고, 반환값은 없습니다. TSv1의 온톨로지 편집 함수에서는 객체 속성에 값을 대입하는 것 자체가 편집으로 기록되므로, `aircraft.myMediaProperty = mediaItem` 한 줄이 "이 항공기의 미디어 속성을 이 미디어로 바꾼다"는 편집이 됩니다.

<a id="media-item-parameter-on-object-types"></a>
### 객체 타입의 미디어 항목 파라미터 (Media item parameter on object types)

다음 예제는 객체 타입의 미디어 참조 속성에 `isAudio` 미디어 연산을 사용하는 모습을 보여 줍니다.

```typescript tab="TypeScript v1"
MediaItem.isAudio(objectType.mediaReferenceProperty)
```

<a id="read-raw-media-data"></a>
### 원시 미디어 데이터 읽기 (Read raw media data)

객체의 미디어 참조 속성을 선택해 미디어 항목에 접근할 수 있습니다. 메서드 시그니처는 다음과 같습니다.

```typescript tab="TypeScript v1"
// Blob은 변경 불가능한 원시 데이터를 담은 파일 형태의 객체를 나타내는 표준 JavaScript 타입입니다.
// https://developer.mozilla.org/en-US/docs/Web/API/Blob
readAsync(): Promise<Blob>;
```

<a id="get-media-metadata"></a>
### 미디어 메타데이터 가져오기 (Get media metadata)

미디어 항목의 메타데이터에 접근할 수 있습니다. 메서드 시그니처는 다음과 같습니다.

```typescript tab="TypeScript v1"
getMetadataAsync(): Promise<IMediaMetadata>;
```

<a id="type-guards"></a>
### 타입 가드 (Type guards)

TypeScript v1의 타입 가드를 사용하면 특정 미디어 타입에만 해당하는 기능에 접근할 수 있습니다. 미디어 항목 메타데이터에 사용할 수 있는 타입 가드는 다음과 같습니다.

* `isAudioMetadata()`
* `isDicomMetadata()`
* `isDocumentMetadata()`
* `isImageryMetadata()`
* `isSpreadsheetMetadata()`
* `isUntypedMetadata()`
* `isVideoMetadata()`

예를 들어 이미지 타입 가드를 사용해 이미지 전용 메타데이터 필드를 꺼낼 수 있습니다.

```typescript tab="TypeScript v1"
const metadata = await myObject.mediaReference?.getMetadataAsync();
if (isImageryMetadata(metadata)) {
    const imageWidth = metadata.dimensions?.width;
    ...
}
```

**설명**: 타입 가드(type guard)는 불리언을 반환하면서 동시에 TypeScript 컴파일러에게 "이 검사가 참이면 값의 타입은 X다"라고 알려 주는 함수입니다. `isImageryMetadata(metadata)`가 참인 블록 안에서는 `metadata`가 이미지 메타데이터 타입으로 취급되어 `dimensions` 필드를 쓸 수 있습니다. 앞의 TSv2 판별 유니온에서 `type` 값을 비교하던 것과 같은 목적입니다.

미디어 항목 네임스페이스에도 타입 가드를 사용할 수 있으며, 그러면 타입별 미디어 항목의 더 많은 메서드에 접근할 수 있습니다. 여기서 사용할 수 있는 타입 가드는 다음과 같습니다.

* `MediaItem.isAudio()`
* `MediaItem.isDicom()`
* `MediaItem.isDocument()`
* `MediaItem.isImagery()`
* `MediaItem.isSpreadsheet()`
* `MediaItem.isVideo()`

<a id="document-specific-operations"></a>
### 문서 전용 연산 (Document-specific operations)

<a id="text-extraction"></a>
#### 텍스트 추출 (Text extraction)

문서에서 텍스트를 추출하려면 광학 문자 인식(OCR)을 사용하거나, 미디어 항목에 내장된 텍스트를 추출할 수 있습니다.

기계로 생성된 PDF에서는 광학 문자 인식(OCR)을 쓰는 것보다 PDF에 디지털로 내장된 텍스트를 추출하는 편이 더 빠르거나 더 정확할 수 있습니다. 아래는 텍스트 추출 사용 예입니다.

```typescript tab="TypeScript v1"
extractTextAsync(options: IDocumentExtractTextOptions): Promise<string[]>;
```

TypeScript v1을 사용할 때는 다음을 선택적으로 객체 형태로 제공할 수 있습니다.

* `startPage`: 0부터 시작하는 시작 페이지(포함, 비워 둘 수 있음)
* `endPage`: 0부터 시작하는 끝 페이지(미포함, 비워 둘 수 있음)

`startPage`와 `endPage`를 모두 비워 두면 문서의 모든 페이지 텍스트가 반환됩니다.

기계로 생성되지 않은 PDF에는 OCR 방법으로 텍스트를 추출하는 것이 가장 좋습니다.

```typescript tab="TypeScript v1"
ocrAsync(options: IDocumentOcrOptions): Promise<string[]>;
```

다음을 선택적으로 TypeScript 객체로 제공할 수 있습니다.

* `startPage`: 0부터 시작하는 시작 페이지(포함)
* `endPage`: 0부터 시작하는 끝 페이지(미포함)
* `languages`: 인식할 언어 목록(비워 둘 수 있음)
* `scripts`: 인식할 문자 체계(script) 목록(비워 둘 수 있음)
* `outputType`: 출력 타입을 `text` 또는 `hocr`로 지정

**설명**: "기계로 생성된 PDF"는 워드 프로세서 등에서 내보낸 PDF로, 글자가 텍스트 데이터로 들어 있어 그대로 꺼낼 수 있습니다. 반면 종이를 스캔한 PDF는 페이지가 이미지일 뿐이라 내장 텍스트가 없으므로 OCR로 글자를 인식해야 합니다. 두 메서드 모두 페이지마다 문자열 하나씩 담은 배열(`string[]`)을 반환합니다.

미디어 타입별 연산에 접근하려면 타입 가드를 사용해야 한다는 점을 기억하세요. 다음은 `isDocument()` 타입 가드를 사용한 뒤 OCR 텍스트 추출을 수행하는 예입니다.

```typescript tab="TypeScript v1"
import { MediaItem } from "@foundry/functions-api";
import { ArxivPaper } from "@foundry/ontology-api";

@Function()
public async firstPageText(paper: ArxivPaper): Promise<string | undefined> {
    if (MediaItem.isDocument(paper.mediaReference)) {
        const text = (await paper.mediaReference.ocrAsync({ endPage: 1, languages: [], scripts: [], outputType: 'text' }))[0];
        return text;
    }

    return undefined;
}
```

**설명**: 입력은 ArxivPaper 객체이고, 출력은 첫 페이지의 OCR 텍스트(문서가 아니면 `undefined`)입니다. `MediaItem.isDocument`로 미디어가 문서인지 확인해야 `ocrAsync`를 호출할 수 있습니다. `endPage: 1`은 미포함이므로 0번 페이지만 처리하고, 결과 배열의 `[0]`이 그 페이지의 텍스트입니다.

<a id="audio-specific-operations"></a>
### 오디오 전용 연산 (Audio-specific operations)

<a id="transcription"></a>
#### 음성 받아쓰기 (Transcription)

오디오 미디어 항목은 transcribe 메서드로 음성 받아쓰기(transcription)를 지원합니다. 시그니처는 다음과 같습니다.

```typescript tab="TypeScript v1"
transcribeAsync(options: IAudioTranscriptionOptions): Promise<string>;
```

받아쓰기 실행 방식을 지정하기 위해 다음을 선택적으로 전달할 수 있습니다.

* `language`: 받아쓸 언어. `TranscriptionLanguage` 열거형으로 전달합니다.
* `performanceMode`: 받아쓰기를 `More Economical`(더 경제적) 또는 `More Performant`(더 고성능) 모드로 실행합니다. `TranscriptionPerformanceMode` 열거형으로 전달합니다.
* `outputFormat`: `type`이 `plainTextNoSegmentData`(일반 텍스트) 또는 `pttml`인 객체를 전달해 출력 형식을 지정합니다. `pttml`은 [TTML과 유사한 ↗](https://en.wikipedia.org/wiki/Timed_Text_Markup_Language) 형식입니다. type이 `plainTextNoSegmentData`인 경우 이 객체는 불리언 `addTimestamps` 파라미터도 받습니다.

받아쓰기 옵션을 제공하는 예:

```typescript tab="TypeScript v1"
import { Function, MediaItem, TranscriptionLanguage, TranscriptionPerformanceMode } from "@foundry/functions-api";
import { AudioFile } from "@foundry/ontology-api";

@Function()
public async transcribeAudioFile(file: AudioFile): Promise<string|undefined> {
    if (MediaItem.isAudio(file.mediaReference)) {
        return await file.mediaReference.transcribeAsync({
            language: TranscriptionLanguage.ENGLISH,
            performanceMode: TranscriptionPerformanceMode.MORE_ECONOMICAL,
            outputFormat: {type: "plainTextNoSegmentData", addTimestamps: true}
        });
    }

    return undefined;
}
```

**설명**: 입력은 AudioFile 객체이고, 출력은 받아쓴 텍스트(오디오가 아니면 `undefined`)입니다. `isAudio` 타입 가드로 오디오인지 확인한 뒤, 영어로, 비용이 적은 모드로, 타임스탬프가 포함된 일반 텍스트 형식으로 받아쓰도록 요청합니다. 열거형(enum)은 허용되는 값의 목록을 미리 정해 둔 타입이라, 문자열을 직접 쓸 때보다 오타를 컴파일 시점에 잡을 수 있습니다.

> **중간 요약**: TSv1은 미디어 업로드를 지원하지 않고, 기존 미디어를 객체 속성에 대입하거나 `readAsync`, `getMetadataAsync`로 읽는 것만 가능합니다. 타입 가드(`MediaItem.isDocument`, `isAudio` 등)로 타입을 확인한 뒤 문서는 `extractTextAsync`/`ocrAsync`, 오디오는 `transcribeAsync` 같은 전용 연산을 쓸 수 있습니다.

## 정리

- 미디어는 미디어 세트에 저장되고, 객체에는 그것을 가리키는 미디어 참조 속성이 들어갑니다.
- TSv2와 Python은 `Media` 타입으로 입출력, 업로드(`uploadMedia`/`upload_media`), 내용과 메타데이터 조회를 지원하며, 업로드한 미디어는 온톨로지 편집으로 객체에 설정해야 영구 저장됩니다.
- 전체 메타데이터는 미디어 타입별 판별 유니온이므로 타입을 좁힌 뒤 페이지 수, 이미지 크기 같은 필드를 읽습니다.
- 베타 기능인 미디어 변환으로 이미지 회전, PDF 렌더링과 자르기, OCR, 바운딩 박스 주석을 실행할 수 있고, 결과 바이트는 다시 업로드해 `Media`로 만듭니다.
- TSv1은 `MediaItem`과 타입 가드로 기존 미디어를 읽고 OCR, 텍스트 추출, 음성 받아쓰기를 수행하며, 업로드는 지원하지 않고 20MB 미만 파일을 권장합니다.
