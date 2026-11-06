# 사용자 편집이 적용되는 방식 (How user edits are applied)

- 원문: https://www.palantir.com/docs/foundry/object-edits/how-edits-applied/
- 사이드바 위치: Ontology architecture > Object edits and materializations > How user edits are applied

이 페이지는 사용자가 액션(Action)으로 객체를 수정했을 때 그 편집(edit)이 객체 데이터베이스에 어떻게 반영되고, 어디에 영구 저장되며, 원본 데이터소스의 갱신과 충돌할 때 어떤 값이 최종 값이 되는지를 설명합니다. 온톨로지의 객체는 데이터셋에서 오는 값과 사용자가 직접 바꾼 값이 섞여 만들어지므로, 이 규칙을 알아야 화면에 보이는 객체 상태를 예측할 수 있습니다.

사용자 편집은 아래 스크린샷처럼 Ontology Manager의 **Datasources** 탭에 있는 **Edits** 토글로 켜고 끌 수 있습니다.

![객체 편집(Object Edits) 토글](https://www.palantir.com/docs/resources/foundry/object-edits/edits.png)

<a id="edit-objects-via-actions"></a>
## 액션으로 객체 편집하기 (Edit objects via Actions)

이 섹션은 온톨로지가 액션을 통한 객체 편집을 어떻게 관리하는지 설명합니다.

액션이 객체, 링크, 또는 객체 집합(object set)에 적용되면, 데이터 수정 로직은 객체 데이터베이스의 인덱스에 즉시 적용되고, 주기적으로 Funnel이 소유하고 관리하는 Foundry 데이터셋 형태의 영구 저장소로 플러시(flush)됩니다. 자세한 내용은 [사용자 편집의 영구 저장](#persistent-storage-of-user-edits) 문서에서 확인할 수 있습니다.

**설명**: 여기서 "인덱스"는 객체를 빠르게 조회하기 위해 객체 데이터베이스가 유지하는 검색용 사본입니다. 편집은 먼저 이 인덱스에 반영되어 곧바로 조회 결과에 나타나고, 나중에 일정 주기로 묶여서 데이터셋(파일 기반의 영구 저장소)에 기록됩니다. "플러시"는 메모리나 큐에 쌓여 있던 변경 내용을 영구 저장소에 써 넣는 동작을 뜻합니다.

<a id="user-edits-on-live-data"></a>
### 실시간 데이터에 대한 사용자 편집 (User edits on live data)

액션이 실행되면 Actions 서비스는 수정 명령을 Funnel 서비스로 보냅니다. 이 명령은 여러 사용자의 동시 편집을 지원하기 위해 오프셋 추적(offset tracking) 기능이 있는 Funnel 관리 큐에 저장됩니다. Object Storage v2는 모든 객체 타입과, 조인 테이블을 가진 모든 다대다(many-to-many) 링크 타입에 대해 이 오프셋을 추적합니다. 오프셋은 객체 데이터베이스의 실시간 인덱싱된 데이터에 적용됩니다. 온톨로지 쿼리 과정에서 일어나는 객체 읽기가 사용자 수정이 전송된 이후에 발생한다면, 그 객체 읽기에는 사용자 편집이 반드시 포함됩니다.

**설명**: 큐(queue)는 먼저 들어온 항목을 먼저 처리하는 자료구조이고, 오프셋(offset)은 큐에 쌓인 항목의 순번입니다. 예를 들어 편집 명령 세 개가 큐에 오프셋 101, 102, 103으로 들어갔다면, 인덱스가 "103번까지 반영했다"는 사실을 기록해 두는 식입니다. 이렇게 순번을 추적하면 편집을 보낸 직후의 읽기가 그 편집을 놓치지 않도록 보장할 수 있습니다. 이를 흔히 "자기가 쓴 내용은 바로 읽을 수 있다(read-your-writes)" 일관성이라고 부릅니다.

<a id="how-to-discardwipedelete-existing-user-edits"></a>
### 기존 사용자 편집을 버리거나 지우는 방법 (How to discard/wipe/delete existing user edits)

이미 사용자 편집이 들어 있는 데이터는 추가 사용자 편집으로만 갱신할 수 있습니다. 단일 사용자 편집이나 삭제를 직접 되돌리는 메커니즘은 없으며, 추가 사용자 편집(예: 객체 액션)으로 객체를 갱신하거나 객체를 다시 만드는 방법밖에 없습니다.

상황에 따라서는 모든 객체의 상태를 입력 데이터소스와 똑같이 되돌리기 위해 기존 사용자 편집을 전부 버리고 싶을 수 있습니다. 예를 들어 객체 타입을 운영 환경에 출시하기 전에, 테스트 중에 적용된 사용자 편집을 모두 삭제하고 싶을 수 있습니다.

Object Storage v2는 사용자 편집을 마이그레이션하기 위한 [스키마 마이그레이션 프레임워크](05_schema-migrations.md)를 제공합니다. ["drop all edits"](05_schema-migrations.md#list-of-supported-schema-migrations-in-osv2) 명령을 사용하면 객체 타입의 기존 사용자 편집을 모두 버릴 수 있습니다. 이 마이그레이션 명령은 Ontology Manager의 **Datasources** 탭, **Edits** 섹션에 있는 **Delete edits** 버튼을 클릭해 적용할 수 있습니다.

![객체 편집 삭제](https://www.palantir.com/docs/resources/foundry/object-edits/drop_edits.png)

Object Storage v1(Phonograph)은 스키마 마이그레이션을 지원하지 않지만, 객체 타입에서 라이트백(writeback) 데이터셋 설정을 제거하면 기존 사용자 편집이 모두 삭제되므로 이를 우회 방법으로 쓸 수 있습니다.

> **중간 요약**: 액션의 편집은 Funnel 큐를 거쳐 객체 데이터베이스 인덱스에 즉시 반영되고, 편집 직후의 읽기에는 그 편집이 반드시 보입니다. 개별 편집을 되돌리는 기능은 없고, OSv2에서는 "drop all edits" 마이그레이션(**Delete edits** 버튼)으로 전체 편집을 버릴 수 있습니다.

<a id="ontology-entity-version-control"></a>
## 온톨로지 엔터티 버전 관리 (Ontology entity version control)

액션을 적용하는 과정에서는 액션 검증, [함수(Functions)](../../02_define-ontologies/03_action-types/11_function-backed-actions/01_function-actions-overview.md), 액션 [부수 효과(side effect)](../../02_define-ontologies/03_action-types/12_side-effects/01_side-effects-overview.md) 등 여러 목적으로 객체 타입 정의와 객체 인스턴스를 불러옵니다. 액션을 적용하는 동안 객체 인스턴스가 바뀔 수 있으므로, 잠재적인 데이터 정확성 문제(예: 잘못된 버전의 객체에 액션을 적용하는 문제)를 피하려면 트랜잭션성(transactionality)을 보장하는 것이 중요합니다.

온톨로지에는 객체 타입과 객체 인스턴스 양쪽의 버전 일관성을 확인하는 메커니즘이 있으며, 그 동작은 Object Storage v1(Phonograph)과 Object Storage v2에서 서로 다릅니다.

**설명**: 트랜잭션성은 데이터베이스 수업에서 배우는 트랜잭션의 성질(특히 일관성과 격리성)과 같은 문제를 다룹니다. 예를 들어 액션이 객체 A를 읽어 검증한 뒤 편집을 쓰기 전에 다른 사용자가 A를 바꿨다면, 검증은 옛날 A를 기준으로 통과했는데 편집은 새 A 위에 쓰이게 됩니다. 이를 막기 위해 "읽을 때의 버전"과 "쓸 때의 버전"이 같은지 비교하는 방식이 낙관적 동시성 제어(optimistic concurrency control)이며, 아래에서 나오는 `StaleObject` 오류는 이 비교가 실패했을 때 발생합니다.

<a id="entity-version-control-between-front-end-consumers-and-the-actions-server"></a>
### 프런트엔드 소비자와 Actions 서버 사이의 엔터티 버전 관리 (Entity version control between front-end consumers and the Actions server)

사용자가 [액션 폼](../../02_define-ontologies/03_action-types/02_getting-started.md#edit-parameters)에서 객체 속성 값을 버전 `{V1, V2, V3, ...}`으로 불러오는 상황을 생각해 봅시다. 프런트엔드 소비자 애플리케이션은 그 객체 속성 값을 담아 Actions 서버의 `/apply` 엔드포인트를 호출하지만, 이 요청에는 버전이 포함되지 않습니다. 요청을 받은 Actions 서버는 `/apply` 엔드포인트 안에서 객체를 버전 `{V1', V2', V3', ...}`으로 불러옵니다. 프런트엔드에서 불러온 버전 `{V1, V2, V3, ...}`과 Actions 서버가 불러온 버전 `{V1', V2', V3', ...}`이 항상 같다는 보장은 없습니다.

**설명**: 즉, 사용자가 폼을 열어 둔 사이에 다른 사람이 객체를 바꾸면, 사용자가 화면에서 본 값과 서버가 실제로 처리하는 객체 값이 다를 수 있다는 뜻입니다. 이 구간의 버전 차이는 검사되지 않습니다.

<a id="entity-version-control-within-the-actions-server"></a>
### Actions 서버 내부의 엔터티 버전 관리 (Entity version control within the Actions server)

<a id="object-storage-v1-phonograph-planned-deprecation"></a>
#### Object Storage v1 (Phonograph) \[지원 중단 예정]

**주의**: 지원 중단 예정(Planned deprecation). Object Storage v1(Phonograph)은 개발 단계상 [지원 중단 예정](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으며 2026년 6월 30일 이후에는 사용할 수 없습니다. [객체 타입과 링크 타입을 Object Storage v2로 마이그레이션](../01_overview-and-getting-started/03_osv1-osv2-migration.md)하세요. 자세한 내용은 [Upgrade Assistant](https://www.palantir.com/docs/foundry/upgrade-assistant/overview/)의 `Migrate object types and many-to-many link types from Object Storage v1 to v2` 조치 항목을 참고하세요. 워크플로의 OSv1에서 OSv2로의 마이그레이션에 관해 질문이 있으면 Palantir Support에 문의하세요.

Object Storage v1(Phonograph)에서는 Actions 서버가 불러온 객체의 버전을 추적하고, 액션 실행 내내 캐시에서 같은 버전을 불러옵니다. Object Storage v1(Phonograph)에 사용자 편집을 적용할 때는 요청에 객체 버전이 포함됩니다. 그러면 Object Storage v1(Phonograph)은 객체 버전 중 하나라도 바뀌었는지 확인하고, 변경이 감지되면 `StaleObject` 오류를 던집니다.

이런 검사는 Actions 서버 안에서 전반적인 일관성을 보장합니다. 예를 들어 Object Storage v1은 액션이 동기식 [웹훅(webhook)](../../02_define-ontologies/03_action-types/12_side-effects/04_webhooks.md) 생성, 실행, 검증, 편집 적용을 모두 같은 버전의 객체에 대해 수행하도록 보장합니다. 하지만 속성 수준의 객체 변경은 검사하지 않으므로, 객체의 관련 없는 속성에 대한 사용자 편집 때문에도 `StaleObject` 충돌이 발생할 수 있습니다.

<a id="object-storage-v2"></a>
#### Object Storage v2

Object Storage v2에서는 Actions 서버가 Funnel 서비스에 사용자 편집을 보내기 전에 자체적으로 객체 버전 검사를 수행하지만, Object Storage v1(Phonograph)에 비해 서버가 수집한 버전 중 제한된 일부만 검사합니다.

Actions 서버는 편집을 만드는 데 직접 사용된 객체의 버전만 검사합니다. 예를 들어 어떤 객체 `A`의 속성 하나를 객체 `B`에 복사했다면 `A`의 버전이 검사 대상이 되며, 이 버전들은 편집된 객체의 버전과만 대조됩니다.

이 동작 덕분에 `StaleObject` 충돌의 빈도는 줄어들지만, 그 대가로 OSv2의 보장은 더 약해집니다. Object Storage v2에서 Actions 서비스는 액션 `/apply` 내내 항상 같은 버전의 객체를 불러오지만, 편집 생성 외의 목적으로 읽은 객체가 액션 진행 중에 바뀌지 않았다는 것은 보장하지 않습니다.

**설명**: 예를 들어 액션이 객체 C를 읽어 "C의 상태가 Open일 때만 실행"이라는 검증에만 쓰고, 편집은 객체 D에만 만든다고 합시다. OSv1에서는 C가 액션 도중 바뀌면 `StaleObject` 오류가 나지만, OSv2에서는 C가 편집 생성에 직접 쓰이지 않았으므로 그 변경이 검사되지 않습니다. 충돌은 덜 나지만, 엄밀한 일관성이 필요한 액션이라면 이 차이를 고려해야 합니다.

<a id="cross-backend-actions"></a>
#### 교차 백엔드 액션 (Cross-backend Actions)

액션 타입이 OSv1과 OSv2의 객체를 동시에 수정하면 "교차 백엔드(cross-backend)" 액션으로 간주됩니다. 이 경우 Actions 서비스는 다음을 검사합니다.

* OSv1에서 읽었거나 편집한 모든 객체
* OSv2에서 편집한 모든 객체

> **중간 요약**: 프런트엔드 폼과 서버 사이의 버전 차이는 검사되지 않습니다. OSv1은 액션이 읽은 모든 객체의 버전을 검사해 강한 일관성을 주지만 불필요한 `StaleObject` 충돌이 잦고, OSv2는 편집 생성에 직접 쓰인 객체만 검사해 충돌은 적지만 보장이 약합니다.

<a id="persistent-storage-of-user-edits"></a>
## 사용자 편집의 영구 저장 (Persistent storage of user edits)

객체 데이터베이스의 인덱싱된 데이터는 모두 일시적(ephemeral)인 것으로 간주되므로, 모든 온톨로지 데이터는 다른 방식으로 영구 저장해야 합니다. 마찬가지로 액션을 통해 적용된 사용자 편집도 영구적으로 저장되어야 합니다. 객체 타입을 뒷받침하는 Foundry 데이터소스는 이미 Foundry 데이터셋, 제한된 뷰(restricted view) 등의 형태로 영구 저장되어 있습니다.

[Funnel 파이프라인 문서](../03_indexing/02_funnel-batch-pipelines.md)에서 설명하듯, Funnel 서비스는 여러 Foundry 데이터셋을 소유하고 관리하며, 그중에는 데이터소스에서 오는 데이터와 사용자 편집을 합친 병합(merged) 데이터셋이 있습니다. 병합 데이터셋은 자동으로 빌드됩니다. 이를 통해 큐에 저장된 사용자 편집이 Foundry에 영구 저장되고, 큐가 너무 커지지 않도록 비워집니다. 기본적으로 이 빌드 작업은 다음 경우에 실행됩니다.

* 객체 타입 데이터소스에 새 데이터 트랜잭션이 생길 때마다
* 데이터소스에 새 데이터가 없더라도, 어떤 객체에서든 편집이 감지되었다면 6시간마다

**설명**: 일시적이라는 말은 인덱스가 언제든 원본에서 다시 만들어질 수 있는 사본이라는 뜻입니다. 따라서 "원본"은 두 가지로 나뉩니다. 하나는 입력 데이터셋이고, 다른 하나는 사용자 편집입니다. 사용자 편집은 처음에는 큐에만 있으므로, Funnel이 주기적으로 입력 데이터와 편집을 합친 병합 데이터셋을 빌드해 영구 기록으로 남깁니다.

> **중간 요약**: 인덱스는 일시적인 사본이므로 사용자 편집도 영구 저장이 필요합니다. Funnel은 입력 데이터와 편집을 합친 병합 데이터셋을 새 데이터가 들어올 때마다, 또는 편집이 있으면 6시간마다 자동으로 빌드합니다.

<a id="resolve-conflicting-user-edits-and-datasource-updates"></a>
## 사용자 편집과 데이터소스 갱신의 충돌 해결 (Resolve conflicting user edits and datasource updates)

Foundry 온톨로지의 객체는 입력 데이터소스와 사용자 편집 양쪽에서 생성되고 수정될 수 있습니다. 하나의 객체(즉, 특정 기본 키(primary key) 값을 가진 행 또는 객체)가 입력 데이터소스와 사용자 편집 양쪽에서 데이터를 받으면, 받은 값들은 *충돌 해결 전략(conflict resolution strategy)에* 따라 투명하게 해결되어야 합니다.

**주의**: 삭제는 편집으로 간주되지 않습니다. 삭제가 적용되면 데이터소스 상태와 관계없이 객체는 더 이상 보이지 않습니다. 나중에 객체가 다시 생성되더라도 이전 편집은 이어받지 않습니다.

충돌을 해결하는 전략은 두 가지입니다.

* [전략 1: 사용자 편집 적용(기본값)](#strategy-1-apply-user-edits-default)
* [전략 2: 가장 최근 값 적용](#strategy-2-apply-most-recent-value)

<a id="strategy-1-apply-user-edits-default"></a>
### 전략 1: 사용자 편집 적용, 기본값 (Strategy 1: Apply user edits (default))

이 전략에서는 같은 객체의 편집된 속성에 대해 이후 데이터소스 갱신이 있더라도, 객체의 최종 상태는 항상 그 객체에 적용된 사용자 편집으로 결정됩니다.

사용자 편집과 데이터소스 갱신을 바탕으로 객체의 최신 상태를 판단하려면 아래 흐름도를 참고하세요.

![객체 편집 흐름도](https://www.palantir.com/docs/resources/foundry/object-edits/object-edits-visibility-flowchart.png)

아래 표는 "사용자 편집이 항상 이긴다" 충돌 해결 전략에 따라, 특정 객체가 사용자 편집과 입력 데이터소스 갱신을 받은 뒤 상태가 어떻게 바뀌는지 보여 줍니다.

| 시점 | 현재 데이터소스 행 상태 | 사용자 편집 | 최종 객체 상태 | 설명 |
| --- | --- | --- | --- | --- |
| T0 | `columns = {pk_column = pk1, col1 = val1, col2 = val2}` |  | `properties = {pk_column = pk1, col1 = val1, col2 = val2}, deleted = false` |  |
| T1 | `columns = {}` |  | `properties = {}, deleted = true` | 데이터소스에서 행이 사라지고, 객체가 더 이상 Foundry 온톨로지에 없습니다 |
| T2 | `columns = {pk_column = pk1, col1 = val1, col2 = val2}` |  | `properties = {pk_column = pk1, col1 = val1, col2 = val2}, deleted = false` | 같은 행이 데이터소스에 다시 나타납니다 |
| T3 | `columns = {pk_column = pk1, col1 = val1, col2 = val2}` | 객체 수정: `properties = {pk_column = pk1, col2 = newVal2}` | `properties = {pk_column = pk1, col1 = val1, col2 = newVal2}, deleted = false` | 사용자가 `Modify object` 액션을 실행합니다 |
| T4 | `columns = {}` |  | `properties = {}, deleted = true` | 데이터소스에서 행이 다시 사라지고, 객체가 더 이상 Foundry 온톨로지에 없습니다 |
| T5 | `columns = {pk_column = pk1, col1 = val1, col2 = val2}` |  | `properties = {pk_column = pk1, col1 = val1, col2 = newVal2}, deleted = false` | 같은 행이 데이터소스에 다시 나타나고, 행이 다시 나타날 때 이전 사용자 편집이 여전히 객체에 적용됩니다 |
| T6 | `columns = {pk_column = pk1, col1 = newVal1, col2 = val2}` |  | `properties = {pk_column = pk1, col1 = newVal1, col2 = newVal2}, deleted = false` | 편집되지 않은 속성(`col1`)이 입력 데이터소스에서 데이터 갱신을 받고, 그 값이 객체에 적용됩니다 |
| T7 | `columns = {pk_column = pk1, col1 = newVal1, col2 = val2}` | 객체 삭제 | `properties = {}, deleted = true` | 사용자가 `Delete object` 액션을 실행하고, 객체가 더 이상 Foundry 온톨로지에 없습니다 |
| T8 | `columns = {pk_column = pk1, col1 = newVal1, col2 = val2, col3 = null}` |  | `properties = {}, deleted = true` |  |
| T9 | `columns = {pk_column = pk1, col1 = newVal1, col2 = val2, col3 = null}` | 객체 생성: `properties = {pk_column = pk1, col3 = val3}` | `properties = {pk_column = pk1, col1 = null, col2 = null, col3 = val3}, deleted = false` | 사용자가 `Create object` 액션을 실행합니다 |
| T10 | `columns = {pk_column = pk1, col1 = newVal1, col2 = newVal2, col3 = newVal3}` |  | `properties = {pk_column = pk1, col1 = null, col2 = null, col3 = val3}, deleted = false` | 입력 데이터소스에서 `col3`이 갱신되었지만, 앞선 `Create object` 액션 때문에 더 이상 객체의 최종 상태에 반영되지 않습니다 |
| T11 | `columns = {pk_column = pk1, col1 = newVal1, col2 = newVal2, col3 = newVal3}` | 객체 수정: `properties = {pk_column = pk1, col2 = newVal22}` | `properties = {pk_column = pk1, col1 = null, col2 = newVal22, col3 = val3}, deleted = false` | 사용자가 `Modify object` 액션을 실행합니다 |
| T12 | `columns = {}` |  | `properties = {pk_column = pk1, col1 = null, col2 = newVal22, col3 = val3}, deleted = false` | 데이터소스에서 행이 사라지지만, 마지막으로 사용자 편집에 의해 생성되었으므로 객체는 여전히 Foundry 온톨로지에 있습니다 |
| T13 | `columns = {pk_column = pk1, col1 = newVal1, col2 = newVal2, col3 = newVal3}` | 객체 삭제 | `properties = {}, deleted = true` | 행이 다시 나타나지만, 사용자가 `Delete object` 액션을 실행해 객체가 삭제됩니다 |
| T14 | `columns = {pk_column = pk1, col1 = newVal1, col2 = newVal2, col3 = newVal3}` | 객체 수정: `properties = {pk_column = pk1, col2 = newVal2, col3 = val3}` | `properties = {}, deleted = true` | 사용자가 삭제된 객체에 `Modify object` 액션을 실행합니다. 이런 `Modify object` 액션 호출은 모두 실패합니다 |

**설명**: 표에서 읽어 낼 규칙은 세 가지입니다. 첫째, 사용자가 수정한 속성(T3의 `col2`)은 이후 데이터소스 값이 바뀌어도 사용자 값이 유지되고, 수정하지 않은 속성(T6의 `col1`)은 데이터소스 갱신을 따라갑니다. 둘째, 객체가 사용자 편집으로 생성되면(T9) 그 뒤로는 데이터소스 행 전체가 무시되어, `col1`과 `col2`가 데이터소스 값 대신 `null`이 되고 데이터소스에서 행이 사라져도(T12) 객체가 남습니다. 셋째, 사용자가 삭제한 객체(T7, T13)는 데이터소스에 행이 있어도 보이지 않으며, 삭제된 객체를 수정하려는 액션(T14)은 실패합니다.

<a id="strategy-2-apply-most-recent-value"></a>
### 전략 2: 가장 최근 값 적용 (Strategy 2: Apply most recent value)

이 전략에서는 사용자 편집이 조건부로 적용됩니다. 즉, 사용자 편집의 타임스탬프가 해당 객체에 대해 데이터소스에서 오는 타임스탬프 값보다 더 최근일 때만 사용자 편집이 적용됩니다. 각 편집의 타임스탬프는 데이터소스에서 오는 편집되지 않은 타임스탬프 값과 비교되므로, 같은 객체에서 더 새로운 사용자 편집은 적용되고 더 오래된 사용자 편집은 적용되지 않는 일이 생길 수 있습니다.

<a id="configuration"></a>
#### 설정 (Configuration)

충돌 해결 전략은 객체 타입 수준에서 설정하며, OSv2 객체 타입에서만 지원됩니다.

사용자는 이 옵션을 Ontology Manager의 **Datasources** 섹션에서 설정할 수 있습니다. 객체 타입의 각 데이터소스는 서로 다른 해결 전략을 가질 수 있습니다. 예를 들어 데이터소스 두 개로 뒷받침되는 객체 타입이라면, 한 데이터소스는 `Apply user edits (default)`를, 다른 데이터소스는 `Apply most recent value`를 쓸 수 있습니다. `Apply most recent value` 옵션을 쓰려면 데이터소스에 타임스탬프(timestamp) 타입 속성이 있어야 합니다. 날짜(date) 속성 타입으로는 이 옵션이 동작하지 않습니다. 타임스탬프 속성은 사용자 편집을 적용할지 비교하고 결정하는 데 쓰입니다. 타임스탬프 속성은 협정 세계시(UTC)여야 합니다.

![편집 충돌 해결 설정](https://www.palantir.com/docs/resources/foundry/object-edits/edits-conflict-resolution-configuration.png)

<a id="behavior"></a>
#### 동작 (Behavior)

데이터소스에 대해 `Apply most recent value` 충돌 해결 전략을 저장하는 즉시, 그 데이터소스가 뒷받침하는 속성에 대한 모든 사용자 편집이 조건부로 적용됩니다.

각 조건부 편집은 백킹 데이터소스(backing datasource)의 타임스탬프 값과 편집에 연결된 타임스탬프를 비교하는 방식으로 해결됩니다. 충돌 해결 전략을 변경한 *이후에* 적용된 해당 속성의 사용자 편집은, 그 편집을 만든 액션 제출 시점의 타임스탬프를 기준으로 조건부 적용됩니다. 해당 속성에 대한 *기존* 편집은 충돌 해결 전략을 변경한 시점의 타임스탬프를 기준으로 조건부 적용됩니다.

백킹 데이터소스의 타임스탬프 속성 값이 사용자 편집에 연결된 타임스탬프보다 오래되었으면 사용자 편집이 적용되고, 그렇지 않으면 편집이 무시됩니다.

하나의 편집이 여러 데이터소스에 걸친 속성을 갱신한다면, 그 편집이 조건부로 적용될지 항상 적용될지는 해당 속성을 뒷받침하는 데이터소스의 해결 전략으로 결정됩니다.

사용자 편집과 데이터소스 갱신을 바탕으로 객체의 최신 상태를 판단하려면 아래의 갱신된 흐름도를 참고하세요.

![가장 최근 값 전략의 객체 편집 흐름도](https://www.palantir.com/docs/resources/foundry/object-edits/object-edits-visibility-flowchart-most-recent-strategy.png)

다음 예시가 이 동작을 보여 줍니다. `Ticket` 객체 타입에 객체 두 개가 있고, 백킹 데이터소스에는 아래 데이터가 있으며, `Apply most recent value` 옵션이 켜져 있다고 가정합니다.

| Ticket ID | Title      | Timestamp                    | Priority | Type            |
|-----------|------------|------------------------------|----------|-----------------|
| 101       | Ticket One | January 1, 2010, 9:00 AM UTC |P1        | Product Bug     |
| 102       | Ticket Two |                              |P2        | Feature Request |

이 티켓들에 대해 다음 세 액션이 실행되었다고 합시다.

* 2010년 1월 1일 오전 8:30에 두 티켓의 제목을 "Ticket"으로 설정했습니다.
* 2010년 1월 1일 오전 9:30에 두 티켓의 우선순위를 "P0"으로 설정했습니다.
* 2010년 1월 1일 오전 10:30에 두 티켓의 Type을 "Unknown"으로 설정했습니다.

그러면 온톨로지에서 관찰되는 두 객체의 상태는 다음과 같습니다.

| Ticket ID | Title      | Timestamp                    | Priority | Type    |
|-----------|------------|------------------------------|----------|---------|
| 101       | Ticket One | January 1, 2010, 9:00 AM UTC | P0       | Unknown |
| 102       | Ticket     |                              | P0       | Unknown |

Ticket ID가 101인 티켓의 경우, Title 속성에 대한 편집은 백킹 데이터소스의 오전 9:00 타임스탬프보다 먼저 만들어졌으므로 적용되지 않았습니다. 하지만 나머지 두 속성에 대한 편집은 오전 9:00 이후에 일어났으므로 해결된 객체에 반영되어 있습니다.

Ticket ID가 102인 티켓의 경우, 백킹 데이터소스에 타임스탬프 속성 값이 없으므로 연결된 타임스탬프와 관계없이 세 조건부 편집이 모두 적용됩니다.

**설명**: 이 전략은 원천 시스템(예: 외부 티켓 관리 시스템)에서도 같은 데이터가 계속 수정되는 경우를 위한 것입니다. 데이터소스 행의 타임스탬프가 "원천 시스템에서 이 행이 마지막으로 갱신된 시각"을 나타낸다고 보면, 판단 규칙은 `편집 시각 > 데이터소스 타임스탬프`이면 편집 값, 아니면 데이터소스 값입니다. 101번의 Title 편집(8:30)은 9:00보다 이르므로 데이터소스 값 "Ticket One"이 남고, 102번은 비교할 타임스탬프가 없으므로 편집이 모두 이깁니다.

<a id="edit-only-properties"></a>
#### 편집 전용 속성 (Edit-only properties)

[편집 전용 속성(edit-only property)](../../02_define-ontologies/02_object-and-link-types/03_properties/06_edit-only-properties.md)의 경우, 입력 데이터소스의 타임스탬프와 관계없이 사용자 편집이 항상 적용됩니다.

[위](#behavior)의 티켓 예시로 돌아가 다음 표를 생각해 봅시다.

|Ticket ID| Title      | Timestamp                    | Priority | Team (편집 전용 속성) |
|---------|------------|------------------------------|----------|---------------------------|
|102      | Ticket Two | January 1, 2050, 9:00 AM UTC | P2       | Sales                     |

`Change team` 액션 타입으로 `Team` 속성을 `Recruiting`으로 수정한다고 합시다. `Change team` 액션을 `Ticket Two`에 적용하면 팀은 `Recruiting`으로 설정됩니다. 어떤 충돌 해결 전략을 쓰든, `Team`은 편집 전용 속성이므로 편집이 적용됩니다.

액션이 편집 전용 속성과 일반 속성을 함께 수정할 때도 동작은 같습니다. 일반 속성의 편집은 조건에 따라 적용되고, 편집 전용 속성의 편집은 항상 적용됩니다.

**설명**: 편집 전용 속성은 데이터소스의 열과 연결되지 않고 사용자 편집으로만 값이 채워지는 속성입니다. 비교할 데이터소스 값이 없으므로 충돌 자체가 생기지 않아 항상 편집이 적용됩니다.

<a id="only-input-datasource-values-considered"></a>
#### 입력 데이터소스 값만 고려 (Only input datasource values considered)

온톨로지는 편집 타임스탬프를 입력 데이터소스의 타임스탬프 값과만 비교합니다. 사용자가 사용자 편집으로 타임스탬프 속성을 바꾸더라도, 조건부 비교는 입력 데이터소스의 타임스탬프와 사용자 편집 적용 시각 사이에서만 일어납니다.

이 동작 때문에 타임스탬프 속성은 입력 데이터소스의 타임스탬프 열로 뒷받침되어야 합니다. 원천 시스템이 데이터 피드의 갱신 시각을 나타내는 타임스탬프 값을 제공하지 않는다면, 데이터 파이프라인에서 입력 데이터소스의 타임스탬프 열을 수정할 수 있습니다.

[위](#behavior)의 티켓 예시로 돌아가 다음 표를 생각해 봅시다.

| Ticket ID | Title       | Timestamp                    | Priority |
|-----------|-------------|------------------------------|----------|
| 101       | Ticket One  | January 1, 2010, 9:00 AM UTC | P1       |

`Change Timestamp` 액션 타입을 사용해 위 티켓의 타임스탬프를 `January 1, 2050, 9:00 AM UTC`로 수정한다고 합시다.

| Ticket ID | Title       | Timestamp                                                     | Priority |
|-----------|-------------|---------------------------------------------------------------|----------|
| 101       | Ticket One  | ~~January 1, 2010, 9:00 AM UTC~~ January 1, 2050, 9:00 AM UTC | P1       |

이제 `Change Priority` 액션을 Ticket One에 적용하면, 우선순위는 여전히 `P0`으로 설정됩니다. 객체에 표시된 타임스탬프와 관계없이, 비교는 입력 데이터소스의 타임스탬프와 사용자 편집 적용 시각 사이에서만 일어나기 때문입니다.

**설명**: 화면에 보이는 타임스탬프는 2050년으로 바뀌었지만 이는 사용자 편집 값일 뿐이고, 비교에 쓰이는 값은 데이터소스에 들어 있는 원래 값(2010년 9:00)입니다. 따라서 그보다 나중에 실행된 `Change Priority` 편집은 정상적으로 적용됩니다.

> **중간 요약**: 기본 전략은 "사용자 편집이 항상 이긴다"이며, 편집된 속성은 데이터소스 갱신을 무시하고 사용자가 생성하거나 삭제한 객체는 데이터소스 행 상태와 무관해집니다. OSv2에서 고를 수 있는 "가장 최근 값 적용" 전략은 데이터소스의 UTC 타임스탬프 열과 편집 시각을 비교해 더 최근 쪽을 택하며, 편집 전용 속성은 예외로 항상 편집이 적용됩니다.

## 정리

- 액션의 편집은 Funnel 큐를 거쳐 객체 데이터베이스 인덱스에 즉시 반영되고, 병합 데이터셋 빌드를 통해 영구 저장됩니다.
- 개별 편집을 되돌리는 기능은 없으며, OSv2에서는 **Delete edits**("drop all edits" 마이그레이션)로 전체 편집을 버릴 수 있습니다.
- 액션 실행 중 버전 검사는 OSv1이 더 엄격하고(읽은 객체 전체), OSv2는 편집 생성에 직접 쓰인 객체만 검사합니다.
- 데이터소스와 편집이 충돌하면 기본적으로 사용자 편집이 이기며, OSv2에서는 데이터소스별로 타임스탬프 기반 "가장 최근 값 적용" 전략을 고를 수 있습니다.
