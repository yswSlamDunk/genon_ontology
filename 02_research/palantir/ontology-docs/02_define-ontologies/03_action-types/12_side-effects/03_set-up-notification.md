# 알림 설정하기 (Set up a notification)

- 원문: https://www.palantir.com/docs/foundry/action-types/set-up-notification/
- 사이드바 위치: Define Ontologies > Action types > Side effects > Set up a notification

이 페이지는 액션 타입에 알림을 실제로 추가해 보는 튜토리얼입니다. `Alert` 객체의 우선순위를 바꾸는 액션에 담당자 알림을 붙이는 과정을 수신자 설정, 내용 설정, 링크 설정, 테스트 전송 순서로 따라갑니다. 앞 페이지 [알림](02_notifications.md)에서 설명한 옵션들이 실제 화면에서 어떻게 쓰이는지 확인할 수 있습니다.

이 튜토리얼은 알림이 포함된 액션을 설정하는 방법을 보여 줍니다.

여기서는 `Alert` 객체의 `Priority` 속성을 업데이트하고, 동시에 그 Alert 객체의 속성으로 저장된 `Assignee`(Foundry 사용자)에게 알림을 보내는 액션을 사용합니다. 따라 하려면 다음이 미리 준비되어 있어야 합니다.

* 올바른 속성을 가지고 있으며 액션으로 편집할 수 있도록 설정된 객체
* 객체 하나와 새 우선순위를 담은 파라미터를 입력받아, 지정된 객체의 priority 속성을 업데이트하는 액션. [액션 시작하기 튜토리얼](../02_getting-started.md)을 이미 따라 했다면 이것이 준비되어 있을 것입니다.

객체 관리가 처음이라면 [객체 타입을 설정하는 방법](../../02_object-and-link-types/02_object-types/02_create-object-type.md)을 읽어 볼 수 있습니다.

<a id="prerequisites"></a>
## 사전 준비 (Prerequisites)

<a id="complete-the-getting-started-tutorial"></a>
### 시작하기 튜토리얼 완료하기 (Complete the Getting Started tutorial)

이 튜토리얼은 액션의 [시작하기(Getting Started)](../02_getting-started.md) 튜토리얼을 이미 완료했다고 가정합니다.

<a id="add-the-assignee-property-to-your-object-type"></a>
### 객체 타입에 담당자 속성 추가하기 (Add the assignee property to your object type)

이 튜토리얼을 진행하려면 `Alert` 객체에 `Case Managers`라는 속성이 있어야 하고, 이 속성에는 현재 배정된 사용자의 Foundry 사용자 ID가 들어 있어야 합니다. 보통 액션으로 업무 흐름을 구성한다면, 애플리케이션의 사용자 선택기(user selector) 컴포넌트로 사용자 ID를 수집하고 저장할 수 있습니다. 이렇게 저장한 ID는 Foundry에서 표시되는 곳마다 전체 사용자 이름으로 나타납니다.

**설명**: 예를 들어 Alert 객체 타입의 데이터가 다음과 같다고 합시다.

| alert_id | title | priority | case_managers |
|---|---|---|---|
| AL-1 | 서버 응답 지연 | Low | `7f3c...`(사용자 ID) |
| AL-2 | 결제 오류 | High | `a91e...`(사용자 ID) |

`case_managers` 열에는 이름이나 이메일이 아니라 Foundry 사용자 ID 문자열이 들어 있어야 알림의 수신자로 쓸 수 있습니다.

> **중간 요약**: 액션 시작하기 튜토리얼에서 만든 우선순위 변경 액션과, 사용자 ID를 담은 `Case Managers` 속성이 있는 `Alert` 객체 타입이 필요합니다.

<a id="add-a-notification"></a>
## 알림 추가하기 (Add a notification)

먼저 티켓 우선순위를 업데이트하는 액션으로 이동합니다. **Rules**(규칙) 섹션에서 **Add new rule**을 선택한 다음 **Notification**을 선택합니다. 그러면 알림을 추가하는 설정 대화상자가 열립니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/side_effects_notification_tutorial_edit_action_rules.png" alt="수신자 설정" width="500" />

<a id="configure-recipients"></a>
## 수신자 설정하기 (Configure recipients)

이 예시에서는 편집 대상인 `Alert` 객체의 속성으로 저장된 담당자에게 알림을 보냅니다. 이를 위해 **Recipients** 드롭다운에서 "Recipient(s) from property of object parameter" 옵션을 사용합니다. 액션의 파라미터로 제공되는 `Alert` 객체를 선택하고, 이어서 속성을 고르라는 안내가 나오면 `Case managers` 속성을 선택합니다.

설정의 **Recipients** 섹션에 선택한 객체 파라미터와 속성이 표시되어야 합니다. 수신자는 항상 Foundry 사용자 ID여야 한다는 점을 기억하세요. 이 속성에 문자열 이메일 주소 같은 다른 값이 들어 있으면 알림이 전송되지 않습니다.

테스트 단계에서는 처음에 액션을 하드코딩된 수신자로 설정해, 로직과 알림 내용이 예상대로 구성되었는지 검증해 볼 수도 있습니다.

![하드코딩된 수신자](https://www.palantir.com/docs/resources/foundry/action-types/side_effects_notification_tutorial_static_test_user.png)

[다른 수신자 설정 옵션에 대해 더 알아보세요.](02_notifications.md#recipients)

> **중간 요약**: Rules에서 Notification 규칙을 추가하고, 수신자는 "객체 파라미터의 속성" 방식으로 Alert의 `Case managers`를 지정합니다. 테스트할 때는 자신을 고정 수신자로 넣어 보는 방법이 편리합니다.

<a id="configure-notification-content"></a>
## 알림 내용 설정하기 (Configure notification content)

다음으로 알림 내용을 설정합니다. 수신자를 이름으로 부르고, `Alert` 객체의 이전 우선순위와 새 우선순위를 내용에 포함하도록 알림을 구성합니다. 아래에 알림 설정 예시가 있습니다.

먼저 내용 옵션에서 "Template"을 선택합니다. 이것이 내용을 설정하는 가장 간단한 방법이며 코드를 작성할 필요가 없습니다.

제목 줄에는 원하는 메시지를 입력합니다. 파라미터 참조를 추가하려면 슬래시 `/`를 입력하고 드롭다운 목록에서 원하는 파라미터를 선택합니다. 객체 파라미터를 선택하면 어떤 속성을 참조할지 고르라는 안내가 나옵니다.

본문에는 수신자를 이름으로 부르고, 변경한 사용자를 밝히고, 이전 상태와 업데이트된 상태를 알려 주는 텍스트를 입력합니다.

제목에서 객체를 참조할 때와 마찬가지로, 드롭다운 목록에서 "Recipient"(수신자), "Current User"(현재 사용자) 및 각종 파라미터 옵션을 선택해 해당 사용자 속성에 대한 올바른 참조를 생성할 수 있습니다.

[더 복잡한 요구사항을 가진 알림 내용을 생성하는 방법을 알아보세요.](02_notifications.md#content)

**설명**: 예를 들어 본문을 "{{{Recipient 이름}}}님, {{{Current User 이름}}}님이 {{{alert.title}}}의 우선순위를 {{{alert.priority}}}에서 {{{new priority 파라미터}}}(으)로 변경했습니다."처럼 구성할 수 있습니다(실제 참조 구문은 드롭다운으로 자동 생성됩니다). 여기서 `alert.priority`는 편집 적용 전 값이므로 "이전 우선순위"로 쓰기에 적합하고, 새 우선순위는 파라미터 값에서 가져옵니다.

<a id="configure-a-link"></a>
## 링크 설정하기 (Configure a link)

마지막으로 Object Explorer에서 지정된 `Alert`의 Object View로 가는 링크를 추가합니다. "Object View"를 선택한 다음 드롭다운에서 티켓 객체 파라미터를 선택합니다. 그리고 링크 버튼의 라벨을 `View Ticket`으로 입력합니다.

이제 전체 알림 설정을 저장할 준비가 되었습니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/side_effects_notification_tutorial_updated_full_finished_configuration.png" alt="전체 설정" width="400" />

[설정할 수 있는 다른 링크 유형에 대해 더 알아보세요.](02_notifications.md#content)

> **중간 요약**: 내용은 Template 방식으로, `/`를 눌러 파라미터와 Recipient, Current User를 참조하며 작성합니다. 링크는 Alert의 Object View로 걸고 버튼 라벨을 `View Ticket`으로 정한 뒤 저장합니다.

<a id="send-a-test-notification"></a>
## 테스트 알림 보내기 (Send a test notification)

확인을 위해 자신을 담당자로 지정한 테스트 알림(Alert)을 만듭니다. 액션을 실행하려면 [액션 문서](https://www.palantir.com/docs/foundry/workshop/actions-overview/)에서 설명한 대로 Object Explorer에서 액션을 노출하거나 Workshop 모듈의 버튼으로 노출해야 합니다.

테스트 변경을 하고 나면, 플랫폼 내 푸시 알림과 함께 Foundry 사용자 프로필에 지정된 이메일 계정으로 이메일 알림을 받게 됩니다. 플랫폼 내 알림과 이메일 알림의 미리보기는 모두 알림 설정 화면 안에 표시됩니다.

이메일을 받지 못했다면 이메일 알림 또는 플랫폼 내 알림을 꺼 두었기 때문일 수 있습니다. **User Settings**(사용자 설정)의 **Notifications**에서 확인할 수 있습니다.

<a id="next-steps"></a>
## 다음 단계 (Next steps)

* 수신자가 이메일로 알림을 받도록 선택한 경우를 위한 [사용자 정의 내용](02_notifications.md#content-components) 같은 다른 선택 기능을 살펴보세요.
* [함수](../../04_functions/09_language-agnostic-features/03_configure-notifications.md)를 사용해 수신자나 내용에 대한 복잡한 로직을 설정해 보세요.

## 정리

- 우선순위 변경 액션의 Rules에 **Notification** 규칙을 추가하는 것으로 시작합니다.
- 수신자는 `Alert` 객체 파라미터의 `Case managers` 속성(Foundry 사용자 ID)으로 지정하며, 테스트 때는 고정 수신자를 쓸 수 있습니다.
- 내용은 Template으로 작성하고 `/`로 파라미터, Recipient, Current User를 참조합니다.
- Object View 링크 버튼(`View Ticket`)을 추가하고 저장한 뒤, Object Explorer나 Workshop에서 액션을 실행해 플랫폼 내 알림과 이메일을 확인합니다.
