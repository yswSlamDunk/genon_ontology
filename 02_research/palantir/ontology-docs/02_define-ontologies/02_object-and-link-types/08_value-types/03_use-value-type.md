# 값 타입 사용하기 (Use value types)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/use-value-type/
- 사이드바 위치: Define Ontologies > Object and link types > Value types > Use value types

이 페이지는 만들어 둔 값 타입(value type)을 실제로 적용하는 곳과 방법을 설명합니다. 객체 타입 속성, 공유 속성(shared property), Pipeline Builder 파이프라인, 액션 파라미터에 값 타입을 붙일 수 있으며, 특히 속성에 적용할 때의 인덱싱 실패 위험과 액션 파라미터 제약 조건으로 쓸 때의 규칙을 자세히 다룹니다.

[값 타입을 만든](02_create-value-type.md) 뒤에는 Foundry 전반에서 데이터 타입이나 재사용 가능한 제약 조건으로 사용할 수 있습니다. 지원되는 사용 사례는 다음과 같습니다.

* 객체 타입 속성(property)에 값 타입 지정
* 공유 속성에 값 타입 지정
* Pipeline Builder 파이프라인 속성에 `logical type cast` 표현식을 사용해 논리 타입(logical type)으로 값 타입을 지정하고, objects 대상(target)에 쓸 때 속성에서 값 타입을 선택
* 액션 파라미터가 받을 수 있는 값을 제약

<a id="assign-a-value-type-to-a-property"></a>
## 속성에 값 타입 지정하기 (Assign a value type to a property)

속성에 값 타입을 지정하려면 속성을 구성하는 동안 드롭다운 메뉴에서 값 타입을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/value-type-use.png" alt="속성 구성 중에 값 타입을 선택한 모습" width="500" />

**주의**: 검증에 실패하는 속성 값이 들어 있는 객체 속성에 값 타입을 적용하면 해당 객체 타입의 인덱싱이 실패합니다. 이런 인덱스 실패는 Ontology Manager의 객체 타입 상태(health status)에서 볼 수 있으며, 거기서 데이터를 고치거나 값 타입을 갱신해 문제를 해결할 수 있습니다.

**설명**: 인덱싱은 백킹 데이터셋의 행을 객체로 만들어 조회용 저장소에 넣는 작업입니다. 값 타입의 제약 조건은 이 과정에서 검사되므로, 기존 데이터에 `not-an-email` 같은 값이 한 행이라도 있으면 객체 타입 전체 인덱싱이 실패합니다. 이미 데이터가 있는 속성에 값 타입을 붙이기 전에 기존 값이 제약 조건을 만족하는지 먼저 확인하는 것이 좋습니다.

> **중간 요약**: 속성 구성 화면에서 값 타입을 고르면 되지만, 기존 값 중 하나라도 검증에 실패하면 객체 타입 인덱싱이 실패하므로 데이터나 값 타입을 고쳐야 합니다.

<a id="constrain-an-action-parameter-with-a-value-type"></a>
## 값 타입으로 액션 파라미터 제약하기 (Constrain an action parameter with a value type)

값 타입 제약 조건을 사용해 액션 파라미터에 재사용 가능한 검증 규칙을 적용할 수 있습니다.

1. Ontology Manager에서 액션 타입을 열고 **Parameters** 탭을 선택합니다.
2. 제약하려는 파라미터를 선택합니다.
3. **Constraints** 카드에서 제약 조건 유형으로 **Value type**을 선택합니다.
4. 값 타입을 선택합니다.
5. 변경 사항을 저장합니다.

값 타입 선택기에는 [기본 타입(base type)](../03_properties/09_base-types.md)이 파라미터 타입과 호환되는 값 타입만 표시됩니다. 값 타입 제약 조건은 `String`, `Integer`, `Long`, `Double`, `Decimal`, `Date`, `Timestamp` 파라미터와, 이 타입들의 리스트 파라미터에 사용할 수 있습니다. 리스트 파라미터에서 리스트 전체를 제약하려면 `Array` 값 타입을 선택합니다. 리스트의 각 항목에 같은 제약 조건을 적용하려면 호환되는 비배열(non-array) 값 타입을 선택합니다. 값 타입 제약 조건은 구조체(struct) 파라미터나 그 필드에는 적용할 수 없습니다. [개별 구조체 파라미터 필드에는 지원되는 다른 제약 조건을 구성](../../03_action-types/10_actions-on-structs.md#constraints-on-struct-parameter-fields)할 수 있습니다.

액션 검증과 제출 과정에서 파라미터 값은 선택한 값 타입 제약 조건을 만족해야 합니다. 검증에 실패하면 액션을 제출할 수 없으며 값 타입의 **Failure validation message**(검증 실패 메시지)가 표시됩니다. 값 타입에 대한 호환성을 깨지 않는 갱신은 액션 타입에 자동으로 전파됩니다. [값 타입 버전](04_value-types-versions.md)에 대해 더 알아보세요.

**설명**: 리스트 파라미터의 두 가지 선택을 예로 들면 다음과 같습니다. 이메일 주소 목록을 받는 `List<String>` 파라미터에 "email" 값 타입(비배열)을 고르면 `["a@x.com", "b@y.com"]`의 각 원소가 이메일 형식인지 검사합니다. 반면 "최대 3개" 같은 범위 제약을 가진 `Array` 값 타입을 고르면 리스트 자체의 크기를 검사합니다.

> **중간 요약**: 액션 타입의 Parameters 탭에서 파라미터 제약 조건으로 값 타입을 고를 수 있으며, 기본 타입이 호환되는 값 타입만 선택할 수 있습니다. 리스트는 전체(Array 값 타입) 또는 원소별(비배열 값 타입)로 제약할 수 있고, 구조체 파라미터에는 쓸 수 없습니다.

## 정리

- 값 타입은 객체 타입 속성, 공유 속성, Pipeline Builder 속성(`logical type cast`), 액션 파라미터 제약 조건에 사용할 수 있습니다.
- 속성에 적용할 때 기존 값이 검증에 실패하면 객체 타입 인덱싱이 실패하며, Ontology Manager의 상태 화면에서 확인하고 고칩니다.
- 액션 파라미터에는 `String`, `Integer`, `Long`, `Double`, `Decimal`, `Date`, `Timestamp`와 그 리스트 타입에 값 타입 제약을 걸 수 있고, 검증 실패 시 실패 메시지가 표시되며 제출이 막힙니다.
- 값 타입의 호환성을 깨지 않는 갱신은 액션 타입에 자동으로 반영됩니다.
