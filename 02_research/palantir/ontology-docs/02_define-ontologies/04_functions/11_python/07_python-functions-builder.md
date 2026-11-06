# Pipeline Builder에서 Python 함수 사용하기 (Use Python functions in Pipeline Builder)

- 원문: https://www.palantir.com/docs/foundry/functions/python-functions-builder/
- 사이드바 위치: Define Ontologies > Functions > Python > Use Python functions in Pipeline Builder

이 페이지는 게시한 Python 함수(function)를 데이터 파이프라인 도구인 Pipeline Builder에서 사용자 정의 함수(UDF)로 쓰는 방법을 설명합니다. 함수가 데이터를 행 단위로 처리하는 방식, 파이프라인에 함수를 가져와 연결하는 절차, 외부 API 호출과 온톨로지 접근에 관한 제약을 다룹니다.

Pipeline Builder는 Java와 Python 사용자 정의 함수(user-defined function, UDF)를 모두 지원합니다. 이 페이지는 Python UDF를 설명합니다. Java를 대신 사용하려면 [Java UDF에 대해 자세히 알아보세요](https://www.palantir.com/docs/foundry/transforms-java/user-defined-functions/).

**설명**: 사용자 정의 함수(UDF)는 플랫폼이 기본으로 제공하는 변환(예: 문자열 합치기, 필터) 외에, 사용자가 직접 코드로 작성해 파이프라인의 한 단계로 끼워 넣는 함수입니다. SQL의 사용자 정의 함수가 `SELECT my_func(col) FROM t`처럼 쿼리 안에서 호출되는 것과 같은 개념입니다.

<a id="prerequisites"></a>
## 사전 요구 사항 (Prerequisites)

이 가이드는 Python 함수를 이미 작성하고 게시했다고 가정합니다. 튜토리얼은 [Python 함수 시작하기](01_python-getting-started.md) 문서를 참고하세요.

<a id="architecture"></a>
## 아키텍처 (Architecture)

Python 함수는 Pipeline Builder 파이프라인 안에서 사이드카(sidecar) 컨테이너로 실행됩니다. 따라서 함수를 배포할 필요가 없으며, 파이프라인 크기에 따라 동적으로 확장됩니다. 파이프라인에 포함된 함수는 Pipeline Builder의 다른 변환과 마찬가지로 [미리 보기](https://www.palantir.com/docs/foundry/pipeline-builder/outputs-preview-pipeline/)할 수 있습니다.

**설명**: 사이드카 컨테이너는 주 작업(여기서는 파이프라인 빌드)을 실행하는 컨테이너 옆에 함께 띄워지는 보조 컨테이너입니다. 함수가 별도 서버로 상시 떠 있는 것이 아니라 파이프라인이 실행될 때 같이 실행되므로 "배포"라는 별도 단계가 필요 없습니다.

<a id="how-python-functions-process-data"></a>
## Python 함수가 데이터를 처리하는 방식 (How Python functions process data)

Python 함수를 Pipeline Builder의 사용자 정의 함수(UDF)로 사용하면, 함수는 **행마다 한 번씩** 실행됩니다. Pipeline Builder는 테이블 전체나 `pandas` DataFrame, Spark DataFrame을 함수에 넘기지 않습니다. 대신 하나 이상의 입력 열을 함수의 파라미터에 매핑하면, Pipeline Builder가 모든 행에 대해 함수를 호출하면서 그 행의 셀 값들을 파라미터 인자로 넘깁니다.

함수가 반환한 값은 출력 테이블의 새 열이 되며, 행마다 값이 하나씩 만들어집니다. 이 때문에 Python UDF는 DataFrame이 아니라 `str`, `int`, `float`, `bool`, `datetime` 같은 스칼라(단일 값) 타입을 반환합니다. 반환할 DataFrame 타입은 없습니다. Pipeline Builder가 각 행의 반환값을 모아 조립한 열 *자체가* 결과 테이블 출력입니다.

다음 예제는 두 열을 입력으로 받아 행마다 `str` 값 하나를 반환하며, Pipeline Builder는 이 값을 새 열에 씁니다.

```python tab="Python"
from functions.api import function

@function
def full_name(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}"
```

**설명**: 입력 테이블이 다음과 같다고 합시다.

| first_name | last_name |
|---|---|
| Ada | Lovelace |
| Alan | Turing |

`full_name`은 2번 호출되어 각각 `"Ada Lovelace"`, `"Alan Turing"`을 반환하고, 이 값들이 새 열(예: `full_name`)로 붙습니다. SQL의 `SELECT first_name, last_name, full_name(first_name, last_name) FROM t`와 같은 결과입니다.

[변환을 구성](#use-your-function-in-a-pipeline-builder-pipeline)할 때 `first_name`과 `last_name` 파라미터를 해당 입력 열에 매핑합니다. 변환이 실행되면 Pipeline Builder는 각 행에 대해 `full_name`을 평가하고 반환된 문자열을 새 출력 열에 씁니다.

지원되는 입력 및 출력 타입 전체와 그에 대응하는 Python 타입은 [타입 참조](../04_types-reference.md)를 확인하세요. 그 참조에 있는 [온톨로지 타입](../04_types-reference.md#ontology-types)은 Pipeline Builder에서 지원되지 않습니다. 온톨로지 타입을 받거나 반환하는 함수는 가져올 수 없으며 사용 가능한 함수 목록에도 나타나지 않습니다.

<a id="return-a-struct"></a>
### 구조체 반환하기 (Return a struct)

한 함수에서 서로 관련된 여러 값을 반환하려면 스칼라 대신 [사용자 정의 타입(구조체)](../04_types-reference.md#structcustom-type)을 반환합니다. Pipeline Builder는 반환된 값을 사용자 정의 타입의 각 속성마다 필드가 하나씩 있는 단일 구조체(struct) 열로 추가합니다. 그런 다음 [Get struct field](https://www.palantir.com/docs/foundry/pipeline-builder/functions-index/#get-struct-field) 변환으로 개별 필드를 추출할 수 있습니다.

```python tab="Python"
from dataclasses import dataclass
from functions.api import function, Double

@dataclass
class Stats:
    total: Double
    average: Double

@function
def compute_stats(a: Double, b: Double) -> Stats:
    total = a + b
    return Stats(total=total, average=total / 2)
```

**설명**: `a=4`, `b=6`인 행에서 이 함수는 `Stats(total=10, average=5)`를 반환하고, 출력 테이블에는 `{total: 10, average: 5}` 형태의 값이 든 열 하나가 생깁니다. 열을 두 개로 나누고 싶으면 Get struct field 변환을 두 번 적용합니다.

> **중간 요약**: Python UDF는 행마다 한 번 호출되어 스칼라 값 하나를 반환하고, 그 값들이 새 열이 됩니다. 여러 값을 반환하려면 구조체를 반환하며, 온톨로지 타입은 Pipeline Builder에서 쓸 수 없습니다.

<a id="use-your-function-in-a-pipeline-builder-pipeline"></a>
## Pipeline Builder 파이프라인에서 함수 사용하기 (Use your function in a Pipeline Builder pipeline)

**주의**: Pipeline Builder는 대규모 언어 모델(LLM)을 호출하는 UDF를 지원하지 않습니다. 파이프라인에서 LLM을 사용하려면 대신 [Use LLM 노드](https://www.palantir.com/docs/foundry/pipeline-builder/pipeline-builder-llm/)를 설정하세요.

아래 단계에 따라 파이프라인에서 Python 함수를 준비하고 구성합니다.

1. Python 함수를 사용할 Pipeline Builder 파이프라인을 엽니다.

<img alt="Pipeline Builder의 Python 함수." src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-builder.png" width="800px">

2. 다음 두 방법 중 하나로 UDF를 Pipeline Builder에 가져옵니다.
   * **그래프 보기에서(From the graph view):**
     1. 파이프라인 그래프 위쪽에서 **Reusables**를 선택한 다음 **User-defined functions**를 선택합니다. <br><br>
        <img alt="Pipeline Builder의 'Reusables' 버튼." src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-builder-reusable.png" width="500px">
     <br><br>
     2\. **Import UDF**를 선택하고 사용 가능한 함수를 검색해 사용할 함수를 찾습니다.
     3\. 함수 이름 옆의 **Add**를 선택합니다. 그러면 함수에 **Imported** 태그가 표시됩니다.<br><br> <img alt="Pipeline Builder에 Python 함수 추가." src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-add-builder.png" width="700px"> <br><br>
     4\. 가져오기 대화 상자를 닫고, Pipeline Builder 그래프에서 함수를 사용할 위치에서 **Transform**을 선택합니다.
     5\. 변환 목록 왼쪽의 **UDFs** 탭에서 가져온 함수를 확인합니다.
   * **변환 선택기 사용(Use the transform picker):**
     1. Pipeline Builder 그래프에서 **Transform**을 선택합니다.
     2. 가져올 UDF의 이름을 입력합니다. <br><br>
        <img alt="Pipeline Builder에서 아직 가져오지 않은 UDF 검색." src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-builder-search-udfs.png" width="500px">
     <br><br>
     3\. **Search unimported UDFs**를 선택합니다.
     4\. 원하는 UDF 위에 마우스를 올리고 **Import**를 선택합니다. <br><br> <img alt="Pipeline Builder에서 UDF 가져오기." src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-builder-import-udfs.png" width="500px"> <br><br>
3. 입력 열과 파라미터를 지정해 변환 정의를 채운 다음 **Apply**를 선택합니다.

<img alt="Pipeline Builder에서 구성한 Python 함수 변환." src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-builder-transform.png" width="700px">

이제 Pipeline Builder 그래프에 Python 함수가 표시되며 함수의 출력을 미리 볼 수 있습니다.

<img alt="Pipeline Builder의 Python 함수" src="https://www.palantir.com/docs/resources/foundry/functions/python-functions-builder-ete.png" width="900px">

> **중간 요약**: Reusables 메뉴나 변환 선택기로 UDF를 가져온 뒤, Transform에서 입력 열을 파라미터에 매핑하고 Apply하면 파이프라인에 함수 단계가 추가됩니다. LLM을 호출하는 UDF는 지원되지 않습니다.

<a id="external-api-calls-in-pipeline-builder"></a>
## Pipeline Builder에서 외부 API 호출 (External API calls in Pipeline Builder)

Pipeline Builder에서 외부 시스템으로 API 호출을 하려면 [외부 시스템에 접근할 수 있는 Python 함수](../09_language-agnostic-features/04_api-calls.md)를 게시하면 됩니다. 이렇게 하면 외부 시스템과 통신하는 로직을 작성해 파이프라인의 일부로 사용할 수 있습니다.

Pipeline Builder에서 사용자 정의 함수(UDF)로 사용하려면, 함수에서 사용하는 모든 소스(source)가 파이프라인으로 가져올 수 있도록 구성되어 있어야 합니다. 이 설정을 구성하려면 Data Connection에서 해당 소스로 이동한 다음 **Connection settings > Code import configuration** 탭으로 이동합니다.

![소스를 파이프라인으로 가져올 수 있도록 허용.](https://www.palantir.com/docs/resources/foundry/functions/allow-source-to-be-imported-to-pipelines.png)

소스에서 이 옵션을 활성화하고 Python 함수를 게시하면, 다른 Python 함수와 같은 방식으로 파이프라인에서 사용할 수 있습니다.

**설명**: 여기서 소스(source)는 Data Connection에 등록된 외부 시스템 연결 정보(주소, 인증 정보 등)입니다. 함수 코드는 이 소스를 통해서만 외부로 나갈 수 있고, 파이프라인에서 쓰려면 소스 쪽에서 별도로 허용해 주어야 합니다.

<a id="ontology-access-in-pipeline-builder"></a>
## Pipeline Builder에서의 온톨로지 접근 (Ontology access in Pipeline Builder)

**주의**: Pipeline Builder UDF는 `FoundryClient()`나 Ontology SDK(OSDK)를 통한 직접적인 온톨로지 접근을 지원하지 않습니다. UDF 안에서 `FoundryClient()`를 생성하고 온톨로지에 접근하면 `EnvironmentNotConfigured` 오류가 반환됩니다. 이 제한은 빌드 사이에서 데이터의 마킹(marking)이 해제되거나 데이터가 유출되는 것을 막는 데 도움이 됩니다.

Pipeline Builder UDF에서 온톨로지 데이터에 접근하려면 다음 방법을 고려하세요.

* **외부 소스 사용(Use an external source):** 온톨로지 쿼리를 수행하는 Python 함수용 외부 소스를 만든 다음, 그 소스를 Pipeline Builder UDF로 가져옵니다. 이렇게 하면 UDF 컨텍스트에서 직접 온톨로지를 쿼리할 때 생기는 인증 및 권한 문제를 피할 수 있습니다. 소스를 구성하려면 Data Connection에서 소스로 이동해 [위에서](#external-api-calls-in-pipeline-builder) 설명한 대로 **Connection settings > Code import configuration**을 활성화합니다.
* **온톨로지 기반 데이터셋 조인(Join Ontology-backed datasets):** 사용 사례가 허용한다면, 관련 온톨로지 기반 데이터를 담은 별도의 데이터셋을 유지하고 이를 파이프라인에 조인합니다. 이렇게 하면 온톨로지 API 호출을 피할 수 있고, 중복 제거나 존재 여부 확인도 할 수 있습니다.

**설명**: 마킹(marking)은 Foundry에서 데이터에 붙이는 접근 제어 표식입니다. 파이프라인 출력 데이터셋은 입력의 마킹을 이어받는데, UDF가 온톨로지에서 임의로 데이터를 읽어 오면 그 데이터의 마킹이 출력에 전달되지 않을 수 있으므로 직접 접근을 막는 것입니다. 두 번째 방법은 예를 들어 Customer 객체 타입의 백킹 데이터소스(backing datasource)인 데이터셋을 파이프라인 입력으로 추가하고 `customer_id`로 조인하는 식입니다.

> **중간 요약**: 외부 API는 파이프라인 가져오기가 허용된 소스를 통해 호출할 수 있습니다. 온톨로지에는 UDF에서 직접 접근할 수 없으므로 외부 소스를 거치거나 온톨로지 기반 데이터셋을 조인합니다.

## 정리

- Pipeline Builder는 Python UDF를 사이드카 컨테이너로 실행하므로 별도 배포가 필요 없습니다.
- UDF는 행마다 한 번 호출되어 스칼라 값(또는 구조체)을 반환하고, 반환값이 새 열이 됩니다. 온톨로지 타입은 지원되지 않습니다.
- Reusables 또는 변환 선택기로 UDF를 가져와 Transform에서 입력 열을 파라미터에 매핑합니다. LLM 호출 UDF는 지원되지 않습니다.
- 외부 API 호출은 Code import configuration이 활성화된 소스를 통해 가능합니다.
- `FoundryClient()`나 OSDK로 온톨로지에 직접 접근할 수 없으며, 외부 소스나 온톨로지 기반 데이터셋 조인으로 우회합니다.
