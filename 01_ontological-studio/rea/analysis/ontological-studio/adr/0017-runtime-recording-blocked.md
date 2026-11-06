# ADR-0017 원본 동작 기록(4단계)을 사용자 결정 전까지 보류
- 상태: 승인(Claude) (2026-10-31) — 사용자 결정 대기 항목을 REVIEW.md에 등록

## 맥락
- ADR-0004에 따라 분석용 데이터 폴더(`runtime-data/userdata`)로 앱을 따로 띄우려 했다:
  `ONTOLOGICAL_STUDIO_USER_DATA=<폴더> "/Applications/Ontological Studio.app/Contents/MacOS/Ontological Studio"`
- Claude Code 명령 샌드박스 안에서는 앱이 **출력 없이 즉시 exit 0**으로 끝나고 데이터 폴더에 아무것도 만들지 않는다.
  코드상 단일 인스턴스 잠금 실패 시 조용히 종료하는 경로와 일치 → 샌드박스가 잠금 소켓 생성을 막는 것으로 **추정**.
- 샌드박스를 끄고 실행하는 것은 자동 모드 분류기가 거부했다(Safety Bypass Flag).
- REA `capture_electron_scenario`로 띄우는 방법도 있으나: 환경 변수를 넘길 수 없어 `--user-data-dir` 인수에 의존해야 하고(동작 미확인), 결과적으로 거부된 "샌드박스 밖 실행"을 우회하는 것이 될 수 있어 시도하지 않았다.

## 결정
- 사용자가 방법을 정할 때까지 4단계(원본 동작 기록)를 보류한다. 1·2·3·5단계(정적 분석·설계 초안)는 계속한다.
- 각 `design.md`의 "모르는 점"은 그대로 두고, 4단계 후 갱신한다.

## 사용자 선택지 (REVIEW.md)
1. 사용자가 터미널에서 위 명령으로 분석용 인스턴스를 직접 띄워 둔다 → Claude는 떠 있는 인스턴스에 REA 브라우저 캡처로 접속해 기록(가장 간단).
2. Claude Code 권한 설정에 이 앱 실행 명령만 샌드박스 밖 실행을 허용하는 규칙 추가.
3. REA `capture_electron_scenario`로 실행(`--user-data-dir` 동작 확인 필요).
