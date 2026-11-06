# SQL로 객체 분석하기 (Analyze using SQL)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/analyze-sql/
- 사이드바 위치: Applications > Object Explorer > Search and explore objects > Analyze using SQL

이 페이지는 Object Explorer에서 객체 타입을 SQL로 바로 질의해 볼 수 있는 **Analyze using SQL** 기능(베타)을 설명합니다. 사용 방법, 객체 타입을 SQL에서 가리키는 문법, 질의가 가능하기 위한 조건(백킹 데이터소스 또는 머티리얼라이제이션), 데이터 최신성, 지원하는 SQL 방언, 실행 제한을 다룹니다. 데이터베이스 수업에서 배운 SQL로 온톨로지 데이터를 확인할 수 있는 통로입니다.

**참고**: 베타(Beta). 온톨로지 SQL 지원은 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 개발 단계에 있으며, 사용 중인 엔롤먼트에서 이용하지 못할 수도 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다. 온톨로지 SQL 활성화를 요청하려면 Palantir Support에 문의하세요.

**Analyze using SQL** 기능을 사용하면 객체 타입에 대한 빠른 분석을 볼 수 있습니다. 이 기능은 읽기 전용 SQL 질의를 실행할 수 있는 SQL "스크래치패드(scratchpad)"로 구성됩니다. [Dataset Preview](https://www.palantir.com/docs/foundry/sql-warehousing/sql-console/)와 비슷하게 다음 기능을 지원합니다.

* 객체 타입 RID 자동 완성
* 효율적인 `JOIN` 질의를 위해 백틱( \` ) 안에서 다른 객체 타입 검색
* 강조 표시한 질의를 실행하는 키보드 단축키 같은 편집기 친화적 기능 사용
* 실행한 SQL 질의 결과를 미리 보기 표로 출력
* 열과 아래쪽 패널 크기를 원하는 대로 조정

Analyze using SQL을 사용하려면 아래 단계를 따르세요.

1. 탐색(exploration)을 엽니다.
2. 오른쪽 위 메뉴에서 **Analyze using SQL**을 선택해 크기를 조정할 수 있는 미리 보기 패널을 엽니다.
3. **Code** 탭에서 데이터셋에 대한 읽기 전용 질의를 작성합니다.

!["Analyze using SQL" 기능 사용 예시.](https://www.palantir.com/docs/resources/foundry/object-explorer/analyze-sql-example.png)

질의 안에서 객체 타입 이름을 입력해 어떤 객체 타입이든 검색할 수 있습니다. 자동 완성 창이 나타나 객체 타입의 전체 RID를 빠르게 선택하고 채워 넣을 수 있습니다.

![객체 RID 자동 완성 예시](https://www.palantir.com/docs/resources/foundry/object-explorer/object-rid-autofill.png)

또는 다음 문법으로 객체 타입의 API 이름을 사용할 수 있습니다.

```sql
`ontologyApiName`.`objectTypeApiName`
```

![객체 API 이름으로 질의하는 예시.](https://www.palantir.com/docs/resources/foundry/object-explorer/object-api-name-query.png)

다대다 링크 타입을 질의하려면 백틱으로 감싼 링크 타입의 RID(`` `RID` ``)를 사용할 수 있습니다.

**설명**: RID(Resource Identifier)는 Foundry의 모든 리소스에 붙는 전역 고유 식별자로, `ri.ontology.main.object-type.xxxx` 같은 형태입니다. SQL에서는 이 RID나 `온톨로지API이름`.`객체타입API이름`이 테이블 이름 자리에 들어갑니다. 예를 들어 ``SELECT origin, COUNT(*) FROM `myOntology`.`Flight` GROUP BY origin``처럼 쓰면 출발지별 Flight 객체 수를 셀 수 있습니다. 다대다 링크 타입을 따로 질의할 수 있는 이유는, 다대다 관계는 관계형 데이터베이스에서 두 테이블의 기본 키 쌍을 저장하는 조인 테이블(join table)로 표현되기 때문입니다.

> **중간 요약**: **Analyze using SQL**은 탐색 화면에서 객체 타입에 읽기 전용 SQL을 실행하는 스크래치패드입니다. 객체 타입은 RID 자동 완성이나 `` `온톨로지API이름`.`객체타입API이름` `` 형식으로, 다대다 링크 타입은 백틱으로 감싼 RID로 가리킵니다.

<a id="requirements"></a>
## 요구 사항 (Requirements)

Analyze using SQL은 온톨로지 엔터티의 백킹 데이터소스(backing datasource) 또는 머티리얼라이제이션(materialization)을 질의하는 방식으로 동작합니다. 다음 요구 사항에 유의하세요.

* 편집이 비활성화된 온톨로지 엔터티는 데이터소스가 하나여야 합니다.
* 편집이 활성화된 엔터티, 편집 전용 속성(edit-only property)이 있는 엔터티, 또는 데이터소스가 여러 개인 엔터티는 머티리얼라이제이션이 필요합니다.

이 요구 사항을 충족하지 않는 온톨로지 입력을 질의하려고 하면 코드 편집기에 경고가 표시됩니다.

![객체 타입에 머티리얼라이제이션이 필요하다는 코드 편집기 경고 예시.](https://www.palantir.com/docs/resources/foundry/object-explorer/object-needs-materialization-warning.png)

**주의**: 하나의 질의 안에서 표 형식 소스(데이터셋, 테이블, 제한된 뷰(restricted view) 등)와 온톨로지 입력을 섞을 수 없습니다.

**설명**: 객체 데이터는 원본 데이터셋(백킹 데이터소스)에 사용자 편집(edit)이 덧씌워진 결과입니다. 편집이 꺼져 있고 데이터소스가 하나면 원본 데이터셋이 곧 객체 데이터이므로 그대로 질의하면 됩니다. 하지만 편집이 켜져 있으면 원본 데이터셋에는 사용자가 액션으로 바꾼 값이 반영되어 있지 않습니다. 그래서 원본과 편집을 합친 결과를 별도 데이터셋으로 써 둔 머티리얼라이제이션이 있어야 SQL로 정확한 값을 읽을 수 있습니다. 데이터소스가 여러 개인 경우도 여러 데이터셋을 합친 결과가 필요하므로 같은 이유로 머티리얼라이제이션이 필요합니다.

> **중간 요약**: SQL 질의는 백킹 데이터소스나 머티리얼라이제이션을 읽습니다. 편집이 꺼져 있고 데이터소스가 하나면 바로 질의할 수 있지만, 편집이 켜져 있거나 편집 전용 속성이 있거나 데이터소스가 여럿이면 머티리얼라이제이션이 필요합니다. 데이터셋과 온톨로지 입력을 한 질의에 섞을 수 없습니다.

<a id="data-freshness"></a>
## 데이터 최신성 (Data freshness)

편집이 활성화된 객체의 경우, Analyze using SQL은 엔터티의 머티리얼라이제이션을 질의합니다. 따라서 객체에 수행한 편집이나 액션 같은 최근 변경 사항이 질의 결과에 나타나기까지 최대 30초가 걸릴 수 있습니다. 코드 편집기는 출력 표 위에 이 데이터 최신성 지연 시간에 대한 안내를 표시합니다.

<a id="compatibility"></a>
## 호환성 (Compatibility)

SQL 엔진은 **Spark SQL** 방언을 지원합니다. Spark SQL에서는 테이블 이름 같은 식별자를 작은따옴표나 큰따옴표가 아니라 백틱( \` )으로 감싸야 합니다.

아래 예시가 이 문법을 보여 줍니다.

```sql
SELECT column_name FROM \`ri.ontology.main.object-type...\`;
```

Spark SQL 방언과 문법에 대한 자세한 내용은 [공식 Spark SQL 문서 ↗](https://spark.apache.org/docs/latest/sql-ref.html)를 참고하세요.

**설명**: SQL 방언(dialect)은 데이터베이스 제품마다 조금씩 다른 SQL 문법 변형을 말합니다. 예를 들어 PostgreSQL은 식별자를 큰따옴표(`"table"`)로 감싸지만 Spark SQL은 백틱(`` `table` ``)을 씁니다. Spark SQL에서 작은따옴표와 큰따옴표는 문자열 값을 나타내므로, RID를 따옴표로 감싸면 테이블이 아니라 문자열로 해석됩니다. 객체 타입 RID에는 마침표(`.`)와 하이픈(`-`)이 들어 있어 백틱 없이는 식별자로 쓸 수 없습니다.

<a id="query-execution-details-and-limitations"></a>
## 질의 실행 세부 사항과 제한 (Query execution details and limitations)

1. 각 질의는 전체 데이터셋에 대해 실행되며 [Contour](https://www.palantir.com/docs/foundry/contour/overview/)와 같은 연산 백엔드를 사용합니다.
2. 각 질의는 최대 1,000행의 샘플을 반환합니다.
3. SQL 콘솔 사용량은 [리소스 관리(resource management)](https://www.palantir.com/docs/foundry/resource-management/overview/)에서 **Contour**라는 라벨의 소스 아래, 데이터셋 수준으로 집계됩니다.

**설명**: 1번과 2번을 함께 보면, `SELECT * FROM 객체타입`처럼 결과가 100만 행인 질의도 연산 자체는 전체 데이터에 대해 수행되지만 화면에는 최대 1,000행만 돌아옵니다. 반면 `SELECT COUNT(*) ...`처럼 집계하는 질의는 전체 데이터를 대상으로 정확한 결과(한 행)를 돌려줍니다. 따라서 이 기능은 전체 행을 내려받는 용도보다 집계와 빠른 확인 용도에 맞습니다.

> **중간 요약**: 편집이 켜진 객체는 머티리얼라이제이션을 읽으므로 최근 변경이 반영되기까지 최대 30초가 걸립니다. SQL은 Spark SQL 방언이라 식별자를 백틱으로 감싸며, 질의는 전체 데이터에 대해 Contour 백엔드에서 실행되고 결과는 최대 1,000행만 반환됩니다.

## 정리

- **Analyze using SQL**은 Object Explorer 탐색 화면에서 객체 타입에 읽기 전용 SQL을 실행하는 베타 기능입니다.
- 객체 타입은 RID 또는 `` `온톨로지API이름`.`객체타입API이름` ``으로, 다대다 링크 타입은 RID로 질의합니다.
- 편집이 켜져 있거나 데이터소스가 여럿인 엔터티는 머티리얼라이제이션이 있어야 하고, 데이터셋과 온톨로지 입력은 한 질의에 섞을 수 없습니다.
- 편집 반영에는 최대 30초 지연이 있으며, SQL은 Spark SQL 방언(백틱 식별자)을 씁니다.
- 질의는 전체 데이터에서 실행되지만 결과는 최대 1,000행이며, 사용량은 Contour 소스로 집계됩니다.
