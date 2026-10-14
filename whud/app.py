"""主程式迴圈與按鍵控制。"""
import os
import time

import pygame

from . import config
from .fonts import find_cjk_font
from .render import Renderer, compose
from .sources import ARROWS, DemoSource

HELP = """按鍵（以反射後看到的方向為準）：
  H 左右鏡像   V 上下翻轉   方向鍵 移動畫面   +/- 縮放   [ ] 亮度
  G 校正格線   空白 暫停    N 下一個路口      C 切換顏色  S 儲存設定
  P 截圖       R 重設       Esc/Q 離開"""

COLORS = [(255, 255, 255), (0, 255, 120), (255, 190, 0), (0, 220, 255)]
OVERLAY_SECONDS = 3.0


class App:
    def __init__(self, settings, config_path=config.DEFAULT_PATH, screen_size=None):
        self.s = settings
        self.config_path = config_path
        self.screen = None
        self.size = screen_size or (settings.width, settings.height)
        font_path = find_cjk_font(settings.font_path)
        if font_path is None:
            print("[whud] 找不到中文字型，中文會變成方框。請安裝：sudo apt install fonts-noto-cjk")
        else:
            print(f"[whud] 字型：{font_path}")
        self.renderer = Renderer(self.size, font_path)
        self.source = DemoSource(speed_kmh=settings.demo_speed_kmh)
        self.calibration = False
        self.overlay_until = 0.0
        self.message = ""

    # ---------- 顯示 ----------
    def open_display(self):
        pygame.display.init()
        pygame.font.init()
        if self.s.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            pygame.mouse.set_visible(False)
        else:
            self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("W-HUD")
        self.size = self.screen.get_size()
        self.renderer = Renderer(self.size, self.renderer.font_path)
        print(f"[whud] 解析度 {self.size[0]}x{self.size[1]}")

    def render_frame(self, state):
        if self.calibration:
            content = self.renderer.draw_calibration(self.s)
        else:
            content = self.renderer.draw_hud(state, self.s)
        frame = compose(content, self.s, self.size)
        if time.monotonic() < self.overlay_until:
            ov = pygame.Surface(self.size, pygame.SRCALPHA)
            self.renderer.draw_overlay(ov, self.s, self.message)
            frame.blit(pygame.transform.flip(ov, self.s.mirror_h, self.s.flip_v), (0, 0))
        return frame

    # ---------- 按鍵 ----------
    def notify(self, msg=""):
        self.message = msg
        self.overlay_until = time.monotonic() + OVERLAY_SECONDS

    def handle_key(self, key, mod=0):
        s = self.s
        step = 20 if mod & pygame.KMOD_SHIFT else 5
        if key in (pygame.K_ESCAPE, pygame.K_q):
            return False
        elif key == pygame.K_h:
            s.mirror_h = not s.mirror_h
        elif key == pygame.K_v:
            s.flip_v = not s.flip_v
        elif key == pygame.K_LEFT:
            s.offset_x -= step
        elif key == pygame.K_RIGHT:
            s.offset_x += step
        elif key == pygame.K_UP:
            s.offset_y -= step
        elif key == pygame.K_DOWN:
            s.offset_y += step
        elif key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
            s.scale += 0.05
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            s.scale -= 0.05
        elif key == pygame.K_RIGHTBRACKET:
            s.brightness += 0.1
        elif key == pygame.K_LEFTBRACKET:
            s.brightness -= 0.1
        elif key == pygame.K_g:
            self.calibration = not self.calibration
        elif key == pygame.K_SPACE:
            self.source.paused = not self.source.paused
            self.notify("暫停" if self.source.paused else "播放")
            return True
        elif key == pygame.K_n:
            self.source.next_step()
        elif key == pygame.K_c:
            i = COLORS.index(tuple(s.color)) if tuple(s.color) in COLORS else -1
            s.color = COLORS[(i + 1) % len(COLORS)]
        elif key == pygame.K_r:
            keep = (s.fullscreen, s.width, s.height, s.font_path)
            self.s = s = config.Settings()
            s.fullscreen, s.width, s.height, s.font_path = keep
            self.notify("已重設（按 S 才會存檔）")
            return True
        elif key == pygame.K_s:
            config.save(s, self.config_path)
            self.notify("設定已儲存")
            return True
        elif key == pygame.K_p:
            name = time.strftime("whud_%Y%m%d_%H%M%S.png")
            pygame.image.save(self.screen, name)
            self.notify(f"截圖 {name}")
            return True
        else:
            return True
        s.clamp()
        self.notify()
        return True

    # ---------- 主迴圈 ----------
    def run(self):
        self.open_display()
        print(HELP)
        self.notify("按 G 校正，S 儲存")
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.tick(self.s.fps) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    running = self.handle_key(ev.key, ev.mod) and running
            state = self.source.update(dt)
            self.screen.blit(self.render_frame(state), (0, 0))
            pygame.display.flip()
        pygame.quit()


def render_snapshot(settings, out_path, size, calibration=False, arrow=None, seconds=0.0):
    """不開視窗直接輸出一張畫面（開發 / 測試用）。"""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.display.init()
    pygame.font.init()
    settings.fullscreen = False
    app = App(settings, screen_size=size)
    app.calibration = calibration
    state = app.source.update(seconds)
    if arrow:
        state.arrow = arrow
    pygame.image.save(app.render_frame(state), out_path)
    pygame.quit()
    return out_path


__all__ = ["App", "render_snapshot", "ARROWS"]
