#!/usr/bin/env python3
"""
Шукає в документі числа без джерела — тобто потенційно вигадані.

Це не стиль, а структурна перевірка: людина (і модель) не можуть надійно
пам'ятати про дисципліну джерел на 400 рядках. Скрипт може.

  python3 check_numbers.py company/hypotheses/2026-08-01-x/DOSSIER.md
  python3 check_numbers.py --strict landing/index.html    # ненульовий код виходу

Тег має стояти В ТОМУ САМОМУ РЯДКУ, що й число — інакше незрозуміло,
до якого саме числа він належить. Допустимі теги:
  [ФАКТ: <звідки>]      виміряно/отримано з інструмента чи кабінету
  [ОЦІНКА: <як>]        порахували ми, видно з чого
  [ПРИПУЩЕННЯ]          взяли зі стелі свідомо, підлягає перевірці
  [ДЕМО]                вигадано для прикладу, у реальні документи не переносити
  НЕВІДОМО              даних немає і ми це визнаємо
Або посилання на джерело: (Semrush, 2026-07) · джерело: · за даними
"""
import argparse
import re
import sys

TAGS = re.compile(
    r'\[(?:ФАКТ|ОЦІНКА|ПРИПУЩЕННЯ|ДЕМО|FACT|ESTIMATE|ASSUMPTION|DEMO)[:\]]'
    r'|НЕВІДОМО|UNKNOWN'
    r'|джерело\s*:|за даними|source\s*:'
    r'|\((?:[^)]*\b(?:Semrush|PostHog|Stripe|Meta|Google|GA4|кабінет|розрахунок)\b[^)]*)\)'
    r'|\(\s*\d{4}-\d{2}',
    re.I)

# числа, що вимагають джерела: гроші, відсотки, множники, великі кількості
NUM = re.compile(
    r'(?<![\w.])(?:'
    r'\$\s?\d[\d\s,.]*'                     # $290, $1 500
    r'|\d[\d\s]*(?:[.,]\d+)?\s?(?:%|відсотк\w*)'   # 3.2%, 61 відсоток
    r'|\d[\d\s]*(?:[.,]\d+)?\s?(?:грн|₴|€|USD|EUR)'
    r'|\d[\d\s]{3,}'                        # 18 400, 2400
    r'|\d+(?:[.,]\d+)?\s?[×x]\s?\d'         # 3x
    r')', re.U)

# рядки, які не перевіряємо
SKIP_LINE = re.compile(
    r'^\s*(?:#|<!--|//|/\*|\*|--|\||```)'   # заголовки, коментарі, межі таблиць
    r'|^\s*[-*]\s*\[[ x]\]'                 # чеклісти
    r'|python3|npm |pip |http', re.I)

# CSS/SVG/код — числа там технічні, не бізнесові
CSS_LINE = re.compile(
    r'\b(?:px|rem|em|vw|vh|deg|ms|fr|ch)\b'
    r'|rgba?\(|oklch|hsla?\(|#[0-9a-f]{3,8}\b|var\(--'
    r'|gradient|transform|translate|scale|rotate|blur|opacity|cubic-bezier'
    r'|\bviewBox|\bstroke|\bd="[Mm]|\bpath\b|\bwidth=|\bheight='
    r'|[{};]\s*$|^\s*[.#@]?[\w-]+\s*[:{]'
    r'|calc\(|clamp\(|min\(|max\(|@media|@keyframes|:root'
    , re.I)


def scan(path, strict=False):
    try:
        lines = open(path, encoding="utf-8").read().split("\n")
    except OSError as e:
        sys.exit(f"Не читається: {e}")

    in_code = in_style = False
    flagged = []
    for i, line in enumerate(lines):
        low = line.lower()
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if "<style" in low:
            in_style = True
        if "</style" in low:
            in_style = False
            continue
        if in_code or in_style or not line.strip():
            continue
        if SKIP_LINE.search(line) or CSS_LINE.search(line):
            continue
        nums = NUM.findall(line)
        if not nums:
            continue
        # ТІЛЬКИ цей рядок: тег із сусіднього рядка стосується сусіднього числа
        if TAGS.search(line):
            continue
        flagged.append((i + 1, line.strip()[:96], nums[:4]))

    print(f"Файл: {path}")
    if not flagged:
        print("Чисто: усі числа мають джерело або тег.")
        return 0

    print(f"\nЧИСЕЛ БЕЗ ДЖЕРЕЛА: {len(flagged)}\n")
    for ln, text, nums in flagged:
        print(f"  рядок {ln}: {', '.join(str(n).strip() for n in nums)}")
        print(f"     {text}")
    print("\nКожне з них має отримати тег або джерело:")
    print("  [ФАКТ: кабінет Meta, 2026-07-30]  [ОЦІНКА: трафік × CR × чек]")
    print("  [ПРИПУЩЕННЯ]  [ДЕМО]  або  НЕВІДОМО ⚠️")
    return 1 if strict else 0


def main():
    p = argparse.ArgumentParser(description="Перевірка чисел на наявність джерела")
    p.add_argument("files", nargs="+")
    p.add_argument("--strict", action="store_true",
                   help="ненульовий код виходу якщо знайдено (для хуків і CI)")
    a = p.parse_args()
    rc = 0
    for f in a.files:
        rc |= scan(f, a.strict)
        print()
    sys.exit(rc)


if __name__ == "__main__":
    main()
