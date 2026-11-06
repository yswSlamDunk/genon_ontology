# 함수 기반 액션 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/action-types/function-actions-overview/
- 사이드바 위치: Define Ontologies > Action types > Function-backed actions > Overview

액션 타입은 보통 "객체 생성, 수정, 삭제" 같은 간단한 규칙(rule)으로 정의하지만, 여러 객체를 한꺼번에 바꾸거나 복잡한 계산이 필요한 경우에는 규칙만으로 부족합니다. 이 페이지는 이런 경우에 액션이 함수(function)를 호출해 변경 로직을 코드로 정의하는 함수 기반 액션(function-backed action)의 개념과 필요성을 소개합니다.

<a id="function-backed-actions"></a>
## 함수 기반 액션 (Function-backed actions)

액션 타입에서 [규칙(rule)](../06_rules.md)은 액션이 적용될 때 객체가 어떻게 바뀌어야 하는지를 정의합니다. 많은 액션 타입은 객체를 생성, 수정, 삭제하거나 객체 사이의 링크를 생성, 삭제할 수 있는 간단한 규칙으로 정의할 수 있습니다.

그러나 어떤 경우에는 간단한 규칙만으로는 원하는 변경을 표현하기에 충분하지 않습니다. 예를 들어 다음과 같은 일을 하고 싶을 수 있습니다.

* 현재 서로 링크되어 있는 여러 객체를 수정합니다. 예를 들어 `Incident` 객체의 `status` 필드를 `Closed`로 설정하면서, 링크된 모든 `Alert` 객체의 `status`도 `Resolved`로 설정하고 싶을 수 있습니다.
* 좀 더 복잡한 로직에 따라 객체의 속성(property)을 수정합니다. 예를 들어 여러 객체에서 데이터를 읽는 비즈니스 로직으로 값을 계산한 다음, 그 값을 객체 속성에 써 넣고 싶을 수 있습니다.
* 서로 다른 타입의 객체 여러 개를 생성하고 그 사이에 링크를 설정합니다.

이런 사용 사례를 지원하기 위해, 액션 타입이 객체를 어떻게 수정할지 로직을 정의하는 [함수](../../04_functions/01_overview.md)를 호출하도록 구성할 수 있습니다. 이런 액션 타입을 흔히 **함수 기반 액션(function-backed action)이라고** 부릅니다. 함수를 사용하면 원하는 만큼 많은 객체를 읽고 필요에 따라 객체를 수정하면서, 어떤 복잡도의 액션 타입이든 만들 수 있습니다.

**설명**: 첫 번째 예시를 SQL로 쓰면 다음 두 문장을 하나의 작업으로 묶는 것입니다.

```sql
UPDATE incident SET status = 'Closed' WHERE incident_id = 'INC-7';
UPDATE alert SET status = 'Resolved' WHERE incident_id = 'INC-7';
```

간단한 규칙은 "파라미터로 받은 객체 하나의 속성을 이 값으로 바꾼다" 수준이라, 두 번째 문장처럼 "링크된 객체들을 찾아 모두 바꾼다"는 표현하기 어렵습니다. 함수 기반 액션에서는 함수가 `Incident` 객체를 입력으로 받아 링크를 따라 `Alert` 객체들을 조회하고, 각각의 `status`를 바꾸는 편집(edit)을 반환합니다. 액션은 그 편집들을 온톨로지에 적용합니다. 즉 함수는 "무엇을 바꿀지 계산"하고, 액션은 "권한 검사와 제출 조건을 거쳐 실제로 적용"하는 역할을 나눠 맡습니다.

함수 기반 액션 타입은 매우 유연하지만, [액션 타입 제한](../17_scale-property-limits.md)과 [함수 실행 제한](../../04_functions/07_function-management/02_manage-functions.md#enforced-limits)을 모두 받습니다.

[튜토리얼](02_function-actions-getting-started.md)을 따라 함수 기반 액션을 시작해 보세요.

## 정리

- 간단한 규칙은 객체 생성, 수정, 삭제와 링크 생성, 삭제를 다루지만, 링크된 여러 객체 일괄 수정, 복잡한 계산, 여러 타입 객체 동시 생성 같은 경우에는 부족합니다.
- 함수 기반 액션은 액션이 함수를 호출해 변경 로직을 코드로 정의하므로 어떤 복잡도의 변경이든 표현할 수 있습니다.
- 대신 액션 타입 제한과 함수 실행 제한을 모두 지켜야 합니다.
