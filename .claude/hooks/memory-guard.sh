#!/usr/bin/env bash
# Stop-хук цифрової компанії.
# 1) ліміт MEMORY.md (200 рядків — технічний ліміт вшивання в промпт)
# 2) скан секретів у пам'яті (вона комітиться в git)
# 3) автокоміт+пуш пам'яті, щоб вона не зникла з контейнером
set -uo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$ROOT" ] && exit 0
cd "$ROOT" 2>/dev/null || exit 0
[ -d .claude/agent-memory ] || exit 0

WARN=""

# --- 1. ліміт MEMORY.md ---
OVER=""
while IFS= read -r f; do
  n=$(wc -l < "$f" 2>/dev/null || echo 0)
  [ "$n" -ge 200 ] && OVER="${OVER}$(basename "$(dirname "$f")") ($n) "
done < <(find .claude/agent-memory -name MEMORY.md 2>/dev/null)
[ -n "$OVER" ] && WARN="${WARN}MEMORY.md перевищив 200 рядків: ${OVER}— почисти, інакше хвіст не потрапить у промпт. "

# --- 2. секрети в пам'яті ---
SECRETS=$(grep -rIinE \
  'sk-ant-[A-Za-z0-9_-]{20}|hf_[A-Za-z0-9]{30}|gh[pousr]_[A-Za-z0-9]{30}|github_pat_[A-Za-z0-9_]{30}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{32}|sk_(live|test)_[A-Za-z0-9]{20}|xox[baprs]-[A-Za-z0-9-]{10}|AIza[0-9A-Za-z_-]{35}|glpat-[A-Za-z0-9_-]{20}|BEGIN [A-Z ]*PRIVATE KEY|(api[_-]?key|secret|passwd|password|token|credential)[a-z_]*["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9_/+=-]{24}' \
  .claude/agent-memory company .claude/settings.json 2>/dev/null | head -5)
[ -n "$SECRETS" ] && WARN="${WARN}УВАГА: схоже на секрет у пам'яті (вона комітиться в git): $(echo "$SECRETS" | cut -c1-160 | tr '\n' ' '). Прибери і зроти ключ. "

# --- 3. автокоміт + пуш пам'яті ---
COMMITTED=""
if [ -n "$(git status --porcelain .claude/agent-memory company 2>/dev/null)" ]; then
  if [ -z "$SECRETS" ]; then
    BR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    git add .claude/agent-memory company >/dev/null 2>&1
    if git commit -q -m "memory: автозбереження пам'яті працівників

Автоматичний коміт Stop-хука. Пам'ять живе лише в git — контейнер ефемерний.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" >/dev/null 2>&1; then
      COMMITTED="пам'ять збережено в git"
      if git push -q origin "$BR" >/dev/null 2>&1; then
        COMMITTED="$COMMITTED і запушено ($BR)"
        # Дзеркала: компанія має бути видима з будь-якої гілки, інакше нова сесія
        # побачить застарілу памʼять. Звичайний (не force) push — якщо гілка
        # розійшлась, він просто не пройде і нічого не зіпсує.
        MIRRORED=""
        for M in main claude/add-marketing-skills-6gIws; do
          [ "$M" = "$BR" ] && continue
          git push -q origin "HEAD:$M" >/dev/null 2>&1 && MIRRORED="$MIRRORED $M"
        done
        [ -n "$MIRRORED" ] && COMMITTED="$COMMITTED; синхронізовано:$MIRRORED"
      else
        COMMITTED="$COMMITTED, але пуш не пройшов — запуш вручну"
      fi
    fi
  else
    WARN="${WARN}Автокоміт пам'яті пропущено через підозру на секрет. "
  fi
fi

MSG=""
[ -n "$WARN" ] && MSG="$WARN"
[ -n "$COMMITTED" ] && MSG="${MSG}${COMMITTED}."
[ -z "$MSG" ] && exit 0

python3 -c 'import json,sys; print(json.dumps({"systemMessage": sys.argv[1]}))' "$MSG" 2>/dev/null || true
exit 0
