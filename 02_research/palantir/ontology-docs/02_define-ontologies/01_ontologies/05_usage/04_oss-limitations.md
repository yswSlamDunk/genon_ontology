# Object Set Service 제한 사항 (Object Set Service limitations)

- 원문: https://www.palantir.com/docs/foundry/ontologies/oss-limitations/
- 사이드바 위치: Define Ontologies > Ontologies > Usage > Object Set Service limitations

이 페이지는 온톨로지에서 객체를 조회하는 서비스인 Object Set Service(OSS)가 쿼리 크기에 따라 실행 방식을 어떻게 바꾸는지, 그리고 객체 집합(object set)을 다룰 때 부딪히는 크기 제한이 무엇인지 설명합니다. 함수(function)나 OSDK로 많은 객체를 다루는 코드를 짤 때 이 제한을 모르면 시간 초과나 오류를 만나게 되므로, 설계 단계에서 알아 두어야 합니다.

Object Set Service(OSS)는 온톨로지에서 객체를 쿼리하고 가져오는 일을 담당하는 서비스입니다. OSS는 성능과 규모 사이의 균형을 맞추기 위해 계층형(tiered) 실행 전략을 사용하며, 쿼리의 크기와 복잡도에 따라 최적의 방식을 자동으로 선택합니다.

이 페이지는 OSS가 다양한 크기의 쿼리를 어떻게 처리하는지, 그리고 객체 집합으로 작업할 때 알아야 할 제한 사항을 설명합니다.

<a id="query-execution-strategies"></a>
## 쿼리 실행 전략 (Query execution strategies)

OSS는 쿼리를 처리하는 최적의 방식을 자동으로 선택하는 계층형 실행 전략을 사용합니다.

1. **저장 계층으로 푸시다운(Pushdown to storage layer):** 단순한 쿼리의 경우, OSS는 인덱싱된 자료구조를 활용하기 위해 연산을 저장 계층으로 직접 내려보냅니다. 가장 빠른 실행 경로이며 컴퓨트 오버헤드가 최소입니다.

2. **인메모리 실행(In-memory execution):** 더 복잡한 연산이 있는 쿼리의 경우, OSS는 일정 용량까지 데이터를 메모리에 올려 빠르게 처리합니다. 중간 규모의 쿼리에 적합합니다.

3. **Spark 기반 실행(Spark-based execution):** 인메모리 용량을 넘는 대규모 쿼리의 경우, OSS는 자동으로 Spark 기반 분산 컴퓨트로 전환(fallback)합니다. 추가 지연 시간과 컴퓨트 사용량을 감수하는 대신 훨씬 큰 객체 집합을 처리할 수 있습니다.

이 실행 전략들 사이의 전환은 자동으로 이루어지며 여러 요인에 따라 결정됩니다.

* **객체 집합 크기:** 집합이 클수록 Spark 실행이 일어납니다.
* **사용 가능한 컴퓨트 자원:** OSS는 성능과 자원 활용 사이의 균형을 맞춥니다.

OSS는 하나의 복잡한 쿼리 안에서도 실행 단계마다 서로 다른 실행 전략을 사용할 수 있습니다. 각 방식의 임계값과 제한 사항을 이해하면 효율적인 쿼리를 설계하고 성능 특성을 이해하는 데 도움이 됩니다.

**설명**: 푸시다운은 "데이터를 가져와서 거르는" 대신 "저장소에게 걸러서 달라고 요청하는" 방식입니다. 예를 들어 `status = 'Delayed'`인 Flight를 찾는 쿼리는 인덱스가 있는 저장 계층에서 바로 처리됩니다. 반면 링크를 따라가며 여러 단계를 계산해야 하는 쿼리는 OSS가 데이터를 메모리에 올려 직접 처리하고, 그것도 너무 크면 여러 서버에 나누어 처리하는 Spark로 넘깁니다. 아래로 갈수록 처리 가능한 규모는 커지지만 느리고 비쌉니다.

<a id="oss-execution-flow-for-object-storage-v2"></a>
### Object Storage v2의 OSS 실행 흐름 (OSS execution flow for Object Storage v2)

다음 다이어그램은 OSS가 쿼리에 따라 적절한 실행 전략을 선택하는 방식을 보여 줍니다. 이 결정 과정은 각 단계의 복잡도에 따라 하나의 쿼리 안에서 여러 번 실행될 수 있습니다.

![결정 지점과 실행 전략을 보여 주는 OSS 실행 흐름 다이어그램.](https://www.palantir.com/docs/resources/foundry/ontologies/oss-execution-flow.png)

**주요 임계값:**

* **객체 100,000개(기본 임계값):** Search Around와 파생 속성(derived property)에서 인메모리 실행에서 Spark 기반 실행으로 전환하는 임계값입니다.
* **내부 페이지네이션 임계값:** 데이터 로딩 단계 중 어느 하나라도 Object Storage v2에서 25페이지가 넘는 데이터가 필요하면 OSS는 Spark로 전환합니다.
* **객체 10,000,000개(기본 임계값):** Search Around 작업의 최대 결과 집합 크기입니다(리프 한도, leaf limit).
* **객체 100,000개(기본 임계값):** `.all()` 또는 `.allAsync()`로 객체를 메모리에 로드할 때의 최대치입니다(OSDK 제한 사항이며, `getAllObjects` API로는 더 많이 로드할 수 있습니다).

<a id="execution-strategy-comparison"></a>
### 실행 전략 비교 (Execution strategy comparison)

| 전략 | 사용 시점 | 성능 | 컴퓨트 비용 | 사용 사례 |
|----------|-----------|-------------|--------------|-----------|
| **저장 계층으로 푸시다운** | 단순한 필터와 집계 | 가장 빠름 | 가장 낮음 | 인덱스 조회로 해결할 수 있는 기본 쿼리 |
| **인메모리 실행** | 객체 집합 ≤100k | 빠름 | 보통 | 대부분의 Search Around, 중간 규모 쿼리 |
| **Spark 기반 실행** | 객체 집합 >100k | 느림(지연 시간 증가) | 높음 | 대규모 Search Around, 복잡한 다단계 쿼리 |

> **중간 요약**: OSS는 푸시다운, 인메모리, Spark 순으로 실행 전략을 자동 선택합니다. 객체 10만 개와 내부 25페이지가 Spark 전환 기준이고, Search Around 결과는 1,000만 개, OSDK `.all()` 로드는 10만 개가 기본 한도입니다.

<a id="object-set-size-limitations"></a>
## 객체 집합 크기 제한 (Object set size limitations)

OSS는 저장 백엔드와 작업 유형에 따라 서로 다른 크기 제한을 적용합니다. 이 제한은 시스템 안정성과 예측 가능한 성능을 보장합니다.

<a id="object-storage-v1-phonograph-planned-deprecation"></a>
### Object Storage v1 (Phonograph) [지원 종료 예정] (Object Storage v1 (Phonograph) [Planned deprecation])

**주의**: 지원 종료 예정(Planned deprecation). Object Storage v1(Phonograph)은 개발 수명 주기상 [지원 종료 예정(planned deprecation)](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으며 2026년 6월 30일 이후에는 사용할 수 없습니다. [객체 타입과 링크 타입을 Object Storage v2로 마이그레이션](../../../06_ontology-architecture/01_overview-and-getting-started/03_osv1-osv2-migration.md)하십시오.

Object Storage v1에는 다음과 같은 제한이 있습니다.

* **객체를 메모리에 로드:** [Functions on Objects](../../04_functions/01_overview.md)의 `.all()` 또는 `.allAsync()` 메서드로 최대 **100,000개의 객체**를 로드할 수 있습니다.
* **Search Around 작업:** 객체 집합 A에서 객체 집합 B로 Search Around를 수행할 때, 결과 집합(객체 집합 B)은 **100,000개 객체**를 넘을 수 없습니다.

이 제한은 Object Storage v1의 모든 작업에 적용됩니다. 더 큰 쿼리를 위한 Spark 기반 실행으로의 자동 전환은 없습니다.

<a id="object-storage-v2"></a>
### Object Storage v2

Object Storage v2는 하이브리드 실행 모델을 통해 더 큰 유연성과 규모를 제공합니다.

* **인메모리 실행:** 기본적으로 OSS는 최대 **100,000개 객체**까지의 객체 집합에 대한 쿼리를 메모리에서 처리합니다.
* **Spark 기반 실행:** Search Around 작업에 **100,000개**가 넘는 객체가 관련되면 OSS는 자동으로 Spark 기반 분산 컴퓨트로 전환합니다.
* **Search Around 결과 한도:** Search Around 작업의 결과 집합(단일 데이터소스에서 로드되는 "리프(leaf)" 객체 집합)은 개별 Search Around 작업마다 **1,000만 개 객체**를 넘을 수 없습니다. 또한 쿼리 실행 중 로드되는 모든 데이터셋의 객체 총합은 **3,000만 개 객체**를 넘을 수 없습니다.
* **객체를 메모리에 로드(OSDK 제한 사항):** Ontology SDK에서 `.all()` 또는 `.allAsync()` 메서드로 객체를 로드할 때는 메모리 고갈과 함수 시간 초과를 막기 위해 최대 **100,000개 객체**로 제한됩니다. `getAllObjects` API 엔드포인트를 사용하면 더 많은 객체를 로드할 수 있습니다.

**주의**: Functions on Objects에서 10,000개가 넘는 객체를 로드하면 함수 로직의 복잡도에 따라 실행 시간 초과가 발생할 수 있습니다. 페이지네이션이나 필터링을 사용해 객체 집합 크기를 줄이는 것을 고려하십시오.

**설명**: 정리하면 OSv1은 10만 개에서 막히는 고정 한도이고, OSv2는 10만 개를 넘으면 Spark로 넘어가서 계속 처리하되 Search Around 결과 1,000만 개, 쿼리 전체 3,000만 개라는 더 큰 상한이 있습니다. 다만 함수 코드 안에서 객체를 한꺼번에 메모리로 가져오는 `.all()`은 저장소 버전과 관계없이 10만 개가 상한이고, 실무적으로는 1만 개만 넘어도 시간 초과를 걱정해야 합니다.

> **중간 요약**: OSv1(2026년 6월 30일 이후 사용 불가)은 메모리 로드와 Search Around 결과 모두 10만 개가 고정 한도입니다. OSv2는 10만 개를 넘으면 Spark로 전환하며 Search Around 결과 1,000만 개, 쿼리 전체 3,000만 개가 한도이고, OSDK `.all()`은 10만 개로 제한됩니다.

<a id="pagination-and-memory-limits"></a>
## 페이지네이션과 메모리 한도 (Pagination and memory limits)

OSS는 페이지 단위 읽기 요청에 메모리 한도를 적용합니다. 그 결과 더 남은 객체가 있더라도 한 페이지에 요청한 페이지 크기보다 적은 객체가 들어 있을 수 있습니다. 짧은 페이지를 결과 집합의 끝으로 해석하지 마십시오. 반환된 페이지 토큰이 빌 때까지 그 토큰으로 계속 페이지를 요청하십시오.

`loadObjects` 엔드포인트는 더 이상 권장되지 않습니다(deprecated). `StaticObjectSetV2`를 사용하는 페이징 엔드포인트로 마이그레이션하십시오. `loadObjects`는 요청된 모든 객체를 반환해야 하므로 부분 결과를 반환할 수 없습니다. 요청된 객체를 로드하는 것이 메모리 한도를 넘으면 엔드포인트는 `ObjectSet:ResultSizeLimitExceeded` 오류를 반환합니다.

**설명**: 페이지 크기를 1,000으로 요청했는데 600개만 왔다고 해서 끝난 것이 아닙니다. 종료 조건은 "받은 개수가 요청 크기보다 작다"가 아니라 "다음 페이지 토큰이 비어 있다"입니다. 의사코드로 쓰면 `token = null; do { page = fetch(pageSize, token); 처리(page.data); token = page.nextPageToken; } while (token != null)` 형태로 반복해야 합니다.

<a id="understanding-search-around-result-sets"></a>
## Search Around 결과 집합 이해하기 (Understanding Search Around result sets)

객체 사이의 링크 관계를 따라가는 Search Around 작업을 수행하면, OSS는 관련 객체를 효율적으로 찾기 위해 특수한 유형의 조인 연산을 사용합니다.

예를 들어 고객 객체 집합에서 시작해 링크 관계를 통해 관련된 모든 주문 객체를 찾는다면 다음과 같습니다.

* **시작 집합(starting set)은** 고객 객체입니다(검색을 시작하는 객체).
* **결과 집합(result set)은** 그 고객들에 링크된 주문 객체입니다(검색해 도달하는 객체).

OSS는 Search Around 작업을 왼쪽 세미 조인(left-semi join)으로 구현합니다. 이 조인은 시작 집합의 데이터를 중복시키지 않고, 결과 집합에서 일치하는 링크가 있는 객체만 반환합니다. 1,000만 개 객체 한도는 이 결과 집합, 즉 링크 관계를 따라간 뒤 반환되는 서로 다른(distinct) 객체의 전체 모음에 적용됩니다.

**설명**: 일반 조인(`INNER JOIN`)은 고객 열과 주문 열을 붙인 행을 만들기 때문에, 고객 한 명에 주문이 100개면 그 고객 정보가 100번 반복됩니다. 세미 조인은 SQL의 `SELECT * FROM orders o WHERE EXISTS (SELECT 1 FROM customers c WHERE c.id = o.customer_id AND <시작 집합 조건>)`에 해당하며, 주문 테이블의 열만 돌려주고 각 주문은 한 번씩만 나옵니다. 따라서 한도 1,000만 개는 "조인 결과 행 수"가 아니라 "결과로 나온 서로 다른 주문 객체 수"를 기준으로 셉니다.

> **중간 요약**: 페이지네이션 응답은 메모리 한도 때문에 요청보다 짧을 수 있으므로 토큰이 빌 때까지 반복해야 하며, `loadObjects`는 페이징 엔드포인트로 옮겨야 합니다. Search Around는 세미 조인으로 구현되어 결과 객체를 중복 없이 반환하고, 한도는 그 결과 객체 수에 적용됩니다.

<a id="best-practices-for-working-within-oss-limitations"></a>
## OSS 제한 안에서 작업하기 위한 모범 사례 (Best practices for working within OSS limitations)

최적의 성능을 보장하고 크기 제한에 걸리지 않으려면 다음을 따르십시오.

* **일찍 필터링하기:** 조인을 수행하거나 객체를 메모리에 로드하기 전에 필터를 적용해 객체 집합 크기를 줄이십시오. OSS는 인덱싱된 자료구조를 활용해 필터링된 쿼리를 더 효율적으로 처리합니다.

* **인덱스를 활용할 수 없는 연산 피하기:** 파생 속성과 계산된 SQL 열에 대한 필터링, 집계, 정렬 등의 연산은 모든 행을 평가해야 하며 내부 인덱스를 사용할 수 없습니다. 이런 연산은 빠른 푸시다운 경로를 사용하지 못하며, 작은 객체 집합에서도 인메모리 또는 Spark 실행을 일으킬 수 있습니다. 예를 들어 2026년 5월에 발생한 모든 주문을 필터링하려면 `(MONTH FROM order_date) = 'May' AND (YEAR FROM order_date) = '2026'`을 사용하지 말고, 범위 필터 `order_date > '2026-05-01' && order_date < '2026-06-01'`을 사용하십시오.

* **페이지네이션 사용하기:** Functions on Objects에서 큰 객체 집합으로 작업할 때는 모든 객체를 한 번에 로드하지 말고 페이지네이션 패턴으로 객체를 묶음(batch) 단위로 처리하십시오.

* **객체 집합 크기 모니터링하기:** Search Around 같은 비싼 작업을 수행하기 전에 집계 쿼리로 객체 집합의 크기를 파악하십시오. Search Around 작업은 계산 비용이 크며, 그래서 OSS가 이런 크기 제한을 두는 것입니다.

* **데이터 모델 최적화하기:** 크기 제한에 자주 걸린다면 전통적인 데이터 모델링 원칙을 사용해 온톨로지 구조를 바꾸는 것을 고려하십시오. 관련 데이터를 객체 속성으로 통합해 온톨로지를 비정규화(denormalize)하면 비싼 Search Around 작업의 필요를 줄이고 쿼리를 더 효율적으로 만들 수 있습니다. 또한 자연스럽게 더 작은 결과 집합을 만드는, 더 목적이 분명한 객체 타입이나 링크 관계를 만들 수도 있습니다.

* **컴퓨트 비용 고려하기:** Spark 기반 실행은 인메모리 실행보다 컴퓨트 자원을 더 많이 씁니다. Spark 전환을 일으키는 쿼리는 추가 [컴퓨트 초](03_query-compute-usage.md)를 소비합니다.

**주의**: OSS는 쿼리를 실행할지 결정하기 위해 크기 추정(size estimation)을 사용합니다. 추정 크기가 한도를 크게(2배 넘게) 초과하면, 정확한 임계값에 도달하기 전에 쿼리가 실패할 수 있습니다. 이는 비싼 정확한 개수 세기 연산을 피하기 위한 성능 최적화입니다.

**설명**: 범위 필터 예시가 중요한 이유는 데이터베이스 인덱스의 원리와 같습니다. `order_date`에 정렬된 인덱스가 있으면 "5월 1일부터 6월 1일 전까지"는 인덱스에서 구간 하나를 잘라 내면 끝납니다. 반면 `MONTH(order_date)`처럼 열에 함수를 씌우면 각 행마다 함수를 계산해 봐야 하므로 인덱스를 쓸 수 없고 전체 스캔이 됩니다. 비정규화의 예로는, 주문 화면에서 매번 Customer로 Search Around해 고객 등급을 가져오는 대신 Order 객체에 `customer_tier` 속성을 미리 넣어 두는 방식이 있습니다.

> **중간 요약**: 먼저 거르고, 인덱스를 쓸 수 있는 형태(범위 필터 등)로 조건을 쓰고, 큰 집합은 페이지 단위로 처리하고, 비싼 작업 전에 크기를 확인하고, 필요하면 비정규화로 Search Around를 줄이는 것이 권장 사항입니다. 추정 크기가 한도의 2배를 넘으면 실제 한도 전에 실패할 수 있습니다.

<a id="related-resources"></a>
## 관련 자료 (Related resources)

* [온톨로지 아키텍처(Ontology architecture)](../../../06_ontology-architecture/01_overview-and-getting-started/01_overview.md): Object Set Service와 온톨로지 백엔드의 다른 구성 요소에 대해 더 알아봅니다.
* [온톨로지 쿼리의 컴퓨트 사용량(Compute usage with Ontology queries)](03_query-compute-usage.md): 쿼리 패턴에 따라 컴퓨트 사용량이 어떻게 달라지는지 이해합니다.
* [Functions on Objects](../../04_functions/01_overview.md): 객체 집합을 다루는 효율적인 함수 작성 방법을 알아봅니다.
* [객체 집합 API 레퍼런스(TSv1)(Object sets API reference (TSv1))](../../04_functions/13_functions-on-objects/07_api-object-sets.md): 객체 집합 작업을 위한 상세 API 문서입니다.

## 정리

- OSS는 온톨로지에서 객체를 조회하는 서비스로, 푸시다운, 인메모리, Spark 실행을 쿼리 크기와 복잡도에 따라 자동 선택합니다.
- OSv1은 10만 개 고정 한도이며 2026년 6월 30일 이후 사용할 수 없습니다. OSv2는 10만 개 초과 시 Spark로 전환하고 Search Around 결과 1,000만 개, 쿼리 전체 3,000만 개가 한도입니다.
- OSDK와 함수의 `.all()` 로드는 10만 개가 상한이고, 함수에서는 1만 개를 넘으면 시간 초과 위험이 있습니다.
- 페이지네이션은 토큰이 빌 때까지 반복해야 하며, Search Around는 세미 조인으로 구현됩니다.
- 선 필터링, 인덱스 친화적 조건, 페이지네이션, 크기 확인, 비정규화가 제한 안에서 효율적으로 작업하는 방법입니다.
