# 로컬 온톨로지 SDK (Local Ontology SDKs)

- 원문: https://www.palantir.com/docs/foundry/functions/local-sdks/
- 사이드바 위치: Define Ontologies > Functions > Python > Local Ontology SDKs

이 페이지는 함수 리포지토리 안에서 온톨로지 SDK(OSDK)를 자동으로 생성하는 로컬 SDK 방식을 설명합니다. 함수 코드가 객체 타입이나 링크 타입을 타입 안전하게 다루려면 그 타입들에 맞춘 코드(SDK)가 필요한데, 로컬 SDK는 이 코드를 별도 패키지로 관리하지 않고 리포지토리의 리소스 임포트 설정에서 바로 만들어 줍니다. 새로 설정하는 방법, 명령줄로 생성하는 방법, 기존 리포지토리를 옮기는 방법을 다룹니다.

TypeScript v2 함수와 Python 함수는 **로컬 온톨로지 SDK(local Ontology SDK)를** 지원합니다. 로컬 SDK에서는 OSDK를 별도 패키지로 수동 버전 관리하고 설치하는 대신, 리소스 임포트(resource imports)로부터 자동 생성합니다. 따라서 SDK 타입이 항상 최신 리소스 임포트 상태와 일치합니다. [Global Branching](https://www.palantir.com/docs/foundry/global-branching/overview/)을 완전히 지원하려면 로컬 SDK가 필요합니다.

**설명**: SDK(Software Development Kit)는 여기서 "온톨로지에 정의된 객체 타입, 속성(property), 링크 타입을 프로그래밍 언어의 클래스와 타입으로 옮겨 놓은 코드 묶음"을 뜻합니다. 예를 들어 온톨로지에 `brand`와 `capacity` 속성을 가진 Aircraft 객체 타입이 있으면, SDK에는 같은 이름의 필드를 가진 `Aircraft` 클래스가 생성됩니다. 덕분에 코드에서 `aircraft.capacity`를 쓸 때 에디터 자동 완성과 타입 검사를 받을 수 있습니다. 온톨로지에 속성을 추가했는데 SDK가 예전 버전이면 코드에서 그 속성을 쓸 수 없으므로, SDK를 온톨로지와 맞춰 두는 일이 중요합니다.

<a id="set-up-a-new-local-sdk"></a>
## 새 로컬 SDK 설정하기 (Set up a new local SDK)

리포지토리에서 처음으로 로컬 SDK를 만든다면 다음 단계를 따릅니다.

1. Code Repositories나 VS Code에서 **Resources** 사이드 패널을 엽니다.
2. 패널 오른쪽 아래에서 **Select**를 선택합니다. 코드 에디터에 **Modify Import Resources** 탭이 열립니다.
3. 드롭다운 메뉴에서 사용할 온톨로지를 선택합니다.
4. 사이드 패널에서 임포트할 객체 타입, 링크 타입, 인터페이스 타입, 기타 엔터티를 선택합니다.

![온톨로지와 패키지 이름 선택을 보여 주는 Resources 사이드 패널.](https://www.palantir.com/docs/resources/foundry/functions/local-sdk-popover.png)

온톨로지에서 엔터티를 추가하면 SDK가 자동으로 새 버전으로 갱신되고 리포지토리 안에 코드 바인딩(code bindings)이 생성됩니다. 그러면 SDK 패키지에서 온톨로지 엔터티를 임포트해 함수 시그니처에 사용할 수 있습니다. 함수 버전에 태그를 붙이면 CI에서 SDK가 생성되어 함수 버전과 함께 묶이며, 태그를 붙인 시점의 온톨로지 상태를 반영합니다.

**설명**: CI(Continuous Integration, 지속적 통합)는 코드가 커밋되거나 태그될 때 자동으로 빌드와 검사를 실행하는 시스템입니다. "태그 시점의 온톨로지 상태를 반영한다"는 것은, 게시된 함수 버전 1.0.0에 포함된 SDK가 태그를 만든 순간의 객체 타입 정의로 고정된다는 뜻입니다.

> **중간 요약**: **Resources** 사이드 패널에서 온톨로지와 임포트할 엔터티를 고르면 SDK가 자동으로 갱신되어 코드에서 바로 쓸 수 있고, 함수에 태그를 붙이면 그 시점의 온톨로지 상태로 SDK가 생성되어 함께 묶입니다.

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

패키지 이름은 코드에서 온톨로지 엔터티를 임포트하는 경로를 결정합니다(예: `import { MyObjectType } from "@ontology/sdk"`). 패키지 이름은 아무것이나 정할 수 있지만 `ontology`가 기본 관례입니다.

리소스 임포트를 바꾼 뒤 SDK를 다시 생성하려면 다음을 실행합니다.

```bash
./rune sdk generate
```

리포지토리에 `./rune`이 없다면 `.palantir-scripts/install-rune`을 실행해 설치합니다.

**설명**: 세 명령의 순서는 (1) `env prepare`로 개발 환경 준비, (2) 최초 1회 `--sdk-package-name`과 함께 생성, (3) 이후 임포트가 바뀔 때마다 이름 없이 재생성입니다. 패키지 이름을 `ontology`로 정하면 TypeScript에서는 `@ontology/sdk`라는 경로로 임포트하게 됩니다.

> **중간 요약**: VS Code 없이도 `./rune env prepare`와 `./rune sdk generate` 명령으로 로컬 SDK를 생성하고 갱신할 수 있으며, 처음 생성할 때 지정한 패키지 이름이 임포트 경로가 됩니다.

<a id="migrate-an-existing-repository-to-a-local-sdk"></a>
## 기존 리포지토리를 로컬 SDK로 마이그레이션하기 (Migrate an existing repository to a local SDK)

독립형(standalone) SDK를 쓰던 리포지토리를 로컬 SDK로 옮기려면 다음 단계를 따릅니다.

1. 리포지토리에서 `functions.json` 파일을 찾아 `useSdkSidebar`를 `false`로 설정합니다.

2. **Resources** 사이드 패널로 이동합니다. 위쪽의 **Migrate**를 선택해 로컬 SDK를 생성하고 자동 생성된 변경 사항을 커밋합니다. TypeScript v2에서는 `package.json`과 `package-lock.json` 파일이 갱신됩니다. Python에서는 `meta.yaml`과 `hawk.lock` 파일이 갱신됩니다.

![로컬 SDK로 마이그레이션하는 버튼을 보여 주는 Resources 사이드 패널.](https://www.palantir.com/docs/resources/foundry/functions/local-sdk-migrate-popover.png)

**설명**: `package.json`과 `meta.yaml`은 각각 TypeScript(npm)와 Python(conda 계열) 프로젝트의 의존성 목록 파일이고, `package-lock.json`과 `hawk.lock`은 실제로 설치된 정확한 버전을 기록하는 잠금(lock) 파일입니다. 마이그레이션은 이 파일들에서 독립형 SDK 패키지에 대한 의존을 로컬 SDK로 바꾸는 작업입니다.

## 정리

- 로컬 온톨로지 SDK는 TypeScript v2와 Python 함수에서 리소스 임포트로부터 OSDK를 자동 생성하는 방식으로, SDK 타입이 항상 최신 임포트 상태와 일치합니다.
- Global Branching을 완전히 지원하려면 로컬 SDK가 필요합니다.
- **Resources** 사이드 패널에서 온톨로지와 엔터티를 고르면 SDK가 갱신되며, 태그 시점의 온톨로지 상태로 SDK가 함수 버전에 묶입니다.
- VS Code 밖에서는 `./rune sdk generate` 명령으로 생성하고, 기존 리포지토리는 `useSdkSidebar`를 `false`로 바꾼 뒤 **Migrate**로 옮깁니다.
