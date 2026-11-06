# 핵심 개념 (Core concepts)

- 원문: https://www.palantir.com/docs/foundry/ontology/core-concepts/
- 사이드바 위치: Ontology building > Core concepts

이 페이지는 Foundry 온톨로지(Ontology)를 이루는 주요 개념(객체 타입, 속성, 공유 속성, 링크 타입, 액션 타입, 역할, 함수, 인터페이스, Object View)의 정의를 한곳에 모아 둔 용어집 성격의 페이지입니다. 특히 데이터셋의 구조(행, 열, 조인)와 온톨로지 개념을 일대일로 대응시킨 표가 있어, 데이터베이스 지식을 바탕으로 온톨로지를 이해하는 출발점이 됩니다.

이 페이지는 Foundry의 온톨로지와 관련된 주요 개념을 설명합니다.

<a id="ontology"></a>
## 온톨로지 (Ontology)

온톨로지는 세계를 범주화한 것입니다. Foundry에서 온톨로지는 조직의 디지털 트윈(digital twin)으로서, 조직의 디지털 자산(데이터셋과 모델)을 하나의 일관된 전체로 통합합니다. Foundry 온톨로지는 데이터셋과 모델을 객체 타입, 속성(property), 링크 타입, 액션 타입에 매핑함으로써 조직의 세계에 대한 완전한 그림을 만들어 냅니다.

* [객체 타입](#object-type)은 조직 내의 엔터티(entity)나 이벤트를 정의합니다.
* [속성](#property)은 객체 타입의 특성을 정의합니다.
* [링크 타입](#link-type)은 두 객체 타입 사이의 관계를 정의합니다.
* [액션 타입](#action-type)은 객체 타입을 어떻게 수정할 수 있는지 정의합니다.

온톨로지를 구성하는 개념들은 데이터셋의 구조와 대응 관계를 가집니다. 각 객체 타입은 데이터셋에 대응한다고 생각할 수 있습니다. 행이 데이터셋의 항목 하나인 것처럼, 객체는 객체 타입의 인스턴스입니다. 데이터셋의 열은 주어진 행에 대한 추가 정보를 제공하므로 객체의 속성에 대응합니다. 데이터셋 필드의 값(스프레드시트의 셀 하나)은 객체의 속성 값에 해당합니다. 그리고 데이터셋을 다양한 방식으로 조인할 수 있는 것처럼, 객체 사이에도 속성 값을 기준으로 링크가 존재할 수 있습니다. 아래 표는 이 비교를 요약합니다.

|데이터셋 |온톨로지       |
|---    |---            |
|데이터셋(Dataset)  |객체 타입(Object type)    |
|행(Row)      |객체(Object)         |
|열(Column)   |속성(Property)       |
|필드(Field)    |속성 값(Property value) |
|조인(Join)     |링크 타입(Link type)      |

**설명**: 구체적인 예로 `flights` 데이터셋이 다음과 같다고 합시다.

| flight_id | origin | destination | aircraft_id |
|---|---|---|---|
| F100 | JFK | SFO | A1 |
| F101 | SFO | ORD | A2 |
| F102 | ORD | JFK | A1 |

이 데이터셋을 매핑하면 Flight 객체 타입이 생기고, 세 행은 각각 Flight 객체 3개(F100, F101, F102)가 됩니다. `origin`, `destination` 등의 열은 Flight의 속성이 되고, F100 행의 `origin` 칸에 있는 "JFK"는 F100 객체의 속성 값입니다. 또 `aircraft_id`가 `aircraft` 데이터셋의 기본 키(primary key)를 가리킨다면, SQL에서 `flights JOIN aircraft ON flights.aircraft_id = aircraft.aircraft_id`로 조인하던 관계를 Flight와 Aircraft 사이의 링크 타입으로 정의할 수 있습니다. 객체 지향 관점에서는 객체 타입이 클래스, 객체가 그 클래스의 인스턴스에 해당합니다.

아래 다이어그램은 이 개념들이 어떻게 모여 온톨로지를 이루는지 보여 줍니다. 이어지는 내용에서 온톨로지의 각 구성 요소를 더 자세히 정의합니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology/airline-ontology.png" alt="항공 온톨로지" height="500" />

> **중간 요약**: 온톨로지는 데이터셋과 모델을 객체 타입, 속성, 링크 타입, 액션 타입에 매핑한 것입니다. 데이터셋, 행, 열, 필드, 조인이 각각 객체 타입, 객체, 속성, 속성 값, 링크 타입에 대응합니다.

<a id="object-type"></a>
## 객체 타입 (Object type)

**객체 타입(object type)은** 현실 세계의 엔터티나 이벤트에 대한 스키마 정의입니다. **객체(object)는** 객체 타입의 인스턴스 하나를 가리키며, 하나의 현실 세계 엔터티나 이벤트에 대응합니다. **객체 집합(object set)은** 여러 객체 인스턴스의 모음을 가리킵니다. 즉, 객체 집합은 현실 세계 엔터티나 이벤트의 그룹을 나타냅니다.

[객체 타입에 대해 더 알아보세요.](../02_define-ontologies/02_object-and-link-types/02_object-types/01_object-types-overview.md)

**설명**: 객체 집합은 SQL 질의 결과로 얻는 행들의 집합에 해당합니다. 예를 들어 "출발지가 JFK인 모든 Flight"는 `SELECT * FROM flights WHERE origin = 'JFK'`의 결과와 같은 범위의 객체 집합입니다. 엔터티(entity)는 직원, 항공기처럼 지속적으로 존재하는 대상이고, 이벤트(event)는 비행, 정비 작업처럼 특정 시점에 일어난 일입니다. 둘 다 객체 타입으로 표현할 수 있습니다.

<a id="property"></a>
## 속성 (Property)

객체 타입의 **속성(property)은** 현실 세계 엔터티나 이벤트의 특성에 대한 스키마 정의입니다. **속성 값(property value)은** 객체의 특정 속성에 들어 있는 값, 즉 해당 현실 세계 엔터티나 이벤트의 단일 인스턴스가 가진 값을 가리킵니다.

[속성에 대해 더 알아보세요.](../02_define-ontologies/02_object-and-link-types/03_properties/01_properties-overview.md)

<a id="shared-property"></a>
## 공유 속성 (Shared property)

**공유 속성(shared property)은** 온톨로지의 여러 객체 타입에서 사용할 수 있는 속성입니다. 공유 속성을 사용하면 객체 타입 전반에서 일관된 데이터 모델링을 할 수 있고, 속성 메타데이터를 중앙에서 관리할 수 있습니다.

[공유 속성에 대해 더 알아보세요.](../02_define-ontologies/02_object-and-link-types/05_shared-properties/01_shared-property-overview.md)

**설명**: 예를 들어 Employee, Contractor, Customer 객체 타입이 모두 "이메일 주소" 속성을 가진다고 합시다. 각 타입에서 따로 정의하면 이름(`email`, `emailAddress`, `mail`)이나 설명이 제각각이 될 수 있습니다. 공유 속성 `email` 하나를 정의해 세 객체 타입에 붙이면 이름, 타입, 설명 같은 메타데이터를 한곳에서 관리할 수 있고, 한 번 수정하면 세 타입에 모두 반영됩니다.

<a id="link-type"></a>
## 링크 타입 (Link type)

**링크 타입(link type)은** 두 객체 타입 사이의 관계에 대한 스키마 정의입니다. **링크(link)는** 두 객체 사이에 존재하는 그 관계의 인스턴스 하나를 가리킵니다.

[링크 타입에 대해 더 알아보세요.](../02_define-ontologies/02_object-and-link-types/06_link-types/01_link-types-overview.md)

<a id="action-type"></a>
## 액션 타입 (Action type)

**액션 타입(action type)은** 사용자가 한 번에 수행할 수 있는, 객체, 속성 값, 링크에 대한 변경 또는 편집(edit)의 집합에 대한 스키마 정의입니다. 여기에는 액션이 제출될 때 일어나는 부수 효과(side effect) 동작도 포함됩니다. 온톨로지에서 액션 타입을 구성하고 나면, 최종 사용자는 액션을 적용해 객체를 변경할 수 있습니다.

[액션 타입에 대해 더 알아보세요.](../02_define-ontologies/03_action-types/01_overview.md)

**설명**: "한 번에 수행할 수 있는 변경의 집합"이라는 점에서 데이터베이스 트랜잭션과 연결해 이해할 수 있습니다. 예를 들어 "항공기 교체" 액션 타입은 한 번 제출로 Flight 객체의 `aircraft_id` 속성을 바꾸고, 기존 Aircraft와의 링크를 끊고 새 Aircraft와 링크를 맺는 여러 편집을 함께 수행할 수 있습니다. 부수 효과는 이런 데이터 편집 외에 추가로 일어나는 동작으로, 예를 들어 담당자에게 알림을 보내거나 외부 시스템에 요청을 보내는 것입니다.

> **중간 요약**: 객체 타입은 엔터티나 이벤트의 스키마, 속성은 그 특성, 공유 속성은 여러 객체 타입이 함께 쓰는 속성, 링크 타입은 두 객체 타입의 관계, 액션 타입은 한 번에 수행하는 편집의 묶음과 부수 효과를 정의합니다.

<a id="roles"></a>
## 역할 (Roles)

**역할(role)은** 온톨로지의 중심 권한 모델입니다. Foundry 파일 시스템의 역할과 마찬가지로, 온톨로지 역할은 온톨로지 리소스에 대한 접근 권한을 부여합니다. 역할은 온톨로지 수준에서 부여할 수도 있고 개별 리소스 수준에서 부여할 수도 있습니다.

[온톨로지 역할](../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)과, 역할이 객체 타입, 링크 타입, 액션 타입에 어떻게 사용되는지 더 알아보세요.

**설명**: 역할 기반 접근 제어(RBAC)는 사용자에게 개별 권한을 직접 주는 대신 "Owner", "Editor", "Viewer" 같은 역할을 주고, 역할마다 허용되는 작업을 정해 두는 방식입니다. "온톨로지 수준에서 부여"하면 그 온톨로지 안의 리소스 전반에 적용되고, "개별 리소스 수준에서 부여"하면 특정 객체 타입 하나 같은 단일 리소스에만 적용됩니다.

<a id="functions"></a>
## 함수 (Functions)

**함수(function)는** 입력 파라미터를 받아 출력을 반환하는 코드 기반 로직입니다. 함수는 온톨로지와 기본적으로 통합되어 있습니다. 함수는 객체와 객체 집합을 입력으로 받을 수 있고, 객체의 속성 값을 읽을 수 있으며, 온톨로지 위에 구축된 액션 타입과 애플리케이션 전반에서 사용될 수 있습니다.

[함수 전반에 대해 더 알아보거나](../02_define-ontologies/04_functions/01_overview.md), [온톨로지 기반 함수에 대해 더 알아보세요](../02_define-ontologies/04_functions/13_functions-on-objects/01_functions-on-objects.md).

<a id="interfaces"></a>
## 인터페이스 (Interfaces)

**인터페이스(interface)는** 객체 타입의 형태(shape)와 기능을 기술하는 온톨로지 타입입니다. 인터페이스는 객체 타입 다형성(polymorphism)을 제공하여, 공통된 형태를 공유하는 객체 타입들을 일관되게 모델링하고 다룰 수 있게 해 줍니다.

[인터페이스](../02_define-ontologies/05_interfaces/01_interface-overview.md)에 대해 더 알아보세요.

**설명**: 프로그래밍 언어의 인터페이스와 같은 개념입니다. 예를 들어 Airport 객체 타입과 Heliport 객체 타입이 모두 `name`과 `location` 속성을 가진다면, 이 두 속성을 요구하는 "Facility" 인터페이스를 정의하고 두 객체 타입이 이를 구현하게 할 수 있습니다. 그러면 Facility를 입력으로 받는 함수나 화면은 Airport와 Heliport를 구분하지 않고 함께 처리할 수 있습니다.

<a id="object-views"></a>
## Object View

**Object View는** 특정 객체와 관련된 모든 정보와 워크플로를 모아 둔 중심 허브입니다. 여기에는 객체에 대한 핵심 정보, 링크된 객체, 관련 지표뿐 아니라, 해당 객체와 관련된 분석, 대시보드, 애플리케이션이 포함됩니다.

[Object View에 대해 더 알아보세요.](../05_applications/03_object-views/01_overview.md)

> **중간 요약**: 역할은 온톨로지 리소스에 대한 권한 모델, 함수는 객체를 입력으로 다룰 수 있는 코드 기반 로직, 인터페이스는 공통 형태를 가진 객체 타입의 다형성, Object View는 객체 하나에 대한 정보와 워크플로를 모은 화면입니다.

## 정리

- 온톨로지는 데이터셋과 모델을 객체 타입, 속성, 링크 타입, 액션 타입에 매핑해 조직을 표현합니다.
- 데이터셋, 행, 열, 필드, 조인은 각각 객체 타입, 객체, 속성, 속성 값, 링크 타입에 대응합니다.
- 공유 속성은 여러 객체 타입이 같은 속성 정의를 쓰게 하고, 인터페이스는 공통 형태를 가진 객체 타입을 하나처럼 다루게 합니다.
- 액션 타입은 편집의 묶음과 부수 효과를, 함수는 코드 기반 로직을 정의합니다.
- 역할은 온톨로지 수준이나 개별 리소스 수준에서 접근 권한을 부여하고, Object View는 객체 하나의 정보 허브 역할을 합니다.
