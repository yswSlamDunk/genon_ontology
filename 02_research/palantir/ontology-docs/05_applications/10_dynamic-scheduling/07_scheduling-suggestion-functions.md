# 제안 함수 (Suggestion Functions)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-suggestion-functions/
- 사이드바 위치: Applications > Dynamic Scheduling > Suggestion Functions

이 페이지는 Scheduling Gantt Chart에서 일정 객체(퍽)를 어디에, 언제 놓는 것이 적절한지를 색으로 표시해 주는 Suggestion Function(제안 함수)을 설명합니다. 조직의 규칙을 TypeScript 함수로 작성해 두면, 사용자가 퍽을 옮길 때 화면에 적합한 구간이 강조되어 판단을 돕습니다. 함수가 받아야 하는 입력과 돌려줘야 하는 출력의 타입 정의도 함께 제공합니다.

스케줄링과 자원 배정 워크플로의 핵심 과제는 특정 이벤트가 어디서, 언제 일어날 수 있는지, 또는 어디로 옮길 수 있는지를 아는 것입니다. 대부분의 일정에는 제약이 있고 모든 일정 선택지가 똑같이 적절한 것은 아닙니다. 이러한 제약과 기준을 로직으로 구현해 두면 도구가 사용자의 선택지 평가를 빠르게 도울 수 있습니다. Suggestion Functions 기능은 조직이 정의한 로직을 바탕으로 Schedule 객체 퍽을 놓을 수 있는 위치의 적합성을 시각적으로 표시해 사용자의 행동을 안내합니다.

각 Suggestion Function은 TypeScript 함수(function)로 뒷받침됩니다. 규칙 로직의 출력은 배정을 할 수 있는 영역을 강조하거나, 반대로 배정을 할 수 없는 영역을 강조하는 데 사용할 수 있습니다. 애플리케이션 빌더는 Workshop 위젯 구성의 설정을 통해 이 제안을 강제할 수 있는 선택권이 있습니다. 이 설정을 켜면 퍽이 가장 가까운 강조 영역에 강제로 놓이게 됩니다.

**주의**: Scheduling Gantt Chart에서 Suggestion Function의 결과는 정적입니다. 함수는 애플리케이션이 처음 로드될 때 실행되며, 그 이후에 수행된 액션은 **반영되지 않습니다**. 이 점은 이 기능이 여러분의 워크플로에 적합한지 판단하는 데 영향을 줍니다.

**설명**: 결과가 정적이라는 것은 함수가 화면 로드 시점에 한 번 계산한 결과를 계속 쓴다는 뜻입니다. 예를 들어 로드 후에 사용자가 Susan에게 작업 하나를 배정해 Susan의 일정이 꽉 찼더라도, 강조 영역은 로드 시점의 계산 결과 그대로 남아 있습니다. 배정할 때마다 적합성이 크게 바뀌는 워크플로라면 이 한계를 고려해야 합니다.

아래는 Suggestion Function을 효과적으로 사용하는 두 가지 예입니다.

다음 그림에서 Suggestion Function은 배정 대상인 개인(여기서는 "Susan")의 선호 위치를 제안하도록 작성되었습니다. 초록색 영역은 Garden City가 Susan이 선호하는 위치임을 나타내고, 회색으로 표시된 Sandbar는 선호하지 않는 위치임을 나타냅니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/suggestion-function-1.png" alt="예시: Suggestion Function 인터페이스." width="700" >

아래 예에서는 애플리케이션이 항공편을 조종사에게 배정하는 데 사용됩니다. 초록색으로 표시된 세로 방향의 시간 조각은, 스케줄러가 항공편의 시작/종료 시각은 조정하지 말고 조종사인 사람만 바꿔야 함을 알려 줍니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/suggestion-function-2.png" alt="예시: Suggestion Function 인터페이스." width="700" >

> **중간 요약**: Suggestion Function은 TypeScript 함수로 퍽을 놓기 적합한 영역과 부적합한 영역을 계산해 강조하며, 강조 영역에 퍽을 강제로 붙이는 설정도 있습니다. 결과는 애플리케이션 로드 시점에 한 번 계산되므로 이후 변경은 반영되지 않습니다.

<a id="functions-interface"></a>
## 함수 인터페이스 (Functions interface)

아래 타입들은 행이나 퍽에서 호출될 때 Search Function을 작성하는 데 필요한 정보를 나타내며, 검색 그룹에 대한 세부 사항도 포함합니다.

**설명**: 원문의 이 문장은 "Search Function"이라고 적혀 있지만, 아래 코드는 Suggestion Function의 타입 정의입니다. 원문 표기를 그대로 옮겼습니다.

```
/*
   Suggestion function은 퍽 기본 키 목록과 간트 차트의 시작/종료 시각을 입력받아,
   퍽 기본 키에서 (행 기본 키에서 시간 슬롯 배열로의 매핑)으로의 매핑을 반환합니다.
*/


type ISuggestion = (
    scheduleObjectPrimaryKeys: string[],
    domainStart: Timestamp,
    domainEnd: Timestamp,
) => FunctionsMap<string, FunctionsMap<string, Array<ISuggestionSlot>>>

/* Suggestion 타입 */

export interface IDomain {
    start: Long;
    end: Long;
}

/* rating은 위젯 UI의 강조 색을 정하는 데 사용됩니다. -1에서 1 사이 척도입니다.
   1에 가까울수록 더 진한 초록색으로, -1에 가까울수록 빨간색으로 강조됩니다.
*/

export interface ISuggestionSlot {
    domain: IDomain;
    rating: Float;
}

export type IValidSlots = Array<ISuggestionSlot>;
export type ISlotMappings = FunctionsMap<string, IValidSlots>;
export type ISuggestionResult = FunctionsMap<string, ISlotMappings>;


/*
  Schedule 객체의 시작/종료 시각이 고정되어 있고 배정된 자원만 바뀔 수 있는
  워크플로(세로 조각이 강조되는 경우)에서는 ALL_ROWS_ID를 지름길로 사용할 수 있습니다.
*/

export const ALL_ROWS_ID = "__ALL_ROWS";
```

**설명**: 이 코드는 함수의 입력과 출력 형식을 정의합니다.

- 입력: 화면에 있는 퍽들의 기본 키(primary key) 목록 `scheduleObjectPrimaryKeys`와, 간트 차트가 보여 주는 시간 범위의 시작 `domainStart`와 끝 `domainEnd`입니다.
- 출력: 2단계 맵입니다. 바깥 맵의 키는 퍽 기본 키, 안쪽 맵의 키는 행(자원) 기본 키이고, 값은 `ISuggestionSlot` 배열입니다. 각 슬롯은 시간 구간 `domain`(start와 end, Long 타입이므로 보통 밀리초 단위 시각 값)과 적합도 점수 `rating`(-1에서 1)을 가집니다.
- 예를 들어 결과가 `{"task-1": {"Susan": [{domain: {start: 9시, end: 12시}, rating: 0.9}]}}`이면, task-1 퍽을 Susan 행의 9시\~12시 구간에 놓는 것이 매우 적합하다는 뜻이고 그 구간이 진한 초록색으로 표시됩니다.
- 안쪽 맵의 키로 `ALL_ROWS_ID`(`"__ALL_ROWS"`)를 쓰면 행 구분 없이 모든 행에 같은 시간 구간을 표시합니다. 위의 조종사 배정 예처럼 시각은 고정이고 사람만 바꾸는 경우에 사용합니다.

> **중간 요약**: Suggestion Function은 퍽 기본 키 목록과 화면 시간 범위를 받아, 퍽마다 행별로 "시간 구간과 -1\~1 사이 점수" 목록을 돌려줍니다. 점수가 강조 색을 결정하며, `ALL_ROWS_ID`로 모든 행을 한꺼번에 지정할 수 있습니다.

## 정리

- Suggestion Function은 일정 제약과 선호를 TypeScript 함수로 구현해, 퍽을 놓기 적합한 영역을 간트 차트에 색으로 표시합니다.
- 위젯 설정으로 퍽이 가장 가까운 강조 영역에 놓이도록 강제할 수 있습니다.
- 결과는 애플리케이션 로드 시점에 한 번 계산되는 정적 결과이므로, 이후 액션은 반영되지 않습니다.
- 함수는 퍽 기본 키 목록과 시작/종료 시각을 입력받고, 퍽 기본 키와 행 기본 키로 찾아가는 시간 슬롯(구간과 rating) 배열을 반환합니다.
