# Marketplace의 함수 (Functions in Marketplace)

- 원문: https://www.palantir.com/docs/foundry/functions/marketplace-functions/
- 사이드바 위치: Define Ontologies > Functions > Function management > Functions in Marketplace

이 페이지는 직접 만든 함수(function)를 Marketplace 제품(product)에 담아 다른 환경이나 다른 사용자가 설치해 재사용하도록 하는 방법을 설명합니다. 함수를 제품에 추가하는 절차, 설치 시 함수 버전과 API 이름이 결정되는 두 가지 방식(중복 제거 모드와 안정 모드), 배포형(deployed) 함수의 실행 모드가 어떻게 함께 포장되는지, 그리고 설치하는 쪽에서 동작을 바꿀 수 있게 하는 정적 입력과 별칭(alias)을 다룹니다. 한 환경에서 만든 로직을 여러 환경에 배포해야 할 때 반드시 알아야 하는 내용입니다.

[Foundry DevOps](https://www.palantir.com/docs/foundry/devops/overview/)를 사용하면 함수를 [Marketplace 제품](https://www.palantir.com/docs/foundry/devops/core-concepts/#product)에 포함해 다른 사용자가 설치하고 재사용하게 할 수 있습니다.

**설명**: Marketplace 제품은 데이터셋, 객체 타입, 함수, 애플리케이션 같은 Foundry 리소스를 하나로 묶어 다른 프로젝트나 다른 Foundry 환경(enrollment)에 설치할 수 있게 만든 패키지입니다. 프로그래밍 언어의 패키지 관리자(npm, pip)에서 라이브러리를 배포하고 설치하는 흐름을 Foundry 리소스 단위로 수행한다고 보면 됩니다. 원래 리소스가 있는 곳을 원본 환경(source), 설치되는 곳을 대상 환경(destination 또는 target)이라고 부릅니다.

<a id="adding-functions-to-products"></a>
## 제품에 함수 추가하기 (Adding functions to products)

제품에 함수를 추가하려면 먼저 [제품을 만듭니다](https://www.palantir.com/docs/foundry/foundry-devops/create-products/). 그런 다음 아래와 같이 함수 출력(function output)을 추가합니다.

![함수 출력을 추가합니다.](https://www.palantir.com/docs/resources/foundry/functions/marketplace-add-function-output.png)

함수와 버전을 선택하라는 안내가 표시됩니다.

![함수를 검색합니다.](https://www.palantir.com/docs/resources/foundry/functions/marketplace-function-search.png)

<a id="including-model-functions"></a>
### 모델 함수 포함하기 (Including model functions)

모델의 기본 브랜치에 있는 직접 배포(direct deployment)를 기반으로 하는 모델 함수를 포장(package)할 수 있습니다. 함수를 출력으로 추가하면 그 함수의 모델 버전과 라이브 배포(live deployment)에 대한 의존성이 함께 포함됩니다. 모델을 포장할 때 **Package live deployment**(라이브 배포 포장) 항목에서 **Yes**를 선택해 함수를 자동으로 포함시킬 수도 있습니다.

설치된 함수는 대상 환경에 있는 모델과 배포를 사용합니다. 함수가 추론(inference) 요청을 처리하려면 그 배포가 실행 중이어야 합니다. 포장 요구 사항, 버전 선택, 업그레이드 동작은 [Marketplace의 모델 함수](https://www.palantir.com/docs/foundry/model-integration/marketplace-models/#model-functions)를 참고하세요. 시작 옵션은 [라이브 배포 설치](https://www.palantir.com/docs/foundry/model-integration/marketplace-models/#install-and-start-a-live-deployment)를 참고하세요.

**설명**: 모델 함수는 머신러닝 모델을 함수 형태로 호출할 수 있게 감싼 것입니다. 입력을 받아 모델에 넘기고 예측 결과(추론 결과)를 돌려줍니다. 모델이 요청을 처리하려면 모델을 올려 둔 서버 프로세스(배포)가 떠 있어야 하므로, 설치만 하고 배포를 시작하지 않으면 함수 호출이 실패합니다.

<a id="including-source-code-for-code-repositories"></a>
### 코드 저장소의 소스 코드 포함하기 (Including source code for code repositories)

코드 저장소(code repository)에서 작성한 함수를 포장하면, 그 함수의 백킹 저장소(backing repository)가 제품의 추가 출력으로 자동 포함됩니다. 코드 저장소를 소스 코드와 함께 포장하도록 선택할 수도 있지만, [부트스트랩 모드(bootstrap mode)](https://www.palantir.com/docs/foundry/foundry-devops/create-products/#installation-mode)로 설치할 의도가 없는 제품에는 소스 코드를 포함하지 않기를 일반적으로 권장합니다. Marketplace로 설치된 함수는 실행에 백킹 소스 코드가 필요하지 않기 때문입니다. 또한 코드 저장소가 설치 직후 그대로 컴파일되거나 빌드된다는 보장이 없습니다.

설치 후 함수를 변경하고 싶다면(예: 버그 수정이나 기능 보강), 원래 함수에 변경을 가하고 Marketplace 제품의 새 버전을 릴리스한 다음 설치본을 업그레이드하기를 권장합니다. 설치된 제품의 소유자가 아니라면 그 제품의 관리자에게 버그 보고나 기능 요청을 보내야 합니다.

**설명**: 설치된 함수는 이미 컴파일된 결과물(실행 가능한 버전)로 동작합니다. 소스 코드는 실행에 필요 없고, 대상 환경에서 소스를 고치면 원본과 갈라져 이후 업그레이드가 복잡해집니다. 그래서 "원본 수정, 새 버전 릴리스, 업그레이드" 순서를 권장합니다. 부트스트랩 모드는 설치한 쪽이 받은 리소스를 출발점 삼아 자유롭게 수정하는 설치 방식입니다.

<a id="extended-function-execution-requirements"></a>
### 확장 함수 실행 요구 사항 (Extended function execution requirements)

확장 실행 기능을 사용하는 함수는 Marketplace 설치 시 추가 요구 사항이 있습니다. 이런 기능에는 함수 안에서 [액션](../../03_action-types/01_overview.md)을 호출하는 것과 유효 기간(TTL, time-to-live)이 연장된 인증 토큰을 얻는 것이 포함됩니다. 설치하기 전에 관리자가 [Control Panel](https://www.palantir.com/docs/foundry/administration/control-panel/)의 **Functions settings** 아래 **Extended function execution** 허용 목록(allowlist)에 대상 프로젝트를 추가해야 합니다.

허용 목록 설정 방법은 [함수 설정(Functions settings)](../09_language-agnostic-features/09_functions-settings.md)을 참고하세요.

> **중간 요약**: 함수는 제품에 함수 출력으로 추가하며 이때 버전을 고릅니다. 모델 함수는 모델 버전과 라이브 배포 의존성이 함께 들어가고, 코드 저장소 소스는 실행에 필요 없으므로 보통 포함하지 않습니다. 액션 호출 등 확장 실행 기능을 쓰는 함수는 대상 프로젝트가 관리자 허용 목록에 있어야 합니다.

<a id="version-and-api-name-resolution"></a>
## 버전과 API 이름 결정 (Version and API name resolution)

Marketplace를 통해 함수를 설치할 때 버전과 API 이름이 결정되는 방식은 두 가지입니다. 중복 제거 모드(deduplication mode)와 안정 모드(stable mode)입니다.

<a id="deduplication-mode"></a>
### 중복 제거 모드 (Deduplication mode)

Marketplace로 설치된 함수의 버전과 API 이름을 결정하는 기존의 기본 동작입니다.

중복 제거 모드에서 함수 버전은 다음과 같이 결정됩니다.

* 설치로 함수가 처음 생성될 때 첫 버전은 `0.1.0`으로 게시됩니다.
* 업그레이드 같은 이후 설치에서는 함수의 최신 버전에서 마이너 버전을 하나 올린 버전으로 게시됩니다. 예를 들어 설치된 함수의 최신 버전이 `1.1.0`이면 다음 설치는 `1.2.0`으로 게시됩니다.

**주의**: [함수 버전](01_functions-versioning.md)은 불변(immutable)입니다. 즉, 함수의 어떤 버전이 한 번 게시되면 그 버전을 변경하거나 덮어쓸 수 없습니다.

중복 제거가 필요한 이유는 [함수 API 이름](../09_language-agnostic-features/02_query-functions.md#api-name-validations)이 온톨로지마다 유일해야 하기 때문입니다. 어떤 온톨로지에 API 이름이 `myFunction`인 함수가 이미 있으면, 그 온톨로지의 다른 함수는 같은 API 이름을 쓸 수 없습니다.

함수의 API 이름은 다음과 같이 결정됩니다.

* 설치 대상 온톨로지에서 그 API 이름이 이미 다른 함수에 묶여 있으면, 증가하는 정수 접미사를 붙여 API 이름의 중복을 제거합니다. 예를 들어 `myFunction`이 이미 사용 중이면 함수는 `myFunction1`이라는 API 이름으로 설치됩니다. 그 이름도 사용 중이면 `myFunction2`로 설치되는 식입니다.
* 설치된 함수에 한 번 API 이름이 생기면, 업그레이드 같은 이후 설치에서도 그 API 이름을 유지합니다.

**설명**: 버전 번호 `1.2.0`은 시맨틱 버저닝(semantic versioning) 형식으로 `메이저.마이너.패치`를 뜻합니다. 중복 제거 모드에서는 원본에서 어떤 버전이었든 대상 환경에서 버전을 새로 매깁니다. 예를 들어 원본에서 `3.0.0`이었던 함수도 대상 환경에 처음 설치되면 `0.1.0`이 됩니다. API 이름도 충돌하면 `myFunction1`처럼 바뀔 수 있으므로, 함수를 이름과 버전으로 고정 참조하는 외부 코드는 대상 환경에서 이름이나 버전이 달라져 깨질 수 있습니다. 이 문제를 해결하려는 것이 다음의 안정 모드입니다.

<a id="stable-mode"></a>
### 안정 모드 (Stable mode)

**참고**: 베타(Beta). 안정 모드는 개발 단계상 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/)이며 사용 중인 환경에서는 제공되지 않을 수 있습니다. 활발히 개발 중이므로 기능이 바뀔 수 있습니다. 환경에서 이 기능을 활성화하려면 Palantir Support에 문의하세요.

버전과 API 이름은 함수 API의 핵심 부분입니다. 그래서 Marketplace를 통해 포장하고 설치할 때 이것들을 그대로 보존하는 것이 바람직한 경우가 많습니다. 특히 [Developer Console 애플리케이션](https://www.palantir.com/docs/foundry/developer-console/marketplace-installation/)처럼 함수 의존성을 정적으로 참조하는 업스트림 애플리케이션과 함께 함수를 설치할 때 중요합니다.

[컴퓨트 모듈 함수(compute module functions)](https://www.palantir.com/docs/foundry/compute-modules/functions/)는 Foundry에서 자체 버전 관리 동작을 갖기 때문에 안정 모드를 지원하지 않습니다.

안정 모드에서 함수 버전은 다음과 같이 결정됩니다.

* 설치된 함수는 항상 포장된 버전 그대로 게시됩니다.
* 설치된 함수에 그 버전이 이미 존재하면 완전히 새로운 함수가 생성됩니다. 기존 함수는 숨겨지고 그 API 이름은 제거됩니다.

**주의**: 버전 충돌을 해결하려고 새 함수를 만드는 것은 업스트림 애플리케이션에 영향을 줍니다. 업스트림 애플리케이션이 같은 설치에 포함되어 있으면 새 함수를 참조하도록 자동으로 갱신됩니다. 그렇지 않으면 직접 갱신해야 합니다.

함수의 API 이름은 다음과 같이 결정됩니다.

* 설치된 함수는 항상 포장 당시의 API 이름으로 게시됩니다.
* 그 API 이름을 이미 다른 함수가 쓰고 있으면 설치 오류가 발생합니다. 이 충돌을 해결하려면 기존 함수를 삭제하거나 기존 함수의 API 이름을 바꿔야 합니다.

**설명**: 두 모드의 차이를 예로 정리하면 다음과 같습니다. 원본 환경의 함수가 API 이름 `scoreLoan`, 버전 `2.3.0`이고 대상 온톨로지에 이미 `scoreLoan`이라는 다른 함수가 있다고 합시다. 중복 제거 모드에서는 `scoreLoan1`, 버전 `0.1.0`으로 설치되어 설치는 성공하지만 이름과 버전이 바뀝니다. 안정 모드에서는 이름이 충돌하므로 설치 자체가 오류로 멈추고, 충돌을 없애면 `scoreLoan`, `2.3.0` 그대로 설치됩니다.

> **중간 요약**: 기본값인 중복 제거 모드는 대상 환경에서 버전을 `0.1.0`부터 새로 매기고 API 이름이 겹치면 숫자 접미사를 붙여 설치를 성공시킵니다. 베타 기능인 안정 모드는 포장된 버전과 API 이름을 그대로 유지하며, 이름이 겹치면 설치 오류가 나고 버전이 겹치면 새 함수를 만듭니다.

<a id="deployed-functions"></a>
## 배포형 함수 (Deployed functions)

함수는 서버리스(serverless) 실행 모드로 실행되거나, 오래 유지되는(long-lived) 컨테이너에 [배포](../09_language-agnostic-features/06_functions-deployed.md)되어 실행됩니다. Marketplace는 함수 저장소의 실행 모드를 함수와 함께 포장하므로, 설치된 함수는 포장된 환경에서 실행되던 것과 같은 방식으로 실행됩니다.

**설명**: 서버리스 실행은 함수가 호출될 때마다 실행 환경을 준비해 코드를 돌리고 끝나면 정리하는 방식입니다. 배포형 실행은 함수 코드를 담은 컨테이너(독립된 실행 환경으로 패키징된 프로세스)를 미리 띄워 두고 요청이 오면 바로 처리하는 방식입니다. 배포형은 호출 지연이 적고 메모리나 CPU 같은 자원을 직접 지정할 수 있지만, 켜져 있는 동안 계속 자원을 차지합니다.

<a id="how-marketplace-packages-function-execution-mode"></a>
### Marketplace가 함수 실행 모드를 포장하는 방식 (How Marketplace packages function execution mode)

함수 실행 모드는 저장소 단위로 설정되며, Marketplace는 같은 배포를 기반으로 하는 모든 함수에 대해 실행 모드를 *한 번만* 포장합니다.

배포 모드인 저장소의 경우, Marketplace는 환경 변수, 리소스 요청량과 한도, 스케일링 한도, 기타 주요 배포 설정 정보를 수집합니다.

Marketplace는 컨테이너 이미지를 고정 값으로 포장하지 않습니다. 대신 설치 중에 설치되는 함수 버전으로부터 컨테이너 이미지를 결정하므로, 설치된 배포는 항상 설치된 함수의 이미지를 실행합니다.

배포 모드인 저장소의 함수를 포장하려면 그 저장소에 대한 배포가 존재해야 하고, 그 배포가 포장하려는 함수 버전을 실행하고 있어야 합니다. 그렇지 않으면 포장이 실패합니다. 이 문제를 해결하려면 포장하려는 버전을 실행하도록 배포를 시작하거나 갱신하거나, 저장소를 서버리스 실행으로 전환합니다.

<a id="how-marketplace-applies-configuration-during-installation"></a>
### 설치 중 Marketplace가 설정을 적용하는 방식 (How Marketplace applies configuration during installation)

제품을 설치하거나 업그레이드하면 Marketplace는 포장된 실행 모드와 배포 설정을 대상 환경에 적용합니다. 이는 설치본의 잠금을 풀고, 제품이 포장된 환경과 같도록 실행 설정을 직접 구성하는 것과 같은 효과입니다.

포장된 모드가 *배포(deployed)*이면, Marketplace는 설치된 저장소에 대한 배포가 아직 없을 경우 배포를 만들고, 포장된 배포 설정을 적용한 뒤 배포를 시작합니다.

포장된 모드가 *서버리스(serverless)*이면, Marketplace는 설치된 저장소를 서버리스 실행으로 설정합니다. 그 저장소에 대한 배포가 이미 존재하면 Marketplace는 설치를 중단합니다.

서버리스 함수는 모든 환경에서 제공되지는 않을 수 있습니다. 제품이 함수를 서버리스 모드로 포장했지만 대상 환경에서 서버리스 실행을 사용할 수 없으면, 함수는 대신 배포 모드로 설치됩니다. 이 경우 Marketplace는 기본 설정으로 배포를 만들고 시작합니다. 이렇게 해서 설치된 함수가 배포형 함수로 실행 가능하도록 보장합니다.

**주의**: 컴퓨트 비용(Compute costs). 배포형 함수는 배포가 실행 중인 동안 계속 컴퓨트 비용이 발생하지만, 서버리스 함수는 실행될 때만 비용이 발생합니다. 따라서 대상 환경이 서버리스 실행을 지원하지 않아 배포 모드로 설치된 서버리스 함수는 오래 유지되는 배포의 컴퓨트 비용을 발생시킵니다.

<a id="limitations-of-deployed-functions-in-marketplace"></a>
### Marketplace에서 배포형 함수의 제약 (Limitations of deployed functions in Marketplace)

Marketplace의 배포형 함수에는 다음과 같은 제약이 있습니다.

<a id="only-one-version-of-a-function-can-be-deployed-at-a-time"></a>
#### 한 번에 한 버전만 배포할 수 있음 (Only one version of a function can be deployed at a time)

하나의 배포는 함수의 한 버전만 실행합니다. 배포형 함수를 포함한 Marketplace 제품을 업그레이드하면 함수가 새 버전으로 다시 게시되고, 그 새 버전이 이전에 배포되어 있던 버전을 대신해 자동으로 배포됩니다.

업그레이드되는 설치본 밖의 제품은 그 업그레이드로 갱신되지 않습니다. 여기에는 외부 제품, 그리고 Marketplace 제품에 포함되지도 않고 [연결된 제품(linked product)](https://www.palantir.com/docs/foundry/foundry-devops/linked-products/)의 일부도 아닌 제품이 포함됩니다. 이런 제품이 배포형 함수의 특정 버전을 참조하고 있으면, 그 참조는 계속 이전 버전을 가리킵니다. 함수는 한 번에 한 버전만 배포될 수 있으므로, 이전 버전에 대한 참조는 모두 오류를 반환합니다.

이를 피하려면 다음을 지켜야 합니다.

* 배포형 함수를 사용하는 쪽(consumer)을 같은 제품이나 [연결된 제품](https://www.palantir.com/docs/foundry/foundry-devops/linked-products/)에 함께 포장해, 함수와 함께 업그레이드되도록 합니다.
* 가능하면 서버리스 실행을 사용합니다. 서버리스 함수는 필요할 때 함수의 여러 버전을 실행할 수 있으므로, 업그레이드해도 이전 버전에 대한 참조가 무효화되지 않습니다.

**설명**: 예를 들어 Workshop 모듈 A가 함수 `calcRisk`의 `1.0.0` 버전을 고정 참조하고 있는데, `calcRisk`가 들어 있는 제품만 업그레이드해 배포가 `1.1.0`으로 바뀌었다고 합시다. 배포된 컨테이너에는 이제 `1.1.0`만 있으므로 A가 `1.0.0`을 호출하면 오류가 납니다. A를 같은 제품에 넣어 두면 업그레이드 때 A의 참조도 `1.1.0`으로 함께 바뀌어 이 문제가 생기지 않습니다.

<a id="deployments-restart-during-upgrades"></a>
#### 업그레이드 중 배포가 재시작됨 (Deployments restart during upgrades)

배포형 함수를 받치는 오래 유지되는 컨테이너에 대한 일부 변경(예: 컨테이너에 설정된 소스 갱신)은 컨테이너가 실행 중인 상태에서는 적용할 수 없습니다. 이 때문에 Marketplace 제품 업그레이드의 일부로 업그레이드될 때마다 배포가 중지되었다가 다시 시작될 수 있으며, 그동안 함수가 중단(downtime)될 수 있습니다.

> **중간 요약**: Marketplace는 저장소의 실행 모드(서버리스 또는 배포)와 배포 설정을 함께 포장해 대상 환경에 그대로 적용하며, 서버리스를 지원하지 않는 환경에서는 배포 모드로 대신 설치합니다. 배포형 함수는 한 번에 한 버전만 실행되므로 다른 제품이 이전 버전을 참조하면 오류가 나고, 업그레이드 중에는 재시작으로 인한 중단이 생길 수 있습니다.

<a id="static-function-inputs"></a>
## 정적 함수 입력 (Static function inputs)

**주의**: 이 기능은 [TypeScript v1](../12_typescript-v1/01_typescript-v1-getting-started.md)에서만 지원됩니다.

Marketplace 제품과 함께 배포되는 "정적(static)" 함수 입력을, 설치 시점에 로컬에서 정의한 함수로 덮어써서 함수 동작의 일부를 바꿀 수 있습니다. 이렇게 하려면 `@Static` 데코레이터를 사용해 특정 함수를 덮어쓸 수 있다고 지정합니다.

```
import { Function, Static, Double } from "@foundry/functions-api";

export class MyFunctions {

    @Function()
    public async modifyNumberByStaticFoo(
        n: Double,
        @Static() staticFunctionInput: (num: Double) => Promise<Double> = this.defaultFoo
    ): Promise<Double> {
        return await staticFunctionInput(n);
    }

    private async defaultFoo(n: number) {
        return -n;
    }

}
```

**설명**: `modifyNumberByStaticFoo`는 숫자 `n`을 받아 `staticFunctionInput`이라는 함수에 넘긴 결과를 돌려줍니다. `staticFunctionInput`은 숫자를 받아 숫자를 돌려주는 함수 타입의 파라미터이고, 기본값은 `defaultFoo`(부호를 뒤집는 함수)입니다. `@Static()` 데코레이터가 붙어 있으므로 이 파라미터는 일반 호출 인자가 아니라 설치 시점에 정해지는 값이 됩니다. 아무것도 지정하지 않으면 `n = 5`일 때 `-5`를 돌려주고, 설치하는 쪽이 "두 배로 만드는 함수"를 지정하면 같은 입력에 `10`을 돌려줍니다. 고차 함수(함수를 인자로 받는 함수)로 동작의 일부를 바꿔 끼우는 구조입니다.

함수를 포장하면 정적 입력은 설치 중에 함수 입력으로 표시됩니다. 그러면 설치하는 사람이 기본 동작을 덮어쓸 자신만의 함수 로직을 제공할 수 있습니다.

**주의**: 덮어쓴 정적 함수 안에서 [쿼리](../09_language-agnostic-features/02_query-functions.md)를 호출하거나 [API 호출](../09_language-agnostic-features/04_api-calls.md)을 하는 것은 지원되지 않습니다.

<a id="custom-aliases"></a>
## 사용자 정의 별칭 (Custom aliases)

[사용자 정의 별칭(custom alias)](../15_aliases/01_custom-aliases.md)은 설정 파라미터, 기능 플래그(feature flag), 환경별 설정 같은 문자열 값을 저장합니다. 사용자 정의 별칭이 있는 함수를 Marketplace 제품에 추가하면, 그 별칭이 **Inputs** 아래에 설정 가능한 파라미터로 자동 표시됩니다. 설치하는 사람은 함수 소스 코드를 수정하지 않고 환경별 값을 지정할 수 있습니다.

사용자 정의 별칭은 TypeScript v2 함수와 Python 함수에서 지원됩니다. [정적 함수 입력](#static-function-inputs)과 달리 사용자 정의 별칭은 다음과 같은 특징이 있습니다.

* TypeScript v2와 Python 모두에서 동작합니다.
* 설치하는 사람이 함수 로직이 아니라 문자열 값을 설정하게 합니다.
* Marketplace 설치 화면에서 설명과 미리 정한 값(preset value)을 지원합니다.

함수에서 사용자 정의 별칭을 정의하고 사용하는 자세한 방법은 [사용자 정의 별칭](../15_aliases/01_custom-aliases.md)을 참고하세요.

**설명**: 예를 들어 함수가 외부 시스템의 기본 URL을 별칭 `apiBaseUrl`로 읽는다면, 개발 환경에서는 `https://dev.example.com`, 운영 환경에 설치할 때는 `https://prod.example.com`으로 설치자가 값만 바꿔 넣을 수 있습니다. 코드에 값을 하드코딩하지 않고 환경 변수처럼 바깥에서 주입하는 방식입니다.

<a id="model-aliases"></a>
## 모델 별칭 (Model aliases)

[모델 별칭(model alias)](../15_aliases/02_model-aliases.md)을 통해 언어 모델을 참조하는 함수를 Marketplace 제품에 추가할 수 있습니다. Marketplace는 이런 별칭에 특정한 제약을 둡니다.

**주의**: 모델 별칭은 설치 중에 다른 모델로 다시 매핑할 수 없습니다. 별칭이 참조하는 모델을 대상 환경에서 사용할 수 없으면, 함수가 실행 시점에 별칭을 해석하지 못해 실패합니다.

설치 중에 설정 가능한 파라미터로 표시되는 [사용자 정의 별칭](#custom-aliases)과 달리, Marketplace는 원본 저장소에 설정된 정확한 모델 RID를 사용해 실행 시점에 모델 별칭을 해석합니다. 별칭이 참조하는 모델이 제품을 설치할 모든 대상 환경에서 사용 가능한지 확인하세요.

**설명**: RID(Resource Identifier)는 Foundry가 각 리소스에 붙이는 고유 식별자 문자열입니다. 모델 별칭은 원본에서 지정한 RID를 그대로 들고 가므로, 대상 환경에 같은 RID의 모델이 없으면 함수가 실행 중 실패합니다.

<a id="known-issues"></a>
## 알려진 문제 (Known issues)

<a id="interface-inputs-in-marketplace-functions"></a>
### Marketplace 함수의 인터페이스 입력 (Interface inputs in Marketplace functions)

[인터페이스](../../05_interfaces/01_interface-overview.md)를 입력 파라미터로 받는 함수는 대상 환경에서 `MarketplaceSdkObjectMappingNotFound` 오류를 낼 수 있습니다. Marketplace는 SDK 바인딩에 인터페이스뿐 아니라 구체 객체 타입(concrete object type)도 포함되어 있기를 요구합니다.

함수가 인터페이스 입력을 선언하고, 대상 환경에 그 인터페이스를 구현하는 구체 타입의 객체가 있으면, SDK가 구체 타입 매핑을 찾지 못합니다. 그러면 함수가 실행 시점에 실패합니다.

**해결 방법(Workaround):** 대상 환경에서 사용하는 구체 객체 타입이 원본 환경에도 존재하도록 한 다음, 그 타입을 Marketplace로 포장되는 SDK에 명시적으로 포함합니다. 그러면 필요한 매핑이 생성되어 함수가 그 객체 타입을 해석하고 사용할 수 있습니다.

**설명**: 인터페이스는 여러 객체 타입이 공통으로 갖는 속성 형태를 정의한 것이고, 실제 객체는 항상 그 인터페이스를 구현한 구체 객체 타입(예: 인터페이스 `Vehicle`을 구현한 `Truck`)에 속합니다. 프로그래밍 언어의 인터페이스와 구현 클래스 관계와 같은 구조입니다. 함수가 `Vehicle`만 알고 `Truck`에 대한 매핑을 모르면, 실제로 들어온 `Truck` 객체를 어떻게 읽을지 결정하지 못해 실패합니다.

## 정리

- 함수는 Foundry DevOps로 Marketplace 제품에 함수 출력으로 추가해 다른 환경에 설치할 수 있으며, 소스 코드는 실행에 필요 없으므로 보통 포함하지 않습니다.
- 버전과 API 이름은 기본값인 중복 제거 모드(새로 번호 매김, 이름 충돌 시 숫자 접미사)나 베타인 안정 모드(포장된 값 그대로 유지, 충돌 시 오류)로 결정됩니다.
- 저장소의 실행 모드(서버리스 또는 배포)와 배포 설정도 함께 포장되며, 배포형 함수는 한 번에 한 버전만 실행되고 업그레이드 시 재시작될 수 있습니다.
- 설치자가 동작을 바꾸게 하려면 TypeScript v1의 정적 함수 입력이나 TypeScript v2와 Python의 사용자 정의 별칭을 쓰며, 모델 별칭은 다시 매핑할 수 없습니다.
- 인터페이스 입력을 받는 함수는 구체 객체 타입을 SDK에 함께 포함해야 대상 환경에서 오류가 나지 않습니다.
