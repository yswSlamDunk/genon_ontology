# 속성 메타데이터 참조 (Metadata reference)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/property-metadata/
- 사이드바 위치: Define Ontologies > Object and link types > Properties > Metadata reference

이 페이지는 온톨로지에서 속성(property) 하나를 표현하는 메타데이터 항목(ID, 표시 이름, 설명, RID, 상태, API 이름, 키, 기본 타입, 서식, 타입 클래스, 렌더 힌트, 가시성)을 한곳에 정리한 참조 문서입니다. 또한 일부 기본 타입(`byte`, `float`, `short`, `vector`)이 기능상 제한을 받는다는 점도 설명합니다. 속성 편집기의 각 설정 칸이 무엇을 뜻하는지 확인할 때 펼쳐 보는 용도로 쓰입니다.

속성은 온톨로지에서 다음 메타데이터로 표현됩니다.

* **ID:** 속성의 고유 식별자로, 주로 애플리케이션을 설정할 때 속성을 참조하는 데 사용됩니다. 예를 들어 `start-date`가 시작일(start date) 속성의 ID일 수 있습니다.
* **표시 이름(Display name):** 사용자 애플리케이션에서 이 속성의 값에 접근하는 모든 사람에게 보이는 이름입니다. 예를 들어 `start date` 속성의 표시 이름은 `Start date`일 수 있습니다.
* **설명(Description):** 사용자 애플리케이션에서 누구나 읽을 수 있는 속성에 대한 설명 텍스트입니다. 예를 들어 `start date` 속성의 설명은 `The day the employee began new hire training`(직원이 신규 입사자 교육을 시작한 날)일 수 있습니다.
* **RID:** Foundry의 모든 리소스에 자동으로 생성되는 고유 식별자입니다. 속성의 RID는 플랫폼 전반의 오류 메시지에서 참조됩니다.
* **상태(Status):** 속성이 개발 과정의 어느 단계에 있는지를 사용자와 다른 온톨로지 빌더에게 알리는 신호입니다. `active`, `experimental`, `deprecated` 중 하나일 수 있습니다. 기본적으로 `start date` 속성의 상태는 `experimental`입니다. [상태](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.
* **API 이름(API name):** 코드에서 프로그래밍 방식으로 속성을 가리킬 때 쓰는 이름입니다. 예를 들어 `start date` 속성의 API 이름은 `startDate`일 수 있습니다. [API 이름(TSv1)](../../04_functions/13_functions-on-objects/06_api-objects-links.md)에 대해 더 읽어 보세요.
* **키(Keys):** 속성이 객체 타입의 타이틀 키(title key)인지 기본 키(primary key)인지를 나타냅니다.
  * **타이틀 키는** 이 타입 객체의 표시 이름 역할을 하는 속성입니다. 예를 들어 `Employee` 객체 타입의 타이틀 키로 `full name` 속성을 지정하면, 가상의 직원 "Melissa Chang"과 "Diego Rodriguez"처럼 그 속성의 값이 각 `Employee` 객체의 표시 이름으로 사용됩니다.
  * **기본 키는** 객체 타입의 각 인스턴스를 고유하게 식별하는 역할을 하는 속성입니다. 즉 백킹 데이터소스의 모든 행은 이 속성에 대해 서로 다른 값을 가져야 합니다. 예를 들어 `employee number` 속성의 값으로 "Melissa Chang"을 조직 내의 고유한 직원으로 식별할 수 있습니다.
* **기본 타입(Base type):** 이 속성의 값이 어떤 타입인지를 나타내며, 사용자 애플리케이션에서 사용할 수 있는 연산의 범위를 결정합니다. 예를 들어 `start date` 속성의 기본 타입은 `date`입니다. 사용자 애플리케이션은 이 속성으로 타임라인 위젯을 설정할 수 있게 해 줍니다.
* **값 서식(Value formatting):** 속성의 기본 타입에 따라 숫자 서식, 날짜와 시간 서식, 사용자 ID 서식, 리소스 ID 서식을 속성에 적용할 수 있으며, 이 서식은 사용자 애플리케이션에서 원시 값을 더 읽기 쉬운 형태로 바꿔 보여 줍니다. [값 서식](03_value-formatting.md)에 대해 더 읽어 보세요.
* **조건부 서식(Conditional formatting):** 사용자용 애플리케이션에서 속성 값이 어떻게 표시될지(예: 색상, 정렬 등)를 정하는, 속성에 설정된 규칙입니다. 예를 들어 사용자 애플리케이션에서 신규 입사자를 표시하기 위해, `start date` 속성의 값이 2주 이내이면 `full name` 속성의 값을 초록색으로 칠하는 규칙을 `full name` 속성에 설정할 수 있습니다. [조건부 서식](04_conditional-formatting.md)에 대해 더 읽어 보세요.
* **타입 클래스(Type classes):** 사용자 애플리케이션이 해석하는 추가 메타데이터입니다. [타입 클래스](../09_metadata/01_metadata-typeclasses.md)에 대해 더 읽어 보세요.
* **렌더 힌트(Render hints):** 같은 기본 타입의 대부분의 속성과 다르게 이 속성을 어떻게 표시할지를 사용자 애플리케이션에 알려 주는 표시입니다. 많은 렌더 힌트는 그 속성이 정의된 객체 타입의 재인덱싱 성능에 영향을 줄 수 있습니다. 예를 들어 사용자 애플리케이션에서 아무도 `start date` 속성으로 검색하거나 정렬하지 않을 것이라면, `searchable` 렌더 힌트와 `sortable` 렌더 힌트를 선택 해제해 `Employee` 객체 타입의 재인덱싱 성능을 높일 수 있습니다. [렌더 힌트](../09_metadata/02_metadata-render-hints.md)에 대해 더 읽어 보세요.
* **가시성(Visibility):** 사용자 애플리케이션에 이 속성을 얼마나 눈에 띄게 표시할지 알려 주는 표시입니다. `prominent` 속성은 애플리케이션이 사용자에게 가장 먼저 보여 줍니다. `hidden` 속성은 사용자 애플리케이션에 나타나지 않습니다. 기본적으로 `start date` 속성의 가시성은 `normal`입니다.

[온톨로지에서 속성을 만들고 설정하는 방법과 속성 메타데이터의 검증 요건에 대해 더 알아보세요.](../02_object-types/02_create-object-type.md)

**설명**: 식별자가 세 가지(ID, RID, API 이름) 있어 헷갈리기 쉽습니다. 예를 들어 `Employee` 객체 타입의 시작일 속성은 다음과 같은 값을 가질 수 있습니다.

| 항목 | 예시 값 | 주로 쓰이는 곳 |
|---|---|---|
| ID | `start-date` | 애플리케이션 설정 |
| RID | 플랫폼이 자동 생성하는 고유 문자열 | 플랫폼 오류 메시지 |
| API 이름 | `startDate` | 코드(함수, OSDK 등) |
| 표시 이름 | `Start date` | 사용자 화면 |

렌더 힌트의 `searchable`, `sortable`은 데이터베이스에서 열에 인덱스를 만들지 여부와 비슷한 선택입니다. 인덱스를 만들면 검색과 정렬이 빨라지지만 데이터를 적재할 때 인덱스를 함께 만들어야 하므로 적재(재인덱싱)가 느려집니다. 검색이나 정렬에 쓰지 않을 속성은 이 힌트를 끄면 재인덱싱 비용을 줄일 수 있습니다.

> **중간 요약**: 속성은 ID, 표시 이름, 설명, RID, 상태, API 이름, 키, 기본 타입, 값 서식, 조건부 서식, 타입 클래스, 렌더 힌트, 가시성이라는 메타데이터로 표현됩니다. 타이틀 키는 객체의 표시 이름, 기본 키는 객체의 고유 식별자 역할을 합니다.

<a id="property-base-types-with-limited-support"></a>
## 지원이 제한된 속성 기본 타입 (Property base types with limited support)

일부 속성 기본 타입은 지원이 제한됩니다. 이런 타입은 속성 기본 타입 선택기에서 `Limited support` 태그로 표시됩니다.

* `byte`:
  * 이 타입의 속성은 액션 타입에서 사용할 수 없습니다.
* `float`:
  * 이 타입의 속성은 액션 타입에서 사용할 수 없습니다.
* `short`:
  * 이 타입의 속성은 액션 타입에서 사용할 수 없습니다.
* `vector`:
  * 벡터는 [KNN(TSv1)](../../04_functions/13_functions-on-objects/07_api-object-sets.md#k-nearest-neighbors-knn)으로만 질의할 수 있습니다.
  * 벡터의 최대 차원은 2048입니다.

액션 타입에서 속성 기본 타입의 제한 사항에 대한 자세한 내용은 [지원되는 속성 타입에 관한 문서](../../03_action-types/17_scale-property-limits.md#supported-property-types)를 참고하세요.

**설명**: `byte`(8비트 정수), `short`(16비트 정수), `float`(32비트 부동소수점)는 더 넓은 범위의 타입인 `integer`, `long`, `double`보다 작은 자료형입니다. 액션에서 값을 써야 하는 속성이라면 이 작은 타입 대신 더 넓은 타입을 고르는 것이 안전합니다. `vector`는 `[0.12, -0.53, ...]`처럼 실수 여러 개를 담은 배열로, 주로 임베딩(텍스트나 이미지를 숫자 벡터로 바꾼 값)을 저장합니다. KNN(k-nearest neighbors, k-최근접 이웃) 질의는 주어진 벡터와 거리가 가장 가까운 k개의 객체를 찾는 검색입니다.

> **중간 요약**: `byte`, `float`, `short` 타입 속성은 액션 타입에서 쓸 수 없고, `vector` 타입은 KNN으로만 질의할 수 있으며 최대 2048차원입니다.

## 정리

- 속성은 ID, 표시 이름, 설명, RID, 상태, API 이름, 키, 기본 타입, 값 서식, 조건부 서식, 타입 클래스, 렌더 힌트, 가시성으로 설명됩니다.
- 타이틀 키는 객체의 표시 이름이 되고, 기본 키는 백킹 데이터소스의 각 행마다 값이 달라야 하는 고유 식별자입니다.
- 렌더 힌트를 조정하면 재인덱싱 성능을 높일 수 있습니다.
- `byte`, `float`, `short`, `vector`는 지원이 제한된 기본 타입이며 `Limited support` 태그로 표시됩니다.
