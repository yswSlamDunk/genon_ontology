# F3. 데이터소스

- 상태: 초안 v0.1 (2026-11-01, Claude 작성) — 사용자 보정 전
- 원본 기준: `../../analysis/ontological-studio/menus/03-datasources/design.md`, `user-scenarios.md` (S1–S12)
- 관련: [02 §7 Backing source](../02-ontology-model.md), [02 §16 발행 컴파일](../02-ontology-model.md), [03 §7 비밀 관리](../03-security.md), [F1 온톨로지 구축](F1-ontology-build.md)(속성 매핑 편집기), [F4 그래프 콘솔](F4-graph-console.md), [F8 설정](F8-settings.md)

---

## 1. 목적
원천 업무 DB를 **데이터를 복사하지 않고** 플랫폼에 연결하고, 원천 테이블의 구조와 실제 행을 확인하며, 그 테이블을 **Object type의 백킹 데이터(Backing source)** 로 연결하는 출발점이 되는 화면.

원본에서 이 화면은 "테이블 하나 = 가상 노드 타입 하나"를 만드는 곳이었다. 새 설계에서 사용자가 만드는 것은 **Object type과 그 백킹 매핑**이며(02 §7), 가상 노드·가상 관계는 발행 컴파일러가 만드는 **내부 결과물**(02 §16)로 내려간다. 원본의 패브릭 문장 기능은 "고급"으로 남긴다.

## 2. 원본 기준 동작 요약 [원본]
근거: 분석 `menus/03-datasources/design.md` §1–§11.
- 3단 레이아웃: 왼쪽(`Data fabric`, 데이터소스 목록, 가상 그래프 목록, 「Ontological Portal 에서 질의」) / 가운데(테이블 목록, 「테이블 찾기」) / 오른쪽(컬럼 표, 미리보기 또는 「가상 노드로 노출」 카드).
- 모든 쓰기 = 패브릭 문장 1개. 폼 값이 바뀌면 180ms 디바운스로 `dry: true` 요청을 보내 「실행될 문장」을 미리 보여 준다. 비밀번호는 표시 문장에서 항상 `'••••'`.
- 연결 대화상자: 엔진 4종(PostgreSQL / MySQL · MariaDB / Oracle / SQL Server · Azure SQL), 설치되지 않은 커넥터는 「— 이 설치에 없음」 비활성. 엔진별 기본 포트·스키마(5432/`public`, 3306/없음, 1521/빈칸, 1433/`dbo`). 이름 규칙 `^[a-z_][a-z0-9_]*$`.
- 데이터소스 **수정 화면 없음**(해제 후 재연결). 「테이블 다시 읽기」는 새 테이블만 가져온다(컬럼 변경 미반영 추정).
- 미리보기는 **가상 노드가 있는 테이블만** 가능(`MATCH (n:<Label>) RETURN n LIMIT 20`). 바닥 문구 `<n>행 · Bolt → Ontological → <커넥터> → 원천`.
- 「가상 노드로 노출」: 노드 이름 자동 생성(파스칼 표기), KEY 컬럼 추정, 컬럼별 체크·이름 바꾸기 → `CREATE VIRTUAL NODE … KEY … [PROPERTIES (…)]`.
- 가상 그래프 뷰: 지도(열 = 데이터소스), 노드 타입 표, 관계 표, 「관계 만들기」(두 속성 값이 같은 행끼리 잇는 조인).
- 의존 거절: 가상 노드가 쓰는 데이터소스 해제 거절, 관계가 이어진 노드 삭제 거절. 한국어 번역 배너 + 엔진 원문.
- 「실행한 문장」 막대: **쓰기 문장만**, 최신순 30건, 메모리에만(새로 고침하면 사라짐). 튜토리얼은 읽기 문장도 남는 것처럼 설명 → 불일치(REVIEW #6).
- 비밀번호는 엔진 사용자 매핑에 평문 옵션으로 저장(REVIEW #5). 브리지는 인증 없이 그래프 관리자 계정으로 동작.
- 예제 시드: 데이터소스 `crm`·`erp`·`wms`, 그래프 `sample`에 가상 노드 7·관계 5.

## 3. 새 설계에서 달라지는 점 [제안]
| # | 원본 | 새 설계 | 근거 |
|---|---|---|---|
| C1 | 화면의 결과물 = 가상 노드·가상 관계 | 화면의 결과물 = **데이터소스 연결 + Object type 백킹 매핑(작업본)**. 테이블에서 「Object type으로 만들기」/「기존 Object type에 매핑」 → F1 속성 매핑 편집기 | 02 §7, 원칙 1 |
| C2 | 가상 노드 = 사용자 개념 | 가상 노드·관계 = 발행 컴파일 대상(02 §16). 화면에는 「고급 › 패브릭」에서 **읽기 전용 검사기**로 보이고, 원본식 직접 생성은 관리되지 않는 그래프(예: `sample`)에서만 | 02 §16 |
| C3 | 미리보기는 가상 노드가 있어야 가능 | **모든 테이블 미리보기**(코어가 만드는 고정 형태 질의, 사용자 SQL 아님) | 백킹 매핑 전에 데이터를 봐야 하므로 |
| C4 | 수정 불가, 해제 후 재연결 | 「연결 정보 수정」(호스트·포트·사용자·비밀번호 등. 이름·엔진은 불변) + 「연결 시험」 | 사용성 |
| C5 | 비밀번호 평문(사용자 매핑) | OS 키체인 + `secret_ref`. 엔진 사용자 매핑은 [결정 대기 D-09] 권장안대로 **접속 시점 생성·종료 시 폐기** | 03 §7, S6 |
| C6 | 「실행한 문장」: 쓰기만, 30건, 메모리 | **읽기·쓰기 모두 기록**(튜토리얼 설명을 따름), 코어에 영구 보관, 막대에는 최근 30건, 「읽기 문장 숨기기」 필터 | D-12 (튜토리얼이 더 합리적) |
| C7 | 「테이블 다시 읽기」= 새 테이블만 | 「구조 다시 읽기」: 새 테이블 + **기존 테이블의 컬럼 변경**까지 반영하고, 영향받는 백킹 매핑을 F1 검증 경고로 보냄 | 원본 결함(외래 테이블 컬럼 고정) |
| C8 | 해제 거절 기준 = 가상 노드 | 해제 거절 기준 = **이 데이터소스를 쓰는 Object type**(작업본·발행본 모두)과 Link type(join-source) | 02 §17-9 영향 분석 |
| C9 | 브리지(셸 내 별도 서버, 무인증, 그래프 관리자 계정) | 코어 **Data 모듈** API(`/api/v1/datasources…`), 세션 토큰 필수, 원천 읽기는 데이터소스별 읽기 역할 | 01 §2.1, 03 §3·§6 |
| C10 | 내장 PG 포트가 바뀌면 예제 데이터소스 3개만 재등록, 사용자 데이터소스는 옛 포트를 가리킴(REVIEW #4, 추정) | 내장 PG를 가리키는 데이터소스는 **"내장" 표식**을 두고, 포트가 바뀌면 예제·사용자 구분 없이 모두 다시 가리킴 | 결함 수정 |
| C11 | 가상 그래프 지도(열 = 데이터소스, 노드 = 가상 노드) | **백킹 지도**: 열 = 데이터소스, 상자 = 테이블, 오른쪽 = 그 테이블을 쓰는 Object type(주 원천 실선, 보강 원천 점선), 아래 = 테이블 간 Link type | 02 §7·§8 |

### 3.1 "패브릭 문장"의 새 위치
- 원본 화면이 보여 주던 패브릭 문장(`CREATE DATASOURCE …`, `REFRESH DATASOURCE …`, `DROP DATASOURCE …`)은 **연결 관리**에 한해 그대로 「실행될 문장」/「실행한 문장」에 보인다. 이 문장 문법은 그래프 엔진 선택(D-02)과 무관하게 코어가 유지하는 **표시 계약**이다. D-02 A안이면 엔진에 실제로 그 문장이 실행되고, B안이면 코어가 같은 문법으로 표시하고 내부적으로 동등한 작업을 한다. [결정 대기 D-02]
- 가상 노드·가상 관계 문장은 일반 흐름에서 사라진다. 대신:
  1. **발행 결과 검사기**(읽기 전용): 「고급 › 패브릭」 탭에서 발행 컴파일이 만든 가상 타입·관계를 원본 표와 같은 열(노드·원천·KEY·속성 수·저장)로 보여 주고, 각 행에 "어느 Object type/Link type에서 나왔는지"를 표시한다. 문장 열에는 컴파일러가 실행한 `CREATE VIRTUAL NODE …` 문장을 보여 준다.
  2. **관리되지 않는 그래프의 직접 편집**(고급): `sample`처럼 온톨로지 발행이 관리하지 않는 그래프에서는 원본의 「가상 노드로 노출」·「관계 만들기」·삭제를 **원본과 같은 화면·문장**으로 쓸 수 있다(튜토리얼 06 재현과 비교 테스트용). 발행이 관리하는 그래프에 대한 가상 타입 DDL은 거부한다(§10 E-11).
  3. F4 콘솔에서 `SHOW …` 패브릭 문장은 항상 실행 가능, 가상 타입 DDL은 위 2와 같은 조건 + 설정의 콘솔 쓰기(D-20)가 켜져 있을 때만.
- `CREATE DATASOURCE`를 콘솔 문장으로 직접 실행하는 것은 막는다(비밀번호가 질의 기록·감사에 남으므로). 연결은 이 화면에서만. [제안]

## 4. 사용자 시나리오
원본 시나리오 번호(S)와 대응. 새 시나리오는 N-번호.

| # | 시나리오 | 원본 대응 | 새 기대 결과 요약 |
|---|---|---|---|
| S1 | 탭 열고 구성 보기 | S1 | 왼쪽 「데이터소스 3」(`crm`·`erp`·`wms`), 아랫줄 `127.0.0.1 · 테이블 N · Object type M`. 첫 데이터소스 자동 선택 → 테이블 목록 → 첫 테이블 상세 |
| S2 | 테이블 구조·미리보기 | S2 | 모든 테이블에 미리보기. `wms.shipment` 최대 지연 `SHP-03`(9일, `CUSTOMS_HOLD`), `crm.claim` 3행. 바닥 문구는 경로 표시(§5.4) |
| S3 | 새 데이터소스 연결 | S3 | 같은 대화상자·기본값·필수 칸·이름 규칙 문구. 비밀번호는 키체인. 「연결 시험」 추가 |
| S4 | 실행한 문장 | S4 | 쓰기와 읽기가 모두 기록(의도된 차이), 앱 재시작 후에도 남음 |
| S5 | 구조 다시 읽기·연결 해제 | S5 | 해제 시 Object type이 쓰고 있으면 거절: 「Object type 발주, 협력사 이(가) 이 데이터소스를 백킹으로 쓰고 있어 해제할 수 없습니다. …」 |
| S6 | 테이블을 Object type으로 | S6(가상 노드로 노출) | `erp.po_line` → 「Object type으로 만들기」 → F1 매핑 편집기에 `PoLine`(표시 이름 `Po Line`), 기본 키 `poLineId`, 속성 4개 미리 채움 → 작업본 저장 → 발행 후 조회 가능 |
| S7 | 백킹 지도 | S7(가상 그래프 보기) | 열 = 데이터소스, 테이블 → Object type 연결선. 예제 온톨로지 기준 Object type 6개 |
| S8 | 테이블 간 관계 | S8(가상 관계) | 일반 흐름에서는 F1 Link type 편집기(foreign-key, 변환 허용)로 이동. 원본식 가상 관계는 `sample` 그래프 고급 화면에서 원본과 같게 |
| S9 | 삭제와 의존 거절 | S9 | 원본 문구 유지(고급 화면). Object type 의존 거절은 새 문구(§10) |
| S10 | 테이블 찾기 | S10 | 같음 + Object type 이름(표시 이름 포함)으로도 찾음 |
| S11 | 홈 최근 항목에서 열기 | S11 | 설명 `postgres · 테이블 3 · Object type 1`. 누르면 `ds=wms` 선택 상태로 열림 |
| S12 | 문장 복사·콘솔로 이동 | S12 | 미리보기 카드의 「Object set으로 보기」/「Cypher 복사」 → F4 콘솔(대상 온톨로지 자동 선택 — 원본은 그래프를 사용자가 바꿔야 했음) |
| N1 | 기존 Object type에 매핑 | 신규 | `wms.shipment` → 「기존 Object type에 매핑」 → `PurchaseOrder` 선택 → 역할 「보강」, 매칭 식 제안 `replace(ref_po_no, 'PO-', '')` ↔ `poId` → F1 편집기 |
| N2 | 연결 정보 수정 | 신규 | 비밀번호만 바꾸기 → 키체인 갱신 → 「연결 시험」 성공 → 기존 Object type 그대로 동작 |
| N3 | 구조 변경 감지 | 신규 | 원천에 컬럼 추가·삭제 → 「구조 다시 읽기」 → 변경 요약(추가 1, 삭제 1) + 삭제 컬럼을 매핑에 쓰는 Object type 경고 → F1 검증 오류로 표시 |
| N4 | 원본 가상 노드를 Object type으로 가져오기 | 신규(이행) | `sample` 그래프의 가상 노드 7개·관계 5개 선택 → 「Object type으로 가져오기」 → 새 온톨로지 작업본에 Object type 7, Link type 5(foreign-key) 생성(02 §18 이행표 규칙) |
| N5 | 비밀번호 보관 확인 | 신규(보안) | DB 덤프·로그·API 응답 어디에도 원천 비밀번호 평문 없음(D-09 결정에 따름) |
| N6 | 엔진 커넥터 없음 | S3 일부 | Windows 등에서 커넥터가 없는 엔진은 「— 이 설치에 없음」 비활성(원본과 같음) |

## 5. 화면 구성과 상호작용

### 5.1 레이아웃 (3단, 원본 유지)
- **왼쪽 사이드바**
  - 머리: 제목 `Data fabric`(원본 유지), 「＋」(title 「데이터소스 연결」).
  - 「데이터소스 N」 목록: 이름 + 엔진 태그(+ 내장 PG면 「내장」 태그), 아랫줄 `<host> · 테이블 <n> · Object type <m>`. 연결 오류 상태면 빨간 점 + 「연결 안 됨」. 비어 있으면 「연결된 데이터소스가 없습니다.」 + 「연결하기」(원본 문구).
  - 「백킹 지도」 항목(가상 그래프 목록 대체): 온톨로지별 한 줄 `<온톨로지 표시 이름> · Object type n · v<발행 버전>`.
  - 「고급 › 패브릭」 접힘 항목: 가상 그래프 목록(원본과 같은 표시: `sample` 「예제」 태그, 발행 관리 그래프는 「발행 관리」 태그·잠금 아이콘).
  - 하단 안내: 「데이터는 복사하지 않습니다. live Object type은 질의할 때마다 원천을 그 자리에서 읽습니다.」 + 「그래프 콘솔에서 질의」(F4 열기).
- **본문**: 데이터소스 뷰 / 백킹 지도 뷰 / 패브릭 뷰(고급) / 빈 상태 「왼쪽에서 데이터소스를 고르세요.」(원본 문구).
- **하단 「실행한 문장」 막대**: §5.7.
- 상단 오류: 「패브릭 정보를 읽지 못했습니다: <원문>」 + 「다시 시도」(원본 문구).

### 5.2 첫 진입 (원본 순서 유지)
1. 개요 조회 → 2. 주소의 `ds` 값이 실제 데이터소스면 그것, 아니면 첫 데이터소스 → 3. 테이블 목록 → 첫 테이블 → 컬럼 → 미리보기.
- 원본과 다른 점: 미리보기는 백킹 여부와 무관하게 항상 요청한다(C3).

### 5.3 데이터소스 뷰
- 머리: `Datasource`, 이름 + 엔진 태그, `<host> · 테이블 <n> · Object type <m>`, 마지막 구조 읽기 시각.
- 동작 버튼: 「구조 다시 읽기」(title 「REFRESH DATASOURCE — 원천의 새 테이블과 컬럼 변경을 가져옵니다」), 「연결 정보 수정」, 「연결 시험」, 「연결 해제」.
- 삭제류 확인 패턴(원본 유지): 첫 클릭 → 그 자리에 실행될 문장 + 「해제」/「취소」. **새로 추가**: 해제는 데이터 손실이 없으므로 네이티브 확인 창은 쓰지 않는다(03 §4 대상 아님).
- 오류 배너(원본 유지): 한국어 번역이 있으면 굵게 + 원문 코드.
- **가운데 테이블 목록**: 「테이블 찾기」(화면 내 필터: 테이블 이름, Object type apiName·displayName 부분 일치, 대소문자 무시). 항목 = 테이블 이름, 컬럼 수, 백킹 칩(`발주` — 주 원천은 채운 칩, 보강은 테두리 칩, 작업본에만 있으면 「초안」 표시).
- **오른쪽 상세**
  - **구조 카드**: `ds.table` + 사용처 칩 또는 「매핑 안 됨」. 표 `컬럼 | 타입 | 제약(NOT NULL) | 원천 키(PK) | 매핑(→ Object type.property)`. 원본의 `key` 열(가상 노드 KEY)은 「원천 키」(원천 카탈로그의 PK·유일 제약)와 「매핑」 열로 나눈다. PII 추정 컬럼(이름에 `email`, `phone`, `tel`, `ssn`, `birth`, `addr` 등)은 회색 「PII?」 표시(속성 생성 시 `pii: true` 기본 제안).
  - **미리보기 카드**: 라벨 「미리보기」, 문장 표시 `PREVIEW <ds>.<table> LIMIT 20`(사용자가 고칠 수 없는 고정 형태, §6.3), 「행 수 바꾸기」(20/50/200). 표 규칙은 원본과 같음(컬럼 표 순서, null은 `null`, 타입별 스타일). 로딩 「원천을 읽는 중…」(원본), 0행이면 「행이 없습니다.」. 바닥 `<행수>행 · 코어 → <커넥터> → 원천`(원본의 `Bolt → Ontological →` 부분은 엔진 경유가 아니므로 바꿈 — 의도된 차이).
    - 이 테이블이 발행된 live Object type의 주 원천이면 카드에 「Object set으로 보기」(F4 DSL 탭, `{base:{objectType: X}, limit: 20}`)와 「Cypher 복사」(`MATCH (n:\`<Ontology>.<Type>\`) RETURN n LIMIT 20`)를 둔다.
  - **백킹 카드**(원본 「가상 노드로 노출」 카드 자리):
    - 이 테이블을 쓰는 Object type 목록: `<표시 이름> (<apiName>) · 주 원천|보강 · live|indexed · 발행 v3|초안` + 「매핑 편집」(F1 편집기로 이동).
    - 버튼 **「Object type으로 만들기」**, **「기존 Object type에 매핑」**(§5.5). 안내 「원천 행 하나가 객체 하나가 됩니다. 데이터는 복사하지 않습니다(live).」
    - 대상 온톨로지 선택(기본: 최근 연 온톨로지 → 예제 온톨로지). 온톨로지가 없으면 「새 온톨로지」.

### 5.4 연결 대화상자 (원본 유지 + 추가)
- 작은 제목 `CREATE DATASOURCE`, 제목 「데이터소스 연결」, 배경 클릭·Esc로 닫힘.
- 설명(원본 문구를 새 모델로): 「원천 스키마의 테이블을 외부 테이블로 들여옵니다(<커넥터>). 행은 복사하지 않습니다 — Object type의 백킹으로 연결한 뒤 질의할 때 읽습니다.」
- 항목·기본값·엔진 전환 규칙·필수 칸·힌트 문구는 원본 §5.5와 **같다**(이름 `sales` placeholder, Oracle 「서비스 이름」 `FREEPDB1 · ORCLPDB1 …`, MySQL 스키마 칸 없음 등).
- **추가 항목**: 「TLS」 선택(끔 / 켬 / 켬 + 인증서 검증 안 함 — 원본은 MySQL에서 검증 끔이 암묵 기본). 「읽기 전용 계정 권장」 안내 문구.
- 비밀번호 칸: 입력값은 저장 요청 때 코어로 한 번 전달되고 바로 키체인에 들어간다. 다시 열면 빈 칸 + 「저장됨(••••)」 표시.
- 「실행될 문장」 미리보기(§5.6). 「연결 시험」(실제 접속만 해 보고 등록하지 않음; 결과 「접속됨 · 테이블 N개 보임」 또는 번역된 오류). 「취소」, 「연결」.
- 성공: 닫기 → 개요 다시 읽기 → 새 데이터소스 선택(원본 동작).
- **수정 모드**(N2): 같은 대화상자, 제목 「연결 정보 수정」, 이름·엔진 비활성, 비밀번호는 비워 두면 기존 값 유지. 표시 문장 `ALTER DATASOURCE <ds> SET PARAMETERS = {…}` [제안 — 엔진 문법 D-02 확인 필요].

### 5.5 백킹 진입: 「Object type으로 만들기」 / 「기존 Object type에 매핑」
F3는 **초안을 계산해 F1 편집기에 넘기는 것까지** 책임진다. 저장·검증·발행은 F1(작업본 → 제안 → 발행, 02 §14).

**A. Object type으로 만들기** (S6)
1. 코어가 테이블 컬럼으로 Object type 초안을 계산한다(`POST …/scaffold`, §6). 규칙:
   - `apiName`: 테이블 이름을 영숫자 외 문자로 쪼개 각 조각 첫 글자를 대문자로 이어 붙임, 숫자로 시작하면 앞에 `T`(원본 노드 이름 규칙과 같음 — `po_line` → `PoLine`). 같은 온톨로지에 이미 있으면 뒤에 `2`, `3`.
   - `displayName`: 원천 테이블 주석(comment)이 있으면 그것, 없으면 apiName을 띄어 쓴 것. `pluralDisplayName`은 비워 둠.
   - 기본 키: 원천 PK → 원본 KEY 추정 규칙(NOT NULL이면서 이름이 `id` 또는 `_id`·`_no`·`_code`·`_key`로 끝남 → 첫 NOT NULL → 첫 컬럼). 원천 PK가 복합이면 복합 기본 키(02 §5, 원본은 1개만).
   - 속성: 컬럼마다 `apiName` = snake_case → camelCase(`po_line_id` → `poLineId`), `baseType` = 컬럼 타입 매핑표(§7.2), `required` = NOT NULL, `pii` = PII 추정. 매핑은 `expr: "<컬럼>"`.
   - `titleKey`: 이름이 `name`/`title`/`subject`인 문자열 컬럼 → 없으면 기본 키.
   - `storage`: `live`(02 §7.3 조건 충족 시). `backing: [{role: primary, kind: table, ref:{datasource, table}, key, mappings}]`.
2. F1 Object type 편집기가 **속성 매핑 탭이 열린 채** 뜬다(같은 창의 F1 탭으로 이동, `view=build&ontology=<rid>&edit=objectType:new&from=ds:<ds>.<table>`). 사용자는 원본의 「속성 체크·이름 바꾸기」에 해당하는 작업(속성 빼기, apiName·표시 이름 바꾸기, 타입 바꾸기, 변환식)을 여기서 한다. 기본 키 속성은 뺄 수 없다(원본 「KEY 컬럼 체크는 끌 수 없음」 계승).
3. 「작업본에 저장」 → F3로 돌아오면 테이블에 「초안」 칩. 발행 전에는 F4·Object API에서 보이지 않는다.

**B. 기존 Object type에 매핑** (N1)
1. 대화상자: 대상 Object type 선택(이 온톨로지의 것, 검색 가능) → 역할 자동 제안: 대상에 주 원천이 없으면 「주 원천」, 있으면 「보강」.
2. 코어가 매칭·매핑을 제안한다(`POST …/suggest-backing`):
   - 보강 원천의 **매칭 식**: 대상 기본 키 값 샘플과 이 테이블 컬럼 값 샘플을 비교해 후보를 점수화(원본 `reverse_bind_preview`의 점수 규칙 계승 — F1 명세). 단순 일치가 없으면 흔한 변환(`trim`, `upper`, 접두어 제거 `replace(x,'PO-','')`, 앞 0 채우기)을 시도해 일치율이 가장 높은 식을 제안. 각 후보에 일치율(예: `7/8 행 일치`) 표시.
   - **자동 매핑(Automap)** [조사: Palantir 속성 편집기]: 컬럼 이름 ↔ 속성 apiName/displayName/aliases 유사도로 기존 속성에 연결, 연결 안 된 컬럼은 「새 속성으로 추가」 후보.
3. F1 편집기의 해당 Object type 「백킹」 탭이 새 원천이 추가된 상태로 열린다. 같은 속성을 두 원천이 주면 `priority` 입력 필요(02 §7.6) — 편집기가 경고.
4. live Object type에 다른 데이터소스의 보강 원천을 추가하면 [결정 대기 D-05] 권장안에 따라 「live는 같은 데이터소스만 보강할 수 있습니다. 저장 방식을 indexed로 바꾸시겠습니까?」 확인.

**C. 테이블 간 관계** (S8 대체)
- 테이블 상세의 컬럼 행 메뉴 「이 컬럼으로 Link type 만들기」: 컬럼 값이 다른 Object type 기본 키와 맞는지 샘플로 확인해 후보(대상 타입, 변환식, 카디널리티 추정)를 보이고 → F1 Link type 편집기(join `foreign-key`)로 넘긴다.
- 원본 「관계 만들기」 폼의 속성 자동 선택 규칙(상대 KEY와 같은 이름 우선 → 공통 이름 → 첫 속성)은 후보 정렬 규칙으로 계승.

### 5.6 「실행될 문장」 미리보기 (원본 유지)
- 폼 변경 → 180ms 디바운스 → 해당 쓰기 API에 `dry: true` → 응답 `statement` 강조 표시. 늦게 온 이전 응답은 버림. 미완성이면 「…」. 입력 검증 오류는 그 자리에 문구.
- 강조 키워드 목록은 원본과 같고 `ALTER`, `SET`, `PREVIEW`를 추가. HTML 이스케이프 필수. 비밀번호는 항상 `'••••'`.

### 5.7 「실행한 문장」 (원본 수정 — D-12)
- 막대 표시 조건: 기록이 1건 이상(원본과 같음). 이제 탭을 열자마자 읽기 문장(`SHOW DATASOURCES` 등)이 기록되므로 사실상 항상 보인다.
- 접힌 막대: 「실행한 문장」 + 건수 + 마지막 **쓰기** 항목 `✓ <결과>` / `✕ <오류>`(마지막 읽기는 막대 요약에 쓰지 않음 — 쓰기 결과가 묻히지 않게).
- 펼친 목록: 최신순 최근 30건(원본 상한 유지), 각 줄 = 종류 태그(`읽기`/`쓰기`) + 문장(강조) + 결과(행 수 또는 결과 문구)/오류 + 시각 + 행위자(`사람`/`에이전트`/`시스템`). 필터 「읽기 문장 숨기기」(기본 꺼짐), 「전체 기록 보기」(페이지 넘김, 최대 보관 1,000건 또는 30일).
- 기록되는 문장: 연결 관리 쓰기(`CREATE/ALTER/REFRESH/DROP DATASOURCE`), 고급 화면의 가상 타입 DDL, 카탈로그 읽기(`SHOW DATASOURCES`, `SHOW TABLES FROM`, `SHOW COLUMNS FROM`), 미리보기(`PREVIEW …`), 발행 컴파일이 실행한 패브릭 문장(행위자 `시스템`, 「발행 v3」 태그).
- 저장 위치: 코어 `workbench.runtime`(데이터소스 문장 기록). 쓰기 문장은 감사(`workbench.audit`)에도 남는다.
- 성공 결과 문구: 엔진 `result` 문구, 없으면 「완료」(원본). 읽기는 `<n>행`.

### 5.8 쓰기 후 갱신 (원본 유지 + 확장)
- 성공한 쓰기 뒤 개요·테이블 목록·선택 테이블을 다시 읽는다(원본). 연결 해제 성공 시 선택을 비우고 첫 진입 절차.
- 쓰기 진행 중 모든 쓰기 버튼 비활성(원본).
- **원본과 다름**: 다른 곳(F1 작업본 저장, 발행, F4 콘솔)에서 바뀐 내용은 코어가 SSE `GET /api/v1/events?topics=datasource,ontology`로 알려 자동 갱신(원본은 자동 반영 없음).

### 5.9 백킹 지도 뷰 (S7 대체)
- 머리: `Backing map`, 온톨로지 표시 이름 + 「발행 v<N>」 또는 「초안 포함」 토글.
- 지도: 열 = 데이터소스(이름순, 원본과 같은 배치 규칙), 상자 = 백킹으로 쓰이는 테이블, 오른쪽 열 = Object type 카드. 테이블 → Object type 선(주 원천 실선, 보강 점선, 매칭 식이 있으면 `ƒ` 표시). Object type 사이 Link type 곡선 + 방향 이름. 원천이 `system`/`document`/`manual`인 Object type은 「데이터소스 밖」 열에.
- 상자 클릭 → 테이블 상세(원본 노드 클릭 동작 계승), Object type 카드 클릭 → F1 편집기.
- 아래 표: `Object type | 저장 방식 | 주 원천 | 보강 원천 수 | 마지막 동기화(indexed) | 상태`.

### 5.10 패브릭 뷰 (고급, 원본 가상 그래프 뷰)
- 그래프 선택: 발행 관리 그래프(잠금)와 관리되지 않는 그래프(`sample` 등).
- **발행 관리 그래프**: 원본 「노드 타입」·「관계」 표와 같은 열 + 「출처」 열(Object type/Link type, 발행 버전). 삭제 버튼 없음, 「관계 만들기」 카드 없음. 상단 안내 「이 그래프는 온톨로지 발행이 관리합니다. 바꾸려면 Object type을 고치고 발행하세요.」
- **관리되지 않는 그래프**: 원본 §5.3–§5.4의 「가상 노드로 노출」·지도·표·「관계 만들기」·삭제를 **원본 그대로**(문구·기본값·자동 선택 규칙 포함). 각 가상 노드 행에 「Object type으로 가져오기」(N4).

## 6. API
모두 코어 `/api/v1`, JSON, 세션 토큰 필수(03 §3). 오류 본문 `{error, code, statement?, detail?}`.

### 6.1 연결 관리
| 메서드 | 경로 | 요청 | 응답 |
|---|---|---|---|
| GET | `/datasources` | — | `{datasources: Datasource[]}` |
| GET | `/datasources/engines` | — | `{engines: [{id, label, available, connector, reason?}]}` (원본 `{engines: string[]}`를 확장) |
| POST | `/datasources` | `{name, engine, host, port?, database?, service?, schema?, user, password?, tls?, dry?}` | `{statement, result, datasource}` / dry: `{statement}` |
| POST | `/datasources/test` | 위와 같음(`name` 선택) 또는 `{name}`(저장된 연결 시험) | `{ok, tables?, error?, translated?}` |
| PATCH | `/datasources/{ds}` | `{host?, port?, database?, service?, schema?, user?, password?, tls?, dry?}` | `{statement, result}` |
| POST | `/datasources/{ds}/refresh` | `{dry?}` | `{statement, result, changes: {addedTables[], removedTables[], changedTables: [{table, addedColumns[], removedColumns[], typeChanged[]}]}, affected: [{objectType, ontology, property?, problem}]}` |
| DELETE | `/datasources/{ds}` | `{dry?}` | `{statement, result}`; 의존 있으면 409 |
| GET | `/datasources/{ds}/usage` | — | `{objectTypes: [{ontology, rid, apiName, displayName, role, storage, state: draft|published}], linkTypes: [...]}` |

- 원본 필드(`name, engine, host, port, database, service, schema, user, password, dry`)와 엔진 별칭(postgresql→postgres, mariadb→mysql, mssql→sqlserver), 엔진별 필수 값, 키 순서, 기본 포트는 **같다**.
- `password`는 요청에만 존재하고 어떤 응답·로그에도 없다.

### 6.2 카탈로그·미리보기
| 메서드 | 경로 | 응답 |
|---|---|---|
| GET | `/datasources/{ds}/tables` | `{tables: Table[]}` |
| GET | `/datasources/{ds}/tables/{t}/columns` | `{columns: Column[]}` |
| GET | `/datasources/{ds}/tables/{t}/preview?limit=20` | `{statement, columns: string[], rows: any[][], rowCount, truncated, elapsedMs, path}` (limit 1–200, 기본 20 — 원본과 같음) |
| GET | `/datasources/{ds}/tables/{t}/profile` | `{columns: [{name, nullRatio, distinct, sample: [..5], minMax?}]}` — 매칭 제안·타입 추정용, 최대 1,000행 표본 [제안] |

### 6.3 미리보기의 질의 규칙
- 사용자 입력 SQL은 받지 않는다(원본 501 원칙 유지). 코어가 식별자 검증(`^[A-Za-z_][A-Za-z0-9_]*$` — 원본 규칙) 후 `SELECT * FROM <ds>.<t> LIMIT <n>`에 해당하는 질의를 Graph Port/FDW 경유로 실행. 표시 문장 `PREVIEW <ds>.<t> LIMIT <n>`.
- 실행 역할: `fabric_ro` 계열(03 §6) — 읽기 전용 트랜잭션, `statement_timeout` 15초.

### 6.4 백킹 진입 (F1 작업본과의 경계)
| 메서드 | 경로 | 요청 | 응답 |
|---|---|---|---|
| POST | `/ontologies/{ont}/draft/scaffold/object-type` | `{datasource, table}` | `{objectType: ObjectType(초안, 저장 안 됨), notes: [..]}` |
| POST | `/ontologies/{ont}/draft/scaffold/backing` | `{objectType, datasource, table, role?}` | `{backing: BackingSource(초안), matchCandidates: [{expr, property, matched, sampled}], automap: [{column, property|null, score}]}` |
| POST | `/ontologies/{ont}/draft/scaffold/link-type` | `{datasource, table, column}` | `{candidates: [{to, fromExpr, toProperty, matched, cardinality}]}` |
| POST | `/ontologies/{ont}/draft/import-virtual` | `{graph, nodes: [label], relationships: [name]}` | `{created: {objectTypes, linkTypes}, warnings}` — N4, 작업본에 저장 |
- scaffold는 **저장하지 않는다**. 저장은 F1의 `PUT /ontologies/{ont}/draft/object-types/{apiName}` 등(F1 명세).

### 6.5 패브릭(고급)·기록
| 메서드 | 경로 | 비고 |
|---|---|---|
| GET | `/fabric/graphs` | `{graphs: [{name, managed, ontology?, version?, virtualNodes, virtualRelationships}]}` |
| GET | `/fabric/graphs/{g}/virtual-nodes`, `/virtual-relationships` | 원본 VirtualNode/VirtualRel 형태 + `origin: {ontology, kind, apiName, version}|null` |
| POST/DELETE | `/fabric/graphs/{g}/virtual-nodes[/{label}]`, `/virtual-relationships[/{name}]` | 원본 요청 본문과 같음(`label, source, key, properties, dry` / `name, from, to, dry`). 관리 그래프면 403 |
| GET | `/datasources/statements?kind=read|write&limit=30&before=` | `{items: [{id, at, kind, statement, ok, result|error, actor: {kind, id}, origin?}]}` |

## 7. 데이터

### 7.1 엔터티
- **Datasource** `{name, engine, displayName(=name), host, port, database|service, schema, user, tls, builtin: bool, tableCount, status: connected|error, lastRefreshAt, secretRef}` — 원본 필드 `{name, engine, display_name, database, host, table_count}`는 응답에서 같은 이름으로도 제공(비교 테스트용 별칭).
- **Table** `{name, schema(=ds), columnCount, comment, usage: [{objectType, role, state}]}` (원본 `virtual_node`는 `usage`로 대체; 고급 API에서는 원본 필드 유지)
- **Column** `{name, type, nullable, sourceKey: bool, mappedTo: [{objectType, property}], piiGuess: bool}` (원본 `primary_key` = 가상 노드 KEY 여부 → `sourceKey`(원천 PK)로 뜻을 바로잡음 — 의도된 차이)
- **StatementLog** `{id, at, datasource?, kind: read|write, statement, ok, result, error, actor, origin}`
- 데이터소스 정의는 그래프 엔진 카탈로그(D-02 A) + 코어 `workbench.meta`의 데이터소스 레코드(표시 정보·`secret_ref`·`builtin`) 두 곳에 있다. 원천(진실)은 코어 레코드, 엔진 카탈로그는 코어가 맞춘다(부팅 시 대조).
- **BackingSource**는 02 §7.1 그대로. F3가 만드는 것은 `kind: table` 초안뿐.

### 7.2 컬럼 타입 → baseType 매핑 (scaffold 기본값)
| 원천 타입 | baseType |
|---|---|
| smallint, integer, int, tinyint(≠1) | integer |
| bigint | long |
| real, double, float | double |
| numeric/decimal(p,s), money | decimal (s=0이고 p≤18이면 long) |
| boolean, bit, tinyint(1) | boolean |
| date | date |
| timestamp, datetime, timestamptz | timestamp |
| char, varchar, text, nvarchar, clob | string |
| json/jsonb | string(+ 「struct로 바꾸기」 제안) |
| uuid | string |
| bytea, blob | (매핑 안 함 — 체크 해제 상태로 제안) |
| 배열 타입 | 요소 타입 + `array: true` |
- 엔진이 컬럼 타입을 주지 못하면 원본처럼 미리보기 1행으로 추정(정수/소수/불리언/`YYYY-MM-DD` 날짜/텍스트).

### 7.3 비밀번호 보관 [결정 대기 D-09]
- 키체인 항목 이름: `<제품>/<데이터 폴더 id>/datasource/<name>`. `workbench.secret_ref`에 `{name, kind: datasource-password, lastUsedAt}`.
- 권장안(접속 시점 생성): 코어가 원천 접속이 필요한 시점(카탈로그 읽기·미리보기·live 질의·동기화)에 엔진 사용자 매핑을 키체인 값으로 만들고, 코어 종료 시(및 비정상 종료 뒤 다음 부팅 첫 단계에서) 모든 사용자 매핑의 비밀번호 옵션을 지운다. 사용자 매핑은 `PUBLIC`이 아니라 `fabric_ro` 계열 역할에만.
- 대안(엔진이 위를 지원하지 못할 때): 엔진 저장 + PG 데이터 디렉터리 암호화 불가 → 최소 노출 문서화(사용자 매핑은 슈퍼유저만 읽음, 백업·덤프에서 사용자 매핑 옵션 제외).

### 7.4 내장 PG 데이터소스 (C10)
- host가 `127.0.0.1`/`localhost`이고 port가 현재 내장 PG 포트이며 database가 내장 DB면 `builtin: true`. 저장 시 port 대신 `@builtin` 표식.
- 부팅 때 내장 PG 포트가 바뀌었으면 `builtin` 데이터소스 전부를 새 포트로 다시 가리킨다(원본은 예제 3개만).

### 7.5 예제 시드
- 데이터소스 `erp`·`wms`·`crm`(내장, 읽기 전용 계정) — 원본과 같음.
- 예제 **온톨로지** 「공급망 운영 (예제)」의 Object type 6개(02 §7.2 표)가 이 테이블들을 백킹으로 쓴다(F1 명세).
- 원본 `sample` 그래프의 가상 노드 7·관계 5는 **비교 테스트용으로 그대로 시드**한다(관리되지 않는 그래프). 튜토리얼 06·07·08장의 Cypher 실측값 재현이 이 그래프에 의존한다(F4).

## 8. 에이전트 연동
| 모드 | 이 기능 관련 도구 | 비고 |
|---|---|---|
| `brief` | `catalog_list`, `catalog_describe`(테이블·컬럼), `table_preview`(최대 30행) | 읽기만 |
| `build` | 위 + `table_profile`, `draft_scaffold_object_type`, `draft_scaffold_backing`, `draft_upsert_backing`, `backing_preview(objectType)`, `reverse_bind_preview` | 결과는 **작업본**에만. 데이터소스 생성·수정·해제 도구는 **없음**(자격 증명은 사람만 다룸) [제안] |
| `answer`/`act` | 없음 | 질의는 Object set·Function으로(02 §12). 원천 테이블 직접 조회 도구 없음 |
| 외부 MCP `data` 범위 | live Object type 값 조회만(04 §8) | 테이블 단위 조회 도구는 없음 |
- 도구 결과의 행 상한(원본 30행)과 `truncated` 표시 유지(04 §5). PII 추정 컬럼 값은 에이전트 도구 결과에서 마스킹(`•••`), 이름·타입만 노출.
- 에이전트가 만든 작업본 변경은 감사에 `actor.kind = agent`, 화면 칩에 「AI 초안」.

## 9. 보안·권한
- 모든 API 세션 토큰 필수(03 §3). 원본 브리지의 무인증 접근 제거.
- 비밀번호: 요청 본문 → 코어 → 키체인. 응답·로그·문장 기록·감사·오류 메시지에 평문 없음(오류 원문에 비밀번호가 섞일 수 있는 엔진 메시지는 마스킹 필터 통과).
- 원천 읽기 역할: 데이터소스별 사용자 매핑은 `fabric_ro` 계열 역할에만(원본은 `FOR PUBLIC` 추정). 코어 `wb_core`는 원천 외부 테이블에 직접 권한 없음.
- 원천 쓰기 금지: 외부 테이블 쓰기 거절 트리거 유지(원본). 원천 변경은 Action의 시스템 호출로만(F7).
- 권장: 연결 대화상자에서 「읽기 전용 계정 권장」. 연결 시험 때 계정에 쓰기 권한이 보이면(가능한 엔진에서) 경고 「이 계정은 원천에 쓸 수 있습니다. 읽기 전용 계정을 권장합니다.」 [제안]
- 미리보기 크기 상한 200행, 응답 1MB, 시간 15초.
- 관리 그래프 DDL 거부(§3.1) — 발행 결과와 사용자의 수동 변경이 섞이지 않게.

## 10. 오류·예외
원본 번역표(분석 design §9의 1–14)는 **문구 그대로 유지**한다. 추가·변경:

| # | 상황 | 표시 | 원본 대비 |
|---|---|---|---|
| E-1 | 이름 규칙 위반 | 「데이터소스 이름은 영문 소문자·숫자·밑줄만 쓸 수 있고 숫자로 시작할 수 없습니다: "…"」 (400) | 같음 |
| E-2 | 예약 이름(시스템 스키마, `workbench`, `meta`, `runtime`, `audit`, `secret_ref`, `sample`) | 번역표 3번 문구 | 예약어 확장 |
| E-3 | 엔진 거절 | 422 + `statement`, 번역 배너 | 같음 |
| E-4 | Object type이 사용 중이라 해제 불가 | 409 「Object type <표시 이름 목록> 이(가) 이 데이터소스를 백킹으로 쓰고 있어 해제할 수 없습니다. 온톨로지 구축에서 백킹을 먼저 바꾸세요.」 + 「사용처 보기」 | 새 문구(원본 1번 대체) |
| E-5 | 관리되지 않는 그래프의 가상 노드가 사용 중 | 원본 번역표 1번 문구 그대로 | 같음 |
| E-6 | 구조 다시 읽기에서 매핑 컬럼 삭제 감지 | 경고 배너 「원천에서 사라진 컬럼을 쓰는 매핑이 있습니다: 발주.status ← erp.purchase_order.status」 + 「온톨로지 구축에서 보기」 | 신규 |
| E-7 | 키체인 접근 거부/잠김 | 「OS 키체인에서 비밀번호를 읽지 못했습니다. 키체인 접근을 허용한 뒤 다시 시도하세요.」 | 신규 |
| E-8 | 키체인에 비밀번호 없음(다른 기기에서 데이터 폴더 복사 등) | 데이터소스 「연결 안 됨」 + 「비밀번호 다시 입력」 | 신규 |
| E-9 | 연결 시험 실패 | 원본 번역표 5–11번 문구 | 같음 |
| E-10 | 미리보기 시간 초과 | 「원천이 15초 안에 답하지 않았습니다.」 | 신규 |
| E-11 | 관리 그래프에 가상 타입 DDL | 403 「이 그래프는 온톨로지 발행이 관리합니다. Object type을 고치고 발행하세요.」 | 신규 |
| E-12 | 정의 안 된 쓰기 경로 | 원본 501 문구 「이 패키지에서는 원천 DB에 임의 SQL을 보내지 않습니다. …」에서 뒷부분을 「…Object type으로 연결해 조회하세요.」로 | 문구 일부 변경 |
| E-13 | scaffold 대상 온톨로지 없음 | 「먼저 온톨로지를 만드세요.」 + 「새 온톨로지」 | 신규 |

## 11. 원본과 비교할 테스트
**같아야 함**
1. 탭 진입 요청 순서(개요 → 테이블 → 컬럼 → 미리보기), `ds` 쿼리로 선택.
2. 예제 상태: 데이터소스 3(`crm`·`erp`·`wms` 이름순, engine `postgres`, host `127.0.0.1`), 테이블 수 6/3/4.
3. `SHOW TABLES FROM erp` 상당 결과 6행과 컬럼 수(원본 S4 표).
4. 미리보기 값: `wms.shipment` 최대 지연 `SHP-03`(9, `CUSTOMS_HOLD`), `crm.claim` 3행. 원천 행 변경 후 즉시 반영.
5. dry 문장: 연결(엔진 4종 키 순서·기본값·비밀번호 마스킹), 해제·새로 고침.
6. 입력 검증 메시지·400, 엔진 거절 422 + `statement`, 번역표 14개 문구.
7. 연결 대화상자 항목·기본값·엔진 전환·필수 칸·비활성 엔진 표시.
8. 이름 생성 규칙: `po_line` → `PoLine`, 키 추정 `po_line_id`(이제 Object type scaffold 결과로 확인).
9. 관리되지 않는 그래프(`sample`)의 가상 노드·관계 화면: 원본 S6·S8·S9 전체(문장, 자동 선택 `po_id`/`po_id`, 거절 문구 2종).
10. 홈 최근 항목 행 클릭 → `ds` 선택 상태로 열림.
11. 테이블 찾기 필터가 서버 요청 없이 동작.

**의도된 차이 (D-12)**
1. 「실행한 문장」에 읽기 문장 기록, 앱 재시작 후 유지(원본: 쓰기만·메모리). 근거: 튜토리얼 설명, REVIEW #6.
2. 가상 노드 없는 테이블도 미리보기 가능, 바닥 경로 문구 변경.
3. 해제 거절 기준이 Object type 사용 여부(E-4).
4. 원천 비밀번호가 엔진 카탈로그·DB 덤프에 평문으로 없음(N5) — REVIEW #5.
5. 「구조 다시 읽기」가 컬럼 변경 반영.
6. 내장 PG 포트 변경 시 사용자 데이터소스도 재지정(C10) — REVIEW #4.
7. 무인증 브리지 제거: 토큰 없는 요청 401.
8. 홈 행 설명 `노드 N` → `Object type N`.
9. 연결 정보 수정·연결 시험 존재.

## 12. 열린 질문
1. D-02 B안(엔진 교체)일 때 패브릭 문장 문법을 "표시 계약"으로만 유지하는 것으로 충분한가, 아니면 F4 콘솔에서 실행 가능한 문법으로 코어가 직접 해석해야 하나.
2. `ALTER DATASOURCE` 문법이 원본 엔진에 있는지 [확인 필요]. 없으면 수정 = 내부적으로 DROP+CREATE(외래 테이블 재생성, 가상 타입 재컴파일) — 발행 중인 live Object type이 잠시 끊긴다.
3. 「구조 다시 읽기」의 컬럼 변경 반영 = 외래 테이블 재가져오기. 이 동안 live 질의가 실패할 수 있다. 짧은 잠금으로 충분한지.
4. 문장 기록 보관 기간(1,000건/30일)과, 읽기 문장 기록이 너무 많을 때(탭 열 때마다 4건) 묶어 표시할지.
5. 비-테이블 원천(`sql`, `system`, `document`)의 진입점: `sql`은 이 화면의 「SQL로 백킹 만들기」(단일 SELECT 검증)로 둘지, F1에만 둘지. 이 명세는 F1에만 둔다고 가정.
6. PII 추정 규칙(컬럼 이름 목록)을 설정(F8)에서 고칠 수 있게 할지.
7. Windows에서 PostgreSQL 외 커넥터 제공 여부와 Oracle 클라이언트 재배포 조건(D-02와 함께).
