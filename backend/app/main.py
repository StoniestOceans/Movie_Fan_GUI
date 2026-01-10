import os
import asyncio
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
        # PARALLEL EXECUTION STRATEGY
        # We launch all agent tasks simultaneously to minimize latency.
        from backend.app.ingestion.opensubtitles_agent import OpenSubtitlesAgent
        os_agent = OpenSubtitlesAgent()
        
        # Create coroutines
        task_wiki = wiki_agent.search_movie(request.query)
        task_subs = os_agent.search_and_download(request.query)
        task_fanart = fanart_agent.get_movie_assets(movie_name=request.query) # Use query initially
        
        # Execute concurrently
        import asyncio # Ensure asyncio is imported
        results = await asyncio.gather(task_wiki, task_subs, task_fanart, return_exceptions=True)
        
        # Unpack results
        wiki_data = results[0] if not isinstance(results[0], Exception) else {}
        srt_content = results[1] if not isinstance(results[1], Exception) else None
        fanart_data = results[2] if not isinstance(results[2], Exception) else {}
        
        # Exception Handling Logging
        if isinstance(results[0], Exception): print(f"Wiki Agent Failed: {results[0]}")
        if isinstance(results[1], Exception): print(f"Subtitle Agent Failed: {results[1]}")
        if isinstance(results[2], Exception): print(f"Fanart Agent Failed: {results[2]}")

        # Logic to merge data
        # If Wikipedia found a better title, we might want to re-query Fanart (optional, but for speed we accept the simultaneous result)
        title = wiki_data.get('title', request.query)

        if srt_content:
            srt_manager.load_file(srt_content)
            response_text = f"Simultaneously fetched data for '{title}' from Wikipedia, Fanart, and OpenSubtitles!"
        else:
            response_text = f"Fetched data for '{title}', but subtitles were not found."

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
    
    # GENERATIVE UI LOGIC:
    # We decide the "Type" of UI to render based on the context.
    
    if "Neo" in text:
        detected_entity = "Neo"
        summary = "Thomas A. Anderson, also known as Neo, is the protagonist."
        context_type = "ingestion" # Standard Card, but we'll try to find an image
        
    elif "Matrix" in text:
        detected_entity = "The Matrix"
        summary = "A simulated reality created by sentient machines to subdue the human population."
        context_type = "ingestion"
        
    elif "blue pill" in text:
        detected_entity = "Blue Pill"
        summary = "Choosing the Blue Pill means returning to the simulated reality of the Matrix."
        context_type = "ingestion"

    elif "red pill" in text:
        detected_entity = "Red Pill"
        summary = "Choosing the Red Pill reveals the truth about the Matrix."
        context_type = "ingestion"
        
    elif "Morpheus" in text:
        # SHOWCASE: MINDMAP GENERATION
        detected_entity = "Morpheus"
        context_type = "mindmap"
        summary = "Captain of the Nebuchadnezzar."

    # Generate Thesys UI for this context
    # We reuse the "ingestion" adapter logic but with context data
    adapter = ThesysMockAdapter()
    
    data_payload = {}
    
    if context_type == "mindmap":
        # Dynamic Knowledge Graph Construction
        data_payload = {
            "center": detected_entity,
            "relations": [
                {"relation": "Captain of", "label": "Nebuchadnezzar"},
                {"relation": "Mentor to", "label": "Neo"},
                {"relation": "Enemy of", "label": "Agents"},
                {"relation": "Believes in", "label": "The One"}
            ]
        }
    else:
        # Standard Card
        # In a real app, we'd query the DB for the Fanart we found earlier
        # Here we mock it for the high-fidelity demo
        image_url = None
        if detected_entity == "Neo":
            image_url = "https://images.fanart.tv/fanart/the-matrix-523ce51b89944.jpg" 
        elif detected_entity == "The Matrix":
            image_url = "https://images.fanart.tv/fanart/the-matrix-5979c6d66e762.jpg"

        data_payload = {
            "title": detected_entity,
            "summary": f"Line: \"{text}\"\n\nContext: {summary}",
            "url": "#timestamp",
            "images": [image_url] if image_url else []
        }
    
    # Use adapter to format it
    ui_schema = adapter.adapt_response(context_type, data_payload)
    
    # SYSTEM LOGS (Observability)
    # Simulate meaningful backend activity logs for the HUD
    system_logs = [
        f"[SYNC] Processing frame @ {request.timestamp_seconds}s",
        f"[SRT] Active Subtitle Index: {sub['index']}",
        f"[NLP] Entity Extraction: '{detected_entity}'",
    ]
    
    if context_type == "mindmap":
        system_logs.append(f"[GEN-UI] Trigger: Narrative Importance")
        system_logs.append(f"[GEN-UI] Rendering Knowledge Graph for {detected_entity}...")
    elif context_type == "ingestion" and detected_entity != "Unknown":
        system_logs.append(f"[DB] Querying Fanart.tv Collection...")
        system_logs.append(f"[GEN-UI] Injecting Asset: {data_payload.get('images', [''])[0] or 'None'}")

    return {
        "subtitle": sub,
        "ui_schema": ui_schema["ui_schema"],
        "logs": system_logs
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
