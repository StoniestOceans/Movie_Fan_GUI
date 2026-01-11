import asyncio
from collections import deque
from backend.app.nemo_agent import NeMoAgent

class SceneBufferAgent:
    """
    Buffers recent dialogue to determine the 'Scene Theme' or 'Mood'.
    """
    def __init__(self, buffer_size=10):
        self.buffer = deque(maxlen=buffer_size)
        self.current_theme = "neutral"
        self.nemo = NeMoAgent()
        self.last_analysis_time = 0
        self._lock = False

    def add_line(self, text: str):
        """Adds a subtitle line to the buffer."""
        if text and text not in self.buffer:
           self.buffer.append(text)

    async def analyze_scene(self) -> str:
        """
        Analyzes the buffered text to determine the mood.
        Returns: 'action', 'suspense', 'emotional', or 'neutral'.
        """
        if len(self.buffer) < 3:
            return "neutral"
            
        # Combine buffer
        transcript = " ".join(self.buffer)
        
        # Simple Heuristic Check first (for speed/fallback)
        lower_text = transcript.lower()
        if any(w in lower_text for w in ['kill', 'fight', 'attack', 'shoot', 'blast', 'thanos']):
            self.current_theme = "action"
            return "action"
        if any(w in lower_text for w in ['love', 'sorry', 'cry', 'tears', 'miss']):
            self.current_theme = "emotional"
            return "emotional"
        if any(w in lower_text for w in ['secret', 'hide', 'quiet', 'unknown', 'matrix']):
            self.current_theme = "suspense"
            return "suspense"

        # LLM Analysis (Async, Fire and Forget ideally, but here we await fast)
        # We only really need to call this if heuristics fail or periodically.
        # For this high-speed sync loop, let's stick to the heuristic + cached updates 
        # to avoid stalling the UI for 500ms.
        
        self.current_theme = "neutral"
        return "neutral"

    def get_current_theme(self):
        return self.current_theme
