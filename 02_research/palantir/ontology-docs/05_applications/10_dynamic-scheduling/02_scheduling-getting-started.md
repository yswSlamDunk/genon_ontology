# 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-getting-started/
- 사이드바 위치: Applications > Dynamic Scheduling > Getting started

이 페이지는 동적 스케줄링 워크플로의 첫 버전을 만드는 최소 절차를 안내합니다. 먼저 온톨로지에 일정(Schedule)과 자원(Resource) 객체 타입, 링크, 저장용 액션을 만들고, 다음으로 Workshop에서 Scheduling Gantt Chart 위젯을 설정하는 두 단계로 구성됩니다.

다음 가이드는 동적 스케줄링 워크플로의 첫 번째 버전을 구현하는 단계를 제공합니다. 각 섹션에서 참조하는 문서를 검토하여 더 많은 정보를 얻으세요.

<a id="1-create-core-ontology-objects"></a><a id="create-core-ontology-objects"></a>
## 1. 핵심 온톨로지 객체 만들기 (Create core Ontology objects)

동적 스케줄링 워크플로를 만들려면 다음 핵심 객체 타입을 만들어야 합니다.

* `Schedule` 객체 타입을 만듭니다. 이것은 자원이 배정되는 이벤트, 배정(assignment), 또는 슬롯을 나타냅니다. 예를 들어 `Schedule` 객체 타입이 `Maintenance Tasks`(정비 작업)일 수 있고, 이 작업들은 `Technicians`(기술자)에게 배정되어야 합니다.
  * 이 객체 타입은 자원 객체 타입과의 관계를 만들기 위한 외래 키(foreign key)를 담는 속성(property)을 가져야 합니다.
  * 이 객체 타입은 `Schedule`의 고정된 길이를 강제할지 여부를 정하는 `fixed duration` 불리언(Boolean) 속성을 가질 수 있습니다.
  * 이 객체에서 편집(edit)을 활성화해야 합니다. 이 과정 전체에서 시작, 종료, 길이와 자원과의 관계가 편집되기 때문입니다.
* 일정에 배정할 자원을 나타내는 자원 객체 타입을 하나 이상 만듭니다. 예를 들어 작업을 수행해야 하는 사람(`Technician`)입니다.
* `Schedule` 객체 타입과 여러 `Resource` 객체 타입 사이에 링크를 만듭니다.
* 각 `Schedule`에 대해 저장 핸들러(save handler) 액션을 만듭니다. 자세한 내용은 [드래그 앤 드롭](12_schedule-layer-level-interactions/03_scheduling-drag-and-drop.md)을 참고하세요.
  * 저장 핸들러는 `Schedule` 객체에서 다음 파라미터를 수정해야 합니다. 각 파라미터는 선택(optional)으로 표시해야 합니다.
    * Resource ID (자원 객체를 가리키는 외래 키)
    * Start Time (시작 시각)
    * End Time (종료 시각)
  * 액션의 파라미터 ID는 일정 객체 타입에서 사용하는 속성 ID와 정확히 일치해야 합니다(예: 속성이 `start_time`이면 파라미터 ID도 `start_time`이어야 합니다).

각 객체 타입의 스키마에 대한 자세한 내용은 [동적 스케줄링 온톨로지 기본 요소 문서](04_scheduling-ontology-primitives.md)를 검토하세요.

**설명**: 구체적인 데이터로 보면 다음과 같습니다. `Technician` 테이블에 `T1 김정비`, `T2 이정비` 두 행이 있고, `Maintenance Task` 테이블의 각 행에 `technician_id`, `start_time`, `end_time` 열이 있다고 합시다. `technician_id`가 외래 키이며, 이 값을 기준으로 두 객체 타입이 링크됩니다. 사용자가 차트에서 작업 막대를 T1 행에서 T2 행으로 끌어 옮기면, 저장 핸들러 액션이 `technician_id`를 `T2`로, 필요하면 `start_time`과 `end_time`도 새 값으로 바꾸는 편집을 실행합니다. 파라미터를 선택으로 두는 이유는 한 번의 드래그에서 셋 중 일부만 바뀔 수 있기 때문으로 이해할 수 있습니다.

> **중간 요약**: Schedule 객체 타입(외래 키, 편집 허용), 하나 이상의 Resource 객체 타입, 둘 사이의 링크, 그리고 자원 ID와 시작/종료 시각을 선택 파라미터로 받는 저장 핸들러 액션이 필요합니다. 파라미터 ID는 속성 ID와 같아야 합니다.

<a id="2-configure-the-widget-in-workshop"></a><a id="configure-the-widget-in-workshop"></a>
## 2. Workshop에서 위젯 설정하기 (Configure the widget in Workshop)

핵심 객체를 만들었으면 이제 Workshop에서 사용할 위젯을 설정할 수 있습니다.

Scheduling Gantt Chart 설정에는 최소한 다음이 필요합니다.

* **Timeline Data:** 차트의 전체 범위를 정하는 시작 및 종료 타임스탬프입니다.
* **Row Data:** 차트의 각 행에 대응하는 `Resource` 객체입니다.
* **Input Data (Pucks):** 다음을 갖춘 일정 레이어(schedule layer)가 최소 하나 있어야 합니다.
  * **Schedule Object Set:** 이 레이어에 표시할 `Schedule` 객체입니다.
  * **Linked Resource Property:** 각 `Schedule` 객체를 `Resource` 객체에 연결하는 속성입니다.
  * **Start Time Property** 및 **End Time Property:** 각 `Schedule` 객체의 시작 시각과 종료 시각을 정하는 속성입니다.
  * **Save Handler Action:** `Schedule` 객체에 대응하는 저장 핸들러 액션입니다.
    * 설정 옵션 안에서, 드롭다운에 있는 위젯 제공 파라미터를 사용해 저장 핸들러 액션의 기본 파라미터를 지정해야 합니다.

자세한 내용은 [Scheduling Gantt Chart 위젯 문서](05_scheduling-gantt-chart-widget.md)를 검토하세요.

**설명**: 퍽(puck)은 간트 차트 위에 그려지는 작업 막대(블록) 하나를 가리키는 용어입니다. 즉 `Schedule` 객체 하나가 퍽 하나로 그려지고, `Resource` 객체 하나가 행 하나로 그려집니다.

> **중간 요약**: 위젯에는 타임라인 범위, 행이 될 Resource 객체, 그리고 Schedule 객체 집합과 연결 속성, 시작/종료 속성, 저장 핸들러 액션을 갖춘 일정 레이어가 최소한 필요합니다.

## 정리

- 1단계: 온톨로지에 Schedule 객체 타입(외래 키 속성, 편집 활성화, 선택적으로 `fixed duration`), Resource 객체 타입, 둘 사이의 링크를 만듭니다.
- 저장 핸들러 액션은 Resource ID, Start Time, End Time을 선택 파라미터로 받으며 파라미터 ID가 속성 ID와 같아야 합니다.
- 2단계: Workshop의 Scheduling Gantt Chart에 Timeline Data, Row Data, 그리고 일정 레이어(객체 집합, 연결 속성, 시작/종료 속성, 저장 핸들러)를 설정합니다.
