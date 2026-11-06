# 텍스트 검색 이해하기 (Understanding text search)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/understanding-text-search/
- 사이드바 위치: Applications > Object Explorer > Search and explore objects > Understanding text search

이 페이지는 Foundry 전반(Object Explorer, Workshop, Functions API)의 텍스트 검색이 내부적으로 어떻게 동작하는지를 분석기(analyzer)와 토큰(token) 개념을 중심으로 설명합니다. 왜 `rown`으로 `brown`이 검색되지 않는지, 왜 `banana`로 `banana_pudding`이 검색되지 않는지 같은 의외의 결과를 이해하고, 화면이나 API마다 어떤 검색 기능이 지원되는지 비교할 수 있습니다.

Object Explorer, Workshop, Functions API를 포함한 Foundry 플랫폼 전반의 텍스트 검색은 **분석기(analyzer)라는** 메커니즘으로 텍스트를 처리하는 하부 검색 엔진에 의존합니다. 분석기가 어떻게 동작하는지 이해하면 더 효과적인 검색 질의를 작성하고 애플리케이션에서 더 나은 검색 경험을 만들 수 있습니다.

<a id="how-text-analysis-works"></a>
## 텍스트 분석의 동작 방식 (How text analysis works)

문자열 속성(property)이 검색용으로 인덱싱될 때, 플랫폼은 그 값을 분석기로 처리합니다. **표준 분석기(standard analyzer)라고** 불리는 기본 분석기([Lucene StandardAnalyzer ↗](https://lucene.apache.org/core/10_2_0/core/org/apache/lucene/analysis/standard/StandardAnalyzer.html) 참고)는 다음 단계를 수행합니다.

1. 공백과 문장부호 경계에서 텍스트를 **토큰(token)이라고** 부르는 개별 단어로 나눕니다.
2. 모든 토큰을 소문자로 바꿉니다.

예를 들어 속성 값 `The Quick Brown Fox`는 토큰 `the`, `quick`, `brown`, `fox`로 저장됩니다. `quick`을 검색하면 검색 엔진은 이 검색어 토큰을 저장된 토큰과 비교해 일치 항목을 찾습니다.

이런 토큰 기반 방식에는 중요한 의미가 있습니다.

* 인덱싱 중에 모든 토큰이 소문자로 바뀌므로, 검색은 기본적으로 **대소문자를 구분하지 않습니다**.
* 구문(phrase) 질의가 아닌 질의는 토큰을 독립적으로 일치시킵니다. 예를 들어 `brown fox` 검색은 `brown`과 `fox` 토큰을 따로 평가하므로, 순서나 근접성과 관계없이 두 토큰을 모두 포함하는 속성과 일치합니다. 토큰이 순서대로 붙어서 나타나야 한다면 구문 검색(`"brown fox"`)을 사용하세요.
* `rown`은 완전한 토큰이 아니므로 `rown` 검색은 `brown`과 일치하지 **않습니다**.

**설명**: 검색 엔진은 보통 역색인(inverted index)을 사용합니다. 역색인은 "토큰에서 그 토큰을 포함한 문서(객체) 목록으로" 가는 사전입니다. 예를 들어 객체 1의 값이 `The Quick Brown Fox`, 객체 2의 값이 `Brown Bear`라면 역색인은 `the: [1]`, `quick: [1]`, `brown: [1, 2]`, `fox: [1]`, `bear: [2]`입니다. `brown`을 검색하면 사전에서 `brown` 항목을 찾아 [1, 2]를 바로 얻습니다. 반면 `rown`이라는 항목은 사전에 없으므로 결과가 없습니다. 검색어 자체도 같은 분석기로 처리되기 때문에 `BROWN`을 검색해도 `brown`으로 바뀌어 일치합니다.

<a id="analyzer-types"></a>
### 분석기 유형 (Analyzer types)

문자열 속성에 사용되는 분석기는 온톨로지에서 설정합니다. 다음 분석기 유형을 사용할 수 있습니다.

| 분석기 | 동작 | 예시 값 | 결과 토큰 |
| ----- | ----- | ----- | ----- |
| Standard(기본값) | 공백과 문장부호로 나누고 소문자로 변환 | `The Quick-Brown Fox` | `the`, `quick`, `brown`, `fox` |
| Simple | 문자가 아닌 모든 문자에서 나누고 소문자로 변환(숫자와 문장부호는 버림) | `The Quick-Brown Fox 42` | `the`, `quick`, `brown`, `fox` |
| Not analyzed | 값 전체를 하나의 토큰으로 저장 | `The Quick-Brown Fox` | `The Quick-Brown Fox` |
| Whitespace | 공백에서만 나누고 대소문자 유지 | `The Quick-Brown Fox` | `The`, `Quick-Brown`, `Fox` |
| Language | 언어별 토큰화, 어간 추출(stemming), 불용어(stopword) 제거 적용 | `Running quickly`(영어) | `run`, `quick` |

Language 분석기는 다음 언어를 지원합니다: `english`, `french`, `german`, `japanese`, `korean`, `arabic`, `combined_arabic_english`.

속성의 분석기는 **Ontology Manager**에서 해당 속성의 검색 설정에서 확인하거나 바꿀 수 있습니다. 속성을 검색할 수 있으려면 **Searchable** 렌더 힌트(render hint)가 활성화되어 있어야 합니다.

**설명**: 어간 추출(stemming)은 `running`, `runs`, `ran` 같은 활용형을 기본형 `run`으로 줄이는 처리이고, 불용어(stopword)는 `the`, `a`, `is`처럼 너무 흔해서 검색에 도움이 되지 않는 단어입니다. Not analyzed는 주문 번호 `ORD-2024-001`처럼 값 전체가 그대로 일치해야 하는 식별자 속성에 적합합니다. 표준 분석기를 쓰면 이 값이 `ord`, `2024`, `001`로 쪼개져 `001`만 검색해도 다른 주문들이 함께 걸릴 수 있습니다.

<a id="special-character-handling-in-tokens"></a>
### 토큰 안의 특수 문자 처리 (Special character handling in tokens)

표준 분석기는 밑줄(`_`)과 마침표(`.`)를 구분자가 아니라 토큰의 일부로 취급합니다. 즉 다음과 같습니다.

* `banana_pudding`은 `banana`와 `pudding`이 아니라 단일 토큰 `banana_pudding`으로 저장됩니다.
* `user.name`은 `user`와 `name`이 아니라 단일 토큰 `user.name`으로 저장됩니다.

토큰 기반 검색 방법을 사용할 때 `banana` 검색은 값 `banana_pudding`과 일치하지 **않습니다**. 이런 값과 일치시켜야 한다면 `banana*` 같은 와일드카드 검색을 사용하거나 공백(whitespace) 분석기 사용을 고려하세요.

> **중간 요약**: 문자열 속성은 인덱싱될 때 분석기에 의해 토큰으로 나뉘어 저장되고, 검색은 이 토큰 단위로 일치 여부를 판단합니다. 표준 분석기는 공백과 문장부호로 나누고 소문자로 바꾸지만 밑줄과 마침표는 나누지 않으며, 속성마다 Simple, Not analyzed, Whitespace, Language 분석기를 고를 수 있습니다.

<a id="search-in-object-explorer"></a>
## Object Explorer에서의 검색 (Search in Object Explorer)

Object Explorer는 여전히 온톨로지 탐색, 전역 검색, 개별 객체 보기를 위한 기본 인터페이스입니다. [Insight](https://www.palantir.com/docs/foundry/insight/overview/)는 Object Explorer를 바탕으로 확장된 분석 기능을 제공하며, Object Explorer와 함께 사용할 수 있습니다.

Object Explorer는 서로 다른 일치 동작을 가진 두 가지 검색 인터페이스를 제공합니다.

<a id="global-search-bar"></a>
### 전역 검색창 (Global search bar)

Object Explorer 홈 페이지와 결과 페이지의 전역 검색창은 모든 객체 타입의 검색 가능한 모든 속성을 대상으로 토큰 기반 검색을 수행합니다. 기본적으로 질의의 각 단어는 OR 논리로 독립적으로 검색됩니다. 예를 들어 `yellow cab`을 검색하면 `yellow` 또는 `cab`과 일치하는 객체가 반환됩니다.

[검색 문법](02_search-syntax.md)에서 설명하는 기능으로 이 동작을 바꿀 수 있습니다.

* **구문 검색:** 용어를 따옴표로 감싸면(`"yellow cab"`) 정확한 구문 일치가 요구됩니다.
* **논리 연산자:** **AND**, **OR**, **NOT**으로 검색 조건을 결합합니다.
* **와일드카드:** `*`는 0개 이상의 문자, `?`는 문자 하나와 일치합니다. 뒤쪽 와일드카드(`term*`)는 지원되지만, 앞뒤를 함께 감싸는 와일드카드(예: `*row*`)는 지원되지 않습니다.
* **퍼지 검색:** 용어 뒤에 `~`를 붙이면 근사 일치를 찾습니다.

앞쪽 와일드카드 검색은 전역 검색창에서 지원되지 **않습니다**. 이 검색은 탐색(exploration)에서 개별 문자열 속성으로 필터링할 때만 사용할 수 있으며, 그것도 **Ontology Manager**에서 **Enable leading wildcards** 렌더 힌트가 활성화된 문자열 속성에서만 가능합니다. **Searchable** 렌더 힌트도 선택되어 있어야 합니다. 렌더 힌트 설정에 대한 자세한 내용은 [렌더 힌트](../../../02_define-ontologies/02_object-and-link-types/09_metadata/02_metadata-render-hints.md)를 참고하세요.

**설명**: 앞 페이지인 [검색 문법](02_search-syntax.md)에는 와일드카드 항목 아래에 `*smith` 같은 앞쪽 와일드카드 예가 함께 나오지만, 이 페이지에 따르면 앞쪽 와일드카드는 전역 검색창이 아니라 탐색 안의 속성 필터에서만 동작합니다.

<a id="property-filters-in-explorations"></a>
### 탐색에서의 속성 필터 (Property filters in explorations)

특정 객체 타입을 탐색할 때는 개별 문자열 속성에 키워드 필터를 추가할 수 있습니다. 이 필터는 다음 일치 모드를 제공합니다.

| 모드 | 동작 |
| ----- | ----- |
| Contains(기본값) | 속성이 모든 검색 토큰을 포함하는 객체와 일치 |
| Starts with | 속성이 검색어로 시작하는 토큰을 포함하는 객체와 일치(`term*`와 동일) |
| Exact | 속성 값이 검색어와 정확히 같은 객체와 일치 |
| Is not | 속성이 검색 토큰을 포함하는 객체를 제외 |

속성 키워드 필터는 해당 속성의 분석기가 만든 개별 토큰과 비교해 일치 여부를 판단합니다. 속성이 **not analyzed** 분석기를 사용한다면 값 전체가 하나의 토큰으로 취급되므로, 그에 맞게 일치시켜야 합니다.

> **중간 요약**: Object Explorer의 전역 검색창은 모든 검색 가능 속성에 대해 단어별 OR 토큰 검색을 하며 구문, 논리 연산자, 뒤쪽 와일드카드, 퍼지 검색을 지원합니다. 탐색 안의 속성 필터는 Contains, Starts with, Exact, Is not 모드를 제공하고, 앞쪽 와일드카드는 이 속성 필터에서만 쓸 수 있습니다.

<a id="leading-wildcard-search"></a>
## 앞쪽 와일드카드 검색 (Leading wildcard search)

앞쪽 와일드카드 검색을 사용하면 속성 값이 특정 용어로 끝나는 객체를 찾을 수 있습니다. 예를 들어 `*smith`를 검색하면 `Goldsmith`, `Blacksmith`, `smith` 같은 값과 일치합니다.

<a id="enabling-leading-wildcard-search"></a>
### 앞쪽 와일드카드 검색 활성화 (Enabling leading wildcard search)

앞쪽 와일드카드 검색을 사용하려면 관련 문자열 속성에 **Enable leading wildcards** 렌더 힌트를 활성화해야 합니다.

1. **Ontology Manager**에서 해당 객체 타입으로 이동해 설정할 문자열 속성을 선택합니다.
2. 속성 편집기에서 **Enable leading wildcards** 렌더 힌트를 선택합니다.
3. 앞쪽 와일드카드가 동작하려면 **Searchable** 렌더 힌트도 필요하므로, 이것도 선택되어 있는지 확인합니다.
4. 변경 사항을 저장하고 객체 타입의 백킹 데이터소스(backing datasource)를 Object Storage v1(Phonograph)로 다시 인덱싱합니다. 다음에 트리거되는 재인덱싱을 기다리거나, **Data sources** 탭에서 직접 시작할 수 있습니다.

사용할 수 있는 렌더 힌트의 전체 목록은 [렌더 힌트](../../../02_define-ontologies/02_object-and-link-types/09_metadata/02_metadata-render-hints.md)를 참고하세요.

**설명**: 4단계에서 재인덱싱이 필요한 이유는, 앞쪽 와일드카드를 지원하려면 인덱스 자체를 다른 형태로 만들어야 하기 때문입니다. 렌더 힌트만 바꾸고 재인덱싱을 하지 않으면 이미 만들어진 인덱스에는 그 구조가 없으므로 검색이 동작하지 않습니다. 일반적으로 검색 엔진은 단어를 뒤집어서 한 번 더 저장하는 방식(예: `goldsmith`를 `htimsdlog`로도 저장)으로 끝부분 검색을 앞부분 검색으로 바꿔 처리하는데, Palantir가 정확히 어떤 방식을 쓰는지는 원문에 나와 있지 않습니다.

<a id="using-leading-wildcard-search"></a>
### 앞쪽 와일드카드 검색 사용 (Using leading wildcard search)

렌더 힌트가 활성화되면 Object Explorer 속성 필터에서 검색어 앞에 `*`를 붙여 앞쪽 와일드카드를 사용할 수 있습니다. 예:

* `*smith`는 `Goldsmith`, `Blacksmith`, `smith`와 일치합니다.
* `*ing`은 `running`, `swimming`, `ing`과 일치합니다.

**주의**: 앞뒤를 함께 감싸는 와일드카드(`*term*`)는 지원되지 **않습니다**. 앞쪽 와일드카드(`*term`)나 뒤쪽 와일드카드(`term*`) 중 하나는 쓸 수 있지만 둘을 동시에 쓸 수는 없습니다. 부분 문자열 일치가 필요하다면 [Contour](https://www.palantir.com/docs/foundry/contour/overview/)나 Workshop Filter List의 Regex 모드 사용을 고려하세요.

<a id="search-in-workshop"></a>
## Workshop에서의 검색 (Search in Workshop)

Workshop은 객체를 검색하고 필터링하는 여러 방법을 제공하며, 각각 기능이 다릅니다.

<a id="filter-list-keyword-search"></a>
### Filter List 키워드 검색 (Filter list keyword search)

[Filter List](https://www.palantir.com/docs/foundry/workshop/widgets-filter-list/) 키워드 검색 구성 요소는 사용자가 질의할 때 고를 수 있는 다섯 가지 검색 모드를 지원합니다.

| 모드 | 동작 |
| ----- | ----- |
| All | 가장 넓은 검색입니다. 토큰 일치, 와일드카드 일치, 접두사 일치를 결합해 질의와 부분적으로든 완전히든 일치하는 모든 결과를 반환합니다. 와일드카드 하위 일치는 질의에 분석기를 적용하지 않고 인덱싱된 토큰과 직접 비교하므로, 와일드카드 질의는 **Not analyzed**나 **Whitespace** 분석기를 쓰는 속성에서 가장 예측 가능하게 동작합니다. |
| Any | 속성이 검색 토큰 중 하나라도 포함하는 객체와 일치 |
| Exact | 속성이 모든 검색 토큰을 순서대로 정확한 구문으로 포함하는 객체와 일치 |
| Advanced | 복잡한 질의를 위해 **AND**, **OR**, **NOT**, 따옴표, 괄호를 사용하는 불(Boolean) 문법 지원 |
| Regex | 속성 토큰에 정규 표현식 패턴을 적용해 일치하는 객체 찾기 |

고급 필터링에 대한 자세한 내용은 [Filter List 고급 필터링](https://www.palantir.com/docs/foundry/workshop/widgets-filter-list/#advanced-filtering) 문서를 참고하세요.

<a id="exploration-search-bar-widget"></a>
### Exploration Search Bar 위젯 (Exploration search bar widget)

Workshop의 **Exploration Search Bar** 위젯은 Object Explorer 전역 검색창과 같은 검색 인프라를 사용합니다. 구문 검색을 위한 따옴표, 논리 연산자, 와일드카드, 퍼지 검색을 포함해 같은 문법을 지원합니다.

<a id="object-set-filter-variables"></a>
### 객체 집합 필터 변수 (Object set filter variables)

[객체 집합 필터 변수(object set filter variable)](https://www.palantir.com/docs/foundry/workshop/object-set-filter-variables/)는 접두사로만 일치시키는 `CONTAIN` 필터를 지원합니다. 예를 들어 속성 값이 `id000123`이고 필터 질의가 `id0001`이면 일치로 간주됩니다. 그러나 질의 `d0001`은 값의 처음부터 시작하지 않으므로 일치하지 **않습니다**.

**설명**: 이름은 `CONTAIN`이지만 실제 동작은 SQL의 `LIKE 'id0001%'`(접두사 일치)에 해당하고, `LIKE '%d0001%'`(부분 문자열 일치)는 아닙니다.

> **중간 요약**: 앞쪽 와일드카드는 Enable leading wildcards와 Searchable 렌더 힌트를 켜고 재인덱싱해야 속성 필터에서 쓸 수 있습니다. Workshop에서는 Filter List가 All, Any, Exact, Advanced, Regex 다섯 모드를 제공하고, Exploration Search Bar는 전역 검색창과 같은 문법을 쓰며, 객체 집합 필터 변수의 `CONTAIN`은 접두사 일치만 합니다.

<a id="search-in-the-functions-api"></a>
## Functions API에서의 검색 (Search in the Functions API)

[Functions API(TSv1)](../../../02_define-ontologies/04_functions/13_functions-on-objects/07_api-object-sets.md#filtering)는 문자열 필터 메서드를 통해 텍스트 검색 동작을 가장 세밀하게 제어할 수 있게 합니다.

| 메서드 | 동작 |
| ----- | ----- |
| `.exactMatch()` | 속성 값이 질의 문자열과 정확히 같은 객체와 일치 |
| `.phrase()` | 질의를 토큰으로 나누고, 모든 토큰을 순서대로, 사이에 다른 토큰 없이 포함하는 값과 일치 |
| `.phrasePrefix()` | `.phrase()`와 같지만, 마지막 토큰은 그 토큰으로 시작하는 토큰과도 일치 |
| `.prefixOnLastToken()` | 질의를 토큰으로 나누고, 모든 토큰을 순서에 관계없이 포함하는 값과 일치하며, 마지막 토큰은 그 토큰으로 시작하는 토큰과도 일치 |
| `.matchAnyToken()` | 질의를 토큰으로 나누고, 토큰 중 하나라도 포함하는 값과 일치 |
| `.matchAllTokens()` | 질의를 토큰으로 나누고, 모든 토큰을 순서에 관계없이 포함하는 값과 일치 |
| `.fuzzyMatchAnyToken()` | `.matchAnyToken()`과 같지만 편집 거리(edit distance) 안의 근사 일치를 허용 |
| `.fuzzyMatchAllTokens()` | `.matchAllTokens()`와 같지만 편집 거리 안의 근사 일치를 허용 |

**주의**: `.phrase()`와 `.phrasePrefix()` 메서드는 밑줄이나 마침표로 만들어진 토큰 경계를 넘어 일치시키지 않습니다. 예를 들어 `banana_pudding`은 단일 토큰이므로 `.phrase("banana")`는 값 `banana_pudding`과 일치하지 않습니다.

**설명**: 값이 `New York City`(토큰 `new`, `york`, `city`)일 때 각 메서드의 결과를 비교하면 다음과 같습니다. `.phrase("york city")`는 일치, `.phrase("city york")`는 순서가 달라 불일치, `.phrasePrefix("new yo")`는 마지막 토큰 `yo`가 `york`의 접두사라 일치, `.matchAllTokens("city new")`는 순서와 관계없으므로 일치, `.matchAnyToken("boston city")`는 `city`가 있으므로 일치, `.exactMatch("new york")`는 값 전체가 같지 않으므로 불일치입니다.

<a id="comparison-of-search-capabilities"></a>
## 검색 기능 비교 (Comparison of search capabilities)

아래 표는 각 컨텍스트에서 어떤 검색 기능을 사용할 수 있는지 요약합니다.

| 기능 | Object Explorer(전역) | Object Explorer(속성 필터) | Workshop Filter List | Functions API |
| ----- | ----- | ----- | ----- | ----- |
| 토큰 검색 | 예 | 예 | 예 | 예 |
| 구문 검색 | 예(따옴표) | 아니요 | 예(Exact 모드) | 예(`.phrase()`) |
| 접두사 검색 | 예(`term*`) | 예(Starts with) | 예(All 모드) | 예(`.phrasePrefix()`, `.prefixOnLastToken()`) |
| 앞쪽 와일드카드 검색 | 아니요 | 예(렌더 힌트 필요) | 아니요 | 아니요 |
| 와일드카드 검색 | 예(`*`, `?`) | 아니요 | 예(All 모드) | 아니요 |
| 퍼지 검색 | 예(`~`) | 아니요 | 아니요 | 예(`.fuzzyMatchAnyToken()`, `.fuzzyMatchAllTokens()`) |
| 불 연산자 | 예(AND, OR, NOT) | 아니요 | 예(Advanced 모드) | 예(`Filters.and()`, `Filters.or()`, `Filters.not()`) |
| 정규 표현식 | 아니요 | 아니요 | 예(Regex 모드) | 아니요 |

> **중간 요약**: Functions API는 정확 일치, 구문, 접두사, 토큰 일치, 퍼지 일치를 메서드로 세밀하게 고를 수 있습니다. 앞쪽 와일드카드는 Object Explorer 속성 필터에서만, 정규 표현식은 Workshop Filter List에서만 쓸 수 있습니다.

<a id="common-pitfalls"></a>
## 흔히 겪는 문제 (Common pitfalls)

* **단어 일부로 검색하면 토큰과 일치하지 않습니다:** 와일드카드(`app*`)나 접두사 검색 메서드를 쓰지 않는 한 `app` 검색은 `application`과 일치하지 않습니다. 표준 분석기가 만든 토큰은 `application`이고, `app`은 이 토큰과 정확히 일치하지 않기 때문입니다.
* **밑줄과 마침표 때문에 토큰이 나뉘지 않습니다:** 표준 분석기는 `first_name`과 `user.name`을 단일 토큰으로 취급합니다. `first_name` 안의 `first`를 검색해야 한다면 와일드카드를 쓰거나 속성의 분석기를 바꾸는 것을 고려하세요.
* **Object Explorer에서 따옴표 없는 여러 단어 질의는 OR 논리를 씁니다:** Object Explorer 전역 검색창에서 `New York`을 검색하면 `new` 또는 `york`와 일치하는 객체가 반환되어, 예상하지 못한 결과가 포함될 수 있습니다. 정확한 구문 일치를 원하면 `"New York"`을 사용하세요.
* **와일드카드 필터는 질의를 분석하지 않습니다:** 와일드카드 검색(예: `Quick*`)을 사용하면 질의 문자열은 분석기를 거치지 않고, 인덱싱된 토큰과 문자 단위로 그대로 비교됩니다. 이로 인해 두 가지 결과가 생깁니다.
  * **대소문자가 인덱싱된 형태와 맞아야 합니다.** 표준 분석기(모든 토큰을 소문자로 바꿈)를 쓰는 속성에서는, 원래 텍스트에 대문자가 있었더라도 분석 과정에서 소문자로 바뀌었기 때문에 대문자를 포함한 와일드카드 질의는 일치하지 않습니다.
  * **여러 단어로 된 와일드카드 질의는 일치하지 않습니다.** 인덱싱된 토큰은 각각 한 단어이므로, 공백을 포함한 와일드카드 질의(예: `a search term*`)는 개별 토큰과 비교되어 일치할 수 없습니다. 따라서 와일드카드 검색은 사실상 한 단어 질의로 제한됩니다. 여러 단어에 걸친 부분 일치가 필요하다면 [Contour](https://www.palantir.com/docs/foundry/contour/overview/)나 Workshop Filter List의 Regex 모드를 고려하세요.
* **앞쪽 와일드카드에는 렌더 힌트가 필요합니다:** 앞쪽 와일드카드 검색(`*term`)은 **Ontology Manager**에서 **Enable leading wildcards** 렌더 힌트가 활성화된 문자열 속성에서만 사용할 수 있습니다. 이 렌더 힌트가 없으면 앞쪽 와일드카드 질의는 결과를 반환하지 않습니다.
* **앞뒤를 함께 감싸는 와일드카드는 지원되지 않습니다:** Object Explorer나 Workshop에서 `*term*`을 검색할 수 없습니다. 부분 문자열 일치가 필요하다면 [Contour](https://www.palantir.com/docs/foundry/contour/overview/)나 Workshop Filter List의 Regex 모드 사용을 고려하세요.

**설명**: 대소문자 문제의 구체적인 예입니다. 값 `Quickly`는 표준 분석기에서 토큰 `quickly`로 저장됩니다. 일반 검색 `Quickly`는 질의도 분석기를 거쳐 `quickly`가 되므로 일치합니다. 하지만 와일드카드 검색 `Quick*`는 분석기를 거치지 않아 대문자 `Q`가 그대로 남고, 저장된 토큰 `quickly`와 비교하면 첫 글자가 달라 일치하지 않습니다. 이때는 `quick*`처럼 소문자로 검색해야 합니다.

> **중간 요약**: 단어 일부 검색, 밑줄과 마침표로 붙은 단어, 따옴표 없는 여러 단어 질의, 대문자가 들어간 와일드카드 질의는 예상과 다른 결과를 내기 쉽습니다. 부분 문자열 일치가 필요하면 Contour나 Workshop Filter List의 Regex 모드를 사용합니다.

## 정리

- Foundry의 텍스트 검색은 인덱싱 시 분석기가 만든 토큰 단위로 일치 여부를 판단하며, 기본 표준 분석기는 공백과 문장부호로 나누고 소문자로 바꿉니다(밑줄과 마침표는 나누지 않음).
- 속성마다 Standard, Simple, Not analyzed, Whitespace, Language 분석기를 Ontology Manager에서 고를 수 있습니다.
- Object Explorer 전역 검색창, 속성 필터, Workshop Filter List, Functions API는 지원하는 검색 기능(구문, 접두사, 와일드카드, 퍼지, 불 연산자, 정규 표현식)이 서로 다릅니다.
- 앞쪽 와일드카드는 렌더 힌트 설정과 재인덱싱 후 속성 필터에서만 쓸 수 있고, `*term*` 형태는 어디서도 지원되지 않습니다.
- 와일드카드 질의는 분석기를 거치지 않으므로 소문자 한 단어로 써야 예상대로 동작합니다.
