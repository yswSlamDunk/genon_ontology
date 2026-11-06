# 레거시 온톨로지 권한 (Legacy ontology permissions)

- 원문: https://www.palantir.com/docs/foundry/object-permissioning/ontology-permissions-legacy/
- 사이드바 위치: Ontology architecture > Object permissioning > Legacy ontology permissions

이 페이지는 프로젝트 기반 권한이 도입되기 전에 온톨로지 리소스(객체 타입, 링크 타입, 액션 타입과 그 메타데이터)에 쓰이던 두 가지 레거시 권한 모델, 즉 온톨로지 역할(Ontology roles)과 데이터소스 파생 권한(datasource-derived permissions)을 설명합니다. 아직 이 모델을 쓰는 환경이 있으므로, 각 모델에서 리소스를 만들고 편집하려면 어떤 역할이나 그룹 소속이 필요한지를 리소스 종류별로 정리합니다.

# 온톨로지 권한 \[레거시] (Ontology permissions \[Legacy])

**주의**: 이제 온톨로지 리소스는 Compass로 권한을 관리합니다(Ontology resources now permissioned via Compass). 온톨로지 리소스(객체 타입, 액션 타입, 링크 타입, 공유 속성(shared property), 인터페이스)는 [Compass 파일 시스템으로 관리되는 일반 프로젝트 리소스](02_ontology-permissions.md)가 될 수 있습니다. 이는 이전의 온톨로지 역할과 데이터소스 파생 권한 모델을 대체합니다. 자세한 내용은 [온톨로지 권한에 대한 최신 문서](02_ontology-permissions.md)를 참고하십시오.

온톨로지 리소스는 객체 타입, 링크 타입, 액션 타입과 그 메타데이터(스키마)를 가리킵니다.

여러분의 환경(enrollment)에는 다음 두 가지 레거시 권한 모델 중 하나가 적용되어 있을 수 있습니다.

1. **[온톨로지 역할(Ontology roles)](#ontology-roles)** 은 온톨로지 리소스에 권한을 부여하는 기본 방법입니다. 온톨로지 역할을 사용하면 백킹 데이터소스(backing datasource)와 무관하게 각 온톨로지 리소스에 [역할](#ontology-roles)을 직접 적용할 수 있습니다.

* 예를 들어 사용자는 온톨로지에서 객체 타입을 편집하기 위해 객체 타입에 대한 `Ontology Editor` 역할만 있으면 되고, 백킹 데이터소스에 대한 권한은 전혀 필요하지 않습니다.
* `Ontology Editor` 역할은 온톨로지 리소스와 그 메타데이터를 편집하는 것만 허용하며, 데이터나 데이터소스 자체에 대한 권한은 부여하지 않습니다. 객체 데이터(메타데이터가 아닌 것)에 대한 접근은 여전히 백킹 데이터소스에 부여된 권한으로 통제됩니다.

2. **[데이터소스 파생 권한(Datasource-derived permissions)](#datasource-derived-permissions)** 은 온톨로지 리소스에 권한을 부여하는 레거시 방식입니다. 데이터소스 파생 권한은 각 객체 타입의 백킹 데이터소스에 정의된 권한에 의존하므로, 온톨로지의 객체 타입과 백킹 데이터소스 사이에 1:1의 직접적인 의존 관계가 생깁니다. 이 때문에 데이터소스 파생 권한을 쓰는 객체 타입에는 백킹 데이터셋이 반드시 있어야 합니다.

* 예를 들어 사용자가 온톨로지에서 객체 타입을 편집하려면 백킹 데이터소스에 대한 `Editor` 접근 권한이 있어야 하고, (온톨로지 수준의) [`Ontology Administrators` 그룹](https://www.palantir.com/docs/foundry/platform-security-management/manage-groups/)의 구성원이어야 합니다.

**설명**: 두 모델의 차이는 "권한 정보를 어디에 저장하느냐"입니다. 온톨로지 역할 모델은 객체 타입마다 별도의 권한 목록(누가 Owner, Editor, Viewer인지)을 따로 둡니다. 데이터소스 파생 모델은 객체 타입에 권한 목록이 없고, 백킹 데이터셋의 권한을 그대로 빌려 씁니다. 그래서 데이터셋 `employees`에 Editor인 사람이 곧 Employee 객체 타입의 Editor가 됩니다.

> **중간 요약**: 레거시 모델은 두 가지입니다. 온톨로지 역할 모델은 리소스마다 역할을 직접 부여하고, 데이터소스 파생 모델은 백킹 데이터소스의 권한을 그대로 따릅니다. 두 모델 모두 지금은 Compass 프로젝트 기반 권한으로 대체되었습니다.

<a id="ontology-roles"></a>
## 온톨로지 역할 (Ontology roles)

온톨로지 역할은 다음과 같이 정의됩니다.

* `Ontology Owner`: 온톨로지 리소스를 편집할 수 있고, 그 보안과 공유에 대한 전체 통제권을 가집니다.
* `Ontology Editor`: 온톨로지 리소스를 편집할 수 있습니다.
* `Ontology Viewer`: 온톨로지 리소스를 볼 수 있지만 편집할 수는 없습니다.
* `Ontology Discoverer`: 스키마를 제외한 온톨로지 리소스의 이름과 메타데이터만 볼 수 있습니다.

위 역할을 온톨로지 리소스에 직접 부여하는 것 외에도, [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md) 애플리케이션에서 온톨로지의 **Ontology Configuration** 탭으로 이동해 온톨로지 수준에서 이 역할들을 부여할 수도 있습니다. 온톨로지 수준에서 부여된 역할 중 그 온톨로지의 모든 리소스에 상속되는 것은 `Ontology owner` 역할뿐입니다. `Ontology editor` 역할은 온톨로지 수준 권한에만 의미가 있습니다.

모범 사례로, 온톨로지 전체를 책임질 신뢰할 수 있는 사용자 그룹(온톨로지 거버넌스 위원회(Ontology Governance Board)라고도 함)을 정하고, 그 사용자 그룹에 온톨로지 전체에 대한 `Ontology Owner` 역할을 부여할 것을 강력히 권장합니다.

기본 온톨로지 역할에 포함된 작업을 사용자 정의하거나, 여러 사용자 그룹의 필요에 맞게 추가 사용자 정의 역할을 구성할 수 있습니다. 자세한 내용은 [역할 문서](https://www.palantir.com/docs/foundry/security/projects-and-roles/#roles)를 참고하십시오.

**설명**: 역할(role)은 "어떤 작업들을 할 수 있는가"를 묶어 이름을 붙인 것입니다. 사용자에게 개별 작업 권한을 하나씩 주는 대신 역할 하나를 주면 그 역할에 포함된 작업 권한을 모두 갖게 됩니다. 이는 데이터베이스의 `GRANT` 문에서 권한 묶음을 역할로 만들어 사용자에게 부여하는 RBAC(Role-Based Access Control) 방식과 같은 개념입니다. 상속(inheritance)은 상위 범위(온톨로지 전체)에 준 역할이 하위 범위(개별 객체 타입)에도 자동으로 적용되는 것을 말합니다.

<a id="create-new-resources-with-ontology-roles"></a>
### 온톨로지 역할로 새 리소스 만들기 (Create new resources with Ontology roles)

온톨로지에서 리소스를 만드는 것은 온톨로지 수준에서 `Ontology Owner` 또는 `Ontology Editor` 역할을 가진 사용자로 제한됩니다. 역할 모델로 새로 만든 객체 타입, 링크 타입, 공유 속성, 액션 타입은 기본적으로 만든 사용자를 해당 리소스의 `Ontology Owner`로, 다른 모든 사용자를 `Ontology Viewer`로 표시합니다. 리소스가 만들어진 뒤에는 만든 사용자가 그 리소스에 추가 역할을 적용할 수 있습니다.

**주의**: 기본적으로 모든 사용자에게는 온톨로지 수준의 `Ontology Editor` 역할이 부여되어 있어, 자기 워크플로를 위한 새 온톨로지 리소스를 만들 수 있습니다. 어떤 사용자 그룹이 새 온톨로지 리소스를 추가할 수 있는지 사용자 정의하려면, `Ontology Owner`가 Ontology Manager의 **Ontology configuration** 탭으로 이동해 온톨로지 수준 역할 부여를 조정하면 됩니다.

<a id="type-specific-edit-permissions-with-ontology-roles"></a>
### 온톨로지 역할에서 타입별 편집 권한 (Type-specific edit permissions with Ontology roles)

<a id="permissions-for-editing-object-types-and-their-properties"></a>
#### 객체 타입과 그 속성을 편집하기 위한 권한 (Permissions for editing object types and their properties)

객체 타입과 그 속성(property)을 변경하려면 사용자는 객체 타입에 대한 `Ontology Editor` 권한이 있어야 합니다. 데이터소스나 열을 객체 타입 속성에 매핑하려는 경우에는 매핑 대상 데이터소스에 대한 `Viewer` 권한도 필요합니다.

<a id="permissions-for-shared-properties"></a>
#### 공유 속성에 대한 권한 (Permissions for shared properties)

[공유 속성](../../02_define-ontologies/02_object-and-link-types/05_shared-properties/01_shared-property-overview.md)을 변경하려면 사용자는 그 공유 속성에 대한 `Ontology Editor` 권한이 있어야 합니다. 또한 공유 속성을 추가하려는 모든 객체 타입에 대해 `Ontology Editor` 권한이 있어야 합니다.

<a id="permissions-for-editing-link-types"></a>
#### 링크 타입을 편집하기 위한 권한 (Permissions for editing link types)

링크 타입을 변경(생성, 삭제, 수정 등)하려면 사용자에게 다음 권한이 있어야 합니다.

* 링크 타입의 양쪽에서 참조하는 객체 타입에 대한 `Ontology viewer` 권한.
* 링크 타입 자체에 대한 `Ontology editor` 권한.

링크 타입이 조인 테이블을 사용하고 변경 내용이 조인 테이블의 변경을 포함한다면, 링크 타입을 뒷받침하는 조인 테이블 데이터소스에 대한 `Viewer` 권한도 필요합니다.

<a id="permissions-for-editing-action-types"></a>
#### 액션 타입을 편집하기 위한 권한 (Permissions for editing action types)

액션 타입을 변경(생성, 삭제, 수정 등)하려면 사용자에게 다음 권한이 있어야 합니다.

* 직접 부여되었거나 [온톨로지 수준](#ontology-roles)에서 상속된, 액션 타입에 대한 최소 `Editor` 권한.
* 액션 타입이 실행 중에 편집(edit)을 만들어 낼 수 있는 모든 객체 타입에 대한 `Ontology Editor` 권한.

액션 타입이 편집을 만들어 낼 수 있는 객체 타입에는 다음이 포함됩니다.

* 객체 생성, 수정, 삭제 규칙에서 참조하는 객체 타입.
* 링크 생성 및 삭제 규칙에서 참조하는 링크 타입에 연결된 객체 타입.
* 함수 기반 액션(function-backed Actions)의 함수(function)에서 편집하는 객체 타입.
* (구성되어 있다면) [액션 로그(Action Log)](../../02_define-ontologies/03_action-types/26_action-log.md#action-log) 객체 타입.

**설명**: 액션 타입 편집 권한이 엄격한 이유는, 액션 타입을 정의하는 사람이 그 액션을 통해 다른 객체 타입의 데이터를 바꾸는 규칙을 만들 수 있기 때문입니다. 예를 들어 "Ticket을 닫으면 Employee의 workload 속성을 1 줄인다"는 액션 타입을 만들려면, Ticket뿐 아니라 Employee 객체 타입에도 편집 권한이 있어야 합니다. 그렇지 않으면 권한 없는 객체 타입을 액션을 통해 우회해서 수정할 수 있게 됩니다.

<a id="read-only-views"></a>
### 읽기 전용 화면 (Read-only views)

사용자에게 객체 타입, 링크 타입, 공유 속성, 액션 타입을 편집할 권한이 없으면 편집 화면이 비활성화되고, 배너가 사용자에게 어떤 권한이 있고 어떤 권한이 없는지 설명합니다.

![보기 권한 배너는 viewer 역할을 가진 사용자에게 접근 정보를 표시합니다.](https://www.palantir.com/docs/resources/foundry/object-permissioning/oma-user-interface-view-permission.png)

![발견 권한 배너는 discoverer 역할을 가진 사용자에게 제한된 접근을 보여 줍니다.](https://www.palantir.com/docs/resources/foundry/object-permissioning/oma-user-interface-discover-permission.png)

> **중간 요약**: 온톨로지 역할은 Owner, Editor, Viewer, Discoverer 네 가지이며, 온톨로지 수준에서 부여한 역할 중 Owner만 모든 리소스에 상속됩니다. 기본적으로 모든 사용자가 온톨로지 수준 Editor라서 리소스를 만들 수 있습니다. 링크 타입 편집에는 양쪽 객체 타입의 Viewer 권한이, 액션 타입 편집에는 그 액션이 편집할 수 있는 모든 객체 타입의 Editor 권한이 추가로 필요합니다.

<a id="datasource-derived-permissions"></a>
## 데이터소스 파생 권한 (Datasource derived permissions)

* [보기 권한](#view-permissions)
* [타입별 편집 권한](#type-specific-edit-permissions)
  * [객체 타입과 그 속성을 편집하기 위한 권한](#permissions-for-editing-object-types-and-their-properties)
  * [공유 속성에 대한 권한](#permissions-for-shared-properties)
  * [링크 타입을 편집하기 위한 권한](#permissions-for-editing-link-types)
  * [액션 타입을 편집하기 위한 권한](#permissions-for-editing-action-types)
* [읽기 전용 화면](#read-only-views)

<a id="view-permissions"></a>
### 보기 권한 (View permissions)

객체 타입이나 링크 타입을 뒷받침하는 데이터소스에 대한 `Viewer` 권한이 있으면, 그 데이터소스와 연결된 객체 타입이나 링크 타입을 볼 수 있습니다.

기본적으로 ***액션 타입은 온톨로지에 접근할 수 있는 모든 사용자에게 보입니다***. 데이터소스 파생 권한 모델에서는 모든 사용자가 모든 액션 타입의 제목, 설명, 규칙을 볼 수 있습니다.

<a id="type-specific-edit-permissions"></a>
### 타입별 편집 권한 (Type-specific edit permissions)

Ontology Manager에서 무엇이든 변경하려면 사용자는 `Ontology Administrators` 사용자 그룹의 구성원이어야 합니다. [그룹과 플랫폼 보안](https://www.palantir.com/docs/foundry/platform-security-management/manage-groups/)에 대해 더 읽어 보십시오.

데이터소스 파생 권한을 사용하는 경우, Foundry 온톨로지에서 변경을 성공적으로 수행하려면 타입별 권한이 추가로 필요할 수 있습니다.

<a id="permissions-for-editing-object-types-and-their-properties"></a>
#### 객체 타입과 그 속성을 편집하기 위한 권한 (Permissions for editing object types and their properties)

객체 타입과 그 속성을 변경하려면 사용자는 객체 타입을 뒷받침하는 데이터소스에 대한 `Editor` 권한이 있어야 합니다.

**주의**: 객체 타입이 [객체 보안 정책(object security policies)](07_object-security-policies.md)을 사용한다면 추가 권한이 적용됩니다. 보안 정책을 만들거나 편집하려면 온톨로지에 대한 `Owner` 권한이 필요합니다. 보안 정책이 구성된 뒤에는 속성을 추가하거나 제거하는 데에도 온톨로지에 대한 `Owner` 권한이 필요합니다. 이로 인해 흔한 작업 흐름 상당수가 매우 제한적이 되므로, 객체 보안 정책을 구성하기 전에 [프로젝트 기반 권한으로 마이그레이션](02_ontology-permissions.md)할 것을 권장합니다.

<a id="permissions-for-shared-properties"></a>
#### 공유 속성에 대한 권한 (Permissions for shared properties)

[공유 속성](../../02_define-ontologies/02_object-and-link-types/05_shared-properties/01_shared-property-overview.md)을 만들거나 편집하거나 객체 타입에 공유 속성을 추가하려면, 사용자는 `Ontology Administrators` 그룹의 구성원이어야 합니다.

<a id="permissions-for-editing-link-types"></a>
#### 링크 타입을 편집하기 위한 권한 (Permissions for editing link types)

링크 타입을 변경하려면 사용자는 링크 타입을 뒷받침하는 데이터소스에 대한 `Editor` 권한과, 링크 타입에서 참조하는 두 객체 타입을 뒷받침하는 데이터소스에 대한 `Viewer` 권한이 있어야 합니다.

<a id="permissions-for-editing-action-types"></a>
#### 액션 타입을 편집하기 위한 권한 (Permissions for editing action types)

* 온톨로지에 접근할 수 있는 모든 사용자는 액션 타입 전체(예: 편집 가능한 속성, 이름, 사용자 권한)를 볼 수 있습니다.
* 온톨로지에서 액션 타입을 변경(생성, 삭제, 수정 등)하려면 사용자는 `Ontology Administrators` 그룹의 구성원이어야 합니다.
* 액션을 실행하려면 사용자는 편집되는 모든 객체 타입에 대해 `Viewer`여야 합니다.
* 사용자가 객체 타입을 수정하거나 객체 타입에 추가하는 액션을 만든다면, 그 객체 타입에 대해 `Edits` 옵션이 활성화되어 있어야 합니다.

액션 타입 권한에 대한 자세한 내용은 [문서](../../02_define-ontologies/03_action-types/19_permissions.md#permissions)를 참고하십시오.

<a id="read-only-views"></a>
### 읽기 전용 화면 (Read-only views)

사용자에게 객체 타입, 링크 타입, 액션 타입을 편집할 권한이 없으면 편집 화면이 비활성화되고, 배너가 사용자에게 어떤 권한이 있고 어떤 권한이 없는지 설명합니다.

<a id="deleting-the-backing-dataset"></a>
### 백킹 데이터셋 삭제 (Deleting the backing dataset)

데이터소스 파생 권한을 쓰는 객체 타입의 백킹 데이터셋이 휴지통에서 영구 삭제되면, 그 객체 타입은 고아(orphaned) 상태로 간주됩니다. 권한은 더 이상 접근할 수 없는 백킹 데이터셋에서 파생되므로, 모든 편집자 권한이 사라져 사용자는 그 객체 타입을 더 이상 수정할 수 없습니다. 온톨로지는 고아 객체 타입을 자동으로 삭제합니다.

**주의**: 고아 객체 타입은 24시간 후 제거됩니다(Orphaned object types are removed after 24 hours). 데이터소스 파생 권한에서는 모든 객체 타입에 백킹 데이터셋이 있어야 합니다. 편집할 수 없는 온톨로지 타입이 쌓이는 것을 막기 위해, 데이터소스 파생 권한을 쓰지만 백킹 데이터셋이 없는 객체 타입은 24시간 후 제거됩니다.

**설명**: 고아 객체 타입은 프로그래밍에서 참조하는 대상이 사라진 댕글링 참조(dangling reference)와 같은 상태입니다. 데이터베이스에서 외래 키가 가리키던 부모 행이 삭제되면 자식 행이 고아가 되는 것처럼, 권한의 출처인 데이터셋이 사라지면 객체 타입은 아무도 관리할 수 없는 상태가 되므로 시스템이 정리합니다.

> **중간 요약**: 데이터소스 파생 모델에서는 데이터소스 Viewer가 곧 객체 타입 Viewer이고, 편집에는 `Ontology Administrators` 그룹 소속과 데이터소스 Editor 권한이 필요합니다. 액션 타입은 모두에게 보이며, 백킹 데이터셋이 영구 삭제된 객체 타입은 고아가 되어 24시간 후 제거됩니다.

## 정리

- 레거시 권한 모델은 온톨로지 역할(리소스마다 역할 직접 부여)과 데이터소스 파생 권한(백킹 데이터소스 권한을 따름) 두 가지이며, 둘 다 프로젝트 기반 권한으로 대체되었습니다.
- 온톨로지 역할은 Owner, Editor, Viewer, Discoverer이고, 온톨로지 수준 Owner만 모든 리소스에 상속됩니다.
- 링크 타입과 액션 타입을 편집할 때는 그 리소스뿐 아니라 연결되거나 편집 대상이 되는 객체 타입에 대한 권한도 필요합니다.
- 데이터소스 파생 모델에서는 `Ontology Administrators` 그룹 소속이 편집의 전제이며, 백킹 데이터셋이 사라진 객체 타입은 24시간 후 자동 삭제됩니다.
