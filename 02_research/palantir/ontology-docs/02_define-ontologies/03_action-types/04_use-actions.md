# 플랫폼에서 액션 사용하기 (Use actions in the platform)

- 원문: https://www.palantir.com/docs/foundry/action-types/use-actions/
- 사이드바 위치: Define Ontologies > Action types > Use actions in the platform

액션 타입을 정의하는 것만으로는 사용자가 실제로 액션을 실행할 수 없습니다. 이 페이지는 정의한 액션 타입이 Object View, Object Explorer, Workshop 같은 Foundry 애플리케이션 화면의 어디에 나타나고, 버튼으로 어떻게 구성하는지 설명합니다. 같은 액션 하나를 화면마다 다른 기본값과 라벨로 노출하는 방법도 다룹니다.

액션 타입은 Foundry의 여러 애플리케이션에 매끄럽게 통합할 수 있습니다. 아래에서 [Object Explorer](../../05_applications/01_object-explorer/01_overview.md)와 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)에서 액션을 구성하고 적용하는 방법을 알아봅니다.

아래 예시에서 **단일 액션 타입(single action type)은** 객체 참조(object reference) 파라미터를 사용하는 액션 타입을, **일괄 액션 타입(bulk action type)은** 객체 참조 목록(object reference list) 파라미터를 사용하는 액션을 가리킵니다.

아래의 각 위치에는 현재 선택에 적용할 수 있는 액션 타입만 나열됩니다. 여러 객체가 목록 보기로 표시되는 일괄 컨텍스트에서는, 객체 목록 파라미터가 선택된 객체 타입과 일치하는 일괄 액션 타입만 나열된다는 뜻입니다.

**설명**: 객체 참조 파라미터는 함수의 인자로 객체 하나(예: `Flight` 객체 F100)를 받는 것이고, 객체 참조 목록 파라미터는 객체 배열(예: `[F100, F101, F102]`)을 받는 것입니다. 그래서 사용자가 객체 하나를 보고 있을 때는 단일 액션이, 여러 객체를 목록으로 선택했을 때는 그 객체 타입의 목록을 받는 일괄 액션이 메뉴에 나타납니다. 예를 들어 Flight 객체 50개를 선택한 상태라면 `Flight` 목록을 받는 일괄 액션만 보이고, `Aircraft` 목록을 받는 액션은 보이지 않습니다.

<a id="object-views"></a>
## Object View

[Object View](../../05_applications/03_object-views/01_overview.md)에는 **Actions section**(액션 섹션)을 사용해 액션을 추가할 수 있습니다.

![Object View의 Actions section](https://www.palantir.com/docs/resources/foundry/action-types/integrate_actions_object_explorer_object_view_actions_section.png)

**Actions section**을 구성할 때 다음을 할 수 있습니다.

* 어떤 액션이든 섹션에 버튼으로 추가합니다.
* 버튼마다 고유한 라벨과 색상을 지정합니다.
* 클릭 시 기본 동작을 "폼 열기"에서 "기본값(유효한 경우)으로 즉시 액션 적용"으로 바꿉니다.
* 화면에 보이지 않는 파라미터가 유효하지 않을 때 버튼을 숨길지 비활성화할지 지정합니다(보이는 파라미터는 폼을 열었을 때 사용자가 고칠 수 있다는 생각에서입니다).
* 파라미터마다 기본값을 제공합니다. 기본값은 현재 객체의 속성(property) 값이거나 "로컬" 값(현재 사용자, 현재 타임스탬프, 현재 객체, 직접 입력한 값)일 수 있습니다.
* 파라미터마다 표시 여부를 재정의합니다.

위에서 보듯, 이 섹션을 사용하면 같은 범용 액션 하나를 구조화된 여러 버전("10분 지연", "30분 지연" 등)으로 제공할 수 있습니다.

**설명**: 예를 들어 `Delay flight`라는 액션 타입이 `flight`(객체 참조)와 `delayMinutes`(정수) 두 파라미터를 받는다고 합시다. Object View에 버튼 두 개를 만들고, 첫 번째 버튼은 `delayMinutes` 기본값을 10, 두 번째 버튼은 30으로 두고 `delayMinutes`를 숨긴 뒤 "즉시 적용"으로 설정하면, 사용자는 폼을 열지 않고 클릭 한 번으로 해당 항공편을 10분 또는 30분 지연시킬 수 있습니다. `flight` 파라미터 기본값은 "현재 객체"로 둡니다. 액션 타입은 하나지만 버튼마다 고정된 인자값을 넣어 호출하는 구조입니다.

> **중간 요약**: Object View의 Actions section에서 액션을 버튼으로 추가하고, 버튼마다 라벨, 색상, 클릭 동작, 파라미터 기본값과 표시 여부를 따로 지정할 수 있습니다. 이를 이용해 하나의 액션을 여러 개의 미리 정해진 버튼으로 노출합니다.

<a id="object-explorer"></a>
## Object Explorer

[Object Explorer](../../05_applications/01_object-explorer/01_overview.md)에서는 액션이 세 곳에 자동으로 표시됩니다.

1. Exploration View(탐색 보기) 오른쪽 위의 **Actions** 드롭다운.

![Exploration View의 Actions 드롭다운](https://www.palantir.com/docs/resources/foundry/action-types/integrate_actions_object_explorer_exploration_view_actions_dropdown.png)

이 드롭다운은 현재 객체 집합(object set)을 기준으로, 적용 가능한 일괄 액션으로 자동 채워집니다.

2. Object View 오른쪽 위의 **Object Actions** 드롭다운 메뉴.

![Object View의 Object Actions 드롭다운](https://www.palantir.com/docs/resources/foundry/action-types/integrate_actions_object_explorer_object_view_object_actions_dropdown.png)

이 드롭다운 메뉴는 현재 객체를 기준으로, 적용 가능한 단일 및 일괄 액션 타입으로 자동 채워집니다.

3. Object View 위쪽의 **Linked objects view section**(연결된 객체 보기 섹션).

![Object View의 Linked objects view section](https://www.palantir.com/docs/resources/foundry/action-types/integrate_actions_object_explorer_object_view_linked_objects_view_section.png)

이 드롭다운은 선택한 객체(하나 또는 여러 개)를 기준으로, 적용 가능한 단일 및/또는 일괄 액션 타입으로 자동 채워집니다.

**설명**: Object Explorer에서는 별도 구성 없이도 액션이 나타난다는 점이 Object View의 Actions section과 다릅니다. 플랫폼이 "지금 화면에 있는 객체를 파라미터로 받을 수 있는 액션"을 찾아 메뉴를 채웁니다. 탐색 보기는 검색 결과처럼 여러 객체를 다루므로 일괄 액션만, 객체 하나의 Object View는 그 객체 하나를 넣을 수 있는 단일 액션과 일괄 액션(목록에 그 객체 하나를 넣는 경우)이 나타납니다.

> **중간 요약**: Object Explorer는 탐색 보기의 Actions 드롭다운, Object View의 Object Actions 드롭다운, Linked objects view section 세 곳에 현재 선택에 맞는 액션을 자동으로 보여 줍니다.

<a id="workshop"></a>
## Workshop

[Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)에서는 [**Button group** 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-button-group/)을 사용해 액션을 구성하고 적용할 수 있습니다.

![Workshop의 Button group 위젯](https://www.palantir.com/docs/resources/foundry/action-types/integrate_actions_workshop_button_group_widget.png)

이 위젯은 Object View의 [Actions section](#object-views)과 같은 구성 옵션을 가지며, 몇 가지 주목할 확장이 있습니다.

* 레이아웃이 세 가지 있으며, 위 그림에 모두 나와 있습니다.
* 버튼에 왼쪽/오른쪽 아이콘, minimal 스타일, tag 스타일 같은 추가 표시 옵션이 있습니다.
* 개별 버튼은 액션 외에도 Workshop 이벤트, URL, 객체 집합 내보내기(export)를 실행할 수 있습니다.

그리고 차이점이 하나 있습니다.

* 기본값으로 [변수(variable)](https://www.palantir.com/docs/foundry/workshop/concepts-variables/), 현재 사용자, 현재 타임스탬프를 쓸 수 있습니다.

[Workshop의 액션](https://www.palantir.com/docs/foundry/workshop/actions-overview/)에 대해 더 읽어 보거나, 사용 가능한 모든 구성 옵션은 [Button Group 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-button-group/) 전체 레퍼런스를 참고하세요.

**설명**: Workshop의 변수는 모듈 안에서 위젯끼리 값을 주고받는 상태 값입니다. 예를 들어 테이블 위젯에서 사용자가 선택한 행이 "선택된 Flight" 변수에 담기면, Button group 버튼의 `flight` 파라미터 기본값을 그 변수로 지정해 "선택한 항공편을 지연" 버튼을 만들 수 있습니다. Object View에서는 "현재 객체"가 기본값 출처였다면, Workshop에서는 변수가 그 역할을 합니다.

> **중간 요약**: Workshop에서는 Button group 위젯으로 액션 버튼을 만듭니다. Actions section과 같은 옵션에 레이아웃, 아이콘, 이벤트/URL/내보내기 실행이 추가되고, 기본값으로 Workshop 변수를 쓸 수 있습니다.

## 정리

- 단일 액션 타입은 객체 하나, 일괄 액션 타입은 객체 목록을 파라미터로 받으며, 각 화면에는 현재 선택에 맞는 액션만 나타납니다.
- Object View의 Actions section에서는 액션을 버튼으로 추가하고 라벨, 색상, 즉시 적용 여부, 파라미터 기본값과 표시 여부를 버튼별로 지정합니다.
- Object Explorer는 세 위치(탐색 보기, Object Actions 메뉴, Linked objects 섹션)에 적용 가능한 액션을 자동으로 채웁니다.
- Workshop에서는 Button group 위젯을 사용하며, Workshop 변수를 파라미터 기본값으로 쓸 수 있습니다.
