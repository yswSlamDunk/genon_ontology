# 시나리오 메타데이터를 객체로 저장하기 (Store scenario metadata as objects)

- 원문: https://www.palantir.com/docs/foundry/ontology/persisted-scenario/
- 사이드바 위치: Ontology scenarios > Store scenario metadata as objects

이 페이지는 시나리오(scenario)의 메타데이터를 온톨로지 안에 객체로 저장해 "영구(persisted) 시나리오"로 만드는 방법을 다룹니다. 임시 시나리오는 정해진 시간이 지나면 사라지지만, 객체로 저장한 시나리오는 팀원과 공유하고 비교하고 권한으로 통제할 수 있습니다. 시나리오 객체 타입 설정, 생성(저장) 액션 설정, Workshop에서 기존 시나리오를 저장하는 방법, 그리고 승인 워크플로를 구성해 접근을 통제하는 방법까지 순서대로 설명합니다.

**참고**: 베타(Beta). 온톨로지 시나리오는 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며 사용 중인 환경(enrollment)에서는 제공되지 않을 수 있습니다. 온톨로지 시나리오 인터페이스를 사용하려면 Palantir Support에 문의하세요.

시나리오의 메타데이터를 온톨로지에 정의하고 저장할 수 있습니다. 이때 각 객체가 하나의 시나리오를 나타내며, 이렇게 만든 시나리오를 **영구(persisted)** 시나리오라고 합니다.

온톨로지에 저장된 시나리오는 공유할 수 있고 함께 작업할 수 있습니다. 팀은 여러 영구 시나리오를 나란히 놓고 비교할 수 있고, 설명과 작성자 같은 풍부한 메타데이터를 붙일 수 있으며, 관련 객체에 시나리오를 링크해 쉽게 정리할 수 있습니다. 영구 시나리오는 Foundry의 권한 및 거버넌스 모델을 그대로 상속하므로 적절한 접근 제어가 보장되고, 의사 결정 과정에 대한 지속적인 감사 기록(audit trail)이 남습니다.

**설명**: 시나리오는 온톨로지의 실제 데이터를 바꾸지 않고 "만약 이렇게 편집하면 어떻게 될까"를 따로 떼어 놓은 공간에서 시험해 보는 기능입니다. 시나리오 자체는 RID(Resource Identifier, Foundry 리소스의 고유 식별 문자열)로 식별됩니다. 이 페이지의 핵심 아이디어는 그 RID를 기본 키로 삼는 객체 타입을 하나 만들어, 시나리오 한 개당 객체 한 개(행 한 개)를 두는 것입니다. 예를 들어 `Scenario` 객체 타입에 `scenario_ref`(기본 키), `created_by`, `description` 열이 있는 테이블을 생각하면 됩니다. 이렇게 하면 시나리오도 일반 객체처럼 검색하고, 링크를 걸고, 권한을 줄 수 있습니다.

<a id="configure-scenario-object-type"></a>
## 시나리오 객체 타입 설정하기 (Configure scenario object type)

Ontology Manager에서 시나리오 객체 타입을 설정하려면 아래 단계를 따르세요.

1. Ontology Manager에서 **Object types** 탭으로 이동해 **+ New object type**을 선택합니다.

2. 설정 마법사를 따라 진행합니다. 3단계(**Properties**)에서 인터페이스를 **Add**(추가)하도록 선택한 다음 **Ontology Scenario** 인터페이스를 검색합니다. **Scenario Reference**가 객체 타입의 기본 키(primary key)에 매핑되어 있는지 확인한 뒤 나머지 단계를 마칩니다. <br><br>
   ![온톨로지에 시나리오 메타데이터 저장하기.](https://www.palantir.com/docs/resources/foundry/ontology/persist-scenario-metadata-ontology-manager.png) <br><br>

3. 새 객체 타입이 만들어지면 **Properties** 탭을 열고 **Primary Key** 속성(property)에 **Scenario Reference** 값 타입(value type)이 지정되어 있는지 확인합니다.

4. **Expiration Time** 인터페이스 속성은 시나리오가 언제 만료되는지를 제어합니다. 만료 시간을 설정하지 않으면 시나리오는 [기본 유지 시간(default time to live)](01_overview-ontology-scenario.md#time-to-live)이 지난 뒤 만료됩니다. **Timestamp** 기본 타입(base type)을 가진 속성을 추가하고 이를 **Expiration Time** 인터페이스 속성에 매핑하면 만료 시간을 바꿀 수 있습니다. 이 타임스탬프 속성을 갱신하는 액션은 모두 시나리오의 만료 시간도 함께 갱신합니다. 만료 시간은 현재 시각으로부터 31일을 넘을 수 없다는 점에 유의하세요.

5. 필요하면 **Created By**나 **Description**처럼 시나리오에 대한 메타데이터를 저장할 속성을 추가합니다. 설정을 저장하고 최초 동기화(initial sync)가 끝날 때까지 기다립니다.

**설명**: 인터페이스(interface)는 여러 객체 타입이 공통으로 갖춰야 할 속성의 목록을 정해 둔 규약입니다. 프로그래밍 언어의 인터페이스처럼, **Ontology Scenario** 인터페이스를 구현한 객체 타입은 `Scenario Reference`, `Expiration Time` 같은 정해진 속성을 반드시 갖게 됩니다. 플랫폼은 이 인터페이스를 보고 "이 객체 타입은 시나리오를 담는 타입"이라고 인식합니다. 값 타입(value type)은 문자열 같은 기본 타입에 의미와 제약을 덧붙인 타입이며, 여기서는 기본 키 값이 시나리오 RID 형식이어야 한다는 뜻입니다. TTL(time to live)은 데이터가 자동으로 삭제되기 전까지 유지되는 시간을 말합니다.

> **중간 요약**: 새 객체 타입을 만들 때 **Ontology Scenario** 인터페이스를 추가하고 **Scenario Reference**를 기본 키에 매핑합니다. 만료 시간은 Timestamp 속성을 **Expiration Time**에 매핑해 조절할 수 있으며 최대 31일입니다.

<a id="configure-createsave-action"></a>
## 생성/저장 액션 설정하기 (Configure create/save action)

1. Ontology Manager에서 만든 시나리오 객체 타입(Scenario Object Type)을 찾습니다. 처음 설정할 때 **Create Object** 액션을 설정하지 않았다면 **Action types** 카드에서 **+ New**를 선택해 하나 만듭니다.

2. **Create Object** 액션 설정 안에서 **String** 타입의 파라미터를 하나 더 추가합니다. **Constraints** 카드에서 값 타입을 **Scenario Reference Value**로 설정합니다. 그런 다음 **Visibility** 토글을 꺼서 최종 사용자에게 이 파라미터가 보이지 않게 합니다. <br><br>
   ![온톨로지에서 시나리오 저장 액션 만들기.](https://www.palantir.com/docs/resources/foundry/ontology/persist-scenario-create-scenario-action-configuration.png) <br><br>

3. 액션 설정 페이지의 **Rules** 탭에서 **Unique ID** 속성이 새로 만든 **Scenario Reference** 파라미터에 매핑되어 있는지 확인합니다. <br><br>
   ![온톨로지에서 시나리오 저장 액션의 속성 매핑.](https://www.palantir.com/docs/resources/foundry/ontology/persist-scenario-create-scenario-action-property-mapping-redacted.png) <br><br>

**설명**: 이 액션은 SQL로 치면 `INSERT INTO scenario (unique_id, ...) VALUES (:scenario_reference, ...)`에 해당합니다. 기본 키 열(Unique ID)에 들어갈 값을 사용자가 직접 입력하지 않고, 숨겨진 파라미터를 통해 현재 시나리오의 RID가 자동으로 채워지도록 만드는 것이 목적입니다.

> **중간 요약**: 시나리오 객체 타입의 **Create Object** 액션에 숨겨진 String 파라미터(값 타입 **Scenario Reference Value**)를 추가하고, 이 파라미터를 기본 키 속성에 매핑합니다.

<a id="persist-an-existing-temporary-scenario"></a>
## 기존 임시 시나리오를 영구 저장하기 (Persist an existing temporary scenario)

진행하기 전에 [임시 시나리오 설정 튜토리얼](02_temporary-scenario.md)을 완료했는지 확인하세요. 첫 번째 임시 시나리오가 준비되었다면 Workshop에서 다음 단계를 따릅니다.

1. 시나리오 저장을 담당할 **Button Group** 위젯을 애플리케이션에 추가합니다.

2. 버튼의 액션을 시나리오 객체 타입에 설정해 둔 **Create Object** 액션으로 지정합니다.

3. **Default Value** 설정에서 **Scenario Reference** 파라미터가 **Scenario Manager** 위젯이 만들어 내는 Active Scenario 변수로 채워지도록 설정합니다. <br><br>
   ![시나리오 저장 버튼의 파라미터 기본값.](https://www.palantir.com/docs/resources/foundry/ontology/persist-scenario-button-parameter-default.png) <br><br>

**설명**: 동작 순서를 정리하면 다음과 같습니다. 사용자가 Workshop 화면에서 임시 시나리오 안에서 편집을 합니다. 그 시나리오의 RID는 Scenario Manager 위젯의 Active Scenario 변수에 들어 있습니다. 사용자가 저장 버튼을 누르면 Create Object 액션이 실행되고, 이 RID를 기본 키로 하는 시나리오 객체가 하나 생깁니다.

> **중간 요약**: Workshop에 버튼을 추가하고, 버튼이 Create Object 액션을 실행할 때 Active Scenario 변수 값을 Scenario Reference 파라미터로 넘기도록 하면 임시 시나리오가 객체로 저장됩니다.

<a id="create-new-scenario-object"></a>
## 새 시나리오 객체 만들기 (Create new scenario object)

영구 시나리오를 표시하려면 Workshop에서 다음과 같이 조정합니다.

1. **Create or Save Scenario** 액션에서 **Scenario reference** 파라미터에는 기본값이 필요하지 않습니다. 액션이 실행될 때 자동으로 생성됩니다.

2. **Scenario Manager** 위젯을 영구 시나리오 객체 목록을 보여 주도록 설정한 **Object List** 위젯(또는 다른 객체 표시 위젯)으로 교체합니다.

3. 새로 추가한 위젯의 데이터 소스로 **Scenario Object Type**을 지정합니다. <br><br>
   ![Workshop에서 영구 시나리오 Object List 설정.](https://www.palantir.com/docs/resources/foundry/ontology/persist-scenario-workshop-object-list-widget.png) <br><br>

4. **Active Scenario** 변수를 **Object-backed scenario** 변수로 교체하고, 그 값을 **Object List** 위젯의 **Active Object**로 설정합니다. 다른 위젯에서도 변수 선택을 이것으로 바꿔야 합니다. <br><br>
   ![Workshop에서 객체 기반 시나리오 변수 설정.](https://www.palantir.com/docs/resources/foundry/ontology/persist-scenario-object-backed-scenario-variable.png) <br><br>

**설명**: 앞 섹션은 이미 있는 임시 시나리오를 나중에 저장하는 방식이고, 이 섹션은 처음부터 시나리오를 객체로 만들고 목록에서 고르는 방식입니다. 사용자가 Object List에서 시나리오 객체 하나를 선택하면, 그 객체(기본 키가 시나리오 RID)가 곧 "현재 작업 중인 시나리오"가 됩니다.

> **중간 요약**: Scenario Manager 대신 시나리오 객체를 나열하는 Object List 위젯을 쓰고, 선택된 객체를 Object-backed scenario 변수로 연결하면 목록에서 고른 영구 시나리오를 작업 대상으로 삼을 수 있습니다.

<a id="control-access-to-and-govern-persisted-scenarios"></a>
## 영구 시나리오의 접근 통제와 거버넌스 (Control access to and govern persisted scenarios)

영구 시나리오를 누가 보고 편집할 수 있는지 통제하고 검토 워크플로를 관리하려면 객체 속성, [객체 보안 정책(object security policies)](../06_ontology-architecture/02_object-permissioning/07_object-security-policies.md), [액션 제출 조건(submission criteria)](../02_define-ontologies/03_action-types/08_submission-criteria.md)을 사용합니다. 각 영구 시나리오가 객체로 표현되기 때문에 이런 통제 수단을 쓸 수 있습니다.

예를 들어 팀은 다음과 같은 시나리오 승인 워크플로를 구성할 수 있습니다.

* 시나리오 소유자는 자기 시나리오를 볼 수 있고, 초안을 검토 요청할 수 있습니다.
* [승인 그룹(approvals group)](https://www.palantir.com/docs/foundry/security/users-and-groups/#groups)의 구성원은 모든 시나리오를 볼 수 있고, 검토 중인 시나리오를 승인하거나 반려할 수 있습니다.
* 그 밖의 사용자는 영구 시나리오 객체를 볼 수 없습니다.

이렇게 하려면 다음 단계를 따릅니다.

1. Ontology Manager에서 시나리오 객체 타입에 다음 속성을 추가합니다.

   * **Created By:** 시나리오 소유자를 식별합니다.
   * **Status:** 시나리오가 `Draft`, `In review`, `Approved`, `Rejected` 중 어느 상태인지 추적합니다.
   * **Reviewed By:** 선택 사항으로, 검토자를 기록합니다.
   * **Reviewed At:** 선택 사항으로, 검토가 이루어진 시각을 기록합니다. <br><br>
     ![Ontology Manager에서 영구 시나리오 객체 타입에 속성 추가하기.](https://www.palantir.com/docs/resources/foundry/ontology/persist-scenario-add-properties.png) <br><br>
     **Create Object** 액션에서 액션 규칙(rule)을 사용해 **Created By**를 **Current user**(현재 사용자)로, **Status**를 정적 값 `Draft`로 설정합니다. <br><br>
     ![Ontology Manager에서 객체 생성 액션의 규칙 설정하기.](https://www.palantir.com/docs/resources/foundry/ontology/persist-scenario-set-action-rules.png) <br><br>

2. 시나리오 객체 타입의 **Security** 탭으로 이동해, 다음 조건 중 하나라도 참이면 접근을 허용하는 객체 보안 정책을 설정합니다.

   * 현재 사용자의 ID가 시나리오 객체의 **Created By** 속성과 일치한다.
   * 현재 사용자의 그룹 ID 목록에 승인 그룹이 포함된다.

   정책을 정의할 때 승인 그룹은 이름이 아니라 변하지 않는 그룹 ID로 참조하세요. 그래야 그룹 이름이 바뀌어도 정책이 영향을 받지 않습니다. 사용자는 시나리오 객체 타입 정의를 볼 수 있는 권한도 가지고 있어야 합니다. <br><br>
   ![시나리오 객체 타입의 보안 정책 설정.](https://www.palantir.com/docs/resources/foundry/ontology/persist-scenario-configure-granular-policy.png) <br><br>

3. 시나리오 객체 타입을 **Only allow edits via actions**(액션을 통한 편집만 허용)로 설정합니다. 그런 다음 허용할 상태 전이마다 별도의 액션을 만듭니다.

   | 액션 | 결과 | 제출 조건 |
   | --- | --- | --- |
   | **Submit for review** | 상태를 `Draft`에서 `In review`로 바꿉니다. | 현재 사용자가 **Created By**와 일치하고, 현재 상태가 `Draft`입니다. |
   | **Approve scenario** | 시나리오를 승인해 상태를 `In review`에서 `Approved`로 바꾸고, 선택적으로 **Reviewed By**와 **Reviewed At**을 채웁니다. | 현재 사용자의 그룹 ID에 승인 그룹이 포함되고, 현재 상태가 `In review`입니다. |
   | **Reject scenario** | 상태를 `In review`에서 `Rejected`로 바꾸고, 선택적으로 **Reviewed By**와 **Reviewed At**을 채웁니다. | 현재 사용자의 그룹 ID에 승인 그룹이 포함되고, 현재 상태가 `In review`입니다. |

   선택적으로, **Approve scenario** 액션에 **Apply Scenario** 규칙을 추가하면 승인과 [시나리오 병합](04_merge-scenario.md)이 하나의 통제된 액션 안에서 함께 일어나게 할 수 있습니다.

**설명**: 이 구성은 상태 기계(state machine)를 액션으로 구현한 것입니다. `Status` 속성이 가질 수 있는 상태는 Draft, In review, Approved, Rejected 네 가지이고, 허용되는 전이는 Draft에서 In review로, In review에서 Approved 또는 Rejected로 가는 세 가지뿐입니다. "액션을 통한 편집만 허용"으로 막아 두면 사용자가 속성을 직접 고칠 수 없으므로, 제출 조건을 통과한 액션으로만 상태가 바뀝니다. 객체 보안 정책은 SQL의 행 수준 보안(row-level security)과 같은 개념으로, `WHERE created_by = current_user OR current_user_groups CONTAINS approvals_group_id`를 만족하는 행만 보이게 하는 것과 같은 효과를 냅니다.

> **중간 요약**: 영구 시나리오는 객체이므로 속성, 객체 보안 정책, 제출 조건을 조합해 소유자와 승인 그룹만 볼 수 있게 하고, 상태 전이를 액션으로만 허용하는 승인 워크플로를 만들 수 있습니다.

## 정리

- 영구 시나리오는 시나리오 RID를 기본 키로 하는 객체로, **Ontology Scenario** 인터페이스를 구현한 객체 타입에 저장합니다.
- 만료 시간은 Timestamp 속성을 **Expiration Time**에 매핑해 조절하며, 현재로부터 최대 31일입니다.
- Create Object 액션에 숨겨진 Scenario Reference 파라미터를 두고, Workshop 버튼이나 Object List 위젯과 연결해 시나리오를 저장하고 선택합니다.
- 객체 보안 정책과 제출 조건, 상태 속성을 조합하면 검토와 승인 워크플로를 구성할 수 있고, 승인 액션에 Apply Scenario 규칙을 붙여 병합까지 한 번에 처리할 수 있습니다.
