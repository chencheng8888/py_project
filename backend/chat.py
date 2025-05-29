from typing import List, Dict, Any
import httpx
from config import Config
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

class ChatRequest:
    def __init__(self, model: str, messages: List[Message], stream: bool = False):
        self.model = model
        self.messages = messages
        self.stream = stream

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "messages": [msg.to_dict() for msg in self.messages],
            "stream": self.stream
        }

class ChatResponse:
    def __init__(self, choices: List[Dict[str, Any]], **kwargs):
        self.choices = choices
        # 忽略其他未定义的字段

class ChatService:
    def __init__(self, config: Config):
        self.client = httpx.Client(timeout=30.0)
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
    def chat(self, request: ChatRequest) -> ChatResponse:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = self.client.post(
                self.base_url,
                json=request.to_dict(),
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

    def close(self):
        self.client.close()

__all__ = ['Message', 'ChatRequest', 'ChatResponse', 'ChatService']
