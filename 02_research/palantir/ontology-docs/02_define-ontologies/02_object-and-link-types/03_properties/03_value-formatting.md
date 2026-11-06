# 값 서식 추가 (Add value formatting)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/value-formatting/
- 사이드바 위치: Define Ontologies > Object and link types > Properties > Add value formatting

이 페이지는 속성(property)의 원시 값(raw value)을 사람이 읽기 쉬운 형태로 바꿔 보여 주는 값 서식(value formatting)을 설명합니다. 지원하는 서식의 종류(숫자, 날짜와 시간, Foundry ID, 리소스 RID, 아티팩트 GID), 서식을 추가하는 절차, 숫자와 날짜 서식의 세부 옵션을 다룹니다. 값 서식은 저장된 데이터를 바꾸지 않고 화면에 표시하는 방식만 바꾼다는 점이 핵심입니다.

**값 서식(value formatting)은** 속성 값에 특수한 서식 지정기(formatter)를 적용해 원시 값을 더 읽기 쉬운 형태로 변환하는 것을 말합니다. 아래 이미지에서 왼쪽(**Before**)은 서식이 없는 `weight` 열과 `value` 열을 보여 줍니다. 오른쪽(**After**)에서는 `weight` 열에 단위("kg")가 적용되었고, `value` 열은 통화 기호와 함께 더 간결한 형태("$100K")로 표시됩니다. 둘 다 숫자 서식(numeric formatting)의 예입니다. 온톨로지는 날짜와 시간 서식, 사용자 ID 서식, 리소스 RID 서식, 아티팩트 GID 서식도 지원합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/value-formatting-numeric-formatting-example.png" alt="값 서식 예시" width="600"/>

**설명**: 데이터셋에 `value` 열의 값이 `100000`으로 저장되어 있어도, 값 서식을 적용하면 화면에는 `$100K`로 보입니다. 저장된 값은 여전히 숫자 `100000`이므로 정렬, 필터, 합계 계산은 원래 숫자로 이루어집니다. 프로그래밍에서 `double` 값을 그대로 두고 출력할 때만 `printf("%.2f")` 같은 형식 문자열을 적용하는 것과 같은 구조입니다.

<a id="supported-value-formatting"></a>
## 지원하는 값 서식 (Supported value formatting)

|타입 |설명 |
|--- |--- |
| 숫자 서식(Numeric formatting) | 통화, 단위, 접두사를 붙이고, 여러 표기법(간결 표기, 과학적 표기)과 백분율을 적용합니다. 자세한 내용은 [숫자 서식 섹션](#numeric-formatting-options)을 참고하세요. |
| 날짜와 시간 서식(Date and time formatting) | 타임스탬프와 날짜를 특정 형식과 특정 시간대로 표시합니다. |
| Foundry ID 서식(Foundry ID formatting) | Foundry ID를 사용자의 이름과 성, 또는 그룹 이름으로 표시합니다. |
| 리소스 RID 서식(Resource RID formatting) | Foundry 리소스 ID(RID)를 아이콘과 리소스 이름으로 표시하고, 해당 리소스로 이동하는 클릭 가능한 링크를 붙입니다. |
| 아티팩트 GID 서식(Artifact GID formatting) | 아티팩트 전역 ID(GID)를 아이콘과 아티팩트 이름으로 표시하고, 해당 아티팩트로 이동하는 클릭 가능한 링크를 붙입니다. |

**설명**: RID(Resource Identifier)는 Foundry 안의 데이터셋, 파일 같은 리소스 하나하나에 붙는 고유 식별 문자열입니다. 데이터에는 `ri.foundry.main.dataset.1234...` 같은 긴 문자열이 저장되지만, 서식을 적용하면 사람이 알아볼 수 있는 리소스 이름과 링크로 보입니다. 외래 키 값만 저장된 열을 화면에 표시할 때 참조 테이블과 조인해 이름을 보여 주는 것과 같은 효과입니다.

> **중간 요약**: 값 서식은 저장 값은 그대로 두고 표시 방식만 바꾸며, 숫자, 날짜와 시간, Foundry ID, 리소스 RID, 아티팩트 GID 서식을 지원합니다.

<a id="add-value-formatting"></a>
## 값 서식 추가하기 (Add value formatting)

속성 편집기에서 다음을 수행합니다.

1. 값 서식을 추가하려는 속성을 선택합니다.
2. 속성 창(properties pane)의 오른쪽 패널에 속성의 기본 타입(base type)에 따라 서식 종류(값 서식, 숫자 서식, 날짜와 시간 서식 등)가 보입니다. 해당 서식을 켭니다(toggle on).

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/value-formatting-toggle.png" alt="값 서식 토글" width="500" />

3. 숫자 서식과 날짜와 시간 서식에는 아래에서 설명하는 추가 서식 옵션이 있습니다.
   * [숫자 서식 옵션](#numeric-formatting-options)
   * [날짜와 시간 서식 옵션](#date-and-time-formatting-options)
4. 사용 가능한 서식 옵션을 선택하면, 새 서식이 적용되었을 때 속성 값이 어떻게 표시될지 미리 보기가 나타납니다.

<a id="numeric-formatting-options"></a>
### 숫자 서식 옵션 (Numeric formatting options)

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/value-formatting-numeric-formatting.png" alt="숫자 서식 옵션" width="500"/>

| 이름 | 설명 | 사용법 |
| --- | --- | --- |
| **Numeric formatting** | 켜기/끄기 토글입니다. | 숫자 서식을 제거하거나 추가하려면 이 토글을 사용합니다. |
| **Base type** | 사용할 수 있는 여러 서식 유형(Currency(통화), Standard unit(표준 단위), Percentage(백분율), Prefix / suffix(접두사/접미사), Fixed values(고정 값))과 각 유형의 예시 및 설명이 들어 있습니다. | `Capacity in Pounds`에 연관된 단위가 있다면 이 드롭다운에서 **Standard unit**을 선택합니다. |
| **Use grouping** | 로캘(locale)에 맞는 쉼표 구분 기호를 추가합니다. | 이 옵션을 켜면 123456이 123,456으로 표시됩니다. |
| **Notation** | Compact(간결), Scientific(과학적), Engineer(공학) 표기법이 들어 있습니다. | 값을 123K처럼 근사해서 보여 주려면 Compact를 선택합니다. |
| **Maximum fraction digits** | 소수점 뒤에 표시할 최대 자릿수입니다. 소수 자릿수가 이보다 많은 값은 이 길이로 반올림됩니다. | `2`로 설정하면 `3.14159`가 `3.14`로 표시됩니다. |
| **Minimum fraction digits** | 소수점 뒤에 표시할 최소 자릿수입니다. 이보다 짧은 값은 뒤에 0을 채웁니다. | `2`로 설정하면 `3.5`가 `3.50`으로 표시됩니다. |
| **Maximum/Minimum significant digits** | 0이 아닌 첫 자리부터 세어 표시할 유효 숫자의 최대, 최소 개수입니다. | 최대 유효 숫자를 `3`으로 설정하면 `3.14159`가 `3.14`로 표시됩니다. |
| **Minimum integer digits** | 소수점 앞에 표시할 최소 자릿수이며, 부족하면 앞에 0을 채웁니다. | `2`로 설정하면 `5`가 `05`로 표시됩니다. |
| **Preview result** | 숫자 서식을 확인하고 시험해 봅니다. | 속성 값으로 예상되는 것과 비슷한 숫자를 입력하면 서식이 적용된 미리 보기를 볼 수 있습니다. |

**설명**: 유효 숫자(significant digits)는 값의 크기와 상관없이 0이 아닌 첫 자리부터 센 자릿수입니다. 예를 들어 최대 유효 숫자가 3이면 `3.14159`는 `3.14`, `123456`은 `123000`, `0.0012345`는 `0.00123`이 됩니다. 반면 소수 자릿수(fraction digits)는 소수점 뒤 자릿수만 셉니다.

> **중간 요약**: 속성 편집기에서 속성을 선택하고 서식을 켠 뒤 옵션을 고르면 미리 보기로 결과를 확인할 수 있습니다. 숫자 서식은 통화, 단위, 자릿수 구분, 표기법, 소수 자릿수, 유효 숫자, 정수 자릿수를 조절합니다.

<a id="date-and-time-formatting-options"></a>
### 날짜와 시간 서식 옵션 (Date and time formatting options)

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/value-formatting-date-formatting.png" alt="날짜와 시간 서식 옵션" width="500" />

|이름 |설명 |예시 |
|--- |--- |--- |
|**Date** |날짜만 표시(시간 없음) |`Wed, Jul 22, 2020` |
|**Date and time** |날짜와 시간을 긴 형식으로 표시 |`Wed, July 22, 2020, 1:00:00 PM` |
|**Date and time, short** |날짜와 시간을 짧은 형식으로 표시 |`Jul 22, 2020, 1:00 PM` |
|**ISO instant** |날짜와 시간을 ISO 8601 형식으로 표시 |`2020-07-22T13:00:00.000Z` |
|**Relative to now** |현재 시각을 기준으로 한 상대 날짜 |`8 minutes ago` |
|**Time** |시간만 표시(날짜 없음) |`1:00 pm` |

**Relative to now** 서식을 적용하면, 애플리케이션은 24시간 전까지만 상대적인 표현으로 표시합니다. 그보다 오래된 값은 요일을 포함한 **Date and time, short** 형식(`Wed, Jul 22, 2020, 1:00 PM`)으로 표시합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/value-formatting-relative-to-now.png" alt="Relative to now 예시" width="300" />

<a id="time-zones"></a>
#### 시간대 (Time zones)

타임스탬프에 서식을 적용할 때는 타임스탬프를 표시할 시간대를 지정할 수 있습니다. 직접 입력한 고정(static) 시간대를 쓰거나, 애플리케이션 사용자의 현재 시간대를 쓸 수 있습니다. 고정 시간대를 입력할 때는 UTC 오프셋이나 로캘 이름을 입력해 시간대를 검색할 수 있습니다.

**설명**: ISO 8601 예시 `2020-07-22T13:00:00.000Z`의 끝에 있는 `Z`는 UTC(협정 세계시)를 뜻합니다. 타임스탬프는 보통 하나의 절대 시점(UTC 기준)으로 저장되고, 표시할 때 시간대를 적용해 지역 시각으로 바꿉니다. 같은 값이 서울(UTC+9) 사용자에게는 2020년 7월 22일 오후 10시로 보일 수 있습니다. 고정 시간대를 지정하면 보는 사람과 관계없이 같은 시각으로 표시됩니다.

<a id="user-id-formatting"></a>
### 사용자 ID 서식 (User ID formatting)

Foundry/Multipass 사용자 ID 또는 그룹 ID인 문자열에 값 서식을 적용하고 **Username or group name**(사용자 이름 또는 그룹 이름) 옵션을 선택하면, ID 대신 사용자의 이름과 성 또는 그룹 이름이 표시됩니다. 이 서식 옵션은 보통 속성을 편집하면서 속성 필드 중 하나에 사용자 ID나 그룹 ID를 저장하는 [액션](../../03_action-types/01_overview.md)을 만들었을 때 사용합니다. 백킹 데이터에는 이 정보가 사용자의 Foundry 사용자 ID나 그룹 ID로 저장되며, 값 서식을 적용하면 ID 대신 사용자 이름이나 그룹 이름이 표시됩니다.

**설명**: Multipass는 Foundry에서 사용자와 그룹을 관리하는 인증 서비스의 이름입니다. 예를 들어 "담당자 지정" 액션이 `assignedTo` 속성에 `a1b2c3d4-...` 같은 사용자 ID를 저장한다면, 이 서식을 적용해 화면에 "Jane Kim"처럼 이름을 보여 줄 수 있습니다.

> **중간 요약**: 날짜와 시간 서식은 여섯 가지 형식과 시간대 지정을 지원하며, Relative to now는 24시간 이내 값에만 상대 표현을 씁니다. 사용자 ID 서식은 저장된 ID를 사람 이름이나 그룹 이름으로 보여 줍니다.

<a id="faq"></a>
## FAQ

<a id="will-this-work-with-existing-type-classes"></a>
### 기존 타입 클래스와 함께 작동하나요? (Will this work with existing type classes?)

UI에서는 값 서식이 기존 타입 클래스보다 우선합니다. 둘 다 설정되어 있으면 값 서식이 표시됩니다. 다만 한 속성에는 값 서식을, 다른 속성에는 타입 클래스를 사용할 수 있습니다.

<a id="will-this-work-with-editable-properties-in-object-views"></a>
### Object View의 편집 가능한 속성에서도 작동하나요? (Will this work with editable properties in Object Views?)

값 서식은 [인라인 편집(inline edits)](../../03_action-types/18_inline-edits.md#object-explorer-inline-edits)이 설정된 속성에서 지원됩니다. 레거시 `hubble:editable` 타입 클래스가 있는 속성에서는 값 서식이 비활성화됩니다.

> **중간 요약**: 값 서식은 타입 클래스보다 우선 표시되고, 인라인 편집 속성에서는 지원되지만 레거시 `hubble:editable` 타입 클래스가 있으면 비활성화됩니다.

## 정리

- 값 서식은 저장된 원시 값을 바꾸지 않고 애플리케이션에서 보이는 형태만 바꿉니다.
- 숫자, 날짜와 시간, Foundry ID(사용자/그룹), 리소스 RID, 아티팩트 GID 서식을 지원합니다.
- 속성 편집기에서 속성을 선택하고 서식을 켠 뒤 옵션을 고르면 미리 보기로 확인할 수 있습니다.
- 숫자 서식은 통화, 단위, 표기법, 자릿수를, 날짜와 시간 서식은 형식과 시간대를 조절합니다.
- 값 서식은 타입 클래스보다 우선하며, 레거시 `hubble:editable` 타입 클래스와는 함께 쓸 수 없습니다.
