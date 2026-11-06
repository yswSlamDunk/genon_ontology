# 워크플로 구성 (Configure workflow)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/configure-workflow/
- 사이드바 위치: Applications > Foundry Rules > Deploy > Configure workflow

이 페이지는 Foundry Rules 배포의 두 번째 단계로, 배포한 워크플로에 입력과 출력을 추가하고 저장해 규칙 실행 파이프라인을 만드는 절차를 설명합니다. 마지막에는 제한된 뷰를 쓰는 객체 등에 필요한 대체 백킹 데이터셋이라는 고급 설정도 다룹니다.

[워크플로 템플릿 배포](02_deploy-workflow.md)를 마쳤다면, 다음 단계에 따라 [워크플로를 구성](../02_core-concepts/05_foundry-rules-workflow-configuration.md)합니다.

1. **기존 규칙 열기:** Foundry Rules 홈 페이지의 기존 규칙 목록에서 항목을 선택합니다. 또는 **Files**에서 해당 프로젝트로 이동해 선택할 수도 있습니다. <br><br>
   ![Foundry Rules의 기존 규칙 목록](https://www.palantir.com/docs/resources/foundry/foundry-rules/overview@2x.png) <br><br>

2. **워크플로 입력 추가:** 규칙을 연 상태에서 **Add Input** 버튼을 선택해 워크플로에 객체 또는 데이터셋 입력을 추가합니다. 추가한 입력은 다음 섹션에서 작성하는 규칙의 입력으로 사용할 수 있게 됩니다.
   * 입력은 원하는 만큼 추가할 수 있지만, 모든 워크플로에는 입력이 최소 하나 있어야 합니다.
   * 객체 타입 입력을 추가하면 각 객체 타입 아래에 링크 타입 섹션이 나타납니다. 여기서 선택한 링크는 [Rules Management 애플리케이션](../02_core-concepts/03_workshop-application.md)에서 서로 다른 객체를 조인하는 데 사용할 수 있게 됩니다. <br><br>
     ![새 워크플로 입력을 추가하는 버튼](https://www.palantir.com/docs/resources/foundry/foundry-rules/add_workflow_input.png) <br><br>

**주의**: 제한된 뷰(restricted view)를 백킹으로 하는 객체는 입력으로 직접 사용할 수 없습니다. 대신 그 제한된 뷰를 백킹하는 데이터셋을 [대체 백킹 데이터셋(alternate backing dataset)](03_configure-workflow.md#alternate-backing-datasets)으로 구성하세요.

3. **워크플로 출력 추가:** 편집기의 세 번째 섹션에서 **Add Dataset Output**을 클릭하고, 규칙 결과가 출력될 데이터셋의 이름과 위치를 입력합니다. <br><br>
   ![새 워크플로 출력을 추가하는 버튼](https://www.palantir.com/docs/resources/foundry/foundry-rules/add_workflow_output.png) <br><br>

   * **Rules Management 애플리케이션**에서 규칙 작성자에게 표시될 출력 이름을 입력합니다(a).
   * **Add column**을 클릭해 출력에 열을 최소 하나 추가합니다(b). 이 열에는 데이터셋에서 쓰일 이름과, 규칙 애플리케이션에서 규칙 작성자에게 보여 줄 표시 이름을 지정합니다. 열의 타입을 구성할 수 있고, 규칙을 작성할 때 이 열의 값을 반드시 입력해야 하는지도 정할 수 있습니다. [허용 값과 기본 출력 값](../04_settings-customization/05_permitted-and-default-output-values.md)에 대해 더 알아보세요.
   * 규칙 결과에서 담고 싶은 정보마다 열을 하나씩 추가합니다. 예를 들어 알림 워크플로라면 `Alert ID`, `Severity`, `Assignee` 열과 함께 알림을 일으킨 객체의 식별자를 담는 열(예: `Machine ID`)을 둘 수 있습니다. <br><br>
     ![워크플로 출력 구성](https://www.palantir.com/docs/resources/foundry/foundry-rules/workflow_output_configuration.png) <br><br>

4. **워크플로 저장:** 구성 편집기 오른쪽 위의 저장 버튼을 클릭합니다.
   * 워크플로를 저장하면 편집기 상단에 녹색 배너가 나타나며, 이는 [트랜스폼 파이프라인](../02_core-concepts/05_foundry-rules-workflow-configuration.md#rule-execution)이 성공적으로 생성되었음을 뜻합니다. <br><br>
     ![트랜스폼 파이프라인이 성공적으로 생성되었음을 보여 주는 배너](https://www.palantir.com/docs/resources/foundry/foundry-rules/transforms-pipeline-success-banner.png) <br><br>

위 단계를 마쳤으면 [규칙을 작성하고 실행하는 방법](04_author-and-run-a-rule.md)을 알아보세요.

**설명**: 출력 열 구성은 결과 테이블의 스키마를 미리 정하는 작업입니다. 예를 들어 열을 `alert_id`(String, 필수), `severity`(String, 필수), `assignee`(String, 선택), `machine_id`(String, 필수)로 정의하면, 규칙 작성자는 규칙마다 이 네 칸을 채우는 폼을 보게 되고, 모든 규칙의 결과는 이 네 열을 가진 한 데이터셋에 쌓입니다. `machine_id`처럼 원인 객체의 식별자를 남겨 두면 나중에 알림에서 해당 객체로 거슬러 올라갈 수 있습니다.

> **중간 요약**: 워크플로를 열어 입력(객체 또는 데이터셋, 필요 시 링크 타입)과 출력 데이터셋의 열을 추가하고 저장하면, 규칙을 실행할 트랜스폼 파이프라인이 생성됩니다.

<a id="advanced-configurations"></a>
## 고급 구성 (Advanced configurations)

<a id="alternate-backing-datasets"></a>
### 대체 백킹 데이터셋 (Alternate backing datasets)

객체 입력에 대체 백킹 데이터셋을 구성할 수 있습니다. 이렇게 하면 규칙이 온톨로지에 구성된 라이트백(writeback) 데이터셋(또는 백킹 데이터셋) 대신 지정한 대체 백킹 데이터셋을 대상으로 평가됩니다.

다음과 같은 경우에 유용합니다.

* 제한된 뷰를 백킹으로 하는 객체에 대해 규칙을 작성할 때
* 객체의 백킹 데이터 중 일부에 대해서만 규칙을 실행할 때 <br><br>
  <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/configuring_alternate_backing_datasets.png" alt="대체 백킹 데이터셋 구성" width="800" />

<br><br>

**설명**: 예를 들어 Machine 객체 타입의 백킹 데이터셋에 전 세계 공장의 기계 10만 대가 들어 있는데 한국 공장 기계 5천 대에만 규칙을 돌리고 싶다면, 그 5천 행만 걸러 낸 데이터셋을 따로 만들어 대체 백킹 데이터셋으로 지정할 수 있습니다. 규칙 작성 화면에서는 여전히 Machine 객체 타입과 그 속성(property) 이름으로 규칙을 쓰지만, 파이프라인이 실제로 읽는 데이터는 지정한 데이터셋이 됩니다.

> **중간 요약**: 대체 백킹 데이터셋을 지정하면 규칙이 온톨로지 기본 데이터 대신 지정한 데이터셋에 적용되며, 제한된 뷰 객체나 부분 데이터 처리에 쓰입니다.

## 정리

- 워크플로 구성은 기존 워크플로 열기, 입력 추가, 출력 추가, 저장의 네 단계입니다.
- 입력은 최소 하나 필요하며, 객체 입력에는 조인에 쓸 링크 타입을 함께 허용할 수 있습니다.
- 출력은 결과 데이터셋의 이름, 위치, 열(이름, 표시 이름, 타입, 필수 여부)을 정의합니다.
- 저장하면 녹색 배너와 함께 트랜스폼 파이프라인이 생성됩니다.
- 대체 백킹 데이터셋으로 제한된 뷰 객체나 데이터 일부에 대해 규칙을 실행할 수 있습니다.
