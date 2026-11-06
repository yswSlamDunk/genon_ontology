# 온톨로지 인식 애플리케이션 (Ontology-aware applications)

- 원문: https://www.palantir.com/docs/foundry/ontology/applications/
- 사이드바 위치: Ontology building > Ontology-aware applications

온톨로지(Ontology)를 만든 뒤 실제 사용자는 Object Views, Object Explorer, Quiver, Workshop, Slate, Carbon, Map 같은 애플리케이션을 통해 객체를 보고 분석하고 변경합니다. 이 페이지는 각 애플리케이션이 무엇을 하는지 소개하고, 사용 사례, 워크플로 스타일, 구성 모델이라는 세 기준으로 비교해 어떤 상황에 무엇을 써야 하는지 안내합니다.

Foundry에는 온톨로지 위에서 기본적으로(natively) 동작하도록 개발된 여러 애플리케이션이 있습니다. 이러한 객체 인식(object-aware) 애플리케이션들은 함께 다양한 사용 사례와 사용자 유형을 지원하는 강력한 분석 및 운영 플랫폼을 제공합니다.

온톨로지를 구축하고 객체 인식 애플리케이션을 사용하는 것이 왜 가치 있는지 더 알아보려면 [이 페이지](02_why-ontology.md)를 참고하세요.

이 페이지는 사용할 수 있는 애플리케이션에 대한 참고 자료를 제공하고, 각각을 언제 사용해야 하는지 설명합니다.

* [애플리케이션 참고 자료](#application-reference)
* [애플리케이션 비교](#application-comparison)

**설명**: "객체 인식(object-aware)" 또는 "온톨로지 인식(ontology-aware)" 애플리케이션이란, 데이터를 행과 열의 테이블로만 다루지 않고 온톨로지에 정의된 객체 타입, 속성(property), 링크, 액션을 이해하고 그 단위로 화면을 구성하는 애플리케이션을 뜻합니다. 예를 들어 Airport 객체를 열면 그 공항에 링크된 Flight 객체 목록을 자동으로 보여 줄 수 있는 것은 애플리케이션이 링크 타입 정의를 알고 있기 때문입니다.

<a id="application-reference"></a>
## 애플리케이션 참고 자료 (Application reference)

<a id="object-views"></a>
### Object Views

[**Object Views는**](../05_applications/03_object-views/01_overview.md) 특정 객체와 관련된 모든 정보와 워크플로를 모아 둔 중심 허브입니다. 여기에는 객체에 대한 핵심 "기본 신상 데이터(biographical data)", 링크된 객체, 주요 관련 지표, 그리고 해당 객체와 관련된 주요 분석, 대시보드, 애플리케이션으로 가는 링크(또는 이들을 임베드한 것)가 포함됩니다.

예를 들어 `Airport` 객체 타입의 Object View는 각 `Airport` 객체에 대해 다음 정보를 제공할 수 있습니다.

* `country`, `city`, `longitude`, `latitude` 등의 기본 신상 데이터
* 해당 `Airport`에 링크된 모든 `Aircraft` 객체와 `Flight` 객체에 대한 360도 뷰
* 임베드된 `Airport Covid Response` 워크플로
* 해당 `Airport`와 관련된 `Flight delay` 이벤트의 `Root-Cause Analysis`로 가는 링크

![Object View 허브 예시](https://www.palantir.com/docs/resources/foundry/ontology/object-apps-object-view-hub.png)

**설명**: "360도 뷰"는 한 대상과 연결된 모든 관련 정보를 한 화면에 모아 보여 주는 것을 가리키는 업계 용어입니다. 데이터베이스로 치면 `airports` 테이블의 한 행을 기준으로 `flights`, `aircraft` 등 외래 키로 연결된 테이블의 관련 행을 모두 조인해 한 페이지에 보여 주는 상세 화면입니다.

<a id="object-explorer"></a>
### Object Explorer

[**Object Explorer는**](../05_applications/01_object-explorer/01_overview.md) 온톨로지 계층에 있는 무엇에 대해서든 질문에 답할 수 있는 검색 및 분석 도구입니다. 사용자는 단순한 필터부터 Search Around까지 다양한 검색 질의를 시각적으로 구성해 관심 있는 객체를 찾을 수 있습니다. 그런 다음 탐색 뷰(exploration view)를 사용해 결과 객체 집합(object set)을 탐색하거나, 결과를 테이블로 볼 수 있습니다. 또한 사용자는 객체 집합들을 서로 비교하고 대조할 수 있으며, 객체 집합에 대해 일괄 액션(예: 라이트백(writeback))을 수행할 수 있습니다. 이후 객체 집합을 내보내거나 Workshop 같은 호환 애플리케이션에서 열 수 있습니다.

탐색 뷰는 미리 설정되어 있으면서 구성도 가능한 시각화(차트나 지도 등)의 모음으로, 사용자는 이를 활용해 객체의 특정 하위 집합으로 더 깊이 파고들(drill-down) 수 있습니다. Object Explorer는 사전 구성이 필요 없으며, 기술적 배경이 적은 사용자를 대상으로 합니다.

![Object Explorer](https://www.palantir.com/docs/resources/foundry/ontology/object-apps-oe.png)

**설명**: "Search Around"는 현재 객체 집합에서 링크를 따라 연결된 다른 객체 집합으로 이동하는 검색입니다. 예를 들어 "지연된 Flight 객체 집합"에서 Search Around로 "그 비행에 쓰인 Aircraft 객체 집합"을 얻는 식이며, SQL로는 조건으로 걸러 낸 행들에 다른 테이블을 조인해 연결된 쪽 행을 가져오는 것에 해당합니다. "드릴다운(drill-down)"은 전체 요약에서 시작해 조건을 하나씩 더하며 세부 데이터로 좁혀 들어가는 분석 방식입니다.

<a id="quiver"></a>
### Quiver

[**Quiver는**](https://www.palantir.com/docs/foundry/quiver/overview/) 시각적인 포인트 앤 클릭(point-and-click) 인터페이스와 강력한 차트 라이브러리를 통해 온톨로지 계층에서 고급 분석 워크플로를 가능하게 합니다. Quiver는 단순한 선형 드릴다운 분석부터, 집계와 통계 함수를 사용하는 많이 분기된 복잡한 분석까지 모두 지원할 수 있습니다. Quiver는 시계열 분석도 기본으로 지원합니다. Quiver 분석은 템플릿화하여 더 많은 사람이 볼 수 있는 읽기 전용 대시보드로 만들 수 있습니다.

![Quiver](https://www.palantir.com/docs/resources/foundry/ontology/object-apps-quiver.png)

<a id="workshop"></a>
### Workshop

[**Workshop은**](https://www.palantir.com/docs/foundry/workshop/overview/) 온톨로지 계층 위에서 코드 없이 포인트 앤 클릭으로 애플리케이션을 만들 수 있게 해 줍니다. Workshop으로 만든 애플리케이션은 다른 포인트 앤 클릭 도구로 만든 일반적인 대시보드보다 더 동적이고 상호작용성이 높습니다.

품질 높은 [레이아웃(Layouts)](https://www.palantir.com/docs/foundry/workshop/concepts-layouts/)과 사용하기 쉬우면서도 정교한 [이벤트 시스템(Events system)](https://www.palantir.com/docs/foundry/workshop/concepts-events/)을 활용함으로써, Workshop 애플리케이션은 직접 개발한 React 애플리케이션만큼 사용자 친화적이고 품질 높은 것을 목표로 합니다.

*Workshop 편집기 화면*

![Workshop 편집기 화면](https://www.palantir.com/docs/resources/foundry/ontology/object-apps-workshop-editor-view.png)

*완성된 Workshop 모듈*

![완성된 Workshop 모듈](https://www.palantir.com/docs/resources/foundry/ontology/object-apps-workshop-module.png)

**설명**: React는 웹 화면을 컴포넌트 단위 코드로 작성하는 JavaScript 라이브러리입니다. Workshop은 이런 코드를 직접 쓰지 않고, 위젯(widget)을 화면에 배치하고 "이 표에서 행을 선택하면 저 차트를 갱신" 같은 이벤트 연결을 설정하는 방식으로 애플리케이션을 만듭니다. Workshop에서 만든 애플리케이션 하나를 모듈(module)이라고 부릅니다.

<a id="slate"></a>
### Slate

[**Slate는**](https://www.palantir.com/docs/foundry/slate/overview/) Workshop보다 더 많은 기술적 구성과 코드가 필요한 Foundry용 유연한 애플리케이션 빌더입니다. Slate 애플리케이션은 온톨로지 계층과 상호작용하지만, Foundry 데이터셋과 직접 상호작용할 수도 있습니다. Slate는 웹 개발 패러다임을 바탕으로 상당한 수준의 시각적 커스터마이징을 할 수 있고 사용 가능한 기능도 폭넓지만, 애플리케이션을 만들고 유지보수하는 데 Workshop보다 더 많은 기술 지식이 필요합니다.

*Slate 편집기 화면*

![Slate 편집기 화면](https://www.palantir.com/docs/resources/foundry/ontology/object-apps-slate-editor-view.png)

*Slate 애플리케이션 화면*

![Slate 애플리케이션 화면](https://www.palantir.com/docs/resources/foundry/ontology/object-apps-slate-app-view.png)

<a id="carbon"></a>
### Carbon

[**Carbon은**](https://www.palantir.com/docs/foundry/carbon/overview/) Foundry의 여러 리소스나 애플리케이션을 결합해 운영 사용자를 위해 잘 다듬어진 *워크스페이스(workspace)를* 만들 수 있게 해 줍니다. 대시보드 같은 분석 결과, Workshop이나 Slate로 만든 애플리케이션, Object Views와 Object Explorer 같은 기본 제공 기능을 결합할 수 있게 함으로써, Carbon은 워크플로 구축자가 커스터마이징의 "마지막 단계(last mile)"를 수행해 최종 사용자에게 고도로 맞춤화되고 사용하기 쉬운 경험을 만들 수 있게 합니다.

![Carbon 워크스페이스](https://www.palantir.com/docs/resources/foundry/ontology/carbon-workspace.png)

<a id="map"></a>
### Map

[**Map**](../05_applications/08_map/01_overview.md) 애플리케이션을 사용하면 객체와 기타 데이터를 지리공간적 맥락에서 한데 모아 분석할 수 있습니다.

![Map 애플리케이션](https://www.palantir.com/docs/resources/foundry/ontology/map-overview.png)

> **중간 요약**: Object Views는 객체 하나의 정보 허브, Object Explorer는 검색과 탐색, Quiver는 고급 분석과 대시보드, Workshop은 코드 없는 애플리케이션 구축, Slate는 코드 기반의 유연한 애플리케이션 구축, Carbon은 여러 리소스를 묶은 워크스페이스, Map은 지리공간 분석 도구입니다.

<a id="application-comparison"></a>
## 애플리케이션 비교 (Application comparison)

객체 인식 애플리케이션들은 몇 가지 측면에서 서로 다릅니다. 특히 중요한 세 가지 측면은 다음과 같습니다.

* 애플리케이션의 [주요 사용 사례](#use-cases)
* 애플리케이션의 [워크플로 스타일](#workflow-style)
* 애플리케이션의 [구성 모델](#configuration-model)

| Foundry 애플리케이션 | [주요 사용 사례](#use-cases) | [워크플로 스타일](#workflow-style) | [구성 모델](#configuration-model) | 객체 또는 데이터셋 |
| --- | --- | --- | --- | --- |
|[Object Views](#object-views) | 발견(Discovery) | 워크플로 특화 | 즉시 사용 가능 | 객체 |
|[Object Explorer](#object-explorer) | 발견 및 분석 | 탐색형 | 즉시 사용 가능 | 객체 |
|[Quiver](#quiver) | 분석 및 대시보드 | 탐색형(분석 모드), 워크플로 특화(대시보드 모드) | 즉시 사용 가능(분석 모드), 커스터마이징 가능(대시보드 모드) | 객체 |
|[Workshop](#workshop) | 애플리케이션 및 대시보드 | 워크플로 특화 | 커스터마이징 가능 | 객체 |
|[Slate](#slate) | 애플리케이션 및 대시보드(복잡한 경우) | 워크플로 특화 | 커스터마이징 가능 | 객체(권장) 및 데이터셋 |
|[Map](#map) | 지리공간 | 탐색형 또는 워크플로 특화 | 즉시 사용 가능 | 객체 |

<a id="use-cases"></a>
### 사용 사례 (Use cases)

객체 인식 애플리케이션이 지원하는 주요 사용 사례는 **발견(Discovery)**, **분석(Analysis)**, **대시보드(Dashboards)**, **애플리케이션(Applications)입니다**.

* **발견(Discovery)은** 사용자가 올바른 정보나 워크플로를 찾을 수 있게 합니다. 발견은 주로 두 가지 핵심 기능, 즉 큐레이션된 콘텐츠 허브와 검색을 통해 가능해집니다. 큐레이션된 콘텐츠 허브(랜딩 페이지 또는 "360 뷰"라고도 함)는 모든 사용자를 위한 포괄적인 표준 뷰부터 특정 사용자 집단이나 사용 사례를 위한 맞춤 뷰까지 다양합니다. 검색 기능은 핵심 키워드에 대한 자유 텍스트 검색뿐 아니라, 링크 탐색이나 드릴다운을 통한 반복적인 검색으로도 발견을 지원합니다.
* **분석(Analysis)은** 사용자가 폭넓은 질문에 답할 수 있게 합니다. 질문은 단순한 것(*특정 제품의 평균 고객 유지율은 얼마인가?*)부터 매우 복잡한 것(*세 개의 서로 다른 고객 집단(cohort)이 모든 제품 전체와 개별 제품 각각에 대해 시간에 따른 유지율과 전체 매출 측면에서 어떻게 비교되는가?*)까지 다양합니다. 분석 경로는 탐색적입니다. 즉, 최종 사용자 스스로 경로를 정하며 대개 매우 반복적입니다. 처음 질문에 답이 나오면 새로운 질문이 생기고 그것이 분석 경로에 추가됩니다.
* **대시보드(Dashboards)는** 미리 구성된 시각화의 모음으로, 주로 더 넓은 소비자 사용자층이 읽기 전용으로 사용합니다. 대시보드는 의미 있는 *분석을* 정기 보고나 운영 모니터링으로 바꾸는 데 자주 쓰입니다. 대시보드는 많은 수의 차트와 기타 시각화가 특징이지만, *애플리케이션*(아래 참조)만큼 커스터마이징하거나 상호작용할 수 있지는 않습니다. 대시보드는 사용자가 시각화를 데이터의 여러 하위 집합으로 걸러 볼 수 있도록 파라미터화되는 경우가 많습니다.
* **애플리케이션(Applications)은** 특정 사용자 그룹이 특정 문제를 해결하도록 만든 상호작용형 맞춤 운영 인터페이스입니다. 애플리케이션은 대개 대시보드보다 복잡하며, 사용자가 정해진 경로를 따라가는(on-rails) 특정 워크플로를 수행하도록 하는 데 초점을 둡니다. 애플리케이션에는 의사결정에 필요한 큐레이션된 분석 콘텐츠(예: 통계, 차트, 그래프 등)가 일부 포함될 수 있지만, 일반적으로 여러 워크플로 요소도 갖추고 있으며 사용자 입력(예: 라이트백)을 받는 경우가 많습니다.

**설명**: 대시보드와 애플리케이션의 가장 큰 차이는 "쓰기" 여부입니다. 대시보드는 데이터를 읽어 보여 주는 화면(SQL의 `SELECT` 결과를 차트로 그린 것)이고, 애플리케이션은 사용자가 입력 폼을 채우고 버튼을 눌러 객체를 수정하는 화면(액션을 통해 데이터가 바뀜)까지 포함합니다. "파라미터화"는 대시보드에 날짜 범위나 지역 같은 입력값을 두어, 같은 차트를 다른 조건으로 다시 그릴 수 있게 하는 것입니다.

<a id="workflow-style"></a>
### 워크플로 스타일 (Workflow style)

객체 인식 애플리케이션은 주된 워크플로 스타일에 맞춰 최적화되어 있습니다.

* **탐색형 애플리케이션(Exploratory applications)은** "빌더(builder)" 사용자가 미리 구성할 필요가 없으며, 데이터가 온톨로지로 모델링되는 즉시 최종 사용자가 별도 준비 없이 바로 사용합니다. 탐색형 애플리케이션에서는 최종 사용자가 자신의 분석 경로를 정하며, 미리 정해지지 않은 폭넓은 질문에 답할 수 있습니다. 탐색형 애플리케이션에는 일반적으로 이를 가능하게 하는 검색, 시각화, 변환 기능이 갖춰져 있습니다. 주로 탐색형인 객체 인식 애플리케이션으로는 Object Explorer와 Quiver가 있습니다.
* **워크플로 특화 애플리케이션(Workflow-specific applications)은** 최종 사용자가 실제로 사용하기 전에 "빌더" 사용자가 미리 구성해야 합니다. 이는 두 개의 주요 사용자 그룹, 즉 (1) 특정 대시보드나 애플리케이션을 구성하는 빌더 그룹과 (2) 애플리케이션이 만들어지는 대상인 하위의 최종 사용자를 가지는 대시보드나 애플리케이션에서 일반적입니다. Workshop 모듈과 Slate 모듈은 모두 "빌더" 사용자가 편집 모드에서 미리 구성해야 합니다.

Quiver 같은 일부 애플리케이션은 두 워크플로 스타일을 모두 수용합니다. 주된 모드는 탐색형이지만, 그 결과물을 더 많은 사람이 사용하는 워크플로 특화 산출물로 구성할 수 있기 때문입니다. Quiver 분석(Quiver Analyses)은 매우 탐색적이지만, 더 넓은 대상이 접근할 수 있도록 미리 구성된 분석 뷰인 Quiver 대시보드(Quiver Dashboards)로 게시할 수 있습니다.

<a id="configuration-model"></a>
### 구성 모델 (Configuration model)

구성 모델은 최종 사용자가 사용자 인터페이스를 활용하기 전에 그 인터페이스를 어느 정도까지 구성해야 하는지를 나타냅니다.

* **즉시 사용 가능(Walk-up usable)** 애플리케이션은 구성 요구 사항이나 유지보수 부담이 거의 또는 전혀 없이 사용자가 바로 효과적으로 사용할 수 있습니다. 예를 들어 Object Explorer는 구성 요구 사항이 최소한이거나 아예 없으므로, 온톨로지가 정의되면 최종 사용자가 즉시 사용할 수 있습니다.
* **커스터마이징 가능(Customizable)** 애플리케이션은 최종 사용자의 특정 문제를 해결하는 인터페이스를 구현하기 위해 (흔히 별도의 "빌더" 사용자가) 초기 투자를 해야 합니다. 이는 지속적인 유지보수 비용이 더 높다는 의미이기도 합니다. 그러나 그 결과로 만들어지는 애플리케이션은 일반적으로 특정 워크플로의 요구를 정확히 충족하는 목적 맞춤형 인터페이스가 됩니다. Workshop과 Slate가 이런 커스터마이징 유형의 예입니다.

> **중간 요약**: 애플리케이션은 사용 사례(발견, 분석, 대시보드, 애플리케이션), 워크플로 스타일(탐색형 또는 워크플로 특화), 구성 모델(즉시 사용 가능 또는 커스터마이징 가능)로 비교할 수 있습니다. Object Explorer와 Quiver는 준비 없이 탐색에, Workshop과 Slate는 빌더가 미리 만든 맞춤형 워크플로에 적합합니다.

## 정리

- 온톨로지 위에서 동작하는 객체 인식 애플리케이션으로 Object Views, Object Explorer, Quiver, Workshop, Slate, Carbon, Map이 있습니다.
- Object Views와 Object Explorer는 객체를 찾고 살펴보는 데, Quiver는 고급 분석과 대시보드에, Map은 지리공간 분석에 쓰입니다.
- Workshop은 코드 없이, Slate는 코드와 함께 맞춤형 애플리케이션을 만들며, Slate는 데이터셋에도 직접 접근할 수 있습니다.
- Carbon은 여러 리소스와 애플리케이션을 하나의 워크스페이스로 묶습니다.
- 애플리케이션 선택 기준은 사용 사례, 워크플로 스타일(탐색형 또는 워크플로 특화), 구성 모델(즉시 사용 가능 또는 커스터마이징 가능)입니다.
