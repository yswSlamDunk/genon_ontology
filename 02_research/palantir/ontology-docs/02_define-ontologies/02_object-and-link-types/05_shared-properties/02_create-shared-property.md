# 공유 속성 만들기 (Create shared properties)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/create-shared-property/
- 사이드바 위치: Define Ontologies > Object and link types > Shared properties > Create shared properties

이 페이지는 Ontology Manager의 공유 속성 페이지에서 새 공유 속성(shared property)을 만드는 절차와, 만들 때 설정할 수 있는 메타데이터 항목을 설명합니다. 공유 속성은 일반 속성 메타데이터의 일부만 가지므로, 어떤 항목을 설정하는지 알아 두면 여러 객체 타입에 일관된 속성 정의를 적용할 수 있습니다.

Ontology Manager 애플리케이션의 공유 속성 페이지에서 새 공유 속성을 만들고 설정합니다.

페이지에 접근하려면 아래 단계를 따릅니다.

1. Ontology Manager에서 **Shared properties** 메뉴 옵션을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/shared-property-menu-option.png" alt="Ontology Manager의 공유 속성 페이지" width="800" />

2. 공유 속성 페이지에서 오른쪽 위의 **New shared property**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/new-shared-property-button.png" alt="공유 속성 생성 버튼" width="800" />

3. 공유 속성 생성 모달이 열리며, 여기서 이름, 설명, 타입 등의 메타데이터를 설정해 공유 속성을 만들 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-shared-property-modal.png" alt="공유 속성 생성 모달" width="500" />

공유 속성은 일반 속성 메타데이터 중 일부로 설정할 수 있습니다.

* **이름(Name):** 공유 속성의 이름입니다.
* **설명(Description):** 공유 속성에 대한 설명 텍스트입니다. 예를 들어 `start date` 공유 속성의 설명은 `The day the employee or contractor began working`(직원 또는 계약자가 근무를 시작한 날)일 수 있습니다.
* **기본 타입(Base type):** 이 속성의 값 타입을 나타내며, 사용자 애플리케이션에서 쓸 수 있는 연산의 집합을 결정합니다. 예를 들어 `start date` 속성의 기본 타입은 `date`입니다. 사용자 애플리케이션에서는 이 속성으로 타임라인 위젯을 구성할 수 있습니다. 기본 타입은 기반 열의 타입과 관련이 있으며, 객체 타입에 적용하려면 열 타입과 일치해야 합니다.
* **값 서식(Value formatting):** 속성의 기본 타입에 따라 숫자 서식, 날짜 및 시간 서식, 사용자 ID 서식, 리소스 ID 서식을 속성에 적용할 수 있으며, 원시 값을 사용자 애플리케이션에서 더 읽기 쉬운 형태로 바꿔 줍니다. [값 서식](../03_properties/03_value-formatting.md)에 대해 더 알아보세요.
* **타입 클래스(Type classes):** 사용자 애플리케이션이 해석하는 추가 메타데이터입니다. [타입 클래스](../09_metadata/01_metadata-typeclasses.md)에 대해 더 알아보세요.
* **렌더 힌트(Render hints):** 같은 기본 타입의 다른 속성 대부분과 다르게 이 속성을 어떻게 렌더링할지 사용자 애플리케이션에 알려 주는 표시입니다. 많은 렌더 힌트는 해당 속성이 정의된 객체 타입의 재인덱싱(reindex) 성능에 영향을 줄 수 있습니다. 예를 들어 사용자 애플리케이션에서 아무도 `start date` 속성으로 검색하거나 정렬하지 않을 것으로 예상된다면, `searchable`과 `sortable` 렌더 힌트를 해제해 `Employee` 객체 타입의 재인덱싱 성능을 높일 수 있습니다. [렌더 힌트](../09_metadata/02_metadata-render-hints.md)에 대해 더 알아보세요.
* **가시성(Visibility):** 사용자 애플리케이션이 이 속성을 얼마나 눈에 띄게 표시할지 알려 주는 표시입니다. `prominent` 속성은 애플리케이션이 사용자에게 이 속성을 가장 먼저 보여 주게 합니다. `hidden` 속성은 사용자 애플리케이션에 나타나지 않습니다. 기본적으로 `start date` 속성의 가시성은 `normal`입니다.

4. 공유 속성을 온톨로지에 영구 반영하려면 Ontology Manager 오른쪽 위의 **Save**를 선택합니다.

**설명**: 렌더 힌트와 재인덱싱의 관계를 조금 더 풀어 보면, 검색이나 정렬이 가능하려면 해당 속성 값에 대한 인덱스를 만들어 두어야 합니다. 데이터베이스에서 `CREATE INDEX`로 인덱스를 추가하면 그 열로 검색하거나 정렬하는 질의는 빨라지지만, 데이터를 다시 쓸 때마다 인덱스도 함께 갱신해야 하므로 쓰기 비용이 늘어납니다. 같은 이유로 `searchable`, `sortable`을 끄면 객체 타입 데이터를 다시 인덱싱할 때 할 일이 줄어듭니다.

## 정리

- 공유 속성은 Ontology Manager의 **Shared properties** 페이지에서 **New shared property**로 만듭니다.
- 설정 항목은 이름, 설명, 기본 타입, 값 서식, 타입 클래스, 렌더 힌트, 가시성입니다.
- 기본 타입은 객체 타입에 적용될 때 기반 열 타입과 일치해야 합니다.
- 검색, 정렬이 필요 없는 속성은 렌더 힌트를 꺼서 재인덱싱 성능을 높일 수 있습니다.
- 마지막에 **Save**를 눌러야 온톨로지에 반영됩니다.
