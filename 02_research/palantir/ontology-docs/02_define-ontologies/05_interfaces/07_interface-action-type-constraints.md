# 인터페이스 액션 타입 제약 (Interface action type constraints)

- 원문: https://www.palantir.com/docs/foundry/interfaces/interface-action-type-constraints/
- 사이드바 위치: Define Ontologies > Interfaces > Interface action type constraints

이 페이지는 인터페이스 수준에서 "이 인터페이스를 구현하는 객체 타입이라면 이런 액션을 제공해야 한다"는 약속을 정의하는 기능인 인터페이스 액션 타입 제약을 설명합니다. 제약을 어떻게 정의하고, 파라미터 모양을 어떻게 지정하며, 구현 객체 타입에서 실제 액션 타입에 어떻게 연결(매핑)하는지 다룹니다. 아직 베타 단계 기능이므로 애플리케이션별 지원 수준과 한계도 함께 정리되어 있습니다.

**참고**: 베타(Beta). 인터페이스 액션 타입 제약은 추가 검증 기능이 활발히 개발되는 동안 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있습니다. 기능이 추가되더라도 기존 제약과 매핑 구성은 계속 동작하지만, 제약과 매핑을 구성하는 사용자 인터페이스는 바뀔 수 있습니다. 활발한 개발 기간 동안 지원 범위가 더 많은 애플리케이션과 서비스로 확대될 예정이며, 기존에 지원되는 워크플로는 계속 사용할 수 있습니다.

인터페이스 액션 타입 제약(interface action type constraint)은 인터페이스를 구현하는 객체 타입들에 공통으로 기대되는 액션 기능을 정의합니다. 제약은 액션의 사용자 관점 의미, API 이름, 파라미터 모양을 기술합니다. 그러면 각 구현 객체 타입은 이 제약을 해당 객체 타입의 구체적인 액션 타입에 매핑할 수 있습니다.

예를 들어 `Ticket` 인터페이스가 `Create ticket` 액션 타입 제약을 정의한다고 합시다. `Bug` 객체 타입은 `Create bug` 액션 타입으로 이 제약을 충족하고, `Feature request` 객체 타입은 `Create feature request` 액션 타입으로 충족합니다. 구체적인 액션 로직은 각 객체 타입에 고유하지만, 두 액션 타입은 동일한 인터페이스 수준 기능을 구현합니다.

인터페이스 액션 타입 제약을 어디서 구성하고, 배포하고, 사용할 수 있는지 알아보려면 [현재 지원 수준](#current-levels-of-support)을 확인하세요.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/iatc-config-page.png" alt="인터페이스 액션 타입 제약 탭." width="800" />

인터페이스 액션 타입 제약은 액션 실행 로직, 제출 조건(submission criteria), 부수 효과(side effect), 폼 레이아웃을 정의하지 않습니다. 이러한 동작은 제약을 충족하는 구체적인 액션 타입에서 구성합니다. 인터페이스 객체에 대해 동작하는 액션 규칙에 대한 자세한 내용은 [인터페이스에 대한 액션](../03_action-types/09_actions-on-interfaces.md)을 참조하세요.

현재 액션 타입 제약은 충족하는 액션 타입이 어떻게 동작해야 하는지를 기술하는 표현력이 제한적입니다. 충족하는 액션 타입이 무엇을 하도록 의도되었는지는 제약의 설명(description)을 사용해 애플리케이션 빌더에게 알려 주세요. 예를 들어 기대하는 편집(edit), 부수 효과, 제출 동작, 그 밖에 제약 모델이 강제하지 않는 의미상의 요구 사항을 설명에 적습니다.

**설명**: 프로그래밍 언어의 인터페이스에 대응시키면 이해가 쉽습니다. Java에서 `interface Ticket { void create(String title); }`를 선언하면 이를 구현하는 `Bug`, `FeatureRequest` 클래스는 각자 `create` 메서드의 본문을 작성해야 합니다. 인터페이스는 메서드 이름과 파라미터 시그니처만 정하고 본문은 정하지 않습니다. 액션 타입 제약도 마찬가지로 "이름과 파라미터 모양"만 정하고, 실제로 어떤 객체를 만들거나 수정하는지는 각 객체 타입의 액션 타입이 정합니다. 시그니처가 동작의 의미까지 보장하지 못하듯 제약도 의미를 강제하지 못하므로, 원문은 기대 동작을 설명 칸에 글로 적으라고 권합니다.

> **중간 요약**: 액션 타입 제약은 인터페이스를 구현하는 객체 타입이 제공해야 할 액션의 이름과 파라미터 모양을 정하는 약속입니다. 실행 로직, 제출 조건, 부수 효과는 정하지 않으며, 각 객체 타입의 구체적인 액션 타입이 이를 담당합니다.

<a id="action-type-constraints"></a>
## 액션 타입 제약 (Action type constraints)

액션 타입 제약은 인터페이스 수준 액션 기능의 파라미터를 정의합니다. 이 파라미터에는 다음이 포함됩니다.

* **Display name(표시 이름):** 액션 타입 제약의 사용자용 이름입니다.
* **Description(설명):** 충족하는 액션 타입이 무엇을 해야 하는지 사용자가 읽을 수 있게 적은 설명입니다.
* **API name(API 이름):** 코드와 플랫폼 구성에서 제약을 가리킬 때 쓰는 API 이름입니다.
* **Parameter constraints(파라미터 제약):** 충족하는 액션 타입이 노출해야 하는 파라미터입니다.
* 객체 타입 구현 시 이 액션 타입 제약이 필수인지 여부.

액션 타입 제약이 필수(required)이면, 인터페이스를 구현하는 모든 객체 타입은 이 제약을 구체적인 액션 타입에 매핑해야 합니다. 선택(optional) 액션 타입 제약은 구현 객체 타입이 그 기능을 지원할 때 매핑할 수 있고, 기능이 해당되지 않으면 건너뛸 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/iatc-config-dialog-set.png" alt="액션 타입 제약 구성 대화 상자." width="500" />

> **중간 요약**: 제약은 표시 이름, 설명, API 이름, 파라미터 제약, 필수 여부로 구성됩니다. 필수 제약은 모든 구현 객체 타입이 반드시 매핑해야 하고, 선택 제약은 건너뛸 수 있습니다.

<a id="parameter-constraints"></a>
## 파라미터 제약 (Parameter constraints)

파라미터 제약은 충족하는 액션 타입이 제공해야 하는 액션 파라미터의 모양을 정의합니다. 각 파라미터 제약에는 다음이 포함됩니다.

* **Type(타입):** 파라미터 타입입니다. 예를 들어 string, timestamp, 객체 참조(object reference), 인터페이스 참조(interface reference), 객체 집합(object set), 첨부 파일(attachment), 미디어 참조(media reference), 구조체(struct) 등이 있습니다.
* **Single or list value(단일 값 또는 리스트 값):** 파라미터가 값 하나를 받는지, 값의 리스트를 받는지 여부입니다.
* **Display name(표시 이름):** 파라미터 제약의 사용자용 이름입니다.
* **API name(API 이름):** 파라미터 제약을 가리킬 때 쓰는 API 이름입니다.
* 구현 객체 타입이 이 파라미터를 반드시 매핑해야 하는지 여부.

파라미터 제약을 만들 때는 새 파라미터를 수동으로 정의하거나, 기존 인터페이스 속성(property)에서 파라미터를 추가할 수 있습니다. 인터페이스 속성에서 파라미터를 추가하면 선택한 속성의 표시 이름, 타입, 필수 여부를 바탕으로 파라미터 제약이 만들어집니다. 파라미터 API 이름은 표시 이름에서 생성되며 수정할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/iatc-config-dialog-properties.png" alt="기존 인터페이스 속성에서 파라미터 추가." width="500" />

필수 파라미터 제약은 구체적인 액션 타입의 필수 파라미터에 매핑되어야 합니다. 필요하다면 선택 파라미터 제약도 매핑할 수 있습니다. 같은 액션 타입 제약 안에서 하나의 구체적 액션 파라미터가 여러 파라미터 제약을 동시에 충족할 수는 없습니다.

객체 참조, 인터페이스 참조, 객체 집합, 구조체 파라미터의 경우, 인터페이스 액션 타입 제약은 구체적인 구현 세부 사항까지 모두 기술하지 않고 파라미터의 일반적인 종류만 기술합니다. 예를 들어 객체 참조 파라미터 제약은 충족하는 액션 타입에 호환되는 객체 참조 파라미터가 있을 것을 요구하지만, 제약 자체가 특정 객체 타입 하나에 묶이지는 않습니다.

**설명**: 앞의 `Ticket` 예에서 `Create ticket` 제약에 `title`(string, 필수)과 `assignee`(객체 참조, 선택) 파라미터 제약이 있다고 합시다. `Create bug` 액션 타입은 필수 string 파라미터 하나를 `title`에 매핑해야 하고, `assignee`는 매핑해도 되고 안 해도 됩니다. `assignee`가 객체 참조라는 것만 정해져 있으므로, `Bug` 쪽에서는 `Employee` 객체 참조를, `Feature request` 쪽에서는 `Team` 객체 참조를 연결하는 식으로 객체 타입이 달라도 됩니다.

> **중간 요약**: 파라미터 제약은 타입, 단일/리스트 여부, 이름, 필수 여부를 정하며 인터페이스 속성에서 바로 만들 수도 있습니다. 필수 파라미터 제약은 구체 액션의 필수 파라미터에 매핑되어야 하고, 하나의 파라미터를 두 제약에 중복 매핑할 수 없습니다.

<a id="implementing-action-type-constraints"></a>
## 액션 타입 제약 구현하기 (Implementing action type constraints)

객체 타입이 액션 타입 제약이 있는 인터페이스를 구현하면, 그 객체 타입은 필수 제약을 충족하는 구체적인 액션 타입을 골라야 합니다. 구체적인 액션 타입이 제약의 필수 파라미터에 호환되는 파라미터를 갖고 있으면 그 제약을 충족합니다.

Ontology Manager에서 인터페이스 구현을 추가하고 나면, 객체 타입의 **Interfaces** 탭 아래 **Actions** 하위 탭에 인터페이스의 액션 타입 제약이 나열됩니다. 각 필수 제약에 대해 구현 객체 타입의 구체적인 액션 타입을 선택하세요. 선택 제약은 건너뛰거나 매핑할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/iatc-mapping-page.png" alt="인터페이스 액션 타입 제약에 대한 객체 타입 액션 매핑." width="800" />

파라미터 매핑을 구성하려면 매핑된 액션 타입 제약의 설정 아이콘을 선택해 **Configure parameters** 대화 상자를 엽니다. 각 필수 파라미터 제약을 선택한 액션 타입의 호환되는 필수 파라미터에 매핑합니다. 애플리케이션이 인터페이스 액션 기능을 통해 값을 전달하거나 미리 채워야 하는 경우에는 선택 파라미터 제약도 매핑할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/iatc-parameter-mapping.png" alt="인터페이스 액션 타입 제약에 대한 파라미터 매핑." width="500" />

Ontology Manager는 온톨로지에 변경 사항을 저장할 때 액션 타입 제약 매핑을 검증합니다. 다음 경우에는 저장할 수 없습니다.

* 구현 객체 타입이 필수 액션 타입 제약을 매핑하지 않은 경우.
* 필수 파라미터 제약이 매핑되지 않은 경우.
* 매핑된 파라미터의 파라미터 타입이 호환되지 않는 경우.
* 같은 구체적 액션 파라미터가 둘 이상의 파라미터 제약에 매핑된 경우.
* 매핑된 액션 타입 제약이나 파라미터 제약이 더 이상 존재하지 않는 경우.

> **중간 요약**: 구현 객체 타입의 Interfaces 탭, Actions 하위 탭에서 제약마다 구체 액션 타입을 고르고 Configure parameters에서 파라미터를 연결합니다. 저장 시 누락, 타입 불일치, 중복 매핑, 삭제된 제약 참조가 있으면 저장이 거부됩니다.

<a id="interface-extensions"></a>
## 인터페이스 확장 (Interface extensions)

액션 타입 제약은 [인터페이스 확장](08_extend-interface.md)을 통해 상속됩니다. 자식 인터페이스가 액션 타입 제약을 가진 기반 인터페이스를 확장하면, 자식 인터페이스를 구현하는 객체 타입은 자식 인터페이스에 직접 선언된 제약뿐 아니라 상속된 필수 액션 타입 제약도 충족해야 합니다.

어떤 기능이 넓은 범위의 인터페이스에 적용되고 더 구체적인 인터페이스들에서도 쓸 수 있어야 한다면 상속된 액션 타입 제약을 사용하세요. 기능이 자식 인터페이스에만 해당된다면 자식 인터페이스에 새 액션 타입 제약을 정의하세요.

> **중간 요약**: 기반 인터페이스의 액션 타입 제약은 확장한 자식 인터페이스로 상속되며, 자식 인터페이스 구현자는 상속분과 자체 선언분을 모두 충족해야 합니다.

<a id="choosing-required-vs-optional-constraints"></a>
## 필수 제약과 선택 제약 고르기 (Choosing required vs. optional constraints)

인터페이스 기반 애플리케이션이 올바르게 동작하려면 인터페이스를 구현하는 모든 객체 타입이 그 기능을 지원해야 하는 경우, 필수 액션 타입 제약을 사용하세요.

기능이 유용하지만 모든 경우에 해당하지는 않는다면 선택 액션 타입 제약을 사용하세요. 선택 제약은 베타 상태의 인터페이스 모델을 반복 개선하는 동안에도 유용합니다. 아직 그 기능을 지원할 준비가 되지 않은 구현을 막지 않으면서 객체 타입들이 기능을 점진적으로 도입할 수 있기 때문입니다.

파라미터 제약의 경우, 충족하는 모든 액션 타입이 그 파라미터를 필수 액션 입력으로 노출해야 할 때만 필수로 표시하세요. 구현체가 값을 내부적으로 계산하거나, 기본값을 쓰거나, 아예 그 값이 필요 없을 수 있다면 파라미터 제약을 선택으로 두세요.

> **중간 요약**: 모든 구현체가 반드시 지원해야 하는 기능만 필수로 하고, 나머지는 선택으로 두면 기존 구현을 깨뜨리지 않고 점진적으로 도입할 수 있습니다.

<a id="limitations"></a>
## 제한 사항 (Limitations)

지원 여부는 애플리케이션과 서비스마다 다릅니다. 어떤 애플리케이션이 인터페이스를 지원한다고 해서 액션 타입 제약까지 지원하는 것은 아닙니다. 베타 기간 동안 기능이 추가될 수 있고, 제약과 매핑을 구성하는 사용자 인터페이스는 바뀔 수 있습니다. 이러한 기능이 추가되어도 기존 정의와 매핑은 계속 동작합니다.

<a id="current-levels-of-support"></a>
### 현재 지원 수준 (Current levels of support)

다음 표는 인터페이스 액션 타입 제약을 어디서 구성하고, 배포하고, 사용할 수 있는지 요약합니다.

| 애플리케이션 또는 서비스 | 지원 | 할 수 있는 일과 현재 제한 사항 |
| --- | --- | --- |
| [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md) | 지원(Supported) | 인터페이스에 제약을 정의하고, 구현 객체 타입의 구체적인 액션 타입과 파라미터에 매핑합니다. 저장 시 모든 구현 객체 타입이 필수 제약을 충족하는지 검증합니다. 객체 타입을 사용하는 애플리케이션이 제약을 직접 노출하지 않더라도, 여러 객체 타입에 공통 액션 기능을 강제하는 용도로 사용하세요. |
| [Marketplace](https://www.palantir.com/docs/foundry/marketplace/overview/) | 지원(Supported) | 액션 타입 제약이 있는 인터페이스를 패키징하고 설치할 수 있습니다. |
| [Ontology SDK (OSDK)](https://www.palantir.com/docs/foundry/ontology-sdk/overview/) | 부분 지원(Partial) | 커스텀 애플리케이션은 TypeScript OSDK를 사용해 어떤 객체 타입에서 제약을 충족하는 구체적인 액션 타입을 조회(resolve)할 수 있습니다. 매핑을 조회한 다음, 충족하는 구체적인 액션 타입을 호출하세요. OSDK를 통해 제약 자체를 직접 호출할 수는 없습니다. |
| [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/) | 직접 사용 미지원(Direct use not supported) | Workshop은 현재 최종 사용자에게 인터페이스 액션 타입 제약을 직접 노출하지 않습니다. Workshop에서 제약 기반 액션 조회를 사용하려면 TypeScript OSDK로 충족하는 구체적인 액션 타입을 조회하고 호출하는 [커스텀 위젯](https://www.palantir.com/docs/foundry/custom-widgets/overview/)을 만드세요. |
| [Pipeline Builder](https://www.palantir.com/docs/foundry/pipeline-builder/overview/) | 매핑 미지원(Mapping not supported) | Pipeline Builder에서 인터페이스를 구현할 때는 액션 타입 제약을 매핑할 수 없습니다. 인터페이스에 필수 액션 타입 제약이 있다면 [Ontology Manager에서 인터페이스를 구현하고 매핑하세요](03_implement-interface.md#how-to-implement-an-interface-in-ontology-manager). |

**설명**: OSDK 행의 "조회한 다음 호출"은 두 단계로 동작한다는 뜻입니다. 1단계에서 "`Bug` 객체 타입에서 `Create ticket` 제약을 충족하는 액션은 무엇인가"를 물어 `Create bug`라는 답을 얻고, 2단계에서 그 `Create bug` 액션을 실제로 실행합니다. `Create ticket`이라는 이름으로 바로 실행하는 호출은 없습니다.

<a id="constraint-semantics"></a>
### 제약의 의미 (Constraint semantics)

인터페이스 액션 타입 제약은 구체적인 액션 타입이 가져야 할 모양을 정의합니다. 객체 타입마다 다른 액션 로직을 하나로 통일하지는 않습니다. 충족하는 각 액션 타입의 규칙, 제출 조건, 권한, 부수 효과를 검토해 인터페이스 제약에 기술된 의미와 일치하는지 확인하세요.

> **중간 요약**: 현재 제약 정의와 매핑은 Ontology Manager, 패키징은 Marketplace에서 지원되고, OSDK는 조회 후 구체 액션 호출 방식으로만, Workshop은 커스텀 위젯을 통해서만 활용할 수 있으며 Pipeline Builder에서는 매핑할 수 없습니다. 제약은 모양만 맞출 뿐 동작의 의미는 사람이 확인해야 합니다.

## 정리

- 인터페이스 액션 타입 제약은 구현 객체 타입이 제공해야 할 액션의 이름, 설명, API 이름, 파라미터 모양을 정의하며, 실행 로직은 정의하지 않습니다.
- 필수 제약은 모든 구현 객체 타입이 구체 액션 타입에 매핑해야 하고, 필수 파라미터 제약은 구체 액션의 필수 파라미터에 연결되어야 합니다.
- 매핑은 Ontology Manager에서 객체 타입의 Interfaces 탭, Actions 하위 탭에서 하며 저장 시 검증됩니다.
- 제약은 인터페이스 확장을 통해 상속됩니다.
- 베타 기능이므로 애플리케이션별 지원 수준이 다르고, 동작의 의미는 설명 칸과 사람의 검토로 보완해야 합니다.
