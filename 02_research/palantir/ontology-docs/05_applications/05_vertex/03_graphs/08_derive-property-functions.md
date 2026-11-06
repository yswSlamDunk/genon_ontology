# 함수로 속성 파생하기 (Derive properties using Functions)

- 원문: https://www.palantir.com/docs/foundry/vertex/derive-property-functions/
- 사이드바 위치: Applications > Vertex > Graphs > Derive properties using Functions

이 페이지는 데이터셋에 저장되어 있지 않은 값을 함수(function)로 계산해 Vertex 그래프의 객체 속성처럼 보여 주는 파생 속성(derived property)을 설명합니다. 어떤 조건을 만족하는 함수가 파생 속성으로 쓰일 수 있는지, 그리고 노선별 항공편 취소율을 계산하는 예제를 다룹니다.

[함수(Functions)](../../../02_define-ontologies/04_functions/01_overview.md)를 사용해 객체에 **파생 속성(derived properties)을** 만들 수 있습니다. 파생 속성은 객체 뷰에 표시하거나, 확장 노드 레이블에 보여 주거나, 레이어 스타일 옵션에서 노드 색을 지정하는 데 사용할 수 있습니다.

다음 조건을 만족하는 함수라면 무엇이든 **파생 속성으로** 사용할 수 있습니다.

* 메서드가 함수로 내보내져 있습니다(TypeScript v1에서는 `@Function()` 데코레이터를 사용하고, TypeScript v2에서는 `export default`를 사용).
* 메서드가 `public`입니다.
* 메서드가 객체에서 값으로의 맵을 반환합니다(TypeScript v1에서는 `FunctionsMap<ObjectType, CustomType>`, TypeScript v2에서는 `Record<ObjectSpecifier<ObjectType>, CustomType>`).
* 맵의 모든 키는 객체입니다.
* 맵의 모든 값은 기본(primitive) 타입이거나, 각 필드가 기본 타입인 사용자 정의 타입입니다.
* 메서드가 릴리스용으로 태그되어 있습니다.
* 메서드가 단일 객체(예: `ExampleDataRoute`)가 아니라 객체 집합(object set, 예: `ExampleDataRoute[]` 또는 `ObjectSet<ExampleDataRoute>`)을 대상으로 동작합니다. 이렇게 하면 그래프의 모든 객체마다 함수가 따로 호출되지 않으며, 그렇게 따로 호출되면 큰 그래프에서 성능이 매우 느려질 수 있습니다.
* 메서드에 객체 집합 외의 다른 입력이 없습니다.

**설명**: 객체 집합을 받아 맵을 반환하게 하는 이유는 호출 횟수 때문입니다. 그래프에 Route 노드가 500개 있을 때 객체 하나를 받는 함수라면 500번 호출해야 하지만, 객체 집합을 받는 함수라면 한 번 호출로 `{Route1: 2.5, Route2: 0.0, ..., Route500: 7.1}` 같은 맵을 받아 각 노드에 값을 나눠 붙일 수 있습니다. 데이터베이스에서 행마다 쿼리를 하나씩 보내는 대신 `WHERE id IN (...)` 쿼리 하나로 한꺼번에 가져오는 것과 같은 이유입니다(이른바 N+1 쿼리 문제를 피하는 방법).

예:

```typescript
import { Function, FunctionsMap, Double } from "@foundry/functions-api";
import { ExampleDataRoute } from "@foundry/ontology-api";

export class VertexDerivedPropertyFunctions {
    @Function()
    public async flightCancellationPercentage(
        routes: ExampleDataRoute[],
    ): Promise<FunctionsMap<ExampleDataRoute, Double>> {
        const routeMap = new FunctionsMap<ExampleDataRoute, Double>();

        // 모든 노선의 항공편을 동시에 조회
        const allFlights = await Promise.all(
            routes.map((route) => route.flights.allAsync()),
        );

        for (let i = 0; i < routes.length; i++) {
            const route = routes[i];
            const flights = allFlights[i];
            const cancelledFlights = flights.filter(
                (flight) => flight.cancelled,
            );
            const cancellationPercentage =
                (cancelledFlights.length / flights.length) * 100;
            routeMap.set(route, cancellationPercentage);
        }

        return routeMap;
    }
}
```

**설명**: 위 코드는 원문의 TypeScript v1 예제입니다. 입력은 Route 객체 배열이고, 출력은 Route 객체를 키로, 취소율(%)을 값으로 하는 `FunctionsMap`입니다. `Promise.all`로 모든 노선의 `flights` 링크를 한꺼번에 조회한 뒤, 노선마다 `cancelled`가 참인 항공편 수를 전체 항공편 수로 나누고 100을 곱해 맵에 넣습니다(`routeMap.set(route, ...)`가 핵심 줄입니다). 예를 들어 어떤 노선에 항공편이 40편 있고 그중 2편이 취소되었다면 값은 `5.0`이며, Vertex에서는 이 값이 해당 Route 노드의 파생 속성으로 표시되거나 색 기준으로 쓰입니다.

(원문에는 같은 계산을 하는 TypeScript v2 버전 예제도 있습니다. v2에서는 `ObjectSet<ExampleDataRoute>`를 받아 `asyncIter()`로 순회하고, `Record<ObjectSpecifier<ExampleDataRoute>, Double>` 객체에 `route.$objectSpecifier`를 키로 값을 넣어 `export default` 함수로 반환합니다.)

## 정리

- 파생 속성은 함수로 계산한 값을 객체의 속성처럼 보여 주는 기능이며, 객체 뷰, 확장 노드 레이블, 노드 색 지정에 쓸 수 있습니다.
- 함수는 객체 집합 하나만 입력으로 받고, 객체를 키로 하고 기본 타입(또는 기본 타입 필드로 된 사용자 정의 타입)을 값으로 하는 맵을 반환해야 합니다.
- 함수는 내보내져 있고 `public`이며 릴리스 태그가 붙어 있어야 합니다.
- 객체 하나씩이 아니라 객체 집합 단위로 계산하게 해서 큰 그래프에서도 호출 횟수를 줄입니다.
