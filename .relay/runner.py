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


def search_products_api(query: str, max_price: int) -> list:
    """Try Rozetka's internal catalog API directly (no browser needed)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "uk-UA,uk;q=0.9",
        "Referer": "https://rozetka.com.ua/",
        "Origin": "https://rozetka.com.ua",
    }
    endpoints = [
        # Main catalog search API
        f"https://xl-catalog-api.rozetka.com.ua/v4/goods/get?category_id=80089&text={query.replace(' ', '%20')}&price=0%3B{max_price}&sort=popular&page=1",
        # Older API format
        f"https://rozetka.com.ua/api/product-api/v4/goods/get?text={query.replace(' ', '%20')}&price=0;{max_price}&sort=popular",
    ]
    for url in endpoints:
        try:
            r = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
            print(f"API {url[:60]}: HTTP {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                goods = data.get("data", {}).get("goods", [])
                if goods:
                    return [{"name": g.get("title", g.get("full_name", "")),
                             "price": int(g.get("price", 0)),
                             "url": g.get("href", g.get("url", ""))} for g in goods[:10]]
        except Exception as e:
            print(f"API error: {e}")
    return []


def search_products(page, query: str, max_price: int) -> list:
    api_responses = []

    # Intercept Rozetka's catalog API calls
    def handle_response(response):
        url = response.url
        if any(x in url for x in ["catalog-api", "goods/get", "search", "xl-catalog"]):
            try:
                body = response.json()
                if isinstance(body, dict) and body.get("data", {}).get("goods"):
                    api_responses.append(body)
                    print(f"Captured API: {url[:80]} → {len(body['data']['goods'])} goods")
            except Exception:
                pass

    page.on("response", handle_response)

    search_url = (
        f"https://rozetka.com.ua/ua/search/"
        f"?text={query.replace(' ', '+')}"
        f"&price=0;{max_price}&sort=popular"
    )
    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

    # Wait for actual product tiles to appear (not skeleton)
    try:
        page.wait_for_selector(
            "app-goods-tile-default, .goods-tile__title, a.goods-tile__heading",
            timeout=25000
        )
        time.sleep(3)
    except Exception:
        print("Product tiles didn't appear, trying to wait more...")
        time.sleep(8)

    screenshot(page, "03_search_results")

    # Save debug HTML
    html_content = page.content()
    Path(".relay/debug_page.html").write_text(html_content[:80000])

    # Method 1: From intercepted API responses
    if api_responses:
        products = []
        for resp in api_responses:
            for good in resp.get("data", {}).get("goods", [])[:10]:
                products.append({
                    "name": good.get("title", good.get("full_name", "")),
                    "price": int(good.get("price", 0)),
                    "url": good.get("href", good.get("url", "")),
                })
        products = [p for p in products if p["name"] and p["price"] > 0]
        if products:
            print(f"API interception: {len(products)} products")
            return products[:10]

    # Method 2: JS DOM extraction after full render
    try:
        js_products = page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('app-goods-tile-default, li.catalog-grid__cell').forEach(tile => {
                const nameEl = tile.querySelector('a.goods-tile__heading, .goods-tile__title');
                const priceEl = tile.querySelector('.goods-tile__price-value');
                const linkEl = tile.querySelector('a[href*="rozetka.com.ua"]');
                if (nameEl && priceEl) {
                    results.push({
                        name: nameEl.textContent.trim(),
                        price: parseInt(priceEl.textContent.replace(/\\D/g, '')) || 0,
                        url: linkEl ? linkEl.href : ''
                    });
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

    # Try multiple selector strategies for Rozetka's structure
    selectors_to_try = [
        ".goods-tile",
        "li.catalog-grid__cell",
        "app-goods-tile-default",
        "[data-testid='product-item']",
        ".product-card",
        "rz-catalog-tile",
    ]

    tiles = []
    for sel in selectors_to_try:
        found = page.locator(sel).all()
        if found:
            print(f"Found {len(found)} tiles with selector: {sel}")
            tiles = found[:10]
            break

    if not tiles:
        # Fallback: extract from JSON-LD or page text
        body_text = page.evaluate("document.body.innerText")[:3000]
        Path(".relay/debug_body.txt").write_text(body_text)
        print("No tiles found. Body snippet:", body_text[:300])
        return []

    products = []
    for tile in tiles:
        try:
            # Try multiple name selectors
            name = ""
            for name_sel in [".goods-tile__title", ".product-card__title", "a[title]", "h3", "h2"]:
                try:
                    el = tile.locator(name_sel).first
                    if el.is_visible(timeout=1000):
                        name = el.inner_text(timeout=1000).strip()
                        if name:
                            break
                except Exception:
                    continue

            # Try multiple price selectors
            price = 0
            for price_sel in [
                ".goods-tile__price-value",
                ".product-price__big",
                "[data-testid='price']",
                ".price__value",
                "span.price",
            ]:
                try:
                    el = tile.locator(price_sel).first
                    if el.is_visible(timeout=1000):
                        price_raw = el.inner_text(timeout=1000)
                        digits = "".join(filter(str.isdigit, price_raw))
                        if digits:
                            price = int(digits)
                            break
                except Exception:
                    continue

            # Get link
            link = ""
            for link_sel in ["a.goods-tile__heading", "a.goods-tile__title", "a[href*='rozetka']", "a"]:
                try:
                    href = tile.locator(link_sel).first.get_attribute("href", timeout=1000)
                    if href and "rozetka" in href:
                        link = href
                        break
                except Exception:
                    continue

            if name and price > 0:
                products.append({"name": name, "price": price, "url": link})
        except Exception as e:
            print(f"Tile parse error: {e}")
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

                # Try direct API first (faster, no bot detection issue)
                products = search_products_api(query, max_price)
                if not products:
                    print("API failed, falling back to browser...")
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
