# 함수의 버전 범위 의존성 (Version range dependencies)

- 원문: https://www.palantir.com/docs/foundry/functions/version-range-dependencies-for-functions/
- 사이드바 위치: Define Ontologies > Functions > Function consumption > Version range dependencies

이 페이지는 Workshop, Actions, Automate가 함수(function)를 사용할 때 특정 버전 하나에 고정할지, 버전 범위를 지정해 자동으로 새 버전을 쓰게 할지에 대한 동작 원리와 위험을 설명합니다. 버전 범위를 쓰면 함수가 업데이트될 때마다 사용하는 쪽을 고치지 않아도 되지만, 함수 작성자가 실수로 호환성을 깨뜨리면 그 영향이 바로 전파되므로 장단점을 알고 선택해야 합니다.

Workshop, Actions, Automate는 고정된(pinned) 함수 버전에 의존할 수도 있고, 버전 범위에 의존할 수도 있습니다. 버전 범위를 사용하면 런타임에 자동으로 업그레이드되므로 개발 작업을 줄일 수 있고, [배포된 함수(deployed functions)](../09_language-agnostic-features/06_functions-deployed.md)가 다운타임 없이 업그레이드될 수 있습니다.

버전 범위 의존성은 강력한 기능이지만 특정 위험도 따릅니다(예를 들어 [Actions에만 해당하는 권한 관련 결과](#permissions-and-provenance-in-actions)가 있습니다). 이 문서는 버전 범위가 해석되는 방식을 설명하여, 이러한 위험을 더 잘 이해하고 버전 범위 의존성이 여러분의 애플리케이션에 적합한지 근거 있게 판단할 수 있도록 합니다.

이 문서는 하위 호환성(backward compatibility)과 시맨틱 버저닝(Semantic Versioning) 같은 주제에 대한 사전 지식을 전제로 합니다. 이 주제가 익숙하지 않다면 [함수 버전 관리](../07_function-management/01_functions-versioning.md) 문서를 먼저 읽어 보세요.

또한 [시맨틱 버저닝 명세 ↗](https://semver.org/#spec-item-11)에 정의된 버전 우선순위 규칙도 알고 있어야 합니다. 즉, 서로 다른 두 버전이 주어졌을 때 어느 쪽의 우선순위가 낮은지 판단할 수 있어야 합니다. 예: `1.0.0-rc.1` < `1.0.0` < `1.0.1` < `1.1.0` < `2.0.0`.

**설명**: 시맨틱 버저닝에서 버전은 `MAJOR.MINOR.PATCH` 세 숫자로 이루어집니다. 하위 호환이 깨지는 변경(예: 함수 파라미터 삭제)은 MAJOR를, 하위 호환을 유지하며 기능을 추가하면 MINOR를, 버그 수정은 PATCH를 올리는 것이 규칙입니다. `-rc.1`처럼 하이픈 뒤에 붙는 부분은 정식 출시 전의 사전 출시(pre-release) 버전을 뜻하며, 같은 숫자의 정식 버전보다 우선순위가 낮습니다. 그래서 `1.0.0-rc.1`이 `1.0.0`보다 앞에 옵니다.

<a id="version-ranges"></a>
## 버전 범위 (Version ranges)

가장 단순한 형태로 보면 버전 범위는 버전 부등식의 모음이며, 어떤 버전이 범위의 모든 부등식을 만족하면 그 버전이 범위를 "만족한다(satisfy)"고 합니다. 예를 들어 버전 `1.2.0`은 범위 `>=1.0.0 <2.0.0`을 만족합니다.

내부적으로 함수 버전 범위의 의미 체계는 JavaScript 생태계의 대표적인 패키지 관리자인 NPM에서 가져왔습니다. 엄밀한 정의는 [버전 범위에 관한 NPM 문서 ↗](https://docs.npmjs.com/cli/v6/using-npm/semver#ranges)를 참고하세요.

Workshop과 Actions 같은 애플리케이션은 현재 하위 호환되는 버전(즉, minor 또는 patch 업그레이드)으로만 이루어진 버전 범위만 허용합니다. 이 하위 호환 범위에 해당하는 NPM 표기는 [캐럿 범위(caret range) ↗](https://docs.npmjs.com/cli/v6/using-npm/semver#caret-ranges-123-025-004)입니다.

**설명**: NPM의 캐럿 범위 `^1.2.0`은 `>=1.2.0 <2.0.0`과 같은 뜻입니다. 즉 MAJOR 숫자가 같은 버전 중에서 지정한 버전 이상인 것을 모두 허용합니다. 예를 들어 `1.2.0`, `1.2.5`, `1.9.0`은 이 범위를 만족하지만 `2.0.0`과 `1.1.9`는 만족하지 않습니다. 시맨틱 버저닝 규칙이 지켜진다면 이 범위 안의 버전은 모두 하위 호환이어야 합니다.

> **중간 요약**: 버전 범위는 버전 부등식의 모음이며 NPM의 의미 체계를 따릅니다. Workshop과 Actions는 하위 호환 버전만 포함하는 캐럿 범위만 허용합니다.

<a id="version-range-resolution"></a>
## 버전 범위 해석 (Version range resolution)

배포된 함수를 제외하면, 버전 범위로 함수에 의존할 때는 실행 시점(런타임)에 범위를 만족하는 구체적인 버전 하나가 선택됩니다. 구체적으로는 범위를 만족하는 버전 중 *최대* 버전이 결국에는(eventual) 선택됩니다(새 릴리스가 반영되기까지 몇 분 걸릴 수 있습니다).

**설명**: 예를 들어 Workshop 모듈이 함수 범위 `^1.2.0`에 의존하고 공개된 버전이 `1.2.0`, `1.3.0`, `1.3.1`, `2.0.0`이라면, 범위를 만족하는 최대 버전인 `1.3.1`이 실행됩니다. 이후 작성자가 `1.4.0`을 공개하면 몇 분 안에 Workshop 쪽 설정을 바꾸지 않아도 `1.4.0`이 실행되기 시작합니다. "결국에는(eventual)"이라는 표현은 공개 직후 바로가 아니라 일정 시간이 지나 반영된다는 뜻입니다.

<a id="deployed-functions"></a>
### 배포된 함수 (Deployed functions)

배포된 함수의 경우에는 구체적인 버전이 현재 배포되어 있는 버전으로 해석됩니다. 단, 그 버전이 범위를 만족해야 합니다. 배포된 버전이 범위를 만족하지 않으면 오류가 반환됩니다.

> **중간 요약**: 일반 함수는 실행 시점에 범위를 만족하는 최대 버전이 몇 분의 지연을 두고 선택됩니다. 배포된 함수는 현재 배포된 버전이 쓰이며, 그 버전이 범위 밖이면 오류가 납니다.

<a id="risks"></a>
## 위험 (Risks)

함수 개발자는 시맨틱 버저닝 명세와 일반적인 모범 사례를 따르도록 안내받지만, major가 아닌 버전 릴리스에서도 호환성을 깨는 변경이 실수로 들어갈 가능성은 언제나 있습니다. 함수를 공개하는 쪽에서는 [안정(stable) 버전 태그를](https://www.palantir.com/docs/foundry/code-repositories/branch-settings/#restrict-stable-version-tags) 보호된 브랜치로 제한하여 이 위험을 줄일 수 있습니다. 이 제한을 걸면, 다운스트림 애플리케이션이 자동으로 가져다 쓸 수 있는 안정 버전을 릴리스하기 전에 코드 리뷰를 반드시 거치게 됩니다.

애플리케이션이 호환성을 깨는 변경을 가져가게 되면 런타임 실패나 예기치 않은 동작 등 다양한 문제로 나타날 수 있습니다.

호환성을 깨는 변경을 발견하면 즉시 해당 함수의 개발자에게 연락해 [수정 버전을 릴리스](../07_function-management/01_functions-versioning.md#accidentally-releasing-a-backward-incompatible-change-as-a-patch-or-minor-version)하도록 해야 하며, 그동안에는 함수 의존성을 마지막으로 정상 동작한 버전에 고정해 두어야 합니다.

**주의**: 배포된 함수 의존성이라는 예외를 제외하면, 애플리케이션에 엄격한 가동 시간(uptime) 요구 사항이 있어 어떤 중단도 허용할 수 없다면 고정 버전 의존성을 사용해야 합니다.

<a id="permissions-and-provenance-in-actions"></a>
### Actions에서의 권한과 출처 (Permissions and provenance in Actions)

[함수 기반 액션(Function-backed Actions)](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)에서 함수 버전 범위를 사용할 때는 액션의 동작에 영향을 줄 수 있는 권한과 출처(provenance) 관련 고려 사항이 있습니다. 그 영향에 대한 자세한 내용은 액션 문서의 [자동 업그레이드(auto upgrades)](../../03_action-types/11_function-backed-actions/02_function-actions-getting-started.md#auto-upgrades)를 참고하세요.

**설명**: 출처(provenance)는 어떤 결과가 어떤 리소스에서 비롯되었는지를 추적하는 정보입니다. 액션이 버전 범위로 함수를 호출하면 실제로 실행되는 함수 버전이 시간에 따라 바뀌므로, 그 버전이 어떤 데이터에 접근하는지도 바뀔 수 있습니다. 구체적인 영향은 링크된 액션 문서에서 다룹니다.

> **중간 요약**: minor나 patch 릴리스에서도 실수로 호환성이 깨질 수 있으므로, 중단을 허용할 수 없는 애플리케이션은 고정 버전을 써야 합니다. 함수 기반 액션에서는 권한과 출처 측면의 추가 고려 사항이 있습니다.

## 정리

- Workshop, Actions, Automate는 함수의 고정 버전이나 버전 범위에 의존할 수 있으며, 버전 범위는 자동 업그레이드를 가능하게 합니다.
- 버전 범위의 의미는 NPM을 따르며, 현재는 하위 호환 버전만 포함하는 캐럿 범위만 허용됩니다.
- 일반 함수는 범위를 만족하는 최대 버전이 몇 분 이내에 선택되고, 배포된 함수는 현재 배포된 버전이 범위를 만족해야 합니다.
- 실수로 호환성을 깨는 변경이 전파될 위험이 있으므로, 엄격한 가동 시간이 필요하면 고정 버전을 사용하고 문제가 생기면 마지막 정상 버전으로 고정합니다.
- 함수 기반 액션에서 버전 범위를 쓸 때는 권한과 출처에 관한 별도 고려 사항을 확인해야 합니다.
