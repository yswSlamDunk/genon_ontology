# 파라미터 구성 재정의 (Override parameter configurations)

- 원문: https://www.palantir.com/docs/foundry/action-types/parameters-override/
- 사이드바 위치: Define Ontologies > Action types > Parameters > Override parameter configurations

이 페이지는 특정 조건에서 파라미터의 동작과 설정을 바꾸는 재정의(override)를 설명합니다. 재정의를 쓰면 "관리자에게는 사유 입력을 필수로, 담당자에게는 숨김으로"처럼 사용자나 입력값에 따라 폼을 다르게 만들 수 있어, 거의 같은 액션 타입을 여러 개 만들 필요가 줄어듭니다.

<a id="add-and-edit-overrides"></a><a id="overrides"></a>
## 재정의 (Overrides)

재정의는 특정 상황에서 파라미터의 동작과 구성을 바꾸는 데 사용합니다. 재정의를 사용하면 파라미터와 폼이 더 유연해지므로, 사소한 차이만 있는 별도의 액션 타입을 따로 구성할 필요가 없어집니다. 재정의를 적절히 사용하면 사용자가 액션을 제출하는 과정을 안내해 사용자 경험을 개선할 수 있습니다.

예를 들어 지원 티켓 객체의 상태를 바꾸는 액션 타입이 있고, 액션 제출을 관리자와 담당자로 제한하려 한다고 합시다. 담당자는 상태를 그냥 바꿀 수 있지만, 관리자는 사유를 제공해야 합니다. 재정의를 사용하면 `Justification reason` 파라미터를 관리자에게는 필수이면서 보이도록, 담당자에게는 숨겨지고 선택 사항이 되도록 만들 수 있습니다.

<a id="add-and-edit-overrides"></a><a id="override-block"></a>
## 재정의 추가와 편집 (Add and edit overrides)

재정의는 파라미터 화면의 여러 곳에서 추가하고 편집할 수 있습니다. 새 재정의를 추가하는 가장 쉬운 방법은 **General** 섹션의 **Value** 탭에서 바로 추가하는 것입니다. 세 가지 옵션 중 하나에서 **Add override**를 클릭하면 팝업으로 재정의를 쉽게 만들 수 있으며, 이 팝업은 선택한 옵션을 기준으로 재정의를 자동으로 구성해 줍니다. **General** 섹션에는 각 옵션에 재정의가 이미 구성되어 있는지, 몇 개가 구성되어 있는지도 표시됩니다. 기존 재정의를 편집하려면 재정의 버튼을 선택합니다.

![재정의 팝업](https://www.palantir.com/docs/resources/foundry/action-types/override_pop_up.png)

**Overrides** 탭에서 재정의를 직접 추가할 수도 있습니다. Overrides 탭은 해당 파라미터에 구성된 모든 재정의의 개요를 보여 줍니다. 여기서 재정의 블록을 추가하거나, 기존 블록에 새 조건이나 재정의를 추가할 수 있습니다.

![재정의 탭](https://www.palantir.com/docs/resources/foundry/action-types/override_tab.png)

> **중간 요약**: 재정의는 General 섹션의 Value 탭에서 팝업으로 빠르게 추가하거나, Overrides 탭에서 블록 단위로 직접 관리할 수 있습니다.

<a id="if-and-conditions"></a><a id="override-block"></a>
## 재정의 블록 (Override block)

재정의 블록은 재정의의 기본 단위입니다. 블록은 조건("if" 부분에 표시)과 재정의("then" 부분에 표시)를 함께 정의합니다. 각 블록의 머리글에는 로직의 요약이 표시됩니다. 파라미터마다 여러 재정의 블록을 둘 수 있지만, 둘 이상이 참이면 첫 번째 블록만 실행됩니다.

![재정의 블록](https://www.palantir.com/docs/resources/foundry/action-types/override_block.png)

<a id="if-and-conditions"></a><a id="then-and-overrides"></a>
### "If"와 조건 ("If" and conditions)

각 블록에는 조건이 하나 이상 들어갈 수 있습니다. 조건과 그 구성 방법은 [제출 조건 문서의 조건 부분](../08_submission-criteria.md#conditions)을 참고하세요. 재정의 조건과 제출 조건(submission criteria)의 조건 사이의 유일한 차이는, 재정의 조건에서는 폼 계층에서 현재 파라미터보다 위에 있는 파라미터만 참조할 수 있다는 점입니다.

<a id="multiple-override-blocks"></a><a id="then-and-overrides"></a>
### "Then"과 재정의 ("Then" and overrides)

**Then** 섹션은 블록의 조건이 충족될 때 적용될 재정의를 정의합니다. 각 블록의 **Then** 섹션에는 여러 재정의를 둘 수 있으며, 이들은 모두 함께 적용됩니다. 재정의는 파라미터의 제약(constraints), 가시성(visibility), 필수 여부(requiredness), 기본값 설정을 바꿀 수 있습니다. 재정의가 파라미터에 이미 설정된 기본값과 같은 값을 갖도록 구성되면 재정의 자체에 경고가 표시됩니다.

<a id="multiple-override-blocks"></a>
### 여러 재정의 블록 (Multiple override blocks)

하나의 파라미터에 여러 재정의 블록을 추가할 수 있습니다. 둘 이상의 블록이 참이면 첫 번째 재정의만 실행됩니다.

**설명**: 재정의 블록 목록은 `if / else if / else if ...` 연쇄 조건문과 같은 방식으로 평가됩니다. 앞의 예시를 코드로 쓰면 다음과 같습니다.

```text
// Justification reason 파라미터의 기본 설정: hidden, optional
if (현재 사용자가 Managers 그룹에 속함) {
    visibility = visible
    required = true
}
```

블록이 여러 개라면 위에서부터 검사해 처음으로 참이 되는 블록의 Then 부분만 적용하고, 어느 블록도 참이 아니면 파라미터의 기본 설정이 그대로 쓰입니다. 블록의 순서가 결과를 바꿀 수 있으므로 더 구체적인 조건을 위쪽에 두는 것이 안전합니다.

> **중간 요약**: 재정의 블록은 "if 조건이면 then 설정 변경" 구조이며, 여러 블록 중 처음으로 참이 된 블록 하나만 적용됩니다. 조건에서는 현재 파라미터보다 위에 있는 파라미터만 참조할 수 있고, Then에서는 제약, 가시성, 필수 여부, 기본값을 바꿀 수 있습니다.

## 정리

- 재정의는 조건에 따라 파라미터의 설정을 바꿔, 비슷한 액션 타입을 여러 개 만들지 않아도 되게 합니다.
- 재정의는 Value 탭의 **Add override** 팝업이나 **Overrides** 탭에서 추가하고 편집합니다.
- 재정의 블록은 조건(If)과 재정의(Then)로 이루어지며, 조건 작성법은 제출 조건과 같지만 위쪽 파라미터만 참조할 수 있습니다.
- Then에서는 제약, 가시성, 필수 여부, 기본값을 함께 바꿀 수 있습니다.
- 여러 블록이 참이면 첫 번째 블록만 적용됩니다.
