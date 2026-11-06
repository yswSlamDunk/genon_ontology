# 객체 드롭다운 보안 고려 사항 (Object dropdown security considerations)

- 원문: https://www.palantir.com/docs/foundry/action-types/dropdown-security/
- 사이드바 위치: Define Ontologies > Action types > Parameters > Object dropdown security considerations

이 페이지는 객체 드롭다운 필터에 정적 값을 넣었을 때 생길 수 있는 정보 노출 문제를 설명합니다. 사용자가 객체 자체를 볼 권한이 없어도 필터 조건에 적힌 값은 알게 될 수 있으므로, 민감한 값이 필터에 들어가는 경우 어떻게 설계해야 하는지 알아 두어야 합니다.

객체 드롭다운 검증에 쓰인 정적 값 필터는 액션 타입을 볼 수 있는 모든 사용자에게 노출됩니다. 이런 필터를 쓰면, 필터링된 객체를 볼 권한이 없는 사용자에게 속성 값 조합이 노출될 위험이 있습니다. 객체 집합을 필터링할 때 객체 속성이나 파라미터에 의존하면 이 위험을 줄일 수 있습니다. 그 경우 값이 인터페이스에 직접 보이지 않습니다.

<a id="example-data-privacy-issue"></a>
## 예시: 데이터 프라이버시 문제 (Example: Data privacy issue)

예를 들어 `Investigation Name` 속성을 가진 `Document` 객체가 있다고 합시다. 액션 타입에서 객체 참조 파라미터에 필터를 추가해, **Investigation Name**이 `Area 51 Investigation`인 **Documents**만 보이게 합니다.

![객체 드롭다운 보안 우려](https://www.palantir.com/docs/resources/foundry/action-types/objectDropdownSecurityFilter.png)

이 경우 해당 문서들을 볼 수 없는 사용자에게, 어떤 `Document` 객체들이 `Area 51 Investigation`이라는 속성 값을 가지고 있다는 사실을 드러낼 수 있습니다.

이는 **정적 값 필터에만** 해당합니다. `Investigation Name` 속성을 파라미터나 다른 객체의 속성으로 필터링할 때는 `Area 51 Investigation`에 대한 참조가 없습니다. 그 이유는 다음과 같습니다.

* `Investigation Name` 파라미터는 사용자가 제공하는 값입니다. 액션 타입을 보는 사람에게 기반 데이터에 대한 정보가 노출되지 않습니다.
* `Investigation Object` 파라미터는 이 사용자에 대한 기존 객체 가시성 제한을 따릅니다.

따라서 이 두 검색 쿼리는 어느 쪽도 데이터 프라이버시 우려가 되지 않습니다.

![객체 드롭다운 속성 필터](https://www.palantir.com/docs/resources/foundry/action-types/objectDropdownSecurityProperty.png)

**설명**: 정적 값 필터는 `Investigation Name = "Area 51 Investigation"`처럼 비교 대상 문자열이 설정 안에 그대로 저장됩니다. 반면 파라미터 필터는 `Investigation Name = {사용자가 입력한 값}`, 객체 속성 필터는 `Investigation Name = {선택한 Investigation 객체의 name}`처럼 설정에는 변수 자리만 있고 실제 값은 실행할 때 채워집니다. 설정 안에 민감한 문자열이 없으니 설정을 본다고 해서 알 수 있는 것도 없습니다.

> **중간 요약**: 정적 값 필터는 필터 값 자체가 액션 타입 설정에 들어 있어 권한 없는 사용자에게 노출될 수 있습니다. 파라미터나 객체 속성으로 필터링하면 이 문제가 없습니다.

<a id="technical-details"></a>
## 기술적 세부 사항 (Technical details)

대부분의 경우 액션 백엔드는 민감한 속성 값이 노출되지 않도록 액션 타입 정의 안의 민감한 정보를 가립니다(redact). 예를 들어 액션의 제출 조건(submission criteria)은 액션 타입을 편집할 수 없는 사용자에게 숨겨집니다. 마찬가지로 사용자는 인터페이스에서든 백엔드 응답을 살펴보든 액션 타입 정의 안의 새 객체 드롭다운 필터를 볼 수 없습니다.

그러나 액션 폼을 볼 때는 객체 드롭다운 검증이 객체 집합으로 변환됩니다. 이는 사용자가 이 객체 집합을 담은 네트워크 요청을 살펴볼 수 있다는 뜻입니다. 위 예시에서 사용자는 `Investigation Name = 'Area 51 Investigation'` 필터를 담은 객체 집합 RID를 받게 되며, 그 값에 해당하는 객체를 하나도 볼 수 없더라도 그런 속성 값이 존재한다는 사실이 드러납니다.

즉 이 값들은 어떤 사용자에게도 **인터페이스에는 보이지 않습니다**. 보안보다 화면 노출(가시성)이 더 큰 관심사라면 이 경고는 무시해도 됩니다.

**설명**: RID(Resource Identifier)는 Foundry가 리소스마다 붙이는 고유 식별자입니다. 브라우저 개발자 도구의 네트워크 탭에서는 화면에 표시되지 않는 HTTP 요청과 응답 본문도 볼 수 있으므로, 폼을 열 때 오가는 객체 집합 정의에서 필터 문자열을 읽을 수 있다는 것이 이 절의 요지입니다. 따라서 "화면에 안 보이면 충분한" 경우에는 문제가 없지만, 값의 존재 자체가 기밀이라면 정적 값 필터를 쓰지 말아야 합니다.

> **중간 요약**: 백엔드는 액션 타입 정의의 민감 정보를 가리지만, 폼을 열 때 드롭다운 검증이 객체 집합으로 변환되어 네트워크 요청에 필터 값이 실립니다. 화면에는 보이지 않으므로 가시성만 문제라면 괜찮지만, 보안이 중요하면 정적 값 필터를 피해야 합니다.

## 정리

- 객체 드롭다운의 정적 값 필터는 액션 타입을 볼 수 있는 사용자에게 필터 값을 노출할 위험이 있습니다.
- 파라미터나 다른 객체의 속성으로 필터링하면 설정에 민감한 값이 남지 않아 이 위험이 없습니다.
- 백엔드는 정의를 가리지만, 폼을 열 때 생성되는 객체 집합이 네트워크 요청에 담겨 값이 드러날 수 있습니다.
- 값이 인터페이스에 표시되지는 않으므로, 보안이 아닌 화면 노출만 신경 쓴다면 경고를 무시해도 됩니다.
