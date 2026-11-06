# Scheduling Gantt Chart 위젯 (Scheduling Gantt Chart widget)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-gantt-chart-widget/
- 사이드바 위치: Applications > Dynamic Scheduling > Scheduling Gantt Chart widget

이 페이지는 동적 스케줄링의 중심 위젯인 Scheduling Gantt Chart의 화면 구성과 모든 설정 항목을 설명합니다. 타임라인, 행(자원), 일정 레이어(퍽), 레이아웃, 지표, 출력 변수, 시나리오 순서로 설정을 훑으며, 어떤 항목이 필수인지 표시합니다. 위젯을 실제로 구성할 때 참조표로 쓰는 페이지입니다.

Scheduling Gantt Chart는 스케줄링이나 자원 배정 워크플로를 위한 대화형 간트 차트를 그리는 Workshop 위젯입니다. 위젯을 설정하기 전에 [동적 스케줄링 온톨로지](04_scheduling-ontology-primitives.md)를 구성했는지 확인하세요.

Scheduling Gantt Chart 위젯을 설정하는 모듈 빌더는 다음을 할 수 있습니다.

* 자원 객체 행의 제목 및 부제목 속성(아이콘과 함수 기반 속성 포함)을 설정합니다.
* 오른쪽 클릭 메뉴에 나타날 액션, 이벤트, 추천을 선택합니다.
* [퍽 스타일](06_scheduling-schedule-layer-style.md)을 고르고, 퍽의 색상과 상호작용(배정 동작, 스냅 동작)을 사용자 지정합니다.

아래 예시에서 Scheduling Gantt Chart는 조종사를 항공편에 배정합니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/example-use-case.png" alt="Scheduling Gantt Chart 예시: 조종사를 항공편에 배정하기." width="800" >

<a id="widget-layout"></a>
## 위젯 레이아웃 (Widget layout)

아래 이미지는 위젯 레이아웃의 개요를 보여 줍니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/use-case-widget.png" alt="위젯 레이아웃 예시." width="1000" >

1. **일정 객체(퍽) (Schedule objects (pucks)):** 각 일정 객체는 Scheduling Gantt Chart 위에 퍽으로 그려집니다. 사용자는 이 퍽을 드래그 앤 드롭하여 객체의 시작 시각, 종료 시각, 그리고/또는 연결된 자원 객체를 갱신할 수 있습니다. 퍽에는 두 가지 부가 기능이 있습니다.
   * **일정 객체 상세(Schedule object details):** 커서를 퍽 위에 올리면 카드로 나타납니다. 기본적으로 카드에는 시작/종료 시각, 일정 객체 타입에 설정된 규칙들의 상태, Object View로 가는 링크가 표시됩니다. 빌더는 표시하고 싶은 속성을 추가할 수도 있습니다.
   * **오른쪽 클릭 메뉴(Right-click menu):** 사용자가 퍽을 오른쪽 클릭하면 나타납니다. 빌더는 액션, 이벤트, 추천을 설정할 수 있습니다.
2. **자원 객체 또는 행(Resource object or rows):** 각 자원 객체는 Scheduling Gantt Chart의 행으로 그려집니다.
   * **자원 객체 상세(Resource object details):** 커서를 행 위에 올리면 카드로 나타납니다. 카드에는 객체 타이틀, 애플리케이션 빌더가 선택한 속성, Object View로 가는 링크가 표시됩니다.
3. **검색창(Search bar):** Scheduling Gantt Chart 위젯에는 위젯 안 검색창이 있습니다. 사용자가 검색어를 입력하면 결과가 노란 테두리로 강조됩니다. `Enter` 키를 누르면 결과로 새 검색 그룹이 만들어집니다.
4. **위반 규칙 필터(Violation rules filter):** 위반 규칙 필터는 일정에서 주의가 필요한 부분에 집중하는 데 쓰입니다. 일정에 대해 평가할 규칙을 켜고 끌 수 있으며, 선택한 규칙을 위반하는 객체만 걸러 볼 수 있습니다.
5. **사용자 환경설정(User preferences, 지원 중단):** 사용자는 선호하는 설정을 정의하고 저장할 수 있습니다. 사용자 지정 가능한 옵션은 다음과 같습니다.
   * **Timezone:** 기본적으로 Foundry의 모든 타임스탬프는 UTC입니다. 이 기능은 사용자가 선택한 시간대에 맞게 오프셋을 처리합니다.
   * **Collapse pucks:** 위젯은 화면 공간을 아끼기 위해 겹치는 퍽들을 자동으로 하나의 퍽으로 합칩니다. 이 토글로 이 기능을 켜고 끌 수 있습니다.
   * **Show time now line:** 현재 시각이 빨간 세로선으로 표시됩니다.
   * **Expand legend:** 범례를 기본으로 펼칠지 접을지 정합니다.
   * **Expand unscheduled:** 미배정(unscheduled) 서랍을 기본으로 펼칠지 접을지 정합니다.
   * **Expand all nested pucks:** 중첩된 퍽을 기본으로 펼칠지 접을지 정합니다.
   * **Scroll to pucks on external selection:** 켜면, 사용자가 위젯 바깥에서 일정 객체를 선택했을 때 타임라인이 선택된 객체의 위치로 스크롤됩니다.
   * **Persist row widths:** 사용자는 행 경계를 끌어 자원 객체 행의 너비를 조절할 수 있습니다. 이 너비 설정을 저장하면 애플리케이션을 다시 불러와도 기본값으로 돌아가지 않습니다.
   * **Persist row/grouping order:** 사용자는 자원 객체 행을 드래그 앤 드롭하여 순서를 직접 바꿀 수 있습니다. 이 순서 설정을 저장하면 애플리케이션을 다시 불러와도 기본값으로 돌아가지 않습니다.
6. **미배정 서랍(Unscheduled drawer):** 일정 객체가 시작/종료 시각과 연결된 자원 객체를 모두 갖추지 않으면 미배정으로 간주됩니다. 이 속성들 중 하나라도(또는 전부) null이면 일정 객체 퍽은 미배정 서랍에 나타납니다.
7. **변경 로그(Change log):** 변경 로그는 사용자가 일정에 가한 모든 편집을 추적합니다.
8. **변경 검토(Review changes):** 시나리오를 사용할 때 표시되는 옵션입니다. 이를 선택하면 활성 시나리오에서 이루어진 모든 온톨로지 편집과 남아 있는 검증 규칙 위반의 요약을 보여 주는 팝업이 뜹니다. 확인하면 온톨로지 편집이 실행됩니다.

**설명**: 미배정 판단은 단순한 null 검사입니다. 예를 들어 작업 행 `(id=W7, technician_id=null, start_time=09:00, end_time=10:00)`은 자원이 비어 있으므로 차트의 어느 행에도 그릴 수 없고, 따라서 하단 미배정 서랍에 표시됩니다. 사용자가 이 퍽을 서랍에서 어떤 정비사 행으로 끌어 놓으면 저장 핸들러가 `technician_id`를 채웁니다.

> **중간 요약**: 화면은 퍽(일정 객체), 행(자원 객체), 검색창, 위반 규칙 필터, 사용자 환경설정(지원 중단), 미배정 서랍, 변경 로그, 변경 검토로 구성됩니다. 시간이나 자원 값이 null인 일정 객체는 미배정 서랍에 들어갑니다.

<a id="widget-setup"></a>
## 위젯 설정 (Widget setup)

Scheduling Gantt Chart 위젯에는 여러 필수 및 선택 설정 항목이 있습니다. 이 섹션은 개요를 제공하며, 필수 설정에는 따로 표시를 했습니다.

<a id="timeline-data"></a>
### 타임라인 데이터 (Timeline data)

* **Start Timestamp \[필수]:** 타임라인의 시작입니다.
* **End Timestamp \[필수]:** 타임라인의 끝입니다.

<a id="timeline-configuration"></a>
### 타임라인 설정 (Timeline configuration)

* **Custom Display Range:** 사용자가 Workshop 모듈을 처음 열었을 때 타임라인에 표시되는 기간을 설정합니다. 다른 곳에서 따로 지정하지 않는 한, 사용자는 Scheduling Gantt Chart의 전체 길이를 스크롤할 수 있습니다.
* **Custom Timeline Grid Precision:** 기본 격자선을 대체할 간트 차트 격자선의 시간 단위를 선택합니다.
* **Disable timeline zoom and scroll:** 사용자가 타임라인 스크롤이나 확대/축소 기능을 사용하지 못하게 합니다.
* **Operating Hours:** 차트의 구간을 "운영/비운영"으로 구분합니다. 이 구간들은 서로 다른 색으로 음영 처리됩니다. 일별 일정, 사용자 지정 시간 범위, 요일 기반 일정을 설정할 수 있습니다. 선택적으로 **Collapse by default**를 켜면 간트 차트가 처음 그려질 때 비운영 시간이 접힙니다.
* **Timeline Date-Time Formatting:** 확대/축소 수준별로 타임라인의 날짜와 시간 형식을 사용자 지정합니다. 분, 시, 일, 주, 월, 분기, 연 단위 눈금에 대한 형식 문자열을 설정할 수 있습니다. 형식을 지정하지 않으면 기본값이 쓰입니다.

<a id="row-data"></a>
### 행 데이터 (Row data)

* **Fixed Resource Object Set \[필수]:** 인터페이스에서 Scheduling Gantt Chart 위젯의 행으로 그려집니다. 집합 안의 객체 하나가 행 하나에 대응합니다.

<a id="row-configuration"></a>
### 행 설정 (Row configuration)

* **Title Icon:** 각 행의 제목 속성 옆에 나타날 아이콘을 선택합니다.
* **Row Title:** 기본 행 제목을 대체할 속성을 선택합니다. 속성 값이 null일 때 행 제목을 표시할지 여부도 토글로 정할 수 있습니다.
* **Sub-Titles:** 객체 제목 아래에 나타날, 자원 객체 집합의 속성을 하나 이상 선택합니다. 또한 아래 이미지처럼 각 부제목에 아이콘을 선택할 수 있습니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/setup-4.png" alt="부제목이 설정된 Scheduling Gantt Chart 위젯." width="200" > <br><br>
* **Group-By Property:** 고정 자원(행)을 하위 그룹으로 나눌 고정 자원 객체 집합의 속성을 선택합니다. 정의된 그룹은 차트 안의 토글로 열고 닫을 수 있습니다. 아래 예시에서 자원은 "Garden City", "Garza", "Hoople" 그룹으로 나뉘었습니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/setup-5.png" alt="Scheduling Gantt Chart 위젯의 그룹화 설정." width="300" > <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/setup-6.png" alt="Scheduling Gantt Chart 위젯의 그룹화 설정." width="300" > <br><br>
* **Default Sorts:** 차트의 행 순서에 하나 이상의 기본 정렬을 적용할 수 있게 합니다.
* **Right Click Menu:** 자세한 내용은 [행에서 액션과 이벤트 실행하기](11_row-level-interactions/02_scheduling-row-level-triggering-actions-and-events.md)를 참고하세요.
  * **Action configuration:** 자원 객체 타입과 관련된 액션을 설정합니다. 이 액션은 표준 온톨로지 생성, 수정, 삭제 액션이거나 사용자 정의 [FoO 기반 액션](../../02_define-ontologies/04_functions/13_functions-on-objects/01_functions-on-objects.md)일 수 있습니다.
  * **Search function:** 행 수준 추천 함수를 설정합니다. 이 함수는 사용자가 차트에서 아무것도 배정되지 않은 시간을 오른쪽 클릭할 때 실행됩니다. 커서 위치는 특정 시각과 자원 객체에 대응하며, 이것을 함수의 입력으로 사용할 수 있습니다.
* **On Row Select Event:** 차트에서 행이 선택될 때 실행할 Workshop 이벤트를 설정합니다. 예를 들어 더 자세한 Object View가 담긴 서랍이 나타나게 할 수 있습니다.
* **Popover Actions:** 행 위에 마우스를 올릴 때 나타나는 기본 팝오버를 대체할 액션을 설정합니다.

**설명**: FoO는 Functions on Objects의 줄임말로, 온톨로지 객체를 입력으로 받아 읽거나 편집하는 함수(function)를 말합니다. 행 수준 검색 함수의 입력이 "커서 위치"라는 점은 구체적으로, 사용자가 정비사 T2 행의 14:00 지점을 오른쪽 클릭하면 함수가 `(resource = T2, time = 14:00)`를 받는다는 뜻입니다.

> **중간 요약**: 타임라인의 시작과 끝, 그리고 행이 될 고정 자원 객체 집합이 필수입니다. 행에는 제목, 부제목, 그룹화, 정렬, 오른쪽 클릭 메뉴(액션, 행 수준 검색 함수), 선택 이벤트, 팝오버 액션을 설정할 수 있습니다.

<a id="input-data-pucks"></a>
### 입력 데이터 (퍽) (Input data (pucks))

각 일정 레이어는 **Input Data (Pucks)** 섹션 안에서 독립적으로 설정합니다. 일정 레이어는 간트 차트 위에 퍽으로 표시되는 `Schedule` 객체의 집합을 나타냅니다. 각 레이어에는 데이터, 드래그 앤 드롭 동작, 외관, 상호작용, 규칙을 위한 하위 섹션이 따로 있습니다.

각 일정 레이어마다 [퍽 스타일](06_scheduling-schedule-layer-style.md)을 골라 시각적 표현을 바꿀 수 있습니다. 퍽 스타일, 색상, 속성에 대한 자세한 내용은 [일정 레이어(퍽) 스타일](06_scheduling-schedule-layer-style.md)을 참고하세요.

**설명**: 레이어를 여러 개 둘 수 있다는 것은, 예를 들어 같은 정비사 행 위에 "정비 작업" 객체 집합과 "휴가" 객체 집합을 서로 다른 레이어로 겹쳐 그릴 수 있다는 뜻입니다. 레이어마다 데이터, 색상, 저장 액션, 규칙을 따로 설정합니다.

<a id="data"></a>
#### 데이터 (Data)

* **Schedule Object Set \[필수]:** 차트에 그릴 `Schedule` 객체입니다.
* **Linked Resource Property \[필수]:** `Schedule` 객체에서 `Resource` 객체로 연결되는 속성입니다.
* **Start Time Property \[필수]:** `Schedule` 객체에서 시작 시각으로 쓸 속성입니다.
* **End Time Property \[필수]:** `Schedule` 객체에서 종료 시각으로 쓸 속성입니다.
* **Object set filter for unallocated pucks:** 미배정 퍽에만 적용되는 선택적 객체 필터입니다.

<a id="drag-drop"></a>
#### 드래그 앤 드롭 (Drag & drop)

**Drag & Drop** 하위 섹션은 차트 안에서 퍽을 어떻게 옮길 수 있는지 설정합니다. 자세한 설정 방법은 [드래그 앤 드롭 문서](12_schedule-layer-level-interactions/03_scheduling-drag-and-drop.md)를 참고하세요.

* **Allocation Behavior:** Scheduling Gantt Chart에서 퍽 배치가 어떻게 이루어질지 정합니다. 미리 정의된 옵션은 다음과 같습니다.
  * **Allocate:** 퍽을 차트 어디에나 드래그 앤 드롭할 수 있습니다. 같은 자원에 같은 시간에 여러 퍽이 배정될 수 있습니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/allocation-1.gif" alt="퍽 동작 예시: Allocate." width="600"> <br><br>
  * **Allocate (no overlaps):** **Allocate**와 비슷하지만, 같은 객체 타입의 퍽이 겹치지 않도록 보장합니다. 퍽을 다른 퍽 위에 놓으면, 기존 퍽과 그보다 나중 시간대에 배정된 모든 것이 자동으로 밀려나 겹침을 막고 순서를 유지합니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/allocate-no-overlap.gif" alt="퍽 동작 예시: Allocate no overlap." width="600"> <br><br>
  * **Allocate (resource only):** 일정 객체를 다른 자원으로만 옮길 수 있는 경우를 기본 지원합니다.
  * **Allocate (time only):** 일정 객체를 시간 방향으로만 옮길 수 있는 경우를 기본 지원합니다.
  * **Simple swap:** **Allocate (no overlaps)와** 비슷하지만, 퍽을 다른 퍽 위에 놓으면 두 퍽이 서로 자리를 바꿉니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/allocation-swap.gif" alt="퍽 동작 예시: Swap." width="600"> <br><br>
  * **Swap with downstream:** **Simple swap**과 비슷하게 선택한 퍽들이 자리를 바꿉니다. 다만 이 경우 자리를 바꾼 퍽 뒤에 배정된 모든 후속 퍽도 각자의 앞 퍽을 따라 움직여, 결과적으로 이후 순서 전체가 이동합니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/allocation-downstream.gif" alt="퍽 동작 예시: Swap with downstream." width="600"> <br><br>
  * **Snap to previous:** 퍽이 해당 행에서 가장 가까운 기존 퍽의 끝에 자동으로 붙습니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/allocation-swap.gif" alt="퍽 동작 예시: Snap to previous." width="600"> <br><br>

**설명**: **Allocate (no overlaps)를** 구체적인 값으로 보면 다음과 같습니다. 한 행에 A(09:00\~10:00), B(10:00\~11:00)가 있을 때 1시간짜리 새 퍽 X를 09:00에 놓으면, X가 09:00\~10:00을 차지하고 A는 10:00\~11:00, B는 11:00\~12:00으로 뒤로 밀립니다. **Simple swap**에서는 X를 A 위에 놓으면 X와 A의 자리만 바뀝니다.

* **Snap Behavior:** 기본적으로 사용자는 Scheduling Gantt Chart 위젯의 어떤 시각에든 분 단위까지 객체를 배정할 수 있습니다. 스냅 동작을 쓰면 빌더가 객체를 배정할 수 있는 정해진 간격을 설정할 수 있습니다. 퍽을 차트의 새 위치에 놓으면 퍽은 가장 가까운 간격의 시작점으로 맞춰집니다.

  예를 들어 의사 진료 예약을 지원하는 일정을 설정하는 사용자는 모든 배정(예약)이 정각(:00)이나 30분(:30)에 시작해야 한다고 정할 수 있습니다.

  * **Snap Interval Size**는 각 간격의 길이를 정하는 정수여야 합니다. 아래 예시에서 간격은 8시간으로 설정되어 있습니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/snap-behavior.gif" alt="스냅 동작 예시." width="600"> <br><br>
  * **Start Timestamp** 옵션은 스냅 간격이 시작되는 시각을 가리킵니다. 기본적으로 스냅 간격은 Scheduling Gantt Chart 위젯의 시작 타임스탬프에서 시작합니다. 이 값을 설정하면 기본 시작점을 대체하여 설정한 시각을 기준으로 퍽을 맞춥니다.

* **Save Handler Action:** 퍽을 드래그 앤 드롭하거나 크기를 바꿀 때 호출되는 액션입니다.
  * 저장 핸들러는 `Schedule` 객체에서 다음 파라미터를 수정해야 합니다. 각 파라미터는 선택(optional)으로 표시해야 합니다.
    * Resource ID (자원 객체를 가리키는 외래 키)
    * Start time (시작 시각)
    * End time (종료 시각)
  * 저장 핸들러 액션을 설정할 때는 위젯이 제공하는 파라미터를 기본값으로 넣어야 합니다. 자세한 내용은 스케줄링 [드래그 앤 드롭 문서](12_schedule-layer-level-interactions/03_scheduling-drag-and-drop.md)를 참고하세요.

> **중간 요약**: 일정 레이어마다 객체 집합, 연결 자원 속성, 시작/종료 속성이 필수입니다. 배정 동작(Allocate, no overlaps, resource only, time only, swap 계열, snap to previous)과 스냅 간격으로 드롭 결과를 제어하고, 저장 핸들러 액션이 실제 편집을 수행합니다.

<a id="appearance"></a>
#### 외관 (Appearance)

* **Color Config:** 이 일정 레이어의 모든 퍽에 쓸 색상을 선택합니다. 다음 색상 옵션 중에서 고를 수 있습니다.
  * **Static:** 이것을 선택하면 모든 퍽이 드롭다운 색상 선택기로 고른 같은 색이 됩니다. 정적 색상 퍽은 아래 이미지와 같습니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/setup-puck-color.png" alt="별도 설정이 없는 퍽 서식." width="600" > <br><br>
  * **Segmented by:** 간트 차트가 기본 색상 세트를 돌아가며 차트의 퍽을 칠합니다. <br><br>
  * **Conditional coloring:** 속성 값에 따라 퍽 색상을 정하는 조건부 색상 규칙을 설정합니다.
  * **Function-backed:** 각 일정 객체를 16진수 색상 문자열 또는 `color`와 `name` 필드를 가진 [사용자 정의 타입](../../02_define-ontologies/04_functions/04_types-reference.md)으로 대응시키는 맵을 반환하는 [함수](https://www.palantir.com/docs/foundry/workshop/functions-use/)를 설정합니다. `name`을 제공하면 범례가 지원됩니다.
* **Puck Title:** 기본 퍽 제목을 대체할 속성을 선택합니다.
* **Puck Properties:** 각 퍽 위에 직접 표시할 속성을 선택합니다. 속성은 위젯 설정에서와 같은 순서로 퍽에 나타납니다.
* **Popover Properties:** 각 퍽 위에 마우스를 올렸을 때 표시할 속성을 선택합니다. 속성은 설정에 선언된 순서대로 표시됩니다.
* **Puck Sort Order:** 한 레이어 안에서 퍽이 겹칠 때 퍽에 정렬을 적용합니다. 배경(background) 퍽에는 적용되지 않습니다.

**설명**: 함수 기반 색상의 반환값은 "객체 하나당 색 하나"인 맵(딕셔너리) 자료구조입니다. 예를 들어 `{작업A: "#FF0000", 작업B: "#00AA00"}` 형태이거나, 범례 이름까지 주려면 `{작업A: {color: "#FF0000", name: "지연"}}` 형태가 됩니다.

<a id="interactions"></a>
#### 상호작용 (Interactions)

* **Custom Suggestions:** 일정 객체에 대한 제안 함수를 선택합니다. 사용자가 퍽을 집어 들면 함수 결과가 차트 위에 강조 영역으로 그려집니다. 이를 이용해 사용자가 퍽을 놓을 수 있거나 놓아야 하는 곳을 알려 줄 수 있습니다. **Enforce Suggestions**를 켜면 사용자는 강조된 영역에만 퍽을 놓을 수 있습니다(Shift를 누르고 있으면 무시할 수 있습니다). 자세한 내용은 [제안 함수](07_scheduling-suggestion-functions.md)를 참고하세요.
* **Drag Cursor to Create Action:** 인터페이스를 가로질러 드래그하여 일정 대상 객체 타입의 새 객체를 만드는 동작을 활성화합니다. 사용자는 Shift를 누른 채 위젯 안에서 커서를 끌어 이 동작을 시작합니다. 자세한 내용은 [드래그하여 만들기 문서](12_schedule-layer-level-interactions/02_scheduling-drag-to-create.md)를 참고하세요. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/drag-create-action.gif" alt="커서를 드래그하여 생성 액션을 실행하는 예시." width="600"> <br><br>
* **Right Click Menu:**
  * **Action configuration:** 일정 객체 타입과 관련된 액션을 설정합니다. 표준 온톨로지 생성, 수정, 삭제 액션이거나 사용자 정의 Function-on-Objects 기반 액션일 수 있습니다.
  * **Search function:** 퍽 수준 추천 함수를 설정합니다. 이 함수는 사용자가 퍽을 오른쪽 클릭할 때 실행됩니다. 일정 객체의 시작/종료 시각과 객체 자체를 함수의 입력으로 사용할 수 있습니다.
  * **Events:** 위젯 안에서 실행할 수 있는 표준 Workshop 이벤트의 조합을 설정합니다.
* **Popover Actions:** 퍽 팝오버의 탭에 나타날 액션을 설정하며, 기본 팝오버 화면을 대체합니다.
* **Enable Cross Widget Drops:** 사용자가 다른 위젯의 객체를 이 일정 레이어로 끌어 올 수 있게 합니다. 켜면, 끌어 놓은 객체를 어떻게 처리할지 정하는 드롭 액션을 설정합니다.
* **On Puck Select Event:** 차트에서 퍽이 선택될 때 실행할 Workshop 이벤트를 설정합니다.

<a id="rules"></a>
#### 규칙 (Rules)

일정 레이어에 적용할 선택적 검증 규칙입니다. 자세한 내용은 [검증 규칙](09_scheduling-validation-rules.md)을 참고하세요.

**주의**: Background 및 Event 퍽 스타일은 규칙(Rules)을 지원하지 않습니다.

> **중간 요약**: 외관에서는 색상(정적, 순환, 조건부, 함수 기반), 퍽 제목, 표시 속성, 정렬을 정합니다. 상호작용에서는 제안 함수, 드래그 생성, 오른쪽 클릭 메뉴(액션, 퍽 수준 검색 함수, 이벤트), 다른 위젯에서의 드롭, 선택 이벤트를 설정하고, 규칙에서는 검증 규칙을 붙입니다.

<a id="layout"></a>
### 레이아웃 (Layout)

**Layout** 섹션은 위젯의 시각적 표현을 제어하는 네 개의 하위 섹션으로 구성됩니다.

<a id="timeline"></a>
#### 타임라인 (Timeline)

* **Timeline Location:** 타임라인을 차트의 위쪽 또는 아래쪽에 둡니다.
* **Display Cursor Time Flag:** 켜면 커서 위치에 대응하는 깃발이 달린 세로선이 타임라인에 그려집니다. 깃발의 시간 표시 형식을 설정할 수 있습니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/display-cursor-time-flag.png" alt="일정 인터페이스에 커서 시각 깃발이 표시된 예시." width="300" > <br><br>
* **Timezone:** 위젯 전체에서 시간을 표시할 때 쓸 시간대를 설정합니다. 정적 값으로 지정하거나, Workshop 변수에 연결해 동적으로 시간대를 고르게 할 수 있습니다.
* **Expand Legend:** 범례를 기본으로 펼칠지 접을지 정합니다.

<a id="top-bar"></a>
#### 상단 바 (Top bar)

* **Hide Header:** 검색창, 검증 규칙 필터, 사용자 환경설정을 포함한 헤더를 숨깁니다.
* **Custom Header Date/Time Formatting:** 헤더의 날짜 범위 표시에 쓸 사용자 지정 날짜 및 시간 형식 문자열을 설정합니다.

<a id="bottom-bar"></a>
#### 하단 바 (Bottom bar)

* **Hide Footer:** 미배정 서랍, 변경 로그, 검토 옵션을 포함한 푸터를 숨깁니다.
* **Hide Unscheduled:** 켜면 미배정 토글 버튼이 숨겨집니다.
* **Expand Unscheduled:** 켜면 미배정 퍽 서랍이 기본으로 펼쳐집니다.
* **Standard Unallocated Puck Size:** 기본적으로 퍽의 크기는 아래 이미지처럼 시간 길이에 비례합니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/standard-unallocated-puck-size.png" alt="예시: 표준 미배정 퍽 크기." width="500" > <br><br>
  **Standard Unallocated Puck Size**를 켜면 아래 이미지처럼 미배정 영역에서 퍽 크기가 일정하게 맞춰집니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/toggled-puck-size.png" alt="예시: 크기가 일정하게 맞춰진 퍽." width="500" > <br><br>

<a id="puck-display"></a>
#### 퍽 표시 (Puck display)

* **Split Rows by Schedule Layer:** 각 일정 레이어가 하나의 고정 자원 안에서 하위 행을 갖습니다. 일정 레이어의 순서와 레이블은 **Input Data (Pucks)** 설정에서 정해지며, 객체 위에 마우스를 올리면 나타납니다. 이 설정은 기본적으로 꺼져 있으며, 애플리케이션에 일정 레이어가 여러 개 설정된 경우에만 적용됩니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/split-rows-by-schedule.png" alt="예시: 일정 레이어별로 행 나누기." width="600" > <br><br>
* **Expand All Nested Pucks:** 켜면 중첩된 자식을 가진 퍽이 기본으로 펼쳐집니다.
* **Collapse overlapping pucks:** 위젯이 화면 공간을 아끼기 위해 겹치는 퍽을 하나의 퍽으로 합칩니다.
* **Disable Popovers:** 켜면 팝오버가 비활성화됩니다.

> **중간 요약**: Layout은 타임라인(위치, 커서 시각 깃발, 시간대, 범례), 상단 바(헤더 숨김, 날짜 형식), 하단 바(푸터와 미배정 서랍, 미배정 퍽 크기), 퍽 표시(레이어별 하위 행, 중첩 펼침, 겹침 합치기, 팝오버 끄기)를 제어합니다.

<a id="metrics"></a>
### 지표 (Metrics)

**Metrics** 섹션에서는 사용자 정의 함수를 제공해 간트 차트에 지표를 추가할 수 있습니다. 두 종류의 지표를 설정할 수 있습니다.

* **Header Metrics:** 차트의 시간 축에 맞춰 정렬되는 지표입니다.
* **Row Metrics:** 차트 안의 각 행에 맞춰 정렬되는 지표입니다.

자세한 내용은 [인라인 지표](10_scheduling-inline-metrics.md)를 참고하세요.

<a id="output"></a>
### 출력 (Output)

Scheduling Gantt Chart 위젯은 다른 Workshop 위젯이 애플리케이션을 확장하는 데 사용할 수 있는 출력 변수를 생성합니다. 출력 변수는 다음과 같습니다.

* **Selected Objects:** 위젯에서 선택된 객체들의 객체 집합(object set)입니다.
* **Search Results Output:** 가장 최근의 검색/추천이 반환한 객체들의 객체 집합입니다. 이 출력은 함수가 객체를 반환할 때만 채워집니다.
* **User Preferences (지원 중단):** 모듈 인터페이스나 상태 저장(state saving)과 함께 사용하여 저장된 사용자 환경설정을 유지할 수 있는 직렬화된 문자열입니다.

**설명**: Workshop에서 위젯끼리는 변수로 데이터를 주고받습니다. 예를 들어 간트 차트의 **Selected Objects** 출력 변수를 옆의 테이블 위젯 입력으로 연결하면, 사용자가 차트에서 퍽 3개를 선택할 때 테이블에 그 3개 객체의 상세 속성이 표시됩니다.

<a id="scenarios"></a>
### 시나리오 (Scenarios)

Scheduling Gantt Chart 위젯에 대한 [온톨로지 시나리오](../../04_ontology-scenarios/01_overview-ontology-scenario.md)를 설정합니다.

* **Enable Scenarios:** 켜면 시나리오를 인식하는 다른 모든 워크플로에서 사용할 수 있는 시나리오 변수를 지정할 수 있습니다. 위젯에서 실행한 액션은 먼저 시나리오에 기록됩니다. 끄면 위젯에서 실행한 액션이 온톨로지에 직접 기록됩니다.
* **Disable Scenario:** 시나리오 비활성화 여부를 제어하는 불리언 변수입니다. true로 설정되면 액션이 온톨로지에 직접 기록됩니다.

> **중간 요약**: Metrics로 시간 축과 행에 정렬된 함수 기반 지표를 붙이고, Output 변수(선택 객체, 검색 결과, 사용자 환경설정)로 다른 위젯과 연동하며, Scenarios 설정으로 편집을 시나리오에 먼저 기록할지 온톨로지에 바로 기록할지 정합니다.

## 정리

- Scheduling Gantt Chart는 일정 객체를 퍽, 자원 객체를 행으로 그리는 Workshop 위젯이며, 검색창, 위반 규칙 필터, 미배정 서랍, 변경 로그, 변경 검토를 갖습니다.
- 필수 설정은 타임라인 시작/종료, 고정 자원 객체 집합, 그리고 각 일정 레이어의 객체 집합, 연결 자원 속성, 시작/종료 속성입니다.
- 일정 레이어마다 배정 동작, 스냅 간격, 저장 핸들러 액션, 색상과 표시 속성, 제안 함수와 검색 함수, 검증 규칙을 따로 설정합니다.
- Layout, Metrics, Output, Scenarios 섹션으로 화면 구성, 지표, 위젯 간 연동, 시나리오 기반 편집을 제어합니다.
