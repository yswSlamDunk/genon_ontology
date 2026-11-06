# 공유 속성 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/shared-property-overview/
- 사이드바 위치: Define Ontologies > Object and link types > Shared properties > Overview

이 페이지는 공유 속성(shared property)이 무엇인지 소개합니다. 공유 속성은 여러 객체 타입에서 함께 쓰는 속성 정의로, 같은 의미의 속성을 객체 타입마다 따로 정의하지 않고 한곳에서 메타데이터를 관리할 수 있게 해 줍니다.

**공유 속성(shared property)은** 온톨로지 안의 여러 [객체 타입](../02_object-types/01_object-types-overview.md)에서 사용할 수 있는 [속성(property)](../03_properties/01_properties-overview.md)입니다. 공유 속성을 쓰면 객체 타입 전반에 걸쳐 일관된 데이터 모델링을 할 수 있고, 속성 메타데이터를 중앙에서 관리할 수 있습니다. 속성 메타데이터는 객체들 사이에 공유되지만, 그 밑에 있는 객체 데이터는 공유되지 않습니다.

예를 들어 Ontology Manager에 `Employee`와 `Contractor` 객체 타입이 있고 둘 다 `start date` 속성을 가진다고 합시다. `start date` 공유 속성을 만들어 두 객체 타입에 사용하면, 일관된 속성으로 데이터를 모델링할 수 있고 `start date` 메타데이터를 객체 타입마다 고치는 대신 한곳에서 업데이트할 수 있습니다.

**설명**: "메타데이터는 공유되지만 데이터는 공유되지 않는다"는 말을 구체적으로 보면 다음과 같습니다. `start date`의 표시 이름, 설명, 타입(`date`), 표시 형식은 공유 속성 한곳에 정의되고 `Employee`와 `Contractor`가 그것을 따릅니다. 하지만 직원 E001의 시작일 `2023-05-01`은 `Employee`의 백킹 데이터소스에서, 계약자 C042의 시작일 `2024-01-15`는 `Contractor`의 백킹 데이터소스에서 각각 따로 옵니다. 데이터베이스로 말하면 두 테이블의 열 정의(이름, 타입, 주석)를 공통으로 관리할 뿐, 행 데이터는 각자의 테이블에 있습니다.

공유 속성은 [직접 생성](02_create-shared-property.md)할 수도 있고, 객체 타입에 있는 기존 속성을 공유 속성으로 변환할 수도 있습니다. 온톨로지에 추가된 공유 속성은 데이터를 온톨로지화하는 과정에서 객체 타입에 [사용](04_use-shared-property.md)할 수 있으며, 일반 속성과 비슷한 방식으로 [편집](03_edit-shared-property.md)할 수 있습니다.

객체에 있는 공유 속성은 이름 옆에 지구본 아이콘으로 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/shared-property-menu-option.png" alt="Ontology Manager의 공유 속성 페이지" width="800" />

## 정리

- 공유 속성은 여러 객체 타입이 함께 쓰는 속성 정의입니다.
- 이름, 설명, 타입, 표시 형식 같은 메타데이터만 공유되고 실제 값은 각 객체 타입의 데이터소스에서 옵니다.
- 직접 만들거나 기존 속성을 변환해 만들 수 있으며, 객체 타입에 붙여 쓰고 일반 속성처럼 편집합니다.
- 화면에서는 이름 옆 지구본 아이콘으로 구분됩니다.
