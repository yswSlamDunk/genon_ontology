# Code Repositories로 리소스 가져오기 (Import resources into Code Repositories)

- 원문: https://www.palantir.com/docs/foundry/functions/resource-imports-sidebar/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v1 > Import resources into Code Repositories

TypeScript 함수 코드에서 객체 타입이나 언어 모델 같은 Foundry 리소스를 쓰려면 먼저 그 리소스를 저장소(repository)로 가져와야(import) 합니다. 이 페이지는 TypeScript v1 함수 저장소에서 Code Repositories의 Resource imports 사이드바로 온톨로지 선택, 리소스 가져오기와 관리, API 이름과 값 타입 의존성 문제 해결, `resources.json` 파일 형식, `functions.json`의 기능 플래그 설정을 설명합니다.

**팁**: 아래 문서는 TypeScript v1 함수에만 해당합니다. Ontology SDK 지원과 구성 가능한 리소스 요청 등 [더 강력한 기능](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 위해 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)할 것을 권장합니다.

Code Repositories의 **Resource imports**(리소스 가져오기) 사이드바는 TypeScript 함수 저장소 안으로 가져온 Foundry 리소스를 관리하는 중앙 인터페이스를 제공합니다. 이 사이드바에서 온톨로지 타입, LMS 언어 모델, 라이브 배포(live deployment), REST API 같은 외부 시스템 등 다양한 리소스를 가져오고, 제거하고, 세부 정보를 볼 수 있습니다.

![Resource Imports 사이드바](https://www.palantir.com/docs/resources/foundry/functions/resource-imports-sidebar.png)

**설명**: 일반적인 프로그래밍에서 외부 라이브러리를 쓰려면 의존성을 선언하고 `import` 해야 하듯, Foundry 함수에서도 온톨로지의 `Employee` 객체 타입을 쓰려면 그 타입을 저장소에 "가져오기"로 등록해야 합니다. 등록하면 Foundry가 해당 타입에 대한 TypeScript 코드(클래스, 속성 타입 등)를 자동 생성해 주므로, 코드에서 `employee.name`처럼 타입 검사를 받으며 쓸 수 있습니다.

<a id="select-an-ontology"></a>
## 온톨로지 선택하기 (Select an Ontology)

객체 타입과 링크 타입을 가져오려면 온톨로지가 필요합니다. 온톨로지를 고르려면 다음과 같이 합니다.

1. **Add**를 선택해 리소스 선택 메뉴를 열고, **Ontology**를 선택해 온톨로지 타입 가져오기를 시작합니다. 선택된 온톨로지가 없으면 온톨로지 선택 대화상자가 자동으로 열립니다.

이미 온톨로지 타입을 하나 이상 가져왔다면 그 타입의 온톨로지가 자동으로 선택됩니다. 온톨로지를 바꾸려면 선택된 온톨로지 이름 옆의 **Edit** 버튼을 선택해 온톨로지 선택 대화상자를 엽니다.

![온톨로지 선택 대화상자](https://www.palantir.com/docs/resources/foundry/functions/sidebar-ontology-picker.png)

저장소 안의 모든 가져온 리소스는 같은 온톨로지에 속해야 합니다. 따라서 온톨로지를 바꾼 뒤 리소스를 가져오면 다른 온톨로지에서 가져왔던 기존 항목은 덮어쓰여집니다.

**설명**: 한 Foundry 환경에 온톨로지가 여러 개 있을 수 있습니다(예: 부서별 온톨로지). 저장소 하나는 그중 하나에만 묶이므로, A 온톨로지에서 `Employee`를 가져온 상태에서 B 온톨로지로 바꿔 `Flight`를 가져오면 `Employee` 가져오기는 사라집니다.

<a id="import-resources"></a>
## 리소스 가져오기 (Import resources)

**주의**: 최신 버전의 TypeScript v1 템플릿은 저장소의 현재 가져오기 상태를 저장소에 체크인된 `resources.json` 파일에 유지합니다.

사이드바에서 해결할 수 없는 파일(unresolvable file)에 대한 경고가 나타나면, 기대되는 파일 형식과 문제 해결 단계는 [파일 기반 저장소 가져오기](#file-based-repository-imports) 섹션을 참고하세요.

사이드바로 리소스를 가져오려면 다음과 같이 합니다.

1. 사이드바 오른쪽 위의 **Add** 버튼을 사용해 원하는 리소스 유형을 선택합니다. 그 리소스의 선택 대화상자가 열립니다.
2. 검색창과 필터로 가져올 리소스를 찾습니다.
3. 리소스를 선택하면 상세 정보가 담긴 미리보기 패널이 표시됩니다.
4. **Select** 버튼으로 리소스를 선택 목록에 추가합니다.
5. 장바구니(cart) 패널을 펼쳐 선택 목록을 검토하고 **Confirm selection**을 선택해 확정합니다.

선택을 확정하면 변경 사항을 반영하는 데 필요한 코드 생성 작업을 다시 실행하기 위해 Code Assist가 재시작됩니다. 그러면 가져온 각 리소스가 생성된 패키지(generated package)로 노출되므로, 자신의 파일 기준 상대경로가 아니라 생성된 패키지 경로에서 가져오게 됩니다. 예를 들어 온톨로지 타입은 `@foundry/ontology-api`에서 가져오며, 정확한 경로는 리소스 유형에 따라 다릅니다.

![리소스 선택 대화상자 예시](https://www.palantir.com/docs/resources/foundry/functions/language-model-import-dialog.png)

특정 유형의 리소스를 가져오는 방법은 다음을 참고하세요.

* [온톨로지 타입](../13_functions-on-objects/05_ontology-imports.md)
* [언어 모델](../14_models/03_language-models-python-tsv2.md#import-a-language-model)
* [라이브 배포](../14_models/01_functions-on-models.md#import-a-live-deployment-in-a-repository)
* [외부 소스](10_webhooks.md)

**설명**: Code Assist는 Code Repositories 안에서 자동 완성과 타입 검사를 제공하는 언어 서버입니다. 가져오기를 확정하면 Code Assist가 재시작되면서 `Employee` 같은 타입의 코드를 새로 생성하고, 이후 코드에서는 다음처럼 생성된 패키지 이름으로 가져옵니다.

```typescript
import { Employee, Objects } from "@foundry/ontology-api";
```

`./generated/employee` 같은 상대경로가 아니라 패키지 이름으로 가져오는 이유는, 이 코드가 저장소 파일이 아니라 빌드 과정에서 생성되는 패키지이기 때문입니다.

> **중간 요약**: 객체 타입과 링크 타입을 가져오려면 먼저 온톨로지를 하나 선택해야 하며, 저장소의 모든 가져오기는 같은 온톨로지에 속해야 합니다. Add 버튼, 선택 대화상자, Confirm selection 순서로 가져오면 Code Assist가 재시작되어 `@foundry/ontology-api` 같은 생성된 패키지가 만들어집니다.

<a id="manage-imported-resources"></a>
## 가져온 리소스 관리하기 (Manage imported resources)

사이드바에서 리소스는 유형별로 분류됩니다.

* Ontology: 객체, 인터페이스, 링크 타입
* Models: LMS 모델과 라이브 배포
* Sources: REST API 같은 외부 시스템

사이드바 위쪽의 해당 리소스 아이콘을 선택해 유형별로 필터링하거나, 텍스트 입력란으로 이름을 검색합니다. 리소스를 제거하려면 리소스 아이콘 위에 마우스를 올리고 **Remove** 버튼을 선택합니다. 여러 리소스를 한꺼번에 추가하거나 제거하려면 선택 대화상자를 사용합니다. 더 자세한 정보를 보려면 가져온 리소스를 선택해 미리보기 패널을 엽니다.

일부 리소스 유형은 다른 리소스와 의존 관계를 가질 수 있습니다. 예를 들어 링크 타입은 해당 객체 타입 아래에 정리됩니다. 가져온 리소스에 의존 항목이 있으면 리소스 제목 옆에 "(1 link type)" 같은 메시지가 표시됩니다. 리소스의 의존 항목을 보려면 리소스 아이콘 위에 마우스를 올리고 나타나는 꺾쇠(chevron)를 선택합니다.

![Resource Imports 사이드바 필터 컨트롤](https://www.palantir.com/docs/resources/foundry/functions/resource-imports-sidebar-filters.png)

<a id="importing-resources-without-api-names"></a>
## API 이름이 없는 리소스 가져오기 (Importing resources without API names)

TypeScript 함수 저장소의 코드에서 리소스를 참조하려면 그 리소스에 API 이름이 있어야 합니다. 리소스에 API 이름이 없으면 경고가 표시됩니다. 경고 표시 위에 마우스를 올려 자세한 내용을 보거나 **Add API name**을 선택해 API 이름을 쉽게 구성할 수 있습니다. 또는 **Learn more**를 선택해 해당 리소스 유형에 맞춘 API 이름 추가 문서를 볼 수 있습니다.

![Resource Imports 사이드바의 API 이름 경고](https://www.palantir.com/docs/resources/foundry/functions/resource-imports-sidebar-api-name-warning.png)

**설명**: API 이름은 코드에서 쓰는 식별자입니다. 화면에 보이는 이름(display name)은 "Flight Delay Event"처럼 공백이 들어갈 수 있지만, 코드의 클래스 이름이나 속성 이름으로 쓰려면 `FlightDelayEvent`처럼 프로그래밍 언어 식별자 규칙을 따르는 이름이 필요합니다. API 이름이 없으면 코드 생성기가 클래스 이름을 정할 수 없으므로 경고가 나옵니다.

<a id="import-resources-with-value-type-dependencies"></a>
## 값 타입 의존성이 있는 리소스 가져오기 (Import resources with value type dependencies)

함수 인터페이스(function interface)처럼, 일부 리소스는 그 리소스와 상호작용하는 데 쓰이는 데이터 타입을 정의하기 위해 [값 타입(value type)](../../02_object-and-link-types/08_value-types/01_value-types-overview.md)에 의존합니다. 이런 리소스는 리소스와 함께 사용할 수 있도록 값 타입 의존 항목이 저장소로 자동으로 가져와집니다.

어떤 경우에는 이런 리소스를 여러 개 조합해 가져오면 값 타입 의존성 충돌이 생길 수 있습니다. 이는 서로 다른 리소스가 공통으로 의존하는 값 타입을 서로 다른 버전으로 요구할 때 발생합니다. 같은 값 타입의 두 버전을 동시에 가져올 수는 없으므로 컴파일 오류가 납니다. 이 오류와 함께 사이드바에 경고가 표시되어, 의존성이 충돌하는 리소스를 확인할 수 있습니다.

![값 타입 충돌 경고](https://www.palantir.com/docs/resources/foundry/functions/value-type-conflicts-warning.png)

**설명**: 패키지 관리에서 흔히 보는 버전 충돌과 같은 문제입니다. 예를 들어 함수 인터페이스 A는 `EmailAddress` 값 타입 버전 1을, 함수 인터페이스 B는 `EmailAddress` 버전 2를 요구한다고 합시다. 저장소에는 `EmailAddress` 타입 정의가 하나만 존재할 수 있으므로 A와 B를 함께 가져오면 컴파일이 실패합니다. 해결하려면 두 리소스가 같은 버전을 쓰도록 맞추거나 둘 중 하나만 가져와야 합니다.

> **중간 요약**: 가져온 리소스는 Ontology, Models, Sources 유형으로 분류되어 필터, 검색, 제거, 의존 항목 확인이 가능합니다. 코드에서 쓰려면 리소스에 API 이름이 있어야 하고, 값 타입에 의존하는 리소스는 같은 값 타입의 다른 버전을 요구하면 충돌이 납니다.

<a id="file-based-repository-imports"></a>
## 파일 기반 저장소 가져오기 (File-based repository imports)

최신 버전의 TypeScript v1 템플릿은 저장소에 체크인된 `resources.json` 파일로 저장소 가져오기의 현재 상태를 유지합니다. 이렇게 하면 Git의 기능을 그대로 쓸 수 있어, 가져오기 변경 사항을 리뷰하고, 브랜치로 나누고, 되돌릴 수 있습니다. 리소스 가져오기 사이드바는 `resources.json` 파일에 항목을 자동으로 삽입해 이 파일을 갱신하는 일을 돕습니다.

`resources.json` 파일이 유효하지 않은 상태가 되면, 사이드바에 파일을 처리할 수 없다는 경고가 나타납니다. 이 오류가 나면 파일에 다음 데이터를 담은 JSON 객체 하나만 들어 있는지 확인하세요.

| 필드 | 타입 |
|---|---|
| `objectTypes` | `{ rid: string }`의 배열 |
| `linkTypes` | `{ rid: string }`의 배열 |
| `sources` | `{ rid: string }`의 배열 |
| `functions` | `{ rid: string, version: string }`의 배열 |
| `valueTypes` | `{ rid: string, version: string }`의 배열 |
| `functionInterfaces` | `{ rid: string, version: string }`의 배열 |
| `_comment` | 문자열 |
| `version`\[1] | 정수 |

\[1] `version` 필드는 `resources.json` 파일의 버전과 형식을 나타냅니다. 현재는 `version: 1`만 지원됩니다. `version: 0`은 저장소가 이전의 저장소 전체(repository-wide) 가져오기 방식에서 마이그레이션되어야 함을 나타냅니다. 이 마이그레이션은 `version: 0`으로 커밋하면 저장소에 패치가 적용되면서 자동으로 처리됩니다.

`resources.json` 파일은 저장소에 체크인되어 있으므로 커밋 기록을 보고, 그 기록을 이용해 파일을 정상 동작하던 상태로 되돌릴 수 있습니다.

**설명**: rid(resource identifier)는 Foundry가 모든 리소스에 부여하는 고유 식별자 문자열입니다. 표의 형식에 맞는 파일은 대략 다음과 같은 모양입니다(rid 값은 형식만 보여 주는 예시입니다).

```json
{
  "_comment": "이 파일은 Resource imports 사이드바가 관리합니다",
  "version": 1,
  "objectTypes": [{ "rid": "ri.ontology.main.object-type.xxxx" }],
  "linkTypes": [],
  "sources": [],
  "functions": [{ "rid": "ri.function-registry.main.function.yyyy", "version": "1.2.0" }],
  "valueTypes": [],
  "functionInterfaces": []
}
```

함수, 값 타입, 함수 인터페이스는 버전을 가진 리소스라 `version`이 함께 기록되고, 객체 타입처럼 항상 최신 정의를 쓰는 리소스는 rid만 기록됩니다. 가져오기 목록이 일반 파일이므로, 잘못 수정해 경고가 나면 `git log`로 이전 커밋을 찾아 되돌리면 됩니다.

> **중간 요약**: 최신 TypeScript v1 템플릿은 가져오기 상태를 저장소의 `resources.json`에 기록해 Git으로 리뷰, 브랜치, 되돌리기를 할 수 있게 합니다. 파일은 표의 필드를 가진 JSON 객체 하나여야 하며, 현재 `version`은 1만 지원됩니다.

<a id="enable-resource-types"></a>
## 리소스 유형 활성화하기 (Enable resource types)

기본적으로 일부 리소스 유형은 저장소에서 사용하도록 활성화되어 있지 않을 수 있습니다. 활성화된 리소스 유형은 `functions.json` 파일로 결정됩니다. 다음은 일반적인 기본 `functions.json` 파일의 내용입니다.

```json
{
  "useOntologyApiNames" : true,
  "enableModelFunctions" : false,
  "enableModelGraphFunctions" : false,
  "enableDiscoverImproperOntologyAccess": false,
  "enableQueries": false,
  "enableModelMetadata": false,
  "useDeploymentApiNames": true,
  "enableVectorProperties": true,
  "enableTimeSeriesProperties": false,
  "enableExternalSystems": false,
  "enableMediaReferenceProperties": false
}
```

**설명**: 각 키는 저장소의 코드 생성과 검사에서 특정 기능을 켜고 끄는 불리언 플래그입니다. 이 페이지에서 직접 언급하는 것은 두 가지입니다. `enableModelFunctions`는 라이브 배포(모델) 사용, `enableExternalSystems`는 외부 소스(REST API 등) 사용을 켭니다. 나머지 플래그의 의미는 원문에서 따로 설명하지 않으므로 이름으로만 짐작할 수 있습니다.

`functions.json` 파일에서 해당 플래그를 켜지 않고 리소스를 가져오면 저장소의 검사(check)가 실패할 수 있습니다. 가져온 라이브 배포를 사용하려면 `enableModelFunctions`를 true로 설정하세요. 가져온 소스를 사용하려면 `enableExternalSystems`를 true로 설정하세요.

## 정리

- TypeScript v1 함수 저장소에서는 Code Repositories의 Resource imports 사이드바로 온톨로지 타입, 언어 모델, 라이브 배포, 외부 소스를 가져오고 관리합니다(신규 작업은 TypeScript v2 권장).
- 저장소의 모든 가져오기는 한 온톨로지에 속해야 하고, 가져오기를 확정하면 Code Assist가 재시작되어 `@foundry/ontology-api` 같은 생성된 패키지로 리소스를 쓸 수 있게 됩니다.
- 코드에서 참조하려면 API 이름이 필요하고, 값 타입에 의존하는 리소스끼리 버전이 다르면 충돌이 납니다.
- 가져오기 상태는 `resources.json`(현재 `version: 1`)에 기록되어 Git으로 관리되며, 라이브 배포와 외부 소스는 `functions.json`의 `enableModelFunctions`, `enableExternalSystems` 플래그를 켜야 사용할 수 있습니다.
