# Workshop 모듈에 그래프 임베드하기 (Embed a graph in a Workshop module)

- 원문: https://www.palantir.com/docs/foundry/vertex/embed-graph-workshop/
- 사이드바 위치: Applications > Vertex > Graphs > Embed a graph in a Workshop module

이 페이지는 Vertex에서 만든 그래프, 그래프 템플릿, 다이어그램을 Workshop 모듈 안에 위젯으로 넣는 방법과, 그 위젯의 구성 옵션(입력, 상호작용, 시간, 기능, 인터페이스)을 설명합니다. Workshop 변수로 템플릿 파라미터를 채우고 그래프에서 선택한 객체를 다시 변수로 내보내는 구조를 이해하면, 객체 관계 시각화를 업무 화면의 다른 위젯과 연결할 수 있습니다. 마지막에는 그래프 탐색 결과를 객체 속성에 저장해 공유하는 패턴을 다룹니다.

그래프, 그래프 템플릿, 다이어그램은 Workshop 모듈에 임베드할 수 있으며, 사용자는 Workshop 워크플로 안에서 바로 Vertex 시각화와 상호작용할 수 있습니다. 이 통합을 통해 더 넓은 Workshop 모듈의 일부로 강력한 데이터 탐색과 시각화 경험을 제공할 수 있습니다.

그래프 템플릿에는 Workshop 변수에서 파라미터 값을 직접 전달할 수 있으므로, 사용자 상호작용이나 워크플로 상태에 따라 갱신되는 동적인 데이터 기반 시각화 경험을 만들 수 있습니다.

**설명**: Vertex 그래프는 객체를 노드로, 링크를 간선으로 그린 네트워크 그림입니다. 그래프 템플릿은 "어떤 시작 객체를 받으면 어떤 링크를 따라가 그래프를 만들지"를 정해 둔 규칙으로, 파라미터를 받는 함수에 해당합니다. 예를 들어 "Aircraft 하나를 받아 그 항공기의 Flight와 각 Flight의 Airport를 그린다"는 템플릿에 Workshop 변수로 Aircraft A1을 넘기면 A1 기준 그래프가 만들어지고, 변수가 A2로 바뀌면 A2 기준 그래프로 다시 그려집니다.

Workshop 모듈에 템플릿을 임베드하는 주요 단계는 세 가지입니다.

1. [Workshop에 Vertex 그래프 위젯 추가하기](#add-a-vertex-graph-widget-in-workshop)
2. [리소스 선택하기](#choose-a-resource)
3. [위젯 구성하기](#configure-the-widget)

<a id="add-a-vertex-graph-widget-in-workshop"></a>
## Workshop에 Vertex 그래프 위젯 추가하기 (Add a Vertex graph widget in Workshop)

Workshop 모듈에서 원하는 섹션의 **+** 아이콘 또는 **+Add widget** 버튼을 클릭해 위젯 메뉴를 열고, **Vertex Graph** 위젯을 검색합니다.

![Vertex 그래프 위젯 추가하기](https://www.palantir.com/docs/resources/foundry/vertex/workshop-adding-widget.png)

<a id="choose-a-resource"></a>
## 리소스 선택하기 (Choose a resource)

위젯 편집기에서 **Select**를 클릭해 임베드할 그래프, 그래프 템플릿, 또는 다이어그램 리소스를 선택합니다. 리소스 선택기에는 호환되는 리소스만 표시됩니다.

<a id="configure-the-widget"></a>
## 위젯 구성하기 (Configure the widget)

**Vertex graph** 위젯의 구성은 여러 섹션으로 나뉘어 있습니다. 각 섹션은 위젯의 동작과 모양의 서로 다른 측면을 제어합니다.

<a id="input"></a>
### 입력 (Input)

**Input** 섹션은 표시할 그래프나 템플릿, 그리고 그것이 데이터를 받는 방식을 제어합니다.

<img alt="Input 섹션." src="https://www.palantir.com/docs/resources/foundry/vertex/workshop-input-section.png" width="400" />

* **Resource**
  * **Static:** 이 리소스 모드를 선택하면 리소스 선택기로 입력 리소스 하나를 고릅니다. 그래프, 그래프 템플릿, 다이어그램 중 하나일 수 있습니다.
  * **Variable:** 이 리소스 모드를 선택하면 입력 리소스를 문자열 변수로 제공합니다. 이 변수에는 그래프, 그래프 포인터, 또는 그래프 템플릿의 RID가 들어 있어야 합니다.
  * **Override graph RID:** (선택) 선택한 리소스가 그래프 템플릿이라면, 템플릿과 그 파라미터로 그래프를 생성하는 대신 표시할 그래프의 RID를 제공할 수 있습니다. 이를 통해 객체의 속성에 저장된 RID로 기존 그래프를 불러올 수 있습니다. 자세한 내용은 [그래프 탐색 저장과 공유](#save-and-share-graph-explorations) 섹션을 참조하세요.
* **Parameters**
  * 그래프 템플릿을 임베드할 때 Workshop 변수를 사용해 템플릿 파라미터 값을 제공할 수 있습니다. 템플릿에 정의된 각 파라미터가 여기에 나타나 구성할 수 있습니다.
  * 객체 타입 파라미터에는 Workshop의 객체 집합(object set) 변수를 선택합니다.
  * 객체가 아닌 파라미터에는 파라미터 타입에 맞는 적절한 값을 제공합니다.
* **Sub-graph**
  * 여러 하위 그래프(sub-graph)가 있는 기존 그래프나 다이어그램 리소스를 임베드할 때, 해당 하위 그래프의 객체를 하나라도 포함한 Workshop 객체 집합 변수를 선택해 어떤 하위 그래프를 표시할지 고를 수 있습니다.
* **Refresh key**
  * 이 변수의 값이 바뀔 때마다 위젯은 그래프를 완전히 다시 로드합니다. 워크플로 상태 변화에 따라 새로 고침을 트리거할 때 유용합니다.
* **Append on parameter change**
  * 이 옵션을 켜면 파라미터를 바꿀 때 그래프를 처음부터 다시 생성하지 않고 기존 그래프에 새 객체를 덧붙입니다.
* **Scenario**
  * **Load data from scenario:** [온톨로지 시나리오](../../../04_ontology-scenarios/01_overview-ontology-scenario.md)를 사용하면 기본 온톨로지를 바꾸지 않고 격리된 샌드박스에서 편집(edit)을 적용할 수 있습니다. 이 토글을 켜면 주어진 리소스를 기본 온톨로지 대신 시나리오를 사용해 로드합니다.
  * **Regenerate graph after applying or switching scenarios:** 이 옵션을 설정하면 시나리오를 수정하거나 전환할 때마다 위젯이 그래프를 새로 고칩니다.

**주의**: 이전에는 그래프 템플릿에 정의된 필요한 객체 타입을 모두 담은 단일 입력 객체 집합 변수로 템플릿 입력을 제공했습니다. 이 방식은 객체가 아닌 파라미터가 없고 객체 타입마다 객체 파라미터가 하나인 템플릿에서만 동작하므로 이제 권장하지 않습니다. 이 기능을 사용하려면 **Use legacy input object set** 체크박스를 선택하고 객체 집합 변수를 제공하세요.

**설명**: Static과 Variable의 차이는 "어떤 그래프를 보여 줄지"가 화면을 설계할 때 고정되는지, 실행 중에 정해지는지입니다. Static은 설계 시점에 리소스 하나를 박아 두고, Variable은 문자열 변수에 들어 있는 RID를 실행 시점에 읽어 해당 리소스를 엽니다. 또 Refresh key는 값 자체보다 "값이 바뀌었다"는 사실을 신호로 쓰는 변수입니다. 예를 들어 다른 위젯에서 액션을 실행한 뒤 이 변수 값을 현재 시각으로 바꾸면 그래프가 최신 데이터로 다시 그려집니다.

> **중간 요약**: Input 섹션은 표시할 리소스(고정 또는 변수), 템플릿 파라미터에 연결할 Workshop 변수, 하위 그래프 선택, 새로 고침 신호, 시나리오 사용 여부를 정합니다. 저장된 그래프를 불러오려면 Override graph RID를 사용합니다.

<a id="interaction"></a>
### 상호작용 (Interaction)

**Interaction** 섹션은 사용자가 그래프와 상호작용하는 방식, 그리고 그래프가 다른 Workshop 컴포넌트와 상호작용하는 방식을 구성합니다.

![Interaction 섹션.](https://www.palantir.com/docs/resources/foundry/vertex/workshop-interaction-section.png)

* **Selected objects**
  * 이 옵션은 현재 선택된 객체들의 객체 집합을 출력합니다. 이 객체 집합은 현재 모듈 안의 다운스트림 위젯에서 사용할 수 있습니다.
  * 사용자가 그래프에서 객체를 선택하면 이 변수가 선택 내용으로 자동으로 채워집니다.
* **On selected objects change**
  * 그래프에서 선택된 객체가 바뀔 때 트리거할 Workshop 이벤트를 구성합니다.
  * 선택된 객체의 상세 화면이 있는 드로어를 열거나, 다른 위젯의 새로 고침을 트리거하거나, 그 밖의 Workshop 이벤트 동작에 사용할 수 있습니다.
* **On successful action application**
  * 사용자가 그래프에서 액션을 성공적으로 적용했을 때 트리거할 Workshop 이벤트를 구성합니다.
  * 이 이벤트는 기반 액션이 성공적으로 실행된 뒤 발생합니다.
* **Zoom to object set**
  * 입력이 바뀔 때마다 주어진 객체 집합의 객체가 보이도록 뷰포트를 설정합니다.
  * 이를 통해 프로그래밍 방식으로 그래프의 초점을 특정 객체에 맞출 수 있습니다.
* **Objects on subgraph**
  * 현재 선택된 하위 그래프에 있는 모든 객체를 담은 객체 집합을 출력합니다.
  * 현재 화면에 보이는 모든 객체를 다른 위젯에서 쓰기 위해 수집할 때 유용합니다.
* **Add objects to subgraph**
  * 주어진 객체를 현재 선택된 하위 그래프에 추가합니다.
  * 이를 통해 다른 위젯에서 프로그래밍 방식으로 그래프에 객체를 추가할 수 있습니다.
* **Available actions**
  * 그래프 인터페이스 안에서 사용자가 바로 쓸 수 있는 액션을 제어합니다.
  * 옵션은 다음과 같습니다.
    * **All:** 그래프에 있는 모든 객체의 모든 액션을 사용할 수 있습니다.
    * **Some:** 특별히 선택한 액션만 사용할 수 있습니다.
    * **None:** 사용할 수 있는 액션이 없습니다.

**설명**: 이 섹션의 옵션은 방향에 따라 두 종류로 나뉩니다. Selected objects와 Objects on subgraph는 그래프에서 Workshop 변수로 값을 내보내는 출력이고, Zoom to object set과 Add objects to subgraph는 Workshop 변수에서 그래프로 값을 넣는 입력입니다. 예를 들어 그래프에서 Flight F100을 클릭하면 Selected objects 변수에 F100이 들어가고, 같은 모듈의 표 위젯이 이 변수를 입력으로 받아 F100의 상세 속성을 보여 줄 수 있습니다.

> **중간 요약**: Interaction 섹션은 선택된 객체와 화면의 객체를 변수로 내보내고, 변수로 받은 객체에 확대하거나 추가하며, 선택 변경과 액션 성공 시 이벤트를 트리거하고, 그래프에서 쓸 수 있는 액션 범위를 정합니다.

<a id="time-configuration"></a>
### 시간 구성 (Time Configuration)

**Time configuration** 섹션은 그래프에서 시간을 표현하고 상호작용하는 방식을 제어합니다.

![Time Configuration 섹션.](https://www.palantir.com/docs/resources/foundry/vertex/workshop-time-configuration.png)

* **Selected time**
  * 그래프의 선택된 시각을 제어합니다.
  * 선택된 시각은 그래프나 선택 패널에 표시되는 시간 데이터의 판독값을 결정합니다.
  * 시각 선택은 타임라인, 시간 선택 패널, 시리즈 패널 중 하나가 활성화되어 있을 때만 가능합니다.
  * 선택된 시각의 기본값은 그래프가 로드된 시각입니다.
  * 옵션:
    * **Default:** 시각 선택이 변수로 동기화되지 않습니다.
    * **Timestamp variable:** `Timestamp` 타입의 Workshop 변수와 그래프 시각 표시를 동기화합니다.
    * **Date variable:** `Date` 타입의 Workshop 변수와 그래프 시각 표시를 동기화합니다.
* **Time window**
  * 그래프에서 사용하는 시간 범위(time window)를 제어합니다. 시간 범위는 시간 차트에 표시되는 데이터의 범위를 결정합니다.
  * 시간 범위 선택은 타임라인, 시간 선택 패널, 시리즈 패널 중 하나가 활성화되어 있을 때만 가능합니다.
  * 기본 시간 범위는 Control Panel에서 구성합니다.
  * 옵션:
    * **Default:** 시간 범위가 변수와 동기화되지 않습니다.
    * **Timestamp:** `Timestamp` 타입의 Workshop 변수 두 개로 시간 범위를 정의합니다.
      * **Start:** 시간 범위의 시작입니다.
      * **End:** 시간 범위의 끝입니다.
    * **Date:** `Date` 타입의 Workshop 변수 두 개로 시간 범위를 정의합니다.
      * **Start:** 시간 범위의 시작입니다.
      * **End:** 시간 범위의 끝입니다.

**설명**: 선택된 시각은 한 점이고, 시간 범위는 구간입니다. 예를 들어 Aircraft 객체에 고도 시계열 속성이 있을 때, 선택된 시각이 10:00이면 선택 패널에는 10:00 시점의 고도 값 하나가 표시되고, 시간 범위가 09:00부터 12:00이면 시리즈 차트에는 그 세 시간 동안의 고도 변화가 그려집니다.

> **중간 요약**: Time Configuration 섹션은 그래프의 선택 시각(한 점)과 시간 범위(구간)를 Workshop의 `Timestamp` 또는 `Date` 변수와 동기화할지 정합니다.

<a id="capabilities"></a>
### 기능 (Capabilities)

**Capabilities** 섹션은 위젯 사용자가 쓸 수 있는 기능을 제어합니다.

![Capabilities 섹션.](https://www.palantir.com/docs/resources/foundry/vertex/workshop-capabilities-section.png)

* **Read-only mode**
  * 이 설정을 켜면 편집 기능이 제거되고 편집 툴바가 숨겨집니다.
  * 사용자가 그래프를 수정해서는 안 되는 보기 전용 시각화를 만들 때 유용합니다.
* **Enable transition to Vertex application**
  * 이 옵션을 켜면 사용자가 현재 그래프 상태 그대로 Vertex 애플리케이션을 열 수 있는 버튼이 표시됩니다.
  * 더 고급 작업을 위해 Workshop에 임베드된 그래프에서 전체 Vertex 애플리케이션으로 매끄럽게 넘어갈 수 있습니다.
* **Enable export as PNG**
  * 이 옵션을 켜면 사용자가 현재 그래프를 PNG 이미지로 내보낼 수 있습니다.
  * 이 기능을 사용하려면 사용자에게 임베드된 리소스에 대한 프런트엔드 내보내기(frontend export) 권한이 있어야 합니다.
* **Saving settings**
  * 사용자가 현재 그래프 상태를 저장할 수 있는지 제어합니다.
  * 옵션:
    * **Disabled:** 사용자가 그래프를 저장할 수 없습니다.
    * **Enabled:** 사용자가 다음 추가 구성과 함께 그래프를 저장할 수 있습니다.
      * **Default resource name:** 새로 저장되는 그래프의 이름을 지정합니다.
        * **Static:** 고정된 텍스트 문자열을 이름으로 사용합니다.
        * **Variable:** Workshop 문자열 변수를 이름으로 사용합니다.
      * **Default folder:** 새로 저장되는 그래프가 보관될 위치를 지정합니다.
        * **Folder reference:** 특정 폴더를 선택합니다.
        * **Static RID:** 특정 폴더 RID를 사용합니다.
        * **Variable:** 폴더 RID나 경로를 담은 Workshop 변수를 사용합니다.
      * **On create new graph:** 그래프가 저장될 때 일어날 일을 구성합니다.
        * **Event:** 그래프가 저장될 때 Workshop 이벤트를 트리거합니다.
        * **Action:** 그래프가 저장될 때 Foundry 액션을 실행합니다.
          * 저장된 그래프 RID, 저장된 그래프 이름, 현재 사용자의 ID를 액션의 특수 입력으로 사용할 수 있습니다.
          * 모든 필수 파라미터에는 기본값이 구성되어 있어야 합니다.
      * **Show save dialog:** 저장할 때 리소스 대화 상자를 표시할지 제어합니다.
        * **None:** 대화 상자를 표시하지 않고 기본 이름과 위치로 리소스를 저장합니다.
        * **Resource dialog:** 사용자에게 이름과 위치를 선택하라는 창이 뜹니다.
      * **Save as versioned graph:** 이 옵션을 켜면 이전에 버전 관리되지 않던 그래프라도 버전 관리 그래프(versioned graph)로 저장합니다. 버전 관리 그래프는 자동 저장과 버전 이력을 지원합니다.

**설명**: On create new graph의 Action 옵션에서 "모든 필수 파라미터에 기본값이 있어야 한다"는 조건은, 저장 버튼을 누를 때 액션 입력 폼을 띄우지 않고 바로 실행하기 때문으로 이해할 수 있습니다. 저장된 그래프 RID처럼 위젯이 자동으로 채우는 특수 입력 외의 나머지 파라미터는 미리 정해진 값이 있어야 실행할 수 있습니다.

> **중간 요약**: Capabilities 섹션은 읽기 전용 여부, Vertex 앱으로 이동, PNG 내보내기, 그래프 저장(이름, 폴더, 저장 후 이벤트나 액션, 대화 상자, 버전 관리)을 설정합니다.

<a id="interface"></a>
### 인터페이스 (Interface)

**Interface** 섹션은 위젯 사용자에게 보이는 UI 요소와 패널을 제어합니다.

![Interface 섹션.](https://www.palantir.com/docs/resources/foundry/vertex/workshop-interface-section.png)

* **Legend/objects panel**
  * 이 토글을 켜면 왼쪽 패널이 표시됩니다. 이 패널에는 아래에서 활성화한 레이어, 선택, 검색, 히스토그램, 정보 패널이 들어 있습니다.
* **Series panel**
  * 이 토글을 켜면 위젯 하단에 시리즈 패널이 표시됩니다.
  * 시리즈 패널은 선택된 객체와 관련된 시계열 데이터를 보여 줍니다.
* **Time selection panel**
  * 이 토글을 켜면 위젯 오른쪽 위에 시간 스크러버(time scrubber)가 표시됩니다.
  * 이 패널로 사용자는 시간 데이터와 상호작용하고 특정 시점을 선택할 수 있습니다.
* **Enable timeline**
  * 이 토글을 켜면 데이터의 타임라인 보기가 표시됩니다.
  * 이벤트와 데이터 지점을 시간 순서로 보여 줍니다.
* **Is timeline open**
  * 모듈을 처음 로드할 때 타임라인이 열려 있을지 닫혀 있을지 제어합니다.
* **Enable layers panel**
  * 이 토글을 켜면 레이어 패널을 표시할 수 있습니다.
  * 레이어 패널은 여러 데이터 레이어의 표시 여부를 전환하는 컨트롤을 제공합니다.
* **Enable selection panel**
  * 이 토글을 켜면 선택 패널을 표시할 수 있습니다.
  * 선택 패널은 현재 선택된 객체의 세부 정보를 보여 줍니다.
* **Enable search panel**
  * 이 토글을 켜면 검색 패널을 표시할 수 있습니다.
  * 검색 패널은 그래프에서 객체를 찾는 기능을 제공합니다.
* **Enable histogram panel**
  * 이 토글을 켜면 히스토그램 패널을 표시할 수 있습니다.
  * 히스토그램 패널은 그래프에 있는 객체들의 속성 값 분포를 보여 줍니다.
* **Enable info panel**
  * 이 토글을 켜면 정보 패널을 표시할 수 있습니다.
  * 정보 패널은 그래프에 대한 상위 수준의 개요 메타데이터를 제공하며, 레이어의 범례도 포함합니다.
* **Enable version history panel**
  * 이 토글을 켜면 버전 이력 패널을 표시할 수 있습니다.
  * 버전 이력 패널은 버전 관리 그래프의 이전 버전을 보여 줍니다.
* **Enable add object**
  * 이 토글을 켜면 사용자가 그래프에 새 객체를 추가할 수 있습니다.
* **Is legend/objects panel collapsed**
  * 모듈을 처음 로드할 때 범례/객체 패널이 접혀 있을지 펼쳐져 있을지 제어합니다.
  * 위젯 안에서 초기 화면 공간 배분을 관리하는 데 도움이 됩니다.
* **Enable subgraph navigation menu**
  * 이 토글을 켜면 사용자가 하위 그래프 사이를 이동하고 새 하위 그래프를 만들 수 있습니다.
  * 그래프에 하위 그래프가 여러 개 있으면 이 설정과 관계없이 내비게이션 메뉴가 항상 나타납니다.
* **Incomplete inputs message**
  * 필수 입력이 없어 그래프 템플릿을 실행할 수 없을 때 이 메시지가 대화 상자로 사용자에게 표시됩니다.
  * 필수 템플릿 파라미터가 제공되지 않았을 때 사용자에게 보여 줄 메시지를 이 필드로 사용자 정의합니다.

> **중간 요약**: Interface 섹션은 왼쪽 범례/객체 패널과 그 안의 하위 패널, 시리즈 패널, 시간 스크러버, 타임라인, 하위 그래프 메뉴의 표시 여부와 초기 상태, 그리고 입력이 부족할 때 보여 줄 메시지를 정합니다.

<a id="patterns"></a>
## 패턴 (Patterns)

<a id="graph-template-parameterization"></a>
### 그래프 템플릿 파라미터화 (Graph template parameterization)

그래프 템플릿을 임베드할 때 Workshop 변수를 사용해 파라미터화할 수 있습니다. 이를 통해 사용자 입력이나 워크플로의 다른 데이터에 따라 갱신되는 동적 시각화를 만들 수 있습니다.

<a id="save-and-share-graph-explorations"></a>
### 그래프 탐색 저장과 공유 (Save and share graph explorations)

흔히 쓰는 패턴은, 사용자가 어떤 초기 객체에 적용할 수 있는 그래프 템플릿을 두고, 현재 탐색 상태를 저장해 나중에 이어서 탐색할 수 있게 하는 것입니다.
이를 통해 사용자는 템플릿화된 워크플로에서 시작해 추가 조사를 수행하고, 그래프와 상호작용하면서 발견한 흥미로운 인사이트나 관계를 기록할 수 있습니다.
저장된 그래프는 객체에 참조로 추가할 수 있으므로, 다른 사람과 쉽게 공유하거나 나중에 다시 볼 수 있습니다.

이 패턴을 구현하려면 다음 단계를 따릅니다.

1. 저장된 그래프 RID를 담을 **속성(property)을 객체 타입에 추가합니다**.
   * 이 속성은 **Resource RID** 옵션을 사용하는 **Value Formatting**이 적용된 문자열이어야 합니다.
   * 이 속성에는 값을 설정하는 **액션**이 연결되어 있어야 하며, 이 액션은 그래프를 리소스로 저장한 뒤 사용됩니다.
   * 이 객체는 보통 그래프 템플릿에 파라미터로 전달되는 객체와 같은 객체이지만, 저장된 그래프를 담는 데 쓰이는 별도의 특정 객체 타입일 수도 있습니다. 이 경우 탐색 대상 객체에 링크되어 있는 경우가 많습니다.
2. 초기 탐색을 수행하도록 구성된 **그래프 템플릿을 만듭니다**.
3. Vertex graph 위젯을 사용해 **그래프 템플릿을 Workshop 모듈에 임베드합니다**.
   1. **Resource** 섹션에서 **Static** 옵션으로 그래프 템플릿을 선택합니다.
   2. 템플릿의 파라미터를 구성합니다.
   3. **Override graph RID** 옵션으로 저장된 그래프 RID를 담고 있는 객체 속성을 지정합니다.
      * 이 객체는 템플릿에 전달된 것과 같은 객체일 수도 있고, 그래프가 링크된 객체에 참조되는 경우라면 링크 검색이나 별도의 저장된 그래프 목록에서 얻은 Workshop 변수로 찾은 객체일 수도 있습니다.
4. 위젯 구성에서 **저장 설정을 활성화해** 사용자가 현재 그래프 상태를 저장할 수 있게 합니다.
   * **On create new graph** 옵션을 사용해 속성 값을 저장된 그래프 RID로 설정하는 액션을 실행합니다.
   * 액션 파라미터를 구성할 때 특수 값인 **Saved graph RID**를 적절한 파라미터에 전달해야 합니다.

이 패턴을 따르면 사용자가 저장 아이콘을 선택할 때 현재 그래프 상태가 리소스로 저장되고, 객체의 속성이 저장된 그래프의 RID로 업데이트됩니다. 사용자가 그 객체를 다시 방문하면 **Override graph RID** 옵션을 통해 저장된 그래프가 로드됩니다.

**설명**: 이 패턴의 데이터 흐름을 구체적으로 따라가 보면 다음과 같습니다. `Investigation` 객체 타입에 `saved_graph_rid` 문자열 속성이 있고, 처음에는 I1 객체의 이 값이 비어 있습니다. (1) 사용자가 I1의 화면을 열면 Override graph RID가 비어 있으므로 템플릿이 I1을 파라미터로 받아 그래프를 새로 생성합니다. (2) 사용자가 객체를 몇 개 더 펼친 뒤 저장 아이콘을 누르면 그래프가 `ri.vertex...` 같은 RID를 가진 리소스로 저장됩니다. (3) On create new graph에 연결된 액션이 이 RID를 I1의 `saved_graph_rid`에 기록합니다. (4) 다음에 누군가 I1을 열면 `saved_graph_rid`에 값이 있으므로 템플릿을 다시 실행하지 않고 저장된 그래프를 그대로 불러옵니다. 즉 객체 속성에 그래프 리소스를 가리키는 참조를 저장해, 객체와 그래프를 연결하는 구조입니다.

> **중간 요약**: 그래프 탐색 결과를 저장하려면 객체 타입에 RID 문자열 속성과 그 값을 설정하는 액션을 만들고, 위젯에서 Override graph RID로 그 속성을 읽게 하며, 저장 시 On create new graph 액션으로 저장된 그래프 RID를 속성에 기록합니다.

## 정리

- Vertex 그래프, 그래프 템플릿, 다이어그램은 Workshop의 Vertex Graph 위젯으로 임베드하며, 위젯 추가, 리소스 선택, 구성의 세 단계를 거칩니다.
- Input 섹션은 리소스와 템플릿 파라미터를 Workshop 변수에 연결하고, 하위 그래프, 새로 고침, 시나리오 사용을 정합니다.
- Interaction 섹션은 선택된 객체를 변수로 내보내고 이벤트와 액션 범위를 설정하며, Time Configuration 섹션은 시각과 시간 범위를 변수와 동기화합니다.
- Capabilities와 Interface 섹션은 읽기 전용, 내보내기, 저장 기능과 각종 패널의 표시 여부를 제어합니다.
- 저장된 그래프의 RID를 객체 속성에 기록하고 Override graph RID로 다시 불러오는 패턴으로 그래프 탐색을 저장하고 공유할 수 있습니다.
