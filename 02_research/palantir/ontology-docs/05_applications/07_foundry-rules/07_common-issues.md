# 문제 해결 참고 자료 (Troubleshooting reference)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/common-issues/
- 사이드바 위치: Applications > Foundry Rules > Troubleshooting reference

이 페이지는 Foundry Rules를 사용하면서 자주 만나는 오류 메시지와 증상, 그리고 각각의 원인과 해결 단계를 정리한 참고 자료입니다. 현재 버전에서 생기는 오류와 함께, 2022년 7월 이전의 구버전(Taurus) 설정에서 생기던 오류도 다룹니다.

이 페이지는 Foundry Rules에서 흔히 발생하는 몇 가지 문제와 디버깅 단계를 설명합니다.

<a id="error-messages"></a>
## 오류 메시지 (Error messages)

<a id="readonlyobjecterror"></a>
### `ReadonlyObjectError`

생성한 각 객체에 라이트백(writeback) 데이터셋이 연결되어 있는지 확인하세요. 자세한 내용은 [규칙 작성 및 실행](03_deploy/04_author-and-run-a-rule.md)의 라이트백 데이터셋 빌드 단계를 참고하세요.

**설명**: 라이트백 데이터셋은 사용자가 액션으로 객체를 수정한 내용(편집)이 기록되는 데이터셋입니다. 객체 타입에 라이트백 데이터셋이 없으면 그 객체는 읽기 전용 상태가 되어, 규칙이 객체를 만들거나 바꾸려 할 때 이 오류가 납니다.

<a id="400-actionsinvalidparametersforapply"></a>
### 400: `Actions:InvalidParametersForApply`

액션 요청에 필수 파라미터 일부가 제공되지 않았습니다. 액션이 올바르게 설정되었는지 확인하세요.

**설명**: 400은 HTTP 상태 코드 "Bad Request"로, 요청 형식이나 내용이 서버가 받아들일 수 없는 상태라는 뜻입니다. 여기서는 액션 타입에 필수로 정의된 파라미터 값이 요청에 빠져 있다는 의미입니다.

> **중간 요약**: `ReadonlyObjectError`는 라이트백 데이터셋이 없을 때, `Actions:InvalidParametersForApply`는 액션의 필수 파라미터가 빠졌을 때 발생합니다.

<a id="proposal-diff-not-displayed-correctly-for-custom-property"></a>
## 사용자 지정 속성의 제안 차이가 올바르게 표시되지 않음 (Proposal diff not displayed correctly for custom property)

제안(proposal) 위젯이 차이(diff)를 올바르게 표시하게 하려면 다음 단계를 따르세요.

1. Workshop 앱에서 Proposal Reviewer 위젯 설정의 **Properties grouped by section**(섹션별로 그룹화된 속성)에 `new_<PROPERTY>` 속성을 추가합니다. 여기서 "current"(현재) 값을 선택할 필요는 없습니다.

2. 원한다면 속성 이름을 편집해 "new" 접두사를 제거합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/custom_property_in_proposal_reviewer.png" alt="Proposal Reviewer 설정 사이드바에 추가된 Alert Recipient 속성. 제거할 수 있는 'New' 접두사가 강조되어 있음" width="300" />

3. **제안 객체(proposal object)** 의 **current** 속성에 `foundry-rules.property-diff-for:ID_OF_NEW_PROPERTY` 타입 클래스(type class)를 추가합니다. 타입 클래스는 *kind*(종류)와 *name*(이름)으로 구성되며 `kind.name` 형태로 씁니다. `foundry-rules.property-diff-for:new_<PROPERTY>`의 경우 kind는 `foundry-rules`이고 name은 `property-diff-for:new_<PROPERTY>`입니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/typeclass_example.png" alt="온톨로지 앱에서 속성에 추가한 타입 클래스의 name과 kind 예시" width="300" />

**설명**: Foundry Rules의 제안 객체는 같은 정보를 "현재 값" 속성과 "새 값"(`new_` 접두사) 속성 쌍으로 들고 있고, Proposal Reviewer 위젯은 두 값을 비교해 차이를 보여 줍니다. 예를 들어 사용자 지정 속성 `alert_recipient`를 추가했다면 `new_alert_recipient`를 위젯에 등록하고, 현재 값 속성에 `foundry-rules.property-diff-for:new_alert_recipient` 타입 클래스를 붙여 "이 속성은 `new_alert_recipient`와 비교할 대상"이라는 짝을 알려 주는 것입니다. 타입 클래스는 속성에 붙이는 메타데이터 태그로, 애플리케이션이 그 속성을 어떻게 다룰지 판단하는 데 씁니다.

> **중간 요약**: 사용자 지정 속성의 차이를 보이려면 `new_<PROPERTY>`를 Proposal Reviewer 위젯에 추가하고, 현재 값 속성에 `foundry-rules.property-diff-for:new_<PROPERTY>` 타입 클래스를 붙여 두 속성을 짝지어야 합니다.

<a id="older-errors"></a>
## 이전 오류 (Older errors)

2022년 7월 이전의 Foundry Rules(이전 이름 Taurus)는 추가 설정이 필요했고 약간 다른 개념을 사용했습니다. 다음 오류는 그 과정과 관련된 것입니다. 2022년 7월 이후에 Foundry Rules를 배포했는데 아래 문제 중 하나를 만났다면, [Workflow Configuration Editor](02_core-concepts/05_foundry-rules-workflow-configuration.md)로 이동해 워크플로에 오류가 있는지 확인해 보세요.

<a id="taurusmissingontologyinformation"></a>
### `Taurus:MissingOntologyInformation`

이 오류는 오류 메시지에 표시된, 요청한 온톨로지 정보가 존재하지 않거나 트랜스폼에 그 정보에 접근할 권한이 없다는 뜻입니다. 오류를 해결하려면 다음 단계를 확인하세요.

1. 메시지에 있는 RID 또는 ID가 [Ontology Manager](../04_ontology-manager/01_overview.md)에 존재하는지 확인합니다.
2. Foundry Rules Workshop 애플리케이션에서 사용하는 모든 객체 타입 *과* 관계(relation)를 Code Repository의 **Settings** 탭에 있는 **Ontology Imports** 도우미로 프로젝트에 가져왔는지 확인합니다.
3. Foundry Rules Workshop 애플리케이션에서 사용하는 모든 객체 타입 *과* 관계의 RID가 트랜스폼 코드 상단의 `@AdditionalInputs` 섹션에 나열되어 있는지 확인합니다. [`@AdditionalInputs` 사용](06_legacy-foundry-rules-setup-taurus/04_configure-transforms-pipeline.md#using-additionalinputs-to-add-ontology-inputs)에 대해 더 알아보세요.
4. Foundry Rules Workshop 애플리케이션에서 사용하는 객체 타입과 다대다(many-to-many) 관계의 모든 백킹 데이터셋을 프로젝트 뷰의 **Project References** 섹션으로 프로젝트에 [가져왔는지](https://www.palantir.com/docs/foundry/compass/move-and-share-resources/) 확인합니다. 여기에는 Restricted View로 뒷받침되는 객체나 관계도 포함됩니다.

**설명**: 다대다 관계는 학생과 강의처럼 양쪽 모두 여러 개와 연결될 수 있는 관계입니다. 관계형 데이터베이스에서 이런 관계는 `(student_id, course_id)` 쌍을 저장하는 별도의 조인 테이블로 표현하는데, 온톨로지의 다대다 링크 타입도 이런 조인 데이터셋을 백킹 데이터셋으로 가집니다. 그래서 객체 타입의 데이터셋뿐 아니라 이 조인 데이터셋도 프로젝트에 가져와야 합니다. Restricted View는 행 단위 접근 제어가 적용된 데이터 뷰입니다.

<a id="transformsgradlepluginstatictaurusdependencydisallowed"></a>
### `TransformsGradlePlugin:StaticTaurusDependencyDisallowed`

이 오류는 `tau-execution-core`에 고정된 버전 번호로 의존성을 선언하는 것이 더 이상 허용되지 않는다는 뜻입니다. 이 오류를 해결하려면 선언된 버전을 고정 버전 번호 대신 버전 범위 `[0,1[`로 바꿉니다.

1. 먼저 Foundry Rules 트랜스폼이 들어 있는 [**Code Repository**](https://www.palantir.com/docs/foundry/code-repositories/overview/)로 이동합니다.
2. **Show hidden files and folders**를 켭니다.
3. 프로젝트 수준 `build.gradle` 파일에서 다음 줄
   `compile "com.palantir.tau-execution:tau-execution-core:0.x.x"`
   을 `compile "com.palantir.tau-execution:tau-execution-core:[0,1["`로 바꿉니다.
   * `compile "com.palantir.tau-grammar:tau-grammar-api-objects:0.x.x"` 라는 다른 줄이 있다면 *이 줄을 삭제합니다*.
4. 결과를 커밋하면 검사(checks)가 통과합니다.

**설명**: `[0,1[`는 수학의 반열린 구간 표기로, "0 이상 1 미만의 모든 버전"을 뜻합니다. 고정 버전(예: `0.60.4`)을 쓰면 그 버전에 묶이지만, 범위를 쓰면 빌드 시점에 그 범위 안의 최신 버전을 받아 오게 됩니다.

<a id="the-rule-editor-preview-does-not-match-the-output-from-the-foundry-rules-transform"></a>
### Rule Editor 미리 보기가 Foundry Rules 트랜스폼의 출력과 일치하지 않음 (The Rule Editor preview does not match the output from the Foundry Rules transform)

1. Foundry Rules 트랜스폼의 입력 데이터셋이 Rule Editor 미리 보기에서 객체를 뒷받침하는 데이터셋과 일치하는지 확인합니다.
2. Foundry Rules 트랜스폼에서 `.shouldMatchContourExecutionBehavior(true)` 플래그가 `true`로 설정되어 있는지 확인합니다(아래 예시). 이 플래그는 Foundry Rules 트랜스폼이 수행하는 로직 실행이 Rule Editor 미리 보기에서와 같도록 보장합니다.

```java
    // Foundry Rules Rule Runner 설정
    Args ruleRunnerArgs = new TaurusRuleRunner.Args.Builder()
            .rules(new Rules.Builder()
                    .logicColumnName("RuleLogic")
                    .ruleIdColumnName("RuleId")
                    .dataset(rulesDataset)
                    .build())
            .putSources(SourceReference.objectTypeId("employee"), source)
            // 규칙 실행 결과가 Rule Editor 위젯의 미리 보기와 일치하도록 true로 설정
            .shouldMatchContourExecutionBehavior(true)
            .context(transformContext)
            .build();
```

**설명**: 이 코드는 규칙 실행기(`TaurusRuleRunner`)에 넘길 인자를 빌더로 구성합니다. `rules(...)`는 규칙이 저장된 데이터셋(`rulesDataset`)과 그 안에서 규칙 로직 열(`RuleLogic`), 규칙 ID 열(`RuleId`)의 이름을 지정합니다. `putSources`는 객체 타입 `employee`를 입력 소스 `source`에 연결합니다. 핵심 줄은 `.shouldMatchContourExecutionBehavior(true)`로, 트랜스폼의 실행 방식을 미리 보기(Contour 기반 실행)와 같게 맞춥니다.

<a id="taurusunknownmeasurename"></a>
### `Taurus:UnknownMeasureName`

이 오류는 센서 객체가 없거나 트랜스폼에 올바른 권한이 없을 때 발생할 수 있습니다. 오류를 해결하려면 다음을 확인하세요.

* 루트 객체와 센서 객체 사이 링크의 RID를 Code Repository의 **Settings** 탭에 있는 Ontology Imports 도우미로 프로젝트에 가져왔는지 확인합니다.
* 루트 객체와 센서 객체 사이 링크의 RID가 트랜스폼 코드 상단의 `@AdditionalInputs` 섹션에 나열되어 있는지 확인합니다.
* 센서 객체의 백킹 데이터셋이 트랜스폼 코드 상단의 `@AdditionalInputs` 섹션에 나열되어 있는지 확인합니다.
* 센서 객체의 백킹 데이터셋을 프로젝트 뷰의 **Project References** 섹션으로 프로젝트에 [가져왔는지](https://www.palantir.com/docs/foundry/compass/move-and-share-resources/) 확인합니다.

[배포 가이드](06_legacy-foundry-rules-setup-taurus/04_configure-transforms-pipeline.md)의 모든 단계를 따랐는지 확인하세요.

> **중간 요약**: 구버전 오류의 대부분은 트랜스폼이 온톨로지 리소스에 접근하지 못해서 생기며, Ontology Imports, `@AdditionalInputs`, Project References 세 곳에 필요한 리소스가 모두 들어 있는지 확인하면 해결됩니다. 의존성 버전은 범위 `[0,1[`로 선언하고, 미리 보기와 결과를 맞추려면 `shouldMatchContourExecutionBehavior(true)`를 설정합니다.

## 정리

- `ReadonlyObjectError`는 라이트백 데이터셋 누락, `Actions:InvalidParametersForApply`는 필수 액션 파라미터 누락이 원인입니다.
- 사용자 지정 속성의 제안 차이를 보이려면 `new_<PROPERTY>`를 Proposal Reviewer에 추가하고 현재 값 속성에 `foundry-rules.property-diff-for:` 타입 클래스를 붙입니다.
- 구버전(Taurus) 오류인 `MissingOntologyInformation`과 `UnknownMeasureName`은 객체 타입, 링크, 백킹 데이터셋을 Ontology Imports, `@AdditionalInputs`, Project References에 등록해 해결합니다.
- `StaticTaurusDependencyDisallowed`는 `build.gradle`의 버전을 `[0,1[` 범위로 바꿔 해결합니다.
- 미리 보기와 트랜스폼 결과가 다르면 입력 데이터셋 일치 여부와 `shouldMatchContourExecutionBehavior(true)` 설정을 확인합니다.
