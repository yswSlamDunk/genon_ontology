# 사용자 편집 이력 활성화 (Enable user edit history)

- 원문: https://www.palantir.com/docs/foundry/object-edits/user-edit-history/
- 사이드바 위치: Ontology architecture > Object edits and materializations > Enable user edit history

이 페이지는 Object Storage v2에 인덱싱된 객체에 대해, 사용자가 언제 무엇을 바꿨는지 기록하는 편집 이력(edit history) 기능을 켜고 끄는 방법과 주의 사항을 설명합니다. 객체는 기본적으로 현재 상태만 보여 주므로, 과거 변경 내역을 감사하거나 화면에 보여 주려면 이 기능을 켜야 합니다.

이 기능은 Object Storage v2에 인덱싱된 객체에 대한 사용자 편집(edit)의 이력을 추적합니다. 아래 스크린샷처럼 Ontology Manager의 **Datasources** 탭에 있는 **Track user edit history** 토글로 이 기능을 켜거나 끌 수 있습니다.

![Track user edit history 토글](https://www.palantir.com/docs/resources/foundry/object-edits/track-user-edits-history.png)

사용자 편집을 허용하려면 [Edits 토글](02_how-edits-applied.md)이 켜져 있어야 합니다.

**팁**: 편집 이력은 편집이 어떤 방식으로 이루어졌는지와 관계없이 객체에 대한 모든 편집을 기록합니다. 편집 자체가 아니라 편집 뒤에 있는 결정(사용자가 제출한 파라미터 값과 제출 당시의 맥락 포함)을 기록하려면, 액션 타입에서 [액션 로그(action log)](../../02_define-ontologies/03_action-types/26_action-log.md)를 켜세요.

**설명**: 편집 이력은 "객체 X의 속성 status가 Open에서 Closed로 바뀌었다"처럼 결과로서의 값 변화를 객체 단위로 남깁니다. 액션 로그는 "사용자 U가 Close ticket 액션을 파라미터 reason=duplicate로 제출했다"처럼 액션 실행 단위의 기록을 남깁니다. 데이터베이스로 치면 전자는 행 변경 이력 테이블, 후자는 요청 감사 로그 테이블에 해당합니다.

<a id="edit-history-timestamps"></a>
## 편집 이력 타임스탬프 (Edit history timestamps)

편집 이력은 액션이 Object Storage v2에 편집을 제출하려고 준비할 때 캡처하는 UTC 커밋 타임스탬프를 사용합니다. 액션 타입에 [액션 로그](../../02_define-ontologies/03_action-types/26_action-log.md#action-log-timestamps)가 있으면, 같은 액션에 대한 액션 로그 항목과 편집 이력 항목은 같은 타임스탬프를 사용합니다. 이 타임스탬프는 편집이 쿼리에서 보이기 시작하는 정확한 시각을 나타내지는 않습니다.

[액션 규칙](../../02_define-ontologies/03_action-types/06_rules.md#values-and-parameters)에서 **Current User/Time**이 제공하는 타임스탬프는 액션 실행이 시작된 시각을 나타내며 실행 내내 고정됩니다. 따라서 이 규칙으로 설정한 타임스탬프 속성은 편집 이력 타임스탬프보다 더 이른 값을 가질 수 있습니다.

**설명**: 예를 들어 액션이 10:00:00.000에 시작해 검증과 함수 실행을 거쳐 10:00:01.500에 편집을 제출한다면, **Current User/Time**으로 채운 `updated_at` 속성은 10:00:00.000이고 편집 이력에는 10:00:01.500 무렵의 커밋 타임스탬프가 남습니다. 두 값이 다르다고 해서 오류는 아닙니다.

> **중간 요약**: 편집 이력은 OSv2 객체의 모든 편집을 UTC 커밋 타임스탬프와 함께 기록하며, 이 시각은 액션 로그와 같고 **Current User/Time** 값보다 늦을 수 있습니다.

<a id="common-issues-and-notes"></a>
## 자주 생기는 문제와 참고 사항 (Common issues and notes)

* 편집 이력은 **Track user edit history**를 켠 이후 객체에 일어난 변경을 반영합니다. 이 기능을 켜기 전의 변경은 추적되지 않습니다.
* **Track user edit history**를 켜면 초기화하는 데 몇 분이 걸립니다. 이 짧은 시간 동안 사용자는 해당 객체에 액션을 수행할 수 없습니다.
* Object Storage v1에서 Object Storage v2로 마이그레이션하는 경우, 편집 이력을 유지하려면 마이그레이션 중에 `preserve edit history`가 체크되어 있는지 확인하세요.
* 객체의 현재 상태(같은 기본 키(primary key)를 가진 객체)에 접근할 수 있는 사용자는 그 객체의 전체 이력에 접근할 수 있습니다. 즉, 객체가 삭제되었다가 다시 생성되어도, 사용자는 삭제 액션 이전에 일어난 이력을 여전히 볼 수 있습니다.

**Track user edit history**를 켠 뒤에는 [Edit History 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-edits-history/)을 Workshop 모듈이나 Workshop 기반 Object View에 추가해 편집 이력을 표시할 수 있습니다.

**설명**: 마지막 항목은 이력이 기본 키 값에 묶여 있다는 뜻입니다. 기본 키 `T-1`인 객체를 삭제하고 같은 키로 다시 만들면, 새 `T-1`을 볼 수 있는 사용자는 삭제 전 `T-1`의 이력까지 볼 수 있습니다. 권한 설계 시 이 점을 고려해야 합니다.

<a id="disable-edit-history"></a>
## 편집 이력 비활성화 (Disable edit history)

**Track user edit history**를 끄면 이 객체 타입의 기존 편집 이력이 모두 영구 삭제됩니다. 온톨로지를 저장하기 전에 사용자는 경고를 받으며, 편집 이력이 삭제된다는 사실을 확인하는 동의를 해야 합니다.

![사용자 편집 이력 비활성화 토글](https://www.palantir.com/docs/resources/foundry/object-edits/disable-edits-history.png)

## 정리

- **Track user edit history** 토글은 OSv2 객체의 사용자 편집 이력 기록을 켜며, **Edits** 토글이 먼저 켜져 있어야 합니다.
- 기록은 켠 시점 이후부터만 남고, 켤 때 몇 분간 액션이 막힙니다.
- 이력 타임스탬프는 편집 제출 직전의 UTC 커밋 시각이며, 액션 결정 내용까지 남기려면 액션 로그를 함께 씁니다.
- 이력은 기본 키에 묶여 삭제 후 재생성된 객체에서도 보이며, 기능을 끄면 기존 이력이 영구 삭제됩니다.
