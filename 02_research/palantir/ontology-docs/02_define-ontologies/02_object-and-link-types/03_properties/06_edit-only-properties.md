# 편집 전용 속성 (Edit-only properties)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/edit-only-properties/
- 사이드바 위치: Define Ontologies > Object and link types > Properties > Edit-only properties

이 페이지는 백킹 데이터셋의 열에 매핑되지 않고, 사용자의 편집(edit)으로만 값이 채워지는 편집 전용 속성(edit-only property)을 설명합니다. 원본 데이터셋을 고치지 않고 객체에 추가 정보를 저장하고 싶을 때 쓰며, 만드는 방법과 나중에 실제 열에 매핑하는 방법을 다룹니다.

편집 전용 속성을 사용하면 객체 타입의 백킹 데이터셋에 있는 열에 직접 매핑되지 않는 온톨로지 속성을 정의할 수 있습니다.
이 기능은 기반 데이터셋을 수정하지 않고 객체 타입과 함께 추가 정보를 저장하고 싶은 상황에서 특히 유용합니다.

모든 속성 값을 사용자 편집으로 채우려 한다면 [백킹 데이터소스 없이 객체 타입 만들기](../02_object-types/02_create-object-type.md#create-an-object-type-without-a-backing-datasource)를 고려하세요.

**설명**: 예를 들어 `Ticket` 객체 타입이 외부 시스템에서 동기화되는 데이터셋(`ticket_id`, `title`, `created_at` 열)으로 만들어져 있다고 합시다. 현장 담당자가 각 티켓에 `reviewNote`(검토 메모)를 남기고 싶은데, 원본 데이터셋은 외부 시스템이 관리하므로 열을 추가할 수 없습니다. 이때 `reviewNote`를 편집 전용 속성으로 만들면, 처음에는 모든 객체에서 값이 비어 있다가 사용자가 액션으로 값을 쓰면 그 편집 내용이 온톨로지에 저장됩니다.

<a id="summary-of-edit-only-properties"></a>
## 편집 전용 속성 요약 (Summary of edit-only properties)

편집 전용 속성을 다룰 때는 다음을 염두에 두세요.

* **백킹 데이터셋의 열에 매핑하지 않음:** 편집 전용 속성은 백킹 데이터셋의 특정 열에 매핑할 필요가 없습니다. 덕분에 백킹 열이 생기기 전에 새 속성을 쉽게 만들거나, 온톨로지를 통해서만 편집될 속성을 만들 수 있습니다.
* **객체 타입의 백킹 데이터셋 중 하나에 권한이 연결됨:** 데이터 일관성과 보안을 보장하기 위해, 편집 전용 속성은 객체 타입을 뒷받침하는 데이터셋 중 하나에 권한(permission)이 연결되어야 합니다.
* **Object Storage v2에서만 사용 가능:** 편집 전용 속성은 Object Storage v2를 사용하는 객체 타입에서만 쓸 수 있는 기능입니다.

**설명**: "데이터셋에 권한이 연결된다"는 것은 이 속성 값을 누가 볼 수 있는지를, 지정한 백킹 데이터셋의 접근 권한을 기준으로 판단한다는 뜻입니다. 편집 전용 속성에는 자기 열이 없으므로, 권한 판단의 기준이 될 데이터셋을 따로 지정해 주어야 합니다.

<a id="creating-edit-only-properties"></a>
### 편집 전용 속성 만들기 (Creating edit-only properties)

1. **Ontology Manager**로 이동합니다.
2. 편집 전용 속성을 추가할 객체 타입을 선택합니다.
3. **Create Property**(속성 만들기)를 선택하고 속성 이름, 타입, 설명 등 필요한 세부 정보를 채웁니다.
4. **Data** 섹션에서 **Edit-only property** 토글을 켜고, 권한을 연결할 데이터셋을 선택합니다(객체 타입을 뒷받침하는 데이터셋이 둘 이상인 경우).
5. 변경 사항을 **Save**(저장)해 편집 전용 속성을 만듭니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/edit_only_property.png" alt="편집 전용 속성" width="300" />

<a id="mapping-edit-only-properties-to-dataset-columns"></a>
### 편집 전용 속성을 데이터셋 열에 매핑하기 (Mapping edit-only properties to dataset columns)

나중에 현재 편집 전용인 속성에 대응하는 열을 백킹 데이터셋에 추가하기로 했다면, 그 속성을 새 열에 쉽게 매핑할 수 있습니다.

1. **Ontology Manager**로 이동합니다.
2. 매핑하려는 편집 전용 속성이 있는 객체 타입을 선택합니다.
3. 편집 전용 속성을 선택해 세부 정보를 엽니다.
4. **Data** 섹션에서 편집 전용 속성 토글을 끄고, 백킹 데이터셋 중 하나의 열을 선택합니다.
5. 변경 사항을 **Save**(저장)합니다.

> **중간 요약**: 편집 전용 속성은 열 매핑 없이 사용자 편집으로만 값이 채워지는 속성으로, 백킹 데이터셋 하나에 권한을 연결해야 하고 Object Storage v2에서만 쓸 수 있습니다. Data 섹션의 토글로 만들고, 나중에 토글을 끄고 열을 골라 일반 속성으로 바꿀 수 있습니다.

## 정리

- 편집 전용 속성은 백킹 데이터셋의 열에 매핑되지 않고 온톨로지 편집으로만 값을 가지는 속성입니다.
- 원본 데이터셋을 바꾸지 않고 추가 정보를 저장하거나, 열이 생기기 전에 속성을 먼저 만들 때 유용합니다.
- 권한은 객체 타입의 백킹 데이터셋 중 하나에 연결해야 하며, Object Storage v2 전용 기능입니다.
- Ontology Manager의 Data 섹션에서 Edit-only property 토글로 만들고, 토글을 끄면 실제 열에 매핑할 수 있습니다.
