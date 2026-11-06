# 미디어 업로드 (Upload media)

- 원문: https://www.palantir.com/docs/foundry/action-types/upload-media/
- 사이드바 위치: Define Ontologies > Action types > Upload media

이 페이지는 액션으로 미디어 파일(이미지, 문서, 영상 등)을 업로드하는 방법과, 이때 권장되는 미디어 참조 속성(media reference property)의 장점을 설명합니다. 설정 방법은 다른 문서로 안내하고, 업로드 권한이 어떻게 관리되는지를 다룹니다.

액션은 액션 폼이나 테이블을 사용해 미디어 파일을 업로드하는 기능을 지원합니다. Foundry의 대부분의 사용 사례에서는 미디어 참조 속성(media reference property)에 업로드하는 방법이 권장됩니다.

미디어 참조 속성([미디어 세트(media set)를](https://www.palantir.com/docs/foundry/data-integration/media-sets/) 기반으로 함)은 첨부 파일 속성(attachment property)에 비해 다음과 같은 장점이 있습니다.

* **확장성(Scalability):** 효율적인 저장과 조회로 수십억 개의 파일을 지원합니다.
* **내장 변환(Built-in transformations):** 다양한 미디어 변환과 LLM 기능이 지원되며 별도 설정 없이 쉽게 사용할 수 있습니다.
* **고급 미리보기(Advanced previews):** 지원되는 형식에 대해 내장 렌더링과 풍부한 미리보기 기능을 제공합니다.
* **형식 지원(Format support):** 표준 형식은 물론 NITF, GeoTIFF, DICOM 같은 특수 형식에 대해서도 맞춤형 업무 흐름을 지원합니다.

사용자는 파일 선택기 인터페이스로 미디어 파일을 업로드할 수 있으며, 파일은 액션이 성공적으로 제출되면 미디어 세트에 저장됩니다.

**주의**: [형식 변환](https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-overview/#additional-input-formats)은 액션이 완료되고 미디어 파일이 미디어 세트에 업로드된 후에만 일어납니다.

**설명**: 미디어 세트는 파일 자체를 저장하는 Foundry의 저장소이고, 미디어 참조 속성은 객체에 "미디어 세트 안의 어떤 파일인지"를 가리키는 참조 값만 저장합니다. 데이터베이스에서 이미지 바이너리를 테이블에 직접 넣지 않고 파일 저장소에 두고 경로만 열에 저장하는 설계와 같은 구조입니다. NITF와 GeoTIFF는 위성/지리 영상 형식, DICOM은 의료 영상 형식입니다.

<a id="configuration"></a>
## 설정 (Configuration)

미디어 참조 속성을 설정하고 미디어 업로드 액션을 구성하는 자세한 방법은 [미디어 참조 속성 설정하기](../02_object-and-link-types/03_properties/09_base-types.md#configure-media-reference-properties)와 [미디어 업로드](https://www.palantir.com/docs/foundry/media-sets-advanced-formats/upload-media/)를 참고하세요.

<a id="permissions"></a>
## 권한 (Permissions)

액션을 통한 미디어 업로드 권한은 [액션 제출 조건(submission criteria)이](08_submission-criteria.md) 관리합니다. 사용자가 액션 제출 조건을 충족하면, 백킹 미디어 세트에 대한 권한이 없어도 미디어를 업로드할 수 있습니다.

**주의**: 미디어 세트에 대한 편집 권한은 미디어 세트가 객체 타입에 처음 추가되거나 액션 타입에서 처음 참조될 때 확인됩니다. 미디어 세트를 온톨로지에 추가하면 접근 제어가 미디어 세트에서 온톨로지로 위임됩니다. 즉, 객체 타입에서 액션을 관리할 수 있는 사람이 누가 미디어 세트에 미디어를 업로드할 수 있는지를 통제할 수 있게 됩니다.

> **중간 요약**: 미디어 업로드에는 확장성, 내장 변환, 미리보기, 특수 형식 지원이 있는 미디어 참조 속성이 권장됩니다. 업로드 권한은 액션 제출 조건이 관리하며, 미디어 세트를 온톨로지에 연결하는 순간 접근 제어가 온톨로지로 위임됩니다.

## 정리

- 액션은 폼이나 테이블에서 파일 선택기로 미디어를 업로드할 수 있고, 파일은 액션 제출이 성공하면 미디어 세트에 저장됩니다.
- 대부분의 경우 첨부 파일 속성보다 미디어 참조 속성이 권장됩니다.
- 형식 변환은 액션 완료와 업로드 이후에 일어납니다.
- 업로드 권한은 액션 제출 조건으로 관리되며, 미디어 세트 편집 권한은 처음 연결할 때만 확인됩니다.
