# 함수에서 웹훅 사용하기 (Use webhooks)

- 원문: https://www.palantir.com/docs/foundry/functions/webhooks/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v1 > Use webhooks

이 페이지는 TypeScript v1 함수(function)에서 웹훅(webhook)을 이용해 Foundry 바깥의 외부 시스템(예: 외부 REST API)에 요청을 보내는 방법을 다룹니다. 소스를 저장소로 가져오는 절차, 코드에서 웹훅을 호출하는 방법, 오류 처리, 버전 관리, 필요한 권한, 모니터링 도구와 모범 사례까지 차례로 설명합니다. 함수가 플랫폼 안의 데이터만이 아니라 외부 시스템과도 주고받아야 할 때 필요한 내용입니다.

**팁**: 이 페이지의 소스 가져오기 안내와 코드 예제는 TypeScript v1 함수 전용입니다. Ontology SDK 지원과 리소스 요청 설정 등 [더 강력한 기능](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 쓰려면 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)하는 것을 권장합니다.

이 가이드는 [웹훅](https://www.palantir.com/docs/foundry/data-connection/webhooks-overview/)을 사용해 외부 시스템에 요청을 보낼 수 있는 함수를 설정하는 과정을 안내합니다.

TypeScript v2나 Python 함수에서 웹훅을 사용하려면 대신 [웹훅 함수로 게시](https://www.palantir.com/docs/foundry/data-connection/webhooks-reference/#webhook-functions)하십시오. 게시된 함수를 함수 저장소로 가져온 뒤 [Ontology SDK로 호출](../09_language-agnostic-features/02_query-functions.md#call-a-query-function)하면 됩니다. 웹훅 함수는 [Workshop](https://www.palantir.com/docs/foundry/workshop/functions-use/), [함수 기반 액션(function-backed actions)](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md), 다른 함수에서도 호출할 수 있습니다.

아웃바운드 애플리케이션(outbound application)이 뒷받침하는 웹훅도 지원됩니다. 자세한 내용은 아웃바운드 애플리케이션 구성 페이지의 [Supported workflows](https://www.palantir.com/docs/foundry/administration/configure-outbound-applications/#supported-workflows) 섹션을 참고하십시오.

**설명**: 웹훅은 여기서 "Foundry가 외부 시스템으로 보내는 HTTP 요청을 미리 정의해 둔 것"입니다. Data Connection에서 소스(source, 외부 시스템 연결 정보: 주소, 인증 정보 등)를 만들고 그 아래에 웹훅(요청 메서드, 경로, 입력 파라미터, 응답 형식)을 정의해 두면, 함수 코드에서는 HTTP 세부 사항을 직접 다루지 않고 `소스.webhooks.웹훅이름.call({...})` 형태의 타입이 붙은 함수 호출로 외부 API를 부를 수 있습니다.

<a id="prerequisites"></a>
## 사전 준비 (Prerequisites)

이 가이드를 따르기 전에 다음을 갖추었는지 확인하십시오.

* [데이터 연결 소스와 웹훅](https://www.palantir.com/docs/foundry/data-connection/external-functions/)을 만들었습니다.
* 함수 저장소를 만들었고, [튜토리얼](../03_getting-started.md)에서 설명하는 함수 작성과 게시 방법을 검토했습니다.

<a id="import-sources-into-a-functions-repository"></a>
## 함수 저장소로 소스 가져오기 (Import sources into a functions repository)

먼저 소스를 Code Repositories로 가져올 수 있도록 활성화해야 합니다. 이를 위해 REST API 소스의 **Enable code imports**(코드 가져오기 활성화) 메뉴로 가서 소스를 Code Repositories로 가져올 수 있게 허용하는 옵션을 켭니다. 함수가 사용되는 모든 워크플로에서 내보내기 가능 Marking 검증(exportable Marking validation)을 수행할 수는 없으므로, 각 소스의 **Enable exports**(내보내기 활성화) 메뉴에서 Marking 검증 없이 소스로 내보내는 것도 허용해야 합니다.

![코드 가져오기 구성.](https://www.palantir.com/docs/resources/foundry/functions/source-code-import-configuration.png)

![내보내기 구성.](https://www.palantir.com/docs/resources/foundry/functions/source-export-configuration.png)

다음으로, 함수에서 웹훅을 사용하려면 웹훅을 뒷받침하는 REST API 소스를 먼저 저장소로 가져와야 합니다. 왼쪽의 [**Resource imports** 패널](08_resource-imports-sidebar.md)을 선택하면 저장소로 가져온 소스를 볼 수 있습니다. **Add > Sources**를 선택하면 가져올 소스를 고를 수 있는 검색 대화 상자가 나타납니다. 이 대화 상자로는 API 이름이 있는 소스만 가져올 수 있습니다.

![가져오기 대상으로 특정 소스가 선택된 외부 함수 소스 가져오기 모달](https://www.palantir.com/docs/resources/foundry/functions/external-functions-source-import-modal.png)

**주의**: 웹훅 사용을 위해 함수 저장소로 소스를 가져오는 방식은 Python 트랜스폼 저장소나 컴퓨트 모듈(compute module)로 소스를 가져오는 방식과 다르게 동작합니다. 특정 소스를 웹훅 용도로만 사용하는 함수 저장소는 소스 개요 화면의 저장소 목록에 표시되지 *않습니다*. 소스에 대해 `Viewer` 접근 권한이 있는 사용자라면 누구나 그 웹훅을 가져와 외부 함수에서 사용할 수 있습니다.

> **중간 요약**: 소스 설정에서 코드 가져오기와 Marking 검증 없는 내보내기를 켠 뒤, 함수 저장소의 Resource imports 패널에서 API 이름이 있는 REST API 소스를 가져와야 웹훅을 쓸 수 있습니다. 소스의 Viewer 권한만 있어도 웹훅을 가져와 사용할 수 있다는 점에 유의합니다.

<a id="use-webhooks-in-functions"></a>
## 함수에서 웹훅 사용하기 (Use webhooks in functions)

REST API 소스를 함수 저장소로 가져오면 TypeScript 환경에서 사용할 수 있게 되며, 소스의 네임스페이스를 통해 접근할 수 있습니다.

```typescript
import { Function } from "@foundry/functions-api";
import { MyDictionarySource } from "@foundry/external-systems/sources";
```

`Cannot find module '@foundry/external-systems' or its corresponding type declarations.` 오류가 나면 `functions-typescript/functions.json` 파일에서 `enableExternalSystems` 값이 `true`로 설정되어 있는지 확인하십시오. 값을 바꾸고 변경 사항을 커밋하면 시스템이 `@foundry/external-systems`를 포함한 필요한 패키지를 설치합니다.

![외부 함수 가져오기 오류 메시지.](https://www.palantir.com/docs/resources/foundry/functions/external-functions-import-error-message.png)

<a id="example-make-multiple-calls-from-a-function"></a>
### 예제: 하나의 함수에서 여러 번 호출하기 (Example: Make multiple calls from a Function)

아래 예제에서는 하나의 함수로 사전(dictionary) API를 여러 번 호출하는 방법을 설명합니다.

함수가 온톨로지 편집(edit)을 하지 않는다면 `@Query()` 함수를 만듭니다. 온톨로지 편집을 하려면 대신 `@OntologyEditFunction` 데코레이터가 필요합니다. 함수에서 온톨로지 편집을 하는 방법은 [문서](03_api-ontology-edits.md)를 참고하십시오.

표준 [TypeScript async/await 패턴 ↗](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-1-7.html#asyncawait-support-in-es6-targets-node-v4)을 사용하면 하나의 함수에서 여러 웹훅 호출을 동시에 보낼 수 있습니다. 호출 성공 여부는 `@foundry/functions-api`에서 내보내는 `isOk` 헬퍼 함수로 확인합니다.

다음 함수는 단어 목록을 TypeScript 문자열 배열로 받아 단어마다 한 번씩 호출합니다.

```typescript
import { OntologyEditFunction, isOk } from "@foundry/functions-api";
import { MyDictionarySource } from "@foundry/external-systems/sources";

export class MyFunctions {

    @OntologyEditFunction()
    public async defineWords(words: string[]): Promise<void> {

        // 단어마다 웹훅 호출을 만들고, Promise.all로 모두 동시에 기다림
        const results = await Promise.all(words.map(word => MyDictionarySource.webhooks.GetDefinition.call({
            wordToDefine: word
        })));

        results.forEach((result, i) => {
            if (isOk(result)) {
                const output = result.value.output;
                output.dictionary_definitions.forEach(definitions_for_word => {
                    definitions_for_word.meanings.forEach(meaning => {
                        meaning.definitions.forEach(def_for_part_of_speech => {
                            console.log(`Found a ${meaning.partOfSpeech} definition for "${words[i]}": ${def_for_part_of_speech.definition}`);
                        })
                    })
                });
            }
        });
    }
}
```

**설명**: 입력은 문자열 배열 `words`입니다. `words.map(...)`이 단어마다 `GetDefinition` 웹훅 호출(Promise)을 하나씩 만들고, `Promise.all`이 그 Promise들이 모두 끝날 때까지 기다린 뒤 결과 배열 `results`를 돌려줍니다. 순서대로 하나씩 기다리지 않으므로 네트워크 요청 여러 개가 동시에 진행됩니다. 각 `result`는 성공 또는 실패를 담은 Result 객체이며, `isOk(result)`가 참일 때만 `result.value.output`으로 응답 본문에 접근합니다. 응답이 단어, 품사(meaning), 정의(definition)의 중첩 배열 구조이므로 `forEach`를 세 번 중첩해 정의를 하나씩 로그로 출력합니다.

`["tuba", "cool"]`을 입력했을 때의 로그 출력:

```
LOG [2023-07-28T03:16:22.968Z] Found a noun definition for "tuba": A large brass musical instrument, usually in the bass range, played through a vibration of the lips upon the mouthpiece and fingering of the keys.
LOG [2023-07-28T03:16:22.968Z] Found a noun definition for "tuba": A type of Roman military trumpet, distinct from the modern tuba.
LOG [2023-07-28T03:16:22.968Z] Found a noun definition for "tuba": A large reed stop in organs.
LOG [2023-07-28T03:16:22.968Z] Found a noun definition for "tuba": A Malayan plant whose roots are a significant source of rotenone, Derris malaccensis.
LOG [2023-07-28T03:16:22.968Z] Found a noun definition for "tuba": A reddish palm wine made from coconut or nipa sap.
LOG [2023-07-28T03:16:22.968Z] Found a noun definition for "tuba": A tube or tubular organ.
LOG [2023-07-28T03:16:22.968Z] Found a noun definition for "cool": A moderate or refreshing state of cold; moderate temperature of the air between hot and cold; coolness.
LOG [2023-07-28T03:16:22.968Z] Found a noun definition for "cool": A calm temperament.
```

> **중간 요약**: 가져온 소스는 `@foundry/external-systems/sources`에서 import하며, `소스.webhooks.이름.call()`로 웹훅을 호출합니다. 온톨로지 편집이 없으면 `@Query()`, 있으면 `@OntologyEditFunction`을 쓰고, async/await와 `Promise.all`로 여러 호출을 동시에 보낼 수 있습니다.

<a id="error-handling"></a>
## 오류 처리 (Error handling)

네트워크로 연결된 시스템을 다룰 때 생기는 실패에 대응할 수 있도록, 함수는 웹훅에서 전파된 오류를 Result 객체로 노출합니다. Result 객체는 어떤 종류의 오류가 발생했는지에 대한 정보를 제공합니다.

```typescript
import { OntologyEditFunction, isOk } from "@foundry/functions-api";
import { MyDictionarySource } from "@foundry/external-systems/sources";

export class MyFunctions {

    @OntologyEditFunction()
    public async defineWords(words: string[]): Promise<void> {

        const results = await Promise.all(words.map(word => MyDictionarySource.webhooks.GetDefinition.call({
            wordToDefine: word
        })));

        results.forEach((result, i) => {
            if (isOk(result)) {
                // 응답 추출
            } else {
                const errorName = result.error.name;

                if (errorName === "WebhookExecutionFailedToStart") {
                    console.log("We were unable to initiate a request to the dictionary API.");
                } else if (errorName === "ParsingResponseFailed") {
                    console.log("The external request succeeded, but the response couldn't be parsed.");
                } else {
                    console.log("Something went wrong.");
                }
            }
        });
    }
}
```

**설명**: 웹훅 호출은 실패해도 예외(exception)를 던지지 않고, 실패 정보를 담은 Result 값을 돌려줍니다. 그래서 `try/catch` 대신 `isOk(result)`로 분기하고, 실패한 경우 `result.error.name`(오류 이름 문자열)을 비교해 오류 종류별로 다르게 처리합니다. 마지막 `else`는 아래 표에 없는 새 오류 이름이 돌아올 때를 대비한 기본 처리입니다.

오류를 처리할 때 작성하는 코드는 특정 오류 이름을 확인하고 그에 맞게 대응해야 합니다. 함수는 현재 다음 오류를 반환합니다.

| 오류 | 설명 |
| ----- | ----------- |
| `WebhookExecutionFailedToStart` | 웹훅이 시작되지 못했습니다. 이 오류가 반환되면 외부 시스템으로 요청이 전혀 보내지지 않았다고 안전하게 가정할 수 있습니다. |
| `WebhookExecutionTimedOut` | 웹훅 실행은 시작되었지만, 설정된 웹훅 시간 제한 안에 외부 시스템에서 응답을 받지 못했습니다. |
| `RemoteRestApiReturnedError` | 외부 시스템이 오류를 반환했습니다. REST API 소스에 구성된 웹훅에서만 반환됩니다. |
| `RemoteApiReturnedError` | 외부 시스템이 오류를 반환했습니다. REST API가 아닌 소스에 구성된 웹훅에서만 반환됩니다. |
| `ParsingResponseFailed` | 웹훅 실행은 성공했지만 외부 시스템의 응답을 제대로 파싱하지 못했습니다. 예를 들어 외부 시스템의 응답에 기대한 필드가 없을 때 발생할 수 있습니다. 웹훅 호출 결과가 반드시 사용되는 것은 아니므로, 이를 최종 사용자에게 실패로 표시할지는 애플리케이션 빌더가 결정합니다. |
| `ServerError` | 웹훅 서비스나 커넥터 내부에서 문제가 발생했습니다. |
| `UnknownError` | 어느 Foundry 서비스의 문제라고 직접 특정할 수 없는 오류가 발생했습니다. |

이 오류 유형 목록은 바뀔 수 있습니다. 함수 실행기가 새로운 이름의 오류를 반환하는 경우를 대비해 코드에 기본(default) 분기를 넣어 두어야 합니다.

**설명**: `WebhookExecutionFailedToStart`와 `WebhookExecutionTimedOut`의 차이는 중요합니다. 앞의 것은 요청이 나가지 않았음이 보장되므로 재시도해도 외부 시스템에 같은 작업이 두 번 적용될 걱정이 없습니다. 뒤의 것은 요청은 나갔지만 응답만 못 받은 상태라서, 외부 시스템에서 작업이 실제로 처리되었는지 알 수 없습니다. 쓰기 요청이라면 재시도 전에 중복 처리 여부를 따져야 합니다.

<a id="example-handle-errors-when-making-multiple-webhook-calls-from-a-single-function"></a>
### 예제: 하나의 함수에서 여러 웹훅을 호출할 때 오류 처리하기 (Example: Handle errors when making multiple webhook calls from a single Function)

다음 코드는 같은 함수 안에서 일부 웹훅 호출은 성공하고 일부는 실패하는 경우를 처리하는 방법을 보여 줍니다. 이 예제에서는 사전 서버가 주어진 단어의 정의를 찾지 못하면 `RemoteRestApiReturnedError`가 반환됩니다.

(원문에는 앞의 "여러 번 호출하기" 예제 코드에 `else` 분기를 추가해 `result.error.name === "RemoteRestApiReturnedError"`일 때 `` console.log(`ERROR: ${words[i]} could not be defined`, result.error.message) ``를 출력하는 예제 코드가 있습니다.)

위 함수에 `["asdf", "shire"]`를 입력하면 다음 결과가 나옵니다.

```
LOG [2023-07-28T15:38:47.263Z] ERROR: asdf could not be defined Request returned an unsuccessful response code: 404 Response body: {"title":"No Definitions Found","message":"Sorry pal, we couldn't find definitions for the word you were looking for.","resolution":"You can try the search again at later time or head to the web instead."}
LOG [2023-07-28T15:38:47.264Z] Found a noun definition for "shire": Physical area administered by a sheriff.
LOG [2023-07-28T15:38:47.264Z] Found a noun definition for "shire": Former administrative area of Britain; a county.
LOG [2023-07-28T15:38:47.264Z] Found a noun definition for "shire": The general area in which a person lives or comes from, used in the context of travel within the United Kingdom.
LOG [2023-07-28T15:38:47.264Z] Found a noun definition for "shire": A rural or outer suburban local government area of Australia.
LOG [2023-07-28T15:38:47.264Z] Found a noun definition for "shire": A shire horse.
LOG [2023-07-28T15:38:47.264Z] Found a verb definition for "shire": To (re)constitute as one or more shires or counties.
```

**설명**: "asdf"에 대한 호출은 외부 서버가 HTTP 404를 돌려주어 `RemoteRestApiReturnedError`가 되었고, `result.error.message`에 응답 코드와 응답 본문이 담겨 있습니다. 같은 `Promise.all` 안의 "shire" 호출은 영향을 받지 않고 정상적으로 처리되었습니다. 즉 결과 하나가 실패해도 나머지 결과는 그대로 사용할 수 있습니다.

> **중간 요약**: 웹훅 오류는 예외가 아니라 Result 객체로 돌아오며, `isOk`로 성공 여부를 나누고 `result.error.name`으로 오류 종류를 구분합니다. 오류 목록은 바뀔 수 있으므로 항상 기본 분기를 둡니다.

<a id="limitations"></a>
## 제한 사항 (Limitations)

현재 온톨로지 편집 함수 안에서 보낼 수 있는 요청 수에는 제한이 없지만, 기존 [함수 리소스 제한](../07_function-management/02_manage-functions.md#enforced-limits)은 그대로 적용됩니다. [웹훅 제한](https://www.palantir.com/docs/foundry/data-connection/webhooks-reference/#limits)도 적용됩니다.

함수는 현재 다음 입력 및 출력 타입을 쓰는 웹훅을 지원합니다.

* Attachments(첨부 파일)
* Booleans
* Integers
* Longs
* Doubles
* Strings
* Optionals
* Dates
* Timestamps
* Lists
* Enums(허용된 String 타입 값의 목록)
* 기대 필드(expected fields)가 있거나 없는 Records

`@Query` 함수에서 웹훅을 호출할 때는 그 웹훅이 외부 시스템을 변경하지 않는 `Read API` 호출만 수행해야 합니다. 쿼리 함수는 자주 재시도되거나 페이지 로드 시 사용자 모르게 실행되므로, `@OntologyEditFunction`에서 가능한 수준의 구조화되고 의도적인 실행을 보장하지 않습니다. 웹훅을 구성할 때 `Read API` 또는 `Write API` 옵션으로 쿼리 함수에서 실행해도 안전한지 지정할 수 있습니다.

**설명**: 예를 들어 Workshop 화면이 열릴 때마다 실행되는 쿼리 함수가 "주문 생성" 같은 쓰기 웹훅을 호출한다면, 사용자가 화면을 새로 고칠 때마다 외부 시스템에 주문이 하나씩 더 생길 수 있습니다. 그래서 쿼리 함수에는 조회만 하는(HTTP GET처럼 상태를 바꾸지 않는) 웹훅만 허용하고, 쓰기는 사용자가 명시적으로 실행하는 액션 뒤의 편집 함수에서 하도록 구분합니다.

<a id="unsupported-webhook-features"></a>
### 지원하지 않는 웹훅 기능 (Unsupported webhook features)

* 입력 또는 출력 파라미터로 `OR` 타입을 사용하는 웹훅은 현재 지원하지 않습니다. 이런 웹훅에 대해서는 코드가 생성되지 않습니다.

> **중간 요약**: 함수 리소스 제한과 웹훅 제한이 적용되며, 지원되는 입출력 타입이 정해져 있고 `OR` 타입은 지원하지 않습니다. 쿼리 함수에서는 외부 시스템을 변경하지 않는 Read API 웹훅만 호출해야 합니다.

<a id="handle-version-changes-in-functions-and-webhooks"></a>
## 함수와 웹훅의 버전 변경 다루기 (Handle version changes in functions and webhooks)

함수와 웹훅에는 버전이 있으며, 호출자는 함수나 웹훅의 어떤 버전이든 호출할 수 있습니다. 함수를 게시하면 그 시점에 사용 가능한 가장 최신 웹훅 버전이 함수에 고정(pin)됩니다.

[Code Repositories](https://www.palantir.com/docs/foundry/code-repositories/overview/) 애플리케이션에서 함수 저장소를 열면, 자동 완성에 쓰이는 생성된 코드 바인딩은 항상 가장 최신 버전의 웹훅을 사용합니다. 이 웹훅 버전은 왼쪽의 **Resource imports** 사이드 패널에 표시됩니다.

![웹훅 하나가 있는 소스를 보여 주는, 함수 저장소의 Resource imports 사이드 패널.](https://www.palantir.com/docs/resources/foundry/functions/external-functions-import-sidebar.png)

**팁**: 웹훅의 기능에 의존하는 함수를 게시하기 전에 웹훅이 안정적인지 확인하십시오.

웹훅이나 함수를 변경했다면 함수를 다시 게시하고 사용자를 새 버전으로 올려 주어야 한다는 점을 기억하십시오. 이전에 게시되어 고정된 함수 버전은 계속 사용할 수 있습니다.

**설명**: 예를 들어 함수 1.0.0을 게시할 때 웹훅 버전이 3이었다면, 이후 웹훅이 버전 4로 바뀌어도 함수 1.0.0은 계속 웹훅 버전 3을 호출합니다. 웹훅 버전 4를 쓰려면 함수를 1.0.1 같은 새 버전으로 다시 게시하고, 그 함수를 쓰는 애플리케이션이 새 함수 버전을 사용하도록 바꿔야 합니다. 라이브러리 의존성 버전을 lock 파일로 고정하는 것과 같은 원리입니다.

> **중간 요약**: 함수를 게시하는 순간의 최신 웹훅 버전이 그 함수 버전에 고정됩니다. 웹훅이 바뀌면 함수를 다시 게시하고 사용처를 새 버전으로 올려야 합니다.

<a id="permissions"></a>
## 권한 (Permissions)

다음 표는 외부 함수를 작성, 게시, 사용하는 데 필요한 권한을 정리한 것입니다.

| 작업 | 사용자 | 필요한 권한 |
|--------|------|---------------------|
| 함수 저장소로 웹훅 가져오기 | 함수 편집자 | 웹훅에 대한 `webhooks:editor`. **Editor** 기본 역할에 부여됩니다. |
| 웹훅을 호출하는 함수 게시 | 함수 편집자 | 소스에 대한 `webhooks:execute` 권한. **Owner**와 **Editor** 기본 역할에만 부여됩니다. |
| 웹훅을 호출하는 `@OntologyEditFunction()`을 사용하도록 액션 구성 | 액션 편집자 | 웹훅에 대한 `webhooks:grant-action-validated-execution` 권한과 함수에 대한 `Viewer` 권한 |
| Workshop에서 `@Query()` 웹훅 실행 | 최종 사용자 | 소스에 대한 `webhooks:execute` 권한. `Owner`와 `Editor` 기본 역할에만 부여됩니다. |
| 액션에서 `@OntologyEditFunction()` 실행 | 최종 사용자 | 사용자가 해당 액션의 [제출 조건(submission criteria)](../../03_action-types/08_submission-criteria.md)을 충족해야 합니다. 이 경우 소스, 웹훅, 함수에 대한 권한은 검사하지 않습니다. 액션을 만들고 관리하는 사용자는 제출 조건이 적절히 구성되어 있는지 반드시 확인해야 합니다. |

**설명**: 마지막 행이 핵심입니다. 액션을 통해 편집 함수를 실행하는 최종 사용자는 소스나 웹훅 권한이 없어도 외부 시스템에 요청을 보낼 수 있습니다. 대신 액션 편집자가 `webhooks:grant-action-validated-execution` 권한으로 "이 액션을 통해서라면 웹훅을 실행해도 된다"고 승인한 것이고, 누가 그 액션을 실행할 수 있는지는 제출 조건이 결정합니다. 따라서 제출 조건이 사실상 외부 시스템 접근을 통제하는 장치가 됩니다.

> **중간 요약**: 웹훅 가져오기, 게시, 액션 구성, 실행 단계마다 요구 권한이 다릅니다. 액션에서 편집 함수를 실행할 때는 소스와 웹훅 권한 대신 제출 조건만 검사하므로 제출 조건을 신중히 설정해야 합니다.

<a id="monitoring-troubleshooting-and-debugging"></a>
## 모니터링, 문제 해결, 디버깅 (Monitoring, troubleshooting, and debugging)

함수에서 실행한 웹훅을 더 자세히 파악하려면 다음 플랫폼 도구를 사용하십시오.

* [웹훅 실행 기록](https://www.palantir.com/docs/foundry/data-connection/webhooks-reference/#webhook-history): [Data Connection](https://www.palantir.com/docs/foundry/data-connection/overview/)에서 웹훅 하나를 볼 때 **History** 탭에서 확인할 수 있습니다.
* 함수 사용 기록: [Ontology Manager](../../../05_applications/04_ontology-manager/01_overview.md)에서 볼 수 있으며, 함수가 언제 실행되었는지와 입력, 출력, 함수를 실행한 사용자를 보여 줍니다.
* [함수 지표(Function metrics)](../08_function-consumption/02_function-metrics.md): 함수의 성공/실패 횟수와 P95 실행 시간을 거의 실시간으로 보여 줍니다.
* [함수 코드 작성 미리보기](../13_functions-on-objects/02_foo-getting-started.md#test-in-live-preview): 성능 프로파일링, 디버그 출력 등을 제공합니다.

**설명**: P95 실행 시간은 실행 100번 가운데 95번이 이 시간 안에 끝났다는 뜻의 값입니다. 평균보다 느린 쪽 꼬리를 잘 드러내므로, 외부 API 응답이 가끔 느려지는 문제를 발견하는 데 유용합니다.

<a id="best-practices"></a>
## 모범 사례 (Best practices)

함수에서 외부 소스를 이용해 웹훅을 호출할 때 다음 모범 사례를 권장합니다.

* 함수에서 웹훅을 사용하기 전에 Data Connection의 [웹훅 테스트 사이드 패널](https://www.palantir.com/docs/foundry/data-connection/webhooks-setup/#test-the-webhook)로 웹훅을 충분히 테스트하십시오.
* 가능하면 기대 필드가 있는 `record` 타입의 웹훅 입력, 출력 파라미터를 사용하십시오. JSON 대신 명시적인 타입을 쓰면 함수 코드가 예상치 못한 런타임 오류를 낼 가능성이 줄어듭니다.
* `@foundry/functions-api`에서 내보내는 내장 함수 `isOk`와 `isErr`로 성공과 오류 상태를 확인하고, name 필드로 오류 종류를 좁히십시오.
* 사용자가 한 번의 함수 호출로 외부 시스템과 온톨로지에 모두 쓰게 된다면, 외부 시스템 쓰기가 성공하더라도 온톨로지 쓰기는 실패할 수 있다는 점을 기억하십시오. 이런 불일치를 처리할 대책을 마련하고, 필요하면 사용자가 두 시스템에 대한 변경 상태를 모두 확인할 수 있게 하십시오.

**설명**: 마지막 항목은 분산 트랜잭션 문제입니다. 데이터베이스 하나 안에서는 트랜잭션으로 "둘 다 반영하거나 둘 다 취소"를 보장할 수 있지만, 외부 API 호출과 온톨로지 편집은 서로 다른 시스템이라 하나의 트랜잭션으로 묶이지 않습니다. 예를 들어 외부 결제 시스템에 결제 요청은 성공했는데 온톨로지의 Order 객체 상태 갱신이 실패하면 두 시스템의 상태가 어긋납니다. 이런 경우를 감지하고 보정하는 절차를 따로 설계해야 합니다.

## 정리

- TypeScript v1 함수는 함수 저장소로 가져온 REST API 소스의 웹훅을 `소스.webhooks.이름.call()`로 호출해 외부 시스템과 통신합니다(TypeScript v2와 Python은 웹훅 함수로 게시해 사용).
- 소스 설정에서 코드 가져오기와 내보내기를 켜고, Resource imports 패널에서 소스를 가져와야 합니다.
- 오류는 Result 객체로 반환되며 `isOk`/`isErr`와 오류 이름으로 처리하고, 새 오류에 대비한 기본 분기를 둡니다.
- 쿼리 함수에서는 Read API 웹훅만 써야 하며, 함수 게시 시점의 웹훅 버전이 고정됩니다.
- 액션을 통한 실행은 제출 조건만 검사하므로 제출 조건 설정이 접근 통제의 핵심이고, 외부 시스템과 온톨로지 쓰기 사이의 불일치에도 대비해야 합니다.
