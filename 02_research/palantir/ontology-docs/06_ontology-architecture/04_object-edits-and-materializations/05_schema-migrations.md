# 스키마 변경 관리 (Manage schema changes)

- 원문: https://www.palantir.com/docs/foundry/object-edits/schema-migrations/
- 사이드바 위치: Ontology architecture > Object edits and materializations > Manage schema changes

이 페이지는 사용자 편집(edit)이 이미 쌓여 있는 객체 타입의 스키마를 바꿀 때 무엇이 "호환성을 깨는 변경(breaking change)"인지, 그리고 Object Storage v2(OSv2)가 기존 편집을 새 스키마에 맞춰 옮기는 스키마 마이그레이션(schema migration)을 어떻게 제공하는지 설명합니다. 사용자 편집은 원본 데이터셋과 별도로 저장되므로, 속성(property)을 지우거나 타입을 바꾸면 그 편집을 어떻게 처리할지 정해야 합니다.

**설명**: 데이터베이스에서 `ALTER TABLE`로 열의 타입을 바꾸거나 열을 삭제할 때 기존 데이터를 어떻게 변환할지 정하는 것을 스키마 마이그레이션이라고 합니다. 온톨로지에서는 원본 데이터셋은 파이프라인이 다시 만들어 주지만, 사용자가 액션(action)으로 수정한 값(사용자 편집)은 온톨로지 안에만 존재합니다. 예를 들어 `Description` 속성에 사용자가 직접 입력한 값 100개가 있는데 이 속성을 삭제하면, 그 100개의 편집을 버릴지 다른 속성으로 옮길지 결정해야 합니다. 이 결정을 미리 정의된 목록 중에서 고르는 것이 이 페이지의 주제입니다.

<a id="changing-object-type-schema"></a>
## 객체 타입 스키마 변경 (Changing object type schema)

Foundry 온톨로지 위에 만든 워크플로와 애플리케이션은 조직의 요구가 바뀌면 함께 발전해야 합니다. 경우에 따라 이 발전 과정에서 객체 타입의 스키마를 다른 곳에도 추가 변경이 필요한 방식으로 업데이트해야 할 수 있습니다("호환성을 깨는 변경", breaking changes). 스키마의 호환성을 깨는 변경의 예로는 기존 속성의 데이터 타입 변경, 객체 타입의 백킹 데이터소스(backing datasource) 변경, 객체 타입의 기본 키(primary key) 변경이 있습니다. 아래에서 [호환성을 깨는 스키마 변경의 전체 목록](#list-of-breaking-schema-changes)을 볼 수 있습니다.

Object Storage v1(Phonograph)에서는 사용자 인터페이스가 이런 스키마 변경을 권장하지 않으며, 특히 객체 타입에 사용자 편집이 있을 때 더 그렇습니다. OSv1에서는 이런 사용자 편집을 마이그레이션할 수 없기 때문입니다. 대신, 시간이 많이 들고 복잡한 수동 조치를 하지 않으면 호환성을 깨는 변경으로 기존 사용자 편집이 사라집니다.

Object Storage v2는 유연하고 반복적인 워크플로 구축을 돕기 위해 스키마 변경에 대한 이 제약을 없앴습니다. 이를 위해 OSv2는 호환성을 깨는 스키마 변경 후에 기존 사용자 편집에 적용할 수 있는, 미리 정의된 마이그레이션 목록을 갖춘 스키마 마이그레이션 프레임워크를 제공합니다. Ontology Manager는 호환성을 깨는 스키마 변경을 자동으로 감지하고, 사용자가 미리 정의된 목록에서 마이그레이션 옵션을 고르도록 안내합니다. 아래에서 [지원되는 마이그레이션의 전체 목록](#list-of-supported-schema-migrations-in-osv2)을 볼 수 있습니다.

<a id="example-workflow"></a>
### 워크플로 예시 (Example workflow)

이 워크플로 예시에서 사용자는 기존 사용자 편집이 있는 객체 타입에서 `Description` 속성을 삭제합니다. Ontology Manager는 이를 호환성을 깨는 스키마 변경으로 자동 식별하고, 아래 스크린샷처럼 마이그레이션이 필요하다는 경고를 표시합니다.

![호환성을 깨는 변경 경고](https://www.palantir.com/docs/resources/foundry/object-edits/breaking_changes.png)

경고 표시와 더불어, 사용자가 변경 사항을 온톨로지에 저장하려고 하면 Ontology Manager는 **Review changes**(변경 사항 검토) 화면에 **Migrations** 탭을 보여 줍니다. Ontology Manager는 사용자가 호환성을 깨는 변경에 대한 마이그레이션을 정의할 때까지 변경 사항 저장을 막습니다. 이렇게 해서 변경이 다른 워크플로를 망가뜨리는 것을 방지합니다.

사용자가 **Migrations** 탭으로 이동하면, Ontology Manager는 아래처럼 호환성을 깨는 변경의 종류에 따라 사용 가능한 마이그레이션 옵션을 표시합니다.

![편집 검토](https://www.palantir.com/docs/resources/foundry/object-edits/edits_review.png)

사용자가 Ontology Manager에서 스키마 변경을 지정하고 저장하면, 백엔드에서 객체 타입의 새 스키마 버전이 만들어지고, 객체 타입의 인덱스를 업데이트하기 위해 그에 대응하는 [교체용 Funnel 배치 파이프라인(replacement Funnel batch pipeline)](../03_indexing/02_funnel-batch-pipelines.md#funnel-batch-pipelines)이 실행됩니다. 교체 파이프라인이 완료되고 새 버전이 [객체 데이터베이스에 의해 완전히 하이드레이션(hydrated)](../03_indexing/02_funnel-batch-pipelines.md#hydration)되었다고 선언되는 즉시, 새 객체 타입 버전을 Object Set Service(OSS)와 온톨로지 API의 다른 소비자들이 조회할 수 있게 됩니다.

**설명**: 저장 이후의 동작 순서는 다음과 같습니다. (1) 객체 타입의 스키마 버전이 예를 들어 v3에서 v4로 올라갑니다. (2) 교체 파이프라인이 원본 데이터와 마이그레이션이 적용된 사용자 편집으로 v4 기준 인덱스를 처음부터 새로 만듭니다. (3) 새 인덱스가 다 채워지면(하이드레이션 완료) 조회 대상이 v4로 바뀝니다. 그동안 사용자는 기존 v3 인덱스를 계속 조회하므로, 새 인덱스를 만드는 중에도 서비스가 끊기지 않습니다.

> **중간 요약**: OSv1은 편집을 마이그레이션할 수 없어 스키마 변경 시 편집이 사라지지만, OSv2는 미리 정의된 마이그레이션으로 편집을 보존합니다. Ontology Manager는 호환성을 깨는 변경을 감지하면 마이그레이션을 정할 때까지 저장을 막고, 저장 후에는 교체 파이프라인이 새 버전의 인덱스를 만듭니다.

<a id="list-of-breaking-schema-changes"></a>
## 호환성을 깨는 스키마 변경 목록 (List of breaking schema changes)

온톨로지에서 다음 변경은 호환성을 깨는 스키마 변경으로 간주됩니다.

* 객체 타입의 입력 데이터소스 변경
* 객체 타입의 기본 키 변경
* 속성의 데이터 타입 변경
* 사용자 편집을 받은 속성의 ID 변경
* 사용자 편집을 받은 속성 삭제
* 사용자 편집을 받은 구조체(struct) 필드 삭제
* 구조체 필드의 데이터 타입 변경

<a id="list-of-non-breaking-schema-changes"></a>
## 호환성을 깨지 않는 스키마 변경 목록 (List of non-breaking schema changes)

온톨로지에서 다음 변경은 호환성을 깨는 스키마 변경으로 간주되지 **않습니다**.

* 사용자 편집을 받은 속성의 표시 이름(display name), 타이틀 키(title key), 렌더 힌트(render hints), 타입 클래스(type classes), 가시성(visibility) 변경
* 사용자 편집을 한 번도 받지 않은 속성의 삭제 또는 스키마 변경
* 사용자 편집을 한 번도 받지 않은 구조체 필드의 삭제 또는 스키마 변경

**설명**: 두 목록을 비교하면 기준이 드러납니다. 저장된 편집 값의 해석이 달라지거나 값이 갈 곳을 잃는 변경(타입 변경, ID 변경, 삭제, 기본 키 변경)은 호환성을 깨는 변경이고, 화면에 어떻게 보이는지만 바꾸는 메타데이터 변경이나 애초에 편집이 없어서 옮길 것이 없는 변경은 그렇지 않습니다. 예를 들어 편집이 한 번도 없었던 `Notes` 속성은 삭제해도 마이그레이션이 필요 없습니다.

> **중간 요약**: 기존 사용자 편집에 영향을 주는 변경(데이터소스, 기본 키, 데이터 타입 변경, 편집된 속성이나 구조체 필드의 ID 변경과 삭제)은 호환성을 깨는 변경이고, 표시용 메타데이터 변경이나 편집이 없는 속성의 변경은 그렇지 않습니다.

<a id="list-of-supported-schema-migrations-in-osv2"></a>
## OSv2에서 지원되는 스키마 마이그레이션 목록 (List of supported schema migrations in OSv2)

다음은 현재 Object Storage v2에서 지원되는 스키마 마이그레이션의 전체 목록입니다.

* **Drop all property edits(속성의 모든 편집 삭제):** 이 마이그레이션 명령은 객체 타입의 특정 속성에 있는 기존 사용자 편집을 모두 삭제합니다. 객체 타입의 다른 속성에 있는 사용자 편집은 영향을 받지 않습니다. 이 명령은 보통 객체 타입에서 속성을 삭제하고 그 자리를 대신할 새 속성이 없을 때 사용합니다.

* **Drop all struct field edits(구조체 필드의 모든 편집 삭제):** 이 마이그레이션 명령은 객체 타입의 구조체 속성 안에 있는 특정 구조체 필드의 기존 사용자 편집을 모두 삭제합니다. 같은 구조체 속성의 다른 구조체 필드에 있는 사용자 편집은 영향을 받지 않습니다. 이 명령은 보통 구조체 속성에서 구조체 필드를 삭제하고 그 자리를 대신할 새 구조체 필드가 없을 때 사용합니다.

* **Drop all edits(모든 편집 삭제):** 이 마이그레이션 명령은 객체 타입의 모든 속성에 있는 기존 사용자 편집을 모두 삭제합니다. 이 마이그레이션이 실행되면 객체 타입의 모든 객체 상태가 입력 데이터소스의 데이터로 초기화됩니다. 이 마이그레이션을 실행하려면 객체 타입의 **Datasources** 탭으로 이동해 **Edits** 섹션에 있는 **Delete edits**를 선택합니다.

* **Move edits(편집 이동):** 이 마이그레이션 명령은 특정 속성 또는 객체 타입 전체의 기존 사용자 편집을 모두 이동합니다. 이 명령은 보통 다음 두 경우에 사용합니다.
  * 기존 속성의 이름을 바꾸거나 삭제하고 새 속성으로 대체하는 경우
  * 객체 타입의 입력 데이터소스를 다른 데이터소스로 교체하는 경우

* **Move struct field edits(구조체 필드 편집 이동):** 이 마이그레이션 명령은 특정 구조체 필드의 기존 사용자 편집을 모두 다른 구조체 필드로 이동합니다. 이 명령은 보통 기존 구조체 필드를 삭제하고 새 구조체 필드로 대체할 때 사용합니다.

* **Cast property to new type(속성을 새 타입으로 변환):** 이 마이그레이션 명령은 특정 속성의 기존 사용자 편집의 데이터 타입을 그 속성의 새 데이터 타입으로 변환(cast)합니다. 지원되는 데이터 타입 변환 목록은 다음과 같습니다.
  * Attachment에서 String으로
  * Boolean에서 String으로
  * Date에서 String으로
  * Double에서 Integer로
  * Double에서 Long으로
  * Double에서 String으로
  * Geopoint에서 String으로
  * Geoshape에서 String으로
  * Integer에서 Long으로
  * Integer에서 Double로
  * Integer에서 String으로
  * Long에서 Integer로
  * Long에서 Double로
  * Long에서 String으로
  * Mandatory marking에서 String으로
  * String에서 Integer로
  * String에서 Long으로
  * String에서 Double로
  * String에서 Boolean으로
  * String에서 Date로
  * String에서 Timestamp로
  * String에서 Geopoint로
  * String에서 Geoshape로
  * Timestamp에서 String으로

* **Cast struct field to new type(구조체 필드를 새 타입으로 변환):** 이 마이그레이션 명령은 특정 구조체 필드의 기존 사용자 편집의 데이터 타입을 그 구조체 필드의 새 데이터 타입으로 변환합니다. 지원되는 데이터 타입 변환 목록은 다음과 같습니다.
  * Boolean에서 String으로
  * Date에서 String으로
  * Double에서 Integer로
  * Double에서 Long으로
  * Double에서 String으로
  * Geopoint에서 String으로
  * Integer에서 Long으로
  * Integer에서 Double로
  * Integer에서 String으로
  * Long에서 Integer로
  * Long에서 Double로
  * Long에서 String으로
  * String에서 Integer로
  * String에서 Long으로
  * String에서 Double로
  * String에서 Boolean으로
  * String에서 Date로
  * String에서 Timestamp로
  * String에서 Geopoint로
  * Timestamp에서 String으로

**설명**: 변환(cast)은 프로그래밍 언어의 형 변환과 같은 개념입니다. 예를 들어 `Rating` 속성을 String에서 Integer로 바꾸면, 사용자가 편집으로 넣어 둔 `"4"`라는 문자열 값이 정수 `4`로 바뀝니다. Double에서 Integer로처럼 정밀도가 줄어드는 변환도 목록에 있으므로 소수점 이하가 어떻게 처리되는지 결과를 확인하는 것이 좋습니다. 원문은 실패 시 동작을 따로 설명하지 않지만, `"abc"`처럼 변환할 수 없는 문자열 값이 있다면 마이그레이션이 정상적으로 끝나지 않을 수 있다는 점을 염두에 두어야 합니다(아래 "실패한 스키마 마이그레이션에서 복구" 항목 참고).

* **Backfill a value(값 채워 넣기):** 이 마이그레이션 명령은 사용자 편집으로 만들어진 객체에서 속성이 설정되지 않은(unset) 경우에만 그 속성을 지정한 값으로 설정합니다. 기존 값은 덮어쓰지 않으며, 명시적으로 `null`로 설정된 값도 덮어쓰지 않습니다. 이 명령은 보통 객체 타입에 속성을 추가한 뒤, 사용자 편집으로 만들어진 기존 객체에 기본값을 지정할 때 사용합니다.

**설명**: 여기서 "설정되지 않음(unset)"과 "`null`로 설정됨"은 다른 상태입니다. 새 속성 `Priority`를 추가하면, 그 전에 액션으로 만든 객체들은 이 속성에 대해 아무 값도 기록된 적이 없는 unset 상태입니다. 반면 누군가 액션으로 `Priority`를 일부러 비워(`null`) 두었다면 그것은 사용자의 의도적인 선택이므로 보존됩니다. SQL로 치면 `ALTER TABLE ... ADD COLUMN ... DEFAULT 'Medium'`을 실행해 기존 행에 기본값을 채우는 것에 대응합니다.

* **Revert migration(마이그레이션 되돌리기):** 이 마이그레이션 명령은 이전에 적용된 스키마 마이그레이션을 되돌립니다. 이 명령은 보통 Ontology Manager의 **History** 섹션을 통해 저장된 온톨로지 변경을 되돌릴 때 사용합니다.
  * 마이그레이션을 되돌리려면 대상 온톨로지의 Ontology Manager에서 **History** 섹션으로 이동해, 기록 이벤트 안의 **Migrations** 섹션을 펼치고, 마이그레이션 이벤트의 **...** 메뉴를 열어 **Revert**를 선택합니다. 마이그레이션을 되돌린 뒤에는 Ontology Manager에서 수정 사항을 저장합니다.

![마이그레이션 되돌리기](https://www.palantir.com/docs/resources/foundry/object-edits/revert_migration.png)

**주의**: 한 번에 적용할 수 있는 스키마 마이그레이션은 최대 500개입니다. 스키마 변경 수가 이 한도를 넘으면 마이그레이션을 여러 묶음으로 나눠 수행해야 합니다. 현재 스키마 마이그레이션 프레임워크는 객체 타입의 기본 키 속성에 마이그레이션 명령을 적용하는 것을 지원하지 않습니다.

* **Recovering from failed schema migrations(실패한 스키마 마이그레이션에서 복구):** 스키마 마이그레이션이 완료되지 못하면, **Datasources** 탭의 교체 파이프라인 위에 오류 메시지가 표시되어 객체 타입을 인덱싱 실패 상태에서 복구하는 데 도움이 되는 정보를 제공합니다. 실패에서 복구하려면 추가 스키마 마이그레이션을 스테이징(staging)해야 하는 경우, 오류 메시지에 필요한 마이그레이션을 스테이징하는 **Fix schema migrations** 옵션이 나타납니다.

![Datasources 탭의 교체 파이프라인 위에 오류 메시지가 표시되고, 실패한 스키마 마이그레이션에서 객체 타입을 복구하는 옵션이 있습니다.](https://www.palantir.com/docs/resources/foundry/object-edits/schema-migration-recovery-ui.png)

**설명**: 스테이징(staging)은 변경을 바로 적용하지 않고 "적용할 목록"에 올려 두는 것을 뜻합니다. Git에서 `git add`로 변경을 스테이징한 뒤 커밋하는 것처럼, 여기서도 필요한 마이그레이션을 스테이징한 뒤 온톨로지 변경을 저장하면 적용됩니다.

> **중간 요약**: OSv2는 편집 삭제(속성, 구조체 필드, 전체), 편집 이동(속성, 구조체 필드, 데이터소스), 타입 변환(속성, 구조체 필드), 기본값 채우기, 마이그레이션 되돌리기를 지원합니다. 한 번에 최대 500개까지 적용할 수 있고 기본 키 속성에는 적용할 수 없으며, 실패하면 Datasources 탭의 **Fix schema migrations**로 복구합니다.

## 정리

- 호환성을 깨는 스키마 변경은 기존 사용자 편집의 의미나 위치에 영향을 주는 변경(데이터소스, 기본 키, 데이터 타입 변경, 편집된 속성이나 구조체 필드의 ID 변경과 삭제)입니다.
- OSv1은 이런 변경 시 편집을 잃지만, OSv2는 미리 정의된 마이그레이션으로 편집을 삭제, 이동, 변환, 보충할 수 있습니다.
- Ontology Manager는 호환성을 깨는 변경을 감지하면 **Migrations** 탭에서 마이그레이션을 정할 때까지 저장을 막습니다.
- 저장하면 새 스키마 버전이 만들어지고 교체 Funnel 배치 파이프라인이 인덱스를 다시 만들며, 하이드레이션이 끝나면 새 버전이 조회됩니다.
- 한 번에 최대 500개 마이그레이션, 기본 키 속성 제외라는 제약이 있고, 실패 시 **Fix schema migrations**로 복구합니다.
