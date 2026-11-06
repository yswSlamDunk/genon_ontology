# 시계열 Foundry Rules 배포 (Deploy time series Foundry Rules)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/deploy-timeseries-foundry-rules/
- 사이드바 위치: Applications > Foundry Rules > Time series > Deploy time series Foundry Rules

이 페이지는 이미 배포한 Foundry Rules 워크플로에서 시계열 규칙 기능을 켜는 추가 설정을 설명합니다. 시계열 데이터가 시계열 속성으로 구성되었는지 측정값으로 구성되었는지에 따라 필요한 단계가 달라집니다.

이 지침은 플랫폼에 시계열이 이미 설정되어 있다고 가정합니다. [Foundry에서 시계열 사용하기](https://www.palantir.com/docs/foundry/time-series/time-series-usage/)에 대해 더 알아보세요.

Foundry Rules에서 시계열 기능을 활성화하려면 먼저 [Foundry Rules 배포](../03_deploy/01_deploy-foundry-rules.md) 단계를 따릅니다. Foundry Rules를 배포한 뒤 시계열 지원을 활성화하려면 아래 단계가 필요합니다.

1. 시계열 규칙을 만들려면 워크플로 입력 중 하나가 시계열 루트 객체 타입(time series root object type)이어야 합니다. 시계열 규칙을 작성하려는 모든 입력 객체 타입에 대해 **Enable time series** 스위치를 켭니다. <br><br>
   ![객체 타입을 시계열 규칙의 입력으로 사용하도록 하는 스위치](https://www.palantir.com/docs/resources/foundry/foundry-rules/enable-timeseries-on-object.png) <br><br>

2. 시계열 데이터가 [시계열 속성(time series property)](https://www.palantir.com/docs/foundry/time-series/time-series-setup/)으로 설정되어 있다면 추가 구성 단계 없이 바로 시계열 기반 규칙 작성을 시작할 수 있습니다. 그러나 시계열 데이터가 측정값(measure)으로 구성되어 있다면 다음 단계를 완료해야 합니다.

* **enable time series** 스위치를 켜면 **Series object type**에서 **Root object type**으로 가는 링크를 선택하라는 대화 상자가 열립니다.
* 그다음 트랜스폼 구성 섹션에서 이 측정값들을 백킹하는 [시계열 동기화(time series sync)](https://www.palantir.com/docs/foundry/time-series/time-series-syncs/)를 *모두* 추가해야 합니다. <br><br>
  ![시계열 동기화를 추가하는 선택기](https://www.palantir.com/docs/resources/foundry/foundry-rules/add-a-time-series-sync.png) <br><br>

**설명**: 루트 객체 타입은 시계열이 "누구의" 데이터인지를 나타내는 객체 타입입니다(예: Pump). 시계열 속성 방식에서는 Pump 객체의 속성 하나가 곧 시계열을 가리키므로 추가 연결 정보가 필요 없습니다. 측정값 방식에서는 시계열마다 별도의 Series 객체(예: "P-1 온도 센서")가 있고 이것이 Pump에 링크로 연결되어 있으므로, 어떤 링크를 따라 루트 객체로 가는지 지정하고, 실제 시계열 값을 제공하는 시계열 동기화도 파이프라인에 알려 주어야 합니다.

## 정리

- 시계열 규칙을 쓰려면 먼저 일반 Foundry Rules를 배포하고, 시계열 루트 객체 타입을 워크플로 입력으로 두어야 합니다.
- 시계열 규칙을 쓸 입력 객체 타입마다 **Enable time series** 스위치를 켭니다.
- 시계열 속성 방식이면 추가 구성이 필요 없습니다.
- 측정값 방식이면 Series 객체 타입에서 Root 객체 타입으로 가는 링크를 선택하고, 측정값을 백킹하는 시계열 동기화를 트랜스폼 구성에 모두 추가해야 합니다.
