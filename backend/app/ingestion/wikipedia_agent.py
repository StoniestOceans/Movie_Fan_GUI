import wikipedia
import uuid
from typing import Dict, Any
from datetime import datetime
from backend.app.database import db
from backend.app.models import Movie, Fact

class WikipediaAgent:
    def __init__(self, lang: str = "en"):
        wikipedia.set_lang(lang)

    async def search_movie(self, query: str) -> Dict[str, Any]:
        """
        Searches Wikipedia, returns metadata, and PERSISTS it to the DB.
        """
        try:
            # Basic search (synchronous call)
            results = wikipedia.search(query)
            if not results:
                return {"error": "No results found"}
            
            # Fetch generic page
            page = wikipedia.page(results[0], auto_suggest=False)
            
            # Create Movie Entity
            # Generate a consistent ID based on title or use UUID
            movie_id = f"movie_{uuid.uuid4().hex[:8]}"
            
            movie = Movie(
                _id=movie_id,
                name=page.title,
                title=page.title,
                metadata={
                    "url": page.url,
                    "source": "wikipedia",
                    "images": page.images
                }
            )
            
            # Create Fact Entity (Summary)
            fact_id = f"fact_{uuid.uuid4().hex[:8]}"
            summary_fact = Fact(
                _id=fact_id,
                content=page.summary,
                source="Wikipedia",
                related_entities=[movie_id],
                tags=["summary", "overview"]
            )
            
            # Persist to MongoDB
            if db.db is not None:
                await db.db.movies.update_one(
                    {"name": movie.name}, 
                    {"$set": movie.model_dump(by_alias=True)}, 
                    upsert=True
                )
                await db.db.facts.update_one(
                    {"_id": fact_id},
                    {"$set": summary_fact.model_dump(by_alias=True)},
                    upsert=True
                )
            
            return {
                "title": page.title,
                "summary": page.summary,
                "url": page.url,
                "saved_to_db": True,
                "movie_id": movie_id
            }
            
        except wikipedia.exceptions.DisambiguationError as e:
            return {"error": "Disambiguation", "options": e.options}
        except wikipedia.exceptions.PageError:
            return {"error": "Page format not supported or found"}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Test stub
    import asyncio
    agent = WikipediaAgent()
    # Note: db connection won't work in this stub unless we call db.connect()
    print("Agent initialized. Run via main API to test persistence.")
