#!/usr/bin/env python3
"""
Генератор лендінга за логікою Manus / Kimi: шаблон структури + контент-модель + напрям.

Чому так, а не «згенеруй сайт з нуля»: коли структура вигадується щоразу заново,
якість стрибає. Коли структура фіксована і перевірена, а змінюється тільки
контент і візуальна мова — результат передбачуваний. Саме на цьому тримаються
Manus і Kimi: користувач обирає шаблон, система підганяє під нього контент.

  python3 render_site.py content.json --direction 2 --template saas --out index.html
  python3 render_site.py --schema           # показати порожню контент-модель

Напрями — directions.py (ті самі, що на дошці референсів, тому прев'ю = результат).
"""
import argparse, html, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from directions import by_number

TEMPLATES = {
    "saas":    ["hero", "proof", "problem", "features", "how", "pricing", "faq", "final"],
    "service": ["hero", "proof", "problem", "how", "features", "pricing", "faq", "final"],
    "waitlist":["hero", "problem", "features", "how", "faq", "final"],
    "product": ["hero", "features", "how", "proof", "pricing", "final"],
}

SCHEMA = {
    "product": "Назва продукту",
    "hero": {"h1": "", "sub": "", "cta": "", "cta2": "", "note": ""},
    "proof": ["рядок довіри 1", "рядок 2", "рядок 3"],
    "problem": {"title": "", "items": [{"t": "", "d": ""}]},
    "features": {"title": "", "lede": "", "items": [{"t": "", "d": "", "stat": ""}]},
    "how": {"title": "", "lede": "", "steps": [{"t": "", "d": "", "meta": ""}]},
    "pricing": {"title": "", "lede": "", "plans": [
        {"name": "", "price": "", "unit": "", "features": [""], "cta": "", "featured": False}]},
    "faq": [{"q": "", "a": ""}],
    "final": {"h2": "", "sub": "", "cta": ""},
    "footer": "",
}

E = html.escape


def css(d):
    serif = "serif" in d["hf"]
    return f""":root{{
  --bg:{d['bg']};--fg:{d['fg']};--mut:{d['mut']};--acc:{d['acc']};--line:{d['line']};
  --r:{d['r']};--font:{d['hf']};
  --sec:clamp(64px,9vw,124px);--wrap:1120px;
  --e:cubic-bezier(.16,1,.3,1);
}}
*,*::before,*::after{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:var(--font);
  line-height:1.62;-webkit-font-smoothing:antialiased;overflow-x:hidden}}
h1,h2,h3{{margin:0;line-height:{'1.14' if serif else '1.08'};
  letter-spacing:{'-.005em' if serif else '-.028em'};
  font-weight:{'500' if serif else '750'}}}
h1{{font-size:clamp(2.3rem,5.4vw,{'4.2rem' if serif else '3.9rem'});max-width:16ch}}
h2{{font-size:clamp(1.7rem,3.4vw,2.7rem);max-width:19ch}}
h3{{font-size:1.12rem;letter-spacing:-.015em}}
p{{margin:0;max-width:62ch}}
a{{color:inherit;text-decoration:none}}
.wrap{{width:min(100% - 40px,var(--wrap));margin-inline:auto}}
.sec{{padding-block:var(--sec)}}
.mut{{color:var(--mut)}}
.eyebrow{{font-size:11.5px;letter-spacing:.2em;text-transform:uppercase;
  font-weight:700;color:var(--acc);margin-bottom:14px}}
.lede{{margin-top:16px;font-size:1.06rem;color:var(--mut)}}
:focus-visible{{outline:2px solid var(--acc);outline-offset:3px}}

nav{{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--bg) 86%,transparent);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}}
.nav{{display:flex;align-items:center;justify-content:space-between;height:64px}}
.logo{{display:flex;align-items:center;gap:9px;font-weight:700;letter-spacing:-.02em}}
.logo i{{width:9px;height:9px;border-radius:50%;background:var(--acc);display:block}}

.btn{{display:inline-flex;align-items:center;gap:9px;font:inherit;font-weight:650;
  font-size:15px;padding:13px 26px;border-radius:var(--r);cursor:pointer;
  background:var(--acc);color:var(--bg);border:1px solid var(--acc);
  transition:transform .2s var(--e),opacity .2s}}
.btn:hover{{transform:translateY(-1px);opacity:.92}}
.btn-2{{background:transparent;color:var(--fg);border-color:var(--line)}}
.btn-lg{{padding:16px 32px;font-size:16px}}

.hero{{padding-top:clamp(56px,8vw,96px);padding-bottom:var(--sec);position:relative}}
.hero-cta{{display:flex;gap:12px;flex-wrap:wrap;margin-top:32px}}
.hero-note{{margin-top:16px;font-size:13px;color:var(--mut)}}

.strip{{border-block:1px solid var(--line);padding-block:22px}}
.strip-in{{display:flex;gap:34px;flex-wrap:wrap;font-size:13.5px;color:var(--mut)}}
.strip-in b{{color:var(--fg);font-weight:650}}

.grid3{{display:grid;grid-template-columns:repeat(auto-fit,minmax(248px,1fr));
  gap:20px;margin-top:44px}}
.card{{border:1px solid var(--line);border-radius:var(--r);padding:26px 24px;
  background:color-mix(in srgb,var(--fg) 2.5%,var(--bg))}}
.card h3{{margin-bottom:9px}}
.card p{{color:var(--mut);font-size:14.5px}}
.stat{{display:block;font-size:1.9rem;font-weight:780;letter-spacing:-.04em;
  color:var(--acc);margin-bottom:8px;font-variant-numeric:tabular-nums}}

.steps{{display:grid;grid-template-columns:repeat(auto-fit,minmax(214px,1fr));
  gap:1px;margin-top:44px;background:var(--line);
  border:1px solid var(--line);border-radius:var(--r);overflow:hidden}}
.step{{background:var(--bg);padding:28px 24px}}
.step .n{{font-size:12px;font-weight:700;color:var(--acc);letter-spacing:.1em}}
.step h3{{margin:12px 0 9px}}
.step p{{color:var(--mut);font-size:14.5px}}
.step .meta{{margin-top:16px;padding-top:13px;border-top:1px solid var(--line);
  font-size:12px;color:var(--mut)}}

.plans{{display:grid;grid-template-columns:repeat(auto-fit,minmax(262px,1fr));
  gap:20px;margin-top:44px}}
.plan{{border:1px solid var(--line);border-radius:var(--r);padding:30px 26px;
  display:flex;flex-direction:column}}
.plan.f{{border-color:var(--acc);border-width:2px}}
.plan .name{{font-size:15px;font-weight:650;color:var(--mut)}}
.plan .price{{font-size:2.7rem;font-weight:800;letter-spacing:-.045em;margin-top:12px;
  line-height:1;font-variant-numeric:tabular-nums}}
.plan .price small{{font-size:.9rem;font-weight:500;color:var(--mut);letter-spacing:0}}
.plan ul{{list-style:none;padding:0;margin:22px 0 26px;display:grid;gap:11px;
  font-size:14.5px;color:var(--mut);flex:1}}
.plan li{{display:flex;gap:10px;align-items:flex-start}}
.plan li svg{{flex:none;margin-top:4px;color:var(--acc)}}
.plan .btn{{width:100%;justify-content:center}}
.tag{{display:inline-block;font-size:11.5px;font-weight:700;padding:4px 11px;
  border-radius:999px;background:var(--acc);color:var(--bg);margin-bottom:12px}}

.faq{{margin-top:40px;border-top:1px solid var(--line);max-width:820px}}
details{{border-bottom:1px solid var(--line)}}
summary{{padding:21px 0;cursor:pointer;font-weight:650;font-size:1.02rem;
  list-style:none;display:flex;justify-content:space-between;gap:18px;align-items:center}}
summary::-webkit-details-marker{{display:none}}
summary::after{{content:"";width:10px;height:10px;flex:none;
  border-right:2px solid var(--mut);border-bottom:2px solid var(--mut);
  transform:rotate(45deg) translateY(-3px);transition:transform .28s var(--e)}}
details[open] summary::after{{transform:rotate(225deg) translateY(-3px)}}
details p{{padding-bottom:23px;color:var(--mut);font-size:15px}}

.final{{border:1px solid var(--line);border-radius:var(--r);
  padding:clamp(44px,6vw,76px) 32px;text-align:center;
  background:color-mix(in srgb,var(--acc) 6%,var(--bg))}}
.final h2{{margin-inline:auto}}
.final .lede{{margin-inline:auto}}
.final .hero-cta{{justify-content:center}}
footer{{border-top:1px solid var(--line);padding-block:32px;
  color:var(--mut);font-size:13.5px}}

section[id]{{scroll-margin-top:84px}}
.rv{{opacity:0;transform:translateY(22px);
  transition:opacity .65s var(--e),transform .65s var(--e)}}
.rv.in{{opacity:1;transform:none}}
html:not(.js) .rv{{opacity:1;transform:none}}
@media (max-width:640px){{ .nav-links{{display:none}} }}
@media (prefers-reduced-motion:reduce){{
  *,*::before,*::after{{animation-duration:.01ms!important;transition-duration:.01ms!important}}
  .rv{{opacity:1;transform:none}}
}}"""


def tick():
    return ('<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
            '<path d="M3 8.4l3.2 3.2L13 5" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def sec_hero(c, d):
    h = c.get("hero", {})
    b2 = (f'<a class="btn btn-2 btn-lg" href="#how">{E(h["cta2"])}</a>'
          if h.get("cta2") else "")
    note = f'<p class="hero-note">{E(h["note"])}</p>' if h.get("note") else ""
    return f'''<header class="hero"><div class="wrap">
  <h1 class="rv">{E(h.get("h1",""))}</h1>
  <p class="lede rv">{E(h.get("sub",""))}</p>
  <div class="hero-cta rv"><a class="btn btn-lg" href="#pricing">{E(h.get("cta","Почати"))}</a>{b2}</div>
  {note}
</div></header>'''


def sec_proof(c, d):
    items = c.get("proof") or []
    if not items:
        return ""
    return ('<div class="strip"><div class="wrap strip-in">'
            + "".join(f"<span>{E(x)}</span>" for x in items) + "</div></div>")


def _cards(block, with_stat=False):
    out = []
    for it in block.get("items", []):
        stat = f'<span class="stat">{E(it["stat"])}</span>' if with_stat and it.get("stat") else ""
        out.append(f'<div class="card rv">{stat}<h3>{E(it.get("t",""))}</h3>'
                   f'<p>{E(it.get("d",""))}</p></div>')
    return f'<div class="grid3">{"".join(out)}</div>'


def sec_problem(c, d):
    b = c.get("problem") or {}
    if not b.get("items"):
        return ""
    return f'''<section class="sec" id="problem"><div class="wrap">
  <div class="rv"><div class="eyebrow">Проблема</div><h2>{E(b.get("title",""))}</h2></div>
  {_cards(b)}
</div></section>'''


def sec_features(c, d):
    b = c.get("features") or {}
    if not b.get("items"):
        return ""
    lede = f'<p class="lede">{E(b["lede"])}</p>' if b.get("lede") else ""
    return f'''<section class="sec" id="features"><div class="wrap">
  <div class="rv"><div class="eyebrow">Що всередині</div><h2>{E(b.get("title",""))}</h2>{lede}</div>
  {_cards(b, with_stat=True)}
</div></section>'''


def sec_how(c, d):
    b = c.get("how") or {}
    if not b.get("steps"):
        return ""
    steps = "".join(
        f'<div class="step rv"><div class="n">{i+1:02d}</div><h3>{E(s.get("t",""))}</h3>'
        f'<p>{E(s.get("d",""))}</p>'
        + (f'<div class="meta">{E(s["meta"])}</div>' if s.get("meta") else "")
        + "</div>"
        for i, s in enumerate(b["steps"]))
    lede = f'<p class="lede">{E(b["lede"])}</p>' if b.get("lede") else ""
    return f'''<section class="sec" id="how"><div class="wrap">
  <div class="rv"><div class="eyebrow">Як це працює</div><h2>{E(b.get("title",""))}</h2>{lede}</div>
  <div class="steps">{steps}</div>
</div></section>'''


def sec_pricing(c, d):
    b = c.get("pricing") or {}
    if not b.get("plans"):
        return ""
    plans = []
    for p in b["plans"]:
        feats = "".join(f"<li>{tick()}{E(f)}</li>" for f in p.get("features", []))
        tag = '<span class="tag">Повний цикл</span>' if p.get("featured") else ""
        btn = "btn" if p.get("featured") else "btn btn-2"
        plans.append(f'<div class="plan rv{" f" if p.get("featured") else ""}">{tag}'
                     f'<div class="name">{E(p.get("name",""))}</div>'
                     f'<div class="price">{E(p.get("price",""))}'
                     f'<small>{E(p.get("unit",""))}</small></div>'
                     f'<ul>{feats}</ul>'
                     f'<a class="{btn}" href="#">{E(p.get("cta","Обрати"))}</a></div>')
    lede = f'<p class="lede">{E(b["lede"])}</p>' if b.get("lede") else ""
    return f'''<section class="sec" id="pricing"><div class="wrap">
  <div class="rv"><div class="eyebrow">Ціни</div><h2>{E(b.get("title",""))}</h2>{lede}</div>
  <div class="plans">{"".join(plans)}</div>
</div></section>'''


def sec_faq(c, d):
    items = c.get("faq") or []
    if not items:
        return ""
    qs = "".join(f'<details{" open" if i==0 else ""}><summary>{E(q.get("q",""))}</summary>'
                 f'<p>{E(q.get("a",""))}</p></details>' for i, q in enumerate(items))
    return f'''<section class="sec" id="faq"><div class="wrap">
  <div class="rv"><div class="eyebrow">Питання</div><h2>Що зазвичай питають</h2></div>
  <div class="faq">{qs}</div>
</div></section>'''


def sec_final(c, d):
    b = c.get("final") or {}
    if not b.get("h2"):
        return ""
    return f'''<section class="sec"><div class="wrap"><div class="final rv">
  <h2>{E(b["h2"])}</h2>
  <p class="lede">{E(b.get("sub",""))}</p>
  <div class="hero-cta"><a class="btn btn-lg" href="#pricing">{E(b.get("cta","Почати"))}</a></div>
</div></div></section>'''


SECTIONS = {"hero": sec_hero, "proof": sec_proof, "problem": sec_problem,
            "features": sec_features, "how": sec_how, "pricing": sec_pricing,
            "faq": sec_faq, "final": sec_final}


def build(content, d, template):
    order = TEMPLATES[template]
    body = "".join(SECTIONS[s](content, d) for s in order)
    prod = E(content.get("product", "Product"))
    title = E(content.get("hero", {}).get("h1", prod))
    return f'''<!doctype html>
<html lang="uk"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{prod} — {title}</title>
<meta name="description" content="{E(content.get("hero",{}).get("sub",""))}">
<style>{css(d)}</style>
</head><body>
<script>document.documentElement.classList.add("js")</script>
<nav><div class="wrap nav">
  <a class="logo" href="#"><i></i>{prod}</a>
  <a class="btn btn-2" href="#pricing">{E(content.get("hero",{}).get("cta","Почати"))}</a>
</div></nav>
{body}
<footer><div class="wrap">{E(content.get("footer", "© " + prod))}</div></footer>
<script>
const io=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting){{
  e.target.classList.add('in');io.unobserve(e.target)}}}}),{{threshold:.12,rootMargin:'0px 0px -6% 0px'}});
document.querySelectorAll('.rv').forEach((el,i)=>{{el.style.transitionDelay=(i%3*60)+'ms';io.observe(el)}});
setTimeout(()=>document.querySelectorAll('.rv').forEach(el=>el.classList.add('in')),2500);
</script>
</body></html>'''


def main():
    a = argparse.ArgumentParser(description="Лендінг: шаблон + контент + напрям")
    a.add_argument("content", nargs="?", help="JSON з контентом")
    a.add_argument("--direction", type=int, default=6, help="номер напряму з дошки (1-8)")
    a.add_argument("--template", default="saas", choices=list(TEMPLATES))
    a.add_argument("--out", default="index.html")
    a.add_argument("--schema", action="store_true", help="показати порожню контент-модель")
    args = a.parse_args()

    if args.schema:
        print(json.dumps(SCHEMA, ensure_ascii=False, indent=2))
        return
    if not args.content:
        sys.exit("Вкажи файл з контентом, або --schema щоб побачити модель")

    content = json.loads(Path(args.content).read_text(encoding="utf-8"))
    d = by_number(args.direction)
    Path(args.out).write_text(build(content, d, args.template), encoding="utf-8")
    print(f"Готово: {args.out}")
    print(f"  напрям:  {d['n']}. {d['name']} ({d['note']})")
    print(f"  шаблон:  {args.template} → {' · '.join(TEMPLATES[args.template])}")
    print("Перевір скріншотом на 1440 і 390 перед здачею.")


if __name__ == "__main__":
    main()
