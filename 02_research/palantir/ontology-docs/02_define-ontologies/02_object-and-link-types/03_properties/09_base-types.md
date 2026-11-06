# 기본 타입 (Base types)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/base-types/
- 사이드바 위치: Define Ontologies > Object and link types > Properties > Base types

이 페이지는 속성(property)에 저장할 수 있는 데이터의 종류를 정하는 기본 타입(base type)을 설명합니다. 일반 필드 타입 외에 벡터, 지리 좌표, 첨부 파일, 시계열, 미디어 참조, 구조체(struct) 같은 고급 타입을 소개하고, 추가 설정이 필요한 미디어 참조와 구조체를 자세히 다룹니다. 프로그래밍 언어에서 변수의 자료형을 정하는 것과 같은 역할입니다.

속성 기본 타입은 속성에 저장할 수 있는 데이터의 종류를 정의합니다. 지원되는 모든 속성 기본 타입의 전체 목록은 [속성 개요](01_properties-overview.md#supported-property-types)를 참고하세요.

**기본 타입(base type)은** 객체의 속성을 정의하는 데 사용됩니다. 속성의 기본 타입은 사용자 애플리케이션에서 그 속성에 사용할 수 있는 연산의 범위를 결정합니다. `Map` 타입과 `Binary` 타입을 제외한 모든 필드 타입이 유효한 기본 타입입니다.

기본 타입에는 다음과 같은 고급 타입도 포함됩니다.

* **Vector:** 시맨틱 검색(semantic search)에 사용하기 위해 객체에 [벡터](https://www.palantir.com/docs/foundry/announcements/2023-11/#configure-a-vector-property-type)를 저장하는 타입입니다.
* **`Geopoint`:** 지리적 [점(point)](https://www.palantir.com/docs/foundry/geospatial/ontology/#points)을 나타내는 속성을 정의하는 타입입니다.
* **`Geoshape`:** 지리적 [도형(shape)](https://www.palantir.com/docs/foundry/geospatial/ontology/#polygons-and-lines)을 나타내는 속성을 정의하는 타입입니다.
* **Attachment:** [객체 함수(functions on objects)](../../04_functions/13_functions-on-objects/08_attachments.md)와 함께 사용하기 위해 객체에 파일을 저장하는 타입입니다.
* **Time series:** 속성을 [시계열(time series)](https://www.palantir.com/docs/foundry/time-series/time-series-overview/)로 정의하는 타입입니다.
* **Geotemporal series:** 속성을 [지리시간 시리즈(geotemporal series)](https://www.palantir.com/docs/foundry/geospatial/geotemporal-series-overview/)에 대한 참조로 정의하는 타입입니다.
* **Media reference:** [미디어 파일에 대한 참조](https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-overview/#media-references)를 정의하는 타입입니다.
* **Cipher text:** [Cipher](https://www.palantir.com/docs/foundry/cipher/overview/)로 인코딩된 문자열 값을 저장하는 타입입니다.
* **Struct:** [여러 필드](../04_structs/01_structs-overview.md)를 가진 스키마 기반 속성을 정의하는 타입입니다.

`Vector` 타입과 `Time series` 타입을 제외한 모든 기본 타입은 배열로 사용해 한 속성에 여러 값을 담을 수 있습니다.

**설명**: 기본 타입은 데이터베이스 열의 자료형(`VARCHAR`, `INTEGER`, `DATE` 등)에 대응합니다. 예를 들어 `Aircraft` 객체 타입이라면 `tailNumber`는 `String`, `seatCount`는 `Integer`, `lastPosition`은 `Geopoint`(위도와 경도 한 쌍), `engineTemperature`는 `Time series`(시각별 온도 값의 연속)로 정할 수 있습니다. 배열 타입은 `String[]`처럼 같은 타입 값 여러 개를 담는 것이며, `tags = ["A", "B"]` 같은 값이 됩니다. `Map`(키-값 사전)과 `Binary`(원시 바이트)는 속성 타입으로 쓸 수 없습니다.

> **중간 요약**: 기본 타입은 속성에 담을 데이터 종류와 가능한 연산을 정하며, `Map`과 `Binary`를 제외한 필드 타입과 Vector, Geopoint, Geoshape, Attachment, Time series, Geotemporal series, Media reference, Cipher text, Struct 같은 고급 타입이 있습니다. Vector와 Time series를 제외하면 배열로도 쓸 수 있습니다.

<a id="complex-property-base-types"></a>
## 복합 속성 기본 타입 (Complex property base types)

일부 속성 기본 타입은 추가 설정이 필요하거나 특정한 용도를 가집니다. 다음 속성 기본 타입에 대한 정보는 아래 섹션을 참고하세요.

* **[미디어 참조(Media references)](#media-references):** 미디어 세트(media set)에 저장된 미디어 항목을 참조합니다.
* **[구조체 타입(Struct types)](#structs):** 여러 필드를 가진 복잡한 구조의 데이터입니다.

<a id="media-references"></a>
### 미디어 참조 (Media references)

**미디어 참조(media reference)** 속성 타입을 사용하면 이미지, 동영상, 오디오 파일, 문서 같은 미디어를 객체에 붙일 수 있습니다. [미디어 참조](https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-overview/#media-references)는 [미디어 세트](https://www.palantir.com/docs/foundry/data-integration/media-sets/) 안의 특정 미디어 항목을 가리킵니다. 미디어 참조에는 미디어 파일에 대한 정보가 들어 있으므로, Foundry는 미디어 참조가 사용되는 곳 어디에서든 미디어를 표시할 수 있습니다.

<a id="media-reference-format"></a>
#### 미디어 참조 형식 (Media reference format)

다음은 미디어 참조의 예입니다.

```json
{
  "mimeType": "image/png",
  "reference": {
    "type": "mediaSetViewItem",
    "mediaSetViewItem": {
      "mediaSetRid": "ri.mio.main.media-set.00000000-0000-0000-0000-00000000000",
      "mediaSetViewRid": "ri.mio.main.view.00000000-0000-0000-0000-00000000000",
      "mediaItemRid": "ri.mio.main.media-item.00000000-0000-0000-0000-00000000000"
    }
  }
}
```

미디어 참조는 다음을 포함합니다.

* **`mimeType`:** 파일의 미디어 타입입니다.
* **`reference`:** 미디어 세트 RID, 뷰 RID, 특정 미디어 항목 RID를 담은 참조입니다.

**설명**: 이 JSON은 파일 내용 자체가 아니라 파일의 "위치 정보"입니다. `mimeType`의 `image/png`는 HTTP의 `Content-Type` 헤더에 쓰이는 것과 같은 MIME 타입 표기로, PNG 이미지라는 뜻입니다. `reference` 안의 세 RID는 차례로 "어느 미디어 세트의", "어느 뷰에 있는", "어느 항목인가"를 가리킵니다. 데이터베이스에서 큰 파일을 BLOB으로 직접 넣지 않고 파일 저장소의 경로만 열에 저장하는 방식과 같은 구조입니다.

<a id="configure-media-reference-properties"></a>
#### 미디어 참조 속성 설정 (Configure media reference properties)

미디어 참조 속성이 있는 객체 타입은 데이터셋이 뒷받침합니다. 백킹 데이터셋에는 미디어 참조 속성에 매핑될 미디어 참조 열이 있어야 합니다. 이 열 타입은 미디어 참조 값을 저장하도록 특별히 설계된 것으로, 온톨로지 객체와 미디어 세트 사이의 올바른 통합을 보장합니다.

![미디어 참조 속성의 소스](https://www.palantir.com/docs/resources/foundry/object-link-types/media-reference-source.png)

또한 미디어 참조 속성에는 하나 이상의 **미디어 소스(media source)가** 있어야 하며, 이는 객체 타입의 **Capabilities** 탭에서 설정할 수 있습니다. 속성에 미디어 소스가 여러 개 있다면 그중 하나를 **Upload destination**(업로드 대상)으로 선택해, 온톨로지 편집을 통해 업로드되는 미디어 항목을 어느 미디어 세트에 저장할지 정할 수 있습니다.

![Capabilities 탭의 미디어 참조 속성](https://www.palantir.com/docs/resources/foundry/object-link-types/media-reference-media-source.png)

> **중간 요약**: 미디어 참조 속성은 미디어 세트 안의 특정 미디어 항목을 가리키는 참조(MIME 타입과 RID들)를 저장합니다. 백킹 데이터셋에 미디어 참조 열이 있어야 하고, Capabilities 탭에서 미디어 소스와 업로드 대상을 설정합니다.

<a id="structs"></a>
### 구조체 (Structs)

**구조체(struct)는** 사용자가 여러 필드를 가진 스키마 기반 속성을 만들 수 있게 해 주는 온톨로지 속성 기본 타입입니다. 구조체 속성은 구조체 타입의 데이터셋 열로부터 만들어집니다. 구조체에 대해 더 알아보려면 [구조체](../04_structs/01_structs-overview.md) 전체 문서를 참고하세요.

> **중간 요약**: 구조체는 여러 필드를 하나로 묶은 속성 타입이며, 구조체 타입의 데이터셋 열에서 만들어집니다.

## 정리

- 기본 타입은 속성에 저장할 데이터의 종류와 애플리케이션에서 가능한 연산을 정합니다.
- `Map`과 `Binary`를 제외한 필드 타입과 여러 고급 타입(Vector, Geopoint, Geoshape, Attachment, Time series 등)을 쓸 수 있습니다.
- Vector와 Time series를 제외한 모든 기본 타입은 배열로 쓸 수 있습니다.
- 미디어 참조는 미디어 세트의 항목을 가리키며, 미디어 참조 열과 Capabilities 탭의 미디어 소스 설정이 필요합니다.
- 구조체는 여러 필드를 가진 속성 타입으로, 구조체 타입 데이터셋 열에서 만들어집니다.
