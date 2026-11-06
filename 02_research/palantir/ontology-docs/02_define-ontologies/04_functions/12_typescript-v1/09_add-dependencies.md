# npm 의존성 추가하기 (Add NPM dependencies)

- 원문: https://www.palantir.com/docs/foundry/functions/add-dependencies/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v1 > Add NPM dependencies

TypeScript 함수를 작성하다 보면 날짜 계산, 통계, XML 처리처럼 이미 만들어진 외부 라이브러리를 쓰고 싶을 때가 많습니다. 이 페이지는 TypeScript v1 함수 저장소에 npm 패키지를 의존성으로 추가하는 방법(공개 npm 레지스트리 활성화, Libraries 사이드바로 추가, `package.json` 직접 수정)과, 함수 런타임에서 쓸 수 있는 패키지의 조건을 설명합니다.

**팁**: 아래 문서는 TypeScript v1 함수에만 해당합니다. Ontology SDK 지원과 구성 가능한 리소스 요청 등 [더 강력한 기능](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 위해 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)할 것을 권장합니다.

함수 저장소는 의존성 관리에 [npm ↗](https://www.npmjs.com/)을 사용하며, 여기에는 Foundry 온톨로지를 기반으로 코드를 생성하는 패키지와 코드에서 함수를 찾아내는 패키지도 포함됩니다. `npm`을 사용해 외부 의존성을 저장소에 설치할 수 있으며, 숫자와 날짜 다루기, 통계 계산, XML 같은 데이터 형식 처리 등을 위한 표준 패키지를 쓸 수 있습니다.

함수 런타임은 순수 JavaScript 라이브러리만 지원합니다. NodeJS 런타임에 의존하고 시스템 호출(system call)을 하는 패키지는 지원되지 않습니다.

**설명**: npm은 JavaScript/TypeScript 생태계의 패키지 관리자이고, 프로젝트가 쓰는 패키지 목록은 `package.json`에, 실제로 설치된 정확한 버전은 `package-lock.json`에 기록됩니다. "순수 JavaScript 라이브러리만 지원"한다는 것은 언어 자체의 기능(계산, 문자열과 배열 처리 등)만 쓰는 패키지는 되지만, `fs`(파일 시스템), `child_process`(프로세스 실행), `net`(소켓) 같은 Node.js 전용 모듈을 통해 운영체제 기능을 호출하는 패키지는 안 된다는 뜻입니다. 예를 들어 날짜 계산 라이브러리는 대개 쓸 수 있지만, 로컬 파일을 읽고 쓰는 라이브러리는 쓸 수 없습니다.

<a id="enable-fetching-dependencies-from-the-public-npm-registry"></a>
## 공개 npm 레지스트리에서 의존성 가져오기 활성화 (Enable fetching dependencies from the public npm registry)

기본적으로 함수 저장소는 공개 npm 레지스트리에서 패키지를 가져오지 않습니다.

저장소가 아직 공개 npm 레지스트리에서 의존성을 가져오지 않는 상태라면, Code Repositories에서 `package.json` 파일을 열 때 이를 활성화하는 배너가 나타납니다.

![Code Repositories에서 외부 npm 활성화.](https://www.palantir.com/docs/resources/foundry/functions/external-npm.png)

<a id="add-dependencies-in-code-repositories"></a>
## Code Repositories에서 의존성 추가하기 (Add dependencies in Code Repositories)

**Code Repositories**의 Libraries(라이브러리) 사이드바를 사용해 함수 저장소에 패키지를 추가할 수 있습니다. 원하는 패키지를 검색하고 결과를 선택하면 최신 버전 같은 세부 정보를 볼 수 있습니다. 결과에는 Foundry의 패키지와 <https://npmjs.com>의 패키지가 포함됩니다.

![Code Repositories 사이드바에서 라이브러리 추가.](https://www.palantir.com/docs/resources/foundry/functions/npm-installation-controls.png)

`package.json` 파일의 `dependencies`와 `devDependencies` 중 어디에 패키지를 추가할지 고릅니다. **Add and install library**를 선택하면 저장소에 패키지가 추가됩니다.

![라이브러리를 추가하기 전에 라이브러리 의존성 변경 사항 확인.](https://www.palantir.com/docs/resources/foundry/functions/npm-backing-repositories.png)

패키지의 출처 저장소가 아직 백킹 저장소(backing repository)로 구성되어 있지 않으면, 추가 리소스를 가져오라는 대화상자가 나타납니다. **Add and install library** 버튼은 패키지와 그 의존 패키지를 함수 저장소로 자동으로 가져오고 `package.json`과 `package-lock.json`을 갱신합니다.

실행 중인 설치 작업이 끝나면 저장소에서 패키지를 사용할 준비가 됩니다.

`typescript-functions` 템플릿 버전이 0.520.0보다 낮다면 태스크 러너(task runner)를 통한 설치가 비활성화됩니다. 이 경우 갱신한 `package.json` 파일을 커밋하고, 검사(check)가 통과하는지 확인한 다음, Code Assist를 재시작해 새 패키지를 사용할 수 있게 하세요.

**설명**: `dependencies`는 코드가 실행될 때 필요한 패키지, `devDependencies`는 개발과 빌드 단계에서만 필요한 패키지(타입 정의, 테스트 도구 등)입니다. 예를 들어 `d3-array`는 함수 실행 중에 호출되므로 `dependencies`에, 그 TypeScript 타입 정의인 `@types/d3-array`는 컴파일할 때만 필요하므로 `devDependencies`에 넣습니다. 백킹 저장소가 정확히 어떻게 동작하는지는 이 페이지에서 설명하지 않으며, 원문에서 알 수 있는 것은 패키지 출처가 아직 백킹 저장소로 구성되지 않았다면 추가 리소스를 가져오는 절차를 거친다는 점입니다.

> **중간 요약**: 함수 저장소는 기본적으로 공개 npm 레지스트리를 쓰지 않으므로 `package.json`을 열 때 나타나는 배너로 활성화합니다. Libraries 사이드바에서 패키지를 검색해 `dependencies` 또는 `devDependencies`를 고르고 Add and install library로 설치하며, 템플릿 버전이 0.520.0 미만이면 커밋 후 Code Assist를 재시작해야 합니다.

<a id="manually-add-dependencies"></a>
## 수동으로 의존성 추가하기 (Manually add dependencies)

Code Repositories에서 `package.json` 파일을 수정해 패키지를 수동으로 추가할 수 있습니다. 특정 버전의 패키지를 설치해야 할 때 유용합니다. `package.json`을 열고 <https://npmjs.com>에서 고른 적절한 버전으로 의존성을 추가한 뒤 **Commit**을 선택합니다. 검사가 통과하는 것을 확인한 다음, Code Assist를 재시작해 새 패키지를 사용할 수 있게 합니다.

![상태 표시줄에 마우스를 올리고 상태 기호를 선택해 Code Assist 재시작.](https://www.palantir.com/docs/resources/foundry/functions/restart-code-assist.png)

아래는 저장소의 `package.json` 파일에 `d3-array` 패키지를 수동으로 추가하는 예입니다.

```typescript
  "dependencies": {
    ...
    "d3-array": "^2.3.1"
  },
  "devDependencies": {
    ...
    "@types/d3-array": "^2.0.0"
  }
```

**설명**: `...`는 기존 항목을 생략한 표시입니다. `"d3-array": "^2.3.1"`은 실행 시 의존성으로 `d3-array`를 추가하고, `"@types/d3-array": "^2.0.0"`은 개발 의존성으로 그 타입 정의를 추가합니다. 버전 앞의 `^`는 npm의 시맨틱 버전 범위 표기로, `^2.3.1`은 "2.3.1 이상이면서 3.0.0 미만"을 뜻합니다. 즉 주(major) 버전 2 안에서 호환되는 최신 버전을 허용합니다.

## 정리

- TypeScript v1 함수 저장소는 npm으로 의존성을 관리하며, 함수 런타임은 시스템 호출을 하지 않는 순수 JavaScript 라이브러리만 지원합니다.
- 공개 npm 레지스트리 사용은 기본적으로 꺼져 있으며 `package.json`을 열 때 나타나는 배너로 켭니다.
- Libraries 사이드바에서 패키지를 검색해 `dependencies` 또는 `devDependencies`로 추가하면 `package.json`과 `package-lock.json`이 자동 갱신됩니다.
- 특정 버전이 필요하면 `package.json`을 직접 수정해 커밋하고, 검사 통과 후 Code Assist를 재시작합니다.
