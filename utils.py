import os
import subprocess
import tempfile
from pymongo import MongoClient
from datetime import datetime
import m3u8
import aiohttp
import asyncio

def is_admin(user_id: int, admin_list: list):
    return user_id in admin_list

def save_cookie(mongo_uri, user_id, cookie_path):
    client = MongoClient(mongo_uri)
    db = client["video_bot"]
    col = db["cookies"]
    with open(cookie_path, "r") as f:
        cookie_data = f.read()

    col.update_one(
        {"user_id": user_id},
        {"$set": {"cookie": cookie_data, "updated_at": datetime.utcnow()}},
        upsert=True
    )
    client.close()

def get_cookie(mongo_uri, user_id):
    client = MongoClient(mongo_uri)
    db = client["video_bot"]
    col = db["cookies"]
    user = col.find_one({"user_id": user_id})
    client.close()
    if user:
        path = f"cookies/{user_id}_active_cookie.txt"
        with open(path, "w") as f:
            f.write(user['cookie'])
        return path
    return None

async def download_segment(session, url, headers, output_path):
    async with session.get(url, headers=headers) as resp:
        if resp.status == 200:
            with open(output_path, "wb") as f:
                f.write(await resp.read())

async def process_m3u8_video(m3u8_url, cookie_path=None):
    headers = {}
    if cookie_path:
        with open(cookie_path, "r") as f:
            cookies = f.read().replace("\n", "; ")
            headers["cookie"] = cookies

    async with aiohttp.ClientSession() as session:
        playlist = m3u8.load(m3u8_url, headers=headers)
        best_stream = playlist.playlists[-1] if playlist.playlists else playlist

        if hasattr(best_stream, 'uri'):
            m3u8_url = best_stream.uri
            playlist = m3u8.load(m3u8_url, headers=headers)

        segment_urls = [seg.uri for seg in playlist.segments]
        temp_dir = tempfile.mkdtemp()
        segment_files = []

        for i, seg_url in enumerate(segment_urls):
            seg_path = os.path.join(temp_dir, f"seg{i}.ts")
            await download_segment(session, seg_url, headers, seg_path)
            segment_files.append(seg_path)

        joined_file = os.path.join(temp_dir, "output.ts")
        with open(joined_file, "wb") as outfile:
            for fname in segment_files:
                with open(fname, "rb") as infile:
                    outfile.write(infile.read())

        final_output = os.path.join(temp_dir, "final.mp4")
        cmd = ["ffmpeg", "-y", "-i", joined_file, "-c", "copy", final_output]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return final_output
      
