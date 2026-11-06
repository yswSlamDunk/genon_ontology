#!/usr/bin/env bash
# 시스템 인증 비밀 값 4개를 macOS 로그인 세션 환경에 넣는다 (서버_설계서.md 2.3절, 6.3절 4번).
# Studio 실행기(kinetic-action)는 앱이 시작될 때의 환경에서 비밀 값을 읽는다. studio.env 는 실행기에 전달되지 않는다.
# 실행 뒤 Studio 앱을 완전히 종료하고 다시 열어야 적용된다. 값은 출력하지 않는다.
#
#   ./studio-env.sh          # 넣기
#   ./studio-env.sh unset    # 지우기
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$HERE/.env.local"
NAMES=(INS_CONTRACT_API_KEY INS_INTAKE_BASIC INS_REVIEW_TOKEN INS_PAYMENT_API_KEY)

if [[ "${1:-}" == "unset" ]]; then
  for n in "${NAMES[@]}"; do launchctl unsetenv "$n"; done
  echo "지웠습니다: ${NAMES[*]}"; exit 0
fi
[[ -f "$ENV_FILE" ]] || { echo "$ENV_FILE 이 없습니다. ./run.sh start 를 먼저 실행하세요." >&2; exit 1; }
for n in "${NAMES[@]}"; do
  v="$(grep "^$n=" "$ENV_FILE" | cut -d= -f2-)"
  [[ -n "$v" ]] || { echo "$n 값이 없습니다" >&2; exit 1; }
  launchctl setenv "$n" "$v"
done
echo "넣었습니다: ${NAMES[*]}"
echo "이제 Studio 앱을 완전히 종료(⌘Q)하고 다시 여세요."
