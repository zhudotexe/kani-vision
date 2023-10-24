"""
To determine how many tokens a given image will use when passed to GPT-4V, let's do a naive binary search for the
resolutions of an image which change the number of tokens in the prompt.
"""
import asyncio
import os
import sys

from PIL import Image

from kani import ChatRole
from kani.engines.openai import OpenAIClient
from kani.ext.vision import ImagePart
from kani.ext.vision.engines.openai.models import OpenAIImage, OpenAIVisionChatMessage

sys.path.append("..")

client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))


async def main():
    size = (1080, 1920)
    img = Image.new("RGB", size)
    resp = await client.create_chat_completion(
        model="gpt-4-visual",
        messages=[
            OpenAIVisionChatMessage(
                role=ChatRole.USER,
                content=[
                    OpenAIImage.from_imagepart(ImagePart.from_image(img)),
                ],
            )
        ],
        max_tokens=1,
    )
    print(f"{size}: {resp.prompt_tokens - 61} tokens")
    print(resp)
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
