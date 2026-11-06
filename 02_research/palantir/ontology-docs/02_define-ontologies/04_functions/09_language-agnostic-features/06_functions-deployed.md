# 함수 배포하기 (Deploy functions)

- 원문: https://www.palantir.com/docs/foundry/functions/functions-deployed/
- 사이드바 위치: Define Ontologies > Functions > Language-agnostic features > Deploy functions

이 페이지는 함수(function)를 실행하는 두 가지 방식인 서버리스(serverless) 모드와 배포(deployed) 모드의 차이를 설명하고, 함수를 배포 모드로 구성해 실행하는 절차를 단계별로 안내합니다. 어떤 경우에 배포 모드가 필요한지(GPU, 서드파티 클라이언트, 로컬 캐싱 등)와 그 대가(상시 비용, 단일 버전 실행)를 판단하는 데 필요한 내용입니다.

**설명**: 서버리스 모드는 요청이 들어올 때만 실행 자원을 할당해 함수를 실행하고, 끝나면 자원을 반납하는 방식입니다. 배포 모드는 컨테이너(함수 실행에 필요한 프로그램과 라이브러리를 묶은 격리된 실행 환경)를 계속 띄워 두고 요청을 받는 방식으로, 웹 서버 프로세스를 상시 실행해 두는 것과 같은 구조입니다.

<a id="prerequisites"></a>
## 사전 요구 사항 (Prerequisites)

이 가이드는 Python 또는 TypeScript v2 함수를 이미 작성하고 게시했다고 가정합니다. 튜토리얼은 [Python 함수 시작하기](../11_python/01_python-getting-started.md) 또는 [TypeScript v2 함수 시작하기](../10_typescript-v2/01_typescript-v2-getting-started.md) 문서를 참조하십시오.

<a id="choose-between-deployed-and-serverless-execution-modes"></a>
## 배포 실행 모드와 서버리스 실행 모드 중에서 선택하기 (Choose between deployed and serverless execution modes)

등록 환경(enrollment)에서 서버리스 함수가 활성화되어 있다면, 새 저장소는 기본적으로 서버리스를 사용합니다. 대부분의 사용 사례에는 일반적으로 서버리스 함수를 권장합니다. 배포된 함수가 유용한 경우도 있지만, 서버리스 실행 모드는 유지 관리가 덜 필요하고 오래 실행되는 배포에 따르는 비용을 발생시키지 않습니다.

배포된 함수에는 서버리스 함수에서 사용할 수 없는 몇 가지 기능이 있습니다.

* 배포된 함수는 오래 실행되므로, 함수가 재시작을 견딜 수 있다면 로컬 캐싱이 가능할 수 있습니다.
* 서버리스 함수는 제공된 소스 객체의 클라이언트를 사용하는 [외부 소스](04_api-calls.md)는 지원하지만 서드파티 클라이언트는 지원하지 않습니다. 서드파티 클라이언트로 외부 API를 호출하려면 함수를 배포해야 합니다.
* 배포된 함수는 병렬 처리를 통해 계산량이 많은 모델 학습과 추론 워크플로를 가속하는 GPU 할당을 지원하지만, 서버리스 함수는 지원하지 않습니다.
* 배포된 함수는 전체 서비스 디스커버리(service discovery) API에 접근할 수 있지만, 서버리스 함수는 `api_gateway`, `telemetry` 같은 제한된 서비스 디스커버리 API 부분집합에만 접근할 수 있습니다.

배포된 함수에는 서버리스 실행에는 해당하지 않는 몇 가지 제한이 있습니다.

* 서버리스 함수는 하나의 함수의 서로 다른 버전을 필요할 때마다 실행할 수 있어 업그레이드가 더 안전합니다. 배포된 함수는 한 번에 하나의 함수 버전만 실행할 수 있습니다.
* 서버리스 함수는 실행될 때만 비용이 발생하지만, 배포된 함수는 배포가 실행되는 동안 계속 비용이 발생합니다.
* 서버리스 함수는 인프라가 자동으로 관리되므로 초기 설정과 장기 유지 관리가 덜 필요합니다.

등록 환경에서 서버리스 함수를 활성화하려면 Palantir 관리자에게 문의하십시오.

**설명**: 로컬 캐싱은 계산 결과나 불러온 데이터를 프로세스 메모리에 보관해 다음 요청에서 다시 쓰는 기법입니다. 프로세스가 계속 살아 있는 배포 모드에서만 의미가 있으며, 재시작되면 캐시가 사라지므로 "재시작을 견딜 수 있다면"이라는 조건이 붙습니다. 서비스 디스커버리는 실행 중인 프로그램이 다른 내부 서비스의 주소를 찾아내는 기능입니다.

> **중간 요약**: 서버리스가 기본이자 권장 방식이며, 실행할 때만 비용이 들고 여러 버전을 동시에 실행할 수 있습니다. 로컬 캐싱, 서드파티 HTTP 클라이언트, GPU, 전체 서비스 디스커버리가 필요할 때만 배포 모드를 고려합니다.

<a id="architecture"></a>
## 아키텍처 (Architecture)

함수는 필요할 때 할당되는(on-demand) 자원을 활용하는 서버리스 모드로 실행하거나, 오래 실행되는 컨테이너에 배포할 수 있습니다.

**팁**: 등록 환경에서 서버리스 함수가 활성화되어 있다면 배포된 함수보다 서버리스 함수를 사용할 것을 권장합니다. [배포된 함수가 유용한 경우](#choose-between-deployed-and-serverless-execution-modes)도 일부 있지만, 서버리스 실행기(executor)가 일반적으로 더 유연합니다.

함수가 배포되면, 들어오는 실행 요청을 처리하기 위해 오래 실행되는 환경이 생성됩니다. 이 환경은 요청량에 따라 확장(scale)되며, 자동화된 프로세스에 의해 가끔 재시작됩니다. 하나의 저장소에 있는 모든 함수는 하나의 배포에서 호스팅됩니다.

함수의 실행 모드와 배포 구성은 함수가 Marketplace를 통해 배포될 때 패키징되어 그대로 재현됩니다. 자세한 내용과 제한 사항은 [Marketplace의 배포된 함수](../07_function-management/03_marketplace-functions.md#deployed-functions)를 참조하십시오.

**주의**: 컴퓨팅 비용(Compute costs). 배포된 함수는 실행 중인 배포에 대해 컴퓨팅 비용이 발생합니다. 서버리스 함수는 실행될 때만 비용이 발생합니다.

<a id="deploy-a-function"></a>
## 함수 배포하기 (Deploy a function)

다음 단계에 따라 함수를 구성하고 배포합니다.

1. 함수 저장소를 열고 **Branches** 탭으로 이동한 다음 **Tags and releases**를 선택합니다.
2. 배포할 함수 위에 마우스를 올린 다음 **Open in Ontology Manager**를 선택합니다.

![선택한 함수를 Ontology Manager에서 열기.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-open-ontology-manager-v2.png)

3. 왼쪽의 버전 선택기에서 사용할 함수 버전을 선택합니다.
4. **Configure execution**(실행 구성)을 선택합니다.

![함수의 실행 구성하기.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-configure-execution.png)

5. 환경에서 서버리스 함수가 활성화되어 있다면 서버리스와 배포 모드를 전환하는 옵션이 보입니다. 아무것도 선택하지 않았고 배포가 없다면 기본적으로 서버리스가 사용됩니다.

![서버리스 모드인 함수의 설정.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-serverless-mode-configuration.png)

6. **Deployed** 실행 모드 옵션을 선택합니다.

7. 함수에 대한 배포가 없다면 **Create deployment**(배포 만들기)를 선택합니다.

![기존 배포가 없는 배포 모드 함수의 설정.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-create-deployment.png)

8. 배포를 처음 만들 때는 구성에 기본값이 적용됩니다. 페이지 끝까지 스크롤하면 전체 구성을 볼 수 있습니다.

![배포 모드인 함수의 설정.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-deployed-mode-configuration.png)

9. 필요에 따라 배포 구성을 수정합니다. 다음 항목을 구성할 수 있습니다.
   * CPU, GPU, 메모리를 포함해 배포에 할당되는 컴퓨팅 자원.
   * 요청 부하에 따른 자동 확장(autoscaling)의 최소 한도와 최대 한도.
   * 배포가 시작될 때 설정될 환경 변수.
   * 함수가 타임아웃 오류를 반환하기 전까지 실행될 수 있는 총 시간. 다른 배포 설정과 달리 타임아웃은 함수 버전마다 개별적으로 구성됩니다.

![배포 모드인 함수의 메모리 할당 수정하기.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-modify-deployment-memory-allocation.png)

10. **Save and start deployment**를 선택하면 변경 사항을 저장하고 배포를 시작합니다. 배포를 시작하지 않고 구성만 저장하려면 **Save without starting deployment**를 선택할 수도 있습니다.

![배포 모드인 함수의 배포 저장 및 시작.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-save-and-start-deployment.png)

11. **Save and start deployment**를 선택했다면, 함수를 호스팅하는 배포가 시작될 때까지 기다려야 합니다. 몇 분 정도 걸릴 수 있습니다.

12. 배포가 실행 중인지 확인하려면 함수가 들어 있는 코드 저장소로 이동해 함수를 실행합니다. 함수가 성공적으로 실행되어 예상한 결과를 반환해야 합니다.

![배포 모드로 함수 실행하기.](https://www.palantir.com/docs/resources/foundry/functions/python-functions-run-deployed-function.png)

**설명**: 자동 확장은 요청이 많아지면 같은 컨테이너를 여러 개(인스턴스)로 늘리고, 줄어들면 다시 줄이는 기능입니다. 예를 들어 최소 1, 최대 3으로 설정하면 평소에는 컨테이너 1개가 실행되다가 부하가 높아지면 최대 3개까지 늘어납니다. 최소 한도만큼은 항상 실행되므로 그만큼 비용이 계속 발생합니다.

> **중간 요약**: 배포는 Ontology Manager에서 함수 버전을 고르고 **Configure execution**에서 **Deployed** 모드를 선택해 진행합니다. 자원(CPU, GPU, 메모리), 자동 확장 범위, 환경 변수, 버전별 타임아웃을 설정한 뒤 배포를 시작하고, 함수를 실행해 동작을 확인합니다.

## 정리

- 함수는 요청 시에만 자원을 쓰는 서버리스 모드나, 상시 실행 컨테이너를 쓰는 배포 모드로 실행할 수 있으며, 서버리스가 기본이자 권장 방식입니다.
- 배포 모드는 로컬 캐싱, 서드파티 HTTP 클라이언트, GPU, 전체 서비스 디스커버리가 필요할 때 씁니다.
- 배포 모드는 실행 중 내내 비용이 들고 한 번에 한 버전만 실행할 수 있으며, 한 저장소의 모든 함수가 하나의 배포에서 호스팅됩니다.
- 배포는 Ontology Manager의 **Configure execution**에서 구성하며, 자원, 자동 확장, 환경 변수, 타임아웃을 설정할 수 있습니다.
