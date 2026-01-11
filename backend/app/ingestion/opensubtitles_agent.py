import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from backend.app.database import db

# Minimal OpenSubtitles API Client
# API Documentation: https://opensubtitles.com/docs/api/html/index.htm

class OpenSubtitlesAgent:
    BASE_URL = "https://api.opensubtitles.com/api/v1"
    
    def __init__(self):
        self.api_key = os.getenv("OPENSUBTITLES_API_KEY")
        self.headers = {
            "Api-Key": self.api_key or "",
            "Content-Type": "application/json",
            "User-Agent": "MovieFanDashboard v1.0" # Required by their API
        }

    async def search_and_download(self, query: str) -> Optional[str]:
        """
        Searches for subtitles for the movie query and returns the SRT content string.
        """
        print(f"🎬 OpenSubtitlesAgent: Searching for '{query}'...")
        
        # 1. Check if we have an API key
        if not self.api_key:
            print("⚠️ OpenSubtitlesAgent: No API Key found. Using Mock Mode.")
            if "matrix" in query.lower():
                print(f"[{self.agent_name}] Using MOCK SRT for 'The Matrix'")
                return await self._mock_search("matrix")
                
            if "avengers" in query.lower() or "infinity" in query.lower():
                print(f"[{self.agent_name}] Using MOCK SRT for 'Avengers: Infinity War'")
                return await self._mock_search("avengers")
            return None

        # 2. Real API Search (If Key Present)
        try:
            async with aiohttp.ClientSession() as session:
                # Step A: Search for the movie/subtitle
                params = {"query": query, "languages": "en"}
                async with session.get(f"{self.BASE_URL}/subtitles", headers=self.headers, params=params) as resp:
                    if resp.status != 200:
                        print(f"❌ OpenSubtitles API Error: {resp.status} - {await resp.text()}")
                        return await self._mock_search(query)
                    
                    data = await resp.json()
                    if not data.get("data"):
                        print("❌ OpenSubtitles: No results found.")
                        return None
                        
                    # Get the first best match
                    first_match = data["data"][0]
                    file_id = first_match["attributes"]["files"][0]["file_id"]
                    print(f"✅ Found subtitle for '{query}' (ID: {file_id})")

                # Step B: Download Request (to get link)
                download_payload = {"file_id": file_id}
                async with session.post(f"{self.BASE_URL}/download", headers=self.headers, json=download_payload) as resp:
                    if resp.status != 200:
                        print(f"❌ Download Link Error: {resp.status}")
                        return None
                    
                    link_data = await resp.json()
                    download_url = link_data.get("link")
                
                # Step C: Fetch raw content
                if download_url:
                    async with session.get(download_url) as resp:
                        if resp.status == 200:
                            content = await resp.text()
                            # Persist to DB if possible
                            if db.db is not None:
                                await db.db.subtitles.update_one(
                                    {"query": query},
                                    {"$set": {"content": content, "source": "opensubtitles"}},
                                    upsert=True
                                )
                            return content
                            
        except Exception as e:
            print(f"❌ OpenSubtitles Exception: {e}")
            
        return await self._mock_search(query)

    async def _mock_search(self, query: str) -> Optional[str]:
        """
        Fallback mock that returns local matrix.srt or hardcoded avengers data
        """
        if "avengers" in query.lower():
            return """1
00:00:10,000 --> 00:00:13,000
Thor: BRING ME THANOS!

2
00:00:13,500 --> 00:00:17,000
[Thunder crashes as Stormbreaker flies]

3
00:00:17,500 --> 00:00:22,000
Thanos: You should have gone for the head.

4
00:00:22,500 --> 00:00:25,000
[Thanos snaps his fingers]

5
00:00:25,500 --> 00:00:28,000
Thor: No!
"""

        if "matrix" in query.lower():
            print("🤖 Mock: Loading local matrix.srt")
            # Try to find the file we used before
            # Assuming running from root/backend context
            possible_paths = [
                "matrix.srt",
                "backend/matrix.srt",
                "../matrix.srt"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        return f.read()
            print("❌ Mock: Local matrix.srt not found.")
        
        return None
