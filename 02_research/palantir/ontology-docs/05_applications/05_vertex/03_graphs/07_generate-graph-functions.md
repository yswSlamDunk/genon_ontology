# 함수로 그래프 생성하기 (Generate graphs using Functions)

- 원문: https://www.palantir.com/docs/foundry/vertex/generate-graph-functions/
- 사이드바 위치: Applications > Vertex > Graphs > Generate graphs using Functions

이 페이지는 TypeScript로 작성한 함수(function)를 Vertex의 Search Around로 사용하는 방법을 설명합니다. 링크 하나를 따라가는 기본 Search Around로는 표현하기 어려운 탐색(예: "N번 환승 안에 갈 수 있는 모든 공항")을 코드로 작성하고, 결과를 Vertex가 이해하는 정해진 반환 타입 `IGraphSearchAroundResultV1`으로 돌려주면 그래프에 노드와 간선이 추가됩니다.

[함수(Functions)](../../../02_define-ontologies/04_functions/01_overview.md)를 사용하면 하나 이상의 객체에서 시작해 결과 그래프를 반환하는 복잡한 **Search Around** 함수를 작성할 수 있습니다. 이 함수는 **Search Around** 도구 모음 메뉴, 오른쪽 클릭 메뉴, 또는 [URL 파라미터로 그래프를 만들 때](06_generate-graph-apps.md) 실행할 수 있습니다. 각 함수는 온톨로지 객체 타입이거나 온톨로지 객체 목록인 인수를 정확히 하나 가져야 하며, 아래에서 자세히 설명하는 반환 타입 `IGraphSearchAroundResultV1`을 가져야 합니다.

![UI](https://www.palantir.com/docs/resources/foundry/vertex/graph_generation_and_search_around-ui.jpg)

도구 모음이나 오른쪽 클릭 메뉴를 통해 사용할 때, 함수는 `Integer`, `Double`, `Float`, `string`, `boolean`, `Timestamp`, `Date` 타입의 추가 인수를 가질 수 있습니다. 이런 Search Around를 실행하면 사용자가 그 파라미터를 입력할 수 있는 양식이 생성됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/vertex/graph_generation_and_search_around-parameters.jpg" alt="파라미터" width="300" />

**설명**: 정리하면 함수 시그니처의 규칙은 "객체(또는 객체 목록) 인수 정확히 1개 + 선택적인 기본 타입 인수 여러 개, 반환은 `IGraphSearchAroundResultV1`"입니다. 예를 들어 `destinations(airport: Airport, distance: Integer)`는 객체 인수 `airport` 하나와 숫자 인수 `distance` 하나를 가지므로, 실행할 때 `distance`를 입력하는 양식이 나타납니다.

<a id="search-around-functions"></a>
### Search Around 함수 (Search Around functions)

**Search Around** 함수는 TypeScript 함수 저장소(repository)에서 작성합니다. 자세한 내용은 [함수 문서](../../../02_define-ontologies/04_functions/01_overview.md)를 참고하세요.

**Search Around** 함수는 반환 타입을 `IGraphSearchAroundResultV1` 또는 `Promise<IGraphSearchAroundResultV1>`으로 선언해야 합니다. Vertex는 반환 타입의 이름과 구조를 사용해 Search Around 함수를 찾아내므로, 반환 타입은 반드시 다음과 정확히 같게 선언해야 합니다.

```typescript
export interface IGraphSearchAroundResultV1 {
    directEdges?: IGraphSearchAroundResultDirectEdgeV1[];
    intermediateEdges?: IGraphSearchAroundResultIntermediateEdgeV1[];
    orphanObjectRids?: string[];
    objectRidsToGroup?: string[][];
    layout?: string;
}

export interface IGraphSearchAroundResultDirectEdgeV1 {
    sourceObjectRid: string;
    targetObjectRid: string;
    linkTypeRid?: string;
    label?: string;
    direction?: string;
}

export interface IGraphSearchAroundResultIntermediateEdgeV1 {
    sourceObjectRid: string;
    sourceToIntermediateLinkTypeRid?: string;
    intermediateObjectRid: string;
    intermediateToTargetLinkTypeRid?: string;
    targetObjectRid: string;
    label?: string;
    direction?: string;
}
```

**설명**: 이 코드는 함수가 반환할 결과의 모양을 정의하는 TypeScript 인터페이스 세 개입니다. 최상위 `IGraphSearchAroundResultV1`은 "직접 간선 목록, 중간 객체를 거치는 간선 목록, 연결 없는 객체 목록, 묶을 객체 그룹 목록, 레이아웃 이름"을 담는 객체입니다. 필드 이름 뒤의 `?`는 선택 필드라는 뜻이므로, 예를 들어 직접 간선만 반환하는 함수는 `{ directEdges: [...] }`만 돌려주면 됩니다. 간선은 객체 자체가 아니라 객체의 RID(Foundry 리소스 식별 문자열)로 양 끝을 지정합니다.

* `directEdges`는 그래프에서 두 객체 사이를 직접 잇는 간선으로 표시됩니다. 이 간선이 링크에 기반한 것이라면, 온톨로지에 있는 그 링크의 `linkTypeRid`를 제공해 간선을 따라 링크 타입의 표시 이름을 보여 주고 Vertex가 간선 방향을 알게 할 수 있습니다.
* `intermediateEdges`를 사용하면 이벤트나 다른 중간 객체를 바탕으로 두 객체 사이에 간선을 만들 수 있습니다. 중간 간선은 두 객체 사이의 간선으로 표시되며, 중간 객체는 간선 안에 그룹화됩니다. 같은 두 객체 사이에 많은 중간 간선이 반환되면 모든 중간 객체가 하나의 간선에 그룹화됩니다. 직접 간선과 마찬가지로, 표현하는 관계가 링크 쌍(출발 객체에서 중간 객체로 가는 링크 하나, 중간 객체에서 도착 객체로 가는 링크 하나)에 기반한다면 이 링크 타입 RID들을 제공할 수 있습니다. Vertex는 함수가 그래프에 추가하는 객체만 간선 안에 그룹화합니다. 따라서 이미 그래프에 있는 객체(함수에 입력으로 전달한 객체 포함)는 자기 자신의 노드로 남습니다.
* `orphanObjectRids`를 사용하면 응답 안의 다른 객체와 어떤 링크도 없는 객체를 반환할 수 있습니다. `directEdges`나 `intermediateEdges`의 간선에 참여하는 객체는 여기에 반환할 필요가 없습니다.
* `objectRidsToGroup`을 사용하면 그룹의 배열을 반환해 객체들을 하나의 노드로 묶을 수 있습니다. 각 그룹은 객체 RID의 배열입니다. 참고: 같은 RID를 여러 그룹에 넣으면 그 그룹들은 하나로 합쳐집니다.
* `label`을 사용하면 출발 객체와 도착 객체 사이에 생성되는 기능 링크(functional link)에 사용자 지정 레이블을 붙일 수 있습니다.
* `direction`을 사용하면 Search Around 함수가 만들어 내는 기능 링크의 방향을 바꿀 수 있습니다. 값은 `NONE`, `FORWARD`, `REVERSE` 중 하나여야 합니다. 생략하면 기본값은 `FORWARD`입니다. `linkTypeRid`가 있어서 나타나는 링크는 `direction`의 영향을 받지 않습니다.
* `layout`을 사용하면 결과 객체가 그래프에 추가될 때 사용할 레이아웃을 바꿀 수 있습니다. 값은 `auto`, `auto-grid`, `grid`, `linear-row`, `linear-column`, `circular` 중 하나여야 합니다. 생략하면 계층형(hierarchy) 레이아웃이 기본값입니다.
  * 이 옵션은 애플리케이션에서 Search Around를 직접 실행할 때만 사용할 수 있으며, 템플릿에서 그래프를 생성할 때는 사용할 수 없습니다.

**설명**: 직접 간선과 중간 간선의 차이를 구체적인 값으로 보면 다음과 같습니다. `{ sourceObjectRid: "SAN의 RID", targetObjectRid: "FAT의 RID" }`를 `directEdges`에 넣으면 SAN과 FAT 노드 사이에 선이 하나 그려집니다. `{ sourceObjectRid: "SAN", intermediateObjectRid: "항공편 F1", targetObjectRid: "FAT" }`과 `{ ..., intermediateObjectRid: "항공편 F2", ... }` 두 개를 `intermediateEdges`에 넣으면 SAN과 FAT 사이에 선이 하나 그려지고, 그 선 안에 F1과 F2가 묶입니다. 기능 링크는 온톨로지에 정의된 링크 타입이 아니라 함수가 계산해서 만든 연결을 말합니다.

> **중간 요약**: Search Around 함수는 객체 인수 하나(와 선택적인 기본 타입 인수)를 받아 `IGraphSearchAroundResultV1`을 반환하며, 이 타입은 정확히 문서대로 선언해야 Vertex가 인식합니다. 결과에는 직접 간선, 중간 객체를 담는 간선, 고립 객체, 그룹, 레이블, 방향, 레이아웃을 담을 수 있습니다.

<a id="tips-troubleshooting"></a>
## 팁과 문제 해결 (Tips & troubleshooting)

* 성능을 최대화하려면 모든 코드를 가능한 한 비동기로 작성해야 합니다.
* Vertex는 함수의 최신 게시 버전을 사용합니다. 함수를 게시하려면 원하는 브랜치나 커밋에 시맨틱 버전(예: `1.0.0`) 태그를 붙여야 합니다.
* 저장소는 함수에서 사용하려는 모든 온톨로지 객체와 링크에 접근할 수 있어야 합니다. 이는 **Repository Settings**의 **Ontology** 섹션에서 구성할 수 있습니다.
* 객체 타입과 그 백킹 데이터셋(backing dataset)이 저장소와 다른 프로젝트에 정의되어 있다면, 저장소가 들어 있는 프로젝트에 그 백킹 데이터셋과 객체 타입에 대한 참조(reference)가 있어야 합니다.

![문제 해결](https://www.palantir.com/docs/resources/foundry/vertex/graph_generation_and_search_around-troubleshoot.jpg)

**설명**: 비동기로 작성하라는 것은 링크를 여러 번 조회할 때 하나가 끝나기를 기다렸다가 다음을 시작하지 말고, `Promise.all`처럼 여러 조회를 동시에 보내라는 뜻입니다. 경로 100개의 항공편을 하나씩 조회하면 100번의 왕복 시간이 걸리지만, 동시에 보내면 대략 가장 느린 한 번의 시간만 걸립니다. 시맨틱 버전은 `주.부.수정`(MAJOR.MINOR.PATCH) 형식의 버전 번호 규칙입니다.

> **중간 요약**: 코드는 최대한 비동기로 작성하고, 함수는 시맨틱 버전 태그로 게시해야 Vertex가 최신 버전을 사용합니다. 저장소 설정에서 필요한 객체와 링크 접근을 허용하고, 다른 프로젝트의 리소스는 참조로 가져와야 합니다.

<a id="reference-examples"></a>
## 참고 예제 (Reference Examples)

다음 예제에는 **Search Around** 함수 두 개가 들어 있습니다.

첫 번째 함수 `allFlights`는 노선을 따라 운항하는 모든 항공편을 반환하며, 이 항공편들은 공항 사이의 간선 하나에 병합됩니다. 예를 들어 노선 "SAN -> FAT"에 대해 실행하면 다음 결과가 나옵니다.

![search\_around\_functions-all\_flights](https://www.palantir.com/docs/resources/foundry/vertex/search_around_functions-all_flights.jpg)

두 번째 함수 `destinations`는 사용자가 거리를 고르게 하고, 처음 공항에서 그 횟수 이내의 비행으로 갈 수 있는 모든 공항을 반환합니다. 예를 들어 공항 "\[ADK] Adak + Adak Island, AK"에 대해 거리 2로 실행하면 다음 결과가 나옵니다.

![search\_around\_functions-destinations](https://www.palantir.com/docs/resources/foundry/vertex/search_around_functions-destinations.jpg)

아래는 TypeScript v2로 작성한 `allFlights` 함수입니다(인터페이스 선언은 앞과 같으므로 줄였습니다).

```typescript
import { ObjectSet, Osdk } from "@osdk/client";
import { Integer } from "@osdk/functions";
import { ExampleDataAirport, ExampleDataRoute } from "@ontology/sdk";

// IGraphSearchAroundResultV1 등 인터페이스 선언은 위와 동일 (생략)

export async function allFlights(
    routes: ObjectSet<ExampleDataRoute>,
): Promise<IGraphSearchAroundResultV1> {
    const intermediateEdges: IGraphSearchAroundResultIntermediateEdgeV1[] = [];

    for await (const route of routes.asyncIter()) {
        // 노선의 출발 공항과 도착 공항을 링크로 조회
        const [departure] = await Array.fromAsync(
            route.$link.departingAirport.asyncIter(),
        );
        const [arrival] = await Array.fromAsync(
            route.$link.arrivingAirport.asyncIter(),
        );
        if (!departure || !arrival) continue;

        // 노선의 항공편 각각을 출발 공항과 도착 공항 사이의 중간 객체로 추가
        for await (const flight of route.$link.flights.asyncIter()) {
            intermediateEdges.push({
                sourceObjectRid: departure.$rid!,
                intermediateObjectRid: flight.$rid!,
                targetObjectRid: arrival.$rid!,
            });
        }
    }

    return { intermediateEdges };
}

export default allFlights;
```

**설명**: 입력은 Route 객체 집합(`ObjectSet<ExampleDataRoute>`)이고 출력은 `intermediateEdges`만 채운 `IGraphSearchAroundResultV1`입니다. 각 노선에 대해 `route.$link.departingAirport`와 `route.$link.arrivingAirport`로 링크된 공항을 하나씩 가져오고, `route.$link.flights`로 링크된 항공편을 모두 순회하면서 `{출발 공항, 항공편, 도착 공항}` 세 RID를 중간 간선으로 넣습니다. 같은 두 공항 사이의 중간 간선은 하나의 간선으로 합쳐지므로, 그래프에는 SAN과 FAT 사이에 선 하나가 그려지고 그 안에 항공편이 묶입니다. 핵심 줄은 `intermediateEdges.push({...})`입니다.

(원문에는 TypeScript v1 버전 예제도 있으며, 그 안에 `allFlights`의 v1 구현과 함께 `destinations` 함수 구현이 들어 있습니다. `destinations`는 시작 공항에서 `distance` 횟수만큼 반복하며 각 공항의 노선과 도착 공항을 `Promise.all`로 동시에 조회하고, 출발 공항과 도착 공항 사이를 `directEdges`로 추가하는 너비 우선 탐색 방식의 코드입니다.)

> **중간 요약**: `allFlights`는 노선마다 출발 공항, 항공편, 도착 공항을 중간 간선으로 반환해 항공편을 공항 사이 간선 하나에 묶고, `destinations`는 거리 파라미터만큼 노선을 따라가며 직접 간선을 반환합니다.

## 정리

- 함수로 복잡한 Search Around를 작성할 수 있으며, 도구 모음, 오른쪽 클릭 메뉴, URL 파라미터에서 실행할 수 있습니다.
- 함수는 객체(또는 객체 목록) 인수를 정확히 하나 가지고, 정해진 구조의 `IGraphSearchAroundResultV1`을 반환해야 합니다.
- 결과의 `directEdges`는 두 객체를 직접 잇고, `intermediateEdges`는 중간 객체를 간선 안에 묶으며, `orphanObjectRids`, `objectRidsToGroup`, `label`, `direction`, `layout`으로 표시 방식을 조정합니다.
- 추가 기본 타입 인수는 실행 시 입력 양식으로 나타납니다.
- 함수는 시맨틱 버전 태그로 게시하고, 저장소에 필요한 온톨로지 접근 권한을 설정해야 합니다.
