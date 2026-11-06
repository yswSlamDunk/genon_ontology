# Python 함수 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/functions/python-getting-started/
- 사이드바 위치: Define Ontologies > Functions > Python > Getting started

이 페이지는 Python으로 Foundry 함수(function)를 처음 만드는 과정을 단계별로 안내합니다. Python 함수 리포지토리를 만들고, 예제 함수의 구조를 살펴보고, 라이브 미리보기로 실행해 본 뒤, 커밋하고 태그를 붙여 게시(publish)하는 흐름을 다룹니다. 게시한 함수는 Workshop이나 Pipeline Builder 같은 다른 애플리케이션에서 호출할 수 있게 됩니다.

다음 문서는 Palantir 플랫폼에서 Python 함수를 사용할 수 있도록 준비하는 초기 단계를 안내합니다. Python 함수 리포지토리를 만들고, 함수를 커밋하고 게시하고, 라이브 미리보기(live preview)에서 테스트하는 방법 등을 배웁니다.

<a id="create-a-python-functions-repository"></a>
## Python 함수 리포지토리 만들기 (Create a Python functions repository)

원하는 프로젝트로 이동한 뒤 **+ New > Repository**를 선택해 새 코드 리포지토리를 만듭니다. 리포지토리를 초기화할 때 **Python functions** 템플릿을 선택합니다. 비용을 최소화하려면 Workshop이나 온톨로지 기반 애플리케이션에서 사용할 모든 함수를 하나의 리포지토리에 모아 두는 것을 권장합니다.

![Python 함수 코드 리포지토리 만들기.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-create-repo.png)

리포지토리가 만들어지면 `python-functions/python/python-functions/my_function.py` 파일로 이동합니다.

<a id="explore-the-repository"></a>
## 리포지토리 살펴보기 (Explore the repository)

리포지토리는 몇 가지 예제 함수가 들어 있는 `my_function.py` 파일과 함께 초기화되며, 그중에는 다음 함수가 있습니다.

```python tab="Python"
from functions.api import function, String

@function
def my_function() -> String:
    return "Hello World!"
```

이 함수가 다음 제약을 따른다는 점에 주목하세요.

* Python 함수로 인식되려면 함수에 `functions.api` 패키지의 `@function` 데코레이터를 붙여야 합니다. Python 파일 여러 개에 각각 여러 함수를 둘 수 있지만, *이 데코레이터가 붙은 함수만* Python 함수로 등록됩니다.
* 함수는 모든 입력의 타입과 출력 타입을 선언해야 하며, 이때 functions API 패키지의 타입이나 그에 대응하는 Python 타입을 사용할 수 있습니다. 예를 들어 위 예제의 출력 타입은 functions API의 `String`으로 선언되어 있지만, 대응하는 Python 타입인 `str`로 선언해도 됩니다.

인자의 타입을 API 타입(예: `String`)으로 선언하더라도, 실행 시점에 함수에는 대응하는 Python 타입(이 예에서는 `str`)의 값이 전달됩니다.

Python 함수의 타입 전체 개요는 [타입 참조 문서](../04_types-reference.md)를 참고하세요.

리포지토리에 Python 패키지를 추가하려면 [Python 라이브러리 찾기와 사용하기](https://www.palantir.com/docs/foundry/transforms-python/use-python-libraries/)에서 설명하는 대로 **Libraries** 사이드 패널을 사용합니다.

**설명**: 데코레이터(decorator)는 `@이름` 형태로 함수 정의 위에 붙여 그 함수에 추가 동작이나 표시를 덧붙이는 Python 문법입니다. 여기서 `@function`은 "이 함수를 플랫폼에 등록하라"는 표시 역할을 합니다. 타입 선언(`-> String`, `start_time: datetime` 같은 타입 힌트)은 일반 Python에서는 선택 사항이지만, Foundry는 이 정보를 읽어 Workshop 같은 화면에서 어떤 입력 칸을 보여 줄지, 다른 함수와 어떻게 연결할지를 결정하므로 반드시 적어야 합니다.

> **중간 요약**: **Python functions** 템플릿으로 리포지토리를 만들면 예제 파일이 생깁니다. `@function` 데코레이터가 붙고 입력과 출력 타입이 모두 선언된 함수만 Python 함수로 등록됩니다.

<a id="test-in-live-preview"></a>
## 라이브 미리보기에서 테스트하기 (Test in live preview)

새 함수를 추가한 뒤에는 **Functions** 도우미에서 바로 실행해 볼 수 있습니다. 화면 왼쪽 아래에서 **Functions** 도우미를 열고 **Live Preview**를 선택합니다. `add_seconds_to_datetime` 함수를 고르고 입력값을 넣은 뒤 **Run**을 선택해 코드를 실행합니다.

![Functions 도우미에서 새 함수 실행하기.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-live-preview.png)

오른쪽 위의 **Commit**을 선택해 변경 사항을 리포지토리의 `master` 브랜치에 커밋합니다.

<a id="commit-and-publish-a-function"></a>
### 함수 커밋하고 게시하기 (Commit and publish a function)

함수를 작성한 뒤(또는 제공된 예제 함수 중 하나의 주석을 해제한 뒤) 다음 단계에 따라 커밋하고 게시합니다.

1. **Source control** 탭에서 **Commit**을 선택하고 커밋 메시지를 추가해 변경 사항을 커밋합니다.
2. 화면 위쪽 가운데의 **Branches** 탭을 선택한 다음 **Tags and releases**를 선택합니다.
3. **New tag**를 선택하고 릴리스 버전을 입력합니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/new-functions-tag.png" alt="적절한 버전 선택하기" width=500>

4. **Tag and release**를 선택하고 릴리스 단계가 끝날 때까지 기다립니다.

5. 검사(check)가 성공하면 **Code** 탭을 선택한 다음 페이지 아래쪽의 **Functions** 탭을 엽니다. 결과에 `my_function`이 보입니다.

![Functions 도우미 열기.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-preview.png)

6. 함수를 선택한 다음 **Run**을 선택해 방금 게시한 함수를 실행합니다.

![Functions 도우미에서 함수 실행하기.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-run.png)

**설명**: 라이브 미리보기는 커밋하지 않은 현재 코드를 그 자리에서 실행해 보는 기능이고, 게시는 특정 버전을 고정해 다른 애플리케이션이 호출할 수 있게 만드는 단계입니다. 게시는 git 태그로 이루어집니다. 태그는 특정 커밋에 `1.0.0` 같은 이름을 붙이는 git 기능이며, 태그를 만들면 Foundry가 그 커밋을 빌드하고 검사한 뒤 해당 버전의 함수를 등록합니다. 코드를 고친 뒤 다른 곳에서 새 동작을 쓰려면 새 버전 태그를 다시 만들어야 합니다.

> **중간 요약**: **Functions** 도우미의 **Live Preview**로 커밋 전 코드를 바로 실행해 볼 수 있습니다. 게시하려면 커밋한 뒤 **Tags and releases**에서 새 버전 태그를 만들고, 검사가 끝나면 **Functions** 탭에서 게시된 함수를 실행할 수 있습니다.

<a id="add-another-function"></a>
## 다른 함수 추가하기 (Add another function)

이제 이 리포지토리에 더 복잡한 함수를 추가해 테스트하고 게시해 보겠습니다. 아래 코드를 복사해 `my_function` 파일 맨 아래에 붙여 넣습니다.

```python tab="Python"
from functions.api import function, String
from datetime import datetime, timedelta

@function
def add_seconds_to_datetime(start_time: datetime, elapsed_millis: int) -> str:
    dt = start_time + timedelta(milliseconds=elapsed_millis)
    return dt.isoformat()
```

**설명**: 시작 시각(`datetime`)과 경과 밀리초(`int`)를 입력받아, 시작 시각에 그만큼을 더한 시각을 ISO 8601 형식 문자열로 반환합니다. 예를 들어 `start_time`이 2024-01-01 09:00:00이고 `elapsed_millis`가 90000이면 `"2024-01-01T09:01:30"`을 반환합니다. 함수 이름은 "seconds"지만 실제로는 밀리초 단위로 더한다는 점에 주의하세요. 이 함수가 앞의 라이브 미리보기 절에서 실행해 본 `add_seconds_to_datetime`입니다.

플랫폼에서 Python 함수를 활용하는 더 많은 예는 [Pipeline Builder에서 Python 함수 사용하기](07_python-functions-builder.md)와 [Workshop에서 Python 함수 사용하기](08_python-functions-workshop.md) 문서를 참고하세요.

## 정리

- **Python functions** 템플릿으로 코드 리포지토리를 만들면 `my_function.py` 예제 파일이 생기며, Workshop과 온톨로지 애플리케이션용 함수는 비용을 줄이기 위해 한 리포지토리에 모으는 것이 권장됩니다.
- `@function` 데코레이터가 붙고 입력과 출력 타입이 선언된 함수만 등록되며, API 타입으로 선언해도 실행 시에는 대응하는 Python 타입이 전달됩니다.
- **Functions** 도우미의 **Live Preview**로 커밋 전 코드를 실행해 볼 수 있습니다.
- 커밋 후 **Tags and releases**에서 버전 태그를 만들어 게시하면, 게시된 함수를 실행하고 다른 애플리케이션에서 사용할 수 있습니다.
