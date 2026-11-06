# 구조체 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/structs-overview/
- 사이드바 위치: Define Ontologies > Object and link types > Structs > Overview

이 페이지는 속성(property) 하나에 여러 필드를 담을 수 있게 하는 구조체(struct) 기본 타입을 소개합니다. 구조체 속성이 데이터소스의 어떤 열에 연결되는지, 어떤 제약이 있는지, 질의할 때 각 필드 조건이 어떻게 평가되는지, 그리고 현재 어떤 애플리케이션과 서비스에서 지원되는지를 다룹니다. 특히 구조체 배열을 질의할 때의 동작은 직관과 다를 수 있으므로 주의해서 읽어야 합니다.

**구조체(struct)는** 속성 하나가 값 하나 대신 여러 필드를 담을 수 있게 해 주는 온톨로지 속성 [기본 타입(base type)](../03_properties/09_base-types.md)입니다. 필드는 속성을 정의할 때 선언하며, 각 필드는 자체 이름과 타입을 가집니다. 흔히 쓰는 많은 객체 속성을 이런 방식으로 모델링할 수 있습니다. 예를 들어 `Full Name` 속성은 `firstName`과 `lastName` 필드를 담을 수 있고, `Address` 속성은 `street`, `city`, `postalCode`, `country`를 담을 수 있습니다.

구조체 속성은 그 자체로 구조체 타입인 데이터소스 열 하나로 뒷받침됩니다. Ontology Manager에서 [구조체 속성을 만들](02_create-struct-type.md) 때 그 열을 속성의 **Backing column**(백킹 열)으로 선택합니다. 필드 값이 처음에는 서로 다른 데이터소스에 있더라도, 온톨로지에서 속성을 정의하기 전에 하나의 구조체 타입 열로 합쳐 두기만 하면 됩니다.

**설명**: 구조체는 C의 `struct`나 Java의 작은 값 클래스처럼 여러 필드를 하나로 묶은 타입입니다. 예를 들어 `Address`를 일반 속성으로 만들면 `street`, `city`, `postalCode`, `country` 네 속성이 따로 생기지만, 구조체로 만들면 `address` 속성 하나에 `{street: "1 Main St", city: "Seoul", postalCode: "04524", country: "KR"}` 같은 값이 들어갑니다. 데이터셋 쪽에서는 Spark의 `StructType` 열이 이에 해당하며, 파이프라인에서 여러 열을 `struct(street, city, postalCode, country)`처럼 하나의 열로 묶어 두어야 합니다.

<a id="struct-configuration"></a>
## 구조체 구성 (Struct configuration)

구조체 속성에는 다음 제약이 있습니다.

* 구조체 속성은 다른 구조체를 포함할 수 없습니다.
* 구조체 필드는 배열일 수 없습니다. 다만 구조체 속성 자체는 구조체의 배열을 담을 수 있습니다.
* 구조체 속성은 필드를 최소 하나 가져야 합니다.
* 구조체 속성 필드는 현재 다음 타입만 지원합니다.
  * `BOOLEAN`
  * `BYTE`
  * `DATE`
  * `DECIMAL`
  * `DOUBLE`
  * `FLOAT`
  * `GEOPOINT`
  * `INTEGER`
  * `LONG`
  * `SHORT`
  * `STRING`
  * `TIMESTAMP`

**설명**: 즉 구조체는 한 단계 깊이만 허용됩니다. `Address` 안에 또 다른 구조체 `Coordinates {lat, lon}`를 넣을 수 없고, `phoneNumbers: [String]` 같은 배열 필드도 넣을 수 없습니다. 반면 속성 전체를 `Address[]`(구조체의 배열)로 만들어 한 객체에 주소 여러 개를 담는 것은 가능합니다.

> **중간 요약**: 구조체는 속성 하나에 이름과 타입을 가진 여러 필드를 담는 기본 타입이며, 구조체 타입 열 하나가 백킹 열이 됩니다. 중첩 구조체와 배열 필드는 허용되지 않고, 필드는 정해진 원시 타입만 쓸 수 있습니다.

<a id="query-semantics"></a>
## 질의 의미 (Query semantics)

구조체는 [ElasticSearch object 필드 타입 ↗](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/object)과 비슷하게 인덱싱되며, 이는 질의가 각 필드 조건을 독립적으로 평가한다는 뜻입니다. 구조체 속성이 배열을 담고 있으면, 배열 안의 어떤 구조체 하나도 모든 조건을 만족하지 않는데도 질의가 객체에 일치할 수 있습니다.

예를 들어 값의 배열을 담는 `Full Name` 속성을 생각해 봅시다. 어떤 객체가 `[{"firstName": "Ada", "lastName": "Chen"}, {"firstName": "Blake", "lastName": "Moreau"}]`를 저장하고 있다면, `"firstName": "Ada" AND "lastName": "Moreau"` 질의가 이 객체에 일치합니다. 첫 번째 값이 `firstName` 조건을 만족하고 두 번째 값이 `lastName` 조건을 만족하므로, 어느 값도 혼자서 두 조건을 모두 만족하지는 않지만 두 조건이 모두 충족된 것으로 처리됩니다.

**설명**: 이런 동작이 생기는 이유는 인덱싱할 때 구조체 배열이 필드별 값 목록으로 평탄화되기 때문입니다. 위 예시는 내부적으로 `firstName: ["Ada", "Blake"]`, `lastName: ["Chen", "Moreau"]`처럼 저장되어, 어떤 값이 어떤 값과 짝이었는지 정보가 질의 시점에 쓰이지 않습니다. 따라서 "Ada Moreau라는 이름을 가진 사람"을 정확히 찾으려는 의도라면, 구조체 배열에 대한 필드 조건 조합만으로는 원하는 결과를 얻지 못할 수 있습니다.

> **중간 요약**: 구조체 배열에 대한 질의는 필드 조건을 원소별로 묶어 평가하지 않고 필드마다 독립적으로 평가합니다. 그래서 서로 다른 원소가 각 조건을 나눠 만족해도 객체가 일치합니다.

<a id="current-levels-of-support"></a>
## 현재 지원 수준 (Current levels of support)

구조체 속성 지원은 아직 확대되는 중이므로, Palantir 플랫폼 전반에서 사용 가능 여부가 다릅니다. 현재 구조체는 다음 애플리케이션과 서비스에서 지원됩니다.

* **[Ontology Manager](../../../05_applications/04_ontology-manager/01_overview.md):** 구조체를 정의하고 편집합니다.
* **[Actions](../../03_action-types/01_overview.md):** [구조체 속성 값을 생성하고 수정합니다](../../03_action-types/10_actions-on-structs.md).
* **[Pipeline Builder](https://www.palantir.com/docs/foundry/pipeline-builder/overview/):** 구조체를 정의하고 편집합니다.
* **[Workshop](https://www.palantir.com/docs/foundry/workshop/overview/):** 구조체 속성을 표시하고 변수로 사용합니다.
* **[Marketplace](https://www.palantir.com/docs/foundry/marketplace/overview/):** 구조체 속성을 패키징하고 설치합니다.
* **[Object Explorer](../../../05_applications/01_object-explorer/03_search-and-explore-objects/01_search-objects.md):** 구조체 속성 값으로 객체를 검색합니다. 구조체 필드 검색은 개발 중입니다.
* **[Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/overview/):** 구조체 속성을 불러오고 구조체 속성 값으로 객체를 검색합니다. 모든 Ontology SDK가 구조체 속성을 지원하는 것은 아니므로 [지원되지 않는 속성 타입](https://www.palantir.com/docs/foundry/ontology-sdk/unsupported-types/#object-types-unsupported-property-types) 문서를 참고하세요.
* **[Functions](../../04_functions/01_overview.md):** TypeScript v2와 Python 함수(function)는 구조체 파라미터와 구조체 속성 편집(edit)을 지원합니다. [TypeScript v2](../../04_functions/10_typescript-v2/04_typescript-v2-ontology-edits.md#edits-on-struct-properties) 함수와 [Python](../../04_functions/11_python/05_python-ontology-edits.md#edit-struct-properties) 함수의 구조체 속성 편집 문서를 참고하세요.

구조체는 Object Storage v1(Phonograph)에서는 지원되지 않을 예정입니다. 현재 구조체 속성은 데이터셋과 제한된 뷰(restricted view)에서만 만들 수 있습니다.

## 정리

- 구조체는 속성 하나에 `firstName`, `lastName`처럼 이름과 타입을 가진 여러 필드를 담는 기본 타입이며, 데이터소스의 구조체 타입 열 하나로 뒷받침됩니다.
- 중첩 구조체와 배열 필드는 허용되지 않지만, 속성 자체를 구조체 배열로 만들 수는 있습니다. 필드 타입은 원시 타입 12가지로 제한됩니다.
- 구조체 배열 질의는 필드 조건을 독립적으로 평가하므로, 서로 다른 원소가 조건을 나눠 만족해도 일치합니다.
- Ontology Manager, Actions, Pipeline Builder, Workshop, Marketplace, Object Explorer, OSDK, Functions에서 지원되며, OSv1에서는 지원되지 않고 데이터셋과 제한된 뷰에서만 만들 수 있습니다.
