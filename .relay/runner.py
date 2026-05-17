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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "uk-UA,uk;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
}


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


def search_allo(query: str, max_price: int) -> list:
    """Search allo.ua — major Ukrainian electronics retailer with simpler API."""
    debug = []
    try:
        q = query.replace(' ', '+')
        # Allo search page (SSR rendered)
        url = f"https://allo.ua/ua/catalogsearch/result/?q={q}"
        r = httpx.get(url, headers={**HEADERS, "Accept": "text/html"}, timeout=20, follow_redirects=True)
        debug.append(f"allo.ua HTTP {r.status_code}")

        if r.status_code == 200:
            import re
            # Try to find JSON-LD product data
            json_ld = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', r.text, re.DOTALL)
            for block in json_ld:
                try:
                    data = json.loads(block)
                    if isinstance(data, dict) and data.get("@type") == "ItemList":
                        items = data.get("itemListElement", [])
                        products = []
                        for item in items[:10]:
                            offer = item.get("item", item)
                            price_data = offer.get("offers", {})
                            price = int(float(price_data.get("price", 0))) if price_data else 0
                            if price and price <= max_price:
                                products.append({
                                    "name": offer.get("name", ""),
                                    "price": price,
                                    "url": offer.get("url", ""),
                                    "shop": "allo.ua"
                                })
                        if products:
                            debug.append(f"allo.ua JSON-LD: {len(products)} products")
                            return products, debug
                except Exception:
                    pass

            # Try regex extraction from HTML
            # Allo uses data attributes or specific patterns
            prices = re.findall(r'"price"\s*:\s*"?(\d+)"?', r.text)
            names = re.findall(r'"name"\s*:\s*"([^"]{10,100})"', r.text)
            urls = re.findall(r'"url"\s*:\s*"(https://allo\.ua/[^"]+)"', r.text)
            debug.append(f"allo.ua regex: {len(names)} names, {len(prices)} prices")
            if names and prices:
                products = []
                for i in range(min(len(names), len(prices), len(urls) if urls else 99, 10)):
                    price = int(prices[i]) if prices[i].isdigit() else 0
                    if price and price <= max_price:
                        products.append({
                            "name": names[i],
                            "price": price,
                            "url": urls[i] if i < len(urls) else "",
                            "shop": "allo.ua"
                        })
                if products:
                    return products, debug

    except Exception as e:
        debug.append(f"allo.ua error: {e}")
    return [], debug


def search_rozetka_api(query: str, max_price: int) -> tuple:
    """Try multiple Rozetka API endpoints."""
    debug = []
    session = httpx.Client(follow_redirects=True, timeout=20, headers=HEADERS)

    # Get homepage cookies first
    try:
        r = session.get("https://rozetka.com.ua/ua/", timeout=15)
        debug.append(f"rozetka homepage: HTTP {r.status_code}, cookies: {list(r.cookies.keys())[:5]}")
    except Exception as e:
        debug.append(f"rozetka homepage error: {e}")

    q = query.replace(' ', '%20')
    endpoints = [
        (f"https://search.rozetka.com.ua/ua/search/api/v6/goods?text={q}&price=0%3B{max_price}&sort=popular", "v6"),
        (f"https://xl-catalog-api.rozetka.com.ua/v4/goods/get?text={q}&price=0%3B{max_price}&sort=popular&page=1", "xl-v4"),
        (f"https://rozetka.com.ua/api/product-api/v4/goods/get?text={q}&price=0;{max_price}&sort=popular", "main-v4"),
    ]

    for url, name in endpoints:
        try:
            r = session.get(url, headers={"Referer": "https://rozetka.com.ua/ua/search/", "Accept": "application/json"})
            debug.append(f"rozetka {name}: HTTP {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                debug.append(f"  keys: {list(data.keys())[:5]}, snippet: {str(data)[:150]}")
                # v6 format: data is list
                if isinstance(data.get("data"), list) and data["data"]:
                    goods = data["data"][:10]
                    products = [{"name": g.get("title", ""), "price": int(g.get("price", 0)),
                                "url": g.get("href", ""), "shop": "rozetka.com.ua"} for g in goods]
                    products = [p for p in products if p["name"] and p["price"] > 0]
                    if products:
                        return products, debug
                # v4 format: data.goods
                goods = data.get("data", {}).get("goods", [])
                if goods:
                    products = [{"name": g.get("title", g.get("full_name", "")), "price": int(g.get("price", 0)),
                                "url": g.get("href", ""), "shop": "rozetka.com.ua"} for g in goods[:10]]
                    products = [p for p in products if p["name"] and p["price"] > 0]
                    if products:
                        return products, debug
            else:
                debug.append(f"  response: {r.text[:100]}")
        except Exception as e:
            debug.append(f"  error: {e}")

    return [], debug


def search_rozetka_browser(page, query: str, max_price: int) -> list:
    """Browser-based Rozetka search — last resort."""
    api_responses = []

    def handle_response(response):
        url = response.url
        if any(x in url for x in ["catalog-api", "goods/get", "search/api", "xl-catalog", "product-api"]):
            try:
                body = response.json()
                if isinstance(body, dict):
                    goods = (body.get("data", {}).get("goods") or
                             (body.get("data") if isinstance(body.get("data"), list) else None))
                    if goods:
                        api_responses.append(goods)
                        print(f"Captured API response: {url[:80]} → {len(goods)} goods")
            except Exception:
                pass

    page.on("response", handle_response)

    # Visit homepage first for session
    page.goto("https://rozetka.com.ua/ua/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    screenshot(page, "02a_homepage")

    search_url = f"https://rozetka.com.ua/ua/search/?text={query.replace(' ', '+')}&price=0;{max_price}&sort=popular"
    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    screenshot(page, "03a_initial_load")

    try:
        page.wait_for_selector(
            "app-goods-tile-default, .goods-tile__title, a.goods-tile__heading",
            timeout=45000
        )
        print("Product tiles appeared!")
        time.sleep(3)
    except Exception:
        print("No product tiles after 45s")
        time.sleep(10)

    screenshot(page, "03_search_results")
    html_content = page.content()
    Path(".relay/debug_page.html").write_text(html_content[:80000])

    if api_responses:
        products = []
        for goods in api_responses:
            for g in goods[:10]:
                products.append({
                    "name": g.get("title", g.get("full_name", "")),
                    "price": int(g.get("price", 0)),
                    "url": g.get("href", g.get("url", "")),
                    "shop": "rozetka.com.ua"
                })
        products = [p for p in products if p["name"] and p["price"] > 0]
        if products:
            return products[:10]

    # JS DOM extraction
    try:
        js_products = page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('app-goods-tile-default, li.catalog-grid__cell').forEach(tile => {
                const nameEl = tile.querySelector('a.goods-tile__heading, .goods-tile__title');
                const priceEl = tile.querySelector('.goods-tile__price-value');
                const linkEl = tile.querySelector('a[href*="rozetka"]');
                if (nameEl && priceEl) {
                    const price = parseInt(priceEl.textContent.replace(/\\D/g, ''));
                    if (price > 0) {
                        results.push({ name: nameEl.textContent.trim(), price, url: linkEl ? linkEl.href : '' });
                    }
                }
            });
            return results;
        }""")
        if js_products:
            print(f"JS DOM: {len(js_products)} products")
            return [dict(p, shop="rozetka.com.ua") for p in js_products[:10]]
    except Exception as e:
        print(f"JS DOM error: {e}")

    body_text = page.evaluate("document.body.innerText")[:3000]
    Path(".relay/debug_body.txt").write_text(body_text)
    print("Body snippet:", body_text[:500])
    return []


def add_to_cart(page, product_url: str) -> dict:
    page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    screenshot(page, "04_product_page")
    buy_selectors = [
        "button.buy-button", "button.product-buy__btn", "rz-buy-button button",
        "button:has-text('Купити')", "button:has-text('Додати в кошик')",
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="uk-UA",
            timezone_id="Europe/Kyiv",
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['uk-UA', 'uk']});
            window.chrome = {runtime: {}};
        """)
        page = context.new_page()
        if stealth_sync:
            stealth_sync(page)
            print("Stealth mode applied")

        try:
            if action in ("search", "fetch_api"):
                query = request.get("query", "")
                max_price = request.get("max_price", 999999)
                all_debug = []

                # 1. Try Rozetka direct API
                products, debug = search_rozetka_api(query, max_price)
                all_debug.extend(debug)

                # 2. Try allo.ua if Rozetka API failed
                if not products:
                    print("Rozetka API failed, trying allo.ua...")
                    products, debug = search_allo(query, max_price)
                    all_debug.extend(debug)

                # 3. Browser fallback for Rozetka
                if not products and action == "search":
                    print("All API attempts failed, using Rozetka browser...")
                    products = search_rozetka_browser(page, query, max_price)

                result["status"] = "ok"
                result["data"] = {"products": products, "count": len(products), "debug": all_debug}

            elif action == "add_to_cart":
                query = request.get("query", "")
                max_price = request.get("max_price", 999999)
                login_result = login_rozetka(page)
                result["data"]["login"] = login_result
                if not login_result.get("logged_in"):
                    result["status"] = "login_failed"
                else:
                    products = search_rozetka_browser(page, query, max_price)
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
