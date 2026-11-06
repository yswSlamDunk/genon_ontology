# 객체 함수 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/functions/functions-on-objects/
- 사이드바 위치: Define Ontologies > Functions > Functions on objects > Overview

이 페이지는 Foundry 함수(function)가 온톨로지의 객체와 링크 데이터를 직접 읽고 수정할 수 있다는 점, 즉 흔히 "객체 함수(Functions on objects, FOO)"라고 부르는 기능을 소개합니다. 함수 저장소로 온톨로지 타입을 가져오면 무엇이 자동으로 생기는지, 그리고 언어(TypeScript v1, TypeScript v2, Python)별로 객체를 읽는 API가 어떻게 다른지 안내합니다.

<a id="functions-on-objects-foo"></a><a id="object-apis-by-language"></a>
## 객체 함수 (Functions on objects, FOO)

Foundry의 함수는 온톨로지의 객체와 링크에서 데이터를 읽고 수정하는 기능을 기본으로 지원합니다. 온톨로지에서 객체 타입과 링크 타입을 정의한 뒤 이 타입들을 함수 저장소로 가져오면 코드 바인딩(code binding)이 자동으로 생성됩니다. 이 코드 바인딩은 다음을 지원합니다.

* 객체 타입과 객체 집합(object set) 타입을 함수의 [파라미터](../04_types-reference.md#ontology-types)로 전달하기
* 필요할 때 객체 집합 검색하기
* [온톨로지 편집(edit)](../09_language-agnostic-features/01_edits-overview.md)으로 객체 수정하기

**설명**: 코드 바인딩은 온톨로지 정의를 바탕으로 자동 생성되는 타입과 클래스 코드입니다. 예를 들어 온톨로지에 `Airport` 객체 타입(속성 `city`, `country`)이 있으면, 저장소에 `Airport`라는 TypeScript 타입이 생겨서 `airport.city`처럼 속성에 접근할 때 컴파일러가 이름과 타입을 검사하고 편집기가 자동 완성을 제공합니다. 데이터베이스 스키마에서 ORM 엔터티 클래스를 생성하는 것과 같은 방식입니다.

이처럼 온톨로지를 기본으로 지원하기 때문에, Foundry의 함수는 흔히 쓰이는 FaaS(Functions-as-a-Service) 플랫폼을 훨씬 넘어섭니다. 데이터 저장, 조회, 수정을 기본으로 지원하고, 이 모든 작업에 Foundry의 데이터 보안, 계보(lineage), 투명성 보장이 적용됩니다.

**설명**: FaaS는 AWS Lambda처럼 함수 코드만 올려 두면 요청이 올 때 플랫폼이 실행해 주는 서비스 형태를 말합니다. 일반적인 FaaS에서는 데이터를 읽거나 쓰려면 함수 코드가 직접 데이터베이스에 접속하고 권한도 따로 관리해야 합니다. Foundry 함수는 온톨로지 객체를 파라미터나 검색으로 바로 받아 쓰고, 접근 권한 검사와 변경 이력 추적을 플랫폼이 맡는다는 점이 다릅니다.

"객체 함수(functions on objects)"(때로 "FOO"라고 부름)라는 용어는 파라미터로 받거나 객체 검색을 통해 객체 데이터를 읽는 함수를 느슨하게 가리키는 말입니다. Foundry에 다른 함수와 구별되는 "객체 함수"라는 공식 개념이 있는 것은 아닙니다.

<a id="object-apis-by-language"></a>
## 언어별 객체 API (Object APIs by language)

객체를 읽을 때 사용하는 API는 함수를 작성하는 언어에 따라 다릅니다.

* TypeScript v1 함수는 `@foundry/ontology-api` 패키지에서 내보내는 `Objects.search()` API로 객체를 검색합니다. [객체 집합 (TSv1)](07_api-object-sets.md)과 [객체와 링크 (TSv1)](06_api-objects-links.md)를 참고하십시오.
* TypeScript v2 함수는 [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/overview/) 클라이언트로 온톨로지를 조회합니다. [TypeScript v2 함수 시작하기](../10_typescript-v2/01_typescript-v2-getting-started.md)를 검토한 다음, 전체 쿼리 문법은 [TypeScript OSDK 레퍼런스](https://www.palantir.com/docs/foundry/ontology-sdk/typescript-osdk/)를 참고하십시오.
* Python 함수는 [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/overview/) 클라이언트로 온톨로지를 조회합니다. [Python의 객체 함수](../11_python/03_python-functions-on-objects.md)를 검토한 다음 [Python OSDK 레퍼런스](https://www.palantir.com/docs/foundry/ontology-sdk/python-osdk/)를 참고하십시오.

아직 언어를 정하지 않았다면 [언어별 기능 지원](../02_language-feature-support.md)과 [TypeScript v1과 TypeScript v2 비교](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)를 검토하십시오.

[객체 함수를 시작하는 방법을 알아보십시오.](02_foo-getting-started.md)

## 정리

- Foundry 함수는 온톨로지 객체와 링크를 기본으로 읽고 수정할 수 있으며, 타입을 가져오면 코드 바인딩이 자동 생성됩니다.
- 코드 바인딩으로 객체와 객체 집합을 파라미터로 받고, 객체를 검색하고, 온톨로지 편집으로 객체를 수정할 수 있습니다.
- "객체 함수(FOO)"는 객체 데이터를 읽는 함수를 가리키는 비공식 용어일 뿐 별도 개념이 아닙니다.
- TypeScript v1은 `Objects.search()`, TypeScript v2와 Python은 Ontology SDK 클라이언트로 객체를 조회합니다.
