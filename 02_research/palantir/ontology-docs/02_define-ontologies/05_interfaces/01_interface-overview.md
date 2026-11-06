# 인터페이스 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/interfaces/interface-overview/
- 사이드바 위치: Define Ontologies > Interfaces > Overview

이 페이지는 온톨로지(Ontology)의 인터페이스(interface)가 무엇이고 객체 타입과 어떻게 다른지, 어떤 요소로 구성되는지, 플랫폼의 어느 애플리케이션에서 지원되는지를 설명합니다. 인터페이스를 쓰면 공통된 형태를 가진 여러 객체 타입을 하나의 타입처럼 다룰 수 있어, 새 객체 타입이 추가되어도 워크플로를 고칠 필요가 줄어듭니다.

**인터페이스(interface)는** 객체 타입의 형태(shape)와 기능(capabilities)을 기술하는 온톨로지 타입입니다. 인터페이스를 사용하면 공통된 형태를 공유하는 객체 타입들을 일관되게 모델링하고 상호작용할 수 있습니다. 예를 들어 `Facility` 인터페이스에 `Facility Name`과 `Location` 속성(property)이 포함될 수 있습니다. `Facility`는 `Airport`, `Manufacturing Plant`, `Maintenance Hangar` 같은 객체 타입이 구현할 수 있으며, 각 객체 타입은 타입별 속성을 추가로 가질 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/interface-example.png" alt="`Facility` 인터페이스 예시." width="800" />

`Facility` 인터페이스를 사용하면 워크플로는 `Airport`, `Manufacturing Plant`, `Maintenance Hangar` 객체 타입의 구체적인 세부 사항을 몰라도, 이들을 한꺼번에 또는 개별적으로 다룰 수 있습니다. 또한 `Facility` 인터페이스를 구현하는 새 객체 타입이 추가되면, 워크플로는 추가 리팩터링 없이 곧바로 새 객체 타입과 호환됩니다.

플랫폼에서 인터페이스를 어디에 사용할 수 있는지는 [현재 지원 수준](01_interface-overview.md#current-levels-of-support)을 참고하세요.

**설명**: 구체적인 데이터로 보면 다음과 같습니다. `Airport` 객체 타입에는 `airportName`, `location`, `runwayCount` 속성이 있고, `Maintenance Hangar` 객체 타입에는 `hangarName`, `location`, `bayCount` 속성이 있다고 합시다. 두 타입이 `Facility` 인터페이스를 구현하면서 `airportName`과 `hangarName`을 각각 인터페이스의 `Facility Name`에 연결하면, "모든 Facility를 지도에 표시"하는 화면은 `Facility Name`과 `Location`만 읽으면 됩니다. 나중에 `Manufacturing Plant`가 같은 인터페이스를 구현하면 그 화면에 자동으로 함께 나타납니다.

> **중간 요약**: 인터페이스는 객체 타입이 가져야 할 공통 형태를 기술하는 온톨로지 타입이며, 이를 통해 여러 객체 타입을 구체적인 타입을 몰라도 한꺼번에 다룰 수 있습니다.

<a id="interface-features"></a>
## 인터페이스의 구성 요소 (Interface features)

인터페이스는 인터페이스 속성, [링크 타입 제약 조건(link type constraints)](06_interface-link-types-overview.md), [액션 타입 제약 조건(action type constraints)](07_interface-action-type-constraints.md), 인터페이스에 대한 [메타데이터](09_interface-metadata.md)로 구성됩니다. 인터페이스 속성은 인터페이스에 로컬로 정의하거나(권장) [공유 속성(shared property)](../02_object-and-link-types/05_shared-properties/01_shared-property-overview.md)을 사용해 정의할 수 있습니다. 하나의 인터페이스는 여러 객체 타입이 구현할 수 있습니다.

프로그래밍 언어의 인터페이스와 마찬가지로, [인터페이스를 확장(extend)](08_extend-interface.md)해서 원래 인터페이스의 속성을 상속받는 자식 인터페이스를 만들고, 그 자식 인터페이스에 더 구체적인 새 속성을 추가할 수 있습니다. 그런 다음 객체 타입이 [인터페이스를 구현](03_implement-interface.md)해서 자신이 인터페이스 정의를 따른다는 것을 나타낼 수 있습니다. 객체 타입은 서로 다른 워크플로에 쓰기 위해 여러 인터페이스를 구현할 수 있습니다. 인터페이스도 여러 다른 인터페이스를 확장할 수 있으며, 다른 인터페이스를 확장한 인터페이스를 다시 확장할 수도 있으므로, 속성이 여러 층의 인터페이스를 거쳐 상속될 수 있습니다.

**설명**: Java로 표현하면 `interface Facility { String facilityName(); Location location(); }`가 있고, `interface Airfield extends Facility { int runwayCount(); }`처럼 확장한 뒤, `class Airport implements Airfield, Taxable`처럼 하나의 클래스가 여러 인터페이스를 구현하는 구조와 대응합니다. 온톨로지에서는 클래스 자리에 객체 타입이 옵니다.

> **중간 요약**: 인터페이스는 속성, 링크 타입 제약 조건, 액션 타입 제약 조건, 메타데이터로 이루어지며, 확장(상속)과 다중 구현이 가능합니다.

<a id="differences-between-interfaces-and-object-types"></a>
## 인터페이스와 객체 타입의 차이 (Differences between interfaces and object types)

온톨로지 안에서 인터페이스와 객체 타입 사이에는 기능상의 차이와 표시 방식의 차이가 모두 있습니다.

객체 타입은 구체적(concrete)입니다. 공유 속성이나 로컬 속성으로 정의된 스키마를 가지며, 속성 값을 담은 데이터셋이 뒷받침(backing)하고, 객체로 인스턴스화할 수 있습니다.

반면 인터페이스는 추상적(abstract)입니다. 인터페이스 속성으로 정의된 스키마를 가지며, 데이터셋이 뒷받침하지 않고, 직접 인스턴스화할 수 없으며 반드시 특정 객체 타입으로 인스턴스화되어야 합니다.

표시 방식 면에서, 플랫폼에서 인터페이스는 아이콘 주위에 점선이 있어 객체 타입과 시각적으로 구분됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/interface-icon-example.png" alt="인터페이스 아이콘 예시" width="100" />

**설명**: 객체 지향 프로그래밍에서 추상 타입은 `new Facility()`처럼 직접 인스턴스를 만들 수 없고, 구체 클래스의 인스턴스를 그 추상 타입으로 바라볼 수만 있습니다. 온톨로지도 같습니다. `Facility` 인터페이스 자체에는 백킹 데이터셋(backing dataset)이 없으므로 "Facility 객체"는 실제로는 항상 `Airport` 객체나 `Maintenance Hangar` 객체입니다.

> **중간 요약**: 객체 타입은 데이터셋이 뒷받침하는 구체 타입이고, 인터페이스는 데이터셋 없이 형태만 정의하는 추상 타입입니다. 인터페이스 아이콘은 점선으로 표시됩니다.

<a id="interface-permissions"></a>
## 인터페이스 권한 (Interface permissions)

인터페이스의 권한은 [온톨로지 역할(Ontology roles)](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#ontology-roles)로 관리됩니다.

<a id="current-levels-of-support"></a>
## 현재 지원 수준 (Current levels of support)

인터페이스 온톨로지 타입에 대한 지원이 확대되는 중이므로, Palantir 플랫폼 전반에서 사용 가능 여부가 다릅니다.

인터페이스는 현재 다음 애플리케이션과 서비스에서 지원됩니다.

* **[Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md):** 인터페이스 정의, 편집, 구현.
* **[Marketplace](https://www.palantir.com/docs/foundry/marketplace/overview/):** 인터페이스 패키징과 설치.
* **[Functions](../04_functions/01_overview.md):** TypeScript v2 함수.

인터페이스는 다음 애플리케이션과 서비스에서 부분적으로 지원됩니다.

* **[Actions](../03_action-types/01_overview.md):** 인터페이스를 구현하는 객체를 생성, 수정, 삭제, 링크하는 액션을 정의할 수 있습니다. 인터페이스 액션 타입 제약 조건은 베타이며, 인터페이스를 구현하는 객체 타입 전반에서 기대되는 액션 기능을 정의하는 데 사용할 수 있습니다.
* **[Object Set Service](../../06_ontology-architecture/01_overview-and-getting-started/01_overview.md#object-set-service-oss):** 인터페이스로 객체를 검색하고 정렬할 수 있습니다. 인터페이스 기준 집계 지원은 개발 중입니다. 인터페이스 링크 타입 지원도 개발 중입니다.
* **[Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/overview/):** 인터페이스를 구현 객체 타입과 상호작용하는 API 계층으로 사용할 수 있습니다. 지원 범위는 언어마다 다릅니다. 현재 TypeScript가 지원되며, Java와 Python 지원은 개발 중입니다.
* **[Workshop](https://www.palantir.com/docs/foundry/workshop/ontology-interfaces/):** 인터페이스 기반 객체 집합(object set)을 만들고, 지원되는 위젯에서 인터페이스 속성을 사용할 수 있습니다. 위젯마다 지원 여부가 달라서, 일부 위젯은 인터페이스 기반 객체 집합을 객체 타입 기반 객체 집합으로 취급합니다.

인터페이스는 활발히 개발 중이지만 다음에서는 아직 지원되지 않습니다.

* **[Functions](../04_functions/01_overview.md):** TypeScript v1 함수와 Python 함수

> **중간 요약**: Ontology Manager, Marketplace, TypeScript v2 함수는 인터페이스를 완전히 지원하고, Actions, Object Set Service, OSDK, Workshop은 부분 지원하며, TypeScript v1과 Python 함수는 아직 지원하지 않습니다.

<a id="get-started-with-interfaces"></a>
## 인터페이스 시작하기 (Get started with interfaces)

온톨로지에 인터페이스를 추가하려면 새 인터페이스를 [만들거나](02_create-interface.md) 기존 인터페이스를 [확장](08_extend-interface.md)할 수 있습니다. 인터페이스가 생기면 적절한 형태를 가진 객체 타입으로 그 인터페이스를 [구현](03_implement-interface.md)하거나, 온톨로지가 발전함에 따라 조직에 더 잘 맞도록 인터페이스를 [편집](04_edit-interface-definition.md)할 수 있습니다.

## 정리

- 인터페이스는 객체 타입의 형태와 기능을 기술하는 추상 온톨로지 타입이며, 여러 객체 타입을 공통 형태로 다룰 수 있게 합니다.
- 인터페이스는 속성, 링크 타입 제약 조건, 액션 타입 제약 조건, 메타데이터로 구성되고, 확장과 다중 구현을 지원합니다.
- 객체 타입과 달리 인터페이스는 데이터셋이 뒷받침하지 않으며 직접 인스턴스화할 수 없습니다.
- 권한은 온톨로지 역할로 관리하며, 지원 범위는 애플리케이션마다 완전, 부분, 미지원으로 나뉩니다.
