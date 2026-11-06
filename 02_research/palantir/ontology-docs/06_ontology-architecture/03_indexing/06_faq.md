# 인덱싱 FAQ (FAQ)

- 원문: https://www.palantir.com/docs/foundry/object-indexing/faq/
- 사이드바 위치: Ontology architecture > Indexing > FAQ

이 페이지는 데이터를 온톨로지(Ontology)의 객체 데이터베이스로 옮겨 넣는 인덱싱(indexing) 과정에 대해 자주 묻는 질문을 모은 것입니다. 인덱싱 완료 여부 확인, 실패한 작업의 재시도, 데이터 크기 제한, 그리고 스트리밍 데이터소스를 쓰는 객체 타입의 지연 시간, 처리량, 비용, 보존 기간 같은 운영상의 질문을 다룹니다. 앞의 Funnel 배치 파이프라인, Funnel 스트리밍 파이프라인 페이지를 읽은 뒤 보면 이해가 쉽습니다.

**설명**: 인덱싱(indexing)은 원본 데이터셋의 행을 검색과 조회가 빠른 저장소(여기서는 Object Storage v2, 줄여서 OSv2)에 객체 형태로 적재하는 작업입니다. 데이터베이스에서 인덱스를 만들면 `WHERE` 조건 검색이 빨라지는 것처럼, 온톨로지 애플리케이션은 원본 데이터셋을 직접 읽지 않고 이렇게 인덱싱된 객체를 조회합니다. Funnel은 이 인덱싱 파이프라인을 실행하는 Foundry 서비스의 이름입니다.

<a id="how-do-i-know-when-an-object-type-has-been-indexed-into-osv2"></a>
## 객체 타입이 OSv2에 인덱싱되었는지 어떻게 알 수 있나요? (How do I know when an object type has been indexed into OSv2?)

Ontology Manager 애플리케이션에는 Funnel 파이프라인 안의 여러 작업(job) 상태를 보여 주는 전용 파이프라인 그래프가 있습니다. 그래프의 Object Storage v2 노드에 초록색 체크 표시가 있으면 인덱싱이 완료되어 해당 객체 타입을 OSv2에서 조회할 준비가 되었다는 뜻입니다.

![인덱싱 상태 v2](https://www.palantir.com/docs/resources/foundry/object-indexing/faq_indexing.png)

> **중간 요약**: 인덱싱 완료 여부는 Ontology Manager의 파이프라인 그래프에서 Object Storage v2 노드의 초록색 체크 표시로 확인합니다.

<a id="why-might-an-indexing-job-fail-even-though-it-was-successfully-registered-with-object-storage-v1-phonograph-before"></a>
## 이전에 Object Storage v1(Phonograph)에는 등록이 잘 되었는데 인덱싱 작업이 실패하는 이유는 무엇인가요? (Why might an indexing job fail even though it was successfully registered with Object Storage v1 (Phonograph) before?)

OSv1과 OSv2는 데이터 검증(validation) 방식이 조금 다릅니다.

OSv1은 하부의 분산 문서 저장소 및 검색 엔진과 강하게 결합되어 있기 때문에, 그 동작이 대체로 하부 데이터 저장소의 동작에 따라 결정됩니다. OSv2는 온톨로지로 들어가는 데이터의 품질을 보장하고, OSv1에 비해 더 결정적인(deterministic) 동작과 시스템 전반의 높은 가독성을 제공하기 위해 더 엄격한 검증을 수행합니다.

따라서 OSv1에서는 받아들여지던 데이터가 OSv2에서는 검증 오류를 일으키는 인덱싱 파이프라인이 있을 수 있습니다. 이런 호환성을 깨는 변경 사항의 자세한 목록은 [OSv1과 OSv2 사이의 온톨로지 호환성 변경(breaking changes)](../01_overview-and-getting-started/02_object-storage-v2-breaking-changes.md) 문서를 참고하세요.

**설명**: "결정적인 동작"이란 같은 입력을 주면 언제나 같은 결과가 나온다는 뜻입니다. 예를 들어 기본 키(primary key) 열에 같은 값이 두 번 들어 있는 데이터셋이 있다고 합시다. 검증이 느슨한 시스템은 둘 중 어느 행이 남을지 상황에 따라 달라질 수 있지만, 엄격한 시스템은 이를 오류로 거부해서 결과가 흔들리지 않게 합니다. 그래서 OSv1에서 문제없이 들어가던 데이터가 OSv2에서는 실패할 수 있습니다.

> **중간 요약**: OSv2는 데이터 품질과 결정적 동작을 위해 OSv1보다 검증이 엄격하므로, 예전에 통과하던 데이터가 OSv2에서 실패할 수 있습니다.

<a id="one-of-the-jobs-failed-but-might-succeed-if-i-retry-how-do-i-trigger-a-rebuild"></a>
## 작업 하나가 실패했는데 다시 시도하면 성공할 것 같습니다. 재빌드는 어떻게 시작하나요? (One of the jobs failed but might succeed if I retry. How do I trigger a rebuild?)

OSv2는 작업 재시도를 포함해 작업의 모든 측면을 관리합니다. 작업을 다시 빌드하면 해결될 수 있는 일시적인 오류로 작업이 실패하면, OSv2는 약 5분 뒤에 자동으로 작업을 재시도합니다. 작업이 최종적으로(terminally) 실패했다고 OSv2가 판단하면(예: 잘못된 데이터 형식 때문에), 새 데이터가 들어왔을 때만 자동으로 재시도합니다. 객체 타입이 제한된 뷰(restricted view) 데이터소스를 기반으로 하는 경우에는 데이터나 정책(policy)이 바뀔 때 작업이 시작됩니다.

**설명**: 일시적인 오류(transient error)는 네트워크 순간 장애나 일시적인 자원 부족처럼 같은 작업을 다시 실행하면 저절로 해결될 가능성이 있는 오류입니다. 반대로 최종 실패는 날짜 열에 "abc" 같은 문자열이 들어 있는 경우처럼 데이터 자체가 잘못되어 몇 번을 다시 해도 같은 결과가 나오는 오류입니다. 이 경우에는 원본 데이터를 고쳐서 새 데이터가 들어와야 재시도가 의미가 있습니다.

> **중간 요약**: 사용자가 직접 재빌드할 필요가 없습니다. 일시적 오류는 약 5분 뒤 자동 재시도되고, 최종 실패는 새 데이터가 들어올 때 재시도됩니다.

<a id="is-there-a-limit-to-the-size-of-data-that-can-be-indexed"></a>
## 인덱싱할 수 있는 데이터 크기에 제한이 있나요? (Is there a limit to the size of data that can be indexed?)

인덱스 크기는 주로 해당 객체 타입이 인덱싱되는 객체 데이터베이스의 저장 공간에 의해 제한됩니다. 예를 들어 OSv2 데이터 저장소에서는 검색 노드(search node)의 디스크 공간이 그 한도가 됩니다.

디스크 공간이 부족하면 인덱싱 작업이 성공하지 못하며, Ontology Manager 애플리케이션의 파이프라인 그래프에 근본 원인이 표시됩니다. 디스크 공간 오류가 발생하면 Palantir 담당자에게 문의하세요.

> **중간 요약**: 고정된 크기 제한은 없고, 객체 데이터베이스(OSv2의 경우 검색 노드)의 디스크 공간이 실제 한도입니다.

<a id="can-i-backfill-large-scale-historical-data-for-object-types-with-streaming-datasources"></a><a id="can-i-backfill-large-scale-historical-data-for-object-types-with-streaming-datasourcesdocsfoundryobject-indexingfunnel-streaming-pipelines"></a>
## [스트리밍 데이터소스를 쓰는 객체 타입](03_funnel-streaming-pipelines.md)에 대규모 과거 데이터를 백필(backfill)할 수 있나요? (Can I backfill large scale historical data for object types with streaming datasources?)

스트리밍 데이터소스를 기반으로 하는 객체 타입을 동기화할 때는 두 단계가 있습니다. 내부 스트림 생성(internal stream creation)과 인덱싱입니다. 스트리밍 인덱싱 작업은 Spark를 사용해 과거 스트리밍 데이터의 초기 처리를 대규모로 병렬화하므로, [Funnel 배치 파이프라인](02_funnel-batch-pipelines.md)과 비슷한 인덱싱 지연 시간을 가집니다. 이 인덱싱 지연 시간은 [라이브 온톨로지 데이터에 대한 사용자 편집(edit)](../04_object-edits-and-materializations/02_how-edits-applied.md#user-edits-on-live-data)과도 비슷합니다. 보통 병목이 되는 것은 내부 스트림 생성 단계입니다. 이 단계는 Palantir의 스트리밍 인프라를 사용해 데이터소스를 레코드 단위로 하나씩 처리합니다.

**설명**: 백필(backfill)은 시스템을 새로 연결할 때 과거에 쌓인 데이터를 한꺼번에 채워 넣는 작업입니다. 위 내용은 인덱싱 단계 자체는 Spark로 병렬 처리해서 빠르지만, 그 앞의 내부 스트림 생성 단계는 레코드를 하나씩 처리하므로 과거 데이터가 많을수록 이 단계가 오래 걸린다는 뜻입니다.

> **중간 요약**: 백필은 가능합니다. 인덱싱은 Spark 병렬 처리로 빠르지만, 레코드 단위로 처리하는 내부 스트림 생성 단계가 주된 병목입니다.

<a id="what-is-the-expected-latency-for-streaming-into-the-ontology"></a>
## 온톨로지로 스트리밍할 때 예상 지연 시간은 얼마인가요? (What is the expected latency for streaming into the Ontology?)

[Funnel 스트리밍 파이프라인](03_funnel-streaming-pipelines.md)에서 가장 시간이 많이 드는 부분은 "정확히 한 번(exactly once)" 스트리밍 일관성을 보장하기 위한 Flink 체크포인팅(checkpointing)입니다. 기본 체크포인트 주기는 1초에 한 번이므로, 입력 스트림에 데이터가 도착한 뒤 온톨로지에 인덱싱되기까지의 지연 시간은 이 값이 대부분을 차지합니다. Palantir는 체크포인트 주기를 줄이거나 아예 없애는 방식으로 비용, 성능, 지연 시간 사이의 절충을 평가하는 실험을 계속 진행하고 있습니다.

필요한 경우 이 동작을 설정하려면 Palantir Support에 문의하세요.

**설명**: Flink는 스트림 데이터를 처리하는 오픈 소스 엔진입니다. 체크포인트는 처리 중인 상태를 주기적으로 저장해 두는 것으로, 장애가 나면 마지막 체크포인트부터 다시 처리합니다. "정확히 한 번"은 장애와 재시작이 있어도 각 레코드가 결과에 중복이나 누락 없이 정확히 한 번만 반영된다는 보장입니다. 체크포인트가 확정된 뒤에 결과를 내보내기 때문에, 체크포인트 주기(1초)가 곧 지연 시간의 주요 원인이 됩니다.

> **중간 요약**: 스트리밍 지연 시간은 주로 Flink 체크포인팅 주기(기본 1초)에 의해 결정됩니다.

<a id="what-is-the-expected-throughput-for-streaming-into-ontology"></a>
## 온톨로지로 스트리밍할 때 예상 처리량은 얼마인가요? (What is the expected throughput for streaming into Ontology?)

인덱싱 처리량은 [Object Storage v2 객체 데이터베이스](../01_overview-and-getting-started/01_overview.md#object-storage-v2-architecture)로 들어가는 객체 타입 하나당 초당 2MB로 제한됩니다. 더 높은 인덱싱 처리량이 필요하면 Palantir Support에 문의하세요.

<a id="can-i-specify-a-timestamp-that-my-objects-will-be-deduplicated-by-when-using-stream-datasources-in-the-ontology"></a>
## 온톨로지에서 스트림 데이터소스를 쓸 때 객체 중복 제거 기준이 되는 타임스탬프를 지정할 수 있나요? (Can I specify a timestamp that my objects will be deduplicated by when using stream datasources in the Ontology?)

아니요. [Funnel 스트리밍 파이프라인](03_funnel-streaming-pipelines.md)은 인덱싱할 때 입력 스트림의 순서를 그대로 유지합니다. 데이터는 스트림에 순서대로 써야 합니다. 이는 상위(upstream) 스트리밍 파이프라인에서 이벤트 타임스탬프를 기준으로 데이터를 윈도잉(windowing)하고, 데이터가 해시 파티셔닝되도록 기본 키를 지정하는 방식으로 할 수 있습니다.

**설명**: 스트리밍에서는 같은 기본 키를 가진 레코드가 여러 번 들어오면 나중에 도착한 레코드가 객체의 최종 상태가 됩니다. 예를 들어 `order_id=7`에 대해 "배송 중"(10:00 발생)과 "배송 완료"(10:05 발생)가 순서가 뒤바뀌어 도착하면 최종 상태가 "배송 중"으로 남습니다. 해시 파티셔닝은 기본 키의 해시값으로 파티션을 정하는 방식이라, 같은 키의 레코드는 항상 같은 파티션에 들어가 그 안에서 순서가 유지됩니다. 따라서 순서 정리는 온톨로지가 아니라 상위 파이프라인의 책임입니다.

> **중간 요약**: 스트림 객체 타입은 처리량이 객체 타입당 초당 2MB로 제한되고, 타임스탬프 기준 중복 제거는 지원하지 않으므로 상위 파이프라인에서 순서를 맞춰 써야 합니다.

<a id="does-ontology-streaming-support-change-data-capture-cdc-workflows"></a>
## 온톨로지 스트리밍이 변경 데이터 캡처(CDC) 워크플로를 지원하나요? (Does Ontology streaming support change data capture (CDC) workflows?)

[Funnel 스트리밍 파이프라인](03_funnel-streaming-pipelines.md)은 생성, 수정, 삭제 워크플로를 지원합니다. 삭제 메타데이터를 설정하는 방법은 [변경 데이터 캡처(change data capture)](https://www.palantir.com/docs/foundry/data-integration/change-data-capture/) 문서에서 더 자세히 볼 수 있습니다.

**설명**: 변경 데이터 캡처(CDC)는 원본 데이터베이스에서 일어난 INSERT, UPDATE, DELETE 같은 변경 내역을 이벤트 스트림으로 뽑아 다른 시스템에 전달하는 방식입니다. 삭제는 "이 키의 행이 삭제되었다"는 표시(삭제 메타데이터)가 붙은 레코드로 전달됩니다.

<a id="can-i-write-partial-rows-to-the-ontology-when-using-stream-datasources-can-i-update-a-few-properties-at-a-time-instead-of-providing-the-entire-object"></a>
## 스트림 데이터소스를 쓸 때 온톨로지에 일부 행만 쓸 수 있나요? 객체 전체를 주지 않고 속성 몇 개만 업데이트할 수 있나요? (Can I write partial rows to the Ontology when using stream datasources? Can I update a few properties at a time instead of providing the entire object?)

현재는 불가능합니다. 객체 전체를 완성하는 작업은 상위 파이프라인에서 해야 합니다. 규모 문제 때문에 [상태 유지 스트리밍(stateful streaming)](https://www.palantir.com/docs/foundry/building-pipelines/stream-vs-batch/#state-management)으로 이 문제가 해결되지 않는다면 Palantir Support에 문의하세요.

**설명**: 예를 들어 `Truck` 객체에 `location`과 `fuel_level` 속성이 있을 때, 위치만 바뀐 레코드를 `{truck_id: T1, location: ...}`처럼 보내면 안 되고 `fuel_level`까지 모두 채운 전체 레코드를 보내야 합니다. 상태 유지 스트리밍은 파이프라인이 키별 마지막 값을 기억해 두었다가 빠진 속성을 채워 넣는 방식으로 이를 해결합니다.

<a id="can-i-use-ontology-streaming-for-many-to-many-link-types"></a><a id="can-i-use-ontology-streaming-for-many-to-many-link-typesdocsfoundryobject-link-typescreate-link-type"></a>
## [다대다(many-to-many) 링크 타입](../../02_define-ontologies/02_object-and-link-types/06_link-types/02_create-link-type.md)에 온톨로지 스트리밍을 쓸 수 있나요? (Can I use Ontology streaming for many-to-many link types?)

네, 지원됩니다. 스트리밍 데이터소스로 온톨로지 타입을 설정하는 방법은 [관련 문서](03_funnel-streaming-pipelines.md#configuring-streaming-object-types)에서 더 알아보세요.

<a id="is-streaming-supported-for-object-databases-other-than-object-storage-v2"></a><a id="is-streaming-supported-for-object-databasesobject-databases-other-than-object-storage-v2docsfoundryobject-backendoverviewobject-storage-v2-architecture-materializationsdocsfoundryobject-editsmaterializations-or-automatedocsfoundryautomateoverview-for-example"></a>
## [Object Storage v2](../01_overview-and-getting-started/01_overview.md#object-storage-v2-architecture) 외의 [객체 데이터베이스](../05_object-databases/01_object-storage-v1.md)(예: [머티리얼라이제이션](../04_object-edits-and-materializations/06_materializations.md)이나 [Automate](https://www.palantir.com/docs/foundry/automate/overview/))에서도 스트리밍이 지원되나요? (Is streaming supported for object databases other than Object Storage v2?)

온톨로지 스트리밍은 현재 Object Storage v2 객체 데이터베이스에서만 지원됩니다. 다른 객체 데이터베이스에서 이 기능이 필요하면 Palantir Support에 문의하세요.

<a id="are-materializations-supported-for-object-types-with-stream-datasources"></a><a id="are-materializationsdocsfoundryobject-editsmaterializations-supported-for-object-types-with-stream-datasources"></a>
## 스트림 데이터소스를 쓰는 객체 타입에서 [머티리얼라이제이션](../04_object-edits-and-materializations/06_materializations.md)이 지원되나요? (Are materializations supported for object types with stream datasources?)

아니요. 스트림 데이터소스를 쓰는 객체 타입에서는 사용자 편집이 지원되지 않으므로, 머티리얼라이즈된 데이터셋을 만들어도 스트림의 아카이브 데이터셋과 다를 것이 없습니다. 현재 아키텍처에서는 데이터셋 형태로 중복 제거된 뷰를 제공할 수 없습니다.

**설명**: 머티리얼라이제이션(materialization)은 원본 데이터와 사용자 편집을 합친 객체의 최신 상태를 데이터셋으로 내보내는 기능입니다(자세한 내용은 Materializations 페이지 참고). 편집이 없으면 합칠 대상이 없으므로 원본 스트림을 그대로 쌓은 아카이브 데이터셋과 내용상 차이가 없다는 뜻입니다.

> **중간 요약**: 스트림 객체 타입은 생성, 수정, 삭제(CDC)와 다대다 링크 타입을 지원하지만, 부분 행 업데이트, OSv2 외 객체 데이터베이스, 머티리얼라이제이션은 지원하지 않습니다.

<a id="my-funnel-streaming-pipeline-is-always-running-how-can-i-cancel-it"></a><a id="my-funnel-streaming-pipelinefunnel-streaming-pipelinesmd-is-always-running-how-can-i-cancel-it"></a>
## [Funnel 스트리밍 파이프라인](03_funnel-streaming-pipelines.md)이 항상 실행 중입니다. 어떻게 취소하나요? (My Funnel streaming pipeline is always running. How can I cancel it?)

Funnel 스트리밍 파이프라인은 사용자가 취소할 수 없습니다. 운영 환경의 객체 타입에는 높은 가용성이 필요하기 때문에 Funnel은 스트림을 항상 살아 있게 유지합니다. 이 구성 때문에 프로토타입을 만드는 단계에서는 원치 않는 비용이 생길 수 있습니다. 이것이 사용 사례에 큰 걸림돌이 된다면 Palantir Support에 문의하세요. 또는 프로토타입 단계에서는 객체 타입을 배치 방식으로 바꿔 두는 방법도 있습니다.

<a id="how-can-i-cut-over-my-stream-datasource-from-one-stream-to-another-without-downtime"></a>
## 다운타임 없이 스트림 데이터소스를 한 스트림에서 다른 스트림으로 전환하려면 어떻게 하나요? (How can I cut over my stream datasource from one stream to another without downtime?)

[Funnel 스트리밍 파이프라인](03_funnel-streaming-pipelines.md)에는 새 스트림으로 전환하기 전에 파이프라인이 대체 스트림을 "따라잡았는지(up to date)" 판단하는 휴리스틱이 있습니다. 다음 단계에 따라 데이터소스가 다른 스트림이나 스트림의 다른 브랜치를 가리키도록 바꿀 수 있습니다.

1. 새 로직을 별도의 스트림(또는 다른 브랜치)에서 실행합니다.
2. 새 스트림이 재생(replay)을 마칠 때까지 기다립니다. 예를 들어 모든 과거 레코드가 처리된 뒤까지 기다립니다.
3. 객체 타입의 입력 데이터소스를 새 스트림으로 바꿉니다.
4. Funnel 스트리밍 파이프라인은 새 스트림의 대체 파이프라인이 완전히 인덱싱될 때까지 원래 스트림의 라이브 파이프라인을 유지합니다.
5. Funnel이 전환(cutover)을 마치면 원래 스트림을 끌 수 있습니다.

**설명**: 이 절차의 핵심은 4단계입니다. 데이터소스를 바꾸는 순간 바로 끊는 것이 아니라, 새 파이프라인이 다 준비될 때까지 옛 파이프라인이 계속 객체를 제공하므로 조회가 중단되는 시간(다운타임)이 생기지 않습니다.

<a id="what-are-some-common-mistakes-that-may-lead-to-unintended-consequences"></a>
## 의도치 않은 결과로 이어질 수 있는 흔한 실수는 무엇인가요? (What are some common mistakes that may lead to unintended consequences?)

1. 데이터가 예상과 다르다면 입력 스트림이 예상한 순서대로 정렬되어 있는지 확인하세요.
2. [Funnel 스트리밍 파이프라인](03_funnel-streaming-pipelines.md)은 [Funnel 배치 파이프라인](02_funnel-batch-pipelines.md)과 같은 검증을 수행합니다. 하지만 스트리밍 파이프라인에서는 스트림 처리를 일시 중지할 수 없으므로 사용자 변환(transform)에서 오류를 발생시키는 메커니즘이 없고, 따라서 유효하지 않은 레코드는 버려집니다.

**설명**: 배치 파이프라인에서는 잘못된 행이 있으면 작업 전체가 실패해 문제를 바로 알 수 있습니다. 스트리밍에서는 처리를 멈출 수 없으므로 잘못된 레코드가 조용히 빠집니다. 따라서 일부 객체가 보이지 않는다면 해당 레코드가 검증에서 탈락했을 가능성을 의심해야 합니다.

> **중간 요약**: 스트리밍 파이프라인은 취소할 수 없고, 스트림 전환은 새 파이프라인 준비가 끝날 때까지 옛 파이프라인을 유지해 다운타임 없이 이뤄집니다. 순서가 어긋난 입력과 조용히 버려지는 잘못된 레코드에 주의해야 합니다.

<a id="what-is-the-cost-of-ontology-streaming"></a>
## 온톨로지 스트리밍 비용은 얼마인가요? (What is the cost of Ontology streaming?)

[Funnel 스트리밍 파이프라인](03_funnel-streaming-pipelines.md)의 컴퓨팅 비용은 일반 스트리밍 리소스와 같은 방식으로 계산됩니다. 스트리밍 리소스 비용에 대한 자세한 내용은 [스트리밍 컴퓨팅 사용량(streaming compute usage)](https://www.palantir.com/docs/foundry/building-pipelines/streaming-compute-usage/#calculating-usage) 문서를 참고하세요.

<a id="how-do-retention-windows-work"></a>
## 보존 기간(retention window)은 어떻게 동작하나요? (How do retention windows work?)

보존 기간은 원래 베타 릴리스 시기에 데이터 크기를 제한하는 장치로 개발되었습니다. 그래서 최선 노력(best effort) 방식으로만 구현되어 있습니다. 즉, 보존 기간 안의 객체는 조회할 수 있지만, 보존 기간 밖의 객체는 결국에는 삭제됩니다. 예를 들어 보존 기간을 2주로 설정했고, 스트림 데이터소스의 어떤 객체가 입력 스트림에서 마지막으로 업데이트된 것이 3주 전이라면, 그 객체는 해당 객체 타입에서 삭제될 수 있습니다. 하지만 그 객체가 온톨로지에 며칠 더 남아 있을 수도 있으며, 특정 기간 안에 반드시 삭제된다는 보장은 없습니다.

현재 온톨로지에서 오래된 데이터를 "정리"하는 메커니즘은 [파이프라인 교체(pipeline replacement)](02_funnel-batch-pipelines.md#replacement-pipelines)이며, 기본적으로 2주마다 실행됩니다. 교체가 일어나면 Funnel 스트리밍 파이프라인은 보존 기간의 시작 시점부터 스트림을 다시 재생하므로, 그보다 오래된 객체가 온톨로지에서 제거됩니다. 오래된 객체를 더 자주 삭제해야 한다면 Palantir Support에 문의하세요.

보존 기간을 설정하지 않으면 입력 스트림 소스의 모든 데이터가 온톨로지에 수집됩니다.

**설명**: 동작 순서로 정리하면 다음과 같습니다. 보존 기간이 2주이고 교체 파이프라인이 11월 1일에 실행되면, 파이프라인은 10월 18일 이후의 스트림 레코드만 다시 재생해 새 인덱스를 만듭니다. 10월 10일에 마지막으로 업데이트된 객체는 재생 범위에 없으므로 새 인덱스에 포함되지 않고, 이렇게 해서 삭제됩니다. 교체가 2주마다 일어나기 때문에 보존 기간을 넘긴 객체가 최대 2주 정도 더 남아 있을 수 있습니다.

> **중간 요약**: 보존 기간은 최선 노력 방식이라 기간이 지난 객체의 삭제 시점이 보장되지 않습니다. 실제 정리는 기본 2주마다 실행되는 교체 파이프라인이 보존 기간 시작부터 스트림을 재생하면서 이뤄집니다.

<a id="why-is-my-stream-source-being-indexed-in-batch-or-failing-with-duplicate-errors"></a>
## 스트림 소스가 배치로 인덱싱되거나 중복 오류로 실패하는 이유는 무엇인가요? (Why is my stream source being indexed in batch or failing with duplicate errors?)

[Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)에서는 입력 데이터소스가 스트림이라는 것을 항상 명시적으로 지정해야 합니다. 이는 스트리밍 데이터소스를 쓰는 객체 타입과 스트림을 기반으로 하는 [제한된 뷰(restricted view)](../02_object-permissioning/05_configuring-rv-access-controls.md) 모두에 해당합니다. 그렇지 않으면 데이터소스가 일반 [Funnel 배치 파이프라인](02_funnel-batch-pipelines.md)으로 인덱싱되는 방식으로 돌아갑니다. 자세한 내용은 [스트리밍 객체 타입 설정](03_funnel-streaming-pipelines.md#configuring-streaming-object-types) 문서를 참고하세요.

**설명**: 중복 오류가 나는 이유는 이렇게 설명할 수 있습니다. 스트림의 아카이브에는 같은 기본 키의 레코드가 여러 번(변경될 때마다) 쌓여 있습니다. 스트리밍 방식은 이를 순서대로 덮어쓰지만, 배치 방식으로 인덱싱하면 이를 하나의 표로 보고 기본 키가 중복된 행이 있다고 판단해 실패합니다.

<a id="can-i-query-object-types-with-streaming-datasources-through-ontology-functions"></a><a id="can-i-query-object-types-with-streaming-datasources-through-ontology-functionsdocsfoundryfunctionsfunctions-on-objects"></a>
## [온톨로지 함수(function)](../../02_define-ontologies/04_functions/13_functions-on-objects/01_functions-on-objects.md)로 스트리밍 데이터소스를 쓰는 객체 타입을 조회할 수 있나요? (Can I query object types with streaming datasources through Ontology functions?)

네. [온톨로지 조회](../01_overview-and-getting-started/01_overview.md#object-set-service-oss)는 스트리밍 객체 타입과 배치 객체 타입에서 똑같이 동작합니다.

> **중간 요약**: 스트림 소스는 Ontology Manager에서 스트림으로 명시해야 하며, 그렇지 않으면 배치로 인덱싱되어 중복 오류가 날 수 있습니다. 조회 방식은 스트리밍과 배치 객체 타입이 같습니다.

## 정리

- 인덱싱 상태는 Ontology Manager 파이프라인 그래프에서 확인하며, 실패한 작업은 OSv2가 자동으로 재시도합니다(일시적 오류는 약 5분 뒤, 최종 실패는 새 데이터가 들어올 때).
- OSv2는 OSv1보다 검증이 엄격해 예전에 통과하던 데이터가 실패할 수 있고, 인덱스 크기는 검색 노드 디스크 공간에 따라 제한됩니다.
- 스트리밍 객체 타입은 지연 시간이 Flink 체크포인트 주기(기본 1초)에 좌우되고, 처리량은 객체 타입당 초당 2MB로 제한되며, 입력 순서를 그대로 따르므로 상위 파이프라인에서 순서와 전체 행을 보장해야 합니다.
- 스트리밍은 CDC와 다대다 링크 타입을 지원하지만 부분 행 업데이트, OSv2 외 객체 데이터베이스, 머티리얼라이제이션은 지원하지 않으며, 파이프라인은 사용자가 취소할 수 없습니다.
- 보존 기간은 최선 노력 방식으로, 기본 2주마다 실행되는 교체 파이프라인이 오래된 객체를 정리합니다.
