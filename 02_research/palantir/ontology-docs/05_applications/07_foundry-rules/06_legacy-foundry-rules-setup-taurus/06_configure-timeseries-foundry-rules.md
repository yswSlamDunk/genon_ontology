# 시계열 설정 (Configure time series for Foundry Rules)

- 원문: https://www.palantir.com/docs/foundry/foundry-rules/configure-timeseries-foundry-rules/
- 사이드바 위치: Applications > Foundry Rules > Legacy Foundry Rules setup (Taurus) > Configure time series for Foundry Rules

이 페이지는 2022년 7월 이전에 배포한 구버전 Foundry Rules(옛 이름 Taurus)에서 시계열(time series) 규칙을 쓸 수 있도록 추가 설정하는 방법을 다룹니다. Workshop 애플리케이션의 설정, 규칙을 실행하는 트랜스폼(transform) 파이프라인의 추가 입력, 프로젝트 참조 설정을 차례로 설명합니다. 새로 배포하는 경우에는 필요 없는 절차입니다.

**참고**: 2022년 7월 이전의 Foundry Rules(이전 이름 Taurus)는 사용자가 Foundry Rules를 실행하기 위한 트랜스폼을 직접 만들어야 했습니다. 이 섹션은 2022년 7월 이전에 Foundry Rules를 배포한 경우에만 해당합니다.

이 안내는 플랫폼에 시계열이 이미 설정되어 있다고 가정합니다. [Foundry에서 시계열을 사용하는 방법](https://www.palantir.com/docs/foundry/time-series/time-series-usage/)에 대해 더 알아보세요. 새 워크플로를 만드는 경우에는 [Foundry Rules 배포](../03_deploy/01_deploy-foundry-rules.md) 단계를 따르세요. 2022년 7월 이전에 Foundry Rules를 배포했다면, 시계열 지원을 활성화하기 위해 아래에 설명한 추가 단계가 필요합니다.

**설명**: 시계열(time series)은 시각과 값의 쌍이 시간 순서로 이어진 데이터입니다. 예를 들어 펌프 센서가 1초마다 기록한 온도 값 `(2024-01-01 00:00:00, 71.2), (2024-01-01 00:00:01, 71.4), ...` 가 시계열입니다. 트랜스폼은 입력 데이터셋을 읽어 출력 데이터셋을 만드는 Foundry의 데이터 변환 코드입니다. 구버전 Foundry Rules는 이 트랜스폼 안에서 규칙을 실행했기 때문에, 규칙이 시계열을 읽으려면 트랜스폼에 시계열 관련 입력을 추가로 알려 줘야 합니다.

<a id="workshop-application"></a>
## Workshop 애플리케이션 (Workshop application)

Workshop 애플리케이션에서 시계열 규칙 작성을 시작하려면 두 단계가 필요합니다.

1. Rule Editor의 **Enable time series rules**(시계열 규칙 사용) 설정을 켜야 합니다. 이 설정으로 가려면 Workshop 모듈을 편집 모드로 열고, Rule Editor 위젯을 클릭한 다음 **Enable time series rules** 라벨이 붙은 옵션을 찾습니다.

    <img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/time_series_workshop_flag.png" alt="Workshop의 시계열 플래그" width="400" />

2. 시계열 규칙을 만들려면 소스 객체가 루트 객체 타입(root object type)이어야 합니다. 필요한 루트 객체 타입을 모두 **Permitted object types**(허용된 객체 타입) 집합에 추가합니다. 여기에 추가한 모든 객체는 트랜스폼 파이프라인에도 추가해야 합니다.

**설명**: Foundry의 시계열 모델에서 루트 객체는 펌프나 기계처럼 시계열을 가진 대상이고, 센서 객체는 그 대상에 달린 개별 측정 채널(온도 센서, 압력 센서 등)입니다. 루트 객체와 센서 객체는 링크로 연결됩니다. 이 페이지에서 말하는 "루트와 센서 객체 사이의 관계(relation)"가 바로 이 링크 타입입니다.

> **중간 요약**: Workshop에서는 Rule Editor 위젯의 **Enable time series rules**를 켜고, 루트 객체 타입을 **Permitted object types**에 추가해야 시계열 규칙을 작성할 수 있습니다.

<a id="transforms-pipeline"></a>
## 트랜스폼 파이프라인 (Transforms pipeline)

Foundry Rules는 트랜스폼의 일부로 실행됩니다. [파이프라인](04_configure-transforms-pipeline.md) 설정 안내를 이미 따랐는지 확인하세요.

<a id="additional-inputs"></a>
## 추가 입력 (Additional inputs)

이 섹션은 시계열 메타데이터에 접근하기 위한 권한을 제공합니다. 시계열 규칙이 실행되려면 추가 입력(additional inputs)에 다음 항목을 더 넣어야 합니다.

* 시계열 데이터를 뒷받침하는 각 시계열 동기화(time series sync)마다 `.addTimeseriesSyncRids`를 사용해 동기화 RID를 추가합니다.
* 위 시계열 동기화에서 사용하는 각 틱 데이터셋(tick dataset)마다 `.addBackingDatasetRids`를 사용해 틱 데이터셋의 RID를 추가합니다. 이것이 실제 시계열 데이터를 담고 있는 데이터셋입니다.
* `.addObjectRids`를 사용해 루트 객체와 센서 객체의 RID를 추가합니다.
* `.addLinkRids`를 사용해 루트 객체와 센서 객체 사이 관계의 RID를 추가합니다.

**설명**: RID(Resource Identifier)는 Foundry 안의 리소스(데이터셋, 객체 타입, 링크 타입 등)를 유일하게 가리키는 식별 문자열로, `ri.foundry.main.dataset.7041...` 같은 형태입니다. 트랜스폼은 기본적으로 자신이 선언한 입력만 읽을 수 있으므로, 규칙 실행에 필요한 온톨로지 리소스와 시계열 리소스의 RID를 모두 추가 입력으로 선언해야 접근 권한이 생깁니다. 틱 데이터셋은 시계열의 각 측정값(틱)이 한 행씩 저장된 데이터셋입니다.

<a id="example"></a>
### 예시 (Example)

```java
 @AdditionalInputs
    public static Set<InputSpec> additionalInputs = ImmutableOntologyInputs.builder()
        .addObjectRids("ri.ontology.main.object-type.adc4f61c-7ddd-4be2-9ade-a3a0483e63e4") // 루트 객체
        .addObjectRids("ri.ontology.main.object-type.98f40fe0-d36f-4fcc-b36c-dc3824be17b5") // 센서 객체
        .ontologyBranchRid("ri.ontology.main.branch.00000000-0000-0000-0000-000000000000")
        .ontologyRid("ri.ontology.main.ontology.00000000-0000-0000-0000-000000000000")

         // 시계열 입력
        .addLinkRids("ri.ontology.main.relation.6e82c6be-2a9a-42be-9cf0-c84a706b4101") // 루트 객체 <-> 센서 객체
        .addTimeseriesSyncRids("ri.time-series-catalog.main.sync.8023a1b6-bae0-4dbf-8df5-9a879d8e0be0") // 시계열 동기화
        .addBackingDatasetRids("ri.foundry.main.dataset.7041bedc-c475-46f6-81b6-8b989f099447") // 틱 데이터셋
        .addBackingDatasetRids("ri.foundry.main.dataset.7ee6741c-ea3d-48aa-9ba3-ec43b2ce42e4") // 센서 객체의 백킹 데이터셋
        .build()
        .getInputSpecs();
```

**설명**: 이 Java 코드는 `@AdditionalInputs` 애너테이션이 붙은 정적 필드로, 트랜스폼이 추가로 읽을 입력 목록을 빌더 패턴으로 만듭니다. `addObjectRids` 두 줄은 루트 객체 타입과 센서 객체 타입, `addLinkRids`는 둘을 잇는 링크 타입, `addTimeseriesSyncRids`는 시계열 동기화, `addBackingDatasetRids`는 틱 데이터셋과 센서 객체의 백킹 데이터셋을 선언합니다. `ontologyRid`와 `ontologyBranchRid`는 어느 온톨로지와 브랜치를 기준으로 할지 지정합니다. 마지막의 `build().getInputSpecs()`가 이 정보를 트랜스폼 입력 명세(`Set<InputSpec>`)로 변환합니다.

<a id="project-references"></a>
### 프로젝트 참조 (Project references)

[Code Repository](https://www.palantir.com/docs/foundry/code-repositories/ontology-imports/)의 **Settings** 탭에 있는 **Ontology Imports** 도우미를 사용해 루트 객체 타입, 센서 객체 타입, 그리고 둘 사이의 관계를 프로젝트로 가져오는(import) 작업도 필요합니다.

![Code Repository의 Ontology imports 도우미](https://www.palantir.com/docs/resources/foundry/foundry-rules/ontology_imports.png)

또한 시계열 동기화나 그것을 뒷받침하는 틱 데이터셋이 트랜스폼과 같은 프로젝트에 있지 않다면, 프로젝트 뷰의 **Project References** 섹션을 사용해 이들도 프로젝트로 [가져와야](https://www.palantir.com/docs/foundry/compass/move-and-share-resources/) 합니다.

<img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/project_reference_compass_1.png" alt="Rules Workflow 프로젝트 뷰" width="400" />

<img src="https://www.palantir.com/docs/resources/foundry/foundry-rules/project_reference_compass_2.png" alt="Rules Workflow 참조" width="400" />

**설명**: Foundry에서 프로젝트는 리소스와 권한을 묶는 단위입니다. 트랜스폼 코드에 RID를 적는 것만으로는 부족하고, 다른 프로젝트에 있는 리소스는 참조(reference)로 현재 프로젝트에 가져와야 트랜스폼이 실제로 그 리소스를 읽을 수 있습니다.

> **중간 요약**: 트랜스폼의 `@AdditionalInputs`에 객체 타입, 링크 타입, 시계열 동기화, 틱 데이터셋의 RID를 선언하고, Ontology Imports와 Project References로 관련 리소스를 프로젝트에 가져와야 시계열 규칙이 실행됩니다.

## 정리

- 이 절차는 2022년 7월 이전에 배포한 구버전 Foundry Rules(Taurus)에만 필요합니다.
- Workshop의 Rule Editor 위젯에서 **Enable time series rules**를 켜고, 루트 객체 타입을 **Permitted object types**에 추가합니다.
- 트랜스폼의 `@AdditionalInputs`에 루트와 센서 객체 타입, 둘 사이 링크, 시계열 동기화, 틱 데이터셋 RID를 추가합니다.
- Code Repository의 **Ontology Imports**와 프로젝트 뷰의 **Project References**로 필요한 리소스를 프로젝트에 가져옵니다.
