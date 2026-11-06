# 웹훅 (Webhooks)

- 원문: https://www.palantir.com/docs/foundry/action-types/webhooks/
- 사이드바 위치: Define Ontologies > Action types > Side effects > Webhooks

이 페이지는 액션에서 웹훅(webhook)을 사용해 Foundry 바깥의 외부 시스템으로 요청을 보내는 방법을 설명합니다. 웹훅을 라이트백(writeback)으로 쓸 때와 부수 효과(side effect)로 쓸 때의 실행 시점과 실패 처리 차이, 웹훅 입력 파라미터를 채우는 방법, 출력 파라미터를 후속 규칙에서 쓰는 방법, OAuth 2.0 인증을 다룹니다. Foundry에서 내린 결정을 Salesforce나 SAP 같은 원천 시스템에 되돌려 써야 하는 업무 흐름의 핵심 기능입니다.

[웹훅(webhook)은](https://www.palantir.com/docs/foundry/data-connection/webhooks-overview/) Data Connection의 개념으로, Salesforce, SAP 또는 설정된 임의의 HTTP 서버 같은 외부 시스템에 요청을 보낼 수 있게 해 줍니다. 보통 그 외부 시스템의 데이터를 수정하는 데 쓰입니다.

웹훅을 설정한 다음 액션에서 사용하도록 구성하면, 최종 사용자가 Foundry에서 액션을 적용할 때 외부 시스템으로 데이터를 보낼 수 있습니다. 이를 통해 Foundry의 업무 흐름이 원천 시스템과 직접 연결되어 데이터와 결정을 그 시스템에 다시 써 넣을(write back) 수 있습니다.

이 섹션은 액션에서 웹훅을 설정할 때 사용할 수 있는 여러 옵션을 자세히 설명합니다. 단계별 튜토리얼은 [액션에 웹훅을 추가하는 방법](05_set-up-webhook.md) 문서를 참고하세요.

**설명**: 웹훅은 여기서 "미리 정의해 둔 HTTP 요청 템플릿"을 뜻합니다. 예를 들어 `POST https://crm.example.com/api/tickets/{id}`에 `{"priority": "..."}` 본문을 보내는 요청을 Data Connection에 웹훅으로 등록해 두면, 액션은 빈칸(`id`, `priority`)에 들어갈 값만 채워 이 요청을 실행합니다. Data Connection은 Foundry가 외부 시스템과 연결(source)을 관리하는 애플리케이션입니다.

<a id="webhooks-writeback-vs-side-effect"></a>
## 웹훅: 라이트백과 부수 효과 비교 (Webhooks: Writeback vs. side effect)

웹훅을 액션에서 사용하도록 구성하는 방법은 **라이트백(writeback)과** **부수 효과(side effect)** 두 가지입니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/webhooks-add-webhook.png" alt="웹훅 추가" width="400" />

편의를 위해 라이트백 웹훅과 부수 효과 웹훅의 동작을 비교한 표를 아래에 둡니다.

| 유형 | 적용 시점 | 최종 사용자에게 실패가 표시되는가? | 타이밍 |
|--- |--- |--- |--- |
| **라이트백(Writeback)** | 객체 변경 전 | 예 | 사용자가 성공 또는 실패를 보기 전 |
| **부수 효과(Side effect)** | 객체 변경 후 | 아니요 | 사용자가 성공 메시지를 본 뒤일 수 있음 |

다음 섹션에서 라이트백 웹훅과 부수 효과 웹훅을 더 자세히 설명합니다.

<a id="writeback-webhooks"></a>
### 라이트백 웹훅 (Writeback webhooks)

**라이트백으로** 설정하면 웹훅은 다른 모든 규칙이 평가되기 *전에* 실행됩니다. 웹훅 실행이 실패하면 다른 변경은 일어나지 않습니다. 외부 시스템보다 먼저 Foundry에서 변경이 일어나지 않도록 보장하고 싶다면 웹훅을 라이트백으로 설정해야 합니다.

이 동작은 Foundry와 외부 시스템 사이에 어느 정도의 트랜잭션성(transactionality)을 제공합니다. 라이트백 웹훅을 사용하면 외부 시스템으로의 요청이 실패했을 때 Foundry 온톨로지에 아무 변경도 적용되지 않는다는 것이 보장됩니다. 하지만 외부 요청은 성공했는데 온톨로지 변경이 실패하는 경우는 여전히 일어날 수 있습니다.

라이트백 웹훅이 실패하면 액션 적용이 중단되기 때문에, 라이트백으로 설정할 수 있는 웹훅은 하나뿐입니다. 액션을 적용할 때 이 웹훅이 실패하면 최종 사용자에게 실패 내용을 설명하는 오류가 표시됩니다.

웹훅을 라이트백으로 설정하면 그 출력 파라미터를 이후 규칙에서 사용할 수 있습니다. 자세한 내용은 아래 [출력 파라미터](#output-parameters) 섹션을 참고하세요.

**설명**: 데이터베이스의 트랜잭션은 여러 변경을 "전부 성공하거나 전부 취소"되게 묶는 단위입니다. 두 개의 서로 다른 시스템(Foundry와 외부 CRM)에 걸친 변경은 하나의 트랜잭션으로 묶을 수 없으므로, 라이트백은 "외부 먼저, 실패하면 Foundry는 손대지 않음"이라는 순서만 보장합니다. 그래서 반대 경우(외부 성공, Foundry 실패)는 막지 못하며, 원문이 "어느 정도의" 트랜잭션성이라고 표현한 것입니다.

<a id="side-effect-webhooks"></a>
### 부수 효과 웹훅 (Side effect webhooks)

**부수 효과로** 설정하면 웹훅은 다른 규칙이 평가된 *후에* 실행됩니다. 즉, Foundry 객체에 대한 수정이 부수 효과보다 먼저 일어납니다. 하나의 액션에 부수 효과 웹훅을 여러 개 설정할 수 있으며, 이들은 특정한 순서 없이 실행됩니다. 부수 효과 웹훅이 있는 액션에서 최종 사용자는 Foundry 객체가 수정된 뒤 성공 메시지를 보게 되며, 부수 효과의 실행은 성공 메시지가 표시된 뒤에 일어날 수도 있습니다.

하나의 액션에서 웹훅을 여러 번 호출해야 한다면, 부수 효과 웹훅에 페이로드(payload) 목록을 입력으로 제공하면 됩니다. 그러면 제공된 목록에 들어 있는 페이로드 수만큼 웹훅이 트리거되며, 처리 순서는 보장되지 않습니다. 이에 대한 예시는 아래 [입력 파라미터](#input-parameters) 섹션에 있습니다.

최선 노력(best-effort) 방식의 알림을 보내거나 여러 외부 시스템에 라이트백해야 할 때는 부수 효과 웹훅을 사용해야 합니다.

**설명**: "최선 노력(best-effort)"은 전송을 시도하되 성공을 보장하지는 않는다는 뜻입니다. 부수 효과 웹훅이 실패해도 이미 적용된 Foundry 편집은 되돌려지지 않고 사용자에게 실패가 표시되지도 않으므로, 실패해도 업무에 치명적이지 않은 요청에 적합합니다.

> **중간 요약**: 라이트백 웹훅은 다른 규칙보다 먼저 실행되고, 실패하면 Foundry 편집도 일어나지 않으며 사용자에게 오류가 보입니다(액션당 하나만 가능). 부수 효과 웹훅은 객체 편집 후에 순서 없이 실행되고, 여러 개를 두거나 페이로드 목록으로 여러 번 호출할 수 있습니다.

<a id="input-parameters"></a>
## 입력 파라미터 (Input parameters)

액션에서 웹훅을 설정하려면 웹훅의 필수 입력 파라미터를 모두 채워야 합니다. 웹훅 입력 파라미터에 대한 일반 참고 자료는 [Data Connection 문서](https://www.palantir.com/docs/foundry/data-connection/webhooks-reference/#input-parameters)에 있습니다.

웹훅 입력 파라미터를 설정하는 방법은 액션 파라미터에 매핑하는 방법과 함수(function)를 사용하는 방법 두 가지입니다.

**액션 파라미터에** 매핑할 때는, 각 필수 웹훅 입력을 같은 타입의 액션 파라미터, 고정 값(static value), 또는 객체 파라미터의 속성 중 하나로 설정해야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/webhooks-input-parameters.png" alt="입력 파라미터" width="400" />

[함수](../../04_functions/01_overview.md)를 사용할 때는, 필수 웹훅 입력 파라미터를 모두 포함하고 웹훅 타입과 엄격하게 일치하는 사용자 정의 타입을 반환하는 함수를 선택해야 합니다. 그렇지 않으면 `OntologyMetadata:ActionWebhookInputsDoNotHaveExpectedType` 오류가 발생합니다. 함수로 웹훅 입력 파라미터를 채우는 방법은 로직을 사용해 입력을 채우고 싶을 때, 특히 그 로직이 온톨로지 객체에 기반할 때 유용합니다. 예를 들어 링크된 객체를 조회하고 그 객체들의 속성 값을 가져와 웹훅 입력을 미리 채울 수 있습니다.

예를 들어 ID가 `name`, `industry`, `country`인 입력 파라미터 세 개를 받는 웹훅이 있다고 합시다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/webhooks-input-parameters-example.png" alt="입력 파라미터 예시" width="400" />

이와 같은 구조의 사용자 정의 인터페이스를 반환하는 함수를 작성할 수 있습니다. (원문에는 `name`, `industry`, `country` 세 필드만 가진 `MyWebhookInput` 인터페이스 정의만 따로 보여 주는 코드가 있으며, 같은 정의가 아래 전체 예제에 포함되어 있습니다.)

그런 다음 액션에서 웹훅 입력을 설정할 때 이 함수를 선택하고, 액션 파라미터를 함수가 요구하는 파라미터에 매핑합니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/webhooks-input-parameters-define-using-action.png" alt="액션 파라미터를 함수가 요구하는 파라미터에 매핑하기" width="400" />

아래는 온톨로지 객체에서 데이터를 불러와 웹훅 입력을 채우는 함수의 전체 코드 예제입니다.

```typescript
import { Function, UserFacingError } from "@foundry/functions-api";
import { Company } from "@foundry/ontology-api";

export interface MyWebhookInput {
    name: string;
    industry: string;
    country: string;
}

export class MyWebhookFunctions {
    @Function()
    public returnWebhookInput(company: Company): MyWebhookInput {
        if (!company.name || !company.industry || !company.country) {
            throw new UserFacingError("Some required fields are not set.");
        }
        return {
            name: company.name,
            industry: company.industry,
            country: company.country,
        }
    }
}
```

**설명**: 이 함수는 `Company` 객체 하나를 입력받아, 웹훅이 요구하는 세 필드(`name`, `industry`, `country`)를 가진 `MyWebhookInput` 객체를 반환합니다. 반환 타입의 필드 이름과 타입이 웹훅 입력 파라미터와 정확히 일치해야 액션에서 이 함수를 선택할 수 있습니다. `if` 문은 세 속성 중 하나라도 비어 있으면 `UserFacingError`를 던지는데, 이 오류의 메시지는 액션을 실행한 최종 사용자 화면에 그대로 표시되므로, 불완전한 데이터로 외부 요청이 나가는 것을 막을 수 있습니다.

부수 효과 웹훅은 함수가 페이로드 목록을 반환하게 해서 여러 번 호출할 수 있습니다. 아래는 회사 두 곳을 입력으로 받아, 웹훅이 기대하는 입력 파라미터에 맞는 페이로드 두 개가 담긴 목록을 반환하는 함수 예시입니다. 액션에서 부수 효과 웹훅의 입력을 반환하는 데 이 함수를 사용하면 웹훅이 두 번 따로 실행됩니다.

```typescript
import { Function } from "@foundry/functions-api";
import { Company } from "@foundry/ontology-api";

export interface MyWebhookInput {
    arg1: string;
    arg2: string;
}

export class MyFunctions {
    @Function()
    public createWebhookRequest(company1: Company, company2: Company): MyWebhookInput[] {
        return [
        {
           arg1: company1.someProperty,
           arg2: company1.someOtherProperty,
        },
        {
           arg1: company2.someProperty,
           arg2: company2.someOtherProperty,
        }
        ];
    }
}
```

**설명**: 앞 예제와 달리 반환 타입이 배열 `MyWebhookInput[]`입니다. 배열의 원소 하나가 웹훅 호출 한 번의 입력이 되므로, 원소가 2개면 HTTP 요청이 2번 나갑니다. 이 방식은 부수 효과 웹훅에서만 가능하다는 점(라이트백은 액션당 한 번)에 주의하세요.

> **중간 요약**: 웹훅 입력은 액션 파라미터, 고정 값, 객체 파라미터의 속성에 매핑하거나, 웹훅 입력 구조와 정확히 일치하는 타입을 반환하는 함수로 채웁니다. 함수가 목록을 반환하면 부수 효과 웹훅이 원소 수만큼 실행됩니다.

<a id="output-parameters"></a>
## 출력 파라미터 (Output parameters)

웹훅을 [라이트백 웹훅](#writeback-webhooks)으로 설정한 경우 그 출력 파라미터를 이후 규칙에서 사용할 수 있습니다. 외부 시스템이 반환한 데이터를 곧바로 Foundry 객체에 쓰거나, 이후의 [알림](02_notifications.md) 또는 [부수 효과 웹훅](#side-effect-webhooks)에서 사용하고 싶을 때 유용합니다.

웹훅 출력 파라미터에 대한 일반 참고 자료는 [Data Connection 문서](https://www.palantir.com/docs/foundry/data-connection/webhooks-reference/#output-parameters)에 있습니다.

이후의 로직 규칙에서 출력 파라미터를 사용하려면, 로직 규칙의 값을 채울 때 **Writeback response**를 선택한 다음 사용하려는 특정 출력을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/webhooks-output-parameters-in-logic-rule.png" alt="로직 규칙에서 출력 파라미터 사용하기" width="400" />

**설명**: 예를 들어 외부 티켓 시스템에 새 티켓을 만드는 라이트백 웹훅이 응답으로 `{"ticket_number": "EXT-5531"}`을 돌려준다고 합시다. 이 값을 출력 파라미터로 받아 두면, 뒤따르는 "객체 생성" 규칙에서 Foundry의 Ticket 객체 `external_id` 속성에 "EXT-5531"을 저장할 수 있습니다. 라이트백만 이것이 가능한 이유는, 라이트백이 다른 규칙보다 먼저 실행되어 그 결과가 이미 존재하기 때문입니다.

<a id="oauth-20-authentication"></a>
## OAuth 2.0 인증 (OAuth 2.0 authentication)

인증에 [아웃바운드 애플리케이션(outbound application)을](https://www.palantir.com/docs/foundry/administration/configure-outbound-applications/) 사용하는 REST API 소스에 웹훅이 설정된 경우, Foundry가 사용자를 대신해 OAuth 2.0 인가 흐름을 관리합니다. 개발자는 토큰 획득이나 갱신을 처리할 필요가 없습니다. Foundry가 모든 웹훅 호출에 올바른 액세스 토큰을 함께 전달합니다.

Foundry 업무 흐름 전반의 OAuth 2.0 아웃바운드 애플리케이션 지원에 대한 전체 개요는 [OAuth 2.0 아웃바운드 애플리케이션](https://www.palantir.com/docs/foundry/administration/configure-outbound-applications/) 문서를 참고하세요.

**설명**: OAuth 2.0은 사용자의 비밀번호를 직접 넘기지 않고, 외부 서비스가 발급한 액세스 토큰으로 API를 호출하는 표준 인가 방식입니다. 토큰은 만료 시간이 있어 주기적으로 갱신해야 하는데, 이 페이지는 그 처리를 Foundry가 대신한다는 뜻입니다.

## 정리

- 웹훅은 Data Connection에 정의된 외부 HTTP 요청이며, 액션에서 라이트백 또는 부수 효과로 실행할 수 있습니다.
- 라이트백 웹훅은 다른 규칙보다 먼저 실행되어 실패 시 Foundry 편집을 막고 사용자에게 오류를 보여 주며, 액션당 하나만 둘 수 있습니다.
- 부수 효과 웹훅은 객체 편집 후 순서 없이 실행되며, 여러 개를 두거나 페이로드 목록으로 여러 번 호출할 수 있습니다.
- 입력은 액션 파라미터 매핑 또는 웹훅 입력 구조와 일치하는 타입을 반환하는 함수로 채웁니다.
- 라이트백 웹훅의 출력은 **Writeback response**로 후속 규칙에서 쓸 수 있고, OAuth 2.0 토큰 처리는 Foundry가 대신합니다.
