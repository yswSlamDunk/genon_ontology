# 레이아웃 위젯 (Layout)

- 원문: https://www.palantir.com/docs/foundry/object-views/widgets-layout/
- 사이드바 위치: Applications > Object Views > Legacy Object Views > Layout

이 페이지는 레거시(Legacy) Object View의 한 탭 안에서 화면 배치를 구성하는 레이아웃 위젯(widget)을 다룹니다. 위젯을 가로나 세로로 배치하는 컨테이너, 탭 안에 또 탭을 두는 컨테이너, 조건에 따라 내용을 보이거나 숨기는 컨테이너, 객체의 속성 값을 끼워 넣은 텍스트를 보여 주는 Markdown 위젯의 설정 방법을 설명합니다. 다른 위젯을 담는 위젯들이므로, 앞의 시각화나 필터링 위젯과 함께 조합해 쓰게 됩니다.

**레이아웃 위젯(Layout widgets)은** 특정 탭 안에서 Object View 페이지를 여러 컨테이너로 나누어 배치함으로써 페이지의 레이아웃을 정리하고 구조화하는 데 사용합니다.

각 Object View에는 세 단계의 레이아웃 제어가 있습니다.

* 탭(Tabs): 관련 기능은 [Configuring Tabs](02_config-tabs.md)에서 설명합니다.
* 탭 안의 레이아웃 위젯(컨테이너(Containers)라고도 함): Object View를 콘텐츠 상자 단위로 정리할 수 있게 합니다.
* 모든 콘텐츠 위젯(시각화, 속성과 링크, 필터 등): Object View를 이루는 기본 구성 요소입니다.

**설명**: 세 단계는 포함 관계를 이룹니다. Object View는 탭 여러 개를 가지고, 각 탭은 컨테이너를 가지며, 컨테이너는 콘텐츠 위젯이나 다른 컨테이너를 가집니다. 즉 화면 구성은 루트가 Object View인 트리(tree) 구조이고, 콘텐츠 위젯이 잎(leaf) 노드, 컨테이너가 내부 노드에 해당합니다. 웹 개발에서 HTML의 `<div>` 요소를 중첩해 레이아웃을 만드는 방식과 같은 구조입니다.

레이아웃 컨테이너의 유형은 다음과 같습니다.

* 페이지의 시각적 설계: [Horizontal Distribution](#horizontal-distribution)과 [Vertical Stack Container](#vertical-stack-container).
* 탭 안에 중첩된 콘텐츠 단계를 하나 더 추가: [Tabbed Container](#tabbed-container).
* 사용자가 조작하는 [필터](07_widgets-filtering.md)에 따라 콘텐츠를 표시하거나 숨김: [Conditional Container](#conditional-container).
* 객체 값으로 보강한 텍스트 표시: [Markdown](#markdown) 위젯.

<a id="horizontal-distribution"></a>
## 가로 배치 (Horizontal Distribution)

이 위젯은 컨테이너 안에서 위젯들을 가로로 나란히 배치해 Object View의 레이아웃을 시각적으로 정리할 수 있게 합니다. 다른 위젯을 담는 컨테이너일 뿐이며 그 자체로는 다른 기능이 없습니다.

<a id="configuration"></a>
### 설정 (Configuration)

Horizontal Distribution 위젯을 추가하면, 설정 화면에서 "Add Item"을 클릭해 이 컨테이너 안에 여러 위젯을 추가할 수 있습니다. "Add Item"을 클릭하면 위젯 선택기가 열립니다.

컨테이너 안의 각 위젯에 너비를 얼마나 할당할지 정하는 방법은 두 가지입니다.

* Relative(상대값): 컨테이너 안의 각 위젯에 정수를 하나씩 지정합니다. 위젯은 이 상대적인 숫자에 따라 분배됩니다. 예: 위젯 3개의 크기가 A=1, B=3, C=2이면 위젯 A는 길이의 1/6, 위젯 B는 길이의 3/6을 차지합니다.
* Pixel(픽셀): 각 위젯에 할당할 픽셀 수를 절대값으로 지정합니다. 픽셀 합계가 Object View의 한계(약 1150픽셀)를 넘으면 위젯이 페이지 밖으로 "넘쳐" 나갑니다.

**설명**: Relative 방식의 계산은 각 위젯의 숫자를 전체 합으로 나누는 것입니다. A=1, B=3, C=2이면 합계가 6이므로 A는 1/6, B는 3/6, C는 2/6을 차지합니다. 컨테이너 너비가 1200픽셀이라면 각각 200, 600, 400픽셀이 됩니다. CSS의 `flex-grow` 값과 같은 방식의 비율 분배입니다.

**자주 겪는 문제와 참고 사항:**

* Horizontal Distribution 위젯에는 반드시 제목을 붙이세요. 제목이 있어야 위젯을 추가할 수 있습니다. 제목은 위젯 헤더에 표시됩니다.

<a id="vertical-stack-container"></a>
## 세로 쌓기 컨테이너 (Vertical Stack Container)

이 위젯은 컨테이너 안에서 위젯들을 세로로 위아래로 쌓아 배치해 Object View의 레이아웃을 시각적으로 정리할 수 있게 합니다. 다른 위젯을 담는 컨테이너일 뿐이며 그 자체로는 독립적인 기능이 없습니다.

<a id="configuration"></a>
### 설정 (Configuration)

Vertical Stack Container 위젯을 추가하면, 설정 화면에서 "Add Item"을 클릭해 이 컨테이너 안에 여러 위젯을 추가할 수 있습니다. "Add Item"을 클릭하면 위젯 선택기가 열립니다.

**자주 겪는 문제와 참고 사항:**

* Vertical Stack Container 위젯에는 반드시 제목을 붙이세요. 제목이 있어야 위젯을 추가할 수 있습니다.
* Vertical Stack Container를 다른 위젯 옆에 나란히 배치하려면 설정의 "Format" 탭으로 가서 기본값인 "Full Width" 대신 Left/Right 정렬을 선택하세요.
* 설정의 "Settings" 아래에서 각 탭 옆의 위/아래 화살표 버튼으로 탭 순서를 정합니다. 여기서 탭을 삭제하거나 각 탭 안의 위젯을 교체할 수도 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-vertical-stack.png" alt="세로 쌓기 컨테이너" height="400"/>

> **중간 요약**: Horizontal Distribution과 Vertical Stack Container는 기능 없이 위젯을 가로 또는 세로로 배치만 하는 컨테이너입니다. 가로 배치는 상대 비율이나 픽셀로 너비를 나누며(Object View 너비 한계는 약 1150픽셀), 두 컨테이너 모두 제목이 있어야 추가할 수 있습니다.

<a id="tabbed-container"></a>
## 탭 컨테이너 (Tabbed Container)

현재 탭 안에 탭들을 담는 컨테이너를 만들어 Object View에 탭 계층을 하나 더 추가합니다. 사용자는 이 탭들 사이를 오갈 수 있으며, 각 탭에는 위젯이 하나씩 들어갑니다(이 위젯이 여러 위젯을 담은 컨테이너일 수도 있습니다).

Tabbed Container는 다른 위젯을 담는 컨테이너일 뿐이며 그 자체로는 독립적인 기능이 없습니다.

<a id="configuration"></a>
### 설정 (Configuration)

* Tabbed Container 위젯을 추가하면, 설정 화면에서 "Add Tab"을 클릭해 이 컨테이너 안에 위젯 탭을 여러 개 추가할 수 있습니다. "Add Tab"을 클릭하면 위젯 선택기가 열립니다.
* 각 탭의 이름은 그 탭에 있는 위젯의 제목이며, 설정의 "Format" 아래에 있습니다.
* 설정의 "Settings" 아래에서 각 탭 옆의 위/아래 화살표 버튼으로 탭 순서를 정합니다. 여기서 탭을 삭제하거나 각 탭 안의 위젯을 교체할 수도 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-tabs.png" alt="탭" height="400"/>

**자주 겪는 문제와 참고 사항:**

* 온톨로지에서 중심이 되는 객체에서는 이 탭이 필요한 경우가 있습니다. 다만 "탭 안의 탭" 구조는 사용자 경험을 복잡하게 만든다는 점에 유의하세요.
* Tabbed Container 위젯에는 반드시 제목을 붙이세요. 제목이 있어야 위젯을 추가할 수 있습니다. 제목은 위젯 헤더에 표시됩니다.

<a id="conditional-container"></a>
## 조건부 컨테이너 (Conditional Container)

조건부 컨테이너는 조건에 따라 콘텐츠를 표시하거나 숨길 수 있게 합니다. 이 조건은 다음을 기준으로 할 수 있습니다.

* 사용자가 Object View에 적용한 필터
* 객체 또는 링크된 객체의 속성(property) 값
* 특정 타입의 링크된 객체가 존재하는지 여부

<a id="configuration"></a>
### 설정 (Configuration)

이 위젯에는 *조건부 섹션(conditional section)을* 하나 이상 추가할 수 있습니다. 각 섹션은 *조건*과, 그 조건에 따라 *조건부로 표시되는* 위젯 하나 이상으로 이루어집니다. 조건부 섹션은 다음 세 단계로 설정합니다.

**1단계: 조건 설정하기**

첫 단계는 컨테이너의 내용을 표시할지 숨길지 결정하는 조건을 정의하는 것입니다. 조건에는 세 가지 유형이 있습니다.

***조건 1: Filters(필터)***

*Filters* 조건은 Object View에 필터가 적용되어 있는지 여부에 따라 컨테이너의 내용을 표시하거나 숨깁니다. 이 조건은 세 가지 방식으로 설정할 수 있습니다.

* **Specific Filter(특정 필터)**: 특정 속성에 필터가 적용되어 있을 때만 컨테이너 내용을 표시합니다. 이 속성은 현재 보고 있는 객체의 속성일 수도 있고 링크된 객체의 속성일 수도 있습니다. 따라서 이 조건을 쓰려면 이 조건에 정의한 것과 똑같은 객체와 속성으로 필터링하는 다른 필터 위젯이 있어야 합니다.
  * *예*: Airport의 Object View를 설정하면서 취소된 항공편만 남기는 필터(Status = "Cancelled")를 두었습니다. 취소된 항공편의 세부 정보를 보여 주는 Conditional Container를, 바로 이 특정 필터가 적용되었을 때만 표시되도록 설정합니다.
  * *참고*: 이 조건 유형이 작동하려면 "Filter linked object"와 "Filter property" 드롭다운에서 같은 객체 타입을 선택해야 합니다.
* **No Filter(필터 없음)**: 현재 탭이나 이 탭과 교차 필터를 공유하는 어떤 탭에도 필터가 적용되어 있지 않을 때만 컨테이너를 표시합니다. 날짜 필터, 드롭다운 필터, 버튼 필터 등 어떤 유형의 필터든 해당됩니다.
* **Any Filter(아무 필터)**: 현재 탭이나 이 탭과 교차 필터를 공유하는 탭에 필터가 하나 이상 적용되어 있을 때만 컨테이너를 표시합니다. *No Filter와* 마찬가지로 날짜 필터, 드롭다운 필터, 버튼 필터 등 어떤 유형의 필터든 해당됩니다.

***조건 2: Properties(속성)***

*Properties* 조건은 객체의 속성 값에 따라 컨테이너의 내용을 표시하거나 숨깁니다. 대상 객체는 현재 보고 있는 객체일 수도 있고 링크된 객체일 수도 있습니다. 링크된 객체라면 현재 객체와의 관계가 *1대1(1-to-1)* 또는 *다대1(many-to-1)이어야* 하며, 다대1인 경우 현재 객체가 관계의 "다(many)" 쪽에 있어야 합니다.

이 조건 유형을 사용하려면 먼저 사용할 속성을 선택합니다. 이어서 그 속성을 기준으로 조건부 컨테이너의 내용을 언제 보여 줄지 정합니다. 다음 네 가지 옵션이 있습니다.

* **Is defined(정의됨)**: 속성 값이 `null`이 아닙니다.
* **Is not defined(정의되지 않음)**: 속성 값이 `null`입니다.
* **Is one of(다음 중 하나)**: 속성 값이 사용자가 정의한 값 중 하나와 일치합니다.
* **Is not one of(다음 중 어느 것도 아님)**: 속성 값이 사용자가 정의한 값 중 어느 것과도 일치*하지 않습니다*.

**is one of와** **is not one of에서는** 정의한 값이 속성 타입(integer, double, date, boolean인 경우)에 맞게 변환됩니다. 이 속성 비교가 어떻게 이루어지는지는 아래에서 자세히 설명합니다.

**설명**: 현재 객체가 "다" 쪽에 있어야 하는 이유는 비교할 값이 하나로 정해져야 하기 때문입니다. Flight와 Airline의 관계에서 항공편 하나는 항공사 하나에 속하므로(Flight가 "다" 쪽), Flight 객체 F100의 화면에서 "소속 항공사의 `country` 속성"은 값이 하나로 정해집니다. 반대로 Airline 객체의 화면에서 "소속 항공편의 `status` 속성"은 항공편이 수백 개라 값도 수백 개이므로 `Is one of` 같은 단일 값 비교를 할 수 없습니다. 데이터베이스로 말하면 외래 키(foreign key)를 가진 쪽 테이블의 행에서 참조 대상 행을 하나 따라가는 경우만 허용되는 것입니다.

***조건 3: Linked Objects(링크된 객체)***

*Linked Objects* 조건은 특정 타입의 링크된 객체가 존재하는지 여부에 따라 컨테이너의 내용을 표시하거나 숨깁니다. 이 조건을 설정하려면 먼저 링크 경로를 선택합니다. 그다음 선택한 경로의 링크된 객체가 *존재할 때* 내용을 보여 줄지, *존재하지 않을 때* 보여 줄지 정합니다.

이 조건의 논리는 Linked Objects View와 비교해 생각하면 이해하기 쉽습니다. 이 조건을 가진 컨테이너의 내용은, 같은 링크 경로를 쓰는 Linked Objects View가 객체를 하나 이상 보여 줄 때(링크된 객체가 *존재해야* 하는 경우) 또는 하나도 보여 주지 않을 때(링크된 객체가 *존재하지 않아야* 하는 경우)에만 표시되어야 합니다.

**설명**: 이 조건은 SQL의 `EXISTS`와 `NOT EXISTS`에 해당합니다. 예를 들어 Aircraft 객체 화면에서 링크 경로를 "Maintenance Records"로 정하고 "존재할 때 표시"를 고르면, `EXISTS (SELECT 1 FROM maintenance WHERE aircraft_id = 'A1')`이 참일 때만 정비 이력 섹션이 나타납니다.

**2단계: 위젯 추가하기**

조건을 정의했으면 두 번째 단계로 컨테이너 안에 실제로 표시할 콘텐츠를 설정합니다. "Add Section" 버튼을 클릭하고 필요한 만큼 위젯을 추가합니다. 위/아래 화살표 버튼으로 Conditional Container 안에 표시되는 위젯의 순서를 정할 수 있습니다.

**3단계: 레이아웃 고르기**

마지막 세 번째 단계는 컨테이너의 레이아웃을 고르는 것입니다. 레이아웃은 다음 중 하나입니다.

* **Horizontal(가로)**: Horizontal Distribution Container 위젯처럼 위젯을 왼쪽에서 오른쪽으로 표시합니다.
* **Vertical(세로)**: Vertical Stack Container 위젯처럼 위젯을 위에서 아래로 표시합니다.

이 세 단계를 마치면 Conditional Container 설정이 끝나 바로 사용할 수 있습니다.

**자주 겪는 문제와 참고 사항:**

* 속성 값 비교는 어떻게 이루어지나요?
  * 문자열 값은 일반적인 방식으로 일치 여부를 비교합니다.
  * 숫자 속성의 경우 위젯에 입력한 모든 값을 숫자로 변환해 숫자 속성과 비교합니다(예: 문자열 3.1415를 입력하면 double로 변환됩니다).
  * boolean 속성의 경우 위젯에 "true", "yes", "1"을 입력하면 모두 참으로 간주하며, 나머지는 모두 거짓입니다.
  * 날짜와 타임스탬프 값은 문자열로 변환한 뒤 비교합니다.
  * 배열(array)은 현재 지원하지 않습니다.
* 조건을 여러 개 추가하면 위에서 아래로 차례로 평가합니다. 처음으로 충족되는 조건의 섹션만 렌더링하고 나머지는 무시합니다.
* 속성 값 기준 조건부 컨테이너 옵션은 1대1 또는 다대1 관계에서, 현재 표시 중인 객체가 관계된 쪽("다" 쪽)에 있을 때 작동합니다.
  * 다대다(many-to-many) 관계나, 현재 객체가 주(primary) 쪽에 있는 1대다(1-to-many) 관계의 조건은 허용*하지 않으며*, 링크된 객체 값의 집계(aggregation)에 따른 조건부 표시도 허용*하지 않습니다*.
  * *예*: aircraft 객체를 볼 때, 그 항공기가 어느 항공사에 속하는지에 따른 조건은 추가할 수 있습니다(항공기가 항공사 하나에만 속한다고 가정). 하지만 "속성 X를 가진 링크된 flight 객체가 있는가?"에 따른 조건은 추가할 수 없습니다.
* 이 위젯은 탭 수준의 선택 설정인 "Visibility(표시 여부)"를 위젯 수준으로 확장한 것입니다. 다만 완전히 같지는 않습니다.
  * "Visibility"는 사용자 프로필에 따라 조건부 탭을 정의할 수 있게 합니다.
  * 이 위젯은 (1) 한 탭 안에서 조건부 뷰를 설정할 수 있고, (2) 적용된 필터(사용자의 조작에 따라 달라짐)에 따른 조건부 표시 옵션이 있으며, (3) 사용자 프로필별 조건부 뷰는 포함하지 않습니다.
* 적용된 필터에 따라 조건부 섹션을 표시하거나 숨기는 옵션을 쓰려면 오른쪽 설정 편집기의 "Settings" 아래에 있는 "cross-filtering" 체크박스를 반드시 체크하세요.
* Conditional Container는 다른 위젯을 가로 또는 세로로 배치해 담는 컨테이너일 뿐입니다.

**설명**: "위에서 아래로 평가하고 처음 충족되는 조건만 렌더링"하는 동작은 프로그래밍 언어의 `if ... else if ... else if` 체인과 같습니다. 예를 들어 첫 번째 섹션 조건이 "Status Is one of Cancelled", 두 번째 섹션 조건이 "Status Is defined"라면, 상태가 Cancelled인 항공편에서는 두 조건이 모두 참이지만 첫 번째 섹션만 표시됩니다. 따라서 더 구체적인 조건을 위에 두어야 합니다.

> **중간 요약**: Tabbed Container는 탭 안에 탭을 하나 더 두는 컨테이너이고, Conditional Container는 필터 적용 여부, 속성 값, 링크된 객체 존재 여부를 조건으로 내용을 보이거나 숨기는 컨테이너입니다. 속성 조건은 현재 객체가 "다" 쪽인 1대1 또는 다대1 관계에서만 쓸 수 있고, 여러 조건은 위에서부터 처음 충족되는 것 하나만 적용됩니다.

<a id="markdown"></a>
## 마크다운 (Markdown)

이 위젯은 Object View 레이아웃의 일부로 서식 있는 텍스트를 추가할 수 있게 합니다. 경량 서식 문법인 Markdown(`markdown-it` 라이브러리)을 기반으로 하는 일반 텍스트 편집기를 제공합니다. 여기에 더해, 이 위젯에서는 객체 속성 값을 텍스트 안에 템플릿으로 끼워 넣을 수 있습니다.

![markdown hubble plugin 1](https://www.palantir.com/docs/resources/foundry/object-views/widgets_markdown-hubble-plugin-1.png)
![markdown hubble plugin 2](https://www.palantir.com/docs/resources/foundry/object-views/widgets_markdown-hubble-plugin-2.png)

<a id="configuration"></a>
### 설정 (Configuration)

* 텍스트 상자는 단순한 텍스트 편집기이며, 표준 `markdown-it` 라이브러리를 지원합니다.
* **객체 속성 템플릿(Object properties templating)**: 이중 중괄호를 쓴 {{propertyName}} 형식으로 Markdown 내용에 현재 객체의 속성 값을 템플릿으로 넣습니다. propertyName은 [온톨로지의 속성](../../../02_define-ontologies/02_object-and-link-types/03_properties/01_properties-overview.md) 이름을 대소문자까지 정확히 쓴 것입니다. {{objectId}}, {{objectTypeId}}, {{objectTypeRid}} 값도 지원합니다.

*추가 설정*:

* 줄바꿈(Line breaks), 두 가지 옵션이 있습니다.
  * Enable line breaks(줄바꿈 사용): 켜면(기본값) 편집기의 줄바꿈 하나가 실제 줄바꿈으로 작동합니다. 끄면 편집기의 줄바꿈이 결과에 영향을 주지 않습니다. 이 경우에도 제목(header) 서식은 그대로 작동합니다.
  * Convert "\n" to line breaks("\n"을 줄바꿈으로 변환): `\n`을 줄바꿈으로 표시합니다("Enable line breaks"가 켜져 있어야 합니다).
* Enable sanitized HTML rendering(정제된 HTML 렌더링 사용): markdown-it으로 안전하게 HTML을 렌더링합니다. 객체 속성에서 온 HTML을 임베드하는 기능은 비활성화되어 있으며, 보안을 위해 모든 속성 값은 이스케이프(escape) 처리됩니다.

**설명**: 템플릿 치환은 다음과 같이 동작합니다. Airport 객체의 속성이 `name = "John F. Kennedy International"`, `city = "New York"`이고 Markdown 위젯에 `**{{name}}** 공항은 {{city}}에 있습니다.`라고 쓰면, 화면에는 굵은 글씨의 "John F. Kennedy International" 뒤에 "공항은 New York에 있습니다."가 이어져 표시됩니다. 이스케이프 처리란 속성 값에 `<script>` 같은 HTML 태그가 들어 있어도 태그로 해석하지 않고 `&lt;script&gt;`처럼 문자 그대로 보여 주는 것으로, 데이터에 섞인 악성 스크립트가 실행되는 공격(XSS)을 막기 위한 일반적인 방법입니다.

**자주 겪는 문제와 참고 사항:**

* 현재 {{propertyName}} 형식으로 넣은 긴 텍스트와 배열은 텍스트 상자 밖으로 넘칠 수 있으며 기본적으로 렌더링되지 않습니다.

> **중간 요약**: Markdown 위젯은 markdown-it 기반의 서식 텍스트를 Object View에 넣고, {{propertyName}} 형식으로 현재 객체의 속성 값을 끼워 넣을 수 있게 합니다. 줄바꿈 처리 방식을 고를 수 있고, HTML 렌더링 시 속성 값은 보안을 위해 이스케이프됩니다.

## 정리

* 레거시 Object View의 레이아웃은 탭, 탭 안의 레이아웃 위젯(컨테이너), 콘텐츠 위젯의 세 단계로 구성됩니다.
* Horizontal Distribution과 Vertical Stack Container는 위젯을 가로 또는 세로로 배치만 하는 컨테이너이며, 제목이 있어야 추가할 수 있습니다.
* Tabbed Container는 탭 안에 탭을 하나 더 두지만 사용자 경험이 복잡해질 수 있습니다.
* Conditional Container는 필터, 속성 값, 링크된 객체 존재 여부에 따라 내용을 보이거나 숨기며, 조건은 위에서부터 처음 충족되는 것만 적용됩니다.
* Markdown 위젯은 객체 속성 값을 템플릿으로 끼워 넣은 서식 텍스트를 보여 줍니다.
