# 인터페이스 정의 편집하기 (Edit an interface definition)

- 원문: https://www.palantir.com/docs/foundry/interfaces/edit-interface-definition/
- 사이드바 위치: Define Ontologies > Interfaces > Edit an interface definition

이 페이지는 이미 만든 인터페이스(interface)의 정의를 고치는 방법, 즉 속성(property), 공유 속성(shared property), 링크 타입 제약 조건, 액션 타입 제약 조건을 추가하거나 수정하거나 제거하는 방법을 설명합니다. 인터페이스는 여러 객체 타입과 애플리케이션이 의존하는 계약이므로, 정의를 바꿀 때 생기는 호환성 문제(breaking change)를 먼저 경고합니다.

**주의**: 호환성을 깨는 변경(Breaking changes). 인터페이스는 API 이름을 노출하므로, 인터페이스 정의를 변경하면 다운스트림 애플리케이션이 깨질 가능성이 있고, 기존 객체 구현은 반드시 깨집니다. 인터페이스에 새 필수 속성, 링크 타입 제약 조건, 액션 타입 제약 조건을 추가할 때는 그 인터페이스를 사용하는 객체 타입의 모든 구현을 온톨로지의 같은 업데이트 안에서 **반드시** 함께 수정해야 합니다. 또한 인터페이스 정의와 그 소비자(consumer)를 동시에 업데이트할 것을 권장합니다.

다운스트림 애플리케이션을 인터페이스 변경과 동시에 업데이트할 수 없다면, 대안으로 인터페이스의 새 버전을 ([확장](08_extend-interface.md)으로 또는 독립된 인터페이스로) 만들고 가능한 한 빨리 새 인터페이스 정의로 이전(migrate)할 수 있습니다.

**설명**: 다운스트림(downstream)은 어떤 리소스를 가져다 쓰는 쪽을 말합니다. 예를 들어 `Facility` 인터페이스의 `facilityName` 속성을 읽는 Workshop 모듈이나 OSDK 코드가 다운스트림 애플리케이션입니다. API 이름을 `facilityName`에서 `name`으로 바꾸면 이 코드는 존재하지 않는 필드를 찾게 되어 동작하지 않습니다. 또 필수 속성을 새로 추가하면, 그 인터페이스를 구현한 `Airport` 객체 타입에는 아직 그 속성의 매핑이 없으므로 구현이 더 이상 유효하지 않게 됩니다. 그래서 같은 저장 작업 안에서 모든 구현의 매핑을 함께 채워야 합니다.

<a id="add-new-properties"></a>
## 새 속성 추가하기 (Add new properties)

인터페이스 구성의 **Properties** 탭에서 **New property**를 선택합니다. 인터페이스 속성 구성 사이드 패널이 열립니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/edit-interface-properties.png" alt="인터페이스 속성 편집." width="800" />

속성 메타데이터를 편집하는 옵션은 네 개의 탭으로 묶여 있으며, 다음 구성에 접근할 수 있습니다.

1. **표시 이름과 설명(Display name and description):** 기존 표시 이름이나 설명을 선택해 텍스트를 수정합니다.
2. **API 이름(API name):** 기존 API 이름을 선택해 값을 변경합니다.
3. **속성 기본 타입(Property base type):** 드롭다운 메뉴에서 속성의 기본 타입(base type)을 선택합니다. 속성의 타입은 그 속성 값에 대해 수행할 수 있는 연산의 범위를 제한합니다.
   * 예를 들어 기본 타입이 `timestamp`인 속성은 Object Explorer의 타임라인 위젯에 표시할 수 있습니다.
4. **기본 키 제약 조건(Primary key constraint):** 속성이 기본 키(primary key)여야 하는지, 또는 기본 키가 될 수 없는지를 지정합니다.

**주의**: 인터페이스 속성 타입을 변경하면, 이 인터페이스를 구현하는 모든 객체 타입도 함께 업데이트해야 합니다.

5. **타입 클래스(Type classes):** 애플리케이션이 해석할 수 있는 추가 메타데이터로 타입 클래스를 적용합니다.
   * 사용 가능한 타입 클래스 목록은 [타입 클래스 문서](../02_object-and-link-types/09_metadata/01_metadata-typeclasses.md)를 참고하세요.
6. **렌더 힌트(Render hints):** 체크리스트에서 렌더 힌트를 선택해 속성 값이 표시되는 방식과 Object Storage v1(Phonograph)에 인덱싱되는 방식을 개선합니다.
   * 사용 가능한 렌더 힌트의 설명은 [렌더 힌트 문서](../02_object-and-link-types/09_metadata/02_metadata-render-hints.md)를 참고하세요.
7. **가시성(Visibility):** 기존 가시성을 선택하면 사용 가능한 가시성 값의 드롭다운 메뉴가 열립니다. `prominent` 속성은 애플리케이션이 사용자에게 이 속성을 먼저 보여 주게 합니다. `hidden` 속성은 사용자 애플리케이션에 나타나지 않습니다.

**설명**: 원문은 "네 개의 탭"이라고 적은 뒤 일곱 항목을 나열합니다. 화면의 탭 구성과 항목 수가 일대일로 대응하지 않을 수 있으므로 실제 화면을 함께 확인하는 것이 좋습니다. 기본 타입은 프로그래밍 언어의 자료형에 해당합니다. `timestamp` 타입이면 시간 순 정렬과 타임라인 표시가 가능하고, `string`이면 그렇지 않은 식으로, 타입에 따라 쓸 수 있는 기능이 정해집니다.

> **중간 요약**: **Properties** 탭의 **New property**로 인터페이스 속성을 추가하고, 표시 이름, API 이름, 기본 타입, 기본 키 제약 조건, 타입 클래스, 렌더 힌트, 가시성을 설정합니다. 속성 타입을 바꾸면 모든 구현 객체 타입도 고쳐야 합니다.

<a id="add-shared-properties"></a>
## 공유 속성 추가하기 (Add shared properties)

인터페이스 구성의 **Properties** 탭에서 **Add shared properties**를 선택하고 인터페이스에 추가할 공유 속성을 고릅니다.

<a id="add-a-link-type-constraint"></a>
## 링크 타입 제약 조건 추가하기 (Add a link type constraint)

**Link type constraints** 탭에서 **Create new link type constraint**를 선택하고 필요한 [제약 조건 메타데이터](02_create-interface.md#create-interface-link-types-optional)를 추가합니다.

<a id="add-an-action-type-constraint"></a>
## 액션 타입 제약 조건 추가하기 (Add an action type constraint)

**Action type constraints** 탭에서 **Create new action type constraint**를 선택하고 필요한 [제약 조건 메타데이터](07_interface-action-type-constraints.md#action-type-constraints)와 [파라미터 제약 조건](07_interface-action-type-constraints.md#parameter-constraints)을 추가합니다.

> **중간 요약**: 공유 속성, 링크 타입 제약 조건, 액션 타입 제약 조건은 각각 해당 탭에서 추가 버튼을 눌러 덧붙입니다.

<a id="remove-properties"></a>
## 속성 제거하기 (Remove properties)

**Properties** 탭에서 인터페이스에서 제거할 속성 옆의 **...** 를 선택합니다. 또는 인터페이스 속성 사이드 패널을 열고 오른쪽 위의 휴지통 아이콘을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/remove-property-from-interface.png" alt="인터페이스에서 속성 제거." width="800" />

<a id="remove-or-edit-link-type-constraints"></a>
## 링크 타입 제약 조건 제거 또는 편집하기 (Remove or edit link type constraints)

**Link type constraint** 탭에서 인터페이스에서 편집하거나 제거할 링크 타입 제약 조건 옆의 **...** 를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/remove-link-type-constraint.png" alt="링크 타입 제약 조건 제거 또는 편집." width="800" />

제약 조건을 편집하는 경우, 처음 [링크 타입 제약 조건을 만들 때](02_create-interface.md#create-interface-link-types-optional)와 같은 방식으로 메타데이터를 업데이트할 수 있습니다.

<a id="remove-or-edit-action-type-constraints"></a>
## 액션 타입 제약 조건 제거 또는 편집하기 (Remove or edit action type constraints)

**Action type constraints** 탭에서 인터페이스에서 편집하거나 제거할 액션 타입 제약 조건 옆의 **...** 를 선택합니다.

제약 조건을 편집하는 경우, 처음 [액션 타입 제약 조건을 만들 때](07_interface-action-type-constraints.md#action-type-constraints)와 같은 방식으로 메타데이터와 파라미터 구성을 업데이트할 수 있습니다.

> **중간 요약**: 속성과 제약 조건의 제거나 편집은 각 탭에서 항목 옆 **...** 메뉴로 하며, 편집 화면은 처음 만들 때와 같습니다.

## 정리

- 인터페이스는 API 이름을 노출하는 계약이므로 정의 변경은 다운스트림 애플리케이션과 기존 구현을 깨뜨릴 수 있습니다.
- 새 필수 속성이나 필수 제약 조건을 추가할 때는 모든 구현을 같은 온톨로지 업데이트 안에서 함께 고쳐야 하며, 어려우면 새 버전의 인터페이스를 만들어 이전합니다.
- 속성 추가 시 표시 이름, API 이름, 기본 타입, 기본 키 제약 조건, 타입 클래스, 렌더 힌트, 가시성을 설정합니다.
- 공유 속성, 링크 타입 제약 조건, 액션 타입 제약 조건은 각 탭에서 추가, 편집, 제거합니다.
