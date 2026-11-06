# Foundry Rules 워크플로 구성 (Foundry Rules workflow configuration)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/foundry-rules-workflow-configuration/
- 사이드바 위치: Applications > Foundry Rules > Core concepts > Foundry Rules workflow configuration

이 페이지는 Foundry Rules 워크플로 전체의 설정을 다루는 워크플로 구성 편집기를 설명합니다. 규칙 작성자가 쓸 수 있는 입력, 규칙 결과가 저장될 출력, 규칙을 실행하는 트랜스폼 설정, 그리고 실제로 규칙이 실행되는 파이프라인 구조를 다룹니다.

**워크플로 구성 편집기(workflow configuration editor)는** Foundry Rules 워크플로 전체의 구성 방식을 바꿀 때 사용합니다. 예를 들어 규칙 작성자가 사용할 수 있도록 새 [입력](04_rule-logic.md#inputs)을 추가하거나, [워크플로 출력](#workflow-outputs)을 수정할 때 사용합니다. Foundry Rules 워크플로가 [배포](../03_deploy/01_deploy-foundry-rules.md)되고 나면 [Ontology Manager](../../04_ontology-manager/01_overview.md)에서 워크플로 구성 편집기에 접근할 수 있습니다. Foundry Rules 워크플로는 프로젝트(Project)에 연결되며 프로젝트 폴더에 리소스로 표시됩니다. 이를 통해 워크플로 구성에 대한 권한이 제어되고, 사용자는 워크플로의 이름을 바꾸거나 이동하거나 삭제할 수 있습니다.

<a id="workflow-inputs"></a>
## 워크플로 입력 (Workflow inputs)

[규칙 로직 입력](04_rule-logic.md#inputs) 섹션에서 설명했듯이, 구성 편집기의 **Inputs** 창은 워크플로 소유자가 규칙 작성자를 위해 입력을 추가하는 곳입니다. 객체 입력을 추가할 때 소유자는 연결된 링크 타입 중 어떤 것을 사용할 수 있게 할지도 선택할 수 있습니다.

![Foundry Rules 워크플로 입력](https://www.palantir.com/docs/resources/foundry/foundry-rules/workflow_inputs.png)

**설명**: 링크 타입을 함께 열어 두면 규칙 작성자는 입력 객체에서 링크를 따라 연결된 객체의 속성(property)까지 조건에 쓸 수 있습니다. 예를 들어 Transaction 입력에 Transaction과 Customer 사이의 링크 타입을 허용하면 "고객 국가가 X인 거래"처럼 두 테이블을 조인해야 하는 조건을 만들 수 있습니다.

<a id="workflow-outputs"></a>
## 워크플로 출력 (Workflow outputs)

워크플로 출력은 워크플로 안의 모든 Foundry 규칙이 내보내는 결과의 목적지와 형식을 지정합니다. 각 출력은 서로 다른 **Foundry 데이터셋** 하나에 대응하며, 이 데이터셋을 빌드하면 그 출력을 참조하는 모든 Foundry 규칙의 결과가 들어갑니다. 각 출력 안에서 출력 열의 이름과 타입을 구성할 수 있습니다. 출력 열이 [허용하는 값과 기본값](../04_settings-customization/05_permitted-and-default-output-values.md)을 제한할 수도 있습니다.

![Foundry Rules 워크플로 출력](https://www.palantir.com/docs/resources/foundry/foundry-rules/workflow_outputs.png)

<a id="transform-configuration"></a>
## 트랜스폼 구성 (Transform configuration)

이 섹션에는 Foundry 규칙의 결과를 생성하는 **트랜스폼(Transform)** 구성에 대한 추가 정보가 들어 있습니다. 규칙 상태 데이터셋(rule status dataset)의 위치와 트랜스폼에 적용된 **Spark 프로필(Spark profile)이** 포함됩니다. 이 섹션은 고급 구성이므로 Foundry Rules 워크플로를 처음 설정할 때는 무시해도 됩니다.

![Foundry Rules 트랜스폼 구성](https://www.palantir.com/docs/resources/foundry/foundry-rules/transform_config.png)

**설명**: 트랜스폼은 Foundry에서 입력 데이터셋을 읽어 계산한 뒤 출력 데이터셋을 쓰는 데이터 처리 작업입니다. Spark는 대용량 데이터를 여러 머신에 나눠 처리하는 분산 처리 엔진이고, Spark 프로필은 그 작업에 할당할 메모리와 실행기(executor) 수 같은 자원 설정 묶음입니다. 데이터가 커서 빌드가 느리거나 메모리 부족으로 실패할 때 조정하는 항목입니다.

<a id="rule-execution"></a>
## 규칙 실행 (Rule execution)

Foundry Rules 워크플로 구성은 규칙을 적용하는 트랜스폼 파이프라인도 생성합니다. 트랜스폼 파이프라인은 규칙이 실제로 효과를 내는 곳으로, 예를 들어 알림을 생성하거나 데이터를 분류하고 태깅합니다. 아래 [Data Lineage](https://www.palantir.com/docs/foundry/data-lineage/overview/) 그래프는 Foundry Rules 파이프라인의 예를 보여 줍니다. 파이프라인의 정확한 구조는 사용 사례에 따라 달라지며 필요와 상황에 따라 크게 다를 수 있습니다.

![객체를 백킹하는 데이터셋과 라이트백 데이터셋, 규칙을 작성할 대상 데이터셋, 규칙의 출력을 보여 주는 Data Lineage 그래프](https://www.palantir.com/docs/resources/foundry/foundry-rules/foundry_rules_data_lineage.png)

파이프라인은 [워크플로 입력](#workflow-inputs)을 백킹하는 데이터셋과 규칙의 라이트백(writeback) 데이터셋을 함께 받아 규칙을 입력에 적용합니다. 그런 다음 규칙이 내보낸 행으로 [워크플로 출력](#workflow-outputs)에 지정된 출력 데이터셋을 채웁니다.

**설명**: 동작 순서를 정리하면 다음과 같습니다. (1) 사용자가 Workshop에서 규칙을 만들고 제안이 승인되면 Rule 객체의 편집 내용이 라이트백 데이터셋에 기록됩니다. 라이트백 데이터셋은 사용자 편집이 반영된 객체 데이터를 데이터셋 형태로 내보낸 것입니다. (2) 파이프라인이 빌드될 때 이 라이트백 데이터셋에서 규칙 목록(각 규칙의 로직 JSON 포함)을 읽습니다. (3) 입력 데이터셋에 각 규칙의 로직을 적용합니다. (4) 결과 행을 출력 데이터셋에 씁니다. 즉 규칙의 정의는 온톨로지에, 규칙의 실행은 데이터 파이프라인에 있습니다.

> **중간 요약**: 워크플로 구성은 규칙 실행용 트랜스폼 파이프라인을 만들며, 이 파이프라인이 입력 데이터셋과 규칙 라이트백 데이터셋을 읽어 출력 데이터셋을 채웁니다.

## 정리

- 워크플로 구성 편집기는 Ontology Manager에서 열 수 있고, 워크플로는 프로젝트 폴더의 리소스로 관리됩니다.
- Inputs 창에서 규칙 작성자가 쓸 입력과 허용할 링크 타입을 정합니다.
- 워크플로 출력은 결과가 저장될 데이터셋과 열의 이름, 타입, 허용 값, 기본값을 정합니다.
- 트랜스폼 구성은 규칙 상태 데이터셋 위치와 Spark 프로필을 다루는 고급 설정입니다.
- 실제 규칙 실행은 입력 데이터셋과 규칙 라이트백 데이터셋을 읽어 출력 데이터셋을 만드는 트랜스폼 파이프라인에서 일어납니다.
