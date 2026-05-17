"""
GitHub Actions Browser Relay Runner.
Reads .relay/request.json, executes the task, writes .relay/result.json.
"""

import json
import os
import time
import traceback
import httpx
from pathlib import Path
from playwright.sync_api import sync_playwright
try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

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


def search_products_api_direct(query: str, max_price: int) -> list:
    """Try multiple Rozetka API endpoints directly with session cookies."""
    session = httpx.Client(
        follow_redirects=True,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "uk-UA,uk;q=0.9,ru;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
        }
    )

    # Step 1: Visit homepage to get cookies/session
    print("Getting session cookies from homepage...")
    try:
        r = session.get("https://rozetka.com.ua/ua/", timeout=15)
        print(f"Homepage: HTTP {r.status_code}, cookies: {list(r.cookies.keys())[:5]}")
        time.sleep(1)
    except Exception as e:
        print(f"Homepage fetch error: {e}")

    q_encoded = query.replace(' ', '%20')
    q_plus = query.replace(' ', '+')

    endpoints = [
        # v6 search API (newer)
        f"https://search.rozetka.com.ua/ua/search/api/v6/goods?text={q_encoded}&price=0%3B{max_price}&sort=popular&page=1",
        # xl-catalog API
        f"https://xl-catalog-api.rozetka.com.ua/v4/goods/get?category_id=80089&text={q_encoded}&price=0%3B{max_price}&sort=popular&page=1",
        # Main API
        f"https://rozetka.com.ua/api/product-api/v4/goods/get?text={q_encoded}&price=0;{max_price}&sort=popular",
        # Search page API
        f"https://rozetka.com.ua/ua/search/?text={q_plus}&price=0;{max_price}&sort=popular",
    ]

    for url in endpoints:
        try:
            r = session.get(url, headers={"Referer": "https://rozetka.com.ua/ua/search/"})
            print(f"API {url[:70]}: HTTP {r.status_code}")
            if r.status_code == 200:
                try:
                    data = r.json()
                    # v6 format
                    if "data" in data and isinstance(data["data"], list):
                        goods = data["data"][:10]
                        results = [{"name": g.get("title", g.get("full_name", "")),
                                   "price": int(g.get("price", 0)),
                                   "url": g.get("href", g.get("url", ""))} for g in goods]
                        results = [p for p in results if p["name"] and p["price"] > 0]
                        if results:
                            print(f"v6 API: {len(results)} products")
                            return results
                    # v4 format
                    goods = data.get("data", {}).get("goods", [])
                    if goods:
                        results = [{"name": g.get("title", g.get("full_name", "")),
                                   "price": int(g.get("price", 0)),
                                   "url": g.get("href", g.get("url", ""))} for g in goods[:10]]
                        results = [p for p in results if p["name"] and p["price"] > 0]
                        if results:
                            print(f"v4 API: {len(results)} products")
                            return results
                    print(f"  Response keys: {list(data.keys())[:5]}, content: {str(data)[:200]}")
                except Exception as e:
                    print(f"  JSON parse error: {e}, content: {r.text[:200]}")
        except Exception as e:
            print(f"  Request error: {e}")

    return []


def search_products_browser(page, query: str, max_price: int) -> list:
    """Browser-based search with API interception and extended waiting."""
    api_responses = []

    def handle_response(response):
        url = response.url
        if any(x in url for x in ["catalog-api", "goods/get", "search/api", "xl-catalog", "product-api"]):
            try:
                body = response.json()
                if isinstance(body, dict):
                    # Check various response structures
                    goods = (body.get("data", {}).get("goods") or
                             body.get("data") if isinstance(body.get("data"), list) else None)
                    if goods:
                        api_responses.append({"goods": goods, "url": url})
                        print(f"Captured API: {url[:80]} → {len(goods)} goods")
            except Exception:
                pass

    page.on("response", handle_response)

    # Visit homepage first to establish session
    print("Visiting homepage first...")
    page.goto("https://rozetka.com.ua/ua/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    screenshot(page, "02a_homepage")

    search_url = (
        f"https://rozetka.com.ua/ua/search/"
        f"?text={query.replace(' ', '+')}"
        f"&price=0;{max_price}&sort=popular"
    )
    print(f"Navigating to search: {search_url}")
    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    screenshot(page, "03a_initial_load")

    # Wait up to 40 seconds for product tiles
    print("Waiting for product tiles...")
    try:
        page.wait_for_selector(
            "app-goods-tile-default, .goods-tile__title, a.goods-tile__heading, rz-catalog-tile",
            timeout=40000
        )
        print("Product tiles appeared!")
        time.sleep(3)
    except Exception:
        print("Product tiles didn't appear — waiting 20s more...")
        time.sleep(20)

    screenshot(page, "03_search_results")
    print("Page title:", page.title())
    print("Page URL:", page.url)

    # Save debug HTML
    html_content = page.content()
    Path(".relay/debug_page.html").write_text(html_content[:80000])

    # Method 1: From intercepted API responses
    if api_responses:
        products = []
        for resp in api_responses:
            for good in resp["goods"][:10]:
                products.append({
                    "name": good.get("title", good.get("full_name", "")),
                    "price": int(good.get("price", 0)),
                    "url": good.get("href", good.get("url", "")),
                })
        products = [p for p in products if p["name"] and p["price"] > 0]
        if products:
            print(f"API interception: {len(products)} products")
            return products[:10]

    # Method 2: JS DOM extraction
    try:
        js_products = page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('app-goods-tile-default, li.catalog-grid__cell, rz-catalog-tile').forEach(tile => {
                const nameEl = tile.querySelector('a.goods-tile__heading, .goods-tile__title, [class*="title"]');
                const priceEl = tile.querySelector('.goods-tile__price-value, [class*="price-value"], [class*="price"]');
                const linkEl = tile.querySelector('a[href*="rozetka.com.ua"], a[href*="/ua/"]');
                if (nameEl && priceEl) {
                    const priceText = priceEl.textContent.replace(/\\D/g, '');
                    if (priceText && parseInt(priceText) > 0) {
                        results.push({
                            name: nameEl.textContent.trim(),
                            price: parseInt(priceText),
                            url: linkEl ? linkEl.href : ''
                        });
                    }
                }
            });
            return results;
        }""")
        js_products = [p for p in (js_products or []) if p["price"] > 0]
        if js_products:
            print(f"JS DOM: {len(js_products)} products")
            return js_products[:10]
    except Exception as e:
        print(f"JS DOM error: {e}")

    # Log what's actually on the page
    body_text = page.evaluate("document.body.innerText")[:3000]
    Path(".relay/debug_body.txt").write_text(body_text)
    print("Body snippet:", body_text[:500])
    return []


def search_products(page, query: str, max_price: int) -> list:
    """Try API first, then browser fallback."""
    # Try direct API with session cookies
    products = search_products_api_direct(query, max_price)
    if products:
        return products

    print("Direct API failed, using browser with extended wait...")
    return search_products_browser(page, query, max_price)


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
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="uk-UA",
            timezone_id="Europe/Kyiv",
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['uk-UA', 'uk', 'ru']});
            window.chrome = {runtime: {}};
        """)
        page = context.new_page()

        if stealth_sync:
            stealth_sync(page)
            print("Stealth mode applied")

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

            elif action == "fetch_api":
                # Direct API test — no browser needed
                query = request.get("query", "")
                max_price = request.get("max_price", 999999)
                products = search_products_api_direct(query, max_price)
                result["status"] = "ok"
                result["data"] = {"products": products, "count": len(products)}

        except Exception:
            result["status"] = "error"
            result["data"]["traceback"] = traceback.format_exc()

        finally:
            browser.close()

    RESULT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run()
