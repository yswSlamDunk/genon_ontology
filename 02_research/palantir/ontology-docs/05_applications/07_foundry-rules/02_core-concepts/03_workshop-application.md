# Workshop 애플리케이션 (Workshop application)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/workshop-application/
- 사이드바 위치: Applications > Foundry Rules > Core concepts > Workshop application

이 페이지는 사용자가 실제로 규칙을 만들고 검토하는 화면인 Foundry Rules의 Workshop 애플리케이션 구성을 설명합니다. 규칙을 작성하는 Rule Editor 페이지와 변경 제안을 승인하는 Proposal Reviewer 페이지가 각각 어떤 위젯으로 이루어져 있는지 알 수 있습니다.

표준 Foundry Rules 애플리케이션은 Workshop 애플리케이션이며, 보통 Rule Editor 페이지와 Proposal Reviewer 페이지의 두 페이지로 구성됩니다.

* **[Rule Editor](#rule-editor)** 페이지는 규칙을 생성, 편집(edit), 삭제하는 데 사용합니다.
* **[Proposal Reviewer](#proposal-reviewer)** 페이지는 규칙 제안(proposal)을 검토하고 승인 또는 거부하는 데 사용합니다.

읽기 전용 규칙 로직 뷰어를 만들 수 있는 **Rule Viewer** 위젯도 추가로 제공됩니다.

<a id="rule-editor"></a>
## Rule Editor

Rule Editor 페이지의 목적은 규칙을 생성하고 유지 관리할 수 있게 하는 것입니다. 다음 스크린샷은 아래 위젯(식별을 위해 번호를 붙임)으로 구성된 Rule Editor 페이지의 예입니다.

1. **Filter list:** 표시되는 규칙을 걸러 내는 필터 모음입니다.
2. **Object list:** Filter list(1)로 걸러진 기존 규칙 목록입니다. 항목을 선택하면 Rule Editor(3)에 내용이 채워집니다.
3. **Rule Editor:** 제안을 생성하는 Foundry 액션(Action)을 받아, 그 파라미터로부터 필요한 입력 필드를 자동 생성하는 위젯입니다. Rule Editor에 표시되는 폼 요소는 온톨로지에서 새 규칙 생성용으로 구성된 액션에 의해 결정됩니다. <br><br>
   ![위에서 설명한 세 개의 창이 있는 Rules editor Workshop 모듈 페이지](https://www.palantir.com/docs/resources/foundry/foundry-rules/rules_editor_annotated.png) <br><br>

*규칙*을 생성하거나 편집한 뒤에는 **Submit changes** 버튼을 눌러 새 *제안*을 만듭니다. 이 제안은 Proposal Reviewer 페이지에서 보고 검토할 수 있습니다.

**설명**: Rule Editor 위젯이 폼을 "자동 생성"한다는 것은, 액션 타입에 정의된 파라미터 목록(예: `rule_name`은 문자열, `alert_severity`는 선택 목록)을 읽어 각 파라미터에 맞는 입력 칸을 화면에 그려 준다는 뜻입니다. 따라서 입력 칸을 바꾸고 싶으면 위젯이 아니라 온톨로지의 액션 타입을 수정해야 합니다. 또 Submit changes를 눌러도 규칙이 바로 바뀌지 않고, 먼저 제안 객체만 생깁니다.

> **중간 요약**: Rule Editor 페이지는 필터, 규칙 목록, 편집 폼의 세 위젯으로 이루어지며, 편집 폼은 온톨로지의 액션 정의로부터 만들어집니다. 변경 사항은 제출 시 제안으로 저장됩니다.

<a id="proposal-reviewer"></a>
## Proposal Reviewer

Proposal Reviewer 페이지에서는 규칙 제안을 검토하고 승인 또는 거부할 수 있습니다. Rule Editor와 마찬가지로 세 부분으로 구성됩니다(아래 스크린샷에 번호로 표시).

1. **Filter list:** 어떤 제안을 표시할지 바꾸는 필터 모음입니다(1).
2. **Object list:** Filter list로 걸러진 제안 목록(2)입니다. 항목을 선택하면 Proposal Reviewer(3)에 내용이 채워집니다.
3. **Proposal Reviewer:** 제안을 승인하거나 거부하는 Foundry 액션을 받는 위젯입니다. 이 위젯은 편집된 속성(property)의 diff를 보여 주는데, 변경된 값은 노란색으로, 이전 값은 흐린 회색으로 표시됩니다. 사용자가 제안을 승인하면 편집 내용이 적용되고, 제안 내용에 따라 규칙이 생성, 편집, 삭제됩니다. <br><br>
   ![위에서 설명한 세 개의 창이 있는 Proposal reviewer Workshop 모듈 페이지](https://www.palantir.com/docs/resources/foundry/foundry-rules/proposal_reviewer_annotated.png) <br><br>

> **중간 요약**: Proposal Reviewer 페이지는 제안 목록과 diff 화면을 제공하며, 승인 액션이 실행되어야 비로소 규칙 객체가 실제로 바뀝니다.

## 정리

- Foundry Rules의 기본 화면은 Rule Editor와 Proposal Reviewer 두 페이지로 된 Workshop 애플리케이션입니다.
- 두 페이지 모두 Filter list, Object list, 전용 위젯(Rule Editor 또는 Proposal Reviewer)의 세 부분으로 구성됩니다.
- Rule Editor의 입력 폼은 온톨로지의 규칙 생성 액션에서 자동 생성되며, 제출하면 제안이 만들어집니다.
- Proposal Reviewer에서 승인하면 제안의 변경 사항이 규칙에 반영됩니다.
- 읽기 전용 화면이 필요하면 Rule Viewer 위젯을 사용할 수 있습니다.
