# 알림 (Notifications)

- 원문: https://www.palantir.com/docs/foundry/object-monitors/notifications/
- 사이드바 위치: Applications > Object Monitors [Sunset] > Core concepts > Notifications

이 페이지는 객체 모니터(object monitor)의 구독자가 모니터에 새 활동이 생겼을 때 받는 알림을 설명합니다. 구독자별 알림 끄기, 사용자별 알림 수신 방식 설정, 활동 유형별 알림 범주, 그리고 알림 내용을 템플릿이나 함수(function)로 사용자 정의하는 방법을 다룹니다. Object Monitors는 지원 종료(Sunset) 단계의 제품으로, 후속 제품은 Automate입니다.

객체 모니터의 구독자는 모니터에 새 활동이 있을 때 알림을 받도록 선택할 수 있습니다.

알림은 모든 구독자에게 기본으로 활성화되어 있지만, 구독자별로 비활성화할 수 있습니다. 알림을 끄려면 Object Monitors 애플리케이션에서 모니터를 구성하거나 편집할 때 **Subscribers** 탭의 종 아이콘을 클릭하세요.

![Subscribers 탭에서 알림 끄기](https://www.palantir.com/docs/resources/foundry/object-monitors/monitor_subscriber_notifications_configuration.png)

개별 사용자는 Object Monitors에서 알림을 받는 방식을 설정할 수도 있습니다. 모니터 구성 모달의 **Notification** 탭에서 알림을 설정할 수 있으며, 이 설정은 그 사용자가 구독한 모든 모니터에 전역으로 적용됩니다.

![알림 설정 구성](https://www.palantir.com/docs/resources/foundry/object-monitors/monitor_notifications_settings.png)

| 범주(Category) | 활동 유형(Activity types) |
| ------------- | ----------------------- |
| `Triggered`   | [Monitor triggered(모니터 트리거됨)](05_activity.md#monitor-triggered) |
| `Recovered`   | [Monitor recovered(모니터 복구됨)](05_activity.md#monitor-recovered) |
| `Errors`      | [Evaluation failed(평가 실패)](05_activity.md#evaluation-failed) |
| `Other info`  | [Condition edited(조건 편집됨)](05_activity.md#condition-edited), [Subscribed(구독함)](05_activity.md#subscribed), [Unsubscribed(구독 해제함)](05_activity.md#unsubscribed), [Muted(음소거됨)](05_activity.md#muted), [Unmuted(음소거 해제됨)](05_activity.md#unmuted), [Disabled(비활성화됨)](05_activity.md#disabled), 또는 [Enabled(활성화됨)](05_activity.md#enabled) |

**설명**: 설정이 두 층으로 나뉜다는 점이 핵심입니다. 모니터 쪽(**Subscribers** 탭의 종 아이콘)은 "이 모니터가 이 구독자에게 알림을 보낼지"를 정하고, 사용자 쪽(**Notification** 탭)은 "내가 구독한 모든 모니터의 알림을 어떤 범주에 대해, 어떤 경로로 받을지"를 정합니다. 예를 들어 사용자가 `Other info` 범주를 꺼 두면, 누군가 모니터 조건을 편집하거나 구독을 추가해도 알림을 받지 않고 실제 트리거(`Triggered`)와 오류(`Errors`) 알림만 받게 됩니다.

> **중간 요약**: 알림은 구독자마다 기본으로 켜져 있으며, 모니터의 **Subscribers** 탭에서 구독자별로 끌 수 있고, 사용자는 **Notification** 탭에서 모든 구독 모니터에 적용되는 수신 방식을 정합니다. 활동 유형은 `Triggered`, `Recovered`, `Errors`, `Other info` 네 범주로 묶입니다.

<a id="custom-notification-content"></a>
## 사용자 정의 알림 내용 (Custom notification content)

[모니터 트리거됨(monitor triggered)](05_activity.md#monitor-triggered)과 [모니터 복구됨(monitor recovered)](05_activity.md#monitor-recovered) 활동에 대해 보내는 알림은 사용자 정의할 수 있습니다. Object Monitors 애플리케이션에서 모니터를 구성하거나 편집할 때 **Notifications** 탭에서 사용자 정의 알림 구성을 제공할 수 있습니다.

<a id="templated-rendering"></a>
### 템플릿 렌더링 (Templated rendering)

템플릿 렌더링을 사용하면 사용자 정의 내용(제목, 본문, 링크 라벨, 링크 대상 포함)이 제공된 양식에 직접 표시됩니다. 원한다면 고급 이메일 구성에서 HTML을 사용할 수도 있습니다. 양식 오른쪽에서 플랫폼 내 알림과 이메일 알림의 미리 보기를 볼 수 있습니다.

![monitor\_custom\_notifications\_templated](https://www.palantir.com/docs/resources/foundry/object-monitors/monitor_custom_notifications_templated.png)

<a id="function-backed-rendering"></a>
### 함수 기반 렌더링 (Function-backed rendering)

함수 기반 렌더링을 사용하면 사용자 정의 내용이 제공된 알림 반환 타입을 사용하는 함수에서 반환됩니다. 이벤트 조건이 있는 모니터의 경우, 함수는 모니터링 대상 객체 타입의 `ObjectSet<>`을 입력으로 받을 수 있으므로, 모니터가 감지한 객체에 대한 데이터를 추출해 알림 내용에 직접 렌더링할 수 있습니다.

**설명**: 두 방식의 차이는 내용이 고정이냐 계산되느냐입니다. 템플릿은 양식에 미리 써 둔 문구가 그대로 나갑니다. 함수 기반은 모니터가 트리거될 때마다 함수가 실행되어 그때 감지된 객체 집합을 입력으로 받아 제목과 본문을 만들어 반환합니다. 예를 들어 "새로 지연된 항공편" 모니터라면 함수가 `ObjectSet<Flight>`을 받아 "지연 항공편 3건: KE001, KE017, OZ202"처럼 실제 객체 목록이 들어간 본문을 만들 수 있습니다.

> **중간 요약**: 트리거와 복구 알림은 **Notifications** 탭에서 사용자 정의할 수 있습니다. 템플릿 렌더링은 양식에 적은 고정 내용(HTML 가능)을 보내고, 함수 기반 렌더링은 감지된 객체 집합을 받아 내용을 동적으로 생성합니다.

## 정리

- 객체 모니터 구독자는 새 활동이 있을 때 알림을 받으며, 기본으로 켜져 있고 구독자별로 끌 수 있습니다.
- 사용자는 **Notification** 탭에서 구독한 모든 모니터에 전역으로 적용되는 알림 수신 방식을 설정합니다.
- 활동 유형은 `Triggered`, `Recovered`, `Errors`, `Other info` 범주로 나뉩니다.
- 트리거와 복구 알림 내용은 템플릿 렌더링(고정 내용) 또는 함수 기반 렌더링(감지된 객체 집합으로 동적 생성)으로 사용자 정의할 수 있습니다.
