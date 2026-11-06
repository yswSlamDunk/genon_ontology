# 권한 (Permissions)

- 원문: https://www.palantir.com/docs/foundry/action-types/permissions/
- 사이드바 위치: Define Ontologies > Action types > Permissions

이 페이지는 액션 타입에 적용되는 권한, 특히 "누가 이 액션을 실행(apply)할 수 있는가"를 결정하는 요소들을 정리합니다. 객체 타입의 편집 허용 방식(액션으로만 편집 허용인지, 다른 경로도 허용인지)에 따라 사용자에게 필요한 권한이 크게 달라지며, 부수 효과(side effect)인 웹훅과 알림에도 별도의 권한 규칙이 있습니다.

권한은 액션 타입에 다음과 같은 방식으로 적용됩니다.

* 누가 특정 액션 타입을 볼 수 있는가?
* 누가 특정 액션 타입을 편집할 수 있는가?
* 누가 특정 파라미터 집합으로 액션 타입을 실행할 수 있는가?

<a id="apply-action"></a>
## 액션 실행 (Apply action)

액션 타입을 실행할 수 있는지는 그 액션이 편집하는 객체 타입과 링크 타입의 구성에 따라 달라집니다. 어떤 경우든 액션을 제출하는 사용자는 편집 대상 객체 타입과 링크 타입, 그리고 그 데이터소스를 볼 수 있어야 하고, [제출 조건(submission criteria)](08_submission-criteria.md)을 통과해야 합니다. 객체 타입이 액션을 통한 편집만 허용하는 경우, 사용자는 자신이 볼 수 있는 모든 객체에 대해 편집할 수 있습니다. 액션 외의 편집도 허용하는 객체 타입과 링크 타입의 경우, 객체 타입이나 링크 타입이 데이터셋을 백킹으로 하고 있다면 사용자는 라이트백(writeback) 데이터셋에 대한 편집 권한도 필요합니다. 객체 타입이나 링크 타입이 [Restricted View](https://www.palantir.com/docs/foundry/security/restricted-views/)를 백킹으로 하고 있다면, 사용자는 편집 정책(edit policy)을 통과해야 합니다.

접근 권한을 더 넓게 검토하려면 워크스페이스 사이드바의 **Check access** 패널을 사용해 사용자의 Workshop 모듈 접근 권한을 확인할 수 있습니다. 여기에는 모듈이 의존하는 액션 타입과 그 제출 조건에 대한 접근도 포함됩니다. 자세한 내용은 [Check access 패널 문서](https://www.palantir.com/docs/foundry/security/checking-permissions/)를 참고하세요.

**주의**: 읽기 시점에만 적용됨(Read-time enforcement only). 행 및 열 접근 제어([restricted view](https://www.palantir.com/docs/foundry/security/restricted-views/), [객체 보안 정책](../../06_ontology-architecture/02_object-permissioning/07_object-security-policies.md), [속성 보안 정책](https://www.palantir.com/docs/foundry/security/property-security-markings/) 포함)는 사용자가 액션을 호출할 때 읽을 수 있는 대상을 걸러 냅니다. 이 제어는 액션의 쓰기에는 적용되지 않습니다. 데이터가 하위로 흘러가는 동안에도 보호되도록 하려면, 이 제어를 [마킹(marking)](https://www.palantir.com/docs/foundry/security/markings/)이나 [분류 기반 접근 제어(Classification-based Access Control)](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/)와 함께 사용하세요. 전체 모델은 [접근 제어 전파(Access control propagation)](https://www.palantir.com/docs/foundry/security/access-control-propagation/)를 참고하세요.

**설명**: 라이트백 데이터셋은 사용자의 편집 결과가 기록되는 데이터셋으로, 원본 데이터셋과 사용자 편집을 합친 결과를 담습니다. Restricted View는 행 단위 보안 정책을 붙인 데이터셋 뷰로, SQL에서 `WHERE` 조건으로 사용자별 접근 가능한 행만 보여 주는 보안 뷰와 같은 역할을 합니다. "읽기 시점에만 적용"이란, 예를 들어 사용자가 볼 수 없는 행은 액션의 입력으로 고를 수 없지만, 액션이 만들어 낸 새 데이터에는 그 행 수준 제한이 자동으로 따라붙지 않는다는 뜻입니다. 그래서 하위 데이터까지 보호하려면 데이터 자체에 붙는 마킹을 함께 써야 합니다.

<a id="submission-criteria"></a>
### 제출 조건 (Submission criteria)

액션 제출 조건은 누가 액션을 실행할 수 있는지를 세밀하게 제어합니다. 간단한 제출 조건은 특정 사용자 ID나 그룹 ID를 요구할 수 있고, 파라미터의 정보와 조합할 수 있습니다. 자세한 내용은 [제출 조건 문서](08_submission-criteria.md)를 참고하세요.

<a id="read-and-write-authorizations"></a>
### 읽기 및 쓰기 권한 부여 (Read and write authorizations)

읽기 및 쓰기 권한 부여(read and write authorization)는 액션이 직접 읽거나 다른 로직으로부터 입력으로 받을 수 있는 마킹된 데이터를 제한하고, 액션이 만들거나 수정하는 데이터에 최소 보안을 강제합니다. 자세한 내용은 [읽기 및 쓰기 권한 부여 문서](20_read-write-authorizations.md)를 참고하세요.

<a id="action-log-permissions"></a>
### 액션 로그 권한 (Action log permissions)

액션 타입에 [액션 로그(action log)](26_action-log.md)가 구성되어 있으면, 액션을 제출하는 사용자는 액션 로그 객체 타입에 대한 적절한 권한이 필요합니다. 액션이 만들거나 수정하는 다른 모든 객체 타입에도 같은 요구 사항이 적용됩니다. 이 권한이 없으면 액션은 제출 시점에 실패합니다.

<a id="object-edits-permissions"></a>
### 객체 편집 권한 (Object edits permissions)

객체 편집은 액션을 통해서만 허용되도록 잠글 수도 있고, 액션, Foundry Forms, Object Explorer 직접 편집, API 호출을 통한 편집을 허용하도록 다시 열 수도 있습니다. 여러 워크플로에 걸쳐 일관된 보안 체계를 강제하기 위해, 새 객체 타입은 기본적으로 액션을 통한 편집만 허용합니다. 다른 형태의 편집은 새로 사용하는 것을 권장하지 않습니다.

액션을 통한 편집만 허용하는 객체 타입에서는, 액션을 제출하는 사용자가 편집 대상 객체에 대해 `Read` 권한만 있으면 됩니다. 따라서 사용자가 자신이 볼 수 없는 객체를 만들 수도 있습니다.

반대로 데이터셋을 백킹으로 하는 객체 타입이 액션, Foundry Forms, Object Explorer 직접 편집, API 호출로 편집될 수 있는 경우, 액션을 제출하는 사용자는 편집되는 모든 객체의 라이트백 데이터셋에 대해 `Edit` 권한을 가져야 합니다. `Edit` 권한이 있는 사용자는 라이트백 데이터셋의 모든 데이터를 볼 수 있습니다.

따라서 객체 타입을 액션, Foundry Forms, Object Explorer 직접 편집, API 호출로 편집할 수 있도록 설정하는 것은 권장하지 않습니다. 단지 객체 편집을 위해 `Edit` 권한을 부여하면, 온톨로지 편집 워크플로를 완료하는 데 필요한 것보다 많은 데이터가 사용자에게 노출될 수 있기 때문입니다.

어느 라이트백 설정을 쓰든, 액션 타입 구성 화면에는 영향을 받는 하위 객체 타입의 권한 설정이 표시되지 않습니다. 액션 타입을 구성하는 사람이 이 권한이 올바른지 직접 확인해야 합니다.

객체 타입의 편집 권한을 "Only allow edits via actions"(액션을 통한 편집만 허용)로 바꿔도 과거에 액션 외의 방법으로 이루어진 편집은 제거되지 않지만, 이후 Foundry Forms, Object Explorer 직접 편집, API 호출을 통한 편집은 막힙니다.

![액션을 통한 편집만 허용하는 설정을 권장합니다.](https://www.palantir.com/docs/resources/foundry/action-types/recommended-writeback-setting.png)

[라이트백 권한에 대해 더 알아보세요.](../../06_ontology-architecture/02_object-permissioning/05_configuring-rv-access-controls.md)

**설명**: 두 설정의 차이를 예로 보겠습니다. Employee 객체 타입의 라이트백 데이터셋에 직원 1,000명의 급여가 들어 있고, 사용자 김 씨는 자기 팀 직원 10명만 볼 수 있다고 합시다. "액션을 통한 편집만 허용"이면 김 씨는 그 10명에 대한 `Read` 권한만으로 액션을 통해 이들의 정보를 수정할 수 있습니다. 반면 "다른 경로도 허용"이면 김 씨에게 라이트백 데이터셋의 `Edit` 권한이 있어야 하고, 이 권한은 데이터셋 전체에 걸쳐 있으므로 김 씨가 1,000명 전원의 데이터를 볼 수 있게 됩니다. 최소 권한 원칙(principle of least privilege)에 따라 전자가 권장되는 이유입니다.

> **중간 요약**: 액션을 실행하려면 편집 대상 객체 타입, 링크 타입, 데이터소스를 볼 수 있고 제출 조건을 통과해야 합니다. 액션으로만 편집을 허용하는 객체 타입은 `Read` 권한만으로 편집이 가능해 노출이 적고, 다른 편집 경로를 허용하면 라이트백 데이터셋 전체에 대한 `Edit` 권한이 필요해 권장되지 않습니다. 행과 열 단위 접근 제어는 읽기에만 적용되며, 액션 로그가 있으면 그 객체 타입에 대한 권한도 필요합니다.

<a id="side-effect-permissions"></a>
## 부수 효과 권한 (Side effect permissions)

액션을 설정할 수 있는 사용자라면 누구나 부수 효과(side effect)를 구성할 수 있습니다.

* 웹훅 부수 효과는 기본적으로 켜져 있지 않습니다. 액션 설정 페이지에서 웹훅을 사용하려면 먼저 Data Connection 앱에서 웹훅 플러그인을 구성해야 하며, 여기에는 추가 권한이 필요합니다. Foundry 인스턴스에서 웹훅을 사용하는 데 관한 질문은 Palantir 담당자에게 문의하세요.

제출 조건은 평소대로 통과해야 합니다. 액션 제출 조건이 실패하면 부수 효과는 실행되지 않습니다.

수신자는 알림에 포함된 모든 객체 데이터에 접근할 수 있어야 합니다.

* 사용자가 알림 내용에 포함된 데이터 전부에 접근할 수 없으면, 그 사용자에게는 알림이 전송되지 않습니다.
* 수신자가 여러 명이고 그중 일부가 알림에 포함된 데이터에 대한 적절한 권한이 없으면, 충분한 권한이 있는 사용자에게만 알림이 갑니다.
* 어떤 이유로든 알림 전송이 실패하더라도 편집은 성공할 수 있습니다.

액션을 실행하는 사용자는 알림을 받을 사용자 및/또는 그룹을 볼 수 있어야 합니다.

> **중간 요약**: 웹훅은 Data Connection에서 플러그인을 구성하는 추가 권한이 있어야 쓸 수 있습니다. 부수 효과는 제출 조건을 통과해야 실행되고, 알림은 내용의 데이터에 접근할 수 있는 수신자에게만 전송되며, 알림이 실패해도 편집은 성공할 수 있습니다.

## 정리

- 액션 타입의 권한은 보기, 편집하기, 특정 파라미터로 실행하기의 세 측면에서 적용됩니다.
- 액션 실행에는 편집 대상 객체 타입, 링크 타입, 데이터소스를 볼 수 있는 권한과 제출 조건 통과가 필요하며, 액션 로그 객체 타입에 대한 권한도 필요할 수 있습니다.
- 행과 열 단위 접근 제어는 읽기 시점에만 적용되므로, 하위 데이터 보호에는 마킹이나 분류 기반 접근 제어를 함께 씁니다.
- 새 객체 타입은 기본적으로 액션을 통한 편집만 허용하며, 이 설정이 라이트백 데이터셋 전체에 `Edit` 권한을 주지 않아도 되므로 권장됩니다.
- 웹훅은 추가 권한이 필요하고, 알림은 데이터 접근 권한이 있는 수신자에게만 전송됩니다.
