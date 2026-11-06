# Object Explorer URL 생성하기 (Generate Object Explorer URLs)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/generate-urls/
- 사이드바 위치: Applications > Object Explorer > Generate Object Explorer URLs

이 페이지는 다른 애플리케이션이나 외부 시스템에서 Object Explorer의 특정 검색, 객체 타입 탐색, 저장된 탐색으로 바로 이동하는 URL을 만드는 방법을 설명합니다. 키워드 검색 URL, 탐색 링크, 그리고 필터를 JSON으로 기술해 URL에 담는 복잡한 검색 URL까지 단계별로 다룹니다.

Object View를 개발하는 과정에서, 또는 Object View를 Slate 애플리케이션이나 외부 시스템에 통합할 때, 특정 객체로 연결되거나 객체를 검색하는 URL을 생성해야 할 수 있습니다.

특정 Object View로 연결되는 URL을 만드는 방법은 Object Views 문서의 [Object View URL 생성하기](../03_object-views/09_generate-urls.md)를 참고합니다.

<a id="generating-a-keyword-only-search"></a>
## 키워드 전용 검색 생성하기 (Generating a keyword-only search)

텍스트에 특수 문자나 공백이 들어 있으면 인코딩해야 합니다.

`encodeURIComponent("hello world");`

URL을 만듭니다.

`<BASEURL>/hubble/external/keyword/v0/<MY_ENCODED_TEXT>`

**설명**: URL에는 공백이나 `/`, `?`, `&` 같은 문자를 그대로 넣을 수 없습니다. 이런 문자는 URL 구조를 나누는 구분자로 해석되기 때문입니다. JavaScript의 `encodeURIComponent("hello world")`는 `"hello%20world"`를 돌려주며, 이처럼 문자를 `%` 뒤에 16진수 코드가 붙는 형태로 바꾸는 것을 퍼센트 인코딩이라고 합니다. `<BASEURL>`은 사용 중인 Foundry 환경의 주소입니다. 경로에 있는 `hubble`은 Object Explorer의 내부 이름으로 URL에 쓰입니다.

<a id="linking-to-explorations"></a>
## 탐색으로 연결하기 (Linking to explorations)

Object Explorer는 특정 객체 타입, 저장된 탐색, 또는 URL에 필터가 기술된 새 검색으로 연결되는 링크를 열 수 있습니다. 각 링크는 집계 결과를 차트로 보여 주는 기본 Explore 보기로 열 수도 있고, 링크 URL 끝에 `perspectiveId=results` 파라미터를 덧붙여 표 형태의 Results 보기로 열 수도 있습니다.

**탐색할 객체 타입 열기 (Opening an object type For exploration)**

특정 객체 타입에 대한 탐색은 `objectTypeId` URL 파라미터로 열 수 있습니다. 예를 들면 다음과 같습니다.

`/workspace/hubble/exploration?objectTypeId=aircraft`.

Results 보기로 열려면 `perspectiveId=results` 파라미터를 덧붙입니다.

`/workspace/hubble/exploration?objectTypeId=aircraft&perspectiveId=results`

**저장된 탐색이나 객체 집합 불러오기 (Loading a Saved Exploration or Object Set)**

저장된 탐색이나 객체 집합(object set)을 열려면 `saved` 경로를 사용합니다.

`/workspace/hubble/exploration/saved/ri.object-set.main.versioned-object-set.4b117663-06d7-4bd1-a2be-8e1ba20998cb`

다른 Foundry 애플리케이션이 만든 객체 집합을 불러오려면 `external/objectSet` 경로를 사용합니다.

`/workspace/hubble/external/objectSet/v0/ri.object-set.main.object-set.f6916120-5b52-4312-8be4-9f5764983907`

**설명**: `ri.object-set.main...`처럼 `ri.`로 시작하는 문자열은 RID(Resource Identifier)로, Foundry 안의 리소스 하나를 전역적으로 유일하게 가리키는 식별자입니다. 데이터베이스의 기본 키가 테이블 안에서 행 하나를 가리키듯, RID는 플랫폼 전체에서 리소스 하나를 가리킵니다. URL의 `?` 뒤에 붙는 `objectTypeId=aircraft&perspectiveId=results`는 HTTP 쿼리 문자열이며, `&`로 여러 파라미터를 이어 붙입니다.

> **중간 요약**: 키워드 검색은 텍스트를 인코딩해 `/hubble/external/keyword/v0/` 뒤에 붙이고, 객체 타입 탐색은 `objectTypeId` 파라미터로, 저장된 탐색과 외부 객체 집합은 RID를 경로에 넣어 엽니다. `perspectiveId=results`를 붙이면 표 보기로 열립니다.

<a id="advanced-generating-a-complex-search"></a>
## [고급] 복잡한 검색 생성하기 (\[Advanced] Generating a complex search)

필터 묶음을 다음과 같은 형태로 만듭니다.

```json
{
  "keyword": "",
  "objectTypes": [
    "google-reviews"
  ],
  "filters": [
    {
      "type": "propertyFilter",
      "objectType": "google-reviews",
      "propertyType": "Description",
      "value": {
          "type": "textFilter",
          "text": "hello"
      }
    },
    {
      "type": "propertyFilter",
      "objectType": "google-reviews",
      "propertyType": "rating",
      "value": {
          "type": "valuesFilter",
          "values": ["3", "4"]
      }
    },
    {
      "type": "propertyFilter",
      "objectType": "google-reviews",
      "propertyType": "creation-date",
      "value": {
          "type": "dateRangeFilter",
          "dateRangeFilter": {
              "start": "2000-01-10",
              "end": "2000-01-11"
          }
      }
    },
    {
      "type": "linkFilter",
      "objectType": "google-reviews",
      "linkType": "restaurant-to-review",
      "value": {
          "type": "presenceFilter",
          "matchType": "MUST_HAVE"
      }
    }
  ]
}
```

**설명**: 이 JSON은 `google-reviews` 객체 타입에서 네 가지 조건을 모두 만족하는 객체를 찾는 검색입니다. (1) `Description` 속성에 "hello"라는 텍스트가 들어 있고, (2) `rating` 속성 값이 3 또는 4이며, (3) `creation-date`가 2000-01-10부터 2000-01-11 사이이고, (4) `restaurant-to-review` 링크로 연결된 식당이 반드시 있어야 합니다(`MUST_HAVE`). SQL로 쓰면 대략 `WHERE description LIKE '%hello%' AND rating IN (3, 4) AND creation_date BETWEEN ... AND EXISTS (연결된 식당)`에 해당합니다. 앞의 세 개는 속성 조건(`propertyFilter`)이고 마지막 하나는 링크 조건(`linkFilter`)입니다.

위 예시는 최신 형식이 아닐 수 있습니다. 최신 형식은 아래 절차로 확인합니다.

이 밖에도 다음과 같은 필터 타입을 사용할 수 있습니다.

* **numberRangeFilter:** `min`(선택, 숫자), `max`(선택, 숫자)
* **relativeDateFilter:** `sinceDaysAgo`(선택, 숫자), `untilDaysAgo`(선택, 숫자)
* **timestampRangeFilter:** `startMillis`(선택, 숫자), `endMillis`(선택, 숫자)
* **relativeTimestampFilter:** `sinceMillisAgo`(선택, 숫자), `untilMillisAgo`(선택, 숫자)

값의 타입은 Object Explorer에서 해당 속성에 기본으로 표시되는 위젯의 타입과 일치해야 합니다. 예를 들어 히스토그램 위젯에는 `valuesFilter`, 텍스트 상자에는 `textFilter`를 씁니다.

이 필터를 생성하는 권장 방법은 다음과 같습니다.

1. Object Explorer를 열고, 생성하려는 모든 필터에 샘플 값을 골라 넣은 예시 검색을 만듭니다.

2. Chrome 콘솔을 엽니다(*마우스 오른쪽 클릭* 후 *inspect element*(요소 검사)). 그냥 Chrome 콘솔만 여는 것이 아니라, 결과 개수처럼 Object Explorer가 제공하는 요소를 검사해야 합니다.

3. 콘솔에서 `await hubble_get_current_search()`를 실행합니다.

그러면 현재 필터 묶음의 JSON이 반환되며, 이를 이용해 올바른 형식을 파악하고 값을 원하는 값으로 바꿔 넣을 수 있습니다.

**주의**: *속성(PROPERTY)* 필터는 여러 개 둘 수 있지만, *링크(LINK)* 필터는 1개만 둘 수 있습니다.

4. URL 인코딩합니다.

`encodeURIComponent(<MY_FILTERS>);`

5. URL을 만듭니다.

`<BASEURL>/hubble/external/search/v2/{<ENCODED-URL-FROM-ABOVE>}`

**설명**: 전체 흐름은 "화면에서 예시 검색 만들기, 브라우저 콘솔에서 그 검색의 JSON 꺼내기, 값 바꾸기, 인코딩해서 URL 경로에 붙이기"입니다. 예를 들어 외부 시스템이 리뷰 점수별 링크를 만들어야 한다면, 위 JSON의 `values`만 프로그램에서 바꿔 끼운 뒤 `encodeURIComponent(JSON.stringify(filters))` 결과를 URL에 넣으면 됩니다.

> **중간 요약**: 복잡한 검색은 필터를 JSON으로 기술하고 URL 인코딩해 `/hubble/external/search/v2/` 경로에 넣어 만듭니다. 최신 JSON 형식은 브라우저 콘솔의 `hubble_get_current_search()`로 확인하며, 링크 필터는 하나만 허용됩니다.

## 정리

- 특정 Object View로 가는 URL은 Object Views 문서에서 따로 다룹니다.
- 키워드 검색 URL은 인코딩한 텍스트를 `/hubble/external/keyword/v0/` 뒤에 붙여 만듭니다.
- 객체 타입 탐색은 `objectTypeId`, 저장된 탐색과 외부 객체 집합은 RID 경로로 열며, `perspectiveId=results`로 표 보기를 지정합니다.
- 복잡한 검색은 속성 필터와 링크 필터(1개까지)를 담은 JSON을 인코딩해 `/hubble/external/search/v2/` 경로에 넣어 만들고, 최신 형식은 콘솔에서 확인합니다.
