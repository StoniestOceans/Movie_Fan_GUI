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
        # Simplified logic: assume it's a search for a movie for now
        # In reality, router would extract entities
        data_payload = await wiki_agent.search_movie(request.query)
        response_text = f"Here is what I found for '{request.query}'. I've saved it to the Knowledge Graph."
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
