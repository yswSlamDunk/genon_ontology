# 온톨로지 정리 (Ontology cleanup)

- 원문: https://www.palantir.com/docs/foundry/ontology-manager/cleanup/
- 사이드바 위치: Applications > Ontology Manager > Ontology cleanup

이 페이지는 Ontology Manager의 Ontology cleanup 도구를 설명합니다. 온톨로지(Ontology)를 오래 운영하면 테스트용으로 만들었거나 더 이상 쓰지 않는 객체 타입이 쌓이는데, 이 도구는 그런 후보를 자동으로 찾아 주고 숨기기(Snooze), 사용 중단 예고(Deprecate), 삭제(Delete) 중 하나를 안전하게 선택하도록 돕습니다. 어떤 기준(플래그)으로 후보를 고르는지도 함께 다룹니다.

Ontology cleanup 도구는 객체 타입을 안전하게 삭제하는 방법이며, 다음과 같은 여러 이점을 제공합니다.

* 불필요한 객체 타입이 없어 탐색하기 쉬운 온톨로지
* 검색과 로드가 더 적은 수의 객체 타입을 대상으로 실행되므로 성능이 더 좋은 온톨로지
* 과도한 저장 비용 부담이 없는 온톨로지

이 도구는 온톨로지 편집자가 객체 타입을 삭제해도 안전한지 판단하도록 돕고, 객체 타입 사용자에게 향후 제거될 것임을 알리는 사용 중단(deprecation) 옵션을 제공합니다.

**설명**: 데이터베이스에서 테이블을 `DROP TABLE`로 바로 지우면 그 테이블을 읽던 다른 프로그램이 즉시 오류를 냅니다. 그래서 실무에서는 먼저 "이 테이블은 언제부터 쓰지 않습니다"라고 공지하고 유예 기간을 둔 뒤 삭제합니다. 여기서 말하는 사용 중단(deprecation)이 그 공지 단계에 해당합니다.

<a id="access-ontology-cleanup-tool"></a>
## Ontology cleanup 도구에 접근하기 (Access Ontology cleanup tool)

이 화면은 Ontology cleanup 도구의 홈 페이지에서 접근할 수 있습니다.

![홈 페이지에서 도구에 접근하기](https://www.palantir.com/docs/resources/foundry/ontology-manager/cleanup-navigation-from-homepage.png)

**Start cleanup**(정리 시작)을 선택하면, 온톨로지의 크기에 따라 도구가 정리 후보를 찾는 데 시간이 걸릴 수 있습니다.

![Start cleanup 버튼](https://www.palantir.com/docs/resources/foundry/ontology-manager/cleanup-start-cleanup-button.png)

결과로 나오는 객체 타입 목록은 홈 페이지에서 접근하는, 목록을 보여 주는 다른 페이지들과 비슷하게 동작합니다. 목록을 특정 플래그나 본인이 담당하는 객체 타입 그룹으로 필터링할 수 있습니다. 표에 표시할 열도 사용자 지정할 수 있습니다.

![정리 필터](https://www.palantir.com/docs/resources/foundry/ontology-manager/cleanup-filters.png)

기본적으로 표는 객체 타입이 걸린 플래그 중 가장 높은 우선순위를 기준으로 정렬됩니다.

**설명**: 플래그(flag)는 "이 객체 타입은 정리 대상일 수 있다"는 근거가 되는 검사 항목입니다. 예를 들어 어떤 객체 타입이 "설명 없음"과 "휴지통에 들어간 데이터소스" 두 플래그에 걸렸다면, 둘 중 우선순위가 더 높은 플래그를 기준으로 표에서의 순서가 정해집니다.

> **중간 요약**: 홈 페이지에서 **Start cleanup**을 누르면 도구가 정리 후보 객체 타입 목록을 만들고, 이 목록은 플래그와 객체 타입 그룹으로 필터링할 수 있으며 기본적으로 가장 높은 플래그 우선순위 순으로 정렬됩니다.

<a id="cleaning-up-your-ontology"></a>
## 온톨로지 정리하기 (Cleaning up your Ontology)

다음은 개발되던 중 출시되지 않은 워크플로인 "Planning" 워크플로로 필터링한 예입니다.

![정리 필터 예시](https://www.palantir.com/docs/resources/foundry/ontology-manager/cleanup-filter-example.png)

행 안의 체크박스를 사용해 세 개의 객체 타입을 선택합니다.

이 객체 타입들을 관리하는 옵션은 세 가지입니다.

* **Snooze(일시 숨김):** 설정 가능한 기간 동안 정리 대기열에서 객체 타입을 숨깁니다. Snooze는 그것을 수행한 사용자에게만 영향을 주는 동작입니다.
* **Deprecate(사용 중단):** 객체 타입 상태를 표시하는 모든 곳에서 객체 타입을 사용 중단(deprecated)으로 표시합니다. 이 옵션은 사용자에게 다른 객체 타입으로 옮기라고 알리거나, 해당 객체 타입이 아직 유용하다고 표시할 기회를 줍니다. 사용 중단과 함께 기한을 설정하면 사용자가 이 객체 타입 사용을 언제까지 멈춰야 하는지 알 수 있습니다.
* **Delete(삭제):** 온톨로지에서 객체 타입을 삭제하고 객체 저장소(object storage)에서 관련 데이터를 제거합니다.

대기열의 객체 타입에 대해 조치를 하면 그 객체 타입은 대기열에서 사라집니다. 이미 선택한 모든 조치를 보려면 표 필터를 사용합니다.

사용 중단과 삭제는 일반적인 온톨로지 수정과 같은 방식으로 스테이징(staging)됩니다. 위 예에서 "Work Item" 객체 타입에는 사용자 편집(edit)이 있는 객체가 있으므로 사용 중단 처리하고, 나머지 두 개는 삭제할 수 있습니다. 오른쪽 위의 **Save**를 선택하면 변경 사항을 온톨로지에 바로 저장하거나, 다른 사용자에게 검토를 요청하는 제안(proposal)을 만들 수 있습니다.

![정리 스테이징 예시](https://www.palantir.com/docs/resources/foundry/ontology-manager/cleanup-staging-example.png)

**설명**: 스테이징은 변경을 바로 반영하지 않고 "반영 예정" 상태로 모아 두는 것입니다. Git에서 `git add`로 변경을 모은 뒤 `git commit`으로 한 번에 기록하는 흐름과 대응합니다. 여기서는 Snooze, Deprecate, Delete로 고른 조치가 쌓여 있다가 **Save**를 눌러야 실제 온톨로지에 반영됩니다. "Work Item"을 삭제하지 않고 사용 중단만 하는 이유는, 사용자가 액션 등으로 직접 수정한 데이터(편집)는 백킹 데이터소스(backing datasource)에 없는 정보라서 삭제하면 되살릴 수 없기 때문입니다.

> **중간 요약**: 후보 객체 타입을 골라 Snooze(나만 숨김), Deprecate(사용 중단 공지, 기한 설정 가능), Delete(정의와 저장 데이터 삭제) 중 하나를 고릅니다. 사용 중단과 삭제는 스테이징되었다가 **Save**에서 직접 저장하거나 제안으로 검토를 요청합니다.

<a id="configure-ontology-cleanup"></a>
## Ontology cleanup 구성하기 (Configure Ontology cleanup)

정리 페이지에는 사용할 플래그와 각 플래그의 우선순위를 사용자 지정할 수 있는 하위 페이지가 있습니다.

![정리 구성 화면으로 이동](https://www.palantir.com/docs/resources/foundry/ontology-manager/cleanup-configuration-navigation.png)

이 페이지에서 플래그 설정을 구성할 수 있으며, 기본 플래그 세트를 쓸지 사용자 지정 플래그를 쓸지 선택할 수 있습니다.

![정리 구성 화면](https://www.palantir.com/docs/resources/foundry/ontology-manager/cleanup-configuration-view.png)

대기열에서 객체 타입을 Snooze하는 것과 마찬가지로, 이 설정은 개인별 사용자 지정이며 다른 온톨로지 편집자에게 영향을 주지 않습니다.

변경 사항을 저장하고 메인 **Cleanup** 탭으로 돌아가면 정리 대기열을 다시 계산하라는 안내가 나타납니다.

사용자 지정 플래그 구성을 사용하는 경우, 향후 추가되는 새 플래그는 기본 플래그 세트에서 켜져 있더라도 자동으로 켜지지 않습니다.

> **중간 요약**: 플래그 종류와 우선순위는 하위 구성 페이지에서 개인별로 바꿀 수 있고, 저장 후에는 대기열을 다시 계산합니다. 사용자 지정 구성을 쓰면 새로 추가되는 플래그는 직접 켜야 합니다.

<a id="ontology-cleanup-flags"></a>
## Ontology cleanup 플래그 (Ontology cleanup flags)

다음 플래그 목록은 흔한 문제를 찾는 데 목적이 있으며, 모든 경우를 망라하지는 않습니다.

* **Past deprecation date(사용 중단 날짜 경과):** 객체 타입이 현재 `deprecated` 상태이고 사용 중단 날짜 필드가 과거입니다.
* **Trashed datasource(휴지통에 들어간 데이터소스):** 이 객체 타입을 백킹하는 데이터소스(데이터셋, restricted view 등 종류와 관계없이) 중 하나가 Compass에서 휴지통으로 이동되었습니다.
* **Datasource not updated in \[x] days([x]일 동안 갱신되지 않은 데이터소스):** 백킹 데이터소스의 마지막 수정 시각을 Compass에서 확인합니다.
* **Description missing(설명 없음):** 객체 타입의 설명이 비어 있습니다. 객체 타입의 모든 속성(property)에 대한 설명까지 검사하지는 않습니다.
* **Display name regex matches string(표시 이름이 정규식과 일치):** 기본값인 `\[test|deprecated\]`는 표시 이름에 `[test]`나 `[deprecated]`가 들어 있는 객체 타입과 일치합니다. 예를 들어 조직에서 사용자 인수 테스트(UAT) 중인 객체 타입에 `UAT -`나 `Testing -` 접두어를 붙이는 관행이 있다면, 정규식 `UAT -|Testing -`를 사용해 이 패턴에 맞는 모든 객체 타입을 찾을 수 있습니다. ECMA(JavaScript) 정규식 문법을 지원합니다.
* **Phonograph deindexed(Phonograph 인덱스 해제됨):** Object Storage v1의 객체 타입에만 적용되는 플래그입니다. Object Storage v2에는 이에 해당하는 검사가 없습니다.

**설명**: 정규식(regular expression)은 문자열 패턴을 표현하는 문법입니다. `|`는 "또는"을 뜻하므로 `UAT -|Testing -`는 "UAT -" 또는 "Testing -"가 들어 있는 이름과 일치합니다. 예를 들어 표시 이름이 `UAT - Order`, `Testing - Invoice`, `Customer`인 객체 타입 세 개가 있으면 앞의 두 개만 이 플래그에 걸립니다. Compass는 Foundry에서 파일과 리소스를 관리하는 파일 시스템 계층이고, Phonograph는 Object Storage v1에서 쓰이던 인덱싱(indexing) 저장소입니다.

> **중간 요약**: 기본 플래그는 사용 중단 기한 경과, 데이터소스 휴지통 이동, 오랫동안 갱신 없음, 설명 없음, 표시 이름 정규식 일치, (OSv1 한정) 인덱스 해제를 검사합니다.

## 정리

- Ontology cleanup 도구는 쓰이지 않는 객체 타입을 찾아 안전하게 정리하도록 돕는 Ontology Manager의 기능입니다.
- 후보는 플래그(검사 항목)로 찾고, 가장 높은 플래그 우선순위 순으로 정렬됩니다.
- 조치는 Snooze(개인 숨김), Deprecate(사용 중단 공지와 기한), Delete(정의와 데이터 삭제) 세 가지입니다.
- 사용 중단과 삭제는 스테이징되었다가 **Save**로 직접 저장하거나 제안으로 검토받습니다.
- 사용자 편집이 있는 객체 타입은 삭제보다 사용 중단이 적절할 수 있습니다.
