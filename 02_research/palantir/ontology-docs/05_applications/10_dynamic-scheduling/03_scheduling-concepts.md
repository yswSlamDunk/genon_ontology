# 핵심 개념 (Core concepts)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-concepts/
- 사이드바 위치: Applications > Dynamic Scheduling > Core concepts

이 페이지는 동적 스케줄링을 이루는 핵심 개념(일정 객체, 자원 객체, 스케줄링 위젯, 시나리오, 저장 액션 핸들러, 제안 함수, 검색 함수, 검증 규칙)을 정의합니다. 이후 페이지들에서 반복해서 나오는 용어이므로 먼저 정확한 뜻을 잡아 두는 것이 좋습니다.

동적 스케줄링은 다음 핵심 개념 위에 만들어집니다.

<a id="schedule-object"></a>
## 일정 객체 (Schedule object)

일정 객체는 작업이나 활동을 온톨로지에서 표현한 것이며, 그 이벤트가 일어나는 시작 시각과 종료 시각, 그리고/또는 예상 소요 시간을 포함해야 합니다.

<a id="resource-object"></a>
## 자원 객체 (Resource object)

자원 객체는 일정 객체가 배정되거나 일정이 잡히는 대상이 되는 모든 엔터티(사람, 장소, 프로젝트 등)를 나타냅니다.

**설명**: 두 개념의 관계는 데이터베이스의 다대일 관계로 볼 수 있습니다. 예를 들어 `Task` 테이블의 행 3개(작업 A 09:00\~10:00, 작업 B 10:00\~12:00, 작업 C 13:00\~14:00)가 모두 `resource_id = M1`(정비사 1번)을 가리키면, 정비사 M1이라는 자원 객체 하나에 일정 객체 세 개가 배정된 상태입니다.

> **중간 요약**: 일정 객체는 시간 정보(시작, 종료, 길이)를 가진 작업이고, 자원 객체는 그 작업이 배정되는 사람, 장소, 프로젝트 같은 대상입니다.

<a id="scheduling-widgets"></a>
## 스케줄링 위젯 (Scheduling widgets)

<a id="scheduling-gantt-chart"></a>
### Scheduling Gantt Chart

Scheduling Gantt Chart는 스케줄링이나 자원 배정 워크플로를 위한 대화형 차트를 그리며, 두 가지 핵심 요소로 이루어집니다.

* **일정 객체(Schedule objects):** 일정 객체(예: 항공기 정비 작업)는 Scheduling Gantt Chart 위에 퍽(puck, 블록)으로 그려집니다. 사용자는 퍽을 드래그 앤 드롭하여 일정 객체의 시작 시각, 종료 시각, 그리고/또는 연결된 자원 객체를 갱신할 수 있습니다.
* **자원 객체(Resource objects):** 자원 객체(예: 항공기 정비사)는 Scheduling Gantt Chart의 행으로 그려집니다. 사용자가 행 위에 마우스를 올리면 자원 객체의 타이틀, 모듈 빌더가 선택한 속성, 그리고 Object View로 가는 링크를 보여 주는 카드가 표시됩니다.

Scheduling Gantt Chart 위젯은 모듈 빌더가 인터페이스 색상과, 일정 객체 퍽의 배정 동작(puck allocation behavior) 및 스냅 동작(snap behavior) 같은 상호작용을 자유롭게 선택할 수 있게 해 줍니다.

자세한 내용은 [Scheduling Gantt Chart 위젯](05_scheduling-gantt-chart-widget.md) 문서를 참고하세요.

<a id="calendar"></a>
### Calendar

Calendar는 `Schedule` 객체를 일, 주, 월, 또는 사용자 지정 보기로 그립니다.

> **중간 요약**: 간트 차트에서는 일정 객체가 퍽, 자원 객체가 행으로 그려지고 드래그 앤 드롭으로 시간과 배정 대상을 바꿀 수 있습니다. Calendar는 일정 객체를 달력 형태로 보여 줍니다.

<a id="scenarios"></a>
## 시나리오 (Scenarios)

[시나리오](../../04_ontology-scenarios/01_overview-ontology-scenario.md)를 사용하면 가정(what-if) 분석을 만들고 비교할 수 있습니다. 시나리오를 사용하면 위젯에서 한 편집이 온톨로지에 바로 기록되지 않습니다. 대신 격리된 샌드박스 안에서 제안된 변경으로 만들어지며, 이를 검토하고 병합(merge)할 수 있습니다.

**설명**: 이는 Git에서 별도 브랜치에 커밋해 두고 검토 후 main에 병합하는 흐름과 같은 구조입니다. 예를 들어 "정비사 한 명이 병가를 내면 일정이 어떻게 바뀌는가"를 시나리오 안에서 여러 안으로 편집해 보고, 실제 데이터에는 고른 안만 반영할 수 있습니다.

<a id="schedule-save-action-handler"></a>
## 일정 저장 액션 핸들러 (Schedule save action handler)

일정 저장 액션 핸들러는 Scheduling Gantt Chart 위젯에서 온톨로지 편집을 실행하는 데 쓰입니다. 사용자가 드래그 앤 드롭으로 퍽을 편집하고 그 변경을 온톨로지에 반영(stage)하려면 이 액션이 반드시 필요합니다. 대부분의 사용 사례에서는 단순한 온톨로지 수정(modify) 액션을 사용할 수 있지만, 고급 워크플로에서는 [함수 기반 사용자 정의 저장 액션](../../02_define-ontologies/03_action-types/11_function-backed-actions/01_function-actions-overview.md)을 사용할 수 있습니다. 함수 기반 액션은 최소한 다음 선택(optional) 파라미터를 받아야 합니다.

* Resource ID (자원 객체를 가리키는 외래 키)
* Start time (시작 시각)
* End time (종료 시각)

<a id="suggestion-function"></a>
## 제안 함수 (Suggestion function)

[제안 함수](07_scheduling-suggestion-functions.md)는 조직이 정의한 로직을 바탕으로 일정 객체를 어떤 위치에 놓는 것이 얼마나 적합한지 알려 줍니다. 사용자가 일정 객체 퍽을 선택하면, 사용자 인터페이스는 규칙 로직에 정의된 조건을 만족하는 일정상의 영역을 강조 표시합니다. 규칙 로직의 출력은 배정이 가능한 영역을 강조하는 데 쓸 수도 있고, 반대로 배정이 불가능한 영역을 강조하는 데 쓸 수도 있습니다. 애플리케이션 빌더는 Workshop 위젯 설정의 옵션으로 이 규칙을 강제할 수 있습니다. 이 기능을 켜면 퍽이 가장 가까운 강조 영역에 놓이도록 강제됩니다.

<a id="search-function"></a>
## 검색 함수 (Search function)

[검색 함수](08_scheduling-search-functions.md)는 "문제 해결사" 역할을 하며, 사용자의 구체적인 필요와 기준에 맞춘 스케줄링 추천을 제공합니다. 이 함수는 목적과 요구 사항에 따라 일정 객체 집합 또는 시간 슬롯 집합을 반환합니다. 검색 함수는 Scheduling Gantt Chart 위젯에서 마우스 오른쪽 버튼을 클릭해 실행합니다. 추천 함수는 항상 현재 상태를 고려하므로, 사용자가 활성 시나리오에서 한 스케줄링 변경도 추천에 반영됩니다.

<a id="validation-rule"></a>
### 검증 규칙 (Validation rule)

[검증 규칙](09_scheduling-validation-rules.md)을 사용하면 스케줄링 제약을 코드로 명시할 수 있으며, 최종 사용자는 자기 워크플로를 규정하는 제한과 제약을 이해한 상태에서 일정을 만들거나 수정할 수 있습니다. 각 검증 규칙은 함수로 뒷받침되며, 이 함수는 배정 객체의 현재 상태가 함수 로직에 정의된 특정 조건을 만족하는지 평가합니다.

**설명**: 세 종류의 함수는 입력과 출력으로 구분하면 쉽습니다. 제안 함수는 "선택한 퍽 하나"를 입력받아 "놓을 수 있는(또는 없는) 시간 영역"을 출력합니다. 검색 함수는 사용자가 요청한 조건을 입력받아 "추천 일정 객체나 시간 슬롯 목록"을 출력합니다. 검증 규칙 함수는 "현재 배정 상태"를 입력받아 "조건을 만족하는지 여부"를 출력합니다(예: 정비사 M1의 작업 시간이 겹치면 위반).

> **중간 요약**: 저장 액션 핸들러는 드래그 앤 드롭 편집을 온톨로지에 반영하는 액션입니다. 제안 함수는 놓을 수 있는 영역을 강조하고, 검색 함수는 추천을 반환하며, 검증 규칙은 제약 위반 여부를 평가합니다.

## 정리

- 일정 객체는 시간 정보를 가진 작업, 자원 객체는 그 작업이 배정되는 대상입니다.
- Scheduling Gantt Chart는 일정 객체를 퍽, 자원 객체를 행으로 그리며, Calendar는 일정 객체를 달력 보기로 보여 줍니다.
- 시나리오는 편집을 샌드박스에 모아 검토 후 병합하게 해 줍니다.
- 저장 액션 핸들러(Resource ID, Start time, End time 선택 파라미터)는 드래그 앤 드롭 편집에 필수입니다.
- 제안 함수, 검색 함수, 검증 규칙은 각각 배치 가능 영역 표시, 추천 생성, 제약 검사를 담당합니다.
