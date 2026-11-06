# 패널 Object View 구성하기 (Configure panel Object Views)

- 원문: https://www.palantir.com/docs/foundry/object-views/config-panel-views/
- 사이드바 위치: Applications > Object Views > Panel Object Views > Configure panel Object Views

이 페이지는 구성된 패널 Object View의 두 종류(객체 인스턴스 패널, 객체 집합 패널)가 기본적으로 어떤 내용을 담는지, 그리고 편집기에서 두 종류를 전환하고 좁은 패널 크기에 맞춰 화면을 설계하는 방법을 설명합니다. 패널은 다른 애플리케이션 옆에 붙는 작은 화면이므로, 실제 표시 크기를 가늠하며 편집하는 기능이 함께 제공됩니다.

객체 타입의 객체 하나 또는 여러 개를 표시하기 위해 만들 수 있는 구성된 패널 Object View에는 두 종류가 있습니다. [*객체 인스턴스 패널(object instance panels)*](#object-instance-panels)은 개별 객체를 표시하고, [*객체 집합 패널(object set panels)*](#object-set-panels)은 여러 객체를 객체 집합으로 표시합니다. 두 종류의 구성된 Object View는 같은 [편집 진입점](../04_config-overview.md#edit-configured-object-views)과 같은 구성 방식을 공유합니다.

<a id="object-instance-panels"></a>
## 객체 인스턴스 패널 (Object instance panels)

기본 객체 인스턴스 패널 뷰는 [Property List 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-property-list/) 하나를 보여 주며, 이 위젯은 객체 타입의 인스턴스 하나에 대한 [주요 속성(prominent properties)](../../../02_define-ontologies/02_object-and-link-types/03_properties/05_property-metadata.md#metadata-reference)을 표시합니다.

**설명**: 주요 속성은 객체 타입을 정의할 때 "이 속성은 중요하니 먼저 보여 달라"고 표시해 둔 속성입니다. 예를 들어 Employee 객체 타입에 속성이 30개 있어도 `name`, `department`, `title` 세 개만 주요 속성으로 지정해 두면 좁은 패널에는 이 세 개만 표시됩니다.

<a id="object-set-panels"></a>
## 객체 집합 패널 (Object set panels)

객체 집합 패널은 같은 객체 타입에 속한 여러 인스턴스를 집계한 뷰를 표시합니다. 기본 객체 집합 패널은 탭 레이아웃으로 되어 있으며, 객체 모음을 탐색할 수 있는 두 가지 인터페이스를 제공합니다.

* **Charts** 탭은 최대 5개의 [XY 차트(XY Charts)](https://www.palantir.com/docs/foundry/workshop/widgets-chart/)를 표시하며, 이 차트들은 속성 값으로 그룹화한 객체 집계를 시각화합니다.
* **List** 탭은 [Object List 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-object-list/)을 보여 주며, 객체마다 최대 3개의 속성을 표시합니다. 여기에는 객체의 제목, 주요 속성, 그리고 미디어가 있으면 미디어가 포함됩니다.

**설명**: "속성 값으로 그룹화한 집계"는 SQL의 `SELECT department, COUNT(*) FROM employees GROUP BY department`와 같은 계산입니다. 선택된 Employee 객체 집합이 있다면 Charts 탭은 부서별 인원수 같은 막대 차트를 보여 주고, List 탭은 각 직원을 한 줄씩 나열합니다.

> **중간 요약**: 기본 객체 인스턴스 패널은 주요 속성을 보여 주는 Property List 위젯 하나로 이루어집니다. 기본 객체 집합 패널은 최대 5개의 그룹별 집계 차트를 보여 주는 Charts 탭과 객체를 나열하는 List 탭으로 이루어집니다.

<a id="edit-configured-panel-object-views"></a>
## 구성된 패널 Object View 편집하기 (Edit configured panel Object Views)

두 종류의 구성된 패널 Object View 중 어느 것이든 변경하려면 [편집 진입점](../04_config-overview.md#edit-configured-object-views) 중 하나를 이용해 구성된 Object View 편집기로 이동합니다. 편집기에 들어가면 [Workshop 모듈](https://www.palantir.com/docs/foundry/workshop/overview/)을 꾸미는 것과 같은 방식으로 구성된 패널 Object View의 콘텐츠를 사용자 정의할 수 있습니다.

객체 인스턴스 패널 뷰를 구성하는 중에 객체 집합으로 전환하고 싶다면, 상단 리본에서 **Object instance**를 선택한 다음 드롭다운 메뉴에서 **Object set**을 고릅니다. 같은 메뉴로 **Object set**에서 **Object instance**로 전환할 수도 있습니다.

![패널 Object View 종류 전환.](https://www.palantir.com/docs/resources/foundry/object-views/panel-object-view-type-switching.png)

왼쪽 패널의 설정 영역에 있는 **Module Type** 섹션에서는 편집 캔버스의 크기를 구성해 간결한 모듈을 만들기 쉽게 할 수 있습니다.

* **Edit display size**(표시 크기 편집): 드롭다운에서 옵션을 선택하면 캔버스에 보이는 패널의 미리 보기 크기가 조정됩니다. 실제 패널 크기는 기기와 애플리케이션마다 다르므로, 이 기능은 빌더가 여러 워크플로에서 쓸 수 있는 공간을 대략 가늠하기 위한 도구일 뿐입니다.
  * 표시 옵션에는 여러 플랫폼 애플리케이션의 패널 크기에 맞춘 **application presets**(애플리케이션 프리셋), 일반적인 **resolution presets**(해상도 프리셋), 모듈의 높이와 너비를 픽셀 단위로 입력하는 **manual entry**(직접 입력)가 있습니다.
* **Show resolution picker in canvas**(캔버스에 해상도 선택기 표시): 켜면 편집기 왼쪽 아래 모서리에 해상도 선택기가 표시되어, 빌더가 캔버스에서 바로 모듈의 표시 크기를 편집할 수 있습니다.
* **Fit to canvas**(캔버스에 맞추기): 해상도 크기가 캔버스 크기를 넘으면 해상도 선택기 옆에 버튼이 나타나며, 이 버튼으로 패널 전체를 화면에 맞춰 보는 방식과 표준 배율로 보는 방식을 전환합니다.

![패널 Object View 구성 옵션.](https://www.palantir.com/docs/resources/foundry/object-views/panel-object-view-configuration.gif)

**설명**: 이 설정들은 사용자에게 보이는 결과를 바꾸는 것이 아니라 편집하는 사람의 미리 보기 화면만 바꿉니다. 웹 개발에서 브라우저 개발자 도구로 모바일 화면 크기를 흉내 내어 레이아웃을 확인하는 것과 같은 목적의 기능입니다.

> **중간 요약**: 패널 편집은 편집기에서 Workshop 모듈처럼 하며, 상단 리본 메뉴로 객체 인스턴스와 객체 집합 사이를 전환합니다. **Module Type** 섹션의 표시 크기, 해상도 선택기, 캔버스 맞춤 설정으로 실제 패널 크기를 가늠하며 편집할 수 있습니다.

## 정리

- 구성된 패널 Object View에는 객체 하나를 보여 주는 객체 인스턴스 패널과 여러 객체를 집계해 보여 주는 객체 집합 패널이 있습니다.
- 기본 인스턴스 패널은 주요 속성의 Property List 위젯, 기본 집합 패널은 Charts 탭(최대 5개 XY 차트)과 List 탭(Object List 위젯)으로 구성됩니다.
- 두 종류 모두 같은 편집 진입점과 Workshop 방식의 편집을 쓰며, 상단 리본에서 서로 전환할 수 있습니다.
- **Module Type** 설정으로 미리 보기 크기를 조정해 좁은 패널에 맞는 화면을 설계합니다.
