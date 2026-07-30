#!/usr/bin/env python3
"""
Юніт-економіка гіпотези: LTV, стеля CAC, точка беззбитковості,
і — головне — межа при якій модель ламається.

Використання:
  python3 unit_economics.py --price 19 --margin 0.75 --retention 8 \
                            --cpc 2.4 --cr-landing 0.03 --cr-trial 0.25 \
                            --fixed 500 [--json]

Усі відсотки — часткою (0.75), не 75.
"""
import argparse
import json
import sys


def compute(price, margin, retention, cpc, cr_landing, cr_trial, fixed,
            cogs_per_user=0.0, one_time=False):
    """Повертає dict з усіма показниками. Чиста функція, без побічних ефектів."""
    # Валова маржа з урахуванням змінної собівартості на користувача
    gross_per_month = price * margin - cogs_per_user
    months = 1 if one_time else retention
    ltv = gross_per_month * months

    # Скільки кліків треба на одного платника
    cr_total = cr_landing * cr_trial
    clicks_per_customer = (1 / cr_total) if cr_total > 0 else float("inf")
    cac = cpc * clicks_per_customer

    cac_ceiling = ltv / 3.0            # індустріальний поріг LTV:CAC = 3
    ltv_cac = (ltv / cac) if cac > 0 else float("inf")
    payback_months = (cac / gross_per_month) if gross_per_month > 0 else float("inf")

    # Межі поломки: за якого CPC / CR модель перестає сходитись (LTV:CAC = 3)
    break_cpc = (cac_ceiling * cr_total) if cr_total > 0 else 0.0
    break_cr_total = (cpc / cac_ceiling) if cac_ceiling > 0 else float("inf")
    break_cr_landing = (break_cr_total / cr_trial) if cr_trial > 0 else float("inf")

    # Беззбитковість: скільки платників покриють постійні витрати
    be_customers = (fixed / gross_per_month) if gross_per_month > 0 else float("inf")

    if ltv_cac >= 3:
        verdict = "PASS"
    elif ltv_cac >= 1:
        verdict = "MARGINAL"
    else:
        verdict = "FAIL"

    return {
        "inputs": {
            "price": price, "margin": margin, "retention_months": months,
            "cpc": cpc, "cr_landing": cr_landing, "cr_trial": cr_trial,
            "fixed_monthly": fixed, "cogs_per_user": cogs_per_user,
            "one_time": one_time,
        },
        "gross_per_month": gross_per_month,
        "ltv": ltv,
        "cac": cac,
        "cac_ceiling": cac_ceiling,
        "ltv_cac": ltv_cac,
        "payback_months": payback_months,
        "clicks_per_customer": clicks_per_customer,
        "breakeven_customers": be_customers,
        "breaks_at": {
            "max_cpc": break_cpc,
            "min_cr_landing": break_cr_landing,
            "min_cr_total": break_cr_total,
        },
        "verdict": verdict,
    }


def fmt(r):
    b = r["breaks_at"]
    icon = {"PASS": "PASS", "MARGINAL": "MARGINAL", "FAIL": "FAIL"}[r["verdict"]]
    lines = [
        "=" * 58,
        "  ЮНІТ-ЕКОНОМІКА",
        "=" * 58,
        f"  Валовий дохід з клієнта / міс   ${r['gross_per_month']:>10.2f}",
        f"  LTV                             ${r['ltv']:>10.2f}",
        f"  CAC (при поточних CPC і CR)     ${r['cac']:>10.2f}",
        f"  Стеля CAC (LTV / 3)             ${r['cac_ceiling']:>10.2f}",
        f"  LTV:CAC                          {r['ltv_cac']:>10.2f}   (норма >= 3)",
        f"  Окупність залучення              {r['payback_months']:>10.1f} міс",
        f"  Кліків на 1 платника             {r['clicks_per_customer']:>10.0f}",
        f"  Беззбитковість                   {r['breakeven_customers']:>10.0f} клієнтів",
        "-" * 58,
        "  МОДЕЛЬ ЛАМАЄТЬСЯ ЯКЩО:",
        f"    CPC піднімається вище          ${b['max_cpc']:>10.2f}",
        f"    CR лендінга падає нижче         {b['min_cr_landing']*100:>9.2f} %",
        "-" * 58,
        f"  ВЕРДИКТ: {icon}",
        "=" * 58,
    ]
    if r["verdict"] == "FAIL":
        lines.append("  Модель не сходиться. Варіанти: підняти ціну, підняти")
        lines.append("  утримання, знайти дешевший канал, або вбити гіпотезу.")
    elif r["verdict"] == "MARGINAL":
        lines.append("  Запас відсутній. Будь-яке погіршення CPC або CR = збиток.")
        lines.append("  Не масштабуй без покращення хоча б одного важеля.")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Юніт-економіка гіпотези")
    p.add_argument("--price", type=float, required=True, help="ціна/міс або чек, $")
    p.add_argument("--margin", type=float, default=0.8, help="валова маржа часткою, 0.8")
    p.add_argument("--retention", type=float, default=6, help="середній термін життя, міс")
    p.add_argument("--cpc", type=float, required=True, help="вартість кліка, $")
    p.add_argument("--cr-landing", type=float, required=True, help="CR лендінга часткою")
    p.add_argument("--cr-trial", type=float, default=1.0,
                   help="CR ліда/тріалу в оплату часткою (1.0 якщо оплата одразу)")
    p.add_argument("--fixed", type=float, default=0.0, help="постійні витрати/міс, $")
    p.add_argument("--cogs", type=float, default=0.0,
                   help="змінна собівартість на користувача/міс, $ (AI-токени тощо)")
    p.add_argument("--one-time", action="store_true", help="разова покупка, не підписка")
    p.add_argument("--json", action="store_true", help="вивід у JSON")
    a = p.parse_args()

    for name, val in (("margin", a.margin), ("cr-landing", a.cr_landing),
                      ("cr-trial", a.cr_trial)):
        if not 0 < val <= 1:
            sys.exit(f"Помилка: --{name} має бути часткою в (0, 1], отримано {val}")

    r = compute(a.price, a.margin, a.retention, a.cpc, a.cr_landing,
                a.cr_trial, a.fixed, a.cogs, a.one_time)
    print(json.dumps(r, indent=2) if a.json else fmt(r))


if __name__ == "__main__":
    main()
