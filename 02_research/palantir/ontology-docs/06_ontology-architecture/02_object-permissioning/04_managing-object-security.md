# 객체 보안 관리 (Managing object security)

- 원문: https://www.palantir.com/docs/foundry/object-permissioning/managing-object-security/
- 사이드바 위치: Ontology architecture > Object permissioning > Managing object security

이 페이지는 온톨로지 데이터를 보호하는 두 가지 방법, 즉 객체 및 속성 보안 정책과 데이터소스 정책을 비교합니다. 두 방법 모두 행 단위와 열 단위를 결합한 셀 단위 보안을 지원하지만, 설정 위치, 반영 속도, 스트리밍과 브랜치 지원에서 차이가 있습니다. 어떤 경우에 어느 방법을 써야 하는지, 데이터소스 정책을 쓸 때 제한 뷰(restricted view)와 다중 데이터소스 객체 타입(MDO)이 어떤 역할을 하는지 설명합니다.

온톨로지 데이터는 [객체 및 속성 정책(object and property policies)](#object-and-property-security-policies) 또는 [데이터소스 정책(data source policies)](#data-source-policies)으로 보호할 수 있습니다. 두 방식 모두 행 단위 보안과 열 단위 보안을 결합한 *셀 단위 보안(cell-level security)을* 지원합니다.

예를 들어 항공사 관리 플랫폼에 `User ID`, `Flight Number`, `Seat Assignment`, `Name`, `Address`, `Phone Number` 속성(property)을 가진 `Passenger` 객체 타입이 있다고 합시다.

* **행 단위 보안(Row-level security):** 일부 사용자는 VIP이며, 이들의 객체 인스턴스(백킹 데이터셋의 행에 해당)는 사용자가 `VIP` 마킹(marking)을 가진 경우에만 볼 수 있습니다.
* **열 단위 보안(Column-level security):** `Name`, `Address`, `Phone number` 속성은 사용자 데이터를 담고 있으며 `PII` 마킹을 가진 사용자만 접근할 수 있습니다.

사이드바의 **Check access** 패널을 사용하면 어떤 사람이 Workshop 또는 Slate 애플리케이션에 접근할 수 있는지, 의존하는 객체 타입과 그 데이터소스, 세분화된 접근 제어(granular access controls)까지 포함해 확인할 수 있습니다. 자세한 내용은 [Check access 패널 문서](https://www.palantir.com/docs/foundry/security/checking-permissions/)를 참고하세요.

**경고**: 일부 속성 값은 온톨로지 바깥의 다른 리소스에 저장된 데이터를 가리킵니다. 이 섹션에서 설명하는 접근 제어 메커니즘은 속성 값의 가시성만 제어하며, 그 다른 리소스의 가시성은 제어하지 않습니다. 예를 들어 미디어 참조 속성은 미디어 세트에 저장된 미디어 항목을 가리킬 수 있습니다. 미디어 세트의 권한이 객체 타입과 다르다면, 사용자가 미디어 참조 속성에는 접근할 수 없지만 미디어 세트에서 미디어 항목을 직접 가져올 수는 있는 상황이 생길 수 있습니다. 따라서 온톨로지에서 다른 리소스를 사용할 때는 그 리소스에도 적절한 권한이 설정되어 있는지 확인하는 것이 중요합니다.

**설명**: 마킹(marking)은 데이터에 붙이는 보안 라벨이며, 그 라벨에 대한 접근 권한이 있는 사용자만 데이터를 볼 수 있게 합니다. 셀 단위 보안을 위 예시 데이터로 보면 다음과 같습니다.

| User ID | Flight Number | Name | Phone Number | (VIP 여부) |
|---|---|---|---|---|
| U1 | KE001 | 김민수 | 010-1111-2222 | 아니요 |
| U2 | KE001 | 박지영 | 010-3333-4444 | 예 |

`VIP` 마킹이 없는 사용자에게는 U2 행 전체가 보이지 않고(행 단위), `PII` 마킹이 없는 사용자에게는 `Name`과 `Phone Number` 열이 보이지 않습니다(열 단위). 두 조건이 겹치면 특정 행의 특정 열, 즉 셀 단위로 가시성이 정해집니다. SQL로는 `WHERE` 조건으로 행을 걸러 내고 `SELECT` 목록에서 열을 빼는 것을 사용자마다 다르게 적용하는 것과 같은 결과입니다.

> **중간 요약**: 온톨로지 보안은 객체 및 속성 정책 또는 데이터소스 정책으로 구성하며 둘 다 셀 단위 보안을 지원합니다. 다만 속성 값이 가리키는 외부 리소스(예: 미디어 세트)는 별도로 권한을 맞춰야 합니다.

<a id="object-and-property-security-policies"></a>
## 객체 및 속성 보안 정책 (Object and property security policies)

객체 및 속성 보안 정책을 사용하면 객체 인스턴스와 그 속성에 보기 권한을 설정해 셀 단위 권한을 구현할 수 있습니다. 이 정책은 객체 타입의 Ontology Manager 화면에서 직접 관리하며, 백킹 데이터소스의 권한과는 독립적입니다.

객체 인스턴스의 가시성은 객체 보안 정책이, 속성 값의 가시성은 속성 보안 정책이 결정합니다. 필수(mandatory) 접근 제어와 분류 기반(classification based) 접근 제어, 그리고 세분화된 접근 제어를 객체 및 속성 보안 정책에 적용할 수 있습니다. 이들을 함께 사용하면 온톨로지에서 셀 단위 보안을 구현할 수 있습니다.

**주의**: 읽기 시점에만 적용(Read-time enforcement only). 객체 또는 속성 보안 정책 안의 세분화된 행 및 열 제어는 사용자가 읽을 수 있는 것을 걸러 냅니다. 이 제어는 하위(downstream) 출력이나 내보내기(export)까지 확장되지 않습니다. 하지만 같은 정책 안의 필수 제어와 분류 기반 제어는 파생 데이터에도 계속 적용됩니다. 행과 열 데이터가 하위로 흘러가는 동안에도 보호되게 하려면, 이 제어를 [마킹](https://www.palantir.com/docs/foundry/security/markings/)이나 [분류 기반 접근 제어(Classification-based Access Control)](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/)와 함께 사용하세요. 전체 모델은 [접근 제어 전파(Access control propagation)](https://www.palantir.com/docs/foundry/security/access-control-propagation/)를 참고하세요.

[객체 및 속성 보안 정책 설정에 대해 더 알아보세요.](07_object-security-policies.md)

**설명**: "읽기 시점에만 적용"의 의미를 구체적으로 보면, 세분화된 규칙(예: "자기 부서의 행만 보기")은 사용자가 객체를 조회하는 순간에 결과를 걸러 줄 뿐, 권한 있는 사용자가 그 데이터로 새 데이터셋을 만들면 새 데이터셋에는 그 규칙이 따라가지 않는다는 것입니다. 반면 마킹은 파생된 데이터에도 계속 붙어 다니므로(전파), 하위 데이터까지 보호하려면 마킹이 필요합니다.

> **중간 요약**: 객체 보안 정책은 행(객체) 가시성을, 속성 보안 정책은 열(속성) 가시성을 정하며 Ontology Manager에서 데이터소스와 독립적으로 관리합니다. 세분화된 제어는 읽기 시점에만 적용되므로 하위 데이터 보호에는 마킹이나 분류 기반 제어를 함께 써야 합니다.

<a id="data-source-policies"></a>
## 데이터소스 정책 (Data source policies)

객체 타입의 데이터 권한은 객체 타입의 입력 데이터소스에 적용된 권한에 의해 암묵적으로 제어됩니다.

**주의**: [백킹 데이터소스가 없는 객체 타입](../../02_define-ontologies/02_object-and-link-types/02_object-types/02_create-object-type.md#create-an-object-type-without-a-backing-datasource)은 데이터소스 정책을 사용할 수 없습니다. 이런 객체 타입은 만들 때 객체 보안 정책을 설정해야 합니다.

<a id="object-and-property-policies-vs-data-source-policies"></a>
### 객체 및 속성 정책과 데이터소스 정책 비교 (Object and property policies vs. data source policies)

대부분의 경우 객체 보안을 관리할 때는 객체 및 속성 보안 정책이 권장됩니다. 이 정책은 객체 타입에서 직접 셀 단위 보안(행, 열, 셀 단위 권한)을 통합된 방식으로 제공합니다. 그래서 데이터소스 정책보다 설정하고 유지 관리하기가 더 간단합니다.

<a id="benefits-of-object-and-property-security-policies"></a>
#### 객체 및 속성 보안 정책의 이점 (Benefits of object and property security policies)

객체 및 속성 보안 정책은 데이터소스 정책을 사용할 때 생기는 여러 문제를 해결합니다.

* **통합된 셀 단위 보안:** 제한 뷰(restricted view, RV)와 다중 데이터소스 객체 타입(multi-data source object type, MDO)을 조합할 필요 없이, 하나의 기능이 행 단위(객체 보안 정책), 열 단위(속성 보안 정책), 셀 단위 권한을 모두 제공합니다.
* **간소화된 설정:** 보안을 백킹 데이터소스와 독립적으로 Ontology Manager의 객체 타입에서 직접 관리합니다. 복잡성과 유지 관리 부담이 줄어듭니다.
* **거의 즉각적인 정책 반영:** 객체 및 속성 보안 정책의 변경은 거의 바로 적용됩니다. RV에서는 정책을 바꾼 뒤 파이프라인을 다시 빌드해야 읽기에 새 정책이 반영됩니다. 다만 그룹 멤버십이나 기타 사용자 속성 같은 Multipass의 변경은 여전히 짧은 시간 동안 캐시됩니다.
* **스트리밍 지원:** 객체 보안 정책은 스트림으로 뒷받침되는 객체 타입에도 적용할 수 있어, 스트리밍 데이터에 대해서도 행 단위 및 열 단위 권한을 구현할 수 있습니다.
* **브랜치 호환성:** 객체 보안 정책은 [Global Branching](https://www.palantir.com/docs/foundry/global-branching/overview/)과 통합되어, 병합하기 전에 브랜치에서 보안 설정을 시험해야 하는 개발 워크플로를 지원합니다.

**설명**: Multipass는 Foundry에서 사용자 인증과 그룹, 사용자 속성을 관리하는 서비스 이름입니다. "짧은 시간 캐시된다"는 것은, 예를 들어 어떤 사용자를 그룹에서 뺐을 때 정책 자체는 바로 바뀌지 않았어도 그 사용자의 그룹 정보가 잠시 이전 값으로 남아 있을 수 있다는 뜻입니다.

<a id="when-to-use-data-source-policies"></a>
#### 데이터소스 정책을 써야 하는 경우 (When to use data source policies)

RV와 MDO에 기반한 데이터소스 정책은 다음 경우에 적합합니다.

1. **온톨로지 바깥에서의 세분화된 접근 제어:** 백킹 데이터셋이 온톨로지 바깥에서도 사용되고 그 맥락에서 세분화된 접근 제어가 필요하다면 여전히 RV가 적절한 해법입니다. 예를 들어 RV는 [Code Workspaces](https://www.palantir.com/docs/foundry/code-workspaces/overview/)에서 접근 수준이 서로 다른 사용자들이 백킹 데이터셋을 읽는 것을 보호할 수 있습니다. 객체 및 속성 보안 정책은 범위가 온톨로지로 한정되므로, 온톨로지가 아닌 맥락에서 원시 데이터셋에 대한 접근은 제어하지 않습니다.
2. **특정 요구 사항이 있는 MDO:** 데이터소스별로 다른 해석 전략(resolution strategy)이나 다른 빌드 일정이 필요한 등의 이유로 객체 타입에 MDO가 필요하다면 데이터소스 정책이 필요할 수 있습니다. [이 구성에 대해 더 알아보세요](../04_object-edits-and-materializations/02_how-edits-applied.md#configuration).

> **중간 요약**: 일반적으로는 객체 및 속성 보안 정책이 권장됩니다(통합된 셀 단위 보안, 간단한 설정, 즉각 반영, 스트리밍과 브랜치 지원). 데이터셋 자체를 온톨로지 밖에서도 보호해야 하거나 MDO가 꼭 필요한 경우에는 데이터소스 정책을 씁니다.

<a id="object-input-data-sources"></a>
### 객체 입력 데이터소스 (Object input data sources)

데이터셋과 스트림은 [객체 타입](../../02_define-ontologies/02_object-and-link-types/02_object-types/01_object-types-overview.md)의 입력 데이터소스로 가장 널리 쓰이는 리소스입니다. 이 데이터소스들의 데이터 권한은 다음과 같이 결정됩니다.

* **[데이터셋(Datasets)](https://www.palantir.com/docs/foundry/data-integration/datasets/):** 데이터셋의 각 행은 온톨로지의 객체 인스턴스 하나에 대응하며, 데이터셋과 그 트랜잭션에 최소 `Viewer` 권한을 가진 사용자는 그 데이터셋에서 만들어진 모든 객체 인스턴스에 접근할 수 있습니다.
* **[스트림(Streams)](https://www.palantir.com/docs/foundry/data-integration/streams/):** 스트림은 온톨로지에서 지연 시간이 짧은 스트리밍 데이터에 쓰이는 입력 데이터소스입니다. 스트림 데이터소스에 최소 `Viewer` 권한을 가진 사용자는 그 스트림 데이터소스에서 만들어진 모든 객체 인스턴스에 접근할 수 있습니다.

데이터소스 정책으로 행 단위 또는 열 단위 권한을 구현해야 한다면 [제한 뷰(RV)](#restricted-views)와 [다중 데이터소스 객체 타입(MDO)](#multi-data-source-object-types)을 사용할 수 있습니다.

**설명**: 즉 데이터소스 정책의 기본 단위는 "데이터셋 전체"입니다. 데이터셋을 볼 수 있으면 그 데이터셋에서 나온 객체를 전부 보고, 볼 수 없으면 하나도 못 봅니다. 그보다 세밀하게 나누려면 행을 거르는 RV나, 열을 다른 데이터셋으로 나누는 MDO가 필요합니다.

<a id="configure-data-source-policies-with-rvs-and-mdos"></a>
### RV와 MDO로 데이터소스 정책 설정하기 (Configure data source policies with RVs and MDOs)

<a id="restricted-views"></a>
#### 제한 뷰 (Restricted views)

제한 뷰는 데이터셋의 특정 행과, 그 행에서 만들어진 대응 객체 인스턴스에 대한 *행 단위 접근 제어(row-level access control)를* 가능하게 합니다. 제한 뷰는 데이터셋 위에만 만들 수 있으며, 스트림이나 다른 데이터소스 타입 위에는 만들 수 없습니다. 특정 기본 키(primary key)를 가진 객체 인스턴스에 대한 접근은, 제한 뷰의 입력 데이터소스에서 그 특정 행에 누가 접근할 수 있는지에 따라 결정됩니다.

예를 들어 의료 기관 직원은 자기 진료 센터를 방문하는 환자의 데이터셋 행과 객체 인스턴스는 볼 수 있지만, 다른 진료 센터만 방문하는 환자의 데이터는 볼 수 없도록 제한될 수 있습니다. 두 종류의 데이터가 같은 데이터셋과 객체 타입 안에 있더라도 그렇습니다.

어떤 데이터셋 `care_event_info`에 `patient_id`, `doctor_id`, `care_center` 열이 있다면, 그 위에 `user.userAttribute('care_center') == care_center` 정책을 가진 제한 뷰를 만들 수 있습니다. 이 제한 뷰는 `care_event_info`에서 사용자와 같은 진료 센터를 가진 행에만 접근을 허용합니다.

Ontology Manager에서 제한 뷰는 데이터셋과 같은 방식으로 객체 타입의 입력 데이터소스로 선택할 수 있습니다.

[제한 뷰를 설정하고 객체의 행 단위 권한을 관리하는 방법에 대해 더 알아보세요.](05_configuring-rv-access-controls.md)

**설명**: 위 정책은 사용자마다 다른 `WHERE` 절이 자동으로 붙는 뷰로 이해할 수 있습니다. 사용자 속성 `care_center = 'Seoul'`인 직원이 조회하면 사실상 `SELECT * FROM care_event_info WHERE care_center = 'Seoul'`의 결과만 보게 됩니다.

<a id="multi-data-source-object-types"></a>
#### 다중 데이터소스 객체 타입 (Multi-data source object types)

온톨로지는 여러 입력 데이터소스를 하나의 객체 타입에 매핑하는 기능을 지원합니다. 이런 객체 타입을 다중 데이터소스 객체 타입(MDO)이라고 하며, Object Storage v2에서만 사용할 수 있습니다.

MDO를 사용하면 서로 다른 데이터소스의 열을 객체 타입의 여러 속성에 매핑할 수 있습니다. 이를 통해 분리된 입력 데이터소스에 대응하는 여러 접근 제어를 하나의 객체 타입에 적용할 수 있습니다. 이 입력 데이터소스는 데이터셋과 제한 뷰의 어떤 조합이든 될 수 있습니다.

예를 들어 어떤 진료 이벤트(care event) 객체 타입에 대해, 일부 의료 기관 직원은 개인 건강 정보(`PHI`)를 담은 객체 속성에 접근해야 하고 다른 직원은 접근하면 안 된다고 합시다. 이 접근 제어는 `Care Event` 객체 타입을 두 개의 분리된 입력 데이터소스로 뒷받침하고, 각 입력 데이터소스에 서로 다른 접근 제어와 권한을 적용하여 지원할 수 있습니다. `Care Event` 객체 타입은 `Patient ID`를 기본 키로 가지며 데이터소스 `patient_info`와 `care_event_info`로 뒷받침됩니다.

* `patient_info`에는 `patient_id`, `name`, `address`, `contact_number`, `age` 열이 있습니다. 이 데이터셋에는 `PHI` 마킹이 붙어 있습니다. `PHI` 마킹에 접근할 수 있는 사용자만 `patient_info`에서 온 속성 값에 접근할 수 있습니다.
* `care_event_info`에는 `patient_id`, `doctor_id`, `care_center` 열이 있습니다. 이 데이터셋에는 마킹이 없습니다. 사용자는 이 데이터셋에서 온 속성 값에 접근하는 데 어떤 마킹도 필요하지 않습니다.

이 서로 다른 권한은 객체 인스턴스에서 존중되고 적용됩니다. 사용자는 `PHI` 마킹이 없으면 `patient_info`에서 매핑된 `name`, `address`, `contact_number`, `age` 같은 속성에 접근할 수 없습니다.

[MDO를 설정하고 객체의 열 단위 권한을 관리하는 방법에 대해 더 알아보세요.](06_multi-datasource-objects.md)

**설명**: MDO는 데이터베이스 정규화에서 테이블을 세로로 나누는 것(수직 분할)과 같은 구조입니다. 두 테이블이 같은 기본 키 `patient_id`를 공유하고, 객체 하나는 이 키로 두 테이블의 행을 합쳐 만들어집니다. 권한은 테이블 단위로 걸리므로, `PHI` 마킹이 없는 사용자에게는 같은 객체에서 `care_event_info` 쪽 속성만 보이게 됩니다.

> **중간 요약**: 데이터소스 정책에서 데이터셋이나 스트림에 `Viewer` 권한이 있으면 거기서 나온 객체를 모두 봅니다. 행 단위 제한은 사용자 속성 기반 필터를 가진 제한 뷰(데이터셋 전용)로, 열 단위 제한은 권한이 다른 여러 데이터소스를 하나의 객체 타입에 매핑하는 MDO(OSv2 전용)로 구현합니다.

## 정리

- 온톨로지 데이터는 객체 및 속성 보안 정책 또는 데이터소스 정책으로 보호하며, 둘 다 행과 열을 결합한 셀 단위 보안을 지원합니다.
- 객체 및 속성 보안 정책은 Ontology Manager에서 데이터소스와 독립적으로 설정하며, 즉각 반영, 스트리밍, Global Branching을 지원하므로 대부분의 경우 권장됩니다. 단, 세분화된 제어는 읽기 시점에만 적용됩니다.
- 데이터소스 정책은 입력 데이터소스 권한을 그대로 따르며, 행 단위는 제한 뷰, 열 단위는 MDO로 구현합니다.
- 백킹 데이터소스가 없는 객체 타입은 반드시 객체 보안 정책을 써야 하고, 속성이 가리키는 외부 리소스(미디어 세트 등)는 별도로 권한을 맞춰야 합니다.
