# 조건부 서식 추가 (Add conditional formatting)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/conditional-formatting/
- 사이드바 위치: Define Ontologies > Object and link types > Properties > Add conditional formatting

이 페이지는 속성 값이 어떤 조건을 만족할 때 색이나 정렬 같은 표시 방식을 바꾸는 조건부 서식(conditional formatting)을 설명합니다. 규칙을 추가하는 절차, 규칙 편집기(Rule editor)의 각 구성 요소, 규칙을 다른 속성으로 복사하는 방법을 다룹니다. 값 서식이 값 자체를 읽기 좋게 바꾼다면, 조건부 서식은 값에 따라 시각적 강조를 다르게 준다는 점이 다릅니다.

**조건부 서식(conditional formatting)을** 사용하면 어떤 속성에든 규칙을 설정해, 사용자용 애플리케이션에서 그 속성 값이 어떻게 표시될지(예: 색상, 정렬 등)를 정할 수 있습니다. Ontology Manager에서 조건부 서식을 설정하면 그 서식 규칙이 Object Explorer, Object View, Quiver, Workshop에 적용됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/conditional-formatting-cond-form-example.png" alt="예시" width="600"/>

위 그림의 Object Explorer에 있는 예시 `Aircraft` 객체 타입에서는 `type` 속성과 `wifi` 속성의 값이 특정 조건에 따라 색이 입혀진 상자 안에 표시됩니다. 이런 서식을 추가하는 주된 이점은 정보를 빠르게 이해할 수 있게 해 준다는 것입니다. 분석가가 "JFK"에 있는 wifi 없는 "A320" 항공기를 모두 찾고 있다면, 위 결과를 훑어보기만 해도 필요한 항공기가 "Q-AAY"라는 것을 알 수 있습니다.

이 조건들이 어떻게 적용되는지 살펴보겠습니다.

* `wifi` 속성의 경우, 표의 각 객체에 대해 속성 값이 "true"이면 초록색, "false"이면 빨간색을 지정합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/conditional-formatting-wifi-rules.png" alt="규칙 예시" width="250"/>

* `type` 속성의 경우, "A320", "A321", "A330" 중 어느 것과 정확히 일치하는지에 따라 색을 지정합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/conditional-formatting-type-rules.png" alt="type 색상 예시" width="250"/>

**설명**: 조건부 서식 규칙은 "조건이 참이면 이 서식을 적용한다"는 if 문의 목록입니다. `wifi` 예시는 다음 코드와 같은 의미입니다: `if (wifi == true) color = green; else if (wifi == false) color = red;`. 데이터 값은 바뀌지 않고, 화면에 그릴 때만 색이 결정됩니다.

> **중간 요약**: 조건부 서식은 속성 값에 따라 색상, 정렬 같은 표시 방식을 정하는 규칙이며, Object Explorer, Object View, Quiver, Workshop에 공통으로 적용됩니다.

<a id="add-conditional-formatting"></a>
## 조건부 서식 추가하기 (Add conditional formatting)

속성 편집기에서 다음을 수행합니다.

1. 조건부 서식을 추가하려는 속성을 선택합니다.
2. 속성 창(properties pane)에 조건부 서식 항목이 보입니다. **Add a rule**(규칙 추가) 버튼을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/conditional-formatting-cond-form-oma.png" alt="규칙 추가" width="600"/>

1. 새로 만들어진 기본 규칙을 클릭해 **Edit conditional formatting rule**(조건부 서식 규칙 편집) 편집기를 엽니다. [규칙 편집기의 구성 요소에 대한 자세한 내용은 아래를 참고하세요](#edit-rules-using-the-rule-editor).
2. 규칙을 수정합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/conditional-formatting-rule.png" alt="규칙 수정" width="600"/>

> **중간 요약**: 속성 편집기에서 속성을 선택하고 Add a rule로 기본 규칙을 만든 뒤, 그 규칙을 클릭해 편집기에서 수정합니다.

<a id="edit-rules-using-the-rule-editor"></a>
## 규칙 편집기로 규칙 편집하기 (Edit rules using the Rule editor)

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/conditional-formatting-rule-editor-string.png" alt="규칙 편집기" width="700"/>

|라벨 |설명 |사용법 |
|--- |--- |--- |
|A |**Standard**(표준) 규칙, **Always true**(항상 참) 규칙, **Math**(수학) 규칙 사이를 전환합니다. |다른 규칙이 일치하지 않을 때를 대비한 대체(fallback) 규칙으로 **Always true**를 사용합니다. 위 예시에서는 `type` 값이 어느 것과도 일치하지 않을 때 회색을 대체 규칙으로 둘 수 있습니다.<br><br>일부 속성에 수학 연산자를 적용하고 싶을 때는 **Math** 규칙을 사용합니다. |
|B |규칙은 항상 **Add a rule**을 선택한 그 속성에 적용됩니다. 다만 이 드롭다운에서 다른 속성의 값을 기준으로 규칙을 적용하도록 고를 수 있습니다. |위 예시에서 `Performance factor` 값이 특정 임곗값 아래로 떨어지면 `Type` 값을 빨간색으로 칠하고 싶다고 가정합니다. 이때 로직에서 `Type` 대신 `Performance factor`를 선택합니다. 그래도 색은 여전히 `Type`에 표시됩니다. |
|C |사용할 수 있는 비교 유형은 속성의 타입에 따라 정해집니다. 예를 들어 문자열에는 **String comparison**(문자열 비교)과 **Is null**(null 여부)이 있습니다. 숫자 타입에는 **Numeric range**(숫자 범위)나 **Exact numeric match**(정확한 숫자 일치)가 있습니다. |값이 null일 때 `type`을 회색으로 칠하려면 이 드롭다운에서 **String comparison** 대신 **Is null**을 선택합니다. |
|D |비교의 하위 유형입니다. **String comparison**에는 **Is exactly**(정확히 일치), **Contains**(포함), **Starts with**(로 시작) 등이 있습니다. |"A32"로 **Starts with** 하는 모든 항공기 `type` 값에 색을 칠할 때 사용합니다. |
|E |상수(constant) 또는 속성 참조(property reference)와 비교합니다. |이 예시에서는 상수 "A320"을 찾고 있지만, 같은 객체 타입의 다른 속성을 참조하도록 추가할 수도 있습니다. |
|F |**True** 규칙과 **False** 규칙 사이를 전환합니다. |A320이 **아닌** 모든 항공기를 파란색으로 칠하려면 이 값을 **False**로 바꿉니다. |
|Formatting |Blueprint 색상과 인텐트(intent)를 사용하거나 직접 지정한 색상을 추가합니다. 정렬도 바꿀 수 있습니다. |필요에 따라 hex, RGB, Blueprint 색상 사이를 전환합니다. 숫자는 상자를 오른쪽에 정렬하면 더 읽기 쉽습니다. |
|Preview |조건부 서식이 여러 맥락에서 어떻게 보이는지 확인합니다. |**Objects table**(객체 표)이나 **Property card**(속성 카드)를 미리 봅니다. |

**설명**: 라벨 B는 "조건을 검사하는 속성"과 "서식이 표시되는 속성"을 분리할 수 있다는 뜻입니다. SQL로 쓰면 `CASE WHEN performance_factor < 0.5 THEN 'red' END`의 결과를 `type` 열의 색으로 쓰는 것과 같습니다. 라벨 F의 False 규칙은 조건을 부정(NOT)합니다. Blueprint는 Palantir가 만든 오픈 소스 UI 컴포넌트 라이브러리이며, 인텐트는 primary, success, warning, danger처럼 의미에 따라 정해진 색상 묶음입니다.

> **중간 요약**: 규칙 편집기에서는 규칙 종류(Standard, Always true, Math), 조건을 검사할 속성, 비교 유형과 하위 유형, 비교 대상(상수 또는 속성), 참/거짓, 색상과 정렬을 정하고 미리 볼 수 있습니다.

<a id="copy-rules"></a>
## 규칙 복사 (Copy rules)

속성 편집기에서 다음을 수행합니다.

1. 조건부 서식 규칙을 복사해 올 속성을 선택합니다.

2. 속성 창에 조건부 서식 항목이 보입니다. **Copy rules**(규칙 복사) 버튼을 선택해 **Copy rule** 대화 상자를 엽니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/conditional-formatting-copy-rule-select-annotated.png" alt="속성 편집기" width="600"/>

3. 조건부 서식 규칙을 복사해 넣을 속성들을 선택합니다.

**주의**: 복사 대상 속성에 이미 자체 조건부 서식 규칙이 있다면, 새 규칙으로 덮어쓰입니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/conditional-formatting-copy-rule.png" alt="규칙 복사" width="600"/>

복사된 규칙은 계속해서 원래 속성을 참조합니다. 예를 들어 `wifi` 값이 "true"일 때 `wifi` 값을 초록색으로 표시하라는 규칙을 `customer experience` 속성에 복사하면, 객체의 `wifi` 값이 "true"일 때 `customer experience` 속성 값도 초록색으로 표시됩니다. 규칙이 참조하는 속성을 바꾸려면 규칙을 선택하고 규칙 편집기의 **Property** 드롭다운에서 새 속성을 고르면 됩니다.

> **중간 요약**: Copy rules로 한 속성의 규칙을 다른 속성들에 복사할 수 있지만, 대상 속성의 기존 규칙은 덮어쓰이고, 복사된 규칙은 여전히 원래 속성의 값을 기준으로 판단합니다.

<a id="faq"></a>
## FAQ

<a id="will-this-work-with-existing-type-classes"></a>
### 기존 타입 클래스와 함께 작동하나요? (Will this work with existing type classes?)

조건부 서식은 기존 타입 클래스보다 우선합니다([다음 질문](#will-this-work-with-editable-properties-in-object-views)에서 설명하는 예외 하나가 있습니다). 둘 다 설정되어 있으면 조건부 서식이 표시됩니다. 다만 한 속성에는 조건부 서식을, 다른 속성에는 타입 클래스를 사용할 수 있습니다.

<a id="will-this-work-with-editable-properties-in-object-views"></a>
### Object View의 편집 가능한 속성에서도 작동하나요? (Will this work with editable properties in Object Views?)

조건부 서식은 [인라인 편집(inline edits)](../../03_action-types/18_inline-edits.md#object-explorer-inline-edits)이 설정된 속성에서 지원됩니다. 레거시 `hubble:editable` 속성 타입 클래스가 있는 속성에서는 조건부 서식이 비활성화됩니다.

## 정리

- 조건부 서식은 속성 값에 따라 색상과 정렬을 바꾸는 규칙이며, Object Explorer, Object View, Quiver, Workshop에 적용됩니다.
- 속성 편집기에서 Add a rule로 규칙을 만들고 규칙 편집기에서 조건과 서식을 정합니다.
- 조건은 다른 속성의 값을 기준으로 삼을 수 있고, Always true 규칙을 대체 규칙으로 둘 수 있습니다.
- 규칙 복사 시 대상의 기존 규칙은 덮어쓰이며, 복사된 규칙은 원래 속성을 계속 참조합니다.
- 조건부 서식은 타입 클래스보다 우선하지만, 레거시 `hubble:editable` 타입 클래스가 있으면 비활성화됩니다.
