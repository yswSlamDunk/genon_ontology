# 객체 타입 메타데이터 참조 (Metadata reference)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/object-type-metadata/
- 사이드바 위치: Define Ontologies > Object and link types > Object types > Metadata reference

이 페이지는 온톨로지에서 객체 타입(object type) 하나를 기술하는 메타데이터 항목을 한 목록으로 정리한 참조 문서입니다. ID, RID, 표시 이름, API 이름처럼 객체 타입을 가리키는 여러 이름과, 가시성, 상태, 인덱스 상태, 라이트백(writeback)처럼 객체 타입의 현재 상황을 알려 주는 값이 각각 무엇인지 `Employee` 예시로 설명합니다. 객체 타입 설정 화면에서 보이는 필드의 의미를 확인할 때 참고하면 됩니다.

온톨로지에서 객체 타입은 다음 메타데이터로 표현됩니다.

* **ID:** 객체 타입의 고유 식별자로, 주로 애플리케이션을 구성할 때 이 타입의 객체를 참조하는 데 쓰입니다. 예를 들어 `employee`가 `Employee` 객체 타입의 ID일 수 있습니다.
* **RID:** Foundry의 모든 리소스에 대해 자동으로 생성되는 고유 식별자입니다. 객체 타입의 RID는 플랫폼 전반의 오류 메시지에서 참조됩니다.
* **Icon(아이콘):** 객체 타입을 시각적으로 구분하는 그림과 색상으로, 사용자가 사용자 애플리케이션에서 이 타입의 객체를 볼 때 나타납니다. 예를 들어 사람 아이콘으로 `Employee` 객체 타입을 나타낼 수 있습니다.
* **Display name(표시 이름):** 사용자 애플리케이션에서 이 타입의 객체 하나에 접근하는 모든 사람에게 보이는 이름입니다. 예를 들어 `Employee` 객체 타입의 표시 이름은 `Employee`일 수 있습니다.
* **Plural display name(복수형 표시 이름):** 사용자 애플리케이션에서 이 타입의 객체 여러 개에 접근하는 모든 사람에게 보이는 이름입니다. 예를 들어 `Employee` 객체 타입의 복수형 표시 이름은 `Employees`일 수 있습니다.
* **Description(설명):** 사용자 애플리케이션에서 누구나 읽을 수 있는 객체 타입에 대한 설명 문구입니다. 예를 들어 `Employee` 객체 타입의 설명은 `All full-time and part-time employees of Organization X`(조직 X의 모든 정규직 및 시간제 직원)일 수 있습니다.
* **Groups(그룹):** 그룹은 객체 타입을 분류하는 데 도움이 되는 레이블입니다. 예를 들어 `Employee` 객체 타입은 `HR` 그룹과 `Employee 360` 그룹에 속할 수 있습니다.
* **API name(API 이름):** 코드에서 프로그래밍 방식으로 객체 타입을 가리킬 때 쓰는 이름입니다. 예를 들어 `Employee` 객체 타입의 API 이름은 `Employee`일 수 있습니다. [API 이름(TSv1)](../../04_functions/13_functions-on-objects/06_api-objects-links.md)에 대해 더 읽어 보세요.
* **Visibility(가시성):** 사용자 애플리케이션에 객체 타입을 얼마나 눈에 띄게 표시할지 알려 주는 표시입니다. `prominent` 객체 타입은 애플리케이션이 이 객체 타입을 사용자에게 가장 먼저 보여 주도록 합니다. `hidden` 객체 타입은 사용자 애플리케이션에 나타나지 않습니다. 기본적으로 `Employee` 객체 타입의 가시성은 `normal`입니다.
* **Status(상태):** 객체 타입이 개발 과정의 어디쯤에 있는지 사용자와 다른 온톨로지 빌더에게 알려 주는 신호입니다. `active`, `experimental`, `deprecated` 중 하나입니다. 기본적으로 `Employee` 객체 타입의 상태는 `experimental`입니다. [상태](../09_metadata/03_metadata-statuses.md)에 대해 더 읽어 보세요.
* **Index status(인덱스 상태):** 객체 타입과 그 백킹 데이터소스(backing datasource)의 마지막 재인덱싱 결과 상태입니다. `success`, `failed`, `not started` 중 하나입니다. [인덱스 상태](../../../06_ontology-architecture/05_object-databases/01_object-storage-v1.md)에 대해 더 읽어 보세요.
* **Writeback(라이트백):** 객체 타입에 라이트백 데이터셋이 생성되어 있는지, 그리고 최종 사용자가 이 타입의 객체를 편집할 수 있도록 허용하는 기능이 `enabled`(활성화)인지 `disabled`(비활성화)인지를 나타냅니다. [라이트백 데이터셋](../07_allow-editing.md)에 대해 더 읽어 보세요.

**설명**: 이 목록에는 객체 타입을 가리키는 이름이 네 가지 나옵니다. 같은 `Employee` 객체 타입을 예로 들면 다음과 같습니다.

| 항목 | 예시 값 | 누가 쓰는가 |
|---|---|---|
| 표시 이름 | `Employee` | 화면을 보는 사용자 |
| ID | `employee` | 애플리케이션 구성(예: Workshop 설정) |
| API 이름 | `Employee` | 코드(함수, OSDK) |
| RID | 시스템이 자동 생성한 문자열 | 플랫폼 내부와 오류 메시지 |

RID(Resource Identifier)는 사용자가 정하지 않고 시스템이 부여하는 값이라는 점에서 데이터베이스의 자동 증가 대리 키(surrogate key)와 성격이 비슷하고, ID와 API 이름은 사람이 정하는 이름입니다. 인덱스 상태는 백킹 데이터셋의 내용을 검색과 조회가 빠른 객체 저장소로 옮기는 작업(인덱싱)이 마지막으로 성공했는지를 보여 줍니다. 라이트백 데이터셋은 사용자가 화면에서 한 편집(edit)을 반영한 결과를 다시 데이터셋 형태로 기록해 둔 것입니다.

[온톨로지에서 객체 타입을 만들고 구성하는 방법과 객체 타입 메타데이터의 유효성 요건에 대해 더 알아보세요.](02_create-object-type.md)

[속성(property, 객체 타입의 특성)에 대해 더 알아보세요.](../03_properties/01_properties-overview.md)

## 정리

- 객체 타입은 ID, RID, 아이콘, 표시 이름, 복수형 표시 이름, 설명, 그룹, API 이름, 가시성, 상태, 인덱스 상태, 라이트백이라는 메타데이터로 표현됩니다.
- ID는 애플리케이션 구성용, API 이름은 코드용, 표시 이름은 사용자 화면용 이름이고, RID는 시스템이 자동으로 부여합니다.
- 가시성(`prominent`, `normal`, `hidden`)은 화면 노출 정도를, 상태(`active`, `experimental`, `deprecated`)는 개발 단계를 나타냅니다.
- 인덱스 상태는 마지막 재인덱싱 결과를, 라이트백은 사용자 편집 허용 여부와 라이트백 데이터셋 존재 여부를 알려 줍니다.
