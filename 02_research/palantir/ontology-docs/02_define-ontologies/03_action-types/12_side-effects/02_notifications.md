# 알림 (Notifications)

- 원문: https://www.palantir.com/docs/foundry/action-types/notifications/
- 사이드바 위치: Define Ontologies > Action types > Side effects > Notifications

이 페이지는 액션 타입(action type)에 부수 효과(side effect)로 알림(notification)을 붙이는 방법을 설명합니다. 액션이 실행될 때 누구에게(수신자), 무엇을(내용) 보낼지 설정하는 옵션과, 수신자 수와 내용 길이 제한, 권한 검사, 이메일 내용 가림(redaction) 같은 운영상의 제약을 다룹니다. 액션으로 데이터를 바꾼 뒤 관련 담당자에게 자동으로 알려야 하는 업무 흐름을 만들 때 필요한 내용입니다.

알림은 **Add new rule**(새 규칙 추가) 드롭다운 메뉴를 통해 액션에 추가할 수 있습니다. [알림을 추가하는 방법을 더 알아보세요.](03_set-up-notification.md)

<img src="https://www.palantir.com/docs/resources/foundry/action-types/side_effects_notification_tutorial_edit_action_rules.png" alt="Add new rule 드롭다운 메뉴" width="500" />

알림을 설정하려면 [수신자](#recipients)와 [내용](#content)을 지정해야 합니다. 다음 섹션에서 이 옵션들을 자세히 설명합니다.

**설명**: 액션 타입의 규칙(rule)은 액션이 실행될 때 수행할 작업의 목록입니다. "객체의 속성 값 수정" 같은 규칙은 온톨로지 데이터를 바꾸고, 알림 규칙은 데이터를 바꾸지 않고 바깥(사용자의 받은 알림함, 이메일)으로 메시지를 내보냅니다. 데이터 변경 외에 따라 일어나는 이런 작업을 부수 효과(side effect)라고 부릅니다.

<a id="recipients"></a>
## 수신자 (Recipients)

알림의 **Recipients**(수신자) 옵션을 설정하면 액션이 실행될 때 알림을 받을 Foundry 사용자 집합을 지정할 수 있습니다. 알림은 각 수신자에게 개별적으로 전송됩니다. 이메일 알림에 사용자를 참조(CC, carbon copy) 수신자로 추가하는 기능은 지원되지 않습니다.

수신자를 지정하는 방법은 여러 가지가 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/side_effects_recipients_selector.png" alt="Recipients 드롭다운" width="400" />

* **고정(Static):** 설정에서 액션이 실행될 때마다 항상 알림을 받을 사용자나 그룹 집합을 선택할 수 있습니다.
* **파라미터에서(From a parameter):** 액션에 Foundry 사용자 ID나 그룹 ID를 값으로 갖는 파라미터가 있다면, 그 파라미터를 알림의 수신자로 지정할 수 있습니다.
  * 이 방법을 쓰면 이 액션을 사용하는 애플리케이션이나 모듈의 사용자 인터페이스에서 발신자가 한 명 이상의 수신자를 직접 고르게 하거나, 액션을 실행하는 사용자를 자동으로 감지해 그 사용자에게 알림을 보낼 수 있습니다.
* **객체 파라미터의 속성에서(From an attribute of an object parameter):** 액션에 객체 파라미터가 있고 그 객체의 속성 중 하나에 Foundry 사용자 ID나 그룹 ID가 들어 있다면, 파라미터의 그 속성을 수신자로 지정할 수 있습니다. Foundry 사용자 ID와 그룹 ID의 목록(list)에 대해서도 가능합니다.
* **함수에서(From a function):** 위 옵션들로 해결되지 않는 사용 사례라면, 액션 파라미터를 입력받아 알림을 받을 사용자나 그룹의 목록을 반환하는 사용자 정의 함수(function)를 작성할 수 있습니다. [사용자나 그룹의 목록을 반환하는 함수를 작성하는 방법을 더 알아보세요.](../../04_functions/04_types-reference.md#users-groups-and-principals)

  함수 기반 수신자의 사용 사례 예시는 다음과 같습니다.

  * 다른 수신자 옵션을 조합하는 경우. 예를 들어 객체 파라미터의 속성에서 지정한 `assignee`에게 알리면서, 고정된 추가 수신자 집합에게도 항상 알리는 경우입니다.
  * 다른 파라미터나 파라미터의 속성 값에 따라 수신자를 고르는 경우. 예를 들어 EMEA 지역에 새 작업이 생길 때마다 한 사용자 집합에 알리고, 북미 지역에 새 작업이 생길 때마다 다른 사용자 집합에 알리는 경우입니다.
  * 그 밖에 구조화된 옵션에 맞지 않는 모든 사용자 정의 로직.

**주의**: 수신자는 알림을 전달받는 방식에 대한 자신의 환경설정을 바꿀 수 있습니다. 예를 들어 어떤 사용자는 웹 브라우저로만 알림을 받도록 선택하고, 다른 사용자는 플랫폼 내 토스트(toast)와 이메일을 모두 받도록 선택할 수 있습니다. 개인 환경설정에서 액션 알림을 꺼 둔 사용자는 알림을 받지 못합니다. 다만 Foundry에 로그인한 상태에서 Workspace의 "Notifications"로 가서 "See All"을 선택하면 자신의 알림을 볼 수 있습니다.

**설명**: 수신자를 정하는 네 방식은 "수신자 목록을 어디서 얻느냐"의 차이입니다. 예를 들어 `Alert` 객체에 `assignee` 속성이 있고 값이 사용자 ID 문자열(예: `"a1b2c3..."`)이라면, 세 번째 방식은 액션이 받은 Alert 객체에서 그 속성 값을 꺼내 수신자로 씁니다. 함수 방식은 입력(액션 파라미터)을 받아 출력(사용자/그룹 ID 목록)을 돌려주는 코드를 직접 작성하는 것이므로 가장 자유롭습니다. 토스트는 화면 구석에 잠깐 떴다 사라지는 작은 알림 창을 뜻하는 UI 용어입니다.

> **중간 요약**: 수신자는 고정 목록, 사용자/그룹 파라미터, 객체 파라미터의 속성, 사용자 정의 함수 네 가지 방식으로 지정합니다. 알림은 수신자마다 개별 전송되며, 실제 전달 방식은 각 수신자의 환경설정을 따릅니다.

<a id="content"></a>
## 내용 (Content)

알림 내용을 사용자 정의하는 옵션은 여러 가지가 있습니다. 내용은 *템플릿(Template)으로* 설정하거나 사용자 정의 *함수(function)로* 제공할 수 있습니다. 템플릿 내용을 선택하면 설정 대화상자에서 전체 내용을 직접 구성할 수 있습니다. 함수 내용을 쓰려면 적절한 알림 타입을 반환하는, 게시(publish)된 함수가 있어야 합니다.

![Content 타입 드롭다운](https://www.palantir.com/docs/resources/foundry/action-types/side_effects_content_selection_dropdown.png)

<a id="content-components"></a>
### 내용 구성 요소 (Content components)

1. **제목(Subject):** 내용에는 보통 제목 줄이 포함됩니다. 기본적으로 제목은 모든 전달 방식에서 동일합니다.

2. **본문(Body):** 알림의 본문입니다. 플랫폼 내 알림에서는 알림 토스트 안에 표시됩니다. 이메일에서는 이메일 본문 안에 렌더링됩니다.

3. **링크(Link):** 링크를 지정할 수 있습니다. 링크는 알림 본문 바로 아래에 버튼으로 나타납니다. 버튼의 텍스트는 사용자 정의할 수 있습니다.
   * 링크를 설정할 때 사용할 수 있는 옵션은 다음과 같습니다.
     * 기존 객체 파라미터로 연결
     * Workshop 앱으로 연결
     * Carbon 워크스페이스로 연결
     * 새로 생성된 객체로 연결

4. **고급 이메일 설정(Advanced Email Configuration):** 알림을 설정할 때 이메일로 알림을 전달하는 경우에 사용할 별도의 본문 내용을 지정할 수 있습니다. 이 옵션을 쓰면 플랫폼 내 알림에서는 지원되지 않는 고급 서식을 HTML로 작성할 수 있습니다. 미리보기는 파라미터 참조를 제외하고 알림이 어떻게 보일지를 보여 줍니다. 수신자는 이메일로 알림을 받도록 환경설정한 경우에만 이 내용을 받습니다.

**참고**: 위에서 말한 제목, 본문, 링크에서 파라미터와 사용자 속성을 참조할 때 삼중 핸들바(triple handlebars)를 사용할 수 있습니다. 섹션을 편집할 때 사용 가능한 파라미터 중 하나를 클릭하면 해당 파라미터나 사용자 속성에 대한 올바른 핸들바 참조가 자동으로 생성됩니다.

**설명**: 핸들바(Handlebars)는 `{{이름}}` 형태의 자리표시자를 실제 값으로 치환하는 템플릿 문법입니다. 삼중 핸들바 `{{{alert.priority}}}`는 HTML 이스케이프 없이 값을 그대로 넣는 형태입니다. 예를 들어 제목이 `우선순위 변경: {{{alert.title}}}`이고 액션에 전달된 Alert 객체의 title이 "서버 다운"이면, 실제로 전송되는 제목은 "우선순위 변경: 서버 다운"이 됩니다.

5. **함수에서(From a Function):** "From a Function"을 선택하면 위에 나열한 섹션들을 설정하지 않습니다. 대신 사용자 정의 내용의 각 섹션을 지정하는 적절한 속성들을 가진 `Notification` 객체를 반환하는 함수를 제공해야 합니다. 다음 중 하나라도 해당하면 함수를 사용해야 할 수 있습니다.
   * 수신자나 액션의 입력 파라미터에 따라 알림 내용이 완전히 달라지는 경우.
   * 이메일 알림과 플랫폼 내 알림에 서로 다른 제목 줄을 쓰고 싶은 경우.
   * 외부 시스템이나 Foundry 바깥에 있는 애플리케이션으로 가는 링크를 포함해 전체 링크 URL을 쓰고 싶은 경우.
   * 내용을 렌더링할 때 Search Around, 집계(aggregation), 또는 파라미터로 제공되는 것 이상의 데이터 조회를 하고 싶은 경우.
   * 템플릿 내용 옵션으로는 불가능한 기타 사용자 정의 요구사항이 있는 경우.

Notification 반환 타입에 대한 자세한 정보는 [함수 문서](../../04_functions/09_language-agnostic-features/03_configure-notifications.md)에서 확인할 수 있습니다.

**주의**: 알림 내용을 생성하는 데 쓰이는 온톨로지 데이터는 현재 액션의 편집(edit)이 적용되기 **전의** 온톨로지 상태를 반영합니다. 알림 수신자가 특정 객체의 최신 상태를 볼 수 있게 하려면, 객체 파라미터로 참조된 객체로 가는 링크나, 새로 생성된 객체로 가는 링크(그 객체가 함수가 아니라 "create object" 규칙으로 생성된 경우)를 알림에 넣을 수 있습니다.

**설명**: 이 주의 사항은 실행 순서 때문에 생깁니다. 예를 들어 Alert의 priority를 "Low"에서 "High"로 바꾸는 액션에서, 알림 내용에 `{{{alert.priority}}}`를 넣으면 편집 전 값인 "Low"가 들어갈 수 있다는 뜻입니다. 새 값을 보여 주려면 객체 속성 대신 새 우선순위를 담은 파라미터를 직접 참조하거나, 링크를 넣어 수신자가 최신 상태를 열어 보게 합니다.

> **중간 요약**: 내용은 템플릿(제목, 본문, 링크, 이메일용 HTML)으로 직접 구성하거나, `Notification` 객체를 반환하는 함수로 만듭니다. 템플릿에서는 삼중 핸들바로 파라미터를 참조하며, 알림에 쓰이는 온톨로지 데이터는 편집 적용 전 상태라는 점에 주의해야 합니다.

***

<a id="example-configuration"></a>
## 설정 예시 (Example configuration)

다음은 알림 설정의 예시입니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/side_effects_numbered_example_configuration.png" alt="번호가 붙은 알림 설정 예시" width="400" />

1. **Recipients**(수신자) 설정
2. **Content**(내용) 설정
   * 템플릿(Ontology 앱 대화상자에서 직접 설정) 또는 함수(완전한 형태의 `Notification` 객체를 반환하는 함수를 지정) 중에서 선택합니다.
3. 템플릿 알림의 **제목(Subject)** 줄.
4. 액션에서 사용할 수 있는 파라미터를 기준으로 한 사용 가능한 **파라미터** 목록. 파라미터를 클릭하면 그 파라미터를 참조하는 `{{{}}}` 구문이 생성됩니다.
5. 템플릿 알림의 **본문(Body)** 내용.
6. 템플릿 알림의 **링크(Link)** 설정(선택 사항).
7. 템플릿 알림에서 **이메일용 사용자 정의 HTML 내용**(선택 사항).

> **중간 요약**: 하나의 알림 설정 화면에서 수신자, 내용 방식, 제목, 파라미터 목록, 본문, 링크, 이메일용 HTML을 차례로 구성합니다.

***

<a id="other-key-information"></a>
## 기타 주요 정보 (Other key information)

<a id="maximum-recipient-limits"></a>
### 최대 수신자 수 제한 (Maximum recipient limits)

* 알림 내용을 "From a Function" 옵션으로 렌더링할 때는 수신자가 최대 50명입니다. 내용 설정 옵션에서 "From a Function"을 선택하면 설정 패널에 경고가 표시되고, 액션이 실행될 때마다 수신자 수를 검사합니다. 수신자 수가 한도를 넘으면 빨간색 오류 토스트가 표시되고 액션 실행이 실패합니다.
* "Template" 옵션을 사용해 설정 대화상자에서 내용을 직접 구성한 경우, 액션 알림 하나당 수신자는 최대 500명입니다.

![함수로 렌더링한 내용의 최대 수신자 수 경고](https://www.palantir.com/docs/resources/foundry/action-types/side_effects_function_content_max_recipients.png)

<a id="content-length-limits"></a>
### 내용 길이 제한 (Content length limits)

* 제목의 최대 길이는 250자입니다.
* 본문의 최대 길이는 1,000자입니다. 이메일용 사용자 정의 HTML 내용을 렌더링할 때의 최대 길이는 51,200자입니다.

이 최대 길이는 알림이 렌더링될 때 검증되고 잘린다는 점을 기억하세요. 즉, 렌더링되는 내용이 동적인 경우(예: 알림 내용에 객체 데이터가 포함된 경우) 허용된 최대 길이를 넘는 부분은 잘리고 끝에 `...`가 붙어 표시됩니다.

<a id="strict-redaction"></a>
### 엄격한 가림 처리 (Strict redaction)

Foundry 인스턴스에서 외부로 나가는 이메일 알림에 "Strict Redaction" 또는 "Group Redaction"이 활성화되어 있으면 사용자 정의 알림 내용은 렌더링되지 않습니다. 대신 사용자는 아래와 같은 일반 메시지를 받습니다. "View"를 선택하면 Foundry로 이동해 전체 알림 내용을 볼 수 있습니다. [Foundry의 이메일 내용 가림 처리에 대해 더 알아보세요.](https://www.palantir.com/docs/foundry/email/email-content-redaction/)

![엄격한 가림 처리 시 기본 이메일 내용](https://www.palantir.com/docs/resources/foundry/action-types/side_effects_redacted_email_content.png)

**설명**: 가림 처리(redaction)는 민감한 데이터가 이메일처럼 Foundry 바깥으로 나가는 경로에 실리지 않도록 본문을 일반 문구로 대체하는 보안 기능입니다. 이메일은 한번 발송되면 Foundry의 권한 검사가 미치지 않는 곳(개인 메일함, 전달된 메일 등)에 남기 때문입니다.

<a id="recipient-user-accounts"></a>
### 수신자 사용자 계정 (Recipient user accounts)

* 알림을 보내기 전에 데이터에 대한 권한을 검사하기 위해, 그룹은 개별 사용자로 풀어서(resolve) 처리됩니다.
* Foundry 사용자 ID와 그룹 ID는 Settings의 Account에서 찾을 수 있습니다. 알림 설정 인터페이스는 고정 수신자 집합을 고를 때 사용자와 그룹 선택기를 제공합니다. 선택기에는 액션을 설정하는 사람이 충분한 권한을 가진 사용자와 그룹만 표시됩니다.
* 수신자를 객체 속성 참조로 설정했다면, 그 속성이 Foundry 사용자 ID나 그룹 ID를 문자열(string)로 저장하는지 확인하세요. 조건부 서식을 사용해 연결된 사용자나 그룹의 표시 이름을 보여 줄 수 있습니다(자세한 내용은 [값 서식 문서](../../02_object-and-link-types/03_properties/03_value-formatting.md)를 참고하세요).
* 이메일 주소로 직접 보내는 기능은 지원되지 않습니다.

<a id="links-to-newly-created-objects"></a>
### 새로 생성된 객체로 가는 링크 (Links to newly-created objects)

새 객체로 링크를 걸 때는 그 객체의 기본 키(primary key)를 참조해야 합니다. 알림이 렌더링되는 시점에는 아직 객체 RID가 생성되지 않았기 때문입니다.

**예시:** 새 `task` 객체를 생성하고, 작업을 생성할 때 고유 ID를 만들어 내는 액션이 있다고 합시다. 액션 알림 안에서 [Object Explorer가 제공하는 파라미터 옵션](../../../05_applications/01_object-explorer/05_generate-urls.md)을 사용해 새로 생성된 객체로 가는 링크를 렌더링합니다.

* 함수가 생성하는 내용을 사용할 때 URL 링크를 지정하는 방법은 두 가지가 지원됩니다.
  * 전체 링크 예시: `https://<your-foundry-instance>.com/workspace/module/view/latest/<module-rid>`
  * 상대 링크 예시: `/module/view/latest/<module-rid>`

**설명**: RID(Resource Identifier)는 Foundry가 리소스와 객체마다 내부적으로 부여하는 식별자입니다. 반면 기본 키는 액션이 객체를 만들 때 이미 정해져 있는 값(예: 파라미터로 받은 `task_id = "T-1024"`)입니다. 알림 렌더링 시점에 확실히 알 수 있는 값은 기본 키뿐이므로, 링크도 기본 키로 객체를 찾도록 만들어야 합니다.

<a id="required-data-access-for-recipients"></a>
### 수신자에게 필요한 데이터 접근 권한 (Required data access for recipients)

* 사용자는 자신이 볼 수 있도록 허용된 데이터가 담긴 알림만 받을 수 있습니다.
* 수신자가 여러 명인 경우, 모든 수신자가 알림 내용에 렌더링되는 객체 데이터에 접근할 수 있어야 합니다.
* 액션을 설정할 때 사이드바의 **Security & Submission Criteria** 탭 하단에서 알림 실패를 처리하는 두 가지 방법을 고를 수 있습니다.
  * **Require all users to have permissions(모든 사용자에게 권한 요구, 기본값):** 수신자 중 누구라도 필요한 접근 권한이 없으면 액션을 적용하려 할 때 오류가 표시됩니다. 이 경우 데이터는 편집되지 않고 알림도 전송되지 않습니다.
  * **Require any user to have permissions(한 명 이상에게 권한 요구):** 적어도 한 사용자가 객체를 볼 수 있으면 액션이 성공합니다. 권한이 있는 사용자만 알림을 받습니다.

<a id="override-and-disable-email-content-redaction"></a>
### 이메일 내용 가림 처리 재정의 및 비활성화 (Override and disable email content redaction)

[조직 설정이 허용하는 경우](https://www.palantir.com/docs/foundry/email/email-content-redaction/#disable-email-redaction-in-action-types), 특정 액션 타입에 대해 조직 수준에서 설정된 다른 엄격한 가림 처리 설정을 우회해, 가림 처리되지 않은 내용을 보내는 액션 타입을 만들 수 있습니다.

이메일 알림의 가림 처리를 재정의하려면 **Security & Submission** 탭으로 이동한 뒤 **Notification settings > Disable notification redaction**을 선택합니다.

![가림 처리 비활성화 옵션이 있는 알림 설정](https://www.palantir.com/docs/resources/foundry/action-types/notification_settings.png)

조직에서 이 기능을 활성화하는 방법은 [이메일 가림 처리 문서 페이지](https://www.palantir.com/docs/foundry/email/email-content-redaction/#disable-email-redaction-in-action-types)를 참고하세요.

> **중간 요약**: 수신자는 함수 내용일 때 50명, 템플릿일 때 500명까지이며, 제목 250자, 본문 1,000자(HTML 51,200자) 제한이 있습니다. 새 객체 링크는 기본 키로 걸어야 하고, 수신자 전원(또는 설정에 따라 일부)이 데이터 접근 권한을 가져야 하며, 조직 설정에 따라 이메일 가림 처리가 적용되거나 액션 타입 단위로 해제될 수 있습니다.

## 정리

- 알림은 액션 타입의 **Add new rule**로 추가하는 부수 효과이며, 수신자와 내용을 설정해야 합니다.
- 수신자는 고정 목록, 파라미터, 객체 파라미터의 속성, 함수 중 하나로 지정하고, 모두 Foundry 사용자/그룹 ID여야 합니다(이메일 주소 직접 지정 불가).
- 내용은 템플릿(제목, 본문, 링크, 이메일 HTML, 삼중 핸들바 참조) 또는 `Notification`을 반환하는 함수로 만듭니다.
- 알림에 쓰이는 온톨로지 데이터는 편집 적용 전 상태이며, 수신자 수와 내용 길이에 상한이 있습니다.
- 수신자의 데이터 접근 권한 검사와 이메일 가림 처리 설정이 실제 전송 여부와 내용을 좌우합니다.
