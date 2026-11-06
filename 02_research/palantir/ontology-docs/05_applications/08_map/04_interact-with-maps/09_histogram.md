# 히스토그램과 필터링 (Histogram and filtering)

- 원문: https://www.palantir.com/docs/foundry/map/histogram/
- 사이드바 위치: Applications > Map > Interact with maps > Histogram and filtering

이 페이지는 Map 애플리케이션의 **Histogram** 패널로 지도 위 객체를 속성 값별로 세고, 선택하고, 필터링하는 방법을 다룹니다. 지도에 객체가 많을 때 "어떤 값을 가진 객체가 몇 개인지"를 보고 원하는 객체만 남기는 데 쓰입니다. 정렬, 날짜와 숫자 속성의 구간 나누기(binning), 선택 방법, 필터 동작을 설명합니다.

**Histogram** 패널을 사용하면 지도에 있는 객체 데이터를 선택하고 필터링할 수 있습니다. 패널의 첫 번째 섹션인 **Object types**는 지도에 있는 객체 수를 객체 타입별로 보여 줍니다. 그 아래에는 지도에 있는 모든 객체 타입에 걸쳐 속성 타입마다 섹션이 하나씩 있습니다. 패널 상단의 필터 상자를 사용하면 이름이 일치하는 속성으로 결과를 좁힐 수 있습니다.

<a id="use-the-histogram"></a>
## 히스토그램 사용하기 (Use the histogram)

히스토그램 섹션을 펼치면 해당 속성의 고유한 값마다 행이 하나씩 표시되며, 기본적으로 값의 개수 순으로 정렬한 상위 5개로 제한됩니다. **Show more**를 클릭하면 다음 5개 행이 표시됩니다.

**Value** 머리글을 클릭하면 정렬 방식이 **Value**(오름차순)와 **Value**(내림차순) 사이에서 전환됩니다. **Count** 머리글을 클릭하면 정렬 방식이 **Count**(내림차순), **Count**(오름차순), **Selected Count**(내림차순), **Selected Count**(오름차순) 사이에서 전환됩니다.

| Value | Count | Selected count |
|---|---|---|
| ![값의 알파벳순으로 정렬한 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-value.png) | ![개수로 정렬한 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-count.png) | ![선택된 개수로 정렬한 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-selected-count.png) |

**설명**: 히스토그램 섹션 하나는 SQL의 `SELECT 속성, COUNT(*) FROM 지도위객체 GROUP BY 속성 ORDER BY COUNT(*) DESC LIMIT 5`와 같은 결과를 보여 줍니다. 예를 들어 지도에 항공기 객체 20대가 있고 `status` 속성이 `active` 12대, `maintenance` 6대, `retired` 2대라면, `status` 섹션에 세 행이 개수와 함께 나옵니다. Selected Count는 그중 현재 선택된 객체의 개수입니다.

날짜와 숫자 속성에는 **Binning**(구간 나누기)을 제어하는 옵션이 추가로 있습니다.

날짜 속성의 경우, 이 머리글을 클릭하면 구간 나누기 방식이 **Year**(연), **Year and month**(연월), **Quarter**(분기), **Month**(월), **Day**(일) 사이에서 전환됩니다. 예시 이미지를 클릭하면 크게 볼 수 있습니다.

| Year | Year and month | Quarter | Month | Day |
|---|---|---|---|---|
| ![연 단위로 구간을 나눈 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-binning-year.png) | ![연월 단위로 구간을 나눈 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-binning-year-and-month.png) | ![분기 단위로 구간을 나눈 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-binning-quarter.png) | ![연중 월 단위로 구간을 나눈 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-binning-month.png) | ![요일 단위로 구간을 나눈 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-binning-day.png) |

**설명**: 이미지 설명을 보면 **Year and month**는 "2024년 3월"처럼 연도까지 구분하는 구간이고, **Month**는 연도와 상관없이 "3월"끼리 묶는 구간(연중 월), **Day**는 요일별로 묶는 구간입니다. 예를 들어 2023년 3월과 2024년 3월의 사건은 **Year and month**에서는 다른 행, **Month**에서는 같은 행에 들어갑니다.

숫자 속성의 경우, 이 머리글을 클릭하면 구간 나누기 방식이 **No binning**(구간 없음), **Equal size**(같은 크기, 숫자 값을 같은 크기의 구간으로 자동 묶음), **Logarithmic**(로그, 숫자 값을 자릿수 크기 순서로 묶음) 사이에서 전환됩니다.

| No binning | Equal size | Logarithmic |
|---|---|---|
| ![숫자 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-binning-none.png) | ![같은 크기 구간으로 나눈 숫자 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-binning-equal-size.png) | ![로그 크기 구간으로 나눈 숫자 히스토그램](https://www.palantir.com/docs/resources/foundry/map/histogram-binning-log.png) |

**설명**: 값이 3, 45, 80, 950, 12000이라면 Equal size는 전체 범위를 같은 폭으로 나누므로(구간 수는 자동으로 정해짐) 작은 값들이 한 구간에 몰리기 쉽습니다. Logarithmic은 1\~10, 10\~100, 100\~1000, 1000\~10000처럼 10배씩 커지는 구간을 쓰므로 3, (45와 80), 950, 12000이 각각 다른 구간에 들어갑니다. 값의 범위가 여러 자릿수에 걸쳐 있을 때 로그 구간이 분포를 보기 좋습니다.

> **중간 요약**: Histogram 패널은 객체 타입별 개수와 속성 값별 개수를 보여 주며, 기본 상위 5개를 표시하고 값이나 개수로 정렬할 수 있습니다. 날짜 속성은 연, 연월, 분기, 월, 요일 단위로, 숫자 속성은 구간 없음, 같은 크기, 로그 구간으로 묶을 수 있습니다.

<a id="selection"></a>
## 선택 (Selection)

**Histogram** 패널에서 행을 클릭하면 일치하는 모든 객체가 선택됩니다. Shift를 누른 채 두 번째 행을 선택하면 행 범위가 선택됩니다. Ctrl(Windows) 또는 Cmd(Mac)를 누른 채 선택하면 기존 선택에 행이 추가됩니다. 이렇게 하면 히스토그램의 여러 섹션에 걸쳐 행을 선택할 수 있습니다.

![히스토그램 행이 선택된 Map 애플리케이션](https://www.palantir.com/docs/resources/foundry/map/histogram-filters-selected.png)

<a id="filtering"></a>
## 필터링 (Filtering)

히스토그램 행이 선택되어 있으면 **Filter to** 또는 **Filter out** 버튼으로 필터를 만들 수 있습니다. 필터는 조건에 맞지 않는 객체의 불투명도를 일시적으로 낮춥니다. 이 객체들은 상호작용할 수 없게 되며 히스토그램 통계에도 반영되지 않습니다. 필터가 있으면 메인 애플리케이션 툴바 위의 막대에 표시됩니다. 필터는 필터의 **x** 버튼으로 하나씩 제거하거나, **Clear filters** 버튼으로 모두 제거할 수 있습니다. 필터는 지도와 함께 저장되지 않습니다.

**Filter to**를 선택하면 선택한 행과 일치하는 객체만 남도록 지도가 필터링됩니다.

![객체가 필터로 남겨진(filter to) Map 애플리케이션](https://www.palantir.com/docs/resources/foundry/map/histogram-filtered-in.png)

**Filter out**을 선택하면 선택한 행과 일치하지 않는 객체만 남도록 지도가 필터링됩니다.

![객체가 필터로 제외된(filter out) Map 애플리케이션](https://www.palantir.com/docs/resources/foundry/map/histogram-filtered-out.png)

**Filter to**와 **Filter out** 버튼 외에도, 히스토그램 행을 더블클릭해 그 행 하나로 필터링할 수 있습니다. 현재 선택된 모든 객체로 필터링하려면 지도의 오른쪽 클릭 메뉴에서 **Filter to selected objects** 메뉴 항목을 사용합니다.

**설명**: 선택과 필터는 다릅니다. 선택은 객체를 강조 표시하고 다른 작업의 대상으로 삼는 것이고, 필터는 조건에 맞지 않는 객체를 흐리게 만들어 상호작용과 통계 계산에서 빼는 것입니다. 위의 항공기 예시에서 `maintenance` 행을 선택하고 **Filter to**를 누르면 정비 중인 6대만 또렷하게 남고, 다른 히스토그램 섹션(예: `manufacturer`)의 개수도 그 6대 기준으로 다시 계산됩니다. **Filter out**을 누르면 반대로 정비 중이 아닌 14대가 남습니다. SQL로는 각각 `WHERE status = 'maintenance'`와 `WHERE status <> 'maintenance'`에 해당합니다.

> **중간 요약**: 행 클릭으로 객체를 선택하고 Shift(범위)와 Ctrl/Cmd(추가)로 여러 행을 고를 수 있습니다. **Filter to**와 **Filter out**은 맞지 않는 객체를 흐리게 하고 통계에서 빼며, 필터는 지도와 함께 저장되지 않습니다.

## 정리

- **Histogram** 패널은 지도 위 객체를 객체 타입별, 속성 값별로 세어 보여 줍니다.
- 기본으로 상위 5개 값을 개수순으로 보여 주며, 값, 개수, 선택된 개수로 정렬을 바꿀 수 있습니다.
- 날짜 속성은 연, 연월, 분기, 월, 요일로, 숫자 속성은 구간 없음, 같은 크기, 로그로 구간을 나눌 수 있습니다.
- 행을 클릭해 객체를 선택하고, **Filter to**나 **Filter out**, 더블클릭, **Filter to selected objects**로 필터를 만듭니다.
- 필터는 맞지 않는 객체를 흐리게 하고 상호작용과 통계에서 제외하며, 지도에 저장되지 않습니다.
