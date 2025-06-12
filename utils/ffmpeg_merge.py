import asyncio
import logging

async def merge_streams(video_path: str, audio_path: str, output_path: str):
    """
    Merges video and audio into one .mp4 file using ffmpeg.
    If only video is provided, it will just repackage it.
    """
    if audio_path:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-c", "copy",
            output_path
        ]

    logging.info("Merging streams...")
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"Merge failed: {stderr.decode()}")
