# Тех-завдання людині-розробнику

**Не плутати з `task-brief.md`.** Той — для наших 21 працівника. Цей — для **живих
розробників** у команді засновника.

| | `task-brief.md` | `dev-handoff.md` |
|---|---|---|
| Кому | працівник-агент | людина-розробник |
| Мова | українська | **англійська** |
| Читач | має памʼять і протоколи | має тільки цей документ |
| Формат задає | ми | **засновник** — див. нижче |

## Правило

Коли артефакт призначений розробнику — **виводимо в цьому форматі за замовчуванням**,
не питаючи. Це пряма вказівка засновника (профіль, 2026-08-02).

**Англійською.** Українська — для стратегії й розмови із засновником; усе, що йде
команді розробників, — англійською.

---

## Формат

Пʼять обовʼязкових блоків. Порядок фіксований.

```markdown
## What to build
<Feature or change description. Concrete, no ambiguity.>

## Why
<Business context. ONE sentence.>

## Acceptance criteria
- [ ] <verifiable condition>
- [ ] <verifiable condition>

## Edge cases
- <case> → <expected behavior>

## Files / components affected
- `path/to/file` — <what changes>
```

`Files / components affected` — якщо відомо. Не знаємо — пишемо `Unknown — investigate first`,
а не вигадуємо шляхи.

---

## Що робить це завдання придатним

**Критерії приймання перевіряються, а не оцінюються.**

| Погано | Добре |
|---|---|
| `Search should work well` | `Query with 0 results shows empty state, not a spinner` |
| `Make it fast` | `Category page renders under 1s on 3G throttling` |
| `Handle errors` | `API 500 → toast with retry button; input stays filled` |

**Крайні випадки — половина цінності документа.** Саме вони вертаються багами через
тиждень. Мінімум, який називаємо завжди: порожньо · дуже багато · немає мережі ·
немає прав · подвійний клік · дані з іншої мови або розкладки.

**Одне завдання — одна зміна.** Дві незалежні речі — два документи. Інакше приймання
стає неможливим: половина зроблена, половина ні, статус незрозумілий.

**Ніякого «і взагалі подивись там».** Обсяг названий явно; що поза обсягом — окремим
рядком `Out of scope:`.

---

## Приклад

```markdown
## What to build
Add empty-state handling to the tools catalog search.

## Why
Users searching narrow queries hit a blank page and bounce.

## Acceptance criteria
- [ ] Zero results → message + 3 suggested popular categories
- [ ] Search under 2 chars → no request fired, hint shown instead
- [ ] Loading state visually distinct from empty state
- [ ] Works on mobile viewport (360px)

## Edge cases
- Query with only spaces → treat as empty input, no request
- Non-Latin query (Cyrillic) → normal search path, no crash
- Slow API (>3s) → skeleton, not spinner; no layout shift

## Files / components affected
- Unknown — investigate first

## Out of scope
- Search ranking algorithm
- Analytics events
```

---

## Перед тим як віддати

- [ ] Кожен критерій приймання **перевіряється** — можна відповісти «так» або «ні»
- [ ] «Why» вкладається в одне речення
- [ ] Крайні випадки названі, а не «обробити помилки»
- [ ] Обсяг закритий — є `Out of scope`, якщо є що виключати
- [ ] Англійською
- [ ] Немає припущень про реалізацію там, де ми її не знаємо

---

## Хто це складає

Зазвичай `fullstack-engineer` або `principal-architect` — вони перекладають рішення
в технічні вимоги. Оркестратор перевіряє формат перед передачею засновнику.

Засновник **керує результатами, а не кодом** — тому документ описує, **що має бути
правдою після зміни**, а не як це реалізувати. Рішення про реалізацію лишається
розробнику, якщо немає окремої вимоги.
