# Object View 브랜치 작업 (Branching object views)

- 원문: https://www.palantir.com/docs/foundry/object-views/branching-object-views/
- 사이드바 위치: Applications > Object Views > Branching object views

이 페이지는 Object View 구성을 Global Branching의 브랜치 위에서 개발하는 방법을 다룹니다. 브랜치에 어떤 리소스가 올라가는지, 다른 애플리케이션과 어떻게 함께 동작하는지, `main`으로 병합하기 전에 통과해야 하는 검사와 승인, 리베이스와 충돌 해결, 알려진 제한 사항을 설명합니다. 많은 사람이 쓰는 화면을 운영 상태에 영향 없이 고치려면 브랜치 기반 변경 관리가 필요합니다.

<a id="overview"></a>
## 개요 (Overview)

Object Views는 Global Branching과 통합되어, Object View 구성을 안전하고 격리된 환경에서 개발할 수 있게 해 줍니다. 이 문서는 브랜치에서 Object View를 다루는 방법을 설명하며, 리소스 추가와 수정, 애플리케이션 간 호환성, 병합 요구 사항, 리베이스, 알려진 제한 사항을 포함합니다.

Global Branching의 일반적인 개념과 워크플로는 [Global Branching 문서](https://www.palantir.com/docs/foundry/global-branching/overview/)를 참고하세요.

**설명**: 브랜치(branch)는 Git의 브랜치와 같은 개념입니다. `main`은 실제 사용자가 보는 운영 상태이고, 브랜치는 `main`에서 갈라져 나온 별도의 작업 공간입니다. 브랜치에서 한 변경은 병합(merge)하기 전까지 `main`에 영향을 주지 않습니다. Global Branching은 Foundry에서 객체 타입, 액션 타입, Workshop 모듈, Object View 같은 여러 종류의 리소스를 하나의 브랜치에서 함께 변경하고 함께 병합할 수 있게 해 주는 기능입니다.

<a id="adding-removing-and-modifying-resources"></a>
## 리소스 추가, 제거, 수정 (Adding, removing, and modifying resources)

Object View를 브랜치에 추가하려면 브랜치 위에 있는 상태에서 [Object View 편집기](06_full-object-views/02_config-object-views.md#use-the-object-view-editor)로 Object View 버전을 저장합니다.

Object View는 브랜치와 호환되는 두 종류의 리소스를 지원합니다.

* **OV 관리 모듈(OV-managed modules):** 브랜치에서 Object View에 가한 Workshop 콘텐츠 변경을 담습니다. 전체 Object View의 각 탭, 객체 인스턴스 패널(object instance panel), 객체 집합 패널(object set panel)마다 OV 관리 모듈이 따로 만들어집니다. Workshop 애플리케이션에서 쓸 수 있는 모든 브랜치 인식 기능을 Object View 안에서도 쓸 수 있습니다.
* **전체 Object View 탭(Full object view tabs):** Object View 탭의 구조적 변경을 담습니다. 탭 추가, 삭제, 이름 변경, 프로필 변경, 표시 조건(visibility condition) 수정이 여기에 해당합니다.

아래 예시는 `Museum` 객체 타입에 대해 브랜치에 올라간 여러 리소스를 보여 줍니다. 위에서부터 차례로 전체 Object View 탭 리소스, `Museum` 객체 타입 자체, 전체 Object View의 **Museum History** 탭, 그리고 [패널 Object View](07_panel-object-views/02_config-panel-views.md#object-instance-panels)입니다.

![브랜치 작업 표시줄에 표시된 Museum 객체 타입의 여러 브랜치 리소스 스크린숏.](https://www.palantir.com/docs/resources/foundry/object-views/object-view-branch-resources.png)

브랜치 작업 표시줄(branch taskbar)을 사용하면 어떤 Object View 리소스든 브랜치에서 개별적으로 제거할 수 있습니다. 전체 Object View 탭 리소스를 제거하면 그에 딸린 모든 탭이 브랜치에서 자동으로 제거됩니다.

![브랜치 작업 표시줄에서 Object View 브랜치 리소스를 제거하는 옵션을 보여 주는 스크린숏.](https://www.palantir.com/docs/resources/foundry/object-views/removing-object-view-branch-resource.png)

**설명**: 두 리소스의 차이는 "무엇이 바뀌었는가"입니다. 탭 목록 자체(어떤 탭이 몇 개 있고 이름이 무엇이며 언제 보이는가)는 전체 Object View 탭 리소스 하나에 기록되고, 각 탭 안에 배치된 위젯과 레이아웃은 탭마다 하나씩 있는 OV 관리 모듈에 기록됩니다. 예를 들어 탭 3개짜리 Object View에서 탭 하나의 이름만 바꾸면 탭 리소스만 바뀌고, 둘째 탭의 표 위젯을 고치면 그 탭의 모듈만 바뀝니다.

> **중간 요약**: 브랜치에서 Object View 버전을 저장하면 리소스가 브랜치에 올라갑니다. 리소스는 탭 안의 콘텐츠를 담는 OV 관리 모듈과 탭 구조를 담는 전체 Object View 탭 리소스 두 종류이며, 브랜치 작업 표시줄에서 개별 제거할 수 있습니다.

<a id="cross-application-compatibility"></a>
## 애플리케이션 간 호환성 (Cross-application compatibility)

Object View는 브랜치에 있는 온톨로지의 최신 상태를 기준으로 편집할 수 있으며, 브랜치에서 새로 만든 객체 타입과 액션 타입도 여기에 포함됩니다. Object View 위젯을 사용하면 브랜치의 Object View를 독립형 Workshop 애플리케이션 안에 삽입할 수도 있습니다. 브랜치의 Object View는 Ontology Manager의 **Object views** 탭에서 미리 볼 수 있습니다.

> **중간 요약**: 브랜치에서는 그 브랜치에만 있는 객체 타입과 액션 타입까지 반영해 Object View를 편집할 수 있고, Workshop 위젯 삽입과 Ontology Manager 미리 보기도 브랜치 기준으로 동작합니다.

<a id="merge-requirements"></a>
## 병합 요구 사항 (Merge requirements)

<a id="deployability-checks"></a>
### 배포 가능성 검사 (Deployability checks)

브랜치의 Object View를 `main`으로 배포하기 전에 다음 배포 가능성 검사를 통과해야 합니다.

* **사용자에게 게시 권한이 있음(User has publish permissions):** [Object View 편집 권한](04_config-overview.md#permissions)이 필요합니다. 이는 `main`에서 새 Object View 버전을 게시할 때 하는 권한 검사와 같습니다.

* **Object View가 main과 리베이스되어 있어야 함(Object view must be rebased with main):** 병합하기 전에 브랜치의 각 Object View 리소스를 `main`의 최신 변경 사항으로 리베이스합니다.

* **레거시 필드가 수정되지 않음(No Legacy fields modified):** 새 Object View 편집기가 지원하지 않는 기능이 브랜치에서 수정되지 않았는지 확인합니다. 이 검사는 항상 통과해야 합니다. 실패하면 Palantir Support에 문의하세요.

**설명**: 리베이스(rebase)는 내 브랜치가 갈라져 나온 뒤 `main`에 쌓인 변경을 먼저 받아들이고, 그 위에 내 변경을 다시 얹는 작업입니다. 이렇게 하면 병합 시점에 내 브랜치가 `main`의 최신 상태를 모두 포함하므로, 다른 사람이 그사이 `main`에 반영한 변경을 실수로 덮어쓰지 않게 됩니다.

<a id="approvals-checks"></a>
### 승인 검사 (Approvals checks)

Object View는 [승인(approvals)](https://www.palantir.com/docs/foundry/global-branching/resource-protection-and-approval-policies/)을 사용해, 브랜치에서 변경한 사용자가 그 변경을 병합하는 데 필요한 권한을 가졌는지 판단합니다. 구체적으로 필요한 권한은 Object View가 연결된 객체 타입의 [권한 모델](../../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)에 따라 다릅니다.

<a id="object-type-uses-datasource-derived-permissions"></a>
#### 객체 타입이 데이터소스 파생 권한을 사용하는 경우 (Object type uses datasource-derived permissions)

객체 타입이 [데이터소스 파생 권한(datasource-derived permissions)](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#datasource-derived-permissions)을 사용하는 경우, 기여자(contributor) 또는 승인하는 검토자(reviewer)는 다음을 가져야 합니다.

* 객체 타입에 대한 `View` 접근 권한과, 객체 타입의 백킹 데이터소스(backing datasource) **전부에** 대한 `Editor` 접근 권한.
* [Control Panel](https://www.palantir.com/docs/foundry/administration/enrollments-and-organizations-permissions/)의 `Object View Admin` 애플리케이션 권한. 이 권한은 Object Explorer에서 Object View를 게시하는 데 필요하며, `main`에서 [새 Object View 버전을 게시](04_config-overview.md#permissions)할 때 필요한 애플리케이션 권한과 같습니다.

**주의**: 병합 시점에는 데이터소스 권한이 더 엄격합니다(Datasource permissions are stricter at merge time). 위의 데이터소스 권한 요구 사항은 브랜치 밖에서 쓰는 일반적인 편집 권한 검사보다 엄격합니다. `main`에서 Object View를 편집할 때는 객체 타입의 백킹 데이터소스 중 **하나라도** `Editor` 역할이 있으면 됩니다. 하지만 브랜치의 변경을 병합하려면 **모든** 백킹 데이터소스에 대해 `Editor` 역할이 있어야 합니다.

**설명**: 예를 들어 Museum 객체 타입이 `museums_raw`와 `museums_enriched` 두 데이터셋을 백킹 데이터소스로 쓴다고 합시다. `museums_raw`에만 `Editor` 역할이 있는 사용자는 `main`에서 Object View를 편집할 수는 있지만, 브랜치 변경을 병합하려면 두 데이터셋 모두에 `Editor` 역할이 있거나, 그런 권한을 가진 검토자의 승인을 받아야 합니다.

<a id="object-type-uses-ontology-roles-or-project-based-permissions"></a>
#### 객체 타입이 온톨로지 역할 또는 프로젝트 기반 권한을 사용하는 경우 (Object type uses ontology roles or project-based permissions)

객체 타입이 [온톨로지 역할(ontology roles)](../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md#ontology-roles) 또는 [프로젝트 기반 권한](../../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)을 사용하는 경우, 기여자 또는 승인하는 검토자는 객체 타입에 대한 편집 권한만 있으면 됩니다. 이 권한은 보통 온톨로지 역할에서는 `Ontology Editor` 역할로, 프로젝트 기반 권한에서는 `Editor` 프로젝트 역할로 부여됩니다. 객체 타입에 대한 편집 권한에는 Object Explorer에서 Object View를 게시하는 권한이 이미 포함되므로 별도의 `Object View Admin` 애플리케이션 권한은 필요하지 않습니다.

<a id="inherited-project-approval-policies"></a>
#### 상속된 프로젝트 승인 정책 (Inherited project approval policies)

Object View와, Object View의 탭과 패널을 이루는 Workshop 모듈은 상위 객체 타입의 논리적 하위 리소스입니다. 객체 타입이 [보호(protected)](https://www.palantir.com/docs/foundry/global-branching/resource-protection-and-approval-policies/#resource-protection)되어 있고 [프로젝트 승인 정책(project approval policy)](https://www.palantir.com/docs/foundry/global-branching/resource-protection-and-approval-policies/#project-approval-policies)이 있는 프로젝트에 속해 있다면, 그 정책은 Object View와 그 모듈에도 적용됩니다. 제안(proposal)을 병합하려면 두 리소스에 대한 승인 요청이 모두 정책을 만족해야 합니다.

**주의**: 상위 객체 타입에서 상속되는 보호(Inherited protection from the parent object type). 상속된 리소스 보호 기능은 개발 중이며 곧 출시될 예정입니다. 이 기능이 제공되면, 상위 객체 타입이 보호되어 있을 때 Object View나 그 모듈을 `main`에서 직접 편집하는 것이 막힙니다. 그 전까지는 상위 객체 타입이 보호되어 있더라도 Object View와 그 탭과 패널을 이루는 모듈을 `main`에서 직접 편집할 수 있습니다.

**설명**: "보호된(protected)" 리소스는 `main`에서 직접 수정할 수 없고 반드시 브랜치와 제안(proposal, Git의 풀 리퀘스트에 해당)을 거쳐 승인을 받아야 병합되는 리소스입니다. 현재는 Object View가 이 보호를 상위 객체 타입에서 물려받지 못하므로, 객체 타입이 보호되어 있어도 Object View는 `main`에서 바로 고칠 수 있는 상태입니다.

> **중간 요약**: 병합하려면 게시 권한, `main` 기준 리베이스, 레거시 필드 미수정이라는 배포 가능성 검사를 통과해야 합니다. 승인에 필요한 권한은 객체 타입의 권한 모델에 따라 다르며, 데이터소스 파생 권한에서는 모든 백킹 데이터소스의 `Editor` 역할이 필요합니다. 보호된 객체 타입의 프로젝트 승인 정책은 Object View에도 적용되지만, `main` 직접 편집 차단은 아직 제공되지 않습니다.

<a id="rebasing-and-conflict-resolution"></a>
## 리베이스와 충돌 해결 (Rebasing and conflict resolution)

브랜치의 각 Object View 리소스는 배포하기 전에 `main`과 리베이스해야 합니다. Object View 모듈 리소스는 [Workshop 리베이스](https://www.palantir.com/docs/foundry/workshop/branching-integration/#rebasing-and-conflict-resolution)로 리베이스할 수 있습니다. [전체 Object View 탭 리소스](06_full-object-views/01_use-full-views-in-platform.md)에 있는 탭 구성 변경은 탭 콘텐츠 변경과 별도로 리베이스해야 합니다. 전체 Object View에 리베이스가 필요하면 [Object View 편집기](06_full-object-views/02_config-object-views.md#edit-object-view-tabs)의 Object View 섹션 아래에 알림 메시지가 나타납니다.

Object View 리베이스 대화 상자에는 세 개의 열이 표시됩니다.

* main 브랜치 상태
* 내 브랜치 상태
* 제안된 리베이스 결과

`main`과 내 브랜치 사이에서 충돌하지 않는 변경은 자동으로 수락되어 결과에 포함됩니다. 충돌이 있으면, 영향을 받는 탭마다 `main`의 버전을 유지할지 내 브랜치의 버전을 유지할지 골라야 합니다. 결과 열은 리베이스 후의 최종 상태를 미리 보여 줍니다. 리베이스를 완료하기 전에 자동 수락된 변경을 수정할 수도 있습니다.

아래는 Object View 리베이스 대화 상자의 예시입니다. 이 예시에서는 충돌하지 않는 두 변경이 자동 수락되었습니다. 그리고 `Louvre` 탭에 대한 두 편집 사이에서 충돌이 감지되었습니다.

![Object View 리베이스 대화 상자 예시.](https://www.palantir.com/docs/resources/foundry/object-views/object-view-rebase-example.png)

충돌을 해결하려면 브랜치 버전이나 `main` 버전 중 하나를 고릅니다. 그러면 리베이스가 성공적으로 진행됩니다. 충돌한 행을 펼치면 표시(visibility) 세부 정보를 볼 수 있습니다.

![Object View 리베이스 대화 상자에서 충돌을 해결하는 예시.](https://www.palantir.com/docs/resources/foundry/object-views/object-view-rebase-conflict-resolution.png)

**설명**: 충돌(conflict)은 같은 대상을 양쪽에서 서로 다르게 바꿨을 때 생깁니다. 예를 들어 `main`에서는 `Louvre` 탭 이름을 "Louvre Museum"으로, 내 브랜치에서는 "Musée du Louvre"로 바꿨다면 시스템이 어느 쪽을 택할지 스스로 정할 수 없습니다. 반면 `main`에서는 탭 A를 추가하고 내 브랜치에서는 탭 B를 삭제했다면 서로 다른 대상이므로 둘 다 자동으로 반영됩니다. Object View 리베이스는 줄 단위가 아니라 탭 단위로 어느 쪽을 쓸지 고르는 방식입니다.

> **중간 요약**: 모듈 리소스는 Workshop 리베이스로, 탭 구성 리소스는 별도의 Object View 리베이스 대화 상자로 리베이스합니다. 대화 상자는 main, 내 브랜치, 결과의 세 열을 보여 주며, 충돌이 없는 변경은 자동 수락되고 충돌이 있는 탭은 어느 쪽 버전을 쓸지 직접 고릅니다.

<a id="known-limitations"></a>
## 알려진 제한 사항 (Known limitations)

[레거시 Object View 탭](08_legacy-object-views/01_config-legacy-object-views.md)은 브랜치에서 편집할 수 없습니다.

## 정리

- Object View는 Global Branching과 통합되어 브랜치에서 격리된 상태로 개발할 수 있습니다.
- 브랜치 리소스는 탭별 Workshop 콘텐츠를 담는 OV 관리 모듈과 탭 구조를 담는 전체 Object View 탭 리소스 두 종류입니다.
- `main`으로 병합하려면 게시 권한, 리베이스, 레거시 필드 미수정 검사를 통과하고, 객체 타입 권한 모델에 맞는 승인을 받아야 합니다.
- 데이터소스 파생 권한을 쓰는 객체 타입은 병합 시 모든 백킹 데이터소스에 대한 `Editor` 역할이 필요해 평소보다 엄격합니다.
- 리베이스 대화 상자에서 충돌하는 탭마다 `main`과 브랜치 중 하나를 골라 해결하며, 레거시 Object View 탭은 브랜치에서 편집할 수 없습니다.
