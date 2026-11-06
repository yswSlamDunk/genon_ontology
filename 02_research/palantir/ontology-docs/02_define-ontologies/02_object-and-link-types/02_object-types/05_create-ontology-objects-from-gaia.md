# Gaia에서 온톨로지 객체 만들기 (Create Ontology objects from Gaia)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/create-ontology-objects-from-gaia/
- 사이드바 위치: Define Ontologies > Object and link types > Object types > Create Ontology objects from Gaia

이 페이지는 Gotham의 지도 애플리케이션인 Gaia에서 사용자가 그린 도형, 찍은 점, 구성한 전술 그래픽을 Foundry 온톨로지(Ontology)의 객체로 저장하는 전체 과정을 설명합니다. 이를 위해서는 특정 인터페이스를 구현한 객체 타입, 객체를 만들어 주는 액션 타입, 그리고 Gaia가 그 객체 타입을 찾을 수 있게 하는 등록 절차가 필요합니다. 지도 위의 그림 한 개가 데이터베이스의 행 하나로 저장되는 흐름을 처음부터 끝까지 따라가는 실습형 문서입니다.

[온톨로지의 데이터를 Gaia 지도에 추가](https://www.palantir.com/docs/foundry/geospatial/add-ontology-data-to-gaia/)할 수 있는 것처럼, 반대로 지도에서 그린 도형, 찍은 점, 구성한 전술 그래픽으로부터 온톨로지 객체를 만들 수도 있습니다. 방법은 그 객체에 `Creatable Geoshape`, `Creatable Geopoint`, 또는 `MILSTD 2525C Symbol` [인터페이스](../../05_interfaces/01_interface-overview.md)를 구현한 객체 타입을 태그하는 것입니다.

**참고**: 계획된 지원 중단 단계의 인터페이스 대신 이를 대체하는 객체 생성 인터페이스를 구현하세요(Implement the superseding object creation interfaces instead of those in planned deprecation). `Creatable Geoshape`, `Creatable Geopoint`, `MILSTD 2525 Symbol` 인터페이스는 각각 `Gaia Geoshape Creatable`, `Gaia Geopoint Creatable`, `Gaia Milsym Creatable` 인터페이스를 대체합니다. `Gaia Geoshape Creatable`과 `Gaia Geopoint Creatable`은 개발 생명 주기상 [계획된 지원 중단(planned deprecation)](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/#planned-deprecation) 단계에 있으며 2026년 11월까지 지원이 중단됩니다. `Gaia Milsym Creatable` 인터페이스는 이미 [지원 중단(deprecated)](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/#deprecated)되었습니다. 계획된 지원 중단 단계의 인터페이스 대신 대체 인터페이스를 구현해야 합니다. [아래의 구성 지침](#create-an-object-type-that-implements-the-gaia-geoshape-creatable-interface)에 나오는 객체 타입과 액션 타입 설정은 어느 쪽 인터페이스에도 적용됩니다. 다만 [인터페이스 액션 타입 제약(interface action type constraints)](#use-interface-action-type-constraints-to-enable-automatic-discovery-of-object-types-supporting-object-creation)은 `Creatable Geoshape`, `Creatable Geopoint`, `MILSTD 2525C Symbol` 인터페이스만 지원합니다. `Gaia Geoshape Creatable`과 `Gaia Geopoint Creatable` 인터페이스는 인터페이스 액션 타입 제약을 쓰는 대신 [이를 구현한 객체 타입과 지원 액션을 Gaia의 관리자 애플리케이션 또는 Control Panel 확장 기능에 등록](#register-your-ontology-and-its-types)해야 합니다.
여러분의 환경(enrollment)에서 `Creatable Geoshape`, `Creatable Geopoint`, `MILSTD 2525 Symbol` 인터페이스를 사용할 수 있는지에 대한 문의는 Palantir Support에 연락하세요.

![Gaia 지도의 왼쪽 패널에 Create shape 창이 표시되어 있으며, 사용자는 지도에 그린 도형을 자신의 온톨로지에 있는 객체 타입의 객체로 태그할 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/create-shape.png)

**설명**: Gaia는 Palantir의 다른 플랫폼인 Gotham에 포함된 지도 애플리케이션입니다. 이 페이지의 흐름을 데이터 관점에서 보면, 사용자가 지도에 다각형을 하나 그리면 그 좌표 정보가 `Geoshape` 속성 값이 되고, 자동 생성된 ID가 기본 키(primary key)가 되어 객체 타입의 새 행(객체) 하나가 만들어지는 과정입니다. 인터페이스는 프로그래밍 언어의 인터페이스처럼 "이 객체 타입은 `Geoshape` 속성을 가진다"는 형태 계약을 정의하므로, Gaia는 해당 인터페이스를 구현한 객체 타입이라면 어떤 것이든 도형 저장 대상으로 다룰 수 있습니다. "enrollment"는 한 고객 조직이 사용하는 Palantir 플랫폼 설치 단위를 가리킵니다.

아래 섹션들은 Gaia의 도형, 점, 전술 그래픽을 온톨로지와 통합하는 전체 과정을 설명합니다.

**주의**: Gaia 지도에서 온톨로지 객체를 만들려면 여러분의 enrollment가 Foundry와 Gotham을 모두 사용해야 합니다.

* [필요한 Marketplace 제품을 모두 설치합니다](#install-prerequisite-marketplace-products).
* [제한된 뷰(restricted view)를 백킹 데이터소스로 쓰는 지원 객체 타입에 `Gaia Geoshape Creatable` 인터페이스를 구현합니다](#create-an-object-type-that-implements-the-gaia-geoshape-creatable-interface).
* [제한된 뷰를 백킹 데이터소스로 쓰는 지원 객체 타입에 `Gaia Geopoint Creatable` 인터페이스를 구현합니다](#create-an-object-type-that-implements-the-gaia-geopoint-creatable-interface).
* [제한된 뷰를 백킹 데이터소스로 쓰는 지원 객체 타입에 `MILSTD 2525C Symbol` 인터페이스를 구현합니다](#create-an-object-type-that-implements-the-milstd-2525c-symbol-interface).
* [객체 타입에서 인터페이스 액션 타입 제약을 충족시킵니다](#use-interface-action-type-constraints-to-enable-automatic-discovery-of-object-types-supporting-object-creation).
* [온톨로지를 등록하고 Gaia에서 객체 타입을 검색합니다](#register-your-ontology-and-its-types).
* [객체를 만드는 진입점을 이해합니다](#entry-points-to-create-objects-on-your-gaia-map).
* [지도에 새 도형을 그리고 객체 타입으로 태그합니다](#draw-a-new-shape-on-your-gaia-map-and-tag-it-to-an-object-type).
* [지도에 새 점을 찍고 객체 타입으로 태그합니다](#drop-a-new-point-on-your-gaia-map-and-tag-it-to-an-object-type).
* [지도에 그린 도형으로 전술 그래픽을 구성하고 객체 타입으로 태그합니다](#configure-a-tactical-graphic-on-your-gaia-map-and-tag-it-to-an-object-type).

> **중간 요약**: Gaia 지도에서 그린 도형, 점, 전술 그래픽을 온톨로지 객체로 저장할 수 있으며, 이를 위해 객체 타입이 `Creatable Geoshape`, `Creatable Geopoint`, `MILSTD 2525C Symbol` 같은 인터페이스를 구현해야 합니다. 예전 `Gaia ... Creatable` 인터페이스는 지원 중단 예정이거나 이미 중단되었고, Foundry와 Gotham을 함께 쓰는 환경이어야 합니다.

<a id="install-prerequisite-marketplace-products"></a>
## 사전 필요한 Marketplace 제품 설치 (Install prerequisite Marketplace products)

**참고**: 이 섹션의 지침은 `Gaia Geoshape Creatable` 또는 `Gaia Geopoint Creatable` 인터페이스를 사용할 때만 수행하면 됩니다. 최신 `Creatable Geoshape` 또는 `Creatable Geopoint` 인터페이스를 사용할 때는 Marketplace에서 설치해야 할 사전 요구 사항이 없습니다.

[Marketplace](https://www.palantir.com/docs/foundry/marketplace/overview/)는 게시된 데이터 제품이나 플랫폼 리소스 모음을 사용자가 설치할 수 있게 제공하는 Foundry의 상점입니다. 홈 화면의 **Search...** 바나 **Applications** 포털을 통해 Marketplace에 접근할 수 있습니다.

Marketplace를 열었다면 다음 제품을 설치합니다.

* [Core Ontology Store의 Core Property Types](#core-property-types-from-the-core-ontology-store): 객체의 등급(classification)과 지오셰이프(geoshape)처럼 온톨로지의 여러 객체 타입에서 쓸 수 있는 핵심 공유 속성(shared property) 타입을 담고 있습니다.
* [Gaia App Store의 `Gaia Geoshape Creatable` 인터페이스](#gaia-geoshape-creatable-interface-from-the-gaia-app-store): 지리 공간 객체 타입의 형태를 기술하여, 같은 형태를 가진 다른 객체 타입과 일관되게 모델링하고 상호작용할 수 있게 합니다.
* [Gaia App Store의 `Gaia Geopoint Creatable` 인터페이스](#gaia-geopoint-creatable-interface-from-the-gaia-app-store): 단일 점 객체 타입의 위치를 기술합니다.

**설명**: 지오셰이프(geoshape)는 다각형이나 선처럼 여러 좌표로 이루어진 지리 도형 값이고, 지오포인트(geopoint)는 위도와 경도 한 쌍으로 표현되는 점 하나의 위치 값입니다. 공유 속성은 여러 객체 타입이 같은 정의를 재사용하는 속성이므로, `Geoshape`을 공유 속성으로 두면 서로 다른 객체 타입들도 "같은 의미의 도형 속성"을 가진다고 플랫폼이 인식할 수 있습니다.

<a id="core-property-types-from-the-core-ontology-store"></a>
### Core Ontology Store의 Core Property Types (Core Property Types from the Core Ontology Store)

Core Property Types 제품이 들어 있는 Core Ontology Store가 Marketplace에 없다면, Palantir Support에 연락해 Core Ontology를 [Foundry 제품](https://www.palantir.com/docs/foundry/marketplace/foundry-products/)으로 여러분의 Foundry enrollment에 설치해 달라고 요청하세요.

<a id="gaia-geoshape-creatable-interface-from-the-gaia-app-store"></a>
### Gaia App Store의 `Gaia Geoshape Creatable` 인터페이스 (`Gaia Geoshape Creatable` interface from the Gaia App Store)

Foundry에서 [인터페이스](../../05_interfaces/01_interface-overview.md)는 온톨로지 안에 존재하면서 객체 타입의 형태와 기능을 기술하고, 공통된 형태를 가진 객체 타입들 사이에서 일관된 모델링과 상호작용을 가능하게 합니다. 하나의 인터페이스를 여러 객체 타입에 구현할 수 있으며, 인터페이스는 다른 인터페이스를 몇 개든 확장(extend)할 수 있습니다. `Gaia Geoshape Creatable` 인터페이스를 객체 타입에 구현하면 Gaia 지도에 그린 도형으로부터 온톨로지의 객체를 만들 수 있게 됩니다.

**참고**: `Gaia Geoshape Creatable` 인터페이스는 지원 중단된 `Gaia Geocreatable` 인터페이스를 대체합니다. Marketplace에서 `Gaia Geoshape Creatable` 인터페이스에 접근할 수 없다면 Palantir Support에 연락하세요.

Marketplace에서 `Gaia Geoshape Creatable` 인터페이스를 설치하는 방법은 다음과 같습니다.

1. Marketplace로 돌아가 **Search stores...** 에서 `Gaia App Store`를 검색합니다.
2. `Gaia Geoshape Creatable` 제품을 선택합니다.
3. 화면 오른쪽의 파란색 **Install** 버튼을 선택해 설치 초안(draft installation)을 시작합니다. 원하면 설치에 설명용 접미사(suffix)를 붙일 수 있습니다.
4. 설치가 저장될 **Namespace**를 지정합니다. Marketplace는 선택한 **Namespace** 안에 새 **Project**를 자동으로 만듭니다.
5. **Permissions** 에서 제품의 등급과 접근 제어를 구성합니다. **Classification based access control (CBAC)** 에서 선택한 등급이 이 설치의 *최대* 등급이 됩니다.
6. **Next**를 선택해 설치 창의 **Inputs** 페이지를 엽니다.
7. 왼쪽 패널의 **Inputs** 아래 **Shared properties** 탭을 선택해, 온톨로지의 `Geoshape` 공유 속성을 새 인터페이스에 매핑합니다.
8. **Next**를 선택해 설치 창의 **Content** 페이지를 엽니다.

![Gaia Geoshape Creatable 인터페이스의 Shared properties 페이지가 표시되어 있으며, 사용자는 여기서 인터페이스에 포함할 공유 속성을 구성합니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/map-geoshape-creatable-inputs-as-spts.png)

9. 원하면 **Prefix Ontology entities**를 켜고 유효한 접두사(prefix)를 입력합니다. 접두사에는 괄호나 대괄호 같은 일부 특수 문자를 쓸 수 없습니다.
10. 화면 오른쪽에서 활성화할 **Ontology schema migrations**를 선택합니다. 스키마 관리에 대한 추가 정보는 기존 [객체 편집과 머티리얼라이제이션 문서](../../../06_ontology-architecture/04_object-edits-and-materializations/05_schema-migrations.md)를 참고하세요.
11. **Next**를 선택하기 전에, 필요에 따라 **New versions** 의 자동 구성을 사용 사례에 맞게 수정합니다. Marketplace는 일부 제품을 자동으로 업그레이드하도록 미리 구성해 둡니다.
12. 인터페이스 구성을 검토하고 **Install**을 선택합니다.

**설명**: CBAC(Classification Based Access Control, 등급 기반 접근 제어)는 데이터와 사용자에게 "기밀", "비밀" 같은 등급을 붙이고, 사용자의 등급이 데이터의 등급 이상일 때만 접근을 허용하는 방식입니다. 5단계의 "최대 등급"은 이 설치로 만들어지는 리소스가 가질 수 있는 등급의 상한입니다. 10단계의 스키마 마이그레이션은 이미 데이터가 쌓인 상태에서 속성 타입 등 스키마가 바뀔 때 기존 데이터를 어떻게 옮길지 정하는 설정입니다.

<a id="gaia-geopoint-creatable-interface-from-the-gaia-app-store"></a>
### Gaia App Store의 `Gaia Geopoint Creatable` 인터페이스 (`Gaia Geopoint Creatable` interface from the Gaia App Store)

Marketplace의 Gaia App Store에서 `Gaia Geopoint Creatable` 인터페이스를 설치하려면 상점 메뉴에서 `Gaia Geopoint Creatable` 제품을 선택합니다. Marketplace의 인터페이스 설치 흐름은 인터페이스마다 공통이므로, 위의 [Geoshape Creatable 인터페이스 설치 지침](#gaia-geoshape-creatable-interface-from-the-gaia-app-store)과 같은 단계를 따르되 다음 차이점만 적용하면 됩니다.

* **Inputs** 창의 **Shared properties** 섹션에서, 온톨로지의 `Geopoint` 공유 속성을 `Gaia Geopoint Creatable` 인터페이스에 매핑합니다.

> **중간 요약**: 예전 `Gaia Geoshape Creatable`, `Gaia Geopoint Creatable` 인터페이스를 쓸 때만 Marketplace에서 Core Property Types와 해당 인터페이스 제품을 설치해야 합니다. 설치 과정에서 `Geoshape` 또는 `Geopoint` 공유 속성을 인터페이스에 매핑하고, 등급, 네임스페이스, 스키마 마이그레이션 등을 설정합니다.

<a id="create-an-object-type-that-implements-the-gaia-geoshape-creatable-interface"></a>
## `Gaia Geoshape Creatable` 인터페이스를 구현하는 객체 타입 만들기 (Create an object type that implements the `Gaia Geoshape Creatable` interface)

Gaia는 온톨로지에서 [데이터셋](https://www.palantir.com/docs/foundry/data-integration/datasets/) 또는 [제한된 뷰(restricted view)](https://www.palantir.com/docs/foundry/security/restricted-views/)를 백킹 데이터소스(backing datasource)로 쓰는 객체 타입이 `Gaia Geoshape Creatable` 인터페이스를 구현하고 나면 그 객체 타입을 찾아낼 수 있습니다. 다음 섹션들에서는 아래 작업을 합니다.

* [객체 타입의 백킹 데이터셋 또는 제한된 뷰를 만듭니다](#create-an-object-type-backing-dataset-or-restricted-view).
* [객체 타입을 만들고 Gotham과 통합되는지 확인합니다](#create-an-object-type-and-ensure-it-integrates-with-gotham).
* [Gaia에서 객체를 생성할 수 있도록 액션 타입을 구성합니다](#create-and-configure-an-action-type-to-enable-object-creation-in-gaia).
* [`Gaia Geoshape Creatable` 인터페이스를 구현합니다](#implement-the-gaia-geoshape-creatable-interface).

<a id="create-an-object-type-backing-dataset-or-restricted-view"></a>
### 객체 타입의 백킹 데이터셋 또는 제한된 뷰 만들기 (Create an object type-backing dataset or restricted view)

**팁**: 사용자의 등급(classification)에 따라 객체를 보호하거나, 파일 접근을 제어하기 위해 [마킹(markings)](https://www.palantir.com/docs/foundry/security/markings/)을 적용할 계획이라면 제한된 뷰를 만들어야 합니다. 사용 사례에 등급 기반 접근이나 마킹이 제공하는 추가 객체 보안이 필요하지 않다면, 객체 타입의 백킹 데이터소스로 데이터셋을 만들면 됩니다.

**설명**: 제한된 뷰는 데이터셋 위에 행 단위 접근 정책을 얹은 뷰입니다. SQL의 뷰(view)에 사용자별 `WHERE` 조건이 자동으로 붙는다고 보면 정확합니다. 예를 들어 `classification` 열 값이 "SECRET"인 행은 SECRET 등급 이상을 가진 사용자에게만 보이게 할 수 있습니다. 마킹은 데이터에 붙이는 접근 제어 표식으로, 그 마킹에 대한 권한이 있는 사용자만 데이터를 볼 수 있습니다.

Gaia와 통합할 수 있는 객체 타입을 만들려면 먼저 최소한 다음 열을 가진 데이터셋 또는 제한된 뷰를 만들어야 합니다.

* `Geoshape`: `string`으로 설정하며, Gaia가 그려진 객체의 도형으로 자동으로 채웁니다.
* `Object ID`: `string`으로 설정하며, Gaia 도형을 객체로 만들 때마다 Foundry가 고유 ID로 자동으로 채웁니다. 이 열이 객체 타입의 기본 키가 됩니다.
* `Classification`: `array`로 설정하며, 객체의 등급을 담습니다. `Classification` 열은 제한된 뷰가 객체 타입의 백킹 데이터소스일 때*만* 필요합니다.

**팁**: 사용 사례에 맞게 데이터셋이나 제한된 뷰에 열을 더 구성할 수 있습니다. 예를 들어 사용자가 입력한 객체 설명 정보를 담기 위해 `Name`, `Category`, `Notes` 같은 열을 `string`으로 둘 수 있습니다.

**설명**: 예를 들어 최소 구성의 백킹 테이블은 처음에는 비어 있고, Gaia에서 도형을 하나 저장하면 다음과 같은 행이 추가됩니다.

| Object ID | Geoshape | Classification | Name |
|---|---|---|---|
| `a1b2c3` | `{"type":"Polygon","coordinates":[...]}` | `["SECRET"]` | 집결지 A |

`Geoshape`은 문자열 열이지만 객체 타입에서는 geoshape 속성 타입으로 해석됩니다(이 예시의 값 형식은 설명을 위한 것입니다).

Project에서 **New** 버튼을 선택해 `.csv` 같은 기존 파일을 업로드하거나, [Fusion](https://www.palantir.com/docs/foundry/fusion/overview/)을 사용해 독립 데이터셋 또는 제한된 뷰의 백킹 데이터셋을 만듭니다. 데이터셋을 객체 타입의 백킹 데이터소스로 쓴다면 아래의 제한된 뷰 생성 지침은 건너뛰고 [객체 타입 만들기](#create-an-object-type-and-ensure-it-integrates-with-gotham)로 넘어가면 됩니다.

![사용자는 Project에서 New 버튼을 선택해 데이터를 .csv로 업로드하거나, 제한된 뷰의 백킹 데이터를 저장할 새 Fusion 시트를 만들 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/create-new-dataset-upload-fusion.png)

**팁**: 제한된 뷰 생성에 대한 추가 지침은 Foundry의 [보안](https://www.palantir.com/docs/foundry/security/restricted-views/#create-restricted-views) 문서와 [객체 권한](../../../06_ontology-architecture/02_object-permissioning/05_configuring-rv-access-controls.md) 문서를 참고하세요.

제한된 뷰에는 사용자의 [등급 접근 권한](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/)에 따라 뷰 안의 데이터 접근을 제한하는 [세분화된 정책(granular policy)](https://www.palantir.com/docs/foundry/security/restricted-views/#compose-a-granular-policy)이 있어야 합니다. 세분화된 정책은 **Create '{restricted view}'** 창의 첫 단계에서 작성합니다.

![제한된 뷰 정책의 예시가 표시되어 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/create-restricted-view.png)

**주의**: 객체에 접근을 제한하는 CBAC 속성이나 필수 마킹(mandatory marking) 속성이 있다면, Foundry는 Gaia 지도로부터 상속한 CBAC 또는 필수 마킹을 사용해 객체를 만들며, 지도의 보안 및 공유 설정에 정의된 그룹 제한은 *적용하지 않습니다*.

아래는 JSON으로 작성한 정책 예시입니다.

```json
{
  "condition": {
    "and": {
      "conditions": [
        {
          "markings": {
            "value": {
              "field": {
                "fieldName": "classification"
              },
              "type": "field"
            },
            "filters": [
              {
                "markingTypes": {
                  "markingTypes": [
                    "CBAC"
                  ]
                },
                "type": "markingTypes"
              }
            ]
          },
          "type": "markings"
        }
      ]
    },
    "type": "and"
  }
}
```

**설명**: 이 정책은 조건 하나(`and` 안에 `markings` 조건 하나)로 이루어져 있습니다. 각 행의 `classification` 필드 값을 마킹으로 해석하되, 그중 마킹 타입이 `CBAC`인 것만 검사 대상으로 삼습니다. 결과적으로 "사용자가 이 행의 `classification` 열에 적힌 CBAC 마킹을 모두 충족할 때만 그 행을 볼 수 있다"는 행 단위 필터가 됩니다.

<a id="create-an-object-type-and-ensure-it-integrates-with-gotham"></a>
### 객체 타입을 만들고 Gotham과 통합되는지 확인하기 (Create an object type and ensure it integrates with Gotham)

제한된 뷰를 구성했다면 [Ontology Manager](../../../05_applications/04_ontology-manager/01_overview.md)를 열고 다음 단계에 따라 객체 타입을 만듭니다.

1. 화면 오른쪽 위에서 **New** > **Object type**을 선택합니다.
2. **Use existing datasource**를 선택하고 **Select datasource**를 눌러 제한된 뷰를 찾아 **Select**한 다음 **Next**를 선택합니다.
3. 객체 타입의 이름을 정하고, 원하면 **Description**을 입력합니다.
4. `Object ID`를 **Primary Key**로, `Name`을 **Title**로 설정합니다.
5. `Classification`의 **Property**가 문자열 배열이고 `Geoshape`의 **Property**가 geoshape인지 확인합니다. 앞의 것(`Classification`)은 제한된 뷰가 객체 타입의 백킹 데이터소스일 때만 확인하면 됩니다.

![Ontology Manager의 Create a new object type 창이 표시되어 있으며, 사용자는 객체 타입의 Primary Key와 Title을 설정하고 속성을 구성할 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/object-type-classification-array.png)

6. **Create**를 선택합니다. 액션 타입은 객체 타입을 만든 *후에* 생성하고 구성합니다.

초안 객체 타입이 Ontology Manager에 표시되면, 다음으로 `Classification`과 `Geoshape` 속성을 온톨로지의 공유 속성 타입으로 지정합니다. **Overview** 아래의 **Properties** 패널을 선택하고 다음 단계에 따라 공유 속성 타입 지정을 마칩니다.

**팁**: `Classification` 속성이 *없는* 데이터셋을 객체 타입의 백킹 데이터소스로 쓰고 있다면, `Geoshape` 속성에 대해 아래 1단계와 4단계만 수행하면 됩니다.

1. 속성 목록에서 `Classification`을 선택해 화면 오른쪽에 **Property editor** 창을 엽니다.
2. **Base type** 드롭다운 메뉴를 각각 `Mandatory control`과 `CBAC Marking`으로 바꿉니다.
3. 속성의 **Max Classification**(최대 등급)을 구성합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/map-classification-spt.png" alt="Property editor 창이 표시되어 있으며, 사용자는 여기서 속성을 공유 속성 타입에 매핑할 수 있습니다" width=400>

**주의**: **Mandatory control** 마킹은 모든 Foundry enrollment에서 일반 제공(generally available)되는 기능이 아니므로, `Classification`의 기본 타입으로 **Mandatory control**을 선택할 수 없다면 Palantir Support에 연락하세요.

4. 창 맨 아래의 **Shared property** 섹션까지 스크롤한 뒤, 드롭다운 메뉴로 `Classification`을 공유 속성으로 지정합니다.

![Property editor 창의 Shared property 섹션에서 공유 속성을 지정합니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/assign-classification-spt.png)

`Geoshape` 속성에 대해서도 위의 1단계와 4단계를 반복합니다. `Geoshape`은 필수 통제(mandatory control) 마킹이나 등급을 구성할 필요가 *없습니다*.

다음으로 넘어가기 전에 화면 위쪽의 초록색 **Save** 버튼을 눌러 변경 사항을 온톨로지에 점진적으로 게시합니다.

여러분의 Foundry enrollment에 Map Rendering Service(MRS)가 있다면, 지리 공간 속성 타입을 가진 온톨로지의 객체 타입은 Gotham과 자동으로 통합되므로 바로 [Gaia에서 객체를 생성할 수 있도록 액션 타입 만들기](#create-and-configure-an-action-type-to-enable-object-creation-in-gaia)로 넘어가면 됩니다. enrollment에 MRS가 있는지 확인하려면 [Gotham 통합 문서](04_enable-gotham-integration.md#how-to-check-if-your-enrollment-contains-mrs)의 단계를 따르세요. enrollment에 MRS가 *없다면* [이 지침](04_enable-gotham-integration.md#toggle-on-type-mapping-in-foundrys-ontology-manager)을 따라 온톨로지의 데이터를 Gotham과 통합합니다.

**설명**: 2단계의 `Mandatory control`은 기본 타입(base type)이 "필수 통제 마킹 값을 담는 속성"이라는 뜻이고, `CBAC Marking`은 그 마킹이 등급 기반 접근 제어용이라는 세부 지정입니다. 이렇게 지정하면 이 속성의 값이 단순 문자열이 아니라 접근 제어에 실제로 쓰이는 값이 됩니다.

<a id="create-and-configure-an-action-type-to-enable-object-creation-in-gaia"></a>
### Gaia에서 객체를 생성할 수 있도록 액션 타입 만들고 구성하기 (Create and configure an action type to enable object creation in Gaia)

객체 타입을 만들고 Gotham과 통합되는 것을 확인했다면 Ontology Manager의 **Overview** 창으로 돌아갑니다. 여기서 사용자가 Gaia에서 도형으로 객체를 만들고 편집하며 `Name`, `Category` 같은 속성을 구성할 수 있게 하는 [액션 타입](../../03_action-types/01_overview.md)을 만듭니다.

**주의**: Gaia에서 온톨로지 객체를 편집하려면 Foundry enrollment에 MRS가 있어야 합니다. 이 기능은 타입 매핑(type mapping)을 통해 Gaia에 추가된 객체에는 적용되지 않습니다. MRS 설치나 기능에 대한 문의는 Palantir Support에 연락하세요.

다음 단계에 따라 액션 타입을 구성합니다.

1. 객체 타입 **Overview** 창의 **Action types** 섹션에서 **New**를 선택해 **Create a new action type** 팝업 창을 엽니다.

**팁**: **Action types** 에서 **New** 버튼을 선택할 수 없다면, **Datasources** 창에서 객체 타입의 **Allow edits**를 켜면 됩니다.

2. **Object actions** 아래의 **Modify or create object**를 선택한 다음 **Next**를 선택합니다.

3. **Or create a new object with** 드롭다운 메뉴에서 **Auto-generated primary key**를 선택합니다.

4. **Add property**를 선택해 기존 속성을 모두 액션 타입에 추가한 다음, **Next**를 선택해 액션 타입의 메타데이터를 구성합니다.

   `Classification` 속성은 제한된 뷰가 객체 타입의 백킹 데이터소스일 때만 매핑하면 됩니다.

   ![Create a new action type 창이 표시되어 있으며, 사용자는 액션 입력으로 쓰일 액션 파라미터를 매핑할 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/configure-create-or-modify-action-type-properties.png)

5. 액션 타입의 이름을 정하고, 원하면 설명을 입력하고 기본 아이콘을 바꿉니다.

6. 액션을 실행할 수 있는 **Organization**, **Group**, 또는 **User**를 선택한 다음 **Create**를 선택합니다.

다음으로 넘어가기 전에 화면 위쪽의 초록색 **Save** 버튼을 눌러 변경 사항을 온톨로지에 점진적으로 게시합니다.

이제 다음 단계에 따라 액션 타입의 **Rules**와 **Parameters**를 구성합니다.

1. 화면 왼쪽에서 **Rules**를 선택합니다.
2. **Configure parameter** 옆의 화살표 아이콘을 선택해 `Geoshape` 속성의 구성을 확인합니다.
   * 화면 오른쪽의 **Type** 드롭다운 메뉴에서 `Geoshape` 속성의 타입이 `Geoshape` 또는 `String`인지 확인합니다.
   * 사용자가 `Geoshape`의 위치를 수동으로 구성하지 못하도록 **General** 패널에서 **Disabled** 옵션이 선택되어 있는지 확인합니다.

![Ontology Manager의 Create object 창이 표시되어 있으며, 사용자는 Rules 패널에서 속성을 매핑해 규칙을 만들 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/configure-create-object-type.png)

3. 화면 왼쪽의 **Form content** 패널에서 `Classification` 속성을 선택하고 **Type**이 `Mandatory control`인지 확인합니다. `Classification` 속성은 제한된 뷰가 객체 타입의 백킹 데이터소스일 때만 구성하면 됩니다.
4. **Back to Form**을 선택하고, **Object Id** 패널 오른쪽 끝의 **X** 아이콘을 눌러 **Form content** 에서 `Object Id`를 제거합니다. Foundry가 Gaia에서 만들어지는 각 객체에 고유 ID를 자동으로 생성합니다.
5. 화면 위쪽의 초록색 **Save** 버튼을 눌러 액션 타입 구성을 온톨로지에 저장합니다.

**설명**: 이 액션 타입은 SQL로 보면 "기본 키가 없으면 `INSERT`, 있으면 `UPDATE`"하는 업서트(upsert) 연산을 정의한 것입니다. 액션의 파라미터는 함수의 인자에 해당하며, Gaia가 액션을 호출할 때 `Geoshape` 파라미터에 사용자가 그린 도형을 자동으로 넣습니다. 그래서 `Geoshape` 파라미터는 폼에서 **Disabled**로 두어 사용자가 직접 수정하지 못하게 하고, `Object Id`는 자동 생성되므로 폼에서 아예 제거합니다.

<a id="implement-the-gaia-geoshape-creatable-interface"></a>
### `Gaia Geoshape Creatable` 인터페이스 구현하기 (Implement the `Gaia Geoshape Creatable` interface)

Ontology Manager에서 객체 타입을 만들고 구성하는 마지막 단계는 [앞서 Marketplace에서 설치한](#gaia-geoshape-creatable-interface-from-the-gaia-app-store) `Gaia Geoshape Creatable` 인터페이스를 구현하는 것입니다. 객체 타입의 **Overview** 페이지로 돌아가 다음 단계에 따라 인터페이스를 구현한 뒤 온톨로지에 변경 사항을 저장합니다.

1. 화면 왼쪽의 **Object Views** 아래에 있는 **Interfaces** 창으로 이동합니다.
2. **Implement new interface**를 선택하고 `Gaia Geoshape Creatable`을 검색한 다음 **Next**를 선택합니다. 여러분의 enrollment에서 이를 대체하는 `Creatable Geoshape` 인터페이스를 쓸 수 있다면 그것을 검색합니다.
3. **Choose an option** > **Replace existing**을 선택해 온톨로지의 `Geoshape` 공유 속성 타입을 인터페이스를 구현하는 객체 타입에 매핑합니다.
4. **Confirm**을 선택해 **Implement an interface** 창을 닫고, 새로 구성한 인터페이스를 온톨로지에 **Save**합니다.

![객체 타입에 구현된 후의 Gaia Geoshape Creatable 인터페이스가 Ontology Manager의 Interfaces 창에 표시되어 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/implemented-gaia-geoshape-creatable-interface.png)

**설명**: 3단계의 **Replace existing**은 객체 타입에 이미 있는 `Geoshape` 속성을 인터페이스가 요구하는 `Geoshape` 공유 속성에 연결한다는 뜻입니다. 클래스가 인터페이스를 구현할 때 인터페이스에 선언된 메서드를 클래스의 기존 메서드로 채우는 것과 같은 대응 관계입니다.

> **중간 요약**: `Geoshape`, `Object ID`(기본 키), 필요하면 `Classification` 열을 가진 데이터셋 또는 제한된 뷰를 만들고, 이를 백킹 데이터소스로 객체 타입을 만듭니다. 이어서 기본 키를 자동 생성하는 `Modify or create object` 액션 타입을 구성하고, 마지막으로 `Gaia Geoshape Creatable`(또는 `Creatable Geoshape`) 인터페이스를 구현해 `Geoshape` 공유 속성을 연결합니다.

<a id="create-an-object-type-that-implements-the-gaia-geopoint-creatable-interface"></a>
## `Gaia Geopoint Creatable` 인터페이스를 구현하는 객체 타입 만들기 (Create an object type that implements the `Gaia Geopoint Creatable` interface)

`Gaia Geopoint Creatable` 인터페이스를 구현하는 객체 타입을 만들려면, 위의 [`Gaia Geoshape Creatable` 인터페이스용 객체 타입 생성 지침](#create-an-object-type-that-implements-the-gaia-geoshape-creatable-interface)과 같은 단계를 따르되 각 섹션에서 다음 차이점을 적용합니다.

* [객체 타입의 백킹 제한된 뷰 만들기](#create-an-object-type-backing-dataset-or-restricted-view).
  * `Geoshape` 열 대신 `Geopoint` 열을 만듭니다.
* [객체 타입을 만들고 Gotham과 통합되는지 확인하기](#create-an-object-type-and-ensure-it-integrates-with-gotham).
  * 객체 타입 생성 창에서 `Geopoint`의 **Property**가 geopoint인지 확인합니다.
* [Gaia에서 객체를 생성할 수 있도록 액션 타입 구성하기](#create-and-configure-an-action-type-to-enable-object-creation-in-gaia).
  * 액션 타입의 **Parameters** 창에서 `Geopoint` 속성의 **Type**이 `Geopoint`인지 확인합니다.
* [`Gaia Geoshape Creatable` 인터페이스 구현하기](#implement-the-gaia-geoshape-creatable-interface).
  * `Gaia Geoshape Creatable` 인터페이스 대신 `Gaia Geopoint Creatable` 인터페이스를 검색합니다. enrollment에서 이를 대체하는 `Creatable Geopoint` 인터페이스를 쓸 수 있다면 그것을 검색합니다.
  * 온톨로지의 공유 속성 타입을 매핑할 때 `Geoshape` 속성 대신 `Geopoint` 속성에 대해 **Replace existing**을 선택합니다.

> **중간 요약**: 점 객체용 `Gaia Geopoint Creatable`(또는 `Creatable Geopoint`) 인터페이스의 구현 절차는 도형용과 같으며, `Geoshape` 자리에 `Geopoint`를 쓰는 것만 다릅니다.

<a id="create-an-object-type-that-implements-the-milstd-2525c-symbol-interface"></a>
## `MILSTD 2525C Symbol` 인터페이스를 구현하는 객체 타입 만들기 (Create an object type that implements the `MILSTD 2525C Symbol` interface)

**주의**: `Gaia Geoshape Creatable`, `Gaia Geopoint Creatable` 인터페이스와 달리, `MILSTD 2525C Symbol` 인터페이스를 구현하는 객체 타입은 **반드시** 제한된 뷰를 백킹 데이터소스로 써야 합니다.

**설명**: MIL-STD-2525C는 미국 국방부의 군사 부호(military symbology) 표준으로, 부대, 장비, 작전 지역 등을 지도에 표시하는 기호 체계를 정의합니다. 이 표준에서 각 기호는 SIDC(Symbol Identification Code)라는 문자열 코드로 식별되며, 아래에 나오는 `SIDC` 속성이 이 코드입니다. `Symbol Anchor Points`는 기호나 전술 그래픽을 지도에 배치하는 기준 좌표들입니다.

`MILSTD 2525C Symbol` 인터페이스를 구현하는 객체 타입을 만들려면, 위의 [`Gaia Geoshape Creatable` 인터페이스용 객체 타입 생성 지침](#create-an-object-type-that-implements-the-gaia-geoshape-creatable-interface)과 같은 단계를 따르되 각 섹션에서 다음 차이점을 적용합니다.

* [객체 타입의 백킹 제한된 뷰 만들기](#create-an-object-type-backing-dataset-or-restricted-view).
  * `Object ID`, `Classification`, `Title` 열*만* 만들면 됩니다.
* [객체 타입을 만들고 Gotham과 통합되는지 확인하기](#create-an-object-type-and-ensure-it-integrates-with-gotham).
  * 객체 타입 생성 창에서 `Object ID`를 **Primary key**로, `Title`을 **Title**로 설정합니다.

[객체 생성을 위한 액션 타입을 구성](#create-and-configure-an-action-type-to-enable-object-creation-in-gaia)할 때, **Next**를 선택하기 전에 **Create a new action type** 창에서 *최소한* `Symbol Anchor Points`와 `SIDC` 속성을 매핑해야 합니다. `Classification` 속성 매핑은 선택 사항이지만, 매핑하면 사용자가 Gaia 지도에서 만드는 객체에 등급 마킹이 적용되는 방식을 제어할 수 있습니다.

![MILSTD 2525C Symbol 인터페이스를 구현하는 객체 타입에 대한 Create a new action type 창이 표시되어 있으며, 사용자는 액션 입력으로 쓰일 액션 파라미터를 매핑할 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/configure-milsym-action-type-properties.png)

다음으로 넘어가기 전에 화면 위쪽의 초록색 **Save** 버튼을 눌러 변경 사항을 온톨로지에 점진적으로 게시합니다.

`Classification` 속성을 매핑했다면, 다음 단계에 따라 액션 타입의 **Rules**와 **Parameters**를 구성합니다.

1. 화면 왼쪽에서 **Rules**를 선택합니다.
2. `Classification` 속성 오른쪽의 화살표 아이콘을 선택해 **Configure parameter**를 엽니다.

![액션 타입 생성 창의 Rules 패널에 액션 타입 입력으로 매핑된 속성들이 표시되어 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/configure-milsym-action-type.png)

3. 객체 타입의 `Classification` 속성이 공유 속성 타입으로 채워져 있다면, **General** 섹션에서 **Disabled**를 켜서 생성되는 객체가 Gaia 지도로부터 등급 마킹을 자동으로 상속하도록 합니다. 생성 시 등급 마킹을 수동으로 설정하고 싶다면 **Disabled**를 켜지 않습니다.
4. **Set a parameter max classification** 아래의 **Add**를 선택해, 액션 타입의 최대 등급이 객체 타입의 최대 등급과 일치하도록 합니다.

![액션 폼의 Classification 파라미터가 표시되어 있으며, 사용자는 여기서 Type을 확인하고, 편집을 Disable하고, 최대 등급을 구성할 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/configure-milsym-classification-parameter.png)

화면 위쪽의 초록색 **Save** 버튼을 눌러 액션 타입을 온톨로지에 게시합니다.

**주의**: [액션에서 구조체(struct) 속성 사용은 현재 지원되지 않으므로](../04_structs/01_structs-overview.md#current-levels-of-support), `Speed Modifier (Z)`나 `Altitude/Depth Modifier (X)` 속성은 액션 타입 파라미터로 구성할 수 없습니다.

* [`Gaia Geoshape Creatable` 인터페이스 구현하기](#implement-the-gaia-geoshape-creatable-interface).
  * `Gaia Geoshape Creatable` 인터페이스 대신 `MILSTD 2525C Symbol` 인터페이스를 검색합니다.
  * 온톨로지의 공유 속성 타입을 매핑할 때 `Classification` 속성에는 **Replace existing**을, 나머지 속성에는 **Create edit-only property**를 선택합니다.

**설명**: **Create edit-only property**는 백킹 데이터소스에 대응하는 열이 없는 속성을 만든다는 의미로 읽을 수 있습니다. 이 경우 `SIDC`나 `Symbol Anchor Points` 값은 백킹 테이블의 열에서 오지 않고, 액션으로 기록된 편집(edit)으로만 채워집니다. 위에서 백킹 제한된 뷰에 `Object ID`, `Classification`, `Title` 열만 만들라고 한 이유가 여기에 있습니다.

> **중간 요약**: 군사 부호용 `MILSTD 2525C Symbol` 인터페이스는 반드시 제한된 뷰를 백킹 데이터소스로 쓰고, 액션 타입에 최소 `SIDC`와 `Symbol Anchor Points`를 매핑해야 합니다. `Classification`은 선택적으로 매핑해 등급 상속 여부와 최대 등급을 제어하며, 구조체 속성은 액션 파라미터로 쓸 수 없습니다.

<a id="use-interface-action-type-constraints-to-enable-automatic-discovery-of-object-types-supporting-object-creation"></a>
## 인터페이스 액션 타입 제약으로 객체 생성 지원 객체 타입을 자동 발견하게 하기 (Use interface action type constraints to enable automatic discovery of object types supporting object creation)

`Creatable Geoshape`, `Creatable Geopoint`, 또는 `MILSTD 2525C Symbol` 인터페이스를 구현한 객체 타입에 구성된 `Create or Modify` 액션을 사용해, 이 인터페이스들의 선택적 `Create or Modify` [인터페이스 액션 타입 제약](../../05_interfaces/07_interface-action-type-constraints.md)을 충족시킬 수 있습니다. 인터페이스 액션 타입 제약이 매핑되어 있으면, 객체 타입과 그 액션 타입을 [Gaia 관리자 애플리케이션 또는 Control Panel 확장 기능](#register-your-ontology-and-its-types)에 등록하지 *않아도* Gaia에서 온톨로지 객체를 만들 수 있습니다. 이 제약은 수동 등록 과정에서 생길 수 있는 오류를 줄여 주므로, 객체 타입과 액션 타입을 수동으로 등록하는 대신 인터페이스 액션 타입 제약을 충족시키는 방식을 써야 합니다.

**참고**: Gaia 관리자 애플리케이션과 Control Panel 확장 기능의 계획된 지원 중단(Planned deprecation of the Gaia admin application and Control Panel extension). Gaia 관리자 애플리케이션과 Control Panel 확장 기능은 2026년 11월에 [계획된 지원 중단](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/#planned-deprecation) 단계에 들어갑니다. 2026년 11월부터 **Foundry Object Creation Config**(관리자 애플리케이션) 섹션과 **Actions for Creating Objects From Gaia**(Control Panel 확장 기능) 섹션은 읽기 전용이 되며, 대신 인터페이스 액션 타입 제약을 사용하게 됩니다. 이미 수동으로 등록한 객체 타입의 마이그레이션에 대한 문의는 Palantir Support에 연락하세요.

대체된 `Gaia Geoshape Creatable`, `Gaia Geopoint Creatable`, `Gaia Geocreatable`, `Gaia Milsym Creatable` 인터페이스는 인터페이스 액션 타입 제약을 정의하지 *않습니다*. 대체된 인터페이스만 구현한 객체 타입은 인터페이스 액션 타입 제약을 충족시킬 수 없으므로, 객체 타입과 그 액션 타입을 Gaia 관리자 애플리케이션 또는 Control Panel 확장 기능에 수동으로 등록해야 합니다.

**설명**: 인터페이스 액션 타입 제약은 인터페이스가 속성뿐 아니라 "이 인터페이스를 구현하는 객체 타입은 이런 모양의 액션도 제공해야 한다"는 요구까지 선언하는 기능입니다. 인터페이스에 메서드 시그니처를 선언하고 구현 클래스가 그 메서드를 채우는 것과 같은 구조입니다. Gaia는 인터페이스를 통해 "객체를 만들 때 호출할 액션"을 바로 알아낼 수 있으므로, 별도의 등록 표에 객체 타입 RID와 액션 타입 RID 쌍을 손으로 적어 둘 필요가 없어집니다.

<a id="fulfill-an-interface-action-type-constraint-on-your-object-type"></a>
### 객체 타입에서 인터페이스 액션 타입 제약 충족시키기 (Fulfill an interface action type constraint on your object type)

Ontology Manager에서 객체 타입을 열고 다음 사전 조건을 확인합니다.

* 객체 타입이 [인터페이스 액션 타입 제약을 지원하는 인터페이스](#use-interface-action-type-constraints-to-enable-automatic-discovery-of-object-types-supporting-object-creation)를 구현해야 합니다. 객체 타입이 지원 인터페이스를 둘 이상 구현한다면, 제약을 충족시키기 전에 [액션 타입 구성 방식](#choose-your-action-type-configuration)을 검토하세요.
* 객체 타입에 `Create or Modify` 액션 타입이 구성되어 있어서, Gaia에서 새 객체를 만들 수 *있고* 기존 객체도 수정할 수 있어야 합니다.

그다음 아래 단계에 따라 인터페이스 액션 타입 제약을 충족시킵니다.

1. 객체 타입의 왼쪽 패널에서 **Interfaces**를 선택한 다음 **Actions** 탭을 선택합니다.
2. `Create or Modify` 액션 타입을 인터페이스의 액션 타입 제약에 매핑합니다.
3. **Settings** 아이콘을 선택해 제약의 파라미터를 액션 타입의 파라미터에 매핑합니다. `Creatable Geopoint` 인터페이스는 `Geopoint` 파라미터를, `Creatable Geoshape` 인터페이스는 `Geoshape` 파라미터를, `MILSTD 2525C Symbol` 인터페이스는 최소한 `Symbol Anchor Points`와 `SIDC` 파라미터를 매핑합니다. <br>
   ![인터페이스 액션 타입 제약 파라미터를 구성합니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/configure-iatc-parameters.png) <br>
4. 화면 위쪽의 초록색 **Save** 버튼을 눌러 변경 사항을 온톨로지에 게시합니다.
5. 이전에 이 객체 타입을 수동으로 등록했다면, 관리자 애플리케이션 또는 Control Panel 확장 기능의 **Foundry Object Creation Config** 패널에서 해당 객체 타입과 액션 타입 RID 항목을 찾아 삭제하고 변경 사항을 저장합니다.
6. Gaia를 새로 고치고 **Object type** 드롭다운 메뉴에 객체 타입이 나타나는지 확인합니다.

<a id="choose-your-action-type-configuration"></a>
### 액션 타입 구성 방식 고르기 (Choose your action type configuration)

객체 타입이 지원 인터페이스를 여러 개 구현한다면, 제약마다 *하나의* 액션 타입을 공유하거나 *별도의* 액션 타입을 둘 수 있습니다.

* **단일 액션 타입(권장):** 객체 타입이 구현하는 모든 인터페이스의 제약에 `Create or Modify` 액션 타입 하나를 매핑합니다. 구성이 가장 적고 가장 유연한 방식입니다. 액션 타입 하나가 모든 인터페이스를 담당하므로, 액션 폼에 모든 생성 흐름에 해당하지는 않는 선택적 파라미터가 포함될 수 있습니다.

* **별도 액션 타입:** 객체 타입이 구현하는 인터페이스마다 `Create or Modify` 액션 타입을 하나씩 정의하고, 각 액션 타입을 해당 인터페이스의 제약에 매핑합니다. 각 액션 폼에는 그 인터페이스에 관련된 파라미터만 들어가므로 사용자가 보는 선택적 파라미터가 줄어듭니다. 대신 구성 작업이 더 많습니다.

**설명**: 예를 들어 `Site` 객체 타입이 `Creatable Geopoint`와 `Creatable Geoshape`를 모두 구현한다고 합시다. 단일 액션 타입 방식에서는 `Geopoint`와 `Geoshape` 파라미터를 모두 가진 액션 하나를 두고, 점을 찍을 때는 `Geoshape`이 빈 채로, 도형을 그릴 때는 `Geopoint`가 빈 채로 제출됩니다. 별도 액션 타입 방식에서는 점용 액션과 도형용 액션을 따로 두어 각 폼에 필요한 파라미터만 남깁니다.

> **중간 요약**: 새 인터페이스(`Creatable Geoshape`, `Creatable Geopoint`, `MILSTD 2525C Symbol`)는 `Create or Modify` 액션을 인터페이스 액션 타입 제약에 매핑해 두면 Gaia가 객체 타입을 자동으로 발견하므로 수동 등록이 필요 없습니다. 예전 인터페이스는 이 제약을 지원하지 않아 수동 등록이 필요하며, 수동 등록 화면은 2026년 11월부터 읽기 전용이 됩니다.

<a id="register-your-ontology-and-its-types"></a>
## 온톨로지와 타입 등록하기 (Register your ontology and its types)

이제 `Gaia Geoshape Creatable`, `Gaia Geopoint Creatable`, `MILSTD 2525C Symbol` 인터페이스를 구현한 객체 타입들이 있고, 각 객체 타입에는 사용자가 Gaia 지도에서 그린 도형, 찍은 점, 구성한 전술 그래픽으로 만드는 객체를 구성할 수 있게 하는 액션 타입이 함께 있습니다. 다음으로 enrollment에 따라 Gaia의 관리자 애플리케이션 또는 [Control Panel](https://www.palantir.com/docs/foundry/administration/control-panel/) 확장 기능에 온톨로지, 객체 타입, 액션 타입을 등록합니다.

**참고**: Gaia의 관리자 애플리케이션에 접근하려면 플랫폼 관리자여야 합니다. Gaia의 Control Panel 확장 기능에 접근하려면 **Organization administrator** 역할이 부여되어 있어야 합니다.
어느 쪽에도 접근할 수 없다면 관리자 애플리케이션 또는 Control Panel 확장 기능 접근에 대해 Palantir Support에 문의하세요.

온톨로지, 객체 타입, 액션 타입을 등록하려면 Gaia의 관리자 애플리케이션 또는 Control Panel 확장 기능을 열고 다음 단계를 따릅니다.

1. **Ontology Config**(관리자 애플리케이션) 또는 **Ontology**(Control Panel 확장 기능) 패널을 찾아 온톨로지 구성을 확인합니다. 온톨로지가 구성되어 있지 않다면 패널 왼쪽의 토글을 선택해 **Ontology Config**/**Ontology** 를 `overridden`(관리자 애플리케이션) 또는 `Override`(Control Panel 확장 기능)로 설정합니다.
2. 온톨로지의 RID와 API 이름을 **Ontology RID**와 **API Name** 텍스트 상자에 입력합니다. 온톨로지의 RID와 API 이름을 찾아 복사하려면 Ontology Manager로 이동해 왼쪽 패널 맨 아래의 **Ontology configuration**을 선택해 **Ontology metadata** 창을 엽니다.

![Gaia 관리자 애플리케이션과 Control Panel 확장 기능의 Ontology Config 패널입니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/gaia-admin-app-ontology-config.png)

**설명**: RID(Resource Identifier)는 Foundry에서 온톨로지, 객체 타입, 액션 타입 같은 리소스 하나하나를 전역적으로 유일하게 식별하는 문자열 ID입니다. 데이터베이스의 기본 키처럼, 이름이 바뀌어도 RID는 그대로 유지되므로 시스템 간 참조에 사용됩니다.

**참고**: 객체 타입이 `Creatable Geoshape`, `Creatable Geopoint`, `MILSTD 2525C Symbol` 인터페이스 중 하나를 구현한다면 아래의 나머지 단계는 건너뛰세요. Gaia는 이러한 객체 타입을 [충족된 인터페이스 액션 타입 제약](#use-interface-action-type-constraints-to-enable-automatic-discovery-of-object-types-supporting-object-creation)을 통해 자동으로 객체 생성에 사용할 수 있게 하므로, **Foundry Object Creation Config** 패널에 수동으로 입력할 필요가 없습니다.

1. **Foundry Object Creation Config** 패널을 찾아 **Show**(관리자 애플리케이션) 또는 **Override**(Control Panel 확장 기능)를 선택합니다.
2. enrollment의 기존 객체 타입 및 액션 타입 목록 맨 아래에서 **Add**를 선택합니다.
3. 세 객체 타입과 각 지원 액션 타입의 RID를 복사해, 세 개의 **Object type rid** 텍스트 상자와 **Action type rid** 텍스트 상자에 각각 붙여 넣습니다.
4. 오른쪽 위 리본의 **Preview and save**(관리자 애플리케이션) 또는 오른쪽 아래의 **Save for {Organization}**(Control Panel 확장 기능)을 선택합니다.

![Gaia 관리자 애플리케이션과 Control Panel 확장 기능의 Foundry Object Creation Config 패널입니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/gaia-admin-app-foundry-object-creation-config.png)

객체 타입의 RID는 Ontology Manager의 **Overview** 창에서 확인할 수 있습니다. 클립보드 아이콘을 선택하면 RID가 복사됩니다. 또한 **Overview** 창의 **Action types** 섹션에서 **Create {object type name}** 을 선택하면 액션 타입의 RID를 확인할 수 있으며, 이 RID도 클립보드 아이콘으로 복사할 수 있습니다.

![Ontology Manager의 Overview 창에서 객체 타입과 액션 타입의 RID를 모두 복사할 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/combined-object-action-rid-copy.png)

다음으로 Gotham의 Gaia 애플리케이션을 열고, **Add to map** 메뉴를 사용해 지도에서 그린 도형, 찍은 점, 구성한 전술 그래픽으로 객체를 만듭니다.

> **중간 요약**: 관리자 애플리케이션 또는 Control Panel 확장 기능에서 온톨로지 RID와 API 이름을 등록합니다. 예전 인터페이스를 쓰는 객체 타입은 추가로 객체 타입 RID와 액션 타입 RID 쌍을 **Foundry Object Creation Config** 에 등록해야 하고, 새 인터페이스를 쓰는 객체 타입은 이 단계가 필요 없습니다.

<a id="entry-points-to-create-objects-on-your-gaia-map"></a>
## Gaia 지도에서 객체를 만드는 진입점 (Entry points to create objects on your Gaia map)

Gaia는 지도에서 객체를 하나 또는 여러 개 만들 때 쓸 수 있는 서로 다른 진입점 두 가지를 제공하며, 어느 진입점을 쓰느냐에 따라 **Object type** 드롭다운 메뉴에 표시되는 객체 타입 목록이 달라집니다.

* **객체 타입을 먼저 선택하기:** Gaia 툴바의 드롭다운 메뉴는 지원 인터페이스를 구현한 모든 객체 타입을 나열합니다. 지원 인터페이스에는 `Creatable Geoshape`, `Creatable Geopoint`, `Gaia Geoshape Creatable`, `Gaia Geopoint Creatable`, `MILSTD 2525C Symbol` 인터페이스가 있습니다. 객체 타입을 선택하면 Gaia는 사용 가능한 그리기 도구를 그 객체 타입이 구현한 인터페이스와 호환되는 도구*만* 남도록 걸러 냅니다. 예를 들어 `Gaia Geoshape Creatable` 인터페이스를 구현한 객체 타입을 선택하면 도형 그리기 도구만 표시됩니다. 그런 다음 그리기 도구를 선택하면, Gaia는 **Object type** 드롭다운 메뉴에 그 객체 타입이 이미 채워진 상태로 왼쪽 패널을 엽니다.

**팁**: 하나의 객체 타입이 둘 이상의 인터페이스를 구현할 수 있습니다. 예를 들어 어떤 객체 타입이 `Gaia Geopoint Creatable`과 `Gaia Geoshape Creatable` 인터페이스를 모두 구현한다면, 툴바에서 그 객체 타입을 선택했을 때 점 기호와 모든 도형 그리기 도구가 표시되고 기호 **Search** 메뉴는 걸러집니다.

* **그리기 도구를 먼저 선택하기:** 객체 타입보다 그리기 도구를 먼저 선택하면, Gaia는 객체 타입이 미리 선택되지 않은 상태로 왼쪽 패널을 엽니다. 이 경우 **Object type** 드롭다운 메뉴에는 선택한 도구에 맞는 인터페이스를 구현한 객체 타입만 나열됩니다. 예를 들어 점 기호를 선택하면 `Gaia Geopoint Creatable` 인터페이스를 구현한 객체 타입만 표시됩니다.

> **중간 요약**: 객체 타입을 먼저 고르면 그 타입에 맞는 그리기 도구만 남고, 그리기 도구를 먼저 고르면 그 도구에 맞는 인터페이스를 구현한 객체 타입만 남습니다. 어느 쪽이든 인터페이스가 객체 타입과 그리기 도구를 짝지어 주는 기준입니다.

<a id="draw-a-new-shape-on-your-gaia-map-and-tag-it-to-an-object-type"></a>
### Gaia 지도에 새 도형을 그리고 객체 타입으로 태그하기 (Draw a new shape on your Gaia map and tag it to an object type)

**주의**: 국제 날짜 변경선 관련 현재 제한 사항(Current limitations around the International Date Line). Gaia 지도에서 180도 경선(반자오선, antimeridian)을 가로지르는 지도 주석(annotation)은 만들 수 있지만, 이를 가로지르는 도형을 Foundry 객체로 태그해 그릴 수는 없습니다.
주석 생성, 렌더링, 또는 Gotham에 있는 Gaia의 추가 문서에 대한 문의는 Palantir Support에 연락하세요.

시작하기 전에 [객체 생성 진입점](#entry-points-to-create-objects-on-your-gaia-map)을 검토해, 선택한 객체 타입과 그리기 도구가 사용 가능한 객체 타입을 어떻게 결정하는지 이해하세요.

Gaia 지도가 열린 상태에서, 지도 왼쪽 위 영역의 메뉴에서 객체 아이콘을 선택해 **Draw annotation** 모드에서 **Create object** 모드로 전환합니다.

![Gaia의 툴바가 표시되어 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/select-object-map-tool-bar.png)

다음으로 같은 메뉴의 오른쪽에서 그릴 도형을 선택합니다. 도형을 다 그리면 Gaia의 왼쪽 패널에 **Create shape** 창이 나타납니다. 다음 단계에 따라 도형을 구성하고 온톨로지에 객체로 저장합니다.

1. **Object type** 드롭다운 메뉴에서 객체 타입을 검색해 선택합니다. 지도 캔버스의 툴바 드롭다운 메뉴에서 이미 객체 타입을 선택했다면, Gaia가 **Create shape** 의 드롭다운 메뉴를 그 값으로 자동으로 채웁니다.
2. **Finish**를 선택하기 전에 액션 폼에서 `Category`, `Name` 같은 객체의 필수 필드를 채웁니다.

![Gaia 지도에 다각형이 그려져 있으며, 사용자는 이를 객체 타입에 지오태그할 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/draw-polygon.png)

도형을 객체로 저장하면 Gaia 왼쪽 패널의 **Layers** 중 하나로 표시됩니다. 객체 이름을 선택하면 화면 오른쪽에 **Selection** 패널이 열리고, 여기서 객체의 속성을 보고 모양을 사용자 지정할 수 있습니다.

![사용자는 도형을 그린 후 Gaia 지도에서 그 도형의 객체 데이터를 볼 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/gaia-map-drawn-object-view.png)

Foundry의 [Object Explorer](../../../05_applications/01_object-explorer/01_overview.md)에서도 객체를 볼 수 있습니다.

![사용자는 그린 객체를 Foundry의 Object Explorer에서 볼 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/view-drawn-object-in-foundry-oe.png)

**설명**: 2단계의 **Finish**는 앞에서 만든 `Modify or create object` 액션을 실행하는 버튼입니다. 즉 Gaia가 그린 도형을 `Geoshape` 파라미터로, 사용자가 입력한 `Name`, `Category`를 나머지 파라미터로 넣어 액션을 제출하고, 그 결과 객체 타입에 객체 하나가 추가됩니다. 같은 객체를 Object Explorer에서도 볼 수 있는 것은 Gaia와 Foundry가 같은 온톨로지 데이터를 보고 있기 때문입니다.

<a id="edit-an-existing-shape-object"></a>
#### 기존 도형 객체 편집하기 (Edit an existing shape object)

기존 도형 객체를 편집하려면 왼쪽 패널에서 객체 위에 커서를 올리고 **Edit selection**을 선택해 **Edit shape** 창을 엽니다. 지도에서 객체를 더블클릭해도 이 창을 열 수 있습니다.

![사용자는 연필 아이콘을 선택해 왼쪽 패널에 Edit shape 창을 열어 Gaia 지도의 객체를 편집할 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/edit-object.png)

꼭짓점(vertex)을 선택해 끌면 도형을 조정할 수 있고, 도형 경계 안의 점을 선택해 끌면 도형을 지도의 다른 위치로 옮길 수 있습니다. 변경을 마쳤으면 **Edit shape** 창 아래쪽의 **Finish**를 선택합니다.

<a id="drop-a-new-point-on-your-gaia-map-and-tag-it-to-an-object-type"></a>
### Gaia 지도에 새 점을 찍고 객체 타입으로 태그하기 (Drop a new point on your Gaia map and tag it to an object type)

시작하기 전에 [객체 생성 진입점](#entry-points-to-create-objects-on-your-gaia-map)을 검토해, 선택한 객체 타입과 그리기 도구가 사용 가능한 객체 타입을 어떻게 결정하는지 이해하세요.

Gaia 지도가 열린 상태에서 아래쪽 화살표를 선택해 기호 **Search** 메뉴를 표시하고, 지도 어디에든 놓을 수 있는 기호를 고릅니다. 사용 가능한 **Tactical Graphics** 기호 중 하나를 선택하면 [`MILSTD 2525C Symbol` 인터페이스](#create-an-object-type-that-implements-the-milstd-2525c-symbol-interface)를 구현한 객체 타입의 객체만 만들 수 있습니다. Gaia는 지도의 좌표계 설정에 따라 **Coordinates** 입력 상자를 자동으로 채웁니다.

![Gaia 툴바의 기호 선택 화면이 표시되어 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/create-geopoint-from-tool-bar.png)

**팁**: 기본 좌표계를 바꾸려면 Gaia 위쪽 리본에서 **File** > **Preferences** > **Coordinate system**을 선택합니다.

Gaia 왼쪽 패널에 **Create symbol** 창이 나타나며, 여기서 `Gaia Geopoint Creatable` 인터페이스를 구현한 객체 타입을 검색해 선택할 수 있습니다. 다음으로 원하면 지오포인트의 **Bearing (mag)**(자북 기준 방위각)을 조정한 뒤 객체의 **Title**을 입력합니다. **Finish**를 선택하면 놓은 기호가 온톨로지에 객체로 저장됩니다.

지오포인트를 객체로 저장한 뒤에는 [지도에 그린 도형과 같은 방식으로](#draw-a-new-shape-on-your-gaia-map-and-tag-it-to-an-object-type) 새 지도 레이어와 상호작용하고 Foundry의 Object Explorer에서 객체를 볼 수 있습니다.

<a id="edit-an-existing-geopoint-object"></a>
#### 기존 지오포인트 객체 편집하기 (Edit an existing geopoint object)

기존 지오포인트 객체는 [지도에 그린 도형과 같은 방식으로](#edit-an-existing-shape-object) 편집할 수 있습니다.

<a id="configure-a-tactical-graphic-on-your-gaia-map-and-tag-it-to-an-object-type"></a>
### Gaia 지도에서 전술 그래픽을 구성하고 객체 타입으로 태그하기 (Configure a tactical graphic on your Gaia map and tag it to an object type)

**주의**: 전술 그래픽을 객체 타입으로 태그하려면 Foundry enrollment에 MRS가 있어야 합니다. MRS 설치나 기능에 대한 문의는 Palantir Support에 연락하세요.

시작하기 전에 [객체 생성 진입점](#entry-points-to-create-objects-on-your-gaia-map)을 검토해, 선택한 객체 타입과 그리기 도구가 사용 가능한 객체 타입을 어떻게 결정하는지 이해하세요.

[새 지오포인트를 추가해 객체로 태그하는 것과 비슷하게](#drop-a-new-point-on-your-gaia-map-and-tag-it-to-an-object-type), 아래쪽 화살표를 선택해 기호 **Search** 메뉴를 표시하고, 지도 어디에든 놓을 수 있는 전술 그래픽을 고릅니다. **Search symbols...** 입력 상자에 원하는 전술 그래픽의 이름(예: `Brigade Support Area`)을 입력합니다.

![Gaia의 기호 검색 창에서 사용자는 지도에 추가할 기호나 전술 그래픽을 검색할 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/search-for-tactical-graphic.png)

Gaia 왼쪽 패널에 **Create symbol** 창이 나타나며, 위의 [도형 생성 지침](#draw-a-new-shape-on-your-gaia-map-and-tag-it-to-an-object-type)과 같은 방식으로 전술 그래픽을 지도에 추가하고 객체 타입으로 태그할 수 있습니다.

![Gaia 지도의 캔버스에 전술 그래픽이 그려져 저장된 모습이 표시되어 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/draw-tactical-graphic.png)

<a id="edit-an-existing-tactical-graphic-object"></a>
#### 기존 전술 그래픽 객체 편집하기 (Edit an existing tactical graphic object)

기존 전술 그래픽 객체는 [위의 도형 객체 편집 지침](#edit-an-existing-shape-object)을 따라 편집할 수 있습니다.

> **중간 요약**: **Create object** 모드에서 도형을 그리거나 기호를 놓은 뒤, 객체 타입을 고르고 액션 폼을 채워 **Finish**를 누르면 객체가 저장됩니다. 점은 `Gaia Geopoint Creatable` 계열, 전술 그래픽은 `MILSTD 2525C Symbol` 인터페이스를 구현한 객체 타입으로만 저장할 수 있고, 전술 그래픽에는 MRS가 필요합니다. 편집 방식은 세 종류 모두 같습니다.

<a id="create-new-objects-in-bulk"></a>
### 새 객체를 대량으로 만들기 (Create new objects in bulk)

**Create shape** 또는 **Create symbol** 패널 왼쪽 아래의 **Bulk create**를 선택하면 지도에 **Bulk create objects** 표가 열립니다.

![Gaia의 Create shape 또는 Create symbol 왼쪽 패널에서 Bulk create를 선택합니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/select-bulk-create-in-gaia.png)

각 행은 Gaia 지도에 하나의 지오메트리(geometry)를 객체로 렌더링하는 별도의 액션 제출 하나를 나타내고, 각 열은 액션 파라미터 하나를 나타냅니다. 한 표에서 한 번에 최대 5,000개의 객체를 만들 수 있습니다.

![Gaia 지도 아래쪽에 Bulk create objects 표가 표시되어 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/bulk-object-creation-table.png)

**설명**: 이 표는 행마다 액션을 한 번씩 호출하는 배치 입력 화면입니다. 예를 들어 열이 `Geoshape`, `Name`, `Category`이고 행이 3개라면, 제출 시 액션이 세 번 실행되어 객체 3개가 만들어집니다. 함수 호출로 보면 `create(geoshape, name, category)`를 인자 목록 3개로 각각 호출하는 것입니다.

Gaia는 지도에 처음 그린 도형이나 처음 놓은 기호로 표의 첫 행을 채웁니다. 도형이나 기호를 더 추가하려면 **Add row**를 선택합니다. 또는 표 아래쪽의 빈 행에 있는 빈 셀 위에 커서를 올리고 선택해도 됩니다. 객체의 `geoshape` 또는 `geopoint` 셀을 선택하면 해당하는 **Editing geoshape** 또는 **Editing geopoint** 패널이 열립니다. 지도에 새 도형을 그리거나 새 기호를 놓은 다음 **Save**를 선택합니다.

![geoshape 또는 geopoint 속성의 셀을 선택해 새 도형을 그리거나 새 기호를 놓아 Bulk create objects 표에 추가합니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/bulk-add-additional-shape-symbol.png)

`MILSTD 2525C Symbol` 인터페이스로 전술 그래픽이나 군사 부호를 만들려면, 생성 액션에 `SIDC`와 `Symbol Anchor Points`를 구성합니다. 원하면 Gaia가 자동으로 채울 추가 스칼라 수식자(scalar modifier)를 포함할 수도 있습니다. 기호 선택기에서 전술 그래픽이나 군사 부호를 선택합니다. Gaia가 객체의 `SIDC` 값을 설정하고 관련 좌표 편집기를 엽니다. 지도에 도형을 그려 `Symbol Anchor Points` 속성을 채웁니다.

![군사 부호를 대량으로 만들려면 액션 구성에 SIDC와 Symbol Anchor Points 속성이 필요합니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/milsym-bulk-shape-creation.png)

단일 점(single-point) 전술 그래픽을 선택하면, Gaia는 도형을 그릴 때 쓰는 배열 대신 기호 기준점(anchor point) 하나로 `Symbol Anchor Points` 속성을 채웁니다.

![단일 점 군사 부호를 대량으로 만들면 Symbol Anchor Points 속성에 좌표 하나가 설정됩니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/bulk-create-single-point-symbol.png)

작업을 마쳤으면 표 오른쪽 아래의 **Submit**을 선택해 새 객체를 만듭니다. 저장하지 않고 **Bulk create objects** 표를 나가려면 언제든 **Return to single object**를 선택합니다. 제거할 여러 행을 강조 표시하려면 표 맨 왼쪽의 인덱스 번호를 선택합니다. 그런 다음 `Cmd+Up`/`Cmd+Down`(macOS) 또는 `Ctrl+Up`/`Ctrl+Down`(Windows)을 누릅니다. 또한 복사할 값 위에서 `Cmd+C`(macOS)/`Ctrl+C`(Windows)를 누른 뒤 대상 행에서 `Cmd+V`(macOS)/`Ctrl+V`(Windows)를 눌러, 행 전체를 복사해 붙여 넣거나 한 행의 값을 다른 행으로 옮길 수 있습니다.

<a id="promote-an-annotation-to-an-object"></a>
### 주석을 객체로 승격하기 (Promote an annotation to an object)

Gaia에서 *주석(annotation)* 은 현재 지도에만 존재하는 도형, 점, 기호입니다. 지도의 주석을 온톨로지의 객체로 승격(promote)하면, 그 객체 타입에 접근할 수 있는 다른 사용자가 만든 다른 지도에서도 사용할 수 있습니다. 승격해도 지도에서 주석이 삭제되지는 *않습니다*. 대신 Gaia는 새로 만들어진 객체를 별도 레이어에 표시하고, 원래 주석과 그 원본 레이어는 둘 다 지도에 남아 있습니다. 객체를 만든 뒤 원래 주석이 더 이상 필요 없으면 숨기거나 제거할 수 있습니다.

**설명**: 주석과 객체의 차이는 데이터가 어디에 저장되느냐입니다. 주석은 해당 지도 문서 안에만 저장되는 지역 데이터이고, 객체는 온톨로지(공유 데이터베이스)의 행으로 저장되어 다른 지도, Object Explorer, 다른 애플리케이션에서도 조회할 수 있습니다. 승격은 주석의 지오메트리를 입력으로 생성 액션을 실행해 온톨로지에 새 행을 만드는 작업입니다.

기존 주석을 객체로 태그하려면, 지도에서 주석을 더블클릭하거나 왼쪽 패널 **Layers** 탭에서 주석의 연필 아이콘 위에 커서를 올려 도형, 점, 또는 기호 편집 창을 엽니다. 그다음 **Promote to object**를 선택하고, **Object type** 드롭다운 메뉴에서 객체 타입을 고른 뒤, 도형, 점, 또는 기호 편집 창에서 액션 폼을 채웁니다.

![Gaia 지도에 사용자가 왼쪽 패널을 통해 객체로 승격하는 주석이 표시되어 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/promote-annotation.png)

온톨로지*에서* Gotham*으로* 데이터를 추가하는 다양한 방법에 대해 더 알아보려면 기존 [지리 공간 데이터 통합 문서](https://www.palantir.com/docs/foundry/geospatial/add-ontology-data-to-gaia/)를 참고하세요.

<a id="promote-existing-annotations-in-bulk"></a>
#### 기존 주석을 대량으로 승격하기 (Promote existing annotations in bulk)

Gaia에서는 다음 주석 유형을 대량으로 객체로 승격할 수 있습니다.

* 점
* 도형(다각형, 사각형, 선, 거리 고리(range ring) 포함)
* 군사 부호
* 단일 점 및 다중 점 전술 그래픽

다음 지침에 따라 지도의 여러 주석을 온톨로지의 객체로 승격합니다.

1. 지도에서 또는 왼쪽 패널의 **Layers** 탭에서 지원되는 주석을 두 개 이상 선택합니다.
2. 화면 오른쪽의 **Selection** 패널에서 **Create objects**를 선택합니다. <br>
   ![오른쪽 Selection 패널에서 Create objects를 선택해 주석을 대량으로 지정합니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/create-objects-from-annotations.png) <br>
3. 관련 객체 타입을 검색해 선택하면 **Bulk create objects** 표가 열립니다.
4. 액션 표에 미리 채워진 행(주석의 위치, 도형, 기준점 등)을 검토합니다.
5. 액션 폼에 구성된 나머지 필수 필드를 채우고 **Submit**을 선택합니다.

![Bulk create objects 표에 객체로 만들 주석 두 개가 표시되어 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/bulk-create-objects-from-annotations.png)

Gaia는 대량 승격에 호환되는 객체 타입과 호환되지 않는 객체 타입의 목록을 표시하며, 목록의 객체 타입 위에 커서를 올리면 호환되지 않는 이유를 설명하는 툴팁이 나타납니다. 이 목록은 **Selection** 패널과 **Bulk create objects** 표 *모두에* 표시됩니다.

![대량 생성 흐름에서 호환되는 객체 타입과 호환되지 않는 객체 타입이 나열되며, 부적격 사유를 설명하는 툴팁이 함께 표시됩니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/bulk-create-incompatible-warning.png)

**참고**: 액션 타입은 선택한 모든 주석 유형을 지원해야 합니다(Action types must support all selected annotation types). 객체 타입이 승격 옵션으로 나타나려면, 그 액션 타입이 선택 항목에 대응하는 모든 인터페이스의 파라미터를 포함해야 합니다. 예를 들어 선택 항목에 지오포인트, 지오셰이프, 전술 그래픽이 포함되어 있다면, 객체의 액션 타입은 각 인터페이스의 `Geopoint`, `Geoshape`, `SIDC`, `Symbol Anchor Point` 파라미터를 최소한 모두 가지고 있어야 합니다.

> **중간 요약**: **Bulk create** 표에서는 행 하나가 액션 제출 하나에 해당하며 한 번에 최대 5,000개 객체를 만들 수 있습니다. 지도에만 있던 주석은 **Promote to object**로 온톨로지 객체로 승격할 수 있고, 여러 주석을 한꺼번에 승격하려면 액션 타입이 선택한 모든 주석 유형의 파라미터를 가져야 합니다.

<a id="troubleshoot-bulk-object-creation-and-promotion"></a>
### 대량 객체 생성과 승격 문제 해결 (Troubleshoot bulk object creation and promotion)

아래 섹션은 객체를 대량으로 만들거나 주석을 대량으로 승격할 때 만날 수 있는 오류를 해결하는 요령을 담고 있습니다.

<a id="the-bulk-create-button-does-not-appear"></a>
#### **Bulk create** 버튼이 나타나지 않음 (The **Bulk create** button does not appear)

**Create shape** 또는 **Create symbol** 창 왼쪽 아래에 **Bulk create** 버튼이 나타나지 않는다면 다음을 확인합니다.

* **Draw annotation** 모드가 아니라 **Create object** 모드에서 작업하고 있습니다.
* 지도에 대한 `Edit` 권한이 있습니다.
* 선택한 객체 타입이 `Gaia Geopoint Creatable`, `Gaia Geoshape Creatable`, `MILSTD 2525C Symbol` 인터페이스 중 최소 하나를 구현합니다.
* [액션을 실행하는 데 필요한 권한](../../03_action-types/19_permissions.md)이 있습니다.
* 객체를 만드는 액션에 [구조체](../04_structs/01_structs-overview.md) 파라미터가 없습니다. 예를 들어 `MILSTD 2525C Symbol` 인터페이스의 `Speed Modifier (Z)`와 `Altitude/Depth Modifier` 속성은 구조체이므로 대량 생성 표에서 지원되지 않습니다.

위 항목을 확인했는데도 단일 객체 생성은 되고 대량 생성은 되지 않는다면, Palantir Support에 연락해 여러분의 enrollment에서 대량 객체 생성이 활성화되어 있는지 확인하세요.

<a id="the-bulk-create-objects-table-reports-that-the-tabular-view-is-unavailable"></a>
#### **Bulk create objects** 표에서 표 형식 보기를 사용할 수 없다고 표시됨 (The **Bulk create objects** table reports that the tabular view is unavailable)

`Create` 액션에 액션 표가 표현할 수 없는 규칙이나 파라미터 타입이 포함되어 있으면 이런 일이 생길 수 있습니다. 예를 들어 구조체 파라미터를 가진 액션은 지원되지 않습니다. 지원되는 파라미터 타입만 사용하는 별도의 `Modify or create` 액션을 구성하세요.

<a id="gaia-does-not-prefill-geometry-or-symbol-values"></a>
#### Gaia가 지오메트리나 기호 값을 미리 채우지 않음 (Gaia does not prefill geometry or symbol values)

객체 타입의 인터페이스 속성이 객체 속성에 매핑되어 있는지, 그리고 충족된 액션에 해당 속성들에 대한 파라미터가 있는지 확인합니다. 전술 그래픽의 경우 `SIDC`와 `Symbol Anchor Points`가 같은 액션에 속해야 합니다. 그다음 객체 타입 RID와 액션 RID가 [Gaia 관리자 애플리케이션 또는 Control Panel 확장 기능](#register-your-ontology-and-its-types)에 등록되어 있는지 확인합니다.

<a id="gaia-reports-invalid-or-excess-selections"></a>
#### Gaia가 잘못되었거나 초과된 선택 항목을 보고함 (Gaia reports invalid or excess selections)

폴더, 조각(fragment), 주석이 아닌 레이어처럼 지원되지 않는 항목을 표에서 제거합니다. 선택 항목이 적격 항목 5,000개를 넘는다면, 제공되는 선택 해제 동작을 사용하거나 더 작은 그룹을 선택해 별도의 배치로 제출합니다.

<a id="the-action-submits-but-the-object-does-not-appear-on-the-map"></a>
#### 액션은 제출되었지만 객체가 지도에 나타나지 않음 (The action submits but the object does not appear on the map)

먼저 [Insight](https://www.palantir.com/docs/foundry/insight/overview/)에서 객체 타입을 열고 이름이나 다른 속성 값으로 객체를 하나 이상 검색해, 액션이 실제로 객체를 만들었는지 확인합니다. 다음으로 지도에서 해당 객체 타입의 객체를 담는 대상 레이어를 확인한 뒤, 지도와 객체 타입의 보안 마킹이 서로 호환되는지 검증합니다.

<a id="submission-fails-without-a-clear-cell-error"></a>
#### 명확한 셀 오류 없이 제출이 실패함 (Submission fails without a clear cell error)

액션은 표가 제출 전에 감지하지 못하는 제약을 강제할 수 있습니다. 액션의 필수 파라미터, 좌표와 지오메트리의 유효성, 마킹 한도를 확인하고, 액션 권한을 검증합니다.

**설명**: 마지막 항목은 표의 클라이언트 측 검증과 서버 측 검증이 서로 다를 수 있다는 뜻입니다. 표는 셀 타입 정도만 미리 확인하고, 제출 조건(submission criteria)이나 권한 검사 같은 규칙은 액션이 서버에서 실행될 때 비로소 평가되므로, 그 단계에서 실패하면 특정 셀을 가리키는 오류 없이 제출 자체가 실패할 수 있습니다.

> **중간 요약**: 대량 생성 버튼이 없으면 모드, 지도 편집 권한, 인터페이스 구현, 액션 권한, 구조체 파라미터 여부를 확인합니다. 값이 미리 채워지지 않거나 객체가 보이지 않거나 제출이 실패하면 속성 매핑, RID 등록, 레이어와 보안 마킹, 액션의 제약 조건을 차례로 점검합니다.

## 정리

- Gaia 지도의 도형, 점, 전술 그래픽은 각각 `Creatable Geoshape`, `Creatable Geopoint`, `MILSTD 2525C Symbol` 인터페이스를 구현한 객체 타입의 객체로 저장할 수 있으며, Foundry와 Gotham이 모두 필요합니다.
- 준비 순서는 백킹 데이터셋 또는 제한된 뷰 만들기, 객체 타입 만들기(자동 생성 기본 키, 공유 속성 지정), `Modify or create object` 액션 타입 구성, 인터페이스 구현입니다.
- 새 인터페이스는 인터페이스 액션 타입 제약으로 Gaia가 객체 타입을 자동 발견하므로 수동 등록이 필요 없고, 예전 `Gaia ... Creatable` 인터페이스는 관리자 애플리케이션이나 Control Panel 확장 기능에 RID를 수동으로 등록해야 합니다.
- Gaia에서는 **Create object** 모드에서 그린 뒤 액션 폼을 제출해 객체를 만들고, **Bulk create** 표로 최대 5,000개까지 한꺼번에 만들거나 기존 주석을 객체로 승격할 수 있습니다.
- 대량 작업이 안 될 때는 모드, 권한, 인터페이스 구현, 구조체 파라미터, 속성 매핑, 보안 마킹을 점검합니다.
