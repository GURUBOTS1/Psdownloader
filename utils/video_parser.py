# utils/video_parser.py

import asyncio
from playwright.async_api import async_playwright


async def extract_m3u8_link(url: str, cookie_path: str = None) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # If user provided cookies, load them
        if cookie_path:
            with open(cookie_path, 'r') as f:
                raw_cookie = f.read().strip()
            cookies = []
            for item in raw_cookie.split(';'):
                if '=' in item:
                    name, value = item.strip().split('=', 1)
                    cookies.append({
                        'name': name,
                        'value': value,
                        'domain': '.' + url.split('/')[2],
                    })
            await context.add_cookies(cookies)

        page = await context.new_page()

        # Listen for .m3u8 requests
        m3u8_url = None

        async def capture_route(route):
            nonlocal m3u8_url
            if ".m3u8" in route.request.url:
                m3u8_url = route.request.url
            await route.continue_()

        await context.route("**/*", capture_route)

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(10)  # wait for player to load and request m3u8
        finally:
            await browser.close()

        if not m3u8_url:
            raise Exception("❌ Failed to find any .m3u8 link on the page.")

        return m3u8_url
