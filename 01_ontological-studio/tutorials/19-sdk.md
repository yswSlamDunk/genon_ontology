# 코드 앱 SDK — 직접 읽고 고치기

*분류: 애플리케이션 · 19장 · 원문: <https://www.uengine.org/docs/ontological-studio/sdk.html>*

> 코드 앱에서 사용하는 SDK(`og.js`)의 함수를 살펴보고, 에이전트 없이 앱 코드를 직접 수정해 봅니다. 프로그래밍 수업에서 JavaScript를 조금 써 봤다면 충분합니다.

[▶ 영상: 코드 앱 SDK — 직접 읽고 고치기 — 영상 3:49](https://www.youtube.com/watch?v=KyeVSf67vdA)

## 앱 하나의 구조

```html
<데이터 폴더>/codeapps/<앱 id>/
  ├─ index.html     ← /apps/_runtime/og.css · echarts.min.js 를 싣고 app.js 를 모듈로 부른다
  ├─ app.js         ← Vue 3 앱 (ES 모듈)
  ├─ style.css
  ├─ AGENTS.md, CLAUDE.md   ← 에이전트 규칙 (앱이 아니라 에이전트가 읽는 파일)
```

macOS의 데이터 폴더는 `~/Library/Application Support/Ontological Studio/`입니다. 미리보기 주소는 `/apps/<앱 id>/`이고, 화면 오른쪽 위에 보입니다.

`index.html`은 이렇게 생겼습니다. `/apps/_runtime/…` 줄은 지우지 않습니다.

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <title>지연 선적 보드</title>
  <link rel="stylesheet" href="/apps/_runtime/og.css" />
  <link rel="stylesheet" href="./style.css" />
  <script src="/apps/_runtime/echarts.min.js"></script>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="./app.js"></script>
</body>
</html>
```

## SDK 함수

```javascript
import { query, schema, theme, onTheme, color, actions, act } from '/apps/_runtime/og.js'
```

| 함수 | 하는 일 |
| --- | --- |
| `await query(cypher, params?)` | **읽기 전용** Cypher를 실행하고 행 배열을 반환합니다. 쓰기 절(`CREATE`·`MERGE`·`SET`·`DELETE`)은 서버가 거절합니다. 실패하면 엔진의 메시지로 `Error`를 던집니다. |
| `await schema()` | 발행된 온톨로지의 클래스·속성·관계. 앱이 스스로 둘러볼 때 |
| `theme()` | `'light'` 또는 `'dark'` — Studio의 테마 설정을 따릅니다 |
| `onTheme(fn)` | 테마가 바뀌면 `fn`을 부릅니다. 차트를 다시 칠할 때. 해제 함수를 반환합니다 |
| `color(name)` | 테마 색 토큰의 값. `color('accent')`, `color('fg')` — 캔버스 차트에 넘길 때 |
| `await actions(className?)` | 발행된 액션 목록([20장](20-app-actions.md)) — 0.1.1부터 |
| `await act(opts)` | 계획 → 승인 → 실행 → 취소 창을 띄웁니다([20장](20-app-actions.md)) — 0.1.1부터 |

### query()가 돌려주는 모양

```cypher
const rows = await query('MATCH (s:Supplier) RETURN s.name AS name, s.tier AS tier ORDER BY name')
// → [{ name: 'Hanoi Assembly', tier: 2 }, { name: 'Ningbo Magnetics', tier: 2 }, …]
```

(12장 연습 2로 「한빛정밀」을 추가 인제스천했다면 `{ name: '한빛정밀', tier: 1 }`도 함께 나옵니다.)

- `RETURN`의 이름(`AS`)이 객체의 키가 됩니다. 숫자는 숫자로 옵니다.
- 노드 전체를 반환하면(`RETURN s`) 속성 객체에 `_labels`·`_id`가 붙어 옵니다.
- 값은 문자열로 이어 붙이지 말고 **매개변수**로 넘깁니다. 따옴표 문제와 주입 공격을 막습니다.

```cypher
const pos = await query(
  'MATCH (p:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier) WHERE s.name = $name RETURN p.po_id AS po, p.status AS status',
  { name: 'Shenzhen Goldline PCB' })
```

### 테마 색

`style.css`에서는 색을 이 변수들로만 칠합니다. 그러면 낮/밤이 저절로 따라갑니다.

| 변수 | 쓰임 |
| --- | --- |
| `--og-bg` `--og-panel` `--og-raised` | 바탕, 패널, 떠 있는 카드 |
| `--og-line` | 선, 테두리 |
| `--og-fg` `--og-dim` `--og-mute` | 글자(진함 → 흐림) |
| `--og-accent` `--og-on-accent` | 강조색과 그 위의 글자 |
| `--og-blue` `--og-warn` `--og-danger` `--og-ok` `--og-purple` `--og-soft` | 상태 색 |

## 따라 하기 — 손으로 고치기

에이전트에게 맡기지 않고 직접 한 줄을 고쳐 봅시다. [18장](18-code-app.md)에서 만든 「지연 선적 보드」의 지연 기준을 “1일 넘게”에서 “3일 넘게”로 바꿉니다.

1. 「파일」 탭에서 위치를 확인하고, 데이터 폴더의 `codeapps/<앱 id>/app.js`를 편집기(VS Code 등)로 엽니다.
2. `WHERE s.delay_days > 0`을 `WHERE s.delay_days > 3`으로 바꾸고 저장합니다.
3. Studio의 「미리보기 새로 고침」을 누릅니다. 4건이던 표가 2건(SHP-03, SHP-02)이 됩니다.

> **[팁] 에이전트와 번갈아 고쳐도 됩니다**
>
> 손으로 고친 뒤 말로 이어서 고치라고 해도, 에이전트는 파일을 다시 읽고 이어서 작업합니다. 반대로 에이전트가 고친 코드를 손으로 다듬어도 됩니다. 코드가 곧 앱입니다.

## 차트 하나 더하기 (선택)

ECharts는 전역 `echarts`로 있습니다. 협력사별 미결 금액을 막대로 그려 봅시다. 테마가 바뀔 때 차트를 다시 그리는 부분도 함께 작성합니다.

```cypher
import { query, color, onTheme } from '/apps/_runtime/og.js'

const rows = await query(`
  MATCH (p:PurchaseOrder)-[:ORDERED_FROM]->(s:Supplier) WHERE p.status = 'OPEN'
  RETURN s.name AS supplier, sum(p.amount_usd) AS amount ORDER BY amount DESC`)

const chart = echarts.init(document.getElementById('chart'))
function draw() {
  chart.setOption({
    textStyle: { color: color('dim') },
    xAxis: { type: 'category', data: rows.map(r => r.supplier), axisLine: { lineStyle: { color: color('line') } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: color('line') } } },
    series: [{ type: 'bar', data: rows.map(r => r.amount), itemStyle: { color: color('accent') } }],
  })
}
draw()
onTheme(draw)   // 낮/밤이 바뀌면 다시 칠한다
```

`index.html`에 `<div id="chart" style="height:320px"></div>`를 하나 더해야 합니다.

> **[확인 문제]**
>
> 1. `query('MATCH (s:Supplier) SET s.tier = 1')`을 부르면 어떻게 될까요?
> 2. 사용자가 입력한 협력사 이름으로 발주를 찾을 때, Cypher 문자열에 이름을 이어 붙이면 왜 안 될까요?
> 3. 색을 `#14b8a6`처럼 직접 적으면 무엇이 문제일까요?

> **▼ 정답 보기**
>
> 1. 쓰기 절이 있어 서버가 거절하고, `query()`가 `Error`를 던집니다. 값을 바꾸는 일은 액션으로만 합니다.
> 2. 이름에 따옴표(예: `O'Neil`)가 들어가면 문장이 깨지고, 악의적인 입력이 질의를 바꿀 수 있습니다(주입). `$name` 매개변수로 넘기면 값으로만 다뤄집니다.
> 3. 테마가 바뀌어도 그 색은 그대로라 밤 테마에서 안 보이거나 어색해집니다. `--og-*` 변수나 `color()`를 쓰세요.
