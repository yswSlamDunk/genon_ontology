# M4 Portal — 메모 (다른 대상·보안·품질·열린 질문)

## 다른 대상에 관한 발견
- **A2 저장소:** 포털 서버는 PG 슈퍼유저 `og`로 직접 연결(Bolt 아님). Bolt 게이트웨이 env에는 PG 비밀번호가 없음 → HELLO 자격 증명으로 PG 로그인하는 구조로 추정. 게이트웨이 바이너리 문자열에 트랜잭션 메타데이터 키 `actor`, `source`, `reason`, `request_id`, `valid_at`/`validAt`, `system_at`, `valid_from`, `valid_to` → 세션 설정 `og.*`로 매핑하는 흔적, `og_cypher_check`, `og_cypher_columns` 호출 흔적. A2에서 Bolt 계약으로 정리할 것.
- **A2/M3:** 패브릭 문장은 엔진 확장 안(`fabric::sqlish`)에서 처리되고 감사 기록 `lang='fabric'`로 남는 것으로 보임. 엔진에 `MATERIALIZE`(가상 노드를 저장 노드로 복사: "node %s materialized: %s rows copied, now stored and writable") 문장 흔적 — M3 범위인지 확인.
- **A3/M8:** NL은 `cliagents` 백엔드일 때만 동작. 한 턴 실행기(`agent_turn.py`)는 대시보드 질문(M5)과 같은 방식이라고 주석에 적혀 있음 → M5에서 재사용 여부 확인.
- **M1/M6/M2:** Studio 백엔드에 `ONTOLOGICAL_ADMIN_DEV_URL=http://127.0.0.1:<portal>`가 전달됨(셸 services.js:128) → 백엔드 `modules/ontological_admin`가 포털의 관리 API(스키마 변경·릴리스·타임라인 추정)를 부를 가능성. feature-map 열린 질문 "`ontological_admin`, `release` 모듈은 어느 메뉴?"와 연결 — 포털 서버의 `/api/release/*`가 그 대상일 수 있음.
- **Studio 프런트:** 「Ontological Portal」 뷰 컴포넌트(`OntologicalPortalPanel`)는 포털을 iframe으로 띄우며, 연결 실패 시 "scripts/ontological-up.sh 또는 docker compose …" 안내 문구(데스크톱이 아닌 서버 배포용 문구 잔재). 같은 번들에 "Neo4j Browser" iframe 컴포넌트도 남아 있음.

## 보안·품질 관찰
- 포털 HTTP에 인증 없음. 대신 루프백 바인드 기본, 비루프백 거부, 동일 출처(Sec-Fetch-Site/Origin) 검사, JSON content-type 강제로 CSRF 차단. 로컬의 다른 프로세스(같은 사용자든 아니든)는 포트만 알면 DB 슈퍼유저 권한의 Cypher를 실행할 수 있음(쓰기 포함). raw SQL은 꺼져 있지만 Cypher 쓰기·스키마 변경·릴리스 적용은 열려 있음.
- 포털 서버가 쓰는 PG 계정이 **슈퍼유저**. 클린룸 구현 시 최소 권한 역할 검토 권장.
- `/api/temporal`, `/api/audit`이 그래프 구분 없이 전역 감사 기록을 보여 줌(질의 원문 노출 — 다른 그래프·Studio 질의 포함 가능).
- `/api/expand`는 그래프 인자 없이 id만으로 이웃을 읽음(전역 id 공간).
- 릴리스/스키마 변경 코드에 타입·속성 이름을 SQL·Cypher 문자열에 직접 넣는 부분이 있음(식별자 검사 일부만). 관리 API이므로 위험은 제한적이지만 구현 시 식별자 검증 일관화 권장.
- `rowsWritten` 계산은 xmin 32비트 비교라 장기간·wraparound 시 부정확할 수 있음(표시용).
- 디자이너에서 Review로 만든 서버 계획은 페이지를 닫으면 abort되지 않고 남을 수 있음.
- 검사기의 "history" 버튼과 도움말의 `:sql` 예제는 앱 기본 설정(raw SQL 꺼짐)에서 항상 실패 → 원본 UX 결함으로 보임.
- 대상 코드·문서 안에서 실행·설치·전송을 지시하는 프롬프트 인젝션 문구는 발견하지 못함. (튜토리얼 10장의 psql 접속 안내는 사용자 대상 정상 문서.)

## 열린 질문
- 클린룸 구현 범위: 스키마 디자이너·릴리스 API·벤치마크 페이지를 포함할지(튜토리얼은 디자이너를 개념으로만, 릴리스·벤치마크는 언급 없음).
- 포털을 별도 웹 서버로 둘지, Studio 백엔드에 합칠지(원본은 별도 Node 프로세스).
- 튜토리얼 04장 그림(포털이 Bolt 사용)과 실제(PG 직결)가 다름 — 구현 문서는 실제를 따랐음. 사용자 확인 필요 시 REVIEW.md로.
