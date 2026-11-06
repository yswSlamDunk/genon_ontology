# 활용 사례 (Example use cases)

- 원문: https://www.palantir.com/docs/foundry/vertex/example-use-cases/
- 사이드바 위치: Applications > Vertex > Example use cases

이 페이지는 Vertex를 조직에서 실제로 어떻게 쓸 수 있는지 두 가지 사례로 보여 줍니다. 하나는 객체 기반의 공정 흐름도와 시스템 그래프를 그리는 것이고, 다른 하나는 그 그래프 위에서 "만약 이렇게 바꾸면?" 같은 시뮬레이션을 돌려 의사 결정을 비교하는 것입니다.

이 페이지는 조직에서 Vertex를 사용할 수 있는 몇 가지 예를 설명합니다.

<a id="point-and-click-process-flow-diagramming-beta"></a>
## 클릭 방식의 프로세스 흐름 다이어그램 작성 \[베타] (Point-and-click process flow diagramming \[Beta])

**참고**: 베타(Beta). Vertex의 다이어그램 작성 기능은 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며 사용자의 환경(enrollment)에서는 사용할 수 없을 수도 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다. 이 기능을 사용하려면 플랫폼 관리자에게 Control Panel에서 Vertex 설정을 수정해 달라고 요청하세요.

* 조직의 성과를 극대화하는 조건을 시험할 수 있는, 운영 전반을 동적으로 통합한 디지털 트윈을 만듭니다.
* 원자재 가공과 설비 조정부터 생산과 공급망 관리까지 모든 유형의 워크플로에 대해 객체 기반 시스템 그래프나 생산 다이어그램(production diagram)을 빠르게 구성합니다.
* 모델링한 객체와 프로세스 사이에 미리 정의된 관계를 활용해 시스템 전반의 자재 흐름과 이벤트를 시각화합니다.
* 핵심 속성(property), 지표, 측정값을 기준으로 객체 그래프나 다이어그램을 구성하고 스타일을 지정해 시스템 시각화를 목적에 맞게 조정합니다.

**설명**: "객체 기반(object-backed)"은 그림 속 도형 하나하나가 온톨로지의 실제 객체에 연결되어 있다는 뜻입니다. 예를 들어 생산 다이어그램의 "Mixer 2" 상자는 Equipment 객체 하나에 대응하고, 상자의 색이나 표시 숫자는 그 객체의 속성 값(예: `temperature = 85`)에서 옵니다. 데이터가 바뀌면 그림도 그에 맞춰 바뀝니다. 그림과 데이터를 따로 관리하는 일반 도식 도구와의 차이가 여기에 있습니다.

**생산 다이어그램:**

![생산 다이어그램](https://www.palantir.com/docs/resources/foundry/vertex/vertex_use_cases-production_diagram.jpg)

*이 스크린샷은 가상의 데이터를 사용합니다.*

**시스템 그래프:**

![시스템 그래프](https://www.palantir.com/docs/resources/foundry/vertex/vertex_use_cases-system_graph.jpg)

*이 스크린샷은 가상의 데이터를 사용합니다.*

<a id="simulation-dynamic-analysis-and-decision-optimization"></a>
## 시뮬레이션, 동적 분석, 의사 결정 최적화 (Simulation, dynamic analysis, and decision optimization)

Vertex를 사용하면 Foundry에 게시된 모든 모델, 예측(forecast), 비즈니스 로직과 통합해 디지털 트윈과 상호 작용하고 이를 분석할 수 있습니다.

* 전체 네트워크에 걸쳐 "what-if(만약 ~라면)" 분석과 시뮬레이션을 실행해, 시스템에 영향을 주는 의사 결정, 이벤트, 잠재적 변경의 결과를 이해하고 비교합니다.
* 시뮬레이션을 구성하고 실행해, 모델링한 세계에 제안된 변경이 미치는 영향을 정확하게 정량화하는 데 필요한 실제 맥락을 적용합니다.
* 디지털 트윈 전반의 프로세스와 시스템을 연결해 운영상, 데이터상의 사일로를 허물고 조직 전반에서 여러 분야에 걸친 새로운 혁신을 이끌어 냅니다.

**설명**: what-if 분석은 입력 값 일부를 가정으로 바꾼 뒤 모델을 다시 계산해 결과를 비교하는 방법입니다. 예를 들어 "설비 A의 처리 속도를 시간당 100개에서 120개로 올리면 하루 생산량은 어떻게 되는가"를 계산할 때, 실제 데이터는 그대로 두고 가정한 값으로만 함수나 모델을 실행해 현재 결과와 나란히 비교합니다.

## 정리

- Vertex의 첫 번째 활용 사례는 온톨로지 객체에 연결된 시스템 그래프와 생산 다이어그램을 클릭만으로 구성하는 것입니다(다이어그램 기능은 베타).
- 그래프의 스타일은 객체의 속성, 지표, 측정값에 따라 바뀌므로 데이터 변화가 그림에 반영됩니다.
- 두 번째 활용 사례는 Foundry의 모델, 예측, 비즈니스 로직을 연결해 what-if 시뮬레이션을 실행하고 결정의 영향을 정량적으로 비교하는 것입니다.
