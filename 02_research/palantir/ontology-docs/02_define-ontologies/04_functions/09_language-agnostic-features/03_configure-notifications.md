# 알림 구성하기 (Configure notifications)

- 원문: https://www.palantir.com/docs/foundry/functions/configure-notifications/
- 사이드바 위치: Define Ontologies > Functions > Language-agnostic features > Configure notifications

이 페이지는 함수(function)를 사용해 Foundry 안에서 보낼 알림(notification)의 내용과 받는 사람을 유연하게 구성하는 방법을 다룹니다. 알림 내용을 직접 만들어 반환하는 방법, 함수 안에서 사용자와 그룹을 조회하는 방법, 알림을 받을 사람(수신자) 목록을 반환하는 방법을 예제와 함께 설명합니다. 고정된 문구가 아니라 객체의 속성 값에 따라 달라지는 알림을 보내야 할 때 필요한 기능입니다.

함수를 사용하면 플랫폼 안에서 보낼 알림을 유연하게 구성할 수 있으며, 여기에는 사용자의 이메일 주소로 외부에 보내는 알림도 포함됩니다.

함수에서 알림을 구성할 때는 `Principal`(`User` 또는 `Group`을 나타냄) 타입과 `notification` 타입을 사용합니다. 이 섹션을 진행하면서 다음 참조 문서가 도움이 될 수 있습니다.

* [Principal, User, Group 타입](../04_types-reference.md#users-groups-and-principals)에 대한 참조
* [notification 타입](../04_types-reference.md#notification)에 대한 참조

**설명**: 주체(principal)는 권한이나 알림의 대상이 될 수 있는 존재를 통칭하는 보안 용어입니다. Foundry에서는 개별 사용자(`User`)와 사용자 묶음(`Group`)이 모두 `Principal`에 속합니다. 프로그래밍으로 보면 `Principal`은 `User`와 `Group` 두 경우를 담을 수 있는 합 타입(union type)입니다.

<a id="define-a-custom-notification"></a>
### 사용자 지정 알림 정의하기 (Define a custom notification)

온톨로지에 `User`에게 할당될 수 있는 `Issue` 객체가 있다고 가정합니다. 해당 `User`에게 보낼 알림을 정의하고 그 안에 `Issue`의 세부 정보를 담는 함수를 만들 수 있습니다.

```typescript tab="TypeScript v2"
import { NotificationLink, Notification } from "@osdk/functions";
import { Issue } from "@ontology/sdk";
import type { Osdk } from "@osdk/api";

export default function createIssueNotification(issue: Osdk.Instance<Issue>): Notification {
    // 플랫폼 안의 Issue 객체로 연결되는 링크
    const links: NotificationLink[] = [
        {
            label: "Issue",
            linkTarget: {
                type: "object",
                object: issue
            }
        }
    ]

    const platformNotification = {
        heading: "New issue",
        content: "A new issue has been assigned to you.",
        links: links
    }

    // 이메일 본문을 정의합니다. 본문에는 데이터 표 같은 headless HTML을 넣을 수 있습니다
    const emailBody = `Hello,

A new issue has been assigned to you: ${issue.description}.`;

    const emailNotification = {
        subject: "New issue",
        body: emailBody,
        links: links
    }

    return {
        platformNotification: platformNotification,
        emailNotification: emailNotification
    }
}
```

(원문에는 `ShortNotification.builder()`와 `EmailNotificationContent.builder()` 같은 빌더 패턴으로 같은 알림을 만드는 TypeScript v1 버전과, `PlatformNotification`, `EmailNotification` 클래스를 사용하는 Python 버전도 있습니다. TypeScript v1 버전은 `User`도 입력으로 받아 이메일 본문에 `user.firstName`을 넣고, Python 버전은 객체 링크를 포함하는 알림이면 반환 타입에 객체 타입을 선언해야 한다는 점(`Notification[Issue]`)을 주석으로 설명합니다.)

**설명**: 이 함수는 `Issue` 객체 하나를 입력받아 `Notification` 값을 반환합니다. 알림은 두 부분으로 구성됩니다. `platformNotification`은 Foundry 화면 안에 표시되는 짧은 알림(제목 `heading`, 내용 `content`)이고, `emailNotification`은 이메일로 보내는 알림(제목 `subject`, 본문 `body`)입니다. 두 부분 모두 `links`를 통해 알림을 받은 사람이 해당 `Issue` 객체로 바로 이동할 수 있게 합니다. 이메일 본문은 템플릿 문자열로 만들기 때문에 `${issue.description}`처럼 객체의 속성 값을 넣을 수 있습니다. 예를 들어 description이 "로그인 오류"인 Issue라면 본문이 "A new issue has been assigned to you: 로그인 오류."가 됩니다.

> **중간 요약**: 함수가 `Notification`을 반환하면 플랫폼 안 알림과 이메일 알림의 내용을 코드로 정의할 수 있습니다. 객체 링크와 속성 값을 넣어 객체마다 다른 알림을 만들 수 있습니다.

<a id="retrieve-users-and-groups"></a>
### 사용자와 그룹 조회하기 (Retrieve users and groups)

함수에 `User`를 입력으로 전달받는 것 외에도, 필요할 때 `User`나 `Group`을 조회할 수 있습니다. `Issue` 객체에 사용자 ID를 담는 `assignee` 필드가 있다고 가정합니다. 아래 예제에서 함수는 사용자에게 이슈를 상기시키는 알림을 반환합니다.

```typescript tab="TypeScript v2"
import { NotificationLink, Notification } from "@osdk/functions";
import { Users } from "@osdk/foundry.admin";
import { Issue } from "@ontology/sdk";
import { Client } from "@osdk/client";
import type { Osdk } from "@osdk/api";

export default async function createIssueReminderNotification(client: Client, issue: Osdk.Instance<Issue>): Promise<Notification> {
    const user = await Users.get(client, issue.assignee);

    const emailBody = `Hello, ${user.firstName},

This is a reminder to investigate the following issue: ${issue.description}`;

    // 이 구조를 사용해 알림 전체를 인라인으로 만들 수도 있습니다
    const links: NotificationLink[] = [
        {
            label: "Issue",
            linkTarget: {
                type: "object",
                object: issue
            }
        }
    ]

    // 이 구조를 사용해 알림 전체를 인라인으로 만들 수도 있습니다
    return {
        platformNotification: {
            heading: "Issue reminder",
            content: "Investigate this issue.",
            links:  links
        },
        emailNotification: {
            subject: "New issue",
            body: emailBody,
            links: links
        }
    }
}
```

(원문에는 `Users.getUserByIdAsync`로 사용자를 조회하고 assignee가 없으면 `UserFacingError`를 던지는 TypeScript v1 버전과, `client.admin.User.get`으로 사용자를 조회하는 Python 버전도 있습니다.)

**설명**: 핵심 줄은 `Users.get(client, issue.assignee)`입니다. `Issue` 객체의 `assignee` 속성에는 사용자 ID 문자열만 들어 있으므로, 이 ID로 Foundry의 사용자 정보를 조회해 이름(`firstName`) 같은 세부 정보를 얻습니다. 데이터베이스로 보면 `issue.assignee`는 사용자 테이블을 가리키는 외래 키이고, `Users.get`은 그 키로 사용자 행을 찾아오는 조회입니다.

<a id="return-recipients"></a>
### 수신자 반환하기 (Return recipients)

앞에서 설명한 `Notification` API를 사용하면 사용자 지정 알림 내용을 반환할 수 있습니다. 함수로 알림을 구성하는 또 다른 방법은 알림을 받을 수신자 목록을 반환하는 것입니다. 이렇게 하려면 `User`나 `Group` 객체 같은 `Principal` 객체를 하나 이상 반환하는 함수를 만듭니다.

아래 예제에서 함수는 이슈를 보고한 사용자와 현재 이슈에 할당된 사용자를 모두 반환합니다.

```typescript tab="TypeScript v2"
import { UserId, Principal } from "@osdk/functions";
import { Users, Groups } from "@osdk/foundry.admin";
import { Issue } from "@ontology/sdk";
import { Client } from "@osdk/client";
import type { Osdk } from "@osdk/api";

/**
 * Issue를 받아, 현재 담당자와 이슈를 처음 보고한 사용자를 나타내는 사용자 목록을 반환합니다.
 */
async function getIssueAssigneeAndReporter(client: Client, issue: Osdk.Instance<Issue>): Promise<UserId[]> {
    const user = await Users.get(client, issue.assignee);
    const issueReporter = await Users.get(client, issue.reporter);

    return [user.id, issueReporter.id];
}

/**
 * Issue를 받아, 현재 담당자인 사용자와 이슈가 속한 그룹을 반환합니다.
 */
async function getIssueAssigneeAndGroups(client: Client, issue: Osdk.Instance<Issue>): Promise<Principal[]> {
    // 그룹과 사용자를 함께 반환하려면 Principal 타입을 반환합니다.

    const user = await Users.get(client, issue.assignee);
    const group = await Groups.get(client, issue.group);

    return [{type: "user", id: user.id}, {type: "group", id: group.id}];
}
```

(원문에는 `User[]`를 반환하는 TypeScript v1 버전과, `Array[UserId]`, `Array[Principal]`을 반환하는 Python 버전도 있습니다.)

**설명**: 첫 번째 함수는 사용자만 반환하므로 반환 타입이 `UserId[]`(사용자 ID 배열)입니다. 두 번째 함수는 사용자와 그룹을 섞어 반환해야 하므로 `Principal[]`을 쓰고, 각 원소에 `type: "user"` 또는 `type: "group"`을 붙여 어느 쪽인지 구분합니다. 예를 들어 담당자가 사용자 `u-123`, 이슈 그룹이 `g-ops`라면 반환값은 `[{type: "user", id: "u-123"}, {type: "group", id: "g-ops"}]`이고, 알림은 그 사용자와 그룹 구성원 전체에게 전달됩니다.

> **중간 요약**: 함수 안에서 사용자 ID로 `User`나 `Group`을 조회해 알림 내용에 활용할 수 있습니다. 알림 내용 대신 수신자 목록(`UserId[]` 또는 `Principal[]`)을 반환하는 함수로도 알림을 구성할 수 있습니다.

## 정리

- 함수로 플랫폼 안 알림과 이메일 알림을 구성할 수 있으며, `Principal`(`User`, `Group`) 타입과 `notification` 타입을 사용합니다.
- `Notification`을 반환하는 함수는 플랫폼 알림(제목, 내용)과 이메일 알림(제목, 본문)을 함께 정의하고, 객체 링크와 속성 값을 넣을 수 있습니다.
- 객체에 저장된 사용자 ID로 `User`나 `Group`을 조회해 이름 같은 정보를 알림에 넣을 수 있습니다.
- 알림 내용 대신 수신자 목록을 반환하는 함수를 만들어 누가 알림을 받을지 결정할 수도 있습니다.
