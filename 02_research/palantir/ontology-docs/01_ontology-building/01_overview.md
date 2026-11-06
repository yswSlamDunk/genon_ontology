# 온톨로지 구축 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/ontology/overview/
- 사이드바 위치: Ontology building > Overview

이 페이지는 Palantir 온톨로지(Ontology)가 무엇인지, 그리고 온톨로지를 이루는 큰 구성 요소(객체 타입, 링크 타입, 액션 타입, 함수, 인터페이스)가 각각 어떤 역할을 하는지 소개하는 입구 페이지입니다. 이후 문서 전체가 이 구성 요소들을 하나씩 자세히 다루므로, 여기서 전체 지도를 먼저 잡아 두면 나머지 페이지를 읽기 쉬워집니다.

![온톨로지 개요 헤더 이미지.](https://www.palantir.com/docs/resources/foundry/ontology/ontology-overview-header.png)

Palantir **온톨로지는** 조직을 위한 운영 계층(operational layer)입니다. 온톨로지는 Palantir 플랫폼에 통합된 디지털 자산([데이터셋](https://www.palantir.com/docs/foundry/data-integration/datasets/), [가상 테이블](https://www.palantir.com/docs/foundry/data-integration/virtual-tables/), [모델](https://www.palantir.com/docs/foundry/integrate-models/integrate-overview/)) 위에 자리 잡고, 이 자산들을 현실 세계의 대응물과 연결합니다. 대응물은 공장, 장비, 제품 같은 물리적 자산부터 고객 주문이나 금융 거래 같은 개념까지 다양합니다. 많은 환경에서 온톨로지는 조직의 디지털 트윈(digital twin) 역할을 하며, 모든 종류의 사용 사례를 가능하게 하는 데 필요한 의미적 요소(semantic elements: 객체, 속성(property), 링크)와 동적 요소(kinetic elements: 액션, 함수(function), 동적 보안)를 모두 담고 있습니다.

**설명**: "운영 계층"이란 데이터를 저장해 두고 조회만 하는 층이 아니라, 사용자가 실제 업무를 처리하면서 데이터를 읽고 바꾸는 층이라는 뜻입니다. 예를 들어 `orders`라는 데이터셋에 주문 행이 쌓여 있다면, 온톨로지는 이 행들을 "주문(Order)"이라는 객체로 보여 주고, 사용자가 "주문 취소" 같은 액션을 실행해 상태를 바꿀 수 있게 합니다. "디지털 트윈"은 현실의 공장, 장비, 주문 등을 소프트웨어 안에서 같은 구조로 표현한 모델을 가리키는 용어입니다. "의미적(semantic)" 요소는 데이터가 무엇을 뜻하는지 정의하는 부분(명사에 해당), "동적(kinetic)" 요소는 데이터를 바꾸거나 계산하는 부분(동사에 해당)입니다.

<a id="object-and-link-types"></a>
## 객체 타입과 링크 타입 (Object and link types)

조직의 의미 체계(semantics)를 정의하는 일은 기존 데이터소스를 온톨로지의 **객체, 속성, 링크로** 매핑하는 방식으로 이루어집니다. 온톨로지는 단순한 데이터 카탈로그나 스키마 설계 도구를 훨씬 넘어서, 최종 사용자 워크플로를 위한 견고한 기반을 정의할 수 있게 해 줍니다. 여기에는 모든 필드에 대한 풍부한 메타데이터와, 모든 변경에 대한 세밀한 보안 및 거버넌스가 포함됩니다.

온톨로지의 의미적 요소를 만드는 방법은 [객체 타입](../02_define-ontologies/02_object-and-link-types/02_object-types/01_object-types-overview.md)과 [링크 타입](../02_define-ontologies/02_object-and-link-types/06_link-types/01_link-types-overview.md) 문서에서 알아보세요.

**설명**: 데이터베이스 관점으로 보면, 객체 타입은 테이블 정의(스키마), 객체는 테이블의 행 하나, 속성은 열, 링크는 외래 키로 연결된 두 행의 관계에 대응합니다. 예를 들어 `employees` 테이블(열: `id`, `name`, `dept_id`)을 매핑하면 Employee 객체 타입이 생기고, `dept_id`로 `departments` 테이블과 연결된 관계는 Employee와 Department 사이의 링크 타입이 됩니다. "거버넌스(governance)"는 누가 무엇을 바꿀 수 있는지, 변경 이력을 어떻게 관리하는지에 대한 규칙과 통제를 말합니다.

> **중간 요약**: 기존 데이터소스를 객체, 속성, 링크로 매핑해 조직의 의미 체계를 정의합니다. 이는 단순한 스키마 설계를 넘어 메타데이터, 보안, 거버넌스까지 포함합니다.

<a id="action-types-and-functions"></a>
## 액션 타입과 함수 (Action types and functions)

조직의 동적 측면, 즉 조직의 통제와 거버넌스를 지키면서 변경을 가능하게 하는 부분은 온톨로지에서 **액션 타입(action type)과 함수(function)로** 정의합니다. 액션 타입을 사용하면 조직 내 실무자(operator)로부터 데이터를 입력받거나, 기존 시스템과 연결되는 의사결정 프로세스를 조율(orchestrate)할 수 있습니다. 함수는 임의의 복잡도를 가진 비즈니스 로직을 작성하고 발전시킬 수 있는 수단을 제공합니다.

온톨로지의 동적 요소를 만드는 방법은 [액션 타입](../02_define-ontologies/03_action-types/01_overview.md)과 [함수](../02_define-ontologies/04_functions/01_overview.md) 문서에서 알아보세요.

**설명**: 액션 타입은 "어떤 입력을 받아 어떤 객체를 어떻게 바꾸는가"를 미리 정해 둔 변경 양식입니다. 예를 들어 "티켓 담당자 지정" 액션 타입은 입력으로 티켓과 담당자를 받고, 해당 티켓 객체의 `assignee` 속성을 바꿉니다. SQL로 치면 미리 정의된 `UPDATE` 문에 권한 검사와 입력 검증을 붙여 둔 것에 해당합니다. 함수는 TypeScript나 Python 같은 코드로 작성하는 로직으로, 입력(객체, 숫자 등)을 받아 계산 결과를 돌려주거나 편집(edit)을 만들어 냅니다.

> **중간 요약**: 데이터를 바꾸는 동작은 액션 타입으로, 복잡한 비즈니스 로직은 함수로 정의합니다.

<a id="interfaces"></a>
## 인터페이스 (Interfaces)

**인터페이스는** 객체 타입의 형태(shape)와 기능을 기술하는 온톨로지 타입입니다. 인터페이스는 객체 타입 다형성(polymorphism)을 제공하여, 공통된 형태를 공유하는 객체 타입들을 일관되게 모델링하고 다룰 수 있게 해 줍니다.

[인터페이스](../02_define-ontologies/05_interfaces/01_interface-overview.md)에 대해 더 알아보세요.

**설명**: 객체 지향 프로그래밍의 인터페이스와 같은 개념입니다. 예를 들어 Java에서 `Vehicle` 인터페이스가 `getLocation()`을 요구하면 `Truck`과 `Ship` 클래스가 모두 이를 구현하고, 호출하는 쪽은 둘을 구분하지 않고 `Vehicle`로 다룰 수 있습니다. 온톨로지에서도 Truck 객체 타입과 Ship 객체 타입이 같은 인터페이스(예: 위치 속성을 가진 "Vehicle")를 구현하면, 애플리케이션은 두 타입을 한꺼번에 조회하고 처리할 수 있습니다.

> **중간 요약**: 인터페이스는 여러 객체 타입이 공유하는 공통 형태를 정의해, 이들을 하나의 타입처럼 다룰 수 있게 합니다.

<a id="powering-decision-making"></a>
## 의사결정 지원 (Powering decision-making)

온톨로지에 투자하는 목적은 조직 전체 규모에서 더 나은 의사결정을 돕는 데 있습니다. 이를 위해 온톨로지는 Palantir의 사용자용 분석 도구와 운영 도구에 깊이 통합되어 있습니다. 사용자는 재사용 가능한 Object View를 만들고, Object Explorer에서 관심 있는 객체를 검색하고, Quiver에서 복잡한 분석을 수행하고, Workshop에서 품질 높은 애플리케이션을 만드는 등의 작업을 할 수 있습니다.

[사용자용 애플리케이션에서 온톨로지를 활용하는 방법을 더 알아보세요.](05_applications.md) 이제 이론을 알았으니, [Palantir Learning 포털의 강좌 ↗](https://learn.palantir.com/deep-dive-creating-your-first-ontology)로 첫 번째 온톨로지 구축을 시작해 보세요.

> **중간 요약**: 온톨로지는 Object View, Object Explorer, Quiver, Workshop 같은 사용자 도구와 통합되어 실제 의사결정에 쓰입니다.

## 정리

- 온톨로지는 데이터셋, 가상 테이블, 모델 위에 놓여 이를 현실 세계의 대상과 연결하는 운영 계층입니다.
- 의미적 요소(객체, 속성, 링크)는 "데이터가 무엇을 뜻하는가"를, 동적 요소(액션, 함수, 동적 보안)는 "데이터를 어떻게 바꾸고 계산하는가"를 정의합니다.
- 인터페이스는 공통 형태를 가진 객체 타입들에 다형성을 제공합니다.
- 온톨로지는 Workshop, Quiver, Object Explorer 등 사용자 도구와 연결되어 의사결정을 지원합니다.
