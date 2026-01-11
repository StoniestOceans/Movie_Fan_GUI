import asyncio
import os
from dotenv import load_dotenv

# Load Env from backend/
load_dotenv("backend/.env")

from backend.app.ingestion.fanart_agent import FanartAgent
from backend.app.nemo_agent import NeMoAgent
from backend.app.ingestion.wikipedia_agent import WikipediaAgent

async def run_checks():
    print("🚦 Starting API Verification...")
    
    # 1. Check Env
    fw_key = os.getenv("FIREWORKS_API_KEY")
    fan_key = os.getenv("FANART_API_KEY")
    print(f"🔑 Keys found: Fireworks={'YES' if fw_key else 'NO'}, Fanart={'YES' if fan_key else 'NO'}")

    # 2. Check NeMo (LLM)
    print("\n🧠 Testing NeMo Agent (LLM)...")
    nemo = NeMoAgent()
    resp = await nemo.generate_response("What is the release date of The Matrix?")
    print(f"   Response: {resp[:100]}...")

    # 3. Check Fanart
    print("\n🎨 Testing Fanart Agent...")
    fanart = FanartAgent()
    # Test Fallback (Avenger)
    res_mock = await fanart.get_movie_assets(movie_name="Avengers: Infinity War")
    url_mock = res_mock.get('assets', {}).get('moviebackground', [{}])[0].get('url', 'None')
    print(f"   [Mock/Real] Avengers Background: {url_mock}")
    
    # 4. Check Wikipedia
    print("\n📚 Testing Wikipedia Agent...")
    wiki = WikipediaAgent()
    res_wiki = await wiki.search_movie("The Matrix")
    print(f"   Wiki Title: {res_wiki.get('title', 'Error')}")

    print("\n✅ Verification Complete.")

if __name__ == "__main__":
    asyncio.run(run_checks())
