import asyncio

from kani import Kani
from kani.ext.vision import ImagePart
from kani.ext.vision.engines.llava import LlavaEngine

# Load the engine
engine = LlavaEngine("liuhaotian/llava-v1.5-7b")

# You can also load the 4-bit quantized version by uncommenting the following lines:
# import torch
# from transformers import BitsAndBytesConfig
#
# engine = LlavaEngine(
#     "liuhaotian/llava-v1.5-7b",
#     model_load_kwargs={
#         "device_map": "auto",
#         "load_in_4bit": True,
#         "low_cpu_mem_usage": True,
#         "quantization_config": BitsAndBytesConfig(
#             load_in_4bit=True,
#             bnb_4bit_compute_dtype=torch.float16,
#             bnb_4bit_use_double_quant=True,
#             bnb_4bit_quant_type="nf4",
#         ),
#     },
# )

# Nothing special here - use the normal Kani object
ai = Kani(engine)


async def main():
    msg = await ai.chat_round_str([
        "Please describe this image:", ImagePart.from_path("../docs/_static/kani-vision-logo.png")
    ])
    print(msg)


if __name__ == "__main__":
    asyncio.run(main())
