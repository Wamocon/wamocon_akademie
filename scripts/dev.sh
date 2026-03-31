#!/usr/bin/env bash
# Static preview: always from repo root, bind IPv4 localhost, replace stuck servers on :3000
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti tcp:3000 -sTCP:LISTEN 2>/dev/null || true)
  if [[ -n "${PIDS}" ]]; then
    echo "Port 3000 is in use — stopping listener(s): ${PIDS}"
    kill ${PIDS} 2>/dev/null || true
    sleep 0.4
  fi
fi

echo "Serving ${ROOT}"
echo "Open: http://127.0.0.1:3000/index.html"
exec python3 -m http.server 3000 --bind 127.0.0.1
