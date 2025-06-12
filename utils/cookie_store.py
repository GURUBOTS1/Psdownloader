# utils/cookie_store.py

from pymongo import MongoClient
import os
import datetime

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["ott_bot"]
cookie_col = db["cookies"]

def save_cookie(admin_id: int, cookie_str: str) -> None:
    cookie_col.update_one(
        {"admin_id": admin_id},
        {
            "$set": {
                "cookie": cookie_str,
                "updated_at": datetime.datetime.utcnow()
            }
        },
        upsert=True
    )

def get_cookie(admin_id: int) -> str | None:
    record = cookie_col.find_one({"admin_id": admin_id})
    if record:
        return record["cookie"]
    return None

def cookie_exists(admin_id: int) -> bool:
    return cookie_col.count_documents({"admin_id": admin_id}) > 0
