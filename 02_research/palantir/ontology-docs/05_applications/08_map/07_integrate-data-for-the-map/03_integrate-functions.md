# 지도의 함수 기반 스타일 지정 (Functions for the map)

- 원문: https://www.palantir.com/docs/foundry/map/integrate-functions/
- 사이드바 위치: Applications > Map > Integrate data for the map > Functions for the map

이 페이지는 함수(function)로 객체마다 값을 계산해 지도 위 객체의 색을 바꾸는 "함수 기반 스타일 지정"을 다룹니다. 객체에 저장된 속성(property)만으로는 표현할 수 없는 값(예: 노선별 결항률)을 그때그때 계산해 시각화하고 싶을 때 사용합니다. 함수가 갖춰야 할 형태와, Workshop Map 위젯에서 추가 인수를 넘기는 방법을 설명합니다.

원문 페이지 제목은 "함수 기반 스타일 지정(Function-based styling)"입니다.

[함수](../../../02_define-ontologies/04_functions/01_overview.md)를 지도에서 사용해 객체에 대한 동적인 값을 생성할 수 있습니다. 이 값은 **Selection** 패널에 표시할 수 있고, [값 기반 스타일 지정(value-based styling)](../06_visualize-ontology-data/01_visualize-objects.md#value-based-styling)을 통해 지도 위 객체의 색을 칠하는 데 적용할 수 있습니다.

<a id="define-a-function-for-styling"></a>
## 스타일 지정용 함수 정의하기 (Define a function for styling)

함수를 지도의 스타일 지정에 사용하려면 다음 조건을 만족해야 합니다.

* 배열 또는 객체 집합(object set) 중 하나인 인수를 하나만 가져야 합니다.
* 키는 입력 인수에 들어 있는 객체이고 값은 문자열 또는 숫자 타입인 맵(map)을 반환해야 합니다.
  * [TypeScript v1](../../../02_define-ontologies/04_functions/12_typescript-v1/01_typescript-v1-getting-started.md)에서는 `FunctionsMap`을 사용해 맵을 반환합니다.
  * [TypeScript v2](../../../02_define-ontologies/04_functions/10_typescript-v2/01_typescript-v2-getting-started.md)에서는 `ObjectSpecifier` 키를 가진 `Record`를 사용해 맵을 반환합니다.

**설명**: 여기서 맵은 지도가 아니라 키-값 자료구조(해시 맵, 딕셔너리)를 뜻합니다. 예를 들어 노선 객체 3개를 입력받으면 `{ 노선A: 12.5, 노선B: 0, 노선C: 3.2 }`처럼 객체마다 숫자 하나를 짝지은 결과를 돌려주고, Map은 이 숫자에 따라 각 노선의 색을 정합니다.

예:

```typescript tab="TypeScript v1"
import { Function, FunctionsMap, Double } from "@foundry/functions-api";
import { ExampleDataRoute } from "@foundry/ontology-api";

export class DerivedPropertyFunctions {
    @Function()
    public async flightCancellationPercentage(routes: ExampleDataRoute[]): Promise<FunctionsMap<ExampleDataRoute, Double>> {
        const routeMap = new FunctionsMap<ExampleDataRoute, Double>();

        const allFlights = await Promise.all(routes.map(route => route.flights.allAsync()));

        for (let i = 0; i < routes.length; i++) {
            const route = routes[i];
            const flights = allFlights[i];
            const cancelledFlights = flights.filter(flight => flight.cancelled);
            const cancellationPercentage = (cancelledFlights.length / flights.length) * 100;
            routeMap.set(route, cancellationPercentage);
        }

        return routeMap;
    }
}
```

(원문에는 같은 계산을 `Record<ObjectSpecifier<ExampleDataRoute>, Double>`로 반환하는 TypeScript v2 버전도 있습니다. v2에서는 `routeMap[route.$objectSpecifier] = cancellationPercentage;`처럼 객체 지정자를 키로 값을 넣고, 함수를 `export default`로 내보냅니다.)

**설명**: 입력은 노선(`ExampleDataRoute`) 객체 배열입니다. 먼저 `Promise.all`로 모든 노선의 링크된 항공편(`route.flights`)을 동시에 불러옵니다. 그다음 노선마다 결항된(`cancelled`가 참인) 항공편 수를 전체 항공편 수로 나누고 100을 곱해 결항률(%)을 계산하고, `routeMap.set(route, ...)`으로 노선과 결항률을 짝지어 넣습니다. 출력은 노선별 결항률이 담긴 `FunctionsMap`입니다.

**주의**: Map 애플리케이션은 객체를 배치(batch) 단위로 나누어 함수에 넘기며, 배치에 들어 있는 모든 객체에 대해 값이 반환되기를 기대합니다. 레이어의 모든 객체가 한 번의 함수 호출에서 첫 번째 인수로 한꺼번에 제공되지 *않습니다*. 함수는 객체가 어떻게 배치로 나뉘든 일관된 결과를 내야 합니다. 즉, 어떤 객체에 대해서든 같은 배치에 어떤 객체들이 함께 들어 있는지와 관계없이 같은 값을 반환해야 합니다.

**설명**: 예를 들어 레이어에 노선이 1,000개 있으면 Map이 함수를 여러 번(예: 200개씩 5번) 호출할 수 있습니다. 따라서 "배치 안에서 결항률이 가장 높은 노선에 1을 매긴다"처럼 같은 배치의 다른 객체에 따라 값이 달라지는 계산은 배치 구성에 따라 결과가 바뀌므로 피해야 합니다. 위 예제는 각 노선의 값이 그 노선의 항공편만으로 계산되므로 이 조건을 만족합니다.

> **중간 요약**: 스타일 지정용 함수는 객체 배열 또는 객체 집합 하나를 받아 객체별 문자열 또는 숫자 값을 담은 맵을 반환해야 하며, 배치 구성과 무관하게 객체마다 같은 값을 내야 합니다.

<a id="pass-additional-arguments-to-functions"></a>
## 함수에 추가 인수 전달하기 (Pass additional arguments to functions)

Workshop Map 위젯에서 스타일 지정용 함수를 사용할 때, 함수는 주된 객체 입력 외에 추가 인수를 받을 수 있습니다.

추가 인수를 사용할 때도 첫 번째 인수는 항상 값을 계산해 반환해야 하는 대상 객체를 지정합니다. 위젯이 이 첫 번째 인수의 값은 자동으로 제공하며, 화면에는 추가 인수만 표시됩니다. 위젯 설정에서 변수(variable)를 선택해 추가 인수의 값을 지정할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/styling-functions.png" alt="Workshop Map 위젯에서 스타일 지정 함수에 추가 인수를 넘기는 설정." width="350" />

**설명**: Workshop의 변수는 모듈 안에서 위젯끼리 값을 주고받는 저장소입니다. 예를 들어 함수에 `minFlights: Integer` 인수를 추가하고, 이를 사용자가 입력 위젯에서 바꾸는 변수에 연결하면 사용자가 값을 바꿀 때마다 지도 색이 다시 계산됩니다.

## 정리

- 함수로 객체별 동적 값을 계산해 **Selection** 패널에 보여 주거나 값 기반 스타일 지정으로 색을 칠할 수 있습니다.
- 함수는 배열 또는 객체 집합 인수 하나를 받고, 객체를 키로 하는 문자열 또는 숫자 값의 맵을 반환해야 합니다(v1은 `FunctionsMap`, v2는 `Record`와 `ObjectSpecifier`).
- Map은 객체를 배치로 나눠 함수를 호출하므로 결과가 배치 구성에 의존하면 안 됩니다.
- Workshop Map 위젯에서는 첫 번째 인수 외의 추가 인수를 변수로 지정해 넘길 수 있습니다.
