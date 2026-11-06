# Object View URL 생성하기 (Generate Object View URLs)

- 원문: https://www.palantir.com/docs/foundry/object-views/generate-urls/
- 사이드바 위치: Applications > Object Views > Generate Object View URLs

이 페이지는 특정 객체의 Object View로 바로 이동하는 URL을 만드는 세 가지 형식을 설명합니다. 다른 애플리케이션이나 웹 페이지에서 객체 화면으로 링크를 걸거나, iframe으로 화면을 끼워 넣을 때 어떤 URL을 써야 하는지 알 수 있습니다.

Object View를 개발하다 보면 특정 객체로 연결되거나 객체를 검색하는 URL을 생성해야 할 때가 있습니다.

이 뷰를 링크로 제공하지 않고 iframe 안에 임베드한다면, URL 쿼리 파라미터 `embedded=true`를 덧붙이세요. 그러면 Workspace 사이드바 없이 뷰가 로드됩니다.

검색이나 Exploration으로 연결되는 URL을 만드는 방법은 [Object Explorer URL 생성하기](../01_object-explorer/05_generate-urls.md)를 참고하세요.

**설명**: iframe은 HTML 페이지 안에 다른 웹 페이지를 넣어 보여 주는 태그(`<iframe src="...">`)입니다. URL 쿼리 파라미터는 주소의 `?` 뒤에 `이름=값` 형태로 붙는 부분이며, 여러 개는 `&`로 잇습니다. 예를 들어 `.../object-view/ri.abc?embedded=true`처럼 씁니다.

<a id="generate-object-links"></a>
## 객체 링크 생성하기 (Generate object links)

객체로 연결하는 방법은 세 가지입니다.

**옵션 1**

`/workspace/hubble/external/object/v0/<object-type-id>?<primary-key-property-id>=<primary-key-property-value>`

예시:

`/workspace/hubble/external/object/v0/aircraft?aircraftId=1234`

**설명**: 이 형식은 객체 타입 ID와 기본 키(primary key) 값으로 객체를 찾습니다. 위 예시는 `aircraft` 객체 타입에서 기본 키 속성 `aircraftId`의 값이 `1234`인 객체를 엽니다. SQL로 쓰면 `SELECT * FROM aircraft WHERE aircraftId = '1234'`로 행 하나를 지정하는 것과 같은 방식입니다.

**옵션 2**

`/workspace/hubble/external/search/v2/?objectId=<objectRid>`

기본 키 속성 값에 특수 문자가 들어갈 가능성이 있다면 이 방법을 권장합니다.

이 URL은 Object Explorer의 맥락 안에서 Object View를 로드합니다. 추가적인 감싸는 화면 없이 Object View만 로드하려면 `/workspace/hubble/objects/<objectRid>` 형태의 URL을 만드세요. Object View를 iframe에 임베드하려면 대신 옵션 3을 사용하세요.

**설명**: RID(Resource Identifier)는 Foundry가 각 리소스와 객체에 부여하는 고유 식별 문자열입니다(`ri.`로 시작). 기본 키 값에 `&`, `?`, `/`, 공백 같은 문자가 있으면 URL 쿼리 문자열에서 의미가 섞일 수 있으므로, 이런 문자가 없는 RID를 쓰는 옵션 2가 더 안전합니다.

**옵션 3**

`/workspace/object-view/<objectRid>`

이 URL은 독립형(standalone) Object View 경로이며 항상 Workspace 사이드바 없이 로드됩니다. 헤더 없이 Object View를 로드하려면 URL 쿼리 파라미터 `shouldHideHeader=true`를 덧붙이세요. 다크 모드로 뷰를 로드하려면 `inDarkMode=true`를 덧붙이세요. 예시: `/workspace/object-view/<objectRid>?shouldHideHeader=true&inDarkMode=true`

댓글이나 Object Explorer에서 탐색(exploration)을 시작하는 옵션 같은 헤더 기능은 `/workspace/hubble/*` 경로와 다를 수 있습니다.

> **중간 요약**: 객체 링크는 기본 키로 찾는 옵션 1, 객체 RID로 찾는 옵션 2(특수 문자에 안전), iframe 임베드용 독립형 경로인 옵션 3으로 만들 수 있습니다. 옵션 3은 `shouldHideHeader`, `inDarkMode` 파라미터로 표시 방식을 조절합니다.

## 정리

- iframe에 넣을 때는 `embedded=true`를 붙이면 Workspace 사이드바 없이 로드됩니다.
- 옵션 1은 객체 타입 ID와 기본 키 값으로, 옵션 2는 객체 RID로 객체를 엽니다. 기본 키에 특수 문자가 있을 수 있으면 옵션 2를 씁니다.
- 옵션 3(`/workspace/object-view/<objectRid>`)은 항상 사이드바 없이 뜨는 독립형 경로이며 iframe 임베드에 적합합니다.
- 경로에 따라 헤더 기능(댓글, 탐색 시작 등)이 다를 수 있습니다.
