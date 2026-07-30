#!/usr/bin/env python3
"""
HTML/CSS-анімація -> MP4. Рендер повністю локальний, без AI-генераторів.

Так робляться: анімовані заголовки, hook-плашки, лого-стінгери, демо інтерфейсу,
підписи-субтитри, кінцеві заставки з CTA, motion-графіка для реклами.

Як працює: Playwright відкриває HTML, ставить час анімації вручну кадр за кадром
(детермінований рендер, не запис у реальному часі), ffmpeg збирає кадри в MP4.

  python3 render_motion.py scene.html out.mp4 --duration 5 --fps 30 --size 1080x1920

Вимоги: playwright (chromium вже є в середовищі), ffmpeg у PATH або --ffmpeg.
У HTML анімації мають бути звичайні CSS @keyframes — скрипт керує їх часом сам.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def find_ffmpeg(explicit=None):
    if explicit:
        return explicit
    for c in ("ffmpeg", "./node_modules/ffmpeg-static/ffmpeg"):
        p = shutil.which(c) if "/" not in c else (c if os.path.exists(c) else None)
        if p:
            return p
    sys.exit("ffmpeg не знайдено. Встанови: npm i ffmpeg-static, або передай --ffmpeg PATH")


def find_chromium(explicit=None):
    """Playwright-python може не мати власного браузера — беремо готовий з середовища."""
    if explicit:
        return explicit
    for c in ("/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
              "/opt/pw-browsers/chromium/chrome-linux/chrome"):
        if os.path.exists(c):
            return c
    for pat in sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"),
                      reverse=True):
        return str(pat)
    return None  # хай playwright сам шукає свій


def render(html, out, duration, fps, width, height, ffmpeg, keep,
           chromium=None, lossless=False):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Немає playwright. Встанови: pip install playwright")

    frames_dir = Path(tempfile.mkdtemp(prefix="motion_"))
    total = int(duration * fps)
    url = Path(html).resolve().as_uri()
    exe_path = find_chromium(chromium)

    with sync_playwright() as p:
        launch_kw = {"args": ["--force-color-profile=srgb", "--disable-lcd-text"]}
        if exe_path:
            launch_kw["executable_path"] = exe_path
        browser = p.chromium.launch(**launch_kw)
        page = browser.new_page(viewport={"width": width, "height": height},
                                device_scale_factor=1)
        page.goto(url, wait_until="networkidle")
        # Заморожуємо анімації: керуємо часом вручну -> детермінований результат
        page.evaluate("""() => {
            document.getAnimations().forEach(a => { a.pause(); });
        }""")
        ext = "png" if lossless else "jpg"
        shot_kw = {} if lossless else {"type": "jpeg", "quality": 92}
        for i in range(total):
            t_ms = (i / fps) * 1000
            page.evaluate("""(t) => {
                document.getAnimations().forEach(a => { a.currentTime = t; });
                if (window.onFrame) window.onFrame(t);
            }""", t_ms)
            page.screenshot(path=str(frames_dir / f"f{i:05d}.{ext}"), **shot_kw)
        browser.close()

    cmd = [
        ffmpeg, "-y", "-framerate", str(fps),
        "-i", str(frames_dir / f"f%05d.{ext}"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "18", "-preset", "slow",
        "-movflags", "+faststart",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2500:], file=sys.stderr)
        sys.exit("ffmpeg впав")

    if keep:
        print(f"Кадри збережено: {frames_dir}")
    else:
        shutil.rmtree(frames_dir, ignore_errors=True)
    print(f"Готово: {out}  ({total} кадрів, {duration}с, {width}x{height}, {fps}fps)")


def main():
    a = argparse.ArgumentParser(description="HTML-анімація -> MP4")
    a.add_argument("html")
    a.add_argument("out")
    a.add_argument("--duration", type=float, default=5.0, help="секунд")
    a.add_argument("--fps", type=int, default=30)
    a.add_argument("--size", default="1080x1920", help="ШхВ, напр. 1920x1080")
    a.add_argument("--ffmpeg", default=None)
    a.add_argument("--chromium", default=None, help="шлях до chrome, якщо автопошук не спрацював")
    a.add_argument("--keep-frames", action="store_true")
    a.add_argument("--lossless", action="store_true",
                   help="PNG-кадри замість JPEG: якісніше, але у ~3 рази повільніше")
    args = a.parse_args()

    w, _, h = args.size.partition("x")
    render(args.html, args.out, args.duration, args.fps,
           int(w), int(h), find_ffmpeg(args.ffmpeg), args.keep_frames,
           args.chromium, args.lossless)


if __name__ == "__main__":
    main()
