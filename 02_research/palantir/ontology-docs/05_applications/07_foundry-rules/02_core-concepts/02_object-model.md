# 객체 모델 (Object model)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/object-model/
- 사이드바 위치: Applications > Foundry Rules > Core concepts > Object model

이 페이지는 Foundry Rules가 온톨로지(Ontology) 안에서 어떤 객체로 표현되는지 설명합니다. Foundry Rules에서 규칙(rule)과 규칙 변경 제안(proposal)은 모두 일반 객체이므로, 그 객체가 어떤 속성(property)을 갖는지 알면 규칙이 어떻게 저장되고 검토되는지 이해할 수 있습니다.

Foundry Rules와 관련된 주요 객체 모델 개념은 두 가지입니다.

* 데이터에 적용되는 [규칙(Rules)](#rules)
* 규칙을 변경하는 수단을 제공하는 [제안(Proposals)](#proposals)

<a id="rules"></a>
### 규칙 (Rules)

규칙은 다음으로 구성된 표준 객체입니다.

* 이름, 설명, 작성자, 규칙 유형 등 *규칙 메타데이터 속성*의 모음
* 필터링된 데이터셋에 적용되거나 트랜스폼(transform)에 전달되는 *사용자 정의 속성(custom property)* 의 모음
  * "알림(alerting)" 패턴이라면 `alert_severity`, `alert_assignee`, `priority` 같은 속성이 될 수 있습니다.
  * "분류(categorization)" 패턴이라면 `group`, `sub-group` 같은 속성이 될 수 있습니다.
* 해당 규칙의 일치 조건(match condition)을 담는 *로직 속성(logic property)*
  * 로직은 일관된 직렬화를 위해 특정 문법을 따르는 압축된 JSON blob으로 저장됩니다.

![규칙 이름 같은 메타데이터 입력 필드, 의심 수준 같은 워크플로별 입력 필드, 그리고 객체 속성에 대한 간단한 필터를 보여 주는 로직](https://www.palantir.com/docs/resources/foundry/foundry-rules/example_rule.png)

여러분의 워크플로에 맞게 [속성을 사용자 정의하는 방법](../04_settings-customization/03_add-a-custom-property.md)을 알아보세요.

**설명**: 규칙 하나가 객체 하나라는 점이 핵심입니다. 예를 들어 Rule 객체 타입을 테이블로 보면 행 하나가 규칙 하나이고, 열은 `rule_name`, `author`, `alert_severity`, `logic` 등이 됩니다. `logic` 열에는 "Transaction.amount > 10000" 같은 조건이 사람이 읽는 문장이 아니라 정해진 문법의 JSON을 압축한 값으로 들어 있습니다. 직렬화(serialization)는 메모리 속 구조를 저장 가능한 문자열이나 바이트로 바꾸는 것을 말하며, 문법이 고정되어 있어야 나중에 파이프라인이 이 값을 다시 읽어 실제 필터로 실행할 수 있습니다.

<a id="proposals"></a>
### 제안 (Proposals)

규칙 관리 사용 사례 상당수에는 규칙의 생성, 편집(edit), 삭제를 통제하는 감사(audit) 및 검토 절차에 대한 요구 사항이 따라옵니다. 이런 요구를 충족하기 위해 Foundry Rules는 규칙 변경을 제출하고, 검토하고, 모니터링하는 방법으로 **규칙 제안(rule proposal)을** 지원합니다. 규칙 제안은 소프트웨어 개발의 ["풀 리퀘스트(pull request)" ↗](https://en.wikipedia.org/wiki/Distributed_version_control#Pull_requests) 개념에 해당하며, 따라서 하나의 규칙에 동시에 여러 개의 제안이 있을 수 있습니다.

제안은 Foundry Rules의 기능 중 하나일 뿐 필수 요소는 아닙니다. Foundry Rules는 이 승인 흐름을 만들 때 표준 객체와 액션(Action)을 사용하므로, 규칙 변경 관리에 대한 운영상 또는 규제상 요구 사항에 맞게 워크플로를 원하는 대로 사용자 정의할 수 있습니다.

제안은 다음을 담은 객체로 표현됩니다.

* 편집, 생성, 삭제할 대상의 *규칙 ID*
* 제안 작성자, 타임스탬프, 상태(open, approved, rejected), 검토자 같은 *제안 메타데이터*
* 제안에 담긴 *변경 사항의 diff*(즉 변경 목록). `old_rule_name`, `new_rule_name`, `old_logic`, `new_logic` 같은 속성에 기록됩니다.

![메타데이터 필드와 규칙 로직의 변경 사항을 보여 주는 diff](https://www.palantir.com/docs/resources/foundry/foundry-rules/example_proposal.png)

**설명**: 제안 객체는 "변경 전 값"과 "변경 후 값"을 쌍으로 저장합니다. 예를 들어 규칙 R-7의 이름을 "고액 거래"에서 "초고액 거래"로 바꾸는 제안이라면 `rule_id = R-7`, `old_rule_name = 고액 거래`, `new_rule_name = 초고액 거래`, `status = open`인 Proposal 객체가 하나 생깁니다. 검토자가 승인하면 그때 Rule 객체가 실제로 수정됩니다. Git에서 브랜치의 변경이 풀 리퀘스트 승인 후에야 main에 병합되는 흐름과 같은 구조입니다.

## 정리

- Foundry Rules의 핵심 객체는 규칙(Rule)과 제안(Proposal) 두 가지입니다.
- 규칙 객체는 메타데이터 속성, 워크플로별 사용자 정의 속성, 압축 JSON으로 저장된 로직 속성으로 이루어집니다.
- 제안 객체는 대상 규칙 ID, 제안 메타데이터, 변경 전후 값(diff)을 담으며 풀 리퀘스트처럼 검토 후 반영됩니다.
- 제안은 선택 기능이며 표준 객체와 액션으로 구현되므로 조직의 요구에 맞게 바꿀 수 있습니다.
