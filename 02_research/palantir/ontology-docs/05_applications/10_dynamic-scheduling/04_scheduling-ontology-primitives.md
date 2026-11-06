# 온톨로지 기본 요소와 데이터 모델 구성 (Ontology primitives)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-ontology-primitives/
- 사이드바 위치: Applications > Dynamic Scheduling > Ontology primitives

이 페이지는 Dynamic Scheduling(동적 스케줄링) 위젯을 쓰기 위해 온톨로지(Ontology)에 어떤 객체 타입과 속성(property), 링크 타입을 준비해야 하는지 설명합니다. 스케줄링 화면은 "무엇을(작업)"과 "어디에/누구에게(자원)"라는 두 종류의 데이터를 시간축 위에 배치하므로, 이 두 가지를 객체 타입으로 먼저 모델링해야 위젯을 구성할 수 있습니다. 항공기 정비 일정을 예로 들어 최소 구성과 확장 구성을 보여 줍니다.

동적 스케줄링을 위한 온톨로지 기본 요소는 `Schedule` 객체 하나와 하나 이상의 `Resource` 객체로 이루어집니다. 먼저 [Ontology Manager](../04_ontology-manager/01_overview.md)에서 객체를 만드는 것부터 시작합니다. Workshop 위젯은 최소한 두 개의 객체 타입, 즉 `Schedule` 객체와 `Resource` 객체를 필요로 합니다.

| 객체 타입 | 설명 |
| --- | --- |
| Schedule 객체 | Schedule 객체는 관심 대상인 작업이나 활동을 나타내며, 해당 이벤트가 언제 일어나는지에 대한 시작 시각과 종료 시각, 그리고/또는 예상 소요 시간을 포함해야 합니다. |
| Resource 객체 | Resource 객체는 Schedule 객체가 배정되거나 일정이 잡히는 대상이 되는 모든 엔터티(사람, 장소, 프로젝트 등)를 나타냅니다. |

**설명**: 두 객체 타입을 데이터베이스 테이블로 생각하면 이해가 쉽습니다. 예를 들어 `MaintenanceTask` 테이블(Schedule 객체)에는 `task_id`, `aircraft_id`, `start_time`, `end_time` 열이 있고, `Aircraft` 테이블(Resource 객체)에는 `aircraft_id`, `model` 열이 있습니다. 화면에서는 Aircraft 한 대가 간트 차트의 한 행이 되고, 그 행 위에 해당 항공기에 배정된 MaintenanceTask들이 시간 구간으로 그려집니다.

<a id="ontology-requirements"></a>
## 온톨로지 요구 사항 (Ontology requirements)

`Schedule` 객체는 아래에 정리된 속성 및 링크 요구 사항을 충족해야 합니다.

<a id="required-schedule-object-properties"></a>
### Schedule 객체의 필수 속성 (Required schedule object properties)

| 객체 속성 | 타입 |
| --- | --- |
| 자원에 대한 외래 키 | String |
| 시작 시각 | Timestamp |
| 종료 시각 | Timestamp |

**설명**: 외래 키(foreign key)는 다른 테이블의 기본 키(primary key)를 가리키는 열입니다. 위 예에서 `MaintenanceTask.aircraft_id`가 `Aircraft.aircraft_id`를 가리키므로, 이 값을 보고 각 작업이 어느 항공기 행에 그려질지 결정됩니다. 시작 시각과 종료 시각은 Timestamp 타입이어야 시간축 위의 위치와 길이를 계산할 수 있습니다.

<a id="required-ontology-links"></a>
### 필수 온톨로지 링크 (Required Ontology links)

Schedule 객체 타입은 각 Resource 객체 타입과 링크되어 있어야 합니다. 다대일(many-to-one) 관계와 다대다(many-to-many) 관계를 모두 지원합니다. 예를 들어 위의 예에서는 여러 작업이 한 대의 항공기에 배정될 수 있습니다. 위젯 구성의 **Resource Link Type**이 관계가 다대일인지 다대다인지를 결정합니다.

**설명**: 다대일은 작업 여러 개가 항공기 하나를 가리키는 경우로, 작업 테이블에 외래 키 열 하나를 두면 표현됩니다. 다대다는 작업 하나가 여러 자원(예: 정비사 두 명)에 동시에 배정될 수 있는 경우로, 관계형 데이터베이스에서는 보통 별도의 조인 테이블(작업 ID, 자원 ID 쌍을 저장하는 테이블)로 표현합니다.

> **중간 요약**: Schedule 객체에는 자원을 가리키는 외래 키(String), 시작 시각과 종료 시각(Timestamp)이 반드시 있어야 하고, Schedule 객체 타입은 각 Resource 객체 타입과 다대일 또는 다대다 링크로 연결되어 있어야 합니다.

<a id="example-aircraft-maintenance-schedule"></a>
## 예시: 항공기 정비 일정 (Example: Aircraft maintenance schedule)

아래 예시는 항공기에 대한 정비 작업 일정을 잡는 과정을 보여 줍니다.

<a id="simple-configuration"></a>
### 단순 구성 (Simple configuration)

Dynamic Scheduling Workshop 위젯의 최소 요구 사항인 두 객체 타입 구성은 아래와 같습니다.

* **Schedule 객체 타입:** 아래 예에서 정비 작업은 시간이 정해진 활동입니다.
* **Resource 객체 타입:** 항공기는 작업이 수행되는 대상 또는 장소입니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/dynamic-scheduling-two-obj.png" alt="Schedule 객체 타입." width="500" >

<a id="advanced-configuration"></a>
### 고급 구성 (Advanced configuration)

동적 스케줄링 데이터는 두 객체 타입 모델을 넘어 다양한 추가 구성을 지원하므로, 애플리케이션 빌더는 복잡하고 고급스러운 워크플로를 만들 수 있습니다.

위의 두 객체 타입 모델을 바탕으로, 사용자는 배정된 항공기에서 정비 작업이 *언제* 일어날지 일정을 잡는 것 외에도, 작업을 특정 정비사에게 배정해 *누가* 정비 작업을 수행할지도 정할 수 있습니다. 아래 그림의 새 온톨로지에서 정비사 객체는 **두 번째 Resource 객체 타입** 역할을 하며, Resource 객체 타입의 개수에는 제한이 없습니다.

* **Schedule 객체 타입:** 정비 작업은 시간이 정해진 활동입니다.
* **Resource 객체 타입 1:** 항공기는 작업이 수행되는 대상 또는 장소입니다.
* **Resource 객체 타입 2:** 배정된 정비 작업을 수행할 정비사입니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/three-obj.png" alt="고급 Schedule 객체 타입." width="500" >

**설명**: 고급 구성에서는 MaintenanceTask 테이블에 `aircraft_id`와 `mechanic_id` 두 개의 외래 키가 생긴다고 보면 됩니다. 같은 작업 객체가 항공기 기준 행에도, 정비사 기준 행에도 나타날 수 있으므로 "어느 항공기에서, 누가, 언제"를 한 화면에서 조정할 수 있습니다.

> **중간 요약**: 최소 구성은 정비 작업(Schedule)과 항공기(Resource) 두 객체 타입이며, 정비사처럼 Resource 객체 타입을 더 추가해 "누가 수행하는지"까지 일정에 반영할 수 있습니다.

## 정리

- Dynamic Scheduling 위젯은 최소 두 객체 타입, 즉 일정의 대상인 Schedule 객체와 일정이 배정되는 Resource 객체가 필요합니다.
- Schedule 객체에는 자원 외래 키(String), 시작 시각과 종료 시각(Timestamp) 속성이 필수입니다.
- Schedule 객체 타입은 각 Resource 객체 타입과 링크되어야 하며, 다대일과 다대다를 모두 지원하고 위젯의 **Resource Link Type** 설정으로 구분합니다.
- Resource 객체 타입은 여러 개(예: 항공기와 정비사)를 둘 수 있어 더 복잡한 배정 워크플로를 만들 수 있습니다.
