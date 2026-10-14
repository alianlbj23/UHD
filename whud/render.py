"""畫面繪製。

流程：在「正常方向」的 content 畫布上畫 HUD → compose() 做縮放 / 位移 /
亮度 / 鏡像 → 輸出到螢幕。所有內容（含設定提示）都走同一條鏡像路徑，
所以在擋風玻璃反射裡看到的永遠是正向文字。
"""
import math

import pygame

from .sources import format_distance

# 箭頭路徑，單位座標 [-1, 1]，y 向下；最後一點是箭頭尖端
_UTURN_ARC = [(0.4 * math.cos(a), -0.2 - 0.4 * math.sin(a))
              for a in (i * math.pi / 12 for i in range(13))]
ARROW_PATHS = {
    "straight": [(0.0, 0.9), (0.0, -0.9)],
    "right": [(-0.4, 0.9), (-0.4, -0.1), (0.85, -0.1)],
    "left": [(0.4, 0.9), (0.4, -0.1), (-0.85, -0.1)],
    "slight_right": [(-0.25, 0.9), (-0.25, 0.25), (0.6, -0.75)],
    "slight_left": [(0.25, 0.9), (0.25, 0.25), (-0.6, -0.75)],
    "uturn": [(0.4, 0.9)] + _UTURN_ARC + [(-0.4, 0.75)],
}


def draw_arrow(surf, kind, center, radius, color):
    cx, cy = center
    pts = [(cx + x * radius, cy + y * radius) for x, y in ARROW_PATHS[kind]]
    shaft_w = max(int(radius * 0.24), 2)
    head_len = radius * 0.5
    head_w = radius * 0.7

    tip = pts[-1]
    px, py = pts[-2]
    seg = math.hypot(tip[0] - px, tip[1] - py)
    dx, dy = (tip[0] - px) / seg, (tip[1] - py) / seg
    # 箭身止於箭頭底部稍內側，避免從箭頭尖端穿出
    base = (tip[0] - dx * head_len, tip[1] - dy * head_len)
    shaft = pts[:-1] + [(base[0] + dx * 2, base[1] + dy * 2)]

    # 每段畫成矩形多邊形（pygame.draw.lines 粗線在斜角會鋸齒），接頭補圓
    r = shaft_w / 2
    for (x1, y1), (x2, y2) in zip(shaft, shaft[1:]):
        L = math.hypot(x2 - x1, y2 - y1) or 1.0
        ox, oy = -(y2 - y1) / L * r, (x2 - x1) / L * r
        pygame.draw.polygon(surf, color, [(x1 + ox, y1 + oy), (x2 + ox, y2 + oy),
                                          (x2 - ox, y2 - oy), (x1 - ox, y1 - oy)])
    for p in shaft[:-1]:
        pygame.draw.circle(surf, color, (round(p[0]), round(p[1])), round(r))
    nx, ny = -dy, dx
    pygame.draw.polygon(surf, color, [
        tip,
        (base[0] + nx * head_w / 2, base[1] + ny * head_w / 2),
        (base[0] - nx * head_w / 2, base[1] - ny * head_w / 2),
    ])


class Renderer:
    def __init__(self, size, font_path=None):
        self.w, self.h = size
        self.font_path = font_path
        self._fonts = {}

    def font(self, px):
        px = max(int(px), 8)
        if px not in self._fonts:
            self._fonts[px] = pygame.font.Font(self.font_path, px)
        return self._fonts[px]

    def text(self, s, px, color, max_w=None):
        img = self.font(px).render(s, True, color)
        if max_w and img.get_width() > max_w:  # 太長就等比縮小，不截字
            k = max_w / img.get_width()
            img = pygame.transform.smoothscale(img, (int(img.get_width() * k), int(img.get_height() * k)))
        return img

    def draw_hud(self, state, settings):
        w, h = self.w, self.h
        surf = pygame.Surface((w, h))
        col = settings.color

        draw_arrow(surf, state.arrow, (int(w * 0.24), int(h * 0.40)), min(w * 0.19, h * 0.32), col)

        x0 = int(w * 0.46)
        avail = w - x0 - int(w * 0.04)
        num, unit = format_distance(state.distance_m)
        num_img = self.text(num, h * 0.30, col, max_w=avail * 0.75)
        unit_img = self.text(unit, h * 0.13, col)
        top = int(h * 0.10)
        surf.blit(num_img, (x0, top))
        # 單位與數字底部對齊
        surf.blit(unit_img, (x0 + num_img.get_width() + int(w * 0.015),
                             top + num_img.get_height() - unit_img.get_height() - int(h * 0.03)))
        road_img = self.text(state.road, h * 0.10, col, max_w=avail)
        surf.blit(road_img, (x0, top + num_img.get_height() + int(h * 0.02)))

        lyric_img = self.text(state.lyric, h * 0.075, settings.lyric_color, max_w=int(w * 0.92))
        surf.blit(lyric_img, ((w - lyric_img.get_width()) // 2, int(h * 0.84)))
        return surf

    def draw_calibration(self, settings):
        """校正畫面：格線看變形/梯形、圓看比例、F 與方位字看鏡像方向。"""
        w, h = self.w, self.h
        surf = pygame.Surface((w, h))
        col = settings.color
        grid = (90, 90, 90)
        for i in range(1, 10):
            pygame.draw.line(surf, grid, (w * i // 10, 0), (w * i // 10, h), 1)
            pygame.draw.line(surf, grid, (0, h * i // 10), (w, h * i // 10), 1)
        pygame.draw.rect(surf, col, (0, 0, w, h), 4)
        pygame.draw.line(surf, col, (w // 2 - 30, h // 2), (w // 2 + 30, h // 2), 3)
        pygame.draw.line(surf, col, (w // 2, h // 2 - 30), (w // 2, h // 2 + 30), 3)
        pygame.draw.circle(surf, col, (w // 2, h // 2), int(h * 0.3), 3)

        f = self.text("F", h * 0.3, col)
        surf.blit(f, (int(w * 0.08), int(h * 0.08)))
        for label, pos in (("上 TOP", "top"), ("下 BOTTOM", "bottom"), ("左 L", "left"), ("R 右", "right")):
            img = self.text(label, h * 0.07, col)
            iw, ih = img.get_size()
            xy = {"top": ((w - iw) // 2, 12), "bottom": ((w - iw) // 2, h - ih - 12),
                  "left": (16, (h - ih) // 2), "right": (w - iw - 16, (h - ih) // 2)}[pos]
            surf.blit(img, xy)
        hint = self.text("看到的 F 與文字是正的 = 鏡像方向正確；圓不是正圓 = 有變形", h * 0.045, col,
                         max_w=int(w * 0.6))
        surf.blit(hint, ((w - hint.get_width()) // 2, int(h * 0.88) - hint.get_height()))
        return surf

    def draw_overlay(self, surf, settings, extra=""):
        s = settings
        line = (f"鏡像[H] {'開' if s.mirror_h else '關'}  翻轉[V] {'開' if s.flip_v else '關'}  "
                f"縮放[+/-] {s.scale:.2f}  位移[方向鍵] ({s.offset_x},{s.offset_y})  "
                f"亮度[ [ ] ] {int(s.brightness * 100)}%  {extra}")
        img = self.text(line, self.h * 0.04, (255, 210, 0), max_w=self.w - 20)
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, self.w, img.get_height() + 12))
        surf.blit(img, (10, 6))


def compose(content, settings, out_size):
    """縮放 + 位移 + 亮度 + 鏡像，回傳可直接貼到螢幕的 Surface。"""
    frame = pygame.Surface(out_size)
    frame.fill((0, 0, 0))
    cw, ch = content.get_size()
    if abs(settings.scale - 1.0) > 1e-3:
        content = pygame.transform.smoothscale(content, (max(int(cw * settings.scale), 1),
                                                         max(int(ch * settings.scale), 1)))
    x = (out_size[0] - content.get_width()) // 2 + settings.offset_x
    y = (out_size[1] - content.get_height()) // 2 + settings.offset_y
    frame.blit(content, (x, y))
    if settings.brightness < 0.999:
        b = int(255 * settings.brightness)
        frame.fill((b, b, b), special_flags=pygame.BLEND_MULT)
    if settings.mirror_h or settings.flip_v:
        frame = pygame.transform.flip(frame, settings.mirror_h, settings.flip_v)
    return frame
