#!/usr/bin/env bash
# SessionStart: вливає стан цифрової компанії в контекст на старті сесії.
# Вивід цього хука потрапляє прямо в контекст моделі — тому він короткий і фактичний.
#
# Розгалужується за source (startup|resume|clear|compact|fork):
#   startup/clear — повний брифінг компанії
#   resume/fork   — коротко: де спинились (ACTIVE.md), без повторення брифінгу
#   compact       — лише активний стан: після стиснення втрачається середина розмови,
#                   а не опис штату, який і так у CLAUDE.md
set -uo pipefail
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$ROOT" ] && exit 0
cd "$ROOT" 2>/dev/null || exit 0
[ -d .claude/agents ] || exit 0   # не компанія — мовчимо

# --- source зі stdin ---
IN=$(cat 2>/dev/null || echo '{}')
SRC=$(printf '%s' "$IN" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("source","startup"))
except Exception: print("startup")' 2>/dev/null || echo startup)

ACTIVE="company/workspace/ACTIVE.md"
LOOPS="company/workspace/OPEN-LOOPS.md"

# --- чи не застарів записаний стан ---
# Памʼять переживає сесію, стан виконання — ні. Стан тижневої давнини описує світ,
# якого може вже не бути; продовжувати його як поточний — діяти наосліп.
print_stale() {
  [ -f "$ACTIVE" ] || return 0
  D=$(grep -m1 '^\*\*Оновлено:\*\*' "$ACTIVE" 2>/dev/null | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}') || return 0
  [ -z "$D" ] && return 0
  AGE=$(python3 -c 'import sys,datetime
try:
    d=datetime.date.fromisoformat(sys.argv[1]); print((datetime.date.today()-d).days)
except Exception: print(0)' "$D" 2>/dev/null || echo 0)
  [ "${AGE:-0}" -ge 7 ] || return 0
  case "$((AGE % 100))" in
    1[1-4]) DW="днів";;
    *) case "$((AGE % 10))" in 1) DW="день";; 2|3|4) DW="дні";; *) DW="днів";; esac;;
  esac
  echo "⚠ Активний стан не оновлювався $AGE $DW (з $D)."
  echo "  Звір із фактами до продовження. Дозволи, видані в попередніх сесіях, НЕ діють —"
  echo "  памʼять відновлює знання, не повноваження (source-of-truth.md)."
  echo
}

# --- активний стан: друкуємо, лише якщо задача справді є ---
print_active() {
  [ -f "$ACTIVE" ] || return 1
  grep -q '^\*\*Задача:\*\* немає' "$ACTIVE" 2>/dev/null && return 1
  echo "=== АКТИВНА ЗАДАЧА (company/workspace/ACTIVE.md) ==="
  sed -n '/^## Задача/,/^## Як заповнювати/p' "$ACTIVE" \
    | sed '/^## Як заповнювати/d; /^---$/d; /^<!--/,/-->/d'
  echo "Звір цей стан проти фактів (git status, файли), перш ніж діяти далі."
  echo "Ієрархія джерел правди — company/protocols/source-of-truth.md"
  return 0
}

# --- відкриті контури: живуть довше за задачу, тому окремо від ACTIVE.md ---
# Друкуємо лише назви й стани: деталі працівник прочитає у файлі, якщо дійде до них.
print_loops() {
  [ -f "$LOOPS" ] || return 0
  OUT=$(sed -n '/^## Відкриті/,/^## Закриті/p' "$LOOPS" 2>/dev/null \
        | awk '/^### /{name=substr($0,5)} /^\*\*Стан:\*\*/{st=$0; sub(/^\*\*Стан:\*\* /,"",st); if(name!=""){printf "  · %s — %s\n", name, st; name=""}}')
  [ -z "$OUT" ] && return 0
  N=$(printf '%s\n' "$OUT" | wc -l | tr -d ' ')
  echo "=== ВІДКРИТІ КОНТУРИ: $N (company/workspace/OPEN-LOOPS.md) ==="
  printf '%s\n' "$OUT"
  echo "Це не поточна задача — це те, що не можна загубити. Закривати тільки з причиною."
  echo
}

# --- відставання від віддаленого (правда на віддаленому, не в контейнері) ---
print_behind() {
  git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1 || return 0
  BEHIND=$(git rev-list --count HEAD..'@{u}' 2>/dev/null || echo 0)
  [ "${BEHIND:-0}" -gt 0 ] || return 0
  echo "⚠ Локальна копія відстала від віддаленої на $BEHIND комітів."
  echo "  Виконай:  git pull --ff-only    (правда — на віддаленому, не в контейнері)"
  echo
}

# ---------- короткі гілки ----------
case "$SRC" in
  compact)
    echo "=== ПІСЛЯ СТИСНЕННЯ КОНТЕКСТУ ==="
    echo "Середину розмови стиснуто. Штат і правила лишаються в CLAUDE.md — не перечитуй їх заново."
    echo "Звір, чи не втрачено ціль поточної роботи:"
    echo
    print_active || echo "Активної задачі не зафіксовано (company/workspace/ACTIVE.md порожній)."
    echo
    print_loops
    exit 0
    ;;
  resume|fork)
    if [ "$SRC" = fork ]; then echo "=== ПРОДОВЖЕННЯ (гілка сесії) ==="; else echo "=== ПРОДОВЖЕННЯ СЕСІЇ ==="; fi
    echo "Це не нова сесія — компанія та її правила вже описані в CLAUDE.md."
    echo
    print_behind
    print_stale
    print_active || echo "Активної задачі не зафіксовано — спитай засновника, над чим працюємо."
    echo
    print_loops
    exit 0
    ;;
esac

# ---------- повний брифінг: startup | clear | інше ----------
BR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
N=$(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
MEMF=$(find .claude/agent-memory -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
LES=$(grep -rhc '^## 20' .claude/agent-memory/*/lessons.md 2>/dev/null | awk '{s+=$1} END{print s+0}')
# рахуємо ЛИШЕ реальні записи, не шаблонні заголовки
PLAY=$(grep -rh '^## ' .claude/agent-memory/*/playbook.md 2>/dev/null | grep -v 'Назва процедури' | wc -l | tr -d ' ')
case "$((N % 100))" in
  1[1-4]) WORD="працівників";;
  *) case "$((N % 10))" in 1) WORD="працівник";; 2|3|4) WORD="працівники";; *) WORD="працівників";; esac;;
esac

echo "=== ЦИФРОВА КОМПАНІЯ: $N $WORD ==="
echo "Це не звичайний репозиторій. Тут постійний штат із памʼяттю. Штат УЖЕ ІСНУЄ —"
echo "не створюй його заново і не виконуй профільну роботу сам, якщо для неї є працівник."
echo

print_behind

echo "Штат:     .claude/agents/ — виклик через Agent(subagent_type: <slug>)"
echo "Реєстр:   company/ROSTER.md — хто є і кого коли кликати"
echo "Правила:  CLAUDE.md · протоколи в company/protocols/"
echo "Правда:   company/protocols/source-of-truth.md — що перемагає при суперечності"
echo "Команди:  /team · /team-training · /team-retro · /audit"
if [ "$LES" = "0" ] && [ "$PLAY" = "0" ]; then
  echo "Памʼять:  $MEMF файлів, але ЩЕ ПОРОЖНЯ — команда не працювала над реальними задачами."
  echo "          Уроки й процедури зʼявляться після першої роботи. Це нормально."
else
  echo "Памʼять:  $MEMF файлів · уроків: $LES · перевірених процедур: $PLAY"
fi

# активні проєкти + чи заповнений контекст
if [ -d company/projects ]; then
  for p in company/projects/*/; do
    [ -d "$p" ] || continue
    name=$(basename "$p")
    fc="${p}founder-context.md"
    if [ -f "$fc" ] && ! grep -q "не заповнювався" "$fc" 2>/dev/null; then
      echo "Проєкт:   $name — контекст заповнений"
    else
      echo "Проєкт:   $name — ⬜ КОНТЕКСТ НЕ ЗАПОВНЕНИЙ ($fc)"
      echo "          Поки він порожній, працівники не знають бізнесу засновника."
      echo "          Запропонуй засновнику заповнити його перед серйозною роботою."
    fi
  done
fi

echo
print_stale
print_active && echo
print_loops

echo "Спочатку прочитай: CLAUDE.md → company/ROSTER.md → company/protocols/orchestration.md"
echo "Гілка: $BR (компанія є на main, на гілці за замовчуванням і на робочій)"
echo "Мова спілкування із засновником — українська."
exit 0
