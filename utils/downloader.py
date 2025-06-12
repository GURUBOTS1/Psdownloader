import os
import aiohttp
import asyncio
import subprocess
from utils.ffmpeg_merge import merge_streams


async def download_file(url: str, headers: dict, output: str) -> None:
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to download {url}: {resp.status}")
            with open(output, "wb") as f:
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)


def _cookie_header(cookie_file: str) -> str:
    if not cookie_file or not os.path.exists(cookie_file):
        return ""
    with open(cookie_file, "r") as f:
        return f"cookie: {f.read().strip()}"


async def process_m3u8_video(m3u8_url: str, cookie_path: str = None) -> str:
    output_name = "output.mp4"
    temp_audio = "audio.ts"
    temp_video = "video.ts"

    headers = {}
    cookie_header = _cookie_header(cookie_path)
    if cookie_header:
        headers["Cookie"] = cookie_header.replace("cookie: ", "")

    # Use FFmpeg to download both streams (for best compatibility)
    command = [
        "ffmpeg",
        "-headers", f"Cookie: {headers['Cookie']}" if 'Cookie' in headers else "",
        "-i", m3u8_url,
        "-c", "copy",
        output_name
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"FFmpeg failed: {stderr.decode()}")

    return output_name
