# Marketplace 제품에 Foundry Rules 추가하기 (Add Foundry Rules to a Marketplace product)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/marketplace/
- 사이드바 위치: Applications > Foundry Rules > Add Foundry Rules to a Marketplace product

이 페이지는 Foundry Rules 워크플로를 Marketplace 제품(product)으로 묶어 다른 사용자가 설치하고 재사용할 수 있게 하는 방법을 다룹니다. 어떤 기능이 패키징되고 무엇이 빠지는지, 제품에 워크플로를 추가하는 순서, 운영(Production) 설치 시 주의 사항을 설명합니다.

[Foundry DevOps](https://www.palantir.com/docs/foundry/devops/overview/)를 사용하면 Foundry Rules 워크플로를 [Marketplace 제품](https://www.palantir.com/docs/foundry/devops/core-concepts/#product)에 포함해 다른 사용자가 설치하고 재사용하게 할 수 있습니다. [첫 제품을 만드는 방법을 알아보세요](https://www.palantir.com/docs/foundry/foundry-devops/create-products/).

**설명**: Marketplace 제품은 애플리케이션, 온톨로지 정의(객체 타입, 액션 타입 등), 파이프라인 같은 Foundry 리소스를 하나의 설치 가능한 패키지로 묶은 것입니다. 소프트웨어 패키지 관리자(npm, pip)가 코드를 묶어 배포하듯, 리소스의 정의를 묶어 다른 환경에 설치합니다.

<a id="supported-features"></a>
## 지원되는 기능 (Supported features)

작성된 규칙 자체를 제외한 모든 Foundry Rules 기능이 지원됩니다. [객체는 Marketplace로 패키징할 수 없기](../../02_define-ontologies/02_object-and-link-types/11_marketplace-ontology-types.md#unsupported-features) 때문에, `Rule` 객체와 `Proposal` 객체, 그리고 그 안에 담긴 규칙 로직은 제품에 포함되지 않습니다.

**설명**: 제품에는 객체 타입이라는 "스키마"는 들어가지만 객체라는 "데이터 행"은 들어가지 않습니다. Foundry Rules에서 사용자가 작성한 각 규칙은 `Rule` 객체 하나로 저장되므로, 제품을 설치한 쪽에는 빈 `Rule` 객체 타입만 생기고 규칙은 새로 작성해야 합니다.

> **중간 요약**: Foundry Rules의 기능은 모두 패키징되지만, 작성된 규칙과 제안은 객체(데이터)이므로 제품에 포함되지 않습니다.

<a id="add-foundry-rules-workflows-to-products"></a>
## 제품에 Foundry Rules 워크플로 추가하기 (Add Foundry Rules workflows to products)

제품에 Foundry Rules 워크플로를 추가하려면 먼저 [제품을 만든](https://www.palantir.com/docs/foundry/foundry-devops/create-products/) 다음, 아래와 같이 **Workshop Application** 콘텐츠 유형을 선택하고 이어서 [Foundry Rules 작성 애플리케이션](03_deploy/04_author-and-run-a-rule.md)을 선택합니다.

![제품에 Foundry Rules 규칙 작성 애플리케이션 추가](https://www.palantir.com/docs/resources/foundry/foundry-rules/add-fr-workfhop.png)

Workshop 애플리케이션을 추가한 뒤에는 제품 입력(inputs)의 **Foundry rules workflows** 섹션으로 가서 워크플로를 포함합니다.

![입력 섹션에서 제품에 Foundry Rules 워크플로 애플리케이션 추가](https://www.palantir.com/docs/resources/foundry/foundry-rules/including-fr-workflow.png)

워크플로가 포함되면 추가 객체 타입과 액션 타입이 제품의 입력으로 포함됩니다. 대개 `Rule`과 `Proposal` 객체 타입, 그리고 생성된 모든 액션 타입을 제품에 포함하는 것이 좋습니다.

![제품에 Rule과 Proposal 객체 타입 추가](https://www.palantir.com/docs/resources/foundry/foundry-rules/fr-add-object-types.png)
![제품에 Foundry Rules가 생성한 액션 타입 추가](https://www.palantir.com/docs/resources/foundry/foundry-rules/fr-add-action-types.png)

**주의**: 제품의 설치 모드를 `Production`으로 설정할 때는 Ontology Manager 애플리케이션의 `Datasources` 탭에서 `Rule`과 `Proposal` 객체 타입에 대해 `Only allow edits via actions`(액션을 통한 편집만 허용)를 반드시 켜세요. 이 단계를 빼먹으면 사용자가 제안을 만들려고 할 때 `Actions:PermissionDenied` 오류를 만나게 됩니다.

> **중간 요약**: 제품에 Workshop 애플리케이션을 추가하고, 입력의 **Foundry rules workflows**에서 워크플로를 포함한 뒤, `Rule`과 `Proposal` 객체 타입과 생성된 액션 타입을 함께 넣습니다. `Production` 설치라면 두 객체 타입에 `Only allow edits via actions`를 켜야 합니다.

## 정리

- Foundry DevOps로 Foundry Rules 워크플로를 Marketplace 제품에 넣어 다른 사용자가 설치하고 재사용하게 할 수 있습니다.
- 작성된 규칙(`Rule` 객체)과 제안(`Proposal` 객체)은 객체이므로 제품에 포함되지 않습니다.
- **Workshop Application** 콘텐츠로 규칙 작성 애플리케이션을 추가한 뒤, **Foundry rules workflows** 입력에서 워크플로를 포함하고 관련 객체 타입과 액션 타입을 추가합니다.
- `Production` 설치 모드에서는 `Rule`과 `Proposal`에 `Only allow edits via actions`를 켜야 `Actions:PermissionDenied` 오류를 피할 수 있습니다.
