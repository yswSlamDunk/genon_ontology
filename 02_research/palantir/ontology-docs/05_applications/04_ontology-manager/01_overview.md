# Ontology Manager 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/ontology-manager/overview/
- 사이드바 위치: Applications > Ontology Manager > Overview

이 페이지는 온톨로지(Ontology)를 만들고 유지보수하는 Foundry 애플리케이션인 Ontology Manager를 소개합니다. 애플리케이션에 들어가는 방법과, 이후 문서 곳곳에서 언급되는 화면 구성 요소(탐색 영역, Discover 뷰, 객체 타입 뷰, 속성 편집기, 링크 타입 뷰, 액션 타입 뷰, 함수 타입 뷰)를 차례로 설명합니다.

**Ontology Manager**(Ontology Management Application, 줄여서 OMA라고도 부름)는 조직의 온톨로지를 구축하고 유지보수할 수 있게 해 줍니다. Ontology Manager는 새 객체 타입을 만들고 새 액션 타입을 정의하는 일부터, 데이터를 온톨로지에 연결하고, 사용자 애플리케이션에서 데이터가 갱신되고 있는지 조사하는 일까지, 온톨로지와 관련된 폭넓은 작업에 사용할 수 있습니다.

**설명**: 온톨로지의 구성 요소(객체 타입, 속성, 링크 타입, 액션 타입 등)는 데이터베이스로 치면 스키마에 해당합니다. Ontology Manager는 이 스키마를 정의하고 수정하는 관리 도구로, DBMS의 관리 콘솔에서 테이블과 열, 외래 키를 정의하는 역할을 합니다. 실제 객체를 조회하고 다루는 일은 Object Explorer, Workshop 같은 다른 애플리케이션이 담당합니다.

<a id="accessing-the-application"></a>
## 애플리케이션 접근하기 (Accessing the application)

다음 세 가지 방법 중 하나로 애플리케이션에 접근할 수 있습니다.

* Workspace 사이드바의 **Apps** 섹션에서 **Ontology Manager** 아이콘을 선택합니다.
* Data Lineage에서 객체 타입을 마우스 오른쪽 버튼으로 클릭하고 **Configure object type**을 선택합니다.
* Foundry 홈 페이지 URL 끝에 `/workspace/ontology`를 붙입니다(예: `https://example.website.com/workspace/ontology`).

> **중간 요약**: Ontology Manager는 온톨로지를 만들고 관리하는 애플리케이션이며, Workspace 사이드바, Data Lineage의 오른쪽 클릭 메뉴, `/workspace/ontology` URL로 접근합니다.

<a id="user-interface"></a>
## 사용자 인터페이스 (User interface)

Ontology Manager 인터페이스는 다음 요소들로 나뉘며, 문서 전반에서 이 이름으로 언급됩니다.

* [Ontology Manager 탐색 영역](#ontology-manager-navigation)
* [Discover 뷰](#discover)
* [객체 타입 뷰](#object-type-view)
* [속성 편집기 뷰](#property-editor-view)
* [링크 타입 뷰](#link-type-view)
* [액션 타입 뷰](#action-type-view)
* [함수 타입 뷰](#function-type-view)

<a id="ontology-manager-navigation"></a>
### Ontology Manager 탐색 영역 (Ontology Manager navigation)

Ontology Manager에서 항상 표시되는 두 요소는 상단 바와 사이드바입니다. 상단 바와 사이드바는 탐색 요소로서, 애플리케이션 안의 다양한 기능과 섹션에 직관적으로 접근할 수 있게 해 줍니다.

상단 바에는 세 가지 주요 기능이 있습니다. 사용자는 상단 바에서 온톨로지 리소스를 검색하고, 새 온톨로지 리소스를 만들고, 브랜치 사이를 이동하거나 새 브랜치를 만들 수 있습니다.

사이드바는 Ontology Manager 안의 여러 리소스, 페이지, 애플리케이션으로 쉽게 이동할 수 있게 해 줍니다.

![주석이 달린 Ontology Manager 화면.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-navigation-annotated.png)

**설명**: 브랜치는 Git의 브랜치처럼 본 온톨로지와 분리된 작업 공간에서 변경을 만들고, 검토를 거쳐 나중에 합치는 방식의 변경 관리 단위입니다. 여러 사람이 동시에 온톨로지를 고칠 때 서로의 미완성 변경이 운영 중인 애플리케이션에 바로 영향을 주지 않게 하려는 목적입니다.

<a id="discover"></a>
### Discover

Discover 뷰는 사용자의 선호에 맞게 폭넓게 맞춤 설정할 수 있는 첫 화면(landing page)을 제공합니다. 기본적으로 Discover 뷰에는 즐겨찾는 객체 타입, 최근에 본 객체 타입, 즐겨찾는 그룹이 표시됩니다.

![Ontology Manager Discover 뷰.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-discover-view.png)

사용자가 해당 온톨로지를 처음 사용하는 경우에는 특별한 섹션 두 개가 표시됩니다. 하나는 그 온톨로지에서 최근에 수정된 모든 객체 타입을 보여 주고, 다른 하나는 주요(prominent) 객체 타입 전체를 보여 줍니다.

![Ontology Manager 대체(fallback) 섹션.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-fallback-sections.png)

Discover 뷰에서는 페이지에 나타날 섹션을 설정하고 섹션마다 표시할 항목 수를 조절할 수 있습니다. 사용할 수 있는 섹션에는 "Recently viewed object types"(최근 본 객체 타입), "Favorite object types"(즐겨찾는 객체 타입), "Favorite groups"(즐겨찾는 그룹)가 있습니다. 또한 특정 그룹에 대한 별도 섹션을 추가해 그 그룹 안의 모든 객체 타입을 둘러볼 수도 있습니다.

![Ontology Manager 홈페이지 맞춤 설정 기능.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-customize-homepage.png)

![Ontology Manager 그룹 섹션.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-type-group-section.png)

> **중간 요약**: 상단 바(검색, 새 리소스 생성, 브랜치)와 사이드바가 항상 표시되는 탐색 요소입니다. Discover 뷰는 즐겨찾기, 최근 본 항목, 그룹 섹션으로 구성되는 맞춤형 첫 화면이며, 처음 쓰는 사용자에게는 최근 수정된 객체 타입과 주요 객체 타입이 표시됩니다.

<a id="object-type-view"></a>
### 객체 타입 뷰 (Object type view)

객체 타입을 선택하면 객체 타입 뷰가 열리며, 다음 구성 요소로 이루어집니다.

* 페이지를 선택하는 사이드바(아래 이미지의 왼쪽)
* 선택한 페이지(아래 이미지의 오른쪽)

![객체 타입 뷰.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-object-type-view.png)

객체 타입의 **Overview** 페이지에는 아래 이미지에 번호로 표시된 다음 섹션들이 있습니다.

1. 객체 타입 메타데이터
2. 속성(Properties)
3. 액션 타입(Action types)
4. 링크 타입 그래프(Link type graph)
5. 종속 항목(Dependents)
6. 데이터(Data)
7. 사용량(Usage)

![객체 타입 Overview 페이지.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-overview-annotated.png)

**설명**: 종속 항목(Dependents)은 이 객체 타입을 사용하는 다른 리소스(예: 이 타입을 화면에 띄우는 Workshop 모듈, 이 타입을 다루는 액션 타입이나 함수)를 뜻합니다. 데이터베이스에서 어떤 테이블을 참조하는 뷰나 저장 프로시저 목록을 확인하는 것과 같은 목적으로, 객체 타입을 바꾸기 전에 영향 범위를 볼 수 있습니다.

<a id="property-editor-view"></a>
### 속성 편집기 뷰 (Property editor view)

객체 타입 **Overview** 페이지의 **Properties** 섹션에서 속성을 선택하면 애플리케이션의 속성 편집기 뷰가 열립니다.

![속성 편집기 인터페이스.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-property-editor-v2.png)

<a id="link-type-view"></a>
### 링크 타입 뷰 (Link type view)

객체 타입 **Overview** 탭의 링크 타입 그래프(아래 이미지 참고)에서 링크 타입을 선택하면 링크 타입 뷰(**Overview**와 **Datasources** 페이지 포함)가 열립니다.

![링크 타입 뷰.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-link-type.png)

> **중간 요약**: 객체 타입 뷰는 페이지 선택 사이드바와 선택한 페이지로 구성되며, **Overview** 페이지에는 메타데이터, 속성, 액션 타입, 링크 타입 그래프, 종속 항목, 데이터, 사용량 섹션이 있습니다. 여기서 속성을 고르면 속성 편집기가, 링크 타입을 고르면 링크 타입 뷰가 열립니다.

<a id="action-type-view"></a>
### 액션 타입 뷰 (Action type view)

객체 타입 **Overview** 탭의 액션 타입 섹션에서 액션 타입을 선택하면 액션 타입 뷰가 열리며, 여기서 **Overview**, **Logic**, **Observability** 페이지로 이동할 수 있습니다.

![액션 타입 뷰.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-action-type.png)

<a id="view-action-metrics-and-monitoring-rules"></a>
#### 액션 지표와 모니터링 규칙 보기 (View action metrics and monitoring rules)

**Observability** 탭에는 지난 30일 동안의 거의 실시간 [액션 사용량](../../02_define-ontologies/03_action-types/25_action-metrics.md)과 함께, 해당 액션에 정의된 [모니터링 규칙](https://www.palantir.com/docs/foundry/monitoring-views/overview/)과 그 상태가 표시됩니다. 액션 모니터링 규칙의 상세 설정 옵션은 [액션 규칙 살펴보기](https://www.palantir.com/docs/foundry/monitoring-views/rules-reference/#action-rules)를 참고하세요.

![액션 Observability 탭 화면.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-action-type-observability-tab.png)

**설명**: 모니터링 규칙은 "지난 1시간 동안 이 액션의 실패 횟수가 10회를 넘으면 알림" 같은 조건을 정해 두고, 조건이 충족되면 담당자에게 알리는 설정입니다. Observability(관측 가능성)는 운영 중인 기능이 얼마나 호출되고 얼마나 실패하는지 지표로 확인할 수 있는 상태를 뜻합니다.

<a id="function-type-view"></a>
### 함수 타입 뷰 (Function type view)

객체 타입 **Overview** 탭의 함수 타입 섹션에서 함수 타입을 선택하면 함수 타입 뷰가 열리며, 여기서 **Overview**, **Configuration**, **Observability** 페이지로 이동할 수 있습니다.

<a id="usage-history-of-a-function"></a>
#### 함수의 사용 이력 (Usage history of a function)

Usage History 패널은 함수(function)의 어떤 버전이든 사용한 애플리케이션을 각 버전 정보와 함께 기록합니다. 이 패널에서 해당 애플리케이션으로 이동해 함수 버전을 업그레이드할 수 있습니다.

<a id="view-previous-versions-of-a-function"></a>
#### 함수의 이전 버전 보기 (View previous versions of a function)

기본적으로 함수의 최신 버전이 표시됩니다. 다른 버전을 보려면 왼쪽 패널에 있는 버전 드롭다운 선택기를 사용하세요.

<a id="navigate-to-the-functions-code-repository"></a>
#### Functions Code Repository로 이동하기 (Navigate to the Functions Code Repository)

함수 수정은 Functions Code Repository 안에서만 할 수 있습니다. 저장소로 이동하려면 엔터티 뷰 오른쪽 위 모서리에 있는 **Open in Code Repository** 버튼을 사용하세요.

![함수 타입 뷰.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-function-type.png)

**설명**: 함수는 코드 저장소에서 작성하고 버전을 붙여 배포하며, 각 애플리케이션은 특정 버전을 골라 사용합니다. 라이브러리 의존성을 `mylib==1.2.0`처럼 버전으로 고정해 두는 것과 같은 방식이어서, 새 버전을 배포해도 애플리케이션 쪽에서 버전을 올리기 전까지는 예전 버전이 계속 쓰입니다. Usage History 패널은 어느 애플리케이션이 어느 버전에 머물러 있는지 보여 줍니다.

<a id="view-function-metrics-and-monitoring-rules"></a>
#### 함수 지표와 모니터링 규칙 보기 (View function metrics and monitoring rules)

**Observability** 탭에는 지난 30일 동안의 거의 실시간 [함수 사용량](../../02_define-ontologies/04_functions/08_function-consumption/02_function-metrics.md)과 함께, 해당 함수에 정의된 [모니터링 규칙](https://www.palantir.com/docs/foundry/monitoring-views/overview/)과 그 상태가 표시됩니다. 함수 모니터링 규칙의 상세 설정 옵션은 [함수 규칙 살펴보기](https://www.palantir.com/docs/foundry/monitoring-views/rules-reference/#function-rules)를 참고하세요.

![함수 Observability 탭 화면.](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-function-type-observability-tab.png)

> **중간 요약**: 액션 타입 뷰는 **Overview**, **Logic**, **Observability** 페이지를, 함수 타입 뷰는 **Overview**, **Configuration**, **Observability** 페이지를 제공합니다. **Observability** 탭에서 30일 사용량과 모니터링 규칙을 보고, 함수는 사용 이력과 버전을 확인하되 수정은 Functions Code Repository에서만 합니다.

## 정리

- Ontology Manager(OMA)는 객체 타입과 액션 타입 정의, 데이터 연결, 데이터 갱신 조사 등 온톨로지 구축과 유지보수를 위한 애플리케이션입니다.
- Workspace 사이드바, Data Lineage, `/workspace/ontology` URL로 접근합니다.
- 상단 바(검색, 리소스 생성, 브랜치)와 사이드바가 탐색을 담당하고, Discover 뷰가 맞춤형 첫 화면을 제공합니다.
- 객체 타입 뷰의 **Overview** 페이지에서 속성 편집기, 링크 타입 뷰, 액션 타입 뷰, 함수 타입 뷰로 이어집니다.
- 액션과 함수는 **Observability** 탭에서 30일 사용량과 모니터링 규칙을 확인하며, 함수 코드는 Functions Code Repository에서만 수정합니다.
