# 읽기 및 쓰기 권한 부여 (Read and write authorizations)

- 원문: https://www.palantir.com/docs/foundry/action-types/read-write-authorizations/
- 사이드바 위치: Define Ontologies > Action types > Read and write authorizations

이 페이지는 액션 타입에 보안 경계를 추가하는 읽기 권한 부여(read authorization)와 쓰기 권한 부여(write authorization)를 설명합니다. 읽기 권한 부여는 액션이 읽을 수 있는 마킹된 데이터의 상한을, 쓰기 권한 부여는 액션이 만들어 내는 데이터가 갖춰야 할 보안의 하한을 정합니다. 두 설정이 다르면 데이터의 보안 등급이 낮아지는(기밀 해제) 일이 생길 수 있으므로, 그 위험과 구성 방법을 함께 다룹니다.

**참고**: 베타(Beta). 읽기 및 쓰기 권한 부여는 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며, 사용자의 환경(enrollment)에서는 제공되지 않을 수 있습니다. 활발히 개발 중이므로 기능과 플랫폼 지원이 바뀔 수 있습니다.

읽기 및 쓰기 권한 부여는 액션 타입에 보안 경계를 추가합니다. [읽기 권한 부여](#read-authorization)는 액션이 직접 읽거나, 다른 로직이 액션을 호출할 때 입력으로 받을 수 있는 마킹된 데이터를 제한합니다. [쓰기 권한 부여](#write-authorization)는 액션이 만들거나 수정하는 데이터의 최소 보안 요구 사항을 정합니다. 이 권한 부여들은 사용자의 기존 권한과 액션 타입의 [제출 조건(submission criteria)](08_submission-criteria.md)을 보완합니다. 접근 권한을 새로 부여하거나 기존 권한이나 제출 조건을 대체하지는 않습니다.

**설명**: 마킹(marking)은 데이터에 붙는 보안 라벨입니다. 예를 들어 `PII`(개인 식별 정보) 마킹이 붙은 데이터셋은 그 마킹에 대한 접근 권한이 있는 사용자만 볼 수 있고, 이 데이터에서 파생된 데이터에도 같은 마킹이 따라가는 것이 원칙입니다. 이 페이지의 두 설정은 사용자가 아니라 액션 자체에 "읽을 수 있는 데이터의 최대 보안 수준"과 "써야 하는 데이터의 최소 보안 수준"을 붙이는 기능입니다.

<a id="read-authorization"></a>
## 읽기 권한 부여 (Read authorization)

읽기 권한 부여는 액션이 실행 중에 읽거나 입력으로 받을 수 있는 데이터에 추가적인 상한을 둡니다. 읽기 권한 부여는 Foundry가 파라미터에 값을 불러올 때(다른 로직이 액션을 호출하는 경우 포함)와 함수 기반 액션이 읽기를 수행할 때 적용됩니다. 데이터가 구성된 읽기 권한 부여를 넘어서면, 사용자가 원래는 그 데이터에 접근할 수 있더라도 액션은 그 데이터를 불러올 수 없습니다.

액션을 실행하는 사용자는 여전히 데이터에 접근할 권한을 가지고 있어야 합니다. 읽기 권한 부여에 마킹이 하나도 구성되어 있지 않으면, 액션에는 사용자의 기존 접근 권한 외에 추가적인 읽기 경계가 없습니다.

**설명**: 실제로 읽을 수 있는 범위는 "사용자가 접근할 수 있는 데이터"와 "읽기 권한 부여가 허용하는 데이터"의 교집합입니다. 예를 들어 사용자가 `PII`와 `Finance` 마킹 데이터를 모두 볼 수 있어도, 액션의 읽기 권한 부여가 `Finance`까지만 허용한다면 이 액션은 `PII` 마킹 데이터를 불러오지 못합니다.

<a id="write-authorization"></a>
## 쓰기 권한 부여 (Write authorization)

쓰기 권한 부여는 액션이 만들거나 수정하는 데이터가 충족해야 하는 최소 보안을 정의합니다. Foundry는 결과 데이터의 보안을 검증하고, 결과가 구성된 최소치보다 낮으면 액션을 차단합니다.

쓰기 권한 부여는 사용자에게 마킹에 대한 접근 권한을 주지 않으며, 구성된 마킹을 자동으로 추가하지도 않고, 원래 유효하지 않은 편집을 허용해 주지도 않습니다. 사용자는 필요한 권한을 가지고 있어야 하고, 해당하는 경우 유효한 마킹 값을 제공해야 하며, 액션 타입의 제출 조건을 통과해야 합니다. 쓰기 권한 부여에 마킹이 하나도 구성되어 있지 않으면, 이 기능은 추가적인 최소 출력 보안을 강제하지 않습니다.

구성된 쓰기 권한 부여는 플랫폼이 관리하는 쓰기, 즉 [액션 로그(action log)](26_action-log.md)와 [편집 이력(edit history)](../../06_ontology-architecture/04_object-edits-and-materializations/03_user-edit-history.md) 객체에는 적용되지 않습니다. 따라서 액션 로그와 편집 이력에 적용되는 보안은 쓰기 권한 부여보다 낮을 수 있습니다.

> **중간 요약**: 읽기 권한 부여는 액션이 불러올 수 있는 데이터 보안의 상한이고, 쓰기 권한 부여는 액션이 만드는 데이터 보안의 하한입니다. 둘 다 기존 권한과 제출 조건을 대체하지 않고 보완하며, 쓰기 권한 부여는 액션 로그와 편집 이력에는 적용되지 않습니다.

<a id="mandatory-marking-guarantees"></a>
## 필수 마킹 보장 (Mandatory marking guarantees)

[필수 마킹(mandatory marking)](https://www.palantir.com/docs/foundry/security/markings/#data-dependency)은 데이터 의존성을 따라 전파되어, 파생 데이터가 입력 데이터의 보호를 유지하도록 하기 위한 것입니다. 액션의 경우 출력 데이터에 적용되는 보안은 액션의 로직이 정합니다. 따라서 액션은 받거나 읽은 데이터와 같은 보안, 더 높은 보안, 또는 더 낮은 보안으로 출력을 만들 수 있습니다. 읽기 및 쓰기 권한 부여는 액션이 할 수 있는 일에 상한과 하한을 정합니다. 둘이 함께 액션의 입력과 출력 사이에 허용되는 보안 차이를 보장합니다.

쓰기 권한 부여를 읽기 권한 부여보다 덜 제한적으로 구성하면, 액션은 자신이 읽을 수 있는 데이터의 보안 경계보다 낮은 보안으로 데이터를 쓸 수 있습니다. 이는 의도적으로 필수 마킹 전파를 끊는 것이며, 데이터 기밀 해제(declassification)로 이어질 수 있습니다. 읽기와 쓰기 설정이 다를 때마다 액션 타입 편집기는 경고를 표시합니다.

읽기와 쓰기 권한 부여가 다르면, Foundry는 액션 타입을 저장하거나 게시하는 사용자의 권한을 확인합니다. 이 사용자는 읽기 경계와 쓰기 경계 사이에서 끊기는 모든 필수 마킹을 기밀 해제할 권한을 가지고 있어야 합니다. 확인에 성공하면 액션 타입은 승인된 기밀 해제를 수행할 수 있으며, Foundry는 런타임에 이 권한 확인을 반복하지 않습니다.

**경고**: 읽기 및 쓰기 권한 부여는 현재 선택 사항입니다. 읽기 권한 부여가 구성되어 있지 않으면, Foundry는 액션 타입을 저장하거나 게시할 때 기밀 해제 권한 확인을 수행하지 않습니다. 따라서 액션이 쓰기 경계보다 높은 데이터를 읽고 덜 제한적인 데이터를 쓸 수 있으며, 이는 데이터 유출(data spill)을 일으킬 수 있습니다. 액션이 마킹된 데이터를 읽을 가능성이 있다면 항상 읽기 권한 부여를 구성하세요.

**설명**: 구체적인 예로, 읽기 권한 부여가 `{PII, Finance}`, 쓰기 권한 부여가 `{Finance}`라고 합시다. 이 액션은 `PII` 마킹이 붙은 고객 데이터를 읽어서 `Finance` 마킹만 붙은 객체에 결과를 쓸 수 있습니다. 즉 `PII` 마킹이 출력에서 빠지므로, `PII` 접근 권한이 없는 사람도 그 출력을 볼 수 있게 됩니다. 이것이 기밀 해제입니다. 그래서 이 액션 타입을 저장하는 사람은 `PII` 마킹을 기밀 해제할 권한이 있어야 합니다. 반대로 읽기 권한 부여를 아예 설정하지 않으면 이 확인 절차 자체가 일어나지 않으므로, 경고문은 이런 경우를 막기 위해 읽기 권한 부여를 꼭 설정하라고 말합니다.

> **중간 요약**: 액션의 출력 보안은 로직이 정하므로 입력보다 낮아질 수 있으며, 읽기와 쓰기 권한 부여가 그 차이의 범위를 정합니다. 쓰기 쪽이 더 느슨하면 기밀 해제가 일어나며, 저장 또는 게시하는 사람에게 해당 마킹의 기밀 해제 권한이 있어야 합니다. 읽기 권한 부여를 설정하지 않으면 이 확인이 없어 데이터 유출 위험이 있습니다.

<a id="authorization-rules-by-marking-category"></a>
## 마킹 범주별 권한 부여 규칙 (Authorization rules by marking category)

Foundry는 구성된 마킹을 범주에 따라 다음과 같이 조합합니다.

| 마킹 범주 | 읽기 권한 부여 | 쓰기 권한 부여 |
| --- | --- | --- |
| 분류 마킹(Classification markings) | 환경에 구성된 계층 구조와 연언적(conjunctive) 또는 선언적(disjunctive) 범주 규칙을 따릅니다. | 환경에 구성된 계층 구조와 연언적 또는 선언적 범주 규칙을 따릅니다. |
| 기타 필수 마킹(Other mandatory markings) | 구성된 모든 마킹이 필요합니다. | 구성된 모든 마킹이 필요합니다. |
| 조직(Organizations) | 구성된 모든 Organization이 필요합니다. | 구성된 Organization 중 최소 하나가 필요합니다. |

분류 동작은 환경마다 다를 수 있습니다. 분류 계층 구조와 연언적 또는 선언적 범주에 대한 자세한 내용은 [분류 기반 접근 제어(Classification-based Access Controls)](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/#conjunctive-and-disjunctive-classification-marking-categories)를 참고하세요.

**설명**: 연언적(conjunctive)은 AND 조건, 선언적(disjunctive)은 OR 조건을 뜻합니다. 예를 들어 연언적 범주에서 마킹 A와 B가 구성되면 둘 다 만족해야 하고, 선언적 범주라면 둘 중 하나만 만족해도 됩니다. 계층 구조는 "기밀"이 "대외비"보다 높은 식의 등급 순서를 말합니다.

<a id="configure-read-and-write-authorizations"></a>
## 읽기 및 쓰기 권한 부여 구성 (Configure read and write authorizations)

액션 타입 편집기에서 **Access constraints**(접근 제약)를 켜면 권한 부여를 구성할 수 있습니다. 접근 제약을 켜면 두 권한 부여가 마킹 없는 상태로 초기화됩니다. 접근 제약을 끄면 두 권한 부여가 모두 지워집니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/read-write-authorizations-write-security.png" alt="Access constraints가 켜져 있고, Write security 탭에 분류, 필수 마킹, Organization 요구 사항이 표시된 화면." width="800" />

**Write security**와 **Read security** 탭에서 각 권한 부여를 따로 구성합니다. 설정이 서로 다르면 편집기가 경고를 표시합니다. 권한 부여에 사용자가 볼 수 없는 값이 들어 있으면, 그 값은 가려진(redacted) 상태로 표시되며 편집할 수 없습니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/read-write-authorizations-read-security.png" alt="분류가 선택된 Read security 탭과, 읽기 및 쓰기 권한 부여가 달라서 표시된 기밀 해제 경고." width="800" />

액션을 제출하기 전에, 액션 폼은 쓰기 권한 부여를 기준으로 **Minimum required security**(최소 필요 보안)를 표시할 수 있습니다. 상태는 다음 중 하나입니다.

* **Security passed:** 대상 데이터의 보안이 구성된 최소치를 충족할 것으로 예상됩니다.
* **Security not passed:** 대상 데이터의 보안이 구성된 최소치보다 낮습니다.
* **Can’t be determined:** Foundry가 제출 전에 대상 데이터의 보안을 판단할 수 없습니다.
* **Not set:** 쓰기 권한 부여 마킹이 구성되어 있지 않습니다.
* **Redacted:** 사용자가 구성된 권한 부여를 볼 수 없습니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/read-write-authorizations-minimum-security.png" alt="제출 전에 판단할 수 없는 최소 필요 보안이 표시된 액션 폼." width="500" />

폼의 상태 표시는 미리 피드백을 주기 위한 것입니다. 최종 검증은 액션이 제출될 때 Foundry가 수행하며, 결과 데이터가 쓰기 권한 부여를 충족하지 않으면 액션이 실패합니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/read-write-authorizations-submission-error.png" alt="액션의 데이터가 구성된 분류 또는 마킹 요구 사항을 충족하지 않을 때 표시되는 오류 메시지." width="600" />

> **중간 요약**: 액션 타입 편집기의 Access constraints를 켠 뒤 Write security와 Read security 탭에서 각각 구성합니다. 액션 폼은 제출 전에 최소 필요 보안 상태를 미리 보여 주지만, 최종 검증은 제출 시점에 이루어집니다.

## 정리

- 읽기 권한 부여는 액션이 불러오거나 입력받을 수 있는 마킹된 데이터의 상한을, 쓰기 권한 부여는 액션이 만드는 데이터 보안의 하한을 정합니다.
- 두 기능은 사용자 권한과 제출 조건을 보완할 뿐 대체하지 않으며, 쓰기 권한 부여는 액션 로그와 편집 이력에는 적용되지 않습니다.
- 쓰기 쪽이 읽기 쪽보다 느슨하면 필수 마킹 전파가 끊겨 기밀 해제가 일어나므로, 저장하거나 게시하는 사람에게 기밀 해제 권한이 필요합니다.
- 읽기 권한 부여를 설정하지 않으면 이 확인이 없어 데이터 유출이 생길 수 있으므로, 마킹된 데이터를 읽는 액션에는 반드시 설정합니다.
- 마킹 범주별로 조합 규칙이 다르며, 구성은 Access constraints와 Write security, Read security 탭에서 합니다.
