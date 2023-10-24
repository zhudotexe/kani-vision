from kani.engines.openai.models import OpenAIChatMessage
from kani.models import BaseModel, ChatMessage
from ...parts import ImagePart


class OpenAIImage(BaseModel):
    image: str
    resize: int = None

    @classmethod
    def from_imagepart(cls, part: ImagePart):
        return cls(image=part.b64)


class OpenAIVisionChatMessage(OpenAIChatMessage):
    """Override for the base OpenAIChatMessage noting that a content part can be an image."""

    content: str | list[OpenAIImage | str] | None

    @classmethod
    def from_chatmessage(cls, m: ChatMessage):
        # leave primitive content as is
        if isinstance(m.content, str) or m.content is None:
            content = m.content
        # translate ImageParts into OpenAIImages
        else:
            content = []
            for part in m.parts:
                if isinstance(part, ImagePart):
                    content.append(OpenAIImage.from_imagepart(part))
                else:
                    content.append(str(part))

        return cls(role=m.role, content=content, name=m.name, function_call=m.function_call)
