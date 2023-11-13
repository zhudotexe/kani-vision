from typing import Annotated, Literal, Union

from pydantic import Field

from kani.engines.openai.models import OpenAIChatMessage
from kani.models import BaseModel, ChatMessage, ChatRole
from ...parts import ImagePart, RemoteURLImagePart


# note: `type` does not have default since we use `.model_dump(..., exclude_defaults=True)`
class OpenAIText(BaseModel):
    type: Literal["text"]
    text: str

    @classmethod
    def from_text(cls, data: str):
        return cls(type="text", text=data)


class OpenAIImage(BaseModel):
    type: Literal["image_url"]
    image_url: str
    detail: Literal["high"] | Literal["low"] | None = None

    @classmethod
    def from_imagepart(cls, part: ImagePart):
        if isinstance(part, RemoteURLImagePart):
            return cls(type="image_url", image_url=part.url)
        return cls(type="image_url", image_url=part.b64_uri)


OpenAIPart = Annotated[Union[OpenAIText, OpenAIImage], Field(discriminator="type")]


class OpenAIVisionChatMessage(OpenAIChatMessage):
    """Override for the base OpenAIChatMessage noting that a content part can be an image."""

    content: list[OpenAIPart] | str | None

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
                    content.append(OpenAIText.from_text(str(part)))

        # translate tool responses to a function to the right openai format
        if m.role == ChatRole.FUNCTION:
            if m.tool_call_id is not None:
                return cls(role="tool", content=content, name=m.name, tool_call_id=m.tool_call_id)
            return cls(role=m.role.value, content=content, name=m.name)
        return cls(
            role=m.role.value, content=content, name=m.name, tool_call_id=m.tool_call_id, tool_calls=m.tool_calls
        )
