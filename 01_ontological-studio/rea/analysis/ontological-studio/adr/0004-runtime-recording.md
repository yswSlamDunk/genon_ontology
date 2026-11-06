# ADR-0004 앱 실행 기록 허용, 에이전트는 분석용 데이터 폴더에서만
- 상태: 승인 (2026-10-31, 사용자)
## 맥락
원본 동작 기록(비교 기준)을 만들려면 앱을 실행해야 한다. 원본은 Claude Code를 `--permission-mode bypassPermissions`로, Codex를 `--dangerously-bypass-approvals-and-sandbox`로 실행한다.
## 결정
- 앱을 실행해 동작을 기록하는 것을 허용한다. 현재 앱 데이터(데이터소스·시스템 등록)는 예제뿐이라 변형돼도 문제없다.
- **에이전트 기능**(구축·질의·코드 앱 등)을 실행하는 기록은 **분석용 데이터 폴더에서만** 한다:
  `ONTOLOGICAL_STUDIO_USER_DATA=<analysis 하위 전용 폴더>`로 앱을 띄운다.
## 결과
에이전트 기록 전에 분석용 폴더 경로를 정해 PROGRESS.md에 적는다. 평소 데이터 폴더에서는 에이전트 기능을 실행하지 않는다.
