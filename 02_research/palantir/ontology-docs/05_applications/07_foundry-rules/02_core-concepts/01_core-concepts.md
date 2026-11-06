# Foundry Rules 핵심 개념 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/core-concepts/
- 사이드바 위치: Applications > Foundry Rules > Core concepts > Overview

이 페이지는 Foundry Rules를 이해하는 데 필요한 네 가지 기본 개념(객체 모델, Workshop 애플리케이션, 규칙 로직, 워크플로 구성)을 나열하고 각 상세 페이지로 안내하는 목차 성격의 페이지입니다. 규칙이 온톨로지의 객체로 저장되고, Workshop 앱에서 편집과 검토를 거친다는 전체 구조를 먼저 잡아 두는 데 쓰입니다.

Foundry Rules의 근간이 되는 개념은 다음과 같습니다.

* **[객체 모델(Object model)](02_object-model.md):** Foundry 규칙은 **속성(property)을** 가진 **객체이며**, **규칙 제안(rule proposal)을** 통해 관리할 수 있습니다.
* **[Workshop 애플리케이션(Workshop application)](03_workshop-application.md):** Foundry 규칙은 **Workshop 애플리케이션으로** 관리되며, 이 애플리케이션에는 보통 **Rule Editor**(규칙 편집기)와 **Proposal Reviewer**(제안 검토기) 기능이 들어 있습니다.
* **[규칙 로직(Rule logic)](04_rule-logic.md):** Foundry 규칙은 [특정 워크플로](../01_overview.md#example-use-cases)를 수행하도록 설계된 비즈니스 로직을 담습니다. 이 로직은 정해진 구조를 따르며, 데이터에 대한 일련의 변환(transformation)을 정의합니다.
* **[Foundry Rules 워크플로 구성(Foundry Rules workflow configuration)](05_foundry-rules-workflow-configuration.md):** Foundry 규칙은 워크플로 구성 편집기(workflow configuration editor)로 구성합니다. 이 편집기는 워크플로 소유자가 Foundry Rules를 자신의 사용 사례에 맞게 사용자 정의할 때 쓰는 인터페이스입니다. <br><br>
  ![Foundry Rules 워크플로 개요 목록](https://www.palantir.com/docs/resources/foundry/foundry-rules/overview@2x.png) <br><br>

**주의**: 2022년 7월 이전의 Foundry Rules에는 추가 개념이 있었고 더 많은 구성이 필요했습니다. 그 이전에 Foundry Rules를 배포했다면 이 [추가 개념과 구성](../06_legacy-foundry-rules-setup-taurus/01_legacy-foundry-rules-setup-taurus.md)에 대해 알아보세요.

**설명**: 규칙 자체가 "객체"라는 점이 핵심입니다. 즉 규칙 하나하나가 온톨로지 객체 타입(예: Rule)의 한 행으로 저장되고, 규칙 이름, 조건 로직 같은 정보가 속성으로 들어갑니다. 사용자가 규칙을 바로 고치는 대신 "제안(proposal)"을 만들고 다른 사람이 검토해 승인하는 흐름은, 코드 저장소에서 바로 커밋하지 않고 풀 리퀘스트를 올려 리뷰를 받는 절차와 같은 구조입니다.

## 정리

- Foundry Rules의 기본 개념은 객체 모델, Workshop 애플리케이션, 규칙 로직, 워크플로 구성의 네 가지입니다.
- 규칙은 속성을 가진 온톨로지 객체이며, 규칙 제안을 통해 변경됩니다.
- 규칙은 Rule Editor와 Proposal Reviewer를 갖춘 Workshop 애플리케이션에서 관리합니다.
- 규칙 로직은 데이터에 대한 변환을 정의하고, 워크플로 소유자는 워크플로 구성 편집기로 전체 설정을 맞춥니다.
- 2022년 7월 이전 배포본은 레거시(Taurus) 설정 문서를 따로 참고해야 합니다.
