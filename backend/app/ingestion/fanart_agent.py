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
        if not tmdb_id and not movie_name:
             return {"error": "Need tmdb_id or movie_name"}

        assets = {}
        
        # Real API call if Key and ID exist
        if self.api_key and tmdb_id:
            try:
                url = f"{self.base_url}/{tmdb_id}?api_key={self.api_key}"
                # requests is blocking, in prod use httpx. For now wrapping or leaving as is.
                response = requests.get(url)
                if response.status_code == 200:
                    assets = response.json()
            except Exception as e:
                print(f"Fanart API failed: {e}")
        
        # fallback mock assets if no API key
        if not assets:
            assets = {"moviebackground": [{"url": "http://example.com/poster.jpg"}]}
            
        # Persist (Update Movie)
        if db.db is not None and movie_name:
            # We assume the movie exists or we upsert it with minimal info
            await db.db.movies.update_one(
                {"name": movie_name},
                {"$set": {"metadata.fanart": assets}},
                upsert=True
            )
            return {"status": "updated", "assets": assets, "movie": movie_name}

        return {"status": "fetched", "assets": assets}

if __name__ == "__main__":
    # Example usage (requires API key)
    agent = FanartAgent()
    print(agent.get_movie_assets("12345"))
