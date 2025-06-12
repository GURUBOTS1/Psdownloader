from playwright.async_api import async_playwright


async def extract_m3u8_link(url: str, cookie_path: str = None) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Set cookies if available
        if cookie_path:
            with open(cookie_path, "r", encoding="utf-8") as f:
                raw_cookie = f.read().strip()
                # Convert raw cookie string to browser cookie format
                cookies = []
                for item in raw_cookie.split(";"):
                    if "=" in item:
                        name, value = item.strip().split("=", 1)
                        cookies.append({
                            "name": name.strip(),
                            "value": value.strip(),
                            "domain": ".hotstar.com"
                        })
                await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto(url, wait_until="networkidle")

        # Extract m3u8 link from network logs
        m3u8_url = None
        async def log_request(route):
            nonlocal m3u8_url
            if ".m3u8" in route.request.url and "drm" not in route.request.url.lower():
                m3u8_url = route.request.url

        page.on("request", log_request)

        await page.wait_for_timeout(5000)  # wait 5 seconds for all network calls
        await browser.close()

        if not m3u8_url:
            raise Exception("❌ .m3u8 link not found.")

        return m3u8_url
