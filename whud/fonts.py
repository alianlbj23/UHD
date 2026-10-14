"""尋找系統上的中文字型（Jetson / Raspberry Pi OS 安裝 fonts-noto-cjk 即可）。"""
import os
import shutil
import subprocess

CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
]


def find_cjk_font(preferred=""):
    if preferred and os.path.exists(preferred):
        return preferred
    if shutil.which("fc-match"):
        for pattern in ("Noto Sans CJK TC:bold", "Noto Sans TC:bold", ":lang=zh-tw"):
            try:
                out = subprocess.run(["fc-match", "-f", "%{file}", pattern],
                                     capture_output=True, text=True, timeout=3).stdout.strip()
            except (OSError, subprocess.SubprocessError):
                break
            # fc-match 找不到時會回傳 DejaVu 之類的西文字型，要排除
            low = out.lower()
            if out and os.path.exists(out) and any(k in low for k in ("cjk", "notosanstc", "wqy", "droid")):
                return out
    for p in CANDIDATES:
        if os.path.exists(p):
            return p
    return None
