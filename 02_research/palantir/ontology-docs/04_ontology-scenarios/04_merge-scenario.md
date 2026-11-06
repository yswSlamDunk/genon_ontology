# 시나리오 병합하기 (Merge scenarios)

- 원문: https://www.palantir.com/docs/foundry/ontology/merge-scenario/
- 사이드바 위치: Ontology scenarios > Merge scenarios

이 페이지는 시나리오 안에서 쌓아 둔 편집(edit)을 실제 온톨로지에 반영하는 "병합(merge)" 방법을 다룹니다. 병합은 전용 액션 타입을 통해 이루어지므로, 누가 병합할 수 있는지와 어떤 편집을 반영할지를 세밀하게 통제할 수 있습니다.

시나리오는 액션 타입을 통해 병합합니다. 액션 타입을 사용하면 시나리오 편집을 세밀하게 제어할 수 있고, 실행 권한을 세분화해 강제할 수 있습니다. 병합 액션에는 최소한 **Scenario** 파라미터 하나가 필요합니다. 이 파라미터는 시나리오의 RID이며, 그 시나리오에서 실행된 모든 액션을 포함합니다. 파라미터 값은 Workshop 변수나 OSDK 애플리케이션에서 전달할 수 있습니다.

<a id="apply-edits-on-a-scenario"></a>
## 시나리오의 편집 적용하기 (Apply edits on a scenario)

시나리오 안에서 작업할 때는 모든 편집(객체 생성, 속성 수정, 객체 삭제, 링크 추가나 제거)이 그 시나리오의 격리된 샌드박스(sandbox) 안에만 존재합니다. 이 편집은 메인 온톨로지에 영향을 주지 않습니다. 시나리오를 적용(apply)하면 병합 액션을 통해 쌓여 있던 편집 전체가 하나의 트랜잭션으로 온톨로지에 커밋됩니다.

**설명**: 트랜잭션(transaction)은 여러 변경을 "모두 반영되거나 하나도 반영되지 않거나" 둘 중 하나로 처리하는 단위입니다. 예를 들어 시나리오 안에서 객체 3개를 수정하고 링크 1개를 추가했다면, 병합 시 이 4개 변경이 한꺼번에 반영됩니다. 중간에 실패하면 일부만 반영된 상태로 남지 않습니다. 데이터베이스의 `BEGIN ... COMMIT`과 같은 동작입니다.

<a id="configure-the-merge-action"></a>
## 병합 액션 설정하기 (Configure the merge action)

1. **Ontology Manager**에서 **Action types** 탭으로 이동해 **+ New action type**을 선택합니다. 생성 마법사에서 **Scenario** 탭을 선택합니다.
2. **Scenario** 탭 안에서 관련 **Object types**와 **Link types**를 추가해 시나리오 편집의 범위를 정의합니다. <br><br>
   ![병합 액션을 설정하기 위한 Object type과 Link type 선택 필드가 있는 Scenario 탭을 보여 주는 새 액션 타입 생성 대화 상자.](https://www.palantir.com/docs/resources/foundry/ontology/merge-scenario-action.png) <br><br>
3. 마법사를 마친 뒤 새로 만든 액션의 **Security & Submission Criteria** 탭을 열어 병합 액션을 실행할 수 있는 사용자를 정의합니다.

이미 있는 액션을 병합 액션으로 쓰고 싶다면, 새 액션 타입을 만드는 대신 Ontology Manager의 액션 설정에서 **Rules** 탭에 들어가 **Apply Scenario** [규칙(rule)](../02_define-ontologies/03_action-types/06_rules.md)을 추가하면 됩니다.

![Ontology Manager의 Apply Scenario 규칙에 있는 Scenario 파라미터.](https://www.palantir.com/docs/resources/foundry/ontology/merge-scenario-parameter.png)

**설명**: 2단계에서 지정하는 객체 타입과 링크 타입이 병합 범위입니다. 즉, 이 액션으로 병합할 때 반영 대상이 되는 편집의 종류를 미리 정해 두는 것입니다. 3단계의 제출 조건(submission criteria)은 "특정 그룹만 병합할 수 있다" 같은 조건을 거는 곳입니다.

## 정리

- 시나리오 안의 편집은 격리된 샌드박스에만 존재하며, 병합 액션을 실행해야 메인 온톨로지에 하나의 트랜잭션으로 반영됩니다.
- 병합 액션은 최소한 시나리오 RID를 받는 **Scenario** 파라미터가 필요하고, 값은 Workshop 변수나 OSDK에서 전달합니다.
- 새 액션 타입을 만들 때 **Scenario** 탭에서 범위(객체 타입, 링크 타입)를 정하거나, 기존 액션에 **Apply Scenario** 규칙을 추가해 병합 액션으로 만들 수 있습니다.
- 실행 권한은 **Security & Submission Criteria** 탭에서 통제합니다.
