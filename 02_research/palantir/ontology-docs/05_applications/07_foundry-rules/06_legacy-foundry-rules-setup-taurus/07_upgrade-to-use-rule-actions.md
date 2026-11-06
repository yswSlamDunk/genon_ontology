# 규칙 액션 사용으로 업그레이드 (Upgrade to use rule Actions)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/upgrade-to-use-rule-actions/
- 사이드바 위치: Applications > Foundry Rules > Legacy Foundry Rules setup (Taurus) > Upgrade to use rule Actions

이 페이지는 데이터셋 입력만 지원하던 구버전 Foundry Rules(옛 이름 Taurus)를 객체 입력과 규칙 액션(rule Action)을 쓰는 방식으로 업그레이드하는 절차를 다룹니다. 라이브러리 버전 올리기, 로직 버전 변경, Workshop 애플리케이션 설정, 트랜스폼 파이프라인 코드 갱신까지 다섯 단계로 구성됩니다.

**주의**: 이 단계는 Foundry Rules(이전 이름 Taurus)의 레거시 버전을 위한 것입니다. Foundry Rules 배포를 이제 막 시작하는 경우에는 다음 단계가 필요 없으며, 이미 [기본 설정](../03_deploy/01_deploy-foundry-rules.md)에 포함되어 있습니다. 이 섹션으로 따로 안내받은 경우가 아니라면 이 단계를 따를 필요가 없을 가능성이 큽니다.

이전에는 Foundry Rules가 규칙의 [입력](../02_core-concepts/04_rule-logic.md#inputs)으로 데이터셋만 지원했고 [규칙 액션](05_configure-rule-actions.md)이라는 개념이 없었습니다. 객체에 대해 규칙을 작성하는 것은 선택 기능이지만, **규칙 액션(rule Actions)** 을 사용하도록 업그레이드할 것을 강력히 권장합니다. 특히 객체를 사용하도록 업그레이드한다면 더욱 그렇습니다.

**설명**: 규칙 액션은 규칙이 조건에 맞는 데이터를 찾았을 때 무엇을 할지(예: 알림 객체 생성, 담당자 지정)를 온톨로지의 액션 타입으로 정의한 것입니다. 구버전은 규칙 결과를 데이터셋 행으로만 내보냈다면, 규칙 액션을 쓰면 결과가 액션 타입을 통해 온톨로지에 반영됩니다.

Foundry Rules에서 객체와 규칙 액션을 활성화하려면 아래 단계를 따르세요.

*모든 스크린숏은 가상의 데이터를 사용합니다.*

1. **Foundry Rules 트랜스폼 라이브러리 버전 업그레이드:** 프로젝트 수준 `build.gradle` 파일에서 `tau-execution:tau-execution-core`가 *최소* `0.60.4` 버전인지 확인합니다.
   * `compile "com.palantir.tau-execution:tau-execution-core:0.60.4"`
   * `build.gradle` 파일을 찾을 수 없다면, **Files** 사이드바의 톱니바퀴 아이콘 아래에 있는 **Show hidden files and folders**(숨김 파일 및 폴더 표시) 옵션을 체크합니다.

2. **로직 버전 업데이트:** Foundry Rules Workshop 애플리케이션의 편집 모드에서 **Rule Editor widget**으로 이동해 **Logic Version**을 "V1"으로 변경합니다. 이 선택기를 바꿔도 파괴적인 영향은 없지만, V1으로 바꾼 뒤에는 다시 V0으로 되돌릴 수 없습니다. 다만 V0으로 돌아가서 얻는 이점도 없습니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/v1_logic_version_selection.png" alt="Workshop 앱에서 V1 로직 버전 선택" width="300" />

3. **Workshop 애플리케이션에 객체 추가:** 같은 Workshop 애플리케이션에서 Foundry Rules 안에서 쓸 수 있게 하려는 객체 타입을 **Permitted object types** 객체 집합 변수에 추가합니다. 이 변수는 아래와 같이, 노출하려는 모든 객체 타입을 합친(union) 객체 집합이어야 합니다.

   * 데이터셋에서 그에 대응하는 객체로 전환하는 경우, 기존 규칙이 모두 그 객체를 사용하도록 이전될 때까지 Foundry Rules에서 데이터셋을 계속 사용할 수 있게 두어야 합니다. 다만 트랜스폼은 둘을 모두 선언한 상태로 계속 동작할 수 있으므로 즉시 객체로 전환해야 할 급한 이유는 없습니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/add_input_objects_to_workshop_app.png" alt="Workshop 앱에 추가 입력 객체 추가" width="700" />

4. **규칙 액션 추가:** [Ontology Manager](../../04_ontology-manager/01_overview.md)에서 적절한 Foundry 액션을 만든 뒤, **Add Rule actions**를 클릭해 그 액션을 Workshop 애플리케이션에 추가합니다.

   규칙 액션 [설정](05_configure-rule-actions.md)에 대해 더 알아보세요.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/rule_action_configuration.png" alt="사용 가능한 규칙 액션 설정" width="500" />

   **팁**: Workshop 설정에 규칙 액션을 추가하고 나면, 기존 규칙은 각각 다음에 편집될 때 규칙 액션을 설정해야 합니다. 하지만 각 규칙에 규칙 액션이 설정되지 않은 상태에서도 기존 트랜스폼 파이프라인은 계속 동작합니다. 따라서 이전(migration)에 따른 중단 시간이 없으며, 사용자에게 맞는 속도로 이전을 진행할 수 있습니다.

5. **트랜스폼 파이프라인 코드 업데이트:** 트랜스폼 파이프라인을 업데이트하는 가장 간단한 방법은 Ontology Manager 안에 있는 기존 규칙 워크플로 템플릿 인스턴스에 빠진 객체와 액션을 추가해 업데이트하는 것입니다. 그런 다음 업데이트된 트랜스폼을 배포해 참고용으로 사용합니다. 참고용 트랜스폼을 배포한 뒤에는 [트랜스폼 파이프라인을 설정](04_configure-transforms-pipeline.md)해 이 새 코드를 기존 워크플로에 매핑할 수 있습니다.

   **주의**: 위에서 언급했듯이 새 트랜스폼 코드가 동작하려면 모든 규칙에 규칙 액션이 설정되어 있어야 합니다. 따라서 트랜스폼 변경은 브랜치에서 하고, 병합(merge)하기 전에 그 변경을 테스트할 것을 권장합니다.

**설명**: 4단계와 5단계의 차이가 중요합니다. 기존 트랜스폼은 규칙 액션이 없는 규칙도 처리하므로 4단계 이후에도 그대로 돌아갑니다. 반면 5단계의 새 트랜스폼 코드는 모든 규칙에 규칙 액션이 있다고 가정합니다. 그래서 규칙 이전이 끝나기 전에 새 코드를 기본 브랜치에 병합하면 실행이 실패할 수 있으므로, 별도 브랜치에서 먼저 검증하라는 것입니다.

> **중간 요약**: 라이브러리를 `0.60.4` 이상으로 올리고, 로직 버전을 V1으로 바꾸고, 객체 타입과 규칙 액션을 Workshop에 추가한 뒤, 트랜스폼 코드를 브랜치에서 갱신하고 검증하는 순서로 업그레이드합니다.

## 정리

- 이 절차는 데이터셋 입력만 지원하던 레거시 Foundry Rules에만 해당하며, 신규 배포에는 이미 포함되어 있습니다.
- `build.gradle`에서 `tau-execution-core`를 `0.60.4` 이상으로 올리고, Rule Editor 위젯의 **Logic Version**을 V1으로 바꿉니다(되돌릴 수 없음).
- 사용할 객체 타입을 **Permitted object types**에 합친 객체 집합으로 추가하고, Ontology Manager에서 만든 액션을 **Add Rule actions**로 추가합니다.
- 기존 규칙은 편집할 때마다 규칙 액션을 설정하면 되므로 중단 없이 점진적으로 이전할 수 있습니다.
- 새 트랜스폼 코드는 모든 규칙에 규칙 액션이 있어야 하므로 브랜치에서 테스트한 뒤 병합합니다.
