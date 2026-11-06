# 온톨로지의 모델 (Models in the Ontology)

- 원문: https://www.palantir.com/docs/foundry/ontology/models/
- 사이드바 위치: Ontology building > Models in the Ontology

이 페이지는 AI/ML 모델을 온톨로지(Ontology)에 연결해 실제 업무 화면에서 쓰이게 만드는 과정을 다룹니다. 모델을 학습시키는 방법이 아니라, 이미 평가를 마친 모델을 배포하고 함수(function)로 감싸 애플리케이션에서 호출하는 단계에 초점을 맞춥니다. 또한 모델을 온톨로지에 매핑하면 어떤 이점이 있는지 정리합니다.

조직들은 의사결정을 가속하고 개선하기 위해 인공지능(AI)과 머신러닝(ML)을 활용하려고 합니다. 그러나 AI/ML을 실제 운영에 적용하는 현실은 복잡하며, 일반적인 투자 대비 수익은 기대에 미치지 못하는 경우가 많습니다.

Foundry는 이 간극을 메우는 데 필요한 핵심 기능을 제공합니다. 신뢰할 수 있는 데이터 기반, 조직의 목표에 비추어 모델을 평가하고 비교하는 도구, 그리고 모델을 사용자 대상 운영 워크플로에 배포하는 기능입니다. 이 페이지는 마지막 단계, 즉 평가를 마친 모델을 프로덕션에 배포하는 단계에 초점을 둡니다.

<a id="end-to-end-workflow"></a>
## 종단간 워크플로 (End-to-end workflow)

상위 수준에서 보면, Foundry에서 온톨로지와 함께 실시간 추론(live inference)을 위해 AI/ML을 운영에 적용하는 데 필요한 종단간 단계는 다음과 같습니다.

1. Foundry에서 [모델을 만듭니다](https://www.palantir.com/docs/foundry/integrate-models/integrate-overview/).
2. [직접 모델 배포(direct model deployment)](https://www.palantir.com/docs/foundry/manage-models/create-a-model-deployment/)를 구성합니다.
3. [모델을 감싸는 간단한 래퍼 함수를 게시하고](https://www.palantir.com/docs/foundry/model-integration/model-functions-guide/), 필요하면 모델을 중심으로 복잡한 로직을 조율하기 위해 [다른 함수에서 이를 호출합니다](../02_define-ontologies/04_functions/14_models/01_functions-on-models.md).
4. 그 함수를 [Workshop](https://www.palantir.com/docs/foundry/workshop/functions-use/), [Vertex](../05_applications/05_vertex/01_overview.md) 및 기타 최종 사용자용 애플리케이션에서 실시간 추론에 사용합니다.

온톨로지 객체는 모델을 활용해 일괄 추론(batch inference)을 수행한 데이터셋을 백킹 데이터소스로 사용할 수도 있습니다. [Code Repositories에서 모델을 사용하는 방법을 알아보세요](https://www.palantir.com/docs/foundry/model-integration/tutorial-train-code-repositories/).

**설명**: 추론(inference)은 학습이 끝난 모델에 새 입력을 넣어 예측값을 얻는 과정입니다. "실시간 추론"은 사용자가 화면에서 버튼을 누르는 시점에 함수가 모델을 호출해 즉시 결과를 받는 방식입니다. 예를 들어 Workshop 화면에서 주문 하나를 선택하면 `predictDeliveryDelay(order)` 같은 함수가 배포된 모델을 호출해 지연 확률을 돌려줍니다. "일괄 추론"은 미리 전체 데이터에 대해 모델을 한꺼번에 돌려 결과를 데이터셋에 저장해 두는 방식입니다. 예를 들어 매일 밤 모든 주문 행에 `predicted_delay` 열을 계산해 넣어 두고, 그 데이터셋을 Order 객체 타입의 백킹 데이터소스(backing datasource)로 쓰면 예측값이 객체의 속성(property)으로 보입니다. "래퍼(wrapper) 함수"는 모델 호출을 감싸서 입력과 출력 형식을 맞춰 주는 얇은 함수입니다.

> **중간 요약**: 모델 생성, 배포 구성, 래퍼 함수 게시, 애플리케이션에서 호출의 4단계로 실시간 추론을 운영에 붙입니다. 미리 계산한 일괄 추론 결과 데이터셋으로 객체를 채우는 방법도 있습니다.

<a id="benefits"></a>
## 이점 (Benefits)

데이터셋을 온톨로지 개념에 매핑하는 것이 워크플로 개발과 의사결정에 [이점](02_why-ontology.md)을 주는 것처럼, 모델을 온톨로지에 매핑하는 것도 여러 이점을 제공합니다.

* **해석 가능성(Interpretability)**. 모든 모델링 결과가 현실 세계의 개념(객체 타입의 속성)으로 정의되므로, 최종 사용자는 모델링 결과를 사용하기 위해 머신러닝을 이해할 필요가 없습니다. 사용자는 그저 *예측(forecast)*, *추정(estimate)*, *분류(classification)* 같은 단순한 개념과 상호작용하면 됩니다.
* **규모의 경제(Economies of scale)**. 각 모델링 프로젝트가 특정 사용 사례를 위해 매번 따로 만드는 맞춤형 작업이 되는 대신, 모델링 작업이 시간이 지나면서 서로를 기반으로 쌓여 갈 수 있습니다. 예를 들어 한 사용 사례를 위해 만든 예측을 이후의 사용 사례에도 즉시 활용할 수 있으므로, 중복 작업이 줄고 시간이 갈수록 최종 사용자에게 더 빨리 가치를 제공할 수 있습니다.
* **대규모 연결성(Connectivity at scale)**. ML 모델을 포함함으로써 온톨로지는 데이터 측면뿐 아니라 *로직* 측면에서도 조직의 단일 진실 공급원(single source of truth)이 됩니다. 모델은 미래에 상황이 어떻게 변할지에 대한 조직의 예상을 담고 있습니다. 이런 방식으로 온톨로지는 기업 전체의 "디지털 트윈"이 되며, 서로 분리된 수많은 모델링 작업으로는 결코 불가능했던 방식으로 조직 전반의 변화를 시뮬레이션할 수 있게 합니다.

**설명**: "해석 가능성" 항목의 핵심은 모델의 출력이 Order 객체의 `predicted_delay_days` 같은 평범한 속성으로 보인다는 점입니다. 사용자는 이 값이 어떤 알고리즘으로 계산됐는지 몰라도 일반 열 값처럼 정렬하고 필터링할 수 있습니다. "단일 진실 공급원"은 같은 정보를 여러 곳에 따로 두지 않고 한 곳을 기준으로 삼는다는 뜻으로, 데이터베이스 정규화에서 같은 사실을 한 테이블에만 저장하는 원칙과 같은 목적입니다.

> **중간 요약**: 모델 결과를 객체의 속성으로 노출하면 사용자가 ML 지식 없이 쓸 수 있고, 한 번 만든 예측을 여러 사용 사례에서 재사용할 수 있으며, 온톨로지가 데이터와 로직 모두의 기준점이 됩니다.

## 정리

- 이 페이지는 평가가 끝난 모델을 온톨로지와 연결해 프로덕션에서 쓰는 단계를 다룹니다.
- 실시간 추론 흐름은 모델 생성, 직접 모델 배포 구성, 래퍼 함수 게시, Workshop나 Vertex 같은 애플리케이션에서 함수 호출의 순서입니다.
- 일괄 추론 결과를 담은 데이터셋을 객체의 백킹 데이터소스로 쓰는 방법도 있습니다.
- 모델을 온톨로지에 매핑하면 해석 가능성, 규모의 경제, 대규모 연결성이라는 이점을 얻습니다.
