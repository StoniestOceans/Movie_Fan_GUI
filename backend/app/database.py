import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, TEXT

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "movie_fan_db")

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Trigger a connection check
            await self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            print(f"Connected to MongoDB: {DB_NAME}")
            await self.init_indexes()
        except Exception as e:
            print(f"WARNING: Could not connect to MongoDB. Running in 'No-Persistence' mode. Error: {e}")
            self.client = None
            self.db = None

    async def close(self):
        if self.client:
            self.client.close()

    async def init_indexes(self):
        # Create indexes for efficient querying
        await self.db.movies.create_indexes([
            IndexModel([("title", TEXT)], name="title_text_index"),
            IndexModel([("release_date", ASCENDING)], name="release_date_index")
        ])
        await self.db.people.create_indexes([
            IndexModel([("name", TEXT)], name="name_text_index")
        ])
        await self.db.facts.create_indexes([
            IndexModel([("related_entities", ASCENDING)], name="related_entities_index"),
            IndexModel([("content", TEXT)], name="content_text_index")
        ])

db = Database()
