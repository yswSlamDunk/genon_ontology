# 객체 타입 만들기 (Create an object type)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/create-object-type/
- 사이드바 위치: Define Ontologies > Object and link types > Object types > Create an object type

이 페이지는 Ontology Manager에서 새 객체 타입(object type)을 만드는 방법을 처음부터 끝까지 안내합니다. 단계별 도우미(helper)를 쓰는 권장 방법, 도우미를 중간에 빠져나온 뒤 수작업으로 마무리하는 방법, 데이터소스 없이 액션만으로 채우는 객체 타입을 만드는 방법을 다룹니다. 마지막으로 API 이름 규칙과 저장할 때 자주 만나는 오류를 정리합니다. 객체 타입은 온톨로지의 가장 기본 단위이므로, 이 페이지의 절차가 이후 거의 모든 작업의 출발점이 됩니다.

새 객체 타입을 만들고 구성하는 기본 방법은 [**단계별 안내 도우미(guided step-by-step helper)**](#create-a-new-object-type-with-the-helper)를 사용하는 것입니다. 안내 도우미가 권장 방법이지만, 객체 생성 과정을 마치기 전에 도우미를 빠져나왔다면 새 객체 타입의 메타데이터, 백킹 데이터소스(backing datasource), 속성(property) 매핑, 키(기본 키와 타이틀 키)를 직접 지정해 [**수작업으로**](#create-a-new-object-type-manually) 과정을 마무리할 수도 있습니다. 모든 속성을 [액션](../../03_action-types/01_overview.md)으로 채울 계획이라면 [백킹 데이터소스 없이 객체 타입을 만들](#create-an-object-type-without-a-backing-datasource) 수도 있습니다.

새 객체 타입을 만든 뒤에는 기본으로 지정된 [API 이름을 바꿀](#configure-api-names) 수 있습니다.

이 페이지에는 새 객체 타입 생성 과정에 대한 [문제 해결](#troubleshooting) 정보도 들어 있습니다.

프로그래밍 방식으로 객체 타입을 만들고 싶다면 [SuperRepo](https://www.palantir.com/docs/foundry/superrepo/overview/)를 사용하세요. SuperRepo는 [Ontology-as-code](https://www.palantir.com/docs/foundry/superrepo/core-concepts/#ontology-as-code) 방식으로 코드에서 객체 타입을 정의하며, Ontology Manager에서 만든 객체 타입을 SuperRepo로 [가져올(import)](https://www.palantir.com/docs/foundry/superrepo/core-concepts/#importing) 수도 있습니다.

**설명**: 백킹 데이터소스는 객체 타입의 속성 값을 공급하는 원본 데이터(보통 Foundry 데이터셋)입니다. 데이터셋의 각 행이 객체 하나가 되고, 각 열이 속성 하나에 매핑됩니다. "Ontology-as-code"는 객체 타입 정의를 화면에서 클릭으로 만드는 대신 소스 코드 파일로 작성하고 버전 관리하는 방식을 뜻합니다. 데이터베이스에서 GUI 도구로 테이블을 만드는 대신 `CREATE TABLE` 문을 마이그레이션 파일로 관리하는 것과 같은 차이입니다.

<a id="create-a-new-object-type-with-the-helper"></a>
## 도우미로 새 객체 타입 만들기 (Create a new object type with the helper)

* [새 객체 타입 만들기](#create-a-new-object-type)
* [백킹 데이터소스 선택하기](#choosing-a-backing-datasource)
* [백킹 데이터소스 없이 객체 타입 만들기](#create-an-object-type-without-a-backing-datasource)
* [객체 타입 메타데이터](#object-type-metadata)
* [객체 타입의 속성 만들기](#create-properties-for-the-object-type)
* [기본 키와 타이틀 키 구성하기](#configure-the-primary-key-and-title-key)
* [액션 생성하기](#generate-actions)
* [저장 위치](#save-location)
* [보안 정책 구성하기](#configure-security-policies)
* [온톨로지에 변경 사항 저장하기](#save-change-to-ontology)

<a id="create-a-new-object-type"></a>
### 새 객체 타입 만들기 (Create a new object type)

새 객체 타입을 만들려면 Ontology Manager 홈 페이지에서 **Create your first object type** 옵션을 선택하거나, 같은 페이지 오른쪽 위에 있는 **New > Create object type**을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-new-object-type.png" alt="New 드롭다운 메뉴에서 object type을 선택합니다." width="300" />

**Create new object type** 도우미가 나타납니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-datasource-step.png" alt="새 객체 타입의 데이터소스 단계." width="500" />

<a id="choosing-a-backing-datasource"></a>
### 백킹 데이터소스 선택하기 (Choosing a backing datasource)

Foundry에 객체 타입을 뒷받침할 데이터가 담긴 기존 데이터소스가 있다면 그것을 선택할 수 있습니다. 그러면 객체 타입의 메타데이터가 자동으로 채워집니다. 또한 백킹 데이터소스의 모든 열이 각각 속성 하나로 매핑되는데, 추가된 속성은 **Properties** 단계에서 버릴 수 있습니다.

**주의**: 객체 타입의 백킹 데이터소스에는 `MapType`이나 `StructType` 열이 있으면 안 됩니다.

객체 타입의 데이터가 담긴 기존 데이터소스가 없다면, 기존 데이터소스 없이 계속 진행하도록 선택하고 권한 관리용 데이터셋을 생성할 위치를 고를 수 있습니다. 이 옵션은 Object Storage v1을 사용하는 경우에는 사용할 수 없습니다. 데이터소스 기반 타입의 객체 권한은 백킹 데이터소스가 있는 위치에 따라 결정되기 때문에, 빈 데이터셋을 저장할 위치를 고르라는 안내가 나옵니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-choose-new-datasource-location.png" alt="새 객체 타입의 데이터소스 위치" width="500" />

**설명**: `MapType`은 키와 값의 쌍을 담는 열 타입(예: `{"color": "red", "size": "L"}`)이고, `StructType`은 여러 하위 필드를 묶은 중첩 열 타입(예: `address` 열 안에 `city`, `zip`이 들어 있는 형태)입니다. Spark 같은 데이터 처리 엔진에서 쓰는 복합 타입으로, 객체 타입의 백킹 데이터소스로는 쓸 수 없으니 미리 평평한 열로 풀어 두어야 합니다. 또한 Foundry에서는 "누가 이 객체를 볼 수 있는가"가 백킹 데이터셋이 저장된 프로젝트 폴더의 권한을 따라가므로, 데이터가 없더라도 권한 기준점으로 쓸 빈 데이터셋을 만들어 두는 것입니다.

<a id="create-an-object-type-without-a-backing-datasource"></a>
### 백킹 데이터소스 없이 객체 타입 만들기 (Create an object type without a backing datasource)

모든 속성을 액션으로 채울 계획이라면, 빈 백킹 데이터셋을 생성하지 않고도 객체 타입을 만들 수 있습니다.

**Datasource** 단계에서 백킹 데이터소스 없이 계속하도록 선택합니다. 이때 도우미는 다음을 요구합니다.

* 객체 타입이 [프로젝트 기반 권한 모델](../../../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)을 사용하도록 프로젝트 안에 저장해야 합니다.
* 액션으로 만들어진 객체를 누가 볼 수 있는지 결정하는 [객체 보안 정책(object security policy)](../../../06_ontology-architecture/02_object-permissioning/07_object-security-policies.md)을 구성해야 합니다.

나머지 도우미 단계는 아래 설명대로 진행합니다. 모든 객체 타입에는 여전히 기본 키(primary key)가 필요하며, 액션으로 만들어지는 각 객체는 고유한 기본 키 값을 가져야 합니다.

**설명**: 이런 객체 타입은 처음에 행이 0개인 테이블로 시작해서, 사용자가 액션(예: "새 정비 요청 등록" 버튼)을 실행할 때마다 `INSERT`처럼 객체가 하나씩 추가되는 구조입니다. 데이터셋 폴더 권한을 빌려 올 수 없으므로 보안 정책을 직접 지정해야 합니다.

<a id="object-type-metadata"></a>
### 객체 타입 메타데이터 (Object type metadata)

이 단계에서는 새 객체 타입에 대한 다음 정보를 입력합니다.

* **Icon(아이콘):** 기본 아이콘을 선택해 객체 타입의 아이콘과 색상을 바꿉니다. 이 아이콘과 색상은 사용자가 사용자 애플리케이션에서 이 타입의 객체를 볼 때 표시됩니다.
* **Name(이름):** 사용자 애플리케이션에서 이 타입의 객체 하나에 접근하는 모든 사람에게 보이는 이름입니다.
* **Plural name(복수형 이름):** 사용자 애플리케이션에서 이 타입의 객체 여러 개에 접근하는 모든 사람에게 보이는 이름입니다.
* **Description(설명):** 사용자 애플리케이션에서 이 타입의 객체에 접근하는 모든 사람을 위한 설명 문구입니다. 예를 들어 Object Explorer에서 검색하는 사용자는 검색 결과에서 객체 타입의 설명을 보게 됩니다.
* **Groups(그룹):** 이 객체 타입을 어떤 그룹에 포함할지 선택합니다. 그룹은 온톨로지를 정리하는 수단으로, 나중에 작업할 객체 타입을 필터링하기 쉽게 해 줍니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-metadata-step.png" alt="새 객체 타입의 메타데이터 단계." width="500" />

<a id="create-properties-for-the-object-type"></a>
### 객체 타입의 속성 만들기 (Create properties for the object type)

대화 상자의 세 번째 단계에서는 객체 타입이 가질 속성을 정할 수 있습니다. 기존 Foundry 데이터소스를 골랐다면 모든 열이 자동으로 매핑되지만, 이 단계에서 버릴 수 있습니다.

모든 객체 타입에는 속성이 최소 하나 있어야 합니다. 객체 타입은 객체를 유일하게 식별할 기본 키가 필요하기 때문입니다. 마법사(wizard)에서 원하는 다른 속성도 추가할 수 있습니다.

미디어(media)처럼 고급 구성이 필요한 속성 타입은 초기 설정 마법사 안에서 생성할 수 없으므로, 마법사를 빠져나온 뒤에 추가해야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-properties-step.png" alt="새 객체 타입의 속성 단계" width="500" />

<a id="configure-the-primary-key-and-title-key"></a>
### 기본 키와 타이틀 키 구성하기 (Configure the primary key and title key)

**Properties** 단계에서 기본 키와 타이틀 키를 골라야 합니다.

* **타이틀 키(title key):** 이 타입 객체의 표시 이름 역할을 하는 속성입니다.
  * 예를 들어 `Employee` 객체 타입의 타이틀 키로 `full name` 속성을 선택하면, 그 속성의 값인 "Melissa Chang", "Akriti Patel", "Diego Rodriguez" 등이 각 가상의 `Employee` 객체의 표시 이름으로 쓰입니다.
* **기본 키(primary key):** 객체 타입의 각 인스턴스를 유일하게 식별하는 속성입니다. 모든 객체는 이 속성에 대해 고유한 값을 가져야 합니다. 데이터소스 기반 객체 타입에서는 백킹 데이터소스의 각 행이 서로 다른 값을 가져야 합니다.
  * 예를 들어 `employee ID` 속성의 값은 "Melissa Chang"을 조직 안의 유일한 직원으로 식별하는 데 쓰입니다.

지원되는 속성 타입 목록은 [객체 타입 속성 문서](../03_properties/01_properties-overview.md#supported-property-types)에서 볼 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-configure-keys-helper.png" alt="새 객체 타입" width="500" />

**경고**: 기본 키를 지정하기 전에 반드시 백킹 데이터소스에 중복이 있는지 확인하세요. 선택한 기본 키는 데이터소스의 모든 레코드에서 고유해야 합니다. 온톨로지가 [Object Storage v2](../../../06_ontology-architecture/01_overview-and-getting-started/01_overview.md)를 사용한다면, 기본 키가 중복되면 [Funnel 배치 파이프라인](../../../06_ontology-architecture/03_indexing/02_funnel-batch-pipelines.md) 오류가 발생해 빌드가 실패합니다. Object Storage v1(Phonograph)을 사용한다면 업데이트는 성공한 것으로 보이지만, 중복된 기본 키 때문에 온톨로지에 예기치 않은 변경이 생길 수 있습니다.

기본 키는 고유할 뿐 아니라 결정적(deterministic)이어야 합니다. 기본 키가 비결정적이어서 빌드할 때마다 바뀌면 편집(edit)이 사라지고 링크가 없어질 수 있습니다. 온톨로지 편집은 객체의 기본 키에 연결되어 있기 때문에 편집이 사라질 수 있고, 링크 ID를 갱신하도록 빌드가 조율되지 않으면 객체 사이의 링크가 사라질 수 있습니다. 기본 키를 결정적으로 만들려면, 기본 키가 하나의 열 또는 여러 열의 함수가 되도록 파이프라인 로직을 정의해야 합니다. 행 번호 매기기나 무작위 키 생성은 빌드 실행마다 기본 키가 바뀔 수 있으므로 피하세요.

**설명**: 관계형 데이터베이스의 기본 키와 같은 개념입니다. 다음 Employee 데이터를 예로 들어 보겠습니다.

| employee_id | full_name | department |
|---|---|---|
| E001 | Melissa Chang | Sales |
| E002 | Akriti Patel | Finance |
| E003 | Diego Rodriguez | Sales |

여기서 `employee_id`가 기본 키, `full_name`이 타이틀 키로 적합합니다. 타이틀 키는 화면에 보여 줄 이름일 뿐이라 중복되어도 되지만(동명이인), 기본 키는 절대 중복되면 안 됩니다. "결정적"이라는 말은 같은 입력 데이터로 파이프라인을 다시 돌리면 항상 같은 키가 나와야 한다는 뜻입니다. 예를 들어 `row_number()`로 키를 만들면 원본 데이터의 정렬 순서가 바뀔 때 Melissa Chang의 키가 1에서 2로 바뀔 수 있습니다. 그러면 "1번 객체에 사용자가 남긴 편집"이 엉뚱한 직원에게 붙게 됩니다. 반면 `employee_id` 열 값을 그대로 쓰거나 `concat(country, '-', employee_number)`처럼 열 값으로 계산한 키는 매번 같은 결과를 냅니다.

<a id="generate-actions"></a>
### 액션 생성하기 (Generate actions)

선택적으로, 이 타입의 객체를 편집하는 표준 액션 묶음을 생성하고 그 액션을 실행할 수 있는 특정 사용자나 그룹을 지정할 수 있습니다.

객체 타입을 확정하고 도우미를 빠져나온 뒤에도 이 액션들을 편집하거나 새 액션을 추가로 만들 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-actions-step.png" alt="새 객체 타입의 Actions 단계" width="500" />

이 단계는 Object Storage v1을 사용하는 경우에는 사용할 수 없습니다.

<a id="save-location"></a>
### 저장 위치 (Save location)

이 객체 타입을 저장할 프로젝트를 고릅니다. 그런 다음 **Create**를 선택합니다. **Create**를 선택하면 변경 사항이 스테이징(staging)만 될 뿐 **저장되지는 않습니다**.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-save-location-step.png" alt="새 객체 타입의 저장 위치 단계." width="500" />

**설명**: 스테이징은 변경 사항을 임시로 모아 둔 상태입니다. Git에서 `git add`만 하고 아직 `git commit`하지 않은 상태처럼, 화면에는 반영되어 보이지만 온톨로지에는 아직 기록되지 않았습니다. 아래 "온톨로지에 변경 사항 저장하기" 단계에서 **Save**를 눌러야 실제로 저장됩니다.

<a id="configure-security-policies"></a>
### 보안 정책 구성하기 (Configure security policies)

이 단계는 [백킹 데이터소스 없이](#create-an-object-type-without-a-backing-datasource) 객체 타입을 만드는 경우에만 필요합니다. 데이터소스 기반 타입의 객체는 백킹 데이터소스가 있는 위치에서 권한을 상속하므로 정책을 구성할 필요가 없습니다.

이 타입의 객체를 누가 볼 수 있는지 결정하는 [객체 보안 정책](../../../06_ontology-architecture/02_object-permissioning/07_object-security-policies.md)을 구성합니다. 기대한 대로 접근 권한을 부여하는 정책을 설정하고 [테스트](../../../06_ontology-architecture/02_object-permissioning/07_object-security-policies.md#test-object-security-policies)하는 방법은 [객체 및 속성 보안 정책 구성 문서](../../../06_ontology-architecture/02_object-permissioning/07_object-security-policies.md#configure-object-and-property-security-policies)를 참고하세요.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-security-policies-step.png" alt="새 객체 타입의 Security policies 단계." width="500" />

<a id="save-change-to-ontology"></a>
### 온톨로지에 변경 사항 저장하기 (Save change to ontology)

Ontology Manager로 돌아와 오른쪽 위의 **Save**를 선택해 [온톨로지에 변경 사항을 반영합니다](../../../05_applications/04_ontology-manager/06_change-management/01_save-changes.md).

> **중간 요약**: 도우미는 데이터소스 선택, 메타데이터 입력, 속성 구성, 기본 키와 타이틀 키 지정, 액션 생성, 저장 위치 선택, (데이터소스가 없을 때) 보안 정책 구성의 순서로 진행됩니다. 기본 키는 고유하고 결정적이어야 하며, **Create**는 스테이징일 뿐이고 **Save**를 눌러야 실제로 저장됩니다.

<a id="create-a-new-object-type-manually"></a>
## 수작업으로 새 객체 타입 만들기 (Create a new object type manually)

도우미로 새 객체 타입을 만들 때, 위의 [**Create a new object type** 도우미 안내](#create-a-new-object-type-with-the-helper)의 모든 단계를 마치기 전에 **Create**를 선택할 수도 있습니다. 과정이 끝나기 전에 **Create**를 선택하면 도우미를 빠져나와 **Overview** 페이지로 이동합니다.

이 시점의 객체 타입은 저장되지 않은 상태이며, 아래 단계를 모두 마치기 전에는 저장할 수 없습니다. (**Create a new object type** 도우미 밖에서) 수작업으로 생성 과정을 마무리하는 단계는 다음과 같습니다.

* [새 객체 타입에 메타데이터 추가하기](#add-metadata-for-a-new-object-type)
* [새 객체 타입에 백킹 데이터소스 추가하기](#add-a-backing-datasource-to-a-new-object-type)
* [새 속성 추가하기](#add-a-new-property)
* [속성 하나를 데이터에 매핑하기](#map-a-single-property-to-data)
* [매핑되지 않은 모든 열을 새 속성으로 매핑하기](#map-all-unmapped-columns-as-new-properties)
* [기본 키와 타이틀 키 구성하기](#configure-the-primary-key-and-title-key)

<a id="add-metadata-for-a-new-object-type"></a>
### 새 객체 타입에 메타데이터 추가하기 (Add metadata for a new object type)

**Overview** 페이지의 메타데이터 영역에서 객체 타입의 표시 이름, 복수형 표시 이름, 설명, ID를 편집할 수 있습니다.

1. **Display name(표시 이름):** 사용자 애플리케이션에서 이 타입의 객체 하나에 접근하는 모든 사람에게 보이는 이름입니다.
2. **Plural display name(복수형 표시 이름):** 사용자 애플리케이션에서 이 타입의 객체 여러 개에 접근하는 모든 사람에게 보이는 이름입니다.
3. **Aliases(별칭):** 사용자가 검색할 때 이 객체 타입을 찾아 주는 추가 용어입니다.
4. **Description(설명):** 사용자 애플리케이션에서 이 타입의 객체에 접근하는 모든 사람을 위한 설명 문구입니다. 예를 들어 Object Explorer에서 검색하는 사용자는 검색 결과에서 객체 타입의 설명을 보게 됩니다.
5. **Groups(그룹):** 객체 타입을 분류하는 데 도움이 되는 하나 이상의 레이블입니다.
6. **ID:** 객체 타입의 고유 식별자로, 주로 사용자 애플리케이션을 구성할 때 이 타입의 객체를 참조하는 데 쓰입니다.
   * ID에는 소문자, 숫자, 대시(-)를 쓸 수 있습니다.
   * ID의 첫 글자는 **반드시** 소문자여야 합니다.
   * 속성의 ID가 저장되고 그 속성이 사용자 애플리케이션에서 참조되고 나면, 속성 ID를 **조금이라도** 바꾸면 애플리케이션이 깨집니다.
7. **Icon(아이콘):** 객체 타입 보기의 사이드바에서 기본 아이콘을 선택해 객체 타입의 아이콘과 색상을 바꿉니다. 이 아이콘과 색상은 사용자가 사용자 애플리케이션에서 이 타입의 객체를 볼 때 표시됩니다.
8. **Backing datasource(백킹 데이터소스):** 이 타입 객체의 속성 값으로 쓰이는 데이터의 원천입니다. 백킹 데이터소스 없이 만든 객체 타입은 이 필드에 값이 표시되지 않습니다.

![Overview 페이지](https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-new-object-overview-page-annotated.png)

***

<a id="add-a-group-to-an-object-type"></a>
### 객체 타입에 그룹 추가하기 (Add a group to an object type)

[그룹(Groups)](../10_type-groups.md)은 객체 타입을 분류하는 데 도움이 되는 레이블입니다. 객체 타입 메타데이터 위젯에서 다음을 할 수 있습니다.

* 기존 그룹 목록에서 그룹을 추가합니다.
* 그룹 이름을 입력해 새 그룹을 만듭니다.
* 객체 타입에서 그룹을 제거합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/object-type-groups-create.png" alt="객체 타입 그룹을 고르거나 새로 추가합니다" width="450" />

그룹은 [Ontology Manager의 **Search** 바와 **Search** 바 대화 상자](../../../05_applications/04_ontology-manager/02_navigation.md#header-search-bar)에서 검색할 수 있습니다. Ontology Manager의 객체 타입 표는 그룹 표시와 그룹별 필터링을 지원합니다. 그룹은 [Object Explorer 홈 페이지](../../../05_applications/01_object-explorer/02_getting-started.md#group-exploration-b-c-d)에도 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/object-type-groups-add.png" alt="새 객체 타입 그룹 추가" width="300" />

**주의**: 객체 타입 메타데이터의 레이블로서의 그룹은, 기본 키 속성에 `oe_home_page_object_type_group` 타입 클래스를 추가하던 이전 방식을 대체합니다. 이전 방식은 더 이상 사용할 수 없습니다.

***

<a id="add-a-backing-datasource-to-a-new-object-type"></a>
### 새 객체 타입에 백킹 데이터소스 추가하기 (Add a backing datasource to a new object type)

이 타입 객체의 속성 값을 데이터로 채우려면 백킹 데이터소스를 추가해야 합니다. 방법은 다음과 같습니다.

* **Overview** 페이지의 **Properties** 영역에서 **Create new**를 선택하거나, 객체 타입 보기 사이드바의 **Properties** 페이지에서 **Edit property mapping** 버튼을 선택해 속성 편집기(Property editor)로 들어갑니다.
* 그런 다음 아래 그림처럼 **Add a backing datasource** 버튼을 선택합니다. 그러면 Foundry에서 사용할 수 있는 어떤 데이터소스든 백킹 데이터소스로 선택할 수 있습니다.
  * 데이터소스 하나는 객체 타입 하나만 뒷받침할 수 있습니다.

![백킹 데이터셋 편집](https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-edit-backing-dataset.png)

<a id="add-a-new-property"></a>
### 새 속성 추가하기 (Add a new property)

속성 편집기 안에서 화면 오른쪽의 **Properties** 창에 있는 **Add**를 선택합니다. 그러면 객체 타입에 새 속성이 추가됩니다.

![새 속성 추가](https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-add-new-property.png)

<a id="map-a-single-property-to-data"></a>
### 속성 하나를 데이터에 매핑하기 (Map a single property to data)

속성을 백킹 데이터소스의 열에 매핑하는 방법은 다음과 같습니다.

* [열을 새 속성에 매핑하기](#map-a-column-to-a-new-property)
* [열을 기존 속성에 매핑하기](#map-a-column-to-an-existing-property)
* [속성을 열에 매핑하기](#map-a-property-to-a-column)

<a id="map-a-column-to-a-new-property"></a>
#### 열을 새 속성에 매핑하기 (Map a column to a new property)

화면 왼쪽의 데이터소스 창(아래 그림 참고)에서 데이터소스의 모든 열을 볼 수 있습니다. 매핑하려는 열 위에 마우스를 올리고 **Add as a new property** 버튼을 선택하면 이 열에 매핑된 새 속성이 만들어집니다. 속성 ID, 표시 이름, 기본 타입(base type)은 열 이름에서 추론됩니다.

![새 속성으로 추가](https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-add-as-a-new-property.png)

<a id="map-a-column-to-an-existing-property"></a>
#### 열을 기존 속성에 매핑하기 (Map a column to an existing property)

화면 왼쪽의 데이터소스 창에서 데이터소스의 모든 열을 볼 수 있습니다. 매핑되지 않은 열 위에 마우스를 올리고 **Add as a new property** 버튼을 선택합니다. 열 이름과 일치하는 속성 ID를 가진 속성이 이미 있으면, 그 열은 기존 속성에 매핑됩니다.

<a id="map-a-property-to-a-column"></a>
#### 속성을 열에 매핑하기 (Map a property to a column)

화면 오른쪽의 속성 창에서 열에 매핑하려는 속성 위에 마우스를 올리고 **Map to a column**을 선택합니다. 그러면 속성에 매핑할 열을 고를 수 있는 드롭다운이 열립니다.

![속성을 열에 매핑](https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-map-property-to-column.png)

<a id="map-all-unmapped-columns-as-new-properties"></a>
### 매핑되지 않은 모든 열을 새 속성으로 매핑하기 (Map all unmapped columns as new properties)

데이터소스 창의 데이터소스 이름 옆에 **Add all unmapped columns as new properties** 버튼이 있습니다. 이 버튼을 선택하면 데이터소스에서 매핑되지 않은 모든 열에 대해 속성이 만들어집니다. 속성의 ID, 표시 이름, 기본 타입은 데이터소스의 해당 열에서 추론됩니다.

* 속성의 ID가 저장되고 그 속성이 사용자 애플리케이션에서 참조되고 나면, 속성 ID를 **조금이라도** 바꾸면 애플리케이션이 깨집니다.

![매핑되지 않은 모든 열을 새 속성으로 추가](https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-add-all-unmapped-columns-as-new-properties.png)

**설명**: 예를 들어 백킹 데이터셋에 `employee_id`(string), `full_name`(string), `hire_date`(date) 세 열이 있다면, 이 버튼 한 번으로 같은 ID와 타입을 가진 속성 세 개가 생깁니다. ID 변경이 애플리케이션을 깨뜨리는 이유는, Workshop 같은 애플리케이션이 속성을 이름이 아니라 ID로 참조하기 때문입니다. 프로그램에서 변수 이름을 바꾸면 그 변수를 참조하던 다른 코드가 컴파일되지 않는 것과 같은 문제입니다.

<a id="configure-the-primary-key-and-title-key"></a>
### 기본 키와 타이틀 키 구성하기 (Configure the primary key and title key)

새 객체 타입을 만들고, 백킹 데이터소스를 추가하고, 이를 새 속성에 매핑했더라도, 객체 타입을 저장하려면 기본 키와 타이틀 키를 구성해야 합니다. 속성 편집기의 속성 메타데이터 창(아래 그림 참고)으로 이동해 속성을 기본 키와 타이틀 키로 지정할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-configure-keys-manual.png" alt="기본 키와 타이틀 키 구성" width="500" />

* **기본 키:** 객체 타입의 각 인스턴스를 유일하게 식별하는 속성입니다. 모든 객체는 이 속성에 대해 고유한 값을 가져야 합니다. 데이터소스 기반 객체 타입에서는 백킹 데이터소스의 각 행이 서로 다른 값을 가져야 합니다.
  * 예를 들어 `employee ID` 속성의 값은 "Melissa Chang"을 조직 안의 유일한 (가상의) 직원으로 식별하는 데 쓰입니다.
  * 기본 키를 구성하려면, 속성 편집기의 속성 창에서 기본 키로 지정할 속성을 선택하고 **Primary key** 옵션을 체크합니다.
  * 편집은 그 편집을 한 기본 키 값에 영구적으로 연결됩니다. 객체 타입의 기본 키를 바꿀 때마다 기존 편집을 모두 삭제하라는 안내가 나옵니다.
* **타이틀 키:** 이 타입 객체의 표시 이름 역할을 하는 속성입니다.
  * 예를 들어 `Employee` 객체 타입의 타이틀 키로 `full name` 속성을 선택하면, 그 속성의 값인 "Melissa Chang", "Akriti Patel", "Diego Rodriguez" 등이 각 가상의 `Employee` 객체의 표시 이름으로 쓰입니다.
  * 타이틀 키를 구성하려면, 속성 편집기의 속성 창에서 타이틀 키로 지정할 속성을 선택하고 **Title key** 옵션을 체크합니다.
    이 시점까지 변경 사항은 스테이징되었을 뿐 **아직 저장되지 않았습니다**. 새 객체 타입을 온톨로지에 저장하려면 [온톨로지에 변경 사항을 저장하는 방법](../../../05_applications/04_ontology-manager/06_change-management/01_save-changes.md) 안내를 따르세요.

**주의**: 기본 키를 지정하기 전에 반드시 백킹 데이터소스에 중복이 있는지 확인하고, 결정적인 기본 키를 사용하세요. Object Storage v2가 인덱싱 중에 강제하는 제약은 [기본 키와 고유성](../../../06_ontology-architecture/03_indexing/05_data-restrictions.md#primary-keys-and-uniqueness)을 참고하세요.

**설명**: 기본 키를 바꾸면 기존 편집을 지워야 하는 이유는, 편집이 "기본 키가 E001인 객체의 department를 Marketing으로 바꿈"처럼 기본 키 값을 주소로 삼아 저장되기 때문입니다. 기본 키를 `employee_id`에서 `email`로 바꾸면 E001이라는 주소가 더 이상 어떤 객체도 가리키지 않게 됩니다.

> **중간 요약**: 도우미를 일찍 빠져나와도 Overview 페이지와 속성 편집기에서 메타데이터 입력, 백킹 데이터소스 추가, 열과 속성 매핑, 기본 키와 타이틀 키 지정을 마치면 객체 타입을 저장할 수 있습니다. 데이터소스 하나는 객체 타입 하나만 뒷받침할 수 있고, 속성 ID나 기본 키를 나중에 바꾸면 애플리케이션이나 기존 편집에 영향을 줍니다.

<a id="configure-api-names"></a>
## API 이름 구성하기 (Configure API names)

API 이름은 코드에서 프로그래밍 방식으로 객체 타입이나 속성을 가리킬 때 쓰는 이름입니다. 새로 만든 모든 객체 타입과 속성에는 표시 이름에서 추론한 API 이름이 자동으로 지정됩니다. [API 이름에 대해 더 알아보세요(TSv1).](../../04_functions/13_functions-on-objects/06_api-objects-links.md)

자동으로 지정된 API 이름은 다음과 같이 바꿀 수 있습니다.

* 객체 타입의 API 이름은 객체 타입의 **Overview** 페이지에서 편집할 수 있습니다.
* 속성의 API 이름은 속성 편집기의 속성 창에서 편집할 수 있습니다.

<a id="naming-guidelines"></a>
### 이름 지정 지침 (Naming guidelines)

객체 타입 API 이름은 함수형 코딩 표준을 따릅니다. 객체 타입의 API 이름은 다음 조건을 만족해야 합니다.

* 대문자로 시작하고 영문자와 숫자로만 이루어져야 합니다.
* PascalCase(UpperCamelCase라고도 하며, 복합어에서 각 단어의 첫 글자를 대문자로 씁니다. 예: "ThisExampleName")로 써야 합니다.
* 모든 객체 타입에 걸쳐 고유해야 합니다.
* 길이가 1자 이상 100자 이하여야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-api.png" alt="객체 타입 API" width="500" />

속성의 API 이름은 다음 조건을 만족해야 합니다.

* 소문자로 시작하고 영문자와 숫자로만 이루어져야 합니다.
* camelCase(복합어에서 첫 단어 다음 각 단어의 첫 글자를 대문자로 씁니다. 예: "thisExampleName")로 써야 합니다.
* 같은 객체 타입에 속한 모든 속성에 걸쳐 고유해야 합니다.
* 길이가 1자 이상 100자 이하여야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/create-object-type-property-type-api.png" alt="속성 타입 API" width="500" />

**설명**: 이 규칙은 생성되는 SDK 코드에서 객체 타입이 클래스 이름, 속성이 필드 이름으로 쓰이는 관례와 맞춰져 있습니다. 예를 들어 표시 이름이 "Flight Delay"인 객체 타입은 API 이름이 `FlightDelay`, 표시 이름이 "Departure Time"인 속성은 `departureTime`이 됩니다. 이 페이지에는 ID, 표시 이름, API 이름이라는 세 가지 이름이 나오는데, 표시 이름은 사람이 보는 이름, ID는 애플리케이션 구성에서 쓰는 내부 식별자, API 이름은 코드에서 쓰는 식별자입니다.

> **중간 요약**: API 이름은 코드에서 객체 타입과 속성을 부르는 이름으로, 표시 이름에서 자동 생성되며 바꿀 수 있습니다. 객체 타입은 PascalCase, 속성은 camelCase로 쓰고, 각각의 범위 안에서 고유해야 하며 길이는 1\~100자입니다.

<a id="troubleshooting"></a>
## 문제 해결 (Troubleshooting)

<a id="mandatory-object-type-fields"></a>
### 필수 객체 타입 필드 (Mandatory object type fields)

새 객체 타입을 저장하려면 다음 객체 타입 필드가 비어 있으면 안 됩니다.

* ID
* 표시 이름(Display name)
* 복수형 표시 이름(Plural display name)
* 백킹 데이터소스(백킹 데이터소스 없이 만드는 경우는 제외)
* API 이름

또한 다음 속성 필드가 비어 있으면 안 됩니다.

* 속성 ID(Property ID)
* 속성 표시 이름(Property display name)
* 백킹 열(Backing column, 속성을 액션으로만 채우는 경우는 제외)
* 속성 API 이름(Property API name)
* 타이틀 키
* 기본 키

<a id="valid-id-checklist"></a>
### 유효한 ID 체크리스트 (Valid ID checklist)

<a id="object-type-id"></a>
#### 객체 타입 ID (Object type ID)

객체 타입 ID는 다음 조건을 따릅니다.

* 소문자, 숫자, 대시로 이루어질 수 있습니다.
* 문자로 시작해야 합니다.
* 모든 객체 타입에 걸쳐 고유해야 합니다.

<a id="property-type-id"></a>
#### 속성 타입 ID (Property type ID)

속성 타입 ID는 다음 조건을 따릅니다.

* 소문자나 대문자, 숫자, 대시, 밑줄로 이루어질 수 있습니다.
* 문자로 시작해야 합니다.
* 같은 객체 타입에 속한 모든 속성에 걸쳐 고유해야 합니다.

<a id="api-name"></a>
#### API 이름 (API name)

함수형 코딩 표준에 맞춰, 객체 타입의 API 이름은 다음 조건을 만족해야 합니다.

* 영문자, 숫자, 밑줄로만 이루어져야 합니다.
* 모든 객체 타입에 걸쳐 고유해야 합니다.
* 길이가 1자 이상 100자 이하여야 합니다.

속성의 API 이름은 다음 조건을 만족해야 합니다.

* 유효한 유니코드여야 합니다.
* 같은 객체 타입에 속한 모든 속성에 걸쳐 고유해야 합니다.
* 길이가 1자 이상 100자 이하여야 합니다.

다음 예약어는 API 이름으로 쓸 수 없습니다: `ontology`, `object`, `property`, `link`, `relation`, `rid`, `primaryKey`, `typeId`, `ontologyObject`.

**설명**: 예약어 제한은 프로그래밍 언어에서 `class`나 `if`를 변수 이름으로 쓸 수 없는 것과 같은 이유입니다. 생성되는 코드나 API 응답에서 이 이름들이 이미 시스템용 필드로 쓰이기 때문에, 사용자 속성 이름과 충돌하지 않도록 막아 둔 것입니다. 원문의 "이름 지정 지침"과 "API 이름 체크리스트"의 문구가 조금 다른데(예: 밑줄 허용 여부), 번역은 원문을 그대로 옮겼습니다.

<a id="errors"></a>
### 오류 (Errors)

<a id="error-phonograph2datasetandbranchalreadyregistered"></a>
#### 오류: `Phonograph2:DatasetAndBranchAlreadyRegistered`

`Phonograph2:DatasetAndBranchAlreadyRegistered` 오류가 발생했다면, 저장하려는 객체 타입을 뒷받침하는 데이터소스가 이미 온톨로지의 다른 객체 타입을 뒷받침하고 있어서 다시 사용할 수 없다는 뜻입니다.

> **중간 요약**: 저장이 안 될 때는 필수 필드(ID, 표시 이름, 복수형 표시 이름, 백킹 데이터소스, API 이름, 기본 키, 타이틀 키 등)가 비어 있지 않은지, ID와 API 이름 규칙과 예약어를 지켰는지 확인합니다. `DatasetAndBranchAlreadyRegistered` 오류는 데이터소스가 이미 다른 객체 타입에 쓰이고 있다는 뜻입니다.

## 정리

- 새 객체 타입은 Ontology Manager의 단계별 도우미로 만드는 것이 권장되며, 도우미를 중간에 나와도 Overview 페이지와 속성 편집기에서 수작업으로 마무리할 수 있습니다.
- 백킹 데이터소스의 열이 속성으로 매핑되고, 데이터소스 하나는 객체 타입 하나만 뒷받침합니다. 모든 속성을 액션으로 채울 경우 데이터소스 없이 만들 수 있지만, 이때는 프로젝트 저장과 객체 보안 정책이 필요합니다.
- 기본 키는 고유하고 결정적이어야 하며, 편집은 기본 키 값에 연결되므로 기본 키를 바꾸면 기존 편집이 삭제됩니다. 타이틀 키는 화면 표시용 이름입니다.
- **Create**는 스테이징일 뿐이고 **Save**를 눌러야 온톨로지에 저장됩니다.
- API 이름은 객체 타입은 PascalCase, 속성은 camelCase로 쓰며, 예약어는 쓸 수 없습니다.
