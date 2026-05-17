"""
GitHub Actions Browser Relay Runner.
Reads .relay/request.json, executes the task, writes .relay/result.json.
"""

import json
import os
import re
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

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


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


def search_hotline_browser(page, query: str, max_price: int) -> tuple:
    """Scrape hotline.ua — Ukrainian price comparison site, simple HTML, less protected."""
    debug = []
    q = query.replace(' ', '+')
    url = f"https://hotline.ua/ua/search/query/?q={q}"

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        screenshot(page, "hotline_search")
        debug.append(f"hotline.ua: {page.title()}")

        # Extract products via JS from hotline's HTML structure
        products = page.evaluate("""(maxPrice) => {
            const results = [];
            // hotline.ua product cards
            const cards = document.querySelectorAll('.list-item, .hl-product-card, [class*="product-item"]');
            cards.forEach(card => {
                const nameEl = card.querySelector('a.name, .hl-name, h2 a, h3 a, [class*="name"] a, a[title]');
                const priceEl = card.querySelector('.price-box span, .hl-price, [class*="price"] span, .price');
                if (nameEl && priceEl) {
                    const priceText = priceEl.textContent.replace(/[^0-9]/g, '');
                    const price = parseInt(priceText);
                    if (price > 0 && price <= maxPrice) {
                        results.push({
                            name: nameEl.textContent.trim() || nameEl.title,
                            price: price,
                            url: nameEl.href || '',
                            shop: 'hotline.ua'
                        });
                    }
                }
            });
            return results.slice(0, 10);
        }""", max_price)

        debug.append(f"hotline.ua JS: {len(products)} products")
        if products:
            return products, debug

        # Fallback: text content
        body = page.evaluate("document.body.innerText")[:2000]
        debug.append(f"hotline body snippet: {body[:200]}")
        Path(".relay/debug_hotline.txt").write_text(body)
        html = page.content()
        Path(".relay/debug_hotline.html").write_text(html[:80000])

    except Exception as e:
        debug.append(f"hotline browser error: {e}")

    return [], debug


def search_comfy_browser(page, query: str, max_price: int) -> tuple:
    """Scrape comfy.ua — Ukrainian electronics retailer."""
    debug = []
    q = query.replace(' ', '+')
    url = f"https://comfy.ua/ua/search/?search={q}"
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(4)
        screenshot(page, "comfy_search")
        debug.append(f"comfy.ua: {page.title()}")

        products = page.evaluate("""(maxPrice) => {
            const results = [];
            const cards = document.querySelectorAll('.products-list__item, .product-card, [class*="product"]');
            cards.forEach(card => {
                const nameEl = card.querySelector('a.product-card__title, .product-card__name, h2, h3, a[title]');
                const priceEl = card.querySelector('.product-card__price, .price, [class*="price"]');
                const linkEl = card.querySelector('a[href*="comfy.ua"], a[href^="/ua/"]');
                if (nameEl && priceEl) {
                    const priceText = priceEl.textContent.replace(/[^0-9]/g, '');
                    const price = parseInt(priceText);
                    if (price > 0 && price <= maxPrice) {
                        results.push({
                            name: nameEl.textContent.trim() || nameEl.title,
                            price: price,
                            url: (linkEl && (linkEl.href.startsWith('http') ? linkEl.href : 'https://comfy.ua' + linkEl.getAttribute('href'))) || '',
                            shop: 'comfy.ua'
                        });
                    }
                }
            });
            return results.slice(0, 10);
        }""", max_price)

        debug.append(f"comfy.ua JS: {len(products)} products")
        if products:
            return products, debug

        html = page.content()
        Path(".relay/debug_comfy.html").write_text(html[:80000])
        debug.append(f"comfy body: {page.evaluate('document.body.innerText')[:200]}")

    except Exception as e:
        debug.append(f"comfy browser error: {e}")

    return [], debug


def search_rozetka_browser_full(page, query: str, max_price: int) -> tuple:
    """Rozetka with full cookie warmup — visits API subdomain first."""
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
                    debug.append(f"Captured: {url[:80]} → {len(goods)} items")
            except Exception:
                pass

    page.on("response", handle_response)

    # Warm up: visit homepage first
    page.goto("https://rozetka.com.ua/ua/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    debug.append(f"Homepage: {page.title()}")
    screenshot(page, "rz_homepage")

    # Navigate to search
    search_url = f"https://rozetka.com.ua/ua/search/?text={query.replace(' ', '+')}&price=0;{max_price}&sort=popular"
    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    screenshot(page, "rz_search_01")

    # Wait longer for Angular to load
    try:
        page.wait_for_selector("app-goods-tile-default, .goods-tile__title", timeout=50000)
        debug.append("Product tiles appeared!")
        time.sleep(2)
    except Exception:
        debug.append("No product tiles after 50s wait")
        time.sleep(10)

    screenshot(page, "rz_search_02")
    html = page.content()
    Path(".relay/debug_page.html").write_text(html[:80000])

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
            debug.append(f"API interception: {len(products)} products")
            return products[:10], debug

    # JS DOM
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

    body = page.evaluate("document.body.innerText")[:2000]
    Path(".relay/debug_body.txt").write_text(body)
    debug.append(f"Body snippet: {body[:200]}")
    return [], debug


def add_to_cart(page, product_url: str) -> dict:
    page.goto(product_url, wait_until="domcontentloaded", timeout=30000)
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
                  "--disable-blink-features=AutomationControlled",
                  "--disable-web-security"],
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

        try:
            if action in ("search", "fetch_api"):
                query = request.get("query", "")
                max_price = request.get("max_price", 999999)
                all_debug = []
                products = []

                # 1. Try hotline.ua (price comparison, simpler HTML)
                print("Trying hotline.ua...")
                products, debug = search_hotline_browser(page, query, max_price)
                all_debug.extend(debug)

                # 2. Try comfy.ua
                if not products:
                    print("Trying comfy.ua...")
                    products, debug = search_comfy_browser(page, query, max_price)
                    all_debug.extend(debug)

                # 3. Try Rozetka with full warmup
                if not products:
                    print("Trying Rozetka with full warmup...")
                    products, debug = search_rozetka_browser_full(page, query, max_price)
                    all_debug.extend(debug)

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
                    products, _ = search_rozetka_browser_full(page, query, max_price)
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
