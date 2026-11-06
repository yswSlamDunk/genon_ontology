# Python 객체 함수 (Functions on objects)

- 원문: https://www.palantir.com/docs/foundry/functions/python-functions-on-objects/
- 사이드바 위치: Define Ontologies > Functions > Python > Functions on objects

이 페이지는 Python 함수(function)에서 온톨로지 객체를 입력으로 받거나 검색하는 방법을 다룹니다. 그러려면 먼저 Python 온톨로지 SDK(OSDK)를 생성하고 설치해야 하므로, 페이지의 앞부분은 SDK 생성 절차를, 뒷부분은 객체를 다루는 함수 예제를 설명합니다.

Python 온톨로지 SDK를 사용해 온톨로지와 상호 작용하는 함수를 작성할 수 있습니다.

<a id="generate-a-python-ontology-sdk"></a>
## Python 온톨로지 SDK 생성하기 (Generate a Python Ontology SDK)

Python 온톨로지 SDK 클라이언트를 생성하려면 [**Resource imports** 사이드바](../12_typescript-v1/08_resource-imports-sidebar.md)로 이동해 **Add > Ontology**를 선택합니다. 그런 다음 원하는 온톨로지를 고르고, 함수에서 다루고 싶은 객체와 링크를 임포트합니다. 저장해서 선택을 확정하면 대응하는 OSDK가 아직 만들어지지 않았다는 배너가 나타납니다.

**SDK Generation** 탭으로 이동해 OSDK를 생성하고 설치합니다.

**주의**: SDK 생성이 `cannot import name 'Equipment2' from 'ontology_sdk.ontology.objects'` 같은 임포트 오류를 반환하면, 인터페이스 아래쪽의 파란색 막대에서 온톨로지를 선택했는지 확인하세요. 객체 타입을 임포트하는 것만으로는 SDK 생성에 필요한 온톨로지가 선택되지 않습니다.

![새 SDK 만들기.](https://www.palantir.com/docs/resources/foundry/functions/python-sdk-create-new.png)

아직 OSDK가 생성된 적이 없다면 생성할 패키지의 이름을 입력하라는 안내가 나옵니다. 패키지 이름은 첫 번째 버전이 생성된 뒤에는 바꿀 수 없습니다.

**Create new version**을 선택한 뒤 이 화면에서 생성 진행 상황을 지켜볼 수 있습니다.

![생성 중인 SDK 패키지.](https://www.palantir.com/docs/resources/foundry/functions/python-sdk-package-generating.png)

생성이 끝나면 <img src="https://www.palantir.com/docs/resources/foundry/functions/python-sdk-package-install-icon.png" alt="설치"> 버튼으로 새로 생성된 버전을 설치해야 합니다.

![설치할 준비가 된 생성된 SDK 패키지.](https://www.palantir.com/docs/resources/foundry/functions/python-sdk-package-ready-to-install.png)

그러면 태스크 러너(task runner) 패널에서 대화형 설치가 시작됩니다. 이 태스크가 성공적으로 끝나면(Task Runner에 `BUILD SUCCESSFUL`이 표시됨) 코드 어시스트(code assist) 세션에서 OSDK 코드 자동 완성을 사용할 수 있습니다.

`meta.yml` 파일도 생성된 패키지를 참조하도록 갱신됩니다. 설치 도우미를 쓰는 대신 `meta.yml`을 직접 수정할 수도 있지만, 그렇게 하면 변경 사항을 반영하기 위해 코드 어시스트 세션을 다시 빌드해야 합니다.

![설치된 SDK 패키지가 포함된 meta.yml.](https://www.palantir.com/docs/resources/foundry/functions/python-sdk-meta-yml-updated.png)

사이드바에서 리소스를 추가로 임포트할 때마다, 그 리소스를 포함한 새 OSDK 버전을 생성하고 설치하라는 안내가 나옵니다. 또한 임포트한 리소스를 수정한 경우(예: 이미 임포트한 객체 타입에 새 속성(property)을 추가한 경우)에도 변경 사항을 반영하려면 새 OSDK 버전을 생성해야 합니다.

생성된 OSDK는 구조체(struct) 속성을 위한 클래스도 제공합니다. 각 구조체 속성 클래스는 해당 객체 전용 모듈에서 임포트합니다.

```python
from ontology_sdk.ontology.objects import MyObjectType
from ontology_sdk.ontology.objects.my_object_type import MyStructPropertyClass
```

생성된 구조체 속성 클래스를 사용하는 예는 [구조체 속성 편집하기](05_python-ontology-edits.md#edit-struct-properties)를 참고하세요.

**설명**: 절차를 순서대로 정리하면 (1) 리소스 임포트 사이드바에서 온톨로지 선택과 객체 및 링크 임포트, (2) **SDK Generation** 탭에서 새 버전 생성, (3) 설치 버튼으로 설치, (4) `meta.yml`에 패키지 의존성 추가 확인입니다. 이 SDK는 생성 시점의 객체 타입 정의를 바탕으로 만들어진 코드이므로, 온톨로지 쪽 정의가 바뀌면 SDK도 새로 생성해야 코드에서 새 속성을 쓸 수 있습니다. 구조체 속성은 속성 하나 안에 여러 하위 필드를 가진 값(예: `address` 속성 안의 `city`, `zip`)이며, SDK는 이를 Python 클래스로 만들어 줍니다.

> **중간 요약**: Python 함수에서 객체를 다루려면 리소스 임포트 사이드바에서 온톨로지와 객체를 고른 뒤 **SDK Generation** 탭에서 OSDK를 생성하고 설치해야 합니다. 리소스를 추가하거나 바꿀 때마다 새 OSDK 버전을 생성해야 하며, 패키지 이름은 처음 정한 뒤 바꿀 수 없습니다.

<a id="examples"></a>
## 예제 (Examples)

`brand`와 `capacity` 속성을 가진 `Aircraft`라는 예제 객체 타입이 있을 때, `Aircraft` 객체를 받아 요약하는 함수는 다음과 같이 작성할 수 있습니다.

```python
from functions.api import function
from ontology_sdk.ontology.objects import Aircraft

@function
def aircraft_input_example(aircraft: Aircraft) -> str:
    return f"{aircraft.brand} aircraft, holds {aircraft.capacity} passengers"
```

**설명**: 입력은 Aircraft 객체 하나이고 출력은 문자열입니다. 객체의 속성은 `aircraft.brand`처럼 클래스 인스턴스의 필드로 읽습니다. 예를 들어 `brand`가 "Boeing", `capacity`가 180인 객체를 넘기면 `"Boeing aircraft, holds 180 passengers"`를 반환합니다. Workshop 같은 화면에서 이 함수를 호출하면 사용자가 고른 Aircraft 객체가 인자로 전달됩니다.

또한 특정 수용 인원 기준을 만족하는 `Aircraft` 객체를 검색하려면 다음과 같이 작성할 수 있습니다.

```python
from functions.api import function
from ontology_sdk import FoundryClient
from ontology_sdk.ontology.objects import Aircraft
from ontology_sdk.ontology.object_sets import AircraftObjectSet

@function
def aircraft_search_example() -> AircraftObjectSet:
    client = FoundryClient()
    return client.ontology.objects.Aircraft.where(Aircraft.object_type.capacity > 100)
```

**설명**: `FoundryClient()`로 온톨로지에 접근하는 클라이언트를 만들고, `Aircraft.where(...)`로 `capacity`가 100보다 큰 항공기만 고른 객체 집합(object set)을 반환합니다. SQL로 쓰면 `SELECT * FROM aircraft WHERE capacity > 100`에 해당합니다. 반환 타입이 리스트가 아니라 `AircraftObjectSet`이라는 점이 중요합니다. 객체 집합은 조건을 담은 질의 정의이므로, 호출하는 쪽에서 추가 필터링이나 집계를 이어 붙일 수 있습니다.

Python OSDK는 pandas DataFrame과의 상호 운용 같은 베타 기능도 제공합니다.

```python
from functions.api import function
from ontology_sdk.ontology.object_sets import AircraftObjectSet

@function
def aircraft_dataframe_example(aircrafts: AircraftObjectSet) -> int:
    df = aircrafts.to_dataframe()
    return df['capacity'].sum()
```

**설명**: 입력받은 객체 집합을 `to_dataframe()`으로 pandas DataFrame(행과 열로 이루어진 표 형태의 메모리 내 자료구조)으로 바꾼 뒤, `capacity` 열의 합계를 반환합니다. 객체가 3개이고 수용 인원이 각각 180, 150, 300이면 630을 반환합니다. 객체 하나가 DataFrame의 행 하나, 속성 하나가 열 하나가 됩니다.

자세한 내용은 [Python 온톨로지 SDK 문서](https://www.palantir.com/docs/foundry/ontology-sdk/python-osdk/)를 참고하세요.

> **중간 요약**: 생성된 OSDK의 클래스를 타입 힌트로 쓰면 객체를 입력으로 받을 수 있고, `FoundryClient`와 `where`로 객체 집합을 검색할 수 있으며, `to_dataframe()`(베타)으로 pandas DataFrame으로 바꿔 분석할 수 있습니다.

## 정리

- Python 함수에서 온톨로지를 다루려면 리소스 임포트 사이드바에서 객체와 링크를 임포트하고 **SDK Generation** 탭에서 OSDK를 생성하고 설치해야 합니다.
- SDK 생성 시 임포트 오류가 나면 아래쪽 파란 막대에서 온톨로지를 선택했는지 확인합니다.
- 리소스를 추가하거나 수정할 때마다 새 OSDK 버전이 필요하고, 패키지 이름은 첫 버전 이후 바꿀 수 없습니다.
- 생성된 클래스로 객체를 입력받고, `FoundryClient`로 객체 집합을 검색하며, 구조체 속성 클래스와 DataFrame 변환도 사용할 수 있습니다.
