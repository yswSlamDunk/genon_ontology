# 값 타입 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/value-types-overview/
- 사이드바 위치: Define Ontologies > Object and link types > Value types > Overview

이 페이지는 값 타입(value type)이 무엇이고 왜 필요한지 소개합니다. 값 타입은 String이나 Integer 같은 기본 타입에 의미와 검증 규칙을 덧붙여 "이메일 주소", "우편번호" 같은 도메인 타입을 만들고, 이를 여러 객체 타입과 파이프라인에서 재사용하게 해 줍니다. 값 타입이 space 단위로 관리된다는 점, 권한과 버전 관리가 있다는 점도 함께 다룹니다.

<a id="value-types"></a>
## 값 타입 (Value types)

**값 타입(value type)은** [필드 타입(field type)](https://www.palantir.com/docs/foundry/data-integration/datasets/#supported-field-types)을 감싸는 의미적 래퍼(semantic wrapper)로, 타입 안전성을 높이고 표현력을 개선하며 추가 맥락을 제공하는 메타데이터와 제약 조건을 포함합니다. 값 타입은 도메인에 특화된 데이터 타입을 캡슐화하고, 플랫폼 전반에서 재사용할 수 있는 방식으로 데이터 검증을 강제합니다. 객체 타입, 속성(property), 링크 타입처럼 온톨로지(Ontology)를 정의하고 구성하는 다른 타입과 달리, 값 타입은 플랫폼의 [space](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/#spaces)에 연결됩니다. 하나의 space는 하나의 온톨로지를 가질 수 있습니다. 값 타입은 그것이 정의된 space 안에서만 사용할 수 있습니다. 값 타입은 Default 온톨로지에서는 사용할 수 없습니다.

데이터셋의 [필드 타입](https://www.palantir.com/docs/foundry/data-integration/datasets/#supported-field-types)과 속성의 [기본 타입(base type)](../03_properties/09_base-types.md)은 프로그래밍 언어에 있는 원시 타입(primitive type)을 반영합니다. 이런 타입은 도메인과 무관하며 도메인 맥락을 전혀 제공하지 않습니다. 반면 값 타입은 데이터의 맥락과 의미를 담고 데이터 검증을 한곳에 모읍니다. 사용자는 열 이름이나 속성 설명 같은 주변 정보에 의존하지 않고, 값 타입에서 직접 의미를 정의하고 읽어 냅니다. 또한 값 타입은 Builder 파이프라인과 온톨로지에 있는 데이터에 검증 제약 조건을 강제하므로, 데이터 통합 담당자와 온톨로지 관리자는 자신의 데이터 흐름과 모델에서 의미적 타입이 올바르게 지정되도록 보장할 수 있습니다.

예를 들어 사용자는 정규 표현식 제약 조건을 가진 "email" 값 타입을 정의해, 이 값 타입을 사용하는 모든 속성이 유효한 이메일 주소를 나타내도록 보장할 수 있습니다. 이 값 타입은 그런 속성마다 검증 로직을 중복해서 만들 필요 없이 여러 객체 타입과 파이프라인에서 재사용할 수 있습니다. 또한 이 값 타입을 사용하는 각 속성은 이메일 주소를 담고 있다는 것이 명시적으로 드러납니다.

값 타입은 여러 파이프라인과 객체 타입에서 재사용하기 위한 것이므로, 사용자가 필요한 곳에 적용할 수 있도록 [권한](05_value-types-permissions.md)이 관리되고, 호환성을 깨는 편집과 깨지 않는 편집을 모두 처리하기 위해 [버전](04_value-types-versions.md)이 관리됩니다.

[새 값 타입을 만드는 방법](02_create-value-type.md) 또는 속성에 [기존 값 타입을 사용하는 방법](03_use-value-type.md)부터 알아보세요.

**설명**: 프로그래밍 언어로 보면 값 타입은 원시 타입을 감싸고 생성 시점에 값을 검증하는 작은 클래스에 해당합니다. 예를 들어 다음 표에서 `contact` 열은 모두 String입니다.

| employee_id | contact |
|---|---|
| E1 | kim@example.com |
| E2 | lee@example.com |
| E3 | not-an-email |

기본 타입만 String으로 지정하면 E3의 잘못된 값도 그대로 통과합니다. `contact` 속성에 "email" 값 타입을 지정하면 정규 표현식 검증에서 E3이 걸러지고, 이 열이 이메일이라는 사실도 열 이름과 상관없이 타입 자체로 알 수 있습니다. 같은 검증이 필요한 다른 객체 타입(예: Customer의 이메일 속성)은 같은 값 타입을 다시 지정하기만 하면 됩니다.

**설명**: space는 Foundry에서 조직의 리소스와 권한을 나누는 상위 단위입니다. 값 타입이 space에 묶여 있으므로, 한 space에서 정의한 값 타입은 그 space와 연결된 온톨로지 안에서만 쓸 수 있습니다.

## 정리

- 값 타입은 필드 타입(기본 타입)에 메타데이터와 제약 조건을 더한 의미적 래퍼로, 도메인 데이터 타입과 검증 규칙을 재사용 가능하게 만듭니다.
- 기본 타입은 도메인 의미가 없지만, 값 타입은 의미와 검증을 한곳에 모으고 Builder 파이프라인과 온톨로지 양쪽에서 검증을 강제합니다.
- 값 타입은 space에 연결되어 그 space 안에서만 쓸 수 있고, Default 온톨로지에서는 쓸 수 없습니다.
- 재사용을 위해 권한과 버전이 관리됩니다.
