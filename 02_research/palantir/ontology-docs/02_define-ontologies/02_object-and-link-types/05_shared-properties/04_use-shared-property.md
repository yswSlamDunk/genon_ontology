# 객체 타입에서 공유 속성 사용하기 (Use shared properties on object types)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/use-shared-property/
- 사이드바 위치: Define Ontologies > Object and link types > Shared properties > Use shared properties on object types

이 페이지는 객체 타입에 있는 기존 속성을 공유 속성(shared property)에 연결하는 방법과, 연결했을 때 속성 ID, API 이름, 메타데이터, 렌더 힌트가 어떻게 처리되는지 설명합니다. 연결을 해제(detach)하는 방법도 함께 다룹니다.

객체 타입의 속성을 공유 속성으로 바꾸려면 다음 단계를 따릅니다.

1. Ontology Manager에서 해당 객체 타입으로 이동합니다.
2. 패널에서 바꾸려는 속성을 선택한 다음, 설정 화면의 **Shared Property** 섹션까지 아래로 스크롤합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/convert-shared-property.png" alt="공유 속성 사용하기" width="500" />

3. 드롭다운 메뉴에서 사용할 기존 공유 속성을 선택하거나, [공유 속성 생성](02_create-shared-property.md) 모달로 이 속성을 새 공유 속성으로 변환합니다.

그러면 속성이 공유 속성으로 표시됩니다. 공유 속성 사용을 온톨로지에 영구 반영하려면 오른쪽 위의 **Save**를 선택합니다.

* 객체에서 공유 속성을 사용할 때, 객체 고유 속성의 속성 ID와 API 이름은 바뀌지 않고 그대로 유지됩니다. 이를 활용하는 기존 하위(downstream) 워크플로가 깨지지 않도록 하기 위해서입니다.
* 공유 속성과 연결되어 있는 동안에는 공유 속성에서 상속된 속성 메타데이터를 직접 편집할 수 없습니다. 타입 클래스는 여전히 추가, 삭제, 편집할 수 있습니다. 속성을 불러올 때 최종 타입 클래스 집합은 속성 자체의 타입 클래스와 연결된 공유 속성의 타입 클래스의 합집합이 됩니다.
* 사용하는 공유 속성의 [렌더 힌트](../09_metadata/02_metadata-render-hints.md) 설정 값이 선택한 속성과 다르면, 공유 속성을 사용할 때 선택한 속성의 설정 값이 덮어쓰입니다. 사용 사례에 맞는 렌더 힌트로 공유 속성이 설정되어 있는지 확인하세요.

**설명**: 세 가지 규칙을 예로 정리합니다. `Employee`의 `startDate` 속성(API 이름 `startDate`)을 `start date` 공유 속성에 연결해도 API 이름은 `startDate` 그대로이므로, 이 이름으로 속성을 읽던 함수나 애플리케이션 코드는 수정할 필요가 없습니다. 표시 이름과 설명은 공유 속성 쪽 값으로 고정되어 객체 타입 쪽에서 따로 고칠 수 없습니다. 타입 클래스는 예외로, 속성에 `{a, b}`, 공유 속성에 `{b, c}`가 있으면 결과는 합집합 `{a, b, c}`입니다. 렌더 힌트는 공유 속성 값이 이깁니다.

<a id="detach-a-shared-property-from-an-object"></a>
### 객체에서 공유 속성 분리하기

속성을 공유 속성에서 분리하려면, Ontology Manager에서 객체 타입의 같은 속성 패널을 열고 **Detach**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/detach-shared-property.png" alt="공유 속성 분리하기" width="500" />

이렇게 하면 속성과 공유 속성 사이의 연결이 제거됩니다.

## 정리

- 객체 타입의 속성 패널 **Shared Property** 섹션에서 기존 공유 속성을 고르거나 새 공유 속성으로 변환한 뒤 **Save**합니다.
- 연결 후에도 속성 ID와 API 이름은 유지되어 하위 워크플로가 깨지지 않습니다.
- 상속된 메타데이터는 직접 편집할 수 없고, 타입 클래스는 합집합으로 합쳐지며, 렌더 힌트는 공유 속성 값으로 덮어쓰입니다.
- **Detach**로 연결을 해제할 수 있습니다.
