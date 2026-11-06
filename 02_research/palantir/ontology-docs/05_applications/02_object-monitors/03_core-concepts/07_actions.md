# 액션 (Actions)

- 원문: https://www.palantir.com/docs/foundry/object-monitors/actions/
- 사이드바 위치: Applications > Object Monitors [Sunset] > Core concepts > Actions

이 페이지는 객체 모니터(object monitor)가 트리거되거나 복구될 때 액션(action)을 자동으로 실행하는 방법을 설명합니다. 액션 구성, 감지된 객체 집합을 액션 파라미터로 넘기는 방법, 모니터에서 쓸 수 있는 액션을 제한하는 설정, 그리고 액션이 특정 사용자 권한으로 실행된다는 점을 다룹니다.

**주의**: 지원 종료(Sunset). Object Monitors는 [Automate](https://www.palantir.com/docs/foundry/automate/overview/)로 대체되었습니다. Automate는 완전히 하위 호환되는 제품으로, 플랫폼의 모든 비즈니스 자동화를 위한 단일 진입점을 제공합니다.

[액션](../../../02_define-ontologies/03_action-types/01_overview.md)은 객체 모니터가 트리거되거나 복구될 때 자동으로 실행될 수 있습니다.

<a id="configuring-actions"></a>
## 액션 구성하기 (Configuring Actions)

구독자는 새로운 [모니터 트리거됨(monitor triggered)](05_activity.md#monitor-triggered) 활동 이벤트가 있을 때 실행할 액션을 구성할 수 있습니다. 액션은 평가가 완료되는 즉시 모니터에 의해 자동으로 제출됩니다. 여러 사용자가 액션을 구성했다면 액션은 사용자마다 따로 실행됩니다.

![action\_visibility\_settings\_monitoring](https://www.palantir.com/docs/resources/foundry/object-monitors/action_visibility_settings_monitoring.png)

**설명**: 동작 순서는 (1) 모니터가 주기적으로 조건을 평가하고, (2) 조건이 충족되어 "트리거됨" 활동이 기록되면, (3) 액션을 구성해 둔 각 구독자에 대해 그 액션을 한 번씩 제출하는 것입니다. 구독자 A와 B가 모두 "담당자에게 작업 할당" 액션을 구성했다면, 한 번의 트리거로 액션이 두 번 실행됩니다.

<a id="affected-objects"></a>
## 영향을 받는 객체 (Affected objects)

이벤트 조건의 경우, 모니터가 감지한 객체 집합을 객체 집합(object set) 파라미터로 액션에 전달할 수 있습니다. [모니터 구성](../02_create_new_object_monitor.md#create-from-object-monitors-application) 페이지의 **Actions** 탭에서, 해당 파라미터가 모니터링 대상과 같은 객체 타입의 `ObjectSet<>`을 받도록 구성해야 합니다. 그러면 객체 집합을 제공하는 옵션을 선택할 수 있게 됩니다.

![Object Monitors 앱에서 액션 구성](https://www.palantir.com/docs/resources/foundry/object-monitors/management_app_configure_actions.png)

**주의**: 이 객체 집합은 액션 알림(Action notifications)의 입력으로 사용할 수 없습니다. 해당 모니터 실행에서 영향을 받은 객체 집합에는 액션 효과를 구성한 사용자만 접근할 수 있습니다.

**설명**: 예를 들어 Flight 객체 타입에 "지연 상태로 새로 바뀐 항공편" 이벤트 조건을 건 모니터라면, 액션 타입에 `ObjectSet<Flight>` 타입의 파라미터를 두어야 그 실행에서 감지된 항공편들만 액션에 넘길 수 있습니다. 파라미터 타입이 다른 객체 타입이면 이 옵션이 나타나지 않습니다.

> **중간 요약**: 구독자는 모니터 트리거 시 실행할 액션을 구성할 수 있고, 액션은 평가 직후 구독자마다 따로 제출됩니다. 이벤트 조건에서는 감지된 객체를 같은 객체 타입의 `ObjectSet<>` 파라미터로 넘길 수 있지만, 이 집합은 액션 알림 입력으로 쓸 수 없습니다.

<a id="action-visibility-settings"></a>
## 액션 표시 설정 (Action visibility settings)

모든 액션이 객체 모니터와 함께 쓰기에 적절한 것은 아닙니다. Ontology Manager에서 액션 타입을 구성할 때 그 액션이 객체 모니터링에 나타나지 않도록 비활성화할 수 있습니다. 액션 타입을 만든 뒤 **Action type** 목록에서 액션 타입을 클릭해 세부 정보를 보고, 왼쪽 패널에서 **Security & Submission Criteria** 탭을 클릭합니다. 그런 다음 **Frontend consumers** 섹션을 찾아 "Allow An Object Monitor To Submit This Action"(객체 모니터가 이 액션을 제출하도록 허용) 스위치를 끕니다.

![Ontology Manager에서 액션 표시 끄기](https://www.palantir.com/docs/resources/foundry/object-monitors/disable_action_visability@2x.png)

<a id="permissions"></a>
## 권한 (Permissions)

액션은 모니터를 구독한 특정 사용자와 연결됩니다. 즉, 액션을 구성하는 구독자는 해당 액션의 [제출 조건(submission criteria)](../../../02_define-ontologies/03_action-types/08_submission-criteria.md)을 통과해야 합니다.

다른 구독자를 대신해 액션을 구성할 수는 없습니다.

**주의**: 액션은 특정 사용자를 대신해 실행되므로, 그 사용자가 구독을 해제하거나 사용자 계정이 비활성화되거나 삭제되면 액션은 더 이상 실행되지 않습니다.

**설명**: 제출 조건은 "이 액션을 누가, 어떤 입력 값일 때 제출할 수 있는가"를 정하는 규칙입니다. 모니터의 액션은 구독자 본인의 신원으로 제출되므로, 예를 들어 "Operations 그룹 사용자만 제출 가능"이라는 조건이 걸린 액션은 그 그룹에 속하지 않은 구독자가 모니터에 구성할 수 없습니다. 같은 이유로 담당자가 퇴사해 계정이 삭제되면 그 사람이 구성한 자동 액션도 함께 멈추므로, 운영 중인 자동화는 이 점을 고려해 관리해야 합니다.

> **중간 요약**: Ontology Manager의 **Frontend consumers** 설정으로 특정 액션 타입이 모니터에서 쓰이지 않게 할 수 있습니다. 모니터 액션은 구성한 구독자 본인 권한으로 실행되므로 그 사용자가 제출 조건을 통과해야 하며, 구독 해제나 계정 비활성화, 삭제 시 실행이 중단됩니다.

## 정리

- Object Monitors는 지원 종료 단계이며 Automate로 대체되었습니다.
- 구독자는 모니터 트리거 시 자동 실행할 액션을 구성할 수 있으며, 액션은 구독자마다 따로 실행됩니다.
- 이벤트 조건에서는 감지된 객체를 같은 객체 타입의 `ObjectSet<>` 파라미터로 액션에 넘길 수 있습니다.
- 액션 타입의 **Security & Submission Criteria** 탭에서 객체 모니터 제출 허용 여부를 끌 수 있습니다.
- 액션은 구성한 구독자의 권한으로 실행되며, 그 사용자가 구독을 해제하거나 계정이 사라지면 실행이 멈춥니다.
