# OSv1과 OSv2 사이의 호환성을 깨는 변경 사항 (Breaking changes between OSv1 and OSv2)

- 원문: https://www.palantir.com/docs/foundry/object-backend/object-storage-v2-breaking-changes/
- 사이드바 위치: Ontology architecture > Overview and getting started > Breaking changes between OSv1 and OSv2

이 페이지는 레거시 객체 저장소 Object Storage v1(Phonograph)에서 Object Storage v2(OSv2)로 옮길 때 기존 방식이 그대로 동작하지 않는 지점(호환성을 깨는 변경, breaking change)을 정리합니다. 영구적으로 바뀐 동작과 아직 개발 중이라 일시적으로 지원되지 않는 기능을 나누어 설명하므로, 마이그레이션 전에 무엇을 고쳐야 하는지 점검하는 목록으로 쓸 수 있습니다.

**설명**: 호환성을 깨는 변경(breaking change)은 새 버전으로 바꾸었을 때 기존 코드나 설정이 수정 없이는 동작하지 않게 되는 변경을 말합니다. 예를 들어 라이브러리 함수의 이름이 바뀌거나 인자 개수가 달라지면 그 함수를 호출하던 기존 코드는 고쳐야 합니다.

Object Storage v1(Phonograph)에서 Object Storage v2(OSv2)로의 전환은 여러 호환성을 깨는 변경을 동반하는 큰 아키텍처 전환입니다. 레거시 Object Storage v1(Phonograph)은 API 표면적이 넓어, 상당히 많은 저수준 데이터베이스 기능을 직접 노출합니다. 반면 새 Object Storage v2 아키텍처는 규모, 성능, 유연성, 보안을 개선하기 위해 Object Data Funnel 서비스를 통해 객체를 특화된 객체 데이터베이스로 동기화합니다. 이 아키텍처 전환은 크게 두 종류의 호환성을 깨는 변경으로 이어집니다.

* 특정 사용 사례를 위해 설계된 특화 객체 데이터베이스는 Object Storage v1과 같은 기능을 제공하지 않을 수 있습니다. 이 경우 워크플로를 OSv1에서와 다르게 OSv2에서 모델링해야 할 수 있습니다.
* Object Storage v1에 한데 묶여 있던 [관심사의 차원](01_overview.md#object-storage-v2-architecture)을 분리했기 때문에, OSv1 API와 직접 상호작용하던 일부 기존 쿼리는 리팩터링이 필요합니다.

이러한 호환성을 깨는 변경 때문에, 일부 OSv1 기반 객체 타입은 리팩터링이나 조치 없이 OSv2로 마이그레이션할 수 없을 수 있습니다. [OSv2로의 마이그레이션](03_osv1-osv2-migration.md) 문서에 이런 문제가 사용자에게 어떻게 표시되는지, 그리고 OSv1에서 OSv2로 마이그레이션을 어떻게 수행하는지에 대한 자세한 내용이 있습니다.

**설명**: "API 표면적이 넓다"는 외부에서 호출할 수 있는 기능(엔드포인트, 메서드)이 많다는 뜻입니다. OSv1은 내부 데이터베이스 기능을 외부에 많이 열어 두었기 때문에, 그 기능을 직접 호출하던 코드는 OSv2에서 그 기능이 사라지거나 다른 서비스로 옮겨지면 고쳐야 합니다.

> **중간 요약**: OSv2는 Funnel과 특화 객체 데이터베이스로 구조를 바꾸었기 때문에, OSv1의 일부 기능이 없거나 다른 방식으로 바뀌었습니다. 그래서 일부 객체 타입은 마이그레이션 전에 워크플로나 쿼리를 고쳐야 합니다.

<a id="permanent-breaking-changes"></a>
## 영구적인 호환성을 깨는 변경 사항 (Permanent breaking changes)

이 섹션은 Object Storage v1(Phonograph)과 Object Storage v2(OSv2) 사이의 호환성을 깨는 변경 목록을 제공합니다. 어떤 객체 타입이든 OSv2로 마이그레이션하기 전에 이 변경 사항들을 먼저 해결해야 합니다. OSv1과 OSv2 사이의 이 모든 변경은 온톨로지로 들어가는 데이터의 품질을 높이고, 더 결정적인(deterministic) 동작을 보장하며, 플랫폼 전반의 가독성을 높이기 위한 것입니다.

<a id="actions-and-edits"></a>
### 액션과 편집 (Actions and edits)

* OSv2는 액션을 통한 사용자 편집(edit)만 지원합니다. OSv1 편집 API를 직접 호출하던 기존 쿼리는 모두 OSv2로 마이그레이션하기 전에 액션을 사용하도록 리팩터링해야 합니다.
* OSv2는 "라이트백 데이터셋(writeback datasets)"의 이름을 "머티리얼라이제이션(materializations)"으로 바꿉니다. OSv1에서는 라이트백 데이터셋이 필수이지만, OSv2에서는 머티리얼라이제이션이 선택 사항입니다. 머티리얼라이즈된 데이터셋에 대한 자세한 내용은 [머티리얼라이제이션](../04_object-edits-and-materializations/06_materializations.md)을 참고하십시오.

**설명**: 머티리얼라이제이션은 원본 데이터소스에 사용자 편집까지 반영한 최종 객체 상태를 다시 데이터셋으로 내보낸 결과물입니다. 예를 들어 Employee 데이터셋에 E1의 부서가 "Sales"로 되어 있는데 사용자가 액션으로 "Marketing"으로 바꾸었다면, 머티리얼라이즈된 데이터셋에는 E1의 부서가 "Marketing"으로 기록됩니다. OSv2에서는 이 출력 데이터셋이 꼭 필요하지 않고, 다운스트림 파이프라인에서 편집 결과를 쓰고 싶을 때만 만들면 됩니다.

<a id="edit-history"></a>
### 편집 이력 (Edit history)

* OSv1에서 OSv2로의 마이그레이션은 객체의 편집 이력을 보존하는 옵션을 제공합니다.
  * 이 옵션을 켜면 마이그레이션 과정에 편집 이력이 포함되며, 처리와 저장에 추가 컴퓨팅 비용이 발생합니다.
  * 이 옵션을 켜지 않으면 OSv1의 이전 편집 결과 자체는 유지되지만, OSv1의 전체 편집 이력은 OSv2에서 볼 수 없습니다. 마이그레이션이 완료된 뒤에는 OSv1의 전체 편집 이력을 복구할 수 없습니다. 사용자는 Object Storage v2로 마이그레이션할 때 액션 로그(Action Logs)를 제외하고는 사용자 편집(액션)의 이력이 보존되지 않는다는 점을 확인(acknowledge)해야 합니다.
* OSv2에서는 Ontology Manager에서 객체 타입에 대해 [**Track user edit history**](../04_object-edits-and-materializations/03_user-edit-history.md)(사용자 편집 이력 추적)를 켜야 하며, 사용자 편집 이력을 표시하려면 Object View에 [Edit History 위젯](../../05_applications/03_object-views/08_legacy-object-views/05_widgets-properties-links.md#edit-history)을 추가하도록 업데이트해야 합니다.
* 사용자는 액션이 객체에 어떤 영향을 주었는지 다른 방식으로 기록하기 위해 [액션 로그(Action Log)](../../02_define-ontologies/03_action-types/26_action-log.md) 객체 타입을 구성할 수도 있습니다. 대상 객체 전반에 걸친 액션 이력을 표시하려면 [Action Log Timeline 위젯](../../02_define-ontologies/03_action-types/26_action-log.md#action-log-timeline)도 참고하십시오.

**설명**: "편집 결과는 유지되지만 편집 이력은 사라진다"는 말은, 예를 들어 E1의 부서가 Sales에서 Marketing으로, 다시 Finance로 바뀌었다면 마이그레이션 후에도 현재 값 Finance는 그대로 남지만 "언제 누가 Sales에서 Marketing으로 바꾸었는가" 같은 중간 기록은 남지 않는다는 뜻입니다.

<a id="data-restrictions"></a>
### 데이터 제약 (Data restrictions)

OSv2는 온톨로지로 들어가는 데이터의 품질을 보장하기 위해 기본 키(primary key)와 속성 타입에 데이터 제약을 적용합니다. 전체 제약 목록은 [OSv2 데이터 제약](../03_indexing/05_data-restrictions.md) 문서를 참고하십시오.

<a id="changelog-and-incremental-updates"></a>
### 변경 로그와 증분 업데이트 (Changelog and incremental updates)

* 변경 로그(changelog) 데이터소스를 사용하는 객체 타입의 경우, OSv2는 [레거시 변경 로그 데이터셋](https://www.palantir.com/docs/foundry/building-pipelines/maintaining-incremental-performance/#changelog-datasets)에서 쓰이던 "가장 최근 타임스탬프가 이긴다(latest timestamp wins)" 의미론을 고려하지 않습니다.
  * OSv2는 기본적으로 모든 파이프라인을 증분 방식으로 인덱싱합니다. 관련된 변경 로그 계산은 모두 Funnel이 백그라운드에서 자동으로 수행하므로, "변경 로그 Python 데코레이터"는 더 이상 필요하지 않습니다.
* OSv2는 지오포인트(geopoint) 속성에 대해 더 엄격한 검증을 수행합니다.

**설명**: 변경 로그 데이터셋은 테이블의 현재 상태 대신 "어떤 행이 언제 추가, 수정, 삭제되었는가"를 행 단위로 쌓아 두는 형식입니다. 같은 기본 키에 대한 기록이 여러 개 있으면 타임스탬프가 가장 늦은 기록을 현재 값으로 보는 것이 "latest timestamp wins" 규칙입니다. OSv2는 이 규칙을 따로 해석하지 않고 Funnel이 증분 인덱싱 과정에서 변경분을 직접 계산합니다.

<a id="monitoring"></a>
### 모니터링 (Monitoring)

* OSv2 객체 타입은 [모니터링 뷰(monitoring views)](https://www.palantir.com/docs/foundry/monitoring-views/overview/)로만 모니터링할 수 있으며, 이것이 [Object Storage v1(Phonograph) 동기화 상태 헬스 체크(sync status health check)](https://www.palantir.com/docs/foundry/health-checks/checks-reference/#sync-status)를 대체합니다.

<a id="object-set-service-oss-changes"></a>
### Object Set Service (OSS) 변경 사항 (Object Set Service (OSS) changes)

* OSS API는 쿼리 문자열(query string)을 지원하지 않습니다. OSv1은 쿼리 문자열을 지원합니다.
* OSS 카디널리티(cardinality) 지표는 Object Storage v1과 Object Storage v2의 객체를 함께 포함하는 객체 집합(object set), 예를 들어 다중 백엔드 객체 집합에서는 지원되지 **않습니다**.

**설명**: 여기서 쿼리 문자열은 검색창에 입력하듯 `name:Kim AND dept:Sales` 같은 텍스트 형식의 검색식을 그대로 넘기는 방식을 가리키는 것으로 보입니다. OSS에서는 필터를 구조화된 형태로 지정해야 합니다. 카디널리티 지표는 집합에 들어 있는 원소(객체)의 개수, 또는 서로 다른 값의 개수를 뜻합니다.

> **중간 요약**: 영구적인 변경 사항은 액션을 통한 편집만 허용, 라이트백 데이터셋을 선택 사항인 머티리얼라이제이션으로 대체, 편집 이력의 선택적 보존, 기본 키와 속성 타입의 데이터 제약, 변경 로그 처리 방식 변화, 모니터링 뷰로의 일원화, OSS의 쿼리 문자열 미지원 등입니다.

<a id="temporary-breaking-changes"></a>
## 일시적인 호환성을 깨는 변경 사항 (Temporary breaking changes)

이 섹션은 현재 Object Storage v1(Phonograph)과 Object Storage v2(OSv2) 사이의 기능 격차를 나열합니다. 이 기능들은 개발 중이며, 호환성 문제가 해결되는 대로 목록이 갱신됩니다.

* OSv2는 현재 업스트림 대상과 다운스트림 대상 사이의 경로가 머티리얼라이제이션을 거치는 스케줄 연결을 지원하지 않습니다.
* OSv2는 현재 사용자 정의 분석기(custom analyzers)를 지원하지 않습니다.
* Foundry Rules Archetypes는 현재 OSv2의 전체 기능을 지원하지 않습니다. 예를 들어 여러 데이터소스를 백킹으로 하는 객체 타입이나 머티리얼라이제이션이 여러 개인 객체 타입은 지원되지 않습니다. 자세한 내용은 [Foundry Rules 문서](../../05_applications/07_foundry-rules/02_core-concepts/04_rule-logic.md#inputs)를 참고하십시오.

**설명**: 분석기(analyzer)는 검색 엔진에서 텍스트를 인덱싱하기 전에 단어 단위로 자르고, 소문자로 바꾸고, 불용어를 제거하는 등의 전처리 규칙 묶음입니다. 사용자 정의 분석기는 이 규칙을 직접 정한 것을 말합니다. 업스트림과 다운스트림은 데이터 파이프라인에서 데이터가 흘러오는 앞쪽 단계와 그 결과를 받아 쓰는 뒤쪽 단계를 뜻합니다.

> **중간 요약**: 머티리얼라이제이션을 거치는 스케줄 연결, 사용자 정의 분석기, Foundry Rules의 일부 기능은 아직 OSv2에서 지원되지 않으며 개발 중입니다.

## 정리

- OSv1에서 OSv2로의 전환은 저수준 API를 노출하던 단일 시스템에서 Funnel과 특화 객체 데이터베이스 구조로 바뀌는 큰 변화라서 호환성을 깨는 변경이 생깁니다.
- 영구적인 변경: 편집은 액션으로만 가능, 라이트백 데이터셋은 선택적 머티리얼라이제이션으로 대체, 편집 이력 보존은 선택(비용 발생), 데이터 제약 강화, 변경 로그 처리 자동화, 모니터링 뷰 사용, OSS의 쿼리 문자열 미지원.
- 일시적인 변경: 머티리얼라이제이션을 거치는 스케줄 연결, 사용자 정의 분석기, Foundry Rules 일부 기능은 아직 지원되지 않습니다.
- 마이그레이션 전에 이 목록을 기준으로 워크플로를 점검하고 리팩터링해야 합니다.
