# 타입 레퍼런스 (Types reference)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/type-reference/
- 사이드바 위치: Define Ontologies > Object and link types > Types reference

이 페이지는 온톨로지를 정의할 때 쓰는 타입들(객체 타입, 속성, 공유 속성, 링크 타입, 액션 타입, 객체 타입 그룹, 인터페이스, 값 타입)을 한눈에 정리한 목록입니다. 각 항목의 짧은 정의와 상세 페이지 링크를 제공하며, 특히 "객체 타입 정의(메타데이터)"와 "객체 인스턴스(데이터)"의 차이를 명확히 구분합니다.

온톨로지를 정의할 때, Foundry로 가져온 데이터의 현실 세계 정의를 표현하기 위해 다양한 타입을 사용할 수 있습니다. Foundry에서 쓰이는 타입은 *온톨로지* 타입과 *데이터* 타입으로 분류됩니다.

* **온톨로지 타입(Ontology types)은** 현실 세계의 도메인을 온톨로지로 모델링하는 데 사용합니다.
* **데이터 타입(Data types)은** 데이터 값을 표현하는 데 사용합니다. Foundry의 데이터 타입은 [RDF ↗](https://w3c.github.io/rdf-concepts/spec/#section-Datatypes), [OWL ↗](https://www.w3.org/TR/owl-ref/#Datatype), [XSD ↗](https://www.w3.org/TR/xmlschema-2/#datatype)의 유사한 개념에서 영감을 받았습니다.

**설명**: 두 분류의 차이는 프로그래밍 언어로 보면 분명합니다. 데이터 타입은 `string`, `integer`, `date`처럼 값 하나의 형식을 정하는 기본 타입이고, 온톨로지 타입은 `class Airport { String name; String country; }`처럼 그런 기본 타입들을 묶어 도메인의 개념을 정의하는 사용자 정의 타입입니다. RDF, OWL, XSD는 웹에서 지식과 데이터를 기술하기 위한 W3C 표준으로, 특히 XSD는 `xsd:string`, `xsd:dateTime` 같은 기본 데이터 타입 체계를 정의합니다.

<a id="ontology-resources"></a>
## 온톨로지 리소스 (Ontology resources)

다음 타입들을 사용해 온톨로지를 구축하고 정의할 수 있습니다.

<a id="object-type"></a>
### 객체 타입 (Object type)

**객체 타입(object type)은** 개별 객체들로 이루어진, 현실 세계 엔터티나 이벤트의 스키마 정의입니다. 예를 들어 `JFK`와 `LHR`은 둘 다 `Airport` 객체 타입의 객체가 될 수 있습니다.

[객체 타입에 대해 더 알아보세요.](02_object-types/01_object-types-overview.md)

<a id="property"></a>
#### 속성 (Property)

객체 타입의 **속성(property)은** 현실 세계 엔터티나 이벤트를 설명하는 특성입니다. 예를 들어 `LHR`이 `Airport` 객체 타입의 객체라면, `name`과 `country`는 `Airport`의 속성입니다. `LHR` 객체의 속성 값은 다음과 같습니다.

* **name:** LHR
* **country:** United Kingdom

[속성에 대해 더 알아보세요.](03_properties/01_properties-overview.md)

<a id="shared-property"></a>
### 공유 속성 (Shared property)

**공유 속성(shared property)은** 온톨로지의 여러 객체 타입에서 사용할 수 있는 속성입니다. 공유 속성을 사용하면 객체 타입 전반에 걸쳐 일관된 데이터 모델링을 할 수 있고, 속성 메타데이터를 중앙에서 관리할 수 있습니다.

[공유 속성에 대해 더 알아보세요.](05_shared-properties/01_shared-property-overview.md)

**설명**: 예를 들어 Employee, Contractor, Customer 객체 타입이 모두 이메일 주소를 가진다면, 각 객체 타입에 `email` 속성을 따로 세 번 정의하는 대신 `email` 공유 속성 하나를 만들어 세 객체 타입에 붙입니다. 그러면 표시 이름이나 설명을 바꿀 때 한 곳만 수정하면 됩니다.

<a id="link-type"></a>
### 링크 타입 (Link type)

**링크 타입(link type)은** 두 객체 타입 사이 관계의 스키마 정의입니다. **링크(link)는** 두 객체 사이에 존재하는 그 관계의 인스턴스 하나를 가리킵니다.

[링크 타입에 대해 더 알아보세요.](06_link-types/01_link-types-overview.md)

<a id="action-type"></a>
### 액션 타입 (Action type)

**액션 타입(action type)은** 사용자가 한 번에 수행할 수 있는, 객체, 속성 값, 링크에 대한 변경 또는 편집(edit) 묶음의 스키마 정의입니다. 액션 타입에는 액션이 일어날 때 함께 발생하는 부수 효과(side effect) 동작도 포함됩니다. 온톨로지에 액션 타입이 구성되면 최종 사용자는 액션을 적용해 객체를 변경할 수 있습니다.

[액션 타입에 대해 더 알아보세요.](../03_action-types/01_overview.md)

**설명**: 액션 타입은 여러 변경을 하나로 묶은 트랜잭션 정의로 볼 수 있습니다. 예를 들어 "항공편 지연 처리" 액션 타입은 Flight 객체의 `status`를 `Delayed`로 바꾸고, 새 Delay 객체를 만들어 Flight와 링크하는 변경을 한 번에 수행하도록 정의할 수 있고, 부수 효과로 담당자에게 알림을 보내게 할 수 있습니다.

<a id="object-type-groups"></a>
### 객체 타입 그룹 (Object type groups)

객체 타입 그룹은 사용자가 온톨로지를 더 잘 검색하고 탐색하도록 돕는 분류용 기본 요소(classification primitive)입니다.

[객체 타입 그룹에 대해 더 알아보세요.](10_type-groups.md)

<a id="interfaces"></a>
### 인터페이스 (Interfaces)

**인터페이스(interface)는** 객체 타입의 형태(shape)와 기능을 기술하는 온톨로지 타입입니다. 인터페이스는 객체 타입 다형성(polymorphism)을 제공하여, 공통된 형태를 공유하는 객체 타입들을 일관되게 모델링하고 다룰 수 있게 합니다.

[인터페이스](../05_interfaces/01_interface-overview.md)에 대해 더 알아보세요.

**설명**: 객체 지향 언어의 인터페이스와 같은 개념입니다. Java에서 `interface Vehicle { String getVin(); }`을 정의하고 `Car`, `Truck` 클래스가 이를 구현하면 `List<Vehicle>`로 둘을 함께 다룰 수 있듯이, 온톨로지에서도 Vehicle 인터페이스를 Car와 Truck 객체 타입이 구현하게 하면 두 객체 타입을 하나의 형태로 함께 조회하고 처리할 수 있습니다.

> **중간 요약**: 온톨로지 리소스에는 객체 타입(과 그 속성), 여러 객체 타입이 함께 쓰는 공유 속성, 관계를 정의하는 링크 타입, 변경 묶음을 정의하는 액션 타입, 분류용 객체 타입 그룹, 다형성을 위한 인터페이스가 있습니다.

<a id="difference-between-object-types-and-objects"></a>
## 객체 타입과 객체의 차이 (Difference between object types and objects)

객체 타입과 객체의 차이를 명확히 하기 위해 아래에 예시를 제공합니다. 같은 구분이 링크 타입과 링크에도 적용됩니다.

<a id="object-type-definitions"></a>
### 객체 타입 정의 (Object type definitions)

객체 타입 정의는 간단히 "객체 타입"이라고도 부르며, 객체 타입, 링크 타입, 액션 타입 같은 온톨로지 엔터티의 타입 수준 정보를 가리킵니다. 예를 들어 객체 타입의 메타데이터에는 표시 이름, 속성 이름, 속성 데이터 타입, 설명 등이 포함될 수 있습니다. 메타데이터는 객체 타입의 속성이나 기본 키(primary key)의 실제 데이터나 값을 가리키지 않습니다. 그런 것은 온톨로지 데이터로 간주됩니다.

<a id="object-instances"></a>
### 객체 인스턴스 (Object instances)

객체 인스턴스는 간단히 "객체"라고도 부르며, 온톨로지 엔터티의 특정 인스턴스가 가진 실제 기본 키와 속성 값을 가리킵니다. 예를 들어 `Airplane` 객체 타입에는 `Plane ID` 속성 값이 `my_plane_id1`이고 `Maximum Occupancy` 속성 값이 `240`인 객체 인스턴스가 있을 수 있습니다.

**설명**: 데이터베이스로 옮기면 객체 타입 정의는 `CREATE TABLE airplane (plane_id VARCHAR PRIMARY KEY, maximum_occupancy INT)`라는 스키마(메타데이터)이고, 객체 인스턴스는 `('my_plane_id1', 240)`이라는 행 하나(데이터)입니다. 이 구분은 권한이나 브랜치를 다룰 때 중요합니다. 스키마를 바꾸는 일과 행의 값을 바꾸는 일은 서로 다른 작업이기 때문입니다.

> **중간 요약**: 객체 타입 정의는 이름, 속성 이름과 데이터 타입, 설명 같은 메타데이터이고, 객체 인스턴스는 실제 기본 키와 속성 값을 가진 데이터입니다. 링크 타입과 링크도 같은 방식으로 구분합니다.

<a id="value-types"></a>
## 값 타입 (Value types)

**값 타입(value type)은** 메타데이터와 제약 조건으로 이루어진, 필드 타입(field type)을 감싸는 의미적 래퍼(semantic wrapper)로서 타입 안전성을 높이고 표현력을 개선하며 추가 맥락을 제공할 수 있습니다. 값 타입은 도메인에 특화된 데이터 타입을 캡슐화하고, 플랫폼 전반에서 재사용 가능한 방식으로 데이터 검증을 강제합니다. 흔히 쓰이는 값 타입으로는 이메일 주소, URL, UUID, 열거형(enumeration)이 있습니다.

필드 타입과 기본 타입(base type)은 정적으로 정의되는 반면, 값 타입은 특정 [스페이스(space)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/)의 맥락 안에서 사용자 정의됩니다. 따라서 사용자는 새로운 필드 타입이나 기본 타입을 만들 수는 없지만, **값 타입**은 동적으로 만들 수 있습니다.

[값 타입에 대해 더 알아보세요.](08_value-types/01_value-types-overview.md)

**설명**: 예를 들어 이메일 주소는 저장 형식으로는 그냥 `string`이지만, 아무 문자열이나 들어가면 안 됩니다. "Email Address" 값 타입은 기본 타입 `string`에 "정규식 `^[^@]+@[^@]+$`에 맞아야 한다"는 제약과 "이메일 주소"라는 의미 정보를 붙인 것입니다. 이 값 타입을 쓰는 모든 속성은 같은 검증 규칙을 자동으로 적용받습니다. 프로그래밍에서 `String`을 그대로 쓰는 대신 생성자에서 형식을 검사하는 `EmailAddress` 클래스를 만들어 쓰는 것과 같은 효과입니다.

> **중간 요약**: 값 타입은 기본 타입에 제약 조건과 의미 메타데이터를 덧씌운 재사용 가능한 타입이며, 기본 타입은 새로 만들 수 없지만 값 타입은 스페이스 안에서 사용자가 만들 수 있습니다.

## 정리

- Foundry의 타입은 도메인을 모델링하는 온톨로지 타입과 값을 표현하는 데이터 타입으로 나뉩니다.
- 온톨로지 리소스에는 객체 타입, 속성, 공유 속성, 링크 타입, 액션 타입, 객체 타입 그룹, 인터페이스가 있습니다.
- 객체 타입 정의는 메타데이터(스키마), 객체 인스턴스는 실제 기본 키와 속성 값(데이터)이며, 링크 타입과 링크도 같은 관계입니다.
- 값 타입은 기본 타입에 제약과 의미를 더한 재사용 가능한 타입으로, 스페이스 안에서 사용자가 만들 수 있습니다.
