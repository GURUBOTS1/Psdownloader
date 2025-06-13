import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

from utils.cookie_store import save_cookie, get_cookie, is_admin
from utils.downloader import process_m3u8_video
from utils.video_parser import extract_m3u8_link

load_dotenv()
logging.basicConfig(level=logging.INFO)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS").split(',')))
MONGO_URI = os.getenv("MONGO_URI")

app = Client("video_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    if is_admin(message.from_user.id, ADMIN_IDS):
        await message.reply(
            "👋 Welcome, Admin!\nSend any OTT `.m3u8` link or full video URL (e.g., Hotstar),\n\nUse /setcookies to upload cookies."
        )
    else:
        await message.reply("❌ This bot is restricted to admins only.")


@app.on_message(filters.command("setcookies") & filters.private)
async def set_cookies(client, message: Message):
    if not is_admin(message.from_user.id, ADMIN_IDS):
        return await message.reply("❌ You are not allowed to do this.")

    if not message.document:
        return await message.reply("📎 Please upload your cookies file (e.g., `.txt` or `.json`).")

    os.makedirs("cookies", exist_ok=True)
    file_path = f"cookies/{message.from_user.id}_{message.document.file_name}"
    await message.download(file_path)
    save_cookie(MONGO_URI, message.from_user.id, file_path)
    await message.reply("✅ Cookies saved successfully and will be reused until expiry.")


@app.on_message(filters.text & filters.private)
async def handle_link(client, message: Message):
    if not is_admin(message.from_user.id, ADMIN_IDS):
        return

    url = message.text.strip()
    cookie_path = get_cookie(MONGO_URI, message.from_user.id)

    try:
        if url.endswith(".m3u8"):
            await message.reply("⏳ Processing direct .m3u8 stream...")
            output_file = await process_m3u8_video(url, cookie_path)
        else:
            await message.reply("🔎 Extracting video stream link...")
            m3u8_url = await extract_m3u8_link(url, cookie_path)
            await message.reply(f"🎯 Found `.m3u8` link:\n`{m3u8_url}`\n⏳ Now downloading...")
            output_file = await process_m3u8_video(m3u8_url, cookie_path)

        await message.reply_video(output_file, caption="✅ Here is your video.")
        os.remove(output_file)

    except Exception as e:
        logging.exception("Error processing link")
        await message.reply(f"❌ Error while processing link: {e}")


if __name__ == "__main__":
    app.run()
