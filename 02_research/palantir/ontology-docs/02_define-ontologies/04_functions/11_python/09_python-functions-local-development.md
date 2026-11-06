# Python 함수 로컬 개발 (Local development)

- 원문: https://www.palantir.com/docs/foundry/functions/python-functions-local-development/
- 사이드바 위치: Define Ontologies > Functions > Python > Local development

이 페이지는 Foundry의 웹 기반 Code Repositories 대신 자신의 컴퓨터에서 Python 함수(function) 저장소를 개발하는 방법을 설명합니다. 저장소를 git으로 복제하는 절차, Java와 환경 변수 같은 사전 준비, 그리고 Visual Studio Code와 PyCharm에서 Python 인터프리터를 설정하는 방법을 다룹니다.

Python 함수 저장소를 로컬에서 개발할 수 있으며, 이를 통해 직접 꾸민 환경에서 빠르게 반복 작업을 할 수 있습니다.

<a id="setting-up-local-development-for-python-functions-repositories"></a>
## Python 함수 저장소의 로컬 개발 설정 (Setting up local development for Python functions repositories)

<a id="clone-the-repository"></a>
### 저장소 복제하기 (Clone the repository)

1. 저장소의 메뉴 바에서 **Work locally**를 선택해 대화 상자를 열고, 표시된 저장소 URL을 복사합니다. <br><br>
   ![오른쪽에 "Work locally" 옵션이 있는 저장소 상단 메뉴 바.](https://www.palantir.com/docs/resources/foundry/functions/clone-repo.png) <br><br>
   ![“Work locally” 대화 상자.](https://www.palantir.com/docs/resources/foundry/functions/work-locally-dialog.png) <br><br>

2. 로컬 컴퓨터의 원하는 디렉터리에서 명령줄로 `git clone <URI>`를 실행합니다. 그런 다음 `cd` 명령으로 저장소 디렉터리로 이동합니다.

**설명**: Foundry의 코드 저장소는 내부적으로 git 저장소이므로, 표준 git 명령으로 복제(clone), 커밋(commit), 푸시(push)를 할 수 있습니다. 복사한 URL에는 인증용 토큰이 포함되어 있습니다.

<a id="limitations"></a>
### 제한 사항 (Limitations)

* 복제를 위해 발급되는 토큰은 수명이 짧고 읽기 전용입니다. 단, 저장소로 다시 푸시하는 것은 예외로 허용됩니다.
* 아티팩트를 게시하거나 체크(checks) 또는 빌드를 실행하려면 여전히 변경 사항을 Foundry로 푸시해야 합니다.

> **중간 요약**: Work locally 대화 상자의 URL로 `git clone`해 로컬에서 작업할 수 있지만, 게시와 체크, 빌드는 Foundry에 푸시해야 실행됩니다.

<a id="set-up-the-development-environment"></a>
## 개발 환경 설정 (Set up the development environment)

<a id="prerequisites"></a>
### 사전 요구 사항 (Prerequisites)

* Java 21이 설치되어 있고 환경 변수 `JAVA_HOME`이 올바른 Java 설치 경로를 가리키는지 확인합니다. Java 21은 [Oracle 웹사이트 ↗](https://www.oracle.com/java/technologies/downloads/#java21)에서 내려받을 수 있습니다.

**참고**: 운영 체제별로 `JAVA_HOME` 환경 변수를 설정하는 방법은 다음과 같습니다.

* Windows: PowerShell에서 `SETX JAVA_HOME -m "<java-home-dir>"`을 실행합니다. 이 명령은 시스템 환경 변수를 수정하며, 변경 사항을 적용하려면 셸을 다시 시작해야 합니다. 또는 ` [System.Environment]::SetEnvironmentVariable("JAVA_HOME", "<java-home-dir>")`을 실행해 실행 중인 프로세스에서 `JAVA_HOME`을 설정할 수도 있습니다.
* Linux 또는 macOS: `export JAVA_HOME=<java-home-dir>`을 실행합니다.

* [여기](https://www.palantir.com/docs/foundry/code-repositories/repository-upgrades/#manual-branch-upgrade)에 설명된 단계에 따라 저장소가 최신 템플릿 버전으로 업그레이드되어 있는지 확인합니다.
* 환경 변수 `CI`, `JEMMA`, `CA`가 설정되어 있지 않은지 확인합니다.
* Apple silicon Mac에서 실행하는 경우 [Rosetta 2 ↗](https://developer.apple.com/documentation/apple-silicon/about-the-rosetta-translation-environment)가 설치되어 있는지 확인합니다. 터미널에서 `/usr/sbin/softwareupdate --install-rosetta --agree-to-license`를 실행해 Rosetta 2를 설치할 수 있습니다.

**설명**: Python 함수 저장소인데 Java가 필요한 이유는 빌드 도구로 Gradle(`./gradlew`)을 쓰기 때문입니다. Gradle은 JVM 위에서 실행되며, 이 Gradle 작업들이 Conda로 Python 환경을 만들어 줍니다. `CI`, `JEMMA`, `CA` 같은 환경 변수는 빌드 스크립트가 "Foundry 안의 빌드 서버에서 실행 중"이라고 판단하는 데 쓰일 수 있으므로 로컬에서는 비워 두어야 합니다.

**주의**: 템플릿 버전 오류(Template version error). `./gradlew` 명령이 다음과 비슷한 오류로 실패하면 저장소가 오래된 템플릿 버전에 있는 것입니다.

```
A problem occurred evaluating project ':transforms-python'.
> Failed to apply plugin class 'com.palantir.transforms.lang.python.gradle.ModelTrainingPlugin'.
   > Could not create task ':transforms-python:createCondaPackLayer'.
      > Task with name 'condaPackRun' not found in project ':transforms-python'.
```

이 오류를 해결하려면 위에서 설명한 대로 저장소를 최신 템플릿 버전으로 업그레이드하세요.

> **중간 요약**: 로컬 개발에는 Java 21과 `JAVA_HOME` 설정, 최신 템플릿 버전, `CI`/`JEMMA`/`CA` 환경 변수 해제, (Apple silicon이면) Rosetta 2가 필요합니다.

<a id="visual-studio-code"></a>
## Visual Studio Code

* [Visual Studio Code ↗](https://code.visualstudio.com/)가 설치되어 있는지 확인합니다.
* Visual Studio Code 사이트나 애플리케이션의 **Extensions** 탭에서 [Python 확장 ↗](https://marketplace.visualstudio.com/items?itemName=ms-python.python)을 설치합니다.
* Visual Studio Code용 Python 인터프리터를 구성하는 설정 파일을 자동으로 생성하려면 `./gradlew vsCode` 명령을 실행합니다.

<a id="pycharm"></a>
## PyCharm

* Python 개발 환경을 설정하려면 `./gradlew condaDevelop` 명령을 실행합니다.

* 로컬에 [JetBrains PyCharm ↗](https://www.jetbrains.com/pycharm/)이 설치되어 있는지 확인합니다.

* [여기 ↗](https://www.jetbrains.com/help/pycharm/open-projects.html)에 설명된 단계에 따라 프로젝트를 가져옵니다.

* 상태 표시줄의 [Python Interpreter 선택기 ↗](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#widget)에서 **Add New Interpreter**를 선택합니다. <br><br>
  ![Python 인터프리터 추가 화면](https://www.palantir.com/docs/resources/foundry/functions/pycharm-add-python-interpreter.png) <br><br>

* **Add Python Interpreter** 대화 상자의 왼쪽 창에서 **Virtualenv Environment**를 선택합니다. <br><br>
  ![Python 인터프리터 구성 화면](https://www.palantir.com/docs/resources/foundry/functions/pycharm-configure-python-interpreter.png) <br><br>

* **Existing environment**를 선택하고 **Interpreter** 필드를 Conda 환경의 Python 인터프리터로 설정합니다.
  * Unix에서 Python 인터프리터 경로는 <code>\<your-conda-environment-dir>/bin/python</code>입니다.<br/>
  * Windows에서 Python 인터프리터 경로는 <code>\<your-conda-environment-dir>\python.exe</code>입니다.

**팁**: 테스트 플러그인의 활성화 여부에 따라, 설치되는 환경에는 `./python-functions/build/conda/run-env`, `./python-functions/build/conda/test-env` 또는 둘 다가 포함됩니다. 테스트를 실행할 계획이라면 테스트 환경을 선택해야 합니다.

* **Ok**를 선택합니다.

**설명**: 인터프리터를 Conda 환경으로 지정해야 하는 이유는, 그 환경에 저장소가 의존하는 라이브러리(예: `functions.api`, 생성된 `ontology_sdk`)가 설치되어 있기 때문입니다. 시스템 기본 Python을 지정하면 IDE가 `import` 문을 해석하지 못해 자동 완성과 오류 표시가 동작하지 않습니다.

> **중간 요약**: VS Code는 Python 확장 설치 후 `./gradlew vsCode`로, PyCharm은 `./gradlew condaDevelop`로 만든 Conda 환경을 기존 인터프리터로 지정해 설정합니다.

## 정리

- Work locally에서 복사한 URL로 `git clone`하면 Python 함수 저장소를 로컬에서 개발할 수 있습니다.
- 복제 토큰은 짧은 수명의 읽기 전용(푸시만 예외)이며, 게시와 체크, 빌드는 Foundry로 푸시해야 합니다.
- Java 21과 `JAVA_HOME`, 최신 템플릿, 특정 환경 변수 해제, Apple silicon의 Rosetta 2가 사전 요구 사항입니다.
- 템플릿이 오래되면 `./gradlew` 실행 시 `condaPackRun` 관련 오류가 나므로 업그레이드합니다.
- VS Code는 `./gradlew vsCode`, PyCharm은 `./gradlew condaDevelop` 후 Conda 인터프리터 지정으로 설정합니다.
