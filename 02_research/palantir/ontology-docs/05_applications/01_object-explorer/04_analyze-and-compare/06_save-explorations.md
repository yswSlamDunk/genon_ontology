# 탐색 저장하기 (Save explorations)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/save-explorations/
- 사이드바 위치: Applications > Object Explorer > Analyze and compare > Save explorations

이 페이지는 Object Explorer에서 진행한 작업을 탐색(Exploration)으로 저장하고, 저장한 탐색을 다시 찾아 여는 방법을 설명합니다. 비공개와 공개 저장의 차이, 공유 시 권한이 어떻게 적용되는지도 다룹니다.

Object Explorer에서 한 작업은 **Exploration**(탐색)으로 저장하고 공유할 수 있습니다. 저장된 탐색을 사용하면 적용한 필터와 구성한 레이아웃을 유지한 채 같은 검색 파라미터 세트를 다시 볼 수 있습니다.

**설명**: 저장되는 것은 객체 목록 자체가 아니라 "어떤 객체 타입에 어떤 필터를 걸었는가"라는 조건과 화면 구성입니다. SQL로 보면 쿼리 결과가 아니라 쿼리문을 저장하는 것에 가깝습니다. 그래서 나중에 열면 그 시점의 데이터로 다시 계산된 결과가 나옵니다. 고정된 객체 목록을 저장하려면 [목록 저장하기](07_save-lists.md)를 사용합니다.

<a id="saving-an-exploration"></a>
### 탐색 저장하기 (Saving an exploration)

탐색을 저장하려면 화면 오른쪽 위의 파란색 **Save** 버튼을 선택합니다. 탐색의 제목 같은 저장용 메타데이터 정보도 입력하라는 안내가 나옵니다.

![탐색 저장](https://www.palantir.com/docs/resources/foundry/object-explorer/explorations_saved_exploration.png)

탐색은 **Private**(비공개) 또는 **Public**(공개)으로 저장할 수 있습니다.

* **Private**를 고르면 탐색은 홈 폴더의 Explorations 폴더에 저장되며, 기본적으로 본인만 접근할 수 있습니다.
* **Public**을 고르면 탐색을 저장할 위치를 지정하라는 안내가 나옵니다. 그러면 탐색은 저장한 위치에 접근할 수 있는 모든 사람이 접근할 수 있게 됩니다.

**참고**: 등록 환경(enrollment)의 구성에 따라 홈 폴더에 파일을 저장하지 못하도록 막혀 있을 수 있습니다. 이 경우 비공개 탐색 저장 옵션도 비활성화됩니다.

탐색을 공유해도 그 밑의 객체에 대한 접근 권한까지 공유되지는 않습니다. 따라서 보는 사람은 저장된 탐색 자체에 대한 접근 권한과 함께 데이터에 대한 적절한 역할도 가지고 있어야 합니다.

**설명**: Foundry에서 파일의 접근 권한은 그 파일이 놓인 폴더(프로젝트)의 권한을 따르는 경우가 많습니다. 그래서 공개 저장은 "어느 폴더에 둘 것인가"를 고르는 것이 곧 "누가 볼 수 있는가"를 정하는 일이 됩니다. 다만 탐색 파일에 접근할 수 있는 것과 그 안의 객체 데이터를 볼 수 있는 것은 별개의 권한입니다.

> **중간 요약**: 오른쪽 위 **Save**로 탐색을 저장하며, 비공개는 홈 폴더에, 공개는 지정한 위치에 저장되어 그 위치의 권한을 따릅니다. 탐색을 공유해도 데이터 권한은 공유되지 않습니다.

<a id="accessing-a-saved-exploration"></a>
### 저장된 탐색 열기 (Accessing a saved exploration)

[Object Explorer 홈 페이지](../02_getting-started.md)의 전역 검색창을 사용하면 저장된 탐색이 [검색 결과](../03_search-and-explore-objects/01_search-objects.md)에 표시됩니다.

![탐색 검색 결과](https://www.palantir.com/docs/resources/foundry/object-explorer/explorations_explorations_search_result.png)

위쪽 내비게이션 바의 **Explorations** 드롭다운으로도 저장된 탐색에 접근할 수 있습니다. 이 드롭다운 메뉴에는 표시되는 탐색을 더 좁힐 수 있는 텍스트 검색과 자주 쓰는 필터 옵션이 내장되어 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/explorations_explorations_dropdown_all.png" alt="모든 탐색" width="300"/>        <img src="https://www.palantir.com/docs/resources/foundry/object-explorer/explorations_explorations_dropdown_created.png" alt="내가 만든 탐색" width="300"/>

## 정리

- 탐색(Exploration)은 필터와 레이아웃을 저장해 같은 검색을 다시 실행할 수 있게 합니다.
- 비공개 저장은 홈 폴더의 Explorations 폴더에, 공개 저장은 지정한 위치에 저장되며, 환경 설정에 따라 비공개 저장이 막혀 있을 수 있습니다.
- 탐색을 공유해도 객체 데이터 권한은 따로 필요합니다.
- 저장된 탐색은 홈 페이지 검색창이나 위쪽 **Explorations** 드롭다운에서 찾습니다.
