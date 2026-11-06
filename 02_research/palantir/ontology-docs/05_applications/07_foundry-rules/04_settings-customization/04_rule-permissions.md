# 규칙 편집 권한 (Permissions for editing rules)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/rule-permissions/
- 사이드바 위치: Applications > Foundry Rules > Settings & customization > Permissions for editing rules

이 페이지는 규칙을 편집하거나 삭제하는 제안을 누가 승인하고 거부할 수 있는지 제한하는 예시 설정을 설명합니다. 규칙 작성자가 자기 규칙의 변경에 대해 최종 승인권을 갖도록, 액션의 제출 조건(submission criteria)을 구성하는 방법을 다룹니다.

일부 워크플로에서는 규칙을 편집하거나 수정할 수 있는 사용자 집합을 제한하고 싶을 수 있습니다. 다음 예시는 규칙 작성자가 자기 규칙에 영향을 주는 모든 변경에 대해 최종 승인권을 갖도록 권한을 설정하는 방법을 보여 줍니다.

권한 설정은 다음과 같습니다.

* 규칙 작성자(와 슈퍼유저)만 자기 규칙을 편집하는 제안을 승인할 수 있습니다.
* 규칙 작성자(와 슈퍼유저)만 자기 규칙을 삭제하는 제안을 승인할 수 있습니다.
* 규칙 작성자와 제안 작성자(그리고 슈퍼유저)만 규칙 소유자의 규칙에 대한 제안을 거부할 수 있습니다.
  * 실수로 만든 제안 문제를 줄이기 위해, 제안 작성자도 제안을 거부할 수 있습니다. 예를 들어 사용자 A가 실수로 사용자 B의 규칙에 제안을 만들었다면, 사용자 A가 그 제안을 거부(사실상 철회)할 수 있습니다.

이 권한 설정을 구현하려면 아래 단계를 따르세요.

1. *approve a proposal to edit a rule* 액션을 구성해, 사용자가 제안과 연결된 규칙의 작성자이거나 슈퍼유저여야 하도록 합니다. <br><br>
   ![먼저 users 또는 superusers 그룹에 속해야 하고, 그리고(AND) 규칙 작성자이거나 슈퍼유저여야 하는 액션 검증 조건](https://www.palantir.com/docs/resources/foundry/foundry-rules/proposal_edit_validation.png) <br><br>

2. *approve a proposal to delete a rule* 액션을 구성해, 사용자가 제안과 연결된 규칙의 작성자이거나 슈퍼유저여야 하도록 합니다.

3. *reject a proposal* 액션을 구성해, 사용자가 제안과 연결된 규칙의 작성자, 제안 작성자, 슈퍼유저 중 하나여야 하도록 합니다. <br><br>
   ![규칙 작성자, 제안 작성자, 슈퍼유저 중 하나여야 하는 액션 검증 조건](https://www.palantir.com/docs/resources/foundry/foundry-rules/proposal_reject_validation.png) <br><br>

**참고**: 규칙 객체를 기준으로 검증하는 옵션이 보이지 않는다면, 아마 액션에 규칙 객체가 파라미터로 추가되어 있지 않은 것입니다. 다른 Foundry Rules 액션에 규칙 객체 파라미터를 추가하는 것과 같은 방식으로 *reject a proposal* 액션에 새 규칙 객체 파라미터를 추가하세요.

**설명**: 1단계의 조건을 논리식으로 쓰면 `(현재 사용자 ∈ users 그룹 OR 현재 사용자 ∈ superusers 그룹) AND (현재 사용자 == rule.author OR 현재 사용자 ∈ superusers 그룹)`입니다. 여기서 `rule.author`는 액션 파라미터로 받은 규칙 객체의 작성자 속성(property) 값입니다. 그래서 조건이 규칙 객체의 속성을 참조하려면 그 객체가 액션의 파라미터로 들어와 있어야 하며, 참고 문단은 바로 이 점을 말합니다.

## 정리

- 예시 설정의 목표는 규칙 작성자가 자기 규칙의 편집과 삭제에 대해 최종 승인권을 갖게 하는 것입니다.
- 편집 승인과 삭제 승인 액션은 규칙 작성자 또는 슈퍼유저만 실행할 수 있도록 제출 조건을 설정합니다.
- 거부 액션은 규칙 작성자, 제안 작성자, 슈퍼유저가 실행할 수 있게 하여 실수로 만든 제안을 철회할 수 있게 합니다.
- 규칙 객체 기준 검증을 하려면 해당 액션에 규칙 객체 파라미터가 있어야 합니다.
