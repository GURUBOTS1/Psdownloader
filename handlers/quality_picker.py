# handlers/quality_picker.py

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.video_parser import extract_stream_details

@Client.on_message(filters.text & filters.private)
async def handle_stream_url(client, message: Message):
    url = message.text.strip()

    if not url.endswith(".m3u8"):
        return await message.reply("❌ Invalid URL. Please send a direct `.m3u8` video link.")

    try:
        languages, qualities = extract_stream_details(url)
    except Exception as e:
        return await message.reply(f"⚠️ Error parsing stream: {str(e)}")

    # Save URL in user_data (for future selection step)
    client.user_data[message.from_user.id] = {"url": url}

    # Ask for language selection
    lang_buttons = [[InlineKeyboardButton(lang, callback_data=f"lang|{lang}")] for lang in languages]
    await message.reply("🌐 Select Language:", reply_markup=InlineKeyboardMarkup(lang_buttons))


@Client.on_callback_query(filters.regex(r"lang\|"))
async def select_language(client, callback_query: CallbackQuery):
    lang = callback_query.data.split("|")[1]
    user_id = callback_query.from_user.id

    if user_id not in client.user_data:
        return await callback_query.answer("❌ Session expired. Please send the URL again.", show_alert=True)

    client.user_data[user_id]["language"] = lang

    # Now show quality options
    _, qualities = extract_stream_details(client.user_data[user_id]["url"])
    quality_buttons = [[InlineKeyboardButton(q, callback_data=f"quality|{q}")] for q in qualities]

    await callback_query.message.edit_text("📺 Select Quality:", reply_markup=InlineKeyboardMarkup(quality_buttons))


@Client.on_callback_query(filters.regex(r"quality\|"))
async def select_quality(client, callback_query: CallbackQuery):
    quality = callback_query.data.split("|")[1]
    user_id = callback_query.from_user.id

    if user_id not in client.user_data or "language" not in client.user_data[user_id]:
        return await callback_query.answer("❌ Session expired. Please send the URL again.", show_alert=True)

    client.user_data[user_id]["quality"] = quality
    await callback_query.message.edit_text("🎬 Starting download...")

    # Pass to downloader
    from downloader import process_download
    await process_download(client, user_id, client.user_data[user_id])
