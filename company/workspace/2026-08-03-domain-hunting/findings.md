# Знахідки

**Автор:** ai-engineer (Кай Ямамото) · **Дата:** 2026-08-03

## 1. Перевірені факти з джерелами

| Факт | Джерело |
|---|---|
| WHOIS для gTLD офіційно виведено з експлуатації 28.01.2025; RDAP — обов'язковий джерело реєстраційних даних. Виняток: .com, .name, .post ще зобов'язані тримати WHOIS. До вересня 2025 374 gTLD вимкнули WHOIS повністю | icann.org/en/announcements/details/icann-update-launching-rdap-sunsetting-whois-27-01-2025-en |
| ICANN CZDS: будь-хто може подати заявку на доступ до зон-файлів gTLD; доступ мінімум на 3 місяці, викачка раз на 24 год; зони оновлюються 00:00–06:00 UTC | icann.org/resources/pages/zfa-2013-06-28-en · czds.icann.org/help |
| Verisign направляє за .com/.net саме в CZDS | verisign.com/resources/zone-file/ |
| Клієнти CZDS з відкритим кодом: pyCZDS (PyPI), acidvegas/czds (GitHub), pogzyb/czdsdump | pypi.org/project/pyCZDS/ · github.com/acidvegas/czds |
| ExpiredDomains.net — безкоштовні щоденні списки для 676 TLD, включно з pending-delete; веде Marco Schmidt | expireddomains.net |
| Drop-catchers для .com: DropCatch (мережа 1000+ реєстраторів), SnapNames, Gname; при кількох претендентах — публічний аукціон | domcop.com/blog/guide-to-domain-drop-catching/ |
| MCP-сервер `domain-search-mcp` (MIT, npm): 12 tools, ланцюг RDAP → GoDaddy → WHOIS, **ключі не потрібні** для перевірки доступності | github.com/dorukardahan/domain-search-mcp (заявa README, незалежно не перевіряв) |
| Instant Domain Search MCP: без автентифікації, без API-ключів, працює з Claude/ChatGPT/Cursor | instantdomainsearch.com/mcp (сторінка недоступна для WebFetch — з витягу пошуку) |
| Namecheap API безкоштовний, але вимагає $50 балансу АБО 20+ доменів на акаунті; ліміт 700 викликів/хв; метод `namecheap.domains.check` | blogzenn.com/namecheap-api-setup-and-pricing-guide-2026/ |
| WhoisJSON — 1000 безкоштовних запитів/міс без картки | whoisjson.com/blog/best-domain-availability-api |
| Готові n8n-шаблони: «Domain availability monitor with Porkbun, Google Sheets & multi-channel alerts» (перевірка кожні 30 хв, алерти Gmail+Discord), «Namesilo bulk domain availability checker» (батчі + Excel) | n8n.io/workflows/10378-... · n8n.io/workflows/3047-... |
| .AI: з січня 2025 реєстр веде Identity Digital; з 5 березня 2026 оптова ціна +$10/рік = +$20 на 2-річну транзакцію, до $160 за 2 роки (+14%); роздріб ~$84/рік, мінімум 2 роки | domainnamewire.com/2026/02/02/ai-domain-name-prices-going-up-20/ · x.com/Porkbun/status/2018844641500836292 |
| .io: договір UK–Маврикій підписано 22.05.2025; ICANN описує ризик вилучення коду IO зі списку ISO 3166-1 і подальшу 5-річну процедуру виводу; станом на 2026 угоду призупинено, статус невизначений | icann.org/en/blogs/details/the-chagos-archipelago-and-the-io-domain-14-11-2024-en · webstacks.com/blog/is-the-end-of-io-domains-near |
| Ціни моделей Claude (скіл `claude-api`, кеш 2026-06-24): Haiku 4.5 $1/$5 за 1M; Sonnet 5 $3/$15 (інтро $2/$10 до 2026-08-31); Opus 5 $5/$25. Batch API = −50% | скіл `claude-api` |

## 2. Що працює в цьому середовищі (перевірено)

- **Сирий DNS UDP/53 на 8.8.8.8 і 1.1.1.1 — працює.** Запит NS, RCODE=3 (NXDOMAIN) на обох резолверах = делегування немає.
  Контроль: `google.com/anthropic.com/openai.com/elevenlabs.io/perplexity.ai` → rc=0, an≥2 (TAKEN);
  `zzqq9x7blorptv.{com,ai,io}` → rc=3, an=0 (FREE?).
- Скрипт: `/tmp/claude-0/.../scratchpad/domcheck.py` (наведений повністю у звіті).
- Перевірено 398 доменів за 3 прогони, ~21 с на 180 доменів у 12 потоків.

## 3. Що НЕ працює (dead ends, дослівно)

1. **`whois` і `dig` відсутні** у контейнері:
   `which dig` → порожньо; `whois google.com` → `timeout: failed to run command 'whois': No such file or directory`.
2. **RDAP-хости заблоковані egress-політикою проксі:**
   `curl https://rdap.verisign.com/com/v1/domain/google.com` → `curl: (56) CONNECT tunnel failed, response 403`;
   статус проксі: `{"kind":"connect_rejected","detail":"gateway answered 403 to CONNECT (policy denial or upstream failure)","host":"rdap.verisign.com:443"}`.
   Так само 000/403: `dns.google/resolve`, `cloudflare-dns.com/dns-query`, `rdap.org`, `api.domainsdb.info`, `instantdomainsearch.com`, `domainr.com`.
3. **WebFetch на rdap.org / instantdomainsearch.com/mcp / n8n.io/workflows/... → HTTP 403.** WebSearch працює, WebFetch — вибірково (github.com пройшов).
4. **Пряме опитування авторитетних NS реєстру не вдалось — трафік порт 53 перехоплюється.**
   Доказ: `google.com NS @192.5.6.30 RD=0` повертає `rcode=0 AA=0 an=4` — справжній gTLD-сервер віддав би referral в AUTHORITY з AA=1, а не ANSWER без AA. І `@8.8.8.8 RD=0` → `rcode=2` (SERVFAIL), типова поведінка кеш-резолвера. Висновок: усі UDP/53 назовні NAT-яться на один рекурсивний резолвер. Перевірка на рівні реєстру в цьому середовищі **неможлива**.
5. **SERVFAIL (rc=2) як стійкий стан** у 4 доменів (`obsidara.com`, `mirovane.com`, `digitalcoworkers.ai`, `evalops.io`, `lunaro.io`) — повторний прогін дав те саме. Це НЕ «вільний», це «невизначено» (найімовірніше — збій DNSSEC-валідації батьківської зони або NS домену).
6. **`workerroster.*` відкинуто попри вільність:** існує активний бренд **AgentRoster** (agentroster.ai — «Hire AI Digital Employees»), назва плутається. Джерело: agentroster.ai.
7. **`cyprano.*` понижено:** зайнятий соцхендл — `instagram.com/cyprano`, виконавець на Apple Music/SoundCloud. DNS вільний, але соцмережі — ні.

## 4. Числа

- 398 перевірок DNS, з них 118 «FREE?» · 275 «TAKEN» · 5 «UNCLEAR/NO-ANSWER».
- .com зайнятий майже суцільно: з 60 імен першого батчу вільним у .com було 1 (`workercrew.com`).
- Вартість пайплайну (розрахунок у звіті): $0.014/прогін на Haiku 4.5, $0.042 на Sonnet 5. Тижнево → $0.06 / $0.18 на місяць.

## 5. Для наступного в ланцюгу

- Якщо треба **юридично достовірна** перевірка — потрібен вихід на RDAP (`rdap.verisign.com`, `rdap.org`) або ключ реєстратора. Зараз обидва шляхи закриті політикою egress. Питання до `security-engineer`/оркестратора: чи можна додати ці хости в allowlist.
- Рішення «який домен купити» НЕ приймалось — це рішення засновника.
