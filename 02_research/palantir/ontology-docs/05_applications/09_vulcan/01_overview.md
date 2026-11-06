# Vulcan 개요 (Overview)

- 원문: https://www.palantir.com/docs/foundry/vulcan/overview/
- 사이드바 위치: Applications > Vulcan > Overview

이 페이지는 Palantir 플랫폼에서 CAD 모델, 공학 도면, 포인트 클라우드를 3D로 보여 주는 애플리케이션 Vulcan을 소개합니다. Vulcan이 할 수 있는 일, 온톨로지에 저장된 CAD 객체를 장면(scene)에 불러오는 방법, 지원하는 모델 파일 형식을 설명합니다. 핵심은 3D 모델 파일도 온톨로지 객체로 다루고, Vulcan에서 만든 주석이나 측정값도 다시 온톨로지 객체로 저장된다는 점입니다.

원문 페이지 제목은 "Vulcan"입니다.

**Vulcan**은 Palantir 플랫폼에서 컴퓨터 지원 설계(computer-aided design, CAD) 모델, 공학 도면, 포인트 클라우드(point cloud)를 표시하는 3D 렌더링 애플리케이션입니다.

Vulcan으로 다음을 할 수 있습니다.

* [온톨로지](../../01_ontology-building/01_overview.md)에 CAD 객체로 저장된 CAD 모델을 봅니다. Vulcan에 필요한 객체 타입과 속성(property)은 [스키마 참조](03_schema-reference.md)를 참고하세요.
* 모델의 부품에 주석을 달고, 측정하고, 단면을 보고, 색을 바꿉니다. [도구](02_tool-overview.md)를 참고하세요.
* 3D 뷰포트(viewport)를 Workshop 모듈에 임베드합니다. [Workshop 모듈에 Vulcan 임베드하기](04_widget.md)를 참고하세요.

Vulcan에서 저장한 주석, 측정값, 단면 평면(section plane)은 온톨로지 객체이므로, 알림(alert)이나 대시보드 같은 다른 Palantir 플랫폼 워크플로를 구동하는 데 사용할 수 있습니다.

![Vulcan 화면의 메인 뷰포트에 3D 모델이 표시되고, 왼쪽에 장면 트리(scene tree)가 보입니다.](https://www.palantir.com/docs/resources/foundry/vulcan/vulcan-overview.png)

*이 스크린샷은 가상의 데이터를 사용합니다.*

**설명**: CAD 모델은 기계나 부품을 설계할 때 만드는 3차원 도형 파일입니다. 포인트 클라우드는 레이저 스캐너(LiDAR) 등으로 실제 물체 표면을 측정해 얻은 (x, y, z) 좌표 점들의 대규모 집합입니다. 주석이 온톨로지 객체로 저장된다는 것은, 예를 들어 "danger 등급 주석이 새로 생기면 담당자에게 알림"처럼 다른 애플리케이션이 그 객체를 조회하거나 감시할 수 있다는 뜻입니다.

> **중간 요약**: Vulcan은 온톨로지의 CAD 객체를 3D로 보여 주고, 주석, 측정, 단면, 색칠 도구를 제공하며, Workshop에 임베드할 수 있는 애플리케이션입니다. Vulcan에서 저장한 결과물도 온톨로지 객체가 됩니다.

<a id="getting-started"></a>
## 시작하기 (Getting started)

Vulcan은 [온톨로지](../../01_ontology-building/01_overview.md)에 CAD 객체로 저장된 3D 모델을 렌더링합니다. [CAD 객체](03_schema-reference.md#cad-object)란 `cad_media_reference` 타입 클래스(type class)가 붙은 속성을 가진 온톨로지 객체이며, 이 속성은 모델 파일을 가리키는 미디어 참조(media reference)를 담습니다.

단독(standalone) 애플리케이션에서는 **Add to scene**을 선택한 다음 CAD 객체를 고릅니다. 이 과정을 반복하면 장면에 모델을 더 추가할 수 있습니다.

Vulcan 위젯에서는 위젯 설정이 어떤 모델을 불러올지 결정합니다. [CAD 객체 선택하기](04_widget.md#choose-a-cad-object)를 참고하세요.

**설명**: 타입 클래스는 속성에 붙이는 이름표입니다. 예를 들어 `Engine` 객체 타입에 `model_file`이라는 미디어 참조 속성이 있고 여기에 `cad_media_reference` 타입 클래스가 붙어 있으면, Vulcan은 속성 이름과 관계없이 이 속성에서 3D 파일을 찾아 렌더링합니다. 미디어 참조는 테이블 칸에 파일 내용을 직접 넣지 않고, 별도로 저장된 파일을 가리키는 식별자를 넣어 두는 방식입니다.

<a id="supported-model-formats"></a>
### 지원하는 모델 형식 (Supported model formats)

Vulcan은 세 종류의 형상(geometry)을 렌더링합니다. 각 부품의 표면을 삼각형으로 근사하는 메시(mesh) 모델, 2D 공학 도면, 포인트 클라우드입니다. CAD 객체의 미디어 참조 속성(`cad_media_reference` 타입 클래스가 붙은 속성)이 다음 형식 중 어느 파일을 가리켜도 변환 없이 사용할 수 있습니다.

* 메시 형식: `GLB`, `GLTF`, `STL`, `OBJ`, `PLY`, `3MF`
* 공학 도면: `DXF`
* 포인트 클라우드: `LAS`, `LAZ`

> **중간 요약**: CAD 객체는 `cad_media_reference` 타입 클래스가 붙은 미디어 참조 속성을 가진 객체이며, 단독 앱에서는 **Add to scene**으로, 위젯에서는 위젯 설정으로 불러옵니다. 메시, DXF 도면, LAS/LAZ 포인트 클라우드 형식을 변환 없이 지원합니다.

## 정리

- Vulcan은 CAD 모델, 공학 도면, 포인트 클라우드를 보여 주는 3D 렌더링 애플리케이션입니다.
- 모델은 `cad_media_reference` 타입 클래스 속성으로 파일을 가리키는 온톨로지 CAD 객체로 저장됩니다.
- 주석, 측정, 단면, 색칠 도구를 제공하며, 저장된 주석, 측정값, 단면 평면은 온톨로지 객체로서 다른 워크플로에 쓰입니다.
- 지원 형식: 메시(`GLB`, `GLTF`, `STL`, `OBJ`, `PLY`, `3MF`), 도면(`DXF`), 포인트 클라우드(`LAS`, `LAZ`).
