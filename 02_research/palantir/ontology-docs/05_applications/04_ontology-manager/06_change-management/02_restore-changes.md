# 변경 사항 검토와 복원 (Review and restore changes)

- 원문: https://www.palantir.com/docs/foundry/ontology-manager/restore-changes/
- 사이드바 위치: Applications > Ontology Manager > Change management > Review and restore changes

이 페이지는 Ontology Manager에서 온톨로지에 가해진 변경 이력을 확인하고, 객체 타입을 이전 버전으로 되돌리는 방법을 설명합니다. 아직 저장하지 않은 변경, 이미 저장된 변경, 리소스 하나의 변경 이력을 각각 어디서 보는지와, 복원 후 반드시 저장해야 한다는 점을 다룹니다.

<a id="review-changes-made-to-the-ontology-globally"></a>
## 온톨로지 전체에 대한 변경 검토하기 (Review changes made to the Ontology globally)

온톨로지 전체에서 저장하지 않은 변경을 검토하려면:

홈페이지 사이드바에서 **Unsaved changes**를 선택하면 내가 만든 모든 미저장 변경 목록을 볼 수 있습니다.

![Unsaved changes 버튼](https://www.palantir.com/docs/resources/foundry/ontology-manager/review-restore-unsaved-changes-button.png)

온톨로지 전체에서 저장된 변경을 검토하려면:

홈페이지 사이드바의 **History** 탭을 선택하면 저장된 모든 온톨로지 변경 목록을, 변경이 이루어진 시점과 변경을 적용한 사용자 정보와 함께 볼 수 있습니다.

![History 버튼](https://www.palantir.com/docs/resources/foundry/ontology-manager/review-restore-history-button.png)

기본적으로 변경 목록은 접혀 있습니다. 어떤 변경이든 ![아래쪽 화살표](https://www.palantir.com/docs/resources/foundry/ontology-manager/down-arrow.png)(아래쪽 화살표)를 선택하면 세부 내용을 볼 수 있습니다.

**설명**: Ontology Manager에서는 편집한 내용이 곧바로 온톨로지에 반영되지 않고, 먼저 작업 상태(working state)라는 나만의 임시 변경 묶음에 쌓입니다. 저장(save)을 해야 다른 사용자도 보는 실제 온톨로지에 반영됩니다. 그래서 "미저장 변경"은 나만 보는 작업 상태의 내용이고, "저장된 변경"은 History에 남는 공식 이력입니다. Git으로 치면 미저장 변경은 커밋 전 작업 디렉터리의 수정 사항, History는 커밋 로그에 해당합니다.

> **중간 요약**: 홈 사이드바의 **Unsaved changes**에서 내 미저장 변경을, **History** 탭에서 저장된 전체 변경을 시점과 사용자 정보와 함께 볼 수 있습니다.

<a id="filter-changes-made-to-the-ontology-globally"></a>
## 온톨로지 전체에 대한 변경 필터링하기 (Filter changes made to the Ontology globally)

**Ontology history** 페이지에서는 내가 볼 권한이 없는 객체 타입과 링크 타입에 대한 변경을 숨기는 옵션을 쓸 수 있습니다. 이 옵션을 켜지 않으면, 온톨로지에 변경이 있었다는 사실은 볼 수 있지만 추가 세부 내용은 볼 수 없습니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/review-restore-hide-changes.png" alt="볼 수 없는 항목 숨기기" width="600"/>

편집 이력의 각 항목은 사용자가 변경을 저장한 한 번의 행위에 대응합니다. 같은 작성자가 만든 변경을 하나의 항목으로 합쳐서 보기를 간결하게 만드는 옵션도 있습니다.

<a id="review-changes-made-to-a-single-ontology-resource"></a>
## 단일 온톨로지 리소스에 대한 변경 검토하기 (Review changes made to a single Ontology resource)

온톨로지 리소스에 대한 변경을 검토하려면 해당 리소스 페이지에서 **History** 탭을 선택하세요. 리소스에 가해진 편집 목록이 다음 세부 정보와 함께 표시됩니다.

* 내가 이 리소스에 만든 미저장 변경
* 이 리소스에 대해 저장된 모든 변경과, 변경이 이루어진 시점 및 변경을 적용한 사용자 정보

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/review-restore-entity-history-button.png" alt="리소스 History 버튼" width="600"/>

온톨로지 리소스 뷰의 왼쪽 아래에는 리소스가 마지막으로 언제, 어느 사용자에 의해 편집되었는지 알려 주는 푸터가 있습니다.

> **중간 요약**: **Ontology history** 페이지에서는 권한 없는 리소스의 변경을 숨기거나 같은 작성자의 변경을 합쳐 볼 수 있고, 리소스별 **History** 탭에서는 그 리소스의 미저장 변경과 저장된 변경을 함께 봅니다.

<a id="restore-changes-made-to-a-single-object-type"></a>
## 단일 객체 타입에 대한 변경 복원하기 (Restore changes made to a single object type)

객체 타입을 이전 버전으로 복원하려면 아래 단계를 따르세요.

1. 복원 버튼 ![복원 버튼](https://www.palantir.com/docs/resources/foundry/ontology-manager/restore-button.png)(반시계 방향 화살표)을 선택합니다.
2. **Confirm**을 선택합니다.

**주의**: 복원한 변경은 저장해야 적용됩니다(Restored changes must be saved to take effect). 객체 타입을 이전 버전으로 복원하면, 선택한 항목 이후에 이루어진 모든 변경이 취소됩니다. 이 변경은 내 작업 상태(working state)에 추가되며, 복원이 적용되려면 변경 사항을 온톨로지에 저장해야 합니다. [온톨로지에 저장하는 방법을 더 알아보세요.](01_save-changes.md)

**설명**: 복원은 과거 상태로 돌아가는 "새 변경"을 작업 상태에 만드는 동작입니다. Git의 `git revert`가 이전 커밋을 지우지 않고 되돌리는 새 커밋을 만드는 것처럼, 복원 직후에는 아직 미저장 변경일 뿐이고 저장해야 실제 온톨로지에 반영됩니다.

## 정리

- 홈 사이드바의 **Unsaved changes**는 내 미저장 변경을, **History** 탭은 저장된 전체 변경 이력을 보여 줍니다.
- **Ontology history** 페이지에서 권한 없는 리소스의 변경을 숨기거나 같은 작성자의 변경을 합쳐 볼 수 있습니다.
- 리소스별 **History** 탭과 왼쪽 아래 푸터로 해당 리소스의 변경 이력과 마지막 편집자를 확인합니다.
- 객체 타입은 복원 버튼과 **Confirm**으로 이전 버전으로 되돌릴 수 있지만, 그 결과를 저장해야 실제로 적용됩니다.
