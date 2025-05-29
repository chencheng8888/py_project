from pydantic import BaseModel
from typing import Dict
from fastapi import HTTPException
from chat import ChatService, Message, ChatRequest
from typing import Optional

class EvaluateRequest(BaseModel):
    name: str
    gender: str
    grade: str
    grades: Dict[str, float]

class EvaluateController:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    async def evaluate(self, request: EvaluateRequest) -> str:
        try:
            return await self._analyze_grades(request)
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def _analyze_grades(self, request: EvaluateRequest) -> str:
        user_content = f"""
        我叫{request.name}，性别{request.gender}，目前是{request.grade}学生。这是我的期末考试成绩：
        {request.grades}
        请分析我的成绩，给出分析结果，字数在300字左右
        """

        chat_resp = await self.chat_service.chat(ChatRequest(
            model="deepseek-chat",
            messages=[
                Message(
                    role="system",
                    content="你是一个成绩分析助手，可以根据用户提供的成绩和个人信息，给出成绩的分析结果"
                ),
                Message(
                    role="user",
                    content=user_content
                )
            ],
            stream=False
        ))
        
        return chat_resp.choices[0]["message"]["content"]

__all__ = ['EvaluateRequest', 'EvaluateController']
