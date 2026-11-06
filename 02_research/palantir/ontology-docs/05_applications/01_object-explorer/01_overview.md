# Object Explorer 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-explorer/overview/
- 사이드바 위치: Applications > Object Explorer > Overview

이 페이지는 온톨로지에 있는 객체를 검색하고 분석하는 애플리케이션인 Object Explorer를 소개합니다. 온톨로지를 만든 뒤 실제 사용자가 그 데이터를 찾아보고 질문에 답하는 대표적인 화면이므로, 온톨로지가 어떻게 활용되는지 이해하는 출발점이 됩니다.

**Object Explorer**는 온톨로지에 있는 모든 것에 대한 질문에 답하기 위한 검색 및 분석 도구입니다.

* 사용자는 간단한 키워드 검색부터 포괄적인 속성(property) 필터까지 다양한 질의를 직관적인 포인트 앤 클릭(point-and-click) 인터페이스에서 실행해 관심 있는 객체를 쉽게 찾을 수 있습니다. 그런 다음 탐색 뷰(exploration view)로 결과 객체 집합(object set)을 탐색하거나, 결과를 테이블로 보거나, 특정 객체를 선택해 그 [Object View](../03_object-views/01_overview.md)를 볼 수 있습니다.
* 또한 사용자는 객체 집합을 서로 비교하고 대조하며, 객체 집합에 대해 일괄 액션(예: 라이트백(writeback))을 수행하고, 객체 집합을 호환되는 다른 애플리케이션(예: Quiver)에서 열거나 내보낼 수 있습니다. 사용자는 탐색(Exploration)을 저장해 두었다가 언제든 다시 열어 최신 결과를 볼 수도 있습니다.
* 탐색 뷰는 미리 설정되어 있거나 구성 가능한 시각화(예: 차트나 지도)의 모음으로, 사용자는 이를 활용해 특정 객체 부분 집합으로 더 깊이 파고들(drill-down) 수 있습니다.
* Object Explorer는 설정이 거의 필요 없으며, 기술적 배경이 적은 사용자를 대상으로 합니다.

**설명**: SQL로 생각하면 Object Explorer에서 하는 일은 `SELECT * FROM flights WHERE origin = 'JFK'` 같은 질의를 코드 없이 클릭으로 만드는 것입니다. 결과는 행 목록이 아니라 "객체 집합"이라는 단위로 다뤄지고, 이 집합을 차트로 보거나 다른 집합과 비교하거나 액션을 한꺼번에 실행할 수 있습니다. 드릴다운(drill-down)은 차트의 막대 하나를 클릭해 그 조건(예: 출발 공항이 JFK인 항공편)으로 집합을 더 좁혀 들어가는 동작을 말합니다.

[Object Explorer 인터페이스 개요](02_getting-started.md)를 따라가며 시작해 보세요.

[객체와 온톨로지 기반 데이터 모델링의 개념](../../01_ontology-building/04_core-concepts.md)에 대해 더 알아볼 수도 있습니다.

또는 [개별 객체의 Object View를 설정하는 방법](../03_object-views/01_overview.md)을 살펴보세요.

## 정리

- Object Explorer는 온톨로지의 객체를 검색하고 분석하는, 비기술 사용자 대상의 포인트 앤 클릭 도구입니다.
- 키워드 검색과 속성 필터로 객체 집합을 만들고, 탐색 뷰(차트, 지도), 테이블, 개별 Object View로 결과를 봅니다.
- 객체 집합 비교, 일괄 액션, 다른 애플리케이션으로 열기나 내보내기, 탐색 저장을 지원합니다.
