---
name: cinematography
description: |
  Експерт з кінематографії для AI відео-генерації. ЗАВЖДИ використовуй цей скіл коли потрібно: описати рух камери у промпті, вибрати тип кадру, вказати освітлення, налаштувати глибину різкості, задати настрій через колір і атмосферу, або коли користувач каже "як описати рух камери", "які є типи кадрів", "як зробити кіношний вигляд", "що таке bokeh", "rack focus", "Dutch angle", "golden hour", "cinematic lighting", "як виглядає як кіно", "промпт виглядає штучно — як виправити". Також тригер: будь-яке прохання покращити якість AI відео через правильні кінематографічні терміни в промпті.
---

# Cinematography — Кінематографічна База для AI Промптів

## Ідентичність
Ти — кінооператор який знає як перетворити звичайний промпт на кіношний кадр. Кожне слово в промпті = інструкція для AI камери. Чим точніша мова — тим кращий результат.

---

## ТИПИ КАДРІВ (Shot Types)

### За відстанню до субʼєкта
| Назва | Англійська | Що показує | Коли використовувати |
|-------|-----------|-----------|---------------------|
| Загальний план | Extreme Wide Shot (EWS) | Весь простір, людина маленька | Встановлення локації |
| Широкий план | Wide Shot (WS) | Людина повністю + середовище | Контекст сцени |
| Середній план | Medium Shot (MS) | Від пояса вгору | Діалог, дії рук |
| Середній крупний | Medium Close-Up (MCU) | Від грудей вгору | Розмова, емоції |
| Крупний план | Close-Up (CU) | Обличчя | Емоції, деталі |
| Дуже крупний | Extreme Close-Up (ECU) | Очі, деталь | Драма, деталізація |
| Над плечем | Over-the-Shoulder (OTS) | З-за плеча | Діалог, точка зору |
| Точка зору | POV Shot | Очима персонажа | Залучення глядача |

**Для продукт (найчастіше використовуй):**
- `medium shot` — людина за ноутбуком, розмова
- `close-up` — руки на клавіатурі, екран з AI інтерфейсом
- `extreme wide shot` — офіс, простір, масштаб
- `POV shot` — "дивишся на екран з AI"

---

## РУХИ КАМЕРИ (Camera Movements)

### Основні рухи
```
СТАТИЧНІ:
static shot              — камера не рухається (стабільність, напруга)
locked-off shot          — жорстко зафіксована (документальний стиль)

ГОРИЗОНТАЛЬНІ:
pan left / pan right     — поворот камери (слідкування за субʼєктом)
truck left / truck right — переміщення камери (паралельно до сцени)

ВЕРТИКАЛЬНІ:
tilt up / tilt down      — нахил вгору/вниз (відкриття, пригнічення)
pedestal up / down       — підйом/опускання платформи (плавно)

НАБЛИЖЕННЯ:
zoom in / zoom out       — наближення/віддалення (без руху камери)
dolly in / dolly out     — фізичне наближення камери (більш "живе")
push in                  — повільне наближення (наростання напруги)
pull back / pull out     — відкриття масштабу

СКЛАДНІ:
arc shot                 — напівколо навколо субʼєкта
crane shot / jib         — підйом зверху
handheld                 — з рук (живість, документальність)
steadicam                — плавне переміщення (кінематографічно)
drone shot               — повітряна зйомка
whip pan                 — різкий панорамний рух (перехід між сценами)
```

### Комбінації для продукту з company/products.md контенту
```
— Інтро до огляду інструменту:
"slow push in on laptop screen showing AI interface, cinematic"

— Розкриття масштабу:
"pull back from close-up of screen to reveal full modern workspace"

— Динамічний Shorts початок:
"whip pan from dark background revealing bright AI interface screen"

— Технологічний B-Roll:
"slow arc shot around laptop with glowing AI dashboard, dark room, 
blue ambient lighting"

— Атмосферний початок:
"crane shot slowly descending into modern office space, morning light"
```

---

## ОСВІТЛЕННЯ (Lighting)

### Природне освітлення
```
golden hour              — тепле, м'яке, 1 год після сходу/перед заходом
blue hour                — синювате, містичне, одразу після заходу
overcast / cloudy        — рівномірне, без тіней, природне
harsh sunlight           — різкі тіні, контрастно, опівдні
window light             — бокове м'яке, студійний вигляд
```

### Штучне освітлення
```
soft box lighting        — рівномірне, студійне, YouTube-блогер стиль
ring light               — фронтальне, яскраве, TikTok стиль
rembrandt lighting       — одна сторона освітлена, драматично
backlit / rim light      — підсвічування ззаду, силует, містично
neon lighting            — кольорове, cyberpunk, технологічний стиль
ambient glow             — загальне слабке освітлення, атмосфера
god rays / light shafts  — промені через вікна або хмари
```

### Кольорова температура
```
warm lighting            — жовте/помаранчеве (затишок, продуктивність)
cool lighting            — синє/біле (технологічність, майбутнє)
neutral lighting         — природний баланс (документальність)
mixed lighting           — тепле+холодне (сучасний кінематограф)
```

### Кращі комбінації для продукту з company/products.md
```
— Технологічний AI контент:
"cool blue ambient lighting, screen glow reflecting on face, dark background"

— Продуктивний підприємець:
"warm soft box lighting, natural window light, bright modern office"

— Преміум / корпоративний:
"Rembrandt lighting, dark elegant background, single key light"

— Енергійний Shorts:
"bright even lighting, clean white background, high contrast"
```

---

## ЛІНЗИ ТА ОПТИКА (Lens & Optics)

### Глибина різкості
```
shallow depth of field   — тільки субʼєкт різкий, фон розмитий (боке)
deep depth of field      — все різке, від переднього до заднього плану
rack focus               — перефокусування з одного обʼєкта на інший
bokeh background         — художнє розмиття фону
```

### Типи лінз (для стилю)
```
wide angle lens          — широкий кут, простір здається більшим
telephoto / long lens    — компресія простору, фон здається ближче
macro lens               — екстремальна деталізація малих обʼєктів
anamorphic lens          — кінематографічні блики, широкий формат
```

### Дефекти лінз (додають реалізм)
```
lens flare               — відблиски від світла (кінематографічність)
chromatic aberration     — легке кольорове розмиття країв (реалізм)
film grain               — зерно плівки (аналоговий вигляд)
vignette                 — затемнення країв кадру (фокус на центрі)
```

---

## КУТИ КАМЕРИ (Camera Angles)

```
eye level                — рівень очей (нейтрально, природно)
low angle                — знизу вгору (сила, монументальність, погроза)
high angle               — зверху вниз (вразливість, малість, огляд)
bird's eye / top down    — прямо зверху (карта, деталь, абстракція)
Dutch angle / canted     — нахилений кадр (дезорієнтація, напруга)
worm's eye               — дуже низько знизу (епічність, велич)
```

---

## КОЛІР І НАСТРІЙ (Color Grading)

### Кольорові палітри
```
— Технологічний / AI:
"teal and orange color grade" — найпопулярніший кіностиль
"blue and silver tones" — холодний технологічний
"neon cyberpunk palette" — фіолетовий, рожевий, синій

— Продуктивність / Успіх:
"warm golden tones" — мотивація, енергія
"clean bright whites with accent colors" — мінімалізм

— Преміум / Корпоративний:
"desaturated muted tones" — стриманість
"dark moody cinematic" — серйозність, глибина

— Динамічний Shorts:
"vibrant saturated colors" — ютуб/тікток енергія
"high contrast black and white" — драматизм
```

### Терміни кольору для промптів
```
desaturated              — знебарвлений, стриманий
oversaturated            — яскравий, насичений
high contrast            — сильна різниця між темним і світлим
low contrast / flat      — рівномірний тон (кіно з Дарденів)
crushed blacks           — дуже глибокі тіні
lifted shadows           — підняті тіні (мʼякий вигляд)
film look / filmic       — виглядає як знято на плівку
```

---

## АТМОСФЕРА І ТЕКСТУРА

```
— Повітряні ефекти:
morning mist / fog       — туман, таємничість
dust particles           — частинки в повітрі (теплота, час)
smoke / haze             — атмосферна димка
rain streaks             — дощ (драма, меланхолія)

— Технологічні:
digital noise            — цифровий шум
glitch effect            — збій сигналу (технологічність)
holographic overlay      — голографічні елементи
data streams             — потоки даних
```

---

## ШВИДКІСТЬ КАМЕРИ

```
real time                — звичайна швидкість
slow motion (slo-mo)     — уповільнена зйомка (деталізація, драма)
time-lapse               — прискорена зйомка (час, трансформація)
ramping speed            — перехід між нормальною і уповільненою
hyperlapse               — рух камери + time-lapse
```

---

## ГОТОВІ КІНЕМАТОГРАФІЧНІ КОМБО ДЛЯ SYMPLEXY

### Комбо 1: "Технологічний Преміум" (для оглядів AI)
```
medium close-up, slow push in, teal and orange color grade, 
shallow depth of field, bokeh background, soft blue screen glow, 
cinematic anamorphic lens, dark ambient environment
```

### Комбо 2: "Продуктивний Підприємець" (для мотиваційного контенту)
```
medium shot, static locked-off, warm golden hour window light, 
deep depth of field, clean bright office environment, 
sharp focus, natural colors, documentary style
```

### Комбо 3: "Динамічний Shorts" (для Reels/TikTok)
```
close-up to medium shot, quick cut, whip pan transition, 
vibrant saturated colors, ring light, eye level angle, 
high contrast, energetic feel, handheld style
```

### Комбо 4: "Абстрактний AI" (для заставок і переходів)
```
extreme close-up, slow arc shot, neon cyberpunk palette, 
particles in air, lens flare, teal and purple gradient,
rack focus from foreground to background, film grain
```

### Комбо 5: "Документальний Авторитет" (для серйозних оглядів)
```
over-the-shoulder shot, static camera, neutral daylight color grade,
deep depth of field, natural office lighting, no lens effects,
journalistic style, ground level camera angle
```
