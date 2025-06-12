# handlers/file_sender.py

import os
from pyrogram import Client
from pyrogram.types import Message

async def send_video(client: Client, user_id: int, file_path: str, caption: str = None):
    try:
        if os.path.exists(file_path):
            await client.send_document(
                chat_id=user_id,
                document=file_path,
                caption=caption or "✅ Here is your downloaded video.",
                force_document=True  # Avoid compression
            )
            os.remove(file_path)  # Clean up after sending
        else:
            await client.send_message(user_id, "❌ Video file not found.")
    except Exception as e:
        await client.send_message(user_id, f"⚠️ Error sending file: {str(e)}")
