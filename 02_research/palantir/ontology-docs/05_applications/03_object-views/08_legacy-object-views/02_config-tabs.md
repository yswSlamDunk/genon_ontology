# 탭 구성하기 (Configure tabs)

- 원문: https://www.palantir.com/docs/foundry/object-views/config-tabs/
- 사이드바 위치: Applications > Object Views > Legacy Object Views > Configure tabs

이 페이지는 Object View 안에서 내용을 나누고 탐색하는 기본 단위인 탭(tab)을 다룹니다. 탭의 종류, 탭을 추가하고 삭제하고 옮기는 방법, 그리고 특정 조건에서만 탭이 보이게 하는 표시 설정과 제목, 콘텐츠 유형, 레이아웃, 교차 필터링 같은 탭 설정을 설명합니다.

**탭(tab)은** Object View 안에서 내용을 탐색하고 묶는 주된 수단입니다. 각 탭에는 Workshop 모듈이 들어 있으며, 조건부 표시(conditional visibility), 필터링 설정, 레이아웃 설정 같은 사용자 정의 옵션이 있습니다.

Object View에 추가할 수 있는 탭은 관리형 Workshop(Managed Workshop) 모듈과 독립형 Workshop(Standalone Workshop) 모듈의 두 종류입니다.

* **관리형 Workshop 모듈(Managed Workshop modules):** Object View 안에 새 탭을 만들 때는 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/) 사용을 권장합니다. 이 옵션을 쓰면 Foundry의 애플리케이션 구축 기능을 최대한 활용하는 더 정교한 뷰를 개발할 수 있습니다. [Workshop 기반 탭에 대해 더 알아보세요.](../06_full-object-views/02_config-object-views.md) 관리형 모듈은 권한이 Object View와 자동으로 동기화되며, 재사용할 수 없습니다.
* **기존 Workshop 모듈(Existing Workshop modules):** Workshop에서 이미 만들어 둔 모듈을 Object View 탭에 직접 삽입할 수 있습니다. 같은 모듈을 여러 Object View에서 사용할 수 있습니다.

일부 탭은 **Legacy** 빌더로 만들어졌습니다. 이 빌더로는 레이아웃, 위젯, 데이터 옵션의 유연성이 제한된 단순한 탭을 만들 수 있었습니다. 이 빌더로 새 탭을 추가하는 것은 더 이상 불가능하지만, 기존 탭은 계속 지원됩니다.

**설명**: 두 Workshop 탭의 차이는 소유 관계입니다. 관리형 모듈은 Object View에 소속된 모듈이라 권한도 객체 타입을 따라가고, 다른 곳에서 가져다 쓸 수 없습니다. 기존(독립형) 모듈은 Workshop에 따로 존재하는 모듈을 참조로 끼워 넣는 것이라 여러 Object View가 하나의 모듈을 공유할 수 있지만, 권한은 그 모듈 자체의 설정을 따릅니다.

> **중간 요약**: 탭은 Object View의 탐색 단위이며, 권한이 자동 동기화되고 재사용할 수 없는 관리형 Workshop 모듈과 여러 곳에서 재사용할 수 있는 기존 Workshop 모듈 두 종류가 있습니다. 레거시 빌더 탭은 새로 만들 수 없지만 기존 탭은 지원됩니다.

<a id="manage-tabs"></a>
## 탭 관리하기 (Manage Tabs)

<a id="add-a-new-tab"></a>
### 새 탭 추가하기 (Add a new tab)

편집기 안의 두 곳에서 탭을 추가할 수 있습니다. 하나는 Object View 편집기 사이드바의 **Tabs** 섹션이고, 다른 하나는 Object View 미리 보기 자체의 탭 목록에 있는 **Add tab** 버튼입니다. 어느 쪽을 쓰든 원하는 탭 유형을 선택할 수 있습니다.

![Object View에 새 탭 추가하기](https://www.palantir.com/docs/resources/foundry/object-views/add-new-tab.png)

<a id="delete-a-tab"></a>
### 탭 삭제하기 (Delete a tab)

Object View 편집기 사이드바의 탭 목록에서 탭을 삭제할 수 있습니다. 또는 편집기 사이드바에서 탭을 클릭해 들어간 뒤 **Advanced**로 이동해 **Delete tab**을 클릭해도 됩니다.

![편집기 사이드바에서 Object View 탭 삭제하기](https://www.palantir.com/docs/resources/foundry/object-views/delete-tab-in-editor-sidebar.png)
![Advanced 설정에서 Object View 탭 삭제하기](https://www.palantir.com/docs/resources/foundry/object-views/delete-tab-in-advanced-settings.png)

<a id="move-a-tab"></a>
### 탭 옮기기 (Move a tab)

Object View 편집기 사이드바의 탭 목록에서 탭을 옮깁니다. 위 또는 아래 화살표를 클릭하면 Object View 미리 보기에서 탭 순서가 바뀝니다.

![Object View 편집기 사이드바에서 탭 옮기기](https://www.palantir.com/docs/resources/foundry/object-views/move-tabs.png)

> **중간 요약**: 탭은 편집기 사이드바의 **Tabs** 섹션이나 미리 보기의 **Add tab** 버튼으로 추가하고, 사이드바 목록이나 **Advanced > Delete tab**으로 삭제하며, 사이드바 목록의 위아래 화살표로 순서를 바꿉니다.

<a id="configure-tab-settings"></a>
## 탭 설정 구성하기 (Configure tab settings)

<a id="tab-visibility"></a>
### 탭 표시 여부 (Tab visibility)

탭은 여러 방법으로 보는 사용자에게 조건부로 표시될 수 있습니다. 한 가지 방법은 구성된 Object View와 [프로필(profiles)](04_config-profiles.md)을 사용하는 것입니다. 그 밖에 다음 두 가지 요인에 따라 탭이 조건부로 보이도록 구성할 수도 있습니다.

* **속성 값(Property values):** 현재 보고 있는 객체의 속성 값이 주어진 값과 같거나 같지 않으면 이 조건이 충족됩니다. 속성 값 조건은 특정 속성 값이 기대한 값과 일치하는 객체에만 관련 있는 내용을 탭이 보여 줄 때 유용합니다.
  * 예를 들어 Airport 객체에, 특정 지역의 공항에만 해당하는 *Regional View*(지역 뷰) 탭을 추가하고 싶을 수 있습니다. 다른 지역에 대해서는 조건부 표시가 설정된 또 다른 *Regional View* 탭을 둘 수 있습니다. 각 탭은 서로 다른 시각 요소를 가질 수 있습니다.
* **링크 표시 여부(Link visibility):** 탭을 보는 사용자가, 현재 보고 있는 객체가 링크될 수 있는 객체 타입을 볼 권한이 있으면 이 조건이 충족됩니다. 링크 표시 조건은 탭이 객체의 링크를 바탕으로 내용을 보여 주는데, 보는 사용자가 그 링크 반대편의 객체를 볼 권한이 없을 수도 있을 때 유용합니다.

다음은 이 조건들이 어떻게 보이는지에 대한 예시입니다.

![속성 값과 링크 표시 여부로 탭 표시 구성하기](https://www.palantir.com/docs/resources/foundry/object-views/tab-visibility.png)

**설명**: 속성 값 조건은 SQL의 `WHERE region = 'EU'` 같은 조건을 탭 단위로 거는 것입니다. Airport 객체의 `region` 속성이 `EU`이면 "Regional View (EU)" 탭이 보이고, `APAC`이면 그 탭은 숨겨지고 "Regional View (APAC)" 탭이 보이는 식입니다. 링크 표시 조건은 권한 검사입니다. 예를 들어 Airport와 링크된 Security Incident 객체 타입을 볼 권한이 없는 사용자에게는 보안 사건 목록 탭 자체를 숨겨, 비어 있거나 오류가 나는 탭을 보여 주지 않게 합니다.

<a id="tab-settings"></a>
### 탭 설정 (Tab settings)

그 밖에 구성할 수 있는 일반 탭 설정은 다음과 같습니다.

* **Title**(제목): 제목 설정은 Object View 안의 탭 목록에 표시되는 레이블을 제어합니다. 탭 제목은 짧고 내용을 잘 설명해야 합니다.
* **Content type**(콘텐츠 유형): 관련이 있는 경우, 이 구성을 사용해 탭 안에 나타날 링크 타입이나 링크를 지정할 수 있습니다. *Link* 옵션을 선택하면 Object View의 탭 제목 옆에 배지가 표시되며, 이 배지는 현재 보고 있는 객체에 링크된 객체가 몇 개인지 보여 줍니다.
* **Content layout**(콘텐츠 레이아웃): 모든 레거시 탭은 2열 위젯 목록 레이아웃을 지원하며, 이 레이아웃은 위젯이 특정 열에 정렬되어야 한다고 지정할 때 활성화됩니다. 이 구성 옵션으로 탭 수준의 열들을 같은 너비로 할지, 서로 다른 크기로 할지 제어합니다.
* **Cross-section filtering**(섹션 간 필터링): 이 설정을 켜면 이 탭 안의 위젯들이 위젯과의 상호작용으로 제어되는 필터를 내보내고(publish) 받아 쓸(consume) 수 있습니다. 예를 들어 차트에서 항목 하나를 선택하면 다른 모든 차트가 관련 데이터만 보여 주도록 필터링하고 싶을 수 있습니다. 필터 집합(filter set)의 ID를 사용자 정의한 뒤 다른 탭에서도 같은 ID를 사용하면, 여러 탭에 걸쳐 필터를 받아 쓰고 유지할 수 있습니다.

다음은 구성된 탭 설정의 예시입니다.

![Object View에서 탭 설정 편집하기](https://www.palantir.com/docs/resources/foundry/object-views/tab-settings.png)

**설명**: 섹션 간 필터링은 발행자(publisher)와 구독자(consumer) 구조입니다. 막대 차트에서 "JFK" 막대를 클릭하면 그 차트가 `destination = JFK`라는 필터를 내보내고, 같은 필터 집합 ID를 구독하는 다른 차트와 표가 이 조건을 받아 자기 데이터를 다시 걸러 보여 줍니다. 필터 집합 ID를 여러 탭에서 같게 맞추면 탭을 옮겨 다녀도 이 필터가 유지됩니다.

> **중간 요약**: 탭은 프로필, 속성 값 조건, 링크 표시(권한) 조건으로 조건부 표시할 수 있습니다. 그 밖에 제목, 링크 개수 배지를 보여 주는 콘텐츠 유형, 2열 레이아웃 너비, 위젯 사이에서 필터를 주고받는 섹션 간 필터링을 설정합니다.

## 정리

- 탭은 Object View의 탐색과 그룹화 단위이며, 관리형 Workshop 모듈(권장, 재사용 불가)과 기존 Workshop 모듈(재사용 가능) 두 종류가 있습니다. 레거시 빌더 탭은 기존 것만 지원됩니다.
- 탭은 편집기 사이드바와 미리 보기에서 추가, 삭제, 순서 변경을 할 수 있습니다.
- 탭 표시 여부는 프로필, 속성 값, 링크 표시 권한으로 조건을 걸 수 있습니다.
- 탭 설정으로 제목, 콘텐츠 유형(링크 개수 배지), 2열 레이아웃 너비, 섹션 간 필터링을 구성합니다.
