import os
import uuid
import asyncio
import subprocess

async def process_m3u8_video(url, cookie_path=None):
    output_filename = f"downloads/{uuid.uuid4()}.mp4"
    os.makedirs("downloads", exist_ok=True)

    # Prepare ffmpeg command
    command = [
        "ffmpeg", "-y", "-i", url, "-c", "copy", output_filename
    ]

    if cookie_path:
        command = [
            "ffmpeg", "-y", "-headers", f"cookie: {open(cookie_path).read().strip()}",
            "-i", url, "-c", "copy", output_filename
        ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"ffmpeg error: {stderr.decode()}")

    return output_filename
