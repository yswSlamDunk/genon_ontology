# 타입 매핑으로 Gotham 연동 활성화하기 (Enable Gotham integration)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/enable-gotham-integration/
- 사이드바 위치: Define Ontologies > Object and link types > Object types > Enable Gotham integration

이 페이지는 Foundry 온톨로지(Ontology)의 객체 타입을 Palantir의 다른 플랫폼인 Gotham에서도 쓸 수 있게 만드는 방법, 즉 타입 매핑(type mapping)을 설명합니다. Foundry와 Gotham을 함께 쓰는 환경에서 같은 데이터를 두 플랫폼에 따로 정의하지 않고 Foundry의 정의 하나로 관리하려면 이 과정이 필요합니다. 먼저 타입 매핑이 필요 없는 경우(MRS가 설치된 경우)를 확인하는 방법을 다루고, 이어서 타입 매핑을 켜고 설정하는 절차와 설치 상태를 설명합니다.

**팁**: Map Rendering Service가 있는 엔롤먼트는 타입 매핑을 건너뛸 수 있습니다(Enrollments with Map Rendering Service can skip type mapping). 엔롤먼트(enrollment)에 Map Rendering Service(MRS)가 포함되어 있다면, Gotham 연동을 활성화하기 위해 타입 매핑 과정을 거칠 필요가 *없습니다*. 추가 설정 없이 Gotham에서 [새 온톨로지 객체를 만들거나](05_create-ontology-objects-from-gaia.md) [기존 객체를 추가할](https://www.palantir.com/docs/foundry/geospatial/add-ontology-data-to-gaia/) 수 있습니다. 엔롤먼트에 MRS가 포함되어 있는지 확인하려면 아래 안내를 따르세요. <br><br> MRS의 사용 가능 여부, 설치, 또는 Gotham에 있는 MRS 관련 추가 문서에 대해 궁금한 점은 Palantir Support에 문의하세요.

**설명**: Gotham은 Palantir가 Foundry와 별도로 제공하는 플랫폼으로, 주로 국방과 정보 분석 분야에서 쓰입니다. Gaia는 Gotham 쪽의 지도 애플리케이션입니다. 엔롤먼트는 한 고객 조직에 설치된 Palantir 플랫폼 환경 하나를 가리키는 말입니다. 두 플랫폼은 각자 자기 온톨로지(타입 정의)를 가지고 있으므로, Foundry의 객체를 Gotham에서 보려면 "Foundry의 이 타입이 Gotham의 저 타입에 해당한다"는 대응 관계가 필요합니다. 이 대응 관계를 만드는 것이 타입 매핑입니다.

<a id="how-to-check-if-your-enrollment-contains-mrs"></a>
## 엔롤먼트에 MRS가 포함되어 있는지 확인하는 방법 (How to check if your enrollment contains MRS)

1. [Quicksearch](https://www.palantir.com/docs/foundry/compass/quicksearch/)를 실행해 **Gaia Home**을 검색하고 선택합니다.
2. 기존 Gaia 지도를 열거나 새 지도를 만듭니다.
3. 왼쪽 패널에서 **Data sources**를 선택합니다.
4. **Find...** 검색창에서 `Object search`를 검색합니다.

**Object search**를 찾아서 선택할 수 있다면, 엔롤먼트에 MRS가 포함되어 있는 것입니다.

![Gaia 왼쪽 패널의 Data sources 탭에 MRS 설치 여부를 나타내는 Object search가 표시된 모습.](https://www.palantir.com/docs/resources/foundry/object-link-types/gaia-mrs-installation-indicator.png)

> **중간 요약**: MRS가 설치된 엔롤먼트에서는 타입 매핑 없이 Gotham에서 온톨로지 객체를 만들거나 추가할 수 있습니다. Gaia 지도의 Data sources에서 `Object search`가 검색되면 MRS가 있는 것입니다.

***

<a id="use-type-mapping-to-create-a-unified-representation-of-your-ontology"></a>
## 타입 매핑으로 온톨로지를 통합된 형태로 표현하기 (Use type mapping to create a unified representation of your ontology)

타입 매핑을 사용하면 Foundry의 [Ontology Manager](../../../05_applications/04_ontology-manager/01_overview.md) 애플리케이션 안에서 관리하는, Foundry와 Gotham 전체에 걸친 하나의 통합된 온톨로지 표현을 만들 수 있습니다. 기존 Foundry 객체 타입, 속성(property) 타입, 공유 속성(shared property) 타입을 바탕으로 새 Gotham 타입을 만들 수 있으며, 이 타입들은 온톨로지가 시간이 지나며 바뀌어도 동기화된 상태로 유지됩니다. 타입 매핑 과정을 마치면, Gotham은 [Object Set Service](../../../06_ontology-architecture/01_overview-and-getting-started/01_overview.md#object-set-service-oss)를 통해 Foundry 객체 타입과 그 메타데이터를 조회할 수 있게 됩니다. Object Set Service는 객체 데이터의 검색, 필터링, 집계, 로딩을 지원하는 Foundry 백엔드 서비스입니다.

**주의**: 타입 매핑은 Foundry와 Gotham을 모두 사용하는 엔롤먼트에서만 쓸 수 있으며, 사용하기 전에 플랫폼 관리자가 활성화해야 합니다. 한 Foundry 온톨로지에서 한 번 활성화하면 타입 매핑을 비활성화할 수 없습니다. Gotham 설치 하나당 하나의 Foundry 온톨로지만 타입 매핑을 활성화할 수 있습니다. 타입 매핑 활성화에 도움이 필요하면 Palantir Support에 문의하세요.

<a id="when-to-type-map-object-types-in-your-ontology"></a>
### 온톨로지의 객체 타입을 타입 매핑해야 하는 경우 (When to type map object types in your ontology)

엔롤먼트에 [MRS가 포함되어 있지 않고](#how-to-check-if-your-enrollment-contains-mrs) 아래 조건 중 하나라도 해당한다면, [아래 안내를 따라](#toggle-on-type-mapping-in-foundrys-ontology-manager) Ontology Manager에서 객체 타입을 타입 매핑하세요.

* [전술 그래픽(tactical graphic)](05_create-ontology-objects-from-gaia.md#configure-a-tactical-graphic-on-your-gaia-map-and-tag-it-to-an-object-type)이나 [MIL-STD 2525 기호](https://www.palantir.com/docs/defense-osdk/api/common/interfaceTypes/com-palantir-ontology-defense-types-mil2525CSymbol/)에 없는 사용자 정의 기호 체계(symbology)를 사용할 계획인 경우. [Blueprint ↗](https://blueprintjs.com/) 기호는 타입 매핑 여부와 관계없이 지원됩니다.
* 온톨로지의 데이터를 Gaia에 추가하기 위해 [검색 템플릿(search template)](https://www.palantir.com/docs/foundry/geospatial/add-ontology-data-to-gaia/#create-a-search-template), [함수 기반 Enterprise Map Layer(EML)](https://www.palantir.com/docs/foundry/geospatial/add-ontology-data-to-gaia/#use-a-function-backed-enterprise-map-layer), 또는 [버전이 지정된 객체 집합(versioned object set) 기반 EML](https://www.palantir.com/docs/foundry/geospatial/add-ontology-data-to-gaia/#use-a-versioned-object-set-backed-enterprise-map-layer)을 설정할 계획인 경우.

**설명**: MIL-STD 2525는 군사 지도에서 부대, 장비 등을 표시하는 기호를 정한 미국 국방 표준입니다. Blueprint는 Palantir가 공개한 웹 UI 컴포넌트 라이브러리로, 여기 포함된 아이콘을 지도 기호로 쓸 수 있습니다. 정리하면, 표준 기호나 Blueprint 아이콘만 쓰고 위의 고급 Gaia 기능을 쓰지 않는다면 MRS가 없어도 타입 매핑이 꼭 필요하지는 않을 수 있습니다.

> **중간 요약**: 타입 매핑은 Foundry 객체 타입을 바탕으로 Gotham 타입을 만들고 계속 동기화하여, Gotham이 Object Set Service로 Foundry 객체를 조회할 수 있게 합니다. 관리자가 켜야 하고 한 번 켜면 끌 수 없으며, MRS가 없고 사용자 정의 기호나 검색 템플릿, EML을 쓸 때 필요합니다.

<a id="toggle-on-type-mapping-in-foundrys-ontology-manager"></a>
## Foundry의 Ontology Manager에서 타입 매핑 켜기 (Toggle on type mapping in Foundry's Ontology Manager)

Foundry 온톨로지의 데이터를 Gotham과 연동하려면, 먼저 아래 단계를 따라 Foundry의 Ontology Manager에서 원하는 객체 타입에 대해 타입 매핑을 켜야 합니다.

1. 홈 화면에서 Ontology Manager를 실행합니다.
2. 타입 매핑할 객체 타입을 찾아 선택합니다.
3. 객체 타입의 왼쪽 패널에서 **Capabilities**를 선택합니다.
4. 아래로 스크롤해 **Gotham Integration** 패널로 가서 `Allow objects of this type to be accessed from Gotham applications`(이 타입의 객체를 Gotham 애플리케이션에서 접근할 수 있도록 허용)를 켭니다.

![사용자는 Foundry의 Ontology Manager 애플리케이션에서 객체 타입에 대해 Gotham Integration을 켤 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/enable-gotham-mapping.png)

**주의**: 타입 매핑된 객체가 Gaia 지도에 표시되려면 `geopoint` 속성이 있어야 합니다. 이 속성은 객체 타입의 백킹 데이터셋에 원래 들어 있는 것일 수도 있고, Pipeline Builder의 [create Ontology geopoint](https://www.palantir.com/docs/foundry/pb-functions-expression/createOntologyGeopointV1/) 변환(transform) 기능을 사용해 위도/경도 쌍이나 `geopoint`에서 만들어 낸 것일 수도 있습니다.

**설명**: `geopoint`는 위도와 경도 한 쌍으로 지구 위의 한 점을 나타내는 속성 타입입니다. 예를 들어 데이터셋에 `lat = 37.5665`, `lon = 126.9780` 두 열이 따로 있다면, Pipeline Builder에서 이 둘을 합쳐 하나의 `geopoint` 열로 만든 뒤 속성으로 매핑해야 지도에 점으로 찍을 수 있습니다.

> **중간 요약**: Ontology Manager에서 객체 타입의 Capabilities 페이지로 가서 Gotham Integration 토글을 켜면 타입 매핑이 시작됩니다. 지도에 표시하려면 `geopoint` 속성이 필요합니다.

<a id="configure-an-object-types-parent-category-and-gotham-property-types"></a>
## 객체 타입의 상위 범주와 Gotham 속성 타입 설정하기 (Configure an object type's parent category and Gotham property types)

**Gotham Integration**을 켠 뒤에는, 아래 단계를 따라 기존 Foundry 객체 타입에서 파생된 새 Gotham 객체 타입을 만들고, 객체 타입의 **Parent category**(상위 범주)를 지정하고, **Property types**(속성 타입)를 설정할 수 있습니다.

1. **Gotham Integration**의 **Object type** 섹션에서 **Create a new object type**을 선택해, 기존 Foundry 객체 타입으로부터 Gotham에 새 객체 타입을 만듭니다.

2. 사용 사례에 맞게 `Entity`(사람, 조직, 차량 등), `Event`(항공편, 회의, 콘서트 등), `Document`(PDF 파일, 텍스트 문서, 보고서 등) 중에서 골라 Gotham에서 새 객체 타입의 **Parent category**를 지정합니다.

3. **Property types** 섹션을 사용해 Foundry 객체 타입의 속성을 Gotham에 매핑합니다. 속성은 Gotham 온톨로지에 공유하거나 복제할 수 있습니다. 어떤 속성에 대한 설정을 마치면 속성 이름 옆에 파란색 `Mapped` 태그가 보입니다.

   * `Do not map property to Gotham`(속성을 Gotham에 매핑하지 않음)이 기본 옵션입니다. 매핑하지 않은 Foundry 속성은 Gotham 온톨로지로 전파되지 않습니다.
   * `Assign to shared property`(공유 속성에 할당)를 선택하면 매핑할 *기존* 공유 속성을 고를 수 있습니다.
   * `Promote to shared property`(공유 속성으로 승격)는 다른 객체들도 사용할 수 있는 *새* 공유 속성을 만듭니다.
   * `Create a local clone of the property in Gotham`(Gotham에 속성의 로컬 복제본 만들기)은 선택한 속성의 복제본을 Gotham에 만들며, 이 복제본은 Gotham 애플리케이션과 호환됩니다.

   Foundry는 모든 공유 속성을 자동으로 타입 매핑하여 Gotham에서 사용할 수 있게 합니다.

4. 화면 위쪽 리본의 오른쪽에 있는 초록색 **Save** 버튼을 선택하고 검토합니다.

5. 객체 타입에 대한 변경 사항을 검토한 다음 **Save to ontology**를 선택합니다.

![Foundry와 Gotham 온톨로지를 연동할 때, 사용자는 객체 타입의 상위 범주를 선택할 수 있는 Criteria 패널을 사용해 새 객체 타입을 만들거나 기존 객체 타입을 넘겨받을 수 있습니다.](https://www.palantir.com/docs/resources/foundry/object-link-types/ontology-manager-gotham-integration-view.png)

**설명**: 공유 속성(shared property)은 여러 객체 타입이 함께 쓰는 하나의 속성 정의입니다. 예를 들어 `Person`과 `Organization` 두 객체 타입이 모두 `country` 속성을 가진다면, 이를 공유 속성 하나로 정의해 두고 두 타입이 참조하게 할 수 있습니다. 공유 속성으로 매핑하면 Gotham에서도 같은 정의를 공유하고, 로컬 복제본으로 매핑하면 해당 객체 타입 전용의 별도 속성이 Gotham에 생깁니다.

온톨로지에 변경 사항을 저장한 뒤, 객체 타입의 **Capabilities** 페이지에 있는 **Gotham Integration** 섹션으로 다시 스크롤해 올라가세요. 이제 객체 타입에 할당된 `Gotham URI`가 보이고, Gotham이 보고한 `Installation status`(설치 상태)를 확인할 수 있습니다.

Foundry의 Ontology Manager는 다음 설치 상태 중 하나를 표시합니다.

* `Ready to integrate`: 객체 타입이 Gotham 연동을 위한 타입 매핑을 할 준비가 되었습니다.
* `Installation in progress`: 객체 타입의 설치 과정이 진행 중입니다.
* `Installation complete`: 설치 과정이 끝났으므로 객체 타입을 Gotham에서 사용할 수 있습니다.
* `Installation failed: {failureMessage}`: 객체 타입의 설치가 한 번 이상 실패했으며, 다음 설치 실행 때 다시 시도됩니다. `{failureMessage}`에는 실패 이유가 나옵니다. 흔한 설치 실패 원인은 다음과 같습니다.
  * *라이브 재인덱싱(Live reindex)*: Gotham에서 라이브 재인덱싱이 실행 중이면 온톨로지를 갱신할 수 없습니다. 이 동안에는 변경을 스테이징하는 대신 설치가 실패하며, 라이브 재인덱싱이 끝나면 자동으로 다시 실행됩니다.
  * *필요한 타입이 설치되지 않음(Required types are not installed)*: 객체 타입을 성공적으로 설치하려면, 공유 속성 타입을 포함해 관련된 모든 속성의 설치(즉 매핑)가 완료되어야 합니다.
  * *다른 온톨로지 갱신(Other ontology updates)*: 온톨로지 갱신이 동시에 실행 중이면 타입 매퍼(type mapper)가 온톨로지를 갱신할 수 없으며, 자동으로 다시 실행됩니다.

객체 타입의 설치 상태가 `Installation complete`가 되면, Gotham 애플리케이션에서 객체 타입을 검색하고 사용할 수 있습니다.

Gotham에서 타입 매핑된 객체 타입을 사용 중단(deprecate)하려면, Foundry의 Ontology Manager에서 그 객체 타입을 삭제하면 됩니다. Foundry에서 삭제하면, 대응하는 Gotham 객체 타입과 그 속성 타입은 Gotham에서 접근할 수 없게 되고 Gotham 애플리케이션에서도 사용할 수 없게 됩니다.

Gotham은 Foundry 데이터셋의 보안과 마킹(marking)을 그대로 모델링합니다. 즉 타입 매핑을 통해 Gotham에서 사용할 수 있게 된 Foundry 데이터는 같은 접근 제어와 등급 분류(classification)를 그대로 가집니다.

**설명**: 마킹(marking)은 Foundry에서 데이터에 붙이는 보안 표시로, 그 마킹에 대한 접근 자격이 있는 사용자만 데이터를 볼 수 있게 합니다. 타입 매핑으로 데이터가 Gotham에 노출되어도, Foundry에서 볼 수 없는 사용자는 Gotham에서도 볼 수 없다는 뜻입니다.

> **중간 요약**: Gotham Integration에서 새 Gotham 객체 타입을 만들고 상위 범주(Entity, Event, Document)를 고른 뒤, 각 속성을 매핑하지 않거나, 기존 공유 속성에 할당하거나, 새 공유 속성으로 승격하거나, 로컬 복제본으로 만듭니다. 저장 후에는 Gotham URI와 설치 상태가 표시되며, `Installation complete`가 되면 Gotham에서 사용할 수 있습니다. Foundry의 보안과 마킹은 Gotham에서도 그대로 적용됩니다.

## 정리

- 타입 매핑은 Foundry 객체 타입을 바탕으로 Gotham 타입을 만들고 동기화하여, 두 플랫폼이 하나의 온톨로지 정의를 공유하게 합니다.
- 엔롤먼트에 MRS가 있으면 타입 매핑 없이도 Gotham에서 온톨로지 객체를 쓸 수 있으며, Gaia의 Data sources에서 `Object search`로 확인합니다.
- 타입 매핑은 관리자가 활성화해야 하고 끌 수 없으며, Gotham 설치 하나당 Foundry 온톨로지 하나만 가능합니다.
- 절차는 Capabilities 페이지에서 Gotham Integration 켜기, 상위 범주 선택, 속성 매핑 방식 선택, 저장 순서이며, 지도 표시에는 `geopoint` 속성이 필요합니다.
- 설치 상태로 진행을 확인하고, Foundry에서 객체 타입을 삭제하면 Gotham에서도 사라지며, Foundry의 보안과 마킹이 Gotham에 그대로 적용됩니다.
