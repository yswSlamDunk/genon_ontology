# Marketplace 제품에 온톨로지 타입 추가하기 (Add Ontology types to a Marketplace product)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/marketplace-ontology-types/
- 사이드바 위치: Define Ontologies > Object and link types > Add Ontology types to a Marketplace product

이 페이지는 객체 타입, 링크 타입, 공유 속성(shared property), 인터페이스 같은 온톨로지 정의를 Marketplace 제품(product)에 담아 다른 사용자가 설치하고 재사용할 수 있게 하는 방법을 설명합니다. 한 팀이 설계한 온톨로지 구조를 다른 환경에 그대로 배포할 수 있게 해 주므로, 같은 스키마를 여러 곳에서 반복해서 직접 만드는 수고를 줄여 줍니다. (원문 페이지 제목은 "Add object and link types to a Marketplace product"입니다.)

[Foundry DevOps](https://www.palantir.com/docs/foundry/devops/overview/)를 사용하면 객체 타입과 링크 타입을 [Marketplace 제품](https://www.palantir.com/docs/foundry/devops/core-concepts/#product)에 포함시켜 다른 사용자가 설치하고 재사용하게 할 수 있습니다. [첫 번째 제품을 만드는 방법을 알아보세요.](https://www.palantir.com/docs/foundry/foundry-devops/create-products/)

**설명**: Marketplace 제품은 Foundry 리소스(데이터셋, 파이프라인, 온톨로지 타입, 애플리케이션 등)의 정의를 묶은 배포 단위입니다. 소프트웨어 패키지 관리자(npm, pip 등)의 패키지가 코드와 의존성을 묶어 다른 프로젝트에 설치하게 하는 것처럼, 제품을 설치하면 그 안의 리소스 정의가 설치 대상 환경에 새로 만들어집니다.

<a id="unsupported-features"></a>
## 지원되지 않는 기능 (Unsupported features)

대부분의 [객체 속성 타입](03_properties/01_properties-overview.md)은 Marketplace 제품에서 지원되지만, 다음은 아직 사용할 수 없습니다.

* [Cipher](https://www.palantir.com/docs/foundry/cipher/overview/)
* Geo time
* Vector

객체 자체는 Marketplace로 패키징할 수 없습니다. 예를 들어 액션으로 만든 객체 편집(edit)은 Marketplace 제품에 패키징할 수 없다는 뜻입니다. 하지만 데이터셋과 객체 타입은 패키징할 수 있으므로, Marketplace 제품을 설치한 뒤 새 객체를 만들 수 있습니다.

[백킹 데이터소스(backing datasource)가 없는 객체 타입](02_object-types/02_create-object-type.md#create-an-object-type-without-a-backing-datasource)은 Marketplace 제품에서 지원됩니다.

위에서 지원되지 않는 기능 중 어느 것이든 지원이 필요하다면 Palantir Support에 문의하세요.

**설명**: 여기서 "객체를 패키징할 수 없다"는 것은 스키마(객체 타입 정의, 즉 `CREATE TABLE`에 해당)는 옮길 수 있지만 그 안의 행(객체 인스턴스, 즉 `INSERT`된 데이터)은 옮길 수 없다는 뜻입니다. 대신 데이터셋을 함께 패키징하면, 설치된 환경에서 그 데이터셋을 백킹 데이터소스로 하여 객체가 새로 만들어집니다.

> **중간 요약**: Cipher, Geo time, Vector 속성 타입은 아직 Marketplace에서 지원되지 않습니다. 객체 인스턴스나 액션 편집은 패키징할 수 없지만, 데이터셋과 객체 타입을 함께 패키징하면 설치 후 객체를 새로 만들 수 있습니다.

<a id="add-object-types-to-products"></a>
## 제품에 객체 타입 추가하기 (Add object types to products)

제품에 객체 타입을 추가하려면 먼저 [제품을 만듭니다](https://www.palantir.com/docs/foundry/foundry-devops/create-products/). [출력(output)을 추가](https://www.palantir.com/docs/foundry/foundry-devops/create-products/#add-outputs)한 다음 **Add ontology entities** 옵션을 선택합니다.

그러면 객체 타입을 고르라는 안내가 나옵니다. 객체 타입을 선택하면, 제품에 함께 추가하면 좋을 링크된 객체 타입에 대한 추천이 표시됩니다.

![객체 타입 추가](https://www.palantir.com/docs/resources/foundry/object-link-types/marketplace-add-object-type-dialog.png)

<a id="add-link-types-to-products"></a>
## 제품에 링크 타입 추가하기 (Add link types to products)

제품에 링크 타입을 추가하려면 먼저 [제품을 만든](https://www.palantir.com/docs/foundry/foundry-devops/create-products/) 다음 **Link type** 콘텐츠 타입을 선택합니다.

그러면 아래와 같이 링크 타입을 고르라는 안내가 나옵니다.

![링크 타입 추가](https://www.palantir.com/docs/resources/foundry/object-link-types/marketplace-add-link-type-dialog.png)

링크 타입을 직접 선택할 수도 있지만, 먼저 객체 타입을 추가한 다음 아래와 같이 [정보 패널(information panel)](https://www.palantir.com/docs/foundry/foundry-devops/create-products/#add-outputs)에서 관련 링크를 선택하는 방법을 권장합니다.

![패널에서 링크 타입 추가](https://www.palantir.com/docs/resources/foundry/object-link-types/marketplace-add-link-type-panel.png)

**설명**: 링크 타입은 양쪽 끝의 객체 타입이 있어야 의미가 있습니다. 예를 들어 `Employee`와 `Department`를 잇는 `works_in` 링크 타입만 제품에 넣고 두 객체 타입을 빼면, 설치 환경에서는 링크 타입이 가리킬 대상이 없습니다. 객체 타입을 먼저 넣고 정보 패널에서 관련 링크를 고르는 방식을 권장하는 이유가 이것입니다.

<a id="add-shared-properties-to-products"></a>
## 제품에 공유 속성 추가하기 (Add shared properties to products)

제품에 공유 속성 타입을 추가하려면 먼저 [제품을 만듭니다](https://www.palantir.com/docs/foundry/foundry-devops/create-products/). 그런 다음 아래와 같이 **Shared property** 콘텐츠 타입을 선택합니다.

그러면 공유 속성을 고르라는 안내가 나옵니다.

![Marketplace 제품에 공유 속성 추가하기](https://www.palantir.com/docs/resources/foundry/object-link-types/marketplace-add-shared-property-dialog.png)

<a id="add-interface-types-to-products"></a>
## 제품에 인터페이스 타입 추가하기 (Add interface types to products)

제품에 인터페이스 타입을 추가하려면 먼저 [제품을 만듭니다](https://www.palantir.com/docs/foundry/foundry-devops/create-products/). 그런 다음 아래와 같이 **Interface** 콘텐츠 타입을 선택합니다.

그러면 인터페이스를 고르라는 안내가 나옵니다.

![Marketplace 제품에 인터페이스 타입 추가하기](https://www.palantir.com/docs/resources/foundry/object-link-types/marketplace-add-interface-dialog.png)

> **중간 요약**: 객체 타입은 출력 추가에서 **Add ontology entities**로, 링크 타입, 공유 속성, 인터페이스는 각각 **Link type**, **Shared property**, **Interface** 콘텐츠 타입으로 제품에 추가합니다. 링크 타입은 객체 타입을 먼저 넣은 뒤 정보 패널에서 고르는 방식이 권장됩니다.

## 정리

- Foundry DevOps로 객체 타입, 링크 타입, 공유 속성, 인터페이스를 Marketplace 제품에 담아 다른 사용자가 설치하고 재사용하게 할 수 있습니다.
- Cipher, Geo time, Vector 속성 타입은 아직 지원되지 않으며, 객체 인스턴스와 액션 편집은 패키징할 수 없습니다.
- 데이터셋과 객체 타입을 함께 패키징하면 설치 후 객체가 새로 만들어지며, 백킹 데이터소스가 없는 객체 타입도 지원됩니다.
- 링크 타입은 객체 타입을 먼저 추가한 뒤 정보 패널에서 관련 링크를 선택하는 방식이 권장됩니다.
