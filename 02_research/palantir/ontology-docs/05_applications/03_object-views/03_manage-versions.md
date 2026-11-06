# 구성된 Object View 버전 관리 (Manage configured Object View versions)

- 원문: https://www.palantir.com/docs/foundry/object-views/manage-versions/
- 사이드바 위치: Applications > Object Views > Manage configured Object View versions

이 페이지는 구성된 Object View를 편집할 때 변경 내용이 버전으로 저장되는 방식, 저장과 게시(publish)를 분리하는 방법, 이전 버전을 확인하고 다시 게시하는 방법을 설명합니다. 여러 사람이 쓰는 화면을 안전하게 고치려면 "저장"과 "사용자에게 공개"를 구분해서 다룰 수 있어야 하므로 이 기능이 필요합니다.

Object View에 저장한 편집 내용은 새 버전으로 보관됩니다. 하나의 버전에는 탭 추가, 편집, 삭제 같은 여러 변경이 함께 들어갈 수 있습니다. 버전 관리를 통해 다음을 할 수 있습니다.

* 변경 사항을 조금씩 저장하면서 Object View를 안전하게 반복 개선합니다.
* 어떤 버전을 게시해 사용자에게 보이게 할지 제어합니다.
* 새 버전에 오류가 있으면 이전 버전을 다시 게시합니다.
* 버전에 설명을 붙여 다른 편집자와 협업합니다.

Object View에 포함된 [각 Workshop 모듈에는 별도의 버전](https://www.palantir.com/docs/foundry/workshop/versions/)이 있습니다. 두 버전 번호는 모두 [Object View 편집기 헤더](06_full-object-views/02_config-object-views.md#use-the-object-view-editor)에 표시됩니다.

**설명**: 버전 관리는 Git의 커밋 기록과 같은 구조입니다. 저장할 때마다 번호가 붙은 스냅숏이 쌓이고, 그중 하나를 "현재 게시된 버전"으로 지정합니다. 여기서는 버전 번호가 두 종류라는 점이 중요합니다. 하나는 탭 구성 같은 Object View 자체의 버전이고, 다른 하나는 각 탭 안의 화면을 이루는 Workshop 모듈의 버전입니다.

> **중간 요약**: Object View를 저장하면 새 버전이 생기며, 버전을 통해 단계적 저장, 게시 대상 선택, 롤백, 협업이 가능합니다. Object View 버전과 Workshop 모듈 버전은 따로 관리됩니다.

<a id="save-new-versions"></a>
## 새 버전 저장하기 (Save new versions)

Object View를 편집한 뒤 Object View 편집기 헤더의 **Save** 버튼을 선택하면 변경 사항을 저장할 수 있습니다. **Automatically publish new versions**(새 버전 자동 게시)가 켜져 있으면 이 버튼은 **Save and publish**(저장 후 게시)로 표시되며, 탭 변경 사항과 현재 Workshop 모듈의 변경 사항을 모두 게시합니다. 자동 게시는 기본적으로 켜져 있습니다.

**Automatically publish new versions**를 끄면 저장과 게시 버튼이 따로 표시됩니다. **Save** 버튼은 탭과 Workshop 모듈의 변경 사항을 모두 저장하고, **Publish** 버튼은 이 두 가지 변경 사항을 사용자에게 게시합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/object-view-save-publish.png" alt="Object View의 'Save and publish' 버튼." width="300">

Workshop 모듈을 편집하는 동안에는 다른 Workshop 모듈과 마찬가지로 주기적으로 자동 저장됩니다. 하지만 이 변경 사항은 Object View를 게시하기 전까지 사용자에게 보이지 않습니다.

**팁**: 모범 사례(Best practice). Object View를 많은 사용자가 활발히 쓰고 있거나 여러 편집자가 함께 작업하고 있다면 자동 게시를 끄는 것을 권장합니다. 이렇게 하면 협업이 쉬워지고 사용자 워크플로가 깨질 가능성이 줄어듭니다.

**설명**: 저장(save)은 편집자 쪽에 새 버전을 기록하는 일이고, 게시(publish)는 그 버전을 실제 사용자가 보는 화면으로 바꾸는 일입니다. 웹 서비스에서 코드를 커밋하는 것과 운영 서버에 배포하는 것을 나누는 것과 같은 구분입니다. 자동 게시가 켜져 있으면 저장하는 순간 곧바로 사용자 화면이 바뀌므로, 작업 중인 미완성 상태가 그대로 노출될 수 있습니다.

> **중간 요약**: 자동 게시가 켜져 있으면 저장과 동시에 게시되고, 끄면 Save와 Publish를 따로 누릅니다. 사용자가 많거나 편집자가 여럿이면 자동 게시를 끄는 것이 권장됩니다.

<a id="access-prior-versions"></a>
## 이전 버전에 접근하기 (Access prior versions)

Object View의 이전 버전 목록을 보려면 Object View 편집기 헤더에 있는 파란색 Object View 버전 번호를 선택합니다. 그러면 모든 이전 버전의 날짜, 작성자, 설명을 보여 주는 대화 상자가 열립니다. 이 대화 상자에서 모든 버전을 미리 볼 수 있습니다.

* 현재 게시된 버전에는 초록색 체크 표시가 붙습니다.
* 이전에 게시된 적이 있는 버전에는 회색 체크 표시가 붙습니다.
* 한 번도 게시되지 않은 버전에는 체크 표시가 없습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/object-view-edit-history.png" alt="Object View 편집 기록 패널." width="500">

> **중간 요약**: 헤더의 파란 버전 번호를 누르면 버전 기록 대화 상자가 열리며, 체크 표시 색으로 현재 게시 버전(초록), 과거 게시 버전(회색), 미게시 버전(없음)을 구분합니다.

## 정리

- Object View 편집 내용은 저장할 때마다 새 버전으로 쌓이고, Workshop 모듈 버전은 별도로 관리됩니다.
- 자동 게시가 켜져 있으면 **Save and publish** 하나로 저장과 게시가 함께 일어나고, 끄면 **Save**와 **Publish**가 분리됩니다.
- 사용자가 많거나 협업 중이라면 자동 게시를 끄는 것이 권장됩니다.
- 버전 기록 대화 상자에서 각 버전의 날짜, 작성자, 설명, 게시 여부를 확인하고 미리 볼 수 있습니다.
