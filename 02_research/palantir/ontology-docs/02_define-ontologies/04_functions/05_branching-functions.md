# 함수 브랜칭 (Branching functions)

- 원문: https://www.palantir.com/docs/foundry/functions/branching-functions/
- 사이드바 위치: Define Ontologies > Functions > Branching functions

이 페이지는 글로벌 브랜치(global branch)에서 함수(function)를 개발하고 게시하고 사용하는 방법을 다룹니다. 브랜치 위에서 함수를 바꾸면 `main`에서 운영 중인 Workshop 모듈이나 액션에 영향을 주지 않고 변경을 시험할 수 있습니다. 버전 타깃(version target), 리베이스, 병합 시 어떤 버전이 `main`에 남는지가 핵심입니다.

글로벌 브랜치에서 함수를 개발하고, 게시하고, 사용할 수 있습니다. 현재 이 기능은 TypeScript v1, TypeScript v2, Python, AIP Logic, 그리고 직접 모델 배포(direct model deployment)용 모델 함수에서 지원됩니다.

**설명**: Git 브랜치는 코드 저장소 하나 안에서만 변경을 분리합니다. Foundry의 글로벌 브랜치는 이를 넓혀, 온톨로지 정의, 함수, Workshop 모듈처럼 여러 애플리케이션에 걸친 관련 변경을 하나의 브랜치로 묶습니다. 브랜치에서 만든 변경은 병합(merge)되기 전까지 `main`에 보이지 않습니다.

<a id="developing-functions"></a>
## 함수 개발하기 (Developing functions)

글로벌 브랜치에서 함수를 개발하기 전에 저장소가 다음 요구 사항을 충족하는지 확인합니다.

* TypeScript v1에서 글로벌 브랜칭(Global Branching)을 사용하려면 `functions-typescript` 자식 템플릿을 `0.903.0` 이상 버전으로 업그레이드합니다.
* TypeScript v2에서 글로벌 브랜칭을 사용하려면 `typescript-functions` 부모 템플릿을 `0.1299.0` 이상 버전으로 업그레이드하고 [로컬 Ontology SDK](11_python/02_local-sdks.md)를 활성화합니다.
* Python에서 글로벌 브랜칭을 사용하려면 `python-functions` 부모 템플릿을 `0.724.0` 이상 버전으로 업그레이드하고 로컬 Ontology SDK를 활성화합니다.

방법은 [저장소 업그레이드 문서](https://www.palantir.com/docs/foundry/code-repositories/repository-upgrades/#manual-branch-upgrade)를 참고하세요.

글로벌 브랜치에 있는 리소스의 변경 사항, 예를 들어 새로 만들었거나 수정한 온톨로지 엔터티에 의존하는 함수를 개발할 수 있습니다.

![브랜치에서 새 함수를 개발하는 화면.](https://www.palantir.com/docs/resources/foundry/functions/branch-function.png)

준비가 되면 **버전 타깃(version target)** 을 지정해 함수를 게시합니다. 버전 타깃은 글로벌 브랜치가 병합될 때 `main`에 게시될 안정(stable) 버전입니다. 브랜치에서 개발하는 동안에는 함수가 불안정한 미리 보기(preview) 버전으로 게시됩니다.

![브랜치에서 함수를 게시하는 화면.](https://www.palantir.com/docs/resources/foundry/functions/branch-function-publish.png)

**설명**: 예를 들어 `main`에 함수 버전 `1.2.0`이 있고 브랜치에서 버전 타깃을 `1.3.0`으로 정했다고 합시다. 브랜치에서 게시할 때마다 `1.3.0`을 향한 미리 보기 버전이 만들어지고, 브랜치가 병합되는 시점에 비로소 `main`에 정식 `1.3.0`이 게시됩니다. 버전 번호 체계는 [함수 버전 관리](07_function-management/01_functions-versioning.md) 페이지에서 다룹니다.

브랜치에서 함수 게시에 성공하면, 브랜치 안의 Workshop, AIP Logic, 함수 기반 액션(function-backed action)에서 새 함수 버전을 사용할 수 있습니다. 이 함수 버전에는 `Branched pre-release` 태그가 붙습니다. 브랜치에서 게시한 함수는 `main`을 포함한 다른 브랜치에서 접근할 수 없습니다.

![Workshop에서 브랜치 함수를 사용하는 화면.](https://www.palantir.com/docs/resources/foundry/functions/branch-function-backed-variable.png)

![액션에서 브랜치 함수를 사용하는 화면.](https://www.palantir.com/docs/resources/foundry/functions/branch-function-backed-action.png)

**주의**: 현재 TypeScript v1, TypeScript v2, Python 저장소에서는 쿼리 함수(query function)의 브랜치 버전에 의존할 수 없습니다.

브랜치에서 개발을 계속하면서 같은 버전 타깃으로 함수 버전을 계속 게시할 수 있습니다. 버전 타깃이 바뀌지 않는 한, 함수를 사용하는 모든 리소스는 가장 최근에 게시된 버전을 자동으로 가져옵니다. 덕분에 게시할 때마다 함수 참조를 수동으로 갱신하지 않고 빠르게 반복 작업을 할 수 있습니다.

브랜치에서 버전 타깃이 바뀌면, 브랜치에서 이전 버전을 사용하던 함수의 모든 의존 리소스(dependent)를 새 버전 타깃을 사용하도록 갱신해야 합니다. 이 내용은 [검사(check)](https://www.palantir.com/docs/foundry/global-branching/core-concepts/#checks)로도 표시됩니다.

> **중간 요약**: 저장소 템플릿을 일정 버전 이상으로 올린 뒤, 버전 타깃을 지정해 브랜치에서 함수를 게시합니다. 같은 버전 타깃을 유지하면 브랜치 안의 사용처가 최신 미리 보기 버전을 자동으로 따라가고, 버전 타깃을 바꾸면 사용처를 직접 갱신해야 합니다.

<a id="direct-model-deployment-functions"></a>
## 직접 모델 배포 함수 (Direct model deployment functions)

글로벌 브랜치에서 직접 모델 배포용 [모델 함수](14_models/01_functions-on-models.md)를 게시하면, Foundry는 `-branch-YYYYMMDD-HHMMSS` 형식의 버전 접미사가 붙은 브랜치 로컬(branch-local) 함수 버전을 만듭니다. 이 버전을 보려면 [모델](https://www.palantir.com/docs/foundry/model-integration/models/)을 열고 **Live deployment**, 이어서 **Overview**를 선택합니다. 버전은 **Function** 섹션에 표시됩니다. 이 함수 버전은 같은 글로벌 브랜치의 지원 애플리케이션에서 사용할 수 있지만, `main`이나 다른 브랜치에서는 사용할 수 없습니다.

Foundry는 글로벌 브랜치에서만 브랜치 로컬 모델 함수 버전을 지원합니다. 글로벌 브랜치와 연결되지 않은 모델 브랜치는 브랜치 로컬 함수 버전을 게시할 수 없습니다.

직접 모델 배포 구성(configuration)과 모델 함수를 함께 검토하고 병합할 수 있습니다. 제안(proposal)이 병합되면 Foundry는 선택된 브랜치 로컬 함수 구성을 `main`의 안정 함수 버전으로 게시합니다. 목표로 한 안정 버전이 이미 `main`에 게시되어 있다면, 병합하기 전에 배포 구성을 리베이스해야 합니다.

직접 모델 배포 구성을 추가, 검토, 리베이스, 병합하는 방법은 [직접 모델 배포 브랜칭](https://www.palantir.com/docs/foundry/manage-models/branching-direct-model-deployments/)을 참고하세요.

> **중간 요약**: 모델 함수는 브랜치에서 `-branch-YYYYMMDD-HHMMSS` 접미사가 붙은 브랜치 전용 버전으로 게시되며, 제안이 병합될 때 `main`의 안정 버전이 됩니다.

<a id="conflict-resolution-and-rebasing-functions"></a>
## 충돌 해결과 함수 리베이스 (Conflict resolution and rebasing functions)

브랜치에서 개발하는 동안에는 `main`에 게시된 더 새로운 함수 버전을 자동으로 받지 않습니다. 이렇게 해서 `main`의 개발이 브랜치 작업을 방해하지 않게 합니다. `main`에 더 새로운 버전이 있으면 함수 버전 선택기와 Ontology Manager에 알림이 표시됩니다. 그러면 함수 버전을 리베이스해서 `main`의 새 버전들을 모두 가져올 수 있습니다.

![함수 리베이스 대화 상자.](https://www.palantir.com/docs/resources/foundry/functions/rebasing-functions.png)

**설명**: 리베이스(rebase)는 Git 용어로, 내 브랜치의 출발점을 대상 브랜치(여기서는 `main`)의 최신 상태로 옮기는 작업입니다. 여기서는 브랜치가 갈라진 뒤 `main`에 새로 게시된 함수 버전들을 브랜치로 가져오는 동작을 뜻합니다.

개발 중에 내 버전 타깃이 `main`에 먼저 게시되어 버리면, 병합 전에 새 버전 타깃을 선택해야 합니다. 새 버전 타깃을 선택한 뒤에는 의존 리소스가 새 버전 타깃을 사용하도록 갱신합니다.

**설명**: 예를 들어 브랜치에서 버전 타깃을 `1.3.0`으로 잡았는데, 다른 사람이 `main`에서 먼저 `1.3.0`을 게시했다고 합시다. 같은 번호의 버전을 두 번 게시할 수 없으므로 브랜치의 타깃을 `1.4.0` 같은 새 번호로 바꿔야 합니다.

> **중간 요약**: 브랜치는 `main`의 새 함수 버전을 자동으로 받지 않으며, 필요할 때 리베이스로 가져옵니다. 버전 타깃이 `main`에서 먼저 쓰였다면 새 타깃을 고르고 사용처를 갱신합니다.

<a id="merging"></a>
## 병합 (Merging)

글로벌 브랜치를 병합하면, 수정된 함수가 안정 버전 타깃으로 `main`에 게시됩니다. 브랜치에서 게시된 버전을 사용하던 리소스는 병합 과정에서 `main`에 게시된 새 안정 버전을 자동으로 사용하기 시작합니다.

**주의**: Foundry는 버전 타깃만 `main`에 병합하며, 브랜치에서 게시한 다른 버전은 병합하지 않습니다. 그 버전들은 브랜치가 병합된 뒤 `main`에 존재하지 않습니다.

## 정리

- TypeScript v1, TypeScript v2, Python, AIP Logic, 직접 모델 배포용 모델 함수는 글로벌 브랜치에서 개발하고 게시할 수 있습니다(저장소 템플릿 최소 버전 필요).
- 브랜치에서는 버전 타깃을 정해 미리 보기 버전으로 게시하며, 브랜치 안의 Workshop, AIP Logic, 함수 기반 액션에서만 쓸 수 있습니다.
- 버전 타깃이 같으면 사용처가 최신 미리 보기 버전을 자동으로 따라가고, 바뀌면 사용처를 직접 갱신해야 합니다.
- `main`의 새 버전은 리베이스로 가져오며, 병합 시에는 버전 타깃만 `main`의 안정 버전으로 게시됩니다.
