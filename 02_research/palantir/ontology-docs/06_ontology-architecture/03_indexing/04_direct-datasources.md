# 직접 데이터소스 (Direct datasources) [Beta]

- 원문: https://www.palantir.com/docs/foundry/object-indexing/direct-datasources/
- 사이드바 위치: Ontology architecture > Indexing > Direct datasources

이 페이지는 데이터 애플리케이션(현재는 Pipeline Builder)이 중간 데이터셋이나 Funnel 배치 단계를 거치지 않고 온톨로지에 직접 쓰는 직접 데이터소스(direct datasource)를 설명합니다. 스트림 기반 객체 타입에서도 사용자 편집(edit)을 허용하고 타임스탬프 기준으로 순서를 맞출 수 있다는 점이 핵심입니다. 설정 방법, 소스 타임스탬프 속성, 디버깅 도구(라이브니스, 지표, 로그), 자주 묻는 질문을 다룹니다.

**참고**: 베타(Beta). 직접 데이터소스는 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며, 사용 중인 환경(enrollment)에서는 제공되지 않을 수 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다.

직접 데이터소스는 스트림 기반 데이터를 백킹으로 하는 객체 타입에 대한 [편집](../04_object-edits-and-materializations/01_overview.md)을 포함해, 온톨로지에 지연 시간이 짧은 쓰기를 제공합니다. 직접 데이터소스를 사용하면 데이터 애플리케이션이 온톨로지에 직접 쓸 수 있습니다. 현재 지원되는 쓰기 애플리케이션(writer application)은 Pipeline Builder뿐입니다.

직접 데이터소스는 처리량(throughput)을 일부 포기하는 대신, 스트림에 대한 사용자 편집과 시간 기반 순서 정렬 같은 더 견고한 온톨로지 쓰기 기능을 제공합니다. 데이터와 편집 모두에 짧은 지연 시간이 필요한 워크플로에 가장 적합합니다. 예를 들어 스트리밍 객체 타입에 대한 편집이나, 작고 잦은 증분 빌드를 하는 배치 객체 타입에서 소스 트랜잭션이 일어난 시점부터 객체가 온톨로지에 나타나기까지의 종단 간(end-to-end) 인덱싱 지연 시간을 받아들일 수 없는 경우입니다.

**설명**: 앞 페이지의 배치 파이프라인에서는 데이터셋 트랜잭션이 생긴 뒤 Changelog, Merge changes, Indexing, Hydration 잡이 차례로 돌아야 객체가 바뀝니다. 5분마다 몇 행씩만 바뀌는 데이터라도 매번 이 잡들을 거쳐야 하므로 지연이 쌓입니다. 직접 데이터소스는 Pipeline Builder가 계산한 결과를 바로 온톨로지에 써 넣는 경로이므로 이런 단계별 대기가 없습니다.

<a id="configure-a-direct-datasource"></a>
## 직접 데이터소스 설정하기 (Configure a direct datasource)

직접 데이터소스는 현재 Pipeline Builder에서만 설정할 수 있습니다. 자세한 내용은 [Pipeline Builder 문서](https://www.palantir.com/docs/foundry/pipeline-builder/outputs-add-ontology-output/#enable-direct-datasources-beta)의 안내를 참고하십시오.

배포하고 나면 객체 타입이 [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)에 나타나고, 그 객체들을 [Insight](https://www.palantir.com/docs/foundry/insight/overview/)와 [Object Explorer](../../05_applications/01_object-explorer/01_overview.md)에서 볼 수 있습니다.

<a id="source-timestamp-property"></a>
## 소스 타임스탬프 속성 (Source timestamp property)

선택적으로 **소스 타임스탬프 속성(source timestamp property)을** 설정해 시간 기반 순서 정렬을 활성화할 수 있습니다. 소스 타임스탬프 속성은 사용자가 제공하는 타임스탬프 속성으로, 객체가 생성되거나 갱신된 시각을 나타내야 합니다. 이 값은 순서가 뒤바뀐 직접 쓰기를 버리는 데 사용됩니다. 어떤 객체에 대한 쓰기가 그 객체의 기존 값보다 이른 소스 타임스탬프 값을 가지고 도착하면, 그 쓰기는 버려집니다.

시간 기반 순서 정렬은 소스 타임스탬프 속성을 설정한 뒤에 제출된 쓰기에만 적용됩니다. 소스 타임스탬프 속성을 설정하기 전에 들어온 순서가 뒤바뀐 쓰기를 바로잡으려면, 상류(upstream) 파이프라인을 재실행(replay)하십시오.

**주의**: 재실행하면 기존 객체가 모두 제거됨(Replaying removes all existing objects). 파이프라인을 재실행하면 객체 뷰(object view)가 초기화되어 기존 객체가 모두 제거됩니다. 재실행하기 전에 이 점을 고려하십시오.

소스 타임스탬프 속성은 객체 타입에 이미 타임스탬프 속성이 정의되어 있어야만 설정할 수 있습니다.

소스 타임스탬프 속성을 설정하려면 다음과 같이 합니다.

1. [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)에서 객체 타입의 **Datasources** 탭으로 이동합니다.
2. **Direct writes** 섹션에서 **Source timestamp**를 찾습니다.
3. **Timestamp property**에서 드롭다운 메뉴로 기존 타임스탬프 속성 하나를 선택합니다. 설정을 제거하려면 선택한 속성 옆의 **x** 아이콘을 선택합니다.

![Ontology Manager에서 직접 데이터소스 객체 타입의 Datasources 탭에 있는 Direct writes 패널의 Source timestamp 섹션.](https://www.palantir.com/docs/resources/foundry/object-indexing/direct-datasource-source-timestamp.png)

**설명**: 스트리밍 파이프라인 페이지의 "도착 순서 기준 최근 업데이트 우선" 문제를 해결하는 장치입니다. `updated_at`을 소스 타임스탬프 속성으로 지정했다고 합시다. A1 객체의 현재 `updated_at`이 12:00:05인데 12:00:03짜리 쓰기가 늦게 도착하면, 이 쓰기는 더 오래된 값이므로 버려지고 A1은 12:00:05 상태를 유지합니다. 데이터베이스에서 `UPDATE ... WHERE updated_at < :new_ts`처럼 조건부로 갱신하는 것과 같은 효과입니다.

> **중간 요약**: 직접 데이터소스는 Pipeline Builder에서만 설정하며, 소스 타임스탬프 속성을 지정하면 더 오래된 타임스탬프의 쓰기를 버려 순서를 보장합니다. 설정 이전 데이터를 바로잡으려면 재실행해야 하지만 재실행은 기존 객체를 모두 지웁니다.

<a id="debugging"></a>
## 디버깅 (Debugging)

<a id="navigate-between-a-direct-datasource-writer-and-its-object-type"></a>
### 직접 데이터소스 쓰기 애플리케이션과 객체 타입 사이 이동하기 (Navigate between a direct datasource writer and its object type)

Ontology Manager의 **Datasources** 탭에서, 직접 데이터소스에 대해 온톨로지에 편집을 써 넣은 Pipeline Builder 파이프라인을 볼 수 있습니다. 파이프라인을 선택하면 Pipeline Builder의 해당 파이프라인으로 이동합니다.

현재 지원되는 쓰기 애플리케이션은 Pipeline Builder뿐입니다.

![Ontology Manager에서 객체 타입의 Datasources 탭에 있는 Direct writers 섹션.](https://www.palantir.com/docs/resources/foundry/object-indexing/direct-datasource-direct-writers.png)

<a id="liveness"></a>
### 라이브니스 (Liveness)

데이터 라이브니스(liveness)는 **Datasources** 탭의 **Object Storage v2** 아래에 표시됩니다. 라이브니스는 현재 객체 뷰의 신선도(freshness)를 판단하는 데 도움이 됩니다.

* **Data:** 온톨로지에 기록된 마지막 직접 쓰기.
* **Schema:** 현재 스키마가 최신인지 여부.
* **Latest edit:** 온톨로지에 기록된 마지막 편집. 해당 객체 타입에 기록된 편집이 없으면 이 필드는 표시되지 않습니다.

![Ontology Manager에서 객체 타입의 Datasources 탭에 있는 Object Storage v2 섹션.](https://www.palantir.com/docs/resources/foundry/object-indexing/direct-datasource-liveness.png)

<a id="stream-metrics"></a>
### 스트림 지표 (Stream metrics)

[Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)에서 Pipeline Builder가 조율하는 쓰기 잡이나 현재 실행 중인 잡의 스트림 지표를 볼 수 있습니다. 객체 타입의 **Datasources** 탭에서 **Object Storage v2**로 이동한 뒤, Live 파이프라인에서 직접 데이터소스 노드를 선택합니다.

* **View metrics** 배너를 선택하면 Flink 스트리밍 잡의 로그, 잡 이력, 그 밖의 지표를 볼 수 있습니다.
* 현재 실행 중인 잡의 정보를 보려면 **Latest job**의 줄임표(ellipses)를 선택한 다음 **View job details**를 선택합니다.

![직접 데이터소스와 최근 잡 실행 시점을 포함한 파이프라인을 보여 주는, Ontology Manager 객체 타입 Datasources 탭의 Live pipeline 섹션.](https://www.palantir.com/docs/resources/foundry/object-indexing/direct-datasource-metrics.png)

<a id="logging"></a>
### 로그 (Logging)

직접 쓰기의 로그를 보는 것은 누락된 객체나 유효하지 않은 쓰기를 디버깅할 때 특히 유용합니다. 유효하지 않은 직접 쓰기가 감지되면 **Datasources** 탭에 배너가 나타납니다. 유효하지 않은 쓰기는 버려지며 온톨로지에 나타나지 않습니다.

유효하지 않은 쓰기를 디버깅하려면 다음과 같이 합니다.

1. **Datasources** 탭으로 이동해 경고 배너를 찾습니다.
2. 배너에서 **View logs**를 선택하면 어떤 기본 키(primary key)가 왜 버려졌는지 볼 수 있습니다.

![Ontology Manager의 Datasources 탭에 표시되는 유효하지 않은 레코드 배너.](https://www.palantir.com/docs/resources/foundry/object-indexing/direct-datasource-logging.png)

쓰기가 거부되는 이유는 보통 데이터 검증 실패입니다. 파이프라인 상류에서 데이터 형태를 바로잡은 다음 파이프라인을 재실행하십시오. 뷰가 초기화되고 쓰기가 다시 유효해지면 배너가 사라집니다. 거부된 쓰기의 원인을 파악할 수 없으면 Palantir Support에 문의하십시오.

파이프라인을 재실행하면 객체 뷰가 초기화되어 기존 객체가 모두 제거됩니다. 재실행하기 전에 이 점을 고려하십시오.

**설명**: "데이터 검증 실패"의 예로는 객체 타입에서 정수로 정의된 속성에 문자열이 들어오거나, 기본 키가 비어 있는 레코드가 있습니다. 이런 레코드는 해당 기본 키만 버려지고 나머지 레코드는 정상 반영되므로, 전체 파이프라인은 돌고 있는데 특정 객체만 보이지 않는 증상으로 나타납니다.

> **중간 요약**: Datasources 탭에서 쓰기 파이프라인으로 이동하고, 라이브니스(Data, Schema, Latest edit)로 신선도를 확인하며, Flink 잡 지표와 유효하지 않은 쓰기 로그로 문제를 추적합니다. 데이터를 고친 뒤 재실행하면 기존 객체가 모두 지워진다는 점에 주의해야 합니다.

<a id="faq"></a>
## 자주 묻는 질문 (FAQ)

<a id="after-i-deploy-the-pipeline-the-streaming-job-consistently-fails-before-it-can-start-is-this-expected"></a>
### 파이프라인을 배포한 뒤 스트리밍 잡이 시작되기도 전에 계속 실패합니다. 정상인가요?

예. 처음 배포할 때나 출력을 초기화하며 파이프라인을 재실행할 때, Funnel 설정 과정 때문에 타임아웃이 발생해 잡이 제출 전에 실패할 수 있습니다. 잡이 재시도 한도를 넘으면 실패한 잡을 다시 빌드하십시오. 재실행하는 경우라면 다시 재실행과 함께 배포할 필요는 없습니다. 재실행을 또 트리거하면 Funnel이 설정 과정을 한 번 더 시작하므로 다시 타임아웃이 날 수 있습니다.

<a id="i-replayed-my-streaming-pipeline-and-now-all-of-my-objects-are-missing-why-is-this-happening"></a>
### 스트리밍 파이프라인을 재실행했더니 객체가 모두 사라졌습니다. 왜 그런가요?

이것은 직접 데이터소스의 현재 제약입니다. 새 뷰를 즉시 제공하기 위해 기존 객체 뷰를 완전히 지웁니다. 교체가 즉시 이루어지므로 새 뷰는 아직 완전히 채워지지 않은 상태이며, 그래서 객체 뷰가 불완전하거나 비어 있을 수 있습니다. 이 제약을 해결하기 위한 백그라운드 재실행 기능이 개발 중입니다.

<a id="i-am-missing-objects-that-i-expect-to-exist-in-the-ontology-how-can-i-debug-this"></a>
### 온톨로지에 있어야 할 객체가 보이지 않습니다. 어떻게 디버깅하나요?

먼저 [데이터 라이브니스](#liveness)를 확인하십시오. **Data** 라이브니스가 오래되었다면(예: 30분 전), 소스 스트림이 멈췄을 가능성이 큽니다. [스트림 지표](#stream-metrics)나 현재 잡을 확인하십시오.

**Data가** 최신이라면 유효하지 않은 쓰기가 Funnel에 의해 거부되었을 가능성이 가장 큽니다. 거부된 쓰기가 있으면 Ontology Manager의 **Datasources** 탭에도 배너가 나타납니다. 해결 방법은 [로그](#logging)를 참고하십시오.

경우에 따라 **Data가** 오래된 상태이면서 **동시에** 유효하지 않은 쓰기 때문에 객체가 누락될 수도 있습니다. 이는 특정 시점 이후의 모든 쓰기가 거부되었다는 뜻입니다.

> **중간 요약**: 첫 배포나 재실행 직후의 잡 실패는 Funnel 설정 타임아웃 때문일 수 있으며 실패한 잡만 다시 빌드하면 됩니다. 재실행 후 객체가 비는 것은 현재 제약이고, 누락된 객체는 라이브니스, 스트림 지표, 로그 순으로 확인합니다.

## 정리

- 직접 데이터소스(베타)는 Pipeline Builder가 온톨로지에 직접 써서 데이터와 편집 모두 짧은 지연으로 반영되게 하며, 처리량 대신 스트림 편집과 시간 기반 순서 정렬을 얻습니다.
- 설정은 Pipeline Builder에서 하고, 배포 후 객체는 Ontology Manager, Insight, Object Explorer에서 보입니다.
- 소스 타임스탬프 속성을 지정하면 기존 값보다 오래된 쓰기를 버려 순서 문제를 막습니다.
- Datasources 탭에서 쓰기 파이프라인, 라이브니스, Flink 잡 지표, 유효하지 않은 쓰기 로그를 확인할 수 있습니다.
- 파이프라인 재실행은 기존 객체 뷰를 즉시 지우므로 신중하게 사용해야 합니다.
