# Program Scheduling 위젯 구성 (Widget configuration)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/program-scheduling-configuration/
- 사이드바 위치: Applications > Dynamic Scheduling > Program Scheduling widget > Widget configuration

이 페이지는 Program Scheduling 위젯의 구성 항목을 하나씩 설명하는 참조 문서입니다. 타임라인 범위, 데이터 레이어(객체 집합, 시작과 종료 속성, 의존성 속성), 표시 방식, 상호작용(드래그 시 저장 액션), 인터페이스 옵션, 출력 변수 순서로 정리되어 있으며 필수 항목에는 표시가 붙어 있습니다.

Program Scheduling 위젯에는 여러 필수 및 선택 구성 설정이 있습니다. 이 섹션은 그 개요를 보여 주며, 필수 설정에는 따로 표시를 해 두었습니다.

<a id="timeline"></a>
## 타임라인 (Timeline)

* **Start timestamp \[필수]:** 타임라인 축의 시작을 제어하는 타임스탬프 변수를 설정합니다.
* **End timestamp \[필수]:** 타임라인 축의 끝을 제어하는 타임스탬프 변수를 설정합니다.

<a id="input-data-layers"></a>
## 입력 데이터(레이어) (Input data (layers))

여러 레이어를 사용해 하나의 타임라인에 서로 다른 업무 흐름이나 객체 타입을 표현할 수 있습니다. 예를 들어 한 레이어는 프로젝트 작업을 보여 주고, 다른 레이어는 주요 마일스톤을 겹쳐 보여 줄 수 있습니다. 각 레이어는 독립적으로 구성할 수 있습니다.

* **Data(데이터)**
  * **Object set \[필수]:** 이 레이어에 작업이나 이벤트를 제공하는 객체 집합(object set)입니다.
  * **Puck type \[필수]:** 이 레이어 항목의 시각적 유형을 선택합니다. 옵션은 **Standard**, **Background**, **Event**입니다. 각 유형에 대한 설명은 [퍽 종류](01_program-scheduling-overview.md#puck-types) 섹션을 참고하세요.
  * **Start time property \[필수]:** 시작 시각으로 사용할 날짜 또는 타임스탬프 속성(property)을 선택합니다.
  * **End time property:** 종료 시각으로 사용할 날짜 또는 타임스탬프 속성을 선택합니다. Event 퍽에는 이 속성이 필요하지 않습니다.
  * **Dependency property:** Standard 퍽의 경우, 작업 사이의 의존 관계를 정의하는 배열 속성을 선택합니다. 의존성은 타임라인에서 관련 퍽들을 잇는 화살표로 표시됩니다. 자세한 내용은 [의존성](01_program-scheduling-overview.md#dependencies) 섹션을 참고하세요.

* **Display and formatting(표시와 서식)**
  * **Grouping properties:** 표의 행을 정리하고 중첩할 기준이 되는 속성을 하나 이상 선택합니다(예: 프로젝트 이름, 팀, 단계). 각 그룹화 속성마다 정렬 방향을 오름차순이나 내림차순으로 구성할 수 있습니다.
  * **Detail properties:** 사용자가 퍽을 선택할 때 나타나는 상세 카드에 표시할 속성을 선택합니다.
  * **Color:** 타임라인에 퍽을 표시할 때 사용할 색을 선택합니다.
    * **Static:** 이 레이어의 모든 퍽에 단일 색을 지정합니다.
    * **Dynamic:** 속성 값에 따라 다른 색을 적용하는 조건부 서식 규칙을 구성합니다. 예를 들어 상태나 우선순위에 따라 작업 색을 다르게 칠할 수 있습니다.

* **Interactions(상호작용)**
  * **Save handler action:** Standard 퍽과 Event 퍽의 경우, 사용자가 퍽을 드래그하거나 크기를 조정할 때 실행할 액션을 선택합니다. 이 액션은 갱신된 시작 시각과 종료 시각을 받으므로, 일정 변경 사항을 온톨로지(Ontology)에 다시 기록할 수 있습니다. 이 액션은 다음을 파라미터로 받아야 합니다.
    * Schedule 객체
    * 시작 시각
    * 종료 시각

      의존성 화살표를 편집하고 싶다면, 의존성 배열 속성에 대한 파라미터를 추가해야 합니다.

  * **Right-click menu:** 사용자가 퍽을 오른쪽 클릭할 때 나타나는 사용자 지정 컨텍스트 메뉴 항목을 구성합니다. 각 메뉴 항목은 액션이나 Workshop 이벤트를 실행할 수 있습니다.

**설명**: 그룹화 속성을 여러 개 고르면 계층이 생깁니다. 예를 들어 `project`, `phase` 순으로 고르면 "프로젝트 A" 아래에 "설계 단계", "구현 단계" 그룹이 생기고, 그 안에 작업 행이 들어갑니다. SQL의 `GROUP BY project, phase` 결과를 트리로 펼쳐 보여 주는 것과 같은 구조입니다.

> **중간 요약**: 각 레이어는 객체 집합, 퍽 종류, 시작 시각 속성(필수)과 종료 시각 속성, 의존성 속성을 지정하고, 그룹화 속성과 상세 속성, 색상을 정한 뒤, 드래그 시 실행할 저장 핸들러 액션과 오른쪽 클릭 메뉴를 구성합니다.

<a id="interface"></a>
## 인터페이스 (Interface)

* **Expand groups by default:** 활성화하면 위젯이 로드될 때 모든 표 그룹이 펼쳐집니다. 비활성화하면 그룹이 접힌 상태로 시작합니다.
* **Hide arrows by default:** 활성화하면 퍽 사이의 의존성 화살표가 처음에 숨겨집니다. 사용자는 실행 중에 화살표 표시 여부를 전환할 수 있습니다.
* **Show current time indicator:** 현재 날짜와 시각을 나타내는 세로선을 타임라인에 표시합니다.

<a id="output"></a>
## 출력 (Output)

* **Selected object set:** 현재 선택된 객체들을 담는 변경 가능한(mutable) 출력 변수입니다. 이 객체 집합은 현재 모듈 안의 다른 Workshop 위젯에서 사용할 수 있습니다.

## 정리

- 타임라인의 시작과 끝은 필수 타임스탬프 변수로 지정합니다.
- 레이어마다 객체 집합, 퍽 종류, 시작 시각 속성이 필수이고, 종료 시각 속성(Event 퍽은 불필요)과 의존성 배열 속성(Standard 퍽)을 지정할 수 있습니다.
- 그룹화 속성으로 계층형 행 표를 만들고, 상세 속성과 Static 또는 Dynamic 색상을 정합니다.
- 저장 핸들러 액션은 Schedule 객체, 시작 시각, 종료 시각을 받아야 하며, 의존성 편집이 필요하면 의존성 배열 파라미터를 추가합니다.
- 인터페이스 옵션으로 그룹 펼침, 화살표 숨김, 현재 시각 표시를 정하고, 선택된 객체는 출력 변수로 다른 위젯에 전달됩니다.
