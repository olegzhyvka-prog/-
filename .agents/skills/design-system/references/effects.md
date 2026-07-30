# Бібліотека візуальних ефектів

Усе — чистий CSS/JS без зовнішніх файлів, бібліотек і CDN.
Копіюй, підставляй свої токени. Кожен блок перевірений і самодостатній.

---

## 1. Aurora / mesh-градієнт (герой-фон №1)

Найкраще співвідношення «вау ÷ зусилля». Живий, дорогий, не відволікає.

```css
.aurora {
  position: relative;
  overflow: hidden;
  background: var(--ink-950);
  isolation: isolate;
}
.aurora::before {
  content: "";
  position: absolute;
  inset: -40%;
  z-index: -1;
  background:
    radial-gradient(38% 44% at 22% 28%, color-mix(in oklab, var(--brand-500) 55%, transparent), transparent 70%),
    radial-gradient(32% 38% at 78% 22%, color-mix(in oklab, var(--accent-400) 45%, transparent), transparent 70%),
    radial-gradient(46% 46% at 58% 82%, color-mix(in oklab, var(--brand-700) 50%, transparent), transparent 70%);
  filter: blur(60px) saturate(1.15);
  animation: aurora-drift 22s ease-in-out infinite alternate;
  will-change: transform;
}
@keyframes aurora-drift {
  0%   { transform: translate3d(-3%, -2%, 0) scale(1.05) rotate(0deg); }
  50%  { transform: translate3d(4%, 3%, 0)   scale(1.15) rotate(6deg); }
  100% { transform: translate3d(-2%, 4%, 0)  scale(1.08) rotate(-4deg); }
}
@media (prefers-reduced-motion: reduce) {
  .aurora::before { animation: none; }
}
```

**Тюнінг:** `blur` 40-90px. Менше — видно «плями», більше — каша.
Для світлої теми — ті ж кольори з `opacity: .35` і фоном `--ink-50`.

---

## 2. Шумова текстура (обов'язково поверх градієнтів)

Один шар який відрізняє «дорого» від «дефолтний CSS-градієнт».
SVG-шум інлайном, ~200 байт, без запитів у мережу.

```css
.noise::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: .045;
  mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
```
`opacity` 0.03-0.06. Вище — виглядає брудно.

---

## 3. Шарові тіні (замість дефолтної)

```css
:root {
  /* дешево: 0 4px 6px rgba(0,0,0,.1)  ← так не робимо */
  --shadow-sm:
    0 1px 2px  -1px rgb(0 0 0 / .08),
    0 2px 4px  -2px rgb(0 0 0 / .06);
  --shadow-md:
    0 1px 2px  -1px rgb(0 0 0 / .07),
    0 4px 8px  -2px rgb(0 0 0 / .07),
    0 12px 20px -6px rgb(0 0 0 / .07);
  --shadow-lg:
    0 1px 2px   -1px rgb(0 0 0 / .06),
    0 6px 12px  -3px rgb(0 0 0 / .07),
    0 20px 32px -8px rgb(0 0 0 / .09),
    0 40px 64px -16px rgb(0 0 0 / .10);
}
```
Принцип: 3-4 шари, кожен наступний більший і м'якший, прозорість ~однакова.
У темній темі тіні майже не видно — замість них тонкий світлий бордюр зверху:
`box-shadow: inset 0 1px 0 rgb(255 255 255 / .07)`.

---

## 4. Glass / frosted panel

```css
.glass {
  background: color-mix(in oklab, var(--ink-900) 55%, transparent);
  backdrop-filter: blur(16px) saturate(160%);
  -webkit-backdrop-filter: blur(16px) saturate(160%);
  border: 1px solid rgb(255 255 255 / .08);
  box-shadow:
    inset 0 1px 0 rgb(255 255 255 / .06),
    var(--shadow-lg);
  border-radius: var(--r-lg);
}
```
Працює тільки якщо ПІД панеллю є що розмивати. Glass над однотонним фоном — марно.

---

## 5. Свічення бордюру (conic border)

Преміальний акцент для головної картки/CTA.

```css
.glow-border {
  position: relative;
  border-radius: var(--r-lg);
  background: var(--ink-900);
  isolation: isolate;
}
.glow-border::before {
  content: "";
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  z-index: -1;
  background: conic-gradient(from var(--a, 0deg),
    transparent 0 62%,
    var(--brand-400) 78%,
    var(--brand-200) 84%,
    transparent 92% 100%);
  animation: spin 5s linear infinite;
}
@property --a { syntax: "<angle>"; initial-value: 0deg; inherits: false; }
@keyframes spin { to { --a: 360deg; } }
@media (prefers-reduced-motion: reduce) { .glow-border::before { animation: none; } }
```

---

## 6. Градієнтний текст

```css
.grad-text {
  background: linear-gradient(180deg,
    var(--ink-50) 30%,
    color-mix(in oklab, var(--ink-50) 55%, transparent) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
```
Вертикальний градієнт від білого до напівпрозорого — виглядає дорого і читається.
Райдужний горизонтальний градієнт по тексту — виглядає дешево. Не роби.

---

## 7. Scroll reveal — нативний CSS, без JS

```css
@supports (animation-timeline: view()) {
  .reveal {
    animation: reveal-in linear both;
    animation-timeline: view();
    animation-range: entry 5% cover 32%;
  }
}
@keyframes reveal-in {
  from { opacity: 0; transform: translateY(24px) scale(.98); }
  to   { opacity: 1; transform: none; }
}
/* фолбек для старих браузерів — просто показати */
@supports not (animation-timeline: view()) {
  .reveal { opacity: 1; }
}
@media (prefers-reduced-motion: reduce) {
  .reveal { animation: none; opacity: 1; transform: none; }
}
```

JS-версія (ширша підтримка):
```js
const io = new IntersectionObserver((es) => {
  es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
}, { threshold: .15, rootMargin: '0px 0px -8% 0px' });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));
```
```css
.reveal { opacity: 0; transform: translateY(24px); transition: opacity .6s cubic-bezier(.16,1,.3,1), transform .6s cubic-bezier(.16,1,.3,1); }
.reveal.in { opacity: 1; transform: none; }
.reveal:nth-child(2) { transition-delay: .06s }
.reveal:nth-child(3) { transition-delay: .12s }
```

---

## 8. Spotlight за курсором

```js
document.querySelectorAll('.spot').forEach(card => {
  card.addEventListener('pointermove', e => {
    const r = card.getBoundingClientRect();
    card.style.setProperty('--mx', `${e.clientX - r.left}px`);
    card.style.setProperty('--my', `${e.clientY - r.top}px`);
  });
});
```
```css
.spot { position: relative; overflow: hidden; }
.spot::before {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  opacity: 0; transition: opacity .3s;
  background: radial-gradient(280px circle at var(--mx) var(--my),
    color-mix(in oklab, var(--brand-400) 16%, transparent), transparent 70%);
}
.spot:hover::before { opacity: 1; }
```

---

## 9. Magnetic button

```js
document.querySelectorAll('.magnet').forEach(b => {
  b.addEventListener('pointermove', e => {
    const r = b.getBoundingClientRect();
    const x = (e.clientX - r.left - r.width / 2) * .22;
    const y = (e.clientY - r.top - r.height / 2) * .22;
    b.style.transform = `translate3d(${x}px, ${y}px, 0)`;
  });
  b.addEventListener('pointerleave', () => { b.style.transform = ''; });
});
```
```css
.magnet { transition: transform .35s cubic-bezier(.16,1,.3,1); }
```
Не застосовуй до головного CTA — рухома ціль знижує конверсію. Тільки до вторинних.

---

## 10. Count-up для цифр

```js
const cu = new IntersectionObserver((es) => es.forEach(e => {
  if (!e.isIntersecting) return;
  const el = e.target, end = +el.dataset.to, dur = 1100, t0 = performance.now();
  const tick = t => {
    const p = Math.min((t - t0) / dur, 1);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(end * eased).toLocaleString('uk-UA');
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
  cu.unobserve(el);
}), { threshold: .6 });
document.querySelectorAll('[data-to]').forEach(el => cu.observe(el));
```

---

## 11. Безшовний тікер логотипів

```css
.ticker { overflow: hidden; mask-image: linear-gradient(90deg, transparent, #000 12%, #000 88%, transparent); }
.ticker__row { display: flex; gap: 48px; width: max-content; animation: slide 28s linear infinite; }
.ticker:hover .ticker__row { animation-play-state: paused; }
@keyframes slide { to { transform: translateX(-50%); } }
```
HTML: продублюй список логотипів **двічі** всередині `.ticker__row` — тоді на -50% стик непомітний.

---

## 12. WebGL-шейдер фону (важка артилерія)

Використовуй один раз на сайт, тільки в герої, тільки на десктопі.

```js
const c = document.getElementById('bg');
const gl = c.getContext('webgl');
const vs = `attribute vec2 p; void main(){ gl_Position = vec4(p,0.,1.); }`;
const fs = `precision highp float;
uniform vec2 r; uniform float t;
// проста фрактальна хмара
float h(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
float n(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h(i),h(i+vec2(1,0)),f.x), mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x), f.y); }
void main(){
  vec2 uv = (gl_FragCoord.xy - .5*r)/r.y;
  float f = 0., a = .5; vec2 q = uv*2.4 + vec2(t*.03, t*.02);
  for(int i=0;i<5;i++){ f += a*n(q); q*=2.02; a*=.5; }
  vec3 c1 = vec3(.055,.055,.075);          // фон
  vec3 c2 = vec3(.35,.30,.95);             // бренд
  vec3 col = mix(c1, c2, smoothstep(.35,.85,f)*.55);
  gl_FragColor = vec4(col,1.);
}`;
function sh(t, s){ const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); return o; }
const pr = gl.createProgram();
gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs));
gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs));
gl.linkProgram(pr); gl.useProgram(pr);
const buf = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, buf);
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,3,-1,-1,3]), gl.STATIC_DRAW);
const loc = gl.getAttribLocation(pr,'p');
gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
const uR = gl.getUniformLocation(pr,'r'), uT = gl.getUniformLocation(pr,'t');
const resize = () => { c.width = innerWidth; c.height = innerHeight; gl.viewport(0,0,c.width,c.height); };
addEventListener('resize', resize); resize();
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
(function loop(t){
  gl.uniform2f(uR, c.width, c.height);
  gl.uniform1f(uT, reduce ? 0 : t*.001);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  if (!reduce) requestAnimationFrame(loop);
})(0);
```
**Обов'язково:** вимикай на `innerWidth < 900` і при `prefers-reduced-motion`.
Фолбек — CSS-градієнт з п.1.

---

## 13. Сітка / патерн фону

```css
.grid-bg {
  background-image:
    linear-gradient(to right, rgb(255 255 255 / .045) 1px, transparent 1px),
    linear-gradient(to bottom, rgb(255 255 255 / .045) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(70% 60% at 50% 30%, #000 30%, transparent 100%);
}
```
Маска — критична. Без неї сітка йде до країв і виглядає як таблиця.

---

## 14. Easing і тривалості (шпаргалка)

```css
--e-out:   cubic-bezier(.16, 1, .3, 1);      /* дефолт для появи, виглядає дорого */
--e-inout: cubic-bezier(.65, 0, .35, 1);     /* переходи між станами */
--e-spring:cubic-bezier(.34, 1.56, .64, 1);  /* легкий відскок, дозовано */

--t-fast: 150ms;   /* hover, focus */
--t-base: 280ms;   /* більшість переходів */
--t-slow: 520ms;   /* поява секцій */
```
`linear` — тільки для нескінченних обертань/тікерів. Ніде більше.

---

## 15. Продуктивність — чекліст перед здачею

- [ ] Анімуються тільки `transform` / `opacity` / `filter`
- [ ] `will-change` стоїть тільки на елементах що реально анімуються постійно
- [ ] `backdrop-filter` — не більше 2-3 елементів на екран
- [ ] WebGL/Canvas вимкнено на мобільному
- [ ] `prefers-reduced-motion` покриває всі анімації
- [ ] Жодного зовнішнього запиту: шрифти локально або системні, картинки inline SVG / data-URI
- [ ] LCP-елемент (заголовок героя) не чекає на JS і не анімується на вході
