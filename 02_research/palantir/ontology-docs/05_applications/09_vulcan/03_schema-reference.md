# Vulcan 스키마 참조 (Schema reference)

- 원문: https://www.palantir.com/docs/foundry/vulcan/schema-reference/
- 사이드바 위치: Applications > Vulcan > Schema reference

이 페이지는 Vulcan이 동작하려면 온톨로지에 있어야 하는 객체 타입, 액션 타입, 링크 타입과 그 속성(property)에 붙여야 하는 타입 클래스(type class)를 빠짐없이 나열한 참조 문서입니다. Vulcan은 속성 이름이 아니라 타입 클래스로 속성을 찾기 때문에, 이 표대로 타입 클래스를 붙이는 것이 Vulcan 설정의 핵심입니다. 데이터베이스 스키마 명세서처럼 각 항목의 필수 여부, 데이터 타입, 의미를 표로 정리합니다.

Vulcan은 사용자의 환경(enrollment)에 특정한 온톨로지 객체 타입, 액션, 링크 타입, 속성 타입 클래스 집합이 있기를 기대합니다. 이 페이지는 Vulcan이 읽거나 쓰는 모든 타입 클래스를 나열합니다.

[Ontology Manager](../04_ontology-manager/01_overview.md)에서 객체 타입, 액션, 링크 타입을 만든 다음, 이 페이지에 나열된 타입 클래스를 각각의 속성, 액션 파라미터, 링크 타입에 붙입니다.

**주의**: 스키마 안정성(Schema stability). 스키마 세부 사항은 Vulcan이 발전함에 따라 바뀔 수 있습니다. Vulcan 릴리스마다 스키마를 이 페이지와 대조해 확인하세요.

타입 클래스는 속성에 붙여 그 속성이 무엇을 위한 것인지 Vulcan에 알려 주는 라벨입니다. Vulcan은 속성을 이름이 아니라 항상 타입 클래스로 찾으므로, 속성 이름은 자신의 온톨로지 명명 규칙에 맞게 지을 수 있습니다. 또한 속성 하나에 타입 클래스를 여러 개 붙이면 그 속성이 Vulcan과 다른 애플리케이션 모두에 쓰일 수 있습니다.

아래에 나열된 모든 타입 클래스는 `vulcan` 네임스페이스에 속합니다. 즉, `kind` 필드는 항상 `"vulcan"`이고 `name` 필드만 달라집니다.

**설명**: 예를 들어 `Annotation` 객체 타입의 제목 속성 이름이 `issue_label`이어도, 그 속성에 `kind: "vulcan"`, `name: "annotation_title"` 타입 클래스를 붙이면 Vulcan은 그 속성을 주석 제목으로 읽고 씁니다. 이는 코드에서 필드 이름 대신 어노테이션(annotation)이나 태그로 역할을 지정하는 방식과 같은 구조입니다.

아래 표에서 **Required(필수)는** 해당 타입 클래스가 설정된 스키마에 반드시 있어야 함을 뜻합니다. 표의 종류마다 요구 사항이 하나씩 더 붙습니다.

* **객체 속성:** 필수 속성은 저장된 객체에 값도 있어야 합니다.
* **액션 파라미터:** 액션은 Vulcan이 값을 제공할 수 있도록, 나열된 타입 클래스와 데이터 타입을 가진 파라미터를 노출해야 합니다.
* **링크 타입:** Vulcan이 탐색할 수 있도록 링크 타입에 나열된 타입 클래스가 붙어 있어야 합니다.

> **중간 요약**: Vulcan은 `kind`가 `"vulcan"`인 타입 클래스로 속성, 액션 파라미터, 링크 타입을 찾으므로 이름은 자유롭게 정하고 아래 표의 타입 클래스만 정확히 붙이면 됩니다. 필수 항목은 스키마에 있어야 하고, 객체 속성은 값까지 있어야 합니다.

<a id="object-types"></a>
## 객체 타입 (Object types)

Vulcan은 다음 객체 타입을 읽고 씁니다. 각 표는 Vulcan이 해당 객체 타입의 속성에서 찾는 타입 클래스를 나열합니다.

<a id="cad-object"></a>
### CAD 객체 (CAD object)

Vulcan이 렌더링할 수 있는 3D 모델을 나타냅니다. 모델 형상은 미디어 참조(media reference)로 저장됩니다.

| 타입 클래스 (`name`) | 필수 | 데이터 타입 | 설명 |
| --- | --- | --- | --- |
| `cad_media_reference` | 예 | Media reference | CAD 모델 파일입니다. 이 속성은 [지원하는 모델 형식](01_overview.md#supported-model-formats)에 나열된 어떤 형식이든 받습니다. Vulcan은 파일 확장자로 형식을 판별합니다. |
| `up_axis` | 아니요 | String | 모델의 위쪽 축(up-axis) 규약입니다. 허용 값은 `X`, `Y`, `Z`입니다. 생략하면 Vulcan은 형식별 기본값을 적용합니다: `GLB`와 `GLTF`는 `Y`, `STL`, `OBJ`, `PLY`, `3MF`, `DXF`, `LAS`, `LAZ`는 `Z`. |
| `model_unit` | 아니요 | String | 파일이 자체 단위를 선언하지 않을 때 Vulcan이 모델 좌표를 어떻게 해석할지 정합니다. 단위를 절대 선언하지 않는 `OBJ`, `STL`, `PLY`, `DXF`, `LAS`, `LAZ`에 이 속성을 설정하세요. `GLB`, `GLTF`, `3MF`에는 아무 효과가 없습니다. Vulcan은 이 형식들이 선언한 단위를 항상 읽기 때문입니다. 허용 값은 `m`(또는 `meter` / `metre`)과 `mm`(또는 `millimeter` / `millimetre`)입니다. Vulcan은 그 밖의 값은 무시합니다. |

**설명**: 위쪽 축 규약은 3D 좌표계에서 어느 축이 "위"인지를 뜻합니다. 같은 모델이라도 Y축이 위라고 가정한 프로그램에서 만든 파일을 Z축이 위라고 가정하고 열면 모델이 90도 누워 보입니다. `up_axis` 속성으로 이를 바로잡을 수 있습니다.

<a id="annotation"></a>
### 주석 (Annotation)

CAD 모델의 한 부품에 붙은 주석을 나타냅니다. 주석은 텍스트 라벨, 3D 부착 지점, 작성자와 의도에 관한 메타데이터를 결합합니다.

| 타입 클래스 (`name`) | 필수 | 데이터 타입 | 설명 |
| --- | --- | --- | --- |
| `annotation_id` | 예 | String | 주석의 고유 식별자입니다. |
| `annotation_title` | 예 | String | 주석과 함께 표시되는 짧은 라벨입니다. |
| `annotation_content` | 예 | String | 더 긴 본문 텍스트입니다. |
| `part_instance_id` | 예 | String | 주석이 붙은 부품 인스턴스의 식별자입니다. |
| `annotation_attachment_x` | 예 | Double | 부착 지점의 X 좌표(모델 단위)입니다. |
| `annotation_attachment_y` | 예 | Double | 부착 지점의 Y 좌표(모델 단위)입니다. |
| `annotation_attachment_z` | 예 | Double | 부착 지점의 Z 좌표(모델 단위)입니다. |
| `annotation_sphere_size` | 예 | Double | 모델 단위로 나타낸 마커 반지름입니다. 점 마커로 렌더링하려면 `0`을 사용합니다. |
| `annotation_created_by` | 예 | String | 주석을 만든 사용자의 식별자입니다. |
| `annotation_intent` | 예 | String | 주석 마커의 시각적 의도입니다. 아래 [의도 값](#intent-values)을 참고하세요. |
| `annotation_timestamp` | 예 | Timestamp | 주석이 만들어진 시각입니다. |

<a id="intent-values"></a>
#### 의도 값 (Intent values)

`annotation_intent` 속성은 다음 문자열 값 중 하나를 받습니다. Vulcan은 값마다 다른 마커 색으로 렌더링하므로, 사용자가 한눈에 알아볼 수 있는 방식으로 심각도나 범주를 표현할 수 있습니다. Vulcan은 이 값들에 의미를 강제하지 않으므로, 자신의 워크플로에 맞게 정해 쓸 수 있습니다.

| 값 | 마커 색 |
| --- | --- |
| `none` | 회색 |
| `primary` | 파란색(새 주석을 만들 때의 기본값) |
| `success` | 녹색 |
| `warning` | 노란색 |
| `danger` | 빨간색 |

**설명**: 주석 객체 하나를 구체적인 행으로 보면 예를 들어 다음과 같습니다: `annotation_id`="A-001", `annotation_title`="용접 균열", `part_instance_id`="bracket-3", 좌표 (12.0, 4.5, 30.2), `annotation_sphere_size`=2.0, `annotation_intent`="danger", 작성자 "kim", 시각 2026-03-01T09:00Z. Vulcan은 이 행을 읽어 bracket-3 부품의 해당 좌표에 반지름 2인 빨간 구를 그립니다.

<a id="measurement"></a>
### 측정 (Measurement)

모델 위 두 개 이상의 점 사이에서 기록한 거리 측정을 나타냅니다.

| 타입 클래스 (`name`) | 필수 | 데이터 타입 | 설명 |
| --- | --- | --- | --- |
| `measurement_id` | 예 | String | 측정의 고유 식별자입니다. |
| `measurement_points` | 예 | Array of doubles | 측정을 정의하는 순서 있는 3D 점 좌표로, 평평한(flat) 숫자 배열로 직렬화됩니다. 아래 [점 형식](#points-format)을 참고하세요. |
| `measurement_created_by` | 예 | String | 측정을 만든 사용자의 식별자입니다. |
| `measurement_timestamp` | 예 | Timestamp | 측정이 만들어진 시각입니다. |

<a id="points-format"></a>
#### 점 형식 (Points format)

측정 점들은 모델의 좌표 공간에서 `[x1, y1, z1, x2, y2, z2, ...]` 순서의 평평한 숫자 배열로 직렬화됩니다. 따라서 점 두 개짜리 측정은 숫자 6개를, 점 세 개짜리 측정은 숫자 9개를 담습니다. 점들은 순서 있는 폴리라인으로 해석되며, Vulcan이 측정에 대해 보고하는 전체 거리는 연속한 점들 사이 거리의 합입니다.

**설명**: 예를 들어 `[0,0,0, 3,4,0, 3,4,12]`는 점 (0,0,0), (3,4,0), (3,4,12) 세 개입니다. 첫 구간 길이는 √(3²+4²)=5, 둘째 구간 길이는 12이므로 Vulcan이 보고하는 거리는 17입니다. 3차원 점의 배열을 중첩 배열 `[[x,y,z],...]` 대신 1차원 배열로 펴서 저장하는 이유는 속성 데이터 타입이 "Array of doubles"(실수의 1차원 배열)이기 때문입니다.

<a id="section-plane"></a>
### 단면 평면 (Section plane)

모델을 가로지르는 단면 평면을 나타냅니다.

| 타입 클래스 (`name`) | 필수 | 데이터 타입 | 설명 |
| --- | --- | --- | --- |
| `section_plane_id` | 예 | String | 단면 평면의 고유 식별자입니다. |
| `section_plane_position` | 예 | Array of doubles | `[x, y, z]` 순서의 위치 값 정확히 3개입니다. |
| `section_plane_quaternion` | 예 | Array of doubles | `[x, y, z, w]` 순서의 쿼터니언(quaternion) 값 정확히 4개입니다. |
| `section_plane_created_by` | 예 | String | 단면 평면을 만든 사용자의 식별자입니다. |
| `section_plane_timestamp` | 예 | Timestamp | 단면 평면이 만들어진 시각입니다. |

**설명**: 쿼터니언은 3D 회전을 숫자 4개로 표현하는 방법으로, 3D 그래픽스에서 회전을 저장할 때 널리 쓰입니다. 위치(평면이 놓인 점)와 쿼터니언(평면이 기울어진 방향)을 함께 저장하면 단면 평면을 정확히 재현할 수 있습니다. 예를 들어 `[0, 0, 0, 1]`은 회전이 없는 상태입니다.

> **중간 요약**: Vulcan이 쓰는 객체 타입은 CAD 객체(모델 파일, 위쪽 축, 단위), 주석(식별자, 제목, 본문, 부품, 좌표, 마커 크기, 작성자, 의도, 시각), 측정(식별자, 평평한 점 배열, 작성자, 시각), 단면 평면(식별자, 위치 3개 값, 쿼터니언 4개 값, 작성자, 시각) 네 가지입니다.

<a id="action-types"></a>
## 액션 타입 (Action types)

Vulcan은 액션을 통해 주석, 측정값, 단면 평면을 온톨로지에 다시 기록합니다. 각 액션 타입은 그 액션이 가진 파라미터 타입 클래스의 집합으로 식별됩니다.

아래 표에는 Vulcan이 제공하는 파라미터만 나열되어 있습니다. 생성되는 객체의 나머지 필수 속성은 모두 액션 정의에서 채워야 합니다.

* 세 액션 모두에서 객체 ID와 작성자 속성. 작성자 속성(`annotation_created_by`, `measurement_created_by`, `section_plane_created_by`)은 액션을 제출한 사용자로 설정합니다.
* **Create measurement**와 **Create section plane** 액션에서 타임스탬프 속성. Vulcan은 **Create annotation**에 대해서만 `annotation_timestamp`를 제공합니다.

추가 액션 파라미터에는 Vulcan 타입 클래스가 필요 없습니다. [Workshop 위젯](04_widget.md#actions)에서 액션을 설정할 때 이 파라미터들에 기본값을 주거나 사용자 입력 필드로 노출할 수 있습니다.

**설명**: 예를 들어 **Create measurement** 액션을 만들 때 Vulcan은 `measurement_points` 값만 넘겨 줍니다. 따라서 액션 정의의 규칙에서 `measurement_id`는 새 UUID 같은 고유값으로, `measurement_created_by`는 "현재 사용자"로, `measurement_timestamp`는 "현재 시각"으로 채우도록 설정해야 합니다. 그렇지 않으면 필수 속성이 빈 객체가 만들어집니다.

<a id="create-annotation"></a>
### 주석 만들기 (Create annotation)

| 파라미터 타입 클래스 (`name`) | 필수 | 데이터 타입 | 설명 |
| --- | --- | --- | --- |
| `annotation_title` | 예 | String | 짧은 라벨입니다. |
| `annotation_content` | 예 | String | 본문 텍스트입니다. |
| `part_instance_id` | 예 | String | 주석이 붙을 부품 인스턴스입니다. |
| `annotation_attachment_x` | 예 | Double | 부착 지점의 X 좌표입니다. |
| `annotation_attachment_y` | 예 | Double | 부착 지점의 Y 좌표입니다. |
| `annotation_attachment_z` | 예 | Double | 부착 지점의 Z 좌표입니다. |
| `annotation_sphere_size` | 예 | Double | 모델 단위로 나타낸 마커 반지름입니다. 점 마커는 `0`을 사용합니다. |
| `annotation_intent` | 예 | String | 범주 또는 심각도입니다. |
| `annotation_timestamp` | 예 | Timestamp | 생성 시각입니다. |
| `cad_object` | 예 | Object reference | 주석이 속한 CAD 객체에 대한 참조입니다. |

<a id="create-measurement"></a>
### 측정 만들기 (Create measurement)

| 파라미터 타입 클래스 (`name`) | 필수 | 데이터 타입 | 설명 |
| --- | --- | --- | --- |
| `measurement_points` | 예 | Array of doubles | `[x1, y1, z1, x2, y2, z2, ...]` 형식의 순서 있는 점 좌표입니다. |

<a id="create-section-plane"></a>
### 단면 평면 만들기 (Create section plane)

| 파라미터 타입 클래스 (`name`) | 필수 | 데이터 타입 | 설명 |
| --- | --- | --- | --- |
| `section_plane_position` | 예 | Array of doubles | `[x, y, z]` 순서의 위치 값 정확히 3개입니다. |
| `section_plane_quaternion` | 예 | Array of doubles | `[x, y, z, w]` 순서의 쿼터니언 값 정확히 4개입니다. |

> **중간 요약**: Vulcan은 파라미터 타입 클래스 조합으로 주석, 측정, 단면 평면 생성 액션을 찾아 필요한 값만 넘깁니다. ID, 작성자, (측정과 단면 평면의) 타임스탬프 같은 나머지 필수 속성은 액션 정의에서 직접 채워야 합니다.

<a id="link-types"></a>
## 링크 타입 (Link types)

| 타입 클래스 (`name`) | 필수 | 설명 |
| --- | --- | --- |
| `cad_object` | 예 | 주석을 그 상위 CAD 객체와 연결합니다. |

**설명**: 데이터베이스로 보면 주석 테이블에 CAD 객체를 가리키는 외래 키가 있고, 이 관계를 정의한 링크 타입에 `cad_object` 타입 클래스를 붙이는 것입니다. Vulcan은 이 링크를 따라 "지금 열려 있는 CAD 객체에 달린 주석"을 조회합니다.

## 정리

- Vulcan은 속성 이름이 아니라 `vulcan` 네임스페이스의 타입 클래스로 속성, 액션 파라미터, 링크 타입을 찾습니다.
- 객체 타입: CAD 객체, 주석, 측정, 단면 평면. 각 표의 필수 타입 클래스를 속성에 붙이고 값을 채워야 합니다.
- 주석 의도 값(`none`, `primary`, `success`, `warning`, `danger`)은 마커 색을 정하며 의미는 자유롭게 정할 수 있습니다.
- 측정 점은 `[x1, y1, z1, ...]` 평평한 배열이고 거리는 폴리라인 길이의 합이며, 단면 평면은 위치 3개 값과 쿼터니언 4개 값으로 저장됩니다.
- 생성 액션 세 가지에서 Vulcan이 넘기지 않는 ID, 작성자, 타임스탬프는 액션 정의에서 채우고, 주석과 CAD 객체 사이 링크 타입에는 `cad_object` 타입 클래스를 붙입니다.
- 스키마는 릴리스마다 바뀔 수 있으므로 이 페이지와 대조해 확인해야 합니다.
