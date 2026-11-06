# 링크 타입 편집 (Edit link types)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/edit-link-types/
- 사이드바 위치: Define Ontologies > Object and link types > Link types > Edit link types

이 페이지는 이미 만들어 둔 링크 타입을 수정하는 방법과, 수정할 때 사용자 애플리케이션이 깨질 수 있는 경우를 설명합니다. 링크 타입은 실제 업무 화면(Workshop 등)에서 바로 쓰이기 때문에, 어떤 변경이 재인덱싱을 일으키고 라이트백(writeback) 편집 이력을 지울 수 있는지 먼저 알아야 안전하게 편집할 수 있습니다.

**주의**: 링크 타입을 편집하면 사용자 워크플로를 방해하는 **애플리케이션 중단 수준의 결과가** 생길 수 있습니다. 링크 타입을 편집하기 **전에** 아래의 [잠재적인 호환성 깨짐 변경](#potential-breaking-changes) 섹션을 읽으세요.

<a id="potential-breaking-changes"></a>
## 잠재적인 호환성 깨짐 변경 (Potential breaking changes)

<a id="link-type-without-writeback"></a>
### 라이트백이 없는 링크 타입 (Link type without writeback)

Object Storage v1(Phonograph)이 링크 타입의 백킹 데이터소스(backing datasource)를 등록 해제했다가 다시 등록해야 하는 변경은, 그 재인덱싱 시간 동안 해당 타입의 링크를 사용자 애플리케이션에서 **사용할 수 없게** 만듭니다. 이런 변경은 아래와 같습니다.

다음 변경을 저장하면 링크 타입의 백킹 데이터소스가 등록 해제 후 재등록(또는 삭제)됩니다.

* 다대다(many-to-many) 링크 타입의 백킹 데이터소스 변경
* 링크 타입의 카디널리티(cardinality) 변경
* 링크 타입의 외래 키(foreign key) 변경
* 링크 타입 삭제

이 중 하나라도 저장하려고 하면 사용자 애플리케이션에 미칠 수 있는 영향에 대한 경고가 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-link-type-warning-reindex.png" alt="경고: 재인덱싱하는 동안 객체를 사용할 수 없게 됩니다" width="500" />

예를 들어 어떤 링크 타입이 Workshop 애플리케이션의 search around에 쓰이고 있다면, 재인덱싱이 끝날 때까지 그 Workshop 애플리케이션은 동작하지 않습니다. 링크 타입의 재인덱싱 진행 상황은 해당 링크 타입 **Datasources** 페이지의 **Phonograph** 창에서 확인할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-link-type-phonograph-track-reindex.png" alt="Phonograph에서 재인덱싱 추적" width="500" />

[Object Storage v1(Phonograph)에 대해 더 알아보세요.](../../../06_ontology-architecture/05_object-databases/01_object-storage-v1.md)

**설명**: 인덱싱(indexing)은 원본 데이터셋의 내용을 빠르게 조회할 수 있는 별도 저장 구조(인덱스)로 옮겨 담는 작업입니다. 사용자 애플리케이션은 원본 데이터셋이 아니라 이 인덱스를 조회하므로, 등록 해제로 인덱스가 사라지고 재등록 후 다시 채워지는 동안에는 링크를 조회할 수 없습니다. "search around"는 한 객체에서 링크를 따라 연결된 객체들을 찾는 기능으로, SQL로 치면 조인 질의에 해당합니다. 카디널리티나 외래 키가 바뀌면 "어떤 열을 어떤 열과 조인하는가"가 바뀌는 것이므로 인덱스를 처음부터 다시 만들어야 합니다.

<a id="link-type-with-writeback"></a>
### 라이트백이 있는 링크 타입 (Link type with writeback)

링크 타입에 라이트백이 활성화되어 있다면, 그 링크 타입을 편집할 때 각별히 주의해야 합니다. 링크 타입에 가해진 편집(edit)의 이력은 Object Storage v1(Phonograph)에 저장됩니다. 라이트백 데이터셋이 빌드될 때마다 이 편집 이력이 다시 적용되어 라이트백 데이터셋 안에 편집된 링크의 최종 상태가 만들어집니다. 링크 타입의 백킹 데이터소스가 Object Storage v1(Phonograph)에서 등록 해제되면 Phonograph에 있던 편집 이력이 삭제되고, 이후 라이트백 데이터셋 빌드는 실패하게 됩니다.

[앞 섹션](#link-type-without-writeback)에서 나열한 등록 해제가 필요한 변경 외에도, 라이트백이 있는 링크 타입은 편집을 **한 번이라도** 받은 적이 있는 링크 타입의 백킹 데이터소스에서 **어떤** 열이든 스키마를 변경하면 등록 해제가 필요합니다. 현재는 편집을 받지 않는 상태라도 마찬가지입니다. 스키마 변경에는 열 이름과 기본 타입(base type)의 변경이 포함됩니다.

**주의**: 스키마 변경은 자동 등록 해제를 일으키지 않습니다(Schema changes do not trigger automatic unregistering). Object Storage v1(Phonograph)은 이러한 스키마 변경에 대응해 링크 타입의 백킹 데이터소스를 자동으로 등록 해제하지 **않습니다**. 대신 재인덱싱이 실패하며, 저장한 스키마 변경을 되돌리거나, 링크 타입 Datasources 페이지의 Phonograph 창에서 백킹 데이터소스를 수동으로 등록 해제한 뒤 다시 등록해야만 성공합니다.

편집 이력이 지워질 위험이 있는 변경을 저장하려고 하면, 편집에 미칠 수 있는 영향에 대한 경고가 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-link-type-warning-edit-impact.png" alt="편집에 미치는 영향에 대한 경고" width="500" />

이제 기존 링크 타입을 편집할 때 고려할 사항을 이해했으니, 안전하게 변경을 진행할 수 있습니다.

**설명**: 라이트백 데이터셋은 "원본 데이터 + 사용자가 지금까지 한 편집 이력"을 합쳐 계산한 결과입니다. 예를 들어 원본에 링크가 3개 있고 사용자가 1개를 추가하고 1개를 삭제했다면, 빌드할 때마다 원본 3개에 이력(추가 1, 삭제 1)을 차례로 다시 적용해 최종 3개를 만듭니다. 이력이 지워지면 이 재계산 자체를 할 수 없으므로 빌드가 실패합니다.

> **중간 요약**: 다대다 백킹 데이터소스, 카디널리티, 외래 키 변경과 삭제는 재인덱싱을 일으켜 그동안 링크를 쓸 수 없게 만듭니다. 라이트백이 있는 링크 타입은 여기에 더해 열 스키마 변경도 편집 이력 삭제 위험이 있고, 이 경우 재인덱싱이 자동으로 처리되지 않고 실패합니다.

<a id="edit-an-existing-link-type"></a>
## 기존 링크 타입 편집 (Edit an existing link type)

* [기존 링크 타입으로 이동](#navigate-to-an-existing-link-type)
* [링크 타입 삭제](#delete-a-link-type)
* [백킹 데이터소스 변경](#change-a-backing-datasource)
* [링크 타입 메타데이터 편집](#edit-a-link-types-metadata)

<a id="navigate-to-an-existing-link-type"></a>
### 기존 링크 타입으로 이동 (Navigate to an existing link type)

홈 페이지 사이드바에서 링크 타입 페이지를 선택하고 목록에서 다른 링크 타입을 고르면 언제든지 작업 중인 링크 타입을 바꿀 수 있습니다. 애플리케이션 헤더의 검색창에서 다른 링크 타입을 검색할 수도 있습니다. [탐색(navigation)](../../../05_applications/04_ontology-manager/02_navigation.md)에 대해 더 읽어 보세요.

<a id="delete-a-link-type"></a>
### 링크 타입 삭제 (Delete a link type)

링크 타입 뷰 사이드바 오른쪽 위의 ![...](https://www.palantir.com/docs/resources/foundry/object-link-types/three-dots.png) (점 세 개) 아이콘을 선택한 뒤(아래 이미지 참고) 드롭다운에서 **Delete**(삭제) 옵션을 선택하면 객체 타입(원문 표기 그대로이며, 문맥상 링크 타입을 뜻합니다)을 삭제할 수 있습니다. 링크 타입을 삭제 대상으로 스테이징할지 확인하는 대화 상자가 나타납니다.

* 링크 타입 삭제는 변경 사항을 저장한 뒤에야 적용되며, 해당 객체 타입을 참조하는 모든 뷰와 애플리케이션을 깨뜨립니다.
* `active` 상태인 링크 타입은 삭제할 수 없습니다. [상태(status)](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-link-type-delete-link-type.png" alt="링크 타입 삭제" width="500" />

**설명**: "스테이징(staging)"은 변경을 바로 반영하지 않고 저장 대기 목록에 올려 두는 것입니다. Ontology Manager에서는 여러 변경을 모아 두었다가 저장할 때 한꺼번에 반영하므로, 삭제도 저장 전까지는 취소할 수 있습니다.

<a id="change-a-backing-datasource"></a>
### 백킹 데이터소스 변경 (Change a backing datasource)

백킹 데이터소스는 다음과 같이 변경할 수 있습니다.

1. 링크 타입 뷰의 **Datasources** 페이지로 이동합니다.
2. 기존 데이터소스 옆의 ![pen](https://www.palantir.com/docs/resources/foundry/object-link-types/pen.png) **Select** 아이콘을 선택합니다. 그러면 Foundry에서 사용할 수 있는 데이터소스를 둘러보고 선택할 수 있습니다.

**주의**: 키는 스키마가 일치할 때만 자동으로 다시 매핑됩니다(Keys only remap automatically when the schema matches). 링크 타입의 백킹 데이터소스를 변경하면 이전 데이터소스의 열과 링크 타입을 정의하는 키 사이의 연결이 모두 제거됩니다. 이전 데이터소스와 **같은 스키마를** 가진 새 데이터소스로 바꿀 때**만** 키가 자동으로 다시 매핑됩니다. 그렇지 않으면 새 데이터소스에 키를 직접 다시 매핑해야 합니다.

![백킹 데이터소스 선택](https://www.palantir.com/docs/resources/foundry/object-link-types/edit-link-type-change-backing-datasource-annotated.png)

<a id="edit-a-link-types-metadata"></a>
### 링크 타입 메타데이터 편집 (Edit a link type's metadata)

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-link-type-metadata-new-overview.png" alt="링크 타입 메타데이터 편집" width="500" />

1. **Status(상태):** 링크 타입 창 위쪽의 현재 상태를 선택하면 사용할 수 있는 상태의 드롭다운이 열립니다. `deprecated`, `experimental`, `active` 중에서 선택합니다.
   * [상태](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.
2. **Key(키):** 드롭다운에서 선택해 외래 키를 바꾸거나, 다대다 링크 타입의 열 매핑을 바꿉니다.
   * 다대다 카디널리티 링크 타입에서는 백킹 데이터소스의 열이 객체 타입의 기본 키(primary key)에 매핑되어야 합니다. 객체 타입의 기본 키 속성(property) 타입이 링크 타입 백킹 데이터소스에서 매핑되는 열의 타입과 다르면 오류가 발생해 저장할 수 없습니다.
   * 그 밖의 카디널리티를 가진 링크 타입에서는, 두 객체 타입 중 하나의 키가 반드시 그 객체 타입의 기본 키에 매핑되어야 합니다. 이렇게 해서 카디널리티의 "일(one)" 쪽이 유일하도록 보장합니다.
3. **API name(API 이름):** 기존 API 이름을 선택해 값을 바꿉니다.
   * `active` 상태인 링크 타입은 API 이름을 바꿀 수 없습니다.
     * [상태](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.
     * [유효한 API 이름](../02_object-types/02_create-object-type.md#configure-api-names)에 대해 더 읽어 보세요.
4. **Visibility(가시성):** 링크 가시성 목록에서 가시성을 확인합니다. `prominent` 링크 타입은 애플리케이션이 이 링크 타입을 사용자에게 먼저 보여 주도록 합니다. `hidden` 링크 타입은 사용자 애플리케이션에 나타나지 않습니다.
5. **Type classes(타입 클래스):** 애플리케이션이 해석할 수 있는 추가 메타데이터로 타입 클래스를 적용합니다.
   * 자세한 내용은 [사용 가능한 타입 클래스 목록](../09_metadata/01_metadata-typeclasses.md)을 참고하세요.

**설명**: 키 규칙은 관계형 데이터베이스의 규칙과 같습니다. 일대다 관계(예: Company 하나에 Employee 여러 명)에서는 Employee 테이블의 `employer_id`(외래 키)가 Company 테이블의 `company_id`(기본 키)를 가리켜야 "일" 쪽인 Company가 유일하게 정해집니다. 다대다 관계는 `(employee_id, project_id)` 쌍을 행으로 가지는 조인 테이블로 표현하며, 이 조인 테이블의 두 열이 각각 양쪽 객체 타입의 기본 키에 매핑되어야 하고 타입도 같아야 합니다(예: 기본 키가 String인데 조인 테이블 열이 Integer이면 저장 불가).

> **중간 요약**: 기존 링크 타입은 Ontology Manager에서 찾아 삭제, 백킹 데이터소스 변경, 메타데이터(상태, 키, API 이름, 가시성, 타입 클래스) 편집을 할 수 있습니다. `active` 상태에서는 삭제와 API 이름 변경이 막혀 있고, 데이터소스를 바꾸면 스키마가 같을 때만 키가 자동 매핑됩니다.

## 정리

- 링크 타입 편집 중 다대다 백킹 데이터소스 변경, 카디널리티 변경, 외래 키 변경, 삭제는 Phonograph 재인덱싱을 일으켜 그동안 링크를 쓸 수 없게 합니다.
- 라이트백이 있는 링크 타입은 백킹 데이터소스 등록 해제 시 편집 이력이 삭제되어 이후 라이트백 데이터셋 빌드가 실패하며, 편집을 받은 적이 있다면 열 스키마 변경만으로도 문제가 됩니다.
- 스키마 변경은 자동 등록 해제를 일으키지 않으므로 재인덱싱이 실패하고, 변경을 되돌리거나 수동으로 등록 해제와 재등록을 해야 합니다.
- 삭제와 메타데이터 편집은 저장해야 반영되며, `active` 상태의 링크 타입은 삭제와 API 이름 변경이 불가능합니다.
