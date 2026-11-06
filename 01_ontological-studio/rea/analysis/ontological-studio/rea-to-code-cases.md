# REA로 기존 앱을 분석해 새 프로그램을 만든 사례 조사

조사일: 2026-10-31
조사 범위: REA 저장소 로컬 클론(`rea-src`, docs/·website/·README), GitHub 코드 검색(`gh search code`), 공개 저장소 README와 문서, 커뮤니티 사례 모음 `songshikang0111/awesome-REA-cases`, 웹 검색.
주의: 인용한 저장소와 게시글의 내용은 모두 작성자 본인의 보고다. 이 조사에서는 빌드, 실행, 테스트를 재현하지 않았다.

---

## 1. 요약

- **실제 사례는 있다. 확실성도 높다.** 다만 거의 전부가 네이티브 바이너리(게임 EXE, PE/ELF, Switch/PS4 실행 파일)나 .NET/Android 앱이 대상이다. 공개 저장소에 REA 버전, Evidence ID, 워크플로가 함께 기록돼 있어 "REA로 분석한 뒤 코드를 작성했다"는 사실을 1차 자료로 확인할 수 있는 사례가 최소 5~6건 있다.
  - DX-Ball 재구성(C, 270개 함수 전부 바이트 일치, 플레이 가능)
  - Railroad Tycoon II Rust 재구현
  - hexgrab(PowerToys Color Picker를 연구한 뒤 만든 새 .NET 도구)
  - ShapeCrawler의 Aspose.Slides 기능 동등성 작업
  - Brother 스캔 버튼 대체 Go 서비스
  - OKOK Libre(광고 앱을 대체하는 Android 체중계 클라이언트)
  - gagarin(Yuri's Revenge C++ 재구성)
  - 그 밖에 여러 콘솔/PC 포트 프로젝트(B2recomp, Order:1886, TLG PC, fenji, OpenBattlefield2 등)가 REA를 분석 도구로 명시한다.
- **Electron/JavaScript 앱을 REA로 분석해 다시 구현한 실제 사례는 찾지 못했다.** Electron 쪽 공개 사례(Notion clipboard, T3 Code bridge, Obsidian ASAR, Hamza의 notes 샘플, "hidden network call" 블라인드 테스트)는 모두 **분석만 했거나 정답지와 비교한 테스트**에 그친다. "Electron 앱을 REA로 분석해서 클론했다"는 주장(T3 Code 100-agent 리빌드, 익명 SaaS 워크플로 클론)은 코드나 근거가 없는 미검증 주장이다.
- **REA 자체의 reconstruction 도구(`build_reconstruction_obligation_ledger`, `evaluate_reconstruction_coverage`, `verify_reconstruction`, `import_managed_reconstruction`)를 실제 재구현 프로젝트에서 쓴 공개 기록은 찾지 못했다.** 실제 사례들은 REA의 **분석 도구**(`analyze_function`, `read_bytes`, `inspect_managed_*`, `search_strings`/`xrefs`/`procedure_pseudo_code`, `export_evidence_bundle`)로 증거를 모으고, 검증은 **각 프로젝트의 자체 오라클**로 했다. 자체 오라클의 예는 원본 시대 컴파일러로 바이트 비교, Unicorn 차등 테스트, 원본을 실행해서 행동 관찰 등이다.
- REA 공식 문서는 "REA는 분석 결과를 주고, 구현과 테스트는 에이전트가 한다"고 분명히 말한다(README FAQ: "Your agent uses these findings to write and test an implementation; the showcases give worked examples.").

---

## 2. 사례 목록

확실성 등급:
- **A**: 1차 공개 저장소에 REA 사용과 산출 코드가 함께 있다.
- **B**: 작성자 게시글과 공개 코드는 있지만 REA의 구체적 역할은 일부만 확인된다.
- **C**: 작성자 주장만 있다.
- **D**: 공식 문서에 나온 의도된 워크플로이며 사용자 사례가 아니다.

### 2.1 실제 사용자 사례 (재구현, 대체 구현, 상호운용 도구)

| # | 대상 → 만든 것 | REA 사용 방식 (도구와 단계) | 산출물이 코딩 단계에 들어간 방식 | 확실성 | 출처 |
|---|---|---|---|---|---|
| 1 | **DX-Ball 1.07 (Win32 PE i386)** → 읽을 수 있는 C/C++ 소스 재구성. VC4로 빌드한 게임이 실행된다 | Codex + REA(4.1.0에서 6.4.0) + Ghidra. `analyze_function`(명령어, 의사코드, caller/callee, 데이터 참조) → caller를 따라 `analyze_function` → `read_bytes`로 상수(double) 읽기. 결과는 `scripts/rea` 스냅샷과 Evidence ID로 저장 | 저장해 둔 REA 응답과 연구 노트(원본 주소와 재구성 함수 매핑)를 바탕으로 `src/*.c`를 작성한다. VC4.0으로 컴파일해 원본과 함수 단위로 바이트 비교하고, 차이가 나면 그 지점이 다음 REA 질의 대상이 된다. 2026-10-22 기준 270개 함수, 84,968바이트가 전부 일치하고 Wine에서 플레이 검증을 했다 | **A** | https://github.com/N0zoM1z0/dx-ball (README, docs/REA.md), https://rea.tools/showcase/dx-ball/, 로컬 `website/evidence/dx-ball-sound-pan.md` |
| 2 | **Railroad Tycoon II Platinum** → Rust 재구현(rt2-sim, wgpu 렌더러, 에디터, 멀티플레이) | REA MCP + Ghidra. 역할별 Claude 에이전트(`.claude/agents/`)가 문자열, import, 데이터 테이블을 기준점으로 서브시스템을 분석한다 | 분석 결과를 먼저 **사양서**(`docs/spec/*.md`: 주소, 상수, 의사코드)로 쓰고 나서 Rust로 구현한다. Unicorn으로 원본 함수를 돌려 bit-exact 차등 비교(304개 함수)를 하고, 같은 세이브를 원본(Wine)과 클론에서 진행시켜 필드 단위로 비교한다(131개 케이스 일치). pre-alpha 단계 | **A** | https://github.com/pedryvo/rrt2-decomp (README "analysis uses Ghidra through the REA MCP server") |
| 3 | **PowerToys Color Picker 0.98.0 (.NET UI DLL + 네이티브 DLL)** → 새 .NET 10 도구 **hexgrab**. 코드 복사 없이 설계만 참고 | REA 6.4.0 + Ghidra. ① `inspect_managed_artifact` ② `inspect_managed_native_boundaries`(Win32 API로 구조 파악) ③ `inspect_managed_members`(CLI. 2.7MB라 MCP로는 너무 커서 Python으로 필터링) ④ 네이티브 DLL에 `open_binary` → `search_strings` → `xrefs` → `procedure_pseudo_code` → `procedure_callers` ⑤ `search_procedures` ⑥ `export_evidence_bundle` | `docs/rea-findings.md`에 "PowerToys가 하는 일 / hexgrab이 하는 일 / 이유" 표를 만들고, 이 표가 설계 문서 역할을 했다. 공개 소스와 비교해 채점한 결과 9개 주장 중 8개가 맞고 1개가 부분적으로 맞았다(hotkey 등록이 분석하지 않은 runner 바이너리에 있었다) | **A** | https://github.com/iammukeshm/hexgrab/blob/511c58078776af4fb0d2e3601e098f98e9f90c9a/docs/rea-findings.md |
| 4 | **Aspose.Slides.NET 24.12.0** → 오픈소스 **ShapeCrawler**에 동등 기능을 독립 구현(10회 반복, 각각 PR) | `npx rea-agents@6.7.0 inspect-managed-artifact`, `inspect-managed-members --type ...`. **멤버 조회는 매번 64MiB 메타데이터 예산 초과로 `unavailable`이었다.** `decompile`은 managed 대상 provider가 없었고, `capture-process`는 Windows PTY를 지원하지 않아 실패했다 | REA로 구현 내용은 얻지 못했다. 공개 API 문서와 평가판 Aspose 실행 결과(저장한 PPTX XML 관찰)로 동작을 정했다. 각 반복의 레퍼런스 버전, Evidence ID, 한계, 회귀 테스트를 원장(`aspose-feature-parity.md`)에 기록했다 | **A** (REA 사용은 확인됨. 단 REA 기여는 식별/한계 확인에 그침) | https://github.com/ShapeCrawler/ShapeCrawler/blob/master/docs/aspose-feature-parity.md |
| 5 | **Brother Scan-to-PC 앱** (macOS Push Scan Tool, Linux brscan5) → Go 서비스(SMB/FTP/S3로 스캔을 보내고 웹 UI 제공) | Claude + REA + Ghidra로 `libLxBsScanCoreApi`를 분석했다(README 명시). 기존 brother-scand 작업 위에 쌓았다 | 프로토콜(HTTPS/SNMP 등록, UDP 54925 이벤트, TCP 54921 데이터)을 복원한 뒤 Go로 상호운용 서버를 구현했다. 테스트한 기종은 MFC-L2800DW 하나 | **B** | https://github.com/aurimasniekis/go-brother-scan-to-network-server, awesome-REA-cases 항목 |
| 6 | **OKOK International Android 앱(약 50MB APK)** → **OKOK Libre**(오프라인 Android 체중계 클라이언트, GPL-3.0) | REA + GLM 5.3으로 APK를 분석해 체성분 공식과 BLE 프로토콜을 추출했다. UI는 Opus 5.5가 만들었다. 구체적 도구명은 공개되지 않았다 | 추출한 BLE 프로토콜 3종(classic, OKOKCloud, V4)과 공식을 Kotlin 구현으로 옮겼다. 공식이 원본과 같은지는 검증되지 않았다 | **B** | https://github.com/JYunth/okok-libre, https://x.com/i/status/2116488683188887716 |
| 7 | **C&C Yuri's Revenge gamemd.exe** → **gagarin**(구조화된 C++ 재구성, MSVC6 오라클) | README에 "focused reverse engineering and evidence gathering"에 REA와 Ghidra를 썼다고 명시돼 있다 | 원본 명령어와 VC6 오라클로 일치 여부를 판정한다. 10,204개 함수 일치(51.6%). 링크된 이미지는 아직 실행되지 않는다 | **A/B** | https://github.com/r-melvin/gagarin |
| 8 | **Moon-Buggy (stripped ELF)** → 단일 `index.html` 브라우저 게임 | Claude Code(Opus 5.5) + REA + Ghidra. 문자열(`score_crater` 등)에서 참조를 따라가 규칙(스크롤, 점프, 장애물, 점수)과 주소/상수를 복원했다. 근거는 `ANALYSE.md`로 남겼다 | 복원한 규칙 목록을 그대로 HTML/JS 구현의 사양으로 썼다(12분 29초). 작성자가 원본 소스와 대조해 확인했다(명칭 오류 1건) | **B** (교육용 블로그 실험) | https://www.it-connect.fr/rea-retro-ingenierie-ia-ghidra/ |
| 9 | **Touhou TH08/TH095/TH04** → 소스 재구성과 Linux/Web/x64 포트 | 같은 저자(N0zoM1z0)의 방법론. 공식 블로그에 따르면 "REA gives the agent access to analysis tools", 검증은 프로젝트 자체 컴파일러 오라클이 맡는다. **단, 초기 프로젝트는 자체 분석 스크립트를 썼고 TH04 쇼케이스의 REA 조회는 사후에 새로 한 것이라고 명시돼 있다** | 정확한 기준선 → 원래 플랫폼 빌드 → 의미 복원 → 포트 순서 | **B** (REA의 역할이 일부 회고적임) | https://rea.tools/showcase/th04/, 로컬 `website/evidence/touhou-reconstruction-method.md`, https://github.com/N0zoM1z0/th08 |

### 2.2 REA를 분석 도구로 명시한 포트/재구현 프로젝트 (REA 역할이 보조적이거나 일부만 기록됨)

| 프로젝트 | 만든 것 | REA 사용 기록 | 확실성 |
|---|---|---|---|
| K0NL/B2recomp | Bayonetta 2(Switch) 정적 재컴파일 Windows 포트 | NOTICE: "AI helped in reverse engineering the game, with Ghidra and REA"(`rea-agents` 6.5.0) | B |
| mateussmeneses/theorder1886-port | The Order: 1886(PS4) PC 네이티브 포트 | `docs/ENGINE_RE.md`: eboot를 PE로 감싸 REA(Ghidra)로 디컴파일하고, `main`의 argv 처리 등을 분석했다 | B |
| HayatoG/tlg_pc | The Last Guardian(PS4) PC 포트 | "Ghidra/REA는 **국소 조사용**(버그, 패치, API 계약)이며 게임을 다시 쓰는 데 쓰지 않는다" | B |
| Moxnatiy/OpenBattlefield2 | Refractor 2 엔진 클린룸 C++20 재구현 | `tools/rea.sh`: `rea-agents@4.1.0`으로 `function`, `search`, `resolve-native-call-targets`를 호출하고 바이너리별 스냅샷 캐시를 둔다 | B |
| theintonerzero/fenji | MMO 클라이언트용 클린룸 Rust 서버 에뮬레이터 | `docs/re/README.md`: REA를 "evidence ledger"로 쓴다. 새 발견마다 `procedure_pseudo_code` Evidence ID를 인용하고, Rust 정의(`crates/fenji-proto`)는 그 증거를 인용한다 | A/B |
| smm2recomp/smm2recomp | Super Mario Maker 2 recomp | TOOLCHAIN: REA 6.4.0 MCP가 "Primary RE interface" | B |

### 2.3 Electron/JavaScript 관련 사례 (재구현까지 간 사례는 없음)

| 사례 | 내용 | 등급 |
|---|---|---|
| Notion Desktop 7.6.1 clipboard (공식 쇼케이스) | `analyze_javascript_application`(preload 대상) → contextBridge `__electronApi`, IPC invoke 위치 → 패키지 소스를 읽어 `notion:clipboard:write` → main의 `clipboard.write`. `trace_application_feature`는 부분 커버리지만 나왔다. **분석만 했다** | D/A (공식이 수행한 분석) |
| T3 Code (devtoollab) | REA 정적 분석으로 renderer bridge 멤버 121개를 모두 복원했지만 webview isolation override는 놓쳤다. "100 Claude 리빌드" 주장은 근거가 없다 | C |
| Obsidian ASAR (REA issue #746) | 24MB ASAR 분석 완료. 기능 재구현은 없다 | B (분석 테스트) |
| Electron hidden network call 블라인드 테스트, Hamza notes 샘플, Codex 3-fixture | 직접 만든 정답지/샘플로 IPC와 export 경로를 추적했다 | C/B (분석 테스트) |
| Karthik Nish SaaS 단일 워크플로 클론 | "REA MCP로 조사해 반나절 만에 개인 버전" 주장. 대상, 코드, 출력 모두 없다 | C |
| Yıldız 화면 녹화기 | REA 기반 버전을 라이선스 검토 후 비공개로 돌리고 REA 없이 다시 만들기로 했다 | C |
| n1m21n/Infinite (cables.gl 조사) | REA 6.4.0으로 cables.app(Electron)을 분석했지만 Electron 셸(IPC 11개, 네이티브 애드온 2개)만 다뤘고 ops 카탈로그는 얻지 못했다. 결국 다른 리더로 우회했다 | B (한계 기록으로 유용) |

### 2.4 공식 워크플로/데모 (사용자 사례 아님)

- **AgentEnv(RL 환경) 빌드**: `rea environment-build session.har ./my-env`(또는 MCP `export_environment_bundle`)로 기록한 웹앱 세션에서 MCP 도구와 상태 서버를 갖춘 **실행 가능한 대체 환경**을 만든다. Grafana HAR 예시와 공식 X 데모 영상이 있다. "기존 앱을 분석해 새 프로그램(모의 서버)을 생성"하는 유일한 **공식 자동 생성** 경로다. 생성되는 것은 원본의 재구현이 아니라 캡처를 재생하거나 캡처에서 유도한 상태로 응답하는 환경이다. 등급 D.
- **Reconstruction readiness 검증**(`npm run verify:readiness`): 합성 9단계 입력으로 평가기를 검증한다. 문서가 직접 "end-to-end reconstruction-readiness verdict가 아니다"라고 밝힌다. 등급 D.
- **ILSpy 오라클 → `import_managed_reconstruction`**: `verify:managed`에서 ILSpy C# 출력을 정적 멤버 Evidence에 대해 "reconstruction inference"로 가져온다. 개발/CI용이다. 등급 D.

---

## 3. REA가 공식 지원하는 "분석 → 재구현" 워크플로 (문서에 있는 것만)

REA는 **코드를 생성하지 않는다.** 분석 증거를 주고, 재구현이 얼마나 완료됐는지를 증거 기반으로 판정하는 장부를 제공한다. 구현 코드, 픽스처, 검증기 실행은 호출자(에이전트나 프로젝트)가 맡는다.

| 단계 | 도구 (MCP / CLI) | 문서상 역할 | 문서 |
|---|---|---|---|
| 1. 분석 | 네이티브: `open_binary`, `analyze_function`, `read_bytes`, `xrefs`, `procedure_pseudo_code` 등. JS/Electron: `analyze_javascript_application`(정적 Application Graph와 semantic relation graph), `recover_javascript_sources`(Wakaru, Linux x64, 호출자가 제공), `trace_application_feature`, `trace_javascript_semantics`, `compare_source_to_bundle`, `compare_javascript_export_shapes`. 런타임: `capture_electron_scenario`, `observe_javascript_runtime`, `reconcile_javascript_runtime`. Managed: `inspect_managed_*` | 증거(Evidence ID = 레코드의 SHA-256) 생성 | `javascript-artifact-reconstruction.md`, `javascript-application-workflows.md`, `javascript-recovery.md`, `managed-code-analysis.md` |
| 2. 증거 묶기 | `export_evidence_bundle` / `import_evidence_bundle` | 세션 증거를 인증 가능한 번들로 묶는다 | `mcp-contracts.md` |
| 3. 의무(obligation) 장부 | `build_reconstruction_obligation_ledger` / `rea build-reconstruction-obligation-ledger` | Application Graph와 프로세스 캡처에서 **후보 의무**를 자동 생성하고, 사람이 검토한 의무(예: CLI 파싱, 프로토콜 취소, **Electron 백그라운드 시작 순서**, 영속성 마이그레이션, 네이티브 ABI)를 추가한다. manifest binding(소유 모듈, `owner_sha256`, 원본 케이스, 재구성 픽스처, 검증기 결과)이 모두 갖춰져야 의무가 닫힌다. 정적 증거만으로는 런타임 의무를 닫을 수 없고, 단위 테스트 통과만으로는 `packaged-process` 의무를 닫을 수 없다. REA는 검증 명령을 실행하지 않는다 | `reconstruction-obligation-ledgers.md` |
| 4. 경계 커버리지 | `evaluate_reconstruction_coverage` / `rea evaluate-reconstruction-coverage` | 선택한 `boundary_id`의 표면, 클레임, 의존성 폐포에 대해 검증기 증거의 권위(shipped-artifact, controlled-replay, live-observation, external)와 패키지 증명(빌드, clean-install, 런타임 라우팅)을 평가한다 | `reconstruction-coverage.md` |
| 5. 함수 재구성 클레임 | `verify_reconstruction`(MCP 도구와 같은 이름의 prompt) | 보관된 비교 Evidence(`compare_functions`, `match_native_functions` 등)에 대해 유한 재구성 사양을 평가한다. 미해결 unknown이 있으면 `unknown` | `reconstruction-coverage.md`, `mcp-prompts.md` |
| 6. Managed 디컴파일 결과 가져오기 | `import_managed_reconstruction` | BYO ILSpy 등의 C# 출력을 정적 멤버 식별자에 붙여 "비정규(non-canonical) reconstruction inference"로 기록한다 | `managed-code-analysis.md` |
| 7. 웹앱 → 에이전트 환경 | `capture_browser_scenario` → `rea environment-build` / `export_environment_bundle` → `agent-env run` | HAR이나 캡처에서 MCP 도구, 상태, smoke task를 갖춘 번들을 만든다 | `agent-environments.md`, `agent-environments-quickstart.md` |

보조 장치: `guided_workflows`(prompt: `investigate_feature`, `compare_application_versions`, `verify_reconstruction` 등), `record_unknown`/`update_unknown`/`verify_unknown_resolution`(남은 불확실성 추적).

**실제 사례와의 간극**: 공개된 성공 사례들은 3~6단계(ledger, coverage, verify_reconstruction)를 쓰지 않았다. 대신 프로젝트별 원장(`semantic-acceptance.csv`, `match-units.toml`, `re/coverage.toml`, `aspose-feature-parity.md`)과 자체 오라클을 썼다. 형태는 REA ledger와 비슷하다.

---

## 4. Ontological Studio(Electron + 번들 Python/Postgres)에 주는 시사점

1. **JS/Electron 층의 정적 분석은 검증된 경로다.** `analyze_javascript_application`으로 main, preload, renderer, IPC 채널, contextBridge API를 뽑을 수 있다(Notion, T3 Code, Obsidian 사례). 다만 동적 채널명(`channel_expression: "e"`)이나 webview isolation 같은 보안 설정은 놓칠 수 있다. 번들에서 빠진 값은 `capture_electron_scenario`/`observe_javascript_runtime`로 보완해야 한다.
2. **번들 Python 서비스는 REA 커버리지가 약하다.** PyInstaller CArchive 인벤토리와 추출(`inspect_artifact`/`extract_artifact`)과 `inspect_python_pyc`는 되지만, 문서상 바이트코드 소스 디컴파일은 범위 밖이다. Postgres는 바이너리 분석 대상이 아니다. 스키마와 마이그레이션 SQL 파일, 그리고 런타임 관찰로 접근해야 한다.
3. **실제 사례들이 공통으로 쓴 패턴을 따르는 편이 낫다.** REA 결과를 **사양서나 설계 표**로 먼저 문서화한다(rrt2의 spec, hexgrab의 "원본이 하는 일 / 우리가 할 일" 표). 그다음 구현하고, **원본 대비 오라클**로 확인한다. 이 앱에서 오라클은 IPC 요청/응답 녹화 재생, HTTP API(HAR) 비교, DB 상태 비교가 된다. 로컬 HTTP API가 있다면 `environment-build`(HAR 기반 모의 서버)를 행동 기준선이나 테스트 더블로 쓸 수 있다.
4. **reconstruction ledger를 실제로 쓴 선례가 없다.** 쓰려면 의무 정의, `owner_sha256` 규약, 검증기 증거 생산을 직접 설계해야 한다. 문서의 Electron 예시 의무("background process before renderer bridge")가 출발점이 된다. 단, `packaged-process`/`controlled-replay` 권위는 정적 분석만으로 닫히지 않는다.
5. **법적/윤리적 경계**: hexgrab과 ShapeCrawler는 "원본 코드를 복사하지 않고 관찰된 동작만 반영"하고 그 근거를 기록했다. 클린룸 원칙을 문서화하는 관행을 따르는 것이 좋다.

---

## 5. 출처

REA 저장소 (로컬 클론, `rea-src/`)
- `README.md` (Showcases, FAQ "What code does REA return?")
- `docs/reconstruction-obligation-ledgers.md`, `docs/reconstruction-coverage.md`, `docs/reconstruction-readiness.md`
- `docs/javascript-artifact-reconstruction.md`, `docs/javascript-application-workflows.md`, `docs/javascript-recovery.md`, `docs/python-packaged-applications.md`
- `docs/managed-code-analysis.md` (도구 표, ILSpy 오라클, `import_managed_reconstruction`)
- `docs/agent-environments.md`, `docs/agent-environments-quickstart.md`, `docs/mcp-prompts.md`, `docs/roadmap.md`
- `website/evidence/dx-ball-sound-pan.md`, `th04-bullet-ring.md`, `notion-clipboard.md`, `touhou-reconstruction-method.md`, `rl-environments.md`

공식 웹
- https://rea.tools/showcase/dx-ball/ · https://rea.tools/showcase/th04/ · https://rea.tools/showcase/notion/
- https://rea.tools/guides/rl-environments/ · https://x.com/reatools/status/2112574822584918075

사용자 프로젝트 (1차)
- https://github.com/N0zoM1z0/dx-ball (README, docs/REA.md)
- https://github.com/pedryvo/rrt2-decomp
- https://github.com/iammukeshm/hexgrab/blob/511c58078776af4fb0d2e3601e098f98e9f90c9a/docs/rea-findings.md
- https://github.com/ShapeCrawler/ShapeCrawler/blob/master/docs/aspose-feature-parity.md
- https://github.com/aurimasniekis/go-brother-scan-to-network-server
- https://github.com/JYunth/okok-libre
- https://github.com/r-melvin/gagarin
- https://github.com/K0NL/B2recomp (NOTICE.md)
- https://github.com/mateussmeneses/theorder1886-port (docs/ENGINE_RE.md)
- https://github.com/HayatoG/tlg_pc (docs/TECNICO.md)
- https://github.com/Moxnatiy/OpenBattlefield2 (tools/rea.sh)
- https://github.com/theintonerzero/fenji (docs/re/README.md)
- https://github.com/smm2recomp/smm2recomp (docs/TOOLCHAIN.md)
- https://github.com/n1m21n/Infinite (docs/plans/re-survey/README.md)
- https://github.com/N0zoM1z0/th08 · https://github.com/N0zoM1z0/th04
- https://www.it-connect.fr/rea-retro-ingenierie-ia-ghidra/

2차 모음 / 커뮤니티
- https://github.com/songshikang0111/awesome-REA-cases (INDEX.en.md, cases/en/*: hexgrab, rrt2, brother-scan, okok-libre, karthiknish-saas, t3-code, moon-buggy, gagarin, obsidian-asar)
- https://github.com/morluto/rea/issues/746 (Obsidian ASAR)
- aitoolly.com GitHub trending 기사들 (내용이 일반적이라 근거로 쓰지 않음)
