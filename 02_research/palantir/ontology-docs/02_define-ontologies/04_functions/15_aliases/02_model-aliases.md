# 모델 별칭 (Model aliases)

- 원문: https://www.palantir.com/docs/foundry/functions/model-aliases/
- 사이드바 위치: Define Ontologies > Functions > Aliases > Model aliases

이 페이지는 TypeScript v2와 Python 함수(function)에서 언어 모델을 이름으로 참조하게 해 주는 모델 별칭(model alias)을 다룹니다. 모델을 가져오면서 별칭을 정하는 절차와, 코드에서 별칭을 모델 RID로 바꿔 쓰는 방법, Marketplace에서의 제약을 설명합니다.

모델 별칭은 언어 모델에 대한 이름 붙은 참조로, 코드에서 언어 모델을 편리하게 참조하는 방법을 제공합니다.

함수에서 언어 모델을 사용하는 전체 과정은 [TypeScript v2 및 Python 함수에서 언어 모델 사용하기](../14_models/03_language-models-python-tsv2.md)를 참고하세요.

**설명**: Foundry의 리소스는 RID(Resource Identifier)라는 긴 고유 식별자 문자열로 구분됩니다. 코드에 RID를 그대로 적으면 읽기 어렵고 바꾸기도 번거롭습니다. 모델 별칭은 `gpt5Nano`처럼 사람이 읽기 쉬운 키를 모델 RID에 연결해 두는 장치입니다.

<a id="define-a-model-alias"></a>
## 모델 별칭 정의하기 (Define a model alias)

모델 별칭을 정의하려면 TypeScript v2 또는 Python 코드 저장소를 열고 다음 단계를 따르세요.

1. **Resource imports** 패널에서 **Platform SDK** 탭을 엽니다.

![TypeScript v2 저장소에서 Platform SDK 리소스에 접근하는 탭.](https://www.palantir.com/docs/resources/foundry/functions/platform-sdk-tab.png)

2. 새 언어 모델을 가져오려면 오른쪽 위에서 **Add > Models**를 선택합니다. 사용할 수 있는 Palantir 제공 모델과 등록된(registered) 모델을 볼 수 있는 창이 열립니다.

![TypeScript v2 저장소의 모델 가져오기 대화 상자.](https://www.palantir.com/docs/resources/foundry/functions/models-v3-import-dialog.png)

3. 가져올 모델을 선택한 다음 **Confirm selection**을 선택합니다. 선택한 각 모델의 별칭을 구성할 수 있는 구성 대화 상자가 열립니다. 별칭 옆의 연필 아이콘을 선택해 편집하거나, 기본값을 그대로 둘 수 있습니다. 별칭 키는 저장소 안에서 유일해야 합니다.

![가져올 모델을 고른 뒤 모델 별칭을 구성하는 화면.](https://www.palantir.com/docs/resources/foundry/functions/configure-models-aliases.png)

4. 가져온 모델은 **Resource imports** 사이드 패널의 **Platform SDK** 탭에 나타납니다. 별칭 옆의 연필 아이콘을 선택하면 어떤 별칭이든 그 자리에서 편집할 수 있습니다.

![모델 별칭을 그 자리에서 구성하는 화면.](https://www.palantir.com/docs/resources/foundry/functions/inline-models-aliases-edit.png)

> **중간 요약**: Platform SDK 탭에서 Add > Models로 모델을 가져오면 모델마다 별칭을 정하는 대화 상자가 열립니다. 별칭 키는 저장소 안에서 유일해야 하며 나중에 연필 아이콘으로 고칠 수 있습니다.

<a id="use-a-model-alias-in-code"></a>
## 코드에서 모델 별칭 사용하기 (Use a model alias in code)

함수에서 모델 별칭을 사용하려면 별칭 유틸리티를 import하고 이름으로 별칭을 참조합니다. 별칭은 모델 클라이언트에 전달할 수 있는 모델 RID로 해석(resolve)됩니다.

```typescript
import { Aliases } from "@osdk/functions";

const modelRid = Aliases.model("gpt5Nano").rid;
```

(원문에는 Python 버전도 있습니다. `functions.aliases`에서 `model`을 import하고 `model("gpt5Nano").rid`로 RID를 얻습니다.)

**설명**: `Aliases.model("gpt5Nano")`는 `gpt5Nano` 키에 연결된 모델 정보를 돌려주고, `.rid`로 그 모델의 RID 문자열을 꺼냅니다. 이 코드 자체는 모델을 호출하지 않습니다. 얻은 RID를 모델 클라이언트에 넘겨야 실제로 모델을 호출합니다.

별칭으로 언어 모델을 호출하는 완전한 예는 [언어 모델을 사용하는 함수 작성하기](../14_models/03_language-models-python-tsv2.md#write-a-function-that-uses-a-language-model)를 참고하세요.

**주의**: 모델 별칭은 [Marketplace 제품](../07_function-management/03_marketplace-functions.md)에 추가된 함수에서도 동작하지만, 설치 중에 다른 모델로 다시 매핑(remap)할 수는 없습니다. 별칭이 참조하는 모델이 대상 환경에서 사용할 수 없으면, 함수는 런타임에 별칭을 해석하지 못하고 실패합니다.

<a id="related"></a>
## 관련 문서 (Related)

설정 파라미터, 기능 플래그, 환경별 설정 같은 문자열 값에 대해서는 [사용자 정의 별칭](01_custom-aliases.md)을 정의할 수도 있습니다. 사용자 정의 별칭은 **Platform SDK** 탭에 나타나며, 함수를 여러 환경으로 옮겨 쓸 수 있게 만들어 줍니다.

## 정리

- 모델 별칭은 언어 모델의 RID에 읽기 쉬운 이름을 붙인 참조입니다.
- TypeScript v2 또는 Python 저장소의 Platform SDK 탭에서 모델을 가져올 때 별칭을 정하고, 나중에 편집할 수 있습니다.
- 코드에서는 `Aliases.model("키").rid`(Python은 `model("키").rid`)로 RID를 얻어 모델 클라이언트에 전달합니다.
- Marketplace 설치 시 모델 별칭은 다시 매핑할 수 없으므로, 대상 환경에 같은 모델이 없으면 런타임에 실패합니다.
