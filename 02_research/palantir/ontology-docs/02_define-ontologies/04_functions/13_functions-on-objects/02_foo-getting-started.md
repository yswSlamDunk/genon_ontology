# 객체 함수 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/functions/foo-getting-started/
- 사이드바 위치: Define Ontologies > Functions > Functions on objects > Getting started

이 페이지는 온톨로지 객체를 입력으로 받는 함수(function)를 처음 만들어 보는 튜토리얼입니다. 함수 저장소로 객체 타입, 링크 타입, 인터페이스를 가져오는 방법부터, 객체를 받아 값을 돌려주는 함수 작성, Live Preview에서 테스트, 게시까지 한 번의 흐름으로 안내합니다.

<a id="getting-started-with-functions-on-objects"></a><a id="prerequisites"></a>
## 객체 함수 시작하기 (Getting started with functions on objects)

함수의 핵심 기능 가운데 하나는 Foundry 온톨로지에 통합된 데이터에 쉽게 접근할 수 있다는 점입니다. 온톨로지는 조직의 데이터를 의미 중심으로 모델링(semantic modeling)하므로, 구조화된 데이터에 접근하고 여러 사용 사례에 걸쳐 로직을 재사용하기 쉽습니다.

<a id="import-ontology-types"></a><a id="prerequisites"></a>
### 사전 준비 (Prerequisites)

이 튜토리얼은 TypeScript 저장소를 만들고 설정했다고 가정합니다. 아직 하지 않았다면 먼저 [시작하기](../03_getting-started.md) 튜토리얼을 완료하십시오.

<a id="add-an-object-backed-function"></a><a id="import-ontology-types"></a>
### 온톨로지 타입 가져오기 (Import Ontology types)

함수에서 사용하려는 모든 객체 타입, 인터페이스, 링크 타입은 저장소가 들어 있는 프로젝트(Project)로 가져와야 합니다. **Resource Imports** 사이드바를 선택하면 프로젝트로 가져온 객체 타입이 표시됩니다.

![온톨로지 가져오기 사이드 패널](https://www.palantir.com/docs/resources/foundry/functions/ontology-import-side-panel.png)

객체 타입을 더 가져오려면 **Resource Imports** 사이드바에서 **Add** 버튼을 선택해야 합니다. 아직 온톨로지가 선택되지 않았다면 온톨로지를 선택하라는 안내가 나타납니다. 가져온 온톨로지 타입이 하나라도 있으면 선택된 온톨로지가 자동으로 결정됩니다.

온톨로지를 선택하면 검색 모달이 나타납니다. 표시되는 온톨로지 내용은 조직에서 사용할 수 있는 객체 타입에 따라 다릅니다. 먼저 몇 개의 객체 타입과 그것들을 연결하는 링크 타입을 선택해 보십시오. 이 예제에서는 Airport와 Flight 객체, 그리고 둘 사이의 링크 타입을 가져옵니다.

![온톨로지 가져오기 예시](https://www.palantir.com/docs/resources/foundry/functions/ontology-import-example.png)

**Add** 버튼 아래의 **Interfaces**를 선택하면 온톨로지 인터페이스도 가져올 수 있습니다.

!["Add" 드롭다운 아래에 있는 인터페이스 가져오기 옵션.](https://www.palantir.com/docs/resources/foundry/functions/interface-import-example.png)

**Confirm selection**(선택 확인)을 선택하면 온톨로지 타입을 프로젝트로 가져옵니다. 새로 가져온 객체 타입과 링크 타입을 반영하도록 코드 바인딩을 다시 생성하기 위해 Code Assist가 자동으로 재시작됩니다.

TypeScript v1 저장소에서는 이제 `@foundry/ontology-api` 패키지에서 온톨로지 타입을 import할 수 있습니다. 비공개 온톨로지(private Ontology)를 사용한다면 패키지 이름은 대신 `@foundry/ontology-api/<ontology-api-name>`이 됩니다.

TypeScript v2 저장소에서는 온톨로지 타입을 가져온 뒤 [Ontology SDK를 생성하고 설치](../10_typescript-v2/03_typescript-v2-migration.md#generate-the-ontology-sdk)하라는 안내가 나타납니다. 함수를 작성하기 전에 이 단계를 완료하십시오. 가져온 타입은 Ontology SDK가 설치된 뒤에만 코드에서 사용할 수 있으며, `@ontology/sdk` 패키지에서 import합니다.

**참고**: 비공개 온톨로지(Private Ontologies). 비공개 온톨로지를 사용한다면 이후의 모든 TypeScript v1 예제에서 `@foundry/ontology-api`를 `@foundry/ontology-api/your-private-ontology-api-name-here`로 바꾸십시오.

`@foundry/ontology-api` 패키지는 TypeScript v1 함수에 해당합니다. TypeScript v2 저장소에서는 `@ontology/sdk`에서 온톨로지 타입을 import하기 전에 Ontology SDK를 생성하고 설치해야 합니다. 절차는 [Ontology SDK 생성하기](../10_typescript-v2/03_typescript-v2-migration.md#generate-the-ontology-sdk)를 참고하십시오.

**설명**: 가져오기(import)는 두 단계로 나뉩니다. 먼저 Resource Imports에서 "이 프로젝트가 Airport, Flight 타입을 사용한다"고 등록하고, 그다음 그 등록 정보를 바탕으로 TypeScript 코드(바인딩)가 생성됩니다. TypeScript v1은 Code Assist 재시작 시 `@foundry/ontology-api` 패키지에 바인딩이 자동으로 채워지고, TypeScript v2는 Ontology SDK라는 패키지를 별도로 생성하고 설치하는 단계를 거쳐 `@ontology/sdk`로 제공됩니다.

> **중간 요약**: 함수에서 쓸 객체 타입, 링크 타입, 인터페이스는 Resource Imports 사이드바의 Add로 프로젝트에 가져와야 합니다. TypeScript v1은 `@foundry/ontology-api`, TypeScript v2는 Ontology SDK를 설치한 뒤 `@ontology/sdk`에서 타입을 import합니다.

<a id="add-an-object-backed-function"></a><a id="test-in-live-preview"></a>
### 객체 기반 함수 추가하기 (Add an object-backed function)

다음으로, 방금 가져온 객체 타입을 사용하는 함수를 작성합니다. 코드는 사용할 수 있는 객체 타입, 속성(property), 링크 타입에 따라 달라집니다. **Code** 탭으로 돌아가서 방금 추가한 객체 타입 가운데 하나를 import해 보십시오.

```typescript tab="TypeScript v1"
import { Airport } from "@foundry/ontology-api";
```

(원문에는 같은 import를 `@ontology/sdk`에서 하는 TypeScript v2 버전도 있습니다.)

그런 다음 그 객체를 입력으로 받는 함수를 작성합니다. TypeScript v2에서는 객체 타입 인스턴스가 `@osdk/client` 패키지의 `Osdk.Instance` 타입으로 감싸지며, 각 함수는 `src/functions` 아래에 함수 이름을 딴 파일의 default export가 됩니다.

```typescript tab="TypeScript v1"
@Function()
public myObjectFunction(airport: Airport) {
    airport.
}
```

(원문에는 `export default function myObjectFunction(airport: Osdk.Instance<Airport>)` 형태의 TypeScript v2 버전도 있습니다.)

Code Assist가 시작되면 `airport.`만 입력해도 사용할 수 있는 속성과 링크 타입의 자동 완성 목록이 나타납니다.

![자동 완성](https://www.palantir.com/docs/resources/foundry/functions/autocomplete.png)

이 예제에서는 [템플릿 문자열 ↗](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals#syntax)을 사용해 Airport의 `city`와 `country` 필드를 사람이 읽기 쉬운 위치 문자열로 합칩니다.

```typescript tab="TypeScript v1"
import { Function } from "@foundry/functions-api";
import { Airport } from "@foundry/ontology-api";

export class MyFunctions {

    @Function()
    public airportLocation(airport: Airport): string {
        return `${airport.city}, ${airport.country}`;
    }
}
```

(원문에는 같은 함수의 TypeScript v2 버전도 있습니다. `src/functions/airportLocation.ts` 파일에서 `@ontology/sdk`의 `Airport`와 `@osdk/client`의 `Osdk`를 import하고, `export default function airportLocation(airport: Osdk.Instance<Airport>): string`으로 같은 템플릿 문자열을 반환합니다.)

**설명**: 입력은 Airport 객체 하나, 출력은 문자열입니다. 예를 들어 `city`가 "Seoul", `country`가 "South Korea"인 Airport 객체를 넘기면 `"Seoul, South Korea"`를 돌려줍니다. TypeScript v1에서는 클래스 안의 메서드에 `@Function()` 데코레이터를 붙여 함수로 등록하고, 파라미터 타입 `Airport`가 바로 자동 생성된 코드 바인딩입니다. TypeScript v2에서는 클래스와 데코레이터 대신 파일 하나에 함수 하나를 default export하고, 파라미터 타입을 `Osdk.Instance<Airport>`로 적는다는 점이 다릅니다.

여러분의 온톨로지를 바탕으로 API를 실험해 보고, 객체 타입을 기반으로 값을 반환하는 함수를 작성해 보십시오.

> **중간 요약**: 가져온 객체 타입을 파라미터 타입으로 쓰면 자동 완성으로 속성과 링크에 접근할 수 있습니다. 예제 함수는 Airport 객체의 `city`와 `country`를 합친 문자열을 반환합니다.

<a id="publish-the-new-function"></a><a id="test-in-live-preview"></a>
### Live Preview에서 테스트하기 (Test in live preview)

**functions helper**(함수 도우미)를 열고 **Live Preview**로 전환한 뒤, 위에서 작성한 함수를 선택합니다. 객체 기반 함수를 Live Preview에서 실행하려면 객체 타입의 백킹 데이터소스(backing datasource)를 가져와야 합니다. **Run** 옵션 옆의 경고 아이콘을 선택하십시오.

![도우미의 데이터소스 가져오기](https://www.palantir.com/docs/resources/foundry/functions/helper-datasource-import.png)

그런 다음 대화 상자에서 객체 타입의 백킹 데이터소스를 가져옵니다.

![도우미의 데이터소스 가져오기 대화 상자](https://www.palantir.com/docs/resources/foundry/functions/helper-datasource-import-dialog.png)

데이터소스를 가져온 뒤 객체를 하나 고르고 **Run**을 선택하면 결과를 볼 수 있습니다.

![객체 함수를 미리보기로 실행한 도우미 화면](https://www.palantir.com/docs/resources/foundry/functions/helper-preview-run-foo.png)

**주의**: Live Preview 권한(Live preview permissions). Live Preview에서 객체 타입에 대한 권한은 [각 객체 타입 밑에 있는 백킹 데이터소스에 대한 TypeScript 저장소의 권한](../07_function-management/06_permissions.md#object-loading-permissions)으로 결정됩니다. [알림을 생성하는 함수](../09_language-agnostic-features/03_configure-notifications.md#configure-notifications)를 테스트할 때는 수신자의 권한이 적용되지 않습니다. 그래서 알림을 생성하는 함수가 Live Preview에서는 성공하더라도 Foundry의 다른 곳에서 액션으로 사용될 때는 실패할 수 있습니다.

[액션에 알림 구성하기](../../03_action-types/12_side-effects/02_notifications.md)에 대해 자세히 알아보십시오.

**설명**: Live Preview는 아직 게시하지 않은 코드를 저장소 안에서 바로 실행해 보는 기능입니다. 이때 객체 데이터를 읽는 주체는 "저장소"이므로, 실제 사용자가 아니라 저장소가 백킹 데이터셋을 읽을 수 있는지가 기준이 됩니다. 실제 운영 환경에서는 함수를 실행한 사용자의 권한이 기준이 되므로, 미리보기에서 되던 동작이 운영에서 권한 문제로 실패할 수 있다는 점을 염두에 두어야 합니다.

<a id="next-steps"></a><a id="publish-the-new-function"></a>
### 새 함수 게시하기 (Publish the new function)

코드를 커밋하고 **Branches** 탭에서 새 태그를 게시하면 새 함수가 게시됩니다. 함수가 게시되면 **functions helper**로 테스트할 수 있습니다.

![게시된 객체 함수를 실행한 도우미 화면](https://www.palantir.com/docs/resources/foundry/functions/helper-run-foo.png)

함수가 게시되면 플랫폼 전체의 다른 애플리케이션에서 사용하기 시작할 수 있습니다.

<a id="next-steps"></a>
### 다음 단계 (Next steps)

이 튜토리얼은 객체 함수로 할 수 있는 일의 겉면만 살짝 다루었습니다. 더 알아보려면 다음 자료를 참고하십시오.

* 객체로 할 수 있는 일은 [객체 API 문서 (TSv1)](06_api-objects-links.md)를 참고하십시오.
* 필요할 때 객체를 검색하고 집계(aggregation)하는 방법은 [객체 집합 문서 (TSv1)](07_api-object-sets.md)를 읽어 보십시오.
* TypeScript v2와 Python은 [언어별 객체 API](01_functions-on-objects.md#object-apis-by-language)에서 해당 언어의 레퍼런스를 찾아보십시오.
* [플랫폼에서 함수를 사용하는 방법](../08_function-consumption/01_use-functions.md)을 알아보십시오.

## 정리

- 함수에서 쓸 객체 타입, 링크 타입, 인터페이스는 Resource Imports 사이드바에서 프로젝트로 가져오며, 그러면 코드 바인딩이 생성됩니다.
- TypeScript v1은 `@foundry/ontology-api`, TypeScript v2는 Ontology SDK 설치 후 `@ontology/sdk`에서 타입을 import합니다.
- 객체 타입을 파라미터로 받는 함수를 작성하면 자동 완성으로 속성과 링크에 접근할 수 있습니다.
- Live Preview로 실행하려면 백킹 데이터소스를 가져와야 하며, 권한은 저장소 기준이라 운영 환경과 다를 수 있습니다.
- 커밋 후 Branches 탭에서 태그를 게시하면 다른 애플리케이션에서 함수를 사용할 수 있습니다.
