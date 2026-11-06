# 머티리얼라이제이션 (Materializations)

- 원문: https://www.palantir.com/docs/foundry/object-edits/materializations/
- 사이드바 위치: Ontology architecture > Object edits and materializations > Materializations

이 페이지는 온톨로지(Ontology)에 인덱싱된 객체의 최신 상태(원본 데이터와 사용자 편집을 합친 결과)를 다시 데이터셋으로 내보내는 머티리얼라이제이션(materialization) 기능을 설명합니다. 머티리얼라이제이션을 언제 쓰는지, 어떻게 만드는지, OSv1의 라이트백(writeback) 데이터셋과 무엇이 다른지, 그리고 제한된 뷰(restricted view)로 보호되는 객체 타입을 머티리얼라이즈할 때 필요한 권한을 다룹니다.

**설명**: 온톨로지의 객체 상태는 두 곳에서 옵니다. 파이프라인이 만든 입력 데이터소스와, 사용자가 액션(action)으로 수정한 편집(edit)입니다. 예를 들어 `Ticket` 데이터셋에서 T1의 `status`가 "open"이어도 사용자가 액션으로 "closed"로 바꿨다면, 온톨로지에서 보이는 T1의 상태는 "closed"입니다. 하지만 이 편집은 원본 데이터셋에는 없으므로, 다른 파이프라인이 원본 데이터셋만 읽으면 여전히 "open"으로 봅니다. 머티리얼라이제이션은 이 둘을 합친 최종 결과(`status = closed`)를 새 데이터셋으로 써 주는 기능입니다. 데이터베이스에서 뷰(view)의 결과를 실제 테이블로 저장해 두는 materialized view와 같은 개념입니다.

최신 데이터는 많은 Foundry 워크플로에서 매우 중요합니다. 온톨로지 사용자는 입력 데이터소스와 사용자 편집의 데이터를 결합해 각 객체의 최신 상태를 담은, 온톨로지에 인덱싱된 데이터의 **머티리얼라이제이션**을 만들 수 있습니다.

<a id="use-cases-for-materializations"></a>
## 머티리얼라이제이션의 사용 사례 (Use cases for materializations)

머티리얼라이제이션의 두 가지 주요 사용 사례는 다음과 같습니다.

* 사용자 편집을 포함한 각 객체의 최신 상태가 필요한 하위(downstream) Foundry 파이프라인 구축
* 한 객체 타입의 모든 객체의 최신 상태를 담은 온톨로지 데이터를 다운로드할 수 있게 하기

**팁**: Foundry에서 대량 다운로드를 할 때는 머티리얼라이즈된 데이터셋을 만든 뒤, [데이터 내보내기(data exports)](https://www.palantir.com/docs/foundry/analytics/exporting-outputs/#data-export)나 [Foundry 변환(transforms)](https://www.palantir.com/docs/foundry/code-repositories/prepare-datasets-download/#prepare-datasets-for-download)을 통한 내보내기처럼 다른 Foundry 데이터셋에 쓰는 기존 다운로드 워크플로로 다운로드를 시작하는 방식을 권장합니다.

> **중간 요약**: 머티리얼라이제이션은 입력 데이터와 사용자 편집을 합친 객체의 최신 상태를 데이터셋으로 만들며, 주로 하위 파이프라인 구축과 대량 다운로드에 씁니다.

<a id="create-a-materialized-dataset"></a>
## 머티리얼라이즈된 데이터셋 만들기 (Create a materialized dataset)

Ontology Manager의 **Datasources** 탭에서 [**Edits** 설정](02_how-edits-applied.md)을 켜면 **Materializations** 탭으로 이동할 수 있습니다. **Materializations** 탭에서는 [입력 데이터소스의 종류](../02_object-permissioning/04_managing-object-security.md#object-input-data-sources)에 따라 다양한 설정으로 머티리얼라이즈된 객체 데이터셋이나 객체 제한된 뷰(object restricted view)를 만들 수 있습니다. 머티리얼라이제이션은 자동으로 업데이트되며, Dataset Preview에서 수동으로 빌드할 수 없습니다.

![머티리얼라이제이션 시작 화면](https://www.palantir.com/docs/resources/foundry/object-edits/materializations.png)

> **중간 요약**: **Datasources** 탭에서 **Edits**를 켠 뒤 **Materializations** 탭에서 만들며, 결과물은 자동으로 갱신됩니다.

<a id="comparison-of-writeback-datasets-and-materialized-datasets"></a>
## 라이트백 데이터셋과 머티리얼라이즈된 데이터셋 비교 (Comparison of writeback datasets and materialized datasets)

phonograph라고도 불리는 Object Storage v1(OSv1)에서는 [라이트백 데이터셋(writeback datasets)](https://www.palantir.com/docs/foundry/slate/references-writeback/)이 머티리얼라이즈된 데이터셋에 해당합니다. OSv1에서는 객체 타입이나 조인 테이블을 쓰는 다대다(many-to-many) 링크 타입에서 사용자 편집을 활성화하려면 라이트백 데이터셋이 반드시 있어야 합니다.

Object Storage v2(OSv2)에서는 사용자 편집을 활성화하는 데 머티리얼라이즈된 데이터셋이 필요하지 않습니다. 대신 사용자는 Ontology Manager의 **Datasources** 탭에서 **Edits** 설정을 켜서 객체 타입의 사용자 편집을 활성화할 수 있습니다. 그래서 OSv2에서 머티리얼라이제이션은 선택 사항이며, 위에서 말한 두 가지 주요 사용 사례에 필요할 때만 만들면 됩니다. 또한 OSv2에서는 객체 타입의 속성(property) 중 일부만 머티리얼라이즈하고 싶은 경우를 위해 머티리얼라이즈된 데이터셋을 여러 개 만들 수 있습니다.

OSv1 라이트백 데이터셋과 OSv2 머티리얼라이즈된 데이터셋의 다른 동작 차이는 아래에서 설명합니다.

<a id="build-schedules-in-writeback-and-materialized-datasets"></a>
### 라이트백 데이터셋과 머티리얼라이즈된 데이터셋의 빌드 스케줄 (Build schedules in writeback and materialized datasets)

OSv1(Phonograph) 라이트백 데이터셋과 OSv2 머티리얼라이즈된 데이터셋은 빌드 스케줄을 다르게 처리합니다.

* OSv1에는 새 사용자 편집이 생겼을 때 라이트백 데이터셋의 빌드를 시작하는 메커니즘이 없습니다. 대신 사용자는 원하는 만큼 자주 라이트백 데이터셋을 빌드하도록 [스케줄](https://www.palantir.com/docs/foundry/building-pipelines/create-schedule/)을 만들 수 있습니다. 새 데이터가 없으면 이 빌드는 추가 컴퓨팅 자원을 쓰지 않도록 자동으로 중단됩니다. 스케줄이 없고 라이트백 데이터셋이 빌드되지 않고 있다면, 라이트백 데이터셋의 데이터가 온톨로지를 정확하게 반영하지 않을 수 있습니다.
* OSv2는 두 가지 사용 사례를 각각 다르게 처리하도록 설계되었습니다.
  * [편집이 적용되는](02_how-edits-applied.md) 즉시 사용자 편집이 머티리얼라이즈된 데이터셋에 반영되게 하려면, 사용자 편집의 **automatic**(자동) 전파를 켤 수 있습니다. 이 모드는 사용자 편집을 설정된 머티리얼라이즈된 데이터셋에 자동으로 전파합니다(지연 시간은 몇 분 정도). 새 사용자 편집이 얼마나 자주 생기느냐에 따라 빌드가 더 자주 일어날 수 있으므로 추가 비용이 들 수 있습니다.
  * 사용자 편집이 머티리얼라이즈된 데이터셋에 전파되는 지연 시간이 중요하지 않다면, **periodic**(주기적) 빌드를 설정해 비용을 줄일 수 있습니다. 이 모드에서는 입력 데이터소스에 새 데이터가 들어오거나 6시간이 지날 때마다 머티리얼라이즈된 데이터셋을 다시 빌드합니다.

![새 출력 데이터셋 만들기](https://www.palantir.com/docs/resources/foundry/object-edits/materializations-2.png)

![기존 출력 데이터셋](https://www.palantir.com/docs/resources/foundry/object-edits/materializations-3.png)

**설명**: 두 모드의 차이를 예로 들면 이렇습니다. 오전 9시 10분에 사용자가 T1 티켓을 닫았다면, automatic 모드에서는 몇 분 안에 머티리얼라이즈된 데이터셋에서도 T1이 "closed"가 됩니다. periodic 모드에서는 입력 데이터소스가 새로 갱신되거나 6시간 주기가 돌아올 때까지 머티리얼라이즈된 데이터셋에 T1이 "open"으로 남아 있을 수 있습니다. 대신 편집이 자주 생기는 객체 타입에서는 periodic 모드가 빌드 횟수를 크게 줄여 줍니다.

> **중간 요약**: OSv1 라이트백 데이터셋은 사용자가 직접 스케줄을 걸어야 최신 상태가 유지됩니다. OSv2 머티리얼라이제이션은 몇 분 지연으로 편집을 반영하는 automatic 모드와, 새 입력 데이터가 들어오거나 6시간마다 빌드하는 저비용 periodic 모드 중에서 고를 수 있습니다.

<a id="retention-of-writeback-and-materialized-datasets"></a>
### 라이트백 데이터셋과 머티리얼라이즈된 데이터셋의 보존 (Retention of writeback and materialized datasets)

라이트백 데이터셋과 머티리얼라이즈된 데이터셋의 보존(retention)은 같은 방식으로 동작하지 않습니다.

* OSv1에서 라이트백 데이터셋은 일반 데이터셋처럼 동작해, 플랫폼 안에서 지정할 수 있는 특정 [보존 정책(retention policies)](https://www.palantir.com/docs/foundry/retention/overview/)을 적용할 수 있습니다. 그래서 라이트백 데이터셋을 정기적으로 빌드한다면 객체 타입 상태의 과거 스냅샷을 되돌아볼 수 있습니다.

* OSv2에서 머티리얼라이즈된 데이터셋에는 사용자가 바꿀 수 없는 보존 정책이 적용됩니다. 과거 트랜잭션은 계속 삭제되며, 최신 스냅샷만 사용 가능하다고 보장됩니다. 이 경우 객체 타입 상태의 과거 스냅샷을 보관하는 것이 중요하다면 사용자가 하위에 변환(transform)을 따로 만들어야 합니다. 이 보존 정책은 객체 타입을 삭제한 경우에도 적용되므로, 삭제된 객체 타입의 머티리얼라이즈된 데이터셋을 보관하려면 역시 하위 변환이 필요합니다.

**설명**: Foundry 데이터셋은 빌드할 때마다 트랜잭션(버전)이 하나씩 쌓이고, 예전 트랜잭션을 읽으면 그 시점의 데이터를 볼 수 있습니다. OSv2 머티리얼라이즈된 데이터셋은 예전 트랜잭션이 지워지므로 "지난주 월요일의 티켓 상태"를 보려면, 빌드될 때마다 그 내용을 날짜 열과 함께 다른 데이터셋에 덧붙여(append) 저장하는 변환을 직접 만들어야 합니다.

<a id="dataset-schema-in-writeback-and-materialized-datasets"></a>
### 라이트백 데이터셋과 머티리얼라이즈된 데이터셋의 데이터셋 스키마 (Dataset schema in writeback and materialized datasets)

OSv1(Phonograph) 라이트백 데이터셋과 OSv2 머티리얼라이즈된 데이터셋은 입력 데이터소스 스키마와의 관계가 다릅니다.

* OSv1에서는 입력 데이터소스의 스키마를 복사해 라이트백 데이터셋의 스키마로 사용합니다.
* OSv2는 Foundry 온톨로지의 가독성을 높이기 위해 이 동작을 바꿨습니다. 사용자가 온톨로지에서 데이터를 머티리얼라이즈하는 것이므로, 머티리얼라이즈된 데이터셋의 스키마는 백킹 데이터소스(backing datasource) 설정에 의존하지 않고 온톨로지 정의에서 복사합니다. 구체적으로는 각 속성의 [API Name](../../02_define-ontologies/02_object-and-link-types/03_properties/05_property-metadata.md#metadata-reference) 메타데이터가 머티리얼라이즈된 데이터셋의 스키마로 쓰입니다. [OSv1에서 OSv2로 마이그레이션](../01_overview-and-getting-started/03_osv1-osv2-migration.md)하면서 입력 데이터소스의 스키마를 계속 쓰고 싶다면(예: 기존 라이트백 데이터셋의 하위 호환성을 보장하기 위해) Palantir 담당자에게 문의하세요.

**설명**: 예를 들어 입력 데이터셋의 열 이름이 `tkt_stat_cd`이고, 이 열이 매핑된 속성의 API Name이 `status`라면, OSv1 라이트백 데이터셋에는 `tkt_stat_cd` 열이 생기고 OSv2 머티리얼라이즈된 데이터셋에는 `status` 열이 생깁니다. 그래서 OSv1의 라이트백 데이터셋을 읽던 하위 파이프라인은 OSv2로 옮기면 열 이름이 달라져 깨질 수 있고, 위 문장에서 말하는 하위 호환성 문제가 이것입니다.

**주의**: 머티리얼라이즈된 데이터셋에서 `__`로 시작하는 열(예: `__is_deleted`, `__patch_offset`)은 Foundry가 중복 제거 목적으로 사용하는 메타데이터 열이며, 객체 타입의 상태에 대한 어떤 정보도 나타내지 않습니다. 이 열들은 향후 릴리스에서 사전 경고 없이 이름이 바뀌거나 제거될 수 있으므로 운영 워크플로에서 사용하면 안 됩니다.

> **중간 요약**: OSv1 라이트백 데이터셋은 일반 데이터셋처럼 보존 정책을 걸 수 있고 입력 데이터소스의 스키마를 따릅니다. OSv2 머티리얼라이즈된 데이터셋은 최신 스냅샷만 보장하며, 스키마는 속성의 API Name을 따릅니다. `__`로 시작하는 메타데이터 열은 쓰면 안 됩니다.

<a id="restricted-view-materialization-options"></a>
### 제한된 뷰 머티리얼라이제이션 옵션 (Restricted view materialization options)

OSv1(Phonograph)에서는 [제한된 뷰(restricted view)](https://www.palantir.com/docs/foundry/security/restricted-views/)를 입력 데이터소스로 사용해 세분화된 권한이 설정된 객체 타입에 대해, 제한된 뷰를 머티리얼라이즈할 수 없습니다. 사용자는 제한된 뷰 입력 데이터소스의 백킹 데이터셋에 있는 모든 행을 담은 라이트백 데이터셋만 머티리얼라이즈할 수 있습니다. 그런 다음 사용자가 각자의 접근 제한에 맞게 라이트백 데이터셋에 대한 접근을 적절히 보호할 책임이 있습니다.

OSv2에서는 제한된 뷰를 입력 데이터소스로 사용해 [세분화된 권한이 설정된](../02_object-permissioning/05_configuring-rv-access-controls.md#use-restricted-views-to-back-object-types) 객체 타입에 대해, 아래처럼 일반 데이터셋과 제한된 뷰를 모두 머티리얼라이즈 대상 리소스로 설정할 수 있습니다.

![머티리얼라이즈할 리소스 종류 선택](https://www.palantir.com/docs/resources/foundry/object-edits/materializations-4.png)

**설명**: 제한된 뷰(restricted view)는 데이터셋 위에 행 단위 접근 정책을 얹은 것입니다. 예를 들어 `region` 열의 값이 사용자의 소속 지역과 같은 행만 보이게 하는 정책을 걸면, 서울 지사 사용자는 같은 데이터에서 서울 행만 보게 됩니다. SQL에서 행 수준 보안(Row-Level Security)을 거는 것과 같은 목적입니다. OSv1에서는 머티리얼라이즈할 때 이 정책이 사라진 "모든 행" 데이터셋만 만들 수 있었기 때문에 보안을 사용자가 따로 챙겨야 했고, OSv2에서는 결과물도 제한된 뷰로 만들어 정책을 유지할 수 있습니다.

객체 타입에 [여러 입력 데이터소스](../02_object-permissioning/06_multi-datasource-objects.md)가 있는 경우, 사용자는 어떤 입력 데이터소스의 데이터를 머티리얼라이즈할지 선택해 머티리얼라이즈된 데이터셋을 설정할 수 있습니다. 선택하지 않은 입력 데이터소스에서 매핑된 객체 타입 속성은 머티리얼라이즈된 데이터셋에 반영되지 않습니다. 입력 데이터소스 중 일부가 제한된 뷰라면 사용자에게는 두 가지 선택지가 있습니다.

* 제한된 뷰 리소스 중 하나를 골라 [제한된 뷰](https://www.palantir.com/docs/foundry/security/restricted-views/#restricted-views)로 머티리얼라이즈할 수 있습니다. 설정 예시는 아래와 같습니다.

![머티리얼라이즈된 제한된 뷰](https://www.palantir.com/docs/resources/foundry/object-edits/materializations-5.png)

* 여러 입력 데이터소스를 선택할 수도 있지만, 이 경우에는 온톨로지 데이터를 [Foundry 데이터셋](https://www.palantir.com/docs/foundry/data-integration/datasets/)으로만 머티리얼라이즈할 수 있습니다. 이런 제한이 있는 이유는 서로 다른 제한된 뷰 입력 데이터소스가 [서로 다른 정책 설정](https://www.palantir.com/docs/foundry/security/restricted-views/#restricted-view-policies)을 가질 수 있는데, 제한된 뷰는 현재 열 단위 정책 설정을 지원하지 않기 때문입니다. 설정 예시는 아래와 같습니다.

![제한된 뷰 소스가 있는 머티리얼라이즈된 데이터셋](https://www.palantir.com/docs/resources/foundry/object-edits/materializations-6.png)

**설명**: 예를 들어 `Employee` 객체 타입의 기본 정보(이름, 부서)는 제한된 뷰 A(부서별 정책)에서, 급여 정보는 제한된 뷰 B(인사팀만 볼 수 있는 정책)에서 온다고 합시다. 두 소스를 합친 결과를 하나의 제한된 뷰로 만들려면 "이름 열은 정책 A, 급여 열은 정책 B"처럼 열마다 다른 정책이 필요한데, 제한된 뷰는 행 단위 정책 하나만 걸 수 있습니다. 그래서 여러 소스를 합칠 때는 일반 데이터셋으로만 만들 수 있습니다.

> **중간 요약**: OSv1은 제한된 뷰 기반 객체 타입을 정책이 빠진 전체 데이터셋으로만 머티리얼라이즈할 수 있습니다. OSv2는 제한된 뷰로도 머티리얼라이즈할 수 있지만, 여러 입력 데이터소스를 합칠 때는 열 단위 정책이 없기 때문에 일반 데이터셋으로만 가능합니다.

<a id="materializing-datasets-from-restricted-views"></a>
### 제한된 뷰에서 데이터셋 머티리얼라이즈하기 (Materializing datasets from restricted views)

위에서 말했듯이 OSv1과 OSv2 모두 제한된 뷰를 입력 데이터소스로 쓰는 객체 타입을 일반 데이터셋으로 머티리얼라이즈할 수 있습니다. [제한된 뷰는 변환의 입력으로 사용할 수 없기](https://www.palantir.com/docs/foundry/security/restricted-views/) 때문에, 플랫폼에서 제한된 뷰를 데이터셋으로 바꿀 수 있는 곳은 여기뿐입니다. 머티리얼라이즈된 데이터셋에는 제한된 뷰 정책이 따라가지 않으므로, 머티리얼라이즈된 데이터셋을 만들고 시각화하려면 더 높은 수준의 권한이 필요합니다.

설명을 위해 다음 용어를 사용하겠습니다.

* **Object type(객체 타입):** 다루고 있는 객체 타입
* **Restricted view(제한된 뷰):** 객체 타입의 기반이 되는 제한된 뷰
* **Backing dataset(백킹 데이터셋):** 제한된 뷰의 기반이 되는 데이터셋

아래 다이어그램은 백킹 데이터셋, 제한된 뷰, 객체 타입 사이의 관계를 보여 줍니다.

![임의적 접근 통제가 설정된 백킹 데이터셋의 예시](https://www.palantir.com/docs/resources/foundry/object-edits/materializing-from-rv-term-definition.png)

이 정의를 바탕으로, 사용자가 새 머티리얼라이즈된 데이터셋을 만들고 그 트랜잭션을 보는 데 무엇이 필요한지 살펴보겠습니다. 이 둘은 별개의 단계입니다.

새 머티리얼라이즈된 데이터셋을 만들려면, 사용자에게 백킹 데이터셋에서 새 데이터셋으로 항등 변환(identity transformation)을 수행할 권한이 있어야 합니다. 보안 측면에서 이는 사용자가 백킹 데이터셋과 제한된 뷰 모두에 대해 임의적 접근 통제(discretionary controls)와 강제적 접근 통제(mandatory controls)를 충족해야 한다는 뜻입니다.

**설명**: 두 통제는 Foundry 권한 모델의 두 축입니다. 임의적 접근 통제(discretionary controls)는 리소스 소유자나 관리자가 사용자나 그룹에 역할(Viewer, Editor 등)을 부여하는 방식이고, 강제적 접근 통제(mandatory controls)는 마킹(marking)이나 분류 등급처럼 역할과 무관하게 반드시 충족해야 하는 조건입니다. 역할이 있어도 해당 마킹이 없으면 접근할 수 없습니다. 항등 변환은 입력을 아무 가공 없이 그대로 출력으로 복사하는 변환으로, 결과적으로 백킹 데이터셋의 모든 행을 새 데이터셋에 옮기는 것과 같으므로 두 리소스 모두에 대한 권한이 요구됩니다.

이 조건을 충족하면, 아래 예시처럼 사용자에게 새 머티리얼라이즈된 데이터셋을 만드는 옵션이 주어집니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-edits/creating-materialized-dataset.png" alt="사용자가 임의적 접근 통제를 충족해 머티리얼라이즈된 데이터셋을 만들 수 있는 설정 예시" width="500">

이 조건을 충족하지 않으면 사용자에게 이 옵션이 주어지지 않습니다. 다음 예시에서 사용자는 필요한 임의적 접근 통제를 충족하지 않으므로 머티리얼라이즈된 데이터셋을 만들 수 없습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-edits/materializing-dataset-with-no-discretionary-roles.png" alt="사용자가 임의적 접근 통제를 충족하지 않는 설정 예시" width="500">

머티리얼라이즈된 데이터셋의 트랜잭션을 보려면, 사용자가 백킹 데이터셋의 트랜잭션을 볼 수 있어야 합니다. 다시 말해 사용자는 백킹 데이터셋 트랜잭션의 강제적 접근 통제도 충족해야 합니다.

이는 다음 다이어그램에서 볼 수 있습니다. 다이어그램에는 백킹 데이터셋, 제한된 뷰, 객체 타입, 머티리얼라이즈된 데이터셋이 있습니다. 백킹 데이터셋의 마킹은 제한된 뷰에서는 끊기지만(severed), 머티리얼라이즈된 데이터셋으로는 전파됩니다. 따라서 트랜잭션을 보려면 사용자가 이 마킹을 충족해야 합니다.

![백킹 데이터셋의 출처(provenance)를 이어받은 머티리얼라이즈된 데이터셋의 예시](https://www.palantir.com/docs/resources/foundry/object-edits/materialized-dataset-carrying-provenance-from-backing-dataset.png)

**설명**: Foundry에서 마킹은 보통 데이터 계보(lineage)를 따라 하위 데이터셋으로 전파됩니다. 제한된 뷰는 행 단위 정책으로 보호를 대신하기 때문에 백킹 데이터셋의 마킹 전파를 끊습니다. 그러나 머티리얼라이즈된 데이터셋은 제한된 뷰의 정책 없이 전체 행을 담으므로, 다시 백킹 데이터셋의 마킹을 이어받아 보호됩니다. 예를 들어 백킹 데이터셋에 `PII` 마킹이 있으면, 제한된 뷰는 `PII` 마킹 없이도 정책에 맞는 행을 볼 수 있지만, 머티리얼라이즈된 데이터셋의 내용을 보려면 `PII` 마킹이 필요합니다.

OSv2 객체 타입에 [강제적 접근 통제(mandatory control)](../../02_define-ontologies/02_object-and-link-types/03_properties/08_mandatory-control-properties.md) 타입의 속성이 있다면, 머티리얼라이즈된 데이터셋을 보려면 사용자가 `Allowed markings`, `Allowed organizations`, `Max classification`에 대한 모든 강제적 접근 통제도 충족해야 합니다. 위에서 설명한 대로 출처(provenance)는 백킹 데이터셋에서 이어받고, 강제적 접근 통제 타입 속성을 가진 객체 타입에서는 객체 타입에 정의된 강제적 접근 통제도 함께 적용됩니다.

아래는 마킹 하나가 있는 백킹 데이터셋, 마킹 두 개를 가진 머티리얼라이즈된 데이터셋(하나는 백킹 데이터셋에서 오고), 그리고 객체 타입에 설정된 마킹 하나를 보여 주는 다이어그램입니다.

![객체 타입 강제적 접근 통제의 전파를 보여 주는 계보 그림](https://www.palantir.com/docs/resources/foundry/object-edits/materialized-dataset-with-object-type-provenance.png)

백킹 데이터셋에는 다음 마킹이 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-edits/backing-dataset-marking.png" alt="마킹이 있는 백킹 데이터셋 그림" width="500">

객체 타입 설정에서는 아래처럼 강제적 접근 통제 타입의 속성에 다른 마킹을 설정할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-edits/object-type-mandatory-control-property.png" alt="강제적 접근 통제 타입 객체 타입 속성의 예시" width="500">

이 설정의 결과로, 머티리얼라이즈된 데이터셋은 백킹 데이터셋과, 강제적 접근 통제 타입 속성을 가진 객체 타입 양쪽의 출처를 모두 이어받습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-edits/materialized-dataset-with-ot-dataset-provenance.png" alt="백킹 데이터셋의 출처를 이어받은 머티리얼라이즈된 데이터셋의 예시" width="500">

> **중간 요약**: 머티리얼라이제이션은 제한된 뷰를 일반 데이터셋으로 바꿀 수 있는 유일한 방법이라 권한 요구가 높습니다. 만들려면 백킹 데이터셋과 제한된 뷰 양쪽의 임의적, 강제적 접근 통제를 충족해야 하고, 결과 데이터셋은 백킹 데이터셋의 마킹(그리고 OSv2에서는 객체 타입의 강제적 접근 통제 속성 마킹)을 이어받으므로 보려면 그 마킹도 필요합니다.

<a id="materializing-datasets-from-restricted-view-restrictions"></a>
### 제한된 뷰에서 데이터셋 머티리얼라이즈하기의 제약 (Materializing datasets from restricted view restrictions)

OSv2에서 제한된 뷰에 다음 정책 중 하나라도 있으면 머티리얼라이제이션 데이터셋을 설정할 수 없습니다.

1. 제한된 뷰에 사용자의 강제적 접근 통제를 참조하는 조건이 문자열(string) 속성에 적용되어 있는 경우. 이때는 온톨로지의 문자열 속성을 [강제적 접근 통제 속성](../../02_define-ontologies/02_object-and-link-types/03_properties/08_mandatory-control-properties.md)으로 바꿔서, 최대 [분류 기반 접근 통제(Classification-based Access Control)](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/) 또는 [강제 마킹(mandatory marking)](https://www.palantir.com/docs/foundry/security/markings/) 집합을 설정할 수 있게 해야 합니다.
2. 제한된 뷰에 허가된 그룹 ID(authorized group ID) 조건이 있는 경우
3. 제한된 뷰 데이터소스에 [조직(organizations)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/#organizations)이나 마킹을 정적인 값으로 직접 참조하는 조건이 있는 경우. 이때는 조직과 마킹에 대한 세분화된 조건이 문자열 속성이나 정적 값이 아니라 강제적 접근 통제 속성을 참조하도록 해야 합니다.

**설명**: 공통점은, 이 조건들이 일반 문자열이나 고정값에 기대고 있어서 Foundry가 그것을 "이 행에는 어떤 마킹이 필요하다"는 보안 정보로 해석할 수 없다는 것입니다. 머티리얼라이즈된 데이터셋은 제한된 뷰 정책 대신 마킹으로 보호되므로, 행 단위 조건을 마킹으로 옮길 수 있어야 합니다. 강제적 접근 통제 속성은 값 자체가 마킹이나 분류 등급으로 해석되는 전용 속성 타입이라 이 변환이 가능합니다.

<a id="branching"></a>
### 브랜치 작업 (Branching)

머티리얼라이제이션은 다음 제약 아래에서 Global Branches와 함께 사용할 수 있습니다.

* 브랜치에서 머티리얼라이제이션을 만들 수 없습니다.
* 브랜치에서 머티리얼라이제이션을 수정할 수 없습니다.

머티리얼라이제이션이 연결된 객체 타입에 대한 변경은 브랜치에서 인덱싱됩니다. 그 브랜치의 모든 업데이트는 머티리얼라이즈된 데이터셋이나 제한된 뷰에 기록됩니다. 객체 타입을 삭제하거나 브랜치에서 제거하면 머티리얼라이즈된 데이터셋의 해당 브랜치도 삭제됩니다. 제한된 뷰의 제약 때문에, 머티리얼라이즈된 제한된 뷰의 브랜치는 삭제되지 않습니다. 이 제약에 대한 해결책은 현재 개발 중입니다.

**설명**: 브랜치(branch)는 Git의 브랜치처럼 운영 상태(main)에 영향을 주지 않고 변경을 따로 시험하는 공간입니다. 예를 들어 `feature-x` 브랜치에서 객체 타입에 속성을 추가하면, 그 변경을 반영한 결과가 머티리얼라이즈된 데이터셋의 `feature-x` 브랜치에 쓰이고 main 브랜치의 데이터셋은 그대로 유지됩니다. 다만 머티리얼라이제이션 설정 자체는 main에서만 만들고 수정할 수 있습니다.

> **중간 요약**: OSv2에서는 문자열 속성이나 정적 값에 의존하는 일부 제한된 뷰 정책이 있으면 머티리얼라이제이션을 설정할 수 없습니다. 브랜치에서는 머티리얼라이제이션을 만들거나 수정할 수 없지만, 브랜치의 객체 타입 변경은 머티리얼라이즈된 결과물의 같은 브랜치에 기록됩니다.

## 정리

- 머티리얼라이제이션은 입력 데이터소스와 사용자 편집을 합친 객체의 최신 상태를 데이터셋이나 제한된 뷰로 내보내며, 하위 파이프라인과 대량 다운로드에 씁니다.
- OSv1에서는 편집을 쓰려면 라이트백 데이터셋이 필수였지만, OSv2에서는 **Edits** 설정만으로 편집을 켜고 머티리얼라이제이션은 필요할 때만 만듭니다.
- OSv2 머티리얼라이제이션은 automatic(몇 분 지연) 또는 periodic(새 입력 데이터가 들어오거나 6시간마다) 모드로 빌드되고, 최신 스냅샷만 보장되며, 스키마는 속성의 API Name을 따릅니다.
- 제한된 뷰 기반 객체 타입을 일반 데이터셋으로 머티리얼라이즈하려면 백킹 데이터셋과 제한된 뷰 양쪽의 권한이 필요하고, 결과물은 백킹 데이터셋과 객체 타입의 마킹을 이어받습니다.
- 일부 제한된 뷰 정책에서는 머티리얼라이제이션을 설정할 수 없고, 브랜치에서는 만들거나 수정할 수 없습니다.
