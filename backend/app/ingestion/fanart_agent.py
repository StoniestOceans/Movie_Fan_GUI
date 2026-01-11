import os
import requests
from typing import Dict, Any
from backend.app.database import db

class FanartAgent:
    def __init__(self):
        self.api_key = os.getenv("FANART_API_KEY")
        self.base_url = "http://webservice.fanart.tv/v3/movies"

    async def get_movie_assets(self, tmdb_id: str = None, movie_name: str = None) -> Dict[str, Any]:
        """
        Fetches images/assets from Fanart.tv and updates the Movie in DB.
        If no TMDB ID is provided, it returns a mock response for now or error.
        """
        # For prototype without real TMDB ID, we rely on name matching if id missing
        # DEMO: Manual mapping for high-fidelity demo
        if not tmdb_id and movie_name:
            lower_name = movie_name.lower()
            if "infinity war" in lower_name: tmdb_id = "299536"
            elif "matrix" in lower_name: tmdb_id = "603"
            
        if not tmdb_id and not movie_name:
             return {"error": "Need tmdb_id or movie_name"}

        # 1. Check Cache
        from backend.app.cache_manager import cache
        cache_key = f"fanart_assets_{tmdb_id or movie_name}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            print(f"⚡ Cache Hit for Fanart: {movie_name}")
            return cached_data

        assets = {}
        
        # Real API call if Key and ID exist
        if self.api_key:
            if not tmdb_id and movie_name:
                 # Attempt simpler search or manual ID mapping if possible.
                 # For this demo, if we lack ID, we'll log it and fallback.
                 print(f"⚠️ FanartAgent: Have key but missing TMDB ID for '{movie_name}'.")
                 # In a full impl, we would hit TMDb search API here to get the ID.
                 
            if tmdb_id:
                try:
                    print(f"🎨 FanartAgent: Fetching assets for TMDB ID {tmdb_id}...")
                    url = f"{self.base_url}/{tmdb_id}?api_key={self.api_key}"
                    response = requests.get(url)
                    if response.status_code == 200:
                        assets = response.json()
                        print(f"✅ FanartAgent: Success! Found {len(assets)} categories.")
                    else:
                        print(f"❌ FanartAgent: API Error {response.status_code}")
                except Exception as e:
                     print(f"Fanart API failed: {e}")
        else:
             print("⚠️ FanartAgent: No API Key found. Using Mock Fallback.")
        
        # fallback mock assets if no API key or fetch failed
        if not assets:
            print(f"🎨 FanartAgent: Using fallback assets for '{movie_name}'")
            # Provide better context-aware fallbacks if possible
            if movie_name and "matrix" in movie_name.lower():
                assets = {"moviebackground": [{"url": "https://images.fanart.tv/fanart/the-matrix-523ce51b89944.jpg"}]}
            elif movie_name and "avengers" in movie_name.lower():
                assets = {"moviebackground": [{"url": "https://images.fanart.tv/fanart/avengers-infinity-war-5ac5e1657803e.jpg"}]}
            else:
                 assets = {"moviebackground": [{"url": "https://dummyimage.com/1920x1080/000/fff&text=No+Fanart"}]}
            
        # Persist (Update Movie)
        if db.db is not None and movie_name:
            # We assume the movie exists or we upsert it with minimal info
            await db.db.movies.update_one(
                {"name": movie_name},
                {"$set": {"metadata.fanart": assets}},
                upsert=True
            )
            val = {"status": "updated", "assets": assets, "movie": movie_name}
            await cache.set(cache_key, val)
            return val

        val = {"status": "fetched", "assets": assets}
        await cache.set(cache_key, val)
        return val

if __name__ == "__main__":
    # Example usage (requires API key)
    agent = FanartAgent()
    print(agent.get_movie_assets("12345"))
