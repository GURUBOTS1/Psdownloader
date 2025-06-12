from pyrogram import Client, filters
from pyrogram.types import Message
from utils import save_cookies, get_cookie
import os

ADMIN_IDS = list(map(int, os.getenv("ADMINS", "").split()))

def is_admin():
    return filters.user(ADMIN_IDS)

@Client.on_message(filters.command("setcookies") & is_admin())
async def set_cookies(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("❌ Reply to a text file (.txt or .json) containing cookies.")

    doc = message.reply_to_message.document
    if doc.mime_type not in ["text/plain", "application/json"]:
        return await message.reply("⚠️ Only .txt or .json files are allowed.")

    path = await doc.download()
    try:
        with open(path, "r") as f:
            content = f.read().strip()
            if not content:
                return await message.reply("❌ File is empty.")

        save_cookies(message.from_user.id, content)
        await message.reply("✅ Cookie saved successfully and will be used for future downloads.")
    except Exception as e:
        await message.reply(f"❌ Error saving cookies: `{e}`")
    finally:
        os.remove(path)

@Client.on_message(filters.command("getcookies") & is_admin())
async def get_cookies(client: Client, message: Message):
    cookie = get_cookie(message.from_user.id)
    if cookie:
        await message.reply(f"🍪 Your current saved cookie:\n\n`{cookie[:400]}...`", quote=True)
    else:
        await message.reply("❌ No cookie found for you. Use /setcookies by replying to a .txt or .json file.")

@Client.on_message(filters.command("clearcookies") & is_admin())
async def clear_cookies(client: Client, message: Message):
    from pymongo import MongoClient
    mongo = MongoClient(os.getenv("MONGO_URI"))
    cookie_col = mongo['video_downloader']['cookies']
    result = cookie_col.delete_one({"user_id": message.from_user.id})
    if result.deleted_count:
        await message.reply("🧹 Cookie cleared.")
    else:
        await message.reply("⚠️ No cookie to clear.")

@Client.on_message(filters.command("status") & is_admin())
async def check_status(client: Client, message: Message):
    cookie = get_cookie(message.from_user.id)
    await message.reply(
        f"🧾 **Status Report**\n\n"
        f"👤 Admin ID: `{message.from_user.id}`\n"
        f"🍪 Cookie: {'✅ Set' if cookie else '❌ Not Set'}\n"
    )
