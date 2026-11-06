# 객체 타입 편집하기 (Edit object types)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/edit-object-type/
- 사이드바 위치: Define Ontologies > Object and link types > Object types > Edit object types

이 페이지는 이미 만들어 둔 객체 타입(object type)과 그 속성(property)을 수정하는 방법을 다룹니다. 객체 타입은 이미 여러 애플리케이션에서 쓰이고 있을 수 있으므로, 어떤 변경이 객체를 일시적으로 사용할 수 없게 만들거나 사용자가 남긴 편집(edit) 기록을 잃게 만드는지 먼저 이해해야 합니다. 앞부분에서는 이런 "깨지는 변경(breaking change)"을, 뒷부분에서는 실제 편집 절차(삭제, 백킹 데이터소스 추가와 교체, 메타데이터 수정)와 자주 만나는 오류 메시지를 설명합니다.

**주의**: 객체 타입 편집은 사용자 애플리케이션을 망가뜨릴 수 있습니다(Object type edits can break user applications). 객체 타입과 그 속성을 편집하면 **사용자 워크플로를 방해하는, 애플리케이션이 동작하지 않게 되는 결과를** 낳을 수 있습니다. 객체 타입이나 속성을 편집하기 **전에** 아래의 [잠재적으로 깨지는 변경](#potential-breaking-changes) 섹션을 읽으세요.

<a id="potential-breaking-changes"></a>
## 잠재적으로 깨지는 변경 (Potential breaking changes)

**라이트백(writeback)은** 온톨로지 객체에 대한 사용자 편집을 영구적인(durable) Foundry 데이터셋에 저장하는 과정입니다. 이 데이터셋을 라이트백 데이터셋(writeback dataset)이라고 부릅니다. [Object Storage v1 (Phonograph)](../../../06_ontology-architecture/05_object-databases/01_object-storage-v1.md)에서는 객체 타입에 대해, 또는 조인 테이블(join table)이 있는 다대다(many-to-many) 링크 타입에 대해 라이트백 데이터셋을 설정해야 합니다. 이 설정이 있어야 해당 객체 타입이나 링크 타입이 사용자 편집을 받을 수 있습니다. 라이트백 데이터셋이 Object Storage v2의 [머티리얼라이즈된 데이터셋(materialized dataset)](../../../06_ontology-architecture/04_object-edits-and-materializations/06_materializations.md#comparison-of-writeback-datasets-and-materialized-datasets)과 어떻게 다른지 더 알아보세요.

**설명**: 온톨로지의 객체는 원래 백킹 데이터소스(backing datasource), 즉 데이터셋의 행에서 만들어집니다. 그런데 사용자가 애플리케이션에서 액션을 실행해 객체의 속성 값을 바꾸면, 그 변경은 원본 데이터셋을 직접 고치지 않고 별도의 편집 기록으로 쌓입니다. 예를 들어 `Employee` 객체 `E-001`의 `department` 값이 데이터셋에서는 `Sales`인데 사용자가 `Marketing`으로 바꿨다면, "E-001의 department를 Marketing으로 변경"이라는 편집이 저장됩니다. 라이트백 데이터셋은 원본 데이터에 이런 편집들을 반영한 최종 결과를 다시 데이터셋 형태로 내보낸 것입니다. Phonograph는 Object Storage v1에서 객체 데이터를 저장하고 검색할 수 있게 해 주는 Foundry 서비스의 이름입니다.

<a id="object-type-without-writeback"></a>
### 라이트백이 없는 객체 타입 (Object type without writeback)

Object Storage v1 (Phonograph)이 객체 타입의 백킹 데이터소스를 등록 해제(unregister)했다가 다시 등록(reregister)해야 하는 변경을 하면, 그 재인덱싱(reindex) 시간 동안 해당 타입의 객체를 사용자 애플리케이션에서 **사용할 수 없게** 됩니다. 이런 변경은 아래와 같습니다.

다음 변경은 저장할 때 객체 타입의 백킹 데이터소스를 등록 해제한 뒤 다시 등록(또는 삭제)합니다.

* 객체 타입의 백킹 데이터소스를 변경하는 경우
* 객체 타입의 기본 키(primary key)를 변경하는 경우
* 객체 타입을 삭제하는 경우

이 중 하나를 저장하려고 하면, 사용자 애플리케이션에 미칠 수 있는 영향에 대한 경고가 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object-type-warning-reindex.png" alt="경고: 재인덱싱하는 동안 객체를 사용할 수 없게 됩니다" width="500" />

예를 들어 어떤 객체 타입이 Workshop 애플리케이션에서 쓰이고 있다면, 재인덱싱이 끝날 때까지 그 Workshop 애플리케이션은 동작하지 않습니다. 객체 타입의 재인덱싱 진행 상황은 해당 객체 타입의 **Datasources** 페이지에 있는 **Phonograph** 창에서 확인할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object-type-phonograph-track-reindex.png" alt="Phonograph에서 재인덱싱 진행 상황 추적" width="500" />

[Object Storage v1 (Phonograph)에 대해 더 알아보세요.](../../../06_ontology-architecture/05_object-databases/01_object-storage-v1.md)

**설명**: 인덱싱(indexing)은 데이터셋의 행을 객체 저장소에 읽어 들여 빠르게 검색하고 조회할 수 있는 구조로 만들어 두는 작업입니다. 데이터베이스에서 테이블의 기본 키를 바꾸거나 테이블을 다른 테이블로 통째로 교체하면 기존 인덱스를 버리고 처음부터 다시 만들어야 하는 것처럼, 백킹 데이터소스나 기본 키가 바뀌면 객체 저장소도 기존 등록을 지우고 처음부터 다시 인덱싱해야 합니다. 그동안에는 조회할 객체가 없으므로 그 객체를 쓰는 화면이 비거나 오류를 냅니다.

<a id="object-type-with-writeback"></a>
### 라이트백이 있는 객체 타입 (Object type with writeback)

객체 타입에 라이트백이 활성화되어 있다면, 그 객체 타입을 편집할 때 더 주의해야 합니다. 객체 타입에 가해진 편집의 이력은 Object Storage v1 (Phonograph)에 저장됩니다. 라이트백 데이터셋을 빌드할 때마다 이 편집 이력을 다시 적용해서, 라이트백 데이터셋 안에 편집된 객체의 최종 상태를 만들어 냅니다. 객체 타입의 백킹 데이터소스가 Object Storage v1 (Phonograph)에서 등록 해제되면, Object Storage v1 (Phonograph)에 있던 편집 이력이 삭제되고, 이후의 라이트백 데이터셋 빌드는 실패합니다.

[앞 섹션](#object-type-without-writeback)에서 나열한 등록 해제가 필요한 변경에 더해, 라이트백이 있는 객체 타입은 **한 번이라도** 편집을 받은 적이 있는 속성이라면 **어떤** 속성이든 스키마를 변경할 때 등록 해제가 필요합니다. 지금은 편집을 받지 않고 있더라도 마찬가지입니다. 스키마 변경에는 속성의 ID와 기본 타입(base type)을 바꾸는 것이 포함됩니다.

다음 변경은 등록 해제가 ***필요하지 않으므로*** 편집 이력을 잃을 위험이 없습니다.

* 편집을 받은 적이 있는 속성의 표시 이름(display name), 타이틀 키(title key), 렌더 힌트(render hints), 타입 클래스(type classes), 가시성(visibility)을 바꾸는 것은 객체 타입의 등록 해제를 ***필요로 하지 않습니다***.
* 편집을 받은 적이 없는 필드를 삭제하거나 그런 필드의 스키마를 변경하는 것은 객체 타입의 등록 해제를 ***필요로 하지 않으며***, 따라서 편집을 받고 있는 다른 필드의 편집을 지우거나 되돌리지 않습니다.

**주의**: 변경을 되돌리거나 데이터소스를 수동으로 다시 등록할 때까지 재인덱싱이 실패합니다(Reindex fails until you undo or manually reregister the datasources). Object Storage v1 (Phonograph)은 이런 스키마 변경이 있을 때 객체 타입의 백킹 데이터소스를 자동으로 등록 해제하지 **않습니다**. 대신 재인덱싱이 실패하며, 저장한 스키마 변경을 되돌리거나, 객체 타입의 **Datasource** 페이지에 있는 **Phonograph** 창에서 백킹 데이터소스를 수동으로 등록 해제하고 다시 등록해야만 성공합니다.

속성 편집기(property editor)의 속성 창은 각 필드가 편집을 받은 적이 있는지를 강조 표시합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object-type-properties-pane.png" alt="속성 창" width="500" />

또한 편집 이력을 지울 위험이 있는 변경을 저장하려고 하면, 편집에 미칠 수 있는 영향에 대한 경고가 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object-type-warning-edit-impact.png" alt="편집에 미치는 영향에 대한 경고" width="500" />

이제 기존 객체 타입과 속성을 편집할 때 고려할 사항을 이해했으니, 안전하게 변경할 수 있습니다.

**설명**: 편집 이력은 "어떤 객체(기본 키)의 어떤 속성(속성 ID)을 어떤 값으로 바꿨다"는 형태의 기록이라고 생각하면 이해하기 쉽습니다. 예를 들어 `(E-001, department, "Marketing")` 같은 기록이 쌓여 있는데 속성 ID `department`를 `dept`로 바꾸거나 타입을 문자열에서 정수로 바꾸면, 기존 기록이 가리키는 대상이 더 이상 맞지 않습니다. 그래서 편집을 받은 적 있는 속성의 ID나 타입을 바꾸는 것은 위험한 변경으로 분류됩니다. 반면 표시 이름처럼 화면에 보이는 정보만 바꾸는 것은 기록이 가리키는 대상에 영향을 주지 않으므로 안전합니다. (이 기록 형태는 이해를 돕기 위한 단순화이며, Phonograph의 실제 저장 형식을 설명하는 것은 아닙니다.)

> **중간 요약**: 백킹 데이터소스 변경, 기본 키 변경, 객체 타입 삭제는 Phonograph 재인덱싱을 일으켜 그동안 객체를 쓸 수 없게 만듭니다. 라이트백이 있는 객체 타입에서는 여기에 더해, 편집을 받은 적 있는 속성의 ID나 기본 타입을 바꾸면 편집 이력이 사라질 위험이 있으며 재인덱싱이 실패합니다. 표시 이름 같은 메타데이터 변경과 편집을 받은 적 없는 필드의 변경은 안전합니다.

<a id="edit-an-existing-object-type"></a>
## 기존 객체 타입 편집하기 (Edit an existing object type)

* [기존 객체 타입으로 이동하기](#navigate-to-an-existing-object-type)
* [객체 타입 삭제하기](#delete-an-object-type)
* [백킹 데이터소스 추가 또는 제거하기](#add-or-remove-a-backing-datasource)
* [백킹 데이터소스 변경하기](#change-a-backing-datasource)
* [객체 타입의 메타데이터 편집하기](#edit-an-object-types-metadata)

<a id="navigate-to-an-existing-object-type"></a>
### 기존 객체 타입으로 이동하기 (Navigate to an existing object type)

홈 페이지 사이드바에서 객체 타입 페이지를 선택한 다음 목록에서 다른 객체 타입을 선택하면, 언제든지 작업 중인 객체 타입을 바꿀 수 있습니다. 또한 애플리케이션 헤더의 검색창에서 언제든지 다른 객체 타입을 검색할 수도 있습니다. [탐색에 대해 더 알아보세요.](../../../05_applications/04_ontology-manager/02_navigation.md)

<a id="delete-an-object-type"></a>
### 객체 타입 삭제하기 (Delete an object type)

객체 타입 보기 사이드바의 오른쪽 위에 있는 ![...](https://www.palantir.com/docs/resources/foundry/object-link-types/three-dots.png) (점 세 개) 아이콘을 선택한 다음(아래 이미지 참고) 드롭다운에서 **Delete** 옵션을 선택하면 객체 타입을 삭제할 수 있습니다. 그러면 객체 타입과 그에 연결된 모든 링크 타입을 삭제 대상으로 스테이징(stage)할지 확인하는 대화 상자가 나타납니다.

* 객체 타입 삭제는 변경 사항을 저장한 뒤에야 적용되며, 그 객체 타입을 참조하는 모든 뷰와 애플리케이션을 망가뜨립니다.
* `active` 상태인 객체 타입은 삭제할 수 없습니다. [상태에 대해 더 알아보세요.](../09_metadata/03_metadata-statuses.md)

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object-type-delete-object-type.png" alt="객체 타입 삭제" width="500" />

**설명**: 스테이징(staging)은 변경을 즉시 반영하지 않고 "저장 대기" 목록에 올려 두는 것입니다. Ontology Manager에서는 여러 변경을 모아 두었다가 저장(Save) 버튼을 눌러 한꺼번에 반영합니다. 그래서 삭제를 선택해도 저장하기 전까지는 실제로 지워지지 않습니다.

<a id="add-or-remove-a-backing-datasource"></a>
### 백킹 데이터소스 추가 또는 제거하기 (Add or remove a backing datasource)

[백킹 데이터소스 없이 만든 객체 타입](02_create-object-type.md#create-an-object-type-without-a-backing-datasource)에 백킹 데이터소스를 추가하려면 아래 안내를 따르세요.

1. 객체 타입의 **Properties** 페이지 위쪽에서 **Edit property mapping**을 선택해 속성 편집기로 이동합니다.
2. **Datasources** 창에서 **Add a backing datasource**를 선택한 다음, 사용 가능한 데이터소스를 고릅니다.
3. 데이터소스의 열을 기존 객체 타입 속성에 매핑합니다.
4. 객체 타입의 [보안 설정](../../../06_ontology-architecture/02_object-permissioning/04_managing-object-security.md)을 검토한 다음, 변경 사항을 저장합니다.

백킹 데이터소스를 제거하려면 같은 속성 편집기로 이동해 **Datasources** 창에서 데이터소스를 제거합니다. 필요한 [객체 보안 정책(object security policy)](../../../06_ontology-architecture/02_object-permissioning/07_object-security-policies.md)을 설정한 다음, 변경 사항을 저장합니다.

백킹 데이터소스 제거는 객체 타입이 프로젝트에 저장되어 있을 때만 할 수 있습니다. 이렇게 해야 객체 타입이 백킹 데이터소스에서 권한을 상속받는 대신 [프로젝트 기반 권한 모델](../../../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)을 사용하게 됩니다. 제거된 데이터소스의 열에 매핑되어 있던 모든 속성은 [편집 전용 속성(edit-only property)](../03_properties/06_edit-only-properties.md)이 되며, 그 값은 데이터소스의 열이 아니라 [액션](../../03_action-types/01_overview.md)을 통해 채워집니다.

**설명**: 데이터소스가 있는 객체 타입은 "이 데이터셋을 읽을 수 있는 사람이 이 객체도 볼 수 있다"는 식으로 데이터셋의 권한을 따를 수 있습니다. 데이터소스를 없애면 따를 대상이 사라지므로, 객체 타입이 속한 프로젝트의 권한을 기준으로 삼아야 합니다. 그래서 프로젝트에 저장된 객체 타입만 데이터소스를 제거할 수 있습니다. 또한 값을 읽어 올 열이 없어진 속성은 사용자가 액션으로 입력한 값만 가지게 됩니다.

<a id="change-a-backing-datasource"></a>
### 백킹 데이터소스 변경하기 (Change a backing datasource)

다음 단계로 백킹 데이터소스를 변경할 수 있습니다.

1. 객체 타입의 **Properties** 페이지 위쪽에서 **Edit property mapping**을 선택해 속성 편집기로 이동합니다.
2. **Datasources** 창 위쪽의 ![pen](https://www.palantir.com/docs/resources/foundry/object-link-types/pen.png) **Replace** 버튼을 선택합니다. 그러면 Foundry에서 사용 가능한 데이터소스를 찾아보고 선택할 수 있습니다.

**주의**: 스키마가 일치할 때만 속성이 자동으로 다시 매핑됩니다(Properties are remapped automatically only if the schema matches). 객체 타입의 백킹 데이터소스를 바꾸면 이전 데이터소스의 열과 객체 타입 속성 사이의 연결이 모두 제거됩니다. 이전 데이터소스와 **같은 스키마를** 가진 새 데이터소스로 바꿀 때**만** 속성이 자동으로 다시 매핑됩니다. 그렇지 않으면 객체 타입의 속성을 새 데이터소스에 직접 다시 매핑해야 합니다.

![백킹 데이터소스](https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object-type-backing-datasource.png)

**설명**: 스키마(schema)는 데이터셋의 열 이름과 각 열의 타입 목록입니다. 예를 들어 이전 데이터셋이 `employee_id: string, name: string, hired_at: date`였고 새 데이터셋도 똑같은 열 이름과 타입을 가진다면, 속성과 열의 연결을 그대로 옮길 수 있습니다. 열 이름이 하나라도 다르면(예: `name` 대신 `full_name`) 어느 속성을 어느 열에 연결할지 직접 다시 지정해야 합니다.

<a id="edit-an-object-types-metadata"></a>
### 객체 타입의 메타데이터 편집하기 (Edit an object type's metadata)

![객체 타입 메타데이터 편집](https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object-type-metadata-annotated.png)

1. **아이콘(Icon):** 기본 아이콘을 선택하면, 사용자가 이 타입의 객체를 볼 때 사용자 애플리케이션에 나타나는 객체 타입의 아이콘과 색상을 바꿀 수 있습니다.
2. **표시 이름과 설명(Display names and description):** 기존 표시 이름이나 설명을 선택해 텍스트를 편집합니다.
3. **상태(Status):** 기존 상태를 선택하면 사용 가능한 상태의 드롭다운이 열립니다. `deprecated`, `experimental`, `active` 중에서 고릅니다.
   * [상태](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.
4. **가시성(Visibility):** 기존 가시성을 선택하면 사용 가능한 가시성의 드롭다운이 열립니다. `prominent` 객체 타입은 애플리케이션이 사용자에게 이 객체 타입을 먼저 보여 주게 합니다. `hidden` 객체 타입은 사용자 애플리케이션에 나타나지 않습니다.
5. **API 이름(API name):** 기존 API 이름을 선택해 값을 바꿉니다.
   * `active` 상태인 객체 타입은 API 이름을 바꿀 수 없습니다.
     * [상태](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.
     * [유효한 API 이름](02_create-object-type.md#api-name)에 대해 더 읽어 보세요.

**주의**: 객체 타입의 객체 ID(object ID)는 처음 객체 타입을 만드는 과정이 끝난 뒤에는 편집할 수 없습니다.

**설명**: API 이름은 코드(예: OSDK나 함수)에서 객체 타입을 가리킬 때 쓰는 식별자이고, 표시 이름은 화면에 보이는 이름입니다. `active` 상태는 "운영 중이며 다른 곳에서 이 이름에 의존하고 있을 수 있다"는 뜻이므로, 프로그램의 공개 API 함수 이름을 함부로 바꾸지 못하는 것과 같은 이유로 API 이름 변경이 막혀 있습니다.

> **중간 요약**: 객체 타입은 점 세 개 메뉴에서 삭제할 수 있지만 저장해야 적용되고 `active` 상태이면 삭제할 수 없습니다. 백킹 데이터소스는 속성 편집기(Edit property mapping)에서 추가, 제거, 교체하며, 교체 시 스키마가 같아야 자동 재매핑됩니다. 아이콘, 표시 이름, 상태, 가시성, API 이름 같은 메타데이터도 편집할 수 있지만, `active` 객체 타입의 API 이름과 객체 ID는 바꿀 수 없습니다.

<a id="troubleshooting"></a>
## 문제 해결 (Troubleshooting)

<a id="error-phonograph2foundrycolumnnamenotfound"></a>
#### 오류: `Phonograph2:FoundryColumnNameNotFound`

`Phonograph2:FoundryColumnNameNotFound` 오류가 발생했다면, 저장하려는 객체 타입의 백킹 데이터소스에서 열 하나가 제거되어 어떤 속성이 매핑되지 않은 상태로 남은 것입니다. 그 속성을 매핑하거나 삭제해야 합니다.

<a id="error-phonograph2invalidcolumnremoval"></a>
#### 오류: `Phonograph2:InvalidColumnRemoval`

`Phonograph2:InvalidColumnRemoval` 오류가 발생했다면, 편집을 받은 적이 있는 속성을 뒷받침하던 열이 제거된 것입니다. 그 열을 데이터소스에 다시 추가하거나, 객체 타입을 등록 해제한 뒤 다시 등록해야 합니다.

더 자세한 내용은 위의 [잠재적으로 깨지는 변경](#potential-breaking-changes) 섹션을 참고하세요.

<a id="error-phonograph2invalidcolumnfieldschemachange"></a>
#### 오류: `Phonograph2:InvalidColumnFieldSchemaChange`

`Phonograph2:InvalidColumnFieldSchemaChange` 오류가 발생했다면, 편집을 받은 적이 있는 속성의 ID나 키가 바뀐 것입니다. 그 변경을 되돌리거나, 객체 타입을 등록 해제한 뒤 다시 등록해야 합니다.

더 자세한 내용은 위의 [잠재적으로 깨지는 변경](#potential-breaking-changes) 섹션을 참고하세요.

<a id="error-ontologymetadataincompatiblefoundryfieldschemaforpropertytype"></a>
#### 오류: `OntologyMetadata:IncompatibleFoundryFieldSchemaForPropertyType`

`OntologyMetadata:IncompatibleFoundryFieldSchemaForPropertyType` 오류가 발생했다면, 속성을 뒷받침하는 열의 타입과 호환되지 않는 기본 타입으로 속성을 저장하려는 것입니다. 예를 들어 열 X의 타입이 "string"으로 바뀌었는데, 기본 타입이 "integer"인 속성 X에 매핑되어 있는 경우입니다.

<a id="error-phonograph2schemamismatch"></a>
#### 오류: `Phonograph2:SchemaMismatch`

`Phonograph2:SchemaMismatch` 오류가 발생했다면, 객체를 뒷받침하는 스키마를 의도적으로 변경했지만 아직 Ontology Manager에서 객체의 속성 타입을 갱신하지 않았을 가능성이 높습니다. 속성의 데이터 타입이 새 타입을 받아들이도록 편집해서 온톨로지를 수정하세요. 변경 사항을 게시(publish)하고 데이터셋을 다시 빌드한 다음, 객체의 재인덱싱을 시작합니다.

<a id="error-fieldtypeincompatiblewithontologypropertytype"></a>
#### 오류: `FieldTypeIncompatibleWithOntologyPropertyType`

`FieldTypeIncompatibleWithOntologyPropertyType` 오류가 발생하거나 "Failed to Update Object Type in Phonograph" 메시지를 받았다면, 객체를 뒷받침하는 데이터셋의 데이터 타입과 온톨로지가 기대하는 데이터 타입이 일치하지 않는 것입니다. 모든 스키마 갱신이 데이터셋과 온톨로지 양쪽에 반영되도록 해야 합니다.

온톨로지나 데이터셋을 의도적으로 변경한 적이 없다면, 객체와 그 백킹 데이터소스의 소유자와 연락해 최근 변경 사항을 파악하세요.

**설명**: 이 오류들은 대부분 "데이터셋 쪽 스키마"와 "온톨로지 쪽 속성 정의"가 서로 어긋나서 생깁니다. 데이터셋은 파이프라인이 다시 빌드될 때 열이 추가, 삭제, 타입 변경될 수 있고, 온톨로지는 Ontology Manager에서 따로 저장되므로 두 쪽을 함께 맞춰 주어야 합니다. 오류 이름의 앞부분(`Phonograph2`, `OntologyMetadata`)은 어느 서비스에서 오류가 났는지를 나타냅니다.

> **중간 요약**: 문제 해결 섹션의 오류들은 데이터셋 열의 제거나 타입 변경, 편집을 받은 속성의 ID 변경처럼 데이터셋과 온톨로지 정의가 어긋날 때 발생합니다. 해결 방법은 열을 되살리거나 매핑을 고치거나, 변경을 되돌리거나, 객체 타입을 등록 해제 후 재등록하는 것입니다.

## 정리

- 객체 타입 편집은 사용 중인 애플리케이션을 망가뜨릴 수 있으므로, 어떤 변경이 재인덱싱을 일으키는지 먼저 알아야 합니다.
- 백킹 데이터소스 변경, 기본 키 변경, 객체 타입 삭제는 Object Storage v1 (Phonograph)에서 등록 해제와 재등록을 일으켜 그동안 객체를 쓸 수 없게 합니다.
- 라이트백이 있는 객체 타입에서는 편집을 받은 적 있는 속성의 ID나 기본 타입을 바꾸면 편집 이력이 사라질 위험이 있고, 재인덱싱이 실패합니다.
- 삭제, 백킹 데이터소스 추가와 제거와 교체, 메타데이터(아이콘, 이름, 상태, 가시성, API 이름) 편집 절차가 있으며, `active` 상태와 객체 ID에는 제약이 있습니다.
- `Phonograph2:*` 같은 오류는 대부분 데이터셋 스키마와 온톨로지 속성 정의의 불일치에서 비롯됩니다.
