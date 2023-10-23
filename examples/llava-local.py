import asyncio

from kani import Kani
from kani.ext.vision.engines.llava import LlavaEngine
from kani.ext.vision.parts import ImagePart

engine = LlavaEngine("liuhaotian/llava-v1.5-7b")
ai = Kani(engine)


async def main():
    msg = await ai.chat_round_str(
        ["Please describe this image:", ImagePart.from_path("../docs/_static/kani-vision-logo.png")]
    )
    print(msg)


if __name__ == "__main__":
    asyncio.run(main())
