#!/usr/bin/env bash
# 보험 PoC 업무 시스템 서버 4개를 켜고 끈다 (서버_설계서.md 4절, 6.3절).
#
#   ./run.sh start     # 네 서버 시작 (처음이면 의존성 설치, 비밀 값 생성)
#   ./run.sh stop
#   ./run.sh restart
#   ./run.sh status
#
# DB 접속: 127.0.0.1:5432 / insurance / ins_service. 비밀번호는 ../02_data/.env.local 의 INS_SERVICE_PASSWORD.
# 비밀 값(시스템 인증)은 .env.local 에 만든다 (권한 600). 화면에 출력하지 않는다.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LOGS="$HERE/logs"
ENV_FILE="$HERE/.env.local"
DATA_ENV="$HERE/../02_data/.env.local"
SERVICES=(contract intake review payment)
port_of() { case "$1" in contract) echo 18101;; intake) echo 18102;; review) echo 18103;; payment) echo 18104;; esac; }

rand() { openssl rand -base64 24 | tr -d '/+=' | cut -c1-32; }

ensure_env() {
  if [[ ! -f "$ENV_FILE" ]]; then
    ( umask 077
      {
        echo "INS_CONTRACT_API_KEY=$(rand)"
        echo "INS_INTAKE_BASIC=intake-svc:$(rand)"
        echo "INS_REVIEW_TOKEN=$(rand)"
        echo "INS_PAYMENT_API_KEY=$(rand)"
      } > "$ENV_FILE" )
    echo "시스템 인증 비밀 값을 만들었습니다: $ENV_FILE"
  fi
  # 2단계: 지급 연계 콜백 서명 비밀 값 (Studio에는 넘기지 않는다, 서버_설계서.md 7.6절)
  if ! grep -q '^INS_PAYMENT_CALLBACK_SECRET=' "$ENV_FILE"; then
    ( umask 077; echo "INS_PAYMENT_CALLBACK_SECRET=$(rand)" >> "$ENV_FILE" )
    echo "지급 콜백 서명 비밀 값을 추가했습니다"
  fi
  [[ -f "$DATA_ENV" ]] || { echo "DB 계정 파일이 없습니다: $DATA_ENV (02_data/reset.sh 를 먼저 실행)" >&2; exit 1; }
}

ensure_venv() {
  if [[ ! -x "$HERE/.venv/bin/python" ]] || ! "$HERE/.venv/bin/python" -c 'import httpx' 2>/dev/null; then
    command -v uv >/dev/null || { echo "uv 가 필요합니다 (https://docs.astral.sh/uv/)" >&2; exit 1; }
    echo "의존성 설치 (uv sync)…"
    (cd "$HERE" && uv sync --quiet --python 3.12)
  fi
}

pid_of() { lsof -nP -t -iTCP:"$(port_of "$1")" -sTCP:LISTEN 2>/dev/null | head -1 || true; }

health() { curl -s -o /dev/null -w '%{http_code}' --max-time 3 "http://127.0.0.1:$(port_of "$1")/health" || true; }

start() {
  ensure_env; ensure_venv; mkdir -p "$LOGS"
  set -a; source "$ENV_FILE"; set +a
  local svc_pw; svc_pw="$(grep '^INS_SERVICE_PASSWORD=' "$DATA_ENV" | cut -d= -f2-)"
  export INS_DSN="host=127.0.0.1 port=5432 dbname=insurance user=ins_service password=$svc_pw application_name=ins-systems"
  for s in "${SERVICES[@]}"; do
    if [[ -n "$(pid_of "$s")" ]]; then echo "$s: 이미 실행 중 (./run.sh restart 로 다시 시작)"; continue; fi
    # 실행한 셸과 완전히 분리한다 (입력·출력을 모두 바꾼다). 셸이 끝나도 서버는 계속 돈다
    (cd "$HERE/services" && nohup "$HERE/.venv/bin/python" -m uvicorn "$s:app" --host 127.0.0.1 --port "$(port_of "$s")" \
        --log-level info </dev/null >"$LOGS/$s.log" 2>&1 & disown) </dev/null >/dev/null 2>&1
  done
  unset INS_DSN
  for s in "${SERVICES[@]}"; do
    for _ in $(seq 1 30); do [[ "$(health "$s")" == 200 ]] && break; sleep 0.3; done
  done
  status
}

stop() {
  for s in "${SERVICES[@]}"; do
    local pid; pid="$(pid_of "$s")"
    # PID 파일의 프로세스와, 그 포트를 실제로 잡고 있는 프로세스를 모두 끈다 (실행 파일이 다른 PID로 바뀔 수 있다)
    local port_pids; port_pids="$(lsof -nP -t -iTCP:"$(port_of "$s")" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "$pid$port_pids" ]]; then kill $pid $port_pids 2>/dev/null || true; echo "$s: 중지"; else echo "$s: 실행 중 아님"; fi
    rm -f "$LOGS/$s.pid"
  done
}

status() {
  printf '%-9s %-6s %-8s %s\n' 시스템 포트 PID health
  for s in "${SERVICES[@]}"; do
    printf '%-9s %-6s %-8s %s\n' "$s" "$(port_of "$s")" "$(pid_of "$s" | grep . || echo -)" "$(health "$s")"
  done
}

case "${1:-status}" in
  start) start ;;
  stop) stop ;;
  restart) stop; start ;;
  status) status ;;
  *) echo "사용법: $0 start|stop|restart|status" >&2; exit 2 ;;
esac
