# 결과 보기 (View results)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/view-results/
- 사이드바 위치: Applications > Object Explorer > Analyze and compare > View results

이 페이지는 Object Explorer에서 탐색(exploration)한 결과 객체들을 표 형태로 보여 주는 Results View의 사용법을 다룹니다. 열 정렬, 열 순서와 너비와 표시 여부 설정, 객체 미리 보기, 시계열 속성 보기, 표 안에서 바로 값을 고치는 인라인 편집(inline edit)까지 설명합니다. 검색과 필터로 좁힌 객체를 실제로 하나씩 확인하고 비교하는 화면이므로 Object Explorer에서 가장 자주 쓰게 되는 부분입니다.

Results View는 탐색에 포함된 객체를 표 형태로 표시합니다. 표에 더 많은 객체를 불러오려면 아래로 스크롤합니다.

![Results View](https://www.palantir.com/docs/resources/foundry/object-explorer/results_view.png)

**설명**: 표의 한 행은 객체 하나, 한 열은 속성(property) 하나에 해당합니다. 데이터베이스에서 `SELECT * FROM flights WHERE ...` 결과를 표로 보는 것과 같은 구조이며, 스크롤할 때마다 다음 행 묶음을 추가로 불러오는 방식(페이지네이션)으로 동작합니다.

<a id="sorting-table-by-column"></a>
## 열 기준으로 표 정렬하기 (Sorting Table by Column)

결과 표는 `Sortable` renderHint가 적용된 속성으로 정렬할 수 있습니다. 특정 열로 정렬하려면 열 헤더의 드롭다운 화살표를 클릭합니다.

![열 옵션](https://www.palantir.com/docs/resources/foundry/object-explorer/results_column_options.png)

**설명**: renderHint는 온톨로지에서 속성마다 지정하는 표시와 인덱싱 관련 힌트입니다. `Sortable` 힌트가 없는 속성은 정렬 기준으로 쓸 수 없으므로, 정렬 메뉴가 보이지 않는다면 Ontology Manager에서 해당 속성의 설정을 확인해야 합니다.

어떤 열이 정렬에 사용되면 그 열의 헤더에 정렬 아이콘이 표시됩니다. 여러 열을 정렬 기준으로 고르면 마지막으로 선택한 열이 우선합니다. 앞서 적용한 정렬에는 아래처럼 정렬 아이콘 옆에 숫자가 붙어 정렬 순서를 보여 줍니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/results_sorts.png" alt="열 정렬" width="600"/>

드롭다운에서 "Clear All Sorts"(모든 정렬 해제)를 선택하면 정렬이 원래 상태로 초기화됩니다.

**설명**: 여러 열 정렬은 SQL의 `ORDER BY a, b`와 같은 다단 정렬입니다. 예를 들어 먼저 `출발 공항`으로 정렬한 뒤 `출발 시각`을 선택하면, 마지막에 고른 `출발 시각`이 1순위가 되고 `출발 공항`은 시각이 같은 행끼리의 2순위 기준이 됩니다.

> **중간 요약**: `Sortable` 힌트가 있는 속성 열은 헤더 드롭다운으로 정렬할 수 있고, 여러 열을 고르면 마지막에 고른 열이 우선합니다. "Clear All Sorts"로 초기화합니다.

<a id="configuring-columns"></a>
## 열 구성하기 (Configuring Columns)

<a id="changing-column-order"></a>
### 열 순서 바꾸기 (Changing Column Order)

열 헤더의 핸들 아이콘을 드래그하면 열 순서를 바꿀 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/results_drag_column_header.png" alt="열 순서 바꾸기" width="300"/>

사용자는 열 헤더 드롭다운에서 "Freeze X columns"(X개 열 고정) 옵션을 선택해, 결과 표를 오른쪽으로 스크롤하는 동안에도 가장 왼쪽 X개 열이 계속 보이게 할 수 있습니다. 체크박스 열도 이 개수에 포함됩니다.

<a id="resizing-columns"></a>
### 열 너비 조절하기 (Resizing Columns)

열 너비를 바꾸려면 열 헤더의 오른쪽 경계를 원하는 너비까지 드래그합니다. 파란색으로 강조되는 이 경계는 설정 드롭다운 바로 오른쪽에 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/results_resize_column.png" alt="열 너비 조절" width="300"/>

<a id="adding-and-removing-columns"></a>
### 열 추가와 제거 (Adding and Removing columns)

개별 열을 숨기려면 열 헤더 드롭다운에서 "Hide this column"(이 열 숨기기)을 선택합니다.

여러 열의 순서와 설정을 한 번에 바꾸려면 "Configure columns"(열 구성)를 선택해 아래 메뉴를 엽니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/results_column_configurator.png" alt="열 구성" height="450"/>

왼쪽 패널은 표의 기본 열을 보여 주고, 오른쪽 패널은 가능한 모든 열의 현재 순서와 표시 여부를 보여 줍니다. 바로 가기 버튼으로 모든 열을 숨기거나 추가할 수 있고, 위쪽 검색창에서 특정 열을 찾아 표시 여부를 전환할 수도 있습니다.

열을 원하는 위치로 드래그해 순서를 바꾸거나, 아래 메뉴를 사용해 열을 맨 위나 맨 아래로 옮길 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/results_column_menu.png" alt="열 메뉴" width="300"/>

"don't truncate text in this table"(이 표에서 텍스트를 자르지 않음)을 선택하면, 텍스트 속성이 현재 열 너비에 다 표시되지 않을 때 다음 줄로 줄바꿈되어 표시됩니다.

오른쪽 아래의 버튼으로 구성을 저장합니다. 관리자는 현재 보기를 새 레이아웃으로 저장하고 이를 모든 사용자의 기본값으로 지정해 이 표의 기본 구성을 바꿀 수 있습니다. [기본 구성 변경에 대해 자세히 알아보기.](../06_configure.md#default-layout-administrative-users)

> **중간 요약**: 열은 드래그로 순서와 너비를 바꾸고, 왼쪽 열을 고정하거나 숨길 수 있습니다. "Configure columns" 메뉴에서 여러 열을 한 번에 정리하고 저장하며, 관리자는 이 구성을 모든 사용자의 기본 레이아웃으로 지정할 수 있습니다.

<a id="previewing-results"></a>
## 결과 미리 보기 (Previewing Results)

어떤 객체의 Object View를 새 Object Explorer 탭에서 열려면 그 객체 행의 Title 열을 클릭합니다. Results 탭 안에서 Object View 미리 보기를 열려면, 해당 행의 체크박스나 다른 열을 클릭해 객체를 하나 이상 선택합니다.

객체를 선택하면 오른쪽에서 Selection Preview(선택 미리 보기) 패널이 열립니다. 이 패널을 닫고 표 전체를 보려면 패널 왼쪽 위의 "collapse"(접기) 아이콘(<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/collapse-icon.png" alt="접기 아이콘" width="25">)을 사용합니다.

![결과 미리 보기](https://www.palantir.com/docs/resources/foundry/object-explorer/results_results_preview.png)

여러 객체를 선택하면 처음 20개 중 어느 것이든 Object View를 미리 볼 수 있으며, 이 객체들은 Object View 위쪽에 카드 목록으로 표시됩니다.

![결과 미리 보기(여러 개 선택)](https://www.palantir.com/docs/resources/foundry/object-explorer/results_results_preview_multiselect.png)

두 객체의 Object View를 한 번에 비교하려면 오른쪽 위 드롭다운에서 "Compare objects"(객체 비교)를 선택합니다.

![결과 비교](https://www.palantir.com/docs/resources/foundry/object-explorer/results_results_preview_compare.png)

**설명**: Object View는 객체 하나의 속성, 연결된 객체, 차트 등을 한 화면에 모아 보여 주는 상세 페이지입니다. 표의 한 행이 데이터의 요약이라면, Object View는 그 행 하나(객체 하나)에 대한 상세 화면입니다.

<a id="viewing-time-series-properties"></a>
### 시계열 속성 보기 (Viewing time series properties)

시계열 속성은 Results View에서 일반 속성과 나란히 볼 수 있습니다. 시계열 속성은 타임스탬프가 붙은 값의 이력을 저장하는 객체 속성입니다. [시계열 속성에 대해 자세히 알아보기.](https://www.palantir.com/docs/foundry/time-series/time-series-concepts-glossary/#time-series-property-tsp)

아래 예에서 Results View는 `Country` 객체를 보여 주며, 이 객체에는 `COVID19 New Tests`, `COVID19 New Deaths`, `COVID19 New Cases`라는 세 개의 시계열 속성이 있습니다. 각 열의 왼쪽에는 시계열의 가장 최근 관측값이, 오른쪽에는 시계열 이력을 시각화한 스파크라인(sparkline)이 표시됩니다.

![Results View의 시간 의존 속성](https://www.palantir.com/docs/resources/foundry/object-explorer/results_time-dependent-property-hubble-results-view.png)

**설명**: 일반 속성은 셀 하나에 값 하나(예: 인구 5,100만)를 저장하지만, 시계열 속성은 `(2021-01-01, 1200), (2021-01-02, 1350), ...`처럼 (시각, 값) 쌍의 목록을 가집니다. 표의 셀 하나에 목록 전체를 다 보여 줄 수 없으므로, 마지막 값과 작은 선 그래프(스파크라인)로 요약해 보여 주는 것입니다.

> **중간 요약**: Title 열을 클릭하면 새 탭에서 Object View가 열리고, 행을 선택하면 오른쪽 패널에서 미리 보기가 열립니다. 여러 객체를 고르면 처음 20개까지 미리 볼 수 있고 두 객체를 나란히 비교할 수도 있습니다. 시계열 속성은 최근 값과 스파크라인으로 표시됩니다.

<a id="inline-edits"></a>
## 인라인 편집 (Inline edits)

![Results View의 인라인 편집](https://www.palantir.com/docs/resources/foundry/object-explorer/results_view_inline_edit.png)

인라인 편집 액션이 설정된 속성은 Object Explorer 결과 페이지에서 직접 편집할 수 있습니다. 사용자가 인라인 편집 액션의 제출 조건(submission criteria)을 충족하면, 값 위에 마우스를 올렸을 때 옆에 펜 아이콘이 나타납니다. 값을 클릭하면 속성 타입에 맞는 편집 가능한 필드가 활성화됩니다. 제출하려면 제출 조건을 다시 통과해야 하며, 그렇지 않으면 제출 버튼을 선택할 수 없습니다.

**설명**: 인라인 편집도 결국 온톨로지의 액션 타입을 실행하는 것입니다. 표의 셀을 고치는 것처럼 보이지만, 내부적으로는 "이 객체의 이 속성을 새 값으로 바꾼다"는 액션이 파라미터와 함께 제출됩니다. 제출 조건은 "이 사용자가 이 객체를 이 값으로 바꿀 수 있는가"를 검사하는 규칙이므로, 편집 버튼을 보여 줄 때 한 번, 새 값으로 제출할 때 한 번 더 검사합니다.

## 정리

- Results View는 탐색 결과 객체를 행 단위 표로 보여 주며, 스크롤하면 더 많은 객체를 불러옵니다.
- `Sortable` renderHint가 있는 속성으로 다단 정렬할 수 있고, 마지막으로 고른 열이 우선합니다.
- 열 순서, 너비, 고정, 숨기기를 조절하고 "Configure columns"에서 일괄 구성할 수 있으며, 관리자는 기본 레이아웃을 지정할 수 있습니다.
- 행을 선택하면 Object View 미리 보기와 두 객체 비교가 가능하고, 시계열 속성은 최근 값과 스파크라인으로 표시됩니다.
- 인라인 편집 액션이 설정된 속성은 제출 조건을 통과하면 표에서 바로 편집할 수 있습니다.
