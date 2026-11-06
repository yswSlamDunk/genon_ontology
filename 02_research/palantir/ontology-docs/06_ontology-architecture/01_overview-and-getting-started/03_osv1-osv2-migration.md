# OSv1에서 OSv2로 마이그레이션하기 (Migrate from OSv1 to OSv2)

- 원문: https://www.palantir.com/docs/foundry/object-backend/osv1-osv2-migration/
- 사이드바 위치: Ontology architecture > Overview and getting started > Migrate from OSv1 to OSv2

이 페이지는 레거시 백엔드 Object Storage v1(Phonograph)에 있는 객체 타입과 다대다 링크 타입을 Object Storage v2(OSv2)로 옮기는 실제 절차를 설명합니다. 마이그레이션 전에 확인할 동작과 호환되지 않는 사용 방식, 전환 시간대(transition window)와 안정화 기간(soak period) 설정, 라이트백 데이터셋 처리, 중단과 실패 대응, 일괄 마이그레이션까지 다룹니다. 이 마이그레이션은 모든 객체 타입에 필수이므로 Foundry 운영자가 반드시 거쳐야 하는 작업입니다.

아키텍처 변경으로 가능해진 Object Storage v2(OSv2)의 [개선 사항](01_overview.md)을 누리려면, Object Storage v1(Phonograph)에 있는 객체 타입과 조인 테이블(join table)을 사용하는 다대다 링크 타입을 Object Storage v2(OSv2)로 마이그레이션해야 합니다.

**주의**: Object Storage v1에서 v2로의 마이그레이션은 모든 객체 타입에 대해 **필수**입니다. [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)는 객체 타입과 다대다 링크 타입의 마이그레이션을 위한 통합 프레임워크를 제공합니다.

Foundry 온톨로지는 모든 객체 타입과 다대다 링크 타입을 한 번에 마이그레이션할 것을 요구하지 않습니다. 일부 객체 타입은 Object Storage v1(Phonograph)에, 일부는 Object Storage v2(OSv2)에 있는 상태에서도 정상적으로 계속 동작합니다. Foundry의 [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)는 [온톨로지 타입의 일괄 마이그레이션](#bulk-migrations)도 지원합니다.

**설명**: 다대다(many-to-many) 관계는 관계형 데이터베이스에서 두 테이블의 기본 키 쌍을 저장하는 별도의 조인 테이블로 표현합니다. 예를 들어 Student와 Course 사이의 수강 관계는 `enrollment(student_id, course_id)` 테이블로 저장합니다. 온톨로지의 다대다 링크 타입도 이런 조인 테이블 데이터셋을 백킹으로 삼기 때문에, 객체 타입처럼 인덱싱 대상이 되고 따라서 마이그레이션 대상이 됩니다.

<a id="considerations-before-running-a-migration"></a>
## 마이그레이션 실행 전 고려 사항 (Considerations before running a migration)

<a id="migration-behavior"></a>
### 마이그레이션 동작 (Migration behavior)

* 객체 타입의 온톨로지 정의를 바꾸었을 때 [Funnel 교체 파이프라인(replacement pipeline)](../03_indexing/02_funnel-batch-pipelines.md)이 생기게 되는 변경은 진행 중인 마이그레이션을 모두 중단시킵니다. 이를 피하려면 마이그레이션 전체 기간(안정화 기간 포함) 동안 객체 타입 스키마를 안정적으로 유지하고, 스키마 변경은 마이그레이션을 시작하기 *전에* 수행하십시오.
* Ontology Manager에 저장된 변경 사항은 Object Storage v1(Phonograph) 등록 정보에 동기적으로 반영됩니다. 그러나 Funnel은 온톨로지 정의 변경을 비동기적으로 기록하므로, Ontology Manager에서 온톨로지 변경을 저장한 시점과 Funnel이 그 변경을 감지하는 시점 사이에 지연이 생깁니다. 이 때문에 `start`나 `abort` 같은 마이그레이션 이벤트가 온톨로지를 저장한 뒤 몇 초 늦게 Ontology Manager에 나타날 수 있습니다.
* Object Storage v1(Phonograph)은 Object Storage v1(Phonograph) 편집 API를 통해 객체 타입과 링크 타입을 직접 편집하는 것을 지원합니다. 이 방식은 지원 중단되었으며 OSv2와 호환되지 않습니다. 사용자 편집이 있는 객체 타입의 마이그레이션을 시작하기 전에 [사용 방식이 호환되는지](#incompatible-usage) 확인하십시오. 그다음 Ontology Manager에서 해당 객체 타입을 찾아 **Datasources** 탭으로 이동합니다. `Only allow edits via actions`(액션을 통한 편집만 허용)를 켜면 그 객체 타입의 마이그레이션이 가능해집니다.
* 마이그레이션을 정의한 순간부터 안정화 기간을 포함한 마이그레이션 전체 기간 동안 사용자 편집은 자동으로 비활성화됩니다. 마이그레이션 과정 중에는 새 사용자 편집을 반영할 수 없지만, 객체 읽기는 중단 없이 계속 가능합니다.
* 마이그레이션은 객체 타입의 편집 이력과 작성자 정보(attribution)를 보존하는 옵션을 제공합니다.
  * 이 옵션을 켜면 마이그레이션 과정에 편집 이력이 포함되며, 처리와 저장에 추가 컴퓨팅 비용이 발생합니다.
  * 편집 이력 보존 옵션을 켜지 않으면 마이그레이션 중에 객체 타입의 편집 이력과 작성자 정보는 보존되지 않고, Object Storage v1(Phonograph)에 있는 각 객체 인스턴스의 최신 상태만 Object Storage v2로 옮겨집니다. 마이그레이션이 완료된 뒤에는 Object Storage v1(Phonograph)의 전체 편집 이력을 복구할 수 없습니다. 사용자는 Object Storage v2로 마이그레이션할 때 액션 로그(Action Logs)를 제외하고는 사용자 편집(액션)의 이력이 보존되지 않는다는 점을 확인해야 합니다.
* decimal 속성이 있는 객체 타입을 마이그레이션할 때는 decimal의 정밀도(precision)나 스케일(scale)을 설정하는 추가 조치가 필요할 수 있습니다. 객체에 decimal 속성이 있거나 그 속성에 decimal 정밀도나 스케일을 설정해야 하는 경우 다음 오류가 발생할 수 있습니다.
  * Object Storage v2로의 마이그레이션을 구성할 때 발생하는 오류: `The current version of the object type has an invalid definition which Object Storage v2 is unable to index. ObjectsDataFunnel:DecimalPropertyTypeMissingPrecisionOrScale`
  * 오류: `Precision does not match backing column.`
  * 오류: `Scale does not match backing column.`
* decimal 속성이 있는 객체 타입과 관련된 이 오류들을 해결하려면 다음 단계를 따르십시오.
  1. Ontology Manager에서 **Properties** 탭으로 이동합니다.
  2. 오류가 있는 속성을 선택합니다.
  3. 그 속성에 원하는 Precision과 Scale 값을 설정합니다. **Fix** 버튼을 사용하면 백킹 데이터를 기준으로 Precision과 Scale 값이 자동으로 설정됩니다.

**설명**: 동기적(synchronous) 처리는 요청한 쪽이 작업이 끝날 때까지 기다렸다가 결과를 받는 방식이고, 비동기적(asynchronous) 처리는 요청만 넘겨 두고 실제 작업은 나중에 별도로 처리되는 방식입니다. 그래서 Funnel 쪽 반영은 저장 직후가 아니라 몇 초 뒤에 보일 수 있습니다. decimal 타입의 정밀도는 전체 유효 자릿수, 스케일은 소수점 아래 자릿수입니다. SQL의 `DECIMAL(10, 2)`는 전체 10자리 중 소수점 아래 2자리, 즉 `12345678.90` 같은 값을 저장할 수 있다는 뜻입니다. 오류 메시지의 "backing column"은 속성의 원본이 되는 데이터셋 열을 가리킵니다.

> **중간 요약**: 마이그레이션 중에는 스키마를 바꾸지 말고, 편집은 액션으로만 허용하도록 설정해야 합니다. 마이그레이션 기간 내내 편집은 막히지만 읽기는 가능하며, 편집 이력 보존은 선택(비용 발생)입니다. decimal 속성은 정밀도와 스케일을 지정해야 할 수 있습니다.

<a id="incompatible-usage"></a>
### 호환되지 않는 사용 방식 (Incompatible usage)

Object Storage v2에서 일부 상호작용은 [호환성을 깨는 변경](02_object-storage-v2-breaking-changes.md)으로 간주되어 Object Storage v2와 호환되지 않습니다. 이런 호환되지 않는 사용 방식은 [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)에서 추적되고 보고됩니다. **Incompatible usage** 알림을 선택하면 조치에 도움이 되도록 지난 30일 동안의 호환되지 않는 사용 방식을 시각화해 보여 줍니다. **Incompatible usage** 화면에 접근할 수 없다면 이 기능을 활성화하는 것에 대해 Palantir 담당자에게 문의하십시오.

![OSv1에서 OSv2로의 마이그레이션에서 호환되지 않는 사용 방식 시각화](https://www.palantir.com/docs/resources/foundry/object-backend/migration3.png)

<a id="non-blocking-incompatible-usage"></a>
#### 마이그레이션을 막지 않는 호환되지 않는 사용 방식 (Non-blocking incompatible usage)

Object Storage v1(Phonograph) 엔드포인트를 직접 호출하는 API 호출 같은 일부 호환되지 않는 사용 방식은 OSv2로의 마이그레이션 시작을 막지는 않지만, 객체 타입이 OSv2로 마이그레이션된 뒤에는 실패하게 됩니다.

![OSv1에서 OSv2로의 마이그레이션 경고](https://www.palantir.com/docs/resources/foundry/object-backend/migration-warning.png)

호환되지 않는 사용 방식을 조사해서 조치가 필요한지 판단해야 합니다. 예를 들어 Object Storage v1(Phonograph)을 직접 호출하던 부분을 객체 조회와 읽기는 [Object Set Service](01_overview.md#object-set-service-oss)로, 객체 편집은 [액션](01_overview.md#actions)으로, 객체 타입 메타데이터 정보는 [Ontology Metadata Service](01_overview.md#ontology-metadata-service-oms)로 옮기는 조치가 있습니다. 이런 호환되지 않는 사용 방식이 더 이상 의미가 없거나 깨져도 문제가 없다면, 조치 없이 마이그레이션을 시작할 수 있습니다.

<a id="blocking-incompatible-usage"></a>
#### 마이그레이션을 막는 호환되지 않는 사용 방식 (Blocking incompatible usage)

액션을 통한 편집만 허용하도록 설정하지 않은 경우처럼, OSv1과 OSv2 사이의 다른 변경 사항은 Ontology Manager에서 마이그레이션을 적극적으로 막습니다.

![OSv1에서 OSv2로의 마이그레이션 오류](https://www.palantir.com/docs/resources/foundry/object-backend/migration-error.png)

이 경우에는 마이그레이션을 시작하기 전에 호환되지 않는 사용 방식을 모두 제거해야 합니다.

<a id="no-incompatible-usage"></a>
#### 호환되지 않는 사용 방식이 없는 경우 (No incompatible usage)

호환되지 않는 사용 방식이나 호환성을 깨는 변경이 전혀 없는 객체 타입은 배너에 녹색 체크 아이콘이 표시되어 마이그레이션할 준비가 되었음을 알려 줍니다.

![OSv1에서 OSv2로의 마이그레이션 준비 완료](https://www.palantir.com/docs/resources/foundry/object-backend/migration-ready.png)

> **중간 요약**: Ontology Manager는 지난 30일간의 호환되지 않는 사용 방식을 보여 줍니다. OSv1 API 직접 호출 같은 것은 마이그레이션을 막지 않지만 이후 실패하므로 OSS, 액션, OMS로 옮겨야 하고, 액션 전용 편집 미설정 같은 것은 마이그레이션 자체를 막습니다.

<a id="migrating-an-entity"></a>
## 엔터티 마이그레이션하기 (Migrating an entity)

<a id="starting-a-migration"></a>
### 마이그레이션 시작하기 (Starting a migration)

마이그레이션을 시작하려면 객체 타입 또는 조인 테이블이 있는 다대다 링크 타입의 **Datasources** 탭으로 이동한 뒤 **Indexing Metadata** 섹션으로 갑니다. 객체 타입이 마이그레이션 대상 조건을 충족하면 Object Storage v2 라디오 버튼을 선택할 수 있고, 이 버튼을 누르면 마이그레이션 파라미터를 고르는 마법사가 열립니다. 이 섹션이 보이지 않는다면, 모든 객체 타입과 조인 테이블 링크 타입에 Object Storage v2가 강제되는 온톨로지에서 작업하고 있을 가능성이 큽니다.

Ontology Metadata Service는 Object Storage v1(Phonograph)을 백킹으로 하는 객체 타입의 호환되지 않는 사용 방식을 추적합니다. 호환되지 않는 사용 방식이 있는 객체 타입을 마이그레이션하려고 하면 알림이 발생합니다. 또한 객체 타입 스키마에 호환성을 깨는 변경이 없는지도 확인해야 합니다.

![OSv1에서 OSv2로의 마이그레이션 시작 화면](https://www.palantir.com/docs/resources/foundry/object-backend/migration4.png)

<a id="transition-windows"></a>
### 전환 시간대 (Transition windows)

**Transition windows** 옵션을 사용하면 안전한 마이그레이션을 위해 선호하는 시간대를 지정할 수 있습니다. 예를 들어 객체 타입의 사용 사례에서 활동이 가장 적은 요일과 시간을 지정할 수 있습니다. 마이그레이션 과정이 시작된 뒤 첫 Funnel 파이프라인이 시작되기까지 최대 30분이 걸릴 수 있다는 점에 유의하십시오. 전환 시간대는 OSv2로의 첫 동기화가 성공적으로 끝난 뒤에만 계산되므로, 그 동기화가 완료될 때 이미 진행 중인 시간대는 해당되지 않습니다. 첫 번째 전환 시간대 안에 마이그레이션을 완료할 수 없으면, Object Set Service는 다음 시간대까지 기다렸다가 OSv2에서 데이터를 읽기 시작합니다.

전환 시간대를 설정하지 않으면, 첫 Funnel 파이프라인이 성공하는 즉시 마이그레이션이 시작됩니다.

![OSv1에서 OSv2로의 마이그레이션 전환 시간대](https://www.palantir.com/docs/resources/foundry/object-backend/migration5.png)

**설명**: 여기서 "전환"은 읽기 요청이 OSv1 인덱스 대신 OSv2 인덱스로 향하도록 바뀌는 시점을 뜻합니다. 예를 들어 전환 시간대를 "매주 일요일 02:00\~04:00"으로 정했는데 첫 OSv2 동기화가 일요일 03:00에 끝났다면, 이미 진행 중인 이번 시간대는 쓰지 않고 다음 주 일요일 02:00에 전환됩니다.

<a id="disabled-action-types"></a>
### 비활성화되는 액션 타입 (Disabled action types)

마이그레이션 중에는 마이그레이션을 정의한 순간부터 안정화 기간을 포함한 마이그레이션 전체 기간 동안 편집이 자동으로 비활성화되므로 사용자가 편집을 적용할 수 없습니다. 객체 읽기는 중단 없이 계속 가능합니다.

<a id="soak-period"></a>
### 안정화 기간 (Soak period)

마이그레이션 과정 중에 Object Storage v1(Phonograph)으로 되돌려야 하는 경우, **안정화 기간(soak period)** 동안에는 데이터를 다시 인덱싱하지 않고 되돌릴 수 있습니다. 마이그레이션 프레임워크는 안정화 기간이 끝날 때까지 Object Storage v1(Phonograph) 인덱스를 Object Storage v2(OSv2)와 함께 최신 상태로 유지합니다. 안정화 기간은 일 단위로 최대 14일까지 설정할 수 있고(시간 단위 지정 옵션 있음), 마이그레이션이 전환 시간대를 통과한 뒤에만 시작됩니다. 안정화 기간을 0일로 설정하면, OSv2 인덱스가 준비되고 전환 시간대가 활성화되는 즉시 해당 객체 타입의 OSv1 인덱스가 삭제됩니다.

안정화 기간 동안 Foundry 온톨로지 백엔드는 모든 쿼리를 자동으로 OSv2로 보내며, OSv1으로의 요청은 모두 거부됩니다. 이 기간을 활용해 객체 타입을 읽는 워크플로가 마이그레이션 후에도 기대대로 동작하는지 검증할 수 있습니다. 안정화 기간 중에 문제가 생기면 [마이그레이션을 중단](#aborting-the-migration)하여 즉시 OSv1 인덱스 사용으로 되돌릴 수 있습니다.

안정화 기간이 끝난 뒤에는 OSv1으로 롤백할 수 없습니다. 질문이 있으면 Palantir Support에 문의하십시오.

**팁**: 안정화 기간 동안 객체 타입은 OSv1과 OSv2에 이중으로 인덱싱되므로 추가 컴퓨팅과 저장 사용량이 발생합니다. 추가 리소스 사용을 피하고 싶다면 마이그레이션을 구성할 때 안정화 기간을 0일로 설정할 수 있습니다.

![OSv1에서 OSv2로의 마이그레이션 안정화 기간](https://www.palantir.com/docs/resources/foundry/object-backend/migration6.png)

**설명**: 안정화 기간은 새 시스템으로 실제 트래픽을 보내면서 옛 시스템을 대기 상태로 계속 갱신해 두는 기간입니다. 소프트웨어 배포에서 새 버전을 운영에 올린 뒤 일정 기간 이전 버전을 바로 되돌릴 수 있게 유지하는 롤백 대비 기간과 같은 개념입니다. 대가로 두 인덱스를 동시에 유지하는 비용이 듭니다.

> **중간 요약**: 마이그레이션은 Datasources 탭의 Indexing Metadata에서 시작합니다. 전환 시간대로 읽기가 OSv2로 넘어가는 시점을 정하고, 최대 14일의 안정화 기간 동안 OSv1 인덱스를 함께 유지해 문제가 있으면 되돌릴 수 있습니다. 기간 중에는 편집이 막히고, 기간이 끝나면 롤백할 수 없습니다.

<a id="migrating-a-writeback-dataset"></a>
### 라이트백 데이터셋 마이그레이션하기 (Migrating a writeback dataset)

Object Storage v1(Phonograph)에서는 객체 타입이나 조인 테이블이 있는 다대다 링크 타입에서 사용자 편집을 가능하게 하려면 [라이트백 데이터셋](https://www.palantir.com/docs/foundry/slate/references-writeback/)이 필요합니다. Object Storage v2는 라이트백 데이터셋을 [머티리얼라이즈된 데이터셋](../04_object-edits-and-materializations/06_materializations.md#comparison-of-writeback-datasets-and-materialized-datasets)으로 대체합니다. Object Storage v2는 사용자 편집을 가능하게 하는 데 머티리얼라이즈된 데이터셋을 요구하지 않습니다. OSv2에서는 머티리얼라이즈된 데이터셋이 선택 사항이므로, 다운스트림에서 필요한 경우에만 머티리얼라이제이션을 만들면 됩니다.

객체 타입과 링크 타입의 라이트백 데이터셋은 OSv2의 머티리얼라이제이션 데이터셋으로 마이그레이션할 수 있습니다. 머티리얼라이제이션 데이터셋은 같은 열을 유지하므로 기존 다운스트림 파이프라인과의 호환성이 유지됩니다. 이 토글은 현재 라이트백 데이터셋을 다른 애플리케이션에서 사용하고 있을 때만 의미가 있습니다. 라이트백 데이터셋을 마이그레이션하지 않기로 선택해도 데이터셋 자체는 삭제되지 않습니다. 대신 그 데이터셋은 정적인 상태가 되어 마지막 빌드 시점의 데이터를 담고 있게 됩니다. 사용자 편집은 그래도 OSv2로 마이그레이션됩니다.

**주의**: 라이트백 데이터셋에 어떤 객체 타입 속성에도 매핑되지 않은 열이 있으면, 그 열은 마이그레이션 과정에서 제거됩니다.

![라이트백 데이터셋 마이그레이션 옵션](https://www.palantir.com/docs/resources/foundry/object-backend/migration9.png)

<a id="aborting-the-migration"></a>
### 마이그레이션 중단하기 (Aborting the migration)

Object Storage v2로 전환한 뒤 성능 저하가 관찰되거나 버그가 발생하면, 안정화 기간 동안 진행 중인 마이그레이션을 안전하게 중단하고 OSv1으로 되돌릴 수 있습니다. 마이그레이션 프레임워크는 마이그레이션 과정 내내 OSv1 인덱스가 새 데이터 동기화에 맞춰 최신 상태로 유지되도록 보장합니다.

마이그레이션 중인 객체 타입에 기존 사용자 편집이 있다면, 마이그레이션이 완료될 때까지 새 사용자 편집은 비활성화됩니다.

<a id="sync-failures"></a>
### 동기화 실패 (Sync failures)

마이그레이션 과정 중에 객체 타입의 동기화가 실패할 수 있습니다. 이 경우 객체 타입의 **Datasources** 탭에 있는 **Indexing Metadata** 섹션에 `PIPELINE_FAILED` 오류가 표시됩니다. 그런 일이 생기면 [Funnel 배치 파이프라인 디버깅](../03_indexing/02_funnel-batch-pipelines.md#debug-a-pipeline) 안내를 따라 문제를 조사하고 해결하십시오.

![OSv1에서 OSv2로의 마이그레이션 실패](https://www.palantir.com/docs/resources/foundry/object-backend/migration-failed.png)

<a id="bulk-migrations"></a>
### 일괄 마이그레이션 (Bulk migrations)

왼쪽 탐색 표시줄의 **Object types** 섹션으로 이동해 여러 객체 타입을 동시에 선택하면, 같은 전환 시간대와 안정화 기간 구성을 사용해 마이그레이션을 일괄로 실행할 수 있습니다. 과정과 설정 마법사는 객체 타입 하나를 마이그레이션할 때와 같습니다. 예상하지 못한 복잡성이나 오류를 막기 위해, 한 번에 100개 미만의 엔터티를 일괄 마이그레이션하는 점진적 방식을 권장합니다.

OSv2만 활성화된 온톨로지에서는 이 마법사가 인터페이스에 나타나지 않습니다.

![OSv1에서 OSv2로의 일괄 마이그레이션](https://www.palantir.com/docs/resources/foundry/object-backend/migration8.png)

> **중간 요약**: 라이트백 데이터셋은 같은 열 구조의 머티리얼라이제이션으로 옮길 수 있으며, 매핑되지 않은 열은 사라집니다. 안정화 기간 중에는 언제든 중단해 OSv1으로 돌아갈 수 있고, 동기화가 실패하면 `PIPELINE_FAILED` 오류를 보고 Funnel 파이프라인을 디버깅합니다. 여러 객체 타입은 한 번에 100개 미만씩 일괄 마이그레이션하는 것이 권장됩니다.

## 정리

- OSv1에서 OSv2로의 마이그레이션은 모든 객체 타입에 필수이며, Ontology Manager에서 객체 타입별 또는 일괄로 진행할 수 있습니다.
- 시작 전에 스키마를 확정하고, `Only allow edits via actions`를 켜고, Ontology Manager가 보여 주는 호환되지 않는 사용 방식을 정리해야 합니다.
- 마이그레이션 기간(안정화 기간 포함) 동안 편집은 막히고 읽기는 계속됩니다. 편집 이력 보존은 선택이며 비용이 듭니다.
- 전환 시간대로 읽기 전환 시점을 정하고, 최대 14일의 안정화 기간 동안 OSv1 인덱스를 유지해 중단과 롤백이 가능합니다.
- 라이트백 데이터셋은 선택적으로 머티리얼라이제이션으로 옮길 수 있고, 동기화 실패는 Funnel 파이프라인 디버깅 절차로 해결합니다.
