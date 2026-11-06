# Object Monitors 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-monitors/overview/
- 사이드바 위치: Applications > Object Monitors [Sunset] > Overview

이 페이지는 온톨로지의 데이터가 바뀌는 것을 감시하다가 조건이 맞으면 알림을 보내거나 액션을 자동으로 실행하는 Object Monitors 애플리케이션을 소개합니다. 이 제품은 단계적 종료(sunset) 단계에 있어 Automate로 옮겨 가도록 권장되지만, 감시 대상(입력), 조건, 알림, 자동 액션이라는 구조는 데이터 변경에 반응하는 시스템을 이해하는 데 기본이 되는 개념입니다.

**주의**: 단계적 종료(Sunset). Object Monitors는 개발 수명 주기상 [단계적 종료(sunset)](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으며, 향후 지원 중단(deprecated)될 예정입니다. 전체 지원은 계속 제공됩니다. 워크플로를 [Automate](https://www.palantir.com/docs/foundry/automate/overview/)로 옮기는 것을 권장합니다. Automate는 이전 버전과 완전히 호환되는 제품으로, 플랫폼의 모든 비즈니스 자동화를 위한 단일 진입점을 제공합니다.

**Object Monitors** 애플리케이션은 최종 사용자와 애플리케이션 빌더가 Foundry 온톨로지(Ontology)의 데이터가 언제 바뀌는지 알 수 있게 해 줍니다. 변경이 일어나면, 객체 모니터는 지정한 조건이 충족될 때 자동으로 알림을 보내거나 액션을 제출할 수 있습니다. 객체 모니터는 데이터 위에서 실행되며, 사용자가 개별 검색과 객체를 추적하도록 돕기 위해 설계되었습니다. 또한 객체 모니터는 애플리케이션 빌더가 Foundry에서 만든 애플리케이션에 모니터링과 경보 기능을 포함시키는 도구로도 쓰입니다.

객체 모니터링은 데이터의 내용을 감시하도록 설계되었습니다. 데이터 연결이나 파이프라인 빌드의 상태(health) 모니터링이 필요하다면 [Health checks](https://www.palantir.com/docs/foundry/health-checks/overview/) 문서를 참고합니다.

**설명**: 두 종류의 감시를 구분해야 합니다. Health checks는 "데이터를 만드는 과정이 정상인가"(예: 어젯밤 파이프라인 빌드가 실패했는가)를 봅니다. Object Monitors는 "데이터의 값이 어떤가"(예: 재고가 10개 미만인 창고 객체가 새로 생겼는가)를 봅니다. 데이터베이스로 말하면 Object Monitors는 테이블 내용의 변화에 반응하는 트리거(trigger)에 가까운 역할을 합니다.

객체 모니터링은 Foundry 객체 계층의 기능이며 다양한 워크플로에 사용할 수 있습니다. 예를 들면 다음과 같습니다.

* **감시 검색(Watched searches):** 사용자는 저장된 객체 탐색에 새 결과가 생기거나, 검색 결과 전체에 걸쳐 집계 기준이 충족될 때 알림을 받도록 객체 모니터를 구성할 수 있습니다.
* **자동 알림(Automated notifications):** 워크플로 빌더와 셀프서비스 데이터 소비자는 데이터 변경에 반응해 알림을 보내도록 객체 모니터를 구성할 수 있습니다. 알림은 다음 방법으로 보낼 수 있습니다.
  * Foundry 알림 센터의 플랫폼 내 팝업
  * 이메일
  * SMS([Twilio ↗](https://www.twilio.com/) 같은 서드파티 서비스로 보내는 [웹훅](https://www.palantir.com/docs/foundry/data-connection/webhooks-overview/) 사용)
  * 인스턴트 메시지([Slack ↗](https://slack.com/)이나 [Microsoft Teams ↗](https://www.microsoft.com/microsoft-teams/group-chat-software) 같은 서드파티 서비스로 보내는 웹훅 사용)
  * 맞춤형 또는 독자적인 메시징 시스템
* **워크플로 자동화(Workflow automation):** 객체 모니터를 사용해, 특정 기준을 충족하는 객체 데이터에 대해 액션을 자동으로 수행할 수 있습니다. 객체 모니터로 자동화할 수 있는 작업의 예는 다음과 같습니다.
  * 데이터 이상(anomaly)을 확인하고, 해당 객체를 문제를 바로잡는 로직이 담긴 액션에 자동으로 넘기기
  * 제안이나 잠재적 액션을 지켜보다가, 미리 구성한 이벤트 조건과 시간 조건이 충족되면 자동으로 적용하기. 이런 액션에는 웹훅으로 외부 시스템에 API 호출을 보내 외부 시스템에 직접 변경을 적용하는 것도 포함될 수 있습니다.

**설명**: 웹훅(webhook)은 어떤 일이 일어났을 때 미리 등록해 둔 외부 URL로 HTTP 요청을 보내는 방식입니다. 예를 들어 Slack이 제공하는 웹훅 URL로 `{"text": "재고 부족 창고 3곳"}` 같은 JSON을 POST하면 해당 채널에 메시지가 올라갑니다. Foundry는 이 방식으로 Twilio(SMS), Slack, Teams 같은 외부 서비스와 연결합니다.

> **중간 요약**: Object Monitors는 온톨로지 데이터의 변화를 감시해 조건이 맞으면 알림(플랫폼 팝업, 이메일, 웹훅 기반 SMS나 메신저)을 보내거나 액션을 자동 실행합니다. 파이프라인 상태 감시는 Health checks의 몫이며, 이 제품은 sunset 단계라 Automate로의 이전이 권장됩니다.

<a id="access-object-monitors"></a>
## Object Monitors 열기 (Access Object Monitors)

Object Monitors 애플리케이션에 접근하려면 브라우저 왼쪽의 Foundry 내비게이션 사이드바에서 이름이나 아이콘을 클릭합니다. **Overview** 페이지에는 최근 모니터 활동 목록과 함께 전체 모니터 수, 구독 중이거나 음소거된 모니터 수, 오류가 있거나 곧 만료될 모니터 수가 표시됩니다.

**Monitors** 페이지에는 사용할 수 있는 모니터의 전체 목록이 표시됩니다. 이 목록은 활동 상태, 알림 및 액션 설정, 작성자, 만료일, 모니터 유형, 조건 상태로 필터링할 수 있습니다. 모니터를 클릭하면 모니터 개요 패널이 열려 과거 활동, 구독자, 기타 세부 정보를 볼 수 있습니다.

[새 객체 모니터 만들기](02_create_new_object_monitor.md)에서 객체 모니터링에 대해 더 알아봅니다.

## 정리

- Object Monitors는 온톨로지 데이터 내용의 변화를 감시하고, 조건 충족 시 알림을 보내거나 액션을 자동으로 제출합니다.
- 주요 용도는 감시 검색, 자동 알림(팝업, 이메일, 웹훅 기반 SMS와 메신저 등), 워크플로 자동화입니다.
- 파이프라인과 데이터 연결의 상태 감시는 Health checks를 사용합니다.
- 애플리케이션의 Overview 페이지에서 활동 요약을, Monitors 페이지에서 전체 모니터 목록과 세부 정보를 봅니다.
- 이 제품은 sunset 단계이므로 Automate로 이전하는 것이 권장됩니다.
