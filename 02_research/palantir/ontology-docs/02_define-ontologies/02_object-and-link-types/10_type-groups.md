# 객체 타입 그룹 (Object type groups)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/type-groups/
- 사이드바 위치: Define Ontologies > Object and link types > Object type groups

이 페이지는 객체 타입을 주제별로 묶어 검색과 탐색을 돕는 객체 타입 그룹(object type group)을 만들고 관리하는 방법, 그룹을 볼 수 있는 권한, 그리고 예전 태그 기반 그룹에서 지금의 그룹 기능으로 옮겨 온 과정을 설명합니다. 객체 타입이 수백 개로 늘어난 온톨로지에서는 "재무 관련 객체 타입만 보기"처럼 범주로 좁혀 찾을 수 있어야 하므로 그룹이 필요합니다.

객체 타입 그룹은 사용자가 온톨로지를 더 잘 검색하고 탐색하도록 돕는 분류용 기본 요소(primitive)입니다. 그룹은 Ontology Manager에서 만들고 관리하며, 일반적으로 온톨로지 [소유자와 편집자](10_type-groups.md#group-permissions)가 담당합니다.

**설명**: 그룹과 객체 타입은 다대다(many-to-many) 관계입니다. 예를 들어 `Employee` 객체 타입은 "HR" 그룹과 "Org chart" 그룹에 동시에 속할 수 있고, "HR" 그룹에는 `Employee`, `Leave Request`, `Payroll` 객체 타입이 함께 들어 있을 수 있습니다. 그룹은 객체 타입의 데이터나 스키마를 바꾸지 않는 분류용 표식입니다.

<a id="group-configuration"></a>
## 그룹 설정 (Group configuration)

그룹은 Ontology Manager 사이드바에서 열 수 있는 그룹 메뉴를 통해 만들고 관리합니다.

![그룹을 선택하거나 새 그룹 추가하기](https://www.palantir.com/docs/resources/foundry/object-link-types/groups-menu.png)

객체 타입 개요 페이지에서 **Edit groups**를 선택해 객체 타입에 그룹을 직접 추가할 수도 있습니다.

![객체 타입에 그룹 추가하기](https://www.palantir.com/docs/resources/foundry/object-link-types/group-add-to-object.png)

<a id="group-search-and-discovery"></a>
## 그룹 검색과 탐색 (Group search and discovery)

그룹은 [Ontology Manager의 **Search** 바와 **Search** 바 대화 상자](../../05_applications/04_ontology-manager/02_navigation.md#header-search-bar)에서 검색할 수 있습니다. Ontology Manager의 객체 타입 표는 그룹을 표시하고 그룹으로 필터링하는 기능을 지원합니다. 그룹은 [Object Explorer 홈 페이지](../../05_applications/01_object-explorer/02_getting-started.md#group-exploration-b-c-d)에도 표시됩니다.

![그룹으로 필터링](https://www.palantir.com/docs/resources/foundry/object-link-types/object-type-groups-add.png)

<a id="group-permissions"></a>
## 그룹 권한 (Group permissions)

객체 타입 그룹을 보려면 사용자는 그 객체 타입 그룹이 들어 있는 프로젝트(project)에 대한 **viewer**(보기) 권한이 있어야 합니다.

> **중간 요약**: 그룹은 Ontology Manager 사이드바의 그룹 메뉴나 객체 타입 개요 페이지의 **Edit groups**로 관리하며, Ontology Manager 검색, 객체 타입 표 필터, Object Explorer 홈 페이지에서 쓰입니다. 그룹을 보려면 그룹이 들어 있는 프로젝트의 viewer 권한이 필요합니다.

<a id="legacy-group-migration"></a>
## 레거시 그룹 마이그레이션 (Legacy group migration)

2024년 5월 22일부로, 이 페이지에서 설명하는 *그룹* 기본 요소가 태그 기반의 레거시 그룹 시스템을 대체했습니다.

대부분의 경우 레거시 그룹은 이때 객체 타입 그룹으로 자동 마이그레이션되었습니다. 수동 조치가 필요한 경우에는 Upgrade Assistant 개입(intervention)을 통해 온톨로지 소유자에게 알림이 갔습니다.

**설명**: 레거시 그룹은 [타입 클래스](09_metadata/01_metadata-typeclasses.md) 표의 `oe_home_page_object_type_group` 항목처럼, 각 객체 타입의 기본 키 속성에 그룹 이름 문자열을 태그로 붙이는 방식이었습니다. 이 방식에서는 "그룹"이라는 독립된 리소스가 없고 같은 문자열을 가진 객체 타입끼리 묶일 뿐이라, 철자가 다르면 그룹이 둘로 갈라졌습니다. 새 방식은 그룹을 별도의 리소스로 만들고 객체 타입이 그것을 참조합니다.

<a id="group-name-visibility"></a>
### 그룹 이름 가시성 (Group name visibility)

이전에는 그룹 안의 모든 객체 타입이 특정 사용자에게 보이지 않으면(예: 백킹 데이터셋의 접근 제어 때문에), 그 그룹도 그 사용자에게 보이지 않았습니다. 위의 [그룹 권한](10_type-groups.md#group-permissions) 섹션에서 말했듯이, 이제 모든 그룹은 온톨로지를 볼 수 있는 모든 사용자에게 보입니다. 이 변경은 거버넌스의 명확성과 투명성을 높이기 위해 그룹 가시성을 다른 [온톨로지 기본 요소](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#ontology-roles)와 맞춘 것입니다.

<a id="migration-of-partially-visible-groups"></a>
### 부분적으로만 보이던 그룹의 마이그레이션 (Migration of partially visible groups)

한 명 이상의 사용자에게 보이지 않던 레거시 그룹은 자동 마이그레이션 대상이 아니었습니다. 이런 경우 수동 조치가 필요하다는 사실을 Upgrade Assistant 개입을 통해 온톨로지 소유자에게 알렸습니다.

2024년 5월 22일, 안전하게 마이그레이션할 수 없었던 레거시 그룹은 Workshop과 Object Explorer 같은 모든 애플리케이션에서 운영 사용자에게 보이지 않도록 숨겨졌습니다. 하위 호환성을 위해, 레거시 그룹의 이름은 객체 타입에 [타입 클래스 메타데이터](09_metadata/01_metadata-typeclasses.md)로 계속 저장되어 있습니다.

온톨로지 소유자는 Ontology Manager를 사용해 이렇게 숨겨진 레거시 그룹을 계속 수동으로 마이그레이션할 수 있습니다. 이렇게 하려면 왼쪽 아래 구석의 **Ontology Configuration** 메뉴로 이동해 **Approve all Groups for migration**을 선택합니다.

**설명**: 부분적으로만 보이던 그룹을 자동으로 옮기지 않은 이유는 그룹 이름 자체가 정보를 드러낼 수 있기 때문입니다. 예를 들어 "Project Falcon Acquisition Targets"라는 그룹 이름은 그 안의 객체 타입을 볼 수 없는 사용자에게도 민감한 정보일 수 있습니다. 새 방식에서는 그룹이 온톨로지를 볼 수 있는 모든 사용자에게 보이므로, 이런 그룹을 공개할지는 소유자가 직접 판단하도록 수동 승인 단계를 둔 것입니다.

> **중간 요약**: 2024년 5월 22일부터 태그 기반 레거시 그룹이 지금의 그룹 기능으로 대체되었고, 대부분은 자동 마이그레이션되었습니다. 일부 사용자에게 보이지 않던 그룹은 숨겨진 채 타입 클래스 메타데이터로 남아 있으며, 소유자가 **Approve all Groups for migration**으로 수동 마이그레이션할 수 있습니다.

## 정리

- 객체 타입 그룹은 객체 타입을 분류해 검색과 탐색을 돕는 기본 요소이며, 주로 온톨로지 소유자와 편집자가 Ontology Manager에서 관리합니다.
- 그룹 메뉴나 객체 타입 개요의 **Edit groups**로 설정하고, Ontology Manager 검색과 표 필터, Object Explorer 홈 페이지에서 활용합니다.
- 그룹을 보려면 그룹이 속한 프로젝트의 viewer 권한이 필요하며, 이제 그룹은 온톨로지를 볼 수 있는 모든 사용자에게 보입니다.
- 2024년 5월 22일 태그 기반 레거시 그룹이 대체되었고, 자동으로 옮겨지지 않은 그룹은 **Ontology Configuration** 메뉴에서 수동 마이그레이션할 수 있습니다.
