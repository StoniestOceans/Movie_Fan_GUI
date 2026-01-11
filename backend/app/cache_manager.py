from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from backend.app.database import db

class CacheManager:
    """
    Manages caching of external API responses to MongoDB.
    Uses a separate 'api_cache' collection.
    """
    def __init__(self, collection_name: str = "api_cache"):
        self.collection_name = collection_name

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from cache if it exists and isn't expired (optional expiry logic).
        """
        if db.db is None:
            return None
            
        doc = await db.db[self.collection_name].find_one({"_id": key})
        if doc:
            # We could add TTL logic here if needed
            # if (datetime.utcnow() - doc['timestamp']).days > 7: return None
            return doc.get("data")
        return None

    async def set(self, key: str, data: Dict[str, Any]):
        """
        Save data to cache.
        """
        if db.db is None:
            return

        payload = {
            "data": data,
            "timestamp": datetime.utcnow()
        }
        await db.db[self.collection_name].update_one(
            {"_id": key},
            {"$set": payload},
            upsert=True
        )

# Global instance
cache = CacheManager()
