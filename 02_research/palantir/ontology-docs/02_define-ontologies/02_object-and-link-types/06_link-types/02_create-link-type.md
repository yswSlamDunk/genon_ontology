# 링크 타입 만들기 (Create a link type)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/create-link-type/
- 사이드바 위치: Define Ontologies > Object and link types > Link types > Create a link type

이 페이지는 Ontology Manager의 생성 도우미로 새 링크 타입을 만드는 전체 절차를 설명합니다. 관계 유형(외래 키, 조인 테이블 데이터셋, 백킹 객체)을 고르는 방법, 각 유형에서 링크 리소스를 지정하는 방법, 링크 타입 이름과 API 이름 규칙, 저장 방법을 다루고, 링크에 추가 정보를 담을 수 있는 객체 기반 링크(object-backed link)도 설명합니다. 관계형 데이터베이스의 외래 키와 조인 테이블 개념이 그대로 쓰이므로 이를 떠올리며 읽으면 좋습니다.

아래에 설명하는 안내형 도우미(guided helper)로 새 링크 타입을 만들고 설정하기를 권장합니다. 다만 생성 과정을 마치기 전에 도우미를 빠져나갔다면, 새 링크 타입의 링크 타입, 키, API 이름을 직접 지정해 수동으로 과정을 마칠 수 있습니다.

<a id="access-the-link-type-creation-helper"></a>
## 링크 타입 생성 도우미 열기

Ontology Manager로 이동합니다. 링크 타입 생성 도우미를 열려면 다음 방법 중 하나를 고릅니다.

* 오른쪽 위에서 **New**를 선택한 다음 **Link type**을 선택합니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-new-link-type.png" width=400 alt="New 드롭다운 메뉴에서 Link type 옵션 선택."> <br><br>

* 왼쪽 사이드바의 **Resources** 아래에서 **Link types**를 선택합니다. 그런 다음 **Link types** 페이지 오른쪽 위의 **New link type**을 선택합니다.

* 링크하려는 객체 타입으로 이동한 다음, 객체 타입 **Overview** 페이지의 링크 타입 그래프 안에서 **Create new link type**을 선택합니다. <br><br>
  ![새 링크 타입 만들기](https://www.palantir.com/docs/resources/foundry/object-link-types/create-new-link-type-button.png) <br><br>

<a id="configure-a-new-link-type"></a>
## 새 링크 타입 설정하기

새 링크 타입 도우미는 다음 단계를 안내합니다.

* [관계 유형 선택하기](#choose-the-relationship-type)
* [링크 리소스 정의하기](#define-link-resources)
  * [외래 키 관계 유형](#foreign-key-relationship-type)
  * [조인 테이블 데이터셋 관계 유형](#join-table-dataset-relationship-type)
  * [백킹 객체 관계 유형](#backing-object-relationship-type)
* [링크 타입 이름 정의하기](#define-link-type-names)
* [저장 위치](#save-location)
* [온톨로지에 변경 사항 저장하기](#save-change-to-ontology)

<a id="choose-the-relationship-type"></a>
### 관계 유형 선택하기

1. **Create a new link type** 대화 상자의 첫 단계에서 링크의 관계 유형을 선택합니다.
2. 두 객체 사이의 링크를 정의할 관계 유형을 고릅니다.

   * **Object type foreign keys(객체 타입 외래 키):** "일대일"과 "다대일" 카디널리티 링크 타입을 지원합니다. 원하는 객체들에 대해 외래 키를 나타내는 속성과 그에 대응하는 기본 키(primary key)를 선택할 수 있습니다. 외래 키로 링크 리소스를 정의하는 방법은 [아래 세부 내용](#foreign-key-relationship-type)을 참고하세요.
   * **Join table dataset(조인 테이블 데이터셋):** "다대다" 카디널리티 링크 타입용입니다. 조인 테이블 데이터셋으로 링크를 뒷받침할 수 있습니다. 데이터셋으로 링크 리소스를 정의하는 방법은 [아래 세부 내용](#join-table-dataset-relationship-type)을 참고하세요.
   * **Backing object type(백킹 객체 타입):** 객체 기반 링크 타입(object-backed link type)은 다대일 카디널리티 링크 타입을 확장한 것으로, 객체 타입을 링크 타입 저장 방식으로 정식 지원합니다. 객체가 뒷받침하는 링크 리소스를 정의하는 방법은 [아래 세부 내용](#backing-object-relationship-type)을 참고하세요. 추가 정보는 [객체 기반 링크](#object-backed-links) 섹션을 참고하세요.

아래 예시에서는 카디널리티로 서로 관계를 맺는 두 객체 타입, 즉 `Aircraft` 객체 타입과 `Flight` 객체 타입이 있다고 가정합니다. 카디널리티 유형은 다음과 같습니다.

* *일대일(One-to-one) 카디널리티:* `Aircraft` 하나가 `Flight` 하나에만 링크되어야 함을 나타냅니다. 일대일 카디널리티는 의도한 관계를 알려 주는 표시 역할을 할 뿐, 강제되지는 않습니다.
* *일대다(One-to-many) 카디널리티:* `Aircraft` 하나가 여러 `Flights`에 링크될 수 있음을 나타냅니다.
* *다대일(Many-to-one) 카디널리티:* 여러 `Aircraft`가 `Flight` 하나에 링크될 수 있음을 나타냅니다.
* *다대다(Many-to-many) 카디널리티:* `Aircraft` 하나가 여러 `Flights`에 링크될 수 있고, `Flight` 하나도 여러 `Aircraft`에 링크될 수 있음을 나타냅니다.

3. **Next**를 선택해 다음 단계로 진행합니다. <br><br>
   ![생성 대화 상자에서 링크 타입 관계 유형 선택](https://www.palantir.com/docs/resources/foundry/object-link-types/create-link-relationship-type.png) <br><br>

**설명**: 세 관계 유형은 관계형 데이터베이스에서 관계를 저장하는 방법에 각각 대응합니다. 외래 키 방식은 `flights` 테이블에 `tail_number` 열을 두는 방식, 조인 테이블 방식은 `(flight_id, tail_number)` 쌍만 담은 별도 테이블을 두는 방식, 백킹 객체 방식은 그 별도 테이블에 조종사 같은 추가 열까지 두고 그것 자체를 하나의 엔터티로 다루는 방식입니다. "일대일 카디널리티가 강제되지 않는다"는 것은, 데이터에 실제로 같은 항공기를 가리키는 항공편이 둘 있어도 오류가 나지 않는다는 뜻입니다.

> **중간 요약**: 링크 타입의 관계 유형은 외래 키(일대일, 다대일), 조인 테이블 데이터셋(다대다), 백킹 객체 타입(다대일 확장) 가운데 하나를 고릅니다.

<a id="define-link-resources"></a>
### 링크 리소스 정의하기

<a id="foreign-key-relationship-type"></a>
#### 외래 키 관계 유형

**외래 키(foreign key)는** 한 객체 타입에 있는 속성으로, 다른 객체 타입의 기본 키 값을 저장해 두 객체 타입 사이의 현실 세계 관계를 나타냅니다. 이 개념은 한 테이블의 열이 다른 테이블의 기본 키 열을 참조하는 관계형 데이터베이스의 외래 키에 대응합니다. 일대일 또는 다대일 카디널리티 링크 타입에서는 링크의 외래 키 속성과 기본 키 속성을 정의합니다. 한 객체 타입의 **외래 키** 속성은 다른 객체 타입의 **기본 키** 속성을 참조해야 합니다.

예를 들어 `Tail Number`(기체 등록 번호) 속성은 `Aircraft` 객체 타입의 기본 키로, 항공기 하나하나를 유일하게 식별합니다. `Flight` 객체 타입의 `Flight Tail Number` 속성은 외래 키로, 그 항공편에 배정된 항공기를 나타냅니다. `Aircraft`의 `Tail Number`가 `Flight`의 `Flight Tail Number`와 일치하면 `Aircraft`와 `Flight` 객체 타입 사이에 링크가 생성됩니다.

1. **Link resources** 단계에서 링크할 객체 타입들을 고릅니다.

2. 오른쪽 드롭다운 메뉴에서 기본 키 쪽 객체 타입을 선택합니다(예시에서는 `Aircraft`).

3. 왼쪽 드롭다운 메뉴에서 외래 키 쪽 객체 타입을 선택합니다(예시에서는 `Flight`). 다음 조건이 충족되면 생성 대화 상자가 외래 키를 감지해 자동으로 선택합니다.
   * 외래 키가 링크될 객체 타입의 기본 키와 일치합니다.
   * 두 객체의 속성 타입이 일치합니다.

4. 링크를 이룰 속성들을 고릅니다.
   * 외래 키 쪽 객체 타입에서는 원본 객체 타입의 외래 키로 쓸 속성을 선택합니다(`Flight` 객체 타입의 `Flight Tail Number`).
   * 객체 타입마다 기본 키는 하나뿐이므로 해당 객체 타입의 기본 키는 자동으로 선택됩니다(`Aircraft` 객체 타입의 `Tail Number`).

5. **Next**를 선택해 계속합니다. <br><br>
   ![외래 키 관계 유형으로 링크 리소스 선택](https://www.palantir.com/docs/resources/foundry/object-link-types/create-link-foreign-key.png) <br><br>

**설명**: 이 설정은 SQL로 `flights JOIN aircraft ON flights.flight_tail_number = aircraft.tail_number`라는 조인 조건을 정의하는 것과 같은 결과를 냅니다. 외래 키 값이 `N101`인 Flight 객체는 기본 키가 `N101`인 Aircraft 객체와 링크되고, 일치하는 Aircraft가 없으면 그 Flight에는 링크가 생기지 않습니다.

> **중간 요약**: 외래 키 유형에서는 한쪽 객체 타입의 외래 키 속성과 다른 쪽의 기본 키 속성을 짝지어, 값이 같은 객체끼리 링크되게 합니다.

<a id="join-table-dataset-relationship-type"></a>
#### 조인 테이블 데이터셋 관계 유형

다대다 카디널리티에서는 첫 번째 객체 타입(예시에서는 `Aircraft`)의 기본 키와 두 번째 객체 타입(예시에서는 `Flight`)의 기본 키 사이의 모든 링크 조합을 담은 데이터소스를 선택합니다.

사용자가 링크 타입을 [편집하거나 라이트백(writeback)](../07_allow-editing.md)할 수 있게 하려면, 백킹 데이터소스가 필요한 다대다 카디널리티가 필요합니다.

1. **Link resources** 단계에서 링크할 객체 타입들을 고릅니다.
2. 왼쪽 드롭다운 메뉴에서 첫 번째 객체 타입(`Flight`)을 선택합니다.
3. 오른쪽 드롭다운 메뉴에서 두 번째 객체 타입(`Aircraft`)을 선택합니다.
4. 조인 테이블 데이터셋을 고릅니다. 선택한 두 객체 타입의 기본 키에 대응하는 열을 포함한 데이터셋을 선택합니다. 한 열은 기본 키 하나에만 매핑할 수 있습니다.
   * 이제 새 링크 타입에 대해 조인 테이블을 자동으로 생성할 수 있습니다. **Generate join table** 옵션은 선택한 두 객체 타입의 기본 키를 바탕으로 올바른 스키마를 가진 데이터셋을 만듭니다. 덕분에 사용자 편집으로 채워지는 데이터를 쓰거나, 운영 데이터를 나중에 제공하려는 경우 더 빨리 시작할 수 있습니다.
5. 링크 타입의 백킹 데이터소스에서 어떤 열이 링크되는 각 객체 타입의 기본 키에 매핑되는지 선택합니다.
6. **Next**를 선택해 계속합니다. <br><br>
   ![링크 타입 관계 유형 선택](https://www.palantir.com/docs/resources/foundry/object-link-types/create-link-dataset.png) <br><br>

**설명**: 조인 테이블은 예를 들어 다음과 같은 데이터셋입니다.

| flight_id | tail_number |
|---|---|
| F100 | N101 |
| F100 | N202 |
| F101 | N101 |

각 행이 링크 하나입니다. F100은 두 항공기에, N101은 두 항공편에 연결되어 다대다 관계가 됩니다. 사용자가 링크를 추가하거나 지우는 편집은 결국 이런 행을 추가하거나 지우는 일이므로, 편집 가능한 링크 타입에는 이런 백킹 데이터소스가 필요합니다.

> **중간 요약**: 다대다 관계는 두 기본 키의 조합을 담은 조인 테이블 데이터셋으로 뒷받침하며, **Generate join table**로 빈 조인 테이블을 자동 생성할 수도 있습니다. 사용자 편집을 허용하려면 이 방식이 필요합니다.

<a id="backing-object-relationship-type"></a>
#### 백킹 객체 관계 유형

객체 기반 링크를 만들기 전에 [사전 준비](#prerequisites-for-creating-an-object-backed-link-type)에 필요한 객체와 링크가 만들어져 있는지 확인합니다.

1. 원하는 링크 타입을 나타내도록 사전 준비 단계에서 만든 객체 타입들을 선택합니다. 왼쪽과 오른쪽 객체는 서로 링크될 두 엔터티를 나타냅니다. 가운데 객체는 중개자 역할을 하며 두 엔터티 사이의 연결에 대한 추가 메타데이터를 제공하고 링크를 뒷받침합니다.
2. 왼쪽, 오른쪽 객체와 가운데 중개 객체 사이에 링크가 여러 개 있다면, 드롭다운 메뉴로 왼쪽, 오른쪽 객체와 중개 객체 사이에 쓸 링크를 선택합니다. <br><br>
   ![객체 기반 링크로 링크 리소스 선택](https://www.palantir.com/docs/resources/foundry/object-link-types/oblt-link-dialog.png) <br><br>

<a id="define-link-type-names"></a>
### 링크 타입 이름 정의하기

1. **Link type names** 단계에서 새 링크 타입의 표시 이름과 API 이름을 입력합니다.
2. 링크 타입의 각 면에 대한 표시 이름을 입력합니다. 링크 타입은 관계를 맺는 두 객체 타입 각각에 하나씩, 정확히 두 개의 면을 가지며, 각 면은 그 객체 타입*으로 가는* 링크를 나타냅니다. 예시에서 `Aircraft` 객체 타입의 표시 이름은 `Flight`에서 `Aircraft`*로 가는* 링크를 설명합니다. `Flight` 하나에는 `Assigned Aircraft` 하나가 있으므로 표시 이름을 `Assigned Aircraft`로 정할 수 있습니다. 같은 링크 타입에 대해 두 면을 함께 설정하므로 링크 타입은 어느 방향으로든 탐색할 수 있으며, 반대 방향을 위한 별도의 링크 타입을 정의할 필요가 없습니다. 자세한 내용은 [방향성](01_link-types-overview.md#directionality)을 참고하세요.
3. API 이름은 표시 이름을 바탕으로 자동 생성되지만 필요하면 수정할 수 있습니다.
   * API 이름 필드는 코드에서 프로그래밍 방식으로 링크 타입을 참조할 때 사용됩니다. 링크 타입 한 면의 API 이름으로 그 타입의 객체를 반환받을 수 있습니다. 예를 들어 링크 타입의 `Aircraft` 면 API 이름이 `assignedAircraft`라면 `Flight.assignedAircraft.get()`을 호출했을 때 해당 `Flight` 객체들에 링크된 `Aircraft` 객체가 반환됩니다.
   * 링크 타입 API 이름은 다음을 *반드시* 지켜야 합니다.
     * 소문자로 시작하고 영문자와 숫자로만 구성됩니다.
     * 같은 객체 타입에 연결된 모든 링크 타입 사이에서 고유합니다.
     * 길이가 1자 이상 100자 이하입니다.
     * NFKC 정규화되어 있습니다.
     * 예약어가 아닙니다.
   * [API 이름(TSv1)에 대해 더 알아보세요.](../../04_functions/13_functions-on-objects/06_api-objects-links.md)
4. **Next**를 선택해 진행합니다. <br><br>
   ![링크 타입 이름 지정](https://www.palantir.com/docs/resources/foundry/object-link-types/create-link-api.png) <br><br>

**설명**: 면의 이름은 "그 면에 도착했을 때 무엇을 얻는가"를 기준으로 짓습니다. `Flight` 객체에서 출발해 `Aircraft` 면으로 가면 배정된 항공기를 얻으므로 그 면의 이름이 `Assigned Aircraft`(API 이름 `assignedAircraft`)이고, 반대로 `Aircraft`에서 `Flight` 면으로 가면 항공편 목록을 얻으므로 `Flights`(API 이름 `flights`) 같은 이름이 어울립니다. NFKC 정규화는 겉보기에 같은 유니코드 문자열을 하나의 표준 형태로 맞추는 규칙으로, 같은 이름이 서로 다른 바이트 열로 저장되는 문제를 막습니다.

> **중간 요약**: 링크 타입의 두 면에 각각 표시 이름과 API 이름을 붙입니다. API 이름은 소문자로 시작하는 영숫자, 같은 객체 타입 안에서 고유, 1\~100자, NFKC 정규화, 예약어 아님이라는 규칙을 지켜야 합니다.

<a id="save-location"></a>
### 저장 위치

마지막 단계에서 이 링크 타입을 저장할 프로젝트를 고른 다음 **Submit**을 선택합니다. 이 단계를 마치면 새 링크 타입이 만들어지지만, 아직 저장되지는 않은 상태입니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-link-type-save-location-step.png" alt="새 링크 타입의 Save location 단계." width="500" />

<a id="save-change-to-ontology"></a>
### 온톨로지에 변경 사항 저장하기

Ontology Manager로 돌아와 오른쪽 위의 **Save**를 선택해 [온톨로지에 변경 사항을 반영](../../../05_applications/04_ontology-manager/06_change-management/01_save-changes.md)합니다.

> **중간 요약**: 도우미에서 **Submit**하면 링크 타입이 만들어질 뿐이고, Ontology Manager에서 **Save**를 눌러야 온톨로지에 실제로 저장됩니다.

<a id="object-backed-links"></a>
## 객체 기반 링크 (Object-backed links)

객체 기반 링크 타입은 다대일 카디널리티 링크 타입을 확장한 것으로, 객체 타입을 링크 타입 저장 방식으로 정식 지원합니다. 객체 기반 링크 타입을 쓰면 링크에 추가 메타데이터를 담을 수 있고, 제한된 뷰(restricted view)를 지원합니다.

객체 기반 링크의 예로, `Aircraft`와 `Flight` 객체에 더해 `Flight Manifest`(운항 기록부)라는 객체 타입이 하나 더 있다고 가정합니다. 객체 기반 링크를 쓰면 `Aircraft`와 `Flight` 객체를 링크하는 `Flight Manifest` 객체 타입을 둘 수 있습니다. 외래 키 기반이나 데이터셋 기반 링크와 달리, 이 `Flight Manifest` 객체는 `Pilot`(기장), `First Mate`(부기장) 같은 추가 속성을 담아 링크에 대한 추가 메타데이터를 제공할 수 있습니다.

![객체 기반 링크 개요.](https://www.palantir.com/docs/resources/foundry/object-link-types/oblt_overview.png)

**설명**: 구조로 보면 `Flight Manifest`는 `Flight`와 `Aircraft` 각각에 다대일로 링크된 중간 객체 타입입니다. 예를 들어 Flight Manifest 객체 `M1`이 `{flight: F100, aircraft: N101, Pilot: Lee, First Mate: Park}`이라면, F100과 N101 사이의 링크 하나가 `M1`에 의해 표현되고, 그 링크를 선택하면 Pilot과 First Mate 같은 정보도 함께 볼 수 있습니다. 데이터베이스에서 조인 테이블에 관계 자체의 속성 열을 추가한 것에 해당합니다.

<a id="prerequisites-for-creating-an-object-backed-link-type"></a>
### 객체 기반 링크 타입을 만들기 위한 사전 준비

객체 기반 링크 타입을 만들기 전에 먼저 다음을 해야 합니다.

1. 링크 타입 양쪽에 놓일 객체 타입을 만듭니다. 자세한 내용은 [객체 타입 만들기](../02_object-types/02_create-object-type.md)를 참고하세요.
2. 두 객체 타입을 서로 링크하는 백킹 객체 타입을 만듭니다.
3. 링크 타입의 각 면에서 백킹 객체 타입으로 가는 다대일 링크 타입을 만듭니다. 자세한 내용은 [새 링크 타입 설정하기](#configure-a-new-link-type)를 참고하세요.

위의 `Aircraft`, `Flight`, `Flight Manifest` 예에서는 다음 리소스를 만들어야 합니다.

1. 링크 타입 양쪽에 놓일 객체 타입을 만듭니다.
   1. `Aircraft` 객체 타입
   2. `Flight` 객체 타입
2. 두 객체 타입을 서로 링크하는 백킹 객체 타입을 만듭니다.
   1. `Flight Manifest` 객체 타입
3. 링크 타입의 각 면에서 백킹 객체 타입으로 가는 다대일 링크 타입을 만듭니다.
   1. `Aircraft` 객체 타입과 `Flight Manifest` 객체 타입 사이의 링크
   2. `Flight` 객체 타입과 `Flight Manifest` 객체 타입 사이의 링크

이것들을 만들고 나면 객체 기반 링크 타입을 만들 수 있습니다.

<a id="convert-existing-links-to-object-backed-link-types"></a>
### 기존 링크를 객체 기반 링크 타입으로 변환하기

기존 링크를 객체 기반 링크 타입으로 변환할 수 있습니다. 기존 링크를 수정하기 전에 객체 기반 링크 타입의 [사전 준비](#prerequisites-for-creating-an-object-backed-link-type)를 충족해야 합니다.

기존 링크의 링크 타입을 수정하려면 다음과 같이 합니다.

1. Ontology Manager에서 링크를 엽니다.
2. **Configuration** 섹션에서 조인 방식(join method)을 변경해 **Object type**을 선택합니다.
3. **Update link type to object-backed link type** 대화 상자에서 백킹 객체 타입을 선택합니다.
4. **Update link type to object-backed link type** 대화 상자에서 백킹 객체로 가는 링크 간선(link edge)들의 링크 타입을 선택합니다.
5. **Update to object-backed**를 선택합니다.

<a id="use-object-backed-link-types"></a>
### 객체 기반 링크 타입 사용하기

현재 객체 기반 링크 타입은 Object Explorer, Vertex, Workshop에서 볼 수 있습니다. 링크를 선택하면 링크의 백킹 객체 속성을 볼 수 있습니다. Vertex에서는 링크 제목 대신 링크의 백킹 객체 제목이 표시됩니다.

> **중간 요약**: 객체 기반 링크는 중간 객체 타입이 두 객체 사이의 링크를 뒷받침하게 해서, 링크 자체에 추가 속성을 담습니다. 양쪽 객체 타입, 중간 객체 타입, 그리고 중간 객체로 가는 다대일 링크 두 개를 먼저 만들어야 하며, 기존 링크도 변환할 수 있습니다.

<a id="troubleshooting"></a>
## 문제 해결 (Troubleshooting)

<a id="error-phonograph2datasetandbranchalreadyregistered"></a>
### 오류: `Phonograph2:DatasetAndBranchAlreadyRegistered`

`Phonograph2:DatasetAndBranchAlreadyRegistered` 오류가 나타나면, 저장하려는 링크 타입을 뒷받침하는 데이터소스가 이미 온톨로지의 다른 링크 타입을 뒷받침하고 있어서 다시 사용할 수 없다는 뜻입니다.

## 정리

- 링크 타입은 Ontology Manager의 생성 도우미로 만들며, 관계 유형 선택, 링크 리소스 정의, 이름 정의, 저장 위치 선택, **Save** 순서로 진행합니다.
- 외래 키 유형은 일대일과 다대일, 조인 테이블 데이터셋 유형은 다대다, 백킹 객체 유형은 링크에 추가 메타데이터가 필요할 때 씁니다.
- 사용자가 링크를 편집하거나 라이트백하려면 백킹 데이터소스가 있는 다대다 방식이 필요합니다.
- 링크 타입의 두 면에는 각각 표시 이름과 규칙을 지킨 API 이름을 붙입니다.
- 한 데이터소스는 링크 타입 하나만 뒷받침할 수 있으며, 이를 어기면 `DatasetAndBranchAlreadyRegistered` 오류가 납니다.
