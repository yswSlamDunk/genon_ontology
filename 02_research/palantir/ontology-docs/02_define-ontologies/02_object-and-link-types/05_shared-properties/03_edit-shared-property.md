# 공유 속성 편집하기 (Edit shared properties)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/edit-shared-property/
- 사이드바 위치: Define Ontologies > Object and link types > Shared properties > Edit shared properties

이 페이지는 이미 만든 공유 속성(shared property)의 메타데이터를 수정하는 방법과 공유 속성을 삭제하는 방법을 설명합니다. 공유 속성은 여러 객체 타입이 함께 쓰므로, 수정하면 사용하는 모든 객체 타입에 영향이 가고 삭제하면 그 객체 타입들의 속성이 일반 속성으로 돌아간다는 점을 알아 두어야 합니다.

<a id="edit-shared-property-metadata"></a>
### 공유 속성 메타데이터 편집하기

Ontology Manager의 **Shared property** 페이지에서 편집할 공유 속성을 먼저 선택하면 해당 공유 속성의 메타데이터를 편집할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit-shared-property.png" alt="공유 속성 메타데이터 편집" width="500" />

공유 속성 메타데이터를 편집하는 옵션은 **General**, **Display**, **Interaction**, **Details**의 네 가지 탭으로 묶여 있습니다. 이 탭에는 다음 설정이 들어 있습니다.

* **이름(Name):** 공유 속성의 이름입니다.
* **설명(Description):** 공유 속성에 대한 설명 텍스트입니다. 예를 들어 `start date` 공유 속성의 설명은 `The day the employee or contractor began working`(직원 또는 계약자가 근무를 시작한 날)일 수 있습니다.
* **기본 타입(Base type):** 이 속성의 값 타입을 나타내며, 사용자 애플리케이션에서 쓸 수 있는 연산의 집합을 결정합니다. 예를 들어 `start date` 속성의 기본 타입은 `date`입니다. 사용자 애플리케이션에서는 이 속성으로 타임라인 위젯을 구성할 수 있습니다.
* **값 서식(Value formatting):** 속성의 기본 타입에 따라 숫자 서식, 날짜 및 시간 서식, 사용자 ID 서식, 리소스 ID 서식을 속성에 적용할 수 있으며, 원시 값을 사용자 애플리케이션에서 더 읽기 쉬운 형태로 바꿔 줍니다. [값 서식](../03_properties/03_value-formatting.md)에 대해 더 알아보세요.
* **타입 클래스(Type classes):** 사용자 애플리케이션이 해석하는 추가 메타데이터입니다. [타입 클래스](../09_metadata/01_metadata-typeclasses.md)에 대해 더 알아보세요.
* **렌더 힌트(Render hints):** 같은 기본 타입의 다른 속성 대부분과 다르게 이 속성을 어떻게 렌더링할지 사용자 애플리케이션에 알려 주는 표시입니다. 많은 렌더 힌트는 해당 속성이 정의된 객체 타입의 재인덱싱(reindex) 성능에 영향을 줄 수 있습니다. 예를 들어 사용자 애플리케이션에서 아무도 `start date` 속성으로 검색하거나 정렬하지 않을 것으로 예상된다면, `searchable`과 `sortable` 렌더 힌트를 해제해 `Employee` 객체 타입의 재인덱싱 성능을 높일 수 있습니다. [렌더 힌트](../09_metadata/02_metadata-render-hints.md)에 대해 더 알아보세요.
* **가시성(Visibility):** 사용자 애플리케이션이 이 속성을 얼마나 눈에 띄게 표시할지 알려 주는 표시입니다. `prominent` 속성은 애플리케이션이 사용자에게 이 속성을 가장 먼저 보여 주게 합니다. `hidden` 속성은 사용자 애플리케이션에 나타나지 않습니다. 기본적으로 `start date` 속성의 가시성은 `normal`입니다.

또한 **Usage** 탭에서는 이 공유 속성을 사용하는 객체 타입을 볼 수 있고, **Permissions** 탭에서는 공유 속성의 권한을 업데이트할 수 있습니다.

**설명**: 공유 속성의 메타데이터를 바꾸면 그 공유 속성을 쓰는 모든 객체 타입의 해당 속성이 함께 바뀝니다. 그래서 수정 전에 **Usage** 탭에서 어떤 객체 타입이 영향을 받는지 확인해 두는 것이 좋습니다.

> **중간 요약**: 공유 속성 메타데이터는 **General**, **Display**, **Interaction**, **Details** 탭에서 편집하며, **Usage** 탭으로 사용처를, **Permissions** 탭으로 권한을 관리합니다.

<a id="delete-a-shared-property"></a>
### 공유 속성 삭제하기

공유 속성을 삭제하려면 다음 단계를 따릅니다.

1. Ontology Manager의 **Shared property** 페이지로 이동합니다.
2. 삭제할 공유 속성을 하나 이상 선택한 다음 **Delete property**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/delete-shared-property-button.png" alt="공유 속성 삭제" width="500" />

3. 모달에서 삭제 작업을 확인합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/delete-shared-property-modal.png" alt="공유 속성 삭제 확인" width="500" />

4. 오른쪽 위의 **Save**를 선택합니다.

**주의**: 공유 속성을 삭제하면 이 공유 속성을 사용하던 모든 객체 타입의 속성이 일반 속성으로 되돌아갑니다.

## 정리

- 공유 속성은 **Shared property** 페이지에서 선택해 네 개 탭(**General**, **Display**, **Interaction**, **Details**)으로 메타데이터를 편집합니다.
- **Usage** 탭은 사용처 객체 타입을, **Permissions** 탭은 권한을 다룹니다.
- 삭제는 **Delete property**, 확인, **Save** 순서로 진행합니다.
- 삭제해도 객체 타입의 속성 자체는 사라지지 않고 일반 속성으로 돌아갑니다.
