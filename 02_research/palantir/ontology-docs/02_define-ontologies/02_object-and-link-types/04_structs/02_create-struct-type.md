# 구조체 속성 타입 만들기 (Create a struct type)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/create-struct-type/
- 사이드바 위치: Define Ontologies > Object and link types > Structs > Create a struct type

이 페이지는 Ontology Manager에서 기존 객체 타입(object type)에 구조체(struct) 속성을 새로 만드는 절차를 단계별로 안내합니다. 속성 이름과 기본 타입을 정하고, 구조체 타입 열을 백킹 열로 고른 뒤, 구조체 필드를 하나씩 추가해 데이터소스 열에 매핑하는 순서로 진행합니다.

Ontology Manager의 **Object types** 페이지에서 새 구조체 속성을 만들고 구성합니다. 구조체 속성에 대한 자세한 정보는 [개요](01_structs-overview.md)를 참고하세요.

1. Ontology Manager에서 왼쪽 사이드바의 **Object types** 탭을 열고 기존 객체 타입을 선택합니다.
2. 객체 타입 세부 정보 페이지에서 왼쪽 사이드바의 **Properties** 탭을 열고, **Properties** 표 오른쪽 위의 **Create property** 버튼을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-struct-from-ontology-manager.png" alt="객체 타입의 Properties 표와 'Property editor' 패널."  width="500" />

3. **Property editor** 패널에서 이름과 설명을 추가하고, **Base type** 드롭다운 메뉴에서 **Struct**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/name-struct-from-ontology-manager.png" alt="'Struct'가 선택된 Base type 드롭다운." width="500" />

4. **Data** 영역까지 스크롤해 드롭다운에서 **Backing column**(백킹 열)을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/backing-column-struct-ontology-manager.png" alt="Property editor의 Data 영역에서 백킹 열을 선택합니다." width="500" />

5. **Struct fields** 영역에서 **Add field**를 선택한 다음 **New field**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/struct-field-ontology-manager.png" alt="구조체 속성 타입의 구조체 필드 예시." width="500" />

6. 새 구조체 필드의 이름을 정하고, 선택적으로 설명을 추가합니다.
7. 마지막으로 데이터소스의 열을 새 구조체 필드에 매핑합니다.

**설명**: 예를 들어 백킹 데이터셋에 `address`라는 구조체 타입 열이 있고 그 안에 `street`, `city`, `postal_code` 하위 필드가 있다고 합시다. 4단계에서 `address` 열을 백킹 열로 고르고, 5\~7단계를 세 번 반복해 구조체 필드 `street`, `city`, `postalCode`를 만든 뒤 각각을 열 안의 하위 필드에 연결합니다. 백킹 열은 반드시 구조체 타입 열이어야 하므로, 여러 일반 열에 흩어진 값은 미리 파이프라인에서 하나의 구조체 열로 묶어 두어야 합니다.

## 정리

- 구조체 속성은 객체 타입의 **Properties** 탭에서 **Create property**를 눌러 만듭니다.
- **Property editor**에서 **Base type**을 **Struct**로 고르고, **Data** 영역에서 구조체 타입의 백킹 열을 선택합니다.
- **Struct fields** 영역에서 **Add field**, **New field**로 필드를 추가하고 이름을 정한 뒤 데이터소스 열에 매핑합니다.
