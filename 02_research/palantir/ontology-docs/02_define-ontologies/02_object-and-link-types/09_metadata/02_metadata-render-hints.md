# 렌더 힌트 (Render hints)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/metadata-render-hints/
- 사이드바 위치: Define Ontologies > Object and link types > Metadata > Render hints

이 페이지는 속성(property)에 설정하는 렌더 힌트(render hint)가 무엇이고, 각 힌트가 애플리케이션의 표시 방식과 인덱싱 성능에 어떤 영향을 주는지 설명합니다. 렌더 힌트는 "이 속성으로 정렬할 수 있는가", "이 속성으로 집계할 수 있는가" 같은 사용 방식을 지정하는데, 그중 다수가 추가 인덱스를 만들기 때문에 켜고 끄는 선택이 재인덱싱 시간과 직결됩니다.

## 렌더 힌트 개요

Foundry는 **렌더 힌트(render hint)를** 사용해 온톨로지 [속성](../03_properties/01_properties-overview.md)의 사용 방식에 관한 정보를 [Object Storage v1(Phonograph)](../../../06_ontology-architecture/05_object-databases/01_object-storage-v1.md)과 플랫폼의 사용자 애플리케이션에 전달합니다. 예를 들어 문자열 속성에 `sortable` 렌더 힌트를 붙이면, 애플리케이션이 타임라인이나 차트에서처럼 사용자가 그 속성으로 정렬할 수 있게 합니다.

많은 렌더 힌트가 객체 타입의 재인덱싱(reindex) 성능과 연결되어 있습니다. 예를 들어 렌더 힌트로 어떤 속성은 애플리케이션에서 집계하거나 정렬할 필요가 없다고 [Object Storage v1(Phonograph)](../../../06_ontology-architecture/05_object-databases/01_object-storage-v1.md)에 알려 줄 수 있으며, 그러면 Object Storage v1이 그 속성들을 인덱싱할 때 할 일이 줄어듭니다.

렌더 힌트는 속성 편집기의 속성 창에서 선택하거나 선택 해제할 수 있습니다(아래 이미지 참고).

![렌더 힌트](https://www.palantir.com/docs/resources/foundry/object-link-types/render-hints.png)

**설명**: 인덱싱(indexing)은 백킹 데이터셋(backing dataset)의 행을 검색 가능한 저장소(여기서는 Object Storage v1, 내부 이름 Phonograph)에 넣으면서 빠른 검색, 정렬, 집계를 위한 자료구조를 만드는 과정입니다. 데이터베이스에서 `CREATE INDEX`를 많이 걸수록 조회는 빨라지지만 쓰기와 재구축이 느려지는 것처럼, 렌더 힌트를 많이 켤수록 기능은 늘어나지만 인덱싱 작업량도 늘어납니다. 재인덱싱(reindex)은 데이터나 설정이 바뀌었을 때 이 인덱스를 다시 만드는 작업입니다.

> **중간 요약**: 렌더 힌트는 속성을 정렬, 집계, 검색 등에 어떻게 쓸지를 Object Storage v1과 애플리케이션에 알리는 설정입니다. 필요 없는 힌트를 끄면 인덱싱 작업이 줄어 재인덱싱 성능이 좋아집니다.

## 렌더 힌트 목록

다음 표는 사용 가능한 각 렌더 힌트의 **Name**(이름)과 **Description**(설명)을 보여 줍니다. 또한 렌더 힌트의 두 가지 기술적 측면인 "Adds raw index?"(원시 인덱스 추가 여부)와 "Requires reindex?"(재인덱싱 필요 여부)에 대한 정보도 제공합니다(아래에서 설명).

* **Adds raw index?**(원시 인덱스를 추가하는가?)
  * 원시 인덱스를 추가하는 렌더 힌트를 적용하기 위해, Object Storage v1(Phonograph)은 백킹 데이터셋을 저장할 때 인덱스를 하나 더 만들어 렌더 힌트 정보를 저장합니다.
  * 이 추가 인덱스 때문에, 렌더 힌트가 적용된 속성은 Object Storage v1(Phonograph)에 인덱싱되는 전체 열 수에서 열 두 개로 계산됩니다.
  * 이것이 바로 이러한 렌더 힌트를 선택 해제하면 Object Storage v1(Phonograph)로의 재인덱싱 성능이 좋아지는 이유입니다.
* **Requires reindex?**(재인덱싱이 필요한가?)
  * 어떤 렌더 힌트는 Ontology Manager에서 선택을 저장하는 즉시 사용자 애플리케이션에 적용됩니다.
  * 재인덱싱이 필요한 다른 렌더 힌트의 경우, 변경 사항이 사용자 애플리케이션에 반영되려면 먼저 객체 타입의 백킹 데이터소스(backing datasource)를 Object Storage V1(Phonograph)에 다시 인덱싱해야 합니다.
  * 다음 번에 트리거되는 재인덱싱을 기다리거나, 객체 타입의 **Datasources** 탭으로 이동해 **Phonograph** 창의 파란색 **Reindex** 버튼을 선택하여 수동으로 재인덱싱을 시작할 수 있습니다.

|Name   |Description    |Adds raw index?    |Requires reindex?  |
|---    |---    |---    |---    |
|Disable formatting |- 속성 값이 Object Views에서 브라우저 위치의 지역별 숫자 서식 표준에 따라 서식화되지 않아야 한다면 **활성화**합니다.   |   |   |
|Identifier |- 숫자 기본 타입(base type)을 가지지만 서식화하거나 숫자로 취급할 필요가 없는 기본 키와 외래 키를 지정하고 재인덱싱 성능을 개선하려면 **활성화**합니다. <br>    - 예를 들어 Object Views는 속성 값을 숫자 서식으로 표시하지 않고, Object Explorer는 키를 범위로 필터링하는 기능을 제공하지 않습니다.    |   |   |
|Keywords   |- Object Views에서 속성을 표시할 때 이 속성을 별도 섹션에 강조해서 보여 주려면 **활성화**합니다.     |   |   |
|Long text  |- 속성 값에 많은 양의 텍스트가 들어 있다면 **활성화**합니다. <br>    - 예를 들어 Object Views는 이 속성의 값을 더 읽기 쉬운 형식으로 표시합니다.    |   |   |
|Low cardinality    |- 이 속성에 가능한 값이 많지 않다는 것을 애플리케이션에 알리려면 **활성화**합니다. <br>    - 예를 들어 일부 Object View 위젯은 가능한 값이 많지 않은 속성에 대해서만 필터링을 허용합니다. <br>- Low cardinality와 함께 Searchable 렌더 힌트도 **반드시 선택해야** 합니다.     |yes    |yes    |
|Selectable |- 문자열 속성에서 사용자가 이 속성으로 집계를 수행할 수 있게 하려면 **활성화**합니다. <br>    - 예를 들어 이 속성은 Object Explorer 히스토그램과 Object View 차트에서 집계됩니다. <br>- 숫자와 날짜 속성에서 분포뿐 아니라 정확한 항(term) 값 기준으로도 집계할 수 있게 하려면 **활성화**합니다. <br>- 애플리케이션에서 이 속성을 집계하지 않을 것이라면 재인덱싱 성능을 개선하기 위해 **비활성화**합니다. <br>- 정확히 일치(Exact Match) 필터 기능을 사용하려면 **활성화**합니다. <br>- Selectable과 함께 Searchable 렌더 힌트도 **반드시 선택해야** 합니다.     |yes    |yes    |
|Sortable   |- 문자열 속성에서 사용자가 이 속성으로 정렬할 수 있게 하려면 **활성화**합니다. <br>    - 숫자와 날짜 속성은 항상 정렬할 수 있습니다. <br>    - 예를 들어 Object Views의 타임라인과 차트가 이 속성 기준으로 정렬됩니다. <br>- 애플리케이션에서 이 속성으로 정렬하지 않을 것이라면 재인덱싱 성능을 개선하기 위해 **비활성화**합니다. <br>- 배열은 배열 안의 최솟값을 기준으로 정렬되므로 **배열에는 권장하지 않습니다**. <br>- Sortable과 함께 Searchable 렌더 힌트도 **반드시 선택해야** 합니다.     |yes    |yes    |
|Searchable |- 애플리케이션에서 이 속성으로 검색하거나 정렬하지 않을 것이라면 재인덱싱 성능을 개선하기 위해 **비활성화**합니다. <br>    - 속성에 큰 문자열이 들어 있다면 성능 개선 효과가 특히 큽니다. <br>- 애플리케이션이 Selectable, Sortable, Low cardinality 렌더 힌트를 적용하려면 Searchable이 **반드시 선택되어 있어야** 합니다.     |yes    |yes    |
|Enable leading wildcards   |- 문자열 속성에서 앞쪽 와일드카드(leading wildcard) 질의를 지원하려면 **활성화**합니다. <br>- Enable leading wildcards와 함께 Searchable 렌더 힌트도 **반드시 선택해야** 합니다.     |yes    |yes    |
|Enable regex queries   |- 문자열 속성에서 정규 표현식(regex) 질의를 지원하려면 **활성화**합니다. <br>- Enable regex queries와 함께 Searchable 렌더 힌트도 **반드시 선택해야** 합니다.     |yes    |yes    |

**설명**: 표에 나오는 몇 가지 용어를 구체적인 예로 정리합니다.

- **카디널리티(cardinality)**: 한 열에 나타나는 서로 다른 값의 개수입니다. `status` 열의 값이 `open`, `closed`, `pending` 세 가지뿐이면 카디널리티가 낮고, `email` 열처럼 행마다 값이 다르면 카디널리티가 높습니다. 값 종류가 적은 속성은 "값별 개수"를 필터 목록으로 보여 주기 좋습니다.
- **집계(aggregation)**: SQL의 `SELECT status, COUNT(*) FROM tickets GROUP BY status` 처럼 값별로 묶어 개수나 합계를 내는 작업입니다. Selectable은 문자열 속성에 이런 집계를 허용합니다.
- **앞쪽 와일드카드(leading wildcard)**: `*-2024`처럼 패턴이 와일드카드로 시작하는 질의입니다. SQL의 `LIKE '%-2024'`가 일반 B-트리 인덱스를 활용하기 어려운 것처럼, 앞쪽 와일드카드 검색은 별도의 인덱스 구조가 필요해 따로 켜야 합니다.
- **Identifier의 예**: `employee_number`가 정수 타입이라도 값 `1024`를 `1,024`로 서식화하거나 "1000\~2000 사이" 범위로 필터링하는 것은 의미가 없습니다. 이런 키 열에 Identifier를 켭니다.

> **중간 요약**: 표시 방식만 바꾸는 힌트(Disable formatting, Identifier, Keywords, Long text)는 추가 인덱스나 재인덱싱이 필요 없습니다. Low cardinality, Selectable, Sortable, Searchable, 와일드카드와 정규 표현식 힌트는 원시 인덱스를 추가하고 재인덱싱이 필요하며, Searchable이 나머지 힌트의 전제 조건입니다.

## 정리

- 렌더 힌트는 속성의 사용 방식(정렬, 집계, 검색, 표시 형식)을 Object Storage v1(Phonograph)과 애플리케이션에 알리는 설정입니다.
- 원시 인덱스를 추가하는 힌트가 적용된 속성은 인덱싱 열 수에서 두 개로 계산되므로, 쓰지 않는 힌트를 끄면 재인덱싱 성능이 좋아집니다.
- 재인덱싱이 필요한 힌트는 다음 재인덱싱을 기다리거나 **Datasources** 탭의 **Reindex** 버튼으로 수동 재인덱싱해야 반영됩니다.
- Selectable, Sortable, Low cardinality, 와일드카드, 정규 표현식 힌트를 쓰려면 Searchable도 켜야 합니다.
