# 링크 병합 구성하기 (Configure link merging)

- 원문: https://www.palantir.com/docs/foundry/vertex/link-merging/
- 사이드바 위치: Applications > Vertex > Configuration > Configure link merging

이 페이지는 두 객체 사이를 오가는 중간 객체(예: 거래 기록)를 별도 노드로 그리지 않고 두 노드를 잇는 엣지 안으로 합쳐 보여 주는 링크 병합(Link Merge) 설정을 설명합니다.

Ontology Manager의 Vertex 온톨로지 Capabilities 섹션에서 **Link Merge를** 구성하면, 객체들이 두 노드 사이의 엣지 안으로 자동 그룹화됩니다. 이 구성은 노드 사이의 거래 흐름(transactional flow)을 시각화하는 데 도움이 되고 그래프 생성을 단순하게 만들어 줍니다.

![링크 병합](https://www.palantir.com/docs/resources/foundry/vertex/optional_ontology_config-link_merge.png)

사용자는 **Search Around** 메뉴의 **link via** 옵션으로 이 기능을 사용할 수 있습니다.

![Search Around의 link via](https://www.palantir.com/docs/resources/foundry/vertex/optional_ontology_config-link_merge2.jpg)

**설명**: 예를 들어 Account 객체 타입과 Transfer(송금) 객체 타입이 있고, Transfer 테이블의 각 행이 `from_account`와 `to_account`를 가진다고 합시다. 링크 병합 없이 그리면 Account A, Transfer T1, T2, T3, Account B가 모두 노드로 나타납니다. 링크 병합을 쓰면 Account A와 Account B 두 노드만 그리고, 둘 사이의 엣지 하나에 T1, T2, T3를 묶어 넣어 "A에서 B로 송금 3건"처럼 흐름을 보여 줍니다. 이 예시는 설명을 위한 것이며 원문의 예시는 아닙니다.

## 정리

- 링크 병합은 Ontology Manager의 Vertex Capabilities에서 **Link Merge로** 구성합니다.
- 구성하면 중간 객체들이 두 노드 사이의 엣지 안으로 자동 그룹화되어 거래 흐름이 간결하게 보입니다.
- 사용자는 **Search Around** 메뉴의 **link via** 옵션으로 이 기능을 사용합니다.
