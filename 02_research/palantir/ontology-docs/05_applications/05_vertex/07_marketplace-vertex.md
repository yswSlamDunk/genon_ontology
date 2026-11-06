# Marketplace 제품에 Vertex 그래프 템플릿 추가하기 (Add Vertex graph templates to a Marketplace product)

- 원문: https://www.palantir.com/docs/foundry/vertex/marketplace-vertex/
- 사이드바 위치: Applications > Vertex > Add Vertex graph templates to a Marketplace product

이 페이지는 Vertex 그래프 템플릿을 Marketplace 제품(product)에 포함시켜 다른 사용자가 설치하고 재사용할 수 있게 하는 방법을 설명합니다. 지원되는 기능의 범위와 제품에 템플릿을 넣는 절차가 짧게 나옵니다.

[Foundry DevOps](https://www.palantir.com/docs/foundry/devops/overview/)를 사용하면 [Vertex 그래프 템플릿](03_graphs/05_graphs-template.md)을 [Marketplace 제품](https://www.palantir.com/docs/foundry/devops/core-concepts/#product)에 포함시켜 다른 사용자가 설치하고 재사용하도록 할 수 있습니다. [첫 제품을 만드는 방법을 알아보세요.](https://www.palantir.com/docs/foundry/foundry-devops/create-products/)

<a id="supported-features"></a>
## 지원되는 기능 (Supported features)

저장된 Search Around를 제외한 모든 Vertex 그래프 템플릿 기능이 지원됩니다.

<a id="adding-vertex-graph-templates-to-products"></a>
## 제품에 Vertex 그래프 템플릿 추가하기 (Adding Vertex graph templates to products)

제품에 Vertex 그래프 템플릿을 추가하려면 먼저 [제품을 만들고](https://www.palantir.com/docs/foundry/foundry-devops/create-products/), [출력(output)을 추가](https://www.palantir.com/docs/foundry/foundry-devops/create-products/#add-outputs)합니다. **Add files** 옵션을 선택해 [Compass](https://www.palantir.com/docs/foundry/compass/overview/) 파일 시스템에서 그래프 템플릿으로 이동한 다음 제품에 추가합니다.

**설명**: Marketplace 제품은 데이터셋, 객체 타입, 애플리케이션 리소스 등을 하나로 묶어 다른 환경에 설치할 수 있게 만든 배포 단위입니다. 프로그래밍에서 여러 소스 파일과 의존성을 하나의 패키지로 묶어 배포하는 것에 대응합니다. Compass는 Foundry의 파일 시스템으로, 프로젝트와 폴더 안에 리소스가 저장되는 곳입니다.

## 정리

- Foundry DevOps로 Vertex 그래프 템플릿을 Marketplace 제품에 넣어 다른 사용자가 설치하고 재사용하게 할 수 있습니다.
- 저장된 Search Around를 제외한 모든 템플릿 기능이 지원됩니다.
- 제품을 만들고 출력을 추가할 때 **Add files**로 Compass에서 템플릿을 골라 넣습니다.
