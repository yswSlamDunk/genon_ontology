# 검색 문법 (Search syntax)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/search-syntax/
- 사이드바 위치: Applications > Object Explorer > Search and explore objects > Search syntax

이 페이지는 Object Explorer 전역 검색창에서 쓸 수 있는 검색 문법을 설명합니다. 따옴표로 정확한 구문 찾기, NOT/AND/OR 논리 연산자, 와일드카드, 퍼지 검색을 알면 단순 키워드 검색보다 훨씬 정확하게 원하는 객체를 찾을 수 있습니다.

Object Explorer는 모든 객체와 그 속성(property)을 대상으로 한 검색을 지원합니다. 필요한 것을 찾을 수 있도록, 이 페이지에서는 [전역 검색창](../02_getting-started.md#global-search-bar-a)의 검색 문법을 설명합니다.

<a id="quotation-marks"></a>
### 따옴표 (Quotation marks)

기본적으로 검색창에 입력한 단어들은 각각 독립적으로 검색됩니다. 예를 들어 `yellow cab`을 검색하면 속성 값이 `yellow` 또는 `cab` 중 하나와 일치하는 모든 객체가 반환됩니다.

따옴표를 사용하면 이 동작을 바꿀 수 있습니다. Object Explorer에서 `"yellow cab"`을 검색하면 하나 이상의 속성 값에 정확한 구문 `yellow cab`이 들어 있는 모든 객체가 반환됩니다. 이런 구문 검색은 보통 개별 단어 검색보다 결과가 적습니다.

<a id="logical-operators-notandor"></a>
### 논리 연산자 (not/and/or) (Logical operators (not/and/or))

**NOT**, **AND**, **OR** 연산자를 사용해 Object Explorer의 텍스트 검색을 강화할 수 있습니다.

<a id="join-operators"></a>
#### 결합 연산자 (Join operators)

**AND**와 **OR**를 결합 연산자로 사용하면 서로 다른 두 검색 조건을 합칠 수 있습니다. 구체적으로 **AND**는 두 조건을 모두 만족하는 항목을, **OR**는 적어도 하나의 조건을 만족하는 항목을 검색합니다. 예를 들어 Manhattan과 Brooklyn이 모두 관련된 택시 운행을 찾으려면 `Manhattan AND Brooklyn`을 검색합니다. 마찬가지로 Manhattan이나 Brooklyn 중 하나가 관련된 택시 운행을 찾으려면 `Manhattan OR Brooklyn`을 검색합니다.

<a id="negation-operators"></a>
#### 부정 연산자 (Negation operators)

여러 조건에 한꺼번에 적용되는 결합 연산자(`dogs AND cats`나 `vanilla OR chocolate` 등)와 달리, **NOT** 연산자는 하나의 조건에 적용되어 그 조건을 만족하지 *않는* 요소를 검색합니다.

예를 들어 `NOT Brooklyn`을 검색하면 Object Explorer는 Brooklyn을 언급하는 것을 *제외한* 모든 결과를 반환합니다. **NOT** 연산자는 합쳐진 조건에도 적용할 수 있습니다. 예컨대 `NOT (Manhattan OR Brooklyn)`을 검색하면 Brooklyn이나 Manhattan을 언급하는 것을 *제외한* 모든 검색 결과가 반환됩니다.

<a id="combining-operators"></a>
#### 연산자 조합 (Combining operators)

따옴표로 만든 구문도 검색에 함께 넣을 수 있습니다. 예를 들어 `"yellow cab" AND Manhattan`은 유효한 식입니다.

논리 연산자는 괄호를 사용해 더 복잡한 식으로 구성할 수도 있습니다. 예를 들어 다음 검색은 Manhattan을 언급하지 않으면서 yellow cab 또는 green cab을 언급하는 객체를 반환합니다: `("yellow cab" OR "green cab") AND (NOT Manhattan)`.

**설명**: 이 연산자들은 불 대수(Boolean algebra)의 논리곱, 논리합, 부정과 같고, SQL의 `WHERE ... AND ... OR ... NOT ...`과 같은 방식으로 조합됩니다. 예를 들어 택시 운행 객체 세 개의 설명이 (1) "yellow cab in Manhattan", (2) "green cab in Brooklyn", (3) "yellow cab in Queens"라면, `("yellow cab" OR "green cab") AND (NOT Manhattan)`의 결과는 (2)와 (3)입니다. (1)은 Manhattan을 포함하므로 제외됩니다.

> **중간 요약**: 기본 검색은 단어별 OR 검색이며, 따옴표로 정확한 구문을 찾고 AND, OR, NOT과 괄호로 조건을 조합할 수 있습니다.

<a id="wildcards"></a>
### 와일드카드 (Wildcards)

* `?`: 물음표는 문자 하나를 대신할 수 있습니다.
  * `qu?ck`을 검색하면 `quick`, `quack`, `qu4ck` 등의 결과가 반환됩니다.
* `*`: 별표는 0개 이상의 문자를 대신할 수 있습니다.
  * `bro*`를 검색하면 `bro`, `brother`, `broadcasting` 등의 결과가 반환됩니다.
  * 앞쪽 와일드카드(leading wildcard)도 지원됩니다. `*smith`를 검색하면 `smith`, `Goldsmith`, `Blacksmith` 등의 결과가 반환됩니다. 앞쪽 와일드카드를 사용하려면 **Ontology Manager**에서 해당 문자열 속성에 **Enable leading wildcards** 렌더 힌트(render hint)가 활성화되어 있어야 합니다. 자세한 내용은 [렌더 힌트](../../../02_define-ontologies/02_object-and-link-types/09_metadata/02_metadata-render-hints.md)를 참고하세요.

**주의**: 앞뒤를 함께 감싸는 와일드카드(`*term*`)는 지원되지 않습니다. 앞쪽 와일드카드(`*term`)나 뒤쪽 와일드카드(`term*`) 중 하나는 쓸 수 있지만 둘을 동시에 쓸 수는 없습니다. 이런 종류의 질의가 필요하다면 [Contour](https://www.palantir.com/docs/foundry/contour/overview/) 같은 다른 도구를 사용하는 것을 고려하세요.

**설명**: SQL의 `LIKE`와 비교하면 `?`는 `_`, `*`는 `%`에 해당합니다. 검색 엔진은 보통 단어를 사전순으로 정렬한 인덱스를 사용하므로, `bro*`처럼 앞부분이 정해진 검색은 인덱스에서 `bro`로 시작하는 구간만 읽으면 되지만, `*smith`처럼 앞부분이 비어 있으면 그런 범위 탐색을 할 수 없습니다. 그래서 앞쪽 와일드카드는 별도의 설정(렌더 힌트)을 켜야 하고, 양쪽 와일드카드는 지원되지 않습니다.

플랫폼 전반에서 텍스트 검색이 어떻게 동작하는지(분석기(analyzer) 동작, Workshop과 Functions API의 검색 기능 포함)에 대한 자세한 설명은 [텍스트 검색 이해하기](03_understanding-text-search.md)를 참고하세요.

<a id="fuzzy-searching"></a>
### 퍼지 검색 (Fuzzy searching)

검색어 끝에 `~` 연산자를 붙이면 비슷한 용어에 대한 "퍼지(fuzzy)" 일치와 정확한 일치를 함께 수행합니다. 예를 들어 `quikc~`는 `quick`과 `quack`에 대한 결과를 반환합니다.

**설명**: 퍼지 검색은 보통 편집 거리(edit distance, 레벤슈타인 거리)를 기준으로 합니다. 한 단어를 다른 단어로 바꾸는 데 필요한 문자 삽입, 삭제, 치환(그리고 인접 문자 교환) 횟수가 작으면 비슷한 단어로 간주합니다. `quikc`는 `k`와 `c`의 자리를 바꾸면 `quick`이 되므로 거리가 작아 결과에 포함됩니다.

> **중간 요약**: `?`는 한 글자, `*`는 0개 이상의 글자를 대신하며, 앞쪽 와일드카드는 렌더 힌트를 켜야 하고 앞뒤 동시 와일드카드는 지원되지 않습니다. 검색어 끝의 `~`는 철자가 비슷한 단어까지 찾는 퍼지 검색입니다.

## 정리

- 검색어의 단어들은 기본적으로 각각 독립적으로 검색되며, 따옴표로 감싸면 정확한 구문으로 검색됩니다.
- AND, OR, NOT과 괄호로 복잡한 조건을 조합할 수 있습니다.
- `?`(한 글자)와 `*`(0개 이상의 글자) 와일드카드를 지원하며, 앞쪽 와일드카드는 렌더 힌트 설정이 필요하고 `*term*`은 지원되지 않습니다.
- 검색어 끝에 `~`를 붙이면 비슷한 철자의 단어까지 찾는 퍼지 검색이 됩니다.
