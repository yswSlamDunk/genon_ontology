# 데코레이터 (Decorators)

- 원문: https://www.palantir.com/docs/foundry/functions/decorators/
- 사이드바 위치: Define Ontologies > Functions > TypeScript v1 > Decorators

이 페이지는 TypeScript v1에서 어떤 메서드가 함수(function)로 발견되고 게시되는지 결정하는 규칙과, 그때 사용하는 데코레이터(`@Function`, `@OntologyEditFunction`, `@Edits`, `@Query`)를 설명합니다. 짧은 페이지이지만 함수의 종류(일반, 온톨로지 편집, 쿼리)를 구분하는 기준이 여기서 정해집니다.

**팁**: 이 문서는 TypeScript v1 함수에 한정된 내용입니다. Ontology SDK 지원과 구성 가능한 리소스 요청을 포함한 [더 강력한 기능](../02_language-feature-support.md#typescript-v1-vs-typescript-v2)을 위해 [TypeScript v2로 마이그레이션](../10_typescript-v2/03_typescript-v2-migration.md)하는 것을 권장합니다.

[TypeScript ↗](https://www.typescriptlang.org/docs/handbook/basic-types.html) 함수는 [TypeScript 클래스 ↗](https://www.typescriptlang.org/docs/handbook/classes.html)의 메서드로 선언됩니다. 함수가 발견되고 게시되려면 몇 가지 요구 사항이 있습니다.

* 메서드는 `public`이어야 합니다.
* 메서드가 속한 클래스는 `functions-typescript/src/index.ts` 파일에서 export되어야 합니다.
* 메서드에는 `@foundry/functions-api` 패키지에서 가져온 다음 데코레이터 중 하나가 붙어 있어야 합니다.
  * `@Function()`: 일반 함수용입니다.
  * [`@OntologyEditFunction()`](03_api-ontology-edits.md): 액션을 뒷받침할(back) 함수용입니다.
    * [`@OntologyEditFunction()`](03_api-ontology-edits.md) 메서드를 사용할 때 `@Edits([object type])` 데코레이터로 객체 출처(provenance) 정보를 선택적으로 지정할 수 있습니다.
    * `@Edits([object type])` 데코레이터가 없으면, 코드의 정적 분석을 통해 최선의 노력(best-efforts) 방식으로 객체 출처 정보를 추론합니다.
  * [`@Query({ apiName: "userDefinedAPIName"})`](../09_language-agnostic-features/02_query-functions.md): [Foundry API](https://www.palantir.com/docs/foundry/api/general/overview/introduction/)를 통해 실행하려는 읽기 전용 쿼리용입니다. 이 데코레이터는 `@Function` 데코레이터와 함께 사용하면 안 되며, 단독으로 사용해야 합니다.

**설명**: 데코레이터는 `@이름(...)` 형태로 클래스나 메서드 바로 위에 붙여 메타데이터를 덧붙이는 TypeScript 문법입니다. 메서드의 동작 자체를 바꾸는 것이 아니라, Foundry의 함수 수집기가 "이 메서드는 어떤 종류의 함수인가"를 읽어 가는 표식으로 쓰입니다. 객체 출처(provenance) 정보는 "이 함수가 어떤 객체 타입을 편집하는가"에 대한 정보로, `@Edits`로 명시하지 않으면 코드에서 어떤 객체 타입의 속성을 바꾸는지 보고 추론합니다.

다음은 이 방식으로 올바르게 export된 함수의 예입니다.

```typescript
import { Function, OntologyEditFunction, Query, Integer, Edits } from "@foundry/functions-api";
import { Employee, Objects, ObjectSet } from "@foundry/ontology-api";

export class MyUsefulFunctions {
    @Function()
    public incrementNumber(x: Integer): Integer {
        return x + 1;
    }

    @Edits(Employee)
    @OntologyEditFunction()
    public updateName(employee: Employee, newName: string): void {
        employee.firstName = newName;
    }

    @Query({ apiName: "getEmployeesByName" })
    public async getEmployeesByName(name: string): Promise<ObjectSet<Employee>> {
        return Objects.search().employee().filter(employee => employee.firstName.exactMatch(name));
    }
}
```

**설명**: 세 메서드가 세 종류의 함수를 보여 줍니다.

| 메서드 | 데코레이터 | 하는 일 |
|---|---|---|
| `incrementNumber` | `@Function()` | 정수를 받아 1을 더해 반환하는 일반 함수입니다. |
| `updateName` | `@Edits(Employee)`, `@OntologyEditFunction()` | Employee 객체의 `firstName` 속성을 바꾸는 편집 함수입니다. 반환값이 `void`이며, 액션에서 호출되어야 편집이 실제로 적용됩니다. |
| `getEmployeesByName` | `@Query({ apiName: ... })` | 이름이 정확히 일치하는 Employee 객체 집합(object set)을 반환하는 읽기 전용 쿼리로, `getEmployeesByName`이라는 API 이름으로 외부에서 호출할 수 있습니다. |

private이거나 관련 데코레이터가 붙지 않은 메서드는 함수 레지스트리에 게시되지 않습니다. 덕분에 재사용이나 코드 정리를 위한 도우미 함수와 유틸리티를 자유롭게 만들 수 있습니다.

**주의**: 재게시(Republishing). TypeScript 저장소의 각 함수는 클래스 이름과 메서드 이름으로 고유하게 정의됩니다. 클래스나 메서드의 이름을 바꾸면 함수는 새 식별자로 게시됩니다.

**설명**: 예를 들어 `MyUsefulFunctions.incrementNumber`를 `MyUsefulFunctions.addOne`으로 이름을 바꾸면, Foundry는 이를 기존 함수의 새 버전이 아니라 완전히 다른 함수로 취급합니다. 따라서 기존 이름을 참조하던 Workshop 모듈이나 액션은 새 함수를 자동으로 따라가지 않습니다.

## 정리

- TypeScript v1 함수는 `index.ts`에서 export된 클래스의 `public` 메서드여야 합니다.
- 일반 함수에는 `@Function()`, 액션을 뒷받침하는 편집 함수에는 `@OntologyEditFunction()`(필요하면 `@Edits`와 함께), Foundry API로 호출할 읽기 전용 쿼리에는 `@Query`를 단독으로 붙입니다.
- 데코레이터가 없거나 private인 메서드는 게시되지 않으므로 도우미 함수로 쓸 수 있습니다.
- 함수는 클래스 이름과 메서드 이름으로 식별되므로, 이름을 바꾸면 새 함수로 게시됩니다.
