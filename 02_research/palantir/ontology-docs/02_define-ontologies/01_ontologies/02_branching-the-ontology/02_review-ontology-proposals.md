# 온톨로지 제안 검토하기 (Review ontology proposals)

- 원문: https://www.palantir.com/docs/foundry/ontologies/review-ontology-proposals/
- 사이드바 위치: Define Ontologies > Ontologies > Branching the ontology > Review ontology proposals

브랜치에서 만든 온톨로지(Ontology) 변경은 제안(proposal)을 통해 검토와 승인을 받은 뒤 `main`에 반영됩니다. 이 페이지는 Ontology Manager에서 제안 목록을 찾고, 제안 하나의 개요, 미리보기 상태, 변경 검토, 변경 이력 탭을 사용하는 방법과, 제안을 보고 승인하고 병합하는 데 필요한 권한을 설명합니다.

온톨로지 제안은 버전 관리 시스템의 Pull Request에 해당합니다. 제안은 별도 브랜치에서 만든 변경이 `main`에 통합되기 전에 이를 검토하고 승인하는 메커니즘 역할을 합니다.

글로벌 브랜치의 경우, 온톨로지 제안은 [Global Branching 제안](https://www.palantir.com/docs/foundry/global-branching/core-concepts/#create-and-prepare-a-proposal)이 만들어질 때 자동으로 생성되며, `main`으로 병합되는 변경에 대한 검토, 이름, 설명 같은 메타데이터를 담습니다. 레거시 온톨로지 브랜치의 경우에는 브랜치가 만들어질 때 온톨로지 제안이 생성됩니다.

이 페이지에서는 리소스 상태 확인, 작업(task) 검토, 브랜치에서 이루어진 변경 보기를 포함해 온톨로지 제안을 검토하는 방법을 설명합니다.

**설명**: Pull Request(PR)는 GitHub 같은 Git 호스팅 서비스에서 "내 브랜치의 커밋을 `main`에 합쳐 달라"고 요청하고, 동료가 변경 내용을 보며 댓글을 달고 승인하는 절차입니다. 온톨로지 제안도 같은 구조로, 변경 대상이 소스 코드 파일이 아니라 객체 타입, 링크 타입, 액션 타입 같은 온톨로지 리소스라는 점만 다릅니다. "레거시 온톨로지 브랜치"는 Global Branching이 도입되기 전부터 있던 온톨로지 전용 브랜치 방식을 가리킵니다.

<a id="proposals-tab"></a>
## 제안 탭 (Proposals tab)

측면 탭에서 **Proposals** 페이지로 이동하면 모든 온톨로지 제안을 볼 수 있습니다. 제안은 다음 탭으로 분류됩니다.

* **My proposals:** 내가 작성한 제안입니다.
* **Assigned to me:** 내가 검토자로 지정된 제안입니다.
* **In review:** 진행 중이거나 승인된 제안입니다.
* **Merged proposals:** `Main` 온톨로지에 병합된 제안입니다.
* **Closed proposals:** 병합되지 않고 종료된 제안입니다.

![Ontology Manager의 My proposals 개요 페이지.](https://www.palantir.com/docs/resources/foundry/ontologies/ontology-proposals-page.png)

> **중간 요약**: Proposals 페이지에서 모든 온톨로지 제안을 내 제안, 나에게 할당된 제안, 검토 중, 병합됨, 종료됨으로 나누어 볼 수 있습니다.

<a id="proposal-view"></a>
## 제안 화면 (Proposal view)

**Proposal overview**(제안 개요), **Preview status**(미리보기 상태), **Review changes**(변경 사항 검토), **Changelog**(변경 이력) 탭에서 개별 제안에 대한 더 많은 정보를 볼 수 있습니다.

<a id="proposal-overview-page"></a>
### 제안 개요 페이지 (Proposal overview page)

글로벌 브랜치에 있는 상태에서 개별 제안에 접근하려면, 브랜치 작업 표시줄(branch taskbar)에서 아무 온톨로지 리소스나 선택하고 **View ontology proposal**(온톨로지 제안 보기)을 선택합니다. `Main`에 있다면 **Proposals** 탭으로 이동해 보려는 제안을 선택합니다. 온톨로지 브랜치에 있다면 상단 탐색 표시줄에서 **Open proposal details**(제안 세부 정보 열기)를 선택해 제안에 바로 접근합니다.

제안 안에서는 더 많은 정보를 볼 수 있는 **Proposal overview**, **Preview status**, **Review changes**, **Changelog** 탭이 보입니다.

제안 개요 페이지는 제안의 단계, 변경 사항, 검토가 필요한 작업, 선택된 검토자를 한곳에 모아 보여 줍니다.

* **브랜치의 변경 사항 보기:** 편집 내용은 개요 페이지 하단에 표시됩니다. 편집 내용은 작성자별, 그리고 작업별로 분류되며, 작업 하나는 온톨로지 리소스 하나에 대응합니다. 변경을 보거나, 해당 리소스로 이동하거나, 브랜치에서 변경을 제거할 수 있습니다. 변경 이력은 **Changelog** 탭에서도 볼 수 있으며, 여기에는 변경이 이루어진 정확한 시각도 표시됩니다.
* **검토자 보기 및 추가:** 특정 동료를 지정해 내 제안을 검토하게 할 수 있습니다.
* **주의가 필요한 작업 보기:** 이 섹션에는 검토(Review) 단계에서 거절된 모든 작업이 표시됩니다.
* **Share** 옵션을 사용해 제안 링크를 복사할 수 있습니다.

![특정 글로벌 브랜치의 제안 개요.](https://www.palantir.com/docs/resources/foundry/ontologies/ontology-proposal-overview.png)

<a id="preview-status"></a>
### 미리보기 상태 (Preview status)

**Preview status** 탭은 내 브랜치에서 어떤 객체 타입이 인덱싱되었는지, 인덱싱이 진행 중인지, 인덱싱될 수 없는지를 보여 줍니다. 객체 타입이 인덱싱되면 미리보기가 가능한 상태가 되며, 이는 그 데이터를 내 브랜치에서 보고 테스트할 수 있다는 뜻입니다.

![미리보기 상태 탭.](https://www.palantir.com/docs/resources/foundry/ontologies/ontology-proposal-preview-status-tab.png)

**설명**: 객체 타입의 정의(스키마)만 바꾼 상태에서는 아직 그 정의에 맞는 객체 데이터가 만들어지지 않았습니다. 인덱싱(indexing)은 백킹 데이터소스의 행을 읽어 새 정의에 맞는 객체로 저장소에 적재하는 작업입니다. 예를 들어 브랜치에서 Employee 객체 타입에 `hire_date` 속성(property)을 추가했다면, 인덱싱이 끝나야 브랜치 안에서 각 Employee 객체의 `hire_date` 값을 실제로 조회해 볼 수 있습니다.

<a id="review-changes"></a>
### 변경 사항 검토 (Review changes)

**Review changes** 탭은 제안의 모든 작업을 보여 줍니다. 여기에서 다음 작업을 할 수 있습니다.

* 검토자 추가 초대
* 프로젝트로 마이그레이션된 리소스의 승인 정책 보기
* 각 작업을 개별적으로 승인 또는 거절하거나, 해당하는 모든 작업을 일괄로 승인 또는 거절
* 작업 단위로 댓글을 남기고 동료와 협업

![변경 사항 검토 페이지.](https://www.palantir.com/docs/resources/foundry/ontologies/ontology-proposal-review-changes.png)

<a id="changelog"></a>
### 변경 이력 (Changelog)

Changelog 탭은 브랜치의 변경에 대한 자세한 이력을 보여 줍니다. 작업을 펼치면 특정 사용자가 특정 시점에 한 편집(edit)을 볼 수 있습니다. 관련 온톨로지 리소스로 바로 이동할 수도 있습니다.

![변경 이력 탭.](https://www.palantir.com/docs/resources/foundry/ontologies/ontology-proposal-changelog-tab.png)

> **중간 요약**: 제안 하나는 개요(단계, 변경, 검토자, 거절된 작업), 미리보기 상태(브랜치의 객체 타입 인덱싱 여부), 변경 사항 검토(작업별 승인과 거절, 댓글), 변경 이력(누가 언제 무엇을 바꿨는지) 탭으로 구성됩니다.

<a id="proposal-permissions"></a>
## 제안 권한 (Proposal permissions)

* **제안 보기:** 제안의 제목과 설명은 해당 온톨로지에 접근할 수 있는 모든 사람이 찾아볼 수 있습니다. 제안에 포함된 일부 리소스에 대해 최소 `Viewer` 접근 권한이 있는 사용자는 그 리소스와 관련된 변경을 볼 수 있습니다.
* **온톨로지 리소스 수정:** 리소스에 대한 편집 권한이 있는 사용자는 브랜치에서 그 리소스를 편집할 수 있습니다. [프로젝트 권한](../../../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)이 아니라 [온톨로지 역할](../../../06_ontology-architecture/02_object-permissioning/03_ontology-permissions-legacy.md)을 사용하는 리소스의 경우, 뷰어(viewer)도 브랜치에서 변경을 제안할 수 있습니다.
* **제안의 작업 승인 또는 거절:** 작업이 승인되려면 기본적으로 승인자가 하위 리소스의 편집자(editor) 또는 소유자(owner)여야 합니다. 리소스가 프로젝트로 마이그레이션되어 보호되어 있다면, 대신 승인자가 프로젝트 정책에 따른 승인 권한을 가지고 있어야 합니다.
* **온톨로지 제안 병합:** 온톨로지 제안은 Global Branching 제안을 병합하는 방식으로 병합됩니다. 다만 레거시 온톨로지 브랜치의 경우, 필요한 승인을 모두 받았다면 브랜치를 볼 수 있는 사람은 누구나 제안을 병합할 수 있습니다.

**설명**: 권한은 단계별로 다르게 요구됩니다. 예를 들어 Employee 객체 타입 변경이 담긴 제안에서, Employee에 `Viewer` 권한만 있는 사용자는 변경 내용을 볼 수만 있고, `Editor` 이상이어야 승인할 수 있습니다. 단, Employee가 프로젝트 권한으로 마이그레이션되어 보호된 상태라면 기준이 바뀌어 프로젝트 정책에 지정된 승인 권한 보유자만 승인할 수 있습니다.

> **중간 요약**: 제안 내용은 리소스의 Viewer 권한으로 볼 수 있고, 승인은 기본적으로 리소스의 편집자나 소유자가, 보호된 리소스는 프로젝트 정책상 승인 권한 보유자가 합니다. 병합은 Global Branching 제안 병합으로 이루어집니다.

## 정리

- 온톨로지 제안은 온톨로지 리소스 변경을 위한 Pull Request로, Global Branching 제안을 만들 때 자동으로 생성됩니다.
- Proposals 페이지에서 제안을 내 제안, 할당된 제안, 검토 중, 병합됨, 종료됨으로 나누어 봅니다.
- 개별 제안은 개요, 미리보기 상태, 변경 사항 검토, 변경 이력 탭으로 변경 내용, 인덱싱 상태, 승인 진행 상황, 편집 이력을 보여 줍니다.
- 승인은 리소스(작업) 단위로 이루어지며, 기본적으로 편집자나 소유자, 보호된 리소스는 프로젝트 정책상의 승인 권한 보유자가 승인합니다.
