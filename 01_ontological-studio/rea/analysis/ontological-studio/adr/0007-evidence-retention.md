# ADR-0007 REA 세션은 닫기 전에 증거 내보내기
- 상태: 승인 (2026-10-31)
## 맥락
1차 분석 후 `close_binary`로 세션을 닫은 뒤 내보내 보니 0건이었다. REA 증거는 MCP 서버 메모리에만 있고 재시작하면 사라진다.
## 결정
대상별 REA 작업이 끝나면 `close_binary` **전에** `export_evidence_bundle`로 해당 대상의 `evidence/`에 저장한다.
