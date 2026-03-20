import httpx
import asyncio
from typing import Optional, Dict, Any, List

# ============== SYNC CLIENT ==============
class SyncAPIClient:
    """Synchronous HTTP client"""
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
  
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        with httpx.Client(headers=self.headers) as client:
            response = client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
  
    def post(self, endpoint: str, data: Dict) -> Dict:
        with httpx.Client(headers=self.headers) as client:
            response = client.post(f"{self.base_url}/{endpoint}", json=data)
            response.raise_for_status()
            return response.json()

# ============== ASYNC CLIENT (PREFERRED for MCP) ==============
class AsyncAPIClient:
    """Asynchronous HTTP client - MCP Standard"""
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self._client: Optional[httpx.AsyncClient] = None
  
    async def __aenter__(self):
        self._client = httpx.AsyncClient(headers=self.headers)
        return self
  
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()
  
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        response = await self._client.get(
            f"{self.base_url}/{endpoint}", 
            params=params
        )
        response.raise_for_status()
        return response.json()
  
    async def post(self, endpoint: str, data: Dict) -> Dict:
        response = await self._client.post(
            f"{self.base_url}/{endpoint}", 
            json=data
        )
        response.raise_for_status()
        return response.json()
  
    async def stream(self, endpoint: str, data: Dict):
        """Stream response for long-running tasks"""
        async with self._client.stream(
            "POST", 
            f"{self.base_url}/{endpoint}",
            json=data
        ) as response:
            async for line in response.aiter_lines():
                yield line

# ============== LLM API CLIENT (OpenAI Style) ==============
class LLMClient:
    """LLM API Client for AI interactions"""
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.base_url = base_url
        self.api_key = api_key
  
    async def chat_completion(
        self, 
        messages: List[Dict], 
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7
    ) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

# ============== USAGE EXAMPLE ==============
async def demo_api_client():
    print("=" * 50)
    print("API CLIENT DEMO")
    print("=" * 50)
  
    # Example with mock endpoint
    async with AsyncAPIClient("https://jsonplaceholder.typicode.com") as client:
        # GET request
        posts = await client.get("posts", params={"_limit": 2})
        print(f"\n📥 Retrieved {len(posts)} posts")
  
        # POST request
        new_post = await client.post("posts", data={
            "title": "MCP Test",
            "body": "Testing API",
            "userId": 1
        })
        print(f"✅ Created post ID: {new_post.get('id')}")

if __name__ == "__main__":
    asyncio.run(demo_api_client())