# ADR-0012 분석 기준 버전을 0.1.1로 고정
- 상태: 승인 (2026-10-31, 사용자)
## 맥락
앱에 자동 업데이트 코드는 없다(asar에 electron-updater·autoUpdater 없음, `app-update.yml`만 존재). 사용자가 새 버전을 설치하면 기준이 바뀐다.
## 결정
- 분석 기준: Ontological Studio **0.1.1**. 설치 DMG를 `artifacts/Ontological-Studio-0.1.1-mac-arm64.dmg`로 보관
  (SHA-256 `d49694ba6d699589a086ab7f3499dd7d151ba7cd5e64137d86dba6409f01dae0`).
- 분석이 끝날 때까지 설치된 앱을 업데이트하지 않는다. 새 버전은 분석 완료 후 차이만 따로 확인한다.
## 비고
설치된 앱과 DMG 내부 앱의 동일성은 A1에서 확인한다.
