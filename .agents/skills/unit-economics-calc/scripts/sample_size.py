#!/usr/bin/env python3
"""
Скільки трафіку треба щоб результат тесту щось означав.

Три режими:
  size   — скільки візитів на варіант треба, щоб побачити задану різницю
  mde    — яку мінімальну різницю можна побачити на наявному трафіку
  read   — оцінка вже зібраних даних: чи різниця реальна чи це шум

Приклади:
  python3 sample_size.py size --baseline 0.02 --lift 0.30
  python3 sample_size.py mde  --baseline 0.02 --n 1500
  python3 sample_size.py read --a 12 900 --b 21 950

Нормальне наближення (двосторонній тест, alpha=0.05, power=0.80).
Достатньо точне для маркетингових рішень; для n<30 конверсій не покладайся.
"""
import argparse
import math

Z = {0.80: 1.2816, 0.90: 1.6449, 0.95: 1.9600, 0.975: 1.9600, 0.99: 2.5758}


def _z(p):
    """Обернена функція нормального розподілу (наближення Acklam, точність ~1e-9)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > ph:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def _norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def sample_size(p1, rel_lift, alpha=0.05, power=0.80):
    p2 = p1 * (1 + rel_lift)
    if p2 >= 1:
        raise ValueError("Очікувана конверсія перевищує 100% — зменш lift")
    za = _z(1 - alpha / 2)
    zb = _z(power)
    pbar = (p1 + p2) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) +
           zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / ((p2 - p1) ** 2))


def mde(p1, n, alpha=0.05, power=0.80):
    """Мінімальна відносна різниця, яку видно на n спостережень на варіант."""
    lo, hi = 0.001, 5.0
    for _ in range(200):
        mid = (lo + hi) / 2
        try:
            need = sample_size(p1, mid, alpha, power)
        except ValueError:
            hi = mid
            continue
        if need > n:
            lo = mid
        else:
            hi = mid
    return hi


def read_result(ca, na, cb, nb):
    """Двовибірковий z-тест пропорцій. Повертає p-value і довірчий інтервал різниці."""
    pa, pb = ca / na, cb / nb
    pool = (ca + cb) / (na + nb)
    se_pool = math.sqrt(pool * (1 - pool) * (1 / na + 1 / nb))
    z = (pb - pa) / se_pool if se_pool > 0 else 0.0
    pval = 2 * (1 - _norm_cdf(abs(z)))
    se_diff = math.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb)
    diff = pb - pa
    return {
        "cr_a": pa, "cr_b": pb, "abs_diff": diff,
        "rel_lift": (diff / pa) if pa > 0 else float("inf"),
        "z": z, "p_value": pval,
        "ci95": (diff - 1.96 * se_diff, diff + 1.96 * se_diff),
        "significant": pval < 0.05,
    }


def main():
    p = argparse.ArgumentParser(description="Розмір вибірки і читання A/B")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("size", help="скільки треба трафіку")
    s.add_argument("--baseline", type=float, required=True, help="поточний CR часткою")
    s.add_argument("--lift", type=float, required=True, help="відносний приріст, 0.30 = +30%%")
    s.add_argument("--power", type=float, default=0.80)

    m = sub.add_parser("mde", help="що видно на наявному трафіку")
    m.add_argument("--baseline", type=float, required=True)
    m.add_argument("--n", type=int, required=True, help="візитів на варіант")

    r = sub.add_parser("read", help="оцінити зібрані дані")
    r.add_argument("--a", nargs=2, type=int, required=True, metavar=("CONV", "N"))
    r.add_argument("--b", nargs=2, type=int, required=True, metavar=("CONV", "N"))

    a = p.parse_args()

    if a.cmd == "size":
        n = sample_size(a.baseline, a.lift, power=a.power)
        print(f"Базовий CR:        {a.baseline*100:.2f}%")
        print(f"Шукаємо приріст:   +{a.lift*100:.0f}% (до {a.baseline*(1+a.lift)*100:.2f}%)")
        print(f"\nПотрібно {n:,} візитів НА ВАРІАНТ ({n*2:,} всього)")
        print(f"При 100 візитах/день це {n*2/100:.0f} днів.")
        if n > 5000:
            print("\nЦе багато для швидкого тесту. Варіанти:")
            print("  - шукати більшу різницю (радикально інший офер, не колір кнопки)")
            print("  - тестувати вище по воронці, де конверсії частіші")
            print("  - приймати рішення на слабшому сигналі і швидше — але свідомо")

    elif a.cmd == "mde":
        d = mde(a.baseline, a.n)
        print(f"На {a.n:,} візитах на варіант при CR {a.baseline*100:.2f}%")
        print(f"ти побачиш різницю тільки від +{d*100:.0f}% і більше.")
        print(f"(тобто CR має вирости до {a.baseline*(1+d)*100:.2f}%)")
        print("\nВсе що менше — не відрізниш від шуму. Не інтерпретуй.")

    else:
        res = read_result(a.a[0], a.a[1], a.b[0], a.b[1])
        print(f"A: {a.a[0]}/{a.a[1]} = {res['cr_a']*100:.2f}%")
        print(f"B: {a.b[0]}/{a.b[1]} = {res['cr_b']*100:.2f}%")
        print(f"\nРізниця: {res['abs_diff']*100:+.2f} п.п. ({res['rel_lift']*100:+.1f}%)")
        print(f"p-value: {res['p_value']:.4f}")
        lo, hi = res["ci95"]
        print(f"95% ДІ різниці: [{lo*100:+.2f}; {hi*100:+.2f}] п.п.")
        if res["significant"]:
            print("\nЗНАЧУЩЕ (p < 0.05). Різниця схожа на реальну.")
        else:
            print("\nНЕ ЗНАЧУЩЕ. Це може бути шум — рішення на цих даних приймати не можна.")
            print("Або збирай далі, або визнай що різниці немає.")
        if lo < 0 < hi:
            print("Довірчий інтервал перетинає нуль — напрямок ефекту невідомий.")


if __name__ == "__main__":
    main()
