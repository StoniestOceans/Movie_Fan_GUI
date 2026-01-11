import asyncio
import os
from dotenv import load_dotenv

# Load Env
load_dotenv("backend/.env")

from backend.app.vector_agent import VectorEmbeddingAgent
from backend.app.indexer_agent import MongoIndexerAgent

from backend.app.database import db

async def verify_intelligence():
    print("🧠 Verifying Vector Intelligence...")
    
    # 1. Test Embedding
    vec_agent = VectorEmbeddingAgent()
    print(f"   [VectorAgent] Using Key: {'YES' if vec_agent.api_key else 'NO'}")
    
    vec = await vec_agent.generate_embedding("Thanos is the villain.")
    if vec:
        print(f"   ✅ Generated Embedding Vector (dim: {len(vec)})")
    else:
        print("   ❌ Failed to generate vector.")

    # 2. Test Indexer & Persistence
    print("\n🗄️ Verifying Mongo Connection...")
    await db.connect()
    
    if db.client:
        print("   ✅ Connected to Atlas!")
        idx_agent = MongoIndexerAgent()
        try:
            await idx_agent.ensure_performance_indexes()
            print("   ✅ Indexes ensured on remote DB.")
        except Exception as e:
            print(f"   ⚠️ Indexer warning: {e}")
    else:
        print("   ❌ Connection Failed (check .env credentials)")

if __name__ == "__main__":
    asyncio.run(verify_intelligence())
