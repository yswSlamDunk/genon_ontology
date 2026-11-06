# 함수의 계측과 텔레메트리 (Instrumentation and telemetry)

- 원문: https://www.palantir.com/docs/foundry/functions/instrumentation-telemetry/
- 사이드바 위치: Define Ontologies > Functions > Function management > Instrumentation and telemetry

이 페이지는 함수(function) 코드 안에서 로그(log)와 스팬(span) 같은 텔레메트리(telemetry)를 내보내, 운영 중인 워크플로를 모니터링하고 디버깅하는 방법을 설명합니다. 함수 언어(TypeScript v1, TypeScript v2, Python)마다 지원하는 텔레메트리 종류가 다르므로 표로 비교하고, 로그와 사용자 정의 스팬을 만드는 예제를 보여 줍니다.

**설명**: 텔레메트리는 실행 중인 프로그램이 바깥으로 내보내는 관측 데이터입니다. 보통 세 종류로 나눕니다. 로그는 "언제 무슨 일이 있었는지"를 적은 텍스트 기록, 스팬은 "어떤 작업이 언제 시작해서 얼마나 걸렸는지"를 기록한 구간 데이터(여러 스팬이 모여 요청 하나의 흐름을 보여 주는 트레이스(trace)가 됩니다), 지표(metric)는 실행 횟수나 평균 실행 시간처럼 집계된 숫자입니다. 계측(instrumentation)은 코드에 이런 데이터를 내보내는 장치를 심는 작업을 말합니다. 이 페이지에 나오는 OpenTelemetry는 이런 텔레메트리를 내보내는 방식을 표준화한 오픈소스 SDK입니다.

함수에서 특정 종류의 텔레메트리를 내보내 운영 워크플로를 모니터링하고 디버깅할 수 있습니다.

함수가 내보낸 텔레메트리를 보는 방법은 [온톨로지와 AIP 관측성(observability) 문서](https://www.palantir.com/docs/foundry/aip-observability/overview/)를 참고하세요.

<a id="supported-telemetry-types"></a>
## 지원되는 텔레메트리 유형 (Supported telemetry types)

다음 표는 함수 언어별로 지원되는 텔레메트리 유형을 보여 줍니다. 모든 함수 유형에 대해 함수의 전체 실행 시간을 덮는 스팬 하나와 요청 로그(request log) 하나가 자동으로 생성됩니다.

| 언어 | 로그(Logs) | 스팬(Spans) | 지표(Metrics) |
| ------------- | ---- | ----------------------------- | ------------------------------- |
| TypeScript v1 | 예 | 제품이 정의한 스팬만\[1] | 제품이 정의한 지표만\[2] |
| TypeScript v2 | 예 | 예\[3] | 제품이 정의한 지표만\[2] |
| Python | 예 | 예\[3] | 제품이 정의한 지표만\[2] |

\[1] TypeScript v1 함수에서 제품이 정의한 스팬에는 객체 로드(object load)와 쿼리 실행 같은 작업이 포함됩니다.

\[2] Foundry는 모든 유형의 함수에 대해 전체 실행 시간을 기록합니다.

\[3] TypeScript v2와 Python 함수는 나가는(outbound) 네트워크 요청을 모두 자동으로 계측하며, 사용자 정의 스팬을 추가할 수도 있습니다.

**설명**: "제품이 정의한(product-defined)"은 Foundry가 미리 정해 자동으로 기록하는 것만 있고 개발자가 직접 새 항목을 추가할 수는 없다는 뜻입니다. 정리하면, 로그는 세 언어 모두 직접 남길 수 있고, 사용자 정의 스팬은 TypeScript v2와 Python에서만 만들 수 있으며, 지표는 세 언어 모두 Foundry가 기록하는 실행 시간 등만 제공됩니다.

> **중간 요약**: 모든 함수는 전체 실행을 덮는 스팬과 요청 로그가 자동 생성됩니다. 로그는 모든 언어에서 직접 남길 수 있고, 사용자 정의 스팬은 TypeScript v2와 Python만 지원하며, 지표는 제품이 정의한 것만 있습니다.

<a id="logs"></a>
### 로그 (Logs)

함수에서 사용자 정의 로그를 내보내고 나중에 소급해서 볼 수 있습니다. 원문의 예제는 TypeScript v1, TypeScript v2, Python 함수에서 로그를 내보내는 방법을 보여 줍니다.

TypeScript v2 함수에서는 Foundry가 OpenTelemetry SDK의 전역 로거 프로바이더(global logger provider)를 설정해 두므로, 거기서 로거를 가져와 쓸 수 있습니다. 로깅에 서드파티 라이브러리를 쓰고 싶다면, 전역 로거 프로바이더에서 얻은 로거를 통해 로그를 내보내도록 그 라이브러리를 설정해야 합니다.

```typescript
import { logs } from "@opentelemetry/api-logs";

const logger = logs.getLogger("my-function");

export default function myFunction(name: string): string {
    logger.emit({
        body: "This is a custom log line.",
        attributes: {
            name
        },
    });

    // 전역 console 객체를 써도 됩니다
    console.log(`This is a custom log line, ${name}.`);

    return `Hello, ${name}!`;
}
```

**설명**: TypeScript v2 예제입니다. 파일이 로드될 때 `logs.getLogger("my-function")`으로 전역 로거 프로바이더에서 로거를 하나 가져옵니다. 함수 `myFunction`은 이름 문자열을 받아, `logger.emit`으로 본문(`body`)과 속성(`attributes`, 여기서는 `name` 값)을 담은 로그 한 줄을 내보내고, `console.log`로도 한 줄을 더 남긴 뒤 `Hello, {name}!`을 돌려줍니다. `attributes`에 넣은 값은 나중에 로그를 이름별로 필터링할 때 쓸 수 있는 구조화된 필드가 됩니다. 원문에는 같은 일을 하는 TypeScript v1 예제(`console.log`만 사용)와 Python 예제(표준 `logging` 모듈의 `logger.info` 사용)도 있습니다.

<a id="logging-best-practices"></a>
#### 로깅 모범 사례 (Logging best practices)

다음 로깅 관행을 따르세요.

* **적절한 로그 수준 선택:** 정상 동작에는 `INFO`, 복구 가능한 문제에는 `WARN`, 실패에는 `ERROR`, 자세한 진단 정보에는 `DEBUG`를 사용합니다.
* **관련 맥락 포함:** 실행 흐름을 이해하는 데 도움이 되도록 식별자, 개수, 작업 세부 정보를 추가합니다.
* **민감한 데이터 기록 피하기:** 자격 증명(credential), 민감한 정보가 들어 있을 수 있는 API 응답 전체, 기타 보안상 민감한 내용을 로그에 남기지 않습니다.

효과적인 로그 작성, 서비스 로그 보기, 로그 수준별 필터링에 대한 자세한 안내는 [서비스 로그와 디버깅](https://www.palantir.com/docs/foundry/aip-observability/service-logs-and-debugging/)을 참고하세요.

**설명**: "관련 맥락 포함"의 예를 들면, `"처리 완료"`보다 `"주문 객체 42건 처리 완료, orderId 범위 1001\~1042, 소요 380ms"`처럼 남기는 편이 나중에 어떤 실행에서 무슨 일이 있었는지 찾기 쉽습니다. 로그는 함수 실행자가 아닌 운영자나 다른 개발자도 볼 수 있으므로 비밀번호나 토큰을 남기면 그대로 유출 경로가 됩니다.

<a id="spans"></a>
### 스팬 (Spans)

TypeScript v2와 Python 함수에서는 사용자 정의 스팬을 만들어 특정 작업의 소요 시간을 추적할 수도 있습니다. 다음 예제는 사용자 정의 스팬을 만드는 방법을 보여 줍니다.

TypeScript v2와 Python 함수에서는 Foundry가 OpenTelemetry SDK의 전역 트레이서 프로바이더(global tracer provider)를 설정해 두므로, 거기서 트레이서(tracer)를 가져와 쓸 수 있습니다. 트레이싱에 서드파티 라이브러리를 쓰고 싶다면, 전역 트레이서 프로바이더에서 얻은 트레이서를 통해 트레이스를 내보내도록 그 라이브러리를 설정해야 합니다.

```python
import math

from functions.api import function

from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@function
def sqrt(n: int) -> int:
    with tracer.start_as_current_span("my-custom-span"):
        return math.sqrt(n)
```

**설명**: Python 예제입니다. 모듈이 로드될 때 `trace.get_tracer(__name__)`로 트레이서를 가져옵니다. `sqrt` 함수는 정수 `n`을 받아 제곱근을 계산하는데, 계산을 `with tracer.start_as_current_span("my-custom-span"):` 블록 안에서 수행합니다. `with` 블록에 들어갈 때 이름이 `my-custom-span`인 스팬이 시작되고, 블록을 빠져나올 때(정상 반환이든 예외든) 스팬이 끝나며 그 사이 시간이 기록됩니다. 이렇게 하면 함수 전체 실행 시간 스팬 안에 "제곱근 계산 구간"이 별도로 표시되어, 함수의 어느 부분이 오래 걸리는지 나눠 볼 수 있습니다. 원문에는 `tracer.startActiveSpan`과 `try ... finally { span.end(); }`로 같은 일을 하는 TypeScript v2 예제도 있습니다.

> **중간 요약**: 로그는 OpenTelemetry 로거나 `console.log`, Python `logging`으로 남기며, 적절한 수준, 충분한 맥락, 민감 정보 배제를 지켜야 합니다. TypeScript v2와 Python에서는 전역 트레이서로 사용자 정의 스팬을 만들어 특정 작업의 소요 시간을 따로 측정할 수 있습니다.

## 정리

- 함수는 로그, 스팬, 지표 형태의 텔레메트리를 내보낼 수 있고, 내보낸 텔레메트리는 온톨로지와 AIP 관측성 도구에서 봅니다.
- 모든 함수에는 전체 실행을 덮는 스팬 하나와 요청 로그 하나가 자동으로 생깁니다.
- 사용자 정의 로그는 모든 언어에서, 사용자 정의 스팬은 TypeScript v2와 Python에서만 만들 수 있고, 지표는 제품이 정의한 것만 제공됩니다.
- TypeScript v2와 Python은 Foundry가 설정한 OpenTelemetry 전역 프로바이더를 쓰며, 서드파티 라이브러리도 이를 통해 내보내도록 설정해야 합니다.
- 로그에는 적절한 수준과 맥락을 담되 자격 증명 같은 민감 정보는 남기지 않습니다.
