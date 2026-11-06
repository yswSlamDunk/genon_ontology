# ADR-0008 분석 기준은 배포본, 소스 저장소는 보조 참고
- 상태: 승인 (2026-10-31, 사용자)

## 맥락 (2026-10-31 확인)
- 로컬 저장소 `ontology/01_ontology-studio/repo`는 `main@20afcde`(원격 main과 동일)이며 로컬 수정 파일이 있다.
- 배포본 0.1.1의 메뉴에는 `act`(질의·액션)·`systems`(시스템 등록)가 있지만 main에는 없다.
  공개 브랜치 `feat/kinetic-action-layer@4d6844d`(2026-10-22)에는 있다.
- 배포본 Electron 셸(`ontology-studio-lite`: nl2cypher, codeapps, fabric-bridge, kinetic …)은 공개 브랜치 어디에도 없다.
- 사용자가 배포본과 저장소를 모두 실행해 본 결과, 저장소 버전은 문제가 많고 완성도가 낮았다.

## 결정
- **분석 기준은 배포본** `/Applications/Ontological Studio.app` 0.1.1 이다. 동작·구조·인터페이스 모두 배포본에서 확인한 것을 사실로 삼는다.
- 배포본 안의 읽을 수 있는 코드를 1차 자료로 쓴다:
  - Electron 셸: `extracted-app-asar/src` (난독화 안 됨)
  - Python 백엔드·kinetic·예제 서비스: `Contents/Resources/runtime/...` 의 `.py` (그대로 들어 있음)
  - 프런트엔드: `runtime/frontend/assets/index-*.js` (압축 번들, 소스맵 없음) → REA로 분석
- 소스 저장소(main, kinetic-action-layer 브랜치)는 **보조 참고**로만 쓴다(압축된 프런트엔드를 해석할 때 힌트 등). 저장소 내용을 근거로 사실을 단정하지 않으며, 배포본과 다르면 배포본을 따른다. 사용자 로컬 repo는 수정하지 않는다.

## 결과
- ADR-0006의 2단계 "소스 흐름 추적"은 **배포본 코드** 대상으로 수행한다. 3단계 "배포본 대조"는 저장소와 대조가 아니라, 필요할 때 저장소를 힌트로 참고하는 단계로 축소한다.
- 압축된 프런트엔드 분석에서 REA 비중이 커진다 (`analyze_javascript_application`, `trace_application_feature`, 실행 기록).
