# 워크플로 배포 (Deploy workflow)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/deploy-workflow/
- 사이드바 위치: Applications > Foundry Rules > Deploy > Deploy workflow

이 페이지는 Foundry Rules 배포의 첫 단계로, Rules 애플리케이션에서 새 워크플로 템플릿을 배포하는 방법을 설명합니다. 배포 과정에서 규칙과 제안에 필요한 객체, 액션, 데이터셋, Workshop 애플리케이션이 새 프로젝트에 한꺼번에 만들어집니다.

Rules 애플리케이션 안에서 새 Foundry Rules 워크플로를 배포할 수 있습니다. 애플리케이션에서 워크플로에 필요한 [객체](../02_core-concepts/02_object-model.md)와 액션(Action)을 생성합니다.

1. **새 Rules 워크플로 배포:** 사이드바에서 Foundry Rules 애플리케이션을 찾아 선택한 다음, **Rule-based data pipeline**을 선택합니다. <br><br>
   ![Foundry Rules를 배포하는 Rules 애플리케이션의 버튼](https://www.palantir.com/docs/resources/foundry/foundry-rules/rules-workflow-create@2x.png) <br><br>

2. **구성 정보 입력:** 애플리케이션이 관련 백킹 데이터셋(backing dataset), Foundry Rules 워크플로, Workshop 애플리케이션 리소스가 포함된 새 프로젝트를 만들어 줍니다. <br><br>
   ![Rules 워크플로 구성 페이지](https://www.palantir.com/docs/resources/foundry/foundry-rules/rules_workflow_deployment_configuration@2x.png) <br><br>

   * 적절한 [스페이스(space)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/)를 선택합니다.
   * 적절한 [온톨로지(Ontology)](../../../01_ontology-building/01_overview.md)를 선택합니다. 온톨로지가 여러 개라면 규칙을 정의하려는 객체 타입이 모두 들어 있는 온톨로지를 선택합니다.
   * Rule editor 그룹은 액션의 제출 조건(submission criteria)에 사용됩니다. 이 그룹의 사용자는 규칙을 추가, 편집(edit), 삭제하는 제안(proposal)을 만들 수 있고, 제안에 대한 결정도 내릴 수 있습니다. 이 구성은 시작점으로 의도된 것이며, 나중에 규칙 액션의 제출 조건을 따로 구성할 수 있습니다. 액션 타입의 제출 조건을 변경하려면 [FAQ](#faq)를 확인하세요.

3. **배포:** 필드를 모두 채웠으면 **Deploy**를 선택합니다. 배포는 백그라운드에서 약 2\~3분 걸리며, 그동안 다른 화면으로 이동해도 안전합니다. 진행 중이거나 완료된 설치는 메인 페이지의 **Pending installations** 또는 **Existing Rule Workflows**에서 확인할 수 있습니다. 기존 워크플로 목록에서 모든 워크플로는 기본 이름 "Foundry Rules Workflow"와 타임스탬프로 표시됩니다. 프로젝트 폴더에서 해당 리소스의 이름을 바꾸면 워크플로 이름을 바꿀 수 있습니다. <br><br>
   ![Rules 워크플로 구성 페이지](https://www.palantir.com/docs/resources/foundry/foundry-rules/rules_workflow_deploy_pending.png) <br><br>

위 단계를 마쳤으면 [워크플로를 구성하는 방법](03_configure-workflow.md)을 알아보세요.

**설명**: 제출 조건은 액션을 실행하기 전에 검사하는 조건으로, "현재 사용자가 Rule editor 그룹에 속해 있는가" 같은 규칙을 걸 수 있습니다. 조건을 만족하지 않는 사용자는 액션 버튼을 눌러도 제출이 거부됩니다. 배포 시 지정한 그룹 하나가 제안 생성과 승인 권한을 모두 갖도록 기본 설정되므로, 작성자와 검토자를 분리하려면 나중에 액션별 제출 조건을 따로 고쳐야 합니다.

> **중간 요약**: Rules 애플리케이션에서 Rule-based data pipeline을 선택하고 스페이스, 온톨로지, Rule editor 그룹을 지정해 Deploy하면 약 2\~3분 뒤 필요한 리소스가 담긴 새 프로젝트가 생깁니다.

<a id="faq"></a>
## FAQ

<a id="how-do-i-change-the-submission-criteria-on-the-action-types"></a>
### 액션 타입의 제출 조건은 어떻게 변경하나요?

액션 타입의 제출 조건을 업데이트하려면 Workshop 애플리케이션으로 가서 **Edit**를 선택합니다. 그런 다음 아래와 같이 오른쪽의 Rule Editor 구성 패널을 확인합니다.

![Workshop 애플리케이션의 Rule editor 구성 패널 화면](https://www.palantir.com/docs/resources/foundry/foundry-rules/workshop-application-config-panel.png)

그다음 **Create add proposal action**의 "Create a proposal to add a rule" 드롭다운 옵션 옆에 있는 "i" 아이콘 위에 커서를 올립니다.

새로 뜬 팝업에서 **View Action Configuration**을 선택합니다.

![Create a proposal to add a rule 팝업](https://www.palantir.com/docs/resources/foundry/foundry-rules/view-action-configuration.png)

여기에서 [제출 조건](../../../02_define-ontologies/03_action-types/08_submission-criteria.md)을 변경할 수 있습니다.

## 정리

- 새 워크플로는 Foundry Rules 애플리케이션의 **Rule-based data pipeline**에서 배포합니다.
- 배포 시 스페이스, 온톨로지, Rule editor 그룹을 지정하며, 결과로 백킹 데이터셋, 워크플로, Workshop 애플리케이션이 담긴 새 프로젝트가 만들어집니다.
- Rule editor 그룹은 규칙 액션의 초기 제출 조건으로 쓰이며, 이후 Workshop의 Rule Editor 구성 패널에서 View Action Configuration을 통해 바꿀 수 있습니다.
- 워크플로 이름은 프로젝트 폴더의 리소스 이름을 바꿔 변경합니다.
