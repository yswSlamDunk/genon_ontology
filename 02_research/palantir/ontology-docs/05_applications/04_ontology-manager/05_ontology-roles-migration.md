# 온톨로지 역할 마이그레이션 [레거시] (Ontology roles migration [Legacy])

- 원문: https://www.palantir.com/docs/foundry/ontology-manager/ontology-roles-migration/
- 사이드바 위치: Applications > Ontology Manager > Ontology roles migration [Legacy]

이 페이지는 온톨로지 리소스(객체 타입, 링크 타입, 액션 타입)의 권한 관리 방식을 "데이터소스에서 파생된 권한"에서 "온톨로지 역할(Ontology roles)"로 옮기는 레거시 마이그레이션 절차를 설명합니다. 핵심은 리소스의 정의(메타데이터)를 편집할 권한과 그 리소스에 담긴 실제 데이터를 볼 권한을 분리한다는 점입니다. 현재는 Compass 파일 시스템 기반 권한이 최신 방식이므로, 이 페이지는 기존 환경을 이해하거나 이전 설정을 정리할 때 참고하는 자료입니다.

**주의**: 레거시(Legacy). 이 페이지는 온톨로지 리소스 권한 부여에 더 이상 최신 방법이 아닌 레거시 프로세스를 설명합니다. 이제 온톨로지 리소스는 [Compass 파일 시스템을 사용해 권한을 부여](../../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)할 수 있습니다. 이전하려면 [마이그레이션 가이드를 검토하세요.](04_migrate-to-project-based-permissions.md)

[온톨로지 역할(Ontology roles)](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#ontology-roles)은 온톨로지 리소스에 대한 레거시 인가(authorization) 모델로, [데이터소스 파생 권한(datasource-derived permissions)](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#datasource-derived-permissions)을 대체한 것입니다. 온톨로지 역할은 객체 타입, 링크 타입, 액션 타입에 적용되며, 이들을 "온톨로지 리소스"라고 부릅니다. 공유 속성(shared property) 타입, 인터페이스 등 온톨로지의 최신 기능을 사용하려면 온톨로지 역할이 필요합니다. 기본적으로 2023년 9월 이후 생성된 모든 신규 환경(enrollment)에서는 온톨로지 역할이 사용되어 왔습니다.

온톨로지 역할을 사용하면 각 온톨로지 리소스와 그 메타데이터에 역할을 *직접* 부여할 수 있습니다. 모든 메타데이터 권한은 Ontology Manager에서 관리합니다. 온톨로지 역할을 사용하면 온톨로지 리소스(예: `Aircraft` 객체 타입)를 그 리소스의 *데이터*, 즉 [객체 인스턴스](../../02_define-ontologies/02_object-and-link-types/02_object-types/01_object-types-overview.md)(예: 온톨로지 객체로 표현된 특정 비행기)와 링크 인스턴스로부터 분리할 수 있습니다. 이 데이터 인스턴스는 계속 입력 데이터소스의 권한으로 관리됩니다. [온톨로지 권한](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md)에 대해 자세히 알아보세요.

각 온톨로지는 하나 이상의 [Foundry 조직(organization)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/#organizations)에 연결됩니다.

역할별 권한은 [온톨로지 역할 문서](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#ontology-roles)에 자세히 나와 있습니다.

**주의**: 온톨로지 역할로 마이그레이션된 모든 객체 타입, 링크 타입, 액션 타입은 해당 온톨로지에 접근할 수 있는 모든 사용자에게 보기 권한이 주어집니다. 따라서 온톨로지 리소스 정보는 그 온톨로지의 모든 사용자가 접근할 수 있습니다.

**설명**: 여기서 구분해야 할 두 가지는 "스키마"와 "행 데이터"입니다. 데이터베이스로 치면 `Aircraft` 객체 타입의 정의(이름, 속성 목록, 기본 키 설정)는 `CREATE TABLE` 문에 해당하는 메타데이터이고, 비행기 한 대 한 대의 행은 실제 데이터입니다. 데이터소스 파생 권한에서는 백킹 데이터셋의 권한 하나가 두 가지를 모두 결정했습니다. 온톨로지 역할에서는 메타데이터 권한(누가 객체 타입 정의를 보고 고칠 수 있는가)은 객체 타입에 직접 부여한 역할이 정하고, 행 데이터를 볼 권한은 여전히 데이터셋 권한이 정합니다. 그래서 마이그레이션 후에는 데이터셋 접근 권한이 없는 사용자도 `Aircraft` 객체 타입의 정의는 볼 수 있지만, 비행기 행 데이터는 볼 수 없습니다.

온톨로지 리소스를 온톨로지 역할로 마이그레이션하는 데 정해진 순서는 없습니다. 따라서 일부 객체 타입은 [데이터소스 파생 권한](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#datasource-derived-permissions)을, 다른 객체 타입은 온톨로지 역할을 사용하는 혼합 상태가 가능합니다. 그래서 이 마이그레이션에서는 `able to edit an object type`(객체 타입을 편집할 수 있음)을 다음과 같이 정의합니다.

* **데이터소스 파생 권한을 사용하는 객체 타입:** 사용자가 그 객체 타입의 입력 데이터소스에 `Editor` 권한을 가지고 있습니다.
* **온톨로지 역할을 사용하는 객체 타입:** 사용자가 객체 타입에 `Ontology Editor` 권한을 가지고 있으며, 입력 데이터소스에는 어떤 권한도 필요하지 않습니다. 이 권한은 온톨로지 리소스와 그 메타데이터를 편집하는 것만 허용하며, 데이터나 데이터소스 자체에 대한 권한은 부여하지 않습니다. 객체 *데이터*(*메타데이터*가 아닌)에 대한 접근은 여전히 입력 데이터소스에 부여된 권한으로 관리됩니다.

> **중간 요약**: 온톨로지 역할은 리소스 정의(메타데이터)에 대한 권한을 리소스에 직접 부여하고, 객체 데이터 접근은 계속 데이터소스 권한에 맡기는 모델입니다. 마이그레이션은 리소스별로 순서 없이 진행할 수 있어 두 방식이 섞여 있을 수 있습니다.

<a id="migrate-to-ontology-roles"></a>
## 온톨로지 역할로 마이그레이션하기 (Migrate to ontology roles)

환경에서 온톨로지 역할이 활성화되어 있지만 본인이 소유한 온톨로지 리소스를 아직 역할 인가 모델로 마이그레이션하지 않았다면, Ontology Manager에 마이그레이션을 안내하는 배너가 표시됩니다.
또는 온톨로지 리소스 표를 볼 때, 본인이 소유한 리소스 중 아직 "Same permissions as backing datasource"(백킹 데이터소스와 같은 권한)를 사용하는 것만 필터링할 수 있습니다.

온톨로지 역할은 아직 모든 Foundry 환경에서 사용할 수 있는 것은 아닙니다. 온톨로지 역할에 접근할 수 없다면 Palantir Support에 문의하세요.

<a id="prerequisites"></a>
### 사전 요구 사항 (Prerequisites)

마이그레이션을 수행하려면 사용자에게 다음 권한이 있어야 합니다.

1. Foundry 온톨로지를 변경할 수 있는 권한.

2. 개별 리소스마다 다음 권한.

   * 객체 타입의 경우, 입력 데이터소스에 `Owner` 권한이 있어야 합니다.
   * 일대다 링크 타입의 경우 추가 권한이 필요 없습니다. 링크 타입이 참조하는 두 객체 타입 모두에 `Viewer` 권한만 있으면 되고, 사용자는 링크 타입 자체 또는 온톨로지 수준에서 `Owner`여야 합니다.
   * 다대다 링크 타입의 경우, 링크 타입의 입력 데이터소스에도 `Owner` 권한이 있어야 합니다.
   * 액션 타입에는 추가 권한이 필요 없습니다.

**주의**: 온톨로지 역할로 마이그레이션한 뒤 [액션 타입을 수정](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#permissions-for-editing-action-types)하려면 추가 권한이 필요합니다. 역할을 사용하는 액션 타입을 수정하려면 액션 타입이 편집하는 모든 객체 타입과 액션 타입 자체에 대한 권한이 필요합니다.

**설명**: 링크 타입 종류에 따라 요구 권한이 다른 이유는 저장 구조가 다르기 때문입니다. 일대다 링크는 "다" 쪽 객체 타입의 외래 키 열로 표현되므로 별도의 데이터셋이 없습니다. 반면 다대다 링크는 관계형 데이터베이스의 조인 테이블(예: `student_id`, `course_id` 두 열만 있는 `enrollments` 테이블)처럼 링크 자체를 담는 데이터소스가 따로 있으므로, 그 데이터소스에 대한 `Owner` 권한이 필요합니다.

<a id="notification-to-migrate"></a>
### 마이그레이션 알림 (Notification to migrate)

온톨로지 역할로의 마이그레이션은 [Upgrade Assistant](https://www.palantir.com/docs/foundry/upgrade-assistant/overview/)로 관리합니다. 전용 Upgrade Assistant 작업이 마이그레이션해야 하는 온톨로지 리소스 목록과, 마이그레이션을 수행할 권한이 있는 담당자를 함께 보여 줍니다. Upgrade Assistant에서 리소스를 열면 Ontology Manager 애플리케이션 안에서 해당 리소스의 **Security** 탭으로 이동하여 마이그레이션할 수 있습니다.

사용자에게 온톨로지 역할을 설정할 권한이 있으면, 아직 마이그레이션되지 않은 온톨로지 리소스는 **Security** 탭의 마이그레이션 인터페이스에 나타나며 여기서 처음으로 온톨로지 역할을 설정합니다. 온톨로지 리소스가 마이그레이션된 뒤에는 **Security** 탭에 온톨로지 역할 선택기가 표시되며, `Ontology Owners`가 이를 업데이트할 수 있습니다.

<a id="migrate-using-ontology-manager"></a>
### Ontology Manager로 마이그레이션하기 (Migrate using Ontology Manager)

온톨로지 리소스(객체 타입, 액션 타입, 링크 타입)를 역할로 마이그레이션하는 방법은 두 가지입니다. 온톨로지 리소스의 [일괄 마이그레이션](#bulk-migration-of-ontology-resources)과 모든 온톨로지 리소스에 대한 [하나씩 마이그레이션](#one-by-one-migration-for-all-ontology-resources)입니다.

<a id="bulk-migration-of-ontology-resources"></a>
#### 온톨로지 리소스의 일괄 마이그레이션 (Bulk migration of Ontology resources)

온톨로지 리소스를 역할로 일괄 마이그레이션할 수 있습니다. 진행하기 전에 [사전 요구 사항](#prerequisites) 목록을 확인하세요. 한 번에 500개 리소스까지만 마이그레이션할 수 있습니다.

일괄 마이그레이션을 하려면 Ontology Manager의 **Advanced**로 이동해 Migrations 섹션에서 **continue with migration assistant**를 선택합니다.

마이그레이션 마법사가 다음 단계로 나타납니다.

1. **Choose resources(리소스 선택):** 같은 역할을 적용할 객체 타입, 링크 타입, 액션 타입을 모두 선택합니다. 아래 이미지는 마이그레이션 마법사에서 리소스를 선택하는 인터페이스를 보여 줍니다.

![일괄 마이그레이션.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-migration-wizard-choose-resources.png)

2. **Related resources(관련 리소스):** 함께 마이그레이션할 수 있는 관련 리소스(링크 타입 또는 액션 타입)가 있을 때만 이 단계가 표시됩니다.
3. **Assign roles(역할 할당):** 이 객체 타입들에 할당할 그룹/사용자와 기본 역할을 직접 설정할 수 있습니다. 역할 마이그레이터는 현재 일괄로 역할을 제안할 수 없습니다. 역할을 부여할 때는 **사용자**보다 **사용자 그룹**을 사용할 것을 강력히 권장합니다. 액션 타입을 마이그레이션할 때는 참조되는 객체 타입과 액션 타입이 배포된 모든 사용 사례에 대해 충분한 맥락을 가진 사용자에게만 권한을 부여하세요.
4. **Summary(요약):** 요약을 확인하고, 마이그레이션의 영향을 확인(acknowledge)한 뒤, 마이그레이션을 완료해 역할을 적용합니다.

**경고**: 온톨로지 역할로의 마이그레이션은 되돌릴 수 없습니다(Migrating to Ontology roles is irreversible). 마이그레이션의 영향을 확인한다는 것은, 이전에 백킹 데이터소스에서 파생되던 권한이 새로 할당한 역할 부여로 덮어쓰이며 마이그레이션이 되돌릴 수 없다는 점을 인정하는 것입니다.

**설명**: 개별 사용자보다 그룹에 역할을 주라는 권장은 일반적인 접근 제어 설계 원칙입니다. 예를 들어 `alice`, `bob`, `carol` 세 사람에게 각각 `Ontology Editor`를 주면 사람이 바뀔 때마다 리소스마다 권한을 고쳐야 합니다. `aircraft-data-team` 그룹 하나에 역할을 주면 그룹 구성원만 바꾸면 되므로, 리소스가 수백 개여도 관리 지점이 하나로 줄어듭니다.

<a id="exceptions-to-bulk-migration"></a>
##### 일괄 마이그레이션의 예외 (Exceptions to bulk migration)

일부 액션 타입은 추가 단계 없이는 일괄 마이그레이션할 수 없습니다.

다음과 같은 경우 액션 타입을 역할로 마이그레이션할 수 없습니다.

* 액션 타입에 현재 사용자의 권한을 확인하는 제출 조건(submission criteria)이 없는 경우.
  * 해결 방법: Ontology Manager에서 액션 타입의 **Security & Submission criteria** 탭(**Submission criteria** 섹션)에 현재 사용자 기반 조건을 추가하고, 온톨로지에 저장한 뒤 마이그레이션을 다시 시도합니다.
* 액션 타입이 함수(function)로 뒷받침되며, 마이그레이션 전에 `@edits decorators`와 함께 다시 게시해야 하는 경우.
  * 해결 방법: [데코레이터](../../02_define-ontologies/04_functions/12_typescript-v1/02_decorators.md#decorators) 문서의 단계를 참조하세요.

이 문제들을 해결하려면 **Action Types** 페이지로 이동해 **Same permissions as backing datasource**로 필터링합니다. 그러면 문제 때문에 마이그레이션되지 않은 액션 타입이 표시됩니다. 남아 있는 문제를 모두 해결한 다음, 남은 액션 타입에 대해 다시 일괄 마이그레이션을 진행합니다.

**설명**: 두 예외 모두 "이 액션이 무엇을 바꾸고 누가 실행할 수 있는지"를 시스템이 명시적으로 알아야 한다는 요구에서 나옵니다. 데이터소스 파생 권한에서는 데이터셋 권한이 실행 가능 여부를 암묵적으로 제한했지만, 역할로 바꾸면 그 제한이 사라지므로 제출 조건으로 사용자 확인을 명시해야 합니다. 또 함수 기반 액션은 함수 코드가 어떤 객체 타입을 편집하는지 `@edits` 데코레이터로 선언해 두어야, 그 객체 타입에 대한 권한을 검사할 수 있습니다.

<a id="one-by-one-migration-for-all-ontology-resources"></a>
#### 모든 온톨로지 리소스에 대한 하나씩 마이그레이션 (One-by-one migration for all Ontology resources)

Ontology Manager 홈 페이지에서 마이그레이션할 온톨로지 리소스 종류(객체 타입, 링크 타입, 액션 타입)를 선택하고, `Security setup`을 `Same permissions as backing datasource`로, `permissions`를 `owner`로 필터링합니다.

마이그레이션할 엔터티를 선택한 다음, 헤더의 **Migrate to roles** 또는 Security 탭의 **Start using roles**를 선택합니다.

마이그레이션 마법사가 두 가지 역할 제안 옵션, **Datasource roles**와 **Ontology admins and datasource roles**와 함께 나타납니다. 이 옵션들로 기존 온톨로지 설정에 맞는 역할을 사용하고 구성할 수 있습니다. 옵션 하나를 선택하면 제안된 역할 목록이 미리 채워지며, 이 역할들은 나중에 바꿀 수 있습니다.

* **Datasource roles:** 입력 데이터소스에 `Editor` 또는 `Owner` 역할을 가진 모든 사용자와 사용자 그룹을 추가합니다.
* **Ontology admins and datasource roles:** [데이터소스 파생 권한](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#type-specific-edit-permissions)에 따라 현재 해당 온톨로지 리소스를 수정할 수 있는 모든 사용자를 추가합니다. 이 사용자들은 `Ontology Administrators` 사용자 그룹에 속하며 입력 데이터소스에 Editor 또는 Owner 역할을 가지고 있습니다.

아래 이미지는 마이그레이션 마법사의 역할 제안을 보여 줍니다.

![리소스 하나를 마이그레이션할 때의 역할 제안.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-migrating-one-resource-roles-suggestions.png)

원하는 역할 제안을 선택하고, 제안된 [온톨로지 역할](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#ontology-roles)과 객체 타입의 기본 역할을 검토한 뒤 필요하면 수정합니다. 다음으로 요약을 확인하고, 영향을 확인한 뒤, 마이그레이션을 완료해 역할을 적용합니다.

아래 이미지는 마이그레이션 마법사에서 역할을 할당하는 방법을 보여 줍니다.

![리소스 하나를 마이그레이션할 때의 역할 할당.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-migrating-one-resource-assign-roles.png)

**설명**: 두 제안 옵션은 "마이그레이션 전과 후에 편집 가능한 사람이 최대한 같도록" 초기값을 채워 주는 기능입니다. 예를 들어 `aircraft` 데이터셋에 Editor인 사용자가 `alice`와 `ops-team` 그룹이라면, Datasource roles를 고르면 이 둘이 역할 목록에 미리 들어갑니다. 이후 필요에 따라 목록을 고쳐서 확정합니다.

<a id="exceptions"></a>
##### 예외 (Exceptions)

다음과 같은 경우 액션 타입을 역할로 마이그레이션하려는 시도가 막힐 수 있습니다.

* 액션 타입에 현재 사용자의 권한을 확인하는 제출 조건이 없는 경우.
  * 해결 방법: Ontology Manager에서 액션 타입의 **Security & Submission criteria** 탭(**Submission criteria** 섹션)에 현재 사용자 기반 조건을 추가하고, 온톨로지에 저장한 뒤 마이그레이션을 다시 시도합니다.
* 액션 타입이 함수로 뒷받침되며, 마이그레이션 전에 `@edits decorators`와 함께 다시 게시해야 하는 경우.
  * 해결 방법: [데코레이터](../../02_define-ontologies/04_functions/12_typescript-v1/02_decorators.md#decorators) 문서의 단계를 참조하세요.

이 문제들이 해결되면 액션 타입을 역할로 마이그레이션할 수 있습니다.

<a id="what-if-some-ontology-resources-are-no-longer-needed"></a>
#### 더 이상 필요 없는 온톨로지 리소스가 있는 경우 (What if some ontology resources are no longer needed)

조치가 필요한 온톨로지 리소스가 더 이상 필요 없다면 [Ontology cleanup tool](08_cleanup.md)로 해당 리소스를 삭제할 수 있습니다. 이 도구는 여러 기준(예: 데이터소스가 휴지통에 있는지, 지원 중단(deprecation) 날짜가 지났는지, 인덱스가 실패하고 있는지, 온톨로지 역할을 사용하는지 등)에 따라 어떤 객체 타입을 안전하게 삭제할 수 있는지 파악하도록 도와줍니다.

<a id="migrating-function-backed-action-types"></a>
#### 함수 기반 액션 타입 마이그레이션 (Migrating function-backed action types)

함수 기반 액션 타입은 뒷받침하는 함수를 먼저 마이그레이션해야 합니다. Foundry는 함수를 자동으로 마이그레이션하려고 시도하며, 그러면 액션 타입도 마이그레이션할 수 있습니다. 하지만 일부 함수는 자동으로 마이그레이션되지 않아 함수 안에서 편집되는 객체 타입을 직접 선언해야 할 수 있습니다. 액션 타입을 온톨로지 역할로 마이그레이션한 뒤 함수 기반 액션에서 실패가 발생하면 [FAQ](#how-can-i-resolve-a-function-backed-action-that-is-failing-post-migration) 섹션을 확인하세요.

> **중간 요약**: 마이그레이션은 Advanced 메뉴의 마법사로 최대 500개씩 일괄 처리하거나, 리소스별로 Security 탭에서 하나씩 처리합니다. 되돌릴 수 없으며, 사용자 확인 제출 조건이 없거나 편집 대상 선언이 없는 함수 기반 액션 타입은 먼저 고쳐야 합니다.

<a id="migration-frequently-asked-questions"></a>
### 마이그레이션 자주 묻는 질문 (Migration frequently asked questions)

<a id="will-there-be-any-changes-in-object-aware-applications"></a>
#### 객체 인식 애플리케이션에 변경이 생기나요? (Will there be any changes in object-aware applications?)

사용자는 이전에 입력 데이터소스에 `Viewer` 접근 권한이 없어서 볼 수 없었던 객체 타입과 링크 타입의 메타데이터에 [Ontology Manager](01_overview.md)에서 접근하게 될 수 있습니다. 그렇다고 입력 데이터소스의 데이터에 접근하게 되는 것은 아닙니다. 데이터 접근은 항상 해당 데이터소스의 역할로 관리됩니다. 정확히 어떤 메타데이터를 볼 수 있는지는 사용자의 [온톨로지 역할](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#ontology-roles)로 결정됩니다.

객체 타입이 마이그레이션되면 Object Explorer도 Object View 편집에 대한 권한 검사를 바꿉니다. 객체 타입이 마이그레이션되기 전에는 Object View를 편집하려면 사용자가 `Object View Administrators` 그룹에 속하고 입력 데이터소스에 `Editor` 접근 권한이 있어야 합니다. 객체 타입이 마이그레이션된 뒤에는 Object Explorer가 사용자가 객체 타입 자체에 `Ontology Editor` 권한을 가지고 있는지만 확인합니다.

<a id="how-can-i-resolve-a-function-backed-action-that-is-failing-post-migration"></a>
#### 마이그레이션 후 실패하는 함수 기반 액션은 어떻게 해결하나요? (How can I resolve a function-backed action that is failing post migration?)

Ontology Edit Function이 편집하는 객체 타입을 Foundry가 자동으로 감지하지 못하면, 액션을 제출한 뒤 다음 오류와 함께 실패합니다.

![Functions 출처(provenance) 오류.](https://www.palantir.com/docs/resources/foundry/ontology-manager/functions-provenance-error.png)

이 오류를 해결하려면 [함수 문서](../../02_define-ontologies/04_functions/09_language-agnostic-features/01_edits-overview.md)에 설명된 단계를 따르세요.

> **중간 요약**: 마이그레이션 후에는 데이터 권한이 없는 사용자도 메타데이터를 볼 수 있게 될 수 있고, Object View 편집 권한은 객체 타입의 `Ontology Editor` 여부로만 판단합니다. 함수 기반 액션 실패는 함수에 편집 대상 객체 타입을 선언해 해결합니다.

## 정리

- 온톨로지 역할은 데이터소스 파생 권한을 대체한 레거시 모델이며, 현재는 Compass 파일 시스템 기반 권한이 최신 방식입니다.
- 핵심은 리소스 메타데이터 권한(역할로 직접 부여)과 객체 데이터 권한(데이터소스 권한 유지)의 분리입니다.
- 마이그레이션은 리소스 유형별 사전 권한이 필요하고, 일괄(최대 500개) 또는 하나씩 진행하며, 되돌릴 수 없습니다.
- 사용자 확인 제출 조건이 없거나 편집 대상 선언이 없는 함수 기반 액션 타입은 먼저 고쳐야 마이그레이션할 수 있습니다.
- 마이그레이션 후 메타데이터 가시성과 Object View 편집 권한 검사 방식이 바뀝니다.
