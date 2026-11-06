# Marketplace 제품에 액션 타입 추가하기 (Add action types to a Marketplace product)

- 원문: https://www.palantir.com/docs/foundry/action-types/marketplace-action-types/
- 사이드바 위치: Define Ontologies > Action types > Add action types to a Marketplace product

이 페이지는 직접 만든 액션 타입을 Marketplace 제품(product)에 포함시켜, 다른 사용자가 설치하고 재사용할 수 있게 하는 방법을 설명합니다. 패키징 전에 확인할 지원 범위와, 제품에 액션 타입을 추가하는 화면 절차를 다룹니다.

[Foundry DevOps](https://www.palantir.com/docs/foundry/devops/overview/)를 사용하면 액션 타입을 [Marketplace 제품](https://www.palantir.com/docs/foundry/devops/core-concepts/#product)에 포함시켜 다른 사용자가 설치하고 재사용하도록 할 수 있습니다. [첫 번째 제품을 만드는 방법을 알아보세요.](https://www.palantir.com/docs/foundry/foundry-devops/create-products/)

**설명**: Marketplace 제품은 객체 타입, 액션 타입, 애플리케이션 같은 Foundry 리소스를 하나로 묶은 배포 단위입니다. 소프트웨어 패키지 관리자에서 패키지가 의존성과 함께 설치되는 것처럼, 제품을 설치하면 묶인 리소스들이 다른 환경이나 프로젝트에 함께 만들어집니다.

<a id="supported-features"></a>
## 지원되는 기능 (Supported features)

[지원되지 않는 기능을 사용하는 객체 타입](../02_object-and-link-types/11_marketplace-ontology-types.md#unsupported-features)을 참조하는 액션을 제외하면, 대부분의 액션 타입 기능이 지원됩니다. 액션 타입을 패키징할 준비를 할 때, 액션 타입의 [**Security & Submission criteria**](02_getting-started.md#add-submission-criteria)가 특정 사용자를 참조하지 않는지 확인하세요. 사용자 참조가 있다면 그룹을 참조하도록 바꿔야 합니다.

**설명**: 제출 조건(submission criteria)에 "사용자 ID가 kim인 경우만 허용"처럼 특정 사용자를 적어 두면, 제품이 설치되는 다른 환경에는 그 사용자가 없을 수 있습니다. 반면 "Approvers 그룹 구성원만 허용"처럼 그룹을 참조하면, 설치하는 쪽에서 그 그룹을 자기 환경의 그룹에 대응시킬 수 있으므로 재사용이 가능합니다.

<a id="adding-action-types-to-products"></a>
## 제품에 액션 타입 추가하기 (Adding action types to products)

제품에 액션 타입을 추가하려면 먼저 [제품을 만든](https://www.palantir.com/docs/foundry/foundry-devops/create-products/) 다음, 아래와 같이 **Action type** 콘텐츠 유형을 선택합니다.

![액션 타입 추가.](https://www.palantir.com/docs/resources/foundry/action-types/marketplace-add-action-type.png)

그러면 액션 타입을 선택하라는 메시지가 표시됩니다.

![액션 타입 추가 대화 상자.](https://www.palantir.com/docs/resources/foundry/action-types/marketplace-add-action-type-dialog.png)

액션 타입을 직접 선택할 수도 있지만, [Workshop 애플리케이션](https://www.palantir.com/docs/foundry/workshop/marketplace-workshop/) 같은 콘텐츠를 먼저 추가한 다음, 아래와 같이 의존성(dependencies) 패널에서 관련 액션을 선택하는 방법을 권장합니다.

![패널을 통해 액션 타입 추가.](https://www.palantir.com/docs/resources/foundry/action-types/marketplace-add-action-type-panel.png)

## 정리

- Foundry DevOps를 사용하면 액션 타입을 Marketplace 제품에 넣어 다른 사용자가 설치하고 재사용하게 할 수 있습니다.
- 지원되지 않는 기능을 쓰는 객체 타입을 참조하는 액션은 패키징할 수 없습니다.
- 제출 조건에 있는 특정 사용자 참조는 그룹 참조로 바꿔 두어야 합니다.
- 제품에서 Action type 콘텐츠 유형을 골라 직접 추가할 수도 있지만, Workshop 애플리케이션 등을 먼저 추가하고 의존성 패널에서 관련 액션을 고르는 방식이 권장됩니다.
