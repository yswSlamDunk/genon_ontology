# 링크 타입 메타데이터 참조 (Metadata reference)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/link-type-metadata/
- 사이드바 위치: Define Ontologies > Object and link types > Link types > Metadata reference

이 페이지는 링크 타입 하나를 정의하는 메타데이터 항목(ID, RID, 상태, 객체 타입, 카디널리티, 키, 표시 이름, API 이름, 가시성, 타입 클래스)을 하나씩 설명하는 참조 문서입니다. 링크 타입을 만들거나 편집할 때 각 입력란이 무엇을 뜻하는지 확인하는 용도로 씁니다. 예시는 `Employee`와 `Company` 객체 타입을 잇는 `Employee → Employer` 링크 타입을 중심으로 듭니다.

링크 타입은 Foundry 온톨로지(Ontology)에서 다음 메타데이터로 표현됩니다.

* **ID:** 링크 타입의 고유 식별자로, 주로 애플리케이션을 구성할 때 이 타입의 링크를 참조하는 데 쓰입니다. 예를 들어 `Employee`와 `Company` 객체 타입 사이에 정의된 링크 타입의 ID는 `employee-employer`일 수 있습니다.
* **RID:** Foundry의 모든 리소스마다 자동으로 생성되는 고유 식별자입니다. 플랫폼 전반의 오류 메시지에서 링크 타입의 RID가 참조됩니다.
* **Status(상태):** 링크 타입이 개발 과정의 어느 단계에 있는지를 사용자와 다른 온톨로지 빌더에게 알려 주는 신호입니다. `active`, `experimental`, `deprecated` 중 하나일 수 있습니다. 기본적으로 `Employee → Employer` 링크 타입의 상태는 `experimental`입니다. [상태](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.
* **Object types(객체 타입):** 링크 타입 정의로 서로 연결되는 객체 타입입니다. 예를 들어 `Employee → Employer` 링크 타입은 `Employee`와 `Company` 객체 타입을 가리킵니다.
* **Cardinality(카디널리티):** 링크 타입의 각 객체 타입 쪽에 객체가 하나인지 여러 개인지를 애플리케이션에 알려 줍니다. 예를 들어 `Employee → Employer` 링크 타입에서 Employee 객체 타입의 카디널리티는 `many`이고 Company 객체 타입의 카디널리티는 `one`입니다. 여러 직원이 하나의 고용주에 링크되기 때문입니다. `Direct Report ↔ Manager` 링크 타입에서는, 부하 직원 한 명이 여러 관리자를 가질 수 있고 관리자 한 명이 여러 부하 직원을 가질 수 있다면 양쪽 Employee 객체 타입의 카디널리티가 모두 `many`가 됩니다.
* **Key(키):** 링크를 만드는 데 쓰이는 속성(property) 또는 열입니다.
  * 일대일 또는 일대다 카디널리티 링크 타입에서는, 한 객체 타입의 속성(외래 키)이 다른 객체 타입의 기본 키(primary key) 속성을 참조합니다. 이 외래 키와 기본 키 사이의 참조가 객체 간 링크를 정의합니다. 예를 들어 `Employee → Employer` 링크 타입에서 `Employee` 객체 타입은 `Company` 객체 타입의 `company ID` 속성(기본 키)을 참조하는 `employer ID` 속성(외래 키)을 가질 수 있습니다.
  * 다대다 카디널리티 링크 타입에서는, 기본 키 쌍을 담은 테이블이 두 객체 사이의 링크를 정의합니다. 이런 링크 타입은 조인 테이블을 지정해야 하고, 조인 테이블의 어떤 열이 링크 타입의 어떤 객체 타입 기본 키를 가리키는지 애플리케이션에 알려 주는 키 매핑도 지정해야 합니다. 예를 들어 `Direct Report ↔ Manager` 링크 타입을 뒷받침하는 조인 테이블은 `employee numbers` 쌍을 담을 수 있으며, 각 쌍이 `Direct Report ↔ Manager` 링크 하나를 나타냅니다.
* **Display name(표시 이름):** 사용자 애플리케이션에서 이 타입의 링크에 접근하는 사람에게 보이는 이름입니다. 링크 타입의 각 쪽(side)마다 표시 이름이 있습니다. 링크 타입의 한 쪽은 그 객체 타입*으로 가는* 링크를 나타냅니다. 예를 들어 `Employee → Employer` 링크 타입에서 `Employee` 객체 타입 쪽의 표시 이름은 `Employee`이고 `Company` 객체 타입 쪽의 표시 이름은 `Employer`입니다.
* **Plural display name(복수형 표시 이름):** 사용자 애플리케이션에서 링크된 객체가 여러 개인 경우 이 타입의 링크에 접근하는 사람에게 보이는 이름입니다. 예를 들어 `Employee → Employer` 링크 타입에서 `Employee` 객체 타입 쪽의 복수형 표시 이름은 `Employees`이고, `Company` 객체 타입 쪽에는 복수형 표시 이름이 없습니다. 직원 한 명당 회사는 하나뿐이기 때문입니다.
* **API name(API 이름):** 코드에서 프로그래밍 방식으로 링크 타입을 가리킬 때 쓰는 이름입니다. 링크 타입 한 쪽의 API 이름을 사용해 그 타입의 객체를 반환받을 수 있습니다. 예를 들어 `Employee → Employer` 링크 타입의 Employee 쪽 API 이름이 `employee`라면, `Company.employee.get()`을 호출하면 해당 `Company` 객체에 링크된 `Employee` 객체가 반환됩니다. [API 이름(TSv1)](../../04_functions/13_functions-on-objects/06_api-objects-links.md)에 대해 더 읽어 보세요.
* **Visibility(가시성):** 링크 타입의 한 쪽(그 쪽 객체 타입*으로 가는* 링크)을 사용자 애플리케이션이 얼마나 눈에 띄게 표시할지 알려 주는 표시입니다. `prominent`인 쪽은 애플리케이션이 사용자에게 먼저 보여 주게 합니다. `hidden`인 쪽은 사용자 애플리케이션에 나타나지 않습니다. 기본적으로 Employee 쪽과 Company 쪽의 가시성은 `normal`입니다.
* **Type classes(타입 클래스):** 사용자 애플리케이션이 해석하는 추가 메타데이터입니다. [타입 클래스](../09_metadata/01_metadata-typeclasses.md)에 대해 더 읽어 보세요.

[온톨로지에서 링크 타입을 만들고 구성하는 방법과 링크 타입 메타데이터의 유효성 검사 요구 사항에 대해 더 알아보세요.](02_create-link-type.md)

[속성(객체 타입의 특성)에 대해 더 알아보세요.](../03_properties/01_properties-overview.md)

**설명**: 키 항목을 테이블로 보면 이해가 쉽습니다. 일대다의 경우 다음과 같습니다.

| Employee.employee_id | Employee.name | Employee.employer_id |
|---|---|---|
| E1 | Kim | C1 |
| E2 | Lee | C1 |
| E3 | Park | C2 |

`employer_id`가 Company의 기본 키 `company_id`를 가리키므로, C1 회사에는 E1과 E2가 링크됩니다. 다대다(부하 직원과 관리자)의 경우에는 `(direct_report_id, manager_id)` 쌍을 행으로 가진 별도 조인 테이블이 필요합니다. 한 쪽 열에 값을 하나만 넣을 수 없기 때문입니다.

**설명**: "쪽(side)"마다 이름이 따로 있는 이유는 링크를 어느 방향에서 따라가느냐에 따라 부르는 이름이 다르기 때문입니다. Employee 객체에서 링크를 따라가면 Company 객체가 나오는데, 이 링크는 Company 쪽의 표시 이름인 "Employer"로 보입니다. Company 객체에서 따라가면 여러 Employee 객체가 나오고, 이 링크는 Employee 쪽의 이름 "Employee"(여러 개이므로 복수형 "Employees")로 보입니다. 코드에서도 `Company.employee`처럼 반대편 쪽의 API 이름으로 링크된 객체를 가져옵니다.

## 정리

- 링크 타입은 ID, RID, 상태, 연결하는 두 객체 타입, 카디널리티, 키, 쪽별 표시 이름과 복수형 표시 이름, 쪽별 API 이름, 쪽별 가시성, 타입 클래스로 정의됩니다.
- 일대일과 일대다 링크는 외래 키 속성이 기본 키 속성을 참조하는 방식으로, 다대다 링크는 기본 키 쌍을 담은 조인 테이블로 정의됩니다.
- 표시 이름, API 이름, 가시성은 링크 타입의 각 쪽마다 따로 설정하며, 한 쪽은 그 객체 타입으로 가는 링크를 뜻합니다.
- 새 링크 타입의 기본 상태는 `experimental`, 기본 가시성은 `normal`입니다.
