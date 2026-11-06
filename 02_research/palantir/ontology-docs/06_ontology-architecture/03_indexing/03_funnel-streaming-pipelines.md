# Funnel 스트리밍 파이프라인 (Funnel streaming pipelines)

- 원문: https://www.palantir.com/docs/foundry/object-indexing/funnel-streaming-pipelines/
- 사이드바 위치: Ontology architecture > Indexing > Funnel streaming pipelines

이 페이지는 Foundry 스트림을 입력 데이터소스로 사용해 데이터를 수 초에서 수 분 안에 온톨로지에 인덱싱하는 Funnel 스트리밍 파이프라인을 설명합니다. 배치 방식은 데이터셋 빌드가 끝나야 반영되지만, 스트리밍 방식은 레코드가 도착하는 대로 계속 반영하므로 지연 시간에 민감한 운영 워크플로에 쓰입니다. 현재 제약, 설정 방법(컴퓨트 프로필, 일관성 보장 수준), 디버깅 방법을 다룹니다.

[배치 방식의 온톨로지 데이터 인덱싱](02_funnel-batch-pipelines.md)에 더해, Object Storage v2는 [Foundry 스트림(stream)](https://www.palantir.com/docs/foundry/data-integration/streams/)을 [입력 데이터소스](../02_object-permissioning/04_managing-object-security.md#object-input-data-sources)로 사용해 지연 시간이 짧은 스트리밍 데이터 인덱싱을 지원합니다. 스트림은 비스트리밍 Foundry 데이터셋에 쓰이는 배치 인프라에서 벗어남으로써, 수 초에서 수 분 단위로 Foundry 온톨로지에 데이터를 인덱싱할 수 있게 하여 지연 시간에 민감한 운영 워크플로를 지원합니다.

**참고**: 온톨로지 스트리밍 동작에 대해 더 궁금한 점이 있으면 [자주 묻는 질문](06_faq.md#can-i-backfill-large-scale-historical-data-for-object-types-with-streaming-datasources) 문서를 참고하십시오.

스트리밍 파이프라인의 성능과 지연 시간에 대한 안내는 [스트리밍 성능 고려 사항](https://www.palantir.com/docs/foundry/building-pipelines/streaming-performance-considerations/) 문서를 참고하십시오.

**설명**: 데이터셋은 "어느 시점의 전체 테이블" 단위로 갱신되는 반면, 스트림은 레코드(행) 하나하나가 끝없이 이어지는 이벤트 흐름입니다. 예를 들어 항공기 위치 센서가 초마다 `{aircraft_id: A1, lat: 37.5, lon: 127.0, ts: 12:00:01}` 같은 레코드를 보내면, 스트리밍 파이프라인은 이 레코드를 받는 즉시 Aircraft 객체 A1의 위치 속성을 갱신합니다.

<a id="current-product-limitations-of-streaming-object-types"></a>
## 스트리밍 객체 타입의 현재 제품 제약 (Current product limitations of streaming object types)

Object Storage v2의 스트리밍은 "가장 최근 업데이트가 이긴다(most recent update wins)" 전략을 사용하며, 모든 스트림을 changelog 스트림처럼 취급합니다. 소스에서 이벤트가 순서가 뒤섞인 채 들어오면 온톨로지에 잘못된 데이터가 남게 됩니다. 입력 스트림의 순서를 보장할 수 있다면, Object Storage v2 스트리밍은 그 순서 그대로 업데이트를 처리합니다.

**설명**: "가장 최근"은 이벤트가 실제로 발생한 시각이 아니라 스트림에 도착한 순서를 기준으로 합니다. A1의 위치 레코드가 12:00:05 것이 먼저, 12:00:03 것이 나중에 도착하면 A1의 최종 위치는 더 오래된 12:00:03 값이 됩니다. 그래서 상류(upstream)에서 순서를 맞춰 보내야 합니다.

온톨로지 스트리밍 동작과 그 기능 집합은 아직 활발히 개발 중입니다. 온톨로지 스트리밍을 사용하기 전에 고려해야 할 현재 제품 제약은 다음과 같습니다.

* 스트리밍 객체 타입에서는 사용자 편집(edit)이 지원되지 않습니다. 우회 방법으로, 사용자 편집을 데이터 변경으로 만들어 입력 스트림에 밀어 넣거나, 비스트리밍 입력 데이터소스를 가진 객체 타입을 하나 더 두고 사용자가 그 보조 객체 타입에서 편집하도록 할 수 있습니다. 또는 객체의 백킹을 [직접 데이터소스(direct datasource)](04_direct-datasources.md)로 바꾸면 스트림 기반 객체 타입에서도 편집을 활성화할 수 있습니다.
* [다중 데이터소스 객체 타입(MDO)](../02_object-permissioning/06_multi-datasource-objects.md)은 스트리밍 객체 타입에서 지원되지 않습니다.
* [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)을 제외한 다른 Foundry 프런트엔드 애플리케이션은 실시간 데이터 새로 고침을 지원하지 않습니다. 이 애플리케이션들은 원래 스트리밍 업데이트를 전제로 만들어지지 않았기 때문입니다. 스트리밍 객체 타입의 온톨로지 데이터는 계속 바뀌지만, Workshop 밖에서 새 데이터를 보려면 그때마다 새로 고침해야 합니다.
* Ontology Manager의 객체 타입 **Datasources** 탭에서 사용자는 Funnel 배치 파이프라인 실패와 유효하지 않은 레코드에 대한 [모니터](02_funnel-batch-pipelines.md#monitor-funnel-pipelines)를 설정할 수 있습니다. 현재 스트림 데이터소스를 가진 객체 타입에 대해서는 모니터나 지표(예: 파이프라인 지연 시간)를 지원하지 않습니다.
* 레코드 크기는 1MB를 넘을 수 없고, 객체 타입은 속성(property)을 250개보다 많이 가질 수 없습니다. 더 큰 레코드를 온톨로지로 스트리밍해야 한다면, 더 작은 객체 타입들로 이루어진 다른 온톨로지 모델을 고려해야 합니다.

> **중간 요약**: 스트리밍은 도착 순서 기준 "최근 업데이트 우선"으로 동작하므로 입력 순서가 중요합니다. 사용자 편집, MDO, Workshop 밖의 실시간 새로 고침, 모니터링은 지원되지 않고, 레코드 1MB와 속성 250개 한도가 있습니다.

<a id="configuring-streaming-object-types"></a>
## 스트리밍 객체 타입 설정하기 (Configuring streaming object types)

스트림 입력 데이터소스를 가진 객체 타입은 다른 Foundry 온톨로지 객체 타입과 마찬가지로 [Pipeline Builder](https://www.palantir.com/docs/foundry/pipeline-builder/outputs-add-ontology-output/)나 [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)에서 직접 설정합니다.

스트림 데이터소스는 [다대다(many-to-many) 링크 타입](../../02_define-ontologies/02_object-and-link-types/06_link-types/02_create-link-type.md)에도 설정할 수 있습니다.

아직 입력 스트림이 설정되어 있지 않다면, [Data Connection 애플리케이션에서 기존 스트림과 통합](https://www.palantir.com/docs/foundry/data-connection/set-up-streaming-sync/)하거나 [Pipeline Builder에서 스트림 파이프라인을 구축](https://www.palantir.com/docs/foundry/building-pipelines/create-stream-pipeline-pb/)해서 만들 수 있습니다.

새 객체 타입을 만든 뒤(또는 기존 객체 타입을 사용해), Ontology Manager의 **Datasources** 탭으로 이동하고, 아래와 같이 **Backing datasource** 섹션에서 스트림 입력 데이터소스를 선택한 다음, 변경 사항을 Foundry 온톨로지에 저장합니다.

![온톨로지 스트리밍 설정](https://www.palantir.com/docs/resources/foundry/object-indexing/stream_pipeline.png)

입력 데이터소스 스트림에 대한 추가 설정이 필요하면, 아래와 같이 줄임표(ellipses) 버튼을 선택해 더 많은 옵션을 엽니다.

![추가 스트리밍 설정](https://www.palantir.com/docs/resources/foundry/object-indexing/stream_config.png)
![추가 스트리밍 설정](https://www.palantir.com/docs/resources/foundry/object-indexing/stream_datasource_configuration.png)

**Stream configuration** 섹션은 객체 타입의 스트리밍 잡을 최적화하는 옵션을 제공합니다.

* **Stream compute profile**(스트림 컴퓨트 프로필): 기본적으로 객체 타입의 스트리밍 잡은 대부분의 입력 스트림에 적합한 컴퓨트 프로필을 사용합니다. 하지만 처리량(throughput)이 매우 높은 스트림을 백킹으로 하는 객체 타입은 파이프라인이 뒤처지지 않도록 더 많은 리소스가 필요할 수 있습니다. 반대로 처리량이 낮은 스트림을 백킹으로 하는 객체 타입은 더 작은 프로필을 사용해 컴퓨트 리소스 비용을 아낄 수 있습니다. 사용 가능한 옵션 중 적합한 것이 없으면 Palantir 담당자에게 문의하십시오.
* **Stream consistency guarantee**(스트림 일관성 보장): 기본적으로 객체 타입의 스트리밍 잡은 정확히 한 번(exactly-once) 일관성 보장을 사용합니다. 이 방식은 최소 한 번(at-least-once)보다 지연 시간이 더 있지만, Foundry 애플리케이션이 객체 집합(object set) 업데이트를 정확히 한 번 받도록 보장합니다. 최소 한 번 일관성 보장을 활성화하면 지연 시간이 줄어들지만, 드물게 객체 집합이 바뀔 때 Foundry 애플리케이션이 중복 업데이트를 받을 수 있습니다. 예를 들어 객체 집합 기반 자동화(automation)가 여러 번 트리거될 수 있습니다. 지연 시간에 민감한 객체 타입이라면 최소 한 번 방식의 활성화를 고려하십시오.

![Stream configuration 섹션.](https://www.palantir.com/docs/resources/foundry/object-indexing/stream-configuration.png)

**주의**: 객체 타입의 스트림 설정을 수정하면 연결된 스트리밍 잡이 재시작되므로, 새 스트리밍 레코드의 처리가 일시적으로 지연됩니다.

**설명**: exactly-once와 at-least-once는 분산 시스템의 메시지 전달 보장 수준입니다. 장애가 나서 레코드를 다시 처리할 때, exactly-once는 이미 처리한 레코드인지 확인하는 추가 작업(체크포인트 동기화 등)을 거쳐 결과가 한 번만 반영되게 하고, at-least-once는 이 확인을 생략해 빠른 대신 같은 변경이 두 번 전달될 수 있습니다. "Priority가 High인 티켓이 생기면 알림 발송" 같은 자동화가 있다면, at-least-once에서는 드물게 알림이 두 번 갈 수 있다는 뜻입니다.

> **중간 요약**: 스트리밍 객체 타입은 Pipeline Builder나 Ontology Manager의 Datasources 탭에서 스트림을 백킹 데이터소스로 지정해 만들고, 컴퓨트 프로필과 일관성 보장(exactly-once 또는 at-least-once)을 조정할 수 있습니다. 설정 변경은 스트리밍 잡을 재시작시킵니다.

<a id="debugging-streaming-pipelines"></a>
## 스트리밍 파이프라인 디버깅 (Debugging streaming pipelines)

스트림과 온톨로지 사이의 인터페이스는 개념적으로 [changelog 데이터셋](02_funnel-batch-pipelines.md#changelog)과 비슷하다고 볼 수 있습니다. 입력 스트림의 각 레코드는 온톨로지에 기록될 각 속성의 데이터를 담고 있습니다. 각 레코드는 기본 키(primary key)로 지정된 객체 하나의 모든 속성을 갱신합니다. 삭제는 입력 스트림에 메타데이터를 설정해 입력 레코드에서 지정할 수 있습니다.

Funnel은 데이터소스 스트림에 기록된 순서대로 레코드를 인덱싱하므로, 해당 스트림은 기본 키로 파티셔닝되고 이벤트 타임스탬프로 정렬되어 있어야 합니다. 이는 상류의 [Pipeline Builder](https://www.palantir.com/docs/foundry/pipeline-builder/core-concepts/#pipeline-outputs) 파이프라인에서 처리할 수 있습니다.

스트림 파이프라인에 문제가 있다면 [실패하는 스트림 디버깅](https://www.palantir.com/docs/foundry/optimizing-pipelines/debug-stream/) 문서를 참고하십시오.

객체 타입의 스트리밍 잡에 대한 세부 정보와 지표를 보려면 파이프라인 다이어그램에서 **Stream** 버블을 선택합니다.

![스트리밍 잡 세부 정보와 지표 확인.](https://www.palantir.com/docs/resources/foundry/object-indexing/stream-details-metrics.gif)

**설명**: "각 레코드가 객체의 모든 속성을 갱신한다"는 것은 부분 업데이트가 아니라 행 전체 교체라는 뜻입니다. A1의 레코드에 `lat`, `lon`만 있고 `status` 값이 비어 있다면 `status`도 빈 값으로 덮어써질 수 있으므로, 레코드마다 객체의 전체 속성 값을 담아 보내야 합니다. 또 "기본 키로 파티셔닝"은 같은 객체의 레코드가 같은 파티션에 들어가게 해서, 그 파티션 안에서 타임스탬프 순서가 유지되도록 하기 위한 것입니다.

> **중간 요약**: 스트림 레코드 하나는 객체 하나의 전체 속성을 교체하는 changelog 행으로 취급되며, 기록 순서대로 인덱싱되므로 상류에서 기본 키 파티셔닝과 타임스탬프 정렬을 해 두어야 합니다.

## 정리

- Funnel 스트리밍 파이프라인은 Foundry 스트림을 입력으로 받아 수 초에서 수 분 단위로 OSv2 온톨로지에 데이터를 인덱싱합니다.
- 도착 순서 기준 "가장 최근 업데이트가 이긴다" 전략을 쓰므로 입력 스트림의 순서 보장이 중요합니다.
- 사용자 편집(직접 데이터소스로 우회 가능), MDO, Workshop 밖의 실시간 새로 고침, 모니터링은 지원되지 않으며 레코드 1MB와 속성 250개 한도가 있습니다.
- Datasources 탭에서 스트림을 백킹 데이터소스로 지정하고, 컴퓨트 프로필과 exactly-once 또는 at-least-once 일관성 보장을 선택할 수 있습니다.
- 각 레코드는 객체의 전체 속성을 갱신하므로 상류 파이프라인에서 기본 키 파티셔닝과 이벤트 타임스탬프 정렬을 해야 합니다.
