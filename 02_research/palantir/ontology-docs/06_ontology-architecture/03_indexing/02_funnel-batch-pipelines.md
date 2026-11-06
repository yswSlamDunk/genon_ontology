# Funnel 배치 파이프라인 (Funnel batch pipelines)

- 원문: https://www.palantir.com/docs/foundry/object-indexing/funnel-batch-pipelines/
- 사이드바 위치: Ontology architecture > Indexing > Funnel batch pipelines

이 페이지는 데이터셋의 행과 사용자 편집(edit)을 묶음 단위로 Object Storage v2(OSv2)에 인덱싱하는 Funnel 배치 파이프라인의 내부 구성을 설명합니다. 파이프라인을 이루는 네 단계(Changelog, Merge changes, Indexing, Hydration), 운영 중인 Live 파이프라인과 스키마 변경 시 새로 만들어지는 Replacement 파이프라인, 증분 인덱싱과 전체 재인덱싱의 차이, 모니터링과 디버깅 방법을 다룹니다. 객체 타입의 데이터가 왜 늦게 반영되는지, 빌드가 왜 실패하는지 파악할 때 필요한 내용입니다.

Funnel 배치 파이프라인은 데이터(Foundry 데이터소스에서 온 데이터와 사용자 편집에서 온 데이터 모두)를 배치 방식으로 OSv2에 효율적으로 인덱싱하도록 조율하는 내부 잡(job) 파이프라인이며, 온톨로지의 데이터와 메타데이터를 최신 상태로 유지합니다.

<a id="components-of-a-funnel-batch-pipeline"></a>
## Funnel 배치 파이프라인의 구성 요소 (Components of a Funnel batch pipeline)

Funnel 배치 파이프라인은 일련의 [Foundry 빌드 잡(build job)](https://www.palantir.com/docs/foundry/data-integration/datasets/)으로 이루어져 있습니다.

* [Changelog](#changelog)
* [Merge changes](#merge-changes)
* [Indexing](#indexing)
* [Hydration](#hydration)

아래 스크린샷은 Funnel 배치 파이프라인의 예를 보여 줍니다.

![파이프라인 랜딩 페이지](https://www.palantir.com/docs/resources/foundry/object-indexing/pipeline1.png)

<a id="changelog"></a>
### Changelog

Changelog 잡에서 Funnel은 데이터소스에 새 데이터나 트랜잭션이 들어오면 모든 데이터소스의 데이터 차이(data difference)를 자동으로 계산한 뒤, Funnel 파이프라인 안에 중간 changelog 데이터셋을 만듭니다. Changelog 데이터셋은 각 트랜잭션에 데이터 차이를 담은 [APPEND 트랜잭션](https://www.palantir.com/docs/foundry/data-integration/datasets/#transaction-types)을 받아 [증분 계산 의미론(incremental computation semantics)](https://www.palantir.com/docs/foundry/data-integration/datasets/#transaction-types)을 제공합니다. 이 changelog 데이터셋은 Funnel이 소유하고 관리하므로 사용자는 접근할 수 없습니다.

<a id="merge-changes"></a>
### Merge changes

Merge changes 잡에서는 changelog 단계에서 나온 모든 changelog 데이터셋과 액션(Actions)에서 온 최근 사용자 편집을 객체 타입의 기본 키(primary key)로 조인해 모든 변경 사항을 병합하고, 그 결과를 별도 데이터셋에 저장합니다. 이 병합된 데이터셋은 Funnel이 소유하고 관리하므로 사용자는 접근할 수 없습니다.

<a id="indexing"></a>
### Indexing

변경 사항이 병합되고 나면, Funnel은 객체 데이터베이스마다 인덱싱 잡을 하나씩 시작해, 모든 변경 사항이 병합된 최종 데이터셋의 모든 행을 해당 객체 타입에 설정된 객체 데이터베이스와 호환되는 형식으로 변환합니다. 예를 들어 표준(canonical) OSv2 데이터베이스의 경우, 이전 단계에서 만든 병합 데이터셋의 모든 행이 인덱스 파일로 변환되며, 이 파일들은 별도의 인덱스 데이터셋에 저장됩니다. 이 인덱스 데이터셋은 Funnel이 소유하고 관리하므로 사용자는 접근할 수 없습니다.

<a id="hydration"></a>
### Hydration

인덱싱 잡이 완료되면, 객체 데이터베이스는 인덱싱된 데이터를 질의할 수 있도록 준비해야 합니다. OSv2를 예로 들면, 이 준비 단계에서는 데이터셋의 인덱스 파일을 OSv2 데이터베이스 검색 노드(search node)의 디스크로 내려받습니다. *하이드레이션(hydration)*이라 불리는 이 과정이 객체 타입의 데이터를 갱신하는 이 예시 Funnel 배치 파이프라인의 마지막 단계입니다.

하이드레이션 잡의 진행 상황은 아래 스크린샷처럼 Ontology Manager 애플리케이션에 표시됩니다.

![파이프라인 하이드레이션 상태](https://www.palantir.com/docs/resources/foundry/object-indexing/pipeline2.png)

이 단계들이 완료되면 객체 타입을 사용할 준비가 된 것이며, 외부 또는 Foundry 안의 다른 서비스가 이 객체 타입을 질의할 수 있습니다.

**설명**: 네 단계를 `Employee` 객체 타입(백킹 데이터셋 100행)에 적용해 보면 다음과 같습니다. (1) Changelog: 데이터셋에 새 트랜잭션이 들어와 E005의 `department`가 바뀌고 E101이 추가되었다면, 바뀐 이 2행만 뽑아 changelog 데이터셋에 덧붙입니다. (2) Merge changes: 이 2행과, 사용자가 액션으로 E010의 `title`을 고친 편집을 `employee_id`로 맞춰 하나의 최신 상태로 합칩니다. (3) Indexing: 합쳐진 행들을 검색 엔진이 읽는 인덱스 파일 형식으로 변환합니다. 데이터베이스 수업의 B-트리 인덱스처럼, 빠른 조회를 위해 데이터를 미리 정리해 둔 파일입니다. (4) Hydration: 그 인덱스 파일을 실제 질의를 처리하는 검색 서버의 로컬 디스크로 복사합니다. 이 복사까지 끝나야 Workshop 같은 애플리케이션에서 새 값이 보입니다.

> **중간 요약**: 배치 파이프라인은 변경분 계산(Changelog), 사용자 편집과의 병합(Merge changes), 인덱스 파일 생성(Indexing), 검색 노드로의 적재(Hydration) 네 단계로 이루어지며, 중간 데이터셋은 모두 Funnel 소유라 사용자가 볼 수 없습니다.

<a id="live-and-replacement-funnel-pipelines"></a>
## Live 파이프라인과 Replacement 파이프라인 (Live and replacement Funnel pipelines)

객체 타입에 데이터 업데이트나 스키마 업데이트가 있을 때는 서로 다른 두 개의 Funnel 파이프라인이 관여합니다. 아래 스크린샷은 이 두 Funnel 파이프라인을 보여 줍니다.

![파이프라인 랜딩 페이지](https://www.palantir.com/docs/resources/foundry/object-indexing/pipeline1.png)

<a id="live-pipelines"></a>
### Live 파이프라인 (Live pipelines)

Funnel *Live 파이프라인*은 Foundry 데이터소스에서 온 새 데이터로 운영 중인(production) 객체 타입을 갱신합니다. Live 파이프라인은 해당 데이터소스가 업데이트될 때마다 실행됩니다. 또한 객체에 대한 사용자 편집이 감지되면, 백킹 데이터셋에 명시적인 업데이트가 없더라도 Live 파이프라인은 6시간마다 실행됩니다. 이렇게 해서 인덱싱의 Merge changes 단계에서 사용자 편집이 Funnel 소유 데이터셋에 영구 저장되도록 보장합니다.

사용자 편집은 [객체 데이터베이스](../01_overview-and-getting-started/01_overview.md#functional-components-and-architecture)의 인덱스에 즉시 적용됩니다. 정기적인 6시간 간격의 잡은 이 데이터를 Foundry에 영구 저장하기 위한 내장 통제 장치 역할을 합니다.

**설명**: 사용자가 액션으로 값을 바꾸면 화면에는 바로 반영됩니다(검색 인덱스에 즉시 적용). 하지만 그 편집이 Foundry 데이터셋 형태로 기록되는 것은 다음 Live 파이프라인 실행의 Merge changes 단계에서입니다. 백킹 데이터셋이 하루에 한 번만 갱신되더라도 편집이 있으면 6시간마다 파이프라인이 돌기 때문에, 편집이 데이터셋에 기록되기까지 최대 약 6시간이 걸린다고 볼 수 있습니다.

<a id="replacement-pipelines"></a>
### Replacement 파이프라인 (Replacement pipelines)

객체 타입의 스키마가 바뀌어 이전 파이프라인의 스키마가 더 이상 최신이 아니게 되면, 객체 타입 업데이트를 조율할 새 *Replacement 파이프라인*을 프로비저닝해야 합니다. 스키마 변경에는 객체 타입에 새 속성 타입 추가, 기존 속성 타입 변경, 객체 타입의 입력 데이터소스를 다른 데이터소스로 교체하는 것 등이 포함됩니다.

Live 파이프라인이 평소 주기대로 계속 실행되는 동안, Funnel은 사용자에게 제공되는 라이브 데이터에 영향을 주지 않고 백그라운드에서 Replacement 파이프라인을 조율합니다. Replacement 파이프라인이 처음으로 성공적으로 실행되면 Live 파이프라인은 폐기되고 Replacement 파이프라인으로 대체되며, 객체 타입의 스키마와 데이터도 그에 맞게 갱신됩니다.

스키마 변경이 Funnel이 Replacement 파이프라인을 프로비저닝하는 가장 흔한 이유이지만, Funnel은 다양한 휴리스틱에 근거해 성능상의 이유로 Replacement 파이프라인을 자동으로 프로비저닝하기도 합니다.

**설명**: 이 방식은 데이터베이스에서 테이블 구조를 바꿀 때 기존 테이블을 그대로 서비스하면서 새 구조의 테이블을 따로 만들어 데이터를 채운 뒤, 준비가 끝나면 한 번에 교체하는 절차와 같은 순서로 동작합니다. 예를 들어 `Employee`에 `hire_date` 속성을 추가하면, 새 속성이 포함된 인덱스를 처음부터 만드는 동안 사용자는 기존 속성으로 이루어진 객체를 계속 조회하고, 새 인덱스가 완성되는 시점에 `hire_date`가 나타납니다.

> **중간 요약**: Live 파이프라인은 데이터 갱신과 6시간 주기의 편집 영구 저장을 맡고, 스키마가 바뀌면 백그라운드에서 Replacement 파이프라인이 새로 만들어져 첫 성공 실행 후 Live 파이프라인을 대체합니다.

<a id="incremental-and-full-reindexing"></a>
## 증분 인덱싱과 전체 재인덱싱 (Incremental and full reindexing)

다음 내용은 표준 Object Storage v2 데이터 저장소에 해당합니다. Object Storage v1(Phonograph)의 인덱싱 동작은 [OSv1 문서](../05_object-databases/01_object-storage-v1.md#incremental-and-batch-reindexing)를 참고하십시오.

<a id="incremental-indexing-default"></a>
### 증분 인덱싱(기본값) (Incremental indexing (default))

표준 Object Storage v2 데이터 저장소는 데이터소스의 새 트랜잭션마다 데이터 차이를 자동으로 계산하고, 새로운 데이터 업데이트만 증분 방식으로 인덱싱합니다. Funnel 파이프라인은 모든 객체 타입에 대해 기본적으로 증분 인덱싱을 사용합니다. 증분 인덱싱을 쓰면 모든 데이터를 다시 인덱싱해야 하는 경우보다 Funnel 파이프라인이 더 빠르게 실행됩니다.

예를 들어 100행짜리 데이터소스를 백킹으로 하는, 객체 100개짜리 객체 타입이 있다고 합시다. 새 데이터 업데이트에서 그중 10행이 바뀌면, 입력 데이터소스의 [트랜잭션 타입](https://www.palantir.com/docs/foundry/data-integration/datasets/#transaction-types)과 관계없이 객체 100개를 모두 재인덱싱하는 대신, [Funnel 배치 파이프라인](02_funnel-batch-pipelines.md)은 변경된 10행만 담은 새 `APPEND` 트랜잭션을 changelog 데이터셋에 만듭니다.

<a id="incremental-indexing-of-incremental-datasets"></a>
#### 증분 데이터셋의 증분 인덱싱 (Incremental indexing of incremental datasets)

[Object Storage v2](../01_overview-and-getting-started/01_overview.md#object-storage-v2-architecture)는 증분 데이터셋을 백킹으로 하는 객체 타입을 동기화할 때 "가장 최근 트랜잭션이 이긴다(most recent transaction wins)" 전략을 사용합니다. 데이터셋에 같은 기본 키를 가진 행이 둘 이상 있으면, 가장 최근 트랜잭션에 있는 행의 데이터가 온톨로지에 나타납니다. 한 트랜잭션 안에는 중복된 기본 키가 있으면 안 됩니다. 이 동작은 [사용자 편집과 데이터소스 업데이트 충돌](../04_object-edits-and-materializations/02_how-edits-applied.md#resolve-conflicting-user-edits-and-datasource-updates)을 처리하는 방식과는 관계가 없습니다.

`APPEND` 트랜잭션으로 행 업데이트를 받는 증분 데이터셋, 흔히 changelog 데이터셋이라 부르는 것을 생각해 봅시다. 같은 데이터의 새 버전은 기본 키는 같고 값만 갱신된 새 행으로 표현되며, 한 트랜잭션으로 데이터셋에 덧붙여집니다. `is_deleted`라는 이름의 열은 기본적으로 삭제 열(deletion column)로 취급되지 않습니다. 삭제 열을 사용하려면 데이터소스 스키마에 그 열을 지정하는 레거시 Object Storage v1 changelog 메타데이터가 있어야 합니다.

Object Storage v2는 changelog 데이터셋을 다음과 같이 동기화합니다.

* 기본 키가 여러 트랜잭션에 나타나면 가장 최근 트랜잭션의 행이 유지됩니다.
* 각 트랜잭션에는 기본 키당 최대 한 행만 있어야 합니다.
* 삭제 열은 레거시 Object Storage v1 changelog 메타데이터에 선언되어 있을 때만 인정됩니다.

각 트랜잭션에 기본 키당 최대 한 행만 있도록 하려면, changelog 데이터셋에 증분 윈도 변환(incremental window transform)을 적용해야 할 가능성이 큽니다.

```python
from pyspark.sql.window import Window
from pyspark.sql import functions as F

ordering_window = Window().partitionBy('primary_key').orderBy(F.col('ordering').desc())
df = df.withColumn('rank', F.row_number().over(ordering_window))
df = df.filter((F.col('rank') == 1) & ~F.col('is_deleted'))
```

**설명**: 이 PySpark 코드는 입력 DataFrame `df`에서 기본 키마다 가장 최신 행 하나만 남깁니다. 첫 줄의 `Window().partitionBy('primary_key').orderBy(F.col('ordering').desc())`는 같은 `primary_key` 값을 가진 행끼리 묶고, 각 묶음 안에서 `ordering` 열(예: 갱신 시각) 내림차순으로 정렬하는 창(window)을 정의합니다. 둘째 줄은 각 묶음 안에서 1, 2, 3 순번을 매겨 `rank` 열에 넣고, 셋째 줄은 순번이 1인 행(가장 최신)만 남기면서 `is_deleted`가 참인 행은 버립니다. SQL로는 `ROW_NUMBER() OVER (PARTITION BY primary_key ORDER BY ordering DESC)`로 순번을 매긴 뒤 `WHERE rank = 1 AND NOT is_deleted`로 거르는 것과 같습니다. 예를 들어 한 트랜잭션에 E001 행이 `ordering` 3과 5로 두 개 있으면 5인 행만 남습니다.

<a id="views-incremental-indexing"></a>
#### 뷰의 증분 인덱싱 (Views incremental indexing)

[데이터셋 뷰(dataset view)](https://www.palantir.com/docs/foundry/data-integration/views/)는 증분 인덱싱에 제약이 있습니다. 뷰는 기반 데이터 구조를 추상화하므로, Funnel은 비용을 아끼기 위해 증분 빌드를 시도합니다. 하지만 다음 제약이 적용됩니다.

* **삭제 열이 있는 뷰**는 Funnel이 어떤 행이 삭제되었는지 판단할 수 없으므로 항상 전체 재인덱싱됩니다.
* **중복 제거(deduplication) 열 값이 트랜잭션 순서와 충돌하면 증분 빌드가 일관되지 않은 결과를 낼 수 있습니다.** Funnel은 "마지막 편집이 이긴다(last edit wins)" 전략을 사용하므로, 중복 제거 열 값이 더 큰 행이라도 증분 창(incremental window) 밖에 있으면 무시됩니다. 이를 피하려면 삭제 열을 추가해 전체 재인덱싱을 유도하거나, 중복 제거 열 값이 트랜잭션마다 항상 증가하도록 보장하십시오.
* 기반 데이터셋에 [**최신 뷰에서 삭제하는 보존 정책(retention policy)**](https://www.palantir.com/docs/foundry/retention/manage-retention-policies/#latest-view-transaction-deletion)이 있으면, 오래된 데이터가 제거될 때 예상치 못한 결과가 생길 수 있습니다. 이런 경우에는 전체 재인덱싱을 하면 올바른 결과가 나옵니다.

**설명**: 두 번째 항목의 상황을 구체적으로 보면, 트랜잭션 T1에 E001의 `version`이 9인 행이, 그 뒤 트랜잭션 T2에 `version`이 7인 행이 들어왔다고 합시다. 증분 빌드는 새 트랜잭션 T2만 처리 범위로 보므로 E001은 `version` 7 값으로 갱신됩니다. `version`이 더 큰 행을 기대했다면 결과가 어긋난 것입니다. 중복 제거 열 값이 트랜잭션 순서대로 증가하면 이런 충돌이 생기지 않습니다.

<a id="full-reindexing-special-cases"></a>
### 전체 재인덱싱(특수한 경우) (Full reindexing (special cases))

Funnel 파이프라인은 다음 경우에 배치 인덱싱(모든 객체를 재인덱싱)을 사용합니다.

* 입력 데이터소스의 행 중 일정 비율 이상이 같은 트랜잭션에서 수정되면, changelog를 계산해 증분 인덱싱하는 것보다 재인덱싱이 계산 비용이 적고 더 빠를 수 있습니다. 기본 임곗값은 같은 트랜잭션에서 행의 80%가 변경된 경우로 설정되어 있습니다.
* 객체 타입 스키마의 특정 변경 때문에 [Funnel Replacement 파이프라인](02_funnel-batch-pipelines.md#replacement-pipelines)이 필요할 때. 이 경우 백그라운드에서 완전히 새로운 Funnel 파이프라인(OSv2 인덱스 포함)이 만들어집니다.
* 사용자가 Ontology Manager에서 전체 재인덱싱을 실행할 때.

![... 드롭다운 메뉴의 Reindex 옵션.](https://www.palantir.com/docs/resources/foundry/object-indexing/reindex.png)

> **중간 요약**: OSv2는 기본적으로 바뀐 행만 증분 인덱싱하며, 증분 데이터셋은 트랜잭션당 기본 키 하나의 행만 허용하고 최신 트랜잭션이 이깁니다. 행의 80% 이상이 바뀌거나, Replacement 파이프라인이 필요하거나, 사용자가 요청하면 전체 재인덱싱합니다.

<a id="monitor-funnel-pipelines"></a>
## Funnel 파이프라인 모니터링 (Monitor Funnel pipelines)

Funnel 파이프라인은 여러 빌드 잡으로 이루어져 있습니다. [모니터링 뷰(monitoring views)](https://www.palantir.com/docs/foundry/monitoring-views/overview/)를 사용하면 [모니터링 규칙(monitoring rule)](https://www.palantir.com/docs/foundry/monitoring-views/overview/#add-a-monitoring-rule) 집합을 만들어 Funnel 파이프라인의 특정 잡의 상태를 추적할 수 있습니다.

Ontology Manager에서 **Monitor the health of this object type**(이 객체 타입의 상태 모니터링)을 선택하면 모니터링 뷰를 만들 수 있습니다. 그러면 아래 스크린샷처럼 Data Health 애플리케이션의 [모니터링 뷰](https://www.palantir.com/docs/foundry/monitoring-views/overview/) 탭으로 이동합니다.

![파이프라인 모니터](https://www.palantir.com/docs/resources/foundry/object-indexing/pipeline_monitor.png)

모니터링 뷰 탭에서 Live 파이프라인과 Replacement 파이프라인 양쪽의 잡을 모니터링하는 규칙을 만들 수 있습니다. 또 **Sync Propagation Delay** 규칙을 추가하면, 객체 데이터베이스에 인덱싱된 데이터의 신선도(freshness)가 규칙에 정의한 임곗값을 넘을 때 알림을 받을 수 있습니다.

반면 Object Storage v1(Phonograph)은 온톨로지 엔터티의 동기화를 모니터링하기 위해 [상태 점검(health check)](https://www.palantir.com/docs/foundry/maintaining-pipelines/recommended-health-checks/#optional-checks)을 사용합니다. OSv1에는 객체 타입마다 동기화 잡이 하나뿐이며, 사용자는 이 동기화 잡에 직접 상태 점검을 정의할 수 있습니다.

<a id="debug-a-pipeline"></a>
## 파이프라인 디버깅 (Debug a pipeline)

Foundry 빌드 잡은 여러 이유로 실패할 수 있습니다. 객체 타입의 백킹 데이터소스에 `View` 권한이 있는 사용자는 객체 타입의 **Datasources** 탭에 있는 **Live pipeline** 대시보드에서 파이프라인 오류를 확인할 수 있습니다. 아래 스크린샷처럼 파이프라인 그래프에서 실패한 잡을 고른 다음 **Failed job**을 선택합니다.

![파이프라인 디버깅](https://www.palantir.com/docs/resources/foundry/object-indexing/pipeline3.jpg)

또는 [Builds 애플리케이션](https://www.palantir.com/docs/foundry/data-integration/application-reference/#builds)으로 이동해 왼쪽 패널의 검색 필터에서 객체 타입으로 필터링하면, 해당 객체 타입의 모든 빌드 잡을 나열할 수 있습니다.

![빌드 검색](https://www.palantir.com/docs/resources/foundry/object-indexing/pipeline4.png)

> **중간 요약**: Data Health의 모니터링 뷰로 파이프라인 잡의 상태와 데이터 신선도 지연을 감시할 수 있고, 실패한 잡은 Datasources 탭의 Live pipeline 대시보드나 Builds 애플리케이션에서 확인합니다.

## 정리

- Funnel 배치 파이프라인은 Changelog, Merge changes, Indexing, Hydration 네 개의 빌드 잡으로 데이터와 사용자 편집을 OSv2에 인덱싱합니다.
- Live 파이프라인은 데이터소스 갱신 때와, 편집이 있으면 6시간마다 실행되어 편집을 영구 저장합니다. 스키마 변경 시에는 Replacement 파이프라인이 백그라운드에서 만들어져 Live 파이프라인을 대체합니다.
- 기본은 변경된 행만 처리하는 증분 인덱싱이며, 증분 데이터셋은 "가장 최근 트랜잭션이 이긴다" 규칙과 트랜잭션당 기본 키 한 행 규칙을 따릅니다.
- 행의 80% 이상 변경, Replacement 파이프라인 필요, 사용자 요청 시에는 전체 재인덱싱합니다.
- 모니터링 뷰로 잡 상태와 신선도를 감시하고, Live pipeline 대시보드나 Builds 애플리케이션으로 실패를 디버깅합니다.
