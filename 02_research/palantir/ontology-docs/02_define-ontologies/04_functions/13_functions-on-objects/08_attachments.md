# 첨부 파일 (Attachments)

- 원문: https://www.palantir.com/docs/foundry/functions/attachments/
- 사이드바 위치: Define Ontologies > Functions > Functions on objects > Attachments

이 페이지는 객체에 붙는 파일인 첨부 파일(attachment)을 함수(function)에서 읽고, 파싱하고, 새로 만드는 방법을 설명합니다. 사용자가 엑셀 파일을 올려 객체를 대량으로 만드는 경우처럼, 파일 내용을 온톨로지 데이터로 바꾸는 작업에 필요한 내용입니다. 언어(TypeScript v1, TypeScript v2, Python)별로 지원 범위와 API가 다르다는 점이 중요합니다.

**주의**: TypeScript v1 함수는 메모리 제한이 엄격한 환경에서 실행됩니다. 파일 데이터를 다룰 때는 이 메모리 제한을 금방 넘을 수 있으므로, 20MB 미만의 첨부 파일만 다룰 것을 권장합니다. Python과 TypeScript v2 함수의 기본 제한은 1GB이며, Ontology Manager에서 조정할 수 있습니다.

첨부 파일(attachment)은 객체 속성(property)처럼 동작하는 파일입니다. 첨부 파일은 임시 파일로 업로드된 뒤 [액션을 사용해 객체에 첨부](../../03_action-types/16_upload-attachments.md)됩니다. 객체에 첨부되고 나면 첨부 파일은 영구 저장되며 다른 속성과 비슷한 방식으로 접근할 수 있습니다.

**설명**: 데이터베이스로 치면 객체 테이블의 한 열에 파일 자체가 아니라 "저장소에 보관된 파일을 가리키는 참조"가 들어 있는 구조입니다. 예를 들어 Aircraft 객체의 `maintenanceLog` 속성 값은 정비 기록 파일을 가리키고, 함수는 그 참조를 통해 파일 내용을 읽습니다. 업로드 직후에는 어느 객체에도 연결되지 않은 임시 상태이고, 액션이나 함수가 객체의 속성에 연결해야 영구 보관됩니다.

<a id="attachments-in-functions"></a>
## 함수에서의 첨부 파일 (Attachments in functions)

첨부 파일은 액션에서 함수 입력으로 전달되거나, 객체의 속성으로 접근할 수 있습니다. 함수에서 첨부 파일을 만들어 반환할 수도 있습니다.

Python에서는 첨부 파일을 [API Gateway](https://www.palantir.com/docs/foundry/api/ontologies-v2-resources/attachments/attachment-basics/)로 관리합니다. Python OSDK에 첨부 파일 타입이 제공됩니다. [Attachments](https://www.palantir.com/docs/foundry/ontology-sdk/python-osdk/#attachments)를 참고하세요.

아래는 언어별 첨부 파일 import 구문입니다.

```typescript tab="TypeScript v1"
import { Attachment } from "@foundry/functions-api";
```

```typescript tab="TypeScript v2"
import { Attachment } from "@osdk/functions";
```

```python tab="Python"
# 편의를 위해 OSDK의 Attachment 타입이 Python 함수의 `functions.api` 패키지에서 다시 내보내집니다.
from functions.api import Attachment
```

**설명**: 세 언어 모두 `Attachment`라는 같은 이름의 타입을 쓰지만 가져오는 패키지가 다릅니다. 함수 파라미터 타입을 `Attachment`로 선언하면 액션 폼 등에서 사용자가 올린 파일이 그 파라미터로 전달됩니다.

> **중간 요약**: 첨부 파일은 객체 속성처럼 쓰이는 파일로, 액션으로 객체에 붙여야 영구 저장됩니다. 함수는 첨부 파일을 입력으로 받거나 객체 속성으로 읽을 수 있고, 언어마다 `Attachment` 타입을 가져오는 패키지가 다릅니다.

<a id="read-attachment-data"></a>
## 첨부 파일 데이터 읽기 (Read attachment data)

첨부 파일에는 원시 데이터를 읽는 read 메서드가 제공됩니다. 메서드 시그니처는 다음과 같습니다.

```typescript tab="TypeScript v1"
// Blob은 변경 불가능한 원시 데이터를 담은 파일 형태의 객체를 나타내는 표준 JavaScript 타입입니다.
// https://developer.mozilla.org/en-US/docs/Web/API/Blob
readAsync(): Promise<Blob>;
```

```typescript tab="TypeScript v2"
// Response 인터페이스는 Fetch API의 일부이며, TypeScript v2 환경에서는 `undici`가 제공합니다.
// https://developer.mozilla.org/en-US/docs/Web/API/Response
fetchContents(): Promise<Response>;
```

```python tab="Python"
# BytesIO는 바이너리 스트림을 나타내는 표준 Python 타입입니다.
# https://docs.python.org/3/library/io.html#io.BytesIO
def read(self) -> BytesIO: ...
```

**설명**: 세 시그니처 모두 "파일의 바이트를 돌려준다"는 같은 일을 하지만 반환 타입이 다릅니다. TSv1은 `Blob`(바이트 덩어리), TSv2는 HTTP 응답 객체 `Response`(여기서 `.arrayBuffer()`나 `.text()`로 내용을 꺼냄), Python은 메모리 위 바이트 스트림 `BytesIO`를 돌려줍니다. TypeScript 쪽은 원격 저장소에서 파일을 가져오는 비동기 작업이므로 `Promise`로 감싸져 있습니다.

복잡한 파일 형식을 다루려면 라이브러리를 사용하거나 직접 코드를 작성해야 할 수 있습니다. 예를 들어 PDF는 적절한 라이브러리로 파싱해야 합니다. [함수 저장소에 의존성을 추가하는 방법에 대해 더 알아보세요](../12_typescript-v1/09_add-dependencies.md).

<a id="parse-excel-files-from-attachments"></a>
### 첨부 파일에서 Excel 파일 파싱하기 (Parse Excel files from attachments)

온톨로지 객체를 대량으로 만들거나 수정하려면, Excel 파일을 첨부 파일 파라미터로 받아 그 행을 파싱합니다.

```python tab="Python"
from io import BytesIO
import pandas as pd

from functions.api import function, Attachment, OntologyEdit
from ontology_sdk import FoundryClient
from ontology_sdk.ontology.objects import MyObjectType


@function(edits=[MyObjectType])
def process_excel_upload(excel_file: Attachment) -> list[OntologyEdit]:
    client = FoundryClient()
    ontology_edits = client.ontology.edits()

    # 업로드된 Excel 파일 읽기
    sheet_data: BytesIO = excel_file.read()
    df = pd.read_excel(sheet_data)

    # 각 행을 처리해 객체를 생성하거나 수정
    for _, row in df.iterrows():
        new_obj = ontology_edits.objects.MyObjectType.create(str(row["id"]))
        new_obj.property_a = row["column_a"]
        new_obj.property_b = row["column_b"]

    return ontology_edits.get_edits()
```

(원문에는 SheetJS(`xlsx`) 라이브러리로 Blob을 ArrayBuffer로 바꾸고 첫 번째 시트를 JSON 행으로 변환해 처리하는 TypeScript v1 버전 예제도 있습니다.)

**설명**: 입력은 사용자가 올린 Excel 파일(`Attachment`)이고, 출력은 온톨로지 편집(edit) 목록입니다. `excel_file.read()`로 바이트를 읽고, `pd.read_excel`로 표(DataFrame)로 바꾼 뒤, 각 행마다 `MyObjectType.create(기본 키)`로 새 객체를 만들고 열 값을 속성에 넣습니다. 예를 들어 시트에 `id, column_a, column_b` 열을 가진 행이 3개 있으면 MyObjectType 객체 3개를 만드는 편집이 반환됩니다. `@function(edits=[MyObjectType])`은 이 함수가 어떤 객체 타입을 편집하는지 선언하는 부분입니다. 반환된 편집은 이 함수를 쓰는 액션이 실행될 때 실제로 적용됩니다.

여러 파일을 업로드하려면 파라미터 타입으로 `Attachment[]`(TypeScript) 또는 `list[Attachment]`(Python)를 받습니다. `xlsx`(SheetJS)나 `pandas` 같은 라이브러리는 [의존성 추가](../12_typescript-v1/09_add-dependencies.md)를 참고하세요.

<a id="file-parsing-in-typescript-v1"></a>
### TypeScript v1에서의 파일 파싱 (File parsing in TypeScript v1)

TypeScript v1 함수는 파일 시스템을 지원하지 않습니다. 파일 데이터 파싱과 관련된 의존성은 `fs` 모듈에 의존하는 경우가 많은데, 이 모듈은 함수 환경에서 사용할 수 없습니다. 이 제한 때문에 컴파일과 실행 중에 `fs` 모듈 오류가 발생할 수 있습니다. 이 제한을 우회하려면 메모리 내 파일 시스템(예: `memfs`)에 대한 의존성을 추가한 다음, 그 의존성을 `fs`라는 이름으로 별칭(alias) 지정할 수 있습니다.

아래는 `package.json` 파일에서 NPM 의존성 `memfs`를 사용하는 예입니다.

```json
"fs": "npm:memfs@^x.x.x"
```

**설명**: `fs`는 Node.js에서 디스크 파일을 읽고 쓰는 표준 모듈입니다. 위 설정은 "`fs`라는 이름으로 import하면 실제로는 `memfs` 패키지를 불러오라"는 뜻입니다. 그러면 라이브러리가 `require("fs")`를 호출해도 디스크 대신 메모리에 파일을 흉내 낸 구현이 쓰여 오류 없이 동작합니다. `x.x.x`는 실제 버전 번호로 바꿔 씁니다.

> **중간 요약**: 첨부 파일은 언어별 read 메서드(`readAsync`, `fetchContents`, `read`)로 바이트를 읽고, 필요한 라이브러리로 파싱합니다. Excel을 받아 행마다 객체를 만드는 것이 대표 사례이며, TSv1에서 `fs`가 필요한 라이브러리는 `memfs`를 `fs`로 별칭 지정해 우회합니다.

<a id="create-attachments"></a>
## 첨부 파일 만들기 (Create attachments)

함수로 첨부 파일을 만들어 객체에 첨부할 수도 있습니다. 함수에서 만든 첨부 파일이 영구 저장되려면, 함수가 첨부 파일을 객체에 연결하는 [온톨로지 편집(Ontology edit)](../12_typescript-v1/03_api-ontology-edits.md)을 수행해야 합니다.

**주의**: 객체에 첨부되지 않은 첨부 파일은 업로드한 사람만 볼 수 있으며 일정 시간이 지나면 자동으로 삭제됩니다. <br><br>
TypeScript v2 함수는 첨부 파일 생성을 지원하지 않습니다.

첨부 파일을 만들려면 첨부 파일의 업로드 함수를 사용합니다. 언어별 업로드 함수 시그니처는 다음과 같습니다.

```typescript tab="TypeScript v1"
import { Attachments, Attachment } from "@foundry/functions-api";

// Attachments에 있는 메서드:
uploadFile(filename: string, blob: Blob): Promise<Attachment>;
```

```python tab="Python"
from ontology_sdk import FoundryClient
from foundry_sdk_runtime.attachments import AttachmentMetadata

# FoundryClient에 있는 메서드:
def upload(file_path: str, attachment_name: str) -> AttachmentMetadata: ...
# `file_path`는 업로드할 로컬 파일입니다.
```

**설명**: TSv1은 메모리의 `Blob`을 파일 이름과 함께 바로 올리고, Python은 먼저 로컬 디스크에 파일을 쓴 다음 그 경로를 넘겨 올린다는 차이가 있습니다. 두 경우 모두 반환값(새 첨부 파일)을 객체 속성에 대입해야 영구 저장됩니다.

다음 예제는 파일을 업로드하고 그 결과로 생긴 첨부 파일을 객체에 할당하는 과정을 보여 줍니다.

```python tab="Python"
from io import BytesIO

from functions.api import function, Attachment, OntologyEdit
from ontology_sdk import FoundryClient
from ontology_sdk.ontology.objects import Aircraft


@functions(edits=[Aircraft])
def update_maintenance_log(
    aircraft: Aircraft,
    completed_maintenance_log: Attachment
) -> list[OntologyEdit]:
    client = FoundryClient()
    ontology_edits = client.ontology.edits()

    maintenance_log_data: BytesIO = aircraft.maintenance_log.read()
    completed_maintenance_log_data: BytesIO = completed_maintenance_log.read()

    # 현재 항공기 정비 기록과 완료된 정비 기록을 비교해 새 정비 기록을 만듦
    updated_maintenance_log_data: BytesIO = get_updated_maintenance_log(
        maintenance_log_data,
        completed_maintenance_log_data
    )

    editable_aircraft = ontology_edits.objects.Aircraft.edit(aircraft)

    with open("updated-maintenance-log.txt", "wb") as f:
        f.write(updated_maintenance_log_data.getbuffer())

    editable_aircraft.maintenance_log = client.ontology.attachments.upload(
        "updated-maintenance-log.txt",
        "my_attachment"
    )

    return ontology_edits.get_edits()
```

(원문에는 `aircraft.maintenanceLog.readAsync()`로 기존 기록을 읽고 `Attachments.uploadFile("maintenance-log.txt", ...)` 결과를 `aircraft.maintenanceLog`에 대입하는 TypeScript v1 버전 예제도 있습니다.)

**설명**: 입력은 Aircraft 객체 하나와 새로 완료된 정비 기록 첨부 파일이고, 출력은 Aircraft의 `maintenance_log` 속성을 새 파일로 바꾸는 편집입니다. 순서는 (1) 기존 기록과 새 기록을 각각 읽고, (2) 두 내용을 합친 새 기록을 만들고(`get_updated_maintenance_log`는 예제용으로 가정한 사용자 함수), (3) 로컬 파일로 쓴 뒤 업로드하고, (4) 업로드 결과를 편집 가능한 Aircraft 객체의 속성에 대입하는 것입니다. 마지막 대입이 "첨부 파일을 객체에 연결하는 온톨로지 편집"이며, 이 단계가 있어야 파일이 삭제되지 않고 남습니다.

> **중간 요약**: 함수에서 첨부 파일을 만들려면 업로드 함수(TSv1 `Attachments.uploadFile`, Python `client.ontology.attachments.upload`)를 호출한 뒤, 결과를 객체 속성에 대입하는 온톨로지 편집을 해야 합니다. 객체에 연결되지 않은 첨부 파일은 일정 시간 뒤 삭제되며, TSv2는 첨부 파일 생성을 지원하지 않습니다.

## 정리

- 첨부 파일은 객체 속성처럼 동작하는 파일이며, 객체에 연결되어야 영구 저장됩니다.
- 함수는 첨부 파일을 입력 파라미터로 받거나 객체 속성으로 읽을 수 있고, 읽기 메서드는 TSv1 `readAsync()`, TSv2 `fetchContents()`, Python `read()`입니다.
- Excel 같은 파일은 SheetJS나 pandas 같은 라이브러리로 파싱해 객체를 대량 생성하거나 수정하는 데 쓸 수 있습니다.
- TSv1은 메모리 제한 때문에 20MB 미만 파일을 권장하고 `fs`가 없으므로 `memfs` 별칭으로 우회합니다. Python과 TSv2는 기본 1GB입니다.
- 첨부 파일 생성은 TSv1과 Python에서만 가능하며, 업로드 후 객체 속성에 대입하는 편집이 필요합니다.
