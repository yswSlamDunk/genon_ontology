# 결과 필터링하기 (Filter results)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/filter-results/
- 사이드바 위치: Applications > Object Explorer > Analyze and compare > Filter results

이 페이지는 Object Explorer에서 검색을 시작한 뒤 나타나는 탐색(exploration) 화면에서 객체 집합(object set)을 좁혀 나가는 방법을 설명합니다. 속성(property) 값으로 거르는 방법, 키워드 검색과 수정자(modifier), AND/OR 논리 연산자 조합, 그리고 링크로 연결된 다른 객체를 기준으로 거르는 방법을 다룹니다.

[검색](../03_search-and-explore-objects/01_search-objects.md)을 시작하면 추가 필터링을 할 수 있는 탐색 화면으로 이동합니다.

<a id="search-bar"></a>
## 검색 창 (Search bar)

검색 창은 현재 객체 집합을 필터링하는 중심 지점입니다. 검색 창을 클릭하면 검색 메뉴가 펼쳐집니다. 여기서 몇 가지 필터링 옵션을 사용할 수 있습니다.

![검색](https://www.palantir.com/docs/resources/foundry/object-explorer/explore_search.png)

<a id="filtering-by-properties-of-the-main-object-type"></a>
### (기본 객체 타입의) 속성으로 필터링하기 (Filtering by properties (of the main object type))

**어떤 속성으로 필터링할지 알고 있는 경우**

예: "직원들의 언어(language)로 필터링하고 싶습니다."

검색 메뉴에서 모든 속성 목록 **(B)**(설명은 선택 사항)을 알파벳순으로 볼 수 있습니다.

![검색](https://www.palantir.com/docs/resources/foundry/object-explorer/explore_search_filtered.png)

검색 창 **(A)에** 입력해 특정 속성 타입을 검색합니다. 원하는 속성을 선택하면 팝오버가 나타나 그 속성에서 필터링할 값을 고를 수 있습니다. 입력 방식은 속성의 타입(숫자, 텍스트, 날짜 등)에 따라 다릅니다. 텍스트 속성(예: language)에서는 필(pill) 안에 입력해 선택지를 걸러 낼 수 있습니다.

**값은 알지만 어느 속성에 속하는지 모르는 경우**

예: "로스앤젤레스로 가는 항공편으로 필터링하고 싶습니다."

검색 창에 값(예: "Los Angeles")을 입력합니다. 그 값이 현재 객체 집합에 존재하면, 검색 메뉴 오른쪽에 "Destination City Name이 Los Angeles인 경우(where Destination City Name is Los Angeles)"로 필터링하는 옵션이 나타납니다.

**설명**: 속성 필터는 SQL의 `WHERE` 절에 해당합니다. "직원 언어로 필터링"은 `SELECT * FROM employee WHERE language IN ('Korean', 'English')`처럼 선택한 값 목록으로 거르는 것이고, 숫자나 날짜 속성은 `WHERE hire_date BETWEEN ...` 같은 범위 조건 입력 화면이 나옵니다. 필(pill)은 검색 창 안에 둥근 상자 모양으로 표시되는 필터 하나를 가리키는 UI 요소입니다.

> **중간 요약**: 검색 창은 필터링의 중심입니다. 속성을 알면 속성 목록에서 골라 값을 지정하고, 값만 알면 값을 입력해 그 값을 가진 속성 기준 필터를 추천받을 수 있습니다.

<a id="filtering-by-keywords"></a>
### 키워드로 필터링하기 (Filtering by keywords)

키워드 검색은 객체 타입의 모든 속성 또는 특정 속성에 대해 지원됩니다. 검색어를 포함하는 **아무** 속성에 대해 키워드 검색을 하려면 검색 창에 입력하고 Enter 키를 누르세요. 그 결과로 생긴 필터는 "Has keywords" 필터 필을 클릭해 수정할 수 있습니다.

특정 속성에 대해 키워드 검색을 하려면 텍스트 속성을 선택하고 질의를 입력한 뒤 Enter 키를 누르거나, 필터 차트에서 "Keyword" 탭으로 전환하세요.

![키워드](https://www.palantir.com/docs/resources/foundry/object-explorer/explore_keyword_property.png)

기본적으로 키워드 검색은 정확한 단어나 구문에 일치하며, 접두사나 접미사에는 일치하지 않습니다. 접두사 검색을 하려면 아래의 **"Starts with"** 수정자를 참고하세요.

**설명**: 키워드 검색은 텍스트를 단어 단위(토큰)로 나눠 색인해 두고, 검색어 토큰과 일치하는 단어가 있는지 확인하는 방식입니다. 그래서 "term"으로 검색하면 "term"이라는 단어가 있는 객체는 찾지만, "terminal"처럼 "term"으로 시작하는 다른 단어만 있는 객체는 기본적으로 찾지 않습니다. SQL의 `LIKE '%term%'`(부분 문자열 일치)과는 동작이 다릅니다.

<a id="adding-term-modifiers"></a>
#### 용어 수정자 추가하기 (Adding Term Modifiers)

주어진 검색어에 대해 질의를 수정하는 세 가지 옵션이 있습니다. 일관성을 위해 이 드롭다운에서 검색어를 직접 편집하기보다는 토글로 이 수정자들을 제어하세요.

* **"Is not":** 현재 검색어를 부정하여, 속성에 그 검색어가 포함되지 않은 객체만 찾습니다. `NOT term`을 입력하는 것과 같습니다.
* **"Starts with":** 와일드카드 검색을 수행하여, 속성이 현재 검색어로 시작하는 객체를 찾습니다. `term*`을 입력하는 것과 같으며, "term"과 "terminal" 같은 단어 모두에 일치합니다. 접미사 일치(앞쪽 와일드카드 검색, leading wildcard search)를 하려면 해당 속성에 **Enable leading wildcards** 렌더 힌트(render hint)가 활성화되어 있어야 합니다. 와일드카드 검색의 세부 사항과 제한(여러 단어로 된 와일드카드 질의가 일치하지 않는 이유 포함)은 [텍스트 검색 이해하기(Understanding text search)](../03_search-and-explore-objects/03_understanding-text-search.md#common-pitfalls)를 참고하세요.
* **"Exact":** 공백의 정확한 위치까지 포함해 검색어 전체를 검색합니다. "my search term"에 대해 Exact 검색을 하면 "my search term"이라는 구문만 찾고, "my search for a term" 같은 구문은 찾지 않습니다.

**설명**: 접두사 검색(`term*`)은 색인된 단어 목록이 정렬되어 있으면 이진 탐색처럼 시작 위치를 찾아 연속 구간만 읽으면 되므로 비교적 저렴합니다. 반면 접미사 검색(`*term`)은 모든 단어를 확인해야 하므로 비싸서, 속성별로 렌더 힌트를 켜야만 허용되는 것으로 이해할 수 있습니다.

<a id="adding-logical-operators-andor"></a>
#### 논리 연산자(AND/OR) 추가하기 (Adding Logical Operators (AND/OR))

"And" 또는 "Or"를 선택하면 해당 논리 연산자로 연결된 새 검색어가 기존 질의에 추가됩니다. 새 검색어를 추가한 뒤 검색어를 클릭해 편집하세요.

![새 검색어 추가](https://www.palantir.com/docs/resources/foundry/object-explorer/new_search_term.png)

검색어와 논리 연산자는 중첩하여 더 복잡한 질의를 만들 수 있습니다. 아래는 OR 안에 AND가 중첩된 예입니다. 편집 중이 아닐 때는 각 검색어의 수정자도 간략한 형태로 표시됩니다.

![중첩된 키워드](https://www.palantir.com/docs/resources/foundry/object-explorer/nested_search_terms.png)

"And"/"Or" 태그를 클릭하면 연산자가 뒤바뀝니다. 인접한 두 단계의 연산자가 같아지면 필터는 한 단계 중첩으로 단순화됩니다.

**설명**: 중첩은 괄호로 묶은 불리언 식입니다. 예를 들어 `(engine AND failure) OR overheating`은 "engine"과 "failure"가 모두 들어 있거나, "overheating"이 들어 있는 객체를 찾습니다. 여기서 OR를 AND로 바꾸면 `(engine AND failure) AND overheating`이 되는데, AND는 결합 법칙이 성립하므로 `engine AND failure AND overheating`과 같습니다. 원문의 "한 단계 중첩으로 단순화"가 이 처리를 말합니다.

> **중간 요약**: Enter로 모든 속성 또는 특정 텍스트 속성에 키워드 검색을 할 수 있고, 기본은 단어 단위 정확 일치입니다. "Is not", "Starts with", "Exact" 수정자로 부정, 접두사 검색, 구문 일치를 지정하고, And/Or로 검색어를 중첩 조합할 수 있습니다.

<a id="filtering-on-links"></a>
### 링크로 필터링하기 (Filtering on links)

현재 객체의 속성에 직접 필터를 적용할 수 있는 것과 같은 방식으로, 객체의 관계를 기준으로 객체를 필터링할 수 있습니다. 필터링할 관계를 고르려면 검색 메뉴의 왼쪽 패널에서 선택하세요.

특정 링크를 가진 객체를 검색하려면 "Has Link" 옵션을 선택하세요. 아래 그림에서는 "Has Flight Delay Event"로 강조 표시되어 있습니다. 이 필터는 해당 링크를 가진 객체를 보여 주거나, 해당 링크를 가지지 않은 객체를 보여 주는 데 사용할 수 있습니다.

예: "지연 이벤트가 연결된 항공편."

![지연이 있는 항공편](https://www.palantir.com/docs/resources/foundry/object-explorer/has_link.png)

링크된 객체가 특정 속성 값을 가진 객체를 검색하려면, 검색 메뉴 패널 왼쪽에서 관계를 선택하세요. 그다음 필터링할 속성 타입을 고릅니다.

예: "2018년에 제조된 항공기(Aircraft)로 운항한 항공편."

![항공편 속성 검색](https://www.palantir.com/docs/resources/foundry/object-explorer/linked_to_property.png)

다른 특정 객체로의 링크를 가진 객체를 검색할 수도 있습니다. 예를 들어 링크를 선택한 뒤 "Filter by Airline" 옵션을 고르세요. 그러면 특정 객체로의 링크에 대한 필터가 열립니다. 링크된 객체는 결과 리스토그램(listogram)에서 타이틀로 표시됩니다.

예: "특정 항공사가 운항한 항공편."

![항공사에 링크된 항공편](https://www.palantir.com/docs/resources/foundry/object-explorer/linked_to_object.png)

**설명**: 세 가지 링크 필터를 SQL로 옮기면 다음과 같습니다. "Has Link"는 `WHERE EXISTS (SELECT 1 FROM delay_event d WHERE d.flight_id = f.flight_id)`(링크가 없는 객체는 `NOT EXISTS`), 링크된 객체의 속성 필터는 `JOIN aircraft a ON f.aircraft_id = a.aircraft_id WHERE a.manufacture_year = 2018`, 특정 객체로의 링크 필터는 `WHERE f.airline_id IN ('KE', 'OZ')`에 해당합니다. 리스토그램(listogram)은 값마다 개수를 막대로 보여 주는 목록형 히스토그램 차트입니다.

> **중간 요약**: 링크 필터에는 세 가지가 있습니다. 링크 존재 여부("Has Link"), 링크된 객체의 속성 값, 그리고 링크된 특정 객체(리스토그램에서 타이틀로 선택)입니다.

## 정리

- 탐색 화면의 검색 창은 객체 집합을 필터링하는 중심이며, 속성 이름이나 값으로 필터를 만들 수 있습니다.
- 키워드 검색은 기본적으로 단어 단위 정확 일치이며, "Is not", "Starts with", "Exact" 수정자로 동작을 바꿉니다. 접미사 검색은 렌더 힌트가 필요합니다.
- And/Or 연산자로 검색어를 중첩 조합할 수 있고, 같은 연산자가 인접하면 자동으로 단순화됩니다.
- 링크 존재 여부, 링크된 객체의 속성, 링크된 특정 객체를 기준으로도 필터링할 수 있습니다.
