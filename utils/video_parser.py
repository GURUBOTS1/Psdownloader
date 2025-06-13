import re
import requests
from bs4 import BeautifulSoup

async def extract_m3u8_link(url: str, cookie_path: str = None) -> str:
    headers = {}
    if cookie_path:
        with open(cookie_path, "r") as f:
            headers["Cookie"] = f.read().strip()

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception("Failed to fetch the page")

    html = res.text

    # Extract .m3u8 URLs
    matches = re.findall(r'https://[^"]+\.m3u8[^"]*', html)
    if not matches:
        raise Exception("No m3u8 link found")
    
    return matches[0]  # Return the first found .m3u8 link
