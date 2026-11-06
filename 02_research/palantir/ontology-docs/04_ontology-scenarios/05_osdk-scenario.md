# OSDK에서 시나리오 사용하기 (Use scenarios with OSDK)

- 원문: https://www.palantir.com/docs/foundry/ontology/osdk-scenario/
- 사이드바 위치: Ontology scenarios > Use scenarios with OSDK

이 페이지는 애플리케이션 코드에서 Ontology SDK(OSDK)를 사용해 시나리오를 만들고, 시나리오 안에서 객체를 읽고, 액션을 적용하고, 병합하고, 편집된 엔터티를 조회하는 방법을 다룹니다. Workshop 같은 화면 도구 없이 TypeScript나 Python 프로그램에서 직접 "가정(what-if) 분석"을 수행하려는 개발자를 위한 페이지입니다. 두 언어의 API가 같은 순서로 설명되어 있습니다.

**주의**: 실험적 기능(Experimental). [Ontology SDK(OSDK)](https://www.palantir.com/docs/foundry/ontology-sdk/overview/)의 시나리오 지원은 실험 단계이며 사용 중인 환경에서는 제공되지 않을 수 있습니다. 이 페이지에서 설명하는 API 표면(API surface)은 활발히 개발 중이며 바뀔 수 있다는 점에 유의하세요.

[Ontology SDK(OSDK)](https://www.palantir.com/docs/foundry/ontology-sdk/overview/)를 사용하면 애플리케이션 코드에서 직접 [온톨로지 시나리오](01_overview-ontology-scenario.md)를 만들고 다룰 수 있습니다. 시나리오 범위 클라이언트(scenario-scoped client)는 일반 OSDK 클라이언트와 똑같이 동작합니다. 읽는 모든 객체, 계산하는 모든 집계, 적용하는 모든 액션이 메인 온톨로지가 아니라 시나리오의 격리된 샌드박스를 기준으로 자동 평가됩니다.

시나리오 지원은 TypeScript OSDK와 Python OSDK 모두에서 제공됩니다. 아래 섹션에서는 각 언어로 다음 작업을 수행하는 방법을 설명합니다.

* 새 시나리오를 만들거나 기존 시나리오에 연결(attach)하기
* 시나리오 맥락에서 객체를 읽고 질의하기
* 시나리오 안에서 액션과 편집 적용하기
* 시나리오를 메인 온톨로지에 병합하기
* 시나리오 안에서 편집된 엔터티 목록 조회하기

**설명**: OSDK는 온톨로지의 객체 타입과 액션 타입을 프로그래밍 언어의 타입과 함수로 생성해 주는 SDK입니다. 예를 들어 `Restaurant` 객체 타입이 있으면 `Restaurant`라는 타입이 생기고, `addReview` 액션 타입이 있으면 호출 가능한 함수가 생깁니다. "시나리오 범위 클라이언트"는 같은 질의 코드를 그대로 쓰되, 모든 요청에 "이 시나리오 안에서 실행하라"는 정보가 붙는 클라이언트 객체라고 이해하면 됩니다.

<a id="typescript-osdk"></a>
## TypeScript OSDK

시나리오 지원은 `@osdk/client` `2.27.0` 버전 이상에서 제공됩니다. [Developer Console](https://www.palantir.com/docs/foundry/developer-console/create-application/)에서 이에 맞는 버전의 SDK를 생성하세요.

[커스텀 위젯(Custom widgets)](https://www.palantir.com/docs/foundry/custom-widgets/overview/)도 OSDK를 사용하므로 시나리오를 만들고 다룰 수 있습니다. 자세한 내용은 [위젯 세트에서 Ontology SDK(OSDK) 사용하기](https://www.palantir.com/docs/foundry/custom-widgets/use-osdk/)를 참고하세요.

<a id="create-or-attach-to-a-scenario"></a>
### 시나리오 만들기 또는 연결하기 (Create or attach to a scenario)

새 시나리오를 만들려면 `createScenario`를, RID로 기존 시나리오에 연결하려면 `withScenario`를 사용합니다. 두 함수 모두 시나리오 범위 클라이언트를 반환합니다.

```typescript
import { createScenario, withScenario } from "@osdk/client/unstable-do-not-use";

// 새 시나리오를 만듭니다. 플랫폼을 호출하므로 비동기입니다.
const scenario = await createScenario(client);

// 또는 RID로 기존 시나리오에 연결합니다. 동기 호출이며 네트워크 요청이 없습니다.
const existingScenario = withScenario(client, "ri.actions..scenario.0000-...");

// 저장하거나 공유할 시나리오 참조(RID)를 가져옵니다.
const scenarioRid: string = scenario.getScenarioReference();
```

**설명**: `createScenario`는 서버에 요청해 새 시나리오를 발급받으므로 `await`가 필요합니다. 반면 `withScenario`는 이미 알고 있는 RID를 클라이언트에 붙이기만 하므로 네트워크 호출이 없습니다. `getScenarioReference()`로 얻은 RID 문자열을 저장해 두면 나중에 같은 시나리오로 돌아올 수 있습니다.

기본 `client`가 브랜치로 설정되어 있으면, `createScenario`로 만든 새 시나리오는 그 브랜치를 기반으로 삼습니다.

[영구 시나리오 객체](03_persisted-scenario.md)로 저장된 시나리오에도 연결할 수 있습니다. 영구 시나리오 객체의 기본 키가 시나리오 참조이므로, 객체의 `$primaryKey`를 `withScenario`에 넘기면 됩니다.

(원문에는 객체 질의로 얻은 영구 시나리오 객체의 `$primaryKey`를 `withScenario`에 넘기는 짧은 예제 코드가 더 있습니다.)

<a id="query-objects-within-a-scenario"></a>
### 시나리오 안에서 객체 질의하기 (Query objects within a scenario)

시나리오 클라이언트는 일반 OSDK 클라이언트와 똑같은 방식으로 호출할 수 있습니다. 모든 읽기가 자동으로 시나리오 범위로 한정됩니다.

```typescript
import { Restaurant } from "@my-app/sdk";

// 시나리오 안에서 보이는 모습 그대로 객체 한 페이지를 불러옵니다.
const page = await scenario(Restaurant).fetchPage();

// 필터와 집계도 시나리오를 기준으로 평가됩니다.
const filtered = await scenario(Restaurant)
  .where({ numberOfReviews: { $gte: 100 } })
  .fetchPage();

const counts = await scenario(Restaurant).aggregate({
  $select: { $count: "unordered" },
});
```

**설명**: 일반 클라이언트라면 `client(Restaurant)`로 썼을 자리에 `scenario(Restaurant)`를 쓰는 것이 유일한 차이입니다. 두 번째 질의는 SQL의 `SELECT * FROM restaurant WHERE number_of_reviews >= 100`에 해당하고, 세 번째는 `SELECT COUNT(*)`에 해당합니다. 결과에는 시나리오 안에서 한 편집이 반영되어 있습니다.

<a id="apply-actions-within-a-scenario"></a>
### 시나리오 안에서 액션 적용하기 (Apply actions within a scenario)

시나리오 클라이언트를 통해 액션을 적용하면 편집이 시나리오의 샌드박스 안에 쌓입니다. 이 편집은 시나리오가 병합될 때까지 메인 온톨로지에 영향을 주지 않습니다.

```typescript
import { addReview } from "@my-app/sdk";

const result = await scenario(addReview).applyAction({
  restaurantId: "restaurantId",
  reviewRating: 5,
  reviewSummary: "It was great!",
});
```

**설명**: `addReview` 액션에 세 파라미터를 넘겨 실행합니다. 같은 코드를 `client(addReview)`로 실행하면 실제 온톨로지가 바뀌지만, `scenario(addReview)`로 실행하면 이 시나리오 안에서만 리뷰가 추가된 것으로 보입니다.

**주의**: 시나리오 안에서 액션을 적용할 때는 배치 액션(batch action)을 지원하지 않습니다. 또한 시나리오는 다른 시나리오 안에 중첩할 수 없고, 트랜잭션과 함께 쓸 수도 없습니다.

<a id="merge-a-scenario"></a>
### 시나리오 병합하기 (Merge a scenario)

시나리오를 병합하려면 **Apply Scenario** 규칙이 설정된 액션 타입을 아무것이나 적용하면 됩니다. 액션에 이 규칙을 추가하면 `scenarioReference` 타입의 시나리오 파라미터가 자동으로 노출됩니다. 그 파라미터 값으로 시나리오 클라이언트를 그대로 넘기면, OSDK가 자동으로 시나리오 참조로 변환합니다.

```typescript
import { applyScenario } from "@my-app/sdk";

// `applyScenario`는 Apply Scenario 규칙이 설정된 액션으로,
// `scenario`라는 이름의 시나리오 파라미터를 노출합니다.
await client(applyScenario).applyAction({ scenario });
```

**설명**: 병합 액션은 시나리오 클라이언트가 아니라 일반 `client`로 실행한다는 점이 핵심입니다. 메인 온톨로지에 반영하는 작업이기 때문입니다. `{ scenario }`는 `{ scenario: scenario }`의 축약 문법입니다.

액션과 파라미터 이름은 각자의 온톨로지에 따라 다릅니다. 액션 타입에 **Apply Scenario** 규칙을 설정하는 방법은 [시나리오 병합하기](04_merge-scenario.md)를 참고하세요.

<a id="list-edited-entities-within-a-scenario"></a>
### 시나리오 안에서 편집된 엔터티 조회하기 (List edited entities within a scenario)

시나리오 클라이언트는 시나리오 안에서 어떤 객체와 링크가 편집되었는지 찾는 메서드를 제공합니다. 이 결과는 희소(sparse) 식별자만 반환합니다. 즉, `$apiName`과 `$primaryKey` 필드만 채워져 있습니다. 전체 속성 값을 불러오려면 그 기본 키를 시나리오 클라이언트에 다시 넘겨 조회합니다.

<a id="edited-objects"></a>
#### 편집된 객체 (Edited objects)

`getEditedEntityTypes`로 어떤 객체 타입과 링크 타입이 바뀌었는지 찾은 다음, `getEditedEntities`로 특정 타입의 편집된 객체를 페이지 단위로 조회하거나 `editedEntitiesAsyncIter`로 스트리밍합니다.

```typescript
import { Restaurant } from "@my-app/sdk";

// 시나리오에서 편집된 객체 타입과 링크 타입을 찾습니다.
const { objectTypes, linkTypes } = await scenario.getEditedEntityTypes();

// 특정 객체 타입의 편집된 객체를 페이지 단위로 조회합니다.
const editedPage = await scenario.getEditedEntities(Restaurant, { pageSize: 500 });
for (const obj of editedPage.data) {
  console.log(obj.$apiName, obj.$primaryKey);
}

// 또는 편집된 객체 전체를 스트리밍합니다. 이터레이터가 자동으로 페이지를 넘기고 기본 키 기준으로 중복을 제거합니다.
for await (
  const obj of scenario.editedEntitiesAsyncIter(Restaurant, { pageSize: 500 })
) {
  console.log(obj.$primaryKey);
}
```

**설명**: 먼저 "무엇이 바뀌었나"를 타입 단위로 확인하고, 다음으로 해당 타입에서 바뀐 객체의 기본 키 목록을 얻는 2단계 구조입니다. 페이지 방식은 한 번에 최대 500개씩 가져오고 다음 페이지를 직접 요청해야 하며, `for await` 방식은 이터레이터가 페이지 넘김을 알아서 처리합니다.

편집된 객체의 전체 속성 값을 불러오려면 시나리오 클라이언트로 다시 조회합니다.

(원문에는 `editedPage.data`의 기본 키를 모아 `$primaryKey: { $in: keys }` 조건으로 다시 조회하는 예제 코드가 더 있습니다. SQL의 `WHERE id IN (...)`에 해당합니다.)

<a id="edited-links"></a>
#### 편집된 링크 (Edited links)

편집된 링크는 `getEditedLinkTypes`, `getEditedLinks`, `editedLinksAsyncIter`로 확인합니다. 편집된 링크 하나는 `source`, `target`, `linkType`으로 이루어진 방향 있는 세 쌍(directed triple)으로 반환됩니다. 다대다(many-to-many) 링크만 반환되며, 편집된 일대다(one-to-many) 링크는 외래 키를 가진 객체 타입에 대해 `getEditedEntities`를 호출할 때 드러납니다.

(원문에는 `sisterRestaurants` 링크 타입을 예로 편집된 링크 타입을 찾고, 페이지 단위로 조회하고, 스트리밍하는 예제 코드가 더 있습니다. 구조는 위의 편집된 객체 예제와 같습니다.)

**설명**: 일대다 링크는 "다" 쪽 테이블의 외래 키 열로 구현되므로, 링크를 바꾸면 실제로는 그 객체의 외래 키 속성이 바뀝니다. 그래서 편집된 객체 목록에 나타납니다. 반면 다대다 링크는 별도의 조인 테이블로 표현되므로 링크 단위로 따로 조회합니다. 예를 들어 Restaurant A와 B 사이에 sisterRestaurants 링크를 추가했다면 `(source: A, target: B, linkType: "sisterRestaurants")` 형태로 반환됩니다.

> **중간 요약**: TypeScript에서는 `createScenario`나 `withScenario`로 시나리오 클라이언트를 얻고, 일반 클라이언트처럼 질의하고 액션을 실행합니다. 병합은 Apply Scenario 규칙이 있는 액션을 일반 클라이언트로 실행해 시나리오를 넘기면 되고, 편집된 객체와 다대다 링크는 전용 메서드로 조회합니다.

<a id="python-osdk"></a>
## Python OSDK

시나리오 지원은 Python OSDK `2.209.0` 버전 이상에서 제공됩니다. 편집된 객체와 링크를 조회하려면 `2.221.0` 버전 이상이 필요합니다. 시나리오 지원은 베타 기능이므로 시나리오 코드는 반드시 `AllowBetaFeatures` 컨텍스트 안에서 실행해야 합니다.

<a id="create-or-attach-to-a-scenario"></a>
### 시나리오 만들기 또는 연결하기 (Create or attach to a scenario)

새 시나리오를 발급하려면 `ScenarioClient.create`를, RID로 기존 시나리오에 연결하려면 `ScenarioClient` 생성자를 사용합니다. 둘 다 시나리오 범위 클라이언트를 반환합니다.

```python
from foundry_sdk_runtime import AllowBetaFeatures
from osdk import FoundryClient, ScenarioClient, UserTokenAuth

with AllowBetaFeatures():
    # 새 시나리오를 만듭니다. 플랫폼을 호출해 시나리오를 발급받습니다.
    scenario_client = ScenarioClient.create(client)

    # 또는 RID로 기존 시나리오에 연결합니다.
    scenario_client = ScenarioClient(
        client, scenario_rid="ri.actions..scenario.0000-..."
    )

    # 저장하거나 공유할 시나리오 참조(RID)를 가져옵니다.
    scenario_rid = scenario_client.scenario_rid
```

**설명**: `with AllowBetaFeatures():` 블록은 이 안에서만 베타 API 호출을 허용하는 컨텍스트 매니저입니다. 나머지 흐름은 TypeScript 버전과 같습니다.

`ScenarioClient.create`로 만든 새 시나리오는 기본 `client`의 온톨로지와 브랜치를 상속합니다. `ScenarioClient`에 넘기는 기본 클라이언트 자체가 시나리오 클라이언트여서는 안 됩니다.

[영구 시나리오 객체](03_persisted-scenario.md)로 저장된 시나리오에도 연결할 수 있습니다. 영구 시나리오 객체의 기본 키가 시나리오 참조이므로, 객체의 기본 키를 `ScenarioClient` 생성자에 넘기면 됩니다.

(원문에는 `scenario_object.get_primary_key()`를 `scenario_rid` 인자로 넘기는 예제 코드가 더 있습니다.)

<a id="query-objects-within-a-scenario"></a>
### 시나리오 안에서 객체 질의하기 (Query objects within a scenario)

`scenario_client.ontology.objects`를 통해 객체를 읽고 질의합니다. 모든 읽기가 자동으로 시나리오 범위로 한정됩니다.

(원문에는 `scenario_client.ontology.objects.ExampleRestaurant.get("primaryKey")`로 객체 하나를 읽고, `.page(page_size=30)`으로 한 페이지를 읽는 예제 코드가 있습니다.)

<a id="apply-actions-within-a-scenario"></a>
### 시나리오 안에서 액션 적용하기 (Apply actions within a scenario)

시나리오 클라이언트를 통해 액션을 적용하면 편집이 시나리오의 샌드박스 안에 쌓입니다. 이 편집은 시나리오가 병합될 때까지 메인 온톨로지에 영향을 주지 않습니다.

(원문에는 `scenario_client.ontology.actions.add_review(...)`를 `ActionConfig(mode=ActionMode.VALIDATE_AND_EXECUTE)`와 함께 호출하는 예제 코드가 있습니다. TypeScript 예제와 같은 파라미터를 snake_case 이름으로 넘깁니다.)

<a id="merge-a-scenario"></a>
### 시나리오 병합하기 (Merge a scenario)

시나리오를 병합하려면 **Apply Scenario** 규칙이 설정된 액션 타입을 아무것이나 적용하면 됩니다. 액션에 이 규칙을 추가하면 `scenarioReference` 타입의 시나리오 파라미터가 자동으로 노출됩니다. 그 파라미터 값으로 시나리오 클라이언트(또는 그 `scenario_rid` 문자열)를 넘깁니다.

```python
from foundry_sdk_runtime.types import ActionConfig, ActionMode

with AllowBetaFeatures():
    # `apply_scenario`는 Apply Scenario 규칙이 설정된 액션으로,
    # `scenario`라는 이름의 시나리오 파라미터를 노출합니다. 액션과 파라미터 이름은
    # 각자의 온톨로지에 따라 다릅니다.
    client.ontology.actions.apply_scenario(
        action_config=ActionConfig(mode=ActionMode.VALIDATE_AND_EXECUTE),
        scenario=scenario_client,  # 또는 scenario=scenario_client.scenario_rid
    )
```

**설명**: TypeScript와 마찬가지로 병합은 시나리오 클라이언트가 아닌 기본 `client`로 실행합니다. `VALIDATE_AND_EXECUTE` 모드는 제출 조건 등을 검증한 뒤 통과하면 실행하라는 뜻입니다.

액션 타입에 **Apply Scenario** 규칙을 설정하는 방법은 [시나리오 병합하기](04_merge-scenario.md)를 참고하세요.

<a id="list-edited-entities-within-a-scenario"></a>
### 시나리오 안에서 편집된 엔터티 조회하기 (List edited entities within a scenario)

시나리오 클라이언트는 시나리오 안에서 어떤 객체와 링크가 편집되었는지 찾는 메서드를 제공합니다. 이 결과는 희소 식별자만 반환합니다. 즉, `object_api_name`과 `primary_key` 필드만 채워져 있습니다. 전체 속성 값을 불러오려면 그 기본 키를 시나리오 클라이언트에 다시 넘겨 조회합니다.

<a id="edited-objects"></a>
#### 편집된 객체 (Edited objects)

`get_edited_entity_types`로 어떤 객체 타입과 링크 타입이 바뀌었는지 찾은 다음, `get_edited_objects`로 특정 타입의 편집된 객체를 페이지 단위로 조회하거나 `iterate_edited_objects`로 스트리밍합니다.

(원문에는 TypeScript 예제와 같은 흐름의 Python 예제 코드가 있습니다. 동기 이터레이터 `iterate_edited_objects` 외에 비동기 이터레이터 `async_iterate_edited_objects`를 쓰는 예도 포함되어 있습니다.)

편집된 객체의 전체 속성 값을 불러오려면 시나리오 클라이언트로 다시 조회합니다. 삭제된 객체는 `None`을 반환할 수 있습니다.

(원문에는 `edited_page.data`의 각 기본 키로 `.get()`을 호출해 리스트로 모으는 예제 코드가 있습니다.)

<a id="edited-links"></a>
#### 편집된 링크 (Edited links)

편집된 링크는 `get_edited_link_types`, `get_edited_links`, `iterate_edited_links`로 확인합니다. 편집된 링크 하나는 `source`, `target`, `link_type`으로 이루어진 방향 있는 세 쌍으로 반환됩니다. 다대다 링크만 반환되며, 편집된 일대다 링크는 외래 키를 가진 객체 타입에 대해 `get_edited_objects`를 호출할 때 드러납니다.

(원문에는 `sisterRestaurants` 링크 타입을 예로 편집된 링크 타입을 찾고, 페이지 단위 조회, 동기 스트리밍, 비동기 스트리밍을 하는 예제 코드가 있습니다.)

> **중간 요약**: Python OSDK도 같은 기능을 제공하며, `AllowBetaFeatures` 컨텍스트 안에서 `ScenarioClient.create` 또는 `ScenarioClient(...)`로 시나리오 클라이언트를 얻습니다. 편집 목록 조회에는 `2.221.0` 이상이 필요하고, 동기와 비동기 이터레이터가 모두 있습니다.

## 정리

- OSDK의 시나리오 범위 클라이언트는 일반 클라이언트와 같은 방식으로 쓰지만, 모든 읽기, 집계, 액션이 시나리오 샌드박스 기준으로 실행됩니다.
- TypeScript는 `@osdk/client` 2.27.0 이상(`createScenario`, `withScenario`), Python은 2.209.0 이상(`ScenarioClient`, `AllowBetaFeatures` 필요)에서 지원합니다.
- 영구 시나리오 객체의 기본 키가 곧 시나리오 RID이므로, 그 값으로 기존 시나리오에 연결할 수 있습니다.
- 병합은 Apply Scenario 규칙이 있는 액션을 일반 클라이언트로 실행하면서 시나리오를 파라미터로 넘깁니다.
- 편집 목록 조회는 기본 키만 담긴 희소 결과를 주며, 다대다 링크만 링크로 조회되고 일대다 링크 변경은 객체 편집으로 나타납니다.
- 배치 액션, 시나리오 중첩, 트랜잭션과의 조합은 지원하지 않습니다.
