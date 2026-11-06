# Foundry Rules로 마이그레이션하기 (Migrate to Foundry Rules)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/migrate-to-foundry-rules/
- 사이드바 위치: Applications > Foundry Rules > Legacy Foundry Rules setup (Taurus) > Migrate to Foundry Rules

이 페이지는 예전 방식인 Taurus로 만든 규칙 워크플로를 현재의 Foundry Rules(V2) 워크플로로 옮기는 방법을 다룹니다. 마이그레이션을 할지 판단하는 기준, 마이그레이션 마법사의 단계별 절차, 마이그레이션 성공 여부 확인 방법, 자주 묻는 질문을 설명합니다. 레거시 설정을 쓰는 조직이 새 기능을 쓰려면 이 절차를 거쳐야 합니다.

Taurus에 대한 장기 지원은 계속되지만, 일부 조직은 변경과 파이프라인 유지 보수가 더 쉬워지고 향후 개발 업데이트를 받는 등 추가 기능의 이점을 얻기 위해 기존 Taurus 워크플로를 Foundry Rules로 마이그레이션하고 싶을 수 있습니다.

Taurus 사용 사례를 Foundry Rules로 마이그레이션하면 다음과 같은 이점을 얻을 수 있습니다.

* 하나의 Foundry Rules 구성 페이지에서 몇 분 만에 끝낼 수 있는 단순화된 배포.
* Foundry Rules 구성을 한 단계만 바꾸는 방식의 수정과 유지 보수.
* 스트리밍 워크플로를 포함해, 파이프라인 코드를 건드릴 필요 없이 바로 쓸 수 있는 실행.
* 사용자 정의 파이프라인 코드가 필요한 고급 Foundry Rules 사용 사례를 지원하는 내장 코드 생성기.

가장 좋은 Foundry Rules 워크플로는 사용자가 작성하기를 원하는 한 가지 유형의 규칙으로 하나의 구체적인 사용 사례를 겨냥하는 것입니다. 사용자 그룹이 여러 개이고 규칙 작성 애플리케이션도 여러 개라면, 마이그레이션 마법사를 여러 번 사용해 규칙 워크플로를 여러 개 만드는 것을 고려할 수 있습니다.

**설명**: Taurus 방식에서는 규칙을 실행하는 파이프라인을 사용자가 코드 저장소(Java 등)에 직접 두고 유지했습니다. Foundry Rules(V2)에서는 구성 페이지의 설정만으로 그 파이프라인이 만들어지고 실행됩니다. 그래서 "입력 데이터셋을 하나 추가"하는 변경이 코드 수정, 빌드, 배포가 아니라 구성 화면에서 한 단계로 끝납니다.

<a id="migration-considerations"></a>
## 마이그레이션 고려 사항 (Migration considerations)

Foundry Rules로 마이그레이션하기 전에 다음을 고려하세요.

* 공급망 최적화(supply chain optimization), 자금세탁방지(anti-money laundering), 자동차 산업용 QMOS처럼 Taurus를 더 큰 제품의 일부로 사용하고 있다면, 현재로서는 마이그레이션할 필요가 없습니다.

* 다음 항목이 어떤 식으로든 조합된 복잡한 Taurus 사용 사례라면, 마이그레이션에 어느 정도 리팩터링 작업이 필요하므로 앞에서 설명한 이점과 필요한 변경의 규모를 비교해 보아야 합니다.
  * Taurus Workshop 모듈에 여러 사용자 그룹을 위해 서로 다르게 구성된 rule editor 위젯이 여러 개 있습니다.
  * Taurus 저장소가 Taurus 패키지의 고급 기능을 사용하거나 규칙 로직을 특정 방식으로 적용합니다. 고급 기능을 사용하는 예로는 저장소에서 제안(proposal)을 실행해 잠재적 영향 분석을 만드는 경우가 있습니다.
  * [규칙 액션](05_configure-rule-actions.md)이 선택적 표시(optional visibility)를 구현하거나, object locator, 객체 집합(object set), 첨부 파일(attachment) 필드 타입을 사용합니다.

* Taurus 사용 사례에 입력 데이터셋, 객체 타입, 규칙 출력을 계속 추가하고 있다면, Foundry Rules가 제공하는 새 구성 인터페이스가 유지 보수성을 높여 줄 수 있습니다. Foundry Rules 워크플로와 함께 Java 저장소를 쓰기로 하더라도 부분 코드 생성의 이점을 얻을 수 있습니다.

> **중간 요약**: 더 큰 제품의 일부로 Taurus를 쓰는 경우는 마이그레이션이 필요 없고, 위젯이 여러 개이거나 고급 기능을 쓰는 복잡한 사례는 리팩터링 비용을 따져 보아야 합니다. 입력과 출력을 계속 늘리는 사례라면 새 구성 인터페이스의 이점이 큽니다.

<a id="migrate-taurus-workflow-to-foundry-rules-workflow"></a>
### Taurus 워크플로를 Foundry Rules 워크플로로 마이그레이션하기 (Migrate Taurus workflow to Foundry Rules workflow)

다음 절차는 기존 객체 타입과 Workshop 모듈은 그대로 사용하지만, 운영 중인 파이프라인이 중단되지 않도록 병렬 파이프라인과 새 출력 데이터셋을 만듭니다.

V2로 업그레이드할 때 다음 과정이 수행됩니다.

* 워크플로에 시계열(time series)이 있는지 확인합니다.
* 기존 애플리케이션을 업그레이드합니다.
* 필요한 경우 이전 애플리케이션의 연결을 해제합니다.
* 마이그레이션을 마무리하는 데 필요한 수동 작업이 있습니다.

시작하려면 아래 안내를 따르세요.

1. Foundry 작업 공간 탐색 사이드바에서 **Foundry Rules**로 이동한 다음 **Old Workflows** 탭으로 이동합니다.

2. 온톨로지를 선택하고 목록에서 V1 아키타입(archetype)을 찾거나 검색 필드를 사용합니다.

   ![기존 V1 아키타입](https://www.palantir.com/docs/resources/foundry/foundry-rules/archetype-v1-existing@2x.png)

3. **Migrate from older Version**을 선택합니다.

4. 메인 rule editor Workshop 리소스를 선택하고, 새 Foundry Rules 워크플로를 저장할 대상 폴더를 확인합니다. 필요하면 워크플로 이름을 바꿉니다. 그런 다음 **Start**를 선택합니다.

   ![기존 V1 아키타입](https://www.palantir.com/docs/resources/foundry/foundry-rules/archetype-v1-input@2x.png)

5. Foundry Rules 마이그레이션 마법사가 기존 설정에 [시계열](../05_time-series/01_timeseries-concepts.md)이 포함되어 있는지 확인합니다. 포함되어 있다면 링크 타입과 시계열 동기화(time series sync)를 구성해야 합니다. 추가 구성을 마쳤으면 **Save Rules workflow**를 선택합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/migration-wizard3.png" alt="Foundry Rules 업그레이드 마법사" width="800"/>

6. 일부 리소스는 프로젝트로 가져와야(import) 할 수 있습니다. 리소스 목록을 펼쳐 확인하고 화면에 나오는 필요한 작업을 마친 뒤 **Save**를 선택합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/migration-wizard5.png" alt="Foundry Rules 업그레이드 마법사" width="800"/>

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/migration-wizard6.png" alt="Foundry Rules 업그레이드 마법사" width="800"/>

7. **Upgrade rules application**을 선택합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/migration-wizard7.png" alt="Foundry Rules 업그레이드 마법사" width="800"/>

8. 요청이 나오면 **Unlink old application**을 선택합니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/migration-wizard8.png" alt="Foundry Rules 업그레이드 마법사" width="800"/>

9. 마지막으로 화면의 안내를 확인하고, 새로 업그레이드된 파이프라인에 대해 사용 사례에 맞는 지침을 따릅니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/migration-wizard9.png" alt="Foundry Rules 업그레이드 마법사" width="800"/>

   * Foundry Rules 출력이 온톨로지 객체 타입으로 바로 들어가는 경우.
     * 출력이 (추가 변환 없이) 온톨로지 객체 타입으로 바로 들어간다면, 알림이 새 버전의 Foundry Rules에서 나오도록 해당 객체 타입의 [객체 백킹 데이터셋](../../../02_define-ontologies/02_object-and-link-types/02_object-types/02_create-object-type.md#add-a-backing-datasource-to-a-new-object-type)을 교체해야 합니다.

**경고**: 이 방법을 쓰면 [객체 타입이 V1인 경우 객체 편집(edit)이 사라집니다](../../../02_define-ontologies/02_object-and-link-types/02_object-types/03_edit-object-type.md). 편집을 반드시 보존해야 한다면, [백킹 데이터셋을 유지 ↗](https://stackoverflow.com/questions/72477419/how-to-safely-delete-an-object-property-without-losing-the-object-edits)하면서 그 내용이 새 규칙 출력을 그대로 복사한 것이 되도록 할 수 있습니다.

* Foundry Rules 출력에 추가 변환을 적용하는 경우.
  * 변환에서 이전 규칙 출력 대신 새 출력 데이터셋을 사용하도록 바꿔야 합니다. 고급 사용 사례라면 [규칙 출력을 계산하는 사용자 정의 저장소](../04_settings-customization/06_customize-foundry-rules-pipeline.md)를 등록할 수 있습니다.
* 다른 rule editor Workshop 애플리케이션이 있는 경우.
  * 모든 rule editor의 입력과 출력이 같다면 모두 이 Rules 워크플로를 참조하게 할 수 있습니다. 왼쪽 **Applications** 탭에 있는 아키타입의 배포 메뉴로 rule editor Workshop 애플리케이션을 더 배포할 수 있습니다. rule editor들이 서로 다른 사용 사례에 쓰이고 구성도 다르다면, 새 Rules 아키타입을 배포해 각각을 전용 워크플로로 마이그레이션해야 합니다.

10. 모든 단계를 마쳤으면 **Mark migration completed**를 선택합니다. 이제 사용 사례가 새 Foundry Rules 설정에서 운영됩니다.

**설명**: 9단계의 경고는 백킹 데이터셋 교체와 관련이 있습니다. 백킹 데이터셋은 객체 타입의 각 객체를 만들어 내는 원본 테이블이고, 사용자가 Foundry 화면에서 객체 속성을 직접 고친 내용(편집)은 그 위에 따로 얹혀 저장됩니다. 원문에 따르면 V1 객체 타입에서는 백킹 데이터셋을 바꾸면 이 편집들이 사라지므로, 기존 데이터셋을 그대로 두고 그 안의 내용을 새 규칙 출력으로 채우는 방식이 대안으로 제시됩니다. "병렬 파이프라인"은 기존 Taurus 파이프라인을 끄지 않은 채 새 파이프라인을 옆에 하나 더 만들어, 새 쪽이 검증될 때까지 기존 결과가 계속 나오게 한다는 뜻입니다.

> **중간 요약**: 마이그레이션 마법사는 **Old Workflows** 탭에서 V1 아키타입을 골라 시작하며, 시계열 확인, 리소스 가져오기, 애플리케이션 업그레이드, 이전 애플리케이션 연결 해제를 거칩니다. 마지막에는 출력이 객체 타입으로 바로 가는지, 추가 변환을 거치는지, rule editor가 여러 개인지에 따라 수동 후속 작업을 하고 **Mark migration completed**를 누릅니다.

<a id="verify-migration"></a>
## 마이그레이션 확인 (Verify migration)

Foundry Rules로의 마이그레이션이 성공했는지 확인하려면, 규칙 출력 데이터셋이 저장된 프로젝트로 가는 링크에 접속합니다.

규칙 출력 데이터셋을 열고 **Build**를 선택하거나, Schedules 탭으로 가서 **Add build schedule**을 선택합니다.

<img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/foundry-rules-migration-build.jpg" alt="변환" width="800"/>

빌드가 성공하면 Foundry Rules로의 업그레이드 과정이 성공적으로 완료되었다는 뜻입니다.

<a id="faqs"></a>
## 자주 묻는 질문 (FAQs)

* 출력에 V2에서 달라진 구성이 포함되어 있다는 경고를 받았습니다. 어떻게 해결하나요?
  액션 타입 폼은 다양한 유형의 입력을 받도록 구성할 수 있습니다. 단순한 숫자나 날짜일 수도 있고, 첨부 파일, 객체 속성, 다른 폼 파라미터에서 파생된 값일 수도 있습니다. 마이그레이션 마법사는 원래 구성에 최대한 가깝게 다시 만들려고 하지만, 이 경고 메시지는 구성에 변경이 있었을 수 있다는 뜻입니다.

해결하려면 아래와 같이 규칙 효과(rule effect)의 출력 구성을 검토합니다.

<img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/migration-rule-action.png" alt="규칙 액션" width="800"/>

그런 다음 마이그레이션 5단계를 마친 뒤 rule editor 폼을 확인해, 사용 사례에 맞게 계속 동작하는지 확인합니다.

<img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/migration-outputs-review.png" alt="출력 검토" width="800"/>

* 데이터셋 빌드는 성공했는데 데이터가 하나도 없는 이유는 무엇인가요?

  빌드 작업에는 규칙 상태 데이터셋(rules status dataset)이라는 또 다른 데이터셋이 포함되어 있으며, 여기에는 각 규칙에 대한 정보와 그 규칙이 제대로 실행되지 않은 이유가 들어 있습니다. 또는 라이트백(writeback) 데이터셋을 아직 다시 실행하지 않았을 수도 있습니다. [규칙 작성 및 실행 가이드](../03_deploy/04_author-and-run-a-rule.md#author-and-run-a-rule)의 4단계를 참고하세요. 이 데이터셋은 Build 페이지의 **Transforms Configuration** 섹션에서도 찾을 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/transforms-configuration.jpg" alt="변환" width="800"/>

* 다른 사람이 동시에 Rules 애플리케이션을 변경하면 마이그레이션을 취소할 수 없는 이유는 무엇인가요?

<img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/migration-cancelled.jpg" alt="Foundry Rules 업그레이드 마법사" width="800"/>

이 오류는 Rules 애플리케이션 업그레이드 단계를 마친 상태에서 다른 사용자가 Rules 애플리케이션을 변경했고, 그 뒤에 마이그레이션을 **Cancel**(취소)하려 할 때 발생합니다.

해결하려면 Rules Workshop 애플리케이션을 열고 마이그레이션된 이전 버전을 게시(publish)해 수동으로 가한 변경을 되돌립니다. 그러면 업그레이드 과정을 정상적으로 취소할 수 있습니다.

**설명**: 취소는 "업그레이드 직후 버전"을 기준으로 원래 상태로 되돌리는 동작이라, 그 사이에 다른 사람이 새 버전을 게시하면 기준이 맞지 않아 거부됩니다. 버전 관리 시스템에서 다른 사람이 그 뒤에 커밋을 쌓으면 단순 되돌리기가 충돌하는 것과 같은 상황이며, 먼저 끼어든 변경을 되돌려 기준 버전을 맞추는 것이 해결책입니다.

* rule editor 위젯과 proposal reviewer 위젯이 각각 정확히 하나씩 있어야만 마이그레이션이 진행되는 이유는 무엇인가요?
  * Rules 애플리케이션은 rule editor 위젯과 proposal 위젯을 몇 개든 두도록 설계할 수 있지만, Taurus와 Foundry Rules에서 구성되는 방식이 다릅니다. Taurus에서는 위젯마다 서로 다른 입력을 제공하는 것처럼 고유한 속성을 주어 구성할 수 있습니다. 마이그레이션은 여러 위젯의 구성을 합치지 않고, rule editor 위젯 하나를 Rules 워크플로 하나로 변환합니다. 새 Foundry Rules 설정에서는 구성이 다르면 각각 별도의 Rules 워크플로가 되어야 합니다.
  * 마이그레이션에서 이 문제를 해결하려면 다음 상황별 해결 방법을 검토한 뒤 마이그레이션 마법사를 다시 진행하세요. Workshop 변경은 버전으로 관리되므로 필요하면 변경을 되돌릴 수 있습니다.
    * 실수로 rule editor 위젯이 여러 개 있고 그중 하나만 의미가 있는 경우: 불필요한 위젯을 Workshop 모듈에서 제거하고 마이그레이션을 다시 시도합니다.
    * 구성이 같은 위젯이 여러 개 있는 경우: 하나만 남기고 모두 제거합니다. 마이그레이션 후 업데이트된 위젯을 복사해 붙여 넣어 애플리케이션 디자인을 다시 만들 수 있습니다.
    * 구성이 서로 다른 위젯이 여러 개 있는 경우: Workshop 모듈을 rule editor 위젯이 하나씩 있는 여러 모듈로 나누고, 각각에 대해 Rules 아키타입을 만듭니다. 시간을 아끼려면 마법사에서 **Migrate from older version**을 선택해 각 Workshop 모듈에서 구성을 만듭니다.

> **중간 요약**: 마이그레이션 후 규칙 출력 데이터셋이 성공적으로 빌드되면 완료된 것입니다. 구성 변경 경고는 규칙 효과와 폼을 직접 검토해 해결하고, 빈 출력은 규칙 상태 데이터셋과 라이트백 재실행 여부를 확인하며, 위젯이 여러 개면 rule editor 하나당 워크플로 하나가 되도록 모듈을 정리한 뒤 다시 진행합니다.

## 정리

- Taurus는 계속 지원되지만, Foundry Rules(V2)로 옮기면 구성 페이지 기반 배포, 코드 없는 실행, 내장 코드 생성기의 이점이 있습니다.
- 더 큰 제품의 일부로 Taurus를 쓰면 마이그레이션이 필요 없고, 복잡한 사례는 리팩터링 비용을 따져 봅니다.
- 마이그레이션은 기존 객체 타입과 Workshop 모듈을 유지한 채 병렬 파이프라인과 새 출력 데이터셋을 만들며, 마법사의 10단계를 따릅니다.
- 출력이 객체 타입으로 바로 들어가면 백킹 데이터셋 교체가 필요하며, V1 객체 타입에서는 편집 손실에 주의합니다.
- 규칙 출력 데이터셋 빌드 성공으로 마이그레이션을 확인하고, rule editor 위젯은 워크플로당 하나가 되도록 정리합니다.
