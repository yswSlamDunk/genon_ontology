# 설계 문서 (Source of Truth)

새 온톨로지 플랫폼(가칭 **Ontology Workbench**, 이름은 결정 대기)의 설계 원천 문서다. 구현은 이 폴더만 보고 한다.

- 상태: **초안 v0.1** (2026-11-01, Claude 작성) — 사용자 보정 전. 사용자 보정 후 v0.2.
- 구성: 핵심 문서 7개(Claude 직접) + 기능 명세 9개(에이전트 작성, 클린룸 입력만 사용, Claude 정합성 점검·핵심 문서 반영 완료).
- **처음 읽을 순서(권장):** 90 결정 대기 → 00 → 02 → 01 → 03 → 04 → features/F1 → 나머지 기능.
- 출발점: Ontological Studio 0.1.1 정적 분석 결과(`../analysis/ontological-studio/`)와 사용자의 Palantir 조사(`~/Desktop/workplace/ontology/02_research/palantir/palantir-report.md`).
- 관련 결정: `../analysis/ontological-studio/adr/` (특히 ADR-0002 클린룸, 0011 구현 분리, 0018 이 문서).

## 문서 구성

| 문서 | 내용 |
|---|---|
| [00-vision-scope.md](00-vision-scope.md) | 무엇을 왜 만드나, 원본과의 관계, 범위(MVP/이후) |
| [01-architecture.md](01-architecture.md) | 구성 요소, 프로세스, 저장소, 통신, 배포 |
| [02-ontology-model.md](02-ontology-model.md) | **핵심.** Palantir식 온톨로지 메타모델 (Object type · Link · Action · Function …) |
| [03-security.md](03-security.md) | 위협 모델, 인증·격리·승인·비밀 관리 |
| [04-agent-integration.md](04-agent-integration.md) | 에이전트(LLM) 연동, 모드·도구·권한, MCP |
| [features/](features/) | 메뉴별 기능 명세 (원본 기준 동작 + 새 모델 반영 차이) |
| [90-open-decisions.md](90-open-decisions.md) | 사용자 결정 대기 목록 (권장안 포함) |

## 읽는 법 — 표기

| 표기 | 뜻 |
|---|---|
| **[원본]** | Ontological Studio 0.1.1에서 관찰한 동작 (근거: 분석 폴더의 `design.md`) |
| **[조사]** | 사용자 Palantir 조사 보고서의 내용 |
| **[제안]** | 이 문서가 정하는 새 설계 (사용자 보정 대상) |
| **[결정 대기]** | `90-open-decisions.md`의 번호로 연결. 권장안으로 일단 진행 |
| **[확인 필요]** | 원본 실행 기록(보류 중, ADR-0017)으로 확정할 세부 |

## 설계 원칙
1. **의미가 먼저, 저장은 나중.** 사용자는 테이블이 아니라 업무 객체(Object type)를 설계한다. 테이블·API·문서는 객체의 "백킹 데이터"일 뿐이다. ([02](02-ontology-model.md))
2. **사람이 결정하고, AI는 제안한다.** 쓰기·승인·발행은 사람의 명시적 행위로만 확정된다. 에이전트 권한은 모드별 최소 권한. ([03](03-security.md), [04](04-agent-integration.md))
3. **로컬 우선.** 노트북 한 대에서 설치 하나로 전부 동작한다(원본의 장점 유지). 외부 연결은 원천 DB·업무 시스템·LLM뿐.
4. **원본과 비교 가능하게.** 원본 기능은 같은 시나리오로 비교할 수 있게 계약(화면 흐름, API 형태, 결과 구조)을 유지하되, 원본의 결함·보안 약점은 고친다(고친 곳은 표시).
5. **클린룸.** 이 폴더에는 원본 코드·내부 식별자를 넣지 않는다.
