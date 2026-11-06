# 시나리오 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/vertex/scenarios-getting-started/
- 사이드바 위치: Applications > Vertex > Scenarios > Getting started

이 페이지는 Vertex에서 시나리오를 실제로 만들고 실행하는 순서를 설명합니다. 시나리오에 액션을 추가하는 방법, (지원 종료 예정인) 모델 선택 방법, 입력과 출력 파라미터를 고르는 방법, 실행하고 입력 값을 재정의(override)해 "만약 ~라면" 사례 연구를 쌓아 가는 방법이 차례로 나옵니다.

[시나리오](01_scenarios-overview.md)를 사용하면 시스템에 "만약 ~라면?(What if?)" 질문을 던져 서로 다른 조건이나 의사결정 경로가 미치는 영향을 이해할 수 있습니다. Vertex는 Foundry 안에서 작성, 게시, 오케스트레이션된 기존 모델을 활용해, 시스템 전반의 모델링된 상호작용을 시각화하고 핵심 파라미터를 선택적으로 재정의하는 인터페이스를 제공합니다. 이를 통해 최적의 출력에 도달하기 위해 취할 수 있는 대안 액션을 파악할 수 있습니다.

<a id="add-actions"></a>
## 액션 추가하기 (Add Actions)

미리 구성된 액션으로 온톨로지의 객체를 수정했을 때 로컬 시스템과 전체 시스템에 어떤 영향이 있을지 테스트할 수 있습니다.

<a id="select-actions"></a>
### 액션 선택하기 (Select Actions)

액션을 추가하려면 먼저 **Add scenario** 버튼을 선택합니다. 그러면 액션을 추가할 수 있는 새 시나리오가 만들어집니다. 시나리오를 선택하고 **Add Action** 버튼을 선택하면 시나리오 섹션을 펼칠 수 있습니다.

![액션 추가](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-12.jpg)

추가할 액션을 고른 다음에는 액션의 파라미터를 갱신하고 **Submit을** 선택해 이 액션을 시나리오 안에 저장해야 합니다.

![액션 구성](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-13.jpg)

그런 다음 이 시나리오를 실행하고 만든 액션의 효과를 볼 수 있습니다.

액션을 더 추가할 수도 있고, 시나리오에 모델을 추가해 시스템에 대한 효과를 더 시뮬레이션할 수도 있습니다.

**설명**: 시나리오 안에서 액션을 **Submit** 한다고 해서 실제 온톨로지 데이터가 바로 바뀌는 것은 아닙니다. 원문은 이를 "시나리오 안에 저장"한다고 표현합니다. 즉 시나리오는 실제 데이터 위에 "이 액션들을 적용했다고 가정한" 가상의 변경 목록을 쌓아 두고, 실행할 때 그 가정 아래에서 결과를 계산하는 방식입니다. 데이터베이스의 트랜잭션을 커밋하지 않은 상태에서 결과를 미리 확인하는 것과 대응되는 개념입니다.

> **중간 요약**: **Add scenario**로 시나리오를 만들고 **Add Action**으로 액션을 고른 뒤 파라미터를 채워 **Submit** 하면, 그 액션이 시나리오 안에 저장되어 실행 시 효과를 확인할 수 있습니다.

<a id="select-models"></a><a id="select-models-sunset"></a>
## 모델 선택하기 \[Sunset] (Select models)

**주의**: 지원 종료(Sunset). 아래에서 설명하는 모델 선택, 구성, 실행 과정은 개발 단계상 [지원 종료(sunset)](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으며 향후 사용 중단(deprecated)될 예정입니다. 현재는 완전한 지원이 유지됩니다. Vertex 시나리오에서 모델을 계속 사용하려면 [모델에 대한 함수를 구성](https://www.palantir.com/docs/foundry/model-integration/functions-on-models/)하고, [그 함수를 가져와(import)](../../../02_define-ontologies/04_functions/14_models/01_functions-on-models.md) [함수 기반 액션(function-backed Action)](../../../02_define-ontologies/03_action-types/11_function-backed-actions/02_function-actions-getting-started.md)에 넣은 다음, [위에 나온 안내](#add-actions)를 따르는 것을 권장합니다.

Foundry 안에서 게시되고 [Modeling Objectives](https://www.palantir.com/docs/foundry/model-integration/objectives/)를 통해 온톨로지에 바인딩된 기존 모델이나 함수 중에서 선택할 수 있습니다. Vertex 안에서는 시나리오 사례 연구(case study)를 만들어 로컬 프로세스를 조사하고 이해하며, 개별 변경이 로컬 시스템과 연결된 시스템에 어떤 영향을 줄지 정량화할 수 있습니다.

<a id="new-model-selection"></a>
### 새 모델 선택 (New model selection)

새 조사를 시작하려면 게시된 모델 중 아무것이나 선택할 수 있습니다. **Add new model을** 선택하고 해당 프로세스에 관련된 모델을 검색합니다.

![모델 선택](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-1.jpg)

그러면 선택한 모델이 시나리오 창에 추가되며, 새 사례 연구를 시작하기 위해 올바른 모델 버전과 구성 버전을 선택할 수 있습니다.

![모델 버전과 구성 버전](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-2.jpg)

<a id="default-model-selection"></a>
### 기본 모델 선택 (Default model selection)

기존 시스템이나 프로세스를 탐색할 때는 권장되는 미리 구성된 기본 모델로 시나리오를 실행하도록 선택할 수 있습니다.

![기본 모델](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-3.jpg)

그러면 관련 모델들이 시나리오 창에 추가되며, 새 사례 연구를 시작하기 위해 올바른 모델 버전과 구성 버전을 선택할 수 있습니다.

[시나리오에 구성할 수 있는 옵션에 대해 더 알아보세요.](03_scenarios-options.md)

> **중간 요약**: 모델을 직접 시나리오에 추가하는 방식(새 모델 선택, 기본 모델 선택)은 지원 종료 예정이며, 앞으로는 모델을 함수로 감싸 함수 기반 액션으로 만든 뒤 액션 추가 방식으로 쓰는 것이 권장됩니다.

<a id="select-inputoutput-parameters"></a>
## 입력/출력 파라미터 선택하기 (Select input/output parameters)

모델을 선택하면 입력 또는 출력 파라미터로 사용되는 속성(property)이 객체 선택 패널에 표시됩니다.

**+ Add input or output** 옵션을 사용해 시나리오 표에 표시할 파라미터를 추가할 수 있습니다. 여기서 개별 시계열, 객체 속성, 측정값(measure)을 시나리오에 추가하도록 선택할 수 있습니다. 이 옵션은 선택한 모델에 대해 구성된 입력과 출력이 나열된 검색 및 선택 상자를 엽니다. 미리 구성된 **Add all parameters를** 기본으로 선택할 수도 있습니다. 선택한 파라미터는 모두 시나리오 표에 표시되며, 파라미터가 입력이라면 시나리오를 실행하기 전에 시나리오 표에서 값을 직접 편집해 재정의할 수 있습니다.

![파라미터 추가](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-7.jpg)

![파라미터 추가 2](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-8.jpg)

<a id="run-a-scenario"></a>
## 시나리오 실행하기 (Run a scenario)

파라미터를 추가하면 입력에는 파라미터의 현재 값이 표시되며, 시계열 파라미터의 경우 현재 선택된 시각의 값이 사용됩니다. **Run을** 선택하면 표시된 입력 값을 바탕으로 모델링된 출력을 계산하는 시나리오가 생성됩니다. 완료되면 시나리오에 초록색 체크 표시와 출력을 생성하는 데 걸린 시간이 표시됩니다.

![기준 시뮬레이션](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-9.jpg)

> **중간 요약**: **+ Add input or output**으로 시나리오 표에 보여 줄 입력과 출력을 고르고, **Run**으로 현재 입력 값 기준의 출력을 계산합니다.

<a id="build-your-what-if-case-study"></a>
## "만약 ~라면" 사례 연구 만들기 (Build your "what if" case study)

가능한 해결책을 시험하기 위해 사례 연구를 만들고 "만약 ~라면" 시나리오를 반복해 볼 수 있습니다.

재정의할 파라미터를 선택하고 새로운 시뮬레이션 입력을 넣어 재정의 조건을 입력합니다. 그러면 재정의된 칸이 강조 표시됩니다.

![재정의](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-10.jpg)

재정의 값으로 시나리오를 실행하면 새로 계산된 출력이 표시되어, 앞서 실행한 기준(baseline) 시나리오와 비교할 수 있습니다. 서로 다른 시나리오 실행을 계속 추가해 최적의 출력을 조사할 수 있습니다.

시뮬레이션된 값은 객체 노드의 확장 라벨에 추가된 판독값(readout)에 비교 형태로 표시됩니다.

하나의 사례 연구를 마치면 시나리오 창 위쪽에서 그 이름을 바꿀 수 있습니다. 같은 시스템에서 서로 다른 조건을 조사하기 위해 여러 사례 연구를 만들 수도 있습니다. 개별 시나리오의 이름을 바꿔 관련된 액션을 더 잘 나타내게 할 수도 있습니다.

![사례 연구 이름 바꾸기](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-11.jpg)

**설명**: 기준 시나리오와 재정의 시나리오의 관계를 예시 데이터로 보면 다음과 같습니다.

| 시나리오 | 입력: 펌프 회전수 | 출력: 탱크 수위 |
|---|---|---|
| 기준(재정의 없음) | 1500 rpm (현재 값) | 72% |
| 시나리오 1 | 1800 rpm (재정의) | 81% |
| 시나리오 2 | 1200 rpm (재정의) | 63% |

숫자는 설명을 위한 가상의 값입니다. 입력 하나만 바꾸고 나머지는 그대로 둔 채 출력을 비교하므로, 그 입력의 변화가 출력에 미치는 영향을 분리해서 볼 수 있습니다.

> **중간 요약**: 입력 파라미터를 재정의하고 다시 실행하면 기준 시나리오와 비교한 출력이 계산되며, 여러 실행을 묶은 사례 연구와 개별 시나리오에 이름을 붙여 관리할 수 있습니다.

<a id="chained-models"></a>
## 연쇄 모델 (Chained models)

[연쇄 모델을 구성하는 방법을 알아보세요.](04_chained-models.md)

## 정리

- **Add scenario**로 시나리오를 만들고, 액션을 추가해 파라미터를 채우고 **Submit** 하면 시나리오 안에 저장됩니다.
- 모델을 직접 선택하는 방식은 지원 종료 예정이므로, 모델을 함수 기반 액션으로 감싸 쓰는 방식이 권장됩니다.
- **+ Add input or output**으로 시나리오 표의 파라미터를 고르고, **Run**으로 출력을 계산합니다.
- 입력을 재정의해 여러 번 실행하면 기준 시나리오와 비교하며 "만약 ~라면" 사례 연구를 만들 수 있습니다.
