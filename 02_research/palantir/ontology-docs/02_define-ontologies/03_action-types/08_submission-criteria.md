# 제출 조건 (Submission criteria)

- 원문: https://www.palantir.com/docs/foundry/action-types/submission-criteria/
- 사이드바 위치: Define Ontologies > Action types > Submission criteria

이 페이지는 액션을 제출할 수 있는지 여부를 결정하는 제출 조건(submission criteria)을 설명합니다. 제출 조건은 "누가(사용자), 어떤 데이터에 대해(파라미터), 어떤 맥락에서(실행 컨텍스트)" 액션을 실행할 수 있는지를 논리식으로 정의해, 업무 규칙을 데이터 편집 권한 안에 직접 넣는 장치입니다. 조건, 비교 연산자, 논리 연산자, 실패 메시지를 차례로 다룹니다.

**제출 조건(Submission criteria)은**(이전 명칭은 검증(validations)) 액션을 제출할 수 있는지를 결정하는 조건입니다. 제출 조건은 비즈니스 로직을 데이터 편집 권한에 녹여 넣을 수 있게 하여, 온톨로지 데이터의 품질과 편집 거버넌스를 보장합니다.

제출 조건은 맥락(사용자나 파라미터 등)에 기반한 조건들과 정적 정보를 결합해 하나의 논리식으로 만들어집니다. 제출 조건은 객체, 관계, 그리고 사용자 정보까지 논리식에 포함해 액션 제출 가능 여부를 판단할 수 있습니다.

예를 들어 항공사가 특정 항공편에 배정된 항공기를 바꾸고 싶다고 합시다. 구성된 액션은 사용자가 `Flight` 객체에 링크된 `Aircraft` 객체를 바꿀 수 있게 합니다. 하지만 항공사는 아직 운항 중인 항공기만 사용되도록 하기 위해, 선택된 사용자(예: 운항 관제사)만 이 액션을 사용할 수 있게 하려 합니다. 제출 조건을 사용하면, 빌더는 사용자의 그룹 멤버십과 액션 제출 시점의 항공기 상태를 결합하여, 항공편의 항공기를 바꾸는 액션이 조건을 충족할 때만 제출되도록 보장할 수 있습니다.

![예시: 제출 조건 개요](https://www.palantir.com/docs/resources/foundry/action-types/submission_criteria_overview.png)

제출 조건은 조건(condition)과 연산자(operator)로 구성됩니다. 조건은 파라미터나 사용자 속성의 값을 판단하는 단일 문장입니다. 연산자는 서로 다른 조건을 결합하고 중첩하는 데 사용합니다.

여러 종류의 연산자를 사용하면 비즈니스 프로세스와 요구 사항을 반영한 더 정교한 논리식을 만들 수 있습니다. 액션은 모든 제출 조건이 충족될 때만 제출할 수 있습니다. 이는 사용자가 액션 타입 자체를 편집할 수 있는지를 결정하는 권한과는 별개입니다. 하나의 객체 타입에 객체를 추가, 수정, 삭제하는 액션 타입이 여러 개 있을 수 있지만, 각 액션 타입은 독립적인 제출 조건을 가집니다.

**설명**: 위 항공편 예시를 논리식으로 쓰면 `("Flight Controllers" in 현재사용자.그룹) AND (Aircraft.operating_status == "Yes")`입니다. 데이터베이스의 `CHECK` 제약이나 트리거로 쓰기 연산을 막는 것과 목적이 같지만, 제출 조건은 데이터 값뿐 아니라 "누가 실행하는가"도 조건에 넣을 수 있다는 점이 다릅니다. 또 "액션 타입을 편집할 권한"(설정을 바꿀 수 있는 사람)과 "액션을 제출할 수 있는 조건"(실행할 수 있는 사람과 상황)은 서로 다른 개념입니다.

> **중간 요약**: 제출 조건은 사용자, 파라미터, 실행 맥락에 대한 조건을 연산자로 결합한 논리식이며, 모두 충족될 때만 액션을 제출할 수 있습니다. 액션 타입마다 독립적으로 정의됩니다.

<a id="conditions"></a>
## 조건 (Conditions)

조건은 두 값 사이의 단일 비교 검사입니다. 각 조건은 파라미터나 사용자 입력에 따라 통과하거나 실패합니다. 조건은 세 가지 조건 템플릿 중 하나로 구성할 수 있습니다. "Current user"(현재 사용자), "Parameter"(파라미터), "Execution context"(실행 컨텍스트)입니다. 이 템플릿들은 조건의 나머지 부분에 대한 틀을 제공합니다. 모든 조건은 가운데에 연산자를 두고 두 값을 비교하는 단순한 비교입니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/submission_criteria_select_condition_template.png" alt="예시: 조건 템플릿 선택" width="300" />

예시를 이어 가면, 운항 관제사 요구 사항은 액션을 제출하는 사람의 맥락이 필요하므로 `Current User` 템플릿으로 설정할 수 있습니다. 항공기가 아직 운항 중인지 알려면 `Parameter` 템플릿을 통해 `Aircraft` 객체를 사용해야 합니다.

<a id="current-user"></a>
### 현재 사용자 (Current user)

`Current User` 템플릿은 액션을 제출하는 사용자를 기준으로 권한을 정의합니다. `Current User` 입력으로 사용자의 ID, 그룹 ID를 통한 그룹 멤버십, 또는 사용 가능한 다른 multipass 속성(예: 사용자의 Organization)을 검사할 수 있습니다. Foundry는 사용자 ID를 문자열로 평가하며, 이를 정적으로 정의된 사용자 ID 목록이나 사용자 ID를 저장한 문자열 파라미터와 비교할 수 있습니다.

그룹 ID 옵션을 사용하면 액션 사용자가 속한 그룹(직접 소속이든 상속된 소속이든)을 이용해 조건을 만들 수 있습니다. 그룹은 정적으로 선택한 그룹이나 다른 파라미터가 제공하는 그룹 ID와 비교할 수 있습니다.

Multipass 속성은 문자열 목록으로 취급되며, 다른 문자열이나 문자열 목록과만 비교할 수 있습니다. 사용자에게는 자신이 접근할 수 있는 multipass 속성의 제안 목록이 표시됩니다. `Other user attribute` 필드를 사용하면 사용자가 접근할 수 없는 속성에 대해서도 조건을 구성할 수 있습니다. 사용자가 어떤 속성에 접근할 수 없으면 그 조건은 실패합니다.

**경고**: 그룹, 마킹(marking), 조직 멤버십에 `NOT` 조건을 사용하지 마세요. 이런 상황에서 `NOT` 조건을 쓰는 것은 잘못된 구성입니다. 플랫폼은 사용자 권한의 일부만 담은 범위 제한 토큰(scoped token)을 지원합니다. 이런 토큰에는 `NOT` 조건이 검사하는 속성이 없을 수 있으며, 그러면 조건이 통과되어 의도보다 더 많은 접근을 허용하게 됩니다.

**설명**: multipass는 Foundry의 사용자 인증과 사용자 속성 정보를 가리키는 이름으로 보입니다. `NOT` 조건이 위험한 이유를 예로 들면, "사용자가 `Contractors` 그룹에 속하지 않으면 허용"이라는 조건이 있을 때, 그룹 정보가 빠진 범위 제한 토큰으로 요청하면 시스템은 "그룹 목록에 `Contractors`가 없다"고 판단해 허용합니다. 실제로는 외주 인력인데도 통과하는 것입니다. 그래서 "특정 그룹에 속하면 허용"처럼 긍정형으로 조건을 쓰는 것이 안전합니다. 정보가 빠지면 조건이 실패하는 쪽으로 동작하기 때문입니다.

<a id="parameter"></a>
### 파라미터 (Parameter)

제출 조건은 파라미터 섹션에 정의된 파라미터도 사용할 수 있습니다. 파라미터는 다른 앱이나 사용자 자신으로부터 액션 타입에 전달됩니다. 파라미터에 조건을 걸면 빌더는 비즈니스 로직을 액션 타입에 내장해, 비즈니스 요구 사항에 맞지 않는 데이터에 대해 사용자가 액션을 제출하지 못하게 막을 수 있습니다.

예시에서 운항 상태는 `Aircraft` 객체를 통해 주어지며 항공기마다 다를 수 있습니다. 따라서 조건은 `Aircraft` 객체 타입 파라미터 위에 만들어야 합니다.

<a id="execution-context"></a>
### 실행 컨텍스트 (Execution context)

제출 조건은 액션 제출이 평가되는 실행 컨텍스트, 즉 액션이 [온톨로지 시나리오(Ontology Scenario)](../../04_ontology-scenarios/01_overview-ontology-scenario.md) 안에서 제출되었는지에 따라 정할 수도 있습니다. Scenario 실행 컨텍스트는 액션이 온톨로지 시나리오 안에서 평가되고 있음을 나타냅니다. 특정 시나리오를 식별하지는 않습니다.

예시를 이어 가면, `Aircraft` 객체는 운항 관제사만 바꿀 수 있어야 합니다. 그러나 온톨로지 시나리오 안에서는 운항 관제사가 아닌 계획 담당자도 다른 항공기 배정안을 시험해 보아야 할 수 있습니다.

제출 조건은 다음 중 하나일 때 액션을 허용할 수 있습니다.

* 액션이 시나리오 안에서 실행되고, 현재 사용자가 계획 그룹의 구성원인 경우
* 운항 관제사라는 표준 조건이 충족된 경우

이와 별개로, 시나리오 병합 액션의 제출 조건을 통해 운항 관제사에게 [시나리오 병합](../../04_ontology-scenarios/04_merge-scenario.md#configure-the-merge-action)을 허용할 수 있습니다.

제출 조건은 첨부 파일(attachment) 파라미터와 객체 집합 파라미터를 지원하지 않습니다. 이 파라미터 타입들은 선택 패널에서 제외됩니다.

**설명**: 시나리오는 실제 온톨로지 데이터를 바꾸지 않고 "만약 이렇게 바꾸면?"을 시험해 보는 격리된 작업 공간입니다. 위 예시의 조건을 논리식으로 쓰면 `(실행 컨텍스트 == Scenario AND "Planners" in 현재사용자.그룹) OR ("Flight Controllers" in 현재사용자.그룹)`입니다. 계획 담당자는 시나리오 안에서만 시험적으로 바꿀 수 있고, 그 결과를 실제 데이터에 반영(병합)하는 것은 운항 관제사에게만 허용하는 식으로 역할을 나눌 수 있습니다.

> **중간 요약**: 조건은 현재 사용자(ID, 그룹, multipass 속성), 파라미터, 실행 컨텍스트(시나리오 여부) 세 가지 템플릿으로 만듭니다. 그룹이나 마킹, 조직 멤버십에 `NOT` 조건을 쓰면 범위 제한 토큰 때문에 의도치 않게 통과할 수 있으므로 피해야 합니다.

<a id="select-a-value"></a>
### 값 선택 (Select a value)

조건 템플릿을 선택한 뒤에는 어떤 값을 비교할지 고릅니다. 일부 파라미터(목록이나 객체 파라미터 등)는 비교에 사용할 값을 더 세부적으로 선택해야 합니다. 목록의 내용 대신 목록의 길이를 비교하도록 선택할 수도 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/submission_criteria_select_a_value_left.png" alt="예시: 값 선택" width="300" />

항공기 예시에서 항공기의 운항 상태는 `Aircraft` 객체의 속성에 저장되어 있습니다.

<a id="operators"></a>
### 연산자 (Operators)

연산자는 두 값 사이의 비교를 정의합니다. 구성 과정을 단순하게 하기 위해, 연산자 목록은 해당 파라미터에 유효한 연산자만 보이도록 미리 걸러집니다. 파라미터가 바뀌면 그 파라미터를 사용하는 모든 조건을 다시 구성해야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/submission_criteria_select_an_operator.png" alt="예시: 연산자 선택" width="300" />

선택한 파라미터에 따라 여러 연산자를 사용할 수 있습니다. 단일 값 파라미터에는 다음 연산자를 사용할 수 있습니다.

|연산자	|예시	|데이터 예시	|설명	|
|---	|---	|---	|---	|
|is	|name *is* John Doe	|"John Doe" is "John Doe" = TRUE	|왼쪽 값이 오른쪽 값과 정확히 일치합니다.	|
|is not	|**Current User** *is not* John Doe	|"John Doe" is not "Maria Smith" = TRUE	|왼쪽 값과 오른쪽 값이 일치하지 않습니다.	|
|matches	|name *matches* `^[A\|E\|I\|O\|U]*`	|"John Doe" matches	|왼쪽 값이 정규 표현식과 일치합니다.	|
|is less than	|Aircraft > Engine Count *is less than* 2	|4 is less than 2 = TRUE	|왼쪽 값이 오른쪽 값보다 작습니다.	|
|is greater than or equals	|Aircraft > Engine Count *is greater than or equals* 2	|4 is greater than or equals 2 = TRUE	|왼쪽 값이 오른쪽 값보다 큽니다.	|

**설명**: 표는 원문을 그대로 옮긴 것입니다. 원문의 `is less than` 행 데이터 예시("4 is less than 2 = TRUE")는 수학적으로는 FALSE가 맞으므로 원문의 오기로 보입니다. 또 `is greater than or equals`의 설명은 원문에 "크다"로만 적혀 있지만 연산자 이름대로 "크거나 같다"로 이해하면 됩니다. `matches`의 정규 표현식 `^[A|E|I|O|U]*`는 문자열 맨 앞에서부터 모음 대문자(및 `|` 문자)가 0개 이상 이어지는 패턴입니다.

다중 값 파라미터에는 다음 연산자를 사용할 수 있습니다. 객체 참조 목록은 값의 목록(객체 값 또는 지정한 속성의 값)으로 변환됩니다.

|연산자	|예시	|데이터 예시	|설명	|
|---	|---	|---	|---	|
|includes	|Aircrafts > Pilot Name *includes* "John Doe"	|\[ "John Doe", "Maria Smith" ] includes "John Doe" = TRUE	|왼쪽 값 중 적어도 하나가 오른쪽 값과 정확히 일치합니다.	|
|includes any	|List of names *includes any* Aircrafts > Pilot Name	|\["King Louis", "John Doe"] is included in \[ "John Doe", "Maria Smith" ] = TRUE	|왼쪽 값 중 적어도 하나가 오른쪽 값 중 적어도 하나와 정확히 일치합니다.	|
|is included in	|name *is included in* \[ "John Doe", "Maria Smith" ]	|"John Doe" is included in \[ "John Doe", "Maria Smith" ] = TRUE	|왼쪽 값이 오른쪽 값 중 적어도 하나와 정확히 일치합니다.	|
|each is	|Aircrafts > Pilot Name *each is* "John Doe"	|\[ "John Doe", "Maria Smith" ] each is "John Doe" = FALSE	|왼쪽 값이 모두 오른쪽 값과 정확히 일치합니다.	|
|each is not	|Aircrafts > Pilot Name *each is not* "John Doe"	|\[ "John Doe", "Maria Smith" ] each is not "King Louis" = TRUE	|왼쪽 값이 모두 오른쪽 값과 정확히 일치하지 않습니다.	|

예시에서 사용자는 여러 그룹의 구성원이지만 비교 대상은 그룹 하나이므로, 겹치는지 확인하려면 `includes` 연산자를 선택해야 합니다. 반면 운항 상태는 기대하는 상태와 정확히 일치해야 하므로 `is` 연산자를 설정해야 합니다.

**설명**: 다중 값 연산자를 집합 연산으로 바꾸어 보면, 왼쪽 목록을 L, 오른쪽 값을 r(또는 목록 R)이라 할 때 `includes`는 r이 L에 속하는지, `includes any`는 L과 R의 교집합이 비어 있지 않은지, `is included in`은 단일 값 l이 R에 속하는지, `each is`는 L의 모든 원소가 r과 같은지, `each is not`은 L의 어떤 원소도 r과 같지 않은지를 검사합니다. 사용자의 그룹 목록에 특정 그룹이 있는지 보는 것은 `includes`입니다.

<a id="value"></a>
### 값 (Value)

값은 비교의 다른 쪽을 나타냅니다. 값은 기존 파라미터, 정적 값, 또는 값 없음(no value) 중 하나로 정할 수 있습니다. 값 없음은 첫 번째 값이 비어 있는지(또는 null인지) 검사합니다. 연산자와 마찬가지로, 사용할 수 있는 선택지는 첫 번째 값의 타입에 따라 달라집니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/submission_criteria_select_a_value_right.png" alt="예시: 값 선택" width="300" />

이제 항공기 예시에 필요한 두 조건을 마무리할 수 있습니다. 운항 관제사의 경우 올바른 그룹을 정적 파라미터로 선택해야 합니다. 그룹은 바뀌면 안 되고, 맥락과 관계없이 액션을 제출할 때마다 같아야 하기 때문입니다. 따라서 `specific value`(특정 값)를 사용하고 드롭다운에서 원하는 그룹을 선택합니다. 항공기는 운항 상태 속성이 `Yes`일 때 운항 가능으로 간주되며, 이 역시 특정 값 옵션으로 설정할 수 있습니다.

> **중간 요약**: 조건 하나는 "왼쪽 값, 연산자, 오른쪽 값"으로 구성됩니다. 왼쪽 값은 템플릿에서 고르고, 연산자는 값의 종류(단일 또는 다중)에 맞게 걸러져 제시되며, 오른쪽 값은 파라미터, 정적 값, 값 없음 중에서 고릅니다.

<a id="logical-operators"></a>
## 논리 연산자 (Logical operators)

논리 연산자는 서로 다른 조건을 결합하는 데 사용합니다. 논리 연산자는 중첩해서 더 복잡한 로직을 만들 수도 있으며, 그 아래에 있는 조건이 모두(all), 하나라도(any), 또는 하나도(no) 충족되어야 통과하도록 할 수 있습니다.

**설명**: all, any, no는 각각 불 논리의 AND, OR, NOR(모두 거짓일 때 참)에 해당합니다. 예를 들어 `any( all(시나리오 실행, 계획 그룹 소속), 운항 관제사 그룹 소속 )`처럼 중첩하면 앞의 실행 컨텍스트 예시를 표현할 수 있습니다.

<a id="failure-message"></a>
## 실패 메시지 (Failure message)

실패 메시지는 액션을 제출할 수 없을 때 어떤 오류를 표시할지 정의합니다. 루트 수준의 모든 조건과 논리 연산자는 각자 고유한 실패 메시지를 가집니다. 하위 수준의 조건이 충족되지 않으면 해당하는 루트 수준(부모)의 실패 메시지가 표시됩니다. 실패 메시지는 조건이 충족되지 않을 때마다 Foundry 전반(Object Explorer, Workshop, Quiver)에서 최종 사용자에게 표시됩니다. 실패 메시지는 사용자에게 왜 액션 제출이 막혔는지 알려 줍니다.

Ontology Manager에서 [테스트 실행(test run)](05_test-run.md)으로 주어진 파라미터 값 집합에 대해 제출 조건이 어떻게 평가되는지 확인할 수 있습니다.

> **중간 요약**: 논리 연산자(all, any, no)로 조건을 결합하고 중첩합니다. 실패 메시지는 루트 수준의 조건이나 논리 연산자마다 정의하며, 하위 조건이 실패하면 루트 수준 메시지가 사용자에게 표시됩니다.

## 정리

- 제출 조건은 액션 제출 가능 여부를 결정하는 논리식으로, 액션 타입 편집 권한과는 별개입니다.
- 조건은 현재 사용자, 파라미터, 실행 컨텍스트 템플릿 중 하나로 만들며, 그룹이나 마킹 멤버십에 `NOT` 조건은 쓰지 않아야 합니다.
- 각 조건은 왼쪽 값, 연산자, 오른쪽 값(파라미터, 정적 값, 값 없음)으로 구성되고, 단일 값과 다중 값에 따라 쓸 수 있는 연산자가 다릅니다.
- 논리 연산자 all, any, no로 조건을 결합하고 중첩할 수 있습니다.
- 루트 수준 실패 메시지가 사용자에게 제출이 막힌 이유를 알려 주며, 테스트 실행으로 평가 결과를 미리 확인할 수 있습니다.
