import json
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from whud import config
from whud.render import ARROW_PATHS, Renderer, compose
from whud.sources import DemoSource, HudState, format_distance

SIZE = (200, 100)


@pytest.fixture(autouse=True)
def _pg():
    pygame.display.init()
    pygame.font.init()
    yield
    pygame.quit()


def marker():
    s = pygame.Surface(SIZE)
    s.fill((0, 0, 0))
    s.set_at((10, 20), (255, 255, 255))
    return s


def lit(surf):
    return [(x, y) for x in range(surf.get_width()) for y in range(surf.get_height())
            if surf.get_at((x, y))[0] > 0]


def settings(**kw):
    s = config.Settings(mirror_h=False)
    for k, v in kw.items():
        setattr(s, k, v)
    return s


def test_no_transform_keeps_pixel():
    assert lit(compose(marker(), settings(), SIZE)) == [(10, 20)]


def test_mirror_h():
    assert lit(compose(marker(), settings(mirror_h=True), SIZE)) == [(SIZE[0] - 11, 20)]


def test_flip_v():
    assert lit(compose(marker(), settings(flip_v=True), SIZE)) == [(10, SIZE[1] - 21)]


def test_offset_is_in_reflected_coordinates():
    # 鏡像開啟時往「右」移，在反射畫面中也要往右 → 螢幕上的像素往左
    out = compose(marker(), settings(mirror_h=True, offset_x=5), SIZE)
    assert lit(out) == [(SIZE[0] - 16, 20)]


def test_brightness_dims():
    out = compose(marker(), settings(brightness=0.5), SIZE)
    assert 120 <= out.get_at((10, 20))[0] <= 135


def test_scale_shrinks_about_center():
    s = pygame.Surface(SIZE)
    s.fill((255, 255, 255))
    out = compose(s, settings(scale=0.5), SIZE)
    assert out.get_at((0, 0))[0] == 0
    assert out.get_at((SIZE[0] // 2, SIZE[1] // 2))[0] == 255


@pytest.mark.parametrize("m,expected", [
    (1234, ("1.2", "km")), (356, ("360", "m")), (99.6, ("99", "m")), (0, ("0", "m")),
])
def test_format_distance(m, expected):
    assert format_distance(m) == expected


def test_demo_counts_down_and_advances():
    route = [("right", 100, "A路"), ("left", 50, "B路")]
    src = DemoSource(speed_kmh=36, route=route, lyrics=["x", "y"], lyric_period_s=4)  # 10 m/s
    st = src.update(5)
    assert st.road == "A路" and st.distance_m == pytest.approx(50)
    assert st.lyric == "y"
    st = src.update(6)
    assert st.road == "B路" and st.arrow == "left"


def test_demo_pause():
    src = DemoSource()
    d0 = src.update(0).distance_m
    src.paused = True
    assert src.update(10).distance_m == d0


def test_config_roundtrip_and_unknown_keys(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"scale": 9, "brightness": 0.5, "bogus": 1}))
    s = config.load(str(p))
    assert s.scale == 2.0 and s.brightness == 0.5 and s.mirror_h is True
    s.offset_x = 42
    config.save(s, str(p))
    assert config.load(str(p)).offset_x == 42


def test_missing_config_gives_defaults(tmp_path):
    assert config.load(str(tmp_path / "none.json")) == config.Settings()


@pytest.mark.parametrize("arrow", sorted(ARROW_PATHS))
def test_every_arrow_renders(arrow):
    r = Renderer((320, 180), font_path=None)
    surf = r.draw_hud(HudState(arrow=arrow, distance_m=350, road="路", lyric="歌"), config.Settings())
    assert len(lit(surf)) > 500


def test_calibration_renders():
    r = Renderer((320, 180), font_path=None)
    assert len(lit(r.draw_calibration(config.Settings()))) > 500


def test_keys_adjust_and_save(tmp_path):
    from whud.app import App
    p = str(tmp_path / "c.json")
    app = App(config.Settings(), config_path=p, screen_size=SIZE)
    app.handle_key(pygame.K_h)
    app.handle_key(pygame.K_RIGHT, pygame.KMOD_SHIFT)
    for _ in range(20):
        app.handle_key(pygame.K_RIGHTBRACKET)
    app.handle_key(pygame.K_s)
    s = config.load(p)
    assert s.mirror_h is False and s.offset_x == 20 and s.brightness == 1.0
    assert app.handle_key(pygame.K_ESCAPE) is False
