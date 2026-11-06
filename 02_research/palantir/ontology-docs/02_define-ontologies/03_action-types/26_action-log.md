# 액션 로그 (Action log)

- 원문: https://www.palantir.com/docs/foundry/action-types/action-log/
- 사이드바 위치: Define Ontologies > Action types > Action log

이 페이지는 성공한 액션 제출 한 건 한 건을 객체로 기록하는 액션 로그(action log)를 설명합니다. "누가, 언제, 어떤 맥락에서 어떤 결정을 내렸는가"를 온톨로지 안의 데이터로 남겨 감사(audit)하고 분석하기 위한 기능입니다. 다른 변경 추적 기능과의 차이, 설정 위치, 로그 객체의 스키마와 타임스탬프, 제한 사항, 문제 해결 방법을 다룹니다.

액션 로그는 성공한 액션 제출을 객체 타입으로 모델링해서, 객체를 다룰 줄 아는 Foundry 도구에서 분석하고 표시할 수 있게 합니다. 액션 로그 객체 타입을 의사 결정 워크플로의 입력으로 사용하고, 온톨로지에 대한 변경을 모니터링하는 데 활용하세요.

**참고**: 액션 로그는 액션 제출로 내려진 결정을 기록하고 그 결정을 온톨로지 안의 데이터로 쓸 수 있게 하도록 설계되었습니다. 객체에 대한 모든 편집을 기록하고 싶은 경우에는 객체 타입에 [편집 기록(edit history)](../../06_ontology-architecture/04_object-edits-and-materializations/03_user-edit-history.md)을 활성화할 수 있습니다.

<a id="background"></a>
## 배경 (Background)

액션은 온톨로지를 수정하고 관련 부수 효과를 일으키는 주된 방법입니다. 이런 온톨로지 수정은 대개 특정 결정의 결과이거나 데이터 감사 요구 사항을 동반합니다. 액션 로그는 이런 결정과 데이터 편집을 나타내는 객체 타입을 만들고 유지하는 일을 단순화합니다. 쉽게 알아볼 수 있도록, 생성된 액션 로그 객체 타입은 `[Log] <액션 타입 이름>`이라는 표시 이름과 `[Logs] <액션 타입 이름>`이라는 복수형 표시 이름을 갖습니다.

**설명**: 핵심은 로그 자체가 "객체 타입"이라는 점입니다. 일반적인 애플리케이션 로그는 텍스트 파일이나 별도 로그 테이블에 쌓이지만, 액션 로그는 온톨로지의 객체로 저장되므로 다른 객체처럼 검색, 필터, 집계, 링크 탐색을 할 수 있습니다. 예를 들어 `Approve Loan` 액션 타입에 액션 로그를 켜면 `[Log] Approve Loan` 객체 타입이 생기고, 대출 승인이 한 번 일어날 때마다 그 객체가 하나씩 생깁니다.

<a id="when-to-use-the-action-log"></a>
## 액션 로그를 언제 사용하는가 (When to use the action log)

Foundry는 변경에 관한 질문에 답하는 여러 기능을 제공하며, 이들은 서로 대체할 수 없습니다. 다음 표를 보고 어느 기능을 쓸지 고르세요.

| 답해야 하는 질문 | 사용할 기능 |
|--- |--- |
| 어떤 결정이, 누구에 의해, 언제, 어떤 맥락에서 내려졌는가? | **액션 로그(Action log)** |
| 편집이 어떤 방식으로 이루어졌든 관계없이, 이 객체에 대한 모든 편집의 전체 이력은 무엇인가? | [편집 기록(Edit history)](../../06_ontology-architecture/04_object-edits-and-materializations/03_user-edit-history.md) |
| 이 액션은 얼마나 자주 성공하거나 실패하며, 얼마나 오래 걸리는가? | [액션 지표(Action metrics)](25_action-metrics.md) |
| 액션이 적용한 편집을 어떻게 취소하는가? | [액션 실행 취소 또는 되돌리기](23_action-reverts.md) |
| 액션이 실패하기 시작하면 어떻게 알림을 받는가? | [모니터링(Monitoring)](22_monitoring.md) |

이 역할 분담에서 비롯되는 두 가지 결과를 분명히 짚어 둘 필요가 있습니다.

* 액션 로그는 **성공한** 액션 제출만 기록합니다. 실패는 기록하지 않습니다. 실패는 [액션 지표](25_action-metrics.md#action-failure-types)가 추적합니다.
* 액션 로그는 **액션 타입을 통해** 이루어진 편집을 기록합니다. 백킹 데이터소스에 직접 쓰는 것이나 레거시 Foundry Forms 라이트백(writeback)처럼 액션 타입 밖에서 적용된 편집은 액션 로그 객체를 만들지 않습니다. 구분 기준은 클라이언트가 아니라 경로입니다. API나 SDK를 통해 적용한 액션 타입도 사용자 인터페이스에서와 똑같이 액션 로그 객체를 만들며, Object Explorer의 [인라인 편집](18_inline-edits.md)도 액션 기반이므로 기록됩니다. 경로와 관계없이 모든 편집을 다뤄야 한다면 [편집이 적용되는 방식](../../06_ontology-architecture/04_object-edits-and-materializations/02_how-edits-applied.md)을 검토하세요.

**설명**: "경로"와 "클라이언트"의 구분을 예로 들면, 같은 `Update Status` 액션 타입을 Workshop 버튼으로 실행하든 Python OSDK 스크립트로 실행하든 둘 다 액션 타입이라는 경로를 거치므로 로그가 남습니다. 반대로 누군가 백킹 데이터셋 자체를 파이프라인으로 고쳐서 객체 값이 바뀌었다면, 액션 타입을 거치지 않았으므로 로그가 남지 않습니다.

> **중간 요약**: 액션 로그는 "결정"을 기록하는 기능으로, 액션 타입을 통한 성공한 제출만 기록합니다. 모든 편집 이력은 편집 기록, 실패와 성능은 액션 지표, 취소는 되돌리기, 알림은 모니터링이 담당합니다.

<a id="where-to-configure-the-action-log"></a>
## 액션 로그를 설정하는 위치 (Where to configure the action log)

액션 로그는 [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)의 서로 독립된 두 곳에서 설정합니다.

**단일 액션 타입에 대해 액션 로그 객체를 생성하려면:** 액션 타입을 열고 **Capabilities** 탭을 선택합니다. **Create action log objects** 섹션을 찾습니다. 인터페이스에서는 이 섹션을 *Generate an object every time this action is triggered successfully*(이 액션이 성공적으로 실행될 때마다 객체 생성)라고 설명합니다. 토글을 켠 다음 **Generate object type**을 선택해 액션 로그를 뒷받침할 객체 타입을 만듭니다.

**특정 객체 타입을 편집하는 모든 액션에 액션 로그를 요구하려면:** 객체 타입을 열고 **Datasources** 탭을 선택한 다음, **Edits** 섹션에서 **Only allow Action types with action logs**를 켭니다. 인터페이스에서는 그 효과를 *All actions that edit objects of this type will need an action log in order to function.*(이 타입의 객체를 편집하는 모든 액션은 동작하려면 액션 로그가 있어야 합니다)이라고 설명합니다.

**주의**: 액션 로그 요구 토글은 편집이 활성화되기 전까지 숨겨져 있음(The action log requirement toggle is hidden until edits are enabled). **Only allow Action types with action logs**는 객체 타입에 이미 편집이 활성화되어 있을 때만 나타납니다. 토글을 찾을 수 없다면, 먼저 객체 타입에서 **Allow edits**를 켜고 변경 사항을 저장한 뒤 **Datasources** 탭으로 돌아오세요. 편집을 활성화하는 방법은 [사용자가 객체와 링크를 편집하도록 허용하기](../02_object-and-link-types/07_allow-editing.md)를 검토하세요. **Allow edits**를 다시 끄면 이 설정도 해제됩니다.

> **중간 요약**: 액션 타입 쪽에서는 Capabilities 탭의 Create action log objects로 로그를 켜고, 객체 타입 쪽에서는 Datasources 탭의 Only allow Action types with action logs로 "로그가 있는 액션만 편집 허용"을 강제할 수 있습니다.

<a id="action-log-ontology"></a>
## 액션 로그 온톨로지 (Action log Ontology)

액션 로그 객체 타입은 액션 타입과 일대일로 대응합니다. 액션을 제출하면 대응하는 액션 로그 객체 타입의 새 객체가 하나 생깁니다. 새로 만들어진 이 객체는 제출된 액션이 편집한 모든 객체와 자동으로 링크됩니다. 로그 객체 타입을 액션 타입과 일대일로 모델링하기 때문에, 액션 로그는 특정 객체 편집을 넘어서는 맥락, 예를 들어 어떤 다른 객체가 함께 편집되었는지, 그리고 액션 제출 시점의 세계 상태(온톨로지가 표현하는 상태)까지 담을 수 있습니다.

예를 들어 선택한 여러 `Alert` 객체의 "Status" 속성을 "Closed"로 바꾸는 `Close Alerts` 액션 타입을 생각해 봅시다. 액션 로그가 설정되어 있으면, `Alert` 객체 10개를 한 번에 닫았을 때 10개의 `Alert` 객체 모두에 대한 외래 키 링크를 가진 `action log` 객체가 하나 생깁니다.

**참고**: 액션 로그 기반 액션 타입을 적용하려면, 사용자는 액션 타입이 규칙과 함수를 통해 생성하거나 수정할 수 있는 다른 객체 타입과 마찬가지로 액션 로그 객체 타입에 대한 적절한 권한이 필요합니다. 액션 타입 권한 모델 전체는 [권한](19_permissions.md)을 검토하세요.

**설명**: `Close Alerts` 예를 테이블로 보면 다음과 같습니다. 로그 객체 타입 `[Log] Close Alerts`에 행 하나가 생깁니다.

| action_rid | current_user | current_timestamp | edited_objects |
|---|---|---|---|
| ri.actions.main.action.abc | user-123 | 2025-03-01T09:00:05Z | A1, A2, ..., A10 |

그리고 이 로그 객체와 `Alert` A1\~A10 사이에 링크 10개가 생깁니다. 객체 하나당 로그 하나가 아니라 "제출 한 번당 로그 하나"이므로, 한 번의 결정으로 함께 처리된 객체들이 무엇이었는지 알 수 있습니다. 표의 값은 이해를 돕기 위한 가상의 예시입니다.

<a id="action-log-schema"></a>
### 액션 로그 스키마 (Action log schema)

**Create action log objects** 섹션은 기록할 수 있는 값을 **Values to log** 아래에 **Required values**(필수 값)와 **Optional values**(선택 값)로 나누어 보여 줍니다. **Required values** 그룹의 값은 설정에서 제거할 수 없습니다. 액션 로그 요약(summary)은 **Values to log** 위의 **Summary** 섹션에서 따로 설정합니다.

**Required values**에는 다음이 포함됩니다.

* **Action RID:** 액션 제출 한 건의 고유 식별자
* **Action type RID:** 액션 타입 하나의 고유 식별자
* **Action type version:** 액션 타입이 업데이트될 때마다 자동으로 증가하는 버전 번호
* **Current timestamp:** 액션의 UTC 타임스탬프. Object Storage v2에서는 [커밋 타임스탬프](#action-log-timestamps)입니다.
* **Current user:** 제출한 사용자의 Multipass 사용자 ID
* **Edited objects:** 액션이 편집한 모든 객체의 기본 키(primary key) 값. 편집된 객체의 기본 키 이외의 속성을 저장하는 것은 지원되지 않습니다.

**Required values** 그룹에는 부수 효과와 되돌리기에 대한 출처(provenance) 정보도 포함되며, 편집이 왜 일어났는지 감사할 때 유용합니다.

* 액션이 호출한 웹훅의 식별자(동기 및 비동기 모두)
* 액션이 보낸 알림의 식별자와 알림을 받은 사용자
* 액션이 적용된 [시나리오](../../04_ontology-scenarios/01_overview-ontology-scenario.md)의 RID(있는 경우)
* 액션이 되돌려졌는지 여부와, 되돌린 사용자 및 타임스탬프

**Optional values**에는 다음이 포함됩니다.

* **Parameter values**(파라미터 값)
* **Property values of object reference parameters**(객체 참조 파라미터의 속성 값). 객체 참조 파라미터에 `allow multiple values`가 활성화되어 있으면 지원되지 않습니다.

액션 로그 객체 타입은 액션이 편집하지 않는 객체 속성도 저장하도록 설정할 수 있습니다. 이를 통해 데이터 편집뿐 아니라 온톨로지 편집의 맥락이나 동기에 관한 관련 정보도 저장할 수 있습니다.

`Close Alerts` 액션 타입 예로 돌아가서, `Alert` 객체에 "High Priority"와 "Low Priority" 값을 가지는 "Priority" 속성과 "Created at" 타임스탬프, "Source" 장비 속성도 있다고 합시다. `Close Alerts`가 이 속성들을 편집하지 않더라도 액션 로그는 이 속성들을 저장할 수 있습니다. 해당 열을 편집하지 않고도 "Priority"로 집계하면 "대부분의 'High Priority' 알림은 어디서 발생하는가?"나 "'High Priority' 알림을 닫는 데 얼마나 걸리는가?" 같은 질문에 답할 수 있습니다.

**설명**: 이런 맥락 값을 로그에 함께 저장하는 이유는, 객체의 현재 값은 나중에 바뀔 수 있기 때문입니다. 알림을 닫은 뒤 누군가 그 알림의 Priority를 바꾸더라도, 로그 객체에는 "닫을 당시의 Priority"가 그대로 남아 있으므로 결정 시점의 상황을 정확히 재현할 수 있습니다.

<a id="summary"></a>
#### 요약 (Summary)

**Values to log** 위의 **Summary** 섹션에는 액션을 설명하는, 사용자가 정의할 수 있는 문자열이 들어갑니다. 인터페이스에서는 이를 *Add a human readable summary of what happened. You can reference parameters by hitting `/`*(무슨 일이 있었는지 사람이 읽을 수 있는 요약을 추가하세요. `/`를 눌러 파라미터를 참조할 수 있습니다)라고 설명합니다.

> **중간 요약**: 액션 로그 객체 타입은 액션 타입과 일대일이며, 제출 한 번마다 로그 객체 하나가 생겨 편집된 모든 객체와 링크됩니다. 필수 값(RID, 버전, 시각, 사용자, 편집된 객체, 부수 효과와 되돌리기 출처)과 선택 값(파라미터 값, 객체 참조 파라미터의 속성 값), 사람이 읽을 요약을 기록할 수 있습니다.

<a id="action-log-timestamps"></a>
### 액션 로그 타임스탬프 (Action log timestamps)

Object Storage v2에 쓰는 액션의 경우, 액션 로그와 [편집 기록](../../06_ontology-architecture/04_object-edits-and-materializations/03_user-edit-history.md#edit-history-timestamps)은 같은 커밋 타임스탬프를 사용합니다. 액션은 편집을 저장소에 제출할 준비를 할 때 이 UTC 타임스탬프를 기록합니다. 이 타임스탬프가 편집이 쿼리에서 보이기 시작하는 정확한 시각을 뜻하지는 않습니다.

[액션 규칙](06_rules.md#values-and-parameters)에서 **Current User/Time**이 제공하는 타임스탬프는 액션 실행이 시작된 시각을 나타내며, 실행 내내 고정됩니다. 따라서 이 규칙으로 설정된 타임스탬프 속성은 액션 로그 타임스탬프보다 이른 값을 가질 수 있습니다.

예를 들어 액션이 12:00:00 UTC에 시작하고 12:00:05 UTC에 편집을 제출할 준비를 한다고 합시다. 규칙 값은 12:00:00 UTC입니다. 액션 로그와 편집 기록은 12:00:05 UTC를 사용합니다.

액션을 되돌려도 액션 로그 타임스탬프는 유지됩니다. 액션 로그는 되돌린 시각을 따로 기록합니다.

**설명**: 정리하면 하나의 액션 실행에 시각이 세 종류 있을 수 있습니다. (1) 실행 시작 시각(규칙의 Current Time 값), (2) 커밋 준비 시각(액션 로그와 편집 기록의 타임스탬프), (3) 실제로 쿼리에 보이기 시작하는 시각입니다. 감사 목적으로 시간 순서를 비교할 때는 어떤 시각을 기준으로 삼는지 맞춰야 합니다.

<a id="limits-and-constraints"></a>
### 한도와 제약 (Limits and constraints)

액션 로그를 중심으로 워크플로를 설계하기 전에 다음 제약을 검토하세요.

| 제약 | 세부 내용 |
|--- |--- |
| 속성 타입은 생성 후 고정됨 | 액션 로그 속성의 타입은 속성을 만든 뒤에는 바꿀 수 없습니다. 로그가 매핑하는 원본 속성의 타입이 나중에 바뀌면, 액션 타입이 검증에 실패합니다. 복구하려면 새 타입으로 새 액션 로그 속성을 만들고 매핑이 그 속성을 참조하도록 업데이트하세요. |
| 요약 길이 | 액션 로그 요약은 최대 20개 부분(part)을 받습니다. 리터럴 텍스트 부분 하나는 최대 50자까지 받습니다. 이 길이 제한은 파라미터 부분에는 적용되지 않습니다. |
| 요약 내용 | 액션 로그 요약은 객체 타입 파라미터를 참조할 수 없습니다. |
| 객체 참조 파라미터 | 단일 값 객체 참조 파라미터만 로그에 속성 값을 넣을 수 있습니다. `allow multiple values`가 활성화된 파라미터는 넣을 수 없습니다. |
| 미디어 참조 파라미터 | 미디어 참조를 사용하는 파라미터는 액션 로그에서 제외됩니다. |
| 소급 생성 없음 | 액션 로그를 활성화해도 이미 제출된 액션에 대한 로그 객체는 만들어지지 않습니다. 기록은 설정을 저장한 시점부터 시작됩니다. |
| 편집 한도 | 액션 로그 객체는 다른 객체 편집과 같은 [규모 및 속성 한도](17_scale-property-limits.md#edit-limits)를 따릅니다. |

**설명**: 요약의 "부분(part)"은 요약 문자열을 이루는 조각입니다. 예를 들어 "알림 `{alert}`을 `{status}`로 변경" 같은 요약은 리터럴 텍스트 부분("알림 ", "을 ", "로 변경")과 파라미터 부분(`{alert}`, `{status}`)이 번갈아 이어진 구조입니다. 이 조각의 총수가 20개 이하, 리터럴 조각 하나가 50자 이하여야 합니다.

> **중간 요약**: 액션 로그 타임스탬프는 커밋 준비 시각이며 규칙의 Current Time(실행 시작 시각)보다 늦을 수 있습니다. 로그 속성 타입은 바꿀 수 없고, 요약 길이 제한이 있으며, 소급 생성이 되지 않는다는 점 등을 설계 전에 확인해야 합니다.

<a id="action-log-on-function-backed-action-types"></a>
## 함수 기반 액션 타입의 액션 로그 (Action log on function-backed action types)

함수 기반 액션 타입에 액션 로그를 설정하려면, 백킹 온톨로지 편집 함수에 `Edits` 출처(provenance)가 설정되어 있어야 합니다. `Edits` 출처에 대한 자세한 내용은 [함수 문서](../04_functions/09_language-agnostic-features/01_edits-overview.md)를 참고하세요.

**설명**: `Edits` 출처는 함수가 어떤 객체 타입을 편집하는지를 함수 정의에 명시하는 선언입니다(TypeScript에서는 데코레이터 형태로 씁니다). 플랫폼은 이 선언을 보고 함수 기반 액션이 어떤 객체를 편집할지 미리 알 수 있으므로, 액션 로그 객체와 편집된 객체 사이의 링크를 구성할 수 있습니다.

<a id="action-log-timeline"></a>
## 액션 로그 타임라인 (Action log timeline)

Workshop의 [Action Log Timeline](https://www.palantir.com/docs/foundry/workshop/widgets-action-log-timeline/) 위젯을 사용하면 액션 로그 객체 타입을 타임라인으로 볼 수 있습니다. 타임라인을 설정해 데이터 감사를 지원하고 "무엇이, 누구에 의해, 언제 바뀌었는가?"라는 질문에 답하세요.

Workshop 안에서는 액션 로그 객체 타입들을 합집합(union)으로 묶어, 하나의 유스 케이스 안이나 온톨로지 전체에 걸친 편집을 종합적으로 볼 수 있습니다.

액션 로그 타임라인을 설정하려면 편집된 객체 타입을 선택합니다. 그런 다음 표시할 액션 로그 객체 타입과 원하는 액션 로그 객체 타입 속성을 고릅니다.

[Comments](https://www.palantir.com/docs/foundry/workshop/widgets-comments/#action-log) 위젯을 사용하면 액션 로그를 객체 댓글과 함께 하나의 피드로 표시할 수도 있습니다.

> **중간 요약**: 함수 기반 액션에 로그를 켜려면 함수에 `Edits` 출처가 필요합니다. 기록된 로그는 Workshop의 Action Log Timeline 위젯이나 Comments 위젯으로 시간순으로 볼 수 있습니다.

<a id="troubleshooting"></a>
## 문제 해결 (Troubleshooting)

다음은 액션 로그가 잘못 설정되었을 때 플랫폼이 표시하는 메시지입니다.

| 메시지 | 의미와 해결 방법 |
|--- |--- |
| `Action Log required but not enabled` | 액션 타입에 액션 로그가 없는데, 그 액션 타입이 편집하는 객체 타입이 액션 로그를 요구합니다. 액션 타입의 **Capabilities** 탭에서 **Create action log objects**를 켜세요. |
| `Associated object type is missing. Logs are not being recorded.` | 이 설정을 뒷받침하던 액션 로그 객체 타입이 더 이상 존재하지 않아 로그가 기록되지 않고 있습니다. **Generate object type**을 선택해 새로 만드세요. |
| `Action log has no writeback dataset defined` | 액션 로그 객체 타입에 라이트백 데이터셋이 없어 로그 객체를 저장할 수 없습니다. 액션 로그 객체 타입의 **Writeback datasource**를 설정하세요. |
| `This property will not be used for logging until indexing is complete.` | 새로 추가한 액션 로그 속성이 인덱싱을 기다리고 있습니다. 인덱싱이 끝나면 그 속성에 대한 기록이 시작됩니다. |
| `Function has no Edits Decorator` | 액션 타입을 뒷받침하는 함수가 액션 로그에 필요한 `Edits` 출처를 선언하지 않았습니다. [함수 문서](../04_functions/09_language-agnostic-features/01_edits-overview.md)를 검토하세요. |

일부 플랫폼 메시지는 *액션 로그 규칙(action log rule)* 을 언급합니다. 이는 액션 타입의 **Capabilities** 탭에 있는 **Create action log objects** 섹션과 같은 설정입니다.

<a id="next-steps"></a>
## 다음 단계 (Next steps)

* [Action Log Timeline 위젯으로 액션 로그를 타임라인에 표시하기.](https://www.palantir.com/docs/foundry/workshop/widgets-action-log-timeline/)
* [액션 지표로 액션의 성공, 실패, 소요 시간 모니터링하기.](25_action-metrics.md)
* [편집 기록으로 객체에 대한 모든 편집 추적하기.](../../06_ontology-architecture/04_object-edits-and-materializations/03_user-edit-history.md)
* [액션 타입 권한 모델 검토하기.](19_permissions.md)

## 정리

- 액션 로그는 액션 타입을 통한 성공한 제출 한 건마다 로그 객체 하나를 만들어, 결정의 주체, 시각, 맥락을 온톨로지 데이터로 남깁니다.
- 실패는 액션 지표, 모든 편집 이력은 편집 기록이 담당하며, 액션 타입을 거치지 않은 편집은 로그에 남지 않습니다.
- 액션 타입의 Capabilities 탭에서 로그를 켜고, 객체 타입의 Datasources 탭에서 로그가 있는 액션만 편집하도록 강제할 수 있습니다.
- 로그 객체에는 필수 값, 선택 값, 편집하지 않은 맥락 속성, 요약을 담을 수 있으며 타임스탬프는 커밋 준비 시각입니다.
- 함수 기반 액션은 `Edits` 출처가 필요하고, 로그는 Workshop 타임라인과 댓글 위젯으로 볼 수 있습니다.
