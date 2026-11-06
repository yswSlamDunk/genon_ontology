# 인터페이스 구현 편집하기 (Edit an interface implementation)

- 원문: https://www.palantir.com/docs/foundry/interfaces/edit-interface-implementation/
- 사이드바 위치: Define Ontologies > Interfaces > Edit an interface implementation

이 페이지는 객체 타입에 이미 적용한 인터페이스(interface) 구현을 삭제하거나, 구현에 쓰인 속성(property)과 링크 타입 매핑을 바꾸는 방법을 짧게 설명합니다. 인터페이스 자체의 정의가 아니라 특정 객체 타입 쪽의 구현 설정을 고치는 작업입니다.

객체에 인터페이스를 구현한 뒤에는 구현을 삭제하거나 매핑을 변경해서 구현을 업데이트할 수 있습니다.

먼저 Ontology Manager를 열고, 편집하려는 인터페이스 구현이 있는 객체로 이동합니다.

<a id="1-delete-an-interface-implementation"></a><a id="delete-an-interface-implementation"></a>
## 1. 인터페이스 구현 삭제하기 (Delete an interface implementation)

**...** 아이콘을 선택하고 **Remove interface**를 선택해 이 객체 타입에서 인터페이스 구현을 삭제합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/remove-interface-implementation.png" alt="인터페이스 구현 제거." width="800" />

오른쪽 위의 **Save**를 선택해 온톨로지를 업데이트합니다.

<a id="update-implementation-mappings"></a>
## 구현 매핑 업데이트하기 (Update implementation mappings)

드롭다운 메뉴를 선택해 인터페이스를 구현하는 데 사용되는 속성이나 링크 타입을 변경합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/update-interface-implementation-mapping.png" alt="인터페이스 구현 매핑 업데이트" width="800" />

오른쪽 위의 **Save**를 선택해 온톨로지를 업데이트합니다.

**설명**: 매핑 변경의 예를 들면, `Airport` 객체 타입이 처음에는 `airportCode` 속성을 `Facility` 인터페이스의 `facilityName`에 매핑했는데 나중에 사람이 읽기 좋은 `airportName`으로 바꾸고 싶을 때 이 드롭다운을 사용합니다. 인터페이스를 통해 `facilityName`을 읽는 코드는 그대로 두어도, 저장 후에는 `Airport` 객체에 대해 `airportName` 값이 반환됩니다.

## 정리

- 인터페이스 구현의 편집은 Ontology Manager에서 해당 객체 타입으로 이동해 진행합니다.
- **...** 메뉴의 **Remove interface**로 구현을 삭제할 수 있습니다.
- 드롭다운 메뉴로 구현에 쓰인 속성이나 링크 타입 매핑을 바꿀 수 있습니다.
- 어느 경우든 마지막에 **Save**를 눌러야 온톨로지에 반영됩니다.
