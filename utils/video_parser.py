# utils/video_parser.py

import m3u8
import requests
import re

def fetch_m3u8_playlist(url: str, headers: dict = None) -> m3u8.M3U8:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return m3u8.loads(response.text)

def parse_variants(playlist: m3u8.M3U8) -> list:
    variants = []
    for p in playlist.playlists:
        quality = p.stream_info.resolution
        bandwidth = p.stream_info.bandwidth
        uri = p.uri
        lang_match = re.search(r'lang=([a-zA-Z-]+)', uri)
        language = lang_match.group(1) if lang_match else "Unknown"
        variants.append({
            "uri": uri,
            "resolution": f"{quality[0]}x{quality[1]}" if quality else "Audio",
            "bandwidth": bandwidth,
            "language": language
        })
    return variants

def is_audio_video_separate(playlist: m3u8.M3U8) -> bool:
    return bool(playlist.media and len(playlist.media) > 0)
