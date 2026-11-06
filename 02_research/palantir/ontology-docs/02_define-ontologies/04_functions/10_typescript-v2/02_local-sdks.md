# 로컬 온톨로지 SDK (Local Ontology SDKs)

- 원문: https://www.palantir.com/docs/foundry/functions/local-sdks/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v2 > Local Ontology SDKs

이 페이지는 TypeScript v2와 Python 함수(function) 저장소에서 온톨로지 SDK(OSDK)를 별도 패키지로 설치하지 않고, 저장소 안에서 자동 생성해 쓰는 "로컬 SDK" 방식을 설명합니다. 새 저장소에서 로컬 SDK를 설정하는 방법, 명령줄로 SDK를 생성하는 방법, 기존 저장소를 로컬 SDK로 옮기는 방법을 다룹니다.

TypeScript v2 함수와 Python 함수는 **로컬 온톨로지 SDK(local Ontology SDK)를** 지원합니다. 로컬 SDK에서는 OSDK가 별도 패키지로 버전이 수동 관리되고 설치되는 대신, 리소스 가져오기(resource imports)로부터 자동으로 생성됩니다. 따라서 SDK의 타입이 항상 최신 리소스 가져오기 상태와 일치합니다. [Global Branching](https://www.palantir.com/docs/foundry/global-branching/overview/)을 완전히 지원하려면 로컬 SDK가 필요합니다.

**설명**: 온톨로지 SDK는 객체 타입, 링크 타입 같은 온톨로지 정의를 코드에서 쓸 수 있는 타입과 함수로 바꿔 준 코드 묶음입니다. 예를 들어 온톨로지에 `Employee` 객체 타입이 있으면, SDK에는 `Employee`라는 TypeScript 타입과 이를 조회하는 코드가 생성됩니다. 별도 패키지 방식에서는 온톨로지가 바뀔 때마다 새 SDK 버전을 만들어 저장소에 설치해야 했지만, 로컬 SDK에서는 저장소가 가져온 리소스 목록이 바뀌면 SDK가 다시 생성됩니다.

<a id="set-up-a-new-local-sdk"></a>
## 새 로컬 SDK 설정하기 (Set up a new local SDK)

저장소에서 처음으로 로컬 SDK를 만드는 경우 아래 단계를 따르세요.

1. Code Repositories나 VS Code에서 **Resources** 사이드 패널을 엽니다.
2. 패널 오른쪽 아래에서 **Select**를 선택합니다. 코드 편집기에 **Modify Import Resources** 탭이 열립니다.
3. 드롭다운 메뉴에서 사용할 수 있는 온톨로지를 선택합니다.
4. 사이드 패널에서 가져올 객체 타입, 링크 타입, 인터페이스 타입, 기타 엔터티를 선택합니다.

![온톨로지와 패키지 이름 선택을 보여 주는 Resources 사이드 패널.](https://www.palantir.com/docs/resources/foundry/functions/local-sdk-popover.png)

온톨로지에서 엔터티를 추가하면 SDK가 자동으로 새 버전으로 갱신되고, 저장소 안에 코드 바인딩이 생성됩니다. 그런 다음 SDK 패키지에서 온톨로지 엔터티를 가져와(import) 함수 시그니처에 사용할 수 있습니다. 함수의 버전을 태그하면 SDK가 CI에서 생성되어 함수 버전과 함께 묶이며, 태그한 시점의 온톨로지 상태를 반영합니다.

**설명**: 코드 바인딩(code binding)은 외부 정의(여기서는 온톨로지 스키마)를 특정 프로그래밍 언어에서 바로 쓸 수 있도록 생성된 코드입니다. CI(Continuous Integration)는 커밋이나 태그가 생길 때 자동으로 빌드와 검사를 돌리는 시스템입니다. 태그 시점에 SDK를 다시 생성해 함께 묶기 때문에, 공개된 함수 버전은 그 시점의 온톨로지 스키마에 맞춰 고정됩니다.

> **중간 요약**: Resources 사이드 패널에서 온톨로지와 가져올 엔터티를 고르면 SDK와 코드 바인딩이 자동 생성됩니다. 함수 버전을 태그하면 그 시점의 온톨로지 상태로 SDK가 CI에서 생성되어 함께 묶입니다.

<a id="generate-the-sdk-from-the-command-line"></a>
## 명령줄에서 SDK 생성하기 (Generate the SDK from the command line)

VS Code를 사용하지 않는다면 `./rune` 명령줄 도구로 로컬 SDK를 생성하고 다시 생성할 수 있습니다. 먼저 개발 환경을 준비합니다.

```bash
./rune env prepare
```

SDK를 처음 생성할 때는 패키지 이름을 지정합니다.

```bash
./rune sdk generate --sdk-package-name ontology
```

패키지 이름은 코드에서 온톨로지 엔터티를 가져오는 경로를 결정합니다(예: `import { MyObjectType } from "@ontology/sdk"`). 아무 패키지 이름이나 고를 수 있지만 `ontology`가 기본 관례입니다.

리소스 가져오기를 변경한 뒤 SDK를 다시 생성하려면 다음을 실행합니다.

```bash
./rune sdk generate
```

**설명**: 세 명령은 순서대로 개발 환경 준비, 패키지 이름을 정해 첫 SDK 생성, 이후 변경 사항을 반영한 재생성을 수행합니다. 패키지 이름을 `ontology`로 정하면 생성된 SDK는 `@ontology/sdk` 경로로 가져오게 됩니다.

저장소에 `./rune`이 없다면 `.palantir-scripts/install-rune`을 실행해 설치하세요.

> **중간 요약**: VS Code 없이도 `./rune env prepare`, `./rune sdk generate --sdk-package-name ontology`, `./rune sdk generate` 명령으로 SDK를 생성하고 갱신할 수 있습니다.

<a id="migrate-an-existing-repository-to-a-local-sdk"></a>
## 기존 저장소를 로컬 SDK로 마이그레이션하기 (Migrate an existing repository to a local SDK)

독립(standalone) SDK를 쓰는 저장소를 로컬 SDK로 마이그레이션하려면 다음을 따르세요.

1. 저장소에서 `functions.json` 파일을 찾아 `useSdkSidebar`를 `false`로 설정합니다.

2. **Resources** 사이드 패널로 이동합니다. 상단의 **Migrate**를 선택하여 로컬 SDK를 생성하고, 자동 생성된 변경 사항을 커밋합니다. TypeScript v2에서는 `package.json`과 `package-lock.json` 파일이 갱신됩니다. Python에서는 `meta.yaml`과 `hawk.lock` 파일이 갱신됩니다.

![로컬 SDK로 마이그레이션하는 버튼을 보여 주는 Resources 사이드 패널.](https://www.palantir.com/docs/resources/foundry/functions/local-sdk-migrate-popover.png)

**설명**: `package.json`과 `package-lock.json`은 Node.js 프로젝트의 의존성 목록과 정확한 설치 버전을 기록하는 파일이고, `meta.yaml`과 `hawk.lock`은 Python 저장소에서 같은 역할을 하는 파일입니다. 마이그레이션은 이 의존성 파일에서 별도 SDK 패키지 대신 로컬에서 생성된 SDK를 참조하도록 바꾸는 작업입니다.

## 정리

- 로컬 온톨로지 SDK는 TypeScript v2와 Python 함수에서 리소스 가져오기로부터 OSDK를 자동 생성하는 방식이며, Global Branching을 완전히 지원하려면 필요합니다.
- Resources 사이드 패널에서 온톨로지와 엔터티를 고르면 SDK와 코드 바인딩이 생성되고, 태그 시 CI에서 SDK가 생성되어 함수 버전과 함께 묶입니다.
- VS Code 없이도 `./rune` 도구로 SDK를 생성하고 갱신할 수 있으며, 패키지 이름이 import 경로를 결정합니다.
- 기존 저장소는 `functions.json`의 `useSdkSidebar`를 `false`로 바꾸고 **Migrate**를 실행해 로컬 SDK로 옮깁니다.
