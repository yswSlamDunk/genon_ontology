# 함수 권한 (Permissions)

- 원문: https://www.palantir.com/docs/foundry/functions/permissions/
- 사이드바 위치: Define Ontologies > Functions > Function management > Permissions

이 페이지는 함수(function)를 작성할 때와 게시된 함수를 실행할 때 적용되는 여러 종류의 권한 검사를 설명합니다. 저장소(repository) 자체가 가져야 하는 권한, 함수를 실행하는 사용자가 가져야 하는 권한, 객체를 불러올 때 적용되는 권한, 그리고 관리자가 허용 목록으로 통제하는 확장 실행 기능을 차례로 다룹니다. 함수 개발 중 "권한 거부" 오류를 만났을 때 원인을 찾는 기준이 되는 페이지입니다.

플랫폼에서 함수를 작성하고 실행하는 일은 여러 종류의 권한 검사를 받습니다. 이 섹션은 알아 두어야 할 권한의 종류와 흔히 겪는 문제를 설명합니다.

<a id="function-authoring"></a>
## 함수 작성 (Function authoring)

함수 저장소에는 다음을 위한 적절한 권한이 부여되어야 합니다.

1. 올바른 코드 바인딩(code binding)을 생성할 수 있도록 온톨로지에 접근합니다.
2. 함수 실행의 라이브 미리 보기(live preview)를 돌리기 위해 객체를 불러옵니다.

저장소 권한은 명시적으로 부여해야 하며, 여러분의 사용자 계정에 부여된 권한과 같지 않습니다. 그래서 객체 타입, 링크 타입, 백킹 데이터소스(backing datasource)를 저장소가 들어 있는 프로젝트(Project)로 가져오는(import) 특정 절차를 밟아야 합니다.

이 절차에 대한 튜토리얼은 [이 섹션](../13_functions-on-objects/05_ontology-imports.md)을 참고하세요. 아래에서는 어떤 리소스를 가져오는지, 그 리소스에 어떤 권한이 부여되는지 설명합니다.

**설명**: 코드 바인딩은 온톨로지의 객체 타입과 링크 타입을 코드에서 타입 검사가 되는 클래스와 메서드로 쓸 수 있도록 자동 생성한 코드입니다. 예를 들어 `Flight` 객체 타입을 가져오면 코드에서 `Flight` 타입과 그 속성(`flight.origin` 등)을 바로 쓸 수 있게 됩니다. 핵심은 "내가 볼 수 있다"와 "저장소가 볼 수 있다"가 다르다는 점입니다. 사용자는 어떤 객체 타입을 볼 권한이 있어도, 그 타입을 저장소가 속한 프로젝트로 가져오지 않으면 저장소 안의 코드는 그 타입을 모릅니다. 프로젝트 단위로 사용할 리소스를 명시적으로 선언하게 해서, 저장소가 어떤 데이터에 의존하는지 추적할 수 있게 하는 구조입니다.

<a id="ontology-entity-permissions"></a>
### 온톨로지 엔터티 권한 (Ontology entity permissions)

저장소에서 검사(checks)가 실행되거나 Code Assist가 시작될 때마다, 함수 플러그인은 저장소의 권한을 바탕으로 최신 온톨로지를 불러오고, 불러온 모든 객체 타입과 링크 타입에 대한 코드 바인딩을 생성합니다. 불러오는 객체 타입과 링크 타입의 집합은 다음 리소스 유형을 무엇을 가져왔는지에 따라 정해집니다.

* 온톨로지(Ontologies)
* 온톨로지 브랜치(Ontology branches)
* [객체 타입](../../02_object-and-link-types/02_object-types/01_object-types-overview.md)
* [링크 타입](../../02_object-and-link-types/06_link-types/01_link-types-overview.md)

함수 저장소에서는 **Settings** > **Ontology**로 이동해 필요한 온톨로지 리소스를 가져올 수 있습니다. 이 화면에서 프로젝트로 가져올 객체 타입과 링크 타입을 선택합니다.

![온톨로지 설정](https://www.palantir.com/docs/resources/foundry/functions/ontology-settings-flights.png)

사용자 계정이 여러 온톨로지에 접근할 수 있다면 사용할 온톨로지를 선택할 수도 있습니다. 현재 한 프로젝트에 여러 온톨로지를 가져오는 것은 지원되지 않습니다.

![온톨로지 선택기](https://www.palantir.com/docs/resources/foundry/functions/ontology-picker.png)

**주의**: 온톨로지 가져오기는 저장소 하나가 아니라 프로젝트 전체에 적용됩니다(Ontology imports apply to the whole Project, not one repository). 위 화면은 함수 저장소 안에 나타나지만, 가져온 온톨로지, 객체 타입, 링크 타입은 **프로젝트(Project)** 수준에 추가됩니다. 즉, 한 저장소에서 가져오기를 바꾸면 같은 프로젝트의 다른 저장소에 영향을 줄 수 있습니다. 서로 다른 온톨로지 엔터티에 의존하는 저장소 두 개가 필요하다면 서로 다른 프로젝트로 분리해야 합니다.

<a id="object-loading-permissions"></a>
### 객체 로딩 권한 (Object loading permissions)

저장소의 **functions helper**(함수 도우미)는 두 가지 방법으로 함수를 실행하게 해 줍니다. 게시된 함수를 실행하는 방법과, 라이브 미리 보기로 코드를 실행하는 방법입니다. 라이브 미리 보기로 실행하면 함수 코드는 Code Assist에서 컴파일되고 실행됩니다. Code Assist는 코드 작성자가 빠르게 반복 작업을 할 수 있도록 설계된 인프라입니다.

Code Assist는 저장소에 묶여 있으므로, 위에서 설명한 코드 생성과 같은 권한 요구 사항을 따릅니다. 즉, 라이브 미리 보기로 함수를 실행할 때 사용하려는 각 객체 타입의 바탕이 되는 백킹 데이터소스를 프로젝트로 가져와야 합니다.

functions helper에서, 프로젝트에 객체 타입은 가져왔지만 그에 대응하는 데이터소스를 가져오지 않았다면, 라이브 미리 보기에 가져오기를 갱신하라는 경고가 표시됩니다.

![미리 보기의 백킹 데이터소스 경고](https://www.palantir.com/docs/resources/foundry/functions/preview-backing-datasources.png)

대부분의 객체 타입에서는 **Import backing datasources**(백킹 데이터소스 가져오기) 대화 상자가 Foundry 데이터셋을 가져오라고 안내합니다. [행 수준 보안(row-level security)](../../../06_ontology-architecture/02_object-permissioning/05_configuring-rv-access-controls.md)이 켜진 객체 타입은 [Restricted View](https://www.palantir.com/docs/foundry/security/restricted-views/)를 가져오라고 안내합니다.

**설명**: 객체 타입의 정의(스키마)를 가져오는 것만으로는 코드가 컴파일될 뿐이고, 실제 객체 데이터를 읽으려면 그 데이터가 들어 있는 데이터셋도 저장소에서 접근 가능해야 합니다. 예를 들어 `Flight` 객체 타입만 가져오고 `flights` 데이터셋을 가져오지 않으면, 코드는 빌드되지만 미리 보기에서 Flight 객체를 불러오지 못합니다. Restricted View는 행마다 누가 볼 수 있는지 규칙을 붙인 데이터셋 뷰로, 행 수준 보안 객체 타입은 일반 데이터셋 대신 이것을 백킹 데이터소스로 씁니다.

> **중간 요약**: 함수를 작성하려면 사용자 권한과 별개로 저장소가 속한 프로젝트에 객체 타입, 링크 타입(코드 바인딩용)과 백킹 데이터소스(라이브 미리 보기용)를 가져와야 합니다. 가져오기는 프로젝트 전체에 적용되므로 같은 프로젝트의 다른 저장소에도 영향을 줍니다.

<a id="published-function-execution"></a>
## 게시된 함수 실행 (Published function execution)

함수가 게시되면 더 넓은 범위의 사용자가 쓸 수 있게 되고, [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)과 [액션](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md) 같은 애플리케이션에서 실행되도록 설정할 수 있습니다. 게시된 함수를 실행하는 권한에도 여전히 고려할 점이 있습니다.

<a id="function-permissions"></a>
### 함수 권한 (Function permissions)

함수를 실행하려면 사용자가 그 함수가 게시된 저장소에 대해 **Viewer** 역할을 가지고 있어야 합니다. 일반적으로 함수 저장소는, 그 저장소의 함수에 의존하는 최종 사용자 애플리케이션과 같은 프로젝트에 두는 것이 가장 좋습니다. 그 애플리케이션이 Workshop, Slate, 또는 다른 도구 무엇으로 만들어졌든 마찬가지입니다. 사용자가 함수를 읽을 권한이 없다는 오류(ReadFunctionsPermissionDenied)를 만나면, 그 사용자가 저장소에 읽기 권한이 있는지 확인하세요. [리소스를 이동하고 공유하는 방법을 더 알아보세요.](https://www.palantir.com/docs/foundry/compass/move-and-share-resources/)

반면 코드가 `FunctionRegistry:ReadOntologyFunctionPermissionDenied`인 `PERMISSION_DENIED` 오류는, 폴더 수준의 권한 문제라기보다 함수가 [Developer Console](https://www.palantir.com/docs/foundry/developer-console/overview/)에 등록되어 있지 않거나 사용 가능하지 않다는 뜻인 경우가 많습니다. 폴더와 저장소 권한만으로는 함수가 실행 가능해지지 않으므로, Developer Console에서 함수를 추가하고 등록하세요.

접근 권한을 더 넓게 검토하려면 사이드바의 **Check access**(접근 확인) 패널을 사용해, 어떤 사람이 Workshop이나 Slate 애플리케이션에 접근할 수 있는지(의존하는 함수에 대한 접근 포함) 확인합니다. 자세한 내용은 [권한 확인하기](https://www.palantir.com/docs/foundry/security/checking-permissions/)를 참고하세요.

[함수 기반 액션(Function-backed Actions)](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)은 특별한 경우로, 최종 사용자가 함수를 사용하는 액션을 적용할 때 반드시 그 함수에 대한 읽기 권한이 필요하지는 않습니다. 액션이 함수를 쓰도록 설정하는 관리 사용자는 그 함수에 대한 읽기 권한이 있어야 합니다. 그 이후에는 사용자가 함수에 대한 접근 권한과 관계없이 [액션 수준 권한](../../03_action-types/19_permissions.md)에 따라 액션을 적용할 수 있습니다.

**설명**: 오류 코드별로 정리하면 다음과 같습니다. `ReadFunctionsPermissionDenied`는 사용자에게 함수 저장소의 Viewer 권한이 없을 때 나므로 저장소 공유 설정을 봅니다. `FunctionRegistry:ReadOntologyFunctionPermissionDenied`는 권한보다는 함수 등록 문제인 경우가 많으므로 Developer Console 등록 여부를 봅니다. 함수 기반 액션은 예외로, 액션을 설정하는 관리자만 함수를 읽을 수 있으면 되고 일반 사용자는 액션 권한만 있으면 됩니다.

<a id="object-loading-permissions"></a>
### 객체 로딩 권한 (Object loading permissions)

함수가 파라미터로든 [객체 검색(object search)](../13_functions-on-objects/01_functions-on-objects.md)으로든 객체 데이터를 불러올 때, 어떤 객체가 불러와지는지는 함수를 실행하는 최종 사용자의 권한이 결정합니다. 행 수준 권한으로 보호되는 객체 타입이라면, 같은 함수를 실행하는 서로 다른 사용자가 서로 다른 결과를 받을 수 있다는 뜻입니다. 이는 의도된 동작입니다. 사용자는 자신이 접근할 수 있는 객체만 봐야 하며, 이 동작 덕분에 개별 객체에 대한 접근 권한이 서로 다른 사용자들에게 함수 하나로 대응할 수 있습니다.

**주의**: 읽기 시점에만 적용됨(Read-time enforcement only). 행과 열 접근 제어([Restricted View](https://www.palantir.com/docs/foundry/security/restricted-views/), [객체 보안 정책(object security policy)](../../../06_ontology-architecture/02_object-permissioning/07_object-security-policies.md), [속성 보안 정책(property security policy)](https://www.palantir.com/docs/foundry/security/property-security-markings/) 포함)는 함수가 실행될 때 사용자가 읽을 수 있는 것을 걸러 냅니다. 이 제어는 함수의 출력에는 이어지지 않습니다. 데이터가 하류(downstream)로 흘러가는 동안에도 보호되게 하려면, 이 제어를 [마킹(marking)](https://www.palantir.com/docs/foundry/security/markings/)이나 [분류 기반 접근 제어(Classification-based Access Control)](https://www.palantir.com/docs/foundry/security/classification-based-access-controls/)와 함께 사용하세요. 전체 모델은 [접근 제어 전파(Access control propagation)](https://www.palantir.com/docs/foundry/security/access-control-propagation/)를 참고하세요.

**설명**: 예를 들어 `Employee` 객체 타입에 "자기 부서 직원만 볼 수 있다"는 행 수준 규칙이 있고, 함수 `countEmployees`가 모든 Employee를 세어 숫자를 돌려준다고 합시다. 영업부 사용자가 실행하면 영업부 직원 수만, 인사부 사용자가 실행하면 인사부 직원 수만 나옵니다. 이것이 "실행하는 사용자 권한으로 불러온다"는 뜻입니다. 그런데 영업부 사용자가 이 함수 결과(예: 영업부 직원 이름 목록)를 다른 데이터셋에 기록하면, 그 데이터셋에는 행 수준 규칙이 따라가지 않습니다. 그래서 출력까지 보호하려면 마킹 같은 별도 장치가 필요하다는 것이 주의 문단의 요지입니다.

> **중간 요약**: 게시된 함수를 실행하려면 저장소의 Viewer 권한이 필요하며, 함수 기반 액션은 액션 권한만으로 충분합니다. 함수가 불러오는 객체는 실행하는 사용자의 권한으로 걸러지지만, 이 필터는 출력에 따라가지 않으므로 하류 보호에는 마킹 등을 함께 써야 합니다.

<a id="extended-function-execution"></a>
## 확장 함수 실행 (Extended function execution)

관리자는 [Control Panel](https://www.palantir.com/docs/foundry/administration/control-panel/)의 **Functions settings**에서 확장 실행 기능을 통제합니다. 이 기능은 함수 안에서 [액션](../../03_action-types/11_function-backed-actions/01_function-actions-overview.md)을 호출하거나 유효 기간(TTL)이 최대 4시간인 인증 토큰을 얻는 것처럼 높은 수준의 접근을 부여합니다.

확장 기능이 있는 함수를 게시, 실행, 설치하려면 관리자가 해당 허용 목록(allowlist)을 설정해야 합니다.

* **Repositories allowed to publish extended functions**(확장 함수를 게시할 수 있는 저장소): 이 허용 목록에 있는 저장소만 확장 기능이 있는 함수를 게시할 수 있습니다.
* **Functions allowed to execute with extended capabilities**(확장 기능으로 실행할 수 있는 함수): 이 허용 목록에 있는 함수만 확장 기능으로 실행할 수 있습니다. Foundry는 실행 시점에 이 허용 목록을 확인합니다.
* **Projects allowed for installing extended functions via Marketplace**(Marketplace로 확장 함수를 설치할 수 있는 프로젝트): 이 허용 목록에 있는 프로젝트만 [Marketplace](https://www.palantir.com/docs/foundry/marketplace/overview/)에서 확장 기능이 있는 함수를 설치할 수 있습니다.

확장 기능이 있는 함수의 게시, 실행, Marketplace 설치가 권한 오류를 반환하면, 관리자에게 관련 허용 목록을 확인해 달라고 요청하세요.

**설명**: 허용 목록은 "여기에 적힌 것만 허용하고 나머지는 모두 거부"하는 방식의 접근 통제입니다. 확장 기능은 게시, 실행, Marketplace 설치의 세 단계마다 별도의 허용 목록이 있으므로, 오류가 어느 단계에서 났는지 보고 해당 목록을 확인하면 됩니다.

## 정리

- 함수 작성 시에는 사용자 권한과 별개로, 저장소가 속한 프로젝트에 객체 타입, 링크 타입, 백킹 데이터소스를 가져와야 코드 바인딩 생성과 라이브 미리 보기가 동작합니다.
- 온톨로지 가져오기는 프로젝트 단위로 적용되며, 한 프로젝트에는 온톨로지를 하나만 가져올 수 있습니다.
- 게시된 함수를 실행하려면 저장소의 Viewer 역할이 필요하고, Developer Console 미등록도 권한 오류처럼 보일 수 있습니다. 함수 기반 액션은 액션 권한만으로 실행됩니다.
- 함수가 불러오는 객체는 실행 사용자의 권한으로 걸러지지만 이 보호는 출력까지 이어지지 않습니다.
- 액션 호출, 장기 토큰 같은 확장 실행 기능은 게시, 실행, 설치 단계별 허용 목록으로 관리자가 통제합니다.
