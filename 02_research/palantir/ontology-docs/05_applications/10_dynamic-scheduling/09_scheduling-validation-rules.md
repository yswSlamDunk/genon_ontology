# 검증 규칙 (Validation rules)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-validation-rules/
- 사이드바 위치: Applications > Dynamic Scheduling > Validation rules

이 페이지는 Scheduling Gantt Chart 위젯에서 일정이 조직의 제약 조건(예: 같은 작업자가 두 일정에 겹쳐 배정되면 안 됨)을 지키는지 자동으로 검사하는 검증 규칙(validation rule)을 설명합니다. 규칙은 TypeScript 함수(function)로 작성하며, 사용자가 일정을 바꿀 때마다 다시 평가되어 위반 여부가 화면에 표시됩니다. 규칙이 언제 호출되는지, 위젯에 어떻게 등록하는지, 함수가 어떤 형식으로 결과를 돌려줘야 하는지를 다룹니다.

제약 조건은 모든 스케줄링 워크플로에 본래부터 들어 있는 요소입니다. 단순한 시간 제한부터 자주 바뀌는 규칙 매트릭스까지, 규칙의 복잡도는 다양합니다. 검증 규칙을 사용하면 이러한 제약 조건을 코드로 표현할 수 있으므로, 최종 사용자는 조직 운영을 규정하는 제한 사항과 제약을 이해한 상태에서 일정을 만들고 수정할 수 있습니다.

각 검증 규칙은 TypeScript 함수로 뒷받침되며, 이 함수는 Schedule 객체의 현재 상태가 함수 로직에 정의된 특정 조건을 충족하는지 평가합니다.

사용자는 Workshop의 Scheduling Gantt Chart 위젯 화면에서 검증 규칙의 결과를 보게 됩니다. 처음 로드할 때 모든 규칙이 온톨로지(Ontology)의 현재 상태를 기준으로 평가됩니다. 일정을 수정할 때마다 규칙이 다시 평가됩니다. 이 과정을 통해 사용자는 자신의 결정이 특정 제약과 제한을 어떻게 준수하는지 알 수 있습니다.

아래는 Scheduling Gantt Chart 위젯 안의 스케줄링 제약 조건 예시입니다. 첫 번째 그림에서는 토글로 표시된 것처럼 **No Operator Overlaps**(작업자 중복 없음) 규칙이 적용되어 있습니다. 이 옵션은 이 규칙을 지키는 결과만 표시되도록 합니다. 다음 그림은 그 출력을 보여 줍니다. 이 예에서는 두 행 사이에 충돌이 있는데, 작업자 Brad Evans와 Ashley Brown의 일정이 겹치고 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/constraints-2.png" alt="검증 규칙 인터페이스 예시." width="900" >

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/constraints-1.png" alt="규칙을 충족하지 못한 검증 규칙 예시." width="600" >

**설명**: 앞 페이지의 Suggestion Function은 로드 시점에 한 번만 계산되지만, 검증 규칙은 일정을 바꿀 때마다 다시 평가된다는 점이 다릅니다. 따라서 "방금 옮긴 작업 때문에 규칙이 깨졌는가"를 즉시 확인할 수 있습니다.

> **중간 요약**: 검증 규칙은 일정의 제약 조건을 TypeScript 함수로 표현한 것으로, 처음 로드할 때와 일정을 수정할 때마다 평가되어 위반 여부를 화면에 보여 줍니다.

<a id="orchestration"></a>
## 오케스트레이션 (Orchestration)

Workshop의 Scheduling Gantt Chart 위젯에서는 일정을 검증하기 위해 변경이 수행될 때마다 검증 규칙이 호출됩니다.

```
1. 시나리오에 대해 액션 "saveHandler" 호출
2. 갱신된 시나리오에 대해 검증 규칙 호출
3. 시나리오에 대해 액션 "saveHandler" 호출
4. 갱신된 시나리오에 대해 검증 규칙 호출
등등 ...
n. 사용자가 "Submit changes"를 선택하면, 시나리오에 적용되었던 모든 액션이 온톨로지에 적용됨
```

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/validation-rules-outcome.png" alt="규칙을 충족한 검증 규칙 예시." width="300" >

**설명**: 시나리오(scenario)는 실제 온톨로지 데이터를 바로 바꾸지 않고, 변경 사항을 임시로 쌓아 두는 작업 공간입니다. 사용자가 퍽을 옮길 때마다 `saveHandler` 액션이 시나리오에만 적용되고, 그 시나리오 상태로 규칙을 다시 평가합니다. 사용자가 마지막에 "Submit changes"를 눌러야 쌓인 액션들이 실제 온톨로지에 반영됩니다. 데이터베이스의 트랜잭션에서 커밋 전까지 변경이 확정되지 않는 것과 같은 구조입니다.

> **중간 요약**: 일정 변경은 먼저 시나리오에 적용되고 그때마다 검증 규칙이 다시 호출되며, "Submit changes"를 선택해야 모든 변경이 온톨로지에 반영됩니다.

<a id="implement-validation-rules"></a>
## 검증 규칙 구현하기 (Implement validation rules)

규칙은 Scheduling Gantt Chart 위젯에서 직접 구성하므로, 사용 사례별로 규칙을 적용할 수 있습니다. Scheduling Gantt Chart 위젯에 규칙을 추가하려면 다음을 수행합니다.

1. 해당 객체 타입의 스케줄 데이터 레이어로 이동합니다.
2. 아래로 스크롤해 **Rules** 섹션에서 **Add new item**을 선택합니다.
3. **Rule Name** 텍스트 상자에 Scheduling Gantt Chart에서 최종 사용자에게 보여 줄 규칙 설명을 입력합니다.
4. 드롭다운 메뉴에서 **Constraint Type**을 선택합니다. "HARD"는 느낌표가 있는 빨간 원으로 표시됩니다. "SOFT"는 느낌표가 있는 주황색 삼각형으로 표시됩니다.
5. 드롭다운 메뉴에서 **Rule Function**을 선택합니다.
6. 함수에는 `scheduleObjectPrimaryKeys` 입력 인자가 있어야 합니다. 이 인자는 실행 시점에 위젯이 자동으로 채우므로 비워 두어도 됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/scheduling-rule-config.png" alt="Scheduling Gantt Chart 위젯의 규칙 구성 패널 예시." width="300" >

**설명**: HARD와 SOFT는 제약의 강도를 나타냅니다. 일반적으로 HARD 제약은 반드시 지켜야 하는 조건(예: 한 사람이 같은 시간에 두 곳에 있을 수 없음), SOFT 제약은 지키는 것이 바람직하지만 어길 수도 있는 조건(예: 선호 근무지)에 씁니다. 위젯에서는 아이콘 모양과 색으로 둘을 구분해 보여 줍니다.

<a id="functions-interface"></a>
### 함수 인터페이스 (Functions interface)

아래 타입들은 검증 규칙을 작성하는 데 필요한 정보를 나타내며, 각 객체에 대한 규칙의 상태를 포함합니다.

```typescript
type IFoORule = (scheduleObjectPrimaryKeys: string[]) => Array<IRuleResult>

/*
   규칙 결과는 다음과 같이 해석됩니다.
   true - 규칙을 통과한 것으로 검증됨
   false - 규칙을 통과하지 못한 것으로 검증됨
   undefined - 해당 Schedule 객체와 관련 없는 규칙임
*/

interface IRuleResult {
    result: boolean | undefined;
    scheduleObjectPrimaryKey: string;
    details?: Array<IRuleResultDetails>;
}

/*
   기본적으로 팝오버 카드의 텍스트에는 규칙 객체에 구성된 규칙 이름이 표시됩니다.

   선택적으로, 규칙 평가 결과에 따라 사용자 지정 텍스트를 명시적으로 정의할 수 있습니다.

   또한 관련된 puckId 집합을 제공해, 규칙이 통과하거나 실패하는 이유를
   사용자에게 가리킬 수 있습니다.
*/

interface IRuleResultDetails {
    description: string;
    relatedPuckIds: string[];
}
```

**설명**: 규칙 함수는 검사할 Schedule 객체의 기본 키(primary key) 목록을 받아, 객체마다 하나의 `IRuleResult`를 담은 배열을 반환합니다. `result`는 세 가지 값을 가질 수 있습니다. `true`는 통과, `false`는 위반, `undefined`는 이 규칙이 해당 객체에는 적용되지 않음을 뜻합니다. `details`에 `description`(팝오버에 보여 줄 문장)과 `relatedPuckIds`(예: 겹치는 상대 일정의 퍽 ID)를 넣으면, 사용자가 왜 위반인지 관련 일정을 함께 확인할 수 있습니다.

<a id="example-functions"></a>
### 예제 함수 (Example Functions)

다음은 검증의 핵심 로직을 뺀 함수의 기본 예입니다.

```typescript
import { Function, Integer } from "@foundry/functions-api";
import { Objects, TaskOrSchedule, ObjectSet} from "@foundry/ontology-api";

// 타입 정의는 공개 문서를 참고하세요

interface IRuleResultDetails {
    description: string;
    relatedPuckIds: string[];
}
interface IRuleResult {
    result: boolean | undefined;
    scheduleObjectPrimaryKey: string;
    details?: Array<IRuleResultDetails>;
}
type IFoORule = (scheduleObjectPrimaryKeys: string[]) => Array<IRuleResult>


export class MyFunctions {

    // 참고: 제약 함수의 입력 인자 이름은 반드시 정확히 `scheduleObjectPrimaryKeys`여야 합니다.
    // 위젯은 이 이름을 보고 이 함수에 올바른 키 집합을 보냅니다.
    @Function()
    public async evaluateIfTaskOrScheduleIsValid(scheduleObjectPrimaryKeys: string[]): Promise<Array<IRuleResult>> {
        // 모든 Schedule 온톨로지 객체를 가져옵니다
        const taskOrSchedules = await Objects.search().taskOrSchedule()
            .filter(taskOrSchedule => taskOrSchedule.primaryKey.exactMatch(...scheduleObjectPrimaryKeys))
            .allAsync();

        // 입력된 키마다 순회하며 결과 항목을 하나씩 만듭니다
        const ruleResults: Array<IRuleResult> = scheduleObjectPrimaryKeys.map(pk => {
            const currentTaskOrSchedule = taskOrSchedules.find(taskOrSchedule => taskOrSchedule.primaryKey === pk);
            // 객체를 가지고 무언가를 검증합니다 ...

            // 검증 결과를 만듭니다
            const currentValidationDetails: Array<IRuleResultDetails> = [];
            currentValidationDetails.push(
                {
                    description: "This is the description of the validation that passes or not",
                    relatedPuckIds: []
                });

            const currentResult: IRuleResult= {
                result: true,
                scheduleObjectPrimaryKey: pk,
                details: currentValidationDetails,
            };
            return currentResult;
        });

        return ruleResults;
    }
}
```

**설명**: 이 함수의 동작 순서는 다음과 같습니다.

1. 입력 `scheduleObjectPrimaryKeys`로 받은 기본 키들과 일치하는 `taskOrSchedule` 객체들을 `Objects.search()`로 한 번에 조회합니다. SQL로 쓰면 `SELECT * FROM taskOrSchedule WHERE primaryKey IN (...)`에 해당합니다.
2. 입력 키마다 `map`으로 순회하면서 해당 객체를 찾고, 검증 로직을 수행한 뒤(이 예제에서는 생략됨) `IRuleResult` 하나를 만듭니다.
3. 예제는 항상 `result: true`를 반환하므로 모든 객체가 통과로 표시됩니다. 실제로는 이 자리에 겹침 검사 같은 로직을 넣어 `true`나 `false`를 계산합니다.

입력 인자 이름이 정확히 `scheduleObjectPrimaryKeys`여야 위젯이 값을 채워 준다는 점이 가장 중요한 규칙입니다.

더 복잡한 검증 규칙도 만들 수 있습니다. 예를 들어 규칙으로 다음을 검사할 수 있습니다.

* 일정들이 순서대로(빈틈 없이) 이어지는지
* 일정들이 겹치는지
* 일정에 배정된 사람이 일치하는 기술이나 자격증을 갖고 있는지

> **중간 요약**: 규칙은 스케줄 데이터 레이어의 **Rules** 섹션에서 이름, HARD/SOFT 제약 타입, 규칙 함수를 지정해 추가합니다. 규칙 함수는 `scheduleObjectPrimaryKeys`를 받아 객체별로 통과(true), 위반(false), 해당 없음(undefined)과 선택적 상세 설명을 반환합니다.

## 정리

- 검증 규칙은 일정의 제약 조건을 TypeScript 함수로 표현하며, 처음 로드할 때와 일정을 수정할 때마다 다시 평가됩니다.
- 변경은 시나리오에 먼저 적용되고 그때마다 규칙이 호출되며, "Submit changes"로 확정해야 온톨로지에 반영됩니다.
- 규칙은 위젯의 스케줄 데이터 레이어 **Rules** 섹션에서 추가하고, HARD(빨간 원)와 SOFT(주황 삼각형) 중 제약 타입을 고릅니다.
- 규칙 함수의 입력 인자 이름은 정확히 `scheduleObjectPrimaryKeys`여야 하며, 객체별 `IRuleResult` 배열을 반환합니다.
- 연속성, 겹침, 기술이나 자격 일치 같은 복잡한 규칙도 만들 수 있습니다.
