# 플랫폼에서 전체 Object View 사용하기 (Use full Object Views in the platform)

- 원문: https://www.palantir.com/docs/foundry/object-views/use-full-views-in-platform/
- 사이드바 위치: Applications > Object Views > Full Object Views > Use full Object Views in the platform

이 페이지는 객체 하나의 정보를 한 화면 가득 보여 주는 전체(full) Object View가 Foundry의 어느 곳에서 나타나는지 소개합니다. Workshop, Object Explorer, 그 밖의 플랫폼 애플리케이션에서 같은 Object View가 재사용된다는 점을 알면, Object View를 한 번 잘 구성하는 것이 왜 중요한지 이해할 수 있습니다.

전체 Object View(full Object View)는 객체 데이터를 포괄적으로 보여 주는 화면입니다. 플랫폼 안에서 객체를 볼 때 쓰는 기본 뷰이며, 플랫폼 애플리케이션 안에서 열거나 사용자 정의 Workshop 애플리케이션에 삽입할 수 있습니다.

전체 `Patient` Object View의 예시:

![전체 환자 Object View 예시.](https://www.palantir.com/docs/resources/foundry/object-views/overview-full-object-view.png)

전체 `Rental` Object View의 예시:

![전체 렌털 Object View 예시.](https://www.palantir.com/docs/resources/foundry/object-views/full-object-view-airport-example.png)

<a id="workshop"></a>
## Workshop

[Workshop의 Object View 위젯](https://www.palantir.com/docs/foundry/workshop/widgets-object-view/)은 사용자 정의 Workshop 애플리케이션 안에 상세한 Object View를 표시할 수 있습니다. 전체 Object View를 표시하도록 구성한 경우, 이 위젯은 전체 페이지 크기를 수용하기 위해 오버레이(overlay)나 모달(modal) 안에서 자주 사용됩니다.

![Workshop Object View 위젯 예시.](https://www.palantir.com/docs/resources/foundry/object-views/workshop-object-view-widget-example.gif)

**설명**: 모달은 현재 화면 위에 떠서 열리는 창이고, 오버레이는 기존 화면 위를 덮어 표시되는 영역입니다. 전체 Object View는 넓은 공간이 필요하므로, Workshop 앱의 한 귀퉁이에 넣기보다 사용자가 목록에서 객체를 클릭하면 위에 크게 띄우는 방식으로 쓰는 경우가 많다는 뜻입니다.

<a id="object-explorer"></a>
## Object Explorer

[Object Explorer](../../01_object-explorer/01_overview.md)에서 객체를 검색한 뒤 선택하면 전체 Object View가 열리며, 온톨로지에 정의된 객체에 대한 상세 정보를 제공합니다.

![Object Explorer의 전체 Object View](https://www.palantir.com/docs/resources/foundry/object-views/object-explorer-full-object-view.png)

<a id="platform-applications"></a>
## 플랫폼 애플리케이션 (Platform applications)

Vertex, Maps, Gaia 같은 애플리케이션은 패널 Object View를 사용해, 선택한 객체를 사용자 정의 가능한 간결한 형태로 보여 줍니다. 패널 안에서 객체의 제목을 선택하면 이동과 크기 조절이 가능한 모달에 전체 Object View가 열립니다.

![Vertex 애플리케이션 안의 모달에 표시된 전체 Object View.](https://www.palantir.com/docs/resources/foundry/object-views/vertex-full-object-view.gif)

## 정리

- 전체 Object View는 객체 하나의 데이터를 포괄적으로 보여 주는, 플랫폼의 기본 객체 화면입니다.
- Workshop에서는 Object View 위젯으로 삽입하며, 보통 오버레이나 모달 안에 둡니다.
- Object Explorer에서 객체를 검색해 선택하면 전체 Object View가 열립니다.
- Vertex, Maps, Gaia에서는 패널 Object View의 객체 제목을 선택하면 전체 Object View가 모달로 열립니다.
