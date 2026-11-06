# 온톨로지 설계: 구조적 지침 (Ontology design: Structural guidance)

- 원문: https://www.palantir.com/docs/foundry/ontology/ontology-structural-guidance/
- 사이드바 위치: Define Ontologies > Ontology design: Structural guidance

이 페이지는 온톨로지 안에서 속성, 관계, 접근 제어를 어떤 구조로 만들어야 하는지 구체적으로 안내합니다. 정규화와 파생 속성, 구조체(struct), 인터페이스, 링크와 객체 기반 링크 타입, 이름 규칙, 보안 설계의 여섯 주제를 다루며, 주제마다 피할 설계와 권장 설계를 나란히 비교합니다. [모범 사례](06_ontology-best-practices.md) 페이지의 원칙을 실제 모델링 결정으로 옮기는 방법을 보여 주는 페이지입니다.

다음 섹션들은 온톨로지 안에서 속성(property), 관계, 접근 제어를 구조화하는 방법에 대한 지침을 제공합니다.

<a id="normalization-and-derived-properties"></a>
## 정규화와 파생 속성 (Normalization and derived properties)

**각 사실은 한 번만 저장하세요. 편의를 위해서는 파생 속성을 사용하세요.**

비정규화된 데이터(링크된 객체의 값을 부모 객체에 복사해 두는 것)는 위험할 수 있습니다. 데이터 소스가 바뀌면 모든 사본을 업데이트해야 하기 때문입니다. 정규화는 데이터를 일관되게 유지하고, 파생 속성(derived property)은 관리 부담 없이 비정규화된 접근의 편리함을 제공합니다.

계산된 값이라고 모두 같지는 않습니다. 알맞은 접근 방식은 그 값을 안정적인 입력으로부터 안전하게 미리 계산할 수 있는지, 아니면 온톨로지의 동적인 변경과 계속 동기화되어야 하는지에 따라 달라집니다.

**설명**: 정규화(normalization)는 데이터베이스 설계에서 같은 사실이 여러 곳에 중복 저장되지 않도록 테이블을 나누는 작업입니다. 예를 들어 `Employee` 테이블의 각 행에 `managerName` 열을 두면, 매니저 Alice의 이름이 바뀔 때 Alice 밑의 직원 행을 모두 고쳐야 하고 하나라도 놓치면 데이터가 서로 어긋납니다(갱신 이상). 파생 속성은 값을 저장하지 않고 조회할 때마다 링크된 객체에서 계산하므로, SQL의 뷰(view)나 조회 시점의 `JOIN`, `COUNT` 집계에 해당합니다.

<a id="pre-computed-vs-dynamically-derived-values"></a>
### 미리 계산한 값과 동적으로 파생되는 값 (Pre-computed vs. dynamically derived values)

| 유형 | 특징 | 권장 도구 | 예시 |
|-|-|-|-|
| 미리 계산(Pre-computed) | 같은 객체의 속성에서 계산되며, 입력이 거의 바뀌지 않거나 파이프라인 수집(ingestion)으로만 바뀝니다. | 파이프라인 변환(Pipeline transform) | `fullName` = `firstName` + " " + `lastName` <br><br> 입력이 안정적이고 같은 파이프라인에서 업데이트되므로, 미리 계산해도 안전하고 런타임 오버헤드가 전혀 없습니다. |
| 동적 파생(Dynamically derived) | 링크된 객체에 의존하거나, 액션, 자동화, 기타 온톨로지 수준 연산으로 바뀌는 값에 의존합니다. | 파생 속성(Derived property) | `directReportCount` <br><br> 직원은 액션을 통해 재배치, 입사, 퇴사 처리됩니다. 링크된 `Employee` 객체 수를 세는 파생 속성은 자동으로 올바른 값을 유지합니다. |

**주의**: 값이 액션을 통한 변경에 의존할 때는, 그 값에 영향을 줄 수 있는 모든 액션이 그 값도 함께 업데이트해야 합니다. 어느 하나의 액션이라도 그렇게 하지 않으면, 불일치가 발견될 때까지 값이 잘못된 상태로 남습니다.

<a id="anti-patterns"></a>
### 안티패턴 (Anti-patterns)

* 같은 값이 여러 객체 타입에 속성으로 저장되어 있습니다
* 다른 곳에서 관리되는 값의 사본이라서 속성이 낡은 값으로 남습니다
* 현실 세계의 사실 하나를 업데이트하려면 여러 객체에 쓰기를 해야 합니다
* 정수나 개수 속성을 링크에서 계산하지 않고 수동으로 관리합니다

<a id="example"></a>
### 예시 (Example)

`Manager` 객체 타입에 직속 부하 수를 표시해야 합니다.

```
✗ Avoid                                    ✓ Prefer
────────────────────────────────────────   ────────────────────────────────────────
Manager                                    Manager
  - directReportCount: 5                     - directReportCount (derived):
  (manually maintained integer;                counts linked Employee objects
   must be updated every time          →       at query time
   an employee joins or leaves)
                                           Employee
Employee                                     - manager (link to Manager)
  - managerName: "Alice"
  (copied from the linked Manager;
   breaks if the manager's name
   changes)
```

**설명**: 왼쪽(Avoid)에서 `Manager.directReportCount`는 수동으로 관리하는 정수라서 직원이 들어오거나 나갈 때마다 고쳐야 하고, `Employee.managerName`은 링크된 Manager에서 복사한 값이라 매니저 이름이 바뀌면 틀어집니다. 오른쪽(Prefer)에서는 `Employee`가 `manager` 링크만 갖고, `Manager.directReportCount`는 조회 시점에 링크된 `Employee` 객체 수를 세는 파생 속성입니다. SQL로 쓰면 `SELECT COUNT(*) FROM employee WHERE manager_id = ?`를 조회할 때마다 실행하는 것에 해당합니다.

<a id="performance-considerations"></a>
### 성능 고려 사항 (Performance considerations)

파생 속성은 런타임에 평가됩니다. 성능 특성은 규모에 따라 다릅니다.

| 규모 | 권장 사항 |
|-|-|
| 낮음에서 중간(쿼리당 객체 약 1만 개 미만) | 파생 속성을 자유롭게 사용하세요. 대부분의 워크플로에서 런타임 평가 성능이 충분합니다. |
| 높음(쿼리당 객체 약 1만 개 초과) | 오버헤드가 큰 쿼리 경로 때문에 파생 속성이 지연을 일으킬 수 있습니다. 비정규화가 적절한 트레이드오프일 수 있지만, 기본값이 아니라 의식적이고 문서화된 결정이어야 합니다. |

<a id="best-practices"></a>
### 모범 사례 (Best practices)

1. **각 사실은 의미상 속하는 객체에, 한 곳에만 저장하세요.**
2. **[파생 속성](../03_ontology-search/03_derived-properties.md)을 사용해** 조회 시점에 링크된 객체로부터 값을 계산하거나 집계하세요. 집계 종류별 상대 성능은 [파생 속성 참조](../03_ontology-search/04_derived-properties-reference.md#scale-and-performance-by-aggregation)를 확인하세요.
3. 규모가 커지면 **성능을 모니터링하세요**. 높은 규모에서 파생 속성이 받아들일 수 없는 지연을 일으키면 선택적인 비정규화를 고려하세요.
4. **모든 비정규화를 문서화하세요.** 그 근거, 원본 데이터(source of truth), 사본을 동기화 상태로 유지하기 위한 업데이트 전략을 함께 적습니다.

> **중간 요약**: 각 사실은 한 곳에만 저장하고, 링크된 객체나 액션으로 바뀌는 값은 파생 속성으로 조회 시점에 계산합니다. 같은 객체의 안정적인 입력만 쓰는 값은 파이프라인에서 미리 계산하고, 쿼리당 1만 개를 넘는 규모에서만 문서화된 결정으로 비정규화를 고려합니다.

<a id="structs"></a>
## 구조체 (Structs)

**의미상 관련된 필드는 구조체로 묶으세요.**

속성이 본래 여러 필드로 이루어져 있다면(예: 도로명, 도시, 주, 우편번호로 이루어진 주소), 별도 속성들로 평평하게 펼치지 말고 구조체(struct)를 사용하세요. 구조체는 의미상의 묶음을 보존하고 더 풍부한 메타데이터를 담을 수 있게 합니다.

**설명**: 구조체는 C의 `struct`나 Python의 `dataclass`처럼 이름 붙은 여러 필드를 하나의 값으로 묶은 타입입니다. 예를 들어 `address = { street: "Main St 1", city: "Boston", state: "MA", postalCode: "02101" }`는 속성 하나이지만 안에 필드 네 개를 가집니다.

<a id="when-to-use-structs"></a>
### 구조체를 사용할 때 (When to use structs)

| 시나리오 | 예시 |
|-|-|
| 여러 필드로 이루어진 값 | 주소(도로명, 도시, 주, 우편번호), 좌표(geopoint, 고도) |
| 메타데이터가 딸린 값 | 신뢰도 점수, 출처 참조, 추론 근거가 딸린 AI 생성 출력 |
| 선택 로직이 있는 다중 값 속성 | 리듀서(reducer)가 대표 번호를 골라 보여 주는 여러 개의 전화번호 |

<a id="example"></a>
### 예시 (Example)

`Facility` 객체 타입에 주소를 모델링하는 경우입니다.

```
✗ Avoid                                    ✓ Prefer
────────────────────────────────────────   ────────────────────────────────────────
Facility                                   Facility
  - addressStreet                            - address (struct array)
  - addressCity                                  - street (Main field)
  - addressState                     →           - city (Main field)
  - addressPostalCode                            - state (Main field)
  - addressCountry                               - postalCode (Main field)
  - addressGeopoint                              - country (Main field)
  - addressLastOccupied                          - geopoint
  - addressDatasource                            - lastOccupied (used for reducer sorting)
  - addressLlmConfidence                         - datasource
  - addressLlmReasoning                          - llmConfidence
                                                 - llmReasoning

(Ten unrelated properties with a
 naming convention as the only link         (One semantic concept with main
 between them)                               fields and structured sub-fields)
```

**설명**: 왼쪽은 `address` 접두사라는 이름 규칙만으로 서로 묶여 있는, 서로 관계없는 속성 10개입니다. 오른쪽은 `address`라는 구조체 배열 속성 하나로, 주소 본체인 `street`, `city`, `state`, `postalCode`, `country`를 주 필드(Main field)로 지정하고, 위치(`geopoint`), 리듀서 정렬에 쓰는 `lastOccupied`, 출처(`datasource`), LLM 신뢰도와 추론 근거를 하위 필드로 둡니다. "struct array"이므로 시설 하나가 주소를 여러 개 가질 수 있고, 리듀서가 그중 `lastOccupied`가 가장 최근인 주소를 대표 값으로 고를 수 있습니다.

<a id="key-benefits"></a>
### 주요 이점 (Key benefits)

| 이점 | 세부 내용 |
|-|-|
| 의미상의 묶음 | 주소는 서로 관계없는 속성 10개가 아니라 하나의 개념입니다. 온톨로지가 이를 그대로 반영합니다. |
| 메타데이터 담기 | 구조체는 주 값과 함께 출처, 신뢰도, 타임스탬프 정보를 담을 수 있습니다. |
| 리듀서 지원 | 다중 값 시나리오에서 리듀서가 가장 관련성 높은 값(예: `lastOccupied` 필드가 가장 최근인 주소)을 골라 보여 줄 수 있습니다. |
| 주 필드 동작 | 구조체는 하나 이상의 주 필드를 지정할 수 있어서, 인터페이스와 쿼리에서 단순 속성처럼 동작하거나 필드 일부만 가진 구조체처럼 동작할 수 있습니다. |

구조체는 대규모 언어 모델(LLM) 출력에 주 결과와 그에 딸린 메타데이터(추론 근거, 출처 참조, 신뢰도 점수)가 함께 있는 AI 우선 워크플로에서 특히 가치가 큽니다. 이런 값들을 서로 관계없는 속성에 흩어 놓지 말고 함께 담으세요.

<a id="best-practices"></a>
### 모범 사례 (Best practices)

1. 필드들이 의미상 관련되어 있고 항상 함께 쓰이는 **다중 필드 속성을 식별하세요**.
2. 명확한 필드 이름과 타입으로 **구조체를 정의하세요**.
3. 대부분의 상황에서 구조체가 단순 속성처럼 동작하도록 **주 필드를 지정하세요**.
4. 다중 값 구조체 속성에는 가장 관련성 높은 값을 보여 주도록 **리듀서를 사용하세요**.
5. 특히 AI 생성 출력의 경우, 주 값과 함께 **메타데이터(출처, 신뢰도, 타임스탬프)를 구조체에 담으세요**.

> **중간 요약**: 주소처럼 여러 필드가 한 개념을 이루거나 값에 메타데이터가 딸린 경우, 속성을 펼치지 말고 구조체로 묶습니다. 주 필드를 지정하면 단순 속성처럼 쓸 수 있고, 다중 값이면 리듀서로 대표 값을 고릅니다.

<a id="interfaces"></a>
## 인터페이스 (Interfaces)

**재사용 가능하고 미래에도 유효한 추상화를 만들려면 인터페이스를 사용하세요.**

인터페이스는 ["같은 것을 반복하지 않기" 설계 원칙](06_ontology-best-practices.md#2-do-not-repeat-yourself-rule-of-three)과 [개방-폐쇄 확장성](06_ontology-best-practices.md#3-open-for-extension-closed-for-modification)을 달성하는 주된 도구입니다. 인터페이스는 여러 객체 타입이 구현할 수 있는 공유 모양(속성, 링크, 액션)을 정의하므로, 워크플로가 개별 타입 대신 인터페이스를 대상으로 삼을 수 있게 합니다.

<a id="when-to-use-interfaces"></a>
### 인터페이스를 사용할 때 (When to use interfaces)

| 시나리오 | 예시 |
|-|-|
| 여러 타입에 공통된 속성 | `lastInspectionDate`와 `inspectionStatus`를 가진 `Inspectable` 인터페이스를 `Vehicle`, `Equipment`, `Facility`가 구현 |
| 공유 워크플로 | `SchedulableResource`를 대상으로 하는 일정 관리 워크플로가 수정 없이 경기장, 회의실, 차량에 모두 동작 |
| 분류상의 묶음 | 드릴다운 집계 워크플로를 위해 `Aircraft`, `Vessel`, `GroundVehicle`이 구현하는 `MilitaryAsset` 인터페이스 |
| 다단계 추상화 | `SchedulableResource`가 `Trackable`을 확장해, 더 넓은 추적 추상화에 일정 관리 전용 속성을 추가 |

<a id="example"></a>
### 예시 (Example)

여러 객체 타입에 점검 추적이 필요합니다.

```
✗ Avoid                                    ✓ Prefer
────────────────────────────────────────   ────────────────────────────────────────
Vehicle                                    Interface: Inspectable
  - lastInspectionDate                       - lastInspectionDate
  - inspectionStatus                         - inspectionStatus
  - (duplicate action: Schedule              - (shared action: Schedule Inspection)
     Vehicle Inspection)
                                     →     Vehicle implements Inspectable
Equipment                                    - make, model, mileage, ...
  - lastInspectionDate
  - inspectionStatus                       Equipment implements Inspectable
  - (duplicate action: Schedule              - serialNumber, warrantyExpiry, ...
     Equipment Inspection)
                                           Facility implements Inspectable
Facility                                     - address, capacity, ...
  - lastInspectionDate
  - inspectionStatus                       (One interface, one shared action,
  - (duplicate action: Schedule             three implementing types)
     Facility Inspection)

(Three copies of the same properties
 and logic, maintained independently)
```

**설명**: 왼쪽은 `Vehicle`, `Equipment`, `Facility`가 같은 점검 속성 2개와 거의 같은 점검 예약 액션을 각자 따로 가진 구조로, 같은 속성과 로직의 사본 세 벌이 독립적으로 관리됩니다. 오른쪽은 점검 속성과 `Schedule Inspection` 공유 액션을 `Inspectable` 인터페이스에 한 번만 정의하고, 세 타입은 이를 구현하면서 자기 고유 속성(`make`, `serialNumber`, `address` 등)만 따로 가집니다. 인터페이스 하나, 공유 액션 하나, 구현 타입 셋이 됩니다.

<a id="platform-considerations"></a>
### 플랫폼 고려 사항 (Platform considerations)

현재 플랫폼 도구가 인터페이스 기반 워크플로를 완전히 지원하지 않는 경우에도, 인터페이스를 염두에 두고 설계하면 지원이 확대될수록 효과를 보는 기반을 마련할 수 있습니다.

| 상황 | 지침 |
|-|-|
| 워크플로에서 인터페이스가 완전히 지원됨 | 인터페이스를 직접 대상으로 삼으세요. 워크플로 하나로 모든 구현 타입을 처리합니다. |
| 특정 맥락에서 인터페이스가 아직 지원되지 않음 | 지금 인터페이스를 정의하고, 임시 조치로 워크플로를 타입별로 복제하세요. 이 방법은 인터페이스 없이 작업하는 것보다 비효율적이지 않으며, 지원이 제공되면 통합할 수 있는 분명한 경로를 마련해 줍니다. |

현재 지원 세부 사항은 [인터페이스 문서](05_interfaces/01_interface-overview.md)를 확인하세요.

<a id="best-practices"></a>
### 모범 사례 (Best practices)

1. **공통 모양을 식별하기:** 여러 객체 타입이 속성, 링크, 액션을 공유한다면 그 공유 모양을 담는 인터페이스를 정의합니다.
2. **기능이나 분류를 중심으로 인터페이스 설계하기:** 기능 인터페이스의 예로는 `Inspectable`, `Schedulable`, `Billable`이 있습니다. 분류 인터페이스의 예로는 `MilitaryAsset`, `MedicalDevice`가 있습니다.
3. **워크플로에서 인터페이스를 대상으로 삼기:** 가능하면 액션, 함수(function), 애플리케이션을 인터페이스를 기준으로 만듭니다.
4. **다단계 추상화를 위해 인터페이스 확장하기:** 인터페이스는 다른 인터페이스를 확장해 계층화된 추상화를 만들 수 있습니다.
5. **지금 뼈대를 세우고 나중에 통합하기:** 현재 플랫폼 지원의 공백 때문에 일부 워크플로를 임시로 타입별로 복제해야 하더라도 인터페이스는 정의해 둡니다.

> **중간 요약**: 여러 타입이 공유하는 속성, 링크, 액션은 인터페이스로 한 번만 정의하고 워크플로는 인터페이스를 대상으로 만듭니다. 아직 지원이 부족한 곳에서도 인터페이스를 먼저 정의해 두면 나중에 통합하기 쉽습니다.

<a id="links-and-object-backed-link-types"></a>
## 링크와 객체 기반 링크 타입 (Links and object-backed link types)

**링크는 의미 있는 관계를 나타내야 합니다.**

모든 링크 타입은 다음과 같은 명확한 도메인 질문에 답해야 합니다.

* 이 환자는 어느 시설을 방문했는가?
* 이 직원은 어느 팀에 속하는가?
* 이 작업 지시에는 어떤 장비가 사용되었는가?

<a id="when-to-use-link-types"></a>
### 링크 타입을 사용할 때 (When to use link types)

| 링크 타입 | 사용하는 경우 | 예시 |
|-|-|-|
| 직접 링크(Direct link) | 관계가 의미 있지만 자체 메타데이터를 갖지 않을 때. | `Employee`에서 `Department`로 |
| 객체 기반 링크(Object-backed link) | 관계가 자체 메타데이터(날짜, 역할, 상태, 배정 비율)를 가질 때. | `Employee`에서 `VentureStaffing`을 거쳐 `Venture`로(`role`, `startDate`, `allocation` 포함) |

모든 연결 객체가 모든 맥락에서 보일 필요는 없습니다. 어떤 워크플로는 조인 메타데이터를 중요하게 여기고, 다른 워크플로는 직접 연결만 원합니다. 객체 기반 링크를 사용하면 워크플로에 따라 둘 중 어느 쪽 보기든 노출할 수 있습니다.

**설명**: 객체 기반 링크는 데이터베이스의 다대다 관계에서 쓰는 연결 테이블(junction table)을 객체 타입으로 만든 것입니다. 예를 들어 `venture_staffing(employee_id, venture_id, role, start_date, allocation)` 테이블의 행 하나는 "직원 E1이 벤처 V7에 2026-03-01부터 개발자 역할로 50% 배정됨"이라는 배정 한 건입니다. 이 행을 `VentureStaffing` 객체로 만들면 관계 자체에 속성을 붙일 수 있습니다.

<a id="example"></a>
### 예시 (Example)

각 배정마다 역할과 시작일이 있는, 직원과 벤처 사이의 관계를 모델링하는 경우입니다.

```
✗ Avoid                                    ✓ Prefer
────────────────────────────────────────   ────────────────────────────────────────
Employee → Venture (direct link)           Employee → Venture Staffing → Venture
  (no way to capture role,
   start date, or allocation         →     Venture Staffing
   per assignment)                           - role
                                             - startDate
— OR —                                       - allocationPercentage
                                             - status
Employee
  - ventureRole                            Workflows can expose either:
  - ventureStartDate                         - Direct: Employee → Venture
  (ambiguous if employee has                 - Detailed: Employee → Staffing → Venture
   multiple venture assignments)
```

**설명**: 왼쪽은 피해야 할 두 가지 방식입니다. 첫째, `Employee`와 `Venture`를 직접 링크하면 배정별 역할, 시작일, 배정 비율을 담을 곳이 없습니다. 둘째, `Employee`에 `ventureRole`, `ventureStartDate` 속성을 두면 직원이 여러 벤처에 배정되었을 때 어느 벤처의 역할인지 모호해집니다. 오른쪽은 `Venture Staffing` 객체(`role`, `startDate`, `allocationPercentage`, `status`)를 사이에 두는 방식이며, 워크플로는 직접 보기(직원에서 벤처로)나 상세 보기(직원에서 배정을 거쳐 벤처로) 중 하나를 골라 노출할 수 있습니다.

<a id="impact-of-incorrect-link-design"></a>
### 잘못된 링크 설계의 영향 (Impact of incorrect link design)

| 문제 | 영향 |
|-|-|
| 메타데이터 손실 | 직접 링크로는 관계가 언제, 왜, 어떤 자격으로 존재하는지 담을 수 없습니다. |
| 모호한 다중 링크 | 엔터티가 여러 관계에 참여하면 원천 객체의 `ventureRole` 같은 속성이 모호해집니다. |
| 의미 없는 링크 | 두 데이터셋이 외래 키를 공유한다는 이유만으로 존재하는 링크는 온톨로지에 잡음을 더하고 탐색을 혼란스럽게 합니다. |

<a id="best-practices"></a>
### 모범 사례 (Best practices)

1. **의미를 검증하기:** 두 데이터셋이 외래 키를 공유한다는 이유만으로 존재하는 링크는 피하세요. 그 관계가 도메인에서 의미가 있는지 물어보세요.
2. **관계가 메타데이터를 갖는지 평가하기:** 날짜, 역할, 상태 같은 메타데이터가 있다면 객체 기반 링크 타입으로 그 메타데이터를 담으세요.
3. **알맞은 수준의 세부 정보 노출하기:** 맥락에 따라 직접 관계를 쓰거나 연결 객체를 통한 상세 관계를 쓰도록 워크플로를 설계하세요.
4. **명확한 링크 이름 붙이기:** 링크 이름은 각 방향에서 본 관계를 설명해야 합니다. 자세한 내용은 [이름 규칙](#naming-conventions) 섹션을 참조하세요.

> **중간 요약**: 링크는 외래 키가 있어서가 아니라 도메인에서 의미 있는 질문에 답할 때만 만듭니다. 관계 자체에 날짜, 역할, 상태 같은 정보가 있으면 연결 객체를 두는 객체 기반 링크를 사용합니다.

<a id="naming-conventions"></a>
## 이름 규칙 (Naming conventions)

**사람이 읽기 쉽고 에이전트가 탐색하기 쉽게 최적화하세요.**

일관되고 설명적인 이름 짓기는 온톨로지 품질을 위해 할 수 있는 가장 효과가 큰 투자 중 하나입니다. 명확한 이름은 사람과 AI 에이전트 모두가 온톨로지를 더 쉽게 탐색하게 해 주며, 온톨로지가 사용되기 시작하면 이름을 고치기는 훨씬 어려워집니다.

<a id="naming-rules"></a>
### 이름 규칙 (Naming rules)

| 요소 | 규칙 | 좋은 예 | 나쁜 예 |
|-|-|-|-|
| 객체 타입 | 도메인 전문가가 알아볼 수 있는 단수형 구체 명사 | `Patient`, `WorkOrder`, `FlightSegment` | `Data`, `Item`, `Record` |
| 속성 | 간결하고 그 자체로 의미가 드러남. 타입 정보나 구현 세부 사항을 이름에 넣지 않음 | `age`, `status`, `lastInspectionDate` | `dtLastInspMod`, `nVAL01`, `fieldX` |
| 링크 | 각 방향에서 자연스럽게 읽힘 | `department`(Employee에서 Dept 방향), `employees`(Dept에서 Employee 방향) | `relatedItems`, `link1` |
| 날짜 | 온톨로지 전체에서 하나의 규칙을 일관되게 따름 | `createdDate`, `updatedDate`, `effectiveDate` | `createdDate`와 `dateOfCreation`을 섞어 씀 |
| 모호한 용어 | 구체적인 의미로 한정함 | `monetaryValue`, `quantityOnHand`, `riskScore` | `value`, `quantity`, `score` |

<a id="example"></a>
### 예시 (Example)

```
✗ Avoid                                    ✓ Prefer
────────────────────────────────────────   ────────────────────────────────────────
Object type: Item                    →     Object type: Product

Property: dtLastInspMod              →     Property: lastInspectionDate

Property: value                      →     Property: monetaryValue
                                           Property: quantityOnHand

Link: Item → Related Item            →     Link: Product → Supplier
                                           Link: Employee → Supervisor
```

**설명**: 왼쪽의 막연한 이름을 오른쪽의 구체적인 이름으로 바꾼 예입니다. `Item`은 `Product`로, 축약어 `dtLastInspMod`는 `lastInspectionDate`로, 모호한 `value`는 의미에 따라 `monetaryValue`(금액)나 `quantityOnHand`(보유 수량)로 나누고, `Item`과 `Related Item` 사이의 막연한 링크는 `Product`와 `Supplier`, `Employee`와 `Supervisor`처럼 관계가 드러나는 링크로 바꿉니다.

<a id="best-practices"></a>
### 모범 사례 (Best practices)

1. **만들기 전에 이름 규칙 정하기:** 날짜, 상태, 식별자, 링크의 패턴을 미리 합의합니다.
2. **온톨로지에서 이미 자리 잡은 규칙 따르기:** 온톨로지가 이미 `createdDate`를 쓰고 있다면 `dateOfCreation`을 새로 들이지 마세요.
3. **모호한 속성 한정하기:** `monetaryValue`, `quantityOnHand`, `riskScore`를 쓰세요. `value`, `quantity`, `score`는 쓰지 마세요.
4. **관계에 따라 링크 이름 붙이기:** `Employee`에서 `Department`로 가는 링크는 직원 관점에서 `department`, 부서 관점에서 `employees`여야 합니다.
5. **최종 사용자와 함께 이름 검토하기:** 빌더에게 명확해 보이는 이름이 소비자에게는 모호할 수 있습니다. [분석 훈련(analytical drills)](09_ontology-design-validation.md#exercise-formats)을 활용해 사용자가 검색하는 용어와 그들이 찾을 것으로 기대하는 관계를 관찰하세요.

> **중간 요약**: 객체 타입은 단수형 구체 명사로, 속성은 축약 없이 의미가 드러나게, 링크는 양방향에서 자연스럽게 읽히도록 이름 짓습니다. 규칙은 미리 정해 일관되게 따르고, 사용자와 함께 검토합니다.

<a id="security-design"></a>
## 보안 설계 (Security design)

**최소 권한 원칙에 따라, 보안을 의미에 맞게 설계하세요.**

온톨로지의 보안은 데이터 인프라의 용어가 아니라 도메인에서 이해되는 용어로 표현되어야 합니다. 사용자가 보안 구성을 보고 무엇이 왜 보호되는지 이해할 수 있어야 합니다.

<a id="security-model"></a>
### 보안 모델 (Security model)

행 수준 보안과 열 수준 보안을 결합해 세밀한 셀 수준 접근 제어를 구현합니다.

| 보안 계층 | 제어 대상 | 예시 |
|-|-|-|
| 행 수준(Row-level) | 사용자가 볼 수 있는 객체 | VIP 환자는 선임 직원에게만 공개 |
| 열 수준(Column-level) | 볼 수 있는 객체에서 사용자가 볼 수 있는 속성 | 임상 기록은 담당 진료팀에게만 공개 |
| 셀 수준(결합, Cell-level (combined)) | 행 제한과 열 제한의 교집합 | VIP 환자의 임상 기록은 선임 진료팀에게만 공개 |

**설명**: `Patient` 테이블을 예로 들면, 행 수준 보안은 `WHERE` 조건으로 볼 수 있는 행을 거르는 것이고(VIP 행은 선임 직원만 조회), 열 수준 보안은 `SELECT`할 수 있는 열을 제한하는 것입니다(`clinicalNotes` 열은 진료팀만 조회). 둘을 함께 적용하면 "VIP 환자 행의 `clinicalNotes` 칸"처럼 특정 셀 단위로 접근이 결정됩니다. 최소 권한 원칙(principle of least privilege)은 각 사용자에게 업무에 꼭 필요한 최소한의 접근만 주라는 보안 원칙입니다.

<a id="example"></a>
### 예시 (Example)

민감한 환자 데이터에 대한 접근을 제어하는 경우입니다.

```
✗ Avoid                                    ✓ Prefer
────────────────────────────────────────   ────────────────────────────────────────
PublicPatient (object type)                Patient (single object type)
  - name                                     - name
  - dob                                      - dob
  - diagnosis                                - diagnosis (column-restricted:
                                                 care team only)
RestrictedPatient (object type)      →       - clinicalNotes (column-restricted:
  - name                                         care team only)
  - dob                                      - mentalHealthRecords (column-
  - diagnosis                                    restricted: psychiatry team only)
  - clinicalNotes
  - mentalHealthRecords                    Row-level security:
                                             - VIP patients: senior staff only
(Duplicated schemas; security
 achieved by splitting types.              Column-level security:
 Properties added to one type are            - clinicalNotes: care team only
 easily forgotten on the other.)             - mentalHealthRecords: psychiatry only

                                           (One type; security achieved by policy.
                                            Domain boundaries drive access rules.)
```

**설명**: 왼쪽은 보안을 위해 `PublicPatient`와 `RestrictedPatient` 두 타입으로 쪼갠 설계로, 스키마가 중복되고 한쪽에 추가한 속성을 다른 쪽에 빠뜨리기 쉽습니다. 오른쪽은 `Patient` 타입 하나를 두고 정책으로 보안을 거는 설계입니다. 열 수준 보안으로 `diagnosis`와 `clinicalNotes`는 진료팀만, `mentalHealthRecords`는 정신의학팀만 보게 하고, 행 수준 보안으로 VIP 환자는 선임 직원만 보게 합니다. 도메인 경계가 접근 규칙을 결정합니다.

<a id="impact-of-incorrect-security-design"></a>
### 잘못된 보안 설계의 영향 (Impact of incorrect security design)

| 문제 | 영향 |
|-|-|
| 보안을 위한 타입 중복 | 스키마가 서로 어긋나고, 한 타입에 추가한 속성을 다른 타입에서 빠뜨리기 쉽습니다. ["같은 것을 반복하지 않기" 설계 원칙](06_ontology-best-practices.md#2-do-not-repeat-yourself-rule-of-three)을 위반합니다. |
| 지나치게 허용적인 기본값 | 넓은 접근으로 시작해 나중에 제한하면, 잠금이 끝나기 전에 민감한 데이터가 노출될 위험이 있습니다. |
| 정책 대신 임시방편 필터링 | 보안 로직이 온톨로지 계층에서 강제되지 않고 애플리케이션 코드 곳곳에 흩어져 있으면 깨지기 쉽고 감사하기 어렵습니다. |
| 어긋난 경계 | 도메인 경계를 따르지 않는 보안 경계는 추론하기 어렵고 빈틈이 생기기 쉽습니다. |

<a id="best-practices"></a>
### 모범 사례 (Best practices)

1. **제한적으로 시작하고 신중하게 열기:** 열어 둔 채 시작해 나중에 제한하지 말고, 최소한의 접근을 기본으로 하고 필요에 따라 넓히세요.
2. 세밀한 셀 수준 접근 제어를 위해 **행 수준 보안과 열 수준 보안을 함께 사용하세요**.
3. **보안을 도메인 경계에 맞추기:** 도메인에 자연스러운 접근 경계가 있다면(지역 관리자는 자기 지역의 데이터를 보고, 진료팀은 자기 환자를 봄), 임시방편 데이터 필터링 대신 온톨로지 관계와 보안 정책을 사용해 그 경계를 모델링하세요.
4. **보안을 위해 객체 타입을 복제하지 않기:** 잘 설계된 보안 정책을 가진 단일 타입이, 스키마가 중복된 여러 타입보다 낫습니다.
5. **새 온톨로지 경로의 접근 제어 일관성 검토하기:** 추가한 링크, 타입, 속성이 제한된 데이터에 대해 의도한 보호를 유지하는지 확인하세요.

이 페이지의 지침을 활용해 보안 경계가 도메인 경계와 일치하도록 한 다음, 구성 세부 사항은 [보안 및 거버넌스 문서](https://www.palantir.com/docs/foundry/security/overview/)를 참조하세요. 접근 제어는 누가 데이터를 사용할 수 있는지에 답하는 반면, 프라이버시와 시민적 자유(privacy and civil liberties) 계획은 워크플로가 왜 그 데이터를 필요로 하는지, 더 적은 데이터로도 목적을 달성할 수 있는지도 묻습니다. 이러한 설계 결정을 내릴 때는 [실무에서의 프라이버시와 시민적 자유](https://www.palantir.com/docs/foundry/privacy-civil-liberties/pcl-in-practice/)를 검토하세요.

**설명**: 5번 모범 사례의 "새 온톨로지 경로"는 링크를 따라가는 새 탐색 경로를 말합니다. 예를 들어 `Patient`의 `mentalHealthRecords`를 정신의학팀만 볼 수 있게 해 두었는데, 누군가 `Patient`에서 `PsychiatricVisit` 객체로 가는 링크를 새로 만들고 그 객체에 같은 진단 정보를 속성으로 넣으면, 원래 보호하려던 정보가 다른 경로로 노출될 수 있습니다. 링크, 타입, 속성을 추가할 때마다 이런 우회 경로를 점검하라는 뜻입니다.

> **중간 요약**: 보안은 최소 권한으로 시작하고, 타입을 쪼개는 대신 단일 타입에 행 수준과 열 수준 정책을 결합해 도메인 경계에 맞춰 설계합니다. 새 링크나 속성이 보호를 우회하지 않는지 확인하고, 접근 제어와 별도로 데이터가 꼭 필요한지도 검토합니다.

## 정리

- 각 사실은 한 곳에만 저장하고, 링크나 액션으로 바뀌는 값은 파생 속성으로, 같은 객체의 안정적 입력으로 만든 값은 파이프라인으로 계산합니다.
- 여러 필드가 한 개념을 이루거나 메타데이터가 딸린 값은 구조체로 묶고, 주 필드와 리듀서를 활용합니다.
- 여러 타입이 공유하는 모양은 인터페이스로 정의하고, 지원이 부족한 곳에서도 인터페이스를 먼저 세워 둡니다.
- 링크는 의미 있는 관계에만 만들고, 관계에 메타데이터가 있으면 객체 기반 링크를 사용합니다.
- 이름은 구체적이고 일관되게 짓고, 보안은 최소 권한과 행, 열 수준 정책 결합으로 도메인 경계에 맞춰 설계합니다.
