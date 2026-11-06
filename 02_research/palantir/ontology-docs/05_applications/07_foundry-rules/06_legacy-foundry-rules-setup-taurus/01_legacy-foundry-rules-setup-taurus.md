# 레거시 Foundry Rules 설정(Taurus) 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/legacy-foundry-rules-setup-taurus/
- 사이드바 위치: Applications > Foundry Rules > Legacy Foundry Rules setup (Taurus) > Overview

이 페이지는 2022년 7월 이전에 배포된 Foundry Rules(이전 이름 Taurus)가 현재 버전과 어떻게 다른지 설명합니다. 예전에는 트랜스폼 파이프라인을 직접 관리해야 했고, 입력과 출력을 여러 곳에서 따로 구성해야 했으며, 출력 스키마를 액션으로 강제했다는 점이 핵심 차이입니다.

**주의**: 2022년 7월 이전의 Foundry Rules(이전 이름 Taurus)는 추가 구성이 필요했고 조금 다른 개념을 사용했습니다. 다음 문서는 이 버전과 최신 버전의 Foundry Rules 사이의 차이를 다룹니다.

<a id="transforms-pipeline"></a>
## 트랜스폼 파이프라인 (Transforms pipeline)

예전에는 Foundry Rules가 **트랜스폼 파이프라인**을 자동으로 생성하는 대신, 사용자가 규칙을 실행하는 [Code Repository](https://www.palantir.com/docs/foundry/code-repositories/overview/)를 직접 만들고 유지 관리해야 했습니다.

이 저장소를 만들고 [업데이트하는 방법](04_configure-transforms-pipeline.md)에 대해 더 알아보세요.

<a id="workshop-application"></a>
## Workshop 애플리케이션 (Workshop application)

예전에는 [규칙 입력](../02_core-concepts/04_rule-logic.md#inputs)을 [워크플로 구성 편집기(Workflow Configuration Editor)](../02_core-concepts/05_foundry-rules-workflow-configuration.md)에서 구성하는 대신, Workshop 애플리케이션과 트랜스폼 파이프라인 양쪽에서 모두 구성해야 했습니다.

또한 규칙 출력은 Workshop 애플리케이션, 트랜스폼 파이프라인, [Ontology Manager](../../04_ontology-manager/01_overview.md)의 세 곳에서 구성했습니다. 레거시 규칙 출력에 대해서는 아래 [규칙 액션](#rule-actions) 섹션에서 더 알아보세요.

[Workshop 애플리케이션](03_configure-workshop-app.md)과 [트랜스폼 파이프라인](04_configure-transforms-pipeline.md)에서 규칙 입력을 추가하고 제거하는 방법을 더 알아보세요.

<a id="rule-actions"></a>
## 규칙 액션 (Rule Actions)

[워크플로 출력](../02_core-concepts/05_foundry-rules-workflow-configuration.md#workflow-outputs)이 생기기 전에는 출력 스키마 강제를 Foundry 액션(Action)으로 구현했습니다. 액션의 파라미터는 데이터셋 열을 나타내며, 로직이 출력한 열이나 사용자가 입력한 정적 값 중 하나에 매핑되어야 합니다. 규칙 액션은 [트랜스폼 안에서](04_configure-transforms-pipeline.md#rule-action-datasets) 접근해 일치하는 모든 행을 지정된 형식으로 가져올 수 있습니다. 지정한 규칙 액션의 결과를 가져오면, *생성되는 데이터셋에는 그 액션을 사용하는 모든 규칙이 출력한 행이 들어갑니다*. 이는 모든 Foundry 규칙의 출력을 일관되게 유지하기 쉽도록 설계된 것입니다. 규칙 액션은 Foundry 액션이므로 Ontology Manager에서 구성해야 합니다. 하지만 이 규칙 액션은 관련 객체 위에서 직접 실행되지 않으며, 현재 유일한 효과는 출력 스키마를 지정하는 것입니다.

[규칙 액션 구성](05_configure-rule-actions.md)에 대해 더 알아보세요.

2021년 1월 이전에 배포된 일부 레거시 버전의 Foundry Rules(이전 이름 Taurus)는 규칙 액션을 사용하기 전에 업그레이드가 필요합니다. 특별히 지시받지 않았다면 이 작업은 아마 필요 없을 것입니다. [규칙 액션을 사용하도록 업그레이드하기](07_upgrade-to-use-rule-actions.md)에 대해 더 알아보세요.

**설명**: 규칙 액션이 "실행되지 않는 액션"이라는 점이 특이합니다. 보통 액션 타입은 객체를 생성하거나 수정하는 작업을 정의하지만, 레거시 Foundry Rules는 액션 타입의 파라미터 목록을 출력 테이블의 스키마 정의로 재활용했습니다. 예를 들어 파라미터가 `alert_id: String`, `severity: String`인 규칙 액션은 "출력 테이블은 이 두 열을 가진다"는 선언으로만 쓰였습니다. 현재 버전에서는 이 역할을 워크플로 출력이 맡습니다.

## 정리

- 2022년 7월 이전의 Foundry Rules(Taurus)는 현재 버전보다 구성이 많고 개념이 조금 다릅니다.
- 레거시에서는 규칙 실행용 Code Repository를 사용자가 직접 만들고 관리해야 했습니다.
- 규칙 입력은 Workshop과 트랜스폼 파이프라인 양쪽에서, 규칙 출력은 Workshop, 트랜스폼, Ontology Manager의 세 곳에서 구성했습니다.
- 출력 스키마는 규칙 액션의 파라미터로 강제했으며, 규칙 액션은 객체에 실행되지 않고 스키마만 정의했습니다.
- 2021년 1월 이전 배포본은 규칙 액션을 쓰려면 업그레이드가 필요할 수 있습니다.
