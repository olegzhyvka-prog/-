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
try:
    from playwright_stealth import stealth_sync
except ImportError:
    stealth_sync = None

REQUEST_FILE = Path(".relay/request.json")
RESULT_FILE = Path(".relay/result.json")
SCREENSHOTS_DIR = Path(".relay/screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def screenshot(page, name: str) -> str:
    path = SCREENSHOTS_DIR / f"{name}.png"
    page.screenshot(path=str(path))
    return str(path)


def wait_past_cloudflare(page, timeout_s: int = 30) -> bool:
    """Wait for Cloudflare challenge page to pass. Returns True if passed."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            title = page.title()
            snippet = page.evaluate("document.body ? document.body.innerText.substring(0, 300) : ''")
        except Exception:
            snippet = ""
        if ("Just a moment" not in title and
                "перевірка безпеки" not in snippet and
                "безпеки" not in title and
                title != ""):
            return True
        print(f"  CF challenge active (title={title!r}), waiting...")
        time.sleep(3)
    return False


def login_rozetka(page) -> dict:
    phone = os.environ.get("ROZETKA_PHONE", "")
    password = os.environ.get("ROZETKA_PASSWORD", "")
    if not phone or not password:
        return {"logged_in": False, "reason": "No credentials in GitHub Secrets"}
    page.goto("https://rozetka.com.ua/ua/", wait_until="domcontentloaded")
    wait_past_cloudflare(page, timeout_s=20)
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
        wait_past_cloudflare(page, timeout_s=20)
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


def search_rozetka_browser(page, query: str, max_price: int) -> tuple:
    """Rozetka browser search with Cloudflare challenge handling."""
    debug = []
    api_responses = []

    def handle_response(response):
        url = response.url
        if any(x in url for x in ["catalog-api", "goods/get", "search/api", "xl-catalog", "product-api"]):
            try:
                body = response.json()
                goods = (body.get("data", {}).get("goods") or
                         (body.get("data") if isinstance(body.get("data"), list) else None))
                if goods:
                    api_responses.append(goods)
                    debug.append(f"Captured API: {url[:80]} → {len(goods)} items")
            except Exception:
                pass

    page.on("response", handle_response)

    # Go directly to search page (no homepage warmup, it seems to make things worse)
    search_url = f"https://rozetka.com.ua/ua/search/?text={query.replace(' ', '+')}&price=0;{max_price}&sort=popular"
    print(f"Navigating to: {search_url}")
    page.goto(search_url, wait_until="domcontentloaded", timeout=40000)
    screenshot(page, "01_initial")

    # Wait for Cloudflare challenge to pass (up to 30 seconds)
    passed = wait_past_cloudflare(page, timeout_s=30)
    debug.append(f"CF challenge passed: {passed}, title after: {page.title()!r}")
    screenshot(page, "02_after_cf")

    # Now wait for Angular product tiles (up to 45 more seconds)
    print("Waiting for product tiles...")
    try:
        page.wait_for_selector(
            "app-goods-tile-default, .goods-tile__title, a.goods-tile__heading",
            timeout=45000
        )
        debug.append("Product tiles appeared!")
        time.sleep(2)
    except Exception:
        debug.append("Product tiles timeout")
        time.sleep(5)

    screenshot(page, "03_final")
    html = page.content()
    Path(".relay/debug_page.html").write_text(html[:80000])

    # Body text for diagnosis
    body = page.evaluate("document.body.innerText")[:1000]
    debug.append(f"Body: {body[:300]}")
    Path(".relay/debug_body.txt").write_text(body)

    # Method 1: Intercepted API responses
    if api_responses:
        products = []
        for goods in api_responses:
            for g in goods[:10]:
                p = {"name": g.get("title", g.get("full_name", "")),
                     "price": int(g.get("price", 0)),
                     "url": g.get("href", g.get("url", "")),
                     "shop": "rozetka.com.ua"}
                if p["name"] and p["price"] > 0:
                    products.append(p)
        if products:
            debug.append(f"API interception: {len(products)} products found")
            return products[:10], debug

    # Method 2: JS DOM extraction
    try:
        js_products = page.evaluate("""(maxPrice) => {
            const results = [];
            document.querySelectorAll('app-goods-tile-default, li.catalog-grid__cell').forEach(tile => {
                const nameEl = tile.querySelector('a.goods-tile__heading, .goods-tile__title');
                const priceEl = tile.querySelector('.goods-tile__price-value');
                const linkEl = tile.querySelector('a[href*="rozetka"]');
                if (nameEl && priceEl) {
                    const price = parseInt(priceEl.textContent.replace(/\\D/g, ''));
                    if (price > 0 && price <= maxPrice) {
                        results.push({name: nameEl.textContent.trim(), price, url: linkEl ? linkEl.href : '', shop: 'rozetka.com.ua'});
                    }
                }
            });
            return results;
        }""", max_price)
        if js_products:
            debug.append(f"JS DOM: {len(js_products)} products")
            return js_products[:10], debug
    except Exception as e:
        debug.append(f"JS DOM error: {e}")

    return [], debug


def add_to_cart(page, product_url: str) -> dict:
    page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
    wait_past_cloudflare(page, timeout_s=20)
    time.sleep(3)
    screenshot(page, "04_product_page")
    for sel in ["button.buy-button", "button.product-buy__btn", "rz-buy-button button",
                "button:has-text('Купити')", "button:has-text('Додати в кошик')"]:
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
            args=["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=UA,
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
                products, debug = search_rozetka_browser(page, query, max_price)
                result["status"] = "ok"
                result["data"] = {"products": products, "count": len(products), "debug": debug}

            elif action == "add_to_cart":
                query = request.get("query", "")
                max_price = request.get("max_price", 999999)
                login_result = login_rozetka(page)
                result["data"]["login"] = login_result
                if not login_result.get("logged_in"):
                    result["status"] = "login_failed"
                else:
                    products, debug = search_rozetka_browser(page, query, max_price)
                    result["data"]["debug"] = debug
                    if not products:
                        result["status"] = "no_products"
                    else:
                        best = sorted(products, key=lambda x: x["price"])[0]
                        result["data"]["selected"] = best
                        cart_result = add_to_cart(page, best["url"])
                        result["data"]["cart"] = cart_result
                        result["status"] = "ok" if cart_result["success"] else "cart_failed"

            elif action == "add_to_cart_url":
                # Add specific product (by URL) to cart — bypasses search
                url = request.get("url", "")
                login_result = login_rozetka(page)
                result["data"]["login"] = login_result
                if not login_result.get("logged_in"):
                    result["status"] = "login_failed"
                else:
                    cart_result = add_to_cart(page, url)
                    result["data"]["cart"] = cart_result
                    result["data"]["product_url"] = url
                    result["status"] = "ok" if cart_result["success"] else "cart_failed"

            elif action == "fetch_url":
                url = request.get("url", "")
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                wait_past_cloudflare(page, timeout_s=20)
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
