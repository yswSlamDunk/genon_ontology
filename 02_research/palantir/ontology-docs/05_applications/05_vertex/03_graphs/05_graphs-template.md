# 그래프 템플릿 만들기 (Create a graph template)

- 원문: https://www.palantir.com/docs/foundry/vertex/graphs-template/
- 사이드바 위치: Applications > Vertex > Graphs > Create a graph template

이 페이지는 한 번 수행한 Vertex 분석을 그래프 템플릿으로 바꿔, 다른 객체를 입력으로 넣기만 하면 같은 구조와 스타일의 그래프를 다시 만들 수 있게 하는 방법을 설명합니다. 템플릿의 파라미터 종류, Search Around 연결, 레이어 스타일 저장, 그리고 완성된 템플릿을 URL이나 Workshop에서 사용하는 법을 다룹니다.

Vertex 그래프 템플릿은 파라미터를 바탕으로, 정의된 스타일을 가진 그래프를 생성하는 리소스입니다. 그래프 템플릿으로 다음과 같은 워크플로를 할 수 있습니다.

* 한 객체나 객체 집합(object set)에 대한 그래프 분석을 다른 객체나 객체 집합으로 전환(pivot)하기.
* 그래프 생성 워크플로를 담은 재사용 가능한 리소스를 만들어 사용자에게 제공하기.
* Object View나 Workshop 애플리케이션 같은 다른 Foundry 애플리케이션에 그래프 템플릿을 임베드하기.

어떤 Vertex 분석이든 그래프 템플릿으로 변환할 수 있습니다. 분석을 템플릿으로 바꾸면 이후 같은 성격의 분석을 더 쉽게 수행할 수 있습니다.

**설명**: 그래프 템플릿은 매개변수를 받는 함수와 같은 구조입니다. 입력(파라미터)으로 객체를 받고, 정해진 탐색 절차(Search Around)와 스타일을 실행해, 출력으로 그래프를 돌려줍니다. 한 번 그린 그래프가 "특정 값으로 한 번 실행한 결과"라면, 템플릿은 그 절차를 함수로 정의해 둔 것입니다.

이 예에서는 Search Around 함수를 사용해, 항공편 `Delay Event`와 링크된 `Aircrafts`, 그리고 같은 날 지연된 다른 `Flights`(`Airports`별)를 분석하며 항공사 지연을 탐색합니다. 아래 보이는 항공편 지연 조사 그래프를 만든 분석은 정해진 구조 없이 자유로운 방식으로 수행되었습니다. 이 분석에서 그래프 템플릿을 만들면 이후 조사에서 이 분석 템플릿을 재사용할 수 있습니다.

![템플릿의 바탕이 될 그래프 분석](https://www.palantir.com/docs/resources/foundry/vertex/template-source-graph.png)

이 분석을 그래프 템플릿으로 변환하려면 오른쪽 위 도구 모음에서 저장 옵션을 열고 **Save as Template...을** 선택합니다.

![템플릿 도우미 열기](https://www.palantir.com/docs/resources/foundry/vertex/template-helper.png)

그러면 **Configure parameters**(파라미터 구성) 옵션이 있는 도우미가 열립니다. 그래프 템플릿 파라미터에는 **객체 파라미터(object parameters)와** **비객체 파라미터(non-object parameters)** 두 종류가 있습니다.

객체 파라미터는 템플릿에 대한 객체 입력으로, 템플릿이 사용될 때 그래프에 추가됩니다. 객체 파라미터를 추가하면 그래프 템플릿 사용자가 제공한 객체에 대해 Search Around와 함수(function)를 수행할 수도 있습니다.

비객체 파라미터는 사용자 정의 Search Around 함수나 저장된 Search Around의 인수로 사용할 수 있는 추가 파라미터입니다. 비객체 파라미터가 지원하는 타입은 Search Around 함수가 지원하는 비객체 인수 타입과 같습니다.

![템플릿 파라미터 구성](https://www.palantir.com/docs/resources/foundry/vertex/template-configure-parameters.png)

**설명**: 이 예라면 객체 파라미터는 "조사할 Delay Event 객체"이고, 비객체 파라미터는 "같은 날로 볼 시간 범위(시간 수)" 같은 숫자나 문자열 값이 될 수 있습니다. 함수 시그니처로 쓰면 `generateGraph(delayEvent: DelayEvent, windowHours: Integer)` 형태입니다.

다음으로 템플릿에 연결된 **Search Around를 구성(configure Search Arounds)할** 수 있습니다. 각 객체 파라미터에는 Search Around를 연결할 수 있으며, 이는 온톨로지 링크를 사용하는 단순 Search Around, Search Around 함수, 또는 Search Around 사이드바로 만든 저장된 Search Around 중 하나입니다. Search Around 함수나 저장된 Search Around의 비객체 인수는 상수나 파라미터 중 하나의 값에 매핑할 수 있습니다. 입력을 파라미터에 매핑하려면 입력 상자 왼쪽의 파라미터 버튼을 선택하고 드롭다운에서 파라미터를 고릅니다.

![템플릿 Search Around 구성](https://www.palantir.com/docs/resources/foundry/vertex/template-configure-search-arounds.png)

원하는 파라미터와 Search Around를 추가한 뒤에는 템플릿에 연결된 **레이어와 레이어 스타일을 구성(configure layers)할** 수 있습니다. 스타일을 지정하는 레이어는 그래프에 현재 적용된 스타일을 그대로 저장합니다. 제외한 레이어는 저장된 템플릿에서 해당 레이어 스타일이 빠집니다.

![템플릿 레이어 구성](https://www.palantir.com/docs/resources/foundry/vertex/template-configure-layers.png)

마지막으로, 적용할 레이아웃과 현재 분석에서 유지할 그래프 설정을 고른 뒤 **템플릿 요약(template summary)을** 보고 템플릿을 저장할 수 있습니다.

![템플릿 요약](https://www.palantir.com/docs/resources/foundry/vertex/template-summary.png)

> **중간 요약**: **Save as Template...을** 고르면 도우미가 열리고, 파라미터(객체와 비객체), 각 객체 파라미터에 연결할 Search Around, 저장할 레이어 스타일, 레이아웃과 그래프 설정을 차례로 정한 뒤 요약을 확인하고 저장합니다.

<a id="use-a-graph-template"></a>
## 그래프 템플릿 사용하기 (Use a graph template)

템플릿을 열면 템플릿 파라미터의 값을 입력하라는 안내가 나옵니다.

URL 쿼리 파라미터를 사용해 템플릿에 객체나 객체 집합을 미리 불러올 수도 있습니다.

* **객체(Object):** 쿼리 파라미터 `objectRid=<your_object_rid_here>`를 사용합니다.
* **객체 집합(Object set):** 쿼리 파라미터 `objectSetRid=<your_object_set_rid_here>`를 사용합니다.

입력한 파라미터 값을 다루려면 위쪽 도구 모음의 **Parameters** 버튼을 사용합니다. 이 버튼으로 특정 객체 파라미터의 값으로 쓰인 모든 객체를 선택하거나, 파라미터 값을 바꿔 그래프를 다시 생성할 수 있습니다.

![템플릿 사용](https://www.palantir.com/docs/resources/foundry/vertex/template-usage.gif)

템플릿은 [Vertex 위젯](09_embed-graph-workshop.md)을 사용해 Workshop에 임베드할 수도 있습니다.

**설명**: RID(Resource Identifier)는 Foundry에서 객체나 객체 집합 같은 리소스를 유일하게 가리키는 식별 문자열입니다. 쿼리 파라미터는 URL의 `?` 뒤에 `이름=값` 형태로 붙이는 값이므로, 템플릿 URL 끝에 `?objectRid=...`를 붙이면 템플릿이 열리자마자 그 객체를 객체 파라미터 값으로 사용합니다.

> **중간 요약**: 템플릿을 열면 파라미터 값을 입력하거나 URL의 `objectRid`, `objectSetRid`로 미리 넣을 수 있고, **Parameters** 버튼으로 값을 바꿔 그래프를 다시 생성합니다. Workshop에서는 Vertex 위젯으로 임베드합니다.

## 정리

- 그래프 템플릿은 파라미터를 받아 정해진 Search Around와 스타일로 그래프를 생성하는 재사용 가능한 리소스입니다.
- 어떤 Vertex 분석이든 **Save as Template...으로** 템플릿으로 바꿀 수 있습니다.
- 파라미터는 그래프에 추가될 객체 파라미터와, Search Around 함수 인수로 쓰는 비객체 파라미터로 나뉩니다.
- 템플릿에는 Search Around, 레이어 스타일, 레이아웃, 그래프 설정이 저장됩니다.
- 사용할 때는 파라미터를 입력하거나 URL 쿼리 파라미터로 미리 넣으며, Workshop에 임베드할 수 있습니다.
