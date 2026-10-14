"""設定檔：預設值 + JSON 讀寫。未知欄位忽略，缺的欄位補預設值。"""
import json
import os
from dataclasses import dataclass, asdict, fields

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")


@dataclass
class Settings:
    # 擋風玻璃反射會左右顛倒，所以預設左右鏡像
    mirror_h: bool = True
    # 若螢幕倒放（排線朝駕駛）時需要上下翻轉
    flip_v: bool = False
    # 內容縮放與位移（像素），用來把畫面對到視線前方
    scale: float = 1.0
    offset_x: int = 0
    offset_y: int = 0
    # 軟體亮度 0.1~1.0（HDMI 螢幕無法用軟體調背光，只能壓暗像素）
    brightness: float = 1.0
    # 主色（白色在擋風玻璃上最清楚；夜間可改成綠色或琥珀色）
    color: tuple = (255, 255, 255)
    lyric_color: tuple = (170, 220, 255)
    # 視窗設定：fullscreen 時 width/height 會被螢幕原生解析度取代
    fullscreen: bool = True
    width: int = 1024
    height: int = 600
    fps: int = 30
    # 空字串 = 自動尋找中文字型
    font_path: str = ""
    # 模擬車速（km/h），用來倒數距離
    demo_speed_kmh: float = 40.0

    def clamp(self):
        self.scale = round(min(max(self.scale, 0.3), 2.0), 2)
        self.brightness = round(min(max(self.brightness, 0.1), 1.0), 2)
        self.color = tuple(int(c) for c in self.color)
        self.lyric_color = tuple(int(c) for c in self.lyric_color)
        return self


def load(path=DEFAULT_PATH):
    s = Settings()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        names = {f.name for f in fields(Settings)}
        for k, v in data.items():
            if k in names:
                setattr(s, k, v)
    return s.clamp()


def save(settings, path=DEFAULT_PATH):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(asdict(settings), f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)  # 原子寫入，避免拔電時設定檔損毀
