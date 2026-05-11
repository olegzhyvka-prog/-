from PIL import Image, ImageDraw, ImageFont
import math, os

OUT = "/home/user/-/symplexy-carousel/slides"
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1080

# ── Colors ──────────────────────────────────────────────
BG       = (8,   8,  26)
BG2      = (13,  13, 43)
WHITE    = (255, 255, 255)
DIM      = (180, 180, 200)
VERY_DIM = (90,  90, 110)
PURPLE   = (167, 139, 250)
BLUE     = (96,  165, 250)
PINK     = (244, 114, 182)
CYAN     = (34,  211, 238)
GREEN    = (52,  211, 153)

TOOL_COLORS = [PURPLE, BLUE, PINK, CYAN, GREEN]

# ── Fonts ────────────────────────────────────────────────
def try_fonts(sizes):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    regular_paths = [p.replace("Bold","").replace("-B.ttf",".ttf") for p in paths]
    fonts = {}
    for name, size in sizes.items():
        loaded = False
        for p in paths:
            if os.path.exists(p):
                try:
                    fonts[name] = ImageFont.truetype(p, size)
                    loaded = True
                    break
                except: pass
        if not loaded:
            fonts[name] = ImageFont.load_default()
    return fonts

F = try_fonts({
    "hero":    96,
    "hero_sm": 72,
    "h1":      60,
    "h2":      48,
    "h3":      38,
    "body":    30,
    "body_sm": 24,
    "tag":     20,
    "num":     160,
    "num_sm":  100,
})

# ── Helpers ──────────────────────────────────────────────
def gradient_bg(draw, w=W, h=H):
    for y in range(h):
        t = y / h
        r = int(BG[0] + (BG2[0]-BG[0])*t)
        g = int(BG[1] + (BG2[1]-BG[1])*t)
        b = int(BG[2] + (BG2[2]-BG[2])*t)
        draw.line([(0,y),(w,y)], fill=(r,g,b))

def glow_circle(img, cx, cy, radius, color, alpha=40):
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    steps = 10
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(alpha * (1 - i/steps))
        d.ellipse([cx-r, cy-r, cx+r, cy+r],
                  fill=(color[0], color[1], color[2], a))
    img.paste(overlay, mask=overlay)

def grid_overlay(img):
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    step = 60
    for x in range(0, W, step):
        d.line([(x,0),(x,H)], fill=(100,80,255,8))
    for y in range(0, H, step):
        d.line([(0,y),(W,y)], fill=(100,80,255,8))
    img.paste(overlay, mask=overlay)

def text_centered(draw, y, text, font, color, w=W):
    bbox = draw.textbbox((0,0), text, font=font)
    tw = bbox[2]-bbox[0]
    x = (w - tw) // 2
    draw.text((x, y), text, font=font, fill=color)
    return bbox[3]-bbox[1]

def draw_logo(draw, x=60, y=48):
    """Draw star logo + text"""
    s = 20
    cx, cy = x+s, y+s
    pts = []
    for i in range(5):
        outer_angle = math.radians(-90 + i*72)
        inner_angle = math.radians(-90 + i*72 + 36)
        pts.append((cx + s*math.cos(outer_angle), cy + s*math.sin(outer_angle)))
        pts.append((cx + s*0.45*math.cos(inner_angle), cy + s*0.45*math.sin(inner_angle)))
    draw.polygon(pts, fill=PURPLE)
    draw.text((x + s*2 + 12, y + 6), "Symplexy", font=F["body_sm"], fill=PURPLE)

def draw_tag(draw, text="@_symplexy"):
    bbox = draw.textbbox((0,0), text, font=F["tag"])
    tw = bbox[2]-bbox[0]
    draw.text((W-60-tw, H-54), text, font=F["tag"], fill=VERY_DIM)

def pill(draw, x, y, text, color, w_pad=28, h_pad=14):
    bbox = draw.textbbox((0,0), text, font=F["body"])
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    pw, ph = tw + w_pad*2, th + h_pad*2
    r = ph // 2
    # filled background in accent color, white text for contrast
    draw.rounded_rectangle([x, y, x+pw, y+ph], radius=r,
                            fill=color, outline=(255,255,255,60), width=1)
    draw.text((x+w_pad, y+h_pad), text, font=F["body"], fill=(255,255,255))
    return pw, ph

def progress_dots(draw, active, total=7):
    dot_w, dot_h = 8, 8
    active_w = 24
    total_w = (total-1)*(dot_w+8) + active_w
    sx = 60
    y = H - 54 + (dot_h//2)
    x = sx
    for i in range(total):
        is_active = (i == active)
        w = active_w if is_active else dot_w
        r = 4 if is_active else dot_h//2
        col = PURPLE if is_active else (255,255,255,40)
        if isinstance(col, tuple) and len(col)==4:
            ov = Image.new("RGBA", (w, dot_h), (0,0,0,0))
            dv = ImageDraw.Draw(ov)
            dv.rounded_rectangle([0,0,w-1,dot_h-1], radius=r, fill=col)
        else:
            draw.rounded_rectangle([x, y-dot_h//2, x+w, y+dot_h//2], radius=r, fill=col)
        x += w + 8

def divider_line(draw, y, x1=60, x2=None):
    if x2 is None: x2 = W - 60
    mid = (x1+x2)//2
    draw.line([(x1,y),(mid,y)], fill=(*PURPLE,120), width=2)
    draw.line([(mid,y),(x2,y)], fill=(*BLUE,60), width=2)

# ══════════════════════════════════════════════════════════
# SLIDE 1 — Cover
# ══════════════════════════════════════════════════════════
img = Image.new("RGB", (W,H), BG)
d = ImageDraw.Draw(img)
gradient_bg(d)
grid_overlay(img)
glow_circle(img, W+100, -100, 700, PURPLE, 50)
glow_circle(img, -100, H+100, 500, BLUE, 40)

draw_logo(d)
draw_tag(d)

# Big ghost "5"
ghost5 = str(5)
bbox = d.textbbox((0,0), ghost5, font=F["num"])
tw = bbox[2]-bbox[0]
d.text(((W-tw)//2, 280), ghost5, font=F["num"], fill=(167,139,250,18))

# Eyebrow
ey_text = "⎯  ШІ для маркетологів  ⎯"
text_centered(d, 230, ey_text, F["tag"], PURPLE)

# Headline line 1
line1 = "5 ШІ-інструментів"
bbox = d.textbbox((0,0), line1, font=F["hero"])
tw = bbox[2]-bbox[0]
d.text(((W-tw)//2, 310), line1, font=F["hero"], fill=PURPLE)

# Headline line 2
line2 = "які замінять"
text_centered(d, 420, line2, F["hero_sm"], WHITE)

# Headline line 3
line3 = "маркетинговий відділ"
text_centered(d, 510, line3, F["h1"], WHITE)

# Subtitle
text_centered(d, 632, "Перевірено. Без зайвих слів.", F["body"], VERY_DIM)

# Chips
chips = ["Тексти", "Дизайн", "Контент", "Аналітика", "Email"]
chip_y = 700
total_w = 0
gaps = 14
rendered = []
for c in chips:
    bb = d.textbbox((0,0), c, font=F["body_sm"])
    cw = bb[2]-bb[0]+36
    rendered.append((c, cw))
    total_w += cw + gaps
total_w -= gaps
sx = (W - total_w) // 2
for c, cw in rendered:
    d.rounded_rectangle([sx, chip_y, sx+cw, chip_y+38], radius=19,
                        fill=(167,139,250,20), outline=(167,139,250,80), width=1)
    bb = d.textbbox((0,0), c, font=F["body_sm"])
    tw = bb[2]-bb[0]
    d.text((sx+(cw-tw)//2, chip_y+7), c, font=F["body_sm"], fill=PURPLE)
    sx += cw + gaps

progress_dots(d, 0)
img.save(f"{OUT}/slide_01_cover.png")
print("✓ Slide 1")

# ══════════════════════════════════════════════════════════
# SLIDES 2–6 — Tool slides
# ══════════════════════════════════════════════════════════
tools = [
    ("ChatGPT / Claude",  "Генерація контенту",  "AI", PURPLE, "Пише тексти, email-розсилки\nта скрипти за хвилини",         "  Економить до 8 год/тиждень"),
    ("Canva AI",          "Дизайн та візуали",   "CA", BLUE,   "Генерує банери та рекламні\nкреативи без дизайнера",          "  Дизайн за 2 хвилини"),
    ("Lately AI",         "Контент-планування",  "LA", PINK,   "Аналізує аудиторію та автоматично\nгенерує контент-план на місяць", "  Забудь про «що постити»"),
    ("Hotjar AI",         "Аналітика поведінки", "HJ", CYAN,   "Показує що заважає клієнтам\nкупувати на твоєму сайті",       "  Знайди слабкі місця"),
    ("Klaviyo AI",        "Email-маркетинг",     "KL", GREEN,  "Email-маркетинг що сегментує базу\nі продає автоматично",       "  Конверсія без ручної роботи"),
]

for idx, (name, category, icon, color, desc, stat) in enumerate(tools):
    num = idx + 1
    img = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(img)
    gradient_bg(d)
    grid_overlay(img)
    glow_circle(img, W+150, -150, 700, color, 35)
    glow_circle(img, -100, H+100, 400, BLUE, 25)

    draw_logo(d)
    draw_tag(d)

    # Ghost number
    num_str = f"0{num}"
    bb = d.textbbox((0,0), num_str, font=F["num"])
    nw = bb[2]-bb[0]
    d.text((W-80-nw, 60), num_str, font=F["num"], fill=(*color, 25))

    # Icon box — draw colored rounded rect with 2-letter abbreviation
    box_x, box_y, box_s = 60, 130, 90
    d.rounded_rectangle([box_x, box_y, box_x+box_s, box_y+box_s],
                        radius=20, fill=(*color,25), outline=(*color,80), width=2)
    bb = d.textbbox((0,0), icon, font=F["h3"])
    iw, ih = bb[2]-bb[0], bb[3]-bb[1]
    d.text((box_x+(box_s-iw)//2, box_y+(box_s-ih)//2), icon, font=F["h3"], fill=color)

    # Tool name
    d.text((60, 250), name, font=F["h1"], fill=WHITE)

    # Category
    d.text((60, 332), category, font=F["body_sm"], fill=color)

    # Divider
    divider_line(d, 390)

    # Description
    desc_y = 420
    for line in desc.split("\n"):
        d.text((60, desc_y), line, font=F["h2"], fill=DIM)
        bb = d.textbbox((0,0), line, font=F["h2"])
        desc_y += bb[3]-bb[1] + 12

    # Stat badge
    badge_y = desc_y + 48
    pw, ph = pill(d, 60, badge_y, stat, color, w_pad=32, h_pad=16)

    progress_dots(d, num)
    img.save(f"{OUT}/slide_0{num+1}_tool{num:02d}.png")
    print(f"✓ Slide {num+1}")

# ══════════════════════════════════════════════════════════
# SLIDE 7 — CTA
# ══════════════════════════════════════════════════════════
img = Image.new("RGB", (W,H), BG)
d = ImageDraw.Draw(img)
gradient_bg(d)
grid_overlay(img)
glow_circle(img, W//2, H//2, 600, PURPLE, 45)
glow_circle(img, W//2, H//2, 400, BLUE, 30)
glow_circle(img, W//2, H//2, 200, PINK, 20)

draw_logo(d)

# Star logo centered
star_cx, star_cy, star_r = W//2, 240, 70
pts = []
for i in range(5):
    oa = math.radians(-90 + i*72)
    ia = math.radians(-90 + i*72 + 36)
    pts.append((star_cx + star_r*math.cos(oa), star_cy + star_r*math.sin(oa)))
    pts.append((star_cx + star_r*0.42*math.cos(ia), star_cy + star_r*0.42*math.sin(ia)))
d.polygon(pts, fill=PURPLE)

# Eyebrow
text_centered(d, 358, "— Готовий почати? —", F["tag"], PURPLE)

# CTA headline
line_a = "Всі ці інструменти"
text_centered(d, 408, line_a, F["hero_sm"], WHITE)

symplexy_text = "на Symplexy"
bb = d.textbbox((0,0), symplexy_text, font=F["hero_sm"])
tw = bb[2]-bb[0]
sx = (W-tw)//2
# gradient-ish: draw in purple
d.text((sx, 500), symplexy_text, font=F["hero_sm"], fill=PURPLE)

# Subtitle
text_centered(d, 618, "Тестуй безкоштовно. Без кредитки.", F["body"], VERY_DIM)

# CTA button
btn_text = "  Спробувати безкоштовно"
bb = d.textbbox((0,0), btn_text, font=F["h3"])
bw = bb[2]-bb[0] + 80
bh = bb[3]-bb[1] + 40
bx = (W-bw)//2
by = 700
d.rounded_rectangle([bx, by, bx+bw, by+bh], radius=bh//2,
                    fill=(100, 50, 200), outline=(167,139,250,180), width=2)
tw = bb[2]-bb[0]
d.text(((W-tw)//2, by+20), btn_text, font=F["h3"], fill=WHITE)

# Link hint
hint = "👆  Посилання в шапці профілю"
text_centered(d, by+bh+28, hint, F["body_sm"], VERY_DIM)

progress_dots(d, 6)
img.save(f"{OUT}/slide_07_cta.png")
print("✓ Slide 7")
print(f"\nDone! All slides saved to {OUT}/")
