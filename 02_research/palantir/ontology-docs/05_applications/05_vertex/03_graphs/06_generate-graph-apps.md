# 다른 애플리케이션에서 그래프 생성하기 (Generate a graph from other applications)

- 원문: https://www.palantir.com/docs/foundry/vertex/generate-graph-apps/
- 사이드바 위치: Applications > Vertex > Graphs > Generate a graph from other applications

이 페이지는 URL 파라미터를 붙인 링크 하나로 객체, 객체 집합, Search Around 함수 결과, 시간 범위가 미리 채워진 Vertex 그래프를 여는 방법을 설명합니다. 이 링크를 Object Explorer 같은 다른 Foundry 애플리케이션에 넣으면 클릭 한 번으로 그래프를 생성할 수 있습니다.

다른 Foundry 애플리케이션 안에, 미리 채워진 Vertex 그래프를 자동으로 생성하는 링크를 구성할 수 있습니다.

<a id="using-url-parameters-to-generate-a-graph"></a>
## URL 파라미터로 그래프 생성하기 (Using URL parameters to generate a graph)

URL 파라미터를 사용해 다음 동작을 할 수 있습니다.

* 기존 그래프로 시작하거나 새 그래프를 만듭니다.
* 객체 ID나 객체 집합(object set) ID를 지정해 그래프에 객체를 추가합니다.
* [**Search Around** 함수](07_generate-graph-functions.md)를 실행합니다.
* 시간 선택기의 시간 범위를 설정합니다.

다음 파라미터는 새 그래프를 만드는 URL(`/workspace/vertex/graph/create`)에만 적용됩니다.

* `selectObjectRid`: 지정한 객체가 그래프에 있으면 그 객체를 선택하고 그래프의 중심에 둡니다.
* `objectRid`: 지정한 객체를 그래프에 노드로 추가합니다.
* `objectSetRid`: 지정한 객체 집합의 모든 객체를 그래프에 노드로 추가합니다.
* `searchAroundFnRid`: 지정한 **Search Around** 함수의 결과를 그래프에 추가합니다. 이 함수는 `objectRid` 파라미터와 함께 쓰면 객체 하나로, `objectSetRid`와 함께 쓰면 그 객체 집합의 모든 객체로 호출됩니다.
  * 반드시 `objectSetRid` 또는 `objectRid` URL 파라미터와 함께 사용해야 합니다.

다음 파라미터는 기존 그래프의 URL(`/workspace/vertex/graph/{graphRid}`)과 새로 만드는 그래프의 URL(`/workspace/vertex/graph/create`) 모두에 적용됩니다.

* `selectedTime`: 선택된 시각을 설정합니다.
* `startTime`: 시간 범위의 시작 시각을 설정합니다.
* `endTime`: 시간 범위의 종료 시각을 설정합니다.

모든 시각은 밀리초 단위 UNIX 타임스탬프나 ISO 형식의 날짜 또는 날짜와 시각(예: `2020-02-15/2020-02-15 13:45:00 UTC`)으로 쓸 수 있습니다. `selectedTime`은 지정했지만 `startTime`과 `endTime` 중 하나라도 지정하지 않으면, 시간 범위는 기본 길이를 가지며 선택된 시각을 중심으로 놓입니다. `startTime`과 `endTime`은 지정했지만 `selectedTime`을 지정하지 않으면, 선택된 시각은 `startTime`과 같아집니다.

**설명**: 여러 파라미터를 조합한 URL은 예를 들어 다음과 같습니다(RID 값은 설명용으로 줄여 쓴 것입니다).

```
/workspace/vertex/graph/create?objectRid=ri.phonograph2-objects.main.object.abc
  &searchAroundFnRid=ri.function-registry.main.function.xyz
  &startTime=2020-02-15&endTime=2020-02-16
```

이 링크를 열면 새 그래프가 만들어지고, 객체 `abc`가 노드로 추가되며, 함수 `xyz`가 그 객체를 입력으로 실행되어 결과 객체가 추가되고, 시간 범위는 2020년 2월 15일부터 16일까지로 설정됩니다. `selectedTime`은 지정하지 않았으므로 `startTime`과 같은 값이 됩니다. UNIX 타임스탬프는 1970년 1월 1일 00:00:00 UTC부터 지난 시간을 센 숫자이고, 여기서는 밀리초 단위입니다.

> **중간 요약**: 새 그래프 URL에는 `selectObjectRid`, `objectRid`, `objectSetRid`, `searchAroundFnRid`(객체나 객체 집합 파라미터와 함께 필수)를 쓸 수 있고, 새 그래프와 기존 그래프 모두에 `selectedTime`, `startTime`, `endTime`을 쓸 수 있습니다. 시각은 밀리초 UNIX 타임스탬프나 ISO 형식입니다.

<a id="generate-a-vertex-graph-from-other-applications"></a>
## 다른 애플리케이션에서 Vertex 그래프 생성하기 (Generate a Vertex graph from other applications)

URL 파라미터를 설정했으면 이 링크를 사용해 다른 애플리케이션에서 미리 구성된 그래프를 생성할 수 있습니다. 예를 들어 Object Explorer의 Hyperlinks Widget을 사용하는 경우는 다음과 같습니다.

<img src="https://www.palantir.com/docs/resources/foundry/vertex/generate_graph_from_other_app-ui.jpg" alt="위젯에 링크 추가" width="400" />

## 정리

- URL 파라미터를 붙인 링크로 미리 채워진 Vertex 그래프를 생성할 수 있습니다.
- 새 그래프 URL(`/workspace/vertex/graph/create`)에서는 객체, 객체 집합, Search Around 함수 결과를 추가하고 특정 객체를 선택할 수 있습니다.
- 시간 관련 파라미터(`selectedTime`, `startTime`, `endTime`)는 새 그래프와 기존 그래프 모두에 적용됩니다.
- 이 링크를 Object Explorer의 Hyperlinks Widget 같은 곳에 넣어 다른 애플리케이션에서 그래프를 열 수 있습니다.
