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
