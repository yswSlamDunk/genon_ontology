# Workshop 애플리케이션 구성하기 (Configure Workshop application)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/configure-workshop-app/
- 사이드바 위치: Applications > Foundry Rules > Legacy Foundry Rules setup (Taurus) > Configure Workshop application

이 페이지는 2022년 7월 이전 방식(Taurus)으로 Foundry Rules를 배포한 경우, 규칙 워크플로 템플릿을 배포한 뒤 Rules Workshop 애플리케이션에서 추가로 해야 하는 구성을 다룹니다. 입력 객체와 데이터셋 지정, 규칙 액션 추가, 선택 기능 켜기, 제안 검토 시 변경 비교(diff) 표시 설정의 네 단계를 설명합니다.

**주의**: 2022년 7월 이전의 Foundry Rules(이전 이름 Taurus)는 사용자가 Workshop 애플리케이션에서 추가 구성을 제공해야 했습니다. 이 섹션은 2022년 7월 이전에 Foundry Rules를 배포한 경우에만 해당합니다.

[규칙 워크플로 템플릿을 배포](../03_deploy/02_deploy-workflow.md)한 뒤, 다음 단계에 따라 Rules Workshop 애플리케이션을 구성합니다.

*모든 스크린숏은 가상의 데이터를 사용합니다.*

1. **입력 구성(Configure inputs):** 워크플로 템플릿을 배포할 때 생성된 Workshop 모듈에서 **Rules** 탭의 **Rule Editor** 위젯을 선택합니다.

   * **Permitted object types**(허용된 객체 타입) 집합에는 기본적으로 워크플로 템플릿에서 선택한 **source**(원천) 객체가 들어 있습니다. Foundry Rules 안에서 다른 객체 타입도 쓸 수 있게 하려면 객체 집합(object set) 변수를 선택한 뒤 **Combine with another object set**을 선택합니다.
   * 객체 외에 데이터셋도 추가하려면 **Add Dataset** 버튼을 선택한 다음 입력 데이터셋 RID와 표시 이름을 입력합니다. 이 표시 이름은 나중에 파이프라인에서 입력 데이터셋을 참조할 때 사용됩니다.
   * 여기서 추가한 객체나 데이터셋은 나중에 [변환 파이프라인 구성](04_configure-transforms-pipeline.md)의 일부로 변환 파이프라인에도 추가해야 합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/add_input_objects_to_workshop_app.png" alt="Workshop 앱에 입력 객체를 추가하는 모습" width="600" />

2. **규칙 액션 추가(Add rule Actions):** [워크플로 템플릿을 배포](../03_deploy/02_deploy-workflow.md)할 때 규칙 액션을 구성했다면, 이미 규칙 액션 하나가 구성되어 있습니다. 규칙 액션을 더 추가하려면 먼저 Ontology Manager에서 액션을 만든 다음 **Add Rule actions**를 클릭해 추가합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/rule_action_configuration.png" alt="사용 가능한 규칙 액션 구성" width="500" />

   [규칙 액션 구성](05_configure-rule-actions.md)에 대해 더 알아보세요.

3. **선택 기능 켜기(Enable optional features):** Foundry Rules의 기능을 사용자 정의하기 위해 Workshop 앱의 Rule Editor 위젯 구성에 여러 옵션이 있습니다. [선택 기능](../04_settings-customization/02_enable-optional-features.md) 문서에 설명된 대로 이 옵션을 켜고 꺼서 고급 기능을 활성화하거나 비활성화합니다.

4. **제안 보기 시 diff 구성(Configure diffing when viewing proposals):** 제안 위젯이 변경 비교(diff)를 올바르게 표시하도록 하려면, 관련 **제안 객체(proposal object)** 속성에 다음 타입 클래스(type class)를 추가합니다. 이 타입 클래스는 **액션 파라미터가** 아니라 **객체 타입의** 속성에 추가합니다.

   * Proposal Reviewer 위젯에 표시하고 싶은 모든 속성에 대해, **현재(current)** 속성에 `foundry-rules.property-diff-for:ID_OF_NEW_PROPERTY` 타입 클래스를 추가합니다.
   * 예를 들어 제안 객체의 `new_rule_name` 속성이 규칙 이름의 새 값을, `current_rule_name` 속성이 이전 값을 나타낸다고 합시다. 그러면 `current_rule_name` 속성에 `foundry-rules.property-diff-for:new_rule_name`을 붙여야 합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/typeclass_example.png" alt="온톨로지 앱에서 속성에 추가한 타입 클래스 이름과 종류 예시" width="250" />

위 단계를 마친 뒤에는 만든 [변환 파이프라인을 워크플로에 맞게 구성](04_configure-transforms-pipeline.md)하는 방법을 알아보세요.

**설명**: 4단계의 제안 객체는 한 행에 "바꾸기 전 값"과 "바꾼 뒤 값"을 나란히 담는 구조입니다. 예를 들어 제안 객체 한 행이 `current_rule_name = "고액 거래"`, `new_rule_name = "고액 해외 거래"`라면, Proposal Reviewer는 이 두 열을 짝지어 "고액 거래"에서 "고액 해외 거래"로 바뀌었다고 보여 줘야 합니다. 그런데 시스템은 열 이름만 보고 어느 두 열이 짝인지 알 수 없으므로, 타입 클래스라는 메타데이터 태그를 현재 값 쪽 속성에 붙여 "이 속성은 `new_rule_name`의 이전 값이다"라고 알려 주는 것입니다. RID(Resource Identifier)는 Foundry가 데이터셋, 객체 타입 같은 리소스마다 붙이는 고유 식별자 문자열입니다.

## 정리

- 이 페이지는 2022년 7월 이전에 배포한 레거시(Taurus) 환경에만 해당합니다.
- Rule Editor 위젯에서 허용 객체 타입을 늘리거나 데이터셋 입력을 추가할 수 있으며, 추가한 입력은 변환 파이프라인에도 반영해야 합니다.
- 규칙 액션은 Ontology Manager에서 먼저 만든 뒤 **Add Rule actions**로 추가합니다.
- Rule Editor 위젯 구성에서 선택 기능을 켜고 끌 수 있습니다.
- 제안 diff를 보이려면 제안 객체의 현재 값 속성에 `foundry-rules.property-diff-for:<새 값 속성 ID>` 타입 클래스를 붙입니다.
