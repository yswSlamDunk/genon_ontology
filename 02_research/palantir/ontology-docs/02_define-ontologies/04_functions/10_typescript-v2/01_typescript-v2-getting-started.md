# TypeScript v2 함수 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/functions/typescript-v2-getting-started/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v2 > Getting started

이 페이지는 TypeScript v2로 첫 함수(function)를 만드는 전체 과정을 안내합니다. 저장소 생성, 함수 작성 규칙, 라이브 미리보기로 테스트, 커밋과 버전 태그로 공개, 공개된 함수 실행까지 차례로 다루며, 이후 온톨로지 SDK와 온톨로지 편집(edit)으로 넘어가는 출발점이 됩니다.

TypeScript v2를 사용하면 Node.js 런타임과 일급(first-class) OSDK 지원을 포함해 [TypeScript v1 대비 여러 핵심 개선 사항](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 활용할 수 있습니다. 아래 섹션을 읽고 시작해 보세요.

<a id="create-a-typescript-v2-functions-repository"></a>
## TypeScript v2 함수 저장소 만들기 (Create a TypeScript v2 functions repository)

원하는 프로젝트로 이동해 **+ New > Repository**를 선택하여 새 코드 저장소를 만듭니다. TypeScript v2 functions 템플릿을 선택해 저장소를 초기화합니다.

![TypeScript v2 함수 코드 저장소 만들기.](https://www.palantir.com/docs/resources/foundry/functions/tsv2-functions-create-repo.png)

저장소가 만들어지면 `typescript-functions/src/functions/helloWorld.ts` 파일로 이동합니다.

함수에 온톨로지 타입을 가져오려면, 먼저 **Resource imports** 사이드바에서 객체 타입과 링크 타입을 추가한 다음 온톨로지 SDK를 생성하고 설치해야 합니다. 이 단계는 [온톨로지 SDK 생성하기](03_typescript-v2-migration.md#generate-the-ontology-sdk)를 참고하세요.

<a id="write-a-function"></a>
## 함수 작성하기 (Write a function)

새 함수를 작성하려면 저장소의 `typescript-functions/src/functions` 디렉터리에 새 파일을 만들고 설명적인 이름을 붙입니다(예: `helloWorld.ts`). Foundry가 함수를 감지할 수 있도록 `export default`를 사용해 함수를 작성합니다.

```typescript tab="TypeScript v2"
export default function helloWorld(): string {
    return "Hello World!";
}
```

**설명**: 이 함수는 입력을 받지 않고 문자열 `"Hello World!"`를 반환합니다. 핵심은 `export default`입니다. 한 파일에서 기본(default)으로 내보낸 함수 하나를 Foundry가 공개 대상 함수로 인식합니다. 반환 타입 `string`처럼 입력과 출력 타입을 명시해야 Foundry가 함수의 시그니처를 알 수 있습니다.

함수를 Foundry에 공개하려면 다음 조건을 충족해야 합니다.

1. 함수를 `typescript-functions/src/functions` 디렉터리 안의 `.ts` 파일에 정의합니다. 이 디렉터리 안에서는 관련 함수를 하위 디렉터리로 묶을 수도 있습니다.
2. 파일 이름은 함수 이름과 일치해야 합니다. `myFunction`이라는 함수를 공개하려면 `typescript-functions/src/functions` 디렉터리 안의 `myFunction.ts` 파일에 정의해야 합니다.
3. TypeScript 함수는 파일의 기본 내보내기(default export)여야 합니다.
4. 함수의 입력과 출력 타입은 [타입 레퍼런스](../04_types-reference.md)에 정리된 지원 함수 타입을 따라야 합니다.

함수의 파일 경로는 그 파일에서 공개되는 함수를 유일하게 식별하는 데 사용되므로, 파일 경로를 바꾸면 새로운 함수가 공개됩니다.

**설명**: 예를 들어 `src/functions/helloWorld.ts`를 `src/functions/greetings/helloWorld.ts`로 옮기면, Foundry는 이를 기존 함수의 새 버전이 아니라 별개의 새 함수로 취급합니다. 데이터베이스에서 기본 키(primary key)가 바뀌면 다른 행이 되는 것과 같은 원리로, 파일 경로가 함수의 식별자 역할을 합니다. 그래서 이미 Workshop 등에서 쓰고 있는 함수의 파일을 옮기면 사용처가 새 함수를 자동으로 따라가지 않습니다.

> **중간 요약**: TypeScript v2 함수는 `typescript-functions/src/functions` 아래의 `.ts` 파일에 파일 이름과 같은 이름으로 작성하고 `export default`로 내보내야 합니다. 파일 경로가 함수의 식별자이므로 경로를 바꾸면 새 함수가 됩니다.

<a id="test-in-live-preview"></a>
## 라이브 미리보기로 테스트하기 (Test in live preview)

라이브 미리보기에서 함수를 테스트하려면 **Functions** 도우미를 열고 **Live preview**를 선택합니다. 함수를 고르고 **Run**을 선택해 실행합니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/tsv2-functions-helper-preview-run.png" alt="functions 도우미에서 새 함수 실행하기." width="900">

<a id="commit-and-publish-a-function"></a>
## 함수 커밋하고 공개하기 (Commit and publish a function)

창 오른쪽 위의 **Commit**을 선택해 변경 사항을 저장소의 `master` 브랜치에 커밋합니다. 함수의 검사(check)를 보려면 페이지 상단의 **Checks** 탭을 엽니다. 커밋을 하고 나면 여기에서 실행 중인 검사를 볼 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/tsv2-functions-publish.png" alt="검사를 선택해 진행 상황 보기." width="500">

작업을 커밋한 뒤에는 **Tag version** 옵션이 보입니다. 이 옵션은 저장소의 모든 함수를 공개합니다.

![사용 가능한 태그 옵션.](https://www.palantir.com/docs/resources/foundry/functions/ts-functions-tags.png)

**Tag version**을 선택해 `master` 브랜치에서 릴리스를 태그합니다. 변경 범위에 맞춰 태그 이름을 정한 다음 **Tag and release**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/new-functions-tag.png" alt="새 릴리스에 태그할 버전 유형 고르기." width="500">

**설명**: 태그 이름은 시맨틱 버저닝 형식(`MAJOR.MINOR.PATCH`)의 버전 번호입니다. "변경 범위에 맞춰"라는 것은 버그 수정이면 patch, 하위 호환되는 기능 추가면 minor, 기존 사용처를 깨뜨리는 변경이면 major를 올린다는 뜻입니다. Git에서 태그는 특정 커밋에 붙이는 이름이며, 여기서는 그 커밋 상태의 함수들을 해당 버전으로 공개하는 계기가 됩니다.

함수가 태그되고 릴리스되는 진행 상황을 보려면 **View** 팝업을 선택하거나 **Tags** 탭으로 이동합니다. **Step 2: Release**가 완료되면 공개된 함수를 선택해 함수 레지스트리(function registry)에서 볼 수 있습니다.

**주의**: 권한이 전파되는 동안에는 Workshop이나 함수 레지스트리에서 함수 이름으로 바로 검색되지 않을 수 있습니다.

![태그 검사와 릴리스 검사가 모두 통과하여 새 함수가 공개된 모습.](https://www.palantir.com/docs/resources/foundry/functions/tsv2-functions-tags-and-releases.png)

> **중간 요약**: `master`에 커밋하고 Checks 탭에서 검사를 확인한 뒤, **Tag version**으로 버전을 태그하면 저장소의 모든 함수가 공개됩니다. 공개 직후에는 권한 전파 때문에 검색에 바로 나타나지 않을 수 있습니다.

<a id="use-a-new-function"></a>
## 새 함수 사용하기 (Use a new function)

태그에 대한 검사가 통과하면 **Code Repositories**의 **Code** 탭으로 돌아가 **Functions** 도우미를 선택합니다. 이제 **Published** 섹션 아래에서 함수를 볼 수 있습니다. 함수를 선택하고 새 함수를 실행해 보세요.

![functions 도우미에서 새 함수 실행하기.](https://www.palantir.com/docs/resources/foundry/functions/tsv2-functions-helper-run.png)

<a id="next-steps"></a>
## 다음 단계 (Next steps)

기본 함수를 만들고 공개한 뒤에는 다음 기능을 살펴보세요.

* **온톨로지 SDK:** 온톨로지 객체를 조회하거나 편집하려면 먼저 필요한 객체 타입과 링크 타입을 가져온 다음, [온톨로지 SDK를 생성하고 설치](03_typescript-v2-migration.md#generate-the-ontology-sdk)하세요.
* **온톨로지 편집:** 함수 안에서 [객체를 생성, 수정, 삭제하는 방법](04_typescript-v2-ontology-edits.md)을 알아보세요.
* **스테이징된 쓰기(Staged writes) \[Beta]:** 쓰기 후 읽기(read-after-write) 보장이나 중첩된 함수 호출이 필요한 편집 함수라면 [스테이징된 쓰기](05_typescript-v2-staged-writes.md)를 참고하세요.

## 정리

- TypeScript v2 함수 저장소는 **+ New > Repository**에서 TypeScript v2 functions 템플릿으로 만듭니다.
- 함수는 `typescript-functions/src/functions` 아래에 함수 이름과 같은 이름의 `.ts` 파일로 작성하고 `export default`로 내보내며, 지원되는 입력과 출력 타입만 써야 합니다.
- 파일 경로가 함수의 식별자이므로 경로를 바꾸면 새 함수가 공개됩니다.
- **Live preview**로 테스트하고, 커밋 후 **Tag version**과 **Tag and release**로 공개하면 **Published** 섹션에서 실행할 수 있습니다.
- 다음 단계로 온톨로지 SDK 생성, 온톨로지 편집, 스테이징된 쓰기를 살펴봅니다.
