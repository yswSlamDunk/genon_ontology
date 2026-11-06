# 애플리케이션 사이드바 구성하기 (Configure the applications sidebar)

- 원문: https://www.palantir.com/docs/foundry/object-views/config-app-sidebar/
- 사이드바 위치: Applications > Object Views > Legacy Object Views > Configure the applications sidebar

이 페이지는 레거시 Object View 옆에 현재 객체와 관련된 애플리케이션, 분석, 액션, 외부 링크를 모아 보여 주는 애플리케이션 사이드바(applications sidebar)를 설정하는 방법을 설명합니다. 사이드바를 켜는 방법, 그룹과 애플리케이션 카드를 편집하는 방법, 그리고 현재 객체의 정보를 파라미터로 넘겨 다른 애플리케이션을 여는 방법을 다룹니다.

**애플리케이션 사이드바(applications sidebar)는** 현재 객체와 관련된 애플리케이션, 분석, 액션, 기타 리소스를 표시하고 삽입하는 데 사용됩니다. 애플리케이션 사이드바는 이 리소스들을 그 객체의 주요 콘텐츠와 시각적으로 구분합니다.

애플리케이션 사이드바는 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/), [Quiver](https://www.palantir.com/docs/foundry/quiver/overview/), [Slate](https://www.palantir.com/docs/foundry/slate/overview/), [액션 타입(Action types)](../../../02_define-ontologies/03_action-types/01_overview.md) 등 모든 객체 기반 애플리케이션의 삽입을 지원합니다. 사이드바에 추가하면 이 애플리케이션들을 객체의 맥락 안에서 열 수 있습니다. 사이드바는 파라미터가 포함된 URL로 다른 앱과 외부 웹사이트에 연결하는 것도 지원합니다.

아래 예시에서는 `Airport` 객체를 볼 수 있습니다. 본문 탭에는 그 객체에 대한 주요 정보가 들어 있고, 관련 애플리케이션에는 다음이 포함됩니다.

* 항공편 지연에 대한 Workshop 알림 수신함(Alert Inbox), 교통량 분류(triage)에 사용됩니다.
* 공항의 승객 수용량을 관리하는 데 쓰는 Slate 애플리케이션.
* 공항의 COVID 대응을 위한 전용 애플리케이션.

![Object View의 애플리케이션 사이드바](https://www.palantir.com/docs/resources/foundry/object-views/application-sidebar-object-view.png)

> **중간 요약**: 애플리케이션 사이드바는 현재 객체와 관련된 Workshop, Quiver, Slate 앱과 액션, 외부 링크를 본문과 구분해 모아 보여 주며, 객체의 맥락을 유지한 채 열 수 있게 합니다.

<a id="set-up-the-applications-sidebar"></a>
## 애플리케이션 사이드바 설정하기 (Set up the applications sidebar)

애플리케이션 사이드바는 Object View마다 선택적으로 켜는(opt-in) 부가 기능입니다. 사이드바에 그룹을 추가하기 전까지 사이드바는 사용자에게 보이지 않습니다. **Add new group**(새 그룹 추가) 옵션은 **Sidebar** 탭 아래에 있거나, 아래 이미지처럼 사이드바 자체를 펼치면 찾을 수 있습니다. 빌더가 애플리케이션이나 액션을 추가하고 그 버전을 게시하면 최종 사용자에게 사이드바가 표시됩니다. 사이드바에 빈 그룹만 있으면 사이드바는 표시되지 않습니다.

![Object View에 새 애플리케이션 사이드바 그룹 추가하기](https://www.palantir.com/docs/resources/foundry/object-views/add-application-sidebar-groups.png)

애플리케이션이나 액션을 추가하고 변경 사항을 게시하면 사용자에게 사이드바가 표시됩니다. 사이드바에 빈 그룹만 있으면 사이드바는 표시되지 않습니다.

<a id="edit-the-applications-sidebar"></a>
## 애플리케이션 사이드바 편집하기 (Edit the Applications Sidebar)

애플리케이션 사이드바는 모듈식이며 구성할 수 있습니다. 사이드바는 여러 그룹으로 나눌 수 있고, 각 그룹에 서로 다른 애플리케이션 카드와 액션을 둘 수 있습니다.

사이드바에는 그룹마다, 애플리케이션 카드마다 전용 구성이 있습니다. 아래 이미지에 번호로 표시된 것처럼, 옵션은 다음과 같습니다.

1. 그룹 전체를 다음 옵션으로 편집합니다.
   * (a) 그룹 제목 구성
   * (b) 그룹 안의 애플리케이션 카드와 액션 재정렬
   * (c) 그룹 전체 제거
   * (d) 표시 여부 편집(특정 사용자 프로필에만 그룹이 보이게 함)

2. 특정 애플리케이션 카드를 편집합니다. 이를 선택하면 보조 메뉴가 열리며 다음을 할 수 있습니다.
   * (A) 카드 하나에 쓰이는 애플리케이션 리소스를 추가하거나 변경(자세한 내용은 아래 참고)
   * (B) 제목 재정의(override)
   * (C) 아이콘 재정의
   * (D) 카드에 썸네일 사용. 썸네일은 Foundry에 업로드해 폴더에 저장해 두어야 합니다.
   * (E) 카드 모드(Card mode) 또는 간결 모드(Compact mode) 선택
   * (F) 파라미터 추가

3. 백킹 애플리케이션(backing application)을 편집합니다. 이를 선택하면 Workshop이나 Slate 같은 원본 앱에서 해당 모듈이 열립니다.

4. 그룹에 새 애플리케이션을 추가합니다.

5. 그룹에 새 액션을 추가합니다.

6. 새 그룹을 추가합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/configuring-applications-sidebar_applications-sidebar-config.png" alt="애플리케이션 사이드바 구성" width="500" />

> **중간 요약**: 사이드바는 그룹을 추가하고 내용을 채워 게시해야 보이며, 빈 그룹만 있으면 표시되지 않습니다. 그룹 단위(제목, 순서, 제거, 프로필별 표시)와 카드 단위(리소스, 제목, 아이콘, 썸네일, 표시 모드, 파라미터)로 편집할 수 있습니다.

<a id="addchange-an-application-in-the-sidebar"></a>
## 사이드바에 애플리케이션 추가 또는 변경하기 (Add/change an application in the sidebar)

사이드바에 애플리케이션을 추가하는 주요 방법은 두 가지입니다.

1. Object View 안에 삽입되는 객체 애플리케이션(Workshop, Quiver, Slate 등)의 경우:
   * **Add application**을 선택하고 애플리케이션(예: Workshop)을 골라 리소스 선택기를 연 다음, 삽입하려는 특정 리소스(예: Workshop 모듈)를 선택합니다.
   * Workshop과 Slate 애플리케이션의 파라미터 구성을 사용하면, 현재 객체의 속성, 링크된 객체 집합, 또는 미리 정한 값을 연결된 리소스로 전달할 수 있습니다.
   * 파라미터 값은 삽입된 Workshop 또는 Slate 애플리케이션 안에서 파라미터 이름과 같은 이름의 변수로 접근할 수 있습니다. Workshop에서는 이 변수를 변수 **Settings** 패널에서 모듈 인터페이스 변수(module interface variables)로 구성해야 합니다.

2. 새 탭에서 열 다른 Foundry 애플리케이션과 외부 웹사이트의 경우:
   * **Application link**(애플리케이션 링크)를 추가해 파라미터가 포함된 URL을 가진 새 카드를 만듭니다.
   * 사이드바의 모든 링크는 새 브라우저 탭에서 열리며, 위에서 말한 객체 애플리케이션처럼 삽입되지 않습니다.
   * 이 URL은 Foundry 애플리케이션(예: Workshop, Vertex, 다른 Object View, Foundry 문서)과 외부 웹사이트 모두에 사용할 수 있습니다.
   * URL 카드에는 주소와 파라미터 구성에서 정의한 파라미터를 조합한 템플릿이 필요합니다. URL에 파라미터를 넣으려면 파라미터 이름을 `{{parameterName}}`처럼 감쌉니다. 속성 값 자체가 URL 전체라면 **Encode property value**(속성 값 인코딩) 상자를 체크해 URL 전체임을 표시하고, URL 입력란에는 `{{parameterName}}`만 넣습니다.
   * 기본적으로 현재 객체의 세부 정보는 `{{objectId}}`와 `{{objectTypeId}}` 파라미터로 사용할 수 있습니다.

**주의**: 사용자가 삽입된 애플리케이션에 대한 권한이 없으면 그 애플리케이션을 열 수는 없지만, 애플리케이션 카드는 여전히 보입니다. 사이드바의 각 애플리케이션에 올바른 권한을 설정했는지 확인하세요.

**설명**: 파라미터 전달은 함수 호출 시 인자를 넘기는 것과 같은 구조입니다. 예를 들어 Workshop 모듈이 `airportCode`라는 모듈 인터페이스 변수를 입력으로 받도록 만들어져 있다면, 사이드바 카드에서 `airportCode` 파라미터에 현재 Airport 객체의 `code` 속성을 연결합니다. 사용자가 JFK 공항의 Object View에서 카드를 열면 모듈은 `airportCode = "JFK"`로 시작합니다. URL 카드도 같은 원리로, 템플릿이 `https://example.com/airports/{{airportCode}}`라면 JFK 객체에서는 `https://example.com/airports/JFK`가 열립니다.

> **중간 요약**: 객체 애플리케이션(Workshop, Quiver, Slate)은 **Add application**으로 삽입하고, 파라미터로 현재 객체 정보를 같은 이름의 변수로 넘깁니다. 그 밖의 앱과 외부 사이트는 **Application link**로 `{{parameterName}}` 템플릿 URL을 만들어 새 탭에서 엽니다. 권한이 없는 사용자에게도 카드는 보이므로 각 앱의 권한을 확인해야 합니다.

## 정리

- 애플리케이션 사이드바는 현재 객체와 관련된 앱, 분석, 액션, 링크를 본문과 구분해 모아 보여 주는 선택 기능입니다.
- 그룹을 추가하고 애플리케이션이나 액션을 넣어 게시해야 사용자에게 보이며, 빈 그룹만 있으면 표시되지 않습니다.
- 그룹과 카드 단위로 제목, 순서, 프로필별 표시, 아이콘, 썸네일, 표시 모드, 파라미터를 편집합니다.
- 객체 애플리케이션은 삽입하고 파라미터를 변수로 넘기며, 다른 앱과 외부 사이트는 `{{parameterName}}` 템플릿 URL로 새 탭에서 엽니다.
- 권한이 없는 사용자도 카드는 볼 수 있으므로 각 애플리케이션의 권한을 따로 설정해야 합니다.
