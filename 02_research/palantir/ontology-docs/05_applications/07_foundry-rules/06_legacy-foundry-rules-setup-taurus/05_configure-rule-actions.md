# 규칙 액션 구성하기 (Configure rule Actions)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/configure-rule-actions/
- 사이드바 위치: Applications > Foundry Rules > Legacy Foundry Rules setup (Taurus) > Configure rule Actions

이 페이지는 레거시(Taurus) 방식에서 규칙의 출력 형식을 정하는 규칙 액션(rule Action)을 구성하는 방법을 다룹니다. 규칙 액션은 실제로 실행되는 액션이 아니라, 액션 타입의 파라미터 정의를 빌려 출력 열의 이름과 타입을 지정하는 장치입니다. 파라미터 타입, 필수 여부, 이름과 ID가 결과에 어떻게 반영되는지, 그리고 제출 조건을 어떻게 두는지 설명합니다.

**주의**: 2022년 7월 이전의 Foundry Rules(이전 이름 Taurus)는 규칙 출력으로 Foundry 액션을 사용했습니다. 이 섹션은 2022년 7월 이전에 Foundry Rules를 배포한 경우에만 해당합니다.

규칙 액션은 Foundry Rules 안에서 규칙 출력에 출력 스키마를 강제하는 수단입니다. 이는 열 이름과 타입을 지정하는 메커니즘으로 Foundry 액션을 사용함으로써 이루어집니다. 규칙 액션은 Foundry Rules에서 사용될 Foundry 액션입니다.

<img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/example_rule_action_configuration.png" alt="Foundry Rules에서 사용할 Foundry 액션 구성" width="500" />

위 스크린숏의 액션은 [변환 안에서만 사용되며](04_configure-transforms-pipeline.md#rule-action-datasets) 단독으로 실행되지는 않습니다. 이 액션에는 액션 규칙(Action rules)을 하나도 구성하지 않는 것이 편리합니다(위 스크린숏의 **1**). 그러면 혹시 액션이 실행되더라도 아무 효과가 없습니다.

액션의 파라미터는 Foundry Rules Workshop 애플리케이션에서 최종 사용자에게 표시되며, 규칙 로직이 출력하는 열에 매핑할 수 있게 됩니다(위 스크린숏의 **2**).

* 파라미터 타입은 올바른 열 타입을 강제하는 데 사용됩니다. 예를 들어 날짜(date) 타입 파라미터를 쓰면 날짜와 타임스탬프 타입 열만 이 파라미터에 매핑할 수 있습니다. 또한 파라미터 ID가 규칙의 열 이름이나 객체 속성 ID와 일치하면, 해당 열이나 속성으로 파라미터가 미리 채워집니다.
* 필수로 표시된 파라미터는 Foundry Rules Workshop 애플리케이션에서도 필수입니다. 마찬가지로 선택 파라미터는 매핑된 열 없이 비워 둘 수 있으며, 이는 파라미터에 `null` 값을 주는 것과 같습니다.
* 파라미터 이름은 Foundry Rules Workshop 애플리케이션에서 라벨로 쓰이고, 파라미터 ID는 [변환의 결과 데이터셋](04_configure-transforms-pipeline.md#rule-action-datasets)에서 열 이름으로 쓰입니다.
* 출력 데이터셋에는 파라미터 ID 열 외에도, 그 행이 나온 규칙의 ID를 나타내는 `taurus_rule_id` 열이 들어 있습니다.

액션을 저장하려면 **제출 조건(Submission Criteria)**(**3**)을 정의해야 합니다. 규칙 액션에서 가장 흔한 제출 조건은 **Current User**(현재 사용자)가 Foundry Rules 워크플로를 편집할 권한이 있는 사용자 그룹에 속하는지 확인하는 것입니다. 이 검증은 Foundry Rules 앱에서 규칙을 편집할 때 적용됩니다.

**설명**: 규칙 액션은 액션 타입을 "출력 테이블의 스키마 선언"으로 재활용하는 방식입니다. 예를 들어 파라미터가 `employee_id`(문자열, 필수, 표시 이름 "직원"), `flag_date`(날짜, 필수, 표시 이름 "표시 일자"), `note`(문자열, 선택, 표시 이름 "메모")인 액션을 규칙 액션으로 쓰면, 규칙 작성자는 Workshop에서 "직원", "표시 일자", "메모" 라벨 옆에 규칙 결과의 열을 하나씩 고르게 됩니다. "표시 일자"에는 날짜나 타임스탬프 열만 고를 수 있고, "메모"는 비워 두면 null이 됩니다. 변환이 쓰는 결과 데이터셋의 스키마는 `CREATE TABLE result (employee_id STRING NOT NULL, flag_date DATE NOT NULL, note STRING, taurus_rule_id STRING)`에 해당합니다(규칙 ID 열의 타입은 원문에 명시되어 있지 않습니다).

## 정리

- 이 페이지는 2022년 7월 이전에 배포한 레거시(Taurus) 환경에만 해당합니다.
- 규칙 액션은 Foundry 액션의 파라미터 정의를 이용해 규칙 출력의 열 이름과 타입을 강제하며, 변환 안에서만 쓰이고 단독 실행되지 않습니다.
- 액션 규칙을 비워 두면 실수로 실행되어도 효과가 없습니다.
- 파라미터 타입은 매핑 가능한 열 타입을, 필수 여부는 매핑 필수 여부를 정하며, 파라미터 이름은 라벨, ID는 출력 열 이름이 됩니다. 출력에는 `taurus_rule_id` 열이 추가됩니다.
- 저장하려면 제출 조건이 필요하며, 보통 현재 사용자가 워크플로 편집 권한 그룹에 속하는지 확인합니다.
