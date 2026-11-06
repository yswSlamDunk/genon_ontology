# 값 타입 제약 조건 (Value type constraints)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/value-type-constraints/
- 사이드바 위치: Define Ontologies > Object and link types > Value types > Value type constraints

이 페이지는 값 타입(value type)에 걸 수 있는 검증 제약 조건의 종류와, 각 제약 조건을 어떤 기본 타입에 적용할 수 있는지 정리한 참조 문서입니다. 모든 타입에 공통으로 쓰는 열거(Enum)와 범위(Range)가 있고, String, Array, 구조체(struct)에는 타입별 제약 조건이 추가로 있습니다.

## 값 타입 제약 조건

각 값 타입은 데이터 검증을 강제하기 위해 선택적으로 제약 조건을 정의할 수 있습니다. 이 제약 조건은 **Value Type Manager** 애플리케이션에서 [새 값 타입을 만들 때](02_create-value-type.md) 구성할 수 있습니다. 사용할 수 있는 값 타입 제약 조건과 각각을 적용할 수 있는 기본 타입(base type)은 다음과 같습니다.

* **Enum (one of)(열거, 다음 중 하나):** 허용되는 값의 고정된 집합을 나타내는 제약 조건입니다.
  * **유효한 기본 타입:** String, Boolean, Decimal, Double, Float, Integer, Short
  * String 속성(property)의 경우 열거 값이 대소문자를 구분하도록 할지 구분하지 않도록 할지 선택할 수 있습니다.
* **Range(범위):** 허용되는 값의 최솟값, 최댓값 또는 범위입니다.
  * **유효한 기본 타입:** Decimal, Double, Float, Integer, Short, Date, Timestamp, String, Array
  * String 속성의 경우 문자열의 길이가 제약됩니다.
  * Array 속성의 경우 배열의 크기가 제약됩니다.

또한 다음 속성 타입에는 타입별 제약 조건이 추가로 있습니다.

* **String:**
  * **Regex(정규 표현식):** 문자열이 일치해야 하는 정규 표현식 패턴입니다. 속성 값의 일부 부분 문자열(substring)만 일치해도 검증을 통과하도록 선택적으로 설정할 수 있습니다.
  * **RID:** 문자열이 유효한 RID여야 합니다.
  * **UUID:** 문자열이 유효한 UUID여야 합니다.
* **Array:**
  * **Uniqueness(고유성):** 배열의 모든 원소가 서로 달라야 합니다.
  * **Nested(중첩):** 배열의 원소에 값 타입 제약 조건을 적용할 수 있습니다. 예를 들어 배열 안의 모든 문자열에 정규 표현식 제약 조건을 적용할 수 있습니다.
* **Struct(구조체):**
  * **Element constraints(원소 제약 조건):** 구조체 필드 식별자와 값 타입 참조 사이의 매핑입니다. 구조체 필드 식별자는 참조된 값 타입을 적용할 구조체 구성 요소를 가리킵니다.

**설명**: 몇 가지 구체적인 예입니다.

| 값 타입 | 기본 타입 | 제약 조건 | 통과 | 실패 |
|---|---|---|---|---|
| Priority | String | Enum: `HIGH`, `MEDIUM`, `LOW` (대소문자 구분) | `HIGH` | `high`, `URGENT` |
| Percentage | Integer | Range: 0 이상 100 이하 | `42` | `120` |
| CountryCode | String | Range: 길이 2 이상 2 이하 | `KR` | `KOR` |
| Tags | Array | Uniqueness | `["a", "b"]` | `["a", "a"]` |

Regex의 부분 일치 옵션은 중요한 차이를 만듭니다. 패턴 `[0-9]{3}`을 전체 일치로 검사하면 `123`만 통과하지만, 부분 일치를 허용하면 `abc123xyz`도 안에 `123`이 있으므로 통과합니다. 구조체의 원소 제약 조건은 예를 들어 `address` 구조체의 `email` 필드에는 "email" 값 타입을, `zip` 필드에는 "우편번호" 값 타입을 각각 연결하는 식으로 필드별 검증을 지정합니다.

## 정리

- Enum은 허용 값 집합을, Range는 최솟값과 최댓값을 지정하며 String에서는 길이, Array에서는 크기를 제약합니다.
- String에는 Regex(부분 일치 옵션 포함), RID, UUID 제약 조건이 추가로 있습니다.
- Array에는 원소 고유성과 원소별 중첩 제약 조건이, Struct에는 필드마다 값 타입을 연결하는 원소 제약 조건이 있습니다.
