#!/usr/bin/env python3
"""
Дошка референсів: 8 варіантів героя лендінга в різних візуальних мовах,
одним зображенням. Власник дивиться і називає номер — далі верстаємо тільки його.

  python3 render_board.py --headline "Перевір ідею за тиждень" \
      --sub "Досьє, лендінг, трафік, вирок" --cta "Почати" --out board.png

Напрями і їх логіка — references/directions.md.
Сім із восьми світлі: темний фон тут не дефолт, а свідомий вибір під нічний продукт.
"""
import argparse, html, os, shutil, subprocess, sys, tempfile
from pathlib import Path

from directions import D


def tile(d, head, sub, cta):
    e, acc, fg = d["extra"], d["acc"], d["fg"]
    btn_css = {
        "solid":   f"background:{acc};color:{d['bg']};border:1px solid {acc}",
        "outline": f"background:transparent;color:{acc};border:1px solid {acc}",
        "dashed":  f"background:transparent;color:{acc};border:1.5px dashed {acc}",
    }[d["btn"]]

    if e == "bento":
        cells = [("Попит", "2 400/міс"), ("CAC", "$58"), ("Вирок", "GO")]
        art = (f'<div style="display:grid;grid-template-columns:2fr 1fr;grid-template-rows:40px 40px;'
               f'gap:7px;margin-top:14px">'
               + "".join(f'<div style="background:#fff;border:1px solid {d["line"]};border-radius:12px;'
                         f'padding:7px 9px;{"grid-row:span 2;display:flex;flex-direction:column;justify-content:center" if i==2 else ""}">'
                         f'<div style="font-size:8px;letter-spacing:.1em;color:{d["mut"]};text-transform:uppercase">{t}</div>'
                         f'<div style="font-size:{"13px" if i==2 else "12px"};font-weight:700;color:{acc if i==2 else fg};'
                         f'margin-top:2px">{v}</div></div>'
                         for i, (t, v) in enumerate(cells)) + "</div>")
    elif e == "mono":
        art = (f'<div style="margin-top:14px;border:1px solid {d["line"]};border-radius:{d["r"]};'
               f'padding:10px 12px;font-family:ui-monospace,monospace;font-size:9.5px;'
               f'line-height:1.8;color:{d["mut"]}">'
               f'<span style="color:{acc}">$</span> check --idea<br>'
               f'&nbsp;&nbsp;попит &nbsp;<span style="color:{acc}">ok</span> &nbsp;2 400/міс<br>'
               f'&nbsp;&nbsp;CAC &nbsp;&nbsp;&nbsp;$58 &nbsp;· стеля $174</div>')
    elif e == "poster":
        art = (f'<div style="margin-top:16px;height:40px;background:{fg};border-radius:{d["r"]};'
               f'display:flex;align-items:center;justify-content:center;gap:14px;color:{d["bg"]};'
               f'font-weight:800;font-size:11.5px;letter-spacing:.05em">'
               f'<span>7 ДНІВ</span><span style="opacity:.45">·</span><span>$300</span>'
               f'<span style="opacity:.45">·</span><span>1 ВИРОК</span></div>')
    elif e == "shot":
        art = (f'<div style="margin-top:14px;border:1px solid {d["line"]};border-radius:{d["r"]};'
               f'background:#F7FAFF;padding:9px;box-shadow:0 8px 20px -10px rgba(79,125,243,.35)">'
               f'<div style="height:7px;width:44%;background:{acc};opacity:.35;border-radius:4px"></div>'
               f'<div style="height:7px;width:74%;background:{d["line"]};border-radius:4px;margin-top:6px"></div>'
               f'<div style="height:7px;width:60%;background:{d["line"]};border-radius:4px;margin-top:6px"></div>'
               f'<div style="height:22px;width:34%;background:{acc};border-radius:6px;margin-top:10px"></div></div>')
    elif e == "paper":
        art = (f'<div style="margin-top:14px;border:1.5px dashed {d["line"]};padding:11px 13px;'
               f'font-size:10.5px;line-height:1.65;color:{d["mut"]}">'
               f'«Найдорожча помилка — гарний лендінг для гіпотези,<br>'
               f'яку можна було вбити за годину аналізу.»</div>')
    elif e == "rule":
        art = (f'<div style="margin-top:16px;border-top:1px solid {d["line"]};padding-top:11px;'
               f'display:flex;gap:22px;font-size:10px;color:{d["mut"]}">'
               f'<span><b style="color:{fg};font-size:15px">7</b><br>днів</span>'
               f'<span><b style="color:{fg};font-size:15px">$300</b><br>бюджет</span>'
               f'<span><b style="color:{fg};font-size:15px">1</b><br>вирок</span></div>')
    else:  # pad
        art = (f'<div style="margin-top:14px;background:#F2EDE4;border-radius:{d["r"]};'
               f'padding:13px 15px;font-size:10.5px;color:{d["mut"]};line-height:1.6">'
               f'Досьє з числами · Лендінг · Трафік · Вирок</div>')

    serif = "serif" in d["hf"]
    return f'''
<div class="tile">
  <div class="cap"><b>{d["n"]}. {html.escape(d["name"])}</b><span>{html.escape(d["note"])}</span></div>
  <div class="hero" style="background:{d['bg']};color:{fg};font-family:{d['hf']}">
    <div class="brandline" style="color:{d['mut']}">
      <span style="width:7px;height:7px;border-radius:50%;background:{acc};display:inline-block"></span>
      PRODUCT
    </div>
    <h3 style="font-size:{'21px' if serif else '19px'};line-height:1.1;
        letter-spacing:{'-.005em' if serif else '-.022em'};
        font-weight:{'500' if serif else '750'};margin:9px 0 0">{html.escape(head)}</h3>
    <p style="color:{d['mut']};font-size:11.5px;line-height:1.5;margin:8px 0 0">{html.escape(sub)}</p>
    <div style="margin-top:13px"><span style="display:inline-block;padding:8px 16px;
        border-radius:{d['r']};font-size:11px;font-weight:650;{btn_css}">{html.escape(cta)}</span></div>
    {art}
  </div>
</div>'''


def build_html(head, sub, cta, product):
    tiles = "".join(tile(d, head, sub, cta) for d in D)
    return f'''<!doctype html><html lang="uk"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}
body{{background:#EDEEF0;font-family:ui-sans-serif,system-ui,sans-serif;padding:30px 30px 34px}}
h1{{font-size:20px;letter-spacing:-.02em;color:#14161A}}
.lede{{color:#5C6470;font-size:12.5px;margin-top:5px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:22px}}
.tile{{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.07),0 8px 20px -12px rgba(0,0,0,.22)}}
.cap{{padding:9px 12px;border-bottom:1px solid #E7E8EB;display:flex;flex-direction:column;gap:1px}}
.cap b{{font-size:12px;color:#14161A}}
.cap span{{font-size:9.5px;color:#79808B;line-height:1.35}}
.hero{{padding:16px 16px 18px;min-height:236px}}
.brandline{{font-size:8.5px;letter-spacing:.18em;font-weight:700;display:flex;align-items:center;gap:6px}}
.foot{{margin-top:20px;color:#5C6470;font-size:11.5px;line-height:1.6}}
</style></head><body>
<h1>Дошка референсів — {html.escape(product)}</h1>
<div class="lede">Вісім візуальних мов. Назвіть номер — і лендінг буде зроблено саме в ній.
Можна уточнити: «3, але акцент теплий» або «1 і 7 змішати».</div>
<div class="grid">{tiles}</div>
<div class="foot">
Сім із восьми напрямів світлі. Темний (8) — тільки для нічних продуктів: dev-tools, монтаж, трейдинг.<br>
Не подобається жоден — киньте посилання чи скріншот сайту, який подобається,
і напрям буде побудований з нього.
</div></body></html>'''


def main():
    a = argparse.ArgumentParser(description="Дошка референсів лендінга")
    a.add_argument("--headline", default="Перевір ідею за тиждень")
    a.add_argument("--sub", default="Досьє з числами, лендінг, трафік і чесний вирок.")
    a.add_argument("--cta", default="Почати")
    a.add_argument("--product", default="продукт")
    a.add_argument("--out", default="board.png")
    a.add_argument("--chromium", default=None)
    args = a.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="board_")) / "board.html"
    tmp.write_text(build_html(args.headline, args.sub, args.cta, args.product), encoding="utf-8")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(f"HTML готовий: {tmp}\n(playwright не встановлено — відкрий вручну)")
        return

    exe = args.chromium
    if not exe:
        for c in Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"):
            exe = str(c); break
    with sync_playwright() as p:
        kw = {"executable_path": exe} if exe else {}
        b = p.chromium.launch(**kw)
        pg = b.new_page(viewport={"width": 1500, "height": 700}, device_scale_factor=2)
        pg.goto(tmp.as_uri(), wait_until="networkidle")
        pg.screenshot(path=args.out, full_page=True)
        b.close()
    print(f"Дошка готова: {args.out}")
    print("Покажи власнику і чекай на номер. Повний лендінг — тільки після вибору.")


if __name__ == "__main__":
    main()
