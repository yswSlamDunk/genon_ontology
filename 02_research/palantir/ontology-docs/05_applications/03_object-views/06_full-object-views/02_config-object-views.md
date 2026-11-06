# 전체 Object View 구성하기 (Configure full Object Views)

- 원문: https://www.palantir.com/docs/foundry/object-views/config-object-views/
- 사이드바 위치: Applications > Object Views > Full Object Views > Configure full Object Views

이 페이지는 전체 Object View를 편집하는 방법, 즉 탭을 관리하고 각 탭의 내용을 Workshop 모듈로 꾸미는 방법과 Object View 편집기의 화면 구성을 설명합니다. 다른 Object View 페이지에서 자주 참조하는 "Object View 편집기"가 무엇으로 이루어졌는지 이 페이지에서 확인할 수 있습니다.

<a id="edit-configured-full-object-views"></a>
## 구성된 전체 Object View 편집하기 (Edit configured full Object Views)

모든 객체 타입의 기본 구성된 전체 Object View에는, 객체 타입의 주요 속성(prominent properties)을 보여 주는 [Property List 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-property-list/) 하나와, 객체에 링크가 있다면 그 링크를 보여 주는 [Links 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-links/)이 들어 있습니다. 구성된 전체 Object View를 변경하려면 [편집 진입점](../04_config-overview.md#edit-configured-object-views) 중 하나를 이용해 구성된 Object View 편집기로 이동합니다. 편집기에 들어가면 구성된 전체 Object View의 각 탭 내용을 일반 Workshop 모듈과 똑같이 구성할 수 있습니다.

<a id="edit-object-view-tabs"></a>
### Object View 탭 편집하기 (Edit Object View tabs)

전체 Object View에서 편집할 수 있는 부분은 탭(tab)과 탭 콘텐츠(tab content) 두 가지입니다. 각 Object View 탭은 Workshop 모듈을 기반으로 하므로, [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)을 사용해 고급 기능을 갖춘 Object View 콘텐츠를 만들 수 있습니다. Workshop 탭으로 다음을 할 수 있습니다.

* [레이아웃(layout)](https://www.palantir.com/docs/foundry/workshop/concepts-layouts/)을 완전히 자유롭게 구성합니다.
* Workshop [변수(variables)](https://www.palantir.com/docs/foundry/workshop/concepts-variables/)를 사용해 정보를 유연하고 동적으로 불러옵니다.
* [시나리오(Scenarios)](https://www.palantir.com/docs/foundry/workshop/scenarios-overview/)를 사용해 시뮬레이션이나 모델 기반 결과를 표시합니다.

**설명**: Workshop 변수는 화면 안의 위젯끼리 값을 주고받는 통로입니다. Object View에서는 "지금 보고 있는 객체"가 기본 입력으로 주어지고, 이 값을 변수로 받아 다른 위젯에 넘길 수 있습니다. 예를 들어 Airport 객체의 Object View에서 현재 Airport를 변수로 받은 뒤, 그 공항에서 출발하는 Flight 객체 집합을 계산해 표 위젯에 표시하는 식입니다. 시나리오는 실제 데이터를 바꾸지 않고 "이 값을 바꾸면 결과가 어떻게 달라지는가"를 가정해 계산해 보는 기능입니다.

> **중간 요약**: 기본 전체 Object View는 Property List 위젯과 Links 위젯으로 이루어집니다. 탭마다 Workshop 모듈이 하나씩 붙어 있어 레이아웃, 변수, 시나리오 같은 Workshop 기능을 모두 쓸 수 있습니다.

<a id="use-the-object-view-editor"></a>
### Object View 편집기 사용하기 (Use the Object View editor)

Object View 편집기에는 **헤더(header)**, **객체 제목 표시줄(object title bar)**, **Workshop 모듈(Workshop module)의** 세 가지 주요 영역이 있습니다.

헤더의 이동 경로(breadcrumbs)에는 온톨로지 이름, 객체 타입, 폼 팩터(form factor)가 표시됩니다. 폼 팩터는 드롭다운으로, 전체 Object View 편집과 패널 Object View 편집 사이를 전환하는 데 쓸 수 있습니다. 그 아래에는 Object View와 현재 Workshop 모듈의 버전 번호가 표시됩니다. 오른쪽에서는 미리 볼 다른 객체를 선택하고, 편집 내용을 저장하고 게시하며, Object Explorer에서 객체를 열 수 있습니다.

![Object View 헤더 다이어그램.](https://www.palantir.com/docs/resources/foundry/object-views/object-view-header-diagram.png)

객체 제목 표시줄에서는 톱니바퀴 아이콘을 선택해 탭을 관리할 수 있습니다. 각 탭은 하나의 Workshop 모듈에 대응합니다. 탭이 하나만 구성되어 있으면, 편집 모드에서는 탭 제목이 보이지만 Object View를 볼 때는 탭 제목이 숨겨집니다.

톱니바퀴 아이콘을 선택하면 Object View 탭을 추가하고, 순서를 바꾸고, 이름을 바꾸고, 삭제할 수 있는 대화 상자가 열립니다. 탭을 삭제하면 그 탭에 들어 있는 Workshop 모듈도 함께 삭제됩니다.

이 대화 상자에서는 탭의 [표시 설정(visibility settings)](../08_legacy-object-views/02_config-tabs.md#tab-visibility)을 구성하거나, 다른 [레거시 구성 옵션](../08_legacy-object-views/01_config-legacy-object-views.md)을 편집해야 할 때 레거시 Object View 편집기로 들어갈 수도 있습니다.

![탭 관리("Manage tabs") 대화 상자.](https://www.palantir.com/docs/resources/foundry/object-views/manage-tabs.gif)

탭의 콘텐츠는 일반 Workshop 모듈과 똑같이 편집할 수 있습니다. 편집을 마치면 **Save and publish** 버튼이 탭 편집 내용과 현재 모듈의 편집 내용을 모두 저장하고 게시합니다. 단, [자동 게시가 꺼져 있는 경우](../03_manage-versions.md#save-new-versions)는 예외입니다.

**설명**: 폼 팩터(form factor)는 같은 객체 타입의 Object View를 어떤 크기와 형태로 보여 줄지에 대한 구분입니다. 여기서는 화면 전체를 쓰는 "full"과 다른 앱 옆에 붙는 좁은 "panel" 두 가지가 있으며, 편집기 헤더의 드롭다운으로 둘을 오가며 편집합니다. 탭 삭제가 모듈 삭제로 이어진다는 점은 되돌리기 어려운 동작이므로 주의해야 합니다.

> **중간 요약**: 편집기는 헤더(경로, 폼 팩터 전환, 버전 번호, 미리 보기 객체 선택, 저장과 게시), 객체 제목 표시줄(톱니바퀴로 탭 추가, 순서 변경, 이름 변경, 삭제, 표시 설정), Workshop 모듈(탭 콘텐츠 편집) 세 영역으로 이루어집니다. 탭을 지우면 그 Workshop 모듈도 지워집니다.

## 정리

- 기본 전체 Object View는 주요 속성을 보여 주는 Property List 위젯과 링크를 보여 주는 Links 위젯으로 구성됩니다.
- 전체 Object View의 편집 대상은 탭과 탭 콘텐츠이며, 각 탭은 Workshop 모듈 하나입니다.
- 편집기는 헤더, 객체 제목 표시줄, Workshop 모듈의 세 영역으로 나뉩니다.
- 톱니바퀴 대화 상자에서 탭을 관리하고 표시 설정과 레거시 편집기에 접근하며, 탭 삭제 시 모듈도 삭제됩니다.
- 편집을 마치면 **Save and publish**(자동 게시가 꺼져 있으면 Save와 Publish)로 반영합니다.
