# Ontological Studio 분석 — 진행 기록

마지막 갱신: 2026-10-31

## 목표
REA로 Ontological Studio를 분석하고, 그 결과를 바탕으로 나만의 프로그램을 만든다.

> 의사결정은 `adr/` 폴더에서 관리한다 (목록: `adr/README.md`). 아래 요약과 ADR이 다르면 ADR이 우선.
> 분석 기준은 배포본 (ADR-0008)

## 결정 사항 (2026-10-31, 사용자 확정)
- 진행: 분석 → 설계 문서 → 구현 → 원본과 동작 비교. **지금은 분석 단계만.** 구현 범위는 나중에 결정.
- 구현은 클린룸: 설계 문서에는 동작·인터페이스만, 원본 본체 코드는 복사하지 않음 (본체 repo 라이선스 없음).
- 분석 대상 순서: 공통 기반 A1 셸·부팅·프로세스 / A2 저장소(PG+Bolt) / A3 에이전트·MCP → 사용자 메뉴 8개
  (온톨로지 구축, 질의·액션, 데이터소스, Ontological Portal, 온톨로지 앱, 품질 검수, 시스템 등록, 설정)
- 자료 신뢰도: 배포본 0.1.1(정답) > 소스 repo `~/Desktop/workplace/ontology/01_ontology-studio/repo` (커밋 20afcde)
  ≈ 튜토리얼 `.../01_ontology-studio/tutorials` > PPT 정리본(`ontology/03_ppt/new`, 참고용만)
- 앱 실행 기록 허용. 현재 앱 데이터는 예제뿐이라 변형 문제 없음.
- 에이전트(Claude Code bypassPermissions) 기능 관찰은 **분석용 데이터 폴더에서만**
  (`ONTOLOGICAL_STUDIO_USER_DATA=<분석용 폴더>`로 실행).

## 대상별 조사 절차 (6단계)
1. 사용자 시나리오 (튜토리얼) → `user-scenarios.md` (S1, S2 …)
2. 소스 흐름 추적 (grep/Read) → `code-trace.md` (파일:줄 + 커밋)
3. 배포본 대조 (diff, REA analyze_javascript_application / trace_application_feature) → `bundle-diff.md`, `evidence/`
4. 원본 동작 기록 (REA capture_browser_scenario 등, psql 전후 비교) → `baseline/S*/`
5. 설계 문서 → `design.md`
6. 사용자 검토
- REA 세션은 **닫기 전에 export_evidence_bundle**.

## 환경 (설치 완료)
- REA CLI 6.8.0 (`/opt/homebrew/bin/rea`), Claude Code MCP 등록 완료 (`~/.claude.json` → `rea`)
- 엔진: Ghidra 12.1.4 (`~/.local/share/rea/ghidra/ghidra_12.1.4_PUBLIC`, mac_arm_64 디컴파일러 직접 빌드),
  JDK 21 (`/opt/homebrew/opt/openjdk@21`), JADX JAR (`~/.local/share/rea/android/`), Frida
- `~/.zshrc`에 GHIDRA_INSTALL_DIR / JAVA_HOME / REA_JADX_MCP_JAR 등록

## 분석 대상
| 대상 | 경로 | SHA-256 |
|---|---|---|
| 설치 DMG | `~/Downloads/Ontological-Studio-mac-arm64.dmg` | d49694ba6d699589a086ab7f3499dd7d151ba7cd5e64137d86dba6409f01dae0 |
| 설치된 앱 | `/Applications/Ontological Studio.app` | (디렉터리) |
| app.asar | `Contents/Resources/app.asar` | d7d700700c075d5a0179d8434cccbd417162d183e47ff8befb90614db92a26e4 |

- 앱 소스 추출본: `./extracted-app-asar/` (src/main, src/preload, src/renderer, package.json)
- `evidence-bundle.json`은 세션 종료 후 내보내서 0건 — 재분석 필요 시 다시 실행하고 **close 전에** export 할 것.
- DMG 내부 앱과 설치된 앱의 동일성은 미검증.

## 1차 분석 결과 (정적 분석, 실행 안 함)

### 정체
- `ontology-studio-lite` v0.1.1, bundle id `org.uengine.ontological-studio`, author uEngine
- 자동 업데이트: GitHub `uengine-oss/ontological-studio` (`Resources/app-update.yml`)
- 서명: ad-hoc, TeamIdentifier 없음, 공증 없음 (spctl 거부)

### 아키텍처 (src/main/index.js 부팅 순서)
PostgreSQL → (첫 실행 bootstrap) → `ontological-bolt` (Bolt 게이트웨이, 네이티브) → Node 포털
→ fabric seed → Python Studio 백엔드(uvicorn) + MCP → kinetic-action + 예제 서비스 → UI
- 런타임: `Contents/Resources/runtime/` (417MB: pg, bin, portal, studio/python, studio/app, frontend, kinetic)
- 리소스: `Contents/Resources/resources/` (studio.env.example, agent_turn.py, code_app_turn.py, codeapp/, sample/)
- main 모듈: codeapps, fabric-bridge, kinetic, nl2cypher, ports, postgres, procs, services, tabs, tray, web
- 모든 서버 127.0.0.1 바인딩 (ports.js, postgres.js, web.js, kinetic.js, services.js)
- 사용자 데이터: `~/Library/Application Support/Ontological Studio/` (pgdata, secrets.json 0600, studio.env 0600, logs, sandbox, codeapps, sessions.db)

### Electron
- 렌더러: contextIsolation / sandbox / nodeIntegration:false, preload API `window.liteShell` (14개 멤버)
- IPC: lite:open, lite:info, lite:is-fullscreen, lite:window:new, lite:tabs:*, lite:nl2cypher
- Fuses: RunAsNode·NODE_OPTIONS·inspect 허용, ASAR 무결성 미강제, OnlyLoadAppFromAsar 꺼짐

### 보안 주목점
1. `runtime/studio/app/backend/src/modules/agent_session/cliagents_backend.py`
   - L223 Claude Code `--permission-mode bypassPermissions`
   - L375 Codex `--dangerously-bypass-approvals-and-sandbox`
   - 기본 AGENT_BACKEND=cliagents / claude-code
2. `MCP_ALLOW_DATASOURCE_EXPANSION=true` 기본 → 로컬 MCP로 원본 행 노출 (services.js studioEnv)

### 미분석
- `runtime/bin/ontological-bolt` 네이티브 바이너리 (Ghidra 후보)
- Python 백엔드 전체, 포털, kinetic
- 런타임 동작 관찰

## 다음 후보 작업
1. Ghidra로 ontological-bolt 분석
2. DMG vs 설치 앱 비교
3. 기능 흐름 추적 (nl2cypher, codeapps)
4. 위험 완화 studio.env 정리
5. (완료) REA 분석 → 실제 프로그램 구현 사례 조사 → `rea-to-code-cases.md`
   - 실사례는 주로 네이티브/.NET (DX-Ball, RRT2, hexgrab). Electron 앱 분석→재구현 사례는 없음.
   - 통한 패턴: REA 증거 → 명세/설계표 문서 → 구현 → 원본 동작과 대조 검증
   - REA reconstruction 도구(ledger/coverage/verify)의 실사용 공개 기록은 없음

## 현재 상태 (2026-10-31)
- ADR 0001–0008 승인. 분석 기준은 배포본(ADR-0008).
- `feature-map.md` 초안 v0.1 작성: 홈 카드 8개(M1–M8) ↔ 튜토리얼 장 ↔ 배포본 코드 후보, 공통 기반 A1–A3 범위.
- **다음: A1 셸·부팅·프로세스 분석** (ADR-0006 6단계, 산출물 `common/A1-shell/`).
- (추가) ADR 0010–0014 승인: 에이전트 기능 구조·계약 비교 / 구현은 설계 문서만 받은 별도 세션 / 0.1.1 고정(DMG `artifacts/` 보관, 해시 일치 확인) / 검토 = 시나리오 + 설계 문서 / 깊이 기준·프런트엔드 근거.
- 대상 하나당 사용자 검토 2회: 1단계 후(user-scenarios.md), 5단계 후(design.md).

## 진행 로그 — 2026-10-31 밤 (ADR-0015 자율 진행)
- 공통 색인 `shared/` 생성(API 문자열, 라우트 목록, 앱 바로가기 링크), 작업 지침 `BRIEF.md`.
- DMG ↔ 설치본 파일 17,572개 SHA-256 전부 일치 확인 (`artifacts/app-0.1.1-file-manifest.sha256`).
- A1 정적 분석 완료: `common/A1-shell/{user-scenarios,code-trace,design}.md`.
- 1차 에이전트(A2, A3+M8, M3, M4) 실행 중 → 끝나면 2차(M7, M1, M6, M2, M5).
- **실행 기록(4단계) 보류**: 샌드박스에서 앱이 즉시 종료, 샌드박스 해제는 거부됨 (ADR-0017, REVIEW.md 1번).
- 2026-11-01 02:00 사용량 한도(429)로 에이전트 4개 중단 → 한도 해제 후 재개, 전부 완료.
- **정적 분석 11개 대상 전부 완료** (A1–A3, M1–M8). 결과·결정 대기 항목은 REVIEW.md (24개 항목).
- 사용자 요청(2026-11-01): 분석 후 **통합 설계 문서(SoT)** 작성, 아키텍처 고려, Palantir식 Object type 모델 반영 → ADR-0018, `~/Desktop/workplace/rea/spec/`.
- SoT `~/Desktop/workplace/rea/spec/` 핵심 문서 작성 완료(Claude): README, 00 비전·범위, 01 아키텍처, 02 온톨로지 메타모델(Palantir식), 03 보안, 04 에이전트, 90 결정 대기(D-01–D-20).
- 기능 명세 F1–F8 + P는 에이전트 3개가 작성 중 (클린룸: design.md·user-scenarios.md·REVIEW.md만 참고).
- 2026-11-01 02:40 사용량 한도로 기능 명세 에이전트 3개가 최종 보고 전에 멈춤 — 단, 9개 파일 모두 마지막 절까지 작성 완료 확인(11:12).
- Claude 정합성 점검: 결정 번호 D-01–D-20만 참조, 클린룸 위반 없음(관찰 가능한 SDK 파일 이름만). 핵심 문서 변경 제안 3건 02에 반영(Property identifier·default, FK 복합 키 pairs, live 변환식 → 원천 뷰 컴파일).
- **SoT v0.1 완료** → 사용자 보정 대기.
