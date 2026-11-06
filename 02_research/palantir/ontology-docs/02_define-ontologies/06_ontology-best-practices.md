# 온톨로지 설계: 모범 사례 (Ontology design: Best practices)

- 원문: https://www.palantir.com/docs/foundry/ontology/ontology-best-practices/
- 사이드바 위치: Define Ontologies > Ontology design: Best practices

이 페이지는 온톨로지를 설계할 때 따라야 할 실무 점검 목록(설계 지침 8가지)과 그 바탕이 되는 핵심 설계 원칙 4가지를 설명합니다. 각 원칙마다 피해야 할 안티패턴, 잘못된 설계와 권장 설계를 나란히 놓은 예시, 안티패턴이 가져오는 문제, 모범 사례가 정리되어 있습니다. 소프트웨어 공학에서 배우는 도메인 주도 설계, DRY, 개방-폐쇄 원칙, 상속보다 합성 같은 원칙을 데이터 모델 설계에 그대로 적용한 내용이라 프로그래밍 수업에서 배운 개념과 연결해 읽으면 좋습니다.

잘 설계된 온톨로지는 조직을 하나로 통합된 직관적인 형태로 표현하며, 이를 통해 매끄러운 데이터 통합, 부서 간 협업, 강력한 분석이 가능해집니다. 이 섹션은 빠르게 참조할 수 있는 설계 지침 모음과, 그 지침을 뒷받침하는 핵심 설계 원칙에 대한 더 깊은 설명을 함께 제공합니다.

<a id="design-guidelines"></a>
## 설계 지침 (Design guidelines)

다음 지침은 온톨로지 설계를 위한 실용적인 점검 목록입니다. 해당되는 경우 각 지침은 [핵심 설계 원칙](#core-design-principles), [안티패턴](08_ontology-anti-patterns.md), 또는 [구조적 권장 사항](07_ontology-structural-guidance.md)에 근거를 둡니다.

1. **시스템이 아니라 현실을 모델링하기(Model reality, not systems):** 객체 타입은 개별 원천 시스템이나 부서별 표현이 아니라 현실 세계의 엔터티를 나타내야 합니다.
   * **설계 원칙:** [도메인 주도 설계](#1-domain-driven-design)
2. **의도적으로 선별하기(Curate intentionally):** 모든 속성(property)은 분명한 비즈니스 가치나 기술적 가치를 가져야 합니다.
   * **구조적 권장 사항:** [정규화와 파생 속성](07_ontology-structural-guidance.md#normalization-and-derived-properties)
3. **팀 간에 협업하기(Collaborate across teams):** 온톨로지 설계에는 여러 부서나 팀의 이해관계자가 참여해야 합니다. 팀이 고립되어 있는 것이 중복의 주된 원인입니다.
   * **설계 원칙:** [같은 것을 반복하지 않기](#2-do-not-repeat-yourself-rule-of-three)
4. **객체 타입의 초점을 유지하기(Keep object types focused):** 각 객체 타입은 서로 구별되는 엔터티 하나를 나타내야 합니다.
   * **설계 원칙:** [도메인 주도 설계](#1-domain-driven-design)
5. **알맞은 도구 고르기(Choose the right tool):** 사람이나 에이전트의 의사 결정에는 액션 타입을, 자동화된 변환에는 파이프라인을 사용합니다.
   * **안티패턴:** [황금 망치(The Golden Hammer)](08_ontology-anti-patterns.md#anti-pattern-the-golden-hammer)
6. **추상화에는 인터페이스 사용하기(Use interfaces for abstraction):** 엔터티들이 공통된 특성을 공유할 때는 넓고 희소한(wide, sparse) 객체 타입을 만드는 대신 인터페이스로 추상화를 모델링합니다.
   * **설계 원칙:** [깊은 계층보다 합성](#4-composition-over-deep-hierarchies)
7. **결정 사항을 문서화하기(Document your decisions):** Ontology Manager에서 객체 타입, 속성, 링크를 문서화합니다.
8. **실제 비즈니스 질문으로 검증하기(Validate against real business questions):** 과업 기반 분석 연습을 진행해, 사람과 에이전트가 온톨로지를 탐색하고 이를 중요한 의사 결정에 활용할 수 있는지 확인합니다.
   * **검증 지침:** [온톨로지 설계: 검증](09_ontology-design-validation.md)

**설명**: 6번의 "넓고 희소한 객체 타입"은 열(속성)이 아주 많지만 각 행(객체)에서 대부분의 열이 비어 있는(null) 테이블을 말합니다. 예를 들어 `Aircraft`, `Vessel`, `GroundVehicle`을 하나의 `Vehicle` 타입에 몰아넣고 `wingspan`, `draft`, `wheelCount` 속성을 모두 두면, 선박 객체는 `wingspan`이 항상 null이고 항공기 객체는 `draft`가 항상 null입니다. 인터페이스를 쓰면 각 타입은 자신에게 필요한 속성만 갖고, 공통 속성만 인터페이스로 묶을 수 있습니다.

> **중간 요약**: 설계 지침 8가지는 현실 모델링, 의도적 선별, 팀 간 협업, 객체 타입의 단일 초점, 도구 선택, 인터페이스를 통한 추상화, 문서화, 실제 질문을 통한 검증입니다. 각각은 아래 핵심 원칙이나 다른 페이지의 안티패턴, 구조적 권장 사항과 연결됩니다.

<a id="core-design-principles"></a>
## 핵심 설계 원칙 (Core design principles)

이 네 가지 원칙은 정부 및 상업 분야 구축 사례 전반에서 쌓은 폭넓은 현장 경험에서 도출되었습니다. 원칙은 우선순위 순서로 제시되어 있습니다. 원칙끼리 충돌할 때는 우선순위가 높은 원칙이 우선합니다.

| 우선순위 | 원칙 | 핵심 아이디어 |
|-------------|-------------|----------|
|1	|[도메인 주도 설계(Domain-driven design)](#1-domain-driven-design)	|원천 데이터가 아니라 현실 세계를 모델링합니다.|
|2	|[같은 것을 반복하지 않기(Do not repeat yourself)](#2-do-not-repeat-yourself-rule-of-three)	|같은 것을 세 번 만들었다면 리팩터링합니다.|
|3	|[확장에는 열려 있고 수정에는 닫혀 있기(Open for extension, closed for modification)](#3-open-for-extension-closed-for-modification)	|핵심 모델을 보호합니다. 빌더가 그것을 확장할 수 있게 합니다.|
|4	|[깊은 계층보다 합성(Composition over deep hierarchies)](#4-composition-over-deep-hierarchies)	|인터페이스를 통한 다중 상속을 선호합니다. 구성 요소를 갈아 끼울 수 있게(pluggable) 유지합니다.|

어떤 결정을 내리든 현실적인 고려 사항을 항상 반영해야 합니다. 자세한 내용은 [실용주의와 트레이드오프](#pragmatism-and-tradeoffs) 섹션을 참조하세요.

<a id="1-domain-driven-design"></a><a id="domain-driven-design"></a>
### 1. 도메인 주도 설계 (Domain-driven design)

<img width="1280" height="720" alt="1-도메인 설계" src="https://www.palantir.com/docs/resources/foundry/ontology/domain-design.png" />

**온톨로지는 원천 데이터가 아니라 현실 세계를 모델링합니다.**

객체는 데이터베이스 테이블, API 응답, 스프레드시트 탭이 아니라 의미 있는 현실 세계의 개념(예: `Patient`, `WorkOrder`, `Vessel`)을 나타내야 합니다. 링크는 조인 키나 외래 키의 부산물이 아니라 실제 관계("이 환자가 이 시설을 방문했다")를 나타내야 합니다.

"데이터셋을 온톨로지화해 달라"는 요청을 받았을 때, 열을 속성에 1:1로 매핑하고 작업이 끝났다고 여기고 싶은 유혹을 참으세요. [잡동사니 통(Kitchen Sink)](08_ontology-anti-patterns.md#anti-pattern-the-kitchen-sink) 안티패턴은 유용한 의미 대신 원천 시스템 스키마의 기이한 특성을 그대로 비추는 온톨로지를 만들어 냅니다. 잘 설계된 온톨로지는 직관적으로 사용할 수 있어야 합니다. 구조가 사용자나 AI 에이전트가 이미 자신의 도메인을 생각하는 방식과 일치하므로, 이들이 막힘 없이 탐색할 수 있어야 합니다.

<a id="anti-patterns"></a>
#### 안티패턴 (Anti-patterns)

* 객체 타입이 도메인 엔터티가 아니라 원천 시스템 테이블을 그대로 비춥니다
* 속성이 선별 없이 원천 열에서 1:1로 매핑됩니다
* 이름이 비즈니스 용어(`lastInspectionDate`)가 아니라 원천 시스템 관례(`dtLastInspMod`)에서 옵니다
* 도메인을 이해하는 대신 데이터를 보고 객체 모델을 설계했습니다
* 여러 엔터티를 담은 원천 행 하나를 단일 객체 타입으로 모델링했습니다

<a id="example"></a>
#### 예시 (Example)

`order_id`, `customer_name`, `customer_email`, `product_sku`, `quantity` 열을 가진 CSV는 현실 세계 엔터티 하나가 아니라 최소 세 개를 기술합니다.

```
✗ Avoid                                    ✓ Prefer
────────────────────────────────────────   ────────────────────────────────────────
OrderData                                  Order
  - order_id                                 - order_id
  - customer_name                            - quantity
  - customer_email                →          - Links to → Customer, Product
  - product_sku
  - quantity                               Customer
                                             - name
(One object type mirroring the CSV)          - email

                                           Product
                                             - sku

                                           (Three object types modeling the domain)
```

**설명**: 왼쪽(Avoid, 피할 설계)은 CSV를 그대로 비추는 `OrderData` 객체 타입 하나입니다. 오른쪽(Prefer, 권장 설계)은 도메인을 모델링한 객체 타입 세 개(`Order`, `Customer`, `Product`)이며, `Order`가 `Customer`와 `Product`로 링크됩니다. 데이터베이스 수업의 정규화와 같은 판단입니다. 같은 고객이 주문을 100번 했다면 왼쪽 설계에서는 고객 이름과 이메일이 100개 행에 반복 저장되고, "이 고객의 모든 주문"을 찾으려면 이름 문자열로 검색해야 합니다. 오른쪽 설계에서는 `Customer` 객체 하나에서 링크를 따라 주문 100개로 이동합니다.

<a id="impact-of-anti-patterns"></a>
#### 안티패턴의 영향 (Impact of anti-patterns)

| 문제 | 영향 |
|-|-|
| 직관적이지 않은 모델 | 구조가 도메인에 대한 생각 방식과 맞지 않아 사용자와 AI 에이전트가 온톨로지를 자연스럽게 탐색하지 못합니다. |
| 원천에 대한 취약한 결합 | 온톨로지가 원천 구조를 추상화하지 않고 그대로 비추므로, 원천 시스템의 스키마가 바뀌면 온톨로지 소비자가 깨집니다. |
| 놓친 관계 | 열로 묻혀 있는 엔터티(주문의 `customer_name` 같은)는 독립적으로 링크하거나, 검색하거나, 추론할 수 없습니다. |
| 낮은 재사용성 | 한 시스템의 스키마에 맞춰 만든 객체 타입은 다른 팀이나 다른 사용 사례가 채택하기 어렵습니다. |

<a id="best-practices"></a>
#### 모범 사례 (Best practices)

1. **원천 스키마를 보기 전에 현실 세계 엔터티를 식별하기:** 도메인 이해관계자와 함께 어떤 개념이 중요한지 정의합니다. 데이터셋 하나가 여러 엔터티를 기술하는 경우가 많습니다.
2. **정체성과 관측을 분리하기:** 행 하나가 어떤 엔터티에 대한 측정이나 이벤트를 나타낸다면, 엔터티와 관측은 서로 다른 객체 타입일 가능성이 높습니다.
3. **사람을 위한 이름 붙이기:** API 이름은 직관적이고 그 자체로 의미가 드러나야 합니다. `person.linkedChildPersonObjects`보다 `person.children`을 선호하세요. `equipment.dtLastInspMod`보다 `equipment.lastInspectionDate`를 선호하세요.
4. **도메인을 모델링한 다음 데이터를 매핑하기:** 도메인을 이해하고, 객체 모델을 설계하고, 그다음 원천 데이터를 그 모델에 매핑합니다. 데이터를 보고 그 모양을 복제하려 하지 마세요.
5. **의미적이지 않은 타입은 숨김으로 표시하기:** 특정 워크플로에 의미적이지 않은 타입(현실 세계 도메인 엔터티를 모델링하기보다 기술적 목적에 쓰이는 타입)이 필요하다면, 온톨로지의 기본 보기를 깔끔하게 유지하도록 숨김(hidden)으로 표시합니다. 이런 타입도 빌더가 애플리케이션을 만들 때는 계속 활용할 수 있습니다.

**설명**: 2번 "정체성과 관측의 분리"의 예를 들면, `sensor_readings` 데이터셋에 `sensor_id, location, model, reading_time, temperature` 열이 있을 때 센서 자체(`sensor_id, location, model`)는 시간이 지나도 거의 바뀌지 않는 정체성이고, 측정값(`reading_time, temperature`)은 매번 새로 쌓이는 관측입니다. 따라서 `Sensor` 객체 타입과 `SensorReading` 객체 타입으로 나누고 둘을 링크하는 것이 이 원칙에 맞습니다.

> **중간 요약**: 도메인 주도 설계 원칙은 원천 데이터의 모양이 아니라 현실 세계의 개념을 기준으로 객체 타입과 링크를 정하라는 것입니다. 한 데이터셋에서 여러 엔터티를 찾아 분리하고, 사람이 읽기 쉬운 이름을 붙이며, 기술적 타입은 숨깁니다.

<a id="2-do-not-repeat-yourself-rule-of-three"></a>
### 2. 같은 것을 반복하지 않기: 3의 법칙 (Do not repeat yourself (rule of three))

<img width="1280" height="720" alt="3-반복하지 않기" src="https://www.palantir.com/docs/resources/foundry/ontology/do-not-repeat.png" />

**같은 것을 세 번 만들었다면 리팩터링하세요.**

중복된 객체 타입, 불필요하게 겹치는 속성, 복사해 붙인 워크플로는 유지 보수 부담이자 컨텍스트 관리 문제입니다. 온톨로지를 추론해야 하는 사람과 AI 에이전트 모두에게 그렇습니다. 목표는 각 개념마다 단 하나의 정식(canonical) 표현을 두고, 그 개념에 대한 각 연산마다 단 하나의 정식 워크플로를 두는 것입니다. 3의 법칙은 이 원칙을 적용할 실용적인 계기입니다. 한 번은 우연이고, 두 번은 패턴이며, 세 번이면 리팩터링할 때입니다.

<a id="anti-patterns"></a>
#### 안티패턴 (Anti-patterns)

* 여러 객체 타입이 같은 속성 집합과 비슷한 링크를 공유합니다
* 같은 파생 속성 로직이나 액션 로직이 여러 타입에 나타납니다
* 서로 다른 팀이 조금씩 다른 목적으로 거의 동일한 객체 타입을 만들었습니다
* 타입마다 약간씩만 다른, 복사해 붙인 워크플로가 존재합니다

<a id="example"></a>
#### 예시 (Example)

세 팀이 각자 독립적으로 스키마가 겹치는 고객 관련 객체 타입을 만들었습니다.

```
✗ Avoid                                    ✓ Prefer
────────────────────────────────────────   ────────────────────────────────────────
Sales Customer                             Customer (single canonical type)
  - name                                     - name
  - email                                    - email
  - phone                                    - phone
                                             - salesStatus
Support Customer                   →         - supportTier
  - name                                     - billingAccountId
  - email
  - phone                                 — OR, if shapes are genuinely distinct —

Billing Customer                           Interface: CustomerBase
  - name                                     - name
  - email                                    - email
  - phone                                    - phone

(Three types, three sets of actions,       Implemented by: SalesLead, SupportContact,
 three maintenance burdens)                BillingAccount
```

**설명**: 왼쪽은 영업, 지원, 청구 팀이 각자 만든 고객 타입 세 개로, 타입도 세 개, 액션 묶음도 세 개, 유지 보수 부담도 세 배입니다. 오른쪽은 두 가지 해법을 보여 줍니다. 첫째는 세 팀의 속성을 모두 담은 정식 `Customer` 타입 하나로 합치는 방법입니다. 둘째는 세 타입의 모양이 정말로 다를 때 쓰는 방법으로, 공통 속성(`name`, `email`, `phone`)을 `CustomerBase` 인터페이스로 뽑고 `SalesLead`, `SupportContact`, `BillingAccount`가 이를 구현하게 합니다. 프로그래밍에서 세 클래스에 복사된 같은 메서드를 공통 부모나 인터페이스로 끌어올리는 리팩터링과 같은 작업입니다.

<a id="impact-of-anti-patterns"></a>
#### 안티패턴의 영향 (Impact of anti-patterns)

| 문제 | 영향 |
|-|-|
| 유지 보수 부담 | 변경 사항을 모든 중복본에 똑같이 반영해야 합니다. 업데이트를 놓치면 사본 사이에 차이가 벌어집니다. |
| 모호한 컨텍스트 | 사용자와 AI 에이전트는 거의 똑같은 여러 타입 중 어느 것이 정식인지 판단할 수 없습니다. |
| 일관되지 않은 동작 | 중복된 액션이나 파생 속성 로직은 시간이 지나며 서로 달라져 상충하는 결과를 냅니다. |
| 낭비되는 개발 노력 | 팀들이 하나의 공유 모델에서 협업하는 대신 같은 것을 조금씩 다른 형태로 다시 만듭니다. |

<a id="best-practices"></a>
#### 모범 사례 (Best practices)

1. **중복을 점검하기:** 여러 객체 타입이 공통된 모양(같은 속성, 비슷한 링크, 비슷한 액션)을 공유한다면, 구별용 속성을 둔 단일 타입이어야 하는지, 아니면 공유 인터페이스를 구현해야 하는지 평가합니다.
2. **공유 로직을 통합하기:** 같은 파생 속성이나 액션 로직이 여러 타입에 나타나면 인터페이스나 공유 함수(function)로 추출합니다.
3. **팀별 사본을 통일하기:** 여러 그룹이 거의 동일한 객체 타입을 만들었다면, 적절한 보안 또는 필터링을 적용한 단일 정식 표현으로 통일합니다.
4. **3의 법칙 적용하기:** 중복 하나는 허용될 수 있습니다. 둘은 경고 신호입니다. 셋이면 리팩터링할 때입니다.

> **중간 요약**: 각 개념에는 하나의 정식 표현과 하나의 정식 워크플로만 두는 것이 목표이며, 같은 것이 세 번 나타나면 단일 타입이나 공유 인터페이스로 리팩터링합니다. 팀별 차이는 별도 타입이 아니라 보안이나 필터링으로 처리합니다.

<a id="3-open-for-extension-closed-for-modification"></a><a id="open-for-extension-closed-for-modification"></a>
### 3. 확장에는 열려 있고 수정에는 닫혀 있기 (Open for extension, closed for modification)

<img width="1280" height="720" alt="2-개방 폐쇄" src="https://www.palantir.com/docs/resources/foundry/ontology/open-closed.png" />

**핵심 모델을 보호하세요. 빌더가 그것을 확장할 수 있게 하세요.**

객체 타입, 인터페이스, 워크플로가 현장에서 검증되어 운영(production)에 들어가면, 그 핵심 구조는 안정적이어야 합니다. 조직의 다른 개발자와 팀은 핵심 모델을 수정하지 않고도 그 위에 무언가를 만들 수 있어야 합니다. 예를 들어 인터페이스를 구현하는 새 객체 타입을 추가하거나, 기존 객체를 사용하는 새 워크플로를 추가할 수 있어야 합니다.

<a id="anti-patterns"></a>
#### 안티패턴 (Anti-patterns)

* 자리 잡은 객체 타입에 호환성을 깨는 변경이 잦아 의존하는 애플리케이션 전반으로 연쇄적으로 퍼집니다
* 새 사용 사례가 기존 핵심 타입을 확장하는 대신 수정할 것을 요구합니다
* 팀별 요구를 수용하기 위해 팀들이 공유 인터페이스나 액션을 편집해야 합니다
* 한 팀의 확장을 위한 보안 변경이 의도치 않게 다른 소비자에게 영향을 줍니다

<a id="example"></a>
#### 예시 (Example)

핵심 `Equipment` 객체 타입과 `Inspectable` 인터페이스가 운영 중입니다. 새 팀이 일부 장비의 인증(certification) 데이터를 추적해야 합니다.

```
✗ Avoid                                    ✓ Prefer
────────────────────────────────────────   ────────────────────────────────────────
Modify the core Equipment type:            Extend without modifying core:

Equipment                                  Equipment (unchanged)
  - serialNumber                             - serialNumber
  - manufacturer                             - manufacturer
  - certificationAuthority   (new)   →       - Links to → Equipment Certification
  - certificationExpiry      (new)
  - certificationStatus      (new)         Equipment Certification (new linked type)
  - lastCertAudit            (new)           - certificationAuthority
                                             - certificationExpiry
(Four new properties, null for all           - certificationStatus
 non-certified equipment, existing           - lastCertificationAudit
 consumers must handle the change)
                                           New interface: Certifiable
                                             - certificationStatus
                                             - certificationExpiry

                                           (Core type untouched, new capability
                                            added via linked type and interface)
```

**설명**: 왼쪽은 핵심 `Equipment` 타입에 인증 관련 속성 4개를 직접 추가하는 방식입니다. 인증받지 않은 모든 장비에서 이 4개 속성은 null이 되고, 기존 소비자(이 타입을 쓰는 애플리케이션)는 이 변경에 대응해야 합니다. 오른쪽은 `Equipment`를 그대로 두고, 인증 정보를 새 객체 타입 `Equipment Certification`에 담아 링크로 연결하며, 필요하면 `Certifiable` 인터페이스로 인증 기능을 표현합니다. 핵심 타입은 건드리지 않고 링크된 타입과 인터페이스로 새 기능을 더한 것입니다. 객체 지향 설계의 개방-폐쇄 원칙(OCP)을 데이터 모델에 적용한 것이며, 데이터베이스에서 기존 테이블에 열을 추가(`ALTER TABLE`)하는 대신 외래 키로 연결되는 새 테이블을 만드는 선택에 해당합니다.

<a id="impact-of-anti-patterns"></a>
#### 안티패턴의 영향 (Impact of anti-patterns)

| 문제 | 영향 |
|-|-|
| 호환성을 깨는 변경 | 핵심 타입을 수정하면 조직 전반에서 의존하는 애플리케이션, 액션, 워크플로가 깨질 수 있습니다. |
| 범위 확장(scope creep) | 핵심 타입에 새 사용 사례마다 속성과 로직이 쌓여 [신 객체(God Object)](08_ontology-anti-patterns.md#anti-pattern-the-god-object)로 변해 갑니다. |
| 얽힌 소유권 | 여러 팀이 같은 핵심 타입을 수정하면서 병합 충돌과 불분명한 책임이 생깁니다. |
| 보안 누수 | 명확한 경계 없이 핵심 타입을 확장하면 의도치 않게 데이터 접근 범위가 넓어질 수 있습니다. |

<a id="best-practices"></a>
#### 모범 사례 (Best practices)

1. **무엇이 본질적인지 식별하기:** 어떤 속성과 링크가 엔터티에 진정으로 근본적인지 판단합니다. 그것들은 고정합니다.
2. **확장을 염두에 두고 설계하기:** 핵심 타입과 인터페이스를 만들 때 다른 사람들이 그 위에 무언가를 만들 것을 예상합니다. 링크된 확장 타입과 새 인터페이스 구현이 들어올 여지를 남깁니다.
3. **수정하기보다 확장하기:** 기존 모델에 무언가를 더할 때, 그것이 핵심 타입에 속하는지 아니면 확장(새 링크된 객체 타입, 새 인터페이스 구현, 새 속성 네임스페이스)에 속하는지 검토합니다.
4. **보안 경계를 강제하기:** 핵심 데이터 모델에는 잘 정의된 보안 경계가 있어야 온톨로지를 확장할 때 의도치 않게 접근 범위가 넓어지지 않습니다.

> **중간 요약**: 운영 중인 핵심 타입은 안정적으로 유지하고, 새 요구는 링크된 새 객체 타입이나 인터페이스 구현 같은 확장으로 수용합니다. 이렇게 해야 호환성 파괴, 신 객체화, 소유권 혼란, 보안 누수를 피할 수 있습니다.

<a id="4-composition-over-deep-hierarchies"></a><a id="composition-over-deep-hierarchies"></a>
### 4. 깊은 계층보다 합성 (Composition over deep hierarchies)

<img width="1280" height="720" alt="4-합성" src="https://www.palantir.com/docs/resources/foundry/ontology/composition.png" />

**인터페이스를 통한 다중 상속을 선호하세요. 구성 요소를 갈아 끼울 수 있게 유지하세요.**

Foundry 온톨로지는 인터페이스를 통한 다중 상속을 지원하므로, 엔터티는 단일 상속 체인 대신 초점이 분명한 여러 추상화에서 동작을 조합할 수 있습니다.

<a id="anti-patterns"></a>
#### 안티패턴 (Anti-patterns)

* 부모의 기능을 조합하기 위해서만 존재하는 자식 타입으로 이루어진 깊은 단일 상속 체인
* `SchedulableBuilding`이나 `InspectableVehicle`처럼 서로 관련 없는 두 개념을 한 타입으로 합친 "조합" 타입
* 공유 인터페이스에서 동작할 수 있는데도 특정 객체 타입에 단단히 결합된 워크플로
* 엔터티에 새 기능을 추가하려면 상속 체인을 재구성해야 하는 구조

<a id="example"></a>
#### 예시 (Example)

`Arena`는 건물이면서 동시에 예약 가능한 자원이어야 합니다.

```
✗ Avoid                                    ✓ Prefer
────────────────────────────────────────   ────────────────────────────────────────
Deep single-inheritance:                   Composed interfaces:

Asset                                      Interface: Building
  └── PhysicalAsset                          - address
        └── Building                         - squareFootage
              └── SchedulableBuilding
                    └── Arena              Interface: SchedulableResource
                                             - schedulingCalendar
(Every new combination of capabilities       - bookingPolicy
 requires a new intermediate type.
 A SchedulableWarehouse would need         Arena implements both:
 yet another branch.)                        Building + SchedulableResource
                                             - arenaName
                                             - seatingCapacity

                                           (Adding SchedulableWarehouse only
                                            requires implementing the same two
                                            interfaces — no new hierarchy needed.)
```

**설명**: 왼쪽은 `Asset`, `PhysicalAsset`, `Building`, `SchedulableBuilding`, `Arena`로 이어지는 깊은 단일 상속입니다. 기능 조합이 새로 생길 때마다 중간 타입이 하나씩 더 필요하고, 예약 가능한 창고(`SchedulableWarehouse`)를 만들려면 또 다른 가지가 필요합니다. 오른쪽은 `Building` 인터페이스(`address`, `squareFootage`)와 `SchedulableResource` 인터페이스(`schedulingCalendar`, `bookingPolicy`)를 따로 두고, `Arena`가 둘을 모두 구현하면서 자신만의 속성(`arenaName`, `seatingCapacity`)을 갖습니다. `SchedulableWarehouse`를 추가할 때도 같은 두 인터페이스를 구현하기만 하면 되고 새 계층은 필요 없습니다. Java에서 `class Arena implements Building, SchedulableResource`로 쓰는 구조와 같습니다.

<a id="impact-of-anti-patterns"></a>
#### 안티패턴의 영향 (Impact of anti-patterns)

| 문제 | 영향 |
|-|-|
| 조합 폭발 | 기능의 새 조합이 생길 때마다 계층에 새 중간 타입이 필요합니다. |
| 깨지기 쉬운 계층 | 부모 타입의 변경이 모든 자손 타입에 예측할 수 없게 연쇄적으로 퍼집니다. |
| 제한된 재사용 | 체인 깊숙한 곳의 특정 타입을 기준으로 만든 워크플로는 같은 기능을 공유하는 다른 타입에 재사용할 수 없습니다. |
| 의미 왜곡 | `SchedulableBuilding` 같은 억지스러운 부모 타입은 현실 세계 개념을 나타내지 않으므로 [도메인 주도 설계 원칙](#1-domain-driven-design)을 위반합니다. |

<a id="best-practices"></a>
#### 모범 사례 (Best practices)

1. **기능이나 역할을 중심으로 인터페이스 설계하기:** `Inspectable`, `Schedulable`, `Billable`, `Depreciable`처럼 특정한 동작이나 속성 집합을 담는, 초점이 분명한 인터페이스를 사용합니다.
2. **집계에는 분류 인터페이스 사용하기:** 분류상의 정체성을 나타내는 인터페이스(예: `Aircraft`, `Vessel`, `GroundVehicle`이 구현하는 `MilitaryAsset`)는 드릴다운 조사나 그와 비슷한 집계 워크플로에 특히 유용합니다.
3. **워크플로에서 인터페이스를 대상으로 삼기:** 액션, 함수, 애플리케이션을 만들 때 가능하면 인터페이스를 대상으로 합니다. `SchedulableResource` 인터페이스를 기준으로 만든 워크플로는 수정 없이 경기장, 회의실, 차량에 모두 동작합니다.
4. **상속하기보다 합성하기:** 엔터티에 여러 기능이 필요하면 깊은 단일 상속 체인에 끼워 넣지 말고 여러 인터페이스를 구현합니다.

> **중간 요약**: 기능별로 작은 인터페이스를 만들고 엔터티가 여러 인터페이스를 구현하게 하면 조합 폭발과 깨지기 쉬운 계층을 피할 수 있습니다. 워크플로도 특정 타입이 아니라 인터페이스를 대상으로 만들면 재사용 범위가 넓어집니다.

<a id="pragmatism-and-tradeoffs"></a>
## 실용주의와 트레이드오프 (Pragmatism and tradeoffs)

**이 원칙들은 지침이지 법칙이 아닙니다.**

마감 기한, 레거시 시스템, 부분적인 플랫폼 지원, 사용자 숙련도 같은 현실적 제약 때문에 이상적인 온톨로지 설계를 항상 곧바로 달성할 수 있는 것은 아닙니다. 다음 지침을 사용해 트레이드오프를 헤쳐 나가세요.

| 지침 | 세부 내용 |
|-|-|
| 걸림돌이 되지 않으면서 좋은 설계 쪽으로 이끌기 | 촉박한 기한 안에 무언가가 동작해야 한다면, 지금은 합리적인 것을 만들되 개선으로 가는 분명한 경로를 남겨 둡니다. |
| 트레이드오프를 명시적으로 밝히기 | 지름길을 권할 때는 무엇을 포기하는지, 그것이 언제 문제가 될 수 있는지 설명합니다. 예를 들어 비정규화는 현재 규모에서는 잘 동작할 수 있지만, 객체가 1만 개를 넘어서면 다시 검토해야 할 수 있습니다. |
| 대규모 일괄 리팩터링보다 점진적 개선을 선호하기 | 실제로 사용되며 가치를 만들어 내는 약간 불완전한 온톨로지가, 아직 설계 중인 이론상 완벽한 온톨로지보다 낫습니다. |
| 핵심 불변 조건을 지키기 | 이름의 품질, 의미의 명확성, 보안 설계는 나중에 고치기 어렵습니다. 지름길은 이런 부분이 아니라 구현 세부 사항에서 택하세요. |

온톨로지는 조직을 움직이는 소프트웨어입니다. 운영 코드베이스에 기울이는 것과 같은 정성으로 다루되, 완벽함보다 비즈니스 가치를 우선하세요.

> **중간 요약**: 원칙은 상황에 맞게 적용하는 지침이며, 기한 안에 동작하는 설계를 먼저 만들고 점진적으로 개선합니다. 다만 이름, 의미, 보안처럼 나중에 고치기 어려운 부분은 처음부터 지켜야 합니다.

## 정리

- 설계 지침 8가지는 현실 모델링, 의도적 선별, 팀 간 협업, 단일 초점, 도구 선택, 인터페이스 추상화, 문서화, 실제 질문을 통한 검증입니다.
- 핵심 원칙은 우선순위 순으로 도메인 주도 설계, 반복 금지(3의 법칙), 개방-폐쇄, 깊은 계층보다 합성이며 충돌 시 앞선 원칙이 우선합니다.
- 원천 데이터의 모양을 복제하지 말고, 한 데이터셋에서 여러 엔터티를 찾아 분리하며, 사람이 읽기 쉬운 이름을 붙입니다.
- 중복은 단일 정식 타입이나 공유 인터페이스로 합치고, 운영 중인 핵심 타입은 수정 대신 링크된 타입과 인터페이스로 확장합니다.
- 원칙은 법칙이 아니므로 현실 제약에 맞춰 점진적으로 적용하되, 이름과 의미와 보안은 타협하지 않습니다.
