# 사용자 정의 속성 추가 (Add a custom property)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/add-a-custom-property/
- 사이드바 위치: Applications > Foundry Rules > Settings & customization > Add a custom property

이 페이지는 규칙 객체와 제안 객체에 기본 구성에 없는 속성(예: 심각도)을 추가하는 절차를 설명합니다. 속성 하나를 추가하려면 온톨로지, 액션 타입, Workshop 애플리케이션을 차례로 고쳐야 하므로, 각 단계가 왜 필요한지 함께 이해하는 것이 중요합니다.

Foundry Rules에서 흔한 사용자 정의 중 하나는 규칙 객체와 제안 객체에 사용자 정의 속성(custom property)을 추가하는 것입니다. 사용자 정의 속성을 사용하면 기본 구성 이외의 추가 메타데이터를 추적할 수 있습니다. 사용자 정의 속성을 추가하려면 다음 단계를 따르세요.

1. Ontology Manager에서 규칙 객체에 속성(예: `severity`)을 추가합니다.

**주의**: 객체 속성은 입력 데이터셋의 열을 백킹으로 가져야 합니다.

비어 있는 자동 생성 입력 데이터셋이라면, **Details** 탭에서 기존 열 정의를 복사하고 수정해 스키마를 직접 편집합니다.

기존 파이프라인에서 오는 규칙이라면 트랜스폼에서 새 열을 추가합니다.

2. 제안 객체에 대응하는 `current_<PROPERTY>`와 `new_<PROPERTY>` 속성(예: `current_severity`와 `new_severity`)을 추가합니다.

3. 제안 객체의 `current_<PROPERTY>` 속성에 타입 클래스(type class) `foundry-rules.property-diff-for:new_<PROPERTY>`(예: `foundry-rules.property-diff-for:new_severity`)를 붙입니다.

   타입 클래스는 *종류(kind)와* *이름(name)으로* 구성되며 `kind.name` 형태로 씁니다. `foundry-rules.property-diff-for:new_<PROPERTY>`의 경우 kind는 `foundry-rules`이고 name은 `property-diff-for:new_<PROPERTY>`입니다.

4. Foundry Rules 설정에서 규칙 객체나 제안 객체를 수정하거나 생성하는 모든 액션 타입을 편집해, 새 사용자 정의 속성에 대한 파라미터를 추가합니다. 필요한 추가 사항은 *rule\_name* 같은 비슷한 다른 속성의 예를 따라 확인하세요.

5. Workshop 애플리케이션에서 선택된 규칙의 사용자 정의 속성 값을 받는 Workshop 변수를 추가합니다. 기존 `selectedRule` 변수를 객체 집합(object set) 입력으로 하는 새 objectProperty 변수를 정의하면 됩니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/define_variable_selectedrule.png" alt="변수 정의" width="500" />

   이 Workshop 변수를 Rule Editor 구성 사이드바에서 "Create a proposal to edit rule" 액션의 기본값으로 설정합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/set_default_value.png" alt="Workshop 변수를 기본값으로 설정" width="300" />

6. 제안 위젯이 diff를 올바르게 표시하지 않으면 다음 단계를 따르세요.

   * Workshop 앱에서 Proposal Reviewer 위젯 구성의 **Properties grouped by section**에 `new_<PROPERTY>` 속성을 추가합니다. 여기서 "current" 값은 선택하지 않아도 됩니다.
   * 원한다면 속성 이름을 편집해 "new" 접두어를 없앱니다.
   * **제안 객체**의 **current** 속성에 `foundry-rules.property-diff-for:ID_OF_NEW_PROPERTY` 타입 클래스를 추가합니다.

       <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/custom_property_in_proposal_reviewer.png" alt="Proposal reviewer 구성 사이드바에 Alert Recipient 속성이 추가되어 있고, 제거할 수 있음을 나타내기 위해 'New' 접두어가 강조된 모습" width="300" />

**설명**: `severity` 하나를 추가할 때 고쳐야 하는 곳을 데이터 흐름 순서로 보면 다음과 같습니다.

- Rule 객체 타입: `severity` 속성과 이를 백킹할 데이터셋 열이 필요합니다(1단계). 온톨로지의 속성은 결국 데이터셋의 열이 있어야 존재할 수 있기 때문입니다.
- Proposal 객체 타입: 변경 전 값 `current_severity`와 변경 후 값 `new_severity`를 저장할 두 속성이 필요합니다(2단계). 제안은 "무엇에서 무엇으로 바뀌는지"를 기록해야 하기 때문입니다.
- 타입 클래스: `current_severity`에 `foundry-rules.property-diff-for:new_severity`를 붙이면 Proposal Reviewer 위젯이 두 속성을 짝으로 인식해 diff(노란색 새 값, 회색 이전 값)를 그릴 수 있습니다(3단계). 타입 클래스는 속성에 붙이는 메타데이터 태그로, 애플리케이션이 속성의 용도를 알아내는 데 쓰입니다.
- 액션 타입: 제안을 만들거나 승인하는 액션에 `severity` 파라미터가 없으면 폼에 입력 칸이 나오지 않고 값이 저장되지도 않습니다(4단계).
- Workshop 변수: 기존 규칙을 편집할 때 폼에 현재 `severity` 값이 미리 채워지도록 기본값을 연결합니다(5단계).

## 정리

- 사용자 정의 속성은 규칙 객체에 속성을 추가하는 것에서 시작하며, 그 속성은 입력 데이터셋의 열을 백킹으로 가져야 합니다.
- 제안 객체에는 `current_<PROPERTY>`와 `new_<PROPERTY>` 두 속성을 추가하고, current 속성에 `foundry-rules.property-diff-for:new_<PROPERTY>` 타입 클래스를 붙입니다.
- 규칙과 제안을 만들거나 수정하는 모든 액션 타입에 새 파라미터를 추가합니다.
- Workshop에서 `selectedRule` 기반 변수를 만들어 편집 액션의 기본값으로 설정하고, diff가 잘 보이지 않으면 Proposal Reviewer 구성을 조정합니다.
