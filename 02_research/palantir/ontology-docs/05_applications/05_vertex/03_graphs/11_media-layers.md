# 미디어 레이어와 이미지 주석 (Media layers and image annotations)

- 원문: https://www.palantir.com/docs/foundry/vertex/media-layers/
- 사이드바 위치: Applications > Vertex > Graphs > Media layers and image annotations

이 페이지는 Vertex 그래프에서 이미지(미디어) 위에 객체를 겹쳐 표시하고, 이미지의 특정 영역에 주석(annotation)을 달아 그것을 다시 온톨로지 객체로 저장하는 방법을 다룹니다. 예제는 군함 설계 도면 이미지 위에 선실 위치를 표시하는 과정을 따라가며, Pipeline Builder에서 데이터를 준비하고 Ontology Manager에서 기본 동작을 설정한 뒤 Vertex에서 주석을 만들고 고치는 순서로 진행됩니다. 이미지 속 좌표가 객체의 속성 값으로 저장되고 액션 타입을 통해 수정된다는 점이 핵심입니다.

Vertex의 미디어 레이어(media layer)를 사용하면 지도나 이미지 위에 객체를 시각화하고 주석을 달 수 있어, 데이터에 대한 공간적 분석과 맥락적 이해가 가능해집니다. 객체를 오버레이로 추가하고, 속성(property)을 기준으로 필터링하고, 상호작용 가능한 주석을 만들 수 있습니다.

이 문서 섹션에서는 [Wikimedia Commons의 퍼블릭 도메인 이미지 ↗](https://commons.wikimedia.org/wiki/File:%22B%22_Deck_and_%22C%22_Deck_Plans_-_General_Edwin_D._Patrick,_Suisun_Bay_Reserve_Fleet,_Benicia,_Solano_County,_CA_HAER_CA-344_\(sheet_6_of_8\).png)를 예제로 사용하여, Vertex에서 설계 도면 위에 객체를 겹쳐 제2차 세계대전 시대 군함을 개념적으로 구성해 봅니다.

이 예제를 마치면 이미지 위에 몇 개의 선실을 표시한 주석이 겹쳐진, 상호작용 가능한 함선 도면을 Vertex에서 갖게 됩니다.

![미디어 참조와 이미지 주석을 사용한 Vertex 그래프 예제의 최종 결과.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-end-result.png)

<a id="configuration"></a>
## 구성 (Configuration)

<a id="pipeline-builder-configuration"></a>
### Pipeline Builder 구성

Vertex에서 미디어를 사용하려면 먼저 [미디어 참조(media reference)](https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-overview/#media-references)를 가진 객체 타입이 최소 하나 있어야 합니다. 이 예제에서는 이미지 미디어 셋(media set)으로 만든 객체 타입 하나를 사용합니다. 또한 Vertex 그래프에서 주석을 만드는 데 사용할 객체 타입 두 개가 있습니다.

아래 Pipeline Builder 그래프에서 `Wikipedia commons...` 미디어 셋은 `[Ships] Ship diagram` 객체 타입을 출력합니다. `Text - Ship annotations` 데이터셋은 `[Ship] Text Annotations` 객체 타입을 출력합니다. 마지막으로 `Ship annotations` 데이터셋은 `[Ships] Annotation` 객체 타입을 출력합니다.

![객체 타입을 출력하는 데이터셋과 미디어 셋을 보여 주는 Pipeline Builder 그래프.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-ontology-overview.png)

`Wikipedia commons...` 미디어 셋을 선택하면 미리보기 패널에서 이 미디어 셋을 구성하는 개별 PNG 이미지를 볼 수 있습니다.

![예제 미디어 셋에 있는 PNG 이미지 미리보기.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-media-example-data.png)

`[Ships] Ship diagram` 객체 타입을 선택하면 이미지 미디어 참조와 RID의 미리보기가 표시됩니다.

![이미지 미디어 참조와 RID가 담긴 미디어 셋 미리보기.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-diagram-example-data.png)

같은 노드를 더블클릭하면 소스 데이터셋의 열에서 파생된 `[Ships] Ship diagram` 객체 타입의 속성을 볼 수 있습니다.

![Ontology Manager에서 본 Ship diagram 객체 타입의 속성.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-diagram-properties.png)

`[Ships] Annotation` 객체 타입을 선택하면 소스 데이터셋의 미리보기를 볼 수 있으며, 여기에는 `annotation`, `coordinates`, `hexcolor` 열이 있습니다.

![주석 데이터셋 미리보기.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-annotation-example-data.png)

같은 노드를 더블클릭하면 소스 데이터셋의 열에서 파생된 `[Ships] Annotation` 객체 타입의 속성이 표시됩니다.

![Ontology Manager에서 본 주석 객체 타입의 속성.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-ship-annotation-properties.png)

`Annotation`과 `Text annotation` 객체 타입은 `File Name` [외래 키 속성(foreign key property)](../../../02_define-ontologies/02_object-and-link-types/06_link-types/02_create-link-type.md#foreign-key-relationship-type)으로 관련된 `Ship diagram` 객체 타입에 링크했습니다.

![Pipeline Builder에서의 링크 타입 외래 키 구성.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-link-key.png)

**설명**: 미디어 참조는 이미지 파일 자체를 속성에 넣는 것이 아니라, 미디어 셋 안에 저장된 파일을 가리키는 식별자를 속성 값으로 갖는 방식입니다. 이 예제의 데이터 구성을 테이블로 표현하면 다음과 같습니다(값은 설명을 위한 가상의 예시입니다).

| 테이블 | File Name | 그 밖의 열 |
|---|---|---|
| Ship diagram | `deck_b.png` | 이미지 미디어 참조 |
| Annotation | `deck_b.png` | annotation=`Linen locker`, coordinates=사각형 좌표, hexcolor=`#FF0000` |
| Annotation | `deck_b.png` | annotation=`Galley`, coordinates=사각형 좌표, hexcolor=`#00FF00` |

Annotation 테이블의 `File Name`이 Ship diagram 테이블의 `File Name`을 가리키므로, SQL로 치면 `annotation JOIN ship_diagram ON annotation.file_name = ship_diagram.file_name` 관계입니다. 이 관계를 링크 타입으로 정의해 두었기 때문에 Vertex는 어떤 주석이 어떤 도면 이미지에 속하는지 알 수 있습니다.

이제 미디어 기반 객체 타입과 주석 객체 타입 사이의 관계를 이해했으므로, Ontology Manager에서 구성을 이어 가며 이 객체 타입들을 Vertex 그래프에서 사용할 때의 기본 동작을 설정할 수 있습니다.

<a id="ontology-manager-configuration"></a>
### Ontology Manager 구성

Ontology Manager에서 미디어 기반 객체 타입으로 이동합니다. **Capabilities** 탭에서 미디어 레이어의 기본 이미지로 사용할 이미지 참조를 고릅니다. **Image reference property** 드롭다운 메뉴에서 옵션을 선택합니다.

![Ontology Manager에서 Ship 객체 타입의 미디어 참조 구성.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-config-ship-diagram.png)

이제 `Annotation` 객체 타입이 Vertex에서 사용될 때의 동작을 정의하도록 구성할 수 있습니다.

![Ontology Manager의 Annotation 객체 타입 개요 페이지.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-oma-annotation.png)

개요 페이지에서 `Annotation` 객체 타입에 사용하려고 만든 두 개의 [액션 타입](../../../02_define-ontologies/03_action-types/01_overview.md), `Create [Ships] Annotation`과 `Edit annotation coordinates`를 볼 수 있습니다. Vertex 그래프에서 이 액션 타입들을 사용해 이미지 주석을 만들거나 편집할 수 있습니다.

![Ontology Manager에서 Annotation 객체 타입에 연결된 액션 타입.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-oma-annotation-action-types.png)

액션 타입을 선택하면 그 개요 페이지가 열립니다. 예를 들어 `Create [Ships] Annotation` 액션 타입은 실행될 때 `Annotation name`, `Coordinates`, `Hexcolor`, `File Name` 속성을 사용하도록 설정되어 있음을 알 수 있습니다.

![Ontology Manager에서 주석 생성 액션 타입의 구성.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-oma-create-annotation-action.png)

객체 타입의 속성 중 어느 것을 이미지 주석의 픽셀 공간 경계 상자(pixel space bounding box) 좌표로 기본 사용할지 구성할 수 있습니다. 같은 **Capabilities** 탭의 **Image annotation coordinate property** 드롭다운 메뉴에서 사용 가능한 속성 중 하나를 고릅니다. 이 예제에서는 `Coordinates` 속성을 선택합니다.

![Ontology Manager에서 Ship 객체 타입의 좌표 속성 구성.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-config-annotation.png)

**설명**: 픽셀 공간 경계 상자는 이미지의 픽셀 좌표계(보통 왼쪽 위가 원점)에서 주석 영역을 둘러싸는 사각형을 뜻합니다. 예를 들어 가로 2000픽셀, 세로 1000픽셀 도면에서 x=400\~520, y=200\~260 범위의 사각형이 "Linen locker" 선실 위치라면, 그 사각형을 나타내는 좌표 값이 `Coordinates` 속성에 저장됩니다. 좌표를 저장하는 구체적인 문자열 형식은 원문에 나와 있지 않습니다.

> **중간 요약**: 미디어 레이어를 쓰려면 미디어 참조 속성을 가진 객체 타입과, 그 객체 타입에 외래 키로 링크된 주석 객체 타입이 필요합니다. Ontology Manager의 **Capabilities** 탭에서 기본 이미지 참조 속성과 주석 좌표 속성을 지정하고, 주석을 만들고 고칠 액션 타입을 준비해 둡니다.

<a id="add-objects-as-media-layers"></a>
## 객체를 미디어 레이어로 추가하기 (Add objects as media layers)

Ontology Manager에서 구성을 확인했다면 Vertex 그래프에 객체를 추가할 수 있습니다. **+ Add object**를 선택해 객체 검색 화면을 엽니다.

![Vertex 그래프에 객체 추가하기.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-add-object.png)

이름, 타입, 그 밖의 식별 속성으로 검색할 수 있습니다. 드롭다운 메뉴를 사용해 미디어 참조를 가진 객체 타입만 보이도록 필터링할 수도 있습니다.

![Vertex 그래프에 객체를 추가하는 검색 대화 상자.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-search-dialog.png)

대화 상자 오른쪽 아래의 드롭다운 메뉴로 객체를 Vertex에 어떤 방식으로 추가할지 지정합니다. **Object**가 기본 옵션이며, Ontology Manager에서 객체 타입에 구성된 아이콘과 색상으로 객체를 그래프에 추가합니다. 객체에 주석을 추가하고 보려면 **Object with media** 옵션을 고릅니다.

![객체가 Vertex에 어떻게 표시될지 선택하기.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-filter-object.png)

Vertex에 추가할 객체를 모두 골랐으면 **Add all** 또는 **+ Add selected**를 선택해 그래프에 추가합니다. 추가된 객체는 미디어 레이어로 표시됩니다.

![선택한 객체를 Vertex 그래프에 추가하기.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-add-to-graph.png)

> **중간 요약**: **+ Add object**로 객체를 검색한 뒤 추가 방식을 **Object with media**로 고르면, 객체가 아이콘이 아니라 이미지(미디어 레이어)로 그래프에 올라가고 주석을 다룰 수 있게 됩니다.

<a id="style-and-explore-media-layers"></a>
## 미디어 레이어 스타일 지정과 탐색 (Style and explore media layers)

[Ontology Manager에서 따로 구성하지 않았다면](#ontology-manager-configuration), 미디어 레이어는 기본적으로 첫 번째 미디어 참조를 사용해 객체를 표시합니다. 하지만 왼쪽 **Layers** 패널에서 여는 아이콘 스타일 옵션으로 미디어 레이어 객체의 시각적 모양을 직접 바꿀 수도 있습니다. 표시하려는 객체에 미디어 참조가 여러 개 있으면 어느 것을 사용할지 고를 수 있습니다.

![Vertex 미디어 레이어에서 객체에 사용할 아이콘 수정하기.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-style-icon.png)

그래프에서 마우스 오른쪽 버튼을 눌러 Search Around 기능을 사용하면, 관련 객체를 탐색하고 연결된 데이터로 미디어 레이어 시각화를 확장할 수 있습니다.

![Vertex 그래프의 Search Around 기능.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-search-around.png)

**설명**: Search Around는 선택한 객체에서 링크를 따라 연결된 객체를 찾아 그래프에 추가하는 기능입니다. 이 예제에서는 Ship diagram 객체에서 Search Around를 실행하면, `File Name` 링크로 연결된 Annotation 객체들을 찾아 올 수 있습니다.

Ontology Manager에서 객체에 대해 [이미지 주석 좌표 속성을 구성](#ontology-manager-configuration)하지 않았다면, 스타일 옵션에서 이미지 주석의 픽셀 공간 경계 상자 좌표로 사용할 속성을 직접 고를 수도 있습니다.

![Vertex에서 미디어의 픽셀 공간 경계 상자 좌표 구성하기.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-bounding-box.png)

미디어 레이어 안의 객체를 선택하면 그 속성을 보고 상호작용할 수 있습니다. 선택한 객체가 강조 표시되고 관련 정보가 나타납니다.

![Vertex 미디어 레이어에서 선택된 객체.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-selected-object.png)

주석 레이어 스타일 메뉴에서 채우기 색과 윤곽선 색 등 주석의 스타일을 지정합니다.

![미디어 레이어에서 주석의 채우기 색 수정하기.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-style-option.png)

![스타일을 수정한 뒤의 이미지 주석.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-style-result.png)

> **중간 요약**: 미디어 레이어는 기본적으로 첫 번째 미디어 참조를 표시하지만, **Layers** 패널에서 사용할 미디어 참조, 주석 좌표 속성, 주석의 색 등을 바꿀 수 있습니다. Search Around로 링크된 주석 객체를 함께 불러올 수 있습니다.

<a id="create-image-annotations"></a>
## 이미지 주석 만들기 (Create image annotations)

주석을 사용하면 미디어 레이어 안의 특정 영역이나 특징을 표시할 수 있습니다. 새 주석을 만들려면 미디어 레이어 객체에서 마우스 오른쪽 버튼을 눌러 컨텍스트 메뉴를 열고 **Create Annotation**을 선택합니다.

![그래프에서 마우스 오른쪽 버튼을 눌러 미디어 레이어에 주석 추가하기.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-create-annotation.png)

이미지 위에 직접 드래그해 모양을 정하는 방식으로 주석을 그립니다. 그린 뒤에도 주석의 크기를 바꾸거나 위치를 옮길 수 있습니다.

![그래프 미디어 레이어 위에 그린 주석.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-draw-annotation.png)

미디어의 객체 타입에 링크된 객체에 대해 주석을 만드는 액션 타입을 구성해 두었다면, 그 액션을 실행하는 옵션이 드롭다운 메뉴에 나타납니다. 이 예제에서는 `Create [Ships] Annotation`과 `Create [Ships] Text annotation`이 모두 보입니다.

![선택한 이미지의 객체 타입에 대해 사용 가능한 액션 타입 옵션.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-action-options.png)

실행할 액션 타입을 선택한 다음, 양식을 채워 새 주석 객체의 이름을 지정합니다. 주석의 좌표가 새 객체의 경계 상자 좌표로 사용된다는 점에 주목하세요. 이 동작은 객체 타입에 대해 액션을 어떻게 구성했는지에 따라 달라집니다.

![새 주석 객체를 위한 액션 양식.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-action-form.png)

이제 그래프의 미디어 레이어에서 객체와 그에 연결된 주석을 볼 수 있습니다.

![이미지 객체 타입에 연결된, 그래프 미디어 레이어의 주석 객체.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-add-object-result.png)

**설명**: 이미지에 사각형을 그리는 동작 자체는 화면상의 조작일 뿐이고, 실제로 데이터가 생기는 시점은 액션을 제출할 때입니다. 동작 순서는 다음과 같습니다. (1) 사용자가 사각형을 그립니다. (2) Vertex가 그 사각형의 좌표를 액션 양식의 좌표 파라미터에 미리 채워 넣습니다. (3) 사용자가 이름 등 나머지 파라미터를 입력하고 제출합니다. (4) 액션이 Annotation 객체를 하나 새로 만들고, 이는 Annotation 테이블에 행 하나가 추가되는 것에 해당합니다.

> **중간 요약**: 미디어 레이어 객체에서 **Create Annotation**으로 영역을 그린 뒤, 미리 만들어 둔 생성 액션 타입을 실행하면 그 영역 좌표를 가진 새 주석 객체가 생깁니다.

<a id="modify-existing-annotations"></a>
## 기존 주석 수정하기 (Modify existing annotations)

기존 주석을 수정하려면 편집할 객체를 찾아 선택합니다. 이 예제에서는 이전에 주석을 달아 둔 `Linen locker` 객체를 다룹니다.

![Vertex 그래프 위의 Linen locker 객체.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-linen-locker-existing-object.png)

주석을 옮기거나 크기를 바꾸면, 해당 객체 타입을 수정할 수 있는 액션 타입들이 주석 아래에 나타납니다. 이 예제에서는 `Edit annotation coordinates` 액션 타입을 실행해 주석의 새 위치를 반영할 수 있습니다.

![Edit annotation coordinates 액션 타입을 실행하는 옵션.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-linen-locker-edit.png)

편집 양식을 사용해 객체의 픽셀 공간 경계 상자 좌표를 갱신합니다. 이 좌표는 방금 그린 모양으로 채워져 있습니다.

![Annotation 객체의 좌표를 편집하는 양식.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-edit-form.png)

변경을 마친 뒤에는 갱신된 객체를 검토해 수정 사항이 올바르게 적용되었는지 확인합니다. 편집한 주석은 미디어 레이어에 변경 사항을 반영합니다.

![편집한 주석의 갱신된 속성.](https://www.palantir.com/docs/resources/foundry/vertex/media-layers-edit-result.png)

> **중간 요약**: 기존 주석을 옮기거나 크기를 바꾸면 수정용 액션 타입(`Edit annotation coordinates`)이 제안되고, 새 좌표가 미리 채워진 양식을 제출하면 객체의 좌표 속성이 갱신됩니다.

## 정리

- 미디어 레이어는 미디어 참조 속성을 가진 객체를 이미지로 그래프에 표시하고, 그 위에 링크된 주석 객체를 겹쳐 보여 줍니다.
- 준비 단계에서는 미디어 셋 기반 객체 타입, 외래 키로 링크된 주석 객체 타입, 주석 생성 및 수정용 액션 타입이 필요합니다.
- Ontology Manager의 **Capabilities** 탭에서 기본 이미지 참조 속성과 주석 좌표 속성을 지정하며, 지정하지 않으면 Vertex의 스타일 옵션에서 고를 수 있습니다.
- 주석을 그리거나 옮기는 것은 액션 실행으로 이어져, 좌표가 객체의 속성 값으로 저장됩니다.
