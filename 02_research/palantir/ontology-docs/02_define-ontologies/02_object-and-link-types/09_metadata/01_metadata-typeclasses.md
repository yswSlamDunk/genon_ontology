# 타입 클래스 (Type classes)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/metadata-typeclasses/
- 사이드바 위치: Define Ontologies > Object and link types > Metadata > Type classes

이 페이지는 속성(property), 링크 타입, 액션 타입에 붙일 수 있는 부가 메타데이터인 타입 클래스(type class)를 설명하고, 알려진 타입 클래스 전체를 표로 정리합니다. 타입 클래스는 온톨로지 자체의 데이터 구조를 바꾸지 않고, 온톨로지를 읽는 애플리케이션(Object Explorer, Quiver, Vertex, Map 등)이 그 값을 어떻게 보여 주고 다룰지 알려 주는 표식입니다. 많은 항목이 지원 중단(deprecated)되었거나 **Capabilities** 페이지로 옮겨졌으므로, 표의 상태 열을 함께 확인해야 합니다.

## 타입 클래스 개요

타입 클래스는 속성, 링크 타입, 액션 타입에 적용할 수 있습니다. [인덱싱](../../../06_ontology-architecture/03_indexing/01_overview.md) 동작에 영향을 주는 `analyzer` 종류의 타입 클래스를 제외하면, 타입 클래스는 온톨로지와 상호작용하는 사용자 애플리케이션이 해석할 수 있는 추가 메타데이터를 정의합니다. 예를 들어 일부 `hubble` 속성 타입 클래스를 지정하면 [Object Views](../../../05_applications/03_object-views/01_overview.md)에서 속성 값이 렌더링되는 방식이 달라집니다.

**설명**: 타입 클래스는 `kind`와 `name` 두 문자열로 이루어진 태그입니다. 예를 들어 어떤 속성에 `kind = hubble`, `name = media_url`을 붙이면, 데이터 자체(문자열 URL)는 그대로이지만 Object View는 이 태그를 보고 그 URL을 이미지나 동영상 같은 미디어로 표시합니다. 프로그래밍 언어의 어노테이션(annotation, 예: Java의 `@Deprecated`)이 코드의 동작이 아니라 그 코드를 읽는 도구의 처리 방식에 정보를 주는 것과 같은 역할입니다. 반면 `analyzer` 종류는 검색 엔진이 텍스트를 어떻게 토큰으로 쪼개 인덱스에 넣을지를 바꾸므로 저장과 검색 동작에 직접 영향을 줍니다.

아래 표는 알려진 타입 클래스 목록입니다. 표의 열은 다음과 같습니다.

* **Deprecated**(지원 중단) 열은 해당 타입 클래스가 여전히 지원되는지를 나타냅니다.
  * **Deprecated** 열은 해당 타입 클래스를 이제 **Capabilities** 페이지에서 설정해야 하는지도 나타냅니다.
    * Ontology Manager에서 객체 타입에는 이제 예전에 타입 클래스로 정의하던 기능을 설정하는 **Capabilities** 페이지가 있습니다. 지원되는 모든 타입 클래스의 설정은 **Capabilities** 페이지로 옮겨질 예정입니다.
* **Type** 열은 타입 클래스가 속성, 링크 타입(예전 이름은 relation), 액션 타입 중 어디에 적용되는지를 나타냅니다.
* **Kind**와 **Name** 열에는 Ontology Manager에서 타입 클래스를 추가할 때 설정하는, 사용자가 정의하는 두 필드의 문자열 값이 들어 있습니다. Foundry 제품들은 이 값을 사용해 타입 클래스를 식별합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/typeclasses-kind-name.png" alt="Add Type Class 화면의 Kind와 Name 필드" width="300" />

* **Description**(설명) 열은 해당 타입 클래스가 추가된 속성 값, 링크, 액션과 상호작용할 때 사용자 애플리케이션이 보여야 할 동작을 설명합니다.
  * [Object Explorer](../../../05_applications/03_object-views/01_overview.md)는 `hubble` 타입 클래스를 사용하는 애플리케이션입니다.
  * [Quiver](https://www.palantir.com/docs/foundry/quiver/overview/)는 `timeseries` 타입 클래스를 사용하는 애플리케이션입니다.

> **중간 요약**: 타입 클래스는 `kind`와 `name` 쌍으로 된 메타데이터 태그로, 주로 애플리케이션의 표시 방식을 제어하며 `analyzer`만 인덱싱에 영향을 줍니다. 많은 타입 클래스가 지원 중단되었거나 객체 타입의 **Capabilities** 페이지로 옮겨지고 있습니다.

## 알려진 타입 클래스 목록

표의 Type 열에서 Property는 속성, Relation은 링크 타입, Action type은 액션 타입을 뜻합니다. Deprecated 열의 "Deprecated"는 지원 중단, "Capabilities 페이지에서 설정"은 객체 타입의 **Capabilities** 페이지에서 설정해야 함을 뜻합니다.

|Deprecated        |Type	|Kind	|Name	| Description	|
|---	|---	|---	|---	|--- |
|	|Property	|hubble	|media\_url	| Object View에 나타날 때 속성을 미디어 항목으로 렌더링합니다. |
|Deprecated	|Property	|hubble	|editable	| Object View에 나타날 때 사용자가 속성을 편집할 수 있게 합니다. 대신 [인라인 편집(inline edits)](../../03_action-types/18_inline-edits.md#object-explorer-inline-edits)을 사용하세요. |
|	|Property	|hubble	|icon	| 속성 값으로 저장된 URL이 객체의 아이콘을 담고 있음을 나타냅니다. |
|Deprecated	|Relation	|hubble	|creatable	| Object View 안의 Linked Objects View 위젯에서 사용자가 특정 링크 타입의 새 객체를 만들 수 있게 합니다. 이 타입 클래스는 relation에 붙이며, 일대다 relation에서 "다(many)" 쪽 타입의 객체를 사용자가 만들 수 있게 합니다. 사용자가 새 링크를 만들 수 있게 하는 지원 방식은 [액션](../../03_action-types/01_overview.md)을 참고하세요. |
|Deprecated	|Property	|hubble	|endorsement\_status:<br>endorsed	| 객체 타입의 기본 키 속성에 추가하면 Object Explorer와 Object Views에서 객체를 `endorsed`(승인됨)로 표시합니다. |
|Deprecated	|Property	|hubble	|endorsement\_status:<br>not\_endorsed	| 객체 타입의 기본 키 속성에 추가하면 Object Explorer와 Object Views에서 객체를 `work in progress`(작업 중)로 표시합니다. |
|Deprecated	|Property	|hubble	|thumbnail	| 속성 값으로 저장된 URL을 검색 결과 카드의 썸네일로 사용합니다. <br><br>이전 버전의 Object Explorer에서만 의미가 있었습니다. |
|Deprecated	|Property	|hubble	|array	| 예전에는 속성이 배열 형식이 되도록 하는 데 쓰였지만, 이제 배열은 Ontology Manager에서 정식으로 지원되는 속성 기본 타입(base type)입니다. |
|Deprecated	|Property	|hubble	|default\_sort\_descending	| Object Explorer에서 열을 내림차순 값으로 자동 정렬합니다. <br><br>이전 버전의 Object Explorer에서만 의미가 있었습니다. |
|Deprecated	|Property	|hubble	|quick\_filter	| Object Explorer 목록 보기에서 이 속성들을 기본 필터로 사용할 수 있었습니다. <br><br>이전 버전의 Object Explorer에서만 의미가 있었습니다. |
|	|Relation	|hierarchy	|parent	| 링크 타입의 링크 방향이 계층 구조의 상위(parent)를 나타냄을 알립니다. 그러면 Object Views가 계층 구조의 Object View 상단에 이동 경로(breadcrumb)를 표시합니다(예: 'Europe -> France -> Paris -> Rue Cler'). |
|	|Property	|choropleth\_map\_<br>config\_id	|\<map\_config\_id>	| 지도에 그릴 수 있는 지리적 지역 값(예: 국가 코드)을 담은 모든 속성 타입에 대해 단계구분도(choropleth)를 만들 수 있습니다. 필요한 타입 클래스의 `kind`는 `choropleth_map_config_id`이고, `name`은 속성에 들어 있는 지역 코드의 종류에 따라 달라집니다.<br><br>예를 들어:<br>- 국가: `countries`<br>- 미국 주(US States): `us_states`<br>- 미국 카운티(US Counties): `us_counties`<br>- 미국 우편번호(US Zip Codes): `us_zip_codes`<br><br>추가 지역 경계 옵션이나 이 타입 클래스 추가에 관한 추가 지원이 필요하면 Palantir 담당자에게 문의하세요.<br><br>설정 옵션으로 집계(aggregation) 방식과 색상 스케일을 바꿀 수 있습니다. <br><br>이 타입 클래스를 사용하려면 속성에 `selectable` 또는 `sortable` 렌더 힌트가 적용되어 있어야 합니다. |
|Deprecated		|Property	|oe\_home\_page\_<br> object\_type\_group	|\<your\_object\_type\_ <br> group\_name>	| 객체 타입의 기본 키 속성에 이 타입 클래스를 추가하면 해당 객체 타입을 그룹에 넣습니다. <br><br>그룹이 중복 생성되지 않도록 철자를 정확히 쓰세요. 이렇게 설정한 객체 타입 그룹은 Object Explorer 홈 페이지에 표시됩니다. <br><br>그룹을 설정한 경우, 그룹에 넣지 않은 숨겨지지 않은 객체 타입은 페이지 맨 아래 "Other" 그룹에 배치됩니다. 이 기능은 객체 타입 그룹(object type groups) 기능으로 대체되었습니다. |
|	|Action type	|hubble-oe	|hide-action	| Object Explorer와 Object Views에서 액션 타입을 숨깁니다. 이 타입 클래스가 없으면 액션 타입은 `Actions` 버튼 드롭다운에 자동으로 나타납니다. |
|   |Action type    |hubble-oe-object-set-rid    | \<object\_type\_RID>   | 동적 객체 집합(object set)을 만들 수 있게 하는 실험적 기능입니다. |
|   |Action type    |hubble-oe-security-rid      | \<compass\_RID>   | 동적 객체 집합을 만들 수 있게 하는 실험적 기능입니다. |
|	|Action type	|actions	|generate\_uuid	| 문자열 파라미터를 UUID로 대체합니다. |
|	|Action type	|actions	|prefill\_current\_user	| 문자열 파라미터를 현재 사용자로 대체합니다. |
|	|Action type	|actions	|view\_object\_with\_type	| 성공 토스트(toast) 알림에 생성되거나 수정된 객체를 보여 줍니다. |
|Deprecated	|Property	|analyzer	|not\_analyzed	| [Lucene ↗](https://lucene.apache.org/)이 속성을 토큰화하지 않도록 합니다. 대시(-) 등을 포함하는 식별자 속성에 사용합니다. <br><br>분석기(analyzer)를 설정하려면 **Properties > Interaction**으로 이동하세요. 여기에 분석기를 고르는 드롭다운이 있습니다.|
|Deprecated	|Property	|analyzer	|simple / standard / whitespace / english / french / japanese / arabic / korean / german / combined\_arabic\_english| 특정 언어와 용도를 위한 분석기입니다. 대부분은 Lucene 내장 분석기로 구현되어 있지만 일부는 사용자 정의 플러그인입니다.<br>Korean과 German은 레거시 [Object Storage v1](../../../06_ontology-architecture/05_object-databases/01_object-storage-v1.md)에서 지원되지 않습니다. <br><br>분석기를 설정하려면 **Properties > Interaction**으로 이동하세요. 여기에 분석기를 고르는 드롭다운이 있습니다.|
|Deprecated	|Property	|analyzer	|not\_indexed	| Lucene이 속성을 인덱싱하지 않도록 합니다. 검색하거나 집계할 필요가 없는 속성에 사용합니다. <br><br> 이 타입 클래스는 더 이상 속성의 인덱싱 여부를 관리하는 데 쓰이지 않습니다. 이 기능은 이제 `searchable` [렌더 힌트](02_metadata-render-hints.md)가 관리합니다. |
|Deprecated	|Property	|multipass	|user\_id	| 값이 Multipass UID인 속성에 적용하면, Object Explorer와 Object Views에서 그 속성을 사용자의 사용자 이름(multipass:given-name과 multipass:family-name 속성으로 구성)으로 렌더링합니다. <br><br>이 타입 클래스는 더 이상 속성을 사용자 이름 형식으로 보여 주는 데 쓰이지 않으며, 이제 Ontology Manager의 값 서식(value formatting) 기능이 Multipass UID를 지원합니다. |
|Deprecated	|Property	|global	|\<your\_property\_id>	| 속성을 전역(global)으로 표시하는 데 쓸 수 있습니다. 이렇게 하면 공통 속성으로 여러 객체 타입을 함께 필터링할 수 있습니다. 단, 이 속성으로 필터링할 각 객체 타입에서 속성들이 같은 property\_id와 global 타입 클래스를 가져야 합니다. <br><br>이전 버전의 Object Explorer에서만 의미가 있었습니다.	|
|Deprecated	|Property	|geo	|geojson	| 속성이 GeoJSON 데이터(예: 다각형, 선 등)를 담고 있음을 나타냅니다. [Map 애플리케이션](../../../05_applications/08_map/01_overview.md)이 이 GeoJSON을 지도에 렌더링합니다. 지원 중단됨: 대신 `geoshape` 속성 타입을 사용하세요.	|
|Deprecated	|Property	|geo	|latitude	| 속성이 [Map 애플리케이션](../../../05_applications/08_map/01_overview.md)에서 사용할 위도를 담고 있음을 나타냅니다. 지원 중단됨: 대신 `geopoint` 속성 타입을 사용하세요. |
|Deprecated	|Property	|geo	|longitude	| 속성이 [Map 애플리케이션](../../../05_applications/08_map/01_overview.md)에서 사용할 경도를 담고 있음을 나타냅니다. 지원 중단됨: 대신 `geopoint` 속성 타입을 사용하세요. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|geo	|altitude	| 속성이 해수면 기준 미터 단위의 고도/표고를 담고 있음을 나타내며, 3D 모드의 [Map 애플리케이션](../../../05_applications/08_map/01_overview.md)에서 사용됩니다. |
|    |Property   |vertex   |link\_merge    | Vertex와 Vortex의 관련 객체 Search Around에서 이 객체를 항상 중간 매개체(intermediary)로 취급합니다. 이 객체는 더 이상 관련 객체(Related Object) 목록에 나타나지 않지만, 이 객체에서 나가는 2차 링크는 나타나며, 이 객체는 그래프에서 간선(edge)으로 렌더링됩니다. 타입 클래스는 객체의 기본 키에 붙입니다.    |
|    |Relation   |vertex   |link\_merge\_incoming    | `link_merge`와 같지만 이 relation에만 적용됩니다. 링크 병합되는 객체는 이 relation의 대상(target/to) 쪽입니다.    |
|    |Relation   |vertex   |link\_merge\_outgoing    | `link_merge`와 같지만 이 relation에만 적용됩니다. 링크 병합되는 객체는 이 relation의 출발(source/from) 쪽입니다.    |
|    |Relation   |vertex   |component    | Vertex 다이어그램에서, 기준 객체에 링크된 객체 중 다이어그램에 사용할 객체를 나타냅니다.    |
|    |Property   |vertex   |component\_subtype    | Vertex에서 객체 타입보다 더 세밀한 그룹화를 가능하게 합니다. 타입 클래스는 객체의 기본 키에 붙입니다.    |
|    |Property   |vertex   |event\_intent.\<intent\_>    | 이벤트(Event)를 Vertex와 Vortex에서 사용하려면 이벤트의 기본 키 속성에 설정합니다. `intent`는 이벤트/경보의 색상과 심각도(danger, warning, primary, success 중 하나)를 나타냅니다. 예: `event_intent.danger`    |
|    |Property   |vertex   |event\_value    | 이벤트의 숫자 값을 나타내는 속성임을 표시합니다.    |
|    |Property   |vertex   |event\_value\_unit.\<unit\_>    | `event_value`와 함께 설정합니다. `unit`은 이벤트 숫자 값의 측정 단위입니다. 예: `event_value_unit.Kilograms`    |
|    |Property   |vertex   |event\_property    | Vertex와 Vortex의 이벤트 카드에 이 속성을 보여 줍니다.    |
|    |Property   |vertex   |min    | 시계열 객체용: 시계열 값이 이 최솟값 아래로 떨어지면 Vertex가 경보를 냅니다. |
|    |Property   |vertex   |max    | 시계열 객체용: 시계열 값이 이 최댓값을 넘으면 Vertex가 경보를 냅니다.    |
|    |Property   |vertex   |threshold\_measure.\<measure\_>    | Vertex에서, 임계값 판정에 사용할 측정 항목(measure)을 나타내기 위해 객체의 기본 키 속성에 설정합니다. 예: `threshold_measure.Temperature`    |
|    |Property   |vertex   |threshold\_high\_limit    | `threshold_measure`와 함께 사용하여 어떤 속성이 임계값 상한을 나타내는지 표시합니다. |
|    |Property   |vertex   |threshold\_low\_limit    | `threshold_measure`와 함께 사용하여 어떤 속성이 임계값 하한을 나타내는지 표시합니다. |
|    |Property   |vertex   |threshold\_exceed\_intent.\<intent\_>    | `threshold_measure`와 함께 객체의 기본 키 속성에 설정합니다. `intent`는 임계값 초과 시의 색상과 심각도(danger, warning, primary, success 중 하나)를 나타냅니다. 예: `threshold_exceed_intent.danger`    |
|    |Property   |vertex   |key\_measure.\<measure\_>    | 여기에 나열한 측정 항목은 Vertex 홈 페이지에 표시됩니다. 예: `key_measure.Temperature`    |
|Deprecated    |Property   |vertex   |enum\_values    | 시계열 객체용: 숫자 값에서 문자열 값으로의 JSON 맵입니다. 이 타입 클래스는 더 이상 지원되지 않습니다.    |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|timeseries\_id	| 시계열 객체의 기본 키에 적용하면, 이 타입 클래스는 그 객체의 *시계열 식별자(series identifier)* (`seriesId`)를 지정합니다. 이 속성은 모든 시계열 객체에 걸쳐 전역적으로 고유해야 하며, 객체가 Quiver에서 검색되도록 하는 데 필요한 유일한 타입 클래스입니다. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|timeseries\_measure	| 시계열 객체의 [측정 항목(measure)](https://www.palantir.com/docs/foundry/quiver/timeseries-overview/)을 지정하는 속성입니다. <br><br>참고: 예전에는 같은 목적으로 `timeseries.timeseries_sensor_type` 타입 클래스를 사용했습니다. 이것도 계속 동작하지만, 일관성을 위해 `timeseries.timeseries_measure`를 사용하세요. |
|Deprecated	|Property	|timeseries	|timeseries\_sensor\_type	| 위의 `timeseries_measure`를 참고하세요. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|timeseries\_units	| 시계열 객체의 *값(value)* 단위를 지정하는 속성입니다(예: 주가 시계열이라면 값 단위가 `dollars`일 수 있습니다). |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|timeseries\_internal\_interpolation	| 시계열 객체의 기본 *내부 보간(internal interpolation)* 방식을 지정하는 속성입니다. 내부 보간은 Quiver가 인접한 데이터 포인트 사이의 시계열 값을 추정하는 방식입니다. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|timeseries\_root\_object\_id	| 시계열 객체의 [루트 객체(root object)](https://www.palantir.com/docs/foundry/quiver/timeseries-overview/)를 지정하는 속성입니다. 각 시계열 객체는 루트 객체를 하나만 가질 수 있습니다. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|timeseries\_is\_enum	| 열거형(enum) 값을 갖는 모든 시계열에 대해 `true`여야 하는 불리언 속성입니다. <br><br>참고: 이 요구 사항은 임시적이며 앞으로 바뀔 수 있습니다. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|timeseries\_is\_deprecated	| 시계열에 대해 `true`로 설정하면 Object Explorer와 Object View 검색 결과에서 그 시계열을 걸러 내는 불리언 속성입니다. <br><br>참고: 이 설정은 Quiver의 결과에서만 이 시계열들을 사후 필터링합니다. 다른 애플리케이션의 검색 결과에는 영향을 주지 않습니다. |
|	|Relation	|timeseries	|parent	| `hierarchy.parent`와 비슷하게, 시계열 객체와 각 상위(parent) 객체 사이의 링크를 기술합니다. |
|   |Property   |timeseries |timeseries\_is\_value\_inverted | 이 불리언 속성을 true로 설정하면 Quiver에서 시계열의 y축 값을 자동으로 뒤집어, 아래로 갈수록 값이 커지게 합니다. 지하 시추 작업의 진행 상황을 시간에 따라 추적하는 경우처럼 시간 대 깊이 시계열을 그릴 때 유용합니다.   |
|   |Property   |timeseries |timeseries\_depth\_units  | 복합 시계열(깊이 시계열, 유정 완결(well completion) 시계열, 광섬유(fiber) 시계열)의 깊이 단위를 담은 속성에 붙입니다. 깊이 시계열과 유정 완결 시계열의 값 단위에는 일반 `timeseries.timeseries_units` 속성을 사용합니다.   |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|event\_id	| 이벤트 객체의 *이벤트 식별자(event identifier)* (`eventId`)를 지정하는 속성입니다. 모든 이벤트 객체에 걸쳐 전역적으로 고유해야 합니다. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|event\_start\_time	| 이벤트 객체의 시작 시각을 지정하는 속성입니다. 이 필드는 시간 값(예: `TIMESTAMP`)이어야 합니다. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|event\_end\_time	| 이벤트 객체의 종료 시각을 지정하는 속성입니다. 이 필드는 시간 값(예: `TIMESTAMP`)이어야 합니다. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|event\_description	| 이벤트 객체의 문자열 설명을 지정하는 속성입니다. 이벤트 객체 타입을 [주석 라이트백(annotation writeback)](https://www.palantir.com/docs/foundry/quiver/timeseries-overview/)에 사용할 경우 필수입니다. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|event\_root\_object\_id	| 이벤트 객체의 [루트 객체](https://www.palantir.com/docs/foundry/quiver/timeseries-overview/)를 지정하는 속성입니다. 각 이벤트 객체는 루트 객체를 하나만 가질 수 있습니다. |
|객체 타입의 <br>**Capabilities** 페이지에서 설정	|Property	|timeseries	|event\_linked\_series\_id	| 이벤트 객체가 관련된 [시계열 객체](https://www.palantir.com/docs/foundry/quiver/timeseries-overview/)를 지정하는 속성입니다. 이 필드에는 단일 문자열뿐 아니라 문자열 배열도 지원됩니다. |

**설명**: 표에 자주 나오는 개념 몇 가지를 정리합니다.

- **토큰화(tokenizing)와 분석기(analyzer)**: 검색 엔진은 텍스트를 저장할 때 단어 단위(토큰)로 쪼개 역색인(inverted index)을 만듭니다. 예를 들어 `standard` 분석기는 `"ABC-123-XY"`를 `abc`, `123`, `xy` 세 토큰으로 나눌 수 있습니다. 그러면 사용자가 `ABC-123-XY` 전체를 정확히 찾으려 할 때 의도와 다른 결과가 섞일 수 있습니다. `not_analyzed`는 값을 쪼개지 않고 통째로 하나의 토큰으로 저장하게 하여, 대시가 들어간 식별자를 정확히 일치 검색할 수 있게 합니다.
- **RID**: Foundry에서 리소스(데이터셋, 객체 타입, 폴더 등)를 전역적으로 구분하는 식별자(Resource Identifier)입니다.
- **시계열 객체와 루트 객체**: 예를 들어 펌프 한 대(`Pump-7`)가 온도 센서와 압력 센서를 갖고 있으면, 각 센서의 측정값 흐름이 시계열 객체가 되고 `Pump-7`이 두 시계열 객체의 루트 객체가 됩니다. `timeseries_measure`는 "Temperature", "Pressure" 같은 측정 종류를, `timeseries_units`는 "celsius", "bar" 같은 값 단위를 지정하는 속성입니다.
- **보간(interpolation)**: 10:00에 20도, 10:10에 30도라는 두 데이터 포인트만 있을 때 10:05의 값을 무엇으로 볼지 정하는 규칙입니다. 직선으로 이으면(선형 보간) 25도, 직전 값을 유지하면 20도가 됩니다.

> **중간 요약**: 표는 `hubble`(Object Explorer/Object View 표시), `hierarchy`(계층), `choropleth_map_config_id`(지도), `actions`(액션 파라미터 자동 채우기), `analyzer`(검색 인덱싱), `geo`(지도 좌표), `vertex`(Vertex 그래프와 경보), `timeseries`(Quiver 시계열과 이벤트) 등 종류별 타입 클래스를 나열합니다. 다수는 지원 중단되어 정식 속성 타입, 렌더 힌트, 값 서식, **Capabilities** 페이지 등으로 대체되었습니다.

## 정리

- 타입 클래스는 속성, 링크 타입, 액션 타입에 붙이는 `kind`와 `name` 쌍의 메타데이터입니다.
- 대부분 애플리케이션(Object Explorer, Quiver, Vertex, Map 등)의 표시와 동작을 제어하며, `analyzer` 종류만 인덱싱 동작에 영향을 줍니다.
- 많은 타입 클래스가 지원 중단되었고, 배열, `geopoint`/`geoshape` 속성 타입, `searchable` 렌더 힌트, 값 서식, 인라인 편집, 액션, 객체 타입 그룹 등 정식 기능으로 대체되었습니다.
- 지원되는 타입 클래스의 설정은 객체 타입의 **Capabilities** 페이지로 옮겨지고 있으며, 시계열과 이벤트 관련 항목 다수가 이미 그곳에서 설정됩니다.
