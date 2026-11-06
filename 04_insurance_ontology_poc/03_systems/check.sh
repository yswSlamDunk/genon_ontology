#!/usr/bin/env bash
# 네 서버가 B0 값을 돌려주는지 확인한다 (서버_설계서.md 6.4절). 서버가 켜져 있어야 한다 (./run.sh start).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec "$HERE/.venv/bin/python" "$HERE/check.py"
