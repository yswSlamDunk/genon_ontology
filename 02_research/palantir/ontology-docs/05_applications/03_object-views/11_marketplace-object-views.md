# Marketplace 제품에 Object View 추가하기 (Add Object Views to a Marketplace product)

- 원문: https://www.palantir.com/docs/foundry/object-views/marketplace-object-views/
- 사이드바 위치: Applications > Object Views > Add Object Views to a Marketplace product

이 페이지는 직접 만든 Object View를 Marketplace 제품에 포함시켜 다른 사용자가 설치해 재사용할 수 있게 하는 방법을 설명합니다. 어떤 Object View 탭이 패키징 대상이 될 수 있는지와, 제품에 추가하는 절차를 다룹니다.

[Foundry DevOps](https://www.palantir.com/docs/foundry/devops/overview/)를 사용하면 Object View를 [Marketplace 제품](https://www.palantir.com/docs/foundry/devops/core-concepts/#product)에 포함시켜 다른 사용자가 설치하고 재사용하게 할 수 있습니다. [첫 번째 제품을 만드는 방법을 알아보세요.](https://www.palantir.com/docs/foundry/foundry-devops/create-products/)

**설명**: 여기서 제품(product)은 객체 타입, 애플리케이션 화면 같은 Foundry 리소스 여러 개를 하나로 묶은 배포 단위입니다. 프로그래밍 언어의 패키지(npm 패키지, pip 패키지)를 만들어 저장소에 올리면 다른 프로젝트가 설치해 쓰는 흐름과 같은 구조로, 한 환경에서 만든 리소스를 다른 사용자나 환경에 설치합니다.

<a id="supported-features"></a>
## 지원되는 기능 (Supported features)

Marketplace 제품은 [Workshop 탭](06_full-object-views/02_config-object-views.md) 빌더를 사용하는 [Object View 탭](08_legacy-object-views/02_config-tabs.md)만 지원합니다. 레거시 Object View 빌더는 지원하지 않습니다. 레거시 빌더를 사용하는 Object View 탭을 패키징하고 싶다면, 먼저 Workshop 탭 빌더로 그 탭을 다시 만들어야 합니다.

> **중간 요약**: Workshop 탭 빌더로 만든 Object View 탭만 Marketplace 제품에 넣을 수 있고, 레거시 빌더로 만든 탭은 Workshop 탭 빌더로 다시 만들어야 합니다.

<a id="add-object-views-to-products"></a>
## 제품에 Object View 추가하기 (Add Object Views to products)

Object View를 제품에 추가하려면 먼저 [제품을 만드세요](https://www.palantir.com/docs/foundry/foundry-devops/create-products/). [출력을 추가](https://www.palantir.com/docs/foundry/foundry-devops/create-products/#add-outputs)한 다음 **Add ontology entities** 옵션을 선택하세요.

Object View를 선택한 뒤에는 제품에 포함할 탭을 고를 수 있습니다.

![Object View 탭 추가하기.](https://www.palantir.com/docs/resources/foundry/object-views/marketplace-add-tabs.png)

## 정리

- Foundry DevOps로 Object View를 Marketplace 제품에 포함해 다른 사용자가 설치하게 할 수 있습니다.
- Workshop 탭 빌더로 만든 탭만 지원되며, 레거시 빌더 탭은 먼저 다시 만들어야 합니다.
- 제품 생성, 출력 추가, **Add ontology entities** 선택, Object View와 탭 선택 순으로 추가합니다.
