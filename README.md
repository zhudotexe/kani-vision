<p align="center">
  <img width="256" height="256" alt="kani" src="https://kani-vision.readthedocs.io/en/latest/_static/kani-vision-logo.png">
</p>

<p align="center">
  <a href="https://github.com/zhudotexe/kani-vision/actions/workflows/pytest.yml">
    <img alt="Test Package" src="https://github.com/zhudotexe/kani-vision/actions/workflows/pytest.yml/badge.svg">
  </a>
  <a href="https://kani-vision.readthedocs.io/en/latest/?badge=latest">
    <img alt="Documentation Status" src="https://readthedocs.org/projects/kani-vision/badge/?version=latest">
  </a>
  <a href="https://pypi.org/project/kani-vision/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/kani-vision">
  </a>
  <a href="https://colab.research.google.com/github/zhudotexe/kani-vision/blob/main/examples/colab_quickstart.ipynb">
    <img alt="Quickstart in Colab" src="https://colab.research.google.com/assets/colab-badge.svg">
  </a>
  <a href="https://discord.gg/eTepTNDxYT">
    <img alt="Discord" src="https://img.shields.io/discord/1150902904773935214?color=5865F2&label=discord&logo=discord&logoColor=white">
  </a>
</p>

# kani-vision

## Installation

To install kani-vision, you must have at least Python 3.10. kani-vision uses extras to provide support for specific
models - see below for model-specific instructions and other extras.

You can combine multiple extras into a single command, like `pip install "kani-vision[openai,ascii]"`.

### OpenAI (GPT-4V)

```shell
$ pip install "kani-vision[openai]"
```

### LLaVA v1.5

Note: to install dependencies for LLaVA, you will have to run the following two commands as the LLaVA package installs
some outdated incompatible dependencies by default:

```shell
$ pip install "kani-vision[llava]"
$ pip install --no-deps "llava @ git+https://github.com/haotian-liu/LLaVA.git@v1.1.3"
```

### Other Extras

- `pip install "kani-vision[ascii]"`: When using `chat_in_terminal_vision()`, this will display any images you provide
  to the model as ASCII art in your terminal :).

## Quickstart

```python
from kani import Kani
from kani.ext.vision import chat_in_terminal_vision
from kani.ext.vision.engines.openai import OpenAIVisionEngine

# add your OpenAI API key here
api_key = "sk-..."
engine = OpenAIVisionEngine(api_key, model="gpt-4-vision-preview", max_tokens=512)
ai = Kani(engine)

# use `!path/to/file.png` to provide an image to the engine, e.g. `Please describe this image: !kani-logo.png`
# or use a URL: `Please describe this image: !https://example.com/image.png`
chat_in_terminal_vision(ai)
```

## Usage

This section assumes that you're already familiar with the basic usage of kani. If not, go check
out [the kani docs](https://kani.readthedocs.io/en/latest/kani.html) first!

kani-vision provides two main features to extend kani with vision using
the [message parts API](https://kani.readthedocs.io/en/latest/advanced.html#message-parts).

### Engines

The first are the vision engines, which are the underlying vision-language models (VLMs). kani-vision comes with support
for two VLM engines, GPT-4V (OpenAI's hosted model) and LLaVA v1.5 (an open-source extension of Vicuna):

| Model Name | Extra            | Capabilities | Engine                                              |
|------------|------------------|--------------|-----------------------------------------------------|
| GPT-4V     | `openai`         | 🛠 📡        | `kani.ext.vision.engines.openai.OpenAIVisionEngine` |
| LLaVA v1.5 | `llava` [^llava] | 🔓 🖥 🚀     | `kani.ext.vision.engines.llava.LlavaEngine`         |

**Legend**

- 🛠: Supports function calling.
- 🔓: Open source model.
- 🖥: Runs locally on CPU.
- 🚀: Runs locally on GPU.
- 📡: Hosted API.

[^llava]: See the installation instructions. You may also need to install PyTorch manually.

To initialize an engine, you use it the same way as in normal kani! All vision engines are interchangeable with normal
kani engines.

### Message Part

The second feature you need to be familiar with is the `ImagePart`, the core way of sending messages to the engine.
To do this, when you call the kani round methods (i.e. `Kani.chat_round` or `Kani.full_round` or their str variants),
pass a *list* rather than a string:

```python
from kani import Kani
from kani.ext.vision import ImagePart
from kani.ext.vision.engines.llava import LlavaEngine

engine = LlavaEngine("liuhaotian/llava-v1.5-7b")
ai = Kani(engine)

# notice how the arg is a list of parts rather than a single str!
msg = await ai.chat_round_str([
    "Please describe this image:",
    ImagePart.from_path("path/to/image.png")
])
print(msg)
```

You can also define images from a URL, raw PNG binary or a Pillow Image, using 
`ImagePart.from_url`, `ImagePart.from_bytes`, or `ImagePart.from_image`, respectively.

See [the examples](https://github.com/zhudotexe/kani-vision/tree/main/examples/llava-local.py) for more.

### Terminal Utility

Finally, kani-vision comes with an additional utility to chat with a VLM in your terminal, `chat_in_terminal_vision`.

This utility allows you to provide images on your disk or on the internet inline by prepending it with an exclamation
point:

```pycon
>>> from kani.ext.vision import chat_in_terminal_vision
>>> chat_in_terminal_vision(ai)
USER: Please describe this image: !path/to/image.png and also this one: !https://example.com/image.png
```
