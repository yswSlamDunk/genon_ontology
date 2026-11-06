# 파생 속성 구성하기 (Derived properties)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/derived-properties/
- 사이드바 위치: Define Ontologies > Object and link types > Properties > Derived properties

이 페이지는 Ontology Manager에서 객체 타입(object type)에 온톨로지 정의 파생 속성(derived property)을 구성하는 절차를 설명합니다. 파생 속성은 값을 직접 저장하지 않고, 링크로 연결된 다른 객체의 값을 실행 시점에 가져오거나 집계해서 보여 주는 속성입니다. 링크 타입 선택, 집계 방식 선택, 수집 개수 제한, 최대 세 단계까지의 다단계 링크 탐색 방법을 다룹니다.

**참고**: 베타(Beta). 온톨로지 정의 파생 속성은 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며 사용자의 환경(enrollment)에서는 사용할 수 없을 수도 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다.

파생 속성은 링크된 객체의 값을 바탕으로 실행 시점(runtime)에 계산됩니다. 파생 속성은 데이터를 직접 저장하는 대신 링크 타입으로 연결된 객체에서 정보를 가져오며, 선택적으로 평균 내기, 개수 세기, 값을 목록으로 모으기 같은 집계(aggregation)를 적용합니다.

이 페이지는 Ontology Manager에서 객체 타입에 온톨로지 정의 파생 속성을 구성하는 방법을 설명합니다. 파생 속성이 무엇인지, 보안을 어떻게 상속하는지, 성능 고려 사항은 무엇인지는 [파생 속성 개요 문서](../../../03_ontology-search/03_derived-properties.md)를 참고하세요. 사용 가능한 집계의 전체 목록은 [파생 속성 참조 문서](../../../03_ontology-search/04_derived-properties-reference.md)를 참고하세요.

**설명**: 파생 속성은 데이터베이스의 뷰(view)에서 조인과 집계로 계산하는 열에 해당합니다. 예를 들어 `Department` 객체 타입에 "소속 직원 수"를 저장해 두는 대신, 다음 SQL처럼 질의할 때마다 계산해서 보여 주는 것입니다.

```sql
SELECT d.*, COUNT(e.employee_id) AS employee_count
FROM department d
LEFT JOIN employee e ON e.department_id = d.department_id
GROUP BY d.department_id;
```

값을 저장하지 않으므로 직원이 추가되거나 빠지면 다음 조회 때 자동으로 바뀐 값이 나옵니다.

<a id="configure-a-derived-property"></a>
## 파생 속성 구성하기 (Configure a derived property)

객체 타입에 파생 속성을 구성하려면 아래 단계를 따릅니다.

<a id="1-open-the-property-configuration-panel"></a><a id="open-the-property-configuration-panel"></a>
### 1. 속성 구성 패널 열기 (Open the property configuration panel)

객체 타입의 **Properties** 탭에서 **New property**를 선택하거나, 기존 속성을 선택해 편집합니다. 그러면 속성 구성 사이드 패널이 열립니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/configure-derived-property-source-tab.png" alt="파생 속성 옵션이 있는 속성 Source 탭." width="400" />

<a id="2-navigate-to-the-source-tab"></a><a id="navigate-to-the-source-tab"></a>
### 2. Source 탭으로 이동하기 (Navigate to the Source tab)

속성 구성 사이드 패널에서 **Source** 탭을 선택해 속성이 값을 어디서 가져올지 구성합니다.

<a id="3-select-the-linked-objects-source-type"></a><a id="select-the-linked-objects-source-type"></a>
### 3. Linked objects 소스 타입 선택하기 (Select the Linked objects source type)

**Source type** 영역에서 **Linked objects** 옵션을 선택합니다. 그러면 파생 속성 구성이 활성화됩니다.

<a id="4-select-a-link-type"></a><a id="select-a-link-type"></a>
### 4. 링크 타입 선택하기 (Select a link type)

**Linked objects** 영역의 드롭다운 메뉴에서 링크 타입을 선택합니다. 이 선택이 속성이 어떤 객체에서 값을 파생할지를 결정합니다.

* 드롭다운 메뉴에는 현재 객체 타입에서 사용할 수 있는 모든 링크 타입이 표시됩니다.
* 링크 타입을 선택한 뒤에는, 선택적으로 링크 타입을 더 추가해 여러 단계의 연결을 탐색할 수 있습니다(최대 세 단계).
* **Add linked object**를 선택하면 링크된 객체를 한 단계 더 탐색합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/configure-derived-property-link-selection.png" alt="파생 속성의 링크 타입 선택." width="400" />

<a id="5-configure-an-aggregation"></a><a id="configure-an-aggregation"></a>
### 5. 집계 구성하기 (Configure an aggregation)

링크 체인 중 어느 링크라도 둘 이상의 객체에 닿을 수 있다면, 값을 결합할 **Aggregation**(집계)을 반드시 선택해야 합니다.

* **Count:** 링크된 객체의 개수를 셉니다.
* **Average:** 숫자 값의 평균을 계산합니다.
* **Sum:** 숫자 값의 합을 계산합니다.
* **Minimum:** 최솟값을 선택합니다.
* **Maximum:** 최댓값을 선택합니다.
* **Approximate cardinality:** 고유 값의 개수를 추정합니다.
* **Exact cardinality:** 고유 값의 정확한 개수를 셉니다.
* **Collect list:** 중복을 유지한 채 값을 목록으로 모읍니다.
* **Collect set:** 고유한 값을 집합으로 모읍니다.

체인의 모든 링크가 최대 한 객체에만 닿는다면 집계는 선택 사항이며, 속성을 직접 선택할 수 있습니다.

[집계가 받아들이는 소스 속성 타입에 대해 더 알아보세요.](../../../03_ontology-search/04_derived-properties-reference.md#aggregations)

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/configure-derived-property-aggregation.png" alt="파생 속성의 집계 타입 선택." width="400" />

**설명**: 집계가 필요한지는 링크의 카디널리티(cardinality)에 달려 있습니다. `Employee`에서 `Department`로 가는 링크처럼 다대일(many-to-one)이면 직원 한 명에게 부서가 하나뿐이므로 `department.name`을 그대로 가져오면 됩니다. 반대로 `Department`에서 `Employee`로 가는 일대다(one-to-many) 링크에서는 부서 하나에 직원이 여러 명이므로, SQL에서 `GROUP BY` 없이 여러 행을 한 칸에 넣을 수 없듯이 `COUNT`, `AVG`, 목록 수집 같은 집계 함수가 필요합니다. "Approximate cardinality"는 HyperLogLog 같은 근사 알고리즘으로 고유 값 개수를 빠르게 추정하는 방식이고, "Exact cardinality"는 SQL의 `COUNT(DISTINCT ...)`처럼 정확히 세는 방식입니다(Foundry가 내부적으로 어떤 알고리즘을 쓰는지는 원문에 나와 있지 않습니다).

<a id="6-select-the-property-to-derive"></a><a id="select-the-property-to-derive"></a>
### 6. 파생할 속성 선택하기 (Select the property to derive)

링크 타입과 (필요하다면) 집계를 선택한 뒤, 링크된 객체 타입의 어떤 속성을 파생할지 고릅니다.

* 드롭다운 메뉴에는 링크 체인의 마지막 객체 타입에서 사용할 수 있는 모든 속성이 표시됩니다.
* **Count** 집계에서는 속성을 선택할 필요가 없습니다. 객체 개수가 자동으로 세어집니다.

<a id="7-configure-a-collection-limit"></a><a id="configure-a-collection-limit"></a>
### 7. 수집 개수 제한 구성하기 (Configure a collection limit)

**Collect list**나 **Collect set**을 선택했다면, 선택적으로 수집 개수 제한(collection limit)을 설정할 수 있습니다. 제한의 기본값은 `10`이며 최대 `100`까지 올릴 수 있습니다.

**Collect set**에서는 제한이 적용되기 전에 중복이 제거됩니다. 즉 제한은 고려 대상 값의 총개수가 아니라 반환되는 *서로 다른* 값의 개수를 제어합니다.

**주의**: 수집 개수 제한은 평가되는 값의 개수가 아니라 반환되는 속성 값의 개수를 결정합니다. 수집된 속성에 대한 필터와 정렬은 값 *전체*를 대상으로 실행되므로, 반환된 목록에 없는 값으로도 객체가 필터에 일치할 수 있습니다. 수집된 속성으로 필터링하기 전에 [수집 개수 제한](../../../03_ontology-search/03_derived-properties.md#collection-limits)에 대해 더 알아보세요.

수집된 값은 대표 값 하나로 리듀스할 수 있습니다. 자세한 내용은 [속성 리듀서](10_property-reducers.md)를 참고하세요.

**설명**: 예를 들어 부서에 직원이 15명 있고 "직원 이름 Collect list"를 기본 제한 10으로 구성하면, 화면에는 이름 10개만 반환됩니다. 그런데 "직원 이름에 'Diego'가 포함된 부서"로 필터링하면, Diego가 반환된 10명 안에 없고 나머지 5명 안에 있더라도 이 부서는 필터에 일치합니다. 필터는 15명 전체를 보고 판단하기 때문입니다.

> **중간 요약**: 파생 속성은 **Source** 탭에서 **Linked objects**를 고른 뒤, 링크 타입, (다수 객체에 닿으면 필수인) 집계, 파생할 속성, (목록과 집합 수집 시) 수집 개수 제한을 차례로 지정해 구성합니다. 수집 제한은 반환 개수만 줄일 뿐 필터와 정렬은 전체 값으로 동작합니다.

<a id="multi-hop-derived-properties"></a>
## 다단계 파생 속성 (Multi-hop derived properties)

파생 속성은 링크된 객체를 최대 **세 단계**까지 탐색할 수 있으므로, 시작 객체 타입과 간접적으로 연결된 객체에서도 속성을 파생할 수 있습니다.

예를 들어 `Department` 객체 타입은 `Employee` 객체를 거쳐 그 직원에게 링크된 `Project` 객체까지 탐색해 프로젝트 이름을 파생할 수 있습니다. 이때 링크 체인은 `Department`에서 `Employee`를 거쳐 `Project`로 이어집니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/configure-multi-hop-link.png" alt="다단계 파생 속성 구성." width="400" />

다단계 파생 속성을 구성하려면 다음을 따릅니다.

1. 첫 번째 링크 타입을 선택합니다.
2. **Add linked object**를 선택해 단계를 하나 더 추가합니다.
3. 새로 연결된 객체 타입에서 다음 링크 타입을 선택합니다.
4. 총 세 단계까지 반복합니다.

탐색 단계가 하나 늘어날 때마다 질의 성능이 떨어질 수 있습니다. 필요한 데이터에 닿는 가장 적은 단계를 사용하세요.

다른 파생 속성에서 값을 파생해야 한다면, 대신 원본 데이터까지 직접 탐색하는 다단계 파생 속성을 만드세요. 파생 속성은 다른 파생 속성에서 값을 가져올 수 없습니다.

**설명**: 다단계 탐색은 SQL에서 조인을 여러 번 하는 것과 같습니다. 위 예시는 `department JOIN employee ON ... JOIN employee_project ON ... JOIN project ON ...`처럼 조인이 이어지는 구조이고, 조인이 늘어날수록 처리할 행이 많아져 느려집니다. 파생 속성끼리 연쇄할 수 없으므로, 예를 들어 `Employee`에 "참여 프로젝트 수"라는 파생 속성이 있어도 `Department`에서 그것을 다시 합산할 수는 없고, `Department`에서 `Project`까지 직접 탐색하도록 구성해야 합니다.

<a id="identify-a-derived-property"></a>
## 파생 속성 식별하기 (Identify a derived property)

파생 속성은 **Properties** 탭에서 일반(native) 속성과 함께 나타나며, 값이 저장된 것이 아니라 계산된다는 것을 보여 주는 표시가 붙어 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/recognizing-a-derived-property.png" alt="객체 타입의 Properties 탭. 파생 속성에는 일반 속성과 구분되는 표시가 붙어 있습니다." width="400" />

<a id="limitations"></a>
## 제약 사항 (Limitations)

파생 속성에는 플랫폼 전반에 적용되는 기능상 제약이 있으며, 여기에는 기본 키(primary key), 필수 속성(required property), 값 타입(value type), 표시 서식, 그리고 [OSv1](../../../06_ontology-architecture/01_overview-and-getting-started/03_osv1-osv2-migration.md)으로 인덱싱되는 객체 타입에 대한 제약이 포함됩니다. 전체 목록은 [파생 속성 제약 사항](../../../03_ontology-search/03_derived-properties.md#limitations)을 참고하세요.

> **중간 요약**: 파생 속성은 최대 세 단계까지 링크를 따라갈 수 있지만 단계가 늘수록 느려지고, 다른 파생 속성을 원천으로 삼을 수는 없습니다. **Properties** 탭에서 계산된 속성임을 나타내는 표시로 구분되며, 기본 키, 필수 속성, OSv1 등과 관련된 제약이 있습니다.

## 정리

- 파생 속성은 값을 저장하지 않고, 링크된 객체의 값을 실행 시점에 가져오거나 집계해 보여 주는 베타 기능입니다.
- **Properties** 탭에서 속성을 열고 **Source** 탭의 **Linked objects**를 선택한 뒤 링크 타입, 집계, 대상 속성을 지정합니다.
- 링크가 여러 객체에 닿으면 Count, Average, Sum, Minimum, Maximum, cardinality, Collect list, Collect set 중 하나의 집계가 필요합니다.
- Collect list와 Collect set의 수집 제한(기본 10, 최대 100)은 반환 개수만 정하며, 필터와 정렬은 전체 값을 대상으로 합니다.
- 최대 세 단계까지 다단계 탐색이 가능하지만 파생 속성끼리 연쇄할 수는 없습니다.
