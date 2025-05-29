from pydantic import BaseModel
from typing import List, Optional
import httpx
from configs import Config
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: bool = False

class ChatResponse(BaseModel):
    choices: List[dict]

class ChatService:
    def __init__(self, config: Config):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.base_url = "https://api.deepseek.com/chat/completions"
        self.api_key = config.apikey

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=(
            retry_if_exception_type(httpx.ReadTimeout) |
            retry_if_exception_type(httpx.NetworkError)
        )
    )
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = await self.client.post(
                self.base_url,
                json=request.dict(),
                headers=headers
            )
            response.raise_for_status()
            return ChatResponse(**response.json())
        except httpx.HTTPStatusError as e:
            print(f"API request failed: {e.response.text}")
            raise ValueError(f"API request failed: {e.response.text}") from e
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise ValueError(f"Unexpected error: {str(e)}") from e

    async def close(self):
        await self.client.aclose()

__all__ = ['Message', 'ChatRequest', 'ChatResponse', 'ChatService']
