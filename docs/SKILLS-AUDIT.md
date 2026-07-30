# Ревізія скілів — 2026-07-30

**Було:** 89 активних скілів, ~12 500 токенів описів у кожному запиті.
**Стало:** 36 активних. Решта — в архіві, не видалена.

---

## Навіщо це зроблено

Скіл вибирається за описом. Коли 12 скілів претендують на слово «лендінг»,
а 10 на «конкурент», вибір стає лотереєю: спрацьовує не найкращий, а найближчий
за формулюванням. Плюс кожен опис — це токени в кожному запиті, ще до вашого питання.

**Критерій відбору один:** чи служить скіл головному циклу з CLAUDE.md —
перевірити гіпотезу за 7 днів і $300.

Усе інше — не «погане». Воно передчасне (churn до першого клієнта),
поза профілем (ASO без мобільних застосунків) або дублює те, що лишилось.

---

## Нічого не видалено

| Тип | Де лежить | Як повернути |
|---|---|---|
| Проєктні | `.agents/skills/` — на місці, лише знято символьне посилання | `ln -s ../../.agents/skills/<ім'я> .claude/skills/<ім'я>` |
| Особисті | `~/.claude/skills-archive/` + копія в `.agents/personal-skills-backup/` | `mv ~/.claude/skills-archive/<ім'я> ~/.claude/skills/` |

Скрипт відновлення: `docs/restore-skill.sh <ім'я>`

⚠️ **Особисті скіли синхронізуються з claude.ai.** Якщо після синхронізації
заархівований скіл повернеться в `~/.claude/skills/` — його треба видалити
в інтерфейсі claude.ai, локальне переміщення там не враховується.

---

## Активні (36)

### Цикл гіпотези — 5
`hypothesis-dossier` · `unit-economics-calc` · `smoke-test-kit` · `test-readout` · `handoff-protocol`

### Дослідження — 4
`niche-research` · `competitor-intelligence` · `customer-research` · `decision-framework`

### Гроші — 2
`pricing-strategy` · `monetization`

### Сайт — 6
`site-architecture` · `site-builder` · `design-system` · `copywriting` · `page-cro` · `form-cro`

### Трафік і дані — 4
`paid-ads` · `analytics-tracking` · `ab-test-setup` · `ad-creative`

### Відео — 6
`video-assembly` · `video-scriptwriter` · `ugc-creator` · `ai-video-prompts` · `ai-video-models` · `cinematography`

### Інше — 9
`image` (маршрутизація до зовнішніх генераторів) · `cold-email` (канал тесту) ·
`product-marketing-context` · `xlsx` · `docx` · `pptx` · `pdf` ·
`skill-creator` · `mcp-builder`

---

## Заархівовані — і чому

### Дублювали те, що лишилось (13)

| Скіл | Ким замінений |
|---|---|
| `hypothesis-tester` | `hypothesis-dossier` — той самий предмет, але з економікою, ризиками і kill-критеріями |
| `analytics` | `unit-economics-calc` — там скрипти замість прози |
| `data-tables` | те саме, ще й третій опис юніт-економіки |
| `design` | `design-system` — Brand DNA перенесено, додано токени й ефекти |
| `theme-factory` | `design-system` |
| `research` | `niche-research` + `competitor-intelligence` |
| `competitor-profiling` | `competitor-intelligence` (український, ваш власний) |
| `marketing` | `paid-ads` + `ad-creative` + `page-cro`, без хардкоду продукту |
| `content` | `copywriting` |
| `video` | `video-assembly` + `ai-video-prompts` |
| `marketing-ideas` | `niche-research` на вході циклу |
| `copy-editing` | `copywriting` |
| `site-architecture` (проєктний) | однойменний особистий, український — була пряма колізія імен |

### Передчасні — потрібні після першого клієнта, не до нього (12)
`churn-prevention` · `referral-program` · `email-sequence` · `onboarding-cro` ·
`paywall-upgrade-cro` · `signup-flow-cro` · `popup-cro` · `launch-strategy` ·
`directory-submissions` · `competitor-alternatives` · `content-strategy` · `lead-magnets`

Логіка: усі вони оптимізують те, що вже працює. У циклі, де 6 з 10 гіпотез
помирають на третій день, оптимізувати ще нічого.

### Повільніші за цикл (4)
`seo-audit` · `ai-seo` · `programmatic-seo` · `schema-markup`

SEO дає сигнал за 2-4 місяці. Це валідний канал для того, що вже вижило,
але він не може брати участь у перевірці за 7 днів.

### Поза профілем (5)
`aso-audit` (немає мобільних застосунків) · `revops` (немає відділу продажів) ·
`sales-enablement` (те саме) · `community-marketing` · `free-tool-strategy`

### Підтримка засновника, але не цикл (5)
`dev-management` · `tech-architecture` · `product-tech-decisions` ·
`no-code-automation` · `ai-workflow`

Ваші власні, добре написані. Але вони про управління розробкою й вибір стека —
це інший режим роботи. Повертайте адресно, коли будете будувати продукт,
що пройшов перевірку.

### Приклади Anthropic, не про вашу роботу (8)
`brand-guidelines` (це бренд-гайд Anthropic, не ваш) · `morning` · `internal-comms` ·
`slack-gif-creator` · `algorithmic-art` · `canvas-design` · `doc-coauthoring` ·
`web-artifacts-builder` · `session-start-hook`

### Мета-скіли, що створювали шум (2)
`prompt-engineer` · `model-advisor`

`model-advisor` вимагав спрацьовувати «на початку КОЖНОЇ відповіді» і не спрацював
жодного разу за сесію. Я звузив його опис, але цінність лишилась низькою:
він радить, якою моделлю робити задачу, коли модель уже обрано.

### Контент-конвеєр (1)
`content-pipeline` — операційна система публікацій для Symplexy. Потрібна,
коли ви ведете канал, а не коли перевіряєте гіпотези. Повертайте разом
з `social-content`, коли дійде до контент-маркетингу.

---

## Хардкод продукту

16 скілів мали «Symplexy» вшитим у текст. Це означало, що вони працювали
для одного продукту, а для решти — давали чужий контекст.

Ті, що лишились активними, переведені на `company/products.md` як єдине джерело.
**`company/products.md` треба заповнити** — інакше скіли працюють без контексту.
