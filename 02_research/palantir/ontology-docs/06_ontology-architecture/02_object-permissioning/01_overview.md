# 객체 권한 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-permissioning/overview/
- 사이드바 위치: Ontology architecture > Object permissioning > Overview

이 페이지는 온톨로지의 권한(permission) 구조를 두 수준, 즉 스키마에 해당하는 온톨로지 리소스와 실제 데이터에 해당하는 객체 및 링크로 나누어 소개합니다. 이 구분을 이해해야 "객체 타입은 보이는데 객체는 안 보이는" 상황처럼 권한과 관련된 동작을 해석할 수 있습니다. 각 수준의 자세한 권한 설정은 이어지는 페이지에서 다룹니다.

Foundry 온톨로지는 모든 온톨로지 엔터티에 대해 세분화되고, 견고하며, 유연한 보안 통제를 제공합니다. 이 엔터티에는 [객체 타입](../../02_define-ontologies/02_object-and-link-types/02_object-types/01_object-types-overview.md), [링크 타입](../../02_define-ontologies/02_object-and-link-types/06_link-types/01_link-types-overview.md), [액션 타입](../../02_define-ontologies/03_action-types/01_overview.md)뿐 아니라 [객체와 링크](#objects-and-links)(데이터 자체)도 포함됩니다.

온톨로지의 권한 부여(authorization) 구조는 온톨로지 리소스, 그리고 객체와 링크라는 두 수준으로 개념화할 수 있습니다.

<a id="ontology-resources"></a>
## 온톨로지 리소스 (Ontology resources)

객체 타입, 링크 타입, 액션 타입 같은 온톨로지 리소스는 온톨로지의 스키마를 정의합니다. 예를 들어 객체 타입에는 표시 이름, 속성(property) 이름, 속성 데이터 타입, 설명이 포함될 수 있습니다. 이 리소스들은 실제 속성 값이나 기본 키(primary key) 값을 가리키지 않습니다. 실제 속성 값과 기본 키 값은 객체와 링크에 들어 있습니다.

[온톨로지 리소스의 권한에 대해 더 알아보기.](02_ontology-permissions.md)

<a id="objects-and-links"></a>
## 객체와 링크 (Objects and links)

객체와 링크는 실제 기본 키와 속성 값을 가진, 온톨로지 안의 데이터입니다. 예를 들어 Airplane 객체 타입에는 `Plane ID` 속성 값이 `my_plane_id1`이고 `Maximum Occupancy` 속성 값이 `240`인 객체가 있을 수 있습니다.

[객체와 링크의 권한에 대해 더 알아보기.](04_managing-object-security.md)

**설명**: 관계형 데이터베이스로 보면 온톨로지 리소스 권한은 테이블 정의(`CREATE TABLE airplane (plane_id ..., maximum_occupancy ...)`)를 보거나 고칠 수 있는 권한이고, 객체 권한은 그 테이블의 행(`('my_plane_id1', 240)`)을 읽을 수 있는 권한입니다. 두 권한은 따로 관리되므로, 어떤 사용자는 Airplane 객체 타입의 정의(어떤 속성이 있는지)는 볼 수 있지만 실제 비행기 객체는 하나도 보지 못할 수 있습니다.

## 정리

- 온톨로지 권한은 스키마 수준(온톨로지 리소스: 객체 타입, 링크 타입, 액션 타입)과 데이터 수준(객체와 링크)으로 나뉩니다.
- 온톨로지 리소스는 이름, 속성 이름, 데이터 타입 같은 정의만 담고, 실제 값은 객체와 링크에 있습니다.
- 두 수준의 권한은 따로 설정되며, 각각 이어지는 페이지에서 자세히 다룹니다.
