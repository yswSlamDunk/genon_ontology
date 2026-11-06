# 새 객체 모니터 만들기 (Create a new object monitor)

- 원문: https://www.palantir.com/docs/foundry/object-monitors/create_new_object_monitor/
- 사이드바 위치: Applications > Object Monitors [Sunset] > Create a new object monitor

이 페이지는 객체 모니터를 만드는 두 가지 경로를 단계별로 설명합니다. 하나는 Object Explorer에서 저장한 탐색을 바로 감시하도록 만드는 간단한 경로이고, 다른 하나는 Object Monitors 애플리케이션에서 조건, 입력, 구독자를 모두 지정하는 전체 경로입니다. 어느 경로든 감시 대상은 저장된 탐색이라는 점이 핵심입니다.

**주의**: 단계적 종료(Sunset). Object Monitors는 [Automate](https://www.palantir.com/docs/foundry/automate/overview/)로 대체되었습니다. Automate는 이전 버전과 완전히 호환되는 제품으로, 플랫폼의 모든 비즈니스 자동화를 위한 단일 진입점을 제공합니다.

객체 모니터를 만들려면 먼저 데이터가 Foundry 온톨로지에 통합되어 있어야 합니다. 아직 데이터가 통합되지 않았다면 먼저 [온톨로지를 만드는 방법](../../01_ontology-building/01_overview.md)을 알아봅니다.

<a id="create-from-object-explorer"></a>
## Object Explorer에서 만들기 (Create from Object Explorer)

Object Explorer에서는 탐색을 저장한 뒤 화면 오른쪽 위의 **Monitor**를 클릭해 모니터를 만들 수 있습니다. 탐색은 탐색 화면에서 **Save**를 클릭하고 프로젝트나 폴더 위치를 선택해 저장할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/save_exploration_tooltip.png" alt="탐색 저장 툴팁" width="400"/>

<a id="create-an-object-monitor"></a>
### 객체 모니터 만들기 (Create an object monitor)

탐색을 저장한 뒤 **Monitor**를 클릭하면, 이 탐색을 입력으로 사용하는 모든 객체 모니터를 보여 주는 화면이 열립니다. 새로 만든 탐색이라면 이 목록은 비어 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/add_new_monitor_popover_zero_state.png" alt="새 모니터 추가 팝오버(빈 상태)" width="400"/>

**Add new Monitor**를 클릭하면 새 모니터를 위한 간소화된 설정 화면이 열립니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/create_new_monitor_object_explorer_view.png" alt="Object Explorer의 새 모니터 만들기 화면" width="400"/>

모니터 이름, 선택 사항인 설명, 그리고 모니터 [조건](03_core-concepts/03_condition.md)을 입력합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/condition_dropdown_create_new_monitor_object_explorer_view.png" alt="Object Explorer의 새 모니터 만들기 화면의 조건 드롭다운" width="400"/>

**참고**: 중첩된 하위 조건을 포함하는 고급 조건은 이 화면에서 구성할 수 없습니다. 이런 조건은 Object Monitors 애플리케이션에서 만들고 수정해야 합니다.

기본 저장 위치를 **Private**(비공개)에서 공개(Public) 프로젝트로 바꿀 수도 있습니다(선택 사항). 다른 구독자를 추가할 계획이라면 저장된 탐색과 모니터를 공유 프로젝트에 보관하는 것을 권장합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/monitor_save_location_dialog.png" alt="모니터 저장 위치 대화상자" width="400"/>

필요한 정보를 입력하고 저장을 클릭하면 해당 탐색의 모니터 목록으로 돌아갑니다. 이제 이 목록에 새로 만든 모니터가 들어 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/after_creation_monitor_list_object_explorer.png" alt="생성 후 Object Explorer의 모니터 목록" width="400"/>

**설명**: 비공개 위치(본인 홈 폴더)에 저장한 리소스는 기본적으로 본인만 접근할 수 있습니다. 다른 사람이 모니터와 그 입력인 탐색을 열어 보고 구독하려면 접근 권한이 필요하므로, 여러 사람이 구독할 모니터는 팀이 함께 쓰는 프로젝트에 저장하라는 권장이 나오는 것입니다.

<a id="after-saving"></a>
### 저장한 뒤 (After saving)

모니터를 저장하고 나면 추가 옵션을 사용할 수 있습니다.

모니터의 저장 위치, 생성 시각, 마지막 업데이트 시각 같은 메타데이터는 **Details** 탭에 표시됩니다. 이 탭에는 [만료일](03_core-concepts/01_monitor.md#expiration)도 표시되며, 만료일을 3개월 뒤로 연장할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/object_explorer_monitor_details_tab.png" alt="Object Explorer 모니터의 Details 탭" width="400"/>

**Subscribers** 탭에서 구독자를 추가하거나 제거할 수 있고, 구독자마다 알림을 켜거나 끌 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/object_explorer_monitor_subscribers_tab.png" alt="Object Explorer 모니터의 Subscribers 탭" width="400"/>

**Actions** 탭에서 선택적으로 액션을 구성할 수 있습니다.

Object Monitors에서 [액션을 구성하는 방법](03_core-concepts/07_actions.md)을 더 알아봅니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/object_explorer_monitor_actions_tab.png" alt="Object Explorer 모니터의 Actions 탭" width="400"/>

빠른 작업(quick actions) 드롭다운에는 모니터를 비활성화하거나 음소거하는 옵션과, 모니터를 휴지통으로 옮겨 삭제하는 옵션이 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/object_explorer_monitor_quick_actions_popover.png" alt="Object Explorer 모니터의 빠른 작업 팝오버" width="400"/>

> **중간 요약**: Object Explorer에서 탐색을 저장하고 **Monitor**, **Add new Monitor**를 차례로 눌러 이름, 설명, 조건을 입력하면 모니터가 만들어집니다. 저장 후에는 Details(만료일 연장), Subscribers, Actions 탭과 빠른 작업 메뉴(비활성화, 음소거, 삭제)를 사용할 수 있습니다. 중첩 조건은 이 화면에서 만들 수 없습니다.

<a id="create-from-object-monitors-application"></a>
## Object Monitors 애플리케이션에서 만들기 (Create from Object Monitors application)

Object Monitors 애플리케이션은 한 사용자가 모든 프로젝트에 걸쳐 사용할 수 있는 모든 모니터의 개요를 보여 줍니다. 애플리케이션 화면에서 새 모니터를 만들려면 다음 단계를 따릅니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/management_application_overview.png" alt="관리 애플리케이션 개요"/>

1. 오른쪽 위의 **Add Monitor**를 클릭해 새 모니터를 만듭니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/management_app_create_new_monitor_zero_state.png" alt="관리 앱의 새 모니터 만들기(빈 상태)"/>

2. 새 모니터의 저장 위치를 선택합니다. 구독자가 여러 명일 모니터는 공유 프로젝트에 보관하는 것을 권장합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/management_app_change_save_location.png" alt="관리 앱의 저장 위치 변경"/>

3. 전체 조건 구성을 입력합니다. 구성 옵션은 [이벤트](03_core-concepts/03_condition.md#event) 조건을 쓰는지 [임계값](03_core-concepts/03_condition.md#threshold) 조건을 쓰는지에 따라 달라집니다. 모니터 [입력](03_core-concepts/02_input.md)은 Object Explorer에서 만든 기존의 저장된 탐색을 사용해야 합니다. 필요한 입력 탐색이 없다면 Object Explorer에서 [탐색을 만든](../01_object-explorer/04_analyze-and-compare/06_save-explorations.md) 뒤 이 단계로 돌아옵니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/management_app_threshold_condition_tab.png" alt="관리 앱의 임계값 조건 탭"/>

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/management_app_event_condition_tab.png" alt="관리 앱의 이벤트 조건 탭"/>

**Subscribers** 탭에서 구독자를 추가할 수 있습니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-monitors/management_app_subscriber_tab.png" alt="관리 앱의 Subscribers 탭"/>

4. **Save**를 클릭해 새 모니터를 저장하고 활성화합니다.

## 정리

- 객체 모니터를 만들려면 먼저 데이터가 온톨로지에 통합되어 있어야 하며, 모니터의 입력은 항상 저장된 탐색입니다.
- Object Explorer에서는 탐색 저장 후 **Monitor** 버튼으로 이름, 설명, 단순 조건만 지정해 빠르게 만들 수 있습니다.
- Object Monitors 애플리케이션에서는 **Add Monitor**로 저장 위치, 이벤트 또는 임계값 조건, 입력, 구독자를 모두 구성합니다.
- 여러 사람이 구독할 모니터는 공유 프로젝트에 저장하는 것이 권장되며, 저장 후 만료일 연장, 구독자 관리, 액션 구성이 가능합니다.
