# 객체 집합 비교하기 (Compare object sets)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/compare-object-sets/
- 사이드바 위치: Applications > Object Explorer > Analyze and compare > Compare object sets

이 페이지는 Object Explorer의 Comparison View(비교 보기)로 두 객체 집합(object set)을 나란히 비교하는 방법을 다룹니다. 비교 모드에 들어가는 방법, 비교 중인 두 집합에 함께 필터를 거는 방법, 그리고 비교 결과를 저장, 공유, 검색하는 협업 기능을 설명합니다. "뉴욕 출발 항공편과 캘리포니아 출발 항공편은 무엇이 다른가"처럼 두 그룹의 분포 차이를 확인할 때 쓰는 기능입니다.

Comparison View는 필터링된 두 객체 집합을 비교할 수 있는 기능을 제공합니다. 비교할 객체는 동적으로 필터링한 객체일 수도 있고, 이전에 저장한 탐색(exploration)에서 가져온 객체일 수도 있습니다.

**설명**: 객체 집합(object set)은 "어떤 객체 타입에 어떤 조건을 건 결과"입니다. SQL로 보면 `SELECT * FROM flights WHERE origin_city = 'New York'` 같은 쿼리의 결과 행 집합에 해당합니다. 비교 모드는 이런 쿼리 두 개의 결과를 같은 차트에 겹쳐 보여 줍니다.

<a id="entering-comparison-mode"></a>
## 비교 모드 들어가기 (Entering Comparison Mode)

Comparison Mode를 사용하려면 다음과 같이 합니다.

* Object Explorer로 가서 객체 타입을 열고, 비교하려는 그 타입의 객체 집합이 되도록 필터링합니다. 아래 예에서는 결과를 뉴욕시에서 출발하는 항공편으로 필터링했습니다.
* 검색창 아래의 **Compare** 버튼을 선택합니다. **Compare**를 선택한 다음 비교 대상이 될 객체 집합을 고를 수 있습니다. 예를 들면 다음과 같습니다.
  * 저장된 기존 탐색
  * 해당 타입의 모든 객체(예: **All Flights**)
  * 비교용으로 새로 정의한 객체 집합

아래에서는 뉴욕시 출발 항공편을, 캘리포니아에서 출발하는 모든 항공편에 대한 기존 탐색과 비교하고 있습니다.

![비교 보기 들어가기](https://www.palantir.com/docs/resources/foundry/object-explorer/comparison_enter.png)

비교용 객체 집합을 즉석에서 새로 정의하려면(이 과정을 "동적 필터링(dynamic filtering)"이라고 합니다), 위 이미지의 비교 드롭다운에 보이는 **Create new set of Flights**를 선택합니다.

그러면 객체 집합을 정의하고 편집하거나, 비교 집합에 쓰이는 색상을 바꿀 수 있는 화면이 나타납니다.

![비교용 동적 필터링](https://www.palantir.com/docs/resources/foundry/object-explorer/comparison_dynamic.png)

비교 모드에 들어가면 레이아웃의 모든 차트가 비교 대상 각 집합의 결과를 나란히 보여 주도록 바뀝니다. 이를 통해 NYC 출발 항공편과 CA 출발 항공편의 가장 흔한 도착 공항이나 항공기 등록 번호 같은 항목이 어떻게 다른지 볼 수 있습니다. 이 비교 보기에서도 OE(Object Explorer)의 모든 기능이 그대로 유지됩니다. 예를 들어 차트를 이용한 필터링, 표 보기에서 결과 확인, 액션, 내보내기 등을 모두 사용할 수 있습니다.

![일반 비교 화면](https://www.palantir.com/docs/resources/foundry/object-explorer/comparison_generic.png)

> **중간 요약**: 객체 타입을 필터링한 뒤 **Compare** 버튼을 누르고, 비교 대상으로 저장된 탐색, 전체 객체, 또는 즉석에서 정의한 집합(동적 필터링)을 고릅니다. 그러면 모든 차트가 두 집합의 결과를 나란히 보여 주며, OE의 다른 기능도 그대로 쓸 수 있습니다.

<a id="filtering"></a>
## 필터링 (Filtering)

앞에서 말했듯이, 비교 중인 집합들에 필터를 함께 적용해 비교 범위를 좁힐 수 있습니다. 예를 들어 뉴욕의 취소된 항공편이 캘리포니아의 취소된 항공편과 어떻게 다른지 보기 위해 비교 대상에서 A321 기종 항공편만 보고 싶을 수 있습니다. 이는 평소 OE에서 하듯이 검색창에서 필터를 적용하거나(아래 그림) 차트에서 직접 적용하는 방식으로 할 수 있습니다.

![비교 화면 필터링](https://www.palantir.com/docs/resources/foundry/object-explorer/comparison_filter.png)

**설명**: 여기서 필터는 두 집합 모두에 똑같이 추가됩니다. 즉 집합 A의 조건이 `origin = NYC`, 집합 B의 조건이 `origin = CA`였다면, A321 필터를 걸면 각각 `origin = NYC AND aircraft = A321`, `origin = CA AND aircraft = A321`이 되어 같은 기준으로 좁혀진 두 집합을 비교하게 됩니다.

> **중간 요약**: 검색창이나 차트에서 거는 필터는 비교 중인 두 집합에 함께 적용되어, 같은 조건으로 좁힌 두 집합을 비교할 수 있습니다.

<a id="collaboration"></a>
## 협업 (Collaboration)

<a id="saving-comparison-views"></a>
### 비교 보기 저장하기 (Saving Comparison Views)

Comparison View는 오른쪽 위의 **Save** 버튼을 클릭해 탐색(Exploration)과 똑같이 저장하고 공유할 수 있습니다. 저장할 때 이름을 입력하라는 안내가 나오며, 선택적으로 설명이나 사용자 지정 저장 위치도 지정할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/comparison_save.png" alt="비교 저장" width="300"/>

<a id="sharing-comparison-views"></a>
### 비교 보기 공유하기 (Sharing Comparison Views)

비교를 공유하려면 **Save** 버튼 왼쪽의 **Share** 버튼을 선택하기만 하면 됩니다. 이 비교를 어떤 사용자나 그룹과 공유할지, 어떤 접근 수준을 부여할지, 그리고 모든 사용자에 대한 기본 역할을 둘지를 정하라는 안내가 나옵니다. 비교를 공유해도 연결된 탐색이나 그 밑의 객체에 대한 접근 권한까지 공유되지는 않습니다. 따라서 보는 사람은 저장된 비교 자체에 대한 접근 권한과 함께 데이터에 대한 적절한 역할도 가지고 있어야 합니다.

**설명**: 저장된 비교는 "어떤 집합을 어떤 조건으로 비교할지"라는 정의만 담은 파일입니다. 실제 객체 데이터를 볼 수 있는지는 데이터 쪽 권한으로 따로 결정됩니다. 예를 들어 항공편 데이터에 대한 권한이 없는 동료에게 비교를 공유하면, 그 동료는 비교 파일은 열 수 있어도 항공편 객체는 볼 수 없습니다.

<a id="searching-for-comparison-views"></a>
### 비교 보기 검색하기 (Searching for Comparison Views)

저장된 비교는 홈 페이지의 OE 기본 검색창에서 검색할 수 있습니다.

![비교 검색 결과](https://www.palantir.com/docs/resources/foundry/object-explorer/comparison_search_result.png)

> **중간 요약**: 비교 보기는 **Save**로 이름과 위치를 정해 저장하고 **Share**로 공유하며, 홈 화면 검색창에서 찾을 수 있습니다. 공유는 비교 정의만 넘기는 것이므로 데이터 권한은 따로 필요합니다.

## 정리

- Comparison View는 필터링된 두 객체 집합을 같은 차트에 나란히 놓고 비교합니다.
- 비교 대상은 저장된 탐색, 해당 타입의 전체 객체, 또는 동적 필터링으로 새로 정의한 집합 중에서 고릅니다.
- 검색창이나 차트에서 거는 필터는 두 집합에 함께 적용됩니다.
- 비교 보기는 저장, 공유, 검색이 가능하지만, 공유받은 사람도 데이터 자체에 대한 권한이 있어야 내용을 볼 수 있습니다.
