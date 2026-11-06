# 온톨로지에 변경 사항 저장하기 (Save changes to the Ontology)

- 원문: https://www.palantir.com/docs/foundry/ontology-manager/save-changes/
- 사이드바 위치: Applications > Ontology Manager > Change management > Save changes to the Ontology

이 페이지는 Ontology Manager에서 만든 변경을 실제 온톨로지에 반영(저장)하는 절차를 설명합니다. 저장 전 검토 대화상자, 오류와 경고 처리, 다른 사용자의 변경과의 병합 충돌, 변경 취소, 위험한 변경에 대한 확인 절차, 저장 실패 시 문제 해결까지 다룹니다.

<a id="save-your-changes"></a>
## 변경 사항 저장하기 (Save your changes)

Ontology Manager에서 만든 모든 변경은 작업 중(work-in-progress) 상태로 로컬에 저장됩니다. 이 온톨로지 변경을 다른 사람도 사용할 수 있고 사용자용 애플리케이션에 반영되게 하려면 변경 사항을 저장해야 합니다. 변경을 저장하려면 다음과 같이 합니다.

1. 애플리케이션 오른쪽 위 모서리의 애플리케이션 헤더에서 **Save**를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/save-button-header.png" alt="Save 버튼" width="400"/>

2. **Review edits** 대화상자를 열어 모든 변경 사항을 검토합니다.
3. 마지막으로 **Save**를 선택해 온톨로지를 갱신합니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/save-button-review.png" alt="검토 대화상자의 Save 버튼" width="600"/>

**설명**: 편집 내용은 저장 전까지 나만의 작업 상태(working state)에만 존재하고, 다른 사용자나 Workshop 같은 애플리케이션에는 보이지 않습니다. 데이터베이스 트랜잭션에서 `COMMIT` 전의 변경이 다른 세션에 보이지 않는 것과 같은 구조이며, **Save**가 `COMMIT`에 해당합니다.

> **중간 요약**: Ontology Manager의 변경은 저장 전까지 작업 중 상태로만 남고, 헤더의 **Save**, **Review edits** 대화상자 검토, **Save** 순으로 저장해야 다른 사용자와 애플리케이션에 반영됩니다.

<a id="handle-errors-and-warnings"></a>
## 오류와 경고 처리하기 (Handle errors and warnings)

**Save** 버튼이 회색으로 비활성화되어 있다면, 저장을 막는 오류가 있을 수 있습니다. 이를 해결하려면 다음과 같이 할 수 있습니다.

* 변경 사항을 스크롤하면서 각 줄에 표시된 오류 메시지를 확인하거나,
* **Review edits** 대화상자 위쪽의 **Errors** 탭을 선택해 저장을 막고 있는 오류를 확인합니다.

**Review edits** 대화상자는 반영하기를 권장하는 변경에 대한 경고도 각 줄과 **Warnings** 탭에 보여 줍니다. 오류는 저장하려면 반드시 처리해야 하지만, 경고는 저장을 막지 않습니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/save-review-edits-error.png" alt="오류 검토하기" width="600"/>

오류가 발생하면, 열기 바로가기를 사용해 저장 전에 편집해야 하는 리소스로 이동할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/save-review-edits-error-navigate.png" alt="편집할 리소스로 이동하기" width="600"/>

함수(Functions)에 대한 변경은 Ontology Manager가 아니라 Functions 저장소에서만 할 수 있습니다. Ontology Manager의 Functions 엔터티 뷰에서 Functions Repository로 이동할 수 있습니다.

**설명**: 오류와 경고의 구분은 컴파일러의 오류와 경고 구분과 같은 방식입니다. 컴파일 오류가 있으면 실행 파일이 만들어지지 않지만 경고만 있으면 빌드는 되는 것처럼, 오류가 하나라도 남아 있으면 저장할 수 없고 경고만 있으면 저장할 수 있습니다.

> **중간 요약**: 오류는 **Errors** 탭이나 줄 단위 메시지로 확인해 반드시 고쳐야 저장할 수 있고, 경고는 저장을 막지 않습니다. 함수는 Ontology Manager가 아닌 Functions 저장소에서만 수정합니다.

<a id="handle-updates-and-merge-conflicts"></a>
## 업데이트와 병합 충돌 처리하기 (Handle updates and merge conflicts)

내가 변경을 시작한 뒤로 다른 사용자가 온톨로지를 저장한 경우에도 **Save** 버튼이 회색으로 비활성화될 수 있습니다. 이때는 Review edits 대화상자 위쪽에서 **Update**를 선택해 다른 사용자의 변경을 내 변경과 병합해야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/save-review-edits-update-merge.png" alt="다른 편집 내용으로 온톨로지 갱신하기" width="600"/>

다른 사용자가 만든 변경과 내 작업 상태의 변경 사이에 병합 충돌(merge conflict)이 있을 수 있습니다. 이 경우 충돌을 해결하라는 안내가 나타납니다. 온톨로지 최신 버전에 있는 변경을 유지할지, 내 작업 상태의 변경으로 덮어쓸지 선택할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/save-review-edits-merge-conflict.png" alt="온톨로지 편집의 병합 충돌" width="600"/>

**설명**: 병합 충돌은 두 사람이 같은 대상을 서로 다르게 바꾸었을 때 생깁니다. 예를 들어 내가 Flight 객체 타입의 `origin` 속성 표시 이름을 "출발 공항"으로 바꾸는 동안, 다른 사용자가 같은 속성 표시 이름을 "출발지"로 바꿔 먼저 저장했다면 두 값 중 하나를 골라야 합니다. Git에서 `git pull` 후 같은 줄을 서로 다르게 고친 부분을 해결하는 과정과 같은 절차입니다.

> **중간 요약**: 다른 사용자가 먼저 저장했다면 **Update**로 그 변경을 내 작업 상태에 병합해야 하며, 충돌이 있으면 최신 버전의 변경을 유지할지 내 변경으로 덮어쓸지 선택합니다.

<a id="discard-your-changes"></a>
## 변경 사항 취소하기 (Discard your changes)

내가 편집한 온톨로지 리소스는 각각 **Review edits** 대화상자에 별도 항목으로 나타납니다. **Review edits** 대화상자에서 항목 위에 마우스를 올리고 휴지통 아이콘을 선택하면 그 리소스에 대해 만든 변경을 취소할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/save-review-edits-discard.png" alt="편집 내용 취소하기" width="600"/>

애플리케이션 오른쪽 위 헤더의 **Discard** 버튼을 선택하거나 **Review edits** 대화상자 아래쪽의 **Discard**를 선택하면, 언제든 온톨로지에 만든 저장하지 않은 변경을 모두 취소할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/save-review-edits-discard-all.png" alt="모든 편집 내용 취소하기" width="600"/>

<a id="respond-to-a-warning-message"></a>
## 경고 메시지에 응답하기 (Respond to a warning message)

**Review edits** 대화상자에서 변경 사항을 검토하는 동안, 저장하기 전에 경고를 확인하라는 경고 메시지가 나타날 수 있습니다.

객체 타입과 그 속성에 대한 편집은 해당 객체 타입에 의존하는 애플리케이션을 망가뜨리는 영향을 줄 수 있습니다. 또한 객체 타입에 라이트백(writeback)이 활성화되어 있다면, 그 타입의 객체에 대해 이루어진 편집 이력이 제거되지 않도록 해당 객체 타입을 편집할 때 각별히 주의해야 합니다.

어떤 변경이 파괴적일 수 있는지에 대한 전체 설명은 [잠재적인 호환성 파괴 변경](../../../02_define-ontologies/02_object-and-link-types/02_object-types/03_edit-object-type.md)에 대한 문서를 참고하세요.

경고 메시지에 자세히 적힌 변경의 영향을 읽고 그 의미를 이해했다면, 편집한 엔터티의 이름을 입력해 저장을 진행할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/save-review-edits-warning.png" alt="편집에 대한 경고 메시지" width="600"/>

**설명**: 라이트백은 사용자가 액션 등으로 객체에 가한 편집(edit)을 원본 데이터셋과 별도로 기록해 두는 기능입니다. 예를 들어 사용자가 Flight F100의 상태를 "지연"으로 바꾼 기록이 저장되어 있는데, 객체 타입의 기본 키 속성을 바꾸거나 속성을 삭제하면 이 기록을 어느 객체, 어느 속성에 다시 적용할지 알 수 없게 되어 편집 이력이 사라질 수 있습니다. 엔터티 이름을 직접 입력하게 하는 것은 GitHub에서 저장소를 삭제할 때 저장소 이름을 입력하게 하는 것과 같은 실수 방지 장치입니다.

> **중간 요약**: 리소스별 휴지통 아이콘이나 **Discard** 버튼으로 미저장 변경을 취소할 수 있습니다. 애플리케이션을 망가뜨리거나 라이트백 편집 이력을 잃게 할 수 있는 변경은 경고 메시지가 뜨며, 엔터티 이름을 입력해야 저장이 진행됩니다.

<a id="troubleshooting-when-a-save-fails"></a>
## 저장이 실패할 때 문제 해결하기 (Troubleshooting when a save fails)

저장할 때 온톨로지를 구동하는 백엔드 서비스에 문제가 생기면, 아래 이미지처럼 오류 메시지 "토스트"(팝업)가 나타납니다. 저장할 수 없는 이유를 설명하는 문장 끝에 오류 메시지 이름이 출력됩니다. 오류 메시지 이름은 `OntologyMetadata:` 또는 `Phonograph2:` 접두사로 시작합니다.

<img src="https://www.palantir.com/docs/resources/foundry/ontology-manager/save-error-message.png" alt="오류 메시지" width="500"/>

온톨로지 문서 곳곳에서 온톨로지에 대한 여러 변경과 관련된 가장 흔한 오류들을 다루고 있습니다. 오류 메시지가 보이면 문서에서 검색해 그 오류와 해결 방법이 문서화되어 있는지 확인하세요.

## 정리

- Ontology Manager의 변경은 작업 중 상태로만 남으며, **Save**와 **Review edits** 검토를 거쳐 저장해야 다른 사용자와 애플리케이션에 반영됩니다.
- 오류는 반드시 고쳐야 저장할 수 있고 경고는 저장을 막지 않습니다. 함수는 Functions 저장소에서만 수정합니다.
- 다른 사용자가 먼저 저장했다면 **Update**로 병합하고, 충돌 시 최신 버전과 내 변경 중 하나를 고릅니다.
- 리소스별 또는 전체 변경을 취소할 수 있으며, 위험한 변경은 엔터티 이름을 입력해 확인해야 저장됩니다.
- 저장 실패 시 토스트에 표시되는 `OntologyMetadata:` 또는 `Phonograph2:` 오류 이름으로 문서를 검색합니다.
