# 동적 스케줄링 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/dynamic-scheduling/scheduling-overview/
- 사이드바 위치: Applications > Dynamic Scheduling > Overview

이 페이지는 Palantir의 동적 스케줄링(dynamic scheduling) 기능이 무엇이고 어떤 문제를 풀기 위한 것인지 소개합니다. 일정(누가, 언제, 무엇을 하는가)과 자원 배정을 온톨로지 위에서 다루는 위젯들의 큰 그림과, 이 기능을 떠받치는 세 가지 원칙을 설명합니다.

<a id="dynamic-scheduling"></a>
## 동적 스케줄링 (Dynamic scheduling)

Palantir의 동적 스케줄링 기능을 사용하면 빌더가 조직의 현실적인 복잡성을 반영하고 조직의 구체적인 필요에 맞춘 스케줄링 및 자원 배정(resource allocation) 워크플로를 만들 수 있습니다.

예를 들어 Workshop의 [Scheduling Gantt Chart](05_scheduling-gantt-chart-widget.md) 위젯을 사용하면 사용자가 다음을 할 수 있는 대화형 일정 애플리케이션을 만들 수 있습니다.

* 일정과 그 제약 조건을 시각화합니다.
* 드래그 앤 드롭 인터페이스로 일정을 수정합니다.
* 스케줄링 추천을 찾습니다.
* 온톨로지 액션(Ontology Actions)을 실행합니다.

[Program Scheduling](13_program-scheduling-widget/01_program-scheduling-overview.md) 위젯은 프로그램, 프로젝트, 작업을 시간 순으로 보여 주는 화면을 제공합니다. 사용자는 이를 통해 여러 업무 흐름(workstream)의 진행 상황을 추적하고, 작업 간 의존 관계를 시각화하고, 이후 산출물에 영향을 줄 수 있는 방해 요소(blocker)를 찾아낼 수 있습니다.

**설명**: 간트 차트(Gantt chart)는 가로축을 시간, 세로축을 작업이나 자원으로 두고 각 작업을 시작 시각부터 종료 시각까지의 가로 막대로 그리는 차트입니다. 예를 들어 "정비사 김씨" 행에 09:00\~11:00 막대가 있으면 김씨가 그 시간에 어떤 작업에 배정되어 있다는 뜻입니다.

이러한 동적 스케줄링 기능으로 사용자는 다음과 같은 다양한 과제를 해결할 수 있습니다.

* 시간에 따라 변하는 우선순위와 제약 조건 사이의 균형을 맞추도록 직원 일정을 최적화합니다.
* 머신러닝 기반의 실시간 해결책으로 운송 및 물류 네트워크가 장애에 대한 회복력을 갖추게 합니다.
* 생산 계획과 스케줄링을 개선하여 제조 산출량을 효율적으로 늘립니다.

동적 스케줄링은 세 가지 원칙에 기반합니다.

* [Foundry 온톨로지(Ontology)를 활용해 자원을 모델링합니다.](04_scheduling-ontology-primitives.md)
* [자원의 조건과 제약을 코드로 명시합니다.](05_scheduling-gantt-chart-widget.md)
* [자원과 제약 사이의 관계와 상호 의존성을 모델링합니다.](09_scheduling-validation-rules.md)

Palantir의 동적 스케줄링 기능은 이 원칙들을 실제로 구현합니다. 동적 스케줄링의 [핵심 개념](03_scheduling-concepts.md)에 대해 더 알아보세요.

**설명**: "제약을 코드로 명시한다(codify)"는 것은 "한 정비사는 같은 시간에 두 작업을 할 수 없다" 같은 규칙을 사람이 머릿속으로만 확인하지 않고, 함수(function)로 작성해 시스템이 자동으로 검사하게 만든다는 뜻입니다.

## 정리

- 동적 스케줄링은 일정과 자원 배정 워크플로를 온톨로지 위에서 만드는 기능 묶음입니다.
- 대표 도구는 Workshop의 Scheduling Gantt Chart 위젯(드래그 앤 드롭 편집, 추천, 액션 실행)과 Program Scheduling 위젯(프로그램, 프로젝트, 작업의 시간 순 보기)입니다.
- 직원 일정 최적화, 물류 회복력, 제조 계획 같은 문제에 쓰입니다.
- 세 원칙은 온톨로지로 자원 모델링, 조건과 제약의 코드화, 자원과 제약 간 관계 모델링입니다.
