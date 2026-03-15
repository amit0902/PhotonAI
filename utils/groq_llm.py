from typing import List
from groq import Groq

from pydantic import PrivateAttr
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from utils.groq_message_adapter import map_langchain_role_to_groq


class GroqChatLLM(BaseChatModel):
    """
    LangChain-compatible Groq LLM wrapper
    """

    model_name: str = "llama-3.1-8b-instant"

    _client: Groq = PrivateAttr()

    def __init__(self, api_key: str, model_name: str | None = None):
        super().__init__()
        self._client = Groq(api_key=api_key)

        if model_name:
            self.model_name = model_name

    @property
    def _llm_type(self) -> str:
        return "groq-chat"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop=None,
        run_manager=None,
        **kwargs
    ) -> ChatResult:

        groq_messages = [
            {
                "role": map_langchain_role_to_groq(m.type),
                "content": m.content
            }
            for m in messages
        ]

        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=groq_messages
        )

        generation = ChatGeneration(
            message=AIMessage(
                content=response.choices[0].message.content
            )
        )

        return ChatResult(generations=[generation])