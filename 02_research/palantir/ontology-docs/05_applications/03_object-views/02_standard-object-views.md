# 표준 Object View (Standard Object Views)

- 원문: https://www.palantir.com/docs/foundry/object-views/standard-object-views/
- 사이드바 위치: Applications > Object Views > Standard Object Views

이 페이지는 객체 타입을 만들면 Foundry가 자동으로 생성하는 표준 Object View의 화면 구성과 동작을 설명합니다. 속성의 메타데이터(prominent, normal, hidden)와 기본 타입(base type)이 화면 표시 방식을 어떻게 결정하는지, 그리고 링크된 객체를 탐색하는 컴포넌트가 무엇을 할 수 있는지를 다룹니다.

온톨로지에서 [객체 타입](../../02_define-ontologies/02_object-and-link-types/02_object-types/01_object-types-overview.md)을 만들고 구성하면, Foundry는 그 객체 타입의 모든 객체를 표준화된 방식으로 보여 주는 표준 Object View를 자동으로 만듭니다. 이를 통해 다른 사용자도 객체 타입의 스키마와 링크를 전체적으로 이해할 수 있습니다. 표준 Object View는 객체 타입의 구성을 그대로 따릅니다. 중요(prominent) 속성은 전용 표에 강조해 보여 주거나, 속성의 [기본 타입(base type)](../../02_define-ontologies/02_object-and-link-types/03_properties/09_base-types.md)이 시계열(time series), 미디어 참조(media reference), 지리공간(geospatial) 속성이면 다른 시각적 형식으로 보여 줍니다. 일반(normal) 속성은 일반 표에 표시되고, 숨김(hidden) 속성은 보이지 않습니다.

표준 Object View는 모든 객체 타입에서 사용할 수 있지만, 온톨로지에서 해당 객체 타입이 하는 역할에 맞춰 맥락화되고 엄선된 Object View 경험을 제공하려면 어떤 객체 타입이든 [구성형 뷰](06_full-object-views/02_config-object-views.md)를 만들 수 있습니다. 구성형 Object View를 만들면 Foundry는 그것을 사용자의 기본 뷰로 제공합니다. 하지만 사용자는 표준 뷰를 선택해 객체 데이터를 표준 형식으로 볼 수도 있습니다.

**설명**: 속성마다 "얼마나 눈에 띄게 보여 줄지"를 정하는 메타데이터가 있습니다. 예를 들어 `Aircraft` 객체 타입에 `tail_number`(prominent), `model`(normal), `internal_audit_code`(hidden) 세 속성이 있다면, 표준 Object View는 `tail_number`를 상단에 크게, `model`을 아래 일반 표에 표시하고, `internal_audit_code`는 표시하지 않습니다. 별도로 화면을 설계하지 않아도 객체 타입 정의만으로 화면 배치가 결정된다는 점이 표준 뷰의 특징입니다.

> **중간 요약**: 표준 Object View는 객체 타입 구성에서 자동으로 만들어지며, 속성 메타데이터(prominent, normal, hidden)와 기본 타입에 따라 표시 방식이 정해집니다. 구성형 뷰를 만들어도 표준 뷰로 전환할 수 있습니다.

<a id="prominent-property-displays"></a>
## 중요 속성 표시 (Prominent property displays)

Foundry는 [중요(prominent) 속성](../../02_define-ontologies/02_object-and-link-types/03_properties/05_property-metadata.md#metadata-reference)을 표준 Object View 상단에 보여 주어, 객체의 가장 중요한 정보를 바로 파악할 수 있게 합니다.

<a id="display-behavior"></a>
### 표시 동작 (Display behavior)

중요로 표시된 속성은 타입에 따라 강화된 시각적 처리를 받습니다.

* **[미디어 참조 속성](../../02_define-ontologies/02_object-and-link-types/03_properties/09_base-types.md#media-references):** 지원되는 모든 미디어 유형을 볼 수 있는 전용 미디어 뷰어로 렌더링됩니다.
* **[시계열 속성](https://www.palantir.com/docs/foundry/time-series/time-series-properties/):** 시간에 따른 데이터 패턴을 보여 주는 대화형 차트로 표시됩니다.
* **[지리공간 속성](https://www.palantir.com/docs/foundry/geospatial/ontology/):** 중요 속성으로 geohash, geoshape, 또는 지리시간 시계열 참조(geotemporal series reference, GTSR) 속성을 가진 객체는 [Map](../08_map/01_overview.md)에 렌더링됩니다. [시간에 따른 객체의 위도와 경도를 나타내는](../08_map/07_integrate-data-for-the-map/01_integrate-objects.md#track-objects) 시계열 속성도 Map에 표시됩니다.
* **기타 속성 타입:** 그 밖의 모든 중요 속성은 더 큰 카드 형식으로, 나머지 표준 속성을 보여 주는 표 위에 올려 표시됩니다.

**설명**: 같은 "중요" 표시라도 값의 타입에 따라 화면 위젯이 달라집니다. 이미지 파일을 가리키는 미디어 참조 값은 뷰어로, `(시각, 값)` 쌍이 이어지는 시계열 값은 선 그래프로, 위치 값은 지도로, 문자열이나 숫자 같은 일반 값은 큰 카드로 보입니다. 즉 프로그래밍에서 값의 타입에 따라 다른 렌더링 함수를 호출하는 분기 처리가 자동으로 이루어진다고 이해하면 됩니다.

> **중간 요약**: 중요 속성은 화면 상단에 표시되며, 미디어는 뷰어, 시계열은 차트, 지리공간은 지도, 나머지는 큰 카드로 렌더링됩니다.

<a id="linked-objects-component"></a>
## 링크된 객체 컴포넌트 (Linked objects component)

**Linked objects** 컴포넌트를 사용하면 표준 Object View 안에서 바로 [링크된 객체](../../02_define-ontologies/02_object-and-link-types/06_link-types/01_link-types-overview.md)를 따라 이동할 수 있습니다.

![Linked objects 컴포넌트.](https://www.palantir.com/docs/resources/foundry/object-views/linked-objects-component.png)

표준 Object View의 **Linked objects** 컴포넌트로 다음을 할 수 있습니다.

* 링크된 객체를 링크 타입별로 묶어서 봅니다.
* 현재 뷰를 벗어나지 않고 링크된 객체의 속성을 인라인으로 미리 봅니다.
* 링크된 객체의 일부를 새 탭에서 열어 추가로 탐색합니다.
* 선택한 링크된 객체를 표준 Object View의 측면 패널에서 미리 봅니다.

**설명**: 링크 타입은 데이터베이스의 외래 키 관계에 대응합니다. 예를 들어 `Aircraft` 객체 하나를 열었을 때 "이 항공기가 운항한 Flight" 링크와 "이 항공기의 Maintenance Event" 링크가 있다면, Linked objects 컴포넌트는 두 그룹으로 나눠 각각 연결된 객체를 보여 줍니다. SQL로 `SELECT * FROM flights WHERE aircraft_id = 'A1'`을 실행한 결과를 화면에서 바로 펼쳐 보는 것과 같은 동작입니다.

> **중간 요약**: Linked objects 컴포넌트는 링크된 객체를 링크 타입별로 묶어 보여 주고, 인라인 미리보기, 새 탭 열기, 측면 패널 미리보기를 지원합니다.

<a id="panel-standard-object-view-display-behavior"></a>
## 패널 표준 Object View의 표시 동작 (Panel standard Object View display behavior)

표준 Object View의 모든 기능은 [패널](07_panel-object-views/02_config-panel-views.md) 형태에서도 사용할 수 있습니다.

![표준 Object View 패널.](https://www.palantir.com/docs/resources/foundry/object-views/core-object-view-panel.png)

## 정리

- 객체 타입을 만들면 Foundry가 표준 Object View를 자동으로 생성합니다.
- 속성 메타데이터에 따라 prominent는 상단 강조, normal은 일반 표, hidden은 비표시로 처리됩니다.
- 중요 속성은 기본 타입에 따라 미디어 뷰어, 시계열 차트, 지도, 큰 카드로 렌더링됩니다.
- Linked objects 컴포넌트로 링크된 객체를 링크 타입별로 탐색하고 미리 볼 수 있습니다.
- 구성형 뷰가 있어도 표준 뷰로 전환할 수 있고, 표준 뷰의 기능은 패널 형태에서도 동일하게 쓸 수 있습니다.
