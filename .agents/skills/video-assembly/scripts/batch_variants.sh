#!/usr/bin/env bash
# Пакетна збірка варіантів креативу: кожен хук + спільне тіло + спільна кінцівка.
# Саме так тестуються креативи: змінюється ОДНА змінна (перші 3 секунди).
#
#   bash batch_variants.sh hooks/ body.mp4 cta.mp4 out/ [9x16]
#
# hooks/ — тека з hook-кліпами. Ім'я файлу стає ім'ям варіанта.

set -euo pipefail

HOOKS_DIR="${1:?вкажи теку з хуками}"
BODY="${2:?вкажи body.mp4}"
CTA="${3:?вкажи cta.mp4}"
OUT_DIR="${4:?вкажи теку виводу}"
FORMAT="${5:-9x16}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$OUT_DIR"

shopt -s nullglob
hooks=("$HOOKS_DIR"/*.mp4)
if [ ${#hooks[@]} -eq 0 ]; then
  echo "У $HOOKS_DIR немає .mp4 файлів" >&2
  exit 1
fi

echo "Збираю ${#hooks[@]} варіантів у форматі $FORMAT"
i=0
for hook in "${hooks[@]}"; do
  i=$((i+1))
  name="$(basename "$hook" .mp4)"
  out="$OUT_DIR/${name}_${FORMAT}_v${i}.mp4"
  echo "  [$i/${#hooks[@]}] $name -> $(basename "$out")"
  python3 "$SCRIPT_DIR/assemble.py" \
    --clips "$hook" "$BODY" "$CTA" \
    --out "$out" --format "$FORMAT"
done

echo
echo "Готово: $i варіантів у $OUT_DIR"
echo "Далі: заливай у кабінет з ТИМИ Ж назвами, інакше не прочитаєш результати."
