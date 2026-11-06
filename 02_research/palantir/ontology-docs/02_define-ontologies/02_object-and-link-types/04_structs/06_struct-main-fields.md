# 구조체 주 필드 지정하기 (Designate struct main fields)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/struct-main-fields/
- 사이드바 위치: Define Ontologies > Object and link types > Structs > Designate struct main fields

이 페이지는 구조체(struct) 속성의 필드 가운데 "핵심 값"에 해당하는 필드를 주 필드(main field)로 지정하는 기능을 설명합니다. 주 필드를 지정하면 표나 목록처럼 좁은 화면에서는 핵심 필드만 보여 주고, 필요할 때 나머지 메타데이터 필드를 펼쳐 볼 수 있습니다. 또 인터페이스를 구현할 때 구조체의 특정 필드 하나를 인터페이스 속성에 대응시키는 방법과, 속성 리듀서(property reducer)와 함께 쓰는 방법도 다룹니다.

**참고**: 베타(Beta). 구조체 주 필드는 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며, 사용 중인 환경(enrollment)에서는 제공되지 않을 수 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다.

**구조체 주 필드(struct main fields)는** [구조체](01_structs-overview.md)의 핵심 값과 보조 메타데이터를 구분해 지정할 수 있게 해 줍니다. 예를 들어 `Address` 구조체는 `streetName`과 `postalCode`를 담는 필드를 주 값으로 가질 수 있고, `collectionDate`와 `collectorName` 같은 다른 필드는 그 `Address`를 어떻게 수집했는지 설명하는 메타데이터를 나타낼 수 있습니다.

많은 구조체 속성이 이런 패턴을 따릅니다. 하나 이상의 필드는 애플리케이션에서 가장 보여 주고 싶은 주된 데이터를 담고, 다른 필드는 맥락, 추적 정보, 감사(audit) 세부 정보를 제공합니다.

[지원되는 구조체 필드 타입](01_structs-overview.md#struct-configuration)이라면 무엇이든 주 필드로 지정할 수 있습니다.

**설명**: 위 `Address` 예를 값으로 쓰면 다음과 같습니다.

| 필드 | 값 | 역할 |
|---|---|---|
| `streetName` | Teheran-ro 123 | 주 필드 |
| `postalCode` | 06236 | 주 필드 |
| `collectionDate` | 2024-03-01 | 메타데이터 |
| `collectorName` | Kim | 메타데이터 |

표 위젯에서는 "Teheran-ro 123, 06236"만 보이고, 수집일과 수집자는 펼치거나 마우스를 올렸을 때 보이는 식입니다. 데이터베이스 관점에서는 한 행 안에 "업무 데이터 열"과 "이력, 감사 열"이 섞여 있을 때 기본 화면에서 업무 데이터 열만 SELECT해 보여 주는 것과 결과가 같습니다.

<a id="when-to-use-struct-main-fields"></a>
## 구조체 주 필드를 사용해야 하는 경우

다음과 같은 경우 구조체 주 필드를 사용합니다.

* 구조체에 핵심 값 필드와 함께 보조 메타데이터를 나타내는 필드가 들어 있을 때
* 메타데이터에 대한 접근은 잃지 않으면서 표 표시를 더 깔끔하게 하고 싶을 때
* 구조체의 필드 하나 또는 일부 필드만 사용해 [인터페이스를 구현](../../05_interfaces/03_implement-interface.md)해야 할 때

> **중간 요약**: 주 필드는 구조체의 핵심 값 필드를 표시해 두는 기능입니다. 표시를 간결하게 하거나 인터페이스를 구조체 일부 필드로 구현하려 할 때 씁니다.

<a id="configure-struct-main-fields"></a>
## 구조체 주 필드 설정하기

1. **Ontology Manager**로 이동합니다.
2. 왼쪽 패널의 **Resources** 아래에서 **Object types**를 선택해 객체 타입을 검색하고 선택합니다.
3. 객체 타입의 **Properties** 탭에서 설정할 구조체 속성을 선택합니다.
4. 오른쪽에 나타나는 속성 편집 패널의 **General** 탭에 있는 **Struct fields** 섹션에서 지정할 필드를 고릅니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/struct-main-fields-sidebar-location.png" alt="주 필드 설정 위치" width="400">

5. **Edit {propertyName} struct field** 팝업 창에서 **Struct main field**를 켠 다음 **Confirm**을 선택합니다. 주 필드는 여러 개 지정할 수 있으며, 필드 패널을 클릭하고 끌어서 보기 좋게 순서를 바꿀 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/struct-main-fields-toggle.png" alt="Struct main field 토글" width="450">

6. 변경 사항을 **Save**합니다. 설정된 주 필드는 **Struct fields** 목록에 **Struct main field** 태그로 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/struct-main-fields-tags.png" alt="Struct main field 태그" width="400">

> **중간 요약**: Ontology Manager에서 구조체 속성의 필드를 열고 **Struct main field** 토글을 켠 뒤 저장하면 주 필드가 지정됩니다. 여러 개를 지정하고 순서를 바꿀 수 있습니다.

<a id="how-struct-main-fields-appear-in-applications"></a>
## 애플리케이션에서 구조체 주 필드가 표시되는 방식

구조체 주 필드를 지원하는 애플리케이션은 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)의 [Object Table](https://www.palantir.com/docs/foundry/workshop/widgets-object-table/) 위젯과 [Object List](https://www.palantir.com/docs/foundry/workshop/widgets-object-list/) 위젯 같은 간결한 보기(compact view)에서는 주 필드만 표시하고, 펼친 보기나 마우스를 올렸을 때 구조체 전체에 접근할 수 있게 합니다. 이렇게 하면 모든 구조체 필드를 보지 않고도 가장 중요한 데이터를 빠르게 훑어볼 수 있으며, 필요할 때는 구조체 전체를 살펴볼 수 있습니다.

애플리케이션은 다음 몇 가지 방식으로 구조체 주 필드를 지원합니다.

* **주 필드만(Main fields only):** 표나 요약 카드 같은 간결한 보기에서 주 필드만 표시합니다.
* **주 필드와 호버(Main fields with hover):** 기본적으로 주 필드를 보여 주고, 마우스를 올리면 메타데이터 필드를 드러냅니다.
* **전체 구조체(Full struct):** 완전한 정보가 필요한 상세 보기나 폼에서 모든 필드를 표시합니다.

> **중간 요약**: 간결한 보기에서는 주 필드만, 호버 시에는 메타데이터까지, 상세 보기에서는 전체 필드를 보여 주는 식으로 애플리케이션이 주 필드를 활용합니다.

<a id="use-struct-fields-with-interfaces"></a>
## 인터페이스와 함께 구조체 필드 사용하기

어떤 구조체 필드든 인터페이스 속성에 매핑할 수 있습니다. 인터페이스를 구현할 때 구조체 속성의 특정 필드를 골라 인터페이스 계약을 충족하고 속성 요구 사항을 채울 수 있습니다.

예를 들어 인터페이스가 `cityName`이라는 `String` 속성을 요구한다면, 구조체 속성의 `city` 필드로 이를 채울 수 있습니다. 인터페이스 선택기(picker)는 사용 가능한 모든 구조체 필드를 타입과 함께 보여 주므로 적절한 필드를 고를 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/struct-main-fields-interface-picker.png" alt="인터페이스 속성에 매핑할 구조체 필드 선택" width="700">

구조체 필드를 인터페이스 속성에 매핑하고 나면, 구현 내용에 구조체 속성과 사용 중인 특정 필드가 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/struct-main-fields-interface-mapped.png" alt="인터페이스 속성에 매핑된 구조체 필드" width="700">

주 필드는 선택기에서 **Struct main field** 태그로 표시되므로 쉽게 알아볼 수 있습니다. 하지만 주 필드로 지정되었는지와 관계없이 구조체의 어떤 필드든 선택할 수 있습니다.

**설명**: 인터페이스는 프로그래밍 언어의 인터페이스처럼 "이 인터페이스를 구현하는 객체 타입은 `cityName: String` 속성을 가져야 한다"는 계약을 정합니다. 객체 타입에 `cityName`이라는 독립 속성이 없더라도 `address` 구조체 속성 안에 `city: String` 필드가 있으면, 그 필드를 `cityName` 자리에 연결해 계약을 만족시킬 수 있다는 뜻입니다.

> **중간 요약**: 구조체의 어떤 필드든 인터페이스 속성에 연결할 수 있습니다. 주 필드 태그는 선택기에서 눈에 띄게 해 줄 뿐 선택 조건은 아닙니다.

<a id="combine-main-fields-with-property-reducers"></a>
## 주 필드와 속성 리듀서 함께 쓰기

구조체 주 필드를 [속성 리듀서(property reducers)](../03_properties/10_property-reducers.md)와 함께 사용하면 구조체 배열 속성의 표현과 인터페이스 구현에서 더 많은 유연성을 얻을 수 있습니다. 하나의 구조체 배열 속성이 `Struct Array`, 주 필드의 배열 타입, `Struct`, 또는 주 필드의 기본 타입을 요구하는 인터페이스를 구현할 수 있습니다.

자세한 예제와 구현 옵션은 [속성 리듀서 문서](../03_properties/10_property-reducers.md#combine-property-reducers-with-struct-main-fields)를 참고하세요.

**설명**: 예를 들어 `addresses`가 `Address` 구조체의 배열이고 주 필드가 `streetName: String`이라고 합시다. 이 속성 하나로 `Struct Array`(구조체 배열 그대로), `String` 배열(각 원소의 주 필드만 모은 배열), `Struct`(리듀서로 배열에서 원소 하나를 고른 결과), `String`(그 원소의 주 필드) 가운데 어느 형태를 요구하는 인터페이스든 구현할 수 있다는 뜻입니다. 리듀서는 배열 값을 값 하나로 줄이는 규칙입니다.

<a id="limitations-and-considerations"></a>
## 제한 사항과 고려 사항

* **질의 동작(Query behavior):** 질의는 주 필드만이 아니라 모든 구조체 필드를 대상으로 동작합니다. 구조체의 어떤 필드를 기준으로든 검색하고 필터링할 수 있습니다.

<a id="faqs"></a>
## 자주 묻는 질문 (FAQs)

<a id="can-i-change-which-fields-are-main-fields-later"></a>
### 나중에 어떤 필드를 주 필드로 할지 바꿀 수 있나요?

네, Ontology Manager에서 언제든지 주 필드를 다시 설정할 수 있습니다. 다만 이로 인해 일부 인터페이스 구현이 유효하지 않게 될 수 있으며, 그 경우 해당 구현을 업데이트해야 합니다.

<a id="do-main-fields-affect-how-foundry-stores-data"></a>
### 주 필드가 Foundry의 데이터 저장 방식에 영향을 주나요?

아니요, 주 필드는 Foundry가 데이터를 표시하는 방식과 인터페이스를 구현하는 방식에만 영향을 줍니다. 기반이 되는 구조체는 모든 필드를 손실 없이 담고 있으므로, 모든 필드를 여전히 질의하고 접근할 수 있습니다.

<a id="can-i-use-main-fields-with-struct-arrays"></a>
### 구조체 배열에도 주 필드를 사용할 수 있나요?

네. 주 필드는 단일 구조체 속성과 구조체 배열 속성 *양쪽 모두에서* 동작합니다. [리듀서](../03_properties/10_property-reducers.md)와 함께 쓰면 애플리케이션 전반에서 Foundry가 속성을 표현하는 방식을 가장 유연하게 조정할 수 있습니다.

<a id="do-i-need-to-configure-main-fields-to-use-struct-fields-with-interfaces"></a>
### 인터페이스에서 구조체 필드를 쓰려면 주 필드를 반드시 설정해야 하나요?

아니요. 주 필드로 지정되었는지와 관계없이 어떤 구조체 필드든 인터페이스 속성에 매핑할 수 있습니다. 주 필드는 인터페이스 선택기에서 시각적 표시를 제공하고, 애플리케이션이 간결한 보기에서 구조체를 표시하는 방식에 영향을 줄 뿐입니다.

## 정리

- 구조체 주 필드는 구조체의 핵심 값 필드를 지정해, 간결한 보기에서는 그 필드만 보여 주게 하는 베타 기능입니다.
- Ontology Manager에서 구조체 필드마다 **Struct main field** 토글로 지정하며, 여러 개 지정과 순서 변경이 가능합니다.
- 어떤 구조체 필드든(주 필드 여부와 무관하게) 인터페이스 속성에 매핑할 수 있습니다.
- 속성 리듀서와 함께 쓰면 구조체 배열 속성 하나로 여러 형태의 인터페이스 요구를 만족시킬 수 있습니다.
- 주 필드는 표시와 인터페이스 구현에만 영향을 주고, 저장과 질의는 모든 필드를 대상으로 합니다.
