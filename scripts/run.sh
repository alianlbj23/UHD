#!/usr/bin/env bash
# 啟動 HUD（開機自動啟動也是呼叫這支）
set -e
cd "$(dirname "$0")/.."
# 關閉螢幕保護與省電關螢幕（X11；Wayland 下這行會靜默失敗，無妨）
if [ -n "$DISPLAY" ] && command -v xset >/dev/null; then
  xset s off -dpms s noblank 2>/dev/null || true
fi
PY=python3
[ -x .venv/bin/python ] && PY=.venv/bin/python
exec "$PY" -m whud "$@"
