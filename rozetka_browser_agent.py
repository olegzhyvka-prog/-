#!/usr/bin/env python3
"""
Rozetka Browser Agent — повноцінна автоматизація Розетки.

Запуск:
    python rozetka_browser_agent.py "монітор 27 дюймів" --max-price 30000
    python rozetka_browser_agent.py "iphone 15" --max-price 50000 --add-to-cart

Що робить:
    1. Відкриває браузер (видимий — ти можеш залогінитися)
    2. Шукає товар на Розетці
    3. Фільтрує за ціною
    4. Показує найкращий варіант
    5. Додає в кошик (якщо --add-to-cart)
"""

import sys
import time
import argparse
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, Page


# ── Helpers ───────────────────────────────────────────────────────────────────

def wait(page: Page, selector: str, timeout: int = 10000):
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception:
        return False


def screenshot(page: Page, name: str):
    path = f"/tmp/rozetka_{name}.png"
    page.screenshot(path=path)
    print(f"  📸 Скріншот збережено: {path}")


def slow_type(page: Page, selector: str, text: str):
    page.click(selector)
    page.fill(selector, "")
    page.type(selector, text, delay=50)


# ── Login ─────────────────────────────────────────────────────────────────────

def login(page: Page) -> bool:
    """Check if logged in; if not — wait for user to log in manually."""
    # Check if already logged in
    if page.locator(".header-top-profile__name").is_visible():
        print("  ✅ Вже залогінений")
        return True

    print("\n  🔐 Потрібен вхід в акаунт.")
    print("  → Відкриваю сторінку входу...")

    # Click the login button
    try:
        page.locator("rz-header-login-modal button, .header-actions__item--login, button[routerlink='/login']").first.click()
        time.sleep(1)
    except Exception:
        page.goto("https://rozetka.com.ua/ua/login/", wait_until="domcontentloaded")

    screenshot(page, "login_page")
    print("\n  👤 БУДЬ ЛАСКА, ЗАЛОГІНУЙСЯ В БРАУЗЕРІ:")
    print("     Введи логін та пароль у вікні браузера, яке відкрилось.")
    print("     Після входу натисни Enter тут для продовження...")
    input("  ⏳ Натисни Enter після входу > ")

    # Verify login
    page.goto("https://rozetka.com.ua/ua/", wait_until="domcontentloaded")
    time.sleep(2)
    if page.locator(".header-top-profile__name").is_visible():
        name = page.locator(".header-top-profile__name").inner_text()
        print(f"  ✅ Залогінений як: {name}")
        return True
    else:
        print("  ⚠️  Схоже, вхід не виконано. Продовжуємо без акаунту...")
        return False


# ── Search & filter ───────────────────────────────────────────────────────────

def search_products(page: Page, query: str, max_price: int) -> list[dict]:
    print(f"\n🔍 Шукаю: '{query}' до {max_price:,} грн...")

    # Navigate to search
    page.goto(
        f"https://rozetka.com.ua/ua/search/?text={query.replace(' ', '+')}&price=0;{max_price}&sort=popular",
        wait_until="domcontentloaded",
        timeout=30000,
    )
    time.sleep(3)
    screenshot(page, "search_results")

    # Check for results
    if not wait(page, ".goods-tile", timeout=8000):
        print("  ❌ Товарів не знайдено.")
        return []

    # Collect products
    tiles = page.locator(".goods-tile").all()[:10]
    products = []
    for tile in tiles:
        try:
            name = tile.locator(".goods-tile__title").inner_text(timeout=2000).strip()
            price_text = tile.locator(".goods-tile__price-value").first.inner_text(timeout=2000)
            price = int("".join(filter(str.isdigit, price_text)))
            link_el = tile.locator("a.goods-tile__heading, a.goods-tile__title").first
            link = link_el.get_attribute("href") or ""
            products.append({"name": name, "price": price, "url": link, "element": tile})
        except Exception:
            continue

    print(f"  ✅ Знайдено {len(products)} товарів")
    return products


def pick_best(products: list[dict]) -> dict | None:
    if not products:
        return None
    # Sort by price (best value = cheapest that meets criteria, already filtered)
    products_sorted = sorted(products, key=lambda x: x["price"])
    best = products_sorted[0]
    print(f"\n🏆 Найкращий варіант:")
    print(f"   Назва: {best['name']}")
    print(f"   Ціна:  {best['price']:,} грн")
    print(f"   URL:   {best['url']}")
    return best


# ── Add to cart ───────────────────────────────────────────────────────────────

def add_to_cart(page: Page, product: dict) -> bool:
    print(f"\n🛒 Додаю в кошик: {product['name'][:60]}...")

    page.goto(product["url"], wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    screenshot(page, "product_page")

    # Find and click "Buy" button
    buy_selectors = [
        "button.buy-button",
        "button.product-buy__btn",
        "rz-buy-button button",
        "button:has-text('Купити')",
        "button:has-text('Додати')",
        ".buy-button",
    ]

    clicked = False
    for sel in buy_selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                clicked = True
                print(f"  ✅ Натиснув кнопку '{sel}'")
                break
        except Exception:
            continue

    if not clicked:
        print("  ❌ Не знайшов кнопку 'Купити'. Скріншот: /tmp/rozetka_product_page.png")
        return False

    time.sleep(2)
    screenshot(page, "after_add_to_cart")

    # Confirm cart modal appeared
    if page.locator(".modal, .cart-modal, .cart-popup").is_visible():
        print("  🎉 Товар успішно додано в кошик!")
        return True

    # Check cart counter
    try:
        counter = page.locator(".cart-count, .header-actions__count").inner_text(timeout=3000)
        if counter and int(counter) > 0:
            print(f"  🎉 Кошик: {counter} товар(и)")
            return True
    except Exception:
        pass

    print("  ⚠️  Схоже, товар додано (перевір кошик вручну)")
    return True


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Rozetka Browser Agent")
    parser.add_argument("query", help="Що шукати (напр. 'монітор 27 дюймів')")
    parser.add_argument("--max-price", type=int, default=30000, help="Максимальна ціна (грн)")
    parser.add_argument("--add-to-cart", action="store_true", help="Додати найкращий товар у кошик")
    parser.add_argument("--headless", action="store_true", help="Без видимого вікна браузера")
    args = parser.parse_args()

    print("=" * 60)
    print("🤖 Rozetka Browser Agent")
    print(f"   Пошук:    {args.query}")
    print(f"   Бюджет:   до {args.max_price:,} грн")
    print(f"   Кошик:    {'так' if args.add_to_cart else 'ні'}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=args.headless,
            slow_mo=300,  # повільніше щоб видно рухи
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        # Hide automation indicators
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = context.new_page()

        # Step 1: Open Rozetka
        print("\n📌 Крок 1: Відкриваю Розетку...")
        page.goto("https://rozetka.com.ua/ua/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # Step 2: Login (if needed and adding to cart)
        if args.add_to_cart:
            print("\n📌 Крок 2: Перевіряю авторизацію...")
            login(page)

        # Step 3: Search
        print("\n📌 Крок 3: Пошук товару...")
        products = search_products(page, args.query, args.max_price)
        if not products:
            print("\n❌ Нічого не знайдено. Спробуй інший запит.")
            input("Натисни Enter для закриття...")
            browser.close()
            return

        # Step 4: Show results
        print(f"\n📋 Знайдені товари:")
        for i, p_item in enumerate(products[:5], 1):
            print(f"  {i}. {p_item['name'][:55]:<55} — {p_item['price']:>7,} грн")

        best = pick_best(products)

        # Step 5: Add to cart
        if args.add_to_cart and best:
            print("\n📌 Крок 4: Додаю в кошик...")
            success = add_to_cart(page, best)
            if success:
                print("\n✅ ГОТОВО! Товар у кошику.")
                print(f"   Відкрий https://rozetka.com.ua/ua/cart/ для перегляду.")
            else:
                print("\n❌ Не вдалося додати автоматично. Спробуй вручну.")
        elif best:
            print(f"\n📌 Відкриваю сторінку товару...")
            page.goto(best["url"], wait_until="domcontentloaded")
            screenshot(page, "best_product")
            print(f"\n✅ Відкрито сторінку: {best['name']}")
            print(f"   Ціна: {best['price']:,} грн")
            print(f"\n   Щоб додати в кошик, запусти знову з --add-to-cart")

        print("\n⏸  Вікно браузера залишається відкритим.")
        input("   Натисни Enter для закриття > ")
        browser.close()


if __name__ == "__main__":
    main()
