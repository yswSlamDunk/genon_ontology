# 차트로 탐색하기 (Explore with charts)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/explore-charts/
- 사이드바 위치: Applications > Object Explorer > Analyze and compare > Explore with charts

이 페이지는 Object Explorer의 Explore 화면에서 차트를 이용해 객체를 집계하고 필터링하는 방법을 설명합니다. 차트를 추가, 삭제, 재배치하는 방법, 링크된 객체의 속성으로 만드는 차트, 속성 타입별 차트 종류(리스토그램, 파이 차트, 히스토그램, 그리드 플롯, 통계, 지도), 실행 취소, 레이아웃 저장, 미리 보기 패널을 다룹니다.

탐색할 객체 타입을 선택하면 Explore 화면(perspective)에 검색과 필터링을 위한 차트가 표시됩니다.

![새 탐색](https://www.palantir.com/docs/resources/foundry/object-explorer/exploration_flights.png)

<a id="charts"></a>
## 차트 (Charts)

차트는 Object Explorer 안에서 필터링하는 사용자가 주로 상호 작용하는 지점입니다. 각 차트는 기본 객체 타입 또는 링크된 객체 타입의 속성 필드 하나를 집계한 것을 나타냅니다. 기본적으로 선택한 객체 타입의 주요(prominent) 속성마다 차트가 하나씩 표시됩니다. 하지만 사용자는 이를 바꿔 [자신의 기본 레이아웃을 저장](#saving-a-layout)할 수 있고, 관리자는 [모든 사용자를 위한 전역 기본 레이아웃을 저장](../06_configure.md#default-layout-administrative-users)할 수 있습니다.

**설명**: 차트 하나는 SQL의 `GROUP BY` 집계 결과 하나에 해당합니다. 예를 들어 Flight 객체 타입의 `origin` 속성 차트는 `SELECT origin, COUNT(*) FROM flights GROUP BY origin`의 결과를 막대로 보여 줍니다. 차트에서 값을 클릭하면 그 값이 `WHERE` 조건으로 추가되어 다른 차트들도 함께 다시 계산됩니다.

<a id="adding-removing-and-ordering-charts"></a>
### 차트 추가, 삭제, 정렬하기 (Adding, Removing, and Ordering Charts)

현재 화면 아래쪽의 **Add chart** 카드를 클릭해 탐색에 차트를 추가합니다. 그러면 선택한 객체 타입과 링크된 객체의 속성을 찾는 검색 창이 열립니다. 집계할 속성을 선택하면 차트가 탐색에 나타나고 **Add chart** 카드는 한 칸 아래로 이동합니다.

또는 탐색의 검색 창에 있는 필터에서 차트를 추가할 수도 있습니다. 검색 창에서 새 필터를 추가하는 동안 **Add chart to view** 버튼이 나타납니다. 이 버튼을 선택하면 탐색 레이아웃의 첫 번째 위치에 차트가 추가됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_add_chart_dropdown.png" alt="차트 추가"/>

차트를 삭제하려면 탐색에서 차트 머리글 위에 마우스를 올립니다. **X** 아이콘이 나타나며, 이를 클릭하면 화면에서 차트가 제거되지만 검색의 필터는 제거되지 않습니다.

<img alt="차트 삭제" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_remove_chart.png" height="400"/>

차트는 끌어서 놓기로 순서와 크기를 바꿀 수 있습니다. 차트 머리글의 빈 공간을 클릭한 채로 있으면 차트 순서를 바꾸는 인터페이스가 나타납니다. 레이아웃에서 차트를 옮기면 다른 차트들이 이동하여 비워진 공간을 채웁니다.

<img alt="차트 순서 바꾸기" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_reorder_chart.png" height="400"/>

차트의 가로 크기를 조정하려면 가장자리 하나를 클릭한 채로 끌어 줄이거나 늘립니다. 각 차트는 탐색 레이아웃의 열 하나 또는 두 열 모두를 채울 수 있습니다.

<img alt="가로 크기 조정" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_resize_chart_horizontal.png" height="400"/>

리스토그램(Listogram) 차트에 값이 다섯 개보다 많으면 **Show more**와 **Show less**를 클릭해 차트의 세로 크기를 조정합니다.

<img alt="세로 크기 조정" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_resize_chart_vertical.png" height="400"/>

<a id="charts-on-linked-objects"></a>
### 링크된 객체에 대한 차트 (Charts on Linked Objects)

링크된 객체의 속성으로 필터링하려면 검색 메뉴 왼쪽에서 링크된 객체 타입을 선택합니다.

<img alt="add_linked_property.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_add_linked_property.png" />

탐색 화면에서 차트 머리글은 그 차트가 링크된 객체의 속성으로 필터링한다는 것을 표시합니다. 첨부된 예시에서 위의 두 차트는 선택한 타입의 속성으로, 아래의 두 차트는 링크된 객체의 속성으로 필터링합니다.

<img alt="linked_property_charts.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_linked_property_charts.png" height="400"/>

**설명**: 링크된 객체 차트는 조인 후 집계에 해당합니다. Flight 탐색에서 Aircraft의 `manufacturer` 차트를 추가하면 `SELECT a.manufacturer, COUNT(*) FROM flights f JOIN aircraft a ON f.aircraft_id = a.aircraft_id GROUP BY a.manufacturer`처럼 "제조사별 항공편 수"를 보여 주고, 그 값을 클릭하면 Flight 객체 집합이 그 조건으로 걸러집니다.

> **중간 요약**: 각 차트는 기본 객체 타입이나 링크된 객체 타입의 속성 하나를 집계한 것입니다. **Add chart** 카드나 검색 창의 **Add chart to view**로 추가하고, 머리글의 **X**로 제거(필터는 유지)하며, 끌어서 순서와 크기를 바꿉니다.

<a id="types-of-charts"></a>
## 차트 종류 (Types of Charts)

Object Explorer는 속성 타입에 따라 여러 종류의 차트를 지원합니다. 아래는 각 종류의 요약과 예시입니다.

<a id="listogram"></a>
### 리스토그램 (Listogram)

리스토그램은 숫자가 아닌 속성에 대한 집계를 표시합니다. String, Boolean, Array 속성에 적용됩니다. 이 예시에서 차트는 Employee의 모든 First Name을 나열하고, 그 이름을 가진 Employee 수를 함께 보여 줍니다.

<img alt="listogram.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_listogram.png" height="300"/>

리스토그램은 숫자 속성을 집계한 값과 함께 속성을 표시할 수도 있습니다. 예를 들어 주(state)별로 사업 가맹점의 평균 매출을 보여 줄 수 있습니다.

리스토그램 구성에는 다음이 포함됩니다.

* 집계 유형(Aggregation type)
  * 예를 들어 공항별 *항공편* 수 대신 *비행 시간*의 *평균*을 보여 줍니다.
* 정렬 유형과 방향(Sort type and direction)
  * 예를 들어 개수 오름차순으로 정렬하거나, 속성 값의 알파벳순으로 정렬합니다.

<img alt="listogram_controls.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_listogram_controls.png" height="300"/>

리스토그램으로 필터링하려면 필터링할 값을 클릭합니다. 차트 아래쪽의 드롭다운으로 선택한 값을 유지(keep)하거나 제외(exclude)할 수 있습니다.

<img alt="listogram_select.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_listogram_select.png" height="300"/>

**설명**: 집계 유형을 바꾸는 것은 `COUNT(*)`를 다른 집계 함수로 바꾸는 것입니다. "공항별 평균 비행 시간"은 `SELECT origin, AVG(flight_time) FROM flights GROUP BY origin`입니다. 값 유지는 `WHERE origin IN (...)`, 제외는 `WHERE origin NOT IN (...)`에 해당합니다.

<a id="pie-chart"></a>
### 파이 차트 (Pie Chart)

숫자가 아닌 속성(불리언과 문자열)은 파이 차트로도 표시할 수 있습니다. 차트 구성 옵션에서 **Pie Chart** 옵션을 선택하세요.

<img alt="pie_chart.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_pie_chart.png" height="300"/>

<img alt="pie_chart_configuration.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_pie_chart_configuration.png" height="300"/>

<a id="histogram"></a>
### 히스토그램 (Histogram)

히스토그램은 숫자나 날짜 속성에 대한 막대 차트 집계를 표시합니다.

<img alt="histogram.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_histogram.png" />

히스토그램 차트는 관련 데이터 전체가 들어가도록 크기가 조정되고, 선택하기 쉽도록 자동으로 구간(bucket)을 나눕니다. 추가 구성은 필요 없습니다. 필터링하려면 특정 구간을 선택하거나(왼쪽 그림), 클릭한 채 끌어서 원하는 범위를 선택합니다(오른쪽 그림). 범위의 시작점과 끝점은 차트 아래쪽 입력란에서 편집합니다.

<img alt="histogram_select.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_histogram_select.png" />

**설명**: 구간 나누기(bucketing)는 연속된 값을 일정한 폭의 범위로 묶는 것입니다. 예를 들어 비행 시간 0\~600분을 60분 폭으로 묶으면 10개 구간이 생기고, 각 구간에 속한 항공편 수가 막대 높이가 됩니다. 범위를 끌어서 선택하면 `WHERE flight_time BETWEEN 120 AND 240` 같은 조건이 만들어집니다.

<a id="grid-plots"></a>
### 그리드 플롯 (Grid Plots)

그리드 플롯은 두 속성에 대한 색상 차트를 보여 줍니다. 선택한 속성은 X축에, 다른 **Group By** 속성은 Y축에 놓입니다.

<img alt="grid_plot.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_grid_plot.png" height="300"/>

차트 구성을 열어 축, 정렬 정보, 색상 스케일을 수정할 수 있습니다.

<img alt="grid_plot_config.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_grid_plot_config.png" height="300"/>

그리드 플롯으로 필터링하려면 그리드의 한 칸을 클릭합니다. `ctrl` 또는 `command`를 누른 채로 클릭하면 연속된 범위의 여러 옵션을 선택할 수 있습니다.

**설명**: 그리드 플롯은 `GROUP BY x, y`로 두 속성의 조합마다 개수를 세고, 그 개수를 칸의 색 진하기로 표시하는 히트맵입니다. 예를 들어 X축이 출발 공항, Y축이 요일이면 "월요일 JFK 출발 항공편 수" 같은 값이 한 칸이 됩니다.

<a id="single-statistic"></a>
### 단일 통계 (Single Statistic)

단일 통계 차트는 객체 집합에 대해 숫자 속성 하나의 집계 값을 보여 줍니다. 속성과 집계 유형(Sum, Average, Min, Max, Count, Unique Count)을 선택합니다. 이 차트는 필터링에 사용할 수 없습니다.

<img alt="single_statistic.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_single_statistic.png" height="300"/>

<a id="statistics-table"></a>
### 통계 표 (Statistics Table)

통계 표는 숫자 속성의 집계를 다른 속성으로 그룹화하여 정렬 가능한 표로 보여 줍니다. 사용할 수 있는 집계는 Sum, Min, Max, Average, Count입니다.

<img alt="summary_statistics.png" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_summary_statistics.png" height="300"/>

구성 옵션에는 표시할 지표, 그룹화할 속성, 표 아래쪽에 요약 행 표시 여부가 포함됩니다.

필터링하려면 원하는 그룹화 속성 값의 행을 선택합니다.

<a id="maps"></a>
### 지도 (Maps)

**클러스터 지도 (Cluster Map)**

**geopoint** 타입 속성의 기본 차트는 클러스터 지도로, 객체 수 또는 다른 집계 결과를 크기가 조정된 버블로 보여 줍니다.

<img alt="클러스터 지도" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_cluster_map.png"/>

구성 옵션에서 수행할 집계 유형과 집계 대상 속성을 바꿀 수 있습니다(예: 공항 수 대신 각 지역 안에서 출발하는 항공편 수의 합계를 표시).

<img alt="클러스터 지도 옵션" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_cluster_map_option.png"/>

이 버블들을 클릭한 다음 지도 아래의 **apply filter**를 클릭하면 지리 공간적으로 필터링할 수 있습니다.

**단계 구분도 (Choropleth Map)**

온톨로지에서 타입 클래스(typeclass)로 주석이 달린 일부 텍스트 속성은 아래와 같은 단계 구분도(choropleth map)를 만드는 데 사용할 수 있습니다.

<img alt="단계 구분도" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_choropleth_map.png"/>

단계 구분도는 지도에 표시할 수 있는 지리적 지역 값(예: 국가 코드)을 담은 모든 속성 타입에 대해 만들 수 있습니다. 필요한 타입 클래스의 `kind`는 `choropleth_map_config_id`이고, `name`은 속성이 담고 있는 지역 코드 종류에 따라 다릅니다. 예를 들면 다음과 같습니다.

* 국가에는 `countries`를 사용합니다.
* 미국 주(US States)에는 `us_states`를 사용합니다.
* 미국 카운티(US Counties)에는 `us_counties`를 사용합니다.
* 미국 우편번호(US Zip Codes)에는 `us_zip_codes`를 사용합니다.

추가 지역 경계 옵션이나 이 타입 클래스 추가에 대한 도움이 필요하면 Palantir 담당자에게 문의하세요.

구성 옵션에는 집계 유형과 사용할 색상 스케일 변경이 포함됩니다.

<img alt="단계 구분도 구성" src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_choropleth_map_option.png"/>

**설명**: 단계 구분도는 국가나 주처럼 경계가 정해진 지역을 집계 값에 따라 다른 색으로 칠한 지도입니다. 속성 값이 "KR", "US" 같은 문자열일 뿐이면 시스템은 그것이 국가 코드인지 알 수 없으므로, 타입 클래스라는 메타데이터로 "이 속성은 `countries` 종류의 지역 코드다"라고 표시해 주어야 지도의 어느 영역과 연결할지 결정할 수 있습니다.

> **중간 요약**: 문자열, 불리언, 배열 속성에는 리스토그램과 파이 차트, 숫자와 날짜 속성에는 히스토그램, 두 속성 조합에는 그리드 플롯, 숫자 집계에는 단일 통계(필터 불가)와 통계 표, geopoint에는 클러스터 지도, 타입 클래스가 달린 지역 코드에는 단계 구분도를 씁니다.

<a id="undoing-and-redoing-changes-to-your-exploration"></a>
## 탐색 변경 사항 실행 취소와 다시 실행 (Undoing and redoing changes to your exploration)

탐색에 대한 변경을 실행 취소하거나 다시 실행하려면 화면(perspective) 막대 왼쪽의 버튼을 사용합니다. 현재 최근 5개의 탐색 상태가 실행 취소와 다시 실행을 위해 저장됩니다. 실행 취소할 수 있는 작업은 다음과 같습니다.

* 검색 창이나 차트에서 필터 편집
* 차트 레이아웃 변경(새 차트 추가 또는 기존 차트 순서 변경)
* 탐색 화면(perspective) 변경
* 탐색을 링크된 객체 타입으로 피벗(pivot)

<img alt="실행 취소와 다시 실행" src="https://www.palantir.com/docs/resources/foundry/object-explorer/undo_redo.png"/>

**설명**: 피벗(pivot)은 현재 객체 집합에서 링크를 따라 연결된 다른 객체 타입의 객체 집합으로 탐색 대상을 바꾸는 것입니다. 예를 들어 "지연된 Flight 120건"에서 Aircraft로 피벗하면 "그 항공편들에 쓰인 Aircraft 객체 집합"을 탐색하게 됩니다.

<a id="saving-a-layout"></a>
## 레이아웃 저장하기 (Saving a Layout)

레이아웃을 사용하면 특정 객체 타입에 대해 공유 가능한 화면을 만들 수 있습니다. 공유 가능한 화면에는 추가된 차트, 표의 열 구성, 표의 정렬 구성이 포함됩니다.

레이아웃을 저장하려면 화면 왼쪽 위의 레이아웃 선택기(**A**)를 열고 **Save current view (e.g. charts, sorts, etc.) as new layout**(현재 화면을 새 레이아웃으로 저장, **B**)을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/open_layout_selector.png" alt="레이아웃 선택" width="300"/>

나타나는 팝업에서 **Initial Perspective**(**C**)를 설정합니다. 이는 레이아웃이 처음에 Explore 탭(차트)을 열지 Results 탭(표)을 열지 결정합니다. **Set as default layout for** 아래의 **For yourself**(**D**) 상자를 체크하면 이 레이아웃을 이 객체 타입에 대한 개인 기본 레이아웃으로 설정할 수도 있습니다. 그러면 이 객체 타입으로 새 탐색을 시작할 때마다 이 레이아웃이 기본으로 선택됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/edit_layout_dialog.png" alt="레이아웃 편집" width="300"/>

[관리 사용자(administrative user)](../06_configure.md#default-layout-administrative-users)라면 **Set as default layout for** 아래의 **For all users** 체크 상자(**E**)를 체크하여 레이아웃을 모든 사용자의 전역 기본 레이아웃으로 설정할 수 있습니다.

개별 사용자가 어떤 객체 타입에 대해 자신의 기본 레이아웃을 설정하면, 그 레이아웃이 설정된 전역 기본 레이아웃보다 우선합니다.

사용자는 아래에 보이는 하위 메뉴(**F**)를 사용해 기존 레이아웃을 특정 객체 타입에 대한 자신의 기본 레이아웃으로 설정할 수도 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/user_save_default_layout.png" alt="자신의 기본 레이아웃 설정" width="300"/>

> **중간 요약**: 실행 취소와 다시 실행은 최근 5개 탐색 상태까지 지원하며 필터, 레이아웃, 화면 전환, 피벗이 대상입니다. 레이아웃은 차트, 열, 정렬 구성을 저장한 공유 가능한 화면으로, 개인 기본값(**For yourself**)과 관리자용 전역 기본값(**For all users**)을 지정할 수 있고 개인 기본값이 우선합니다.

<a id="preview-panel"></a>
## 미리 보기 패널 (Preview Panel)

탐색 화면 오른쪽에는 최대 20개 결과 목록이 탐색 내용의 미리 보기로 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/preview_table.png" alt="미리 보기 표 정렬" height="400"/>

미리 보기 카드를 클릭하면 Object View 탭에서 객체가 열립니다. 속성 하나로 정렬하려면 미리 보기 목록 부제목의 **Sort by** 옵션을 사용합니다. 여러 속성으로 정렬하려면 머리글 위에 마우스를 올리고 그림에 보이는 톱니바퀴 아이콘을 선택합니다. 그러면 여러 속성으로 정렬을 구성하는 대화 상자가 열리며, 정렬은 지정한 순서대로 적용됩니다.

**설명**: 여러 속성 정렬은 SQL의 `ORDER BY departure_date DESC, flight_id ASC`와 같습니다. 첫 번째 속성으로 먼저 정렬하고, 값이 같은 객체끼리만 두 번째 속성으로 정렬합니다.

## 정리

- Explore 화면의 차트는 기본 객체 타입이나 링크된 객체 타입의 속성 하나를 집계한 것이며, 클릭으로 필터를 만듭니다.
- 차트는 추가, 제거(필터는 유지), 끌어서 순서와 크기 조정이 가능합니다.
- 속성 타입에 따라 리스토그램, 파이 차트, 히스토그램, 그리드 플롯, 단일 통계, 통계 표, 클러스터 지도, 단계 구분도(타입 클래스 필요)를 사용합니다.
- 최근 5개 탐색 상태까지 실행 취소할 수 있고, 레이아웃을 저장해 개인 또는 전역 기본값으로 지정할 수 있습니다(개인 기본값 우선).
- 오른쪽 미리 보기 패널은 최대 20개 결과를 보여 주며, 단일 또는 다중 속성 정렬을 지원합니다.
