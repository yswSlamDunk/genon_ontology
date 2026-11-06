# 단계구분도 (Choropleths)

- 원문: https://www.palantir.com/docs/foundry/map/visualize-choropleths/
- 사이드바 위치: Applications > Map > Visualize Ontology data > Choropleths

이 페이지는 단계구분도(choropleth) 디스플레이를 설명합니다. 단계구분도는 객체를 지역 단위로 묶고, 각 지역에 속한 객체들의 집계 값(합계, 평균 등)으로 지역 폴리곤에 색을 칠하는 지도입니다. 객체 수가 너무 많아 하나하나 점으로 찍으면 의미를 읽기 어려울 때, 지역별 패턴을 보여 주는 데 씁니다.

단계구분도 지도는 각 지역 안의 모든 객체에 대해 계산한 집계 값으로 지역에 색을 칠해 보여 줍니다. 단계구분도는 큰 데이터셋의 공간적 패턴을 시각화하는 데 유용합니다. 이 예시 지도는 교통사고 객체 3,100만 개로 만든 단계구분도로, 미국의 각 주를 그 주에서 발생한 사고의 평균 심각도로 칠했습니다.

![미국 주별 교통사고 심각도를 보여 주는 단계구분도.](https://www.palantir.com/docs/resources/foundry/map/choropleth-traffic-severity.png)

단계구분도를 설정하려면 집계를 계산할 객체를 지도에 추가하고, **Styling** 패널의 **Add display** 메뉴에서 단계구분도 스타일러(choropleth styler)를 추가합니다.

![디스플레이 메뉴의 단계구분도 추가 옵션.](https://www.palantir.com/docs/resources/foundry/map/choropleth-add-display.png)

그다음 객체를 지역으로 묶는 방법과 각 지역을 표시하는 방법을 지정해야 합니다. 단계구분도의 지역은 [폴리곤 디스플레이](03_visualize-polygons-lines.md)와 같은 스타일 옵션을 가지며, 유일한 차이는 모든 값이 각 지역 안의 모든 객체에 대해 계산한 집계를 바탕으로 한다는 점입니다.

**설명**: 단계구분도는 SQL의 `GROUP BY`와 집계 함수를 지도에 그린 결과입니다. 위 교통사고 예시는 `SELECT state, AVG(severity) FROM accidents GROUP BY state`의 결과 행 하나하나를 주 경계 폴리곤 하나로 그리고, `AVG(severity)` 값으로 색을 칠한 것입니다.

<a id="grouping-objects-into-regions"></a>
## 객체를 지역으로 묶기 (Grouping objects into regions)

단계구분도 스타일의 **Regions** 섹션에서는 객체를 지역으로 묶는 방법을 지정하며, 각 지역은 지도에서 하나의 폴리곤으로 표시됩니다. Map 애플리케이션이 지원하는 경계 식별자(boundary identifier) 타입을 가진 속성(property)으로 묶거나, 레이어의 객체에 링크된 객체 타입으로 묶을 수 있습니다.

<a id="group-by-boundary-identifiers"></a>
### 경계 식별자로 묶기 (Group by boundary identifiers)

Map 애플리케이션은 몇 가지 흔한 식별자 타입이 설정된 객체에 대해 단계구분도를 그릴 수 있습니다. 이런 경계 타입의 폴리곤 지오메트리는 Map 애플리케이션에 내장되어 있으므로, 데이터에 이미 이런 식별자 타입이 붙어 있다면 데이터 통합이 더 쉬워집니다.

Map이 지원하는 식별자 타입의 예는 다음과 같습니다.

* ISO 3166 국가 코드
* 미국 주 약어(CA, TX, OR, …)
* 미국 카운티 FIPS 코드

지원되는 식별자의 전체 목록과, 지도에서 사용하도록 속성 타입이 식별자를 참조하게 설정하는 방법은 [지도용 온톨로지 객체](../07_integrate-data-for-the-map/01_integrate-objects.md#boundary-identifiers) 페이지를 참고하세요.

경계 식별자를 설정하려면 **Group by** 드롭다운 메뉴에서 **Property** 옵션을 선택한 다음, **Property** 드롭다운 메뉴에서 식별자가 설정된 속성 중 하나를 고릅니다. 온톨로지에서 경계 식별자로 설정된 속성만 표시됩니다.

경계 속성을 선택하고 나면, 스타일용 집계를 계산할 때 그 속성 값이 같은 객체들이 모두 하나로 묶입니다.

**설명**: 예를 들어 `Accident` 객체에 `state` 속성이 있고 값이 `CA`, `TX` 같은 미국 주 약어라면, 이 속성을 경계 식별자로 설정해 두기만 하면 됩니다. 주 경계 도형은 Map에 내장되어 있으므로 `CA` 값을 가진 사고들은 캘리포니아 폴리곤 하나로 묶여 표시됩니다.

<a id="group-by-linked-objects"></a>
### 링크된 객체로 묶기 (Group by linked objects)

지역의 지오메트리를 직접 제공해야 한다면, 온톨로지 링크를 선택해 객체를 묶을 수 있습니다. 그러면 Map 애플리케이션은 같은 객체에 링크된 객체들을 하나로 묶습니다. 사용자 지정 지역 지오메트리를 위한 [온톨로지 설정을 알아보세요](../07_integrate-data-for-the-map/01_integrate-objects.md#linked-objects).

**설명**: 예를 들어 `Trail`(등산로) 객체가 `RangerDistrict`(관리 구역) 객체에 링크되어 있고 `RangerDistrict`에 구역 경계를 담은 지오셰이프 속성이 있다면, 같은 `RangerDistrict`에 링크된 등산로들이 한 지역으로 묶이고 그 구역의 폴리곤에 색이 칠해집니다. 링크 타입이 외래 키 역할을 하고, 묶는 기준은 `GROUP BY ranger_district_id`가 됩니다.

> **중간 요약**: 단계구분도는 Map 내장 경계 식별자(국가 코드, 미국 주 약어, 카운티 FIPS 코드 등)를 가진 속성으로 묶거나, 자체 지오메트리를 가진 객체에 대한 링크로 객체를 지역별로 묶습니다.

<a id="styling-by-aggregation"></a>
## 집계로 스타일 지정하기 (Styling by aggregation)

단계구분도에서는 각 지역이 그 안의 객체에 대해 계산한 집계로 칠해지므로 값 기반 스타일이 다르게 동작합니다. 단계구분도의 집계를 정의하는 방법은 **표준(standard)과** **표현식(expression)** 두 가지입니다.

<a id="standard-aggregations"></a>
### 표준 집계 (Standard aggregations)

표준 집계는 지역 안 객체들의 속성 하나에 대한 집계를 간단히 정의하는 방법입니다. 표준 집계를 설정하려면 **Property** 메뉴를 열고 사용할 속성과 집계 함수(sum, mean, max, min)를 선택합니다.

![표준 집계 설정.](https://www.palantir.com/docs/resources/foundry/map/choropleth-standard-aggregation.png)

<a id="expression-aggregations"></a>
## 표현식 집계 (Expression aggregations)

표현식 집계를 사용하면 지역 안의 객체에 대해 사용자 지정 집계를 정의할 수 있습니다. 표현식 참조(expression reference)를 여러 개 추가해 표현식 집계를 만들며, 목록의 마지막 참조가 지역을 칠하는 데 쓰일 값을 제공합니다. 각 참조는 다음 중 하나가 될 수 있습니다.

* 한 지역으로 묶인 객체들의 속성에 대한 단순 집계
* 지역 자체의 속성(링크된 객체로 묶을 때만 사용 가능)
* 다른 두 참조를 결합하는 연산

예를 들어 이 지도는 표현식 집계를 사용해 미국 산림청(US Forest Service) 관리 구역(Ranger District)을 구역별 등산로 밀도로 칠했습니다.

![미국 산림청 관리 구역별 등산로 밀도를 보여 주는 단계구분도.](https://www.palantir.com/docs/resources/foundry/map/choropleth-trail-density.png)

등산로 밀도를 계산하는 데 세 개의 표현식을 사용합니다.

* 첫 번째는 각 미국 산림청 관리 구역 안 등산로의 총길이를 계산합니다.
* 두 번째는 지역의 총면적을 참조합니다.
* 세 번째는 첫 번째 참조를 두 번째 참조로 나눠 에이커당 평균 등산로 길이를 계산하는 연산입니다.

**설명**: SQL로 쓰면 `SUM(trail.length) / district.area`를 구역별로 계산한 것입니다. 첫 번째 참조는 묶인 객체(`Trail`)의 집계, 두 번째는 지역 객체(`RangerDistrict`)의 속성, 세 번째는 둘을 나누는 연산이며, 마지막인 세 번째 참조의 값이 색을 결정합니다.

## 정리

- 단계구분도는 객체를 지역으로 묶고, 지역별 집계 값으로 지역 폴리곤을 칠하는 디스플레이입니다.
- 지역은 Map 내장 경계 식별자를 가진 속성이나, 자체 지오메트리를 가진 객체로의 링크로 정합니다.
- 표준 집계는 속성 하나에 sum, mean, max, min을 적용하고, 표현식 집계는 여러 참조(객체 집계, 지역 속성, 연산)를 이어 마지막 참조 값으로 색을 정합니다.
- 나머지 스타일 옵션은 폴리곤 디스플레이와 같습니다.
