#!/usr/bin/env bash
# SessionStart: вливає стан цифрової компанії в контекст на старті кожної сесії.
# Вивід цього хука потрапляє прямо в контекст моделі — тому він короткий і фактичний.
set -uo pipefail
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$ROOT" ] && exit 0
cd "$ROOT" 2>/dev/null || exit 0
[ -d .claude/agents ] || exit 0   # не компанія — мовчимо

BR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
N=$(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
MEMF=$(find .claude/agent-memory -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
LES=$(grep -rhc '^## 20' .claude/agent-memory/*/lessons.md 2>/dev/null | awk '{s+=$1} END{print s+0}')
# рахуємо ЛИШЕ реальні записи, не шаблонні заголовки
PLAY=$(grep -rh '^## ' .claude/agent-memory/*/playbook.md 2>/dev/null | grep -v 'Назва процедури' | wc -l | tr -d ' ')
case "$N" in *1) [ "$N" = 11 ] && WORD="працівників" || WORD="працівник";; *2|*3|*4) WORD="працівники";; *) WORD="працівників";; esac

echo "=== ЦИФРОВА КОМПАНІЯ: $N $WORD ==="
echo "Це не звичайний репозиторій. Тут постійний штат із памʼяттю. Штат УЖЕ ІСНУЄ —"
echo "не створюй його заново і не виконуй профільну роботу сам, якщо для неї є працівник."
echo

# Компанія є (перевірено вище). Попереджаємо не про назву гілки, а про реальну проблему:
# локальна копія відстала від віддаленої — таке вже траплялось і коштувало плутанини.
if git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
  BEHIND=$(git rev-list --count HEAD..'@{u}' 2>/dev/null || echo 0)
  if [ "${BEHIND:-0}" -gt 0 ]; then
    echo "⚠ Локальна копія відстала від віддаленої на $BEHIND комітів."
    echo "  Виконай:  git pull --ff-only    (правда — на віддаленому, не в контейнері)"
    echo
  fi
fi

echo "Штат:     .claude/agents/ — виклик через Agent(subagent_type: <slug>)"
echo "Реєстр:   company/ROSTER.md — хто є і кого коли кликати"
echo "Правила:  CLAUDE.md · протоколи в company/protocols/"
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
echo "Спочатку прочитай: CLAUDE.md → company/ROSTER.md → company/protocols/orchestration.md"
echo "Гілка: $BR (компанія є на main, на гілці за замовчуванням і на робочій)"
echo "Мова спілкування із засновником — українська."
exit 0
