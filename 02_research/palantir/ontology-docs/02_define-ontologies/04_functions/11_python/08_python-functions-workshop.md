# Workshop에서 Python 함수 사용하기 (Use Python functions in Workshop)

- 원문: https://www.palantir.com/docs/foundry/functions/python-functions-workshop/
- 사이드바 위치: Define Ontologies > Functions > Python > Use Python functions in Workshop

이 페이지는 게시한 Python 함수(function)를 애플리케이션 빌더인 Workshop에서 사용하는 방법을 설명합니다. 함수를 변수로 불러오는 방법, 배포(deployed) 함수의 상태와 새 버전 릴리스 및 오류 디버깅 절차, 그리고 Object Table 위젯에 함수 기반 열(function-backed column)을 만드는 데 필요한 함수 형태를 다룹니다.

<a id="prerequisites"></a>
## 사전 요구 사항 (Prerequisites)

이 가이드는 Python 함수를 이미 작성하고 게시했다고 가정합니다. 튜토리얼은 [Python 함수 시작하기](01_python-getting-started.md) 문서를 참고하세요. Python SDK로 온톨로지를 쿼리하는 예제는 [Python Ontology SDK 문서](https://www.palantir.com/docs/foundry/ontology-sdk/python-osdk/)를 참고하세요.

<a id="use-the-python-function-in-workshop"></a>
## Workshop에서 Python 함수 사용하기 (Use the Python function in Workshop)

Workshop에서 모듈 왼쪽의 **Variables** 탭에서 Python 함수를 검색합니다. [서버리스 함수와 배포 함수](../09_language-agnostic-features/06_functions-deployed.md#choose-between-deployed-and-serverless-execution-modes)가 모두 여기에 나타납니다. 서버리스 함수는 언제든 어떤 버전으로든 실행할 수 있으며 수동으로 배포할 필요가 없습니다. 배포 함수는 함수와 함수 버전 각각에 대해 다음 세 상태 중 하나를 나타내는 아이콘을 표시합니다.

* **Running:** 이 함수와 버전이 요청을 처리할 수 있습니다.
* **Stopped:** 이 함수와 버전을 사용할 수 없습니다. 함수 선택기에서 정보 아이콘 위에 마우스를 올리고 **Configure**를 선택한 다음 **Create and start deployment**를 선택해 함수를 사용 가능하게 만듭니다.
* **Upgrading:** 이 함수와 버전을 아직 사용할 수 없습니다.

<img alt="Workshop의 Python 함수" src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-workshop-deployment-status.png" width="650px">

**설명**: 서버리스(serverless) 함수는 호출될 때마다 실행 환경이 필요에 따라 만들어지는 방식이고, 배포(deployed) 함수는 함수 저장소의 특정 버전을 실행하는 서버가 계속 떠 있는 방식입니다. 그래서 배포 함수에는 서버가 실행 중인지(Running), 멈췄는지(Stopped), 새 버전으로 교체 중인지(Upgrading)를 나타내는 상태가 있습니다.

<a id="cut-a-new-release"></a>
### 새 릴리스 만들기 (Cut a new release)

한 시점에 호스팅되는 것은 함수 저장소의 한 버전뿐입니다. 중단 시간을 최소화하면서 함수를 변경하려면, 변경 사항을 담은 새 함수(예: `function_v1`)를 추가하고 [여기](01_python-getting-started.md#commit-and-publish-a-function)에 설명된 대로 태그를 다는 방법을 권장합니다. 태그 및 릴리스(tags and releases) 아래의 게시된 함수에서 **Open in Ontology Manager**를 선택합니다.

Ontology Manager에서 애플리케이션에 사용할 함수 저장소 버전을 선택한 다음 **Upgrade**를 선택합니다.

<img alt="배포 함수 업그레이드" src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-upgrade-deployed-function.png" width="350px">

이 저장소의 함수를 사용하는 모든 다운스트림 애플리케이션을 새로 배포한 버전으로 업데이트합니다. 이전 배포 버전은 더 이상 실행되지 않으므로, 이 변경을 하는 동안 애플리케이션에 짧은 중단 시간이 생깁니다. `function_v0`과 `function_v1`을 동시에 사용할 수 있으므로, 새 배포 버전으로 전환은 해야 하지만 사용 중인 함수를 바꿀 필요는 없습니다. `function_v0`이 더 이상 사용되지 않으면 그 함수를 삭제할 수 있습니다.

**설명**: 예를 들어 저장소 버전 1.0.0에 `function_v0`만 있었다면, 버전 1.1.0에서는 `function_v0`을 그대로 두고 `function_v1`을 추가합니다. 1.1.0을 배포해도 기존 Workshop 모듈은 여전히 `function_v0`을 호출할 수 있으므로, 버전 번호만 1.1.0으로 올려 주면 되고 함수 이름을 바꾸는 작업은 나중에 천천히 할 수 있습니다.

<a id="debug-errors"></a>
### 오류 디버깅 (Debug errors)

함수가 Workshop에서 예상대로 동작하지 않으면, 먼저 문제가 함수의 로직 때문인지 응답성 때문인지 확인합니다. 로직 문제라면 백킹 코드 저장소의 소스 코드를 살펴봅니다. 함수가 응답하지 않거나 오류를 던지는 문제라면 아래 단계를 따르세요.

1. 함수 선택기 드롭다운 메뉴에서 선택한 버전이 현재 실행 중인지 확인합니다.

<img alt="Workshop 함수 버전 선택기." src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-workshop-function-selector-running.png" width="350px">

2. 함수가 배포되지 않았거나 `Upgrading` 상태이면, 함수의 정보 아이콘 위에 마우스를 올리고 **Configure**를 선택합니다. 그러면 Ontology Manager로 이동하며, 여기서 **Start Deployment**를 선택해 함수를 다시 실행할 수 있습니다.

<img alt="Python 함수 버전 정보." src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-upgrading-function-info.png" width="750px">

3. 함수가 `Running` 상태이거나 배포 동작에 대해 더 많은 정보가 필요하면, Ontology Manager 왼쪽 패널에서 **Deployment**를 선택해 상세 로그를 확인합니다. **View live**를 선택하면 SLS 로그도 볼 수 있습니다.

<img alt="Ontology Manager에서 배포 로그 보기." src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-deployed-function-logs.png" width="850px">

> **중간 요약**: Workshop의 Variables 탭에서 Python 함수를 불러옵니다. 배포 함수는 Running, Stopped, Upgrading 상태를 가지며, 새 함수를 추가하는 방식으로 릴리스하고 Ontology Manager에서 Upgrade합니다. 문제가 생기면 실행 상태, 배포 시작, 배포 로그 순으로 확인합니다.

<a id="create-a-function-backed-column"></a>
## 함수 기반 열 만들기 (Create a function-backed column)

함수 기반 열(function-backed column)을 만들려면 다음 요구 사항을 충족하는 함수를 게시해야 합니다.

* 함수의 입력 파라미터에는 객체 집합(object set) 파라미터(`ontology_sdk.ontology.object_sets`에서 가져옴)가 포함되어야 하며, 다른 입력 파라미터를 선택적으로 포함할 수 있습니다. 이 객체 집합 파라미터를 통해 테이블에 표시된 객체들이 함수로 전달되고, 함수는 원하는 파생 열을 생성합니다. `list[ObjectType]` 파라미터도 동작하지만 성능이 떨어지므로 권장하지 않습니다.

* 함수의 반환 타입은 `dict[ObjectType, ColumnType]`이어야 합니다. 여기서 `ColumnType`은 열에 원하는 [타입](../04_types-reference.md#types-reference)입니다. 또는 함수에서 여러 열을 반환하려면 `dict[ObjectType, CustomType]`을 사용합니다. [사용자 정의 타입](../04_types-reference.md#structcustom-type)에 대해 자세히 알아보세요.

위 조건을 충족하는 함수를 구성하고 게시하면, [Object Table](https://www.palantir.com/docs/foundry/workshop/widgets-object-table/#features-of-function-backed-properties) 위젯 구성에서 함수 기반 속성(property) 열을 구성할 수 있습니다.

열 하나를 반환하는 함수의 예:

```python
from functions.api import Date, Integer, String, function
from ontology_sdk import FoundryClient
from ontology_sdk.ontology.object_sets import MyObjectTypeObjectSet
from ontology_sdk.ontology.objects import MyObjectType

@function
def function_backed_column_single_col(
    selected_objects: MyObjectTypeObjectSet
) -> dict[MyObjectType, Integer]:
    final_dict = {}

    for curr_obj in selected_objects:
        final_dict[curr_obj] = 10 # 값은 임의의 로직으로 정할 수 있습니다

    return final_dict
```

**설명**: 입력은 Object Table에 현재 보이는 객체들의 집합이고, 출력은 "객체를 키, 열 값을 값"으로 하는 딕셔너리입니다. 테이블에 객체 A, B, C가 보이면 함수는 `{A: 10, B: 10, C: 10}`을 반환하고, Object Table은 각 행 옆에 그 값을 새 열로 표시합니다. 실제로는 `10` 자리에 객체의 속성으로 계산한 값을 넣습니다.

![열 하나를 반환하는 함수의 예.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-advanced-single.png)

여러 열을 반환하는 함수의 예:

```python
from dataclasses import dataclass

@dataclass
class CustomType:
    column_name_a: int
    column_name_b: int

@function
def function_backed_column_multiple_cols(
    selected_objects: MyObjectTypeObjectSet, some_other_parameter: String
) -> dict[MyObjectType, CustomType]:
    final_dict = {}

    for curr_obj in selected_objects:
        final_dict[curr_obj] = CustomType(column_name_a=10, column_name_b=20)

    return final_dict

```

**설명**: 딕셔너리 값을 `CustomType` 데이터 클래스로 바꾸면, 데이터 클래스의 필드(`column_name_a`, `column_name_b`)마다 열이 하나씩 생깁니다. 객체 집합 외의 추가 파라미터(`some_other_parameter`)도 함께 받을 수 있습니다.

![여러 열을 반환하는 함수의 예.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-advanced-multiple.png)

> **중간 요약**: 함수 기반 열을 만들려면 객체 집합 파라미터를 받고 `dict[객체 타입, 열 타입]`(여러 열이면 `dict[객체 타입, 사용자 정의 타입]`)을 반환하는 함수를 게시한 뒤 Object Table 위젯에서 구성합니다.

## 정리

- Workshop의 Variables 탭에서 서버리스 함수와 배포 함수를 모두 찾아 쓸 수 있습니다.
- 배포 함수는 Running, Stopped, Upgrading 상태를 가지며, 한 번에 저장소의 한 버전만 호스팅됩니다.
- 중단 시간을 줄이려면 새 이름의 함수를 추가해 릴리스하고 Ontology Manager에서 Upgrade한 뒤 다운스트림 앱을 새 버전으로 옮깁니다.
- 함수가 응답하지 않으면 버전 실행 상태 확인, Start Deployment, Deployment 로그 확인 순으로 디버깅합니다.
- 함수 기반 열에는 객체 집합 입력과 객체별 값을 담은 딕셔너리 반환이 필요합니다.
