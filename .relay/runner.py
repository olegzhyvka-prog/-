"""
GitHub Actions Browser Relay Runner.
Reads .relay/request.json, executes the task, writes .relay/result.json.
"""

import json
import os
import time
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright

REQUEST_FILE = Path(".relay/request.json")
RESULT_FILE = Path(".relay/result.json")
SCREENSHOTS_DIR = Path(".relay/screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)


def screenshot(page, name: str) -> str:
    path = SCREENSHOTS_DIR / f"{name}.png"
    page.screenshot(path=str(path))
    return str(path)


def login_rozetka(page) -> dict:
    phone = os.environ.get("ROZETKA_PHONE", "")
    password = os.environ.get("ROZETKA_PASSWORD", "")
    if not phone or not password:
        return {"logged_in": False, "reason": "No credentials in GitHub Secrets"}

    page.goto("https://rozetka.com.ua/ua/", wait_until="domcontentloaded")
    time.sleep(2)

    # Click login button
    try:
        page.locator("button.header-actions__button--user, .user-identification-button").first.click()
        time.sleep(1)
    except Exception:
        pass

    try:
        page.locator("a[href*='login'], button:has-text('Увійти')").first.click()
        time.sleep(1)
    except Exception:
        page.goto("https://rozetka.com.ua/ua/login/", wait_until="domcontentloaded")

    time.sleep(2)
    screenshot(page, "01_login_page")

    try:
        page.fill("input[type='tel'], input[name='login'], input[type='email']", phone)
        page.fill("input[type='password']", password)
        page.keyboard.press("Enter")
        time.sleep(3)
        screenshot(page, "02_after_login")
        return {"logged_in": True}
    except Exception as e:
        return {"logged_in": False, "reason": str(e)}


def search_products(page, query: str, max_price: int) -> list:
    url = (
        f"https://rozetka.com.ua/ua/search/"
        f"?text={query.replace(' ', '+')}"
        f"&price=0;{max_price}&sort=popular"
    )
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    screenshot(page, "03_search_results")

    tiles = page.locator(".goods-tile").all()[:10]
    products = []
    for tile in tiles:
        try:
            name = tile.locator(".goods-tile__title").inner_text(timeout=2000).strip()
            price_raw = tile.locator(".goods-tile__price-value").first.inner_text(timeout=2000)
            price = int("".join(filter(str.isdigit, price_raw)))
            link = (tile.locator("a.goods-tile__heading, a.goods-tile__title")
                    .first.get_attribute("href") or "")
            products.append({"name": name, "price": price, "url": link})
        except Exception:
            continue
    return products


def add_to_cart(page, product_url: str) -> dict:
    page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    screenshot(page, "04_product_page")

    buy_selectors = [
        "button.buy-button",
        "button.product-buy__btn",
        "rz-buy-button button",
        "button:has-text('Купити')",
        "button:has-text('Додати в кошик')",
    ]
    for sel in buy_selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                time.sleep(2)
                screenshot(page, "05_after_add")
                return {"success": True, "selector_used": sel}
        except Exception:
            continue
    screenshot(page, "05_buy_button_not_found")
    return {"success": False, "reason": "Buy button not found"}


def run():
    request = json.loads(REQUEST_FILE.read_text())
    action = request.get("action")
    result = {"action": action, "status": "error", "data": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = context.new_page()

        try:
            if action == "search":
                query = request.get("query", "")
                max_price = request.get("max_price", 999999)
                products = search_products(page, query, max_price)
                result["status"] = "ok"
                result["data"] = {"products": products, "count": len(products)}

            elif action == "add_to_cart":
                query = request.get("query", "")
                max_price = request.get("max_price", 999999)

                login_result = login_rozetka(page)
                result["data"]["login"] = login_result

                if not login_result.get("logged_in"):
                    result["status"] = "login_failed"
                else:
                    products = search_products(page, query, max_price)
                    if not products:
                        result["status"] = "no_products"
                    else:
                        best = sorted(products, key=lambda x: x["price"])[0]
                        result["data"]["selected"] = best
                        cart_result = add_to_cart(page, best["url"])
                        result["data"]["cart"] = cart_result
                        result["status"] = "ok" if cart_result["success"] else "cart_failed"

            elif action == "fetch_url":
                url = request.get("url", "")
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(3)
                screenshot(page, "fetch_result")
                result["status"] = "ok"
                result["data"] = {
                    "title": page.title(),
                    "url": page.url,
                    "text": page.evaluate("document.body.innerText")[:5000],
                }

        except Exception:
            result["status"] = "error"
            result["data"]["traceback"] = traceback.format_exc()

        finally:
            browser.close()

    RESULT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
