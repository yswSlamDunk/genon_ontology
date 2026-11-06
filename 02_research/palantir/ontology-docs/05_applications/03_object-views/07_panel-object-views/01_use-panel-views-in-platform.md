# 플랫폼에서 패널 Object View 사용하기 (Use panel Object Views in the platform)

- 원문: https://www.palantir.com/docs/foundry/object-views/use-panel-views-in-platform/
- 사이드바 위치: Applications > Object Views > Panel Object Views > Use panel Object Views in the platform

이 페이지는 좁은 공간에 객체 정보를 간결하게 보여 주는 패널(panel) Object View가 어디에 나타나는지 설명합니다. 객체 하나를 보여 주는 객체 인스턴스 패널과 여러 객체를 묶어 보여 주는 객체 집합 패널의 차이, 그리고 Workshop 앱에서 패널을 쓰는 방법을 다룹니다.

패널 Object View(panel Object View)는 Palantir 플랫폼 곳곳의 애플리케이션에 삽입되어, 여러 워크플로에서 사용자가 객체 데이터를 일관되게 경험할 수 있게 해 줍니다. 모든 객체 타입에는 기본적으로 [표준 Object View](../02_standard-object-views.md) 패널이 제공되며, *객체 인스턴스(object instance)* 또는 *객체 집합(object set)을* 표시하는 [구성된 패널 Object View](02_config-panel-views.md)를 만들 수 있습니다.

**설명**: 객체 인스턴스는 객체 타입에 속한 객체 하나(테이블의 행 하나)이고, 객체 집합은 같은 객체 타입에 속한 여러 객체의 모음(조건에 맞는 행들의 집합)입니다. 패널 Object View는 이 둘 각각에 대해 따로 화면을 정의할 수 있습니다.

<a id="panel-object-views-in-platform-applications"></a>
## 플랫폼 애플리케이션의 패널 Object View (Panel Object Views in platform applications)

패널 Object View는 [Vertex](../../05_vertex/01_overview.md), [Map](../../08_map/01_overview.md), Gaia 같은 Palantir 플랫폼 애플리케이션 곳곳에 나타날 수 있습니다.

<a id="object-instance-panels"></a>
### 객체 인스턴스 패널 (Object instance panels)

객체 인스턴스 패널은 객체 타입의 인스턴스 하나를 표시하며, 애플리케이션의 선택 패널(selection panel)에 나타납니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/panel-object-view-in-vertex.png" alt="Vertex에 삽입된 패널 Object View." width="300">
<img src="https://www.palantir.com/docs/resources/foundry/object-views/panel-object-view-in-maps.png" alt="Maps에 삽입된 패널 Object View." width="300">
<img src="https://www.palantir.com/docs/resources/foundry/object-views/panel-object-view-in-gaia.png" alt="Gaia에 삽입된 패널 Object View." width="300">

<a id="object-set-panels"></a>
### 객체 집합 패널 (Object set panels)

객체 집합 패널은 하나의 객체 타입에 속한 여러 인스턴스를 집계한 뷰를 표시합니다. 같은 객체 타입의 인스턴스 여러 개로 이루어진 객체 집합을 선택하면 애플리케이션에 나타납니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/panel-object-set-view-in-gaia-maps-vertex.png" alt="Gaia, Maps, Vertex에 삽입된 객체 집합 뷰 패널." width="800">

**설명**: 예를 들어 Map 애플리케이션에서 공항 하나를 클릭하면 객체 인스턴스 패널이 열려 그 공항의 속성이 보입니다. 지도에서 범위를 드래그해 공항 20개를 한꺼번에 선택하면 객체 집합 패널이 열리고, 개별 공항 대신 "국가별 공항 수" 같은 집계 결과가 보입니다. SQL로 치면 앞의 것은 `WHERE id = ...`로 행 하나를 조회한 결과이고, 뒤의 것은 여러 행에 `GROUP BY`를 적용한 결과입니다.

> **중간 요약**: 패널 Object View는 Vertex, Map, Gaia 같은 앱에 나타납니다. 객체 하나를 선택하면 객체 인스턴스 패널이, 같은 타입의 객체 여러 개를 선택하면 집계를 보여 주는 객체 집합 패널이 표시됩니다.

<a id="panels-in-workshop-applications"></a>
## Workshop 애플리케이션의 패널 (Panels in Workshop applications)

패널은 사용자 정의 Workshop 애플리케이션에서 객체 데이터를 간결하게 보여 주는 데 사용할 수 있습니다. 이렇게 하려면 Workshop의 [Object View 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-object-view/)을 패널 폼 팩터를 표시하도록 구성해 사용합니다.

![Workshop에 삽입된 패널 Object View.](https://www.palantir.com/docs/resources/foundry/object-views/panel-object-view-in-workshop.gif)

## 정리

- 패널 Object View는 여러 Palantir 애플리케이션에 삽입되어 객체 데이터를 일관된 형태로 간결하게 보여 줍니다.
- 모든 객체 타입에 표준 Object View 패널이 기본 제공되며, 구성된 패널 Object View를 직접 만들 수 있습니다.
- 객체 인스턴스 패널은 객체 하나를, 객체 집합 패널은 같은 타입의 여러 객체를 집계해 보여 줍니다.
- Workshop에서는 Object View 위젯을 패널 폼 팩터로 설정해 사용합니다.
