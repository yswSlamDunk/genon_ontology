# 일괄 실행 (Batched execution)

- 원문: https://www.palantir.com/docs/foundry/action-types/function-actions-batched-execution/
- 사이드바 위치: Define Ontologies > Action types > Function-backed actions > Batched execution

이 페이지는 함수 기반 액션이 여러 건의 요청을 한꺼번에 받을 때, 함수를 요청마다 따로 호출하지 않고 한 번의 실행으로 묶어 처리하는 일괄 실행(batched execution) 설정을 설명합니다. 함수가 받아야 하는 입력 형태와 예제 코드를 함께 보여 줍니다.

[Workshop 인라인 편집](https://www.palantir.com/docs/foundry/workshop/widgets-object-table/#inline-edits-cell-level-writeback)이나 [Automate](https://www.palantir.com/docs/foundry/automate/execution-settings/)처럼 액션이 일괄(batch)로 실행될 때, 백킹 함수는 보통 요청 하나마다 한 번씩 순서대로 호출되고, 모든 편집(edit)은 액션 호출이 끝날 때 원자적(atomic)으로 한꺼번에 적용됩니다.

이와 달리 성능을 높이거나 편집 충돌을 해결하기 위해, 함수가 액션 호출 묶음 전체를 한 번의 실행에서 받도록 구성할 수도 있습니다.

일괄 실행을 켜려면 함수가 *구조체(struct)의 리스트*(구조체는 "map" 또는 "dictionary"라고도 부름)를 담은 *단일 입력 파라미터*를 받아야 합니다. 그러면 일괄 실행을 켤 수 있고, 평소 함수의 최상위 입력에 데이터를 전달하는 것과 같은 방식으로 이 구조체의 필드에 데이터를 전달할 수 있습니다.

일괄 실행을 사용할 때는 다음과 같이 동작합니다.

* 단일 액션 호출은 리스트 입력 파라미터에 *항목 하나*가 들어 있는 함수 실행 한 번을 일으킵니다.
* 일괄 액션 호출은 리스트 입력 파라미터에 *여러 항목*이 들어 있는 함수 실행 한 번을 일으킵니다.

**설명**: 원자적 적용이란 묶음 안의 편집이 전부 반영되거나 전부 반영되지 않는다는 뜻으로, 데이터베이스 트랜잭션의 커밋과 같은 성질입니다. 예를 들어 Workshop 표에서 사용자가 Flight 3개의 목적지 칸을 고치고 저장하면 요청이 3건 생깁니다. 기본 방식에서는 함수가 3번 호출되고, 일괄 실행 방식에서는 길이 3인 리스트를 받는 함수가 1번 호출됩니다. 함수가 한 번만 실행되므로 호출 오버헤드가 줄고, 같은 객체를 여러 요청이 건드리는 경우에도 함수 안에서 한꺼번에 보고 처리할 수 있습니다.

<a id="example"></a>
### 예제 (Example)

다음과 같은 시그니처를 가진 함수 기반 액션 대신:

```typescript
@OntologyEditFunction()
  public updateDestination(flight: Flight, destination: Airport): void {
    // flight 객체 업데이트
}
```

함수가 요청의 "묶음(batch)"을 받아 한 번의 실행에서 모두 처리하도록 할 수 있습니다.

```typescript
@OntologyEditFunction()
public updateDestinationBatch(batch: {flight: Flight, destination: Airport}[]): void {
    batch.forEach(({flight, destination}) => {
      // flight 객체 업데이트
    });
}
```

**설명**: 첫 번째 함수는 `flight`와 `destination` 두 개의 입력을 따로 받습니다. 두 번째 함수는 `{flight, destination}` 형태의 객체(구조체)를 원소로 갖는 배열 하나만 받습니다. `{flight: Flight, destination: Airport}[]`가 "구조체의 리스트" 타입이고, 원래 최상위 입력이던 `flight`와 `destination`이 구조체의 필드로 들어갔습니다. `batch.forEach(...)`가 리스트를 돌며 요청 하나하나를 처리합니다. 요청이 1건이면 길이 1인 배열이, 3건이면 길이 3인 배열이 들어옵니다.

그런 다음 액션 타입을 구성할 때 이 함수에 대해 일괄 실행을 켤 수 있습니다.

![일괄 실행 토글](https://www.palantir.com/docs/resources/foundry/action-types/function_backed_actions_batch_execution_toggle.png)

## 정리

- 일괄로 실행되는 액션은 기본적으로 요청마다 함수를 순서대로 한 번씩 호출하고, 편집은 마지막에 원자적으로 적용됩니다.
- 일괄 실행을 켜면 묶음 전체가 함수 실행 한 번으로 전달되어 성능 향상이나 편집 충돌 해결에 도움이 됩니다.
- 이를 위해 함수는 구조체의 리스트를 담은 단일 입력 파라미터를 받아야 하며, 단일 호출이면 항목 1개, 일괄 호출이면 여러 항목이 들어옵니다.
- 함수를 이렇게 작성한 뒤 액션 타입 설정에서 일괄 실행 토글을 켭니다.
