# Аудит інструментів і встановлене

Дата: 2026-08-01

Підхід: спершу інвентаризація наявного, потім пошук прогалин, потім установка
**тільки під прогалини**. Нічого «про запас».

---

## Що вже було (83 скіли)

**Твої власні, user-level (~26):**
ai-video-models, ai-video-prompts, ai-workflow, analytics, cinematography,
competitor-intelligence, content, content-pipeline, data-tables,
decision-framework, design, dev-management, hypothesis-tester, marketing,
model-advisor, monetization, niche-research, no-code-automation,
product-tech-decisions, prompt-engineer, research, site-architecture,
site-builder, tech-architecture, ugc-creator, video-scriptwriter

**Вбудовані Anthropic (~17):**
algorithmic-art, brand-guidelines, canvas-design, doc-coauthoring, docx,
internal-comms, mcp-builder, morning, pdf, pptx, session-start-hook,
skill-creator, slack-gif-creator, theme-factory, web-artifacts-builder, xlsx

**У репо, від coreyhaines31 (40):** маркетинг, SEO, CRO, копірайтинг, email,
ціноутворення, конкуренти, аналітика.

---

## Прогалини

Перевірив усі 83 наявні проти каталогів wshobson (91 плагін / 175 скілів),
Ruflo (39), everything-claude-code, superpowers, офіційних Anthropic (13).

| # | Прогалина | Що покривало раніше | Закрито чим | Статус |
|---|---|---|---|---|
| 1 | Памʼять між сесіями | **нічого** | claude-mem | 📋 локально |
| 2 | Браузер, реальний веб | **нічого** | Playwright MCP | ✅ в репо |
| 3 | Платформи як джерела даних | **нічого** | Agent-Reach | 📋 локально |
| 4 | Оркестрація команди агентів | **нічого** | agent-teams (3 скіли) | ✅ в репо |
| 5 | Самопокращення скілів | skill-creator — лише створення | task-observer | ✅ в репо |
| 6 | Поведінкова дисципліна | model-advisor — лише вибір моделі | karpathy-guidelines | ✅ в репо |
| 7 | Моніторинг змін у часі | **нічого** | — | ⚠️ див. нижче |

---

## ✅ Встановлено в репо

Працює одразу після `git pull`. Перевірено: усі 5 скілів підхопились системою.

**task-observer** — `rebelytics/one-skill-to-rule-them-all`, CC BY 4.0
Дивиться, як ідe робота, ловить твої виправлення й перетворює їх на правки
скілів. Активується автоматично через `CLAUDE.md`.

**karpathy-guidelines** — `forrestchang/andrej-karpathy-skills`, MIT
Не вгадувати, не ховати сумніви, показувати компроміси, мінімум зайвого.

**team-composition-patterns** — `wshobson/agents`, MIT
Скільки агентів запускати, які ролі, який `subagent_type` під кожну.

**task-coordination-strategies** — `wshobson/agents`, MIT
Розбиття складної задачі, граф залежностей, балансування навантаження.

**team-communication-protocols** — `wshobson/agents`, MIT
Як агенти обмінюються повідомленнями, узгодження плану, коректне завершення.

**Playwright MCP** — `.mcp.json`
Конфіг у репо. Один раз підтвердити підключення при першому запуску.

**CLAUDE.md** — правила: активація task-observer, дисципліна, мова, контекст проєктів.

---

## 📋 Доставити з компʼютера

Детальні команди — у `SETUP-LOCAL.md`.

1. **claude-mem** — `npx claude-mem install` — памʼять між сесіями
2. **Agent-Reach** — `pip install agent-reach && agent-reach install` — 13 платформ
3. **Ruflo** — рішення відкладене, аргументи у файлі

---

## ⏭️ Свідомо пропущено

| Що | Причина |
|---|---|
| superpowers | TDD/кодинг. `decision-framework` + `hypothesis-tester` покривають для нетехнічних задач |
| everything-claude-code | Конфіги під кодинг, ризик конфліктів із 83 скілами |
| claude-subconscious | Платний акаунт Letta, дублює claude-mem |
| impeccable | Дизайн закритий: `design`, `site-builder`, `theme-factory` |
| claude-squad | Локальний tmux-сетап; `agent-teams` закриває нативно |
| Ruflo: v3-*, flow-nexus-*, agentdb-* (18 скілів) | Внутрішня розробка claude-flow або привʼязка до хмарної платформи |
| wshobson: SEO, content-marketing, business-analytics (6 плагінів) | Повний дубль твоїх 40 маркетингових скілів |
| wshobson: ~75 плагінів під кодинг | Не твій профіль |
| multi-reviewer-patterns | Заточений під код-рев'ю |

---

## ⚠️ Знайдені проблеми

**Ruflo не можна розібрати на частини.** Swarm-скіли — обгортки над власним
MCP-стеком: `hooks-automation` 116 посилань, `sparc-methodology` 94,
`swarm-advanced` 80, `verification-quality` 73. Скопійовані окремо — зламані.
Або вся платформа (`npx ruflo init`, 314 MCP-інструментів), або нічого.

**Посилання у вихідному завданні було невірне.** `steipete/superpowers` → 404.
Справжній репозиторій — `obra/superpowers`.

**Дані про зірки застаріли.** Усі репозиторії виросли: superpowers 148K→~265K,
awesome-claude-code 28.5K→51.4K, wshobson 25K→38.4K, agent-reach 29K→63.6K.
На вибір це не вплинуло.

**Agent-Reach має багато форків-клонів** з ідентичним описом. Канонічний —
`Panniantong/Agent-Reach`.

---

## 🎯 Три швидкі перемоги для LLM Visibility

**1. claude-mem — постав першим.**
LLM Visibility це моніторинг у часі. Без памʼяті кожна перевірка — окремий
знімок без порівняння з попереднім. Памʼять перетворює знімки на динаміку.

**2. Playwright MCP + Agent-Reach — руки для збору даних.**
Зараз агент фізично не може відкрити сторінку. Ці два дають доступ до сайтів
і до X/Reddit/YouTube — саме там видно, як бренд згадують.

**3. agent-teams — паралельний збір.**
Перевірка видимості по 5 темах × 4 моделях послідовно займе години.
Команда агентів робить це паралельно.

---

## ⚠️ Прогалина №7 — не закрита нічим готовим

Немає скіла під **«відстежувати X у часі й помічати зміни»** — ні в наявних 83,
ні в жодному з перевірених каталогів. А це ядро LLM Visibility.

Готового рішення не існує. Треба писати свій скіл: формат замірів, база
порівняння, поріг «що вважати зміною», формат звіту про зсув.

Це наступний крок, якщо скажеш.
