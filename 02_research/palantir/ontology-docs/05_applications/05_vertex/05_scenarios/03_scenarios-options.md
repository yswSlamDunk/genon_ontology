# 시나리오 옵션 (Scenario options)

- 원문: https://www.palantir.com/docs/foundry/vertex/scenarios-options/
- 사이드바 위치: Applications > Vertex > Scenarios > Scenario options

이 페이지는 Vertex 시나리오를 실행할 때 조정할 수 있는 옵션(시간 창, 시계열 평활화, 범위, 기준 시나리오 실행)과 입력/출력 파라미터 선택 방법을 설명합니다.

<a id="time-window-selection"></a>
### 시간 창 선택 (Time window selection)

시나리오를 실행할 시간 창을 지정할 수 있습니다. 시나리오 범위에 들어가는 객체에 대해 알려진 데이터가 있는 시간을 선택해야 합니다.

![시간 창](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-4.jpg)

<a id="advanced-options"></a>
### 고급 옵션 (Advanced options)

정해진 기간(분 단위)에 걸친 시계열 평활화(smoothing)를 구성할 수 있습니다.

![고급 옵션](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-5.jpg)

**설명**: 시계열 평활화는 짧은 기간의 들쭉날쭉한 변동을 줄이기 위해 일정 기간의 값을 묶어 계산하는 처리입니다. 대표적인 방법은 이동 평균으로, 예를 들어 기간을 3분으로 두면 09:03의 값으로 09:01\~09:03 세 값의 평균을 쓰는 식입니다. Vertex가 구체적으로 어떤 평활화 방법을 쓰는지는 원문에 나와 있지 않습니다.

<a id="scope"></a>
### 범위 (Scope)

객체 기반 시스템 그래프(System Graph)에서는 시나리오의 범위를 그래프에 표시된 객체로만 한정하도록 설정해, 사용할 수 있는 입력/출력 파라미터를 제한할 수 있습니다.

![범위 설정](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-6.jpg)

<a id="run-baseline-scenario"></a>
### 기준 시나리오 실행 (Run baseline scenario)

액션이나 재정의(override)를 포함한 시나리오를 실행할 때마다 추가로 기준(baseline) 시나리오를 실행할지 선택할 수 있습니다. 이 기준 시나리오는 선택한 모델을 액션이나 재정의 없이 실행하므로, 다른 시나리오와 비교할 기준선을 제공하고 액션의 영향을 더 잘 판단할 수 있게 해 줍니다.

<a id="select-inputoutput-parameters"></a>
## 입력/출력 파라미터 선택하기 (Select input/output parameters)

모델을 선택하면 입력 또는 출력 파라미터로 사용되는 속성(property)이 객체 선택 패널에 표시됩니다.

**+ Add input or output** 옵션을 사용해 시나리오 표에 표시할 파라미터를 추가할 수 있습니다. 여기서 개별 시계열, 객체 속성, 측정값(measure)을 시나리오에 추가하도록 선택할 수 있습니다. 이 동작은 선택한 모델에 대해 구성된 입력과 출력이 나열된 검색 및 선택 상자를 엽니다. 미리 구성된 **Add all parameters를** 기본으로 선택할 수도 있습니다. 선택한 파라미터는 모두 시나리오 표에 표시됩니다. 파라미터가 입력이라면 시나리오를 실행하기 전에 시나리오 표에서 값을 직접 편집해 재정의할 수 있습니다.

![파라미터 추가](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-7.jpg)

![파라미터 추가 2](https://www.palantir.com/docs/resources/foundry/vertex/simulate-system-8.jpg)

## 정리

- 시나리오는 데이터가 있는 시간 창을 지정해 실행해야 합니다.
- 고급 옵션에서 분 단위 시계열 평활화를 설정할 수 있고, 범위를 그래프에 보이는 객체로 한정할 수 있습니다.
- 액션이나 재정의가 있는 시나리오를 실행할 때 기준 시나리오를 함께 실행해 비교 기준선을 얻을 수 있습니다.
- **+ Add input or output**으로 시나리오 표에 보일 입력과 출력을 고르고, 입력은 실행 전에 재정의할 수 있습니다.
