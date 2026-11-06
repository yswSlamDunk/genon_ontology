# 앱과 파일 위젯 (Apps and Files)

- 원문: https://www.palantir.com/docs/foundry/object-views/widgets-apps-files/
- 사이드바 위치: Applications > Object Views > Legacy Object Views > Apps and Files

이 페이지는 레거시 Object View 안에 다른 Foundry 앱(Quiver, Slate, Report 등)을 임베드하거나, 미디어와 하이퍼링크, 파일, 코멘트를 붙이는 위젯들을 설명합니다. 특히 Slate 위젯은 Object View와 메시지를 주고받는 이벤트 형식이 정해져 있어, 두 애플리케이션이 브라우저 안에서 어떻게 상태를 공유하는지 보여 줍니다. 여러 위젯이 객체 자체에 데이터를 저장하지 않는다는 한계도 함께 알아 두어야 합니다.

**앱과 파일 위젯(Apps and Files widgets)은** 현재 Object View 안에 다른 Foundry 앱을 임베드하고, 표시하고, 링크할 수 있게 해 줍니다. 이 임베드 위젯들은 [Quiver](https://www.palantir.com/docs/foundry/quiver/overview/)나 [Slate](https://www.palantir.com/docs/foundry/slate/overview/) 같은 다른 앱에서 만든 자산을 지원할 수 있습니다. 또한 Object View에서 미디어를 표시하고, 파일을 업로드하고, 하이퍼링크를 추가하고, 해당 객체에 대한 코멘트와 대화를 허용할 수 있습니다.

더 정교한 Object View를 만들고 싶다면 [Workshop 기반 탭](../06_full-object-views/02_config-object-views.md)을 만드는 것을 고려하세요.

아래 위젯 중 일부는 객체를 인식하지 못합니다(not object-aware). 즉 Object View 안의 다른 위젯과 상호작용하는 데 한계가 있습니다.

* 예 1: Comments 위젯에 남긴 내용은 해당 Object View 안에만 저장되며, 실제 객체에 라이트백(writeback)되지 않습니다. 이 코멘트가 특정 객체의 맥락 밖에서도 유용할 수 있다면, 액션으로 코멘트를 수집하는 것을 고려하세요.
* 예 2: "Linked Files"로 추가한 파일은 Foundry에 저장되지만 객체에 링크되지는 않습니다. 이 파일들을 재사용할 수 있게 하려면 [액션 첨부 파일(Actions attachments)](../../../02_define-ontologies/03_action-types/16_upload-attachments.md)을 사용하는 것을 고려하세요.
* 예 3: Slate나 Contour를 임베드하면 파라미터를 전달할 수는 있지만, 필터를 발행(publish)하거나 소비(consume)하지 않으며 Charts 위젯 같은 다른 위젯과 교차 필터링(cross-filtering)도 할 수 없습니다.

**설명**: "객체를 인식한다"는 것은 위젯이 지금 어떤 객체를 보고 있는지 알고, 그 객체의 데이터를 읽거나 쓰거나, 다른 위젯과 필터를 주고받는다는 뜻입니다. 예를 들어 Comments 위젯에 "엔진 점검 필요"라고 적어도 그 문자열은 Aircraft 객체의 속성 값으로 저장되지 않습니다. 따라서 나중에 "엔진 점검 필요 코멘트가 달린 항공기"를 검색하거나 집계할 수 없습니다. 반면 액션으로 저장하면 객체의 속성이나 별도 객체로 남으므로 검색과 분석이 가능합니다.

<a id="quiver-dashboard"></a>
## Quiver 대시보드 (Quiver Dashboard)

Object View에 Quiver 대시보드를 임베드하는 자세한 단계는 [Quiver 대시보드 문서](https://www.palantir.com/docs/foundry/quiver/dashboards-object-view/)를 참조하세요.

<a id="slate-application"></a>
## Slate 애플리케이션 (Slate Application)

이 위젯은 Object View 안에 [Slate 애플리케이션](https://www.palantir.com/docs/foundry/slate/overview/)을 표시하며, 두 애플리케이션 사이의 상태 공유와 상호작용을 지원합니다. Object View에서 Slate 애플리케이션 방향으로는 현재 객체 맥락과 활성 필터 상태가 제공됩니다. Slate 애플리케이션에서 Object View 방향으로는 Slate 안에 일련의 이벤트가 제공되며, 이 이벤트들은 새 Object 탭이나 Exploration 탭 열기, Object View 필터 갱신 같은 Object Explorer의 동작에 대응됩니다.

<a id="configuration"></a>
### 구성 (Configuration)

**Slate Resource**
표시할 Slate 리소스를 선택합니다. 객체를 볼 권한이 있는 모든 사용자가 이 애플리케이션도 볼 수 있는지 확인하세요.

Slate 리소스를 "반응형(responsive)"으로 디자인하면 가장 좋은 결과를 얻을 수 있습니다. 애플리케이션이 Object View 레이아웃과 사용 가능한 화면 크기에 맞춰 크기를 조정하기 때문입니다.

**Default Parameters**
기본적으로 현재 객체의 ID와 그 객체 타입의 ID가 Slate 대시보드로 전달되며, 변수에 매핑할 수 있습니다. 이 전달은 끌 수도 있고 대상 변수를 바꿀 수도 있습니다. 기본 변수 이름은 `objectId`와 `objectTypeId`입니다. Slate 애플리케이션의 Variable 탭에서 이에 대응하는 변수(Variable)를 직접 만들어 두어야 합니다.

**Custom Parameters**
추가 사용자 정의 파라미터를 사용해 속성 값이나 미리 정해 둔 정적 값을 Slate 애플리케이션으로 전달합니다. Slate 애플리케이션에 대응하는 변수를 만들어 이 파라미터를 받아 애플리케이션에서 사용합니다.

<a id="using-parameters-in-slate"></a>
### Slate에서 파라미터 사용하기 (Using Parameters in Slate)

구성한 파라미터는 Slate 애플리케이션이 로드될 때 전달됩니다. Slate 애플리케이션을 구성할 때 각 파라미터에는 Variable 패널에서 만든 대응 변수가 있어야 합니다. [변수 사용 방법에 대해 자세히 알아보세요.](https://www.palantir.com/docs/foundry/slate/concepts-variables/) Object Explorer에서 Slate로 전달되는 파라미터의 키와 값을 확인하려면 Object View 편집기의 디버깅 툴바에서 "View parameters"를 선택하면 됩니다.

**설명**: 파라미터 전달은 함수 호출 시 인자를 넘기는 것과 같은 구조입니다. Object View가 호출하는 쪽, Slate 앱이 호출되는 쪽이고, 인자 이름(`objectId` 등)과 받는 쪽 변수 이름이 일치해야 값이 들어갑니다. 예를 들어 Aircraft A1의 화면을 열면 `objectId = "A1"`이 전달되고, Slate는 이 변수로 A1에 해당하는 데이터만 조회해 그릴 수 있습니다.

<a id="accessing-object-view-filters"></a>
### Object View 필터 접근하기 (Accessing object view filters)

Object View 필터는 Slate에서 사용할 수 있는 Object Set API와 쉽게 함께 쓰도록 IObjectSetFilter 형식으로 공유됩니다. 필터가 바뀌면 프레임 간(cross-frame) `postMessage`로 Slate에 자동 전송되며, Slate에서 Object Explorer로 이벤트를 보내 수동으로 요청할 수도 있습니다. 이 요청 이벤트는 Slate 대시보드가 처음으로 필터를 받을 준비가 되었을 때 필터 전송을 트리거하는 데 사용할 수 있습니다.

Slate 안에서 필터를 받으려면 `slate.getMessage` 이벤트 핸들러를 구성해야 합니다. 이 핸들러는 post message 페이로드를 받아 JSON으로 파싱한 뒤 결과를 변수에 설정합니다. [이벤트에 대해 자세히 알아보세요.](https://www.palantir.com/docs/foundry/slate/concepts-events/) 다음 코드면 필터를 변수에 받기에 충분합니다.

```js
const payload = {{slEventValue}}["payload"]
return JSON.parse(payload);
```

**설명**: `{{slEventValue}}`는 Slate가 받은 메시지 이벤트의 값입니다. 첫 줄은 메시지에서 `payload` 필드를 꺼내고, 둘째 줄은 문자열로 온 그 값을 `JSON.parse`로 객체로 바꿔 반환합니다. 반환값이 이벤트 핸들러에 연결된 변수에 저장되므로, 이후 Slate의 다른 쿼리나 위젯이 그 변수를 필터 조건으로 쓸 수 있습니다. `postMessage`는 브라우저에서 서로 다른 프레임(여기서는 Object View 페이지와 그 안에 iframe으로 들어간 Slate) 사이에 메시지를 보내는 표준 API입니다.

필터를 받는 형식은 두 가지입니다. 한 형식은 필터가 어느 객체 타입에서 나왔는지 구분하지 않고 모든 필터를 담고, 다른 형식은 필터를 객체 타입별로 묶고 특정 객체 타입에 기반하지 않은 필터는 별도 목록으로 담습니다.

모든 필터를 담는 페이로드는 다음 형태입니다.

```json
{
    "type": "HUBBLE_SLATE_WIDGET // ACTIVE_FILTERS_UPDATED",
    "payload": <IObjectSetFilter[]>
}
```

(원문에는 객체 타입별로 묶인 필터의 페이로드 형태 예제도 있습니다. 메시지 `type`은 `HUBBLE_SLATE_WIDGET // ACTIVE_FILTERS_BY_OBJECT_TYPE_ID_UPDATED`이고, `payload` 안에 객체 타입 ID를 키로 하는 `filtersByObjectType`과 `globalFilters` 두 필드가 있습니다.)

**설명**: 메시지는 `type`과 `payload` 두 필드로 이루어집니다. `type` 문자열이 메시지의 종류를 알려 주고, 받는 쪽은 이 문자열을 보고 `payload`를 어떻게 해석할지 정합니다. `<IObjectSetFilter[]>`는 실제 값이 아니라 "IObjectSetFilter 객체의 배열이 들어간다"는 자리 표시입니다.

> **중간 요약**: Slate 위젯은 Object View에서 객체 ID와 사용자 정의 파라미터를 받고, 필터 상태는 `postMessage`로 IObjectSetFilter 형식의 메시지를 받아 `slate.getMessage` 핸들러로 변수에 저장합니다.

<a id="triggering-events-from-slate"></a>
### Slate에서 이벤트 트리거하기 (Triggering events from Slate)

Slate가 Object Explorer 안에서 트리거할 수 있는 이벤트 유형은 다음과 같습니다.

* Object Explorer에서 새 객체 탭 열기(객체 RID 사용)
* Object Explorer에서 새 객체 탭 열기(객체 기본 키(primary key) 사용)
* 주어진 객체 집합(object set)에 대해 Object Explorer에서 새 exploration 탭 열기
* Object View에 객체 집합 필터 발행하기
* Object View의 객체 집합 필터 지우기
* 현재 Object View의 데이터 새로 고침
* Object View 필터를 Slate로 다시 보내도록 요청하기

이 이벤트들은 `slate.sendMessage` 액션으로 트리거합니다. 이 액션의 사용자 정의 로직에서 이벤트 메시지 객체를 반환합니다. [이벤트에 대해 자세히 알아보세요.](https://www.palantir.com/docs/foundry/slate/concepts-events/) 각 이벤트의 예상 형식은 아래에 나열되어 있습니다. 이벤트 연동을 디버깅하려면 Object View 편집기의 디버깅 툴바를 사용하세요. post message가 수신되었지만 이벤트 페이로드가 어떤 식으로든 잘못된 경우 경고를 보여 줍니다.

**Object Explorer에서 새 객체 탭 열기(객체 RID 사용)**
이 이벤트는 주로 `objectRid` 파라미터를 사용하지만, Object View를 특정 탭에서 열어야 한다면 선택적으로 `tabId`를 받을 수 있습니다.

```json
{
    "type": "HUBBLE_SLATE_WIDGET // OPEN_OBJECT_BY_RID",
    "payload": {
        "objectRid": "...",
    },
}
```

**설명**: RID(Resource Identifier)는 Foundry가 리소스와 객체마다 부여하는 전역 고유 식별자입니다. Slate가 이 메시지를 반환하면 Object Explorer가 `type`을 보고 "RID로 객체 탭 열기"로 해석한 뒤, `objectRid`에 해당하는 객체의 Object View를 새 탭으로 엽니다. 아래의 다른 이벤트도 `type` 문자열과 `payload` 내용만 다를 뿐 같은 방식으로 동작합니다.

**Object Explorer에서 새 객체 탭 열기(객체 기본 키 사용)**
객체 RID를 모르는 경우, 객체의 기본 키 속성과 객체 타입 ID를 사용해 Object View를 열 수도 있습니다. 메시지 `type`은 `HUBBLE_SLATE_WIDGET // OPEN_OBJECT_BY_PRIMARY_KEY`이고, `payload`에 `objectTypeId`와 `primaryKey` 필드를 넣습니다. (원문에는 이 형식의 JSON 예제가 있습니다.)

**주어진 객체 집합에 대해 Object Explorer에서 새 exploration 탭 열기**
객체 집합을 제공하면 새 검색/exploration 탭을 열 수 있습니다. exploration UI에서 표현하는 데 문제가 생기지 않도록 객체 집합은 복잡도를 제한해야 합니다. 메시지 `type`은 `HUBBLE_SLATE_WIDGET // OPEN_NEW_SEARCH_FOR_OBJECT_SET`이고, `payload`에 `objectSet` 필드를 넣습니다. (원문에는 이 형식의 JSON 예제가 있습니다.)

**Object View에 객체 집합 필터 발행하기**
많은 Object View 위젯은 뷰 안의 다른 위젯에 영향을 주는 필터를 발행할 수 있습니다. Slate 위젯은 이 이벤트로 발행할 필터를 보내서 같은 일을 할 수 있습니다. 가장 최근에 발행한 필터는 같은 Slate 위젯이 이전에 발행한 필터를 모두 대체하므로, 이 필터의 상태는 Slate 안에서 직접 관리해야 합니다. 필터는 Object Set Service API 요청에 쓰는 것과 같은 형식인 Object Set Filter 형식이어야 합니다. 필터는 특정 객체 타입용(`filtersByObjectType`) 또는 전역 속성용(`globalFilters`)으로 제공할 수 있습니다. 메시지 `type`은 `HUBBLE_SLATE_WIDGET // PUBLISH_OBJECT_SET_FILTER`입니다. (원문에는 이 형식의 JSON 예제가 있습니다.)

**설명**: "최근 발행이 이전 발행을 대체한다"는 것은 필터를 누적해서 더하는 방식이 아니라 매번 전체 상태를 덮어쓰는 방식이라는 뜻입니다. 예를 들어 먼저 `status = "Active"` 필터를 발행하고 다음에 `region = "EU"`만 담아 발행하면, 최종 필터는 `region = "EU"` 하나뿐입니다. 두 조건을 모두 걸고 싶다면 Slate가 현재 필터 목록을 변수로 기억하고 있다가 두 조건을 함께 담아 보내야 합니다.

**Object View의 객체 집합 필터 지우기**
이 이벤트로 Object View에 발행되어 있는 필터를 빠르게 지울 수 있습니다. 페이로드가 필요 없습니다. 메시지 `type`은 `HUBBLE_SLATE_WIDGET // CLEAR_PUBLISHED_FILTERS`입니다.

**현재 Object View의 데이터 새로 고침**
Object View에 있는 데이터에 업데이트가 적용되었다면 데이터 새로 고침을 트리거해야 할 수 있습니다. 이 이벤트로 그렇게 할 수 있습니다. 페이로드가 필요 없습니다. 메시지 `type`은 `HUBBLE_SLATE_WIDGET // REFRESH_OBJECT_VIEW`입니다.

**Object View 필터를 Slate로 다시 보내도록 요청하기**
위의 "Object View 필터 접근하기" 섹션에서 설명했듯이, 다른 위젯이 발행해 Object View에 있는 필터는 post message로 Slate에 전송됩니다. Slate 대시보드는 초기화를 마치고 필터를 처리할 준비가 되면 이 이벤트를 발생시켜 필터를 요청해야 합니다. 그러면 Hubble에서 필터를 담은 별도의 이벤트를 보냅니다. 요청할 수 있는 필터는 두 종류입니다. 한 형식은 원래 객체 타입과 관계없이 모든 필터를 담고, 다른 형식은 원래 객체 타입별로 묶은 필터를 담습니다. 이 요청에는 페이로드가 필요 없습니다.

모든 필터를 요청하려면 다음을 보냅니다.

```json
{
    "type": "HUBBLE_SLATE_WIDGET // REQUEST_ACTIVE_FILTERS"
}
```

객체 타입별로 묶은 필터를 요청하려면 `type`을 `HUBBLE_SLATE_WIDGET // REQUEST_ACTIVE_FILTERS_BY_OBJECT_TYPE`로 바꿔 보냅니다.

**설명**: 이 요청 이벤트가 필요한 이유는 타이밍 문제 때문입니다. Object View는 필터가 바뀔 때마다 메시지를 보내지만, Slate가 아직 로드 중이면 그 메시지를 받을 핸들러가 없어 메시지를 놓칩니다. 그래서 Slate가 준비를 마친 시점에 "지금 필터를 다시 보내 달라"고 요청하고, 그 응답을 앞에서 만든 `slate.getMessage` 핸들러로 받습니다. 원문에 나오는 Hubble은 메시지 `type`의 접두어 `HUBBLE_SLATE_WIDGET`에서 볼 수 있듯이 Object Explorer 쪽을 가리키는 이름입니다.

> **중간 요약**: Slate는 `slate.sendMessage` 액션으로 정해진 `type`의 메시지를 반환해 Object Explorer의 탭 열기, 필터 발행과 지우기, 새로 고침, 필터 재전송 요청을 트리거합니다. 필터 발행은 매번 이전 상태를 덮어씁니다.

<a id="media-preview"></a>
## 미디어 미리보기 (Media Preview)

이 위젯은 첨부 파일(attachment) 속성 또는 어떤 미디어(이미지, PDF 등)의 URL을 담은 속성을 받아, 미디어 파일 하나를 크게 인라인으로 미리 보여 줍니다.

![미디어 미리보기](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-media-preview.png)

<a id="configuration"></a>
### 구성 (Configuration)

Media Preview 위젯을 사용하려면 현재 보고 있는 객체에 첨부 파일 속성이 포함되도록 구성해야 합니다. 첨부 파일 속성은 관련 미디어를 Foundry 안에 저장하며, 미디어가 추가된 객체의 권한을 상속받아 올바르게 권한이 적용되도록 보장합니다. 첨부 파일 속성에 미디어를 추가하는 방법은 [이 페이지](../../../02_define-ontologies/03_action-types/16_upload-attachments.md)를 참조하세요.

또는 속성에 저장된 URL을 사용해 Foundry에 이미 있는 미디어를 Media Preview 위젯으로 표시할 수도 있습니다. Object View를 보는 사용자는 객체와 미디어가 저장된 위치 모두에 접근 권한이 있어야 합니다. Object View에 미디어를 추가하려면 다음 단계를 따릅니다.

1. **Foundry에 미디어 업로드:** 데이터셋은 임의의 파일 모음을 저장하는 방법으로 사용할 수 있습니다. 이런 데이터셋을 만들려면 먼저 파일을 폴더에 업로드하고, 나타나는 팝업에서 **Bundle all files as a single dataset**을 선택합니다. 파일 하나만 업로드하는 경우 이 옵션은 **Upload to a dataset without a schema**로 표시됩니다.

![파일을 데이터셋으로 업로드](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-upload-files.png)

이 데이터셋을 만든 뒤에는 필요에 따라 파일을 더 추가할 수 있습니다. 데이터셋 미리보기 오른쪽 위의 **Import**를 클릭합니다.

![추가 파일 가져오기](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-import-additional-files.png)

나타나는 대화 상자에서 업로드할 추가 파일을 선택합니다.

![추가 파일 업로드](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-upload-additional-files.png)

2. **URL 열 추가:** 현재 보고 있는 객체의 백킹 데이터셋(backing dataset)에, 각 행에 대응하는 미디어 파일의 URL을 담은 새 열을 추가합니다. URL은 다음 형식이어야 합니다: `https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/transactions/{transaction rid}/{filename}` 또는 `https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/{dataset rid}/views/{branch name}/{filename}`
   * 예: `https://{my-foundry-url}/foundry-data-proxy/api/web/dataproxy/datasets/ri.foundry.main.dataset.39ce332b-1d74-40ca-be35-5a5b48459a9a/transactions/ri.foundry.main.transaction.00000000-0000-30d2-8067-4b5d9c819f4c/sample-doc.pdf`
   * 참고: PDF를 사용하는 경우 URL은 `/foundry-data-proxy/api/web/dataproxy`가 아니라 `/foundry-data-proxy/api/dataproxy`로 시작해야 합니다.
3. **온톨로지에서 열을 `hubble:media_url`로 표시:** 온톨로지에서 이 열에 대한 속성을 만들고, kind = `hubble`, name = `media_url`인 타입 클래스(Typeclass)를 지정합니다.
   * 기타 미디어 타입 클래스: 그 밖에 `hubble:icon`과 `hubble:thumbnail`도 쓸 수 있습니다. 각각 이 URL을 객체의 아이콘으로, 또는 검색 결과 카드의 썸네일로 사용합니다.
4. **Object Explorer의 Object View에 미디어 위젯 추가:** 현재 기본 제공 미디어 위젯은 *Media Preview*와 *Media Thumbnails* 두 종류입니다. Object View를 편집하면서 **Add Section**을 클릭하면 각 섹션 유형의 설명을 볼 수 있습니다. 이 위젯은 **Media Property**, 즉 미리 볼 미디어의 URL을 담은 속성을 설정해야 합니다.

**설명**: URL 형식의 두 경우는 파일을 어떤 버전으로 가리키느냐의 차이입니다. Foundry 데이터셋은 트랜잭션(transaction) 단위로 버전이 쌓이므로, `transactions/{transaction rid}` 형식은 특정 시점의 파일을 고정해서 가리키고, `views/{branch name}` 형식은 해당 브랜치의 최신 상태에 있는 파일을 가리킵니다. 예를 들어 `Document` 객체 타입의 백킹 데이터셋에 `doc_id = D1`, `file_url = .../views/master/manual.pdf` 행이 있으면, D1의 Object View에서 `manual.pdf`가 미리보기로 표시됩니다.

구성할 기타 파라미터는 다음과 같습니다.

* Title(필수): 위젯 헤더에 표시할 제목입니다.
* Icon(필수): 위젯 헤더에 표시할 헤더입니다.
* Help Info: 툴팁에 추가 도움말 정보를 표시합니다.
* Height: 미디어 위젯을 렌더링할 높이(픽셀)입니다.

> **중간 요약**: Media Preview는 첨부 파일 속성이나 미디어 URL 속성을 받아 파일 하나를 크게 보여 줍니다. URL 방식은 파일을 데이터셋에 올리고, URL 열을 추가하고, 그 속성에 `hubble:media_url` 타입 클래스를 붙인 뒤 위젯을 추가하는 순서로 설정합니다.

<a id="hyperlink"></a>
## 하이퍼링크 (Hyperlink)

Hyperlinks 위젯은 웹 페이지로 가는 단순한 링크 역할을 하는 버튼을 만듭니다. Object View에 링크를 원하는 만큼 추가할 수 있으며, 각 링크는 정적(즉 모든 객체 인스턴스에 같은 링크)이거나 객체별 동적 링크일 수 있습니다.

![Hyperlink.png](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hyperlink.png)

<a id="configuration"></a>
### 구성 (Configuration)

1. *Open Link In*: 브라우저의 같은 탭(기본값), 다른 탭, 팝업 창 중 어디서 열지 선택합니다. 팝업은 신뢰성이 낮으며, 브라우저나 설치된 확장 프로그램에 따라 문제가 생기거나 차단될 수 있습니다. 이 설정은 모든 객체에 적용됩니다.
2. *Link Intent*: 링크 버튼의 색상을 정하는 5가지 링크 "의도(intent)"입니다. 버튼에 [Blueprint Intent ↗](https://blueprintjs.com/docs/#core/components/button.css) CSS 클래스가 적용됩니다(기본값은 none).
   1. "None": 회색
   2. "Primary": 파란색
   3. "Success": 초록색
   4. "Warning": 주황색
   5. "Danger": 빨간색
3. *URL Type*: 3가지 URL 구성 유형이 있습니다.
   1. Property: 하이퍼링크 대상으로 사용할 URL을 담은 동적 속성입니다.
      1. 구성 방법: (1) 객체 타입을 선택합니다(보통 현재 보고 있는 객체). (2) 링크를 가져올 속성 열을 선택합니다. 값이 null이면 하이퍼링크 버튼을 숨기는 토글 옵션이 있습니다.
      2. 예를 들어 온톨로지에 `site_URL` 필드가 정의된 "Website" 객체 2개가 있고, 객체 1의 `site_URL`은 `https://palantir.com`, 객체 2의 `site_URL`은 `https://palantir.com/uk`로 설정되어 있을 수 있습니다.
   2. Hardcoded: 모든 객체에 나타나는 정적 URL입니다. URL을 그대로 복사해 붙여 넣고 `https://`가 포함되어 있는지 확인하세요.
   3. Templated: 템플릿 URL을 사용하면 객체의 속성을 바탕으로 링크를 사용자 정의할 수 있습니다. 어떤 속성이든 중괄호 하나 `{ }`로 감싸서 URL에 넣을 수 있습니다.
      1. 예를 들어 보고서 RID가 `report_rid` 속성으로 저장되어 있다면, URL 템플릿 `/workspace/report/{report_rid}`를 사용해 각 객체에 연결된 보고서를 여는 버튼을 만들 수 있습니다.
4. *Link Title*: 하이퍼링크 버튼에 표시되는 텍스트 라벨입니다. 모든 객체에 동일하게 적용됩니다.

**설명**: Templated 방식은 문자열 치환입니다. 객체 X의 `report_rid`가 `ri.report.main.report.123`이면 템플릿 `/workspace/report/{report_rid}`는 `/workspace/report/ri.report.main.report.123`이 됩니다. Property 방식은 URL 전체를 속성 값으로 갖고 있어야 하고, Templated 방식은 URL의 일부만 속성 값으로 채운다는 점이 다릅니다.

**자주 발생하는 문제와 참고 사항:**

* 하이퍼링크가 깨져 있으면 사용자는 Object Explorer의 첫 화면(landing page)으로 리디렉션됩니다.

> **중간 요약**: Hyperlink 위젯은 열기 위치, 버튼 색상, URL 유형(속성, 고정값, 템플릿), 버튼 라벨을 설정해 링크 버튼을 만듭니다.

<a id="linked-files"></a>
## 링크된 파일 (Linked Files)

Linked Files 위젯을 사용하면 리소스 선택기로 Foundry에 이미 있는 파일을 찾아 선택하거나, 로컬 컴퓨터에서 새 파일을 Foundry에 업로드해서, 보고 있는 객체를 파일에 링크할 수 있습니다.

![링크된 파일](https://www.palantir.com/docs/resources/foundry/object-views/widgets_hu-linked-compass-resources.png)

<a id="configuration"></a>
### 구성 (Configuration)

이 섹션에는 사용자 정의 옵션이 없습니다. Format 탭에서 제목과 기타 일반 서식은 바꿀 수 있습니다.

**자주 발생하는 문제와 참고 사항:**

* 이 위젯으로 업로드한 파일은 온톨로지의 일부로 라이트백되지 않습니다. 즉 현재 객체의 속성으로 저장되지 않습니다. 그렇게 하려면 대신 라이트백이 있는 Foundry Forms 사용을 고려하세요.
* 현재 두 옵션 중 하나를 숨기는 방법이 없으므로, 항상 "Upload files"와 "Link new file"이 모두 표시됩니다.
* 현재 파일 업로드의 기본 저장 위치를 설정하는 방법이 없으므로, 사용자는 업로드할 때마다 Foundry 안의 저장 위치를 찾아 선택해야 합니다.

<a id="iframe"></a>
## Iframe

Slate 대시보드나 다른 Foundry 애플리케이션의 인라인 프레임을 Object View에 "웹 페이지 안의 웹 페이지"로 임베드할 수 있습니다. iframe을 사용하면 현재 객체의 값을 Slate의 필터 변수나 Contour의 파라미터로 전달할 수 있습니다.

<a id="configuration"></a>
### 구성 (Configuration)

iframe을 임베드하려면 아래 설명대로 Handlebar 문법을 사용해 올바른 Foundry 주소로 링크를 구성해야 합니다.

1. **필수:** 임베드할 페이지의 전체 링크를 복사하고 `/workspace/` 앞의 텍스트를 모두 지웁니다.
   * Report 예: `https://EXAMPLE.palantirfoundry.com/workspace/report/ri.report.main.report.ABCDEF-1234-5678`이라면 `/workspace/report/ri.report.main.report.ABCDEF-1234-5678`만 남깁니다.
   * Slate 예: `https://EXAMPLE.palantirfoundry.com/workspace/slate/documents/SLATE_DOCUMENT_NAME`이라면 `/workspace/slate/documents/SLATE_DOCUMENT_NAME`만 남깁니다.
2. **필수:** 전체 보기를 그대로 보여 주려면 `embedded=true`를 추가합니다. `embedded=true`가 유일한 구문이면 앞에 `/?`를, 다른 구문에 이어 붙이면 `&`를 붙입니다.
   * Report 예: `/workspace/report/ri.report.main.report.ABCDEF-1234-5678/?embedded=true`
   * Slate 예: `/workspace/slate/documents/SLATE_DOCUMENT_NAME/latest?&embedded=true`
3. **선택:** Slate에 값을 전달해 특정 변수나 파라미터로 필터링합니다. Object Explorer의 객체 타입 ID, 특정 객체 ID, 또는 특정 속성 ID를 사용합니다. `&`를 쓰고, Slate에 주입할 값을 `{{propertyID}}`처럼 이중 중괄호 안에 적습니다. 이는 Handlebar 문법을 기반으로 합니다.
   * Report 예: `/workspace/report/ri.report.main.report.ABCDEF-1234-5678/?PARAMETER_NAME={{propertyID}}&embedded=true`
   * Slate 예: `/workspace/slate/documents/SLATE_DOCUMENT_NAME/latest?VARIABLE_NAME={{propertyID}}&embedded=true`

**설명**: 이 URL은 HTTP 쿼리 문자열 규칙을 따릅니다. 경로 뒤의 `?`부터 쿼리 문자열이 시작되고, `이름=값` 쌍은 `&`로 구분됩니다. `{{propertyID}}` 부분은 Object View가 렌더링될 때 현재 객체의 실제 속성 값으로 치환됩니다. 예를 들어 `tail_number` 속성 값이 `N123`인 객체에서 `?TAIL={{tail_number}}&embedded=true`는 `?TAIL=N123&embedded=true`가 되고, Slate는 `TAIL` 변수로 `N123`을 받습니다.

<a id="other-configurations"></a>
#### 기타 구성 (Other configurations)

* 표준 iframe과 헤더 없는(headerless) iframe의 차이는 헤더 없는 iframe이 위젯의 헤더를 숨긴다는 점입니다. 위젯 헤더에는 보통 아이콘, 제목, 그리고 구성의 **Format** 탭에서 위젯에 제목을 추가하는 옵션이 들어 있습니다.
* iframe 위젯에서는 위젯의 높이를 설정할 수 있습니다. 기본값은 500이며 직접 조정합니다.
* iframe을 설정하면 Object View에서 위젯 아래에 도우미 창이 표시됩니다(편집 모드에서만 표시). 도우미 창에는 객체별 힌트가 들어 있으며, Slate와 다른 Foundry 애플리케이션에 어떤 속성과 ID를 전달할 수 있는지 보여 줍니다.
* URL에 `&__rp_headerBar=hidden`을 추가하면 보고서 헤더를 숨길 수 있습니다.
* Foundry 외부의 웹사이트 임베드는 보안 및 정책 요구 사항에 따라 가능할 수도 있습니다. 사용 사례에 꼭 필요하다고 생각되면 Palantir 담당자에게 문의하세요.

> **중간 요약**: Iframe 위젯은 `/workspace/`부터 시작하는 Foundry 경로에 `embedded=true`를 붙이고, 필요하면 `{{속성ID}}`로 현재 객체 값을 쿼리 파라미터로 넘겨 다른 앱을 임베드합니다.

<a id="comments"></a>
## 코멘트 (Comments)

이 위젯은 객체를 두고 협업하는 사용자들을 위한 로컬 대화 상자를 제공하며, (`@user_name`으로 태그해) 다른 사용자를 멘션하는 옵션이 있습니다.

이 코멘트는 객체 자체에 저장되지 않으며, 이후 Foundry 전반에서 이 대화를 검색하거나 재사용할 수 없습니다.

<a id="configuration"></a>
### 구성 (Configuration)

이 섹션에는 사용자 정의 옵션이 없습니다. **Format** 탭에서 제목과 기타 일반 서식은 바꿀 수 있습니다.

<a id="comment-behavior-when-the-source-dataset-changes"></a>
### 원본 데이터셋이 바뀔 때의 코멘트 동작 (Comment behavior when the source dataset changes)

객체 타입의 원본 데이터셋이 변경되면 해당 코멘트 피드가 사라집니다.

<a id="writeback-for-comments"></a>
### 코멘트의 라이트백 (Writeback for comments)

이 위젯으로 추가한 코멘트는 온톨로지의 일부로 라이트백되지 않습니다. 즉 이 코멘트는 현재 객체의 속성으로 저장되지 않습니다. 코멘트 검색, 분석, 코멘트로부터의 학습이 필요한 사용 사례라면 액션 사용을 고려하세요.

> **중간 요약**: Comments 위젯은 Object View 안의 로컬 대화창일 뿐 객체에 저장되지 않으며, 원본 데이터셋이 바뀌면 사라집니다. 코멘트를 데이터로 활용하려면 액션을 써야 합니다.

## 정리

- 앱과 파일 위젯은 Quiver, Slate, Report 같은 다른 앱과 미디어, 링크, 파일, 코멘트를 Object View에 넣는 위젯입니다.
- Slate 위젯은 파라미터와 `postMessage` 기반 이벤트로 Object View와 필터 및 탐색 동작을 주고받습니다.
- Media Preview는 첨부 파일 속성이나 `hubble:media_url` 타입 클래스가 붙은 URL 속성으로 미디어를 보여 주고, Hyperlink와 Iframe은 속성 값을 URL에 넣어 객체별 링크와 임베드를 만듭니다.
- Linked Files와 Comments는 객체에 라이트백되지 않으므로, 데이터로 재사용하려면 액션(첨부 파일, 라이트백)을 사용해야 합니다.
- 더 정교한 화면이 필요하면 Workshop 기반 탭이 권장됩니다.
