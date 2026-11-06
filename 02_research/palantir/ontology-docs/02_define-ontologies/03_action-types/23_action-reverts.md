# 액션 실행 취소 또는 되돌리기 (Undo or revert Actions)

- 원문: https://www.palantir.com/docs/foundry/action-types/action-reverts/
- 사이드바 위치: Define Ontologies > Action types > Undo or revert Actions

이 페이지는 방금 적용한 액션을 되돌리는(revert) 기능을 설명합니다. 사용자가 실수로 잘못된 값을 저장하거나 객체를 삭제했을 때 바로 원래 상태로 복구할 수 있게 해 주는 기능이며, 어떻게 켜는지, 언제 되돌리기가 실패하는지, 되돌리기로도 복구되지 않는 것이 무엇인지를 다룹니다.

[Ontology Manager](../../05_applications/04_ontology-manager/01_overview.md)의 액션 되돌리기(action revert) 기능을 사용하면 액션이 적용된 직후에 그 액션을 되돌릴(즉, 실행 취소할) 수 있습니다. 액션이 성공적으로 적용된 뒤 표시되는 성공 메시지에서 **Undo**를 선택하면 액션을 되돌릴 수 있습니다.

새 액션은 기본적으로 되돌릴 수 있습니다.

**참고**: 액션 되돌리기는 Object Storage v2에서만 사용할 수 있습니다. 즉 [OSv2](../../06_ontology-architecture/01_overview-and-getting-started/02_object-storage-v2-breaking-changes.md)의 객체 타입을 수정하거나 생성하는 액션만 되돌릴 수 있습니다. 객체 타입이 현재 Object Storage v2에 저장되어 있지 않다면, 이 [가이드](../../06_ontology-architecture/01_overview-and-getting-started/03_osv1-osv2-migration.md#migrate-from-object-storage-v1-phonograph-to-object-storage-v2)를 따라 마이그레이션할 수 있습니다.

**설명**: Object Storage v1(OSv1, Phonograph)과 Object Storage v2(OSv2)는 온톨로지 객체 데이터를 저장하고 인덱싱하는 백엔드의 두 세대입니다. 되돌리기 기능은 새 세대인 OSv2에서만 동작하므로, 오래된 객체 타입을 쓰고 있다면 먼저 저장소 버전을 확인해야 합니다.

<a id="configure-a-revertible-action"></a>
## 되돌릴 수 있는 액션 설정하기 (Configure a revertible action)

현재 액션은 그 액션을 적용한 사용자만 되돌릴 수 있습니다.

액션의 **Form** 탭에서 **Allow revert after action submission**(액션 제출 후 되돌리기 허용) 토글을 켭니다. 이 토글이 올바르게 설정되어 온톨로지에 저장되면 액션을 되돌릴 수 있습니다.

![Form 섹션의 액션 되돌리기 설정 화면](https://www.palantir.com/docs/resources/foundry/action-types/action-reverts-form-button.png)

**Form** 탭의 **Allow revert after action submission** 토글은 2024년 5월 이후에 생성되고 OSv2 객체 타입만 수정하는 액션에서 기본으로 켜져 있습니다.
2024년 5월 이전부터 존재했고 OSv2의 객체 타입을 수정하는 액션은 되돌리기가 기본으로 켜져 있지 않지만, 직접 켤 수 있습니다.

OSv1 객체 타입만 수정하는 액션은 되돌릴 수 없습니다.

> **중간 요약**: 되돌리기는 OSv2 객체 타입을 수정하는 액션에서, 액션을 적용한 본인만 사용할 수 있습니다. Form 탭의 토글로 켜며, 2024년 5월 이후 만든 OSv2 전용 액션은 기본으로 켜져 있습니다.

<a id="revert-an-action"></a>
## 액션 되돌리기 (Revert an action)

**경고**: 액션 되돌리기(Revert action). 아래의 토스트(toast) 알림이 액션을 되돌릴 수 있는 유일한 기회입니다. 삭제 액션을 수행할 때 특히 유의해야 합니다.

되돌리기가 성공하면 사용자는 아래와 같이 원래 액션 성공 때와 비슷한 토스트를 보게 됩니다.

편집 적용됨:

![“Edits successfully reverted”라고 표시된 토스트 알림.](https://www.palantir.com/docs/resources/foundry/action-types/action-reverts-revert-action.png)

편집 되돌려짐:

![“Edits successfully applied”라고 표시된 토스트 알림.](https://www.palantir.com/docs/resources/foundry/action-types/action-reverts-edits-reverted.png)

**설명**: 토스트는 화면 구석에 잠깐 떴다가 사라지는 작은 알림 메시지입니다. 되돌리기 버튼(**Undo**)이 이 토스트 안에만 있으므로, 토스트가 사라지면 같은 방식으로는 더 이상 되돌릴 수 없습니다. 원문의 이미지 설명은 두 그림의 캡션이 서로 바뀌어 있는 것으로 보이지만, 원문 그대로 번역했습니다.

> **중간 요약**: 되돌리기는 액션 직후 뜨는 토스트의 Undo로만 할 수 있으며, 토스트가 사라지면 기회가 없어지므로 삭제 액션에서 특히 주의해야 합니다.

<a id="caveats"></a>
## 주의 사항 (Caveats)

액션 되돌리기는 다음과 같은 경우 실패할 수 있습니다.

* 객체에 대한 액션은 그 뒤에 객체에 다른 편집이 하나라도 가해지면, 그 편집이 다른 속성에 대한 것이더라도 되돌릴 수 없습니다. 다시 말해, 객체에 대한 액션은 그 액션이 그 객체에 대한 가장 최근 편집일 때만 되돌릴 수 있습니다.
* 액션 제출 후 액션 되돌리기 설정을 껐다면, 다시 켜더라도 그 액션은 되돌릴 수 없습니다.

액션 되돌리기는 객체 인스턴스에 대한 편집만 되돌리며, 알림이나 웹훅 같은 부수 효과(side effect)는 되돌리지 않습니다. 또한 적용된 액션이 했던 방식으로 부수 효과를 다시 호출하지도 않습니다.

**설명**: 첫 번째 조건을 예로 들면, 사용자 U가 10:00에 `Ticket` T1의 `status`를 `closed`로 바꾸는 액션을 실행했고, 10:01에 다른 액션이 T1의 `assignee`를 바꿨다면, 10:00의 액션은 더 이상 되돌릴 수 없습니다. 되돌리기는 "가장 최근 편집을 취소"하는 방식이므로, 그 위에 다른 편집이 쌓이면 어디까지 되돌려야 할지 모호해지기 때문입니다.

<a id="undoing-a-delete-action-without-the-revert-action-toast"></a>
### 되돌리기 토스트 없이 삭제 액션 취소하기 (Undoing a delete action without the revert action toast)

삭제 액션을 수행한 뒤 삭제를 취소하고 싶은데 되돌리기 토스트를 더 이상 사용할 수 없다면, 사용할 수 있는 복구 방법은 다음뿐입니다.

* 새 객체 타입으로 마이그레이션하고 함수를 사용해 원하는 편집을 복사합니다. 또는
* 객체 타입의 모든 편집을 삭제(drop)합니다.

**설명**: 두 번째 방법인 "모든 편집 삭제"는 사용자들이 액션으로 가한 편집을 전부 버리고 객체 타입을 백킹 데이터소스의 원래 상태로 되돌리는 것입니다. 삭제된 객체에 해당하는 행이 백킹 데이터소스에 남아 있다면 그 객체는 다시 나타나겠지만, 그 객체 타입에 가해진 다른 모든 사용자 편집도 함께 사라진다는 큰 대가가 따릅니다.

> **중간 요약**: 이후에 다른 편집이 있었거나 설정을 한 번 껐다면 되돌릴 수 없고, 부수 효과는 되돌려지지 않습니다. 토스트를 놓친 삭제는 새 객체 타입으로 옮기거나 모든 편집을 버리는 방법밖에 없습니다.

## 정리

- 액션 되돌리기는 OSv2 객체 타입을 수정하는 액션에서 Form 탭의 **Allow revert after action submission** 토글로 켭니다.
- 액션을 적용한 사용자만, 성공 토스트의 **Undo**로 되돌릴 수 있으며 토스트가 유일한 기회입니다.
- 대상 객체에 이후 편집이 있었거나 설정이 한 번 꺼졌던 경우 되돌릴 수 없습니다.
- 알림, 웹훅 같은 부수 효과는 되돌려지지 않습니다.
- 토스트를 놓친 삭제는 새 객체 타입 마이그레이션 또는 모든 편집 삭제로만 복구할 수 있습니다.
