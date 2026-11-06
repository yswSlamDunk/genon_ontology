# 활동 (Activity)

- 원문: https://www.palantir.com/docs/foundry/object-monitors/activity/
- 사이드바 위치: Applications > Object Monitors [Sunset] > Core concepts > Activity

이 페이지는 객체 모니터의 활동(activity) 기록이 언제 남는지, 어디서 볼 수 있는지, 그리고 어떤 종류의 활동 이벤트가 있는지를 설명합니다. 조건이 발동하거나 회복된 기록뿐 아니라 조건 편집, 구독, 음소거, 비활성화 같은 관리 동작도 활동으로 기록됩니다.

**주의**: 단계적 종료(Sunset). Object Monitors는 [Automate](https://www.palantir.com/docs/foundry/automate/overview/)로 대체되었습니다. Automate는 이전 버전과 완전히 호환되는 제품으로, 플랫폼의 모든 비즈니스 자동화를 위한 단일 진입점을 제공합니다.

객체 모니터 활동은 조건에 따라, 그리고 특정 메타데이터 속성이 변경되거나 업데이트될 때 기록됩니다.

사용자가 구독한 모든 모니터의 활동 타임라인은 Object Monitors 애플리케이션의 **Overview** 페이지에 표시됩니다.

![Object Monitors 앱의 Overview 페이지](https://www.palantir.com/docs/resources/foundry/object-monitors/object_monitors_app_overview.png)

모니터 하나의 활동 타임라인은 개별 모니터 개요 패널의 **History** 탭에 표시됩니다.

![Object Monitors 앱의 활동 타임라인](https://www.palantir.com/docs/resources/foundry/object-monitors/object_monitors_app_activity_timeline.png)

<a id="activity-event-types"></a>
## 활동 이벤트 유형 (Activity event types)

<a id="monitor-triggered"></a>
### `Monitor triggered`

`Monitor triggered`(모니터 발동)는 임계값 조건의 상태가 `false`에서 `true`로 바뀔 때, 그리고 이벤트 조건에서 이벤트가 감지될 때 기록됩니다.

<a id="monitor-recovered"></a>
### `Monitor recovered`

`Monitor recovered`(모니터 회복)는 임계값 조건의 상태가 `true`에서 `false`로 바뀔 때 기록됩니다. 이벤트 조건은 `monitor recovered` 활동을 만들지 않습니다.

**설명**: 임계값 조건 "주문 합계 > 10,000"을 예로 들면, 합계가 9,000에서 12,000이 되는 순간 `Monitor triggered`가, 다시 8,000으로 내려가는 순간 `Monitor recovered`가 기록됩니다. 이벤트 조건은 "객체 추가" 같은 일회성 사건이라 "원래대로 돌아왔다"는 상태 개념이 없으므로 회복 기록이 생기지 않습니다.

<a id="condition-edited"></a>
### `Condition edited`

`Condition edited`(조건 편집됨)는 사용자가 모니터 조건을 업데이트할 때 기록됩니다. 어느 사용자가 편집하든 기록됩니다.

<a id="subscribed"></a>
### `Subscribed`

`Subscribed`(구독함)는 모니터를 구독할 때 기록됩니다. 구독하지 않은 기간의 활동은 기록되거나 표시되지 않습니다.

<a id="unsubscribed"></a>
### `Unsubscribed`

`Unsubscribed`(구독 해제함)는 모니터 구독을 해제할 때 기록됩니다. 구독하지 않은 기간의 활동은 기록되거나 표시되지 않습니다.

<a id="evaluation-failed"></a>
### `Evaluation failed`

`Evaluation failed`(평가 실패)는 어떤 이유로든 모니터 평가가 실패할 때 기록됩니다. 실패에 대한 세부 정보는 해당 모니터의 활동 **History** 화면에서 볼 수 있습니다. 모니터 조건은 성공적으로 평가되었지만 알림이나 액션이 실패한 경우에도 `Evaluation failed`가 표시될 수 있습니다.

<a id="muted"></a>
### `Muted`

`Muted`(음소거됨)는 사용자가 모니터를 음소거할 때 기록됩니다. 어느 사용자가 음소거하든 기록됩니다. 음소거는 모든 구독자에게 적용됩니다. 음소거된 모니터도 계속 평가되지만, 부수 효과(side effect, 예: 알림이나 액션)는 발생하지 않습니다.

<a id="unmuted"></a>
### `Unmuted`

`Unmuted`(음소거 해제됨)는 모니터의 음소거가 해제될 때 기록됩니다. 음소거는 모든 구독자에게 적용되며, 음소거 기간이 끝나면 모니터는 자동으로 음소거 해제됩니다.

<a id="disabled"></a>
### `Disabled`

`Disabled`(비활성화됨)는 사용자가 모니터를 비활성화할 때, 또는 활동이 과도해서 모니터가 자동으로 비활성화될 때 기록됩니다. 비활성화는 모든 구독자에게 적용됩니다. 비활성화된 모니터는 평가되지 않습니다.

<a id="enabled"></a>
### `Enabled`

`Enabled`(활성화됨)는 모니터의 비활성화가 해제될 때 기록됩니다. 활성화는 모든 구독자에게 적용되며, 비활성화 기간이 끝나면 모니터는 다시 활성화됩니다.

**설명**: 음소거와 비활성화의 차이는 "평가를 하는가"입니다. 음소거된 모니터는 평가를 계속하므로 활동 기록은 쌓이지만 알림과 액션만 멈춥니다. 비활성화된 모니터는 평가 자체를 하지 않습니다.

> **중간 요약**: 활동 이벤트에는 조건 관련(`Monitor triggered`, `Monitor recovered`, `Evaluation failed`)과 관리 관련(`Condition edited`, 구독과 구독 해제, 음소거와 음소거 해제, 비활성화와 활성화) 항목이 있습니다. 음소거는 평가는 하되 부수 효과만 막고, 비활성화는 평가 자체를 멈추며, 둘 다 모든 구독자에게 적용됩니다.

## 정리

- 활동은 조건 결과와 일부 메타데이터 변경에 따라 기록되며, 전체 타임라인은 Overview 페이지에, 모니터별 타임라인은 History 탭에 표시됩니다.
- `Monitor triggered`는 임계값이 참이 되거나 이벤트가 감지될 때, `Monitor recovered`는 임계값이 거짓으로 돌아올 때만 기록됩니다.
- 구독하지 않은 기간의 활동은 기록되지 않으며, 평가나 알림, 액션이 실패하면 `Evaluation failed`가 남습니다.
- 음소거는 평가를 유지하고 부수 효과만 멈추며, 비활성화는 평가를 멈춥니다(과도한 활동 시 자동 비활성화도 가능).
