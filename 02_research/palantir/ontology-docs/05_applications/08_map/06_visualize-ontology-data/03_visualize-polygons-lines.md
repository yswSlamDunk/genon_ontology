# 선과 폴리곤 (Lines and polygons)

- 원문: https://www.palantir.com/docs/foundry/map/visualize-polygons-lines/
- 사이드바 위치: Applications > Map > Visualize Ontology data > Lines and polygons

이 페이지는 온톨로지 객체를 지도 위에 선(line)이나 폴리곤(polygon, 다각형 영역)으로 그리는 방법과, 선 굵기, 선 모양, 채우기 같은 스타일 설정을 설명합니다. 도로, 항로, 행정 구역, 건물 외곽처럼 점 하나로 표현할 수 없는 객체를 다룰 때 사용합니다.

지도는 온톨로지 객체를 바탕으로 폴리곤과 선을 그릴 수 있습니다. 그릴 선이나 폴리곤 지오메트리를 지정하는 방법은 두 가지입니다.

* **지오셰이프 속성(geoshape property)**: 객체의 지오셰이프 속성에 저장된 GeoJSON 선과 폴리곤 지오메트리를 표시합니다.
* **선분(Line segment)**: 객체의 두 지오포인트 속성 사이에 선을 표시합니다.

**설명**: GeoJSON은 지리 도형을 JSON으로 표현하는 표준 형식입니다. 예를 들어 사각형 구역 하나는 `{"type": "Polygon", "coordinates": [[[127.0,37.5],[127.1,37.5],[127.1,37.6],[127.0,37.6],[127.0,37.5]]]}`처럼 꼭짓점 좌표 목록으로 저장됩니다. 선분 방식은 이런 도형 없이, 예를 들어 `Flight` 객체의 `origin_location`과 `destination_location` 두 지오포인트 속성을 이어 직선을 그립니다.

스타일 규칙을 설정하는 방법과 색 및 불투명도 스타일 설정은 [값 기반 스타일](01_visualize-objects.md#value-based-styling)을 참고하세요. 폴리곤과 선에는 다음 속성으로 스타일을 추가로 지정할 수 있습니다.

<a id="stroke-width"></a>
## 선 굵기 (Stroke width)

**Stroke width** 섹션에서는 선을 그릴 때, 또는 채우지 않은 폴리곤의 외곽선을 그릴 때 사용할 굵기를 정합니다.

![선 굵기 스타일 지정.](https://www.palantir.com/docs/resources/foundry/map/styling-line-width.png)

<a id="stroke-style"></a>
## 선 스타일 (Stroke style)

**Stroke style** 섹션에서는 선을 그릴 때, 또는 채우지 않은 폴리곤의 외곽선을 그릴 때 사용할 점선 패턴을 정합니다. 사용할 수 있는 옵션은 다음과 같습니다.

| Solid(실선)                                           | Dashed(파선)                                            | Dotted(점선)                                            |
| ----------------------------------------------- | ------------------------------------------------- | ------------------------------------------------- |
| ![실선.](https://www.palantir.com/docs/resources/foundry/map/styling-stroke-solid.png) | ![파선.](https://www.palantir.com/docs/resources/foundry/map/styling-stroke-dashed.png) | ![점선.](https://www.palantir.com/docs/resources/foundry/map/styling-stroke-dotted.png) |

선분의 경우 선의 방향을 나타내는 화살표도 설정할 수 있습니다.

![화살표가 있는 선분.](https://www.palantir.com/docs/resources/foundry/map/styling-arrows.png)

<a id="fill-polygons"></a>
## 폴리곤 채우기 (Fill polygons)

**Fill polygons**를 켜면 폴리곤은 최소한의 외곽선과 함께 내부가 지정한 색으로 채워져 그려집니다. 끄면 폴리곤은 외곽선만 그려지며, 이때 **Stroke width**와 **Stroke style**의 스타일 설정이 사용됩니다.

| 채우기 켬                                        | 채우기 끔                                         |
| --------------------------------------------------- | ----------------------------------------------------- |
| ![채운 폴리곤.](https://www.palantir.com/docs/resources/foundry/map/styling-fill-enabled.png) | ![외곽선만 그린 폴리곤.](https://www.palantir.com/docs/resources/foundry/map/styling-fill-disabled.png) |

<a id="loading-methods"></a>
## 로딩 방식 (Loading methods)

객체를 많이 표시할 때는 폴리곤과 선 지오메트리에서도 타일 기반 [로딩 방식](08_objects-loading-methods.md)을 사용할 수 있습니다.

## 정리

- 선과 폴리곤은 지오셰이프 속성(GeoJSON)이나 두 지오포인트 속성을 잇는 선분으로 그립니다.
- 색과 불투명도는 값 기반 스타일로 지정하고, 추가로 선 굵기와 선 스타일(실선, 파선, 점선)을 설정합니다.
- 선분에는 방향 화살표를, 폴리곤에는 채우기 여부를 설정할 수 있습니다.
- 객체가 많으면 타일 기반 로딩을 사용할 수 있습니다.
