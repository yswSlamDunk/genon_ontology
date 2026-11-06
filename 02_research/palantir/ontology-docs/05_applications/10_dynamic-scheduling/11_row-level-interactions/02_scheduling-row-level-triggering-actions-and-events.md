# 행에서 액션과 이벤트 실행하기 (Triggering actions and events)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-row-level-triggering-actions-and-events/
- 사이드바 위치: Applications > Dynamic Scheduling > Row-level interactions > Triggering actions and events

이 페이지는 Scheduling Gantt 차트의 행에서 온톨로지 액션이나 Workshop 이벤트를 실행하도록 구성하는 방법을 설명합니다. 실행 경로는 행의 오른쪽 클릭 메뉴와 행 선택 시 이벤트 두 가지이며, 액션 파라미터를 행 객체나 클릭한 시각으로 자동 채우는 방법도 다룹니다.

온톨로지 액션을 사용하면 온톨로지(Ontology)에서 객체를 만들고, 수정하고, 삭제할 수 있습니다. Workshop 이벤트를 사용하면 팝업 띄우기, 섹션 토글, 탭 전환, 변수 값 갱신 등을 실행할 수 있습니다. 각 행에 최종 사용자가 실행할 수 있는 액션과 이벤트를 구성할 수 있습니다.

액션과 이벤트는 다음으로 실행할 수 있습니다.

* **행 오른쪽 클릭 메뉴(Row right-click menus)**
* **"On row select" 이벤트**

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/row-right-click-row-select-config.png" alt="오른쪽 클릭 메뉴와 행 선택 이벤트 구성." width="600">

**설명**: 액션(action)은 온톨로지의 데이터를 바꾸는 작업(데이터베이스로 치면 INSERT, UPDATE, DELETE)이고, Workshop 이벤트는 데이터는 그대로 두고 화면 상태만 바꾸는 작업(팝업 열기, 탭 전환 등)입니다.

<a id="row-right-click-menu"></a>
## 행 오른쪽 클릭 메뉴 (Row right-click menu)

행 수준 오른쪽 클릭 메뉴는 **Row Configuration > Right Click Menu**에서 구성할 수 있습니다. 메뉴 항목을 드래그해 메뉴 옵션의 순서를 바꿀 수 있습니다. 사용할 수 있는 오른쪽 클릭 메뉴 옵션은 다음 섹션에서 자세히 설명합니다.

* [액션 타입](#action-types)
* [Workshop 이벤트](#workshop-events)

<a id="action-types"></a>
### 액션 타입 (Action types)

일반적인 용도:

* 행 객체의 속성(property)을 편집합니다.
* 간트 차트에서 오른쪽 클릭한 시점에 새 객체를 만듭니다.

1. 이 메뉴 옵션의 사용자 지정 이름을 입력합니다.
2. 클릭 시 실행할 온톨로지 액션 타입을 선택합니다. `resource object type`과 관련된 액션 타입일 수 있지만, 반드시 그럴 필요는 없습니다.
3. 액션 타입의 파라미터를 Workshop 변수나 Scheduling Gantt 차트 전용 변수로 미리 채웁니다.
   * **Resource object:** 오른쪽 클릭한 행 객체로 자동 채워집니다.
   * **Selected start timestamp:** 행에서 오른쪽 클릭한 지점의 타임스탬프로 자동 채워집니다. 행의 빈 공간을 오른쪽 클릭할 때 유용합니다.

**설명**: 예를 들어 "휴가 등록" 액션 타입에 `technician`과 `start` 파라미터가 있다면, `technician`에는 **Resource object**를, `start`에는 **Selected start timestamp**를 연결해 둡니다. 그러면 사용자가 Kim 행의 11월 5일 지점을 오른쪽 클릭해 메뉴를 고를 때 두 값이 이미 채워진 액션 양식이 열립니다.

<a id="workshop-events"></a>
### Workshop 이벤트 (Workshop events)

일반적인 용도:

* 선택한 행에 대한 자세한 정보를 담은 팝오버를 띄웁니다.
* 선택한 행을 입력으로 미리 채운 상태에서 다른 Workshop 애플리케이션이나 페이지를 엽니다.

1. 이 메뉴 옵션의 사용자 지정 이름을 입력합니다.
2. 클릭 시 실행할 Workshop 이벤트를 선택합니다. 보통 선택한 행을 참조하기 위해 간트 차트의 선택 출력 변수(selection output variable)를 사용합니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/row-right-click-menu-example.png" alt="행 오른쪽 클릭 메뉴 예시." width="600">

> **중간 요약**: 행 오른쪽 클릭 메뉴는 **Row Configuration > Right Click Menu**에서 구성하며, 액션 타입(파라미터를 행 객체나 클릭 시각으로 자동 채움)과 Workshop 이벤트(선택 출력 변수로 선택 행 참조)를 메뉴 항목으로 넣을 수 있습니다.

<a id="on-row-select-event"></a>
## "On row select" 이벤트 ("On row select" event)

"On row select" 이벤트는 구성 화면에서 오른쪽 클릭 메뉴 아래에 있습니다. 이 옵션을 켜면, 사용자가 행 헤더를 선택(클릭)할 때 이벤트가 실행됩니다. 이벤트는 어떤 Workshop 이벤트든 될 수 있습니다.

## 정리

- 행에서는 온톨로지 액션(객체 생성, 수정, 삭제)과 Workshop 이벤트(팝업, 탭 전환, 변수 갱신 등)를 실행할 수 있습니다.
- 실행 경로는 행 오른쪽 클릭 메뉴와 "On row select" 이벤트 두 가지입니다.
- 오른쪽 클릭 메뉴의 액션은 **Resource object**와 **Selected start timestamp** 변수로 파라미터를 자동으로 채울 수 있습니다.
- "On row select" 이벤트는 행 헤더를 클릭할 때 실행됩니다.
