# 인터페이스 메타데이터 참조 (Metadata reference)

- 원문: https://www.palantir.com/docs/foundry/interfaces/interface-metadata/
- 사이드바 위치: Define Ontologies > Interfaces > Metadata reference

이 페이지는 온톨로지에서 인터페이스 하나를 기술하는 메타데이터 항목(RID, 아이콘, 표시 이름, 설명, API 이름, 상태, 검색 가능 여부)을 나열한 참조 페이지입니다. 각 항목이 어디에 쓰이는지와 기본값을 `Facility` 인터페이스 예로 보여 줍니다.

인터페이스는 온톨로지에서 다음 메타데이터로 표현됩니다.

* **RID:** Palantir의 모든 리소스마다 자동 생성되는 고유 식별자입니다. 플랫폼 곳곳의 오류 메시지에서 인터페이스의 RID가 언급됩니다.
* **Icon(아이콘):** 사용자가 애플리케이션에서 이 인터페이스를 볼 때 나타나는 시각적 식별자로, 그림과 색으로 이루어집니다. 인터페이스 아이콘은 객체 타입 아이콘과 시각적으로 구분되도록 주위에 점선이 둘러져 있습니다. 예를 들어 `Facility` 인터페이스는 점선으로 둘러싼 건물 아이콘으로 표시할 수 있습니다.
* **Display name(표시 이름):** 사용자 애플리케이션에서 이 인터페이스에 접근하는 누구에게나 보이는 이름입니다. 예를 들어 `Facility` 인터페이스의 표시 이름은 "Facility"일 수 있습니다.
* **Description(설명):** 사용자 애플리케이션에서 누구나 읽을 수 있는 인터페이스에 대한 설명 텍스트입니다. 예를 들어 `Facility` 인터페이스의 설명은 "An abstract object type interface for representing airline facilities"(항공사 시설을 표현하기 위한 추상 객체 타입 인터페이스)일 수 있습니다.
* **API name(API 이름):** 코드에서 프로그래밍 방식으로 인터페이스를 가리킬 때 쓰는 이름입니다. 예를 들어 `Facility` 인터페이스의 API 이름은 `facility`일 수 있습니다.
* **Status(상태):** 인터페이스가 개발 과정의 어느 단계에 있는지 사용자와 온톨로지 빌더에게 알려 주는 신호입니다. `active`, `experimental`, `example`, `deprecated` 중 하나일 수 있습니다. 기본적으로 `Facility` 인터페이스는 `experimental` 상태를 갖습니다. [상태](../02_object-and-link-types/09_metadata/03_metadata-statuses.md)에 대해 자세히 알아보세요.
* **Searchable(검색 가능):** 인터페이스가 검색 가능한지를 지정하는 Boolean 값입니다. 검색 가능한 인터페이스는 사용자가 그 인터페이스의 모든 객체를 한 번에 불러오거나 검색할 수 있게 해 줍니다. 검색 가능한 인터페이스는 구현 객체 타입이 75개로 제한되고, 검색 불가능한 인터페이스는 1,000개로 제한됩니다. 기본적으로 `Facility` 인터페이스는 검색 가능합니다.

**설명**: RID(Resource Identifier)는 사람이 바꿀 수 있는 표시 이름이나 API 이름과 달리 시스템이 부여하고 바뀌지 않는 ID로, 데이터베이스의 대리 키(surrogate key)와 같은 역할을 합니다. Searchable 항목의 개수 제한은 트레이드오프를 보여 줍니다. 예를 들어 `Facility`를 `Airport`, `Hangar`, `Warehouse` 세 객체 타입이 구현하고 검색 가능으로 설정하면, 세 타입의 객체를 하나의 검색으로 함께 조회할 수 있습니다. 그 대신 구현 객체 타입 수가 75개를 넘을 수 없습니다.

## 정리

- 인터페이스 메타데이터는 RID, 아이콘, 표시 이름, 설명, API 이름, 상태, 검색 가능 여부로 이루어집니다.
- 인터페이스 아이콘은 점선 테두리로 객체 타입 아이콘과 구분됩니다.
- 상태는 `active`, `experimental`, `example`, `deprecated` 중 하나이며 기본값은 `experimental`입니다.
- 검색 가능한 인터페이스는 모든 구현 객체를 한 번에 검색할 수 있지만 구현 객체 타입이 75개로 제한되고, 검색 불가능하면 1,000개까지 허용됩니다.
