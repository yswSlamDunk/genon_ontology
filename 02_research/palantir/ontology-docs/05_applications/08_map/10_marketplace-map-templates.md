# Marketplace 제품에 지도 템플릿 추가하기 (Add Map templates to a Marketplace product)

- 원문: https://www.palantir.com/docs/foundry/map/marketplace-map-templates/
- 사이드바 위치: Applications > Map > Add Map templates to a Marketplace product

이 페이지는 직접 만든 지도 템플릿을 Marketplace 제품(product)에 포함시켜 다른 사용자가 설치해 재사용할 수 있게 하는 방법을 짧게 설명합니다. 어떤 기능이 지원되는지와 제품에 템플릿을 추가하는 절차를 다룹니다.

[Foundry DevOps](https://www.palantir.com/docs/foundry/devops/overview/)를 사용해 [지도 템플릿](08_templates-and-workshop-widget/01_templates.md)을 [Marketplace 제품](https://www.palantir.com/docs/foundry/devops/core-concepts/#product)에 포함하면 다른 사용자가 설치하고 재사용할 수 있습니다. [첫 제품을 만드는 방법을 알아보세요.](https://www.palantir.com/docs/foundry/foundry-devops/create-products/)

**설명**: Marketplace 제품은 템플릿, 모듈, 온톨로지 정의 같은 Foundry 리소스를 하나로 묶어 다른 프로젝트나 조직에 설치할 수 있게 만든 패키지입니다. 소프트웨어 패키지 관리자에서 라이브러리를 배포하고 설치하는 흐름과 같은 구조로, 한 번 만든 리소스를 여러 곳에 복제해 쓰게 해 줍니다.

<a id="supported-features"></a>
## 지원되는 기능 (Supported features)

[지도 레이어(Map Layers)](07_integrate-data-for-the-map/05_layer-editor.md)를 제외한 모든 지도 템플릿 기능이 지원됩니다.

<a id="adding-map-templates-to-products"></a>
## 제품에 지도 템플릿 추가하기 (Adding Map templates to products)

제품에 지도 템플릿을 추가하려면, 먼저 [제품을 만들고](https://www.palantir.com/docs/foundry/foundry-devops/create-products/) [출력(output)을 추가](https://www.palantir.com/docs/foundry/foundry-devops/create-products/#add-outputs)합니다. **Add files** 옵션을 선택해 [Compass](https://www.palantir.com/docs/foundry/compass/overview/) 파일 시스템에서 지도 템플릿으로 이동한 뒤 제품에 추가합니다.

## 정리

- 지도 템플릿은 Foundry DevOps를 통해 Marketplace 제품에 넣어 다른 사용자가 설치하고 재사용하게 할 수 있습니다.
- Map Layer Editor로 만든 지도 레이어를 제외한 모든 템플릿 기능이 지원됩니다.
- 제품을 만들고 출력을 추가할 때 **Add files**로 Compass에서 템플릿을 골라 넣습니다.
