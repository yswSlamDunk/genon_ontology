# 점 표시: 아이콘과 원 (Points (icons and circles))

- 원문: https://www.palantir.com/docs/foundry/map/visualize-points/
- 사이드바 위치: Applications > Map > Visualize Ontology data > Points (icons and circles)

이 페이지는 객체를 지도 위의 한 점으로 표시하는 두 방식인 아이콘(icon)과 원(circle)의 설정 방법을 설명합니다. 공항, 기상 관측소, 선박처럼 위치가 좌표 하나로 정해지는 객체를 지도에 올릴 때 가장 먼저 쓰는 표시 방식입니다.

지도에는 점을 시각화하는 방법이 두 가지 있습니다. 아이콘과 원입니다. 아이콘이나 원을 표시하려면 각 객체의 위치를 제공하는 지오메트리 소스(geometry source)가 필요합니다. 지원되는 지오메트리 소스는 [지오포인트 속성(geopoint property)](https://www.palantir.com/docs/foundry/geospatial/ontology/)과 [트랙](../07_integrate-data-for-the-map/01_integrate-objects.md#track-objects)입니다.

트랙을 점 지오메트리 소스로 사용하면, 지도는 현재 [선택된 시간](../05_time/01_time-overview.md#selected-time-and-time-range)에 해당하는 위치를 트랙에서 뽑아냅니다. 그 위치를 어떻게 보간(interpolate)할지 정하는 설정 옵션은 [트랙](07_visualize-tracks.md) 페이지에서 다룹니다.

**설명**: 지오포인트 속성은 위도와 경도 한 쌍을 담는 속성 타입입니다(예: `"37.56,126.97"`). 트랙은 시각별 위치 기록의 모음이므로, 지도는 선택된 시간에 맞는 위치 하나를 골라 점으로 찍습니다. 보간은 기록된 두 시각 사이의 시점이 선택되었을 때 두 위치 사이의 값을 계산해 채우는 것을 말합니다. 예를 들어 10:00에 A 지점, 10:10에 B 지점이 기록되어 있고 선택된 시간이 10:05라면, 선형 보간은 A와 B의 중간 지점을 위치로 사용합니다.

<a id="icon-configuration"></a>
## 아이콘 설정 (Icon configuration)

아이콘은 점 데이터를 시각화하는 가장 흔한 방법 중 하나입니다. 각 아이콘은 지오메트리 소스가 제공한 위치에 놓이며, 워크플로에 맞는 시각화를 만들도록 다양한 방식으로 스타일을 지정할 수 있습니다.

<a id="icon"></a>
### 아이콘 (Icon)

**Icon** 섹션에서는 각 객체에 표시할 아이콘을 정합니다. 표시할 아이콘을 지정하는 옵션은 다음과 같습니다.

* **Object default**: Ontology Management 애플리케이션에서 설정한 객체 타입의 기본 아이콘을 사용합니다.
* **Media image**: 레이어의 모든 객체에 표시할 이미지 미디어 항목을 고릅니다.
* **Fixed icon**: 레이어의 모든 객체에 표시할 특정 아이콘을 고릅니다.
* **Property**: 객체의 속성 값에 따라 객체마다 아이콘이 정해집니다.

아래 예시는 비 관측 상태 시계열에 색과 아이콘 스타일을 함께 적용해, 미국 태평양 북서부의 기상 관측소 중 선택한 날짜에 비가 관측된 곳을 시각화합니다.

![지역의 날씨 상태를 해와 비 아이콘으로 표시한 지도.](https://www.palantir.com/docs/resources/foundry/map/styling-icon-type.png)

<a id="image-media-items"></a>
### 이미지 미디어 항목 (Image media items)

**Property** 옵션은 [미디어 참조(media reference)](https://www.palantir.com/docs/foundry/media-sets-advanced-formats/media-overview/#media-references) 타입의 객체 속성을 지원하며, 참조된 미디어를 아이콘으로 표시합니다. 아이콘으로 지원되는 미디어 형식은 이미지 미디어 참조뿐입니다.

<a id="rotation"></a>
### 회전 (Rotation)

아이콘의 회전은 어떤 [값 기반 스타일](01_visualize-objects.md#value-based) 옵션으로도 제어할 수 있습니다. 트랙 지오메트리 소스에는 **Automatic** 옵션도 있는데, 트랙에 따라 객체가 움직이는 방향으로 아이콘을 회전시킵니다.

아래 예시는 고정된 화살표 아이콘과 회전 스타일을 사용해 선박 객체의 이동 방향을 표시합니다.

![선박의 이동 방향.](https://www.palantir.com/docs/resources/foundry/map/styling-icon-rotation.png)

<a id="marker-shape"></a>
### 마커 모양 (Marker shape)

아이콘에 설정할 수 있는 마커 스타일은 세 가지입니다.

| Circle(원)                                              | Pin(핀)                                           | None(없음)                                          |
| --------------------------------------------------- | --------------------------------------------- | --------------------------------------------- |
| ![원 마커.](https://www.palantir.com/docs/resources/foundry/map/styling-marker-circle.png) | ![핀 마커.](https://www.palantir.com/docs/resources/foundry/map/styling-marker-pin.png) | ![마커 없음.](https://www.palantir.com/docs/resources/foundry/map/styling-marker-none.png) |

> **중간 요약**: 아이콘은 객체 타입 기본 아이콘, 이미지, 고정 아이콘, 속성 값에 따른 아이콘 중에서 고를 수 있고, 회전(트랙이면 이동 방향 자동 회전 포함)과 마커 모양(원, 핀, 없음)을 설정할 수 있습니다.

<a id="circle-configuration"></a>
## 원 설정 (Circle configuration)

각 원은 제공된 위치를 중심으로 하며, 스타일의 **radius** 섹션에서 설정한 반지름 값으로 그려집니다.

![원 크기가 서로 다른 공항들.](https://www.palantir.com/docs/resources/foundry/map/styling-circle-radius.png)

나머지 원 스타일 옵션은 [폴리곤 표시 옵션](03_visualize-polygons-lines.md)과 같습니다.

**설명**: 반지름도 값 기반 스타일로 지정할 수 있으므로, 예를 들어 공항 객체의 `annual_passengers` 속성 값이 클수록 원을 크게 그리는 식으로 수치를 크기로 표현할 수 있습니다.

<a id="loading-methods"></a>
## 로딩 방식 (Loading methods)

객체를 많이 표시할 때는 아이콘과 원 표시에서도 타일 기반 [로딩 방식](08_objects-loading-methods.md)을 사용할 수 있습니다.

## 정리

- 점 표시는 아이콘과 원 두 가지이며, 지오포인트 속성이나 트랙을 위치 소스로 사용합니다.
- 트랙을 쓰면 선택된 시간에 해당하는 위치(필요하면 보간한 위치)에 점이 찍힙니다.
- 아이콘은 종류(기본, 이미지, 고정, 속성 기반), 회전, 마커 모양을 설정할 수 있습니다.
- 원은 반지름을 설정하고, 나머지 스타일은 폴리곤과 같습니다. 객체가 많으면 타일 기반 로딩을 사용할 수 있습니다.
