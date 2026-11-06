# 구성된 Object View 개요 (Configured Object View overview)

- 원문: https://www.palantir.com/docs/foundry/object-views/config-overview/
- 사이드바 위치: Applications > Object Views > Configured Object View overview

이 페이지는 Workshop 모듈로 직접 꾸미는 "구성된(configured) Object View"가 무엇인지, 기본으로 만들어지는 구성은 어떤 모습인지, 누가 편집할 수 있는지, 그리고 편집 화면에 어디서 들어가는지를 설명합니다. Object View는 객체 하나의 정보를 보여 주는 표준 화면이므로, 이를 조직에 맞게 바꾸는 방법을 아는 것이 온톨로지 기반 애플리케이션 사용성의 출발점입니다.

Configured Object View(구성된 Object View)는 객체 데이터를 사용자 정의할 수 있고 재사용할 수 있는 형태로 표현한 것입니다. [Workshop 모듈](https://www.palantir.com/docs/foundry/workshop/overview/)을 통해 하나의 객체 타입에 대해 [전체(full)](06_full-object-views/01_use-full-views-in-platform.md) Object View와 [패널(panel)](07_panel-object-views/01_use-panel-views-in-platform.md) Object View를 모두 만들 수 있으며, 이로써 플랫폼 곳곳에서 객체를 표현하는 방식을 유연하게 정할 수 있습니다.

Foundry는 모든 객체 타입에 대해 기본적으로 [표준 Object View(standard Object View)](02_standard-object-views.md)를 만듭니다. 구성된 Object View를 만들면 그것이 사용자에게 기본 뷰가 되지만, 사용자는 Object View에 함께 제공되는 토글 버튼으로 표준 Object View로 다시 전환할 수 있습니다. 또한 Gaia나 Vertex처럼 자체 사용자 정의 헤더를 쓰는 Palantir 애플리케이션 안에서 렌더링된 Object View의 경우, 줄임표(ellipsis) 서랍 아이콘 위에 마우스를 올려 표준 뷰와 구성된 뷰 사이를 전환할 수 있습니다.

![애플리케이션에 표시된 표준 Object View와 구성된 Object View 전환 토글.](https://www.palantir.com/docs/resources/foundry/object-views/toggle-core-custom-view-in-selection.png)

표준 Object View와 구성된 Object View를 전환하는 기능은 아직 Workshop에서는 사용할 수 없습니다.

**설명**: Object View는 객체 하나(예: 특정 환자, 특정 항공편)를 선택했을 때 그 객체의 속성(property)과 링크된 객체를 보여 주는 상세 화면입니다. 데이터베이스로 말하면 테이블의 행 하나를 골라 그 행의 열 값과 외래 키로 연결된 다른 테이블의 행들을 한 화면에 모아 보여 주는 상세 페이지입니다. 표준 뷰는 Foundry가 자동으로 만들어 주는 화면이고, 구성된 뷰는 Workshop(Foundry의 화면 구성 도구)으로 레이아웃과 위젯을 직접 배치한 화면입니다.

> **중간 요약**: 구성된 Object View는 Workshop 모듈로 만든 사용자 정의 객체 화면으로, 전체 형태와 패널 형태가 있습니다. 만들면 기본 뷰가 되지만 사용자는 토글로 표준 Object View로 돌아갈 수 있습니다(Workshop에서는 아직 불가).

<a id="default-configurations"></a>
## 기본 구성 (Default configurations)

기본 구성된 Object View는 각 객체 타입마다 자동으로 만들어집니다. 기본 전체 Object View에는 주요 속성(prominent properties) 목록이 들어가고, 주요 속성이 하나도 없으면 숨겨지지 않은 모든 속성의 목록이 들어갑니다. 그리고 객체의 링크 목록도 포함됩니다. 기본 패널에는 같은 속성 목록이 들어갑니다. 기본 뷰는 새 속성 추가나 속성 이름 변경처럼 객체 타입에 생긴 변경 사항을 동적으로 반영해 갱신됩니다. 하지만 Object View를 한 번이라도 편집하면 그 뷰는 사용자가 관리하는(user-managed) 상태가 되며, 이후의 모든 갱신은 수동으로 해야 합니다.

**설명**: 예를 들어 Employee 객체 타입에 `hire_date` 속성을 새로 추가했다고 합시다. 아직 아무도 편집하지 않은 기본 Object View라면 `hire_date`가 자동으로 화면에 나타납니다. 그러나 누군가 Object View를 한 번 편집해 저장했다면, 그 뒤로는 Foundry가 화면을 자동으로 고치지 않으므로 편집자가 직접 `hire_date`를 화면에 추가해야 합니다.

<a id="permissions"></a>
### 권한 (Permissions)

객체 타입의 Object View를 편집하는 데 필요한 권한은 그 객체 타입의 권한 모델에 따라 다릅니다.

* 객체 타입이 레거시 데이터소스 파생 권한(legacy datasource-derived permissions)을 사용한다면, 사용자는 [Control Panel](https://www.palantir.com/docs/foundry/administration/enrollments-and-organizations-permissions/)에서 `Object View Admin` 애플리케이션 권한을 가져야 하고, 동시에 객체 타입의 입력 데이터소스 중 하나 이상에 대해 `Editor` 역할을 가져야 합니다.
* 객체 타입이 [Ontology roles(온톨로지 역할)](../04_ontology-manager/05_ontology-roles-migration.md)을 사용한다면, 사용자는 객체 타입에 대한 `Ontology Editor` 역할만 있으면 됩니다.
* 객체 타입이 [프로젝트 기반 권한(project-based permissions)](../../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)을 사용한다면, 사용자는 객체 타입이 들어 있는 Compass 프로젝트에 대한 `Editor` 역할만 있으면 됩니다.

레거시 구성 옵션을 통해 Object View 탭의 Workshop 모듈을 독립형(standalone) 모듈로 직접 전환하지 않는 한, 그 Workshop 모듈의 권한은 객체 타입이 관리합니다. 이렇게 하면 모듈과 객체 타입 사이의 권한이 일치하게 유지되므로, 객체 타입을 편집하거나 볼 권한이 있는 사용자는 Object View 안의 모든 모듈도 편집하거나 볼 수 있습니다.

**설명**: 세 가지 권한 모델은 "누가 이 객체 타입을 고칠 수 있는가"를 판단하는 기준이 서로 다릅니다. 데이터소스 파생 방식은 원본 데이터셋에 대한 권한을 기준으로 삼고, 온톨로지 역할 방식은 객체 타입 자체에 부여된 역할을, 프로젝트 기반 방식은 객체 타입이 속한 프로젝트(Compass는 Foundry의 파일, 프로젝트 관리 체계)의 역할을 기준으로 삼습니다. Object View 탭 안의 Workshop 모듈은 따로 권한을 설정하지 않고 객체 타입의 권한을 그대로 따릅니다.

<a id="edit-configured-object-views"></a>
### 구성된 Object View 편집하기 (Edit configured Object Views)

구성된 Object View 구성 화면에 들어가는 방법은 여러 가지입니다.

한 객체 타입의 Object View는 Ontology Manager의 **Object views** 탭에서 미리 볼 수 있습니다. 헤더에서 미리 보기에 쓸 기본 표시 객체를 선택하고 고정(pin)할 수 있습니다. 또한 전체 형태와 패널 형태를 미리 보고, Object View가 라이트 모드와 다크 모드에서 어떻게 보이는지 시험할 수 있습니다. 구성된 Object View 편집은 헤더 오른쪽의 **Edit** 옵션으로 들어갈 수 있습니다.

![Ontology Manager에서 Object View 편집하기.](https://www.palantir.com/docs/resources/foundry/object-views/ontology-manager-object-view-edit.png)

Object Explorer에서는 객체를 보는 중에 **More > Advanced > Edit object view**를 선택해 그 객체 타입의 구성된 Object View에 접근할 수 있습니다.

![Object Explorer에서 Object View 편집하기.](https://www.palantir.com/docs/resources/foundry/object-views/object-explorer-object-view-edit.png)

애플리케이션 안에서 패널 Object View를 볼 때는 드롭다운 줄임표 위에 마우스를 올리고 **Edit**를 선택하면 구성 화면에 들어갈 수 있습니다. 이 드롭다운은 Object View를 편집할 권한이 있는 사용자에게만 나타납니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-views/panel-object-view-edit.gif" alt="패널 Object View 편집하기." width="300">

이 진입점들은 모두 구성된 Object View 편집기로 이어집니다. 편집기에서는 Object View 탭을 관리할 수 있고, Workshop 모듈의 모든 표준 기능으로 내용을 편집할 수 있습니다. 게시하면 편집 내용이 그 객체 타입의 모든 객체에 적용됩니다. 편집에 대한 자세한 내용은 [전체 Object View 구성](06_full-object-views/02_config-object-views.md)과 [패널 Object View 구성](07_panel-object-views/02_config-panel-views.md)을 참고하세요.

**설명**: "모든 객체에 적용된다"는 점이 핵심입니다. Object View는 객체 하나마다 따로 만드는 화면이 아니라 객체 타입 단위의 템플릿입니다. 클래스에 정의한 메서드가 모든 인스턴스에 공통으로 적용되듯이, Employee 객체 타입의 Object View를 한 번 바꾸면 직원 1명이든 1만 명이든 모두 같은 레이아웃으로 표시되고, 각 화면에는 해당 객체의 값만 채워집니다.

> **중간 요약**: 기본 구성된 Object View는 객체 타입 변경을 자동 반영하지만, 한 번 편집하면 이후로는 수동 관리입니다. 편집 권한은 객체 타입의 권한 모델에 따라 달라지며, Ontology Manager, Object Explorer, 패널의 줄임표 메뉴에서 편집기로 들어갈 수 있습니다.

## 정리

- 구성된 Object View는 Workshop 모듈로 만든 객체 타입 단위의 사용자 정의 화면이며, 전체 형태와 패널 형태가 있습니다.
- 구성된 뷰가 기본이 되지만 사용자는 토글로 표준 Object View로 돌아갈 수 있습니다(Workshop에서는 아직 불가).
- 자동 생성된 기본 뷰는 객체 타입 변경을 따라 갱신되지만, 편집한 뒤에는 수동으로 관리해야 합니다.
- 편집 권한은 데이터소스 파생 권한, 온톨로지 역할, 프로젝트 기반 권한 중 어느 모델을 쓰는지에 따라 달라집니다.
- Ontology Manager의 **Object views** 탭, Object Explorer의 **More > Advanced > Edit object view**, 패널의 **Edit** 메뉴로 편집기에 들어갑니다.
