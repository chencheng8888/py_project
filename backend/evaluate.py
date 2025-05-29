from typing import Dict
from chat import ChatService, Message, ChatRequest

class EvaluateController:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    def evaluate(self, request: dict) -> str:
        try:
            return self._analyze_grades(request)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Unexpected error: {str(e)}")

    def _analyze_grades(self, request: dict) -> str:
        user_content = f"""
        我叫{request['name']}，性别{request['gender']}，目前是{request['grade']}学生。这是我的期末考试成绩：
        {request['grades']}
        请分析我的成绩，给出分析结果，字数在300字左右
        """

        chat_resp = self.chat_service.chat(ChatRequest(
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

__all__ = ['EvaluateController']
