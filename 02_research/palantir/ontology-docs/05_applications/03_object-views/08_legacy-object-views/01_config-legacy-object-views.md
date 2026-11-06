# 레거시 Object View 구성하기 (Configure legacy Object Views)

- 원문: https://www.palantir.com/docs/foundry/object-views/config-legacy-object-views/
- 사이드바 위치: Applications > Object Views > Legacy Object Views > Configure legacy Object Views

이 페이지는 Workshop 기반 편집기 이전에 쓰이던 레거시(legacy) Object View 구성 방식을 설명합니다. 레거시 탭은 위젯(widget)을 섹션 단위로 쌓아 화면을 만드는 방식이며, 새로 만들 수는 없지만 기존 탭은 여전히 지원되므로 이미 운영 중인 Object View를 유지보수하려면 이 구성 방법을 알아야 합니다.

레거시 Object View 구성에 접근하려면, 객체 타입의 Object View 편집기로 이동해 **Manage tabs** 톱니바퀴 아이콘을 선택한 다음, 탭 위에 마우스를 올려 **Open in legacy editor**(레거시 편집기에서 열기) 아이콘을 선택합니다.

<a id="configure-tabs"></a>
## 탭 구성하기 (Configure tabs)

레거시 위젯 기반 탭은 섹션으로 정리된 위젯 목록을 표시합니다. 탭 설정 안에서 위젯을 추가, 삭제, 재정렬하거나 다른 설정으로 이동할 수 있습니다.

![Object View에서 레거시 위젯 기반 탭 구성하기.](https://www.palantir.com/docs/resources/foundry/object-views/configure-widgets.png)

<a id="configure-widgets"></a>
## 위젯 구성하기 (Configure widgets)

레거시 Object View 탭을 이루는 구성 요소를 **위젯(widgets)이라고** 부릅니다. 위젯은 *섹션(Sections)* 또는 *플러그인(Plugins)이라고도* 불립니다. 위젯은 Object View에서 어떤 형태로든 데이터를 표시하는 주된 수단입니다. 위젯을 사용해 데이터를 KPI나 차트로 시각화하고, Object View 전체의 레이아웃을 배치하고, 표시된 데이터를 조작합니다.

Object View에서 사용할 수 있는 위젯 유형은 다음과 같습니다.

* [속성과 링크(Properties and links)](05_widgets-properties-links.md)
* [시각화(Visualize)](06_widgets-visualization.md)
* [필터(Filters)](07_widgets-filtering.md)
* [레이아웃(Layout)](08_widgets-layout.md)
* [다른 애플리케이션과 파일 삽입(Embed other applications and files)](09_widgets-apps-files.md)

> **중간 요약**: 레거시 편집기는 Manage tabs 대화 상자의 **Open in legacy editor** 아이콘으로 엽니다. 레거시 탭은 섹션으로 정리된 위젯 목록이며, 위젯은 속성과 링크, 시각화, 필터, 레이아웃, 삽입 유형으로 나뉩니다.

<a id="widget-specific-settings"></a>
## 위젯별 설정 (Widget-specific settings)

위젯은 객체와 관련된 데이터를 시각화하거나 조작하는 데 사용됩니다.
위젯은 보통 다음 중 하나에 접근합니다.

* 현재 객체의 속성
* 현재 객체에 링크된 객체
* 현재 객체에 링크된 객체들의 속성에 대한 집계

Object View에서 위젯을 구성할 때는 어떤 객체와 어떤 속성을 시각화할지 정합니다. 관련 객체를 미리 설정하고, 온톨로지 메타데이터 안에서 링크를 미리 정의해 두어야 합니다.

각 위젯의 구체적인 설정은 그 위젯이 제공하는 기능에 따라 고유합니다. 일반적으로 위젯별 구성에는 두 가지 주요 요소가 있습니다.

* **객체 모델(object model)** 구성: 객체 또는 링크된 객체를 선택하고, 어떤 속성을 사용할지 고릅니다. 예를 들어 차트를 구성할 때 한 공항(Airport)에 속한 모든 항공편(Flights)을 목적지(Destination)별로 집계해야 할 수 있습니다.
* **시각(visual)** 구성: 차트 종류, 색상, 형식, 텍스트 레이블 같은 옵션을 선택합니다.

**설명**: 원문의 차트 예시를 SQL로 옮기면 현재 보고 있는 Airport 객체의 키가 `JFK`일 때 `SELECT destination, COUNT(*) FROM flights WHERE origin_airport = 'JFK' GROUP BY destination`과 같은 계산입니다. 여기서 Airport와 Flight 사이의 링크 타입이 조인 조건(`origin_airport = airport_id`)에 해당하므로, 원문이 말하듯 링크를 온톨로지에 먼저 정의해 두어야 위젯이 링크된 객체를 찾아 집계할 수 있습니다.

> **중간 요약**: 위젯은 현재 객체의 속성, 링크된 객체, 링크된 객체의 집계 중 하나를 다루며, 이를 위해 링크가 온톨로지에 미리 정의되어 있어야 합니다. 위젯 설정은 데이터를 고르는 객체 모델 구성과 모양을 정하는 시각 구성으로 나뉩니다.

<a id="widget-format-settings"></a>
## 위젯 형식 설정 (Widget format settings)

모든 위젯에는 기본 형식 설정이 있습니다.

**일반(General)**

* **Title**(제목): 위젯 헤더에 표시할 제목을 추가합니다. 기본값은 위젯 이름이거나 빈 칸입니다. 위젯을 저장하려면 반드시 제목을 추가해야 합니다.
* **Icon**(아이콘): 위젯 헤더 왼쪽 위에 표시할 아이콘을 고릅니다. 각 위젯에는 기본 아이콘이 있습니다.
* **Help Info**(도움말 정보): 기본적으로 비어 있으며, 사용자에게 위젯을 설명하는 텍스트를 추가할 수 있습니다.

![Object View에서 일반 형식 설정 편집하기](https://www.palantir.com/docs/resources/foundry/object-views/widget-general-format-settings.png)

**레이아웃(Layout)**

* **Alignment**(정렬): 위젯이 Object View의 전체 너비를 차지할지, 아니면 두 위젯을 나란히 배치하기 위해 오른쪽 또는 왼쪽 정렬을 할지 선택할 수 있습니다. 정렬의 기본값은 전체 너비입니다.
* **Sizing**(크기 조정): 크기 조정 설정은 모든 위젯에 있는 것은 아닙니다. 이 설정이 있는 경우, Object View 안에서 해당 섹션의 최소 높이와 최대 높이를 제어할 수 있습니다.

<a id="reuse-widget-configurations"></a>
## 위젯 구성 재사용하기 (Reuse widget configurations)

이전에 만든 위젯의 구성은 YAML 구성을 복사해 재사용할 수 있습니다. Object View 편집 화면의 오른쪽 위 모서리에 있는 코드 아이콘을 선택해 구성에 접근합니다. 그런 다음 그 구성을 복사해 새 위젯의 YAML 구성에 붙여 넣습니다.

![위젯 구성을 재사용하기 위해 YAML 구성 열기](https://www.palantir.com/docs/resources/foundry/object-views/access-yaml-config.png)

**설명**: YAML은 들여쓰기로 계층 구조를 표현하는 텍스트 형식의 설정 파일 문법입니다. 위젯의 설정(어떤 속성을 보여 줄지, 제목, 정렬 등)이 내부적으로 YAML 텍스트로 저장되므로, 이 텍스트를 그대로 복사해 다른 위젯에 붙이면 같은 설정을 화면 클릭 없이 한 번에 옮길 수 있습니다.

> **중간 요약**: 모든 위젯에는 제목(필수), 아이콘, 도움말 같은 일반 설정과 정렬, 크기 조정 같은 레이아웃 설정이 있습니다. 위젯 구성은 YAML 텍스트를 복사해 다른 위젯에 붙여 넣는 방식으로 재사용합니다.

## 정리

- 레거시 Object View 편집기는 Manage tabs 대화 상자의 **Open in legacy editor** 아이콘으로 엽니다.
- 레거시 탭은 섹션으로 정리된 위젯 목록이며, 위젯은 속성과 링크, 시각화, 필터, 레이아웃, 삽입 유형이 있습니다.
- 위젯은 현재 객체의 속성, 링크된 객체, 링크된 객체의 집계를 다루며, 객체 모델 구성과 시각 구성을 따로 설정합니다.
- 모든 위젯에 제목, 아이콘, 도움말, 정렬, 크기 조정 같은 공통 형식 설정이 있고, 제목 없이는 저장되지 않습니다.
- YAML 구성을 복사해 위젯 설정을 재사용할 수 있습니다.
