# 객체 타입 속성 편집 (Edit object type properties)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/edit-properties/
- 사이드바 위치: Define Ontologies > Object and link types > Properties > Edit object type properties

이 페이지는 이미 만든 객체 타입의 속성(property)을 속성 편집기(property editor)에서 고치는 방법을 다룹니다. 속성 삭제, 속성을 뒷받침하는 열 변경, 속성 메타데이터(이름, 상태, API 이름, 키, 서식, 타입 등) 편집, 여러 속성 일괄 편집을 차례로 설명합니다. 속성은 데이터베이스 테이블의 열에 대응하므로, 이 페이지의 작업은 테이블 스키마의 열 정의를 수정하는 일에 해당합니다.

<a id="delete-a-property"></a>
### 속성 삭제 (Delete a property)

속성 편집기 안의 속성 창(properties pane)에서 삭제하려는 속성 위에 마우스를 올리고 **Delete property**(속성 삭제)를 선택합니다.

* 속성 삭제는 변경 사항을 저장한 뒤에야 적용되며, 해당 속성을 참조하는 모든 뷰나 애플리케이션이 깨집니다.
* 상태가 `active`인 속성은 삭제할 수 **없습니다**.
  * [상태(status)](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.

**설명**: SQL에서 `ALTER TABLE ... DROP COLUMN`을 실행하면 그 열을 `SELECT` 하던 질의가 모두 오류를 내는 것과 같은 원리입니다. `active` 상태는 "운영 중이라 다른 곳에서 의존하고 있다"는 표시이므로, 실수로 삭제해서 의존하는 애플리케이션을 깨뜨리지 않도록 막아 두는 것입니다.

<a id="change-the-column-backing-a-property"></a>
### 속성을 뒷받침하는 열 변경 (Change the column backing a property)

속성 편집기 안의 속성 창에서 매핑을 해제하려는 속성 위에 마우스를 올리고 **Unlink property**(속성 연결 해제)를 선택합니다. 속성을 새 열에 연결하려면 속성 위에 마우스를 올리고 **Map to a column**(열에 매핑)을 선택합니다.

![열에 매핑하기](https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object-type-map-to-column.png)

**설명**: 객체 타입의 각 속성은 백킹 데이터소스(backing datasource)의 특정 열에서 값을 가져옵니다. 예를 들어 `Employee` 객체 타입의 `fullName` 속성이 데이터셋의 `name` 열에 매핑되어 있다가, 데이터셋에 `full_name` 열이 새로 생겼다면 연결을 해제하고 `full_name` 열에 다시 매핑할 수 있습니다. 속성의 이름과 API 이름은 그대로이고 값의 출처만 바뀝니다.

> **중간 요약**: 속성 삭제는 저장 후 적용되며 참조하는 애플리케이션을 깨뜨리므로 `active` 속성은 삭제할 수 없습니다. 속성이 값을 가져오는 열은 Unlink property와 Map to a column으로 바꿀 수 있습니다.

<a id="edit-a-property-types-metadata"></a>
### 속성 타입의 메타데이터 편집 (Edit a property type's metadata)

아래 이미지처럼 속성 타입을 선택하면 해당 속성 타입의 메타데이터를 편집할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object-type-property-metadata.png" alt="속성 메타데이터 편집" width="500" />

속성 메타데이터를 편집하는 옵션은 네 개의 탭으로 묶여 있으며, 다음 설정에 접근할 수 있습니다.

1. **표시 이름과 설명(Display name and description):** 기존 표시 이름이나 설명을 선택해 텍스트를 편집합니다.
2. **상태(Status):** 기존 상태를 선택하면 사용 가능한 상태의 드롭다운이 열립니다. `deprecated`, `experimental`, `active` 중에서 고릅니다.
   * [상태](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.
3. **API 이름(API name):** 기존 API 이름을 선택해 값을 바꿉니다.
   * 상태가 `active`인 속성은 API 이름을 바꿀 수 **없습니다**.
     * [상태](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.
     * [유효한 API 이름](../02_object-types/02_create-object-type.md#api-name)에 대해 더 읽어 보세요.
4. **키(Keys):** 속성이 객체 타입의 타이틀 키(title key)인지 기본 키(primary key)인지 지정합니다.
   * 상태가 `active`인 객체 타입은 기본 키를 바꿀 수 **없습니다**.
     * [키](../02_object-types/02_create-object-type.md#configure-the-primary-key-and-title-key)와 [상태](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.
5. **값 서식(Value formatting):** 속성 값에 특수한 서식 지정기(formatter)를 적용해 애플리케이션에서 더 읽기 쉽게 만듭니다.
   * [값 서식 지정기](03_value-formatting.md)에 대해 더 읽어 보세요.
6. **조건부 서식(Conditional formatting):** 속성이 애플리케이션에서 어떻게 표시될지 정하는 규칙을 적용합니다.
   * [조건부 서식](04_conditional-formatting.md)에 대해 더 읽어 보세요.
7. **속성 기본 타입(Property base type):** 드롭다운에서 속성의 기본 타입(base type)을 선택합니다. 속성의 타입은 그 속성 값에 대해 수행할 수 있는 연산의 범위를 제한합니다.
   * 예를 들어 기본 타입이 `timestamp`인 속성은 Object Explorer의 타임라인 위젯에 표시할 수 있습니다.
   * 속성의 타입이 백킹 열의 타입과 호환되지 않으면 오류가 발생합니다.

**주의**: 객체 속성 타입을 변경하면, 해당 객체에서 그 속성과 상호작용하는 액션이 기대하는 타입도 함께 업데이트해야 합니다. 이를 위해 Ontology Manager에서 해당 액션을 열고 기대 타입을 편집하세요.

8. **타입 클래스(Type classes):** 애플리케이션이 해석할 수 있는 추가 메타데이터로 타입 클래스를 적용합니다.
   * 사용 가능한 타입 클래스 목록은 [타입 클래스 문서](../09_metadata/01_metadata-typeclasses.md)를 참고하세요.
9. **렌더 힌트(Render hints):** 제공되는 체크리스트에서 속성에 적용할 렌더 힌트를 선택합니다. 렌더 힌트는 속성 값이 표시되는 방식과 Object Storage v1(Phonograph)에 인덱싱되는 방식을 개선합니다.
   * 사용 가능한 렌더 힌트의 설명은 [렌더 힌트 문서](../09_metadata/02_metadata-render-hints.md)를 참고하세요.
10. **가시성(Visibility):** 기존 가시성을 선택하면 사용 가능한 가시성의 드롭다운이 열립니다. `prominent` 속성은 애플리케이션이 사용자에게 가장 먼저 보여 주게 됩니다. `hidden` 속성은 사용자 애플리케이션에 나타나지 않습니다.

속성 메타데이터를 변경한 뒤에는 영향을 받는 객체의 재인덱싱(re-index)을 시작해 온톨로지를 업데이트하세요.

**설명**: API 이름은 코드(예: OSDK, 함수)에서 이 속성을 가리킬 때 쓰는 식별자이므로, 프로그래밍에서 공개 API의 필드 이름을 바꾸면 그 필드를 쓰던 클라이언트 코드가 모두 컴파일되지 않는 것과 같은 문제가 생깁니다. 그래서 `active` 상태에서는 API 이름과 기본 키 변경이 막혀 있습니다. 기본 타입은 프로그래밍 언어의 자료형에 해당합니다. 데이터셋 열이 문자열(`string`)인데 속성을 정수(`integer`)로 지정하면 값을 변환할 수 없어 오류가 납니다. 인덱싱은 데이터셋의 값을 빠르게 조회할 수 있도록 별도 저장소에 정리해 넣는 작업이며, 메타데이터 변경을 반영하려면 이 작업을 다시 해야 합니다.

> **중간 요약**: 속성 메타데이터에는 표시 이름, 상태, API 이름, 키, 값 서식, 조건부 서식, 기본 타입, 타입 클래스, 렌더 힌트, 가시성이 있습니다. `active` 상태에서는 API 이름과 기본 키를 바꿀 수 없고, 타입을 바꾸면 관련 액션의 타입도 고쳐야 하며, 변경 후에는 재인덱싱이 필요합니다.

<a id="bulk-edit-multiple-properties"></a>
### 여러 속성 일괄 편집 (Bulk edit multiple properties)

속성 편집기에서 **Cmd/Ctrl** 키를 누른 채 속성을 선택하면 여러 속성을 동시에 선택할 수 있습니다. 여러 속성을 선택하면 다음 일괄 편집 작업을 사용할 수 있습니다.

* 기본 타입 변경
* 타입 클래스 추가/제거
* 렌더 힌트 변경
* 가시성 변경
* 값 서식 추가/제거

![여러 속성 일괄 편집](https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object-type-bulk-edit-multiple-properties.png)

위 항목 중 일부는 속성 편집기 밖에서도 일괄 편집할 수 있습니다. 객체 타입 뷰의 사이드바에서 **Properties** 페이지를 선택하고, 편집하려는 속성 옆의 체크박스를 선택하면 표 맨 위에 일괄 편집 옵션이 담긴 새 행이 나타납니다.

> **중간 요약**: Cmd/Ctrl로 여러 속성을 선택하면 기본 타입, 타입 클래스, 렌더 힌트, 가시성, 값 서식을 한꺼번에 바꿀 수 있고, Properties 페이지의 체크박스로도 일괄 편집할 수 있습니다.

## 정리

- 속성 삭제는 저장 시점에 적용되며 참조하는 뷰와 애플리케이션을 깨뜨리므로, `active` 상태의 속성은 삭제할 수 없습니다.
- Unlink property와 Map to a column으로 속성이 값을 가져오는 백킹 열을 바꿀 수 있습니다.
- 속성 메타데이터(표시 이름, 상태, API 이름, 키, 서식, 기본 타입, 타입 클래스, 렌더 힌트, 가시성)는 속성 편집기에서 편집하며, `active` 상태에서는 API 이름과 기본 키가 고정됩니다.
- 기본 타입을 바꾸면 관련 액션의 기대 타입도 고쳐야 하고, 메타데이터 변경 후에는 재인덱싱이 필요합니다.
- 여러 속성을 선택해 일부 메타데이터를 일괄 편집할 수 있습니다.
