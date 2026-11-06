# 속성과 링크 위젯 (Properties and Links)

- 원문: https://www.palantir.com/docs/foundry/object-views/widgets-properties-links/
- 사이드바 위치: Applications > Object Views > Legacy Object Views > Properties and Links

이 페이지는 레거시(legacy) Object View에서 객체의 속성(property)과 링크를 표 형태로 보여 주는 위젯들(Properties, Property Cards, Links, Edit History)의 구성 방법을 설명합니다. 온톨로지에서 속성에 지정한 메타데이터(prominent, hidden, long text 등)와 링크의 관계 방향(일대다, 다대일)이 위젯에서 무엇을 보여 줄 수 있는지를 직접 결정하므로, 온톨로지 정의와 화면 구성의 연결 관계를 이해하는 데 도움이 됩니다.

이 페이지는 객체의 데이터 모델과 온톨로지를 단순한 표 형태로 보여 주는 모든 위젯을 다룹니다. 이 위젯들은 현재 객체의 속성과, 그 객체가 다른 객체와 맺고 있는 링크를 강조해 보여 줍니다.

이 범주에는 통계, 지표, KPI를 보여 주는 위젯도 포함됩니다. 이런 값은 객체의 파이프라인에서 미리 계산되어 객체의 속성으로 제공되거나, 현재 객체에 링크된 객체(Linked Objects)에 대한 집계(aggregation)가 필요한 값입니다.

**설명**: "링크된 객체에 대한 집계"는 SQL의 `GROUP BY`와 집계 함수에 해당합니다. 예를 들어 `Aircraft` 객체 A1의 화면에 "총 운항 횟수"를 표시하려면 A1에 링크된 Flight 객체의 개수를 세야 합니다. 이는 `SELECT COUNT(*) FROM flights WHERE aircraft_id = 'A1'`과 같은 계산입니다. 반대로 파이프라인에서 이 값을 미리 계산해 `total_flights` 속성으로 넣어 두었다면 위젯은 그 속성 값을 그대로 읽어 보여 주기만 하면 됩니다.

<a id="properties-widget"></a>
## Properties 위젯 (Properties widget)

**Properties** 위젯은 객체 또는 링크된 객체의 속성을 보여 줍니다. 새로 정의한 객체 타입에는 이 위젯이 들어 있는 탭이 기본 Object View로 만들어집니다.

![Properties 위젯](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-properties.png)

<a id="properties-widget-configuration"></a>
### Properties 위젯 구성 (Properties widget configuration)

<a id="properties-definition-in-the-ontology-manager"></a>
#### Ontology Manager에서의 속성 정의 (Properties definition in the Ontology Manager)

Properties 위젯의 구성은 Ontology Manager의 속성 정의와 밀접하게 연결되어 있습니다. "Edit Properties and Backing Dataset"에서 작업할 때 각 속성에는 별도의 설정 패널이 있으며, 여기서 속성이 Object View에 어떻게 표시될지 정의할 수 있습니다.

Properties 위젯의 표시에 영향을 주는 설정은 다음과 같습니다.

* 속성 가시성(Property visibility)
  * Prominent: 속성이 Properties 위젯에 표시되며, 위젯에는 중요 속성만 표시하는 구성 옵션이 있습니다. 객체의 가장 중요한 핵심 속성에 이 옵션을 사용합니다.
  * Normal: 속성이 Properties 위젯에 표시됩니다. 대부분의 속성에 이 옵션을 사용합니다.
  * Hidden: 속성이 Properties 위젯에 표시되지 않습니다(Object View나 Object Explorer의 어디에도 표시되지 않습니다). 내부 ID나 다른 객체와의 링크를 위한 관계 열(relation-column) 같은 속성에 이 옵션을 사용합니다.
* 렌더 힌트(Render Hints)
  * Long text: 속성을 긴 텍스트로 표시하는 옵션입니다(보통 설명, 코멘트 같은 긴 문자열에 사용). 이 옵션을 켜면 Properties 위젯의 별도 섹션에 텍스트를 표시할 수 있습니다.
  * Keywords: 속성을 키워드로 렌더링합니다. Properties 위젯에서 보이는 방식이 바뀌고, 위젯 안의 별도 섹션에 표시할 수도 있습니다.
* 타입 클래스(Type classes): 속성에 타입 클래스를 정의할 수 있으며, 이는 속성의 기능에 영향을 줍니다.
* 속성을 편집 가능하게 만들기: 속성을 편집 가능하게 하려면 [액션 타입](../../../02_define-ontologies/03_action-types/01_overview.md) 또는 [인라인 액션](../../../02_define-ontologies/03_action-types/18_inline-edits.md)을 설정합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-properties-oma.png" alt="Ontology Manager의 속성" height="500"/>

**설명**: Hidden의 예시로 나온 "관계 열"은 외래 키 열을 말합니다. 예를 들어 Flight 객체 타입의 `aircraft_id` 열은 Aircraft와의 링크를 만드는 데 쓰이지만, 사용자는 링크를 통해 Aircraft 객체를 바로 볼 수 있으므로 `aircraft_id` 문자열 자체를 화면에 보여 줄 필요는 적습니다. 그래서 이런 열을 숨김으로 지정하는 경우가 많습니다.

<a id="configuration-of-the-properties-widget-itself"></a>
#### Properties 위젯 자체의 구성 (Configuration of the Properties widget itself)

위젯 구성에서 먼저 현재 객체(Current Object)의 속성을 표시할지, 링크된 객체(Linked Object)의 속성을 표시할지 선택합니다.

* 링크된 객체를 표시하는 경우, 먼저 표시할 링크를 선택합니다.
* 링크된 객체의 속성 표시는 현재 객체가 오직 하나의 객체와 링크되어 있을 때만 가능합니다. 이는 (1) 일대일 관계이거나, (2) 현재 객체가 "다(many)" 쪽으로 정의된 다대일 관계일 때입니다.
  * 예: Flight 객체를 구성할 때는 이 항공편에 링크된 Aircraft의 속성을 표시할 수 있습니다(Flight와 Aircraft는 다대일 관계입니다). 하지만 Aircraft 객체에서는 링크된 Flight의 속성을 표시할 수 없습니다. Aircraft 하나에 여러 Flight 객체가 링크되어 있기 때문입니다.

**설명**: 위젯은 "속성 이름: 값" 목록 하나를 보여 주므로, 링크를 따라갔을 때 결과가 정확히 한 행이어야 표시할 수 있습니다. Flight F100의 `aircraft_id`는 A1 하나만 가리키므로 A1의 속성을 보여 줄 수 있습니다. 반면 A1에서 Flight 쪽으로 가면 F100, F102 두 행이 나오므로 어느 행의 값을 보여 줄지 정할 수 없습니다. 그런 경우에는 아래 Property Cards 위젯의 집계를 쓰거나 Links 위젯으로 목록을 보여 줘야 합니다.

현재 객체 또는 링크된 객체를 선택한 뒤에는 Data, Sections, View Options의 세 가지 구성 요소를 설정합니다.

<a id="data"></a>
##### 데이터 (Data)

* 표시할 속성을 선택합니다.
  * All Properties: Prominent 또는 Normal로 정의된 모든 속성을 표시하며, Hidden 속성은 표시하지 않습니다. `Properties to Exclude` 선택기(아래 참조)로 특정 속성들을 제외할 수 있습니다.
  * Prominent Properties: Ontology Manager에서 Prominent로 정의된 속성만 표시합니다. `properties to exclude` 선택기(아래 참조)로 특정 속성들을 제외할 수 있습니다.
  * Specific Properties: 해당 링크된 객체의 모든 속성이 들어 있는 다중 선택 드롭다운을 열어 그중에서 선택합니다.
  * No Properties: 아무 속성도 표시하지 않습니다.
* Properties to Exclude: 표시에서 제외할 속성을 선택합니다. 앞의 두 옵션(All Properties, Prominent Properties)에서만 사용할 수 있습니다.

<a id="sections"></a>
##### 섹션 (Sections)

기본적으로 속성 섹션은 세 개입니다.

* Normal properties: Normal과 Prominent 속성 전부입니다.
* Long text properties: Ontology Manager에서 긴 텍스트로 정의된 속성만 표시합니다(위의 세부 내용 참조).
* Keyword properties: 객체의 키워드 속성을 태그로 표시합니다. Ontology Manager의 "Edit Properties and Backing Dataset"에서 키워드로 표시한 속성만 여기에 표시됩니다.

이 섹션들은 제거하거나 순서를 바꿀 수 있습니다. 이 세 가지 외에 다른 종류의 섹션은 없습니다.

<a id="view-options"></a>
##### 보기 옵션 (View options)

* **User Editable:** 사용자가 속성을 편집할 수 있게 할지 정합니다. 이를 위해서는 Ontology Manager에서 미리 두 가지를 설정해야 합니다(자세한 내용은 위 참조).
  * 데이터셋 수준: 객체 타입에서 편집(edit)이 활성화되어 있어야 합니다.
  * 속성 수준: 속성에 [인라인 편집 액션](../../../02_define-ontologies/03_action-types/18_inline-edits.md#object-explorer-inline-edits)이 연결되어 있어야 합니다.
* **Hide Undefined Values:** 값이 정의되지 않은(null) 모든 속성을 숨깁니다. 이 토글이 꺼져 있으면 속성이 회색의 "no value" 텍스트와 함께 표시됩니다.
* **Include link to 'More properties':** 이 옵션을 켜면 **View all** 버튼이 렌더링되며, 이 버튼을 누르면 같은 Object View 안의 **Properties** 탭으로 이동합니다.

<a id="common-issues-and-notes"></a>
#### 자주 발생하는 문제와 참고 사항 (Common issues and notes)

* 속성은 알파벳 순서로 표시됩니다. 다른 순서로 배치하는 주된 방법은 위젯 구성의 "Sections"를 활용하는 것입니다.
* 속성을 Prominent로 설정하거나, Long Text 또는 Keyword로 설정하거나, 사용자 편집 가능하게 만드는 방법은 [속성 편집 문서](../../../02_define-ontologies/02_object-and-link-types/03_properties/02_edit-properties.md)를 참조하세요.

> **중간 요약**: Properties 위젯은 Ontology Manager의 속성 설정(가시성, 렌더 힌트, 편집 가능 여부)을 그대로 반영해 속성을 보여 줍니다. 링크된 객체의 속성은 결과가 객체 하나로 정해지는 일대일 또는 다대일 관계에서만 표시할 수 있습니다.

<a id="property-cards"></a>
## Property Cards 위젯 (Property Cards)

**Property Cards** 위젯은 속성과 링크된 객체에 대한 집계를 카드 형태로 시각화합니다.

Property Cards 위젯을 사용해 현재 객체 또는 그에 링크된 객체에 대한 중요한 속성(숫자, 타임스탬프, 날짜, 문자열 등), 집계, 통계, 지표, KPI, 그 밖의 핵심 정보를 표시합니다.

![Property cards](https://www.palantir.com/docs/resources/foundry/object-views/widgets_property-cards.png)

* 이 위젯은 필터의 영향을 받으며, 필터는 링크된 객체에 대한 모든 집계에 적용됩니다.
* Property Cards 위젯은 [조건부 서식(conditional formatting)](../../../02_define-ontologies/02_object-and-link-types/03_properties/04_conditional-formatting.md)과 [값 서식(value formatting)](../../../02_define-ontologies/02_object-and-link-types/03_properties/03_value-formatting.md)을 위한 풍부한 UI를 지원합니다. 전역 옵션(온톨로지 편집기에서 온톨로지 수준으로 구성한 설정 기반)과 로컬 재정의(override) 옵션을 모두 지원합니다.

<a id="property-card-configuration"></a>
### Property Card 구성 (Property Card configuration)

먼저 속성 또는 링크된 객체 집계를 시각화할 때마다 새 카드를 하나씩 추가합니다. 그런 다음 위젯 안에 있는 모든 카드의 전체 레이아웃을 구성합니다.

<a id="configuration-per-card"></a>
#### 카드별 구성 (Configuration per card)

* Property 카드는 **속성 하나** 또는 **링크된 속성의 집계**를 표시할 수 있습니다.
  * 속성을 표시할 때 카드는 현재 객체의 속성뿐 아니라 일대일 또는 다대일 관계로 링크된 객체의 속성도 보여 줄 수 있습니다(예: 현재 객체가 Flight이고 Aircraft와 다대일 관계라면 Aircraft 객체의 속성을 보여 줄 수 있습니다).
  * 링크된 객체를 표시할 때 카드는 현재 객체와 일대다 또는 다대다 관계로 링크된 모든 객체의 집계를 보여 줄 수 있습니다.
* 집계인 경우 집계 유형을 선택합니다: count(개수), unique count / cardinality(고유 개수), average(평균), min(최솟값), max(최댓값), sum(합계).
* 카드에 표시될 라벨과 아이콘, 아이콘 색상을 추가합니다.
* **조건부 서식과 값 서식:** 기본적으로 위젯은 해당 객체와 속성에 대해 온톨로지 수준에서 정의한 전역 온톨로지 서식 규칙을 사용합니다.
  * 이 위젯은 조건부 서식(예: 미리 정의한 규칙에 따라 값을 빨간색이나 초록색으로 표시)을 지원하지만, 속성에만 적용되고 집계에는 적용되지 않습니다. 지원되는 옵션은 전역 서식(Ontology Manager에서 구성한 것, [조건부 서식 문서](../../../02_define-ontologies/02_object-and-link-types/03_properties/04_conditional-formatting.md) 참조)과 선택적인 로컬 재정의입니다.
  * Property Cards 위젯은 속성과 링크된 속성의 집계 모두에 대해 값 서식(예: `3,625,329` 대신 `$3.6M`)을 지원합니다. 지원되는 옵션은 전역 값 서식(Ontology Manager에서 구성한 것, [값 서식 문서](../../../02_define-ontologies/02_object-and-link-types/03_properties/03_value-formatting.md) 참조)과 로컬 재정의입니다.
  * 로컬 재정의의 경우 값 서식과 조건부 서식 모두 온톨로지 수준 서식과 같은 UI를 사용합니다. 자세한 내용은 위에 링크된 온톨로지 문서를 확인하세요.

**설명**: 관계 방향에 따라 카드가 할 수 있는 일이 나뉩니다. 링크를 따라갔을 때 객체가 하나만 나오면(일대일, 다대일) 그 객체의 속성 값을 그대로 보여 주고, 여러 개가 나오면(일대다, 다대다) 하나의 숫자로 줄이는 집계를 보여 줍니다. 예를 들어 Aircraft A1 화면에서 링크된 Flight가 F100, F102이고 각각 `distance`가 2500, 1800이라면 count 카드는 2, sum 카드는 4300, average 카드는 2150을 보여 줍니다.

<a id="configuration-for-all-cards-on-a-property-cards-widget"></a>
#### Property Cards 위젯의 모든 카드에 대한 구성 (Configuration for all cards on a Property Cards widget)

* 모든 속성 카드와 집계 카드를 구성했다면, 레이아웃 구성으로 표시되는 카드의 배경, 크기, 스타일, 정렬, 아이콘 스타일을 정합니다.
* 카드마다 다른 시각적 구성을 쓰고 싶다면, 서로 다른 구성마다 새 위젯 인스턴스를 추가하는 것을 고려하세요.

<img height="500" alt="Property cards 구성" src="https://www.palantir.com/docs/resources/foundry/object-views/widgets_property-cards-config.png">

<a id="common-issues-and-notes"></a>
#### 자주 발생하는 문제와 참고 사항 (Common issues and notes)

* Property Cards는 현재 객체와 링크된 객체의 중요 속성, 집계, 통계, 지표, KPI, 그 밖의 핵심 정보를 시각화하기 위해 지원되는 위젯입니다.
  * 단일 핵심 속성과 집계를 시각화하는 용도로는 다른 어떤 위젯보다 이 위젯이 권장되는 해결책입니다. 다음 위젯 대신 Property Cards 위젯 사용을 고려하세요: Statistics, Context Stat Section, Linked Statistics, Advanced Statistics, Property Plus.
* Property Cards 위젯은 [객체 기반 함수(Functions on Objects)](../../../02_define-ontologies/04_functions/13_functions-on-objects/01_functions-on-objects.md)를 지원하지 않습니다. 이 지원이 필요하면 Workshop이나 Quiver를 사용하고 전용 위젯으로 Object View에 임베드하는 것을 고려하세요.

> **중간 요약**: Property Cards는 속성 값이나 링크된 객체 집계(count, sum 등)를 카드로 보여 주는 권장 위젯이며, 전역 또는 로컬 서식을 적용할 수 있습니다. 함수(function)로 계산한 값은 지원하지 않으므로 그런 경우 Workshop이나 Quiver를 임베드합니다.

<a id="links"></a>
## Links 위젯 (Links)

**Links** 위젯은 객체의 링크를 트리 형태로 보여 주며, 링크를 따라 이동하고 링크된 객체로 이동할 수 있습니다. 구체적으로 다음을 포함합니다.

* 모든 링크된 객체의 트리를 표시합니다. 각 링크된 객체의 보기를 펼쳐 그 객체에 링크된 모든 객체를 표시하고, 계속해서 링크를 따라 넘어갈 수 있습니다("중첩 링크(nested links)").
* 어떤 객체 위에 마우스를 올리면 그 객체의 모든 중요 속성이 담긴 툴팁을 볼 수 있습니다.
* 어떤 객체를 클릭하면 그 객체의 Object View로 이동합니다.

아래 예시는 다음 3단계를 포함합니다.

* Airport 객체에서 시작합니다.
* 링크된 모든 Flight로 이동합니다.
* 그 Flight 중 하나에 링크된 모든 객체(Aircraft, 도착 Airport, 관련된 모든 Post-Flight Review)로 이동합니다.

![Links 위젯](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-links.png)

<a id="links-widget-configuration"></a>
### Links 위젯 구성 (Links widget configuration)

* Link types (first links only): 위젯에 어떤 유형의 링크를 표시할지 정합니다. 사용자는 링크를 따라 다른 링크된 객체로 넘어갈 수 있습니다(예: Airport에서 모든 Flight로, 다시 그 Flight를 운항하는 Aircraft로, 다시 그 Aircraft를 소유한 Airline으로 이어서 이동).
* Filter Nested Links by Type: 이 설정을 켜면 "Link types (first links only)"에서 선택한 링크된 객체만 표시합니다.

**설명**: 트리 탐색은 그래프 탐색과 같은 동작입니다. 객체를 노드, 링크를 간선으로 보면, 위젯은 현재 노드에서 출발해 사용자가 펼치는 노드마다 인접 노드를 한 단계씩 보여 줍니다. SQL로 하면 Airport에서 Flight로, Flight에서 Aircraft로 이어지는 조인을 한 단계씩 실행해 결과를 펼쳐 보는 것입니다.

<a id="common-issues-and-notes"></a>
#### 자주 발생하는 문제와 참고 사항 (Common issues and notes)

* 현재 다음 항목의 정렬이나 순서 지정은 불가능합니다.
  * 링크된 객체 값의 목록(예: 링크된 모든 Flight를 알파벳 순으로 표시).
  * 이 위젯 아래 링크된 객체의 *유형*(예: 링크된 Flight를 먼저, 링크된 Aircraft를 다음에 표시).
* 이 위젯은 현재 필터의 영향을 받지 않습니다. 표시되는 링크는 항상 현재 객체에 링크된 *모든* 객체입니다.

> **중간 요약**: Links 위젯은 링크를 트리로 펼쳐 여러 단계로 탐색하게 해 주며, 첫 단계에 보일 링크 타입을 고를 수 있습니다. 정렬 기능이 없고 필터의 영향을 받지 않습니다.

<a id="edit-history"></a>
## Edit History 위젯 (Edit History)

**Edit History** 위젯은 현재 보고 있는 객체에 대해 이루어진 모든 편집(edit)의 이력을 목록으로 보여 줍니다. 객체가 한 번도 편집되지 않았거나, 선택한 열 집합(아래 참조)에 편집이 없으면 이 위젯은 `No Edits` 메시지를 표시합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-edits-history.png" alt="편집 이력" />

<a id="edit-history-configuration"></a>
### Edit History 구성 (Edit History configuration)

|옵션 |설명    |
|---    |---    |
|All Properties |해당 객체 타입의 모든 속성에 대한 편집을 표시합니다.  |
|Specific Properties    |Specific Properties: 위젯 구성의 `Properties to Include` 선택기에서 선택한 속성에 대한 편집만 표시합니다. |

<a id="common-issues-and-notes"></a>
#### 자주 발생하는 문제와 참고 사항 (Common issues and notes)

* 액션으로 객체에 가한 변경만 Edit History에 표시됩니다. 백킹 데이터셋(backing dataset)이나 업스트림 파이프라인에서 일어난 변경은 이 위젯에 반영되지 않습니다.
* Edit History는 Ontology Manager에서 [**Track user edit history**](../../../06_ontology-architecture/04_object-edits-and-materializations/03_user-edit-history.md) 토글을 켠 뒤 Object Storage v2에 인덱싱된 객체에 가해진 변경만 반영합니다.
* 마킹(marking) 속성이 있는 객체 타입에 대한 사용자 편집 추적은 현재 지원되지 않습니다.
* 제출된 각 값은 편집으로 기록되며, 액션 파라미터에 구성된 기본값에서 온 값이라도 마찬가지입니다.

**설명**: 온톨로지의 객체 값은 두 경로로 바뀔 수 있습니다. 하나는 원본 데이터셋 자체가 파이프라인 실행으로 갱신되는 경로이고, 다른 하나는 사용자가 액션을 실행해 객체 값을 직접 수정하는 경로입니다. Edit History는 두 번째 경로, 즉 "누가 언제 어떤 액션으로 어떤 값을 바꿨는가"만 기록합니다. 데이터베이스의 감사 로그(audit log) 테이블이 애플리케이션을 통한 변경만 기록하고 일괄 적재(bulk load)는 기록하지 않는 구성과 같은 구분입니다.

> **중간 요약**: Edit History는 액션을 통한 편집 이력만 보여 주며, Track user edit history를 켠 뒤 OSv2에 인덱싱된 객체에 대해서만 기록됩니다.

## 정리

- Properties 위젯은 Ontology Manager의 속성 가시성과 렌더 힌트에 따라 속성을 섹션별로 보여 주며, 링크된 객체의 속성은 일대일 또는 다대일 관계에서만 표시할 수 있습니다.
- Property Cards는 속성 값과 링크된 객체 집계를 카드로 보여 주는 권장 위젯으로, 여러 구형 통계 위젯을 대체합니다.
- Links 위젯은 링크를 트리로 펼쳐 여러 단계로 탐색하게 해 주지만 정렬과 필터는 지원하지 않습니다.
- Edit History 위젯은 액션으로 이루어진 편집만 기록하며, 사용자 편집 이력 추적 설정이 필요합니다.
