# 필수 속성 (Required properties)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/required-properties/
- 사이드바 위치: Define Ontologies > Object and link types > Properties > Required properties

이 페이지는 값이 반드시 있어야 하는 필수 속성(required property)을 설명합니다. 검증이 언제 일어나는지(인덱싱 시점과 액션 적용 시점), 배열 속성의 처리, 빈 배열을 허용하는 옵션, 그리고 백킹 데이터소스가 여러 개인 객체 타입에서 필수 속성이 비어 있을 수 있는 예외 상황을 예시 표와 함께 다룹니다. 데이터베이스의 `NOT NULL` 제약 조건에 해당하는 기능입니다.

필수 속성은 반드시 값을 가져야 하는 객체 타입 속성입니다. 이 객체 타입 속성 설정을 사용하면 이 속성 값이 null인 객체(배열 속성이라면 빈 배열인 객체)가 없도록 검증할 수 있습니다. 이 검증은 백킹 데이터소스에서 온 데이터와 액션을 통한 편집 모두에 적용됩니다.

**설명**: SQL에서 `CREATE TABLE employee (name VARCHAR NOT NULL)`처럼 열에 `NOT NULL` 제약을 걸면, `name`이 비어 있는 행은 삽입할 수 없습니다. 필수 속성도 같은 규칙을 객체 속성에 적용하며, 배열 속성에서는 빈 배열 `[]`까지 "값이 없음"으로 취급한다는 점이 추가됩니다.

<a id="summary-of-required-properties"></a>
## 필수 속성 요약 (Summary of required properties)

필수 속성을 다룰 때는 다음을 염두에 두세요.

* **검증은 데이터가 객체로 인덱싱될 때 일어남:** null 값 검사는 백킹 데이터소스가 Object Storage로 인덱싱될 때 수행됩니다. 즉 필수 속성을 뒷받침하는 열에 null 값이 있더라도 온톨로지 수정 자체는 성공합니다.
* **배열 속성은 비어 있을 수 없음:** 배열 속성을 필수로 설정하면 항목이 최소 하나 있어야 합니다.
* **액션을 통한 변경은 적용 시점에 검증됨:** 액션으로 속성에 null 값이나 빈 값을 쓰려고 하면 액션 실행이 실패합니다.
* **Object Storage v2에서만 사용 가능:** 필수 속성은 Object Storage v2를 사용하는 객체 타입에서만 지원됩니다.

**설명**: 검증 시점이 두 군데라는 점이 중요합니다. 하나는 데이터셋의 행을 객체 저장소로 옮기는 인덱싱 단계이고, 다른 하나는 사용자가 액션을 실행해 값을 바꾸는 단계입니다. "필수" 설정을 저장하는 순간에는 기존 데이터를 검사하지 않으므로 저장은 성공하지만, 그 뒤 인덱싱에서 null을 발견하면 실패합니다.

<a id="create-a-required-property"></a>
### 필수 속성 만들기 (Create a required property)

1. **Ontology Manager**로 이동합니다.
2. 객체 타입을 선택한 다음, 필수로 설정하려는 속성을 선택합니다.
3. **Create Property**(속성 만들기)를 선택하고 속성 이름, 타입, 설명 등 필요한 세부 정보를 채웁니다.
4. **Configuration** 섹션에서 **Required** 토글을 켭니다.
5. 온톨로지에 변경 사항을 **Save**(저장)하고 재인덱싱이 완료될 때까지 기다립니다.

현재 속성의 백킹 열에 null 값이 하나라도 있으면 재인덱싱이 실패합니다. 이를 해결하려면 백킹 데이터소스를 고쳐 해당 열에 null이 없도록 하거나, 속성의 필수 설정을 해제해야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/required_property.png" alt="구성 창에서 Required 토글을 켠 모습" width="500" />

> **중간 요약**: 필수 속성은 null(배열이면 빈 배열)을 허용하지 않는 속성으로, 인덱싱 시점과 액션 적용 시점에 검증되며 Object Storage v2 전용입니다. Configuration 섹션의 Required 토글로 켜고, 백킹 열에 null이 있으면 재인덱싱이 실패합니다.

<a id="required-properties-that-allow-empty-arrays"></a>
### 빈 배열을 허용하는 필수 속성 (Required properties that allow empty arrays)

필수 속성이 빈 배열을 허용하도록 설정할 수 있습니다. 이 경우 속성은 여전히 null 값은 거부하지만 빈 배열은 받아들입니다. 이 설정은 절대 null일 수 없지만 빈 배열은 허용하도록 설정할 수 있는 필수 통제 속성(mandatory control property)에 유용합니다. [필수 통제 속성](08_mandatory-control-properties.md)에 대해 더 알아보세요.

액션은 파라미터에 매핑되어 있지만 그 파라미터가 설정되지 않은 모든 속성에 빈 배열을 씁니다. 즉 빈 배열을 허용하는 필수 속성이 있고 액션에서 해당 파라미터를 비워 두면, 액션은 성공하고 속성에 빈 배열을 씁니다. 이런 동작을 원하지 않고 사용자가 액션을 통해 항상 이 속성에 값을 설정하도록 강제하고 싶다면, 필수 속성에서 빈 배열을 허용하지 않아야 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/object-link-types/advanced_required_property.png" alt="필수 속성의 고급 설정" width="500" />

**설명**: null과 빈 배열은 다른 값입니다. null은 "값 자체가 없음"이고, `[]`는 "항목이 0개인 배열이라는 값이 있음"입니다. 예를 들어 `tags` 속성이 빈 배열을 허용하는 필수 속성이면 `["urgent"]`와 `[]`는 통과하고 null은 거부됩니다. 액션에서 `tags` 파라미터를 비워 두면 빈 배열 `[]`이 쓰이므로 통과합니다.

> **중간 요약**: 빈 배열 허용 옵션을 켜면 null은 거부하되 `[]`는 허용합니다. 액션은 비워 둔 배열 파라미터에 빈 배열을 쓰므로, 사용자가 반드시 값을 입력하게 하려면 이 옵션을 끄세요.

<a id="required-properties-for-object-types-with-multiple-backing-datasources"></a>
### 백킹 데이터소스가 여러 개인 객체 타입의 필수 속성 (Required properties for object types with multiple backing datasources)

여러 데이터소스가 뒷받침하는 객체 타입에서는 가끔 필수 속성에 null 값이 나타나는 상황을 만날 수 있습니다. 이 현상은 어떤 객체의 레코드가 일부 데이터소스에는 있지만, 필수 속성을 공급하는 데이터소스에는 없을 때 발생합니다.

다음 예시가 이 동작을 보여 줍니다. 백킹 데이터소스가 두 개이고 `Genre` 속성이 필수인 `Movie` 객체 타입이 있다고 가정합니다.

**데이터소스 1 (Datasource 1)**

| Movie Id | Title                | Box office | Regions                    |
| -------- | -------------------- | ---------- | -------------------------- |
| 101      | The Adventure Begins | 200m       | \["USA", "Canada", "UK"]    |
| 102      | Love in the City     | 75m        | \[]                         |
| 103      | Galactic Battles     | 500m       | \["USA", "UK", "Australia"] |

**데이터소스 2 (Datasource 2)**

| Movie Id | Budget | Genre (Required) | Director           |
| -------- | ------ | ---------------- | ------------------ |
| 101      | 50m    | Adventure        | Michael John Smith |
| 102      | 20m    | Romance          | Jane Doe           |
| 103      | 150m   | Sci-Fi           |                    |

새 `Movie`가 두 백킹 데이터소스 모두에 추가되었는데 `Genre` 값이 없다면, 이 객체는 온톨로지에 인덱싱되지 못합니다.

그런데 새 `Movie` 객체에 대한 행이 데이터소스 1에만 있다고 가정해 봅시다.

**데이터소스 1 (Datasource 1)**

| Movie Id | Title                | Box office | Regions                    |
| -------- | -------------------- | ---------- | -------------------------- |
| 101      | The Adventure Begins | 200m       | \["USA", "Canada", "UK"]    |
| 102      | Love in the City     | 75m        | \[]                         |
| 103      | Galactic Battles     | 500m       | \["USA", "UK", "Australia"] |
| 104      | Happy Ending         | 150m       | \["UK", "FRANCE"]           |

**데이터소스 2 (Datasource 2)**

| Movie Id | Budget | Genre (Required) | Director           |
| -------- | ------ | ---------------- | ------------------ |
| 101      | 50m    | Adventure        | Michael John Smith |
| 102      | 20m    | Romance          | Jane Doe           |
| 103      | 150m   | Sci-Fi           |                    |

위 예시는 결과 객체에 필수 속성 값이 없음에도 온톨로지에 성공적으로 인덱싱됩니다.

| 속성 (Property)  | 값 (Value)       |
| ---------------- | ---------------- |
| Movie Id         | 104              |
| Title            | Happy Ending     |
| Box Office       | 150m             |
| Regions          | \["UK", "FRANCE"] |
| Budget           |                  |
| Genre (Required) |                  |
| Director         |                  |

액션 편집으로 만든 객체에도 같은 원리가 적용됩니다. `Movie` 객체가 `Datasource 1`의 열에 연결된 속성만 담고 있다면 생성이나 수정이 성공합니다. 그러나 액션이 `Budget`처럼 `Datasource 2`에서 오는 속성을 객체에 추가하면, 그 액션은 유효하지 않게 되어 실행에 실패합니다. 이제 객체가 `Datasource 2`에도 존재하게 되므로 `Genre`가 반드시 설정되어야 하기 때문입니다.

**설명**: 여러 데이터소스로 객체를 만드는 것은 두 테이블을 기본 키 `Movie Id`로 `LEFT OUTER JOIN` 하는 것과 비슷한 결과를 냅니다. 104번 영화는 데이터소스 1에만 있으므로, 조인 결과에서 데이터소스 2의 열(`Budget`, `Genre`, `Director`)은 모두 NULL이 됩니다. 필수 검사는 "필수 속성을 공급하는 데이터소스에 행이 있을 때 그 행의 값이 비어 있는가"를 보는 것이어서, 데이터소스 2에 행 자체가 없으면 검사 대상이 아닙니다. 액션이 `Budget`을 쓰는 순간 데이터소스 2 쪽에 104번 행이 생기는 것으로 취급되므로, 그때부터는 `Genre`도 함께 써야 합니다.

> **중간 요약**: 백킹 데이터소스가 여러 개이면, 필수 속성을 공급하는 데이터소스에 해당 객체의 행이 아예 없을 때 필수 속성이 비어 있어도 인덱싱이 성공합니다. 액션이 그 데이터소스의 속성을 쓰기 시작하면 필수 속성도 함께 채워야 합니다.

## 정리

- 필수 속성은 null(배열은 빈 배열) 값을 허용하지 않는 속성이며, Object Storage v2에서만 지원됩니다.
- 검증은 저장 시점이 아니라 인덱싱 시점과 액션 적용 시점에 일어나므로, 백킹 열에 null이 있으면 재인덱싱이 실패합니다.
- 빈 배열 허용 옵션을 켜면 null만 거부하며, 액션에서 비워 둔 배열 파라미터는 빈 배열로 쓰입니다.
- 백킹 데이터소스가 여러 개이면, 필수 속성을 공급하는 데이터소스에 행이 없는 객체는 필수 속성이 비어 있어도 인덱싱됩니다.
