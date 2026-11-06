# 스케줄 레이어 수준 상호작용 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-schedule-layer-level-interactions/
- 사이드바 위치: Applications > Dynamic Scheduling > Schedule layer-level interactions > Overview

이 페이지는 Scheduling Gantt 차트에서 퍽(일정 객체)이 그려지는 스케줄 레이어마다 따로 상호작용을 정의할 수 있다는 점을 소개합니다. 드래그해서 새 일정 만들기, 퍽을 끌어 옮기기 같은 구체적인 기능은 이 섹션의 다음 페이지들에서 다룹니다.

<a id="schedule-layer-level-interactions"></a>
## 스케줄 레이어 수준 상호작용 (Schedule layer-level interactions)

스케줄 레이어는 시각적으로 구성할 수 있을 뿐 아니라, 레이어마다 고유한 상호작용 집합을 가질 수 있습니다. 같은 객체 타입을 여러 스케줄 레이어에서 사용할 수 있으므로, 매우 구체적인 상호작용 정의를 만들 수 있다는 뜻입니다. 스케줄 레이어 수준 상호작용을 사용하면 사용자가 Schedule 객체의 특정 속성(property)을 수정하거나, 새 Schedule 객체를 만들거나, Workshop 모듈에서 이벤트를 발생시킬 수 있습니다. 드래그 앤 드롭 동작과 그 세밀도(granularity)도 맞춤 설정할 수 있습니다. 이 옵션들은 **Input Data (Pucks)** 아래 각 스케줄 레이어 구성의 **Drag & Drop** 및 **Interactions** 하위 섹션에 정리되어 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/row-level-interactions.gif" alt="스케줄 레이어 수준 상호작용 예시." >

**설명**: "같은 객체 타입을 여러 레이어에서 쓴다"는 것은, 예를 들어 정비 작업 객체 타입을 "확정된 작업" 레이어와 "미확정 작업" 레이어로 나눠 그릴 수 있다는 뜻입니다. 이때 확정 레이어에는 드래그 앤 드롭을 막고, 미확정 레이어에만 허용하는 식으로 레이어별로 다른 상호작용을 줄 수 있습니다.

## 정리

- 스케줄 레이어마다 고유한 상호작용을 정의할 수 있고, 같은 객체 타입도 레이어별로 다르게 동작하게 할 수 있습니다.
- 상호작용으로 Schedule 객체 속성 수정, 새 Schedule 객체 생성, Workshop 이벤트 실행, 드래그 앤 드롭 동작과 세밀도 설정이 가능합니다.
- 설정 위치는 **Input Data (Pucks)** 아래 각 레이어의 **Drag & Drop**과 **Interactions** 하위 섹션입니다.
