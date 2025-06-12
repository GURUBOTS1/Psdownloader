import asyncio
import os
from playwright.async_api import async_playwright

async def extract_m3u8_link(url: str, cookie_path: str = None) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context_args = {}

        if cookie_path and os.path.exists(cookie_path):
            import json
            with open(cookie_path, 'r') as f:
                cookies = json.load(f)
            context_args['storage_state'] = {'cookies': cookies}

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        m3u8_link = None

        async def handle_response(response):
            nonlocal m3u8_link
            try:
                if ".m3u8" in response.url and "drm" not in response.url.lower():
                    m3u8_link = response.url
            except:
                pass

        page.on("response", handle_response)
        await page.goto(url, timeout=60000)

        await asyncio.sleep(10)  # wait for all requests
        await browser.close()

        if not m3u8_link:
            raise Exception("No .m3u8 stream found. Possibly DRM-protected or login required.")
        return m3u8_link
