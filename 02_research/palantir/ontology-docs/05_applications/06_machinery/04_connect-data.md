# Machinery에 데이터 연결하기 (Connect data to Machinery)

- 원문: https://www.palantir.com/docs/foundry/machinery/connect-data/
- 사이드바 위치: Applications > Machinery > Connect data to Machinery

이 페이지는 Machinery 프로세스를 온톨로지의 실제 데이터에 연결하는 방법을 다룹니다. 그려 둔 프로세스 정의만으로는 실제로 객체들이 어떤 상태를 거쳤는지 알 수 없으므로, 현재 상태를 담은 프로세스 객체(process object)와 상태 변경 이력을 담은 로그 객체(log object)를 연결해야 마이닝과 모니터링이 가능해집니다. 로그 객체 타입의 스키마와 자동 설치 방법도 함께 설명합니다.

프로세스를 데이터소스에 연결하면 추상적인 프로세스 정의와 실제 관측 기록 사이의 간극을 메울 수 있습니다. 이 데이터는 초기 [프로세스 마이닝](05_process-mining.md)을 수행하거나 [성능을 모니터링하고 병목을 찾는 데](06_analyze-and-monitor.md) 사용할 수 있습니다.

Machinery는 온톨로지의 두 가지 객체 데이터, 즉 [프로세스 객체](#process-objects)와 [로그 객체](#log-objects)에 연결됩니다. 데이터 구성용 사이드 패널은 메인 도구 상자나 프로세스 컨테이너에서 열 수 있습니다.

<a id="process-objects"></a>
## 프로세스 객체 (Process objects)

프로세스 객체는 프로세스를 거쳐 가는 엔터티입니다.

예를 들어 온보딩 프로세스라면 `Employee`, 구매-지급(purchase-to-pay) 프로세스라면 `Invoice`가 프로세스 객체가 될 수 있습니다. 엔터티의 상태는 문자열 속성(property)으로 명시적으로 추적되며, 이 속성은 보통 `state`라는 이름을 씁니다. `state` 속성의 값(예: "created" 또는 "approved")은 그래프의 상태 노드로 표현됩니다.

**주의**: 상태 값에는 의존 관계가 있을 수 있습니다. 예를 들어 액션의 제출 조건(submission criteria)이나, 특정 상태 조건에서 실행되는 자동화가 그렇습니다. Machinery에서 상태 값을 바꿔도 이런 의존 관계는 갱신되지 않으며, 온톨로지 데이터의 값도 바뀌지 않습니다.

여러 프로세스를 다루는 설정에서는 프로세스 컨테이너 하나가 객체 타입 하나의 상태 속성 하나만을 담당합니다.

![여러 프로세스, 중첩, 계층 구조를 보여 주는 다중 객체 타입 프로세스 예시.](https://www.palantir.com/docs/resources/foundry/machinery/multiple-object-type-processes.png)

위 리소스 예시 스크린샷처럼, 한 객체 타입이 상태 속성을 여러 개 가질 수 있습니다. 예를 들어 대략적인 상태(coarse state)와 세분화된 상태(granular state)를 함께 둘 수 있습니다.

프로세스 객체 타입은 엔터티의 최신 상태를 나타내므로, 상태 전이나 시간적 패턴에 대한 정보는 줄 수 없습니다.

<img src="https://www.palantir.com/docs/resources/foundry/machinery/ontology-configuration.png" width=350 alt="온톨로지 구성 사이드 패널." >

**설명**: 프로세스 객체 타입은 "현재 스냅숏" 테이블입니다. 예를 들어 Invoice 테이블에 `(INV-1, approved)`, `(INV-2, created)`, `(INV-3, paid)` 세 행이 있다면, 지금 각 송장이 어느 상태인지는 알 수 있지만 INV-3이 `created`에서 `paid`까지 며칠 걸렸는지, 중간에 `rejected`를 거쳤는지는 알 수 없습니다. UPDATE 문이 이전 값을 덮어쓰기 때문입니다. 이 정보를 얻으려면 아래의 로그 객체가 필요합니다.

> **중간 요약**: 프로세스 객체는 프로세스를 거치는 엔터티(예: `Invoice`)이며, 보통 `state` 문자열 속성으로 현재 상태를 담습니다. 컨테이너 하나는 상태 속성 하나에 대응하고, 프로세스 객체만으로는 최신 상태만 알 수 있어 전이 이력은 알 수 없습니다.

<a id="log-objects"></a>
## 로그 객체 (Log objects)

로그 객체는 엔터티 상태의 개별 변경 한 건을 나타냅니다. 로그 객체에는 프로세스 엔터티에 대한 참조, 이전 상태, 새 상태, 전이 시각이 들어 있습니다.

* **Log ID (string) \[필수]:** 로그 객체의 기본 키(primary key)입니다.
* **Process ID (string) \[필수]:** 추적 대상 프로세스 객체의 기본 키입니다. 프로세스 객체와 로그 객체 사이에 온톨로지 링크를 설정할 때 사용합니다.
* **Old state (string) \[필수]:** 전이의 시작 상태입니다.
* **New state (string) \[필수]:** 전이의 끝 상태입니다.
* **Timestamp (timestamp) \[필수]:** 끝 상태에 진입한 시각입니다.
* **isLatest (boolean) \[선택]:** 이 로그가 해당 프로세스 객체의 가장 최근 로그이면 True, 아니면 False입니다.
* **Duration (long) \[선택]:** 이전 상태에 진입한 뒤 지난 시간(밀리초)입니다.
* **Path (string) \[선택]:** 현재 상태를 포함해 지금까지 거친 모든 상태의 목록입니다. 직렬화된 JSON 문자열이어야 합니다.
* **Action type RID (string) \[선택]:** 전이를 일으킨 액션 타입의 식별자입니다. 외부 변경의 경우 보통 `NULL`입니다.
* **Owning RID (string) \[선택]:** 액션이 실행된 애플리케이션의 식별자입니다. 수동 액션과 자동화된 액션을 구분할 수 있게 해 줍니다. 외부 변경의 경우 `NULL`입니다.

**설명**: 위 스키마로 INV-3의 이력을 표현하면 다음과 같은 행들이 됩니다.

| Log ID | Process ID | Old state | New state | Timestamp | isLatest | Duration | Path |
|---|---|---|---|---|---|---|---|
| L1 | INV-3 | (없음) | created | 2024-03-01 09:00 | false | | `["created"]` |
| L2 | INV-3 | created | approved | 2024-03-03 14:00 | false | 190800000 | `["created","approved"]` |
| L3 | INV-3 | approved | paid | 2024-03-05 10:00 | true | 158400000 | `["created","approved","paid"]` |

Process ID는 Invoice의 기본 키를 가리키는 외래 키 역할을 하며, 이것으로 Invoice와 로그 사이에 일대다 링크가 생깁니다. Duration 190800000밀리초는 `created`에 머문 53시간입니다. 첫 행의 Old state를 어떻게 채우는지는 원문에 나와 있지 않으므로 표에서는 "(없음)"으로 적었습니다.

이런 로그를 유지하려면 편집이 일어날 때 오케스트레이션(orchestration)이 필요합니다. Machinery는 애플리케이션 안에서 설치할 수 있는 표준 솔루션을 제공합니다. 로그 객체 타입을 설정하려면 프로세스 객체 타입이 있어야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/machinery/install-object-log-type.png" width=350 alt="온톨로지 구성 사이드 패널." >

대화 상자가 설정 과정을 안내합니다. 추적할 편집의 출처를 선택할 수 있습니다.

* 프로세스 객체 타입이 외부 데이터소스로부터 변경을 받는다면, 변경 로그(changelog) 데이터셋을 선택하고 구성할 수 있습니다.
* 프로세스 객체 타입을 플랫폼 안에서 편집할 수 있다면, [프로세스 객체 타입의 편집 이력(edit history)을 켜고](../../06_ontology-architecture/04_object-edits-and-materializations/03_user-edit-history.md) 그 편집들을 로그 객체 타입에 포함하도록 선택할 수 있습니다. Machinery는 편집 이력의 머티리얼라이제이션(materialization) 데이터셋을 자동으로 만들어 집계 분석에 쓸 수 있게 합니다.

**참고**: 데이터소스가 여러 개이거나 행 수준 권한(row-level permissions)이 있는 객체 타입에 대해서는 플랫폼 편집에서 로그를 추적하는 기능이 현재 지원되지 않습니다.

외부 데이터소스의 변경을 추적하려면 표준 변경 로그 형식의 데이터셋을 선택해야 합니다. 이 형식은 Machinery의 로그 객체 타입 스키마를 단순화한 버전입니다. 이 데이터셋은 보통 객체 타입 데이터소스의 상류(upstream)에 있으며, 다음 열을 가집니다.

* **processId (string) \[필수]:** 프로세스 엔터티의 고유 식별자입니다.
* **state (string) \[필수]:** 프로세스가 새로 진입한 상태입니다.
* **timestamp (timestamp) \[필수]:** 전이가 일어난 시각입니다.
* **isDeleted (boolean) \[선택]:** 엔터티가 삭제되었음을 표시하는 속성입니다. 최신 로그의 isDeleted가 `True`이면 해당 객체는 온톨로지에 나타나지 않습니다.

**설명**: 표준 변경 로그는 "새 상태"만 기록합니다. 예를 들어 `(INV-3, created, 03-01)`, `(INV-3, approved, 03-03)`, `(INV-3, paid, 03-05)` 세 행만 있으면, processId별로 timestamp 순으로 정렬해 바로 앞 행의 state를 Old state로 붙이는 방식으로 위의 로그 객체 형식(Old state, New state, Duration 등)을 계산할 수 있습니다. SQL로 치면 `LAG(state) OVER (PARTITION BY processId ORDER BY timestamp)` 같은 윈도 함수 계산입니다. 아래에 나오는 파이프라인이 이런 변환을 맡습니다(구체적인 구현 방식은 원문에 나와 있지 않습니다). "상류"는 데이터가 흘러가는 파이프라인에서 앞 단계에 있다는 뜻입니다.

확인하면 Machinery는 선택한 폴더에 [Marketplace 제품](https://www.palantir.com/docs/foundry/marketplace/overview/)을 설치합니다. 이 제품에는 구성된 출처에서 로그 항목을 올바른 형식으로 계산하는 [Pipeline Builder](https://www.palantir.com/docs/foundry/pipeline-builder/overview/) 파이프라인이 들어 있습니다. 제품은 로그 객체 타입 자체도 배포하며, 이때 프로세스 객체 타입으로 가는 온톨로지 링크도 함께 만들어집니다.

설치가 끝난 뒤에는 파이프라인이 최초 빌드를 마치고, 로그 객체 타입이 데이터베이스에 인덱싱되어야 마이닝과 모니터링에 데이터를 쓸 수 있습니다.

**참고**: 배포된 파이프라인은 데이터소스 중 하나라도 바뀔 때마다 실행되도록 스케줄되어 있습니다. 그 결과 로그 객체 타입은 프로세스 객체 타입보다 빌드 한 번과 인덱싱 작업 한 번만큼 늦으며, 보통 약 2\~5분 정도입니다. 실시간 갱신이 필요하다면 사용자 정의 로그 객체 타입을 직접 유지해야 합니다.

최소 스키마를 충족한다면 사용자 정의 로그 객체 타입을 수동으로 매핑할 수 있습니다.

> **중간 요약**: 로그 객체는 상태 변경 한 건을 한 행으로 담으며 Log ID, Process ID, Old state, New state, Timestamp가 필수입니다. Machinery는 외부 변경 로그 데이터셋이나 플랫폼 편집 이력을 출처로 삼아 로그를 계산하는 파이프라인과 로그 객체 타입을 Marketplace 제품으로 설치해 주며, 이 방식은 2\~5분 정도 지연이 있습니다.

## 정리

- Machinery는 온톨로지의 프로세스 객체(현재 상태)와 로그 객체(상태 변경 이력)에 연결됩니다.
- 프로세스 객체의 `state` 같은 문자열 속성 값이 그래프의 상태 노드가 되며, Machinery에서 상태 값을 바꿔도 데이터나 제출 조건은 바뀌지 않습니다.
- 로그 객체 타입은 필수 필드 5개와 선택 필드 5개로 이루어진 스키마를 가지며, Process ID로 프로세스 객체와 링크됩니다.
- 외부 변경 로그 데이터셋(processId, state, timestamp)이나 플랫폼 편집 이력을 출처로 Machinery가 파이프라인과 로그 객체 타입을 자동 설치할 수 있습니다.
- 자동 설치 방식은 빌드와 인덱싱만큼 지연되므로, 실시간이 필요하면 사용자 정의 로그 객체 타입을 유지합니다.
