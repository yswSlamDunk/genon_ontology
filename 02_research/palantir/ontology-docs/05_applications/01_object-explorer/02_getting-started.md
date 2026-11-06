# 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/getting-started/
- 사이드바 위치: Applications > Object Explorer > Getting started

이 페이지는 Object Explorer를 열면 처음 보이는 홈 화면의 구성 요소를 하나씩 설명합니다. 전역 검색창, 객체 타입 그룹, 그룹 그래프, 객체 타입 미리 보기, 즐겨찾기, 저장된 탐색 목록이 각각 무엇을 하는지 알면, 찾고 싶은 객체가 정해져 있을 때와 어떤 객체 타입이 있는지부터 둘러볼 때 모두 어디서 시작해야 할지 알 수 있습니다.

아래 홈 페이지는 Object Explorer를 열었을 때 표시됩니다. 이 화면은 객체 탐색을 시작하는 안내 허브로, 구체적인 질문을 갖고 시작할 수도 있고 탐색할 만한 객체 타입을 찾아보며 시작할 수도 있습니다.

이 뷰에서 사용자는 다음과 같은 주요 작업을 할 수 있습니다.

* 검색창 **(A)에서** 플랫폼의 객체 영역 전체를 검색합니다.
* 객체 타입 그룹을 탐색합니다 **(B, C, D)**.
* 특정 객체 타입을 미리 봅니다 **(E)**.
* 탐색할 특정 객체 타입을 선택합니다 **(F)**.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/home_general.png" alt="Object Explorer 홈 페이지"/>

<a id="global-search-bar-a"></a>
## 전역 검색창 (A) (Global search bar (A))

전역 검색창은 온톨로지 전체를 대상으로 검색합니다. 개별 객체, 객체 타입, 저장된 탐색(saved exploration), 모듈(객체 기반 애플리케이션)을 검색하는 데 사용할 수 있습니다.

**주의**: 사용자가 찾을 수 있는 객체 타입이 온톨로지에 250개를 넘으면, 키워드 검색은 처음 250개의 객체 타입으로 제한됩니다. 특정 객체 타입이나 객체 타입 그룹을 검색하려면 [아래](#group-exploration-b-c-d)에서 설명하는 기능을 활용해야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/home_search_bar.png" alt="전역 검색창"/>

이 검색은 검색어 **(1)가** 다음과 일치하는 결과를 가져옵니다.

* 객체 타입, 속성 타입(property type), 저장된 탐색의 타이틀이나 메타데이터(예: 이름, 설명 등).
* 개별 객체의 타이틀이나 모든 속성.

일부 일치 항목, 즉 객체 타입과 속성 타입 결과는 입력하는 동안 바로 자동 완성(type-ahead) 결과 **(3)로** 표시됩니다. 모든 일치 항목을 보려면 첫 번째 옵션인 **Search for...** **(2)를** 클릭해 [검색 결과 페이지](03_search-and-explore-objects/01_search-objects.md)로 이동합니다.

검색창의 검색 문법은 [검색 문법 가이드](03_search-and-explore-objects/02_search-syntax.md)에서 더 알아볼 수 있습니다.

> **중간 요약**: 홈 화면의 전역 검색창은 객체, 객체 타입, 저장된 탐색, 모듈을 한꺼번에 검색하며, 객체 타입과 속성 타입은 자동 완성으로 바로 보여 줍니다. 객체 타입이 250개를 넘으면 키워드 검색 대상이 처음 250개로 제한되므로 그룹 기능을 써야 합니다.

<a id="group-exploration-b-c-d"></a>
## 그룹 탐색 (B, C, D) (Group exploration (B, C, D))

사용자가 접근할 수 있는 모든 객체 타입은 검색창 아래에 [설정 가능한 객체 그룹](06_configure.md)으로 표시됩니다. 측면 탐색 영역 **(C)에서** 그룹을 선택해 이동합니다.

<a id="search-with-object-type-groupings-b"></a>
### 객체 타입 그룹으로 검색 (B) (Search with object type groupings (B))

객체 타입 그룹은 전역 검색창에도 반영됩니다. 미리 설정된 그룹은 왼쪽 탭에서 사용할 수 있고, 사용자 지정 그룹은 **Object types** 아래에서 빠르게 구성할 수 있습니다. 여기서 객체 타입 그룹을 선택하면, 탐색할 객체 타입 하나를 고르기 전에 더 좁혀진 객체 타입 집합을 대상으로 검색할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/home_object_type_groupings.png" alt="객체 타입 그룹"/>

<a id="explore-object-type-groups-on-a-graph-d"></a>
### 그래프에서 객체 타입 그룹 탐색 (D) (Explore object type groups on a graph (D))

그래프는 사용자가 온톨로지를 탐색하고 특정 그룹 안의 객체 타입들 사이의 연결을 이해하도록 돕기 위해 설계되었습니다.

**Graph** 아이콘을 클릭하면 그룹 그래프가 표시됩니다. 이 그래프는 그룹 안 객체 타입들 사이의 링크와 다른 객체 타입 그룹으로 가는 링크 **(1)를** 보여 줍니다. 이 뷰에서 객체 타입 그룹을 제거하거나 **(2)** 그래프 레이아웃을 바꿀 수도 있습니다 **(3)**.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/home_object_type_group_graph.png" alt="객체 타입 그룹 그래프"/>

링크 기호(<->)를 클릭하면 객체 타입 사이의 링크 타입이 표시됩니다 **(4)**.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/home_object_type_graph_link.png" alt="객체 타입 그래프 링크"/>

객체 하나를 선택하면 메뉴 **(5)가** 나타나며, 여기서 [객체 타입 미리 보기](#preview-object-types-e)를 살펴보거나 탐색을 시작할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/home_object_type_graph_menu.png" alt="객체 타입 그래프 메뉴"/>

**설명**: 이 그래프는 데이터베이스의 ER 다이어그램(Entity-Relationship diagram)과 같은 정보를 보여 줍니다. 노드는 객체 타입(테이블), 선은 링크 타입(외래 키로 이어지는 관계)입니다. 예를 들어 Flight, Airport, Aircraft가 한 그룹에 있다면 Flight와 Airport 사이, Flight와 Aircraft 사이에 선이 그려집니다.

> **중간 요약**: 객체 타입은 설정 가능한 그룹으로 묶여 표시되며, 그룹을 골라 검색 범위를 좁히거나 그룹 그래프로 객체 타입 사이의 링크 구조를 볼 수 있습니다.

<a id="preview-object-types-e"></a>
## 객체 타입 미리 보기 (E) (Preview object types (E))

객체 미리 보기를 클릭하면 더 포괄적인 탐색 페이지로 이동하지 않고 객체 타입을 빠르게 볼 수 있습니다. 미리 보기에서는 설명, 속성, 링크된 객체 타입을 포함한 객체 타입 정보 **(1)를** 확인할 수 있습니다. **Start Exploration** **(2)을** 클릭하면 해당 객체 타입에 대한 새 탐색(Exploration)이 시작됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/home_object_type_preview.png" alt="객체 타입 미리 보기" width="400"/>

<a id="add-object-type-as-favorite-f"></a>
### 객체 타입을 즐겨찾기에 추가 (F) (Add object type as favorite (F))

객체 타입 카드의 별 아이콘 **(1)을** 클릭하면 그 객체 타입을 즐겨찾기에 추가할 수 있습니다. 즐겨찾기는 측면 탐색 영역 맨 위의 전용 그룹에 표시되며, 인터페이스 하단의 **All object types** 전체 목록에도 나타납니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/home_fav.png" alt="Explorer"/>

<a id="explorations-lists-g"></a>
### 탐색 및 목록 (G) (Explorations & lists (G))

저장된 탐색과 목록(list)은 쉽게 접근할 수 있도록 홈 페이지 상단에 표시됩니다. **Artifacts** 탭에서도 찾을 수 있습니다.

## 정리

- Object Explorer 홈 화면은 검색과 객체 타입 둘러보기를 시작하는 허브입니다.
- 전역 검색창(A)은 객체, 객체 타입, 저장된 탐색, 모듈을 검색하며, 객체 타입이 250개를 넘으면 그룹을 이용해 범위를 좁혀야 합니다.
- 객체 타입 그룹(B, C)으로 검색 대상을 좁히고, 그룹 그래프(D)로 객체 타입 사이의 링크를 확인합니다.
- 미리 보기(E)로 객체 타입의 설명, 속성, 링크를 빠르게 보고 Start Exploration으로 탐색을 시작합니다.
- 즐겨찾기(F)와 저장된 탐색 및 목록(G)으로 자주 쓰는 대상에 빠르게 접근합니다.
