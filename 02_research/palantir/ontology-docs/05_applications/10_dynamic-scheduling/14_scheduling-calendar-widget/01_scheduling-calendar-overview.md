# Scheduling Calendar 위젯 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-calendar-overview/
- 사이드바 위치: Applications > Dynamic Scheduling > Scheduling Calendar widget > Overview

이 페이지는 객체를 날짜나 타임스탬프 속성에 따라 달력 형태로 보여 주는 Workshop 위젯인 Scheduling Calendar를 소개합니다. 간트 차트처럼 자원별 행으로 나누지 않고 일, 주, 월 단위 달력에 이벤트를 배치하므로 예약, 마감일, 근무 교대처럼 날짜 중심의 데이터를 보기에 적합합니다.

<a id="scheduling-calendar-widget"></a>
## Scheduling Calendar 위젯 (Scheduling Calendar widget)

Scheduling Calendar는 객체를 날짜(date) 또는 타임스탬프(timestamp) 속성(property)에 따라 표시하는 데 사용할 수 있는 Workshop 위젯입니다. 사용자는 데이터를 일, 주, 월 단위로 볼 수 있으며, Schedule 객체를 변경해야 할 때를 위해 드래그 앤 드롭 기능을 활성화할 수도 있습니다.

Scheduling Calendar 위젯이 유용한 사용 사례의 예는 다음과 같습니다.

* 약속이나 회의 일정 잡기.
* 작업과 마일스톤 마감일 추적.
* 직원 근무 교대 배정 보기.

![주간 보기로 이벤트를 표시하는 달력 위젯 예시](https://www.palantir.com/docs/resources/foundry/dynamic-scheduling/calendar_weekly_view.png)

**설명**: 위젯이 객체를 달력에 놓으려면 각 객체가 시작 시각(과 보통 종료 시각) 속성을 가져야 합니다. 예를 들어 `Meeting` 객체 타입에 `start_time = 2026-11-03 10:00`, `end_time = 2026-11-03 11:00`인 객체가 있으면, 주간 보기의 11월 3일 칸 10시\~11시 위치에 퍽 하나가 그려집니다.

## 정리

- Scheduling Calendar는 날짜나 타임스탬프 속성을 기준으로 객체를 달력에 표시하는 Workshop 위젯입니다.
- 일, 주, 월 단위 보기를 제공하고, 필요하면 드래그 앤 드롭으로 일정을 바꿀 수 있습니다.
- 회의 예약, 마감일 추적, 근무 교대 확인 같은 날짜 중심 워크플로에 적합합니다.
