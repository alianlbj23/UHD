import argparse

from . import config
from .app import App, render_snapshot
from .sources import ARROWS


def main():
    p = argparse.ArgumentParser(prog="whud", description="DIY W-HUD 簡易測試版")
    p.add_argument("--config", default=config.DEFAULT_PATH, help="設定檔路徑")
    p.add_argument("--windowed", action="store_true", help="視窗模式（在電腦上預覽用）")
    p.add_argument("--no-mirror", action="store_true", help="暫時關閉鏡像（直接看螢幕時用）")
    p.add_argument("--snapshot", metavar="PNG", help="不開視窗，輸出一張畫面後結束")
    p.add_argument("--size", default="1024x600", help="--snapshot / --windowed 的解析度")
    p.add_argument("--calibration", action="store_true", help="--snapshot 輸出校正畫面")
    p.add_argument("--arrow", choices=ARROWS, help="--snapshot 指定箭頭")
    args = p.parse_args()

    s = config.load(args.config)
    if args.no_mirror:
        s.mirror_h = False
    w, h = (int(v) for v in args.size.lower().split("x"))
    if args.snapshot:
        print(render_snapshot(s, args.snapshot, (w, h), args.calibration, args.arrow))
        return
    if args.windowed:
        s.fullscreen, s.width, s.height = False, w, h
    App(s, args.config).run()


if __name__ == "__main__":
    main()
