import os
import uuid
import asyncio
import logging
import tempfile
from utils.ffmpeg_merge import merge_streams

async def process_m3u8_video(m3u8_url: str, cookie_file: str = None) -> str:
    """
    Downloads video/audio streams from .m3u8 and merges them into a single MP4.
    """
    logging.info(f"Processing: {m3u8_url}")
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "video.ts")
    audio_path = os.path.join(temp_dir, "audio.ts")
    output_path = os.path.join("downloads", f"{uuid.uuid4().hex}.mp4")
    os.makedirs("downloads", exist_ok=True)

    base_command = [
        "ffmpeg", "-y", "-headers", _cookie_header(cookie_file)
    ] if cookie_file else ["ffmpeg", "-y"]

    video_cmd = base_command + ["-i", m3u8_url, "-c", "copy", "-bsf:a", "aac_adtstoasc", video_path]

    try:
        await _run(video_cmd)
        # Attempt merge even if single stream
        await merge_streams(video_path, None, output_path)
        return output_path
    finally:
        for f in [video_path, audio_path, temp_dir]:
            if f and os.path.exists(f):
                try:
                    os.remove(f) if os.path.isfile(f) else os.rmdir(f)

def _cookie_header(cookie_file: str) -> str:
    if not cookie_file or not os.path.exists(cookie_file):
        return ""
    with open(cookie_file, "r") as f:
        cookies = f.read().strip().replace("\n", "").replace("\r", "")
        return f"Cookie: {cookies}\\r\\n"

async def _run(cmd):
    logging.info("Running: %s", " ".join(cmd))
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg failed: {stderr.decode()}")
