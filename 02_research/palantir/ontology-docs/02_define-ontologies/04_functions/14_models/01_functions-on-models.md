# 모델 기반 함수 (Functions on models)

- 원문: https://www.palantir.com/docs/foundry/functions/functions-on-models/
- 사이드바 위치: Define Ontologies > Functions > Models > Functions on models

이 페이지는 Foundry에 배포된 머신러닝 모델을 함수(function) 코드 안에서 호출하는 방법을 설명합니다. 모델 배포마다 자동으로 만들어지는 "모델 함수"를 저장소로 가져와 Python, TypeScript v2, TypeScript v1 함수에서 부르는 코드 예제와, 2026년 2월부터 바뀐 온톨로지 귀속 방식, 성능상 제한을 다룹니다. 모델 예측 결과를 온톨로지 객체와 묶어 쓰려면 이 연결 방법을 알아야 합니다.

함수가 실행되는 동안 모델을 호출하는 방식으로, 온톨로지 맥락에서 모델을 배포할 수 있습니다. 모델 함수(model function)는 라이브 모델 배포를 감싸는 자동 생성 래퍼(wrapper)로, 함수 저장소에 가져와 코드에서 호출할 수 있습니다. 이를 통해 모델 예측 주변에 사용자 정의 비즈니스 로직을 추가하거나, 모델을 온톨로지 객체와 통합하거나, 여러 모델 호출을 조율할 수 있습니다.

**설명**: "라이브 배포(live deployment)"는 학습된 모델을 서버에 올려 두고 요청이 오면 즉시 예측을 돌려주도록 만든 상태를 말합니다. 모델 함수는 이 서버에 HTTP 요청을 보내는 코드를 대신 만들어 주는 래퍼입니다. 함수 작성자는 네트워크 호출 세부 사항을 몰라도 `flightModelDeployment(입력)`처럼 일반 함수를 부르듯 예측을 받을 수 있습니다.

<a id="overview"></a>
## 개요 (Overview)

모델 함수는 두 가지 유형의 배포에서 게시할 수 있습니다.

* **[직접 모델 배포(Direct model deployments)](https://www.palantir.com/docs/foundry/manage-models/create-a-model-deployment/):** 모델 페이지에서 직접 게시합니다.
* **[Modeling Objective 라이브 배포(Modeling Objective live deployments)](https://www.palantir.com/docs/foundry/manage-models/set-up-live/):** Modeling Objective의 배포 세부 정보 페이지에서 게시합니다.

두 방법 모두 모델과 같은 입력 및 출력 API를 가진 함수를 만듭니다. 함수 동작, 버전 업그레이드, 구성 옵션에 대한 자세한 내용은 [모델 함수 개발자 가이드(Model functions developer guide)](https://www.palantir.com/docs/foundry/model-integration/model-functions-guide/)를 참고하세요.

모델 함수는 TypeScript v1, TypeScript v2, Python 함수에서 모두 완전히 지원됩니다.

> **중간 요약**: 모델 함수는 라이브 모델 배포를 감싸 자동 생성되는 함수이며, 직접 모델 배포나 Modeling Objective 라이브 배포에서 게시할 수 있습니다. 세 가지 함수 언어(TSv1, TSv2, Python) 모두에서 사용할 수 있습니다.

<a id="import-a-live-deployment-in-a-repository"></a>
## 저장소에 라이브 배포 가져오기 (Import a live deployment in a repository)

라이브 배포에 대한 함수가 [모델 자체에서](https://www.palantir.com/docs/foundry/manage-models/create-a-model-deployment/#3-publish-a-function-for-the-deployment) 또는 [Modeling Objective에서](https://www.palantir.com/docs/foundry/manage-models/set-up-live/#publish-function) 만들어지고 나면, 특정 저장소에서 사용하려면 그 함수를 가져와야(import) 합니다. 저장소 왼쪽 사이드바의 **Resource Imports** 메뉴에서 **Add**와 **Query Functions**를 선택하세요. 모델은 게시할 때 정한 함수 이름으로 검색할 수 있습니다. Python과 TypeScript v2 저장소는 아래 섹션에서 설명하는 것처럼 온톨로지에 연결된 모델 함수만 지원합니다.

**참고**: TypeScript v1 저장소에서는 **Models**를 선택해 모델 함수를 가져올 수도 있으며, 이는 **Query Functions**에서 가져오는 것과 기능상 같습니다.

선호되는 [모델 게시 대화 상자(model publication dialog)](https://www.palantir.com/docs/foundry/manage-models/set-up-live/#publish-function) 대신 Modeling Objectives의 **API Name** 카드를 사용하는 레거시 모델 기반 함수는 여전히 **Modeling Objectives** 섹션에서 가져올 수 있지만, 지원 종료(sunset) 중입니다.

**설명**: "가져오기"는 저장소의 의존성 목록에 해당 모델 함수를 등록하는 일입니다. 등록하면 그 함수의 입력/출력 타입 정보가 코드 생성되어, 코드에서 import 문으로 불러 쓸 수 있게 됩니다. 패키지 관리자에서 라이브러리를 추가하는 것과 같은 단계입니다.

<a id="ontology-or-space-bound-functions"></a>
## 온톨로지 귀속 함수와 스페이스 귀속 함수 (Ontology or space-bound functions)

2026년 2월부터 새로 만드는 모든 모델 함수는 온톨로지에 귀속됩니다. 이는 온톨로지 리소스 가져오기만 허용하는 [TypeScript v2 및 Python 함수](03_language-models-python-tsv2.md)에서 사용하기 위한 전제 조건입니다. 이 날짜 이전에는 모델 함수가 모델의 [스페이스(space)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/)에 귀속되었습니다. TypeScript v1은 두 유형의 모델 함수를 모두 가져올 수 있지만, [아래에서 자세히 설명하는 것처럼](#if-the-function-is-registered-to-an-ontology) 가져오기와 사용 방식이 조금 다릅니다.

함수가 온톨로지에 귀속되어 있는지 확인하려면 모델로 이동하세요. 온톨로지에 귀속되지 않은 모델 함수에는 마이그레이션이 가능하다는 표시가 나타납니다. [함수를 온톨로지 귀속으로 마이그레이션하는 방법을 더 알아보세요.](#migrating-model-functions-to-ontology-bound-functions)

**주의**: Marketplace는 저장소로 가져온 모델 함수를 추적합니다. [지원되는 모델 함수를 모델 및 직접 배포와 함께 패키징](https://www.palantir.com/docs/foundry/model-integration/marketplace-models/#model-functions)하거나, 설치 중에 사용자가 선택하는 입력으로 구성할 수 있습니다. 모델 함수를 가져오지 않고 Platform SDK로 직접 질의하는 모델 함수는 Marketplace가 추적하지 않습니다.

**설명**: 스페이스(space)는 Foundry에서 프로젝트와 리소스를 묶는 보안 및 조직 단위이고, 온톨로지는 객체 타입, 액션 타입, 함수 등을 등록하는 별도 단위입니다. 모델 함수가 어느 쪽에 "소속"되느냐에 따라 어느 언어의 저장소에서 보이는지가 달라지므로, 2026년 2월 이전에 만든 함수를 TSv2나 Python에서 쓰려면 온톨로지 귀속으로 마이그레이션해야 합니다.

> **중간 요약**: 2026년 2월 이후 생성되는 모델 함수는 온톨로지에 귀속되며, TSv2와 Python은 이런 함수만 쓸 수 있습니다. 이전의 스페이스 귀속 함수는 TSv1에서만 쓸 수 있고 마이그레이션이 가능합니다. Marketplace는 저장소로 가져온 모델 함수만 추적합니다.

<a id="call-a-model-function-from-python-or-typescript-v2-functions"></a>
## Python 또는 TypeScript v2 함수에서 모델 함수 호출하기 (Call a model function from Python or TypeScript v2 functions)

라이브 배포에 대한 함수가 만들어지면, 특정 저장소에서 사용하려면 가져와야 합니다. 그다음에는 [다른 쿼리 함수와 똑같이](../09_language-agnostic-features/02_query-functions.md#call-a-query-function) 질의할 수 있습니다.

<a id="example-code-python"></a>
### 예제 코드: Python (Example code: Python)

```python
from functions.api import function, Double
from foundry_sdk_runtime import AllowBetaFeatures
from ontology_sdk import FoundryClient
from ontology_sdk.ontology.objects import Flight


@function(beta=True)
def predict_flight_delays(flight: Flight) -> Double:
    # 모델 함수의 API에 맞게 입력을 준비합니다.
    model_output = FoundryClient().ontology.queries.flight_model_deployment(
        df_in=[
            {
                "lastArrivalTime": flight.last_arrival_time,
                "lastExpectedArrivalTime": flight.last_expected_arrival_time,
            },
        ]
    )
    return model_output.df_out[0].prediction
```

**설명**: 이 함수는 `Flight` 객체 하나를 입력받아 지연 예측 값(실수)을 반환합니다. 핵심 줄은 `FoundryClient().ontology.queries.flight_model_deployment(...)`로, 온톨로지에 쿼리 함수로 등록된 모델 함수를 이름으로 호출합니다. 모델은 표 형식 입력 `df_in`을 기대하므로, 객체의 속성 두 개를 꺼내 행 하나짜리 리스트로 만들어 넘깁니다. 결과 `df_out`도 표이므로 첫 행(`[0]`)의 `prediction` 열 값을 꺼내 반환합니다.

<a id="example-code-typescript-v2"></a>
### 예제 코드: TypeScript v2 (Example code: TypeScript v2)

(원문에는 같은 동작을 TypeScript v2로 작성한 예제도 있습니다. `@osdk/client`의 `Client`를 받아 `client(flightModelDeployment).executeFunction({ "df_in": [...] })`로 모델 함수를 호출하고 `modelOutput.df_out[0].prediction`을 반환하는 구조로, Python 예제와 입력과 출력이 같습니다.)

> **중간 요약**: Python과 TSv2에서는 모델 함수를 가져온 뒤 일반 쿼리 함수처럼 호출합니다. 객체 속성으로 모델 입력 표를 만들고, 출력 표에서 예측 값을 꺼내 반환하는 것이 기본 패턴입니다.

<a id="write-a-model-backed-typescript-v1-function"></a>
## 모델 기반 TypeScript v1 함수 작성하기 (Write a model-backed TypeScript v1 function)

<a id="if-the-model-function-is-registered-to-a-space"></a>
### 모델 함수가 스페이스에 등록된 경우 (If the model function is registered to a space)

먼저 함수를 가져와야 합니다.

```typescript
// 모델 함수가 온톨로지가 아니라 스페이스에 귀속되어 있다면,
// Resource imports 사이드바에서 import 스니펫을 복사하세요.
```

그다음 flight 하나를 받아 모델용 데이터를 준비하고 모델 실행 결과를 해석하는 함수를 작성합니다. 모델은 [모델의 입력 및 출력 명세, 즉 API](https://www.palantir.com/docs/foundry/integrate-models/model-adapter-api/)를 따르는 비동기 함수로 가져와집니다. 이 덕분에 TypeScript는 컴파일 시점에 올바른 데이터 구조를 모델 배포로 보내고 받는지 보장할 수 있습니다.

모델의 API가 정확히 하나의 표 형식 입력과 정확히 하나의 표 형식 출력을 선언하고 [**Enable row-wise processing** 옵션](https://www.palantir.com/docs/foundry/model-integration/model-functions-guide/#row-wise-publishing)(기본값)이 켜져 있으면, 연결된 함수는 입력에 지정된 열에 해당하는 속성을 가진 TypeScript 객체 하나를 받습니다. 추가 입력이나 출력을 선언한 모델 API는 행 단위 처리(row-wise processing) 대상이 아닙니다. 아래의 `predictFlightDelaysRowWise` 함수가 이 패턴을 보여 줍니다. 또는 함수에서 모델을 객체와 함께 쉽게 쓰기 위해 [모델 API에서 Object나 ObjectSet을 직접 사용하는 방법](https://www.palantir.com/docs/foundry/integrate-models/model-adapter-reference/#for-object-inputs)을 고려해 보세요.

아래의 `predictFlightDelays` 함수는 [`FunctionsMap`](../04_types-reference.md#map)을 반환합니다. 이는 객체나 스칼라 값을 키로 하는 맵을 반환할 때 쓰는 TypeScript v1 타입입니다. 이 예제에서는 각 `Flight` 객체를 예측된 지연 값에 매핑합니다.

```typescript
import { Function, Double, FunctionsMap } from "@foundry/functions-api";
import { Flight } from "@foundry/ontology-api";

@Function()
public async predictFlightDelaysRowWise(flight: Flight): Promise<Double> {
    // 모델 함수의 API에 맞게 입력을 준비합니다.
    // 이 모델 함수는 flight 하나를 기대합니다.
    // 여러 flight를 한 번에 처리하려면
    // 행 단위 처리를 끈 새 모델 함수 버전을 게시하세요.

    // 모델 API에서 Object를 직접 사용하면
    // 모델 API와 객체 타입 속성 사이의 번거로운 매핑을 피할 수 있습니다.
    const modelInput = {
        "lastArrivalTime": flight.lastArrivalTime,
        "lastExpectedArrivalTime": flight.lastExpectedArrivalTime,
    };
    // 라이브 배포를 호출합니다.
    const modelOutput = await FlightModelDeploymentRowWise(modelInput);
    return modelOutput.prediction;
}
```

**설명**: 행 단위 처리가 켜져 있으면 모델 함수는 표 전체가 아니라 "행 하나"에 해당하는 객체 `{ lastArrivalTime, lastExpectedArrivalTime }`를 받고, 출력도 행 하나(`modelOutput.prediction`)로 돌려줍니다. 그래서 `df_in`이나 `[0]` 인덱싱이 필요 없습니다. `await`가 붙는 이유는 모델 호출이 네트워크를 거치는 비동기 작업이기 때문입니다.

(원문에는 행 단위 처리가 꺼진 경우의 `predictFlightDelays` 예제도 있습니다. flight 배열을 `map`으로 `dfIn` 행 목록으로 바꿔 `FlightModelDeployment({"df_in": dfIn})`를 한 번 호출하고, 반복문에서 `functionsMap.set(flights[i], modelOutput.df_out[i].prediction)`으로 각 flight와 예측 값을 짝지어 `FunctionsMap<Flight, Double>`을 반환합니다. 입력 행 순서와 출력 행 순서가 같다는 점을 이용해 i번째 flight에 i번째 예측을 붙입니다.)

위 예제는 다음과 같은 모델 API를 가정합니다.

```python
import palantir_models as pm


class ExampleModelAdapter(pm.ModelAdapter):
    ...

    @classmethod
    def api(cls):
        inputs = {
            "df_in": pm.Pandas(columns=[("lastArrivalTime", datetime.datetime), ("lastExpectedArrivalTime", datetime.datetime)])
        }
        outputs = {
            "df_out": pm.Pandas(columns=[("prediction", float)])
        }
        return inputs, outputs
    ...

```

**설명**: 모델 어댑터(model adapter)의 `api()` 메서드는 모델이 받는 입력과 내보내는 출력의 스키마를 선언합니다. 여기서는 입력 `df_in`이 datetime 열 두 개를 가진 pandas 표이고, 출력 `df_out`이 float 열 `prediction` 하나를 가진 표입니다. 모델 함수의 TypeScript/Python 타입은 이 선언에서 생성되므로, 함수 코드의 `"df_in"`, `"lastArrivalTime"`, `prediction` 같은 이름이 모두 여기서 왔습니다.

<a id="if-the-function-is-registered-to-an-ontology"></a>
### 함수가 온톨로지에 등록된 경우 (If the function is registered to an ontology)

이 경우 아래 스니펫의 주석에서 설명하는 것처럼 가져오기 구문과 질의 구문을 모두 바꿔야 합니다.

```typescript
import { Function, Double } from "@foundry/functions-api";
// 온톨로지 귀속 모델 함수를 쓰려면 Queries import를 추가합니다
import { Queries, Flight } from "@foundry/ontology-api";

export class MyFunctions {
    @Function()
    public async predictFlightDelays(flight: Flight): Promise<Double> {
        // Queries에서 API Name으로 모델을 호출합니다
        const modelOutput = await Queries.flightModelDeployment({
            "df_in": [
                {
                    "lastArrivalTime": flight.lastArrivalTime,
                    "lastExpectedArrivalTime": flight.lastExpectedArrivalTime,
                },
            ]
        });
        return modelOutput.df_out[0].prediction;
    }
}
```

**설명**: 스페이스 귀속 함수는 `FlightModelDeployment(...)`처럼 가져온 이름을 바로 호출했지만, 온톨로지 귀속 함수는 `@foundry/ontology-api`의 `Queries` 객체를 통해 `Queries.flightModelDeployment(...)`처럼 API Name으로 호출합니다. 입력 구조(`df_in` 표)와 출력 처리(`df_out[0].prediction`)는 Python 예제와 같습니다.

<a id="migrating-model-functions-to-ontology-bound-functions"></a>
### 모델 함수를 온톨로지 귀속 함수로 마이그레이션하기 (Migrating model functions to ontology-bound functions)

사용자 인터페이스에서 스페이스 귀속 모델 함수를 온톨로지 귀속 함수로 마이그레이션하면, 그 모델을 사용하는 TypeScript v1 함수의 기존 게시 버전은 계속 동작합니다. 그러나 가져오기 구문이 더 이상 인식되지 않으므로, 모델 함수를 사용하는 저장소의 미리 보기(preview)와 새 릴리스 태그 지정은 더 이상 동작하지 않습니다.

마이그레이션 후 TypeScript v1 함수를 업데이트하려면 다음을 수행합니다.

1. 코드 저장소를 열고 **Resource imports** 사이드바를 선택합니다.
2. resources.json 파일을 새 버전으로 업데이트하여, 새로 만들어진 모델 함수 버전을 선택합니다.
3. 위에서 설명한 쿼리 함수 구문을 사용하도록 함수 코드를 업데이트합니다. 자세한 내용은 [쿼리 함수 호출하기](../09_language-agnostic-features/02_query-functions.md#call-a-query-function) 전용 문서를 참고하세요.

**주의**: [Foundry Platform SDK](https://www.palantir.com/docs/foundry/dev-toolchain/overview/#platform-sdks)와 [Functions.Query ↗](https://github.com/palantir/foundry-platform-python/blob/develop/docs/v2/Functions/Query.md) 메서드를 통한 모델 함수 직접 사용은 마이그레이션 즉시 깨집니다. 이 사용 방식은 함수를 API 이름으로 참조하는데, API 이름은 모든 모델 함수 버전에 걸쳐 한꺼번에 전역으로 마이그레이션되기 때문입니다. 이런 사용처를 고치려면 마이그레이션 후 API 이름을 새 값으로 업데이트하세요.

**설명**: 정리하면 마이그레이션의 영향은 두 갈래입니다. 이미 게시된 TSv1 함수 버전은 빌드가 끝난 산출물이므로 그대로 동작하지만, 소스 코드를 다시 빌드(미리 보기, 새 태그)하려면 import와 호출 구문을 고쳐야 합니다. 반면 API 이름 문자열로 직접 부르던 외부 코드는 이름 자체가 바뀌므로 즉시 실패합니다.

> **중간 요약**: TSv1에서 스페이스 귀속 모델 함수는 가져온 이름으로 직접 호출하고, 행 단위 처리 여부에 따라 행 하나 또는 표 전체를 주고받습니다. 온톨로지 귀속 함수는 `Queries.<API Name>`으로 호출합니다. 마이그레이션 후에는 resources.json과 호출 구문을 갱신해야 하며, API 이름으로 직접 호출하던 Platform SDK 사용처는 즉시 깨집니다.

<a id="performance-considerations"></a>
## 성능 고려 사항 (Performance considerations)

모델은 함수 런타임의 일부로 실행되므로 모든 표준 [제한](../07_function-management/02_manage-functions.md#enforced-limits)이 적용됩니다.
함수가 액션(Action)을 뒷받침한다면, 결과로 생기는 편집(edit) 수에 [추가 제한](../../03_action-types/17_scale-property-limits.md#edit-limits)이 있습니다.

라이브 배포 호출은 모델 입력과 출력 데이터를 네트워크로 주고받으며, 상한은 50 MB입니다. 이 네트워크 전송 시간은 함수의 [구성된 시간 제한](../07_function-management/02_manage-functions.md#time-limit)에 포함됩니다. 함수의 타임아웃을 늘리려면 Palantir Support에 문의하세요.

**설명**: 예를 들어 함수 시간 제한이 30초인데 모델에 대량의 행을 보내 응답을 받는 데 25초가 걸리면, 나머지 로직에 쓸 시간은 5초뿐입니다. 큰 입력을 한 번에 보내기보다 필요한 열만 골라 보내는 것이 전송량과 시간 모두에 유리합니다.

> **중간 요약**: 모델 호출은 함수의 실행 제한과 액션 편집 제한을 그대로 받으며, 입출력 전송은 최대 50 MB이고 전송 시간도 함수 시간 제한에 포함됩니다.

## 정리

- 모델 함수는 라이브 모델 배포를 감싼 자동 생성 함수로, 저장소의 **Resource Imports**에서 **Query Functions**로 가져와 사용합니다.
- 2026년 2월 이후 모델 함수는 온톨로지에 귀속되며, TSv2와 Python은 온톨로지 귀속 함수만 쓸 수 있습니다.
- Python과 TSv2에서는 일반 쿼리 함수처럼 호출하고, TSv1에서는 스페이스 귀속(직접 호출)과 온톨로지 귀속(`Queries.<API Name>`)에 따라 구문이 다릅니다.
- 행 단위 처리가 켜지면 행 하나 단위로, 꺼지면 표 단위로 입출력을 주고받습니다.
- 마이그레이션 시 TSv1 소스와 Platform SDK 직접 호출을 갱신해야 하며, 모델 호출은 함수 제한과 50 MB 전송 상한을 받습니다.
