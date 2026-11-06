# Object Storage v1(Phonograph) [지원 중단 예정] (Object Storage v1 (Phonograph) \[Planned deprecation])

- 원문: https://www.palantir.com/docs/foundry/object-databases/object-storage-v1/
- 사이드바 위치: Ontology architecture > Object databases > Object Storage v1 (Phonograph) \[Planned deprecation]

이 페이지는 온톨로지(Ontology)의 예전 저장소인 Object Storage v1(Phonograph, 줄여서 OSv1)이 데이터소스를 어떻게 등록(registration)하고 인덱싱하는지 개괄합니다. OSv1은 지원 중단이 예정되어 있고 새 온톨로지는 Object Storage v2(OSv2)만 쓰지만, 기존 시스템을 OSv2로 옮기거나 OSv2 문서에서 OSv1과 비교하는 내용을 이해하려면 OSv1의 동작 방식을 알아 둘 필요가 있습니다.

**주의**: 지원 중단 예정(Planned deprecation). Object Storage v1(Phonograph)은 개발 단계 중 [지원 중단 예정(planned deprecation)](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으며, 2026년 6월 30일 이후에는 사용할 수 없습니다. [객체 타입과 링크 타입을 Object Storage v2로 마이그레이션](../01_overview-and-getting-started/03_osv1-osv2-migration.md)하세요. 자세한 내용은 [Upgrade Assistant](https://www.palantir.com/docs/foundry/upgrade-assistant/overview/)의 `Migrate object types and many-to-many link types from Object Storage v1 to v2` 조치(intervention)를 참고하세요. 워크플로에서 OSv1을 OSv2로 마이그레이션하는 것에 대해 질문이 있으면 Palantir Support에 문의하세요.

이 페이지는 온톨로지의 레거시 저장소(backing store)인 Object Storage v1(Phonograph)을 개괄합니다. 새 온톨로지와 마이그레이션을 완전히 마친 온톨로지에서는 Object Storage v2가 유일한 선택지입니다.

![Object Storage v1 (Phonograph)](https://www.palantir.com/docs/resources/foundry/object-databases/object-storage-phonograph.png)

<a id="purpose"></a>
## 목적 (Purpose)

Ontology Manager에서 데이터소스를 온톨로지 백킹 데이터소스(backing datasource)나 라이트백(writeback) 데이터셋으로 추가하면, 그 데이터소스는 등록된 다음 저장을 위해 Phonograph에 인덱싱됩니다. 사용자 애플리케이션이 객체의 기반 데이터를 표시하려고 하면 Phonograph에 조회를 보내고, 애플리케이션은 그 결과를 표시합니다.

**설명**: 즉 애플리케이션은 원본 데이터셋 파일을 직접 읽지 않습니다. 동작 순서는 (1) 데이터셋을 Phonograph에 등록, (2) Phonograph가 데이터셋 내용을 자신의 검색용 저장소로 인덱싱, (3) Workshop 같은 애플리케이션이 Phonograph에 조회 요청, (4) Phonograph가 인덱싱된 데이터로 응답하는 흐름입니다.

<a id="registration"></a>
## 등록 (Registration)

백킹 데이터소스를 객체 타입이나 링크 타입에 처음 추가하면, 그 데이터소스를 Phonograph에 등록해야 합니다. 데이터는 Phonograph에 등록되어야 사용자 애플리케이션에서 조회하거나 표시할 수 있습니다.

객체 타입이나 링크 타입의 **Datasources** 탭에 있는 Phonograph 섹션에는 백킹 데이터소스가 Phonograph에 성공적으로 등록되었는지가 표시됩니다. 객체 타입이나 링크 타입의 백킹 데이터소스가 Phonograph에 성공적으로 등록되지 않았다면, 홈 페이지와 검색 결과에서 해당 객체 타입이나 링크 타입의 표시 이름 옆에 빨간색 "not registered"(등록되지 않음) 라벨이 나타납니다.

![Object Storage v1 (Phonograph) 등록](https://www.palantir.com/docs/resources/foundry/object-databases/object-storage-phonograph-registration.png)

객체 타입이나 링크 타입의 백킹 데이터소스 등록을 해제하면, 그 데이터가 사용자 애플리케이션에 나타나지 않게 될 뿐 아니라 (Phonograph에 저장된) 사용자 데이터 편집(edit) 이력도 삭제됩니다. Phonograph에서 백킹 데이터소스 등록을 해제할 때 생길 수 있는 파괴적인 변경과, 등록 해제가 필요한 Ontology Manager의 작업에 대해서는 [잠재적인 호환성 변경(potential breaking changes) 문서](../../02_define-ontologies/02_object-and-link-types/02_object-types/03_edit-object-type.md#potential-breaking-changes)를 참고하세요. 변경 사항이 편집 이력이나 사용자 애플리케이션에 파괴적인 영향을 줄 가능성이 있으면 Ontology Manager는 항상 경고를 표시합니다.

**설명**: OSv1에서는 사용자 편집이 Phonograph 안에 저장되기 때문에, 등록 해제는 인덱스뿐 아니라 그 안의 편집까지 함께 지우는 작업입니다. 예를 들어 사용자가 액션으로 고쳐 둔 `Ticket` 객체의 상태 값 200개가 있었다면, 등록을 해제하는 순간 그 200개 편집이 사라집니다. 이것이 OSv2가 스키마 마이그레이션으로 편집을 보존하도록 바뀐 배경입니다(Manage schema changes 페이지 참고).

> **중간 요약**: OSv1에서는 데이터소스를 Phonograph에 등록해야 애플리케이션에서 조회할 수 있고, 등록 상태는 **Datasources** 탭에서 확인합니다. 등록을 해제하면 데이터가 보이지 않게 되고 편집 이력도 삭제됩니다.

<a id="index-status"></a>
## 인덱스 상태 (Index status)

백킹 데이터소스의 데이터가 업데이트되거나 객체 타입 또는 링크 타입 정의의 스키마가 변경되면, 업데이트된 데이터를 Phonograph에 다시 인덱싱하는 동기화(sync)가 시작됩니다. 흔히 재인덱싱(reindex)이라고 부르는 이 동기화가 완료되면, 업데이트된 데이터와 스키마가 사용자 애플리케이션에 나타납니다.

객체 타입이나 링크 타입의 **Datasources** 탭에 있는 Phonograph 섹션에는 마지막으로 시작된 재인덱싱의 상태가 표시됩니다. 상태는 `success`(성공), `in progress`(진행 중), `failed`(실패) 중 하나입니다. 객체 타입이나 링크 타입의 백킹 데이터소스에 대한 마지막 재인덱싱이 실패했다면, 홈 페이지와 검색 결과에서 해당 객체 타입이나 링크 타입의 표시 이름 옆에 빨간색 "failed"(실패) 라벨이 나타납니다.

![인덱스 상태: 실패](https://www.palantir.com/docs/resources/foundry/object-databases/object-storage-phonograph-index-status-failed.png)

마지막 동기화 위에 마우스를 올리거나 선택하면 동기화가 실패한 이유를 포함한 자세한 정보를 볼 수 있습니다.

<a id="incremental-and-batch-reindexing"></a>
## 증분 재인덱싱과 배치 재인덱싱 (Incremental and batch reindexing)

증분 인덱싱(incremental indexing)에서는 새로 업데이트된 데이터만 인덱싱합니다. Object Storage v1(Phonograph)은 데이터소스의 [트랜잭션 유형](https://www.palantir.com/docs/foundry/data-integration/datasets/#transaction-types)이 APPEND나 UPDATE일 때만 새 데이터소스 트랜잭션을 증분 방식으로 인덱싱합니다. SNAPSHOT 트랜잭션에 대해서는 OSv1이 항상 배치 인덱싱(모든 객체를 다시 인덱싱하는 방식)을 시작합니다.

**설명**: Foundry 데이터셋은 빌드할 때마다 트랜잭션이 쌓이며, 트랜잭션 유형에 따라 의미가 다릅니다. APPEND는 기존 파일에 새 파일을 덧붙이는 것이고, UPDATE는 일부 파일을 추가하거나 바꾸는 것이며, SNAPSHOT은 데이터셋 전체를 새 내용으로 통째로 바꾸는 것입니다. 예를 들어 100만 행 데이터셋에 하루 1,000행이 APPEND로 추가되면 OSv1은 1,000행만 인덱싱하면 되지만, 같은 변경을 SNAPSHOT으로 빌드하면 100만 1,000행 전체를 다시 인덱싱합니다. 따라서 데이터셋을 어떤 트랜잭션 유형으로 빌드하느냐가 인덱싱 시간에 큰 영향을 줍니다.

> **중간 요약**: 데이터나 스키마가 바뀌면 재인덱싱이 일어나고, 상태(`success`, `in progress`, `failed`)는 **Datasources** 탭에서 확인합니다. APPEND와 UPDATE 트랜잭션은 증분으로, SNAPSHOT 트랜잭션은 항상 전체 배치로 재인덱싱됩니다.

## 정리

- Object Storage v1(Phonograph)은 온톨로지의 레거시 저장소이며, 2026년 6월 30일 이후 사용할 수 없으므로 OSv2로 마이그레이션해야 합니다.
- 백킹 데이터소스나 라이트백 데이터셋은 Phonograph에 등록되고 인덱싱되어야 애플리케이션에서 조회할 수 있습니다.
- 등록 해제는 데이터를 애플리케이션에서 숨기고 Phonograph에 저장된 편집 이력까지 삭제하는 파괴적인 작업입니다.
- 데이터나 스키마가 바뀌면 재인덱싱이 일어나며, 등록 상태와 인덱스 상태는 **Datasources** 탭과 빨간색 라벨로 확인합니다.
- APPEND와 UPDATE 트랜잭션은 증분 인덱싱, SNAPSHOT 트랜잭션은 전체 배치 인덱싱을 일으킵니다.
