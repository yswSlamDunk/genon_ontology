# 파라미터 기본값 설정 (Set parameter default value)

- 원문: https://www.palantir.com/docs/foundry/action-types/parameters-default-value/
- 사이드바 위치: Define Ontologies > Action types > Parameters > Set parameter default value

이 페이지는 액션 폼의 입력칸을 미리 채워 두는 파라미터 기본값(default value)을 설정하는 방법을 설명합니다. 기본값을 액션 타입 수준에서 한 번 정해 두면 이 액션을 쓰는 여러 애플리케이션이 같은 값을 공유하므로, 애플리케이션마다 따로 설정하고 따로 고쳐야 하는 번거로움이 사라집니다.

액션 타입 파라미터의 기본값은 액션 폼의 파라미터를 미리 채우는 데 사용됩니다. 기본값은 파라미터 수준에서 구성되며 Workshop, Object Explorer, Object Views, Quiver, Slate에서 지원됩니다. 기본값을 활용하면 여러 소비 애플리케이션에 걸쳐 액션 로직을 표준화할 수 있으므로, 애플리케이션마다 기본값을 따로 추가할 필요가 없습니다.

파라미터의 기본값은 고정된 값을 표시하도록 하거나, 선택된 객체의 속성을 표시하도록 설정할 수 있습니다.

<a id="default-value-interaction-with-local-variables"></a>
## 기본값과 로컬 변수의 상호 작용 (Default value interaction with local variables)

로컬 기본값(예: Workshop 변수)은 항상 전역 기본값보다 우선합니다. 기본값이 있는 액션에 Workshop 변수를 넘기면, 액션 폼은 Workshop 변수의 값으로 미리 채워집니다. Object Views의 환경 변수와 Slate의 기본값에도 같은 방식이 적용됩니다. 액션의 각 인스턴스(사용 위치)에서 제공한 기본값이 우선합니다. 따라서 액션 타입의 기본값으로 옮겨 가려면 로컬 재정의(override)를 제거해야 합니다.

**설명**: 우선순위를 정리하면 "애플리케이션에서 넘긴 값 > 액션 타입에 설정한 기본값"입니다. 예를 들어 액션 타입에서 `Type` 파라미터의 기본값을 `A320`으로 정했더라도, 어떤 Workshop 모듈이 이 파라미터에 변수 값 `B737`을 넘기고 있다면 그 모듈에서는 `B737`이 표시됩니다. 그래서 모든 곳에서 액션 타입의 기본값을 쓰게 하려면 각 애플리케이션에 남아 있는 로컬 설정을 지워야 합니다.

> **중간 요약**: Workshop 변수, Object Views 환경 변수, Slate 기본값 같은 로컬 값이 액션 타입의 전역 기본값보다 우선합니다.

<a id="configuring-default-values"></a>
## 기본값 구성하기 (Configuring default values)

아무 파라미터나 선택하면 그 파라미터의 파라미터 구성 화면이 열립니다. 파라미터의 기본값을 고정된 값으로 할지, 객체 파라미터의 속성 값으로 할지 선택합니다.

<a id="static-default-value"></a>
### 정적 기본값 (Static default value)

선택된 `Aircraft` 객체의 `Type` 속성을 `A320`으로 바꾸는 액션 타입을 예로 들어 보겠습니다. 이를 구성하려면 `Type` 파라미터를 클릭해 들어가 정적 기본값을 추가합니다.

![정적 기본값 구성하기](https://www.palantir.com/docs/resources/foundry/action-types/default_value_static_configuration.png)

기본값 없이 비슷한 사용자 경험을 만들려면 이 파라미터를 사용하는 각 애플리케이션에서 입력 값을 따로 구성해야 합니다. 이 동작을 바꾸려면(예: `A380`으로) 여러 애플리케이션에 걸쳐 일일이 수정해야 할 수도 있습니다.

![정적 기본값 예시](https://www.palantir.com/docs/resources/foundry/action-types/default_value_static_example.png)

<a id="object-property-default-values"></a>
### 객체 속성 기본값 (Object property default values)

객체 속성을 파라미터의 기본값으로 설정하려면 먼저 구성할 객체 파라미터를 선택합니다. 좀 더 일반적인 `Change Airplane Details` 액션 타입을 생각해 보겠습니다. 이 액션에서는 사용자가 편집하기 전에 속성의 현재 값을 알아야 합니다. 각 파라미터의 값이 현재 선택된 객체(여기서는 수정할 `Plane` 객체)에서 미리 채워지도록 구성하면 이를 구현할 수 있습니다. 입력 목록에서 해당 파라미터보다 위에 있는 객체 참조 파라미터만 기본값으로 사용할 수 있습니다.

![속성 기본값 구성하기](https://www.palantir.com/docs/resources/foundry/action-types/default_value_object_configuration.png)

Object Explorer에서 `Change Airplane Details` 액션은 현재 값으로 미리 채워집니다. 이 경우 사용자는 속성 하나만 수정하고 나머지는 그대로 둘 수 있습니다. 이 기본값 로직은 액션이 제출되는 모든 곳에서 동일하게 적용됩니다. 액션 사용자가 기본값을 바꾸면 `Lifetime Hours` 값이 편집됨으로 표시됩니다.

![객체 기본값 예시](https://www.palantir.com/docs/resources/foundry/action-types/default_value_object_example.png)

**설명**: "위에 있는 객체 참조 파라미터만 쓸 수 있다"는 제약은 폼이 위에서 아래로 값을 결정하기 때문입니다. 예를 들어 파라미터 순서가 `Plane`(객체 참조), `Type`, `Lifetime Hours`라면, `Type`의 기본값은 `Plane.type`, `Lifetime Hours`의 기본값은 `Plane.lifetime_hours`로 설정할 수 있습니다. 사용자가 `Plane`에서 기체 `N123`을 고르면 `Type`과 `Lifetime Hours`칸에 `N123`의 현재 값이 채워지고, 사용자는 그중 바꾸고 싶은 칸만 고치면 됩니다.

<a id="type-class-prefills"></a>
### 타입 클래스 프리필 (Type class prefills)

액션 파라미터에 타입 클래스(type class)를 주석으로 붙이면, 자동 생성된 UUID나 현재 사용자의 ID 같은 특수한 값으로 미리 채울 수 있습니다. 온톨로지 문서에 [사용 가능한 타입 클래스의 전체 목록](../../02_object-and-link-types/09_metadata/01_metadata-typeclasses.md)이 있습니다.

![타입 클래스 프리필 구성하기](https://www.palantir.com/docs/resources/foundry/action-types/default_value_type_class_configuration.png)

대부분의 경우 사용자가 이 특수한 프리필 값을 직접 바꾸지 않도록 파라미터의 가시성(visibility)을 `hidden`으로 설정해야 합니다.

**설명**: UUID는 무작위로 생성되는 128비트 식별자로, 새 객체의 기본 키를 사용자 입력 없이 만들 때 자주 씁니다. 이런 값은 사용자가 고칠 이유가 없고 고치면 중복 위험이 생기므로 폼에서 숨기는 것이 일반적입니다.

> **중간 요약**: 기본값은 정적 값, 위쪽 객체 참조 파라미터의 속성 값, 타입 클래스 기반 특수 값(UUID, 현재 사용자 ID 등) 중에서 고를 수 있습니다. 특수 값은 보통 숨김 파라미터로 둡니다.

## 정리

- 파라미터 기본값은 액션 타입 수준에서 정해 여러 애플리케이션에 공통으로 적용됩니다.
- 애플리케이션의 로컬 값(Workshop 변수 등)이 전역 기본값보다 우선하므로, 전역 기본값으로 통일하려면 로컬 설정을 지워야 합니다.
- 정적 기본값은 고정 값을, 객체 속성 기본값은 선택된 객체의 현재 속성 값을 채웁니다.
- 타입 클래스 프리필로 UUID나 현재 사용자 ID를 채울 수 있으며, 보통 `hidden`으로 숨깁니다.
