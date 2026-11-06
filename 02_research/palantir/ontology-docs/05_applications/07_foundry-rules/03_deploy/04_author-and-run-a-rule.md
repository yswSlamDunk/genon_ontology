# 규칙 작성 및 실행 (Author and run a rule)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/author-and-run-a-rule/
- 사이드바 위치: Applications > Foundry Rules > Deploy > Author and run a rule

이 페이지는 Foundry Rules 배포의 마지막 단계로, Workshop 애플리케이션에서 규칙을 처음 작성하고, 제안을 승인하고, 데이터셋을 빌드해 결과를 확인하기까지의 절차를 설명합니다. 앞의 두 단계에서 만든 구성 요소가 실제로 맞물려 동작하는 과정을 끝까지 따라가 볼 수 있습니다.

다음 단계는 Workshop 애플리케이션에서 규칙을 작성하고 실행하는 과정을 안내합니다.

1. **Workshop Rule 애플리케이션 찾기:** 워크플로 구성 화면에서 폴더를 선택하고 Workshop 애플리케이션을 고릅니다. <br><br>
   ![Workshop 구성 페이지에 표시된 경로 스크린샷](https://www.palantir.com/docs/resources/foundry/foundry-rules/fr-workflow-path.png) <br><br>
   ![Workshop 애플리케이션 스크린샷](https://www.palantir.com/docs/resources/foundry/foundry-rules/fr-manual-open.png) <br><br>

2. **규칙 작성:** 앞 단계에서 만들어진 Workshop 애플리케이션 안에서 **Create New** 버튼을 클릭해 규칙 만들기를 시작합니다.
   * (a) 규칙 상단의 폼에 이름, 설명 등 정보를 채웁니다.
   * (b) 규칙이 실행할 로직을 작성합니다. 예를 들어 간단한 필터일 수 있습니다.
   * (c) **Submit changes**를 클릭해 이 새 규칙에 대한 제안(proposal)을 만듭니다. <br><br>
     ![Foundry 규칙 작성](https://www.palantir.com/docs/resources/foundry/foundry-rules/author_a_foundry_rule.png) <br><br>

3. **제안 승인:** Workshop 애플리케이션의 **Proposals** 탭에서 왼쪽에 있는 새로 만들어진 제안을 선택합니다.
   * **Approve**를 선택하면 제안이 규칙으로 활성화됩니다. <br><br>
     ![Foundry 규칙 제안 승인](https://www.palantir.com/docs/resources/foundry/foundry-rules/approve_rule_proposal.png) <br><br>

4. **규칙 라이트백 데이터셋과 규칙 출력 데이터셋 빌드:** [워크플로를 구성](03_configure-workflow.md)할 때 만든 출력 데이터셋으로 이동합니다. 규칙 라이트백 데이터셋은 규칙 객체 타입의 [라이트백 데이터셋 또는 머티리얼라이제이션(materialization)](../../../06_ontology-architecture/04_object-edits-and-materializations/06_materializations.md#comparison-of-writeback-datasets-and-materialized-datasets)이며, [트랜스폼 파이프라인](../02_core-concepts/05_foundry-rules-workflow-configuration.md#rule-execution)이 워크플로 입력에 적용하는 규칙들을 담고 있습니다.
   * **Actions**를 선택한 다음 **Explore data lineage**를 선택해 입력 데이터셋을 확인합니다. <br><br>
     ![출력 데이터셋의 Data Lineage로 이동](https://www.palantir.com/docs/resources/foundry/foundry-rules/navigate_to_data_lineage.png) <br><br>

   * 규칙 라이트백 데이터셋(d)과 출력 데이터셋(e)을 모두 선택합니다.

   * 두 데이터셋을 선택한 상태에서 마우스 오른쪽 버튼을 클릭하고 **Build**를 선택합니다. <br><br>
     ![규칙 라이트백 데이터셋과 Foundry 규칙 출력 데이터셋 빌드](https://www.palantir.com/docs/resources/foundry/foundry-rules/run_rules.png) <br><br>

   * 빌드가 끝나면 출력 데이터셋에 새 규칙의 결과가 들어 있습니다. 앞으로는 이 두 데이터셋을 [스케줄(schedule)](https://www.palantir.com/docs/foundry/data-lineage/manage-schedules/)에 등록해 출력을 최신 상태로 유지할 수 있습니다.

**설명**: 4단계에서 두 데이터셋을 함께 빌드하는 이유는 데이터 흐름 순서 때문입니다. 제안을 승인하면 Rule 객체가 온톨로지에서 바뀌지만, 파이프라인이 읽는 것은 그 편집이 반영된 라이트백 데이터셋입니다. 그래서 (1) 라이트백 데이터셋을 다시 빌드해 새 규칙을 데이터셋에 반영하고, (2) 출력 데이터셋을 빌드해 그 규칙을 입력 데이터에 적용해야 결과가 나옵니다. 라이트백 데이터셋만 빌드하면 규칙은 저장되지만 결과는 바뀌지 않고, 출력 데이터셋만 빌드하면 새 규칙이 아직 반영되지 않은 상태로 실행됩니다. 스케줄은 이 빌드를 정해진 시각이나 상위 데이터 변경 시 자동으로 실행하게 하는 설정입니다.

## 정리

- 워크플로 구성 화면의 폴더에서 Workshop 애플리케이션을 엽니다.
- **Create New**로 규칙의 정보와 로직을 입력하고 **Submit changes**로 제안을 만듭니다.
- **Proposals** 탭에서 제안을 **Approve**하면 규칙이 활성화됩니다.
- Data Lineage에서 규칙 라이트백 데이터셋과 출력 데이터셋을 함께 빌드하면 출력 데이터셋에 규칙 결과가 생기며, 이후에는 스케줄로 자동화할 수 있습니다.
