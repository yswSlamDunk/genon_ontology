# 구조체와 공유 속성 (Structs and shared properties)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/struct-shared-properties/
- 사이드바 위치: Define Ontologies > Object and link types > Structs > Structs and shared properties

이 페이지는 구조체(struct) 타입 속성을 공유 속성(shared property)과 함께 쓰는 방법을 설명합니다. 구조체 타입 공유 속성을 새로 만들고, 기존 구조체 속성에 연결하고, 기존 구조체 속성을 공유 속성으로 변환하는 절차를 다룹니다. 여러 객체 타입이 같은 구조의 복합 값(예: 주소)을 가질 때 그 정의를 한곳에서 관리하려면 이 내용이 필요합니다.

구조체 속성은 로컬 속성 타입과 공유 속성 타입 모두에서 사용할 수 있습니다. 로컬 속성 타입을 공유 속성 타입으로 변환(승격)할 때는 구조체 필드를 다시 매핑해야 합니다. 공유 속성 타입이 뒷받침하는 로컬 구조체 속성 타입은 구조체 필드의 리소스 식별자(RID)를 제외한 공유 속성 타입의 필드를 상속합니다. 즉 구조체 필드 메타데이터(표시 이름, 설명, 별칭)는 공유 속성 타입에서 상속되지만, 구조체 필드는 원래의 RID를 유지합니다.

**설명**: "로컬 속성"은 특정 객체 타입 하나에만 정의된 일반 속성이고, "공유 속성"은 여러 객체 타입이 함께 쓰도록 따로 정의된 속성입니다. 예를 들어 `Employee`와 `Customer`가 모두 `address` 구조체 속성(필드: `street`, `city`, `zip`)을 가진다면, `address`를 공유 속성으로 만들어 두 객체 타입이 연결해 쓰게 할 수 있습니다. 이때 필드의 이름과 설명 같은 메타데이터는 공유 속성의 것을 따르지만, 각 필드를 가리키는 고유 식별자(RID)는 원래 로컬 속성에 있던 값이 그대로 남습니다.

<a id="create-a-struct-type-shared-property"></a>
## 구조체 타입 공유 속성 만들기

1. Ontology Manager에서 두 가지 방법으로 구조체 타입 공유 속성을 만들 수 있습니다.
   * 홈페이지 오른쪽 위에서 **New > Shared property**를 선택합니다.
      <img src="https://www.palantir.com/docs/resources/foundry/object-link-types/new-dropdown-menu-shared-property.png" alt="New 드롭다운 메뉴의 Shared property 옵션." width="300" />

   * **Shared properties > + New shared property**를 선택합니다.
      <img src="https://www.palantir.com/docs/resources/foundry/object-link-types/new-shared-property-button.png" alt="Shared properties 탭의 + New shared property 옵션." width="500" />

2. 메인 패널에서 **New shared property** 버튼을 선택합니다. 그러면 이름, 설명, 별칭, API 이름 등 공유 속성의 메타데이터를 설정할 수 있는 도우미 창이 열립니다. 이어서 **Next**를 선택해 진행합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-shared-property-modal.png" alt="'Create shared property' 대화 상자." width="500" />

3. 기본 타입(base type), 값 타입(value type), 가시성(visibility), 그리고 속성에 값을 필수로 요구할지 여부를 설정합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-shared-property-configuration.png" alt="설정 단계의 Create shared property 창." width="500" />

4. 이 공유 속성을 저장할 프로젝트를 선택합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-shared-property-save-location.png" alt="공유 속성의 저장 위치 선택." width="500" />

5. Ontology Manager로 돌아와 오른쪽 위의 **Save**를 선택해 [온톨로지에 변경 사항을 반영](../../../05_applications/04_ontology-manager/06_change-management/01_save-changes.md)합니다.

**설명**: 구조체 타입 공유 속성을 만들려면 3단계에서 기본 타입으로 구조체(struct)를 고르고 필드를 정의합니다. 5단계의 **Save**를 누르기 전까지는 변경 사항이 온톨로지에 실제로 기록되지 않습니다.

> **중간 요약**: 구조체 타입 공유 속성은 **New > Shared property** 또는 **Shared properties** 탭에서 만들며, 메타데이터, 타입 설정, 저장 프로젝트 선택을 거친 뒤 **Save**로 반영합니다.

<a id="attach-a-struct-type-shared-property"></a>
## 구조체 타입 공유 속성 연결하기

1. Ontology Manager에서 **Properties** 탭을 열고 **Properties** 표에서 원하는 속성을 선택합니다.
2. 오른쪽의 **Property editor**에서 아래로 스크롤해 **Shared property**로 이동한 뒤 **Assign** 아래에서 공유 속성을 선택합니다. 이렇게 하면 두 속성이 속성 메타데이터를 공유합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/spt-attachment.png" alt="Assign 섹션의 공유 속성 드롭다운." width="500" />

**참고:** 로컬 구조체 속성 타입에 공유 속성 타입을 할당한 뒤 새 구조체 필드를 추가하려면, 새 구조체 필드를 공유 속성 타입에 추가하고, 그 공유 속성이 뒷받침하는 모든 로컬 구조체 속성 타입에서 해당 필드를 데이터소스 열에 매핑해야 합니다.

**설명**: 예를 들어 `address` 공유 속성을 `Employee`와 `Customer`가 함께 쓰는 상태에서 `country` 필드를 새로 넣고 싶다면, 먼저 공유 속성 `address`에 `country` 필드를 추가하고, 다음으로 `Employee`의 데이터소스와 `Customer`의 데이터소스 양쪽에서 `country`에 해당하는 열을 각각 매핑해야 합니다. 필드 정의는 한곳에서 하지만, 실제 데이터는 객체 타입마다 다른 데이터소스에서 오기 때문입니다.

> **중간 요약**: 기존 구조체 속성의 **Property editor** 에서 **Assign**으로 공유 속성을 연결하면 메타데이터가 공유됩니다. 필드를 추가할 때는 공유 속성에 먼저 추가하고, 이를 쓰는 모든 객체 타입에서 열 매핑을 해 주어야 합니다.

<a id="convert-a-struct-property-type-into-a-shared-property"></a>
## 구조체 속성 타입을 공유 속성으로 변환하기

다음은 구조체 속성을 공유 속성 타입이 뒷받침하는 구조체 속성으로 변환하는 방법입니다.

1. Ontology Manager에서 **Properties** 탭을 열고 **Properties** 표에서 원하는 속성을 선택합니다.
2. 오른쪽의 **Property editor**에서 아래로 스크롤해 **Convert to a shared property**를 선택합니다. 그러면 구조체 속성이 공유 속성 타입의 뒷받침을 받게 됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/spt-convert.png" alt="Property editor의 'Convert to a shared property' 버튼." width="500" />

## 정리

- 구조체 속성은 로컬 속성과 공유 속성 양쪽에서 사용할 수 있습니다.
- 공유 속성이 뒷받침하는 로컬 구조체 속성은 필드 메타데이터(표시 이름, 설명, 별칭)를 상속하지만 필드 RID는 원래 값을 유지합니다.
- 공유 속성은 새로 만들 수도 있고(**New shared property**), 기존 속성에 연결할 수도 있고(**Assign**), 기존 속성을 변환할 수도 있습니다(**Convert to a shared property**).
- 연결 후 필드를 추가하려면 공유 속성에 필드를 넣고 모든 사용처에서 열 매핑을 해야 합니다.
