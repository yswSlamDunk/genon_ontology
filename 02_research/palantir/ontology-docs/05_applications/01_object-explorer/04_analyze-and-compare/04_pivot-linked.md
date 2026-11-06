# 연결된 객체로 피벗하여 탐색하기 (Pivot to explore linked objects)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/pivot-linked/
- 사이드바 위치: Applications > Object Explorer > Analyze and compare > Pivot to explore linked objects

이 페이지는 Object Explorer에서 탐색의 중심 객체 타입을 링크로 연결된 다른 객체 타입으로 바꾸는 피벗(pivot) 기능을 설명합니다. 공항을 먼저 걸러 낸 뒤 그 공항에서 출발하는 항공편으로 넘어가는 예시를 통해, 링크 타입을 따라 온톨로지를 단계적으로 이동하며 질문에 답하는 방법을 보여 줍니다.

탐색을 수행하는 동안, 탐색의 주 객체 타입을 링크로 연결된 어떤 객체 타입으로든 바꿀 수 있습니다. 아래의 구체적인 예시가 이것이 어떻게 동작하는지 보여 줍니다.

동부 미국의 대형 공항에서 앞으로 30일 안에 출발하는 모든 항공편을 어떻게 찾을 수 있을까요?

특히 이 질문은 **Flights**(항공편) 탐색에서 시작해 연결된 공항의 속성으로 필터링하는 방법([링크된 속성으로 필터링하기](02_explore-charts.md#charts-on-linked-objects))으로도 답할 수 있습니다. 다만 다른 방법으로, **Airports**(공항) 탐색에서 시작해 동부 미국에 있으면서 고유 항공사 수가 많은 공항만 남도록 필터링할 수도 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/charts_cluster_map.png" alt="Airports에 대한 탐색"/>

여기서 이제 연결된 **Departing Flights**(출발 항공편)로 **피벗**하려고 합니다. 오른쪽 아래 "Linked Objects"(연결된 객체) 섹션에서 이 옵션을 클릭하면 됩니다. 그러면 탐색의 주 객체 타입이 **Flights**로 바뀌고, 앞서 필터링해 둔 동부의 대형 공항에서 출발하는 항공편만 남도록 필터가 적용됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/pivot_flights.png" alt="Flights로 피벗된 탐색"/>

위 탐색의 **결과**는 이제 Airports가 아니라 Flights입니다(오른쪽 미리 보기 패널에서 확인할 수 있습니다). 여러 링크를 거쳐 연속으로 피벗할 수도 있으므로, 온톨로지 전체를 유연하게 탐색할 수 있습니다.

**설명**: 피벗은 SQL로 보면 "걸러 낸 공항 집합과 조인해 그 공항의 항공편만 남기는" 조회입니다. 예를 들어 `airports` 테이블에서 `region = 'East' AND carrier_count > 20`으로 공항 3개(JFK, BOS, ATL)를 고른 뒤, `flights` 테이블에서 `departure_airport IN ('JFK', 'BOS', 'ATL')`인 행만 가져오는 것과 결과가 같습니다. Object Explorer에서는 Airports와 Flights 사이의 링크 타입(Departing Flights)이 이미 정의되어 있으므로, 조인 조건을 직접 쓰지 않고 링크 이름을 클릭하는 것만으로 같은 결과를 얻습니다. 이후 "30일 안에 출발" 조건은 Flights 쪽 속성으로 추가 필터링하면 됩니다.

## 정리

- 피벗은 탐색의 주 객체 타입을 링크로 연결된 다른 객체 타입으로 바꾸는 기능입니다.
- 피벗하면 앞서 적용한 필터가 유지되어, 걸러 낸 객체와 연결된 객체만 결과로 남습니다.
- 같은 질문을 링크된 속성 필터링으로도, 피벗으로도 풀 수 있으며, 여러 링크를 거쳐 연속으로 피벗할 수 있습니다.
