# Thumbnail Changer Bot !!
# Made By Flexyy Team dByte !!
# Telegram Username:- @xFlexyy
# Community:- @DragonByte_Network

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from config import MONGO_URL, DB_NAME, OWNER_ID
import datetime  # ⬅️ YEH ADD KARNA HI KARNA HAI

client: AsyncIOMotorClient = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    await db.users.create_index("user_id", unique=True)
    await db.admins.create_index("user_id", unique=True)
    await db.settings.create_index("key", unique=True)
    await db.urls.create_index("url", unique=True)
    
    await add_admin(OWNER_ID)
    print("✅ MongoDB connected")

async def close_db():
    global client
    if client:
        client.close()

# ==================== USER FUNCTIONS ====================

async def add_user(user_id: int, username: str = None, first_name: str = None):
    await db.users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "username": username,
                "first_name": first_name
            },
            "$setOnInsert": {
                "user_id": user_id,
                "thumbnail_file_id": None,
                "usage_count": 0,
                "banned": False
            }
        },
        upsert=True
    )

async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    return await db.users.find_one({"user_id": user_id})

async def get_all_users() -> List[Dict[str, Any]]:
    return await db.users.find().to_list(length=None)

async def get_user_count() -> int:
    return await db.users.count_documents({})

# ==================== THUMBNAIL FUNCTIONS ====================

async def set_thumbnail(user_id: int, file_id: str):
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"thumbnail_file_id": file_id}}
    )

async def get_thumbnail(user_id: int) -> Optional[str]:
    user = await db.users.find_one({"user_id": user_id})
    return user.get("thumbnail_file_id") if user else None

async def remove_thumbnail(user_id: int) -> bool:
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"thumbnail_file_id": None}}
    )
    return result.modified_count > 0

# ==================== USAGE TRACKING ====================

async def increment_usage(user_id: int):
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"usage_count": 1}}
    )

async def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    return await db.users.find(
        {"usage_count": {"$gt": 0}}
    ).sort("usage_count", -1).limit(limit).to_list(length=limit)

# ==================== BAN FUNCTIONS ====================

async def ban_user(user_id: int) -> bool:
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"banned": True}}
    )
    return result.modified_count > 0

async def unban_user(user_id: int) -> bool:
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"banned": False}}
    )
    return result.modified_count > 0

async def is_banned(user_id: int) -> bool:
    user = await db.users.find_one({"user_id": user_id})
    return user.get("banned", False) if user else False

# ==================== ADMIN FUNCTIONS ====================

async def add_admin(user_id: int):
    await db.admins.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

async def remove_admin(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return False
    result = await db.admins.delete_one({"user_id": user_id})
    return result.deleted_count > 0

async def is_admin(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    admin = await db.admins.find_one({"user_id": user_id})
    return admin is not None

async def get_all_admins() -> List[int]:
    admins = await db.admins.find().to_list(length=None)
    return [a["user_id"] for a in admins]

# ==================== RENDER URL FUNCTIONS ====================

async def add_url(url: str, name: str = None) -> bool:
    try:
        if not name:
            name = url.replace("https://", "").replace("http://", "").split(".")[0]
        
        await db.urls.update_one(
            {"url": url},
            {
                "$set": {
                    "url": url,
                    "name": name,
                    "active": True,
                    "last_ping": None,
                    "last_status": None,
                    "added_at": datetime.datetime.now()
                }
            },
            upsert=True
        )
        return True
    except Exception:
        return False

async def remove_url(url: str) -> bool:
    result = await db.urls.delete_one({"url": url})
    return result.deleted_count > 0

async def get_all_urls() -> List[Dict[str, Any]]:
    return await db.urls.find().to_list(length=None)

async def update_url_status(url: str, status: int = None, error: str = None):
    update_data = {
        "last_ping": datetime.datetime.now(),
        "last_status": status if status else "Failed"
    }
    if error:
        update_data["last_error"] = error
    
    await db.urls.update_one(
        {"url": url},
        {"$set": update_data}
    )

async def toggle_url(url: str, active: bool):
    await db.urls.update_one(
        {"url": url},
        {"$set": {"active": active}}
    )

async def get_bot_start_time() -> datetime.datetime:
    doc = await db.settings.find_one({"key": "start_time"})
    if doc:
        return doc.get("value")
    return None

async def set_bot_start_time(time: datetime.datetime):
    await db.settings.update_one(
        {"key": "start_time"},
        {"$set": {"value": time}},
        upsert=True
    )