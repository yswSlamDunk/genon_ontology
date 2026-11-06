# ADR-0018 통합 설계 문서(SoT)와 Palantir식 온톨로지 모델
- 상태: 승인 (2026-11-01, 사용자 요청) — 세부 구조는 Claude 결정, 사용자 사후 보정 예정(ADR-0015)

## 맥락
- 사용자 요청: 분석이 끝나면 **설계 문서(Source of Truth)**를 작성. 작성 전 프로젝트 아키텍처를 고려.
- 사용자 요구: 원본의 "테이블 = 노드, 행 = 인스턴스"(가상 노드) 모델에서 한 단계 나아가 **Palantir처럼 노드(Object type)를 설정**하도록.
- 근거 자료: 사용자 조사 `~/Desktop/workplace/ontology/02_research/palantir/palantir-report.md`(주), `…/enhans/enhans-ontology-layer-draft.md`(비교 참고).
- 사용자가 나중에 보고 보정한다.

## 결정
1. **위치:** `~/Desktop/workplace/rea/spec/` — 분석 폴더와 분리. 이것이 새 제품의 SoT이며, 구현 세션(ADR-0011)은 `spec/`과 분석 폴더의 `design.md`(클린룸 문서)만 본다. `code-trace.md`·`notes.md`·원본 코드는 보지 않는다.
2. **구조:** 핵심 문서(비전·범위 / 아키텍처 / 온톨로지 모델 / 보안 / 에이전트 통합 / 결정 대기 목록)는 Claude가 직접 쓰고, 기능별 명세는 원본 기준 동작(분석 `design.md`)을 출발점으로 **새 온톨로지 모델과 개선 사항을 반영한 차이(delta)** 형태로 쓴다.
3. **온톨로지 모델 방향:** 원본의 클래스/가상 노드 모델을 Palantir 개념(Object type, Property, Link type, Interface, Shared property/Value type, Action type, Function, Object set, Object view, 변경 제안·이력)으로 재구성한다. Object type은 **저장 방식과 분리된 의미 타입**이며, 하나 이상의 원천(테이블·뷰·가상 노드·시스템 API·문서 추출)을 백킹 데이터로 가진다.
4. **표기:** 문서마다 [원본] 원본 0.1.1 동작, [조사] 사용자 Palantir 조사, [제안] Claude 설계 제안을 구분한다. 사용자 결정이 필요한 곳은 `spec/90-open-decisions.md`에 모은다(REVIEW.md 항목과 연결).
5. 원본 동작 기록(4단계)이 보류 중이므로(ADR-0017), 실행 기록에 의존하는 세부는 "확인 필요"로 둔다.
