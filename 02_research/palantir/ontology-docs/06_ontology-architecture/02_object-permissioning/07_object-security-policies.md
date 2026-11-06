# 객체 보안 정책 (Object security policies)

- 원문: https://www.palantir.com/docs/foundry/object-permissioning/object-security-policies/
- 사이드바 위치: Ontology architecture > Object permissioning > Object security policies

이 페이지(원문 제목: Object and property security policies)는 객체 타입 자체에 보안 정책을 걸어, 백킹 데이터소스(backing datasource)의 권한과 독립적으로 "누가 어떤 객체를, 어떤 속성(property)까지 볼 수 있는지"를 정하는 방법을 설명합니다. 객체 보안 정책으로 행 수준 보안을, 속성 보안 정책으로 열 수준 보안을, 둘을 합쳐 셀 수준 보안을 구현합니다. 설정 절차, 편집과 다운로드 권한, 세분화 정책(granular policy) 한도, 머티리얼라이제이션(materialization)과의 관계, 테스트 방법, 제한된 뷰(restricted view)에서의 마이그레이션까지 다룹니다.

객체 보안 정책(object security policy)을 사용하면 객체 타입에 보안 정책을 설정함으로써, 백킹 데이터소스의 권한과는 독립적으로 객체 인스턴스에 대한 보기(view) 권한을 구성할 수 있습니다. 객체 보안 정책은 *행 수준 보안(row-level security)*을 구현하는 데 사용됩니다.

특정 속성의 가시성은 추가적인 *속성 보안 정책(property security policy)*으로 보호할 수 있습니다. 속성 보안 정책은 객체 보안 정책과 동일하지만, 선택한 일부 속성에만 적용된다는 점이 다릅니다. 속성 보안 정책은 *열 수준 보안(column-level security)*을 구현하는 데 사용됩니다.

기본적으로 객체 보안 정책은 모든 속성에 적용됩니다. 어떤 속성이 속성 보안 정책에 포함되어 있으면, 사용자가 그 속성 값을 보려면 객체 보안 정책과 속성 보안 정책을 모두 통과해야 합니다. 객체 보안 정책과 속성 보안 정책의 조합은 *셀 수준 보안(cell-level security)*을 구현하는 데 사용됩니다. 사용자가 객체 보안 정책을 통과하지 못하면 그 사용자는 객체 인스턴스를 볼 수 없습니다. 객체 보안 정책은 통과했지만 속성 보안 정책을 통과하지 못하면, 속성 값 자리에 *null* 값이 보입니다.

**주의**: 읽기 시점에만 적용됨(Read-time enforcement only). 객체 보안 정책과 속성 보안 정책은 사용자가 읽을 수 있는 내용을 걸러 냅니다. 사용자는 볼 권한이 없는 객체 인스턴스나 속성 값을 절대 읽을 수 없습니다. 그러나 이 통제는 다운스트림 출력이나 내보내기(export)까지 확장되지 않습니다. 데이터가 다운스트림으로 흘러가는 동안에도 보호되도록 하려면 이 통제를 [마킹(marking)](https://www.palantir.com/docs/foundry/security/markings/)이나 [분류 기반 접근 제어(Classification-based Access Control)](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/)와 함께 사용하십시오. 전체 모델은 [접근 제어 전파(Access control propagation)](https://www.palantir.com/docs/foundry/security/access-control-propagation/)를 참고하십시오.

**설명**: 객체를 테이블의 행, 속성을 열로 보면 세 가지 보안 수준이 바로 이해됩니다. `Passenger` 테이블에 행이 3개(P1, P2, P3) 있고 열이 `User ID`, `Flight Number`, `Name`이라고 합시다. 객체 보안 정책은 "P3 행은 VIP라서 특정 사용자에게 아예 안 보인다"처럼 행을 거르고, 속성 보안 정책은 "`Name` 열은 개인정보 권한이 있는 사람만 본다"처럼 열을 거릅니다. 둘을 함께 쓰면 "P1 행은 보이지만 P1의 `Name` 칸은 `null`"처럼 칸(셀) 하나 단위로 가시성이 정해집니다. 또 이 필터는 사용자가 객체를 읽을 때 적용되는 것이므로, 누군가 그 객체 데이터를 다른 데이터셋으로 내보내면 그 결과물에는 자동으로 걸리지 않습니다. 그래서 마킹처럼 데이터를 따라 전파되는 통제와 함께 쓰라고 권합니다.

> **중간 요약**: 객체 보안 정책은 행, 속성 보안 정책은 열, 둘의 조합은 셀 단위로 가시성을 정합니다. 이 정책들은 읽기 시점에만 적용되므로 다운스트림 보호에는 마킹 등을 함께 써야 합니다.

<a id="configure-object-and-property-security-policies"></a>
## 객체 보안 정책과 속성 보안 정책 설정하기 (Configure object and property security policies)

객체 인스턴스와 그 속성에 대한 접근은 다음 조건으로 결정됩니다.

* 객체 타입에 대한 `Viewer` 접근 권한.
* 세분화 정책(granular policy)이 설정되어 있다면 그 정책의 통과.
* 모든 [마킹](https://www.palantir.com/docs/foundry/security/markings/), [조직(organization)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/#organizations), [분류(classification)](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/) 검사의 통과.

객체 보안 정책이나 속성 보안 정책이 설정되어 있으면, 사용자는 객체 인스턴스를 보기 위해 객체 타입의 백킹 데이터소스에 대한 `Viewer` 권한이 필요하지 않습니다.

**주의**: 사용 중인 환경(enrollment)이 레거시 [데이터소스 파생 권한 모델(datasource-derived permissions model)](03_ontology-permissions-legacy.md#datasource-derived-permissions)을 쓰고 있다면, 사용자가 객체 타입과 그 인스턴스를 보려면 여전히 백킹 데이터소스에 대한 `Viewer` 권한이 필요합니다. 이 요구 사항은 객체 보안 정책이 설정되어 있어도 적용됩니다. 데이터소스 파생 권한은 객체 보안 정책이 제공하는 분리(decoupling)를 무력화하므로, 객체 보안 정책을 설정하기 전에 [프로젝트 기반 권한으로 마이그레이션](02_ontology-permissions.md)할 것을 권장합니다.

다운로드 권한은 위에서 설명한 보기 권한과 별도로 평가됩니다. 객체 타입이 보안 정책으로 보호되어 있을 때, 플랫폼이 다운로드 권한을 객체 타입에서 검사할지 백킹 데이터소스에서 검사할지는 객체 타입의 위치에 따라 결정되며, 이는 [객체 데이터 다운로드 권한](#permissions-to-download-object-data)에서 설명합니다.

예를 들어 `Passenger` 객체 타입에 `User ID`, `Flight Number`, `Seat Assignment`, `Name`, `Address`, `Phone Number` 속성이 있다고 합시다. 일부 승객은 VIP이며, 이들의 정보는 `VIP` 마킹에 대한 접근 권한이 있는 사용자만 볼 수 있습니다. 또 `Name`, `Address`, `Phone Number` 같은 일부 속성은 `PII` 마킹을 가지고 있고 개인 식별 정보를 볼 권한이 있는 사용자에게만 보여야 합니다. 백킹 데이터셋은 민감한 데이터로 이루어져 있으므로 `PII`와 `VIP`로 마킹되어 있어야 합니다. 하지만 민감 마킹이 없는 사용자도 승객의 항공편 세부 정보에는 접근할 수 있어야 합니다.

다음 단계에 따라 객체 보안 정책으로 `Passenger` 객체 타입을 보호할 수 있습니다.

1. 객체 타입의 **Security** 탭으로 이동합니다. <br><br> <img src="https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-navigate-security-tab.png" width=500 alt="Ontology Manager에서 객체 타입의 'Security' 탭."> <br><br>
2. **Security policies** 섹션 아래의 **Create**를 선택해 데이터소스 정책을 객체 보안 정책으로 재정의(override)합니다. <br><br>
   ![Security policies 섹션 아래의 "Create" 옵션.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-override-datasource-policy.png) <br><br>
3. 객체 인스턴스에 대한 보기 권한을 편집하는 객체 보안 정책을 만듭니다. 세분화 정책을 추가하고 조직과 마킹을 편집할 수 있습니다. <br><br>
   ![객체 보안 정책 개요.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-permissions-ui-overview.png) <br><br>
4. **Markings** 설정에서 `PII`와 `VIP` 마킹의 상속을 중지해, 해당 마킹이 없는 사용자도 객체 인스턴스를 볼 수 있게 합니다. <br><br>
   ![접근 요구 사항 아래에 나열된 마킹과, 마킹 상속을 시작하거나 중지하는 옵션.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-stop-inheriting-markings.png) <br><br>
5. VIP에 대한 접근을 제한하기 위해 **Granular policy**(세분화 정책)를 추가합니다. `VIP` 마킹은 [필수 통제 속성(mandatory control property)](../../02_define-ontologies/02_object-and-link-types/03_properties/08_mandatory-control-properties.md)으로 추가되어 있습니다. 각 행은 필수 통제 속성에 마킹 집합을 가지고 있으며, 사용자가 그 객체 인스턴스에 접근하려면 이 마킹들을 충족해야 합니다. <br><br>
   ![VIP 필수 통제 속성에 조건을 추가하는 옵션이 있는 "Compose granular policy" 화면.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-add-granular-policy.png) <br><br>

**경고**: 그룹, 마킹, 조직 멤버십에 `NOT` 조건을 사용하지 마십시오. 이런 상황에서 `NOT` 조건을 쓰는 것은 잘못된 설정입니다. 플랫폼은 사용자 권한의 일부만 담고 있는 범위 제한 토큰(scoped token)을 지원합니다. 이런 토큰에는 `NOT` 조건이 검사하는 속성(attribute)이 빠져 있을 수 있으며, 그러면 조건이 통과되어 의도보다 더 많은 접근이 허용됩니다.

**설명**: 예를 들어 "`VIP_BLOCKED` 그룹의 구성원이 **아니면** 허용"이라는 조건을 두었다고 합시다. 사용자의 전체 권한으로 요청하면 그룹 소속이 확인되어 차단되지만, 일부 권한만 담은 토큰으로 요청하면 그룹 정보가 토큰에 없으므로 시스템은 "구성원이 아님"으로 판정하고 접근을 허용해 버립니다. 그래서 "~이면 허용"처럼 긍정 조건으로 정책을 작성해야, 정보가 빠졌을 때 접근이 거부되는 안전한 방향으로 동작합니다.

6. 이것으로 객체 보안 정책이 만들어집니다. 이제 `PII` 속성들을 `PII` 마킹으로 보호해야 합니다. 이는 속성 보안 정책을 추가해서 할 수 있습니다. <br><br>
   ![Security policies 섹션에서 속성 보안 정책을 추가하는 옵션.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-add-property-security-policy.png) <br><br>
7. 보호해야 할 속성들을 선택하고 정책 이름을 지정합니다. 그런 다음 **Manage markings** 설정에서 `PII` 마킹을 추가합니다. 속성 보안 정책의 설정 항목은 객체 보안 정책과 동일합니다. <br><br>
   ![정책 이름과 속성이 표시된 속성 보안 정책 개요.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-select-properties-for-policy.png) <br><br>
   속성 보안 정책의 **Manage markings**를 선택하고 `PII` 마킹을 추가합니다. <br><br>
   ![상속된 마킹을 나열하는 "Access requirements" 섹션.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-add-marking-property-security-policy.png) <br><br>
8. 이것으로 속성 보안 정책이 만들어집니다. 정책에 포함된 속성들은 이제 객체 보안 정책과 새 속성 보안 정책 양쪽으로 보호됩니다. 어떤 속성 보안 정책에도 포함되지 않은 속성은 여전히 객체 보안 정책으로 보호됩니다. <br><br>
   ![객체 보안 정책이 적용되는 속성들.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-object-security-policy-properties.png) <br><br>
   ![속성 보안 정책이 적용되는 속성들.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-property-security-policy-properties.png)

**설명**: 위 절차의 결과를 사용자별로 정리하면 다음과 같습니다. 마킹이 없는 일반 사용자는 VIP가 아닌 승객 객체를 볼 수 있고, `Flight Number`와 `Seat Assignment`는 보이지만 `Name`, `Address`, `Phone Number`는 `null`로 보입니다. `PII` 마킹이 있는 사용자는 VIP가 아닌 승객의 모든 속성을 봅니다. VIP 승객 객체는 해당 행의 필수 통제 속성에 있는 `VIP` 마킹을 충족한 사용자만 볼 수 있습니다. 핵심은 4단계에서 데이터셋의 마킹 상속을 끊고, 그 대신 5단계(행)와 7단계(열)에서 필요한 곳에만 다시 제한을 거는 것입니다.

<a id="permissions-to-edit-security-policies"></a>
### 보안 정책 편집 권한 (Permissions to edit security policies)

객체 보안 정책이나 속성 보안 정책을 만들거나 편집하려면 객체 타입의 **Owner**여야 합니다. 사용 중인 환경이 [프로젝트 기반 권한](02_ontology-permissions.md)을 쓴다면, 객체 타입이 들어 있는 프로젝트에서 `Owner` 역할을 가지고 있어야 한다는 뜻입니다.

사용 중인 환경이 레거시 [데이터소스 파생 권한 모델](03_ontology-permissions-legacy.md#datasource-derived-permissions)을 쓴다면, 온톨로지의 `Owner`여야 한다는 뜻입니다. 객체 타입에 보안 정책이 설정된 뒤에는 속성을 추가하거나 제거하는 데에도 온톨로지의 `Owner` 권한이 필요합니다. 이 때문에 흔한 워크플로 다수가 매우 제한적이 되며, 이것이 객체 보안 정책을 설정하기 전에 [프로젝트 기반 권한으로 마이그레이션](02_ontology-permissions.md)할 것을 권장하는 또 하나의 이유입니다.

<a id="permissions-to-download-object-data"></a>
### 객체 데이터 다운로드 권한 (Permissions to download object data)

객체 타입이 객체 보안 정책이나 속성 보안 정책으로 보호되어 있을 때, 플랫폼이 다운로드 권한을 검사하는 위치는 객체 타입의 위치에 따라 정해집니다.

* **[프로젝트](02_ontology-permissions.md)에 저장된 객체 타입:** 플랫폼은 객체 타입에서 다운로드 권한을 검사합니다.
* **[온톨로지 역할(ontology roles)](03_ontology-permissions-legacy.md#ontology-roles)이나 [데이터소스 파생 권한](03_ontology-permissions-legacy.md#datasource-derived-permissions)을 사용하는 객체 타입:** 플랫폼은 백킹 데이터소스에서 다운로드 권한을 검사합니다.

<a id="property-security-policy-restrictions"></a>
### 속성 보안 정책의 제약 (Property security policy restrictions)

하나 이상의 속성 보안 정책을 설정할 때는 다음 제약이 적용됩니다.

* 객체 보안 정책이 이미 설정되어 있어야 합니다.
* 기본 키(primary key) 속성은 어떤 속성 보안 정책에도 포함될 수 없습니다.
* 기본 키가 아닌 속성은 최대 하나의 속성 보안 정책에만 포함될 수 있습니다.

**설명**: 기본 키를 속성 보안 정책에서 제외하는 이유는, 객체가 보인다면 그 객체를 식별하는 값도 보여야 하기 때문입니다. 행 자체는 보이는데 그 행을 가리키는 키가 `null`이면 링크나 조회에서 객체를 구분할 수 없습니다. 그래서 기본 키의 가시성은 객체 보안 정책 하나로만 결정됩니다.

> **중간 요약**: 접근은 객체 타입 `Viewer` 권한, 세분화 정책, 마킹과 조직과 분류 검사로 결정되며, 정책이 있으면 데이터소스 `Viewer` 권한은 필요 없습니다(레거시 모델 제외). 정책 편집에는 Owner 권한이 필요하고, 속성 보안 정책은 객체 보안 정책이 있어야 만들 수 있으며 기본 키는 넣을 수 없습니다.

<a id="configure-access-to-object-types"></a>
## 객체 타입 접근 설정하기 (Configure access to object types)

객체 타입에 대한 접근은 [온톨로지 메타데이터 권한](02_ontology-permissions.md)에서 설정할 수 있습니다. 사용자는 [객체 타입 정의와 인스턴스를 볼 수](02_ontology-permissions.md#viewing-object-types-and-objects) 있어야 합니다.

<a id="configure-a-granular-policy"></a>
## 세분화 정책 설정하기 (Configure a granular policy)

[행 수준 보안을 위한 세분화 정책 설정에 대해 더 알아보기.](https://www.palantir.com/docs/foundry/platform-security-management/manage-granular-policies/)

**설명**: 세분화 정책은 "행의 어떤 값과 사용자의 어떤 속성을 비교해 통과 여부를 정하는 조건식"입니다. 예를 들어 "객체의 `region` 속성 값이 사용자가 속한 그룹 목록에 포함되면 허용"처럼 작성하며, SQL로는 행마다 평가되는 `WHERE` 조건에 해당합니다.

<a id="granular-policy-limits-for-property-security-policies"></a>
### 속성 보안 정책의 세분화 정책 한도 (Granular policy limits for property security policies)

세분화 정책 비교 한도 10,000은 객체 보안 정책에 대해, 그리고 객체 보안 정책과 단일 속성 보안 정책의 각 조합에 대해 따로따로 적용됩니다. 각 속성 보안 정책에 대해, 그 정책의 세분화 정책 [비교 가중치(comparison weight)](https://www.palantir.com/docs/foundry/platform-security-management/manage-granular-policies/#policy-limitations)를 객체 보안 정책의 세분화 정책 가중치에 더합니다. 이렇게 합친 가중치는 10,000 미만이어야 합니다.

예를 들어 `Passenger` 객체 타입에서, VIP 승객에 대한 접근을 통제하는 객체 보안 정책을 유지하고 두 개의 속성 보안 정책 `Flight details`와 `Contact details`를 설정한다고 합시다. 이 예에서는 항공편 세부 정보도 이제 권한 있는 항공사 직원에게만 제한됩니다. `Name`, `Address`, `Phone Number`를 보호하기 위해 `Contact details`에는 `PII` 마킹을 유지합니다. 각 속성 보안 정책에도 세분화 조건을 설정했고, 비교 가중치가 다음과 같다고 가정합니다.

| 보안 정책 | 속성 | 세분화 정책 가중치 | 10,000 한도와 비교되는 가중치 |
| --- | --- | --- | --- |
| 객체 보안 정책 | `User ID`(기본 키). 그 밖의 모든 속성에도 적용 | 3,000 | 3,000 |
| `Flight details` 속성 보안 정책 | `Flight Number`, `Seat Assignment` | 5,000 | 3,000 + 5,000 = 8,000 |
| `Contact details` 속성 보안 정책 | `Name`, `Address`, `Phone Number` | 6,000 | 3,000 + 6,000 = 9,000 |

각 속성 보안 정책은 객체 보안 정책하고만 결합되므로, 합친 가중치는 `Flight details`가 8,000, `Contact details`가 9,000입니다. `Flight details` 정책의 가중치는 `Contact details` 정책의 합산 가중치에 더해지지 않으며, 그 반대도 마찬가지입니다.

객체 보안 정책은 속성 보안 정책이 적용되는 속성을 포함해 모든 속성에 여전히 적용됩니다. 객체 보안 정책의 세분화 조건을 각 속성 보안 정책에 반복해서 넣을 필요는 없습니다.

**설명**: 한도 계산의 핵심은 "어떤 셀 하나를 판정할 때 실제로 함께 평가되는 정책들의 합"만 본다는 것입니다. `Name` 칸을 판정할 때는 객체 보안 정책(3,000)과 `Contact details`(6,000)만 평가되므로 9,000이고, `Flight details`는 이 칸과 관계가 없으니 더하지 않습니다. 따라서 세 가중치를 모두 더한 14,000이 한도를 넘더라도, 각 조합이 10,000 미만이면 설정이 허용됩니다.

> **중간 요약**: 세분화 정책 한도 10,000은 "객체 보안 정책 단독"과 "객체 보안 정책 + 속성 보안 정책 하나" 조합마다 따로 계산합니다. 속성 보안 정책끼리는 가중치를 합치지 않습니다.

<a id="configure-mandatory-controls"></a>
## 필수 통제 설정하기 (Configure mandatory controls)

기본적으로 객체 보안 정책은 데이터소스로부터 모든 필수 통제(mandatory control)를 상속합니다. 여기에는 [마킹](https://www.palantir.com/docs/foundry/security/markings/), [조직](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/#organizations), [분류](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/)가 포함됩니다.

그런 다음 객체 보안 정책을 더 세밀하게 조정해, 새 필수 통제를 추가하거나 더 이상 필요 없는 상속된 필수 통제를 제거할 수 있습니다.

**설명**: 필수 통제는 사용자가 반드시 충족해야 하는 조건으로, 프로젝트 역할 같은 재량적(discretionary) 권한을 가지고 있어도 이것을 충족하지 못하면 접근이 거부됩니다. 데이터셋에 `PII` 마킹이 붙어 있으면 객체 보안 정책도 처음에는 그 마킹을 그대로 요구하고, 앞의 4단계처럼 필요에 따라 상속을 끊을 수 있습니다.

<a id="materializations-with-object-security-policies"></a>
## 객체 보안 정책과 머티리얼라이제이션 (Materializations with object security policies)

객체 보안 정책은 객체 타입에서 [머티리얼라이즈된(materialized)](../04_object-edits-and-materializations/06_materializations.md) 데이터를 보는 권한도 결정합니다.

현재 객체 보안 정책이 있는 객체 타입은 Foundry 데이터셋으로만 머티리얼라이즈할 수 있습니다. 머티리얼라이즈된 데이터에는 가장 제한적인 권한이 적용됩니다. 여기에는 다음이 포함됩니다.

* 백킹 데이터소스의 모든 마킹.
* 객체 보안 정책이나 속성 보안 정책에 추가로 적용된 마킹.
* 모든 객체 보안 정책과 속성 보안 정책의 세분화 정책에서 사용된 모든 필수 통제 속성의 마킹.

**주의**: 머티리얼라이즈된 데이터셋의 트랜잭션은 그 데이터셋이 빌드되는 시점에 생성된 보안 정책으로 보호됩니다. 사용자가 객체 보안 정책이나 속성 보안 정책에서 마킹을 추가하거나 제거하면, 그 마킹은 마킹이 존재하는 시점에 커밋된 트랜잭션에만 반영됩니다. 트랜잭션은 머티리얼라이제이션이 [빌드되도록 예약된](../04_object-edits-and-materializations/06_materializations.md#build-schedules-in-writeback-and-materialized-datasets) 시점에 커밋되며, 이 일정은 사용자가 설정합니다.
객체 보안 정책이나 속성 보안 정책에 마킹을 추가한 뒤에는 다음을 반드시 수행하십시오.

* 마킹이 머티리얼라이제이션 데이터셋에 즉시 전파되어야 한다면 머티리얼라이제이션 데이터셋을 빌드합니다.
* 머티리얼라이제이션 데이터셋의 과거 트랜잭션 전체를 보호하려면, 머티리얼라이제이션 데이터셋이나 백킹 데이터셋에 해당 마킹을 붙입니다.

**설명**: Foundry 데이터셋은 트랜잭션 단위로 버전이 쌓입니다. 월요일에 빌드된 트랜잭션 T1 이후 화요일에 정책에 `PII` 마킹을 추가하고 수요일에 T2가 빌드되었다면, T2에는 `PII` 보호가 적용되지만 T1은 여전히 마킹 없이 남아 있어 과거 버전으로 읽힐 수 있습니다. 그래서 즉시 다시 빌드하거나, 데이터셋 자체에 마킹을 붙여 과거 트랜잭션까지 덮으라고 안내하는 것입니다.

> **중간 요약**: 필수 통제는 데이터소스에서 상속되며 추가와 제거가 가능합니다. 머티리얼라이즈된 데이터셋에는 가장 제한적인 권한이 걸리지만, 정책 변경은 그 뒤에 빌드된 트랜잭션에만 반영됩니다.

<a id="test-object-security-policies"></a>
## 객체 보안 정책 테스트하기 (Test object security policies)

객체 보안 정책을 설정할 때, 아직 저장하지 않은 객체 보안 정책을 기준으로 특정 사용자가 인덱싱된 객체 타입의 속성을 볼 수 있는지 테스트할 수 있습니다. 또 세분화 정책에서 참조하는 속성의 값을 편집해 가상의 객체 인스턴스를 테스트하고, 정책이 올바르게 설정되었는지 확인할 수 있습니다. **Security policies** 섹션에서 **Test policies**를 선택하면 **Test security policies** 모달이 열립니다.

![객체 보안 정책 테스트 진입점.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-testing-entry-point.png)

**Test security policies** 모달에서 **Configure test** 패널을 사용해, 주어진 **Object**에 대한 가시성을 테스트할 **User**를 선택합니다. **Results** 섹션은 현재 보안 정책 설정에 따라 그 사용자가 객체의 어떤 속성을 볼 수 있는지 보여 줍니다.

![사용자의 가시성을 테스트하고 가상 객체 인스턴스의 속성 값을 편집할 수 있는 보안 정책 테스트 대화 상자.](https://www.palantir.com/docs/resources/foundry/object-permissioning/osp-testing-dialog.png)

<a id="current-object-security-policy-testing-limitations"></a>
### 현재 객체 보안 정책 테스트의 제약 (Current object security policy testing limitations)

* [파생 속성(derived property)](../../03_ontology-search/03_derived-properties.md)의 가시성은 테스트할 수 없습니다. 파생 속성은 그 원본 객체에 대한 사용자의 가시성에도 의존하기 때문입니다.
* 보안 정책에서 참조하는 조직의 구성원도 관리자도 아니라면, 테스트할 때 게스트 멤버십과 보조 조직(secondary organization)은 고려되지 않습니다. Foundry는 권한이 없는 조직들을 나열하는 경고 callout을 표시해 이를 알려 줍니다.

> **중간 요약**: Test policies 기능으로 저장 전 정책을 특정 사용자와 특정 객체(또는 값을 바꾼 가상 객체)에 대해 미리 검증할 수 있습니다. 파생 속성과 일부 조직 멤버십은 테스트에 반영되지 않습니다.

<a id="migrate-from-restricted-views-to-object-security-policies"></a>
## 제한된 뷰에서 객체 보안 정책으로 마이그레이션하기 (Migrate from restricted views to object security policies)

온톨로지 위에 구축된 대부분의 사용 사례에서는 [제한된 뷰](https://www.palantir.com/docs/foundry/security/restricted-views/)보다 객체 보안 정책을 권장합니다. 객체 보안 정책은 통합된 셀 수준 보안, 거의 즉각적인 정책 업데이트, 스트리밍과 브랜치(branching) 지원을 제공합니다. [객체 보안 정책과 속성 보안 정책의 이점에 대해 더 알아보기.](04_managing-object-security.md#benefits-of-object-and-property-security-policies)

이전에 제한된 뷰를 백킹으로 하는 객체 타입을 구성했고 객체 보안 정책으로 마이그레이션하려 한다면, 아래에 설명하는 마이그레이션 도구를 사용할 수 있습니다. [객체 및 속성 정책과 데이터소스 정책의 비교에 대해 더 알아보기.](04_managing-object-security.md#object-and-property-policies-vs-data-source-policies)

**Security** 탭의 마이그레이션 도구를 사용하면, 객체 타입의 데이터소스를 제한된 뷰에서 그 제한된 뷰의 백킹 데이터셋으로 바꾸고 객체 보안 정책으로 보호하도록 마이그레이션할 수 있습니다. 이 도구는 제한된 뷰에 정의된 정책과 일치하도록 보안 정책을 구성합니다.

![Security 탭에서 제한된 뷰를 객체 보안 정책으로 마이그레이션하는 진입점.](https://www.palantir.com/docs/resources/foundry/object-permissioning/rv-to-psg-migration-entry-point.png)

**설명**: 제한된 뷰는 데이터셋 위에 행 필터를 씌운 별도의 데이터소스이므로, 정책을 바꾸면 그 뷰를 다시 계산해야 하고 보호 단위도 행에 한정됩니다. 마이그레이션 도구는 객체 타입이 제한된 뷰 대신 원본 데이터셋을 직접 읽게 바꾸고, 같은 행 필터 조건을 객체 보안 정책으로 옮겨 적는 작업을 자동으로 해 줍니다.

<a id="limitations"></a>
### 제약 사항 (Limitations)

마이그레이션 도구는 다음과 같은 제한된 뷰 구성을 지원하지 않습니다.

* 여러 데이터소스를 가진 객체 타입(MDO).
* 머티리얼라이제이션이 여러 개이거나, 제한된 뷰 머티리얼라이제이션이 하나 있는 객체 타입.
* 지원되지 않는 비교 연산자(초과, 이상, 미만, 이하)를 사용하는 [세분화 정책](https://www.palantir.com/docs/foundry/platform-security-management/manage-granular-policies/)이 있는 제한된 뷰.
* integer, long, double 같은 숫자 상수 값을 참조하는 세분화 정책이 있는 제한된 뷰.
* 권한이 부여된 그룹 ID, 조직 마킹 ID, 정적 마킹 ID를 사용자 속성으로 참조하는 세분화 정책이 있는 제한된 뷰. 동등한 보안을 구현하려면 [필수 통제 속성](../../02_define-ontologies/02_object-and-link-types/03_properties/08_mandatory-control-properties.md) 사용을 고려하십시오.

<a id="preserve-discretionary-security"></a>
### 재량적 보안 유지하기 (Preserve discretionary security)

데이터에 대한 프로젝트 보기 제약(제한된 뷰가 들어 있는 프로젝트에서 상속된 보안 구성)을 유지하려면, 마이그레이션 도구를 사용해 객체 타입을 제한된 뷰와 같은 프로젝트로 옮길 수 있습니다.

![제한된 뷰에서 객체 보안 정책으로의 마이그레이션 도구.](https://www.palantir.com/docs/resources/foundry/object-permissioning/rv-to-psg-migration-tool.png)

> **중간 요약**: 대부분의 온톨로지 사용 사례에는 제한된 뷰보다 객체 보안 정책이 권장되며, Security 탭의 마이그레이션 도구가 정책을 자동으로 옮겨 줍니다. MDO, 일부 머티리얼라이제이션 구성, 특정 비교 연산자와 상수를 쓰는 정책은 도구가 지원하지 않습니다.

## 정리

- 객체 보안 정책은 행 수준, 속성 보안 정책은 열 수준, 두 정책의 조합은 셀 수준 보안을 백킹 데이터소스 권한과 독립적으로 제공합니다.
- 이 정책들은 읽기 시점에만 적용되므로, 다운스트림 데이터 보호에는 마킹이나 분류 기반 접근 제어를 함께 사용해야 합니다.
- 정책 편집에는 Owner 권한이 필요하고, 레거시 데이터소스 파생 권한 모델은 정책의 이점을 약화시키므로 프로젝트 기반 권한으로의 마이그레이션이 권장됩니다.
- 속성 보안 정책은 객체 보안 정책이 있어야 하며, 기본 키를 포함할 수 없고, 속성 하나는 최대 하나의 정책에만 속합니다. 세분화 정책 가중치 한도 10,000은 조합별로 계산됩니다.
- 머티리얼라이즈된 데이터에는 가장 제한적인 권한이 걸리지만, 마킹 변경은 이후 빌드된 트랜잭션에만 반영됩니다.
- Test policies로 저장 전에 정책을 검증할 수 있고, 제한된 뷰 기반 객체 타입은 마이그레이션 도구로 객체 보안 정책으로 옮길 수 있습니다.
