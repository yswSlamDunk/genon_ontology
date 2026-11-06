# VS Code 사용법 (Navigating VS Code)

- 원문: https://www.palantir.com/docs/foundry/functions/navigating-vscode/
- 사이드바 위치: Define Ontologies > Functions > Navigating VS Code

이 페이지는 Foundry의 VS Code 작업 공간(workspace)에서 함수(function) 저장소를 다루는 방법을 설명합니다. 온톨로지 리소스와 외부 소스를 저장소로 가져오는 방법, Palantir 확장(extension)으로 브랜치를 만들고 함수를 미리 실행하고 게시하는 방법, 그리고 개발 속도를 높이는 단축키와 설정을 다룹니다.

[VS Code 작업 공간](https://www.palantir.com/docs/foundry/vs-code/overview/)과 [Visual Studio Code용 Palantir 확장](https://www.palantir.com/docs/foundry/palantir-extension-for-visual-studio-code/overview/)을 함께 사용하면 에디터를 떠나지 않고 리소스 가져오기, 함수 미리 보기, 브랜치 관리, 변경 사항 커밋과 게시, 저장소 업그레이드, 로컬 개발 도구 사용을 할 수 있습니다.

<a id="import-resources-into-a-functions-repository"></a>
## 함수 저장소로 리소스 가져오기 (Import resources into a functions repository)

함수에서 Foundry 리소스를 사용하려면 먼저 그 리소스를 저장소로 가져와야(import) 합니다.

**설명**: 함수 코드에서 `Employee` 같은 객체 타입을 쓰려면, 그 객체 타입의 정의(속성 이름과 타입)를 바탕으로 생성된 코드가 저장소에 있어야 합니다. 리소스를 가져오면 이 코드 생성(code generation)이 일어나고, 그 결과로 코드에서 타입 검사와 자동 완성을 받을 수 있습니다. 프로그래밍 언어에서 라이브러리를 `import`해야 그 안의 클래스를 쓸 수 있는 것과 같은 원리입니다.

<a id="import-ontology-and-platform-resources"></a>
### 온톨로지와 플랫폼 리소스 가져오기 (Import Ontology and platform resources)

1. VS Code의 Activity Bar(작업 표시줄)에서 아래쪽 화살표 모양의 **Resource imports** 아이콘을 선택합니다.
2. **Resources** 패널에서 가져오려는 리소스에 따라 **Ontology SDK** 또는 **Platform** 탭을 선택합니다.
3. **Add**를 선택한 다음 객체 타입, 인터페이스, 액션, 쿼리 함수 같은 리소스 타입을 고릅니다. 소스를 가져오려면 [소스 가져오기](#import-a-source)의 단계를 따릅니다.
4. 사용할 리소스를 찾아 선택하고 선택을 확정합니다.
5. 코드에서 리소스를 참조하기 전에 코드 생성과 의존성 설치가 끝날 때까지 기다립니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/vscode-functions-resource-imports.png" alt="VS Code에서 Resource imports 아이콘이 선택되어 있고, Resources 패널에 사용 가능한 Ontology SDK 리소스 타입이 표시된 화면." width="500">

가장 최신의 리소스 타입을 사용하려면 [저장소 업그레이드](https://www.palantir.com/docs/foundry/code-repositories/repository-upgrades/)로 저장소를 최신 상태로 유지합니다. [온톨로지 타입 가져오기](13_functions-on-objects/05_ontology-imports.md)에 대해 더 알아보세요.

<a id="import-a-source"></a>
### 소스 가져오기 (Import a source)

소스(source)는 가져오기 전에 추가 구성이 필요합니다. Data Connection에서 소스의 **Connection settings** 섹션을 열고, [내보내기(export)를 활성화](https://www.palantir.com/docs/foundry/data-connection/export-overview/#enable-exports-for-source)한 다음 [코드 저장소로 소스를 가져오는 것](https://www.palantir.com/docs/foundry/data-connection/external-transforms/#prerequisite-import-a-source-into-code)을 허용합니다.

**설명**: 여기서 소스는 Data Connection에 등록된 외부 시스템 연결(예: 외부 REST API 서버, 데이터베이스)을 말합니다. 함수가 외부 API를 호출하려면 이 연결 정보(주소, 인증 정보)를 저장소에서 쓸 수 있도록 허용해야 합니다.

소스를 구성하고 나면 저장소에서 사용할 수 있습니다. VS Code의 **Resource Imports** 패널에서 **Add > Sources**를 선택하면 선택 대화 상자가 열립니다. 이 대화 상자에서는 현재 저장소에서 사용하도록 활성화된 소스만 검색하고 선택할 수 있습니다. 원하는 소스가 대화 상자에 없으면 하단의 **External Systems** 링크를 클릭합니다. 이 링크는 저장소 설정을 열어 주며, 거기서 저장소에서 사용할 수 있는 소스를 구성할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/add-existing-connections.png" alt="External systems 설정 페이지에서 Add 메뉴가 펼쳐져 Existing connections와 Create new 옵션이 표시된 화면." width="600">

1. 저장소에 소스를 추가한 뒤 VS Code 작업 공간으로 돌아와 **Modify Resource Imports** 대화 상자에서 **Reload Results**를 선택합니다.
2. 사용할 소스를 추가합니다. 소스는 **Resource Imports** 사이드 패널에 나타나며, 거기서 별칭(alias)을 설정할 수 있습니다.
3. 함수에서 별칭으로 소스를 참조해 사용합니다. [소스 별칭](15_aliases/03_source-aliases.md)에 대해 더 알아보세요.

[함수에서 API 호출하기](09_language-agnostic-features/04_api-calls.md)와 [웹훅 사용하기](12_typescript-v1/10_webhooks.md)에 대해 더 알아보세요.

> **중간 요약**: 객체 타입, 인터페이스, 액션, 쿼리 함수는 Resource imports 패널에서 바로 가져올 수 있습니다. 외부 소스는 Data Connection에서 내보내기와 코드 저장소 가져오기를 허용하고 저장소 설정에 등록한 뒤 가져오며, 코드에서는 별칭으로 참조합니다.

<a id="develop-and-publish-with-the-palantir-extension"></a>
## Palantir 확장으로 개발하고 게시하기 (Develop and publish with the Palantir extension)

Activity Bar에서 Palantir 아이콘을 선택하면 Palantir 패널이 열립니다. 이 패널은 브랜치, 미리 보기, 커밋, 게시, 저장소 관리 작업을 제공합니다.

<img src="https://www.palantir.com/docs/resources/foundry/functions/vscode-functions-palantir-extension.png" alt="Palantir 확장 패널에 브랜치 컨트롤과 함께 함수 미리 보기, 변경 사항 커밋과 제안, 버전 태그, 저장소 업그레이드 작업이 표시된 화면." width="400">

<a id="create-or-switch-branches"></a>
### 브랜치 만들기와 전환하기 (Create or switch branches)

편집을 시작하기 전에 **Branch** 섹션에서 브랜치를 만들거나 전환합니다.

1. **Code** 또는 **Global** 탭을 선택합니다.
   * **Code** 브랜치는 코드 저장소 안의 변경을 담는 기본 Git 브랜치입니다.
   * **Global** 브랜치는 여러 지원 Foundry 애플리케이션과 리소스에 걸친 관련 변경을 함께 담을 수 있습니다.
2. 더하기 기호가 붙은 브랜치 모양의 브랜치 생성 아이콘을 선택합니다.
3. 새 브랜치의 이름을 입력하고 확인해 브랜치를 만듭니다.

글로벌 브랜치 지원 여부는 함수 언어와 저장소 구성에 따라 다릅니다. [VS Code에서의 브랜칭](https://www.palantir.com/docs/foundry/vs-code/global-branching/), [Code Repositories의 브랜치 옵션](https://www.palantir.com/docs/foundry/code-repositories/navigation/#branch-options), [글로벌 브랜치에서 함수 개발하고 게시하기](05_branching-functions.md)에 대해 더 알아보세요.

<a id="preview-a-function"></a>
### 함수 미리 보기 (Preview a function)

1. Palantir 패널에서 **Function preview**를 선택합니다.
2. 함수를 선택하고 입력값을 넣은 뒤 실행을 클릭하면, 그 입력값으로 코드가 실행됩니다.
3. 코드가 실행되는 동안 출력, 로그, 편집(edit) 등을 검토합니다. 이를 통해 함수를 디버그하고 테스트할 수 있습니다.

글로벌 브랜치에서 개발 중이라면 미리 보기는 Palantir 패널에서 현재 선택된 브랜치를 기준으로 실행됩니다. [라이브 미리 보기에서 함수 테스트하기](03_getting-started.md#test-in-live-preview)에 대해 더 알아보세요.

**설명**: 미리 보기에서 보이는 "편집(edit)"은 함수가 온톨로지 객체를 수정하도록 작성된 경우, 실제로 저장하지 않고 어떤 객체의 어떤 속성이 어떻게 바뀔지를 보여 주는 결과입니다. 덕분에 실제 데이터를 건드리지 않고 함수 동작을 확인할 수 있습니다.

<a id="commit-propose-and-tag-changes"></a>
### 변경 사항 커밋, 제안, 태그 (Commit, propose, and tag changes)

미리 보기와 테스트가 성공하면 다음을 진행합니다.

1. **Changes** 섹션에서 **Commit**을 선택하고, 변경된 파일을 검토한 다음 설명적인 커밋 메시지를 입력합니다.
2. 병합 전에 코드 리뷰가 필요한 작업이라면 **Propose changes**를 선택합니다.
3. **Tag version**을 선택해 버전을 고르고, 선택한 브랜치의 함수를 게시합니다.

**주의**: 태그를 붙이면 가장 최근에 편집한 함수만이 아니라 저장소의 모든 함수가 게시됩니다.

[함수 게시하기](03_getting-started.md#publish-your-functions)와 [함수 버전 관리](07_function-management/01_functions-versioning.md)에 대해 더 알아보세요.

**설명**: Git에서 태그(tag)는 특정 커밋에 `1.2.0` 같은 이름표를 붙이는 기능입니다. Foundry 함수 저장소에서는 이 태그가 곧 게시 동작이어서, 태그 이름이 함수의 버전 번호가 됩니다.

<a id="upgrade-the-repository"></a>
### 저장소 업그레이드 (Upgrade the repository)

**Changes** 섹션에서 **Upgrade**를 선택하면 저장소 업그레이드가 시작됩니다. 생성된 변경 사항을 검토하고, 테스트와 함수 미리 보기를 다시 실행한 다음 업그레이드를 커밋합니다. [자동 및 수동 저장소 업그레이드](https://www.palantir.com/docs/foundry/code-repositories/repository-upgrades/)에 대해 더 알아보세요.

> **중간 요약**: Palantir 패널에서 Code 또는 Global 브랜치를 만들고, Function preview로 입력값을 넣어 실행해 보고, Commit, Propose changes, Tag version 순서로 게시합니다. 태그는 저장소의 모든 함수를 게시한다는 점에 주의합니다.

<a id="tips-and-tricks-for-vs-code"></a>
## VS Code 팁과 요령 (Tips and tricks for VS Code)

다음 섹션은 함수 개발 속도를 높일 수 있는 선택적인 VS Code 기능과 단축키를 설명합니다.

<a id="run-npm-commands-from-the-functions-project"></a>
### 함수 프로젝트에서 npm 명령 실행하기 (Run npm commands from the functions project)

통합 터미널을 열고 함수 프로젝트의 `package.json` 파일이 있는 `functions-typescript` 디렉터리로 이동합니다. TypeScript v1과 TypeScript v2 함수 저장소는 같은 경로를 사용합니다.

```bash
cd functions-typescript
npm test
```

**설명**: 첫 줄은 함수 프로젝트 디렉터리로 이동하고, 둘째 줄은 `package.json`의 `scripts`에 정의된 `test` 스크립트(단위 테스트)를 실행합니다. npm 명령은 `package.json`이 있는 디렉터리에서 실행해야 하므로 먼저 이동하는 것입니다.

현재 프로젝트에서 사용 가능한 스크립트 목록을 보려면 `npm run`을 실행합니다. 포함된 테스트 프레임워크에 대한 자세한 내용은 [함수 단위 테스트](16_unit-testing-tsv1/01_unit-test-getting-started.md)를 참고하세요.

<a id="format-when-you-save"></a>
### 저장할 때 포맷하기 (Format when you save)

**Settings**를 열고 `format on save`를 검색한 뒤 **Editor: Format On Save**를 활성화합니다. `Cmd+S`(macOS) 또는 `Ctrl+S`(Windows/Linux)를 누르면 현재 파일이 저장되면서 설정된 포매터가 실행됩니다. Command Palette에서 **Format Document**를 실행할 수도 있습니다.

[VS Code의 포맷팅 ↗](https://code.visualstudio.com/docs/editing/codebasics#_formatting)에 대해 더 알아보세요.

<a id="use-ai-development-tools"></a>
### AI 개발 도구 사용하기 (Use AI development tools)

Palantir MCP는 VS Code 작업 공간에 기본으로 통합되어 있으며 TypeScript 함수 저장소를 위한 컨텍스트 도구를 제공합니다. 그래서 Continue 확장이 함수 코드, 가져온 온톨로지 리소스, Foundry 컨텍스트를 참조할 수 있습니다.

[VS Code 작업 공간의 AI 개발 도구](https://www.palantir.com/docs/foundry/vs-code/ai-development-tools/)와 [Palantir MCP](https://www.palantir.com/docs/foundry/palantir-mcp/overview/)에 대해 더 알아보세요.

**설명**: MCP(Model Context Protocol)는 AI 코딩 도우미가 외부 도구와 데이터에 접근하는 표준 프로토콜입니다. Continue는 VS Code용 AI 코딩 도우미 확장입니다. 즉, AI 도우미가 MCP를 통해 저장소에 가져온 객체 타입 정의 등을 읽고 코드를 제안할 수 있습니다.

<a id="use-built-in-navigation-and-editing-shortcuts"></a>
### 기본 제공 탐색과 편집 단축키 사용하기 (Use built-in navigation and editing shortcuts)

VS Code에는 작업 전환을 줄여 주는 단축키가 있습니다.

| 작업 | macOS | Windows/Linux |
| --- | --- | --- |
| Command Palette 열기 | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| 파일 빠르게 열기 | `Cmd+P` | `Ctrl+P` |
| 저장소 전체 검색 | `Cmd+Shift+F` | `Ctrl+Shift+F` |
| 현재 파일의 심볼로 이동 | `Cmd+Shift+O` | `Ctrl+Shift+O` |
| 심볼의 정의로 이동 | `F12` | `F12` |
| 심볼의 참조 찾기 | `Shift+F12` | `Shift+F12` |
| 심볼 이름을 바꾸고 참조도 함께 갱신 | `F2` | `F2` |
| 사용 가능한 빠른 수정(quick fix) 보기 | `Cmd+.` | `Ctrl+.` |

Quick Open에서 파일 이름 뒤에 콜론과 줄 번호를 붙이면(예: `myFunction.ts:42`) 해당 줄로 바로 이동합니다. 또 `Option`(macOS) 또는 `Alt`(Windows/Linux)를 누른 채 위치를 선택하면 커서를 여러 개 추가해 반복되는 코드를 동시에 편집할 수 있습니다. 전체 목록은 [VS Code 기본 키보드 단축키 ↗](https://code.visualstudio.com/docs/reference/default-keybindings)를 참고하세요.

> **중간 요약**: `functions-typescript` 디렉터리에서 npm 명령을 실행할 수 있고, 저장 시 자동 포맷, Palantir MCP 기반 AI 도구, VS Code 기본 단축키로 개발 속도를 높일 수 있습니다.

## 정리

- 함수에서 Foundry 리소스를 쓰려면 먼저 Resource imports 패널에서 가져와야 하며, 가져오면 코드 생성과 의존성 설치가 일어납니다.
- 외부 소스는 Data Connection에서 내보내기와 코드 가져오기를 허용하고 저장소에 등록한 뒤 별칭으로 사용합니다.
- Palantir 패널에서 Code 또는 Global 브랜치 관리, Function preview 실행, Commit, Propose changes, Tag version, Upgrade를 처리합니다.
- Tag version은 저장소의 모든 함수를 게시합니다.
- npm 명령, 저장 시 포맷, Palantir MCP, 단축키 같은 VS Code 기능으로 개발을 빠르게 할 수 있습니다.
