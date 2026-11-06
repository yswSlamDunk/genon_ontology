# 인터페이스 구현하기 (Implement an interface)

- 원문: https://www.palantir.com/docs/foundry/interfaces/implement-interface/
- 사이드바 위치: Define Ontologies > Interfaces > Implement an interface

이 페이지는 객체 타입이 인터페이스(interface)를 구현한다는 것이 무엇을 뜻하는지, 그리고 Ontology Manager와 Pipeline Builder에서 실제로 구현을 설정하는 절차를 설명합니다. 구현의 핵심은 객체 타입의 속성(property), 링크 타입, 액션 타입을 인터페이스가 요구하는 항목에 하나씩 매핑하는 것입니다.

인터페이스가 정의되면, 인터페이스 정의를 따르는 모든 객체 타입이 그 인터페이스를 구현할 수 있습니다. 즉 객체 타입은 인터페이스의 필수 속성을 만족하는 속성, 인터페이스에 정의된 모든 필수 링크 타입 제약 조건을 만족하는 링크, 모든 필수 액션 타입 제약 조건을 만족하는 액션 타입을 가지고 있어야 합니다.

객체 타입으로 인터페이스를 구현한다는 것은 그 객체 타입이 온톨로지 안에서 인터페이스의 구체적인 인스턴스라는 것을 나타냅니다. 이 선언으로 객체 타입에 다음과 같은 추가 기능이 생깁니다.

* 인터페이스를 대상으로 한 Object Set Service 검색이 구현 객체 타입의 일치하는 객체를 반환합니다.
* 구현 객체 타입의 객체는, 구체적인 객체 타입으로 다룰 때는 로컬 API 이름으로, 인터페이스 타입으로 다룰 때는 속성과 링크의 인터페이스 API 이름으로 상호작용할 수 있습니다.

요약하면, 인터페이스를 구현하면 애플리케이션 사용자는 구현된 모든 객체를 인터페이스 정의를 통해 다룰 수 있습니다. 덕분에 애플리케이션이 모든 구현 객체 타입을 하나하나 지원할 필요 없이, 인터페이스를 API 계층으로 삼아 애플리케이션 코드를 작성할 수 있습니다. 또한 인터페이스를 애플리케이션 API 계층으로 사용하면, 새 객체 타입이 애플리케이션 인터페이스를 구현하게 하는 것만으로 애플리케이션에 추가할 수 있어 새 객체 타입을 명시적으로 지원하기 위한 코드 변경이 필요 없습니다.

**설명**: "로컬 API 이름"과 "인터페이스 API 이름"의 차이를 예로 보면 다음과 같습니다. `Airport` 객체 타입의 속성 `airportName`이 `Facility` 인터페이스의 속성 `facilityName`에 매핑되어 있다고 합시다. 코드가 객체를 `Airport` 타입으로 받으면 `airportName`으로 읽고, `Facility` 타입으로 받으면 같은 값을 `facilityName`으로 읽습니다. 그래서 `Facility`만 아는 코드는 `Airport`든 `Maintenance Hangar`든 같은 이름으로 값을 꺼낼 수 있습니다.

> **중간 요약**: 객체 타입이 인터페이스의 필수 속성, 링크, 액션 요건을 만족하면 구현할 수 있고, 구현하면 인터페이스 기준 검색과 인터페이스 API 이름으로 객체를 다룰 수 있게 됩니다.

<a id="how-to-implement-an-interface-in-ontology-manager"></a>
## Ontology Manager에서 인터페이스 구현하기 (How to implement an interface in Ontology Manager)

아래 단계에 따라 객체 타입으로 인터페이스를 구현하세요.

<a id="1-select-your-interface-and-object-type"></a><a id="select-your-interface-and-object-type"></a>
### 1. 인터페이스와 객체 타입 선택하기 (Select your interface and object type)

먼저 Ontology Manager에서 객체 타입으로 이동해 **Interfaces** 탭을 엽니다. 페이지 오른쪽 위에서 **+ Implement new interface**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-from-object-type.png" alt="객체 타입에서 인터페이스 구현하기." width="800" />

나타나는 대화 상자에서 구현할 인터페이스를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-select-interface.png" alt="구현할 인터페이스 선택." width="800" />

또는 인터페이스 개요 페이지로 이동해 **Implementations** 섹션에서 **+ New**를 선택할 수도 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-from-interface-overview.png" alt="인터페이스 개요에서 인터페이스 구현하기." width="800" />

그런 다음 인터페이스를 구현할 객체 타입을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-select-object-type.png" alt="인터페이스를 구현할 객체 타입 선택." width="800" />

<a id="2-map-local-properties"></a><a id="map-local-properties"></a>
### 2. 로컬 속성 매핑하기 (Map local properties)

인터페이스를 구현하려면 객체 타입은 기존 객체 속성을 인터페이스의 필수 속성에 매핑하는 선언을 해야 합니다. 인터페이스 속성이 **optional**로 표시되어 있으면 매핑을 건너뛸 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-map-properties.png" alt="인터페이스와 구현 객체 타입 사이의 속성 매핑." width="800" />

<a id="3-map-link-type-constraints"></a><a id="map-link-type-constraints"></a>
### 3. 링크 타입 제약 조건 매핑하기 (Map link type constraints)

인터페이스에 필수 [링크 타입 제약 조건](06_interface-link-types-overview.md)이 선언되어 있다면, 각 필수 링크 타입 제약 조건을 만족하는 링크 타입을 객체 타입에서 선택해야 합니다. 필수가 아닌 링크 타입 제약 조건에도 선택적으로 링크 매핑을 제공할 수 있습니다. 각 제약 조건을 만족시키기 위해 기존 링크 타입을 고르거나 새 링크 타입을 만들 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-link-type-constraint.png" alt="링크 타입 제약 조건을 만족하도록 링크 타입 매핑." width="800" />

<a id="4-map-action-type-constraints"></a><a id="map-action-type-constraints"></a>
### 4. 액션 타입 제약 조건 매핑하기 (Map action type constraints)

인터페이스에 필수 [액션 타입 제약 조건](07_interface-action-type-constraints.md)이 선언되어 있다면, 각 필수 액션 타입 제약 조건을 만족하는 액션 타입을 객체 타입에서 선택해야 합니다. 필수가 아닌 액션 타입 제약 조건에도 선택적으로 액션 매핑을 제공할 수 있습니다.

인터페이스 구현이 만들어진 뒤에는 객체 타입의 **Interfaces** 탭에서 파라미터 매핑을 구성합니다. 온톨로지에 변경 사항을 저장하기 전에, 모든 필수 파라미터 제약 조건을 구체적인 액션 타입의 호환되는 필수 파라미터에 매핑해야 합니다.

**설명**: 액션 타입 제약 조건에는 "이 액션은 이런 파라미터를 받아야 한다"는 파라미터 제약 조건이 함께 있을 수 있습니다. 예를 들어 제약 조건이 `newStatus`라는 문자열 파라미터를 요구하면, 매핑할 실제 액션 타입의 문자열 필수 파라미터(예: `status`) 하나를 그 제약 조건에 연결해야 저장할 수 있습니다.

<a id="5-save-changes"></a><a id="save-changes"></a>
### 5. 변경 사항 저장하기 (Save changes)

**Save**를 선택해 온톨로지에 변경 사항을 반영합니다.

> **중간 요약**: Ontology Manager에서는 객체 타입의 **Interfaces** 탭이나 인터페이스의 **Implementations** 섹션에서 시작해, 속성, 링크 타입 제약 조건, 액션 타입 제약 조건(파라미터 포함)을 차례로 매핑하고 저장합니다.

<a id="how-to-implement-an-interface-in-pipeline-builder"></a>
## Pipeline Builder에서 인터페이스 구현하기 (How to implement an interface in Pipeline Builder)

아래 단계에 따라 Pipeline Builder의 [객체 타입 출력(object type output)](https://www.palantir.com/docs/foundry/pipeline-builder/outputs-add-ontology-output/#add-an-object-type-output)에서 인터페이스를 구현하세요.

**설명**: Pipeline Builder는 데이터 변환 파이프라인을 만드는 Foundry 애플리케이션이며, 파이프라인의 결과를 데이터셋뿐 아니라 온톨로지 객체 타입으로 직접 내보낼 수 있습니다. 이 내보내기 대상을 객체 타입 출력이라고 합니다.

<a id="1-open-output-type-configuration"></a><a id="open-output-type-configuration"></a>
### 1. 출력 타입 구성 열기 (Open output type configuration)

인터페이스를 구현할 객체 타입 출력을 선택한 다음 **Edit** 옵션을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-interface-object-type-output-edit.png" alt="객체 타입 출력 편집." width="800" />

<a id="2-select-the-interface-to-implement"></a><a id="select-the-interface-to-implement"></a>
### 2. 구현할 인터페이스 선택하기 (Select the interface to implement)

**Implement interface**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-interface-pipeline-builder-implement-button.png" alt="Implement interface 선택." width="800" />

그런 다음 구현할 인터페이스를 선택하고 **Implement and go to mapping**을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-interface-pipeline-builder-selection.png" alt="인터페이스를 선택하고 매핑으로 이동." width="800" />

<a id="3-map-local-properties"></a><a id="map-local-properties"></a>
### 3. 로컬 속성 매핑하기 (Map local properties)

인터페이스를 구현하려면 객체 타입이 인터페이스의 공유 속성을 포함하고 있거나, **또는** 기존 객체 속성을 인터페이스 공유 속성에 매핑하는 선언을 해야 합니다. 인터페이스와 객체 타입 양쪽에 모두 있는 공유 속성은 자동으로 매핑됩니다. 객체 타입에 없는 공유 속성은 인터페이스 정의를 만족하도록 매핑을 직접 입력해야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-interface-pipeline-builder-mapping.png" alt="로컬 속성 매핑." width="800" />

<a id="4-review-implemented-interfaces"></a><a id="review-implemented-interfaces"></a>
### 4. 구현된 인터페이스 검토하기 (Review implemented interfaces)

출력 타입 구성 패널에서 이 객체 타입 출력이 구현한 인터페이스를 볼 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/implement-interface-pipeline-builder-review.png" alt="구현된 인터페이스 검토." width="800" />

**주의**: Pipeline Builder는 현재 인터페이스를 구현할 때 링크 타입 제약 조건이나 액션 타입 제약 조건 매핑을 지원하지 않습니다. 인터페이스에 필수 링크 타입 제약 조건이나 필수 액션 타입 제약 조건이 있다면 Ontology Manager에서 인터페이스를 구현해야 합니다.

> **중간 요약**: Pipeline Builder에서는 객체 타입 출력의 **Edit**에서 **Implement interface**를 골라 속성을 매핑합니다. 링크나 액션 제약 조건이 필수인 인터페이스는 Ontology Manager에서만 구현할 수 있습니다.

## 정리

- 인터페이스 구현은 객체 타입이 인터페이스의 필수 속성, 링크 타입 제약 조건, 액션 타입 제약 조건을 만족한다고 선언하는 것입니다.
- 구현하면 인터페이스 기준 검색에 그 객체 타입의 객체가 포함되고, 인터페이스 API 이름으로도 객체를 다룰 수 있습니다.
- Ontology Manager에서는 속성, 링크 타입, 액션 타입(파라미터 포함)을 매핑한 뒤 저장합니다.
- Pipeline Builder에서는 속성 매핑만 지원하므로 링크나 액션 제약 조건이 필수인 경우 Ontology Manager를 사용해야 합니다.
