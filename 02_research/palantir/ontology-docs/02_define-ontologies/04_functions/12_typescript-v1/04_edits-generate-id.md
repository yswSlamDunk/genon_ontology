# 새 객체에 고유 ID 생성하기 (Generate unique IDs for new objects)

- 원문: https://www.palantir.com/docs/foundry/functions/edits-generate-id/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v1 > Generate unique IDs for new objects

이 페이지는 객체를 새로 만드는 온톨로지 편집 함수(function)에서 기본 키(primary key)로 쓸 고유 ID를 생성하는 방법을 TypeScript v2와 TypeScript v1으로 나누어 설명합니다. 새 객체에는 반드시 기본 키가 있어야 하므로, 사용자가 직접 입력하지 않는 경우 함수가 겹치지 않는 값을 만들어야 합니다.

[온톨로지 편집 함수](../09_language-agnostic-features/01_edits-overview.md)에서 객체를 만들 때, 새로 만든 객체에 고유 ID를 생성하고 싶을 수 있습니다.

**설명**: 여기서 쓰는 ID는 UUID(Universally Unique Identifier)입니다. UUID 버전 4는 122비트의 무작위 값으로 `3f2a9c1e-8b4d-4e2a-9c1f-0a7b6d5e4c3b` 같은 36자 문자열로 표현됩니다. 중앙에서 번호를 발급하지 않아도 두 값이 겹칠 확률이 사실상 0이므로, 여러 사용자가 동시에 객체를 만들어도 기본 키가 충돌하지 않습니다.

<a id="typescript-v2"></a>
## TypeScript v2

TypeScript v2에는 내장되거나 플랫폼 고유한 UUID 생성기가 없습니다. npm의 [`uuid` 패키지 ↗](https://www.npmjs.com/package/uuid) 같은 표준 UUID 라이브러리를 사용하세요.

<a id="install-the-package"></a>
### 패키지 설치하기 (Install the package)

저장소의 의존성에 `uuid` 패키지를 추가합니다.

```bash
npm install uuid
npm install --save-dev @types/uuid
```

**설명**: 첫 줄은 실행 시 필요한 `uuid` 라이브러리를, 둘째 줄은 TypeScript가 이 라이브러리의 타입을 알 수 있도록 하는 타입 정의 파일을 개발 의존성으로 설치합니다.

<a id="use-the-package-in-code"></a>
### 코드에서 패키지 사용하기 (Use the package in code)

```typescript
import { v4 as uuidv4 } from 'uuid';

export default function createFlightScenario(): void {
    const uniqueId = uuidv4();
    // uniqueId를 새 객체의 기본 키로 사용합니다
}
```

<a id="typescript-v1"></a>
## TypeScript v1

**팁**: 이 문서는 TypeScript v1 함수에 한정된 내용입니다. Ontology SDK 지원과 구성 가능한 리소스 요청을 포함한 [더 강력한 기능](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 위해 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)하는 것을 권장합니다.

TypeScript v1 함수에서는 `@foundry/functions-utils` 패키지를 사용해 전역적으로 고유한 식별자를 생성합니다.

<a id="import-the-package"></a>
### 패키지 가져오기 (Import the package)

`@foundry/functions-utils` 패키지는 기본으로 설치되어 있지만, `package.json` 파일에 이 패키지가 없다면 다음과 같이 합니다.

* `"dependencies"` 섹션에 `"@foundry/functions-utils": "0.1.0"`을 추가합니다.

[의존성 추가에 관한 문서](09_add-dependencies.md)에 언급된 대로, 새 패키지를 자동 완성에서 사용할 수 있도록 Code Assist를 다시 시작하는 것을 잊지 마세요.

<a id="use-the-package-in-code"></a>
### 코드에서 패키지 사용하기 (Use the package in code)

고유 ID를 생성하려면 `@foundry/functions-utils` 패키지의 `Uuid.random()` 유틸리티 함수를 사용할 수 있습니다. 아래 코드 예제는 예시 온톨로지 편집 함수에서 `random` 함수를 사용하는 방법을 보여 줍니다.

```typescript
import { OntologyEditFunction, Timestamp } from "@foundry/functions-api";
import { Objects } from "@foundry/ontology-api";
import { Uuid } from "@foundry/functions-utils";

export class ExampleEditFunctions {
    @Edits(FlightScenario)
    @OntologyEditFunction()
    public createFlightScenario(): void {
        const scenario = Objects.create().flightScenarios(Uuid.random());
        scenario.scenarioName = "New scenario";
        scenario.creationTime = Timestamp.now();
    }
}
```

**설명**: `Uuid.random()`이 만든 문자열을 `Objects.create().flightScenarios(...)`의 기본 키 인자로 넘겨 새 FlightScenario 객체를 만들고, 이름과 생성 시각 속성을 채웁니다. 함수가 호출될 때마다 새 UUID가 만들어지므로 같은 함수를 여러 번 실행해도 객체가 서로 덮어쓰지 않습니다.

## 정리

- 새 객체의 기본 키로 쓸 고유 ID는 UUID로 생성합니다.
- TypeScript v2는 내장 생성기가 없으므로 npm `uuid` 패키지(`v4`)를 설치해 사용합니다.
- TypeScript v1은 기본 설치된 `@foundry/functions-utils`의 `Uuid.random()`을 사용하며, 패키지가 없으면 `package.json`에 추가하고 Code Assist를 다시 시작합니다.
