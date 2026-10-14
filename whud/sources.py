"""HUD 資料來源。

HudState 是渲染器唯一看的資料。測試版用 DemoSource 產生假資料；
正式版只要另寫一個 GpsSource / AncsSource 回傳同樣的 HudState 即可替換。
"""
from dataclasses import dataclass

ARROWS = ("straight", "left", "right", "slight_left", "slight_right", "uturn")


@dataclass
class HudState:
    arrow: str = "straight"
    distance_m: float = 0.0
    road: str = ""
    lyric: str = ""


# 假路線：(箭頭, 起始距離 m, 路名)
DEMO_ROUTE = [
    ("straight", 800, "中山北路二段"),
    ("right", 350, "民權東路"),
    ("slight_left", 500, "建國高架道路"),
    ("left", 200, "南京東路三段"),
    ("uturn", 150, "復興北路"),
    ("slight_right", 600, "市民大道"),
]

# 假歌詞（自編，避免版權問題）
DEMO_LYRICS = [
    "♪ 夜色裡的路燈 一盞一盞往後退",
    "♪ 收音機輕輕唱 把疲倦都吹散",
    "♪ 下一個路口 會遇見誰",
    "♪ 握緊方向盤 往有光的地方開",
]


def format_distance(m):
    if m >= 1000:
        return f"{m / 1000:.1f}", "km"
    # 導航慣例：大於 100 m 取整到 10 m
    if m >= 100:
        return f"{int(round(m / 10.0) * 10)}", "m"
    return f"{int(m)}", "m"


class DemoSource:
    def __init__(self, speed_kmh=40.0, lyric_period_s=4.0, route=DEMO_ROUTE, lyrics=DEMO_LYRICS):
        self.speed_kmh = speed_kmh
        self.lyric_period_s = lyric_period_s
        self.route = route
        self.lyrics = lyrics
        self.paused = False
        self.reset()

    def reset(self):
        self.step = 0
        self.remaining = float(self.route[0][1])
        self.lyric_t = 0.0
        self.lyric_idx = 0

    def next_step(self):
        self.step = (self.step + 1) % len(self.route)
        self.remaining = float(self.route[self.step][1])

    def update(self, dt):
        if not self.paused:
            self.remaining -= self.speed_kmh / 3.6 * dt
            if self.remaining <= 0:
                self.next_step()
            self.lyric_t += dt
            if self.lyric_t >= self.lyric_period_s:
                self.lyric_t -= self.lyric_period_s
                self.lyric_idx = (self.lyric_idx + 1) % len(self.lyrics)
        arrow, _, road = self.route[self.step]
        return HudState(arrow=arrow, distance_m=max(self.remaining, 0.0), road=road,
                        lyric=self.lyrics[self.lyric_idx])
