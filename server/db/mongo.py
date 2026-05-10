import os
from core.config import MONGO_URI, MONGO_DB

USE_MONGO = os.getenv("USE_MONGO", "auto")


def _try_mongo():
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        return client, client[MONGO_DB]
    except Exception:
        return None, None


_mongo_client, _mongo_db = _try_mongo() if USE_MONGO != "false" else (None, None)
_using_mongo = _mongo_db is not None


def get_collection(name: str):
    if _using_mongo:
        return _mongo_db[name]
    from db.json_store import get_collection as json_get_collection
    return json_get_collection(name)
