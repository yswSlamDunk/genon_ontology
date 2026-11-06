# 인덱싱 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-indexing/overview/
- 사이드바 위치: Ontology architecture > Indexing > Overview

이 페이지는 온톨로지의 인덱싱(indexing)이 무엇인지 정의하고, Object Storage v2에서 인덱싱을 담당하는 Funnel 서비스와 그 파이프라인 종류를 소개하는 입구 페이지입니다. 데이터셋에 있는 행이 어떻게 객체가 되어 빠르게 조회되는지 이해하려면 이 섹션의 나머지 페이지를 읽기 전에 이 개요부터 보는 것이 좋습니다.

<a id="indexing"></a>
## 인덱싱 (Indexing)

온톨로지에서 **인덱싱**은 Foundry 데이터소스에 있는 표 형태(tabular) 또는 그 밖의 형태의 데이터를, 특화된 데이터베이스를 통해 더 빠르게 조회할 수 있도록 만드는 과정입니다.

이 문서 섹션은 Object Storage v2의 인덱싱 과정을 설명합니다. Object Storage v2에서는 Object Data Funnel 서비스("Funnel")가 인덱싱을 총괄합니다. Funnel 서비스는 온톨로지의 객체 인스턴스를 생성하고 수정하며 데이터와 메타데이터를 최신 상태로 유지하는 Funnel 파이프라인을 조율(orchestrate)하는 역할을 맡습니다.

Funnel 파이프라인에는 크게 두 종류, 즉 **Funnel 배치 파이프라인(batch pipeline)과** **Funnel 스트리밍 파이프라인(streaming pipeline)이** 있습니다. 사용자는 데이터소스 환경, 지연 시간(latency)과 워크플로 요구 사항, 비용을 고려해 둘 중 하나의 인덱싱 방식을 택할 수 있습니다.

[Funnel 배치 파이프라인에 대해 더 알아보기.](02_funnel-batch-pipelines.md)

[Funnel 스트리밍 파이프라인에 대해 더 알아보기.](03_funnel-streaming-pipelines.md)

온톨로지에 지연 시간이 짧은 쓰기와 편집(edit)이 필요하다면 [직접 데이터소스(direct datasource)](04_direct-datasources.md)를 사용할 수도 있습니다.

Object Storage v1(Phonograph)의 인덱싱에 대한 정보는 [레거시 문서](../05_object-databases/01_object-storage-v1.md)를 참고하십시오.

**설명**: 데이터베이스 수업에서 배우는 인덱스는 테이블의 특정 열을 B-트리 같은 자료구조로 정리해 `WHERE` 검색을 빠르게 하는 보조 구조입니다. 여기서 말하는 인덱싱은 범위가 더 넓습니다. Foundry 데이터셋은 기본적으로 대량 처리용 파일(예: Parquet 파일 묶음)로 저장되어 있어서 "기본 키가 E001인 행 하나"를 즉시 찾는 데는 적합하지 않습니다. 인덱싱은 이 데이터를 읽어 객체 단위로 변환한 뒤, 조회와 검색에 최적화된 별도 데이터베이스(객체 스토리지)에 적재하는 전체 과정을 말합니다. 배치 방식은 데이터셋이 갱신될 때 묶음 단위로 다시 적재하고, 스트리밍 방식은 레코드가 들어오는 대로 계속 반영합니다.

## 정리

- 인덱싱은 데이터소스의 데이터를 특화된 데이터베이스에 적재해 객체를 빠르게 조회할 수 있게 만드는 과정입니다.
- Object Storage v2에서는 Funnel 서비스가 Funnel 파이프라인을 조율해 객체를 만들고 최신 상태로 유지합니다.
- 파이프라인은 배치와 스트리밍 두 종류가 있으며 데이터소스, 지연 시간, 비용에 따라 고릅니다.
- 짧은 지연의 쓰기에는 직접 데이터소스를 쓸 수 있고, OSv1(Phonograph)은 별도 레거시 문서에서 다룹니다.
