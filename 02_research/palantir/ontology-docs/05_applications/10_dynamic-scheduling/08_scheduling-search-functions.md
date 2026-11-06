# 검색 함수 (Search Functions)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-search-functions/
- 사이드바 위치: Applications > Dynamic Scheduling > Search Functions

이 페이지는 Scheduling Gantt Chart에서 사용자가 행이나 퍽을 오른쪽 클릭해 실행하는 Search Function(검색 함수)을 설명합니다. 예를 들어 "이 작업을 맡을 수 있는 다른 정비사는 누구인가", "이 항공기에 비어 있는 시간은 언제인가" 같은 질문에 대한 답을 함수가 계산해 화면에 강조해 줍니다. 함수의 입력, 출력 타입 정의도 함께 제공합니다.

Search Function을 사용하면 스케줄링 워크플로에서 생기는 구체적이고 고유한 문제에 대해 가능한 해결책을 빠르게 찾고 평가할 수 있습니다.

각 Search Function은 TypeScript 함수(function)로 뒷받침됩니다. 유연한 인터페이스 덕분에 빌더는 퍽, 시간 슬롯, 또는 둘의 조합을 반환하는 함수를 작성할 수 있습니다. 또한 Search Function은 행 기반이거나 퍽 기반일 수 있습니다.

행 기반 Search Function의 경우, 사용자는 빈 공간을 오른쪽 클릭해 행 객체와 시각을 함수 입력으로 전달해야 합니다. 퍽 기반 Search Function의 경우, 사용자는 퍽을 오른쪽 클릭해 객체와 시각을 함수 입력으로 전달해야 합니다.

아래 그림은 퍽을 반환하는 Search Function의 인터페이스를 보여 줍니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/search-functions-1.png" alt="예시: 퍽을 반환하는 Search Function" width="700" >

아래 그림은 시간 슬롯을 반환하는 Search Function의 인터페이스를 보여 줍니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/search-functions-2.png" alt="예시: 시간 슬롯을 반환하는 Search Function" width="700" >

Search Function이 실행되면 Scheduling Gantt Chart에 새 검색 그룹이 만들어지고 결과가 노란색으로 강조됩니다. 검색 그룹은 그룹 헤더 오른쪽의 캐럿 기호(**^**)를 선택해 접고 펼 수 있습니다. 또한 사용자는 **Results Overview** 옵션을 선택해 Search Function의 출력을 보여 주는 패널을 열어 검색 결과를 자세히 볼 수 있습니다. 아래 그림이 그 화면입니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/search-functions-3.png" alt="Search Function 결과 개요 인터페이스." width="700" >

**설명**: 행 기반과 퍽 기반의 차이는 함수가 받는 입력입니다. 행 기반은 "어느 행(자원)의 어느 시각"을 받아 그 주변에서 해결책을 찾고(예: 이 정비사가 이 시각에 할 수 있는 작업 찾기), 퍽 기반은 "어느 일정 객체"를 받아 그 객체에 대한 해결책을 찾습니다(예: 이 작업을 대신 맡을 수 있는 정비사 찾기). 반환값 중 퍽은 기존 일정 객체를 가리키고, 시간 슬롯은 특정 행의 특정 시간 구간을 가리킵니다.

> **중간 요약**: Search Function은 행이나 퍽을 오른쪽 클릭해 실행하는 TypeScript 함수로, 퍽이나 시간 슬롯을 반환합니다. 결과는 새 검색 그룹에 노란색으로 강조되고, **Results Overview** 패널에서 자세히 볼 수 있습니다.

<a id="functions-interface"></a>
## 함수 인터페이스 (Functions interface)

아래 타입들은 행이나 퍽에서 호출될 때 Search Function을 작성하는 데 필요한 정보를 나타내며, 검색 그룹에 대한 세부 사항을 포함합니다.

```
type IPuckSearch = (puck: ObjectReference) => ISearchResult
type IRowSearch = (rowId: string, selectedTime: Timestamp) => ISearchResult


/*
   Search Function은 시간 슬롯, 퍽, 또는 둘 다 반환할 수 있습니다. SLOT과 PUCK은
   IHighlight의 type으로 사용됩니다.
*/

export enum HighlightType {
    SLOT = "SLOT",
    PUCK = "PUCK",
}


/*
   시간 슬롯 집합을 반환하는 함수에서 IHighlight 안에 사용됩니다.
*/

export interface IDomain {
    start: Long;
    end: Long;
}

/*
   Search Function 실행 후 UI에서 무엇을 강조할지 결정하는 데 사용됩니다.
*/

export interface IHighlight {
    type: string;
    // "SLOT"에 필요
    domain?: IDomain;
    containerId?: string;
    // "PUCK"에 필요
    schedulableObjectPrimaryKey?: string;
    schedulableObjectTypeId?: string;
    // 선택 사항
    comment?: string;
}

/*
   새로 만들어지는 검색 그룹의 제목과 함수가 반환하는 행들을 정의합니다.
*/
export interface IRowGroup {
    title: string;
    containerIds: string[];
    highlights: IHighlight[];
}

/*
   함수의 전체 반환 타입입니다.
*/

export interface ISearchResult {
    rowGroup?: IRowGroup;
    sourcePuckIds?: string[];
    error?: string;
}
```

**설명**: 이 코드는 Search Function의 시그니처와 반환 구조를 정의합니다.

- 입력: 퍽 기반 함수(`IPuckSearch`)는 오른쪽 클릭한 퍽의 객체 참조(`ObjectReference`) 하나를 받습니다. 행 기반 함수(`IRowSearch`)는 행 ID(`rowId`)와 클릭한 시각(`selectedTime`)을 받습니다.
- 출력: `ISearchResult`입니다. 핵심은 `rowGroup`으로, 새 검색 그룹의 제목(`title`), 그룹에 보여 줄 행 ID 목록(`containerIds`), 강조할 항목 목록(`highlights`)을 담습니다. 문제가 있으면 `error`에 메시지를 담아 돌려줄 수 있습니다.
- `IHighlight`의 `type`이 `"SLOT"`이면 `containerId`(행)와 `domain`(시간 구간)을 채워 특정 행의 특정 시간 구간을 강조하고, `"PUCK"`이면 `schedulableObjectPrimaryKey`와 `schedulableObjectTypeId`를 채워 기존 퍽 하나를 강조합니다. `comment`는 강조 항목에 붙일 설명입니다.
- 예를 들어 "작업 T-7을 맡을 수 있는 정비사 찾기" 함수라면, `title`을 "T-7 대체 정비사"로, `containerIds`를 후보 정비사 ID 목록으로, `highlights`를 각 정비사 행의 비어 있는 시간 구간(SLOT)으로 채워 반환하는 식입니다.

> **중간 요약**: Search Function은 퍽 참조 또는 (행 ID, 시각)을 받아 `ISearchResult`를 반환하며, 그 안의 `rowGroup`이 검색 그룹의 제목, 표시할 행, 강조 항목(SLOT 또는 PUCK)을 정의합니다.

## 정리

- Search Function은 스케줄링 중 생기는 개별 문제의 해결책을 찾는 TypeScript 함수입니다.
- 행 기반 함수는 빈 공간을 오른쪽 클릭해 행과 시각을, 퍽 기반 함수는 퍽을 오른쪽 클릭해 객체와 시각을 입력으로 받습니다.
- 결과로 퍽, 시간 슬롯, 또는 둘 다를 반환할 수 있으며, 새 검색 그룹에 노란색으로 강조되고 **Results Overview** 패널에서 자세히 볼 수 있습니다.
- 반환 타입 `ISearchResult`는 검색 그룹 정보(`rowGroup`), 원본 퍽 ID(`sourcePuckIds`), 오류 메시지(`error`)로 구성됩니다.
