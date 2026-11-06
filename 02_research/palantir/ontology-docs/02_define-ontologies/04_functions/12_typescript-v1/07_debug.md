# 함수 디버깅하기 (Debug functions)

- 원문: https://www.palantir.com/docs/foundry/functions/debug/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v1 > Debug functions

이 페이지는 TypeScript v1 함수(function)를 작성하면서 실행 상태를 들여다보는 두 가지 방법, 즉 Code Repositories의 디버거와 콘솔 로그를 설명합니다. 디버거로는 원하는 줄에서 실행을 멈추고 변수 값을 확인할 수 있고, 콘솔 로그로는 실행 중에 원하는 값을 출력해 테스트 결과나 라이브 미리보기 화면에서 볼 수 있습니다.

**팁**: 다음 문서는 TypeScript v1 함수에만 해당합니다. 온톨로지 SDK 지원, 설정 가능한 리소스 요청 등 [더 강력한 기능](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 쓰려면 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)하는 것을 권장합니다.

함수를 작성하다 보면 코드의 정확성이나 성능 문제를 고치기 위해 실행 상태를 살펴봐야 할 때가 많습니다. 아래는 이를 위해 사용할 수 있는 기능입니다. 이 디버깅 단계는 [단위 테스트](../16_unit-testing-tsv1/01_unit-test-getting-started.md)에도 똑같이 적용됩니다.

<a id="authoring-debugger"></a>
## 작성용 디버거 (Authoring debugger)

Code Repositories의 디버거 도구를 사용해 단위 테스트가 실행되는 동안 그 동작을 살펴볼 수 있습니다. 중단점(breakpoint)을 설정해 단위 테스트 실행을 일시 정지하고, 변수를 살펴보고, 함수와 라이브러리의 동작을 이해할 수 있습니다.

![디버거 개요 패널.](https://www.palantir.com/docs/resources/foundry/functions/debugger-overview.png)

<a id="set-breakpoints"></a>
## 중단점 설정하기 (Set breakpoints)

디버거를 사용하려면 중단점을 설정해야 합니다. 중단점은 디버거가 코드 실행을 멈춰야 하는 지점을 나타내며, 그 지점에서 변수와 상호 작용할 수 있게 해 줍니다.

각 코드 줄 옆 여백의 흐릿한 빨간 점을 선택해 중단점을 설정합니다. 디버거는 표시한 줄이 실행되기 *전에* 실행을 일시 중단합니다. 필요하다면 여러 파일에 걸쳐 중단점을 여러 개 설정할 수 있습니다.

![디버거 중단점.](https://www.palantir.com/docs/resources/foundry/functions/debugger-breakpoint.png)

**설명**: 예를 들어 `return employee.firstName + " " + employee.lastName;` 줄에 중단점을 걸면, 이 줄이 실행되기 직전에 멈추므로 `employee` 객체의 두 속성 값이 실제로 무엇인지 확인한 다음 실행을 이어 갈 수 있습니다. `print`문을 여기저기 넣고 다시 실행하는 것보다 한 번의 실행으로 더 많은 상태를 볼 수 있습니다.

<a id="run-the-debugger"></a>
## 디버거 실행하기 (Run the debugger)

<a id="during-live-preview"></a>
### 라이브 미리보기 중 (During live preview)

코드에 중단점을 추가한 뒤 functions 패널에 있는 **Run and debug**를 선택합니다.

![라이브 미리보기 디버거 레이아웃.](https://www.palantir.com/docs/resources/foundry/functions/live-preview-debugger-run.png)

<a id="during-testing"></a>
### 테스트 중 (During testing)

코드에 중단점을 추가한 뒤 코드 에디터에서 단위 테스트 옆에 있는 **Run test**를 선택합니다.

![테스트 디버거 레이아웃.](https://www.palantir.com/docs/resources/foundry/functions/test-debugger-run.png)

<a id="use-the-debugger"></a>
## 디버거 사용하기 (Use the debugger)

디버거가 시작되면 디버거 패널이 열리고 처음 만나는 중단점에서 일시 정지합니다. 디버거 왼쪽 막대에서 코드를 탐색하고, 중단점을 제거하고, 디버깅 세션을 마치거나 중지할 수 있습니다.

코드를 탐색하는 동안 에디터는 다음에 실행될 코드 줄을 강조 표시합니다. 다음 버튼으로 디버거를 진행합니다.

![디버거 컨트롤.](https://www.palantir.com/docs/resources/foundry/functions/debugger-controls.png)

1. **Resume execution(실행 재개):** 실행이 끝나거나 다음 중단점에서 멈출 때까지 실행을 계속합니다.
2. **Step over(한 줄 실행):** 내부 함수 안으로 들어가지 않고 코드 줄을 실행합니다.
3. **Step into(안으로 들어가기):** 해당 코드 줄에 내부 함수가 있으면 그 안으로 들어갑니다.
4. **Step out(밖으로 나가기):** 내부 함수에서 빠져나와 디버거를 진행합니다.
5. **Stop execution(실행 중지):** 디버거를 완전히 중지합니다.
6. **Remove breakpoints(중단점 제거):** 리포지토리의 모든 중단점을 제거하고 실행을 멈추지 않은 채 단위 테스트를 실행합니다.
7. **Settings(설정):** 중단점을 지우지 않고 디버거를 켜거나 끕니다.
8. **Documentation(문서):** 추가 정보를 위한 문서를 엽니다.

**설명**: Step over와 Step into의 차이는 현재 줄이 `const total = computeTotal(items);`처럼 다른 함수를 호출할 때 드러납니다. Step over는 `computeTotal` 전체를 한 번에 실행하고 다음 줄로 넘어가고, Step into는 `computeTotal` 함수의 첫 줄로 들어가서 멈춥니다. Step out은 그렇게 들어간 함수의 나머지를 실행하고 호출한 곳으로 돌아옵니다.

> **중간 요약**: 코드 줄 옆 빨간 점으로 중단점을 걸고, 라이브 미리보기에서는 **Run and debug**, 테스트에서는 **Run test**로 디버거를 실행합니다. 멈춘 뒤에는 재개, 한 줄 실행, 들어가기, 나가기, 중지 버튼으로 실행을 조절합니다.

<a id="examine-variables"></a>
## 변수 살펴보기 (Examine variables)

디버거가 실행되는 동안 코드 실행이 멈춘 바로 그 지점의 변수와 데이터를 살펴볼 수 있습니다.

<a id="frames"></a>
### 프레임 (Frames)

프레임은 디버거가 활성화되어 있거나 중단점이 있는 함수를 나타냅니다. 각 프레임에는 함수 이름과 그 함수가 작성된 파일 이름과 줄 번호가 표시됩니다.

프레임을 선택하면 그 프레임 안의 변수를 살펴보고 그 프레임을 대상으로 콘솔 명령을 실행할 수 있습니다.

**설명**: 프레임은 호출 스택(call stack)의 한 칸입니다. `getFullName`이 `formatName`을 호출한 상태에서 멈췄다면 스택에는 `formatName` 프레임과 그 아래 `getFullName` 프레임이 쌓여 있고, 각 프레임은 자기 함수의 지역 변수를 따로 가집니다.

<a id="variables"></a>
### 변수 (Variables)

변수 섹션은 변환(transform)이 실행되는 동안 지역 변수와 전역 변수에 저장된 값을 표시합니다.

![디버거 변수.](https://www.palantir.com/docs/resources/foundry/functions/debugger-variables.png)

<a id="console"></a>
### 콘솔 (Console)

콘솔을 사용하면 디버거가 실행되는 동안 JavaScript 콘솔 명령으로 데이터와 상호 작용할 수 있습니다. 콘솔은 선택한 프레임의 컨텍스트에서 동작하므로, 다른 프레임의 지역 변수에 대해 명령을 실행하려고 하면 오류가 납니다.

![디버거 콘솔.](https://www.palantir.com/docs/resources/foundry/functions/debugger-console.png)

> **중간 요약**: 멈춘 상태에서 프레임을 골라 그 함수의 지역 변수와 전역 변수를 확인하고, 콘솔에서 선택한 프레임의 변수를 대상으로 JavaScript 명령을 실행할 수 있습니다.

<a id="console-logging"></a>
## 콘솔 로깅 (Console logging)

Functions는 디버깅을 위해 실행 중에 콘솔 로그를 내보내는 기능을 지원합니다. `console.log` 명령으로 로그를 내보내기만 하면 됩니다. 예를 들면 다음과 같습니다.

```typescript
    @Function()
    public testConsoleLogging(n: Integer): Integer {
        for (let i = 0; i < n; i++) {
            console.log(`Iteration ${i}`);
        }
        return n;
    }
```

**설명**: 정수 `n`을 받아 `n`번 반복하면서 매번 `Iteration 0`, `Iteration 1`, ... 같은 로그를 출력하고 `n`을 그대로 반환합니다. `n`이 3이면 로그 3줄이 출력되고 반환값은 3입니다. 이 로그는 아래 설명처럼 테스트 결과나 라이브 미리보기 화면에 표시됩니다.

이렇게 콘솔 로그를 사용하면 정확성 문제를 디버깅하는 데 도움이 됩니다. 코드의 성능 병목을 찾기 위해 콘솔 로그를 추가할 수도 있습니다. 링크 탐색 로직의 성능을 개선하는 방법은 [성능 최적화](../08_function-consumption/03_optimize-performance.md) 가이드를 참고하세요.

<a id="during-testing"></a>
### 테스트 중 (During testing)

**Authoring**에서 **Tests** 도우미로 함수를 실행하면 콘솔 로그가 수집되어 아래에 표시됩니다.

![테스트의 콘솔 로깅.](https://www.palantir.com/docs/resources/foundry/functions/console-logging-tests.png)

<a id="during-live-preview"></a>
### 라이브 미리보기 중 (During live preview)

**Authoring**에서 **Functions** 도우미로 함수를 실행하면 콘솔 로그가 수집되어 타임스탬프와 함께 아래에 표시됩니다.

![라이브 미리보기의 콘솔 로깅.](https://www.palantir.com/docs/resources/foundry/functions/console-logging-live-preview.png)

**설명**: 라이브 미리보기의 로그에는 타임스탬프가 붙으므로, 두 로그 사이의 시간 차이를 보고 어느 구간(예: 링크 탐색)이 오래 걸리는지 확인할 수 있습니다.

> **중간 요약**: `console.log`로 출력한 로그는 **Tests** 도우미에서는 테스트 결과 아래에, **Functions** 도우미의 라이브 미리보기에서는 타임스탬프와 함께 표시되어 정확성과 성능 문제를 찾는 데 쓰입니다.

## 정리

- TypeScript v1 함수는 Code Repositories의 디버거로 디버깅할 수 있으며, 같은 방법이 단위 테스트에도 적용됩니다.
- 코드 줄 옆에 중단점을 걸고 라이브 미리보기의 **Run and debug**나 테스트의 **Run test**로 디버거를 시작합니다.
- 실행 재개, Step over, Step into, Step out 등의 버튼으로 실행을 진행하고, 프레임, 변수, 콘솔에서 멈춘 지점의 상태를 확인합니다.
- `console.log`로 남긴 로그는 테스트 결과와 라이브 미리보기(타임스탬프 포함)에 표시되어 정확성과 성능 문제를 찾는 데 도움이 됩니다.
