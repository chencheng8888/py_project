from typing import Dict
from chat import ChatService, Message, ChatRequest

class SuggestController:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    def suggest(self, request: dict) -> str:
        try:
            return self._generate_suggestions(request)
        except Exception as e:
            raise RuntimeError(str(e))

    def _generate_suggestions(self, request: dict) -> str:
        user_content = f"""
        我叫{request['name']}，性别{request['gender']}，目前是{request['grade']}学生。这是我的期末考试成绩：
        {request['grades']}
        请分析我的成绩,给出学习建议,字数在300字左右
        """

        chat_resp = self.chat_service.chat(ChatRequest(
            model="deepseek-chat",
            messages=[
                Message(
                    role="system",
                    content="你是一个学习建议助手，可以根据学生信息和成绩评价，给出具体的学习建议"
                ),
                Message(
                    role="user",
                    content=user_content
                )
            ],
            stream=False
        ))
        
        return chat_resp.choices[0]["message"]["content"]

__all__ = ['SuggestController']
