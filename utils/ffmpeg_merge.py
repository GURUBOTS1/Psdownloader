# utils/ffmpeg_merge.py

import subprocess
import os
import uuid

def merge_audio_video(video_path: str, audio_path: str) -> str:
    output_path = f"/tmp/merged_{uuid.uuid4().hex[:8]}.mp4"
    
    command = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        output_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    except subprocess.CalledProcessError as e:
        print("FFmpeg merge error:", e)
        return None
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
