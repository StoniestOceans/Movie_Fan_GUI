from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class Entity(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    metadata: dict = Field(default_factory=dict)

class Movie(Entity):
    title: str
    release_date: Optional[datetime] = None
    genres: List[str] = []
    directors: List[str] = []  # List of Person IDs
    cast: List[str] = []      # List of Person IDs
    external_ids: dict = Field(default_factory=dict) # e.g., {'imdb': 'tt123', 'tmdb': '456'}

class Person(Entity):
    biography: Optional[str] = None
    filmography: List[str] = [] # List of Movie IDs

class Fact(BaseModel):
    id: str = Field(..., alias="_id")
    content: str
    source: str # e.g., "Wikipedia", "Fanart.tv"
    confidence_score: float = 1.0
    related_entities: List[str] = [] # Entity IDs
    tags: List[str] = []

class Relationship(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relationship_type: str # e.g., "DIRECTED", "ACTED_IN", "MARRIED_TO"
    description: Optional[str] = None
    weight: float = 1.0
