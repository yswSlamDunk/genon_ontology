# Object Explorer 구성하기 (Configure Object Explorer)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/configure/
- 사이드바 위치: Applications > Object Explorer > Configure Object Explorer

이 페이지는 관리자나 온톨로지 편집자가 Object Explorer의 동작을 조정하는 방법을 모아 둔 페이지입니다. 홈 페이지의 객체 타입 그룹, 액션 성공 알림에 Object View 링크 넣기, 특정 액션 숨기기, 탐색 결과를 동적 객체 집합으로 저장하는 액션, 기본 레이아웃을 관리하는 관리자 권한을 다룹니다. 대부분의 설정은 액션 파라미터에 타입 클래스(type class)라는 메타데이터를 붙이는 방식으로 이루어집니다.

**설명**: 타입 클래스는 속성이나 파라미터에 붙이는 `kind`와 `name` 한 쌍의 태그입니다. 데이터 값 자체에는 영향을 주지 않고, 그 태그를 읽는 애플리케이션(여기서는 Object Explorer)이 특정 동작을 하도록 알려 주는 용도입니다. 프로그래밍 언어의 어노테이션(예: Java의 `@Deprecated`)이 컴파일러나 프레임워크에 추가 정보를 주는 것과 같은 방식입니다.

<a id="customizable-object-type-groupings-on-home-page"></a>
### 홈 페이지의 객체 타입 그룹 사용자 지정 (Customizable object type Groupings on Home Page)

객체 타입을 그룹으로 만들어 추가하려면 Ontology Manager에서 해당 객체 타입의 [메타데이터 위젯](../../02_define-ontologies/02_object-and-link-types/02_object-types/02_create-object-type.md#add-metadata-for-a-new-object-type)으로 갑니다. 이 작업을 하려면 온톨로지에 대한 편집자 권한이 있어야 합니다.

사용자 지정 그룹이 구성되어 있으면, 어떤 그룹에도 속하지 않는 숨겨지지 않은 객체 타입은 페이지 맨 아래의 "Other"(기타)라는 그룹에 배치됩니다.

<a id="linking-to-object-view-from-actions-success-toast"></a>
### 액션 성공 토스트에서 Object View로 연결하기 (Linking to object view from Actions success toast)

액션이 성공적으로 적용되면, 성공 토스트(확인 팝업 메시지)에 생성되거나 수정된 객체 인스턴스의 Object View로 가는 하이퍼링크를 표시하도록 구성할 수 있습니다. 이렇게 하면 새로 만들었거나 수정한 객체의 Object View로 빠르게 이동할 수 있습니다.

성공 토스트를 이렇게 구성하려면, 해당 *객체 생성(create object)* 액션의 Primary Key 파라미터, 또는 해당 *객체 수정(modify object)* 액션의 Object Reference List 파라미터에 새 타입 클래스(아래 코드 참고)를 추가해야 합니다. 타입 클래스는 Ontology Editor 앱에서 추가할 수 있으며, 온톨로지 편집 권한이 필요합니다.

```yaml
kind: "actions"
name: "view_object_with_type:<OBJECT_TYPE_ID>"
```

**설명**: `<OBJECT_TYPE_ID>` 자리에 링크로 보여 줄 객체 타입의 ID(예: `aircraft`)를 넣습니다. 이 태그가 붙은 파라미터 값(새 객체의 기본 키, 또는 수정한 객체 참조)을 Object Explorer가 읽어서 "이 타입의 이 객체로 가는 링크"를 토스트에 만들어 줍니다.

다음 예시는 새로 생성한 객체 인스턴스의 Object View로 연결되는 성공 토스트를 추가하는 방법을 보여 줍니다.

1. 온톨로지 액션 "Create New Aircraft"는 새 Aircraft 객체 인스턴스를 생성할 수 있게 해 줍니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_actions_success_toast_typeclass.png" alt="액션 성공 토스트 타입 클래스"/>

2. 팝업 메뉴에서 관련 정보를 입력한 뒤 "Submit"(제출)을 선택합니다. 이 경우 Id가 `187`이고 Aircraft Registration이 `Q-AHE`인 Aircraft 객체 인스턴스가 생성됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_apply_actions.png" alt="액션 적용"/>

3. 앞에서 설명한 타입 클래스를 Primary Key 파라미터에 추가해 두었으므로, 성공 토스트에 새로 생성된 객체 인스턴스 `Q-AHE`로 가는 하이퍼링크가 표시됩니다. 하이퍼링크를 클릭하면 이 객체 인스턴스의 Object View로 이동합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_success_toast.png" alt="성공 토스트"/>

<a id="hiding-actions-in-object-explorer"></a>
### Object Explorer에서 액션 숨기기 (Hiding Actions in Object Explorer)

액션은 [액션 타입 문서](../../02_define-ontologies/03_action-types/04_use-actions.md)에 설명된 대로 Object Explorer의 세 곳에 자동으로 표시됩니다. 어떤 객체 타입의 액션을 숨기려면 Ontology Editor 앱에서 Object Reference List 파라미터에 `hubble-oe:hide-action` 타입 클래스를 추가합니다. 이 작업을 하려면 온톨로지 편집 권한이 있어야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_hide_actions_typeclass.png" alt="액션 숨기기 타입 클래스" width = "500"/>

> **중간 요약**: 홈 페이지 그룹은 객체 타입의 메타데이터에서 정하며, 그룹이 없는 타입은 "Other"로 갑니다. 액션 파라미터에 타입 클래스를 붙이면 성공 토스트에 Object View 링크를 넣거나(`actions` / `view_object_with_type:...`), Object Explorer에서 액션을 숨길 수 있습니다(`hubble-oe:hide-action`).

<a id="actions-on-a-dynamic-object-set"></a>
## 동적 객체 집합에 대한 액션 (Actions on a Dynamic Object Set)

**주의**: 이 기능은 아직 개발 중이며, 자동 마이그레이션 *없이* 지원 중단될 수 있습니다. 따라서 이 기능을 쓰면 나중에 액션을 수동으로 마이그레이션해야 할 위험을 감수하게 됩니다. 이 기능을 사용할 계획이라면 사용하기 전에 Palantir 담당자에게 문의하십시오.

경우에 따라 탐색 결과를 정적 객체 집합이 아니라 동적 객체 집합으로 사용하고 싶을 수 있습니다. 동적 객체 집합은 적용된 필터의 표현으로 저장됩니다. 따라서 새 데이터가 그 필터에 맞게 되거나 맞지 않게 되면 객체 집합도 갱신됩니다.

**설명**: 정적 객체 집합은 저장 시점의 객체 목록(예: 기본 키 10개)을 그대로 보관하고, 동적 객체 집합은 `MSN BETWEEN 5025 AND 5050` 같은 조건만 보관합니다. 동적 집합은 조회할 때마다 조건을 다시 평가하므로, 데이터베이스의 뷰(view)가 조회 시점의 테이블 내용으로 결과를 만드는 것과 같은 방식으로 동작합니다.

이 기능의 가장 일반적인 사용 사례는 동적 객체 집합에 대한 참조를 객체 인스턴스의 속성 값으로 추가하는 것입니다.

다음 예시는 Aircraft Manufacturer's Serial Number(MSN, 항공기 제조사 일련번호)를 기준으로 동적인 `Aircraft` 객체 집합을 `Airline` 객체에 할당하는 액션을 만드는 방법을 보여 줍니다.

1. `Airline` 객체 타입에 "Aircraft" 객체 집합에 대한 참조를 값으로 넣을 수 있는 `String` 속성(이 예에서는 `Aircraft Set`)이 있는지 확인합니다. 이 속성의 값 서식(value formatting)을 활성화하고 드롭다운에서 **Resource RID**를 선택합니다. 이렇게 하면 이 속성에 할당된 객체 집합 RID가 Object Explorer에서 해당 객체 집합으로 가는 링크로 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_value_formatting.png" alt="값 서식" width="300"/>

2. 이제 액션을 만들 준비가 되었습니다. 액션에 `Airline` 객체 타입의 `Aircraft Set` 속성에 대한 **Modify Object** 규칙을 추가합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_modify_object_rule.png" alt="객체 수정 규칙" width="300"/>

3. `Aircraft Set` 파라미터에 다음 타입 클래스를 추가합니다. 여기서 `<OBJECT_TYPE_ID>`는 탐색 화면에서 이 액션을 옵션으로 표시하려는 객체 타입의 ID입니다(이 예에서는 `Aircraft` 객체 타입).

```yaml
kind: "hubble-oe-object-set-rid"
name: <OBJECT_TYPE_ID>
```

4. 역시 `Aircraft Set` 파라미터에 다음 타입 클래스를 추가합니다. 여기서 `<RESOURCE_RID>`는 동적 객체 집합에 부여하려는 올바른 권한을 가진 폴더의 RID입니다. 이 객체 집합은 프로젝트에 노출되지 않고 검색되지도 않습니다. 이 RID는 저장된 객체 집합이 어떤 권한을 받아야 하는지 지정하는 데에만 쓰입니다.

```yaml
kind: "hubble-oe-security-rid"
name: <RESOURCE_RID>
```

**설명**: 3단계의 타입 클래스는 "이 파라미터에는 현재 탐색을 객체 집합으로 저장한 RID를 넣는다, 그리고 이 액션은 `Aircraft` 탐색에서 보인다"는 뜻이고, 4단계의 타입 클래스는 "그렇게 저장되는 객체 집합의 접근 권한은 이 폴더의 권한을 따른다"는 뜻입니다. 저장된 객체 집합도 Foundry 리소스이므로 누가 볼 수 있는지 정해야 하는데, 이를 기존 폴더의 권한에서 빌려 오는 것입니다.

5. 액션을 만든 뒤 `Aircraft` 객체에 대한 탐색으로 이동합니다. 예를 들어 MSN이 5,025에서 5,050 사이인 모든 `Aircraft`를 Frontier Airlines에 할당하고 싶다고 합시다. 그러려면 해당 객체로 필터링한 뒤 Actions 드롭다운에서 새로 만든 액션을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_assign_aircraft.png" alt="항공기 할당"/>

그러면 현재 탐색에 대한 동적 객체 집합이 자동으로 생성되고, 드롭다운에서 선택한 `Airline` 객체의 `Aircraft Set` 속성에 할당됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_choose_airline.png" alt="항공사 선택" width="300"/>

6. 이제 "Frontier Airlines Inc." 객체의 `Aircraft Set` 속성에 MSN이 5,025에서 5,050 사이인 `Aircraft` 집합으로 가는 링크가 표시됩니다. 이 범위의 MSN을 가진 새 `Aircraft`가 온톨로지에 추가되거나 현재 집합에 있는 `Aircraft` 중 일부가 온톨로지에서 제거되면, 집합은 자동으로 갱신됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_airline_exploration.png" alt="항공사 탐색"/>

7. Linked Objects Exploration 위젯을 사용하면 "Frontier Airlines Inc."의 Object View에서 이 동적 객체 집합의 내용을 볼 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_linked_objects_exploration.png" alt="연결된 객체 탐색"/>

이 위젯을 구성할 때 `Initial Exploration`을 **From Object Set RID Property**로, `Object Set RID Property`를 **Aircraft Set**으로 설정합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_linked_objects_exploration_config.png" alt="연결된 객체 탐색 구성"/>

> **중간 요약**: 동적 객체 집합은 필터 조건으로 저장되어 데이터가 바뀌면 자동으로 갱신됩니다. 문자열 속성(Resource RID 서식)과 Modify Object 규칙, 그리고 `hubble-oe-object-set-rid`와 `hubble-oe-security-rid` 타입 클래스를 이용해 탐색 결과를 다른 객체의 속성 값으로 할당할 수 있습니다. 이 기능은 개발 중이므로 사용 전 Palantir 담당자와 상의해야 합니다.

<a id="default-layout-administrative-users"></a>
### 기본 레이아웃 관리자 (Default Layout Administrative Users)

`hubble-exploration-admins` multipass 그룹에 속하거나 Control Panel에서 `Object Exploration Admin` 애플리케이션 권한을 가진 사용자는 객체 타입의 기본 레이아웃 이름을 바꾸거나, 삭제하거나, 저장할 수 있습니다. 레이아웃에는 결과 표 구성에 적용한 모든 변경 사항이 포함됩니다. 관리자 사용자이고 어떤 레이아웃을 모든 사용자의 기본값으로 지정하려면, 아래 이미지처럼 레이아웃을 저장할 때 **Set as default layout** 아래의 **For all users** 체크박스를 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-explorer/admin_edit_layout_dialog_for_admins.png" alt="기본 레이아웃 편집" width="300"/>

## 정리

- 홈 페이지의 객체 타입 그룹은 Ontology Manager의 메타데이터 위젯에서 지정하며 온톨로지 편집자 권한이 필요합니다.
- 액션 파라미터에 타입 클래스를 붙여 성공 토스트에 Object View 링크를 넣거나 Object Explorer에서 액션을 숨길 수 있습니다.
- 개발 중인 기능으로, 탐색 결과를 필터 조건 기반의 동적 객체 집합으로 저장해 다른 객체의 속성에 할당하는 액션을 만들 수 있습니다.
- `hubble-exploration-admins` 그룹이나 `Object Exploration Admin` 권한을 가진 사용자는 모든 사용자의 기본 레이아웃을 지정할 수 있습니다.
