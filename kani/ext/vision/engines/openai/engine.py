from kani import AIFunction, ChatMessage
from kani.engines.openai import OpenAIEngine
from kani.engines.openai.models import ChatCompletion, FunctionSpec
from .img_tokens import tokens_from_image_size
from .models import OpenAIVisionChatMessage
from ...parts import ImagePart


class OpenAIVisionEngine(OpenAIEngine):
    """Engine for using vision models on the OpenAI API.

    This engine supports all vision-language models, chat-based models, and fine-tunes. It is a superset of the base
    :class:`~kani.engines.openai.OpenAIEngine`.
    """

    def __init__(self, api_key: str = None, model="gpt-4-visual", *args, **kwargs):
        super().__init__(api_key, model, *args, **kwargs)
        # GPT-4V always includes a 54-token system prompt
        if model.endswith("visual"):
            self.token_reserve = 54

    def message_len(self, message: ChatMessage) -> int:
        mlen = 7
        for part in message.parts:
            if isinstance(part, ImagePart):
                mlen += tokens_from_image_size(part.image.size)
            else:
                mlen += len(self.tokenizer.encode(str(part)))
        if message.name:
            mlen += len(self.tokenizer.encode(message.name))
        if message.function_call:
            mlen += len(self.tokenizer.encode(message.function_call.name))
            mlen += len(self.tokenizer.encode(message.function_call.arguments))
        return mlen

    async def predict(
        self, messages: list[ChatMessage], functions: list[AIFunction] | None = None, **hyperparams
    ) -> ChatCompletion:
        if functions:
            function_spec = [FunctionSpec(name=f.name, description=f.desc, parameters=f.json_schema) for f in functions]
        else:
            function_spec = None
        translated_messages = [OpenAIVisionChatMessage.from_chatmessage(m) for m in messages]
        completion = await self.client.create_chat_completion(
            model=self.model, messages=translated_messages, functions=function_spec, **self.hyperparams, **hyperparams
        )
        return completion
