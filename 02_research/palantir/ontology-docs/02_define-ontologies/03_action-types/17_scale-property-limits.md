# 규모와 속성 제한 (Scale and property limits)

- 원문: https://www.palantir.com/docs/foundry/action-types/scale-property-limits/
- 사이드바 위치: Define Ontologies > Action types > Scale and property limits

이 페이지는 액션 하나가 한 번에 처리할 수 있는 양의 상한(파라미터 리스트 길이, 편집할 수 있는 객체 수, 일괄 호출 횟수, 알림 수신자 수)과, 액션으로 편집할 수 있는 속성(property) 타입의 목록을 정리한 레퍼런스입니다. 액션을 설계할 때 이 제한을 넘지 않도록 미리 확인하는 용도로 씁니다.

편집되는 객체 타입이 편집을 빠르게 처리하고, 실행 중인 애플리케이션을 느리게 하지 않으면서 사용자에게 보이는 데이터를 업데이트할 수 있도록 여러 제한이 마련되어 있습니다. 이 제한을 넘는 액션 제출은 성공하지 않으며 사용자에게 오류 메시지가 표시됩니다.

<a id="configuration-limits"></a>
## 구성 제한 (Configuration limits)

`Allow multiple values`(여러 값 허용) 토글을 켜면 사용자가 파라미터에 값의 리스트를 전달할 수 있습니다.

| 제한 | 최대값 |
| --- | --- |
| 원시(primitive) 타입 리스트 파라미터의 원소 수 | 10,000 |
| 객체 참조(object reference) 리스트 파라미터의 원소 수 | 1,000 |
| 제출 조건(submission criteria)에서 사용될 때 리스트 파라미터의 원소 수 | 1,000 |

**설명**: 원시 타입은 문자열, 정수, 날짜처럼 값 자체를 담는 타입이고, 객체 참조는 온톨로지의 객체 하나를 가리키는 타입입니다. 예를 들어 태그 문자열 리스트는 최대 10,000개까지 넘길 수 있지만, Flight 객체 리스트는 최대 1,000개까지만 넘길 수 있습니다.

<a id="edit-limits"></a>
## 편집 제한 (Edit limits)

| 제한 | 최대값 |
| --- | --- |
| 한 번의 액션 제출에서 편집할 수 있는 **객체 타입** 수 | 50 |
| 한 번의 액션 제출에서 편집할 수 있는 **객체** 수 | 10,000 |
| 액션 제출 안에서 **객체** 하나에 대한 개별 편집의 크기 | 32KB (OSv1), 3MB (OSv2) |

**설명**: OSv1과 OSv2는 객체 데이터를 저장하고 인덱싱하는 백엔드인 Object Storage V1과 Object Storage V2(OSv2)를 가리킵니다. 같은 객체 하나를 편집하더라도 어느 저장 백엔드를 쓰느냐에 따라 한 번의 편집에 담을 수 있는 데이터 크기가 32KB와 3MB로 크게 다릅니다.

<a id="batch-call-limits"></a>
## 일괄 호출 제한 (Batch call limits)

액션은 한 번의 일괄(batch) 호출에서 최대 10,000번 호출될 수 있습니다. 함수 기반 액션이면서 그 함수가 [일괄 실행(batched execution)](11_function-backed-actions/03_function-actions-batched-execution.md)을 사용하도록 구성되어 있지 않으면 이 제한은 20으로 줄어듭니다.

일괄 액션 호출에서 적용되는 편집은, 묶음 안의 어떤 요청이 그 편집을 일으켰는지와 관계없이 [편집 제한](#edit-limits)을 적용할 때 하나의 그룹으로 취급됩니다.

호출하는 애플리케이션에 따라 추가 제한이 적용될 수 있습니다.

**설명**: 예를 들어 Workshop 표에서 행 30개를 한꺼번에 인라인 편집하면 액션이 30번 호출되는 일괄 호출이 됩니다. 일반 액션이라면 10,000번 한도 안이므로 문제가 없지만, 일괄 실행이 꺼진 함수 기반 액션이라면 한도가 20이므로 실패합니다. 또 요청 하나가 객체 500개를 편집하고 그런 요청이 30개 있다면, 편집 객체 수는 요청별로 따지지 않고 합계 15,000개로 계산되므로 10,000개 제한을 넘습니다.

> **중간 요약**: 리스트 파라미터는 원시 타입 10,000개, 객체 참조 1,000개까지 받을 수 있고, 한 번의 제출로 객체 타입 50개, 객체 10,000개까지 편집할 수 있습니다. 일괄 호출은 최대 10,000번(일괄 실행이 꺼진 함수 기반 액션은 20번)이며, 편집 제한은 묶음 전체 합계로 적용됩니다.

<a id="supported-property-types"></a>
## 지원되는 속성 타입 (Supported property types)

아래는 지원되는 단일 속성 타입과 배열 속성 타입의 명세입니다. 일부는 Object Storage v2(OSv2)에서만 지원됩니다.

<a id="single-property-types"></a>
### 단일 속성 타입 (Single property types)

| 속성 타입 | 파라미터 타입 | 지원 여부 |
| --- | --- | --- |
| Attachment | Attachment | 예 |
| Boolean | Boolean | 예 |
| Byte | Integer | 예 |
| Cipher text | String | 예 |
| Date | Date | 예 |
| Decimal | Decimal | 예 |
| Double | Double | 예 |
| Float | Double | 예 |
| Geopoint | Geopoint | 예 |
| Geoshape | Geoshape | 예 |
| Geotemporal series reference | Geotemporal series reference | 예 (OSv2 전용) |
| Integer | Integer | 예 |
| Long | Long | 예 |
| Mandatory control | - | 속성으로도, 액션에서도 지원되지 않음 |
| Media reference | Media reference | 예 (OSv2 전용) |
| String | String | 예 |
| Short | Integer | 예 |
| Struct | Struct | 예 (OSv2 전용) |
| Timestamp | Timestamp | 예 |
| Time series reference | Time series reference | 예 (OSv2 전용) |
| Vector | Double list | 예 (OSv2 전용) |

<a id="array-property-types"></a>
### 배열 속성 타입 (Array property types)

| 배열 속성 타입 | 리스트 파라미터 타입 | 지원 여부 |
| --- | --- | --- |
| Attachment | Attachment | 예 |
| Boolean | Boolean | 예 |
| Byte | Integer | 예 |
| Cipher text | String | 예 |
| Date | Date | 예 |
| Decimal | Decimal | 예 |
| Double | Double | 예 |
| Float | Double | 예 |
| Geopoint | Geopoint | 예 |
| Geoshape | Geoshape | 예 |
| Geotemporal series reference | Geotemporal series reference | 아니요 |
| Integer | Integer | 예 |
| Long | Long | 예 |
| Mandatory control | Mandatory control | 예 |
| Media reference | - | 액션에서 지원되지 않음 |
| String | String | 예 |
| Short | Integer | 예 |
| Struct | Struct | 예 (OSv2 전용) |
| Timestamp | Timestamp | 예 |
| Time series reference | - | 속성으로도, 액션에서도 지원되지 않음 |
| Vector | - | 속성으로도, 액션에서도 지원되지 않음 |

**설명**: 표의 "파라미터 타입" 열은 그 속성을 액션으로 편집할 때 사용자 입력을 받는 파라미터가 어떤 타입이어야 하는지를 나타냅니다. 예를 들어 Byte, Short 속성은 액션 파라미터에서는 Integer로 입력받고, Float 속성은 Double로 입력받습니다. 더 넓은 범위의 타입으로 입력을 받은 뒤 저장할 때 해당 속성 타입에 맞춘다고 이해하면 됩니다. Vector 속성은 실수 배열(임베딩 벡터 등)이므로 단일 속성일 때 Double 리스트 파라미터로 입력받습니다.

> **중간 요약**: 대부분의 기본 속성 타입은 액션으로 편집할 수 있으며, Struct, Media reference, Time series reference 같은 일부 타입은 OSv2에서만 지원됩니다. 배열 속성은 Media reference, Time series reference, Vector, Geotemporal series reference 배열을 액션으로 편집할 수 없습니다.

<a id="supported-properties"></a>
## 지원되는 속성 (Supported properties)

현재 액션으로 객체의 **기본 키(primary key)는** 편집할 수 없습니다. 기본 키를 수정하는 것은 객체를 삭제한 뒤 새 객체를 추가하는 것과 같습니다. 액션으로 기본 키를 편집하는 대신, [규칙](06_rules.md#ontology-rules)을 사용해 객체를 직접 만들거나 삭제할 수 있습니다.

**설명**: 기본 키는 테이블에서 각 행을 유일하게 구분하는 열이고, 온톨로지에서도 객체 하나를 식별하는 값입니다. 다른 객체의 링크나 편집 기록이 이 값으로 객체를 가리키므로, 키 값이 바뀌면 사실상 다른 객체가 됩니다. 그래서 `F100`을 `F200`으로 바꾸고 싶다면 `F100` 객체를 삭제하고 `F200` 객체를 새로 만드는 규칙을 써야 합니다.

<a id="notification-recipients"></a>
## 알림 수신자 (Notification recipients)

[부수 효과 알림](12_side-effects/02_notifications.md)을 사용할 때, 하나의 액션에서 알림을 받을 수 있는 수신자는 최대 500명입니다. 알림 내용이 "From a function"(함수로부터)으로 렌더링될 때는 이 제한이 50명으로 줄어듭니다. 알림을 생성할 때 고려해야 할 제한에 대한 자세한 내용은 [알림의 최대 수신자 제한](12_side-effects/02_notifications.md#maximum-recipient-limits) 문서를 참고하세요.

## 정리

- 액션에는 성능을 지키기 위한 여러 제한이 있으며, 넘으면 제출이 실패하고 오류 메시지가 표시됩니다.
- 리스트 파라미터 원소 수, 한 번의 제출에서 편집할 객체 타입 수(50)와 객체 수(10,000), 객체 하나당 편집 크기(OSv1 32KB, OSv2 3MB)에 상한이 있습니다.
- 일괄 호출은 최대 10,000번이며, 일괄 실행이 꺼진 함수 기반 액션은 20번이고, 편집 제한은 묶음 전체에 합산 적용됩니다.
- 지원 속성 타입 표에서 어떤 타입을 어떤 파라미터 타입으로 편집하는지, OSv2 전용인지 확인할 수 있습니다.
- 기본 키는 액션으로 편집할 수 없고, 알림 수신자는 최대 500명(함수 렌더링 시 50명)입니다.
