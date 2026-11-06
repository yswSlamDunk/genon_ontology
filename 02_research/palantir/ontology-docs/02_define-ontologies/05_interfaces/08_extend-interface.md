# 인터페이스 확장하기 (Extend an interface)

- 원문: https://www.palantir.com/docs/foundry/interfaces/extend-interface/
- 사이드바 위치: Define Ontologies > Interfaces > Extend an interface

이 페이지는 한 인터페이스가 다른 인터페이스를 확장(extend)해 그 내용을 물려받는 방법을 설명합니다. 확장을 쓰면 작은 인터페이스 여러 개를 조합해 더 구체적인 인터페이스를 만들 수 있습니다. Ontology Manager에서 확장을 추가하고 제거하는 절차가 담겨 있습니다.

인터페이스를 확장하면 여러 인터페이스를 조합해 새롭고 더 구체적인 인터페이스를 만들 수 있습니다. 이는 여러 [기능 인터페이스(capability interface)](01_interface-overview.md)를 구현하는 [추상 객체 인터페이스(abstract object interface)](01_interface-overview.md)를 구성할 때 특히 유용합니다. 인터페이스는 자신이 확장하는 인터페이스의 공유 속성(shared property), 링크 타입 제약, 액션 타입 제약을 상속합니다. 하나의 인터페이스는 다른 인터페이스를 개수 제한 없이 확장할 수 있습니다.

**설명**: Java의 `interface Facility extends Locatable, Maintainable { ... }`처럼 인터페이스가 여러 인터페이스를 동시에 상속하는 구조와 같은 개념입니다. 예를 들어 `Locatable` 인터페이스에 `latitude`, `longitude` 공유 속성이 있고 `Maintainable` 인터페이스에 `lastInspectionDate` 공유 속성이 있다면, 둘을 확장한 `Facility` 인터페이스는 세 속성을 모두 갖게 됩니다. `Facility`를 구현하는 객체 타입은 이 세 속성을 모두 매핑해야 합니다.

인터페이스를 확장하려면 아래 단계를 따르세요.

1. Ontology Manager에서 확장하려는 인터페이스를 선택해 인터페이스 개요 페이지를 엽니다.

2. 개요 페이지의 왼쪽 패널에서 **Extension**을 선택합니다.

3. 인터페이스 확장 페이지에서 **Add extension**(확장 추가)을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/extend-interface.png" alt="인터페이스에 확장 추가." width="800" />

4. 드롭다운 메뉴에서 현재 인터페이스가 확장할 인터페이스를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/confirm-extension.png" alt="인터페이스 확장 확인." width="500" />

5. 확인 대화 상자에서 인터페이스 확장으로 추가될 공유 속성, 링크 타입 제약, 액션 타입 제약을 검토한 뒤 **Confirm**을 선택합니다.

6. 오른쪽 위의 **Save**를 선택해 인터페이스 확장을 온톨로지에 추가합니다.

확장을 제거해 한 인터페이스를 다른 인터페이스에서 분리할 수도 있습니다. 이 작업은 인터페이스에서 상속된 공유 속성을 모두 제거하고, 상속된 링크 타입 제약과 상속된 액션 타입 제약을 모두 제거하며, 확장하는 인터페이스와 기반 인터페이스 사이의 연관을 해제합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/remove-interface-extension.png" alt="기존 인터페이스 확장 제거." width="800" />

## 정리

- 인터페이스 확장은 다른 인터페이스의 공유 속성, 링크 타입 제약, 액션 타입 제약을 상속받는 기능이며, 여러 인터페이스를 동시에 확장할 수 있습니다.
- 여러 기능 인터페이스를 조합해 추상 객체 인터페이스를 만들 때 유용합니다.
- 인터페이스 개요 페이지의 Extension 패널에서 Add extension, 대상 선택, Confirm, Save 순서로 추가합니다.
- 확장을 제거하면 상속받았던 속성과 제약이 모두 함께 제거됩니다.
