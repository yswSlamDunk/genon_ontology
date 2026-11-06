# 지도의 Search Around (Search Arounds for the map)

- 원문: https://www.palantir.com/docs/foundry/map/integrate-searcharounds/
- 사이드바 위치: Applications > Map > Integrate data for the map > Search Arounds for the map

이 페이지는 Map 애플리케이션에서 선택한 객체와 관련된 다른 객체를 찾아 지도에 불러오는 Search Around 기능을 설정하는 방법을 다룹니다. 링크 타입을 그대로 따라가는 방식, 중간 객체를 거치는 두 단계 방식(link merge), 그리고 TypeScript 함수(function)로 탐색 로직을 직접 작성하는 방식을 차례로 설명합니다. 지도 위에서 "이 공장과 거래하는 공급업체는 어디인가"처럼 관계를 따라가며 분석하려면 이 설정이 필요합니다.

Search Around는 링크 또는 함수 기반의 검색으로, 사용자가 관련된 객체를 탐색할 수 있게 해 줍니다. [Control Panel에서 Search Around 한도를 설정](../09_configuration/02_control-panel.md#data-loading)할 수 있습니다.

**설명**: Search Around는 데이터베이스 관점에서 보면 "선택한 행에서 외래 키를 따라가 조인된 행을 가져오는" 동작입니다. 예를 들어 Factory 객체 하나를 선택하고 Search Around를 실행하면, Factory와 링크 타입으로 연결된 Supplier 객체들이 조회되어 지도에 추가됩니다.

<a id="link-search-arounds"></a>
## 링크 Search Around (Link Search Arounds)

사용자는 어떤 지리공간(geospatial) 객체에서든 그 객체와 링크로 연결된 지리공간 객체로 Search Around를 할 수 있습니다. 자세한 내용은 [링크 타입 만들기](../../../02_define-ontologies/02_object-and-link-types/06_link-types/02_create-link-type.md)를 참고하세요.

**설명**: 지리공간 객체란 위치 정보(좌표, 도형 등)를 담은 속성(property)을 가진 객체를 말합니다. 지도에 그릴 수 있으려면 이런 위치 속성이 있어야 합니다.

> **중간 요약**: 가장 기본적인 Search Around는 온톨로지에 정의된 링크 타입을 따라 연결된 지리공간 객체를 지도에 불러오는 것입니다.

<a id="link-merged-search-arounds"></a>
## 링크 병합 Search Around (Link merged Search Arounds)

Map 애플리케이션은 두 단계 Search Around를 실행할 수 있습니다. 이는 어떤 지리공간 객체가 중간(intermediary) 객체(지리공간 객체가 아니어도 됨)를 거쳐 다른 지리공간 객체와 링크되어 있는 경우입니다.

* 중간 객체는 두 객체 사이의 관계를 나타낼 수 있습니다. 예를 들어 `Factory` 객체와 `Supplier` 객체가 `Supply Contract` 객체를 통해 연결되어 있을 수 있습니다. 이 경우 Search Around를 실행하면 지도에 공장에서 공급업체로 이어지는 호(arc)가 표시되며, 이 호가 공급 계약을 나타냅니다.
* 중간 객체는 두 객체가 함께 관련된 이벤트일 수도 있습니다. 예를 들어 `Customer` 객체가 `Delivery` 이벤트를 통해 `Distribution Center` 객체와 링크되어 있을 수 있습니다. 이 경우 배송 이벤트는 호를 따라 이동하는 원으로 표시됩니다. 원의 위치는 이벤트의 시작 시각과 종료 시각, 그리고 현재 선택된 타임스탬프를 바탕으로 호 위에서 보간(interpolate)되어 정해집니다.

![링크 병합 호 예시](https://www.palantir.com/docs/resources/foundry/map/integrate-objects-linkmerge-arc-example.png)

**설명**: 데이터베이스로 표현하면 `Factory`, `Supply Contract`, `Supplier` 세 테이블이 있고 `Supply Contract` 테이블이 `factory_id`와 `supplier_id` 두 외래 키를 가진 다대다(many-to-many) 연결 테이블인 구조입니다. 링크 병합은 이 연결 테이블을 따로 보여 주지 않고 `Factory`에서 `Supplier`로 바로 가는 관계처럼 지도에 그려 줍니다. 보간은 예를 들어 배송 시작이 09:00, 도착이 11:00이고 현재 선택 시각이 10:00이면 원을 호의 중간 지점에 그리는 식으로 위치를 계산하는 것입니다.

링크 병합 Search Around에 사용할 객체를 설정하는 방법은 두 가지입니다.

* 중간 객체를 링크 병합 객체로 지정합니다. 이렇게 하면 이 객체 타입 자체는 Search Around 목록에 절대 나타나지 않고, 이 객체를 거쳐 이어지는(transitive) 링크만 나타납니다.
* 병합할 특정 링크 경로(link traversal)를 지정합니다. 중간 객체의 관계 중 일부만 링크 병합해야 할 때 이 방법을 사용합니다.

<a id="set-an-intermediary-object-type-to-always-link-merge"></a>
### 중간 객체 타입을 항상 링크 병합하도록 설정하기

중간 객체 타입이 항상 링크 병합되도록 지정하려면, 중간 객체 타입의 **Capabilities** 탭에 있는 **Search Around** 섹션에서 **Link merge always**를 켭니다. 이렇게 하면 이 객체 타입 자체는 Search Around 목록에 절대 나타나지 않고, 이 객체를 거쳐 이어지는 링크만 나타납니다.

![Ontology Manager의 링크 병합 설정.](https://www.palantir.com/docs/resources/foundry/map/oma-capabilities-link-merge.png)

예를 들어 중간 객체 타입이 `Delivery`이고 양쪽 객체 타입이 `Distribution Center`와 `Customer`라면, `Distribution Center`를 선택해 Search Around를 할 때 목록에 `Delivery`는 나타나지 않고 `Customer (via Delivery)`가 나타납니다. 아래 예시를 참고하세요.

![링크 병합 객체가 포함된 Search Around 메뉴.](https://www.palantir.com/docs/resources/foundry/map/integrate-objects-searcharound-linkmerge-example.png)

<a id="set-specific-link-traversals-to-be-link-merged"></a>
### 특정 링크 경로를 링크 병합하도록 설정하기

특정 링크 경로를 링크 병합하도록 지정하려면, 중간 객체 타입의 **Capabilities** 탭에 있는 **Search Around** 섹션에서 **Incoming links to merge**(병합할 들어오는 링크)와 **Outgoing links to merge**(병합할 나가는 링크)를 모두 지정합니다.

![Ontology Manager의 들어오는/나가는 링크 병합 설정.](https://www.palantir.com/docs/resources/foundry/map/oma-capabilities-link-merge-incoming-outgoing.png)

예를 들어 `Supplier` 객체 타입에서 `Delivery` 객체 타입을 거쳐 `Distribution Center` 객체 타입으로 Search Around를 할 수 있게 하려면, `Delivery` 객체 타입을 중간 객체로 설정하고 `Delivery <-> Supplier` 링크를 **Incoming links to merge**로, `Delivery <-> Distribution Center` 링크를 **Outgoing links to merge**로 선택합니다. 그러면 `Supplier`를 선택해 Search Around를 할 때 목록에 `Distribution Centers (via Delivery)`가 선택지로 나타납니다.

링크 경로의 양쪽 방향이 모두 Search Around 목록에 나타나게 하려면(예를 들어 `Suppliers`에서는 `Distribution Centers (via Delivery)`가, `Distribution Centers`에서는 `Suppliers (via Delivery)`가 모두 나타나게 하려면), 해당 링크들을 **Incoming links to merge**와 **Outgoing links to merge** 양쪽에 모두 설정해야 합니다.

**설명**: Incoming과 Outgoing은 탐색 방향을 정합니다. "Incoming에 넣은 링크로 중간 객체에 들어와서, Outgoing에 넣은 링크로 나간다"는 규칙이므로, `Supplier`에서 출발하면 `Delivery <-> Supplier`로 들어와 `Delivery <-> Distribution Center`로 나갑니다. 반대 방향 탐색까지 허용하려면 두 링크를 양쪽 목록에 다 넣어야 하는 이유가 여기에 있습니다.

> **중간 요약**: 중간 객체를 거치는 두 단계 관계는 링크 병합으로 한 번에 탐색할 수 있습니다. 중간 객체 타입 전체를 항상 병합(**Link merge always**)하거나, 들어오는 링크와 나가는 링크를 지정해 특정 경로만 병합할 수 있습니다.

<a id="search-around-functions"></a>
## Search Around 함수 (Search Around functions)

**Map Search Around** [함수](../../../02_define-ontologies/04_functions/01_overview.md)를 작성하면 Map에서 강력한 **Map Search Around**를 만들 수 있습니다. 이를 통해 선택된 객체를 입력으로 받아 온톨로지를 탐색하고, 수행 중인 특정 분석에 관련되거나 유용한 모든 객체를 돌려주는 TypeScript 함수를 작성할 수 있습니다.

**Map Search Around** 함수는 다음을 포함할 수 있는 데이터 구조를 반환합니다.

* `objectRids`: 객체들. 지도에 추가됩니다.
* `edges`: 간선(edge)들. 각 간선은 출발 객체, 도착 객체, 그리고 선택적으로 중간 객체들을 포함합니다. 출발 객체와 도착 객체는 지도에 추가되고 그 사이에 호가 그려지며, 호를 선택하면 중간 객체들이 목록으로 표시됩니다.
* `measures`: 시계열 측정값(Time Series Measures). [타임라인](../05_time/03_timeline.md)에 추가됩니다.

**설명**: RID(Resource Identifier)는 Foundry에서 객체 같은 리소스를 전역적으로 유일하게 가리키는 식별 문자열입니다. 함수는 객체 자체가 아니라 이 RID 목록을 돌려주고, Map이 RID로 객체를 불러와 그립니다. `edges`는 그래프 자료구조의 간선 목록과 같은 형태로, (출발 노드, 도착 노드) 쌍에 부가 정보를 붙인 것입니다.

<a id="implement-a-map-search-around-function"></a>
### Map Search Around 함수 구현하기

**Map Search Around** 함수는 TypeScript 함수 저장소(repository)에서 개발합니다. 자세한 내용은 [함수 문서](../../../02_define-ontologies/04_functions/01_overview.md)를 참고하세요.

<a id="return-type"></a>
#### 반환 타입 (Return type)

**Map Search Around** 함수는 반환 타입을 `Promise<IMapSearchAroundResults>`로 선언해야 합니다. Map 애플리케이션은 반환 타입의 이름과 구조를 보고 Search Around 함수를 찾아내므로, 반환 타입을 반드시 아래와 똑같이 선언해야 합니다.

```typescript
export interface IMapSearchAroundResults {
    objectRids?: string[];
    edges?: IMapSearchAroundEdge[];
    measures?: IMapSearchAroundMeasure[];
}

export interface IMapSearchAroundEdge {
    sourceObjectRid: string;
    targetObjectRid: string;
    intermediaryObjectRids?: string[];
}

export interface IMapSearchAroundMeasure {
    objectRids: string[];
    measureId: string;
}

```

**설명**: 세 개의 TypeScript 인터페이스가 반환값의 모양을 정의합니다. `?`가 붙은 필드는 생략할 수 있으므로, 객체만 돌려주려면 `{ objectRids: [...] }`만 반환해도 됩니다. Map은 함수 목록에서 "반환 타입 이름이 `IMapSearchAroundResults`이고 이 구조를 가진 함수"를 골라 Search Around 메뉴에 올리기 때문에, 이름이나 필드명을 바꾸면 Map이 함수를 인식하지 못합니다.

<a id="parameters"></a>
#### 파라미터 (Parameters)

Map Search Around 함수는 객체 파라미터를 하나(그리고 오직 하나만) 포함해야 하며, 다음 중 하나일 수 있습니다.

* **단일 객체:** 지정한 타입의 객체 하나가 선택되었을 때 이 Search Around 함수가 Search Around 메뉴에 나타납니다. 예:

```typescript
public exampleSearchAround(object: ExampleObjectType) { ...
```

* **객체 배열:** 지정한 타입의 객체가 몇 개든 선택되었을 때 이 Search Around 함수가 Search Around 메뉴에 나타납니다. 예:

```typescript
public exampleSearchAround(objects: ExampleObjectType[]) { ...
```

* **객체 집합(object set):** 지정한 타입의 객체가 몇 개든 선택되었을 때 이 Search Around 함수가 Search Around 메뉴에 나타납니다. 예:

```typescript
public exampleSearchAround(objectSet: ObjectSet<ExampleObjectType>) { ...
```

Map Search Around 함수는 선택적으로 다음 스칼라 타입의 추가 파라미터를 몇 개든 포함할 수 있습니다: `string`, `boolean`, `Integer`, `Long`, `Float`, `Double`, `LocalDate`, `Timestamp` (자세한 내용은 [스칼라 타입](../../../02_define-ontologies/04_functions/04_types-reference.md#scalar-types) 참고). 사용자가 추가 파라미터가 있는 Search Around 함수를 실행하면 파라미터 값을 입력하라는 안내가 나타납니다. 예:

```typescript
public exampleSearchAround(objectSet: ObjectSet<ExampleObjectType>, stringParameter: string, timestampParameter: Timestamp) { ...
```

**설명**: 객체 배열은 이미 메모리에 불러온 객체 목록이고, 객체 집합은 "어떤 객체들인지에 대한 정의(쿼리)"여서 실제로 객체를 불러오기 전에 필터나 링크 탐색을 이어 붙일 수 있습니다. 많은 객체가 선택될 수 있다면 객체 집합을 쓰는 편이 효율적입니다. 위 마지막 예에서는 사용자가 실행할 때 `stringParameter`와 `timestampParameter` 값을 입력하게 됩니다.

<a id="tips-troubleshooting"></a>
### 팁과 문제 해결 (Tips & troubleshooting)

* 성능을 최대화하려면 모든 코드를 가능한 한 비동기로 작성해야 합니다. 함수 코드에서 객체를 불러올 때는 항상 `all()`과 `get()` 대신 `allAsync()`와 `getAsync()`를 사용하고, `await` 문은 가능한 한 적게 사용하세요.
* Map 애플리케이션은 함수의 가장 최근 게시(published) 버전을 사용합니다. 함수를 게시하려면 원하는 브랜치나 커밋에 semver 호환 버전(예: 1.0.0)으로 태그를 붙여야 합니다.
* 저장소는 함수에서 사용하려는 모든 온톨로지 객체와 링크에 접근할 수 있어야 합니다. 이는 저장소 **Settings**의 **Ontology** 섹션에서 설정할 수 있습니다.
* 객체 타입과 그 백킹 데이터셋이 저장소와 다른 프로젝트에 정의되어 있다면, 저장소가 들어 있는 프로젝트에 해당 백킹 데이터셋과 객체 타입에 대한 참조(reference)를 추가해야 합니다.

**설명**: `await`를 줄이라는 말은 독립적인 조회 여러 개를 하나씩 기다리지 말고 `Promise.all([...])`로 묶어 동시에 실행하라는 뜻입니다. 조회 3개가 각각 1초 걸린다면 순서대로 기다리면 3초, 동시에 실행하면 약 1초가 걸립니다. semver(Semantic Versioning)는 `주.부.수` 형식(예: 1.0.0)의 버전 표기 규칙입니다.

<a id="examples"></a>
### 예시 (Examples)

이 예제 코드는 오픈 소스 샘플 데이터를 바탕으로 한 Search Around 함수 세 개를 담고 있습니다.

* `airportsRelatedObjects`: 공항 집합과 관련된 여러 객체를 반환합니다. 공항 분석용 지도 템플릿에서 사용할 수 있습니다.
* `nearbyAirports`: 지리공간 검색을 수행해 주어진 거리 안에 있는 다른 공항을 찾습니다. 이 함수는 선택적인 거리 파라미터를 받으므로, 사용자가 함수를 실행할 때 거리를 입력할 수 있습니다.
* `routesBetweenAirports`: 공항 집합이 주어지면, 그 공항들 사이에서만 오가는 모든 노선을 반환합니다.

아래는 이 중 `nearbyAirports` 함수를 대표 예제로 남긴 것입니다(import 문과 반환 타입 선언은 위와 같습니다).

```typescript
export class MapSearchAroundFunctions {

    /**
     * 선택한 공항에서 지정한 킬로미터(기본값 50) 이내에 있는 모든 공항을 반환
     */
    @Function()
    public async nearbyAirports(airport: ExampleDataAirport, distanceKm?: Integer): Promise<IMapSearchAroundResults> {
        const point = airport.airportLocation;
        const distance = Distance.ofKilometers(distanceKm ?? 50);

        if (point === undefined) {
            return {};
        }

        const nearbyAirports = await Objects.search()
            .exampleDataAirport()
            .filter(airportFilter => airportFilter.airportLocation.withinDistanceOf(point, distance))
            .allAsync();

        const objectRids = nearbyAirports.map(o => o.rid!);

        return {
            objectRids,
        };
    }
}
```

(원문에는 링크 두 개를 동시에 탐색해 활주로와 노선 객체를 돌려주는 `airportsRelatedObjects`, 선택한 공항 사이의 노선을 `edges`로 돌려주는 `routesBetweenAirports` 예제 코드가 더 있습니다.)

**설명**: 입력은 공항 객체 하나(`airport`)와 선택적 정수 `distanceKm`입니다. 공항의 위치 속성 `airportLocation`을 꺼내고, 거리가 주어지지 않으면 `??` 연산자로 50km를 기본값으로 씁니다. 위치가 없으면 빈 결과 `{}`를 반환합니다. 핵심 줄은 `Objects.search().exampleDataAirport().filter(... withinDistanceOf(point, distance))`로, 모든 공항 객체 중 이 지점에서 지정 거리 안에 있는 것만 거르는 지리공간 필터입니다. SQL로 치면 `SELECT * FROM airport WHERE distance(location, :point) <= :distance`에 해당합니다. 마지막으로 결과 객체들의 RID를 `objectRids`에 담아 반환하면 Map이 이 공항들을 지도에 추가합니다. 원문의 `routesBetweenAirports`는 노선 객체를 지도에 점으로 두는 대신 출발 공항과 도착 공항을 `sourceObjectRid`, `targetObjectRid`로 하고 노선을 `intermediaryObjectRids`에 넣어 호로 그리게 합니다.

> **중간 요약**: Map Search Around 함수는 객체(또는 객체 배열, 객체 집합) 파라미터 하나와 선택적 스칼라 파라미터를 받아 `IMapSearchAroundResults`를 반환하는 TypeScript 함수입니다. 반환 타입 이름과 구조를 정확히 맞춰야 Map이 인식하며, 게시된 최신 버전이 사용됩니다.

## 정리

- Search Around는 선택한 객체에서 관련 객체를 찾아 지도에 불러오는 기능이며, 한도는 Control Panel에서 설정합니다.
- 링크 Search Around는 링크 타입을 그대로 따라갑니다.
- 링크 병합 Search Around는 중간 객체를 거치는 두 단계 관계를 호로 그리며, 중간 객체 타입의 **Capabilities** 탭에서 **Link merge always** 또는 들어오는/나가는 링크 지정으로 설정합니다.
- Search Around 함수는 `Promise<IMapSearchAroundResults>`를 반환하는 TypeScript 함수로, 객체, 간선, 시계열 측정값을 돌려줄 수 있습니다.
- 함수는 비동기 호출을 최대한 묶어 쓰고, semver 태그로 게시하며, 저장소에 필요한 온톨로지 접근 권한과 프로젝트 참조를 갖춰야 합니다.
