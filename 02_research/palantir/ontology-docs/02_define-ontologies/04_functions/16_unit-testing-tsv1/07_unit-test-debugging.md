# 디버그 (Debug)

- 원문: https://www.palantir.com/docs/foundry/functions/unit-test-debugging/
- 사이드바 위치: Define Ontologies > Functions > Unit testing (TSv1) > Debug

이 페이지는 TypeScript v1 함수(function)의 단위 테스트를 실행하는 도중에 Code Repositories의 디버거로 동작을 들여다보는 방법을 짧게 안내합니다. 자세한 사용법은 함수 디버깅 문서로 연결됩니다.

Code Repositories의 디버거 도구를 사용하면 단위 테스트가 실행되는 동안 그 동작을 살펴볼 수 있습니다. 중단점(breakpoint)을 설정해 단위 테스트 실행을 일시 정지하면 변수를 확인하고, 함수와 라이브러리를 이해할 수 있습니다.

![디버거 개요 패널.](https://www.palantir.com/docs/resources/foundry/functions/debugger-overview.png)

[중단점 설정](../12_typescript-v1/07_debug.md#set-breakpoints), [디버거 실행](../12_typescript-v1/07_debug.md#run-the-debugger), [변수 확인](../12_typescript-v1/07_debug.md#examine-variables)에 대한 자세한 내용은 [함수 디버깅 문서](../12_typescript-v1/07_debug.md)를 참고하세요.

**설명**: 중단점은 코드의 특정 줄에 걸어 두는 표시로, 실행이 그 줄에 도달하면 프로그램이 멈춥니다. 멈춘 상태에서 그 시점의 지역 변수 값과 호출 스택을 확인한 뒤 한 줄씩 실행을 이어 갈 수 있습니다. 테스트가 기대와 다른 값을 낼 때 어느 줄에서 값이 달라지는지 찾는 데 씁니다.

## 정리

- Code Repositories의 디버거로 단위 테스트 실행을 중단점에서 멈추고 변수를 확인할 수 있습니다.
- 중단점 설정, 디버거 실행, 변수 확인의 자세한 절차는 TypeScript v1 함수 디버깅 문서에 있습니다.
