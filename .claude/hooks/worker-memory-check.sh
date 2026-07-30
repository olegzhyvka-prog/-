#!/usr/bin/env bash
# SubagentStop-хук: працівник завершив роботу — чи оновив він пам'ять?
# Правило компанії: робота не завершена, поки пам'ять не оновлена.
set -uo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$ROOT" ] && exit 0
cd "$ROOT" 2>/dev/null || exit 0
[ -d .claude/agent-memory ] || exit 0

IN=$(cat 2>/dev/null || echo '{}')
SID=$(printf '%s' "$IN" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("session_id","x"))' 2>/dev/null || echo x)
STATE="/tmp/.claude-mem-${SID}"

NOW=$(git status --porcelain .claude/agent-memory 2>/dev/null | md5sum | cut -d' ' -f1)
PREV=$(cat "$STATE" 2>/dev/null || echo "")
printf '%s' "$NOW" > "$STATE"

# перший запуск у сесії — нема з чим порівнювати
[ -z "$PREV" ] && exit 0
[ "$NOW" != "$PREV" ] && exit 0

python3 -c 'import json;print(json.dumps({"systemMessage":"Працівник завершив роботу, не змінивши жодного файлу памʼяті. За company/protocols/definition-of-done.md робота не вважається завершеною: урок → lessons.md, процедура → playbook.md, факти бізнесу → projects/<проєкт>/state.md. Поверни працівника на доопрацювання або зафіксуй памʼять сам.","hookSpecificOutput":{"hookEventName":"SubagentStop","additionalContext":"Памʼять працівника не оновлена після запуску. Перевір, чи це порушення протоколу памʼяті, і виправ до звіту засновнику."}}))' 2>/dev/null || true
exit 0
