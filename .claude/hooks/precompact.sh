#!/usr/bin/env bash
# PreCompact: контекст зараз стиснеться і середина розмови зникне.
#
# Це головне місце тихої втрати роботи. Після обриву сесії видно, що сесія нова.
# Після стиснення ззовні не змінюється нічого — модель просто перестає памʼятати
# середину і продовжує працювати, вважаючи, що все знає.
#
# Хук нічого не блокує. Він нагадує зафіксувати стан у ACTIVE.md ДО стиснення,
# щоб SessionStart(source=compact) міг влити його назад.
set -uo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$ROOT" ] && exit 0
cd "$ROOT" 2>/dev/null || exit 0
[ -d .claude/agents ] || exit 0   # не компанія — мовчимо

ACTIVE="company/workspace/ACTIVE.md"

# Чи є незакомічена робота — її треба зберегти незалежно від стиснення
DIRTY=""
[ -n "$(git status --porcelain company .claude 2>/dev/null)" ] && DIRTY="так"

if [ -f "$ACTIVE" ] && ! grep -q '^\*\*Задача:\*\* немає' "$ACTIVE" 2>/dev/null; then
  MSG="Контекст стискається. Активна задача зафіксована в $ACTIVE — перевір, що там актуальний крок і повний розділ «Незворотне вже зроблене», бо після стиснення памʼять про це лишиться тільки у файлі."
else
  MSG="Контекст стискається, а $ACTIVE порожній. Якщо зараз виконується задача — запиши в нього поточний крок, зроблене і незворотні дії ДО стиснення. Інакше після нього ці факти не відновити."
fi

[ -n "$DIRTY" ] && MSG="$MSG Є незакомічені зміни в company/ або .claude/."

python3 -c 'import json,sys
print(json.dumps({
  "systemMessage": sys.argv[1],
  "hookSpecificOutput": {
    "hookEventName": "PreCompact",
    "additionalContext": "Перед стисненням: зафіксуй у company/workspace/ACTIVE.md поточний крок, що вже зроблено і які незворотні дії виконані. Після стиснення середина розмови буде недоступна — джерелом правди стане цей файл."
  }
}))' "$MSG" 2>/dev/null || true
exit 0
