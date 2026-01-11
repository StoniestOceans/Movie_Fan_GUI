import os
import fireworks.client
from typing import Dict, Any

class NeMoAgent:
    """
    Wrapper for 'NeMo' conversational AI capabilities, powered by Fireworks.ai for this demo.
    """
    def __init__(self):
        self.api_key = os.getenv("FIREWORKS_API_KEY")
        if self.api_key:
            fireworks.client.api_key = self.api_key
        else:
            print("⚠️ NeMoAgent: No FIREWORKS_API_KEY found. Running in basic Mock mode.")

    async def generate_response(self, user_query: str, context: Dict[str, Any] = None) -> str:
        """
        Generates a conversational response based on user query and context.
        """
        if not self.api_key:
             return f"I understand you are asking about '{user_query}'. (Add FIREWORKS_API_KEY to .env for real AI responses)"

        try:
            # Construct a prompt that encourages "Generative UI" thinking
            system_prompt = (
                "You are an advanced Movie Database Assistant. "
                "You help users explore movies, actors, and trivia. "
                "Keep your answers concise, witty, and engaging."
            )
            
            completion = fireworks.client.ChatCompletion.create(
                model="accounts/fireworks/models/mixtral-8x7b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"❌ NeMo (Fireworks) Error: {e}")
            return "I'm having trouble connecting to my knowledge base right now."

    async def analyze_sentiment(self, text: str) -> str:
        # Simple keywords for now
        positive = ["good", "great", "love", "amazing", "awesome"]
        if any(word in text.lower() for word in positive):
            return "positive"
        return "neutral"

if __name__ == "__main__":
    agent = NeMoAgent()
    import asyncio
    # Simple synchronous test for main
    if agent.api_key:
        try:
             # Fireworks sync client check
             print(str(agent.generate_response("Tell me about Inception"))) # warning: this is async method called syncish if used directly without await in script
        except:
             pass 
    else:
        print("Mock mode test.")
