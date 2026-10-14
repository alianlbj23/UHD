#!/usr/bin/env bash
# 安裝相依套件；加 --autostart 會設定登入桌面後自動全螢幕啟動
# 適用：Jetson (JetPack 5/6, Ubuntu 20.04/22.04) 與 Raspberry Pi OS (Bookworm)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -f /etc/nv_tegra_release ]; then PLATFORM=jetson
elif grep -qi "raspberry pi" /proc/device-tree/model 2>/dev/null; then PLATFORM=rpi
else PLATFORM=generic; fi
echo "== 平台：$PLATFORM"

sudo apt-get update
sudo apt-get install -y python3-venv python3-pip fonts-noto-cjk fontconfig x11-xserver-utils

# --system-site-packages：pip 裝不起來時可退回 apt 版 pygame
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -U pip
if ! .venv/bin/pip install -r requirements.txt; then
  echo "== pip 安裝 pygame 失敗，改用 apt 版"
  sudo apt-get install -y python3-pygame
fi
.venv/bin/python -c "import pygame; print('pygame', pygame.version.ver)"
fc-match -f '%{file}\n' 'Noto Sans CJK TC:bold'

if [ "$1" = "--autostart" ]; then
  mkdir -p ~/.config/autostart
  cat > ~/.config/autostart/whud.desktop <<DESK
[Desktop Entry]
Type=Application
Name=W-HUD
Exec=$ROOT/scripts/run.sh
X-GNOME-Autostart-Delay=3
DESK
  # GNOME（Jetson 預設桌面）：關閉閒置黑屏與鎖定
  if command -v gsettings >/dev/null; then
    gsettings set org.gnome.desktop.session idle-delay 0 2>/dev/null || true
    gsettings set org.gnome.desktop.screensaver lock-enabled false 2>/dev/null || true
  fi
  echo "== 已設定自動啟動：~/.config/autostart/whud.desktop"
  if [ "$PLATFORM" = jetson ]; then
    echo "== 還需要開啟自動登入：sudo nano /etc/gdm3/custom.conf"
    echo "   在 [daemon] 下加入：AutomaticLoginEnable=true 與 AutomaticLogin=$USER"
  elif [ "$PLATFORM" = rpi ]; then
    echo "== 用 sudo raspi-config → System Options → Boot / Auto Login → Desktop Autologin"
    echo "   並在 Display Options → Screen Blanking 關閉螢幕空白"
  fi
fi
echo "== 完成。執行：$ROOT/scripts/run.sh   （視窗預覽：加 --windowed）"
