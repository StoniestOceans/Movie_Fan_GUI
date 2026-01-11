import os
import fireworks.client
from typing import List, Optional

class VectorEmbeddingAgent:
    """
    Agent responsible for generating vector embeddings for text using Fireworks AI.
    """
    def __init__(self):
        self.api_key = os.getenv("FIREWORKS_API_KEY")
        if self.api_key:
            fireworks.client.api_key = self.api_key
        else:
            print("⚠️ VectorAgent: No FIREWORKS_API_KEY found.")

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generates a vector embedding for the given text using REST API.
        """
        if not self.api_key:
            print("⚠️ VectorAgent: Using Mock Embedding")
            return [0.1] * 768

        try:
             # Direct REST API call to avoid client version issues
            import requests
            url = "https://api.fireworks.ai/inference/v1/embeddings"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "nomic-ai/nomic-embed-text-v1.5",
                "input": text
            }
            
            # Since this is sync inside async, ideally await loop.run_in_executor
            # For simplicity in this demo:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data["data"][0]["embedding"]
            else:
                print(f"❌ Vector API Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Vector Generation Failed: {e}")
            return None

if __name__ == "__main__":
    agent = VectorEmbeddingAgent()
    import asyncio
    # Test
    vec = asyncio.run(agent.generate_embedding("Iron Man is a superhero."))
    if vec:
        print(f"Generated Vector Dim: {len(vec)}")
