# 함수 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/functions/overview/
- 사이드바 위치: Define Ontologies > Functions > Overview

이 페이지는 Foundry의 함수(function)가 무엇이고 어디에 쓰이는지 소개하는 출발점입니다. 함수는 대시보드나 애플리케이션 같은 운영 환경에서 빠르게 실행되는 서버 측 코드로, 온톨로지의 객체를 읽고, 링크를 따라가고, 편집하는 기능을 기본으로 지원합니다. 대표적인 사용 사례와 지원 언어, 그리고 다음에 읽을 튜토리얼을 안내합니다.

**함수(function)는** 코드 작성자가 의사 결정 프로세스를 돕기 위해 설계된 대시보드와 애플리케이션 같은 운영 환경에서 빠르게 실행될 수 있는 로직을 작성할 수 있게 해 줍니다. 이 로직은 서버 측의 격리된 환경에서 실행됩니다.

특히 함수는 온톨로지 기반의 로직 작성을 일급(first-class)으로 지원합니다. 여기에는 다양한 객체 타입의 속성(property) 읽기, 링크 따라가기(traversal), 유연한 온톨로지 편집(edit)이 포함됩니다.

**설명**: "일급 지원"이란 별도 라이브러리나 우회 없이 언어 차원에서 바로 쓸 수 있도록 지원한다는 뜻입니다. 예를 들어 함수 안에서 `flight.origin`처럼 객체의 속성을 필드처럼 읽거나, `flight.aircraft.get()`처럼 링크를 따라 연결된 객체를 가져올 수 있습니다. 직접 SQL 질의나 REST 호출 코드를 쓰지 않아도 온톨로지 객체를 클래스 인스턴스처럼 다룰 수 있다는 의미입니다. "격리된 환경"은 함수 코드가 다른 사용자의 코드나 플랫폼 내부와 분리된 별도의 실행 공간(예: 컨테이너)에서 돈다는 뜻입니다.

함수의 일반적인 사용 사례는 다음과 같습니다.

* [Workshop](https://www.palantir.com/docs/foundry/workshop/functions-use/)에서 사용할 객체 집합(object set)이나 변수 값을 반환하기
* [Workshop의 함수 기반 열(function-backed columns)](https://www.palantir.com/docs/foundry/workshop/widgets-object-table/#function-backed-columns)을 사용해 파생 표 열에 변환된 값을 표시하기
* 객체 타입의 값을 집계해 [Workshop 차트](https://www.palantir.com/docs/foundry/workshop/widgets-chart/#function-aggregations-function-backed-layers)로 표시하기
* [함수 기반 액션](../03_action-types/11_function-backed-actions/01_function-actions-overview.md)을 통해 많은 객체를 업데이트하는 복잡한 온톨로지 편집을 표현하기
* 백엔드에서 로직을 실행해 [Slate](https://www.palantir.com/docs/foundry/slate/overview/)의 프런트엔드에 표시할 정보를 반환하기
* [Quiver](https://www.palantir.com/docs/foundry/quiver/overview/)에 표시할 사용자 정의 지표나 집계를 계산하기
* [외부 함수(external functions)](12_typescript-v1/10_webhooks.md)를 통해 외부 시스템을 조회해 온톨로지의 객체를 보강하기
* 특히 [언어 모델](09_language-agnostic-features/08_streaming-functions.md)을 다룰 때, 실시간 경험을 위해 결과를 점진적으로 스트리밍하기
* [Pipeline Builder](11_python/07_python-functions-builder.md)에서 Python 함수를 사이드카(sidecar) 컨테이너로 사용하기

**설명**: 예를 들어 "Workshop의 함수 기반 열"은 Flight 표에 원본 데이터에는 없는 "예상 도착 시각" 열을 추가하고, 각 행마다 함수가 `출발 시각 + 비행 시간 + 지연 시간`을 계산해 채워 주는 방식입니다. 사이드카 컨테이너는 주 프로세스 옆에 함께 실행되며 보조 기능을 제공하는 별도 컨테이너를 말합니다.

함수가 지원하는 언어는 [TypeScript ↗](https://www.typescriptlang.org/docs/handbook/basic-types.html)와 [Python ↗](https://www.python.org/)입니다.

언어별 기능 지원과 언어 및 언어 버전 선택에 대한 자세한 내용은 [언어별 기능 지원 명세](02_language-feature-support.md)를 참고하세요.

Foundry에서 함수를 시작하려면 다음 튜토리얼을 권장합니다.

* [TypeScript v1 함수 시작하기](12_typescript-v1/01_typescript-v1-getting-started.md)
* [TypeScript v2 함수 시작하기](10_typescript-v2/01_typescript-v2-getting-started.md)
* [Python 함수 시작하기](11_python/01_python-getting-started.md)
* Palantir Learning 포털의 ["Speedrun: Your first Ontology function" 과정 ↗](https://learn.palantir.com/speedrun-your-first-ontology-function)

## 정리

- 함수는 운영 애플리케이션에서 빠르게 실행되는 서버 측 로직으로, 격리된 환경에서 실행됩니다.
- 객체 속성 읽기, 링크 따라가기, 온톨로지 편집을 언어 차원에서 바로 지원합니다.
- Workshop 변수와 열, 차트, 함수 기반 액션, Slate, Quiver, 외부 시스템 조회, 언어 모델 스트리밍, Pipeline Builder 등에 쓰입니다.
- 지원 언어는 TypeScript와 Python이며, 언어별 시작하기 튜토리얼이 마련되어 있습니다.
