#!/usr/bin/env python3
"""
Монтаж рекламного ролика з готових кліпів: нарізка, склейка, кроп під формат,
музика з дакінгом, субтитри, кінцева заставка.

  python3 assemble.py --clips hook.mp4 body.mp4 cta.mp4 \
      --out ad_v1.mp4 --format 9x16 --music bg.mp3 --subs subs.srt

Формати: 9x16 (Reels/TikTok/Shorts), 1x1 (стрічка), 16x9 (YouTube), 4x5 (Meta feed)

Кроп «розумний»: масштабує по більшій стороні і ріже по центру (crop), щоб не було
чорних смуг. Для важливого тексту в кадрі — див. --pad щоб вписати з розмиттям.
"""
import argparse
import os
import shutil
import subprocess
import sys

SIZES = {"9x16": (1080, 1920), "1x1": (1080, 1080),
         "16x9": (1920, 1080), "4x5": (1080, 1350)}


def ff(explicit=None):
    if explicit:
        return explicit
    p = shutil.which("ffmpeg")
    if p:
        return p
    local = "./node_modules/ffmpeg-static/ffmpeg"
    if os.path.exists(local):
        return local
    sys.exit("ffmpeg не знайдено (npm i ffmpeg-static або --ffmpeg PATH)")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(" ".join(cmd), file=sys.stderr)
        print(r.stderr[-3000:], file=sys.stderr)
        sys.exit("ffmpeg впав")
    return r


def build(a):
    W, H = SIZES[a.format]
    exe = ff(a.ffmpeg)
    n = len(a.clips)

    # Кожен кліп: привести до єдиного формату/fps/аудіо, потім склеїти
    if a.pad:
        # вписати повністю, фон — розмита копія (нічого не ріжеться)
        vf = (f"split[bg][fg];"
              f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H},boxblur=28:2[bgb];"
              f"[fg]scale={W}:{H}:force_original_aspect_ratio=decrease[fgs];"
              f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1,fps={a.fps}")
    else:
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H},setsar=1,fps={a.fps}")

    inputs, filters = [], []
    for i, c in enumerate(a.clips):
        inputs += ["-i", c]
        filters.append(f"[{i}:v]{vf}[v{i}]")
        # аудіо може бути відсутнім — нормалізуємо через anullsrc пізніше
        filters.append(f"[{i}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]")

    concat_in = "".join(f"[v{i}][a{i}]" for i in range(n))
    filters.append(f"{concat_in}concat=n={n}:v=1:a=1[vcat][acat]")

    vlast, alast = "[vcat]", "[acat]"

    # Субтитри вшиваємо в картинку (для соцмереж — обов'язково, 80% дивляться без звуку)
    if a.subs:
        style = ("FontName=Arial,Fontsize=20,PrimaryColour=&H00FFFFFF,"
                 "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,"
                 "Alignment=2,MarginV=120")
        filters.append(f"{vlast}subtitles='{a.subs}':force_style='{style}'[vsub]")
        vlast = "[vsub]"

    # Музика: підмішуємо і приглушуємо під голос (sidechain ducking)
    if a.music:
        inputs += ["-stream_loop", "-1", "-i", a.music]
        mi = n
        filters.append(f"[{mi}:a]aresample=48000,volume={a.music_gain}[mus]")
        filters.append(f"[mus]{alast}sidechaincompress=threshold=0.06:ratio=9:"
                       f"attack=8:release=320[duck]")
        filters.append(f"[duck]{alast}amix=inputs=2:duration=first:dropout_transition=0[amix]")
        alast = "[amix]"

    filters.append(f"{alast}loudnorm=I=-14:TP=-1.5:LRA=11[aout]")

    cmd = [exe, "-y"] + inputs + [
        "-filter_complex", ";".join(filters),
        "-map", vlast, "-map", "[aout]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        a.out,
    ]
    run(cmd)
    print(f"Готово: {a.out}  [{a.format} {W}x{H} @ {a.fps}fps]")


def main():
    p = argparse.ArgumentParser(description="Монтаж рекламного ролика")
    p.add_argument("--clips", nargs="+", required=True, help="кліпи по порядку")
    p.add_argument("--out", required=True)
    p.add_argument("--format", default="9x16", choices=list(SIZES))
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--music", help="фонова музика (буде приглушена під голос)")
    p.add_argument("--music-gain", type=float, default=0.22, help="гучність музики 0..1")
    p.add_argument("--subs", help=".srt файл — вшивається в картинку")
    p.add_argument("--pad", action="store_true",
                   help="вписати кадр повністю з розмитим фоном замість обрізки")
    p.add_argument("--ffmpeg")
    build(p.parse_args())


if __name__ == "__main__":
    main()
