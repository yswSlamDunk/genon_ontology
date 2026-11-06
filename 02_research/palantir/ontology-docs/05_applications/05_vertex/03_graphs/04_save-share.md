# 저장, 공유, 협업 (Save, share, and collaborate)

- 원문: https://www.palantir.com/docs/foundry/vertex/save-share/
- 사이드바 위치: Applications > Vertex > Graphs > Save, share, and collaborate

이 페이지는 Vertex 그래프를 Foundry 프로젝트에 저장하고, 링크로 다른 사람과 공유하고, 복제하고, 버전 관리하는 방법을 설명합니다. 그래프를 공유해도 데이터 권한(permission)은 넓어지지 않는다는 점이 중요합니다.

시스템 그래프나 사례 연구(case study)를 저장하고 공유하는 방법은 여러 가지입니다.

<a id="save-a-draft"></a>
## 초안 저장하기 (Save a draft)

위쪽 도구 모음에서 **Save as**를 선택하면 그래프를 관련 Foundry 프로젝트 안에 저장하라는 안내가 나옵니다. 그래프는 그것이 저장된 프로젝트에 접근 권한이 있는 사람에게만 보입니다. 초안을 처음 저장한 뒤에는 **Save**를 선택하면 상태가 갱신됩니다.

이 그래프를 더 넓게 공유하고 싶다면 위쪽 도구 모음의 **Share** 메뉴에서 링크 공유를 켤 수 있습니다. 이 메뉴에서 공유 링크를 사용하는 사용자에게 허용할 권한 역할(role)을 선택할 수 있습니다. 다른 사람이 링크에 접근하면 **Roles** 아래에서 그들의 사용자 이름을 볼 수 있습니다.

![초안](https://www.palantir.com/docs/resources/foundry/vertex/save_share_collaborate-draft.jpg)

그래프를 공유해도, 사용자가 원래 접근 권한을 가지고 있지 않은 다른 리소스에 대한 접근 권한이 부여되지는 않습니다. 그래프를 열었을 때 권한이 없거나 데이터가 삭제되어 사용자가 그래프에서 참조하는 객체나 시계열(time series)에 접근할 수 없다면, 사용자는 여전히 그래프의 구조와 모양은 볼 수 있습니다. 다만 해당 객체에 관한 구체적인 데이터는 볼 수 없습니다.

**설명**: 그래프 리소스에 대한 권한과 그래프가 보여 주는 데이터에 대한 권한은 별개로 검사됩니다. 예를 들어 A가 Employee 객체 5개가 들어 있는 그래프를 B에게 공유했는데 B가 Employee 데이터셋에 대한 권한이 없다면, B의 화면에는 노드 5개와 간선은 그려지지만 노드를 눌러도 이름이나 급여 같은 속성 값은 나오지 않습니다. 그래프 파일은 "어떤 객체를 어떻게 배치했는가"만 담고, 실제 값은 열람할 때마다 사용자의 권한으로 다시 조회하기 때문입니다.

> **중간 요약**: **Save as**로 그래프를 프로젝트에 저장하고, **Share** 메뉴에서 역할을 지정한 링크 공유를 켤 수 있습니다. 공유받은 사용자는 권한이 없는 객체에 대해 그래프 구조만 보고 데이터는 보지 못합니다.

<a id="duplicate-existing-graphs"></a>
## 기존 그래프 복제하기 (Duplicate existing graphs)

기존 그래프를 바탕으로 작업하고 싶다면 **Save** 드롭다운 메뉴에서 **Duplicate**를 선택할 수 있습니다. 이 동작은 그래프의 사본을 원하는 새 프로젝트에 저장하라는 안내를 띄웁니다. 복제하면 원본을 바꾸지 않고 작업할 수 있는 새 그래프가 만들어집니다.

![그래프 복제](https://www.palantir.com/docs/resources/foundry/vertex/save_share_collaborate-duplicate.jpg)

![저장](https://www.palantir.com/docs/resources/foundry/vertex/save_share_collaborate-save.jpg)

<a id="version-control"></a>
## 버전 관리 (Version control)

그래프의 변경 사항을 시간에 따라 추적하고 싶다면 **Save** 드롭다운 메뉴에서 **Enable versioning**을 선택할 수 있습니다. 이후 저장할 때마다 그래프의 새 버전이 생성됩니다.

![버전 관리 켜기](https://www.palantir.com/docs/resources/foundry/vertex/enable_versioning.png)

전체 버전 기록은 **Graph History** 사이드바에서 볼 수 있습니다. 그래프의 이전 버전은 읽기 전용 모드로 열 수 있습니다(현재 버전 번호는 리소스 머리글에 표시됩니다).

![그래프 기록](https://www.palantir.com/docs/resources/foundry/vertex/graph_history.png)

Graph History 사이드바에서 **Revert**를 선택하면, 선택한 버전과 같은 내용으로 새 버전이 생성됩니다.

**설명**: **Revert**가 과거 버전으로 "되감는" 것이 아니라 과거 내용을 복사한 새 버전을 만든다는 점은 Git의 `git revert`와 같은 방식입니다. 예를 들어 버전 1, 2, 3이 있을 때 버전 1로 Revert하면 버전 2와 3은 기록에 그대로 남고, 버전 1과 내용이 같은 버전 4가 새로 생깁니다.

> **중간 요약**: **Duplicate**로 원본을 건드리지 않는 사본을 만들 수 있고, **Enable versioning**을 켜면 저장할 때마다 버전이 쌓이며 **Revert**는 과거 내용으로 새 버전을 만듭니다.

## 정리

- 그래프는 Foundry 프로젝트에 저장되며, 그 프로젝트 접근 권한이 있는 사람만 볼 수 있습니다.
- **Share** 메뉴로 역할을 지정한 링크 공유를 할 수 있지만, 공유가 데이터 접근 권한을 늘리지는 않습니다.
- **Duplicate**로 원본과 독립된 사본을 만들 수 있습니다.
- **Enable versioning**으로 버전 기록을 남기고, **Graph History**에서 이전 버전을 보거나 **Revert**할 수 있습니다.
