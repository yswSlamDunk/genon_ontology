# 임시 시나리오 (Temporary scenarios)

- 원문: https://www.palantir.com/docs/foundry/ontology/temporary-scenario/
- 사이드바 위치: Ontology scenarios > Temporary scenarios

이 페이지는 현재 세션 안에서만 존재하는 임시 시나리오(temporary scenario)를 설명하고, Workshop에서 임시 시나리오를 지원하는 간단한 애플리케이션을 단계별로 만드는 튜토리얼을 제공합니다. 튜토리얼을 따라가면 시나리오를 만드는 위젯, 시나리오 데이터를 보여 주는 테이블과 차트, 시나리오에 액션을 적용하는 버튼이 어떻게 서로 연결되는지 알 수 있습니다.

임시 시나리오는 현재 세션 안에서만 생성되고 사용됩니다. 그 메타데이터는 플랫폼에 영속적으로 저장되지 않으며, 사용자가 현재 세션을 끝내면(예: Workshop에서) 삭제됩니다. 이런 시나리오는 결과를 공동 작업하거나 공유할 필요가 없는, 빠르고 즉석적인 "what-if" 분석에 유용합니다. 임시 시나리오를 사용하면 온톨로지 상태에 영향을 주지 않고, 저장된 불필요한 시나리오로 작업 공간을 어지럽히지도 않으면서 여러 액션을 실험할 수 있습니다.

**설명**: "메타데이터가 영속적으로 저장되지 않는다"는 것은 시나리오의 존재 자체(이름, 그 안에 적용된 편집 목록 등)가 서버의 저장소에 기록되지 않고 브라우저 세션의 메모리에만 있다는 뜻입니다. 예를 들어 Workshop 탭을 닫으면 그 시나리오와 편집이 모두 사라집니다. 반대로 영속 시나리오(persisted scenario)는 객체로 저장되어 나중에 다시 열거나 다른 사람과 공유할 수 있습니다.

<a id="workshop-tutorial"></a>
## Workshop 튜토리얼 (Workshop tutorial)

이 튜토리얼에서는 임시 시나리오를 지원하는 기본 [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/) 애플리케이션을 만드는 과정을 단계별로 살펴봅니다.

<a id="part-i-add-the-scenario-manager-widget"></a>
### 1부: Scenario Manager 위젯 추가 (Part I: Add the Scenario Manager widget)

1. 새로운 빈 Workshop 모듈에서 왼쪽 탐색 영역의 **Settings** 패널로 이동해, **Advanced Functionalities** 섹션에서 **Scenarios**와 **Scenarios V2** 설정이 활성화되어 있는지 확인합니다. <br><br>
   ![Advanced Functionalities 섹션에서 Scenarios 토글이 활성화된 Workshop Settings 패널.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-settings-advanced-functionalities.png) <br><br>
2. 사이드바 섹션에 **[Scenario Manager](https://www.palantir.com/docs/foundry/workshop/widgets-scenario-manager/)** 위젯을 추가합니다. 이 위젯은 Workshop의 시나리오 전용 위젯 중 하나로, 모듈 전체에서 사용할 임시 시나리오를 만들고 관리하는 데 쓰입니다. <br><br>
   ![Scenario Manager, Scenario Selector, Scenario Summary 등 시나리오 전용 위젯이 보이는 Workshop 위젯 검색 패널.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-scenario-manager-search.png) <br><br>
3. 오른쪽의 위젯 설정 패널에서 **Dynamic scenarios** 필드가 새 동적 시나리오(dynamic scenario)를 사용하도록 설정합니다. 그러면 위젯 가운데에 **Create** 버튼이 나타납니다. <br><br>
   ![Dynamic scenario 변수로 설정되어 가운데에 Create 버튼이 보이는 Scenario Manager 위젯.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-scenario-manager-dynamic-variable.png) <br><br>

**설명**: Workshop에서 위젯끼리는 변수(variable)를 통해 값을 주고받습니다. Scenario Manager 위젯은 "생성된 시나리오들의 배열" 변수와 "현재 활성 시나리오" 변수를 출력하고, 다른 위젯들은 이 변수를 입력으로 받아 시나리오 데이터를 표시하거나 시나리오에 액션을 적용합니다. 이후 단계는 모두 이 변수들을 다른 위젯에 연결하는 작업입니다.

<a id="part-ii-add-an-object-table-widget"></a>
### 2부: Object Table 위젯 추가 (Part II: Add an Object Table widget)

1. 모듈 본문에 **Object Table** 위젯을 추가합니다. <br><br>
   ![Object Table 위젯 옵션이 보이는 Workshop 위젯 검색 패널.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-object-table-search.png) <br><br>

2. 테이블을 채우는 데는 어떤 객체 집합(object set)이든 사용할 수 있지만, 이미 연결된 [액션](../02_define-ontologies/03_action-types/01_overview.md)이 하나 이상 설정된 객체 타입으로 시작하는 것을 권장합니다. <br><br>
   ![객체 집합과 속성이 선택된 Object Table 위젯 설정.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-object-table-object-set-config.png) <br><br>

3. 이제 테이블에 표시할 속성(property)을 몇 개 추가합니다.

4. 속성 아래에서 이 위젯에 **Load Data from Scenario**(시나리오에서 데이터 불러오기) 옵션을 활성화합니다. 이 옵션은 사실상 Object Table 위젯이 시나리오를 인식하도록(scenario-aware) 만듭니다.

5. Scenario Manager 위젯이 생성한 시나리오 배열 변수를 선택합니다. 그러면 Object Table 위젯의 데이터는 원래의 온톨로지가 아니라 Scenario Manager 위젯의 시나리오에 가해진 수정 사항을 반영하게 됩니다. <br><br>
   ![Load Data from Scenario 토글이 보이는 Object Table 위젯 설정.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-object-table-load-from-scenario.png) <br><br>

<a id="part-iii-add-the-scenario-summary-widget"></a>
### 3부: Scenario Summary 위젯 추가 (Part III: Add the Scenario Summary widget)

1. 시나리오에 적용할 변경 사항을 미리 보려면 모듈에 **Scenario Summary** 위젯을 추가합니다.

2. 위젯 설정에서 Scenario Manager 위젯이 생성한 활성 시나리오(active scenario) 변수에 연결합니다. <br><br>
   ![Scenario Manager 위젯의 Active scenario 변수에 연결된 Scenario Summary 위젯 설정.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-scenario-summary-config.png) <br><br>
   이 시점에서는 아직 시나리오에 어떤 수정도 적용되지 않았으므로 데이터는 동일해야 합니다.

> **중간 요약**: 모듈 설정에서 Scenarios 기능을 켜고, Scenario Manager 위젯으로 시나리오를 만들 수 있게 한 뒤, Object Table의 Load Data from Scenario 옵션과 Scenario Summary 위젯을 Scenario Manager의 변수에 연결해 시나리오 데이터와 변경 내역을 보여 줍니다.

<a id="part-iv-configure-an-action"></a>
### 4부: 액션 설정 (Part IV: Configure an action)

1. 시나리오에 적용할 액션을 설정하기 위해 **Button Group** 위젯을 추가합니다. <br><br>
   ![Button group 위젯이 보이는 Workshop 위젯 검색 패널.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-button-group-search.png) <br><br>

2. 테이블에 있는 객체 타입을 수정하는 액션을 선택합니다.

3. 이 액션을 온톨로지 대신 시나리오에 적용하려면 **Apply to Scenario**(시나리오에 적용) 옵션을 활성화하고 메뉴에서 활성 시나리오 변수를 선택합니다. <br><br>
   ![Apply to Scenario 옵션이 활성화되고 활성 시나리오 변수가 선택된 Button group 위젯 설정.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-button-group-apply-to-scenario.png) <br><br>

4. 새로 설정한 액션을 사용해 테이블에 있는 아무 객체의 속성을 새 값으로 바꿔 봅니다.

5. 액션을 적용하기 전에 Scenario Manager 위젯에서 **Create**를 선택해 새 시나리오를 만듭니다. <br><br>
   ![Scenario Manager에 Scenario 1이 생성되고 Object table에 항공편 데이터가 표시된 Workshop 애플리케이션.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-module-scenario-created.png) <br><br>

아래 예시에서는 테이블에 있는 항공편 하나의 `Year`를 업데이트합니다. Object Table 위젯이 새 데이터로 새로 고쳐지는 것을 볼 수 있습니다. <br><br>
![Apply to Scenario 버튼과 항공편 속성 필드가 보이는 Edit Flight Demo 대화 상자.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-action-apply-to-scenario.png) <br><br>
Scenario Summary 위젯에는 데이터 변경을 나타내는 기록이 나타납니다. 이 액션은 온톨로지에 적용되지 *않았으며* 시나리오 안에만 존재합니다. <br><br>
![Apply to Scenario 버튼과 항공편 속성 필드가 보이는 Edit Flight Demo 대화 상자.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-action-apply-to-scenario.png) <br><br>

**설명**: 예를 들어 항공편 F100의 `Year`가 원래 2019였고 시나리오 안에서 2020으로 바꿨다면, Object Table(시나리오 데이터를 불러오도록 설정됨)에는 2020이 보이고 Scenario Summary에는 "F100: Year 2019에서 2020으로 변경" 같은 기록이 남습니다. 같은 객체를 Object Explorer 같은 다른 곳에서 열면 여전히 2019입니다. (원문에서는 이 단락 앞뒤에 같은 이미지가 두 번 실려 있어 그대로 옮겼습니다.)

<a id="part-v-add-a-chart-widget"></a>
### 5부: 차트 위젯 추가 (Part V: Add a chart widget)

1. 결과를 더 잘 시각화하기 위해 테이블 위에 섹션을 추가하고 **Chart: XY** 위젯을 넣습니다. <br><br>
   ![Chart: XY 위젯 옵션이 보이는 Workshop 위젯 검색 패널.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-chart-xy-search.png) <br><br>

Chart: XY 위젯은 시나리오를 개수 제한 없이 지원하며, 서로 다른 시나리오를 서로 다른 레이어(layer)에 설정할 수 있습니다. <br><br>
![Compare Against Scenarios 옵션이 활성화되고 Dynamic scenarios 변수가 지정된 Chart: XY 위젯 설정.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-chart-xy-compare-scenario-config.png) <br><br>
2\. 다양한 레이어 타입을 살펴보면서 여러 시나리오가 각각 어떻게 시각화되는지 확인해 봅니다.

3. **Group By**와 기타 집계도 설정할 수 있으며, 이들은 시나리오 값을 올바르게 반영합니다. <br><br>
   ![출발 공항별로 그룹화된 막대 차트를 보여 주는 Chart: XY 위젯이 있는 Workshop 애플리케이션.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-chart-xy-result.png) <br><br>

<a id="part-vi-add-a-metric-card-widget"></a>
### 6부: Metric Card 위젯 추가 (Part VI: Add a Metric Card widget)

1. 지표 카드(metric card)의 값도 시나리오로부터 채울 수 있습니다. 새 **Metric Card** 위젯을 추가합니다. <br><br>
   ![Metric Card 위젯 옵션이 보이는 Workshop 위젯 검색 패널.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-metric-card-search.png) <br><br>
2. 본래 시나리오를 인식하지 않는 위젯에서도 시나리오로부터 변수 값을 구성해 사용할 수 있습니다. 예를 들어 Metric Card 위젯에는 명시적인 시나리오 설정 섹션이 없습니다. 대신 Metric Card 설정에서 새 숫자 지표(numeric metric)를 만들고, 그 값을 새 객체 집합 집계 변수(object set aggregation variable)로 정의합니다. <br><br>
   ![Metric Card 위젯에서 값을 설정하는 Workshop 위젯 화면.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-metric-card-value-config.png) <br><br>
   변수 설정 창에 있는 **Scenario** 섹션에서 시나리오 변수를 추가할 수 있습니다. 시나리오 변수를 선택하면 시나리오의 수정 사항이 적용된 상태로 집계가 실행됩니다. 마찬가지로 객체 속성 변수 설정도 시나리오를 지원합니다. <br><br>
   ![Scenario 설정 섹션이 있는 객체 집합 집계 변수를 보여 주는 Metric Card 설정.](https://www.palantir.com/docs/resources/foundry/ontology/temporary-scenario-metric-card-scenario-config.png) <br><br>

**설명**: 위젯 자체에 시나리오 옵션이 없더라도, 그 위젯에 값을 넘겨주는 변수 쪽에서 시나리오를 지정하면 됩니다. 예를 들어 "전체 항공편 수" 집계 변수에 시나리오를 지정하면, 시나리오 안에서 추가되거나 삭제된 항공편까지 반영된 개수가 Metric Card에 표시됩니다.

> **중간 요약**: Button Group의 Apply to Scenario 옵션으로 액션을 실제 온톨로지 대신 시나리오에 적용하고, Chart: XY 위젯으로 여러 시나리오를 레이어별로 비교합니다. 시나리오 옵션이 없는 Metric Card 같은 위젯은 집계 변수에 시나리오를 지정하는 방식으로 시나리오 값을 표시합니다.

<a id="next-steps"></a>
## 다음 단계 (Next steps)

첫 번째 시나리오를 만들었으니, 이 튜토리얼에서 사용한 시나리오 전용 Workshop 위젯들의 다양한 설정과 레이아웃을 실험해 보기를 권장합니다.

<a id="persist-temporary-scenario-metadata"></a>
## 임시 시나리오 메타데이터 영속화 (Persist temporary scenario metadata)

이 시나리오의 메타데이터를 영속적으로 저장하고 싶다고 판단되면 [영속 시나리오(persisted scenarios)](03_persisted-scenario.md) 문서의 안내를 따르세요.

## 정리

- 임시 시나리오는 현재 세션에만 존재하고, 세션이 끝나면 메타데이터와 편집이 함께 삭제됩니다.
- 공유나 협업이 필요 없는 빠른 what-if 분석에 적합합니다.
- Workshop에서는 Scenario Manager 위젯이 시나리오를 만들고, 그 출력 변수를 Object Table, Scenario Summary, Button Group, Chart: XY 등에 연결해 시나리오를 인식하게 합니다.
- Button Group의 Apply to Scenario 옵션을 켜면 액션 결과가 온톨로지가 아닌 시나리오에만 반영됩니다.
- 결과를 보존해야 하면 영속 시나리오로 전환합니다.
