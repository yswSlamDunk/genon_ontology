# 객체 관계 탐색하기 (Explore object relationships)

- 원문: https://www.palantir.com/docs/foundry/vertex/explore-object-relationships/
- 사이드바 위치: Applications > Vertex > Graphs > Explore object relationships

이 페이지는 Vertex에서 빈 그래프로 새 탐색을 시작하고, 링크를 따라가며 관련 객체를 그래프에 추가하는 방법을 설명합니다. 핵심은 Search Around 기능으로, 한 단계짜리 기본 탐색부터 필터와 파라미터를 붙인 여러 단계 탐색, 그리고 그 탐색을 리소스로 저장해 재사용하는 방법까지 다룹니다.

Vertex를 사용하면 실제 조직의 디지털 트윈(digital twin) 전반에서 원인과 결과를 시각화하고 정량화할 수 있습니다. Vertex를 사용해 조직이 게시한 기존 그래프에 접근해 탐색하거나 새 그래프를 만들 수 있습니다.

<a id="start-a-new-exploration"></a>
## 새 탐색 시작하기 (Start a new exploration)

Vertex는 Foundry 작업 공간 사이드바의 **Apps** 섹션에서 **Operational Applications** 머리글 아래에서 실행할 수 있습니다. 새 탐색을 시작하려면 애플리케이션 목록에서 **Vertex**를 선택하고 **+ New Graph** 아이콘을 클릭합니다.

새 탐색을 시작하면 빈 작업 공간이 열리며, 여기서 **+ add objects**(객체 추가)를 선택해 시작할 수 있습니다. 객체 검색 팝업에서 탐색하고 싶은 객체를 선택하면 그래프 만들기가 시작됩니다.

![이벤트 배지](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_1.jpg)

<a id="object-selection-panel"></a>
### 객체 선택 패널 (Object selection panel)

그래프에서 객체를 클릭하면 선택 패널이 자동으로 열려 객체의 속성(property)을 표시합니다.

![선택 패널](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_2.jpg)

선택 패널 오른쪽 아래 모서리의 **(+)** 기호를 선택하면 [파생 속성 함수(derived property functions)](08_derive-property-functions.md)를 추가할 수 있습니다. 이 예에서는 간단한 함수가 공항과 관련된 노선의 알림(alert) 총개수를 계산합니다. 파생 속성은 선택 패널 맨 위에 표시됩니다.

![파생 속성](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_3.jpg)

**설명**: 파생 속성은 데이터셋의 열로 저장되어 있지 않고, 객체를 입력으로 받아 함수(function)가 그 자리에서 계산해 돌려주는 값입니다. 예를 들어 JFK Airport 객체를 넣으면 함수가 JFK와 링크된 Route 객체들을 찾고, 각 Route에 링크된 Alert 객체 수를 더해 `12` 같은 숫자를 반환합니다. SQL로 치면 저장된 열이 아니라 조회 시점에 `COUNT(*)`로 계산하는 열입니다.

> **중간 요약**: **Apps** 사이드바에서 Vertex를 열고 **+ New Graph**로 빈 그래프를 만든 뒤 객체를 추가합니다. 객체를 클릭하면 속성이 선택 패널에 나오고, **(+)로** 함수 기반 파생 속성을 추가할 수 있습니다.

<a id="explore-related-objects"></a>
## 관련 객체 탐색하기 (Explore related objects)

Vertex에서는 운영상의 관계를 따라 이동하며 그래프 시각화를 확장할 수 있습니다. 개별 노드나 노드 그룹에서 마우스 오른쪽 버튼을 클릭하면 선택, 레이아웃, 탐색 옵션을 볼 수 있습니다.

<a id="search-around"></a>
### Search Around

관련 객체 목록에서 선택하면 그 객체들이 그래프에 추가됩니다. 드롭다운 목록 안에 타입별 객체 총개수가 표시됩니다. 객체 수가 많다면 객체 수 옆의 필터 아이콘을 사용해 추가 필터를 넣는 것을 고려하세요. 이 아이콘을 누르면 **Search Around** 패널이 열리며, 여기서 필터를 추가하고 여러 단계에 걸쳐 검색할 수 있습니다.

![기본 Search Around](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_4.jpg)

<a id="build-multi-step-search-arounds"></a>
### 여러 단계 Search Around 만들기 (Build multi-step Search Arounds)

그래프의 객체에서 기본 Search Around를 실행하는 것은 온톨로지(Ontology)를 탐색하고 관련 객체를 그래프에 빠르게 추가하는 좋은 방법입니다. 서로 다른 객체 타입을 가로지르는, 여러 단계에 걸친 필터링된 그래프를 만들고 싶을 때는 **Search Around** 패널이 새 그래프를 생성하면서 로직을 구성할 수 있는 클릭 방식 인터페이스를 제공합니다.

**Search Around** 패널은 기본 **Search Around** 드롭다운 목록 안의 필터 아이콘을 선택하거나, 작업 공간 오른쪽에 있는 탭을 통해 열 수 있습니다. Search Around를 시작하려면 객체 하나 또는 같은 타입의 객체 여러 개를 선택합니다. 그러면 링크를 골라 선택 항목에서 시작하는 Search Around를 만들 수 있습니다.

![여러 단계 Search Around](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_5.png)

시작 객체 집합을 바꾸고 싶다면 새 객체(또는 객체 그룹)를 선택하고, 시작 객체 상자 위에 마우스를 올리면 나타나는 **Set starting objects** 옵션을 클릭합니다.

<a id="find-related-objects"></a>
### 관련 객체 찾기 (Find related objects)

추가할 관련 객체를 선택하면, 결과 객체 타입 옆에 찾은 객체 수가 표시됩니다. 반환된 객체를 더 필터링하려면 **Add filter** 버튼을 클릭하고 결과 객체 집합(object set)을 필터링하는 데 쓸 속성을 선택합니다.

![필터](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_6.png)

객체 집합을 필터링한 뒤에는 바로 그래프에 추가하거나, **Add link** 버튼을 사용해 여러 객체에 걸친 여러 단계 Search Around를 계속 만들 수 있습니다.

Search Around의 다음 링크는 이전 링크의 결과 객체 집합을 시작 객체 집합으로 사용합니다. 이 새 Search Around의 결과 객체 집합을 사용해 그래프에 추가할 관련 객체를 더 찾을 수 있습니다. 이 예에서는 Link 1에서 생성된 항공편의 도착 공항을 찾습니다.

![Link 2](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_7.png)

새 관련 객체 집합을 추가한 뒤에는 이 객체 집합을 더 필터링할 수 있습니다. 필터가 적용되면 시작 객체 집합은 필터링된 결과 객체 집합과 연결된 객체로 걸러집니다. 이 예에서는 157개 항공편이 뉴욕주의 공항으로 출발합니다.

![그래프에 추가](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_8.png)

**Add to graph**를 선택하면 Search Around 패널에서 정의한 탐색 경로를 바탕으로 새 그래프가 생성됩니다. Search Around의 복잡도에 따라 그래프를 생성하는 데 시간이 걸릴 수 있습니다.

**설명**: 여러 단계 Search Around는 조인을 연달아 하는 것과 같습니다. 이 예를 SQL로 쓰면 대략 다음과 같습니다.

```sql
-- Link 1: 시작 공항에서 출발하는 항공편
-- Link 2: 그 항공편의 도착 공항, 단 뉴욕주(NY) 공항만
SELECT f.*, dest.*
FROM airports start
JOIN flights f     ON f.origin = start.code
JOIN airports dest ON f.destination = dest.code
WHERE start.code IN (...선택한 시작 공항...)
  AND dest.state = 'NY';
```

마지막 단계에 필터(`dest.state = 'NY'`)를 걸면, 앞 단계의 항공편 집합도 그 조건을 만족하는 공항과 연결된 항공편만 남습니다. 문서에서 "157개 항공편"이 바로 이렇게 걸러진 결과입니다.

> **중간 요약**: 오른쪽 클릭 메뉴의 기본 Search Around는 링크 하나를 따라 관련 객체를 추가합니다. **Search Around** 패널에서는 **Add filter**와 **Add link**로 필터가 붙은 여러 단계 탐색을 만들고 **Add to graph**로 그래프를 생성하며, 뒤 단계 필터는 앞 단계 객체 집합에도 반영됩니다.

<a id="add-parameters"></a>
### 파라미터 추가하기 (Add parameters)

Search Around의 재사용성을 높이기 위해, Search Around 전체에서 쓸 수 있는 파라미터를 정의할 수 있습니다. 패널 오른쪽 위의 **View parameters** 버튼을 선택해 기존 파라미터를 보거나 새 파라미터를 만듭니다. **Add parameter** 버튼을 선택해 추가할 파라미터의 타입을 고릅니다.

![파라미터 추가](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_9.png)

파라미터를 추가하면 값을 지정하거나, 편집 버튼을 선택해 이름, 설명, 그리고 이 Search Around를 불러올 때 사용할 기본값을 바꿀 수 있습니다.

![파라미터 편집](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_10.png)

그런 다음 타입이 맞는 필터 필드라면 어디에서든 이 파라미터를 사용할 수 있습니다. 파라미터를 쓰려면 필터 필드 옆의 파라미터 토글을 선택한 다음 드롭다운에서 파라미터를 고릅니다. 파라미터 값을 바꾸면 그 파라미터가 쓰인 모든 곳에 새 값이 반영되도록 Search Around가 갱신됩니다.

![파라미터 사용](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_11.png)

**설명**: 파라미터는 함수의 매개변수와 같은 역할을 합니다. 앞의 SQL에서 `'NY'`를 직접 쓰는 대신 `state` 파라미터(문자열 타입, 기본값 `NY`)를 만들어 필터에 연결하면, 값을 `CA`로 바꾸는 것만으로 같은 탐색을 캘리포니아주 공항 기준으로 다시 실행할 수 있습니다. 타입이 맞아야 한다는 것은 문자열 파라미터는 문자열 속성 필터에만 연결할 수 있다는 뜻입니다.

<a id="save-and-load"></a>
### 저장하고 불러오기 (Save and load)

이 Search Around를 다른 그래프나 그래프 템플릿 안에서 재사용하고 싶다면 리소스로 저장할 수 있습니다. 이렇게 하려면 저장하려는 Search Around의 탭 옆 드롭다운을 선택합니다. 그러면 Search Around를 저장할 이름과 위치를 고를 수 있는 모달이 열립니다.

![Search Around 저장](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_12.png)

Search Around 탭 머리글의 **+** 아이콘으로 새 Search Around를 추가할 때 **Load Search Around** 옵션을 선택하면, 열 Search Around를 고를 수 있는 리소스 선택기가 열립니다. Search Around를 불러오면 Search Around의 시작 객체 집합으로 쓸 객체를 그래프에서 선택하라는 안내가 나옵니다. 타입이 맞는 객체만 선택할 수 있습니다.

![Search Around 불러오기](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_13.png)

> **중간 요약**: Search Around에 파라미터를 정의하면 값만 바꿔 같은 탐색을 재사용할 수 있고, Search Around 자체를 리소스로 저장했다가 다른 그래프나 템플릿에서 불러와 새 시작 객체에 적용할 수 있습니다.

<a id="histogram-filters"></a>
## 히스토그램 필터 (Histogram filters)

객체 그래프를 만든 뒤에는 히스토그램 필터를 사용해 그래프를 탐색하고 필터링할 수 있습니다. 히스토그램은 선택한 객체의 속성을 표시하고 각 값의 합계를 제공합니다. 히스토그램에서 한 선택은 그래프에 반영되어, 탐색을 더 세밀하게 할 수 있습니다.

![히스토그램 필터](https://www.palantir.com/docs/resources/foundry/vertex/explore_objects_14.jpg)

## 정리

- 새 탐색은 Vertex에서 **+ New Graph**로 빈 그래프를 만들고 **+ add objects**로 시작합니다.
- 객체 선택 패널은 속성을 보여 주며, 함수로 계산하는 파생 속성을 추가할 수 있습니다.
- Search Around는 링크를 따라 관련 객체를 추가하는 기능이며, 패널에서 필터와 여러 단계 링크를 조합할 수 있습니다.
- 파라미터와 리소스 저장 기능으로 Search Around를 다른 그래프와 템플릿에서 재사용할 수 있습니다.
- 그래프를 만든 뒤에는 히스토그램 필터로 결과를 더 세밀하게 탐색합니다.
