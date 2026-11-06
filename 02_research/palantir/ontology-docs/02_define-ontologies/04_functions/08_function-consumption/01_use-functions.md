# 플랫폼에서 함수 사용하기 (Use functions in the platform)

- 원문: https://www.palantir.com/docs/foundry/functions/use-functions/
- 사이드바 위치: Define Ontologies > Functions > Function consumption > Use functions in the platform

이 페이지는 작성하고 게시한 함수(function)를 Foundry의 여러 애플리케이션에서 실제로 호출하는 지점을 모아 보여 줍니다. Workshop의 변수(variable), 표, 차트, 액션 타입의 편집 로직과 부수 효과(side effect), Slate, Quiver, Automate에서 함수가 각각 어떤 역할을 하는지 다룹니다. 함수를 만든 다음 "어디에 꽂아 쓰는가"를 한눈에 파악하는 목록 성격의 페이지입니다.

이 섹션은 Foundry 플랫폼 전반에서 함수를 사용할 수 있는 다양한 방법을 정리합니다. 이 목록은 대체로 최신 상태로 유지되지만, 여기 담기지 않은 다른 사용 방법이 있을 수도 있습니다.

<a id="workshop"></a>
## Workshop

[Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)은 다양한 방식으로 함수와의 통합을 지원하므로, Workshop으로 만든 모듈 곳곳에서 사용자 정의 로직을 쓸 수 있습니다.

<a id="variables"></a>
### 변수 (Variables)

대부분의 Workshop [변수](https://www.palantir.com/docs/foundry/workshop/concepts-variables/)는 함수 기반(Function-backed)으로 만들 수 있습니다. 즉, 애플리케이션 제작자가 함수로 값을 계산하고 그 값을 Workshop 전체에서 쓸 수 있습니다. 기본적으로 변수의 값은 그 변수가 의존하는 다른 변수가 갱신되면 다시 계산됩니다. 이 덕분에 사용자 입력에 따라 값을 유연하게 재계산할 수 있습니다. 예를 들어 사용자가 입력 컴포넌트를 수정하면, 그 값에 의존하는 함수 기반 객체 집합(Object Set) 변수가 자동으로 재계산됩니다.

**참고**: 함수 기반 변수는 같은 입력에 대해서는 다시 계산하지 않고 결과를 캐시해 둡니다. 변수의 [재계산 동작](https://www.palantir.com/docs/foundry/workshop/concepts-variables/#recompute-variable-value)을 설정하거나, [변수 값 설정(set variable value)](https://www.palantir.com/docs/foundry/workshop/concepts-events/#set-variable-value) 이벤트를 사용해 재계산을 명시적으로 일으킬 수 있습니다.

더 알아보려면 [함수로 Workshop 변수를 받치는 방법에 대한 튜토리얼](https://www.palantir.com/docs/foundry/workshop/functions-use/#function-backed-variables-in-workshop)을 참고하세요.

아래는 Workshop 변수 타입과 이에 대응하는 TypeScript 타입의 매핑입니다. 각 타입의 Workshop 변수는 나열된 유효한 타입 중 하나를 반환하는 함수로 받칠 수 있습니다. [사용 가능한 함수 타입을 더 알아보세요.](../04_types-reference.md)

* Boolean: `boolean`
* String: `string`
* Numeric: `Integer`, `Long`, `Float`, `Double`
* Date: `LocalDate`
* Timestamp: `Timestamp`
* Array: `BaseType[]` 또는 `Set<BaseType>`
* Object Set: `ObjectSet<ObjectType>`(권장), `ObjectType[]`, 또는 `Set<ObjectType>`

**설명**: Workshop 변수는 화면의 위젯끼리 값을 주고받는 저장 칸입니다. 함수 기반 변수는 "이 변수의 값 = 함수(다른 변수들)"로 정의되므로, 스프레드시트에서 셀 수식이 참조하는 셀이 바뀌면 다시 계산되는 의존성 그래프와 같은 방식으로 동작합니다. 예를 들어 날짜 선택 위젯의 값을 입력으로 받아 "그 날짜 이후 출발하는 Flight 객체 집합"을 돌려주는 함수가 있다면, 사용자가 날짜를 바꿀 때마다 표에 보이는 Flight 목록이 바뀝니다. 캐시 때문에 입력이 같으면 다시 호출하지 않으므로, 입력은 같지만 바탕 데이터가 바뀌어 다시 계산해야 할 때는 재계산 설정이나 이벤트를 써야 합니다. 객체 집합 변수를 받칠 때 `ObjectSet<ObjectType>`을 권장하는 것은, 배열은 객체를 모두 메모리에 불러와야 하지만 객체 집합은 필터 조건만 들고 다니다가 필요할 때 조회할 수 있기 때문입니다.

<a id="derived-properties"></a><a id="object-table-derived-properties"></a>
### Object Table: 파생 속성 (Derived properties)

Workshop의 **Object Table** 위젯은 함수 기반 열(column)을 계산하도록 설정할 수 있습니다. 이 열은 사용자 입력에 따라 바뀔 수 있고, 최종 사용자가 표를 스크롤하는 동안 즉석에서 다시 계산됩니다. 이 기능 사용법은 [전체 튜토리얼](https://www.palantir.com/docs/foundry/workshop/widgets-object-table/#function-backed-columns)에서 볼 수 있습니다.

함수 기반 열은 미디어 참조(media reference)를 반환할 수 있습니다. 함수가 `mimeType`과 `reference` 속성을 가진 `mediaReference` 타입을 반환하면, Object Table은 그 결과를 원시 데이터 대신 미디어로 자동 렌더링합니다. 이를 통해 사용자 정의 함수 로직에 따라 표 열에 동적인 미디어를 보여 줄 수 있습니다.

**설명**: 파생 속성은 객체 타입에 실제로 저장된 속성이 아니라 화면에 보여 줄 때 계산하는 값입니다. 예를 들어 Flight 표에 "예정 출발 시각과 실제 출발 시각의 차이(분)" 열을 추가하고 싶은데 데이터셋에 그런 열이 없다면, 함수로 계산해 열로 붙일 수 있습니다. 화면에 보이는 행에 대해서만 계산하므로 스크롤하면서 새 행이 나타날 때 계산됩니다.

<a id="chart-derived-aggregations"></a>
### 차트: 파생 집계 (Chart: Derived aggregations)

Workshop의 **Chart: XY** 위젯은 함수 기반 집계를 사용해 집계 값을 필요할 때 도출하는 기능을 지원합니다. 집계 데이터가 사용자 선택에 따라 달라지게 하고 싶을 때 유용합니다. Chart 위젯에서 함수를 쓰려면 차트 레이어 설정을 클릭하고 *Function aggregation*을 선택하면 됩니다.

![차트에서 함수 사용](https://www.palantir.com/docs/resources/foundry/functions/use-functions-chart.png)

[집계 API 참조](../04_types-reference.md#aggregation-types)가 제공됩니다. 더 고급 사용 사례라면 [TSv1](../13_functions-on-objects/04_create-custom-aggregation.md)이나 [Python](../11_python/04_python-functions-create-custom-aggregation.md)에서 사용자 정의 집계를 계산하는 방법에 대한 문서를 읽어 보세요.

**설명**: 집계(aggregation)는 SQL의 `GROUP BY`와 `COUNT`, `SUM`, `AVG` 같은 연산으로 여러 행을 묶어 요약 값을 만드는 것입니다. 기본 차트는 객체 속성 하나를 기준으로 묶어 개수나 합계를 내지만, 함수 기반 집계를 쓰면 "선택한 공항 기준으로 지연 시간을 가중 평균" 같은 계산을 코드로 정의해 차트의 막대 값으로 쓸 수 있습니다.

> **중간 요약**: Workshop에서는 함수로 변수 값을 계산하거나(의존 변수가 바뀌면 재계산, 같은 입력은 캐시), Object Table에 파생 열을 붙이거나, XY 차트에 사용자 정의 집계를 제공할 수 있습니다.

<a id="actions"></a>
## 액션 (Actions)

[액션 타입](../../03_action-types/01_overview.md)은 애플리케이션이 Foundry 온톨로지의 객체를 변경하고, 외부 알림과 부수 효과(side effect)를 유연하고 안전하게 보낼 수 있게 해 줍니다. 액션 안에서 함수는 완전한 유연성을 제공해, 코드 작성자가 객체를 어떻게 갱신할지 또는 부수 효과를 어떻게 구성할지 정의할 수 있게 합니다.

<a id="function-backed-actions"></a>
### 함수 기반 액션 (Function-backed Actions)

함수 기반 액션은 [온톨로지 편집(Ontology edits)](../09_language-agnostic-features/01_edits-overview.md) API를 사용해 객체를 어떻게 갱신할지에 대한 로직을 정의합니다. 이를 통해 복잡한 편집을 코드로 표현할 수 있습니다. 예를 들어 어떤 시작 객체에 링크된 모든 객체를 갱신할 수 있습니다. [함수 기반 액션을 처음부터 끝까지 사용하는 튜토리얼을 확인하세요.](../../03_action-types/11_function-backed-actions/02_function-actions-getting-started.md)

**설명**: 일반 액션 타입은 "이 객체의 이 속성을 파라미터 값으로 바꾼다" 같은 정해진 규칙만 설정할 수 있습니다. 함수 기반 액션은 그 규칙 대신 함수를 실행해 편집 내용을 만듭니다. 예를 들어 Aircraft 객체 하나를 "정비 중"으로 바꿀 때 그 항공기에 링크된 앞으로의 Flight 객체 10개를 모두 "기체 변경 필요"로 표시하는 일은 반복문이 필요하므로 함수로 작성합니다.

<a id="side-effects-notifications"></a>
### 부수 효과: 알림 (Side effects: Notifications)

액션은 지정된 사용자에게 알림(Notification)을 보내도록 설정할 수 있습니다. 함수를 사용하면 어떤 사용자가 알림을 받을지, 그리고 알림 내용 자체를 계산할 수 있습니다. 이를 통해 객체 안에 저장된 수신자 사용자 ID를 불러오거나, 객체 데이터를 바탕으로 이메일 내용을 렌더링하는 등의 유연성을 얻습니다. 더 알아보려면 [알림에 대한 전체 문서](../../03_action-types/12_side-effects/02_notifications.md)와 [함수로 알림을 설정하는 가이드](../09_language-agnostic-features/03_configure-notifications.md)를 참고하세요.

<a id="side-effects-webhooks"></a>
### 부수 효과: 웹훅 (Side effects: Webhooks)

액션은 적용될 때 웹훅(Webhook)을 실행하도록 설정할 수도 있습니다. 웹훅은 Foundry를 다른 시스템과 통합해, 사용자가 적용한 액션이 Foundry 바깥의 API에 다시 쓸(write back) 수 있게 합니다. 함수를 사용해 실행될 웹훅에 보낼 파라미터를 계산할 수 있으므로, 객체 데이터를 바탕으로 웹훅 파라미터를 채우는 워크플로가 가능합니다. [웹훅에 대한 전체 문서를 확인하세요.](../../03_action-types/12_side-effects/04_webhooks.md)

**설명**: 웹훅은 어떤 이벤트가 일어났을 때 미리 정해 둔 외부 URL로 HTTP 요청을 보내는 방식입니다. 예를 들어 Foundry에서 "주문 승인" 액션을 적용하면 사내 ERP 시스템의 `POST /orders/{id}/approve` API를 호출하도록 설정할 수 있고, 함수는 이 요청 본문에 넣을 값(주문 번호, 승인자, 금액 등)을 객체에서 읽어 만들어 줍니다.

> **중간 요약**: 액션에서 함수는 복잡한 객체 편집 로직(함수 기반 액션)을 정의하거나, 알림의 수신자와 내용, 웹훅에 보낼 파라미터를 계산하는 데 쓰입니다.

<a id="slate"></a>
## Slate

[Slate](https://www.palantir.com/docs/foundry/slate/overview/)는 **Platform** 탭에서 함수를 찾아 쓰는 기능을 기본으로 지원합니다. Slate 문서를 편집할 때 Platform 탭을 열고 왼쪽 아래에서 **Foundry Function**을 추가합니다. 그러면 함수를 검색하고, 파라미터를 설정하고, 그 결과를 Slate 문서에서 사용할 수 있습니다.

![Slate에서 함수 사용](https://www.palantir.com/docs/resources/foundry/functions/use-functions-slate.png)

역사적인 이유로 Slate 제품에는 자체적인 "함수(functions)" 개념이 있는데, 이는 각 Slate 문서 안에 들어 있는 JavaScript 로직 조각입니다. 그래서 이 함수 제품은 "Foundry functions"라고 불리고 **Platform** 탭 아래에 있습니다. Slate의 함수 기능은 문서 안에서 빠르고 쉽게 데이터를 가공할 수 있게 해 주지만, 객체를 기본으로 지원하지는 않습니다.

Slate의 함수와 Foundry 함수는 서로 함께 쓸 수 있습니다. 예를 들어 Foundry 함수에서 데이터를 반환받아 Slate 함수에서 가공하거나, Slate 함수로 Foundry 함수에 넘길 파라미터를 계산할 수 있습니다.

**설명**: 이름이 같아 헷갈리기 쉬운 부분입니다. Slate 함수는 브라우저에서 그 문서 안에서만 도는 JavaScript 코드이고, Foundry 함수는 이 문서 묶음에서 다루는, 서버에서 실행되며 온톨로지 객체를 다룰 수 있는 함수입니다.

<a id="quiver"></a>
## Quiver

Quiver의 [객체 집합 플롯(Object set plots)](https://www.palantir.com/docs/foundry/quiver/objects-chart-drilldown/#code-function-categorical-plot)은 Workshop의 Chart: XY 위젯과 같은 바탕 컴포넌트를 사용합니다. 그래서 Quiver 분석에서도 함수 기반 집계를 사용할 수 있습니다.

**Code function object set**(코드 함수 객체 집합)과 **Code function categorical plot**(코드 함수 범주형 플롯) 카드는 객체 파라미터를 받는 함수를 지원합니다. 다른 카드를 참조하거나 카드 편집기에서 객체를 선택해 파라미터 값을 지정합니다.

Quiver 검색 대화 상자에서 코드 함수를 추가할 수도 있습니다. **Code functions** 범주는 객체 집합, 범주형 플롯, 값(value), 시계열(time series) 출력을 지원합니다.

<a id="automate"></a>
## Automate

[Automate](https://www.palantir.com/docs/foundry/automate/overview/)에서는 함수 기반 자동화를 만들 수 있습니다. 이 자동화는 지정한 조건이 충족되면 함수를 자동으로 실행합니다.

함수 효과(Function effect)를 설정할 때 함수를 선택하고 버전을 지정할 수 있습니다. 안정 버전(1.0.0 이상)에 대해서는 호환되는 버전으로 자동 업그레이드되도록 설정할 수 있습니다. Automate의 함수는 비동기로 실행되며 최대 4시간까지 실행될 수 있습니다.

온톨로지 편집을 반환 타입으로 가진 함수는 Automate에서 효과로 쓰일 때 편집이 적용되지 않습니다. 더 알아보려면 [함수 효과 문서](https://www.palantir.com/docs/foundry/automate/effect-function/)를 참고하세요.

**설명**: "호환되는 버전으로 자동 업그레이드"는 시맨틱 버저닝에서 메이저 번호가 같은 새 버전(예: `1.2.0`에서 `1.3.0`)이 게시되면 자동으로 새 버전을 쓰도록 하는 것입니다. 메이저 번호가 바뀌는 버전(`2.0.0`)은 호환되지 않는 변경으로 보고 자동으로 따라가지 않습니다. 또 편집을 반환하는 함수를 Automate에서 실행해도 객체가 바뀌지 않으므로, 자동화로 객체를 바꾸려면 함수 효과 대신 액션 효과를 써야 한다는 뜻으로 이해하면 됩니다(자세한 내용은 링크된 문서 참고).

> **중간 요약**: Slate에서는 Platform 탭의 Foundry Function으로, Quiver에서는 함수 기반 집계와 코드 함수 카드로 함수를 씁니다. Automate는 조건이 충족되면 함수를 비동기로 최대 4시간 실행하지만, 함수가 반환한 온톨로지 편집은 적용하지 않습니다.

## 정리

- 게시된 함수는 Workshop, 액션, Slate, Quiver, Automate 등 여러 애플리케이션에서 호출됩니다.
- Workshop에서는 변수 값 계산, Object Table의 파생 열, XY 차트의 사용자 정의 집계에 쓰이며, 변수 타입별로 반환 가능한 TypeScript 타입이 정해져 있습니다.
- 액션에서는 복잡한 편집 로직을 정의하거나 알림과 웹훅의 내용을 계산합니다.
- Slate의 자체 "함수"는 문서 안의 JavaScript 조각으로, Foundry 함수와 구분되며 서로 조합할 수 있습니다.
- Automate는 함수를 비동기로 실행하며 버전 자동 업그레이드를 지원하지만, 함수가 반환한 편집은 적용하지 않습니다.
