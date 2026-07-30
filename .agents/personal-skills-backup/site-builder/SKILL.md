---
name: site-builder
description: >
  Будує landing page / сайт на замовлення від нуля до фінального HTML-файлу
  з правильними фото, SVG-іконками, UX-формами і модальними вікнами.
  ЗАВЖДИ використовуй цей скіл коли: будуєш сайт за референсом, створюєш
  лендінг для бізнесу, правиш HTML/CSS сайт, підбираєш фото для сайту,
  додаєш форму запису або модальне вікно. Тригери: "зроби сайт", "лендінг",
  "референс", "виправ картинки", "додай модал", "виглядає не так".
---

# Site Builder — Від Референсу до Готового HTML


> ## ⚠️ УВАГА: у Claude Code на вебі стокові фото НЕ ПРАЦЮЮТЬ
> `images.pexels.com`, `picsum.photos`, `images.unsplash.com` і `fonts.googleapis.com`
> у цьому середовищі **заблоковані мережевою політикою** (перевірено 2026-07-30).
>
> Наслідок: сайт із зовнішніми фото відкриється у відвідувача нормально,
> **але я не побачу його на скріншоті** — тобто правило CLAUDE.md «перевіряй
> результат очима» перестає працювати, і я не помічу зламану верстку.
>
> **Тому за замовчуванням верстай без растрових фото:** inline SVG, градієнти,
> mesh/aurora-фони, типографіка, скріншоти продукту. Візуальна мова —
> скіл `design-system`. Фото додавай лише коли власник приніс файли в репозиторій.
>
> Розділ про Pexels нижче лишається чинним тільки для середовищ з відкритою мережею.


## Твоя роль
Ти — senior front-end розробник і дизайнер, що будує production-ready
односторінкові сайти у вигляді єдиного HTML-файлу з вбудованим CSS і JS.
Мова — та яку просить клієнт (дефолт: українська).

---

## КРОК 0 — Перед тим як писати код

Завжди починай з цього чеклисту:

### A. Аналіз референсу (якщо є)
Коли отримуєш референс-зображення — витягни **Style DNA**:

```
Фон:          [колір / текстура]
Акцент:       [колір кнопок і деталей]
Типографіка:  [характер — serif/sans, bold/light, з курсивом чи без]
Layout:       [2 колонки / повна ширина / асиметрія]
Картки:       [скло / тверді / тінь / без рамки]
Фото:         [є / немає / де / як обрізані]
Ключовий прийом: [що запам'ятовується найбільше]
```

Потім пиши код ТІЛЬКИ під цей DNA — не вигадуй свій стиль.

### B. Уточнення до старту
Запитай якщо не вказано:
- Ніша / послуга
- Місто
- Кольорова гамма (якщо немає референсу)
- Які блоки обов'язкові

---

## КРОК 1 — Фото: Єдиний Правильний Підхід

### Проблема яку треба уникати
Picsum.photos → рандомні фото (ведмеді, будівлі). Unsplash `images.unsplash.com` → не доступний без API ключа. `source.unsplash.com` → deprecated.

### Рішення: Pexels CDN + пошук опису

**Формат URL що ЗАВЖДИ працює в `<img src>`:**
```
https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?auto=compress&cs=tinysrgb&w={W}&h={H}&fit=crop
```

**Алгоритм підбору фото:**
1. Зроби пошук: `pexels.com photo {тема} site:pexels.com/photo`
2. З результатів читай ОПИС фото (Google показує alt-текст і keywords)
3. Вибирай тільки ті де опис ТОЧНО відповідає потрібній темі
4. Бери photo ID з URL: `pexels.com/photo/назва-{ID}/`
5. Завжди шукай мінімум 3 кандидати на кожну зону

**Пошукові запити для б'юті/лазер ніші:**
```
laser hair removal clinic woman site:pexels.com/photo      → hero, why
laser epilation legs procedure site:pexels.com/photo       → послуга "ноги"
woman smooth skin legs close up site:pexels.com/photo      → ноги
woman armpit underarm beauty site:pexels.com/photo         → пахви
hot stones back spa treatment site:pexels.com/photo        → спина
woman skincare face closeup portrait site:pexels.com/photo → обличчя
woman bikini body beach site:pexels.com/photo              → бікіні
beauty salon woman portrait site:pexels.com/photo          → аватари
```

**Перевірені Pexels ID для лазерної епіляції:**
| Зона | ID | Опис |
|------|-----|------|
| Hero (лазер процедура) | 3985354 | Beautician conducting laser hair removal |
| Why (майстер з апаратом) | 5619448 | Master doing laser epilation with apparatus |
| Ноги (гладка шкіра) | 8187421 | Close up legs smooth skin |
| Бікіні (тіло/купальник) | 1757976 | Woman wearing bikini |
| Обличчя (портрет) | 3373716 | Woman's face smooth skin |
| Руки (догляд) | 9775212 | Woman doing skin care |
| Пахви | 6591452 | Close up woman armpit |
| Спина/спа | 6560266 | Hot stones on back spa |
| Аватар жінка 1 | 774909 | Woman portrait |
| Аватар жінка 2 | 1036623 | Woman portrait |
| Аватар жінка 3 | 1065084 | Woman portrait |
| Аватар жінка 4 | 1499327 | Woman portrait |

**ВАЖЛИВО:** `<img src="https://images.pexels.com/...">` НІКОЛИ не потребує fetch().
`<img>` теги завантажуються напряму, без CORS. Не використовуй JS fetch для фото.

---

## КРОК 2 — Іконки: Тільки SVG, Ніколи Емодзі

### Правило
Емодзі (📍☎️📸) виглядають дешево і не вписуються в дизайн.
SVG-іконки масштабуються, приймають колір через CSS, виглядають на всіх екранах.

### Підхід
Вбудовуй SVG напряму в HTML — не потрібен CDN, не потрібен fetch.
Використовуй Feather Icons / Lucide (24x24 grid, stroke-width: 1.8).

**Готові SVG для б'юті сайту:**
```html
<!-- Локація -->
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
  <circle cx="12" cy="10" r="3"/>
</svg>

<!-- Телефон -->
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
  <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 8.81 19.79 19.79 0 010 2.18 2 2 0 012 0h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 7.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>
</svg>

<!-- Instagram -->
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
  <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
  <path d="M16 11.37A4 4 0 1112.63 8 4 4 0 0116 11.37z"/>
  <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
</svg>

<!-- Годинник -->
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
</svg>

<!-- Блискавка (апарат/енергія) -->
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
  <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
</svg>

<!-- Щит (гарантія) -->
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
</svg>

<!-- Стрілка → (картки послуг) -->
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <line x1="5" y1="12" x2="19" y2="12"/>
  <polyline points="12 5 19 12 12 19"/>
</svg>

<!-- Галочка (успіх) -->
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
  <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
  <polyline points="22 4 12 14.01 9 11.01"/>
</svg>
```

---

## КРОК 3 — Glassmorphism: Як у Референсі

Glassmorphism працює тільки коли картки **поверх фото/кольорового фону**.
На білому фоні — просто виглядає як напівпрозорий div.

**Правильний CSS:**
```css
.glass-card {
  background: rgba(255, 255, 255, 0.22);
  backdrop-filter: blur(18px) saturate(180%);
  -webkit-backdrop-filter: blur(18px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.55);
  border-radius: 18px;
  box-shadow:
    0 8px 32px rgba(26,23,16,0.18),
    inset 0 1px 0 rgba(255,255,255,0.6);
}
```

**Важливо:**
- `overflow: hidden` на батьківському контейнері прибирає картки з поля зору — використовуй `overflow: visible`
- Картки мають бути всередині межі фото (не `left: -20px`)
- Градієнт між текстом і фото: `linear-gradient(to right, var(--bg) 0%, transparent 28%)`

---

## КРОК 4 — UX: Модальне Вікно Запису

### Архітектура
Єдиний модал на всю сторінку. Всі кнопки "Записатись" відкривають його з потрібними параметрами.

```js
// Будь-яка кнопка на сторінці
onclick="openModal({dataset:{zone:'Назва зони', price:'1200', sessions:'6'}})"

// Картка послуги (DOM-елемент)
<div data-zone="Ноги" data-price="1200" data-sessions="6" onclick="openModal(this)">
```

```js
function openModal(card) {
  const dataset = card.dataset || card; // підтримка обох форматів
  ...
}
```

### Структура модала
1. Назва зони (з data-zone)
2. Кнопки кількості сеансів (динамічні, 1..N)
3. Динамічний калькулятор ціни зі знижкою
4. Кнопка "Тільки консультація"
5. Поля Ім'я + Телефон
6. CTA-кнопка (золота, градієнтна)
7. Після відправки → thank-you screen з анімацією

### Єдине джерело знижок
```js
const discounts = { 1:0, 2:5, 3:10, 4:15, 5:18, 6:20 };
// НЕ дублювати знижки в HTML — тільки через JS
```

**Знижки мають бути однаковими скрізь:** в модалі, на сторінці, в офер-блоці.

---

## КРОК 5 — HTML Структура Лендінгу

### Обов'язкові секції (порядок)
```
1. NAV          — фіксований, blur backdrop, логотип + посилання + CTA
2. HERO         — 2 колонки: текст + фото з glass-картками
3. MARQUEE      — темна стрічка що крутиться
4. WHY          — фото + список переваг з SVG-іконками
5. SERVICES     — сітка карток з фото + onclick модал
6. PROCESS      — 4 кроки
7. REVIEWS      — 3 відгуки з аватарами
8. OFFER        — офер-блок з ціною
9. CONTACTS     — контакти + форма
10. FOOTER      — лінки + великий логотип
```

### Переходи між секціями
Hero → Marquee — плавний градієнт знизу:
```css
.hero::after {
  content: '';
  position: absolute; bottom: 0; left: 0; right: 0; height: 120px;
  background: linear-gradient(to bottom, transparent, var(--bg));
  z-index: 5;
}
```

---

## КРОК 6 — Чеклист перед відповіддю

Перед тим як видати HTML — перевір кожен пункт:

- [ ] Всі `<img>` мають src з Pexels CDN або іншим реальним URL
- [ ] Жодного `src=""` або `src="#"` в `<img>`
- [ ] Жодного емодзі в іконках — тільки SVG
- [ ] Glassmorphism — картки поверх фото, `overflow: visible` на контейнері
- [ ] Всі кнопки "Записатись" ведуть до модала
- [ ] Знижки однакові скрізь (єдина константа)
- [ ] Модал відновлюється після закриття (originalModalHTML)
- [ ] Кнопка в формі відрізняється візуально (золота, велика, не схожа на текст)

---

## КРОК 7 — Деплой

Після створення файлу — нагадай:
> Відкрий на Netlify Drop (netlify.com/drop) — перетягни HTML-файл.
> Там фото будуть 100% завантажуватись (Pexels CDN не має CORS на https://).
> При відкритті з локального файлу (file://) зовнішні фото можуть не вантажитись.

---

## Довідка: Типові Помилки і Рішення

| Проблема | Причина | Рішення |
|----------|---------|---------|
| Фото не вантажаться | Відкриваєш з `file://` | Деплой на Netlify Drop |
| Рандомні фото (ведмідь) | Picsum без seed | Pexels з конкретним ID |
| Картки обрізані | `overflow:hidden` на батьку | `overflow:visible` |
| Glassmorphism не видно | Картки на білому фоні | Помісти поверх фото |
| Кнопка схожа на текст | Немає стилізації | Окремий клас з градієнтом |
| Знижки різняться | Дубльовані в HTML | Єдина JS константа |
| Модал не відновлюється | innerHTML не зберігається | `originalModalHTML` при DOMContentLoaded |
