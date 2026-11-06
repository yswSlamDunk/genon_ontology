# Foundry Rules 파이프라인 사용자 정의 (Customize Foundry Rules pipeline)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/customize-foundry-rules-pipeline/
- 사이드바 위치: Applications > Foundry Rules > Settings & customization > Customize Foundry Rules pipeline

이 페이지는 Foundry Rules가 자동으로 만들어 주는 규칙 실행 파이프라인 대신, 사용자가 직접 관리하는 코드 저장소에서 파이프라인을 실행하도록 바꾸는 방법을 설명합니다. 규칙 실행 시점 제어, 입력 전처리, 증분 처리 같은 고급 요구가 있을 때 쓰는 기능입니다.

**주의**: Foundry Rules 파이프라인 사용자 정의는 숙련된 Foundry 파이프라인 작성자를 위한 고급 기능입니다. 이 사용자 정의는 워크플로 관리자의 구현 및 유지 관리 부담을 늘릴 수 있습니다.

Foundry Rules는 기본적으로 사용자가 파이프라인 로직을 전혀 작성하지 않아도 됩니다. 하지만 일부 사용 사례에서는 다른 방법으로는 얻을 수 없는 결과를 얻기 위해 Foundry Rules 파이프라인을 사용자 정의해야 합니다.

<a id="use-cases"></a>
## 사용 사례 (Use cases)

Foundry Rules 파이프라인을 사용자 정의하면 다음과 같은 이점을 얻을 수 있습니다.

* 서로 다른 규칙 하위 집합을 어떻게, 언제 실행할지 세밀하게 제어할 수 있습니다.
* 규칙 로직을 실행하기 전에 Foundry Rules 입력을 전처리할 수 있습니다.
* [증분 트랜스폼(incremental transform)](https://www.palantir.com/docs/foundry/transforms-python/incremental-overview/) 안에서 Foundry Rules를 실행할 수 있습니다. 이를 위해서는 규칙 로직이 증분 데이터와 호환되어야 합니다.

Foundry Rules 출력의 후처리(예: 열 추가)는 별도의 하위(downstream) 트랜스폼으로 처리할 수 있습니다. Foundry Rules 출력의 후처리만을 위해 Foundry Rules 파이프라인을 사용자 정의하는 것은 권장하지 않습니다.

**설명**: 증분 트랜스폼은 매번 입력 전체를 다시 계산하지 않고, 지난 빌드 이후 새로 추가된 행만 처리하는 방식입니다. 예를 들어 거래 데이터가 하루 100만 행씩 쌓인다면 전체 재계산은 날마다 비용이 커지지만, 증분 방식은 새 100만 행만 규칙에 통과시킵니다. 다만 "지난 30일 합계"처럼 과거 행 전체가 필요한 집계 로직은 새 행만 봐서는 결과가 맞지 않으므로, 원문이 말하는 "증분 데이터와 호환되는 로직"이어야 한다는 조건이 붙습니다.

> **중간 요약**: 파이프라인 사용자 정의는 규칙 실행 제어, 입력 전처리, 증분 처리가 필요할 때 씁니다. 단순 후처리라면 하위 트랜스폼을 따로 두는 편이 권장됩니다.

<a id="instructions"></a>
## 절차 (Instructions)

**참고**: 사용자 정의 파이프라인은 현재 스트리밍 워크플로에서는 지원되지 않습니다.

자체 관리 트랜스폼(self-managed transforms)을 활성화하고, 사용자 정의 트랜스폼 저장소를 선택하고, Foundry Rules 워크플로를 저장한 다음, Foundry Rules 파이프라인 코드를 생성해 선택한 저장소에 저장하면 자체 Foundry Rules 파이프라인을 배포할 수 있습니다. 방법은 다음과 같습니다.

1. 톱니바퀴 아이콘을 클릭해 고급 설정 메뉴를 엽니다.

   <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/open_advanced_settings.png" alt="고급 설정을 여는 Foundry Rules 워크플로 구성 헤더의 버튼" width="800" />

2. **Enable self-managed transforms** 옵션을 켭니다.

   <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/enable_self_managed_transforms.png" alt="자체 관리 트랜스폼을 활성화하는 고급 설정의 버튼" width="500" />

3. **Transforms Configuration** 섹션에서 **Use a custom transform repository**를 클릭합니다. **Deploy a new repository**(권장)를 고르거나, **Select existing repository**를 선택해 원하는 저장소를 찾아 선택할 수 있습니다.

   <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/use_custom_transform_repository.png" alt="사용자 정의 트랜스폼 저장소를 사용하는 버튼" width="700" />

4. Foundry Rules 워크플로를 저장합니다.

5. **Generate**를 클릭한 다음 **copy**를 클릭해 Foundry Rules 파이프라인 코드를 생성하고 복사합니다.

   <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/generate_and_copy_buttons.png" alt="Foundry Rules 트랜스폼 코드를 생성하고 복사하는 버튼" width="500" />

6. 앞에서 기존 저장소를 골랐다면 `rules.transforms` 디렉터리 안에 `FoundryRulesTransform`이라는 파일을 만들고 복사한 코드를 붙여 넣습니다. 3단계에서 새로 배포한 저장소를 골랐다면 "FoundryRulesTransform"을 찾아 코드를 붙여 넣습니다.

**설명**: 이 절차의 결과로 규칙 실행 코드가 Foundry가 숨겨서 관리하는 파이프라인에서 여러분의 Code Repositories 저장소 안 파일로 옮겨집니다. 이후 그 파일을 직접 수정해 전처리 단계를 넣거나 규칙 일부만 실행하도록 바꿀 수 있지만, 워크플로 구성이 바뀌면 코드를 다시 생성해 반영하는 일도 관리자의 몫이 됩니다. 원문 첫머리의 주의 문단이 말하는 유지 관리 부담이 이것입니다.

> **중간 요약**: 고급 설정에서 자체 관리 트랜스폼을 켜고 저장소를 지정한 뒤, 생성된 코드를 저장소의 `FoundryRulesTransform` 파일에 붙여 넣으면 사용자 정의 파이프라인이 됩니다. 스트리밍 워크플로에는 쓸 수 없습니다.

## 정리

- 파이프라인 사용자 정의는 숙련자용 고급 기능이며 유지 관리 부담을 늘립니다.
- 규칙 하위 집합 실행 제어, 입력 전처리, 증분 트랜스폼 실행이 대표적인 용도이고, 후처리만이 목적이라면 하위 트랜스폼을 권장합니다.
- 절차는 고급 설정 열기, 자체 관리 트랜스폼 활성화, 저장소 선택, 워크플로 저장, 코드 생성과 복사, 저장소에 붙여 넣기 순입니다.
- 스트리밍 워크플로에는 사용자 정의 파이프라인을 쓸 수 없습니다.
