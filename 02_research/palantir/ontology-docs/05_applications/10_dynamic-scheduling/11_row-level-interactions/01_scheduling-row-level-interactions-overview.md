# 행 수준 상호작용 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-row-level-interactions-overview/
- 사이드바 위치: Applications > Dynamic Scheduling > Row-level interactions > Overview

이 페이지는 Scheduling Gantt 차트의 각 행(Resource 객체)에서 사용자가 할 수 있는 상호작용을 소개합니다. 행은 기술자, 차량, 승무원처럼 일정이 배정되는 대상을 나타내며, 행 수준 상호작용을 설정하면 화면에서 바로 그 대상의 속성을 바꾸거나 새 객체를 만들 수 있습니다.

<a id="row-level-interactions"></a>
## 행 수준 상호작용 (Row-level interactions)

Scheduling Gantt 차트의 각 행은 하나의 `Resource` 객체를 나타냅니다. 예를 들어 `Resource`는 다음을 나타낼 수 있습니다.

* 작업 배정을 위한 기술자
* 정비 일정이 잡히는 차량
* 운행에 배정되는 승무원

행 수준 상호작용을 사용하면 사용자가 행 객체의 특정 속성(property)을 수정하거나, 객체를 만들거나, Workshop 모듈에서 이벤트를 발생시킬 수 있습니다.

![행 수준 상호작용 예시.](https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/row-level-interactions.gif)

**설명**: 행은 Resource 객체 하나에 대응하므로, 행 수준 상호작용의 대상은 기본적으로 그 Resource 객체입니다. 예를 들어 기술자 행에서 "휴가 등록" 메뉴를 실행하면 그 기술자 객체가 액션의 입력으로 들어가는 식입니다. 구체적인 설정 방법은 다음 페이지에서 다룹니다.

## 정리

- Scheduling Gantt 차트의 각 행은 Resource 객체 하나(기술자, 차량, 승무원 등)를 나타냅니다.
- 행 수준 상호작용으로 행 객체의 속성을 수정하거나, 객체를 만들거나, Workshop 이벤트를 발생시킬 수 있습니다.
