# 지도 템플릿 (Map templates)

- 원문: https://www.palantir.com/docs/foundry/map/templates/
- 사이드바 위치: Applications > Map > Templates and Workshop widget > Map templates

이 페이지는 입력값(파라미터)만 바꿔 넣으면 분석에 필요한 데이터가 모두 채워진 지도를 자동으로 만들어 주는 지도 템플릿을 다룹니다. 템플릿을 만드는 방법, 파라미터, Search Around, 레이어, 시리즈, 인터페이스 설정, 그리고 URL로 객체를 미리 불러와 템플릿을 사용하는 방법을 설명합니다. 같은 형태의 지리공간 분석을 대상만 바꿔 반복해야 할 때 유용합니다.

지도 템플릿은 사용자가 지리공간 분석 작업에 필요로 할 수 있는 모든 데이터를 갖춘 지도를 생성하는 강력한 도구입니다.

지도 템플릿은 새 지도를 생성하는 데 쓸 수 있고, [위젯](02_widget.md)을 사용해 Workshop 모듈에 임베드할 수도 있습니다.

**설명**: 템플릿과 파라미터의 관계는 함수 정의와 인수의 관계로 볼 수 있습니다. 템플릿은 "공항 객체 하나를 입력받아, 그 공항과 링크된 활주로와 노선을 불러오고, 이 스타일로 그린다"는 정의이고, 사용자가 특정 공항(예: JFK)을 파라미터로 넣으면 그 공항에 대한 지도가 생성됩니다.

<a id="create-a-map-template"></a>
## 지도 템플릿 만들기 (Create a map template)

먼저 생성될 지도가 어떤 모습이기를 원하는지 보여 주는 예시로 일반 지도를 만듭니다. 그런 다음 **Save** 옆의 아래쪽 화살표를 클릭하고 **Save as template...을** 클릭합니다.

<img src="https://www.palantir.com/docs/resources/foundry/map/save-as-template.png" alt="Save as template 옵션" width="265" />

<a id="configure-a-map-template"></a>
## 지도 템플릿 설정하기 (Configure a map template)

<a id="parameters"></a>
### 파라미터 (Parameters)

지도 템플릿에서는 두 종류의 파라미터를 설정할 수 있으며, 이 파라미터는 아래 **Search Around** 설정에 사용할 수 있습니다.

* **Object parameters(객체 파라미터):** 결과 지도를 생성하는 데 사용할 객체 타입을 정의합니다.
* **Non-object parameters(비객체 파라미터):** 기본(primitive) 데이터 타입의 추가 입력을 정의합니다. 예를 들어 `string`, `float`, `double`, `integer`, `long`, `boolean`, `date`, `timestamp` 입력입니다.

![템플릿 파라미터](https://www.palantir.com/docs/resources/foundry/map/template-parameters.png)

<a id="search-arounds"></a>
### Search Around

다음으로 템플릿에 연결된 **Search Around를 설정**할 수 있습니다. 각 객체 파라미터에 Search Around를 연결할 수 있으며, 이는 온톨로지 링크를 사용하는 단순 Search Around이거나 Search Around 함수일 수 있습니다.

Search Around 함수의 비객체 인수는 각각 어떤 값에 매핑할 수 있으며, 그 값은 상수 또는 파라미터일 수 있습니다. 함수 입력을 파라미터에 매핑하려면, 입력 상자 왼쪽의 **Parameter** 버튼을 클릭하고 드롭다운에서 파라미터를 선택합니다.

![템플릿 Search Around](https://www.palantir.com/docs/resources/foundry/map/template-search-arounds.png)

**설명**: 예를 들어 `nearbyAirports(airport, distanceKm)` Search Around 함수를 템플릿에 연결한다고 합시다. `airport`는 객체 파라미터로 채워지고, `distanceKm`는 상수 `50`으로 고정하거나 템플릿의 비객체 파라미터 `radius`에 매핑해 템플릿을 열 때마다 사용자가 입력하게 할 수 있습니다.

<a id="layers"></a>
### 레이어 (Layers)

객체 레이어는 다음과 같이 설정할 수 있습니다.

* **Constant(상수):** 레이어와 그 안의 모든 객체가 그대로 템플릿에 포함됩니다.
* **Styling(스타일):** 이 레이어에 현재 들어 있는 객체는 무시되지만, 레이어의 모든 스타일 설정은 템플릿에 포함됩니다. 이후 이 타입의 객체가 지도에 추가되면(예: 템플릿 Search Around를 통해서나 사용자에 의해), 이 방식대로 스타일이 적용됩니다.
* 또는 레이어의 **X**를 클릭해 레이어를 제거하면 템플릿에 포함되지 않습니다.

오버레이(overlay) 레이어는 템플릿에 포함하거나 제거할 수 있습니다.

<a id="series"></a>
### 시리즈 (Series)

지도에 고정(pin)한 시리즈(series)가 있으면, 결과 템플릿에 그 시리즈를 포함할지 제거할지 선택할 수 있습니다.

<a id="interface"></a>
### 인터페이스 (Interface)

생성되는 지도의 인터페이스는 다음과 같이 설정할 수 있습니다.

* **Workshop module:** 사용자가 선택한 Workshop 모듈로 돌아가는 링크를 볼 수 있게 합니다.
* **Series panel:** 템플릿으로 새 지도를 만들 때 **Series panel**을 기본으로 엽니다.
* **Viewport settings (Fly to objects on map):** 지도에 있는 객체를 중심으로 지도를 자동으로 맞춥니다.

> **중간 요약**: 템플릿은 객체 파라미터와 비객체 파라미터를 정의하고, 객체 파라미터에 Search Around(링크 또는 함수)를 연결하며, 레이어를 상수, 스타일, 제거 중 하나로 정하고, 시리즈와 인터페이스 옵션을 고르는 방식으로 설정합니다.

<a id="use-a-map-template"></a>
## 지도 템플릿 사용하기 (Use a map template)

템플릿을 열면 템플릿 파라미터의 값을 입력하라는 안내가 나타납니다.

URL 쿼리 파라미터를 사용해 객체나 객체 집합(object set)을 템플릿에 미리 불러올 수도 있습니다.

* **단일 객체:** `objectRids` 쿼리 파라미터를 사용합니다. `objectRids=<object_rid>`
* **여러 객체:** 객체 RID를 쉼표로 구분해 `objectRids` 쿼리 파라미터를 사용합니다. `objectRids=<first_object_rid>,<second_object_rid>`
* **객체 집합:** `objectSetRid` 쿼리 파라미터를 사용합니다. `objectSetRid=<object_set_rid>`

**설명**: 쿼리 파라미터는 URL의 `?` 뒤에 붙는 `이름=값` 쌍입니다. 예를 들어 템플릿 주소 뒤에 `?objectRids=ri.a,ri.b`를 붙여 링크를 만들면, 그 링크를 연 사용자는 두 객체가 이미 파라미터로 채워진 상태에서 시작합니다. 다른 애플리케이션에서 "이 객체를 지도에서 보기" 링크를 만들 때 쓸 수 있습니다.

주어진 파라미터 값을 다루려면 상단 도구 모음의 **Parameters**를 클릭합니다. 여기서 어떤 객체 파라미터의 값으로 사용된 모든 객체를 선택하거나, 파라미터 값을 바꿔 지도를 다시 생성할 수 있습니다.

> **중간 요약**: 템플릿을 열면 파라미터 값을 입력하며, `objectRids` 또는 `objectSetRid` URL 쿼리 파라미터로 객체를 미리 채울 수 있고, 상단 **Parameters**에서 값을 바꿔 지도를 다시 만들 수 있습니다.

## 정리

- 지도 템플릿은 예시 지도를 만든 뒤 **Save as template...으로** 저장하며, 새 지도 생성이나 Workshop 임베드에 사용합니다.
- 객체 파라미터와 기본 타입의 비객체 파라미터를 정의하고, 객체 파라미터에 링크 또는 함수 기반 Search Around를 연결합니다.
- 객체 레이어는 Constant(객체째 포함), Styling(스타일만 포함), 제거 중에서 고르며, 오버레이와 고정 시리즈도 포함 여부를 정합니다.
- 템플릿 사용 시 파라미터를 입력하거나 URL 쿼리 파라미터로 객체를 미리 불러오고, **Parameters** 메뉴에서 값을 바꿔 다시 생성합니다.
