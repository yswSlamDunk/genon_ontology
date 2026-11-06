# 게시된 함수 관리 (Manage published functions)

- 원문: https://www.palantir.com/docs/foundry/functions/manage-functions/
- 사이드바 위치: Define Ontologies > Functions > Function management > Manage published functions

이 페이지는 게시된 함수(function)를 Ontology Manager에서 검색하고, 입출력과 사용 지표를 확인하고, 타임아웃이나 메모리 같은 실행 설정을 바꾸는 방법을 설명합니다. 또 함수 기반 액션이 사용하는 일관된 스냅샷(consistent snapshot)과, 함수 실행에 걸리는 시간, 메모리, 멀티스레딩, 객체 집합 크기 제한을 정리합니다. 함수가 느리거나 실패할 때 원인을 찾으려면 이 제한들을 알아야 합니다.

게시된 함수는 종류에 관계없이 모두 **Ontology Manager**에서 보고 관리할 수 있습니다.

<a id="searching-for-functions"></a>
## 함수 검색하기 (Searching for functions)

함수를 검색하려면 **Ontology Manager**로 이동해 **Functions** 탭을 선택합니다.
함수 이름, 설명, API 이름, RID를 비롯해 함수의 대부분의 메타데이터로 함수를 검색할 수 있습니다.

![Ontology Manager에서 함수 검색하기](https://www.palantir.com/docs/resources/foundry/functions/functions-search.png)

**설명**: RID(Resource Identifier)는 Foundry가 모든 리소스에 부여하는 고유 식별자 문자열입니다. API 이름은 코드에서 함수를 부를 때 쓰는 이름입니다. 화면에 보이는 표시 이름과 달리 이 두 값은 정확히 하나의 함수를 가리킵니다.

<a id="function-overview-page"></a>
## 함수 개요 페이지 (Function overview page)

Ontology Manager에서 함수를 선택하면 그 함수의 입력, 출력, 사용 이력, 그리고 성공과 실패 횟수 및 P95 실행 시간을 포함한 [함수 지표](../08_function-consumption/02_function-metrics.md)를 볼 수 있습니다.

![Ontology Manager에서 함수 개요 보기](https://www.palantir.com/docs/resources/foundry/functions/function-overview.png)

**설명**: P95 실행 시간은 실행 시간을 짧은 순으로 줄 세웠을 때 95% 지점에 있는 값입니다. 예를 들어 P95가 2초라면 실행 100번 중 95번은 2초 안에 끝났다는 뜻입니다. 평균과 달리 드물게 매우 느린 실행이 섞여 있어도 왜곡이 적어, "대부분의 사용자가 겪는 최악의 대기 시간"을 보는 데 쓰입니다.

<a id="function-configuration-page"></a>
## 함수 구성 페이지 (Function configuration page)

일부 종류의 함수는 타임아웃이나 메모리 한도 같은 리소스를 구성할 수 있습니다.
함수가 구성 옵션을 지원하면 **Configuration** 탭에서 이를 보고 편집할 수 있습니다.
이 탭이 없다면 그 함수는 구성 옵션을 지원하지 않는 것입니다.

**주의**: 구성 재정의(configuration override)는 함수 버전 단위로 적용됩니다. 함수를 게시하는 애플리케이션에 따라 새 버전에는 기본 구성이 적용될 수 있으므로, 구성 재정의를 다시 적용해야 할 수도 있습니다.

예를 들어 다음 이미지처럼 TypeScript 함수의 타임아웃을 구성할 수 있습니다.

![Ontology Manager에서 함수 런타임 구성 관리하기](https://www.palantir.com/docs/resources/foundry/functions/function-configuration.png)

<a id="configuration-inheritance"></a>
### 구성 상속 (Configuration inheritance)

함수는 새 버전을 게시할 때 구성 재정의를 상속하는 기능을 기본으로 지원합니다. 구성은 시맨틱 버전 명세에 따른 이전 안정 버전에서 상속됩니다. 안정 버전이 아닌 버전을 게시하는 경우, 이전 버전이 안정 릴리스인지와 관계없이 이전 버전에서 구성을 상속합니다.

구성 상속을 사용하려면 저장소에 갱신된 템플릿 구성이 있어야 합니다. 숨겨진 `templateConfiguration.json` 파일을 확인하면 저장소가 어떤 버전인지 알 수 있습니다.

* TypeScript v1 함수 저장소는 `parentTemplateVersion >= 3.512.0` 이어야 합니다.
* Python 함수 저장소는 `parentTemplateVersion >= 0.423.0` 이어야 합니다.

**설명**: 예를 들어 버전 `1.2.0`에서 타임아웃을 120초로 재정의해 두었다고 합시다. 구성 상속이 지원되는 저장소에서 `1.3.0`을 게시하면 `1.3.0`도 120초 설정을 물려받습니다. 지원되지 않는 저장소라면 `1.3.0`은 기본값(60초)으로 시작하므로 다시 설정해야 합니다. 바로 앞의 주의 문단이 이 경우를 말합니다.

> **중간 요약**: Ontology Manager의 Functions 탭에서 함수를 검색하고, 개요 페이지에서 입출력과 지표를, Configuration 탭에서 타임아웃과 메모리 같은 설정을 봅니다. 설정은 버전마다 적용되며, 템플릿 버전이 충분히 높으면 이전 버전의 설정이 새 버전으로 상속됩니다.

<a id="consistent-snapshots"></a>
## 일관된 스냅샷 (Consistent snapshots)

함수 기반 액션(function-backed action)은 한 번의 실행 안에서 모든 읽기 요청에 하나의 온톨로지 스냅샷을 자동으로 사용합니다.

일관된 스냅샷은 다음과 같은 특성을 제공합니다.

* **데이터 일관성:** 스냅샷이 없으면, 요청 사이에 기반 데이터가 바뀌었을 경우 함수 안의 연속된 온톨로지 쿼리가 서로 다른 버전의 데이터를 반환할 수 있습니다. 스냅샷을 쓰면 데이터베이스 트랜잭션의 스냅샷 격리(snapshot isolation)처럼 함수가 온톨로지의 일관된 상태를 기준으로 동작합니다.
* **성능 향상:** 모든 온톨로지 요청에 하나의 스냅샷을 재사용하면 온톨로지 읽기 성능이 크게 좋아집니다. 함수 기반 액션 하나와 그 안의 모든 쿼리가 이 이점을 얻습니다.

**설명**: 스냅샷 격리는 트랜잭션이 시작된 시점의 데이터 상태를 기준으로 모든 읽기를 수행하는 데이터베이스 격리 수준입니다. 예를 들어 함수가 첫 번째 쿼리로 Order 객체 10개를 읽고, 두 번째 쿼리로 그 주문들의 합계를 계산한다고 합시다. 두 쿼리 사이에 다른 사용자가 주문 하나를 삭제하면, 스냅샷이 없을 때는 두 결과가 서로 맞지 않습니다. 스냅샷이 있으면 두 쿼리 모두 같은 시점의 데이터를 보므로 결과가 일치합니다.

<a id="snapshot-configuration"></a>
### 스냅샷 구성 (Snapshot configuration)

고급 사용 사례에서 스냅샷을 명시적으로 관리해야 한다면, [함수 구성 페이지](#function-configuration-page)에서 다음 옵션으로 스냅샷 동작을 구성할 수 있습니다.

* **Default (권장):** 스냅샷 관련 오류가 생기지 않는 한 이 옵션을 선택한 상태로 둡니다.
* **Disable snapshots:** 실행 중 각 쿼리마다 가장 최신 데이터가 필요하거나, 오래 실행되는 작업 때문에 스냅샷 오류가 발생할 때 사용합니다.
* **Enable snapshots:** 모든 읽기에서 일관된 특정 시점 상태가 필요하고 더 나은 읽기 성능을 원하며, 함수가 실행 도중 데이터가 갱신되지 않아도 괜찮을 때 사용합니다. 대부분의 사용 사례에서는 권장하지 않습니다.

**팁**: 소스(source)를 사용하는 함수는 기본적으로 스냅샷 없이 실시간 데이터를 대상으로 실행됩니다. 함수가 쓰기를 수행하거나 외부 시스템을 호출할 수 있으므로 스냅샷을 강제하는 것은 권장하지 않습니다.

> **중간 요약**: 함수 기반 액션은 한 실행 안의 모든 읽기에 같은 온톨로지 스냅샷을 써서 일관성과 성능을 얻습니다. 구성 페이지에서 Default, Disable snapshots, Enable snapshots 중 고를 수 있으며, 특별한 이유가 없으면 Default를 둡니다.

<a id="enforced-limits"></a>
## 강제되는 제한 (Enforced limits)

함수가 실행될 때 리소스를 지나치게 소비하지 않도록 몇 가지 제한이 적용됩니다.

<a id="time-limit"></a>
### 시간 제한 (Time limit)

함수는 기본적으로 경과 실행 시간이 **60초** 로 제한됩니다. 이 제한은 [함수 구성 페이지](#function-configuration-page)에서 바꿀 수 있습니다.

라이브 미리 보기(live preview)에서 실행할 때는 함수 구성 페이지에서 값을 바꿨더라도 최대 **280초** 까지 실행할 수 있습니다.

[Automate](https://www.palantir.com/docs/foundry/automate/overview/)를 통해 실행되는 함수는 비동기로 최대 **4시간** 까지 실행되며, 이는 표준 실행 제한을 넘어섭니다.

**주의**: TypeScript v1 함수는 추가로 CPU 시간 **30초** 로 제한되며, 이 값은 구성할 수 없습니다. 함수가 이 기준을 넘는 원인은 비효율적인 데이터 로딩 로직인 경우가 많습니다. CPU 타임아웃을 피하는 방법은 [성능 최적화](../08_function-consumption/03_optimize-performance.md) 섹션을 참고하세요.

**설명**: 경과 시간(elapsed time, wall-clock time)은 함수 시작부터 끝까지 실제로 흐른 시간이고, CPU 시간은 그중 CPU가 실제로 계산에 쓴 시간입니다. 함수가 데이터를 기다리는 동안에는 경과 시간만 늘고 CPU 시간은 거의 늘지 않습니다. 따라서 CPU 시간 30초를 넘는다는 것은 메모리에 올린 대량의 객체를 반복문으로 계산하는 등 실제 연산이 많다는 뜻입니다.

<a id="memory-limit"></a>
### 메모리 제한 (Memory limit)

메모리 제한은 TypeScript v1, TypeScript v2, Python 함수마다 다릅니다.

<a id="typescript-v1"></a>
#### TypeScript v1

함수 실행의 메모리 사용량은 **128 Megabytes** 로 제한됩니다. 이 제한에 도달하는 경우는 드물며, 대개는 메모리 제한보다 시간 제한이나 객체 로딩 제한에 먼저 걸립니다.

<a id="deployed-python-functions"></a>
#### 배포된 Python 함수 (Deployed Python functions)

배포된(deployed) Python 함수는 기본적으로 **2 Gigabytes** 의 메모리를 사용할 수 있습니다. 현재 배포된 Python 함수는 함수 구성 페이지에서 메모리 사용량을 구성할 수 없습니다.

<a id="serverless-python-and-typescript-v2-functions"></a>
#### 서버리스 Python과 TypeScript v2 함수 (Serverless Python and TypeScript v2 functions)

서버리스(serverless) 함수는 기본적으로 **1024 Mebibytes** 의 메모리를 사용할 수 있습니다. 이 값은 [함수 구성 페이지](#function-configuration-page)에서 **512 Mebibytes** 부터 **5120 Mebibytes** 까지 구성할 수 있습니다.

**설명**: 배포된(deployed) 함수는 항상 켜져 있는 전용 실행 환경에서 돌아가는 방식이고, 서버리스(serverless) 함수는 호출이 들어올 때 실행 환경이 할당되는 방식입니다. Megabyte(MB)는 10의 6제곱 바이트, Mebibyte(MiB)는 2의 20제곱(1,048,576) 바이트로 정의가 조금 다르며, 원문은 두 단위를 구분해 쓰고 있습니다.

<a id="multithreading"></a>
### 멀티스레딩 (Multithreading)

TypeScript v1에서 함수 실행은 단일 스레드로 이루어지므로 한 번에 하나의 연산만 수행할 수 있습니다. 그러나 객체 집합(object set)이나 링크의 로딩은 병렬화할 수 있습니다. 자세한 내용은 [성능 최적화](../08_function-consumption/03_optimize-performance.md)를 참고하세요.

TypeScript v2와 Python 함수에서는 Node.js의 기본 제공 `worker_threads` 라이브러리와 Python의 `threading` 라이브러리로 멀티스레딩을 사용할 수 있습니다.

**설명**: 단일 스레드에서도 로딩을 병렬화할 수 있는 이유는, 데이터 로딩이 대부분 서버 응답을 기다리는 I/O 작업이기 때문입니다. JavaScript의 `Promise.all`처럼 여러 요청을 한꺼번에 보내 놓고 응답을 함께 기다리면, CPU 연산은 하나씩 하더라도 대기 시간은 겹쳐서 줄어듭니다.

<a id="object-set-limits-with-typescript-v1"></a>
### TypeScript v1의 객체 집합 제한 (Object set limits with TypeScript v1)

[객체 집합](../13_functions-on-objects/07_api-object-sets.md)을 사용할 때 다음 경우에 `.all()` 또는 `.allAsync()`를 호출하면 오류가 발생합니다.

* 객체 집합에서 한 번에 **100,000개 객체** 를 넘게 로드하는 경우. 일반적으로 수만 개의 객체를 로드하기만 해도 시간 제한이나 메모리 제한에 걸립니다. 이 제한에 부딪히는 사용 사례라면 [집계(aggregation)](../13_functions-on-objects/07_api-object-sets.md#computing-aggregations)로 요약 데이터를 가져오거나 [정렬과 개수 제한](../13_functions-on-objects/07_api-object-sets.md#ordering-and-limiting)으로 객체의 일부만 가져오는 방법을 고려하세요.
* 한 번에 **3개를 넘는 [검색 연결(search around)](../13_functions-on-objects/07_api-object-sets.md#search-around)** 을 사용하는 경우.

일부 집계와 버킷팅(bucketing) 연산에도 제한이 있습니다. 자세한 내용은 [집계](../13_functions-on-objects/07_api-object-sets.md#computing-aggregations) 섹션을 참고하세요.

**설명**: 집계는 SQL의 `SELECT COUNT(*), AVG(amount) FROM orders GROUP BY status`처럼 서버에서 계산한 결과만 받아 오는 방식이라, 객체 수십만 개를 함수 메모리로 가져오지 않아도 됩니다. 정렬과 개수 제한은 `ORDER BY ... LIMIT 100`에 해당합니다. 검색 연결(search around)은 링크를 따라 연결된 객체 집합으로 이동하는 연산으로, SQL의 조인 한 단계에 해당합니다. 예를 들어 Employee에서 Department로, 다시 Department에서 Project로 이동하면 검색 연결을 2번 쓴 것입니다.

> **중간 요약**: 함수는 기본 60초(라이브 미리 보기 280초, Automate 4시간)의 시간 제한과 언어별 메모리 제한을 받으며, TypeScript v1은 CPU 30초, 단일 스레드, 객체 10만 개와 검색 연결 3회 제한이 추가로 있습니다. 큰 데이터는 집계나 정렬과 개수 제한으로 줄여서 다룹니다.

## 정리

- 게시된 모든 함수는 Ontology Manager의 Functions 탭에서 검색하고, 개요 페이지에서 입출력, 사용 이력, 성공과 실패 횟수, P95 실행 시간을 볼 수 있습니다.
- Configuration 탭에서 타임아웃, 메모리, 스냅샷 동작을 설정하며, 설정은 버전 단위로 적용되고 조건이 맞으면 새 버전에 상속됩니다.
- 함수 기반 액션은 한 실행 안에서 하나의 온톨로지 스냅샷을 사용해 일관성과 성능을 확보합니다.
- 시간 제한은 기본 60초이고, 메모리 제한은 TypeScript v1 128MB, 배포된 Python 2GB, 서버리스 Python과 TypeScript v2 1024MiB(512\~5120MiB 조정 가능)입니다.
- TypeScript v1은 CPU 30초, 단일 스레드, `.all()` 로드 10만 개, 검색 연결 3회 제한이 있습니다.
