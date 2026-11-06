# 온톨로지 권한 (Ontology permissions)

- 원문: https://www.palantir.com/docs/foundry/object-permissioning/ontology-permissions/
- 사이드바 위치: Ontology architecture > Object permissioning > Ontology permissions

이 페이지는 객체 타입, 링크 타입, 액션 타입 같은 온톨로지 리소스를 누가 보고, 편집하고, 관리할 수 있는지를 정하는 현재의 방식인 프로젝트 기반 권한(project-based permissions)을 설명합니다. 온톨로지 리소스를 다른 Foundry 파일처럼 프로젝트 안에 저장하고 그 프로젝트의 역할로 권한을 정하는 구조이며, 객체 타입을 보는 권한과 객체 데이터를 보는 권한의 차이, Marketplace 설치와 분류 기반 접근 통제(CBAC)와의 관계도 함께 다룹니다.

온톨로지 리소스를 보고, 편집하고, 관리하는 권한(permission)은 Palantir 플랫폼의 파일 시스템인 [Compass](https://www.palantir.com/docs/foundry/compass/overview/)를 통해 관리됩니다. 온톨로지 리소스는 프로젝트 안에 저장되며, 어느 프로젝트를 선택하느냐에 따라 누가 그 리소스를 보고, 편집하고, 관리할 수 있는지가 결정됩니다.

이 기능은 새 온톨로지에서는 활성화되어 있습니다. 기존 온톨로지의 경우 온톨로지 소유자가 이 기능을 직접 활성화해야 하며, [기존 온톨로지 리소스는 마이그레이션이 필요합니다](../../05_applications/04_ontology-manager/04_migrate-to-project-based-permissions.md).

이 프로젝트 기반 권한 방식은 이전 권한 모델인 [온톨로지 역할과 데이터소스 파생 권한](03_ontology-permissions-legacy.md)을 대체합니다. 이 방식에는 여러 이점이 있습니다.

* **통합된 권한 모델:** 온톨로지 리소스가 다른 리소스 타입과 같은 권한 시스템을 사용하므로, 권한을 한곳에서만 배우고 관리하면 됩니다.
* **일괄 관리:** 프로젝트나 폴더 수준에서 권한을 설정해 여러 리소스에 대한 접근을 한 번에 통제할 수 있으므로, 개별 항목마다 권한을 설정할 필요가 없습니다.
* **권한 설명 가능성:** **Security** 탭은 객체 타입을 보고 편집하는 데 필요한 권한과, 인스턴스를 보거나 액션을 실행하는 데 필요한 권한을 보여 줍니다.
* **추가 개인 정보 통제:** 민감한 온톨로지 리소스에 마킹(marking)을 적용하거나, 사용자에게 역할이 부여되지 않은 프로젝트에 넣어 숨길 수 있습니다.
* **Compass 큐레이션 기본 요소:** 포트폴리오와 태그로 온톨로지 리소스를 정리하고, 역할 부여나 마킹으로 사용자와 관련 없는 리소스를 숨길 수 있습니다.

프로젝트로 마이그레이션해도 백킹 데이터소스(backing datasource)에 누가 접근할 수 있는지는 바뀌지 않습니다. 데이터소스를 백킹으로 하는 객체 타입의 경우, 사용자가 객체를 보려면 여전히 객체 타입과 데이터소스 양쪽에 대한 권한이 필요합니다.

**주의**: [백킹 데이터소스가 없는 객체 타입](../../02_define-ontologies/02_object-and-link-types/02_object-types/02_create-object-type.md#create-an-object-type-without-a-backing-datasource)은 반드시 프로젝트에 저장되어야 하며 프로젝트 기반 권한을 사용해야 합니다. 또한 누가 그 객체를 볼 수 있는지 결정하기 위해 [객체 보안 정책(object security policy)](07_object-security-policies.md)이 필요합니다.

**설명**: Compass는 Foundry의 파일 시스템으로, 운영 체제의 폴더 구조처럼 프로젝트와 폴더 안에 데이터셋, 코드, 애플리케이션 같은 리소스를 저장합니다. 프로젝트 기반 권한은 리눅스 파일 시스템에서 디렉터리 권한이 그 안의 파일에 적용되는 것처럼, 프로젝트에 부여된 역할(Viewer, Editor, Owner 등)이 그 프로젝트 안의 모든 리소스에 적용되는 방식입니다. 마킹(marking)은 "개인 정보 포함" 같은 꼬리표를 리소스에 붙여, 그 마킹에 대한 접근 자격이 있는 사용자만 볼 수 있도록 하는 Foundry의 필수 접근 통제 장치입니다.

> **중간 요약**: 온톨로지 리소스의 권한은 이제 Compass 프로젝트에 저장해 프로젝트 역할로 관리합니다. 이는 이전의 온톨로지 역할과 데이터소스 파생 권한을 대체하며, 통합 관리, 일괄 관리, 권한 설명 가능성 같은 이점이 있습니다. 객체를 보려면 여전히 객체 타입과 데이터소스 양쪽 권한이 필요합니다.

<a id="example-of-project-based-permission"></a>
## 프로젝트 기반 권한의 예 (Example of project-based permission)

프로젝트 `A`에 파일로 저장된 `Building`이라는 객체 타입을 생각해 봅시다. `Building`을 보고, 편집하고, 관리할 수 있는지는 프로젝트 `A`에서의 역할에 달려 있습니다. 프로젝트 `A`에서 `Editor`라면 `Building` 객체 타입을 편집할 수 있습니다. 특정 `Building` 객체(예: `Empire State Building`)를 보려면, 객체 타입에 대한 `Viewer` 역할이 필요하고, 객체 타입의 보안 구성 방식에 따라 백킹 데이터소스에 대한 접근 권한이나 [객체 및 속성 보안 정책](04_managing-object-security.md#object-and-property-security-policies)을 통해 부여된 접근 권한 중 하나가 필요합니다.

![프로젝트 안의 온톨로지 리소스.](https://www.palantir.com/docs/resources/foundry/object-permissioning/ontology-in-project.png)

객체 타입에 대한 보기 권한만 있다면 스키마와 담당자 정보 같은 정보만 볼 수 있고 실제 데이터는 볼 수 없습니다. 필요한 권한을 이해하는 데 도움이 필요하면 Compass 프로젝트 사이드 패널을 확인하십시오.

<a id="viewing-object-types-and-objects"></a>
## 객체 타입과 객체 보기 (Viewing object types and objects)

객체 타입과 객체는 권한이 서로 다르게 적용됩니다. 객체 타입을 보려면 객체 타입에 대한 View 권한이 있어야 하지만, 백킹 데이터소스에 대한 View 권한은 필요하지 않습니다.

객체를 보려면 객체 타입에 대한 View 권한과 데이터에 대한 접근 권한이 모두 있어야 합니다. 기반 데이터에 대한 접근은 객체 타입의 보안 구성에 따라 결정됩니다.

* **[객체 및 속성 보안 정책](04_managing-object-security.md#object-and-property-security-policies):** 객체의 가시성이 백킹 데이터소스 권한과 무관하게 객체 타입에 직접 구성된 정책으로 결정됩니다.
* **[데이터소스 정책](04_managing-object-security.md#data-source-policies):** 객체의 가시성이 백킹 데이터소스의 권한으로 결정됩니다. 객체를 보려면 백킹 데이터소스에 대한 View 권한이 있어야 합니다.

객체 보안 구성에 대한 자세한 내용은 [객체 보안 관리 문서](04_managing-object-security.md)를 참고하십시오. 객체 타입(스키마)과 객체(데이터)의 구분에 대한 자세한 내용은 [객체 권한 문서](01_overview.md)를 참고하십시오.

프로젝트 안에 있는 데이터소스 기반 객체 타입의 경우, 객체가 인덱싱되려면 백킹 데이터소스가 그 프로젝트로 가져와져(import) 있어야 합니다. 백킹 데이터소스가 아직 프로젝트에 없다면, 객체를 만드는 과정에서 가져오라는 안내가 나타납니다.

**설명**: 정리하면 판단은 두 단계로 이루어집니다. 1단계: 사용자가 `Building` 객체 타입에 View 권한이 있는가(프로젝트 역할로 결정). 2단계: 데이터 접근이 허용되는가(데이터소스 정책이면 데이터셋 View 권한, 객체 보안 정책이면 정책 조건 충족 여부). 1단계만 통과하면 "Building에는 name, height 속성이 있다"는 스키마만 보이고, 두 단계를 모두 통과해야 `Empire State Building` 같은 실제 객체가 보입니다.

> **중간 요약**: 객체 타입(스키마)을 보려면 객체 타입 View 권한만 있으면 되지만, 객체(데이터)를 보려면 거기에 더해 데이터 접근 권한이 필요합니다. 데이터 접근은 데이터소스 정책(데이터셋 권한)이나 객체 및 속성 보안 정책(객체 타입에 직접 정의한 정책) 중 구성된 방식으로 결정됩니다.

<a id="edit-permissions-for-links-and-actions"></a>
## 링크와 액션의 편집 권한 (Edit permissions for links and actions)

편집하려는 리소스에 따라 적절한 편집 권한이 필요합니다.

* **링크의 경우:** 링크 타입과 연결된 객체 타입들 모두에 대한 편집 권한이 있어야 합니다.
* **액션의 경우:** 액션 타입과, 그 액션이 편집하는 모든 온톨로지 리소스 타입에 대한 편집 권한이 있어야 합니다.

<a id="packaging-and-installing-with-different-permission-models"></a>
## 서로 다른 권한 모델로 패키징하고 설치하기 (Packaging and installing with different permission models)

Marketplace 제품은 패키징될 때 사용한 것과 같은 권한 모델로 설치됩니다. **Ontology configuration**의 **Require new ontology resources be saved in a project**(새 온톨로지 리소스는 프로젝트에 저장하도록 요구) 토글은 새 온톨로지 리소스의 생성에만 영향을 줍니다. 이 토글은 Marketplace가 **소스 환경**(제품이 패키징된 곳)을 기준으로 **대상 환경**(제품이 설치되는 곳)에 제품을 설치하는 방식을 바꾸지 않습니다.

* **온톨로지 역할로 패키징된 경우:** 온톨로지 역할을 사용해 설치됩니다.
* **프로젝트 권한으로 패키징된 경우:** 프로젝트 권한을 사용해 설치됩니다.
* **게시 후 소스가 프로젝트 권한으로 마이그레이션된 경우:** 다음 업그레이드 때 대상 환경의 온톨로지 리소스가 프로젝트 권한으로 마이그레이션됩니다.

**설명**: Marketplace는 온톨로지 리소스, 파이프라인, 애플리케이션 등을 하나의 제품(패키지)으로 묶어 다른 환경에 설치할 수 있게 하는 Foundry 기능입니다. 소프트웨어 패키지 관리자가 패키지를 빌드한 환경의 설정을 그대로 담아 설치하는 것처럼, 권한 모델도 패키징 당시의 방식이 그대로 따라갑니다.

> **중간 요약**: 링크를 편집하려면 링크 타입과 양쪽 객체 타입에, 액션을 실행하려면 액션 타입과 그 액션이 편집하는 모든 리소스에 편집 권한이 필요합니다. Marketplace 제품은 패키징 당시의 권한 모델로 설치됩니다.

<a id="classification-based-access-controls-cbac"></a>
## 분류 기반 접근 통제 (Classification-based access controls (CBAC))

[분류 기반 접근 통제(CBAC)](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/)가 적용되는 프로젝트에 온톨로지 리소스를 저장하는 경우, 다음 규칙이 적용됩니다.

* 리소스를 만들 때 파일 분류(file classification)를 지정해야 합니다.
* 파일 분류는 [프로젝트 최대 분류(project maximum classification)](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/#project-maximum-classification)와 같거나 낮아야 합니다.
* 분류가 지정되지 않으면 객체 타입 머티리얼라이제이션(materialization)이 실패합니다.

**설명**: 분류 기반 접근 통제는 정부나 국방 분야에서 쓰는 "대외비, 비밀, 일급비밀" 같은 보안 등급을 파일마다 붙이고, 사용자의 허가 등급이 파일 등급 이상일 때만 접근을 허용하는 방식입니다. 프로젝트에는 담을 수 있는 최고 등급이 정해져 있어서, 그보다 높은 등급의 파일은 그 프로젝트에 둘 수 없습니다.

<a id="marketplace-and-file-classifications"></a>
### Marketplace와 파일 분류 (Marketplace and file classifications)

파일 분류는 온톨로지에만 해당하는 것이 아니라 모든 파일에 적용됩니다. 아래 규칙은 프로젝트 권한이 [분류 기반 접근 통제](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/)와 어떻게 상호작용하는지에 영향을 주기 때문에 여기서 따로 언급합니다. Marketplace는 제품 안에 파일 분류를 담아 가지 않습니다.

* **게시 시점:** Marketplace는 파일 분류를 추적하지 않습니다. Marketplace 스토어의 분류가 제거될 분류 중 어느 것보다 낮으면, 사용자에게 그 마킹들에 대한 분류 해제(declassify) 권한이 있는지 확인합니다.
* **설치 시점:** 설치되는 각 파일은 대상 프로젝트의 분류를 따릅니다. 대상 프로젝트의 분류가 Marketplace 스토어의 분류보다 낮으면, 설치하는 사용자가 그 마킹들에 대한 분류 해제 권한을 가지고 있어야 합니다.
* **업그레이드 시:** 파일 분류는 바뀌지 않습니다. 설치 시점에 설정된 분류는 직접 수정할 수 있으며, 그렇게 직접 수정한 내용은 이후 업그레이드에서도 유지됩니다.

![소스 프로젝트와 대상 프로젝트의 분류 마킹이 다르면 Marketplace가 분류 해제 권한을 요청합니다.](https://www.palantir.com/docs/resources/foundry/object-permissioning/ontology-in-projects-marketplace-file-classifications.png)

> **중간 요약**: CBAC가 적용된 프로젝트에서는 온톨로지 리소스를 만들 때 프로젝트 최대 분류 이하의 파일 분류를 지정해야 합니다. Marketplace는 분류를 제품에 담지 않으므로, 게시나 설치 과정에서 분류가 낮아지면 분류 해제 권한이 필요하고, 설치된 파일은 대상 프로젝트의 분류를 따릅니다.

<a id="previous-permission-models"></a>
## 이전 권한 모델 (Previous permission models)

이전에는 온톨로지 리소스의 권한 부여 방식이 온톨로지의 권한 부여 모델에 따라 달랐습니다. 아래 표는 각 모델에서 현재 리소스가 어떻게 관리되는지 요약합니다. [이 레거시 권한 시스템에 대해 더 알아보려면 문서](03_ontology-permissions-legacy.md)를 참고하십시오.

| 레거시 온톨로지 권한 모델 | 설명 |
| --- | --- |
| **온톨로지 역할(Ontology roles)** | - 온톨로지 리소스는 Ontology Manager에서 온톨로지 전용 역할(Ontology `viewer`, Ontology `editor`, Ontology `owner`)로 권한이 부여됩니다. 이 리소스들은 프로젝트의 리소스가 아닙니다. |
| **데이터소스 파생(Datasource-derived)** | - 온톨로지 리소스는 객체의 백킹 데이터소스에서 권한을 물려받습니다. 예를 들어 백킹 데이터소스에 대해 `editor`일 때, 그리고 그때에만 객체 타입에 대해서도 `editor`입니다. |

## 정리

- 온톨로지 리소스의 권한은 Compass 프로젝트에 저장해 프로젝트 역할로 관리하며, 이것이 이전의 온톨로지 역할과 데이터소스 파생 방식을 대체합니다.
- 객체 타입을 보려면 객체 타입 View 권한, 객체를 보려면 거기에 더해 데이터소스 권한이나 객체 보안 정책을 통한 접근이 필요합니다.
- 백킹 데이터소스가 없는 객체 타입은 프로젝트 저장과 객체 보안 정책이 필수입니다.
- 링크와 액션 편집에는 관련된 모든 리소스의 편집 권한이 필요하고, Marketplace 제품은 패키징 당시의 권한 모델로 설치됩니다.
- CBAC 프로젝트에서는 파일 분류 지정이 필수이며, Marketplace 게시와 설치에서 분류가 낮아지면 분류 해제 권한이 필요합니다.
