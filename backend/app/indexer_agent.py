from backend.app.database import db
from pymongo import IndexModel, ASCENDING

class MongoIndexerAgent:
    """
    Agent responsible for maintaining high-performance MongoDB Indexes.
    """
    def __init__(self):
        pass

    async def create_vector_index(self, collection_name: str, field_name: str = "embedding"):
        """
        Creates a Vector Search Index on the specified collection.
        Note: Atlas Vector Search indexes are usually managed via Atlas UI or API,
        but we can simulate standard index creation here or print instructions.
        """
        if db.db is None:
            print("❌ DB not connected.")
            return

        collection = db.db[collection_name]
        
        # Standard Index for filtering
        await collection.create_index([("title", ASCENDING)])
        print(f"✅ Created standard index on {collection_name}.title")

        # For Atlas Vector Search, we typically define an index definition.
        # Since we can't easily push Atlas Search config via standard driver commands without
        # using the 'runCommand' with specific privileges, we will log the definition.
        
        index_def = {
            "name": "vector_index",
            "type": "vectorSearch",
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": field_name,
                        "numDimensions": 768,
                        "similarity": "cosine"
                    }
                ]
            }
        }
        print(f"ℹ️ [Atlas Requirement] Please create a SEARCH INDEX on '{collection_name}' with definition:")
        print(str(index_def))

    async def ensure_performance_indexes(self):
        """
        Creates compound indexes for speed.
        """
        if db.db is None: return

        # Movies: Search by Title + Year
        await db.db.movies.create_index([("title", ASCENDING), ("release_date", ASCENDING)])
        
        # Subtitles: Search by Movie + Language
        await db.db.subtitles.create_index([("movie_id", ASCENDING), ("language", ASCENDING)])
        
        print("🚀 Performance Indexes Ensured.")

if __name__ == "__main__":
    import asyncio
    agent = MongoIndexerAgent()
    # Mock DB connect if needed for test
    asyncio.run(agent.ensure_performance_indexes())
