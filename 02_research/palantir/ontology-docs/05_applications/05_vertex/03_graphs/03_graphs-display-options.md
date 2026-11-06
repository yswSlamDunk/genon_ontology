# 객체와 간선 표시 옵션 (Object and edge display options)

- 원문: https://www.palantir.com/docs/foundry/vertex/graphs-display-options/
- 사이드바 위치: Applications > Vertex > Graphs > Object and edge display options

이 페이지는 Vertex 그래프의 겉모습을 정하는 방법을 다룹니다. 노드를 자동으로 배치하는 레이아웃 종류와 그 세부 파라미터, 여러 객체를 하나의 노드나 간선으로 묶는 그룹화, 객체 타입별 레이어 스타일(색, 레이블, 배지, 선 굵기 등), 링크 방향 설정, 그리고 선택한 객체 묶음을 저장하는 저장된 선택(saved selection)을 설명합니다.

Vertex에서는 그래프의 객체와 간선(edge)에 동적 스타일을 구성할 수 있습니다. 스타일을 설정하고 핵심 속성(property) 표시값을 구성한 뒤에는 시간 선택 창을 사용해 이 핵심 속성이 시간에 따라 어떻게 바뀌는지 볼 수 있습니다.

**설명**: 그래프 자료구조에서 노드(node)는 점, 간선(edge)은 두 노드를 잇는 선입니다. Vertex에서 노드는 보통 객체(또는 객체 묶음)이고, 간선은 링크 타입으로 연결된 두 객체 사이의 관계입니다.

<a id="graph-layout"></a>
## 그래프 레이아웃 (Graph layout)

<a id="automatic-layout-options"></a>
### 자동 레이아웃 옵션 (Automatic layout options)

작업 공간 위쪽 도구 모음에서 미리 정의된 여러 레이아웃 옵션을 찾을 수 있습니다. 하나를 선택하면 객체와 간선이 자동으로 움직여, 관계를 탐색하면서 그래프를 정돈할 수 있습니다. 이 레이아웃 중 다수는 동작을 바꾸는 고급 파라미터를 가지고 있습니다. 이 파라미터는 해당 레이아웃 옆의 톱니바퀴 아이콘을 선택해 열 수 있습니다.

![레이아웃 옵션과 오른쪽의 톱니바퀴 아이콘이 있는 "Layout" 드롭다운.](https://www.palantir.com/docs/resources/foundry/vertex/styling_layout_1.png)

아래는 각 레이아웃의 고급 파라미터입니다. 고급 파라미터가 없는 **Auto**와 **Circular** 레이아웃은 제외했습니다.

<a id="hierarchy-left-to-righttop-to-bottom"></a>
#### Hierarchy (Left to Right/Top to Bottom) (계층형: 왼쪽에서 오른쪽/위에서 아래)

* **Reverse:** 계층의 순서를 뒤집습니다. 왼쪽에서 오른쪽은 오른쪽에서 왼쪽이 되고, 위에서 아래는 아래에서 위가 됩니다.
* **Root nodes:** 계층의 루트를 차지할 노드를 고릅니다. `Automatic`을 선택하면 간선 방향을 바탕으로 루트 노드가 자동으로 선택됩니다.

**설명**: 계층형 레이아웃은 트리 자료구조를 그리는 방식입니다. 간선 방향을 부모에서 자식으로 보고, 루트 노드를 첫 줄에 두고 그 자식을 다음 줄에 두는 식으로 배치합니다. 예를 들어 Plant 객체에서 Line 객체 2개로, 각 Line에서 Machine 객체 3개로 간선이 있으면 Plant, Line, Machine 순서로 세 층이 생깁니다.

<a id="grid"></a>
#### Grid (격자)

* **Staggered:** 홀수 행의 요소를 엇갈리게 배치하는 옵션을 제공합니다.
* **Grid dimensions:** 격자의 행 수나 열 수에 대한 제약을 지정합니다. `Automatic` 모드는 행과 열의 수를 같게 하려고 시도합니다.

<a id="horizontal-rowvertical-column"></a>
#### Horizontal Row/Vertical Column (가로 행/세로 열)

* **Order by:** 노드를 정렬할 기준 객체 속성입니다.
  * 기본적으로 오름차순을 사용합니다.
  * `Order by` 속성을 선택하지 않으면, 레이아웃은 행일 때는 기존의 가로 노드 순서를, 열일 때는 기존의 세로 노드 순서를 유지합니다.
  * 그룹화된 노드와, 지정한 속성을 가지지 않은 객체로 백킹된 노드는 오름차순일 때 맨 앞에, 내림차순일 때 맨 뒤에 놓입니다.
  * 이 선택 목록에는 숫자 속성만 나타납니다.
  * 서로 다른 객체에서 이름이 같은 속성은 함께 정렬됩니다.
* **Reverse:** 정렬 순서를 오름차순과 내림차순 사이에서 전환합니다. 이 옵션은 `Order by` 속성을 선택했을 때만 나타납니다.

**설명**: "속성이 없는 노드는 오름차순일 때 맨 앞"이라는 규칙은 SQL에서 값이 없는(NULL) 행을 `ORDER BY ... ASC NULLS FIRST`로 정렬하는 것과 같은 결과입니다. 예를 들어 Flight 노드 3개의 `delay_minutes`가 `15`, 없음, `5`이면 오름차순 결과는 없음, `5`, `15` 순서입니다.

<a id="radial"></a>
#### Radial (방사형)

* **Central node:** 레이아웃 중심에 나타날 노드를 지정합니다.
* **Density:** 노드 사이 간격을 정하는 1에서 5 사이(양 끝 포함)의 값입니다.

<a id="cluster"></a>
#### Cluster (클러스터)

* **Cluster by:** 노드를 클러스터로 묶을 기준 속성을 지정합니다.
  * 속성을 선택하지 않으면 이 레이아웃은 객체 타입별로 클러스터를 만듭니다.
  * 그룹화된 노드와, 선택한 속성을 가지지 않은 객체로 백킹된 노드는 함께 하나의 클러스터로 묶입니다.
  * 이 드롭다운에는 [렌더 힌트(render hints)](../../../02_define-ontologies/02_object-and-link-types/09_metadata/02_metadata-render-hints.md) `Selectable` 또는 `Low Cardinality`가 설정된 속성만 나타납니다.
  * 서로 다른 객체에서 이름이 같은 속성은 함께 클러스터로 묶입니다.

**설명**: 렌더 힌트는 온톨로지에서 속성에 붙이는 표시용 메타데이터입니다. `Low Cardinality`는 "서로 다른 값의 개수가 적다"는 뜻입니다. 예를 들어 `status` 속성의 값이 `Open`, `Closed`, `Pending` 세 가지뿐이면 클러스터도 세 개로 깔끔하게 나뉘지만, 값이 행마다 다른 `id` 속성으로 클러스터를 만들면 노드 수만큼 클러스터가 생겨 의미가 없습니다. 그래서 이런 힌트가 있는 속성만 고를 수 있게 한 것입니다.

<a id="cartesian"></a>
#### Cartesian (직교 좌표)

* **X/Y property:** 레이아웃에서 노드의 x 좌표와 y 좌표로 사용할 속성입니다.
  * 레이아웃을 실행할 때 노드가 뷰포트 안에 들어가도록 좌표가 정규화됩니다.
  * x 속성, y 속성, 또는 둘 다를 선택하지 않으면 직교 좌표 레이아웃은 실행되지 않습니다.
  * 그룹화된 노드와, 선택한 속성을 가지지 않은 객체로 백킹된 노드는 레이아웃 실행 전 위치에 그대로 남습니다.
  * 이 드롭다운에는 [렌더 힌트](../../../02_define-ontologies/02_object-and-link-types/09_metadata/02_metadata-render-hints.md) `Selectable` 또는 `Low Cardinality`가 설정된 속성만 나타납니다.
  * 서로 다른 객체에서 이름이 같은 속성은 함께 정렬됩니다.
* **X/Y reverse:** x 좌표와 y 좌표를 뒤집습니다. reverse 토글은 속성을 선택한 뒤에만 나타납니다.

**설명**: 정규화는 값의 범위를 화면 크기에 맞게 바꾸는 계산입니다. 예를 들어 Airport 객체의 `longitude`를 x 속성, `latitude`를 y 속성으로 고르면, 경도 -122에서 -73 사이 값이 화면 왼쪽 끝에서 오른쪽 끝 사이로 비례 변환되어 공항이 지도와 비슷한 위치에 놓입니다.

> **중간 요약**: 도구 모음에서 Auto, Circular, Hierarchy, Grid, Horizontal Row/Vertical Column, Radial, Cluster, Cartesian 레이아웃을 고를 수 있고, 대부분 톱니바퀴 아이콘으로 방향, 정렬 기준, 중심 노드, 클러스터 기준, 좌표 속성 같은 고급 파라미터를 조정합니다.

<a id="group-nodes-by-object-type"></a>
### 객체 타입별로 노드 그룹화하기 (Group nodes by object type)

관련 객체를 더 많이 추가하다 보면 객체 여러 개를 그래프에서 하나의 노드로 묶고 싶을 수 있습니다. 묶을 객체를 선택한 다음 작업 공간 위쪽의 레이아웃 도구 모음을 사용해 선택한 객체를 그룹화하거나 그룹 해제합니다.

여러 객체를 하나의 노드로 그룹화하면, 작업 공간 왼쪽의 선택 패널에서 그룹에 포함된 객체의 전체 목록을 볼 수 있습니다. 노드 안의 객체 중 일부만 그룹 해제하고 싶다면, 아래처럼 선택 패널에서 해당 객체를 선택하고 **Ungroup**을 고릅니다. 히스토그램의 **Filter to** 기능을 사용해도 같은 작업을 할 수 있습니다.

![노드 그룹화](https://www.palantir.com/docs/resources/foundry/vertex/styling_group_nodes_1.jpg)

<a id="group-by-a-property-of-the-object-type"></a>
### 객체 타입의 속성으로 그룹화하기 (Group by a property of the object type)

히스토그램을 사용하면 선택한 객체의 속성을 탐색할 수 있고, 표시된 값을 기준으로 객체를 그룹화할 수도 있습니다. 이렇게 하면 새 그룹을 반영해 그래프의 객체 배치가 바뀝니다.

![속성으로 그룹화](https://www.palantir.com/docs/resources/foundry/vertex/styling_group_by_property.jpg)

**설명**: 속성 기준 그룹화는 SQL의 `GROUP BY`와 같은 결과를 그래프로 보여 줍니다. 예를 들어 Flight 객체 50개를 `carrier` 속성으로 그룹화하면 `AA`, `DL`, `UA` 같은 값마다 노드 하나가 생기고, 각 노드에 해당 항공사의 항공편이 묶입니다.

<a id="group-nodes-into-edge"></a>
### 노드를 간선으로 그룹화하기 (Group nodes into edge)

어떤 객체는 거래(transaction) 성격을 띠며 시스템 안의 다른 노드나 객체 사이를 오갑니다. 예를 들어 Flight는 거래성 객체로서 `Departure Airport`와 `Destination Airport` 사이를 이동합니다. 이 경우 이런 객체를 간선 위로 그룹화할 수 있으며, 핵심 속성이나 지표를 기준으로 간선 스타일을 지정할 수 있습니다.

Ontology Manager의 Capabilities 탭에서 거래성 객체를 관련 간선으로 자동 그룹화하도록 설정할 수 있습니다. [링크 병합(link merging)에 대해 자세히 알아보세요.](../06_configuration/02_link-merging.md)

간선을 선택하고 오른쪽 클릭 메뉴에서 **Ungroup**을 선택하면 간선에 묶여 있던 모든 객체가 표시됩니다. 또는 히스토그램이나 선택 패널로 그룹 해제할 객체를 먼저 선택해 일부만 그룹 해제할 수도 있습니다.

![간선으로 그룹화](https://www.palantir.com/docs/resources/foundry/vertex/styling_group_edge.jpg)

**설명**: 그룹화하지 않으면 JFK 노드, Flight 노드 30개, LAX 노드가 있고 JFK와 각 Flight, 각 Flight와 LAX 사이에 간선이 60개 그려집니다. Flight를 간선으로 그룹화하면 JFK와 LAX 사이에 간선 하나만 남고, 그 간선이 Flight 30개를 담습니다. 이렇게 하면 간선의 굵기나 레이블로 "이 노선의 항공편 수" 같은 집계 값을 보여 줄 수 있습니다.

> **중간 요약**: 여러 객체를 하나의 노드로 묶거나(타입별, 속성 값별), 두 객체 사이를 오가는 거래성 객체를 간선 하나로 묶을 수 있으며, **Ungroup**으로 전체나 일부를 다시 풀 수 있습니다.

<a id="layer-styling-options"></a>
## 레이어 스타일 옵션 (Layer styling options)

레이어(layer)는 같은 객체 타입의 객체 노드들, 또는 노드 사이의 간선 관계를 가리킵니다. 각 레이어는 여러 레이아웃 옵션으로 개별 구성할 수 있어, 시스템의 디지털 트윈을 유연하게 시각화하고 직관적으로 상호 작용할 수 있습니다.

왼쪽 사이드바의 레이어 스타일 패널을 사용하면 노드와 간선을 개별적으로 스타일 지정하거나, 객체의 속성 및 관련 시계열(time series)이나 측정값에 따라 스타일을 지정할 수 있습니다. 레이어 스타일을 사용하면 핵심 정보를 시각화하고, 지표를 계산하고, 파라미터화된 조건에 따라 스타일을 지정해 현재 시스템 상태나 시뮬레이션된 시스템 상태를 보여 줄 수 있습니다.

<a id="object-styling"></a>
### 객체 스타일 (Object styling)

구성하려는 객체 타입 옆의 **Styling Options**를 선택해 스타일 메뉴를 엽니다.

![객체 스타일 패널](https://www.palantir.com/docs/resources/foundry/vertex/styling_object_styling_panel.jpg)

<a id="color-by"></a>
#### 색 기준 (Color by)

**Fill Color** 드롭다운을 선택해, 이 레이어의 모든 객체에 대해 스타일 기준이 될 파라미터와 색을 고릅니다. 시계열 측정값을 **Color by** 파라미터로 선택할 수 있으며, 이 경우 선택한 시간 창에 따라 스타일이 동적으로 갱신됩니다. [파생 속성 함수](08_derive-property-functions.md)를 사용해 노드에 색을 지정할 수도 있습니다.

![색 기준](https://www.palantir.com/docs/resources/foundry/vertex/styling_color_by.jpg)

**설명**: 시계열은 시각별 값의 목록입니다. 예를 들어 Pump 객체의 `pressure` 시계열이 `[(08:00, 3.1), (09:00, 4.8), (10:00, 2.9)]`이고 "4 이상이면 빨간색" 규칙을 걸었다면, 시간 창을 09:00에 두었을 때만 이 노드가 빨간색이 됩니다.

<a id="subtitle"></a>
#### 부제목 (Subtitle)

객체 타입이나 객체의 선택한 속성을 각 객체의 부제목으로 추가할 수 있습니다. 부제목은 그래프에서 같은 타입의 모든 객체에 표시됩니다.

![부제목](https://www.palantir.com/docs/resources/foundry/vertex/styling_subtitle.jpg)

<a id="extended-labels"></a>
#### 확장 레이블 (Extended labels)

**Extended Labels**를 선택하면 선택한 객체 노드에 특정 표시값을 추가할 수 있습니다. 실제 시계열 측정값이나 시뮬레이션된 값을 선택할 수 있으므로, 현재 상태와 모델링한 상태를 한 화면에서 비교할 수 있습니다.

![확장 레이블](https://www.palantir.com/docs/resources/foundry/vertex/styling_extended_labels_1.jpg)

확장 레이블 스타일을 설정한 다음에는 작업 공간 왼쪽의 객체 선택 패널에서 표시할 속성이나 시계열을 선택할 수 있습니다.

![확장 레이블](https://www.palantir.com/docs/resources/foundry/vertex/styling_extended_labels_1.jpg)

<a id="badges"></a>
#### 배지 (Badges)

특정 객체 타입에 링크된 이벤트 수를 나타내는 배지를 추가합니다. 아래 스크린샷에서 지연된 항공편 이벤트가 하나 있는 것을 볼 수 있습니다.

![배지](https://www.palantir.com/docs/resources/foundry/vertex/styling_badges.jpg)

<a id="node-style"></a>
#### 노드 스타일 (Node style)

객체를 기본 노드로 표시할지, 전체 객체 카드로 표시할지 고를 수 있습니다.

![노드 타입](https://www.palantir.com/docs/resources/foundry/vertex/styling_node_type.jpg)

> **중간 요약**: 객체 레이어는 **Styling Options**에서 색 기준(속성, 시계열, 파생 속성 함수), 부제목, 확장 레이블(실측값과 시뮬레이션 값), 이벤트 배지, 노드와 카드 표시 방식을 설정합니다.

<a id="edge-styling"></a>
### 간선 스타일 (Edge styling)

간선은 객체 사이의 관계를 나타내며, 시스템이나 프로세스 안의 노드 간 상호 작용을 시각화하도록 스타일을 지정할 수 있습니다.

구성하려는 간선에서 **Styling Options**를 선택합니다.

![간선 스타일](https://www.palantir.com/docs/resources/foundry/vertex/styling_edge_styling.jpg)

<a id="line-color"></a>
#### 선 색 (Line color)

객체 타입이나 관련 객체의 공통 속성을 기준으로 간선의 색을 설정할 수 있습니다.

![선 색](https://www.palantir.com/docs/resources/foundry/vertex/styling_line_color.jpg)

<a id="line-type"></a>
#### 선 종류 (Line type)

선을 직선, 곡선, 직각선(orthogonal) 중 하나로 그리도록 지정할 수 있습니다.

![선 종류](https://www.palantir.com/docs/resources/foundry/vertex/styling_line_type.jpg)

<a id="labels"></a>
#### 레이블 (Labels)

간선에 객체가 그룹화되어 있는 경우, 핵심 지표를 보여 주도록 객체의 개별 속성이나 집계된 속성을 기준으로 레이블을 구성할 수 있습니다.

![레이블](https://www.palantir.com/docs/resources/foundry/vertex/styling_label.jpg)

<a id="line-width"></a>
#### 선 굵기 (Line width)

객체의 속성을 기준으로 간선마다 다른 굵기를 적용할 수 있습니다. 선 굵기를 다르게 하면 객체(예: 공항) 사이를 오가는 거래(예: 항공편)의 이동과 양을 나타낼 수 있습니다.

![선 굵기](https://www.palantir.com/docs/resources/foundry/vertex/styling_width.png)

<a id="badges"></a>
#### 배지 (Badges)

객체 노드와 마찬가지로, 특정 간선 관계에 링크된 이벤트 수를 나타내는 배지를 추가할 수 있습니다. 여기서는 지연된 항공편 이벤트가 하나 있는 것을 볼 수 있습니다.

![간선 배지](https://www.palantir.com/docs/resources/foundry/vertex/styling_edge_badges.jpg)

<a id="ontology-level-edge-direction-configuration"></a>
#### 온톨로지 수준의 간선 방향 구성 (Ontology-level edge direction configuration)

그래프에 링크를 추가하면 기본적으로 간선 화살표는 링크의 오른쪽에서 왼쪽을 가리키도록 표시됩니다. 예를 들어 온톨로지에서 다대일(many-to-one) 링크 타입으로 구성된 링크라면 화살표는 "일(one)" 쪽에서 "다(many)" 쪽을 가리킵니다. 이 방향은 다음 온톨로지 타입 클래스(type class)를 사용해 링크 타입별로 구성할 수 있습니다.

* Primary Direction: `kind`: `vertex`, `name`: `link_primary_direction`
  * 링크의 한쪽에 붙이면, 간선 화살표가 링크의 이쪽 객체를 가리켜야 한다는 뜻입니다.
* Undirectional: `kind`: `vertex`, `name`: `link_undirectional`
  * 링크의 어느 쪽에든 붙이면, 간선에 화살표를 표시하지 않아야 한다는 뜻입니다.
* Bidirectional: `kind`: `vertex`, `name`: `link_bidirectional`
  * 링크의 어느 쪽에든 붙이면, 간선의 양쪽 끝에 화살표를 표시해야 한다는 뜻입니다.

간선 화살표는 레이어 스타일 옵션을 사용해 그래프별로 숨기거나 방향을 뒤집을 수도 있습니다.

![간선 방향 스타일 옵션](https://www.palantir.com/docs/resources/foundry/vertex/optional_ontology_config-edge-direction.jpg)

**설명**: 다대일 링크는 관계형 데이터베이스의 외래 키 관계입니다. 예를 들어 Flight 여러 개(다)가 `aircraft_id` 외래 키로 Aircraft 하나(일)를 가리키면, 기본 화살표는 Aircraft에서 Flight 쪽으로 그려집니다. 타입 클래스는 온톨로지 요소에 붙이는 `kind`와 `name` 쌍의 태그이고, 이 태그를 읽는 애플리케이션(여기서는 Vertex)이 동작을 바꿉니다. 예를 들어 링크의 Aircraft 쪽에 `link_primary_direction`을 붙이면 화살표가 Flight에서 Aircraft 쪽을 가리킵니다.

<a id="saved-styles"></a>
### 저장된 스타일 (Saved styles)

구성을 마치면 같은 그래프에 대해 서로 다른 스타일 옵션을 저장해 시스템의 여러 뷰를 제공할 수 있습니다. 예를 들어 여러 공항 사이 항공편의 뷰를 항공사의 핵심 성과 지표 기준으로 스타일 지정해 둘 수 있습니다. 그런 다음 같은 그래프에 다른 스타일을 적용해 같은 노선에 대한 고객 만족도를 보여 줄 수 있습니다.

![저장된 스타일](https://www.palantir.com/docs/resources/foundry/vertex/styling_saved_styles.jpg)

> **중간 요약**: 간선 레이어는 선 색, 선 종류, 레이블, 선 굵기, 배지로 스타일을 지정합니다. 화살표 방향은 온톨로지의 링크 타입에 Vertex 타입 클래스를 붙여 정하거나 그래프별로 바꿀 수 있고, 여러 스타일 조합을 저장된 스타일로 보관할 수 있습니다.

<a id="saved-selections"></a>
## 저장된 선택 (Saved selections)

그래프에서 선택한 객체 그룹을 저장된 선택(saved selection)으로 저장할 수도 있습니다. 이렇게 하려면 원하는 객체가 들어 있는 노드와 간선을 원하는 만큼 선택하고, 오른쪽 클릭 메뉴나 도구 모음의 **Selection** 메뉴에서 **Save objects in current selection**을 선택합니다.

![현재 선택의 객체 저장](https://www.palantir.com/docs/resources/foundry/vertex/saved-selection-save-objects-in-selection.png)

각 저장된 선택에는 이름과 색이 연결되어 있으며, 이는 레이어 패널의 **Saved selections** 섹션에 나타납니다. 그래프의 각 객체(간선이나 노드로 표현됨)에는 그 객체가 속한 저장된 선택들의 색으로 나뉜 테두리가 표시됩니다. 각 객체는 필요한 만큼 많은 저장된 선택에 속할 수 있지만, 테두리에는 처음 세 개의 저장된 선택 색만 표시됩니다.

![레이어 패널의 저장된 선택](https://www.palantir.com/docs/resources/foundry/vertex/saved-selection-layers-panel-and-borders.png)

저장된 선택에 들어 있는 모든 객체를 빠르게 선택하려면, 저장된 선택 위에 마우스를 올렸을 때 나타나는 빠른 선택(quick select) 동작을 선택합니다.

![저장된 선택의 빠른 선택](https://www.palantir.com/docs/resources/foundry/vertex/saved-selection-quick-select.png)

저장된 선택은 레이어 패널에서 편집할 수 있습니다. 저장된 선택의 이름을 바꾸려면 이름을 선택하고 새 이름을 입력한 뒤 Enter 키를 누릅니다. 저장된 선택을 삭제하거나 색을 바꾸려면 저장된 선택 위에 마우스를 올렸을 때 나타나는 **...** 아이콘(<img alt="점 세 개 아이콘" src="https://www.palantir.com/docs/resources/foundry/vertex/more.svg" width="20px">)을 선택합니다. 눈 아이콘(<img alt="눈 아이콘" src="https://www.palantir.com/docs/resources/foundry/vertex/eye-open.svg" width="20px">)으로 저장된 선택별로 테두리를 켜고 끌 수도 있습니다.

![저장된 선택의 추가 동작](https://www.palantir.com/docs/resources/foundry/vertex/saved-selection-more-actions.png)

저장된 선택에 들어 있는 객체는 그래프에서 객체를 고른 다음 **...** (<img alt="점 세 개 아이콘" src="https://www.palantir.com/docs/resources/foundry/vertex/more.svg" width="20px">) 버튼을 선택하고 **Add selected objects**(선택한 객체 추가) 또는 **Remove selected objects**(선택한 객체 제거) 옵션을 사용해 편집할 수 있습니다.

![저장된 선택의 객체 편집 옵션](https://www.palantir.com/docs/resources/foundry/vertex/saved-selection-edit-objects.png)

> **중간 요약**: 저장된 선택은 이름과 색이 붙은 객체 묶음으로, 그래프에서 색 테두리(최대 세 색)로 표시되고 빠른 선택, 이름과 색 변경, 삭제, 객체 추가와 제거가 가능합니다.

## 정리

- Vertex는 Hierarchy, Grid, Row/Column, Radial, Cluster, Cartesian 등 자동 레이아웃과 그 고급 파라미터를 제공합니다.
- 객체는 타입이나 속성 값별로 하나의 노드로 묶을 수 있고, 거래성 객체는 간선 하나로 묶을 수 있습니다.
- 레이어 스타일로 노드(색, 부제목, 확장 레이블, 배지, 카드 표시)와 간선(색, 종류, 레이블, 굵기, 배지)을 데이터에 따라 동적으로 꾸밉니다.
- 간선 화살표 방향은 링크 타입에 Vertex 타입 클래스를 붙여 온톨로지 수준에서 정할 수 있습니다.
- 저장된 스타일과 저장된 선택으로 같은 그래프의 여러 뷰와 객체 묶음을 보관합니다.
