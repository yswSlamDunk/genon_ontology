# 사용량 보기 (Viewing usage)

- 원문: https://www.palantir.com/docs/foundry/ontology-manager/view-usage/
- 사이드바 위치: Applications > Ontology Manager > Viewing usage

이 페이지는 Ontology Manager에서 객체 타입과 링크 타입이 얼마나, 누구에게, 어떤 애플리케이션에서 쓰이고 있는지 보여 주는 사용량 지표(Ontology metrics)를 설명합니다. 객체 타입을 바꾸거나 지우기 전에 그 변경이 누구에게 영향을 주는지 파악하는 데 쓰입니다. 원문 페이지의 제목은 "Ontology metrics"입니다.

Ontology Manager는 객체 타입과 링크 타입의 사용량 지표를 표시하도록 설정할 수 있습니다.

<a id="key-terminology"></a>
## 핵심 용어 (Key terminology)

* **Reads(읽기):** 애플리케이션이 지정된 객체 타입의 객체를 로드할 때 읽기 한 건이 기록됩니다. Workshop의 테이블에 객체를 표시하는 것, 특정 객체 타입에 대해 검색으로 모든 객체를 반환하는 것, 객체 타입의 속성을 집계하는 것 등이 여기에 포함될 수 있습니다. 읽기 한 건은 [Object Storage v1 (Phonograph)](../../06_ontology-architecture/05_object-databases/01_object-storage-v1.md) 또는 Object Set Service(OSS)에 대한 로드 요청 한 번을 뜻합니다. 많은 객체를 한 번에 로드하거나 집계해도 읽기 한 건으로만 기록됩니다. Ontology Manager 안에서 일어난 객체 타입이나 링크 타입 사용은 포함되지 않습니다.
* **Writes(쓰기):** 애플리케이션이 [액션](../../02_define-ontologies/03_action-types/01_overview.md), [함수](../../02_define-ontologies/04_functions/01_overview.md), Foundry Form, Object Explorer에서의 직접 편집, API 호출의 결과로 이 타입의 객체를 편집(edit)할 때 쓰기 한 건이 기록됩니다. 쓰기 한 건은 [Object Storage v1 (Phonograph)](../../06_ontology-architecture/05_object-databases/01_object-storage-v1.md)으로 보낸 편집 요청 한 번을 뜻합니다. 많은 객체를 한 번에 일괄 편집해도 쓰기 한 건으로만 기록됩니다.
* **Interactions(상호작용):** 지난 30일 동안 이 타입의 객체에 대해 일어난 읽기와 쓰기의 총수입니다.
* **Active users(활성 사용자):** 지난 30일 동안 기록된 읽기와 쓰기를 발생시킨 고유 사용자 ID의 수입니다.

**설명**: 지표는 객체 개수가 아니라 요청 횟수로 셉니다. 예를 들어 Workshop 테이블이 Flight 객체 500개를 한 번의 요청으로 불러오면 읽기는 500이 아니라 1로 기록됩니다. SQL로 치면 `SELECT * FROM flights LIMIT 500` 쿼리 한 번이 한 건이고, `UPDATE`로 행 100개를 한 번에 바꾸는 것도 쓰기 한 건입니다. 활성 사용자는 같은 사람이 여러 번 요청해도 한 명으로 셉니다(`COUNT(DISTINCT user_id)`).

> **중간 요약**: 읽기와 쓰기는 객체 수가 아니라 저장소로 보낸 요청 수로 기록되고, 상호작용은 30일간 읽기와 쓰기의 합, 활성 사용자는 30일간의 고유 사용자 수입니다.

<a id="viewing-usage"></a>
## 사용량 보기 (Viewing usage)

Ontology Manager에서 객체 타입과 링크 타입의 사용량을 볼 수 있는 곳은 두 군데입니다.

* **Overview** 탭의 사용량 그래프: 지난 30일 동안의 사용량을 개략적으로 요약해, 온톨로지 사용자가 이 리소스에 호환성을 깨는 변경(breaking change)을 했을 때의 영향을 빠르게 파악할 수 있게 합니다.

![Overview 탭의 사용량 그래프](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-overview-usage.png)

**참고**: 사용량 그래프가 비어 있다면 내부 테이블이 설정되지 않았을 수 있습니다(Empty usage graph may indicate unconfigured internal tables). 사용량 통계가 있을 것으로 예상되는데 사용량 그래프에 "No usage for the last 30 days"가 보인다면, 내부 테이블이 설정되지 않았을 가능성이 있습니다. 자세한 내용은 Palantir 담당자에게 문의하세요.

* 전용 **Usage** 탭: 리소스의 상세 사용량 지표를 보여 줍니다. 사용자는 지난 30일 동안 누가, 언제, 어느 Foundry 애플리케이션에서 각 객체 타입을 사용했는지 볼 수 있습니다. 이 기능은 변경의 영향을 더 명확히 이해하게 해 줌으로써 온톨로지 사용자가 온톨로지를 더 안전하게 변경하도록 돕기 위한 것입니다. **Overview** 탭의 사용량 그래프에서 **See more**를 클릭해도 **Usage** 탭으로 이동할 수 있습니다.

![Usage 탭](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-usage-tab.png)

**설명**: 호환성을 깨는 변경(breaking change)은 기존 사용처가 더 이상 동작하지 않게 만드는 변경입니다. 예를 들어 속성 이름을 바꾸거나 삭제하면, 그 속성을 표시하던 Workshop 화면이나 그 속성을 읽던 함수가 오류를 낼 수 있습니다. **Usage** 탭에서 지난 30일간 이 객체 타입을 쓴 애플리케이션과 사용자를 확인하면 누구에게 미리 알려야 하는지 알 수 있습니다.

> **중간 요약**: **Overview** 탭의 그래프는 30일 사용량을 요약해 보여 주고, **Usage** 탭은 누가 언제 어느 애플리케이션에서 사용했는지 상세히 보여 줍니다. 그래프가 예상과 달리 비어 있으면 내부 테이블 미설정을 의심해야 합니다.

<a id="enabling-ontology-usage"></a>
## 온톨로지 사용량 활성화하기 (Enabling Ontology usage)

**Overview** 탭의 사용량과 **Usage** 탭의 상세 사용량 지표는 Control Panel의 **Ontology settings** 탭에 있는 **Ontology metrics** 토글로 설정합니다. 이 토글은 온톨로지 관리자만 켜거나 끌 수 있으며, 변경 사항이 Ontology Manager에 반영되기까지 최대 60분이 걸릴 수 있습니다.

<a id="shared-ontology-usage"></a>
## 공유 온톨로지 사용량 (Shared Ontology usage)

조직이 다른 조직과 온톨로지를 공유하고 있다면, Ontology metrics를 켠 모든 조직의 사용자가 **Usage** 탭에 접근할 수 있습니다. 표시되는 사용량 지표에는 해당 객체 타입에 접근 권한이 있는 사용자이면서 Ontology metrics를 켠 조직에 속한 사용자의 사용량만 포함됩니다. 자세한 내용은 [온톨로지 사용량 활성화하기](#enabling-ontology-usage)의 단계를 참고하세요.

> **중간 요약**: 사용량 지표는 온톨로지 관리자가 Control Panel의 **Ontology metrics** 토글로 켜며(반영까지 최대 60분), 공유 온톨로지에서는 지표를 켠 조직의 사용자 사용량만 집계됩니다.

## 정리

- 읽기와 쓰기는 객체 개수가 아니라 저장소로 보낸 요청 횟수로 기록되며, Ontology Manager 안에서의 사용은 제외됩니다.
- 상호작용은 30일간 읽기와 쓰기의 합계, 활성 사용자는 30일간의 고유 사용자 수입니다.
- **Overview** 탭의 그래프로 요약을, **Usage** 탭으로 누가 언제 어디서 썼는지를 확인해 변경의 영향을 파악합니다.
- 지표는 온톨로지 관리자가 Control Panel의 **Ontology metrics** 토글로 활성화하고, 공유 온톨로지에서는 지표를 켠 조직의 사용량만 보입니다.
