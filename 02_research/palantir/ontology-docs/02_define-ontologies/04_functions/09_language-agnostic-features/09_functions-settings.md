# 함수 설정 (Functions settings)

- 원문: https://www.palantir.com/docs/foundry/functions/functions-settings/
- 사이드바 위치: Define Ontologies > Functions > Language-agnostic features > Functions settings

이 페이지는 관리자가 Control Panel의 **Functions settings** 페이지에서 스페이스(space) 단위로 함수(function)의 동작을 관리하는 방법을 설명합니다. 특히 함수 안에서 액션을 호출하거나 수명이 긴 인증 토큰을 얻는 확장 실행(Extended function execution) 기능과, 이 기능을 쓸 수 있는 저장소, 함수, 프로젝트를 제한하는 허용 목록(allowlist)을 다룹니다.

[Control Panel](https://www.palantir.com/docs/foundry/administration/control-panel/)의 **Functions settings** 페이지에서 관리자는 특정 [스페이스(space)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/) 안에서 함수가 동작하는 방식을 결정하는 설정 모음을 관리할 수 있습니다. 각 설정은 아래 섹션에서 자세히 설명하는 특정 기능의 활성화 여부를 제어합니다. 이 페이지에 접근하려면 구성하려는 스페이스에서 **Control Panel > Functions settings**로 이동합니다.

<a id="extended-function-execution"></a>
## 확장 함수 실행 (Extended function execution)

**Extended function execution** 모달을 사용하면 특정 함수가 다음과 같은 확장 기능을 가지고 실행되도록 할 수 있습니다.

* 함수 안에서 [액션](../../03_action-types/01_overview.md)을 호출합니다.
* 최대 4시간까지 연장된 유효 시간(TTL, time-to-live)을 가진 인증 토큰을 얻습니다.

![Control Panel의 Extended function execution 설정. 함수의 확장 기능을 제어하는 세 가지 허용 목록이 보입니다.](https://www.palantir.com/docs/resources/foundry/functions/extended-function-execution.png)

이 기능들은 함수에 높은 수준의 접근 권한을 부여하므로, 확장 함수 실행 기능은 모달의 접을 수 있는 섹션에서 구성하는 허용 목록 집합을 통해 이 기능이 어디서 활성화되는지를 세밀하게 제어할 수 있게 합니다. 함수가 이 확장 기능을 가지고 게시, 실행, 설치되려면 먼저 관련 허용 목록을 만족해야 합니다. 어떤 저장소, 함수, 프로젝트가 확장 함수 실행을 사용할 수 있는지 제어하려면 다음 허용 목록을 구성합니다.

**설명**: 허용 목록(allowlist)은 목록에 명시된 대상만 허용하고 나머지는 모두 거부하는 방식의 접근 제어입니다. TTL은 토큰이 발급된 뒤 유효한 시간입니다. 토큰이 오래 유효할수록 오래 걸리는 작업을 끝까지 수행할 수 있지만, 유출되었을 때 악용될 수 있는 시간도 길어지므로 관리자가 범위를 제한합니다.

<a id="repositories-allowed-to-publish-extended-functions"></a>
### 확장 함수를 게시할 수 있는 저장소 (Repositories allowed to publish extended functions)

이 허용 목록에 있는 저장소만이 스페이스 안에서 확장 실행 기능을 가진 함수를 게시할 수 있습니다. 저장소를 추가하려면 **Add**를 선택하고 허용할 저장소를 검색합니다.

<a id="functions-allowed-to-execute-with-extended-capabilities"></a>
### 확장 기능으로 실행할 수 있는 함수 (Functions allowed to execute with extended capabilities)

이 허용 목록에 있는 함수만이 확장 기능을 가지고 실행됩니다. 이 목록은 실행 시점에 확인되므로, 함수가 계속 확장 기능으로 실행되려면 허용 목록에 남아 있어야 합니다. 허용 목록에 있는 저장소에서 새로 게시된 함수는 함수 허용 목록에 자동으로 추가됩니다. 함수를 추가하려면 **Add**를 선택하고 허용할 함수를 검색합니다.

<a id="projects-allowed-for-installing-extended-functions-via-marketplace"></a>
### Marketplace를 통해 확장 함수를 설치할 수 있는 프로젝트 (Projects allowed for installing extended functions via Marketplace)

이 허용 목록에 있는 프로젝트에서만 확장 실행 기능을 가진 함수의 [Marketplace](https://www.palantir.com/docs/foundry/marketplace/overview/) 설치가 성공합니다. 프로젝트를 추가하려면 **Add**를 선택하고 허용할 프로젝트를 검색합니다.

**설명**: 세 허용 목록은 함수의 수명 주기 단계마다 하나씩 대응합니다. 게시 단계에서는 저장소 목록, 실행 단계에서는 함수 목록, Marketplace 설치 단계에서는 프로젝트 목록을 확인합니다. 예를 들어 허용된 저장소 A에서 함수 f를 게시하면 f는 함수 목록에 자동으로 들어가지만, 나중에 관리자가 f를 함수 목록에서 지우면 f는 그다음 실행부터 확장 기능 없이 실행됩니다.

## 정리

- 관리자는 Control Panel의 **Functions settings**에서 스페이스 단위로 함수 동작 설정을 관리합니다.
- **Extended function execution**은 함수 안에서 액션을 호출하거나 최대 4시간 TTL의 인증 토큰을 얻는 기능을 허용합니다.
- 이 기능은 권한이 높으므로 저장소(게시), 함수(실행), 프로젝트(Marketplace 설치) 세 가지 허용 목록으로 사용 범위를 제한합니다.
- 함수 허용 목록은 실행 시점에 확인되며, 허용된 저장소에서 게시된 새 함수는 자동으로 추가됩니다.
