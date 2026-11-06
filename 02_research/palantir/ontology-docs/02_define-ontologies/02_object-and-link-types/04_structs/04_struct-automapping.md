# 구조체 타입 자동 매핑 (Automapping struct types)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/struct-automapping/
- 사이드바 위치: Define Ontologies > Object and link types > Structs > Automapping struct types

이 페이지는 구조체(struct) 속성(property)의 필드를 데이터소스의 열에 하나씩 손으로 연결하지 않고 한 번에 자동으로 연결하는 방법을 설명합니다. 객체 타입이 이미 있을 때는 Ontology Manager에서, 아직 없을 때는 Pipeline Builder의 객체 타입 생성 마법사에서 자동 매핑을 할 수 있습니다.

자동 매핑(automapping)을 사용하면 열을 하나씩 수동으로 매핑하는 대신 모든 열을 자동으로 매핑할 수 있습니다.

**설명**: 구조체 속성은 여러 필드(예: `street`, `city`, `zip`)를 하나로 묶은 속성입니다. 백킹 데이터소스(backing datasource)의 구조체 열 안에 들어 있는 하위 필드를 온톨로지 쪽 구조체 필드에 연결하는 작업이 "매핑"입니다. 필드가 많으면 하나씩 지정하기 번거로우므로, 이름과 타입을 기준으로 한꺼번에 연결해 주는 기능이 자동 매핑입니다.

<a id="automap-struct-types-in-ontology-manager"></a>
## Ontology Manager에서 구조체 타입 자동 매핑하기

객체가 이미 생성되어 있다면 **Automap all**(모두 자동 매핑) 기능을 사용해 모든 열을 자동으로 매핑할 수 있습니다.

1. Ontology Manager에서 **Properties** 탭으로 들어가 원하는 속성을 선택합니다.
2. **Column mapping** 탭에서 원하는 열을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/automap-struct-oma.png" alt="'Column mapping' 탭과 'Automap all' 버튼." width="500" />

3. **Automap all**을 선택합니다.

<a id="automap-struct-types-in-pipeline-builder"></a>
## Pipeline Builder에서 구조체 타입 자동 매핑하기

객체가 아직 생성되지 않았다면, 객체 타입 생성 마법사로 처음 객체를 만들 때 자동 매핑을 할 수 있습니다.

1. Pipeline Builder 파이프라인에서 해당 데이터셋을 열고 오른쪽 위의 **All Actions** 드롭다운을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/automap-struct-pipelinebuilder.png" alt="데이터셋 상세 페이지의 All actions 드롭다운." width="500" />

2. **Create object type**을 선택해 새 객체를 만듭니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/automap-struct-properties.png" alt="'Create a new object' 대화 상자의 Properties 탭." width="500" />

3. **Properties** 아래에서 매핑할 속성을 추가합니다.
4. **Next**를 선택하고 나머지 단계를 마쳐 자동 매핑된 객체 타입을 만듭니다.

## 정리

- 자동 매핑은 구조체 속성의 필드를 데이터소스 열에 한꺼번에 연결하는 기능입니다.
- 객체 타입이 이미 있으면 Ontology Manager의 **Column mapping** 탭에서 **Automap all**을 누릅니다.
- 객체 타입이 아직 없으면 Pipeline Builder의 **All Actions** 에서 **Create object type** 마법사를 실행하면서 자동 매핑합니다.
