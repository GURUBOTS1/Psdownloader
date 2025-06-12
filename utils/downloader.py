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
        return f.read().strip()


async def process_m3u8_video(m3u8_url: str, cookie_path: str = None) -> str:
    output_name = "output.mp4"

    # Prepare headers if cookie is provided
    cookie = _cookie_header(cookie_path)
    headers_option = []
    if cookie:
        headers_option = ["-headers", f"Cookie: {cookie}"]

    # FFmpeg command to download and merge streams
    command = [
        "ffmpeg",
        *headers_option,
        "-i", m3u8_url,
        "-c", "copy",
        "-bsf:a", "aac_adtstoasc",
        "-loglevel", "error",
        output_name
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"FFmpeg failed:\n{stderr.decode().strip()}")

    return output_name
