from llava.mm_utils import process_images, tokenizer_image_token

from kani import AIFunction, ChatMessage, ChatRole
from kani.engines import llama2_prompt
from kani.engines.base import Completion
from kani.engines.huggingface import HuggingEngine
from kani.exceptions import MissingModelDependencies
from ...parts import ImagePart

try:
    import sentencepiece
    import torch
    from llava.constants import (
        DEFAULT_IM_END_TOKEN,
        DEFAULT_IM_START_TOKEN,
        DEFAULT_IMAGE_PATCH_TOKEN,
        DEFAULT_IMAGE_TOKEN,
        IMAGE_TOKEN_INDEX,
    )
    from torch import tensor
except ImportError:
    raise MissingModelDependencies(
        "The LlavaEngine requires extra dependencies. Please see the kani-vision installation documentation for"
        " instructions on how to install the LLaVA dependencies"
        " (https://github.com/zhudotexe/kani-vision#installation)."
    ) from None


class LlavaEngine(HuggingEngine):
    """Implementation of LLaVA v1.5 using Hugging Face transformers.

    You may also use the 13b or other LLaVA models that use the LLaVA prompt and image encoding by passing the
    HuggingFace model ID to the initializer.

    Model IDs:

    - ``liuhaotian/llava-v1.5-7b``
    - ``liuhaotian/llava-v1.5-13b``

    **GPU Support**

    By default, the HuggingEngine loads the model on GPU if CUDA is detected on your system. To override the device
    the model is loaded on, pass ``device="cpu|cuda"`` to the constructor.

    .. seealso:: https://github.com/haotian-liu/LLaVA/tree/main

    .. code-block:: python

        engine = LlavaEngine("liuhaotian/llava-v1.5-7b")
        ai = Kani(engine)
        msg = await ai.chat_round_str(["Please describe this image:", ImagePart.from_path("path/to/image.png")])
    """

    token_reserve = 7

    def __init__(
        self,
        model_id: str = "liuhaotian/llava-v1.5-7b",
        *args,
        tokenizer_kwargs: dict = None,
        model_load_kwargs: dict = None,
        **kwargs,
    ):
        """
        :param model_id: The ID of the model to load from HuggingFace.
        :param max_context_size: The context size of the model.
        :param device: The hardware device to use. If not specified, uses CUDA if available; otherwise uses CPU.
        :param tokenizer_kwargs: Additional arguments to pass to ``AutoTokenizer.from_pretrained()``.
        :param model_load_kwargs: Additional arguments to pass to ``AutoModelForCausalLM.from_pretrained()``.
        :param hyperparams: Additional arguments to supply the model during generation.
        """
        kwargs.setdefault("max_context_size", 2048)
        # model kwargs
        if model_load_kwargs is None:
            model_load_kwargs = {}
        model_load_kwargs.setdefault("torch_dtype", torch.float16)
        model_load_kwargs.setdefault("low_cpu_mem_usage", True)
        model_load_kwargs.setdefault("device_map", "auto")
        # tokenizer kwargs
        if tokenizer_kwargs is None:
            tokenizer_kwargs = {}
        tokenizer_kwargs.setdefault("use_fast", False)
        super().__init__(
            model_id, *args, tokenizer_kwargs=tokenizer_kwargs, model_load_kwargs=model_load_kwargs, **kwargs
        )

        # initialization for base LLaVA from https://github.com/haotian-liu/LLaVA/blob/main/llava/model/builder.py#L128
        # note: these lines (until resize_token_embeddings) are only really used in MPT, but are here for fidelity
        mm_use_im_start_end = getattr(self.model.config, "mm_use_im_start_end", False)
        mm_use_im_patch_token = getattr(self.model.config, "mm_use_im_patch_token", True)
        if mm_use_im_patch_token:
            self.tokenizer.add_tokens([DEFAULT_IMAGE_PATCH_TOKEN], special_tokens=True)
        if mm_use_im_start_end:
            self.tokenizer.add_tokens([DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN], special_tokens=True)
        self.model.resize_token_embeddings(len(self.tokenizer))

        vision_tower = self.model.get_vision_tower()
        if not vision_tower.is_loaded:
            vision_tower.load_model()
        vision_tower.to(device=self.device, dtype=torch.float16)
        self.image_processor = vision_tower.image_processor

        if hasattr(self.model.config, "max_sequence_length"):
            self.max_context_size = self.model.config.max_sequence_length
        else:
            self.max_context_size = 2048

    # much of the implementation adapted from
    # https://github.com/haotian-liu/LLaVA/blob/main/llava/serve/cli.py#L56
    # https://github.com/haotian-liu/LLaVA/blob/main/llava/serve/model_worker.py#L136

    def build_prompt(self, messages: list[ChatMessage], functions: list[AIFunction] | None = None) -> torch.Tensor:
        # first, build up the string in the format llava expects (vicuna-style)
        prompt_lines = []
        for message in messages:
            if message.role == ChatRole.USER:
                prompt_lines.append(f"USER: {message.text}")
            elif message.role == ChatRole.ASSISTANT:
                prompt_lines.append(f"ASSISTANT: {message.text}</s>")
            else:
                prompt_lines.append(f"{message.text}\n")
        prompt = "\n".join(prompt_lines)
        text = f"{prompt}\nASSISTANT:"

        # TODO: LLaMA v2
        # text = ""
        # for content, bos, eos in llama2_prompt.build_str(messages):
        #     if bos:
        #         text += "<s>"
        #     text += content
        #     if eos:
        #         text += "</s>"
        # text = text.removeprefix("<s>")

        # then pass it along, ala
        # https://github.com/haotian-liu/LLaVA/blob/main/llava/serve/cli.py#L87
        return (
            tokenizer_image_token(text, self.tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt")
            .unsqueeze(0)
            .to(self.device)
        )

    async def predict(
        self, messages: list[ChatMessage], functions: list[AIFunction] | None = None, **hyperparams
    ) -> Completion:
        # we need to extract all the ImageParts and pass them as a model kwarg
        images = []
        translated_messages = messages.copy()
        for idx, message in enumerate(translated_messages):
            # skip any simple messages
            if isinstance(message.content, str):
                continue
            # translate parts messages
            did_translate = False
            translated_parts = message.parts.copy()
            for part_idx, part in enumerate(translated_parts):
                if isinstance(part, ImagePart):
                    did_translate = True
                    translated_parts[part_idx] = DEFAULT_IMAGE_TOKEN
                    images.append(part.image)
            # update the message if we did a translation
            if did_translate:
                translated_messages[idx] = message.copy_with(parts=translated_parts)

        # turn all the image parts into a tensor
        image_tensor = process_images(images, self.image_processor, self.model.config)
        if type(image_tensor) is list:
            image_tensor = [image.to(self.device, dtype=torch.float16) for image in image_tensor]
        else:
            image_tensor = image_tensor.to(self.device, dtype=torch.float16)

        # and call the prediction logic
        return await super().predict(translated_messages, functions, images=image_tensor, **hyperparams)

    def vicuna_message_len(self, message: ChatMessage) -> int:
        # remove 1 for the <s> token at the start
        if message.role == ChatRole.USER:
            # USER: {}\n -> 5
            return self.tokenizer(message.text, return_length=True).length + 4
        elif message.role == ChatRole.ASSISTANT:
            # ASSISTANT: {}</s>\n -> 8
            return self.tokenizer(message.text, return_length=True).length + 7
        # {}\n\n -> 2
        return self.tokenizer(message.text, return_length=True).length + 1

    def message_len(self, message: ChatMessage) -> int:
        if isinstance(message.content, str):
            return self.vicuna_message_len(message)
        # count the image parts
        image_parts = 0
        translated_parts = message.parts.copy()
        for part_idx, part in enumerate(translated_parts):
            if isinstance(part, ImagePart):
                translated_parts[part_idx] = DEFAULT_IMAGE_TOKEN
                image_parts += 1
        # if we have any, tokenize the translated message with <image> tokens
        if image_parts:
            image_tokens = self.model.get_vision_tower().num_patches * image_parts
            return self.vicuna_message_len(message.copy_with(parts=translated_parts)) + image_tokens
        # otherwise return normally
        return self.vicuna_message_len(message)