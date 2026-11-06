# 제한 뷰 기반 객체 타입 설정하기 (Configuring restricted-view-backed object types)

- 원문: https://www.palantir.com/docs/foundry/object-permissioning/configuring-rv-access-controls/
- 사이드바 위치: Ontology architecture > Object permissioning > Configuring restricted-view-backed object types

이 페이지는 제한 뷰(restricted view, RV)를 객체 타입의 백킹 데이터소스(backing datasource)로 써서 행 단위 접근 제어를 구현하는 방법을 설명합니다. Object Storage v1과 v2에서 객체를 보기 위한 조건이 어떻게 다른지, 사용자의 편집(edit)이 보안 판단에 쓰이는 속성을 바꿀 때 어떤 일이 생기는지, 그리고 읽기와 편집을 나누어 정하는 세분화 정책(Granular Policies)을 다룹니다.

[제한 뷰(RV)](https://www.palantir.com/docs/foundry/platform-security-management/manage-restricted-views/#use-restricted-views-to-back-object-types)는 온톨로지 데이터에 행 단위 접근 제어를 제공합니다. 이를 통해 데이터셋 전체나 특정 타입의 모든 객체에 대한 접근을 통째로 부여하는 것보다 더 세밀한 접근 제어가 가능합니다.

제한 뷰는 데이터셋과 비슷하지만 데이터셋의 *특정 행*에 대한 접근을 제한합니다. 제한 뷰는 데이터셋 수준에서 설정되며, 온톨로지 객체는 제한 뷰 정책에 정의된 세분화된 권한을 상속합니다.

<a id="use-restricted-views-to-back-object-types"></a>
## 제한 뷰로 객체 타입 뒷받침하기 (Use restricted views to back object types)

객체 타입을 제한 뷰로 뒷받침하면 사용자가 볼 수 있는 특정 객체가 제어됩니다. 예를 들어 사용자가 어떤 정책의 요구 사항을 만족해 제한 뷰의 특정 행을 볼 수 있다면, 그에 대응하는 온톨로지 객체도 볼 수 있습니다.

데이터셋으로 뒷받침되는 객체 타입의 객체를 보려면 그 데이터셋도 볼 수 있어야 합니다.

* Object Storage v1(Phonograph)에서 제한 뷰로 뒷받침되는 객체 타입의 객체를 보려면 객체 타입 자체를 볼 수 있어야 하며, 제한 뷰를 반드시 볼 수 있어야 하는 것은 아닙니다. 대신 해당 행에 대해 제한 뷰의 [마킹](https://www.palantir.com/docs/foundry/security/restricted-views/#create-marking-backed-restricted-views)과 읽기 정책만 만족하면 됩니다.
* Object Storage v2에서는 제한 뷰로 뒷받침되는 객체 타입의 객체를 보려면 그 제한 뷰를 볼 수 있어야 합니다.

사용자에게서 특정 객체를 제한하려는 경우, Ontology Manager에서 객체 타입의 백킹 데이터소스로 제한 뷰만 선택하세요.

![입력 데이터소스](https://www.palantir.com/docs/resources/foundry/object-permissioning/object-security-backing-datasource.png)

**설명**: OSv1과 OSv2의 차이는 검사하는 조건의 개수로 정리할 수 있습니다. OSv1에서는 "객체 타입을 볼 수 있는가" + "그 행에 대해 마킹과 읽기 정책을 만족하는가"를 봅니다. OSv2에서는 여기에 "제한 뷰 리소스 자체를 볼 수 있는가"가 추가로 필요합니다. 따라서 OSv2로 옮길 때는 사용자에게 제한 뷰에 대한 보기 권한이 있는지도 확인해야 합니다.

> **중간 요약**: 제한 뷰를 백킹 데이터소스로 쓰면 사용자가 볼 수 있는 행에 대응하는 객체만 보입니다. OSv1에서는 행 단위 마킹과 읽기 정책만 만족하면 되지만, OSv2에서는 제한 뷰 자체에 대한 보기 권한도 필요합니다.

<a id="ontology-edits"></a>
## 온톨로지 편집 (Ontology edits)

**주의**: 객체의 보안에서 참조하는 속성을 편집할 수 있으므로, 사용자 편집이 온톨로지 객체에 대한 접근에 영향을 줄 수 있습니다. 이런 경우 사용자가 백킹 제한 뷰의 행은 볼 수 있지만 온톨로지의 대응 객체는 볼 수 없거나, 그 반대가 될 수 있습니다.

예를 들어 다음 데이터를 가진 `Ticket` 객체 타입이 있고, 제한 뷰의 정책은 행을 보려면 `Assignee` 열에 있는 그룹의 구성원이어야 한다고 요구한다고 합시다.

| Ticket ID  | Title      | Assignee         |
|------------|------------|------------------|
| 101        | Ticket One | palantir-support |

이 객체의 `Assignee`를 `customer-support`로 바꾸는 액션이 적용되면, `palantir-support`의 구성원이면서 `customer-support`의 구성원은 아닌 사용자는 온톨로지에서 이 객체에 대한 접근을 잃습니다. 하지만 그들은 제한 뷰의 행은 계속 볼 수 있습니다. 제한 뷰는 액션의 영향을 받지 않기 때문입니다. 반대로 `customer-support`의 구성원이면서 `palantir-support`의 구성원은 아닌 사용자는 온톨로지 객체에 대한 접근을 얻지만, 제한 뷰의 행은 여전히 볼 수 없습니다.

**설명**: 이런 불일치가 생기는 이유는 온톨로지 편집이 원본 데이터셋을 바로 고치지 않고 별도로 저장되어 객체에 덧씌워지기 때문입니다. 제한 뷰는 원본 행(`Assignee = palantir-support`)을 기준으로 판단하고, 온톨로지 객체는 편집이 반영된 값(`Assignee = customer-support`)을 기준으로 판단하므로 두 판단 결과가 달라집니다.

> **중간 요약**: 보안 정책이 참조하는 속성(예: `Assignee`)을 액션으로 바꾸면, 온톨로지 객체의 가시성은 편집된 값을, 제한 뷰의 행 가시성은 원본 값을 따르게 되어 둘이 어긋날 수 있습니다.

<a id="security-configuration"></a>
## 보안 설정 (Security configuration)

Ontology Manager의 **Datasources** 탭에는 **Granular Policies**를 편집하는 추가 설정 옵션이 표시됩니다. **Granular Policies** 섹션에서는 이 타입의 객체를 편집하는 권한을 설정할 수 있습니다.

**주의**: 편집에 대한 Granular Policies는 Object Storage v1을 사용하면서 **Only allow edits via actions** 옵션이 선택되지 않은 객체 타입에서만 설정할 수 있습니다. 그 밖의 모든 객체 타입에서는 편집 권한이 그 객체 타입을 편집하는 액션 타입을 통해 제어됩니다. [액션 권한에 대해 더 알아보세요.](../../02_define-ontologies/03_action-types/19_permissions.md)

이 정책은 사용자가 자신의 속성(예: 객체의 속성과 비교되는 값)에 따라 특정 객체만 보거나 편집하게 하고 싶은 경우에 맞춰 설정할 수 있습니다. 예를 들어 `region` 열 값이 `Europe`인 유럽 객체는 `Europe` 사용자만 보고 편집하게 하고 싶을 수 있으며, 이는 제한 뷰의 정책과 다를 수 있습니다.

객체의 속성에 누가 접근할 수 있는지 정의하는 정책은 세 가지입니다.

* **Read:** 제한 뷰의 모든 속성을 누가 볼 수 있는지 정의합니다. 위 예시에서는 `region` 열을 사용자 속성에 있는 값(`Europe`)과 비교해 사용자가 볼 수 있는 객체를 정하는 정책이 될 수 있습니다.
* **Edit property:** 라이트백(writeback)용으로 설정된 속성 중, 어떤 세분화 권한 정책 정의에도 쓰이지 않는 속성을 누가 수정할 수 있는지 정의합니다. 위 예시에서 이 정책은 `name` 속성을 누가 편집할 수 있는지는 제어하지만, `region` 속성은 정책에 쓰이므로 제어하지 않습니다.
* **Edit policy property:** 라이트백용으로 설정된 속성 중, 세분화 권한 정책 정의에도 쓰이는 속성을 누가 수정할 수 있는지 정의합니다. 위 예시에서 이 정책은 `region` 속성을 누가 편집할 수 있는지 제어합니다.

![세분화된 권한](https://www.palantir.com/docs/resources/foundry/object-permissioning/object-security-granular-permissions.png)

**경고**: Object Storage v1(Phonograph)에 객체 타입을 등록한 뒤 보기 정책을 바꿨다면, **Ontology Manager**에서 객체 타입의 **Datasources** 탭에 있는 Phonograph 섹션의 **Update** 버튼으로 등록을 갱신해야 합니다. 등록을 갱신하지 않으면 이전에 등록된 정책을 기준으로 제한 뷰의 최신 데이터가 제공될 수 있습니다. Object Storage v2에서는 자동 정책 전파가 기본으로 제공됩니다.

**설명**: 편집 정책을 둘로 나누는 이유는 정책 판단에 쓰이는 속성이 특히 민감하기 때문입니다. 위 `region` 예시에서 누군가 `region`을 `Europe`에서 `Asia`로 바꾸면 그 객체를 볼 수 있는 사람 자체가 바뀝니다. 그래서 `name` 같은 일반 속성(Edit property)보다 `region` 같은 정책 속성(Edit policy property)의 수정 권한을 더 엄격하게 따로 줄 수 있게 되어 있습니다.

> **중간 요약**: OSv1에서 액션 전용 편집이 꺼진 객체 타입은 Datasources 탭의 Granular Policies로 Read, Edit property(정책에 안 쓰이는 속성), Edit policy property(정책에 쓰이는 속성)를 정할 수 있습니다. 다른 경우는 액션 권한으로 제어하며, OSv1에서 보기 정책을 바꾸면 Update로 등록을 갱신해야 합니다.

## 정리

- 제한 뷰를 백킹 데이터소스로 쓰면 사용자가 볼 수 있는 행에 대응하는 객체만 보이는 행 단위 보안이 됩니다.
- OSv1은 행 단위 마킹과 읽기 정책 충족만 요구하고, OSv2는 제한 뷰 자체의 보기 권한도 요구합니다.
- 보안에 쓰이는 속성을 편집하면 온톨로지 객체와 제한 뷰 행의 가시성이 어긋날 수 있습니다.
- Granular Policies(Read, Edit property, Edit policy property)는 OSv1의 일부 객체 타입에만 해당하며, 나머지는 액션 권한으로 편집을 제어합니다.
- OSv1은 보기 정책 변경 후 수동 Update가 필요하고, OSv2는 자동으로 정책이 전파됩니다.
