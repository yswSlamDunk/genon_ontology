# 변환 파이프라인 구성하기 (Configure transforms pipeline)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/configure-transforms-pipeline/
- 사이드바 위치: Applications > Foundry Rules > Legacy Foundry Rules setup (Taurus) > Configure transforms pipeline

이 페이지는 레거시(Taurus) 방식에서 Workshop 앱에 작성된 규칙을 실제 데이터에 적용하는 Java 변환(transform) 코드의 구조를 설명합니다. 변환은 규칙 데이터셋과 원천 데이터를 읽어 규칙을 실행하고, 그 결과를 규칙 액션별 출력 데이터셋과 상태 데이터셋으로 씁니다. 각 코드 블록이 무슨 역할을 하는지, 입력을 추가할 때 어디를 고쳐야 하는지를 다룹니다.

**주의**: 2022년 7월 이전의 Foundry Rules(이전 이름 Taurus)는 Foundry Rules를 실행하기 위해 사용자가 직접 변환을 만들어야 했습니다. 이 섹션은 2022년 7월 이전에 Foundry Rules를 배포한 경우에만 해당합니다.

규칙이 [Workshop 애플리케이션에서 작성되고 검토되고 나면](../03_deploy/04_author-and-run-a-rule.md), 인코딩된 로직은 변환의 일부로 적용됩니다. 이 섹션은 변환의 여러 구성 요소와, 이를 사용 사례에 맞게 구성하는 방법을 설명합니다. 변환의 대부분은 기본 배포를 통해 기본값으로 구성되지만, 워크플로를 확장하려면 추가 단계가 필요할 수 있습니다.

**설명**: Foundry에서 변환(transform)은 하나 이상의 입력 데이터셋을 읽어 계산한 뒤 출력 데이터셋을 쓰는 코드 단위입니다. 함수로 보면 `출력 데이터셋들 = f(입력 데이터셋들)`이며, 아래 예제에서는 Apache Spark의 `Dataset<Row>`(분산 처리되는 테이블)로 데이터를 다룹니다. 여기서 규칙은 코드에 하드코딩되지 않고 `rules_input` 데이터셋의 행으로 들어온다는 점이 핵심입니다. 사용자가 Workshop에서 규칙을 바꾸면 이 데이터셋의 행이 바뀌고, 변환을 다시 빌드하면 새 규칙이 적용됩니다.

<a id="example-transform"></a>
## 변환 예제 (Example transform)

[Foundry Rules 변환을 배포](../03_deploy/02_deploy-workflow.md)한 뒤의 변환은 아래 예제와 비슷한 모습입니다.

```java
public final class FoundryRulesTransformExample {
    // 아래 RID들을 바꾸는 것 외에도, 위쪽 'Settings' 탭의 "Ontology" 섹션에서
    // 관련 객체 타입과 관계(relation)를 프로젝트로 가져와야 합니다.
    @AdditionalInputs
    public static Set<InputSpec> additionalInputs = ImmutableOntologyInputs.builder()
            .addObjectRids("ri.ontology.main.object-type.4168ed49-00...") // employee
            // .addLinkRids("...") // 참조하는 모든 관계를 추가
            .ontologyRid("ri.ontology.main.ontology.00000000-0000-0000-0000-000000000000")
            .ontologyBranchRid("ri.ontology.main.branch.00000000-0000-0000-0000-000000000000")
            .build()
            .getInputSpecs();

    @Compute
    public void compute(
            @Input("ri.foundry.main.dataset.0000...") FoundryInput source_object_backing_dataset,
            @Input("ri.foundry.main.dataset.0000...") FoundryInput rules_input,
            @Output("ri.foundry.main.dataset.0000...") FoundryOutput outcome_output,
            @Output("REPLACE WITH PATH TO WRITE STATUS DATASET TO") FoundryOutput rule_status_output,
            TransformContext transformContext) {

        Dataset<Row> source = source_object_backing_dataset.asDataFrame().read();
        Dataset<Row> rulesDataset = rules_input.asDataFrame().read();

        // Taurus Rule Runner 구성
        Args ruleRunnerArgs = new TaurusRuleRunner.Args.Builder()
                .rules(new Rules.Builder()
                        .logicColumnName("RuleLogic")
                        .ruleIdColumnName("RuleId")
                        .dataset(rulesDataset)
                        .build())
                // Foundry Rules 편집기 Workshop 앱에서 쓰는 모든 원천을 여기에 넣습니다
                // (데이터셋의 경우 이 이름이 Foundry Rules 앱의 데이터셋 이름과 일치해야 합니다)
                .putSources(SourceReference.objectTypeId("employee"), source)
                // .putSources(SourceReference.dataset(DatasetName.of("name in Foundry Rules app")), dataset)
                // 다대다 온톨로지 조인 테이블을 쓰는 경우 필요:
                // .manyToManyJoinTables(ImmutableMap.of(LinkTypeId.of("relation-id"), dataset))
                // true로 두면 규칙 실행 결과가 rule editor 위젯의 미리 보기와 일치하도록 보장합니다(기본값 false)
                // .shouldMatchContourExecutionBehavior(true)
                .context(transformContext)
                .build();

        // Spark로 규칙 실행(지연 평가)
        RuleEffects ruleEffects = TaurusRuleRunner.runRules(ruleRunnerArgs);

        // 지정한 액션을 사용하는 모든 규칙의 결과를 가져옵니다
        Dataset<Row> outcomes = ruleEffects.actionReadyMergedDataset(
            ActionTypeRid.valueOf("ri.actions.main.action-type.b6f052c7-f7b1-4b4f-83ee-f81d9e854114"));
        outcome_output.getDataFrameWriter(outcomes).write();

        rule_status_output.getDataFrameWriter(ruleEffects.statusDataset()).write();
    }
}
```

**설명**: 이 변환은 다음 순서로 동작합니다.
1. `@AdditionalInputs`로 사용할 객체 타입(여기서는 employee)의 메타데이터에 접근할 권한을 선언합니다.
2. `compute`의 `@Input` 두 개로 employee 객체의 백킹 데이터셋(`source`)과 규칙들이 저장된 데이터셋(`rulesDataset`)을 읽습니다. `rulesDataset`은 행 하나가 규칙 하나이고, `RuleId` 열에 규칙 ID, `RuleLogic` 열에 규칙 로직이 들어 있습니다.
3. `TaurusRuleRunner.Args`에 규칙 데이터셋과 원천 데이터를 등록하고 `runRules`로 모든 규칙을 실행합니다.
4. `actionReadyMergedDataset`으로 특정 액션 타입 RID에 해당하는 결과만 모아 `outcome_output`에 쓰고, 실행 상태를 `rule_status_output`에 씁니다.

"지연 평가(lazily evaluated)"는 Spark의 특성으로, `runRules`를 호출하는 시점에는 실행 계획만 만들고 실제 계산은 `write()`가 호출될 때 일어난다는 뜻입니다.

이하 섹션들은 위 예제의 각 부분을 차례로 설명합니다. 원문은 섹션마다 해당 부분의 코드를 다시 보여 주지만, 여기서는 위 전체 예제의 해당 부분을 가리키는 것으로 대신합니다.

> **중간 요약**: 기본 배포로 생성되는 변환은 규칙 데이터셋과 원천 데이터를 읽어 `TaurusRuleRunner`로 규칙을 실행하고, 규칙 액션별 결과 데이터셋과 상태 데이터셋을 씁니다.

***

<a id="using-additionalinputs-to-add-ontology-inputs"></a>
## `@AdditionalInputs`로 온톨로지 입력 추가하기 (Using `@AdditionalInputs` to add Ontology inputs)

(원문에는 위 예제의 `@AdditionalInputs` 부분만 다시 보여 주는 코드가 있습니다.)

`@AdditionalInputs`를 사용하면 Foundry Rules에서 쓰는 객체 타입의 메타데이터에 접근할 권한을 제공할 수 있습니다. Foundry Rules Workshop 애플리케이션에서 쓰도록 구성한 모든 객체 타입은 여기에 추가해야 합니다. 첫 번째 객체 타입 RID는 기본으로 채워져 있지만, [워크플로 템플릿 배포](../03_deploy/02_deploy-workflow.md) 섹션에서 추가한 객체는 `.addObjectRids()` 항목으로 더 추가해야 합니다.

또한 Workshop 애플리케이션에서 사용할 모든 *관계(relation)는* `.addLinkRids()` 항목으로 여기에 추가해야 합니다. 이 RID들은 [Ontology Manager](../../04_ontology-manager/01_overview.md)의 객체 타입 페이지와 관계 페이지에서 각각 얻을 수 있습니다.

이 항목들을 추가한 뒤에는 Code Repository의 **Settings** 탭에 있는 **Ontology Imports** 도우미를 사용해 객체 타입과 관계를 프로젝트로 가져와야 합니다.

![가져온 객체 타입이 표시된 Ontology imports 설정 패널](https://www.palantir.com/docs/resources/foundry/foundry-rules/ontology_imports.png)

**설명**: 여기서 "관계(relation)"는 링크 타입의 이전 이름입니다. 예를 들어 규칙이 "직원의 소속 부서의 예산"처럼 employee에서 department로 링크를 따라가는 조건을 쓴다면, employee 객체 타입 RID뿐 아니라 employee와 department 사이 링크 타입의 RID도 `.addLinkRids()`로 등록해야 합니다.

<a id="input-and-output-datasets"></a>
## 입력 및 출력 데이터셋 (Input and output datasets)

(원문에는 위 예제의 `compute` 메서드 시그니처 부분만 다시 보여 주는 코드가 있습니다.)

이 부분은 애플리케이션의 Foundry 규칙이 사용하는 모든 [입력](../02_core-concepts/04_rule-logic.md#inputs)에 대한 데이터를 제공합니다. 여기에는 Foundry 규칙에서 사용하는 모든 객체의 백킹 데이터셋과 다대다 조인 테이블이 포함됩니다. 기본적으로 이 중 몇 가지는 미리 채워져 있습니다.

그러나 [워크플로 템플릿을 배포](../03_deploy/02_deploy-workflow.md)하면서 추가한 객체나 데이터셋은 여기에 새 `@Input` 항목으로 추가해야 합니다. 이 데이터셋들은 나중에 [TaurusRuleRunner.Args](#foundry-rules-rule-runner)에서 필요합니다.

또한 `rule_status_output`의 출력 경로를 지정해야 합니다. 이 데이터셋에는 성공적으로 실행되지 않은 규칙의 세부 정보가 들어 있어 디버깅 도구로 유용합니다.

**설명**: 다대다 조인 테이블은 데이터베이스 설계에서 배우는 연결 테이블(junction table)입니다. 예를 들어 직원과 프로젝트가 다대다 관계라면 `(employee_id, project_id)` 쌍을 담는 별도 테이블이 있어야 하고, 규칙이 이 링크를 따라가려면 이 테이블도 입력으로 받아야 합니다.

<a id="foundry-rules-rule-runner"></a>
## Foundry Rules 규칙 실행기 (Foundry Rules rule runner)

(원문에는 위 예제의 `TaurusRuleRunner.Args` 구성 부분만 다시 보여 주는 코드가 있습니다.)

이 부분은 `rulesDataset`에 담긴 Foundry 규칙을 최종적으로 실행할 규칙 실행기(`TaurusRuleRunner`)를 구성합니다. 이 부분도 대부분 기본값으로 미리 구성되어 있지만, [입력 및 출력 데이터셋](#input-and-output-datasets)에서 설명한 것처럼 추가 [입력](../02_core-concepts/04_rule-logic.md#inputs)은 `.putSources()` 항목을 추가해 `TaurusRuleRunner`에 등록해야 합니다. 또한 Foundry 규칙으로 구성된 객체들 사이에 쓰이는 다대다 조인 테이블은 위 예제처럼 `.manyToManyJoinTables()`로 여기에 등록해야 합니다.

**설명**: 입력을 하나 추가하려면 세 곳을 함께 고쳐야 합니다. 예를 들어 `department` 객체 타입을 추가한다면 (1) `.addObjectRids()`에 department 객체 타입 RID, (2) `compute`에 department 백킹 데이터셋을 받는 `@Input` 파라미터, (3) `.putSources(SourceReference.objectTypeId("department"), departmentDataset)`를 추가합니다. 하나라도 빠지면 규칙이 그 원천을 찾지 못합니다.

> **중간 요약**: Workshop에서 객체나 데이터셋 입력을 추가했다면 변환에서도 `@AdditionalInputs`(메타데이터 권한), `@Input`(데이터), `.putSources()`(실행기 등록) 세 곳을 함께 갱신해야 하며, 다대다 링크는 조인 테이블을 `.manyToManyJoinTables()`로 등록합니다. 상태 데이터셋 경로는 반드시 지정합니다.

<a id="rule-action-datasets"></a>
## 규칙 액션 데이터셋 (Rule Action datasets)

(원문에는 위 예제의 `runRules`와 `actionReadyMergedDataset` 호출 부분만 다시 보여 주는 코드가 있습니다.)

**규칙 액션(Rule Actions)은** 여러 Foundry 규칙에 공통으로 적용되는 출력 스키마 역할을 합니다. `.runRules()`로 모든 규칙을 실행한 뒤, 원하는 액션의 **Action type RID로** `.actionReadyMergedDataset()`을 호출하면 특정 규칙 액션에 해당하는 모든 결과 행을 얻을 수 있습니다. 이 RID는 [Ontology Manager](../../04_ontology-manager/01_overview.md)의 액션 타입 화면에서 찾을 수 있습니다.

![특정 액션 타입의 Action Type Rid가 보이는 Ontology 앱](https://www.palantir.com/docs/resources/foundry/foundry-rules/action_type_rid.png)

반환된 데이터셋은 위 예제처럼 변환의 출력으로 쓸 수 있습니다. 이 데이터셋에는 액션의 액션 파라미터마다 열이 하나씩 있고, 그 행이 나온 규칙의 ID를 담은 `Foundry Rules_rule_id` 열이 추가로 들어 있습니다.

Workshop 앱에 추가한 다른 **규칙 액션도** 예제를 복사한 뒤 액션 타입 RID를 바꾸고, [입력 및 출력 데이터셋](#input-and-output-datasets) 섹션에서 설명한 대로 새 출력 데이터셋을 추가해 여기에 포함할 수 있습니다.

변환이나 CI 검사를 실행할 때 오류가 발생하면 [문제 해결 참고 자료](../07_common-issues.md)를 검토하세요.

**설명**: 예를 들어 "Create Alert" 액션 타입의 파라미터가 `employee_id`(문자열)와 `severity`(정수) 두 개라면, `actionReadyMergedDataset`이 돌려주는 데이터셋은 `employee_id`, `severity`, 규칙 ID 열을 가집니다. 서로 다른 조건을 가진 규칙 10개가 모두 이 액션을 출력으로 쓰면, 10개 규칙의 결과 행이 이 하나의 스키마로 합쳐져(merged) 나옵니다. 열 이름 표기는 원문 이 페이지에서는 `Foundry Rules_rule_id`, 규칙 액션 구성 페이지에서는 `taurus_rule_id`로 서로 다르게 적혀 있어 원문 그대로 옮겼습니다.

<a id="reference-implementation"></a>
### 참조 구현 (Reference implementation)

Palantir 담당자가 구성해 두었다면 위 변환의 참조 구현이 제공될 수 있습니다. `Business Rules with Rules Workflow` 폴더를 검색하거나, **Foundry Training and Resources** 프로젝트로 이동한 다음 **Reference Examples > Application Development in Workshop > Business Rules with Rules Workflow로** 이동하세요.

여기에서 예제 항공(aviation) 온톨로지 위에 구현된 템플릿 워크플로 애플리케이션과 변환 파이프라인을 찾을 수 있습니다.

> **중간 요약**: 규칙 액션은 여러 규칙의 공통 출력 스키마이며, `actionReadyMergedDataset(액션 타입 RID)`로 해당 액션의 결과를 모아 출력 데이터셋으로 씁니다. 결과에는 파라미터별 열과 규칙 ID 열이 들어 있고, 액션을 추가하면 이 부분과 출력 데이터셋을 복제해 추가합니다.

## 정리

- 레거시(Taurus) 방식에서는 Workshop에서 작성된 규칙을 Java 변환으로 실행하며, 대부분은 기본 배포로 미리 구성됩니다.
- `@AdditionalInputs`에는 사용하는 모든 객체 타입과 관계 RID를 등록하고, Code Repository의 **Ontology Imports로** 프로젝트에 가져옵니다.
- 추가 입력은 `@Input`과 `.putSources()`에도 등록하고, 다대다 링크는 `.manyToManyJoinTables()`로 조인 테이블을 등록합니다.
- `runRules` 후 `actionReadyMergedDataset`으로 규칙 액션별 결과를 얻어 출력에 쓰며, 상태 데이터셋은 실패한 규칙을 디버깅하는 데 씁니다.
- 참조 구현은 **Foundry Training and Resources** 프로젝트의 예제 폴더에 있을 수 있습니다.
