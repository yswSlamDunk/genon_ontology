# 액션 타입 브랜치 작업 (Branching action types)

- 원문: https://www.palantir.com/docs/foundry/action-types/branching-action-types/
- 사이드바 위치: Define Ontologies > Action types > Branching action types

이 페이지는 Global Branching 기능을 이용해 운영 환경(`main`)에 영향을 주지 않고 브랜치에서 액션 타입을 시험하는 방법을 설명합니다. 브랜치에서 액션을 실행하기 위한 전제 조건, 함수 기반 액션의 동작, 그리고 웹훅, 외부 호출 함수, 알림 같은 부수 효과가 브랜치에서 기본적으로 어떻게 막히고 어떻게 허용할 수 있는지를 다룹니다.

온톨로지 액션은 Global Branching과 통합되어 있어, 운영(production) 환경에 영향을 주지 않고 브랜치에서 액션 타입을 시험할 수 있습니다. 변경 사항을 `main`에 병합하기 전에, 격리된 브랜치 맥락에서 액션을 실행하고, 설정을 검증하고, 편집을 관찰할 수 있습니다. 브랜치에서 생긴 편집은 병합되지 않습니다.

Global Branching의 일반적인 개념과 워크플로는 [Global Branching 문서](https://www.palantir.com/docs/foundry/global-branching/overview/)를 참고하세요.

**설명**: 브랜치(branch)는 Git의 브랜치와 같은 개념입니다. `main`은 실제 사용자가 쓰는 운영 버전이고, 브랜치는 그 사본 위에서 변경을 시험하는 공간입니다. 여기서 주의할 점은 "액션 타입의 정의 변경"은 브랜치에서 `main`으로 병합되지만, "브랜치에서 액션을 실행해서 생긴 객체 데이터 편집"은 병합되지 않는다는 것입니다. 즉 브랜치에서의 실행은 순수하게 시험용입니다.

<a id="running-actions-on-a-branch"></a>
## 브랜치에서 액션 실행하기 (Running actions on a branch)

브랜치의 Workshop 모듈에서 액션을 시험해 올바르게 설정되었는지 검증할 수 있습니다. 관련된 모든 객체 타입이 브랜치에서 인덱싱되어 있으면, 액션 타입을 실행하고 그 결과 생긴 편집을 브랜치에서 볼 수 있습니다.

<a id="prerequisites"></a>
### 전제 조건 (Prerequisites)

브랜치에서 액션을 실행하려면, 액션 타입이 편집하는 모든 객체 타입이 그 브랜치에서 인덱싱되어 있어야 합니다. 객체 타입은 Ontology Manager에서 개별 객체 타입 페이지나 액션 타입 페이지를 통해 인덱싱할 수 있습니다.

Ontology Manager에서 액션 타입을 편집할 때, 액션 타입이 브랜치에서 인덱싱되지 않은 객체 타입을 수정하면 경고가 나타납니다.

![액션 타입이 브랜치에서 인덱싱되지 않은 객체 타입을 수정한다는 Ontology Manager의 경고.](https://www.palantir.com/docs/resources/foundry/action-types/action-indexing-banner.png)

이 객체 타입들이 인덱싱되기 전에 액션을 실행하면 액션은 편집을 적용하지 않습니다. 토스트 알림이 나타나 액션 자체는 유효하지만 액션이 편집하는 객체 타입 중 하나 이상이 브랜치에서 읽기 전용이라는 점을 알려 줍니다. 알림에는 Ontology Manager로 가는 링크가 있어, 액션을 다시 실행하기 전에 나머지 객체 타입을 인덱싱할 수 있습니다.

**주의**: 브랜치에서 액션을 실행하는 것은 시험용 메커니즘입니다. 브랜치에서의 액션 편집은 `main`으로 다시 병합되지 않습니다.

**설명**: 인덱싱(indexing)은 백킹 데이터셋의 데이터를 객체 저장소에 적재해 검색하고 편집할 수 있는 상태로 만드는 작업입니다. 브랜치에서는 객체 타입마다 브랜치용 인덱스가 따로 있어야 그 브랜치에서 편집을 받을 수 있으므로, 인덱싱되지 않은 객체 타입은 브랜치에서 읽기 전용으로 취급됩니다.

<a id="working-with-function-backed-actions-on-a-branch"></a>
### 브랜치에서 함수 기반 액션 다루기 (Working with function-backed actions on a branch)

브랜치에서 함수 기반 액션은 브랜치 인식(branch-aware) 여부에 따라 다르게 동작합니다. 브랜치 인식 함수는 브랜치에서 수정할 수 있고 브랜치의 스키마를 읽는 반면, 브랜치를 인식하지 않는 함수는 `main`의 스키마만 읽습니다. 브랜치 인식 여부와 관계없이, 모든 함수 기반 액션은 브랜치에서만 실행되며 변경 사항을 `main`에 쓰지 않습니다. 지원되는 함수 유형은 [Global Branching 문서](https://www.palantir.com/docs/foundry/global-branching/integrations/)를 참고하세요.

**설명**: 예를 들어 브랜치에서 `Employee` 객체 타입에 `level` 속성을 새로 추가했다고 합시다. 브랜치 인식 함수는 브랜치의 스키마를 읽으므로 `level`을 볼 수 있지만, 브랜치를 인식하지 않는 함수는 `main`의 스키마만 알기 때문에 `level`을 모릅니다. 어느 쪽이든 실행 결과로 생긴 편집은 브랜치에만 남습니다.

> **중간 요약**: 브랜치에서 액션을 실행하려면 액션이 편집하는 모든 객체 타입을 그 브랜치에서 인덱싱해야 합니다. 함수 기반 액션은 브랜치 인식 여부에 따라 읽는 스키마가 다르지만, 편집은 항상 브랜치에만 남고 `main`으로 병합되지 않습니다.

<a id="managing-side-effects-on-branches"></a>
## 브랜치에서 부수 효과 관리하기 (Managing side effects on branches)

**참고**: 다음 내용은 브랜치에서 **액션을 통해** 적용되는 웹훅, 외부 호출이 있는 함수, 알림에만 해당합니다. 다른 방식으로 적용되는 부수 효과는 해당 소비자(consumer)가 정의한 대로 동작합니다.

<a id="webhooks"></a>
### 웹훅 (Webhooks)

기본적으로 브랜치에서 액션이 적용될 때 웹훅은 실행되지 않습니다. 이는 시험 환경에서 실수로 외부 시스템에 쓰는 일을 막기 위한 동작입니다.

이 경우 이 동작을 알려 주는 토스트 알림이 표시됩니다.

![액션은 적용되었지만 웹훅은 실행되지 않았음을 알리는 토스트 알림.](https://www.palantir.com/docs/resources/foundry/action-types/action-webhook-toast.png)

그러나 READ 엔드포인트를 호출하는 경우처럼, 브랜치에서 웹훅을 시험하는 것이 바람직한 경우도 있습니다.

기본 동작을 바꾸려면, Ontology Manager에서 액션 타입의 **Security and submission criteria** 탭을 설정해 브랜치에서 웹훅 실행을 활성화합니다.

![브랜치에서 웹훅 활성화 설정.](https://www.palantir.com/docs/resources/foundry/action-types/action-webhook-setting.png)

**주의**: 브랜치에서 웹훅을 활성화하면, 웹훅은 `main`에서와 똑같이 실행됩니다. 따라서 웹훅이 외부 운영 환경을 호출하도록 설정되어 있다면, 액션을 브랜치에서 실행하더라도 계속 운영 환경을 호출합니다.

**설명**: READ 엔드포인트는 데이터를 조회만 하고 바꾸지 않는 API(HTTP의 GET 요청 등)를 말합니다. 이런 호출은 몇 번을 보내도 외부 시스템 상태가 바뀌지 않으므로 브랜치에서 시험해도 안전합니다. 반대로 주문 생성 같은 쓰기 API를 호출하는 웹훅을 브랜치에서 켜면, 시험 중에도 실제 주문이 생깁니다.

<a id="functions-with-external-calls"></a>
### 외부 호출이 있는 함수 (Functions with external calls)

기본적으로 브랜치에서 액션이 적용될 때 외부 호출이 있는 함수 기반 액션 로직은 실행되지 않으며, 액션 전체가 실패합니다. 이는 시험 환경에서 실수로 외부 시스템에 쓰는 일을 막기 위한 동작입니다.

이 경우 실패를 알리는 토스트 알림이 이 동작에 대한 설명과 함께 표시됩니다.

<img src="https://www.palantir.com/docs/resources/foundry/action-types/action-function-error-toast.png" alt="외부 함수 호출로 액션이 차단됨." width="400">

그러나 READ 엔드포인트를 호출하는 경우처럼 브랜치에서 시험하는 것이 필요할 때도 있습니다. Ontology Manager에서 액션 타입의 **Security and submission criteria** 탭에서 브랜치에서 외부 호출이 있는 함수를 활성화하면 이 제한을 바꿀 수 있습니다.

![브랜치에서 외부 호출이 있는 함수 활성화 설정.](https://www.palantir.com/docs/resources/foundry/action-types/action-function-setting.png)

**주의**: 브랜치에서 외부 호출이 있는 함수를 활성화하면, 함수는 `main`에서와 똑같은 외부 호출을 합니다. 따라서 함수가 외부 운영 환경을 호출하도록 설정되어 있다면, 액션을 브랜치에서 실행하더라도 계속 운영 환경을 호출합니다.

<a id="notifications"></a>
### 알림 (Notifications)

기본적으로 브랜치에서 액션이 적용될 때 알림은 실행되지 않습니다. 이는 시험 환경에서 실수로 수신자에게 알림을 보내는 일을 막기 위한 동작입니다.

이 경우 이 동작을 알려 주는 토스트 알림이 표시됩니다.

![액션은 적용되었지만 알림은 실행되지 않았음을 알리는 토스트 알림.](https://www.palantir.com/docs/resources/foundry/action-types/action-notification-toast.png)

그러나 브랜치에서 알림을 시험하는 것이 바람직한 경우도 있습니다.

기본 동작을 바꾸려면, Ontology Manager에서 액션 타입의 **Security and submission criteria** 탭에서 브랜치에서 알림을 활성화할 수 있습니다.

또한 액션이 브랜치에서 실행될 때의 알림 수신자를 지정할 수 있습니다.

* **Branch owner:** 모든 알림을 브랜치 소유자에게 보냅니다.
* **Default recipients:** 원래 알림에 설정된 수신자에게 알립니다.

![브랜치에서 알림 활성화 설정.](https://www.palantir.com/docs/resources/foundry/action-types/action-notification-setting.png)

> **중간 요약**: 브랜치에서 웹훅과 알림은 기본적으로 실행되지 않고, 외부 호출이 있는 함수 기반 액션은 기본적으로 실패합니다. 각각 Security and submission criteria 탭에서 허용할 수 있지만, 허용하면 운영 환경과 똑같이 외부를 호출하므로 주의해야 합니다.

<a id="known-limitations"></a>
## 알려진 제한 사항 (Known limitations)

* 브랜치에서의 액션 편집은 시험용이며 `main`으로 다시 병합되지 않습니다.
* 브랜치에서 액션을 실행하면 웹훅과 이메일 알림이 기본적으로 실행되지 않습니다.
* 외부 시스템을 호출하는 함수는 브랜치에서 액션을 실행할 때 기본적으로 실패합니다.

## 정리

- Global Branching으로 `main`에 영향 없이 브랜치에서 액션 타입을 시험할 수 있지만, 브랜치에서 생긴 편집은 병합되지 않습니다.
- 브랜치에서 실행하려면 액션이 편집하는 모든 객체 타입이 그 브랜치에서 인덱싱되어 있어야 합니다.
- 함수 기반 액션은 브랜치 인식 여부에 따라 브랜치 또는 `main`의 스키마를 읽지만, 편집은 브랜치에만 씁니다.
- 웹훅과 알림은 기본적으로 건너뛰고, 외부 호출 함수는 기본적으로 실패하며, Security and submission criteria 탭에서 각각 허용할 수 있습니다.
