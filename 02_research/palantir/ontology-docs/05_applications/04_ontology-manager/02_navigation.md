# Ontology Manager 탐색 (Navigation)

- 원문: https://www.palantir.com/docs/foundry/ontology-manager/navigation/
- 사이드바 위치: Applications > Ontology Manager > Navigation

이 페이지는 Ontology Manager 화면에서 리소스를 찾고 이동하는 방법을 설명합니다. 헤더 검색창, 홈 페이지 사이드바의 필터, 그리고 리소스를 연 뒤 홈으로 돌아가는 버튼을 다룹니다.

<a id="header-search-bar"></a>
## 헤더 검색창 (Header search bar)

애플리케이션 헤더 가운데에 **Search** 바가 있습니다. **Search** 바를 클릭하거나 `Cmd/Ctrl + K`를 누르면 **Search** 바 대화상자가 열립니다.

![검색창](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-navigation-search.png)

홈 페이지에서 **Search** 바로 검색하면, 홈 페이지가 검색과 일치하는 리소스 목록으로 갱신됩니다. 관심 있는 객체 타입, 속성(property), 링크 타입, 액션 타입, 공유 속성(shared property), 인터페이스, 함수(function)를 검색할 수 있습니다. 검색 결과에는 검색어가 어느 필드와 일치했는지 강조 표시됩니다. 키보드의 위쪽, 아래쪽 화살표 키로 검색 결과를 이동하면서 선택한 결과의 미리보기를 볼 수 있습니다. **Open**을 선택하거나 Enter 키를 누르면 선택한 결과가 열립니다.

![헤더에서 검색하기](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-navigation-search-in-header.png)

> **중간 요약**: 헤더의 **Search** 바(`Cmd/Ctrl + K`)로 객체 타입, 속성, 링크 타입, 액션 타입, 공유 속성, 인터페이스, 함수를 검색하고 키보드로 결과를 이동하며 열 수 있습니다.

<a id="home-page-filters"></a>
## 홈 페이지 필터 (Home page filters)

홈 페이지 사이드바에서 **Object types**, **Link types**, **Action Types**, **Shared Properties**, **Interfaces**, **Functions** 페이지를 선택할 수 있습니다. 이 페이지들에서는 가시성(visibility), 개발 상태(development status), 인덱싱 문제를 기준으로 객체 타입과 링크 타입을 필터링할 수 있습니다.

![홈 페이지 사이드바](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-navigation-homepage-sidebar.png)

백킹 데이터소스(backing datasource)가 등록되지 않았거나 Object Storage v1(Phonograph)으로의 재인덱싱에 실패한 객체 타입은 객체 타입 페이지의 issue 열에 빨간색 오류 메시지가 표시됩니다.

**설명**: 백킹 데이터소스는 객체 타입의 객체들을 만들어 내는 원본 데이터셋입니다. 인덱싱은 이 데이터셋의 행을 객체 저장소(여기서는 Object Storage v1, 내부 이름 Phonograph)로 옮겨 빠르게 검색하고 조회할 수 있는 형태로 만드는 작업입니다. 데이터베이스에서 테이블에 인덱스를 만들어 두어야 조회가 빨라지는 것과 같은 목적이며, 이 작업이 실패하면 애플리케이션에서 최신 객체를 읽지 못할 수 있으므로 오류로 표시됩니다.

> **중간 요약**: 홈 사이드바의 리소스별 페이지에서 가시성, 개발 상태, 인덱싱 문제로 필터링할 수 있고, 데이터소스 미등록이나 재인덱싱 실패는 빨간 오류로 표시됩니다.

<a id="navigation-back-from-a-selection"></a>
## 선택 화면에서 돌아가기 (Navigation back from a selection)

객체 타입, 링크 타입, 액션 타입을 연 뒤에는 뷰 사이드바 왼쪽 위 모서리의 **Back home**을 선택해 홈으로 돌아갈 수 있습니다.

![Back home](https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-navigation-back-home.png)

**Back home** 버튼 위에 마우스를 올리면 최근 편집한 객체 타입, 링크 타입, 액션 타입으로 가는 빠른 링크와, 지금 보고 있는 리소스와 관련된 모든 리소스로 가는 빠른 링크도 나타납니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/oma-user-interface-navigation-back-home-hover.png" alt="Back home에 마우스를 올린 모습" width="400" />

## 정리

- 헤더 **Search** 바(`Cmd/Ctrl + K`)로 온톨로지의 여러 리소스를 검색하고 키보드로 결과를 탐색합니다.
- 홈 사이드바에서 리소스 종류별 페이지를 열고 가시성, 개발 상태, 인덱싱 문제로 필터링합니다.
- 데이터소스 미등록이나 재인덱싱 실패는 issue 열에 빨간 오류로 나타납니다.
- **Back home** 버튼으로 홈에 돌아가고, 마우스를 올리면 최근 편집 리소스와 관련 리소스 링크가 보입니다.
