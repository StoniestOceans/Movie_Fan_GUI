import sys
import os
import asyncio
# Allow running from root or backend/
sys.path.append(os.getcwd())

from dotenv import load_dotenv

# Load Environment (Force path)
env_path = os.path.join(os.getcwd(), "backend", ".env")
load_dotenv(env_path)

from backend.app.database import db
from backend.app.ingestion.opensubtitles_agent import OpenSubtitlesAgent
from backend.app.srt_parser import SRTManager
from backend.app.vector_agent import VectorEmbeddingAgent
from backend.app.helpers.cleaner import DataCleanerAgent

async def ingest_movie(movie_title: str):
    print(f"🚀 Starting HIGH-VELOCITY Ingestion for: {movie_title}")
    
    # 1. Connect to DB
    await db.connect()
    if not db.client:
        print("❌ DB Connection Failed.")
        return

    # 2. Get Subtitles
    print("📥 Fetching Subtitles...")
    os_agent = OpenSubtitlesAgent()
    srt_content = await os_agent.search_and_download(movie_title)
    
    if not srt_content:
        print("❌ No subtitles found.")
        return

    # 3. Parse Subtitles
    manager = SRTManager()
    manager.load_file(srt_content)
    subs = manager.subs
    print(f"✅ Loaded {len(subs)} subtitle lines.")

    # 4. Prepare Batches
    print("🧠 Processing & Vectorizing (Turbo Mode)...")
    vec_agent = VectorEmbeddingAgent()
    cleaner = DataCleanerAgent()
    
    chunk_size = 10 
    doc_batches = [] # Hold processed docs
    
    semaphore = asyncio.Semaphore(10) # Max 10 concurrent API calls
    
    async def process_batch(batch_subs, batch_idx):
        async with semaphore:
            text_raw = " ".join([s.text.replace("\n", " ") for s in batch_subs])
            text_clean = cleaner.clean_text(text_raw)
            if not text_clean: return None

            start_time = batch_subs[0].start.ordinal / 1000.0
            end_time = batch_subs[-1].end.ordinal / 1000.0

            vector = await vec_agent.generate_embedding(text_clean)
            if vector:
                return {
                    "movie": movie_title,
                    "text": text_clean,
                    "start": start_time,
                    "end": end_time,
                    "embedding": vector
                }
            return None

    tasks = []
    total_chunks = 0
    
    # Create Tasks
    for i in range(0, len(subs), chunk_size):
        batch = subs[i:i+chunk_size]
        if not batch: continue
        tasks.append(process_batch(batch, i // chunk_size))
        total_chunks += 1

    print(f"   ⚡ Launching {total_chunks} concurrent tasks...")
    
    # Run all tasks (gather)
    # Note: For very large movies, we might want to chunk the gather too, 
    # but for ~150 chunks, gather is fine.
    results = await asyncio.gather(*tasks)
    
    # Filter valid results
    valid_docs = [r for r in results if r]

    # 5. Bulk Store in MongoDB
    if valid_docs:
        print(f"💾 Bulk Writing {len(valid_docs)} vectors to MongoDB...")
        collection = db.db["subtitles"]
        
        # Clear old data
        await collection.delete_many({"movie": movie_title})
        
        # Batch Insert
        await collection.insert_many(valid_docs)
        print("✅ Turbo Ingestion Complete!")
    else:
        print("⚠️ No valid chunks created.")

    await db.close()

if __name__ == "__main__":
    asyncio.run(ingest_movie("Avengers: Infinity War"))
