# utils/video_parser.py
from playwright.async_api import async_playwright

IGNORE_LIST = ["example.com", ...]  # Add domains from repo

async def extract_m3u8_link(url: str, cookie_path: str = None) -> str:
    # skip ignored domains
    for d in IGNORE_LIST:
        if d in url:
            raise Exception(f"Domain {d} not supported")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        # load cookies
        if cookie_path:
            with open(cookie_path) as f:
                raw = f.read()
                cookies = [{"name":n,"value":v,"domain":".hotstar.com"} for n,v in (c.split("=",1) for c in raw.split(";"))]
                await ctx.add_cookies(cookies)
        page = await ctx.new_page()
        await page.goto(url, wait_until="networkidle")
        m3u8 = None
        page.on("request", lambda req: req.url if '.m3u8' in req.url.lower() else None)
        await page.wait_for_timeout(7000)
        await browser.close()
        if not m3u8:
            raise Exception("Failed to find m3u8 URL")
        return m3u8
