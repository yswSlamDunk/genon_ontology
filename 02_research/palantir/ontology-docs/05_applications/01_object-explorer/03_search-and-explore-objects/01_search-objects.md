# 객체 검색 (Search for objects)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/search-objects/
- 사이드바 위치: Applications > Object Explorer > Search and explore objects > Search for objects

이 페이지는 Object Explorer의 전역 검색창으로 검색했을 때 나타나는 검색 결과 페이지를 설명합니다. 결과가 탭과 사이드바로 어떻게 분류되는지, 어떤 종류의 결과가 나오고 어떤 순서로 정렬되는지, 그리고 검색 결과의 객체에서 링크를 따라 바로 탐색을 시작하는 방법을 다룹니다.

Object Explorer [홈 페이지](../02_getting-started.md)의 전역 검색창으로 검색한 결과는 검색 결과 페이지에 표시됩니다.

검색어는 검색창(아래 그림의 A)에 표시되며 수정할 수 있습니다.

페이지는 탭 **(B)으로** 나뉩니다.

* **All** 탭이 기본으로 표시되며 모든 결과를 포함합니다.
* 일치하는 결과는 다음과 같은 별도의 탭으로 걸러 볼 수 있습니다.
  * Objects(객체) **(C)**,
  * Object types(객체 타입) **(D)**,
  * Artifacts(아티팩트) **(E)**.

이 검색 결과 페이지에는 [사이드바](#navigate-using-the-sidebar)(아래 그림의 **F**)도 있습니다.

![검색 결과 화면](https://www.palantir.com/docs/resources/foundry/object-explorer/OE_search_results_general_annotated.png)

<a id="navigate-using-the-sidebar"></a>
## 사이드바로 탐색하기 (Navigate using the sidebar)

결과는 모두 유형별로 분류됩니다. 왼쪽의 탐색 메뉴(위 그림의 **F**)를 이용하면 여러 범주 사이를 이동할 수 있습니다.

어떤 섹션의 제목을 선택해도 그 유형의 결과로 필터링됩니다. 또한 **All results** 뷰에서 기본으로 보여 주는 개수보다 결과가 많은 경우, 그 유형의 결과를 모두 보여 줍니다(아래 그림의 **1**).

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/OE_search_results_sidebar_annotated.png" alt="사이드바" width="200"/>

* 첫 번째 항목인 **All results**(위 그림의 **1**)는 범주별로 일치 항목의 일부 샘플을 표시합니다. 페이지에 처음 들어오면 이 항목이 기본으로 활성화되어 있습니다.
* 다음은 **"Object type filters"(객체 타입 필터) (2)** 입니다. 이 중 하나를 클릭하면 해당 객체 타입에 대한 더 긴 일치 목록이 표시됩니다. 섹션 하단의 **"View X other filters >"를** 클릭하면 탭이 "All"에서 "Objects"로 바뀌며, 여기서 객체 결과와 필터의 전체 목록을 살펴볼 수 있습니다.
* **"Object type groups"(객체 타입 그룹) (3)** 는 연관된 그룹을 기준으로 결과를 필터링합니다. 섹션 하단의 **"View all filters >"를** 클릭하면 탭이 "All"에서 "Object types"로 바뀌며, 여기서 객체 타입 결과의 전체 목록을 살펴볼 수 있습니다.
* 마지막은 **"Artifacts"(아티팩트) (4)** 에 대한 일치 항목으로, "Explorations & Lists", "Comparison Views", "Modules"로 나뉩니다. 섹션 하단의 **"View all filters >"를** 클릭하면 탭이 "All"에서 "Artifacts"로 바뀌며, 여기서 결과의 전체 목록을 살펴볼 수 있습니다.

> **중간 요약**: 검색 결과 페이지는 All, Objects, Object types, Artifacts 탭과 왼쪽 사이드바로 구성됩니다. 사이드바의 각 섹션(객체 타입 필터, 객체 타입 그룹, 아티팩트)을 클릭하면 해당 유형의 전체 결과로 이동합니다.

<a id="types-of-results"></a>
## 결과 유형 (Types of results)

Object Explorer 검색창은 플랫폼의 모든 객체(맨 위 그림의 **(C)**)와 함께, 객체 타입 **(D)**, 저장된 탐색(Exploration), 목록(List), 비교(Comparison), 모듈(Module) **(E)** 같은 객체 관련 리소스를 검색합니다.

숨김(hidden) 처리된 객체 타입과 속성 타입은 검색 결과에 표시되지 않으며, Object Explorer의 다른 어느 곳에도 표시되지 않습니다.

<a id="sorting-results"></a>
### 결과 정렬 (Sorting results)

개별 객체 결과 섹션 안에서 결과는 다음과 같이 정렬됩니다.

* 모든 주요(prominent) 객체 타입이 주요하지 않은(non-prominent) 객체 타입보다 먼저 표시됩니다.
* 주요 결과와 비주요 결과 각각의 안에서는, 객체 타입이 해당 타입의 개별 객체 결과 수를 기준으로 오름차순 정렬됩니다. 즉 결과가 가장 적은 주요 객체 타입이 먼저 표시되고, 그다음 결과가 더 많은 주요 객체 타입, 그다음 (다른 비주요 타입과 비교해) 결과가 가장 적은 비주요 객체 타입 순으로 표시됩니다.

**설명**: "주요(prominent)"와 "숨김(hidden)"은 Ontology Manager에서 객체 타입이나 속성 타입에 지정하는 가시성(visibility) 설정입니다. 예를 들어 Flight(주요, 결과 30개), Airport(주요, 결과 2개), LogEntry(비주요, 결과 5개)가 검색되면 표시 순서는 Airport, Flight, LogEntry입니다. 결과가 적은 타입을 먼저 보여 주므로, 검색어와 정확히 맞는 소수의 객체가 많은 결과에 묻히지 않습니다.

<a id="exploring-objects-linked-to-a-particular-result"></a>
### 특정 결과에 링크된 객체 탐색 (Exploring objects linked to a particular result)

개별 객체에 대한 일치 항목(위 그림의 **2**)에 마우스를 올리면, 그 개별 결과와 특정 링크로 연결된 객체들에 대한 탐색을 시작하는 옵션이 나타납니다.

예: 공항 "SFO"를 검색했다면, 결과에 마우스를 올려 그 공항에 도착하는 항공편에 대한 탐색을 시작할 수 있습니다.

![Search Around](https://www.palantir.com/docs/resources/foundry/object-explorer/OE_search_results_search_around.png)

**설명**: 이 동작을 Search Around라고 부르며, SQL로는 `SELECT * FROM flights WHERE destination_airport_id = 'SFO'`처럼 검색된 객체의 키로 링크된 테이블을 조회하는 것에 해당합니다. 결과로 SFO에 도착하는 Flight 객체 집합이 만들어지고, 그 집합에 대한 새 탐색이 열립니다.

> **중간 요약**: 검색은 객체뿐 아니라 객체 타입, 저장된 탐색, 목록, 비교, 모듈까지 대상으로 하며, 숨김 처리된 타입은 나오지 않습니다. 객체 결과는 주요 타입 우선, 그 안에서 결과 수 오름차순으로 정렬되고, 결과에서 링크를 따라 바로 탐색을 시작할 수 있습니다.

## 정리

- 전역 검색 결과는 All, Objects, Object types, Artifacts 탭과 왼쪽 사이드바로 분류되어 표시됩니다.
- 사이드바의 섹션 제목이나 "View ... filters >"를 누르면 해당 유형의 전체 결과로 이동합니다.
- 숨김 처리된 객체 타입과 속성 타입은 어디에도 표시되지 않습니다.
- 객체 결과는 주요 객체 타입이 먼저, 각 그룹 안에서는 결과 수가 적은 타입이 먼저 표시됩니다.
- 개별 객체 결과에서 링크를 따라 연결된 객체 집합에 대한 탐색을 바로 시작할 수 있습니다.
