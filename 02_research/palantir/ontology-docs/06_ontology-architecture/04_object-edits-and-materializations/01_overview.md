# 객체 편집과 머티리얼라이제이션 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-edits/overview/
- 사이드바 위치: Ontology architecture > Object edits and materializations > Overview

이 페이지는 사용자가 액션으로 객체를 수정하는 일, 즉 객체 편집(edit)이 온톨로지에서 어떤 위치를 차지하는지 소개하는 섹션 입구입니다. 온톨로지의 데이터는 데이터소스에서 오는 값과 사용자가 직접 바꾼 값이 합쳐진 결과이며, 이 섹션의 다른 페이지들은 그 결합이 가능하도록 하는 설정과 내부 메커니즘을 다룹니다.

<a id="object-edits-and-materializations"></a>
## 객체 편집과 머티리얼라이제이션 (Object edits and materializations)

Foundry 온톨로지는 다양한 데이터소스의 데이터와 사용자가 객체에 가한 편집에서 오는 데이터를 결합함으로써, 운영 워크플로를 구동하고 인사이트를 만들어 내며 사용자에게 중요한 대상을 최신 상태로 표현합니다. Foundry 온톨로지에서 사용자는 [액션(Actions)](../../02_define-ontologies/03_action-types/01_overview.md)을 적용해 속성(property) 값을 편집하고, 링크를 추가하거나 제거하고, 객체를 생성하거나 삭제할 수 있습니다.

Foundry에서 액션은 사용자가 정의한 로직에 따라 하나 이상의 객체의 속성을 변경하는 단일 트랜잭션입니다. 액션을 사용하면 개별 속성 편집을 하나하나 쫓아다니는 대신 전체 목표를 생각하면서 데이터를 사용하고 관리할 수 있습니다. 액션은 Foundry 애플리케이션([Workshop](https://www.palantir.com/docs/foundry/workshop/actions-use/), [Object Views](../../05_applications/03_object-views/01_overview.md) 등)에서 실행하거나, [Foundry API](../../02_define-ontologies/03_action-types/04_use-actions.md)를 통해 외부 애플리케이션에서 실행할 수 있습니다. 액션을 설정하고 적용하는 방법에 대한 자세한 내용은 [액션 문서](../../02_define-ontologies/03_action-types/01_overview.md)를 참고하십시오.

이 섹션의 다른 페이지들은 액션을 사용할 수 있도록 객체 타입과 링크 타입에 필요한 설정, 그리고 온톨로지에서 사용자 주도 편집을 가능하게 하는 기반 메커니즘을 다룹니다.

**주의**: [Foundry 스트림 데이터소스를 가진 객체 타입](../02_object-permissioning/04_managing-object-security.md#object-input-data-sources)에서는 아직 액션이 지원되지 않습니다.

**설명**: "단일 트랜잭션"은 데이터베이스의 트랜잭션과 같은 의미입니다. 예를 들어 "티켓 재배정" 액션이 Ticket 객체의 `assignee` 속성을 바꾸고 동시에 Ticket과 새 담당자 Employee 사이의 링크를 추가한다면, 두 변경은 함께 반영되거나 함께 반영되지 않습니다. 또 데이터소스(데이터셋)는 파이프라인이 만들어 내는 값이고 편집은 사용자가 나중에 덧씌우는 값이므로, 온톨로지가 보여 주는 객체는 "데이터셋의 행 + 그 위에 적용된 편집"의 결과입니다. 이 결합된 결과를 다시 데이터셋으로 써내는 것을 머티리얼라이제이션(materialization)이라고 하며, 이 섹션의 뒤쪽 페이지에서 다룹니다.

## 정리

- 온톨로지의 객체는 데이터소스에서 온 데이터와 사용자 편집을 결합한 결과입니다.
- 사용자는 액션을 통해 속성 값 수정, 링크 추가와 제거, 객체 생성과 삭제를 할 수 있습니다.
- 액션은 하나 이상의 객체를 바꾸는 단일 트랜잭션이며 Workshop, Object Views, Foundry API에서 실행할 수 있습니다.
- Foundry 스트림 데이터소스를 가진 객체 타입에서는 아직 액션을 쓸 수 없습니다.
