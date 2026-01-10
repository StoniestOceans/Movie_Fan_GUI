import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

from backend.app.database import db
from backend.app.agent_router import AgentRouter
from backend.app.ingestion.wikipedia_agent import WikipediaAgent
from backend.app.ingestion.fanart_agent import FanartAgent
from backend.app.commerce.x402_agent import X402Agent
from backend.app.nemo_agent import NeMoAgent
from backend.app.thesys_adapter import ThesysMockAdapter

# API Models
class ChatRequest(BaseModel):
    query: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    data: dict = {}
    agent_used: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.close()

app = FastAPI(title="Movie Fan Generative UI API", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agents
router = AgentRouter()
wiki_agent = WikipediaAgent()
fanart_agent = FanartAgent()
x402 = X402Agent()
nemo = NeMoAgent()

from backend.app.srt_parser import SRTManager
srt_manager = SRTManager()
# Load sample file immediately for demo
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
# Assumes matrix.srt is in parent of app/ i.e. backend/matrix.srt
srt_path = os.path.join(base_dir, "..", "matrix.srt")
srt_manager.load_from_path(srt_path)

@app.get("/")
def read_root():
    return {"message": "Welcome to Movie Fan Dashboard API"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main entry point for the Generative UI Chat.
    """
    intent = await router.route_query(request.query)
    response_text = ""
    data_payload = {}

    if intent == "ingestion":
        # 1. Search Wikipedia (Metadata & Persistence)
        wiki_data = await wiki_agent.search_movie(request.query)
        
        # 2. Search OpenSubtitles (SRT Content)
        # Import here to avoid circulars if any, but better at top. 
        # For now we assume imports are clean.
        from backend.app.ingestion.opensubtitles_agent import OpenSubtitlesAgent
        # We instantiate here or globally. Globally is better but for rapid proto:
        os_agent = OpenSubtitlesAgent()
        srt_content = await os_agent.search_and_download(request.query)
        
        # 3. Fanart Integration (Assets & Persistence)
        # We rely on the movie name found by Wikipedia, or the original query
        movie_name_for_fanart = wiki_data.get('title', request.query)
        fanart_data = await fanart_agent.get_movie_assets(movie_name=movie_name_for_fanart)

        if srt_content:
            # Load into the global SRT Manager
            srt_manager.load_file(srt_content)
            response_text = f"Found '{movie_name_for_fanart}' on Wikipedia, fetched Fanart, and loaded subtitles!"
        else:
            response_text = f"Found '{movie_name_for_fanart}' on Wikipedia and Fanart, but no subtitles found."

        data_payload = {**wiki_data, "fanart": fanart_data.get('assets', {})}
        
    elif intent == "commerce":
        # Mock buying flow
        data_payload = x402.buy_gift_card(25.0, "user@example.com")
        response_text = "I can help you with that gift card transaction."

    elif intent == "reasoning":
        # NeMo conversation
        response_text = await nemo.generate_response(request.query)
        data_payload = {"context": "knowledge_graph_lookup"}

    else:
        response_text = "I'm not sure how to handle that yet."

    # Adapt for Thesys Generative UI
    thesys_adapter = ThesysMockAdapter()
    ui_schema = thesys_adapter.adapt_response(intent, data_payload)

    return ChatResponse(
        response=response_text,
        data={**data_payload, **ui_schema}, # Merge UI schema into data
        agent_used=intent
    )

class SyncRequest(BaseModel):
    timestamp_seconds: float

@app.post("/api/sync")
async def sync_endpoint(request: SyncRequest):
    """
    Returns the context UI for a specific timestamp (seconds).
    """
    sub = srt_manager.get_subtitle_at_time(request.timestamp_seconds)
    
    if not sub:
        return {"ui_schema": [], "subtitle": None}
        
    # LOGIC: Extract keywords from subtitle to simulate "Context"
    text = sub["text"]
    
    # Naive entity extraction for demo
    detected_entity = "Unknown"
    summary = "Context loading..."
    
    if "Neo" in text:
        detected_entity = "Neo"
        summary = "Thomas A. Anderson, also known as Neo, is the protagonist."
        
    elif "Matrix" in text:
        detected_entity = "The Matrix"
        summary = "A simulated reality created by sentient machines to subdue the human population."
        
    elif "blue pill" in text:
        detected_entity = "Blue Pill"
        summary = "Choosing the Blue Pill means returning to the simulated reality of the Matrix."

    elif "red pill" in text:
        detected_entity = "Red Pill"
        summary = "Choosing the Red Pill reveals the truth about the Matrix."
        
    elif "Morpheus" in text:
        detected_entity = "Morpheus"
        summary = "Captain of the Nebuchadnezzar, he frees Neo from the Matrix."

    # Generate Thesys UI for this context
    # We reuse the "ingestion" adapter logic but with context data
    adapter = ThesysMockAdapter()
    
    # Create a "Context Card"
    # We map 'title' -> Entity, 'summary' -> Description
    data_payload = {
        "title": detected_entity,
        "summary": f"Line: \"{text}\"\n\nContext: {summary}",
        "url": "#timestamp"
    }
    
    # Use adapter to format it
    ui_schema = adapter.adapt_response("ingestion", data_payload)
    
    return {
        "subtitle": sub,
        "ui_schema": ui_schema["ui_schema"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
