# 읽기 전용 모드 (Read-only mode)

- 원문: https://www.palantir.com/docs/foundry/vertex/read-only-mode/
- 사이드바 위치: Applications > Vertex > Graphs > Read-only mode

이 페이지는 Vertex 그래프가 읽기 전용 모드로 열릴 때 어떤 동작이 제한되는지, 그리고 어떤 상황에서 읽기 전용 모드가 적용되는지를 설명합니다. 그래프를 다른 애플리케이션에 임베드해 보여 줄 때 사용자가 그래프를 바꾸지 못하게 하려는 경우에 관련된 내용입니다.

특정 상황에서는 Vertex 그래프가 읽기 전용 모드로 열릴 수 있습니다.
읽기 전용 모드에서는 다음 제한이 적용됩니다.

* 그래프에 새 객체를 추가할 수 없습니다(Search Around를 통한 추가도 포함).
* 그래프 노드의 위치를 다시 배치할 수 없습니다(끌어서 놓기 또는 다른 방법 모두).
* 페이지 상단의 툴바가 숨겨집니다.

**설명**: Search Around는 그래프에 있는 객체에서 링크를 따라가 연결된 객체를 찾아 그래프에 추가하는 탐색 기능입니다. 예를 들어 Aircraft A1 노드에서 Search Around로 Flight 링크를 따라가면 F100, F102 노드가 그래프에 추가됩니다. 읽기 전용 모드에서는 이런 확장도 막히므로, 사용자는 처음 로드된 그래프의 노드와 간선만 그대로 보게 됩니다.

<a id="when-are-vertex-graphs-opened-in-read-only-mode"></a>
## Vertex 그래프는 언제 읽기 전용 모드로 열리나요? (When are Vertex graphs opened in read-only mode?)

아래는 그래프가 읽기 전용 모드로 열리는 상황의 목록이며, 모든 경우를 망라한 것은 아닙니다.

* 그래프가 Workshop에 임베드되어 있고 [위젯 구성](09_embed-graph-workshop.md#configure-the-widget)에서 읽기 전용 모드 설정을 명시적으로 켠 경우.
* 그래프를 [Carbon](https://www.palantir.com/docs/foundry/carbon/overview/)에서 연 경우.
* 그래프가 [Notepad](https://www.palantir.com/docs/foundry/notepad/widgets-vertex-graph/)에 임베드된 경우.

## 정리

- 읽기 전용 모드에서는 객체 추가(Search Around 포함), 노드 재배치가 불가능하고 상단 툴바가 숨겨집니다.
- Workshop 위젯에서 읽기 전용 모드를 켠 경우, Carbon에서 연 경우, Notepad에 임베드된 경우 등에 읽기 전용 모드가 적용됩니다.
