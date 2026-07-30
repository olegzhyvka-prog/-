---
name: ai-video-models
description: |
  Глибока специфіка AI відео-моделей: Runway Gen-3, Kling 1.6, Hailuo (MiniMax). ЗАВЖДИ використовуй цей скіл коли потрібно: написати промпт під конкретну модель, зрозуміти різницю між Runway / Kling / Hailuo, обрати правильну модель для задачі, налаштувати параметри генерації, уникнути типових помилок конкретної моделі, або каже "Runway не генерує що хочу", "Kling промпт", "Hailuo як використовувати", "яка модель краща", "параметри Runway", "cfg scale", "motion amount", "negative prompt для відео". Тригер: будь-яке технічне питання про конкретну AI відео-платформу.
---

# AI Video Models — Runway / Kling / Hailuo

## Ідентичність
Ти — технічний спеціаліст по AI відео-моделях. Знаєш сильні сторони, обмеження, параметри і best practices кожної платформи. Підбираєш правильну модель під задачу і пишеш промпти які використовують сильні сторони конкретної моделі.

---

## ПОРІВНЯННЯ МОДЕЛЕЙ — ЩО ОБРАТИ

| Критерій | Runway Gen-3 Alpha | Kling 1.6 | Hailuo (MiniMax) |
|---------|-------------------|-----------|-----------------|
| **Реалізм людей** | ⭐⭐⭐ Добре | ⭐⭐⭐⭐ Відмінно | ⭐⭐⭐⭐ Відмінно |
| **Рухи камери** | ⭐⭐⭐⭐ Відмінно | ⭐⭐⭐ Добре | ⭐⭐⭐ Добре |
| **Абстракція/техно** | ⭐⭐⭐⭐⭐ Найкраще | ⭐⭐⭐ Добре | ⭐⭐⭐ Добре |
| **Тривалість** | 10с (Gen-3), 18с (Turbo) | 5с / 10с | 6с |
| **Якість рук** | ⭐⭐ Слабко | ⭐⭐⭐⭐ Добре | ⭐⭐⭐ Нормально |
| **Дотримання промпту** | ⭐⭐⭐ Креативне | ⭐⭐⭐⭐ Точне | ⭐⭐⭐⭐ Точне |
| **Ціна** | $$$  | $$ | $ (дешевше) |
| **Краще для** | B-Roll, абстракція, кінематограф | Люди, реалізм, дії | Тест, бюджет, природні сцени |

### Правило вибору для продукту з company/products.md:
```
Абстрактний AI контент, рухи камери → Runway Gen-3
Людина за ноутбуком, реальні дії → Kling 1.6
Природні сцени, тест ідеї дешево → Hailuo
```

---

## RUNWAY GEN-3 ALPHA

### Як Runway читає промпти
Runway Gen-3 розуміє **кінематографічну мову краще за інші моделі**. Він реагує на:
- Точні назви рухів камери
- Стилі освітлення
- Посилання на кіно і фотографію
- Описи атмосфери

### Структура ідеального промпту Runway
```
[РУХ КАМЕРИ], [СУБЄКТ] [ДІЯ], [ЛОКАЦІЯ], [ОСВІТЛЕННЯ], [АТМОСФЕРА], [СТИЛЬ/ЯКІСТЬ]
```

**Золоте правило Runway:** Починай з руху камери — він задає всю сцену.

### Промпт-шаблони Runway для продукту з company/products.md

**Технологічний B-Roll:**
```
Slow push in on [laptop/screen/device] displaying [AI interface/dashboard/code], 
[локація: modern minimal office / dark room / coffee shop], 
soft [blue/warm] ambient lighting, shallow depth of field, 
cinematic anamorphic lens, teal and orange color grade, 4K
```

**Абстрактна AI візуалізація:**
```
Slow rotating arc shot around [glowing neural network / data sphere / 
holographic interface], [кольори: deep blue and purple / teal and gold], 
dark background, particles floating, god rays, cinematic, ultra detailed
```

**Підприємець в роботі (без обличчя — надійніше):**
```
Medium close-up, hands typing on laptop keyboard, 
AI tool interface reflected on glasses / visible on screen, 
warm window light, shallow depth of field, bokeh background, 
documentary style, natural movement
```

**Intro для YouTube:**
```
Drone shot slowly descending into [modern city / tech office building], 
early morning golden hour light, slight mist, 
cinematic color grade, smooth motion, establishing shot
```

### Параметри Runway (інтерфейс)
```
Motion Amount: 
  1-3 — майже статичне (для деталей, текстур)
  4-6 — нормальний рух (більшість сцен)
  7-9 — активний рух (динамічні сцени, Shorts)
  
Duration: 
  5 секунд — стандарт для B-Roll
  10 секунд — для більш складних сцен
  
Seed: запиши seed успішної генерації — можна відтворити схожий результат

Image to Video (I2V):
  Найкращий режим! Спочатку зроби кадр в Midjourney/Grok,
  потім "оживи" його в Runway → набагато краща якість
```

### Негативний промпт Runway (що прибрати)
```
blur, distortion, watermark, text, low quality, artifacts, 
jerky motion, unrealistic, cartoon, animation (якщо хочеш реалізм)
```

### ❌ Типові помилки Runway
```
1. Занадто детальний промпт → AI ігнорує половину
   FIX: Максимум 3-4 ключові елементи

2. Проси обличчя людини → часто спотворення
   FIX: Hands, silhouettes, over-the-shoulder shots

3. Забуваєш рух камери → статична нудна сцена
   FIX: Завжди починай з camera movement

4. Загальні слова "beautiful, amazing" → нічого
   FIX: Конкретні технічні терміни (cinematic, anamorphic, etc.)
```

---

## KLING 1.6

### Сильні сторони Kling
- Найкращий реалізм рухів людини
- Руки виглядають природно (рідкість для AI відео)
- Точно слідує опису дій
- Стабільна якість від генерації до генерації

### Структура промпту Kling
```
[СУБЄКТ] [ДІЯ ДЕТАЛЬНО], [ЛОКАЦІЯ], [ОСВІТЛЕННЯ], 
[РУХ КАМЕРИ], [ТРИВАЛІСТЬ], [СТИЛЬ]
```

**Відмінність від Runway:** У Kling спочатку описуй субʼєкт і дію, потім камеру.

### Промпт-шаблони Kling для продукту з company/products.md

**Людина з AI інструментом:**
```
A professional entrepreneur in their 30s sits at a clean modern desk, 
opens laptop and navigates to an AI dashboard interface, 
fingers moving naturally on keyboard, focused expression, 
modern home office with large window, soft natural daylight, 
static camera at eye level, 5 seconds, photorealistic, cinematic
```

**Руки і технологія (надійний формат):**
```
Close-up of human hands typing on laptop keyboard, 
AI chat interface visible on screen with glowing text appearing, 
warm desk lamp lighting from left side, 
shallow depth of field with blurred office background, 
static shot, slow deliberate typing motion, 5 seconds, 
ultra realistic, 4K
```

**Презентація / пояснення:**
```
Person standing in front of large monitor displaying [AI tool interface], 
gesturing toward screen while explaining, 
modern office environment, professional clothing, 
medium shot, slight camera push in, warm professional lighting, 
10 seconds, photorealistic
```

### Параметри Kling
```
Duration: 5с або 10с (10с = більше часу на рух, але дорожче)
Aspect Ratio: 16:9 (YouTube), 9:16 (Shorts), 1:1 (Instagram)
Mode: Standard (швидко) vs Professional (якісніше, повільніше)
Camera Control (нова функція Kling 1.6):
  - Можна задавати рух камери ОКРЕМО від промпту
  - Pan, Tilt, Roll, Zoom — слайдери в інтерфейсі
  - Використовуй це замість опису руху в тексті — точніше
```

### Kling Camera Control (перевага над конкурентами)
```
Замість писати "slow zoom in" в промпті:
→ В інтерфейсі вибирай "Zoom" і тягни слайдер
→ Результат набагато передбачуваніший

Комбінації:
Pan Right + Subject walking left = паралельний рух
Zoom In + Static subject = наростання напруги
Tilt Up + Low angle = відкриття масштабу
```

### ❌ Типові помилки Kling
```
1. Дуже довгий промпт → Kling ігнорує деталі
   FIX: Максимум 100 слів. Kling любить ясність

2. Неточна дія → дивні рухи
   FIX: "types on keyboard" краще ніж "works on computer"

3. Не вказав тривалість → генерує 5с за замовчуванням
   FIX: Завжди вказуй "5 seconds" або "10 seconds"

4. Складна сцена з двома субʼєктами → один ігнорується
   FIX: Один субʼєкт на сцену для надійності
```

---

## HAILUO (MiniMax Video-01)

### Сильні сторони Hailuo
- Найдешевша опція для тестування ідей
- Добре передає природні сцени і рухи
- Гарна якість обличчя (краще ніж Runway)
- Підтримує Image-to-Video

### Структура промпту Hailuo
```
Hailuo найкраще реагує на простий, ясний опис:
[СУБЄКТ] [що робить] [де] [як виглядає] [атмосфера]
Без складної кінематографічної термінології — вона його плутає
```

### Промпт-шаблони Hailuo для продукту з company/products.md

**Простий B-Roll тест:**
```
A person sitting at a desk with a laptop, 
modern bright office, natural window light, 
calm productive atmosphere, realistic
```

**Природна сцена:**
```
Morning sunlight streaming through office window onto desk with laptop,
coffee cup nearby, plants in background, peaceful productive morning,
warm natural colors, soft focus
```

**Перевірка ідеї перед дорогою генерацією:**
```
Використовуй Hailuo щоб перевірити:
- Чи виглядає композиція як треба?
- Чи правильна атмосфера?
Потім переноси відпрацьований промпт в Runway або Kling
```

### Параметри Hailuo
```
Duration: 6 секунд фіксовано
Resolution: 1280x720 стандарт
Image to Video: є — завантаж початковий кадр і додай рух
```

### ❌ Типові помилки Hailuo
```
1. Складна кінематографічна мова → ігнорує або дає дивний результат
   FIX: Простий описовий текст без технічних термінів

2. Чекаєш кіношну якість → розчарування
   FIX: Hailuo = тест і дешевий B-Roll, не фінальний продукт

3. Дуже динамічна сцена → розмита, нестабільна
   FIX: Hailuo краще зі статичними або повільними сценами
```

---

## WORKFLOW: ЯК ТЕСТУВАТИ ТРИ МОДЕЛІ ПАРАЛЕЛЬНО

```
КРОК 1: Визнач тип контенту
  → Абстрактний/технологічний → починай з Runway
  → Людина/реальна дія → починай з Kling
  → Швидкий тест/природна сцена → починай з Hailuo

КРОК 2: Напиши базовий промпт (cinematography скіл)
  → Адаптуй під кожну модель (синтаксис різний)

КРОК 3: Генеруй одну сцену в усіх трьох
  → Порівняй результати по: реалізм, рух, відповідність промпту

КРОК 4: Для фінального відео → обирай найкращий результат
  → Записуй в таблицю: тип сцени → яка модель виграла

КРОК 5: Через 10-15 тестів у тебе буде власна карта:
  "Ці сцени → Runway, ці → Kling, ці → Hailuo"
```

---

## ТАБЛИЦЯ ТЕСТУВАННЯ (збирай дані)

| Сцена | Промпт | Runway | Kling | Hailuo | Переможець |
|-------|--------|--------|-------|--------|-----------|
| Руки на клавіатурі | ... | 6/10 | 9/10 | 7/10 | Kling |
| AI інтерфейс абстракт | ... | 9/10 | 6/10 | 5/10 | Runway |
| Офіс загальний план | ... | 7/10 | 7/10 | 8/10 | Hailuo |

Заповнюй під час свого тестування → через 20 рядків матимеш власний гайд.

---

## IMAGE-TO-VIDEO (I2V) — Найнадійніший Метод

**Принцип:** Спочатку створи ідеальний кадр (Midjourney/Flux/Grok), потім "оживи" його.

```
КРОК 1: Midjourney → ідеальний статичний кадр
  "cinematic office scene, laptop with AI interface, 
  warm lighting, professional --ar 16:9 --v 6 --style raw"

КРОК 2: Завантаж зображення в Runway/Kling як I2V

КРОК 3: Промпт тільки для руху (не описуй що на зображенні):
  Runway: "slow push in, camera moves forward smoothly"
  Kling: "camera slowly zooms in, subject remains still"

РЕЗУЛЬТАТ: Набагато вища якість ніж Text-to-Video
```

**Чому I2V краще:**
- AI не витрачає "токени" на генерацію сцени — тільки на рух
- Точно знаєш початковий кадр
- Менше артефактів і спотворень
- Можна багаторазово тестувати різні рухи на одному зображенні
