# Control Panel에서 Vertex 설정 구성하기 (Configure settings in Control Panel)

- 원문: https://www.palantir.com/docs/foundry/vertex/vertex-settings-control-panel/
- 사이드바 위치: Applications > Vertex > Configuration > Configure settings in Control Panel

이 페이지는 조직 전체에 적용되는 Vertex 설정을 Control Panel에서 바꾸는 방법과, 각 설정 항목(그래프 기본값, 데이터 로딩 제한, 모델 구성)의 의미를 설명합니다. 개별 사용자가 아니라 관리자가 조직 단위로 정하는 값이라는 점이 핵심입니다.

조직 전체에 적용되는 여러 Vertex 설정은 [Control Panel](https://www.palantir.com/docs/foundry/administration/control-panel/)에서 구성할 수 있습니다. Vertex 설정을 수정하려면 `Vertex Admin` 역할이 필요합니다.

![Control Panel의 Vertex 섹션](https://www.palantir.com/docs/resources/foundry/vertex/control-panel-vertex.png)

<a id="graph-defaults"></a>
## 그래프 기본값 (Graph defaults)

* **Default time selection:** 기본 시간 선택이 걸치는 일수입니다.
* **Default graph mode:** 새 그래프를 다이어그램 모드(diagram mode) \[beta]로 만들지 그래프 모드(graph mode)로 만들지 정합니다.
* **Active icon categories:** 다이어그램 모드 \[beta]에서 사용할 수 있는 아이콘 카테고리를 정합니다.

**참고**: 베타(Beta). 다이어그램 모드는 개발 단계상 [베타](https://www.palantir.com/docs/foundry/platform-overview/development-life-cycle/) 단계에 있으며, 여러분의 환경(enrollment)에서는 사용하지 못할 수도 있습니다. 활발히 개발되는 동안 기능이 바뀔 수 있습니다. 다이어그램 모드를 켜려면 플랫폼 관리자에게 Control Panel에서 [애플리케이션 접근 권한 수정](https://www.palantir.com/docs/foundry/administration/configure-application-access/)을 요청하세요.

> **중간 요약**: 그래프 기본값에서는 기본 시간 선택 기간, 새 그래프의 기본 모드(그래프 또는 베타인 다이어그램), 다이어그램 모드의 아이콘 카테고리를 정합니다.

<a id="data-loading"></a>
## 데이터 로딩 (Data loading)

* **Time series polling interval:** 라이브 모드(live mode)에서 Vertex가 갱신된 시계열 값을 얼마나 자주(초 단위) 확인할지 정합니다.
* **Time series missing data warning:** 시계열에 최근 관측값이 없으면 Vertex는 경고를 표시합니다. 이 설정은 경고가 나타나기 전까지 선택한 시각과 가장 가까운 시계열 값 사이에 허용되는 최대 시간(시간 단위)을 정합니다.
* **Object search limits:** 사용자가 검색 대화 상자에서 그래프에 추가할 수 있는 객체의 최대 개수를 정합니다.
* **Search around limits:** Search Around로 그래프에 객체를 추가하는 동작을 제어합니다.
  * **Maximum number of objects:** 한 번의 Search Around 결과로 Vertex가 불러올 최대 객체 수입니다.
  * **Maximum number of ungrouped objects:** Search Around 결과 중 Vertex가 그룹이 아니라 개별 노드로 그래프에 추가할 최대 객체 수입니다. 이 한도보다 많은 객체가 그래프에 추가되려 하면 객체들이 자동으로 그룹화됩니다.
  * **Template search around max depth:** 템플릿을 만들 때 허용되는 중첩 Search Around의 최대 개수입니다.

**설명**: 폴링(polling)은 서버에 주기적으로 "새 값이 있는가"를 묻는 방식입니다. 예를 들어 폴링 간격이 30초면 라이브 모드의 Vertex는 30초마다 시계열 값을 다시 요청합니다. 누락 데이터 경고는 예를 들어 허용 시간이 2시간이고 선택한 시각이 12:00인데 가장 가까운 시계열 값이 09:00에 기록된 것이라면, 3시간 차이가 나므로 경고가 표시되는 식입니다. 중첩 Search Around 깊이는 링크를 몇 단계까지 따라갈지를 뜻하며, 예를 들어 깊이 2는 Flight에서 Aircraft로, 다시 Aircraft에서 Maintenance로 두 단계 따라가는 것에 해당합니다.

> **중간 요약**: 데이터 로딩 설정은 시계열 폴링 주기, 누락 데이터 경고 기준, 검색과 Search Around로 한 번에 불러올 수 있는 객체 수, 자동 그룹화 기준, 템플릿의 Search Around 최대 깊이를 정합니다.

<a id="model-configurations"></a>
## 모델 구성 (Model configurations)

* **Legacy model configuration:** Modeling objectives 애플리케이션을 통해 개선된 모델 구성 환경을 사용할 수 있습니다. Vertex에서 직접 구성한 모델에 대한 지원은 유지되지만, Vertex 구성 패널에서 새 모델을 구성하는 것은 이제 권장되지 않습니다.
* **Model configuration mappings:** 모델 구성자가 사용할 수 있는 데이터 매핑 유형을 선택합니다.

## 정리

- 조직 전체 Vertex 설정은 Control Panel에서 `Vertex Admin` 역할을 가진 사용자가 구성합니다.
- 그래프 기본값은 기본 시간 선택 기간, 기본 그래프 모드, 다이어그램 모드 아이콘 카테고리를 정합니다.
- 데이터 로딩 설정은 시계열 폴링과 누락 경고, 객체 검색과 Search Around의 개수 및 깊이 한도를 정합니다.
- Vertex에서 직접 모델을 구성하는 방식은 권장되지 않으며 Modeling objectives 애플리케이션이 대안입니다.
