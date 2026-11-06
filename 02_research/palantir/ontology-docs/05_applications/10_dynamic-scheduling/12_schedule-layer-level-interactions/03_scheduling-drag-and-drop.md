# 드래그 앤 드롭 (Drag and drop)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-drag-and-drop/
- 사이드바 위치: Applications > Dynamic Scheduling > Schedule layer-level interactions > Drag and drop

이 페이지는 Scheduling Gantt Chart에서 퍽을 끌어 다른 행이나 다른 시각으로 옮기는 드래그 앤 드롭 기능을 설정하는 방법을 설명합니다. 퍽을 놓는 순간 위젯이 "저장 핸들러(save handler)" 액션을 호출해 객체의 시작 시각, 종료 시각, 배정 자원을 갱신하는 구조이며, 이동 단위(스냅), 고급 액션, 제안 함수 같은 맞춤 설정도 다룹니다.

Scheduling Gantt Chart 위젯의 드래그 앤 드롭 기능을 사용하면 최종 사용자가 "퍽"을 다른 행 그리고/또는 다른 시점으로 배정하거나 다시 배정할 수 있습니다. 드래그 앤 드롭은 위젯에서 퍽과 상호작용하는 기본 방법입니다.

<a id="set-up-drag-and-drop-behavior"></a>
## 드래그 앤 드롭 동작 설정 (Set up drag-and-drop behavior)

드래그 앤 드롭 동작을 구성하려면 위젯 구성 옵션에 저장 액션 핸들러(save action handler)를 제공해야 합니다. 퍽을 드래그 앤 드롭하면 위젯이 이 액션을 호출합니다. 아래 단계에서는 가장 일반적인 액션 타입, 즉 연결된 Schedule 객체의 시작 시각, 종료 시각, 배정된 행을 수정하는 단순한 액션에 드래그 앤 드롭 동작을 설정하는 방법을 안내합니다. 이 예에서는 스케줄 레이어를 `Object type A`라고 부르겠습니다.

<a id="set-up-instructions"></a>
## 설정 방법 (Set up instructions)

1. Ontology Manager에서 `Object type A`로 이동해 수정(modify) 액션 타입을 만듭니다. 이 액션 타입에는 다음 파라미터가 있어야 합니다.
   * object type A의 객체 하나
   * 그 객체 참조의 `Start timestamp` 속성
   * 그 객체 참조의 `End timestamp` 속성
   * 그 객체 참조의 외래 키 속성. 이 값은 해당 Schedule 객체가 배정된 `Row ID`에 해당합니다.
     결과적으로 이 액션 타입은 `Start timestamp`, `End timestamp`, 그리고/또는 갱신된 외래 키를 입력하면 object type A 객체의 값이 조정되도록 구성되어야 합니다.

2. 이제 Workshop에서 **Input Data (Pucks) > \[your schedule layer] > Drag & Drop**으로 이동합니다.

3. **Save Handler Action**에서 앞에서 구성한 액션 타입을 선택합니다.

4. 방금 입력한 액션 타입 아래에서 **Select parameter to configure**를 선택하고 객체, 시작 타임스탬프, 종료 타임스탬프, 외래 키 파라미터를 선택합니다. 이제 구성에 이 네 파라미터가 나열되어 보여야 합니다. 이어서 Scheduling Gantt 변수를 선택해 이 파라미터 값들을 미리 채웁니다.
   1. `Object` 파라미터의 경우, **Local Default Value**에서 팝업 창의 **SCHEDULE OBJECT**를 선택합니다. 그러면 드래그 앤 드롭할 때 위젯이 드래그 앤 드롭하는 Schedule 객체를 자동으로 전달합니다.
   2. `Start Timestamp` 파라미터의 경우, **Local Default Value**에서 팝업의 **SELECTED START TIMESTAMP**를 선택합니다. 그러면 드래그 앤 드롭할 때 위젯이 Schedule 객체를 끌어다 놓은 새 시작 타임스탬프를 자동으로 전달합니다.
   3. `End Timestamp` 파라미터의 경우, **Local Default Value**에서 팝업의 **SELECTED END TIMESTAMP**를 선택합니다. 그러면 드래그 앤 드롭할 때 위젯이 Schedule 객체를 끌어다 놓은 새 종료 타임스탬프를 자동으로 전달합니다.
   4. `foreign key` 파라미터의 경우, **Local Default Value**에서 팝업의 **RESOURCE ID**를 선택합니다. 그러면 드래그 앤 드롭할 때 위젯이 Schedule 객체를 끌어다 놓은 새 행(자원)을 자동으로 전달합니다.

이제 이 스케줄 레이어의 어떤 퍽이든 새 행(자원) 그리고/또는 새 시작 타임스탬프와 종료 타임스탬프로 드래그 앤 드롭할 수 있습니다. 놓는 순간 이 액션 타입이 갱신된 값들로 파라미터가 미리 채워진 상태로 실행됩니다. 추가 맞춤 설정은 다음 섹션을 참고하세요.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/configuring-drag-and-drop.gif" alt="드래그 앤 드롭 설정." width = "800">

**설명**: 예를 들어 작업 T-7(정비사 Kim, 9시\~11시)을 Lee 행의 13시 위치로 끌어다 놓으면, 위젯은 저장 핸들러 액션을 `Object = T-7`, `Start = 13시`, `End = 15시`, `foreign key = Lee`로 호출합니다. SQL로 보면 `UPDATE tasks SET start_ts = 13시, end_ts = 15시, mechanic_id = 'Lee' WHERE id = 'T-7'`에 해당하는 수정이 일어납니다. 앞에서 설명한 드래그로 만들기와 달리, 기존 객체를 받는 `Object` 파라미터가 하나 더 있다는 점이 다릅니다.

> **중간 요약**: 드래그 앤 드롭은 객체, 시작 시각, 종료 시각, 외래 키를 받는 수정 액션 타입을 **Save Handler Action**으로 지정하고, 네 파라미터를 **SCHEDULE OBJECT**, **SELECTED START TIMESTAMP**, **SELECTED END TIMESTAMP**, **RESOURCE ID** 변수로 채우도록 연결해 설정합니다.

<a id="drag-and-drop-behavior-customizations"></a>
## 드래그 앤 드롭 동작 맞춤 설정 (Drag-and-drop behavior customizations)

앞 섹션에서 설명한 단순 구성 외에도 드래그 앤 드롭 동작을 맞춤 설정할 수 있습니다.

<a id="update-snap-behavior"></a>
### 스냅 동작 변경 (Update snap behavior)

기본적으로 드래그 앤 드롭이 구성되면 퍽은 분 단위로 드래그할 수 있습니다. 스냅 동작(snap behavior)을 사용하면 퍽이 드래그되는 단위의 세밀도를 맞춤 설정할 수 있습니다. 예를 들어 퍽을 드래그 앤 드롭할 때 화면상에서 1분 단위가 아니라 하루 단위로 앞뒤로 움직이게 하고 싶을 때 사용합니다. 스냅 동작은 퍽의 가장자리를 끌어 기간을 늘리거나 줄일 때에도 적용됩니다. 설정하려면 아래 지침을 따르세요.

1. **Input Data (Pucks) > \[your schedule layer] > Drag & Drop > Snap Behavior**로 이동합니다.
2. 스냅 간격 크기에 대한 숫자 변수를 제공합니다.
3. 시간 단위를 선택합니다. 예를 들어 스냅 간격 크기에 `3`, 시간 단위에 `Day`를 지정하면, 이 레이어의 퍽을 드래그 앤 드롭할 때마다 3일 단위로 움직입니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/schedule-layer-snap-behavior.gif" alt="스냅 동작 설정." width = "800">

<a id="advanced-save-handler-action-type"></a>
### 고급 저장 핸들러 액션 타입 (Advanced save handler action type)

드래그 앤 드롭할 때 위젯은 제공된 파라미터로 저장 핸들러 액션 타입을 호출합니다. 일반적인 경우 이 액션 타입은 해당 속성들을 직접 수정하는 단순한 액션 타입입니다. 하지만 위젯이 `Schedule Object`, `Start Timestamp`, `End Timestamp`, `Resource ID`를 전달할 수만 있다면, 액션 타입의 내부 로직과 결과는 원하는 대로 만들 수 있습니다. 즉, 단순한 편집(edit) 대신 예를 들어 객체 대상 함수(function on object)로 뒷받침되는 액션 타입을 사용할 수도 있다는 뜻입니다. 또한 Workshop에서 추가 파라미터나 값을 액션 타입에 전달할 수도 있습니다.

다음과 같은 경우에는 드래그 앤 드롭에 함수 기반 액션 타입(function-backed action type)을 사용하는 것을 고려하세요.

* Schedule 객체를 편집하면서, 조건에 따라 온톨로지의 다른 객체에도 편집을 일으키고 싶을 때.
* Schedule 객체를 편집하면서, 온톨로지에 추가 객체를 만들고 싶을 때.
* Schedule 객체를 편집하면서, API를 호출하고 싶을 때.

**설명**: 함수 기반 액션 타입은 액션이 실행될 때 정해진 속성 수정 규칙 대신 사용자가 작성한 함수 코드를 실행하는 액션입니다. 예를 들어 작업을 옮길 때 원래 정비사의 "배정 시간 합계" 속성도 함께 줄이고 새 정비사의 값은 늘리는 처리처럼, 여러 객체를 한 번에 바꿔야 할 때 사용합니다.

<a id="suggestion-function"></a>
### 제안 함수 (Suggestion function)

퍽을 다른 행 그리고/또는 다른 시각으로 드래그 앤 드롭할 때, 최종 사용자에게 필요할 때 바로 추천을 제공하고 싶을 수 있습니다. **Custom Suggestions > Suggestion Function**을 사용하면 드래그 앤 드롭 시 실행되는 함수를 정의할 수 있습니다. 이 함수는 여러분이 작성한 로직에 따라 간트 차트의 시간 슬롯을 일시적으로 초록색이나 빨간색으로 칠해 "좋은" 위치와 "나쁜" 위치를 표시할 수 있습니다.

자세한 내용은 [Suggestion functions](../07_scheduling-suggestion-functions.md)를 참고하세요.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/drag-and-drop-suggestion-function.gif" alt="스냅 동작 설정." width = "800">

> **중간 요약**: 스냅 동작으로 퍽 이동 단위(예: 3일)를 바꿀 수 있고, 저장 핸들러를 함수 기반 액션 타입으로 바꿔 다른 객체 편집, 추가 객체 생성, API 호출까지 할 수 있으며, 제안 함수로 드래그 중 좋은 위치와 나쁜 위치를 색으로 표시할 수 있습니다.

## 정리

- 드래그 앤 드롭은 퍽을 다른 행이나 시각으로 옮겨 재배정하는 기본 상호작용입니다.
- 객체, 시작 시각, 종료 시각, 외래 키를 받는 수정 액션 타입을 **Save Handler Action**으로 지정하고, 파라미터를 위젯 변수로 자동 채우도록 연결합니다.
- 스냅 동작으로 이동과 기간 조정의 단위를 분 단위에서 원하는 단위로 바꿀 수 있습니다.
- 위젯이 필요한 네 값을 넘길 수 있다면 저장 핸들러는 함수 기반 액션 등 어떤 로직이든 될 수 있습니다.
- **Custom Suggestions > Suggestion Function**으로 드래그 중 추천 위치를 색으로 보여 줄 수 있습니다.
