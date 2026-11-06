# Scheduling Calendar 위젯 구성 (Widget configuration)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-calendar-widget/
- 사이드바 위치: Applications > Dynamic Scheduling > Scheduling Calendar widget > Widget configuration

이 페이지는 Scheduling Calendar 위젯의 구성 방법을 설명합니다. 읽기 전용 모드와 동적 모드의 차이, 입력 데이터(객체 집합, 시작과 종료 속성, 색상, 저장 핸들러 액션) 설정, 표시 설정, 드래그로 새 일정 만들기, 그리고 자주 발생하는 구성 오류와 해결 방법을 다룹니다. 특히 저장 핸들러 액션의 파라미터 ID가 속성 ID와 정확히 같아야 한다는 규칙이 중요합니다.

<a id="widget-modes"></a>
## 위젯 모드 (Widget modes)

Scheduling Calendar 위젯에는 읽기 전용(read-only)과 동적(dynamic) 두 가지 모드가 있습니다. 기본적으로 위젯은 읽기 전용 모드로 시작하며, 이 모드는 아무것도 변경하지 않고 데이터를 보고 분석하기 위해 설계되었습니다. 동적 모드로 전환하면 위젯 안에서 직접 Schedule 객체를 추가, 편집, 삭제할 수 있습니다.

<a id="input-data-pucks"></a>
## 입력 데이터(퍽) (Input data (pucks))

* **Schedule Name:** 구성 중에 여러 레이어를 구분하는 데 도움이 되는 레이어 이름입니다. 이 값은 위젯 자체에는 표시되지 않습니다.

* **Schedule Object Set:** Scheduling Calendar 위젯의 입력 변수로, 어떤 데이터가 표시될지를 결정합니다. 이 객체 집합(object set)에 대해 선택한 객체 타입은 시작 시각과 종료 시각을 나타내는 속성(property)을 가지고 있어야 합니다.

* **Start Time:** 이벤트의 시작 시각으로 사용할 날짜 또는 타임스탬프 속성을 선택합니다.

* **End Time:** 이벤트의 종료 시각으로 사용할 날짜 또는 타임스탬프 속성을 선택합니다.

* **Title:** 위젯에서 객체 퍽에 표시되는 레이블 값으로 사용할 속성을 선택합니다.

* **Color:** 차트에 이벤트를 표시할 때 사용할 색을 선택합니다.
  * **Static:** 모든 퍽에 단일 색을 지정합니다.
  * **Segment-by:** 속성을 선택하면, 위젯이 선택한 속성의 값에 따라 퍽의 색을 자동으로 구분합니다.
  * **Dynamic:** 차트의 퍽에 적용할 조건부 서식 규칙을 구성합니다.

* **Pop-over Properties:** 사용자의 커서가 달력의 퍽 위에 올라갔을 때 나타나는 팝오버 카드에 표시할 속성을 정합니다.

* **Save Handler Action (동적 모드):** 드래그 앤 드롭 상호작용에 사용할 액션을 선택합니다. 이 액션은 Schedule 객체의 시작 시각과 종료 시각 속성을 편집하는 Modify(수정) 액션이어야 합니다.
  * 액션에는 Schedule 객체의 시작 시각과 종료 시각을 수정하는 파라미터가 있어야 합니다.
  * 액션의 파라미터 ID는 시작 시각과 종료 시각으로 선택한 속성 ID와 정확히 일치해야 합니다. 예를 들면 다음과 같습니다.
    * 시작 시각 속성이 `start_time`이면, 액션 파라미터 ID도 `start_time`이어야 합니다.
    * 종료 시각 속성이 `end_time`이면, 액션 파라미터 ID도 `end_time`이어야 합니다.
  * 모든 파라미터는 선택 사항(optional)으로 표시해야 합니다.

* **Enable Drag to Create (동적 모드):** 최종 사용자가 달력의 빈 공간을 드래그해 새 Schedule 객체를 만들 수 있도록 액션을 선택합니다. 설정과 사용 방법은 [드래그로 만들기](#drag-to-create)를 참고하세요.

![데이터 레이어 구성](https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/calendar_data_layer_config.png)

**설명**: Scheduling Gantt Chart에서는 파라미터마다 **Local Default Value**로 위젯 변수를 연결했지만, Calendar의 저장 핸들러는 파라미터 ID와 속성 ID가 같은지로 값을 연결합니다. 그래서 `start_time` 속성을 시작 시각으로 골랐다면 액션 파라미터 ID도 반드시 `start_time`이어야 위젯이 끌어다 놓은 새 시각을 그 파라미터에 넣을 수 있습니다. 파라미터 ID는 화면에 보이는 이름이 아니라 내부 식별자라는 점에 주의하세요.

> **중간 요약**: 위젯은 기본적으로 읽기 전용이고 동적 모드에서만 편집이 가능합니다. 입력 데이터로 객체 집합, 시작과 종료 속성, 제목, 색상, 팝오버 속성을 지정하며, 동적 모드의 저장 핸들러 액션은 파라미터 ID가 시작과 종료 속성 ID와 정확히 같아야 하고 모든 파라미터가 선택 사항이어야 합니다.

<a id="display-configuration"></a>
### 표시 구성 (Display configuration)

* **Starting Day of Week:** 차트가 주 보기나 월 보기일 때 한 주의 시작 요일을 무엇으로 할지 정합니다.

* **Interval Size (동적 모드 전용):** 기본적으로 사용자는 Scheduling Calendar 위젯에서 객체를 분 단위까지 아무 시각에나 배정할 수 있습니다. 스냅 동작(snap behavior)을 사용하면 빌더가 객체를 배정할 수 있는 시각의 간격을 정할 수 있습니다. 퍽을 차트의 새 위치에 놓으면, 퍽이 가장 가까운 간격의 시작 시각에 맞춰집니다.

* **Starting Hour:** 일 보기나 주 보기에서 차트가 몇 시부터 시작할지 정합니다.

* **Ending Hour:** 일 보기나 주 보기에서 차트가 몇 시에 끝날지 정합니다.

![표시 구성 패널](https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/calendar_config.png)

**설명**: 예를 들어 Interval Size를 30분으로 정하면, 사용자가 퍽을 10시 12분 위치에 놓았을 때 그 위치가 속한 30분 간격의 시작인 10시 00분으로 맞춰집니다.

<a id="drag-to-create"></a>
## 드래그로 만들기 (Drag to create)

Calendar 위젯에서는 최종 사용자가 보조 키(modifier key)를 누른 채 달력을 드래그해 새 Schedule 객체를 만들 수 있습니다.

<a id="set-up-drag-to-create-behavior"></a>
### 드래그로 만들기 동작 설정 (Set up drag-to-create behavior)

1. Ontology Manager에서 달력 레이어에 표시되는 객체 타입에 대한 `Create Action`(생성 액션)을 만듭니다. 이 액션에는 다음 파라미터가 필요합니다.

   * 객체의 `Start Time` 속성
   * 객체의 `End Time` 속성
   * 선택적으로, 객체를 만들 때 사용자가 채우도록 하고 싶은 추가 속성.

   시작 시각과 종료 시각 파라미터는 객체 타입의 해당 속성에 맞춰 타임스탬프나 날짜 타입 중 하나로 지정할 수 있습니다.
2. Workshop에서 **Input Data (Pucks) > \[your calendar layer] > Interactions > Enable Drag to Create**로 이동합니다.
3. 구성한 `Create Action`을 선택합니다.
4. **Select parameter to configure**를 선택한 다음, **Local Default Value**에서 시작 시각과 종료 시각 파라미터를 연결합니다.
   * 시작 시각 파라미터에는 **SELECTED START TIMESTAMP**(파라미터가 날짜 타입이면 **SELECTED START DATE**)를 선택합니다. 그러면 드래그로 만들기를 할 때 위젯이 드래그를 시작한 시각을 전달합니다.
   * 종료 시각 파라미터에는 **SELECTED END TIMESTAMP**(또는 **SELECTED END DATE**)를 선택합니다. 그러면 드래그로 만들기를 할 때 위젯이 드래그를 끝낸 시각을 전달합니다.

<a id="use"></a>
### 사용 (Use)

새 객체를 만들려면 운영체제에 맞는 보조 키를 누른 채 달력의 빈 공간을 드래그합니다.

* **macOS:** `Cmd`(⌘)를 누른 채 드래그합니다.
* **Windows:** `Windows` 키를 누른 채 드래그합니다.

드래그를 놓으면 위젯은 드래그한 시작 시각과 종료 시각을 바탕으로 새로 제안된 객체를 즉시 표시합니다. 기본적으로는 구성의 자유도를 최대로 하기 위해 생성할 때마다 양식이 팝업으로 열립니다. **Hide form and apply immediately if valid** 구성을 선택하면 이 양식이 숨겨집니다. 새 객체는 변경 사항을 저장할 때에만 온톨로지(Ontology)에 실제로 만들어집니다.

**설명**: 드래그 직후 화면에 보이는 객체는 아직 온톨로지에 저장되지 않은 "제안된" 상태입니다. 사용자가 변경 사항을 저장해야 비로소 생성 액션이 반영되어 다른 사용자와 애플리케이션에서도 그 객체를 볼 수 있습니다.

> **중간 요약**: 드래그로 만들기는 시작과 종료 시각 파라미터를 가진 생성 액션을 **Enable Drag to Create**에 연결하고 두 파라미터를 **SELECTED START/END TIMESTAMP**(또는 DATE)로 채워 설정합니다. 사용자는 macOS에서 `Cmd`, Windows에서 `Windows` 키를 누른 채 드래그하며, 객체는 변경 사항을 저장할 때 온톨로지에 만들어집니다.

<a id="common-configuration-issues"></a>
## 자주 발생하는 구성 문제 (Common configuration issues)

<a id="error-the-action-parameter-ids-must-align-with-the-ids-of-the-selected-properties"></a>
### 오류: "The action parameter ids must align with the ids of the selected properties"

이 오류는 저장 핸들러 액션의 파라미터 ID가 위젯 구성에서 사용한 속성 ID와 정확히 일치하지 않을 때 발생합니다.

**원인:** 위젯은 다음 두 가지가 정확히 일치해야 합니다.

* 시작 시각 및 종료 시각 속성의 속성 ID
* 저장 핸들러 액션의 파라미터 ID

**해결 방법:**

1. Ontology Manager에서 속성 ID를 확인합니다.
   * Schedule 객체 타입으로 이동합니다.
   * 정확한 속성 ID(예: `start_time`, `end_time`)를 기록해 둡니다.
2. 액션 파라미터 ID를 확인합니다.
   * Ontology Manager에서 저장 핸들러 액션을 엽니다.
   * 액션의 파라미터 구성에서 파라미터 ID가 속성 ID와 정확히 일치하는지 확인합니다.
   * 파라미터 이름은 달라도 되지만, *파라미터 ID*는 속성 ID와 동일해야 합니다.
3. 필요하면 액션 파라미터 ID를 속성 ID와 일치하도록 수정합니다.

**설명**: 예를 들어 속성 ID가 `start_time`인데 액션 파라미터 ID가 `startTime`이나 `start_ts`로 되어 있으면 이 오류가 납니다. 화면에 보이는 파라미터 이름이 "Start Time"으로 같아도 ID가 다르면 일치하지 않는 것으로 판단됩니다.

> **중간 요약**: "The action parameter ids must align..." 오류는 저장 핸들러 액션의 파라미터 ID와 시작, 종료 속성 ID가 다를 때 발생하며, Ontology Manager에서 둘을 비교해 파라미터 ID를 속성 ID와 같게 고치면 해결됩니다.

## 정리

- Scheduling Calendar 위젯은 읽기 전용 모드로 시작하며, 동적 모드에서 객체 추가, 편집, 삭제가 가능합니다.
- 입력 데이터로 객체 집합, 시작과 종료 속성, 제목, 색상(Static, Segment-by, Dynamic), 팝오버 속성을 지정합니다.
- 동적 모드의 저장 핸들러 액션은 시작과 종료 시각을 수정하는 Modify 액션이어야 하고, 파라미터 ID가 속성 ID와 정확히 같아야 하며 모든 파라미터가 선택 사항이어야 합니다.
- 표시 구성으로 주 시작 요일, 스냅 간격, 일과 주 보기의 시작과 끝 시각을 정합니다.
- 드래그로 만들기는 생성 액션을 연결해 설정하고, 보조 키를 누른 채 드래그해 사용하며, 저장할 때 온톨로지에 반영됩니다.
