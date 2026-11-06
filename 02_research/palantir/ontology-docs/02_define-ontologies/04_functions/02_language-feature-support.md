# 언어별 기능 지원 (Feature support by language)

- 원문: https://www.palantir.com/docs/foundry/functions/language-feature-support/
- 사이드바 위치: Define Ontologies > Functions > Feature support by language

이 페이지는 함수(function)를 작성할 수 있는 언어(AIP Logic, TypeScript v1, TypeScript v2, Python)별로 어떤 플랫폼 기능을 쓸 수 있는지 비교한 표와, 언어 선택에 도움이 되는 설명을 담고 있습니다. 특히 TypeScript v1과 v2의 차이, 서버리스(serverless) 실행과 배포(deployed) 실행의 차이를 다룹니다. 새 함수 리포지토리를 만들기 전에 어떤 언어를 고를지 판단하는 근거로 씁니다.

모든 기능이 모든 언어에서 지원되는 것은 아닙니다. 언어별 기능 지원은 아래 표를 참고하세요.

| 언어별 함수 기능 | AIP Logic | TypeScript v1 | TypeScript v2 | Python | 설명 |
| --- | --- | --- | --- | --- | --- |
| 온톨로지 객체 지원 | 예 | 예 | 예 | 예 | 함수에서 [온톨로지 객체에 접근](13_functions-on-objects/02_foo-getting-started.md)하는 기능입니다. |
| 온톨로지 인터페이스 지원 | 아니요 | 아니요 | 예 | 아니요 | 함수에서 온톨로지 인터페이스에 접근하고 편집하는 기능입니다. |
| 온톨로지 편집 지원 | 예 | 예 | 예 | 예 | 함수에서 [온톨로지 객체를 편집](09_language-agnostic-features/01_edits-overview.md)하는 기능입니다. |
| 미디어 처리 지원 | 아니요 | 예 | 부분 | 부분 | [미디어 항목](13_functions-on-objects/09_media.md)을 다루는 기능입니다. TypeScript v1은 문서 OCR과 오디오 전사를 포함한 모든 미디어 작업을 지원합니다. TypeScript v2와 Python은 온톨로지 편집을 통한 미디어 업로드와 미디어 속성에 대한 기본 작업을 지원하지만, 문서 전용 또는 오디오 전용 작업은 지원하지 않습니다. |
| Workshop에서 조회 가능 | 예 | 예 | 예 | 예 | [Workshop 애플리케이션](https://www.palantir.com/docs/foundry/workshop/functions-use/)에서 함수를 호출하는 기능입니다. |
| Pipeline Builder에서 사용 가능 | 아니요 | 아니요 | 아니요 | 예 | [Pipeline Builder 파이프라인](11_python/07_python-functions-builder.md)에서 함수를 호출하는 기능입니다. |
| 모델 기반 함수(functions on models) 지원 | 예 | 예 | 예 | 예 | [함수에서](14_models/01_functions-on-models.md) 라이브 배포된 모델을 실행합니다. TypeScript v2와 Python은 온톨로지에 바인딩된(ontology-bound) 모델 함수가 필요합니다. |
| 언어 모델 통합 | 아니요 | 아니요 | 예 | 예 | 모델 별칭(alias)과 Platform SDK import를 사용해 [프록시 엔드포인트](14_models/03_language-models-python-tsv2.md)로 언어 모델을 호출합니다. |
| 시맨틱 검색 지원 | 예 | 예 | 예 | 예 | 함수를 사용해 [시맨틱 검색](../../03_ontology-search/01_semantic-search/01_overview-semantic-search.md)용 벡터를 만듭니다. |
| 웹훅 지원 | 아니요 | 예 | 부분 | 부분 | [함수에서 웹훅을 호출](12_typescript-v1/10_webhooks.md)하는 기능입니다. TypeScript v1은 웹훅을 직접 호출할 수 있고, TypeScript v2와 Python은 웹훅을 [웹훅 함수(webhook function)](https://www.palantir.com/docs/foundry/data-connection/webhooks-reference/#webhook-functions)로 게시해야 합니다. |
| 외부 API 호출 지원 | 아니요 | 예 | 예 | 예 | [함수 안에서](09_language-agnostic-features/04_api-calls.md) 외부 서비스를 조회합니다. |
| 서버리스 실행 지원 | 예 | 예 | 예 | 예 | 서버리스 함수는 호출될 때 필요에 따라 실행 환경이 생성됩니다. 자세한 내용은 아래 [서버리스 함수](#serverless-functions)를 참고하세요. |
| 배포 실행 지원 | 아니요 | 아니요 | 예 | 예 | 배포된 함수에는 전용 리소스가 할당되어 요청을 처리할 준비가 되어 있습니다. |
| 스테이징 쓰기(staged writes) 지원 \[베타] | 아니요 | 아니요 | 예 | 예 | [TypeScript v2](10_typescript-v2/05_typescript-v2-staged-writes.md)와 [Python](11_python/06_python-staged-writes.md)에서 스테이징 쓰기를 사용해 편집 함수에서 쓰기 후 읽기(read-after-write) 보장과 원자적 실행을 얻는 기능입니다. |
| API 게이트웨이에서 함수 호출 | 예 | 예 | 예 | 예 | API 게이트웨이에서 [쿼리 함수(query function)](09_language-agnostic-features/02_query-functions.md)를 호출하는 기능입니다. |
| Marketplace 지원 | 예 | 예 | 예 | 예 | 함수를 [Marketplace](https://www.palantir.com/docs/foundry/marketplace/overview/)에서 패키징하고 배포하는 기능입니다. |
| 자체 모델 가져오기(Bring-your-own-model) | 예 | 예 | 아니요 | 아니요 | 함수를 [모델로](https://www.palantir.com/docs/foundry/aip/bring-your-own-model/) 등록하는 기능입니다. [함수 인터페이스 방식(function interface method)](https://www.palantir.com/docs/foundry/aip/chat-completion-function-interface-quickstart/)은 TypeScript v1에만 적용되는 레거시 방식입니다. |

**설명**: 표에서 눈여겨볼 차이는 다음과 같습니다. 온톨로지 인터페이스를 다루려면 TypeScript v2만 가능하고, Pipeline Builder에서 쓰려면 Python만 가능합니다. 반대로 문서 OCR(이미지 속 글자를 텍스트로 바꾸는 기능)이나 오디오 전사 같은 미디어 전용 작업은 TypeScript v1에서만 됩니다. 쓰기 후 읽기(read-after-write) 보장은 함수 안에서 객체를 수정한 직후 그 객체를 다시 읽으면 수정된 값이 보인다는 보장으로, 데이터베이스 트랜잭션 안에서 `UPDATE` 후 `SELECT`가 새 값을 돌려주는 것과 같은 성질입니다. API 게이트웨이는 외부 프로그램이 HTTP로 플랫폼 기능을 호출할 때 거치는 진입점입니다.

> **중간 요약**: 객체 접근, 편집, Workshop 호출, 서버리스 실행, Marketplace는 모든 언어에서 지원됩니다. 인터페이스는 TypeScript v2 전용, Pipeline Builder는 Python 전용, 고급 미디어 작업은 TypeScript v1 전용이며, 배포 실행과 스테이징 쓰기, 언어 모델 통합은 TypeScript v2와 Python에서 지원됩니다.

<a id="ontology-sdk-support"></a>
## Ontology SDK 지원 (Ontology SDK support)

Python과 TypeScript v2 함수는 [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/overview/)(OSDK)를 지원합니다. OSDK를 사용하면 개발 환경에서 온톨로지를 직접 활용할 수 있으며, Developer Console과의 호환성, OSDK 버전 관리 같은 [이점](https://www.palantir.com/docs/foundry/ontology-sdk/overview/#osdk-benefits)이 있습니다. 함수 리포지토리에서 이 이점을 누리려면 Python이나 TypeScript v2를 사용할 것을 권장합니다.

**설명**: OSDK는 사용자의 온톨로지(객체 타입, 속성, 링크 타입, 액션 타입)를 바탕으로 생성되는 타입이 지정된 클라이언트 라이브러리입니다. 예를 들어 Flight 객체 타입이 있으면 `Flight` 타입과 그 속성 필드가 코드로 생성되어, 플랫폼 밖의 애플리케이션과 함수 안에서 같은 코드로 온톨로지를 다룰 수 있습니다.

<a id="typescript-v1-vs-typescript-v2"></a>
## TypeScript v1과 TypeScript v2 비교 (TypeScript v1 vs. TypeScript v2)

TypeScript v1과 TypeScript v2 모두 TypeScript의 핵심 언어 기능을 사용할 수 있지만, 위 기능 지원 표에서 보듯 지원되는 플랫폼 기능에 차이가 있습니다. TypeScript v1에 비해 몇 가지 핵심 개선 사항이 있으므로 TypeScript v2 함수로 워크플로를 구축할 것을 권장합니다.

* **완전한 Node.js 런타임에서의 서버리스 실행:** TypeScript v2 함수는 Node.js 환경에서 실행되며 `fs`, `child_process`, `crypto` 같은 핵심 모듈을 지원합니다. 이를 통해 파일 시스템과 상호 작용하거나, CPU 집약적인 작업을 병렬로 수행하거나, 기타 시스템 수준 작업이 필요한 NPM 라이브러리와의 호환성이 높아집니다.
* **OSDK 일급 지원:** 이제 TypeScript v2 함수에서 OSDK를 매끄럽게 사용할 수 있어, 플랫폼 안팎에서 코드를 쉽게 재사용할 수 있습니다. 또한 대규모 온톨로지 데이터를 다루는 더 효율적인 API를 제공합니다.
* **구성 가능한 리소스 요청:** TypeScript v2 함수는 최대 8 vCPU와 5GB 메모리를 요청할 수 있어, 성능과 확장성을 더 세밀하게 제어할 수 있습니다.
* **스테이징 쓰기 \[베타]:** TypeScript v2는 [스테이징 쓰기](10_typescript-v2/05_typescript-v2-staged-writes.md)를 지원합니다. 이는 온톨로지 편집 함수를 위한 대안적 실행 모델로, 함수 안에서 쓰기 후 읽기 보장을 제공하고 다른 스테이징 쓰기 함수를 중첩 호출할 수 있게 합니다.

**설명**: `fs`는 파일 읽기와 쓰기, `child_process`는 다른 프로세스 실행, `crypto`는 해시와 암호화를 담당하는 Node.js 기본 모듈입니다. TypeScript v1은 이런 시스템 모듈을 쓸 수 없는 제한된 환경이라, 이 모듈에 의존하는 NPM 패키지(예: 파일로 임시 데이터를 쓰는 PDF 처리 라이브러리)가 동작하지 않을 수 있습니다. v2에서는 이런 패키지를 그대로 쓸 수 있습니다.

> **중간 요약**: Python과 TypeScript v2는 OSDK를 지원하므로 권장됩니다. TypeScript v2는 v1에 비해 완전한 Node.js 런타임, OSDK 일급 지원, 최대 8 vCPU와 5GB 메모리 요청, 스테이징 쓰기를 제공합니다.

<a id="serverless-functions"></a>
## 서버리스 함수 (Serverless functions)

사용자의 환경(enrollment)에서 서버리스 함수가 켜져 있다면, 새 리포지토리는 기본적으로 서버리스 함수를 사용합니다. 대부분의 사용 사례에서 배포된 함수(deployed function) 대신 서버리스 함수를 사용할 것을 권장합니다. 서버리스 함수를 사용하면 함수 하나의 여러 버전을 필요할 때 실행할 수 있어 업그레이드가 더 안전해집니다.

Python이나 TypeScript v2 함수를 사용할 때는 [배포된 함수가 더 나은 경우](09_language-agnostic-features/06_functions-deployed.md#choose-between-deployed-and-serverless-execution-modes)나 서버리스 대신 배포된 함수를 반드시 써야 하는 경우도 있지만, 흔하지는 않습니다. 사용할 수 있다면 다음과 같은 이유로 서버리스 함수가 선호됩니다.

* 서버리스 함수는 함수 하나의 서로 다른 버전을 필요할 때 실행할 수 있어 업그레이드가 더 안전합니다. 배포된 함수는 한 번에 하나의 함수 버전만 실행할 수 있습니다.
* 서버리스 함수는 실행될 때만 비용이 발생하지만, 배포된 함수는 배포가 실행 중인 동안 계속 비용이 발생합니다.
* 서버리스 함수는 인프라가 자동으로 관리되므로 초기 설정과 장기 유지 관리 부담이 적습니다.

**설명**: 서버리스(serverless) 실행은 요청이 들어올 때 실행 환경을 띄워 코드를 돌리고, 요청이 없으면 자원을 쓰지 않는 방식입니다. 배포(deployed) 실행은 서버 프로세스를 항상 켜 두고 요청을 기다리는 방식입니다. 예를 들어 액션 A는 함수 1.2.0을, 액션 B는 1.3.0을 참조할 때, 서버리스에서는 요청마다 필요한 버전을 띄우므로 두 버전이 공존할 수 있지만, 배포 방식에서는 켜져 있는 하나의 버전만 응답할 수 있습니다. 반면 항상 켜져 있는 배포 방식은 매 요청마다 환경을 새로 띄우는 지연이 없습니다.

> **중간 요약**: 서버리스 함수가 기본값이자 권장 방식이며, 여러 버전 동시 실행, 실행할 때만 드는 비용, 자동 관리라는 장점이 있습니다. 배포된 함수가 필요한 경우는 드뭅니다.

## 정리

- 함수 작성 언어는 AIP Logic, TypeScript v1, TypeScript v2, Python이며, 언어마다 지원하는 플랫폼 기능이 다릅니다.
- 인터페이스는 TypeScript v2, Pipeline Builder는 Python, 고급 미디어 작업과 웹훅 직접 호출은 TypeScript v1에서만 지원됩니다.
- OSDK를 쓸 수 있는 Python과 TypeScript v2가 권장되며, TypeScript v2는 v1보다 런타임, 리소스, 스테이징 쓰기 면에서 개선되었습니다.
- 서버리스 실행이 기본이자 권장 방식이며, 배포 실행은 TypeScript v2와 Python에서 특수한 경우에만 씁니다.
