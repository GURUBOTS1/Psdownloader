import os
from pymongo import MongoClient

def is_admin(user_id, admin_ids):
    return int(user_id) in admin_ids

def save_cookie(mongo_uri, user_id, file_path):
    client = MongoClient(mongo_uri)
    db = client['video_bot']
    collection = db['cookies']

    with open(file_path, 'r') as f:
        content = f.read()

    collection.update_one(
        {"user_id": user_id},
        {"$set": {"cookie": content, "filename": os.path.basename(file_path)}},
        upsert=True
    )
    client.close()

def get_cookie(mongo_uri, user_id):
    client = MongoClient(mongo_uri)
    db = client['video_bot']
    collection = db['cookies']

    record = collection.find_one({"user_id": user_id})
    client.close()

    if record and "cookie" in record:
        os.makedirs("cookies", exist_ok=True)
        cookie_path = f"cookies/{user_id}_{record.get('filename', 'cookie.txt')}"
        with open(cookie_path, 'w') as f:
            f.write(record["cookie"])
        return cookie_path
    else:
        return None
