# 구조체에 대한 액션 (Actions on structs)

- 원문: https://www.palantir.com/docs/foundry/action-types/actions-on-structs/
- 사이드바 위치: Define Ontologies > Action types > Actions on structs

구조체(struct) 속성은 이름이 붙은 여러 필드를 하나로 묶은 속성입니다. 이 페이지는 액션으로 구조체 속성 값을 생성하고 수정할 때 쓰는 구조체 파라미터(struct parameter)의 정의, 속성과 파라미터 사이의 필드 매핑 규칙, 필드별 기본값과 제약 설정, 그리고 제한 사항을 설명합니다.

[구조체 속성(struct property)](../02_object-and-link-types/04_structs/01_structs-overview.md) 값은 구조체 파라미터로 제공된 값을 통해 액션으로 생성하고 수정할 수 있습니다.

<a id="struct-parameters"></a>
## 구조체 파라미터 (Struct parameters)

구조체 파라미터는 기본 타입(base type)이 `STRUCT`인 파라미터로, 그 타입 안에 각자의 이름과 기본 타입을 가진 중첩된 파라미터 필드가 들어 있습니다. 구조체 파라미터는 구조체 속성에 값을 제공하는 용도로만 쓸 수 있습니다. 구조체 파라미터 필드에 지원되는 기본 타입은 `BOOLEAN`, `DATE`, `DOUBLE`, `GEOPOINT`, `INTEGER`, `LONG`, `STRING`, `TIMESTAMP`입니다.

아래는 `Create Ticket` 액션의 `Resolution` 구조체 파라미터입니다. 중첩 필드 `summary`, `resolutionTime`, `owner`가 티켓이 어떻게 해결되었는지에 대한 정보를 하나의 파라미터로 묶습니다.

![중첩 필드가 있는 구조체 파라미터.](https://www.palantir.com/docs/resources/foundry/action-types/struct-parameter-nested-fields.png)

**설명**: 구조체는 C의 `struct`나 TypeScript의 객체 타입과 같은 개념입니다. 위 예를 타입으로 쓰면 다음과 같습니다.

```typescript
type Resolution = {
    summary: string;          // STRING
    resolutionTime: string;   // TIMESTAMP
    owner: string;            // STRING
};
```

일반 파라미터가 값 하나(문자열 하나, 정수 하나)를 받는다면, 구조체 파라미터는 이런 묶음 하나를 받습니다. 필드 타입으로는 위의 기본 타입만 쓸 수 있으므로, 구조체 안에 또 다른 구조체나 배열을 넣을 수는 없습니다.

<a id="defining-actions-on-struct-properties"></a>
## 구조체 속성에 대한 액션 정의하기 (Defining actions on struct properties)

구조체 파라미터를 사용하는 액션으로 구조체 속성을 가진 객체 타입을 생성하고 수정할 수 있습니다. 구조체 속성의 값은 그 속성에 매핑된 구조체 파라미터로 제출되며, 구조체 속성의 각 필드는 구조체 파라미터의 특정 필드에 매핑됩니다. 아래 예에서는 `Resolution` 구조체 파라미터의 각 필드가 `Ticket` 객체 타입의 `Resolution` 구조체 속성의 대응 필드에 매핑됩니다.

![구조체 속성 필드 매핑.](https://www.palantir.com/docs/resources/foundry/action-types/struct-field-mapping.png)

구조체 속성과 구조체 파라미터 사이의 매핑은 완전해야 합니다. 즉 구조체 속성의 모든 필드가 구조체 파라미터의 필드에 매핑되어야 합니다. 구조체 파라미터 필드의 기본 타입은 매핑된 구조체 속성 필드의 기본 타입과 *반드시* 일치해야 합니다. 구조체 속성 타입에 호환성을 깨는 변경(breaking change)이 생기면(예: 필드 추가, 필드 삭제, 필드 기본 타입 변경), 관련된 액션 타입도 그 변경을 반영하도록 수정해야 합니다.

**설명**: 예를 들어 `Ticket.Resolution` 속성에 나중에 `rootCause`(STRING) 필드를 추가하면, 기존 액션의 `Resolution` 파라미터에는 `rootCause`가 없으므로 매핑이 불완전해집니다. 이때 액션 타입의 구조체 파라미터에도 `rootCause` 필드를 추가하고 매핑해야 합니다. 함수의 매개변수 타입을 바꾸면 그 함수를 호출하는 모든 곳을 고쳐야 하는 것과 같은 원리입니다.

<a id="struct-parameters-in-an-action-form"></a>
### 액션 폼의 구조체 파라미터 (Struct parameters in an action form)

구조체 파라미터는 다른 파라미터 타입과 비슷하게 액션 폼으로 값을 채울 수 있습니다. 다만 구조체 파라미터 필드는 폼에서 개별적으로가 아니라 하나의 그룹으로 렌더링됩니다.

![액션 폼의 구조체 파라미터.](https://www.palantir.com/docs/resources/foundry/action-types/struct-parameter-form.png)

> **중간 요약**: 구조체 파라미터는 기본 타입이 `STRUCT`이고 중첩 필드를 가진 파라미터로, 구조체 속성에 값을 넣는 용도로만 쓰입니다. 속성의 모든 필드가 같은 기본 타입의 파라미터 필드에 매핑되어야 하며, 속성 타입이 바뀌면 액션도 고쳐야 합니다.

<a id="default-values-for-struct-parameter-fields"></a>
## 구조체 파라미터 필드의 기본값 (Default values for struct parameter fields)

기본값은 구조체 파라미터 필드별로 정의합니다. 각 구조체 파라미터 필드는 지정된 객체 타입의 구조체 속성 필드에 매핑됩니다. 기본값은 구조체 파라미터의 모든 필드에 대해 정의해야 하며, 모두 같은 객체 타입 구조체 속성의 필드에 매핑되어야 합니다. 구조체 파라미터 필드의 기본값으로는 구조체 속성 필드만 사용할 수 있습니다. 어떤 객체 타입의 구조체 속성 필드를 기본값으로 쓸지는 `ObjectReference` 파라미터에서 지정합니다.

![구조체 파라미터 필드의 기본값 정의.](https://www.palantir.com/docs/resources/foundry/action-types/struct-parameter-default-values.png)

액션을 제출할 때 `ObjectReference` 파라미터에 지정된 타입의 객체 인스턴스가 제공되며, 그 객체의 구조체 속성 필드 값이 대응하는 구조체 파라미터 필드의 값을 자동으로 채웁니다.

![구조체 파라미터 필드에 적용된 기본값.](https://www.palantir.com/docs/resources/foundry/action-types/struct-parameter-form-default-values.png)

**설명**: 예를 들어 `Edit ticket resolution` 액션에 `ticket`(ObjectReference) 파라미터와 `Resolution` 구조체 파라미터가 있다고 합시다. `Resolution`의 각 필드 기본값을 `ticket`의 `Resolution` 속성 필드로 지정해 두면, 사용자가 폼에서 티켓 TKT-12를 고르는 순간 TKT-12에 저장되어 있던 `summary`, `resolutionTime`, `owner` 값이 각 입력칸에 미리 채워집니다. 사용자는 바꾸고 싶은 필드만 고쳐서 제출하면 됩니다.

<a id="constraints-on-struct-parameter-fields"></a>
## 구조체 파라미터 필드의 제약 (Constraints on struct parameter fields)

일반 파라미터처럼 구조체 파라미터 필드에도 개별적으로 제약을 구성할 수 있습니다. 예를 들어 문자열 타입의 구조체 파라미터 필드에 문자열 길이 제약을 정의해, 길이가 10자 이상 500자 이하인 문자열만 허용하도록 할 수 있습니다. 이 경우 `Resolution` 구조체 파라미터의 `summary` 필드는 최소 10자 이상이어야 하고 500자를 넘을 수 없습니다.

![구조체 파라미터 필드의 제약 정의.](https://www.palantir.com/docs/resources/foundry/action-types/struct-parameter-field-constraint.png)

구조체 파라미터 값은 *모든* 필드가 정의된 제약을 충족할 때*만* 유효합니다. 사용자는 각 필드 값이 그 필드에 정의된 제약을 충족할 때만 구조체 파라미터 값을 제출할 수 있습니다. `summary` 필드의 정의대로라면 10자보다 짧은 값은 유효하지 않습니다.

![구조체 파라미터 필드 값에 적용된 제약.](https://www.palantir.com/docs/resources/foundry/action-types/invalid-struct-parameter-value.png)

> **중간 요약**: 구조체 파라미터 필드의 기본값은 `ObjectReference` 파라미터로 지정한 한 객체의 구조체 속성 필드에서만 가져올 수 있고, 모든 필드에 정의해야 합니다. 제약은 필드별로 설정하며, 모든 필드가 제약을 통과해야 값 전체가 유효합니다.

<a id="limitations"></a>
## 제한 사항 (Limitations)

액션으로 구조체 파라미터를 생성하거나 수정할 때 다음 제한 사항을 고려하세요.

* 구조체 속성 값은 *구조체 파라미터*로만 생성하거나 수정할 수 있습니다. 정적 값이나 객체 속성 참조 같은 다른 입력 방식은 지원되지 않습니다.
* 구조체 속성은 *단일* 구조체 파라미터로만 생성하거나 수정할 수 있습니다. 액션의 구조체 속성 매핑은 둘 이상의 파라미터를 사용할 수 없습니다.
* 구조체 파라미터는 *구조체* 속성을 생성하거나 수정하는 데만 쓸 수 있습니다. 구조체 파라미터 필드를 개별적으로 꺼내 구조체가 아닌 속성을 생성하거나 수정하는 데 쓸 수는 없습니다.
* 구조체 파라미터 필드의 기본값으로는 *단일 객체 타입의 구조체 속성 값*에 대한 참조만 쓸 수 있습니다. 정적 값 같은 다른 입력 방식은 지원되지 않습니다.

**설명**: 정리하면 구조체 속성과 구조체 파라미터는 일대일로만 연결됩니다. 예를 들어 `summary`는 일반 문자열 파라미터에서, `owner`는 다른 파라미터에서 가져와 `Resolution` 속성을 조립하는 식은 불가능하고, `Resolution` 구조체 파라미터 하나가 속성 전체를 채워야 합니다. 반대로 `Resolution.summary` 파라미터 필드 값을 `Ticket.title` 같은 일반 속성에 넣는 것도 불가능합니다.

## 정리

- 구조체 파라미터는 기본 타입 `STRUCT`에 중첩 필드(`BOOLEAN`, `DATE`, `DOUBLE`, `GEOPOINT`, `INTEGER`, `LONG`, `STRING`, `TIMESTAMP`)를 가지며, 구조체 속성에 값을 넣는 용도로만 쓰입니다.
- 구조체 속성의 모든 필드가 기본 타입이 같은 파라미터 필드에 매핑되어야 하고, 속성 타입에 호환성을 깨는 변경이 생기면 액션도 수정해야 합니다.
- 폼에서는 필드가 그룹으로 표시되고, 기본값은 `ObjectReference` 파라미터가 가리키는 객체의 구조체 속성에서 가져오며, 제약은 필드별로 적용됩니다.
- 구조체 속성과 구조체 파라미터는 일대일로만 연결되며, 정적 값이나 다른 파라미터로 구조체 속성을 채울 수 없습니다.
