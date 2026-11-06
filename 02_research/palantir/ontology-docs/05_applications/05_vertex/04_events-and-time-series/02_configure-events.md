# 이벤트 구성하기 (Configure events)

- 원문: https://www.palantir.com/docs/foundry/vertex/configure-events/
- 사이드바 위치: Applications > Vertex > Events and time series > Configure events

이 페이지는 Vertex에서 이벤트를 사용하기 위해 이벤트 객체 타입에 어떤 설정을 추가해야 하는지 설명합니다. 핵심은 타입 클래스(type class)라는 메타데이터를 속성에 붙여 이벤트의 색과 심각도를 정하는 것입니다.

<a id="event-configuration"></a>
## 이벤트 구성 (Event configuration)

Vertex에서 이벤트를 사용하려면 시계열 이벤트(time series event) 객체 타입을 만들고, 경보의 색 또는 심각도를 정하는 Vertex 타입 클래스 하나를 추가합니다(어느 열에 붙여도 되지만 보통 기본 키(primary key)에 붙입니다).

* 주황색: `kind`: `vertex`, `name`: `event_intent.warning`
* 빨간색: `kind`: `vertex`, `name`: `event_intent.danger`
* 파란색: `kind`: `vertex`, `name`: `event_intent.primary`
* 초록색: `kind`: `vertex`, `name`: `event_intent.success`

이 타입 클래스들은 Ontology Manager에서 이벤트 객체의 **Capabilities** 탭에서 구성하거나, 객체 속성(property)의 타입 클래스에서 직접 구성할 수 있습니다.

![Capabilities 탭](https://www.palantir.com/docs/resources/foundry/vertex/optional_ontology_config-event.jpg)

**설명**: 타입 클래스는 속성에 붙이는 `kind`와 `name` 쌍으로 된 꼬리표입니다. 속성의 데이터 타입(문자열, 정수 등)을 바꾸지는 않고, 특정 애플리케이션이 그 속성을 어떻게 해석할지 알려 주는 메타데이터 역할을 합니다. 예를 들어 Flight Delay 객체 타입의 기본 키 속성 `delay_id`에 `kind=vertex`, `name=event_intent.danger`를 붙이면, Vertex는 이 객체 타입의 이벤트를 빨간색 경보로 표시합니다.

## 정리

- Vertex에서 이벤트를 쓰려면 시계열 이벤트 객체 타입을 만들고 Vertex 타입 클래스 하나를 추가합니다.
- 타입 클래스의 `name` 값(`event_intent.warning`, `danger`, `primary`, `success`)에 따라 주황, 빨강, 파랑, 초록으로 표시됩니다.
- 타입 클래스는 보통 기본 키 속성에 붙이며, **Capabilities** 탭이나 속성의 타입 클래스 설정에서 구성합니다.
