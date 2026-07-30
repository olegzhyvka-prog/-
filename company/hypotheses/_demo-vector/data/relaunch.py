# Що дає одноплечий перезапуск на $300 при фактичних числах тесту 24-26.07.2026
BUDGET = 300.0
CLICK_TO_VISIT = 198/214          # факт варіанта A
CR_PAY = [0.00089, 0.00505, 0.02805]   # нижня межа ДІ / точка / верхня межа ДІ (Wilson)
LABELS = ["нижня межа ДІ", "точкова оцінка", "верхня межа ДІ"]
PRICE = 290.0
CEILING_CAC = 58.0                # LTV/3 при one-time, маржа 0.6
BREAKEVEN_CAC = 174.0             # LTV при one-time, маржа 0.6
for cpc in (0.40, 0.80):
    clicks = BUDGET/cpc
    visits = clicks*CLICK_TO_VISIT
    print(f"\nCPC ${cpc:.2f} → {clicks:.0f} кліків → {visits:.0f} візитів на $300")
    for cr, lab in zip(CR_PAY, LABELS):
        pays = visits*cr
        rev = pays*PRICE
        cac = BUDGET/pays if pays else float('inf')
        verdict = "нижче стелі" if cac <= CEILING_CAC else ("нижче беззбитковості" if cac <= BREAKEVEN_CAC else "ВИЩЕ беззбитковості")
        print(f"  {lab:<16} CR {cr*100:5.3f}%  оплат {pays:5.2f}  виручка ${rev:8.0f}  CAC ${cac:8.2f}  → {verdict}")
