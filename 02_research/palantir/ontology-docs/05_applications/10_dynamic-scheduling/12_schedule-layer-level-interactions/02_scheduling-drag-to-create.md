# 드래그로 만들기 (Drag to create)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-drag-to-create/
- 사이드바 위치: Applications > Dynamic Scheduling > Schedule layer-level interactions > Drag to create

이 페이지는 Scheduling Gantt Chart에서 사용자가 행 위를 드래그해 새 일정 객체를 만드는 "드래그로 만들기(drag to create)" 기능을 설정하는 방법을 설명합니다. 핵심은 객체 생성 액션 타입을 하나 만들어 두고, 그 파라미터(시작 시각, 종료 시각, 자원 외래 키)를 드래그한 위치에서 자동으로 채우도록 연결하는 것입니다.

드래그로 만들기를 사용하면 최종 사용자가 필요할 때 바로 새 Schedule 객체를 만들 수 있습니다. 드래그로 만들기는 특정 행에, "드래그를 시작한 지점(dragged from)"과 "드래그를 끝낸 지점(dragged to)"을 시작 및 종료 타임스탬프로 하는 새 Schedule 객체를 초기화합니다.

이 페이지는 [Scheduling Gantt Chart 위젯](../05_scheduling-gantt-chart-widget.md)의 드래그로 만들기를 설명합니다. Calendar 위젯에서 드래그로 만들기를 설정하는 방법은 [드래그로 만들기](../14_scheduling-calendar-widget/02_scheduling-calendar-widget.md#drag-to-create)를 참고하세요.

드래그로 만들기를 구성하려면 `Create Action Type`을 제공해야 합니다. 퍽을 드래그 앤 드롭하면 위젯이 이 액션을 호출합니다.

아래 예에서는 스케줄 레이어를 `Object type A`라고 부르겠습니다.

<a id="set-up-drag-to-create-behavior"></a>
## 드래그로 만들기 동작 설정 (Set up drag-to-create behavior)

1. Ontology Manager에서 `Object type A`로 이동해 `Create Action Type`(생성 액션 타입)을 만듭니다. 이 액션 타입에는 다음 파라미터가 있어야 합니다.
   * 새 객체의 기본 키(primary key)
   * `Start Timestamp` 속성
   * `End Timestamp` 속성
   * `foreign key` 속성
   * 선택적으로, 객체 생성 시 채우고 싶은 속성을 추가합니다.
   * 결과적으로 이 액션 타입은 `Start Timestamp`, `End Timestamp`, `foreign key`를 입력하면 그 값들을 가진 `object type A` 객체가 만들어지도록 구성되어야 합니다.
2. 이제 Workshop에서 **Input Data (Pucks) > \[your schedule layer] > Interactions > Drag Cursor to Create Action**으로 이동합니다.
3. **Drag to Create Action**에서 앞에서 구성한 액션 타입을 선택합니다.
4. 방금 입력한 액션 타입 아래에서 **Select parameter to configure**를 선택하고 시작 타임스탬프, 종료 타임스탬프, 외래 키 파라미터를 선택합니다. 이제 구성에 이 세 파라미터가 나열되어 보여야 합니다. 이어서 Scheduling Gantt 변수를 선택해 이 파라미터 값들을 미리 채웁니다.
   * **Start Timestamp** 파라미터의 경우, **Local Default Value**에서 팝업의 **SELECTED START TIMESTAMP**를 선택합니다. 그러면 드래그로 만들기를 할 때 위젯이 드래그를 시작한 지점의 타임스탬프를 자동으로 전달합니다.
   * **End Timestamp** 파라미터의 경우, **Local Default Value**에서 팝업의 **SELECTED END TIMESTAMP**를 선택합니다. 그러면 드래그로 만들기를 할 때 위젯이 드래그를 끝낸 지점의 타임스탬프를 자동으로 전달합니다.
   * **foreign key** 파라미터의 경우, **Local Default Value**에서 팝업의 **RESOURCE ID**를 선택합니다. 그러면 드래그로 만들기를 할 때 위젯이 드래그로 만들기를 실행한 행(자원)을 자동으로 전달합니다.

**설명**: 이 설정은 액션 타입의 파라미터와 위젯이 제공하는 값을 짝지어 주는 과정입니다. 생성 액션은 SQL로 보면 `INSERT INTO object_type_a (id, start_ts, end_ts, resource_id) VALUES (?, ?, ?, ?)`와 같은 구조이고, 위젯은 드래그한 결과에서 `?` 자리 중 세 개(시작 시각, 종료 시각, 행의 자원 ID)를 채워 줍니다. 기본 키는 위젯이 채워 주는 값 목록에 없으므로, 액션 타입 쪽에서 자동 생성하거나 사용자가 양식에서 입력하도록 구성해야 합니다.

> **중간 요약**: Ontology Manager에서 시작 시각, 종료 시각, 외래 키를 받아 객체를 만드는 생성 액션 타입을 만들고, Workshop의 **Drag to Create Action**에 연결한 뒤 세 파라미터의 기본값을 **SELECTED START TIMESTAMP**, **SELECTED END TIMESTAMP**, **RESOURCE ID**로 지정합니다.

<a id="use"></a>
## 사용 (Use)

설정을 마친 뒤에는 원하는 행에서 시작 시각부터 종료 시각까지 `Shift + Drag`를 합니다. 그러면 드래그로 만들기 액션 양식이 팝업으로 열립니다. 제출하면 지정한 행에, "드래그를 시작한 지점"과 "드래그를 끝낸 지점"의 시작 및 종료 타임스탬프를 반영한 새 Schedule 객체가 만들어집니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/drag-to-create.gif" alt="드래그로 만들기 설정." width = "800">

## 정리

- 드래그로 만들기는 행 위를 드래그한 구간으로 새 Schedule 객체를 만드는 기능입니다.
- 먼저 기본 키, 시작 시각, 종료 시각, 외래 키를 파라미터로 받는 생성 액션 타입을 Ontology Manager에서 만듭니다.
- Workshop에서 **Interactions > Drag Cursor to Create Action**에 그 액션 타입을 지정하고, 파라미터 기본값을 위젯 변수로 연결합니다.
- 사용자는 `Shift + Drag`로 구간을 지정하고, 열린 양식을 제출해 객체를 만듭니다.
