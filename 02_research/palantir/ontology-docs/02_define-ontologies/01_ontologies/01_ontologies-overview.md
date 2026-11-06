# 온톨로지 (Overview)

- 원문: https://www.palantir.com/docs/foundry/ontologies/ontologies-overview/
- 사이드바 위치: Define Ontologies > Ontologies > Overview

이 페이지는 Foundry에서 "온톨로지 하나"가 어떤 단위인지 설명합니다. 온톨로지는 객체 타입, 링크 타입, 액션 타입 같은 리소스를 담는 저장 단위이며, Foundry의 스페이스(space)와 일대일로 대응합니다. 한 조직만 쓰는 비공개 온톨로지와 여러 조직이 함께 쓰는 공유 온톨로지 중 무엇을 골라야 하는지 예시와 함께 설명합니다.

온톨로지(ontology)는 다음을 포함한 온톨로지 리소스 또는 엔터티를 저장하는 산출물(artifact)입니다.

* [객체 타입](../02_object-and-link-types/02_object-types/01_object-types-overview.md)
* [링크 타입](../02_object-and-link-types/06_link-types/01_link-types-overview.md)
* [액션 타입](../03_action-types/01_overview.md)
* [인터페이스](../05_interfaces/01_interface-overview.md)
* [공유 속성(shared property)](../02_object-and-link-types/05_shared-properties/01_shared-property-overview.md)
* [객체 타입 그룹](../02_object-and-link-types/10_type-groups.md)

이러한 리소스를 **온톨로지 리소스(Ontology resources)라고** 부릅니다. 온톨로지는 비공개로 하나의 [조직(organization)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/)에 할당될 수도 있고, 여러 조직 사이에 공유될 수도 있습니다. 공유 온톨로지를 사용하면 서로 다른 조직의 사용자들이 데이터와 워크플로를 안전하게 공유할 수 있습니다. 엔터티를 온톨로지 단위로 묶으면 지정된 조직의 사용자만 해당 온톨로지 엔터티에 접근할 수 있도록 보장됩니다.

**설명**: 관계형 데이터베이스 구조에 대응시키면, 온톨로지 하나는 데이터베이스 서버 안의 스키마(또는 데이터베이스) 하나와 같은 역할을 합니다. 그 안에 테이블 정의(객체 타입), 관계 정의(링크 타입), 저장 프로시저에 해당하는 변경 정의(액션 타입) 등이 들어 있고, 접근 권한도 이 단위로 나뉩니다. Foundry에서 "조직(organization)"은 사용자와 리소스를 엄격히 분리하는 최상위 경계로, 보통 회사 하나가 조직 하나입니다.

<a id="relation-with-spaces"></a>
## 스페이스와의 관계 (Relation with spaces)

온톨로지는 [스페이스(space)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/#spaces)와 1:1로 매핑됩니다. 새 스페이스가 만들어지면, 같은 이름을 가지고 스페이스와 같은 조직 [마킹(marking)](https://www.palantir.com/docs/foundry/security/markings/)을 가진 대응 온톨로지가 동시에 생성됩니다. 비공개 스페이스는 비공개 온톨로지에, 공유 스페이스는 공유 온톨로지에 매핑됩니다.

**설명**: 스페이스는 Foundry 파일 시스템에서 프로젝트와 폴더를 담는 최상위 영역입니다. 예를 들어 "Sky Industries"라는 스페이스를 만들면 "Sky Industries"라는 이름의 온톨로지가 자동으로 함께 생기고, 스페이스에 붙은 조직 마킹(이 조직 구성원만 접근 가능하다는 보안 표시)이 온톨로지에도 똑같이 붙습니다. 따라서 온톨로지를 따로 만드는 절차가 있는 것이 아니라, 스페이스를 만들면 온톨로지가 함께 따라옵니다.

> **중간 요약**: 온톨로지는 객체 타입, 링크 타입, 액션 타입 등 온톨로지 리소스를 담는 단위이며, 스페이스와 1:1로 대응해 스페이스가 생길 때 같은 이름과 같은 조직 마킹으로 함께 생성됩니다.

<a id="private-vs-shared-ontologies"></a>
## 비공개 온톨로지와 공유 온톨로지 (Private vs. shared ontologies)

어떤 종류의 온톨로지가 필요한지는 몇 개의 [조직](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/#organizations)이 같은 객체 타입, 링크 타입, 액션 타입으로 작업해야 하는지에 따라 달라집니다. 조직은 사용자 그룹과 리소스 사이를 엄격하게 분리하며, 대부분의 경우 한 회사는 조직을 하나만 가집니다. 온톨로지에 적용된 조직의 구성원과 게스트 구성원만 그 온톨로지가 담고 있는 리소스에 대한 접근 권한을 받을 수 있습니다.

| | 비공개 온톨로지(Private ontology) | 공유 온톨로지(Shared ontology) |
|---|---|---|
| **선택하는 경우** | 객체가 필요한 모든 사람이 한 조직에 속한 경우 | 두 개 이상의 조직에 속한 사람들이 같은 객체를 필요로 하는 경우 |
| **적용되는 조직** | 하나 | 둘 이상 |
| **접근 권한을 받을 수 있는 사람** | 그 한 조직의 구성원과 게스트 구성원 | 적용된 모든 조직의 구성원과 게스트 구성원 |
| **함께 생성되는 것** | 비공개 스페이스 | 공유 스페이스 |

<a id="when-to-use-a-private-ontology"></a>
### 비공개 온톨로지를 사용하는 경우 (When to use a private ontology)

객체가 필요한 모든 사람이 하나의 조직에 속해 있다면 비공개 온톨로지를 선택하세요. 대부분의 워크플로가 이에 해당합니다.

예를 들어 Sky Industries가 자사 지원 팀을 위해 Flight Alert Inbox 애플리케이션을 만든다고 합시다. 이 애플리케이션은 `Flight`, `Flight Alert`, `Delay`, `Aircraft` 객체 타입과, 이들을 연결하는 링크 타입, 그리고 사용자들이 적용하는 액션 타입을 사용합니다. 이 모든 것은 Sky Industries의 운영을 기술하며, Sky Industries 직원만 볼 수 있어야 합니다. Sky Industries는 이 워크플로를 자사의 비공개 스페이스에서 구축하므로, 그 스페이스에 매핑된 온톨로지는 이 리소스 하나하나를 모두 Sky Industries 조직으로 제한합니다.

여러 팀이 이 하나의 온톨로지를 공유합니다. 애플리케이션을 사용하는 운영 사용자, 애플리케이션을 만드는 애플리케이션 개발자, 그리고 애플리케이션의 백킹 데이터(backing data)를 유지 관리하는 파이프라인 개발자가 그들입니다. 다른 팀과 함께 일한다는 것이 두 번째 온톨로지를 만들 이유가 되지는 않습니다. 어떤 팀이 어떤 리소스에 접근할 수 있는지 제어하려면, 해당 리소스를 담고 있는 프로젝트에서 [그룹(groups)](https://www.palantir.com/docs/foundry/security/users-and-groups/#groups)에 [역할(roles)](https://www.palantir.com/docs/foundry/security/projects-and-roles/#roles)을 부여하세요.

**설명**: 같은 회사 안의 팀 구분은 온톨로지를 나눠서 하는 것이 아니라 권한으로 합니다. 예를 들어 `ops-users` 그룹에는 프로젝트의 Viewer 역할을, `app-developers` 그룹에는 Editor 역할을 주는 식입니다. 데이터베이스에서 팀마다 데이터베이스를 따로 만들지 않고, 하나의 데이터베이스에서 `GRANT`로 사용자 그룹별 권한을 나누는 것과 같은 방식입니다. "백킹 데이터"는 객체 타입의 내용을 채우는 원본 데이터셋을 말합니다.

<a id="when-to-use-a-shared-ontology"></a>
### 공유 온톨로지를 사용하는 경우 (When to use a shared ontology)

두 개 이상의 조직에 속한 사람들이 같은 객체로 작업해야 한다면 공유 온톨로지를 선택하세요.

앞의 예를 이어서, Sunrise Airline이 정비 문제로 인한 항공기 지연을 줄이고 싶어 하며, 자사의 정비 데이터를 Sky Industries의 비행 지연 데이터와 결합하기로 합의했다고 합시다. 두 회사에는 양쪽에 걸친 하나의 객체 타입 세트가 필요합니다. 즉, Sunrise Airline 데이터에서 나온 정비 문제가 Sky Industries 데이터로 만든 `Aircraft` 및 `Delay` 객체에 링크되어야 합니다. 두 회사의 분석가 모두 이 객체들을 열고 같은 액션 타입을 적용할 수 있어야 합니다. 비공개 온톨로지로는 이를 지원할 수 없습니다. 비공개 온톨로지는 하나의 조직으로 제한되므로, 다른 회사의 사용자는 그 리소스에 대한 접근 권한을 받을 수 없기 때문입니다.

대신 관리자는 Sky Industries 조직과 Sunrise Airline 조직이 모두 적용된 공유 스페이스를 만듭니다. 그 스페이스와 함께 생성된 공유 온톨로지는 두 조직 마킹을 모두 가지므로, 두 회사의 분석가 모두 공동 객체 타입, 링크 타입, 액션 타입에 대한 접근 권한을 받을 수 있습니다. 각 회사는 공유하고 싶지 않은 데이터와 워크플로를 위해 자사의 비공개 스페이스와 비공개 온톨로지를 그대로 유지합니다.

**주의**: 공유 온톨로지를 만든다고 해서 그것만으로 하위 데이터가 적용된 모든 조직에 보이게 되지는 않습니다. 비공개 프로젝트에서 공유 프로젝트로 참조된 데이터셋은 원래 조직의 접근 요구 사항을 그대로 유지합니다. 다른 조직의 사용자는 개발자가 상속된 요구 사항을 제거하기 전까지 그 데이터를 볼 수 없습니다. 자세한 내용은 [상속된 마킹과 조직 제거하기](https://www.palantir.com/docs/foundry/building-pipelines/remove-inherited-markings/)를 참고하세요.

**설명**: 온톨로지 수준의 접근과 데이터 수준의 접근은 따로 검사된다는 뜻입니다. 예를 들어 Sky Industries의 비공개 프로젝트에 있는 `delays` 데이터셋에는 "Sky Industries 조직 구성원만"이라는 요구 사항이 붙어 있습니다. 이 데이터셋을 공유 프로젝트에서 참조해 `Delay` 객체 타입의 백킹 데이터셋으로 쓰더라도, 그 요구 사항이 그대로 따라오므로 Sunrise Airline 분석가는 객체 타입은 보여도 실제 데이터 행은 볼 수 없습니다. 의도적으로 상속된 요구 사항을 제거하는 절차를 거쳐야 공유됩니다.

조직, 스페이스, 공유 프로젝트를 만드는 방법을 포함해 이 시나리오를 단계별로 살펴보려면 [워크플로: 조직 간 협업(Workflow: Cross-organization collaboration)](https://www.palantir.com/docs/foundry/security/cross-organization-collaboration/)을 참고하세요. 공유 온톨로지에 대한 자세한 내용은 [공유 온톨로지(Shared ontologies)](03_shared-ontologies.md)를 참고하세요.

> **중간 요약**: 한 조직 안에서만 쓰면 비공개 온톨로지를, 여러 조직이 같은 객체를 써야 하면 공유 온톨로지를 선택합니다. 같은 조직 안의 팀 구분은 온톨로지를 나누지 않고 역할 부여로 처리하며, 공유 온톨로지라도 하위 데이터셋의 상속된 조직 요구 사항은 따로 제거해야 합니다.

## 정리

- 온톨로지는 객체 타입, 링크 타입, 액션 타입, 인터페이스, 공유 속성, 객체 타입 그룹 같은 온톨로지 리소스를 담는 단위입니다.
- 온톨로지는 스페이스와 1:1로 대응하며, 스페이스가 생성될 때 같은 이름과 같은 조직 마킹으로 함께 생성됩니다.
- 사용자가 모두 한 조직에 속하면 비공개 온톨로지를, 둘 이상의 조직이 같은 객체를 써야 하면 공유 온톨로지를 씁니다.
- 같은 조직 내 여러 팀은 온톨로지 하나를 공유하고, 접근 범위는 프로젝트에서 그룹에 역할을 부여해 조절합니다.
- 공유 온톨로지를 만들어도 비공개 프로젝트에서 참조한 데이터셋은 원래 조직의 접근 요구 사항을 유지합니다.
