# 연쇄 모델 구성하기 \[Sunset] (Configure chained models)

- 원문: https://www.palantir.com/docs/foundry/vertex/chained-models/
- 사이드바 위치: Applications > Vertex > Scenarios > Configure chained models [Sunset]

이 페이지는 Vertex 시나리오에서 여러 모델을 연쇄(chain)시켜 한 모델의 출력을 다음 모델의 입력으로 전달하는 방법을 설명합니다. 이 기능은 지원 종료 단계에 있으므로, 함수 기반 액션으로 옮겨 가는 권장 경로도 함께 안내합니다.

**주의**: 지원 종료(Sunset). Vertex의 모델 연쇄는 개발 단계상 [지원 종료(sunset)](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으며 향후 사용 중단(deprecated)될 예정입니다. 현재는 완전한 지원이 유지됩니다. Vertex 시나리오에서 모델을 계속 사용하려면 [모델에 대한 함수를 구성](https://www.palantir.com/docs/foundry/model-integration/model-functions-guide/)하고 [그 함수를 가져와(import)](../../../02_define-ontologies/04_functions/14_models/01_functions-on-models.md) [함수 기반 액션(function-backed Action)](../../../02_define-ontologies/03_action-types/11_function-backed-actions/02_function-actions-getting-started.md)에 넣는 것을 권장합니다.

모델링된 세계 전반에서 시스템과 프로세스를 연결하기 시작하면, 시스템의 각 개별 요소가 전체적으로 어떻게 상호작용하는지 이해할 수 있어야 합니다. Vertex를 사용하면 연결된 모델들을 연쇄시켜 변경이 처음부터 끝까지 미치는 영향을 이해하고 정량화할 수 있으며, 이를 통해 최적의 의사결정을 내릴 수 있습니다.

사례 연구에 모델을 추가한 뒤에는 **+ Add New Model을** 선택해 관련된 다른 모델을 검색하고 선택할 수 있습니다. 어떤 모델 출력에 대해 생성된 값이 파라미터에 매핑되어 이후 모델의 입력으로 사용되면, 그 값은 해당 모델의 입력 값으로 전파됩니다. 이렇게 전파된 값은 입력 칸에 링크 아이콘으로 표시됩니다.

선택한 모델들은 시나리오 창에 추가되며, 여기서 사례 연구에 표시할 입력/출력 파라미터를 고를 수 있습니다. 파라미터는 표시된 모델마다 따로 선택합니다.

선택한 모델의 입력 중 어느 곳에든 재정의(override)를 추가하면, "만약 ~라면" 시뮬레이션을 실행할 때 연쇄된 모델에서 영향을 받는 입력이 표시되고, 해당 옵션이 켜져 있으면 기준(baseline) 시나리오도 실행됩니다.

**설명**: 연쇄의 동작 순서를 예시로 보면 다음과 같습니다. 모델 A의 출력 `flow_rate`가 모델 B의 입력 `inflow`에 매핑되어 있다고 합시다. (1) A를 실행해 `flow_rate=120`을 얻습니다. (2) 이 값이 B의 `inflow` 칸에 자동으로 채워지고 링크 아이콘이 붙습니다. (3) B를 실행해 최종 출력을 얻습니다. A의 입력을 재정의하면 `flow_rate`가 바뀌고, 그 변화가 B의 입력과 출력까지 이어집니다.

## 정리

- 모델 연쇄는 지원 종료 예정이며, 모델을 함수로 감싸 함수 기반 액션으로 쓰는 방식이 권장됩니다.
- **+ Add New Model**로 관련 모델을 추가하면, 앞 모델의 출력이 매핑된 파라미터를 통해 뒤 모델의 입력으로 전파되고 링크 아이콘으로 표시됩니다.
- 입력/출력 파라미터는 모델마다 따로 선택합니다.
- 어느 입력이든 재정의하면 연쇄된 모델 전체에 영향이 표시되며, 옵션에 따라 기준 시나리오도 실행됩니다.
