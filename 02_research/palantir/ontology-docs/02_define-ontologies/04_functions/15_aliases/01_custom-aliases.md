# 사용자 정의 별칭 (Custom aliases)

- 원문: https://www.palantir.com/docs/foundry/functions/custom-aliases/
- 사이드바 위치: Define Ontologies > Functions > Aliases > Custom aliases

이 페이지는 함수(function) 코드에서 설정 값을 직접 적지 않고 이름(키)으로 참조할 수 있게 해 주는 사용자 정의 별칭(custom alias)을 다룹니다. 별칭을 정의하고 편집하는 방법, 코드에서 읽는 방법, 그리고 Marketplace로 함수를 배포할 때 설치하는 쪽에서 값을 바꿀 수 있게 하는 방법을 설명합니다. 같은 함수를 개발 환경과 운영 환경처럼 서로 다른 환경에 그대로 옮겨 쓰려면 환경마다 다른 값을 코드 밖으로 빼내야 하는데, 별칭이 그 역할을 합니다.

사용자 정의 별칭은 설정 파라미터, 기능 플래그(feature flag), 환경별 설정 같은 문자열 값을 저장하는 이름 붙은 참조입니다. 값을 하드코딩하는 대신 사용자 정의 별칭을 사용하면 함수 로직을 특정 설정에서 분리할 수 있고, 함수를 여러 환경으로 옮겨 쓸 수 있게(portable) 만들 수 있습니다. 함수에서 언어 모델을 이름으로 참조하려면 [모델 별칭(Model aliases)](02_model-aliases.md)을 참고하세요.

**설명**: 하드코딩이란 `const apiBaseUrl = "https://dev.example.com"`처럼 값을 소스 코드에 직접 써 넣는 것입니다. 이렇게 하면 운영 환경용 값으로 바꿀 때 코드를 수정해야 합니다. 별칭을 쓰면 코드는 `myAlias`라는 키만 알고, 키에 연결된 실제 값(`someValue`)은 저장소 설정이나 설치 시점에 정해집니다. 프로그램에서 환경 변수를 읽는 방식과 목적이 같습니다.

<a id="define-a-custom-alias"></a>
## 사용자 정의 별칭 정의하기 (Define a custom alias)

사용자 정의 별칭을 정의하려면 TypeScript v2 또는 Python 코드 저장소를 열고 다음 단계를 따르세요.

1. **Resource imports** 사이드 패널을 열고 **Platform SDK** 탭을 선택합니다. 사용자 정의 별칭 섹션이 보입니다.

![Platform SDK 탭에 사용자 정의 별칭 옵션이 표시된 Resource imports 사이드 패널.](https://www.palantir.com/docs/resources/foundry/functions/custom-aliases-sidebar.png)

2. **New alias**를 선택해 별칭 생성 대화 상자를 엽니다. 별칭 이름인 **Key**와 그에 연결할 **Value**를 입력한 다음 **Create**를 선택합니다. 별칭 키는 저장소 안에서 유일해야 합니다.

![key가 myAlias, value가 someValue로 설정된 새 별칭 대화 상자.](https://www.palantir.com/docs/resources/foundry/functions/custom-aliases-create.png)

3. 사용자 정의 별칭이 **Custom aliases** 섹션에 나타납니다.

<a id="edit-a-custom-alias"></a>
## 사용자 정의 별칭 편집하기 (Edit a custom alias)

기존 사용자 정의 별칭을 편집하려면 **Platform SDK** 탭의 **Custom aliases** 섹션으로 이동합니다. 별칭 옆의 연필 아이콘을 선택하면 값을 그 자리에서(inline) 편집할 수 있습니다. 점 3개 메뉴를 클릭해 별칭 키를 편집하거나 별칭을 아예 삭제할 수도 있습니다.

![값을 편집하는 옵션과 함께 생성된 별칭이 표시된 사용자 정의 별칭 목록.](https://www.palantir.com/docs/resources/foundry/functions/custom-aliases-edit.png)

> **중간 요약**: 사용자 정의 별칭은 Resource imports 패널의 Platform SDK 탭에서 Key와 Value를 입력해 만들고, 연필 아이콘이나 점 3개 메뉴로 값과 키를 고치거나 삭제합니다. 키는 저장소 안에서 유일해야 합니다.

<a id="use-a-custom-alias-in-code"></a>
## 코드에서 사용자 정의 별칭 사용하기 (Use a custom alias in code)

함수에서 사용자 정의 별칭을 사용하려면 별칭 유틸리티를 import하고 키로 별칭을 참조합니다.

```typescript
import { Aliases } from "@osdk/functions";

export default function getCustomValue(): string {
    return Aliases.custom("myAlias");
}
```

(원문에는 같은 동작을 하는 Python 버전도 있습니다. `functions.aliases`에서 `custom`을 import하고 `@function`을 붙인 `get_custom_value()` 함수에서 `custom("myAlias")`를 반환합니다.)

**설명**: 입력은 없고, 출력은 `myAlias` 키에 연결된 문자열 값입니다. 앞의 예처럼 `myAlias`의 값을 `someValue`로 정의했다면 이 함수는 `"someValue"`를 반환합니다. 핵심 줄은 `Aliases.custom("myAlias")`로, 키를 실행 시점에 실제 값으로 바꿔(resolve) 돌려줍니다.

<a id="use-custom-aliases-with-marketplace"></a>
## Marketplace에서 사용자 정의 별칭 사용하기 (Use custom aliases with Marketplace)

사용자 정의 별칭을 사용하는 함수를 [Marketplace 제품](../07_function-management/03_marketplace-functions.md)에 추가하면, 별칭이 자동으로 **Inputs** 아래에 구성 가능한 파라미터로 나타납니다. 설치하는 사람은 함수 소스 코드를 수정하지 않고도 자기 환경에 맞는 별칭 값을 설정할 수 있습니다.

![함수 출력과 함께 사용자 정의 별칭이 구성 가능한 파라미터 입력으로 표시된 Marketplace 제품.](https://www.palantir.com/docs/resources/foundry/functions/custom-aliases-marketplace-product.png)

**설명**: Marketplace는 Foundry에서 만든 리소스(함수, 객체 타입, 애플리케이션 등)를 묶어 "제품"으로 만들고 다른 환경에 설치할 수 있게 하는 기능입니다. 제품을 만드는 쪽이 별칭을 입력(Inputs)으로 노출하면, 설치하는 쪽이 설치 과정에서 그 값을 채웁니다.

<a id="set-a-description"></a>
### 설명 설정하기 (Set a description)

설치하는 사람이 별칭을 어떻게 구성해야 할지 이해하도록, 별칭 파라미터에 설명(description)을 추가할 수 있습니다. **Inputs** 아래에서 별칭을 선택해 **Details** 패널을 연 다음 **General** 탭에 설명을 입력합니다.

![설명 입력란이 표시된 사용자 정의 별칭 파라미터의 Details 패널.](https://www.palantir.com/docs/resources/foundry/functions/custom-aliases-set-description.png)

<a id="add-presets"></a>
### 프리셋 추가하기 (Add presets)

설치하는 사람이 설치 중에 고를 수 있는 별칭의 프리셋(preset) 값을 정의할 수 있습니다. **Details** 패널에서 **Presets** 탭을 선택하고 **Manual overrides**를 선택해 허용되는 값의 집합을 정의합니다.

![별칭의 프리셋 값이 설정된 수동 재정의 구성을 보여 주는 Presets 탭.](https://www.palantir.com/docs/resources/foundry/functions/custom-aliases-add-presets.png)

<a id="installation-experience"></a>
### 설치 경험 (Installation experience)

설치 중에 설치하는 사람은 별칭 설명을 보고, 프리셋 값 중에서 고르거나 별칭을 직접 구성할 수 있습니다. 설치가 끝나면 함수는 설치하는 사람이 구성한 값으로 별칭을 해석(resolve)합니다.

![설명과 프리셋 값 옵션이 함께 표시된 사용자 정의 별칭 파라미터의 설치 화면.](https://www.palantir.com/docs/resources/foundry/functions/custom-aliases-install.png)

> **중간 요약**: Marketplace 제품에 포함된 함수의 사용자 정의 별칭은 Inputs 파라미터가 됩니다. 제작자는 설명과 프리셋 값을 붙일 수 있고, 설치자는 그 값을 골라 함수 코드를 고치지 않고 환경에 맞춥니다.

## 정리

- 사용자 정의 별칭은 설정 값, 기능 플래그 같은 문자열을 키로 참조하게 해 함수를 환경 간에 옮겨 쓸 수 있게 합니다.
- TypeScript v2 또는 Python 저장소의 Resource imports 패널, Platform SDK 탭에서 만들고 편집합니다.
- 코드에서는 `Aliases.custom("키")`(Python은 `custom("키")`)로 값을 읽습니다.
- Marketplace 제품에서는 별칭이 Inputs 파라미터가 되며, 설명과 프리셋을 붙여 설치자가 값을 정하게 할 수 있습니다.
