# 구조체 속성 타입 편집하기 (Edit struct types)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/edit-struct-type/
- 사이드바 위치: Define Ontologies > Object and link types > Structs > Edit struct types

이 페이지는 이미 만든 구조체(struct) 속성의 필드를 Ontology Manager에서 수정하는 절차를 안내합니다. 절차 자체는 간단하지만, 구조체 필드의 API 이름을 바꾸면 인덱스가 새로 만들어지고 이를 참조하는 애플리케이션도 고쳐야 한다는 주의 사항이 중요합니다.

1. Ontology Manager에서 왼쪽 사이드바의 **Object types** 탭을 열고 기존 객체 타입을 선택합니다.
2. 객체 타입 세부 정보 페이지에서 왼쪽 사이드바의 **Properties** 탭을 열고, **Properties** 표에서 해당 구조체 속성 타입을 선택합니다.
3. **Property editor** 패널에서 **Struct fields** 영역까지 스크롤해 편집하려는 구조체 필드를 선택합니다. 변경한 편집 개수는 Ontology Manager 화면 오른쪽 위에 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/Edit-struct.png" alt="'Property editor' 패널의 구조체 필드." width="500" />

4. **Edit struct field** 대화 상자에서 필요한 편집을 한 뒤 **Confirm**을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/confirm-struct-edit.png" alt="'Edit struct field' 대화 상자." width="500" />

**주의**: 구조체 필드의 API 이름을 바꾸면 새 구조체 필드 RID가 생성됩니다. 이는 속성 타입의 속성 ID를 바꿀 때의 동작과 비슷하게 기존 인덱스를 덮어씁니다. 업데이트된 구조체 필드를 참조하는 모든 애플리케이션도 함께 업데이트해야 합니다.

**설명**: RID는 시스템이 자동으로 부여하는 고유 식별자입니다. API 이름을 `zip`에서 `postalCode`로 바꾸면 시스템은 이를 "기존 필드의 이름 변경"이 아니라 "새 필드"로 취급해 새 RID를 만들고, 그 필드의 인덱스 데이터도 다시 만들어집니다. 그 결과 Workshop 모듈이나 함수 코드에서 예전 이름 `zip`으로 이 필드를 참조하던 곳은 더 이상 동작하지 않으므로, 참조를 새 이름으로 고쳐야 합니다. 3단계의 "편집 개수"는 아직 저장되지 않은 변경 사항의 개수로, 저장하기 전까지는 온톨로지에 반영되지 않습니다.

## 정리

- 구조체 필드는 객체 타입의 **Properties** 탭에서 구조체 속성을 선택한 뒤, **Property editor**의 **Struct fields** 영역에서 필드를 골라 편집합니다.
- **Edit struct field** 대화 상자에서 수정하고 **Confirm**을 누르면 되며, 편집 개수는 화면 오른쪽 위에 표시됩니다.
- 구조체 필드의 API 이름을 바꾸면 새 RID가 생성되고 기존 인덱스를 덮어쓰므로, 이 필드를 참조하는 애플리케이션도 함께 고쳐야 합니다.
