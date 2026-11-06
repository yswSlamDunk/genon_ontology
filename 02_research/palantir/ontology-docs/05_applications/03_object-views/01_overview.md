# Object Views 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/object-views/overview/
- 사이드바 위치: Applications > Object Views > Overview

이 페이지는 Object View가 무엇인지, 그리고 Object View의 두 가지 종류(표준과 구성형)와 두 가지 형태(전체 화면과 패널)를 소개합니다. 온톨로지에 객체를 정의한 뒤 사용자가 객체 하나를 열었을 때 실제로 보게 되는 화면이 Object View이므로, 온톨로지와 애플리케이션을 잇는 출발점이 되는 개념입니다.

Object View는 객체 데이터를 재사용 가능한 방식으로 보여 주는 화면 표현입니다. Object View는 객체와 관련된 모든 정보를 모아 두는 중심 허브 역할을 하며, 속성(property) 데이터, 객체 링크, 관련 애플리케이션 등 객체에 대한 핵심 정보를 담습니다.

**설명**: 데이터베이스에 비춰 보면, 객체 하나는 테이블의 행 하나입니다. Object View는 그 행 하나의 열 값(속성)과, 외래 키로 연결된 다른 테이블의 행들(링크된 객체)을 한 화면에 모아 보여 주는 상세 페이지입니다. 예를 들어 `Patient` 객체 하나를 열면 그 환자의 이름, 나이 같은 속성과 함께 그 환자에게 연결된 처방(Prescription) 객체 목록이 같이 표시됩니다.

<a id="standard-and-configured-object-views"></a>
## 표준 Object View와 구성형 Object View (Standard and configured Object Views)

Object View에는 두 가지 종류가 있습니다.

1. **표준 Object View(Standard Object Views):** 객체 타입의 구성을 자동으로 반영하는, 별도 설정 없이 바로 제공되는 표준화된 표현입니다. 표준 Object View는 모든 객체 타입에서 사용할 수 있으며, 아무 구성 없이도 객체 데이터를 일관된 방식으로 볼 수 있게 해 줍니다. [표준 Object View에 대해 자세히 알아보세요.](02_standard-object-views.md)
2. **구성형 Object View(Configured Object Views):** [Workshop](https://www.palantir.com/docs/foundry/workshop/overview/)으로 만드는, 완전히 사용자 정의할 수 있는 표현입니다. 특정 워크플로에 맞는 맥락화된 경험을 제공하도록 구성할 수 있습니다. 구성형 Object View를 만들면 그것이 기본 뷰가 되지만, 사용자는 언제든지 표준 Object View로 다시 전환할 수 있습니다.

표준 Object View는 구성형 Object View와 함께 존재하는 일급(first-class) 보기 옵션입니다. 구성형 Object View가 만들어지지 않았을 때는 표준 Object View가 기본으로 표시되며, 구성형 Object View를 만든 뒤에도 표준 Object View에는 계속 접근할 수 있습니다. 사용자는 필요에 따라 언제든지 표준 Object View와 구성형 Object View 사이를 전환할 수 있습니다.

![표준 Object View의 전체 화면 형태와 패널 형태가 표시된 모습.](https://www.palantir.com/docs/resources/foundry/object-views/standard-full-and-panel-object-view.png)

**설명**: "일급 보기 옵션"이라는 말은 표준 뷰가 구성형 뷰를 만들기 전까지만 쓰는 임시 화면이 아니라는 뜻입니다. 구성형 뷰가 생겨도 표준 뷰는 사라지지 않고 같은 지위의 선택지로 남습니다. 즉 객체 타입 하나에 대해 "표준 뷰는 항상 존재하고, 구성형 뷰는 선택적으로 추가된다"고 정리할 수 있습니다.

> **중간 요약**: Object View는 표준(자동 생성, 설정 불필요)과 구성형(Workshop으로 직접 설계) 두 종류가 있습니다. 구성형을 만들면 기본 뷰가 바뀌지만 표준 뷰로 언제든 돌아갈 수 있습니다.

<a id="object-view-form-factors"></a>
## Object View 형태 (Object View form factors)

표준 Object View와 구성형 Object View 모두 상세 정도에 따라 두 가지 형태(form factor)로 제공됩니다. 이 서로 다른 형태 덕분에 여러 워크플로에서 객체 데이터를 유연하게 보여 줄 수 있습니다.

1. **전체 Object View(Full Object Views):** 객체에 대한 종합적인 개요로, 관련된 모든 정보를 깊이 있게 보여 줍니다.
2. **패널 Object View(Panel Object Views):** 다른 애플리케이션에 통합되도록 만든 형태로, 특정 워크플로에 가장 중요한 데이터를 보여 주는 데 집중해야 합니다.

> **중간 요약**: 전체 형태는 객체 하나의 모든 정보를 보는 독립 화면이고, 패널 형태는 다른 앱 안에 끼워 넣어 핵심 정보만 보여 주는 작은 화면입니다.

<a id="example-configured-patient-object-view"></a>
## 예시: 구성형 Patient Object View (Example: Configured Patient Object View)

`Patient` 객체에 대한 구성형 전체 Object View에는 다음과 같은 내용이 들어갈 수 있습니다.

* **핵심 인구통계 정보, 활력 징후, 진료 세부 정보:** 환자의 기본 정보, 건강 상태, 진행 중인 진료 계획을 종합적으로 보여 주는 요약입니다.
* **링크된 시술, 처방, 진단:** 의료 처치, 처방된 약물, 확정된 진단을 하나로 모은 목록으로, 환자의 병력을 전체적으로 보여 줍니다.
* **과거 입원 기록에서 나온 분석 추세:** 과거 입원에서 도출한 인사이트로, 시간에 따른 환자 건강의 패턴과 추세를 강조합니다.

이 구성형 전체 Object View는 환자에 관한 모든 관련 정보를 담은 빠짐없는 자료가 되어, 더 근거 있는 의료 의사 결정과 개인 맞춤형 진료 계획 수립을 도울 수 있습니다.

![전체 Patient Object View 예시.](https://www.palantir.com/docs/resources/foundry/object-views/overview-full-object-view.png)

같은 `Patient` 객체에 대한 구성형 패널 Object View는 인구통계 정보와 활력 징후만 보여 줄 수도 있습니다. 그러면 다른 애플리케이션에 패널이 나타날 때 사용자가 자신의 워크플로에 가장 중요한 데이터에 쉽게 접근할 수 있습니다.

![패널 Patient Object View 예시.](https://www.palantir.com/docs/resources/foundry/object-views/overview-panel-object-view.gif)

**설명**: 같은 객체 타입에 대해 전체 뷰와 패널 뷰를 따로 구성한다는 점이 핵심입니다. 데이터는 같은 `Patient` 객체 하나이고, 보여 주는 범위만 다릅니다. 전체 뷰는 링크된 처방과 진단 목록까지 모두 보여 주고, 패널 뷰는 이름, 나이, 혈압처럼 몇 개 속성만 보여 줍니다. SQL로 치면 같은 행에 대해 `SELECT *`를 하는 화면과 `SELECT name, age, blood_pressure`만 하는 화면을 따로 두는 것입니다.

> **중간 요약**: 환자 예시에서 전체 뷰는 인구통계, 링크된 의료 기록, 과거 추세까지 모두 담고, 패널 뷰는 다른 앱에서 빠르게 참고할 핵심 정보만 담습니다.

[객체 타입과 온톨로지 기반 데이터 모델링의 개념에 대해 자세히 알아보세요.](../../01_ontology-building/04_core-concepts.md)

## 정리

- Object View는 객체 하나에 관한 속성, 링크, 관련 애플리케이션을 모아 보여 주는 재사용 가능한 화면입니다.
- 표준 Object View는 객체 타입 구성에서 자동으로 만들어지고, 구성형 Object View는 Workshop으로 직접 설계합니다.
- 구성형 뷰가 생기면 기본 뷰가 되지만 표준 뷰는 항상 함께 남아 전환할 수 있습니다.
- 두 종류 모두 전체(Full) 형태와 패널(Panel) 형태로 제공되며, 패널 형태는 다른 앱에 넣어 핵심 정보만 보여 줍니다.
