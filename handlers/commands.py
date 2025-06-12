# handlers/commands.py

from pyrogram import Client, filters
from pyrogram.types import Message
from utils.cookie_store import save_cookie, is_admin
from templates.start_msg import START_MESSAGE
import os

@Client.on_message(filters.command("start"))
async def start_command(client, message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply("🚫 You are not authorized to use this bot.")
    await message.reply(START_MESSAGE, disable_web_page_preview=True)

@Client.on_message(filters.command("setcookies"))
async def set_cookies(client, message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply("🚫 You are not authorized to use this command.")
    
    if not message.document:
        return await message.reply("📎 Please upload a `.txt` or `.json` file containing your OTT platform cookies.")

    file_path = f"/tmp/{message.document.file_name}"
    await message.download(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        cookie_data = f.read()

    os.remove(file_path)

    platform = message.command[1] if len(message.command) > 1 else "generic"
    save_cookie(user_id=message.from_user.id, platform=platform, cookie_text=cookie_data)

    await message.reply(f"✅ Cookie for **{platform}** saved successfully.")

