# 프로젝트 기반 권한으로 마이그레이션하기 (Migrate to project-based permissions)

- 원문: https://www.palantir.com/docs/foundry/ontology-manager/migrate-to-project-based-permissions/
- 사이드바 위치: Applications > Ontology Manager > Migrate to project-based permissions

이 페이지는 객체 타입, 액션 타입 같은 온톨로지 리소스의 권한 관리 방식을 예전 방식(온톨로지 역할, 데이터소스 기반 권한)에서 프로젝트 기반 권한으로 옮기는 방법을 설명합니다. 마이그레이션의 제약 사항, 리소스를 어느 프로젝트에 둘지에 대한 접근 방식, Marketplace 설치에 미치는 영향, 그리고 마이그레이션 도우미와 직접 마이그레이션 절차를 다룹니다.

객체 타입, 액션 타입, 링크 타입, 인터페이스, 공유 속성(shared property)을 포함한 온톨로지 리소스는 특정 프로젝트 안에 저장할 수 있으며, 그 프로젝트의 권한을 자동으로 상속받습니다. 객체 인스턴스와 링크 인스턴스의 권한은 여전히 백킹 데이터소스(backing datasource)의 위치에 따라 결정됩니다. 마이그레이션이 끝나면 온톨로지 리소스를 보고, 편집하고, 관리하는 권한은 Palantir 플랫폼의 파일 시스템인 [Compass](https://www.palantir.com/docs/foundry/compass/overview/)를 통해 관리됩니다. [프로젝트 기반 권한](../../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)은 이전의 온톨로지 역할(ontology roles) 모델과 데이터소스 기반 권한(datasource-derived permissions) 모델을 대체합니다. 이는 다른 모든 리소스 타입에 사용되는 것과 같은 권한 모델입니다.

마이그레이션 도구를 사용하면 기존 온톨로지 리소스를 [프로젝트 기반 권한](../../06_ontology-architecture/02_object-permissioning/02_ontology-permissions.md)으로 마이그레이션할 수 있습니다. 이 도구는 온톨로지 리소스가 올바른 권한을 받도록 하면서 적절한 프로젝트에 배치할 위치를 제안합니다.

**경고**: 프로젝트 기반 권한으로의 마이그레이션은 되돌릴 수 없습니다(Migrating to project-based permissions cannot be reverted). 리소스를 일단 프로젝트 기반 권한으로 마이그레이션하면, 온톨로지 역할이나 데이터소스 기반 권한으로 되돌릴 수 없습니다.

새 온톨로지 리소스에 프로젝트 권한 방식을 켜려면, 온톨로지 소유자가 Ontology Manager의 **Ontology configuration** 탭으로 이동해 **Require new ontology resources be saved in a project**(새 온톨로지 리소스는 프로젝트에 저장해야 함) 토글을 켭니다. 이 설정을 켜면 사용자가 새 온톨로지 리소스를 만들 때 저장 위치를 고르라는 안내가 나타납니다.

**설명**: 여기서 권한은 두 층으로 나뉩니다. 하나는 "Flight라는 객체 타입의 정의(어떤 속성이 있는지 등)를 누가 보고 고칠 수 있는가"이고, 다른 하나는 "F100, F101 같은 실제 Flight 객체의 데이터를 누가 볼 수 있는가"입니다. 이 마이그레이션은 앞의 것만 바꿉니다. 데이터베이스로 치면 테이블 스키마를 변경할 권한(`ALTER`)과 행을 조회할 권한(`SELECT`)이 따로 있는 것과 같은 구분입니다. 프로젝트는 Compass 파일 시스템에서 폴더에 해당하는 단위로, 프로젝트에 사용자나 그룹별 역할(Viewer, Editor 등)을 부여하면 그 안의 모든 리소스가 같은 권한을 물려받습니다.

> **중간 요약**: 프로젝트 기반 권한에서는 온톨로지 리소스를 Compass 프로젝트에 저장하고 프로젝트 권한을 상속받습니다. 객체와 링크 인스턴스 권한은 여전히 백킹 데이터소스 위치를 따르며, 마이그레이션은 되돌릴 수 없습니다.

<a id="limitations"></a>
## 제약 사항 (Limitations)

시작하기 전에 다음 제약 사항을 알아 두세요.

* 온톨로지 리소스 이름은 Compass 규칙을 따라야 합니다. 슬래시("/")는 허용되지 않으며, 중복된 이름도 허용되지 않습니다. 별칭(alias)을 통해 중복된 이름이 화면에 표시될 수는 있지만, 시스템은 고유한 경로를 보장하기 위해 "(1)"을 덧붙여 중복을 제거합니다.
  * 각 온톨로지 리소스는 고유한 이름을 가져야 합니다.
  * 예: `common/utility-room`은 슬래시 때문에 유효하지 않습니다.
* 온톨로지의 리소스는 그 온톨로지와 같은 스페이스(space) 안의 프로젝트에 저장해야 합니다.

**설명**: 리소스가 파일 시스템의 파일처럼 경로(`/스페이스/프로젝트/폴더/이름`)로 식별되기 때문에, 경로 구분자인 슬래시를 이름에 쓸 수 없고 같은 폴더 안에 같은 이름이 둘 있을 수 없습니다. 운영체제에서 한 디렉터리에 같은 이름의 파일을 두 개 만들 수 없는 것과 같은 규칙입니다.

<a id="approaches-to-migration"></a>
## 마이그레이션 접근 방식 (Approaches to migration)

마이그레이션을 시작하기 전에 온톨로지 리소스를 어떻게 구성할지 생각해 보세요.

* **온톨로지 리소스를 데이터소스와 함께 두거나 유스케이스 프로젝트에 저장하기:** 온톨로지 리소스를 대응하는 데이터소스 바로 옆에 두면 리소스와 인스턴스 사이에 권한이 일관되게 유지됩니다. 이 방식에서는 유스케이스 전체에 대한 권한을 한곳에서 부여할 수 있어, 적절한 사용자가 모든 구성 요소를 함께 보고, 편집하고, 관리할 수 있게 됩니다.

* **온톨로지 리소스를 전용 프로젝트에 저장하기:** 온톨로지 리소스만을 위한 별도 프로젝트를 하나 이상 만듭니다. 이 프로젝트들에 넓은 접근 권한을 부여해, 온톨로지 리소스가 필요한 모든 사람이 볼 수 있게 합니다.

* **혼합 방식:** 핵심 온톨로지 리소스는 모든 사람이 볼 권한을 가진 하나의 프로젝트에 저장합니다. 유스케이스에 특화된 리소스는 유스케이스별 프로젝트에 저장합니다. 이렇게 하면 온톨로지 선택기(picker)와 검색 화면이 유스케이스 전용 온톨로지 리소스로 어수선해지는 것을 막을 수 있습니다.

**참고**: 온톨로지 리소스는 객체 및 링크 인스턴스와 별개의 권한을 가집니다. 이 마이그레이션은 온톨로지 리소스 권한에만 영향을 줍니다. 객체 및 링크 인스턴스 권한은 여전히 백킹 데이터소스의 위치를 기준으로 합니다.

**설명**: 예를 들어 항공 정비 유스케이스가 있다면, 첫 번째 방식은 `Aircraft` 데이터셋과 `Aircraft` 객체 타입을 같은 "정비" 프로젝트에 둡니다. 두 번째 방식은 모든 객체 타입을 "온톨로지 공용" 프로젝트에 모읍니다. 혼합 방식은 여러 팀이 같이 쓰는 `Aircraft`, `Airport` 같은 핵심 타입은 공용 프로젝트에, 정비팀만 쓰는 `MaintenanceTicket` 같은 타입은 정비 프로젝트에 둡니다.

> **중간 요약**: 리소스 이름에는 슬래시와 중복이 허용되지 않고, 리소스는 온톨로지와 같은 스페이스의 프로젝트에 두어야 합니다. 배치 방식은 데이터소스와 함께 두기, 전용 프로젝트에 모으기, 핵심 리소스와 유스케이스 리소스를 나누는 혼합 방식 중에서 고릅니다.

<a id="how-migration-changes-marketplace-installs"></a>
### 마이그레이션이 Marketplace 설치를 바꾸는 방식 (How migration changes Marketplace installs)

프로젝트 권한 방식으로 마이그레이션하기 전에는, 온톨로지 리소스가 **Ontology service project**에 있습니다. 이 프로젝트는 레거시 권한 모델에서 한 온톨로지의 모든 온톨로지 리소스를 담는, 시스템이 관리하는 프로젝트입니다. Ontology service project에서는 모든 사용자가 온톨로지 리소스에 대해 기본 **Viewer** 권한을 가지며, 리소스에는 파일 분류(classification)가 붙지 않습니다. Marketplace 제품을 설치하면 온톨로지 리소스는 이 Ontology service project에 배치되고, 온톨로지가 아닌 파일은 설치하는 사용자가 고른 대상 프로젝트에 배치됩니다.

![Marketplace 설치 시 온톨로지 리소스는 대상 환경의 Ontology service project에, 온톨로지가 아닌 파일은 대상 프로젝트에 배치됩니다.](https://www.palantir.com/docs/resources/foundry/ontology-manager/marketplace-setup-prior-to-ontology-in-projects-migration.png)

프로젝트 권한 방식으로 마이그레이션한 뒤에는, 같은 제품이 온톨로지 리소스를 나머지 파일과 함께 선택한 대상 프로젝트에 바로 설치하며, 그 프로젝트의 역할 부여와 분류가 온톨로지 리소스에도 적용됩니다.

![마이그레이션 후 Marketplace 설치 시 온톨로지 리소스가 선택한 대상 프로젝트에 배치됩니다.](https://www.palantir.com/docs/resources/foundry/ontology-manager/marketplace-setup-after-migration-to-ontology-in-projects.png)

Ontology service project는 모든 사용자에게 기본 Viewer 권한을 주고 분류도 없으므로, 대상 프로젝트의 더 엄격한 역할 부여(그리고 그 프로젝트가 강제하는 필수 마킹(mandatory marking)이나 최대 분류 수준)는 마이그레이션 전과 비교해 설치된 온톨로지 리소스의 가시성을 좁힐 수 있습니다. 온톨로지 리소스를 제품의 다른 파일과 다른 가시성으로 유지하려면, 제품을 서로 연결된 두 개의 Marketplace 제품으로 나누세요. 하나는 온톨로지 리소스를 담아 더 허용적인 프로젝트에 설치하고, 다른 하나는 나머지 파일을 담아 더 제한된 프로젝트에 설치합니다.

![온톨로지 리소스와 온톨로지가 아닌 파일을 서로 다른 가시성의 프로젝트에 설치할 수 있도록 두 개의 연결된 제품으로 나눈 Marketplace 제품.](https://www.palantir.com/docs/resources/foundry/ontology-manager/splitting-marketplace-product-into-two-products.png)

**설명**: 마킹(marking)과 분류(classification)는 역할 기반 권한 위에 추가로 걸리는 접근 제한입니다. 예를 들어 프로젝트에 "개인정보" 마킹이 강제되어 있으면 그 안의 리소스는 해당 마킹 접근 자격이 있는 사용자만 볼 수 있습니다. 마이그레이션 전에는 누구나 볼 수 있던 객체 타입 정의가, 마이그레이션 후 엄격한 프로젝트에 설치되면 일부 사용자에게 보이지 않게 될 수 있다는 것이 이 절의 핵심입니다.

> **중간 요약**: 마이그레이션 전에는 Marketplace가 온톨로지 리소스를 누구나 볼 수 있는 Ontology service project에 설치했지만, 마이그레이션 후에는 대상 프로젝트에 설치되어 그 프로젝트의 권한과 분류를 따릅니다. 가시성을 다르게 유지하려면 제품을 두 개로 나눕니다.

<a id="use-the-migration-assistant-recommended"></a>
## 마이그레이션 도우미 사용하기(권장) (Use the migration assistant (recommended))

마이그레이션 도우미는 온톨로지 리소스에 알맞은 프로젝트와 위치를 빠르게 찾도록 돕습니다.

**마이그레이션 도우미에 접근하려면:** 온톨로지를 선택하고 **Ontology configuration** 페이지로 이동한 뒤, **Migrations** 섹션에서 **Proceed to migration**을 선택하세요.

![Ontology configuration 페이지로 이동한 뒤 "Proceed to migration" 옵션을 사용합니다.](https://www.palantir.com/docs/resources/foundry/ontology-manager/proceed-to-migration.png)

작업 속도를 높이기 위해 리소스를 옮길 위치에 대한 강한 추천은 미리 선택되어 있고, 약한 제안은 검토할 수 있도록 선택되지 않은 상태로 남아 있습니다. 선택을 확인한 뒤 마이그레이션을 진행하세요. 최종 확정 전에 필요한 가져오기(import)를 만들거나 작업을 취소할 수 있습니다.

![마이그레이션 도우미는 검토할 수 있도록 강한 추천을 미리 선택해 둡니다.](https://www.palantir.com/docs/resources/foundry/ontology-manager/migration-assistant-recommendations.png)

이 추천은 리소스 배치에 대해 더 빠르고 근거 있는 결정을 내리도록 돕습니다. 추천이 없는 경우에는 마이그레이션 도우미의 **Individual resources** 탭에서 위치를 직접 선택할 수 있습니다.

![개별 리소스를 마이그레이션할 위치를 직접 선택합니다.](https://www.palantir.com/docs/resources/foundry/ontology-manager/migration-assistant-individual-resources.png)

**설명**: 가져오기(import)는 한 프로젝트의 리소스가 다른 프로젝트의 리소스를 참조할 수 있도록 명시적으로 연결해 두는 Foundry 프로젝트 기능입니다. 예를 들어 객체 타입을 A 프로젝트로 옮겼는데 백킹 데이터셋이 B 프로젝트에 있다면, A 프로젝트에 B의 데이터셋을 가져오는 설정이 필요할 수 있습니다.

<a id="migrate-resources-directly"></a>
## 리소스 직접 마이그레이션하기 (Migrate resources directly)

도우미를 사용하지 않고도 리소스를 마이그레이션할 수 있습니다. 리소스를 어디에 둘지 정확히 알고 있거나 특정 리소스를 빠르게 마이그레이션하고 싶을 때 유용합니다.

* **여러 리소스를 일괄 마이그레이션하기:** 온톨로지를 선택한 다음 왼쪽 사이드바의 **Resources** 섹션에서 리소스 타입을 고릅니다. 마이그레이션할 항목을 선택한 다음 드롭다운 메뉴에서 **Project permission migration**을 선택합니다. <br><br>
  ![리소스를 선택한 뒤 드롭다운 메뉴의 옵션을 사용해 일괄 마이그레이션합니다.](https://www.palantir.com/docs/resources/foundry/ontology-manager/project-based-perm-bulk-res-migration.png) <br><br>

* **개별 리소스 마이그레이션하기:** 온톨로지 리소스를 열고 **Overview** 페이지의 **Actions** 드롭다운 메뉴에서 **Project permission migration**을 선택합니다. <br><br>
  ![드롭다운 메뉴를 사용해 개별 리소스를 마이그레이션합니다.](https://www.palantir.com/docs/resources/foundry/ontology-manager/project-based-perm-individual-res-migration.png)

> **중간 요약**: 권장 방법은 **Ontology configuration** 페이지의 **Proceed to migration**으로 여는 마이그레이션 도우미이며, 강한 추천이 미리 선택되어 있습니다. 위치를 이미 알면 리소스 목록에서 일괄로, 또는 리소스의 **Actions** 메뉴에서 개별로 **Project permission migration**을 실행합니다.

## 정리

- 프로젝트 기반 권한에서는 온톨로지 리소스(객체 타입, 액션 타입, 링크 타입, 인터페이스, 공유 속성)가 Compass 프로젝트에 저장되어 프로젝트 권한을 상속받습니다. 객체와 링크 인스턴스 권한은 여전히 백킹 데이터소스를 따릅니다.
- 마이그레이션은 되돌릴 수 없고, 리소스 이름에 슬래시나 중복이 없어야 하며, 온톨로지와 같은 스페이스의 프로젝트에 두어야 합니다.
- 배치 방식으로 데이터소스와 함께 두기, 전용 프로젝트, 혼합 방식이 있습니다.
- 마이그레이션 후 Marketplace 설치는 온톨로지 리소스를 대상 프로젝트에 넣으므로 가시성이 좁아질 수 있으며, 필요하면 제품을 둘로 나눕니다.
- 마이그레이션 도우미(권장)나 일괄, 개별 직접 마이그레이션으로 진행합니다.
