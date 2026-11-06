# 인터페이스 만들기 (Create an interface)

- 원문: https://www.palantir.com/docs/foundry/interfaces/create-interface/
- 사이드바 위치: Define Ontologies > Interfaces > Create an interface

이 페이지는 Ontology Manager에서 새 인터페이스(interface)를 만드는 절차를 단계별로 설명합니다. 이름과 속성(property)을 정하는 기본 단계에 더해, 선택 사항으로 인터페이스 링크 타입 제약 조건과 액션 타입 제약 조건을 추가하는 방법도 다룹니다.

아래 단계에 따라 [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)에서 새 인터페이스를 만드세요.

1. 먼저 왼쪽 사이드 패널 맨 위에 있는 **Ontologies** 드롭다운 메뉴를 확인해, 원하는 온톨로지에서 작업하고 있는지 확인합니다.

2. 새 인터페이스를 만들려면 다음 중 하나를 선택합니다.
   * 페이지 오른쪽 위에서 **New > Interface**를 선택합니다.
   * 왼쪽 패널의 **Resources** 섹션에서 **Interfaces > + New interface**를 선택합니다. 그런 다음 **Interfaces** 페이지에서 화면 오른쪽 위의 **New interface**를 선택합니다.

3. 도우미(helper)의 첫 페이지에는 인터페이스에 대한 안내가 있습니다. **Next**를 선택합니다. <img src="https://www.palantir.com/docs/resources/foundry/interfaces/create-interface-about.png" alt="인터페이스 생성 안내 페이지." width="800" />

4. 인터페이스의 표시 이름(display name)과 API 이름을 입력합니다. 선택적으로 인터페이스 설명을 입력하고 적절한 아이콘을 고를 수도 있습니다.

    <img src="https://www.palantir.com/docs/resources/foundry/interfaces/create-interface-metadata.png" alt="인터페이스 메타데이터 입력" width="800" />

5. 인터페이스에 속성을 추가합니다. 속성은 인터페이스에 로컬로 정의하거나(권장) [공유 속성(shared property)](../02_object-and-link-types/05_shared-properties/01_shared-property-overview.md)을 사용할 수 있습니다. 각 속성마다 **required**(필수)인지 **optional**(선택)인지 정합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/interfaces/create-interface-choose-properties.png" alt="인터페이스 속성 선택" width="800" />

   **required** 속성의 경우, 인터페이스를 구현하는 모든 객체 타입은 자신의 로컬 속성에서 인터페이스 속성으로의 매핑을 제공해야 합니다. **optional** 속성은 구현할 때 매핑을 건너뛸 수 있습니다. 선택 속성은 Marketplace 패키지를 만들 때 유용한데, 해결하기 어려운 업그레이드 차단 요인(upgrade blocker)을 만들지 않고 인터페이스를 반복 개선할 수 있기 때문입니다.

6. 이 인터페이스를 저장할 프로젝트(project)를 선택한 다음 **Create**를 선택합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/interfaces/create-interface-save-location.png" alt="인터페이스 저장 위치." width="800" />

7. Ontology Manager로 돌아와 오른쪽 위의 **Save**를 선택해 [온톨로지에 변경 사항을 반영](../../05_applications/04_ontology-manager/06_change-management/01_save-changes.md)합니다.

**설명**: 표시 이름은 화면에 보이는 사람용 이름이고, API 이름은 코드(예: OSDK, 함수)에서 인터페이스를 가리킬 때 쓰는 식별자입니다. 필수 속성과 선택 속성의 차이가 중요한 이유는 다음과 같습니다. 인터페이스에 필수 속성을 새로 추가하면 이미 그 인터페이스를 구현한 모든 객체 타입이 새 매핑을 제공해야 하므로, 다른 조직에 설치된 Marketplace 패키지를 업그레이드할 때 막힐 수 있습니다. 선택 속성으로 추가하면 기존 구현은 그대로 유효합니다.

> **중간 요약**: **New > Interface**로 도우미를 열고, 표시 이름과 API 이름, 속성(필수 또는 선택)을 정한 뒤 프로젝트에 저장하고 Ontology Manager에서 **Save**합니다.

<a id="create-interface-link-types-optional"></a>
## 인터페이스 링크 타입 만들기(선택) (Create interface link types (optional))

이 인터페이스가 다른 인터페이스나 객체 타입에 링크되게 하려면, 선택적으로 [인터페이스 링크 타입](06_interface-link-types-overview.md)을 인터페이스에 추가할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/create-link-type-constraint.png" alt="링크 타입 제약 조건 추가" width="800" />

1. 왼쪽 사이드 패널에서 **Link type constraints**를 선택합니다.
2. 그런 다음 오른쪽 위의 **Create new link type constraint**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/create-link-type-constraint-modal.png" alt="링크 타입 제약 조건 만들기" width="400" />

모델링 사용 사례에서 인터페이스 링크 타입이 필수라면, 인터페이스를 구현하는 모든 객체 타입은 인터페이스 링크 타입 제약 조건을 만족하는 새 링크 타입이나 기존 링크 타입을 추가해야 합니다.

<a id="create-interface-action-type-constraints-optional"></a>
## 인터페이스 액션 타입 제약 조건 만들기(선택) (Create interface action type constraints (optional))

인터페이스가 구현 객체 타입 전반에서 기대되는 액션 기능을 정의하게 하려면, 선택적으로 [인터페이스 액션 타입 제약 조건](07_interface-action-type-constraints.md)을 인터페이스에 추가할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/iatc-config-page.png" alt="인터페이스 액션 타입 제약 조건 탭." width="800" />

1. 왼쪽 사이드 패널에서 **Action type constraints**를 선택합니다.
2. **Create new**를 선택합니다.
3. 제약 조건의 메타데이터를 추가하고, 구현이 필수인지 정하고, 파라미터 제약 조건을 구성합니다.

<img src="https://www.palantir.com/docs/resources/foundry/interfaces/iatc-config-dialog-set.png" alt="액션 타입 제약 조건 구성 대화 상자." width="500" />

모델링 사용 사례에서 인터페이스 액션 타입 제약 조건이 필수라면, 인터페이스를 구현하는 모든 객체 타입은 그 제약 조건을 만족하는 구체적인 액션 타입에 제약 조건을 매핑해야 합니다.

**설명**: 제약 조건(constraint)은 "구현하는 쪽이 반드시 갖춰야 하는 것"을 인터페이스가 선언하는 방식입니다. 예를 들어 `Facility` 인터페이스에 "Employee와 연결되는 링크가 있어야 한다"는 링크 타입 제약 조건과 "상태를 바꾸는 액션이 있어야 한다"는 액션 타입 제약 조건을 필수로 두면, `Airport` 객체 타입이 `Facility`를 구현할 때 실제 링크 타입과 액션 타입을 하나씩 지정해야 합니다.

> **중간 요약**: 선택적으로 링크 타입 제약 조건과 액션 타입 제약 조건을 추가할 수 있으며, 필수로 지정하면 구현 객체 타입이 이를 만족하는 실제 링크 타입이나 액션 타입을 연결해야 합니다.

## 정리

- 인터페이스는 Ontology Manager에서 **New > Interface** 또는 **Interfaces > + New interface**로 만듭니다.
- 표시 이름, API 이름, 설명, 아이콘을 정하고 속성을 추가하며, 각 속성을 필수나 선택으로 지정합니다.
- 선택 속성은 Marketplace 패키지에서 업그레이드 차단 없이 인터페이스를 개선하는 데 유용합니다.
- 필요하면 링크 타입 제약 조건과 액션 타입 제약 조건을 추가하며, 마지막에 **Save**로 온톨로지에 반영합니다.
