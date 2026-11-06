# 프로세스 분석과 모니터링 (Analyze and monitor a process)

- 원문: https://www.palantir.com/docs/foundry/machinery/analyze-and-monitor/
- 사이드바 위치: Applications > Machinery > Analyze and monitor a process

이 페이지는 Machinery 프로세스를 Workshop 애플리케이션 안에서 시각화하고 모니터링하는 Machinery 위젯을 설명합니다. 프로세스 정의와 데이터를 연결해 두었다면, 이 위젯으로 각 상태에 객체가 몇 개 있는지, 얼마나 오래 머무는지, 어느 경로를 거치는지 보고 병목을 찾을 수 있습니다. 위젯 구성(입력, 메트릭 보기, 출력)과 사용자 기능(메트릭 순환과 고정, 적합성 필터링, 경로 탐색기, 소요 시간 분포)을 다룹니다.

Machinery 위젯은 구성해 둔 Machinery 프로세스에 대한 운영 인사이트와 모니터링 기능을 제공합니다.

* 사용자들이 프로세스 안에서 활발히 작업하는 동안 프로세스 운영 상황을 파악할 수 있습니다.
* 분석 및 모니터링 워크플로에서 병목을 찾아낼 수 있습니다.
* 구성 가능한 보기를 통해 프로세스 흐름과 메트릭을 시각화할 수 있습니다.

![Machinery 위젯 이미지.](https://www.palantir.com/docs/resources/foundry/machinery/widget.png)

이 위젯은 Workshop 애플리케이션에서 Machinery 그래프를 메트릭, 프로세스 흐름, 객체 분포를 표시할 수 있는 시각화로 렌더링합니다.

Machinery 위젯은 Workshop 모듈에서 사용할 수 있고, Machinery 애플리케이션 안에서 기능이 제한된 독립 보기 모드로도 사용할 수 있습니다.

<a id="widget-configuration"></a>
## 위젯 구성 (Widget configuration)

Workshop 모듈을 만들거나 열고 Machinery Overview 위젯을 선택합니다. 위젯 버전은 기본으로 v2가 선택되며, v2는 Machinery v2 리소스를 지원합니다. 위젯 구성 상단에서 Machinery 그래프 리소스를 선택합니다.

<a id="upgrade-existing-applications"></a>
### 기존 애플리케이션 업그레이드 (Upgrade existing applications)

새 Machinery 위젯은 기본적으로 v2 위젯으로 만들어집니다. 기존 위젯은 v2로 업그레이드해야 합니다.

1. 레거시 위젯을 v2로 업그레이드하려면 **...** 드롭다운 메뉴에서 **Workshop** 편집 모드를 엽니다.
2. 그래프 아무 곳이나 선택하고, **Widget setup** 메뉴에서 **Use Machinery v2**를 선택합니다.
3. [입력](#inputs)을 알맞게 갱신합니다.

<img src="https://www.palantir.com/docs/resources/foundry/machinery/widget-v1-v2.png" alt="Machinery 버전 선택기." width="350" />

<a id="inputs"></a>
### 입력 (Inputs)

그래프의 루트 프로세스마다 입력 객체 집합(object set)을 하나씩 구성합니다. Machinery 위젯은 링크 타입 설정으로부터 하위 프로세스의 객체 집합을 자동으로 도출하며, 하위 프로세스는 **Object type** 아래에서 구성한 대로 부모 객체로 가는 링크 타입을 가집니다.

**예시:** 신청서(application) 객체 100개를 제공하고 각 신청서가 여러 심사(review) 객체에 링크되어 있다면, 위젯은 구성된 링크 타입을 통해 관련된 모든 심사 객체를 자동으로 찾아냅니다. 따라서 그래프의 루트 프로세스마다 객체 입력만 구성하면 됩니다(보통 객체 입력 1개).

**설명**: 이 동작은 SQL의 조인과 같은 계산입니다. 입력이 신청서 100개라면 위젯은 `SELECT r.* FROM review r WHERE r.application_id IN (입력된 신청서 100개의 기본 키)`에 해당하는 심사 객체 집합을 링크 타입을 따라가서 얻습니다. Foundry에서는 이렇게 링크를 따라 연결된 객체 집합을 구하는 것을 "search around"라고 부릅니다.

<a id="metric-views"></a>
### 메트릭 보기 (Metric views)

Machinery 위젯은 다음과 같은 미리 구성된 메트릭 보기를 가지고 생성됩니다.

* **Historical count(누적 개수):** 그 상태를 한 번이라도 거친 개수(ever count) 메트릭을 보여 줍니다.
* **Current count(현재 개수):** 현재 그 상태에 있는 개수를 보여 줍니다.
* **Historical duration(누적 소요 시간):** 그 상태에 머물렀던 과거 소요 시간을 보여 줍니다.
* **Current duration(현재 소요 시간):** 현재 그 상태에 머물고 있는 소요 시간을 보여 줍니다.

애플리케이션 빌더는 이 메트릭 보기들을 추가, 제거, 재배치하거나 사용자 정의할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/machinery/widget-views-edit.png" width="350" alt="Workshop의 편집 모드에서 미리 구성된 보기를 편집하거나 Add item 옵션으로 직접 보기를 추가합니다.">

**+ Add item** 옵션으로 사용자 정의 보기를 추가할 수도 있습니다. 빌더는 보기마다 숫자 서식과 조건부 색상을 가진 노드 메트릭 하나, 선택적인 간선 메트릭 하나를 정의하고, Sankey 다이어그램 간선 두께 설정을 켤 수 있습니다.

**설명**: "Historical"과 "Current"의 차이를 예시로 보면, 송장 3개가 각각 `created`를 거쳐 지금은 `approved`(2개)와 `paid`(1개)에 있다면 `created`의 Historical count는 3이고 Current count는 0입니다. 메트릭은 로그 객체의 이력에서 계산되는 값입니다. Sankey 다이어그램은 흐름의 양을 간선 두께로 나타내는 그림으로, 자주 일어나는 전이일수록 간선이 두껍게 그려집니다.

<a id="outputs"></a>
### 출력 (Outputs)

출력 데이터는 Workshop 모듈 안에서 추가 분석에 사용할 수 있습니다. 그래프 상호작용에 따라 필터링된 결과를 담도록 출력 객체 집합을 구성합니다.

* 그래프의 프로세스마다 출력을 하나씩 만듭니다(선택 사항).
* 출력 객체 집합에는 Machinery 애플리케이션에서 프로세스 수준으로 정의한 필터와, 부모 프로세스에서 자식 프로세스로 가는 search around가 적용됩니다.
* 출력은 노드/간선 선택에 동적으로 반응합니다.
* 경로 탐색기(path explorer)와 분포 차트도 출력에 영향을 주는 추가 수단을 제공합니다.

<a id="node-and-edge-selection"></a>
#### 노드와 간선 선택 (Node and edge selection)

다음 옵션 중 하나를 켜서 노드 선택이 객체 출력에 어떻게 영향을 줄지 바꿀 수 있습니다.

* 현재 선택한 상태에 있는 프로세스(Processes currently in selected states)
* 선택한 상태를 한 번이라도 거친 프로세스(Processes ever in selected states)

간선 선택은 해당 전이를 한 번이라도 거친 객체를 보여 줄지, 마지막 전이만 볼지로 구성할 수 있습니다.

<a id="configure-views"></a>
### 보기 구성 (Configure views)

보기는 위젯에 어떤 메트릭과 시각화가 나타날지를 결정합니다. 자세한 내용은 아래의 메트릭 보기 섹션을 참고하세요.

> **중간 요약**: Workshop에서 Machinery Overview 위젯(기본 v2)을 추가하고 그래프 리소스를 고른 뒤, 루트 프로세스마다 입력 객체 집합을 지정하면 하위 프로세스는 링크로 자동 도출됩니다. 기본 메트릭 보기 네 가지(누적/현재 개수, 누적/현재 소요 시간)를 수정하거나 추가할 수 있고, 출력 객체 집합은 그래프 선택에 따라 필터링됩니다.

<a id="widget-features"></a>
## 위젯 기능 (Widget features)

Machinery 위젯에서 그래프를 보는 사용자는 메트릭 순환과 고정, 여러 사용 모드, 필터 같은 기능을 활용할 수 있습니다.

<a id="metric-views-cycling-and-pinning"></a>
### 메트릭 보기, 순환, 고정 (Metric views, cycling, and pinning)

위젯은 공간을 효율적으로 쓰는 방식으로 메트릭을 표시합니다. 그래프에는 한 번에 노드 메트릭 하나와, 선택했다면 간선 메트릭 하나가 보입니다. 화면을 충분히 확대하면 그래프에 메트릭 3개를 담은 노드 카드가 표시되며, 첫 번째는 현재 활성화된 보기의 메트릭입니다. Sankey 다이어그램 간선을 구성해 두었다면 Transitions 보기에서 간선 두께로 흐름 빈도를 나타냅니다.

![그래프를 확대했을 때 메트릭 카드를 보여 주는 노드.](https://www.palantir.com/docs/resources/foundry/machinery/widget-contextual-zoom.png)

<a id="preconfigured-views"></a>
#### 미리 구성된 보기 (Preconfigured views)

위젯 사용자는 누적 개수, 현재 개수, 누적 소요 시간, 현재 소요 시간 같은 미리 구성된 [메트릭 보기](#metric-views)를 순환하며 볼 수 있습니다. 보기를 선택한 뒤 아무 노드에나 마우스를 올리면 사용 가능한 모든 메트릭이 나타납니다.

![그래프 아래쪽의 위젯 보기 선택기.](https://www.palantir.com/docs/resources/foundry/machinery/widget-views.png)

또한 노드 메트릭을 선택하면 고정(pin)되어 검토하는 동안 메트릭이 계속 보이며, 다시 선택하면 고정이 해제됩니다.

![노드 메트릭을 선택해 고정합니다. 고정을 해제하려면 핀 아이콘을 선택합니다.](https://www.palantir.com/docs/resources/foundry/machinery/node-pinning.png)

<a id="process-conformance-filtering"></a>
### 프로세스 적합성 필터링 (Process-conformance filtering)

기본적으로 위젯은 프로세스 정의에 부합하는(conform) 프로세스만 표시합니다.

* Machinery에 없는 상태와 전이는 제외됩니다.
* 메트릭은 부합하는 프로세스만을 대상으로 계산됩니다.
* 그래프의 로그 객체 타입 중 하나라도 객체가 100만 개를 넘으면 적합성 필터링이 비활성화되며, 그래프는 메트릭 계산과 출력 객체 집합을 포함해 모든 입력 객체를 다룹니다.

**설명**: 예를 들어 정의에 `created`, `approved`, `paid`만 있는데 어떤 송장이 `created`에서 `on_hold`를 거쳐 `approved`로 갔다면, 이 송장은 정의에 없는 상태를 거쳤으므로 부합하지 않는 프로세스로 보고 기본적으로 메트릭 계산에서 빠집니다. 100만 개 기준이 넘으면 이 검사를 하지 않으므로, 대용량 데이터에서는 메트릭에 이런 객체가 섞일 수 있다는 점을 알고 있어야 합니다.

<a id="focus-into-a-parent-process"></a>
### 부모 프로세스로 초점 맞추기 (Focus into a parent process)

그래프에서 원하는 부모 프로세스로 초점을 맞춰 보기를 좁힐 수 있습니다.

<a id="graph-selection-and-outputs"></a>
### 그래프 선택과 출력 (Graph selection and outputs)

그래프와 상호작용해 출력 객체 집합을 필터링합니다.

* 노드를 선택하면 상태로 객체를 필터링합니다.
* 간선을 선택하면 전이로 객체를 필터링합니다.
* 출력 객체 집합은 선택에 따라 자동으로 갱신됩니다.

<a id="graph-features"></a>
### 그래프 기능 (Graph features)

다음 그래프 기능은 위젯 헤더에서 각각 켜거나 끌 수 있습니다.

* **Transition nodes(전이 노드):** Machinery 애플리케이션에서 구성한 액션이나 자동화가 그래프에 포함되어 있으면, Machinery 위젯은 이를 암묵적인 상태 전이로 대체해 상태 전이 관점에서 프로세스를 이해하도록 돕습니다. 대신 전이 노드를 표시하도록 선택할 수 있으며, 기본 동작은 위젯 구성에서 설정합니다.
* **Subprocesses(하위 프로세스):** 그래프에 하위 프로세스가 있다면, 이를 암묵적인 상태 전이로 대체해 현재 초점이 맞춰진 프로세스의 전이 메트릭을 볼 수 있습니다.
* **Deviations(이탈):** 현재 데이터에 이탈 객체가 있으면 기본적으로 숨겨집니다. 이탈 객체란 프로세스 정의에 포함되지 않은 상태나 전이를 거친 객체입니다. 이들을 보이지 않게 할 수 있고, 위젯 출력에 포함할지 여부를 따로 선택할 수 있습니다.

**설명**: "암묵적인 상태 전이로 대체"한다는 것은, 그래프에 `submitted` 다음 "승인" 액션 노드, 그다음 `approved`가 있다면 가운데 액션 노드를 빼고 `submitted`에서 `approved`로 바로 가는 간선 하나로 보여 준다는 뜻입니다. 이렇게 하면 간선에 전이 메트릭(예: 전이 횟수)을 붙여 볼 수 있습니다.

<a id="analysis-modes"></a>
### 분석 모드 (Analysis modes)

Machinery 그래프가 열려 있을 때, 그래프 오른쪽에 있는 경로 탐색기 기능과 소요 시간 분포 기능 사이를 전환할 수 있습니다. 선택한 기능은 오른쪽에 열립니다.

![그래프 오른쪽에서 경로 탐색기 또는 소요 시간 분포 필터를 선택합니다.](https://www.palantir.com/docs/resources/foundry/machinery/widget-filtering-views.png)

<a id="path-explorer"></a>
#### 경로 탐색기 (Path explorer)

경로 탐색기 기능으로 한 번에 프로세스 하나에 대해 개별 프로세스 경로와 그 빈도를 분석합니다. 경로 탐색기를 열려면 그래프 오른쪽에 있는 경로 탐색기 아이콘을 선택합니다.

경로 탐색기는 현재 초점이 맞춰진 프로세스가 거친 모든 경로를 표시하고, 경로 빈도 분포(해당 경로를 완료한 객체의 빈도)를 보여 줍니다.

창에서 경로에 마우스를 올리면 그래프에서 그 경로가 강조 표시됩니다. 하나 이상의 경로를 선택해 출력을 필터링할 수도 있습니다.

![그래프 오른쪽의 경로 탐색기 창.](https://www.palantir.com/docs/resources/foundry/machinery/widget-path-explorer.png)

경로 탐색기가 열려 있으면 경로 선택이 위젯 출력을 제어하며, 앞서 한 노드/간선 선택보다 우선합니다.

**설명**: 경로는 객체 하나가 거친 상태들의 순서열입니다. 예를 들어 송장 100개 중 70개는 `created, approved, paid`, 25개는 `created, rejected`, 5개는 `created, rejected, created, approved, paid`를 거쳤다면, 경로 탐색기는 세 경로와 각각의 빈도 70, 25, 5를 보여 줍니다. 로그 객체의 Path 필드가 이런 순서열을 담는 용도입니다.

<a id="duration-distribution"></a>
#### 소요 시간 분포 (Duration distribution)

소요 시간 분포 필터로 성능 이상치를 찾고 상태별로 머문 시간을 분석합니다.

소요 시간 차트는 그래프의 선택에 반응하며, 구성된 노드 및 간선 선택 옵션을 따릅니다.

개별 버킷이나 버킷 범위를 선택하면 출력 객체 집합이 필터링됩니다. 차트 선택과 그래프 선택을 결합하면 특정 전이나 상태에서 너무 오래 걸리는 것처럼 바람직하지 않은 동작을 보이는 객체를 찾을 수 있습니다.

![객체가 상태 사이를 통과하는 데 얼마나 걸리는지 보려면 소요 시간 분포를 확인합니다.](https://www.palantir.com/docs/resources/foundry/machinery/widget-duration-distribution.png)

**설명**: 버킷은 히스토그램의 구간입니다. 예를 들어 `in_review` 상태에 머문 시간을 0\~1일, 1\~3일, 3\~7일, 7일 이상 구간으로 나눠 각 구간의 객체 수를 막대로 그린 것이 소요 시간 분포 차트이고, "7일 이상" 버킷을 선택하면 그 객체들만 출력 객체 집합에 남습니다.

> **중간 요약**: 위젯 사용자는 메트릭 보기를 순환하고 노드 메트릭을 고정할 수 있으며, 기본적으로 정의에 부합하는 프로세스만 보입니다(로그 객체 100만 개 초과 시 해제). 노드, 간선, 경로, 소요 시간 버킷을 선택해 출력 객체 집합을 필터링하고, 전이 노드, 하위 프로세스, 이탈 표시를 헤더에서 켜고 끌 수 있습니다.

## 정리

- Machinery 위젯은 Workshop에서 Machinery 그래프를 메트릭과 흐름을 담은 시각화로 보여 주며, Machinery 애플리케이션 안의 제한된 독립 보기로도 쓸 수 있습니다.
- 구성 시 그래프 리소스를 고르고 루트 프로세스마다 입력 객체 집합을 지정하면, 하위 프로세스 객체는 링크 타입으로 자동 도출됩니다. 레거시 위젯은 **Use Machinery v2**로 업그레이드합니다.
- 기본 메트릭 보기는 누적/현재 개수와 누적/현재 소요 시간 네 가지이며, 빌더가 추가하거나 바꿀 수 있습니다.
- 출력 객체 집합은 노드, 간선, 경로 탐색기, 소요 시간 분포 선택에 따라 동적으로 필터링됩니다.
- 적합성 필터링과 이탈 숨김이 기본이므로, 정의에 없는 상태를 거친 객체는 메트릭에서 빠진다는 점에 유의합니다.
