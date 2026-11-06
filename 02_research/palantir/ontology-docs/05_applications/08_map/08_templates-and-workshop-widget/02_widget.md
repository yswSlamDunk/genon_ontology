# Workshop 모듈에 지도 템플릿 임베드하기 (Embed a Map template in a Workshop module)

- 원문: https://www.palantir.com/docs/foundry/map/widget/
- 사이드바 위치: Applications > Map > Templates and Workshop widget > Embed a Map template in a Workshop module

이 페이지는 지도 템플릿을 Workshop 모듈 안의 Map 위젯으로 임베드하고, Workshop 변수로 템플릿 파라미터를 채우는 방법을 다룹니다. 위젯을 추가하고 리소스를 고른 다음, 레이어, 상호작용(interaction), 인터페이스 각 영역의 설정 항목을 하나씩 설명합니다. 지도를 단독 앱이 아니라 업무용 Workshop 화면의 일부로 넣어 다른 위젯과 선택 상태를 주고받게 하려면 이 설정이 필요합니다.

[지도 템플릿](01_templates.md)은 Workshop 모듈에 임베드할 수 있습니다. 템플릿의 파라미터 값은 Workshop 변수에서 직접 전달할 수 있습니다.

**설명**: Workshop 변수는 모듈 안에서 위젯끼리 값을 주고받는 저장소입니다. 예를 들어 표 위젯에서 사용자가 공항 한 행을 클릭하면 그 공항 객체가 `selectedAirport` 변수에 들어가고, 이 변수를 지도 템플릿의 객체 파라미터에 연결하면 클릭할 때마다 그 공항에 대한 지도가 생성됩니다.

지도 템플릿을 Workshop 모듈에 임베드하는 단계는 세 가지입니다.

1. [Workshop에 Map 위젯 추가하기](#add-a-map-widget-in-workshop)
2. [리소스 선택하기](#choose-a-resource)
3. [위젯 설정하기](#configure-the-widget)

<a id="add-a-map-widget-in-workshop"></a>
## Workshop에 Map 위젯 추가하기 (Add a Map widget in Workshop)

Workshop 모듈에서 원하는 섹션의 **+** 아이콘 또는 **+ Add widget**을 선택해 위젯 메뉴를 열고, [Map 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-map/)을 검색합니다.

<a id="choose-a-resource"></a>
## 리소스 선택하기 (Choose a resource)

위젯 편집기의 **Layers** 섹션에서 기본값인 **Local configuration** 대신 **Import map template**을 선택합니다. **Resource** 설정에서 **Select**를 선택하면 호환되는 리소스 목록이 나타나며, 여기서 임베드할 지도 템플릿 리소스를 선택합니다.

> **중간 요약**: Workshop 섹션에 Map 위젯을 추가하고, **Layers** 섹션에서 **Import map template**을 고른 뒤 **Resource**에서 임베드할 템플릿을 선택합니다.

<a id="configure-the-widget"></a>
## 위젯 설정하기 (Configure the widget)

**Map** 위젯의 설정 옵션은 대부분 로컬 설정(local configuration)과 임베드된 템플릿에서 동일합니다. 일반 설정은 [Map 위젯 문서](https://www.palantir.com/docs/foundry/workshop/widgets-map/#interactions)를 참고하세요. 일부 위젯 설정은 임베드된 템플릿 설정에만 적용됩니다.

* **Layers**
  * **Resource:** 임베드할 지도 템플릿 리소스를 선택합니다. 선택적으로 **Override map RID**를 지정할 수 있습니다. 이를 지정하면 템플릿과 그 파라미터로 생성되는 기본 지도 대신 기존 지도가 표시됩니다. 이를 이용하면 객체 속성(property)에 저장된 RID로 기존 지도를 불러오는 등의 동작을 할 수 있습니다.
  * **Parameters:** Workshop 변수를 사용해 템플릿 파라미터에 값을 제공합니다.
  * **Refresh key:** 이 변수의 값이 바뀔 때마다 위젯이 지도를 완전히 다시 불러옵니다.
  * **Base layer picker:** 기본 배경 지도 이미지를 제어합니다. **Show base layer picker** 토글을 켜면 사용자가 Map 위젯 화면에서 배경 지도를 바꿀 수 있습니다.
  * **Load data from scenario:** 기본 온톨로지 대신 시나리오를 사용해 주어진 리소스를 불러옵니다.
  * **Regenerate map after applying scenario:** 설정하면 시나리오가 수정될 때마다 지도가 새로 고쳐집니다.

**설명**: 시나리오는 실제 온톨로지 데이터를 바꾸지 않고 "만약 이 편집(edit)을 적용한다면"이라는 가정 상태를 따로 만들어 두는 기능입니다. **Load data from scenario**를 켜면 지도가 실제 데이터 대신 그 가정 상태의 데이터를 보여 줍니다. **Override map RID**는 예를 들어 `Incident` 객체마다 `map_rid` 속성에 담당자가 저장해 둔 지도의 RID가 있을 때, 선택된 사건의 그 지도를 그대로 띄우는 용도로 쓸 수 있습니다.

* **Interaction**
  * **Selected objects:** 현재 선택된 객체들의 객체 집합(object set)을 출력합니다. 이 객체 집합은 현재 모듈의 하위(downstream) 위젯에서 사용할 수 있습니다.
  * **On selected objects change:** 지도에서 선택된 객체가 바뀔 때 실행될 Workshop 이벤트를 설정합니다. 예를 들어 선택한 객체의 상세 화면을 담은 서랍(drawer)을 여는 트리거를 둘 수 있습니다.
  * **All visible objects on map:** 현재 지도에 보이는 객체들의 객체 집합을 출력합니다.
  * **Available actions:** 위젯에서 제출할 수 있는 액션을 제어합니다. **Some** 옵션을 선택하면 사용 가능한 액션을 직접 지정할 수 있으며, 모듈 변수를 파라미터 기본값으로 활용하는 액션 설정도 함께 지정할 수 있습니다.
  * **On selected action application:** 위젯 안에서 어떤 액션이든 성공적으로 적용되었을 때 실행될 Workshop 이벤트를 설정합니다.

> **중간 요약**: **Layers** 영역은 어떤 템플릿 또는 기존 지도를 어떤 파라미터, 시나리오로 불러올지 정하고, **Interaction** 영역은 선택 객체와 보이는 객체를 변수로 내보내며 선택 변경이나 액션 적용 시 이벤트를 실행하게 합니다.

* **Interface**
  * **Show layers panel:** Map 위젯 화면 안에 레이어 패널을 표시합니다.
  * **Show histogram:** 객체 타입이나 속성으로 지도를 필터링할 수 있는 히스토그램 패널을 표시합니다.
  * **Show series panel:** 지도 화면 아래쪽에 시리즈 패널을 표시합니다.
  * **Incomplete inputs message:** 필수 입력이 빠져 지도 템플릿을 실행할 수 없을 때 사용자에게 대화 상자로 보여 줄 메시지입니다.
  * **Enable image export to clipboard:** 사용자가 지도 이미지를 클립보드로 내보낼 수 있게 합니다.
  * **Filter rendered objects:** 설정하면 사용자가 **Object set filter** 변수를 통해 지도에 표시되는 객체를 필터링할 수 있습니다.
  * **Saving settings:** 사용자가 현재 지도를 저장할 수 있게 하려면 활성화합니다.
    * 임베드된 리소스가 지도 템플릿이면, 저장하면 새 지도 리소스가 생성됩니다.
      * 이 지도는 **Default resource name**에 지정된 이름이 붙고 **Default folder**에 지정된 폴더에 놓입니다. **Show resource dialog**가 활성화되어 있으면 사용자에게 리소스 이름과 위치를 고르라는 안내가 나타나며, 리소스 대화 상자에는 설정된 이름과 폴더가 시작값으로 표시됩니다.
      * 지도가 성공적으로 생성되면 **On create new map**에 정의된 이벤트나 온톨로지 액션(또는 둘 다)이 실행됩니다. 생성된 지도의 RID를 액션 파라미터의 입력으로 쓰고 싶다면, 파라미터 입력 선택기에서 특수 옵션인 **Saved map RID**를 사용합니다. 사용자에게 액션 양식이 표시되지 않으므로, 모든 필수 파라미터는 정해진 기본값으로 설정되어 있어야 합니다.
    * 임베드된 리소스가 지도이면, 저장해도 새 리소스를 만들지 않고 임베드된 지도 리소스를 업데이트합니다.

**설명**: **Saving settings**의 흐름을 순서대로 보면 다음과 같습니다. (1) 사용자가 템플릿으로 생성된 지도에서 저장을 누릅니다. (2) 새 지도 리소스가 지정된 폴더에 만들어집니다. (3) **On create new map**에 연결한 액션이 실행되며, 예를 들어 "현재 `Incident` 객체의 `map_rid` 속성에 **Saved map RID** 값을 기록"하는 액션을 두면 나중에 위의 **Override map RID**로 그 지도를 다시 불러올 수 있습니다. 이때 사용자가 값을 입력할 양식이 뜨지 않으므로 액션의 필수 파라미터는 모두 기본값이 있어야 합니다.

**주의**: 이전에는 지도 템플릿에 정의된 모든 필수 객체 타입을 담은 단일 입력 객체 집합 변수 하나로 템플릿 입력을 제공했습니다. 이 방식은 비객체 파라미터가 없고 객체 타입마다 객체 파라미터가 하나뿐인 템플릿에서만 동작하므로 이제는 권장하지 않습니다. 그래도 이 기능을 쓰고 싶다면 **Use legacy input object set** 체크박스를 선택하고 객체 집합 변수를 제공하세요.

> **중간 요약**: **Interface** 영역은 패널 표시, 미완성 입력 메시지, 이미지 내보내기, 표시 객체 필터, 저장 동작을 정합니다. 템플릿을 저장하면 새 지도가 만들어지고 후속 액션을 실행할 수 있으며, 단일 입력 객체 집합 방식은 레거시로 권장되지 않습니다.

## 정리

- 지도 템플릿은 Workshop의 Map 위젯에서 **Import map template**으로 임베드하며, 파라미터는 Workshop 변수로 채웁니다.
- **Layers** 설정에는 리소스와 **Override map RID**, 파라미터, 새로고침 키, 배경 지도 선택기, 시나리오 관련 옵션이 있습니다.
- **Interaction** 설정으로 선택 객체와 보이는 객체를 객체 집합으로 내보내고, 선택 변경과 액션 적용에 이벤트를 연결합니다.
- **Interface** 설정으로 패널과 저장 동작을 정하며, 템플릿을 저장하면 새 지도가 생기고 **Saved map RID**를 액션에 넘길 수 있습니다.
- 단일 입력 객체 집합으로 입력을 넘기는 레거시 방식은 제약이 있어 권장되지 않습니다.
