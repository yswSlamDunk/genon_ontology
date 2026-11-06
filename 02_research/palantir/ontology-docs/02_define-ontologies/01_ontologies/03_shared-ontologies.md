# 공유 온톨로지 (Shared ontologies)

- 원문: https://www.palantir.com/docs/foundry/ontologies/shared-ontologies/
- 사이드바 위치: Define Ontologies > Ontologies > Shared ontologies

이 페이지는 여러 조직(organization)이 하나의 워크플로를 함께 수행할 때 쓰는 공유 온톨로지가 무엇인지 설명합니다. 일반 온톨로지는 한 조직에만 속하기 때문에, 조직 경계를 넘는 협업에는 별도의 온톨로지가 필요합니다.

공유 온톨로지는 여러 [조직(organizations)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/#organizations)이 공유 워크플로에서 협업할 수 있게 해 주는 특별한 종류의 온톨로지입니다. 공유 온톨로지는 해당 워크플로를 위해 따로 만든 전용 공유 [스페이스(space)](https://www.palantir.com/docs/foundry/security/orgs-and-spaces/#spaces) 아래에 존재합니다. 일반 온톨로지는 한 조직에 비공개(private)이며 그 조직의 리소스만 담는 반면, 공유 온톨로지는 여러 조직의 리소스를 하나의 워크플로에서 사용할 수 있게 해 줍니다.

공유 온톨로지는 새 공유 스페이스가 만들어질 때 자동으로 생성됩니다. 공유 온톨로지는 공유 스페이스와 동일한 조직 [마킹(markings)](https://www.palantir.com/docs/foundry/security/markings/)과 [역할 부여(role grants)](https://www.palantir.com/docs/foundry/security/projects-and-roles/#roles)를 가집니다.

워크플로에 공유 온톨로지가 필요한지 비공개 온톨로지가 필요한지 판단하려면 [비공개 온톨로지와 공유 온톨로지를 비교한 예시](01_ontologies-overview.md#private-vs-shared-ontologies)를 참고하십시오.

안전한 협업 워크플로를 구성하는 방법은 [조직 간 협업(cross-organization collaboration)](https://www.palantir.com/docs/foundry/security/cross-organization-collaboration/)에서 자세히 확인할 수 있습니다.

**설명**: 조직(organization)은 Foundry에서 사용자와 리소스를 나누는 최상위 보안 경계이고, 스페이스(space)는 프로젝트들을 담는 상위 공간입니다. 예를 들어 제조사 A와 부품 공급사 B가 공동 재고 관리 워크플로를 운영한다면, 두 조직이 함께 쓰는 공유 스페이스를 만들고, 그 순간 자동으로 생긴 공유 온톨로지에 양쪽의 객체 타입을 올려 함께 사용합니다. 마킹은 데이터에 붙는 접근 제한 표시로, 공유 온톨로지는 공유 스페이스와 같은 마킹과 역할 부여를 물려받으므로 접근 규칙이 스페이스 단위로 일관되게 유지됩니다.

## 정리

- 공유 온톨로지는 여러 조직이 하나의 워크플로에서 리소스를 함께 쓰기 위한 온톨로지입니다.
- 공유 스페이스를 새로 만들면 자동으로 생성되며, 그 스페이스의 조직 마킹과 역할 부여를 그대로 가집니다.
- 일반(비공개) 온톨로지는 한 조직의 리소스만 담습니다. 어느 쪽이 필요한지는 개요 페이지의 비교 예시로 판단합니다.
