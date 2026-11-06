# 함수 시작하기 (Getting started)

- 원문: https://www.palantir.com/docs/foundry/functions/getting-started/
- 사이드바 위치: Define Ontologies > Functions > Getting started

이 페이지는 어떤 언어를 쓰든 공통으로 거치는 함수(function) 개발 흐름, 즉 리포지토리 만들기, 개발 환경 고르기, 라이브 프리뷰로 테스트하기, 버전 태그로 게시하기, 게시된 함수 실행하기를 개괄합니다. 언어별 세부 절차는 별도 튜토리얼로 안내합니다.

Foundry에서 함수를 시작할 때 선택할 수 있는 언어는 TypeScript v1, TypeScript v2, Python 세 가지입니다. 언어별로 지원되는 기능에 대한 자세한 내용은 [언어별 기능 지원](02_language-feature-support.md) 명세를 참고하세요.

언어마다 지원 기능은 다르지만, 함수 실행, 테스트, 게시 같은 기본 플랫폼 기능은 어떤 언어에서든 똑같이 사용할 수 있습니다. 이 페이지는 어떤 언어로 작업하든 함수 리포지토리를 사용하는 방법을 이해할 수 있도록 이러한 기능을 개괄합니다.

특정 언어로 시작하는 더 자세한 방법은 아래 튜토리얼을 참고하세요.

* [TypeScript v1 함수 시작하기](12_typescript-v1/01_typescript-v1-getting-started.md)
* [TypeScript v2 함수 시작하기](10_typescript-v2/01_typescript-v2-getting-started.md)
* [Python 함수 시작하기](11_python/01_python-getting-started.md)

함수 리포지토리 생성과 사용에 대한 일반 정보는 아래 섹션을 참고하세요.

<a id="create-a-functions-repository"></a>
## 함수 리포지토리 만들기 (Create a functions repository)

함수 리포지토리를 만들 때 필요에 가장 맞는 언어를 선택할 수 있습니다. 원하는 프로젝트에서 **+ New > Repository**를 선택해 직접 함수 리포지토리를 초기화하거나, Code Repositories 애플리케이션의 오른쪽 위에서 **+ New repository**를 선택해 초기화할 수 있습니다. 리포지토리가 초기화되면 함수를 추가하고 실행할 수 있습니다.

![함수 코드 리포지토리 만들기.](https://www.palantir.com/docs/resources/foundry/functions/functions-create-repo.png)

특정 언어로 함수 리포지토리를 만드는 자세한 방법은 아래 튜토리얼 섹션을 참고하세요.

* [TypeScript v1 함수 리포지토리 만들기](12_typescript-v1/01_typescript-v1-getting-started.md#create-a-typescript-v1-functions-repository)
* [TypeScript v2 함수 리포지토리 만들기](10_typescript-v2/01_typescript-v2-getting-started.md#create-a-typescript-v2-functions-repository)
* [Python 함수 리포지토리 만들기](11_python/01_python-getting-started.md#create-a-python-functions-repository)

**설명**: 함수 리포지토리는 Foundry 안에서 관리되는 Git 리포지토리로, 함수 코드와 빌드 설정이 들어 있습니다. 언어를 고르면 그 언어용 템플릿(프로젝트 구조, 의존성 설정 파일, 예제 함수)으로 초기화됩니다.

<a id="development-environment-options"></a>
## 개발 환경 옵션 (Development environment options)

[VS Code 워크스페이스](https://www.palantir.com/docs/foundry/vs-code/overview/)에서도 같은 인터페이스와 도구로 함수 리포지토리를 작성할 수 있습니다. VS Code 워크스페이스는 라이브 프리뷰, 리소스 가져오기(import), SDK 생성, 릴리스 관리를 지원합니다.

함수 리포지토리는 Code Repositories나 VS Code 워크스페이스 중 하나에서 개발할 수 있습니다.

* **[VS Code 워크스페이스](https://www.palantir.com/docs/foundry/vs-code/overview/) (권장):** Visual Studio Code용 Palantir 확장을 통해 라이브 프리뷰, 리소스 가져오기, SDK 생성, 브랜치 관리, 통합 터미널, 함수 릴리스 관리를 사용합니다. 함수 리포지토리를 VS Code 워크스페이스에서 열려면 리포지토리 헤더에서 **Edit in VS Code**를 선택합니다.
* **Code Repositories:** 아래 섹션에서 설명하는 웹 기반 개발 환경을 사용해 함수를 개발하고 관리합니다.

[함수 개발을 위한 VS Code 사용법을 알아보세요.](06_navigating-vscode.md)

<a id="test-in-live-preview"></a>
## 라이브 프리뷰에서 테스트하기 (Test in live preview)

함수 라이브 프리뷰를 사용하면 리포지토리에 커밋하기 전에 함수를 테스트할 수 있습니다. 리포지토리에 함수를 추가한 뒤 라이브 프리뷰에서 실행할 수 있습니다. 하단 도구 모음에서 **Functions**를 열고 **Live Preview**를 선택합니다. 함수를 고르고 입력 값을 넣은 다음 **Run**을 선택해 함수를 실행합니다.

![함수 라이브 프리뷰에서 새 함수 실행하기.](https://www.palantir.com/docs/resources/foundry/functions/tsv2-functions-helper-preview-run.png)

**주의**: 라이브 프리뷰는 게시된 함수와 다른 런타임 환경에서 실행됩니다. CPU 리소스, 사용 가능한 메모리, 함수가 타임아웃되기 전까지 실행될 수 있는 시간 등이 다릅니다. [게시된 함수의 런타임 환경 관리하기.](07_function-management/02_manage-functions.md)

오른쪽 위의 **Commit**을 선택해 변경 사항을 리포지토리의 `master` 브랜치에 커밋합니다.

**설명**: 라이브 프리뷰는 아직 커밋하지 않은 코드로 함수를 바로 실행해 보는 기능이라, 단위 테스트를 돌리듯 입력을 바꿔 가며 결과를 빠르게 확인할 수 있습니다. 다만 실행 환경의 자원과 시간 제한이 실제 게시 환경과 다르므로, 프리뷰에서 통과했다고 게시 후에도 같은 성능이나 타임아웃 동작을 보장하지는 않습니다.

> **중간 요약**: 함수 리포지토리는 프로젝트나 Code Repositories에서 언어를 골라 만들고, VS Code 워크스페이스(권장)나 Code Repositories에서 개발합니다. 커밋 전에 라이브 프리뷰로 테스트할 수 있지만, 런타임 환경은 게시된 함수와 다릅니다.

<a id="publish-your-functions"></a>
## 함수 게시하기 (Publish your functions)

작업을 커밋하면 **Tag version**(버전 태그) 옵션이 보입니다. 이 옵션은 리포지토리의 모든 함수를 함수 레지스트리(functions registry)에 게시해 [플랫폼 전체에서 접근할 수 있게](08_function-consumption/01_use-functions.md) 합니다.

!["Tag version" 옵션.](https://www.palantir.com/docs/resources/foundry/functions/ts-functions-tags.png)

**Tag version**을 선택해 `master` 브랜치에서 릴리스를 태그합니다. 변경 범위에 따라 태그 이름을 정한 다음 **Tag and release**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/new-functions-tag.png" alt="새 릴리스에 태그할 버전 유형 선택하기." width="500">

함수가 태그되고 릴리스되는 진행 상황을 보려면 **View** 팝업을 선택하거나 **Tags** 탭으로 이동합니다. **Step 2: Release**가 완료되면 게시된 함수를 선택해 함수 레지스트리에서 확인합니다.

**주의**: 권한이 전파되는 동안에는 Workshop이나 함수 레지스트리에서 함수 이름으로 바로 검색되지 않을 수 있습니다.

![태그 검사와 릴리스 검사가 모두 통과하여 새 함수가 게시된 화면.](https://www.palantir.com/docs/resources/foundry/functions/tsv1-functions-tags-and-releases.png)

**설명**: 태그는 Git에서 특정 커밋에 붙이는 버전 이름(예: `1.2.0`)입니다. "변경 범위에 따라 태그 이름을 정한다"는 것은 시맨틱 버저닝에 따라 호환성을 깨는 변경이면 주 버전, 기능 추가면 부 버전, 버그 수정이면 패치 버전을 올린다는 뜻입니다. 태그가 붙은 커밋이 빌드되어 레지스트리에 등록되면, Workshop이나 액션 같은 다른 애플리케이션이 그 버전을 골라 사용할 수 있습니다.

<a id="run-your-function"></a>
## 함수 실행하기 (Run your function)

태그 검사가 통과하면 Code Repositories의 **Code** 탭으로 돌아가 하단 도구 모음에서 **Functions**를 선택합니다. **Published** 섹션 아래에 새 함수가 보일 것입니다. 함수를 선택하고 새 함수를 실행해 보세요.

![함수 도우미(functions helper)에서 새 함수 실행하기.](https://www.palantir.com/docs/resources/foundry/functions/tsv1-functions-helper-run.png)

[플랫폼 전반에서 함수를 활용하는 방법을 더 알아보세요.](08_function-consumption/01_use-functions.md)

> **중간 요약**: 커밋 후 Tag version으로 버전을 태그하고 릴리스하면 함수가 레지스트리에 게시되어 플랫폼 전체에서 쓸 수 있습니다. 게시된 함수는 Functions 도구 모음의 Published 섹션에서 실행해 볼 수 있습니다.

## 정리

- 함수는 TypeScript v1, TypeScript v2, Python 중 하나로 작성하며, 실행, 테스트, 게시 같은 기본 흐름은 언어와 관계없이 같습니다.
- 리포지토리는 프로젝트의 **+ New > Repository**나 Code Repositories의 **+ New repository**로 만듭니다.
- 개발은 VS Code 워크스페이스(권장)나 웹 기반 Code Repositories에서 할 수 있습니다.
- 커밋 전에는 라이브 프리뷰로 테스트하고, 커밋 후 Tag version으로 버전을 태그해 함수 레지스트리에 게시합니다.
- 게시된 함수는 Functions 도구 모음의 Published 섹션에서 실행할 수 있으며, 권한 전파 전에는 검색되지 않을 수 있습니다.
