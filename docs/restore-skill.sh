#!/usr/bin/env bash
# Повертає заархівований скіл в роботу.
#   bash docs/restore-skill.sh niche-research
#   bash docs/restore-skill.sh --list
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PERS_ARCHIVE="$HOME/.claude/skills-archive"
PERS_ACTIVE="$HOME/.claude/skills"

if [ "${1:-}" = "--list" ] || [ $# -eq 0 ]; then
  echo "Заархівовані проєктні (файли в .agents/skills, знято посилання):"
  for d in "$REPO"/.agents/skills/*/; do
    n=$(basename "$d"); [ -e "$REPO/.claude/skills/$n" ] || echo "  $n"
  done
  echo
  echo "Заархівовані особисті:"
  [ -d "$PERS_ARCHIVE" ] && ls -1 "$PERS_ARCHIVE" | sed 's/^/  /' || echo "  (порожньо)"
  exit 0
fi

S="$1"
if [ -d "$REPO/.agents/skills/$S" ]; then
  ln -sfn "../../.agents/skills/$S" "$REPO/.claude/skills/$S"
  echo "Повернуто проєктний скіл: $S"
elif [ -d "$PERS_ARCHIVE/$S" ]; then
  mv "$PERS_ARCHIVE/$S" "$PERS_ACTIVE/"
  echo "Повернуто особистий скіл: $S"
  echo "Якщо claude.ai пересинхронізує — перевір стан у веб-інтерфейсі."
else
  echo "Не знайдено: $S" >&2
  echo "Копія всіх особистих скілів: $REPO/.agents/personal-skills-backup/" >&2
  exit 1
fi
