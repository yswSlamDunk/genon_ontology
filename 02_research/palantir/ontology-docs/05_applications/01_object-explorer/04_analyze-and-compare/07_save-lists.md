# 목록 저장하기 (Save lists)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/save-lists/
- 사이드바 위치: Applications > Object Explorer > Analyze and compare > Save lists

이 페이지는 Object Explorer의 탐색 결과를 목록(List)으로 저장하고 다시 여는 방법을 설명합니다. 목록은 조건이 아니라 특정 시점의 객체들을 고정해서 저장한다는 점에서 탐색(Exploration) 저장과 다릅니다.

Object Explorer에서 탐색한 결과를 **List**(목록)로 저장하고 공유할 수 있습니다. 저장된 목록을 사용하면 정적인 객체 목록을 다시 볼 수 있습니다. 저장된 목록은 직접 업데이트하지 않는 한 바뀌지 않습니다.

**설명**: 탐색 저장이 쿼리문을 저장하는 것이라면, 목록 저장은 쿼리를 실행한 그 시점의 결과 행들의 기본 키(primary key) 목록을 저장하는 것에 가깝습니다. 예를 들어 오늘 "지연된 항공편" 필터로 항공편 3건(AA100, DL200, UA300)이 나왔고 이를 목록으로 저장했다면, 내일 새로운 지연 항공편이 생겨도 목록에는 여전히 그 3건만 들어 있습니다.

<a id="saving-a-list"></a>
### 목록 저장하기 (Saving a list)

목록을 저장하려면 화면 오른쪽 위의 파란색 **Save** 버튼을 선택한 뒤 드롭다운 메뉴에서 **List**를 선택합니다. 목록의 제목 같은 저장용 메타데이터 정보도 입력하라는 안내가 나옵니다. 객체 전체 목록을 한꺼번에 저장할 수도 있고, Results View에서 행을 하나씩 직접 체크해 특정 객체만 골라 저장할 수도 있습니다.

![목록 저장](https://www.palantir.com/docs/resources/foundry/object-explorer/explorations_saved_list.png)

목록은 **Private**(비공개) 또는 **Public**(공개)으로 저장할 수 있습니다.

* **Private**를 고르면 목록은 홈 폴더의 Explorations 폴더에 저장되며, 기본적으로 본인만 접근할 수 있습니다.
* **Public**을 고르면 목록을 저장할 위치를 지정하라는 안내가 나옵니다. 그러면 목록은 저장한 위치에 접근할 수 있는 모든 사람이 접근할 수 있게 됩니다.

**참고**: 등록 환경(enrollment)의 구성에 따라 홈 폴더에 파일을 저장하지 못하도록 막혀 있을 수 있습니다. 이 경우 비공개 목록 저장 옵션도 비활성화됩니다.

목록을 공유해도 그 밑의 객체에 대한 접근 권한까지 공유되지는 않습니다. 따라서 보는 사람은 저장된 목록 자체에 대한 접근 권한과 함께 데이터에 대한 적절한 역할도 가지고 있어야 합니다.

> **중간 요약**: **Save** 드롭다운에서 **List**를 골라 전체 결과나 직접 선택한 객체만 저장합니다. 비공개와 공개 저장, 권한 규칙은 탐색 저장과 같습니다.

<a id="accessing-a-saved-list"></a>
### 저장된 목록 열기 (Accessing a saved list)

[Object Explorer 홈 페이지](../02_getting-started.md)의 전역 검색창을 사용하면 저장된 목록이 [검색 결과](../03_search-and-explore-objects/01_search-objects.md)에 표시됩니다.

![목록 검색 결과](https://www.palantir.com/docs/resources/foundry/object-explorer/explorations_explorations_search_result.png)

위쪽 내비게이션 바의 **Lists** 드롭다운으로도 저장된 목록에 접근할 수 있습니다. 이 드롭다운 메뉴에는 표시되는 목록을 더 좁힐 수 있는 텍스트 검색과 자주 쓰는 필터 옵션이 내장되어 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/explorations_list_dropdown_all.png" alt="모든 목록" width="300"/>        <img src="https://www.palantir.com/docs/resources/foundry/object-explorer/explorations_list_dropdown_favorites.png" alt="즐겨찾기 목록" width="300"/>

## 정리

- 목록(List)은 탐색 결과 중 특정 객체들을 고정해서 저장하며, 직접 업데이트하지 않으면 바뀌지 않습니다.
- 결과 전체를 저장하거나 Results View에서 체크한 객체만 골라 저장할 수 있습니다.
- 비공개, 공개 저장과 권한 규칙은 탐색 저장과 같고, 데이터 권한은 따로 필요합니다.
- 저장된 목록은 홈 페이지 검색창이나 위쪽 **Lists** 드롭다운에서 찾습니다.
