# 온톨로지 브랜치 작업 (Overview)

- 원문: https://www.palantir.com/docs/foundry/ontologies/branching-ontology/
- 사이드바 위치: Define Ontologies > Ontologies > Branching the ontology > Overview

이 페이지는 운영 중인 온톨로지(Ontology)를 직접 고치지 않고, 별도 브랜치(branch)에서 변경한 뒤 검토를 거쳐 반영하는 방법을 설명합니다. 브랜치 생성, 리소스 보호(protection), 리베이스(rebase)와 충돌 해결, 제안(proposal)을 통한 검토와 병합(merge), 그리고 알려진 제약 사항을 순서대로 다룹니다. Git을 써 본 적이 있다면 브랜치, 리베이스, Pull Request 개념이 그대로 온톨로지 리소스에 적용된다고 보면 됩니다.

온톨로지는 Global Branching과 통합되어 온톨로지 리소스를 안전하고 격리된 환경에서 개발할 수 있게 해 줍니다. 이 문서는 브랜치에서 온톨로지로 작업하는 방법을 다루며, 리소스 추가 및 수정, 리베이스와 충돌 해결, 검토 및 병합 절차, 알려진 제약 사항을 포함합니다.

Global Branching의 개념과 워크플로에 대한 일반적인 정보는 [Global Branching 문서](https://www.palantir.com/docs/foundry/global-branching/overview/)를 참고하세요.

**설명**: 브랜치는 원본(`main`)에서 갈라져 나온 독립된 작업 사본입니다. 예를 들어 Employee 객체 타입에 `hire_date` 속성(property)을 추가하는 작업을 브랜치에서 하면, 작업이 끝나고 병합하기 전까지 `main`을 쓰는 다른 사용자와 애플리케이션은 그 변경을 보지 않습니다. Global Branching은 데이터 파이프라인, 온톨로지, 애플리케이션 등 Foundry의 여러 리소스를 하나의 브랜치로 함께 묶어 관리하는 Foundry 기능입니다.

<a id="definitions"></a>
## 정의 (Definitions)

브랜치, 제안(proposal), 리베이스에 대한 일반적인 정의는 [Global Branching 핵심 개념](https://www.palantir.com/docs/foundry/global-branching/core-concepts/)을 참고하세요. 아래 용어는 온톨로지 브랜치 작업에만 해당합니다.

* **온톨로지 제안(Ontology proposal):** 온톨로지 변경이 포함된 브랜치에서 [Global Branching 제안을 만들면](https://www.palantir.com/docs/foundry/global-branching/core-concepts/#create-and-prepare-a-proposal), 온톨로지 관련 변경을 추적하기 위한 온톨로지 제안이 자동으로 생성됩니다. 온톨로지 제안에는 `main`으로 병합되는 온톨로지 변경에 대한 검토, 이름, 설명 같은 메타데이터가 들어 있습니다.

> **중간 요약**: 온톨로지 브랜치 작업은 Global Branching 위에서 이루어지며, Global Branching 제안을 만들면 온톨로지 변경만 따로 추적하는 온톨로지 제안이 자동으로 생깁니다.

<a id="adding-and-modifying-resources"></a>
## 리소스 추가 및 수정 (Adding and modifying resources)

브랜치에서 온톨로지를 수정하려면 Ontology Manager에서 새 브랜치를 만들거나, 브랜치 선택기(branch selector)를 사용해 기존 브랜치에 접근하면 됩니다.

브랜치를 만들려면 브랜치 선택기를 열고 **Create new branch**(새 브랜치 만들기)를 선택합니다. 그러면 브랜치의 제목과 설명을 입력할 수 있는 대화 상자가 열립니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontologies/branch-selector.png" alt="브랜치 선택기." width="250">

이미 온톨로지에 변경 사항이 있고 이를 브랜치에 포함하고 싶다면, 저장 대화 상자에서 **Save to new branch**(새 브랜치에 저장)를 선택해 그 변경 사항을 담은 별도 브랜치를 만들 수 있습니다. [보호된 온톨로지 리소스](#resource-protection)를 변경한 경우에는 반드시 새 브랜치에 저장해야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontologies/save-to-ontology.png" alt="온톨로지에 저장 옵션." width="250">

**참고**: 브랜치는 메인 온톨로지, 즉 `main` 브랜치에서만 만들 수 있습니다.

브랜치에서 작업하는 동안에는 인터페이스 하단의 [브랜치 작업 표시줄(branch taskbar)](https://www.palantir.com/docs/foundry/global-branching/branch-taskbar/)에 현재 브랜치 이름과 추가 메타데이터가 표시됩니다.

**설명**: "`main`에서만 브랜치를 만들 수 있다"는 것은 브랜치에서 다시 브랜치를 따는 중첩 구조를 허용하지 않는다는 뜻입니다. Git에서는 `feature-a` 브랜치에서 `feature-a-sub` 브랜치를 만들 수 있지만, 온톨로지에서는 모든 브랜치가 `main`에서 직접 갈라져 나옵니다.

> **중간 요약**: Ontology Manager의 브랜치 선택기에서 새 브랜치를 만들거나, 이미 만든 변경을 저장할 때 새 브랜치로 저장할 수 있습니다. 브랜치는 `main`에서만 만들 수 있습니다.

<a id="resource-protection"></a>
## 리소스 보호 (Resource protection)

브랜치 보호를 지원하는 온톨로지 리소스 타입은 다음과 같습니다.

* 객체 타입
* 액션 타입
* 링크 타입
* 인터페이스 타입
* 공유 속성(shared property) 타입

리소스 보호가 지원되지 않는 대상은 다음과 같습니다.

* 타입 그룹(Type groups)
* 규칙 집합(Rule sets) (규칙 집합을 수정할 때는 그 규칙 집합을 포함하는 객체 타입의 보호 상태가 적용됩니다)

또한 온톨로지 리소스는 보호하기 전에 프로젝트 권한을 사용하도록 마이그레이션되어 있어야 합니다. 자세한 내용은 [온톨로지 권한](../../../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)을 참고하세요.

온톨로지 리소스를 프로젝트 권한을 사용하도록 마이그레이션한 뒤에는, 상위 프로젝트의 **Files** 탭에서 그 리소스의 보호 상태를 확인하고 관리할 수 있습니다.

![온톨로지 리소스 보호하기.](https://www.palantir.com/docs/resources/foundry/ontologies/protect-from-compass.png)

보호가 활성화되면 반드시 별도 브랜치에서 변경하고, 제안을 만들어 메인 브랜치로 병합해야 합니다.

보호 상태는 Ontology Manager의 **Overview** 탭에서도 볼 수 있습니다.

![Ontology Manager 개요 페이지에 표시된 보호된 온톨로지 리소스.](https://www.palantir.com/docs/resources/foundry/ontologies/ontology-overview-tab.png)

적용되는 정책은 **Security** 탭에서도 확인할 수 있습니다.

![Ontology Manager의 Security 탭에 표시된 보호된 온톨로지 리소스.](https://www.palantir.com/docs/resources/foundry/ontologies/ontology-security-tab.png)

보호된 리소스를 수정하면 **Save** 대화 상자가 **Create and save to branch**(브랜치를 만들고 저장)로 바뀌어, 변경 사항을 반드시 새 브랜치에 저장하도록 요구합니다.

![Ontology Manager의 새 브랜치에 저장 옵션.](https://www.palantir.com/docs/resources/foundry/ontologies/modify-protected-object.png)

**설명**: 보호(protection)는 GitHub의 보호 브랜치(protected branch) 규칙과 같은 목적의 기능입니다. 보호된 객체 타입은 `main`에서 바로 저장할 수 없고, 반드시 브랜치에서 변경한 뒤 제안을 통해 승인을 받아야 `main`에 반영됩니다. 예를 들어 여러 애플리케이션이 의존하는 Customer 객체 타입을 보호해 두면, 누군가 실수로 속성을 지우는 변경이 검토 없이 운영에 반영되는 일을 막을 수 있습니다. "프로젝트 권한으로 마이그레이션"이란 해당 리소스의 권한을 온톨로지 자체의 역할 체계가 아니라 그 리소스가 들어 있는 Foundry 프로젝트의 권한으로 관리하도록 전환하는 것을 말합니다.

> **중간 요약**: 객체 타입, 액션 타입, 링크 타입, 인터페이스 타입, 공유 속성 타입은 보호할 수 있으며, 그러려면 먼저 프로젝트 권한으로 마이그레이션해야 합니다. 보호된 리소스는 브랜치와 제안을 거쳐서만 변경할 수 있습니다.

<a id="rebasing-and-conflict-resolution"></a>
## 리베이스와 충돌 해결 (Rebasing and conflict resolution)

내가 브랜치에서 변경을 진행하는 동안, `main`도 다른 사람들로부터 새로운 변경을 받을 수 있습니다. 리베이스는 `main`의 최신 변경을 현재 브랜치에 반영해 현재 브랜치를 최신 상태로 유지하는 작업입니다.

**참고**: 자동 리베이스(Automatic rebasing). 글로벌 브랜치에 온톨로지 변경이 없으면 리베이스는 자동으로 이루어집니다. 객체 타입 인덱싱을 포함해 브랜치에 온톨로지 변경을 도입하고 나면, 브랜치를 `main`과 최신 상태로 맞추기 위해 직접 리베이스해야 합니다.

**설명**: 예를 들어 월요일에 `main`에서 브랜치를 만들어 Employee 객체 타입의 설명을 고치고 있는데, 화요일에 다른 사람이 `main`에서 Department 객체 타입에 새 속성을 추가했다고 합시다. 리베이스를 하면 내 브랜치의 기준점이 화요일의 `main`으로 옮겨져, 내 변경과 Department의 새 속성이 함께 있는 상태가 됩니다. 인덱싱(indexing)은 백킹 데이터소스의 데이터를 객체로 조회할 수 있도록 저장소에 적재하는 작업인데, 이것도 온톨로지 변경으로 취급된다는 점에 주의해야 합니다.

<a id="rebase-a-branch"></a>
### 브랜치 리베이스하기 (Rebase a branch)

`main`에 새 변경이 있으면, 사이드바의 **Main branch updates** 탭에 파란색 표시가 나타나 이 변경을 검토하도록 알려 줍니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontologies/main-branch-updates.png" width="300" alt="Main branch updates." />

**Main branch updates** 페이지로 이동하면 마지막 리베이스 이후(처음으로 직접 리베이스하는 경우에는 브랜치 생성 이후) 들어온 변경을 볼 수 있습니다. **Rebase branch**를 선택하면 브랜치가 최신 버전의 `main`으로 갱신됩니다.

![브랜치 리베이스 화면.](https://www.palantir.com/docs/resources/foundry/ontologies/rebase-branch-view.png)

충돌이나 오류가 없으면 리베이스가 자동으로 완료되고 브랜치가 최신 상태가 됩니다.

<a id="resolve-merge-conflicts"></a>
### 병합 충돌 해결하기 (Resolve merge conflicts)

충돌이 있으면 리베이스는 진행 중 상태로 남고, 브랜치와 `main` 사이의 충돌하는 변경을 해결할 수 있도록 **Conflicts tab**(충돌 탭)으로 이동합니다. 충돌 없이 오류만 있는 경우에는 **Errors tab**(오류 탭)으로 이동합니다.

리베이스 중에는 `main`의 변경이 브랜치에 불러와지고, 현재 브랜치에 이전에 저장한 변경은 작업 상태(working state)로 다시 불러와집니다. 이는 **All changes** 탭에서 확인할 수 있습니다.

이 상태에서는 `main`과 내 브랜치 양쪽의 변경을 모두 보고 접근할 수 있습니다. 어떤 온톨로지 리소스에 양쪽 브랜치의 변경이 모두 있으면, 기본적으로 내 브랜치의 버전이 표시됩니다.

![리베이스 변경 사항 검토.](https://www.palantir.com/docs/resources/foundry/ontologies/review-rebase-changes.png)

충돌을 해결하려면 각 리소스마다 **Use Main branch changes**(Main 브랜치 변경 사용) 또는 **Keep current branch changes**(현재 브랜치 변경 유지)를 선택할 수 있습니다. 또는 해당 리소스로 직접 이동해 **사용자 지정 변경(custom changes)을** 적용해 충돌을 해결할 수도 있습니다.

이 예에서 `Palantir employee` 객체 타입에는 `main` 브랜치와 내 브랜치 양쪽에서 표시 이름(display name)이 변경된 충돌이 있습니다. 이 충돌을 해결하려면 이 객체 타입의 어느 버전을 유지할지 선택합니다.

![객체 타입 리베이스 변경 사항 검토.](https://www.palantir.com/docs/resources/foundry/ontologies/review-object-type-rebase-changes.png)

사용자 지정 변경으로 이 충돌을 해결할 수도 있습니다. 이 예에서는 객체 타입으로 이동해 표시 이름을 "Palantir employee"에서 "Current employee"로 바꿀 수 있습니다. 그러면 이 사용자 지정 변경으로 인해 충돌이 해결됩니다.

![Current employee 예시.](https://www.palantir.com/docs/resources/foundry/ontologies/current-employee-example.png)

![Current employee 예시의 충돌.](https://www.palantir.com/docs/resources/foundry/ontologies/current-employee-example-conflicts.png)

모든 충돌을 해결한 뒤, 리베이스를 마치기 전에 오류도 모두 처리했는지 확인하세요.

**설명**: 충돌(conflict)은 같은 리소스의 같은 부분을 양쪽에서 서로 다르게 바꿨을 때 생깁니다. 위 예에서는 `main`이 표시 이름을 A로, 내 브랜치가 B로 바꿨기 때문에 시스템이 어느 쪽을 택할지 스스로 정할 수 없습니다. 해결 방법은 세 가지입니다. `main` 쪽 값을 택하기, 내 브랜치 값을 택하기, 또는 둘 다 아닌 새 값(예: "Current employee")을 직접 입력하기입니다.

<a id="finish-rebase"></a>
### 리베이스 마치기 (Finish rebase)

모든 오류와 충돌이 해결되면 **Finish rebase and save**(리베이스 마치고 저장)를 선택할 수 있으며, 그러면 브랜치가 최신 상태가 됩니다.

![리베이스 마치고 저장 옵션.](https://www.palantir.com/docs/resources/foundry/ontologies/finish-rebase-and-save.png)

브랜치에서 계속 작업하면서 정기적으로 리베이스해 브랜치를 `main` 브랜치의 최신 버전과 맞춰 둘 수 있습니다.

![브랜치가 최신 상태임.](https://www.palantir.com/docs/resources/foundry/ontologies/branch-is-up-to-date.png)

> **중간 요약**: 온톨로지 변경이 있는 브랜치는 직접 리베이스해야 합니다. 충돌이 생기면 리소스별로 `main` 변경, 내 브랜치 변경, 또는 직접 입력한 새 값 중 하나로 해결하고, 오류까지 모두 처리한 뒤 리베이스를 마칩니다.

<a id="merge-requirements"></a>
## 병합 요건 (Merge requirements)

<a id="prepare-your-branch-for-review"></a>
### 검토를 위한 브랜치 준비 (Prepare your branch for review)

변경을 마치고 브랜치를 `main`에 병합할 준비가 되면, 브랜치 작업 표시줄에서 **Create proposal**(제안 만들기) 아이콘을 선택해 제안을 만듭니다. 이름과 설명을 추가해 제안을 설정합니다.

![작업 표시줄에서 제안 만들기.](https://www.palantir.com/docs/resources/foundry/ontologies/create-proposal-taskbar.png)

![대화 상자에서 제안 만들기.](https://www.palantir.com/docs/resources/foundry/ontologies/create-proposal-dialog.png)

제안이 만들어지면 글로벌 브랜치의 리소스가 `main` 브랜치에 병합될 수 있는지 확인하는 **병합 검사(merge checks)가** 실행됩니다. 실패하는 검사에는 브랜치와 `main` 브랜치 사이의 충돌이 포함될 수 있으며, 이 경우 브랜치를 리베이스해야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontologies/branch-taskbar-review-button.png" alt="병합 검사가 표시된 작업 표시줄 팝오버." width="450">

<a id="request-a-review"></a>
### 검토 요청하기 (Request a review)

브랜치 작업 표시줄, Global Branching 제안 페이지, 또는 온톨로지 제안 페이지에서 제안에 검토자를 추가할 수 있습니다.

온톨로지 제안 페이지에서는 **Review changes**(변경 사항 검토)로 이동해 **Invite reviewers**(검토자 초대)를 선택하면 제안에 검토자를 추가할 수 있습니다. 프로젝트로 마이그레이션된 온톨로지 리소스의 경우, **View policies**(정책 보기)를 선택하면 관련 프로젝트 정책에 따라 어떤 검토자가 해당 리소스를 반드시 검토해야 하는지 확인할 수 있습니다.

각 온톨로지 리소스는 개별 작업(task)으로 간주됩니다. 리소스 이름 옆의 상태 태그는 전체 승인 상태를 나타내며, 오른쪽의 **Your review**(내 검토) 섹션에서 검토를 제출할 수 있습니다.

Global Branching에서는 온톨로지 엔터티가 별개의 리소스로 취급되지만, 이들은 하나의 로컬 온톨로지 제안 아래에 묶입니다. 따라서 한 온톨로지 리소스에 검토자를 추가하면 사실상 모든 온톨로지 리소스에 그 검토자가 추가됩니다.

![온톨로지 제안의 변경 사항 검토.](https://www.palantir.com/docs/resources/foundry/ontologies/ontology-proposal-review-tab.png)

제안된 변경에 대한 맥락을 제공하기 위해 제안 안의 여러 작업에 댓글을 남길 수도 있습니다. 맨 오른쪽의 **Comments** 사이드바를 선택하면 작업의 **Comments** 섹션에 접근할 수 있습니다.

**설명**: 하나의 제안 안에서 승인은 리소스(작업) 단위로 따로 이루어집니다. 예를 들어 한 브랜치에서 Employee 객체 타입과 "직원 부서 이동" 액션 타입을 함께 고쳤다면, 제안에는 작업이 2개 생기고 각 작업이 따로 승인 또는 거절됩니다. 반면 검토자 목록은 온톨로지 제안 전체에 하나로 공유됩니다.

<a id="review-the-proposal"></a>
### 제안 검토하기 (Review the proposal)

**Review changes** 탭에서 검토자는 개별 작업을 승인하거나 거절할 수 있습니다. 권한이 없는 사용자도 예를 들어 변경에 대한 의견을 전달하기 위해 작업을 검토할 수는 있지만, 이는 작업의 승인 상태에 영향을 주지 않습니다.

**주의**: 승인 권한(Approval rights). 승인 권한이 있는 사용자는 검토자로 추가되지 않았더라도 제안을 승인할 수 있습니다. 검토자 목록은 누가 변경을 검토해야 하는지 추적하는 용도로 사용하고, 승인을 제한하는 용도로 사용하지 마세요.

온톨로지 제안에서 검토자는 제안의 세부 정보를 보고, 수정된 모든 리소스 또는 특정 온톨로지 리소스에 대한 변경을 승인하거나 거절할 수 있습니다.

![온톨로지 변경 승인.](https://www.palantir.com/docs/resources/foundry/ontologies/review-protected-object.png)

정책 요건이 충족되면 승인된 리소스는 `In Progress`에서 `Approved`로 바뀝니다. 그런 다음 다른 모든 검사를 통과했다면 제안을 병합할 수 있습니다.

<a id="merge-your-branch"></a>
### 브랜치 병합하기 (Merge your branch)

변경을 `main`에 병합할 준비가 되면 Global Branching 제안을 병합해야 합니다. 그러면 온톨로지에 대한 병합 절차가 자동으로 시작됩니다.

![Global Branching 페이지의 브랜치 병합 옵션.](https://www.palantir.com/docs/resources/foundry/ontologies/test-changes-foundry-branching-merge-branch.png)

이를 위해 브랜치 작업 표시줄에서 병합 아이콘을 선택하거나, Global Branching의 제안 페이지로 이동해 **Merge proposal**(제안 병합)을 선택합니다.

> **중간 요약**: 브랜치 작업 표시줄에서 제안을 만들면 병합 검사가 실행됩니다. 검토자는 리소스(작업) 단위로 승인 또는 거절하고, 정책 요건이 충족되어 모든 검사를 통과하면 Global Branching 제안을 병합해 온톨로지 변경을 `main`에 반영합니다.

<a id="known-limitations"></a>
## 알려진 제약 사항 (Known limitations)

* **데이터소스 삭제:** `main` 브랜치에서 백킹 데이터소스(backing datasource)가 교체되거나 제거된 객체 타입에 충돌이 생긴 경우, 내 브랜치의 변경을 유지하도록 선택하면 병합이 실패합니다. 이 경우 `main` 브랜치의 변경을 선택하세요.
* **조건부 서식 삭제:** `main` 브랜치에서 조건부 서식(conditional formatting) 규칙 집합이 교체되거나 제거된 속성 타입에 충돌이 생긴 경우, 내 브랜치의 변경을 유지하도록 선택하면 병합이 실패합니다. 이 경우 `main` 브랜치의 변경을 선택하세요.
* **Pipeline Builder 객체 타입:** Pipeline Builder에서 만든 객체 타입은 브랜치의 Ontology Manager에서 수정할 수 없습니다.
* **인덱싱도 수정으로 간주됨:** 객체 타입 인덱싱은 수정으로 취급됩니다. 리소스가 프로젝트 정책으로 보호되어 있다면 브랜치를 병합하는 데 정책 승인이 필요합니다. 이 요건을 피하려면 병합 전에 인덱싱 변경을 제거하세요.
* **검토자는 모든 온톨로지 리소스에 적용됨:** 온톨로지 변경은 하나로 묶이므로, 한 온톨로지 리소스에 검토자를 추가하면 제안 전체에 추가됩니다. 특정 리소스를 반드시 승인해야 하는 사람은 그 리소스의 프로젝트 정책에 포함된 사용자뿐입니다.

> **중간 요약**: `main`에서 백킹 데이터소스나 조건부 서식 규칙 집합이 바뀐 리소스의 충돌은 `main` 쪽을 택해야 하고, Pipeline Builder로 만든 객체 타입은 브랜치에서 수정할 수 없으며, 인덱싱도 수정으로 취급되어 승인이 필요할 수 있습니다.

## 정리

- 온톨로지는 Global Branching과 통합되어 `main`에서 만든 브랜치에서 격리된 상태로 변경할 수 있습니다.
- 객체 타입, 액션 타입, 링크 타입, 인터페이스 타입, 공유 속성 타입은 프로젝트 권한으로 마이그레이션한 뒤 보호할 수 있고, 보호된 리소스는 브랜치와 제안을 통해서만 변경됩니다.
- 온톨로지 변경이 있는 브랜치는 직접 리베이스하며, 충돌은 리소스별로 `main` 변경, 내 브랜치 변경, 사용자 지정 변경 중 하나로 해결합니다.
- 제안을 만들면 병합 검사가 실행되고, 리소스별 승인을 받은 뒤 Global Branching 제안을 병합하면 온톨로지 병합이 자동으로 진행됩니다.
- 데이터소스나 조건부 서식 삭제 충돌, Pipeline Builder 객체 타입, 인덱싱 등에는 알려진 제약이 있습니다.
