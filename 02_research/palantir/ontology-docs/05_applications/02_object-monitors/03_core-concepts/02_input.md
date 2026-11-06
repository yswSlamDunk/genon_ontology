# 입력 (Inputs)

- 원문: https://www.palantir.com/docs/foundry/object-monitors/input/
- 사이드바 위치: Applications > Object Monitors [Sunset] > Core concepts > Inputs

이 페이지는 객체 모니터가 무엇을 감시할지 정하는 입력(input)을 설명합니다. 입력은 객체 집합(object set)이며, Object Explorer에서 저장한 탐색으로 만듭니다. 입력을 어디서 확인할 수 있는지도 함께 다룹니다.

**주의**: 단계적 종료(Sunset). Object Monitors는 [Automate](https://www.palantir.com/docs/foundry/automate/overview/)로 대체되었습니다. Automate는 이전 버전과 완전히 호환되는 제품으로, 플랫폼의 모든 비즈니스 자동화를 위한 단일 진입점을 제공합니다.

모니터 입력은 [객체 집합(object set)](https://www.palantir.com/docs/foundry/analytics/datasets-object-sets/#object-sets)으로 정의합니다. 그러면 모니터 [조건](03_condition.md)이 입력의 속성을 참조할 수 있습니다. 입력은 집계 같은 지표를 계산하는 데 쓰일 수도 있고, 그 입력에 객체가 추가되거나 제거되는 시점을 감시하는 데 쓰일 수도 있습니다.

**설명**: 같은 입력을 두 가지 방식으로 쓸 수 있습니다. 입력이 "지연된 항공편" 객체 집합이라면, (1) 지표 방식은 `COUNT(*)`나 평균 지연 시간 같은 집계 값을 계산해 기준과 비교하고, (2) 추가/제거 방식은 어제 집합에 없던 항공편 객체가 오늘 새로 들어왔는지를 확인합니다.

입력 객체 집합은 [Object Explorer](../../01_object-explorer/04_analyze-and-compare/06_save-explorations.md)에서 **저장된 탐색(saved exploration)을** 만들어 생성합니다. 저장된 탐색은 [Object Explorer에서 직접](../02_create_new_object_monitor.md#create-from-object-explorer) 모니터 입력으로 추가하거나, [Object Monitors 애플리케이션에서](../02_create_new_object_monitor.md#create-from-object-monitors-application) 새 모니터를 구성할 때 추가할 수 있습니다.

Object Monitors 애플리케이션에서 객체 모니터를 볼 때 모니터 입력은 개요 섹션에 표시됩니다. 모니터를 클릭하면 개요 패널이 열립니다.

![Object Monitors 앱에서 입력 보기](https://www.palantir.com/docs/resources/foundry/object-monitors/input_shown_in_management_app.png)

Object Explorer에서 특정 저장된 탐색을 볼 때는, 그 탐색을 입력으로 사용하는 객체 모니터가 화면 오른쪽 위의 **Monitor** 팝오버에 표시됩니다.

![Object Explorer에서 저장된 탐색을 사용하는 모니터 목록](https://www.palantir.com/docs/resources/foundry/object-monitors/list_of_monitors_for_exploration.png)

## 정리

- 모니터 입력은 객체 집합이며, Object Explorer의 저장된 탐색으로 만듭니다.
- 입력은 집계 지표 계산에 쓰이거나, 객체가 추가되고 제거되는 것을 감시하는 데 쓰입니다.
- 입력은 Object Monitors 애플리케이션의 모니터 개요 패널에서, 또는 Object Explorer의 **Monitor** 팝오버에서 확인할 수 있습니다.
