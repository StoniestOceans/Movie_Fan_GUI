# Database Setup & Schema Guide

## Overview
This project uses **MongoDB** (AsyncMotor) for persisting movie metadata, knowledge graph facts, and subtitle content.

**Current Status**: 
- The backend connects to a local instance (`mongodb://localhost:27017`) or `os.getenv("MONGO_URI")`.
- Database Name: `movie_fan_db` (or `os.getenv("DB_NAME")`)

## Collections & Schemas

### 1. `movies`
Stores high-level metadata about a film.
- **Key**: `_id` (custom, e.g., `movie_<hash>`) or `title` (text index).
- **Schema**:
  ```json
  {
    "_id": "movie_12345",
    "title": "The Matrix",
    "name": "The Matrix",
    "metadata": {
      "url": "https://en.wikipedia.org/...",
      "source": "wikipedia",
      "images": ["url1", "url2"],
      "fanart": {
         "moviebackground": [{"url": "..."}],
         "movieposter": [{"url": "..."}]
      }
    }
  }
  ```

### 2. `facts`
Stores granular facts or summaries extracted from ingestion agents.
- **Key**: `_id` (custom, e.g., `fact_<hash>`).
- **Schema**:
  ```json
  {
    "_id": "fact_67890",
    "content": "A summary of the movie...",
    "source": "Wikipedia",
    "related_entities": ["movie_12345"], // FK to movies._id
    "tags": ["summary", "overview"]
  }
  ```

### 3. `subtitles`
Stores raw specific subtitle files.
- **Key**: `query` (the search term used to find it) or `movie_id`.
- **Schema**:
  ```json
  {
    "_id": "...",
    "query": "The Matrix",
    "content": "1\n00:00:20,000 --> ...", // Raw SRT string
    "source": "opensubtitles"
  }
  ```

## Accessing the DB
The database connection logic is in `backend/app/database.py`.
It uses `motor.motor_asyncio` for non-blocking I/O.

## TODOs for DB Team
- [ ] **Atlas Migration**: Set up a cloud instance and provide the `MONGO_URI` env var.
- [ ] **Vector Search**: Enable Atlas Vector Search for the `facts` collection (for RAG).
- [ ] **Indexes**: Review `backend/app/database.py` > `init_indexes()` and optimize.
