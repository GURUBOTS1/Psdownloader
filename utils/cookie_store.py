import os
import pymongo


def get_db_client(mongo_uri):
    return pymongo.MongoClient(mongo_uri)


def save_cookie(mongo_uri, user_id, file_path):
    client = get_db_client(mongo_uri)
    db = client["video_bot"]
    cookies = db["cookies"]

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    cookies.update_one(
        {"user_id": user_id},
        {"$set": {"cookie_data": content}},
        upsert=True
    )


def get_cookie(mongo_uri, user_id):
    client = get_db_client(mongo_uri)
    db = client["video_bot"]
    cookies = db["cookies"]

    record = cookies.find_one({"user_id": user_id})
    if record and "cookie_data" in record:
        tmp_path = f"/tmp/{user_id}_cookie.txt"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(record["cookie_data"])
        return tmp_path
    return None


def is_admin(user_id, admin_ids):
    return user_id in admin_ids
