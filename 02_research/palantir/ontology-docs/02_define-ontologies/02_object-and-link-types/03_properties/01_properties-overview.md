# 속성 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/properties-overview/
- 사이드바 위치: Define Ontologies > Object and link types > Properties > Overview

이 페이지는 객체 타입(object type)의 속성(property)이 무엇인지 정의하고, 데이터셋의 열과 필드에 어떻게 대응하는지 설명합니다. 이어서 속성에 쓸 수 있는 기본 타입(base type)을 표로 정리하고, 각 타입이 타이틀 키(title key)나 기본 키(primary key)로 쓰일 수 있는지 알려 줍니다. 기본 키에 어떤 타입을 골라야 하는지는 객체 타입 설계에서 자주 하는 결정이므로, 이 표의 "권장하지 않음" 사유를 잘 봐 두는 것이 좋습니다.

[객체 타입](../02_object-types/01_object-types-overview.md)의 **속성(property)은** 현실 세계 엔터티나 이벤트의 특성에 대한 스키마 정의입니다. **속성 값(property value)은** 객체의 속성에 들어 있는 값, 즉 그 현실 세계 엔터티나 이벤트의 단일 인스턴스가 가진 값을 가리킵니다.

예를 들어 Ontology Manager에서 `Employee` 객체 타입은 `employee number`, `start date`, `role` 속성을 가질 수 있습니다. 가상의 직원 "Melissa Chang"은 `employee number`에 "11502", `start date`에 "October 9, 2016", `role`에 "software engineer"라는 속성 값을 가질 수 있습니다.

마찬가지로 Ontology Manager에서 `Flight` 객체 타입은 `departure date`, `arrival date`, `passenger count` 속성을 가질 수 있습니다. 객체 "JFK → SFO 24-02-2021"은 `departure date`에 "24-02-2021", `arrival date`에 "25-02-2021", `passenger count`에 "150"이라는 속성 값을 가질 수 있습니다.

온톨로지의 바탕이 되는 개념은 데이터셋 구조에서 대응하는 개념을 가지고 있습니다. 온톨로지에서 속성의 정의는 데이터셋의 열(column)에 대응하고, 속성 값의 정의는 데이터셋의 필드(field)에 대응합니다. 예를 들어 `Employee` 데이터셋에는 `employee number`, `start date`, `role` 열이 있을 수 있습니다. 이 경우 직원 "Melissa Chang"의 행에서 `employee number` 열에 해당하는 필드 하나의 값은 "11502"입니다.

Foundry 온톨로지는 추상적인 데이터 모델에 그치지 않고 각 온톨로지 개념을 조직의 실제 데이터에 매핑하여, 이 데이터 자산이 현실 세계의 애플리케이션을 구동할 수 있게 합니다. 속성 값은 Ontology Manager에서 백킹 데이터소스(backing datasource)를 추가하거나, 객체 타입의 객체를 생성하는 액션을 구성함으로써 만들어지고 사용자 애플리케이션에 표시됩니다. `Employee` 타입 객체의 `employee number`, `start date`, `role` 속성에 대한 속성 값을 만들기 위해, 조직은 `Employee` 객체 타입에 백킹 데이터소스를 추가하고 직원 명부와 기타 기업 데이터를 온톨로지에 공급할 수 있습니다. 모든 객체를 액션으로 만들 계획이라면 대신 [백킹 데이터소스 없이 객체 타입을 만들](../02_object-types/02_create-object-type.md#create-an-object-type-without-a-backing-datasource) 수 있습니다.

**설명**: 위 `Employee` 예시를 테이블로 그려 보면 다음과 같습니다.

| employee number | start date | role |
|---|---|---|
| 11502 | 2016-10-09 | software engineer |
| 11503 | 2018-03-01 | data analyst |

여기서 열 머리글 `employee number`, `start date`, `role`이 속성(스키마 수준의 정의)이고, 첫 행의 칸에 들어 있는 "11502", "2016-10-09", "software engineer"가 Melissa Chang 객체의 속성 값입니다. 클래스와 인스턴스로 보면 속성은 클래스의 필드 선언(`String role;`), 속성 값은 특정 인스턴스의 필드에 저장된 값에 해당합니다.

> **중간 요약**: 속성은 객체 타입의 특성을 정의한 스키마(데이터셋의 열)이고, 속성 값은 특정 객체가 가진 값(데이터셋의 필드)입니다. 속성 값은 백킹 데이터소스나 객체를 만드는 액션을 통해 채워집니다.

<a id="supported-property-types"></a>
## 지원되는 속성 타입 (Supported property types)

| 속성 기본 타입 | 타이틀 키로 사용 가능? | 기본 키로 사용 가능? | 비고 |
|---|---|---|---|
| 자주 쓰는 타입: `String`, `Integer`, `Short` | 예 | 예 | |
| 시간 기반: `Date`, `Timestamp` | 예 | 권장하지 않음 | 일반적으로 시간 값은 기본 키로 적합하지 않습니다. 저장 형식이 표시 형식과 달라서 예상치 못한 충돌이나 고유성 문제가 생길 수 있기 때문입니다. 대부분의 경우 대신 `String`을 사용할 것을 권장합니다. |
| 숫자와 유사한 타입: `Boolean`, `Byte`, `Long` | 예 | 권장하지 않음 | `Boolean`은 객체 타입의 객체 인스턴스를 두 개로 제한합니다. `Byte` 속성은 액션에서 `Integer` 파라미터를 통해서만 값을 지정할 수 있으므로, 대부분의 경우 대신 `Integer` 속성을 사용할 것을 권장합니다. `Long`은 [JavaScript에서 표현 문제 ↗](https://www.w3schools.com/js/js_numbers.asp#:~\:text=JavaScript%20Numbers%20are%20Always%2064,the%20international%20IEEE%20754%20standard.)가 있어서, 모든 프런트엔드 라이브러리와 코드가 1e15보다 큰 `Long` 값을 잘 처리하지는 못합니다. 대부분의 경우 대신 `String`을 사용할 것을 권장합니다. |
| 실수와 유사한 타입: `Float`, `Double`, `Decimal` | 예 | 아니요 | |
| `Vector` | 아니요 | 아니요 | |
| `Array` | 예 | 아니요 | 배열 속성에는 null 요소가 들어갈 수 없습니다.<br/>`Array`의 내부 타입이 유효한 타이틀 속성이 아니면, 그 `Array` 속성도 타이틀 속성으로 쓸 수 없습니다.<br/>중첩 배열은 Object Storage v2에서 지원되지 않습니다. |
| `Struct` | 아니요 | 아니요 | 구조체(struct) 속성은 중첩을 지원하지 않으며, 필드가 배열일 수 없습니다. 지원되는 필드 타입에 대한 자세한 정보는 [구조체 문서](../04_structs/01_structs-overview.md#struct-configuration)를 참고하세요. |
| `Media Reference`, `Time Series`, `Geotemporal Series`, `Attachment` | 아니요 | 아니요 | |
| `Geopoint` | 예 | 아니요 | Geopoint 값은 `latitude,longitude` 형식의 쉼표로 구분된 문자열로 저장됩니다(예: `57.64911,10.40744`). <br/>[온톨로지에서 지리 공간 데이터 사용하기](https://www.palantir.com/docs/foundry/geospatial/ontology/#points), [Create GeoPoint](https://www.palantir.com/docs/foundry/pb-functions-expression/constructGeoPointV1/), [Convert to Ontology GeoPoint](https://www.palantir.com/docs/foundry/pb-functions-expression/createOntologyGeopointV1/), [Is valid Ontology GeoPoint](https://www.palantir.com/docs/foundry/pb-functions-expression/isValidOntologyGeopointV1/)도 참고하세요. |
| `Geoshape` | 아니요 | 아니요 | |
| `Marking` | 아니요 | 아니요 | |
| `Cipher` | 예 | 아니요 | |

기본 타입에 대해 더 알아보려면 [기본 타입](09_base-types.md)을 참고하세요.

**설명**: 몇 가지 "권장하지 않음" 사유를 구체적으로 보면 다음과 같습니다.

- `Boolean`은 값이 `true`와 `false` 두 가지뿐이므로, 이를 기본 키로 삼으면 서로 다른 객체를 최대 두 개까지만 만들 수 있습니다.
- `Long`은 64비트 정수지만, JavaScript의 `Number`는 IEEE 754 배정밀도 실수라서 정수를 정확히 표현할 수 있는 범위가 2^53(약 9 x 10^15)까지입니다. 그보다 큰 값은 브라우저에서 반올림되어 `9007199254740993`이 `9007199254740992`로 바뀌는 식으로 다른 값이 될 수 있습니다. 기본 키가 이렇게 바뀌면 엉뚱한 객체를 가리키게 되므로 문자열로 저장하는 편이 안전합니다.
- `Timestamp`는 내부적으로 밀리초 등 높은 정밀도로 저장되지만 화면에는 초나 분 단위로 보일 수 있습니다. 그러면 화면에서는 같아 보이는 두 키가 실제로는 다르거나, 그 반대 상황이 생길 수 있습니다.
- 실수 타입(`Float`, `Double`)은 `0.1 + 0.2`가 정확히 `0.3`이 되지 않는 것처럼 비교가 부정확하므로 식별자로 쓸 수 없습니다.

> **중간 요약**: 기본 키로는 `String`, `Integer`, `Short`가 적합하고, 시간 타입과 `Boolean`, `Byte`, `Long`은 권장되지 않으며, 실수 타입과 복합 타입(`Array`, `Struct`, `Vector`, 지리 공간 타입 등)은 사용할 수 없습니다. 타이틀 키로는 더 많은 타입을 쓸 수 있지만 `Vector`, `Struct`, 미디어와 시계열, `Geoshape`, `Marking` 등은 쓸 수 없습니다.

## 정리

- 속성은 객체 타입의 특성을 정의하는 스키마이며 데이터셋의 열에 대응하고, 속성 값은 개별 객체가 가진 값으로 데이터셋의 필드에 대응합니다.
- 속성 값은 백킹 데이터소스를 연결하거나, 객체를 만드는 액션을 구성해 채웁니다.
- 속성 기본 타입마다 타이틀 키와 기본 키로 쓸 수 있는지가 정해져 있으며, 기본 키에는 `String`이나 정수 타입을 쓰는 것이 안전합니다.
- `Array`는 null 요소와 (OSv2에서) 중첩이 허용되지 않고, `Struct`는 중첩과 배열 필드가 허용되지 않습니다.
