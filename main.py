import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import (
    is_admin,
    save_cookie,
    get_cookie,
    process_m3u8_video,
)
from dotenv import load_dotenv
from aiohttp import web

load_dotenv()

logging.basicConfig(level=logging.INFO)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS").split(',')))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8080))
MONGO_URI = os.getenv("MONGO_URI")

app = Client("video_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    if is_admin(message.from_user.id, ADMIN_IDS):
        await message.reply("👋 Welcome, Admin! Send any OTT `.m3u8` link or use /setcookies to upload cookies.")
    else:
        await message.reply("❌ This bot is restricted to admins only.")


@app.on_message(filters.command("setcookies") & filters.private)
async def set_cookies(client, message: Message):
    if not is_admin(message.from_user.id, ADMIN_IDS):
        return await message.reply("❌ You are not allowed to do this.")

    if not message.document:
        return await message.reply("📎 Please upload your cookies file (e.g., `.txt` or `.json`).")

    file_path = f"cookies/{message.from_user.id}_{message.document.file_name}"
    await message.download(file_path)
    save_cookie(MONGO_URI, message.from_user.id, file_path)
    await message.reply("✅ Cookies saved successfully and will be reused until expiry.")


@app.on_message(filters.text & filters.private)
async def handle_link(client, message: Message):
    if not is_admin(message.from_user.id, ADMIN_IDS):
        return

    url = message.text.strip()
    if not url.endswith(".m3u8"):
        return await message.reply("❌ Not a valid `.m3u8` link.")

    await message.reply("⏳ Processing your video...")

    cookie_path = get_cookie(MONGO_URI, message.from_user.id)
    try:
        output_file = await process_m3u8_video(url, cookie_path)
        await message.reply_video(output_file, caption="✅ Here is your video.")
        os.remove(output_file)
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")


# Webhook health check & webhook setup
async def handle_healthcheck(request):
    return web.Response(text="OK")

async def start_webhook():
    await app.start()
    runner = web.AppRunner(web.Application())
    site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
    await site.start()
    await app.set_webhook(WEBHOOK_URL)
    print("✅ Bot ready via webhook.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_webhook())
  
