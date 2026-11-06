# 파라미터 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/action-types/parameter-overview/
- 사이드바 위치: Define Ontologies > Action types > Parameters > Overview

이 페이지는 액션 타입의 입력값인 파라미터가 무엇이고 어떤 역할을 하는지 설명합니다. 파라미터는 Workshop 같은 애플리케이션의 사용자 입력과 액션 타입의 규칙(rule)을 이어 주는 연결부이므로, 이후 기본값, 필터, 재정의(override) 같은 파라미터 설정 페이지를 읽기 전에 먼저 이해해야 하는 개념입니다.

<a id="parameters"></a>
## 파라미터 (Parameters)

**파라미터(Parameters)는** 액션 타입의 입력입니다. 파라미터는 **규칙(Rules)과** [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/), [Slate](https://www.palantir.com/docs/foundry/slate/overview/), [Object Views](../../../05_applications/03_object-views/01_overview.md) 같은 다른 Foundry 애플리케이션 사이의 인터페이스 역할을 합니다. 파라미터는 외부 값을 담는 변수처럼 다루어집니다. 각 파라미터는 타입으로 정의되며, 타입이 그 파라미터가 받을 수 있는 값의 종류를 결정합니다. 타입 외에도 파라미터에는 다양한 설정이 있습니다. 파라미터마다 폼에 노출할지 여부, 사용자가 값을 바꿀 수 있는지 여부를 개별적으로 구성할 수 있습니다.

[값 타입(value type)으로 액션 파라미터를 제약](../../02_object-and-link-types/08_value-types/03_use-value-type.md#constrain-an-action-parameter-with-a-value-type)하면 Foundry 전반에서 검증 규칙을 재사용할 수 있습니다.

파라미터는 액션 타입 전체에 값을 운반합니다. 파라미터는 다음과 같은 곳에서 참조할 수 있습니다. 규칙에서 참조해 객체, 링크, 부수 효과(side effect)에 값을 넘길 수 있고, 제출 조건(submission criteria)에서 참조해 액션을 제출할 수 있는지 검사할 수 있으며, 액션이 바꾸기 전의 객체 속성 현재 값에 접근할 때 쓸 수 있고, 재정의(override)에서 참조해 뒤따르는 파라미터의 설정을 바꿀 수 있습니다.

예를 들어 사용자가 선택한 티켓의 상태를 수정할 수 있게 하는 액션 타입에서, 파라미터 하나는 `Ticket` 객체 타입 형태를 가질 수 있습니다. `Status` 파라미터는 문자열로 정의됩니다. 액션을 제출하면 객체 타입 파라미터는 선택된 `Ticket` 객체를 값으로 받고, `Status` 파라미터에는 바뀔 상태가 들어 있습니다. 그러면 액션 타입은 두 파라미터 값을 규칙에 넘기고 규칙을 실행해 객체를 편집합니다.

파라미터는 호스트 애플리케이션에서 값을 받을 수도 있으며, 이를 이용하면 액션이 속성 값을 바꾸기 전의 값을 기록할 수 있습니다. Workshop의 변수 `previous_status`가 선택된 `Ticket` 객체의 `Status` 속성 현재 값을 가져오게 할 수 있습니다. 이 값을 액션의 숨겨진 파라미터 `Previous Status`에 넘기고, `Status` 파라미터에는 업데이트된 상태를 담을 수 있습니다. 액션을 제출하면 액션 타입은 `Previous Status`와 `Status` 값을 모두 규칙에 넘기고 규칙을 실행해 객체를 편집합니다.

**설명**: 위 예시를 입력과 출력으로 정리하면 다음과 같습니다. 티켓 `T-17`의 현재 상태가 `Open`이고 사용자가 `Closed`를 고른다면, 제출 시 파라미터 값은 `Ticket = T-17`, `Previous Status = "Open"`(Workshop이 자동으로 채운 숨김 값), `Status = "Closed"`(사용자 입력)입니다. 규칙은 이 값으로 `T-17.status`를 `Closed`로 바꾸고, 필요하다면 `Previous Status`를 이력용 속성에 기록할 수 있습니다. "숨겨진 파라미터"는 폼에 보이지 않지만 값은 가지고 있는 파라미터로, 함수의 인자 중 호출하는 쪽이 자동으로 채워 주는 인자에 해당합니다.

## 정리

- 파라미터는 액션 타입의 입력이며, 타입이 받을 수 있는 값의 종류를 정합니다.
- 파라미터마다 폼 노출 여부와 사용자 수정 가능 여부를 설정할 수 있고, 값 타입으로 검증 규칙을 붙일 수 있습니다.
- 파라미터 값은 규칙, 제출 조건, 재정의 등 액션 타입 전체에서 참조됩니다.
- Workshop 같은 호스트 애플리케이션이 숨겨진 파라미터에 값을 넘겨, 변경 전 값을 함께 기록하는 패턴도 가능합니다.
