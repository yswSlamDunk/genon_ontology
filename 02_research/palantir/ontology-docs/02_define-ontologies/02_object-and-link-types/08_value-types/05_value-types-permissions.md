# 값 타입 권한 (Value type permissions)

- 원문: https://www.palantir.com/docs/foundry/object-link-types/value-types-permissions/
- 사이드바 위치: Define Ontologies > Object and link types > Value types > Value type permissions

이 페이지는 값 타입(value type)을 누가 사용하고 누가 만들거나 고칠 수 있는지, 즉 값 타입의 권한이 어떻게 정해지는지 설명합니다. 값 타입 권한은 개별 리소스가 아니라 값 타입이 속한 space의 역할로 결정됩니다.

## 값 타입 권한

값 타입의 권한은 플랫폼 [space](https://www.palantir.com/docs/foundry/platform-security-management/manage-orgs-and-spaces/#spaces)를 통해 관리됩니다. space 안의 모든 값 타입은 자동으로 가져와져(import) 연결된 온톨로지(Ontology)에서 사용할 수 있게 됩니다. 다른 소비자는 사용자가 transforms 프로필이나 파이프라인 입력을 가져오는 것과 비슷한 방식으로, 값 타입을 자신의 프로젝트 범위(project scope)로 가져올 수 있습니다.

space에 대한 View(읽기) 권한이 있는 사용자는 그 space와 연결된 온톨로지의 속성(property) 타입이나 공유 속성(shared property) 타입에 값 타입을 지정할 수 있습니다. space의 Editor 또는 Owner는 그 space에서 값 타입을 생성, 편집, 삭제할 수 있습니다.

**설명**: 정리하면 권한은 두 단계입니다. 예를 들어 space의 Viewer인 사용자 A는 속성 구성 화면에서 "email" 값 타입을 골라 쓸 수 있지만 "email" 값 타입의 정규 표현식을 바꿀 수는 없습니다. 같은 space의 Editor인 사용자 B는 값 타입을 새로 만들거나 고치거나 지울 수 있습니다. 값 타입은 여러 곳에서 공유되므로, 사용 권한과 수정 권한을 나눠 소수만 규칙을 바꿀 수 있게 한 구조입니다.

## 정리

- 값 타입 권한은 space 단위로 관리되며, space의 값 타입은 연결된 온톨로지에서 자동으로 사용 가능합니다.
- 다른 소비자는 값 타입을 자신의 프로젝트 범위로 가져와 쓸 수 있습니다.
- space의 View 권한이 있으면 속성과 공유 속성에 값 타입을 지정할 수 있고, Editor나 Owner는 값 타입을 생성, 편집, 삭제할 수 있습니다.
