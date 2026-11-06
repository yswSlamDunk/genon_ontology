# 공유 속성 메타데이터 참조 (Metadata reference)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/shared-property-metadata/
- 사이드바 위치: Define Ontologies > Object and link types > Shared properties > Metadata reference

이 페이지는 온톨로지에서 공유 속성(shared property) 하나를 표현하는 메타데이터 항목을 모두 나열한 참조 문서입니다. 생성, 편집 페이지에 나온 항목에 더해 RID와 사용처(Usage)까지 포함합니다.

공유 속성은 온톨로지에서 다음 메타데이터로 표현됩니다.

* **이름(Name):** 공유 속성의 이름입니다.
* **설명(Description):** 사용자 애플리케이션에서 누구나 읽을 수 있는 공유 속성 설명 텍스트입니다. 예를 들어 `start date` 공유 속성의 설명은 `The day the employee began new hire training`(직원이 신입 교육을 시작한 날)일 수 있습니다.
* **RID:** Foundry의 모든 리소스에 대해 자동으로 생성되는 고유 식별자입니다. 속성의 RID는 플랫폼 전반의 오류 메시지에서 참조됩니다.
* **기본 타입(Base type):** 이 속성의 값 타입을 나타내며, 사용자 애플리케이션에서 쓸 수 있는 연산의 집합을 결정합니다. 예를 들어 `start date` 속성의 기본 타입은 `date`입니다. 사용자 애플리케이션에서는 이 속성으로 타임라인 위젯을 구성할 수 있습니다.
* **값 서식(Value formatting):** 속성의 기본 타입에 따라 숫자 서식, 날짜 및 시간 서식, 사용자 ID 서식, 리소스 ID 서식을 속성에 적용할 수 있으며, 원시 값을 사용자 애플리케이션에서 더 읽기 쉬운 형태로 바꿔 줍니다. [값 서식](../03_properties/03_value-formatting.md)에 대해 더 알아보세요.
* **타입 클래스(Type classes):** 사용자 애플리케이션이 해석하는 추가 메타데이터입니다. [타입 클래스](../09_metadata/01_metadata-typeclasses.md)에 대해 더 알아보세요.
* **렌더 힌트(Render hints):** 같은 기본 타입의 다른 속성 대부분과 다르게 이 속성을 어떻게 렌더링할지 사용자 애플리케이션에 알려 주는 표시입니다. 많은 렌더 힌트는 해당 속성이 정의된 객체 타입의 재인덱싱(reindex) 성능에 영향을 줄 수 있습니다. 예를 들어 사용자 애플리케이션에서 아무도 `start date` 속성으로 검색하거나 정렬하지 않을 것으로 예상된다면, `searchable`과 `sortable` 렌더 힌트를 해제해 `Employee` 객체 타입의 재인덱싱 성능을 높일 수 있습니다. [렌더 힌트](../09_metadata/02_metadata-render-hints.md)에 대해 더 알아보세요.
* **가시성(Visibility):** 사용자 애플리케이션이 이 속성을 얼마나 눈에 띄게 표시할지 알려 주는 표시입니다. `prominent` 속성은 애플리케이션이 사용자에게 이 속성을 가장 먼저 보여 주게 합니다. `hidden` 속성은 사용자 애플리케이션에 나타나지 않습니다. 기본적으로 `start date` 속성의 가시성은 `normal`입니다.
* **사용처(Usage):** 공유 속성이 사용되는 객체 타입들입니다. 예를 들어 `start date` 속성은 온톨로지 안의 `Employee`, `Contractor` 및 기타 객체 타입에서 사용될 수 있습니다.

**설명**: RID(Resource Identifier)는 `ri.`로 시작하는 긴 문자열로, 이름이 바뀌어도 변하지 않는 리소스의 고유 ID입니다. 데이터베이스에서 사람이 바꿀 수 있는 이름 열과 별도로 바뀌지 않는 대리 키(surrogate key)를 두는 것과 같은 목적입니다. 오류 메시지에 RID가 찍히므로, 문제가 생겼을 때 어느 속성이 원인인지 RID로 찾을 수 있습니다.

## 정리

- 공유 속성의 메타데이터는 이름, 설명, RID, 기본 타입, 값 서식, 타입 클래스, 렌더 힌트, 가시성, 사용처로 구성됩니다.
- RID는 자동 생성되는 고유 식별자로 오류 메시지에서 속성을 가리킬 때 쓰입니다.
- 사용처는 이 공유 속성을 쓰는 객체 타입 목록입니다.
