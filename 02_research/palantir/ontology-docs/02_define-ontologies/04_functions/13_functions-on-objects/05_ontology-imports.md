# 객체, 인터페이스, 링크 타입 가져오기 (Import object, interface, and link types)

- 원문: https://www.palantir.com/docs/foundry/functions/ontology-imports/
- 사이드바 위치: Define Ontologies > Functions > Functions on objects > Import object, interface, and link types

이 페이지는 함수(function) 코드에서 온톨로지의 객체 타입, 인터페이스, 링크 타입을 사용하기 위해 이를 함수 저장소가 있는 프로젝트로 가져오는 방법을 설명합니다. 저장소 템플릿(TypeScript v1, TypeScript v2, Python)에 따라 가져온 타입을 어느 패키지에서 import하는지도 정리합니다.

## 가져오기 절차

함수에서 사용하려는 모든 객체 타입, 인터페이스, 링크 타입은 저장소가 들어 있는 프로젝트(Project)로 가져와야 합니다. **Resource Imports** 사이드바를 선택하면 프로젝트로 가져온 객체 타입을 볼 수 있습니다.

![프로젝트로 가져온 객체 타입을 나열하는 Resource Imports 사이드바.](https://www.palantir.com/docs/resources/foundry/functions/ontology-import-side-panel.png)

객체 타입을 더 가져오려면 **Resource Imports** 사이드바에서 **Add** 버튼을 선택해야 합니다. 온톨로지가 선택되어 있지 않으면 온톨로지를 선택하라는 안내가 나타납니다. 가져온 온톨로지 타입이 하나라도 있으면 선택된 온톨로지가 자동으로 결정됩니다.

온톨로지를 선택하면 검색 모달이 나타납니다. 표시되는 온톨로지 내용은 조직(Organization)에서 사용할 수 있는 객체 타입에 따라 다릅니다. 먼저 몇 개의 객체 타입과 그것들을 연결하는 링크 타입을 선택해 보십시오. 이 예제에서는 `Airport`와 `Flight` 객체, 그리고 둘 사이의 링크 타입을 가져옵니다. 여러분의 조직에는 `Airport`와 `Flight` 객체 타입이 없을 수 있으니, 이 단계를 따라 할 때는 접근할 수 있는 아무 객체 타입이나 사용하십시오.

![Airport와 Flight 객체 타입, 그리고 둘 사이의 링크 타입이 선택된 검색 모달.](https://www.palantir.com/docs/resources/foundry/functions/ontology-import-example.png)

**Add** 버튼 아래의 **Interfaces**를 선택하면 온톨로지 인터페이스도 가져올 수 있습니다.

!["Add" 드롭다운 아래에 있는 인터페이스 가져오기 옵션.](https://www.palantir.com/docs/resources/foundry/functions/interface-import-example.png)

**Save**를 선택하면 온톨로지 타입을 프로젝트로 가져옵니다. 새로 가져온 객체 타입과 링크 타입을 반영하도록 코드 바인딩(code binding)을 다시 생성하기 위해 Code Assist가 자동으로 재시작됩니다.

**설명**: 링크 타입은 양쪽 객체 타입이 모두 있어야 의미가 있습니다. 예를 들어 Flight와 Airport 사이의 링크 타입을 가져오면 코드에서 `flight.departureAirport` 같은 링크 탐색이 가능해지는데, 이는 Airport 타입도 함께 가져와야 돌려받은 객체의 타입이 정해집니다. 그래서 예제에서도 두 객체 타입과 그 사이의 링크 타입을 함께 가져옵니다.

> **중간 요약**: Resource Imports 사이드바의 Add에서 온톨로지를 고르고 객체 타입, 링크 타입, 인터페이스를 선택해 Save하면 프로젝트로 가져오고, Code Assist가 재시작되며 코드 바인딩이 다시 생성됩니다.

## 템플릿별 import 패키지

코드에서 이 타입들을 제공하는 패키지는 저장소가 사용하는 템플릿에 따라 다릅니다.

TypeScript v1 저장소에서는 이제 `@foundry/ontology-api` 패키지에서 온톨로지 타입을 import할 수 있습니다. 비공개 온톨로지(private ontology)를 사용한다면 패키지 이름은 대신 `@foundry/ontology-api/<ontology-api-name>`이 됩니다.

TypeScript v2 저장소에서는 온톨로지 타입을 가져온 뒤 [Ontology SDK를 생성](../10_typescript-v2/03_typescript-v2-migration.md#generate-the-ontology-sdk)한 다음 `@ontology/sdk` 패키지에서 import해야 합니다.

Python 저장소에서는 같은 방식으로 [Python Ontology SDK를 생성](../11_python/03_python-functions-on-objects.md#generate-a-python-ontology-sdk)합니다. 그런 다음 객체 타입은 `ontology_sdk.ontology.objects`에서, 객체 집합(object set)은 `ontology_sdk.ontology.object_sets`에서 import합니다.

| 템플릿 | 추가 단계 | import 위치 |
|---|---|---|
| TypeScript v1 | 없음(Code Assist 재시작 시 자동) | `@foundry/ontology-api` (비공개 온톨로지는 `@foundry/ontology-api/<ontology-api-name>`) |
| TypeScript v2 | Ontology SDK 생성 | `@ontology/sdk` |
| Python | Python Ontology SDK 생성 | `ontology_sdk.ontology.objects`, `ontology_sdk.ontology.object_sets` |

(위 표는 원문 내용을 정리하기 위해 번역자가 덧붙인 것입니다.)

TypeScript v1 저장소에서는 Code Assist가 시작되면 `@foundry/ontology-api` 패키지 이름을 `Ctrl` + 클릭해서 사용 가능한 모든 객체 타입을 볼 수 있습니다. 열린 `index.ts` 파일에 코드로 import할 수 있는 유효한 객체 타입이 모두 표시됩니다.

![코드로 import할 수 있는 모든 객체 타입을 나열하는 생성된 index 파일.](https://www.palantir.com/docs/resources/foundry/functions/ontology-api.png)

TypeScript v2나 Python 저장소에서는 생성된 Ontology SDK가 이 참조를 대신하며, 가져온 타입에 대한 코드 자동 완성을 제공합니다.

둘 이상의 온톨로지에 접근할 수 있다면 선택기로 사용할 온톨로지를 고를 수 있습니다. 현재 하나의 프로젝트로 둘 이상의 온톨로지를 가져오는 것은 지원하지 않습니다.

**설명**: 정리하면 한 프로젝트는 하나의 온톨로지에만 연결됩니다. 여러 온톨로지의 타입을 섞어 쓰는 함수는 하나의 프로젝트 안에서 만들 수 없다는 뜻입니다.

## 정리

- 함수에서 쓸 객체 타입, 인터페이스, 링크 타입은 Resource Imports 사이드바의 Add로 프로젝트에 가져와야 합니다.
- 가져오면 Code Assist가 재시작되어 코드 바인딩이 다시 생성됩니다.
- TypeScript v1은 `@foundry/ontology-api`, TypeScript v2는 Ontology SDK 생성 후 `@ontology/sdk`, Python은 Python Ontology SDK 생성 후 `ontology_sdk.ontology.*`에서 import합니다.
- TypeScript v1에서는 패키지 이름을 Ctrl + 클릭해 `index.ts`로 사용 가능한 타입 목록을 볼 수 있습니다.
- 한 프로젝트에 둘 이상의 온톨로지를 가져올 수는 없습니다.
