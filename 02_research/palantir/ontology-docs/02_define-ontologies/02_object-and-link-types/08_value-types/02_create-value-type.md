# 값 타입 만들기 (Create a value type)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/create-value-type/
- 사이드바 위치: Define Ontologies > Object and link types > Value types > Create a value type

이 페이지는 Value Types Manager 애플리케이션에서 새 값 타입(value type)을 만드는 절차를 단계별로 안내합니다. 이름과 API 이름 같은 메타데이터를 정하고, 기본 타입을 고르고, 필요하면 검증 제약 조건과 실패 메시지, 미리 보기 값을 지정한 뒤 저장하는 순서입니다.

## 값 타입 만들기 절차

플랫폼 [space](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/#spaces) 전반에서 사용할 값 타입을 만들려면 아래 단계를 따르세요.

1. 플랫폼 사이드바에서 **Value Types Manager** 애플리케이션으로 이동합니다.
2. 왼쪽 위 모서리의 드롭다운 메뉴에서 값 타입을 만들 space를 선택합니다.
3. 오른쪽 위 모서리에서 **Create New Value Type**(새 값 타입 만들기)을 선택합니다.
4. 값 타입에 명확한 이름, 설명, 고유한 API 이름을 지정합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/value-type-create-metadata.png" alt="값 타입 메타데이터 생성" width="500" />

5. 값 타입의 [기본 타입(base type)](../03_properties/09_base-types.md)을 선택합니다.
6. (선택 사항) 값 타입의 제약 조건을 정의합니다. 검증 방법으로는 `String` 타입에 대한 정규 표현식, 열거 값(enumerated values), 범위(range) 등이 있으며, 기본 타입에 따라 다른 방법도 있습니다.
   기본 타입별로 지원되는 제약 조건의 전체 목록은 [값 타입 제약 조건](06_value-type-constraints.md) 문서를 참고하세요.
   제약 조건을 정의할 때는 값이 제약 조건을 만족하지 않을 때 표시되는 **Failure validation message**(검증 실패 메시지)를 구성합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/value-type-create-constraint.png" alt="값 타입 제약 조건 생성" width="500" />

7. (선택 사항이지만 권장) 값 타입의 예시 미리 보기 값을 지정합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/value-type-create-preview.png" alt="값 타입 미리 보기 생성" width="500" />

8. 값 타입을 저장합니다.

**설명**: 예를 들어 "email" 값 타입을 만든다면 이름은 `Email`, API 이름은 `email`, 기본 타입은 `String`, 제약 조건은 `^[^@]+@[^@]+\.[^@]+$` 같은 정규 표현식, 실패 메시지는 "유효한 이메일 주소가 아닙니다", 미리 보기 값은 `kim@example.com`처럼 채울 수 있습니다. 실패 메시지는 나중에 이 값 타입이 걸린 액션 파라미터에 잘못된 값을 넣었을 때 사용자에게 보이는 문구입니다.

## 정리

- 값 타입은 Value Types Manager에서 space를 고른 뒤 **Create New Value Type**으로 만듭니다.
- 이름, 설명, 고유 API 이름과 기본 타입은 필수이고, 제약 조건과 검증 실패 메시지는 선택 사항입니다.
- 예시 미리 보기 값은 선택 사항이지만 지정하는 것이 권장됩니다.
