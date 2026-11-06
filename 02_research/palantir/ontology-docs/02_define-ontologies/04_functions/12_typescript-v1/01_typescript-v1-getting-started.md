# TypeScript v1 함수 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/functions/typescript-v1-getting-started/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v1 > Getting started

이 페이지는 TypeScript v1으로 첫 함수(function)를 만드는 튜토리얼입니다. 함수 저장소를 만들고, 클래스 메서드로 함수를 작성하고, 실시간 미리 보기로 실행해 본 뒤, 버전 태그를 달아 게시하고 사용하는 전체 흐름을 다룹니다.

**팁**: 이 문서는 TypeScript v1 함수에 한정된 내용입니다. 이 페이지의 TypeScript v2 버전은 [TypeScript v2 함수 시작하기](../10_typescript-v2/01_typescript-v2-getting-started.md)를 참고하세요. Ontology SDK 지원과 구성 가능한 리소스 요청을 포함한 [더 강력한 기능](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 위해 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)하는 것을 권장합니다.

<a id="create-a-typescript-v1-functions-repository"></a>
## TypeScript v1 함수 저장소 만들기 (Create a TypeScript v1 functions repository)

원하는 프로젝트로 이동해 **+ New > Repository**를 선택해 새 코드 저장소를 만듭니다. TypeScript functions 템플릿을 선택해 저장소를 초기화합니다.

![TypeScript v1 함수 코드 저장소 만들기.](https://www.palantir.com/docs/resources/foundry/functions/tsv1-functions-create-repo.png)

저장소가 만들어지면 `functions-typescript/src/index.ts` 파일로 이동합니다.

<a id="write-a-function"></a>
## 함수 작성하기 (Write a function)

이 저장소의 함수는 TypeScript 클래스 안에 정의되어야 하고, 그 클래스는 `functions-typescript/src/index.ts` 파일에서 export되어야 합니다. `index.ts`에 미리 채워진 예제에 함수를 작성해도 되고, 새 파일을 만들어도 됩니다. 새 파일을 만든다면 `index.ts`에서 그 클래스를 export해야 합니다.

아래는 기본 예제입니다.

```typescript tab="TypeScript v1"
import { Function, Integer } from "@foundry/functions-api";

export class ExampleFunctions {

    @Function()
    public addIntegers(a: Integer, b: Integer): Integer {
         return a + b;
    }
}
```

**설명**: 정수 두 개를 받아 합을 반환하는 함수입니다. `@Function()` 데코레이터가 붙은 `public` 메서드가 Foundry에 함수로 등록됩니다. 함수는 독립된 전역 함수가 아니라 클래스의 메서드로 작성한다는 점이 TypeScript v1의 특징입니다.

위 코드를 `exampleFunctions.ts`라는 파일에 작성했다면, 아래와 같이 index 파일에서 export해야 합니다.

```typescript tab="TypeScript v1"
// functions-typescript/src/index.ts 안에서

export * from "./relative/path/to/exampleFunctions";
```

**설명**: `export * from`은 다른 모듈이 export한 모든 것을 이 파일에서 다시 export하는 구문입니다. Foundry는 `index.ts`가 export하는 클래스만 살펴보므로, 이 줄이 없으면 `ExampleFunctions`의 함수가 발견되지 않습니다.

> **중간 요약**: TypeScript functions 템플릿으로 저장소를 만들고, 클래스 안에 `@Function()` 메서드로 함수를 작성한 뒤 그 클래스를 `index.ts`에서 export합니다.

<a id="test-in-live-preview"></a>
## 실시간 미리 보기로 테스트하기 (Test in live preview)

새 함수를 추가한 뒤 functions 도우미(helper)에서 실행할 수 있습니다. **Functions** 도우미를 열고 **Live Preview**를 선택합니다. `range` 함수를 선택하고 입력 값을 넣은 뒤 **Run**을 선택해 코드를 실행합니다.

**설명**: 원문은 여기서 `range` 함수를 언급하지만, 위 예제에서 작성한 함수는 `addIntegers`입니다. 원문 스크린샷의 예제 함수 이름을 그대로 쓴 것으로 보이며, 실제로는 자신이 작성한 함수를 선택하면 됩니다.

![functions 도우미에서 새 함수 실행하기.](https://www.palantir.com/docs/resources/foundry/functions/tsv1-functions-helper-preview-run.png)

오른쪽 위의 **Commit**을 선택해 변경 사항을 저장소의 `master` 브랜치에 커밋합니다.

<a id="publish-a-function"></a>
## 함수 게시하기 (Publish a function)

작업을 커밋하면 **Tag version** 옵션이 보입니다. 이 옵션은 저장소의 모든 함수를 게시합니다.

![새 버전으로 브랜치에 태그를 다는 옵션.](https://www.palantir.com/docs/resources/foundry/functions/ts-functions-tags.png)

**Tag version**을 선택해 `master` 브랜치에서 릴리스 태그를 만듭니다. 변경 범위에 맞게 태그 이름을 정한 다음 **Tag and release**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/new-functions-tag.png" alt="새 릴리스에 태그할 버전 유형 선택." width="500">

**설명**: 태그 이름은 보통 `1.2.3` 같은 시맨틱 버저닝(semantic versioning) 형식을 따릅니다. 호환되지 않는 변경이면 첫 자리(major), 기능 추가면 둘째 자리(minor), 버그 수정이면 셋째 자리(patch)를 올립니다. 위 화면의 버전 유형 선택이 이 구분입니다.

함수에 태그가 달리고 릴리스되는 진행 상황을 보려면 **View** 팝업을 선택하거나 **Tags** 탭으로 이동합니다. **Step 2: Release**가 완료되면 게시된 함수를 선택해 함수 레지스트리(function registry)에서 확인합니다.

**주의**: 권한이 전파되는 동안에는 Workshop이나 함수 레지스트리에서 함수 이름으로 바로 검색되지 않을 수 있습니다.

![태그와 릴리스 체크가 모두 통과되어 새 함수가 게시됨.](https://www.palantir.com/docs/resources/foundry/functions/tsv1-functions-tags-and-releases.png)

> **중간 요약**: Live Preview로 함수를 시험 실행하고 `master`에 커밋한 뒤, Tag version으로 버전 태그를 달면 저장소의 모든 함수가 게시됩니다.

<a id="use-a-new-function"></a>
## 새 함수 사용하기 (Use a new function)

태그 체크가 통과하면 **Code Repositories**의 **Code** 탭으로 돌아가 **Functions** 도우미를 선택합니다. 이제 **Published** 섹션 아래에 새 `range` 함수가 보여야 합니다. 함수를 선택해 실행합니다.

![functions 도우미에서 새 함수 실행하기.](https://www.palantir.com/docs/resources/foundry/functions/tsv1-functions-helper-run-2.png)

<a id="next-steps"></a>
### 다음 단계 (Next steps)

이 튜토리얼에서는 Code Repositories를 사용해 저장소에서 TypeScript v1 함수를 작성하고, 게시하고, 테스트하는 방법을 배웠습니다. 다음으로 [객체에 대한 함수(functions on objects)](../13_functions-on-objects/02_foo-getting-started.md)를 작성하는 방법을 배우기를 권장합니다.

## 정리

- TypeScript v1 함수는 TypeScript functions 템플릿 저장소에서, 클래스의 `@Function()` 메서드로 작성합니다.
- 함수가 든 클래스는 반드시 `functions-typescript/src/index.ts`에서 export해야 합니다.
- Functions 도우미의 Live Preview로 커밋 전에 함수를 실행해 볼 수 있습니다.
- `master`에 커밋한 뒤 Tag version으로 태그를 달면 저장소의 모든 함수가 게시되고, Published 섹션에서 사용할 수 있습니다.
- 새 기능이 필요하면 TypeScript v2로 마이그레이션하는 것이 권장됩니다.
