# 다중 데이터소스 객체 타입 (Multi-datasource object types, MDOs)

- 원문: https://www.palantir.com/docs/foundry/object-permissioning/multi-datasource-objects/
- 사이드바 위치: Ontology architecture > Object permissioning > Multi-datasource object types (MDOs)

이 페이지는 하나의 객체 타입을 여러 개의 데이터소스로 뒷받침하는 다중 데이터소스 객체 타입(MDO)을 설명합니다. 속성(property)마다 서로 다른 데이터셋에서 값을 가져오게 하면, 데이터셋 단위로 걸린 권한이 곧 속성 단위의 접근 제어가 됩니다. 그래서 이 기능은 객체 권한 설정(Object permissioning) 섹션에 속해 있으며, MDO의 종류, 설정 방법, 자주 묻는 질문을 다룹니다.

다중 데이터소스 객체 타입(MDO)은 온톨로지에서 여러 데이터소스를 백킹 데이터소스(backing datasource)로 가지는 객체 타입이며, Object Storage v2에서만 사용할 수 있습니다. 현재는 [Foundry 데이터셋](https://www.palantir.com/docs/foundry/data-integration/datasets/)이나 [제한된 뷰(restricted view)](https://www.palantir.com/docs/foundry/security/restricted-views/)만 MDO에 사용할 수 있습니다. 스트리밍 소스는 지원하지 않습니다.

<a id="types-of-multi-datasource-object-types"></a><a id="types-of-multi-datasource-object-types-mdos"></a>
## 다중 데이터소스 객체 타입(MDO)의 종류 (Types of multi-datasource object types)

MDO에는 서로 다른 두 가지 범주가 있습니다.

* **열 방향 MDO(Column-wise MDO):** 조인(join)과 비슷한 MDO입니다. 한 객체 타입의 속성들을 서로 겹치지 않는 부분 집합으로 나누어 각기 다른 데이터소스에서 가져와 통합합니다. 열 방향 MDO는 열 수준 접근 제어가 필요한 사용 사례를 지원하는 데 쓸 수 있습니다.
* **행 방향 MDO(Row-wise MDO):** 유니온(union)과 비슷한 MDO입니다. 같은 스키마를 공유하는 여러 데이터소스에서 완전한 객체(모든 속성을 갖춘 객체)를 통합합니다. 행 방향 MDO는 행 수준 접근 제어가 필요한 사용 사례를 지원하는 데 쓸 수 있습니다. Foundry에서는 행 방향 MDO를 쓸 법한 사용 사례를 [제한된 뷰](05_configuring-rv-access-controls.md)가 지원합니다. 행 방향 MDO 자체는 제공되지 않습니다.

**주의**: Foundry는 열 방향 MDO만 지원하며 행 방향 MDO는 지원하지 않습니다. 행 방향 MDO 사용 사례의 대부분은 [제한된 뷰](05_configuring-rv-access-controls.md)로 해결할 수 있습니다. 제한된 뷰로 해결할 수 **없는** 행 방향 MDO 사용 사례가 있다면 Palantir 담당자에게 지원을 요청하십시오.

**설명**: 두 방식을 SQL로 표현하면 차이가 분명해집니다. `Employee` 객체 타입의 기본 키(primary key)가 `employee_id`라고 합시다. `employee_basic`(employee_id, name, department) 데이터셋은 모든 직원이 볼 수 있고, `employee_salary`(employee_id, salary) 데이터셋은 인사팀만 볼 수 있다고 하면, 열 방향 MDO는 두 데이터셋을 `employee_id`로 조인한 결과(`employee_basic JOIN employee_salary USING (employee_id)`)를 하나의 객체 타입으로 보여 주는 것입니다. `salary` 속성은 `employee_salary` 데이터셋에서 오므로, 이 데이터셋의 권한이 없는 사용자에게는 이 열만 가려집니다. 반면 행 방향 MDO는 같은 열 구성을 가진 `employee_seoul`, `employee_busan` 데이터셋을 `UNION`으로 합치는 방식이며, 데이터셋마다 권한을 달리 두어 행 단위로 접근을 제어하려는 목적입니다. Foundry는 이 두 번째 방식 대신 제한된 뷰를 사용하도록 안내합니다.

> **중간 요약**: MDO는 여러 데이터소스로 하나의 객체 타입을 만드는 기능이며, 조인 형태의 열 방향 MDO만 지원합니다. 유니온 형태의 행 방향 요구는 제한된 뷰로 해결합니다.

<a id="configure-a-multi-datasource-object-type"></a>
## 다중 데이터소스 객체 타입 설정하기 (Configure a multi-datasource object type)

Ontology Manager에서 Object Storage v2를 사용하는 [객체 타입을 만든](../../02_define-ontologies/02_object-and-link-types/02_object-types/02_create-object-type.md#create-a-new-object-type-manually) 뒤, 왼쪽 사이드바에서 객체 타입의 **Datasource** 메타데이터 섹션으로 이동합니다. 그런 다음 **Add new backing datasource**(새 백킹 데이터소스 추가)를 선택해 데이터셋을 고릅니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-permissioning/multi-datasource-objects-add-new-datasource.png" alt="새 객체 타입" width="500" />

**Map primary key**(기본 키 매핑) 도우미가 나타나서, 객체 타입의 기본 키와 값이 일치하는 열을 선택하라고 안내합니다. 열을 선택하면 **Backing datasource** 섹션 아래에 여러 개의 백킹 데이터셋이 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-permissioning/multi-datasource-objects-backing-datasources.png" alt="새 객체 타입" width="500" />

왼쪽 사이드바에서 **Properties** 메타데이터 섹션으로 이동해, 새로 추가한 데이터셋의 필드를 새 속성으로 추가합니다.

**설명**: 기본 키 매핑 단계는 앞의 SQL 예에서 `USING (employee_id)`에 해당하는 조인 조건을 정하는 단계입니다. 새로 추가한 데이터셋의 어느 열이 객체의 기본 키와 같은 값을 담고 있는지 알려 주어야 두 데이터셋의 행을 같은 객체로 묶을 수 있습니다.

> **중간 요약**: Datasource 섹션에서 데이터셋을 추가하고, 기본 키에 대응하는 열을 지정한 뒤, Properties 섹션에서 그 데이터셋의 열을 속성으로 추가하면 MDO가 됩니다.

<a id="faq"></a>
## 자주 묻는 질문 (FAQ)

<a id="are-multi-datasource-object-types-available-for-an-object-type-indexed-into-object-storage-v1-phonograph"></a>
### Object Storage v1(Phonograph)에 인덱싱된 객체 타입에서도 다중 데이터소스 객체 타입을 쓸 수 있나요?

아니요. MDO는 Object Storage v2에서만 지원되며 Object Storage v1(Phonograph)에서는 사용할 수 없습니다.

<a id="are-both-column-wise-mdo-and-row-wise-mdo-supported"></a>
### 열 방향 MDO와 행 방향 MDO를 모두 지원하나요?

현재는 열 방향 MDO만 사용할 수 있습니다. 제한된 뷰로 해결할 수 없는 행 방향 MDO 사용 사례가 있다면 Palantir 담당자에게 지원을 요청하십시오.

<a id="are-user-edits-and-materializations-supported-for-mdo"></a>
### MDO에서도 사용자 편집과 머티리얼라이제이션을 지원하나요?

예. MDO에서도 [사용자 편집(user edits)](../04_object-edits-and-materializations/01_overview.md)과 [머티리얼라이제이션(materialization)](../04_object-edits-and-materializations/06_materializations.md)을 지원합니다.

<a id="what-happens-if-a-user-cannot-view-some-of-the-input-datasources-for-a-given-object-type-what-will-the-user-experience-be-like"></a>
### 사용자가 어떤 객체 타입의 입력 데이터소스 중 일부를 볼 수 없으면 어떻게 되나요? 사용자에게는 어떻게 보이나요?

사용자가 일부 입력 데이터소스에 대해 `Viewer` 권한이 없으면, 객체를 표시할 때 그 데이터소스에서 매핑된 속성들은 `null`로 나타납니다. 다만 객체 타입에 대한 접근은 입력 데이터소스와 별도로 제어되므로, 사용자는 그 객체 타입의 스키마(예: 속성 이름)는 계속 볼 수 있습니다.

[객체 타입 권한에 대해 더 알아보기.](02_ontology-permissions.md)

**설명**: 앞의 예에서 인사팀이 아닌 사용자가 직원 E001을 열면 `name`과 `department`는 정상적으로 보이고 `salary`는 `null`로 표시됩니다. 그래도 이 사용자는 `Employee` 객체 타입에 `salary`라는 속성이 있다는 사실(스키마) 자체는 알 수 있습니다. 즉 MDO가 숨기는 것은 값이지 속성의 존재가 아닙니다.

<a id="is-property-multiplicity-supported"></a>
### 속성 다중성(property multiplicity)을 지원하나요?

속성 다중성이란 열 방향 MDO에서 여러 입력 데이터소스가 객체 타입의 같은 열(속성)을 겹쳐서 공급하는 경우를 말합니다. 속성 다중성은 현재 지원되지 않습니다. 즉 객체 타입의 특정 속성은 반드시 입력 데이터소스 중 오직 하나에서만 와야 합니다(단, 기본 키 속성은 예외로, 모든 데이터소스를 조인하려면 모든 입력 데이터소스에 기본 키가 있어야 합니다).

<a id="can-a-property-corresponding-to-a-restricted-view-policy-be-mapped-to-multiple-restricted-view-datasources-if-they-share-the-same-policy"></a>
### 제한된 뷰 정책에 해당하는 속성 하나를, 같은 정책을 공유하는 여러 제한된 뷰 데이터소스에 매핑할 수 있나요?

아니요, 지원되지 않습니다. 제한된 뷰 데이터소스마다 객체 타입에 별도의 정책 속성을 두어야 합니다. 프런트엔드 애플리케이션이 지저분해지지 않도록, 이 속성들 중 일부를 [Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md#property-editor-view)에서 숨김(hidden)으로 표시할 수 있습니다.

<a id="what-is-the-difference-between-mdos-and-linking-two-distinct-object-types-with-a-foreign-key-relation-how-should-users-decide-between-these-options"></a>
### MDO와, 서로 다른 두 객체 타입을 외래 키 관계로 링크하는 것은 무엇이 다른가요? 둘 중 무엇을 고를지 어떻게 정하나요?

MDO는 조직의 디지털 트윈을 구축할 때 같은 구성을 단일 객체 타입으로 설정할 수 있게 해 주는 사용하기 쉬운 방법을 제공하려는 것입니다. 사용자가 데이터를 실제로 그렇게 이해하고 다룬다면 링크로 연결된 여러 객체 타입을 사용할 수도 있습니다. 다만 여러 객체 타입 사이의 링크를 질의하고 순회하는 작업은 같은 객체 타입의 속성으로 필터링하는 것보다 비용이 큰 연산입니다.

**설명**: 판단 기준은 "같은 대상에 대한 정보인가, 다른 대상인가"입니다. 직원의 급여는 직원 자체의 속성이므로 MDO로 같은 `Employee` 객체에 붙이는 편이 자연스럽고, "급여가 5000 이상인 직원" 같은 필터도 한 객체 타입 안에서 끝납니다. 반면 직원과 부서는 서로 다른 대상이므로 `Employee`와 `Department`를 별도 객체 타입으로 두고 링크 타입으로 연결합니다. 이 경우 "영업 부서 소속 직원"을 찾으려면 링크를 따라가는 탐색이 필요하므로 단일 속성 필터보다 비용이 큽니다.

<a id="which-objects-appear-if-two-column-wise-datasources-for-an-object-have-different-sets-of-primary-keys"></a>
### 한 객체의 두 열 방향 데이터소스가 서로 다른 기본 키 집합을 가지면 어떤 객체가 나타나나요?

한 객체의 두 열 방향 데이터소스가 서로 다른 기본 키 집합을 가지면, 일부 사용자가 일부 입력 데이터소스에 접근하지 못하는 경우와 비슷하게 동작합니다. 이 경우 어떤 데이터소스에 존재하지 않는 기본 키에 대해서는, 그 입력 데이터소스에서 매핑된 속성들이 `null`로 표시됩니다.

**설명**: `employee_basic`에 E001, E002, E003이 있고 `employee_salary`에는 E001, E002만 있다면, E003 객체는 나타나되 `salary`가 `null`입니다. SQL로는 기본 키 기준 외부 조인(outer join)을 한 결과와 비슷한 모양입니다.

<a id="is-there-a-limit-to-the-number-of-datasources-an-object-type-can-have"></a>
### 객체 타입이 가질 수 있는 데이터소스 수에 제한이 있나요?

객체 타입은 최대 70개의 데이터소스를 가질 수 있습니다. 객체 스토리지(object storage)에 동기화되는 데이터소스만 이 한도에 포함되므로, 미디어 세트(media set)나 시계열(time series) 동기화는 포함되지 않습니다.

<a id="can-i-use-mdos-with-streaming-object-types"></a>
### 스트리밍 객체 타입에서 MDO를 사용할 수 있나요?

아니요. 스트리밍 객체 타입에서는 MDO를 지원하지 않습니다. 이는 Object Storage v2의 알려진 제약 사항입니다.

> **중간 요약**: MDO는 OSv2 전용이고, 권한이 없는 데이터소스의 속성은 `null`로 보이며, 속성 하나는 하나의 데이터소스에서만 와야 합니다. 데이터소스는 최대 70개이고 스트리밍 객체 타입에는 쓸 수 없습니다.

## 정리

- MDO는 여러 데이터셋(또는 제한된 뷰)을 기본 키로 묶어 하나의 객체 타입을 만드는 기능이며 Object Storage v2에서만 동작합니다.
- 지원되는 것은 조인 형태의 열 방향 MDO뿐이며, 유니온 형태의 행 단위 접근 제어는 제한된 뷰로 해결합니다.
- 데이터소스별 권한이 속성별 가시성이 되어, 권한이 없는 사용자에게는 해당 속성 값이 `null`로 보입니다.
- 각 속성은 정확히 하나의 데이터소스에서 와야 하며(기본 키 제외), 데이터소스는 최대 70개입니다.
- 같은 대상의 정보는 MDO로, 다른 대상은 링크 타입으로 연결하는 것이 기본 판단 기준이며, 링크 순회는 속성 필터보다 비용이 큽니다.
